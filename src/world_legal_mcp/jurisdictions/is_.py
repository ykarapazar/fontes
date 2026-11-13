"""Iceland: case law of Hæstiréttur, Landsréttur and the district courts from island.is. No legislation.

The module is `is_.py` because `is` is a Python keyword; the registry keys adapters by
the class attribute `code`, so the file name does not matter.

Gotchas this code encodes (verified 2026-11-05 from a UK IP):
  * haestirettur.is and landsrettur.is now send readers to https://island.is/domar, the
    government portal (Stafrænt Ísland). Its public GraphQL endpoint
    (POST https://island.is/api/graphql) serves the verdict list and full texts with no key.
    It is undocumented, but the frontend is open source (github.com/island-is/island.is,
    MIT): queries `webVerdicts` / `webVerdictById` in apps/web/screens/queries/Verdicts.ts,
    backend in libs/clients/verdicts. Introspection is off; we use exactly those shapes.
  * Two backends behind one list. Ids `s-<GUID>` are Supreme Court decisions (Hæstiréttur's
    own API; full text is HTML turned into Contentful rich-text JSON by island.is). Ids
    `g-<uuid>` are Landsréttur, district courts and Endurupptökudómur (the "GoPro" court
    system; full text is the signed PDF, base64 in `pdfString`). We extract the PDF text
    with pypdf (text layer, no OCR), drop the page-number line and re-join wrapped lines.
  * Each backend returns at most 10 per page (`pageSize` above 10 is ignored). Without a
    court filter we query the two backends separately (Supreme Court; all other courts),
    fetch the first page*limit of each (max 200), merge by date and slice the page ourselves.
    With a court filter the page maps straight onto upstream pages (no depth cap).
    `total` is the sum of both.
  * Court filter values are the site's slugs: 'Hæstiréttur', 'landsrettur',
    'Endurupptokudomur', 'hd-reykjavik', ... Selecting every non-supreme slug at once means
    "all GoPro courts" upstream (Supreme Court excluded).
  * Unknown ids come back as `webVerdictById: null`.
  * Legislation: the consolidated law collection (althingi.is/lagas/) answers our client
    with a 403 Cloudflare JS challenge, and Alþingi's XML service (/altext/xml/) covers
    parliamentary business, not consolidated law. No headless browser, so no legislation.
"""
from __future__ import annotations

import base64
import io
import re

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, Results

API = "https://island.is/api/graphql"
WEB = "https://island.is/domar"
_ID = re.compile(r"^(s-[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}"
                 r"|g-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$")
SUPREME = "Hæstiréttur"
DISTRICT = ("hd-reykjavik", "hd-vesturland", "hd-vestfirdir", "hd-nordurland-vestra",
            "hd-nordurland-eystra", "hd-austurland", "hd-sudurland", "hd-reykjanes")
NON_SUPREME = (*DISTRICT, "landsrettur", "Endurupptokudomur")
_COURTS = {
    "supreme": [SUPREME], "haestirettur": [SUPREME], "hæstiréttur": [SUPREME],
    "appeal": ["landsrettur"], "landsrettur": ["landsrettur"], "landsréttur": ["landsrettur"],
    "retrial": ["Endurupptokudomur"], "endurupptokudomur": ["Endurupptokudomur"],
    "district": list(DISTRICT),
    **{s: [s] for s in DISTRICT},
}
_LIST_Q = ("query GetVerdicts($input: WebVerdictsInput!) { webVerdicts(input: $input) { total "
           "items { id title court caseNumber verdictDate keywords presentings } } }")
_GET_Q = ("query GetVerdictById($input: WebVerdictByIdInput!) { webVerdictById(input: $input) { "
          "item { pdfString richText title court caseNumber verdictDate keywords presentings "
          "resolutionLink } } }")
_cache: dict = {}
_LOOSE_NOTE = ("island.is matches the query loosely against the whole text and does not rank by relevance, "
               "so hits can be only marginally on topic. For a precise subject use the keyword filter "
               "(the court's lykilorð, an exact match), then read each decision to confirm it is on point.")
_KEYWORD_NOTE = ("The keyword filter matches the court's own lykilorð exactly and the query still applies "
                 "loosely on top of it. Keywords are broader than a legal topic (e.g. 'Húsaleigusamningur' "
                 "also covers commercial and hotel leases) and island.is has no residential-only filter, so "
                 "check each hit. If none is on point, there may be no such ruling in this period.")


