"""UN Treaty Collection (treaties.un.org): the multilateral treaties deposited with the UN
Secretary-General (MTDSG), as legislation. No case law. No API; plain HTML/XML/PDF.

Gotchas this code encodes:
  * Ids are MTDSG numbers: chapter in Roman numerals, optional subchapter letter, number,
    optional lower-case suffix: "IV-4" (ICCPR), "XXI-6" (UNCLOS), "XXI-6-a", "XI-B-19",
    "XXVII-7-d" (Paris Agreement). They are the site's own `mtdsg_no`.
  * Search: the site's search is a multi-step ASP.NET postback form, so we use the chapter
    listings instead: `Pages/Treaties.aspx?id={1..29}&subid=A&clang=_en` (+ subchapters
    B..E linked from the page, e.g. chapter XI). Rows carry hidden cells with the title and
    mtdsg_no. All ~35 pages are fetched on the first unfiltered search (robots.txt asks for
    Crawl-delay 2, so ~70 s) and kept in memory for a day; the `chapter` filter or an
    MTDSG-number query fetches just one chapter.
  * Status record: `/doc/Publication/MTDSG/Volume {I|II}/Chapter {roman}/{id}.en.xml`, the
    XML behind the status page (Volume I = chapters I-XI, Volume II = XII-XXIX; checked
    2026-11). Unknown ids answer 302 to an error page. Text fields hold escaped HTML with
    the site's own tags (<superscript>, <right>, <center>).
  * Treaty text: certified true copies (CTC) as PDF. The XML sometimes links per-language
    CTCs ("CTC-English"); otherwise the status page (`Pages/ViewDetails.aspx`, 0.2-3 MB;
    templates other than "mtdsg" 302 to ViewDetailsIII.aspx etc., with the full page in
    the 302 body) links one CTC PDF (`hypCTC`), often all six languages in one scan. The
    PDFs carry the UN's own OCR text layer (imperfect: "Us» of terme"); we don't OCR.
    Bigger than _MAX_PDF bytes, or no usable text layer: the status record is returned as
    the text instead, and the response says so.
  * Provisions: status sections ("status", "declarations", "objections", ...) from the XML,
    plus "Article N" / "Annex II Article N" cut from the PDF text at exact heading lines.
    In multilingual PDFs English comes before French, so the first occurrence of a label
    is the English one.
"""
from __future__ import annotations

import html as _html
import re
import time
from urllib.parse import quote, urljoin

from lxml import etree
from lxml import html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import LawHit, LawText, Provision, Results, Toc, TocEntry

HOST = "treaties.un.org"
BASE = f"https://{HOST}"
_TTL = 24 * 3600
_MAX_PDF = 40_000_000
_ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV",
          "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI", "XXII", "XXIII", "XXIV", "XXV",
          "XXVI", "XXVII", "XXVIII", "XXIX"]
_MONTHS = {m: i for i, m in enumerate(("january", "february", "march", "april", "may", "june",
                                        "july", "august", "september", "october", "november",
                                        "december"), 1)}
_ID = re.compile(r"^([IVXL]+)(?:-([A-E]))?-(\d+)((?:-[a-z]{1,2})*)$")

_chapters: dict = {}     # chapter no -> (time, [row dicts])
_status: dict = {}       # id -> parsed XML record (LRU)
_texts: dict = {}        # id -> (pdf url, text) or (note, "") (LRU)

# Status sections: provision label -> (XML element, TOC title)
_SECTIONS = (
    ("status", "Header", "Status: entry into force, registration, participants"),
    ("declarations", "Declarations", "Declarations and reservations"),
    ("objections", "Objections", "Objections"),
    ("article-declarations", "DeclarationsUnderArticle", "Declarations under specific articles"),
    ("notifications", "Notifications", "Notifications"),
    ("territorial", "TerritorialApplications", "Territorial application"),
    ("tables", "SpecialTables", "Special tables"),
    ("notes", "EndNotes", "End notes"),
)
_ALIASES = {"parties": "status", "participants": "status", "signatures": "status",
            "ratifications": "status", "reservations": "declarations",
            "declarations and reservations": "declarations", "reservations and declarations":
            "declarations", "endnotes": "notes", "footnotes": "notes",
            "territorial application": "territorial", "special tables": "tables"}


