"""Suriname: case law from rechtspraak.sr (Hof van Justitie) and legislation from De Nationale
Assemblee (dna.sr). Dutch only.

Case law (rechtspraak.sr, WordPress, run for the Hof van Justitie):
  * About 1,400 anonymised decisions (2026-11): Hof van Justitie, the three kantongerechten,
    Krijgsraad, Rechter-Commissaris and the disciplinary boards (ATC, MTC, TCN). Oldest 1962;
    the database started in 2019, with a backlog from the Surinaams Juristenblad.
  * Search is the site's own form. Page 1 is POST /zoekresultaat, which carries the total
    ("Gevonden: N uitspraken"). Later pages come from the theme's load-more endpoint, which
    the site's own JavaScript calls. Hits come 10 per source page, and the site shows at most 500.
  * Id: the SRU number ("SRU-HvJ-2025-24"). Its lower-case form is the page slug, so the
    decision URL also works. The site says SRU numbers never change.

Legislation (www.dna.sr, the National Assembly):
  * Laws are listed by category (geldende teksten t/m 2005, wetten na 2005, wijzigingen na 2005,
    verdragen, begrotingen, naturalisatie), with one page per law and a text-layer PDF.
  * Id: "<category>/<slug>", e.g. "geldende-teksten-t-m-2005/grondwet-van-de-republiek-suriname".
    The law page URL also works. Search matches title words against the listing pages.
  * The PDFs are split on "Artikel N" headings. Footnote numbers are printed right after the
    article number, so "Artikel 12" in the text layer can be article 1 with footnote 2. The
    splitter resolves this from the running article and footnote counters.
  * Two dna.sr pages differ: the disclaimer allows copying "voor eigen gebruik" (own use), the
    auteursrechten page allows copying parts with a link to the source. Decision
    (2026-11-06): follow the auteursrechten page, so the source is on with an attribution warning.
"""
from __future__ import annotations

import calendar
import html as htmllib
import re

from lxml import html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from .._http import fold_combining as _fold
from ..models import Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc, TocEntry

RS_HOST = "rechtspraak.sr"
DNA_HOST = "www.dna.sr"
RS = f"https://{RS_HOST}"
DNA = f"https://{DNA_HOST}"
SEARCH = f"{RS}/zoekresultaat"
LOADMORE = f"{RS}/wp-content/themes/understrap/templates/loadmore_search_results.php"
LAWS = f"{DNA}/wetgeving/surinaamse-wetten"
MAX_PDF = 40_000_000
PER_PAGE = 10                       # source page size
MAX_SHOWN = 500                     # the site never shows more hits than this

_SRU = re.compile(r"^(?:https?://(?:www\.)?rechtspraak\.sr)?/?(sru-(?:[a-z0-9]{1,5}-)?\d{4}-\d{1,5})/?$", re.I)
_MONTHS = {m: i for i, m in enumerate(("januari", "februari", "maart", "april", "mei", "juni", "juli",
                                       "augustus", "september", "oktober", "november", "december"), 1)}
_COURTS = ("Hof van Justitie", "Kantongerecht Eerste Kanton", "Kantongerecht Tweede Kanton",
           "Kantongerecht Derde Kanton", "Rechter Commissaris in Strafzaken", "Krijgsraad",
           "Advocaten Tuchtcollege (ATC)", "Medisch Tuchtcollege (MTC)", "Tuchtcollege voor het Notariaat (TCN)")
_AREAS = ("Civiel recht", "Strafrecht", "Ambtenarenrecht", "Burger-overheid", "Tuchtrecht")
_SORTS = {"relevance": "relevance", "newest": "pronunciation_desc", "oldest": "pronunciation_asc",
          "published": "publish_desc"}
_CATS = {
    "geldende-teksten-t-m-2005": "Geldende teksten t/m 2005",
    "wetten-na-2005": "Wetten na 2005",
    "wijzigingen-na-2005": "Wijzigingen na 2005",
    "overeenkomsten-verdragen": "Overeenkomsten / verdragen",
    "begrotingen": "Begrotingen",
    "naturalisatie-wetten": "Naturalisatiewetten",
}
_LAW_ID = re.compile(r"^(?:https?://(?:www\.)?dna\.sr)?/?(?:wetgeving/surinaamse-wetten/)?"
                     r"([a-z0-9-]{3,60})/([a-z0-9][a-z0-9-]{1,250})/?$", re.I)

