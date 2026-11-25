"""Albania: legislation from the Qendra e Botimeve Zyrtare (qbz.gov.al) and case law
from the Gjykata e Lartë (High Court, gjykataelarte.gov.al).

Gotchas this code encodes:
  * qbz.gov.al is an Angular SPA over a public JSON API at /api/v1 (no auth).
    GET /acts?q=&type=&from=&to=&page=(0-based)&size= searches title, number and
    institution (not full text); words are ANDed and ë/e, ç/c are folded.
    from/to must be YYYY-MM-DD (HTTP 400 otherwise). Our law id is QBZ's numeric
    act id ("12004"); an ELI path ("/eli/ligj/2015/04/30/44") is also accepted and
    resolved with GET /eli?path=.
  * The text is the act's Word file (/files/<sha>.docx, older ones .doc) or its
    text-layer PDF (/pdf/<sha>.pdf). GET /acts/<id>/versions lists consolidated
    versions ("versionNo", "validFrom"); we use the highest one, else the
    original as published. Neither docx nor Word 97 .doc readers are installed,
    so small parsers for both live here.
  * Do not use /publications?type=kode: those are priced (priceLek) code editions.
  * The 1990s base codes (Civil Code 7850/1994, Penal Code 7895/1995, Labour
    Code 7961/1995) are not in the act archive; only their amending acts are.
  * Articles are "Neni 12" (also "Neni 12/1" for inserted ones) on their own
    line, then a heading line. Amending acts quote whole articles of the amended
    law; a label is only taken the first time it appears, so quoted articles stay
    inside the article that quotes them.
  * The High Court backend is https://be.gjykataelarte.gov.al/public/ (JSON, no
    auth, x-ratelimit-limit: 50). documents/search is full-text over the decided
    files; dates must be ISO. Our decision id is the case number
    ("31001-02718-00-2014"); get_decision resolves it with filterVerdicts, then
    verdict?caseId=&caseNumber= gives a presigned S3 URL to the .doc/.docx.
    Decisions are not anonymised: party names appear in titles and text.
  * The backend index starts in 2005. The site (a Gatsby build over a Strapi CMS) also
    publishes, as Word files on the gjykata-media S3 bucket: the monthly volumes of all
    decisions 1999-2019 (/sq/vendimet-e-gjykates/vendimet-1999-2019), the Joint Colleges'
    unifying decisions 1999-2016 (/sq/vendime-unifikuese-ne-vite) and since 2018
    (/sq/vendime-per-njesiminndryshimin-e-praktikes-gjyqesore, /sq/vendime-kolegjet-e-bashkuara).
    Their lists come from each page's /page-data/sq/<slug>/page-data.json. Joint Colleges
    decisions in the backend carry the case category (CV/CR/CA) of the case, not their own.
    Our id for such a file is "media/<S3 key>"; only keys listed on those pages are fetched.
"""
from __future__ import annotations

import io
import re
import struct
import time
import zipfile
from urllib.parse import urlencode

from lxml import etree

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from .._http import fold_ascii as _fold
from ..models import Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc, TocEntry

QBZ = "https://qbz.gov.al"
QBZ_API = f"{QBZ}/api/v1"
GJL = "https://gjykataelarte.gov.al"
GJL_API = "https://be.gjykataelarte.gov.al/public"
_JSON = {"Accept": "application/json"}

_CATEGORY = {"civil": "CV", "penal": "CR", "administrative": "CA"}
_JOINT = ("joint", "kolegjet e bashkuara", "unifying", "unifikues")
MEDIA = "https://gjykata-media.s3.eu-central-1.amazonaws.com/"
_UNIFYING_PAGES = ("vendime-unifikuese-ne-vite", "vendime-per-njesiminndryshimin-e-praktikes-gjyqesore",
                   "vendime-kolegjet-e-bashkuara")
_ARCHIVE_PAGE = "vendimet-e-gjykates/vendimet-1999-2019"
_MONTHS = {"janar": 1, "shkurt": 2, "mars": 3, "prill": 4, "maj": 5, "qershor": 6, "korrik": 7,
           "gusht": 8, "shtator": 9, "tetor": 10, "nentor": 11, "nëntor": 11, "dhjetor": 12}
_GENERIC = {"unifikues", "unifikuese", "unifikuar", "njesues", "njesim", "njesimin", "njesimi", "unifying", "joint"}
_TTL = 6 * 3600
_CATEGORY_NAME = {"CV": "Kolegji Civil", "CR": "Kolegji Penal", "CA": "Kolegji Administrativ",
                  "Çështje Civile": "Kolegji Civil", "Çështje Penale": "Kolegji Penal",
                  "Çështje Administrative": "Kolegji Administrativ"}
_ORIGIN = {"seanceGjyqesore": "Seancë gjyqësore", "dhomeKeshilli": "Dhomë këshillimi"}

_act_cache: dict[str, dict] = {}
_text_cache: dict[str, tuple[list[str], str]] = {}
_pages: dict[str, dict] = {}       # slug -> {"t": monotonic, "files": [...]}


