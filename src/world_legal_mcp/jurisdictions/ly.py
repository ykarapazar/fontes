"""Libya: laws, executive regulations, ministerial decisions and treaties published by the
Ministry of Justice (aladel.gov.ly), and Supreme Court rulings from the court's own site
(alolya.gov.ly). Arabic.

How the source works (verified 2026-11-06, UK IP, honest User-Agent):
  * aladel.gov.ly/home/ is a WordPress site. Its public REST API
    /home/wp-json/wp/v2/posts?search=&categories=&per_page=&page= lists posts (X-WP-Total gives
    the hit count; a page past the end answers 400 rest_post_invalid_page_number). Search
    matches title and body.
  * Legislation lives in the "القوانين والقرارات" categories: laws by field (ids 74-83, 85),
    executive regulations (22), ministerial decisions by year (23, 115-118, 127, 160), treaties
    and charters (19, 20). Drafts (84) are left out. About 190 laws/regulations/treaties plus
    about 150 ministerial decisions (mostly staff matters), posted 2014-2016, 2019.
  * The id is the WordPress post id ("1246"); /home/?p=<id> opens the post. Most posts carry
    the law's text as HTML. Some only link a PDF in wp-content/uploads: those are read through
    the PDF text layer (size checked first, 40 MB cap; Arabic presentation forms folded with
    NFKC). Scanned PDFs and image-only posts raise a SourceError pointing at the file (no OCR).
  * Texts are as the ministry typed them: original enactments, not consolidated. Many laws use
    the Gaddafi-era calendars (e.g. "1373 و.ر.", "1425 ميلادية").

Terms and robots.txt (2026-11-06):
  * aladel.gov.ly: /robots.txt is a 404 (no rules). No terms-of-use page among the site's 86
    pages; footer "2025 -2026 © جميع الحقوق محفوظة وزارة العدل - ليبيا" ("all rights reserved,
    Ministry of Justice - Libya"). Nothing on automated access.

Supreme Court (alolya.gov.ly, verified 2026-11-10):
  * Next.js site; pages are server-rendered and carry their data in the React Server Components
    stream (self.__next_f.push chunks: "<id>:<json>" rows, long strings as "<id>:T<hex bytes>,"
    rows referenced as "$<id>"). Only these HTML pages are read; robots.txt disallows /api/,
    /pdf-viewer and /favorite and allows everything else.
  * /legal-principles (tabs civil, criminal, administrative, personal status, combined chambers,
    15 per page, ?page=N) and /constitutional-court list every ruling the court has put online:
    62 on 2026-11-10 (= the /article/ entries of sitemap.xml), decided 2020-2026. Each
    /article/<uuid> holds the full text: principles, facts, procedure, reasons, operative part,
    panel. The uuid is the id.
  * /technical-office lists the court's journal (مجلة المحكمة العليا) by judicial year,
    paginated with ?page_<type uuid>=N. Years 1-36 are marked not available; 37-60 link a PDF on
    dashboard.alolya.gov.ly (robots.txt: allow all). Sampled 2026-11-10: years 51, 55 and 60
    have a text layer; 37, 41 and 48 are scans (no OCR here). Year 60's text layer inserts a
    stray "ن" after "د" in places ("الدنعوى"); kept as given.
  * /principle (8,240+ principles since 1953) is searched in the browser through /api/,
    which robots.txt disallows: not used.
  * No terms page; footer "جميع الحقوق محفوظة، المحكمة العليا" (all rights reserved).

Not used:
  * supremecourt.gov.ly (old Supreme Court host): Sucuri firewall page "502 Hosting Server
    Connect Timeout" on robots.txt and home page (2026-11-06). Replaced by alolya.gov.ly.
  * lawsociety.ly (private Libyan legislation/judgment database, non-official): robots.txt
    allows only /akn/ and /wp-json/ls/v1/document for bots and blocks the search API; its
    terms page answered a Cloudflare JavaScript challenge (403). Not used.
  * itcadel.gov.ly (MoJ information and documentation centre): "الموقع قيد التطوير" (under
    construction). parliament.ly: robots.txt disallows every query string and /wp- (no search).
  * pm.gov.ly (Cabinet, Joomla): robots.txt disallows /images/ where documents sit; not built.
"""
from __future__ import annotations

import json
import re
import time
import unicodedata
from urllib.parse import urlsplit

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc, TocEntry

HOST = "aladel.gov.ly"
BASE = f"https://{HOST}/home"
API = BASE + "/wp-json/wp/v2/posts"
SRC = "Ministry of Justice (aladel.gov.ly)"
MAX_PDF = 40_000_000

