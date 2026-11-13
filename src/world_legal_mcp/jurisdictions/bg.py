"""Bulgaria: Constitutional Court acts (constcourt.bg), the consolidated Constitution and laws
as adopted by the National Assembly (parliament.bg JSON API, the backend of
www.parliament.bg/bg/const and /bg/laws).

What is not here, and why (checked 2026-11-06 from a UK IP):
  * Supreme Court of Cassation (vks.bg): times out (https and http, www and bare host,
    2026-11-05, -06 and -10).
  * Central portal for court acts (legalacts.justice.bg): https times out; http answers
    with a JavaScript cookie challenge page, i.e. a bot check, so it is not used.
  * Supreme Administrative Court (sac.justice.bg; sac.government.bg has no web host): its
    case/act search runs only through /wp-json/vas/v1/edis/, and robots.txt says
    "Disallow: /wp-json/". The XPages app behind it (info-adc.justice.bg) is stateful
    and answers robots.txt with 403, so it is not used either.
  * Consolidated legislation: no official free source. dv.parliament.bg (State Gazette)
    has gazette materials but its search is a stateful JSF postback; lex.bg is private.
  * data.egov.bg answers 403 to this client.

Gotchas this code encodes:
  * constcourt.bg text search (?mode=search_acts&search=...) is broken server-side: the
    page stops right after the header. The structured filters (year, act_type, number)
    work, so we fetch the filtered list and match the query words locally against each
    entry (act type, number, date, case number, rapporteur, operative part).
  * Listing pages are big (all decisions ever: ~1.6 MB, ~520 entries), so they are cached
    in-process (a few entries).
  * parliament.bg /api/v1/fn-acts/1 lists only laws of the *current* National Assembly
    (its A_ns_id / L_Ses_id filters answer HTTP 500). Older laws are listed by month in
    the site's archive: /api/v1/archive-list/bg/L_Acts_fn/1/0 (years and months, 2006-)
    and /api/v1/archive-period/bg/L_Acts_fn/{year}/{month}/1/0 (t_id, t_label, t_date).
    /api/v1/act/{id} opens any id. Texts are as promulgated in the State Gazette
    (decree, law, signatures), never consolidated; most are amending laws.
  * The Constitution is a site article: /api/v1/nav/bg/const (C_ArL_title, C_ArL_body),
    consolidated with every amendment (header lists them, latest ДВ бр. 66/2024). Its id
    here is the site's own slug, 'const'. The amending laws' transitional provisions are
    appended, so some § labels repeat; a § lookup returns the first.
"""
from __future__ import annotations

import re
from urllib.parse import urlsplit

import httpx
from lxml import html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

CC = "https://www.constcourt.bg"
CC_ACT = CC + "/bg/act-{id}"
CC_COURT = "Конституционен съд"
PARL = "https://www.parliament.bg"
PARL_API = PARL + "/api/v1"
PARL_LAW = PARL + "/bg/laws/ID/{id}"
CONST_ID = "const"
CONST_URL = PARL + "/bg/const"

# constcourt.bg "Вид на акта" option values (from /bg/search-acts, 2026-11)
_ACT_TYPES = {
    "decision": "7", "решение": "7",
    "ruling": "12", "определение": "12",            # ruling that ends the case
    "admissibility": "32",                            # ruling on admissibility
    "ruling_other": "15",
    "order": "21", "разпореждане": "21",
    "dissent": "30",                                  # dissenting opinion on a decision
    "opinion": "31",                                  # concurring/separate opinion on a decision
    "annotation": "33",
    "all": "",
}

_clean = _http.clean
_lists: dict = {}
_laws: dict = {}


_SCAN_MAX = 30


async def _fetch(method: str, url: str, **kw) -> httpx.Response:
    """_http.request, retried once when the server drops a reused keep-alive connection
    without answering (seen on www.parliament.bg, 2026-11-06)."""
    try:
        return await _http.request(method, url, **kw)
    except httpx.RemoteProtocolError:
        return await _http.request(method, url, **kw)


def _num(raw: str, what: str, pattern: str, example: str) -> str:
    s = _clean(raw)
    if s.startswith("http"):
        s = urlsplit(s).path.rstrip("/").rsplit("/", 1)[-1]
    s = re.sub(r"^(act-|id/)", "", s, flags=re.I)
    if not re.fullmatch(pattern, s):
        raise BadRequest(f"Bulgarian {what} ids are {example}, got {raw!r}")
    return s


