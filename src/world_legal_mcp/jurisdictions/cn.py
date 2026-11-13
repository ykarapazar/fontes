"""China: Supreme People's Court guiding cases (指导性案例) from court.gov.cn. No legislation.

Gotchas this code encodes (verified 2026-11-05 from a UK IP):
  * Legislation is NOT implemented. The National Database of Laws and Regulations
    (flk.npc.gov.cn) has a JSON API, but its robots.txt is `User-agent: * / Disallow: /`
    with the comment 禁止使用任何自动化工具、脚本、爬虫程序采集或复制网站数据 ("using any
    automated tools, scripts or crawlers to collect or copy site data is prohibited").
    www.npc.gov.cn has no law index or search (it links to flk); www.gov.cn has none either.
  * Case law: only the SPC guiding cases. China Judgments Online (wenshu.court.gov.cn) needs
    a login with a mainland phone number, so it is left out.
  * court.gov.cn has no robots.txt (/robots.txt answers with an HTML error page) and no
    published terms; the footer says 中华人民共和国最高人民法院 版权所有.
  * The site search (/search.html?content=) does not index article bodies and treats the
    query as one phrase, so search here is a title search over the official guiding-case
    list (/shenpan/gengduo/77.html, 77_2.html, …, ~15 pages of 20), kept in memory for 12 h.
  * Ids are the site's article ids (/shenpan/xiangqing/<id>.html). The same article is also
    served under /fabu/xiangqing/<id>.html. "指导性案例266号" / "指导案例1号" / "GC266" are
    resolved through the list. Early cases are titled 指导案例N号, later ones 指导性案例N号.
  * Parties are pseudonymised in recent cases (黄某欢, 某信用管理有限公司).
"""
from __future__ import annotations

import asyncio
import re
import time

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, Results

HOST = "https://www.court.gov.cn"
LIST_URL = HOST + "/shenpan/gengduo/77{suffix}.html"
CASE_URL = HOST + "/shenpan/xiangqing/{id}.html"
COURT = "最高人民法院"
INDEX_TTL = 12 * 3600

_GC = re.compile(r"^指导(?:性)?案例\s*(\d+)\s*号")
_GC_ID = re.compile(r"^(?:指导(?:性)?案例|gc|guiding case|no\.?)\s*(\d+)\s*号?$", re.I)
_ITEM = re.compile(r'<a title="([^"]+)"[^>]*href="/shenpan/xiangqing/(\d+)\.html"[^>]*>.*?'
                   r'<i class="date">([^<]*)</i>', re.S)

_index: list[DecisionHit] = []
_index_time = 0.0
_index_lock = asyncio.Lock()
_cache: dict[str, Decision] = {}


async def _fetch(url: str, what: str) -> str:
    # court.gov.cn sometimes misses the 15 s connect timeout from abroad (ConnectTimeout,
    # two health runs 2026-11-10) and answers the next try: one retry on a network error.
    try:
        r = await _http.get(url)
    except Exception:  # network error
        r = await _http.get(url)
    if r.status_code == 404:
        raise NotFound(f"{what} not found at court.gov.cn ({url})")
    if r.status_code != 200:
        raise SourceError(_http.error("court.gov.cn", f"{what} failed", r.status_code), r.status_code)
    return r.text


def _hit(title: str, id_: str, date: str) -> DecisionHit:
    title = _http.clean(title)
    m = _GC.match(title)
    return DecisionHit(id=id_, title=title, court=COURT, date=_http.iso_date(date),
                       case_number=f"指导性案例{m[1]}号" if m else "",
                       url=CASE_URL.format(id=id_))


async def _guiding_cases() -> list[DecisionHit]:
    """Every guiding case in the official list, newest first."""
    global _index, _index_time
    async with _index_lock:
        if _index and time.monotonic() - _index_time < INDEX_TTL:
            return _index
        first = await _fetch(LIST_URL.format(suffix=""), "guiding-case list")
        last = max([int(n) for n in re.findall(r'href="/shenpan/gengduo/77_(\d+)\.html"', first)] or [1])
        pages = [first] + [await _fetch(LIST_URL.format(suffix=f"_{n}"), "guiding-case list")
                           for n in range(2, last + 1)]
        hits, seen = [], set()
        for html in pages:
            for title, id_, date in _ITEM.findall(html):
                if id_ not in seen and _GC.match(_http.clean(title)):
                    seen.add(id_)
                    hits.append(_hit(title, id_, date))
        if not hits:
            raise SourceError("court.gov.cn guiding-case list: no cases found (page layout changed?)")
        _index, _index_time = hits, time.monotonic()
        return hits


def _number(s: str) -> str | None:
    m = _GC_ID.match(_http.clean(s))
    return m[1] if m else None