TYPES = {
    "law": (74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 85),
    "regulation": (22,),
    "decision": (23, 115, 116, 117, 118, 127, 160),
    "treaty": (19, 20),
}
ALL_CATS = tuple(c for v in TYPES.values() for c in v)
CAT_NAMES = {
    74: "الملكية الفكرية", 75: "تشريعات السياحية", 76: "تشريعات القانون المدني",
    77: "تشريعات العمل والخدمة المدنية", 78: "تشريعات الشعب المسلح",
    79: "تشريعات المواصلات المواني", 80: "التشريعات الإجتماعية", 81: "التشريعات المالية",
    82: "التشريعات الجنائية", 83: "التشريعات القضائية", 85: "قانون العدالة الانتقالية",
    22: "اللوائح التنفيذية", 23: "القرارات التنظيمية", 115: "قرارات 2014م", 116: "قرارات 2015م",
    117: "قرارات 2013م", 118: "قرارات 2012م", 127: "قرارات 2016م", 160: "قرارات 2019م",
    19: "الاتفاقيات", 20: "المواثيق",
}

_cache: dict = {}
_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")
_NUMBER = re.compile(r"رق[مـ]+\s*\(*\s*(\d+)\s*\)*\s*(?:ل?سن[هة]\s*)?(\d{2,4})?")

# Arabic ordinal words (after _norm: no tatweel/diacritics, alef unified, ة→ه, ى→ي).
_UNITS = {"اول": 1, "اولي": 1, "حادي": 1, "حاديه": 1, "ثاني": 2, "ثانيه": 2, "ثالث": 3,
          "ثالثه": 3, "رابع": 4, "رابعه": 4, "خامس": 5, "خامسه": 5, "سادس": 6, "سادسه": 6,
          "سابع": 7, "سابعه": 7, "سبعه": 7, "ثامن": 8, "ثامنه": 8, "تاسع": 9, "تاسعه": 9,
          "عاشر": 10, "عاشره": 10}
_TENS = {"عشرون": 20, "عشرين": 20, "ثلاثون": 30, "ثلاثين": 30, "اربعون": 40, "اربعين": 40,
         "خمسون": 50, "خمسين": 50, "ستون": 60, "ستين": 60, "سبعون": 70, "سبعين": 70,
         "ثمانون": 80, "ثمانين": 80, "تسعون": 90, "تسعين": 90}
_HUNDS = {"مائه": 100, "مئه": 100, "مائتين": 200, "مئتين": 200, "مائتان": 200,
          "ثلاثمائه": 300, "ثلاثمئه": 300, "اربعمائه": 400, "اربعمئه": 400,
          "خمسمائه": 500, "خمسمئه": 500, "ستمائه": 600, "سبعمائه": 700, "ثمانمائه": 800,
          "تسعمائه": 900, "الف": 1000}
_ART_NUM = re.compile(r"^[\W_]{0,4}(?:ال)?ماد[هة]\s*[\(\)\[\]]*\s*(\d{1,4})\s*[\(\)\[\]]*\s*"
                      r"(مكرر(?:\s*[\(\)]*\s*[ابجد]\s*[\(\)]*)?)?\s*[\(\)\[\]]?\s*[:.\-–]?\s*(.*)$")
_ART_WORD = re.compile(r"^[\W_]{0,4}(?:ال)?ماد[هة]\s+(.*)$")
_HEADING = re.compile(r"^[\W_]{0,4}(?:ال)?(كتاب|باب|فصل|فرع|قسم)\s+\S")
_HEAD_LEVEL = {"كتاب": 0, "باب": 0, "فصل": 1, "فرع": 2, "قسم": 2}


def _norm(s: str) -> str:
    """Fold for matching: digits to ASCII, no tatweel/diacritics, alef/ya/ta-marbuta unified."""
    s = unicodedata.normalize("NFKC", s or "").translate(_DIGITS)
    s = re.sub(r"[ـً-ْ‌-‏]", "", s)
    s = re.sub(r"[أإآ]", "ا", s).replace("ة", "ه").replace("ى", "ي")
    return re.sub(r"عشر\s+ه\b", "عشره", s)


def _ordinal(words: str) -> tuple[int, str]:
    """'الحادية والعشرون بعد المائة ...' -> (121, rest after the number words); (0, words) if none."""
    toks = words.split()
    total = unit = 0
    i = 0
    while i < len(toks):
        t = toks[i].strip("،,.:-–")
        if t == "بعد" and total + unit:
            i += 1
            continue
        w = t[1:] if t.startswith("و") and len(t) > 3 else t
        w = w[2:] if w.startswith("ال") else w
        if w in _UNITS:
            unit = _UNITS[w]
        elif w in ("عشر", "عشره") and unit:
            unit += 10
        elif w in _TENS:
            total += _TENS[w]
        elif w in _HUNDS:
            total += _HUNDS[w]
        else:
            break
        i += 1
    return total + unit, " ".join(toks[i:])


