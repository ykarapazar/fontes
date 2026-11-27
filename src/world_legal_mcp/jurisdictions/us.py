"""United States (federal): case law from govinfo (GPO), legislation from the US Code (OLRC),
the National Archives (Constitution) and govinfo (Statutes at Large, public laws).

Gotchas this code encodes (verified 2026-11-05 from a UK IP):
  * govinfo search (POST api.govinfo.gov/search) needs an api.data.gov key. We read
    WLM_US_GOVINFO_KEY and fall back to DEMO_KEY, which allowed only 10 requests per IP
    (x-ratelimit-limit: 10); once used up, 429 with Retry-After ~10 h (it resets around
    midnight UTC, i.e. ~10 searches/day). The key goes in the X-Api-Key header, not the URL.
  * Search paging is cursor-based (offsetMark). Page N walks from the last cursor we hold.
  * Everything else on govinfo is keyless: granule MODS at
    www.govinfo.gov/metadata/granule/{pkg}/{granule}/mods.xml and the PDF at
    www.govinfo.gov/content/pkg/{pkg}/pdf/{granule}.pdf. So get_decision needs no key.
  * Opinion text exists only as PDF (born-digital, no HTML/text rendition per granule).
    Text extraction needs the optional `pypdf` package; without it get_decision fails
    with a clear SourceError.
  * USCOURTS = lower federal courts (appellate, district, bankruptcy), roughly 2004 on.
    It has no Supreme Court. USREPORTS = the bound U.S. Reports (granule id
    USREPORTS-{vol}-{page}, so "347 U.S. 483" maps straight to an id); recent terms
    are not bound yet, so the newest Supreme Court opinions are missing.
  * uscode.house.gov was rebuilt as static pages: /us/usc/t{title}/ (title TOC, ~1 MB for
    title 42) and /us/usc/t{title}/s{section}/ (one section with notes). The old
    view.xhtml URLs are gone, and search.xhtml and search.json.gz return 403 (Akamai)
    to non-browser clients, so free-text search goes through govinfo's USCODE
    collection (annual edition, used only to find section numbers).
  * Section labels use an en dash on the page ("1320a–7b") but a hyphen in URLs.
  * eCFR is left out: its robots.txt disallows /api/versioner/v1/full/ (the full text).
  * govinfo's bound U.S. Reports stop at vol. 586 (checked 2026-11-10; 587+ answer an HTML
    error page with HTTP 200). The Supreme Court's own term pages
    supremecourt.gov/opinions/slipopinion/{yy} (yy = 18 for October Term 2018 ...) list every
    opinion of the Court with date, docket, name, a one-line summary and citation. Terms
    before 2018 redirect to the current list. Links: per-opinion slip PDFs from OT2020 on;
    before that, whole-volume PDFs (preliminary print / bound volume, 2.5-7 MB) with
    '#page=N', so we read pages N .. (next opinion's start - 1) of that volume. One listed
    link (588US1PP_final.pdf) answers 403; the site itself uses 588US1PP_web.pdf elsewhere.
  * govinfo STATUTE holds Statutes at Large vols 1-138 (1789-2024; checked 2026-11-10 via the
    keyless sitemap). The keyless link service /link/statute/{vol}/{page} (any page inside an
    act) and /link/statute/{congress}/{public|private}/{num} answer 302 to the granule PDF
    (STATUTE-{vol}-Pg{page}[-n]); we read the Location without following it. Unknown -> 400.
    Granule = whole Stat. pages, so old volumes' first/last pages carry neighbouring acts.
  * govinfo PLAW (104th Congress on) has a <pre> text rendition per law and package MODS
    (/metadata/pkg/PLAW-117publ58/mods.xml). A missing package or granule answers HTTP 200
    with an HTML "Page Not Found", so we check for <mods / <pre>.
  * Ids from those pages: the U.S. Reports citation when assigned ('606 U.S. 942'), else the
    docket ('25-123', '25A312', '142, Orig.'). Citations below vol. 587 go to govinfo.
"""
from __future__ import annotations

import asyncio
import os
import re

from lxml import etree
from lxml import html as lxml_html

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

API = "https://api.govinfo.gov"
GOVINFO = "https://www.govinfo.gov"
USCODE = "https://uscode.house.gov"
_MODS = "{http://www.loc.gov/mods/v3}"
SCOTUS = "https://www.supremecourt.gov"
ARCHIVES = "https://www.archives.gov"
_CONST_PAGES = ("/founding-docs/constitution-transcript", "/founding-docs/bill-of-rights-transcript",
                "/founding-docs/amendments-11-27")
_CONST_ID = "US Constitution"
# Popular names whose official title is generic, so title search cannot find them.
_POPULAR = {
    "inflation reduction act": "Pub. L. 117-169",
    "chips and science act": "Pub. L. 117-167",
    "infrastructure investment and jobs act": "Pub. L. 117-58",
    "american rescue plan act": "Pub. L. 117-2",
    "cares act": "Pub. L. 116-136",
    "tax cuts and jobs act": "Pub. L. 115-97",
    "dodd-frank wall street reform and consumer protection act": "Pub. L. 111-203",
    "patient protection and affordable care act": "Pub. L. 111-148",
}
_POPULAR_USC = {   # popular name -> first section of the Code chapter (govinfo title search misses them)
    "clean air act": "42 USC 7401",
    "americans with disabilities act": "42 USC 12101",
    "ada": "42 USC 12101",
    "clean water act": "33 USC 1251",
    "endangered species act": "16 USC 1531",
    "family and medical leave act": "29 USC 2601",
    "age discrimination in employment act": "29 USC 621",
}
_COLLECTIONS = ("USCOURTS", "USREPORTS", "SUPREMECOURT")
_LAST_GOVINFO_VOL = 586   # last bound U.S. Reports volume on govinfo (checked 2026-11-10)
_FIRST_TERM = 18          # first October Term with a supremecourt.gov opinion list
_DOCKET_RE = re.compile(r"^(\d{2})[-AaOo]\d{1,5}$|^\d{1,3},? Orig\.?$", re.I)

_toc_cache: dict[str, Toc] = {}
_section_cache: dict[str, tuple[str, str]] = {}   # url -> (status, html)
_marks: dict[tuple, dict[int, str]] = {}          # search body -> {page: offsetMark}
_const: list[dict] = []                          # Constitution units, loaded once
_terms: dict[int, list[dict]] = {}                # October Term (yy) -> opinion rows
_pdfs: dict[str, bytes] = {}                      # volume PDF url -> bytes


def _key() -> str:
    return os.environ.get("WLM_US_GOVINFO_KEY", "").strip() or "DEMO_KEY"


# =========================================================================== #
# govinfo search (keyed)
# =========================================================================== #
async def _search(query: str, limit: int, page_no: int) -> dict:
    sig = (query, limit)
    marks = _marks.setdefault(sig, {1: "*"})
    start = max(p for p in marks if p <= page_no)
    data: dict = {}
    for p in range(start, page_no + 1):
        if p not in marks:  # the results ended before this page
            return {"count": data.get("count"), "results": []}
        r = await _http.post(f"{API}/search", json={
            "query": query, "pageSize": limit, "offsetMark": marks[p],
            "sorts": [{"field": "score", "sortOrder": "DESC"}],
        }, headers={"X-Api-Key": _key()})
        if r.status_code == 429:
            wait = r.headers.get("Retry-After", "?")
            raise SourceError(f"govinfo rate limit reached (Retry-After {wait} s). " + (
                "DEMO_KEY allows only about 10 searches a day per IP; set WLM_US_GOVINFO_KEY "
                "to a free api.data.gov key." if _key() == "DEMO_KEY" else ""), 429)
        if r.status_code == 403:
            raise SourceError("govinfo refused the API key (WLM_US_GOVINFO_KEY).", 403)
        if r.status_code != 200:
            raise SourceError("govinfo search failed", r.status_code)
        data = r.json()
        if data.get("offsetMark") and data.get("results"):
            _http.lru_put(marks, p + 1, data["offsetMark"], 200)
    _http.lru_put(_marks, sig, marks, 50)
    return data


