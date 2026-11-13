"""Jordan: Constitutional Court (المحكمة الدستورية) judgments and interpretive decisions
from the court's own site, www.cco.gov.jo.

Gotchas this code encodes (verified 2026-11-06 from a UK IP):
  * The court has two structured lists (ASP.NET WebForms): /ar/custompages/provisions
    (judgments on constitutional challenges, الأحكام) and /ar/custompages/decisions
    (interpretations of the Constitution, قرارات التفسير). Each has a search form (full
    text, title, summary, number, year) that is a postback carrying __VIEWSTATE /
    __EVENTVALIDATION; paging is another postback on the pager links (10 cards per page).
    The pager shows a window of page numbers plus "..." links, so reaching page n can
    take a few postbacks.
  * Detail pages are /ar/custompages/ProvisionDetails/<n> and DecisionDetails/<n>; the
    two number spaces overlap, so the id keeps the page name ("ProvisionDetails/1003").
    The full text is HTML in #provisionBriefContent / #decisionBriefContent.
  * The judgment date is only in the text, in words: "الموافق لليوم الثالث من شهر حزيران
    لعام 2026 ميلادي" (Levantine month names). The list cards only carry the year.
  * The older document library (/AR/List/أحكام_المحكمة_) links PDFs whose text layer is
    in a broken legacy font encoding (garbled Arabic): not used.
  * Legislation: the Legislation and Opinion Bureau (lob.gov.jo) API refuses plain
    requests (403) and only answers requests encrypted with a key handshake done by its
    own JavaScript client; not used.
  * 2026-11-10: www.cco.gov.jo and cco.gov.jo time out at TCP connect on ports 80 and 443
    (several tries, http and https, www and bare). The same IP (193.188.64.57) also hosts
    moj.gov.jo and jc.jo, which time out too; lob.gov.jo (another IP) answers. So the shared
    government web front is down or drops UK traffic; we cannot tell which from here. No
    moved site found. Code unchanged; it works again when the host answers.
"""
from __future__ import annotations

import re
from html import unescape

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, Results

HOST = "https://www.cco.gov.jo"
LIST = {"judgment": f"{HOST}/ar/custompages/provisions",
        "interpretation": f"{HOST}/ar/custompages/decisions"}
DETAIL = {"judgment": "ProvisionDetails", "interpretation": "DecisionDetails"}
KIND_OF = {v.lower(): k for k, v in DETAIL.items()}
COURT = "المحكمة الدستورية"
PAGE_SIZE = 10

_ID = re.compile(r"(ProvisionDetails|DecisionDetails)/(\d+)", re.I)
_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")

# Levantine (and Egyptian-style) month names used in Jordanian judgments.
_MONTHS = {"كانون الثاني": 1, "شباط": 2, "اذار": 3, "نيسان": 4, "ايار": 5, "حزيران": 6,
           "تموز": 7, "اب": 8, "ايلول": 9, "تشرين الاول": 10, "تشرين الثاني": 11,
           "كانون الاول": 12, "يناير": 1, "فبراير": 2, "مارس": 3, "ابريل": 4, "مايو": 5,
           "يونيو": 6, "يوليو": 7, "اغسطس": 8, "سبتمبر": 9, "اكتوبر": 10, "نوفمبر": 11,
           "ديسمبر": 12}
_UNITS = {"الاول": 1, "الحادي": 1, "الثاني": 2, "الثالث": 3, "الرابع": 4, "الخامس": 5,
          "السادس": 6, "السابع": 7, "الثامن": 8, "التاسع": 9, "العاشر": 10}
_TENS = {"العشرين": 20, "الثلاثين": 30}


# --------------------------------------------------------------------------- #
# Text helpers (Arabic)
# --------------------------------------------------------------------------- #
def _norm(s: str) -> str:
    """For matching only: no tatweel / harakat, unified alif, Western digits, one space."""
    s = (s or "").translate(_DIGITS).replace("ـ", "")
    s = re.sub("[ً-ْ]", "", s)
    s = re.sub("[أإآ]", "ا", s)
    return re.sub(r"\s+", " ", s).strip()


