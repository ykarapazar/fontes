"""Mongolia: court decisions from shuukh.mn, the Judicial General Council's electronic
database of court decisions (Монгол Улсын Шүүхийн шийдвэрийн цахим сан).

Legislation is not covered: the official Unified Legal Information System (legalinfo.mn,
Ministry of Justice) did not accept TCP connections from a UK IP on 2026-11-05/06; it is
reachable again (2026-11-07) but not built yet. parliament.mn only publishes PDF dossiers
of a few dozen amending laws.

Gotchas this code encodes (verified 2026-11-06 from a UK IP):
  * robots.txt is Cloudflare's "content signals" preamble with no signals and no rules,
    so nothing is disallowed and no AI-use signal is set. No terms of use are published.
  * Search is the JSON endpoint behind the site's own search form:
    /site/case_ajax?id={level}&court_cat={category}&page=n&keyword=..., returning
    {"count", "view" (HTML table rows), "pagination_link"}; 10 rows per page.
    Category 1 = civil, 2 = criminal, 3 = administrative; level 1 = first instance,
    2 = appeal, 3 = Supreme Court (supervisory instance).
  * A decision is /single_case/{n}?id={level}&court_cat={category}. The number n is only
    unique within one category + level, so our id is "{category}/{level}/{n}" (the same
    order as the site's /cases/{category}/{level} lists).
  * Decision numbers are NOT unique ids: criminal first-instance courts all number
    "2026/ШЦТ/173" etc., and the same decision is sometimes uploaded twice.
  * A non-existent id does not 404: the page comes back with empty metadata and a
    "related decisions" list of every decision with an empty case index (16-95 MB).
    Only ids from a search are safe; we detect the empty page and raise NotFound.
  * Party names are anonymised by the courts ("Т" ХХК, Б.Б); judges' names are not.
"""
from __future__ import annotations

import html as _html
import re
from urllib.parse import urlencode

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, Results

SHUUKH = "https://shuukh.mn"
PAGE_SIZE = 10  # fixed by shuukh.mn
MAX_LIMIT = 30  # up to 4 source pages at 4-7 s each
MAX_PAGE = 5 * 2**20

_CATEGORY = {"civil": 1, "criminal": 2, "administrative": 3}
_LEVEL = {"first": 1, "appeal": 2, "supreme": 3}
_CAT_NAME = {1: "civil", 2: "criminal", 3: "administrative"}
_LEVEL_NAME = {1: "first instance", 2: "appeal", 3: "Supreme Court"}


def _case_url(cat: int, level: int, num: str) -> str:
    return f"{SHUUKH}/single_case/{num}?id={level}&court_cat={cat}"


def _parse_id(raw) -> tuple[int, int, str]:
    """'1/3/11071' or a shuukh.mn single_case URL -> (category, level, '11071')."""
    s = str(raw or "").strip()
    m = re.fullmatch(r"([123])/([123])/(\d{1,9})", s)
    if m:
        return int(m[1]), int(m[2]), m[3]
    u = re.search(r"shuukh\.mn/single_case/(\d{1,9})\?(.*)", s)
    if u:
        lv = re.search(r"(?:^|&)id=([123])(?:&|$)", u[2])
        ct = re.search(r"(?:^|&)court_cat=([123])(?:&|$)", u[2])
        if lv and ct:
            return int(ct[1]), int(lv[1]), u[1]
    raise BadRequest(f"Bad shuukh.mn id {raw!r}: use '<category>/<level>/<number>' from a search, "
                     "e.g. '1/3/11071' (category 1 civil, 2 criminal, 3 administrative; level 1 "
                     "first instance, 2 appeal, 3 Supreme Court), or the single_case URL.")


_BLOCK = r"br|p|div|li|tr|td|th|table|ul|ol|h[1-6]"
_INLINE = r"span|font|a|b|i|u|s|strong|em|sup|sub|small|big|img|o:p|st1:\w+"