# --------------------------------------------------------------------------- #
# Word files (.docx and Word 97 .doc) -> paragraphs
# --------------------------------------------------------------------------- #
_W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def _tidy(s: str) -> str:
    return "\n".join(re.sub(r"[ \t\xa0]+", " ", ln).strip() for ln in s.split("\n")).strip()


def docx_paragraphs(data: bytes) -> list[str]:
    root = etree.fromstring(zipfile.ZipFile(io.BytesIO(data)).read("word/document.xml"))
    out = []
    for p in root.iter(_W + "p"):
        s = ""
        for el in p.iter(_W + "t", _W + "tab", _W + "br"):
            s += (el.text or "") if el.tag == _W + "t" else (" " if el.tag == _W + "tab" else "\n")
        if s := _tidy(s):
            out.append(s)
    return out


def _cfb_streams(data: bytes) -> dict[str, bytes]:
    """Streams of an OLE2 compound file (the container of .doc files)."""
    ssz = 1 << struct.unpack_from("<H", data, 30)[0]
    mssz = 1 << struct.unpack_from("<H", data, 32)[0]
    n_fat, dir_start = struct.unpack_from("<II", data, 44)
    cutoff, minifat_start, n_minifat, dif_start, n_dif = struct.unpack_from("<IIIII", data, 56)

    def sector(i):
        return data[512 + i * ssz: 512 + (i + 1) * ssz]

    difat = list(struct.unpack_from("<109I", data, 76))
    s = dif_start
    for _ in range(n_dif):
        vals = struct.unpack(f"<{ssz // 4}I", sector(s))
        difat += vals[:-1]
        s = vals[-1]
    fat = []
    for i in difat[:n_fat]:
        fat += struct.unpack(f"<{ssz // 4}I", sector(i))

    def chain(start, table):
        seen, out = set(), []
        while start < 0xFFFFFFFA and start < len(table) and start not in seen:
            seen.add(start)
            out.append(start)
            start = table[start]
        return out

    dirs = b"".join(sector(i) for i in chain(dir_start, fat))
    entries = []
    for off in range(0, len(dirs) - 127, 128):
        e = dirs[off:off + 128]
        nlen = struct.unpack_from("<H", e, 64)[0]
        start, size = struct.unpack_from("<II", e, 116)
        entries.append((e[:max(0, nlen - 2)].decode("utf-16-le", "replace"), e[66], start, size))
    root = next(e for e in entries if e[1] == 5)
    ministream = b"".join(sector(i) for i in chain(root[2], fat))
    minifat = []
    for i in chain(minifat_start, fat)[:n_minifat]:
        minifat += struct.unpack(f"<{ssz // 4}I", sector(i))
    out = {}
    for name, typ, start, size in entries:
        if typ != 2:
            continue
        if size < cutoff:
            buf = b"".join(ministream[i * mssz:(i + 1) * mssz] for i in chain(start, minifat))
        else:
            buf = b"".join(sector(i) for i in chain(start, fat))
        out[name] = buf[:size]
    return out


def doc_paragraphs(data: bytes) -> list[str]:
    """Main-document text of a Word 97-2003 .doc, read through its piece table."""
    st = _cfb_streams(data)
    wd = st["WordDocument"]
    table = st["1Table" if struct.unpack_from("<H", wd, 0x0A)[0] & 0x0200 else "0Table"]
    ccp_text = struct.unpack_from("<i", wd, 0x4C)[0]
    fc_clx, lcb_clx = struct.unpack_from("<II", wd, 0x1A2)
    clx = table[fc_clx:fc_clx + lcb_clx]
    i = 0
    while clx[i] == 0x01:                                     # Prc (formatting), skip
        i += 3 + struct.unpack_from("<H", clx, i + 1)[0]
    if clx[i] != 0x02:
        raise ValueError("no piece table")
    lcb = struct.unpack_from("<I", clx, i + 1)[0]
    plc = clx[i + 5:i + 5 + lcb]
    n = (lcb - 4) // 12
    cps = struct.unpack_from(f"<{n + 1}i", plc, 0)
    text = []
    for k in range(n):
        start, end = cps[k], min(cps[k + 1], ccp_text)
        if start >= end:
            break
        fc = struct.unpack_from("<I", plc, 4 * (n + 1) + 8 * k + 2)[0]
        cnt = end - start
        if fc & 0x40000000:                                   # compressed: cp1252
            off = (fc & ~0x40000000) // 2
            text.append(wd[off:off + cnt].decode("cp1252", "replace"))
        else:
            text.append(wd[fc:fc + 2 * cnt].decode("utf-16-le", "replace"))
    s = "".join(text)
    s = re.sub(r"\x13[^\x13\x14\x15]*\x14", "", s)          # field code, keep its result
    s = re.sub(r"\x13[^\x13\x14\x15]*\x15", "", s)          # field without result
    s = s.replace("\x0b", "\n").replace("\x07", "\r").replace("\x0c", "\r")
    s = re.sub(r"[\x00-\x08\x0e-\x1f]", "", s)
    return [p for p in (_tidy(p) for p in s.split("\r")) if p]


