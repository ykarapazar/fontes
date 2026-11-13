"""Taiwan (ROC): case law from the Judicial Yuan 裁判書查詢 (FJUD); statute texts from the
MOJ 全國法規資料庫 (law.moj.gov.tw). Traditional Chinese, untranslated.

Gotchas this code encodes:
  * law.moj.gov.tw robots.txt (2026-11-05) is `Disallow: /` with only
    /LawClass/LawAll.aspx, /News/NewsDetail.aspx and the sitemap allowed. So the open-data
    API (/api/...), LawSingle.aspx, the search pages and the English site are all off
    limits: there is no search_legislation. Laws are opened by their pcode
    (B0000001 = 民法) and articles are cut out of the one LawAll.aspx page.
    A bad pcode 302-redirects to /ErrorPage.aspx (disallowed too), so redirects are
    not followed there.
  * FJUD keyword search is an ASP.NET form: GET default.aspx for the __VIEWSTATE, POST it
    with txtKW, read the query hash `q` and total from the answer, then page
    qryresultlst.aspx?q=...&page=n (20 rows per page). No cookie needed.
  * FJUD's own id is "<court code>,<ROC year>,<字別>,<number>,<YYYYMMDD>[,<seq>]", e.g.
    "TPSV,95,台上,1,20060105" (seq is optional); data.aspx?ty=JD&id=<that> is the full text.
    Recent decisions are HTML (<div class="htmlcontent">), older ones a <pre>-style block.
  * Dates on FJUD and MOJ are ROC (民國) years: +1911.
  * Constitutional Court (cons.judicial.gov.tw), JY open data (opendata/data.judicial.gov.tw)
    and lawsearch/legal.judicial.gov.tw timed out (TCP) from the UK on 2026-11-05.
"""
from __future__ import annotations

import re
import unicodedata
from urllib.parse import quote, unquote

from lxml import html as lhtml

from .._http import clean, get, html_to_md, lru_put, post
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, LawText, Provision, Results, Toc, TocEntry

FJUD = "https://judgment.judicial.gov.tw/FJUD"
MOJ = "https://law.moj.gov.tw"
LAW_URL = MOJ + "/LawClass/LawAll.aspx?pcode={pcode}"
_ROWS = 20  # FJUD rows per result page
_MAX_HITS = 500  # FJUD serves only result pages 1-25
_MAX_LIMIT = 100  # up to 6 source pages at 1 s spacing

_PCODE = re.compile(r"^[A-Z]\d{7}$")
_JID = re.compile(r"^[A-Z]{3,5},\d{1,3},[^,]+,\d+,\d{8}(?:,\d+)?$")

# FJUD advanced-search court codes (Default_AD.aspx jud_court); a raw code is accepted too.
_COURTS = {
    "supreme": "TPS",         # 最高法院
    "supreme_admin": "TPA",   # 最高行政法院
    "high": "TPH",            # 臺灣高等法院
    "ip": "IPC",              # 智慧財產及商業法院
    "disciplinary": "TPP",    # 懲戒法院
}
_COURT_NAMES = {  # Chinese names a lawyer types -> the same keys
    "最高法院": "supreme", "最高行政法院": "supreme_admin", "臺灣高等法院": "high",
    "台灣高等法院": "high", "高等法院": "high", "智慧財產及商業法院": "ip",
    "智慧財產法院": "ip", "懲戒法院": "disciplinary",
}

_AMEND_NOTE = ("NOTE: this is the 1947 base text of the Constitution only. It is amended by the "
               "中華民國憲法增修條文 (pcode A0000002), which is not part of this text: 增修條文第1條 "
               "suspends 憲法第25條至第34條 and 第135條 (e.g. Art. 27, National Assembly powers). "
               "Read A0000002 for the operative law.")

_laws: dict[str, "_Law"] = {}
_queries: dict[str, tuple[str, int | None]] = {}


def _roc(s: str) -> str:
    """'115.11.05' or '民國 115 年 11 月 05 日' -> '2026-11-05'; else ''."""
    m = re.search(r"(\d{2,3})\D+?(\d{1,2})\D+?(\d{1,2})", s or "")
    return f"{int(m[1]) + 1911}-{int(m[2]):02d}-{int(m[3]):02d}" if m else ""


def _nfkc(s: str) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", s or ""))