# --------------------------------------------------------------------------- #
# Ids and small parsers
# --------------------------------------------------------------------------- #
def _norm_id(raw: str) -> str:
    s = _http.clean(raw)
    m = re.search(r"mtdsg_no=([^&\s]+)", s)
    if m:
        s = m[1]
    s = re.sub(r"(?i)^(?:mtdsg|untc)\s*(?:no\.?)?\s*", "", s).strip(" .")
    parts = [p for p in re.split(r"[\s\-./]+", s) if p]
    if len(parts) < 2:
        raise BadRequest(_bad_id(raw))
    out = [parts[0].upper()]
    rest = parts[1:]
    if rest and re.fullmatch(r"[A-Ea-e]", rest[0]) and len(rest) > 1 and rest[1].isdigit():
        out.append(rest.pop(0).upper())
    out += [p.lower() for p in rest]
    ident = "-".join(out)
    m = _ID.match(ident)
    if not m or m[1] not in _ROMAN:
        raise BadRequest(_bad_id(raw))
    return ident


def _bad_id(raw: str) -> str:
    return (f"{raw!r} is not an MTDSG treaty number. Use the number search_legislation shows, "
            "e.g. IV-4 (ICCPR), XXI-6 (UNCLOS), XI-B-19, XXVII-7-d.")


def _chapter_of(ident: str) -> int:
    return _ROMAN.index(ident.split("-")[0]) + 1


def _status_url(ident: str) -> str:
    return (f"{BASE}/Pages/ViewDetails.aspx?src=TREATY&mtdsg_no={ident}"
            f"&chapter={_chapter_of(ident)}&clang=_en")


def _xml_url(ident: str) -> str:
    vol = "I" if _chapter_of(ident) <= 11 else "II"
    return (f"{BASE}/doc/Publication/MTDSG/Volume%20{vol}/Chapter%20{ident.split('-')[0]}/"
            f"{quote(ident)}.en.xml")


def _dmy(s: str) -> str:
    """Last '10 December 1982' in s -> '1982-12-10'."""
    found = re.findall(r"\b(\d{1,2})\s+(" + "|".join(_MONTHS) + r")\s+(\d{4})\b", s or "", re.I)
    if not found:
        return ""
    d, mo, y = found[-1]
    return f"{y}-{_MONTHS[mo.lower()]:02d}-{int(d):02d}"


def _md(fragment: str) -> str:
    """The XML's escaped-HTML text (with the site's own tags) -> markdown."""
    s = fragment or ""
    s = re.sub(r"(?is)<superscript>\s*([^<]*?)\s*</superscript>", r" [\1]", s)
    s = re.sub(r"(?is)</?(right|center|left)>", " ", s)
    s = re.sub(r"\r\n?", "\n", s)
    s = re.sub(r"\n+", "<br>", s.strip())
    return _http.html_to_md(s) if "<" in s else _http.clean(_html.unescape(s))


def _el_md(el) -> str:
    return _md(el.text or "") if el is not None else ""


