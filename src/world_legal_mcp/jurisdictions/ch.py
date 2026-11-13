"""Switzerland: federal case law from the Federal Supreme Court (bger.ch) and federal
consolidated law (Systematische Rechtssammlung, SR) from Fedlex.

Gotchas this code encodes:
  * Fedlex metadata comes from the SPARQL endpoint (fedlex.data.admin.ch/sparqlendpoint,
    JOLux ontology). The SR number is the skos:notation of the ConsolidationAbstract's
    taxonomy entry; the latest consolidation is the member with the highest
    jolux:dateApplicability not after today. The endpoint returns many duplicate rows,
    so every query is DISTINCT, and an error inside FILTER(a || b) is not treated the
    usual way, so optional values are COALESCEd first.
  * fedlex.data.admin.ch/robots.txt disallows /filestore/* (checked 2026-11-05). The
    same files are served by the public website at www.fedlex.admin.ch/filestore/...
    (what the Fedlex viewer itself loads; www robots.txt allows /), so texts come from
    there, one file per user request, never from the data host.
  * www.fedlex.admin.ch pages are an Angular SPA: no server-side text. Human links use
    the ELI page https://www.fedlex.admin.ch/eli/cc/.../de (+ #art_N anchors).
  * Fedlex HTML: sections carry role="heading" + aria-level; articles are <article
    id="art_N">; the final title (e.g. ZGB Schlusstitel) sits in #dispositions with
    ids "disp_u1/art_1", so its article numbers repeat and get a prefix label.
    Article marginal notes in older codes (ZGB, OR) are section headings, not h6 text.
  * Reuse terms (Art. 49 PublV, SR 170.512.1): content unchanged and every text must
    carry the notice "Dies ist keine amtliche Veröffentlichung ..." (_NOTICE).
  * BGer: the eurospider search under /ext/eurospider is allowed by robots.txt with
    Crawl-delay: 2. Two collections: "aza" (all decisions since 2000, id
    aza://DD-MM-YYYY-4A_640-2011) and "clir"/BGE (leading cases since 1954, cited as
    "BGE 150 III 71"). Pages are ISO-8859-1 HTML, 10 hits per page. www.bger.ch serves
    an incomplete TLS chain (httpx/certifi fails), so we use search.bger.ch (Imperva
    front, valid chain, same robots.txt), which the bger.ch home page itself links to.
"""
from __future__ import annotations

import datetime
import re
from urllib.parse import parse_qs, urlsplit

import lxml.html

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

SPARQL = "https://fedlex.data.admin.ch/sparqlendpoint"
FEDLEX = "https://www.fedlex.admin.ch"
BGER = "https://search.bger.ch/ext/eurospider/live/de/php"
DEU = "<http://publications.europa.eu/resource/authority/language/DEU>"
IN_FORCE = "<https://fedlex.data.admin.ch/vocabulary/enforcement-status/0>"
_PREFIX = ("PREFIX jolux: <http://data.legilux.public.lu/resource/ontology/jolux#>\n"
           "PREFIX skos: <http://www.w3.org/2004/02/skos/core#>\n")
_NOTICE = ("*Dies ist keine amtliche Veröffentlichung. Massgebend ist allein die "
           "Veröffentlichung durch die Bundeskanzlei.*")

_SR_RE = re.compile(r"^(?:SR\s*)?(0\.)?\d{1,3}(?:\.\d+)*$", re.I)
_ELI_RE = re.compile(r"(?:^|/)(eli/cc/[\w/]+?)(?:/(?:de|fr|it|rm|en))?/?$")
_AZA_RE = re.compile(r"^(?:aza://)?(\d{2})-(\d{2})-(\d{4})-(\w+?)-(\d{4})$", re.I)
_AZA_ISO_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-(\w+?)-(\d{4})$")
_CASE_RE = re.compile(r"^(\d{1,2}[A-Z]{1,2})[_ .](\d+)/(\d{4})$", re.I)
_BGE_RE = re.compile(r"^(?:BGE|ATF|DTF|atf://)?[\s-]*(\d{1,3})[\s-]+([IV]{1,3}|Ia|Ib)[\s-]+(\d+)"
                     r"(?::\w+)?$", re.I)