async def _gql(query: str, variables: dict) -> dict:
    r = await _http.post(API, json={"query": query, "variables": variables})
    if r.status_code != 200:
        raise SourceError(_http.error("island.is", "GraphQL request failed", r.status_code), r.status_code)
    try:
        data = r.json()
    except ValueError:
        raise SourceError("island.is returned non-JSON (block page?)", r.status_code) from None
    if data.get("errors"):
        msg = _http.clean((data["errors"][0] or {}).get("message"))
        raise SourceError(f"island.is GraphQL error: {msg}", r.status_code)
    return data.get("data") or {}


def _norm_id(id: str) -> str:
    s = re.sub(r"^https?://(www\.)?island\.is/(en/)?(domar|court-rulings?)/", "", (id or "").strip(), flags=re.I)
    s = s.split("?")[0].strip("/")
    if s[:2].lower() == "s-":  # Supreme Court GUIDs are upper-case and case-sensitive upstream
        s = "s-" + s[2:].upper()
    elif s[:2].lower() == "g-":
        s = s.lower()
    if not _ID.match(s):
        raise BadRequest(f"{id!r} is not an island.is verdict id. Use the id from search_caselaw, e.g. "
                         "'s-AC188192-B55F-45E0-8476-55C7EDD3EDE5' (Hæstiréttur) or "
                         "'g-7008b376-b90d-4756-afb0-cfe53085b078' (other courts), or an "
                         "https://island.is/domar/... URL.")
    return s


def _date(s) -> str:
    return _http.iso_date((s or "")[:10])


def _title(item: dict) -> str:
    t = _http.clean(item.get("title"))
    if not t or len(t) > 300:  # criminal cases list every defendant and lawyer
        t = f"{_http.clean(item.get('court'))} {_http.clean(item.get('caseNumber'))}".strip() + (
            f": {t[:200].rsplit(' ', 1)[0]} …" if t else "")
    return t


def _stem(term) -> str:
    """Prefix of the longest query word, to match Icelandic inflections (húsaleigu ~ húsaleiga)."""
    words = re.findall(r"\w+", (term or "").lower())
    w = max(words, key=len) if words else ""
    return w[:-2] if len(w) >= 7 else w[:-1] if len(w) >= 5 else w


def _check_date(name: str, v: str) -> str:
    d = _date(v)
    if not d or d != str(v).strip():
        raise BadRequest(f"{name} must be YYYY-MM-DD, got {v!r}.")
    return d + "T00:00:00.000Z"


# --------------------------------------------------------------------------- #
# Full texts
# --------------------------------------------------------------------------- #
def _rt_inline(node: dict) -> str:
    t = node.get("nodeType")
    if t == "text":
        v = (node.get("value") or "").replace("\xa0", " ")
        v = re.sub(r"<br\s*/?>", "\n", v)
        if not v.strip():
            return v
        marks = {m.get("type") for m in node.get("marks") or []}
        lead, core, trail = re.match(r"^(\s*)(.*?)(\s*)$", v, re.S).groups()
        if "bold" in marks:
            core = f"**{core}**"
        if "italic" in marks:
            core = f"*{core}*"
        return lead + core + trail
    return "".join(_rt_inline(c) for c in node.get("content") or [])


def _rt_blocks(node: dict, depth: int = 0) -> list[str]:
    """Contentful rich-text document -> markdown paragraphs."""
    out: list[str] = []
    for ch in node.get("content") or []:
        t = ch.get("nodeType") or ""
        if t.startswith("heading-"):
            out.append("#" * min(int(t[-1]) + 1, 6) + " " + _http.clean(_rt_inline(ch)))
        elif t in ("unordered-list", "ordered-list"):
            for i, li in enumerate(ch.get("content") or [], 1):
                body = " ".join(_rt_blocks(li, depth + 1)).strip()
                out.append("  " * depth + (f"{i}. " if t == "ordered-list" else "- ") + body)
        elif t == "blockquote":
            out += ["> " + p for p in _rt_blocks(ch, depth)]
        elif t == "hr":
            out.append("---")
        elif t in ("paragraph", "list-item"):
            lines = [_http.clean(x) for x in _rt_inline(ch).split("\n")]
            p = "  \n".join(x for x in lines if x)
            if p:
                out.append(p)
        else:
            out += _rt_blocks(ch, depth)
    return [p for p in out if p.strip("#* ")]


