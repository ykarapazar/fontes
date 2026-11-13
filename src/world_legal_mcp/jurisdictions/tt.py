"""Trinidad and Tobago: Judiciary judgments (ttlawcourts.org) and the Digital Legislative
Library of the Law Revision Commission (laws.gov.tt).

Case law
--------
www.ttlawcourts.org is Drupal. Its "Recent Judgments" view
(/media-public-information/recent-judgments, ~8,800 judgments of the Court of Appeal and
High Court, 10 a page, newest first) has the public exposed filters `title` (case name,
contains), `field_case_number_value` (suit number) and `field_date_of_delivery_value`
(exact YYYY-MM-DD). Each row links a node page /recent-judgments/<slug> (case name, suit
number, judges, delivery date, summary) and the judgment PDF on webopac.ttlawcourts.org
(the Judiciary's library server). The id is that slug. Text comes from the PDF's text
layer (pypdf); some rulings have no file attached, then only the node page is returned.
robots.txt (www) disallows /search/, /admin/ etc., not the judgments view; webopac has
no robots.txt (404).

Legislation
-----------
laws.gov.tt/ttdll-web is a Grails app. `revision/list?q=` searches revised Act titles
(substring, all hits on one page); `revision/list?currentid=<n>` shows one Act: chapter,
year, Act number, commencement, classification and every point-in-time version as a PDF
(`revision/download/<doc>?type=act`), newest first, the newest being "as at 31 December
2016" (sometimes listed without a file). `revision/byrecent` ("Recent Updates of Acts",
100 a page) lists *unofficial* updated consolidations made since, one PDF per Act
(`?type=amendment`), keyed by "CHAPTER n:nn" or "No. n of YYYY". The current text of a
chapter is the byrecent PDF when there is one, else the newest version PDF. Acts listed
only in byrecent ("No. 4 of 2021", not yet given a chapter) get id "u<doc>".
Sections are cut from the PDF text using the Act's own "Arrangement of Sections".
`revision/byyear?year=YYYY` ("Chronological List" 1838-now) lists every Act of a year with
the PDF of the Act as passed (`?type=amendment`, the Gazette Legal Supplement Part A copy),
so Acts after the 2016 revision are reached too. Those ids are also "u<doc>". The search
scans the 2017-now year lists (cached 6 h); filter `year` lists any one year. Short Acts
have no Arrangement of Sections: sections are then cut on the running numbering 1., 2., ...
The Government Printery (printery.gov.tt/e-gazette/<year>/Acts/) serves the same Act PDFs
as an Apache directory listing; not needed while the DLL lists them with titles.

Privy Council
-------------
The Judicial Committee of the Privy Council is the final court. Its judgments from 2009 on
are on Find Case Law (The National Archives), reached through the gb adapter's code
(court=ukpc, query plus "Trinidad"); hits whose title names another jurisdiction are dropped.
robots.txt there allows `User-agent: *`. Filter `court=privy council`.
"""
from __future__ import annotations

import re
import time
from urllib.parse import urlencode, urlsplit

from lxml import html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from . import gb
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

WWW = "www.ttlawcourts.org"
OPAC = "webopac.ttlawcourts.org"
DLL = "laws.gov.tt"
JUDG_LIST = f"https://{WWW}/media-public-information/recent-judgments"
JUDG_NODE = f"https://{WWW}/recent-judgments/"
DLL_BASE = f"https://{DLL}/ttdll-web/revision"
SRC_PAGE = 10                      # rows per page of the judgments view
_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_TTL = 6 * 3600

_decisions: dict = {}
_laws: dict = {}
_recent: dict = {}                 # {"t": monotonic, "rows": [...]}
_years: dict = {}                  # year -> {"t": monotonic, "rows": [...]}
FIRST_YEAR, SCAN_FROM = 1838, 2017
_UKPC = re.compile(r"(?i)^(?:\[(\d{4})\]\s*UKPC\s*(\d+)|ukpc/(\d{4})/(\d+))$")
_PC_ALIASES = {"privy council", "privy-council", "jcpc", "ukpc", "pc"}
# JCPC jurisdictions other than T&T, as they appear in judgment titles
_OTHER_PC = re.compile(
    r"(?i)\((?:[^)]*\b(?:Bermuda|Cayman|Bahamas|Gibraltar|Jamaica|Mauritius|Virgin Islands|BVI|Antigua|"
    r"St\.? Kitts|Saint Kitts|St\.? Lucia|Saint Lucia|St\.? Vincent|Grenada|Turks|Isle of Man|Jersey|"
    r"Guernsey|Falkland|Anguilla|Montserrat|Brunei|Cook Islands|Tuvalu|Kiribati|Sovereign Base|Belize|"
    r"Barbados|Dominica|Guyana|New Zealand|Eastern Caribbean|St\.? Helena|Ascension|Pitcairn|Niue|"
    r"Seychelles)\b[^)]*)\)")


