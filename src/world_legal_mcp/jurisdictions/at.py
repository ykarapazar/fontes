"""Austria: case law and federal consolidated law from the RIS OGD API (data.bka.gv.at).

Gotchas this code encodes:
  * One API, v2.6: /Judikatur and /Bundesrecht, keyless JSON. Every query needs an
    `Applikation` (one court family per request: Justiz, Vfgh, Vwgh, Bvwg, Lvwg, Dsk).
  * Judikatur without Dokumenttyp flags returns only Rechtssaetze (headnotes); we
    ask for Entscheidungstexte (full decisions) by default.
  * There is no fetch-by-document-number endpoint. Content files live at
    ogd.ris.bka.gv.at/Dokumente/<Applikation>/<id>/<id>.html; the Applikation is
    derived from the id prefix (JJT_ = Justiz, JFT_ = Vfgh, ...). An ECLI is
    resolved with a full-text search for the ECLI string, then an exact match.
  * Bundesrecht konsolidiert is one document per paragraph/article (NOR... ids);
    the law-level "§ 0" document carries the title. Without Fassung.FassungVom,
    searches also return every historical version, so we always pass today.
  * `Abschnitt.Von/Bis/Typ` selects a provision; `Paragraph.Von` is ignored.
  * There is no whole-law text on the OGD hosts (GeltendeFassung.wxe redirects to
    www.ris.bka.gv.at, which sits behind a bot check), so get_legislation_text is
    not offered; the TOC is built by paging the paragraph list (100 per request).
  * Content HTML repeats every sentence in a screen-reader `sr-only` span
    ("Paragraph 508 a, Absatz 2"); those are removed before conversion.
  * DokumenteProSeite only accepts Ten/Twenty/Fifty/OneHundred; single results
    come back as an object instead of a list.
  * Documented limit: 0.5 req/s, no parallel connections (OGD FAQ).
"""
from __future__ import annotations

import re

import lxml.html
from markdownify import markdownify as _md

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, LawHit, Provision, Results, Toc, TocEntry

API = "https://data.bka.gv.at/ris/api/v2.6"
OGD = "https://ogd.ris.bka.gv.at"

# court filter value -> (Applikation, extra params)
_COURTS = {
    "justiz": ("Justiz", {}),
    "ogh": ("Justiz", {"Gericht": "OGH"}),
    "vfgh": ("Vfgh", {}),
    "vwgh": ("Vwgh", {}),
    "bvwg": ("Bvwg", {}),
    "lvwg": ("Lvwg", {}),
    "dsb": ("Dsk", {}),
}
_SHORT = {"Vfgh": "VfGH", "Vwgh": "VwGH", "Bvwg": "BVwG", "Dsk": "DSB"}
# document-number prefix -> Applikation (content folder)
_PREFIX = {"JJT": "Justiz", "JJR": "Justiz", "JFT": "Vfgh", "JFR": "Vfgh",
           "JWT": "Vwgh", "JWR": "Vwgh", "BVWGT": "Bvwg", "BVWGR": "Bvwg",
           "LVWGT": "Lvwg", "LVWGR": "Lvwg", "DSBT": "Dsk", "DSBR": "Dsk"}
_DOCTYPES = {"text": {"Dokumenttyp.SucheInEntscheidungstexten": "true"},
             "rechtssatz": {"Dokumenttyp.SucheInRechtssaetzen": "true"},
             "all": {"Dokumenttyp.SucheInEntscheidungstexten": "true",
                     "Dokumenttyp.SucheInRechtssaetzen": "true"}}
_PAGE_SIZES = ((10, "Ten"), (20, "Twenty"), (50, "Fifty"), (100, "OneHundred"))