# =========================================================================== #
# Case law: FJUD
# =========================================================================== #
def _decision_id(id: str) -> str:
    s = unquote((id or "").strip())
    m = re.search(r"[?&]id=([^&]+)", s)
    if m:
        s = unquote(m[1])
    s = re.sub(r"\s*,\s*", ",", s)
    if not _JID.match(s):
        raise BadRequest(f"bad FJUD id {id!r}. Use the id from search_caselaw, e.g. "
                         "'TPSV,95,台上,1,20060105' (court,ROC year,字別,number,date[,seq]).")
    return s


def _decision_url(jid: str) -> str:
    return f"{FJUD}/data.aspx?ty=JD&id={quote(jid, safe='')}"


def _split_title(title: str) -> tuple[str, str]:
    """'臺灣士林地方法院 115 年度訴字第 1652 號民事判決' -> (court, '115年度訴字第1652號')."""
    t = clean(title)
    m = re.match(r"^(.*?)\s*(\d+\s*年度.*?號)", t)
    if not m:
        return "", ""
    return m[1].strip(), re.sub(r"\s+", "", m[2])


async def _query_hash(query: str, court: str = "") -> tuple[str, int | None]:
    key = f"{court}|{query}" if court else query
    if key in _queries:
        return _queries[key]
    r = await get(f"{FJUD}/{'Default_AD' if court else 'default'}.aspx")
    if r.status_code != 200:
        raise SourceError("FJUD search form failed", r.status_code)
    form = {k: v for k, v in re.findall(r'name="(__[A-Z]+)" id="[^"]+" value="([^"]*)"', r.text)}
    if "__VIEWSTATE" not in form:
        raise SourceError("FJUD search form changed (no __VIEWSTATE)")
    if court:
        form.update({"jud_kw": query, "jud_court": court, "judtype": "JUDBOOK", "whosub": "0",
                     "ctl00$cp_content$btnQry": "送出查詢"})
    else:
        form.update({"txtKW": query, "judtype": "JUDBOOK", "whosub": "0",
                     "ctl00$cp_content$btnSimpleQry": "送出查詢"})
    r = await post(f"{FJUD}/{'Default_AD' if court else 'default'}.aspx", data=form)
    if r.status_code != 200:
        raise SourceError("FJUD search failed", r.status_code)
    m = re.search(r'qryresultlst\.aspx\?ty=JUDBOOK&(?:amp;)?q=([0-9a-f]+)"[^>]*>.*?'
                  r'<span class="badge">([\d,]*)</span>', r.text, re.S)
    if not m:
        if re.search(r"查無資料|無符合", r.text):
            return "", 0
        raise SourceError("FJUD search answered without a result list (query rejected?)")
    total = int(m[2].replace(",", "")) if m[2] else None
    return lru_put(_queries, key, (m[1], total), 64)


async def _result_page(q: str, n: int) -> list[DecisionHit]:
    r = await get(f"{FJUD}/qryresultlst.aspx", params={"ty": "JUDBOOK", "q": q, "sort": "DS",
                                                      "page": n})
    if r.status_code != 200:
        raise SourceError("FJUD result list failed", r.status_code)
    doc = lhtml.fromstring(r.text)
    table = doc.find('.//table[@id="jud"]')
    if table is None:
        return []
    hits: list[DecisionHit] = []
    for tr in table.findall("tr"):
        a = tr.find('.//a[@id="hlTitle"]')
        if a is not None:
            m = re.search(r"[?&]id=([^&]+)", a.get("href", ""))
            if not m:
                continue
            jid = unquote(m[1])
            tds = tr.findall("td")
            title = clean(a.text_content())
            court, num = _split_title(title)
            hits.append(DecisionHit(
                id=jid, title=title, court=court, case_number=num,
                date=_roc(tds[2].text_content()) if len(tds) > 2 else "",
                url=_decision_url(jid),
                snippet=clean(tds[3].text_content()) if len(tds) > 3 else ""))
        elif "summary" in (tr.get("class") or "") and hits:
            cause = hits[-1].snippet
            body = clean(tr.text_content())
            hits[-1].snippet = f"{cause}: {body}" if cause else body
    return hits


