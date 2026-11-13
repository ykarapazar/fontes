"""European Union: legislation and CJEU case law from the Publications Office CELLAR.

Everything goes through two keyless CELLAR services on publications.europa.eu:
  * SPARQL (Virtuoso, CDM ontology) for search and metadata;
  * REST content negotiation: GET /resource/celex/{CELEX} with
    Accept: application/xhtml+xml and Accept-Language: eng -> 303 -> XHTML.
    `Accept: text/html` gives 404 for case law; always ask for XHTML.

Gotchas this code encodes:
  * eur-lex.europa.eu sits behind an AWS WAF JS challenge (HTTP 202, empty
    body), so it is only used for the public `url` field, never fetched.
  * There is no full-text search: Virtuoso `bif:contains` searches *titles*
    (for judgments the title also carries the subject keywords). Relevance
    comes from `OPTION (score ?sc)`.
  * Aggregates (MAX/SAMPLE + GROUP BY) next to bif:contains return wrong values
    on this endpoint, so searches select DISTINCT works in a sub-select and
    fetch titles around it; duplicates are dropped in Python.
  * CELEX suffixes: "_RES"/"_SUM" etc. are summaries, "R(01)" corrigenda; both
    are filtered out. Consolidated texts are separate works ("0" + CELEX[1:] +
    "-YYYYMMDD") linked by cdm:act_consolidated_based_on_resource_legal.
  * Treaties are sector 1: "12016M/TXT" (TEU), "12016E/TXT" (TFEU), "12016P/TXT"
    (Charter) are the 2016 consolidated texts, fetched like any other CELEX id.
  * Texts are returned in English (Accept-Language: eng); a document with no
    English version falls back to French. The `language` filter only changes
    which language's titles are searched and shown.
"""
from __future__ import annotations

import datetime
import re
from urllib.parse import quote

from lxml import html as lhtml
from markdownify import markdownify as _md

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (
    Decision,
    DecisionHit,
    LawHit,
    LawText,
    Provision,
    Results,
    Toc,
    TocEntry,
)

HOST = "publications.europa.eu"
SPARQL = f"https://{HOST}/webapi/rdf/sparql"
CELEX_URL = f"https://{HOST}/resource/celex/"
EURLEX = "https://eur-lex.europa.eu/legal-content/{lang}/TXT/?uri=CELEX:{celex}"
LANG_URI = "http://publications.europa.eu/resource/authority/language/"

# 24 official EU languages: CELLAR 3-letter code -> EUR-Lex 2-letter code.
LANGS = {"BUL": "BG", "SPA": "ES", "CES": "CS", "DAN": "DA", "DEU": "DE", "EST": "ET",
         "ELL": "EL", "ENG": "EN", "FRA": "FR", "GLE": "GA", "HRV": "HR", "ITA": "IT",
         "LAV": "LV", "LIT": "LT", "HUN": "HU", "MLT": "MT", "NLD": "NL", "POL": "PL",
         "POR": "PT", "RON": "RO", "SLK": "SK", "SLV": "SL", "FIN": "FI", "SWE": "SV"}

_LEG_ID = re.compile(r"^3\d{4}[A-Z]{1,2}\d{4}(\(\d{2}\))?$")
_CONS_ID = re.compile(r"^0\d{4}[A-Z]{1,2}\d{4}(\(\d{2}\))?-(\d{8})$")
_TREATY_ID = re.compile(r"^1\d{4}[A-Z]{1,3}(/[A-Z0-9]{3,4})?$")   # sector 1: 12016M/TXT = TEU
_CASE_ID = re.compile(r"^6(\d{4})([A-Z]{2})(\d{4})(\(\d{2}\))?$")
_ECLI = re.compile(r"^ECLI:EU:[A-Z]:\d{4}:\d+$", re.I)

_LEG_TYPES = {"regulation": "R", "directive": "L", "decision": "D", "all": "[A-Z]{1,2}",
              "treaty": ""}
_LEG_TYPE_NAMES = {"R": "Regulation", "L": "Directive", "D": "Decision"}
_COURTS = {"cj": "C", "gc": "T", "all": "[CT]"}
_CASE_TYPES = {"judgment": "J", "order": "O", "opinion": "C", "all": "[JOC]"}
_COURT_NAMES = {"C": "Court of Justice", "T": "General Court", "F": "Civil Service Tribunal"}
_DOC_NAMES = {"J": "Judgment", "O": "Order", "C": "Opinion of the Advocate General"}
_SORTS = ("relevance", "date")
_DATE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")

