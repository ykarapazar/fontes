"""Maldives: consolidated legislation from MvLaw (mvlaw.gov.mv), the Attorney General's
Office database of the Constitution, Acts, regulations and other legal instruments.

Gotchas this code encodes:
  * MvLaw is a Laravel + Inertia.js site. Every page carries its data as JSON in the
    `data-page` attribute of `<div id="app">`, so plain GETs of the public pages give
    structured data. The `/api/v1/...` routes need an OAuth token and are not used.
    robots.txt: `User-agent: * / Disallow:` (everything allowed, no Crawl-delay,
    checked 2026-11-06).
  * Texts are in Dhivehi only (the English switch is off: `enable_en: false`).
  * Law id = MvLaw's own legislation id, e.g. "163" (Civil Procedure Act 32/2021).
    `/dv/legislations/{id}` redirects to the latest consolidation and holds the whole
    text as a section tree: chapters (ބާބު) / parts (ބައި) -> articles ("1.") ->
    sub-articles ("(ހ)") -> items. A few nodes sit outside their article (data slips in
    the Constitution); they are appended to the block before them.
    The pages are big (Civil Procedure Act ~6.4 MB, Constitution ~3 MB); an unknown id
    is a small 404, and ids are checked to be short digit strings first.
  * Word search (`filter[search]=`) searches titles, numbers and article text, returns
    10 hits a page with no hit count, and ignores `page` (page 2 = page 1, checked
    2026-11-06), so only the first page of a word search is offered. Filter-only
    listings (no words) page properly, 20 a page, with a total.
  * Status "published" is the site's "in force" flag, but the superseded 1932-1998
    constitutions carry it too, so it is passed on as "published", not "in force".
  * Search hits carry no category; the type is guessed from the number
    ("2022/R-100" regulation, "32/2021" law).
  * Dates are stored as UTC midnight-minus-5h ("2022-06-15T19:00:00Z" = 16 June 2022
    in Malé); they are shifted to Maldives time (UTC+5).
  * MvLaw lacks many Acts (most amendment Acts and many Acts since 2008: e.g. 17/2026 is
    not there). Those come from the Government Gazette (gazette.gov.mv, President's
    Office), filter source=gazette: listing /gazette?type=gaanoonu (laws; 10 a page,
    newest first, "ޖުމްލަ N ގެޒެޓް" = total; `q` searches titles and numbers), item page
    gazette.gov.mv/gazette/{id} links one PDF on storage.googleapis.com. The PDF is the
    as-published text (Thaana text layer, no OCR); the extractor sometimes reverses digit
    runs and brackets ("2016/7" for 7/2016), so provisions are offered per PDF page.
    The gazette's law list starts in 2008-2009; robots.txt `Disallow:` (all allowed),
    no terms page (checked 2026-11-10).
  * Case law is not offered: the Supreme Court site (supremecourt.mv) lists judgments
    but every judgment PDF is on old.supremecourt.mv, which answers with a Cloudflare
    challenge; highcourt.gov.mv and judiciary.gov.mv (-> dja.gov.mv) are behind
    Cloudflare blocks too (checked 2026-11-06).
"""
from __future__ import annotations

import datetime
import html as _h
import json
import re
from urllib.parse import urlencode

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import LawHit, LawText, Provision, Results, Toc, TocEntry

HOST = "mvlaw.gov.mv"
BASE = f"https://{HOST}"
LIST = f"{BASE}/dv/legislations"
SEARCH_PER_PAGE = 10
LIST_PER_PAGE = 20

# filter value -> MvLaw category id (from the site's own filter list, 2026-11-06)
CATEGORIES = {"constitution": "9", "law": "1", "regulation": "2", "other": "3",
              "bylaw": "21", "municipal": "22"}
_CAT_ALIASES = {"laws": "law", "act": "law", "acts": "law", "regulations": "regulation",
                "constitutions": "constitution", "municipal regulation": "municipal"}
STATUSES = {"published": "published", "in force": "published", "abolished": "abolished", "not in force": "not_implemented"}
_STATUS_OUT = {"published": "published", "abolished": "abolished",
               "not_implemented": "not yet in force"}

