"""Hong Kong: legislation from the Department of Justice's Hong Kong e-Legislation
(HKeL) open data on DATA.GOV.HK. No case law (see below).

Gotchas this code encodes:
  * www.elegislation.gov.hk itself is closed to us: robots.txt (checked 2026-11-05)
    is `User-agent: * / Disallow: /` (only `/` and `/sitemap` allowed), and pages sit
    behind a JavaScript client check. So we never fetch it; its URLs are only shown
    to the user as the human-readable original.
  * The same texts are published as open data on DATA.GOV.HK (DoJ datasets
    hk-doj-hkel-legislation-current / hk-doj-hkel-list-of-legislation-current):
    a ~2 MB JSON index of every chapter, and the XML texts packed in ZIPs of
    50-560 MB. resource.data.one.gov.hk serves those ZIPs with HTTP Range support,
    so we read only the ZIP's central directory (~150 KB, cached in memory) and
    then the one compressed member we need (tens to hundreds of KB). No bulk
    download, no disk cache.
  * The index's FileName does not always match the member name in the ZIP
    (instruments: "cap_A101_..." in the index, "A101_..." in the ZIP), and the ZIP
    may be newer than the index, so members are matched by cap number + language.
  * Ordinances and subsidiary legislation are structured XML (HKLM schema:
    part/division/section/subsection/paragraph, schedule). Instruments (Basic Law,
    PRC Constitution, ...) are layout tables; for those, articles are split on the
    bold "Article N" / "第N條" lines.
  * Identifiers follow HKeL's own paths: "cap622", "cap4A", "A101", with an
    optional language suffix "!en" (default), "!zh-Hant" or "!zh-Hans".

Case law: the Judiciary's Legal Reference System (legalref.judiciary.hk) has
robots.txt `User-Agent: * / Disallow: /`; HKLII (hklii.hk, non-official, HKU)
is a SPA whose only data route is /api, which its robots.txt disallows. Neither
is used.
"""
from __future__ import annotations

import re
import struct
import time
import zlib

from lxml import etree

from .._http import clean, get, localname, lru_put, text
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import LawHit, LawText, Provision, Results, Toc, TocEntry

DATA = "https://resource.data.one.gov.hk/doj/data"
HKEL = "https://www.elegislation.gov.hk"
_LANGS = ("en", "zh-Hant", "zh-Hans")
_LIST_TTL = 6 * 3600
_STATUS = {"InEffect": "in effect", "NoLongerInEffect": "no longer in effect",
           "NotYetInEffect": "not yet in effect"}
_TYPES = {"O": "Ordinance", "S": "Subsidiary legislation", "I": "Instrument"}
_TITLE_KEY = {"en": "ChapterTitleEnglish", "zh-Hant": "ChapterTitleTraditionalChinese",
              "zh-Hans": "ChapterTitleSimplifiedChinese"}

_list_cache: dict[str, tuple[float, dict]] = {}       # lang -> (fetched, {CAPNO: chapter})
_cd_cache: dict[str, tuple[int, dict]] = {}           # zip url -> (size, {name: entry})
_doc_cache: dict[str, tuple] = {}                     # law id -> (meta, root)


# =========================================================================== #
# Remote ZIP reading via HTTP Range (shareable: any adapter facing a huge ZIP
# on a server with Accept-Ranges could use it)
# =========================================================================== #
async def _range(url: str, start: int, end: int | None = None) -> tuple[bytes, int]:
    rng = f"bytes={start}-{'' if end is None else end}" if start >= 0 else f"bytes={start}"
    r = await get(url, headers={"Range": rng})
    if r.status_code != 206:
        raise SourceError(f"HKeL open data: expected a partial response for {url}",
                          r.status_code)
    total = int((r.headers.get("content-range", "").rsplit("/", 1) + ["0"])[1] or 0)
    return r.content, total


