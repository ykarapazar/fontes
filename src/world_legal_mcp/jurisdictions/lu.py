"""Luxembourg: national legislation from Legilux (Ministère d'État, Service central de
législation): metadata from the JOLux SPARQL endpoint, texts as Akoma Ntoso XML.

Gotchas this code encodes (verified 2026-11-05):
  * Same JOLux ontology as Swiss Fedlex, different modelling. There is no
    ConsolidationAbstract: each consolidated version is a jolux:Consolidation Work whose
    URI is the series ELI plus a date, ".../eli/etat/leg/code/civil/20251226" (codes) or
    ".../eli/etat/leg/loi/2018/08/01/a686/consolide/20251226" (laws). The original act
    published in the Mémorial is ".../loi/2018/08/01/a686/jo". Our law id is the series
    ELI without host and suffix: "eli/etat/leg/code/civil", "eli/etat/leg/loi/2018/08/01/a686".
  * Only ~1,400 acts and codes are consolidated. For any other act we serve the original
    Mémorial text (/jo), which is not updated for later amendments; LawText/Provision say so.
  * Virtuoso quirks: GROUP BY + ORDER BY on aggregates over a UNION fails ("VECSL internal
    error") unless wrapped in a subquery, and a SUBSTR-built key does not group with a
    REPLACE-built one, so both branches build the id with REPLACE.
  * data.legilux.public.lu/robots.txt disallows /eli/* and /filestore/* (checked
    2026-11-05). The public site legilux.public.lu serves the same /filestore/ files and
    its robots.txt allows /filestore and /eli/etat/leg/ (bar a few named items), so texts
    are read from there, one file per user request. The SPARQL endpoint path is allowed.
  * Akoma Ntoso (CSD13) with an scl: namespace for JOLux metadata and index terms (skip it).
    Repealed text is wrapped in <del> (rendered ~~struck~~); ordered lists carry their
    printed numbering in scl:symbol ("1°", "(a)").
  * Licence: CC BY 4.0, stated on every file (jolux:license) and on data.public.lu.

Case law (Cour de cassation, added 2026-11): data.public.lu dataset "cour-de-cassation-1"
(Administration judiciaire, CC BY-ND, updated weekly). It is one ZIP per year (1971-2026,
~0.2-36 MB each, ~560 MB in all) holding one PDF per published decision, named
"YYYYMMDD_<case no>[_n]_pseudonymisé-accessible.pdf". We never download a ZIP: the host
(S3 behind CloudFront, robots.txt "Allow: /") honours HTTP Range, so we read the ZIP's
central directory (~12-16 kB) to list a year, and one PDF member (~50-330 kB) per decision.
The listing gives date + case number only, so there is no full-text search across the
archive: a text query is only run over a narrow candidate set (<= _SCAN_MAX PDFs). The
ZIP year is the upload year, not always the decision year (the 2022 ZIP holds a 2019
file); ids are "<zip year>/<file stem>". Decisions before ~2000 are scans with a noisy OCR
text layer; the text is reproduced as the source gives it (CC BY-ND: no alteration).
"""
from __future__ import annotations

import asyncio
import html
import re
import struct
import time
import unicodedata
import zlib

from lxml import etree

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc, TocEntry

SPARQL = "https://data.legilux.public.lu/sparqlendpoint"
DATA = "http://data.legilux.public.lu/"
SITE = "https://legilux.public.lu/"
XSD_DATE = "<http://www.w3.org/2001/XMLSchema#date>"
XML_FMT = "<http://data.legilux.public.lu/resource/authority/user-format/xml>"
SCL_NS = "http://www.scl.lu"
_PREFIX = "PREFIX jolux: <http://data.legilux.public.lu/resource/ontology/jolux#>\n"

_ID_RE = re.compile(r"^(?:https?://(?:data\.)?legilux\.public\.lu/)?/?(?:eli/)?(etat/leg/[\w/.-]+?)"
                    r"(?:/consolide/\d{8}|/(?:\d{8}))?(?:/jo)?(?:/fr(?:/\w+)?)?/?$")
_HIER = {"book", "part", "title", "subtitle", "chapter", "subchapter", "section", "subsection",
         "division", "subdivision", "tome", "hcontainer"}
_BLOCK = {"alinea", "content", "intro", "wrapUp", "list", "blockList", "container",
          "subparagraph", "blockContainer"}
_INLINE_KEEP = {"b", "i", "u", "sup", "sub", "del", "ins"}
_ROMAN = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "xi", "xii", "xiii",
          "xiv", "xv", "xvi", "xvii", "xviii", "xix", "xx"]
_NOTE = ("Original text as published in the Mémorial (no consolidated version on Legilux): "
         "later amendments are not applied.")

_law_cache: dict[str, dict] = {}