_SUFFIX = r"(?:bis|ter|quater|quinquies|sexies|septies|octies|novies|decies)?"
_ART_RE = re.compile(rf"^((?:Art\.?|Artikel)\s*\d+[a-z]*{_SUFFIX}"
                     rf"(?:\s*(?:–|-|und|bis)\s*\d+[a-z]*{_SUFFIX})?)(?:\s+(.*))?$")
_MONTHS = {m: i + 1 for i, names in enumerate((
    "januar janvier gennaio", "februar février fevrier febbraio", "märz mars marzo",
    "april avril aprile", "mai mai maggio", "juni juin giugno", "juli juillet luglio",
    "august août aout agosto", "september septembre settembre", "oktober octobre ottobre",
    "november novembre novembre", "dezember décembre decembre dicembre"))
    for m in names.split()}

_law_cache: dict[str, dict] = {}


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _lit(s: str) -> str:
    """A SPARQL string literal."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


async def _sparql(query: str) -> list[dict]:
    r = await _http.get(SPARQL, params={"query": _PREFIX + query},
                        headers={"Accept": "application/sparql-results+json"})
    if r.status_code != 200:
        raise SourceError(f"Fedlex SPARQL returned HTTP {r.status_code}", r.status_code)
    try:
        rows = r.json()["results"]["bindings"]
    except (ValueError, KeyError, TypeError):
        raise SourceError("Fedlex SPARQL returned an unexpected payload", r.status_code)
    return [{k: v["value"] for k, v in row.items()} for row in rows]


def _text_date(s: str) -> str:
    """'vom 19. Dezember 2011' / 'du 3 mars 2020' / 'del 1° aprile 2020' -> ISO."""
    m = re.search(r"(\d{1,2})\.?°?\s+([A-Za-zÄäÉéÛû]+)\s+(\d{4})", s or "")
    if not m or m.group(2).lower() not in _MONTHS:
        return ""
    return f"{m.group(3)}-{_MONTHS[m.group(2).lower()]:02d}-{int(m.group(1)):02d}"


def _norm_label(s: str) -> str:
    s = (s or "").replace("\xa0", " ").lower()
    s = re.sub(r"\b(art(icle|icolo|ikel)?)\.?\s*", "", s)
    s = re.sub(r"(?<=\d)\s+(?=\d)", ".", s)  # '9 1' is not Art. 91
    return re.sub(r"\s+", "", s).rstrip(".")


# --------------------------------------------------------------------------- #
# Fedlex (legislation)
# --------------------------------------------------------------------------- #
def _eli_url(cc: str) -> str:
    return cc.replace("https://fedlex.data.admin.ch", FEDLEX) + "/de"


async def _resolve(law_id: str) -> dict:
    """SR number / ELI -> {sr, cc, title, abbr, status, date, file} of the latest German HTML."""
    raw = (law_id or "").strip()
    sr = eli = ""
    if _SR_RE.match(raw):
        sr = re.sub(r"^SR\s*", "", raw, flags=re.I)
    elif _ELI_RE.search(raw):
        eli = "https://fedlex.data.admin.ch/" + _ELI_RE.search(raw).group(1)
    else:
        raise BadRequest(f"law id {law_id!r} is not an SR number (e.g. 210 for the ZGB, 220 "
                         "for the OR, 0.101 for the ECHR) or a Fedlex ELI (eli/cc/24/233_245_233).")
    key = sr or eli
    if key in _law_cache:
        return _law_cache[key]
    match = f"FILTER(STR(?sr) = {_lit(sr)})" if sr else f"FILTER(?cc = <{eli}>)"
    rows = await _sparql(f"""