def word_paragraphs(data: bytes) -> list[str]:
    if data[:2] == b"PK":
        return docx_paragraphs(data)
    if data[:8] == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
        return doc_paragraphs(data)
    raise ValueError("not a Word file")


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #
async def _json(url: str, what: str):
    try:
        r = await _http.get(url, headers=_JSON)
    except Exception as e:
        raise SourceError(f"{what}: {e}", "network") from e
    if r.status_code == 404:
        raise NotFound(f"{what}: not found")
    if r.status_code == 400:
        try:
            msg = r.json().get("error") or r.json().get("message") or r.text[:200]
        except ValueError:
            msg = r.text[:200]
        raise BadRequest(f"{what} rejected the request: {msg}")
    if r.status_code != 200:
        raise SourceError(f"{what} failed", r.status_code)
    try:
        return r.json()
    except ValueError as e:
        raise SourceError(f"{what}: unexpected non-JSON reply", r.status_code) from e


async def _file(url: str, what: str) -> bytes:
    try:
        r = await _http.get(url)
    except Exception as e:
        raise SourceError(f"{what}: {e}", "network") from e
    if r.status_code != 200 or not r.content:
        raise SourceError(f"{what} not available", r.status_code)
    return r.content


def _iso(s) -> str:
    return _http.iso_date(str(s or "")[:10])


def _check_filters(filters, allowed) -> dict:
    f = {k: v for k, v in dict(filters or {}).items() if v not in (None, "")}
    unknown = set(f) - set(allowed)
    if unknown:
        raise BadRequest(f"Unknown filter(s): {', '.join(sorted(unknown))}. "
                         f"Supported: {', '.join(allowed)}")
    return f


def _date_filter(v, name: str, end: bool = False) -> str:
    v = str(v).strip()
    if re.fullmatch(r"\d{4}", v):
        return f"{v}-12-31" if end else f"{v}-01-01"
    d = _http.iso_date(v)
    if not d:
        raise BadRequest(f"{name} must be YYYY-MM-DD or YYYY, got {v!r}")
    return d


# --------------------------------------------------------------------------- #
# Legislation (qbz.gov.al)
# --------------------------------------------------------------------------- #
async def _act(id) -> dict:
    raw = _http.clean(id)
    if raw.startswith(QBZ):
        raw = raw[len(QBZ):]
    m = re.fullmatch(r"(?:/akt/)?(\d+)", raw)
    if m:
        aid = m[1]
    elif raw.startswith("/eli/"):
        d = await _json(f"{QBZ_API}/eli?{urlencode({'path': raw})}", f"qbz.gov.al ELI {raw}")
        aid = str(d.get("actId") or "")
        if not aid:
            raise NotFound(f"No act for ELI {raw} on qbz.gov.al")
    else:
        raise BadRequest(f"Law id must be a qbz.gov.al act id like '12004' or an ELI path like "
                         f"'/eli/ligj/2015/04/30/44'; got {id!r}")
    if aid in _act_cache:
        return _act_cache[aid]
    act = await _json(f"{QBZ_API}/acts/{aid}", f"qbz.gov.al act {aid}")
    try:
        act["_versions"] = await _json(f"{QBZ_API}/acts/{aid}/versions", f"qbz.gov.al act {aid} versions")
    except NotFound:
        act["_versions"] = []
    return _http.lru_put(_act_cache, aid, act, 200)


def _act_title(a: dict) -> str:
    t = _http.clean(a.get("title")).rstrip(" .")
    num = _http.clean(a.get("number"))
    head = f"{a.get('type') or 'Akt'} nr. {num}" if num else (a.get("type") or "Akt")
    date = _iso(a.get("date"))
    return f"{head}, datë {date}: {t}" if date else f"{head}: {t}"


def _act_url(a: dict) -> str:
    return f"{QBZ}/akt/{a['id']}"


async def _act_paragraphs(a: dict) -> tuple[list[str], str]:
    """Paragraphs of the latest consolidated version (or the act as published), and its date."""
    aid = str(a["id"])
    if aid in _text_cache:
        return _text_cache[aid]
    vers = [v for v in a.get("_versions") or [] if (v.get("word") or v.get("pdf"))]
    src = max(vers, key=lambda v: v.get("versionNo") or 0) if vers else a
    as_of = _iso(src.get("validFrom")) if vers else ""
    paras: list[str] = []
    word = (src.get("word") or {}).get("url")
    if word:
        try:
            paras = word_paragraphs(await _file(QBZ + word, f"qbz.gov.al act {aid} Word file"))
        except (ValueError, KeyError, struct.error, IndexError, zipfile.BadZipFile, etree.XMLSyntaxError):
            paras = []
    if not paras and (src.get("pdf") or {}).get("url"):
        text = _http.pdf_text(await _file(QBZ + src["pdf"]["url"], f"qbz.gov.al act {aid} PDF"))
        paras = [p for p in text.split("\n") if p]
    if not paras:
        raise SourceError(f"qbz.gov.al act {aid}: no readable text file", "no-text")
    return _http.lru_put(_text_cache, aid, (paras, as_of), 20)


