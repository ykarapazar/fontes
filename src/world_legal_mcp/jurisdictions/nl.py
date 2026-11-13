"""Netherlands: case law from rechtspraak.nl, legislation from wetten.overheid.nl (BWB).

Ported from nl-legal-mcp. Gotchas this code encodes:
  * rechtspraak.nl blocks non-browser clients (302 -> mededeling.rechtspraak.nl);
    the shared HTTP layer sends a browser UA, and we detect the block anyway.
    /api/document also redirects to mededeling.rechtspraak.nl/404 for an unknown
    ECLI, so a mededeling redirect falls back to the official XML, whose 404 is
    the real "not found".
  * Full-text search exists only on the website backend uitspraken.rechtspraak.nl
    /api/zoek (the open-data API is metadata-only). It has no arbitrary date
    ranges, only four preset windows.
  * Decision fetch: /api/document (clean JSON), fallback to the official
    data.rechtspraak.nl/uitspraken/content XML.
  * Legislation search: KOOP SRU, version=1.2 (2.0 returns HTTP 406). CQL
    relation must be '=' (not '=='), index must be prefixed (overheidbwb.titel=).
    SRU returns one record per version, so numberOfRecords is not a law count.
  * BWB has no per-article endpoint: the whole consolidated "toestand" XML is
    fetched (via manifest.xml -> _latestItem), cached in-process, and sliced.
  * Burgerlijk Wetboek books are separate BWB-ids whose articles are numbered
    per book ("Artikel 2" in BWBR0005289); they are cited "6:2", so that is the
    label we show and accept (plain "2" works too).
"""
from __future__ import annotations

import html as _html
import re
from typing import Any
from urllib.parse import unquote

from lxml import etree
from markdownify import markdownify as _md

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

ZOEK_URL = "https://uitspraken.rechtspraak.nl/api/zoek"
DOC_URL = "https://uitspraken.rechtspraak.nl/api/document/"
DETAILS_URL = "https://uitspraken.rechtspraak.nl/details?id="
OFFICIAL_CONTENT = "https://data.rechtspraak.nl/uitspraken/content"
SRU_URL = "https://zoekservice.overheid.nl/sru/Search"
REPO = "https://repository.officiele-overheidspublicaties.nl/bwb"
WETTEN = "https://wetten.overheid.nl/"

_REFERER = {"Referer": "https://uitspraken.rechtspraak.nl/"}
_BLOCK_HOST = "mededeling.rechtspraak.nl"

# /api/zoek SearchTerms[].Field accepted values (UI label -> API value)
_FIELDS = {
    "alle": "AlleVelden",
    "tekst": "Hoofdtekst",
    "samenvatting": "Samenvatting",
    "ecli": "Uitspraaknummer",
    "zaaknummer": "Zaaknummer",
    "vindplaats": "Vindplaats",
}
_DATE_SORTS = ("uitspraak", "uitspraak_asc", "publicatie")
_SORTS = {
    "relevantie": "Relevance",
    "publicatie": "PublicatieDatumDesc",
    "uitspraak": "UitspraakDatumDesc",
    "uitspraak_asc": "UitspraakDatumAsc",
}
# /api/zoek only supports preset uitspraakdatum buckets (no arbitrary range)
_PERIODS = {
    "week": "BinnenEenWeek",
    "maand": "BinnenEenMaand",
    "dit_jaar": "DitJaar",
    "vorig_jaar": "VorigJaar",
}

# /api/zoek Instanties[] (NodeType 1 = instantie type), Rechtsgebieden[] (NodeType 3),
# Contentsoorten[] (NodeType 7)
_COURTS = {
    "hoge_raad": "Spirit.Npi.Ecli.Domain.TypeHr",
    "gerechtshof": "Spirit.Npi.Ecli.Domain.Gerechtshof",
    "rechtbank": "Spirit.Npi.Ecli.Domain.Rechtbank",
    "raad_van_state": "Spirit.Npi.Ecli.Domain.TypeRvS",
    "crvb": "Spirit.Npi.Ecli.Domain.TypeCRvB",
    "cbb": "Spirit.Npi.Ecli.Domain.TypeCBb",
}
_RG = "http://psi.rechtspraak.nl/rechtsgebied#"
_AREAS = {
    "civiel": _RG + "civielRecht",
    "arbeidsrecht": _RG + "civielRecht_arbeidsrecht",
    "ondernemingsrecht": _RG + "civielRecht_ondernemingsrecht",
    "insolventierecht": _RG + "civielRecht_insolventierecht",
    "straf": _RG + "strafrecht",
    "bestuur": _RG + "bestuursrecht",
    "vreemdelingenrecht": _RG + "bestuursrecht_vreemdelingenrecht",
    "belastingrecht": _RG + "bestuursrecht_belastingrecht",
    "socialezekerheid": _RG + "bestuursrecht_socialezekerheidsrecht",
}
_KINDS = {"uitspraak": "uitspraak", "conclusie": "conclusie"}

