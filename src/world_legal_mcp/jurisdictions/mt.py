"""Malta: consolidated legislation from Legislation Malta (legislation.mt). No case law.

Gotchas this code encodes:
  * Search is the JSON behind the "Consolidated laws" DataTable:
    `POST /Legislations/LegislationPartial` with DataTables form fields (draw, start, length,
    order[0][column]) plus `search[TitleString]` (title words) or `search[ChapterString]`
    (chapter number). Without a search string it errors. `recordsFiltered` is the hit count
    (`recordsTotal` is only the page size). Only titles are searched, not the text.
  * Language comes from the `_culture` cookie (en-GB / mt-MT), not Accept-Language; without
    it titles and links come back in Maltese.
  * Laws are ELI-addressed: `eli/cap/{n}` (Acts, "Cap."), `eli/sl/{n.m}` (subsidiary
    legislation, "S.L." with the leading zero dropped: S.L. 16.07 = sl/16.7, S.L. 16.10 =
    sl/16.10), `eli/const` (Constitution). `{eli}/{eng|mlt}/portalpdf` is an HTML page with
    ELI RDFa (title, current version date, in-force flag); `{eli}/{eng|mlt}/pdf` is the
    consolidated PDF. `/html` and `/xml` do not work (2026-11). An unknown id gives HTTP 200
    with a "not found" HTML page, so check the RDFa / content type.
  * The text exists only as a typeset PDF (FrameMaker) with marginal notes (headings,
    "Amended by:" lists, cross-references) in a side column: left on even pages, right on
    odd pages. pypdf's layout mode keeps that geometry; we split the columns per page, drop
    the running header, and cut articles at "N." lines in ascending order. Marginal notes
    become the article heading and an "Amended by" line. Schedules are one provision each.
  * The Civil Code PDF is 5 MB / 615 pages and takes ~10 s to fetch and parse; parsed laws
    are kept in a small in-memory cache.
  * Case law is left out: ecourts.gov.mt (Judgements) answers with a Cloudflare
    "you have been blocked" 403, even for robots.txt (checked 2026-11-05/06).
"""
from __future__ import annotations

import asyncio
import io
import re

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import LawHit, LawText, Provision, Results, Toc, TocEntry

BASE = "https://legislation.mt"
SEARCH = f"{BASE}/Legislations/LegislationPartial"
MAX_LIMIT = 100
MAX_FETCH = 500
_LANGS = {"en": ("eng", "en-GB"), "mt": ("mlt", "mt-MT")}
_ORD = ("FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH|SEVENTH|EIGHTH|NINTH|TENTH|ELEVENTH|TWELFTH|"
        "THIRTEENTH|FOURTEENTH|FIFTEENTH")
_SCHEDULE = re.compile(rf"^(?:(?:{_ORD})\s+)?SCHEDULE(?:\s+[A-Z0-9]{{1,4}})?$|^(?:L-)?SKEDA\b.{{0,30}}$")
_HEADING = re.compile(r"^(?:PART|Part|TITLE|Title|SUB-TITLE|Sub-title|Sub-Title|SUB-PART|Sub-Part|"
                      r"BOOK|Book|CHAPTER|Chapter|PARTI|Parti|TITOLU|Titolu|Sub-titolu|KTIEB|Ktieb|"
                      r"KAPITOLU|Kapitolu|TAQSIMA|Taqsima)\s+[IVXLC\d]+[A-Z]?\*?"
                      r"(?:\s*[-–:.]\s*[^;]{0,70}|\s+[^a-z;]{0,70})?$")
_ART = re.compile(r"^(\d{1,4})([A-Z]{0,3})\.(?:\s*\*)?(?:\s+|(?=\())(\S.*)$")
_NOTE_META = re.compile(r"^(?:Amended|Added|Substituted|Renumbered|Deleted|Repealed|Emendat|Miżjud|"
                        r"Sostitwit|Imħassar|Substitued|Cap\s?\.|Kap\.|S\.L\.|L\.S\.|L\.N\.|A\.L\.|"
                        r"[IVXLC]+\s?\.\s?\d{4})")