_HIT_PAGE = 100  # fixed govinfo pageSize for searches, whatever the limit


async def _search_hits(query: str, limit: int, page_no: int, hit) -> tuple[list, int | None, str]:
    """Page over the granules `hit` keeps (it returns None to skip one), deduplicated by id:
    hits (page_no-1)*limit+1 .. page_no*limit. govinfo pages are fetched at a fixed size, so
    the source order does not depend on `limit`. Total is exact once the results run out,
    else govinfo's count, which includes skipped granules: the third value then says so."""
    need, out, seen, p = page_no * limit, [], set(), 1
    while True:
        data = await _search(query, _HIT_PAGE, p)
        rows = data.get("results", [])
        for r in rows:
            h = hit(r)
            if h and h.id not in seen:
                seen.add(h.id)
                out.append(h)
        if len(rows) < _HIT_PAGE:
            total = len(out)
            break
        if len(out) >= need:
            total = data.get("count")
            break
        p += 1
    return out[need - limit:need], total, ("" if total == len(out) else
        " Total is govinfo's match count, which includes entries skipped here (front matter, "
        "non-opinion granules, duplicates), so it is an upper bound.")


def _key_note() -> str:
    if _key() == "DEMO_KEY":
        return (" Using govinfo DEMO_KEY (about 10 searches/day per IP); set "
                "WLM_US_GOVINFO_KEY to a free api.data.gov key for more.")
    return ""


# =========================================================================== #
# Case law — govinfo USCOURTS + USREPORTS
# =========================================================================== #
_CITE_RE = re.compile(r"^(\d{1,3})\s*U\.?\s*S\.?\s+(\d{1,4})$", re.I)
_GRANULE_RE = re.compile(r"^(USCOURTS-[A-Za-z0-9]+-[A-Za-z0-9_\-]+-\d+|USREPORTS-\d+-\d+)$")


def _granule_id(ref: str) -> str:
    ref = ref.strip()
    m = _CITE_RE.match(ref)
    if m:
        return f"USREPORTS-{int(m[1])}-{int(m[2])}"
    ref = re.sub(r"^https?://www\.govinfo\.gov/app/details/[^/]+/", "", ref).strip("/")
    if not _GRANULE_RE.match(ref):
        raise BadRequest(f"bad decision id {ref!r}. Use a govinfo granule id like "
                         "'USCOURTS-mad-1_13-cv-12927-4' or 'USREPORTS-347-483', a "
                         "U.S. Reports citation like '347 U.S. 483', or a Supreme Court "
                         "docket like '24-809'.")
    return ref


def _package(gid: str) -> str:
    return gid.rsplit("-", 1)[0]


def _details(gid: str) -> str:
    return f"{GOVINFO}/app/details/{_package(gid)}/{gid}"


def _case_number(gid: str) -> str:
    if gid.startswith("USREPORTS-"):
        _, vol, pg = gid.split("-")
        return f"{vol} U.S. {pg}"
    # USCOURTS-{court}-{case}-{n}: "1_13-cv-12927" -> "1:13-cv-12927"
    return _package(gid).split("-", 2)[2].replace("_", ":", 1)


def _mods_value(el, path: str) -> str:
    found = el.find(path.replace("m:", _MODS))
    return _http.clean(found.text) if found is not None and found.text else ""


# =========================================================================== #
# Supreme Court opinions from 2018 on — supremecourt.gov term lists (keyless)
# =========================================================================== #
def _current_term() -> int:
    y, m = int(_http.today()[:4]), int(_http.today()[5:7])
    return (y if m >= 10 else y - 1) % 100


async def _term_rows(term: int) -> list[dict]:
    if term in _terms:
        return _terms[term]
    url = f"{SCOTUS}/opinions/slipopinion/{term:02d}"
    r = await _http.get(url)
    if r.status_code == 403:   # Akamai turns away some plain requests at random: one slow retry
        await asyncio.sleep(10)
        r = await _http.get(url)
    if r.status_code != 200:
        hint = (" (the site's Akamai edge refuses some automated requests with 403 "
                "'Access Denied'; retry later)" if r.status_code == 403 else "")
        raise SourceError(f"supremecourt.gov opinion list for October Term 20{term:02d} "
                          f"failed{hint}", r.status_code)
    rows = []
    for tr in lxml_html.fromstring(r.text).iter("tr"):
        tds = tr.findall("td")
        a = tr.find(".//a[@href]")
        if len(tds) != 6 or a is None or not tds[0].text_content().strip().isdigit():
            continue
        m, d, y = (tds[1].text_content().strip().split("/") + ["", "", ""])[:3]
        cite = _http.clean(tds[5].text_content())
        href = a.get("href")
        rows.append({
            "docket": _http.clean(tds[2].text_content()),
            "date": f"20{y}-{int(m):02d}-{int(d):02d}" if y.isdigit() and m.isdigit() and d.isdigit() else "",
            "name": _http.clean(a.text_content()), "summary": _http.clean(a.get("title")),
            "author": _http.clean(tds[4].text_content()), "term": term,
            "cite": cite if re.fullmatch(r"\d+ U\.S\. \d+", cite) else "",
            "pdf": href if href.startswith("http") else SCOTUS + href,
        })
    return _http.lru_put(_terms, term, rows, 12)


def _row_id(row: dict) -> str:
    return row["cite"] or row["docket"]


async def _find_opinion(ref: str) -> dict:
    """A citation of vol. 587+ or a docket -> its row in the supremecourt.gov term lists."""
    cur = _current_term()
    m = _CITE_RE.match(ref)
    if m:
        guess = _FIRST_TERM + (int(m[1]) - _LAST_GOVINFO_VOL) // 3
        terms = [t for t in (guess, guess - 1, guess + 1) if _FIRST_TERM <= t <= cur]
        want = lambda row: row["cite"] == f"{int(m[1])} U.S. {int(m[2])}"
    else:
        d = _DOCKET_RE.match(ref)
        yy = int(d[1]) if d and d[1] else None
        terms = ([t for t in range(yy - 1, yy + 4) if _FIRST_TERM <= t <= cur] if yy is not None
                 else list(range(cur, _FIRST_TERM - 1, -1)))
        key = re.sub(r"[\s,.]", "", ref).lower()
        want = lambda row: re.sub(r"[\s,.]", "", row["docket"]).lower() == key
    for t in terms:
        for row in await _term_rows(t):
            if want(row):
                return row
    raise NotFound(f"no Supreme Court opinion {ref!r} in the supremecourt.gov term lists "
                   f"(October Terms 20{_FIRST_TERM}-20{cur:02d}).")


def _pdf_pages(data: bytes, first: int, last: int | None) -> str:
    """Text of pages first..last (1-based, inclusive) of a text-layer PDF, like _http.pdf_text."""
    import io
    from pypdf import PdfReader
    pages = PdfReader(io.BytesIO(data)).pages
    out = []
    for p in pages[first - 1:last]:
        lines = [_http.clean(ln) for ln in (p.extract_text() or "").splitlines()]
        if last is None and out and any(re.match(r"Reporter.s N|ORDERS (?:FOR|FROM) |ORDERS \d+$|\d+ ORDERS$", ln)
                                    for ln in lines[:4]):
            break   # last opinion of a volume: stop where the orders section starts
        out.append("\n".join(ln for ln in lines if ln))
    return re.sub(r"\n{3,}", "\n\n", "\n\n".join(p for p in out if p)).strip()