_NENI = re.compile(r"^Neni\s+(\d+(?:/\d+)?(?:\s*[a-zë])?)\b\.?\s*(?:[-–—.:]\s*)?(.*)$", re.S | re.I)
_HEAD = re.compile(r"^(PJESA|TITULLI|KREU|SEKSIONI|KAPITULLI)\b", re.I)


def _structure(paras: list[str]) -> list[tuple[TocEntry, int, int]]:
    """TOC entries with the paragraph span [start, end) each article covers."""
    out, seen = [], set()
    arts = []  # indices into out that are articles
    for i, p in enumerate(paras):
        m = _NENI.match(p)
        if m and len(p) < 200:
            label = "Neni " + re.sub(r"\s+", "", m[1])
            if label in seen:
                continue
            seen.add(label)
            head = _http.clean(m[2])
            if not head and i + 1 < len(paras) and len(paras[i + 1]) < 150 \
                    and not _NENI.match(paras[i + 1]) and not re.match(r"^\d+[.)]", paras[i + 1]):
                head = _http.clean(paras[i + 1])
            out.append([TocEntry(title=f"{label} - {head}" if head else label, level=1,
                                 provision=label), i, len(paras)])
            arts.append(len(out) - 1)
        elif _HEAD.match(p) and len(p) < 200:
            title = _http.clean(p)
            if i + 1 < len(paras) and len(paras[i + 1]) < 200 and not _NENI.match(paras[i + 1]) \
                    and not _HEAD.match(paras[i + 1]) and paras[i + 1].isupper():
                title += " - " + _http.clean(paras[i + 1])
            out.append([TocEntry(title=title, level=0), i, i + 1])
    # an article runs until the next article or structural heading
    for k, e in enumerate(out):
        if e[0].provision:
            nxt = next((o[1] for o in out[k + 1:]), len(paras))
            e[2] = nxt
    return [tuple(e) for e in out]


def _provision_label(provision) -> str:
    p = _http.clean(provision)
    m = re.fullmatch(r"(?:neni|nenin|nenit|art\.?|article|§)?\s*(\d+(?:/\d+)?(?:\s*[a-zë])?)\.?", p, re.I)
    if not m:
        raise BadRequest(f"Provision must be an article like 'Neni 5', '5' or 'Neni 12/1'; got {provision!r}")
    return "Neni " + re.sub(r"\s+", "", m[1]).lower()


_AMENDING = re.compile(r"\b(?:ndryshim\w*|shtes\w*|plotesim\w*)\b.*\bligj\w*\s+nr", re.I)


def _amending_warning(a: dict) -> str:
    """Plain warning when the act is an amending act: its text is the amendment, not the base law."""
    if _AMENDING.search(_fold(_http.clean(a.get("title")))):
        return ("> Warning: this is an AMENDING act. Its text is the amendment instructions, not the "
                "consolidated text of the law it amends (the base law is not in QBZ's archive if it "
                "dates from the 1990s).\n\n")
    return ""


def _md(paras: list[str]) -> str:
    out = []
    for p in paras:
        if _NENI.match(p) and len(p) < 200 or _HEAD.match(p) and len(p) < 200:
            out.append(f"**{p}**")
        else:
            out.append(p.replace("\n", "  \n"))
    return "\n\n".join(out)


# --------------------------------------------------------------------------- #
# Case law (gjykataelarte.gov.al)
# --------------------------------------------------------------------------- #
def _decision_url(case_id: str, case_number: str) -> str:
    return f"{GJL}/sq/download-vendimet/?{urlencode({'caseId': case_id, 'caseNumber': case_number})}"


def _snippet(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s or "")
    s = s.replace("&#x2F;", "/").replace("&quot;", '"').replace("&#x27;", "'").replace("&#39;", "'")
    s = s.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    return _http.clean(s)


_RANK_WINDOW = 100


def _act_rank(a: dict, q: str):
    """Sort key: query phrase in the title, laws first, base over amending acts, then the shorter title."""
    t = _fold(_act_title(a))
    return (q not in t, _fold(a.get("type") or "") != "ligj", "ndryshues" in _fold(a.get("kind") or ""),
            len(t))


_BASE_LAWS = ("7850", "8417", "7895", "7961", "kodi civil", "kodi penal", "kodi i punes", "kushtetut")


def _base_law_note(query: str) -> str:
    if not any(w in _fold(query) for w in _BASE_LAWS):
        return ""
    return ("NOT AVAILABLE: the base text of the Civil Code (7850/1994), Penal Code (7895/1995), Labour Code "
            "(7961/1995) and Constitution (8417/1998) is not in QBZ's archive and cannot be fetched through "
            "Fontes; the hits below are only acts amending them. ")