async def _central_directory(url: str) -> tuple[int, dict]:
    if url in _cd_cache:
        return _cd_cache[url]
    tail, size = await _range(url, -65536)
    i = tail.rfind(b"PK\x05\x06")
    if i < 0:
        raise SourceError(f"HKeL open data: no ZIP directory in {url}")
    n, cd_size, cd_off = struct.unpack("<HII", tail[i + 10:i + 20])
    if cd_off >= size - len(tail):   # directory already inside the tail we read
        cd = tail[cd_off - (size - len(tail)):][:cd_size]
    else:
        cd, _ = await _range(url, cd_off, cd_off + cd_size - 1)
    entries, p = {}, 0
    while p + 46 <= len(cd) and cd[p:p + 4] == b"PK\x01\x02":
        (meth, csize, usize, fl, el, cl, off) = (
            struct.unpack("<H", cd[p + 10:p + 12])[0], *struct.unpack("<II", cd[p + 20:p + 28]),
            *struct.unpack("<HHH", cd[p + 28:p + 34]), struct.unpack("<I", cd[p + 42:p + 46])[0])
        name = cd[p + 46:p + 46 + fl].decode("utf-8", "replace")
        entries[name.replace("\\", "/").rsplit("/", 1)[-1]] = (off, csize, usize, meth, fl)
        p += 46 + fl + el + cl
    return lru_put(_cd_cache, url, (size, entries), 8)


async def _zip_member(url: str, name: str, entry) -> bytes:
    off, csize, _usize, meth, fl = entry
    blob, _ = await _range(url, off, off + 30 + fl + 1024 + csize)
    if blob[:4] != b"PK\x03\x04":
        _cd_cache.pop(url, None)   # ZIP replaced since we read its directory
        raise SourceError("HKeL open data: ZIP changed while reading; please retry")
    nlen, elen = struct.unpack("<HH", blob[26:30])
    data = blob[30 + nlen + elen:30 + nlen + elen + csize]
    if meth == 0:
        return data
    if meth == 8:
        return zlib.decompress(data, -15)
    raise SourceError(f"HKeL open data: unsupported ZIP compression {meth} for {name}")


# =========================================================================== #
# Index (list of legislation) and ids
# =========================================================================== #
async def _index(lang: str) -> dict:
    hit = _list_cache.get(lang)
    if hit and time.time() - hit[0] < _LIST_TTL:
        return hit[1]
    r = await get(f"{DATA}/hkel_list_c_all_{lang}.json")
    if r.status_code != 200:
        raise SourceError("HKeL open data: list of legislation unavailable", r.status_code)
    try:
        chapters = r.json()["Chapter"]
    except (ValueError, KeyError) as e:
        raise SourceError(f"HKeL open data: unexpected list format ({e})") from e
    idx = {c["CapNo"].upper(): c for c in chapters if c.get("CapNo")}
    _list_cache[lang] = (time.time(), idx)
    return idx


_ID_RE = re.compile(r"^(?:/?hk/)?(?:cap(?:ter)?\.?\s*|chapter\s*|instrument\s*)?"
                    r"([A-Z]?\d+[A-Z]{0,2})(?:!(en|zh-hant(?:-hk)?|zh-hans(?:-cn)?))?$", re.I)


def _parse_id(law_id: str) -> tuple[str, str]:
    """'cap622', 'Cap. 622', '622', 'cap4A!zh-Hant', 'A101', 'Instrument A101' -> (CAPNO, lang)."""
    s = re.sub(r"^https?://www\.elegislation\.gov\.hk/", "", clean(law_id))
    s = re.sub(r"^第\s*(\w+)\s*章$", r"\1", s)
    m = _ID_RE.match(s.replace(" !", "!"))
    if not m:
        raise BadRequest(f"invalid Hong Kong law id {law_id!r}. Use HKeL's chapter id, e.g. "
                         '"cap622" (Companies Ordinance), "cap4A", "A101" (Basic Law); '
                         'add "!zh-Hant" or "!zh-Hans" for the Chinese text.')
    lang = (m[2] or "en").lower()
    lang = "zh-Hant" if lang.startswith("zh-hant") else "zh-Hans" if lang.startswith("zh-hans") else "en"
    cap = m[1].upper()
    return cap, lang


def _make_id(cap: str, lang: str) -> str:
    base = cap if cap[0].isalpha() else f"cap{cap}"
    return base if lang == "en" else f"{base}!{lang}"


def _web(chapter: dict, cap: str, lang: str) -> str:
    v = (chapter.get("Version") or [{}])[0]
    if v.get("Web"):
        return v["Web"]
    suffix = {"en": "en", "zh-Hant": "zh-Hant-HK", "zh-Hans": "zh-Hans-CN"}[lang]
    return f"{HKEL}/hk/{_make_id(cap, 'en')}!{suffix}"


