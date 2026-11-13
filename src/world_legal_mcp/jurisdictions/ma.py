"""Morocco: Constitutional Court decisions (cour-constitutionnelle.ma) and legislation from
the Ministry of Justice legal portal "Adala" (adala.justice.gov.ma).

Case law: www.cour-constitutionnelle.ma (ASP.NET site of the Constitutional Court).
  * Search: POST /search/get-result (the site's own DataTables endpoint behind /Search):
    form fields searchText, draw, start, length -> JSON {recordsFiltered, data: [{iddecision,
    numerodecision, anneedecision, datedecision}]}, newest first. Searches the decision text.
    An empty searchText lists all decisions (2,158 on 2026-11-06).
  * Decision: GET /Decision?id={iddecision}&Page=Decision; the text is the HTML inside
    `div.decision-content`, the institution is the page's `#decision-detail h2`.
    An unknown id answers HTTP 500 (no 404).
  * Covers three institutions: the Constitutional Chamber of the Supreme Court (1963-1994,
    numbers "N/YYYY"), the Constitutional Council (1994-2017, "YYYY/N") and the
    Constitutional Court (2017-, "N/YY"). Arabic only.

Legislation: adala.justice.gov.ma (Next.js; search is server-rendered).
  * Search: GET /search?term=&resources=&type=&number=&start_date=&end_date=&page=
    -> the page's __NEXT_DATA__ JSON holds pageProps.searchResult {total, data}, 15 per page.
    The term matches titles, numbers and keywords, not the PDF text.
  * Each document is a PDF at /api/{path}; `path` ("uploads/YYYY/MM/DD/<name>-<ms>.pdf") is
    the only identifier the portal has, so it is the id here. When the Ministry uploads a
    new consolidated version the path changes.
  * Texts are text-layer PDFs (Arabic; some French). Articles are "الفصل N" (dahirs, older
    codes) or "المادة N" (modern laws); the TOC is built from those heading lines.
  * `gregorianDate` is sometimes the data-entry timestamp, not the text's date; so
    the date is taken only from the title "صادر في ... (11 سبتمبر 2003)"; no date is shown otherwise.

Verified 2026-11-06 (robots checked 2026-11-05/06):
  * adala.justice.gov.ma/robots.txt: 404 (none); pages carry <meta name="robots"
    content="index, follow">. No terms-of-use page; footer "© 2024 وزارة العدل".
  * www.cour-constitutionnelle.ma/robots.txt: "User-agent: * / Disallow:" (all allowed).
    No terms-of-use page; footer "جميع الحقوق محفوظة 2023" (all rights reserved).
  * Not used: juriscassation.cspj.ma (Court of Cassation) timed out twice (connection
    timeout, 2026-11-05 and 2026-11-06); sgg.gov.ma (Bulletin officiel PDFs, no robots.txt)
    is redundant with Adala's consolidated texts.
"""
from __future__ import annotations

import datetime
import json
import re
from urllib.parse import quote, unquote

import httpx
from lxml import html as lxml_html

from .. import _http
from ..base import AdapterError, BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

CC_HOST = "www.cour-constitutionnelle.ma"
CC = f"https://{CC_HOST}"
AD_HOST = "adala.justice.gov.ma"
AD = f"https://{AD_HOST}"
AD_PAGE = 15                      # Adala's fixed page size
_NEXT = re.compile(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S)
_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
# An article heading line: "الفصل 42", "الفصل42", "المادة 5 مكررة", "المادة الأولى" is not numbered.
_ART = re.compile(r"^(الفصل|المادة)\s*(\d+(?:\s*[-.]\s*\d+)?)\s*((?:مكررة|مكرر)(?:\s*(?:مرتين|ثلاث\s*مرات))?)?"
                  r"\s*[-–:.)(]?\s*(.*)$")
_XREF = re.compile(r"^(من(?!\w)|منه(?!\w)|التي(?!\w)|أعلاه|أدناه|الأعلاه|المشار|المذكور|السالف|المبين|المنصوص|المحدد|المشار)", re.U)
_HEAD = re.compile(r"^(الجزء|الكتاب|القسم|الباب|الفرع|الشعبة)\s+\S+")
_RANK = {"الجزء": 0, "الكتاب": 1, "القسم": 2, "الباب": 3, "الفرع": 4, "الشعبة": 5}
_PAGE_NO = re.compile(r"^[-–\s]*\d+[-–\s]*$")
_search_cache: dict = {}
_pdf_cache: dict = {}


