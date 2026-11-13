"""Bangladesh: Laws of Bangladesh (bdlaws.minlaw.gov.bd, Legislative and Parliamentary Affairs
Division) for legislation; Supreme Court of Bangladesh (supremecourt.gov.bd) for judgments.

Legislation, bdlaws.minlaw.gov.bd (server-rendered HTML, served as UTF-16 with a BOM):
  * Search: GET /search.html?q=&type=&page=  type 1 = free text in sections, 2 = short title,
    3 = Act number (Roman, e.g. "IX"), 4 = Act year. 20 hits per page, "1 to 20 of N".
    Free-text hits point at a section (/act-26/section-176.html); the others at the Act.
  * Act page /act-{id}.html: title, "(ACT NO. IX OF 1872)", date, contents list. Each
    contents row links a section page /act-{id}/section-{sid}.html. Rows are the site's own
    sub-units: one numbered section can span several rows (the first carries the number,
    e.g. "1. Short title", the next "Extent", "Commencement" none). Repealed ranges are
    one row ("76-123. [Repealed]"). Bengali Acts number as "১।" / "৩ক।".
  * Full text /act-details-{id}.html (up to ~1.3 MB). Amendment notes are footnotes in
    span.footnote[title]; rendered here as markdown footnotes.
  * Unknown ids redirect (302) to /404.html.
  * The id used here is the site's numeric Act id (26 = Contract Act, 1872), not the official
    Act number, which is shown as `number`.

Case law, supremecourt.gov.bd:
  * Search: POST /web/judgments/judgment_list.php (the site's own AJAX form endpoint):
    div_id 1 = Appellate Division, 2 = High Court Division; type_id 5 = judgments, 4 = orders;
    case_number, year, case_type_id, parties, short_desc. One of case_number/parties/
    short_desc is required. All matches come back at once (no paging, no count).
  * Each row links a PDF /resources/documents/{file}.pdf; the file name is the id here.
    PDFs checked have a text layer; scanned ones return a pointer to the PDF (no OCR).
  * The listing has an upload date only, not the decision date; get_decision reads the
    "Judgment on dd.mm.yyyy" line from the PDF when there is one.

Verified 2026-11-06:
  * robots.txt: bdlaws.minlaw.gov.bd has none (/robots.txt redirects to the site's 404 page);
    www.supremecourt.gov.bd and supremecourt.gov.bd answer 404. No terms-of-use page on either
    site; bdlaws shows "Copyright © 2019, Legislative and Parliamentary Affairs Division",
    the Supreme Court site no terms or licence at all.
"""
from __future__ import annotations

import re
from urllib.parse import quote, unquote, urlsplit

from lxml import html as LH

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

LAWS_HOST = "bdlaws.minlaw.gov.bd"
LAWS = f"https://{LAWS_HOST}"
SC_HOST = "www.supremecourt.gov.bd"
SC_DOC_HOST = "supremecourt.gov.bd"
SC_LIST = f"https://{SC_HOST}/web/judgments/judgment_list.php"
SC_DOCS = f"https://{SC_DOC_HOST}/resources/documents/"
SC = "Supreme Court of Bangladesh"
DIVISIONS = {"appellate": ("1", "Appellate Division"), "high_court": ("2", "High Court Division")}
KINDS = {"judgments": "5", "orders": "4"}
SITE_PAGE = 20
_BN_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
_BN_MONTHS = {"জানু": 1, "ফেব্রু": 2, "মার্চ": 3, "এপ্রি": 4, "মে": 5, "জুন": 6, "জুলা": 7,
              "আগ": 8, "সেপ্ট": 9, "অক্টো": 10, "নভে": 11, "ডিসে": 12}
_NUM = re.compile(r"^\[?\s*([0-9০-৯]+[A-Za-zক-হ]{0,3}(?:\s*[-–]\s*[0-9০-৯]+[A-Za-zক-হ]{0,3})?)"
                  r"\s*[.।৷]\s*(.*)$", re.S)
_BIJOY = re.compile(r"[\u2020\u2021\u00a8\u00b5\u0161\u00d0\u2039\u203a\u00c5\u00cb\u00e9\u00ef]")   # legacy Bijoy-font Bengali
_STOP = {"section", "sections", "sec", "of", "the", "and", "in", "under", "code", "act", "on", "for", "to", "a"}
_DOC_ID = re.compile(r"^[^/\\?#]+\.pdf$", re.I)

