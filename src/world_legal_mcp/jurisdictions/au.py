"""Australia (Commonwealth): legislation from the Federal Register of Legislation (FRL).

Legislation only. Case law is not available from an official source an honest client
can reach (checked 2026-11-05 from a UK IP):
  * High Court (www.hcourt.gov.au, Akamai): every request, robots.txt included, is reset
    (HTTP/2 INTERNAL_ERROR); eresources.hcourt.gov.au redirects there.
  * Federal Court (www.judgments.fedcourt.gov.au, www.fedcourt.gov.au): Cloudflare
    managed challenge (403 "Just a moment...") even for robots.txt.
  * AustLII is a non-profit, behind the same kind of challenge, and opts out of AI use.

Gotchas this code encodes (FRL OData v4 API at api.prod.legislation.gov.au/v1, the
undocumented backend of the legislation.gov.au site):
  * Search is TITLE search only: criteria text("<phrase>",name,contains) matches a phrase
    in the title, so each query word becomes its own clause, AND-ed. Body search
    (text(...,content/text,contains)) answers 400 "cannot parse text".
  * $filter works on `collection` only; isPrincipal/status filters answer 400.
    $orderby=searchContexts/text/relevance desc works but ranks weakly.
  * An unknown title id answers 400 "Cannot serialize a null 'Resource'", not 404.
  * Full text comes as one EPUB per compilation (all volumes inside; the Corporations Act
    is 7 XHTML files, ~23 MB). There is no per-section endpoint. The EPUB's NCX navMap
    is the TOC, with an anchor for every heading, so provisions are cut by anchor rather
    than by Word style names (which differ between old and new drafting templates).
    Every volume repeats the cover page and a TOC; those are dropped.
  * Section numbers restart in each Schedule (CCA s 18 vs Sch 2 s 18, the Australian
    Consumer Law), so schedule sections are labelled "Sch 2 s 18".
"""
from __future__ import annotations

import io
import re
import zipfile
from urllib.parse import quote

from lxml import etree, html as lxml_html

from .._http import clean, get, html_to_md, lru_put
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import LawHit, LawText, Provision, Results, Toc, TocEntry

API = "https://api.prod.legislation.gov.au/v1"
SITE = "https://www.legislation.gov.au"
_ID = re.compile(r"[CF]\d{4}[A-Z]\d{5}")
_COLLECTIONS = ("Act", "LegislativeInstrument", "NotifiableInstrument", "Constitution",
                "AdministrativeArrangementsOrder", "ContinuedLaw", "Gazette",
                "PrerogativeInstrument")
_STATUS = {"InForce": "in force", "Repealed": "repealed", "Ceased": "ceased",
           "NeverEffective": "never effective"}
_NCX = "{http://www.daisy.org/z3986/2005/ncx/}"
_BLOCKS = {"p", "table", "h1", "h2", "h3", "h4", "h5", "h6", "li", "pre"}
_SKIP_CLASS = re.compile(r"^(TOC|SpecialTOC|Header$)")
# Heading styles of the OPC Word templates (ActHead1-9) and the older one (HR = section /
# regulation heading), used only when the EPUB's NCX lists no headings (old compilations).
_HEAD_CLASS = {**{f"ActHead{n}": n - 1 for n in range(1, 10)}, "HR": 4}
_DOCS: dict = {}   # title id -> parsed compilation (small in-process cache)


def _law_url(law_id: str) -> str:
    return f"{SITE}/{law_id}/latest/text"


def _norm_id(law_id: str) -> str:
    m = _ID.search(str(law_id or "").upper())
    if not m:
        raise BadRequest(f"Bad Australian title id {law_id!r}: expected an FRL title id like "
                         "C2004A00109 (Competition and Consumer Act 2010) or F2006L03714.")
    return m[0]


async def _api(path: str, params: dict | None = None):
    r = await get(f"{API}/{path}", params=params, headers={"Accept": "application/json"})
    if r.status_code == 404 or (r.status_code == 400 and "null 'Resource'" in r.text):
        raise NotFound(f"Not found on the Federal Register of Legislation: {path}")
    if r.status_code != 200:
        raise SourceError(f"Federal Register of Legislation API: {clean(r.text)[:200]}",
                          r.status_code)
    return r


# --------------------------------------------------------------------------- #
# Search
# --------------------------------------------------------------------------- #
def _hit(t: dict) -> LawHit:
    number = f"No. {t['number']}, {t['year']}" if t.get("number") and t.get("year") else ""
    title = clean(t.get("name"))
    m = re.search(r"\b(1[89]\d\d|20\d\d)$", title)
    if number and m and t.get("collection") == "Act" and m.group(1) != str(t["year"]):
        # The register keeps the original enactment's number/date for a renamed Act
        # (e.g. Trade Practices Act 1974 -> Competition and Consumer Act 2010).
        number += " (original enactment, Act since renamed; number and date are from 1st enactment)"
    return LawHit(id=t["id"], title=title, type=t.get("collection") or "",
                  number=number, date=(t.get("makingDate") or "")[:10],
                  status=_STATUS.get(t.get("status"), t.get("status") or ""),
                  url=_law_url(t["id"]))


