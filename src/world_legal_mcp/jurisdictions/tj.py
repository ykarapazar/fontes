"""Tajikistan: Constitutional Court decisions and legal texts from constcourt.tj,
presidential decrees/orders and Government resolutions from president.tj, and the
National Legislation Centre's legislation database (base.mmk.tj, frozen in 2019).

Gotchas this code encodes (verified 2026-11-06 from a UK IP):
  * The Ministry of Justice legal database (adlia.tj / minjust.tj), mmk.tj, ncz.tj,
    parlament.tj, majmilli.tj and sud.tj time out from outside Tajikistan; minjust.tj
    serves an expired certificate. None of them is used.
  * constcourt.tj is WordPress with the public REST API. robots.txt only disallows
    /wp-admin/; no terms page (footer: "© 2019. Суди конститутсионии Ҷумҳурии Тоҷикистон").
    Decisions are custom posts "qarorho" (29 acts, Russian and Tajik versions are separate
    posts); legal texts (Constitution, constitutional laws on the courts, ...) are "hujatho"
    (15 posts, ru/tj/en). Full text is in the post HTML. The post date is the 2020 upload
    date, not the decision date, so the decision date is read from the text.
  * president.tj is a React app over a JSON API at controlpanel.president.tj (robots.txt of
    both: "Disallow:" empty, i.e. everything allowed; no terms page found).
    /api/event_search_by_group searches titles and texts, /api/search_document searches by
    act number only, both 10 per page, and both return the full texts of the 10 hits.
    /api/event/show?id=N returns one act ({"data": null} when there is none).
    Tajik, Russian and English versions are separate items with their own ids.
    It has presidential decrees (Фармон/Указ), orders (Амр/Распоряжение), Government
    resolutions and directives, 2000s-now, not laws or codes.
  * base.mmk.tj ("Базаи Қонунгузории ҶТ", © 2017 Маркази миллии қонунгузории назди
    Президенти ҶТ) answers over plain http only (https serves a *.hts.ru certificate; it
    is hosted at a Russian ISP), while mmk.tj itself times out. A PHPMaker app: 621
    records (Constitution, constitutional laws, codes, laws, some decrees and Government
    resolutions), 1993 to December 2019, nothing newer; the status field ("Амалкунанда" /
    "Действующий") is as of then. Each record has full text in Tajik and Russian
    (`language=tj|ru`; the app keeps the language and page size in a session cookie, so
    both are sent on every request). List: view_sanadholist.php?cmd=search&
    z_nomi_sanad=LIKE&x_nomi_sanad=<words> (title substring) or z_raqam==&x_raqam=<no>,
    20 rows a page from `start` (1-based); "Сабт 1 то 20 аз 621" gives the total, and a
    `start` past the end is silently moved to the last page. Record:
    view_sanadhoview.php?showdetail=&sanadID=<id>, fields in <td data-name="...">.
    No robots.txt (the path returns the app page) and no terms page. The server sometimes
    drops the connection ("Server disconnected"); a retry usually works.
"""
from __future__ import annotations

import html
import re

import httpx

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

CC = "https://constcourt.tj"
CC_API = f"{CC}/wp-json/wp/v2"
CC_COURT = "Конституционный суд Республики Таджикистан"
PRES = "https://president.tj"
PRES_API = "https://controlpanel.president.tj/api"
PRES_PAGE = 10                      # fixed page size of the president.tj API
_LANGS = {"tj": 1, "ru": 2, "en": 3}
_PRES_TYPES = {"decrees": "Фармон / Указ (decree)", "commands": "Амр / Распоряжение (order)",
               "resolutions": "Қарор / Постановление Правительства (Government resolution)",
               "directives": "Дастур / Поручение (directive)"}
_HUJ_PREFIX = "constcourt-"
MMK = "http://base.mmk.tj"
MMK_PAGE = 20                       # fixed rows per page sent to base.mmk.tj
_MMK_LANGS = ("ru", "tj")
_MMK_ID = re.compile(r"mmk[-:](\d{1,6})(?:[-/](ru|tj))?", re.I)

_MONTHS = (("янв", 1), ("фев", 2), ("мар", 3), ("апр", 4), ("ма", 5), ("июн", 6), ("июл", 7),
           ("авг", 8), ("сен", 9), ("окт", 10), ("ноя", 11), ("дек", 12))