def _dash_date(s: str) -> str:
    """'27-10-2026 г.' or '27.10.2026' -> '2026-10-27'."""
    m = re.search(r"(\d{1,2})[.\-/](\d{1,2})[.\-/](\d{4})", s or "")
    return f"{m[3]}-{int(m[2]):02d}-{int(m[1]):02d}" if m else ""


# --------------------------------------------------------------------------- #
# Constitutional Court
# --------------------------------------------------------------------------- #
async def _cc_list(year: str, act_type: str, number: str) -> list[dict]:
    key = (year, act_type, number)
    if key in _lists:
        return _lists[key]
    params = {"mode": "search_acts", "year": year, "number": number, "act_type": act_type,
              "judge": ""}
    r = await _fetch("GET", CC + "/", params=params)
    if r.status_code != 200:
        raise SourceError(_http.error("constcourt.bg", "act list failed", r.status_code),
                          r.status_code)
    doc = lhtml.fromstring(r.text)
    if not doc.xpath('//form[.//input[@name="mode"][@value="search_acts"]]'):
        raise SourceError("constcourt.bg: unexpected page (no act search form)", r.status_code)
    out = []
    for it in doc.xpath('//div[@class="result-item"]'):
        link = it.xpath('.//a[contains(@href, "/bg/act-")]/@href')
        if not link:
            continue
        aid = link[0].rsplit("act-", 1)[-1]
        kind = _clean(_http.text(next(iter(it.xpath(".//h3")), None)))
        line = _clean(_http.text(next(iter(it.xpath('.//div[@class="result-date"]')), None)))
        judge = _clean(_http.text(next(iter(it.xpath('.//span[@class="small-title"]')), None)))
        disp = _clean(_http.text(next(iter(it.xpath('.//div[@class="result-text"]')), None)))
        m = re.search(r"к\.д\.\s*№\s*(\d+)\s*/\s*(\d{4})", line)
        out.append({"id": aid, "kind": kind, "line": line, "judge": judge, "disp": disp,
                    "date": _dash_date(line), "case": f"{m[1]}/{m[2]}" if m else ""})
    return _http.lru_put(_lists, key, out, 4)


def _cc_title(kind: str, line: str) -> str:
    return f"{CC_COURT}, {kind} {line}".strip().rstrip(",") if line else f"{CC_COURT}, {kind}"


# --------------------------------------------------------------------------- #
# National Assembly (laws as adopted)
# --------------------------------------------------------------------------- #
async def _constitution() -> dict:
    if CONST_ID in _laws:
        return _laws[CONST_ID]
    r = await _fetch("GET", f"{PARL_API}/nav/bg/{CONST_ID}")
    try:
        d = r.json() if r.status_code == 200 else {}
    except ValueError:
        d = {}
    paras = _http.html_paragraphs(re.sub(r"(?s)<!--\[if.*?<!\[endif\]-->", "", d.get("C_ArL_body") or ""))
    if not paras or not any(_prov_label(p) == "Чл. 1" for p in paras):
        raise SourceError(_http.error("parliament.bg", "Constitution page", r.status_code), r.status_code)
    d = {"L_ActL_final": _clean(d.get("C_ArL_title")), "_paras": paras, "_url": CONST_URL,
         "_note": paras[0] if paras[0].startswith("(Обн.") else ""}
    return _http.lru_put(_laws, CONST_ID, d, 8)


async def _archive_months(year: str) -> list[int]:
    key = ("months",)
    if key not in _lists:
        r = await _fetch("GET", f"{PARL_API}/archive-list/bg/L_Acts_fn/1/0")
        try:
            rows = r.json() if r.status_code == 200 else None
        except ValueError:
            rows = None
        if not isinstance(rows, list):
            raise SourceError(_http.error("parliament.bg", "law archive index", r.status_code), r.status_code)
        _http.lru_put(_lists, key, {str(x["t_year"]): [int(m["t_month"]) for m in x["t_month_list"]]
                                    for x in rows}, 8)
    return _lists[key].get(year, [])


async def _archive(year: str, month: int) -> list[dict]:
    key = ("archive", year, month)
    if key not in _lists:
        r = await _fetch("GET", f"{PARL_API}/archive-period/bg/L_Acts_fn/{year}/{month}/1/0")
        try:
            rows = r.json() if r.status_code == 200 else None
        except ValueError:
            rows = None
        if not isinstance(rows, list):
            raise SourceError(_http.error("parliament.bg", f"law archive {year}-{month}", r.status_code),
                              r.status_code)
        _http.lru_put(_lists, key, rows, 32)
    return _lists[key]