def _content_md(td) -> str:
    """Judgment body: HTML paragraphs, or a preformatted block (older judgments).

    The preformatted text is hard-wrapped at a fixed width, so its source lines are kept
    as lines (one markdown paragraph), not turned into paragraphs.
    """
    for bad in td.xpath(".//script|.//style"):
        bad.drop_tree()
    rich = td.find('.//div[@class="htmlcontent"]')
    if rich is not None and clean(rich.text_content()):
        return html_to_md(lhtml.tostring(rich, encoding="unicode"))
    pre = td.xpath('.//div[contains(@class, "text-pre")]')
    raw = (pre[0] if pre else td).text_content().replace("\r", "")
    lines = [clean(ln) for ln in raw.split("\n")]
    return "\n".join(ln for ln in lines if ln)


# =========================================================================== #
# Legislation: MOJ LawAll.aspx
# =========================================================================== #
class _Law:
    def __init__(self, pcode: str, page: str):
        doc = lhtml.fromstring(page)
        self.pcode = pcode
        self.url = LAW_URL.format(pcode=pcode)
        name = doc.find('.//a[@id="hlLawName"]')
        if name is None:
            raise SourceError("law.moj.gov.tw LawAll page without a law name (layout changed?)")
        self.title = clean(name.text_content())
        self.meta: dict[str, str] = {}
        for tr in doc.xpath('//div[@class="table-title"]//tr'):
            th, td = tr.find("th"), tr.find("td")
            if th is not None and td is not None:
                for btn in td.xpath('.//a[contains(@class, "btn")]'):  # "連結舊法規內容"
                    btn.drop_tree()
                k = clean(th.text_content()).rstrip("：:")
                v = clean(td.xpath("string(.)"))
                if k and v and k != "法規名稱":
                    self.meta[k] = v
        self.as_of = _roc(self.meta.get("修正日期") or self.meta.get("公布日期", ""))
        body = doc.find('.//div[@class="law-reg-content"]')
        if body is None:
            raise SourceError(f"{self.title}: no article block on the LawAll page")
        self.toc: list[TocEntry] = []
        self.articles: dict[str, tuple[str, str]] = {}   # flno -> (label, markdown)
        self.order: list[str] = []
        self.blocks: list[str] = [f"# {self.title}"]
        for el in body:
            cls = el.get("class") or ""
            if cls.startswith("h3"):
                lvl = int(re.search(r"char-(\d)", cls)[1]) if re.search(r"char-(\d)", cls) else 1
                head = clean(el.text_content())
                self.toc.append(TocEntry(title=head, level=lvl - 1))
                self.blocks.append("#" * min(6, lvl + 1) + " " + head)
            elif cls == "row":
                a = el.find('.//div[@class="col-no"]//a')
                if a is None:
                    continue
                label = clean(a.text_content())
                flno = a.get("name") or re.sub(r"[^\d-]", "", label)
                lines = [clean(x.text_content()) for x in el.xpath(
                    './/div[@class="law-article"]/div')]
                md = f"**{label}**\n\n" + "\n\n".join(x for x in lines if x)
                self.articles[flno] = (label, md)
                self.order.append(flno)
                self.toc.append(TocEntry(title=label, level=_depth(self.toc),
                                          provision=re.sub(r"\s+", "", label)))
                self.blocks.append(md)

    def find(self, provision: str) -> tuple[str, str]:
        p = _nfkc(provision)
        if not p:
            raise BadRequest("empty provision. Use an article such as '第 184 條', '184', "
                             "'第184條之1', '184-1' or 'art. 184'.")
        m = re.match(r"^(?:art(?:icle)?\.?|§)?第?(\d+)(?:條)?(?:(?:之|-|_)(\d+))?(?:條)?$", p, re.I)
        if m:
            flno = m[1] + (f"-{m[2]}" if m[2] else "")
            if flno in self.articles:
                return self.articles[flno]
        for label, md in self.articles.values():
            if _nfkc(label) == p:
                return label, md
        raise NotFound(f"{self.title} ({self.pcode}) has no article {provision!r}. Labels look "
                       "like '第 184 條' or '第 15-1 條' (also '184', '第184條之1'); "
                       "see get_legislation_toc.")


def _depth(toc: list[TocEntry]) -> int:
    """Articles sit one level below the nearest heading above them."""
    for e in reversed(toc):
        if not e.provision:
            return e.level + 1
    return 0