_DATE = re.compile(r"«?(\d{1,2})»?\s+([а-яӣӯё]+)\s+(?:соли\s+)?((?:19|20)\d\d)", re.I)
_ARTICLE = re.compile(r"^(?:#{1,6}\s*)?(?:\*\*)?(Статья|Моддаи|Article)\s+(\d+(?:[-.]\d+)?(?:\(\d+\))?)(?![\w-])\.?\s*(.*?)(?:\*\*)?$", re.I)
_HEADING = re.compile(r"^(?:#{1,6}\s*)?(?:\*\*)?(Глава|Боби|Chapter|Раздел|Фасли|Section)\b", re.I)
_POINT = re.compile(r"^(\d{1,3})\.\s")

_docs: dict = {}


def _title(rendered: str) -> str:
    return _http.clean(html.unescape(re.sub(r"<[^>]+>", " ", rendered or "")))


def _text_date(text: str) -> str:
    """First '«4» февраля 2016 года' / '4 феврали соли 2016' in the text -> ISO."""
    dated = re.search(r"(?:г\.|ш\.|шаҳри)\s*[А-ЯЁӢӮҚҒҲҶа-яёӣӯқғҳҷ-]+\s+(?=«?\d{1,2}»?\s+[а-яӣӯё]+\s+(?:соли\s+)?(?:19|20)\d\d)", text[:3000])
    for m in _DATE.finditer(text[:3000], dated.end() if dated else 0):  # the 'г. Душанбе 26 сентября 2016' line
        mon = next((n for stem, n in _MONTHS if m[2].lower().startswith(stem)), 0)
        if mon and 1 <= int(m[1]) <= 31:
            return f"{m[3]}-{mon:02d}-{int(m[1]):02d}"
    return ""


async def _json(url: str, params: dict | None = None, host: str = "constcourt.tj"):
    r = await _http.get(url, params=params)
    if r.status_code == 404:
        raise NotFound(f"{host} has no such item.")
    if r.status_code == 400 and "invalid_page_number" in r.text:
        return None, r
    if r.status_code != 200:
        raise SourceError(_http.error(host, "request failed", r.status_code), r.status_code)
    try:
        return r.json(), r
    except ValueError:
        raise SourceError(f"{host}: answer is not JSON (blocked or changed?)", 200) from None


def _wp_id(raw, what: str, example: str) -> str:
    s = str(raw or "").strip()
    m = re.fullmatch(r"(?:constcourt[-:])?(\d{1,7})", s, re.I) \
        or re.search(r"constcourt\.tj/wp-json/wp/v2/\w+/(\d{1,7})", s)
    if not m:
        raise BadRequest(f"Bad {what} id {raw!r}: use the id from the search, e.g. '{example}'.")
    return m[1]


def _law_id(raw) -> tuple[str, str]:
    """-> ('cc', '501') for a constcourt.tj text, ('pres', '54676') for a president.tj act,
    ('mmk', '621-ru') for a base.mmk.tj record."""
    s = str(raw or "").strip()
    m = _MMK_ID.fullmatch(s) or re.search(r"base\.mmk\.tj/view_sanadhoview\.php\?\S*?sanadID=(\d{1,6})()", s)
    if m:
        return "mmk", f"{m[1]}-{(m[2] or 'ru').lower()}"
    m = re.fullmatch(r"constcourt[-:](\d{1,7})", s, re.I)
    if m:
        return "cc", m[1]
    m = re.fullmatch(r"(?:president[-:])?(\d{1,7})", s, re.I) or re.search(r"president\.tj/event/\S*?/(\d{1,7})$", s)
    if m:
        return "pres", m[1]
    raise BadRequest(f"Bad Tajikistan law id {raw!r}: use 'constcourt-501' (texts on constcourt.tj, "
                     "e.g. the Constitution), 'mmk-621' / 'mmk-621-tj' (base.mmk.tj laws, Russian / "
                     "Tajik) or a president.tj act number such as '54676'.")


def _pres_type(x: dict) -> str:
    rel = x.get("news_type_relation") or []
    return ((rel[0].get("news_type") or {}).get("name") or "") if rel else ""


def _pres_url(x: dict) -> str:
    return f"{PRES}/event/documents/{_pres_type(x) or 'all_documents'}/{x['id']}"


