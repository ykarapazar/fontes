"""Afghanistan: legislation from the Ministry of Justice "laws and orders database"
(laws.moj.gov.af, "مجموعه قوانین افغانستان"), run by the Ministry of Justice of the current de facto
administration (Islamic Emirate). Linked from moj.gov.af ("د افغانستان د قوانینو او حکمونو دیتابیس").

How the source works (verified 2026-11-06, UK IP, honest User-Agent):
  * An ASP.NET WebForms site, plain HTTP only (https:// times out). ShowLawPersian.aspx (Dari titles)
    and ShowLawPashto.aspx (Pashto titles) each hold one search box and a grid of 10 rows:
    record no. (شماره), title, publication date, Official Gazette serial no. (شماره مسلسل),
    status (نافذ in force / ملغی repealed), notes, and a download button. About 4,800 instruments,
    Gazette No. 1 (1964) to the 1470s (2025).
  * Search is a form postback; it matches the title and the Gazette serial number (in Persian digits).
    Pages are reached only by "next page" postbacks (Page$N directly gives HTTP 500).
  * Download is a postback on a grid row; it returns the Official Gazette PDF (OG_01452.pdf) or a
    part of it (OG_0353-1.pdf), as published, bilingual Pashto + Dari, not consolidated.
  * id = "<Gazette serial>-<record no.>", both the database's own numbers: "1452-16577" is record
    16577 (the Law on the Promotion of Virtue and Prevention of Vice) in Official Gazette No. 1452.
    A bare Gazette number ("1452") opens the first record in that issue.
  * PDF text quality: issues since about 2021 have a usable text layer (two columns, Pashto and Dari,
    extracted interleaved). Many 2000s-2010s issues use legacy Arabic fonts whose text layer is
    gibberish, and older issues are scans; for those the adapter says so and gives the link.

Terms: no terms-of-use page on laws.moj.gov.af or moj.gov.af (footer: "Copyright © 2019 | MOJ.
All Rights Reserved"). Nothing on automated access. robots.txt: laws.moj.gov.af has none (HTTP 404);
moj.gov.af has the Drupal default (disallows /admin/, /search/, /user/* etc.), no Crawl-delay, no
AI rules (2026-11-06).

Not used: supremecourt.gov.af (Drupal default robots.txt). Its "فیصله های قطعی محاکم" (final court
decisions) and bulletin pages are empty (2026-11-06), so there is no case-law source.
"""
from __future__ import annotations

import datetime
import re

from lxml import html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import LawHit, LawText, Provision, Results, Toc, TocEntry

HOST = "laws.moj.gov.af"
BASE = f"http://{HOST}"
PAGES = {"fa": BASE + "/ShowLawPersian.aspx", "ps": BASE + "/ShowLawPashto.aspx"}
SOURCE = "Ministry of Justice laws database (de facto authority)"
MAX_BYTES = 40 * 1024 * 1024
MAX_SOURCE_PAGES = 5            # 10 rows each; deeper pages need one postback per page
_GRID = "ctl00$ContentPlaceHolder1$gvShowLaw"
_BOX = "ctl00$ContentPlaceHolder1$txtSearch"
_BTN = "ctl00$ContentPlaceHolder1$Serach"

_FA_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
_TO_FA = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
_ID = re.compile(r"^(?:OG)?[\s_-]*0*(\d{1,5})(?:\s*[-/:]\s*(\d{1,7}))?$", re.I)
_STATUS = {"نافذ": "in force", "ملغی": "repealed", "ملغى": "repealed"}

_doc_cache: dict = {}


# --------------------------------------------------------------------------- #
# Listing / search (form postbacks)
# --------------------------------------------------------------------------- #
def _latin(s: str) -> str:
    return _http.clean(s).translate(_FA_DIGITS).replace("‫", "").replace("‬", "")


def _form(doc) -> dict:
    return {i.get("name"): i.get("value") or "" for i in doc.xpath("//input[@type='hidden'][@name]")}


def _rows(doc) -> list[dict]:
    out = []
    for tr in doc.xpath(f"//table[@id='ContentPlaceHolder1_gvShowLaw']/tr[count(td)=7]"):
        td = [_http.clean(t.text_content()).replace("‫", "") for t in tr.xpath("td")]
        btn = tr.xpath(".//input[@type='image']/@name")
        rec, serial = _latin(td[0]), _latin(td[3])
        if not (rec.isdigit() and serial.isdigit() and btn):
            continue
        out.append({"rec": rec, "title": td[1], "date": td[2], "serial": serial,
                    "status": td[4], "notes": td[5], "btn": btn[0]})
    return out