_lists: dict = {}
_laws: dict = {}


def _nl_date(s: str) -> str:
    m = re.match(r"^\s*(\d{1,2})\s+([a-z]+)\s+(\d{4})", (s or "").lower())
    if not m or m[2] not in _MONTHS:
        return ""
    return f"{m[3]}-{_MONTHS[m[2]]:02d}-{int(m[1]):02d}"


def _dash(s: str) -> str:
    return re.sub(r"[\u2010-\u2015\u2212]", "-", s)


def _check_filters(filters, allowed) -> dict:
    f = {k: v for k, v in dict(filters or {}).items() if v not in (None, "")}
    unknown = set(f) - set(allowed)
    if unknown:
        raise BadRequest(f"Unknown filter(s): {', '.join(sorted(unknown))}. Supported: {', '.join(allowed)}")
    return f


def _site_date(v, end: bool) -> str:
    """'2022', '2022-03' or '2022-03-16' -> the site's dd/mm/yyyy (first day, or last day when end)."""
    m = re.match(r"^\s*(\d{4})(?:-(\d{1,2})(?:-(\d{1,2}))?)?\s*$", str(v))
    if not m or (m[2] and not 1 <= int(m[2]) <= 12) or (m[3] and not 1 <= int(m[3]) <= 31):
        raise BadRequest(f"since/until must be YYYY, YYYY-MM or YYYY-MM-DD, got '{v}'.")
    y, mo, d = int(m[1]), int(m[2] or (12 if end else 1)), m[3]
    if not d:
        d = calendar.monthrange(y, mo)[1] if end else 1
    return f"{int(d):02d}/{mo:02d}/{y}"


def _pick(value, options, name: str) -> str:
    v = _fold(_http.clean(str(value)))
    for o in options:
        if _fold(o) == v or _fold(o).startswith(v):
            return o
    raise BadRequest(f"{name} must be one of: {'; '.join(options)}")


def _labels(node) -> dict[str, str]:
    out = {}
    for li in node.xpath('.//li[strong[contains(@class,"list-label")]]'):
        key = _http.clean(li.xpath('string(./strong)'))
        val = li.xpath('./span[contains(@class,"list-value")]')
        if key and val:
            out[key] = _http.clean(val[0].text_content())
    return out


def _hits(fragment: str) -> list[DecisionHit]:
    doc = lhtml.fromstring(f"<div>{fragment}</div>")
    items = []
    for h in doc.xpath('//h5[contains(@class,"sru-number")]'):
        a = h.xpath('./a[@href]')
        box = h.xpath('following-sibling::div[contains(@class,"sru-list")][1]')
        if not a or not box:
            continue
        sru = _dash(_http.clean(a[0].text_content()))
        f = _labels(box[0])
        court = f.get("Instantie", "")
        items.append(DecisionHit(id=sru, title=f"{court} {sru}".strip(), court=court,
                                 date=_nl_date(f.get("Uitspraakdatum", "")), case_number=f.get("Zaaknummer", ""),
                                 snippet=f.get("Inhoudsindicatie", "")[:400], url=a[0].get("href", "")))
    return items


async def _post(url: str, data: dict) -> str:
    r = await _http.post(url, data=data)
    if r.status_code != 200:
        raise SourceError(_http.error(RS_HOST, "search failed", r.status_code), r.status_code)
    return r.text


# --------------------------------------------------------------------------- #
# dna.sr legislation
# --------------------------------------------------------------------------- #
async def _listing(cat: str) -> list[tuple[str, str]]:
    """[(id, title)] for one category page, de-duplicated (a law can sit on several subject cards)."""
    if cat in _lists:
        return _lists[cat]
    r = await _http.get(f"{LAWS}/{cat}/")
    if r.status_code != 200:
        raise SourceError(_http.error(DNA_HOST, f"law list '{cat}' failed", r.status_code), r.status_code)
    out, seen = [], set()
    for href, title in re.findall(r'<a href="/wetgeving/surinaamse-wetten/([^"]+?)/?"\s+class="list-group-item[^"]*">'
                                  r'([^<]*)</a>', r.text):
        if href not in seen and href.count("/") == 1:
            seen.add(href)
            out.append((href, _http.clean(htmllib.unescape(title))))
    return _http.lru_put(_lists, cat, out, 8)