# --------------------------------------------------------------------------- #
# Source access
# --------------------------------------------------------------------------- #
async def _chapter_rows(no: int) -> list[dict]:
    hit = _chapters.get(no)
    if hit and time.monotonic() - hit[0] < _TTL:
        return hit[1]
    rows: list[dict] = []
    subids, done = ["A"], set()
    name = ""
    while subids:
        sub = subids.pop(0)
        if sub in done:
            continue
        done.add(sub)
        url = f"{BASE}/Pages/Treaties.aspx?id={no}&subid={sub}&clang=_en"
        r = await _http.get(url, follow_redirects=False)
        if r.status_code != 200:
            raise SourceError(_http.error("UNTC", f"chapter {_ROMAN[no - 1]} listing failed",
                                          r.status_code), r.status_code)
        root = lhtml.fromstring(r.text)
        lab = root.xpath("//label[contains(@id,'lblChapter')]")
        name = name or (_http.clean(lab[0].text_content()) if lab else f"CHAPTER {_ROMAN[no - 1]}")
        if sub == "A":
            for a in root.xpath(f"//a[contains(@href,'Treaties.aspx?id={no}&subid=')]"):
                m = re.search(r"subid=([A-Z])", a.get("href"))
                if m and m[1] not in done and m[1] not in subids:
                    subids.append(m[1])
        for tr in root.xpath("//tr[td/a[contains(@href,'mtdsg_no=')]]"):
            tds = tr.xpath("./td")
            if len(tds) < 4:
                continue
            ident = _http.clean(tds[-1].text_content())
            title = _http.clean(tds[-2].text_content())
            link = _http.clean(tr.xpath("./td/a[contains(@href,'mtdsg_no=')]")[0].text_content())
            if not _ID.match(ident) or not title:
                continue
            concl = link[len(title):].lstrip(". ").strip() if link.startswith(title) else ""
            rows.append({"id": ident, "title": title, "conclusion": concl, "chapter": name})
    _chapters[no] = (time.monotonic(), rows)
    return rows


async def _record(ident: str) -> dict:
    if ident in _status:
        return _status[ident]
    r = await _http.get(_xml_url(ident), follow_redirects=False)
    if r.status_code in (301, 302, 303, 404):
        raise NotFound(f"The UN Treaty Collection has no treaty {ident}. Find numbers with "
                       "search_legislation (e.g. IV-4, XXI-6, XI-B-19).")
    if r.status_code != 200:
        raise SourceError(_http.error("UNTC", f"status record {ident} failed", r.status_code),
                          r.status_code)
    try:
        root = etree.fromstring(r.content, etree.XMLParser(recover=True, huge_tree=True))
    except etree.XMLSyntaxError:
        root = None
    t = root.find("Treaty") if root is not None else None
    if t is None:
        raise SourceError(f"Error (UNTC): unexpected status record for {ident}.", r.status_code)
    return _http.lru_put(_status, ident, _parse_record(ident, t), 16)


def _parse_record(ident: str, t) -> dict:
    ext = t.find("Header/ExternalData")
    g = (lambda p: _http.clean(ext.findtext(p) or "")) if ext is not None else (lambda p: "")
    title = g("Titlesect") or _http.clean(t.findtext("Footer") or ident)
    chap = t.find("Header/Chapter")
    chapter = (_http.clean(f"{chap.findtext('Header') or ''}: {chap.findtext('Name') or ''}")
               if chap is not None else "")
    text_el = ext.find("TreatyText/Text") if ext is not None else None
    text_raw = (text_el.text or "") if text_el is not None else ""
    english_ctc = ""
    for href, label in re.findall(r'<a href="([^"]+\.pdf)"[^>]*>([^<]*)</a>', text_raw, re.I):
        if "english" in label.lower() or "_english" in href.lower():
            english_ctc = urljoin(BASE + "/", href)
            break
    rec = {
        "id": ident, "title": title, "chapter": chapter,
        "conclusion": g("Conclusion"),
        "eif": g("EIF/Labeltext"), "registration": g("Registration/Labeltext"),
        "signatories": g("Status/Signatories"), "parties": g("Status/Parties"),
        "text_refs": _md(text_raw), "note": _el_md(ext.find("TreatyNote/Text")) if ext is not None else "",
        "english_ctc": english_ctc, "template": _http.clean(t.findtext("Template") or ""),
        "sections": {},
    }
    rec["sections"]["status"] = _status_md(rec, t)
    for label, tag, _ in _SECTIONS[1:]:
        el = t.find(tag)
        if el is not None and len(el):
            md = _section_md(el)
            if md:
                rec["sections"][label] = md
    return rec