_ID = re.compile(r"^\s*(\d{1,6})\s*$")
_ART = re.compile(r"^(\d{1,4}(?:-\d{1,3})?)\.?$")   # article numbers: "1.", "303", "9-1."
_MV_TZ = datetime.timedelta(hours=5)

_cache: dict = {}

GZ_HOST = "www.gazette.gov.mv"
GZ_LIST = f"https://{GZ_HOST}/gazette"
GZ_ITEM = "https://gazette.gov.mv/gazette/"
GZ_PER_PAGE = 10
_GZ_ID = re.compile(r"^\s*(?:https?://(?:www\.)?gazette\.gov\.mv/)?gazette[/:-](\d{1,6})/?\s*$", re.I)
# Dhivehi month names, matched by their first letters (the gazette spells some two ways)
_GZ_MONTHS = (("ޖަނ", 1), ("ފެބ", 2), ("މާރ", 3), ("އޭޕ", 4), ("އެޕ", 4), ("މޭ", 5), ("މެއ", 5),
              ("ޖޫނ", 6), ("ޖޫން", 6), ("ޖުލ", 7), ("އޮގ", 8), ("ސެޕ", 9), ("އޮކ", 10), ("ނޮވ", 11),
              ("ޑިސ", 12))
_gz_cache: dict = {}
_GZ_NOTE = ("Government Gazette laws, newest first, as published (not consolidated); text comes "
            "from the PDF text layer, where digits and brackets are sometimes reversed: check the PDF.")


# ---------- small helpers ----------

def _page_data(html: str) -> dict:
    m = re.search(r'<div id="app" data-page="([^"]*)"', html)
    if not m:
        raise SourceError("mvlaw.gov.mv page without data (layout changed?)", "no data")
    return json.loads(_h.unescape(m[1]))["props"]


def _strip(s) -> str:
    """Inline HTML (titles, numbers, <em> search marks) -> one clean line."""
    s = re.sub(r"</?(?:em|b|strong|i|span)\b[^>]*>", "", str(s or ""))  # inline marks split words
    return _http.clean(_h.unescape(re.sub(r"<[^>]+>", " ", s)))


def _body(s) -> str:
    s = str(s or "")
    if not s.strip():
        return ""
    if "<" in s or "&" in s:
        return _http.html_to_md(s)
    return _http.clean(s)


def _date(ts) -> str:
    """'2022-06-15T19:00:00.000000Z' (UTC) -> '2022-06-16' (Malé, UTC+5)."""
    m = re.match(r"(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)", str(ts or ""))
    if not m:
        return ""
    return (datetime.datetime.fromisoformat(m[1]) + _MV_TZ).date().isoformat()


def _status(x: dict) -> str:
    if x.get("abolished_at"):
        return "abolished"
    return _STATUS_OUT.get(x.get("status") or "", x.get("status") or "")


def _hit(x: dict) -> LawHit:
    snippet = ""
    for c in x.get("consolidations") or []:
        for s in c.get("sections") or []:
            snippet = _strip(s.get("content") or s.get("title"))
            if snippet:
                break
        if snippet:
            break
    cats = x.get("categories") or []
    no = _strip(x.get("legislation_no"))
    kind = (_strip(cats[-1]["name"]) if cats else
            "regulation" if "R-" in no else "constitution" if "ޤާނޫނުއަސާސީ" in no else
            "law" if re.fullmatch(r"\d+/\d{4}", no) else "")
    return LawHit(id=str(x["id"]), title=_strip(x.get("title")), type=kind,
                  number=no, date=_date(x.get("implemented_at")),
                  status=_status(x), snippet=snippet[:300],
                  url=x.get("latest_consolidation_url") or f"{LIST}/{x['id']}")