# --------------------------------------------------------------------------- #
# Case law helpers
# --------------------------------------------------------------------------- #
def _court(case_number: str) -> str:
    s = case_number.upper()
    if s.startswith("C.A") or "CIV.P" in s or "CIV.S" in s or s.startswith("CR.APP") or "CVA" in s:
        return "Court of Appeal"
    if s.startswith(("H.C", "CV", "HC")):
        return "High Court"
    return ""


def _pdf_href(href: str) -> str:
    href = (href or "").strip()
    u = urlsplit(href)
    if (u.hostname or "").lower() not in (OPAC, WWW, "ttlawcourts.org"):
        return ""
    return f"https://{u.hostname.lower()}{re.sub(r'/{2,}', '/', u.path)}"


def _slug(href: str) -> str:
    m = re.search(r"/recent-judgments/([^/?#]+)", href or "")
    return m[1] if m else ""


def _iso(datetime_attr: str) -> str:
    m = re.match(r"\d{4}-\d{2}-\d{2}", datetime_attr or "")
    return m[0] if m else ""


def _rows(doc) -> list[DecisionHit]:
    out = []
    for tr in doc.xpath("//table[contains(@class,'views-table')]/tbody/tr"):
        def cell(name):
            td = tr.xpath(f"./td[contains(@class,'views-field-{name}')]")
            return td[0] if td else None
        t = cell("title")
        a = t.xpath(".//a[@href]") if t is not None else []
        slug = _slug(a[0].get("href")) if a else ""
        if not slug:
            continue
        num = _http.clean(_http.text(cell("field-case-number")))
        when = cell("field-date-of-delivery")
        tm = when.xpath(".//time/@datetime") if when is not None else []
        judges = cell("field-judge-judicial-officer")
        jn = ", ".join(_http.clean(x.text_content()) for x in judges.xpath(".//a")) if judges is not None else ""
        out.append(DecisionHit(
            id=slug, title=_http.clean(a[0].text_content()) or f"{_court(num)} {num}".strip(),
            court=_court(num), date=_iso(tm[0]) if tm else "", case_number=num,
            snippet=jn, url=JUDG_NODE + slug))
    return out


def _last_page(doc) -> int:
    hrefs = doc.xpath("//li[contains(@class,'pager__item--last')]/a/@href")
    m = re.search(r"[?&]page=(\d+)", hrefs[0]) if hrefs else None
    return int(m[1]) if m else 0


# --------------------------------------------------------------------------- #
# Legislation helpers
# --------------------------------------------------------------------------- #
def _chap(s: str) -> str:
    m = re.search(r"CHAP(?:TER|\.)\s*(\d{1,3}:\d{2}[A-Z]?)", s or "", re.I)
    return m[1].upper() if m else ""


async def _dll_get(url: str, what: str):
    r = await _http.get(url)
    if r.status_code != 200:
        raise SourceError(_http.error("laws.gov.tt", what, r.status_code), r.status_code)
    return r


async def _recent_rows() -> list[dict]:
    """Every 'Recent Updates of Acts' row (unofficial consolidations), cached 6 h."""
    if _recent and time.monotonic() - _recent["t"] < _TTL:
        return _recent["rows"]
    rows, offset = [], 0
    while offset < 2000:
        r = await _dll_get(f"{DLL_BASE}/byrecent?offset={offset}&max=100", "recent updates list failed")
        page = re.findall(r'(?s)download/(\d+)\?type=amendment" class="clear">(.*?)</tr>', r.text)
        for doc, body in page:
            cells = [_http.clean(c) for c in re.sub(r"<[^>]+>", "|", body).split("|")]
            cells = [lhtml.fromstring(c).text_content() if "&" in c else c for c in cells if c]
            if len(cells) < 2:
                continue
            ref, title = cells[0], cells[1]
            rows.append({"doc": doc, "ref": ref, "title": title, "chapter": _chap(ref)})
        if len(page) < 100:
            break
        offset += 100
    _recent.update(t=time.monotonic(), rows=rows)
    return rows


async def _year_rows(year: int) -> list[dict]:
    """Every Act of one year from the Chronological List (PDF of the Act as passed), cached 6 h."""
    hit = _years.get(year)
    if hit and time.monotonic() - hit["t"] < _TTL:
        return hit["rows"]
    r = await _dll_get(f"{DLL_BASE}/byyear?year={year}", f"Acts of {year} list failed")
    if f"year - {year}" not in r.text:
        raise SourceError(f"Error (laws.gov.tt): the Chronological List did not show {year}; layout changed.",
                          "layout")
    rows = []
    for doc, ref, title in re.findall(
            r'(?s)download/(\d+)\?type=amendment" class="clear">\s*<strong[^>]*>([^<]*)</strong>\s*</a>'
            r'\s*</td>\s*<td>(.*?)</td>', r.text):
        title = _http.clean(lhtml.fromstring(title).text_content()) if title.strip() else ""
        rows.append({"doc": doc, "ref": _http.clean(ref), "title": title, "year": year})
    _years[year] = {"t": time.monotonic(), "rows": rows}
    return rows