async def _search(query: str, collection: str | None, limit: int, page: int) -> Results:
    q = clean(query)
    if _ID.fullmatch(q.upper()):
        t = (await _api(f"titles('{q.upper()}')")).json()
        return Results(items=[_hit(t)], total=1)
    words = re.findall(r"[^\W_]+", q)
    if not words:
        raise BadRequest("Give words from the title, e.g. 'Competition and Consumer Act'.")
    clauses = ",".join(f'text("{w}",name,contains)' for w in words)
    criteria = quote(f"and({clauses},pointintime(Latest))", safe="(),")
    top = max(1, min(int(limit), 100))
    params = {"$top": str(top), "$skip": str((max(1, int(page)) - 1) * top), "$count": "true",
              # relevance ties come back in a different order per $top; name breaks them
              # (the API rejects id/makingDate as a secondary key)
              "$orderby": "searchContexts/text/relevance desc,name asc",
              "$select": "id,name,collection,status,makingDate,year,number"}
    if collection:
        if collection not in _COLLECTIONS:
            raise BadRequest(f"Unknown collection {collection!r}; use one of {', '.join(_COLLECTIONS)}.")
        params["$filter"] = f"collection eq '{collection}'"
    try:
        data = (await _api(f"titles/Search(criteria='{criteria}')", params)).json()
    except SourceError as e:
        if e.status == 400 and int(params["$skip"]) > 0:   # backend rejects a $skip past the end
            return Results(items=[], total=None,
                           note=f"Page {page} is past the end of the results; try a lower page.")
        raise
    return Results(items=[_hit(t) for t in data.get("value", [])], total=data.get("@odata.count"),
                   note="Title search: every word must be in the title (no full-text search). "
                        "No date filter (the register API cannot filter by year or making date): "
                        "results come by relevance, so check each date. Repealed titles are included.")


# --------------------------------------------------------------------------- #
# Compilation (EPUB) -> blocks + TOC
# --------------------------------------------------------------------------- #
def _label(text: str, schedule: str | None) -> str:
    """Provision label for a TOC heading, or '' for a pure heading."""
    m = re.match(r"Schedule\b\s*(\d+[A-Z]*)?", text)
    if m:
        return f"Sch {m[1]}" if m[1] else "Sch"
    m = re.match(r"Endnote\s+(\d+)\b", text)
    if m:
        return f"Endnote {m[1]}"
    m = re.match(r"(\d+[A-Z]*(?:\.\d+[A-Z]*)*)\.?\s+\S", text)   # Constitution: "51. Title"
    if m:
        return f"{schedule} s {m[1]}" if schedule else f"s {m[1]}"
    return ""


def _nav(ncx: bytes) -> list[dict]:
    """NCX navMap -> flat list of {title, depth, file, frag, label, schedule}."""
    root = etree.fromstring(ncx)
    out: list[dict] = []

    def walk(el, depth: int, schedule: str | None):
        for np_ in el.findall(f"{_NCX}navPoint"):
            title = clean("".join(np_.find(f"{_NCX}navLabel/{_NCX}text").itertext()))
            src = np_.find(f"{_NCX}content").get("src", "")
            file, _, frag = src.partition("#")
            if re.fullmatch(r"Volume \d+", title):   # multi-volume wrapper: transparent
                walk(np_, depth, schedule)
                continue
            label = _label(title, schedule)
            out.append({"title": title, "depth": depth, "file": file, "frag": frag,
                        "label": label})
            walk(np_, depth + 1, label if label.startswith("Sch") and " s " not in label
                 else schedule)

    walk(root.find(f"{_NCX}navMap"), 0, None)
    return out


def _block_text(el) -> str:
    if el.tag == "table":
        return html_to_md(etree.tostring(el, encoding="unicode", method="html"))
    return clean(el.text_content())


def _parse_file(data: bytes):
    """XHTML volume -> ([[text, skip]], {anchor id: block index}, [(block index, depth)])."""
    root = lxml_html.fromstring(data)
    body = root.find(".//body")
    body = root if body is None else body
    blocks: list[list] = []
    index: dict = {}
    anchors: dict[str, int] = {}
    pending: list[str] = []
    heads: list[tuple[int, int]] = []
    for el in body.iter():
        if not isinstance(el.tag, str):
            continue
        if el.tag in _BLOCKS and not any(a in index or a.tag == "table"
                                         for a in el.iterancestors()):
            index[el] = len(blocks)
            cls = el.get("class") or ""
            skip = bool(_SKIP_CLASS.match(cls))
            if cls in _HEAD_CLASS:
                heads.append((len(blocks), _HEAD_CLASS[cls]))
            blocks.append([_block_text(el), skip])
            for a in pending:
                anchors[a] = index[el]
            pending = []
        eid = el.get("id") or (el.get("name") if el.tag == "a" else None)
        if eid:
            owner = el if el in index else next((a for a in el.iterancestors() if a in index), None)
            if owner is None:
                pending.append(eid)
            else:
                anchors.setdefault(eid, index[owner])
    return blocks, anchors, heads


