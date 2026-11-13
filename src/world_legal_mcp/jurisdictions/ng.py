"""Nigeria: Supreme Court of Nigeria judgments from the Court's own website (supremecourt.gov.ng).

The site is a React app over a Laravel JSON API at supreme-cms.supremecourt.gov.ng/api/v1.0/
(the app's own public endpoints, no key):
  * Search: GET /judgment-new/search?caseTitle=&suitNo=&judgmentDate=&judgmentDate2=
      - caseTitle: substring of the case title only (not the text). Records added since
        about 2023 have no caseTitle (parties are in petitioner/respondent), so a title
        query never finds them; use the date filters instead.
      - suitNo: substring ("91/2002" finds "SC 91/2002" and "SC91/2002").
      - judgmentDate / judgmentDate2: YYYY-MM-DD range.
      - At most 50 rows, no paging, no hit count; the full record (including the text)
        comes back in every row. With no parameters it lists the 50 newest.
  * Document: GET /judgment/passed/{case_id} -> {"success", "data", "contributors"};
    unknown id -> 404 {"success": false, "message": "Judgment not found"}.
  * Two kinds of record:
      - legacy (1960s to 2012, a few hundred): plain text in `judgement` (\\r\\n line breaks,
        backslash-escaped quotes). Some are duplicated under two case_ids.
      - recent (2023 onwards): `judgement` is empty; the lead judgment is a PDF on S3
        (`watermark_settings` is the copy the site links, `pdfFile` the original). The ones
        checked are scanned images with no text layer; no OCR here, so the decision
        carries the metadata and the PDF link. A PDF that does have a text layer is used.
  * Legacy `dateJudgement` is not always the decision date (e.g. Adetoun Oladeji v
    Nigerian Breweries, cited (2007), is dated 2012-10-19). `citation` sometimes holds
    counsel names (data-entry slip), so it is only shown when it looks like a citation.
    Some legacy rows carry the epoch placeholder 1969-12-31 as their date (shown as no
    date here); the API's date filter still matches them on that placeholder.

Verified 2026-11-05:
  * robots.txt on supremecourt.gov.ng and supreme-cms.supremecourt.gov.ng: "User-agent: *
    / Disallow:" (everything allowed). No terms-of-use or copyright page on the site.
  * API answers with x-ratelimit-limit: 60 (Laravel throttle, per minute).
  * Not used: NigeriaLII (robots Content-Signal ai-input=no, "Disallow: /search/", binding
    as a condition of access); Court of Appeal (coa-admin API lists ~20 judgments, text only
    via Google Drive links); PLAC "Laws of Nigeria" (NGO, unrevised 2004 LFN; its search page
    is broken, so searching it would mean crawling ~70 index pages).

Legislation (verified 2026-11-10). There is no free official consolidated Laws of the
Federation online (justice.gov.ng's Constitution PDF link is dead), so three sources are merged
into one small catalogue (fetched once, then searched locally by title):
  * Constitution, consolidated: FAOLEX (FAO) hosts PLAC's April 2023 print of the 1999
    Constitution "updated with the 1st, 2nd, 3rd Alterations (2010), 4th Alteration (2017) and
    5th Alteration (2023)" (faolex.fao.org/docs/pdf/nig164561.pdf, 8 MB, text layer). Unofficial.
    faolex robots.txt only disallows /design-system/ and /?filters=. FAO terms: content "may be
    copied, printed and downloaded for private study, research and teaching purposes, and for
    use in non-commercial products or services" with acknowledgement -> non-commercial.
    The National Assembly's own 1999 text (nass.gov.ng id 5820) is as enacted and its text
    layer lacks the section numbers of ss. 1-91, so it is listed but not the default.
  * National Assembly (nass.gov.ng, official): the documents page's DataTables endpoint
    /documents/magazine_track/?draw=1&start=0&length=500 returns all ~171 publications in one
    JSON call ([title, upload date, chamber, parliament, session, "Magazine", id]); ~160 are
    Acts as passed (mostly 2001-2017 plus the 2025 tax Acts and Electoral Act 2026), PDFs at
    /documents/download/{id} (an unknown id answers 200 "Sorry, this file is being processed.").
    robots.txt answers with the HTML home page (no rules); "Terms" link is "#" (none published).
  * NIPC (nipc.gov.ng, official): 38 investment-related Acts on
    /external-resources/document-types/act?page=1..3, PDFs under /assets/resources/.
    robots.txt allows everything; no terms page.
  * PLAC "Laws of Nigeria" (lawsofnigeria.placng.org, an NGO; UNOFFICIAL; added 2026-11-10): the
    unrevised 2004 Laws of the Federation (law as at 31 Dec 2002), 413 Acts listed (69 index pages of 8 slots, but several slots are empty; the
    index claims ~550) as HTML, one page per
    Act: view2.php?sn=<n>, id "plac:<n>". The index (index.php?page=1..69, 8 titles a page, no
    page-size parameter; its own search is broken) is read only on demand: filter source=plac, or
    when a default search finds nothing (69 requests at 1 s, then cached in memory). No robots.txt
    (the URL answers with the home page: no rules); no terms page, only "(c) Copyright Policy and
    Legal Advocacy Centre 2026"; FAQ says laws after 2002 are not in it. Licence therefore unknown.
Texts are as enacted (except the Constitution), from PDF text layers; sections are found by
their "N. " line starts (the run of increasing numbers with the largest span, which skips the
arrangement of sections and the schedules).
"""
from __future__ import annotations