# XHTML classes (modern CONVEX consolidated, OJ "oj-" layout, older OJ layout).
_ART_CLASSES = {"title-article-norm", "oj-ti-art", "ti-art"}
_STITLE_CLASSES = {"stitle-article-norm", "oj-sti-art", "sti-art"}
_DIV1_CLASSES = {"title-division-1", "oj-ti-section-1", "ti-section-1"}
_DIV2_CLASSES = {"title-division-2", "oj-ti-section-2", "ti-section-2"}
_DROP_CLASSES = {"arrow", "modref"}
_ART_LABEL = re.compile(r"^Article\s+(\d+\s?[a-z]{0,2})\b", re.I)

_text_cache: dict[str, tuple[str, bytes]] = {}   # celex -> (language used, XHTML bytes)


# --------------------------------------------------------------------------- #
# Helpers (candidates for promotion to a shared module)
# --------------------------------------------------------------------------- #
def _norm_celex(s: str) -> str:
    s = (s or "").strip()
    s = re.sub(r"^celex\s*:\s*", "", s, flags=re.I)
    return s.upper().replace(" ", "")


def _eurlex(celex: str, lang: str = "ENG") -> str:
    return EURLEX.format(lang=LANGS.get(lang, "EN"), celex=celex)


def _lit(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"^^<http://www.w3.org/2001/XMLSchema#string>'


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").replace(" ", " ")).strip()


_STEMS = {"dominance": "dominan*"}
# Bare "competition" mostly hits EPSO staff-recruitment cases ("Notice of competition").
_STAFF_WORDS = {"notice", "epso", "recruitment", "civil", "staff", "open", "concours", "laureate"}


def _competition_noise(query: str) -> bool:
    words = set(re.findall(r"\w+", query.lower()))
    return "competition" in words and not words & _STAFF_WORDS


def _fts(query: str) -> str:
    """Turn a user query into a Virtuoso bif:contains expression (all terms AND-ed)."""
    phrases = [p for p in re.findall(r'"([^"]+)"', query)]
    rest = re.sub(r'"[^"]*"', " ", query)
    terms = [_clean(re.sub(r"[^\w\s/.\-]", " ", p)) for p in phrases]
    terms += [t.strip(".-/") for t in re.findall(r"[\w/.\-]+", rest)]
    terms = [t for t in terms if t and (len(t) > 1 or t.isdigit())]
    if not terms:
        raise BadRequest("query needs at least one word, e.g. 'data protection' or 'Schrems'.")
    # Titles say "dominant position"; lawyers say "dominance": match both word forms.
    terms = [_STEMS.get(t.lower(), t) for t in terms]
    return " AND ".join(f'"{t}"' for t in terms)


def _lang(filters: dict) -> str:
    lang = str(filters.get("language") or "ENG").strip().upper()
    if lang not in LANGS:
        raise BadRequest(f"language must be a 3-letter EU code, one of: {', '.join(sorted(LANGS))}.")
    return lang


def _sort(filters: dict) -> str:
    s = str(filters.get("sort") or "relevance").strip().lower()
    if s not in _SORTS:
        raise BadRequest("sort must be 'relevance' or 'date'.")
    return s


def _date_filters(filters: dict) -> str:
    out = []
    for key, op in (("date_from", ">="), ("date_to", "<=")):
        v = str(filters.get(key) or "").strip()
        if not v:
            continue
        if not _DATE.match(v):
            raise BadRequest(f"{key} must be YYYY, YYYY-MM or YYYY-MM-DD, got {v!r}.")
        if len(v) == 4:
            v = v + ("-01-01" if op == ">=" else "-12-31")
        elif len(v) == 7:
            v = v + ("-01" if op == ">=" else "-31")
        out.append(f'FILTER(STR(?date) {op} "{v}")')
    return "\n ".join(out)


async def _sparql(query: str) -> list[dict[str, str]]:
    r = await _http.get(SPARQL, params={"query": query},
                        headers={"Accept": "application/sparql-results+json"}, timeout=45.0)
    if r.status_code != 200:
        raise SourceError(f"CELLAR SPARQL error: {_clean(r.text)[:200]}", r.status_code)
    try:
        rows = r.json()["results"]["bindings"]
    except (ValueError, KeyError) as e:
        raise SourceError(f"CELLAR SPARQL returned an unexpected payload ({e})", r.status_code)
    return [{k: v.get("value", "") for k, v in row.items()} for row in rows]


async def _search(celex_regex: str, query: str, *, limit: int, page: int, filters: dict,
                  extra: str = "", exclude_staff: bool = False) -> tuple[list[dict[str, str]], int | None, str]:
    """Title search. Returns (rows with celex/date/title/..., total, language)."""
    lang = _lang(filters)
    fts = _fts(query)
    if exclude_staff and _competition_noise(query):
        fts += ' AND NOT "civil service"'
    order = "DESC(?s1) DESC(?date) ?celex" if _sort(filters) == "relevance" else "DESC(?date) ?celex"
    dates = _date_filters(filters)
    need_date = "" if not dates else "?w cdm:work_date_document ?date ."
    core = f"""
 ?w cdm:resource_legal_id_celex ?celex .
 ?e cdm:expression_belongs_to_work ?w ; cdm:expression_title ?t ;
    cdm:expression_uses_language <{LANG_URI}{lang}> .
 ?t bif:contains '{fts}' OPTION (score ?sc) .
 FILTER(REGEX(STR(?celex), "{celex_regex}"))
 {need_date}
 {extra}
 {dates}"""
    offset = (page - 1) * limit
    # One row per CELEX before LIMIT/OFFSET: a CELEX can map to several works/expressions,
    # and OFFSET counts rows, so un-grouped rows shift and repeat cases across pages.
    q = f"""PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
SELECT ?w1 ?celex ?date ?s1 ?title ?force ?ecli WHERE {{
 {{ SELECT (MIN(?w) AS ?w1) ?celex ?date (MAX(?sc) AS ?s1) WHERE {{ {core}
    OPTIONAL {{ ?w cdm:work_date_document ?date }} }}
   GROUP BY ?celex ?date
   ORDER BY {order} LIMIT {limit + 5} OFFSET {offset} }}
 OPTIONAL {{ ?e2 cdm:expression_belongs_to_work ?w1 ; cdm:expression_title ?title ;
             cdm:expression_uses_language <{LANG_URI}{lang}> }}
 OPTIONAL {{ ?w1 cdm:resource_legal_in-force ?force }}
 OPTIONAL {{ ?w1 cdm:case-law_ecli ?ecli }}
}} ORDER BY {order}"""
    rows = [{**r, "w": r.get("w1", ""), "sc": r.get("s1", "")}
            for r in await _sparql(q)]
    seen: dict[str, dict[str, str]] = {}
    for row in rows:
        c = row.get("celex", "")
        if c and c not in seen:
            seen[c] = row
    items = list(seen.values())[:limit]
    count_q = f"""PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
SELECT (COUNT(DISTINCT ?w) AS ?n) WHERE {{ {core} }}"""
    try:
        total: int | None = int((await _sparql(count_q))[0]["n"])
    except (SourceError, KeyError, IndexError, ValueError):
        total = None
    return items, total, lang


def _case_number(celex: str) -> str:
    m = _CASE_ID.match(celex)
    if not m:
        return ""
    year, kind, num, _ = m.groups()
    return f"{kind[0]}-{int(num)}/{year[2:]}"


def _split_case_title(title: str) -> tuple[str, str, str]:
    """'Judgment of the Court (...) of 6 October 2015.#A v B.#Request ...#keywords'
    -> (header, case name, rest)."""
    parts = [_clean(p) for p in (title or "").split("#") if _clean(p)]
    if not parts:
        return "", "", ""
    head = parts[0]
    name = parts[1].rstrip(".") if len(parts) > 1 else ""
    rest = " ".join(parts[2:])
    return head, name, rest


def _case_title(celex: str, raw: str) -> tuple[str, str, str]:
    head, name, rest = _split_case_title(raw)
    num = _case_number(celex)
    m = _CASE_ID.match(celex)
    court = _COURT_NAMES.get(m.group(2)[0], "") if m else ""
    if name:
        title = f"{name} ({num})" if num else name
    else:
        title = f"{court} {num}".strip() or celex
    return title, head, rest


# ------------------------------- XHTML ------------------------------------- #
def _classes(el) -> set[str]:
    return set((el.get("class") or "").split())


def _flatten_lists(root) -> None:
    """Grid/table layouts of '(a) | text' rows -> one paragraph per item."""
    for grid in list(root.iter("div")):
        if "grid-container" not in _classes(grid):
            continue
        cols = [c for c in grid if c.tag == "div"]
        if len(cols) != 2:
            continue
        label = _clean(cols[0].text_content())
        body = cols[1]
        first = next((c for c in body.iter("p", "div") if c is not body), None)
        target = first if first is not None else body
        target.text = f"{label} " + (target.text or "")
        body.tag = "div"
        grid.getparent().replace(grid, body)
    for table in list(root.iter("table")):
        rows = [tr for tr in table.iter("tr")]
        if not rows:
            continue
        cells = [[td for td in tr if td.tag in ("td", "th")] for tr in rows]
        if not all(len(c) == 2 and len(_clean(c[0].text_content())) <= 8 for c in cells):
            continue
        box = lhtml.Element("div")
        for label_td, body_td in cells:
            label = _clean(label_td.text_content())
            ps = [c for c in body_td if c.tag in ("p", "div")]
            if ps:
                ps[0].text = f"{label} " + (ps[0].text or "")
                box.extend(list(body_td))
            else:
                p = lhtml.Element("p")
                p.text = f"{label} {_clean(body_td.text_content())}"
                box.append(p)
        table.getparent().replace(table, box)


def _prepare(root) -> None:
    for el in list(root.iter()):
        if not isinstance(el.tag, str):
            continue
        cls = _classes(el)
        if el.tag in ("script", "style", "col", "colgroup", "head") or cls & _DROP_CLASSES:
            el.drop_tree()
        elif el.tag == "p" and cls & _ART_CLASSES:
            el.tag = "h3"
        elif el.tag == "p" and cls & (_DIV1_CLASSES | _DIV2_CLASSES):
            el.tag = "h2"
        elif el.tag == "p" and cls & _STITLE_CLASSES:
            el.tag = "h4"
    _flatten_lists(root)
    # Consolidated layout: <span class="no-parag">1. </span><div>text</div> -> "1. text"
    for span in list(root.iter("span")):
        nxt = span.getnext()
        if "no-parag" not in _classes(span) or nxt is None:
            continue
        target = next((c for c in nxt.iter("p") if c is not nxt), nxt)
        target.text = f"{_clean(span.text_content())} " + (target.text or "")
        span.drop_tree()


def _to_md(el) -> str:
    s = lhtml.tostring(el, encoding="unicode", method="html")
    md = _md(s, heading_style="ATX", strip=["a", "img"], bullets="-")
    md = md.replace(" ", " ")
    md = re.sub(r"[ \t]+", " ", md)
    md = re.sub(r" *\n *", "\n", md)
    md = re.sub(r"\(\s*\\?\*\s*\)", "(*)", md)          # footnote star split over lines
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip()


def _parse(raw: bytes):
    try:
        root = lhtml.fromstring(raw)
    except Exception as e:  # lxml raises several types on odd markup
        raise SourceError(f"CELLAR returned unparseable XHTML ({e})")
    body = root.find(".//body")
    root = body if body is not None else root
    _prepare(root)
    return root


def _articles(root) -> list[tuple[str, str, object]]:
    """[(label 'Article 6', heading 'Article 6 — Lawfulness of processing', h3 element)]."""
    out = []
    for h in root.iter("h3"):
        txt = _clean(h.text_content())
        m = _ART_LABEL.match(txt)
        if not m:
            continue
        label = "Article " + m.group(1).replace(" ", "")
        sub = h.getnext()
        stitle = ""
        if sub is not None:
            h4 = sub if sub.tag == "h4" else sub.find(".//h4")
            if h4 is not None:
                stitle = _clean(h4.text_content())
        out.append((label, f"{label} — {stitle}" if stitle else label, h))
    return out


def _provision_label(p: str) -> str:
    s = _clean(p)
    s = re.sub(r"^(article|art\.?|artikel)\s*", "", s, flags=re.I)
    m = re.match(r"^(\d+)\s*([a-z]{0,2})\b", s, flags=re.I)
    if not m:
        raise BadRequest(f"provision must look like 'Article 6', '6' or 'art. 6a'; got {p!r}.")
    return f"Article {m.group(1)}{m.group(2).lower()}"


def _article_md(h) -> str:
    parent = h.getparent()
    if parent is not None and (parent.get("id") or "").startswith("art_"):
        return _to_md(parent)
    box = lhtml.Element("div")
    box.append(lhtml.fromstring(lhtml.tostring(h)))
    sib = h.getnext()
    while sib is not None:
        if sib.tag in ("h3", "h2") or sib.find(".//h3") is not None or sib.find(".//h2") is not None:
            break
        box.append(lhtml.fromstring(lhtml.tostring(sib)))
        sib = sib.getnext()
    return _to_md(box)


async def _content(celex: str) -> tuple[str, bytes]:
    """(X)HTML for a CELEX number: English, else French. Cached per process.

    Older documents only have an XHTML manifestation, recent CJEU ones only "html",
    and CELLAR answers 404 for a type it does not hold, so both are tried."""
    if celex in _text_cache:
        return _text_cache[celex]
    last = 0
    for lang in ("eng", "fra"):
        for accept in ("application/xhtml+xml", "text/html"):
            r = await _http.get(CELEX_URL + quote(celex, safe="-"),  # '(' must be %28
                                headers={"Accept": accept, "Accept-Language": lang})
            if r.status_code == 200 and r.content.strip():
                ctype = r.headers.get("content-type", "")
                if "html" not in ctype:
                    raise SourceError(f"CELLAR returned {ctype or 'no content type'} for {celex}")
                _text_cache[celex] = (lang.upper(), r.content)
                return _text_cache[celex]
            last = r.status_code
            if r.status_code not in (404, 406):
                raise SourceError(f"CELLAR content fetch failed for {celex}", r.status_code)
    raise NotFound(f"no English or French text in CELLAR for CELEX {celex} (HTTP {last}). "
                   f"Check {_eurlex(celex)}")


# --------------------------------------------------------------------------- #
# The adapter
# --------------------------------------------------------------------------- #
class EuropeanUnion(Jurisdiction):
    code = "eu"
    name = "European Union"
    languages = tuple(c.lower() for c in LANGS)
    aliases = ("european union", "eur-lex", "cjeu", "curia")
    sources = (
        Source(
            "Publications Office CELLAR (EUR-Lex data): SPARQL + REST",
            "https://publications.europa.eu/webapi/rdf/sparql",
            covers=("caselaw", "legislation"),
            licence=("EU legal documents reusable under Commission Decision 2011/833/EU "
                     "(commercial or non-commercial reuse, acknowledge source, do not distort); "
                     "EUR-Lex metadata CC0"),
            commercial_use=True,
            ai_use=None,
            auth="none",
            rate_limit=("none published (checked 2026-11); 1 s spacing, no 429 seen in "
                        "~40 requests (2026-11)"),
            terms_url="https://op.europa.eu/en/web/about-us/legal-notices/publications-office-of-the-european-union-copyright",
        ),
    )
    caselaw_filters = {
        "court": "cj (Court of Justice) | gc (General Court) | all (default)",
        "doc_type": "judgment (default) | order | opinion (Advocate General) | all",
        "date_from": "YYYY, YYYY-MM or YYYY-MM-DD (decision date)",
        "date_to": "YYYY, YYYY-MM or YYYY-MM-DD",
        "language": "3-letter EU code of the titles searched (ENG default, DEU, FRA, ...); texts are returned in English",
        "sort": "relevance (default) | date (newest first)",
    }
    legislation_filters = {
        "doc_type": "regulation | directive | decision | all (default: the three main types) | treaty (primary law, CELEX sector 1: consolidated Treaties, Charter, older versions)",
        "in_force": "yes | no",
        "date_from": "YYYY, YYYY-MM or YYYY-MM-DD (document date)",
        "date_to": "YYYY, YYYY-MM or YYYY-MM-DD",
        "language": "3-letter EU code of the titles searched (ENG default, DEU, FRA, ...); texts are returned in English",
        "sort": "relevance (default) | date (newest first)",
    }
    min_interval = {HOST: 1.0}
    notes = ("EUR-Lex data via CELLAR. Ids are CELEX numbers (32016R0679 = GDPR, "
             "62014CJ0362 = Schrems); ECLI accepted for decisions. Search covers titles only.")
    gaps = (
        "Full-text search of documents: EUR-Lex SOAP webservice needs a free account we have not signed up for (titles only)",
        "Texts in languages other than English (French fallback): CELLAR serves them; not built",
        "InfoCuria case files and pending cases: Angular SPA with no public API found",
        "EUR-Lex website itself: behind an AWS WAF JS challenge (bot check)",
        "Civil Service Tribunal decisions (2005-2016): search covers cj/gc only; get_decision by CELEX (6…FJ…) untested",
        ("Treaties and Charter (sector 1): served by CELEX id (current: 12016M/TXT = TEU, 12016E/TXT = TFEU, "
         "12016P/TXT = Charter; doc_type=treaty lists all consolidated versions). No in-force flag for "
         "old versions (CELLAR marks them all in force); protocols and declarations are inside the TEU/TFEU "
         "text, article labels repeat there (a label resolves to the main treaty first); accession treaties "
         "and amending treaties (sector 1 works without /TXT) not searched"),
        "International agreements (sector 2): not built",
    )
    samples = {
        "caselaw_query": "data protection",
        "decision_id": "62014CJ0362",
        "legislation_query": "general data protection regulation",
        "law_id": "32016R0679",
        "provision": "Article 6",
    }

    # ------------------------------ case law ------------------------------ #
    async def search_caselaw(self, query, *, limit, page, filters):
        court = str(filters.get("court") or "all").strip().lower()
        kind = str(filters.get("doc_type") or "judgment").strip().lower()
        if court not in _COURTS:
            raise BadRequest("court must be cj, gc or all.")
        if kind not in _CASE_TYPES:
            raise BadRequest("doc_type must be judgment, order, opinion or all.")
        if kind == "opinion" and court == "gc":
            raise BadRequest("Advocate General opinions exist only at the Court of Justice (court=cj).")
        regex = f"^6[0-9]{{4}}{_COURTS[court]}{_CASE_TYPES[kind]}[0-9]{{4}}(\\\\([0-9]{{2}}\\\\))?$"
        rows, total, lang = await _search(regex, query, limit=limit, page=page, filters=filters,
                                          exclude_staff=True)
        hits = []
        for r in rows:
            celex = r["celex"]
            title, head, rest = _case_title(celex, r.get("title", ""))
            m = _CASE_ID.match(celex)
            hits.append(DecisionHit(
                id=celex, title=title,
                court=_COURT_NAMES.get(m.group(2)[0], "") if m else "",
                date=r.get("date", "")[:10], case_number=_case_number(celex),
                snippet=_clean(f"{head} {rest}")[:300], url=_eurlex(celex, lang)))
        return Results(hits, total=total, note=(
            "Searches titles and subject keywords only (CELLAR has no body full-text search); "
            "ids are CELEX numbers."))

    async def _resolve_case(self, id: str) -> str:
        s = _clean(id)
        if _ECLI.match(s):
            rows = await _sparql(
                "PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>\n"
                f"SELECT DISTINCT ?celex WHERE {{ ?w cdm:case-law_ecli {_lit(s.upper())} ; "
                "cdm:resource_legal_id_celex ?celex }")
            celexes = sorted(r["celex"] for r in rows if _CASE_ID.match(r["celex"]))
            if not celexes:
                raise NotFound(f"no CJEU document with {s.upper()} in CELLAR")
            return celexes[0]
        celex = _norm_celex(s)
        if not _CASE_ID.match(celex):
            raise BadRequest("decision id must be a CELEX number like 62014CJ0362 "
                             "(6 + year + CJ/TJ/CO/TO/CC + 4-digit case number) or an ECLI like "
                             "ECLI:EU:C:2015:650.")
        return celex

    async def get_decision(self, id):
        celex = await self._resolve_case(id)
        rows = await _sparql(
            "PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>\n"
            "SELECT ?title ?date ?ecli ?plang WHERE {"
            f" ?w cdm:resource_legal_id_celex {_lit(celex)} ."
            " OPTIONAL { ?e cdm:expression_belongs_to_work ?w ; cdm:expression_title ?title ;"
            f"   cdm:expression_uses_language <{LANG_URI}ENG> }}"
            " OPTIONAL { ?w cdm:work_date_document ?date }"
            " OPTIONAL { ?w cdm:case-law_ecli ?ecli }"
            " OPTIONAL { ?w cdm:case-law_uses_procedure_language ?plang } } LIMIT 20")
        if not rows:
            raise NotFound(f"no CJEU document with CELEX {celex} in CELLAR")
        row = max(rows, key=lambda r: len(r.get("title", "")))
        title, head, rest = _case_title(celex, row.get("title", ""))
        used, raw = await _content(celex)
        text = _to_md(_parse(raw))
        m = _CASE_ID.match(celex)
        meta = {"Document": _DOC_NAMES.get(m.group(2)[1], "") if m else "",
                "ECLI": row.get("ecli", ""),
                "Formation": head,
                "Language of the case": row.get("plang", "").rsplit("/", 1)[-1],
                "Text language": "" if used == "ENG" else f"{used} (no English text in CELLAR)"}
        return Decision(
            id=celex, title=title, text=text, url=_eurlex(celex),
            court=_COURT_NAMES.get(m.group(2)[0], "") if m else "",
            date=row.get("date", "")[:10], case_number=_case_number(celex),
            summary=rest, metadata={k: v for k, v in meta.items() if v})

    # ---------------------------- legislation ----------------------------- #
    async def search_legislation(self, query, *, limit, page, filters):
        kind = str(filters.get("doc_type") or "").strip().lower()
        if kind and kind not in _LEG_TYPES:
            raise BadRequest("doc_type must be regulation, directive, decision or all.")
        letters = _LEG_TYPES[kind] if kind else "[RLD]"
        treaty = kind == "treaty"
        extra = ""
        force = str(filters.get("in_force") or "").strip().lower()
        if force:
            if force not in ("yes", "no", "true", "false"):
                raise BadRequest("in_force must be yes or no.")
            val = "true" if force in ("yes", "true") else "false"
            extra = f"?w cdm:resource_legal_in-force \"{val}\"^^<http://www.w3.org/2001/XMLSchema#boolean> ."
        regex = (r"^1[0-9]{4}[A-Z]+/TXT$" if treaty
                 else f"^3[0-9]{{4}}{letters}[0-9]{{4}}(\\\\([0-9]{{2}}\\\\))?$")
        rows, total, lang = await _search(regex, query, limit=limit, page=page, filters=filters,
                                          extra=extra)
        hits = []
        for r in rows:
            celex = r["celex"]
            letter = re.match(r"^[13]\d{4}([A-Z]{1,2})", celex).group(1)
            num = re.search(r"\b(\d{2,4}/\d+(/[A-Z]+)?)\b", r.get("title", ""))
            f = r.get("force", "")
            hits.append(LawHit(
                id=celex, title=_clean(r.get("title", "")) or celex,
                type="Treaty" if treaty else _LEG_TYPE_NAMES.get(letter, letter), number=num.group(1) if num else "",
                date=r.get("date", "")[:10],
                status="" if treaty else {"1": "in force", "true": "in force", "0": "not in force",
                                          "false": "not in force"}.get(f, ""),
                url=_eurlex(celex, lang)))
        return Results(hits, total=total, note=(
            "Searches titles only (CELLAR has no body full-text search); ids are CELEX numbers. "
            "Texts open as the latest consolidated version when one exists."))

    async def _law(self, id: str) -> dict[str, str]:
        """Resolve a CELEX id -> {base, text_celex, title, as_of, date, force}."""
        celex = _norm_celex(id)
        cons = _CONS_ID.match(celex)
        if cons:
            base = "3" + celex[1:].split("-")[0]
        elif _LEG_ID.match(celex) or _TREATY_ID.match(celex):
            base = celex
        else:
            raise BadRequest("law id must be a CELEX number like 32016R0679 (GDPR), a "
                             "consolidated one like 02016R0679-20160504, or a treaty one "
                             "like 12016M/TXT (TEU).")
        rows = await _sparql(
            "PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>\n"
            "SELECT ?title ?date ?force ?cons WHERE {"
            f" ?w cdm:resource_legal_id_celex {_lit(base)} ."
            " OPTIONAL { ?e cdm:expression_belongs_to_work ?w ; cdm:expression_title ?title ;"
            f"   cdm:expression_uses_language <{LANG_URI}ENG> }}"
            " OPTIONAL { ?w cdm:work_date_document ?date }"
            " OPTIONAL { ?w cdm:resource_legal_in-force ?force }"
            " OPTIONAL { ?c cdm:act_consolidated_based_on_resource_legal ?w ;"
            "   cdm:resource_legal_id_celex ?cons } } LIMIT 500")
        if not rows:
            raise NotFound(f"no EU act with CELEX {base} in CELLAR")
        title = max((_clean(r.get("title", "")) for r in rows), key=len) or base
        info = {"base": base, "title": title, "date": rows[0].get("date", "")[:10],
                "force": rows[0].get("force", ""), "text_celex": base, "as_of": ""}
        if _TREATY_ID.match(base):
            return info
        if cons:
            d = cons.group(2)
            info.update(text_celex=celex, as_of=f"{d[:4]}-{d[4:6]}-{d[6:]}")
            return info
        today = datetime.date.today().strftime("%Y%m%d")
        versions = sorted({r["cons"] for r in rows if _CONS_ID.match(r.get("cons", ""))},
                          key=lambda c: c[-8:])
        current = [c for c in versions if c[-8:] <= today] or versions
        if current:
            d = current[-1][-8:]
            info.update(text_celex=current[-1], as_of=f"{d[:4]}-{d[4:6]}-{d[6:]}")
        return info

    async def _law_doc(self, id: str):
        info = await self._law(id)
        try:
            _, raw = await _content(info["text_celex"])
        except NotFound:
            if info["text_celex"] == info["base"]:
                raise
            info.update(text_celex=info["base"], as_of="")   # consolidated text missing
            _, raw = await _content(info["base"])
        return info, _parse(raw)

    async def get_legislation_toc(self, id):
        info, root = await self._law_doc(id)
        has_divs = any(True for _ in root.iter("h2"))
        arts = {h: (label, heading) for label, heading, h in _articles(root)}
        entries: list[TocEntry] = []
        pending_div = ""
        for el in root.iter("h2", "h3"):
            if el.tag == "h2":
                txt = _clean(el.text_content())
                if _classes(el) & _DIV1_CLASSES:
                    if pending_div:
                        entries.append(TocEntry(pending_div, level=0))
                    pending_div = txt
                else:
                    entries.append(TocEntry(f"{pending_div} — {txt}" if pending_div else txt, 0))
                    pending_div = ""
            elif el in arts:
                if pending_div:
                    entries.append(TocEntry(pending_div, level=0))
                    pending_div = ""
                label, heading = arts[el]
                entries.append(TocEntry(heading, level=1 if has_divs else 0, provision=label))
        if not any(e.provision for e in entries):
            raise NotFound(f"no articles found in the text of {info['text_celex']}; "
                           "use get_legislation_text instead.")
        return Toc(id=info["base"], title=info["title"], url=_eurlex(info["text_celex"]),
                   entries=entries)

    async def get_legislation_provision(self, id, provision):
        label = _provision_label(provision)
        info, root = await self._law_doc(id)
        for lab, _heading, h in _articles(root):
            if lab.lower() == label.lower():
                return Provision(law_id=info["base"], law_title=info["title"], provision=lab,
                                 text=_article_md(h), url=_eurlex(info["text_celex"]),
                                 as_of=info["as_of"])
        raise NotFound(f"{label} not found in {info['text_celex']} "
                       "(see get_legislation_toc for the article list).")

    async def get_legislation_text(self, id):
        info, root = await self._law_doc(id)
        meta = {"Original act": info["base"] if info["text_celex"] != info["base"] else "",
                "Consolidated version": info["text_celex"] if info["as_of"] else "",
                "Document date": info["date"],
                "In force": {"1": "yes", "true": "yes", "0": "no", "false": "no"}.get(info["force"], "")}
        return LawText(id=info["base"], title=info["title"], text=_to_md(root),
                       url=_eurlex(info["text_celex"]), as_of=info["as_of"],
                       metadata={k: v for k, v in meta.items() if v})