class _Doc:
    def __init__(self, law_id: str, meta: dict, version: dict, epub: bytes):
        self.id, self.title = law_id, clean(meta.get("name")) or law_id
        self.meta, self.version = meta, version
        z = zipfile.ZipFile(io.BytesIO(epub))
        names = z.namelist()
        ncx_name = next((n for n in names if n.endswith(".ncx")), None)
        if not ncx_name:
            raise SourceError("FRL EPUB has no NCX table of contents", "epub")
        base = ncx_name.rpartition("/")[0]
        nav = _nav(z.read(ncx_name))
        files: list[str] = []
        for n in nav:
            if n["file"] and n["file"] not in files:
                files.append(n["file"])
        self.blocks: list[list] = []   # [text, skip, heading-level or None]
        starts: dict[tuple[str, str], int] = {}
        file_start: dict[str, int] = {}
        styled: list[dict] = []
        for f in files:
            path = f"{base}/{f}" if base else f
            if path not in names:
                continue
            blocks, anchors, heads = _parse_file(z.read(path))
            off = len(self.blocks)
            file_start[f] = off
            self.blocks += [[t, s, None] for t, s in blocks]
            for a, i in anchors.items():
                starts[(f, a)] = off + i
            styled += [{"title": blocks[i][0], "depth": dp, "file": f, "start": off + i}
                       for i, dp in heads if blocks[i][0]]
        # Map TOC entries to block ranges.
        self.entries: list[dict] = []
        for n in nav:
            i = starts.get((n["file"], n["frag"])) if n["frag"] else file_start.get(n["file"])
            if i is None:
                continue
            self.entries.append({**n, "start": i})
        if not any(e["label"] for e in self.entries) and styled:
            self.entries, schedule = [], None   # old compilation: NCX has no headings
            for e in styled:
                label = _label(e["title"], schedule)
                if label.startswith("Sch") and " s " not in label:
                    schedule = label
                self.entries.append({**e, "label": label})
        # Volumes after the first repeat a cover page and TOC: skip up to their first heading.
        firsts = {}
        for e in self.entries:
            firsts.setdefault(e["file"], e["start"])
        for f, off in file_start.items():
            if f != files[0]:
                for b in self.blocks[off:firsts.get(f, off)]:
                    b[1] = True
        for k, e in enumerate(self.entries):
            nxt = next((x["start"] for x in self.entries[k + 1:] if x["depth"] <= e["depth"]),
                       len(self.blocks))
            e["end"] = max(nxt, e["start"] + 1)
            self.blocks[e["start"]][2] = min(6, e["depth"] + 2)
        self.labels: dict[str, dict] = {}
        for e in self.entries:
            if e["label"] and e["label"] not in self.labels:
                self.labels[e["label"]] = e

    def render(self, start: int, end: int) -> str:
        out = []
        for text, skip, level in self.blocks[start:end]:
            if skip or not text:
                continue
            out.append(f"{'#' * level} {text}" if level else text)
        return "\n\n".join(out)

    @property
    def as_of(self) -> str:
        return (self.version.get("start") or "")[:10]


async def _doc(law_id: str) -> _Doc:
    law_id = _norm_id(law_id)
    if law_id in _DOCS:
        return _DOCS[law_id]
    meta = (await _api(f"titles('{law_id}')")).json()
    try:
        version = (await _api(f"versions/find(titleId='{law_id}',asAtSpecification='Latest')")).json()
    except NotFound:
        version = {}
    r = await get(f"{API}/documents/find(titleid='{law_id}',asatspecification='Latest',"
                  "type='Primary',format='Epub',uniqueTypeNumber=0,volumeNumber=0,"
                  "rectificationVersionNumber=0)")
    if r.status_code != 200 or not r.content.startswith(b"PK"):
        raise SourceError(f"No EPUB text for {law_id} on the Federal Register of Legislation; "
                          f"see {_law_url(law_id)} (PDF/Word only?)", r.status_code)
    return lru_put(_DOCS, law_id, _Doc(law_id, meta, version, r.content), 3)