def _strip(fragment: str) -> str:
    # The source double-encodes markup (&lt;span ...&gt;) and cuts snippets mid-tag. Strip only
    # known HTML tag names (so 'a < b and c > d' survives), unescape, repeat until stable.
    t = fragment or ""
    for _ in range(4):
        # Word-pasted junk: comments, conditional blocks, <xml>, <style>, also when cut or orphaned
        t = re.sub(r"<!--.*?-->|<!\[[^\]]*\]-->|<!--.*$", " ", t, flags=re.S)
        t = re.sub(r"<\s*(script|style|xml)\b.*?<\s*/\s*\1\s*>", " ", t, flags=re.S | re.I)
        t = re.sub(r"<\s*(?:script|style|xml)\b.*$", " ", t, flags=re.S | re.I)
        t = re.sub(r"^(?:(?!<).)*?<\s*/\s*(?:script|style|xml)\s*>", " ", t, flags=re.S | re.I)
        t = re.sub(rf"</?(?:{_BLOCK})\b[^<>]*>", " ", t, flags=re.I)
        t = re.sub(rf"</?(?:{_INLINE})(?:\s+[\w:-]+\s*=[^<>]*)?\s*/?>", "", t, flags=re.I)
        t = re.sub(rf"</?(?:{_BLOCK}|{_INLINE})\s+[\w:-]+\s*=[^<>]*$", "", t, flags=re.I)  # cut at the end
        u = _html.unescape(t)
        if u == t:
            break
        t = u
    return _http.clean(t)


def _choice(filters: dict, key: str, table: dict, default: str) -> int:
    v = str(filters.get(key) or default).strip().lower()
    if v not in table:
        raise BadRequest(f"{key} {v!r}: use one of {', '.join(table)}.")
    return table[v]


def _date_range(filters: dict) -> str:
    a, b = (str(filters.get(k) or "").strip() for k in ("date_from", "date_to"))
    for k, v in (("date_from", a), ("date_to", b)):
        if v and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
            raise BadRequest(f"{k} {v!r}: use YYYY-MM-DD, e.g. '2024-01-01'.")
    # an empty range makes the source scan everything and fail with HTTP 500 on big searches
    a, b = a or "1990-01-01", b or _http.today()
    return f"{a.replace('-', '/')} - {b.replace('-', '/')}"


def _rows(view: str, cat: int, level: int) -> list[DecisionHit]:
    hits: list[DecisionHit] = []
    parts = re.split(r'<tr width="100%;" style="height: 20px;">', view)[1:]
    for part in parts:
        cells = re.findall(r"<td[^>]*>\s*<a [^>]*href=\"/single_case/(\d+)\?[^\"]*\"[^>]*>(.*?)</a>",
                           part, re.S)
        if len(cells) < 3:
            continue
        num = cells[0][0]
        court, date, number = (_strip(c[1]) for c in cells[:3])
        snip = re.search(r"Хайлтын товч:</td>\s*<td[^>]*>(.*?)(?:</td>|$)", part, re.S)
        # the source cuts snippets mid-tag: drop an orphan attribute tail such as '0pt">' at the start
        snippet = re.sub(r'^[A-Za-z0-9.;:#%\- ]{0,30}"\s*>\s*', "", _strip(snip[1]))[:300] if snip else ""
        hits.append(DecisionHit(
            id=f"{cat}/{level}/{num}", title=f"{court} {number}".strip(), court=court,
            date=_http.iso_date(date), case_number=number, snippet=snippet,
            url=_case_url(cat, level, num)))
    return hits