_ECLI_RE = re.compile(r"^ECLI:[A-Z]{2}:[A-Z0-9]+:\d{4}:[A-Z0-9.]+$", re.I)
_URL_ECLI_RE = re.compile(
    r"^https?://(?:deeplink|uitspraken)\.rechtspraak\.nl/\S*?[?&]id="
    r"(ECLI(?::|%3A)[A-Z]{2}(?::|%3A)[A-Z0-9]+(?::|%3A)\d{4}(?::|%3A)[A-Z0-9.]+)(?=$|[&#\s])", re.I)
_BWBID_RE = re.compile(r"^BWB[RV]\d+$", re.I)
_TAG_RE = re.compile(r"<[^>]+>")
_DMY_RE = re.compile(r"^(\d{2})-(\d{2})-(\d{4})$")
_BW_BOOK_RE = re.compile(r"^Burgerlijk Wetboek Boek (\w+)$", re.I)

_NS = {
    "srw": "http://www.loc.gov/zing/srw/",
    "dcterms": "http://purl.org/dc/terms/",
    "overheid": "http://standaarden.overheid.nl/owms/terms/",
    "bwb": "http://standaarden.overheid.nl/bwb/terms/",
}
_STRUCT = ("boek", "hoofdstuk", "titeldeel", "afdeling", "paragraaf")

# Per-process cache of fetched toestand XML (keyed by URL) — laws are large.
_toestand_cache: dict[str, bytes] = {}


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #
def _clean_md(s: str) -> str:
    """Collapse runs of spaces and blank lines; keep paragraph breaks."""
    s = re.sub(r"[ \t ]+", " ", s or "")
    s = re.sub(r" *\n *", "\n", s)
    return re.sub(r"\n{3,}", "\n\n", s).strip()


def _html_to_md(html: str) -> str:
    if not html:
        return ""
    return _clean_md(_md(html, strip=["a", "img"], heading_style="ATX"))


def _strip_tags(s: str) -> str:
    return re.sub(r"\s+", " ", _html.unescape(_TAG_RE.sub("", s or ""))).strip()


def _field(v) -> str:
    """Render a scalar-or-list JSON field as one clean, tag-free string."""
    if isinstance(v, list):
        return "; ".join(_names(v))
    return _strip_tags(str(v)) if v not in (None, "") else ""


def _date(v) -> str:
    """ISO date from '2024-05-08T00:00:00' or '08-05-2024'; '' otherwise."""
    s = _field(v)
    if re.match(r"\d{4}-\d{2}-\d{2}", s):
        return s[:10]
    m = _DMY_RE.match(s)
    return f"{m[3]}-{m[2]}-{m[1]}" if m else ""


def _names(items, keys=("Naam", "Tekst", "Label", "Vindplaats", "Identifier")) -> list[str]:
    """Flatten a rechtspraak JSON list (of dicts or strings) into clean labels."""
    out = []
    for it in items or []:
        if isinstance(it, dict):
            val = next((it[k] for k in keys if it.get(k)), "")
        else:
            val = str(it)
        val = _strip_tags(val)
        if val:
            out.append(val)
    return out


def _as_bool(v: Any) -> bool:
    if isinstance(v, str):
        return v.strip().lower() not in ("false", "0", "no", "nee", "")
    return bool(v)


def _pick(table: dict[str, str], name: str, value: Any) -> str:
    val = table.get(str(value).strip().lower())
    if not val:
        raise BadRequest(f"invalid {name} {value!r}; choose from: {', '.join(table)}")
    return val


def _blocked(r) -> bool:
    return _BLOCK_HOST in str(r.url)


def _title(court: str, case_number: str, fallback: str) -> str:
    """Dutch decisions have no case names: '<court> <zaaknummer>'."""
    return " ".join(x for x in (court, case_number) if x) or fallback


# --------------------------------------------------------------------------- #
# Case law: search  ->  /api/zoek
# --------------------------------------------------------------------------- #
def _parse_zoek_titel(titel: str) -> tuple[str, str]:
    """'Rechtbank Midden-Nederland, 08-05-2024, 10832191 \\ UC EXPL 23-8359' -> (court, zaaknr)."""
    parts = [p.strip() for p in _strip_tags(titel).split(", ", 2)]
    if len(parts) >= 2 and _DMY_RE.match(parts[1]):
        return parts[0], parts[2] if len(parts) > 2 else ""
    return (parts[0] if parts else ""), ""