# ---------------------------------------------------------------- case law helpers
def _court(number: str) -> str:
    """Institution from the source's own number format (see module docstring)."""
    n = number.strip()
    if re.fullmatch(r"\d+\s*/\s*\d{2}", n):
        return "المحكمة الدستورية"
    if re.fullmatch(r"(19|20)\d{2}\s*/\s*\d+", n):
        return "المجلس الدستوري"
    if re.fullmatch(r"\d+\s*/\s*(19|20)\d{2}", n):
        return "الغرفة الدستورية بالمجلس الأعلى"
    return ""


def _unreachable(host: str, url: str, e: Exception) -> str:
    """Error naming only the failing site (the generic one lists every source of the country)."""
    return (f"could not reach {host} ({type(e).__name__}: {e or 'no detail'}). "
            f"Try again shortly. Official source: {url}/")


def _cc_url(did: str) -> str:
    return f"{CC}/Decision?id={did}&Page=Decision"


# ---------------------------------------------------------------- legislation helpers
def _ad_url(path: str) -> str:
    return f"{AD}/api/{quote(path)}"


def _law_id(id: str) -> str:
    """The Adala file path; also accepts the PDF URL (encoded or not)."""
    s = unquote(str(id).strip()).split("#")[0]
    m = re.search(r"(uploads/.+\.pdf)$", s, re.I)
    if not m:
        raise BadRequest("Use the id from search_legislation: the Adala file path, e.g. "
                         "'uploads/2026/07/29/ظهير بمثابة قانون الالتزامات والعقود صيغة محينة-1785316295256.pdf', "
                         "or its https://adala.justice.gov.ma/api/uploads/... URL.")
    return m[1]


_AR_MONTHS = {m: i for i, names in enumerate((
    ("يناير", "جانفي"), ("فبراير", "فيفري"), ("مارس",), ("أبريل", "ابريل"), ("ماي", "مايو"),
    ("يونيو", "يونيه", "جوان"), ("يوليوز", "يوليو", "جويلية"), ("غشت", "أغسطس", "اغسطس"),
    ("شتنبر", "سبتمبر"), ("أكتوبر", "اكتوبر"), ("نونبر", "نوفمبر"), ("دجنبر", "ديسمبر")), 1)
    for m in names}
# The text's own date follows its own "صادر في|بتاريخ <hijri> (<gregorian>)"; a cited text is "الصادر في ...",
# so a leading "ال" is skipped. The day is a number, or "فاتح"/"غرة" (the 1st); a stray "(" before the year
# ("(24 يوليو (2015") is tolerated.
_TITLE_DATE = re.compile(r"(ال)?(?:صادر\s+(?:في|بتاريخ)|بتاريخ)\s+[^()]{0,40}?\(\s*(\d{1,2}|فاتح|غرة)\s*("
                         + "|".join(_AR_MONTHS) + r")\s*\(?\s*((?:19|20)\d{2})(?!\d)")


def _title_date(*texts: str) -> str:
    """The text's own Gregorian date from its title, "صادر في 14 رجب 1424 (11 سبتمبر 2003)" -> 2003-09-11,
    else "". Dates of cited texts are ignored."""
    for t in texts:
        t = re.sub(r"[\u200e\u200f\u202a-\u202e]", "", str(t or "")).translate(_DIGITS).replace("\u0640", "")
        for m in _TITLE_DATE.finditer(t):
            if m[1]:
                continue
            try:
                day = 1 if m[2] in ("فاتح", "غرة") else int(m[2])
                return datetime.date(int(m[4]), _AR_MONTHS[m[3]], day).isoformat()
            except ValueError:
                pass
    return ""


def _label(kind: str, num: str, bis: str) -> str:
    bis = " ".join(bis.split())
    return f"{kind} {num} {bis}" if bis else f"{kind} {num}"


def _num(raw: str) -> str:
    """'1- 65', '65 -1', '65.1' -> '65-1' (sub-article: base first; RTL extraction flips the order)."""
    parts = [x for x in re.split(r"\s*[-.]\s*", raw.strip()) if x]
    return "-".join(sorted(parts, key=int, reverse=True)) if len(parts) == 2 else parts[0]