async def _chapter(law_id: str) -> tuple[str, str, dict]:
    cap, lang = _parse_id(law_id)
    c = (await _index(lang)).get(cap)
    if not c:
        raise NotFound(f"no current Hong Kong legislation {law_id!r} in HKeL open data "
                       '(ids look like "cap622", "cap4A", "A101").')
    return cap, lang, c


async def _load(law_id: str):
    cap, lang, c = await _chapter(law_id)
    key = _make_id(cap, lang)
    if key in _doc_cache:
        return _doc_cache[key]
    v = (c.get("Version") or [{}])[0]
    url = v.get("DataResourceUrl")
    if not url:
        raise SourceError(f"HKeL open data: no data file listed for {key}")
    _size, entries = await _central_directory(url)
    pat = re.compile(rf"^(?:cap_)?{re.escape(cap)}_[0-9-]{{14}}_{re.escape(lang)}_c\.xml$", re.I)
    names = sorted(n for n in entries if pat.match(n))
    if not names:
        raise NotFound(f"{key} is listed by HKeL but its text is not in {url.rsplit('/', 1)[-1]}")
    name = names[-1]   # newest version date if several
    try:
        xml = await _zip_member(url, name, entries[name])
    except SourceError:
        _size, entries = await _central_directory(url)   # one retry after directory refresh
        xml = await _zip_member(url, name, entries[name])
    root = etree.fromstring(xml, etree.XMLParser(huge_tree=True, resolve_entities=False,
                                                 no_network=True))
    title = clean(c.get(_TITLE_KEY[lang]) or c.get("ChapterTitleEnglish")) or key
    meta = {
        "id": key, "cap": cap, "lang": lang, "title": f"{c.get('CapNoDisplay', key)} {title}".strip(),
        "url": _web(c, cap, lang),
        "as_of": _first(root, "date") or (v.get("VersionDate", {}).get("value") or "")[:10],
        "status": _STATUS.get(v.get("VersionDate", {}).get("statusCategory", ""), ""),
        "type": _TYPES.get(c.get("LegislationType", ""), c.get("LegislationType", "")),
    }
    return lru_put(_doc_cache, key, (meta, root), 6)


def _first(root, local: str) -> str:
    els = root.xpath(f".//*[local-name()='{local}']")
    return text(els[0]) if els else ""


# =========================================================================== #
# XML -> markdown
# =========================================================================== #
_PROV = {"section", "schedule", "annex", "appendix", "rule", "regulation", "article"}
_LEVELS = {"part": 2, "division": 3, "subdivision": 4}          # pure headings
_HASHES = {"schedule": 2, "annex": 2, "appendix": 2}            # other provisions: 4
_NOTES = {"sourceNote", "editorialNote", "referenceNote", "statutoryNote", "note"}
_BLOCK = {"subsection", "paragraph", "subparagraph", "clause", "subclause", "def", "leadIn",
          "continued", "content", "proviso", "p", "tr", "level", "item", "quotedStructure",
          "longTitle", "commencementNote", "table", "text", "center", "enactingFormula",
          "preamble", "docTitle", "heading"}
_LONE_NUM = re.compile(r"\s*\(?[\w.]{1,8}\)?\.?\s*")


def _head_line(el) -> str:
    num, head = text(el.find("{*}num")), text(el.find("{*}heading"))
    if num and head:
        return f"{num} {head}" if num.endswith(".") else f"{num} — {head}"
    return num or head


class _Md:
    """Collects markdown paragraphs; inline text accumulates in buf until a block ends."""

    def __init__(self):
        self.out: list[str] = []
        self.buf = ""

    def flush(self):
        t = re.sub(r"[ \t]+", " ", self.buf.replace("\xa0", " ")).strip()
        t = re.sub(r" *\n *", "  \n", t)
        if t and not re.fullmatch(r"[*\s]*", t):
            self.out.append(t)
        self.buf = ""

    def add(self, s: str):
        if s:
            self.buf += re.sub(r"\s+", " ", s)

    def para(self, s: str):
        self.flush()
        if s:
            self.out.append(s)