async def _search_caselaw(query: str, *, field: str, sort: str, limit: int,
                          start: int, period: str | None, court: str | None = None,
                          area: str | None = None, kind: str | None = None,
                          loose: bool = False, phrase_tried: bool = False) -> Results:
    field_val = _pick(_FIELDS, "field", field)
    sort_val = _pick(_SORTS, "sort", sort)
    # Plain multi-word queries are matched loosely by the source (partial-word hits rank
    # high), so require every word unless the user used quotes/operators.
    strict = (not loose and field_val != "Uitspraaknummer" and len(query.split()) > 1
              and '"' not in query and not re.search(r"\b(AND|OR|NOT)\b|[()]", query))
    asked, court_filter = query, court
    if strict:
        query = " AND ".join(query.split())
    datum_uitspraak: list = []
    if period:
        datum_uitspraak = [{"NodeType": 5, "Identifier": _pick(_PERIODS, "period", period),
                            "level": 0}]

    body = {
        "StartRow": start,
        "PageSize": limit,
        "ShouldReturnHighlights": True,
        "ShouldCountFacets": False,
        "SortOrder": sort_val,
        "SearchTerms": [{"Term": query, "Field": field_val}] if query else [],
        "Contentsoorten": [{"NodeType": 7, "Identifier": _pick(_KINDS, "type", kind), "level": 0}]
        if kind else [],
        "Rechtsgebieden": [{"NodeType": 3, "Identifier": _pick(_AREAS, "area", area), "level": 1}]
        if area else [],
        "Instanties": [{"NodeType": 1, "Identifier": _pick(_COURTS, "court", court), "level": 0}]
        if court else [],
        "DatumPublicatie": [],
        "DatumUitspraak": datum_uitspraak,
        "Advanced": {"PublicatieStatus": "AlleenGepubliceerd"},
        "CorrelationId": "00000000-0000-0000-0000-000000000000",
        "Proceduresoorten": [],
    }
    r = await _http.post(
        ZOEK_URL,
        json=body,
        headers={**_REFERER, "Content-Type": "application/json",
                 "Accept": "application/json, text/plain, */*",
                 "Origin": "https://uitspraken.rechtspraak.nl"},
    )
    if _blocked(r):
        raise SourceError("rechtspraak.nl blocked the search (redirect to mededeling page); "
                          "try again in a moment", r.status_code)
    if r.status_code != 200:
        raise SourceError("rechtspraak.nl search failed", r.status_code)
    try:
        data = r.json()
    except ValueError:
        raise SourceError("rechtspraak.nl search returned non-JSON", r.status_code)

    hits = []
    for res in (data.get("Results") or [])[:limit]:
        ecli = _strip_tags(res.get("TitelEmphasis", ""))
        if not ecli:
            continue
        court, zaaknr = _parse_zoek_titel(res.get("Titel", ""))
        hits.append(DecisionHit(
            id=ecli,
            title=_title(court, zaaknr, ecli),
            court=court,
            date=_date(res.get("Uitspraakdatum")),
            case_number=zaaknr,
            snippet=_strip_tags(res.get("Tekstfragment") or ""),
            url=res.get("DeeplinkUrl") or DETAILS_URL + ecli,
        ))
    if strict and sort in _DATE_SORTS and start == 0 and not phrase_tried:
        # Date order ignores relevance, so AND-matching ranks off-topic decisions first.
        # Try the exact phrase first; keep it only if it finds something.
        # Prefer decisions whose summary (inhoudsindicatie) has the phrase: they are about it,
        # while a full-text phrase also hits decisions that only mention it in passing.
        r3 = None
        for fld in (("samenvatting", field) if field == "alle" else (field,)):
            r3 = await _search_caselaw('"' + asked + '"', field=fld, sort=sort, limit=limit,
                                       start=start, period=period, court=court_filter,
                                       area=area, kind=kind, loose=True, phrase_tried=True)
            if r3.items:
                break
        if r3.items:
            where = "in their summary " if fld == "samenvatting" and field == "alle" else ""
            r3.note = (f'Showing decisions containing the exact phrase "{asked}" {where}'
                       "(narrow, so it can miss decisions worded differently, e.g. 'ontslag op "
                       "staande voet'), newest first. "
                       "To match the words anywhere in the text, add AND between them. "
                       + (r3.note or ""))
            return r3
    if strict and not hits and start == 0:
        r2 = await _search_caselaw(asked, field=field, sort=sort,
                                   limit=limit, start=start, period=period, court=court_filter,
                                   area=area, kind=kind, loose=True)
        r2.note = ("No decision contains all the words, so this is a loose match (some words "
                   "may be missing). " + (r2.note or ""))
        return r2
    notes = []
    if strict:
        notes.append("All words are required (AND). Use OR between words to widen, or "
                     '"quotes" for an exact phrase.')
    elif (field_val != "Uitspraaknummer" and len(query.split()) > 1 and '"' not in query
            and " AND " not in query):
        notes.append('Rechtspraak matches loosely (decisions with only some of the words can '
                     'rank). Use "quotes" for an exact phrase or AND between words to require '
                     "all of them.")
    if not court_filter and re.search(r"\b(hoge raad|gerechtshof|rechtbank|raad van state|centrale raad)\b",
                               asked, re.I):
        notes.append("A court name in the query is only searched as text, not as a filter. To "
                     'restrict to a court use filters {"court": "hoge_raad"} (also gerechtshof, '
                     "rechtbank, raad_van_state, crvb, cbb), plus {\"type\": \"uitspraak\"} to "
                     "leave out advocate-general conclusies.")
    if sort in _DATE_SORTS and query:
        notes.append("Sorted by date, not relevance, so off-topic decisions that merely contain "
                     'the words can rank first. Add filters {"area": "arbeidsrecht"} (or another '
                     "area) to narrow to the field, or drop the sort for relevance order.")
    if any(re.match(r"ECLI:NL:OG", h.id, re.I) for h in hits):
        notes.append("Some hits are from Kingdom courts outside the Netherlands proper (ECLI:NL:OGEAA "
                     "= Aruba, OGEAC = Curacao, OGEAM = Sint Maarten, OGEABES = Bonaire/Sint "
                     "Eustatius/Saba, OGHACMB = Joint Court of Justice). Their law is not Dutch "
                     "law; check the Court line before citing.")
    return Results(hits, total=data.get("ResultCount"), note=" ".join(notes))