def _unglue(num: str, prev: int | None) -> str:
    """PDF footnote markers stick to article numbers: "الفصل 515" is article 5 + note 15,
    "3831220" is note 383 + article 1220, "1-889295" is article 889-1 + note 295. When the
    number jumps implausibly past the previous article, keep the part that follows it."""
    if prev is None:
        return num
    if "-" in num:      # "a-b" around the base article prev: trim a glued note off either side
        p = str(prev)
        return "-".join(p if x.startswith(p) or x.endswith(p) else x for x in num.split("-"))
    if int(num) <= prev + 50:
        return num
    for i in range(1, len(num)):
        for part in (num[:i], num[-i:]):
            if prev < int(part) <= prev + 5:
                return part
    return num


def _parse(text: str) -> tuple[list[TocEntry], dict[str, str], str]:
    """TOC entries, provision label -> text, and the clean full text."""
    lines = [ln for ln in text.translate(_DIGITS).split("\n") if not _PAGE_NO.match(ln)]
    entries: list[TocEntry] = []
    blocks: dict[str, list[str]] = {}
    current = None
    level = -1                       # level of the innermost heading seen so far
    prev: dict[str, int] = {}
    for ln in lines:
        m = _ART.match(ln.strip())
        # "المادة 53 أعلاه." wrapped onto a line inside another article is a cross-reference, not a heading
        if m and (not m[4] or len(ln) <= 60) and not _XREF.match(m[4] or ""):
            num = _unglue(_num(m[2]), prev.get(m[1]))
            nums = [int(x) for x in num.split("-")]
        else:
            m = None
        if m:
            if nums[0] <= prev.get(m[1], nums[0]) + 50:     # a glued-note number must not become the baseline
                prev[m[1]] = max(nums) if len(nums) == 1 else min(nums, key=lambda x: abs(x - prev.get(m[1], x)))
            label = _label(m[1], num, m[3] or "")
            if label in blocks:            # same number again (annex, second text): keep apart
                i = 2
                while f"{label} ({i})" in blocks:
                    i += 1
                label = f"{label} ({i})"
            entries.append(TocEntry(title=_http.clean(ln), level=level + 1, provision=label))
            blocks[label] = [ln]
            current = label
            continue
        h = _HEAD.match(ln.strip())
        if h and len(ln) <= 80:
            level = _RANK[h[1]]
            entries.append(TocEntry(title=_http.clean(ln), level=level))
            current = None
        if current:
            blocks[current].append(ln)
    full = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
    return entries, {k: "\n".join(v).strip() for k, v in blocks.items()}, full


def _norm_prov(p: str) -> tuple[str, str, str]:
    """('الفصل'|'المادة'|'', number, bis) from a user label."""
    s = _http.clean(str(p)).translate(_DIGITS)
    m = re.match(r"^(?:(الفصل|فصل|المادة|مادة|art(?:icle)?\.?|§)\s*)?(\d+(?:\s*-\s*\d+)?)\s*(.*)$", s, re.I)
    if not m:
        raise BadRequest("Give an article as shown in the TOC, e.g. 'الفصل 230', 'المادة 5', "
                         "'230' or 'art. 230'.")
    kind = {"فصل": "الفصل", "مادة": "المادة"}.get(m[1] or "", m[1] or "")
    if kind not in ("الفصل", "المادة"):
        kind = ""
    rest = re.sub(r"[^\w)]+$", "", m[3].replace("\u0640", ""))
    dup = re.search(r"\(\s*(\d+)\s*\)\s*$", rest)      # duplicate-label suffix "(2)" is part of the label
    rest = re.sub(r"^[\W_]+|[\W_]+$", "", rest[:dup.start()] if dup else rest)
    return kind, _num(m[2]), f"{rest} ({dup[1]})".strip() if dup else rest