import html
import io
import re

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc, TocEntry

HOST = "supreme-cms.supremecourt.gov.ng"
API = f"https://{HOST}/api/v1.0"
SITE = "https://supremecourt.gov.ng"
S3_HOST = "scnwebsites3.s3.af-south-1.amazonaws.com"
COURT = "Supreme Court of Nigeria"
CAP = 50                       # rows the search endpoint returns at most
MAX_PDF = 4_000_000            # bigger PDFs are scanned images in practice: don't download
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_CITATION = re.compile(r"[\[(]\d{4}[\])]")
_search_cache: dict = {}

NASS = "https://nass.gov.ng"
NIPC = "https://nipc.gov.ng"
FAOLEX_PDF = "https://faolex.fao.org/docs/pdf/nig164561.pdf"
CONSTITUTION_ID = "faolex:nig164561"
_ACT = re.compile(r"\bACTS?\b|CONSTITUTION", re.I)
_SECTION = re.compile(r"^(\d{1,3})([A-Z]{0,2})\.(?:\s*[—–]|\s+\S|[A-Z])")
_SCHEDULE = re.compile(r"^((first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)\s+)?schedules?\b", re.I)
PLAC = "https://lawsofnigeria.placng.org"
_plac_catalogue: list[LawHit] = []
_catalogue: list[LawHit] = []
_law_cache: dict = {}


def _s(v) -> str:
    return "" if v is None or str(v).strip().lower() in ("", "none", "null") else str(v)


def _date(r: dict) -> str:
    """dateJudgement, or "" for the epoch placeholder (1969-12-31 / 1970-01-01) legacy rows carry."""
    d = _s(r.get("dateJudgement"))[:10]
    return d if _DATE.match(d) and d not in ("1969-12-31", "1970-01-01") else ""


def _title(r: dict) -> str:
    t = _http.clean(_s(r.get("caseTitle")))
    if not t:
        p, d = _http.clean(_s(r.get("petitioner"))), _http.clean(_s(r.get("respondent")))
        t = f"{p} v {d}" if p and d else p or d
    return t or f"{COURT} {_http.clean(_s(r.get('suitNo')))}".strip()


def _text(raw: str) -> str:
    """Legacy plain text -> markdown paragraphs (one per source line)."""
    raw = html.unescape(raw.replace("\\'", "'").replace('\\"', '"'))
    if re.search(r"<(p|br|div|span)\b", raw, re.I):
        return _http.html_to_md(raw)
    return "\n\n".join(ln for ln in (_http.clean(x) for x in re.split(r"\r?\n", raw)) if ln)


def _hit(r: dict) -> DecisionHit:
    body = _text(_s(r.get("judgement")))
    return DecisionHit(
        id=str(r.get("case_id")), title=_title(r), court=COURT,
        date=_date(r),
        case_number=_http.clean(_s(r.get("suitNo"))),
        snippet=body[:300].replace("\n\n", " ") if body else "(scanned PDF only)",
        url=f"{SITE}/judgment-delivered/{r.get('case_id')}")


def _key(r: dict) -> tuple[str, str]:
    """(suit number, citation) with spaces/punctuation dropped: the same judgment entered twice matches."""
    f = lambda v: re.sub(r"[^A-Z0-9/]", "", _s(v).upper())
    return f(r.get("suitNo")), f(r.get("citation"))


def _twins(rows: list[dict], r: dict) -> list[dict]:
    """Other rows with the same suit number and citation but a different case_id or date."""
    k = _key(r)
    return [x for x in rows if x is not r and k[0] and _key(x) == k
            and (x.get("case_id") != r.get("case_id"))]


def _agrees(r: dict) -> bool:
    """True when the row's date year is the year in its citation, e.g. (2007) and 2007-01-26."""
    c = _CITATION.search(_s(r.get("citation")))
    return bool(c) and bool(_date(r)) and _date(r)[:4] == c[0][1:5]


def _best_date(r: dict, twins: list[dict]) -> str:
    """The row's date, or a twin's date when only the twin agrees with the citation year."""
    if _agrees(r):
        return _date(r)
    return next((_date(x) for x in twins if _agrees(x)), _date(r))