def _table_md(header: list[str], rows: list[list[str]]) -> str:
    esc = lambda c: c.replace("|", "\\|")  # noqa: E731
    out = ["| " + " | ".join(esc(h) for h in header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(esc(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def _status_md(rec: dict, t) -> str:
    parts = [f"## Status of {rec['title']}"]
    for k, v in (("Chapter", rec["chapter"]), ("Concluded", rec["conclusion"]),
                 ("Entry into force", rec["eif"]), ("Registration", rec["registration"]),
                 ("Signatories", rec["signatories"]), ("Parties", rec["parties"])):
        if v:
            parts.append(f"- **{k}:** {v}")
    if rec["text_refs"]:
        parts.append(f"- **Text:** {rec['text_refs']}")
    if rec["note"]:
        parts += ["", "### Note", rec["note"]]
    tg = t.find("Participants/Table/TGroup")
    if tg is not None:
        header = [_md(e.text or "") for e in tg.findall("Thead/Row/Entry")]
        rows = [[_md(e.text or "") for e in row.findall("Entry")]
                for row in tg.findall("Tbody/Rows/Row")]
        if header and rows:
            parts += ["", "### Participants", _table_md(header, rows)]
    return "\n".join(parts).strip()


def _section_md(el) -> str:
    parts: list[str] = []
    titles = [_el_md(x) for x in el.findall("Title")]
    titles = [x for x in titles if x]
    if titles:
        parts.append(f"## {titles[0]}")
        parts += titles[1:]
    if el.tag == "TerritorialApplications":
        hdr = el.find("Header")
        header = [_el_md(c) for c in hdr] if hdr is not None else ["Participant", "Date", "Territories"]
        rows = [[_el_md(c) for c in app] for app in el.findall("Application")]
        if rows:
            parts.append(_table_md(header, rows))
    elif el.tag == "SpecialTables":
        for tab in el.findall("Table"):
            parts.append(f"### {_el_md(tab.find('Title'))}")
            header = [_el_md(c) for c in tab.findall("TableHeader/Title")]
            rows = [[_el_md(c) for c in row.findall("Column")] for row in tab.findall("Rows/Row")]
            if rows:
                n = max(len(r) for r in rows)
                header = (header + [""] * n)[:n]
                parts.append(_table_md(header, [(r + [""] * n)[:n] for r in rows]))
    elif el.tag == "EndNotes":
        for note in el.findall("Note"):
            body = "\n\n".join(x for x in (_el_md(tx) for tx in note.findall("text")) if x)
            parts.append(f"**[{_http.clean(note.findtext('index'))}]** {body}")
    else:
        for item in el:
            if item.tag == "Title":
                continue
            who = _el_md(item.find("Participant"))
            if who:
                parts.append(f"### {who}")
            for tx in item.findall("text"):
                s = _el_md(tx)
                if s:
                    parts.append(f"**{s}**" if tx.get("type") == "title" else s)
    return "\n\n".join(parts).strip()


async def _ctc_from_page(ident: str) -> str:
    """The status page's 'Certified true copy' PDF link, or ''."""
    url = _status_url(ident)
    for _ in range(3):
        r = await _http.get(url, follow_redirects=False)
        m = re.search(r'hypCTC"\s+href="([^"]+)"', r.text or "")
        if m:
            return urljoin(BASE + "/", _html.unescape(m[1]))
        loc = r.headers.get("location", "")
        if r.status_code in (301, 302, 303) and loc and "ViewDetails" in loc:
            url = urljoin(BASE + "/Pages/", loc)
            continue
        if r.status_code != 200:
            raise SourceError(_http.error("UNTC", f"status page {ident} failed", r.status_code),
                              r.status_code)
        return ""
    return ""


async def _treaty_text(rec: dict) -> tuple[str, str]:
    """(pdf url, text) or (reason it is unavailable, '')."""
    ident = rec["id"]
    if ident in _texts:
        return _texts[ident]
    pdf = rec["english_ctc"] or await _ctc_from_page(ident)
    if not pdf:
        res = ("The UN Treaty Collection links no certified true copy (treaty text) for this "
               "treaty; see the United Nations Treaty Series reference in the status record.", "")
        return _http.lru_put(_texts, ident, res, 6)
    h = await _http.request("HEAD", pdf)
    size = int(h.headers.get("content-length") or 0)
    if h.status_code != 200:
        raise SourceError(_http.error("UNTC", f"treaty text PDF {pdf}", h.status_code), h.status_code)
    if size > _MAX_PDF:
        res = (f"The treaty text is a {size // 1_000_000} MB scanned PDF (often all six "
               f"languages in one file), too large to fetch here; open it at {pdf}", "")
        return _http.lru_put(_texts, ident, res, 6)
    r = await _http.get(pdf)
    if r.status_code != 200:
        raise SourceError(_http.error("UNTC", f"treaty text PDF {pdf}", r.status_code), r.status_code)
    # OCR reads "(b)" as "<b)"; repair it so the text cannot look like an HTML tag
    text = re.sub(r"<(?=[a-z0-9]{1,4}\))", "(", _http.pdf_text(r.content))
    if len(re.findall(r"[A-Za-z]{3,}", text)) < 200:
        res = (f"The treaty text PDF has no usable text layer (scanned image; no OCR here): {pdf}", "")
    else:
        res = (pdf, text)
    return _http.lru_put(_texts, ident, res, 6)


# --------------------------------------------------------------------------- #
# Articles in the PDF text
# --------------------------------------------------------------------------- #
_ART_LINE = re.compile(r"^(?:Article|ARTICLE)\s+([0-9kKhUlIiOoSsBg]{1,3}|[IVXL]{1,6})\s*\.?$")
_STRUCT_LINE = re.compile(r"^(PART|SECTION|ANNEX|CHAPTER|Part|Section|Annex|Chapter)\s+"
                          r"([IVXL]{1,6}|\d{1,3}|[A-Z])\b\s*\.?(?:\s+[^a-z]{3,90})?$")
_OCR_DIGITS = str.maketrans("kKhUlIiOoSsBg", "4444111005589")
_STEP = 6     # an article number may skip at most this many (OCR-garbled headings)


def _roman(s: str) -> int:
    vals = {"I": 1, "V": 5, "X": 10, "L": 50}
    n = 0
    for a, b in zip(s, s[1:] + " "):
        n += -vals[a] if vals.get(b, 0) > vals[a] else vals[a]
    return n


def _art_no(tok: str) -> tuple[str, int] | None:
    """Heading token -> (label number, value). The CTCs' OCR reads 4 as 'k'/'h'/'U' and
    1 as 'l'/'I'; Roman-numbered articles stay Roman."""
    if re.fullmatch(r"[IVXL]+", tok) and not tok.isdigit():
        return tok, _roman(tok)
    d = tok.translate(_OCR_DIGITS)
    return (str(int(d)), int(d)) if d.isdigit() else None


def _articles(text: str) -> tuple[list[TocEntry], dict[str, tuple[int, int]]]:
    """TOC entries and label -> (start, end) offsets of each article in the text.

    A heading counts only if its number follows the previous one within _STEP (within the
    same annex), which drops garbled headings and the later language copies of the text
    (multilingual CTCs); any heading line still ends the article before it."""
    entries: list[TocEntry] = []
    spans: dict[str, tuple[int, int]] = {}
    open_label, annex, last, pos = None, "", 0, 0
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        start, pos = pos, pos + len(ln) + 1
        s = ln.strip()
        m = _ART_LINE.match(s)
        st = None if m else _STRUCT_LINE.match(s)
        if not m and not st:
            continue
        if open_label:
            spans[open_label] = (spans[open_label][0], start)
            open_label = None
        if st:
            if st[1].upper() == "ANNEX" and f"Annex {st[2]}" != annex:
                annex, last = f"Annex {st[2]}", 0
            entries.append(TocEntry(title=s, level=0))
            continue
        no = _art_no(m[1])
        if not no or not last < no[1] <= last + _STEP:
            continue
        label = f"{annex} Article {no[0]}".strip()
        if label in spans:
            continue
        last = no[1]
        spans[label] = (start, len(text))
        open_label = label
        nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
        heading = nxt if (nxt and len(nxt) < 80 and nxt[:1].isupper()
                          and not re.search(r"\b(shall|may|is|are|has|have)\b", nxt)
                          and not _ART_LINE.match(nxt) and not _STRUCT_LINE.match(nxt)) else ""
        entries.append(TocEntry(title=label + (f" - {heading}" if heading else ""),
                                level=1, provision=label))
    while entries and not entries[-1].provision:     # headings of later language copies
        entries.pop()
    return entries, spans


_NON_LATIN = re.compile(r"[\u0400-\u04ff\u0600-\u06ff\u3000-\u9fff\uac00-\ud7af]")


def _english_start(text: str) -> int:
    """Offset where the English copy starts in a multilingual CTC whose first pages are
    Chinese/Russian/Arabic (0 if the text already opens in a Latin script). Walks back
    from the first English 'Article 1' over the Latin-script lines (title, preamble)."""
    if len(_NON_LATIN.findall(text[:3000])) < 20:
        return 0
    _, spans = _articles(text)
    first = min((a for a, _ in spans.values()), default=0)
    lines = text[:first].split("\n")
    k = len(lines)
    while k > 0 and len(lines) - k < 200 and not _NON_LATIN.search(lines[k - 1]):
        k -= 1
    return len("\n".join(lines[:k])) + 1 if k else 0


def _text_md(text: str) -> str:
    out = []
    for ln in text.split("\n"):
        s = ln.strip()
        if _ART_LINE.match(s) or _STRUCT_LINE.match(s):
            out.append(f"\n### {s}\n")
        else:
            out.append(ln)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip()


def _norm_provision(raw: str) -> str:
    s = _http.clean(raw).strip(" .,;:")
    low = s.lower()
    if low in dict.fromkeys(x[0] for x in _SECTIONS):
        return low
    if low in _ALIASES:
        return _ALIASES[low]
    m = re.fullmatch(r"(?:annex|annexe?)\s+([ivxl]+|\d+)(?:\s*[,;:]\s*|\s+)(?:art(?:icle)?\.?\s*)?"
                     r"(\d{1,3}|[ivxl]+)", low)
    if m:
        an = _ROMAN[int(m[1]) - 1] if m[1].isdigit() and 1 <= int(m[1]) <= len(_ROMAN) else m[1].upper()
        return f"Annex {an} Article {str(int(m[2])) if m[2].isdigit() else m[2].upper()}"
    m = re.fullmatch(r"(?:art(?:icle)?\.?|art\.)?\s*(\d{1,3}|[ivxl]{1,6})", low)
    if m:
        return f"Article {str(int(m[1])) if m[1].isdigit() else m[1].upper()}"
    return s


# --------------------------------------------------------------------------- #
class UNTC(Jurisdiction):
    code = "untc"
    name = "UN Treaty Collection (multilateral treaties deposited with the UN Secretary-General)"
    languages = ("en",)
    aliases = ("un treaties", "united nations treaty collection", "mtdsg", "un treaty collection",
               "treaties.un.org")
    sources = (
        Source(
            name="United Nations Treaty Collection (treaties.un.org), MTDSG status records and "
                 "certified true copies",
            url="https://treaties.un.org/Pages/ParticipationStatus.aspx?clang=_en",
            covers=("legislation",),
            licence=("© United Nations; UN website Terms of Use: download and copy for personal, "
                     "non-commercial use, no resale, redistribution or derivative compilations"),
            commercial_use=False,
            ai_use=None,   # robots.txt: only 'Crawl-delay: 2'; terms have no AI/TDM clause
            auth="none",
            rate_limit=("robots.txt Crawl-delay: 2 (honoured: 2 s spacing); no 429 seen in "
                        "~130 requests during 2026-11-06 test runs; no documented limit"),
            terms_url="https://www.un.org/en/about-us/terms-of-use",
            warning=("UN Terms of Use: materials may be downloaded and copied for personal, "
                     "non-commercial use only, without redistribution or derivative compilations."),
        ),
    )
    legislation_filters = {
        "chapter": "MTDSG chapter, Roman or Arabic (e.g. IV or 4 = Human Rights, XXI = Law of the "
                   "Sea, XXVII = Environment); searching one chapter is much faster",
    }
    min_interval = {HOST: 2.0}
    notes = ("Multilateral treaties deposited with the UN Secretary-General (MTDSG), by MTDSG "
             "number (IV-4 = ICCPR, XXI-6 = UNCLOS). Status, parties, reservations and "
             "objections as provisions; treaty text from the certified true copy PDF where it "
             "has a text layer. First unfiltered search takes ~70 s (Crawl-delay 2).")
    gaps = (
        ("Treaty text when the certified copy has no usable text layer or is too large: scans only,"
         " no text (status record instead)"),
        ("Treaties registered but not deposited with the Secretary-General (UNTS, incl. bilateral):"
         " not researched yet"),
        ("Full-text search across treaty texts: the site's search is a multi-step ASP.NET form; not"
         " built yet"),
        ("Articles in French and the other official languages: only English headings are cut out; "
         "not built yet"),
    )
    samples = {
        "legislation_query": "law of the sea",
        "law_id": "XXI-6",
        "provision": "Article 3",
    }

    # ------------------------------------------------------------------ #
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        f = {k: str(v).strip() for k, v in (filters or {}).items() if str(v).strip()}
        chapters = list(range(1, len(_ROMAN) + 1))
        if "chapter" in f:
            c = f["chapter"].upper().removeprefix("CHAPTER").strip()
            if c.isdigit() and 1 <= int(c) <= len(_ROMAN):
                chapters = [int(c)]
            elif c in _ROMAN:
                chapters = [_ROMAN.index(c) + 1]
            else:
                raise BadRequest("chapter must be I-XXIX or 1-29 (e.g. IV for human rights).")
        q = _http.clean(query)
        exact = ""
        try:
            exact = _norm_id(q) if re.match(r"(?i)^(?:mtdsg\s*)?[ivxl]+[\s\-./]", q) else ""
        except BadRequest:
            exact = ""
        if exact:
            chapters = [_chapter_of(exact)]
        words = [w.lower() for w in re.findall(r"\w+", q) if len(w) > 1 or w.isdigit()]
        hits = []
        for no in chapters:
            for row in await _chapter_rows(no):
                if exact:
                    if row["id"] != exact:
                        continue
                else:
                    hay = " ".join((row["id"], row["title"], row["conclusion"], row["chapter"])).lower()
                    if not all(re.search(rf"\b{re.escape(w)}", hay) for w in words):
                        continue
                hits.append(row)
        if not exact:      # exact title first, then titles starting with the query, then the rest
            ql = q.lower()
            hits.sort(key=lambda r: 0 if r["title"].lower() == ql
                      else 1 if r["title"].lower().startswith(ql) else 2)
        limit = max(1, min(int(limit), 50))
        page = max(1, int(page))
        items = [LawHit(
            id=row["id"],
            title=row["title"],
            type="Multilateral treaty (MTDSG)",
            number=row["id"],
            date=_dmy(row["conclusion"]),
            snippet=_http.clean(f"{row['conclusion']} · {row['chapter']}".strip(" ·")),
            url=_status_url(row["id"]),
        ) for row in hits[(page - 1) * limit: page * limit]]
        return Results(items=items, total=len(hits),
                       note=("Title words in the MTDSG chapter listings (all words must match); "
                             "date = date of conclusion. Treaties registered but not deposited "
                             "with the Secretary-General (UNTS) are not covered."))

    # ------------------------------------------------------------------ #
    async def get_legislation_toc(self, id):
        ident = _norm_id(id)
        rec = await _record(ident)
        entries = [TocEntry(title=title, level=0, provision=label)
                   for label, _, title in _SECTIONS if label in rec["sections"]]
        src, text = await _treaty_text(rec)
        if text:
            entries.append(TocEntry(title="Treaty text (certified true copy)", level=0))
            arts, _ = _articles(text)
            entries += arts
        else:
            entries.append(TocEntry(title=f"Treaty text: not available here. {src}", level=0))
        return Toc(id=ident, title=rec["title"], url=_status_url(ident), entries=entries)

    async def get_legislation_provision(self, id, provision):
        ident = _norm_id(id)
        label = _norm_provision(provision)
        if label.startswith(("Article", "Annex")) and "(" in label:
            raise BadRequest(f"Sub-paragraph references are not supported ({provision!r}); ask for "
                             "the whole article, e.g. 'Article 3'.")
        if re.fullmatch(r"(?i)annex\s+\w+", label):
            raise BadRequest(f"{provision!r} names a whole annex; ask for one article, e.g. "
                             f"'{label} Article 1' (see get_legislation_toc).")
        rec = await _record(ident)
        if label in rec["sections"]:
            return Provision(law_id=ident, law_title=rec["title"], provision=label,
                             text=rec["sections"][label], url=_status_url(ident),
                             as_of=_http.today())
        if label in dict.fromkeys(x[0] for x in _SECTIONS):
            raise NotFound(f"Treaty {ident} has no '{label}' section in its status record "
                           f"(available: {', '.join(rec['sections'])}).")
        if not label.startswith(("Article", "Annex")):
            raise BadRequest(f"Unknown provision {provision!r}. Use a status section "
                             f"({', '.join(x[0] for x in _SECTIONS)}) or 'Article 5' / "
                             "'Annex II Article 3' as get_legislation_toc lists them.")
        src, text = await _treaty_text(rec)
        if not text:
            raise NotFound(f"No treaty text for {ident}: {src}")
        _, spans = _articles(text)
        m = re.fullmatch(r"Annex (\S+) (Article .+)", label)
        if label not in spans and m and m[1] in _ROMAN:      # annex headed with a digit in the text
            alt = f"Annex {_ROMAN.index(m[1]) + 1} {m[2]}"
            if alt in spans:
                label = alt
        if label not in spans:
            pre, _, num = label.rpartition("Article ")
            pre = pre.strip()
            pres = {pre}
            if m and m[1] in _ROMAN:
                pres.add(f"Annex {_ROMAN.index(m[1]) + 1}")
            nums = [int(k.rpartition("Article ")[2]) for k in spans
                    if k.rpartition("Article ")[0].strip() in pres
                    and k.rpartition("Article ")[2].isdigit()]
            if num.isdigit() and int(num) == 0:
                raise NotFound(f"{label} is not a valid article number; see get_legislation_toc.")
            if pre and not nums:
                raise NotFound(f"{label} not found: no numbered articles were parsed under {pre} "
                               f"in the text of {ident} (the OCR text layer may have garbled the "
                               "headings); see get_legislation_toc.")
            if num.isdigit() and nums and int(num) > max(nums):
                raise NotFound(f"{label} not found: the text of {ident} has no article that high "
                               f"(last {pre + ' ' if pre else ''}Article {max(nums)}); "
                               "see get_legislation_toc.")
            raise NotFound(f"{label} not found in the text of {ident} (the OCR text layer may "
                           "have garbled its heading); see get_legislation_toc.")
        a, b = spans[label]
        return Provision(law_id=ident, law_title=rec["title"], provision=label,
                         text=_text_md(text[a:b]), url=src)

    async def get_legislation_text(self, id):
        ident = _norm_id(id)
        rec = await _record(ident)
        src, text = await _treaty_text(rec)
        meta = {k: v for k, v in {
            "Chapter": rec["chapter"], "Concluded": rec["conclusion"],
            "Entry into force": rec["eif"], "Registration": rec["registration"],
            "Signatories": rec["signatories"], "Parties": rec["parties"],
            "Status record": _status_url(ident)}.items() if v}
        if text:
            meta["Text"] = ("certified true copy PDF, UN's own OCR text layer (may contain "
                            "recognition errors; multilingual copies hold all authentic languages)")
            cut = _english_start(text)
            if cut:
                meta["Text"] += ("; the PDF opens with the Chinese/Russian/Arabic copies, "
                                 "this text starts at the English copy")
            return LawText(id=ident, title=rec["title"], text=_text_md(text[cut:]), url=src,
                           as_of="", metadata=meta)
        meta["Text"] = f"treaty text not available: {src}"
        body = (f"> Treaty text not available here: {src} This is the depositary status "
                "record instead.\n\n" + "\n\n".join(rec["sections"].values()))
        return LawText(id=ident, title=rec["title"], text=body, url=_status_url(ident),
                       as_of=_http.today(), metadata=meta)