async def _scotus_decision(row: dict) -> Decision:
    try:
        import pypdf  # noqa: F401
    except ImportError:
        raise SourceError("reading Supreme Court PDFs needs the optional 'pypdf' package")
    url, _, frag = row["pdf"].partition("#page=")
    if url in _pdfs:
        data = _pdfs[url]
    else:
        r = await _http.get(url)
        if r.status_code == 403:   # see _term_rows
            await asyncio.sleep(10)
            r = await _http.get(url)
        if r.status_code != 200 or not r.content.startswith(b"%PDF"):
            raise SourceError(f"supremecourt.gov PDF {url} unavailable", r.status_code)
        data = r.content
        if frag:  # whole volume: keep it for the other opinions in it
            _http.lru_put(_pdfs, url, data, 2)
    if frag.isdigit():
        first = int(frag)
        nxt = [int(o["pdf"].split("#page=")[1]) for o in _terms.get(row["term"], [])
               if o["pdf"].startswith(url + "#page=") and o["pdf"].split("#page=")[1].isdigit()
               and int(o["pdf"].split("#page=")[1]) > first]
        text = _pdf_pages(data, first, min(nxt) - 1 if nxt else None)
        version = "preliminary print" if "preliminaryprint" in url else "bound volume"
    else:
        text, version = _http.pdf_text(data), "slip opinion"
    meta = {"Citation": row["cite"] or "not yet assigned", "Docket": row["docket"],
            "Opinion by": row["author"], "Version": f"{version} (supremecourt.gov)",
            "PDF": row["pdf"]}
    return Decision(id=_row_id(row), title=row["name"], text=text, url=row["pdf"],
                    court="Supreme Court of the United States", date=row["date"],
                    case_number=row["docket"], summary=row["summary"], metadata=meta)


def _year(v, name: str) -> int | None:
    if v in (None, ""):
        return None
    if not re.fullmatch(r"\d{4}", str(v).strip()):
        raise BadRequest(f"`{name}` must be a four-digit year, e.g. 2022.")
    return int(str(v).strip())


async def _scotus_search(query: str, limit: int, page: int, y_from=None, y_to=None) -> Results:
    words = [w for w in re.findall(r"[a-z0-9]+", query.lower()) if len(w) > 1]
    if not words:
        raise BadRequest("give words from the case name or summary, e.g. 'Fourth Amendment'.")
    rows = []
    for t in range(_current_term(), _FIRST_TERM - 1, -1):
        rows += await _term_rows(t)
    hits = []
    for row in rows:
        hay = " ".join((row["name"], row["summary"], row["docket"], row["cite"])).lower()
        year = int(row["date"][:4]) if row["date"] else 0
        if (y_from and year < y_from) or (y_to and year > y_to):
            continue
        if all(re.search(rf"\b{re.escape(w)}", hay) for w in words):
            hits.append(row)
    hits.sort(key=lambda r: r["date"], reverse=True)
    start = (page - 1) * limit
    return Results(items=[DecisionHit(
        id=_row_id(r), title=r["name"], court="Supreme Court of the United States",
        date=r["date"], case_number=r["docket"], snippet=r["summary"], url=r["pdf"])
        for r in hits[start:start + limit]], total=len(hits), note=(
        "Supreme Court opinions of the Court from October Term 2018 on (supremecourt.gov), "
        "newest first; matches every word against the case name, docket, citation and the "
        "Court's one-line summary, not the full text. Older opinions: collection USREPORTS."))


_STOPWORDS = {"A", "AN", "THE", "OF", "TO", "IN", "ON", "FOR", "BY", "AT", "AS", "IS", "IT", "AND", "OR", "NOT"}


def _require_terms(query, example):
    """govinfo matches everything for blank, operator-, stopword- or negation-only queries
    and 500s on 1-char ones; require one positive, non-stopword word of 2+ characters."""
    positive = re.sub(r"\b(?:[^\W\d_]\.){2,}", lambda m: m[0].replace(".", ""), query or "")  # U.S. -> US
    positive = re.sub(r'\bNOT\s+(\([^)]*\)|"[^"]*"|[^\s()]+)', " ", positive)
    positive = re.sub(r'(?:^|(?<=[\s(]))-("[^"]*"|\S+)', " ", positive)              # -term excludes
    words = re.findall(r"[^\W_]+", positive)
    if not any(len(w) > 1 and w.upper() not in _STOPWORDS for w in words):
        raise BadRequest(f"give a search query with at least one real word, e.g. '{example}'.")