# --------------------------------------------------------------------------- #
# Case law: one decision  ->  /api/document  (fallback: official XML)
# --------------------------------------------------------------------------- #
async def _get_document(ecli: str) -> Decision:
    raw = ecli.strip()
    m = _URL_ECLI_RE.match(raw)
    ecli = unquote(m.group(1) if m else raw).upper()
    if not _ECLI_RE.match(ecli):
        raise BadRequest(f"invalid ECLI {raw!r}; expected e.g. ECLI:NL:HR:2019:1734")
    r = await _http.get(DOC_URL, params={"id": ecli}, headers=_REFERER)
    # A mededeling redirect is either a block or "unknown ECLI": the official XML decides.
    if r.status_code == 200 and not _blocked(r):
        try:
            return _json_document(r.json())
        except (ValueError, KeyError):
            pass  # fall through to official XML
    return await _get_document_official(ecli)


def _json_document(d: dict) -> Decision:
    ecli = d["Identifier"]
    court = _field(d.get("InstantieNaam"))
    zaaknr = _field(d.get("Zaaknummer"))
    meta = {
        "Citation": _field(d.get("CitaatText")),
        "Zittingsplaats": _field(d.get("ZittingsplaatsNaam")),
        "Datum publicatie": _date(d.get("DatumPublicatie")),
        "Type": _field(d.get("Type")),
        "Rechtsgebieden": "; ".join(_names(d.get("Rechtsgebieden"))),
        "Procedure": "; ".join(_names(d.get("ProcedureSoorten"))),
        "Rechter(s)": _field(d.get("RechterLabel")) or "; ".join(_names(d.get("Rechter"))),
        "Formele relaties": "; ".join(_names(d.get("FormeleRelatie"),
                                             keys=("Tekst", "Label", "Identifier"))),
        "Wetsverwijzingen": "; ".join(_names(d.get("WetsverwijzingLinks"),
                                             keys=("Tekst", "Titel", "Label"))),
        "Vindplaatsen": "; ".join(_names(d.get("Vindplaatsen"), keys=("Vindplaats",))),
        "Status": "Ingetrokken/vervallen (withdrawn)" if d.get("Ingetrokken") else "",
    }
    return Decision(
        id=ecli,
        title=_title(court, zaaknr, ecli),
        text=_html_to_md(d.get("UitspraakTekst", "")),
        url=d.get("DeepLink") or DETAILS_URL + ecli,
        court=court,
        date=_date(d.get("DatumUitspraak")),
        case_number=zaaknr,
        summary=_html_to_md(d.get("InhoudsindicatieTekst", "")),
        metadata={k: v for k, v in meta.items() if v and v.lower() != "none"},
    )