def _cached_year_row(doc: str) -> dict | None:
    return next((x for v in _years.values() for x in v["rows"] if x["doc"] == doc), None)


def _split_plain(text: str) -> tuple[list[TocEntry], dict[str, str]]:
    """Sections of an Act as passed that has no Arrangement of Sections: lines starting
    1., 2., 3. ... in strict sequence (quoted inserted sections like '58A.' stay inside)."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip() and not _PAGE_JUNK.match(ln.strip())]
    pos: list[tuple[str, int]] = []
    sched_at = None
    for i, ln in enumerate(lines):
        if pos and _SCHED.match(ln) and ln.split()[-1].isupper():
            sched_at = i
            break
        if re.match(rf"^{len(pos) + 1}\.\s+\S", ln):
            pos.append((str(len(pos) + 1), i))
    texts: dict[str, str] = {}
    toc: list[TocEntry] = []
    for n, (lab, i) in enumerate(pos):
        end = pos[n + 1][1] if n + 1 < len(pos) else (sched_at or len(lines))
        texts[lab] = "\n".join(lines[i:end])
        first = re.sub(rf"^{lab}\.\s+", "", lines[i])
        toc.append(TocEntry(title=f"{lab}. {first[:70]}".rstrip(), level=1, provision=lab))
    if sched_at is not None and pos:
        texts["Schedule"] = "\n".join(lines[sched_at:])
        toc.append(TocEntry(title="Schedule(s)", level=0, provision="Schedule"))
    return toc, texts


def _detail(html: str, cid: str) -> dict:
    doc = lhtml.fromstring(html)
    head = doc.xpath("//a[@href='#showact']")
    if not head:
        raise SourceError(f"Error (laws.gov.tt): record {cid} has no Act panel; the page layout changed.",
                          "layout")
    name = _http.clean(head[0].text_content())
    panel = head[0].getparent()
    while panel is not None and "Classification" not in panel.text_content():
        panel = panel.getparent()
    ptext = _http.clean(panel.text_content()) if panel is not None else ""
    facts = {}
    for k in ("Year", "Act Number", "Commencement Date", "Classification"):
        m = re.search(rf"{k} - (.+?)(?= Year -| Act Number -| Commencement Date -| Classification -| Versions|$)", ptext)
        if m:
            facts[k] = m[1].strip()
    long_title = ""
    m = re.search(r"(An? (?:Act|Ordinance)\b.+?\.)\s+(?:Year -|$)", ptext)
    if m:
        long_title = m[1]
    versions = []
    for a in doc.xpath("//a[contains(@href,'/revision/download/') and contains(@href,'type=act') and @class='clear']"):
        did = re.search(r"download/(\d+)", a.get("href"))[1]
        label = _http.clean(a.text_content())
        versions.append({"doc": did, "label": label})
    title = re.sub(r"\s*Chap\.\s*[\d:A-Z]+$", "", name).strip()
    return {"name": name, "title": title, "chapter": _chap(name), "facts": facts,
            "long_title": long_title, "versions": versions}


_PAGE_JUNK = re.compile(
    r"^(?:U N O F F I C I A L.*|UNOFFICIAL VERSION|UPDATED TO .*|L\.R\.O\.|LAWS OF TRINIDAD AND TOBAGO|"
    r"(?:OFFICE OF THE )?(?:MINISTRY OF THE )?ATTORNEY GENERAL AND (?:MINISTRY OF )?LEGAL AFFAIRS|"
    r"www\.[a-z.]+|\d+ Chap\. [\d:A-Z]+ .*|.* Chap\. [\d:A-Z]+ \d+|SECTION|"
    r"ARRANGEMENT OF SECTIONS[—\- ]+Continued|Page \d+ of \d+)$")
_SEC = re.compile(r"^\*?\s*(\d+[A-Z]{0,2})\.\s+(\S.*)$")
_SCHED = re.compile(r"^((?:FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH|SEVENTH|EIGHTH|NINTH|TENTH)\s+)?SCHEDULE\b.*$")


def _split(text: str) -> tuple[list[TocEntry], dict[str, str], str]:
    """Cut a revised-law PDF text into sections using its Arrangement of Sections.
    Returns (toc, {label: text}, cleaned full text)."""
    lines = [ln for ln in text.splitlines() if not _PAGE_JUNK.match(ln.strip())]
    full = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
    flat = [ln for ln in lines if ln.strip()]
    start = next((i for i, ln in enumerate(flat) if ln.strip().upper().startswith("ARRANGEMENT OF SECTIONS")), None)
    arrangement: list[tuple[str, str]] = []
    headings: dict[str, list[str]] = {}
    body_at = None
    if start is not None:
        pending: list[str] = []
        seen = set()
        for i in range(start + 1, len(flat)):
            ln = flat[i].strip()
            m = _SEC.match(ln)
            if m:
                if m[1] in seen:            # numbering restarts: the body begins
                    body_at = i
                    break
                seen.add(m[1])
                arrangement.append((m[1], m[2]))
                if pending:
                    headings[m[1]] = pending
                    pending = []
            elif ln.isupper() and len(ln) < 90:
                pending.append(ln)
    if not arrangement or body_at is None:
        return [], {}, full
    # locate each section's first line in the body, in order
    body = flat[body_at:]
    labels = [lab for lab, _ in arrangement]
    pos: list[tuple[str, int]] = []
    k = 0
    for i, ln in enumerate(body):
        s = ln.strip()
        for j in range(k, min(k + 4, len(labels))):
            if re.match(rf"^\*?\s*{re.escape(labels[j])}\.(\s|$)", s):
                pos.append((labels[j], i))
                k = j + 1
                break
        if k >= len(labels):
            break
    if not pos:
        return [], {}, full
    sched_at = None
    last = pos[-1][1]
    for i in range(last + 1, len(body)):
        if _SCHED.match(body[i].strip()) and body[i].strip().split()[-1].isupper():
            sched_at = i
            break
    texts: dict[str, str] = {}
    for n, (lab, i) in enumerate(pos):
        end = pos[n + 1][1] if n + 1 < len(pos) else (sched_at or len(body))
        chunk = [x.strip() for x in body[i:end]]
        while len(chunk) > 1 and chunk[-1].isupper() and len(chunk[-1]) < 90:
            chunk.pop()                     # the next section's part heading
        texts[lab] = "\n".join(chunk)
    if sched_at is not None:
        texts["Schedule"] = "\n".join(x.strip() for x in body[sched_at:])
    toc = []
    titles = dict(arrangement)
    for lab, _ in pos:
        for h in headings.get(lab, []):
            toc.append(TocEntry(title=h, level=0))
        toc.append(TocEntry(title=f"{lab}. {titles.get(lab, '')}".strip(), level=1, provision=lab))
    if "Schedule" in texts:
        toc.append(TocEntry(title="Schedule(s)", level=0, provision="Schedule"))
    return toc, texts, full


def _norm_prov(p: str) -> str:
    s = _http.clean(p)
    if re.match(r"(?i)^(the\s+)?(first|second|third|fourth|fifth)?\s*sched", s):
        return "Schedule"
    s = re.sub(r"(?i)^(section|sec\.?|s\.|s|article|art\.?)\s*", "", s).strip().rstrip(".")
    m = re.match(r"^(\d+\s*[A-Za-z]{0,2})(?:\s*\(.*)?$", s)
    return re.sub(r"\s+", "", m[1]).upper() if m else s


# --------------------------------------------------------------------------- #
class TT(Jurisdiction):
    code = "tt"
    name = "Trinidad and Tobago"
    languages = ("en",)
    aliases = ("trinidad", "tobago", "trinidad and tobago", "t&t", "republic of trinidad and tobago")
    sources = (
        Source(
            name="Judiciary of Trinidad and Tobago: Recent Judgments (ttlawcourts.org) and judgment PDFs "
                 "(webopac.ttlawcourts.org)",
            url=JUDG_LIST,
            covers=("caselaw",),
            licence=("© The Judiciary of Trinidad and Tobago; Copyright Act Chap. 22:19. Terms: material "
                     "'may be downloaded for information purposes'"),
            commercial_use=False,   # terms: site "maintained for your personal use and viewing"
            ai_use=None,            # no AI/TDM clause; robots.txt does not cover the judgments view
            auth="none",
            rate_limit="unknown; 1 s spacing per host, no 429 seen in ~25 requests (2026-11)",
            terms_url=f"https://{WWW}/uncategorised/terms-use",
            warning=("Personal use only: Judiciary terms say the site is maintained for personal use and "
                     "viewing; its material may be downloaded for information purposes."),
        ),
        Source(
            name="Digital Legislative Library, Law Revision Commission (laws.gov.tt)",
            url=f"{DLL_BASE}/list",
            covers=("legislation",),
            licence="© Ministry of Land and Legal Affairs, all rights reserved; no licence or reuse terms stated",
            commercial_use=None,
            ai_use=None,            # no robots.txt (404), no terms page, no AI/TDM clause
            auth="none",
            rate_limit="unknown; 1 s spacing, recent-updates list cached 6 h; no 429 seen in ~20 requests (2026-11)",
            terms_url="https://laws.gov.tt/#content",
            warning=("Unofficial versions: the Law Revision Commission says only the printed Revised Laws "
                     "are official; revised editions run to 31 Dec 2016, later updates are unofficial."),
        ),
        gb.UnitedKingdom.sources[0],   # Find Case Law: Privy Council appeals from T&T
    )
    caselaw_filters = {
        "case_number": "suit number as the Judiciary writes it, e.g. CV.2020-02873 or C.A.CIV.P.141/2018",
        "date": "delivered on this day, YYYY-MM-DD",
        "court": ("'privy council' for the final court (JCPC appeals from T&T, 2009 on, via Find Case Law; "
                  "full-text query, all words must match); default: Court of Appeal and High Court"),
    }
    legislation_filters = {
        "year": "list the Acts passed in one year (1838 to now), as passed; the query then narrows titles",
    }
    min_interval = {WWW: 1.0, OPAC: 1.0, DLL: 1.0, "caselaw.nationalarchives.gov.uk": 0.3}
    notes = ("Court of Appeal and High Court judgments published by the Judiciary (search by case name, "
             "suit number or delivery date; text from the official PDF). Privy Council (final court) "
             "appeals from T&T 2009 on via Find Case Law: filter court='privy council'. Revised Acts by "
             "chapter from the Law Revision Commission, its later unofficial updates, and every Act as "
             "passed by year (filter year); title search only.")
    gaps = (
        ("Official text of Acts: only the printed Revised Laws are official; editions run to 31 Dec"
         " 2016, later updates unofficial; Acts since 2017 are given as passed, not consolidated"),
        "Full-text search of Acts: the Digital Legislative Library searches titles only",
        ("Privy Council judgments before 2009: only on BAILII, which forbids scraping; T&T appeals are "
         "picked out of Find Case Law by title, so a title naming no jurisdiction may slip through"),
        "Rulings with no judgment file attached: not published online (node page only)",
        "Magistrates' Courts and tribunals: not researched yet",
        "Subsidiary legislation and the Gazette: not researched yet",
    )
    samples = {
        "caselaw_query": "Attorney General",
        "decision_id": "beckles-wendell-v-attorney-general-trinidad-and-tobago",
        "legislation_query": "Interpretation",
        "law_id": "524",          # Interpretation Act, Chap. 3:01
        "provision": "3",
    }

    # ------------------------------------------------------------------ #
    # Case law
    # ------------------------------------------------------------------ #
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        f = {k: str(v).strip() for k, v in (filters or {}).items() if str(v).strip()}
        coa = False
        if "court" in f:
            if f["court"].lower() in _PC_ALIASES:
                return await self._search_privy_council(query, f, limit, page)
            if f["court"].lower() == "court of appeal" and "case_number" not in f:
                f["case_number"] = "C.A"    # the view has no court filter; appeal suit numbers start C.A.
                coa = True
            if f["court"].lower() not in ("ttlawcourts", "judiciary", "court of appeal", "high court"):
                raise BadRequest("court must be 'privy council' (final court, via Find Case Law) or left out "
                                 "(Court of Appeal and High Court).")
        params = {}
        if (query or "").strip():
            params["title"] = query.strip()
        if "case_number" in f:
            params["field_case_number_value"] = f["case_number"]
        if "date" in f:
            if not _DATE.match(f["date"]):
                raise BadRequest("date must be YYYY-MM-DD (the exact delivery day).")
            params["field_date_of_delivery_value"] = f["date"]
        limit = max(1, min(int(limit), 50))
        start = (max(1, int(page)) - 1) * limit
        hits: list[DecisionHit] = []
        total = None
        src = start // SRC_PAGE
        while len(hits) < limit:
            q = dict(params, page=str(src)) if src else params
            url = JUDG_LIST + ("?" + urlencode(q) if q else "")
            r = await _http.get(url)
            if r.status_code != 200:
                raise SourceError(_http.error("ttlawcourts.org", "judgment search failed", r.status_code),
                                  r.status_code)
            doc = lhtml.fromstring(r.text)
            rows = _rows(doc)
            last = _last_page(doc)
            if src >= last:
                total = src * SRC_PAGE + len(rows)
            elif total is None:
                lr = await _http.get(JUDG_LIST + "?" + urlencode(dict(params, page=str(last))))
                if lr.status_code == 200:
                    total = last * SRC_PAGE + len(_rows(lhtml.fromstring(lr.text)))
            skip = start - src * SRC_PAGE if src == start // SRC_PAGE else 0
            hits += rows[skip:]
            if len(rows) < SRC_PAGE or src >= last:
                break
            src += 1
        note = ("Searches case names and suit numbers only, not judgment text or subjects: the Judiciary's site "
                "cannot search those, so a topic such as 'adverse possession' only matches if it is in the case "
                "name, and 0 hits does not mean there is no case law on it. Each judgment's page lists its "
                "MAIN SUBJECTS (shown by get_decision), but they cannot be searched; search by party name or "
                "suit number, then open the decision to check its subjects. Newest first.")
        if "date" in f:
            note += (f" Filtered to judgments delivered on {f['date']} only; the source has no date range, "
                     "so 'since' a date cannot be searched.")
        if coa:
            note += " Court of Appeal = suit numbers containing 'C.A' (the source has no court filter)."
        elif f.get("court", "").lower() == "high court":
            note += " court='high court' is not applied: the source cannot filter by court."
        return Results(items=hits[:limit], total=total, note=note)

    async def _search_privy_council(self, query, f, limit, page):
        if "case_number" in f or "date" in f:
            raise BadRequest("case_number and date filters apply to the Judiciary's judgments only; with "
                             "court='privy council' put words (party names, topics) in the query.")
        q = " ".join(x for x in ((query or "").strip(), "Trinidad") if x)
        res = await gb._search_caselaw(q, court="ukpc", party=None, judge=None, order="-date",
                                       limit=max(1, min(int(limit), 50)), page_no=max(1, int(page)))
        items = []
        for h in res.items:
            if "trinidad" not in h.title.lower() and _OTHER_PC.search(h.title):
                continue                    # an appeal from elsewhere that cites T&T
            h.court = "Judicial Committee of the Privy Council"
            items.append(h)
        return Results(items=items, total=None,
                       note=("Privy Council judgments from Find Case Law (2009 on), full text, all words must "
                             "match; appeals from other jurisdictions dropped by title, so a page can hold "
                             "fewer hits. " + res.note.split(".")[0] + "."))

    async def get_decision(self, id):
        m = _UKPC.match(re.sub(r"^https?://caselaw\.nationalarchives\.gov\.uk/(?:id/)?", "",
                               (id or "").strip()).strip("/"))
        if m:
            year, num = (m[1], m[2]) if m[1] else (m[3], m[4])
            d = await gb._get_judgment(f"ukpc/{year}/{num}")
            d.court = "Judicial Committee of the Privy Council"
            return d
        slug = (id or "").strip().strip("/")
        slug = _slug("/recent-judgments/" + slug.split("/recent-judgments/")[-1])
        if not _SLUG.match(slug) or len(slug) > 200:
            raise BadRequest("Use the judgment id from search_caselaw, e.g. "
                             "'beckles-wendell-v-attorney-general-trinidad-and-tobago', or a Privy Council "
                             "neutral citation such as '[2026] UKPC 35'.")
        if slug in _decisions:
            return _decisions[slug]
        url = JUDG_NODE + slug
        r = await _http.get(url)
        if r.status_code == 404:
            raise NotFound(f"No judgment '{slug}' on ttlawcourts.org.")
        if r.status_code != 200:
            raise SourceError(_http.error("ttlawcourts.org", "judgment page failed", r.status_code), r.status_code)
        doc = lhtml.fromstring(r.text)
        art = doc.xpath("//article[@data-history-node-id]")
        if not art:
            raise SourceError("Error (ttlawcourts.org): judgment page has no article; layout changed.", "layout")
        art = art[0]

        def field(name):
            return art.xpath(f".//div[contains(@class,'field--name-{name}')]")

        title = _http.clean(_http.text((art.xpath(".//h1") or [None])[0]))
        num_el = field("field-case-number")
        num = _http.clean(_http.text(num_el[0].xpath(".//div[@class='field__item']")[0])) if num_el else ""
        tm = art.xpath(".//div[contains(@class,'field--name-field-date-of-delivery')]//time/@datetime")
        judges = [_http.clean(a.text_content()) for a in
                  art.xpath(".//div[contains(@class,'field--name-field-judge-judicial-officer')]//a")]
        summ_el = field("field-summary")
        summary = _http.clean(_http.text(summ_el[0].xpath(".//div[@class='field__item']")[0])) if summ_el else ""
        if summary.upper() in ("N/A", "NA"):
            summary = ""
        body_el = field("body")
        body = _http.html_to_md(lhtml.tostring(body_el[0], encoding="unicode")) if body_el else ""
        pdfs = [p for p in (_pdf_href(h) for h in
                            art.xpath(".//div[contains(@class,'field--name-field-judgment-attachment')]//a/@href")) if p]
        sums = [p for p in (_pdf_href(h) for h in
                            art.xpath(".//div[contains(@class,'field--name-field-summary-attachment')]//a/@href")) if p]
        text = ""
        if pdfs:
            p = await _http.get(pdfs[0])
            if p.status_code != 200 or not p.content.startswith(b"%PDF"):
                raise SourceError(_http.error("webopac.ttlawcourts.org", f"judgment PDF failed: {pdfs[0]}",
                                              p.status_code), p.status_code)
            text = _http.pdf_text(p.content)
            if not text:
                raise SourceError(f"Error (ttlawcourts.org): the judgment PDF has no text layer (scanned); "
                                  f"read it at {pdfs[0]}", "no-text")
        else:
            text = (body + "\n\n" if body else "") + "_No judgment file is attached to this entry on the " \
                   "Judiciary website._"
        meta = {}
        if judges:
            meta["Judges"] = "; ".join(judges)
        if pdfs:
            meta["Judgment PDF"] = pdfs[0]
        if sums:
            meta["Summary PDF"] = sums[0]
        if body and pdfs:
            meta["Note"] = _http.clean(body)[:300]
        d = Decision(id=slug, title=title or f"{_court(num)} {num}".strip(), text=text, url=url,
                     court=_court(num), date=_iso(tm[0]) if tm else "", case_number=num,
                     summary=summary, metadata=meta)
        return _http.lru_put(_decisions, slug, d, 16)

    # ------------------------------------------------------------------ #
    # Legislation
    # ------------------------------------------------------------------ #
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        q = (query or "").strip()
        f = {k: str(v).strip() for k, v in (filters or {}).items() if str(v).strip()}
        limit = max(1, int(limit))
        start = (max(1, int(page)) - 1) * limit
        this_year = int(_http.today()[:4])
        if "year" in f:
            if not re.fullmatch(r"\d{4}", f["year"]) or not FIRST_YEAR <= int(f["year"]) <= this_year:
                raise BadRequest(f"year must be a year from {FIRST_YEAR} to {this_year}, e.g. 2021.")
            hits = [self._passed_hit(x) for x in await _year_rows(int(f["year"]))
                    if q.lower() in x["title"].lower() or q.lower() in x["ref"].lower()]
            return Results(items=hits[start:start + limit], total=len(hits),
                           note=f"Acts of {f['year']} as passed (Gazette Legal Supplement copies on laws.gov.tt), "
                                "newest number first; not consolidated.")
        if len(q) < 2:
            raise BadRequest("Give at least two letters of the Act's short title, e.g. 'Interpretation', "
                             "or filter year=YYYY to list one year's Acts.")
        hits = await self._dll_titles(q)
        widened = ""
        ql = q.lower()
        for row in await _recent_rows():
            # chaptered updates are reached through their revised-Act record
            if not row["chapter"] and ql in row["title"].lower():
                hits.append(LawHit(id=f"u{row['doc']}", title=f"{row['title']} Act", type="Act",
                                   number=row["ref"], status="unofficial update",
                                   url=f"{DLL_BASE}/download/{row['doc']}?type=amendment"))
        for year in range(this_year, SCAN_FROM - 1, -1):
            hits += [self._passed_hit(x) for x in await _year_rows(year) if ql in x["title"].lower()]
        if not hits and " " in q:
            seen = set()
            for w in (w for w in q.split() if len(w) >= 4):
                hits += [h for h in await self._dll_titles(w) if h.id not in seen and not seen.add(h.id)]
            if hits:
                widened = (f"No Act title contains all of '{q}'; showing titles containing any one of its "
                           "words (check they fit). ")
        return Results(items=hits[start:start + limit], total=len(hits),
                       note=widened + ("Title search only. Revised Laws to 31 Dec 2016, later unofficial updates, and "
                             f"Acts as passed {SCAN_FROM}-{this_year}; filter year=YYYY for earlier years."))

    @staticmethod
    async def _dll_titles(term: str) -> list[LawHit]:
        r = await _dll_get(f"{DLL_BASE}/list?" + urlencode({"offset": 0, "q": term}), "title search failed")
        doc = lhtml.fromstring(r.text)
        out = []
        for a in doc.xpath("//a[contains(@href,'#email-content') and contains(@href,'currentid=')]"):
            cid = re.search(r"currentid=(\d+)", a.get("href"))[1]
            parts = [_http.clean(x) for x in a.itertext() if _http.clean(x)]
            if not parts:
                continue
            title, chap_txt = parts[0], " ".join(parts[1:])
            chap = _chap(chap_txt)
            status = "repealed" if "repealed" in chap_txt.lower() else ""
            out.append(LawHit(id=cid, title=f"{title} Act" if not title.endswith(("Act", "Ordinance")) else title,
                               type="Act", number=f"Chap. {chap}" if chap else chap_txt, status=status,
                               snippet="" if re.fullmatch(r"Chapter [\d:A-Z]+", chap_txt) else chap_txt, url=f"{DLL_BASE}/list?currentid={cid}"))
        return out

    @staticmethod
    def _passed_hit(x: dict) -> LawHit:
        return LawHit(id=f"u{x['doc']}", title=x["title"] or x["ref"], type="Act", number=x["ref"],
                      date="", status="as passed", url=f"{DLL_BASE}/download/{x['doc']}?type=amendment")

    async def _law(self, id) -> dict:
        lid = (id or "").strip()
        m = re.fullmatch(r"(?i)(u)?(\d{1,7})", lid)
        if not m:
            raise BadRequest("Use a law id from search_legislation: a record number such as '524' "
                             "(Interpretation Act) or 'u119113' for an Act known only as an unofficial update.")
        lid = (m[1] or "").lower() + m[2]
        if lid in _laws:
            return _laws[lid]
        meta: dict[str, str] = {}
        if m[1]:
            pdf_url = f"{DLL_BASE}/download/{m[2]}?type=amendment"
            page_url = pdf_url
            chapter, as_of, title = "", "", ""
            row = next((x for x in await _recent_rows() if x["doc"] == m[2]), None)
            if row is not None:
                title, chapter = f"{row['title']} Act", row["chapter"]
                meta["Reference"] = row["ref"]
                meta["Version"] = "Unofficial update (Recent Updates of Acts)"
            else:
                # an Act as passed from the Chronological List; title from the cached list or the PDF
                row = _cached_year_row(m[2])
                if row is not None:
                    title = row["title"]
                    meta["Reference"] = row["ref"]
                meta["Version"] = "Act as passed (Legal Supplement Part A to the Gazette), not consolidated"
        else:
            page_url = f"{DLL_BASE}/list?currentid={lid}"
            r = await _http.get(page_url)
            if r.status_code == 500 and "error has occurred" in r.text:
                raise NotFound(f"No Act record {lid} in the Digital Legislative Library.")
            if r.status_code != 200:
                raise SourceError(_http.error("laws.gov.tt", "Act record failed", r.status_code), r.status_code)
            d = _detail(r.text, lid)
            title, chapter = d["title"], d["chapter"]
            if not title.endswith(("Act", "Ordinance")):
                title += " Act"
            meta.update({k: v for k, v in d["facts"].items()})
            if chapter:
                meta["Chapter"] = chapter
            if d["long_title"]:
                meta["Long title"] = d["long_title"]
            upd = next((x for x in await _recent_rows() if chapter and x["chapter"] == chapter), None)
            if upd:
                pdf_url = f"{DLL_BASE}/download/{upd['doc']}?type=amendment"
                meta["Version"] = "Unofficial update (Recent Updates of Acts), newer than the 2016 revision"
                as_of = ""
            elif d["versions"]:
                v = d["versions"][0]
                pdf_url = f"{DLL_BASE}/download/{v['doc']}?type=act"
                meta["Version"] = v["label"]
                m2 = re.search(r"as at (\w+) (\d+)\w* (\d{4})", v["label"])
                as_of = _http.en_date(f"{m2[1]} {m2[2]}, {m2[3]}") if m2 else ""
            else:
                raise NotFound(f"Act record {lid} ({title}) has no downloadable version.")
        p = await _http.get(pdf_url)
        if m[1] and (p.status_code in (404, 500) or (p.status_code == 200 and not p.content.startswith(b"%PDF"))):
            raise NotFound(f"No Act PDF {lid} in the Digital Legislative Library.")
        if p.status_code != 200 or not p.content.startswith(b"%PDF"):
            raise SourceError(_http.error("laws.gov.tt", f"Act PDF failed: {pdf_url}", p.status_code), p.status_code)
        raw = _http.pdf_text(p.content)
        if not raw:
            raise SourceError(f"Error (laws.gov.tt): the Act PDF has no text layer; read it at {pdf_url}", "no-text")
        if not as_of:
            m2 = re.search(r"UPDATED TO (\w+ \d+)\w* (\d{4})", raw)
            as_of = _http.en_date(f"{m2[1]}, {m2[2]}") if m2 else ""
        if not title:
            t = re.search(r"(?s)may be cited as the (.+?Act)\b", raw)
            title = _http.clean(t[1]) if t else ""
        if "Reference" not in meta:
            n = re.search(r"Act No\. (\d+) of (\d{4})", raw)
            if n:
                meta["Reference"] = f"No. {n[1]} of {n[2]}"
        title = title or meta.get("Reference", "") or f"Act PDF {lid}"
        meta["PDF"] = pdf_url
        toc, sections, full = _split(raw)
        if not toc and m[1]:
            toc, sections = _split_plain(raw)
        if re.search(r"Note on Schedule\s+The Constitution .{0,80}published\s+independently", raw, re.S):
            # Chap. 1:01 only enacts the Constitution; its text is a separate record, not the Schedule
            note = ("[Note: this Act only enacts the Constitution. The Constitution (fundamental rights in "
                    "ss. 4-5 etc.) is a separate record: search_legislation 'Constitution', "
                    "'THE CONSTITUTION Act' No. 4 of 1976, id 'u120718'. The Schedule here is not the "
                    "Constitution.]\n\n")
            sections = {k: note + v for k, v in sections.items()}
            full = note + full
        if chapter:
            title = f"{title}, Chap. {chapter}"
        law = {"id": lid, "title": title, "url": page_url, "pdf": pdf_url, "toc": toc,
               "sections": sections, "text": full, "as_of": as_of, "meta": meta}
        return _http.lru_put(_laws, lid, law, 8)

    async def get_legislation_toc(self, id):
        law = await self._law(id)
        entries = law["toc"] or [TocEntry(title="(no Arrangement of Sections found; use get_legislation_text)")]
        return Toc(id=law["id"], title=law["title"], url=law["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        law = await self._law(id)
        label = _norm_prov(provision)
        if label not in law["sections"]:
            if not law["sections"]:
                raise NotFound(f"{law['title']}: sections could not be separated in this PDF; "
                               f"use get_legislation_text.")
            raise NotFound(f"{law['title']} has no section '{provision}'. "
                           f"Use get_legislation_toc for the labels.")
        return Provision(law_id=law["id"], law_title=law["title"], provision=label,
                         text=law["sections"][label], url=law["pdf"], as_of=law["as_of"])

    async def get_legislation_text(self, id):
        law = await self._law(id)
        return LawText(id=law["id"], title=law["title"], text=law["text"], url=law["url"],
                       as_of=law["as_of"], metadata=law["meta"])