async def _search_page(params: dict, page: int) -> tuple[list[DecisionHit], int | None]:
    q = {"id": params["level"], "court_cat": params["cat"], "bb": 1, "page": page,
         "daterange": params["daterange"], "keyword": params["keyword"], "court": "",
         "judge": "", "index_number": params["index_number"], "number": params["number"],
         "is_active": "", "court_order": 1, "date_order": 1, "result": params["keyword"]}
    r = await _http.get(f"{SHUUKH}/site/case_ajax?{urlencode(q)}",
                        headers={"X-Requested-With": "XMLHttpRequest",
                                 "Accept": "application/json"})
    if r.status_code == 500:
        raise SourceError("shuukh.mn: the search errors (HTTP 500). It does so for broad searches it "
                          "cannot finish and for some date ranges it holds no decisions for (seen for "
                          "pre-2018 ranges). Retry, narrow the date range (date_from/date_to), or add "
                          "a more specific keyword.", 500)
    if r.status_code != 200:
        raise SourceError(_http.error("shuukh.mn", "search failed", r.status_code), r.status_code)
    try:
        js = r.json()
    except ValueError:
        raise SourceError("shuukh.mn: search answer is not JSON (blocked or changed?)", 200) from None
    try:
        total = int(js.get("count"))
    except (TypeError, ValueError):
        total = None
    return _rows(js.get("view") or "", params["cat"], params["level"]), total


def _meta(page: str) -> dict[str, str]:
    i = page.find("Шийдвэрийн мэдээлэл")
    j = page.find("<!--Холбоотой", i)
    if i < 0:
        return {}
    block = page[i:j if j > 0 else i + 5000]
    return {_strip(k): _strip(v) for k, v in
            re.findall(r"<th[^>]*>(.*?)</th>\s*<td[^>]*>(.*?)</td>", block, re.S)}