# Legacy Bijoy (SutonnyMJ) ASCII-Bengali -> Unicode. Longest keys first; kars are reordered afterwards.
_BJ_LIG = {"Av": "আ", "ÿ": "ক্ষ", "Ÿ": "জ্ঞ", "µ": "ক্র", "š": "ন্", "¯": "স্", "œ": "্ন", "¨": "্য",
           "ª": "্র", "¬": "্ব", "³": "ক্ত", "½": "ঙ্গ", "ó": "ষ্ট", "×": "দ্ধ", "æ": "ু", "ï": "শু",
           "‘": "তু", "’": "থ", "Í": "ত", "©": "\ue000", "„": "ৃ", "~": "ূ", "‡": "ে", "†": "ে",
           "ˆ": "ৈ", "‰": "ৈ", "Š": "ৗ", "|": "।"}
_BJ_ONE = {**{c: u for c, u in zip("ABCDEFGHIJ", "অইঈউঊঋএঐওঔ")},
           **{c: u for c, u in zip("KLMNOPQRSTUVWXYZ_`abcdefghijklmn", "কখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমযরলশষসহ")},
           **{"o": "ড়", "p": "ঢ়", "q": "য়", "r": "ৎ", "s": "ং", "t": "ঃ", "u": "ঁ", "v": "া", "w": "ি",
              "x": "ী", "y": "ু", "z": "ু"},
           **{c: u for c, u in zip("0123456789", "০১২৩৪৫৬৭৮৯")}}
_BJ_RE = re.compile("|".join(map(re.escape, sorted(_BJ_LIG, key=len, reverse=True))) + "|.", re.S)
_BJ_CL = r"[\u0995-\u09B9\u09DC-\u09DF](?:\u09CD[\u0995-\u09B9\u09DC-\u09DF])*"
_BJ_MARK = re.compile(r"[†‡µ¨šÍïÿœæ×óª©¬„ˆ‰Š³½¯Ÿ]")
_BJ_LEFT = re.compile(r"[^\x00-\x7f\u0964\u0980-\u09ff\u2000-\u206f\u00a0]")


def _bijoy_line(line: str) -> str:
    out = _BJ_RE.sub(lambda m: _BJ_LIG.get(m[0]) or _BJ_ONE.get(m[0], m[0]), line)
    out = re.sub(f"([িেৈ])({_BJ_CL})", r"\2\1", out)
    out = out.replace("ে" "া", "ো").replace("ে" "ৗ", "ৌ")
    out = re.sub(f"({_BJ_CL})([ািীুূৃেৈোৌ]*)\ue000", lambda m: "র্" + m[1] + m[2], out)
    return out if not _BJ_LEFT.search(out) and "\ue000" not in out else line


def _bijoy_text(text: str) -> tuple[str, bool]:
    """Convert the Bijoy-typed lines of a PDF text layer; returns (text, every such line converted)."""
    lines, clean = text.split("\n"), True
    for i, ln in enumerate(lines):
        if _BJ_MARK.search(ln):
            new = _bijoy_line(ln)
            clean &= new != ln
            lines[i] = new
    return "\n".join(lines), clean


_act_cache: dict = {}       # act id -> parsed act page
_search_cache: dict = {}
_sc_meta: dict = {}         # pdf file -> metadata seen in a search


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _decode(r) -> str:
    b = r.content
    if b[:2] in (b"\xfe\xff", b"\xff\xfe"):
        return b.decode("utf-16")
    return r.text


def _norm(label: str) -> str:
    """Provision label for comparison: ASCII digits, no spaces/dots, lower case."""
    s = _http.clean(label).translate(_BN_DIGITS).lower()
    s = re.sub(r"^(section|sec\.?|s\.|article|art\.?|ধারা|অনুচ্ছেদ)\s*", "", s)
    return re.sub(r"\s+", "", s).rstrip(".।৷").replace("–", "-")


def _date(s: str) -> str:
    """'25th April, 1872' / '১১ অক্টোবর ২০০৬' -> ISO."""
    s = _http.clean(s).strip("[] ").translate(_BN_DIGITS)
    m = re.search(r"(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+),?\s+(\d{4})", s)
    if m:
        return _http.en_date(f"{m[2]} {m[1]}, {m[3]}")
    m = re.search(r"(\d{1,2})\s+(\S+)\s+(\d{4})", s)
    if m:
        for k, v in _BN_MONTHS.items():
            if m[2].startswith(k):
                return f"{m[3]}-{v:02d}-{int(m[1]):02d}"
    return ""


def _act_id(id) -> str:
    s = str(id).strip()
    m = re.fullmatch(r"(?:https?://[^/]+)?/?(?:act-(?:details-)?)?(\d+)(?:\.html)?(?:/.*)?", s, re.I)
    if not m:
        raise BadRequest("Use the bdlaws.minlaw.gov.bd Act id from search_legislation, e.g. '26' "
                         "(Contract Act, 1872), or an act-26.html URL.")
    return m[1]