DATASET_API = "https://data.public.lu/api/1/datasets/cour-de-cassation-1/"
DATASET_PAGE = "https://data.public.lu/fr/datasets/cour-de-cassation-1/"
_SCAN_MAX = 40            # PDFs a text query may open (about 8 MB), never more
_MAX_YEARS = 5            # ZIP listings one search may read
_res_cache: dict[str, tuple] = {}      # "res" -> (fetched at, {year: (url, size)})
_list_cache: dict[int, list] = {}      # year -> entries
_dec_cache: dict[str, Decision] = {}
_FILE_RE = re.compile(r"^(\d{4})(\d{2})(\d{2})_(.+)$")


# --------------------------------------------------------------------------- #
# SPARQL
# --------------------------------------------------------------------------- #
def _lit(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


# Virtuoso rejects sort rows over ~11 kB ("SR319"); some act titles are longer than that.
_TMAX = 1000


async def _sparql(query: str) -> list[dict]:
    r = await _http.get(SPARQL, params={"query": _PREFIX + query},
                        headers={"Accept": "application/sparql-results+json"})
    if r.status_code != 200:
        raise SourceError(f"Legilux SPARQL returned HTTP {r.status_code}", r.status_code)
    try:
        rows = r.json()["results"]["bindings"]
    except (ValueError, KeyError, TypeError):
        raise SourceError("Legilux SPARQL returned an unexpected payload", r.status_code)
    return [{k: v["value"] for k, v in row.items()} for row in rows]


def _short(uri: str) -> str:
    """http://data.legilux.public.lu/eli/etat/leg/... -> eli/etat/leg/..."""
    return uri.replace(DATA, "")


def _status(uri: str) -> str:
    return (uri or "").rsplit("/", 1)[-1].replace("-", " ")


def _clean_title(t: str) -> str:
    t = (t or "").replace("\\n", " ")   # some titles hold a literal backslash-n
    return _http.clean(re.sub(r"^Version (?:consolidée|rectifiée)[^:]*:\s*", "", t))


def _law_id(raw: str) -> str:
    m = _ID_RE.match((raw or "").strip())
    if not m:
        raise BadRequest(f"law id {raw!r} is not a Legilux ELI. Use the id from "
                         "search_legislation, e.g. eli/etat/leg/code/civil or "
                         "eli/etat/leg/loi/2018/08/01/a686.")
    return "eli/" + m.group(1)


async def _resolve(law_id: str) -> dict:
    """Series ELI -> latest consolidated version (or the original /jo act) + its XML file."""
    lid = _law_id(law_id)
    if lid in _law_cache:
        return _law_cache[lid]
    base = DATA + lid
    rows = await _sparql(f"""
SELECT ?w ?kind ?d ?t ?file ?st WHERE {{
 {{ ?w a jolux:Consolidation ; jolux:dateApplicability ?d .
    FILTER(STRSTARTS(STR(?w), {_lit(base + "/")}))
    FILTER(?d <= "{_http.today()}"^^{XSD_DATE}) BIND("cons" AS ?kind) }}
 UNION
 {{ BIND(<{base}/jo> AS ?w) ?w a jolux:Act . OPTIONAL {{ ?w jolux:dateDocument ?d }}
    OPTIONAL {{ ?w jolux:inForceStatus ?st }} BIND("jo" AS ?kind) }}
 ?w jolux:isRealizedBy ?e . ?e jolux:title ?t ; jolux:isEmbodiedBy ?m .
 ?m jolux:userFormat {XML_FMT} ; jolux:isExemplifiedBy ?file .
}} ORDER BY DESC(?kind = "cons") DESC(?d) LIMIT 20""")
    cons = [r for r in rows if r["kind"] == "cons"
            and re.fullmatch(re.escape(base) + r"(?:/consolide)?/\d{8}", r["w"])]
    act = next((r for r in rows if r["kind"] == "jo"), None)
    row = cons[0] if cons else act
    if row is None:
        raise NotFound(f"no text on Legilux for {lid!r}. Check the id with search_legislation.")
    return _http.lru_put(_law_cache, lid, {
        "id": lid, "consolidated": bool(cons), "work": row["w"],
        "title": _clean_title((act or row)["t"]), "date": (row.get("d") or "")[:10],
        "status": _status(act.get("st", "")) if act else "", "file": row["file"],
        "parsed": None}, 8)


# --------------------------------------------------------------------------- #
# Akoma Ntoso -> markdown
# --------------------------------------------------------------------------- #
def _ln(el) -> str:
    return _http.localname(el) or ""


def _is_scl(el) -> bool:
    return isinstance(el.tag, str) and etree.QName(el).namespace == SCL_NS


def _plain(el) -> str:
    """Text without inserted spaces ('1<sup>er</sup>' -> '1er'), scl: parts left out."""
    if el is None:
        return ""
    parts = [el.text or ""]
    for c in el:
        if not _is_scl(c):
            parts.append(_plain(c))
        parts.append(c.tail or "")
    return _http.clean("".join(parts))


def _li_label(symbol: str, n: int) -> str:
    """scl:symbol of the first item ('1°', '(a)', 'i)') -> the label of item n (1-based)."""
    if not symbol:
        return ""
    m = re.search(r"\d+", symbol)
    if m:
        return symbol[:m.start()] + str(int(m.group()) + n - 1) + symbol[m.end():]
    m = re.search(r"\b(i)\b", symbol)
    if m and n <= len(_ROMAN):
        return symbol[:m.start()] + _ROMAN[n - 1] + symbol[m.end():]
    m = re.search(r"[a-zA-Z]", symbol)
    if m and n <= 26:
        return symbol[:m.start()] + chr(ord(m.group()) + n - 1) + symbol[m.end():]
    return symbol


def _numbered(el, inner: str) -> str:
    """Put an element's <num> in front of its first paragraph."""
    num = el.find("{*}num")
    label = html.escape(_plain(num)) if num is not None else ""
    if not label:
        return inner
    if "<p>" in inner:
        return inner.replace("<p>", f"<p>{label} ", 1)
    return f"<p>{label}</p>{inner}"


def _h(el) -> str:
    """Akoma Ntoso subtree -> HTML that _http.html_to_md understands."""
    out = [html.escape(el.text or "")]
    for c in el:
        if isinstance(c.tag, str) and not _is_scl(c):
            out.append(_node(c))
        out.append(html.escape(c.tail or ""))
    return "".join(out)


def _node(el) -> str:
    n = _ln(el)
    if n in ("num", "heading", "mod", "eventRef", "meta", "authorialNote"):
        return ""
    if n == "p":
        return f"<p>{_h(el)}</p>"
    if n in _INLINE_KEEP:
        return f"<{n}>{_h(el)}</{n}>"
    if n == "br":
        return "<br/>"
    if n == "embeddedText":
        return f"« {_h(el).strip()} »"
    if n in ("ol", "ul"):
        sym = next((v for k, v in el.attrib.items() if k.endswith("symbol")), "")
        items = [c for c in el if _ln(c) == "li"]
        lis = "".join(f"<li>{html.escape(_li_label(sym, i)) + ' ' if n == 'ol' and sym else ''}"
                      f"{_h(li)}</li>" for i, li in enumerate(items, 1))
        return f"<ul>{lis}</ul>"
    if n in ("table", "tr", "td", "th", "tbody", "thead", "caption"):
        span = "".join(f' {a}="{html.escape(el.get(a))}"' for a in ("colspan", "rowspan") if el.get(a))
        return f"<{n}{span}>{_h(el)}</{n}>"
    if n in ("paragraph", "point", "item"):
        return f"<div>{_numbered(el, _h(el).strip())}</div>"
    if n in ("embeddedStructure", "quotedStructure"):
        return f"<blockquote>{_h(el)}</blockquote>"
    if n in _HIER or n == "article":   # nested inside quoted text
        head = _http.clean(f"{_plain(el.find('{*}num'))} {_plain(el.find('{*}heading'))}")
        return (f"<p><b>{html.escape(head)}</b></p>" if head else "") + f"<div>{_h(el)}</div>"
    if n in _BLOCK:
        return f"<div>{_h(el)}</div>"
    return _h(el)


def _md(el) -> str:
    return _http.html_to_md(_h(el))


def _norm_label(s: str) -> str:
    s = (s or "").replace("\xa0", " ").lower()
    s = re.sub(r"^\s*(?:article|art\.?)\s*", "", s)
    s = re.sub(r"(\d)\s*(?:er|re|ère)\b", r"\1", s)
    s = re.sub(r"^([a-z])\s*\.?\s*(?=\d)", r"\1", s)   # code prefix: 'L. 121-1' = 'L121-1'
    s = re.sub(r"\s*\.\s*", ".", s).strip(" .")   # keep interior dots: '9.1' != '91'
    return re.sub(r"\s+(?=[a-z])", "", re.sub(r"\s+", " ", s))   # '5 bis' = '5bis'; '1 1' != '11'


def _parse_law(xml: bytes) -> dict:
    """-> {"toc": [TocEntry], "arts": {norm: (label, md)}, "text": md}."""
    try:
        root = etree.fromstring(xml)
    except etree.XMLSyntaxError as e:
        raise SourceError(f"Legilux XML did not parse: {e}")
    body = root.find(".//{*}body")
    if body is None:
        raise SourceError("Legilux XML has no <body>")
    toc, arts, parts = [], {}, []

    def walk(parent, depth):
        for el in parent:
            if not isinstance(el.tag, str) or _is_scl(el):
                continue
            n = _ln(el)
            if n in ("num", "heading", "index"):
                continue
            if n in _HIER:
                head = " – ".join(x for x in (_plain(el.find("{*}num")).rstrip("."),
                                              _plain(el.find("{*}heading"))) if x)
                if head:
                    toc.append(TocEntry(title=head, level=depth))
                    parts.append("#" * min(depth + 1, 5) + " " + head)
                walk(el, depth + 1)
            elif n == "article":
                label = _plain(el.find("{*}num")).rstrip(". ") or el.get("id", "")
                heading = _plain(el.find("{*}heading"))
                key = _norm_label(label)
                if key in arts:
                    label = f"{label} ({el.get('id', len(arts))})"
                    key = _norm_label(label)
                repealed = el.get("style") == "del"
                head = f"{label} – {heading}" if heading else label
                md = "#" * min(depth + 1, 6) + f" {head}\n\n{_md(el)}".rstrip()
                arts[key] = (label, md)
                toc.append(TocEntry(title=head + (" (abrogé)" if repealed else ""),
                                    level=depth, provision=label))
                parts.append(md)
            else:
                md = _md(el)
                if md:
                    parts.append(md)

    walk(body, 0)
    return {"toc": toc, "arts": arts, "text": "\n\n".join(parts)}


async def _law(law_id: str) -> tuple[dict, dict]:
    info = await _resolve(law_id)
    if info["parsed"] is None:
        url = info["file"].replace(DATA + "filestore/", SITE + "filestore/")
        r = await _http.get(url)
        if r.status_code != 200 or b"akomaNtoso" not in r.content[:2000]:
            raise SourceError(f"Legilux text fetch failed for {info['id']}", r.status_code)
        info["parsed"] = _parse_law(r.content)
    return info, info["parsed"]


def _page_url(info: dict) -> str:
    return SITE + _short(info["work"]) + "/fr"


# --------------------------------------------------------------------------- #
# Cour de cassation: yearly ZIPs read by HTTP Range (no whole-archive download)
# --------------------------------------------------------------------------- #
async def _resources() -> dict[int, tuple[str, int]]:
    hit = _res_cache.get("res")
    if hit and time.monotonic() - hit[0] < 1800:   # ZIP URLs change when a year is rewritten
        return hit[1]
    r = await _http.get(DATASET_API)
    if r.status_code != 200:
        raise SourceError(f"data.public.lu returned HTTP {r.status_code}", r.status_code)
    try:
        res = {int(x["title"][:4]): (x["url"], int(x["filesize"]))
               for x in r.json()["resources"] if re.fullmatch(r"\d{4}\.zip", x["title"])}
    except (ValueError, KeyError, TypeError):
        raise SourceError("data.public.lu returned an unexpected dataset payload", r.status_code)
    if not res:
        raise SourceError("data.public.lu dataset lists no yearly ZIPs")
    _res_cache["res"] = (time.monotonic(), res)
    return res


async def _range(url: str, start: int, end: int) -> bytes:
    r = await _http.get(url, headers={"Range": f"bytes={start}-{end}", "Accept-Encoding": "identity"})
    if r.status_code != 206:
        raise SourceError(f"download.data.public.lu ignored the byte range (HTTP {r.status_code}); "
                          "not downloading the whole ZIP", r.status_code)
    return r.content


async def _entries(year: int) -> tuple[str, list[dict]]:
    """Central directory of one year's ZIP -> [{name, stem, meth, cs, off}] (2 small requests)."""
    res = await _resources()
    if year not in res:
        raise NotFound(f"no Cour de cassation ZIP for {year}. Years: {min(res)}-{max(res)} "
                       "(not every year exists).")
    url, size = res[year]
    if year in _list_cache and _list_cache[year][0] == url:
        return url, _list_cache[year][1]
    tail = await _range(url, max(0, size - 4096), size - 1)
    i = tail.rfind(b"PK\x05\x06")
    if i < 0:
        raise SourceError(f"{year}.zip has no end-of-directory record")
    count, cd_size, cd_off = struct.unpack("<HII", tail[i + 10:i + 20])
    if cd_off == 0xFFFFFFFF or count == 0xFFFF:
        raise SourceError(f"{year}.zip uses ZIP64, which this reader does not handle")
    cd = await _range(url, cd_off, cd_off + cd_size - 1)
    out, p = [], 0
    while cd[p:p + 4] == b"PK\x01\x02":
        flag, meth = struct.unpack("<HH", cd[p + 8:p + 12])
        cs = struct.unpack("<I", cd[p + 20:p + 24])[0]
        nl, el, cl = struct.unpack("<HHH", cd[p + 28:p + 34])
        off = struct.unpack("<I", cd[p + 42:p + 46])[0]
        raw = cd[p + 46:p + 46 + nl]
        name = unicodedata.normalize("NFC", raw.decode("utf-8" if flag & 0x800 else "cp437"))
        p += 46 + nl + el + cl
        if name.lower().endswith(".pdf"):
            stem = re.sub(r"-accessible$", "", name[:-4])
            out.append({"name": name, "stem": stem, "meth": meth, "cs": cs, "off": off,
                        "nl": nl, **_meta(stem)})
    out.sort(key=lambda e: (e["date"], e["stem"]), reverse=True)
    _http.lru_put(_list_cache, year, (url, out), 12)
    return url, out


def _meta(stem: str) -> dict:
    """File stem -> date, case number (the source gives nothing else in the listing)."""
    m = _FILE_RE.match(stem)
    if not m:
        return {"date": "", "case": stem}
    y, mo, d, rest = m.groups()
    date = f"{y}-{mo}-{d}" if 1 <= int(mo) <= 12 and 1 <= int(d) <= 31 else ""
    rest = re.sub(r"_pseudonymis.*$", "", rest)
    c = re.match(r"(CAS-\d{4}-\d{5})", rest)
    return {"date": date, "case": c.group(1) if c else rest.replace("_", " ")}


def _hit(year: int, e: dict, snippet: str = "") -> DecisionHit:
    court = "Cour d'appel (in the Cassation dataset)" if e["case"].startswith("CA8") else "Cour de cassation"
    return DecisionHit(id=f"{year}/{e['stem']}", title=f"{court.split(' (')[0]} {e['case']}",
                       court=court, date=e["date"], case_number=e["case"], snippet=snippet,
                       url=DATASET_PAGE)


async def _pdf_text(year: int, e: dict, url: str) -> str:
    # local header = 30 bytes + name + extra (extra length differs from the directory's)
    b = await _range(url, e["off"], e["off"] + 30 + e["nl"] + 512 + e["cs"] - 1)
    if b[:4] != b"PK\x03\x04":
        raise SourceError(f"{e['name']}: bad ZIP member header")
    nl, el = struct.unpack("<HH", b[26:30])
    data = b[30 + nl + el:30 + nl + el + e["cs"]]
    try:
        pdf = zlib.decompress(data, -15) if e["meth"] == 8 else data
    except zlib.error as ex:
        raise SourceError(f"{e['name']}: could not unzip ({ex})")
    text = await asyncio.to_thread(_http.pdf_text, pdf)
    if not text:
        raise SourceError(f"{e['name']} has no text layer")
    return text


def _years_from(filters: dict, query: str) -> list[int]:
    y = str(filters.get("year") or "").strip()
    if y:
        m = re.fullmatch(r"(\d{4})(?:\s*-\s*(\d{4}))?", y)
        if not m:
            raise BadRequest("year must be 2023 or a range like 2020-2023.")
        a, b = int(m.group(1)), int(m.group(2) or m.group(1))
        if b < a or b - a + 1 > _MAX_YEARS:
            raise BadRequest(f"year range is limited to {_MAX_YEARS} years per search.")
        return list(range(b, a - 1, -1))
    years = []
    for m in re.finditer(r"CAS-(\d{4})-\d{5}", query, re.I):   # filed 2022, usually decided 2022-23
        years += [int(m.group(1)) + 1, int(m.group(1))]
    for m in re.finditer(r"(?<![\d-])((?:19|20)\d{2})(?![\d-]\d{5})", query):
        years.append(int(m.group(1)))
    for m in re.finditer(r"\b\d{2}[./]\d{2}[./]((?:19|20)\d{2})\b", query):
        years.append(int(m.group(1)))
    return list(dict.fromkeys(years))[:_MAX_YEARS]


def _qdate(tok: str) -> str:
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", tok)
    if m:
        return "".join(m.groups())
    m = re.fullmatch(r"(\d{2})[./](\d{2})[./](\d{4})", tok)
    return m.group(3) + m.group(2) + m.group(1) if m else ""


# --------------------------------------------------------------------------- #
# Adapter
# --------------------------------------------------------------------------- #
class Luxembourg(Jurisdiction):
    code = "lu"
    name = "Luxembourg"
    languages = ("fr",)
    aliases = ("lux", "luxembourg", "luxemburg", "lëtzebuerg", "grand-duché de luxembourg")
    sources = (
        Source(
            "Legilux — Journal officiel du Grand-Duché de Luxembourg (Ministère d'État, Service "
            "central de législation): JOLux SPARQL + Akoma Ntoso XML",
            "https://legilux.public.lu/",
            covers=("legislation",),
            licence=("CC BY 4.0 (jolux:license on every file; data.public.lu dataset "
                     "'Legilux - Journal officiel'), © Ministère d'État — Service central de "
                     "législation"),
            commercial_use=True,
            ai_use=True,   # robots.txt has no AI/TDM opt-out; CC BY 4.0 allows any reuse
            auth="none",
            rate_limit=("unknown, nothing documented; 1 s spacing on both hosts, no 429 seen in "
                        "~20 requests (2026-11). data.legilux.public.lu robots.txt disallows "
                        "/eli/* and /filestore/*, so files are read from "
                        "legilux.public.lu/filestore (allowed)"),
            terms_url="https://data.public.lu/fr/datasets/legilux-journal-officiel-du-grand-duche-de-luxembourg-1/",
        ),
        Source(
            "data.public.lu — Cour de cassation decisions (Administration judiciaire), yearly "
            "ZIPs of PDFs read member by member with HTTP Range",
            DATASET_PAGE,
            covers=("caselaw",),
            licence=("CC BY-ND 4.0 (stated on the dataset page): reproduce unaltered, credit "
                     "Administration judiciaire; the official search remains justice.public.lu"),
            commercial_use=True,   # CC BY-ND allows commercial use, but no derivative works
            ai_use=True,           # robots.txt on download.data.public.lu is "Allow: /"; no TDM opt-out found
            auth="none",
            rate_limit=("unknown, nothing documented; 1 s spacing, no 429 seen in ~25 requests "
                        "(2026-11). Range reads only: ~16 kB per year listing, ~50-330 kB per "
                        "decision, never a whole ZIP"),
            terms_url=DATASET_PAGE,
        ),
    )
    min_interval = {"data.legilux.public.lu": 1.0, "legilux.public.lu": 1.0,
                    "data.public.lu": 1.0, "download.data.public.lu": 1.0}
    caselaw_filters = {
        "year": "ZIP year of the dataset, e.g. 2023 or 2020-2023 (max 5 years). Usually the decision year.",
        "date_from": "decision date from, YYYY-MM-DD",
        "date_to": "decision date to, YYYY-MM-DD",
    }
    notes = ("National legislation in French: consolidated codes and laws (~1,400) and the "
             "original Mémorial text of every other act. Law id = Legilux ELI, e.g. "
             "eli/etat/leg/code/civil or eli/etat/leg/loi/2018/08/01/a686. Case law: only the "
             "Cour de cassation, published PDFs 1971-today, listed by year/date/case number "
             "(no full-text search; see gaps).")
    gaps = (
        "Cour de cassation full-text search: the source is yearly ZIPs of PDFs with no index, so "
         "search lists by year/date/case number and opens a text only for <= 40 candidates "
         "(narrow with date_from/date_to); text of pre-2000 decisions is noisy OCR",
        "Other courts (justice.public.lu): bot check (FriendlyCaptcha); administrative courts "
         "(ja.public.lu) answer 403; the Tribunal d'arrondissement ZIPs on data.public.lu are not wired",
        "Consolidated text of acts outside the ~1,400 consolidated ones: not published online "
         "(original Mémorial text served)",
    )
    samples = {
        "legislation_query": "code civil",
        "law_id": "eli/etat/leg/code/civil",
        "provision": "Art. 1er",
        "caselaw_query": "CAS-2022-00031",
        "decision_id": "2023/20230112_CAS-2022-00031_2_pseudonymisé",
    }

    async def search_caselaw(self, query, *, limit, page, filters):
        q = _http.clean(query)
        limit = max(1, min(int(limit), 50))
        page = max(1, int(page))
        df, dt = filters.get("date_from", ""), filters.get("date_to", "")
        for v in (df, dt):
            if v and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
                raise BadRequest("date_from / date_to must be YYYY-MM-DD.")
        years = _years_from(filters, q)
        note = ""
        if not years and (df or dt):
            lo = int((df or dt)[:4])
            hi = int(dt[:4]) if dt else max(max(await _resources()), lo)   # date_from alone = "since"
            if hi - lo + 1 > _MAX_YEARS:
                raise BadRequest(f"date range spans more than {_MAX_YEARS} years; narrow it.")
            years = list(range(hi, lo - 1, -1))
        if not years:
            years = [max(await _resources())]
            note = (f"No year given: only the {years[0]} ZIP was read. Pass year=YYYY (or a case "
                    "number / date in the query) for other years. ")
        words, keys, dates = [], [], []
        for tok in q.split():
            d = _qdate(tok)
            if d:
                dates.append(d)
            elif re.fullmatch(r"(?:19|20)\d{2}", tok):
                continue
            elif re.search(r"\d", tok):
                keys.append(tok.lower())
            else:
                words.append(tok)
        cands, newest = [], ""
        for y in years:
            _, ents = await _entries(y)
            for e in ents:
                st = e["stem"].lower()
                if (df and e["date"] < df) or (dt and e["date"] > dt):
                    continue
                if dates and e["stem"][:8] not in dates:
                    continue
                if any(not re.search(rf"(?<![0-9]){re.escape(k)}(?![0-9])", st) for k in keys):
                    continue
                cands.append((y, e))
        partial = False
        if words:
            if len(cands) > _SCAN_MAX:
                cands.sort(key=lambda c: c[1]["date"], reverse=True)
                cut = cands[_SCAN_MAX - 1][1]["date"]
                n_all, cands = len(cands), cands[:_SCAN_MAX]
                partial = True
                left = -(-(n_all - _SCAN_MAX) // _SCAN_MAX)
                note += (f"Range too wide for a full word search ({n_all} decisions match the "
                         "year/date/number filters; the source has no text index, so each PDF "
                         f"must be opened, one per second; limit {_SCAN_MAX} per search). Only the "
                         f"newest {_SCAN_MAX} (decided {cut} or later) were checked, so the hits "
                         f"below are NOT all matches: results are INCOMPLETE. To cover the whole range, "
                         f"repeat the same search with date_to={cut}, then with the new cut date, "
                         f"about {left} more searches. ")
            def fold_map(t):   # folded text + index of each folded char in t (keeps snippets aligned)
                out, idx = [], []
                for k, ch in enumerate(t):
                    f = unicodedata.normalize("NFD", ch.casefold()).encode("ascii", "ignore").decode()
                    out.append(f)
                    idx.extend([k] * len(f))
                return "".join(out), idx
            fold = lambda t: fold_map(t)[0]
            want = [fold(w) for w in words]
            hits = []
            urls = {y: (await _entries(y))[0] for y in {c[0] for c in cands}}
            texts = []
            for i in range(0, len(cands), 4):   # 4 PDFs at a time
                texts += await asyncio.gather(*(_pdf_text(y, e, urls[y]) for y, e in cands[i:i + 4]))
            for (y, e), text in zip(cands, texts):
                ft, idx = fold_map(text)
                if all(w in ft for w in want):
                    i = max(0, idx[ft.find(want[0])] - 80)
                    hits.append((y, e, _http.clean(text[i:i + 240])))
            total, page_items = len(hits), hits[(page - 1) * limit:page * limit]
            items = [_hit(y, e, sn) for y, e, sn in page_items]
            note += (f"Text searched in {len(cands)} decisions only (the filtered candidates, "
                     "all opened and checked; words must all appear in the text).")
        else:
            total, page_items = len(cands), cands[(page - 1) * limit:page * limit]
            items = [_hit(y, e) for y, e in page_items]
            note += ("Listed from file names only (date, case number): the source has no text "
                     "index. Open a decision with get_decision.")
        return Results(items=items, total=total, note=note.strip(), incomplete=partial)

    async def get_decision(self, id):
        m = re.fullmatch(r"(?:(\d{4})/)?(.+?)(?:\.pdf)?(?:-accessible)?", unicodedata.normalize("NFC", id.strip()))
        if not m or not _FILE_RE.match(m.group(2)):
            raise BadRequest(f"decision id {id!r} should look like "
                             "'2023/20230112_CAS-2022-00031_2_pseudonymisé' (from search_caselaw).")
        stem = m.group(2)
        years = [int(m.group(1))] if m.group(1) else [int(stem[:4]), int(stem[:4]) + 1]
        for y in years:
            try:
                url, ents = await _entries(y)
            except NotFound:
                continue
            e = next((x for x in ents if x["stem"] == stem), None)
            if e:
                break
        else:
            raise NotFound(f"no decision {id!r} in the Cour de cassation ZIPs. Use an id from "
                           "search_caselaw ('<zip year>/<file name without .pdf>').")
        key = f"{y}/{stem}"
        if key not in _dec_cache:
            text = await _pdf_text(y, e, url)
            hit = _hit(y, e)
            _http.lru_put(_dec_cache, key, Decision(
                id=key, title=hit.title, text=text, url=DATASET_PAGE, court=hit.court,
                date=e["date"], case_number=e["case"],
                metadata={"Source file": e["name"], "Dataset": f"cour-de-cassation-1, {y}.zip",
                          "Licence": "CC BY-ND 4.0, Administration judiciaire (unaltered text; "
                                     "names pseudonymised by the source)"}), 8)
        return _dec_cache[key]

    async def search_legislation(self, query, *, limit, page, filters):
        words = [w.lower() for w in _http.clean(query).split()]
        if not words:
            raise BadRequest("give search words from the title, e.g. 'code civil' or "
                             "'protection des données'.")
        limit = max(1, min(int(limit), 50))
        offset = (max(1, int(page)) - 1) * limit
        phrase = " ".join(words)
        # titles containing the exact phrase outrank titles that only contain every word somewhere
        pm = f"BIND(IF(CONTAINS(LCASE(STR(?t)), {_lit(phrase)}), 1, 0) AS ?pm)"
        match = " && ".join(f"CONTAINS(LCASE(STR(?t)), {_lit(w)})" for w in words)
        rows = await _sparql(f"""
SELECT ?id ?c ?p ?tact ?tcons ?date ?type ?status WHERE {{
SELECT ?id (MAX(?cons) AS ?c) (MAX(?pm) AS ?p) (MIN(?ta) AS ?tact) (MIN(?tc) AS ?tcons) (MAX(?dd) AS ?date)
       (MIN(STR(?ty)) AS ?type) (MIN(STR(?st)) AS ?status) WHERE {{
 {{ ?w a jolux:Consolidation ; jolux:isRealizedBy/jolux:title ?t ; jolux:dateApplicability ?d0 ;
       jolux:typeDocument ?ty .
    FILTER(?d0 <= "{_http.today()}"^^{XSD_DATE})
    FILTER({match}) {pm}
    BIND(REPLACE(STR(?w), "(/consolide)?/[0-9]{{8}}$", "") AS ?id) BIND(1 AS ?cons)
    BIND(SUBSTR(STR(?t), 1, {_TMAX}) AS ?tc) }}
 UNION
 {{ ?w a jolux:Act ; jolux:isRealizedBy/jolux:title ?t ; jolux:typeDocument ?ty .
    FILTER({match}) {pm}
    FILTER(STRSTARTS(STR(?w), "{DATA}eli/etat/leg/") && STRENDS(STR(?w), "/jo"))
    OPTIONAL {{ ?w jolux:inForceStatus ?st }} OPTIONAL {{ ?w jolux:dateDocument ?dd }}
    BIND(REPLACE(STR(?w), "/jo$", "") AS ?id) BIND(0 AS ?cons) BIND(SUBSTR(STR(?t), 1, {_TMAX}) AS ?ta) }}
 FILTER(STRSTARTS(?id, "{DATA}eli/etat/leg/") && !CONTAINS(?id, "/recueil/"))
}} GROUP BY ?id }}
ORDER BY DESC(?p) DESC(?c) DESC(?type = "{DATA}resource/authority/resource-type/CODE")
         DESC(COALESCE(?status = "{DATA}resource/authority/application-status/in-force", false))
         DESC(?type = "{DATA}resource/authority/resource-type/LOI")
         STRLEN(COALESCE(?tact, ?tcons)) DESC(?date) ?id
LIMIT {limit} OFFSET {offset}""")
        items = []
        for r in rows:
            lid = _short(r["id"])
            consolidated = r.get("c") == "1"
            t = r.get("tact") or r.get("tcons") or ""
            items.append(LawHit(
                id=lid, title=_clean_title(t) + ("…" if len(t) >= _TMAX else ""),
                type=r.get("type", "").rsplit("/", 1)[-1],
                date=(r.get("date") or "")[:10],
                status=", ".join(x for x in (_status(r.get("status", "")),
                                             "consolidated" if consolidated else
                                             "original text only") if x),
                url=SITE + lid))
        return Results(items=items, total=None,
                       note="French titles. Order: exact-phrase title matches first; then consolidated codes, then consolidated acts in "
                            "force (newest first), then the rest. Law id = Legilux ELI.")

    async def get_legislation_toc(self, id):
        info, law = await _law(id)
        return Toc(id=info["id"], title=info["title"], url=_page_url(info),
                   entries=list(law["toc"]))

    async def get_legislation_provision(self, id, provision):
        info, law = await _law(id)
        key = _norm_label(provision)
        if not key:
            raise BadRequest("give an article such as 'Art. 1er', '1', '351-1' or '5bis'.")
        hit = law["arts"].get(key)
        if hit is None:
            raise NotFound(f"no {provision!r} in {info['id']}. See get_legislation_toc for "
                           "the labels.")
        label, body = hit
        if not info["consolidated"]:
            body += f"\n\n*{_NOTE}*"
        return Provision(law_id=info["id"], law_title=info["title"], provision=label,
                         text=body, url=_page_url(info),
                         as_of=info["date"] if info["consolidated"] else "")

    async def get_legislation_text(self, id):
        info, law = await _law(id)
        meta = {"ELI": info["work"], "Status": info["status"],
                "Version": ("consolidated, applicable from " + info["date"])
                if info["consolidated"] else _NOTE}
        return LawText(id=info["id"], title=info["title"], text=law["text"],
                       url=_page_url(info), as_of=info["date"] if info["consolidated"] else "",
                       metadata={k: v for k, v in meta.items() if v})