def _article(line: str) -> str:
    """Provision label if `line` starts an article ('مادة ( 5 )', 'المادة الخامسة', '5 مكرر'), else ''."""
    n = _norm(line)
    m = _ART_NUM.match(n)
    if m:
        return m[1].lstrip("0") + (" مكرر" if m[2] else "")
    m = _ART_WORD.match(n)
    if m:
        num, rest = _ordinal(m[1])
        if num and (len(rest) <= 40 or rest[:1] in ":-–."):
            return str(num)
    return ""


def _heading(line: str) -> int | None:
    m = _HEADING.match(_norm(line))
    return _HEAD_LEVEL[m[1]] if m and len(line) <= 80 else None


def _label(provision: str) -> str:
    """User's provision ('Madde 5', 'art. 5', 'المادة الخامسة', '5 مكرر', '5 (2)') -> TOC label."""
    p = _norm(_http.clean(provision))
    dup = re.search(r"\((\d+)\)\s*$", p)
    suffix = f" ({dup[1]})" if dup and re.search(r"\d.*\(\d+\)\s*$", p) else ""
    if suffix:
        p = p[:dup.start()]
    bis = " مكرر" if "مكرر" in p or re.search(r"\bbis\b", p, re.I) else ""
    m = re.search(r"\d+", p)
    if m:
        return m[0].lstrip("0") + bis + suffix
    words = re.sub(r"^(?:ال)?ماد[هة]\s+", "", p)
    num, _ = _ordinal(words)
    if num:
        return str(num) + bis + suffix
    raise BadRequest(f"Unknown provision {provision!r}. Use an article number as the TOC shows it, "
                     f"e.g. '5', 'مادة 5', 'المادة الخامسة' or '12 مكرر'.")


def _post_id(id: str) -> str:
    s = _http.clean(id).translate(_DIGITS)
    if s.startswith("http"):
        u = urlsplit(s)
        if (u.hostname or "").lower() != HOST:
            raise BadRequest(f"Not an {HOST} link: {id!r}.")
        m = re.search(r"(?:^|&)p=(\d+)", u.query) or re.search(r"/posts/(\d+)", u.path)
        s = m[1] if m else ""
    s = re.sub(r"^(?:post|id)\s*[:#]?\s*", "", s, flags=re.I)
    if not re.fullmatch(r"\d{1,7}", s):
        raise BadRequest(f"Bad Libya law id {id!r}: use the Ministry of Justice post id from "
                         f"search_legislation, e.g. '1246', or a {BASE}/?p=1246 link.")
    return s


def _number(title: str) -> str:
    m = _NUMBER.search(_norm(title))
    if not m:
        return ""
    return f"{m[1]}/{m[2]}" if m[2] else m[1]


def _url(pid) -> str:
    return f"{BASE}/?p={pid}"


def _reflow(text: str) -> list[str]:
    """pdf_text lines -> paragraphs: join wrapped lines; keep articles and headings on their own."""
    out: list[str] = []
    for block in text.split("\n\n"):
        for ln in block.split("\n"):
            # NFKC folds presentation forms; the PDFs' fonts emit Persian yeh/kaf for Arabic
            # ones, and parentheses come out mirrored (") 1 (").
            ln = _http.clean(unicodedata.normalize("NFKC", ln).replace("ی", "ي").replace("ک", "ك"))
            ln = re.sub(r"\)\s*([\d؀-ۿ][^()]{0,60}?)\s*\(", r"(\1)", ln)
            if not ln or re.fullmatch(r"[\d\s\-_]{1,6}", ln):
                continue
            starts = bool(_article(ln) or _heading(ln) is not None)
            if out and not starts and not re.search(r"[.:؛!?]$", out[-1]) \
                    and not _article(out[-1]) and _heading(out[-1]) is None:
                out[-1] += " " + ln
            else:
                out.append(ln)
    return out


async def _pdf_lines(url: str, src: str = SRC) -> list[str]:
    h = await _http.request("HEAD", url)
    if h.status_code == 404:
        raise NotFound(f"The linked PDF is gone: {url}")
    if h.status_code != 200:
        raise SourceError(_http.error(src, "PDF not available", h.status_code), h.status_code)
    size = int(h.headers.get("content-length") or 0)
    if not size or size > MAX_PDF:
        raise SourceError(f"Error ({src}): PDF size {'unknown' if not size else f'{size // 1_000_000} MB'}"
                          f" (cap 40 MB). Open {url}.")
    # Apache here closes idle keep-alive connections after 5 s, and a 1.5 MB PDF has taken from
    # 1.8 s to 7.7 s (2026-11-10): one retry on a network error.
    try:
        r = await _http.get(url)
    except Exception:  # network error
        r = await _http.get(url)
    if r.status_code != 200 or not r.content.startswith(b"%PDF"):
        raise SourceError(_http.error(src, "PDF download failed", r.status_code), r.status_code)
    return _reflow(_http.pdf_text(r.content))