def _walk(el, md: _Md, top: bool = False):
    tag = localname(el)
    tail = "" if top else (el.tail or "")
    if tag is None:                        # comment / processing instruction
        md.add(tail)
        return
    if tag in _LEVELS or tag in _PROV:
        h = _head_line(el)
        md.para(f"{'#' * (_LEVELS.get(tag) or _HASHES.get(tag) or 4)} {h}" if h else "")
        for ch in el:
            if localname(ch) not in ("num", "heading"):
                _walk(ch, md)
        md.flush()
        md.add(tail)
        return
    if tag == "crossHeading":
        t = text(el)
        md.para(f"**{t}**" if t else "")
        md.add(tail)
        return
    if tag in _NOTES:
        t = text(el)
        md.para(f"*{t}*" if t else "")
        md.add(tail)
        return
    if tag in ("b", "strong"):
        t = text(el)
        if t:
            md.add(" " if (el.text or "")[:1].isspace() else "")
            md.add(f"**{t}**")
        md.add(tail)
        return
    if tag == "br":
        md.buf += "\n"
        md.add(tail)
        return
    if tag in _BLOCK and not _LONE_NUM.fullmatch(md.buf or "x"):
        md.flush()                         # a lone "(1)" / "(a)" stays as the block's prefix
    md.add(el.text or "")
    for ch in el:
        _walk(ch, md)
    if tag in ("num", "td", "th"):
        md.add(" ")
    if tag in _BLOCK:
        md.flush()
    md.add(tail)


def _render(el) -> str:
    md = _Md()
    _walk(el, md, top=True)
    md.flush()
    return "\n\n".join(md.out)


def _main(root):
    m = root.find("{*}main")
    return m if m is not None else root