def _ordinal_day(words: str) -> int:
    """'الثالث' -> 3, 'الحادي عشر' -> 11, 'الخامس والعشرين' -> 25, 'الثلاثين' -> 30."""
    w = _norm(words).split()
    if not w:
        return 0
    if w[0] in _TENS:
        return _TENS[w[0]]
    unit = _UNITS.get(w[0], 0)
    if len(w) >= 2 and w[1] in ("عشر", "عشرة"):
        return 10 + unit
    if len(w) >= 2 and w[1].startswith("و") and w[1][1:] in _TENS:
        return _TENS[w[1][1:]] + unit
    return unit


def _judgment_date(text: str) -> str:
    """Gregorian date of the judgment from its closing lines; '' if not found."""
    t = _norm(text)
    # "الموافق لليوم الثالث من شهر حزيران لعام 2026 ميلادي"
    for m in re.finditer(r"(?:اليوم|لليوم|يوم)\s+(\S+(?:\s+(?:عشر|عشره|و\S+))?)\s+من\s+(?:شهر\s+)?"
                         r"(\S+(?:\s+(?:الاول|الثاني))?)\s+(?:لعام|لسنه|عام|سنه)\s+\(?(\d{4})\)?\s*(?:م\b|ميلادي)", t):
        day, month = _ordinal_day(m[1]), _MONTHS.get(m[2])
        if 1 <= day <= 31 and month:
            return f"{m[3]}-{month:02d}-{day:02d}"
    # "الموافق 3/6/2026 م" or "3 حزيران 2026 م"
    m = re.search(r"الموافق\s+(?:ل\S*\s+)?(\d{1,2})\s*/\s*(\d{1,2})\s*/\s*(\d{4})", t)
    if m:
        return f"{m[3]}-{int(m[2]):02d}-{int(m[1]):02d}"
    m = re.search(r"الموافق\s+(?:ل\S*\s+)?(\d{1,2})\s+(\S+(?:\s+(?:الاول|الثاني))?)\s+(?:لعام\s+|عام\s+)?(\d{4})", t)
    if m and _MONTHS.get(m[2]):
        return f"{m[3]}-{_MONTHS[m[2]]:02d}-{int(m[1]):02d}"
    return ""


def _case_number(title: str) -> str:
    """'الحكم رقم (5) لسنة (2026)' -> '5/2026'."""
    m = re.search(r"رقم\s*\(?\s*(\d+)\s*\)?\s*لسن[ةه]\s*\(?\s*(\d{4})", _norm(title))
    return f"{m[1]}/{m[2]}" if m else ""


# --------------------------------------------------------------------------- #
# ASP.NET list pages
# --------------------------------------------------------------------------- #
def _form(html: str) -> dict:
    """The postback fields the browser would send back: hidden fields, the page's own
    text inputs and selects (current values)."""
    d = {m[1]: unescape(m[2]) for m in
         re.finditer(r'<input type="hidden" name="([^"]+)" id="[^"]*" value="([^"]*)"', html)}
    for m in re.finditer(r'<input name="(ctl00\$MainContent\$[^"]+)" type="text"([^>]*)>', html):
        v = re.search(r'value="([^"]*)"', m[2])
        d[m[1]] = unescape(v[1]) if v else ""
    for m in re.finditer(r'<select name="(ctl00\$MainContent\$[^"]+)"(.*?)</select>', html, re.S):
        v = re.search(r'<option selected="selected" value="([^"]*)"', m[2])
        d[m[1]] = unescape(v[1]) if v else ""
    d["__EVENTTARGET"] = d["__EVENTARGUMENT"] = ""
    return d


def _pages(html: str) -> tuple[int, int]:
    m = re.search(r"صفحة\s+(\d+)\s+من\s+(\d+)", html)
    return (int(m[1]), int(m[2])) if m else (1, 1)


def _pager_links(html: str) -> list[tuple[str, str]]:
    """(label, event target) of the upper pager's links, in order."""
    i = html.find('id="MainContent_pagerList"')
    if i < 0:
        return []
    seg = html[i:html.find("</span>", html.find('class="CurrentPageClass', i) + 1) + 4000]
    seg = seg[:seg.find("pager-next-rev", seg.find("CurrentPageClass")) + 200]
    return [(unescape(lbl).strip(), tgt) for tgt, lbl in
            re.findall(r"__doPostBack\(&#39;([^&]+)&#39;,&#39;&#39;\)\">([^<]*)</a>", seg)]