async def _load(id: str) -> dict:
    """Post -> {id, title, url, cats, lines, format}. Cached."""
    pid = _post_id(id)
    if pid in _cache:
        return _cache[pid]
    r = await _http.get(f"{API}/{pid}", params={"_fields": "id,date,link,title,categories,content"})
    if r.status_code in (400, 404):
        raise NotFound(f"No Ministry of Justice post {pid}. Search with search_legislation first.")
    if r.status_code != 200 or "json" not in r.headers.get("content-type", ""):
        raise SourceError(_http.error(SRC, "post lookup failed", r.status_code), r.status_code)
    d = r.json()
    cats = [c for c in d.get("categories", []) if c in CAT_NAMES]
    if not cats:
        raise NotFound(f"Post {pid} is not in the ministry's legislation categories.")
    title = _http.clean(_http.html_to_md(d["title"]["rendered"])) or f"Post {pid}"
    html = d["content"]["rendered"]
    md = _http.html_to_md(html)
    plain = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", md)
    if len(_http.clean(plain)) > 400:
        lines, fmt = [ln.strip() for ln in md.split("\n") if ln.strip()], "HTML"
    else:
        pdfs = re.findall(r'href="([^"]+\.pdf)"', html, re.I)
        files = re.findall(r'href="([^"]+/wp-content/uploads/[^"]+)"', html, re.I)
        if pdfs:
            lines, fmt = await _pdf_lines(pdfs[0]), "PDF (text layer)"
            if sum(len(x) for x in lines) < 200:
                raise SourceError(f"Error ({SRC}): post {pid} is a scanned PDF without a text layer "
                                  f"(no OCR here); read it at {pdfs[0]}")
        elif files:
            raise SourceError(f"Error ({SRC}): post {pid} is only an image/file, no text; "
                              f"read it at {files[0]}")
        else:
            raise SourceError(f"Error ({SRC}): post {pid} carries no text; see {_url(pid)}")
    doc = {"id": pid, "title": title, "url": _url(pid), "cats": cats, "lines": lines,
           "format": fmt, "posted": _http.iso_date(d.get("date", "")[:10])}
    return _http.lru_put(_cache, pid, doc, 32)


def _structure(lines: list[str]):
    """-> TOC entries and {label: (start, end)} line ranges for articles."""
    entries: list[TocEntry] = []
    spans: dict[str, list[int]] = {}
    order: list[str] = []
    level = 0
    for i, ln in enumerate(lines):
        lab = _article(ln)
        if lab:
            k, base = 2, lab
            while lab in spans:
                lab = f"{base} ({k})"
                k += 1
            spans[lab] = [i, len(lines)]
            if order:
                spans[order[-1]][1] = min(spans[order[-1]][1], i)
            order.append(lab)
            title = ln if len(ln) <= 100 else ln[:100].rsplit(" ", 1)[0] + "…"
            entries.append(TocEntry(title=_http.clean(title.strip("*_ ")), level=level, provision=lab))
            continue
        h = _heading(ln)
        if h is not None:
            if order:
                spans[order[-1]][1] = min(spans[order[-1]][1], i)
            entries.append(TocEntry(title=_http.clean(ln.strip("*_ ")), level=h))
            level = h + 1
    return entries, spans


# ---- Supreme Court (alolya.gov.ly) ----

SC_HOST = "www.alolya.gov.ly"
SC = f"https://{SC_HOST}"
DASH = "dashboard.alolya.gov.ly"
SC_SRC = "Supreme Court of Libya (alolya.gov.ly)"
JOURNAL = "87611ae4-d071-4825-8259-36fb83b3382b"   # publication type uuid of مجلة المحكمة العليا
_LISTS = ("legal-principles", "constitutional-court")
CHAMBERS = {"civil": "قضاء النقض المدني", "criminal": "قضاء النقض الجنائي",
            "administrative": "قضاء النقض الإداري", "personal": "قضاء الأحوال الشخصية",
            "joint": "قضاء الدوائر مجتمعة", "constitutional": "القضاء الدستوري"}
_SECTIONS = ("first", "second", "third", "fourth", "fifth", "sixth")
_UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
_TTL = 6 * 3600
_sc: dict = {}


def _rsc(html: str) -> dict:
    """Next.js page -> {row id: payload} from its self.__next_f stream (T rows sized in bytes)."""
    chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)</script>', html, re.S)
    b = "".join(json.loads(f'"{c}"') for c in chunks).encode()
    rows, i, n = {}, 0, len(b)
    while i < n:
        c = b.find(b":", i)
        if c < 0:
            break
        rid, i = b[i:c].decode(errors="replace").strip(), c + 1
        m = re.match(rb"T([0-9a-f]+),", b[i:i + 12])
        if m:
            j = i + m.end()
            rows[rid], i = b[j:j + int(m[1], 16)].decode(errors="replace"), j + int(m[1], 16)
        else:
            e = b.find(b"\n", i)
            e = n if e < 0 else e
            rows[rid], i = b[i:e].decode(errors="replace"), e + 1
    return rows