async def _law(lid: str) -> dict:
    if lid == CONST_ID:
        return await _constitution()
    if lid in _laws:
        return _laws[lid]
    r = await _fetch("GET", f"{PARL_API}/act/{lid}")
    if r.status_code != 200:
        raise SourceError(_http.error("parliament.bg", f"act {lid}", r.status_code), r.status_code)
    try:
        d = r.json()
    except ValueError:
        raise SourceError("parliament.bg: non-JSON reply", r.status_code)
    if not d or not isinstance(d, dict) or not d.get("L_Act_id"):
        raise NotFound(f"No National Assembly act with id {lid} on parliament.bg.")
    body = d.get("L_ActL_final_body") or ""
    paras = _http.html_paragraphs(re.sub(r"(?s)<!--\[if.*?<!\[endif\]-->", "", body))
    if not paras:
        raise NotFound(f"parliament.bg act {lid} has no adopted text (bill not passed?).")
    d["_paras"] = paras
    return _http.lru_put(_laws, lid, d, 8)


_HEAD = re.compile(r"^(Глава|Раздел|Част|Дял)\s+\S+|^(Допълнителн[аи]|Преходн[аи]|Заключителн[аи])"
                   r"\s+разпоредб[аи]|^Преходни и заключителни разпоредби", re.I)
_PROV = re.compile(r"^\**\s*(Чл\.|§)\s*(\d+[а-я]?)\.\s*\**")


def _prov_label(p: str) -> str:
    m = _PROV.match(p)
    return f"{m[1]} {m[2]}" if m else ""


def _norm_label(s: str) -> str:
    """'чл. 5', 'Чл.5', 'art 5', '5' -> 'Чл. 5'; '§ 3', 'par 3' -> '§ 3'."""
    s = _clean(s).lower().rstrip(".")
    m = re.fullmatch(r"(?:чл\.?|член|art\.?|article)?\s*(\d+[а-я]?)", s)
    if m:
        return f"Чл. {m[1]}"
    m = re.fullmatch(r"(?:§|пар\.?|параграф|par\.?|para\.?|paragraph)\s*(\d+[а-я]?)", s)
    if m:
        return f"§ {m[1]}"
    return ""


def _law_hit(x: dict) -> LawHit:
    lid = str(x["L_Act_id"])
    dv = f"ДВ, бр. {x.get('L_Act_dv_iss')} от {x.get('L_Act_dv_year')} г." if x.get("L_Act_dv_iss") else ""
    return LawHit(id=lid, title=_clean(x.get("L_ActL_final")), type="Закон",
                  number=_clean(x.get("L_Act_sign")), date=str(x.get("L_Act_date") or "")[:10],
                  snippet=dv, url=PARL_LAW.format(id=lid))


_CONST_HIT = LawHit(id=CONST_ID, title="Конституция на Република България", type="Конституция",
                    date="1991-07-13", status="в сила (consolidated)", url=CONST_URL,
                    snippet="Обн. ДВ бр. 56/1991, consolidated with all amendments")