async def _get_document_official(ecli: str) -> Decision:
    r = await _http.get(OFFICIAL_CONTENT, params={"id": ecli})
    if r.status_code == 404:
        raise NotFound(f"no decision {ecli} at rechtspraak.nl")
    if r.status_code != 200 or not r.content:
        raise SourceError(f"data.rechtspraak.nl could not return {ecli}", r.status_code)
    try:
        root = etree.fromstring(r.content)
    except etree.XMLSyntaxError:
        raise SourceError(f"data.rechtspraak.nl returned invalid XML for {ecli}", r.status_code)

    def first(local: str) -> str:
        els = root.xpath(f"//*[local-name()='{local}']")
        return els[0].text.strip() if els and els[0].text else ""

    def section(local: str) -> str:
        els = root.xpath(f"//*[local-name()='{local}']")
        return _node_text(els[0]) if els else ""

    court, zaaknr = first("creator"), first("zaaknummer")
    meta = {"Datum publicatie": _date(first("issued")), "Rechtsgebied": first("subject"),
            "Procedure": first("procedure")}
    return Decision(
        id=ecli,
        title=_title(court, zaaknr, ecli),
        text=section("uitspraak"),
        url=DETAILS_URL + ecli,
        court=court,
        date=_date(first("date")),
        case_number=zaaknr,
        summary=section("inhoudsindicatie"),
        metadata={k: v for k, v in meta.items() if v},
    )


def _node_text(el) -> str:
    """Flatten DocBook-ish rechtspraak XML into readable text with paragraph breaks."""
    blocks: list[str] = []
    for node in el.iter():
        if not isinstance(node.tag, str):  # skip comments / processing instructions
            continue
        tag = etree.QName(node).localname
        if tag in ("para", "title", "bridgehead", "nr", "section.title"):
            txt = re.sub(r"\s+", " ", " ".join(node.itertext()).strip())
            if txt:
                blocks.append(f"**{txt}**" if tag in ("title", "bridgehead") else txt)
    # de-duplicate consecutive identical lines that come from nested iter()
    out, prev = [], None
    for b in blocks:
        if b != prev:
            out.append(b)
        prev = b
    return "\n\n".join(out)


# --------------------------------------------------------------------------- #
# Legislation: search  ->  SRU (version 1.2)
# --------------------------------------------------------------------------- #
def _build_cql(query: str, current_only: bool) -> str:
    q = query.strip()
    if _BWBID_RE.match(q):
        cql = f"dcterms.identifier={q.upper()}"
    else:
        words = [w for w in re.split(r"\s+", q) if w]
        cql = " and ".join(f"overheidbwb.titel={w}" for w in words) or f"overheidbwb.titel={q}"
    if current_only:
        cql += f" and overheidbwb.geldigheidsdatum={_http.today()}"
    return cql