_PROV = re.compile(
    r"(?:(?:sch(?:edule)?\.?\s*(?P<sch>\d+[a-z]*)?)\s*,?\s*)?"
    r"(?:(?:s|ss|sec|sect|section|r|reg|regulation|rule|cl|clause|item)\.?\s*)?"
    r"(?P<num>\d+[a-z]*(?:\.\d+[a-z]*)*)?")


def _norm_provision(provision: str) -> str:
    s = clean(provision).lower()
    m = re.fullmatch(r"endnote\s*(\d+)", s)
    if m:
        return f"Endnote {m[1]}"
    m = _PROV.fullmatch(s)
    if not m or not (m["num"] or s.startswith("sch")):
        raise BadRequest(f"Bad provision {provision!r}: use a TOC label like 's 18', "
                         "'Sch 2 s 18', 'Sch 1' or 'Endnote 4' (also '18', 'section 18').")
    sch = ("Sch " + m["sch"].upper()) if m["sch"] else ("Sch" if s.startswith("sch") else "")
    if not m["num"]:
        return sch
    return f"{sch} s {m['num'].upper()}".strip()


# =========================================================================== #
# Adapter
# =========================================================================== #
class Australia(Jurisdiction):
    code = "au"
    name = "Australia"
    languages = ("en",)
    aliases = ("aus", "cth")
    sources = (
        Source("Federal Register of Legislation, Office of Parliamentary Counsel", SITE,
               covers=("legislation",),
               licence="CC BY 4.0 (attribute to the Federal Register of Legislation and link "
                       "legislation.gov.au; Coat of Arms and third-party material excluded)",
               commercial_use=True,
               ai_use=True,   # robots.txt (www): only Crawl-delay 10 + Disallow /assets/; API host has none
               auth="none",
               rate_limit="unknown (none published; API is the site's own backend); 1 s spacing, "
                          "no 429 seen in ~30 requests (2026-11-05)",
               terms_url=f"{SITE}/terms-of-use"),
    )
    legislation_filters = {
        "collection": "Act, LegislativeInstrument, NotifiableInstrument, Constitution, "
                      "AdministrativeArrangementsOrder, ContinuedLaw, Gazette, PrerogativeInstrument",
    }
    min_interval = {"api.prod.legislation.gov.au": 1.0}
    notes = ("Commonwealth legislation only (latest compilation). No case law: the High Court and "
             "Federal Court sites block non-browser clients, and AustLII is not official. "
             "Search matches title words only and cannot filter by date (no year_from/year_to). Ids are FRL title ids, e.g. C2004A00109 "
             "(Competition and Consumer Act 2010); schedule sections are 'Sch 2 s 18'.")
    gaps = (
        ("High Court judgments: hcourt.gov.au (Akamai) resets every request from this client "
         "(2026-11-05)"),
        "Federal Court judgments: Cloudflare managed challenge (403) even for robots.txt",
        ("State and territory legislation: Qld API needs a free key we have not signed up for; NSW"
         " Cloudflare; others not built"),
        ("State court judgments: NSW Caselaw robots.txt disallows /decision and /search; other "
         "states not researched yet"),
        ("Full-text search of Commonwealth legislation: FRL API answers 400 to body search; title "
         "search only"),
    )
    samples = {
        "legislation_query": "Competition and Consumer Act",
        "law_id": "C2004A00109",
        "provision": "s 18",
    }

    async def search_legislation(self, query, *, limit, page, filters):
        return await _search(query, filters.get("collection"), limit, page)

    async def get_legislation_toc(self, id):
        d = await _doc(id)
        return Toc(id=d.id, title=d.title, url=_law_url(d.id),
                   entries=[TocEntry(title=e["title"], level=e["depth"],
                                     provision=e["label"] if d.labels.get(e["label"]) is e else "")
                            for e in d.entries])

    async def get_legislation_provision(self, id, provision):
        d = await _doc(id)
        label = provision.strip() if provision.strip() in d.labels else _norm_provision(provision)
        e = d.labels.get(label)
        if e is None:
            others = [k for k in d.labels if k.endswith(f" {label}") and k != label]
            hint = f" Did you mean {', '.join(others[:5])}?" if others else ""
            raise NotFound(f"{label} not found in {d.title} ({d.id}).{hint}")
        return Provision(law_id=d.id, law_title=d.title, provision=label,
                         text=d.render(e["start"], e["end"]), url=_law_url(d.id), as_of=d.as_of)

    async def get_legislation_text(self, id):
        d = await _doc(id)
        v = d.version
        meta = {k: str(val) for k, val in (
            ("Collection", d.meta.get("collection")),
            ("Status", _STATUS.get(d.meta.get("status"), d.meta.get("status"))),
            ("Compilation", v.get("compilationNumber")),
            ("Register id", v.get("registerId"))) if val}
        return LawText(id=d.id, title=d.title, text=d.render(0, len(d.blocks)),
                       url=_law_url(d.id), as_of=d.as_of, metadata=meta)