_HEAD = re.compile(r"^(?:Artikel|ARTIKEL)\s+(\d+)\s*([a-z]{0,2})(\d*)\s*$")
_PART = re.compile(r"^(?:(?:HOOFDSTUK|TITEL|AFDELING|BOEK|PARAGRAAF)\s+[IVXLC\d]+[A-Z]?\b"
                   r"|§\s*\d+[a-z]?\s*$"
                   r"|(?:EERSTE|TWEEDE|DERDE|VIERDE|VIJFDE|ZESDE|ZEVENDE|ACHTSTE|NEGENDE|TIENDE|ELFDE|TWAALFDE|DERTIENDE|VEERTIENDE|VIJFTIENDE|ZESTIENDE|ZEVENTIENDE|ACHTTIENDE|NEGENTIENDE|TWINTIGSTE)"
                   r"\s+(?:HOOFDSTUK|TITEL|AFDELING|BOEK|PARAGRAAF)(?![A-Za-z])).{0,80}$")


_OCR_HEAD = re.compile(r"^(Artikel|ARTIKEL)\s*([0-9IlSTO|]{1,4})$")
_OCR_DIGIT = str.maketrans("IlSTO|", "118701")


def _ocr_head(s: str) -> str:
    """Repair a heading from an OCR'd text layer ('Artikel I', 'Artikel l0', 'Artikel2' -> 'Artikel 1', ...).
    Only lines whose number is a mix of digits and look-alike letters change; 'II', 'III' stay roman."""
    m = _OCR_HEAD.match(s)
    if not m or re.fullmatch(r"I{2,}", m[2]):
        return s
    return f"{m[1]} {m[2].translate(_OCR_DIGIT)}"


_OCR_NOISE = re.compile(r"[a-z][*<>|^~\\]+[a-z]|[a-z]\d+[a-z]|\b[a-z]+[A-Z][a-z]*[A-Z]\w*|\b[a-z]+:[A-Za-z]+")
_OCR_WARN = ("Let op: de tekstlaag van deze PDF is slecht (OCR); er staan leesfouten in. "
             "Controleer de tekst aan de hand van de PDF op dna.sr.")


def _ocr_poor(text: str) -> bool:
    """True when the text layer shows OCR garbage (symbols or digits inside words) at a noticeable rate."""
    return len(_OCR_NOISE.findall(text)) >= 3 and len(_OCR_NOISE.findall(text)) * 5000 >= len(text)


def _resolve_head(d: str, letter: str, foot: str, last: int, last_fn: int):
    """(article, footnote) for a heading whose digits may carry a glued footnote number;
    the flag says numbering restarts at 1 (a second law in the same PDF)."""
    if letter:
        cands = [(int(d), int(foot) if foot else None)]
    else:
        cands = [(int(d[:k]), int(d[k:]) if d[k:] else None) for k in range(1, len(d) + 1)
                 if not d[k:].startswith("0")]

    def fn_ok(f):
        return f is None or last_fn < f <= last_fn + 60

    ok = [(n, f) for n, f in cands if fn_ok(f) and ((letter and last <= n <= last + 1)
                                                    or (not letter and last < n <= last + 150))]
    if ok:
        return min(ok, key=lambda c: (c[0] != last + 1, (c[1] - last_fn) if c[1] else 0, c[0] - last)), False
    rs = [(n, f) for n, f in cands if n == 1 and fn_ok(f) and not letter]
    return (rs[0], True) if rs else (None, False)