def _objs(rows: dict, key: str):
    """Every dict carrying `key` in the JSON rows."""
    def walk(o):
        if isinstance(o, dict):
            if key in o:
                yield o
            for v in o.values():
                yield from walk(v)
        elif isinstance(o, list):
            for v in o:
                yield from walk(v)
    for v in rows.values():
        if f'"{key}"' in v and v[:1] in "[{":
            try:
                yield from walk(json.loads(v))
            except ValueError:
                continue


async def _sc_rows(path: str, params=None) -> dict:
    r = await _http.get(f"{SC}/{path}", params=params)
    if r.status_code == 404:
        raise NotFound(f"No such page on the Supreme Court site: {SC}/{path}")
    if r.status_code != 200 or "self.__next_f" not in r.text:
        raise SourceError(_http.error(SC_SRC, "page failed", r.status_code), r.status_code)
    return _rsc(r.text)


def _md(rows: dict, v) -> str:
    if isinstance(v, str) and re.fullmatch(r"\$[0-9a-f]+", v):
        v = rows.get(v[1:], "")
    return _http.html_to_md(v) if isinstance(v, str) and v.strip() else ""


def _ruling(a: dict, rows: dict) -> dict:
    """Article object -> plain dict with the text resolved (refs point at T rows)."""
    secs = []
    if isinstance(a.get("rule"), dict):
        secs.append((a["rule"].get("title") or "المبادئ القانونية", _md(rows, a["rule"].get("body_html"))))
    cc = a.get("concatenated_contents") or {}
    for k in _SECTIONS:
        if isinstance(cc, dict) and isinstance(cc.get(k), dict):
            secs.append((cc[k].get("title") or "", _md(rows, cc[k].get("body_html"))))
    for c in a.get("contents") or []:
        if isinstance(c, dict):
            secs.append((c.get("title") or "", _md(rows, c.get("body_html"))))
    num, yr = _http.clean(a.get("number")), _http.clean(a.get("judicial_year"))
    case = f"{num}/{yr}{_http.clean(a.get('sign')) or 'ق'}" if num else ""
    rtype = _http.clean(a.get("ruling_type"))
    title = " ".join(x for x in (rtype, case) if x)
    head = _http.clean(a.get("title"))
    return {"id": a["uuid"], "title": f"{title}: {head}" if title and head else (title or head),
            "court": _http.clean(f"المحكمة العليا - {a.get('author') or a.get('sub_category') or ''}"),
            "chamber": _http.clean(a.get("sub_category")), "type": rtype, "case": case,
            "date": (a.get("ruling_date") or "")[:10], "posted": (a.get("publish_date") or "")[:10],
            "brief": _http.clean(_md(rows, a.get("brief_html"))),
            "principle": _http.clean(f"{a.get('principle_number') or ''} {a.get('principle_type') or ''}"),
            "tags": [t for t in a.get("tags") or [] if isinstance(t, str)],
            "panel": [c.get("name", "") for c in a.get("counselors") or [] if isinstance(c, dict)],
            "pdf": a.get("pdf_file") or "", "sections": [(t, b) for t, b in secs if b],
            "url": f"{SC}/article/{a['uuid']}"}


async def _rulings() -> list[dict]:
    """Every ruling on the court's two list pages (all their pages). Cached."""
    hit = _sc.get("rulings")
    if hit and time.monotonic() - hit[0] < _TTL:
        return hit[1]
    out: dict = {}
    for path in _LISTS:
        page, last = 1, 1
        while page <= last:
            rows = await _sc_rows(path, {"page": page} if page > 1 else None)
            for o in _objs(rows, "articles"):
                if isinstance(o.get("totalPages"), int):
                    last = max(last, min(o["totalPages"], 20))
                for a in o["articles"] if isinstance(o["articles"], list) else []:
                    if isinstance(a, dict) and a.get("uuid") and a["uuid"] not in out:
                        out[a["uuid"]] = _ruling(a, rows)
            page += 1
    items = sorted(out.values(), key=lambda d: d["date"], reverse=True)
    _sc["rulings"] = (time.monotonic(), items)
    return items