_DOCID_RE = re.compile(r"^([A-Z]+)_[A-Za-z0-9_]+$")
_ECLI_RE = re.compile(r"^ECLI:AT:([A-Z0-9]+):\d{4}:[A-Za-z0-9.]+$", re.I)
_GESNR_RE = re.compile(r"^\d{8}$")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_LABEL_RE = re.compile(
    r"^(§+|par\.?|para\.?|paragraph|art\.?|artikel|article|anl\.?|anlage)?\s*"
    r"(\d+[a-z]*|[IVXLC]+[a-z]?)\.?$", re.I)
_META_BLOCKS = {"Gericht", "Entscheidungsdatum", "Geschäftszahl", "European Case Law Identifier",
                "Rechtssatznummer"}

_toc_cache: dict[str, Toc] = {}


# --------------------------------------------------------------------------- #
# Helpers (candidates for promotion: _items, _clean, _html_blocks, _paged)
# --------------------------------------------------------------------------- #
def _items(v) -> list:
    """RIS wraps repeated fields as {"item": x | [x, ...]}; single results are objects."""
    if isinstance(v, dict) and "item" in v:
        v = v["item"]
    if v in (None, ""):
        return []
    return v if isinstance(v, list) else [v]


def _clean(s) -> str:
    s = re.sub(r"<[^>]+>", " ", str(s or ""))
    return re.sub(r"\s+", " ", s).strip()


def _de_date(s: str) -> str:
    m = re.match(r"^(\d{2})\.(\d{2})\.(\d{4})$", (s or "").strip())
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else ""


def _iso(s) -> str:
    s = str(s or "")[:10]
    return s if _DATE_RE.match(s) else ""


def _tidy_md(md: str) -> str:
    md = md.replace("\xa0", " ")
    md = re.sub(r"[ \t]+", " ", md)
    md = re.sub(r" *\n *", "\n", md)
    return re.sub(r"\n{3,}", "\n\n", md).strip()


def _html_blocks(html: bytes) -> list[tuple[str, str]]:
    """Split a RIS content page into (block title, markdown body) pairs."""
    root = lxml.html.fromstring(html)
    for el in root.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " sr-only ")]'
                         ' | //script | //style | //img'):
        el.drop_tree()
    blocks = []
    for div in root.xpath('//div[contains(concat(" ", normalize-space(@class), " "), " contentBlock ")]'):
        h1 = div.find("h1")
        title = _clean(h1.text_content()) if h1 is not None else ""
        if h1 is not None:
            h1.drop_tree()
        for h in div.xpath(".//h1|.//h2|.//h3|.//h4|.//h5"):   # block title is ##, inner one deeper
            h.tag = f"h{min(6, int(h.tag[1]) + 1)}"
        body = _tidy_md(_md(lxml.html.tostring(div, encoding="unicode"), strip=["a"],
                            heading_style="ATX"))
        blocks.append((title, body))
    return blocks


async def _get_json(path: str, params: dict) -> dict:
    r = await _http.get(f"{API}/{path}", params=params)
    if r.status_code != 200:
        raise SourceError(f"RIS API returned HTTP {r.status_code}", r.status_code)
    try:
        res = r.json()["OgdSearchResult"]
    except (ValueError, KeyError, TypeError):
        raise SourceError("RIS API returned an unexpected payload", r.status_code)
    if "Error" in res:
        raise SourceError(f"RIS API error: {_clean(res['Error'].get('Message'))[:300]}", r.status_code)
    return res["OgdDocumentResults"]


def _docs(res: dict) -> tuple[list[dict], int]:
    refs = res.get("OgdDocumentReference") or []
    refs = refs if isinstance(refs, list) else [refs]
    return [x["Data"] for x in refs], int(res.get("Hits", {}).get("#text", 0) or 0)


async def _search(path: str, params: dict, size: str, page_no: int) -> tuple[list[dict], int]:
    try:
        res = await _get_json(path, {**params, "DokumenteProSeite": size, "Seitennummer": page_no})
    except SourceError as e:
        if page_no < 2 or e.status != 500:
            raise
        # RIS answers HTTP 500 for a page past the last one: report an empty page with the real total
        return [], _docs(await _get_json(path, {**params, "DokumenteProSeite": size, "Seitennummer": 1}))[1]
    return _docs(res)