def _cards(html: str, kind: str) -> list[dict]:
    i = html.find("d-none d-md-block", html.find("MainContent_pnlSearch"))
    j = html.find('id="MainContent_divPager"', i)
    seg = html[i:j if j > 0 else None]
    out = []
    for chunk in seg.split('class="card h-100')[1:]:
        m = re.search(rf"href='({DETAIL[kind]}/\d+)[?']", chunk, re.I)
        if not m:
            continue
        fields = {}
        for k, v in re.findall(r'font-bold">([^<]+)</div>\s*<div class="col-8[^"]*">(.*?)</div>', chunk, re.S):
            fields[_http.clean(unescape(k))] = _http.clean(unescape(re.sub(r"<[^>]+>", " ", v)))
        pdf = re.search(r"href='(/ebv4\.0/[^']+\.pdf)'", chunk, re.I)
        out.append({"id": m[1], "fields": fields, "pdf": HOST + pdf[1] if pdf else ""})
    return out


async def _post(url: str, data: dict) -> str:
    r = await _http.post(url, data=data, headers={"Referer": url})
    if r.status_code != 200:
        raise SourceError(_http.error("CCO", f"POST {url}", r.status_code), r.status_code)
    return r.text


async def _site_page(kind: str, search: dict, n: int) -> tuple[list[dict], int]:
    """Cards on page n (1-based) of the list filtered by `search`, plus the page count."""
    url = LIST[kind]
    r = await _http.get(url)
    if r.status_code != 200:
        raise SourceError(_http.error("CCO", f"GET {url}", r.status_code), r.status_code)
    html = r.text
    if search:
        data = _form(html)
        data.update(search)
        data["ctl00$MainContent$btnSearch"] = "بحث"
        html = await _post(url, data)
    for _ in range(25):
        cur, last = _pages(html)
        if n > last:
            return [], last
        if cur == n:
            return _cards(html, kind), last
        links = _pager_links(html)
        target = next((t for lbl, t in links if lbl == str(n)), "")
        if not target:
            nums = [int(lbl) for lbl, _ in links if lbl.isdigit()]
            dots = [t for lbl, t in links if lbl == "..."]
            if not dots:
                break
            target = dots[-1] if not nums or n > max(nums) else dots[0]
        data = _form(html)
        data["__EVENTTARGET"] = target
        html = await _post(url, data)
    raise SourceError(f"CCO pager did not reach page {n} (layout changed?)")


def _check_id(id: str) -> tuple[str, str]:
    m = _ID.search(id or "")
    if not m:
        raise BadRequest(f"Bad CCO id {id!r}: expected 'ProvisionDetails/<n>' (a judgment) or "
                         "'DecisionDetails/<n>' (an interpretive decision), as search_caselaw returns.")
    page = DETAIL[KIND_OF[m[1].lower()]]
    return f"{page}/{m[2]}", KIND_OF[m[1].lower()]