class UnitedStates(Jurisdiction):
    code = "us"
    name = "United States"
    languages = ("en",)
    aliases = ("usa", "united states", "us-federal")
    sources = (
        Source(
            "govinfo (U.S. Government Publishing Office): USCOURTS opinions and U.S. Reports",
            GOVINFO,
            covers=("caselaw", "legislation"),
            licence="Public domain (US Government works, 17 U.S.C. 105; court opinions)",
            commercial_use=True,
            ai_use=True,   # robots.txt: only /app/search/*, /search/ etc. disallowed; no AI opt-out
            auth="free key for search (api.data.gov, env WLM_US_GOVINFO_KEY; falls back to "
                 "DEMO_KEY, ~10 searches/day); metadata and PDFs need none",
            rate_limit="api.govinfo.gov: DEMO_KEY x-ratelimit-limit 10, then 429 with "
                       "Retry-After ~37,000 s (measured 2026-11-05); "
                       "a personal key gets the api.data.gov default (1,000/hour, documented, "
                       "unverified for govinfo). www.govinfo.gov: unknown; 1 s spacing, no 429 "
                       "seen (2026-11)",
            terms_url="https://www.govinfo.gov/about/policies",
        ),
        Source(
            "Supreme Court of the United States: opinions of the Court (supremecourt.gov)",
            SCOTUS,
            covers=("caselaw",),
            licence="Public domain (court opinions; US Government works, 17 U.S.C. 105)",
            commercial_use=True,
            ai_use=True,   # robots.txt: Disallow /images/, /rss/, /cdn/ only (and bans one named scraper)
            auth="none",
            rate_limit="robots.txt Crawl-delay: 1 (documented); 2 s spacing. Akamai answers "
                       "some plain requests with 403 'Access Denied' at random (opinion lists, "
                       "a PDF, the web-policies page; 2026-11-10); the same URL works minutes "
                       "later. One retry after 10 s, then an error",
            terms_url=f"{SCOTUS}/policies/web_policies_and_notices.aspx",
        ),
        Source(
            "National Archives: Constitution of the United States (transcription)",
            ARCHIVES,
            covers=("legislation",),
            licence="Public domain / CC0 1.0 (NARA Copyright, Restrictions, and Permissions "
                    "Notice on /global-pages/privacy.html)",
            commercial_use=True,
            ai_use=True,   # robots.txt: /founding-docs/ not disallowed; Crawl-delay 10
            auth="none",
            rate_limit="robots.txt Crawl-delay: 10 (documented); 10 s spacing, 3 pages, cached",
            terms_url="https://www.archives.gov/global-pages/privacy.html",
        ),
        Source(
            "govinfo (U.S. Government Publishing Office): Statutes at Large and Public and "
            "Private Laws",
            GOVINFO,
            covers=("legislation",),
            licence="Public domain (US Government works, 17 U.S.C. 105; govinfo Public Domain "
                    "& Copyright Notice)",
            commercial_use=True,
            ai_use=True,   # robots.txt disallows /app/search/* and /search/ only; no AI opt-out
            auth="none for citations ('1 Stat. 50', 'Pub. L. 117-58': link service, MODS, PDF/"
                 "HTML); full-text search uses the govinfo API key like the other collections",
            rate_limit="www.govinfo.gov: unknown; 1 s spacing, no 429 in ~40 requests "
                       "(2026-11-10). api.govinfo.gov search: see the govinfo source above",
            terms_url="https://www.govinfo.gov/about/policies",
            probe={"legislation_query": "Pub. L. 119-1", "law_id": "Pub. L. 119-1",
                   "provision": "2"},
        ),
        Source(
            "United States Code (Office of the Law Revision Counsel, U.S. House)",
            USCODE,
            covers=("legislation",),
            licence="Public domain (US Government work, 17 U.S.C. 105)",
            commercial_use=True,
            ai_use=True,   # robots.txt only disallows the Slurp crawler
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~10 requests (2026-11). "
                       "search.xhtml and search.json.gz return 403 (Akamai) and are not used",
            terms_url="https://uscode.house.gov/about_code.html",
        ),
    )
    caselaw_filters = {
        "collection": "USCOURTS (lower federal courts, ~2004 on), USREPORTS (Supreme "
                      "Court, bound U.S. Reports to vol. 586, 2019; govinfo) or SUPREMECOURT "
                      "(Supreme Court opinions from October Term 2018 on, supremecourt.gov, keyless); "
                      "default USCOURTS + USREPORTS",
        "year_from": "YYYY, on or after. USCOURTS (by govinfo publication date, which can "
                     "trail the decision date) and SUPREMECOURT (decision date) only; with "
                     "no collection set, USCOURTS is searched. Not available for USREPORTS",
        "year_to": "YYYY, on or before (same rules as year_from)",
    }
    legislation_filters = {
        "collection": "USCODE (default: the current US Code, by section), STATUTE (Statutes at "
                      "Large vols 1-138, 1789-2024, acts as enacted, scanned/PDF text) or PLAW "
                      "(public and private laws as enacted, 104th Congress 1995 on); full-text "
                      "search, govinfo key. Citations ('1 Stat. 50', 'Pub. L. 117-58') need no filter",
    }
    min_interval = {"api.govinfo.gov": 1.0, "www.govinfo.gov": 1.0, "uscode.house.gov": 1.0,
                    "www.supremecourt.gov": 2.0, "www.archives.gov": 10.0}
    notes = ("Federal only. Case law: govinfo (lower federal courts ~2004 on + bound U.S. "
             "Reports to vol. 586) and supremecourt.gov (Supreme Court opinions from October Term "
             "2018 on: collection SUPREMECOURT; ids '606 U.S. 942' or a docket), PDF text. Legislation: US Code "
             "by title and section, e.g. '42 USC 1983', and the Constitution ('US Constitution'; "
             "provisions 'preamble', 'art. I', 'art. I sec. 8', 'amend. XIV') from the National "
             "Archives transcription. Acts as enacted: Statutes at Large vols 1-138 (1789-2024; ids "
             "'1 Stat. 50', 'STATUTE-1-Pg50', 'Pub. L. 85-1'; provisions are Stat. pages) and public/"
             "private laws from 1995 ('Pub. L. 119-1'; provisions are sections); full-text search "
             "with filter collection STATUTE or PLAW. No state law (state case law: 'us-states'), no CFR.")
    gaps = (
        ("Code of Federal Regulations (eCFR): robots.txt disallows the full-text endpoint "
         "/api/versioner/v1/full/"),
        ("Supreme Court from October Term 2018 on: searchable by name, docket, citation and the "
         "Court's one-line summary only (no full-text search); 'opinions relating to orders' "
         "not wired"),
        "Lower federal court opinions before ~2004: not in govinfo USCOURTS",
        ("State case law: jurisdiction 'us-states' (CourtListener, unofficial, your own free "
         "token). State statutes: not built yet"),
        "Federal Register and Congress bills: source exists and works but not built yet",
        ("US Constitution: National Archives transcription of the parchment text (original "
         "spelling; superseded clauses are not marked in the articles, only in amendment notes)"),
        ("Statutes at Large: page PDFs with GPO's text layer; older volumes are scans, so "
         "expect OCR errors, and a granule's first and last pages can carry the neighbouring "
         "acts. Laws newer than vol. 138 (2024) come from PLAW (1995 on) until bound"),
        ("Public laws: as enacted, not consolidated (the consolidated text of codified "
         "provisions is the US Code); new laws reach govinfo PLAW some weeks after enactment"),
        ("Case-law search beyond ~10/day: needs a free api.data.gov key (WLM_US_GOVINFO_KEY), else "
         "DEMO_KEY"),
    )
    samples = {
        "caselaw_query": "separate but equal",
        "decision_id": "USREPORTS-347-483",
        "legislation_query": "civil action for deprivation of rights",
        "law_id": "42 USC 1983",
        "provision": "1983",
    }

    # ------------------------------------------------------------------ case law
    async def search_caselaw(self, query, *, limit, page, filters):
        _require_terms(query, "Fourth Amendment")
        coll = (filters.get("collection") or "").strip().upper()
        if coll and coll not in _COLLECTIONS:
            raise BadRequest(f"collection must be one of {', '.join(_COLLECTIONS)}.")
        y_from, y_to = (_year(filters.get(k), k) for k in ("year_from", "year_to"))
        if y_from and y_to and y_from > y_to:
            raise BadRequest(f"year_from ({y_from}) is after year_to ({y_to}).")
        if coll == "SUPREMECOURT":
            return await _scotus_search(query or "", limit, page, y_from, y_to)
        scope = f"collection:{coll}" if coll else "collection:(USCOURTS OR USREPORTS)"
        dated = ""
        if y_from or y_to:
            if coll == "USREPORTS":
                raise BadRequest("year_from/year_to do not work with USREPORTS (govinfo dates "
                                 "the bound volumes by publication, not by decision). Use "
                                 "USCOURTS or SUPREMECOURT, or leave the years out.")
            scope = "collection:USCOURTS"
            dated = f" publishdate:range({y_from or 1900}-01-01,{y_to or 2100}-12-31)"
            # a bare year would match docket numbers ('22-02022'), not the topic: the filter does it
            stripped = re.sub(r"(?:\b(?:since|from|after|before|until|in|to|between|and)\s+)*\b(?:19|20)\d\d\b",
                              " ", query, flags=re.I)
            stripped = re.sub(r"\s+", " ", stripped).strip()
            try:
                _require_terms(stripped, "Fourth Amendment")
                query = stripped
            except BadRequest:
                pass
        if limit * page > 1000:
            raise BadRequest("this search reaches only the first 1000 govinfo results (limit x "
                             "page <= 1000); narrow the query or add year_from/year_to.")

        def decision_hit(r):
            gid = r.get("granuleId") or ""
            if not _GRANULE_RE.match(gid):
                return None
            return DecisionHit(
                id=gid, title=_http.clean(r.get("title")) or gid,
                court=_http.clean((r.get("governmentAuthor") or [""])[-1]),
                date=_http.iso_date(r.get("dateIssued")),
                case_number=_case_number(gid), url=_details(gid))
        hits, total, caveat = await _search_hits(f"{scope}{dated} {query}", limit, page, decision_hit)
        return Results(items=hits, total=total, note=(
            "Relevance order. Federal courts only; USCOURTS starts ~2004 and has no Supreme "
            "Court; U.S. Reports end at vol. 586 (2019): for later Supreme Court opinions use "
            "collection SUPREMECOURT."
            + (" Years filter govinfo's publication date, which can trail the decision date; "
               "USCOURTS only." if dated else "") + caveat + _key_note()))

    async def get_decision(self, id):
        ref = _http.clean(id)
        cite = _CITE_RE.match(ref)
        if (cite and int(cite[1]) > _LAST_GOVINFO_VOL) or _DOCKET_RE.match(ref):
            return await _scotus_decision(await _find_opinion(ref))
        gid = _granule_id(id)
        pkg = _package(gid)
        r = await _http.get(f"{GOVINFO}/metadata/granule/{pkg}/{gid}/mods.xml")
        if r.status_code == 404 or (r.status_code == 200 and b"<mods" not in r.content[:1000]):
            raise NotFound(f"no govinfo decision {gid}. For a U.S. Reports citation the id "
                           "is the case's first page; search to find it.")
        if r.status_code != 200:
            raise SourceError("govinfo metadata request failed", r.status_code)
        root = etree.fromstring(r.content)
        # USREPORTS granule MODS describe the granule itself; USCOURTS granule MODS are the
        # package record with one <relatedItem ID="id-{granule}"> per opinion.
        own = root if root.get("ID") == f"id-{gid}" else root.find(
            f"{_MODS}relatedItem[@ID='id-{gid}']")
        if own is None:
            raise NotFound(f"no govinfo decision {gid}")
        pdf = await _http.get(f"{GOVINFO}/content/pkg/{pkg}/pdf/{gid}.pdf")
        if pdf.status_code != 200 or not pdf.content.startswith(b"%PDF"):
            raise SourceError(f"govinfo PDF for {gid} unavailable", pdf.status_code)
        text = _http.pdf_text(pdf.content)

        meta: dict[str, str] = {}
        if gid.startswith("USREPORTS-"):
            court = "Supreme Court of the United States"
            date = _mods_value(own, "m:extension/m:decisionDate")
            case_no = _mods_value(own, "m:extension/m:usCitation") or _case_number(gid)
            for label, path in (("Docket (SCDB)", "m:extension/m:docketId"),
                                ("Opinion by", "m:extension/m:majorityOpinion/m:writer"),
                                ("Decision type", "m:extension/m:decisionType")):
                if v := _mods_value(own, path):
                    meta[label] = v
            if v := _mods_value(own, "m:extension/m:votes/m:majority"):
                meta["Votes"] = f"{v}-{_mods_value(own, 'm:extension/m:votes/m:minority')}"
            summary = ""
        else:
            court = _mods_value(own, "m:extension/m:courtName")
            date = _mods_value(own, "m:extension/m:dateIssued")
            case_no = _mods_value(root, "m:extension/m:caseNumber") or _case_number(gid)
            summary = _mods_value(own, "m:extension/m:docketText")
            for label, path in (("Nature of suit", "m:extension/m:natureSuit"),
                                ("Cause", "m:extension/m:cause"),
                                ("Case type", "m:extension/m:caseType")):
                if v := _mods_value(root, path):
                    meta[label] = v
            parties = dict.fromkeys(f"{p.get('fullName')} ({p.get('role')})"
                                    for p in root.findall(f"{_MODS}extension/{_MODS}party")
                                    if p.get("fullName"))
            if parties:
                meta["Parties"] = "; ".join(parties)
        meta["PDF"] = f"{GOVINFO}/content/pkg/{pkg}/pdf/{gid}.pdf"
        return Decision(id=gid, title=_mods_value(own, "m:titleInfo/m:title") or gid,
                        text=text, url=_details(gid), court=court,
                        date=_http.iso_date(date), case_number=case_no, summary=summary,
                        metadata=meta)

    # ------------------------------------------------------------------ legislation
    async def search_legislation(self, query, *, limit, page, filters):
        _require_terms(query, "civil action for deprivation of rights")
        if _is_const(query) or re.search(r"\bconstitution\b", query or "", re.I):
            if page > 1:
                return Results(items=[], total=1)
            return Results(items=[LawHit(
                id=_CONST_ID, title="Constitution of the United States", type="Constitution",
                date="1787-09-17", url=ARCHIVES + _CONST_PAGES[0],
                snippet=f'Text: get_legislation_text("us", "{_CONST_ID}"); articles and '
                        f'amendments: get_legislation_toc("us", "{_CONST_ID}")')], total=1)
        popular = _POPULAR.get(re.sub(r"^the\s+|\s+of\s+(?:19|20)\d\d$", "", (query or "").strip().lower()))
        if popular:  # official title is generic: go by citation
            if page > 1:
                return Results(items=[], total=1)
            return Results(items=[_act_hit(await _load_act(await _act_id(popular)))], total=1,
                           note=f"Popular name resolved to {popular}; its official title is "
                                "generic, so a title search would not find it.")
        if _is_act(query):  # a Stat. / Pub. L. citation: no key needed
            if page > 1:
                return Results(items=[], total=1)
            return Results(items=[_act_hit(await _load_act(await _act_id(query)))], total=1)
        coll = (filters.get("collection") or "USCODE").strip().upper()
        if coll not in ("USCODE", "STATUTE", "PLAW"):
            raise BadRequest("collection must be USCODE, STATUTE or PLAW.")
        pop = _POPULAR_USC.get(re.sub(r"^the\s+|\s+of\s+(?:19|20)\d\d$", "", (query or "").strip().lower()))
        if pop and coll == "PLAW":
            return Results(items=[], total=0, note=(
                f"{query.strip()} is in the US Code at {pop} et seq. It was enacted before "
                f"the {_FIRST_PLAW}th Congress (1995), outside PLAW: search collection USCODE, or "
                "STATUTE for the act as enacted."))
        note = ""
        if pop and coll == "USCODE":
            query = pop
            note = (f"Popular name resolved to {pop} et seq.; this is the first section of the "
                    "act's chapter, use get_legislation_toc or get_legislation_provision for the rest.")
        try:
            title, section = _law_id(query)
        except BadRequest:
            title = None
        if title:  # a citation: answer from the OLRC page directly, no key needed
            if page > 1:
                return Results(items=[], total=1)
            if not section:
                return Results(items=[LawHit(id=f"{title} USC", title=f"Title {title}, United States Code",
                                             type="USC title", number=f"{title} U.S.C.",
                                             url=f"{USCODE}/us/usc/t{title}/")], total=1)
            _, doc = await _section_page(title, section)
            return Results(items=[_section_hit(title, section, _section_head(doc))], total=1,
                           note=note or None)

        if limit * page > 1000:
            raise BadRequest("this search reaches only the first 1000 govinfo results (limit x "
                             "page <= 1000); narrow the query.")
        if coll != "USCODE":
            def act_hit(r):
                gid, pkg = r.get("granuleId") or "", r.get("packageId") or ""
                if coll == "STATUTE" and _STATUTE_RE.match(gid):
                    aid, typ, num = gid, "Statutes at Large", _stat_cite(gid)
                elif coll == "PLAW" and (m := _PLAW_RE.match(pkg)):
                    aid = num = _pl_id(int(m[1]), m[2].lower() == "pvtl", int(m[3]))
                    typ = "Private law" if aid.startswith("Priv") else "Public law"
                else:
                    return None
                return LawHit(id=aid, title=_http.clean(r.get("title")) or aid, type=typ,
                              number=num, date=_http.iso_date(r.get("dateIssued")),
                              status="as enacted", url=f"{GOVINFO}/app/details/{pkg}" + (
                                  f"/{gid}" if coll == "STATUTE" else ""),
                              snippet=f'Text: get_legislation_text("us", "{aid}")')
            hits, total, caveat = await _search_hits(f"collection:{coll} {query}", limit, page, act_hit)
            return Results(items=hits, total=total, note=(
                ("Statutes at Large vols 1-138 (1789-2024), acts as enacted; page images with "
                 "GPO's text layer (older volumes are scans, so expect OCR errors). "
                 if coll == "STATUTE" else
                 f"Public and private laws as enacted, {_FIRST_PLAW}th Congress (1995) on. ")
                + "Full-text relevance order." + caveat + _key_note()))
        def usc_hit(r):
            m = re.search(r"-title(\w+?)-.*-sec(.+)$", r.get("granuleId") or "")
            return _section_hit(m[1], m[2], _http.clean(r.get("title"))) if m else None
        hits, total, caveat = await _search_hits(f"collection:USCODE {query}", limit, page, usc_hit)
        return Results(items=hits, total=total, note=(
            "Found via govinfo's annual US Code edition; texts come from the current OLRC Code. "
            "Citations like '42 USC 1983' work as queries too." + caveat + _key_note()))

    async def get_legislation_toc(self, id):
        if _is_const(id):
            units = await _load_const()
            return Toc(id=_CONST_ID, title="Constitution of the United States",
                       url=ARCHIVES + _CONST_PAGES[0],
                       entries=[TocEntry(title=u["head"], provision=u["key"]) for u in units])
        if _is_act(id):
            act = await _load_act(await _act_id(id))
            if "pages" in act:
                vol = _STATUTE_RE.match(act["id"])[1]
                entries = [TocEntry(title=f"{vol} Stat. {act['start'] + i}: {p.splitlines()[0][:100]}"
                                    if p else f"{vol} Stat. {act['start'] + i}",
                                    provision=str(act["start"] + i))
                           for i, p in enumerate(act["pages"])]
            else:
                entries = [TocEntry(title=head, provision=label)
                           for label, head, _ in _act_sections(act["text"])]
            return Toc(id=act["id"], title=act["title"], url=act["url"],
                       entries=entries or [TocEntry(title=act["title"], provision="all")])
        title, section = _law_id(id)
        if section:
            _, doc = await _section_page(title, section)
            head = _section_head(doc)
            return Toc(id=f"{title} USC {section}", title=f"{title} U.S.C. § {section}",
                       url=_section_url(title, section),
                       entries=[TocEntry(title=head or f"§ {section}", provision=section)])
        if title in _toc_cache:
            return _toc_cache[title]
        url = f"{USCODE}/us/usc/t{title}/"
        r = await _http.get(url)
        if r.status_code == 404:
            raise NotFound(f"no US Code title {title}")
        if r.status_code != 200:
            raise SourceError("uscode.house.gov title page failed", r.status_code)
        doc = lxml_html.fromstring(r.content)
        content = doc.find(".//div[@id='content-width']")
        if content is None:
            raise SourceError("unexpected uscode.house.gov title page", r.status_code)
        entries: list[TocEntry] = []

        def walk(el, level):
            for child in el:
                if child.tag == "section":
                    h = child.find("h3")
                    if h is not None:
                        entries.append(TocEntry(title=_nowj(h.text_content()), level=level))
                    walk(child, level + 1)
                elif child.tag == "ul":
                    for a in child.iter("a"):
                        m = re.match(r"^s([^/]+)/$", a.get("href", ""))
                        if m:
                            entries.append(TocEntry(title=_nowj(a.text_content()),
                                                    level=level, provision=m[1]))
        walk(content, 0)
        heading = _nowj(content.findtext(".//h1") or "") or f"Title {title}"
        toc = Toc(id=f"{title} USC", title=f"{title} U.S.C. — {heading}", url=url, entries=entries)
        return _http.lru_put(_toc_cache, title, toc, 4)

    async def get_legislation_provision(self, id, provision):
        if _is_const(id):
            key, sec = _const_key(provision)
            unit = next((u for u in await _load_const() if u["key"] == key), None)
            if unit is None:
                raise NotFound(f"no {key!r} in the US Constitution (articles I-VII, "
                               "amendments I-XXVII, preamble).")
            text = unit["text"]
            if sec:
                parts = re.split(r"(?m)^(?=Section\.? \d+\.)", text)
                text = next((p.strip() for p in parts
                             if re.match(rf"Section\.? {sec}\.", p)), "")
                if not text:
                    raise NotFound(f"no Section {sec} in {unit['head']}.")
                key = f"{key} sec. {sec}"
            return Provision(law_id=_CONST_ID, law_title="Constitution of the United States",
                             provision=key, text=text, url=unit["url"])
        if _is_act(id):
            act = await _load_act(await _act_id(id))
            p = _http.clean(provision)
            if p.lower() in ("all", "text", "whole"):
                label, text = "all", act["text"]
            elif "pages" in act:   # Statutes at Large: provisions are pages
                vol = _STATUTE_RE.match(act["id"])[1]
                m = re.fullmatch(rf"(?:{vol}\s*Stat\.?\s*|p(?:age|g)?\.?\s*)?(\d{{1,5}})", p, re.I)
                i = int(m[1]) - act["start"] if m else -1
                if not 0 <= i < len(act["pages"]):
                    raise NotFound(f"{act['id']} covers pages {act['start']}-"
                                   f"{act['start'] + len(act['pages']) - 1} of volume {vol}; "
                                   "give one of those page numbers.")
                label = str(act["start"] + i)
                text = f"[[Page {vol} Stat. {label}]]\n\n{act['pages'][i]}"
            else:
                want = re.sub(r"^(?:§+|sec(?:tion)?\.?)\s*", "", p, flags=re.I).upper().rstrip(".")
                secs = _act_sections(act["text"])
                hit = next((k for k, s in enumerate(secs) if s[0].upper() == want), None)
                if hit is None:
                    raise NotFound(f"no section {provision!r} in {act['id']}; see "
                                   f"get_legislation_toc(\"us\", \"{act['id']}\").")
                end = secs[hit + 1][2] if hit + 1 < len(secs) else len(act["text"])
                label, text = secs[hit][0], act["text"][secs[hit][2]:end].strip()
            return Provision(law_id=act["id"], law_title=act["title"], provision=label,
                             text=text, url=act["url"], as_of=act["date"])
        title, _ = _law_id(id)
        section = _section_label(provision, title)
        _, doc = await _section_page(title, section)
        body = _section_body(doc, notes=False)
        return Provision(law_id=f"{title} USC", law_title=f"Title {title}, United States Code",
                         provision=section, text=body, url=_section_url(title, section),
                         as_of=_as_of(doc))

    async def get_legislation_text(self, id):
        if _is_const(id):
            units = await _load_const()
            return LawText(id=_CONST_ID, title="Constitution of the United States",
                           text="\n\n".join(f"## {u['head']}\n\n{u['text']}" for u in units),
                           url=ARCHIVES + _CONST_PAGES[0],
                           metadata={"Text": "National Archives transcription (parchment "
                                             "spelling); amendments with ratification dates; "
                                             "last amendment ratified 1992 (27th)"})
        if _is_act(id):
            act = await _load_act(await _act_id(id))
            return LawText(id=act["id"], title=act["title"], text=act["text"], url=act["url"],
                           as_of=act["date"], metadata={"Version": "as enacted", **act["meta"]})
        title, section = _law_id(id)
        if not section:
            raise BadRequest(f"whole US Code titles are too large to return. Give a section, "
                             f"e.g. '{title} USC 1', or browse get_legislation_toc('{title} USC').")
        _, doc = await _section_page(title, section)
        return LawText(id=f"{title} USC {section}", title=_section_head(doc) or f"{title} U.S.C. § {section}",
                       text=_section_body(doc, notes=True), url=_section_url(title, section),
                       as_of=_as_of(doc), metadata={"Citation": f"{title} U.S.C. § {section}"})