_PARA = re.compile(r"""^(?:\(\w{1,6}\)|\d+[A-Z]{0,3}\.\s|Provided\b|Iżda\b|["“'‘]{1,2}\w)""")

_cache: dict = {}


# ---------- ids ----------

def _norm_id(raw: str) -> tuple[str, str]:
    """User id -> (eli path, eli language): 'Cap. 16' -> ('cap/16', 'eng')."""
    s = _http.clean(raw)
    lang = "eng"
    m = re.search(r"(?:^|/)eli/(.+)$", s)
    if m:
        s = m[1]
    parts = [p for p in s.strip("/").split("/") if p]
    tail = []
    while parts and parts[-1].lower() in ("eng", "mlt", "pdf", "portalpdf", "html", "xml"):
        tail.append(parts.pop().lower())
    if "mlt" in tail:
        lang = "mlt"
    s = "/".join(parts)
    low = s.lower().replace(" ", "")
    if low in ("const", "constitution"):
        return "const", lang
    m = re.fullmatch(r"(?:cap/|cap\.?|chapter|kap\.?|kapitolu)?(\d+[a-z]?)", low)
    if m:
        return f"cap/{m[1].upper() if m[1][-1].isalpha() else m[1]}", lang
    m = re.fullmatch(r"(?:sl/|s\.?l\.?|l\.?s\.?)?(\d+[a-z]?)\.(\d+[a-z]?)", low)
    if m:
        sub = m[2].lstrip("0") or "0"
        return f"sl/{m[1]}.{sub}", lang
    m = re.fullmatch(r"sl/(\d+[a-z]?|const\.\d+)", low)
    if m:
        return f"sl/{m[1]}", lang
    raise BadRequest(f"law id {raw!r}: use an id from search_legislation, e.g. 'cap/16' "
                     "(Civil Code, also 'Cap. 16'), 'sl/16.8' (S.L. 16.08) or 'const'; "
                     "add '/mlt' for the Maltese text")


def _public_id(eli: str, lang: str) -> str:
    return eli if lang == "eng" else f"{eli}/mlt"


# ---------- PDF layout parsing ----------

def _indent(line: str) -> int:
    return len(line) - len(line.lstrip())


_PAGE_NO_LEFT = re.compile(r"^\s*\d+\s{2,}\S")
_PAGE_NO_RIGHT = re.compile(r"\S\s{2,}\d+\s*$")


def _page_lines(page: str) -> list[tuple[str, str]]:
    """One layout-mode page -> [(body line with indentation, marginal note)], header dropped."""
    lines = page.split("\n")
    # running header: leading lines up to the one that carries the page number
    even = False
    nonblank = [i for i, ln in enumerate(lines) if ln.strip()][:3]
    for i in nonblank:
        if _PAGE_NO_LEFT.match(lines[i]) or _PAGE_NO_RIGHT.search(lines[i]):
            even = bool(_PAGE_NO_LEFT.match(lines[i]))
            lines = lines[i + 1:]
            break
    out: list[tuple[str, str]] = []
    if even:
        col = min((_indent(ln) for ln in lines if ln.strip() and _indent(ln) >= 8), default=0)
        # body lines that share a row with a note are never indented, so the body column also
        # shows where the wide gaps of the note rows end
        ends = [g.end() for ln in lines if ln.strip() and _indent(ln) < 8
                for g in [next(re.finditer(r"\s{3,}", ln[5:]), None)] if g and ln[5 + g.end():].strip()]
        ends = [e + 5 for e in ends if e + 5 >= 15]
        if ends and col:
            col = min(col, max(ends, key=lambda e: (ends.count(e), -e)))
        for ln in lines:
            if (col and ln.strip() and _indent(ln) < col - 3
                    and ln[col - 1:col] == " " and ln[col:col + 1].strip() and ln[:col - 1].strip()
                    and not any(g.end() >= col - 4 and g.start() > 0 for g in re.finditer(r"\s{3,}", ln))):
                out.append(("  " + ln[col:].rstrip(), _http.clean(ln[:col - 1])))   # note | narrow gutter | body
            elif col and ln.strip() and _indent(ln) < col - 3:
                # note, gap, body: split at the first gap that ends in the body column, so a
                # wide space inside the note ("Violence   and") stays in the note
                m = next((g for g in re.finditer(r"\s{3,}", ln) if g.start() > 0 and (
                    g.end() >= col - 4 or re.match(r"\d{1,4}[A-Z]{0,3}\.\s{2,}\S", ln[g.end():]))), None)
                m = (ln[:m.start()], ln[m.end():]) if m and ln[m.end():].strip() else None
                if not m:
                    m = (ln, None)
                else:
                    m = (m[0].strip(), m[1])
                start = len(ln) - len(m[1]) if m[1] else 0
                body = (" " * start + m[1])[min(col - 2, start):].rstrip() if m[1] else ""
                out.append((body, _http.clean(m[0])))
            else:
                out.append((ln.rstrip(), ""))
    else:
        cand = [re.match(r"^(.*?)(\s{5,})(\S(?:\S| {1,4}\S){0,45})\s*$", ln) for ln in lines]
        cand = [m if m and len(m[1]) + len(m[2]) >= 60 else None for m in cand]
        starts = [m.start(3) for m in cand if m]
        col = max(starts, key=lambda c: (starts.count(c), c), default=0)   # the notes column of this page
        for ln, m in zip(lines, cand):
            if m and m.start(3) >= col - 2:    # a wide gap inside a justified body line is no note
                out.append((m[1].rstrip(), _http.clean(m[3])))
            else:
                out.append((ln.rstrip(), ""))
    return out