def _twin_note(r: dict, twins: list[dict]) -> str:
    ids = ", ".join(f"{x.get('case_id')} ({_date(x) or 'no date'})" for x in twins)
    return (f"The Court's site lists this judgment ({_s(r.get('suitNo'))}, citation as given) twice, "
            f"as id {r.get('case_id')} ({_date(r) or 'no date'}) and as id {ids}, with different "
            "dates. The date shown is the one whose year matches the citation, when one does; "
            "check it against the law report.")


async def _json(url: str, params: dict | None = None, what: str = "request"):
    r = await _http.get(url, params=params)
    if r.status_code == 404:
        raise NotFound(f"The Supreme Court of Nigeria site has no judgment with that id ({url}).")
    if r.status_code != 200:
        raise SourceError(_http.error("supremecourt.gov.ng", f"{what} failed", r.status_code), r.status_code)
    try:
        d = r.json()
    except ValueError:
        raise SourceError(_http.error("supremecourt.gov.ng", f"{what}: not JSON", r.status_code), r.status_code)
    if not isinstance(d, dict) or not d.get("success"):
        raise SourceError(f"supremecourt.gov.ng {what}: unexpected payload {str(d)[:200]}")
    return d


async def _pdf_text(url: str) -> str:
    """Text layer of a judgment PDF, or "" (scanned image, too big, or unreachable)."""
    if not url:
        return ""
    head = await _http.request("HEAD", url)
    size = int(head.headers.get("Content-Length") or 0)
    if head.status_code != 200 or not size or size > MAX_PDF:
        return ""
    r = await _http.get(url)
    if r.status_code != 200:
        return ""
    from pypdf import PdfReader
    try:
        pages = [p.extract_text() or "" for p in PdfReader(io.BytesIO(r.content)).pages]
    except Exception:
        return ""
    paras = [_http.clean(p) for p in re.split(r"\n\s*\n", "\n\n".join(pages))]
    out = "\n\n".join(p for p in paras if p and not re.fullmatch(r"\d+\s*/\s*\d+", p))
    return out if len(out) >= 500 else ""


async def _get(url: str, what: str):
    r = await _http.get(url)
    if r.status_code != 200:
        raise SourceError(_http.error(url.split("/")[2], f"{what} failed", r.status_code), r.status_code)
    return r


async def _catalogue_load() -> list[LawHit]:
    """Constitution (FAOLEX) + NIPC's 38 Acts + National Assembly Acts: 4 requests, then cached."""
    if _catalogue:
        return _catalogue
    out = [LawHit(id=CONSTITUTION_ID, title="Constitution of the Federal Republic of Nigeria 1999 "
                  "(with the 1st-5th Alterations, to 2023)", type="Constitution",
                  status="consolidated to the Fifth Alteration (2023)",
                  snippet="Unofficial consolidation printed by PLAC (April 2023), hosted by FAOLEX.",
                  url=FAOLEX_PDF)]
    for pg in (1, 2, 3):
        r = await _get(f"{NIPC}/external-resources/document-types/act?page={pg}", "NIPC Acts list")
        for m in re.finditer(r'<a href="/assets/resources/([^"]+\.pdf)"[^>]*class="w-fit no-underline">'
                             r'(.*?)</a>(.*?)<a ', r.text, re.S):
            short = _http.clean(html.unescape(re.sub(r"<[^>]+>", " ", m[2])))
            desc = _http.clean(html.unescape(re.sub(r"<[^>]+>", " ", m[3])))
            full = re.match(r".*?\b(?:Act|ACT)\b(?:,? \d{4})?", desc)
            out.append(LawHit(id=f"nipc:{m[1]}", title=full[0] if full else short or m[1],
                              type="Act", status="as enacted (NIPC copy)", snippet=desc[:300],
                              url=f"{NIPC}/assets/resources/{m[1]}"))
    r = await _get(f"{NASS}/documents/magazine_track/?draw=1&start=0&length=500",
                   "National Assembly documents list")
    try:
        rows = r.json().get("data") or []
    except ValueError:
        raise SourceError("nass.gov.ng documents list: not JSON")
    for row in rows:
        title = _http.clean(html.unescape(re.sub(r"<br\s*/?>.*", "", str(row[0]), flags=re.S)))
        if not _ACT.search(title):
            continue
        out.append(LawHit(id=f"nass:{row[6]}", title=title,
                          type="Constitution" if "CONSTITUTION" in title.upper() else "Act",
                          status="as passed (National Assembly copy)",
                          snippet=f"National Assembly ({row[2]}, {row[3]}, {row[4]})",
                          url=f"{NASS}/documents/download/{row[6]}"))
    _catalogue[:] = out
    return _catalogue