# =========================================================================== #
# US Code helpers
# =========================================================================== #
_USC = r"U\.?\s*S\.?\s*C(?:ode)?\.?(?:\s*A\.?)?"
_SEC = r"(?:§+\s*|sec(?:tion)?\.?\s*|s(?=\d))?([0-9][0-9A-Za-z\-–.]*)"
_CITE_FULL = re.compile(rf"^(?:title\s*)?(\d{{1,2}}[aA]?)\s*{_USC}(?:\s*{_SEC})?$", re.I)
_TITLE_ONLY = re.compile(r"^(?:title\s*)?(\d{1,2}[aA]?)$", re.I)


def _law_id(ref: str) -> tuple[str, str]:
    """'42 USC 1983', '42 U.S.C. § 1983', '42 USC', 'title 42' -> ('42', '1983' or '')."""
    s = _http.clean(ref)
    m = re.match(r"^https?://uscode\.house\.gov/us/usc/t(\w+)/(?:s([^/]+)/?)?$", s)
    if m:
        return m[1].lower(), (m[2] or "")
    m = _CITE_FULL.match(s) or _TITLE_ONLY.match(s)
    if not m:
        raise BadRequest(f"bad US Code id {ref!r}. Use '42 USC' (a title) or '42 USC 1983' "
                         "(a section).")
    sec = m[2] if m.re is _CITE_FULL else ""
    return m[1].lower(), (sec or "").replace("–", "-").rstrip(".")