async def _paged(path: str, params: dict, limit: int, page: int) -> tuple[list[dict], int]:
    """Map (limit, 1-based page) onto RIS's fixed page sizes."""
    limit = max(1, min(int(limit), 100))
    size, size_name = next((n, s) for n, s in _PAGE_SIZES if n >= limit)
    start = (max(1, int(page)) - 1) * limit
    src_page, off = start // size + 1, start % size
    docs, total = await _search(path, params, size_name, src_page)
    items = docs[off:off + limit]
    if len(items) < limit and off + limit > size and total > src_page * size:
        more, _ = await _search(path, params, size_name, src_page + 1)
        items += more[:limit - len(items)]
    return items, total


async def _content(app_folder: str, doc_id: str) -> bytes:
    url = f"{OGD}/Dokumente/{app_folder}/{doc_id}/{doc_id}.html"
    r = await _http.get(url)
    if r.status_code == 404:
        raise NotFound(f"no RIS document {doc_id}")
    if r.status_code != 200 or b"contentBlock" not in r.content:
        raise SourceError(f"RIS content fetch failed for {doc_id}", r.status_code)
    return r.content


# --------------------------------------------------------------------------- #
# Case law
# --------------------------------------------------------------------------- #
def _court(meta: dict, app: str) -> str:
    j = meta.get("Judikatur", {})
    return _clean((j.get(app) or {}).get("Gericht") or meta["Technisch"].get("Organ", ""))


def _decision_hit(d: dict) -> DecisionHit:
    meta = d["Metadaten"]
    doc_id = meta["Technisch"]["ID"]
    app = meta["Technisch"]["Applikation"]
    j = meta.get("Judikatur", {})
    court = _court(meta, app)
    short = _SHORT.get(app, court)
    if j.get("Dokumenttyp") == "Rechtssatz":
        rs = _items((j.get(app) or {}).get("Rechtssatznummern"))
        number = _clean(rs[0]) if rs else _clean("; ".join(_items(j.get("Geschaeftszahl"))))[:80]
        title = f"{short} {number} (Rechtssatz)"
    else:
        number = _clean("; ".join(_items(j.get("Geschaeftszahl"))))
        title = f"{short} {number}"
    snippet = _clean(j.get("Schlagworte")) or _clean(
        "; ".join(_items((j.get(app) or {}).get("Fachgebiete"))))
    ecli = re.search(r":(\d{4}):", j.get("EuropeanCaseLawIdentifier") or "")
    date = _iso(j.get("Entscheidungsdatum"))
    if j.get("Dokumenttyp") == "Rechtssatz":
        # the RIS date of a Rechtssatz is its last index update, not a decision date
        snippet = (f"First decided {ecli.group(1)} (per ECLI). " if ecli else "") + (
            f"Index date {date} (last update, not the decision date)." if date else "")
        date = ""
    return DecisionHit(id=doc_id, title=title, court=court, date=date,
                       case_number=number, snippet=snippet[:300],
                       url=meta["Allgemein"].get("DokumentUrl") or _doc_url(app, doc_id))


def _doc_url(app: str, doc_id: str) -> str:
    return f"{OGD}/Dokument.wxe?Abfrage={app}&Dokumentnummer={doc_id}"


async def _resolve_ecli(ecli: str) -> str:
    code = _ECLI_RE.match(ecli).group(1).upper()
    app = next((a for p, a in (("VFGH", "Vfgh"), ("VWGH", "Vwgh"), ("BVWG", "Bvwg"),
                               ("LVWG", "Lvwg"), ("DSB", "Dsk")) if code.startswith(p)), "Justiz")
    docs, _ = await _search("Judikatur", {"Applikation": app, "Suchworte": f'"{ecli}"',
                                          **_DOCTYPES["all"]}, "Ten", 1)
    hits = [d for d in docs
            if (d["Metadaten"].get("Judikatur", {}).get("EuropeanCaseLawIdentifier") or "").upper()
            == ecli.upper()]
    if not hits:
        raise NotFound(f"no RIS document with {ecli}")
    hits.sort(key=lambda d: d["Metadaten"]["Judikatur"].get("Dokumenttyp") != "Text")
    return hits[0]["Metadaten"]["Technisch"]["ID"]