async def _search_wetten(query: str, *, current_only: bool, limit: int, page: int,
                         _asked: str | None = None) -> Results:
    cql = _build_cql(query, current_only)
    # SRU returns one record per version; fetch the max and dedupe by BWB-id, rank, then
    # slice the requested page. The SRU caps a request at 100 records.
    want = page * limit
    r = await _http.get(SRU_URL, params={
        "x-connection": "BWB",
        "operation": "searchRetrieve",
        "version": "1.2",
        "query": cql,
        "maximumRecords": "100",
        "startRecord": "1",
    })
    if r.status_code != 200:
        raise SourceError(f"wetten.overheid.nl SRU search failed (CQL: {cql})", r.status_code)
    try:
        root = etree.fromstring(r.content)
    except etree.XMLSyntaxError:
        raise SourceError("wetten.overheid.nl SRU returned invalid XML", r.status_code)
    diag = root.xpath("//*[local-name()='diagnostic']/*[local-name()='message']")
    if diag:
        raise SourceError(f"wetten.overheid.nl SRU: {diag[0].text} (CQL: {cql})", r.status_code)

    today = _http.today()
    seen: dict[str, LawHit] = {}
    for rec in root.findall(".//srw:records/srw:record", _NS):
        bwb = rec.findtext(".//dcterms:identifier", namespaces=_NS)
        if not bwb or bwb in seen:
            continue
        eind = rec.findtext(".//bwb:geldigheidsperiode_einddatum", namespaces=_NS) or ""
        in_force = eind in ("", "9999-12-31") or eind >= today
        rg = [e.text for e in rec.findall(".//bwb:rechtsgebied", _NS) if e.text]
        authority = rec.findtext(".//overheid:authority", namespaces=_NS) or ""
        snippet = "; ".join(x for x in (f"Rechtsgebied: {', '.join(rg)}" if rg else "",
                                        f"Bevoegd gezag: {authority}" if authority else "") if x)
        seen[bwb] = LawHit(
            id=bwb,
            title=_strip_tags(rec.findtext(".//dcterms:title", namespaces=_NS) or bwb),
            type=rec.findtext(".//dcterms:type", namespaces=_NS) or "",
            status="in force" if in_force else f"expired {eind}",
            snippet=snippet,
            url=WETTEN + bwb,
        )
    # SRU order is arbitrary: put exact-title matches first, then titles that start with
    # the query, then the rest (stable, so SRU order is kept within each group).
    qn = " ".join(query.lower().split())
    ranked = sorted(seen.values(), key=lambda h: 0 if h.title.lower() == qn
                    else 1 if h.title.lower().startswith(qn) else 2)
    hits = ranked[(page - 1) * limit:want]
    words = query.split()
    if not hits and page == 1 and len(words) > 1:
        # Topic words (e.g. 'arbeidsovereenkomst') are not in titles: drop trailing words.
        r2 = await _search_wetten(" ".join(words[:-1]), current_only=current_only,
                                  limit=limit, page=page, _asked=_asked or query)
        if r2.items:
            r2.note = (f"No law title contains all of '{_asked or query}'; showing titles matching "
                       f"'{' '.join(words[:-1])}' instead. " + (r2.note or ""))
        elif not _asked:
            r2.note = ("Matches title words only: every word must appear in the law's title, so "
                       "topic words (e.g. 'arbeidsovereenkomst') find nothing. Search the law's "
                       "title, e.g. 'Burgerlijk Wetboek Boek 7'.")
        return r2
    note = "Matches title words only."
    if current_only:
        note += ' Only law in force today; pass filters={"current_only": false} for repealed law.'
    return Results(hits, total=None, note=note)


# --------------------------------------------------------------------------- #
# Legislation: toestand (consolidated current text) fetch + parse
# --------------------------------------------------------------------------- #
class _Law:
    """A parsed toestand: root element, id, title, version date, BW book (if any)."""

    def __init__(self, bwb: str, root):
        self.id = bwb
        self.root = root
        self.title = (root.findtext(".//citeertitel") or root.findtext(".//intitule")
                      or bwb).strip()
        self.as_of = root.get("inwerkingtreding", "")
        m = _BW_BOOK_RE.match(self.title)
        self.book = m[1] if m else ""
        self.url = WETTEN + bwb

    def _nr(self, art) -> str:
        nr = (art.findtext("./kop/nr") or "").strip()
        if not nr:
            nr = re.sub(r"^artikel\s*", "", (art.get("label") or "").strip(), flags=re.I)
        if nr and self.book and ":" not in nr:
            return f"{self.book}:{nr}"
        return nr

    def label(self, art) -> str:
        """Provision label shown in the TOC: '2', '7a', '6:2' for BW books, or the
        article title for unnumbered ones (Grondwet 'Algemene bepaling')."""
        return self._nr(art) or (art.findtext("./kop/titel") or "").strip()

    def heading(self, art) -> str:
        nr = self._nr(art)
        titel = (art.findtext("./kop/titel") or "").strip()
        return " — ".join(x for x in (f"Artikel {nr}" if nr else "Artikel", titel) if x)

    def article_url(self, art) -> str:
        path = art.get("bwb-ng-variabel-deel") or ""
        if path and self.as_of:
            return f"{self.url}/{self.as_of}/#{path.strip('/').replace('/', '_')}"
        return self.url


async def _fetch_toestand(bwb_id: str) -> _Law:
    bwb = bwb_id.strip().upper()
    if not _BWBID_RE.match(bwb):
        raise BadRequest(f"invalid BWB-id {bwb_id!r}; expected e.g. BWBR0005289")
    mr = await _http.get(f"{REPO}/{bwb}/manifest.xml")
    if mr.status_code == 404:
        raise NotFound(f"no law {bwb} in the BWB repository")
    if mr.status_code != 200:
        raise SourceError(f"BWB manifest for {bwb} unavailable", mr.status_code)
    manifest = etree.fromstring(mr.content)
    latest = manifest.get("_latestItem")
    if not latest:
        works = manifest.xpath("//*[@_latestItem]")
        latest = works[0].get("_latestItem") if works else None
    if not latest:
        raise SourceError(f"no current version in the BWB manifest of {bwb}")
    url = f"{REPO}/{bwb}/{latest}"
    data = _toestand_cache.get(url)
    if data is None:
        tr = await _http.get(url)
        if tr.status_code != 200:
            raise SourceError(f"BWB toestand XML for {bwb} unavailable", tr.status_code)
        data = tr.content
        if len(_toestand_cache) > 12:
            _toestand_cache.clear()
        _toestand_cache[url] = data
    return _Law(bwb, etree.fromstring(data))