async def _page_files(slug: str) -> list[dict]:
    """Word files a gjykataelarte.gov.al page lists: [{key, title, url, ext, group}], cached 6 h."""
    hit = _pages.get(slug)
    if hit and time.monotonic() - hit["t"] < _TTL:
        return hit["files"]
    d = await _json(f"{GJL}/page-data/sq/{slug}/page-data.json", f"gjykataelarte.gov.al page {slug}")
    article = (((d.get("result") or {}).get("data") or {}).get("api") or {}).get("article") or {}
    out: list[dict] = []

    def walk(o, group):
        if isinstance(o, dict):
            tab = o.get("tabTitle")
            if isinstance(tab, dict) and (tab.get("text_sq") or "").strip():
                group = tab["text_sq"].strip()
            f, t = o.get("file"), o.get("title")
            if isinstance(f, dict) and isinstance(t, dict) and str(f.get("url", "")).startswith(MEDIA):
                key = f["url"][len(MEDIA):]
                if not any(x["key"] == key for x in out):
                    out.append({"key": key, "title": _http.clean(t.get("text_sq")), "url": f["url"],
                                "ext": f.get("ext") or "", "group": group})
            for k, v in o.items():
                if k != "file":
                    walk(v, group)
        elif isinstance(o, list):
            for v in o:
                walk(v, group)

    walk(article.get("body") or [], "")
    if not out:
        raise SourceError(f"gjykataelarte.gov.al page {slug}: no decision files found; layout changed", "layout")
    _pages[slug] = {"t": time.monotonic(), "files": out}
    return out


def _title_date(title: str) -> str:
    m = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", title or "")
    return f"{m[3]}-{int(m[2]):02d}-{int(m[1]):02d}" if m else ""


def _unifying_college(title: str) -> str:
    t = _fold(title)
    for k, v in (("civil", "Civil"), ("penal", "Penal"), ("administrativ", "Administrativ")):
        if k in t:
            return v
    return ""


def _media_hit(f: dict, court: str, snippet: str = "") -> DecisionHit:
    return DecisionHit(id=f"media/{f['key']}", title=f["title"], court=court, date=_title_date(f["title"]),
                       snippet=snippet, url=f["url"])