# --------------------------------------------------------------------------- #
# Legislation
# --------------------------------------------------------------------------- #
def _parse_label(s: str) -> tuple[str, str]:
    """'§ 1090', '1090', 'par. 1090', 'Art. 7', 'Anlage 1' -> (Abschnitt.Typ, number)."""
    m = _LABEL_RE.match(re.sub(r"\s+", " ", (s or "").strip()))
    if not m:
        raise BadRequest(f"provision {s!r} not understood. Use e.g. '§ 1090', '1090', "
                         "'Art. 7' or 'Anlage 1'.")
    kind = (m.group(1) or "").lower().rstrip(".")
    typ = ("Paragraph" if kind.startswith(("§", "par")) else "Artikel" if kind.startswith("art")
           else "Anlage" if kind.startswith("anl") else "Alle")
    num = m.group(2)
    return typ, (num if re.match(r"^\d", num) else num.upper())


_COMPOUND_RE = re.compile(r"^art(?:\.|ikel)?\s*(\d+[a-z]*)\s*(?:,\s*)?§\s*(\d+[a-z]*)\.?$", re.I)


def _brkons(d: dict) -> dict:
    return d["Metadaten"]["Bundesrecht"]["BrKons"]


def _check_gesnr(law_id: str) -> str:
    law_id = (law_id or "").strip()
    if not _GESNR_RE.match(law_id):
        raise BadRequest(f"law id {law_id!r} is not a RIS Gesetzesnummer (8 digits, "
                         "e.g. 10001622 for the ABGB). Find it with search_legislation.")
    return law_id


def _law_hit(d: dict, with_provision: bool) -> LawHit:
    b = d["Metadaten"]["Bundesrecht"]
    k = b["BrKons"]
    title = _clean(b.get("Kurztitel"))
    if k.get("Abkuerzung"):
        title += f" ({_clean(k['Abkuerzung'])})"
    if with_provision and k.get("ArtikelParagraphAnlage") not in (None, "", "§ 0"):
        title += f" {_clean(k['ArtikelParagraphAnlage'])}"
    end = _iso(k.get("Ausserkrafttretensdatum"))
    return LawHit(id=k["Gesetzesnummer"], title=title, type=_clean(k.get("Typ")),
                  number=_clean(k.get("Kundmachungsorgan")), date=_iso(k.get("Inkrafttretensdatum")),
                  status=f"in force until {end}" if end else "in force",
                  snippet=_clean(b.get("Titel"))[:300],
                  url=k.get("GesamteRechtsvorschriftUrl") or d["Metadaten"]["Allgemein"]["DokumentUrl"])