async def _journals() -> list[dict]:
    """The journal's volumes (/technical-office, every page). Cached."""
    hit = _sc.get("journal")
    if hit and time.monotonic() - hit[0] < _TTL:
        return hit[1]
    out: dict = {}
    page, last = 1, 1
    while page <= last:
        rows = await _sc_rows("technical-office", {f"page_{JOURNAL}": page} if page > 1 else None)
        for o in _objs(rows, "pageKey"):
            if o.get("pageKey") == JOURNAL and isinstance(o.get("totalPages"), int):
                last = max(last, min(o["totalPages"], 20))
        for b in _objs(rows, "publication_type_uuid"):
            if b.get("publication_type_uuid") == JOURNAL and b.get("uuid"):
                out[b["uuid"]] = b
        page += 1
    items = sorted(out.values(), key=lambda b: (-int(b.get("judicial_year") or 0), b.get("number") or ""))
    _sc["journal"] = (time.monotonic(), items)
    return items


def _volume_title(b: dict) -> str:
    return f"مجلة المحكمة العليا - السنة {b.get('judicial_year')} - العدد {b.get('number')}"


def _volume_hit(b: dict) -> DecisionHit:
    pdf = b.get("pdf_file") if b.get("is_available") else ""
    return DecisionHit(id=f"books/{b['uuid']}", title=_volume_title(b), court="المحكمة العليا - المكتب الفني",
                       snippet="PDF " + pdf if pdf else "not online (listed as unavailable)",
                       url=f"{SC}/books/{b['uuid']}")


def _decision_id(id: str) -> tuple[str, str]:
    """-> ('article' | 'books', uuid). Accepts the uuid, 'books/<uuid>' or a site link."""
    s = _http.clean(id).lower()
    m = _UUID.search(s)
    if not m or (s.startswith("http") and (urlsplit(s).hostname or "") not in (SC_HOST, "alolya.gov.ly")):
        raise BadRequest(f"Bad Libya Supreme Court id {id!r}: use the ruling uuid from search_caselaw "
                         f"(e.g. '3b18df15-bc9c-499a-b7cb-a5f4f1f903ed'), 'books/<uuid>' for a journal "
                         f"volume, or a {SC}/article/<uuid> link.")
    return ("books" if "books/" in s else "article"), m[0]