def _pres_hit(x: dict) -> LawHit:
    t = _pres_type(x)
    return LawHit(id=str(x["id"]), title=_http.clean(x.get("title")), type=_PRES_TYPES.get(t, t),
                  number=_http.clean(x.get("number")), date=(x.get("news_date") or "")[:10],
                  url=_pres_url(x))


# ------------------------------ text structure ------------------------------ #
def _lines(body_html: str) -> list[str]:
    """Body HTML -> paragraphs, one per source line: <br> line breaks split paragraphs (the
    texts put 'Моддаи 1' and its first sentence in one <p>), and the Word-made fragmented
    bold ('**Ҷ****УМ**') is joined."""
    out = []
    for p in _http.html_paragraphs(body_html):
        for ln in p.replace("****", "").split("  \n"):
            ln = ln.strip()
            if ln and not re.fullmatch(r"[*\s]*", ln):
                out.append(ln)
    return out


def _parts(lines: list[str]) -> list[dict]:
    """Split paragraphs into TOC parts: articles ('Статья 5' / 'Моддаи 5' / 'Article 5') with
    chapter headings, or else the act's numbered points ('п. 3'). Text before the first
    part is the 'Преамбула'."""
    arts = [(i, _ARTICLE.match(ln)) for i, ln in enumerate(lines) if len(ln) < 200 and _ARTICLE.match(ln)]
    parts: list[dict] = []
    if len(arts) >= 2:
        heads = {i for i, ln in enumerate(lines) if len(ln) < 150 and _HEADING.match(ln)}
        starts = sorted({i for i, _ in arts} | heads)
        first = starts[0]
        if first > 0:
            parts.append({"label": "Преамбула", "title": "Преамбула", "level": 0, "start": 0, "end": first})
        for k, i in enumerate(starts):
            end = starts[k + 1] if k + 1 < len(starts) else len(lines)
            m = _ARTICLE.match(lines[i]) if i not in heads else None
            if m:
                label = f"{m[1].capitalize()} {m[2].replace('.', '-')}"
                title = _http.clean(f"{label}. {m[3]}" if m[3] else label)
                parts.append({"label": label, "title": title, "level": 1, "start": i, "end": end})
            else:  # chapter heading: join the next all-caps title line
                title = lines[i].strip("#* ")
                if i + 1 < len(lines) and lines[i + 1].isupper() and not _ARTICLE.match(lines[i + 1]):
                    title += " " + lines[i + 1].strip("#* ")
                parts.append({"label": "", "title": title, "level": 0, "start": i, "end": i})
        return parts
    pts = [(i, _POINT.match(ln)[1]) for i, ln in enumerate(lines) if _POINT.match(ln)]
    for k, (i, n) in enumerate(pts):
        end = pts[k + 1][0] if k + 1 < len(pts) else len(lines)
        parts.append({"label": f"п. {n}", "title": lines[i][:120], "level": 0,
                      "start": 0 if k == 0 else i, "end": end})
    return parts


def _label(provision: str) -> str:
    s = _http.clean(provision).lower()
    if s in ("преамбула", "preamble", "муқаддима"):
        return "Преамбула"
    m = re.fullmatch(r"(статья|ст\.?|моддаи|модда|art\.?|article)\s*(\d+)(?:\s*[-.]\s*(\d+))?(?:\((\d+)\))?\.?", s)
    if m:
        word = {"моддаи": "Моддаи", "модда": "Моддаи", "article": "Article", "art.": "Article",
                "art": "Article"}.get(m[1], "Статья")
        return f"{word} {m[2]}" + (f"-{m[3]}" if m[3] else "") + (f"({m[4]})" if m[4] else "")
    m = re.fullmatch(r"(?:п\.?|пункт|банди|point)?\s*(\d+)(?:\s*[-.]\s*(\d+))?\.?", s)
    if m:
        return f"#{m[1]}" + (f"-{m[2]}" if m[2] else "")
    raise BadRequest(f"Bad provision {provision!r}: use e.g. 'Статья 5', 'Моддаи 5', '5', "
                     "'Преамбула', or 'п. 3' for a decree's points.")