def _has_next(doc) -> bool:
    return bool(doc.xpath("//tr[@class='GridPager']//a[contains(@href,'Page$Next')]"))


async def _post(url: str, data: dict):
    r = await _http.post(url, data=data)
    if r.status_code != 200:
        raise SourceError(_http.error(SOURCE, "search postback failed", r.status_code), r.status_code)
    return r


async def _search_pages(query: str, lang: str, pages: int):
    n = 0
    async for item in _search(query, lang):
        yield item
        n += 1
        if n >= pages:
            return


async def _search(query: str, lang: str):
    """Yield (rows, doc, url) for each result page, following 'next' postbacks."""
    url = PAGES[lang]
    r = await _http.get(url)
    if r.status_code != 200:
        raise SourceError(_http.error(SOURCE, "database page failed", r.status_code), r.status_code)
    doc = lhtml.fromstring(r.text)
    if not doc.xpath(f"//input[@name='{_BOX}']"):
        raise SourceError(f"Error ({SOURCE}): database page changed (no search box).", 200)
    data = _form(doc) | {_BOX: query, _BTN: "   جستجو   "}
    doc = lhtml.fromstring((await _post(url, data)).text)
    for n in range(MAX_SOURCE_PAGES):
        yield _rows(doc), doc, url
        if n + 1 == MAX_SOURCE_PAGES or not _has_next(doc):
            return
        data = _form(doc) | {_BOX: query, "__EVENTTARGET": _GRID, "__EVENTARGUMENT": "Page$Next"}
        doc = lhtml.fromstring((await _post(url, data)).text)


