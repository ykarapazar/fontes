"""Monaco: Legimonaco (Gouvernement Princier, Direction des Affaires Juridiques), the
official portal for Monegasque legislation and case law.

Gotchas this code encodes (verified 2026-11-06):
  * Search goes through the site's own public Elasticsearch endpoint
    (POST https://legimonaco.mc/~~search/depot/_search), the same one the site's
    search page calls from the browser. Documents are `scgroup: res` (one per text
    version); articles are child `entry` docs. Old/future consolidated versions are
    separate docs, filtered out the way the site does it: startDate > now or
    endDate <= now. The search box also excludes processing home/folder, trashed and
    excludeFromSearch docs.
  * The id is the document's path without the "@<version>" suffix and leading slash:
    "code/code-civil", "tnc/loi/1948/11-24-490", "constitution",
    "jurisprudence/cour-revision/2024/...". Its page is https://legimonaco.mc/<id>/,
    which serves the current version as static HTML (Code civil is ~3 MB, one fetch).
  * Article sections carry data-title ("Article 1er"); headings are nested
    section.legContainer. #content also holds hidden "histoItem" consolidation-history
    popups; we skip them.
  * Decisions: the page holds casePart sections (abstract, summary, visa, argument,
    dispositif, composition). Parties are pseudonymised by the source ("j.E c/ i.D").
    IDBD ("identifiant base de données") is the site's numeric decision id; we accept it
    as a decision id variant.
  * robots.txt: 404 (none). No terms-of-use / mentions-légales page exists on the site
    (checked 2026-11-06).
"""
from __future__ import annotations

import copy
import re

from lxml import etree, html

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

SITE = "https://legimonaco.mc/"
ES = SITE + "~~search/depot/_search"
HOST = "legimonaco.mc"

COURTS = {
    "tribunal-supreme": "Tribunal Suprême",
    "cour-revision": "Cour de révision",
    "cour-appel": "Cour d'appel",
    "tribunal-premiere-instance": "Tribunal de première instance",
    "tribunal-criminel": "Tribunal criminel",
    "tribunal-correctionnel": "Tribunal correctionnel",
    "tribunal-simple-police": "Tribunal de simple police",
    "juge-paix": "Juge de paix",
    "juge-tutelaire": "Juge tutélaire",
    "tribunal-travail": "Tribunal du travail",
    "cour-superieure-arbitrage": "Cour supérieure d'arbitrage",
    "commission-arbitrale-loyers-habitation": "Commission arbitrale des loyers d'habitation",
    "commission-arbitrale-loyers-commerciaux": "Commission arbitrale des loyers commerciaux",
    "cour-europeenne-droits-homme": "Cour européenne des droits de l'Homme",
}
LAW_TYPES = {"constitution": "constitution", "code": "tc", "law": "legislation",
             "regulation": "regulation", "treaty": "tai"}
TYPE_LABEL = {"constitution": "Constitution", "tc": "Code", "tai": "Traité / accord"}
NATURES = {
    "loi": "Loi", "ordonnance-loi": "Ordonnance-loi", "ordonnance": "Ordonnance Souveraine",
    "arrete-ministeriel": "Arrêté ministériel", "arrete-directorial": "Arrêté directorial",
    "arrete-municipal": "Arrêté municipal", "decision-souveraines": "Décision Souveraine",
    "decision-ministerielle": "Décision ministérielle", "decision": "Décision",
    "autre-texte-reglementaire": "Autre texte réglementaire",
}
_MUST_NOT = [
    {"range": {"startDate": {"gt": "now"}}},
    {"range": {"endDate": {"lte": "now"}}},
    {"terms": {"processing": ["home", "folder"]}},
    {"terms": {"trashed": ["true"]}},
    {"terms": {"excludeFromSearch": ["true"]}},
]
_TEXT_FIELDS = ["title^2", "enTitle", "enBody"]
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_ID = re.compile(r"^[a-z][\w.-]*(?:/[\w.-]+)*$")

_pages: dict[str, html.HtmlElement] = {}


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _strip_id(raw: str) -> str:
    """URL / path / id -> 'code/code-civil' (no host, no leading/trailing slash, no @version)."""
    s = (raw or "").strip()
    s = re.sub(r"^https?://(?:www\.)?legimonaco\.mc", "", s)
    s = re.sub(r"[?#].*$", "", s)
    s = re.sub(r"/index\.html$", "", s)
    s = s.strip("/").split("@")[0].strip("/")
    return s