async def _get_laws(path: str, what: str) -> str:
    r = await _http.get(f"{LAWS}{path}")
    if any("404.html" in str(h.headers.get("location", "")) for h in r.history) or "/404.html" in str(r.url):
        raise NotFound(f"bdlaws.minlaw.gov.bd has no {what} at {LAWS}{path}.")
    if r.status_code != 200:
        raise SourceError(_http.error("bdlaws.minlaw.gov.bd", f"{what} failed", r.status_code), r.status_code)
    return _decode(r)


def _footnotes(root) -> dict[str, str]:
    """Replace each span.footnote with a markdown marker [^n]; return {n: note}."""
    notes: dict[str, str] = {}
    for sp in root.xpath("//span[contains(concat(' ', normalize-space(@class), ' '), ' footnote ')]"):
        n = _http.clean(sp.text_content()).translate(_BN_DIGITS) or str(len(notes) + 1)
        notes.setdefault(n, _http.clean(sp.get("title", "")))
        tail = sp.tail
        marker = LH.fromstring(f"<span>[^{n}]</span>")
        marker.tail = tail
        sp.getparent().replace(sp, marker)
    return notes


def _notes_md(notes: dict[str, str], used: str) -> str:
    keep = [f"[^{n}]: {t}" for n, t in notes.items() if t and f"[^{n}]" in used]
    return "\n\n".join(keep)


def _md(el) -> str:
    return _http.html_to_md(LH.tostring(el, encoding="unicode")) if el is not None else ""


def _first(root, cls: str):
    r = root.xpath(f"//*[contains(concat(' ', normalize-space(@class), ' '), ' {cls} ')]")
    return r[0] if r else None


def _act_header(root) -> tuple[str, str, str]:
    h3 = root.xpath("//section[contains(@class,'bg-act-section')]//h3")
    h4 = root.xpath("//section[contains(@class,'bg-act-section')]//h4")
    title = _http.clean(re.sub(r"\[\^\d+\]", "", h3[0].text_content())) if h3 else ""
    number = _http.clean(h4[0].text_content()).strip("() ") if h4 else ""
    pd = _first(root, "publish-date")
    return title, number, _date(pd.text_content()) if pd is not None else ""


async def _act(aid: str) -> dict:
    """Parsed act page: title, number, date, entries [(TocEntry, section_path)]."""
    hit = _act_cache.get(aid)
    if hit:
        return hit
    root = LH.fromstring(await _get_laws(f"/act-{aid}.html", f"Act {aid}"))
    _footnotes(root)
    title, number, date = _act_header(root)
    if not title:
        raise SourceError(f"bdlaws.minlaw.gov.bd Act {aid}: no title on the page (layout changed?)")
    entries: list[tuple[TocEntry, str]] = []
    area = _first(root, "search-here")
    current, chap = "", ""
    for p in (area.iter("p") if area is not None else []):
        cls = p.get("class") or ""
        t = _http.clean(re.sub(r"\[\^\d+\]", "", p.text_content()))
        if not t:
            continue
        if "act-chapter-no" in cls:
            chap = t
        elif "act-chapter-name" in cls:
            entries.append((TocEntry(f"{chap} {t}".strip() if chap and t != chap else t, 0, ""), ""))
            chap = ""
        elif "act-section-head" in cls:
            if chap:
                entries.append((TocEntry(chap, 0, ""), ""))
                chap = ""
            entries.append((TocEntry(t, 1, ""), ""))
        elif "act-section-name" in cls:
            if chap:
                entries.append((TocEntry(chap, 0, ""), ""))
                chap = ""
            a = p.find(".//a")
            href = a.get("href", "") if a is not None else ""
            m = _NUM.match(t)
            if m:
                current = re.sub(r"\s+", "", m[1]).replace("–", "-")
                # the title keeps the site's own number; the provision label uses ASCII digits so a
                # keyword such as '13' finds Bengali section '১৩' (get_legislation_provision reads both)
                entries.append((TocEntry(f"{current}. {m[2]}".strip(), 1, current.translate(_BN_DIGITS)), href))
            elif current:     # continuation row of the current section
                entries.append((TocEntry(t, 2, current.translate(_BN_DIGITS)), href))
            else:             # unnumbered row before any number: open it by its heading
                entries.append((TocEntry(t, 1, t), href))
    data = {"title": title, "number": number, "date": date, "entries": entries}
    return _http.lru_put(_act_cache, aid, data, 16)