def _split(text: str) -> tuple[list[TocEntry], dict[str, str]]:
    lines = text.splitlines()
    heads: list[tuple[str, int]] = []
    parts: dict[int, str] = {}
    last = last_fn = last_par = 0
    seg = 1
    for i, ln in enumerate(lines):
        s = ln.strip()
        if _PART.match(s):
            nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
            title = f" – {nxt}" if nxt.isupper() and len(nxt) < 90 and not _HEAD.match(nxt) else ""
            pm = re.match(r"§\s*(\d+)([a-z]?)\s*$", s)
            if pm:      # '§ 115' may be '§ 1' with footnote 15 glued on: take the paragraph that follows the last one
                d, cands = pm[1], [(int(pm[1]), None)]
                if not pm[2]:
                    cands += [(int(d[:k]), int(d[k:])) for k in range(1, len(d)) if not d[k:].startswith("0")]
                ok = [c for c in cands if c[0] == last_par + 1 and (c[1] is None or last_fn < c[1] <= last_fn + 60)]
                n = (ok or cands[:1])[0][0]
                last_par = n
                parts[i] = _http.clean(f"§ {n}{pm[2]}" + title)
                continue
            last_par = 0
            parts[i] = _http.clean(re.sub(r"(AFDELING|HOOFDSTUK|TITEL|BOEK|PARAGRAAF)\d+", r"\1", s) + title)  # drop glued footnote no.
            continue
        m = _HEAD.match(_ocr_head(s))
        if not m:
            continue
        r, restart = _resolve_head(m[1], m[2], m[3], last, last_fn)
        if r is None:
            continue
        n, f = r
        if restart:
            seg += 1
        label = f"{n}{m[2]}" + (f"-{seg}" if seg > 1 else "")
        heads.append((label, i))
        last = n
        if f:
            last_fn = f
    sections: dict[str, str] = {}
    toc: list[TocEntry] = []
    pi = sorted(parts)
    prev = -1
    for k, (label, i) in enumerate(heads):
        end = heads[k + 1][1] if k + 1 < len(heads) else len(lines)
        end = next((p for p in pi if i < p < end), end)      # stop at the next chapter heading
        for p in pi:
            if prev < p < i:
                toc.append(TocEntry(title=parts[p], level=0))
        prev = i
        body = "\n".join(lines[i + 1:end]).strip()
        if label not in sections:
            sections[label] = f"Artikel {label.split('-')[0]}\n{body}".strip()
            toc.append(TocEntry(title=f"Artikel {label}", level=1, provision=label))
    return toc, sections


def _norm_prov(p: str) -> str:
    s = _http.clean(p).lower()
    s = re.sub(r"^(artikel|art\.?|article)\s*", "", s).strip().rstrip(".")
    m = re.match(r"^(\d+\s*[a-z]{0,2})(-\d+)?$", s)
    if not m:
        return s
    d = re.match(r"^(\d+)\s*(.*)$", m[1])
    return (d[1].lstrip("0") or "0") + d[2] + (m[2] or "")


async def _law(id: str) -> dict:
    m = _LAW_ID.match(_http.clean(id))
    if not m or m[1].lower() not in _CATS:
        raise BadRequest("Use a law id from search_legislation: '<category>/<slug>', e.g. "
                         "'geldende-teksten-t-m-2005/grondwet-van-de-republiek-suriname', or the dna.sr law page URL.")
    lid = f"{m[1].lower()}/{m[2].lower()}"
    if lid in _laws:
        return _laws[lid]
    page_url = f"{LAWS}/{lid}/"
    r = await _http.get(page_url)
    if r.status_code == 404:
        raise NotFound(f"No law '{lid}' on dna.sr. Use search_legislation.")
    if r.status_code != 200:
        raise SourceError(_http.error(DNA_HOST, f"law page failed: {page_url}", r.status_code), r.status_code)
    doc = lhtml.fromstring(r.text)
    title = _http.clean(doc.xpath('string(//h1)'))
    lead = _http.clean(doc.xpath('string(//div[contains(@class,"lead")])'))
    subject = _http.clean(doc.xpath('string(//span[@title="onderwerp"])'))
    pdfs = [h for h in doc.xpath('//a/@href') if re.match(r"^/media/[a-z0-9]+/[^\"]+\.pdf$", h, re.I)]
    if not pdfs:
        raise NotFound(f"{title or lid}: dna.sr has no PDF for this law; see {page_url}")
    pdf = DNA + pdfs[0]
    h = await _http.request("HEAD", pdf)
    if h.status_code != 200 or "pdf" not in h.headers.get("content-type", ""):
        raise SourceError(_http.error(DNA_HOST, f"PDF check failed: {pdf}", h.status_code), h.status_code)
    size = int(h.headers.get("content-length") or 0)
    if size > MAX_PDF:
        raise SourceError(f"Error ({DNA_HOST}): {pdf} is {size // 1_000_000} MB, over the "
                          f"{MAX_PDF // 1_000_000} MB limit; read it there.", "too-large")
    p = await _http.get(pdf)
    if p.status_code != 200 or not p.content.startswith(b"%PDF"):
        raise SourceError(_http.error(DNA_HOST, f"PDF failed: {pdf}", p.status_code), p.status_code)
    raw = _http.pdf_text(p.content)
    if len(raw) < 200:
        raise SourceError(f"Error ({DNA_HOST}): {pdf} has no text layer (scanned; no OCR here); read it there.",
                          "no-text")
    toc, sections = _split(raw)
    meta = {k: v for k, v in (("Categorie", _CATS[m[1].lower()]), ("Onderwerp", subject),
                              ("Omschrijving", lead), ("PDF", pdf)) if v}
    if _ocr_poor(raw):
        meta["Let op"] = _OCR_WARN
    law = {"id": lid, "title": title or lid, "url": page_url, "toc": toc, "sections": sections,
           "text": re.sub(r"\n{3,}", "\n\n", raw).strip(), "meta": meta}
    return _http.lru_put(_laws, lid, law, 8)