async def _load_law(id: str) -> _Law:
    s = (id or "").strip()
    m = re.search(r"pcode=([A-Za-z]\d{7})", s)
    pcode = (m[1] if m else s).upper()
    if not _PCODE.match(pcode):
        raise BadRequest(f"bad law id {id!r}. Use an MOJ pcode such as 'B0000001' (民法), "
                         "'C0000001' (中華民國刑法), 'A0000001' (中華民國憲法), 'N0030001' (勞動基準法). Title search is "
                         "not available: law.moj.gov.tw robots.txt only allows LawAll.aspx.")
    if pcode in _laws:
        return _laws[pcode]
    r = await get(LAW_URL.format(pcode=pcode), follow_redirects=False)
    if r.status_code in (301, 302, 303) and "ErrorPage" in r.headers.get("location", ""):
        raise NotFound(f"law.moj.gov.tw has no law with pcode {pcode!r}.")
    if r.status_code != 200:
        raise SourceError("law.moj.gov.tw LawAll.aspx failed", r.status_code)
    return lru_put(_laws, pcode, _Law(pcode, r.text), 4)


# =========================================================================== #
# Adapter
# =========================================================================== #
class Taiwan(Jurisdiction):
    code = "tw"
    name = "Taiwan"
    languages = ("zh-Hant",)
    aliases = ("twn", "taiwan", "roc", "republic of china", "臺灣", "台灣", "中華民國")
    sources = (
        Source("Judicial Yuan 裁判書查詢 (FJUD, judgment.judicial.gov.tw)", f"{FJUD}/default.aspx",
               covers=("caselaw",),
               licence="Open Government Data License, version 1.0 (政府資料開放授權條款-第1版) per "
                       "the Judicial Yuan website open-data declaration; attribution required",
               commercial_use=True, ai_use=None, auth="none",
               rate_limit="unknown (not published); 1 s spacing, no 429 seen in ~20 requests "
                          "(2026-11)",
               terms_url="https://www.judicial.gov.tw/tw/cp-1327-84674-d8e05-1.html"),
        Source("Ministry of Justice 全國法規資料庫 (law.moj.gov.tw, LawAll.aspx only)", MOJ,
               covers=("legislation",),
               licence="Open Government Data License, version 1.0 (政府資料開放授權條款-第1版) per "
                       "the MOJ open-data declaration; attribution required",
               commercial_use=True, ai_use=None, auth="none",
               rate_limit="unknown (not published); 1 s spacing, no 429 seen in ~10 requests "
                          "(2026-11)",
               terms_url="https://law.moj.gov.tw/Service/Copyright.aspx"),
    )
    min_interval = {"judgment.judicial.gov.tw": 1.0, "law.moj.gov.tw": 1.0}
    notes = ("Case law: all FJUD courts (not the Constitutional Court) via keyword search (supports 台北地院105訴123-style "
             "case numbers and & + - operators). Statutes by MOJ pcode only (B0000001 民法, "
             "C0000001 刑法, N0030001 勞動基準法, A0000001 憲法; A0000001 is the 1947 base text only: Articles 25-34 "
             "(incl. 27, National Assembly) are suspended by 增修條文 A0000002): no law search, robots.txt allows only LawAll.aspx. "
             "Constitutional Court site unreachable from outside Taiwan (2026-11).")
    gaps = (
        ("Legislation search, per-article pages and the English site (law.moj.gov.tw): robots.txt "
         "allows only LawAll.aspx"),
        "Constitutional Court (cons.judicial.gov.tw): timed out from the UK (2026-11-05)",
        ("Judicial Yuan open data (opendata/data.judicial.gov.tw): timed out from the UK "
         "(2026-11-05)"),
        "Local government regulations: not researched yet",
    )
    caselaw_filters = {
        "court": "supreme (最高法院, 台上) / supreme_admin (最高行政法院) / high (臺灣高等法院) / "
                 "ip (智慧財產及商業法院) / disciplinary (懲戒法院), or a raw FJUD court code "
                 "such as TPS. Default: all courts, so a plain query mixes in lower courts "
                 "that merely cite the Supreme Court.",
    }
    samples = {
        "caselaw_query": "侵權行為 損害賠償",
        "decision_id": "TPSV,95,台上,1,20060105",
        "law_id": "B0000001",
        "provision": "第 184 條",
    }

    async def search_caselaw(self, query, *, limit, page, filters):
        query = clean(query)
        if not query:
            raise BadRequest("empty query. Give words, a case number ('最高法院108台上大2680') "
                             "or combine terms with & (and), + (or), - (not).")
        limit, page = max(1, int(limit)), max(1, int(page))
        if limit > _MAX_LIMIT:
            raise BadRequest(f"limit must be at most {_MAX_LIMIT} for FJUD (20 rows per source page, "
                             "1 s apart); use page to walk further.")
        start = (page - 1) * limit
        if start >= _MAX_HITS:
            raise BadRequest(f"FJUD lists only the first {_MAX_HITS} results of a search (newest "
                             "first). Narrow the query or add a court filter.")
        court = str((filters or {}).get("court") or "").strip()
        court = _COURT_NAMES.get(court, court)
        court = _COURTS.get(court.lower(), court.upper())
        if court and not re.fullmatch(r"[A-Z]{3,4}", court):
            raise BadRequest(f"unknown court filter {filters['court']!r}. Use supreme (最高法院), "
                             "supreme_admin, high, ip, disciplinary, or a raw FJUD court code "
                             "such as TPS.")
        q, total = await _query_hash(query, court)
        if not q:
            return Results(items=[], total=0)
        first = start // _ROWS + 1
        rows = await _result_page(q, first)
        if not rows and (f"{court}|{query}" if court else query) in _queries:  # hash expired: redo once
            _queries.pop(f"{court}|{query}" if court else query, None)
            q, total = await _query_hash(query, court)
            rows = await _result_page(q, first)
        off = start - (first - 1) * _ROWS
        last = min(start + limit - 1, _MAX_HITS - 1) // _ROWS + 1
        for n in range(first + 1, last + 1):
            if len(rows) < (n - first) * _ROWS:  # the results ended
                break
            rows += await _result_page(q, n)
        hint = ""
        if not court and re.search(r"最高法院|台上|臺上", query):
            hint = ("Default is all courts, so lower-court judgments that merely cite the Supreme "
                    "Court appear. For Supreme Court judgments only, pass filters "
                    '{"court": "supreme"}. ')
        if total and total > _MAX_HITS:
            hint += f"FJUD lists only the newest {_MAX_HITS} of these; narrow the query for older ones. "
        return Results(items=rows[off:off + limit], total=total,
                       note=hint + "Newest first. Natural persons' names in judgments since "
                            "2010-11-26 are public; others are masked (Ａ０１...).")

    async def get_decision(self, id):
        jid = _decision_id(id)
        url = _decision_url(jid)
        r = await get(url)
        if r.status_code != 200:
            raise SourceError("FJUD data.aspx failed", r.status_code)
        doc = lhtml.fromstring(r.text)
        jud = doc.find('.//div[@id="jud"]')
        if jud is None:
            raise NotFound(f"FJUD has no judgment {jid!r}.")
        meta: dict[str, str] = {}
        for row in jud.xpath('./div[@class="row"]'):
            th, td = row.find('div[@class="col-th"]'), row.find('div[@class="col-td"]')
            if th is not None and td is not None:
                meta[clean(th.text_content()).rstrip("：:")] = clean(td.text_content())
        td = jud.find('.//td[@class="tab_content"]')
        if td is None:
            raise SourceError(f"FJUD judgment {jid!r} has no text block (layout changed?)")
        title = meta.pop("裁判字號", "") or jid
        court, num = _split_title(title)
        text = _content_md(td)
        if not text:
            raise SourceError(f"FJUD judgment {jid!r} came back empty")
        return Decision(id=jid, title=title, text=text, url=url, court=court,
                        date=_roc(meta.pop("裁判日期", "")), case_number=num, metadata=meta)

    async def get_legislation_toc(self, id):
        law = await _load_law(id)
        return Toc(id=law.pcode, title=law.title, url=law.url, entries=law.toc)

    async def get_legislation_provision(self, id, provision):
        law = await _load_law(id)
        label, md = law.find(provision)
        if law.pcode == "A0000001":
            md = (f"{_AMEND_NOTE}\n\n{md}")
        return Provision(law_id=law.pcode, law_title=law.title, provision=label, text=md,
                         url=law.url, as_of=law.as_of)

    async def get_legislation_text(self, id):
        law = await _load_law(id)
        meta = dict(law.meta)
        if law.pcode == "A0000001":
            meta["note"] = _AMEND_NOTE
        return LawText(id=law.pcode, title=law.title, text="\n\n".join(law.blocks), url=law.url,
                       as_of=law.as_of, metadata=meta)