def _offset(page: int, limit: int) -> int:
    off = (max(1, page) - 1) * limit
    if off + limit > 10000:   # Elasticsearch max_result_window
        raise BadRequest(f"page {page} x limit {limit} is past what the source allows "
                         "(at most 10000 results deep); narrow the query or use a smaller page.")
    return off


async def _es(query: dict) -> dict:
    r = await _http.post(ES, json=query)
    if r.status_code != 200:
        raise SourceError(f"Legimonaco search returned HTTP {r.status_code}", r.status_code)
    try:
        data = r.json()
        data["hits"]["hits"]
    except (ValueError, KeyError, TypeError):
        raise SourceError("Legimonaco search returned an unexpected payload", r.status_code)
    return data


def _text_query(q: str) -> dict:
    return {"simple_query_string": {"fields": _TEXT_FIELDS, "default_operator": "AND",
                                    "query": q}}


def _word_query(q: str) -> dict | None:
    """Plain words -> unstemmed prefix match on the body. The source's stemmed field also
    matches look-alikes ('licenciement' finds 'licences'). None when the query uses operators."""
    words = q.split()
    if not words or not all(re.fullmatch(r"[^\W_]+", w) for w in words):
        return None
    return {"simple_query_string": {"fields": ["enBody.exact"], "default_operator": "AND",
                                    "query": " ".join(w + "*" if len(w) >= 4 else w
                                                      for w in words)}}


def _snippet(hit: dict) -> str:
    frag = (hit.get("highlight") or {}).get("enBody") or []
    return _http.clean(re.sub(r"</?em>", "", frag[0])) if frag else ""


def _iso(s) -> str:
    s = str(s or "")
    return s[:10] if _DATE.match(s[:10]) else ""


def _check_date(name: str, v: str) -> str:
    if not _DATE.match(v or ""):
        raise BadRequest(f"filter {name}={v!r}: use YYYY-MM-DD, e.g. 2020-01-31.")
    return v


async def _page(pid: str) -> html.HtmlElement:
    """Fetch and parse https://legimonaco.mc/<pid>/ (small in-memory cache)."""
    if pid in _pages:
        return _pages[pid]
    url = SITE + pid + "/"
    r = await _http.get(url)
    if r.status_code == 404:
        raise NotFound(f"no Legimonaco page at {url}. Use an id from the search tools.")
    if r.status_code != 200:
        raise SourceError(f"Legimonaco returned HTTP {r.status_code} for {url}", r.status_code)
    root = html.fromstring(r.content)
    if not root.xpath('//div[@id="content"]') or not root.xpath('//header[contains(@class,"documentTitle")]'):
        raise NotFound(f"{url} is not a Legimonaco document page (block page or listing).")
    return _http.lru_put(_pages, pid, root, 4)


def _cls(el) -> list[str]:
    return (el.get("class") or "").split()


def _content(root):
    return root.xpath('//div[@id="content"]')[0]


def _title(root) -> str:
    return _http.clean(root.xpath('string(//header[contains(@class,"documentTitle")]//h1)'))


def _info(root) -> tuple[dict[str, str], dict[str, str]]:
    """infoBlocks -> ({label: value}, {label key e.g. 'date', 'lastMod': iso date})."""
    meta, dates = {}, {}
    for b in root.xpath('//header[contains(@class,"documentInfo")]/div[contains(@class,"infoBlock")]'):
        lab = b.xpath('./i')
        val = b.xpath('./div[contains(@class,"infoValue")]')
        if not lab or not val:
            continue
        label = _http.clean(lab[0].text_content())
        meta[label] = _http.clean(val[0].text_content())
        if val[0].get("data-l10n-date"):
            dates[lab[0].get("data-l10n") or label] = val[0].get("data-l10n-date")
    return meta, dates


def _md(el) -> str:
    """One element -> clean markdown, without the copy/anchor buttons."""
    el = copy.deepcopy(el)
    for junk in el.xpath('.//*[contains(@class,"title_tools")] | .//button | '
                         './/a[contains(@class,"sectionAnchor")]'):
        junk.getparent().remove(junk)
    return _http.html_to_md(etree.tostring(el, encoding="unicode", method="html"))


def _heading(sec) -> str:
    h = sec.xpath('./*[contains(@class,"section_ti")]//*[contains(@class,"title_text")]')
    return _http.clean(h[0].text_content()) if h else ""