def _section_label(provision: str, title: str) -> str:
    """'1983', '§ 1983', 's1983', 'sec. 1983', '42 USC 1983' -> '1983'."""
    p = _http.clean(provision)
    m = _CITE_FULL.match(p)
    if m and m[2]:
        if m[1].lower() != title:
            raise BadRequest(f"provision {provision!r} is in title {m[1]}, not title {title}.")
        p = m[2]
    p = re.sub(r"^(?:§+|sec(?:tion)?\.?|s(?=\d))\s*", "", p, flags=re.I)
    p = p.replace("–", "-").rstrip(".")
    if not re.fullmatch(r"\d[0-9A-Za-z\-.]*", p):
        raise BadRequest(f"bad section {provision!r}. Use a section number like '1983' or "
                         "'1320a-7b'.")
    return p


def _nowj(s: str) -> str:
    """Clean one line and drop the word joiners (U+2060) OLRC puts before dashes."""
    return _http.clean(s.replace("\u2060", ""))


def _section_url(title: str, section: str) -> str:
    return f"{USCODE}/us/usc/t{title}/s{section}/"


async def _section_page(title: str, section: str):
    url = _section_url(title, section)
    if url not in _section_cache:
        r = await _http.get(url)
        if r.status_code == 404:
            raise NotFound(f"no section {title} U.S.C. § {section}")
        if r.status_code != 200 or b"section-head" not in r.content:
            raise SourceError("uscode.house.gov section page failed", r.status_code)
        _http.lru_put(_section_cache, url, r.text, 32)
    return url, lxml_html.fromstring(_section_cache[url])