def _find(parts: list[dict], provision: str) -> dict:
    want = _label(provision)
    if want.startswith("#"):  # bare number: article in whatever language, else point
        num = want[1:]
        cands = [p for p in parts if p["label"].split(" ")[-1] == num]
    else:
        cands = [p for p in parts if p["label"] == want]
        if not cands and want.split(" ")[0] in ("Статья", "Моддаи", "Article"):
            num = want.split(" ")[1]
            cands = [p for p in parts if p["label"].split(" ")[-1] == num and not p["label"].startswith("п.")]
    if not cands:
        raise NotFound(f"No provision {provision!r} in this text; see get_legislation_toc.")
    return cands[0]


# ------------------------------ base.mmk.tj ---------------------------------- #
def _mmk_url(sid: str, lang: str) -> str:
    return f"{MMK}/view_sanadhoview.php?showdetail=&sanadID={sid}&language={lang}"


def _mmk_cells(block: str) -> dict[str, str]:
    """<td data-name="raqam">…</td> cells -> {name: inner HTML}."""
    return {m[1]: m[2] for m in re.finditer(r'<td data-name="(\w+)"[^>]*>(.*?)</td>', block, re.S)}


async def _mmk_get(path: str, params: dict) -> str:
    try:
        r = await _http.get(f"{MMK}/{path}", params=params)
    except httpx.RemoteProtocolError:   # the server drops reused keep-alive connections
        r = await _http.get(f"{MMK}/{path}", params=params)
    if r.status_code != 200:
        raise SourceError(_http.error("base.mmk.tj", "request failed", r.status_code), r.status_code)
    return r.text


async def _mmk_page(query: str, number: str, lang: str, offset: int) -> tuple[list[LawHit], int]:
    """Hits from 0-based `offset` to the end of its 20-row page; -> (hits, total).
    The app only starts pages on multiples of 20."""
    start = offset // MMK_PAGE * MMK_PAGE
    params = {"cmd": "search", "t": "view_sanadho", "language": lang, "recperpage": MMK_PAGE,
              "start": start + 1}
    if query:
        params |= {"z_nomi_sanad": "LIKE", "x_nomi_sanad": query}
    if number:
        params |= {"z_raqam": "=", "x_raqam": number}
    s = await _mmk_get("view_sanadholist.php", params)
    pager = re.search(r"(\d+)\s+(?:то|до)\s+(\d+)\s+(?:аз|из)\s+(\d+)", _title(s))
    if not pager:
        if 'data-rowindex="1"' in s:
            raise SourceError("base.mmk.tj: list page without a record count (changed?)", 200)
        return [], 0
    total = int(pager[3])
    if int(pager[1]) != start + 1:      # past the end: the app shows its last page instead
        return [], total
    hits = []
    for row in re.findall(r'<tr data-rowindex="\d+".*?</tr>', s, re.S):
        c = _mmk_cells(row)
        sid = re.search(r"sanadID=(\d+)", c.get("nomi_sanad", ""))
        if not sid:
            continue
        kind = _title(c.get("klassifikatorID"))
        hits.append(LawHit(
            id=f"mmk-{sid[1]}" + ("-tj" if lang == "tj" else ""),
            title=_title(c.get("nomi_sanad")),
            type=kind,
            number=_title(c.get("raqam")),
            date=_http.iso_date(_title(c.get("sanai_qabul"))),
            status=_title(c.get("holatID")),
            snippet=_title(c.get("maqomotID")),
            url=_mmk_url(sid[1], lang)))
    return hits[offset - start:], total


async def _mmk_hits(query: str, number: str, lang: str, offset: int, n: int) -> tuple[list[LawHit], int]:
    hits, total = await _mmk_page(query, number, lang, offset)
    if len(hits) < n and offset + len(hits) < total and hits:
        more, _ = await _mmk_page(query, number, lang, offset + len(hits))
        hits += more
    return hits[:n], total