def _norm_provision(p: str) -> str:
    s = _http.clean(p).replace("ވަނަ", " ")
    s = re.sub(r"(?i)^(?:article|art\.?|section|sec\.?|s\.|§|މާއްދާ)\s*", "", s)
    s = re.sub(r"\s*(?:މާއްދާ)$", "", s).strip()
    m = re.fullmatch(r"(\d{1,4}(?:-\d{1,3})?)\s*\.?", s)
    return m[1] if m else s


# ---------- law text: section tree -> blocks ----------

def _blocks(sections: list) -> list[dict]:
    """Section tree -> ordered blocks {kind: preamble|heading|article, label, title, level, lines}."""
    blocks = [{"kind": "preamble", "label": "", "title": "", "level": 0, "lines": []}]

    def node_line(x: dict, indent: int) -> list[str]:
        num, title, body = _strip(x.get("number")), _strip(x.get("title")), _body(x.get("content"))
        head = " ".join(t for t in (num, title) if t)
        text = f"{head} {body}".strip() if head and body and "\n" not in body else \
            "\n\n".join(t for t in (head, body) if t)
        out = [("  " * indent) + text] if text else []
        if x.get("amendment_note"):
            out.append(("  " * indent) + f"_[{_strip(x['amendment_note'])}]_")
        return out

    def walk(nodes: list, level: int, in_art: bool, indent: int):
        for x in nodes:
            num = _strip(x.get("number"))
            kids = x.get("children") or []
            m = _ART.match(num)
            if not in_art and m:
                title = _strip(x.get("title"))
                lines = [_body(x.get("content"))]
                if x.get("amendment_note"):
                    lines.append(f"_[{_strip(x['amendment_note'])}]_")
                blocks.append({"kind": "article", "label": m[1],
                               "title": f"{m[1]}. {title}".strip(), "level": level,
                               "lines": [ln for ln in lines if ln]})
                walk(kids, level + 1, True, 0)
            elif in_art or not kids:
                blocks[-1]["lines"] += node_line(x, indent)
                walk(kids, level + 1, in_art, indent + 1)
            else:
                title = " – ".join(t for t in (num, _strip(x.get("title"))) if t)
                blocks.append({"kind": "heading", "label": "", "title": title, "level": level,
                               "lines": [_body(x.get("content"))] if _body(x.get("content")) else []})
                walk(kids, level + 1, False, 0)

    walk(sections, 0, False, 0)
    return [b for b in blocks if b["kind"] != "preamble" or b["lines"]]


def _block_md(b: dict) -> str:
    body = "\n\n".join(b["lines"])
    if b["kind"] == "article":
        return f"### {b['title']}\n\n{body}".strip()
    if b["kind"] == "heading":
        return f"## {b['title']}\n\n{body}".strip()
    return body


# ---------- Government Gazette (laws MvLaw lacks) ----------

def _gz_date(s: str) -> str:
    m = re.match(r"(\d{1,2})\s+(\S+)\s+(\d{4})", _http.clean(s))
    if not m:
        return ""
    mon = next((n for pre, n in _GZ_MONTHS if m[2].startswith(pre)), 0)
    return f"{m[3]}-{mon:02d}-{int(m[1]):02d}" if mon else ""


def _gz_hits(html: str) -> list[LawHit]:
    hits = []
    for blk in html.split('class="col-md-12 bordered items"')[1:]:
        m = re.search(r'class="gazette-title" href="https?://(?:www\.)?gazette\.gov\.mv/gazette/(\d+)"[^>]*>([^<]*)<', blk)
        if not m:
            continue
        title = _strip(m[2])
        no = re.search(r"ޤާނޫނު\s*ނަންބަރު\s*:?\s*(\d{1,3}/\d{4})", title)
        d = re.search(r"ތާރީޚު:\s*([^<]*)<", blk)
        vol = re.search(r"ވޮލިއުމް:\s*</span>\s*(\d+)(?:&nbsp;|\s)*<span>[^<]*</span>\s*(\d+)", blk)
        hits.append(LawHit(id=f"gazette/{m[1]}", title=title, type="law (as published in the Gazette)",
                           number=no[1] if no else "", date=_gz_date(d[1]) if d else "",
                           snippet=f"Gazette volume {vol[1]}, issue {vol[2]}" if vol else "",
                           url=GZ_ITEM + m[1]))
    return hits