class Jordan(Jurisdiction):
    code = "jo"
    name = "Jordan"
    languages = ("ar",)
    aliases = ("jordan", "الأردن", "المملكة الأردنية الهاشمية", "hashemite kingdom of jordan")
    sources = (
        Source("Constitutional Court of Jordan (المحكمة الدستورية), cco.gov.jo",
               HOST, covers=("caselaw",),
               licence="Site copyright notice: content owned by the Constitutional Court (Copyright "
                       "Law 22/1992); downloading, viewing and printing allowed for personal or "
                       "in-house, non-commercial use; small parts may be republished unmodified "
                       "with the source named; other uses need the court's permission.",
               commercial_use=False, ai_use=None, auth="none",
               rate_limit="unknown; 1 s spacing, no 429 seen in ~30 requests (2026-11)",
               terms_url=f"{HOST}/AR/Pages/حقوق_النشر",
               warning="Constitutional Court terms: personal or in-house non-commercial use only; "
                       "cite 'المحكمة الدستورية' as the source and quote the text unmodified."),
    )
    caselaw_filters = {
        "kind": "judgment (default: rulings on constitutional challenges) | interpretation "
                "(interpretive decisions on the Constitution)",
        "year": "year of the judgment / decision (YYYY)",
        "number": "judgment / decision number within its year, e.g. 5",
        "title": "words in the title",
        "summary": "words in the court's summary",
    }
    min_interval = {"www.cco.gov.jo": 1.0}
    notes = ("Arabic. Constitutional Court judgments and interpretive decisions (2013 on) from "
             "cco.gov.jo. No official free source for Court of Cassation case law; legislation "
             "(lob.gov.jo) not available: its API needs an encrypted browser handshake.")
    gaps = (
        "Legislation (Legislation and Opinion Bureau, lob.gov.jo): blocks our client (API needs an encrypted JS handshake); needs permission",
        "Court of Cassation and ordinary-court case law: not published online (no official free source)",
        "Older Constitutional Court PDF library: text layer garbled (legacy font encoding), not used",
        ("cco.gov.jo unreachable since 2026-11-10 (TCP connect timeout, also moj.gov.jo and jc.jo on "
         "the same host): outage or block of UK traffic; case law unavailable while it lasts"),
    )
    samples = {
        "caselaw_query": "الدستور",
        "decision_id": "ProvisionDetails/1003",
    }

    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        kind = (filters.get("kind") or "judgment").strip().lower()
        if kind not in LIST:
            raise BadRequest("kind must be 'judgment' or 'interpretation'")
        search = {}
        for key, field in (("year", "txtFilterYear"), ("number", "txtFilterRulingNumber")):
            v = str(filters.get(key, "") or "").strip()
            if v and not v.isdigit():
                raise BadRequest(f"{key} must be a whole number, got {v!r}")
            if v:
                search[f"ctl00$MainContent${field}"] = v
        for key, field in (("title", "txtFilterTitle"), ("summary", "txtFilterSummary")):
            v = _http.clean(filters.get(key, ""))
            if v:
                search[f"ctl00$MainContent${field}"] = v
        q = _http.clean(query)
        if q:
            search["ctl00$MainContent$txtSearch"] = q
        limit, page = max(1, min(int(limit), 50)), max(1, int(page))
        start = (page - 1) * limit
        first = start // PAGE_SIZE + 1
        cards, last = await _site_page(kind, search, first)
        skip = start - (first - 1) * PAGE_SIZE
        cards = cards[skip:]
        n = first
        while len(cards) < limit and n < last:
            n += 1
            more, last = await _site_page(kind, search, n)
            cards += more
        hits = []
        for c in cards[:limit]:
            f = c["fields"]
            title = f.get("العنوان") or c["id"]
            snippet = f.get("الملخص", "")
            extra = [f"{k}: {v}" for k, v in f.items()
                     if k not in ("العنوان", "الملخص", "ملف PDF", "رقم الحكم", "رقم القرار", "السنة") and v]
            if extra:
                snippet = (snippet + " | " if snippet else "") + "; ".join(extra)
            hits.append(DecisionHit(id=c["id"], title=title, court=COURT, date="",
                                    case_number=_case_number(title), snippet=snippet,
                                    url=f"{HOST}/ar/custompages/{c['id']}"))
        return Results(hits, None, note=f"Constitutional Court {'judgments' if kind == 'judgment' else 'interpretive decisions'}; "
                                        f"{last} page(s) of {PAGE_SIZE} at the source. Query searches the full "
                                        "text (Arabic). Hits carry no date: get_decision gives it.")

    async def get_decision(self, id):
        did, kind = _check_id(id)
        url = f"{HOST}/ar/custompages/{did}"
        r = await _http.get(url)
        if r.status_code == 404:
            raise NotFound(f"CCO has no {did}")
        if r.status_code != 200:
            raise SourceError(_http.error("CCO", f"GET {url}", r.status_code), r.status_code)
        box = "provisionBriefContent" if kind == "judgment" else "decisionBriefContent"
        i = r.text.find(f'id="{box}"')
        if i < 0:
            raise NotFound(f"CCO has no {did} (no text on its page)")
        body = r.text[r.text.find(">", i) + 1:]
        end = body.find('<div class="row mt-4">')
        body = body[:end if end > 0 else None]
        text = _http.html_to_md(body)
        if len(text) < 100:
            raise NotFound(f"CCO has no text for {did}")
        first = _http.clean(re.sub(r"[*#]", "", text.split("\n\n", 1)[0]))
        title = first if len(first) < 120 else did
        return Decision(id=did, title=title, text=text, url=url, court=COURT,
                        date=_judgment_date(text), case_number=_case_number(title),
                        metadata={"kind": "judgment (حكم)" if kind == "judgment"
                                  else "interpretive decision (قرار تفسير)"})