class Libya(Jurisdiction):
    code = "ly"
    name = "Libya"
    languages = ("ar",)
    aliases = ("libya", "ليبيا", "lby")
    sources = (
        Source(
            name="وزارة العدل - Ministry of Justice of Libya (aladel.gov.ly)",
            url=BASE + "/",
            covers=("legislation",),
            licence="unknown; footer '© جميع الحقوق محفوظة وزارة العدل - ليبيا' (all rights reserved), "
                    "no terms page",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~25 requests (2026-11)",
            terms_url=BASE + "/",
            warning="Ministry of Justice selection (about 190 laws, regulations and treaties plus "
                    "ministerial decisions), as enacted, not consolidated; not the Official Gazette.",
        ),
        Source(
            name="المحكمة العليا - Supreme Court of Libya (alolya.gov.ly)",
            url=SC + "/",
            covers=("caselaw",),
            licence="unknown; footer 'جميع الحقوق محفوظة، المحكمة العليا' (all rights reserved), "
                    "no terms page",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~30 requests (2026-11)",
            terms_url=SC + "/robots.txt",
            warning="Only the rulings the court has put online (about 60, decided 2020-2026) and its "
                    "journal volumes for judicial years 37-60 (older volumes not online, many scanned); "
                    "not the full archive.",
        ),
    )
    caselaw_filters = {
        "chamber": "civil | criminal | administrative | personal | joint | constitutional (online rulings)",
        "journal_year": "judicial year 1-60, or 'all': list the court journal's volumes instead of rulings "
                        "(the query is ignored: volumes are not searched by text)",
        "date_from": "ruling date on or after YYYY-MM-DD (online rulings; also YYYY or YYYY-MM)",
        "date_to": "ruling date on or before YYYY-MM-DD (online rulings; also YYYY or YYYY-MM)",
    }
    legislation_filters = {"type": "law | regulation | decision | treaty (default: all)"}
    min_interval = {HOST: 1.0, SC_HOST: 1.0, DASH: 1.0}
    notes = ("Legislation: the Ministry of Justice's own selection of laws, executive regulations, "
             "ministerial decisions and treaties (Arabic, not consolidated). Case law: the Supreme "
             "Court's own site, every ruling it has put online (about 60, 2020-2026, full text) and "
             "its journal volumes (years 37-60 as PDFs; text only where the PDF has a text layer).")
    gaps = (
        "Supreme Court archive before 2020: journal years 1-36 not online; years 37-50 sampled as "
         "scans (no OCR); the court's principles database (/principle, 8,240+ principles) is only "
         "reachable through /api/, which robots.txt disallows",
        "Supreme Court journal volumes are whole PDFs (300-500 pages): no search inside them, "
         "two-column layout comes out interleaved",
        "Not in the MoJ selection (checked 2026-11-12): the Constitutional Declaration, the Penal "
         "Code (only amending laws and the military penal code), the Commercial Code and the "
         "commercial companies law",
        "Official Gazette and consolidated texts: not researched yet (only the MoJ's selection of"
         " ~190 acts as enacted)",
        "Parliament acts (parliament.ly): robots.txt disallows every query string and /wp- (no "
         "search)",
        "Cabinet decisions (pm.gov.ly): robots.txt disallows /images/, where the documents sit",
        "Scanned PDFs and image-only posts on aladel.gov.ly: scans only, no text",
        "Private lawsociety.ly judgment database: robots.txt blocks its search API; terms page "
         "behind a Cloudflare challenge",
    )
    samples = {"caselaw_query": "دستورية", "decision_id": "3b18df15-bc9c-499a-b7cb-a5f4f1f903ed",
               "legislation_query": "الزواج", "law_id": "1246", "provision": "1"}

    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        limit, page = max(1, min(int(limit), 50)), max(1, int(page))
        jy = _http.clean(filters.get("journal_year")).lower().translate(_DIGITS)
        if jy:
            if jy != "all" and not (jy.isdigit() and 1 <= int(jy) <= 60):
                raise BadRequest(f"journal_year must be a judicial year 1-60 or 'all', not {jy!r}.")
            vols = [b for b in await _journals() if jy == "all" or str(b.get("judicial_year")) == jy]
            return Results(items=[_volume_hit(b) for b in vols[(page - 1) * limit:page * limit]],
                           total=len(vols),
                           note="NOT a text match: journal_year lists volumes only, so the query "
                                f"{_http.clean(query)!r} is ignored (the count above is the number of "
                                "volumes, not matches); the journal cannot be searched by text. "
                                "Volumes are whole PDFs; open one with get_decision('books/<uuid>'). "
                                "Volumes marked 'not online' (years 1-36 and some later) and scanned "
                                "volumes have no text.",
                           query_ignored=True)
        ch = _http.clean(filters.get("chamber")).lower()
        if ch and ch not in CHAMBERS:
            raise BadRequest(f"Unknown chamber {ch!r}: use one of {', '.join(CHAMBERS)}.")
        terms = [_norm(t) for t in _http.clean(query).split()]
        dfrom, dto = _http.clean(filters.get("date_from")), _http.clean(filters.get("date_to"))
        hits, head_hits = [], []
        for d in await _rulings():
            if ch and d["chamber"] != CHAMBERS[ch]:
                continue
            if (dfrom and d["date"][:len(dfrom)] < dfrom) or (dto and d["date"][:len(dto)] > dto):
                continue
            hay = _norm(" ".join([d["title"], d["case"], d["brief"], " ".join(d["tags"])]
                                 + [b for _, b in d["sections"]]))
            if all(t in hay for t in terms):
                head = _norm(" ".join([d["title"], d["brief"], " ".join(d["tags"])]))
                (head_hits if all(t in head for t in terms) else hits).append(d)
        # Rulings whose title/principles contain every term come before body-text-only matches.
        body_only = len(hits)
        hits = head_hits + hits
        items = [DecisionHit(id=d["id"], title=d["title"], court=d["court"], date=d["date"],
                             case_number=d["case"], snippet=d["brief"][:300], url=d["url"])
                 for d in hits[(page - 1) * limit:page * limit]]
        note = ("Only the rulings the Supreme Court has put online (about 60, 2020-2026; employment, "
                "lease and most other topics may have none); older rulings: journal_year filter "
                "(volumes only, not searchable by text).")
        if body_only and not head_hits:
            note += (" None of these hits has the search words in its title or principles: they "
                     "appear only somewhere in the body text, so check relevance before relying.")
        return Results(items=items, total=len(hits), note=note)

    async def get_decision(self, id):
        kind, uid = _decision_id(id)
        if kind == "books":
            b = next((b for b in await _journals() if b.get("uuid") == uid), None)
            if not b:
                raise NotFound(f"No journal volume {uid}. List them with filter journal_year.")
            url = f"{SC}/books/{uid}"
            if not b.get("is_available") or not b.get("pdf_file"):
                raise NotFound(f"{_volume_title(b)} is listed but not online.")
            lines = await _pdf_lines(b["pdf_file"], SC_SRC)
            if sum(len(x) for x in lines) < 200:
                raise SourceError(f"Error ({SC_SRC}): {_volume_title(b)} is a scanned PDF without a "
                                  f"text layer (no OCR here); read it at {b['pdf_file']}")
            return Decision(id=f"books/{uid}", title=_volume_title(b), text="\n\n".join(lines), url=url,
                            court="المحكمة العليا - المكتب الفني",
                            metadata={"PDF": b["pdf_file"], "Printed": str(b.get("calendar_year") or "")})
        rows = await _sc_rows(f"article/{uid}")
        a = next((o for o in _objs(rows, "concatenated_contents") if o.get("uuid") == uid), None)
        if not a:
            raise NotFound(f"No Supreme Court ruling {uid}. Search with search_caselaw first.")
        d = _ruling(a, rows)
        meta = {"Chamber": d["chamber"], "Ruling type": d["type"], "Principle": d["principle"],
                "Panel": "، ".join(x for x in d["panel"] if x), "Tags": "، ".join(d["tags"]),
                "Posted on site": d["posted"], "PDF": d["pdf"]}
        return Decision(id=uid, title=d["title"], url=d["url"], court=d["court"], date=d["date"],
                        case_number=d["case"], summary=d["brief"],
                        text="\n\n".join(f"## {t}\n\n{b}" if t else b for t, b in d["sections"]),
                        metadata={k: v for k, v in meta.items() if v})

    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        t = (filters.get("type") or "").strip().lower()
        if t and t not in TYPES:
            raise BadRequest(f"Unknown type {t!r}: use one of {', '.join(TYPES)}.")
        cats = TYPES[t] if t else ALL_CATS
        limit, page = max(1, min(int(limit), 50)), max(1, int(page))
        q = _http.clean(query)
        # With a query, read every match (the selection is ~190 acts) so acts whose TITLE has all
        # the words can come first: the source ranks acts that merely cite a law above the law.
        params = {"categories": ",".join(map(str, cats)), "per_page": 100 if q else limit,
                  "page": 1 if q else page, "_fields": "id,link,title,categories,excerpt"}
        if q:
            params["search"] = q
        rows, pages = [], 1
        while True:
            r = await _http.get(API, params=params)
            if r.status_code == 400 and "invalid_page_number" in r.text:
                return Results(items=[], total=None, note="Page past the last result.")
            if r.status_code != 200 or "json" not in r.headers.get("content-type", ""):
                raise SourceError(_http.error(SRC, "search failed", r.status_code), r.status_code)
            rows += r.json()
            pages = int(r.headers.get("x-wp-totalpages", "1") or 1) if q else 1
            if params["page"] >= pages or params["page"] >= 10:
                break
            params["page"] += 1
        if q:
            terms = [_norm(t) for t in q.split()]

            def in_title(d):
                t = _norm(_http.clean(_http.html_to_md(d["title"]["rendered"])))
                return not all(x in t for x in terms)
            rows.sort(key=in_title)
            r_total = len(rows) if pages <= 10 else None
            rows = rows[(page - 1) * limit:page * limit]
        items = []
        for d in rows:
            title = _http.clean(_http.html_to_md(d["title"]["rendered"])) or f"Post {d['id']}"
            cat = next((CAT_NAMES[c] for c in d.get("categories", []) if c in CAT_NAMES), "")
            snip = _http.clean(re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1",
                                      _http.html_to_md(d.get("excerpt", {}).get("rendered", ""))))
            items.append(LawHit(id=str(d["id"]), title=title, type=cat, number=_number(title),
                                snippet=snip[:300], url=_url(d["id"])))
        total = r_total if q else r.headers.get("x-wp-total")
        return Results(items=items, total=int(total) if total and str(total).isdigit() else None,
                       note="Ministry of Justice selection, texts as enacted (not consolidated); "
                            "dates are not given by the source. Not in this selection: the "
                            "Constitutional Declaration, the Penal Code, the Commercial Code and the "
                            "commercial companies law (hits for those words are other acts that "
                            "mention them). The Code of Civil and Commercial Procedure is only inside the "
                            "'موسوعة القوانين القضائية' compilation.")

    async def get_legislation_toc(self, id):
        doc = await _load(id)
        entries, _ = _structure(doc["lines"])
        if not any(e.provision for e in entries):
            entries.append(TocEntry(title=doc["title"], level=0, provision="full"))
        return Toc(id=doc["id"], title=doc["title"], url=doc["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        doc = await _load(id)
        _, spans = _structure(doc["lines"])
        if not spans and _http.clean(provision).lower() in ("full", "text", "all"):
            return Provision(law_id=doc["id"], law_title=doc["title"], provision="full",
                             text="\n\n".join(doc["lines"]), url=doc["url"])
        label = _label(provision)
        if label not in spans:
            raise NotFound(f"No article {label!r} in post {doc['id']} ({doc['title']}). "
                           f"See get_legislation_toc for the labels.")
        a, b = spans[label]
        return Provision(law_id=doc["id"], law_title=doc["title"], provision=label,
                         text="\n\n".join(doc["lines"][a:b]), url=doc["url"])

    async def get_legislation_text(self, id):
        doc = await _load(id)
        return LawText(id=doc["id"], title=doc["title"], text="\n\n".join(doc["lines"]), url=doc["url"],
                       metadata={"Category": ", ".join(CAT_NAMES[c] for c in doc["cats"]),
                                 "Format": doc["format"], "Posted on site": doc["posted"]})