def _gz_pages(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


class Maldives(Jurisdiction):
    code = "mv"
    name = "Maldives"
    languages = ("dv",)
    aliases = ("mdv", "maldives", "dhivehi raajje")
    sources = (
        Source("MvLaw (mvlaw.gov.mv), Attorney General's Office legislation database",
               BASE,
               covers=("legislation",),
               licence="No terms of use published (footer: 'Copy Right 2023 © Atourney generals "
                       "office'); official legislation of the Maldives",
               commercial_use=None,   # no terms page; nothing said either way
               ai_use=None,           # robots.txt allows all, no AI/TDM signal; no terms
               auth="none",
               rate_limit="unknown; no Crawl-delay in robots.txt; 1 s spacing, no 429 seen in "
                          "~20 requests (2026-11-06)",
               terms_url=f"{BASE}/dv/mi-vebsaitaagulhey-mauloomaathu"),
        Source("Government Gazette of the Maldives (gazette.gov.mv), President's Office",
               "https://www.gazette.gov.mv",
               covers=("legislation",),
               licence="No terms of use or licence published (footer: '© ދިވެހި ސަރުކާރުގެ ގެޒެޓް "
                       "2013 - 2026'); the official gazette of the Maldives",
               commercial_use=None, ai_use=None,  # robots.txt allows all; no terms page
               auth="none",
               rate_limit="unknown; robots.txt 'Disallow:' with no Crawl-delay; 1 s spacing, no 429 "
                          "seen in ~15 requests (2026-11-10)",
               terms_url="https://www.gazette.gov.mv/about"),
    )
    legislation_filters = {
        "category": "constitution, law, regulation, other (decisions, guidelines, tax rulings...), "
                    "bylaw (regulations under an Act) or municipal",
        "status": "published (the site's 'in force' flag; superseded old constitutions carry it "
                  "too), abolished, or not in force",
        "year": "year the instrument took effect, e.g. 2021",
        "source": "mvlaw (default: consolidated texts) or gazette (every law as published in the "
                  "Government Gazette since 2008-2009, incl. amendment Acts MvLaw lacks; word search "
                  "over titles and law numbers; no other filters)",
    }
    min_interval = {HOST: 1.0, GZ_HOST: 1.0, "gazette.gov.mv": 1.0, "storage.googleapis.com": 1.0}
    notes = ("Legislation only, in Dhivehi: the AG Office's MvLaw database (Constitution, Acts, "
             "regulations, other instruments), consolidated with amendment notes. Coverage is "
             "still being filled in; laws it lacks (since 2008-2009) come as published from the Government "
             "Gazette (filter source=gazette, ids 'gazette/<n>'). No case law: court judgment hosts sit behind Cloudflare "
             "challenges.")
    gaps = (
        "Case law (Supreme Court, High Court, lower courts): Cloudflare challenge blocks our "
         "client (2026-11-06)",
        "English texts: not published (MvLaw's English switch is off; Dhivehi only)",
        "Acts before 2008 that MvLaw has not entered: the Gazette's law list starts 2008-2009 and "
        "no other official full-text source was found",
        "Gazette texts: as published, not consolidated; provisions only per PDF page (the PDF "
        "text layer garbles article numbering)",
        "Word-search hits beyond the first 10: the source ignores the page parameter",
    )
    samples = {
        "legislation_query": "މަދަނީ",
        "law_id": "139",
        "provision": "1",
    }

    # ---- search ----

    @staticmethod
    def _filter_params(filters: dict) -> dict[str, str]:
        p: dict[str, str] = {}
        if filters.get("category"):
            c = _http.clean(filters["category"]).lower()
            c = _CAT_ALIASES.get(c, c)
            if c not in CATEGORIES:
                raise BadRequest(f"category {filters['category']!r}: use one of {', '.join(CATEGORIES)}")
            p["filter[related_categories]"] = CATEGORIES[c]
        if filters.get("status"):
            s = _http.clean(filters["status"]).lower()
            if s not in STATUSES:
                raise BadRequest(f"status {filters['status']!r}: use one of {', '.join(STATUSES)}")
            p["filter[status]"] = STATUSES[s]
        if filters.get("year"):
            y = _http.clean(filters["year"])
            if not re.fullmatch(r"(1[89]|20)\d\d", y):
                raise BadRequest(f"year {filters['year']!r}: use a 4-digit year, e.g. 2021")
            p["filter[effective_year]"] = y
        return p

    async def _list(self, params: dict) -> dict:
        r = await _http.get(f"{LIST}?" + urlencode(params))
        if r.status_code != 200:
            raise SourceError("mvlaw.gov.mv legislation list failed", r.status_code)
        leg = _page_data(r.text).get("legislations")
        if not isinstance(leg, dict) or "data" not in leg:
            raise SourceError("mvlaw.gov.mv legislation list: unexpected payload", "bad data")
        return leg

    async def _gazette_search(self, q: str, limit: int, page: int) -> Results:
        limit = max(1, min(int(limit), GZ_PER_PAGE))
        start = (max(1, int(page)) - 1) * limit
        p0 = start // GZ_PER_PAGE + 1
        params = {"type": "gaanoonu", **({"q": q} if q else {})}

        async def one(n: int) -> str:
            r = await _http.get(f"{GZ_LIST}?" + urlencode({**params, "page": n}))
            if r.status_code != 200:
                raise SourceError(_http.error("gazette.gov.mv", "law list failed", r.status_code), r.status_code)
            if "gazette-search-form" not in r.text:
                raise SourceError("gazette.gov.mv: unexpected page (layout changed or blocked?)")
            return r.text
        html = await one(p0)
        rows = _gz_hits(html)[start % GZ_PER_PAGE:]
        tot = re.search(r"ޖުމްލަ\s*(\d+)", html)
        total = int(tot[1]) if tot else None
        if len(rows) < limit and total and p0 * GZ_PER_PAGE < total:
            rows += _gz_hits(await one(p0 + 1))
        return Results(items=rows[:limit], total=total,
                       note=_GZ_NOTE)

    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        filters = dict(filters or {})
        src = _http.clean(filters.pop("source", "") or "mvlaw").lower()
        if src not in ("mvlaw", "gazette"):
            raise BadRequest(f"source {src!r}: use mvlaw or gazette")
        if src == "gazette":
            if any(filters.get(k) for k in ("status", "year")) or \
                    _http.clean(filters.get("category") or "law").lower() not in ("law", "laws", "act", "acts"):
                raise BadRequest("source=gazette takes search words only (no category/status/year filter)")
            return await self._gazette_search(_http.clean(query), limit, page)
        params = self._filter_params(filters)
        q = _http.clean(query)
        page = max(1, int(page))
        if q:
            limit = max(1, min(int(limit), SEARCH_PER_PAGE))
            note = ("Word search over titles, numbers and article text (Dhivehi); the source "
                    "returns only its 10 best hits, so refine the words or use filters. Acts MvLaw "
                    "lacks (many since 2008): filters={'source': 'gazette'}.")
            if page > 1:
                return Results(items=[], total=None, note=note)
            if params:
                # the site's word search ignores category/status/year, so list the filtered
                # set and match the words against titles and numbers here
                words = q.split()
                rows, n, capped = [], 1, ""
                while n <= 10:
                    leg = await self._list({**params, "page": n})
                    rows += [x for x in leg["data"]
                             if all(w in f"{_strip(x.get('title'))} {_strip(x.get('legislation_no'))}"
                                    for w in words)]
                    if not leg.get("next_page_url"):
                        break
                    n += 1
                else:
                    capped = " Only the first 200 filtered instruments were matched."
                return Results(items=[_hit(x) for x in rows[:limit]], total=len(rows),
                               note="Filtered by category/status/year; words matched against titles and "
                                    "numbers only (the source cannot combine filters with article-text "
                                    "search)." + capped)
            leg = await self._list({"filter[search]": q})
            return Results(items=[_hit(x) for x in leg["data"][:limit]], total=None, note=note)
        if not params:
            raise BadRequest("give search words (Dhivehi, or a number like '32/2021') or a filter "
                             "(category, status, year)")
        limit = max(1, min(int(limit), LIST_PER_PAGE))
        start = (page - 1) * limit
        p0 = start // LIST_PER_PAGE + 1
        leg = await self._list({**params, "page": p0})
        rows = leg["data"][start % LIST_PER_PAGE:]
        if len(rows) < limit and leg.get("next_page_url"):
            rows += (await self._list({**params, "page": p0 + 1}))["data"]
        return Results(items=[_hit(x) for x in rows[:limit]], total=leg.get("total"),
                       note="Listing in the site's order (oldest first).")

    # ---- one law ----

    @staticmethod
    def _norm_id(raw) -> str:
        m = _ID.match(str(raw or ""))
        if not m:
            raise BadRequest(f"law id {raw!r}: use the MvLaw id from search_legislation, e.g. '163' "
                             "(Civil Procedure Act 32/2021), or a Gazette id like 'gazette/7561'")
        return str(int(m[1]))

    async def _law(self, raw_id) -> dict:
        lid = self._norm_id(raw_id)
        if lid in _cache:
            return _cache[lid]
        r = await _http.get(f"{LIST}/{lid}")
        if r.status_code == 404:
            raise NotFound(f"no legislation {lid} on mvlaw.gov.mv (use search_legislation)")
        if r.status_code != 200:
            raise SourceError(f"mvlaw.gov.mv legislation {lid} failed", r.status_code)
        p = _page_data(r.text)
        leg = p.get("legislation") or {}
        if not isinstance(p.get("sections"), list) or str(leg.get("id")) != lid:
            raise SourceError(f"mvlaw.gov.mv legislation {lid}: unexpected payload", "bad data")
        latest = leg.get("latest_consolidation") or {}
        meta = {"Number": _strip(p.get("legislation_number")),
                "Version": _strip(p.get("consolidation_name")),
                "Took effect": _date(leg.get("implemented_at")),
                "Published": _date(leg.get("published_at")),
                "Status": _status(leg)}
        if leg.get("abolished_at"):
            meta["Abolished"] = _date(leg["abolished_at"])
        if p.get("original_document_url"):
            meta["Gazette copy (PDF)"] = p["original_document_url"]
        doc = {"id": lid, "title": _strip(leg.get("title")), "url": str(r.url),
               "as_of": _date(latest.get("implemented_at")),
               "blocks": _blocks(p["sections"]), "meta": {k: v for k, v in meta.items() if v}}
        return _http.lru_put(_cache, lid, doc, 4)

    async def _gazette(self, gid: str) -> dict:
        if gid in _gz_cache:
            return _gz_cache[gid]
        r = await _http.get(GZ_ITEM + gid)
        if r.status_code == 404:
            raise NotFound(f"no gazette item {gid} on gazette.gov.mv")
        if r.status_code != 200:
            raise SourceError(_http.error("gazette.gov.mv", f"item {gid} failed", r.status_code), r.status_code)
        pdf = re.search(r'href="(https://storage\.googleapis\.com/gazette\.gov\.mv/docs/gazette/\d+\.pdf)"', r.text)
        head = re.search(r'class="iulaan iulaan-title[^"]*">([^<]*)<', r.text)
        if 'class="gazette-type" href="/gazette?type=gaanoonu"' not in r.text:
            raise NotFound(f"gazette item {gid} is not a law (use search_legislation with source=gazette)")
        if not pdf:
            raise NotFound(f"gazette item {gid} has no PDF")
        p = await _http.get(pdf[1])
        if p.status_code != 200:
            raise SourceError(_http.error("gazette.gov.mv", f"PDF of item {gid} failed", p.status_code), p.status_code)
        text = _http.pdf_text(p.content)
        if not text:
            raise SourceError(f"gazette.gov.mv: PDF of item {gid} has no text layer")
        page_txt = _http.clean(re.sub(r"<[^>]+>", " ", r.text))
        title = _strip(head[1]) if head else f"Gazette {gid}"
        d = re.search(r"ޕަބްލިޝްކުރި ތާރީޚު:\s*(\d{1,2}\s+\S+\s+\d{4})", page_txt)
        vol = re.search(r"ވޮލިއުމް:\s*(\d+)\s*އިޝޫ:\s*(\d+)", page_txt)
        meta = {"Source": "Government Gazette, as published (not consolidated)",
                "Text quality": "PDF text layer; digits and brackets sometimes reversed, check the PDF",
                "Published": _gz_date(d[1]) if d else "",
                "Gazette volume / issue": f"{vol[1]} / {vol[2]}" if vol else "",
                "Gazette copy (PDF)": pdf[1]}
        doc = {"id": f"gazette/{gid}", "title": title, "url": GZ_ITEM + gid, "text": text,
               "pages": _gz_pages(text), "as_of": meta["Published"],
               "meta": {k: v for k, v in meta.items() if v}}
        return _http.lru_put(_gz_cache, gid, doc, 4)

    @staticmethod
    def _gz_id(raw) -> str | None:
        m = _GZ_ID.match(str(raw or ""))
        return m[1] if m else None

    async def get_legislation_toc(self, id):
        if gid := self._gz_id(id):
            g = await self._gazette(gid)
            return Toc(id=g["id"], title=g["title"], url=g["url"],
                       entries=[TocEntry(title=f"Page {i}: " + next((ln for ln in p.splitlines() if len(ln) > 8),
                                                                          p.splitlines()[0])[:80],
                                         provision=f"page {i}")
                                for i, p in enumerate(g["pages"], 1)])
        doc = await self._law(id)
        entries = [TocEntry(title=b["title"], level=b["level"],
                            provision=b["label"] if b["kind"] == "article" else "")
                   for b in doc["blocks"] if b["kind"] != "preamble"]
        return Toc(id=doc["id"], title=doc["title"], url=doc["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        if gid := self._gz_id(id):
            g = await self._gazette(gid)
            m = re.fullmatch(r"(?:page|p\.?|pg\.?)?\s*(\d{1,4})", _http.clean(provision), re.I)
            if not m or not 1 <= int(m[1]) <= len(g["pages"]):
                raise NotFound(f"Gazette texts open per PDF page: use 'page 1' to 'page {len(g['pages'])}'")
            n = int(m[1])
            return Provision(law_id=g["id"], law_title=g["title"], provision=f"page {n}",
                             text=f"## Page {n}\n\n_As published in the Gazette; PDF text layer, digits and "
                                  f"brackets sometimes reversed: {g['meta']['Gazette copy (PDF)']}_\n\n"
                                  f"{g['pages'][n - 1]}", url=g["url"], as_of=g["as_of"])
        doc = await self._law(id)
        label = _norm_provision(provision)
        b = next((b for b in doc["blocks"] if b["kind"] == "article" and b["label"] == label), None)
        if not b:
            nums = [a["label"] for a in doc["blocks"] if a["kind"] == "article"]
            have = (f"it has articles {nums[0]} to {nums[-1]}" if nums else "it has no numbered articles")
            raise NotFound(f"no article {provision!r} in MvLaw {doc['id']}: {have}; "
                           "see get_legislation_toc")
        return Provision(law_id=doc["id"], law_title=doc["title"], provision=b["label"],
                         text=_block_md(b), url=doc["url"], as_of=doc["as_of"])

    async def get_legislation_text(self, id):
        if gid := self._gz_id(id):
            g = await self._gazette(gid)
            return LawText(id=g["id"], title=g["title"], text=g["text"], url=g["url"],
                           as_of=g["as_of"], metadata=g["meta"])
        doc = await self._law(id)
        text = "\n\n".join(t for t in (_block_md(b) for b in doc["blocks"]) if t.strip())
        return LawText(id=doc["id"], title=doc["title"], text=text, url=doc["url"],
                       as_of=doc["as_of"], metadata=doc["meta"])