# ------------------------------ documents ----------------------------------- #
async def _law(kind: str, num: str) -> dict:
    key = (kind, num)
    if key in _docs:
        return _docs[key]
    if kind == "mmk":
        sid, lang = num.split("-")
        s = await _mmk_get("view_sanadhoview.php", {"showdetail": "", "sanadID": sid, "language": lang})
        c = _mmk_cells(s)
        title = _title(c.get("nomi_sanad"))
        if not title:
            raise NotFound(f"base.mmk.tj has no record {sid}.")
        lines = _lines(c.get("matn") or "")
        kind_name = _title(c.get("klassifikatorID"))
        d = {"id": f"mmk-{sid}" + ("-tj" if lang == "tj" else ""), "title": title,
             "url": _mmk_url(sid, lang), "date": _http.iso_date(_title(c.get("sanai_qabul"))),
             "meta": {"Source": "base.mmk.tj (National Legislation Centre; database frozen in 2019)",
                      "Type": kind_name, "Number": _title(c.get("raqam")),
                      "Issued by": _title(c.get("maqomotID")),
                      "Status (as of 2019)": _title(c.get("holatID")),
                      "Date": _http.iso_date(_title(c.get("sanai_qabul")))}}
    elif kind == "cc":
        p, _ = await _json(f"{CC_API}/hujatho/{num}", {"_fields": "id,link,title,content,date"})
        lines = _lines((p.get("content") or {}).get("rendered") or "")
        d = {"id": f"{_HUJ_PREFIX}{num}", "title": _title((p.get("title") or {}).get("rendered")),
             "url": p.get("link") or f"{CC}/?p={num}", "date": "", "meta": {"Source": "constcourt.tj"}}
    else:
        x, _ = await _json(f"{PRES_API}/event/show", {"id": num}, host="president.tj")
        x = (x or {}).get("data")
        if not x:
            raise NotFound(f"president.tj has no act with id {num}.")
        if (x.get("news_type_relation") or [{}])[0].get("news_type", {}).get("type") != "documents":
            raise NotFound(f"president.tj item {num} is news, not a legal act.")
        lines = _lines(x.get("text") or "")
        d = {"id": str(x["id"]), "title": _http.clean(x.get("title")), "url": _pres_url(x),
             "date": (x.get("news_date") or "")[:10],
             "meta": {"Source": "president.tj", "Type": _PRES_TYPES.get(_pres_type(x), _pres_type(x)),
                      "Number": _http.clean(x.get("number"))}}
    if not lines:
        raise SourceError("This act has no text online.", 200)
    d["lines"], d["parts"] = lines, _parts(lines)
    return _http.lru_put(_docs, key, d, 16)


