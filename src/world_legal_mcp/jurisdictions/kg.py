"""Kyrgyzstan: Constitutional Court acts from constsot.kg (official site of the
Constitutional Court of the Kyrgyz Republic). Legislation is not covered (see notes).

Gotchas this code encodes (verified 2026-11-06 from a UK IP):
  * constsot.kg is WordPress 5.6 with the public REST API (/ru/wp-json/wp/v2/...).
    robots.txt only disallows /wp-admin/. No terms-of-use page; footer says
    "© 2026 Constitutional Court of the Kyrgyz Republic".
  * The site is bilingual through a qTranslate-style prefix (/ru/, /kg/): same post ids in
    both; a post with no text in the requested language shows the other one with a
    "(Кыргызча)" / "(Русский)" marker, stripped here. We use the /ru/ tree.
  * Court acts are posts in the "Акты" category tree (ids below). The post date is set to
    the decision date (1998 decisions carry 1998 dates). The post title is an <a> to the
    signed PDF; the body is usually empty or a link to the hearing video. Full text = the
    PDF's text layer (_http.pdf_text). The PDF may be in Kyrgyz even when the title is Russian.
  * Search is WordPress full-text search over titles and bodies (not the PDFs).
  * Legislation: the official database cbd.minjust.gov.kg (Ministry of Justice) closes the
    connection on this project's client ("Server disconnected without sending a response";
    curl: HTTP/2 INTERNAL_ERROR) while the site is up for other clients, so it is left out.
    sot.kg / act.sot.kg (general courts) refuse or time out from outside Kyrgyzstan.
"""
from __future__ import annotations

import html
import re
from urllib.parse import urlsplit

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, Results

SITE = "https://constsot.kg"
API = f"{SITE}/ru/wp-json/wp/v2/posts"
COURT = "Конституционный суд Кыргызской Республики"

# WordPress category ids of the "Акты" tree on constsot.kg.
_TYPES = {
    "decision": "5",            # Решения
    "resolution": "7",          # Постановления
    "ruling": "6",              # Определения
    "opinion": "8",             # Заключения
    "college": "9,43,44",       # Определения коллегий (accept / refuse to admit)
}
_ALL_ACTS = {4, 5, 6, 7, 8, 9, 43, 44}
_TYPE_NAMES = {5: "Решение", 7: "Постановление", 6: "Определение", 8: "Заключение",
               9: "Определение коллегии судей", 43: "Определение коллегии судей (о принятии)",
               44: "Определение коллегии судей (об отказе)"}
_FIELDS = "id,date,link,title,categories"
_LANG_MARK = re.compile(r"^\s*\((?:Кыргызча|Русский|English)\)\s*")

_docs: dict = {}


def _title(rendered: str) -> str:
    t = _http.clean(re.sub(r"<[^>]+>", " ", rendered or ""))
    return _http.clean(_LANG_MARK.sub("", html.unescape(t)))


def _parse_id(raw) -> str:
    """'29199', 'constsot:29199' or a constsot.kg wp-json URL -> '29199'."""
    s = str(raw or "").strip()
    m = re.fullmatch(r"(?:constsot:)?(\d+)", s, re.I) or re.search(r"/posts/(\d+)", s) \
        or re.search(r"[?&]p=(\d+)", s)
    if not m:
        raise BadRequest(f"Bad Constitutional Court id {raw!r}: use the numeric id from "
                         "search_caselaw, e.g. '26917'.")
    return m[1]


def _stem(query: str) -> str:
    """The site search matches exact substrings, so cut Russian case endings
    ("право" -> "прав"). Act titles name codes in the genitive ("статьи 82 Уголовного
    кодекса"); a short stem like "Уголов" would also hit Уголовно-процессуальный and
    Уголовно-исполнительный, so code names are put into the genitive instead of cut."""
    out = []
    for w in query.split():
        if re.fullmatch(r"(?i)кодекса?", w):
            w = w.rstrip("аА") + "а"
        elif w.isalpha() and len(w) >= 5 and re.search(r"(?i)(ый|ий|ой)$", w):
            w = w[:-2] + "ого"
        elif w.isalpha() and len(w) >= 5 and not re.search(r"(?i)(ого|его)$", w):
            w = w[:6] if len(w) >= 6 else w[:-1]
        out.append(w)
    # Quote "<adjective> кодекса" as a phrase: unquoted, the site also returns
    # "Уголовного-процессуального кодекса" for "Уголовного кодекса".
    return re.sub(r'(?<!")(\S+ кодекса)(?!")', r'"\1"', " ".join(out))


def _type(cats) -> str:
    for c in (5, 7, 6, 8, 44, 43, 9):
        if c in cats:
            return _TYPE_NAMES[c]
    return ""


async def _json(url: str, params: dict | None = None):
    r = await _http.get(url, params=params)
    if r.status_code == 404:
        raise NotFound("constsot.kg has no such act.")
    if r.status_code == 400 and "invalid_page_number" in r.text:
        return None, r
    if r.status_code != 200:
        raise SourceError(_http.error("constsot.kg", "request failed", r.status_code), r.status_code)
    try:
        return r.json(), r
    except ValueError:
        raise SourceError("constsot.kg: answer is not JSON (blocked or changed?)", 200) from None