def _heading(el) -> str:
    tag = etree.QName(el).localname
    label = el.findtext("./kop/label") or tag.capitalize()
    nr = el.findtext("./kop/nr") or ""
    titel = el.findtext("./kop/titel") or ""
    heading = " ".join(x for x in [label, nr] if x).strip()
    return heading + (f" — {titel.strip()}" if titel else "")


def _depth(el) -> int:
    return sum(1 for a in el.iterancestors() if a.tag in _STRUCT)


def _artikel_text(law: _Law, art) -> str:
    """Render one <artikel> to markdown (handles <lid>/<lidnr>/<al>)."""
    lines = [f"**{law.heading(art)}**", ""]
    leden = art.findall("./lid")
    if leden:
        for lid in leden:
            nr = (lid.findtext("./lidnr") or "").strip()
            txt = _als_text(lid)
            lines.append(f"{nr}. {txt}" if nr else txt)
            lines.append("")
    else:
        txt = _als_text(art)
        if txt:
            lines.append(txt)
    return "\n".join(lines).strip()


def _als_text(el) -> str:
    """Concatenate <al> paragraph text under an element, skipping meta-data."""
    out = []
    for al in el.iter("al"):
        if any(etree.QName(a).localname == "meta-data" for a in al.iterancestors()):
            continue
        t = re.sub(r"\s+", " ", " ".join(al.itertext()).strip())
        if t:
            out.append(t)
    return "\n\n".join(out)


def _toc(law: _Law) -> Toc:
    entries = []
    for el in law.root.iter():
        if el.tag in _STRUCT:
            entries.append(TocEntry(_heading(el), level=_depth(el)))
        elif el.tag == "artikel":
            entries.append(TocEntry(law.heading(el), level=_depth(el), provision=law.label(el)))
    return Toc(id=law.id, title=law.title, url=law.url, entries=entries)


def _norm_provision(s: str) -> str:
    """'Artikel 6:2 BW', 'art. 2', ' 7A ' -> '6:2', '2', '7a'."""
    s = re.sub(r"^(artikel|art\.?)\s*", "", s.strip(), flags=re.I)
    s = re.sub(r"\s*BW$", "", s, flags=re.I)
    return re.sub(r"\s+", "", s).lower()


def _find_artikel(law: _Law, provision: str):
    want = _norm_provision(provision)
    if not want:
        raise BadRequest("empty provision; pass an article number such as '2' or '6:2'")
    want_nr = want
    if law.book and want.startswith(f"{law.book.lower()}:"):
        want_nr = want.split(":", 1)[1]
    for art in law.root.iter("artikel"):
        nr = (art.findtext("./kop/nr") or "").strip().lower()
        path = (art.get("bwb-ng-variabel-deel") or "").lower()
        if (want == _norm_provision(law.label(art)) or want_nr == nr
                or path.endswith(f"/artikel{want_nr}")):
            return art
    raise NotFound(f"no article {provision!r} in {law.id}; get_legislation_toc lists the labels")


def _full_text(law: _Law) -> str:
    lines = []
    for el in law.root.iter():
        if el.tag in _STRUCT:
            lines.append(f"{'#' * min(6, 2 + _depth(el))} {_heading(el)}")
        elif el.tag == "artikel":
            lines.append(_artikel_text(law, el))
    return "\n\n".join(lines)