def _norm(label: str) -> str:
    s = _http.clean(label).lower().rstrip(".")
    s = re.sub(r"^(?:article|art\.?)\s*", "", s)
    s = re.sub(r"^(\d+)\s*(?:er|ère|re)\b", r"\1", s)
    if s in ("premier", "première"):
        s = "1"
    return re.sub(r"\s*-\s*", "-", s)


_AMEND = re.compile(r"^(?:remplacé|modifié|ajouté|abrogé|complété|introduit|créé|rétabli|loi n|ordonnance)", re.I)


def _opening(sec) -> str:
    """First words of an article's own text (Monegasque articles have no headings)."""
    for para in _md(sec).split("\n\n"):
        para = para.strip()
        if para and not para.startswith("#") and not _AMEND.match(para):
            return para if len(para) <= 90 else para[:90].rsplit(" ", 1)[0] + "…"
    return ""


def _arts(root) -> list:
    return root.xpath('//div[@id="content"]//section[contains(concat(" ",@class," ")," art ")]')


def _law_id(raw: str) -> str:
    lid = _strip_id(raw)
    if not lid or not _ID.match(lid) or lid.startswith("jurisprudence"):
        raise BadRequest(f"law id {raw!r} is not a Legimonaco text path. Use the id from "
                         "search_legislation, e.g. code/code-civil, constitution or "
                         "tnc/loi/1948/11-24-490.")
    return lid


def _law_title(root, lid: str) -> str:
    return _title(root) or lid


def _as_of(root) -> str:
    _, dates = _info(root)
    return _iso(dates.get("lastMod") or "")