def _section_head(doc) -> str:
    h = doc.find(".//h3[@class='section-head']")
    return _http.clean(h.text_content()) if h is not None else ""


def _section_hit(title: str, section: str, heading: str) -> LawHit:
    heading = re.sub(r"^§\s*\S+\.\s*", "", heading)
    return LawHit(id=f"{title} USC {section}",
                  title=f"{title} U.S.C. § {section}" + (f" — {heading}" if heading else ""),
                  type="USC section", number=f"{title} U.S.C. § {section}",
                  url=_section_url(title, section),
                  snippet=f'Text: get_legislation_provision("us", "{title} USC", "{section}")')


def _section_body(doc, *, notes: bool) -> str:
    content = doc.find(".//div[@id='content-width']")
    parts = []
    for el in content:
        cls = el.get("class") or ""
        if cls in ("section-nav", "contextHeader"):
            continue
        if not notes and "note-block" in cls:
            break
        parts.append(etree.tostring(el, encoding="unicode", method="html"))
    return _http.html_to_md("".join(parts)).replace("\u2060", "")


def _as_of(doc) -> str:
    m = re.search(r"through Public Law [\d-]+ \(([A-Za-z]+ \d{1,2}, \d{4})\)",
                  doc.findtext(".//span[@class='lawsInEffect']") or "")
    return _http.en_date(m[1]) if m else ""


# =========================================================================== #
# Constitution — National Archives transcription (3 pages)
# =========================================================================== #
def _is_const(ref) -> bool:
    return bool(re.fullmatch(r"(?:the\s+)?(?:u\.?\s*s\.?|united states)?\s*(?:const\.?|constitution)"
                             r"(?:\s+of the united states)?", _http.clean(ref), re.I))