class Tajikistan(Jurisdiction):
    code = "tj"
    name = "Tajikistan"
    languages = ("tg", "ru", "en")
    aliases = ("tjk", "tajikistan", "таджикистан", "тоҷикистон", "republic of tajikistan")
    sources = (
        Source(
            name="Constitutional Court of the Republic of Tajikistan (constcourt.tj)",
            url=CC + "/ru/qarorho/",
            covers=("caselaw", "legislation"),
            licence="none stated (footer: © 2019 Constitutional Court of the Republic of Tajikistan); "
                    "court acts and laws are official documents",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown (robots.txt sets no Crawl-delay); 1 s spacing, no 429 seen (2026-11)",
            terms_url="",
        ),
        Source(
            name="Official website of the President of the Republic of Tajikistan (president.tj)",
            url=PRES + "/event/documents",
            covers=("legislation",),
            licence="none stated; presidential and Government acts are official documents",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown (robots.txt sets no Crawl-delay); 1 s spacing, no 429 seen (2026-11)",
            terms_url="",
        ),
        Source(
            name="Базаи қонунгузории ҶТ, National Legislation Centre under the President of the "
                 "Republic of Tajikistan (base.mmk.tj)",
            url=MMK + "/view_sanadholist.php",
            covers=("legislation",),
            licence="none stated (footer: ©2017 Маркази миллии қонунгузории назди Президенти ҶТ); "
                    "laws are official documents",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; no robots.txt; 1.5 s spacing, no 429 in ~25 requests, but the server "
                       "sometimes drops connections (2026-11)",
            terms_url="",
            warning="base.mmk.tj stopped in December 2019: laws and amendments since then are missing, "
                    "and its 'in force' status is as of 2019.",
        ),
    )
    legislation_filters = {
        "source": "constcourt (Constitution and court-related laws) | mmk (Constitution, codes, laws "
                  "and some decrees to 2019, base.mmk.tj) | president (decrees, orders, Government "
                  "resolutions). Default: all three, in that order",
        "type": "president.tj act type: decrees | commands | resolutions | directives",
        "number": "act number (president.tj or base.mmk.tj), e.g. 1132 or АП-969",
        "lang": "ru (default) | tj, or en for president.tj only",
    }
    min_interval = {"constcourt.tj": 1.0, "controlpanel.president.tj": 1.0, "base.mmk.tj": 1.5}
    notes = ("Constitutional Court decisions (29 acts, ru/tj) and the Constitution plus a few "
             "court laws from constcourt.tj; presidential decrees/orders and Government "
             "resolutions from president.tj; the Constitution, codes and laws 1993-2019 (621 "
             "acts, tj/ru) from the National Legislation Centre's base.mmk.tj, which stopped "
             "updating in December 2019. The current legal database (adlia.tj) and the general "
             "courts are unreachable from abroad.")
    gaps = (
        ("Laws and codes adopted or amended after December 2019: base.mmk.tj is frozen at 2019 and "
         "adlia.tj, mmk.tj, parlament.tj, majmilli.tj time out from the UK (2026-11-10); "
         "minjust.tj certificate expired"),
        "General and Supreme Court decisions (sud.tj): times out from the UK (2026-11-10)",
        ("Constitutional Court decisions beyond the 29 posted on constcourt.tj: not published "
         "online"),
        "Ministerial regulations: not researched yet",
    )
    samples = {
        "caselaw_query": "Конституции",
        "decision_id": "544",
        "legislation_query": "Конституция",
        "law_id": "constcourt-501",
        "provision": "Статья 1",
    }

    # ------------------------------ case law -------------------------------- #
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        limit = max(1, min(int(limit or 10), 100))
        params = {"per_page": limit, "page": max(1, int(page or 1)), "_fields": "id,link,title"}
        if query and query.strip():
            params["search"] = query.strip()
        data, r = await _json(f"{CC_API}/qarorho", params)
        total = int(r.headers["x-wp-total"]) if r.headers.get("x-wp-total", "").isdigit() else None
        items = [DecisionHit(id=str(p["id"]), title=_title(p["title"]["rendered"]), court=CC_COURT,
                             url=p.get("link") or f"{CC}/?p={p['id']}") for p in data or []]
        return Results(items=items, total=total,
                       note="Constitutional Court acts published on constcourt.tj only (29 acts, "
                            "Russian and Tajik versions listed separately); dates are in the full text.")

    async def get_decision(self, id):
        pid = _wp_id(id, "Constitutional Court decision", "544")
        if ("dec", pid) in _docs:
            return _docs[("dec", pid)]
        p, _ = await _json(f"{CC_API}/qarorho/{pid}", {"_fields": "id,link,title,content"})
        text = _http.html_to_md((p.get("content") or {}).get("rendered") or "")
        if len(text) < 100:
            raise SourceError("constcourt.tj: this act has no text online.", 200)
        d = Decision(id=pid, title=_title(p["title"]["rendered"]), text=text,
                     url=p.get("link") or f"{CC}/?p={pid}", court=CC_COURT, date=_text_date(text))
        return _http.lru_put(_docs, ("dec", pid), d, 16)

    # ------------------------------ legislation ----------------------------- #
    async def _cc_laws(self, query: str) -> list[LawHit]:
        params = {"per_page": 100, "_fields": "id,link,title"}
        if query:
            params["search"] = query
        data, _ = await _json(f"{CC_API}/hujatho", params)
        return [LawHit(id=f"{_HUJ_PREFIX}{p['id']}", title=_title(p["title"]["rendered"]),
                       type="constcourt.tj text", url=p.get("link") or f"{CC}/?p={p['id']}")
                for p in data or []]

    async def _pres_page(self, query: str, n: int, filters: dict) -> tuple[list[LawHit], int | None]:
        lang = filters.get("lang") or "ru"
        params = {"page": n, "lang_id": _LANGS[lang], "event_type": filters.get("type") or "documents"}
        if filters.get("number"):
            url = f"{PRES_API}/search_document"
            params["searchText"] = filters["number"]
        else:
            url = f"{PRES_API}/event_search_by_group" if query else f"{PRES_API}/search_document"
            if query:
                params["searchText"] = query
        d, _ = await _json(url, params, host="president.tj")
        d = (d or {}).get("data") or {}
        items = [_pres_hit(x) for x in d.get("data") or []]
        if query and filters.get("number"):
            q = query.lower()
            items = [h for h in items if q in h.title.lower()]
        return items, d.get("total")

    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        filters = dict(filters or {})
        if filters.get("number") is not None:
            filters["number"] = str(filters["number"]).strip()
        query = (query or "").strip()
        limit = max(1, min(int(limit or 10), PRES_PAGE))
        page = max(1, int(page or 1))
        src = filters.get("source") or ""
        if src not in ("", "constcourt", "mmk", "president"):
            raise BadRequest(f"source must be constcourt, mmk or president; got {src!r}.")
        if filters.get("type") and filters["type"] not in _PRES_TYPES:
            raise BadRequest(f"type must be one of {', '.join(_PRES_TYPES)}; got {filters['type']!r}.")
        if filters.get("lang") and filters["lang"] not in _LANGS:
            raise BadRequest(f"lang must be ru, tj or en; got {filters['lang']!r}.")
        if filters.get("number") and not re.fullmatch(r"[\w-]{1,20}", filters["number"]):
            raise BadRequest(f"number must be an act number like 1132 or АП-969; got {filters['number']!r}.")
        if src == "constcourt" and (filters.get("type") or filters.get("number") or filters.get("lang")):
            raise BadRequest("type, number and lang filters apply to source=mmk or president only.")
        if src == "mmk" and (filters.get("type") or filters.get("lang") == "en"):
            raise BadRequest("base.mmk.tj (source=mmk) has no type filter and only ru / tj texts.")
        lang = filters.get("lang") or "ru"
        number = filters.get("number") or ""
        use_cc = src in ("", "constcourt") and not (filters.get("type") or number or filters.get("lang"))
        use_mmk = src in ("", "mmk") and not filters.get("type") and lang in _MMK_LANGS
        use_pres = src in ("", "president")

        # Each fetcher: (offset, n) -> (hits from that offset, source total).
        async def cc(offset, n):
            hits = await self._cc_laws(query)
            return hits[offset:offset + n], len(hits)

        async def mmk(offset, n):
            return await _mmk_hits(query, number, lang, offset, n)

        async def pres(offset, n):
            items, total, k, skip = [], None, offset // PRES_PAGE + 1, offset % PRES_PAGE
            while len(items) < n:
                hits, total = await self._pres_page(query, k, filters)
                items += hits[skip:][:n - len(items)]
                if not hits or k * PRES_PAGE >= (total or 0):
                    break
                k, skip = k + 1, 0
            return items, total or 0

        fetchers = [f for f, on in ((cc, use_cc), (mmk, use_mmk), (pres, use_pres)) if on]
        items, offset, total = [], (page - 1) * limit, 0
        for f in fetchers:
            if len(items) >= limit:
                total = None        # later sources not asked, so the overall count is unknown
                break
            hits, n = await f(offset, limit - len(items))
            items += hits
            offset = max(0, offset - n)
            total += n
        return Results(items=items, total=total,
                       note="constcourt.tj texts are 'constcourt-N'; base.mmk.tj laws (to 2019 only) "
                            "'mmk-N' (Russian) or 'mmk-N-tj'; president.tj acts plain numbers "
                            "(decrees, orders, Government resolutions).")

    async def get_legislation_toc(self, id):
        d = await _law(*_law_id(id))
        entries = [TocEntry(title=p["title"], level=p["level"], provision=p["label"]) for p in d["parts"]]
        if not entries:
            entries = [TocEntry(title=d["title"], provision="текст")]
        return Toc(id=d["id"], title=d["title"], url=d["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        d = await _law(*_law_id(id))
        if _http.clean(provision).lower() in ("текст", "text", "матн"):
            return Provision(law_id=d["id"], law_title=d["title"], provision="текст",
                             text="\n\n".join(d["lines"]), url=d["url"])
        p = _find([p for p in d["parts"] if p["label"]], provision)
        text = "\n\n".join(d["lines"][p["start"]:p["end"]])
        if p["label"].split(" ")[0] in ("Статья", "Моддаи", "Article"):
            text = f"### {d['lines'][p['start']].strip('#* ')}\n\n" + "\n\n".join(d["lines"][p["start"] + 1:p["end"]])
        return Provision(law_id=d["id"], law_title=d["title"], provision=p["label"], text=text, url=d["url"])

    async def get_legislation_text(self, id):
        d = await _law(*_law_id(id))
        return LawText(id=d["id"], title=d["title"], text="\n\n".join(d["lines"]), url=d["url"],
                       metadata={k: v for k, v in d["meta"].items() if v})