class Albania(Jurisdiction):
    code = "al"
    name = "Albania"
    languages = ("sq",)
    aliases = ("albania", "shqipëri", "shqiperi", "shqipëria", "shqiperia", "alb")
    sources = (
        Source(
            name="Qendra e Botimeve Zyrtare (qbz.gov.al, Ministry of Justice)",
            url=QBZ,
            covers=("legislation",),
            licence="Not stated. FAQ: published information is accessible to the general public "
                    "without any restriction",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="Not published; 1 request/s self-imposed, no 429 seen in a handful of "
                       "requests (2026-11-05)",
            terms_url=f"{QBZ}/faq",
        ),
        Source(
            name="Gjykata e Lartë (High Court of Albania, gjykataelarte.gov.al)",
            url=GJL,
            covers=("caselaw",),
            licence="Not stated. Terms: the website is free to use and available to all users; "
                    "only unlawful use is forbidden",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="API sends x-ratelimit-limit: 50 (window not stated); 1.5 s between "
                       "requests self-imposed",
            terms_url=f"{GJL}/sq/termat-e-perdorimit",
        ),
    )
    caselaw_filters = {
        "category": ("Kolegji: civil, penal or administrative; or joint (Kolegjet e Bashkuara: the list of "
                     "unifying decisions 1999 to now; the query then matches their titles)"),
        "archive_year": ("1999-2019: list that year's published monthly volumes of all decisions (full text; "
                         "decisions before 2005 are only there)"),
        "date_from": "Decision date from (YYYY-MM-DD or YYYY)",
        "date_to": "Decision date to (YYYY-MM-DD or YYYY)",
        "case_number": "Case number, e.g. '31001-02718-00-2014'",
    }
    legislation_filters = {
        "type": "Act type as QBZ names it: Ligj, Vendim, Dekret, Udhëzim, Urdhër, ...",
        "date_from": "Act date from (YYYY-MM-DD or YYYY)",
        "date_to": "Act date to (YYYY-MM-DD or YYYY)",
    }
    min_interval = {"qbz.gov.al": 1.0, "be.gjykataelarte.gov.al": 1.5, "gjykataelarte.gov.al": 1.0,
                    "gjykata-media.s3.eu-central-1.amazonaws.com": 1.0,
                    "vendimet-perfundimtare.s3.eu-central-1.amazonaws.com": 1.0}
    notes = ("Albanian only. Legislation: acts in the Fletorja Zyrtare from qbz.gov.al, with the "
             "latest consolidated version where QBZ has one; search matches titles and numbers, "
             "not full text; 1990s base laws (Constitution 8417/1998, Civil, Penal, Labour Codes) are missing: a search for their number returns only amending acts. Case law: High "
             "Court decisions 2005 on, full-text search; Joint Colleges unifying decisions 1999 on "
             "(category=joint); 1999-2019 monthly volumes (archive_year); not anonymised. The "
             "Constitutional Court is not covered.")
    gaps = (
        ("Constitutional Court (gjykatakushtetuese.gov.al): WordPress pages with PDFs, Imunify bot"
         " check present; not built yet"),
        "Appeal, first-instance and administrative courts: not researched yet",
        ("High Court decisions 1999-2004: only in the monthly volumes (archive_year), which are read "
         "whole and are not full-text searchable"),
        ("1990s base laws (Constitution 8417/1998, Civil Code 7850/1994, Penal Code 7895/1995, Labour "
         "Code 7961/1995): not in QBZ's act archive, only their amendments"),
        "Full-text search of legislation: QBZ's API matches title, number and institution only",
    )
    samples = {
        "caselaw_query": "pronesi",
        "decision_id": "31001-02718-00-2014",
        "legislation_query": "Kodi i Procedurave Administrative",
        "law_id": "12004",
        "provision": "Neni 1",
    }

    # ----------------------------------------------------------------- caselaw
    async def search_caselaw(self, query, *, limit, page, filters) -> Results[DecisionHit]:
        f = _check_filters(filters, self.caselaw_filters)
        if f.get("archive_year"):
            return await self._archive(query, f, limit, page)
        if str(f.get("category") or "").lower() in _JOINT:
            return await self._unifying(query, f, limit, page)
        params = {"q": _http.clean(query), "page": page - 1, "size": limit}
        if f.get("category"):
            cat = str(f["category"]).lower()
            if cat not in _CATEGORY:
                raise BadRequest(f"category must be one of {', '.join(_CATEGORY)}, joint")
            params["caseCategory"] = _CATEGORY[cat]
        if f.get("case_number"):
            params["caseNumber"] = _http.clean(f["case_number"])
        if f.get("date_from") or f.get("date_to"):
            params["firstDate"] = _date_filter(f.get("date_from") or "1990", "date_from")
            params["secondDate"] = _date_filter(f.get("date_to") or _http.today(), "date_to", end=True)
        if not params["q"]:
            if not params.get("caseNumber"):
                raise BadRequest("The High Court search needs a query word; filters alone are rejected "
                                 "upstream. Give a query (a case number works as the query).")
            params["q"] = params["caseNumber"]
        d = await _json(f"{GJL_API}/documents/search?{urlencode(params)}", "gjykataelarte.gov.al search")
        hits = []
        for c in d.get("content") or []:
            v = (c.get("verdicts") or [{}])[0]
            num = _http.clean(v.get("caseNumber")) or re.sub(r"\.docx?$", "", c.get("fileName") or "")
            if not num:
                continue
            court = _CATEGORY_NAME.get(v.get("caseCategory"), "Gjykata e Lartë")
            title = _http.clean(v.get("caseTitle")) or num
            hits.append(DecisionHit(
                id=num, title=f"{title} (nr. {v['verdictNumber']})" if v.get("verdictNumber") else title,
                court=f"Gjykata e Lartë, {court}" if court != "Gjykata e Lartë" else court,
                date=_iso(v.get("verdictDate")), case_number=num,
                snippet=" … ".join(_snippet(s) for s in (c.get("snippets") or [])[:2])[:500],
                url=_decision_url(v.get("caseId") or "", num)))
        total = d.get("totalElements")
        return Results(items=hits, total=total if isinstance(total, int) else None,
                       note=("Full-text search of decisions from 2005; matches ignore diacritics (pronesi = pronësi). "
                             "Decisions 1999-2004 are NOT in this search: tell the user so, and list them by "
                             "month with the archive_year filter (each volume opens whole)."))

    async def _unifying(self, query, f, limit, page) -> Results:
        if f.get("case_number") or f.get("archive_year"):
            raise BadRequest("category=joint takes a query and date_from/date_to only.")
        lo = _date_filter(f["date_from"], "date_from") if f.get("date_from") else ""
        hi = _date_filter(f["date_to"], "date_to", end=True) if f.get("date_to") else ""
        q = " ".join(w for w in _fold(_http.clean(query)).split() if w not in _GENERIC)
        files = []
        for slug in _UNIFYING_PAGES:
            for x in await _page_files(slug):
                if not any(y["key"] == x["key"] for y in files):
                    files.append(x)
        hits = []
        for x in files:
            d = _title_date(x["title"])
            if (q and not all(w in _fold(x["title"]) for w in q.split())) or (lo and d and d < lo) \
                    or (hi and d and d > hi):
                continue
            col = _unifying_college(x["title"])
            hits.append(_media_hit(x, "Gjykata e Lartë, Kolegjet e Bashkuara",
                                   f"Vendim unifikues ({col})" if col else "Vendim unifikues"))
        hits.sort(key=lambda h: h.date, reverse=True)
        start = (page - 1) * limit
        return Results(items=hits[start:start + limit], total=len(hits),
                       note=("Every entry here is already a unifying decision, so words like 'unifikues' or "
                             "'njësues' are ignored; titles hold only number, date and college. "
                             "Joint Colleges unifying decisions as the court lists them (1999-2016, and on "
                             "njësimin/ndryshimin e praktikës since 2018); the query matches titles (number, "
                             "date, college) only. Their full text is also in the default full-text search "
                             "from 2005."))

    async def _archive(self, query, f, limit, page) -> Results:
        y = str(f["archive_year"]).strip()
        if not re.fullmatch(r"\d{4}", y) or not 1999 <= int(y) <= 2019:
            raise BadRequest("archive_year must be a year from 1999 to 2019.")
        q = _fold(_http.clean(query))
        hits = [_media_hit(x, "Gjykata e Lartë", f"Vëllim mujor i vendimeve, {y}")
                for x in await _page_files(_ARCHIVE_PAGE)
                if x["group"].strip() == y and (not q or all(w in _fold(x["title"]) for w in q.split()))]
        start = (page - 1) * limit
        return Results(items=hits[start:start + limit], total=len(hits),
                       note=("Monthly volumes: each id opens the whole month (a contents list, then every "
                             "decision in full). The query matches volume titles only (month, 'Kolegje te "
                             "Bashkuara')."))

    async def _media_decision(self, key: str) -> Decision:
        f, court = None, ""
        for slug in (*_UNIFYING_PAGES, _ARCHIVE_PAGE):
            f = next((x for x in await _page_files(slug) if x["key"] == key), None)
            if f:
                court = ("Gjykata e Lartë" if slug == _ARCHIVE_PAGE else "Gjykata e Lartë, Kolegjet e Bashkuara")
                break
        if f is None:
            raise NotFound(f"media/{key} is not on the High Court's lists of unifying decisions or of "
                           f"1999-2019 volumes.")
        data = await _file(f["url"], f"gjykataelarte.gov.al file {key}")
        try:
            paras = word_paragraphs(data)
        except (ValueError, KeyError, struct.error, IndexError, zipfile.BadZipFile, etree.XMLSyntaxError) as e:
            if data[:4] == b"%PDF":
                paras = [p for p in _http.pdf_text(data).split("\n") if p]
            else:
                raise SourceError(f"gjykataelarte.gov.al file {key}: unreadable ({e})", "parse") from e
        meta = {"Lista": f["group"]} if f["group"] else {}
        title = f["title"] if court.endswith("Bashkuara") else f"Vendimet e Gjykatës së Lartë, {f['title']}"
        return Decision(id=f"media/{key}", title=title,
                        text="\n\n".join(p.replace("\n", "  \n") for p in paras), url=f["url"],
                        court=court, date=_title_date(f["title"]), metadata=meta)

    async def get_decision(self, id) -> Decision:
        raw = _http.clean(id)
        if raw.startswith(MEDIA):
            raw = "media/" + raw[len(MEDIA):]
        if raw.startswith("media/"):
            key = raw[len("media/"):]
            if not re.fullmatch(r"[\w.-]+\.(?:docx?|pdf)", key):
                raise BadRequest(f"media id must look like 'media/<file>.doc' as search_caselaw gives it; got {id!r}")
            return await self._media_decision(key)
        num = _http.clean(id)
        if not re.fullmatch(r"[\w-]+", num):
            raise BadRequest(f"Decision id must be a High Court case number like "
                             f"'31001-02718-00-2014'; got {id!r}")
        rows = await _json(f"{GJL_API}/filterVerdicts?{urlencode({'caseNumber': num})}",
                           f"gjykataelarte.gov.al case {num}")
        rows = [r for r in rows or [] if r.get("caseNumber") == num and r.get("caseId")]
        if not rows:
            raise NotFound(f"No decided case {num} on gjykataelarte.gov.al")
        v = max(rows, key=lambda r: r.get("verdictDate") or "")
        d = await _json(f"{GJL_API}/verdict?{urlencode({'caseId': v['caseId'], 'caseNumber': num})}",
                        f"gjykataelarte.gov.al decision {num}")
        if not d.get("path"):
            raise NotFound(f"gjykataelarte.gov.al has no decision file for {num}")
        data = await _file(d["path"], f"gjykataelarte.gov.al decision {num} file")
        try:
            paras = word_paragraphs(data)
        except (ValueError, KeyError, struct.error, IndexError, zipfile.BadZipFile, etree.XMLSyntaxError) as e:
            if data[:4] == b"%PDF":
                paras = [p for p in _http.pdf_text(data).split("\n") if p]
            else:
                raise SourceError(f"gjykataelarte.gov.al decision {num}: unreadable file ({e})",
                                  "parse") from e
        court = _CATEGORY_NAME.get(v.get("caseCategory"), "")
        meta = {"Nr. vendimi": _http.clean(v.get("verdictNumber")),
                "Data e regjistrimit": _iso(v.get("registeredDate")),
                "Palë ndërgjyqëse": _http.clean(v.get("fillingParty")),
                "Shqyrtimi": _ORIGIN.get(v.get("origin"), _http.clean(v.get("origin"))),
                "Vendime të tjera në këtë çështje": str(len(rows) - 1) if len(rows) > 1 else ""}
        return Decision(id=num, title=_http.clean(v.get("caseTitle")) or num,
                        text="\n\n".join(p.replace("\n", "  \n") for p in paras),
                        url=_decision_url(v["caseId"], num),
                        court=f"Gjykata e Lartë, {court}" if court else "Gjykata e Lartë",
                        date=_iso(v.get("verdictDate")), case_number=num,
                        metadata={k: x for k, x in meta.items() if x})

    # ------------------------------------------------------------- legislation
    async def search_legislation(self, query, *, limit, page, filters) -> Results[LawHit]:
        f = _check_filters(filters, self.legislation_filters)
        params = {"q": _http.clean(query), "page": page - 1, "size": limit}
        window = bool(params["q"]) and page * limit <= _RANK_WINDOW
        if window:
            params.update(page=0, size=_RANK_WINDOW)
        if f.get("type"):
            params["type"] = _http.clean(f["type"])
        if f.get("date_from"):
            params["from"] = _date_filter(f["date_from"], "date_from")
        if f.get("date_to"):
            params["to"] = _date_filter(f["date_to"], "date_to", end=True)
        if not params["q"] and len(params) == 3:
            raise BadRequest("Give a search query or at least one filter.")
        d = await _json(f"{QBZ_API}/acts?{urlencode(params)}", "qbz.gov.al search")
        items = d.get("items") or []
        if window:
            # QBZ's own order puts amending orders first; rank the first window by title match instead
            q = _fold(params["q"])
            if not f.get("type") and (d.get("total") or 0) > len(items):
                # laws can sit beyond the window in QBZ's order: add the matching laws
                laws = await _json(f"{QBZ_API}/acts?{urlencode({**params, 'type': 'Ligj'})}", "qbz.gov.al search")
                seen = {a.get("id") for a in items}
                items = items + [a for a in laws.get("items") or [] if a.get("id") not in seen]
            items = sorted(items, key=lambda a: _act_rank(a, q))
            items = items[(page - 1) * limit:page * limit]
        hits = []
        for a in items:
            if not a.get("id"):
                continue
            g = a.get("gazette") or {}
            extra = [_http.clean(a.get("institution")), _http.clean(a.get("kind"))]
            if g.get("number"):
                extra.append(f"Fletorja Zyrtare nr. {g['number']}/{g.get('year') or ''}".rstrip("/"))
            hits.append(LawHit(id=str(a["id"]), title=_act_title(a), type=_http.clean(a.get("type")),
                               number=_http.clean(a.get("number")), date=_iso(a.get("date")),
                               snippet="; ".join(x for x in extra if x), url=_act_url(a)))
        total = d.get("total")
        return Results(items=hits, total=total if isinstance(total, int) else None,
                       note=(_base_law_note(query) +
                             "Matches act titles, numbers and institutions, not full text. Hits titled 'për disa "
                             "ndryshime në ligjin nr. X' are amending acts, not law X itself; 1990s base laws "
                             "(Constitution 8417/1998, Civil Code 7850/1994, ...) are not in QBZ's archive."))

    async def get_legislation_toc(self, id) -> Toc:
        a = await _act(id)
        paras, _ = await _act_paragraphs(a)
        return Toc(id=str(a["id"]), title=_act_title(a), url=_act_url(a),
                   entries=[e for e, _, _ in _structure(paras)])

    async def get_legislation_provision(self, id, provision) -> Provision:
        label = _provision_label(provision)
        a = await _act(id)
        paras, as_of = await _act_paragraphs(a)
        for e, s, t in _structure(paras):
            if e.provision.lower() == label.lower():
                return Provision(law_id=str(a["id"]), law_title=_act_title(a), provision=e.provision,
                                 text=_amending_warning(a) + _md(paras[s:t]), url=_act_url(a), as_of=as_of)
        raise NotFound(f"{label} not found in act {a['id']}; see get_legislation_toc for the articles")

    async def get_legislation_text(self, id) -> LawText:
        a = await _act(id)
        paras, as_of = await _act_paragraphs(a)
        g = a.get("gazette") or {}
        vers = a.get("_versions") or []
        meta = {"Lloji": _http.clean(a.get("type")), "Numri": _http.clean(a.get("number")),
                "Data": _iso(a.get("date")), "Institucioni": _http.clean(a.get("institution")),
                "Fletorja Zyrtare": f"nr. {g['number']}/{g.get('year')}" if g.get("number") else "",
                "ELI": f"{QBZ}{a['eliPath']}" if a.get("eliPath") else "",
                "Teksti": (f"version i konsoliduar nr. {max(v.get('versionNo') or 0 for v in vers)}"
                           if vers else "teksti i botuar")}
        return LawText(id=str(a["id"]), title=_act_title(a), text=_amending_warning(a) + _md(paras), url=_act_url(a),
                       as_of=as_of, metadata={k: v for k, v in meta.items() if v})