class Morocco(Jurisdiction):
    code = "ma"
    name = "Morocco"
    languages = ("ar", "fr")
    aliases = ("morocco", "maroc", "المغرب", "kingdom of morocco", "mar")
    sources = (
        Source(
            name="Constitutional Court of Morocco (cour-constitutionnelle.ma) – Decisions",
            url=f"{CC}/",
            covers=("caselaw",),
            licence="unknown: no terms of use published; footer says 'جميع الحقوق محفوظة' (all rights reserved)",
            commercial_use=None,
            ai_use=None,    # robots.txt allows everything; no AI/TDM clause anywhere on the site
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~15 requests (2026-11-06)",
            terms_url="",
        ),
        Source(
            name="Ministry of Justice legal portal Adala (adala.justice.gov.ma)",
            url=f"{AD}/",
            covers=("legislation",),
            licence="unknown: no terms of use published; footer '© 2024 وزارة العدل'",
            commercial_use=None,
            ai_use=None,    # no robots.txt (404); meta robots "index, follow"; no AI/TDM clause
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~25 requests (2026-11-06)",
            terms_url="",
        ),
    )
    legislation_filters = {
        "resource": "Adala resource id: 1 = legislative and regulatory texts (default), "
                    "681 = treaties, 280 = circulars, 148 = reference documents, 'all' = everything",
        "type": "Adala text-type id, e.g. 13 = ظهير (dahir), 5 = مرسوم (decree), 1 = قانون تنظيمي "
                "(organic law), 7 = قرار (order)",
        "number": "official number, e.g. '1.03.194' or '65.99'",
        "year_from": "YYYY (Gregorian), on or after",
        "year_to": "YYYY (Gregorian), on or before",
    }
    caselaw_filters = {
        "year_from": "YYYY (Gregorian), decisions on or after",
        "year_to": "YYYY (Gregorian), decisions on or before",
    }
    min_interval = {CC_HOST: 1.0, AD_HOST: 1.0}
    notes = ("Case law: Constitutional Court (and its predecessors, 1963-) full text from the "
             "Court's site, Arabic. Legislation: Ministry of Justice 'Adala' portal PDFs "
             "(consolidated codes, Arabic); search matches titles only. Court of Cassation "
             "site unreachable.")
    gaps = (
        "Court of Cassation (juriscassation.cspj.ma, cspj.ma): site down / unreachable (timed out"
         " 2026-11-05 and 2026-11-06)",
        "Courts of appeal and first-instance courts: not researched yet",
        "Bulletin officiel as published (sgg.gov.ma PDFs): source exists and works but not built "
         "yet (Adala's consolidated texts used)",
    )
    samples = {
        "caselaw_query": "النظام الأساسي للقضاة",
        "decision_id": "2074",     # 210/23, 2023-03-07: organic law 14.22 on the statute of judges
        "legislation_query": "الالتزامات والعقود",
        "law_id": "uploads/2026/07/29/ظهير بمثابة قانون الالتزامات والعقود صيغة محينة-1785316295256.pdf",
        "provision": "الفصل 230",
    }

    # ------------------------------------------------------------------ case law
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        f = {k: str(v).strip() for k, v in (filters or {}).items() if str(v).strip()}
        for k in ("year_from", "year_to"):
            if k in f and not re.fullmatch(r"\d{4}", f[k]):
                raise BadRequest(f"{k} must be a year YYYY, got {f[k]!r}.")
        y0, y1 = int(f.get("year_from", 0)), int(f.get("year_to", 9999))
        if y0 > y1:
            raise BadRequest(f"year_from ({y0}) is after year_to ({y1}).")
        limit = max(1, min(int(limit), 50))
        start = (max(1, int(page)) - 1) * limit
        dated = "year_from" in f or "year_to" in f
        # The endpoint cannot filter by date; its rows come newest first, so a year range is cut
        # from the rows read in chunks, stopping once they are older than year_from.
        chunk, pos, rows, total, done = (500 if dated else limit), (0 if dated else start), [], None, False
        while True:
            try:
                r = await _http.post(f"{CC}/search/get-result", data={
                    "searchText": (query or "").strip(), "draw": "1", "start": str(pos), "length": str(chunk)})
            except httpx.HTTPError as e:
                raise AdapterError(_unreachable("cour-constitutionnelle.ma", CC, e))
            if r.status_code != 200:
                raise SourceError(_http.error("cour-constitutionnelle.ma", "search failed", r.status_code), r.status_code)
            try:
                d = r.json()
                got = d["data"]
            except (ValueError, KeyError, TypeError):
                raise SourceError(f"cour-constitutionnelle.ma search: unexpected payload {r.text[:200]}")
            if not dated:
                rows, total = got[:limit], d.get("recordsFiltered")
                break
            for x in got:
                y = int(str(x.get("datedecision") or "0")[:4] or 0)
                if y < y0:
                    done = True
                    break
                if y <= y1:
                    rows.append(x)
            pos += chunk
            if done or len(got) < chunk or len(rows) >= start + limit:
                break
        if dated:
            total = len(rows) if done or len(got) < chunk else None
            rows = rows[start:start + limit]
        items = []
        for x in rows:
            num = _http.clean(x.get("numerodecision") or "")
            court = _court(num)
            did = str(x.get("iddecision"))
            items.append(DecisionHit(
                id=did, title=f"{court or 'قرار'} {num}".strip(), court=court,
                date=str(x.get("datedecision") or "")[:10], case_number=num, url=_cc_url(did)))
        return Results(items=items, total=total,
                       note="Arabic full-text search over Constitutional Court / Council / Chamber decisions (1963-), "
                            "newest first. The site has no date filter; year_from / year_to are applied here "
                            "to the decision date.")

    async def get_decision(self, id):
        m = re.search(r"(?:[?&]id=|^)(\d+)(?:&|$)", str(id).strip())
        if not m:
            raise BadRequest("Use the numeric id from search_caselaw, e.g. '2074', or a "
                             "cour-constitutionnelle.ma/Decision?id=... URL.")
        did = m[1]
        try:
            r = await _http.get(_cc_url(did))
        except httpx.HTTPError as e:
            raise AdapterError(_unreachable("cour-constitutionnelle.ma", CC, e))
        if r.status_code in (404, 500):
            raise NotFound(f"cour-constitutionnelle.ma has no decision with id {did} "
                           f"(the site answers HTTP {r.status_code}).")
        if r.status_code != 200:
            raise SourceError(_http.error("cour-constitutionnelle.ma", "decision failed", r.status_code), r.status_code)
        doc = lxml_html.fromstring(r.text)
        body = doc.xpath('//div[contains(concat(" ", normalize-space(@class), " "), " decision-content ")]')
        if not body:
            raise NotFound(f"cour-constitutionnelle.ma decision {did} has no text on its page.")
        text = _http.html_to_md(lxml_html.tostring(body[0], encoding="unicode"))
        head = doc.xpath('//div[@id="decision-detail"]//h2')
        inst = _http.clean(head[0].text_content()) if head else ""
        spans = [_http.clean(s.text_content()) for s in doc.xpath('//div[contains(@class,"decision-header")]//span')]
        num = date = ""
        for i, s in enumerate(spans[:-1]):
            if s.startswith("قرار رقم"):
                num = spans[i + 1]
            elif s.startswith("تاريخ صدور القرار"):
                date = spans[i + 1].replace("/", "-")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            date = ""
        court = _court(num) or {"قرارات المحكمة الدستورية": "المحكمة الدستورية",
                                "قرارات المجلس الدستوري": "المجلس الدستوري"}.get(inst, "")
        meta = {"Collection": inst} if inst else {}
        return Decision(id=did, title=f"{court or 'قرار'} {num}".strip(), text=text, url=_cc_url(did),
                        court=court, date=date, case_number=num, metadata=meta)

    # ------------------------------------------------------------------ legislation
    async def _ad_search(self, params: dict, page: int) -> dict:
        key = (tuple(sorted(params.items())), page)
        if key in _search_cache:
            return _search_cache[key]
        try:
            r = await _http.get(f"{AD}/search", params={**params, "page": str(page)})
        except httpx.HTTPError as e:
            raise AdapterError(_unreachable("adala.justice.gov.ma", AD, e))
        if r.status_code != 200:
            raise SourceError(_http.error("adala.justice.gov.ma", "search failed", r.status_code), r.status_code)
        m = _NEXT.search(r.text)
        try:
            sr = json.loads(m[1])["props"]["pageProps"]["searchResult"]
            sr = {"total": int(sr.get("total") or 0), "data": list(sr.get("data") or [])}
        except (TypeError, KeyError, ValueError):
            raise SourceError("adala.justice.gov.ma search: page without the expected search data")
        return _http.lru_put(_search_cache, key, sr, 32)

    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        f = {k: str(v).strip() for k, v in (filters or {}).items() if str(v).strip()}
        params = {"term": (query or "").strip()}
        res = f.get("resource", "1")
        if res != "all":
            if not res.isdigit():
                raise BadRequest("resource must be a numeric Adala resource id (e.g. 1) or 'all'.")
            params["resources"] = res
        if "type" in f:
            if not f["type"].isdigit():
                raise BadRequest("type must be a numeric Adala type id, e.g. 13 (ظهير) or 5 (مرسوم).")
            params["type"] = f["type"]
        if "number" in f:
            params["number"] = f["number"]
        for k, p in (("year_from", "start_date"), ("year_to", "end_date")):
            if k in f:
                if not re.fullmatch(r"\d{4}", f[k]):
                    raise BadRequest(f"{k} must be a year YYYY, got {f[k]!r}.")
                params[p] = f[k]
        if "year_from" in f and "year_to" in f and int(f["year_from"]) > int(f["year_to"]):
            raise BadRequest(f"year_from ({f['year_from']}) is after year_to ({f['year_to']}).")
        if not params["term"] and len(params) == 1 + ("resources" in params):
            raise BadRequest("Give a search term or a filter (number, type, year_from/year_to).")

        limit = max(1, min(int(limit), 50))
        start = (max(1, int(page)) - 1) * limit
        rows, total = [], None
        sp = start // AD_PAGE + 1
        while len(rows) < start - (sp - 1) * AD_PAGE + limit:
            sr = await self._ad_search(params, sp + len(rows) // AD_PAGE)
            total = sr["total"]
            rows += sr["data"]
            if len(sr["data"]) < AD_PAGE:
                break
        off = start - (sp - 1) * AD_PAGE
        items = []
        for x in rows[off:off + limit]:
            fm = x.get("fileMeta") or {}
            path = x.get("path") or ""
            if not path:
                continue
            obj = _http.clean(fm.get("object") or "")
            items.append(LawHit(
                id=path, title=_http.clean(x.get("name") or "") or obj or path,
                type=_http.clean((fm.get("LawType") or {}).get("name") or ""),
                number=_http.clean(fm.get("lawNumber") or ""),
                date=_title_date(obj, x.get("name")),
                snippet=obj, url=_ad_url(path)))
        return Results(items=items, total=total,
                       note="Search matches titles, numbers and keywords, not the text. Texts are PDFs "
                            "(Arabic); 'صيغة محينة' = consolidated version. "
                            "Date is shown only when the title states it (the portal's own date field is unreliable).")

    async def _law(self, id: str) -> tuple[str, str, str, list[TocEntry], dict[str, str]]:
        path = _law_id(id)
        hit = _pdf_cache.get(path)
        if hit:
            return hit
        try:
            r = await _http.get(_ad_url(path))
        except httpx.HTTPError as e:
            raise AdapterError(_unreachable("adala.justice.gov.ma", AD, e))
        if r.status_code == 404 or (r.status_code == 200 and not r.content.startswith(b"%PDF")):
            raise NotFound(f"Adala has no file at {path}.")
        if r.status_code != 200:
            raise SourceError(_http.error("adala.justice.gov.ma", "PDF download failed", r.status_code), r.status_code)
        text = _http.pdf_text(r.content)
        if len(text) < 200:
            raise SourceError(f"Adala PDF {path} has no text layer (scanned); no OCR here. Read it at {_ad_url(path)}")
        entries, blocks, full = _parse(text)
        title = _http.clean(re.sub(r"-\d{10,}\.pdf$|\.pdf$", "", path.rsplit("/", 1)[-1]))
        return _http.lru_put(_pdf_cache, path, (path, title, full, entries, blocks), 4)

    async def get_legislation_toc(self, id):
        path, title, _, entries, _ = await self._law(id)
        if not entries:
            entries = [TocEntry(title="(no article headings found; use get_legislation_text)", level=0)]
        return Toc(id=path, title=title, url=_ad_url(path), entries=entries)

    async def get_legislation_provision(self, id, provision):
        path, title, _, _, blocks = await self._law(id)
        raw = _http.clean(str(provision)).translate(_DIGITS)
        if raw in blocks:
            label = raw
        else:
            kind, num, rest = _norm_prov(raw)
            cands = [k for k in blocks if re.fullmatch(
                rf"({kind or 'الفصل|المادة'}) {re.escape(num)}" + (rf" {re.escape(rest)}" if rest else ""), k)]
            if not cands:
                raise NotFound(f"No article {raw!r} in {title}. Use get_legislation_toc for the labels.")
            label = cands[0]
        body = blocks[label].split("\n")
        head = _ART.match(body[0].strip())          # text on the heading line itself belongs to the article
        text = f"**{label}**\n\n" + "\n".join(([head[4]] if head and head[4] else []) + body[1:])
        return Provision(law_id=path, law_title=title, provision=label, text=text.strip(), url=_ad_url(path))

    async def get_legislation_text(self, id):
        path, title, full, _, _ = await self._law(id)
        return LawText(id=path, title=title, text=full, url=_ad_url(path),
                       metadata={"Format": "PDF text layer (Adala)"})