SELECT DISTINCT ?cc ?sr ?title ?abbr ?status ?date ?file WHERE {{
 ?cc a jolux:ConsolidationAbstract ; jolux:classifiedByTaxonomyEntry/skos:notation ?sr .
 {match}
 ?cc jolux:isRealizedBy ?e . ?e jolux:language {DEU} ; jolux:title ?title .
 OPTIONAL {{ ?e jolux:titleShort ?abbr }}
 OPTIONAL {{ ?cc jolux:inForceStatus ?st . ?st skos:prefLabel ?status FILTER(LANG(?status) = "de") }}
 ?cons jolux:isMemberOf ?cc ; jolux:dateApplicability ?date .
 FILTER(?date <= "{_http.today()}"^^<http://www.w3.org/2001/XMLSchema#date>)
 ?cons jolux:isRealizedBy ?ce . ?ce jolux:language {DEU} ; jolux:isEmbodiedBy ?m .
 ?m jolux:userFormat <https://fedlex.data.admin.ch/vocabulary/user-format/html> ;
    jolux:isExemplifiedBy ?file .
}} ORDER BY DESC(COALESCE(?st = {IN_FORCE}, false)) DESC(?date) DESC(?file) LIMIT 1""")
    if not rows:
        raise NotFound(f"no consolidated German HTML text on Fedlex for {law_id!r}. Check the "
                       "SR number with search_legislation.")
    row = rows[0]
    return _http.lru_put(_law_cache, key, {
        "sr": row["sr"], "cc": row["cc"], "title": _http.clean(row["title"]),
        "abbr": _http.clean(row.get("abbr")), "status": row.get("status", ""),
        "date": row["date"][:10], "file": row["file"], "parsed": None}, 8)


def _prep(root) -> None:
    """Fedlex HTML in place: headings by aria-level, footnotes as [^n], no icons."""
    for el in root.xpath('//span[contains(@class,"display-icon") or contains(@class,"external-link-icon")]'):
        el.drop_tree()
    for a in root.xpath('//sup/a[starts-with(@href,"#fn-")]'):    # footnote reference
        sup = a.getparent()
        sup.tag, sup.text = "span", f"[^{_http.clean(a.text_content())}]"
        a.drop_tree()
    for p in root.xpath('//div[contains(@class,"footnotes")]/p'):  # footnote body
        n = p.xpath('./sup[1]/a[starts-with(@href,"#fnbck-")]')
        num = _http.clean(n[0].text_content()) if n else ""
        for sup in p.xpath("./sup"):
            if not _http.clean(sup.text_content()) or sup.xpath('./a[starts-with(@href,"#fnbck-")]'):
                sup.drop_tree()
        if num:
            p.text = f"[^{num}]: " + (p.text or "").lstrip()
    for tag in ("i", "b"):              # <i>a</i><i>:</i> would become "*a**:*"
        for el in reversed(root.xpath(f"//{tag}")):
            nxt = el.getnext()
            if nxt is not None and nxt.tag == tag and not (el.tail or "").strip():
                el.text = (el.text or "") + (el.tail or "") + (nxt.text or "")
                el.extend(list(nxt))
                el.tail = nxt.tail
                nxt.getparent().remove(nxt)

    def inner(el) -> str:
        return (el.text or "") + "".join(lxml.html.tostring(c, encoding="unicode") for c in el)

    for dl in reversed(root.xpath("//dl")):  # "a. text" lists (dt/dd pairs), innermost first
        for dt in dl.xpath("./dt"):
            dd = dt.getnext()
            body = inner(dd) if dd is not None and dd.tag == "dd" else ""
            item = lxml.html.fragment_fromstring(f"<p>{inner(dt).strip()} {body}</p>",
                                                 create_parent="div")
            if body:
                dd.drop_tree()
            dt.addprevious(item)
            dt.drop_tree()
        dl.tag = "div"
    for h in root.xpath('//*[@role="heading"]'):
        if h.tag != "h6":
            h.tag = f"h{min(5, max(1, int(h.get('aria-level') or 1)))}"


def _html_md(el) -> str:
    return _http.html_to_md(lxml.html.tostring(el, encoding="unicode"))


def _parse_law(html: str) -> dict:
    """-> {"toc": [TocEntry], "arts": {norm label: (label, anchor, md)}, "text": md}."""
    root = lxml.html.fromstring(html)
    content = root.get_element_by_id("lawcontent", None)
    if content is None:
        raise SourceError("Fedlex HTML has no #lawcontent")
    _prep(content)
    toc, arts, seen = [], {}, set()
    disp_names: dict[str, str] = {}
    for sec in content.xpath('.//div[@id="dispositions"]/section'):
        h = sec.find("h1")
        name = _http.clean(re.sub(r"\[\^\d+\]", "", h.text_content() if h is not None else ""))
        disp_names[sec.get("id")] = name.split(":")[0].strip()[:60] or sec.get("id")
    for el in content.xpath('.//section | .//article'):
        if el.tag == "section":
            h = next((c for c in el if isinstance(c.tag, str) and re.fullmatch(r"h[1-5]", c.tag)), None)
            if h is not None:
                level = int(h.tag[1]) - 1
                toc.append(TocEntry(title=_http.clean(re.sub(r"\[\^[^\]]+\]", "", h.text_content())),
                                    level=level))
            continue
        h6 = el.find("h6")
        if h6 is None:
            continue
        anchor = el.get("id", "")
        link = h6.find(f'a[@href="#{anchor}"]')
        label = _http.clean((link if link is not None else h6).text_content())
        label = re.sub(r"\s*\[\^[^\]]+\]", "", label)
        lm = _ART_RE.match(label)
        if lm:
            label = _http.clean(lm.group(1))
        heading_text = h6.text_content()
        rest = _http.clean(re.sub(r"\[\^[^\]]+\]", "", heading_text))[len(label):].strip()
        if anchor.startswith("disp_"):
            label = f"{disp_names.get(anchor.split('/')[0], anchor.split('/')[0])} {label}"
        if _norm_label(label) in seen:
            label = f"{label} ({anchor})"
        seen.add(_norm_label(label))
        depth = len(el.xpath("ancestor::section"))
        toc.append(TocEntry(title=_http.clean(f"{label} {rest}"), level=depth, provision=label))
        heading = ""
        if not rest:   # marginal note = nearest section heading (ZGB, OR)
            sec = el.xpath("ancestor::section[1]")
            hs = sec[0].xpath("./h1|./h2|./h3|./h4|./h5") if sec else []
            heading = _http.clean(re.sub(r"\[\^[^\]]+\]", "", hs[0].text_content())) if hs else ""
        h6.clear()
        h6.tag, h6.text = "h2", _http.clean(heading_text)
        body = _html_md(el)
        if heading:
            body = re.sub(r"^(## [^\n]*)", lambda m: f"{m.group(1)}\n\n*{heading}*", body, count=1)
        arts[_norm_label(label)] = (label, anchor, body)
        arts.setdefault(_norm_label(anchor), arts[_norm_label(label)])
    return {"toc": toc, "arts": arts, "text": _html_md(content)}


async def _law(law_id: str) -> tuple[dict, dict]:
    info = await _resolve(law_id)
    if info["parsed"] is None:
        url = info["file"].replace("https://fedlex.data.admin.ch/filestore/", f"{FEDLEX}/filestore/")
        r = await _http.get(url)
        if r.status_code != 200 or b"lawcontent" not in r.content:
            raise SourceError(f"Fedlex text fetch failed for SR {info['sr']}", r.status_code)
        info["parsed"] = _parse_law(r.content.decode("utf-8", "replace"))
    return info, info["parsed"]


def _law_title(info: dict) -> str:
    t = info["title"]
    return f"{t} ({info['abbr']})" if info["abbr"] and info["abbr"] not in t else t


# --------------------------------------------------------------------------- #
# BGer (case law)
# --------------------------------------------------------------------------- #
def _doc_url(docid: str) -> str:
    coll = "clir" if docid.startswith("atf://") else "aza"
    return f"{BGER}/{coll}/http/index.php?lang=de&type=show_document&highlight_docid={docid}"


def _bge_id(vol: str, part: str, page: str) -> str:
    part = part.upper().replace("IA", "Ia").replace("IB", "Ib")
    return f"BGE {int(vol)} {part} {int(page)}"


async def _bger_html(url: str, params: dict | None = None):
    r = await _http.get(url, params=params)
    if r.status_code != 200:
        raise SourceError(f"bger.ch returned HTTP {r.status_code}", r.status_code)
    if "_Incapsula_Resource" in r.text:  # bot-check page, not results; we don't solve it
        raise SourceError("bger.ch answered with a bot check instead of results. Search it in a "
                          "browser: https://search.bger.ch/", 503)
    return lxml.html.fromstring(r.text)


def _total(root) -> int:
    head = root.xpath('//div[@id="ranklist_exact"]//div[contains(@class,"ranklist_header")]')
    m = re.search(r"([\d'’]+)\s+exakte", head[0].text_content()) if head else None
    return int(re.sub(r"\D", "", m.group(1))) if m else 0


def _div(li, cls: str) -> str:
    d = li.xpath(f'.//div[contains(concat(" ", @class, " "), " {cls} ")]')
    return _http.clean(d[0].text_content()) if d else ""


def _aza_hits(root) -> list[DecisionHit]:
    hits = []
    for li in root.xpath('//div[@id="ranklist_exact"]//ol/li'):
        a = li.xpath('.//span[@class="rank_title"]/a')
        if not a:
            continue
        q = parse_qs(urlsplit(a[0].get("href")).query)
        m = _AZA_ISO_RE.match((q.get("highlight_docid") or [""])[0])
        if not m:
            continue
        y, mo, d, pre, yr = m.groups()
        docid = f"aza://{d}-{mo}-{y}-{pre}-{yr}"
        case = f"{pre}/{yr}"
        chamber = _div(li, "court")
        pub = li.xpath('.//span[contains(@class,"published_info")]/a')
        bge = ""
        if pub:
            bm = re.search(r"BGE-(\d+)-(\w+)-(\d+)", pub[0].get("href", ""))
            bge = _bge_id(*bm.groups()) if bm else ""
        snippet = " — ".join(x for x in (_div(li, "subject"), _div(li, "object").rstrip(","),
                                        f"published as {bge}" if bge else "") if x)
        hits.append(DecisionHit(id=docid, title=f"BGer {case}", court=f"Bundesgericht, {chamber}"
                                if chamber else "Bundesgericht", date=f"{y}-{mo}-{d}",
                                case_number=case, snippet=snippet[:300], url=_doc_url(docid)))
    return hits


def _bge_hits(root) -> list[DecisionHit]:
    hits = []
    for li in root.xpath('//div[@id="ranklist_exact"]//ol/li'):
        a = li.xpath('.//span[@class="rank_title"]/a')
        m = re.search(r"BGE-(\d+)-(\w+)-(\d+)", a[0].get("href", "")) if a else None
        if not m:
            continue
        cite = _bge_id(*m.groups())
        urt = _div(li, "urt")
        regeste = re.sub(r"^Regeste\s*\[[^\]]*\]\s*", "", _div(li, "regeste"))
        hits.append(DecisionHit(id=cite, title=f"{cite} — {urt}"[:250] if urt else cite,
                                court="Bundesgericht", date=_text_date(urt),
                                snippet=regeste[:300], url=_doc_url(_bge_docid(cite))))
    return hits


def _bge_docid(cite: str) -> str:
    m = _BGE_RE.match(cite)
    return f"atf://{int(m.group(1))}-{m.group(2)}-{int(m.group(3))}:de"


def _content(root):
    c = root.xpath('//div[@id="highlight_result"]/div[@class="content"]')
    if not c or not _http.clean(c[0].text_content()):
        return None
    for el in c[0].xpath('.//div[contains(@class,"pagebreak")]'):
        el.drop_tree()
    return c[0]


# --------------------------------------------------------------------------- #
# Adapter
# --------------------------------------------------------------------------- #
class Switzerland(Jurisdiction):
    code = "ch"
    name = "Switzerland"
    languages = ("de", "fr", "it")
    aliases = ("che", "switzerland", "schweiz", "suisse", "svizzera", "confoederatio helvetica")
    sources = (
        Source(
            "Bundesgericht / Tribunal fédéral — Rechtsprechung (gratis), eurospider search",
            "https://search.bger.ch/ext/eurospider/live/de/php/aza/http/index.php?lang=de",
            covers=("caselaw",),
            licence=("unknown: no reuse terms published; the site footer says '© Alle Rechte "
                     "vorbehalten', but court decisions are not copyright-protected in "
                     "Switzerland (Art. 5(1)(c) URG, SR 231.1)"),
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit=("robots.txt Crawl-delay: 2 (read 2026-11-05); using 2 s spacing, "
                        "no 429 seen in a handful of requests (2026-11)"),
            terms_url="https://search.bger.ch/robots.txt",
        ),
        Source(
            "Fedlex — Systematische Rechtssammlung (Federal Chancellery): SPARQL + filestore",
            "https://www.fedlex.admin.ch/",
            covers=("legislation",),
            licence=("not copyright-protected (Art. 5 URG); free reuse under Art. 49 PublV "
                     "(SR 170.512.1): text unchanged, kept apart from comments, with the "
                     "notice 'Dies ist keine amtliche Veröffentlichung...'; paid "
                     "redistribution only in value-added form"),
            commercial_use=True,
            ai_use=None,
            auth="none",
            rate_limit=("unknown, nothing documented; 1 s spacing on both hosts, no 429 seen "
                        "(2026-11). fedlex.data.admin.ch robots.txt disallows /filestore/*, so "
                        "files are read from www.fedlex.admin.ch/filestore (allowed)"),
            terms_url="https://www.fedlex.admin.ch/de/broadcasters",
            warning=("Fedlex's data host (fedlex.data.admin.ch) disallows automated access to "
                     "its law files in robots.txt; this tool reads the same files from "
                     "www.fedlex.admin.ch, which allows it. Get the Federal Chancellery's "
                     "explicit permission before relying on this at scale."),
        ),
    )
    caselaw_filters = {
        "collection": "aza (default: all Federal Supreme Court decisions since 2000) or "
                      "bge (published leading cases, BGE/ATF, since 1954)",
        "date_from": "decision date from, YYYY-MM-DD or a year YYYY (aza: exact date; bge: year only)",
        "date_to": "decision date to, YYYY-MM-DD or a year YYYY (aza: exact date; bge: year only)",
    }
    min_interval = {"search.bger.ch": 2.0, "fedlex.data.admin.ch": 1.0, "www.fedlex.admin.ch": 1.0}
    notes = ("Federal law (SR, German consolidated text; FR/IT exist on Fedlex) and Federal "
             "Supreme Court decisions (since 2000, BGE since 1954, in the language of the "
             "case: DE/FR/IT). Law id = SR number (ZGB 210, OR 220). Decision ids: "
             "aza://DD-MM-YYYY-4A_640-2011, a case number like 4A_640/2011, or 'BGE 150 III 71'. "
             "No cantonal law or cantonal courts.")
    gaps = (
        "Cantonal law: not researched yet",
        ("Cantonal court decisions: official cantonal sites not researched; entscheidsuche.ch has "
         "them but is not official"),
        ("Federal Administrative, Criminal and Patent Courts: not researched yet "
         "(entscheidsuche.ch has them, not official)"),
        ("Federal law in French and Italian: on Fedlex; source exists but not built yet (German "
         "only)"),
        "Historical versions of federal law: on Fedlex; not built yet (latest consolidation only)",
        ("Unpublished BGer decisions before 2000: not in the free eurospider collection (BGE "
         "leading cases from 1954 only)"),
    )
    samples = {
        "caselaw_query": "Mietzinsherabsetzung",
        "decision_id": "aza://19-12-2011-4A_640-2011",
        "legislation_query": "Zivilgesetzbuch",
        "law_id": "210",
        "provision": "Art. 1",
    }

    # ---- case law ---------------------------------------------------------- #
    async def search_caselaw(self, query, *, limit, page, filters):
        coll = str(filters.get("collection", "aza")).strip().lower()
        if coll not in ("aza", "bge"):
            raise BadRequest(f"collection {coll!r} unknown. Use 'aza' or 'bge'.")
        dates = {}
        for key in ("date_from", "date_to"):
            v = str(filters.get(key) or "").strip()
            if re.fullmatch(r"\d{4}", v):  # a bare year: whole year (bge works by year)
                v += "-01-01" if key == "date_from" else "-12-31"
            if v and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
                raise BadRequest(f"{key} {v!r} must be YYYY-MM-DD or a year (YYYY).")
            dates[key] = v
        if not (query or "").strip():
            raise BadRequest("bger.ch needs search words.")
        limit = max(1, min(int(limit), 50))
        start = (max(1, int(page)) - 1) * limit
        if coll == "aza":
            url = f"{BGER}/aza/http/index.php"
            de = lambda v: f"{v[8:10]}.{v[5:7]}.{v[:4]}" if v else ""  # noqa: E731
            base = {"lang": "de", "type": "simple_query", "query_words": query,
                    "top_subcollection_aza": "all", "from_date": de(dates["date_from"]),
                    "to_date": de(dates["date_to"]), "sort": "relevance"}
            parse = _aza_hits
        else:
            url = f"{BGER}/clir/http/index.php"
            base = {"lang": "de", "type": "simple_query", "query_words": query,
                    "top_subcollection_clir": "bge", "from_year": dates["date_from"][:4] or "1954",
                    "to_year": dates["date_to"][:4] or str(datetime.date.today().year)}
            parse = _bge_hits
        items, total, src_page = [], None, start // 10 + 1
        skip = start % 10
        while len(items) < limit:
            root = await _bger_html(url, {**base, "page": src_page})
            total = _total(root)
            hits = parse(root)
            items += hits[skip:]
            skip = 0
            if len(hits) < 10 or src_page * 10 >= total:
                break
            src_page += 1
        return Results(items=items[:limit], total=total,
                       note="" if coll == "bge" else
                       "Decisions are anonymised and in the language of the case (DE/FR/IT).")

    async def get_decision(self, id):
        raw = (id or "").strip()
        if _BGE_RE.match(raw) and not _CASE_RE.match(raw):
            return await self._bge(raw)
        m = _AZA_RE.match(raw) or _AZA_ISO_RE.match(raw)
        if m:
            g = m.groups()
            d, mo, y = (g[0], g[1], g[2]) if _AZA_RE.match(raw) else (g[2], g[1], g[0])
            return await self._aza(f"aza://{d}-{mo}-{y}-{g[3]}-{g[4]}")
        c = _CASE_RE.match(raw)
        if c:
            case = f"{c.group(1).upper()}_{c.group(2)}/{c.group(3)}"
            res = await self.search_caselaw(case, limit=10, page=1, filters={})
            hit = next((h for h in res.items if h.case_number.upper() == case.upper()), None)
            if not hit:
                raise NotFound(f"no Federal Supreme Court decision {case} found")
            return await self._aza(hit.id)
        raise BadRequest(f"decision id {id!r} not understood. Use aza://19-12-2011-4A_640-2011, "
                         "a case number like 4A_640/2011, or a BGE citation like BGE 150 III 71.")

    async def _aza(self, docid: str) -> Decision:
        root = await _bger_html(f"{BGER}/aza/http/index.php",
                                {"lang": "de", "type": "show_document", "highlight_docid": docid})
        c = _content(root)
        if c is None:
            raise NotFound(f"no Federal Supreme Court decision {docid}")
        d, mo, y, pre, yr = _AZA_RE.match(docid).groups()
        case = f"{pre}/{yr}"
        text = _http.html_to_md(lxml.html.tostring(c, encoding="unicode"))
        chamber = next((ln for ln in re.split(r"\n+", text)[:20]
                        if re.search(r"(Abteilung|Cour|Corte|Camera)\b", ln)), "")
        return Decision(id=docid, title=f"BGer {case}", text=text, url=_doc_url(docid),
                        court=_http.clean(f"Bundesgericht, {chamber}" if chamber else "Bundesgericht"),
                        date=f"{y}-{mo}-{d}", case_number=case)

    async def _bge(self, raw: str) -> Decision:
        m = _BGE_RE.match(raw)
        cite = _bge_id(*m.groups())
        docid = _bge_docid(cite)
        root = await _bger_html(f"{BGER}/clir/http/index.php",
                                {"lang": "de", "type": "show_document", "highlight_docid": docid})
        c = _content(root)
        if c is None:
            raise NotFound(f"no leading case {cite}")
        rub = c.xpath('.//p[@class="rubrum"]')
        rubrum = _http.clean(rub[0].text_content()) if rub else ""
        summary = ""
        h = c.xpath('.//h3[contains(., "Regeste")]')
        if h:
            paras = []
            for sib in h[0].itersiblings():
                if sib.tag == "h3":
                    break
                paras.append(_http.clean(sib.text_content()))
            summary = "\n\n".join(p for p in paras if p)
        text = _http.html_to_md(lxml.html.tostring(c, encoding="unicode"))
        return Decision(id=cite, title=f"{cite} — {rubrum}"[:300] if rubrum else cite, text=text,
                        url=_doc_url(docid), court="Bundesgericht", date=_text_date(rubrum),
                        summary=summary, metadata={"Rubrum": rubrum} if rubrum else {})

    # ---- legislation ------------------------------------------------------- #
    async def search_legislation(self, query, *, limit, page, filters):
        q = _http.clean(query)
        if not q:
            raise BadRequest("give search words, an abbreviation (OR, ZGB) or an SR number.")
        limit = max(1, min(int(limit), 50))
        offset = (max(1, int(page)) - 1) * limit
        exact = re.sub(r"^SR\s*", "", q, flags=re.I).lower()
        words = " && ".join(f"CONTAINS(LCASE(STR(?title)), {_lit(w.lower())})" for w in q.split())
        words_any = " && ".join(f"CONTAINS(LCASE(STR(?t2)), {_lit(w.lower())})" for w in q.split())
        rows = await _sparql(f"""
SELECT DISTINCT ?cc ?sr ?title ?abbr ?status ?date ?typ ?st WHERE {{
 ?cc a jolux:ConsolidationAbstract ; jolux:classifiedByTaxonomyEntry/skos:notation ?sr ;
     jolux:isRealizedBy ?e .
 ?e jolux:language {DEU} ; jolux:title ?title .
 OPTIONAL {{ ?e jolux:titleShort ?abbr0 }}
 BIND(COALESCE(STR(?abbr0), "") AS ?abbr)
 OPTIONAL {{ ?cc jolux:isRealizedBy ?e2 . ?e2 jolux:title ?t2 }}
 OPTIONAL {{ ?cc jolux:inForceStatus ?st . ?st skos:prefLabel ?status FILTER(LANG(?status) = "de") }}
 OPTIONAL {{ ?cc jolux:dateDocument ?date }}
 OPTIONAL {{ ?cc jolux:typeDocument/skos:prefLabel ?typ FILTER(LANG(?typ) = "de") }}
 FILTER(({words}) || ({words_any}) || LCASE(?abbr) = {_lit(exact)} || STR(?sr) = {_lit(exact)})
}} ORDER BY DESC(STR(?sr) = {_lit(exact)} || LCASE(?abbr) = {_lit(exact)})
   DESC(CONTAINS(LCASE(?abbr), {_lit(exact)}))
   DESC(CONTAINS(LCASE(STR(?title)), {_lit(exact)}) || COALESCE(CONTAINS(LCASE(STR(?t2)), {_lit(exact)}), false))
   DESC(COALESCE(?st = {IN_FORCE}, false))
   DESC(COALESCE(CONTAINS(STR(?typ), "gesetz"), false))
   STRLEN(?title) ?cc
LIMIT {limit + 1} OFFSET {offset}""")
        items, seen = [], set()
        for r in rows:
            if r["cc"] in seen:
                continue
            seen.add(r["cc"])
            title = _http.clean(r["title"])
            if r.get("abbr") and r["abbr"] not in title:
                title += f" ({r['abbr']})"
            items.append(LawHit(id=r["sr"], title=title, type=r.get("typ", ""),
                                number=f"SR {r['sr']}", date=(r.get("date") or "")[:10],
                                status=r.get("status", ""), url=_eli_url(r["cc"])))
        items = items[:limit]
        counts: dict[str, int] = {}
        for it in items:
            counts[it.id] = counts.get(it.id, 0) + 1
        dup = sorted(k for k, n in counts.items() if n > 1)
        reuse = (f" SR number(s) {', '.join(dup)} appear more than once: Fedlex reuses an SR number "
                 "for a repealed act and its successor; check the status of each row." if dup else "")
        return Results(items=items, total=None,
                       note="Titles are shown in German; French and Italian title words are matched too "
                            "(an exact phrase ranks first). "
                            "Law id = SR number. FR/IT texts exist on Fedlex." + reuse)

    async def get_legislation_toc(self, id):
        info, law = await _law(id)
        return Toc(id=info["sr"], title=_law_title(info), url=_eli_url(info["cc"]),
                   entries=list(law["toc"]))

    async def get_legislation_provision(self, id, provision):
        info, law = await _law(id)
        key = _norm_label(provision)
        if not key:
            raise BadRequest("give a provision such as 'Art. 1', '1', '6a' or 'Schlusstitel Art. 1'.")
        hit = law["arts"].get(key)
        if hit is None:
            raise NotFound(f"no {provision!r} in SR {info['sr']}. See get_legislation_toc for "
                           "the labels.")
        label, anchor, body = hit
        return Provision(law_id=info["sr"], law_title=_law_title(info), provision=label,
                         text=f"{body}\n\n{_NOTICE}", url=f"{_eli_url(info['cc'])}#{anchor}",
                         as_of=info["date"])

    async def get_legislation_text(self, id):
        info, law = await _law(id)
        meta = {"SR": info["sr"], "Status": info["status"], "ELI": info["cc"]}
        return LawText(id=info["sr"], title=_law_title(info), text=f"{law['text']}\n\n{_NOTICE}",
                       url=_eli_url(info["cc"]), as_of=info["date"],
                       metadata={k: v for k, v in meta.items() if v})