def _art_key(num: str, suf: str) -> tuple[int, str]:
    return int(num), suf


def _arrangement(blocks: list[dict]) -> bool:
    """True when the articles found so far look like a table of contents (one-liners)."""
    arts = [b for b in blocks if b["kind"] == "article"]
    sizes = sorted(len(b["lines"]) for b in arts)
    return len(arts) >= 3 and sizes[len(sizes) // 2] <= 2


def _parse(pages: list[str]) -> list[dict]:
    """Layout pages -> blocks: {kind: preamble|heading|article|schedule, label, title, lines}."""
    blocks: list[dict] = [{"kind": "preamble", "label": "", "title": "", "lines": [], "notes": []}]
    last: tuple[int, str] | None = None
    in_schedule = False
    for page in pages:
        rows = _page_lines(page)
        body = [_indent(b) for b, _ in rows if b.strip()]
        base = min(body) if body else 0
        for b, note in rows:
            text = _http.clean(b)
            cur = blocks[-1]
            if not text:
                if note:
                    cur["notes"].append(note)
                continue
            ind = _indent(b) - base
            m = _ART.match(text)
            if (m and ind <= 16 and last is not None
                    and (m[1], m[2]) == ("1", "") and _arrangement(blocks)):
                for blk in blocks:                     # that was the "Arrangement" list: restart
                    if blk["kind"] in ("article", "schedule"):
                        blk.update(kind="preamble", label="", title="")
                last, in_schedule = None, False
            if (not in_schedule and m and ind <= 16
                    and (last is None and int(m[1]) <= 2
                         or last is not None and (_art_key(m[1], m[2]) > last)
                         and int(m[1]) - last[0] <= 150)):
                last = _art_key(m[1], m[2])
                blocks.append({"kind": "article", "label": m[1] + m[2], "title": "",
                               "lines": [(ind, text)], "notes": [note] if note else []})
                continue
            if last is not None and _SCHEDULE.match(text):
                in_schedule = True
                label = text.title() if text.isupper() else text
                blocks.append({"kind": "schedule", "label": label, "title": label,
                               "lines": [], "notes": [note] if note else []})
                continue
            if ind >= 10 and _HEADING.match(text) and cur["kind"] != "schedule":
                if cur["kind"] == "heading" and not cur["lines"]:
                    cur["title"] += " – " + text
                else:
                    blocks.append({"kind": "heading", "label": "", "title": text, "lines": [], "notes": []})
                continue
            if (cur["kind"] == "heading" and not cur["lines"] and ind >= 10 and len(text) <= 80
                    and text.upper() == text and re.search(r"[A-Z]", text)):
                cur["title"] += " – " + text          # "Sub-title II" + "OF ANNUITIES"
                continue
            if cur["kind"] == "heading":               # body text after a heading: open a free block
                blocks.append({"kind": "preamble", "label": "", "title": "", "lines": [], "notes": []})
                cur = blocks[-1]
            cur["lines"].append((ind, text))
            if note:
                cur["notes"].append(note)
    carry: list[str] = []            # start of the next article's marginal title, wrapped over a row early
    prev = blocks[0]
    for blk in blocks:
        if carry and not (blk["kind"] == "article" and blk["notes"] and blk["notes"][0][:1].islower()):
            prev["meta"] = _http.clean(" ".join([prev["meta"], *carry]))   # no continuation follows
            carry = []
        if blk["kind"] in ("article", "heading"):
            head, rest, sub, over = [], [], [], []
            notes = carry + [p for n in blk["notes"]
                             for p in re.split(rf"(?<=\.)\s+(?={_NOTE_META.pattern[1:]})", n, maxsplit=1)]
            carry = []
            glued = []                                 # "XV.2009Destructio n, ...": amendment ref glued to a title
            for i, n in enumerate(notes):
                g = re.match(r"^([IVXLC]+\.\d{4})(?=[A-Z][a-z])(.+)$", n)
                if g:
                    glued.append(g[1])
                    notes[i] = g[2]
            for n in notes:
                if rest or _NOTE_META.match(n):
                    rest.append(n)
                elif blk["kind"] == "heading" or (head and head[-1].endswith(".")):
                    sub.append(n)                      # a sub-section title; only an unfinished end is kept
                else:
                    head.append(n)
            # a meta list ends at a line with a "."; digit-less lines after that are another title
            j = max((i for i, n in enumerate(rest) if _NOTE_META.match(n) or re.search(r"\d", n)), default=-1)
            if j >= 0 and rest[j].endswith(".") and j + 1 < len(rest):
                over, rest = rest[j + 1:], rest[:j + 1]
            if over and not over[-1].endswith("."):
                carry = over                           # unfinished: the next article's row ends it
            elif over:
                pass                                   # sub-section titles after an amendments list
            elif sub and not sub[-1].endswith("."):
                carry = sub[max((i for i, n in enumerate(sub) if n.endswith(".")), default=-1) + 1:]
            blk["title"] = _http.clean(" ".join(head)).rstrip() if blk["kind"] == "article" else blk["title"]
            blk["meta"] = _http.clean(" ".join([*glued, *rest]))
        else:
            blk["meta"] = _http.clean(" ".join(blk["notes"]))
        prev = blk
    return blocks


def _paragraphs(lines: list[tuple[int, str]]) -> list[str]:
    paras: list[str] = []
    for ind, text in lines:
        if not paras or _PARA.match(text) or (ind >= 2 and re.search(r"[.;:]$", paras[-1])):
            paras.append(text)
        else:
            paras[-1] += " " + text
    return [_http.clean(p) for p in paras]


def _block_md(blk: dict) -> str:
    if blk["kind"] == "heading":
        return f"## {blk['title']}"
    out = []
    if blk["kind"] == "article":
        out.append(f"### {blk['label']}." + (f" {blk['title']}" if blk["title"] else ""))
    elif blk["kind"] == "schedule":
        out.append(f"## {blk['title']}")
    out += _paragraphs(blk["lines"])
    if blk["meta"]:
        out.append(f"_{blk['meta']}_")
    return "\n\n".join(p for p in out if p)


def _layout_pages(data: bytes) -> list[str]:
    from pypdf import PdfReader
    return [p.extract_text(extraction_mode="layout") or "" for p in PdfReader(io.BytesIO(data)).pages]


# ---------- adapter ----------

class Malta(Jurisdiction):
    code = "mt"
    name = "Malta"
    languages = ("en", "mt")
    aliases = ("mlt", "malta")
    sources = (
        Source("Legislation Malta (legislation.mt), Office of the State Advocate / Legislation Unit",
               BASE,
               covers=("legislation",),
               licence="unknown: '© Copyright: Office of the State Advocate'; no terms of use or "
                       "re-use licence published (FAQ/privacy/cookie pages checked 2026-11)",
               commercial_use=None,
               ai_use=None,    # robots.txt only disallows Sogou; no AI/TDM opt-out found
               auth="none",
               rate_limit="unknown; 1 s spacing, no 429 seen in ~20 requests (2026-11)",
               terms_url=f"{BASE}/Home/FAQList"),
    )
    legislation_filters = {
        "language": "en (default) or mt: language of titles and texts",
    }
    min_interval = {"legislation.mt": 1.0}
    notes = ("Legislation only: consolidated Acts ('cap/16' = Civil Code), subsidiary legislation "
             "('sl/16.8' = S.L. 16.08) and the Constitution ('const'), English or Maltese, parsed "
             "from the official PDFs. Search matches titles only. No case law (eCourts blocks bots).")
    gaps = (
        "Case law of all courts (ecourts.gov.mt): Cloudflare 'you have been blocked' 403, even "
         "for robots.txt (2026-11-05/06)",
        "Acts and legal notices as published (Government Gazette), and past versions of laws: not"
         " researched yet",
    )
    samples = {
        "legislation_query": "civil code",
        "law_id": "cap/452",
        "provision": "36",
    }

    # ---- search ----

    async def search_legislation(self, query, *, limit=20, page=1, filters=None):
        filters = filters or {}
        lang = str(filters.get("language") or "en").lower()
        if lang not in _LANGS:
            raise BadRequest(f"language {lang!r}: use 'en' or 'mt'")
        eli_lang, culture = _LANGS[lang]
        q = _http.clean(query)
        if not q:
            raise BadRequest("give title words (e.g. 'civil code') or a chapter number (e.g. '16')")
        limit = max(1, min(int(limit), MAX_LIMIT))
        page = max(1, int(page))
        # the source sorts by chapter number only (S.L.s of old chapters before the Acts), so
        # fetch every title hit and rank here: Acts first, title starting with the query next
        data = {"draw": "1", "start": "0", "length": str(MAX_FETCH),
                "order[0][column]": "1", "order[0][dir]": "asc"}
        chap = re.fullmatch(r"(?i)(?:cap\.?|chapter|kap\.?)\s*(\d+[A-Za-z]?)", q) or re.fullmatch(r"\d+[A-Za-z]?", q)
        if chap:
            data["search[ChapterString]"] = chap[1] if chap.lastindex else chap[0]
        else:
            data["search[TitleString]"] = q
        r = await _http.post(SEARCH, data=data, headers={"Cookie": f"_culture={culture}"})
        if r.status_code != 200 or "json" not in r.headers.get("content-type", ""):
            raise SourceError("legislation.mt search failed", r.status_code)
        js = r.json()
        items = []
        rows = js.get("data") or []
        if not chap:
            def rank(it):
                title = _http.clean(re.sub(r"<[^>]*>", " ", it.get("ChapterTitle") or "")).lower()
                ref = _http.clean(it.get("ChapterText"))
                return (title.endswith(")") and "repealed" in title or ref.endswith("(R)"),
                        not ref.startswith("Cap."), not title.startswith(q.lower()))
            rows = sorted(rows, key=rank)          # stable: ties keep the chapter order
        for it in rows[(page - 1) * limit:page * limit]:
            m = re.match(r"/?eli/(.+?)/(eng|mlt)/", (it.get("URL") or "").lstrip("/") + "/")
            if not m:
                continue
            eli, l = m[1], m[2]
            ref = _http.clean(it.get("ChapterText"))
            items.append(LawHit(
                id=_public_id(eli, l), title=_http.clean(re.sub(r"<[^>]*>", " ", it.get("ChapterTitle") or "")) or ref,
                type="Chapter" if eli.startswith("cap/") else
                     "Subsidiary Legislation" if eli.startswith("sl/") else "Constitution",
                number=ref, url=f"{BASE}/eli/{eli}/{l}"))
        return Results(items=items, total=js.get("recordsFiltered"),
                       note="Searches titles only (not the text); a chapter number like '16' finds Cap. 16. "
                            "Acts (Cap.) are listed before subsidiary legislation, repealed laws last; "
                            "the source gives no enactment or amendment dates, so results cannot be "
                            "filtered or sorted by year.")

    # ---- documents ----

    async def _meta(self, eli: str, lang: str) -> dict:
        url = f"{BASE}/eli/{eli}/{lang}/portalpdf"
        r = await _http.get(url, headers={"Cookie": f"_culture={_LANGS['mt' if lang == 'mlt' else 'en'][1]}"})
        if r.status_code == 404:
            raise NotFound(f"no Maltese law {eli}")
        if r.status_code != 200:
            raise SourceError("legislation.mt page failed", r.status_code)
        html = r.text
        if f'about="mlt:eli/{eli}"' not in html:
            raise NotFound(f"no law '{eli}' on legislation.mt (try search_legislation)")
        title = ""
        for m in re.finditer(r'about="mlt:eli/[^"]+/(\d{8})/(eng|mlt)"\s+property="eli:title"\s+content="([^"]*)"', html):
            if m[2] == lang or not title:
                title = _http.clean(m[3].replace("&#39;", "'").replace("&amp;", "&"))
        dates = re.findall(rf'mlt:eli/{re.escape(eli)}/(\d{{8}})/{lang}"', html)
        d = max(dates) if dates else ""
        in_force = re.search(r'property="eli:in_force"\s+resource="eli:InForce-(\w+)"', html)
        return {"title": title or eli, "as_of": f"{d[:4]}-{d[4:6]}-{d[6:]}" if d else "",
                "status": in_force[1] if in_force else "", "url": f"{BASE}/eli/{eli}/{lang}"}

    async def _doc(self, raw_id: str) -> dict:
        eli, lang = _norm_id(raw_id)
        key = (eli, lang)
        if key in _cache:
            return _cache[key]
        meta = await self._meta(eli, lang)
        r = await _http.get(f"{BASE}/eli/{eli}/{lang}/pdf")
        if r.status_code != 200:
            raise SourceError("legislation.mt PDF download failed", r.status_code)
        if not r.content.startswith(b"%PDF"):
            raise NotFound(f"legislation.mt has no PDF for {eli} ({lang})")
        pages = await asyncio.to_thread(_layout_pages, r.content)
        blocks = _parse(pages)
        if not any(len(b["lines"]) for b in blocks):
            raise SourceError("the PDF has no text layer (scanned); open it at the url", "no text")
        doc = {"id": _public_id(eli, lang), **meta, "blocks": blocks}
        return _http.lru_put(_cache, key, doc, 4)

    async def get_legislation_toc(self, id):
        doc = await self._doc(id)
        entries = []
        for b in doc["blocks"]:
            if b["kind"] == "heading":
                entries.append(TocEntry(title=b["title"], level=0))
            elif b["kind"] == "article":
                entries.append(TocEntry(title=f"{b['label']}." + (f" {b['title']}" if b["title"] else ""),
                                        level=1, provision=b["label"]))
            elif b["kind"] == "schedule":
                entries.append(TocEntry(title=b["title"], level=0, provision=b["label"]))
        return Toc(id=doc["id"], title=doc["title"], url=doc["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        doc = await self._doc(id)
        p = _http.clean(provision)
        low = re.sub(r"^(?:art(?:icle|ikolu)?|reg(?:ulation)?|rule|section|s|r|para(?:graph)?)\.?\s*",
                     "", p, flags=re.I).strip().rstrip(".")
        for b in doc["blocks"]:
            if b["kind"] == "article" and b["label"].lower() == low.lower():
                break
            if b["kind"] == "schedule" and re.sub(r"\s+", " ", b["label"]).lower() in (
                    p.lower(), f"{p.lower()} schedule"):
                break
        else:
            raise NotFound(f"no provision {provision!r} in {doc['id']}: use a label from "
                           "get_legislation_toc, e.g. '36', '66A' or 'First Schedule'")
        return Provision(law_id=doc["id"], law_title=doc["title"], provision=b["label"],
                         text=_block_md(b), url=doc["url"], as_of=doc["as_of"])

    async def get_legislation_text(self, id):
        doc = await self._doc(id)
        text = "\n\n".join(md for md in (_block_md(b) for b in doc["blocks"]) if md)
        meta = {"status": doc["status"]} if doc["status"] else {}
        return LawText(id=doc["id"], title=doc["title"], text=text, url=doc["url"],
                       as_of=doc["as_of"], metadata=meta)