# --------------------------------------------------------------------------- #
# Provisions. Structured texts: the label is HKeL's temporalId, unique per text
# ("s2", "sch1", "sch2_P1_s1" for s. 1 in Part 1 of Sch. 2, "s1_s1" for O. 1 r. 1
# of the Rules of the High Court). Unstructured instruments: "art24", split from
# the rendered text on the bold article lines.
# --------------------------------------------------------------------------- #
_ART_LINE = re.compile(r"^\*\*\s*(?:Article\s+(\d+)|第([〇零一二三四五六七八九十百千\d]+)條)\s*\*\*$")
_CN = {"〇": 0, "零": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
_CN_NUM = "〇零一二三四五六七八九十百千"


def _cn_int(s: str) -> int:
    """'二十四' -> 24, '一百五十八' -> 158, '24' -> 24."""
    if s.isdigit():
        return int(s)
    total, cur = 0, 0
    for ch in s:
        if ch in _CN:
            cur = _CN[ch]
        else:
            total += (cur or 1) * {"十": 10, "百": 100, "千": 1000}[ch]
            cur = 0
    return total + cur


def _provisions(root) -> dict:
    """temporalId -> element, document order."""
    out = {}
    for e in _main(root).iter():
        if localname(e) in _PROV:
            label = e.get("temporalId") or e.get("name")
            if label and label not in out:
                out[label] = e
    return out


def _articles(root) -> list[tuple[str, str, str]]:
    """(label, heading, markdown) per article of an unstructured instrument."""
    out, cur = [], None
    for p in _render(_main(root)).split("\n\n"):
        m = _ART_LINE.match(p.strip())
        if m:
            head = p.strip("* ")
            cur = (f"art{m[1] or _cn_int(m[2])}", head, [f"#### {head}"])
            out.append(cur)
        elif cur and re.match(r"^(#|\*\*.*(Chapter|Section \d|Annex|第.+[章節]|附件))", p):
            cur = None                     # a chapter heading ends the article
        elif cur:
            cur[2].append(p)
    return [(lab, head, "\n\n".join(body)) for lab, head, body in out]


def _candidates(prov: str) -> list[str]:
    """User label -> candidate labels: 's.2', 'section 2', '2' -> s2; 'Sch. 1', '附表1' -> sch1;
    'Article 24', '第二十四條' -> art24; 'sch1/s1' -> sch1_s1."""
    p = clean(prov)
    m = re.fullmatch(rf"第\s*([{_CN_NUM}]+|\d+[A-Z]*)\s*條", p, re.I)
    if m:
        n = str(_cn_int(m[1])) if m[1][0] in _CN_NUM else m[1].upper()
        return [f"art{n}", f"s{n}"]
    m = re.fullmatch(r"(附表|附件)\s*(\w+)", p)
    if m:
        n = str(_cn_int(m[2])) if m[2][0] in _CN_NUM else m[2]
        return [f"sch{n}"] if m[1] == "附表" else [f"ann{n}", f"sch{n}"]
    key = re.sub(r"[\s.]", "", p).replace("/", "_")
    m = re.fullmatch(r"(section|sec|s|rule|r|regulation|reg|article|art|schedule|sch|annex|ann|"
                     r"appendix|app)?(\d+[a-z]{0,3})", key, re.I)
    if not m:
        return [key]
    kind, n = (m[1] or "").lower(), re.sub(r"[a-z]+$", lambda x: x[0].upper(), m[2])
    return {"schedule": [f"sch{n}"], "sch": [f"sch{n}"], "annex": [f"ann{n}"], "ann": [f"ann{n}"],
            "appendix": [f"app{n}"], "app": [f"app{n}"], "article": [f"art{n}", f"s{n}"],
            "art": [f"art{n}", f"s{n}"]}.get(kind, [f"s{n}", f"art{n}"])


def _lookup(provs: dict, prov: str):
    lower = {k.lower(): k for k in provs}
    # the same label with Part/Division segments dropped ("sch2_P1_s1" -> "sch2_s1"), if unique
    short: dict[str, list[str]] = {}
    for k in provs:
        short.setdefault(re.sub(r"_(?:P|D|SD)\w*?(?=_)", "", k).lower(), []).append(k)
    for c in _candidates(prov):
        c = c.lower()
        if c in lower:
            return lower[c]
        if len(short.get(c, ())) == 1:
            return short[c][0]
    return None


class HongKong(Jurisdiction):
    code = "hk"
    name = "Hong Kong"
    languages = ("en", "zh-Hant")
    aliases = ("hong kong", "hongkong", "hksar", "香港")
    sources = (
        Source(
            name="Hong Kong e-Legislation (Department of Justice) open data on DATA.GOV.HK",
            url="https://data.gov.hk/en-data/dataset/hk-doj-hkel-legislation-current",
            covers=("legislation",),
            licence="DATA.GOV.HK Terms and Conditions of Use v1.2 (free reuse incl. commercial, "
                    "with source acknowledgement and attribution to the HKSAR Government, DoJ "
                    "and DATA.GOV.HK)",
            commercial_use=True,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~12 requests (2026-11)",
            terms_url="https://data.gov.hk/en/terms-and-conditions",
            warning="Attribution required: identify the source (Hong Kong e-Legislation, "
                    "Department of Justice, via DATA.GOV.HK) and acknowledge the HKSAR "
                    "Government's ownership of the data. Texts are the open-data XML, not the "
                    "verified copies with legal status on www.elegislation.gov.hk.",
        ),
    )
    legislation_filters = {
        "lang": "en (default; Chinese queries default to zh-Hant) | zh-Hant | zh-Hans",
        "type": "comma-separated: O (ordinance), S (subsidiary legislation), I (instrument)",
        "status": "in_effect (default) | all | repealed | not_yet",
    }
    min_interval = {"resource.data.one.gov.hk": 1.0}
    notes = ("Legislation only (current versions, English and Chinese) from DoJ HKeL open data. "
             "No case law: the Judiciary's Legal Reference System and HKLII both forbid "
             "automated access in robots.txt.")
    gaps = (
        "Case law (Judiciary Legal Reference System, legalref.judiciary.hk): robots.txt disallows (`Disallow: /`)",
        "HKLII case law (non-official): robots.txt disallows its /api data route",
        "Verified copies with legal status and past versions (www.elegislation.gov.hk): robots.txt disallows; open data is current only",
    )
    samples = {
        "legislation_query": "companies ordinance",
        "law_id": "cap622",
        "provision": "s2",
    }

    async def search_legislation(self, query, *, limit, page, filters):
        q = clean(query)
        if not q:
            raise BadRequest("empty query. Search by title words or chapter number, "
                             'e.g. "companies", "Cap. 622", "基本法".')
        cjk = bool(re.search(r"[㐀-鿿]", q))
        lang = filters.get("lang") or ("zh-Hant" if cjk else "en")
        lang = {"zh": "zh-Hant", "zh-hant": "zh-Hant", "tc": "zh-Hant", "zh-hans": "zh-Hans",
                "sc": "zh-Hans", "en": "en"}.get(lang.lower(), "")
        if not lang:
            raise BadRequest('invalid lang. Use "en", "zh-Hant" or "zh-Hans".')
        types = {t.strip().upper() for t in (filters.get("type") or "").split(",") if t.strip()}
        if types - set(_TYPES):
            raise BadRequest('invalid type. Use O, S, I or a comma list, e.g. "O,S".')
        status = (filters.get("status") or "in_effect").lower()
        wanted = {"in_effect": {"InEffect"}, "repealed": {"NoLongerInEffect"},
                  "not_yet": {"NotYetInEffect"}, "all": set(_STATUS)}.get(status)
        if wanted is None:
            raise BadRequest('invalid status. Use in_effect, all, repealed or not_yet.')

        idx = await _index(lang)
        tkey = _TITLE_KEY[lang]
        try:
            cap_q, _ = _parse_id(q)
        except BadRequest:
            cap_q = ""
        words = [w for w in re.split(r"\s+", q.casefold()) if w] if not cjk else [q.replace(" ", "")]
        scored = []
        for cap, c in idx.items():
            v = (c.get("Version") or [{}])[0].get("VersionDate", {})
            if v.get("statusCategory") not in wanted or (types and c.get("LegislationType") not in types):
                continue
            title = clean(c.get(tkey) or c.get("ChapterTitleEnglish"))
            tl = title.casefold()
            if cap == cap_q:
                score = 0
            elif all(w in tl for w in words):
                score = 1 if tl.strip("《》 ").startswith(q.casefold().strip("《》 ")) else 2
            else:
                continue
            bare = re.sub(r"[(（][^)）]*[)）]", "", title)
            scored.append((score, c.get("LegislationType") != "O", len(bare), cap, c, title))
        scored.sort(key=lambda x: x[:4])
        start = (page - 1) * limit
        items = []
        for *_x, cap, c, title in scored[start:start + limit]:
            v = (c.get("Version") or [{}])[0]
            vd = v.get("VersionDate", {})
            items.append(LawHit(
                id=_make_id(cap, lang), title=f"{c.get('CapNoDisplay', cap)} {title}".strip(),
                type=_TYPES.get(c.get("LegislationType", ""), ""), number=c.get("CapNoDisplay", ""),
                date=(vd.get("value") or "")[:10],
                status=_STATUS.get(vd.get("statusCategory", ""), ""), url=_web(c, cap, lang)))
        note = ("Title / chapter-number search over the current HKeL index (no full-text search); "
                "date = current version date.")
        return Results(items=items, total=len(scored), note=note)

    async def get_legislation_toc(self, id):
        meta, root = await _load(id)
        provs = _provisions(root)
        # Instruments without <section>s (Basic Law, ...): articles from the text first.
        entries = [] if any(localname(e) == "section" for e in provs.values()) else \
            [TocEntry(title=head, level=0, provision=lab) for lab, head, _ in _articles(root)]
        label_of = {e: k for k, e in provs.items()}
        for e in _main(root).iter():
            tag = localname(e)
            if tag not in _LEVELS and e not in label_of:
                continue
            depth = sum(1 for a in e.iterancestors()
                        if localname(a) in _LEVELS or localname(a) in _PROV)
            head = _head_line(e) or e.get("name") or tag
            if e.get("status") == "repealed" and "repeal" not in head.lower():
                head += " (repealed)"
            entries.append(TocEntry(title=head, level=depth, provision=label_of.get(e, "")))
        if not entries:
            raise SourceError(f"HKeL open data: no sections found in {meta['id']}")
        return Toc(id=meta["id"], title=meta["title"], url=meta["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        meta, root = await _load(id)
        provs = _provisions(root)
        label = _lookup(provs, provision)
        if label:
            body = _render(provs[label])
        elif not any(localname(e) == "section" for e in provs.values()):
            arts = {lab: md for lab, _h, md in _articles(root)}
            label = _lookup(arts, provision)
            body = arts.get(label, "")
        if not label:
            raise NotFound(f"{meta['id']} has no provision {provision!r}. Use a label from "
                           'get_legislation_toc, e.g. "s2" (also "s.2", "section 2", "2"), '
                           '"sch1", "sch2_P1_s1", "art24".')
        return Provision(law_id=meta["id"], law_title=meta["title"], provision=label,
                         text=body, url=meta["url"], as_of=meta["as_of"])

    async def get_legislation_text(self, id):
        meta, root = await _load(id)
        return LawText(id=meta["id"], title=meta["title"], text=_render(_main(root)),
                       url=meta["url"], as_of=meta["as_of"],
                       metadata={"Type": meta["type"], "Status": meta["status"],
                                 "Language": meta["lang"],
                                 "Source file": "DoJ HKeL open data (DATA.GOV.HK), current version"})