def _roman(n: int) -> str:
    out = ""
    for v, r in ((10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while n >= v:
            out, n = out + r, n - v
    return out


def _const_key(provision: str) -> tuple[str, str]:
    """'art. I sec. 8', 'article 1, section 8', 'amendment 14', '14th amendment', 'preamble'
    -> ('art. I', '8'), ('amend. XIV', ''), ('preamble', '')."""
    p = _http.clean(provision).lower().replace(",", " ")
    if p.startswith("preamble"):
        return "preamble", ""
    m = re.match(r"^(?:(art(?:icle)?|amend(?:ment)?)\.?\s*([ivxl]+|\d+)|(\d+)(?:st|nd|rd|th)\s+"
                 r"(amend)(?:ment)?)(?:\s*(?:§|s(?:ec(?:tion)?)?)\.?\s*(\d+))?\.?$", p)
    if not m:
        raise BadRequest(f"bad provision {provision!r}. Use 'preamble', 'art. I', 'art. I sec. 8' "
                         "or 'amend. XIV'.")
    kind, num = (m[1], m[2]) if m[1] else (m[4], m[3])
    n = int(num) if num.isdigit() else None
    rom = _roman(n) if n else num.upper()
    return ("art. " if kind.startswith("art") else "amend. ") + rom, (m[5] or "")


async def _load_const() -> list[dict]:
    if _const:
        return _const
    units: list[dict] = []
    for path in _CONST_PAGES:
        url = ARCHIVES + path
        r = await _http.get(url)
        if r.status_code != 200:
            raise SourceError("archives.gov Constitution transcription failed", r.status_code)
        h1 = lxml_html.fromstring(r.content).find(".//h1")
        if h1 is None:
            raise SourceError("unexpected archives.gov Constitution page", r.status_code)
        cur, started = None, path != _CONST_PAGES[1]   # Bill of Rights: skip the 1789 resolution
        for el in h1.getparent():
            t = _http.clean(el.text_content())
            if el.tag in ("h2", "h3"):
                m = re.match(r"^(Article|Amendment)\.?\s+([IVXL]+)\.?$", t, re.I)
                if m:
                    cur = {"key": ("art. " if m[1].lower() == "article" else "amend. ") + m[2].upper(),
                           "head": f"{m[1].capitalize()} {m[2].upper()}", "url": url, "lines": []}
                    units.append(cur)
                    continue
                if t == "The U.S. Bill of Rights":
                    started = True
                if cur is not None and re.match(r"^Section\.? \d+\.$", t):
                    cur["lines"].append(t)
                    continue
                cur = None
            elif el.tag == "div" or t.startswith("Back to"):
                cur = None
            elif el.tag == "p" and t and started:
                if cur is not None:
                    cur["lines"].append(t)
                elif path == _CONST_PAGES[0] and t.startswith("We the People"):
                    units.append({"key": "preamble", "head": "Preamble", "url": url, "lines": [t]})
    for u in units:
        u["text"] = "\n\n".join(u.pop("lines"))
    if len(units) != 1 + 7 + 27:
        raise SourceError(f"archives.gov Constitution pages changed: parsed {len(units)} parts, "
                          "expected 35", 200)
    _const.extend(units)
    return _const


# =========================================================================== #
# Acts as enacted — Statutes at Large (STATUTE) and Public/Private Laws (PLAW)
# =========================================================================== #
_FIRST_PLAW = 104   # PLAW starts with the 104th Congress (1995)
_PL_RE = re.compile(r"^(pub(?:lic)?|p|priv(?:ate)?|pvt)\.?\s*l(?:aw)?\.?\s*(?:no\.?\s*)?(\d{1,3})\s*[-–]\s*(\d{1,4})$", re.I)
_PLAW_RE = re.compile(r"^PLAW-(\d{2,3})(publ|pvtl)(\d{1,4})$", re.I)
_STAT_RE = re.compile(r"^(\d{1,3})\s*Stat\.?\s*(?:at large\s*)?(\d{1,5})$", re.I)
_STATUTE_RE = re.compile(r"^STATUTE-(\d{1,3})-Pg(\d{1,5})(-\d{1,2})?$", re.I)
_SEC_HEAD = re.compile(r"^[ \t]*(?:SECTION|SEC\.)\s+(\d+[A-Z]?(?:-\d+)?)\.\s", re.M)
_acts: dict[str, dict] = {}   # canonical id -> {"meta":…, "text"/"pages":…}


def _is_act(ref: str) -> bool:
    s = _http.clean(ref)
    return any(r.match(s) for r in (_PL_RE, _PLAW_RE, _STAT_RE, _STATUTE_RE))


def _stat_cite(gid: str) -> str:
    m = _STATUTE_RE.match(gid)
    return f"{int(m[1])} Stat. {int(m[2])}"


def _pl_id(congress: int, private: bool, num: int) -> str:
    return f"{'Priv' if private else 'Pub'}. L. {congress}-{num}"


async def _link_granule(path: str, what: str) -> str:
    """govinfo link service -> the STATUTE granule holding that page / law (no key)."""
    r = await _http.get(f"{GOVINFO}/link/statute/{path}?link-type=pdf", follow_redirects=False)
    loc = r.headers.get("location", "")
    m = re.search(r"/(STATUTE-\d+-Pg\d+(?:-\d+)?)\.pdf", loc)
    if r.status_code in (301, 302) and m:
        return m[1]
    if r.status_code in (400, 404):
        raise NotFound(f"govinfo has no Statutes at Large entry for {what}. Volumes 1-138 "
                       "(1789-2024); laws before ~1901 have no public law number: cite them "
                       "as '<vol> Stat. <page>'.")
    raise SourceError("govinfo link service failed", r.status_code)


async def _act_id(ref: str) -> str:
    """Any accepted act reference -> canonical id: 'Pub. L. 117-58' / 'Priv. L. 117-1'
    (104th Congress on, PLAW) or a STATUTE granule id 'STATUTE-1-Pg50'."""
    s = _http.clean(ref)
    if m := _STATUTE_RE.match(s):
        return f"STATUTE-{int(m[1])}-Pg{int(m[2])}{m[3] or ''}"
    if m := _STAT_RE.match(s):
        return await _link_granule(f"{int(m[1])}/{int(m[2])}", s)
    if m := _PLAW_RE.match(s):
        return _pl_id(int(m[1]), m[2].lower() == "pvtl", int(m[3]))
    m = _PL_RE.match(s)
    congress, private, num = int(m[2]), m[1].lower().startswith(("priv", "pvt")), int(m[3])
    if congress >= _FIRST_PLAW:
        return _pl_id(congress, private, num)
    return await _link_granule(f"{congress}/{'private' if private else 'public'}/{num}",
                               _pl_id(congress, private, num))


def _plaw_pkg(aid: str) -> str:
    m = re.match(r"^(Pub|Priv)\. L\. (\d+)-(\d+)$", aid)
    return f"PLAW-{m[2]}{'publ' if m[1] == 'Pub' else 'pvtl'}{m[3]}"


def _plaw_text(html: str) -> str:
    """The <pre> body of a PLAW .htm -> paragraphs. GPO uses hanging indents: a
    continuation line sits 1-4 columns left of its paragraph's first line; anything
    else (blank, deeper, further left, page marker, heading) starts a new paragraph."""
    import html as htmlmod
    body = htmlmod.unescape(re.sub(r"(?s)^.*?<pre>|</pre>.*$", "", html))
    paras: list[str] = []
    cur: list[str] = []
    first = 0
    for raw in body.splitlines():
        line = raw.strip()
        ind = len(raw) - len(raw.lstrip(" "))
        cont = (cur and line and first - 4 <= ind < first and not line.startswith("[[Page")
                and not _SEC_HEAD.match(raw))
        if not cont:
            if cur:
                paras.append(" ".join(cur))
            cur, first = ([line], ind) if line else ([], 0)
            if line.startswith("[[Page") or (line and ind == 0):
                paras.append(line)   # page markers, headings and flush-left lines stand alone
                cur = []
        else:
            cur.append(line)
    if cur:
        paras.append(" ".join(cur))
    return "\n\n".join(_http.clean(p) for p in paras if p.strip())


async def _load_act(aid: str) -> dict:
    if aid in _acts:
        return _acts[aid]
    if aid.startswith("STATUTE-"):
        pkg = aid.split("-Pg")[0]
        r = await _http.get(f"{GOVINFO}/metadata/granule/{pkg}/{aid}/mods.xml")
        if r.status_code in (200, 404) and b"<mods" not in r.content[:2000]:
            raise NotFound(f"no Statutes at Large granule {aid}; cite '<vol> Stat. <page>' and "
                           "the page is resolved to the act that holds it.")
        if r.status_code != 200:
            raise SourceError("govinfo metadata request failed", r.status_code)
        root = etree.fromstring(r.content)
        x = f"{_MODS}extension/{_MODS}"
        law = root.find(f"{x}law")
        pages = root.find(f"{_MODS}part/{_MODS}extent")
        start = int(_mods_value(root, "m:part/m:extent/m:start") or _STATUTE_RE.match(aid)[2])
        meta = {"Citation": _mods_value(root, "m:identifier[@type='preferred citation']") or _stat_cite(aid),
                "Pages": f"{start}-{_mods_value(root, 'm:part/m:extent/m:end')}" if pages is not None else "",
                "Type": _mods_value(root, "m:extension/m:granuleClass"),
                "Congress": _mods_value(root, "m:extension/m:congress"),
                "Chapter": _mods_value(root, "m:extension/m:chapter"),
                "Bill": _mods_value(root, "m:extension/m:associatedBills"),
                "PDF": f"{GOVINFO}/content/pkg/{pkg}/pdf/{aid}.pdf"}
        if law is not None and law.get("number"):
            meta["Law number"] = _pl_id(int(law.get("congress")), law.get("isPrivate") == "true",
                                        int(law.get("number")))
        pdf = await _http.get(meta["PDF"])
        if pdf.status_code != 200 or not pdf.content.startswith(b"%PDF"):
            raise SourceError(f"govinfo PDF for {aid} unavailable", pdf.status_code)
        try:
            import pypdf  # noqa: F401
        except ImportError:
            raise SourceError("reading Statutes at Large PDFs needs the optional 'pypdf' package")
        import io
        from pypdf import PdfReader
        pages = ["\n".join(ln for ln in (_http.clean(x) for x in (p.extract_text() or "").splitlines()) if ln)
                 for p in PdfReader(io.BytesIO(pdf.content)).pages]
        act = {"id": aid, "title": _mods_value(root, "m:titleInfo/m:title") or _stat_cite(aid),
               "date": _http.iso_date(_mods_value(root, "m:extension/m:granuleDate")),
               "url": f"{GOVINFO}/app/details/{pkg}/{aid}", "start": start, "pages": pages,
               "meta": {k: v for k, v in meta.items() if v}}
        vol = _STATUTE_RE.match(aid)[1]
        act["text"] = "\n\n".join(f"[[Page {vol} Stat. {start + i}]]\n\n{p}"
                                  for i, p in enumerate(act["pages"]) if p)
        return _http.lru_put(_acts, aid, act, 4)

    pkg = _plaw_pkg(aid)
    r = await _http.get(f"{GOVINFO}/metadata/pkg/{pkg}/mods.xml")
    if r.status_code in (200, 404) and b"<mods" not in r.content[:2000]:
        raise NotFound(f"govinfo has no {aid} (PLAW holds laws of the {_FIRST_PLAW}th Congress "
                       "on; new laws appear some weeks after enactment).")
    if r.status_code != 200:
        raise SourceError("govinfo metadata request failed", r.status_code)
    root = etree.fromstring(r.content)
    alt = [_http.clean(t.text) for t in root.findall(f"{_MODS}titleInfo[@type='alternative']/{_MODS}title")
           if t.text and not re.match(r"^(Public|Private) Law \d", t.text)]
    official = _mods_value(root, "m:titleInfo/m:title")
    h = await _http.get(f"{GOVINFO}/content/pkg/{pkg}/html/{pkg}.htm")
    if h.status_code != 200 or "<pre>" not in h.text[:2000]:
        raise SourceError(f"govinfo text of {aid} unavailable", h.status_code)
    meta = {"Short title": "; ".join(dict.fromkeys(alt)), "Official title": official,
            "Statute citation": ", ".join(dict.fromkeys(
                t.text for t in root.findall(f"{_MODS}identifier[@type='Statute citation']") if t.text)),
            "Bill": _mods_value(root, "m:extension/m:associatedBills"),
            "PDF": f"{GOVINFO}/content/pkg/{pkg}/pdf/{pkg}.pdf"}
    act = {"id": aid, "title": alt[0] if alt else official or aid,
           "date": _http.iso_date(_mods_value(root, "m:originInfo/m:dateIssued")),
           "url": f"{GOVINFO}/app/details/{pkg}", "text": _plaw_text(h.text),
           "meta": {k: v for k, v in meta.items() if v}}
    return _http.lru_put(_acts, aid, act, 4)


def _act_hit(act: dict) -> LawHit:
    stat = act["id"].startswith("STATUTE-")
    return LawHit(id=act["id"], title=act["title"], type="Statutes at Large" if stat else (
                      "Private law" if act["id"].startswith("Priv") else "Public law"),
                  number=act["meta"].get("Citation") if stat else act["id"], date=act["date"],
                  status="as enacted", url=act["url"],
                  snippet=f'Text: get_legislation_text("us", "{act["id"]}")')


def _act_sections(text: str) -> list[tuple[str, str, int]]:
    """(label, heading line, offset) per SEC. heading of a PLAW text; repeats get '#2'."""
    out, seen = [], {}
    for m in _SEC_HEAD.finditer(text):
        n = seen[m[1]] = seen.get(m[1], 0) + 1
        label = m[1] if n == 1 else f"{m[1]}#{n}"
        end = text.find("\n", m.start())
        head = re.sub(r"<<NOTE:[^>]*>>", "", text[m.start():end if end > 0 else None])
        out.append((label, _http.clean(head)[:160], m.start()))
    return out