# --------------------------------------------------------------------------- #
class Monaco(Jurisdiction):
    code = "mc"
    name = "Monaco"
    languages = ("fr",)
    aliases = ("monaco", "principauté de monaco", "principality of monaco", "mco")
    sources = (
        Source(
            "Legimonaco — Gouvernement Princier de Monaco (Direction des Affaires Juridiques): "
            "Constitution, codes, laws, ordinances, treaties and court decisions",
            SITE,
            covers=("caselaw", "legislation"),
            licence=("unknown: the site states no licence or terms of use (no mentions-légales "
                     "page, checked 2026-11-06); official texts of the Principality"),
            commercial_use=None,
            ai_use=None,   # robots.txt is 404 (no opt-out); no terms found
            auth="none",
            rate_limit=("unknown, nothing documented; 1 s spacing, no 429 seen in ~30 requests "
                        "(2026-11). robots.txt: none (404, 2026-11-06)"),
            terms_url=SITE,
        ),
    )
    caselaw_filters = {
        "court": "court key: " + ", ".join(COURTS),
        "date_from": "decision date from, YYYY-MM-DD",
        "date_to": "decision date to, YYYY-MM-DD",
    }
    legislation_filters = {
        "type": "one of: " + ", ".join(LAW_TYPES),
        "nature": "law/regulation nature: " + ", ".join(NATURES),
    }
    min_interval = {HOST: 1.0}
    notes = ("Official Legimonaco portal, French. Current consolidated Constitution, codes, laws, "
             "ordinances and treaties; ~6,800 decisions of the Monegasque courts (parties "
             "pseudonymised). Ids are page paths: code/code-civil, tnc/loi/1948/11-24-490, "
             "jurisprudence/<court>/<year>/<mm-dd-idbd>.")
    gaps = (
        "Past and future consolidated versions: source exists and works but not built yet "
         "(current version only)",
        "Journal de Monaco (official gazette) as published: not researched yet",
    )
    samples = {
        "caselaw_query": "bail commercial",
        "decision_id": "jurisprudence/commission-arbitrale-loyers-commerciaux/2024/05-15-30935",
        "legislation_query": "code civil",
        "law_id": "code/code-civil",
        "provision": "Article 1",
    }

    # ------------------------------------------------------------------ caselaw
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        must: list[dict] = [{"term": {"scgroup": "res"}}, {"term": {"type": "case"}}]
        word = _word_query(query.strip()) if (query or "").strip() else None
        if (query or "").strip():
            must.append(word or _text_query(query.strip()))
        court = filters.get("court")
        if court:
            if court not in COURTS:
                raise BadRequest(f"court {court!r} unknown; use one of: {', '.join(COURTS)}.")
            must.append({"term": {"jurisdiction": court}})
        rng = {}
        if filters.get("date_from"):
            rng["gte"] = _check_date("date_from", filters["date_from"])
        if filters.get("date_to"):
            rng["lte"] = _check_date("date_to", filters["date_to"])
        if rng:
            must.append({"range": {"date": rng}})
        bool_q = {"must": must, "must_not": _MUST_NOT[2:]}
        if word:
            # the unstemmed prefix match scores every hit alike; rank by the stemmed body score
            # and prefer the words side by side ('bail commercial'), without filtering anything
            bool_q["should"] = [_text_query(query.strip()),
                                {"match_phrase": {"enBody": {"query": query.strip(), "boost": 3}}}]
        q = {"query": {"bool": bool_q},
             "_source": ["path", "title", "date", "jurisdiction", "idbd", "parties"],
             "from": _offset(page, limit), "size": limit, "track_total_hits": True,
             "highlight": {"fields": {"enBody": {"fragment_size": 220, "number_of_fragments": 1}}}}
        if not (query or "").strip():
            q["sort"] = [{"date": {"order": "desc"}}]
        data = await _es(q)
        if word and not data["hits"]["hits"] and page == 1:
            # exact field is accent-sensitive; retry with the source's stemmed search
            must[2] = _text_query(query.strip())
            data = await _es(q)
        items = []
        for h in data["hits"]["hits"]:
            s = h.get("_source") or {}
            pid = _strip_id(s.get("path", ""))
            if not pid:
                continue
            court_l = COURTS.get(s.get("jurisdiction", ""), s.get("jurisdiction", ""))
            items.append(DecisionHit(
                id=pid, title=_http.clean(s.get("title")) or f"{court_l} {s.get('idbd', '')}",
                court=court_l, date=_iso(s.get("date")), snippet=_snippet(h),
                url=SITE + pid + "/"))
        total = (data["hits"].get("total") or {}).get("value")
        note = "Parties are pseudonymised by the source. Text in French."
        if court == "tribunal-premiere-instance":
            note += (" Matches are words anywhere in the judgment, so some hits only mention the"
                     " term; employment disputes sit in court='tribunal-travail'.")
        return Results(items=items, total=total, note=note)

    async def _decision_path(self, raw: str) -> str:
        s = _strip_id(raw)
        if re.fullmatch(r"\d{1,7}", s):   # IDBD
            data = await _es({"query": {"bool": {"must": [
                {"term": {"scgroup": "res"}}, {"term": {"type": "case"}},
                {"term": {"idbd": s}}]}}, "_source": ["path"], "size": 1})
            hits = data["hits"]["hits"]
            if not hits:
                raise NotFound(f"no Legimonaco decision with IDBD {s}.")
            return _strip_id(hits[0]["_source"]["path"])
        if not s.startswith("jurisprudence/") or not _ID.match(s):
            raise BadRequest(f"decision id {raw!r}: use the id from search_caselaw, e.g. "
                             "jurisprudence/cour-revision/2024/03-21-30733, or a numeric IDBD.")
        return s

    async def get_decision(self, id):
        pid = await self._decision_path(id)
        root = await _page(pid)
        meta, dates = _info(root)
        parts = root.xpath('//div[@id="content"]/section[contains(@class,"casePart")]')
        summary = [p for p in parts if {"abstract", "summary"} & set(_cls(p))]
        body = [p for p in parts if p not in summary]
        text = "\n\n".join(t for t in (_md(p) for p in (body or parts)) if t)
        if not text:
            raise SourceError(f"Legimonaco page {pid} has no decision text.")
        idbd = meta.get("IDBD", "")
        court = meta.get("Juridiction", "")
        return Decision(
            id=pid, title=_title(root) or f"{court} {idbd}".strip(), text=text,
            url=SITE + pid + "/", court=court,
            date=_iso(dates.get("date") or ""),
            summary="\n\n".join(t for t in (_md(p) for p in summary) if t),
            metadata={k: v for k, v in meta.items() if k not in ("Type", "Juridiction", "Date")})

    # ------------------------------------------------------------- legislation
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        typ = filters.get("type")
        if typ and typ not in LAW_TYPES:
            raise BadRequest(f"type {typ!r} unknown; use one of: {', '.join(LAW_TYPES)}.")
        must: list[dict] = [{"term": {"scgroup": "res"}},
                            {"terms": {"type": [LAW_TYPES[typ]] if typ else list(LAW_TYPES.values())}}]
        nature = filters.get("nature")
        if nature:
            if nature not in NATURES:
                raise BadRequest(f"nature {nature!r} unknown; use one of: {', '.join(NATURES)}.")
            must.append({"term": {"tncNature": nature}})
        note = "Current consolidated versions, in French."
        qs = (query or "").strip()
        if re.fullmatch(r"(?:le\s+)?code\s+du\s+travail", qs, re.I):
            # Monaco has no single labour code: employment law is Loi n° 729 and its satellites
            qs = "contrat de travail"
            note = ("Monaco has no 'Code du travail'; employment law is Loi n° 729 du 16 mars 1963 "
                    "concernant le contrat de travail and related texts (searched as 'contrat de travail'). "
                    + note)
        if qs:
            must.append(_text_query(qs))
        q = {"query": {"bool": {"must": must, "must_not": _MUST_NOT}},
             "_source": ["path", "title", "date", "type", "tncNature", "number",
                         "legislationAbrogated", "regulationAbrogated", "taiAbrogated"],
             "from": _offset(page, limit), "size": limit, "track_total_hits": True,
             "highlight": {"fields": {"enBody": {"fragment_size": 220, "number_of_fragments": 1}}}}
        if not (query or "").strip():
            q["sort"] = [{"date": {"order": "desc"}}]
        data = await _es(q)
        items = []
        for h in data["hits"]["hits"]:
            s = h.get("_source") or {}
            pid = _strip_id(s.get("path", ""))
            if not pid:
                continue
            ab = s.get("legislationAbrogated") or s.get("regulationAbrogated") or s.get("taiAbrogated")
            status = {"yes": "repealed", "no": "in force"}.get(ab or "", "")
            if s.get("type") in ("tc", "constitution"):
                status = "in force"
            num = s.get("number") or ""
            items.append(LawHit(
                id=pid, title=_http.clean(s.get("title")) or pid,
                type=NATURES.get(s.get("tncNature", ""), TYPE_LABEL.get(s.get("type", ""), s.get("type", ""))),
                number="" if num.startswith("tai") else num,
                date=_iso(s.get("date")), status=status, snippet=_snippet(h),
                url=SITE + pid + "/"))
        total = (data["hits"].get("total") or {}).get("value")
        return Results(items=items, total=total, note=note)

    async def get_legislation_toc(self, id):
        lid = _law_id(id)
        root = await _page(lid)
        entries: list[TocEntry] = []

        def walk(el, level):
            for ch in el.iterchildren():
                if not isinstance(ch.tag, str):
                    continue
                c = _cls(ch)
                if ch.tag == "section" and "art" in c:
                    label = _http.clean(ch.get("data-title")) or _heading(ch)
                    head = _heading(ch)
                    if (not head or head == label) and (hint := _opening(ch)):
                        head = f"{label} - {hint}"
                    entries.append(TocEntry(title=head or label, level=level, provision=label))
                elif ch.tag == "section" and "legContainer" in c:
                    entries.append(TocEntry(title=_heading(ch), level=level))
                    walk(ch, level + 1)
                elif ch.tag == "div" and not any(x.startswith("histoItem") for x in c):
                    walk(ch, level)

        walk(_content(root), 0)
        return Toc(id=lid, title=_law_title(root, lid), url=SITE + lid + "/", entries=entries,
                   note="Legimonaco articles have no headings, so `keyword` only sees the article number and "
                        "the opening words shown here, not the full text. To find a topic (French terms, "
                        "with accents, e.g. 'préavis'), use search_legislation or read get_legislation_text and look there.")

    async def get_legislation_provision(self, id, provision):
        lid = _law_id(id)
        root = await _page(lid)
        want = _norm(provision)
        if not want:
            raise BadRequest("provision is empty; use a label from get_legislation_toc, e.g. 'Article 1'.")
        for sec in _arts(root):
            label = _http.clean(sec.get("data-title")) or _heading(sec)
            if _norm(label) == want:
                return Provision(law_id=lid, law_title=_law_title(root, lid), provision=label,
                                 text=_md(sec), url=SITE + lid + "/#" + (sec.get("id") or ""),
                                 as_of=_as_of(root) or _http.today())
        raise NotFound(f"no {provision!r} in {lid}. See get_legislation_toc for the labels.")

    async def get_legislation_text(self, id):
        lid = _law_id(id)
        root = await _page(lid)
        parts = []
        for el in _content(root).iterchildren():
            if not isinstance(el.tag, str) or el.tag in ("header", "nav", "script"):
                continue
            if any(c.startswith("histoItem") for c in _cls(el)):
                continue
            t = _md(el)
            if t:
                parts.append(t)
        text = "\n\n".join(parts)
        if not text:
            raise SourceError(f"Legimonaco page {lid} has no text.")
        meta, _ = _info(root)
        return LawText(id=lid, title=_law_title(root, lid), text=text, url=SITE + lid + "/",
                       as_of=_as_of(root), metadata=meta)