class Kyrgyzstan(Jurisdiction):
    code = "kg"
    name = "Kyrgyzstan"
    languages = ("ru", "ky")
    aliases = ("kgz", "kyrgyzstan", "kyrgyz republic")
    sources = (
        Source(
            name="Constitutional Court of the Kyrgyz Republic (constsot.kg)",
            url=SITE + "/ru/akty-lary/",
            covers=("caselaw",),
            licence="none stated (footer: © Constitutional Court of the Kyrgyz Republic); "
                    "court acts are official documents",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1.5 s spacing, no 429 seen in ~20 requests (2026-11)",
            terms_url="",
        ),
    )
    caselaw_filters = {
        "type": "decision | resolution | ruling | opinion | college (judges' panel rulings on admissibility)",
        "year": "four-digit year of the act, e.g. 2023",
        "year_from": "first year of a range, e.g. 2022 (with optional year_to)",
        "year_to": "last year of a range, e.g. 2025",
    }
    min_interval = {"constsot.kg": 1.5}
    notes = ("Constitutional Court acts only (1998-now, Russian/Kyrgyz, full text from the "
             "signed PDF). No legislation (codes, statutes) through this server: the Ministry of Justice "
             "database cbd.minjust.gov.kg refuses this client, so read codes there directly; "
             "general-court acts (act.sot.kg) are unreachable abroad. To see how the Criminal "
             "or Civil Code is applied, search_caselaw (Constitutional Court rulings on its articles).")
    gaps = (
        "Legislation (Ministry of Justice database cbd.minjust.gov.kg): blocks our client (connection dropped, 2026-11-06)",
        "General-court case law (sot.kg / act.sot.kg): site down / unreachable from outside Kyrgyzstan (2026-11-06)",
    )
    samples = {
        "caselaw_query": "Водного кодекса",
        "decision_id": "26917",
    }

    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        limit = max(1, min(int(limit or 10), 100))
        params = {"per_page": limit, "page": max(1, int(page or 1)), "_fields": _FIELDS,
                  "categories": ",".join(str(c) for c in sorted(_ALL_ACTS))}
        if query and query.strip():
            params["search"] = _stem(query.strip())
        t = filters.get("type")
        if t:
            if t not in _TYPES:
                raise BadRequest(f"type must be one of {', '.join(_TYPES)}; got {t!r}.")
            params["categories"] = _TYPES[t]
        y = filters.get("year")
        y1 = filters.get("year_from") or y
        y2 = filters.get("year_to") or y
        for k, v in (("year", y), ("year_from", filters.get("year_from")), ("year_to", filters.get("year_to"))):
            if v and not re.fullmatch(r"(19|20)\d\d", str(v)):
                raise BadRequest(f"{k} must be four digits, e.g. 2023; got {v!r}.")
        if y1:
            params["after"] = f"{int(y1) - 1}-12-31T23:59:59"
        if y2:
            params["before"] = f"{int(y2) + 1}-01-01T00:00:00"
        data, r = await _json(API, params)
        total = int(r.headers["x-wp-total"]) if r.headers.get("x-wp-total", "").isdigit() else None
        items = []
        for p in data or []:
            items.append(DecisionHit(
                id=str(p["id"]), title=_title(p["title"]["rendered"]), court=COURT,
                date=(p.get("date") or "")[:10], url=p.get("link") or f"{SITE}/ru/?p={p['id']}",
                snippet=_type(p.get("categories") or []),
            ))
        note = ("Searches act titles on constsot.kg, not the PDF texts. Word endings are trimmed "
                "so 'кодекс' also finds 'кодекса'.")
        if not items and query and len(query.split()) > 1:
            note = ("No act on constsot.kg has all of these words in its title or page text "
                    "(every word must appear; the PDF texts are not searched). Try one key word, "
                    "e.g. the root of the main term, or drop the year filter. " + note)
        return Results(items=items, total=total, note=note)

    async def get_decision(self, id):
        pid = _parse_id(id)
        if pid in _docs:
            return _docs[pid]
        p, _ = await _json(f"{API}/{pid}", {"_fields": _FIELDS + ",content"})
        cats = set(p.get("categories") or [])
        if not cats & _ALL_ACTS:
            raise NotFound(f"constsot.kg post {pid} is not a court act (news or other page).")
        raw_title = p["title"]["rendered"] or ""
        body = (p.get("content") or {}).get("rendered") or ""
        pdfs = [u for u in re.findall(r'href="([^"]+?\.pdf)"', raw_title + body, re.I)
                if (urlsplit(u).hostname or "").endswith("constsot.kg")]
        text = ""
        if pdfs:
            r = await _http.get(pdfs[0])
            if r.status_code == 404:
                raise SourceError(f"constsot.kg: the act's PDF is missing ({pdfs[0]}).", 404)
            if r.status_code != 200:
                raise SourceError(_http.error("constsot.kg", "PDF download failed", r.status_code),
                                  r.status_code)
            text = _http.pdf_text(r.content)
            if not text:
                raise SourceError(f"constsot.kg: the act's PDF is a scan without a text layer; "
                                  f"read it at {pdfs[0]}", 200)
        else:
            text = _http.html_to_md(body)
        if len(text) < 100:
            raise SourceError("constsot.kg: this act has no text online (no PDF attached).", 200)
        meta = {"Type": _type(cats)} if _type(cats) else {}
        if pdfs:
            meta["PDF"] = pdfs[0]
        d = Decision(id=pid, title=_title(raw_title), text=text,
                     url=p.get("link") or f"{SITE}/ru/?p={pid}", court=COURT,
                     date=(p.get("date") or "")[:10], metadata=meta)
        return _http.lru_put(_docs, pid, d, 16)