class Mongolia(Jurisdiction):
    code = "mn"
    name = "Mongolia"
    languages = ("mn",)
    aliases = ("mongolia", "монгол", "монгол улс")
    sources = (
        Source(
            name="shuukh.mn, electronic database of court decisions (Judicial General Council "
                 "of Mongolia)",
            url="https://shuukh.mn",
            covers=("caselaw",),
            licence="no licence or terms published (footer: '© 2020 - 2026 Шүүхийн ерөнхий "
                    "зөвлөл'); court decisions published by a public body",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~20 requests (2026-11)",
            terms_url="https://shuukh.mn/robots.txt",
        ),
    )
    caselaw_filters = {
        "category": "'civil' (default), 'criminal' or 'administrative'",
        "level": "'supreme' (default: Supreme Court), 'appeal' or 'first' (first instance)",
        "date_from": "decision date from, YYYY-MM-DD",
        "date_to": "decision date to, YYYY-MM-DD",
        "number": "decision number, e.g. '001/ХТ2026/00115'",
        "case_index": "case index (Хэргийн индекс), e.g. '101/2024/07666/И'",
    }
    min_interval = {"shuukh.mn": 1.0}
    notes = ("Mongolian-language decisions of all courts from shuukh.mn (Judicial General "
             "Council); parties anonymised. No legislation yet: legalinfo.mn is reachable again (2026-11-07) but not built.")
    gaps = (
        "Legislation (legalinfo.mn, ~20,000 acts): source exists and works but not built yet "
         "(unreachable 2026-11-05/06, reachable again 2026-11-07)",
        "Constitutional Court decisions (333 on legalinfo.mn): source exists and works but not "
         "built yet",
        "Parliament amending laws (parliament.mn): only PDF dossiers of a few dozen laws; not "
         "built",
    )
    samples = {
        "caselaw_query": "түрээс",
        "decision_id": "1/3/11071",
    }

    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        cat = _choice(filters, "category", _CATEGORY, "civil")
        level = _choice(filters, "level", _LEVEL, "supreme")
        q = _http.clean(query)
        if len(q) > 200:
            raise BadRequest("Search text: at most 200 characters.")
        params = {"cat": cat, "level": level, "keyword": q, "daterange": _date_range(filters),
                  "number": _http.clean(filters.get("number"))[:50],
                  "index_number": _http.clean(filters.get("case_index"))[:50]}
        limit = int(limit or PAGE_SIZE)
        if limit > MAX_LIMIT:
            raise BadRequest(f"limit {limit}: shuukh.mn serves 10 results per request and each takes "
                             f"several seconds; use limit <= {MAX_LIMIT} and the page parameter for more.")
        limit = max(1, limit)
        start = (max(1, int(page or 1)) - 1) * limit
        first, last = start // PAGE_SIZE + 1, (start + limit - 1) // PAGE_SIZE + 1
        hits, total = await _search_page(params, first)
        for src in range(first + 1, last + 1):
            if (len(hits) < (src - first) * PAGE_SIZE
                    or (total is not None and total <= (src - 1) * PAGE_SIZE)):
                break
            more, _ = await _search_page(params, src)
            hits += more
        off = start % PAGE_SIZE
        return Results(items=hits[off:off + limit], total=total,
                       note=f"Searched {_CAT_NAME[cat]} decisions, {_LEVEL_NAME[level]} level; "
                            "use the category/level filters for other courts. The date filter and the Date "
                            "shown here use the source's date field, which is occasionally wrong "
                            "(a decision can sit a year off); if a known decision is missing from a "
                            "date window, search by the number filter instead.")

    async def get_decision(self, id):
        cat, level, num = _parse_id(id)
        url = _case_url(cat, level, num)
        # A real decision page is ~100-200 KB; for a non-existent id shuukh.mn sends a
        # 16-95 MB page instead of a 404, so stop reading early.
        try:
            r = await _http.get(url, max_bytes=MAX_PAGE)
        except SourceError as e:
            if e.status == 413:
                raise NotFound(f"shuukh.mn has no decision {id!r} (oversized non-decision page). "
                               "Use an id from search_caselaw: '<category>/<level>/<number>'.") from None
            raise
        if r.status_code == 404:
            raise NotFound(f"shuukh.mn has no decision {id!r}.")
        if r.status_code != 200:
            raise SourceError(_http.error("shuukh.mn", "decision request failed", r.status_code),
                              r.status_code)
        page = r.text
        meta = _meta(page)
        number = meta.get("Дугаар", "")
        i = page.find('<div class="undsen">')
        j = page.find('<div id="editor">', i)
        body = page[i:j] if i >= 0 and j > 0 else ""
        text = _http.html_to_md(body)
        if not number and not text:
            raise NotFound(f"shuukh.mn has no decision {id!r} (empty record). Use an id from "
                           "search_caselaw: '<category>/<level>/<number>'.")
        if not text:
            raise SourceError("shuukh.mn: decision page without a text body (layout changed?)", 200)
        date = _http.iso_date(meta.get("Огноо", ""))
        # the source's date field is sometimes wrong (a decision dated 2025 11 12 in its own text
        # header carried 2026-11-12): flag a mismatch instead of silently showing it
        hdr = re.match(r"\s*(\d{4}) (\d{2}) (\d{2})\b", text)
        if hdr and date and "-".join(hdr.groups()) != date:
            hdr_date = "-".join(hdr.groups())
            if _http.iso_date(hdr_date) == hdr_date:
                meta["Date note"] = (f"the source's date field says {date} but the decision text "
                                     f"header says {hdr_date}; showing the header date")
                date = hdr_date
                meta["Огноо"] = hdr_date
            else:
                meta["Date note"] = (f"the source's date field says {date} but the decision text "
                                     f"header says {hdr_date}; check the text")
        kind = re.search(r'class="decisionfullimg">.*?<p[^>]*>(.*?)</p>', page[:i], re.S)
        court = meta.get("Шүүх", "")
        return Decision(
            id=f"{cat}/{level}/{num}", title=f"{court} {number}".strip() or f"shuukh.mn {num}",
            text=text, url=url, court=court, date=date,
            case_number=number,
            metadata={k: v.rstrip(", ") for k, v in
                      {**meta, "Шийдвэрийн төрөл": _strip(kind[1]) if kind else ""}.items() if v})