def _rows_md(root, chapters: bool = True) -> str:
    """Section rows (heading + body), and chapter headings if `chapters`, of a section or
    full-text page, in order."""
    out = []
    for el in root.xpath("//div[contains(@class,'act-chapter-group')] | "
                         "//div[contains(concat(' ', normalize-space(@class), ' '), ' txt-head ')]"):
        cls = el.get("class") or ""
        if "act-chapter-group" in cls:
            if not chapters:
                continue
            t = " ".join(_http.clean(p.text_content()) for p in el.iter("p") if _http.clean(p.text_content()))
            if t:
                out.append(f"## {t}")
            continue
        head = _http.clean(el.text_content())
        body = el.getnext()
        while body is not None and "txt-details" not in (body.get("class") or ""):
            body = body.getnext()
        if head:
            out.append(f"### {head}")
        b = _md(body)
        if b:
            out.append(b)
    return "\n\n".join(out)


# --------------------------------------------------------------------------- #
# case-law helpers
# --------------------------------------------------------------------------- #
def _case_from_file(case: str, file: str) -> str:
    """Case label whose number the listing lost ('Civil Appeal /2017'): case type from the listing,
    number and year from the PDF file name. Returns the listing text unchanged if they cannot be read."""
    if re.search(r"\bof\s+\d{4}$", case) and "From the" not in case:
        return case
    head = re.split(r"\s*/|\s*\.?\s*From the\b|\s+NOS?\.?(?=\s*\d)", case, flags=re.I)[0].strip(" .")
    fm = re.search(r"Nos?[._\s-]*(\d+(?:[_,&\s-]\d+)*)(?:[_\s]*of[_\s]*(\d{2,4}))?", file, re.I)
    if not (head and fm):
        return head or case
    nums, year = re.findall(r"\d+", fm[1]), fm[2]
    if not year and len(nums) > 1 and re.fullmatch(r"(?:19|20)\d{2}", nums[-1]):
        year = nums.pop()
    if not year:
        return head or case
    label = re.sub(r"[_,&\s]+", ", ", fm[1]).strip(", ")
    if not fm[2]:
        label = re.sub(r"[,\s-]*" + year + "$", "", label)
    return f"{head} No. {label} of {'20' + year if len(year) == 2 else year}"


def _sc_rows(page: str, division: str) -> list[DecisionHit]:
    root = LH.fromstring(page or "<html/>")
    hits = []
    for tr in root.xpath("//tr[contains(@class,'font_e_12')]"):
        tds = tr.findall("td")
        if len(tds) < 4:
            continue
        link = next((a for a in tds[1].iter("a") if (a.get("href") or "").lower().endswith(".pdf")
                     and "translation" not in a.get("href", "")), None)
        if link is None:
            continue
        file = unquote(link.get("href").rsplit("/", 1)[-1])
        listed = _http.clean(link.text_content())
        case = _http.clean(listed.split("(", 1)[0])
        if not re.fullmatch(r"[^\d/]*\d[^/]*/\d{4}", case):   # listing lost or garbled the number
            case = _case_from_file(case, file)
        info = _http.clean(tds[1].text_content())
        up = re.search(r"Uploaded on\s*:\s*(\S+)", info)
        bench = _http.clean(info.split(up[0], 1)[1]) if up else ""
        parties = _http.clean(tds[2].text_content())
        desc = _http.clean(tds[3].text_content())
        title = re.sub(r"\s*\.{2,}\s*[\w-]+(?:\s+\w+)?(?=\s*-?\s*-?Versus|\s*$)", "", parties)
        title = re.sub(r"\s*-*\s*\b(?:vs\.?|versus)\b\s*-*\s*", " v ", title, flags=re.I)
        snippet = "; ".join(x for x in (f"Uploaded {up[1]}" if up else "", bench, desc[:300]) if x)
        h = DecisionHit(id=file, title=title or f"{SC} {case}", court=f"{SC}, {division}",
                        date="", case_number=case, snippet=snippet, url=SC_DOCS + quote(file))
        _sc_meta[file] = {"title": h.title, "court": h.court, "case_number": case,
                          "Uploaded on": up[1] if up else "", "Bench": bench,
                          "Case (as listed)": listed if listed != case and "(.../)" not in listed else "", "Short description": desc}
        while len(_sc_meta) > 1000:
            _sc_meta.pop(next(iter(_sc_meta)))
        hits.append(h)
    return hits