class Bulgaria(Jurisdiction):
    code = "bg"
    name = "Bulgaria"
    languages = ("bg",)
    aliases = ("bulgaria", "българия", "bgr")
    sources = (
        Source(
            name="Конституционен съд (Constitutional Court), constcourt.bg",
            url=CC,
            covers=("caselaw",),
            licence=("no licence or terms page; footer says 'съдържанието е обект на авторско "
                     "право' (content is copyrighted), but official acts of state bodies are "
                     "excluded from copyright (ЗАПСП art. 4 item 1)"),
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 in ~20 requests (2026-11-06); Cloudflare-fronted",
            terms_url=CC + "/bg/cookies",
        ),
        Source(
            name="Народно събрание (National Assembly), parliament.bg API: Constitution and laws as adopted",
            url=PARL + "/bg/laws",
            covers=("legislation",),
            licence=("no terms page; laws are excluded from copyright (ЗАПСП art. 4 item 1)"),
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 in ~40 requests (2026-11-06, -10)",
            terms_url=PARL + "/robots.txt",
        ),
    )
    caselaw_filters = {
        "year": "year of the act, e.g. '2024', or a range up to 10 years, e.g. '2022-2024' "
                "(makes the search much faster)",
        "act_type": "decision (default), ruling, admissibility, ruling_other, order, dissent, "
                    "opinion, annotation, or all",
        "number": "act number within its year, e.g. '18' (use with year)",
    }
    legislation_filters = {
        "year": "year adopted, e.g. '2010': lists that year's laws from the parliament.bg archive "
                "(2006 onwards; one request per month, so slower) and matches the words on titles",
        "month": "1-12, with year: only that month (one request)",
    }
    min_interval = {"www.constcourt.bg": 1.0, "www.parliament.bg": 1.0}
    notes = ("Constitutional Court acts (constcourt.bg; its text search is broken, so query words "
             "are matched against the act list). Constitution: consolidated (id 'const'). Laws: as "
             "adopted/promulgated, never consolidated; search covers the current National Assembly, "
             "or 2006 onwards with a year filter (parliament.bg). Supreme courts' sites time out or "
             "are robots-blocked.")
    gaps = (
        "Supreme Court of Cassation (vks.bg): times out, https and http (2026-11-05 and -06)",
        ("Lower courts (legalacts.justice.bg): https times out, http serves a JavaScript cookie "
         "challenge (bot check)"),
        "Supreme Administrative Court: search only via /wp-json/, which robots.txt disallows",
        ("Consolidated laws and codes (the Constitution is covered): no official free source; "
         "State Gazette search is a stateful JSF postback, lex.bg is private"),
        ("Laws adopted before 2006 (e.g. the base texts of the Penal Code 1968, Obligations and "
         "Contracts Act 1950): not in the parliament.bg archive; only their later amending laws are"),
        "Secondary legislation (Council of Ministers decrees, ordinances): not researched yet",
    )
    samples = {
        "caselaw_query": "Наказателния кодекс",
        "decision_id": "10462",
        "legislation_query": "Закон",
        "law_id": "166967",
        "provision": "Чл. 1",
    }

    # ------------------------------------------------------------------ case law
    async def search_caselaw(self, query, *, limit, page, filters):
        year = _clean(filters.get("year"))
        years = [year]
        rng = re.fullmatch(r"((?:19|20)\d\d)\s*[-\u2013]\s*((?:19|20)\d\d)", year)
        if rng:
            a, b = int(rng[1]), int(rng[2])
            if not a <= b or b - a > 9:
                raise BadRequest(f"year range must run upward and span at most 10 years, got {year!r}")
            years = [str(y) for y in range(b, a - 1, -1)]
        elif year and not re.fullmatch(r"19\d\d|20\d\d", year):
            raise BadRequest(f"year must be a 4-digit year like '2024' or a range like '2022-2024', "
                             f"got {year!r}")
        number = _clean(filters.get("number"))
        if number and not re.fullmatch(r"\d{1,4}", number):
            raise BadRequest(f"number must be digits like '18', got {number!r}")
        at = _clean(filters.get("act_type") or "decision").lower()
        if at not in _ACT_TYPES:
            raise BadRequest(f"act_type must be one of {', '.join(k for k in _ACT_TYPES if k.isascii())}, "
                             f"got {at!r}")
        if not _ACT_TYPES[at] and not year:
            raise BadRequest("act_type 'all' needs a 'year' filter (the full list is too large).")
        rows = [x for y in years for x in await _cc_list(y, _ACT_TYPES[at], number)]
        if rng:
            rows.sort(key=lambda x: x["date"], reverse=True)
        words = [w for w in _clean(query).casefold().replace('"', " ").split() if w != "*"]
        hits = [x for x in rows
                if all(w in " ".join((x["kind"], x["line"], x["judge"], x["disp"])).casefold()
                       for w in words)]
        scanned = False
        if words and not hits and 0 < len(rows) <= _SCAN_MAX:
            # The list never holds the reasoning, so read each act's full text (about 1 s each).
            scanned = True
            for x in rows:
                try:
                    d = await self.get_decision(x["id"])
                except (NotFound, SourceError):
                    continue
                low = d.text.casefold()
                if all(w in low for w in words):
                    i = low.find(words[0])
                    hits.append({**x, "disp": _clean(d.text[max(0, i - 120):i + 180])})
        limit = max(1, int(limit))
        start = (max(1, int(page)) - 1) * limit
        items = [DecisionHit(id=x["id"], title=_cc_title(x["kind"], x["line"]), court=CC_COURT,
                             date=x["date"], case_number=x["case"], snippet=x["disp"][:300],
                             url=CC_ACT.format(id=x["id"]))
                 for x in hits[start:start + limit]]
        return Results(items, total=len(hits), note=(
            (f"No act in the list matched, so the full text of all {len(rows)} listed acts was read "
             f"and matched here (all words, exact spelling; snippets show the first match). "
             if scanned else "")
            + "Words are matched against the act list (type, number, date, case, rapporteur, "
            "operative part), not the full text: constcourt.bg's own text search is broken, so a "
            "topic that appears only in the reasoning cannot be found by search; open decisions "
            "with get_decision to read the reasoning."
            + (f" With more than {_SCAN_MAX} acts the full texts are not scanned; narrow the filters "
               f"(year, act_type, number)." if words and not hits and len(rows) > _SCAN_MAX else "")
            + (f" To screen by topic, repeat the search with an empty query and the same filters "
               f"(filters.year, up to 10 years), page through the {len(rows)} acts listed, then "
               f"open the relevant ones with get_decision." if words and not hits and rows else "")))

    async def get_decision(self, id):
        aid = _num(id, "Constitutional Court act", r"\d{1,6}", "constcourt.bg act numbers like "
                   "'10462' (from https://www.constcourt.bg/bg/act-10462)")
        url = CC_ACT.format(id=aid)
        r = await _fetch("GET", url)
        if r.status_code == 404:
            raise NotFound(f"No Constitutional Court act {aid} on constcourt.bg.")
        if r.status_code != 200:
            raise SourceError(_http.error("constcourt.bg", f"act {aid}", r.status_code), r.status_code)
        doc = lhtml.fromstring(r.text)
        box = doc.xpath('//div[@id="document-content"]')
        if not box:
            raise NotFound(f"No Constitutional Court act {aid} on constcourt.bg.")
        for el in box[0].xpath('.//div[@class="details-box-case"]'):
            el.getparent().remove(el)
        text = _http.html_to_md(lhtml.tostring(box[0], encoding="unicode"))
        if not text:
            raise NotFound(f"Constitutional Court act {aid} has no text on constcourt.bg.")
        info = {}
        for it in doc.xpath('(//div[contains(@class,"case-header")])[1]//div[@class="case-detail-info"]'):
            k = _clean(_http.text(next(iter(it.xpath('./div[@class="case-detail-small-info"]')), None)))
            v = _clean(_http.text(next(iter(it.xpath('./div[@class="case-detail-big-info"]')), None)))
            if k and v and k not in ("Сваляне в", "Разпечатване"):
                info[k] = v
        kind = info.get("Вид на акта", "акт")
        case = info.get("Към дело", "")
        head = text.split("\n\n", 1)[0].replace("*", "")
        m = re.search(r"№\s*(\d+)", head)
        date = _dash_date(info.get("Дата", ""))
        title = f"{CC_COURT}, {kind}{' № ' + m[1] if m else ''}"
        if date:
            title += f" от {date[8:]}.{date[5:7]}.{date[:4]} г."
        if case:
            title += f" по к.д. № {case}"
        meta = {k: v for k, v in info.items() if k != "Дата"}
        return Decision(id=aid, title=title, text=text, url=url, court=CC_COURT, date=date,
                        case_number=case, metadata=meta)

    # ------------------------------------------------------------------ legislation
    async def search_legislation(self, query, *, limit, page, filters):
        q = _clean(query)[:200]
        if q in ("*",):
            q = ""
        year = _clean(filters.get("year"))
        month = _clean(filters.get("month"))
        if year and not re.fullmatch(r"20\d\d", year):
            raise BadRequest(f"year must be a 4-digit year from 2006 on, like '2010', got {year!r}")
        if month and not (year and re.fullmatch(r"\d{1,2}", month) and 1 <= int(month) <= 12):
            raise BadRequest(f"month must be 1-12 and needs a year, got {month!r}")
        limit = max(1, int(limit))
        start = (max(1, int(page)) - 1) * limit
        words = [w for w in q.casefold().replace('"', " ").split()]
        const = [_CONST_HIT] if not year and any(w.startswith(("конституц", "constitution"))
                                                 for w in words) else []
        if year:
            months = [int(month)] if month else await _archive_months(year)
            rows = [x for m in sorted(months, reverse=True) for x in await _archive(year, m)
                    if all(w in _clean(x.get("t_label")).casefold() for w in words)]
            items = [LawHit(id=str(x["t_id"]), title=_clean(x.get("t_label")), type="Закон",
                            date=str(x.get("t_date") or "")[:10], url=PARL_LAW.format(id=x["t_id"]))
                     for x in rows[start:start + limit]]
            return Results(items, total=len(rows), note=(
                f"Laws adopted in {year}{'-' + month if month else ''} (parliament.bg archive), "
                "words matched on titles; texts as promulgated, not consolidated."))
        body = {"A_ns_id": "", "L_Ses_id": "", "A_ns_C_id": "", "A_ns_MP_id": "",
                "L_Act_string": q, "L_Act_sign": "", "date1": "", "date2": "", "Pr_id": ""}
        r = await _fetch("POST", f"{PARL_API}/fn-acts/1", json=body)
        if r.status_code != 200:
            raise SourceError(_http.error("parliament.bg", "law search failed", r.status_code),
                              r.status_code)
        try:
            rows = r.json()
        except ValueError:
            raise SourceError("parliament.bg: non-JSON reply", r.status_code)
        if not isinstance(rows, list):
            raise SourceError("parliament.bg: unexpected search payload", r.status_code)
        hits = const + [_law_hit(x) for x in rows]
        return Results(hits[start:start + limit], total=len(hits), note=(
            "Laws adopted by the current National Assembly, matched on title (add a 'year' filter "
            "for 2006 onwards); texts are as promulgated (mostly amending laws), not consolidated. "
            "The Constitution (id 'const') is consolidated."))

    async def _law_parts(self, id):
        s = _clean(id).lower().rstrip("/")
        if s in (CONST_ID, CONST_URL.lower(), "конституция", "constitution"):
            return CONST_ID, await _law(CONST_ID)
        lid = _num(id, "law", r"\d{1,7}", "parliament.bg act ids like '166967' (from "
                   "https://www.parliament.bg/bg/laws/ID/166967), or 'const' for the Constitution")
        return lid, await _law(lid)

    async def get_legislation_toc(self, id):
        lid, d = await self._law_parts(id)
        entries = []
        for p in d["_paras"]:
            plain = p.replace("*", "").strip()
            label = _prov_label(p)
            if label:
                rest = _clean(_PROV.sub("", p).replace("*", ""))[:80]
                entries.append(TocEntry(title=f"{label}. {rest}", level=1, provision=label))
            elif _HEAD.match(plain) and len(plain) < 200:
                entries.append(TocEntry(title=_clean(plain), level=0))
        return Toc(id=lid, title=_clean(d.get("L_ActL_final")), url=d.get("_url") or PARL_LAW.format(id=lid),
                   entries=entries)

    async def get_legislation_provision(self, id, provision):
        lid, d = await self._law_parts(id)
        want = _norm_label(provision)
        if not want:
            raise BadRequest(f"Give an article like 'Чл. 5' (or '5', 'art. 5') or a paragraph like "
                             f"'§ 3', got {provision!r}")
        paras, out = d["_paras"], []
        for i, p in enumerate(paras):
            if _prov_label(p) == want:
                out = [p]
                for q in paras[i + 1:]:
                    if _prov_label(q) or (_HEAD.match(q.replace("*", "").strip()) and len(q) < 200):
                        break
                    out.append(q)
                break
        if not out:
            raise NotFound(f"{want} not found in parliament.bg act {lid}.")
        return Provision(law_id=lid, law_title=_clean(d.get("L_ActL_final")), provision=want,
                         text="\n\n".join(out), url=d.get("_url") or PARL_LAW.format(id=lid))

    async def get_legislation_text(self, id):
        lid, d = await self._law_parts(id)
        meta = {"Сигнатура": _clean(d.get("L_Act_sign")),
                "Приет": str(d.get("L_Act_date") or "")[:10], "Изменения": d.get("_note", "")}
        if d.get("L_Act_dv_iss"):
            meta["Държавен вестник"] = f"бр. {d['L_Act_dv_iss']} от {d.get('L_Act_dv_year')} г."
        return LawText(id=lid, title=_clean(d.get("L_ActL_final")), text="\n\n".join(d["_paras"]),
                       url=d.get("_url") or PARL_LAW.format(id=lid), as_of=str(d.get("L_Act_date") or "")[:10],
                       metadata={k: v for k, v in meta.items() if v})