# --------------------------------------------------------------------------- #
# Adapter
# --------------------------------------------------------------------------- #
class Austria(Jurisdiction):
    code = "at"
    name = "Austria"
    languages = ("de",)
    aliases = ("aut", "austria", "österreich", "oesterreich")
    sources = (
        Source(
            "RIS — Rechtsinformationssystem des Bundes (OGD API v2.6)",
            "https://data.bka.gv.at/ris/api/v2.6/",
            covers=("caselaw", "legislation"),
            licence="CC BY 4.0 (stated in the RIS OGD FAQ at data.bka.gv.at/ris/api/v2.6/)",
            commercial_use=True,
            ai_use=None,
            auth="none",
            rate_limit=("documented: max 0.5 req/s (2 s gap), no parallel connections; anything "
                        "beyond manual-scale use must be announced to ris.it@bka.gv.at and run "
                        "20:00–05:00 or weekends (RIS OGD FAQ, read 2026-11-05). Using 2 s spacing."),
            terms_url="https://data.bka.gv.at/ris/api/v2.6/",
        ),
    )
    caselaw_filters = {
        "court": "justiz (default: OGH, OLG, LG, BG), ogh, vfgh, vwgh, bvwg, lvwg, dsb",
        "doc_type": "text (default: full decisions), rechtssatz (headnotes), all",
        "date_from": "decision date from, YYYY-MM-DD (for rechtssatz: date of latest applying decision)",
        "date_to": "decision date to, YYYY-MM-DD",
    }
    legislation_filters = {
        "search_in": "title (default: one hit per law) or text (full text, one hit per §/article)",
        "type": "RIS type, e.g. BG (federal act), BVG (constitutional act), V (regulation)",
    }
    min_interval = {"data.bka.gv.at": 2.0, "ogd.ris.bka.gv.at": 2.0}
    notes = ("Federal consolidated law (current version) and decisions of OGH/ordinary courts, VfGH, "
             "VwGH, BVwG, LVwG and DSB. Law id = Gesetzesnummer (ABGB 10001622). Party names are "
             "anonymised. Decision ids: RIS document number or ECLI.")
    gaps = (
        "State law (Landesrecht): in the RIS OGD API (LrKons); source exists but not built yet",
        ("Whole-law text in one call: only on www.ris.bka.gv.at, which sits behind a bot check "
         "(per-paragraph text only)"),
        ("Historical versions of federal law: in the API (Fassung.FassungVom); not built yet, "
         "current version only"),
        ("Municipal and district law (Gemeinden, Bezirke endpoints): source exists but not built "
         "yet"),
        "Bundesfinanzgericht (BFG) decisions: not in the court filter",
    )
    samples = {
        "caselaw_query": "Mietzinsminderung",
        "decision_id": "JJT_20260325_OGH0002_0030OB00192_25V0000_000",
        "legislation_query": "Allgemeines bürgerliches Gesetzbuch",
        "law_id": "10001622",
        "provision": "§ 1090",
    }

    # ---- case law ---------------------------------------------------------- #
    async def search_caselaw(self, query, *, limit, page, filters):
        court = str(filters.get("court", "justiz")).strip().lower()
        if court not in _COURTS:
            raise BadRequest(f"court {court!r} unknown. Use one of: {', '.join(_COURTS)}.")
        doc_type = str(filters.get("doc_type", "text")).strip().lower()
        if doc_type not in _DOCTYPES:
            raise BadRequest(f"doc_type {doc_type!r} unknown. Use one of: {', '.join(_DOCTYPES)}.")
        app, extra = _COURTS[court]
        params = {"Applikation": app, **extra, **_DOCTYPES[doc_type]}
        if query:
            params["Suchworte"] = query
        for key, api in (("date_from", "EntscheidungsdatumVon"), ("date_to", "EntscheidungsdatumBis")):
            if filters.get(key):
                v = str(filters[key]).strip()
                if not _DATE_RE.match(v):
                    raise BadRequest(f"{key} must be YYYY-MM-DD, got {v!r}.")
                params[api] = v
        docs, total = await _paged("Judikatur", params, limit, page)
        dropped = 0
        past_end = page > 1 and not docs
        if doc_type != "text" and filters.get("date_from") and not past_end:
            # a Rechtssatz date is its index update date: do not list headnotes first decided earlier
            y = int(str(filters["date_from"]).strip()[:4])
            keep = [d for d in docs if not (m := re.search(
                r":(\d{4}):", d["Metadaten"].get("Judikatur", {}).get("EuropeanCaseLawIdentifier") or ""))
                or int(m.group(1)) >= y]
            dropped, docs = len(docs) - len(keep), keep
            # the source total counts the dropped headnotes; keep an exact count only when all fit one page
            total = len(docs) if total <= limit and page == 1 else None
        note = ("" if court != "justiz" else
                "Searches ordinary courts only; use filters={'court': 'vfgh'|'vwgh'|...} for others.")
        if doc_type != "text":
            note += (" Rechtssatz (headnote) dates, and date_from/date_to on them, refer to the most "
                     "recent decision that applied the headnote, not the original decision; the "
                     "year of the original decision is in its ECLI (shown as 'first decided'). The source "
                     "cannot filter headnotes by original decision date.")
            if dropped:
                note += (f" {dropped} headnote(s) on this page first decided before the date_from "
                         "year were left out, so the source's total (which counts them) is not shown.")
                if not docs:
                    note += (" For decisions (not headnotes) decided since that date, use "
                             "filters={'doc_type': 'text', 'date_from': ...}, which filters on the "
                             "real decision date.")
        if past_end:
            note += (" This page is past the last page: the source answers HTTP 500 for a page beyond "
                     "the results, and the total shown is the source's own count.")
        return Results([_decision_hit(d) for d in docs], total=total, note=note.strip())

    async def get_decision(self, id):
        ref = (id or "").strip()
        if _ECLI_RE.match(ref):
            doc_id = await _resolve_ecli(ref)
        else:
            doc_id = ref
        m = _DOCID_RE.match(doc_id)
        if not m or m.group(1).upper() not in _PREFIX:
            raise BadRequest(f"{ref!r} is not a RIS decision number (e.g. "
                             "JJT_20260325_OGH0002_0030OB00192_25V0000_000) or an Austrian ECLI "
                             "(e.g. ECLI:AT:OGH0002:2026:0030OB00192.25V.0325.000).")
        app = _PREFIX[m.group(1).upper()]
        blocks = _html_blocks(await _content(app, doc_id))
        meta = {t: b for t, b in blocks if t in _META_BLOCKS}
        court = meta.get("Gericht", "")
        rs_no = meta.get("Rechtssatznummer", "")
        gz = meta.get("Geschäftszahl", "")
        short = _SHORT.get(app, court)
        if rs_no:
            title = f"{short} {rs_no} (Rechtssatz)"
        else:
            title = f"{short} {gz}".strip()
        summary = next((b for t, b in blocks if t == "Leitsatz"), "")
        text = "\n\n".join(f"## {t}\n\n{b}" if t else b for t, b in blocks
                           if t not in _META_BLOCKS and t != "Leitsatz" and b)
        extra = {"ECLI": meta.get("European Case Law Identifier", "")}
        if rs_no:
            extra["Geschäftszahlen"] = gz[:2000]
        date = _de_date(meta.get("Entscheidungsdatum", ""))
        if rs_no and date:
            extra["Index date"] = f"{date} (last update of the headnote, not the decision date)"
            date = ""
        return Decision(id=doc_id, title=title or doc_id, text=text, url=_doc_url(app, doc_id),
                        court=court, date=date,
                        case_number=rs_no or gz, summary=summary,
                        metadata={k: v for k, v in extra.items() if v})

    # ---- legislation ------------------------------------------------------- #
    async def search_legislation(self, query, *, limit, page, filters):
        search_in = str(filters.get("search_in", "title")).strip().lower()
        if search_in not in ("title", "text"):
            raise BadRequest("search_in must be 'title' or 'text'.")
        params = {"Applikation": "BrKons", "Fassung.FassungVom": _http.today()}
        if search_in == "title":
            params.update({"Titel": query, "Abschnitt.Von": "0", "Abschnitt.Bis": "0",
                           "Abschnitt.Typ": "Alle"})
        else:
            params["Suchworte"] = query
        if filters.get("type"):
            params["Typ"] = str(filters["type"]).strip()
        docs, total = await _paged("Bundesrecht", params, limit, page)
        note = "Federal law only (Bundesrecht konsolidiert), version in force today."
        words = (query or "").split()
        if search_in == "title" and not total and len(words) == 1:
            # title search matches whole words only (HinweisgeberInnenschutzgesetz is not found
            # as Hinweisgeberschutzgesetz): retry with a shorter word start
            for n in range(len(words[0]) - 4, 7, -4):
                stem = words[0][:n] + "*"
                docs, total = await _paged("Bundesrecht", {**params, "Titel": stem}, limit, page)
                if total:
                    note += (f" No law title contains the exact word {query!r}; showing titles "
                             f"starting {stem!r}.")
                    break
        return Results([_law_hit(d, with_provision=search_in == "text") for d in docs], total=total,
                       note=note)

    async def get_legislation_toc(self, id):
        law_id = _check_gesnr(id)
        if law_id in _toc_cache:
            return _toc_cache[law_id]
        params = {"Applikation": "BrKons", "Gesetzesnummer": law_id, "Fassung.FassungVom": _http.today()}
        docs, total = await _search("Bundesrecht", params, "OneHundred", 1)
        n = 1
        while len(docs) < total and n < 60:
            n += 1
            more, _ = await _search("Bundesrecht", params, "OneHundred", n)
            if not more:
                break
            docs += more
        if not docs:
            raise NotFound(f"no federal law with Gesetzesnummer {law_id} in force today")
        title = _clean(docs[0]["Metadaten"]["Bundesrecht"].get("Kurztitel"))
        entries, seen = [], set()
        for d in docs:
            label = _clean(_brkons(d).get("ArtikelParagraphAnlage"))
            if not label or label == "§ 0" or label in seen:
                continue
            seen.add(label)
            entries.append(TocEntry(title=label, level=0, provision=label))
        toc = Toc(id=law_id, title=title, entries=entries,
                  url=_brkons(docs[0]).get("GesamteRechtsvorschriftUrl")
                  or f"{OGD}/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer={law_id}")
        _toc_cache[law_id] = toc
        return toc

    async def get_legislation_provision(self, id, provision):
        law_id = _check_gesnr(id)
        comp = _COMPOUND_RE.match(re.sub(r"\s+", " ", (provision or "").strip()))
        if comp:  # e.g. DSG 'Art. 1 § 1': RIS indexes it as paragraph 1 within article 1
            typ, num = "Paragraph", comp.group(2).lower()
            want = f"art. {comp.group(1)} § {num}".lower()
        else:
            typ, num = _parse_label(provision)
            want = ""
        docs, _ = await _search("Bundesrecht", {
            "Applikation": "BrKons", "Gesetzesnummer": law_id, "Fassung.FassungVom": _http.today(),
            "Abschnitt.Von": num, "Abschnitt.Bis": num, "Abschnitt.Typ": typ}, "Ten", 1)
        order = {"Paragraph": 0, "Artikel": 1, "Anlage": 2}

        def rank(d):
            if want:
                lab = re.sub(r"\s+", " ", _clean(_brkons(d).get("ArtikelParagraphAnlage"))).lower()
                return (0, 0) if lab == want else (9, 9)
            try:
                t, n = _parse_label(_brkons(d).get("ArtikelParagraphAnlage", ""))
            except BadRequest:
                return (9, 9)
            return (0 if n.lower() == num.lower() else 1, order.get(t, 3))
        docs = [d for d in docs if rank(d)[0] == 0]
        if not docs:
            raise NotFound(f"{provision!r} not found in law {law_id} (version in force today). "
                           "See get_legislation_toc for the labels.")
        d = min(docs, key=rank)
        doc_id = d["Metadaten"]["Technisch"]["ID"]
        blocks = _html_blocks(await _content("Bundesnormen", doc_id))
        text = next((b for t, b in blocks if t == "Text"), "") or "\n\n".join(b for _, b in blocks)
        return Provision(law_id=law_id,
                         law_title=_clean(d["Metadaten"]["Bundesrecht"].get("Kurztitel")),
                         provision=_clean(_brkons(d).get("ArtikelParagraphAnlage")), text=text,
                         url=d["Metadaten"]["Allgemein"].get("DokumentUrl")
                         or f"{OGD}/Dokumente/Bundesnormen/{doc_id}/{doc_id}.html",
                         as_of=_http.today())