# --------------------------------------------------------------------------- #
# Adapter
# --------------------------------------------------------------------------- #
class Netherlands(Jurisdiction):
    code = "nl"
    name = "Netherlands"
    languages = ("nl",)
    sources = (
        Source(
            "rechtspraak.nl (case law)", "https://uitspraken.rechtspraak.nl",
            covers=("caselaw",),
            licence="Public Domain Mark 1.0 (data.overheid.nl dataset 'Uitspraken "
                    "rechtspraak.nl'); judgments carry no copyright (Auteurswet art. 11)",
            commercial_use=True,
            ai_use=True,   # robots.txt only disallows /api/pdfdownload; no AI/TDM opt-out found
            auth="none",
            rate_limit="documented: max 10 requests/s and no bulk download for the Open Data "
                       "webservice (rechtspraak.nl/uitspraken/open-data, checked 2026-11); "
                       "the /api/zoek + /api/document website backend has no stated limit: "
                       "1 s spacing used, no 429 seen (2026-11)",
            terms_url="https://www.rechtspraak.nl/uitspraken/open-data",
        ),
        Source(
            "wetten.overheid.nl / BWB (legislation)", "https://wetten.overheid.nl",
            covers=("legislation",),
            licence="CC0 1.0 (data.overheid.nl dataset 'Basis Wetten Bestand'); legislation "
                    "carries no copyright (Auteurswet art. 11)",
            commercial_use=True,
            # wetten.overheid.nl robots.txt disallows AI agents by name (GPTBot,
            # ChatGPT-User, ClaudeBot, Claude-Web, anthropic-ai, rag-kennisbank, ...).
            # The SRU host zoekservice.overheid.nl has robots 'Disallow: /' for all
            # agents, although overheid.nl/informatie-hergebruiken offers that SRU
            # API for reuse. The BWB repository host has no robots.txt.
            ai_use=False,
            auth="none",
            rate_limit="unknown; not documented for the SRU or the BWB repository: "
                       "1 s spacing used, no 429 seen (2026-11)",
            terms_url="https://data.overheid.nl/dataset/basis-wetten-bestand",
        ),
    )
    caselaw_filters = {
        "field": "where to search: " + "/".join(_FIELDS) + " (default alle)",
        "sort": "relevantie (default) / publicatie / uitspraak (newest decision) / uitspraak_asc",
        "court": "court level: " + "/".join(_COURTS) + " (hoge_raad includes advocate-general "
                 "conclusies unless type=uitspraak)",
        "area": "area of law: " + "/".join(_AREAS),
        "type": "uitspraak (judgments only) / conclusie (advocate-general opinions)",
        "period": "preset decision-date window: week / maand / dit_jaar / vorig_jaar "
                  "(arbitrary date ranges are not supported by the source)",
    }
    legislation_filters = {
        "current_only": "true (default) = only law in force today; false = include repealed/historical",
    }
    min_interval = {
        "uitspraken.rechtspraak.nl": 1.0,
        "data.rechtspraak.nl": 0.12,      # documented max 10 req/s
        "zoekservice.overheid.nl": 1.0,
        "repository.officiele-overheidspublicaties.nl": 1.0,
    }
    notes = ("Decision ids are ECLIs (ECLI:NL:HR:2024:123). Law ids are BWB-ids "
             "(BWBR0005289 = Burgerlijk Wetboek Boek 6; BW articles are labelled '6:2'). "
             "Search in Dutch; search_legislation matches title words only and looks at "
             "the first 100 SRU records.")
    gaps = (
        "Local and provincial regulations (CVDR / lokale regelgeving): not researched yet",
        "Staatsblad, Staatscourant and parliamentary papers: not researched yet",
        ("Treaties: not built as such; BWB search has no type filter, so treaty records (BWBV) "
         "can appear in results"),
        "Case-law search by arbitrary date range: the source offers only four preset windows",
    )
    samples = {
        "caselaw_query": "huurrecht ontbinding",
        "decision_id": "ECLI:NL:HR:2019:1734",
        "legislation_query": "grondwet",
        "law_id": "BWBR0005289",
        "provision": "6:2",
    }

    async def search_caselaw(self, query, *, limit, page, filters):
        return await _search_caselaw(
            query, field=str(filters.get("field", "alle")), sort=str(filters.get("sort", "relevantie")),
            limit=limit, start=(page - 1) * limit, period=filters.get("period"),
            court=filters.get("court"), area=filters.get("area"), kind=filters.get("type"),
        )

    async def get_decision(self, id):
        return await _get_document(id)

    async def search_legislation(self, query, *, limit, page, filters):
        return await _search_wetten(query, current_only=_as_bool(filters.get("current_only", True)),
                                    limit=limit, page=page)

    async def get_legislation_toc(self, id):
        return _toc(await _fetch_toestand(id))

    async def get_legislation_provision(self, id, provision):
        law = await _fetch_toestand(id)
        art = _find_artikel(law, provision)
        return Provision(law_id=law.id, law_title=law.title, provision=law.label(art),
                         text=_artikel_text(law, art), url=law.article_url(art), as_of=law.as_of)

    async def get_legislation_text(self, id):
        law = await _fetch_toestand(id)
        n = sum(1 for _ in law.root.iter("artikel"))
        return LawText(id=law.id, title=law.title, text=_full_text(law), url=law.url,
                       as_of=law.as_of, metadata={"Articles": str(n)})