async def _plac_load() -> list[LawHit]:
    """The unrevised LFN 2004 index: 69 pages, fetched once per process on demand."""
    if _plac_catalogue:
        return _plac_catalogue
    out: list[LawHit] = []
    last = 1
    pg = 1
    while pg <= last and pg <= 100:
        r = await _get(f"{PLAC}/index.php?page={pg}", "PLAC Laws of Nigeria index")
        if pg == 1:
            last = max([int(x) for x in re.findall(r"\?page=(\d+)", r.text)] or [1])
        for m in re.finditer(r"<a href='view2\.php\?sn=(\d+)'[^>]*>(.*?)</a>", r.text, re.S):
            t = _http.clean(html.unescape(re.sub(r"<[^>]+>", " ", m[2])))
            if t:
                out.append(LawHit(id=f"plac:{m[1]}", title=t.title() if t.isupper() else t, type="Act",
                                  status="LFN 2004, unrevised (law as at 31 Dec 2002)",
                                  snippet="PLAC print of the Laws of the Federation of Nigeria 2004 (unofficial).",
                                  url=f"{PLAC}/view2.php?sn={m[1]}"))
        pg += 1
    if not out:
        raise SourceError("lawsofnigeria.placng.org: no laws found in the index page.")
    _plac_catalogue[:] = out
    return _plac_catalogue


def _plac_lines(page_html: str) -> tuple[str, list[str]]:
    """(title, text lines) of a view2.php page: the Act's <p>/<li> blocks, numbered list items
    ('<li value=2>') given their number so the section splitter sees 'N. Title'."""
    from lxml import html as lh
    doc = lh.fromstring(page_html)
    h3 = doc.xpath("//td//h3")
    title = _http.clean(" ".join(h3[0].itertext())) if h3 else ""
    body = doc.xpath('//div[contains(@class,"field-item")]')
    if not body:
        return title, []
    lines = []
    for el in body[0].iter("p", "li"):
        if el.tag == "p" and el.getparent().tag == "li":
            continue
        t = _http.clean(" ".join(el.itertext()).replace("\xa0", " "))
        if not t:
            continue
        t = re.sub(r"^(\d{1,3}[A-Z]{0,2})\s+\.\s*", r"\1. ", t)          # '1 . Title' -> '1. Title'
        v = el.get("value") if el.tag == "li" else None
        lines.append(f"{v}. {t}" if v else t)
    return title, lines


def _pdf_url(lid: str) -> tuple[str, str]:
    """(law id, PDF URL) for an id from search_legislation or a matching URL."""
    lid = lid.strip()
    m = re.fullmatch(r"(?:nass:|.*nass\.gov\.ng/documents/download/)(\d+)", lid)
    if m:
        return f"nass:{m[1]}", f"{NASS}/documents/download/{m[1]}"
    m = re.fullmatch(r"(?:nipc:|.*nipc\.gov\.ng/assets/resources/)([\w.-]+/[\w.-]+\.pdf)", lid)
    if m:
        return f"nipc:{m[1]}", f"{NIPC}/assets/resources/{m[1]}"
    if lid in (CONSTITUTION_ID, FAOLEX_PDF) or lid.lower() in ("constitution", "nig164561"):
        return CONSTITUTION_ID, FAOLEX_PDF
    raise BadRequest("Use an id from search_legislation: 'faolex:nig164561' (the Constitution), "
                     "'nass:<number>', 'nipc:<folder>/<file>.pdf' or 'plac:<number>'.")