_CASE_NO = re.compile(r"^((?:[A-Z][A-Za-z().]*[ \t]+){1,5}(?i:Petition|Appeal|Reference|Revision|Rule|Case|"
                      r"Application|Suit|Matter)\s+(?i:Nos?)\.?\s*(?:[\d,\s\-–&]|(?i:and))+\s+(?i:of)\s+\d{4})", re.M)
_JDATE = re.compile(r"Date\s+of\s+(?:Judg(?:e)?ment|Order|Decision)s?\s*\.?\s*[:\-]?\s*(?:The\s+)?"
                    r"(\d{1,2})\s*(?:st|nd|rd|th)?\s*,?\s*([A-Za-z]+)\.?,?\s*(\d(?:\s?\d){3})", re.I)
_JDATE_NUM = re.compile(r"Date\s+of\s+(?:Judg(?:e)?ment|Order|Decision)s?\s*[:\-]?\s*(\d{1,2})[.\-/](\d{1,2})[.\-/](\d{4})\b", re.I)


# English names of well-known Acts and topics -> the Bengali words the site's search needs
# (Acts from 1987 on have Bengali titles and text only).
_EN_BN = {
    "money laundering": "মানিলন্ডারিং",
    "digital security": "ডিজিটাল নিরাপত্তা",
}
# Acts the site still lists without a status but a later Act replaced (stated in that Act's preamble).
_SUPERSEDED = {
    "886": "repealed: replaced by the Money Laundering Prevention Act, 2012 (id 1088), whose "
           "preamble repeals the existing law",
}