def _pdf_text(b64: str) -> str:
    from pypdf import PdfReader
    try:
        reader = PdfReader(io.BytesIO(base64.b64decode(b64)))
    except Exception as e:  # bad base64 or pypdf's own error types
        raise SourceError(f"island.is verdict PDF could not be read ({type(e).__name__})") from None
    lines: list[str] = []
    for n, pg in enumerate(reader.pages, 1):
        ls = (pg.extract_text() or "").replace("\xa0", " ").split("\n")
        if ls and ls[0].strip() == str(n):  # page number at the top
            ls = ls[1:]
        if ls and ls[-1].strip() == str(n):  # ... or at the bottom
            ls = ls[:-1]
        lines += ls
    paras: list[str] = []
    buf = ""
    for ln in lines:
        if not ln.strip():
            if buf:
                paras.append(buf)
            buf = ""
            continue
        buf += ln
        if not ln.endswith(" "):  # pypdf keeps the trailing space on soft-wrapped lines
            paras.append(buf)
            buf = ""
    if buf:
        paras.append(buf)
    out = []
    for p in paras:
        p = _http.clean(p)
        # margin paragraph numbers are glued to the text: "12Áfrýjandi" -> "12 Áfrýjandi"
        p = re.sub(r"^(\d{1,3})(?=[A-ZÁÐÉÍÓÚÝÞÆÖ])", r"\1 ", p)
        if p:
            out.append(p)
    return "\n\n".join(out)