# --------------------------------------------------------------------------- #
class Suriname(Jurisdiction):
    code = "sr"
    name = "Suriname"
    languages = ("nl",)
    aliases = ("suriname", "sur")
    sources = (
        Source(
            name="Rechtspraak Suriname, Hof van Justitie (rechtspraak.sr)",
            url=f"{RS}/",
            covers=("caselaw",),
            licence=("no licence, terms or copyright notice on the site (checked 2026-11-06); decisions "
                     "are published anonymised under the court's Selectie- en anonimiseringsbesluit"),
            commercial_use=None,
            ai_use=None,    # robots.txt only disallows /wp-admin/; no AI/TDM clause
            auth="none",
            rate_limit="unknown; no Crawl-delay; 1 s spacing, no 429 in ~40 requests (2026-11)",
            terms_url=f"{RS}/",
        ),
        Source(
            name="Surinaamse wetten, De Nationale Assemblee (dna.sr)",
            url=f"{LAWS}/",
            covers=("legislation",),
            licence=("Auteursrechten page: 'Onder voorwaarde dat (een link naar) de bron wordt vermeld, mogen "
                     "onderdelen van de inhoud van dna.sr worden overgenomen.' The disclaimer bans commercial "
                     "use without written permission (checked 2026-11-06)"),
            commercial_use=False,
            ai_use=None,    # no robots.txt (404); no AI/TDM clause
            auth="none",
            rate_limit="unknown; no robots.txt, no Crawl-delay; 1 s spacing, no 429 in ~30 requests (2026-11)",
            terms_url=f"{DNA}/copyright/auteursrechten/",
            warning=("Cite De Nationale Assemblee (dna.sr) with a link when reusing text; commercial use needs "
                     "written permission from De Nationale Assemblee. 'Geldende teksten t/m "
                     "2005' are older consolidations and may not include later amendments."),
        ),
    )
    caselaw_filters = {
        "court": "Instantie: " + "; ".join(_COURTS),
        "area": "Rechtsgebied: " + "; ".join(_AREAS),
        "since": "decision date from: YYYY, YYYY-MM or YYYY-MM-DD",
        "until": "decision date up to and including: YYYY, YYYY-MM or YYYY-MM-DD",
        "sort": "relevance (default), newest, oldest (decision date) or published (publication date)",
    }
    legislation_filters = {
        "category": "dna.sr list: " + "; ".join(_CATS),
    }
    min_interval = {RS_HOST: 1.0, DNA_HOST: 1.0}
    notes = ("Dutch only. Case law: anonymised decisions of the Hof van Justitie, kantongerechten and "
             "disciplinary boards from rechtspraak.sr (about 1,400; full-text search, at most 500 hits "
             "shown). Legislation: laws published by the National Assembly (dna.sr) as PDFs. Title search "
             "only; 'geldende teksten t/m 2005' are pre-2005 consolidations, with later changes listed "
             "separately (mostly scanned PDFs that cannot be read here). dna.sr terms allow copying parts with a link to the source; commercial use "
             "needs written permission.")
    gaps = (
        ("Consolidated texts after 2005: 'geldende teksten t/m 2005' are older consolidations; "
         "later changes are separate laws"),
        ("Amendment laws ('wijzigingen na 2005', e.g. the 2022 Burgerlijk Wetboek amendment, the 2023 "
         "Grondwet amendment) and some other laws are scanned PDFs without a text layer: they cannot be read "
         "here; open the PDF on dna.sr (the error gives its link). Laws with a poor OCR text layer can lack "
         "some articles"),
        "Legislation full-text search: dna.sr is searched by title words only; not built yet",
        "Case law beyond 500 hits per search: rechtspraak.sr shows at most 500",
        ("Decisions outside the court's selection: not published online (selection and "
         "anonymisation decree)"),
        "Official gazette and subordinate regulations: not researched yet",
    )
    samples = {
        "caselaw_query": "kort geding",
        "decision_id": "SRU-HvJ-1991-6",
        "legislation_query": "Grondwet",
        "law_id": "geldende-teksten-t-m-2005/grondwet-van-de-republiek-suriname",
        "provision": "10",
    }

    # ------------------------------------------------------------------ #
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        f = _check_filters(filters, self.caselaw_filters)
        q = _http.clean(query or "")
        if not q:
            raise BadRequest("Give search words or an SRU number (e.g. 'kort geding', 'SRU-HvJ-2025-24').")
        court = _pick(f["court"], _COURTS, "court") if f.get("court") else "all"
        area = _pick(f["area"], _AREAS, "area") if f.get("area") else "all"
        sort = str(f.get("sort", "relevance")).lower()
        if sort not in _SORTS:
            raise BadRequest(f"sort must be one of: {', '.join(_SORTS)}")
        limit = max(1, min(int(limit), 50))
        page = max(1, int(page))
        start = (page - 1) * limit
        if start >= MAX_SHOWN:
            return Results(items=[], total=None, note=f"rechtspraak.sr shows at most {MAX_SHOWN} hits; narrow the search.")
        common = {"sText": q, "sField": "", "sAuthority[]": court, "sCaseNumber": "", "sJurisdiction[]": area,
                  "sDateType": "", "sDatePeriod": "", "sStartDate": "", "sEndDate": "", "sSruNumber": ""}
        if f.get("since") or f.get("until"):
            # the site's 'na' (after) option ignores its date, so a range always goes out as 'tussen' (between)
            common.update(sDateType="pronunciation", sDatePeriod="between",
                          sStartDate=_site_date(f.get("since") or "1900", False),
                          sEndDate=_site_date(f.get("until") or "2099", True))
        first = start // PER_PAGE + 1
        last = (start + limit - 1) // PER_PAGE + 1
        # page 1 always comes from the form (it carries the total); later pages from load-more
        html1 = await _post(SEARCH, {**common, "sort_order": _SORTS[sort], "search_type": "simple_search",
                                     "advance_search": "advance_search"})
        m = re.search(r"Gevonden:\s*([\d.]+)\s*uitspra", html1)
        total = int(m[1].replace(".", "")) if m else None
        rows: list[DecisionHit] = []
        for n in range(first, last + 1):
            if n == 1:
                i = html1.find('class="load_moredata"')
                rows += _hits(html1[i:] if i >= 0 else html1)
            elif total is None or (n - 1) * PER_PAGE < min(total, MAX_SHOWN):
                rows += _hits(await _post(LOADMORE, {**common, "paged": n, "sSortOrder": _SORTS[sort],
                                                     "search_type": "simple_search",
                                                     "search_type2": "advance_search",
                                                     "max_records_display": 200}))
        off = start - (first - 1) * PER_PAGE
        note = f"Full-text search on rechtspraak.sr (sort: {sort}); the site shows at most {MAX_SHOWN} hits."
        return Results(items=rows[off:off + limit], total=total, note=note)

    async def get_decision(self, id):
        m = _SRU.match(_dash(_http.clean(id)))
        if not m:
            raise BadRequest("Give an SRU number from search_caselaw (e.g. 'SRU-HvJ-2025-24') or its "
                             "rechtspraak.sr URL.")
        url = f"{RS}/{m[1].lower()}/"
        r = await _http.get(url)
        if r.status_code == 404:
            raise NotFound(f"No decision {m[1].upper()} on rechtspraak.sr.")
        if r.status_code != 200:
            raise SourceError(_http.error(RS_HOST, f"decision failed: {url}", r.status_code), r.status_code)
        doc = lhtml.fromstring(r.text)
        box = doc.xpath('//div[contains(@class,"document-page")]')
        body = doc.xpath('//div[contains(@class,"sru-content")]')
        if not box or not body:
            raise NotFound(f"No decision {m[1].upper()} on rechtspraak.sr.")
        sru = _dash(_http.clean(box[0].xpath('string(.//div[contains(@class,"tl-box")]//h3)'))) or m[1].upper()
        f = _labels(box[0].xpath('.//ul[contains(@class,"sru-list-style")]')[0]) \
            if box[0].xpath('.//ul[contains(@class,"sru-list-style")]') else {}
        for h in body[0].xpath('./h3'):
            if _http.clean(h.text_content()) == "Uitspraak":
                h.getparent().remove(h)
        text = _http.html_to_md(lhtml.tostring(body[0], encoding="unicode"))
        court = f.get("Instantie", "")
        meta = {k: f[k] for k in ("Rechtsgebied", "Publicatiedatum") if f.get(k)}
        if f.get("Publicatiedatum"):
            meta["Publicatiedatum"] = _nl_date(f["Publicatiedatum"]) or f["Publicatiedatum"]
        return Decision(id=sru, title=f"{court} {sru}".strip(), text=text, url=url, court=court,
                        date=_nl_date(f.get("Uitspraakdatum", "")), case_number=f.get("Zaaknummer", ""),
                        summary=f.get("Inhoudsindicatie", ""), metadata=meta)

    # ------------------------------------------------------------------ #
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        f = _check_filters(filters, self.legislation_filters)
        q = _fold(_http.clean(query or ""))
        words = re.findall(r"\w+", q)
        if not words:
            raise BadRequest("Give title words, e.g. 'Grondwet' or 'arbeid'.")
        cats = [_pick(f["category"], tuple(_CATS), "category")] if f.get("category") else list(_CATS)
        limit = max(1, min(int(limit), 50))
        page = max(1, int(page))
        found = []
        for cat in cats:
            for lid, title in await _listing(cat):
                t = _fold(title)
                if all(w in t for w in words):
                    found.append((0 if re.match(rf"\W*{re.escape(words[0])}", t) else 1, lid, title))
        found.sort(key=lambda x: x[0])
        start = (page - 1) * limit
        items = [LawHit(id=lid, title=title, type=_CATS[lid.split("/")[0]], url=f"{LAWS}/{lid}/")
                 for _, lid, title in found[start:start + limit]]
        return Results(items=items, total=len(found),
                       note=("Title search over the dna.sr law lists (all words must match). 'Geldende teksten "
                             "t/m 2005' are pre-2005 consolidations; later changes are under 'Wijzigingen na 2005', "
                             "mostly scanned PDFs that cannot be read here (the PDF link is in the error)."))

    async def get_legislation_toc(self, id):
        law = await _law(id)
        entries = law["toc"] or [TocEntry(title="(no 'Artikel' headings found; use get_legislation_text)")]
        return Toc(id=law["id"], title=law["title"], url=law["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        law = await _law(id)
        label = _norm_prov(provision)
        if label not in law["sections"]:
            if not law["sections"]:
                raise NotFound(f"{law['title']}: articles could not be separated in this PDF; "
                               "use get_legislation_text.")
            raise NotFound(f"{law['title']} has no article '{provision}'. Use get_legislation_toc for the labels.")
        text = law["sections"][label]
        if "Let op" in law["meta"]:
            text = f"> {_OCR_WARN}\n\n{text}"
        return Provision(law_id=law["id"], law_title=law["title"], provision=label,
                         text=text, url=law["url"])

    async def get_legislation_text(self, id):
        law = await _law(id)
        return LawText(id=law["id"], title=law["title"], text=law["text"], url=law["url"], metadata=law["meta"])