# --------------------------------------------------------------------------- #
class Bangladesh(Jurisdiction):
    code = "bd"
    name = "Bangladesh"
    languages = ("en", "bn")
    aliases = ("bangladesh", "bgd", "people's republic of bangladesh", "laws of bangladesh",
               "supreme court of bangladesh")
    sources = (
        Source(
            name="Laws of Bangladesh (bdlaws.minlaw.gov.bd), Legislative and Parliamentary Affairs Division",
            url=LAWS,
            covers=("legislation",),
            licence="unknown: no terms of use or licence; page footer 'Copyright © 2019, Legislative "
                    "and Parliamentary Affairs Division'",
            commercial_use=None,
            ai_use=None,    # no robots.txt, no AI/TDM clause
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~20 requests (2026-11)",
            terms_url="",
        ),
        Source(
            name="Supreme Court of Bangladesh (supremecourt.gov.bd) – Judgments and Orders",
            url=f"https://{SC_HOST}/web/?page=judgments.php&menu=00&div_id=1&type_id=5",
            covers=("caselaw",),
            licence="unknown: no terms of use, copyright or licence statement on the site",
            commercial_use=None,
            ai_use=None,    # robots.txt is 404 on both hosts; no AI/TDM clause
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~10 requests (2026-11)",
            terms_url="",
        ),
    )
    caselaw_filters = {
        "division": "appellate | high_court (default: both)",
        "kind": "judgments (default) | orders",
        "parties": "party name or part of it",
        "case_number": "case number only, e.g. '32'",
        "year": "case year, e.g. '2019'",
    }
    legislation_filters = {
        "search_in": "title (default: words in the short title) | text (free text in sections) | "
                     "act_no (Roman Act number, e.g. 'IX') | year (Act year, e.g. '1872')",
    }
    min_interval = {LAWS_HOST: 1.0, SC_HOST: 1.0, SC_DOC_HOST: 1.0}
    notes = ("Legislation: consolidated Acts, Ordinances and President's Orders from the official "
             "Laws of Bangladesh site (English for older laws, Bengali from 1987). Case law: Supreme "
             "Court judgments and orders (PDF) searched by description, parties or case number.")
    gaps = (
        "Subordinate courts and tribunals: not researched yet",
        ("Full-text search of Supreme Court judgments: the site searches description, parties and "
         "case number only"),
        "Scanned Supreme Court PDFs: scans only, no text (no OCR here)",
        "Statutory instruments, rules and regulations (SROs): not researched yet",
    )
    samples = {
        "caselaw_query": "bail",
        "decision_id": "3618580_Death_Reference_1-No.32of2019.pdf",
        "legislation_query": "contract",
        "law_id": "26",          # The Contract Act, 1872 (Act No. IX of 1872)
        "provision": "10",
    }

    # ------------------------------------------------------------------ legislation
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        q = _http.clean(query)
        if not q:
            raise BadRequest("Give a query: words of the short title, or set search_in.")
        where = str((filters or {}).get("search_in") or "title").strip().lower()
        types = {"title": "2", "text": "1", "act_no": "3", "year": "4"}
        if where not in types:
            raise BadRequest(f"search_in must be one of {', '.join(types)}; got {where!r}.")
        limit, page = max(1, int(limit)), max(1, int(page))
        start = (page - 1) * limit
        cut = ""
        orig = q
        if where in ("title", "text") and q.isascii():
            bn = next((v for k, v in _EN_BN.items() if k in q.lower()), "")
            if bn:
                q = bn
        if where == "title" and re.search(r"['\u2019]", q):
            # the site matches the phrase against titles that hold invisible characters inside
            # "People's"; cut the query at the apostrophe so such titles are found
            q, cut = re.split(r"['\u2019]", q, 1)[0].strip(), q
        items, total = [], None
        for sp in range(start // SITE_PAGE + 1, (start + limit - 1) // SITE_PAGE + 2):
            key = (q, where, sp)
            got = _search_cache.get(key)
            if got is None:
                r = await _http.get(f"{LAWS}/search.html", params={"q": q, "type": types[where], "page": sp})
                if r.status_code != 200:
                    raise SourceError(_http.error("bdlaws.minlaw.gov.bd", "search failed", r.status_code), r.status_code)
                got = _http.lru_put(_search_cache, key, self._parse_search(_decode(r)), 32)
            rows, total = got
            base = (sp - 1) * SITE_PAGE
            items += [h for i, h in enumerate(rows, base) if start <= i < start + limit]
            if len(rows) < SITE_PAGE:
                break
        squash = lambda x: re.sub(r"[\s,.\u200b-\u200d]+", "", x).lower()
        if where == "title" and not items and len(q.split()) > 1:
            # the site matches the phrase literally, so 'মানি লন্ডারিং' misses the title
            # 'মানিলন্ডারিং ...': search the longest word, keep titles that hold all words run together
            word = max(q.split(), key=len)
            for sp in (1, 2):
                key = (word, where, sp)
                got = _search_cache.get(key)
                if got is None:
                    r = await _http.get(f"{LAWS}/search.html", params={"q": word, "type": "2", "page": sp})
                    if r.status_code != 200:
                        raise SourceError(_http.error("bdlaws.minlaw.gov.bd", "search failed", r.status_code), r.status_code)
                    got = _http.lru_put(_search_cache, key, self._parse_search(_decode(r)), 32)
                items += [h for h in got[0] if squash(q) in squash(h.title)]
                if len(got[0]) < SITE_PAGE:
                    break
            total = len(items)
            items = items[start:start + limit]
        note = ("Ids are the site's Act ids (not Act numbers). Free-text hits (search_in=text) are "
                "one per matching section, so an Act can repeat." if where == "text" else
                "Ids are the site's Act ids (not Act numbers); the official number is in the TOC/text.")
        if q != orig and not cut:
            note += (f" The English query {orig!r} was searched as the Bengali {q!r}, because Acts "
                     "from 1987 on have Bengali titles and text.")
        for h in items:
            if h.id in _SUPERSEDED:
                h.status = _SUPERSEDED[h.id]
        if cut:
            note += f" The query was cut at the apostrophe and searched as {q!r}."
        if where == "title" and not items:
            note += (" Title search matches the exact phrase in the short title, and Acts from 1987 on "
                     "have Bengali titles, so an English title such as 'Digital Security Act' finds "
                     "nothing: search the Bengali title (e.g. 'ডিজিটাল নিরাপত্তা আইন') or a shorter "
                     "phrase. Free text (search_in=text) is Bengali for those Acts too.")
        return Results(items=items, total=total if total is not None else (len(items) or 0), note=note)

    @staticmethod
    def _parse_search(page: str):
        m = re.search(r"\d+\s+to\s+\d+\s+of\s+(\d+)", page)
        total = int(m[1]) if m else 0
        root = LH.fromstring(page)
        rows = []
        for res in root.xpath("//div[@id='searchtext']//div[contains(@class,'result')]"):
            a = res.find(".//h3/a")
            if a is None:
                continue
            href = (a.get("href") or "").split("?")[0]
            am = re.match(r"/act-(\d+)", href)
            if not am:
                continue
            title = _http.clean(a.text_content())
            p = res.find(".//p")
            snippet = _http.clean(p.text_content()) if p is not None else ""
            rows.append(LawHit(id=am[1], title=title, type="", number="",
                               date="", snippet=snippet[:300], url=f"{LAWS}{href}"))
        return rows, total

    async def get_legislation_toc(self, id):
        aid = _act_id(id)
        a = await _act(aid)
        return Toc(id=aid, title=f"{a['title']} ({a['number']})" if a["number"] else a["title"],
                   url=f"{LAWS}/act-{aid}.html", entries=[e for e, _ in a["entries"]])

    async def get_legislation_provision(self, id, provision):
        aid = _act_id(id)
        a = await _act(aid)
        want = _norm(str(provision))
        if not want:
            raise BadRequest("Give a section label as the TOC shows it, e.g. '10', '19A' or '১৫'.")
        rows = [(e, href) for e, href in a["entries"] if e.provision and _norm(e.provision) == want and href]
        if not rows:  # a section inside a repealed range, e.g. '80' in '76-123'
            for e, href in a["entries"]:
                m = re.fullmatch(r"(\d+)-(\d+)", _norm(e.provision))
                if m and want.isdigit() and int(m[1]) <= int(want) <= int(m[2]) and href:
                    rows = [(e, href)]
                    break
        if not rows:
            raise NotFound(f"{a['title']} has no section {provision!r}; see get_legislation_toc.")
        parts, notes = [], {}
        for _, href in rows[:12]:
            root = LH.fromstring(await _get_laws(href, f"section {provision} of Act {aid}"))
            notes.update(_footnotes(root))
            sec = root.xpath("//section[contains(@class,'bg-striped')]")
            parts.append(_rows_md(sec[0] if sec else root, chapters=False))
        text = "\n\n".join(p for p in parts if p)
        label = rows[0][0].provision
        fn = _notes_md(notes, text)
        return Provision(law_id=aid, law_title=a["title"], provision=label,
                         text=f"## Section {label}\n\n{text}" + (f"\n\n{fn}" if fn else ""),
                         url=f"{LAWS}{rows[0][1]}")

    async def get_legislation_text(self, id):
        aid = _act_id(id)
        root = LH.fromstring(await _get_laws(f"/act-details-{aid}.html", f"Act {aid}"))
        notes = _footnotes(root)
        title, number, date = _act_header(root)
        if not title:
            raise SourceError(f"bdlaws.minlaw.gov.bd Act {aid}: no title on the full-text page")
        pre = root.xpath("//div[contains(@class,'lineremove')]")
        parts = []
        for el in pre[:1]:
            t = _md(el)
            if t:
                parts.append(t)
        body = root.xpath("//section[contains(@class,'bg-striped')]")
        parts.append(_rows_md(body[0] if body else root))
        text = "\n\n".join(p for p in parts if p)
        fn = _notes_md(notes, text)
        meta = {k: v for k, v in (("Number", number), ("Date", date)) if v}
        for a in root.xpath("//td[contains(@class,'act-up-files')]//a"):
            meta[_http.clean(a.text_content()) or "File"] = LAWS + a.get("href", "")
        return LawText(id=aid, title=title, text=text + (f"\n\n## Footnotes\n\n{fn}" if fn else ""),
                       url=f"{LAWS}/act-details-{aid}.html", as_of=_http.today(), metadata=meta)

    # ------------------------------------------------------------------ case law
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        f = {k: _http.clean(v) for k, v in (filters or {}).items() if _http.clean(v)}
        q = _http.clean(query)
        div = f.get("division", "").lower()
        if div and div not in DIVISIONS:
            raise BadRequest(f"division must be appellate or high_court; got {div!r}.")
        kind = f.get("kind", "judgments").lower()
        if kind not in KINDS:
            raise BadRequest(f"kind must be judgments or orders; got {kind!r}.")
        if "year" in f and not re.fullmatch(r"\d{4}", f["year"]):
            raise BadRequest(f"year must be four digits, e.g. 2019; got {f['year']!r}.")
        if not (q or f.get("parties") or f.get("case_number")):
            raise BadRequest("The Supreme Court search needs a query (searched in the short "
                             "description), or a parties or case_number filter.")
        key = (q, kind, div, f.get("parties", ""), f.get("case_number", ""), f.get("year", ""))
        rows = _search_cache.get(key)
        if rows is None:
            rows = await self._sc_search(q, kind, div, f)
            _http.lru_put(_search_cache, key, rows, 32)
        limit = max(1, int(limit))
        start = (max(1, int(page)) - 1) * limit
        miss = ("" if rows else "No description matched. The court's site cannot search the text of "
                "judgments, so a topic that appears only in the judgment (e.g. 'money laundering' for "
                "a bail ruling under that Act) is not found by it: try 'bail' or another word the "
                "court's description would use, or the case_number and year filters. ")
        return Results(items=rows[start:start + limit], total=len(rows),
                       note=miss + "Query searches the court's short description of each case (use the "
                            "parties filter for names; case-insensitive, and a phrase with no match is retried word by "
                            "word), so the count is description matches, not every ruling on "
                            "the topic. The year filter is one case year at a time (no range): run one "
                            "search per year; an empty year simply has no description match. The listing "
                            "gives the upload date only (shown as 'Uploaded'), not the decision date; "
                            "rows are roughly newest upload first, Appellate Division before High Court.")

    async def _sc_search(self, q, kind, div, f) -> list[DecisionHit]:
        """The court's description search is case-sensitive and matches the phrase literally, so
        run the query in a few letter cases, and when a multi-word phrase finds nothing, search its
        first meaningful word and keep descriptions that hold every meaningful word."""
        async def run(term):
            out, seen = [], set()
            cases = dict.fromkeys([term, term.lower(), term[:1].upper() + term[1:].lower(), term.title()]) if term else {"": 0}
            for t in cases:
                for d in ([div] if div else ["appellate", "high_court"]):
                    code, label = DIVISIONS[d]
                    r = await _http.post(SC_LIST, data={
                        "div_id": code, "type_id": KINDS[kind], "case_number": f.get("case_number", ""),
                        "year": f.get("year", ""), "case_type_id": "", "parties": f.get("parties", ""),
                        "short_desc": t})
                    if r.status_code != 200:
                        raise SourceError(_http.error("supremecourt.gov.bd", "search failed", r.status_code), r.status_code)
                    out += [h for h in _sc_rows(r.text, label) if h.id not in seen and not seen.add(h.id)]
            return out
        rows = await run(q)
        words = [w for w in re.findall(r"[\w.]+", q) if w.lower() not in _STOP]
        if not rows and len(words) > 1:
            rows = [h for h in await run(words[0])
                    if all(w.lower() in _sc_meta[h.id]["Short description"].lower() for w in words[1:])]
        return rows

    async def get_decision(self, id):
        s = str(id).strip()
        if s.startswith("http"):
            s = unquote(urlsplit(s).path.rsplit("/", 1)[-1])
        if not _DOC_ID.match(s):
            raise BadRequest("Use the PDF file name from search_caselaw, e.g. "
                             "'3618580_Death_Reference_1-No.32of2019.pdf', or its supremecourt.gov.bd URL.")
        url = SC_DOCS + quote(s)
        r = await _http.get(url)
        if r.status_code == 404:
            raise NotFound(f"supremecourt.gov.bd has no document {s}.")
        if r.status_code != 200 or not r.content.startswith(b"%PDF"):
            raise SourceError(_http.error("supremecourt.gov.bd", "document fetch failed", r.status_code), r.status_code)
        try:
            text = _http.pdf_text(r.content)
        except Exception:
            text = ""
        meta = dict(_sc_meta.get(s, {}))
        head = text[:3000]
        court = meta.pop("court", "")
        if not court:
            court = (f"{SC}, Appellate Division" if "APPELLATE DIVISION" in head.upper() else
                     f"{SC}, High Court Division" if "HIGH COURT DIVISION" in head.upper() else SC)
        case = meta.pop("case_number", "")
        if not case:
            # lead heading only: stop at the "(From the ... passed by ...)" line, which names the impugned case
            m = _CASE_NO.search(re.split(r"^\s*\(\s*From\b", head, maxsplit=1, flags=re.M | re.I)[0])
            case = _http.clean(m[1]) if m else ""
        title = meta.pop("title", "") or f"{court} {case or s}"
        date = ""   # only the decision's own date; "judgment and order dated ..." is the impugned order
        m = _JDATE.search(text[:15000])
        if m:
            date = _http.en_date(f"{m[2]} {m[1]}, {re.sub(r'\s', '', m[3])}")
        elif (m := _JDATE_NUM.search(text[:15000])) and 1 <= int(m[2]) <= 12 and 1 <= int(m[1]) <= 31:
            date = f"{m[3]}-{int(m[2]):02d}-{int(m[1]):02d}"
        if not text or len(text) < 200:
            text = ("The court publishes this document only as a scanned PDF (no text layer), "
                    f"so no text can be returned here. Read it at: {url}")
        extra = {}
        if len(_BIJOY.findall(text)) > 20:
            text, clean = _bijoy_text(text)
            extra["Note"] = ("Parts of this PDF are Bengali typed in an old Bijoy font; the Bengali lines "
                             "were converted to Unicode automatically, so check wording that matters against "
                             "the PDF." + ("" if clean else " Some lines could not be converted and still show "
                             "as unreadable garbage (e.g. 'Rvwgb' for 'জামিন'); read those in the PDF itself."))
        return Decision(id=s, title=title, text=text, url=url, court=court, date=date,
                        case_number=case, metadata={k: v for k, v in meta.items() if v} | extra | {"PDF": url})