class China(Jurisdiction):
    code = "cn"
    name = "China"
    languages = ("zh",)
    aliases = ("china", "prc", "chn", "zh", "中国")
    sources = (
        Source(
            name="Supreme People's Court of the PRC (最高人民法院), guiding cases (指导性案例)",
            url=HOST + "/shenpan/gengduo/77.html",
            covers=("caselaw",),
            licence="none published; site footer: 中华人民共和国最高人民法院 版权所有 (all rights reserved)",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~80 requests (2026-11-05)",
            terms_url=HOST + "/guanyu.html",
        ),
    )
    min_interval = {"www.court.gov.cn": 1.0}
    notes = ("SPC guiding cases (指导性案例) only, title search. No legislation: flk.npc.gov.cn "
             "robots.txt forbids automated access. China Judgments Online needs a login.")
    gaps = (
        "Laws and regulations (flk.npc.gov.cn): robots.txt disallows all and bans '任何自动化工具、脚本、爬虫程序'. "
        "Not available through this server; open https://flk.npc.gov.cn in a browser yourself to read the official consolidated texts",
        "Judgments of all courts (China Judgments Online): needs a login with a mainland phone number",
        "SPC judicial interpretations and typical cases other than guiding cases: not researched yet",
    )
    samples = {
        "caselaw_query": "合同",
        "decision_id": "4214",
    }

    caselaw_filters = {
        "year": "year of the website posting date, e.g. '2022', or a range, e.g. '2022-2024'",
    }

    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        cases = await _guiding_cases()
        ym = re.fullmatch(r"\s*(\d{4})(?:\s*-\s*(\d{4}))?\s*", (filters or {}).get("year") or "2000-9999")
        if not ym or int(ym[2] or ym[1]) < int(ym[1]):
            raise BadRequest("year must be like '2022' or '2022-2024'")
        lo, hi = int(ym[1]), int(ym[2] or ym[1])
        cases = [h for h in cases if lo <= int(h.date[:4] or 0) <= hi]
        q = _http.clean(query)
        num = _number(q) if q else None
        if num:
            found = [h for h in cases if h.case_number == f"指导性案例{num}号"]
        else:
            terms = q.split()
            found = [h for h in cases if all(t in h.title for t in terms)]
        start = (max(1, page) - 1) * limit
        return Results(items=found[start:start + limit], total=len(found),
                       note="Title search over the SPC guiding-case list (指导性案例); "
                            "space-separated words are AND-ed. Full text is not searchable. "
                            "'Court' is the SPC as publisher, not the court that gave the judgment "
                            "(see 裁判结果 in the text). Date is the court.gov.cn website posting "
                            "date; it can differ by days from the 发布 date printed in the text. "
                            "Results are newest first.")

    async def get_decision(self, id):
        raw = _http.clean(id)
        m = re.search(r"/xiangqing/(\d+)\.html", raw)
        if m:
            raw = m[1]
        if not raw.isdigit():
            num = _number(raw)
            if not num:
                raise BadRequest("id must be a court.gov.cn article id like '474491' or a guiding-case "
                                 f"number like '指导性案例266号', got {id!r}")
            hit = next((h for h in await _guiding_cases() if h.case_number == f"指导性案例{num}号"), None)
            if not hit:
                raise NotFound(f"指导性案例{num}号 is not in the SPC guiding-case list")
            raw = hit.id
        if raw in _cache:
            return _cache[raw]
        url = CASE_URL.format(id=raw)
        html = await _fetch(url, f"decision {raw}")
        tm = re.search(r'<div class="title">(.*?)</div>', html, re.S)
        body = re.search(r'<div class="txt_txt">(.*?)<div class="txt_etr">', html, re.S)
        if not tm or not body:
            raise SourceError(f"court.gov.cn {url}: no article title/body (page layout changed?)")
        title = _http.clean(re.sub(r"<[^>]+>", "", tm[1]))
        paras = [p for p in _http.html_paragraphs(body[1]) if p.strip("* ")]
        text = "\n\n".join(paras)
        if not text:
            raise SourceError(f"court.gov.cn {url}: empty article body")
        date = re.search(r"发布时间：\s*(\d{4}-\d{2}-\d{2})", html)
        m = _GC.match(title)
        summary, meta = "", {}
        plain = [re.sub(r"[*_]", "", p).strip() for p in paras]
        for i, p in enumerate(plain):
            if p.startswith("关键词"):
                meta["关键词"] = _http.clean(p[3:])
            if p == "裁判要点":
                nxt = []
                for q in plain[i + 1:]:
                    if q in ("相关法条", "基本案情", "裁判结果", "裁判理由"):
                        break
                    nxt.append(q)
                summary = "\n\n".join(nxt)
        src = re.search(r"来源：([^<]+)<", html)
        if src:
            meta["来源"] = _http.clean(src[1])
        meta["note"] = ("Guiding case selected and published by the SPC; the judgment itself was given "
                        "by the court named under 裁判结果. The Date field is the court.gov.cn website posting date; the official 发布 date is the one printed in the text and can differ by a few days.")
        return _http.lru_put(_cache, raw, Decision(
            id=raw, title=title, text=text, url=url, court=COURT,
            date=date[1] if date else "",
            case_number=f"指导性案例{m[1]}号" if m else "",
            summary=summary, metadata=meta), 64)