def _split(text: str) -> tuple[list[str], dict[str, str]]:
    """Section labels in order and their texts: the run of increasing 'N. ' line starts with the
    most sections (the arrangement of sections is a run too, but a short one)."""
    lines = [ln for ln in text.splitlines() if not re.fullmatch(r"\d{1,4}", ln.strip())
             and not ln.startswith("The Constitution of the Federal Republic of Nigeria Updated with")]
    starts = [(i, int(m[1]), m[1] + m[2]) for i, ln in enumerate(lines) if (m := _SECTION.match(ln))]
    best: list = []
    best_span = (0, 0)
    for k, first in enumerate(starts):
        if first[1] > 5:
            continue
        chain, cur = [first], first
        for nxt in starts[k + 1:]:
            if cur[1] < nxt[1] <= cur[1] + 4 or (nxt[1] == cur[1] and nxt[2] != cur[2]
                                                  and nxt[2][-1:].isalpha()):
                chain.append(nxt)
                cur = nxt
        if len(chain) < 3:
            continue
        if sorted(b[0] - a[0] for a, b in zip(chain, chain[1:]))[len(chain) // 2 - 1] < 2:
            continue      # one line per "section": an arrangement of sections, not the body
        span = (len(chain), sum(len(ln) for ln in lines[chain[0][0]:chain[-1][0]]))
        if span > best_span:     # most sections first: a run that strays into the Regulations is shorter
            best, best_span = chain, span
    secs: dict[str, str] = {}
    for n, (i, _, label) in enumerate(best):
        end = best[n + 1][0] if n + 1 < len(best) else len(lines)
        if n + 1 == len(best):     # the last section stops at the first schedule heading
            end = next((j for j in range(i + 1, len(lines))
                        if len(lines[j]) < 60 and _SCHEDULE.match(lines[j].strip())), end)
        secs.setdefault(label, "\n".join(lines[i:end]).strip())
    return list(secs), secs


async def _plac_law(lid: str) -> dict:
    n = lid.split(":", 1)[1]
    url = f"{PLAC}/view2.php?sn={n}"
    r = await _get(url, "PLAC Act page")
    title, lines = _plac_lines(r.text)
    if not lines:
        raise NotFound(f"No Act at {url}.")
    text = "\n".join(lines)
    order, secs = _split(text)
    title = next((h.title for h in _plac_catalogue if h.id == lid), "") or \
        (title.title() if title.isupper() else title)
    return _http.lru_put(_law_cache, lid, {"id": lid, "url": url, "title": title,
                                           "text": "\n\n".join(lines), "order": order, "secs": secs}, 4)


async def _law(lid: str) -> dict:
    m = re.fullmatch(r"(?:plac:|.*lawsofnigeria\.placng\.org/view2\.php\?sn=)(\d{1,4})", lid.strip())
    if m:
        lid = f"plac:{m[1]}"
        return _law_cache.get(lid) or await _plac_law(lid)
    lid, url = _pdf_url(lid)
    if lid in _law_cache:
        return _law_cache[lid]
    r = await _get(url, "legislation PDF")
    if not r.content.startswith(b"%PDF"):
        raise NotFound(f"No PDF at {url} (the site answered: {_http.clean(r.text[:80])!r}).")
    try:
        text = _http.pdf_text(r.content)
    except Exception as e:
        raise SourceError(f"Could not read the PDF at {url}: {e}")
    if len(text) < 500:
        raise SourceError(f"The PDF at {url} has no usable text layer (scanned image; no OCR here).")
    title = next((h.title for h in _catalogue if h.id == lid), "")
    if not title:
        title = next((ln for ln in text.splitlines()[:20] if _ACT.search(ln)), text.splitlines()[0])
    order, secs = _split(text)
    return _http.lru_put(_law_cache, lid, {"id": lid, "url": url, "title": title, "text": text,
                                           "order": order, "secs": secs}, 4)


def _norm_prov(p: str) -> str:
    m = re.fullmatch(r"(?:s(?:ec(?:tion)?)?\.?\s*)?(\d{1,3}[A-Za-z]{0,2})\.?", str(p).strip(), re.I)
    if not m:
        raise BadRequest(f"Give a section number such as '36' or 'section 36', got {p!r}.")
    return m[1].upper()


class Nigeria(Jurisdiction):
    code = "ng"
    name = "Nigeria"
    languages = ("en",)
    aliases = ("nigeria", "federal republic of nigeria", "nga", "scn", "supreme court of nigeria")
    sources = (
        Source(
            name="Supreme Court of Nigeria (supremecourt.gov.ng) – Judgments",
            url=f"{SITE}/judgment",
            covers=("caselaw",),
            licence="unknown: no terms of use or licence published on the site",
            commercial_use=None,
            ai_use=None,   # robots.txt allows everything; no content signals, no AI/TDM clause
            auth="none",
            rate_limit=("60 req/min per the API's x-ratelimit-limit header (seen 2026-11-05); "
                        "1.1 s spacing"),
            terms_url="",
        ),
        Source(
            name="National Assembly of Nigeria (nass.gov.ng) – Acts as passed",
            url=f"{NASS}/documents/magazine",
            covers=("legislation",),
            licence="unknown: no terms of use published (the footer 'Terms' link is empty)",
            commercial_use=None,
            ai_use=None,   # robots.txt answers with the home page: no rules
            auth="none",
            rate_limit="none documented; 1 s spacing (4 catalogue requests, then one PDF per law)",
            terms_url="",
        ),
        Source(
            name="Nigerian Investment Promotion Commission (nipc.gov.ng) – Acts",
            url=f"{NIPC}/external-resources/document-types/act",
            covers=("legislation",),
            licence="unknown: no terms of use published",
            commercial_use=None,
            ai_use=None,   # robots.txt allows everything
            auth="none",
            rate_limit="none documented; 1 s spacing",
            terms_url="",
        ),
        Source(
            name="PLAC Laws of Nigeria (lawsofnigeria.placng.org): unrevised LFN 2004 (unofficial)",
            url=PLAC + "/",
            covers=("legislation",),
            licence=("unknown: no terms page; footer '(c) Copyright Policy and Legal Advocacy Centre 2026'; "
                     "an NGO print of the official 2004 revision, law as at 31 Dec 2002"),
            commercial_use=None,
            ai_use=None,   # no robots.txt rules (the URL answers with the home page)
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~6 requests (2026-11-10); index read on demand (69 pages)",
            terms_url=PLAC + "/aboutus.php",
            official=False,
            warning=("PLAC's 2004 Laws of the Federation: unrevised, law as at 31 Dec 2002 (later Acts "
                     "and amendments are missing); an NGO copy, not the Government Printer's."),
        ),
        Source(
            name="FAOLEX (FAO) – Constitution of Nigeria 1999, consolidated to 2023 (PLAC print)",
            url="https://faolex.fao.org/docs/pdf/nig164561.pdf",
            covers=("legislation",),
            licence=("FAO terms: may be copied and downloaded for private study, research, teaching "
                     "and non-commercial products or services, with acknowledgement of the source"),
            commercial_use=False,
            ai_use=None,   # robots.txt only disallows /design-system/ and /?filters=
            auth="none",
            rate_limit="none documented; 1 s spacing (one 8 MB PDF, cached)",
            terms_url="https://www.fao.org/contact-us/terms/en/",
            warning=("Constitution text is PLAC's April 2023 consolidation hosted by FAOLEX, not the "
                     "Government Printer's; non-commercial use only under FAO's terms."),
            official=False,
        ),
    )
    caselaw_filters = {
        "suit_no": "suit number or part of it, e.g. 'SC 91/2002' or '91/2002'",
        "date_from": "YYYY-MM-DD, judgment date on or after",
        "date_to": "YYYY-MM-DD, judgment date on or before",
    }
    min_interval = {HOST: 1.1, S3_HOST: 1.0, "nass.gov.ng": 1.0, "nipc.gov.ng": 1.0,
                    "faolex.fao.org": 1.0, "lawsofnigeria.placng.org": 1.0}
    notes = ("Supreme Court of Nigeria judgments from the Court's own site: full text for legacy "
             "judgments (1960s-2012); recent ones (2023+) are scanned PDFs (metadata + link). "
             "Legislation: the 1999 Constitution consolidated to 2023 (unofficial PLAC print on "
             "FAOLEX) plus ~200 Acts as passed from the National Assembly and NIPC; title search only.")
    gaps = (
        "Federal legislation: no free consolidated Laws of the Federation online; only ~160 Acts"
         " as passed (nass.gov.ng, mostly 2001-2017 and 2025-2026) and 38 investment-related Acts"
         " (nipc.gov.ng) are covered, not amended/consolidated, and most principal Acts in LFN 2004"
         " are missing",
        "Constitution: unofficial PLAC consolidation to the Fifth Alteration (2023); any later"
         " alteration is not included (unverified whether there is one)",
        "Legislation search matches titles only (no full-text search at the sources)",
        "PLAC 'Laws of Nigeria' (unrevised LFN 2004, 413 Acts listed, unofficial) is wired in (source=plac, or "
         "when a default search finds nothing; first load reads 69 index pages): law as at 31 Dec 2002, so "
         "Acts and amendments since are missing; licence unknown (no terms page)",
        "Recent Supreme Court judgments (2023 on): scans only, no text (metadata and PDF link "
         "given)",
        "Supreme Court judgments 2013-2022: not published in the Court's database (legacy to "
         "2012, recent from 2023)",
        "Court of Appeal (~20 judgments, text only via Google Drive links): not built",
        "Federal High Court and state courts: not researched yet",
    )
    legislation_filters = {
        "source": "'nass' (National Assembly), 'nipc' (NIPC), 'constitution' or 'plac' (unrevised LFN 2004, "
                  "413 Acts; loaded on demand, ~70 s the first time)",
    }
    samples = {
        "caselaw_query": "bank",
        "decision_id": "122",   # Idundun v Okumagba, SC 309/74, 1976
        "legislation_query": "money laundering",
        "law_id": "nipc:copyright-act-2022/copyright-act-2022.pdf",
        "provision": "36",
    }

    # ------------------------------------------------------------------ #
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        src = str((filters or {}).get("source") or "").strip().lower()
        if src and src not in ("nass", "nipc", "constitution", "plac"):
            raise BadRequest("source must be 'nass', 'nipc', 'constitution' or 'plac'.")
        words = re.findall(r"\w+", (query or "").lower())

        def pick(cat, only=src):
            return [h for h in cat
                    if (not only or h.id.startswith({"constitution": "faolex"}.get(only, only)))
                    and all(w in f"{h.title} {h.snippet}".lower() for w in words)]
        hits = [] if src == "plac" else pick(await _catalogue_load())
        extra = ""
        if src == "plac" or (not hits and not src):     # the 69-page LFN index is read only when needed
            hits = pick(await _plac_load(), "plac" if src else "")
            extra = " PLAC's LFN 2004 is unrevised (law as at 31 Dec 2002; unofficial)."
        limit = max(1, int(limit))
        start = (max(1, int(page)) - 1) * limit
        note = ("Matches titles only. Acts are as passed (not consolidated); the "
                "Constitution is consolidated to 2023 (unofficial)." + extra)
        if not hits:
            note += (" Not found: this index holds only the Constitution, ~160 Acts as passed (nass.gov.ng), "
                     "38 NIPC Acts and the unrevised LFN 2004 on PLAC; many principal Acts (for example the "
                     "Criminal Code Act and the Labour Act) are not in it. Try a shorter title word.")
        return Results(items=hits[start:start + limit], total=len(hits), note=note)

    async def get_legislation_toc(self, id):
        law = await _law(str(id))
        if not law["order"]:
            raise NotFound(f"No numbered sections found in {law['url']}; use get_legislation_text.")
        return Toc(id=law["id"], title=law["title"], url=law["url"],
                   entries=[TocEntry(title=law["secs"][k].split("\n")[0][:120], provision=k)
                            for k in law["order"]])

    async def get_legislation_provision(self, id, provision):
        law = await _law(str(id))
        p = _norm_prov(provision)
        if p not in law["secs"]:
            raise NotFound(f"Section {p} not found in {law['title']} ({law['url']}); "
                           "see get_legislation_toc for the sections found.")
        return Provision(law_id=law["id"], law_title=law["title"], provision=p,
                         text=law["secs"][p], url=law["url"],
                         as_of="2023-04-01" if law["id"] == CONSTITUTION_ID else "")

    async def get_legislation_text(self, id):
        law = await _law(str(id))
        cons = law["id"] == CONSTITUTION_ID
        return LawText(id=law["id"], title=law["title"], text=law["text"], url=law["url"],
                       as_of="2023-04-01" if cons else "",
                       metadata={"Version": "consolidated to the Fifth Alteration (2023), PLAC print"
                                 if cons else "as passed / enacted (not consolidated)",
                                 "Sections found": str(len(law["order"]))})

    # ------------------------------------------------------------------ #
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        f = {k: str(v).strip() for k, v in (filters or {}).items() if str(v).strip()}
        params: dict[str, str] = {}
        q = (query or "").strip()
        if q:
            # a bare suit number goes to the suit-number search
            params["suitNo" if re.fullmatch(r"(SC[ ./]*)?(CV[ ./]*)?\d+[./]\d{2,4}", q, re.I) else "caseTitle"] = q
        if "suit_no" in f:
            params["suitNo"] = f["suit_no"]
        for k, p in (("date_from", "judgmentDate"), ("date_to", "judgmentDate2")):
            if k in f:
                if not _DATE.match(f[k]):
                    raise BadRequest(f"{k} must be YYYY-MM-DD, got {f[k]!r}.")
                params[p] = f[k]
        if "judgmentDate" in params or "judgmentDate2" in params:   # the API needs both ends
            params.setdefault("judgmentDate", "1900-01-01")
            params.setdefault("judgmentDate2", _http.today())

        async def fetch(pr):
            key = tuple(sorted(pr.items()))
            got = _search_cache.get(key)
            if got is None:
                d = await _json(f"{API}/judgment-new/search", pr, "search")
                got = _http.lru_put(_search_cache, key, d.get("data") or [], 32)
            return got

        rows = await fetch(params)
        if not rows and len(params.get("caseTitle", "").split()) > 1:
            # the source wants one contiguous substring of the title ("Adetoun Oladeji (Nig.) Ltd v
            # Nigerian Breweries" is not found by "Adetoun Oladeji Nigerian Breweries"): search each
            # word and keep the titles that contain them all
            ws = params["caseTitle"].lower().split()
            seen_ids: set[str] = set()
            for w in dict.fromkeys(ws):
                if len(w) < 3:
                    continue
                for r in await fetch({**{k: v for k, v in params.items() if k != "caseTitle"}, "caseTitle": w}):
                    if str(r.get("case_id")) not in seen_ids and all(
                            x in f"{_title(r)} {_s(r.get('suitNo'))}".lower() for x in ws):
                        seen_ids.add(str(r.get("case_id")))
                        rows = rows + [r]
        if params.get("caseTitle"):
            # Records since about 2023 carry no caseTitle (only the parties), so the source's title
            # search misses them: also list them by date and match the title here.
            lp = {k: v for k, v in params.items() if k != "caseTitle"}
            lp.setdefault("judgmentDate", "2023-01-01")
            lp.setdefault("judgmentDate2", _http.today())
            words = params["caseTitle"].lower().split()
            have = {str(r.get("case_id")) for r in rows}
            rows = rows + [r for r in await fetch(lp) if str(r.get("case_id")) not in have
                           and all(w in f"{_title(r)} {_s(r.get('suitNo'))}".lower() for w in words)]

        # the same judgment entered twice: list it once, the entry whose date agrees with its citation
        dropped = [r for r in rows if any(_agrees(x) for x in _twins(rows, r)) and not _agrees(r)]
        rows = [r for r in rows if not any(r is d for d in dropped)]
        limit = max(1, int(limit))
        start = (max(1, int(page)) - 1) * limit
        items = [_hit(r) for r in rows[start:start + limit]]
        capped = len(rows) >= CAP
        note = ("Search matches case titles (and suit numbers) only, not the judgment text; "
                "judgments since 2023 have no title, so find them with date_from/date_to. The Court's "
                "database has no judgments between 2013 and 2022.")
        shown = rows[start:start + limit]
        if any(not _s(r.get("judgement")) for r in shown):
            note += (" Entries from 2023 on are scanned PDFs: get_decision returns only the metadata "
                     "and the PDF link, not the text.")
        if not items and not capped and q:
            note += (" This court's site cannot search the judgment text, so a topic such as '" + q +
                     "' finds nothing here. Search by party name or suit number, or list a period with "
                     "date_from/date_to and read the decisions.")
        if capped:
            note = f"The source returns at most {CAP} matches and no total; narrow the query. " + note
        seen, dups = set(), []
        for r in rows + dropped:
            t = _twins(rows + dropped, r)
            if t and _key(r) not in seen and len({_date(x) for x in [r, *t]}) > 1:
                seen.add(_key(r))
                dups.append(f"{_s(r.get('suitNo'))} (ids {', '.join(str(x.get('case_id')) for x in [r, *t])}, "
                            f"dates {', '.join(_date(x) or 'none' for x in [r, *t])})")
        if dups:
            note += (" The site lists the same judgment twice with different dates: " + "; ".join(dups)
                     + ". Check the date against the law report citation.")
        if dropped:
            note += (" Duplicate entries left out because their date does not match the citation year: id "
                     + ", ".join(f"{d.get('case_id')} ({_date(d) or 'no date'})" for d in dropped)
                     + " (get_decision still opens them).")
        return Results(items=items, total=None if capped else len(rows), note=note)

    async def get_decision(self, id):
        did = str(id).strip()
        m = re.search(r"(?:judgment-delivered/|^)(\d+)/?$", did)
        if not m:
            raise BadRequest("Use the numeric case id from search_caselaw, e.g. '122', "
                             "or a supremecourt.gov.ng/judgment-delivered/<id> URL.")
        did = m[1]
        d = await _json(f"{API}/judgment/passed/{did}", what="judgment")
        r = d.get("data")
        if not isinstance(r, dict):
            raise NotFound(f"The Supreme Court of Nigeria site has no judgment {did}.")
        pdf = _s(r.get("watermark_settings")) or _s(r.get("pdfFile"))
        text = _text(_s(r.get("judgement")))
        if not text and pdf:
            text = await _pdf_text(pdf)
            if not text:
                text = ("The Court publishes this judgment only as a scanned PDF (no text layer), "
                        f"so no text can be returned here. Read it at: {pdf}")
        meta = {}
        for label, k in (("Type", "type"), ("Appellant / petitioner", "petitioner"),
                         ("Respondent", "respondent"), ("Lead judgment by", "leadJudgeName"),
                         ("Delivered by", "mainjudge"), ("Panel", "judgeName"),
                         ("Dissenting", "dissentingJudgeName"),
                         ("Counsel for appellant", "petCounsel"), ("Counsel for respondent", "respCounsel")):
            v = _http.clean(_s(r.get(k)))
            if v:
                meta[label] = v
        cit = _http.clean(_s(r.get("citation")))
        if cit and _CITATION.search(cit):
            meta["Citation (as given)"] = cit
        if pdf:
            meta["PDF"] = pdf
        twins: list[dict] = []
        m = re.search(r"\d+/\d{2,4}$", _s(r.get("suitNo")).strip())
        if m and cit:
            try:
                rows = (await _json(f"{API}/judgment-new/search", {"suitNo": m[0]}, "search")).get("data") or []
                twins = _twins([*rows, r], r)
            except SourceError:
                twins = []
            if twins:
                meta["Note"] = _twin_note(r, twins)
        return Decision(
            id=did, title=_title(r), text=text, url=f"{SITE}/judgment-delivered/{did}",
            court=COURT, date=_best_date(r, twins),
            case_number=_http.clean(_s(r.get("suitNo"))), metadata=meta)