class Iceland(Jurisdiction):
    code = "is"
    name = "Iceland"
    languages = ("is",)
    aliases = ("isl", "island", "ísland", "icelandic")
    sources = (
        Source(
            name="Ísland.is court rulings (Stafrænt Ísland; Hæstiréttur, Landsréttur, héraðsdómstólar)",
            url=WEB,
            covers=("caselaw",),
            licence="No reuse licence stated; the island.is user terms (notendaskilmálar, 2022-12-05) "
                    "say nothing on reuse or automated access. Court judgments are not protected "
                    "by copyright in Iceland (höfundalög nr. 73/1972, 9. gr.; unverified). API is the "
                    "portal's own undocumented GraphQL (frontend code is MIT on GitHub)",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="none documented; island.is has no robots.txt (404, 2026-11-05); "
                       "no 429 in ~20 requests (2026-11); using 1 s spacing",
            terms_url="https://island.is/s/stafraent-island/notendaskilmalar-islandis-terms-and-"
                      "conditions-stefnur-og-skilmalar-1/notendaskilmalar-island-is",
        ),
    )
    caselaw_filters = {
        "court": "'supreme' (Hæstiréttur), 'appeal' (Landsréttur), 'district' (all district courts), "
                 "'retrial' (Endurupptökudómur), or one district court: " + ", ".join(DISTRICT),
        "date_from": "decision date from, YYYY-MM-DD",
        "date_to": "decision date to, YYYY-MM-DD",
        "case_number": "case number, e.g. '33/2023' or 'E-7422/2019'",
        "keyword": "the court's subject keyword (lykilorð), e.g. 'Húsaleigusamningur'",
    }
    min_interval = {"island.is": 1.0}
    notes = ("Case law only, Icelandic: Hæstiréttur, Landsréttur, district courts. Ids look like "
             "'s-<GUID>' (Supreme Court) or 'g-<uuid>' (other courts). No legislation: "
             "althingi.is/lagas sits behind a Cloudflare challenge.")
    gaps = (
        "Legislation (consolidated law collection, althingi.is/lagas): bot check / blocks our client (Cloudflare JS challenge)",
        "Regulations and the official gazette (Stjórnartíðindi): not researched yet",
    )
    samples = {
        "caselaw_query": "leigusamningur",
        "decision_id": "s-AC188192-B55F-45E0-8476-55C7EDD3EDE5",   # Hæstiréttur 33/2023 (Fosshótel)
    }

    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        inp: dict = {"searchTerm": (query or "").strip(), "page": max(1, int(page))}
        court = str(filters.get("court") or "").strip().lower()
        if court:
            if court not in _COURTS:
                raise BadRequest(f"court {court!r} unknown; use one of: {', '.join(sorted(_COURTS))}.")
            inp["court"] = _COURTS[court]
        for f, key in (("date_from", "dateFrom"), ("date_to", "dateTo")):
            if filters.get(f):
                inp[key] = _check_date(f, filters[f])
        if filters.get("case_number"):
            inp["caseNumber"] = _http.clean(filters["case_number"])
        if filters.get("keyword"):
            inp["keywords"] = [_http.clean(filters["keyword"])]
        if not any(inp.get(k) for k in ("searchTerm", "court", "dateFrom", "dateTo", "caseNumber", "keywords")):
            raise BadRequest("give a query or a filter, e.g. 'leigusamningur' or court='supreme'.")
        limit = max(1, int(limit))
        page = max(1, int(page))
        both = not court
        start = (page - 1) * limit
        # A court filter needs no merge: map the page onto upstream pages by offset, any depth.
        # Merging needs the first page*limit of each backend, so that path is capped.
        lo, hi = (0, start + limit) if both else (start, start + limit)
        if both and hi > 200:
            raise BadRequest("without a court filter only the first 200 results are reachable "
                             "(limit x page above 200); add a court, date or keyword filter to go deeper.")
        # Page both backends ourselves (upstream pages them independently, which drops or
        # misnumbers hits), merge by date, then cut out exactly this page.
        courts = [[SUPREME], list(NON_SUPREME)] if both else [inp["court"]]
        items, total = [], 0
        for crt in courts:
            sub = {k: v for k, v in inp.items() if k != "page"}
            sub["pageSize"] = 10  # upstream ignores anything above 10
            if both:
                sub["court"] = crt
            n, first = 0, lo // 10
            sub_items = []
            for pg in range(first + 1, (hi - 1) // 10 + 2):
                data = await _gql(_LIST_Q, {"input": {**sub, "page": pg}})
                res = data.get("webVerdicts")
                if res is None:
                    raise SourceError("island.is returned no verdict list")
                n = res.get("total") or 0
                rows = res.get("items") or []
                for it in rows:
                    if not it.get("id"):
                        continue
                    pres = _http.clean(it.get("presentings"))
                    kw = ", ".join(_http.clean(k) for k in it.get("keywords") or [] if k)
                    snippet = pres[:400] + ("…" if len(pres) > 400 else "") if pres else kw
                    sub_items.append(DecisionHit(
                        id=it["id"], title=_title(it), court=_http.clean(it.get("court")),
                        date=_date(it.get("verdictDate")), case_number=_http.clean(it.get("caseNumber")),
                        snippet=snippet, url=f"{WEB}/{it['id']}"))
                if not rows or pg * 10 >= n:
                    break
            items.extend(sub_items[lo - first * 10:] if not both else sub_items)
            total += n
        if both:
            items.sort(key=lambda h: h.date or "", reverse=True)  # stable; newest first
        note = ("Results merge the Supreme Court and the other courts, newest first; only the first "
                "200 are reachable without a court filter." if both else "")
        if inp.get("searchTerm") or inp.get("keywords"):
            note = (note + " " if note else "") + (_KEYWORD_NOTE if inp.get("keywords") else _LOOSE_NOTE)
        page_items = items[start:start + limit] if both else items[:limit]
        stem = _stem(inp.get("searchTerm"))
        if stem and page_items:
            # Flag, don't reorder: reordering inside a page breaks paging (hit n moves between pages).
            hit = [stem in f"{h.title} {h.snippet}".lower() for h in page_items]
            n_hit = sum(hit)
            if n_hit:
                pos = ", ".join(str(start + i + 1) for i, m in enumerate(hit) if m)
                note = (note + " " if note else "") + (
                    f"On this page {n_hit} of {len(hit)} hits mention '{stem}…' in the title or court summary "
                    f"(hits {pos}); the rest matched only deeper in the full text.")
            else:
                note = (f"NO CONFIRMED MATCH: none of the {len(hit)} hits on this page mentions '{stem}…' in its "
                        "title or court summary, so do not read them as rulings on that subject; the word "
                        "appears only in the full text (or the summary uses another term). Open each to check. "
                        + note)
        return Results(page_items, total=total, note=note)

    async def get_decision(self, id):
        vid = _norm_id(id)
        if vid in _cache:
            return _cache[vid]
        data = await _gql(_GET_Q, {"input": {"id": vid}})
        res = data.get("webVerdictById")
        if not res or not res.get("item"):
            raise NotFound(f"No island.is verdict {vid!r}. Find ids with search_caselaw.")
        it = res["item"]
        if it.get("richText"):
            text = "\n\n".join(_rt_blocks((it["richText"] or {}).get("document") or {}))
        elif it.get("pdfString"):
            text = _pdf_text(it["pdfString"])
        else:
            text = ""
        if not text.strip():
            raise SourceError(f"island.is has no text for {vid}")
        meta = {}
        kw = ", ".join(_http.clean(k) for k in it.get("keywords") or [] if k)
        if kw:
            meta["Lykilorð"] = kw
        if it.get("resolutionLink"):
            meta["Tengt mál (resolutionLink)"] = it["resolutionLink"]
        if vid.startswith("g-"):
            meta["Texti"] = "extracted from the court's PDF"
        d = Decision(
            id=vid, title=_title(it), text=text, url=f"{WEB}/{vid}",
            court=_http.clean(it.get("court")), date=_date(it.get("verdictDate")),
            case_number=_http.clean(it.get("caseNumber")),
            summary=_http.clean(it.get("presentings")), metadata=meta)
        return _http.lru_put(_cache, vid, d, 16)