# --------------------------------------------------------------------------- #
# Dates
# --------------------------------------------------------------------------- #
def _jalali_to_iso(y: int, m: int, d: int) -> str:
    """Solar Hijri -> Gregorian (Borkowski/jdf arithmetic)."""
    try:
        jy = y - 979
        days = 365 * jy + (jy // 33) * 8 + ((jy % 33) + 3) // 4 + 79 + (d - 1)
        days += (m - 1) * 31 if m < 7 else (m - 7) * 30 + 186
        g = datetime.date(1600, 1, 1) + datetime.timedelta(days=days)
        return g.isoformat() if 1 <= m <= 12 and 1 <= d <= 31 else ""
    except (ValueError, OverflowError):
        return ""


def _date(s: str) -> str:
    """'۱۴۰۳/۵/۱۰' (Solar Hijri) -> ISO. Lunar Hijri dates (year 1410+) and bare years -> ''."""
    m = re.search(r"(\d{4})/(\d{1,2})/(\d{1,2})", _latin(s))
    if not m or not 1300 <= int(m[1]) < 1410:
        return ""
    return _jalali_to_iso(int(m[1]), int(m[2]), int(m[3]))


def _type(title: str) -> str:
    m = re.match(r"^\(?\s*(قانون|فرمان|حکم|حكم|مقرره|طرزالعمل|لایحه|اصولنامه|کود|ضمیمه|موافقتنامه|"
                 r"اساسنامه|مصوبه|تعدیل|ایزاد|فیصله|اعلامیه)", title)
    return m[1] if m else ""


def _variants(w: str) -> list[str]:
    """Other common forms of one Persian word (plural/ezafe endings) to retry when an exact match fails."""
    if w.endswith("ی"):
        return [w[:-1] + "ان", w[:-1]]
    if w.endswith("ان") or w.endswith("ها"):
        return [w[:-2], w[:-2] + "ی"]
    return []


def _hit(row: dict, url: str) -> LawHit:
    when = row["date"].strip()
    snippet = f"Official Gazette No. {row['serial']}, published {when}" + (f"; {row['notes']}" if row["notes"] else "")
    if row["serial"].isdigit() and int(row["serial"]) < 1410:
        snippet += ("; full text usually unreadable (legacy fonts or scan): open the PDF at the source link; "
                    "text and Contents calls will usually fail for this Gazette")
    if not snippet.endswith("fail for this Gazette"):
        snippet += ("; no Contents offered: article headings are often garbled in the PDF text layer, so "
                    "get_legislation_toc and get_legislation_provision may fail; get_legislation_text always returns the text")
    return LawHit(id=f"{row['serial']}-{row['rec']}", title=row["title"], type=_type(row["title"]),
                  number=row["serial"], date=_date(when), status=_STATUS.get(row["status"], row["status"]),
                  snippet=snippet, url=url, has_toc=False)


# --------------------------------------------------------------------------- #
# PDF download and parsing
# --------------------------------------------------------------------------- #
def _norm_id(raw: str) -> tuple[str, str]:
    m = _ID.match(_latin(raw))
    if not m:
        raise BadRequest("Afghan ids look like '1452-16577' (Official Gazette no. - database record no.) "
                         "or just '1452' (Gazette no.); find them with search_legislation.")
    return m[1], m[2] or ""


async def _download(url: str, data: dict) -> bytes:
    """Download postback, refusing anything over 40 MB (checked on Content-Length before reading)."""
    await _http._throttle(url)
    s = _http.stats.setdefault(HOST, {"requests": 0, "limited": 0, "max_wait": 0.0})
    s["requests"] += 1
    async with _http.get_client().stream("POST", url, data=data) as r:
        if r.status_code != 200:
            raise SourceError(_http.error(SOURCE, "PDF download failed", r.status_code), r.status_code)
        size = r.headers.get("content-length")
        if size and int(size) > MAX_BYTES:
            raise SourceError(f"Error ({SOURCE}): PDF is {int(size) // 2**20} MB, over the 40 MB cap. "
                              f"Download it from {url}", 413)
        buf = bytearray()
        async for chunk in r.aiter_bytes():
            buf += chunk
            if len(buf) > MAX_BYTES:
                raise SourceError(f"Error ({SOURCE}): PDF is over the 40 MB cap. Download it from {url}", 413)
    if not bytes(buf[:5]).startswith(b"%PDF"):
        raise SourceError(f"Error ({SOURCE}): download did not return a PDF.", 200)
    return bytes(buf)


_GLYPHS = re.compile(r"/[a-z]+(?:isolated|initial|medial|final|digit\w*)")


def _readable(text: str) -> bool:
    """Legacy-font PDFs extract as a letter-substitution cipher ("هادۀ" for "مادۀ") or as glyph names;
    a real text layer says "ماده"/"قانون" now and then."""
    if not text or len(_GLYPHS.findall(text)) > 20:
        return False
    words = len(text.split())
    return text.count("ماد") + text.count("قانون") >= max(3, words / 1000)


_GARBLED_HEAD = re.compile(r"^\s*هاد[ۀةٍه]\s", re.M)


async def _doc(raw_id: str) -> dict:
    serial, rec = _norm_id(raw_id)
    key = f"{serial}-{rec}"
    if key in _doc_cache:
        return _doc_cache[key]
    row = None
    async for rows, doc, url in _search(serial.translate(_TO_FA), "fa"):
        row = next((x for x in rows if x["serial"] == serial and (not rec or x["rec"] == rec)), None)
        if row:
            break
    if not row:
        raise NotFound(f"No record {key.rstrip('-')} in the Ministry of Justice database; "
                       "use search_legislation to find ids.")
    form = _form(doc) | {_BOX: serial.translate(_TO_FA), row["btn"] + ".x": "8", row["btn"] + ".y": "8"}
    pdf = await _download(url, form)
    try:
        text = _http.pdf_text(pdf)
    except Exception:
        raise SourceError(f"Error ({SOURCE}): Gazette No. {row['serial']} is a damaged or unreadable PDF. "
                          f"Download it at {url} (search '{row['serial']}').", 200) from None
    out = {"row": row, "id": f"{row['serial']}-{row['rec']}", "url": url, "text": text,
           "readable": _readable(text), "scan": not text}
    _http.lru_put(_doc_cache, key, out, 6)
    _http.lru_put(_doc_cache, out["id"], out, 6)
    return out


def _require_text(d: dict) -> None:
    if d["scan"]:
        raise SourceError(f"Error ({SOURCE}): Gazette No. {d['row']['serial']} is a scan with no text "
                          f"layer. Download it at {d['url']} (search '{d['row']['serial']}').", 200)
    if not d["readable"]:
        raise SourceError(f"Error ({SOURCE}): Gazette No. {d['row']['serial']} uses legacy fonts; its "
                          f"text layer is unreadable. Download it at {d['url']} (search "
                          f"'{d['row']['serial']}').", 200)


# Dari ordinal numbers ("مادۀ بیست و سوم") -> int.
_UNITS = {"یک": 1, "دو": 2, "سه": 3, "چهار": 4, "پنج": 5, "شش": 6, "هفت": 7, "هشت": 8, "نه": 9}
_TEENS = {"ده": 10, "یازده": 11, "دوازده": 12, "سیزده": 13, "چهارده": 14, "پانزده": 15, "شانزده": 16,
          "هفده": 17, "هجده": 18, "هژده": 18, "نزده": 19}
_TENS = {"بیست": 20, "سی": 30, "چهل": 40, "پنجاه": 50, "شصت": 60, "هفتاد": 70, "هشتاد": 80, "نود": 90}
_HUNDREDS = {"صد": 100, "یکصد": 100, "دوصد": 200, "دویست": 200, "سهصد": 300, "سیصد": 300, "چهارصد": 400,
             "پانصد": 500, "ششصد": 600, "هفتصد": 700, "هشتصد": 800, "نهصد": 900}
_CARD = _UNITS | _TEENS | _TENS | _HUNDREDS
_ORD_SPECIAL = {"اول": 1, "یکم": 1, "سوم": 3, "سیم": 30, "سیام": 30}


def _fa_norm(s: str) -> str:
    return (s.replace("ي", "ی").replace("ى", "ی").replace("ك", "ک").replace("ۀ", "ه").replace("ة", "ه")
            .replace("‌", "").replace("ٔ", ""))


def _skel(s: str) -> str:
    """Spelling-tolerant form for matching titles: no tatweel, no alif, unified yeh/kaf/heh."""
    return _fa_norm(s).replace("ـ", "").replace("ا", "")


def _ord_word(p: str, last: bool) -> int | None:
    if not last:
        return _CARD.get(p)
    if p in _ORD_SPECIAL:
        return _ORD_SPECIAL[p]
    for suffix in ("ام", "م"):
        if p.endswith(suffix) and p[:-len(suffix)] in _CARD:
            return _CARD[p[:-len(suffix)]]
    return None


def _ordinal(s: str) -> int | None:
    """'بیست و سوم' -> 23. Tolerates the PDF font quirks seen in the Gazette: final 'م' extracted
    as 'ا' ('پنجا') and a dropped 'چ' ('هارم' for 'چهارم')."""
    s = _latin(s)
    if s.isdigit():
        return int(s)
    parts = [p.replace(" ", "") for p in re.split(r"\s+و\s*", _fa_norm(s).strip())]
    if not parts or not all(parts):
        return None
    total = 0
    for i, p in enumerate(parts):
        last = i == len(parts) - 1
        variants = [p, "چ" + p] + ([p[:-1] + "م", "چ" + p[:-1] + "م"] if last and p.endswith("ا") else [])
        n = next((v for v in (_ord_word(x, last) for x in variants) if v), None)
        if n is None:
            return None
        total += n
    return total or None


_DARI_HEAD = re.compile(r"^:?\s*(?:مادۀ|ماده|مادهٔ|مادة)\s+([^:]{1,40}?)\s*:\s*(.*)$")
_PASHTO_HEAD = re.compile(r"^:?\s*\S+(?:\s+\S+)?\s+ماده\s*:?\s*$")
_JUNK = re.compile(r"^(\(\s*[\d/\s-]+\)|رسمي جريده|رسمی جریده|رسمي جرېده|\d{1,3}|پرله ?\S* ?نمبر.*|.*\.{5,}.*)$")
_FOOTNOTE = re.compile(r"^\(\s*\d+\s*\)\s*-|^-\s")
_MARK_END = re.compile(r"\(\s*[\d۰-۹]+\s*\)\.?$")
_SECTION = re.compile(r"^(?:فصل|باب|بخش|مقدمه|څپرکی)\b")


def _parse(text: str) -> dict:
    """Split the Dari side into articles. Each run restarting at 1 is a new instrument (block)."""
    lines = [ln for ln in text.split("\n") if ln and not _JUNK.match(ln)]
    heads = []   # (line index, n, rest)
    last = 0
    for i, ln in enumerate(lines):
        m = _DARI_HEAD.match(ln)
        if not m:
            continue
        n = _ordinal(m[1])
        if n is None or not (n == 1 or last < n <= last + 5):
            continue
        heads.append((i, n, m[2]))
        last = n
    blocks: list[list[tuple[int, int, str]]] = []
    for h in heads:
        if h[1] == 1 or not blocks:
            blocks.append([])
        blocks[-1].append(h)
    main = max(range(len(blocks)), key=lambda k: len(blocks[k])) if blocks else -1
    provs: dict[str, str] = {}
    entries: list[TocEntry] = []
    order: list[tuple[int, str]] = []
    for k, block in enumerate(blocks):
        if len(blocks) > 1:
            entries.append(TocEntry(title="متن اصلی" if k == main else f"سند {k + 1}", level=0))
        for i, n, rest in block:
            j = i + 1
            while j < len(lines) and not (_DARI_HEAD.match(lines[j]) or _PASHTO_HEAD.match(lines[j])
                                          or _FOOTNOTE.match(lines[j]) or _SECTION.match(lines[j])
                                          or (_MARK_END.search(lines[j - 1]) and lines[j][:1] in "(-")):
                j += 1
            label = f"ماده {n}" if k == main else f"ماده {n} [{k + 1}]"
            body = " ".join(([rest] if rest else []) + lines[i + 1:j])
            provs[label] = f"**{_http.clean(lines[i])}**\n\n{_http.clean(body)}".strip()
            order.append((n, label))
            entries.append(TocEntry(title=_http.clean(lines[i])[:120], level=1, provision=label))
    return {"provs": provs, "entries": entries, "order": order}


def _label(p: str, parsed: dict) -> str:
    s = _http.clean(p)
    if s in parsed["provs"]:
        return s
    block = re.search(r"\[(\d+)\]", s)
    core = re.sub(r"\[\d+\]", "", s)
    core = re.sub(r"^(?:art(?:icle)?\.?|مادۀ|ماده|مادهٔ|madde)\s*", "", core.strip(), flags=re.I).strip(" :")
    n = _ordinal(core)
    if n is None:
        raise BadRequest("Give an article number, e.g. 'ماده 5', 'مادۀ پنجم', 'art. 5' or '5' "
                         "(add '[2]' for the second instrument in the PDF, as the TOC shows).")
    want = f"ماده {n}" + (f" [{block[1]}]" if block else "")
    if want in parsed["provs"]:
        return want
    raise NotFound(f"No article {n} found in the Dari text of this PDF (headings may be garbled); read get_legislation_text, or the PDF at the source link.")


_NO_ARTICLES = ("No readable article headings in Gazette PDF {id}: its text layer is partly garbled "
                "(legacy-font letter substitution, e.g. 'هادۀ' for 'مادۀ'), so articles cannot be split. "
                "Use get_legislation_text for the extracted text as is (it cannot be quoted reliably); "
                "read and quote articles from the original PDF at the source link.")


class Afghanistan(Jurisdiction):
    code = "af"
    name = "Afghanistan"
    languages = ("fa", "ps")
    aliases = ("afghanistan", "afg", "افغانستان")
    sources = (
        Source(
            name=SOURCE,
            url=BASE + "/",
            covers=("legislation",),
            licence="unknown; no terms or licence page, footer 'Copyright © 2019 | MOJ. All Rights Reserved'",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 2 s spacing, no 429 seen in ~30 requests (2026-11)",
            terms_url="https://moj.gov.af/",
            warning=("Site of the Ministry of Justice of the current de facto administration (Islamic "
                     "Emirate); texts and in-force status reflect that administration. PDFs as published "
                     "in the Official Gazette, not consolidated; text extracted from PDF, check the original."),
        ),
    )
    legislation_filters = {
        "language": "'fa' (Dari titles, default) or 'ps' (Pashto titles)",
    }
    min_interval = {HOST: 2.0}
    notes = ("Legislation only: Ministry of Justice database of ~4,800 instruments from the Official Gazette "
             "(1964-2025), searchable by title or Gazette number; full text only where the PDF has a "
             "readable text layer (mostly 2021 onwards). No case-law source.")
    gaps = (
        ("Case law: Supreme Court 'final court decisions' and bulletin pages are empty (not "
         "published online, 2026-11-06)"),
        ("Full text of most pre-2021 Gazette issues: legacy-font PDFs with gibberish text or scans"
         " only, no text (link given)"),
        ("Consolidated texts: the MoJ database has Gazette PDFs as published only; other sources "
         "not researched yet"),
    )
    samples = {
        "legislation_query": "امر بالمعروف",
        "law_id": "1452-16577",
        "provision": "ماده 1",
    }

    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        q = _http.clean(query)
        if not q:
            raise BadRequest("Give words from the title (Dari or Pashto), e.g. 'قانون اساسی', "
                             "or an Official Gazette number, e.g. '1452'.")
        if _latin(q).isdigit():
            q = _latin(q).translate(_TO_FA)       # the database stores Gazette numbers in Persian digits
        lang = (filters or {}).get("language", "fa")
        if lang not in PAGES:
            raise BadRequest("language filter must be 'fa' (Dari) or 'ps' (Pashto).")
        start = (page - 1) * limit
        if start + limit > MAX_SOURCE_PAGES * 10:
            raise BadRequest(f"Only the first {MAX_SOURCE_PAGES * 10} hits can be paged through; refine the query.")
        hits: list[LawHit] = []
        more = False
        q_note = ""
        async for rows, doc, url in _search(q, lang):
            hits += [_hit(r, url) for r in rows]
            more = _has_next(doc)
        if not hits and len(q.split()) == 1:
            # The source matches title words exactly: 'صرافی' (exchange house) misses 'صرافان' (exchangers).
            for alt in _variants(q):
                async for rows, doc, url in _search(alt, lang):
                    hits += [_hit(r, url) for r in rows]
                    more = _has_next(doc)
                if hits:
                    q_note = f" No title has '{q}'; showing matches for the related form '{alt}'."
                    break
        words = q.split()
        if len(words) > 1:
            # The source matches the whole query as one exact phrase, and titles spell words variably
            # (tatweel "مـتحده", "امارت" for "امارات"). Also search each word and keep titles that contain
            # every word in normalised form; phrase hits stay first.
            seen = {h.id for h in hits}
            want = [_skel(w) for w in words]
            for key in dict.fromkeys(words[:4]):
                for n, (rows, doc, url) in enumerate([x async for x in _search_pages(key, lang, 2)]):
                    for r in rows:
                        h = _hit(r, url)
                        if h.id not in seen and all(w in _skel(r["title"]) for w in want):
                            seen.add(h.id)
                            hits.append(h)
                    more = more or (n == 1 and _has_next(doc))
        total = len(hits) if not more else None
        return Results(items=hits[start:start + limit], total=total,
                       note=(f"More than {MAX_SOURCE_PAGES * 10} hits; only the first {MAX_SOURCE_PAGES * 10} can be paged. "
                             if more else "") + q_note + "The source matches the query as one exact phrase (words in that order); "
                            "if nothing matches, words are matched anywhere in the title. "
                            "Searches titles and Gazette numbers by exact word form (no stemming: 'صرافی' misses 'صرافان'; try other forms); ids are '<Gazette no.>-<record no.>'. "
                            "Full text exists mostly for Gazettes from 2021 on; older hits give the PDF link only. "
                            "Dates: Solar Hijri converted; Lunar Hijri dates left blank (see snippet).")

    async def get_legislation_toc(self, id):
        d = await _doc(id)
        _require_text(d)
        p = _parse(d["text"])
        if not p["entries"]:
            raise NotFound(_NO_ARTICLES.format(id=d["id"]))
        return Toc(id=d["id"], title=d["row"]["title"], url=d["url"], entries=p["entries"])

    async def get_legislation_provision(self, id, provision):
        d = await _doc(id)
        _require_text(d)
        p = _parse(d["text"])
        if not p["provs"]:
            raise NotFound(_NO_ARTICLES.format(id=d["id"]))
        label = _label(provision, p)
        return Provision(law_id=d["id"], law_title=d["row"]["title"], provision=label,
                         text=p["provs"][label], url=d["url"], as_of=_date(d["row"]["date"]))

    async def get_legislation_text(self, id):
        d = await _doc(id)
        _require_text(d)
        row = d["row"]
        meta = {"Official Gazette No.": row["serial"], "Record no.": row["rec"],
                "Published": row["date"].strip(), "Status": _STATUS.get(row["status"], row["status"])}
        if row["notes"]:
            meta["Notes"] = row["notes"]
        if _GARBLED_HEAD.search(d["text"]):
            meta["Warning"] = ("The PDF's text layer is partly garbled (letters substituted, e.g. 'هادۀ' for "
                               "'مادۀ', titles and numbers corrupted). Do not quote this text; read the "
                               f"original PDF at {d['url']} (search '{row['serial']}').")
        return LawText(id=d["id"], title=row["title"], text=d["text"].replace("\n\n", "\n\n---\n\n"),
                       url=d["url"], as_of=_date(row["date"]), metadata=meta)
