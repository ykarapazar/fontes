"""Seychelles: recent judgments from the Judiciary of Seychelles website (judiciary.sc) and
Acts, S.I.s and Bills as published in the Official Gazette (gazette.sc).

Gotchas this code encodes:
  * judiciary.sc (WordPress) lists its decisions on ONE page, /resources/court-decisions/
    (~0.3 MB, TablePress tables per court: Constitutional Court, Supreme Court criminal and
    civil; the Court of Appeal table is empty). Columns: case name, main case number,
    related application, media neutral citation, decision date, bench, decision type,
    keywords. Coverage 2025 on (~200 rows, checked 2026-11-06). Search filters that one
    page in memory (cached 1 h). Dates come as "20 January 2026", "24-Jan-25" or an Excel
    serial ("45839" = 2025-07-01).
  * Decision id = the media neutral citation, e.g. "[2026] SCSC 4" (SCSC Supreme Court,
    SCCC Constitutional Court, SCCA Court of Appeal). The text is the linked PDF; most are
    scans with a text layer added by the court, so lines can come out of order on page 1
    and some words are mangled. A few PDFs have no text layer at all (SourceError).
  * robots.txt disallows /imunify-bot-check (an Imunify360 bot-trap link in the footer):
    never followed. A bot-check page instead of the listing raises SourceError.
  * gazette.sc (Drupal) keeps the last ~5 years (2020 on) of Acts, S.I.s, Bills and gazette
    issues as PDFs, as enacted / as gazetted, not consolidated. /s?type=&search=&year=&no=
    is a GET view, 20 rows a page (`page` 0-based), "Displaying 1 - 20 of N" gives the total.
    robots.txt disallows /search/ (Drupal core), not /s.
  * Law id = "Act 14 of 2026", "SI 69 of 2026", "Bill 17 of 2026". Rows show the file size,
    which is checked before any PDF is downloaded (bad ids never reach a download).
  * judiciary.sc/seychelles-law/ links the Constitution (Cap 42, Government Printer 2010
    edition, revised up to August 2018; id "Constitution") and the Penal, Civil, Criminal
    Procedure and Civil Procedure Codes as Laws.Africa PDFs (CC BY 4.0, "Legislation as at …",
    outstanding amendments named in the header); id = the PDF file name without ".pdf",
    e.g. "penal-code". The page is read live (cached 6 h), so new uploads show up.
    These texts are parsed by their ARRANGEMENT / Contents list: the body starts where the
    first label comes round again. The Constitution writes "115.A(1)" for article 115A, and
    the Civil Code's articles sit inside the Act's Schedule (provision "Schedule").
  * SeyLII (seylii.org, now Lexum Decisia) is not used: its terms say "Scraping and bulk
    downloading from this website is strictly prohibited".
"""
from __future__ import annotations

import datetime
import html as _h
import re
import time
from urllib.parse import urlencode

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (
    Decision,
    DecisionHit,
    LawHit,
    LawText,
    Provision,
    Results,
    Toc,
    TocEntry,
)

JHOST = "www.judiciary.sc"
JBASE = f"https://{JHOST}"
DECISIONS = f"{JBASE}/resources/court-decisions/"
GHOST = "www.gazette.sc"
GBASE = f"https://{GHOST}"
GPER_PAGE = 20
MAX_PDF = 20_000_000  # bytes; judgment and act PDFs seen are 0.4-7 MB

_COURT_CODES = {"SCSC": "Supreme Court", "SCCC": "Constitutional Court", "SCCA": "Court of Appeal"}
_COURT_FILTER = {"supreme": "SCSC", "constitutional": "SCCC", "appeal": "SCCA"}
_CIT = re.compile(r"(?i)^\s*\[?\s*(\d{4})\s*\]?\s*(SCSC|SCCC|SCCA)\s*(\d{1,4})\s*$")

_TYPES = {"act": "act", "acts": "act", "si": "si", "s.i.": "si", "sis": "si",
          "statutory instrument": "si", "regulations": "si", "bill": "bill", "bills": "bill"}
_TYPE_WORD = {"act": "Act", "si": "SI", "bill": "Bill"}
_LAW_ID = re.compile(r"(?i)^\s*(act|s\.?\s?i\.?|bill)\s*(?:no\.?)?\s*(\d{1,4})\s*(?:of|/|\s)\s*(\d{4})\s*$")

_cache: dict = {}
_MONTHS = {m: i for i, m in enumerate(("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug",
                                         "sep", "oct", "nov", "dec"), 1)}


def _unesc(s: str) -> str:
    return _http.clean(_h.unescape(re.sub(r"<[^>]+>", " ", s or "")))


def _date(s: str) -> str:
    s = _http.clean(s)
    try:
        if re.fullmatch(r"\d{5}", s):  # Excel serial date
            return (datetime.date(1899, 12, 30) + datetime.timedelta(days=int(s))).isoformat()
        m = re.fullmatch(r"(\d{1,2})(?:st|nd|rd|th)?[\s-]+([A-Za-z]{3,9})[\s-]+(\d{2}|\d{4})", s)
        if m and m[2][:3].lower() in _MONTHS:
            y = int(m[3]) + (2000 if len(m[3]) == 2 else 0)
            return datetime.date(y, _MONTHS[m[2][:3].lower()], int(m[1])).isoformat()
    except ValueError:
        pass
    return ""


def _norm_cit(raw: str) -> str:
    m = _CIT.match(raw or "")
    if not m:
        raise BadRequest(f"decision id {raw!r}: use the neutral citation from search_caselaw, "
                         "e.g. '[2026] SCSC 4' or '[2025] SCCC 6'")
    return f"[{m[1]}] {m[2].upper()} {int(m[3])}"


def _row_warning(title: str, date: str, url: str) -> str:
    """The site's own data can disagree with itself: the date in the case name, or in the PDF
    file name, differs from the Date column (or the row links another case's PDF)."""
    msgs = []
    m = re.search(r"\((\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})\)\s*$", title)
    if m and _date(m[1]) and _date(m[1]) != date:
        msgs.append(f"the case name says {m[1]} but the list's Date column says {date}")
    f = re.search(r"/(\d{2})(\d{2})(\d{4})-", url)
    if f and f"{f[3]}-{f[2]}-{f[1]}" != date:
        msgs.append(f"the PDF file name starts with {f[1]}-{f[2]}-{f[3]}, not the listed date {date}")
    return _warn_text(msgs)


def _title_date(title: str, date: str, url: str) -> str:
    """Show one date in the citation line: when the PDF file name agrees with the Date column
    but the date in the case name does not, the name's date is replaced by the listed one."""
    m = re.search(r"\((\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})\)\s*$", title)
    f = re.search(r"/(\d{2})(\d{2})(\d{4})-", url)
    if not (m and date and _date(m[1]) and _date(m[1]) != date
            and f and f"{f[3]}-{f[2]}-{f[1]}" == date):
        return title
    d = datetime.date.fromisoformat(date)
    return f"{title[:m.start()]}({d.day} {d.strftime('%B %Y')})"


def _warn_text(msgs: list[str]) -> str:
    if not msgs:
        return ""
    return ("judiciary.sc's own data is inconsistent (" + "; ".join(msgs) + "); check the date "
            "and that the PDF is this case before citing")


_NUM = re.compile(r"(?i)\b([A-Z]{1,4})\s*(\d{1,4})\s*(?:of|/)\s*(\d{4})\b")


def _other_case_pdf(number: str, date: str, url: str) -> bool:
    """True when the PDF file name (e.g. '23052025-ca30_2021-...') carries a case number the row
    does not list and a date other than the listed one: the row links another case's PDF."""
    f = re.search(r"/(\d{2})(\d{2})(\d{4})-([a-z]{1,4})(\d{1,4})_(\d{4})-", url, re.I)
    nums = {(a.lower(), int(b), c) for a, b, c in _NUM.findall(number)}
    return bool(f and nums and f"{f[3]}-{f[2]}-{f[1]}" != date
                and (f[4].lower(), int(f[5]), f[6]) not in nums)


_NC_DATE = re.compile(r"Neutral Citation:[^\n]*\n?[^\n]*?(\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]{3,9}\s+\d{4})")


def _decision_rows(html: str) -> list[dict]:
    out, seen = [], set()
    for table in re.findall(r"(?s)<table[^>]*tablepress[^>]*>(.*?)</table>", html):
        for row in re.findall(r"(?s)<tr[^>]*>(.*?)</tr>", table):
            cells = {int(n): c for n, c in re.findall(r'(?s)<td class="column-(\d+)">(.*?)</td>', row)}
            if not cells:
                continue
            vals = [_unesc(cells.get(i, "")) for i in range(1, 9)]
            cit = vals[3]
            link = re.search(r"""href=['"](https://www\.judiciary\.sc/wp-content/uploads/[^'"]+\.pdf)['"]""",
                             row, re.I)
            m = _CIT.match(cit)
            if not (m and link and vals[0]):
                continue
            cid = _norm_cit(cit)
            if cid in seen:  # same citation listed twice (2025 tables repeat some rows)
                continue
            seen.add(cid)
            out.append({"id": cid, "title": _title_date(vals[0], _date(vals[4]), link[1]), "number": vals[1],
                        "related": "" if vals[2] in ("", "N/A") else vals[2],
                        "date": _date(vals[4]), "bench": vals[5], "type": vals[6],
                        "summary": vals[7], "court": _COURT_CODES[m[2].upper()], "url": link[1],
                        "warn": _row_warning(vals[0], _date(vals[4]), link[1]),
                        "wrong_pdf": _other_case_pdf(vals[1], _date(vals[4]), link[1])})
    out.sort(key=lambda r: r["date"], reverse=True)
    return out


async def _pdf(url: str, size: int | None, what: str) -> str:
    if size is None:
        h = await _http.request("HEAD", url)
        if h.status_code != 200:
            raise SourceError(f"PDF for {what} failed", h.status_code)
        size = int(h.headers.get("content-length") or 0)
    if size > MAX_PDF:
        raise SourceError(f"PDF for {what} is {size // 1_000_000} MB; too large to read here. "
                          f"Open it directly: {url}", "too large")
    r = await _http.get(url)
    if r.status_code != 200 or not r.content.startswith(b"%PDF"):
        raise SourceError(f"PDF for {what} failed", r.status_code)
    text = _http.pdf_text(r.content)
    if not text:
        raise SourceError(f"PDF for {what} has no text layer (scanned); open {url}", "no text")
    return text


_NEWPARA = re.compile(r"""^(?:\[\d{1,3}\]|\(\w{1,6}\)|\d{1,3}[A-Z]?\.\s|[“"‘]|PART\b|_{3,})""")


def _paras(lines: list[str]) -> str:
    """PDF lines (wrapped) -> markdown paragraphs."""
    out: list[str] = []
    cur, prev = "", ""
    for ln in lines:
        ln = ln.strip()
        if not ln or re.fullmatch(r"\d{1,4}", ln):
            continue
        if not cur or _NEWPARA.match(ln) or len(prev) < 50 or re.search(r"[.:;–—]$", prev):
            if cur:
                out.append(cur)
            cur = ln
        elif re.search(r"[A-Za-z]-$", cur):
            cur += ln
        else:
            cur += " " + ln
        prev = ln
    if cur:
        out.append(cur)
    return "\n\n".join(re.sub(r"^([#>*+])", r"\\\1", p) for p in out)


# ---------- gazette legislation ----------

_HDR = re.compile(r"(?i)SUPPLEMENT TO OFFICIAL GAZETTE|\[\s*\d{1,2}(?:st|nd|rd|th)?\s+\w+,?\s+\d{4}\s*\]\s*\d*$")


def _strip_headers(text: str) -> list[str]:
    """Drop each page's running header (short title, 'SUPPLEMENT TO OFFICIAL GAZETTE',
    '[24 August 2026] 153')."""
    out: list[str] = []
    for page in text.split("\n\n"):
        lines = page.split("\n")
        k = max((i for i, ln in enumerate(lines[:4]) if _HDR.search(ln)), default=-1)
        out += lines[k + 1:] + [""]
    return out


_SEC = re.compile(r"^(\d{1,3})([A-Z]{0,2})\.\s+(\S.*)$")
_ORD = "FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH|SEVENTH|EIGHTH|NINTH|TENTH"
_SCHED = re.compile(rf"(?i)^(?:({_ORD})\s+)?SCHEDULE(?:\s+[A-Z0-9]{{1,3}})?$")
_ARTICLE = re.compile(r"^Article\s+(\d{1,4}(?:-\d{1,4})?)(?:\s+[–-]\s+\S.*)?$")  # Civil Code (inside its Schedule)
_PART = re.compile(r"^PART\s+[IVXLC]+[A-Z]?\b.{0,120}$")
_START = re.compile(r"(?i)^(BY THE PRESIDENT|ENACTED by|AN ACT\b|A BILL\b|NOW,? therefore|"
                    r"In exercise of the powers)")


def _is_heading(s: str) -> bool:
    return (0 < len(s) <= 100 and s[0].isupper() and not re.search(r"[.,;:—–-]$", s)
            and not _SEC.match(s) and not s.startswith("("))


def _add_article(blocks: list[dict], s: str) -> bool:
    """A Civil Code 'Article N' line inside the Schedule starts an article block; the heading
    line just before it (e.g. 'Delicts and quasi-delicts') is lifted off the previous article."""
    m = _ARTICLE.match(s)
    if not m:
        return False
    prev = blocks[-1]["lines"]
    head = ""
    while prev and not prev[-1].strip():
        prev.pop()
    if blocks[-1]["kind"] == "article" and prev and _is_heading(prev[-1].strip()):
        head = prev.pop().strip()
    blocks.append({"kind": "article", "label": m[1], "lines": [s],
                   "title": f"Article {m[1]} – {head}" if head else f"Article {m[1]}"})
    return True


def _parse_law(text: str) -> list[dict]:
    lines = _strip_headers(text)
    start = 0
    arr = next((i for i, ln in enumerate(lines) if "ARRANGEMENT OF" in ln.upper()), None)
    if arr is not None:
        start = next((i for i in range(arr, len(lines)) if _START.match(lines[i].strip())), arr)
    blocks = [{"kind": "preamble", "label": "", "title": "", "lines": lines[:start]}]
    last, in_sched = 0, False
    for ln in lines[start:]:
        s = ln.strip()
        m = _SCHED.match(s)
        if m and last:
            in_sched = True
            label = f"{m[1].capitalize()} Schedule" if m[1] else "Schedule"
            blocks.append({"kind": "schedule", "label": label, "title": s, "lines": []})
            continue
        if in_sched and _add_article(blocks, s):
            continue
        if not in_sched:
            if _PART.match(s):
                blocks.append({"kind": "heading", "label": "", "title": s, "lines": []})
                continue
            m = _SEC.match(s)
            if m and (int(m[1]) == last + 1 or (m[2] and int(m[1]) == last)):
                last = int(m[1])
                prev = blocks[-1]["lines"]
                head = ""
                while prev and re.fullmatch(r"\s*(st|nd|rd|th)?\s*", prev[-1]):
                    prev.pop()  # blank lines and stray superscript ordinals
                if prev and _is_heading(prev[-1].strip()):
                    head = prev.pop().strip()
                label = f"{m[1]}{m[2]}"
                blocks.append({"kind": "section", "label": label,
                               "title": f"{label}. {head}" if head else f"{label}.",
                               "lines": [s]})
                continue
        blocks[-1]["lines"].append(ln)
    return blocks


def _block_md(b: dict) -> str:
    if b["kind"] in ("section", "article"):
        return f"### {b['title']}\n\n" + _paras(b["lines"])
    if b["kind"] in ("heading", "schedule"):
        return f"## {_http.clean(b['title'])}\n\n" + _paras(b["lines"])
    return _paras(b["lines"])


def _norm_provision(p: str) -> str:
    s = _http.clean(p)
    m = re.fullmatch(rf"(?i)(?:the\s+)?(?:({_ORD})\s+)?schedule", s)
    if m:
        return f"{m[1].capitalize()} Schedule" if m[1] else "Schedule"
    m = re.fullmatch(r"(?i)schedule\s*(\d{1,2})", s)
    if m:
        return f"Schedule {int(m[1])}"
    m = re.fullmatch(r"(?i)(?:sections?|sec\.?|s\.?|articles?|art\.?|regulations?|reg\.?|r\.?|clause|cl\.?|§)?\s*"
                     r"(\d{1,4})\s*([A-Za-z]{0,2})\.?", s)
    return f"{m[1]}{m[2].upper()}" if m else s


def _gazette_rows(html: str) -> tuple[list[dict], int | None]:
    total = re.search(r"Displaying\s+\d+\s*-\s*\d+\s+of\s+(\d+)", html)
    rows = []
    for href, label, size in re.findall(
            r'(?s)views-field-nothing"><span class="field-content"><div><a href="([^"]+)"[^>]*>(.*?)</a></div>'
            r"\s*<div>(.*?)</div>", html):
        label = _unesc(label)
        if not href.startswith(GBASE + "/sites/default/files/"):
            continue
        m = re.match(r"(?i)^(Act|S\.I\.|Bill)\s+(\d{1,4})\s+(\d{4})\s*-\s*(.*)$", label)
        if not m:
            continue  # gazette issues and anything else
        kind = {"act": "act", "s.i.": "si", "bill": "bill"}[m[1].lower()]
        title = re.sub(r"(?i)^(?:(?:Act|SI|S\.I\.|Bill)\s*(?:No\.?)?\s*\d{1,4}\s*(?:-\s*)?(?:\d{4})?\s*-\s*)+",
                       "", m[4]).strip(" .") or m[4]
        sz = re.search(r"([\d.]+)\s*(KB|MB|GB|bytes)", _unesc(size), re.I)
        mult = {"kb": 1e3, "mb": 1e6, "gb": 1e9, "bytes": 1}
        rows.append({"id": f"{_TYPE_WORD[kind]} {int(m[2])} of {m[3]}", "kind": kind, "title": title,
                     "url": _h.unescape(href),
                     "size": int(float(sz[1]) * mult[sz[2].lower()]) if sz else None})
    return rows, int(total[1]) if total else (0 if not rows else None)


# ---------- Laws of Seychelles page (judiciary.sc): Constitution and the main codes ----------

LAWS_PAGE = f"{JBASE}/seychelles-law/"
CONSTITUTION_SLUG = "the-constitution-of-the-republic-of-seychelles-cap42"
_LAWS_TTL = 6 * 3600


def _laws_rows(html: str) -> list[dict]:
    """judiciary.sc/seychelles-law/ -> rows {id (PDF file slug), title, url}; 'Constitution' is
    the id of the 1993 Constitution (Cap 42)."""
    rows, seen = [], set()
    for url, title in re.findall(r'href="(https://www\.judiciary\.sc/wp-content/uploads/[^"]+?\.pdf)"'
                                 r"[^>]*>([^<]+)<", html):
        slug = url.rsplit("/", 1)[1][:-4]
        if slug in seen or not title.strip():
            continue
        seen.add(slug)
        rows.append({"id": "Constitution" if slug == CONSTITUTION_SLUG else slug,
                     "title": _http.clean(_unesc(title)), "url": url})
    return rows


def _law_status(r: dict) -> str:
    return ("superseded: the 1993 Constitution (id 'Constitution') is the one in force"
            if "constitution-of-seychelles-1979" in r["url"] else "")


def _la_meta(text: str) -> dict:
    """Laws.Africa PDF header: 'Legislation as at …' and the outstanding-amendments note;
    the 2010 edition Constitution says 'REVISED UP TO …'."""
    head = text[:1500]
    meta = {}
    if m := re.search(r"Legislation as at ([^\n]+)", head):
        meta["Legislation as at"] = m[1].strip()
    if m := re.search(r"(?s)Note: (There are outstanding amendments.*?)\nThere may have been", head):
        meta["Note"] = _http.clean(m[1])
    if m := re.search(r"\((REVISED UP TO [A-Z]+ \d{4})\)", head):
        meta["Revision"] = m[1].capitalize()
    return meta


_LA_DROP = re.compile(r"^(?:By Laws\.Africa and contributors|\d{4} ED\]|\d{1,4}$)")
_SCHED_ANY = re.compile(rf"(?i)^(?:({_ORD})\s+)?SCHEDULE\s*(\d{{1,2}})?(?![A-Za-z])")


def _label_re(lab: str) -> str:
    """'115' -> '115.' ; '115A' -> '115A.', '115.A', '115.A(' (the 2010 Constitution writes both)."""
    n, suf = re.fullmatch(r"(\d+)([A-Z]*)", lab).groups()
    return rf"{n}\.\s?(?=[\s(]|$)" if not suf else rf"{n}\.?\s?{suf}\.?\s?(?=[\s(]|$)"


def _ordered_parse(text: str, mark: str) -> list[dict]:
    """Revised text whose ARRANGEMENT / Contents list gives the section labels and titles in
    order (Laws.Africa PDFs on SeyLII; the 2010 edition Constitution on judiciary.sc). The body
    starts where the first label comes round again; each later label starts a section."""
    lines = text.split("\n")
    head = next((i for i, ln in enumerate(lines) if ln.strip() in mark.split("|")), None)
    if head is None:
        return _parse_law(text)
    hdr = lines[head - 1].strip() if mark == "Contents" and head else ""   # page header, e.g. "Penal Code (Chapter 158)"
    toc: list[tuple[str, str]] = []
    body = None
    for i in range(head + 1, len(lines)):
        m = re.match(r"^(\d{1,3}[A-Z]{0,3})\.\s*(.*?)(?:\s*\.{3,}\s*\d*)?\s*$", lines[i].strip())
        if not m:
            continue
        if toc and m[1] == toc[0][0]:
            body = i
            break
        if not toc or m[1] != toc[-1][0]:
            toc.append((m[1], m[2]))
    if body is None or not toc:
        return _parse_law(text)
    start = body
    while start > head + 1 and (re.match(r"(?i)^(PART|CHAPTER)\s+[\dIVXLC]", lines[start - 1].strip())
                                or (lines[start - 1].strip().isupper() and len(lines[start - 1]) < 80)):
        start -= 1
    blocks = [{"kind": "preamble", "label": "", "title": "", "lines": lines[:start]}]
    titles, p = dict(toc), 0
    for ln in lines[start:]:
        s = ln.strip()
        if _LA_DROP.match(s) or (hdr and s in (hdr, f"{hdr} Seychelles")):
            continue
        nxt = [toc[k][0] for k in (p, p + 1) if k < len(toc)]
        hit = next(((n, m) for n in nxt if (m := re.match(_label_re(n), s))), None)
        if hit:
            lab = hit[0]
            p = [x[0] for x in toc].index(lab, p) + 1
            t = titles[lab]
            rest = s[hit[1].end():].strip()
            blocks.append({"kind": "section", "label": lab, "title": f"{lab}. {t}".strip(),
                           "lines": [] if rest == t else [rest]})
            continue
        if blocks[-1]["kind"] in ("schedule", "article") and _add_article(blocks, s):
            continue
        m = _SCHED_ANY.match(s)
        if m and p >= len(toc) and len(s) < 120 and not re.search(r"\b(?:of|to|in) the\b", s) \
                and (mark == "Contents" or "SCHEDULE" in s):   # Constitution: " Schedule 7" is a margin note
            label = (f"{m[1].capitalize()} Schedule" if m[1] else
                     f"Schedule {int(m[2])}" if m[2] else "Schedule")
            blocks.append({"kind": "schedule", "label": label, "title": s, "lines": []})
            continue
        if p < len(toc) and re.match(r"(?i)^(PART|CHAPTER)\s+[\dIVXLC]+[A-Z]?\b", s) and len(s) < 120:
            blocks.append({"kind": "heading", "label": "", "title": s, "lines": []})
            continue
        b = blocks[-1]
        if b["kind"] == "heading" and not b["lines"] and s and len(s) < 80 \
                and not re.search(r"[.;:,]$", s) and not re.match(r"\d", s):
            b["title"] += " – " + s   # heading title on its own line
            continue
        b["lines"].append(ln)
    return blocks


class Seychelles(Jurisdiction):
    code = "sc"
    name = "Seychelles"
    languages = ("en",)
    aliases = ("syc", "seychelles")
    sources = (
        Source("Judiciary of Seychelles website (judiciary.sc): Decisions from the Courts", DECISIONS,
               covers=("caselaw",),
               licence="'Copyright © 2022 Seychelles Judiciary | All Rights Reserved'; no terms of "
                       "use page; judgments are public court records",
               commercial_use=None,
               ai_use=None,  # robots.txt has no AI/TDM signal; no terms page
               auth="none",
               rate_limit="unknown; no Crawl-delay in robots.txt; 2 s spacing, no 429 seen in "
                          "~10 requests (2026-11-06)",
               terms_url=f"{JBASE}/robots.txt",
               warning="Judgment PDFs as posted by the Judiciary ('All Rights Reserved'); the text "
                       "layer of scanned PDFs may contain recognition errors - check the PDF."),
        Source("Official Gazette of Seychelles (gazette.sc): Acts, S.I.s and Bills", GBASE,
               covers=("legislation",),
               licence="'© Copyright 2020-2026 Government of Seychelles'; 'The Gazette is available "
                       "online, free of charge, to any person' (About the Official Gazette)",
               commercial_use=None,
               ai_use=None,  # robots.txt has no AI/TDM signal; no terms page
               auth="none",
               rate_limit="unknown; no Crawl-delay in robots.txt; 1 s spacing, no 429 seen in "
                          "~15 requests (2026-11-06)",
               terms_url=f"{GBASE}/about-official-gazette"),
        Source("Judiciary of Seychelles website (judiciary.sc): Laws of Seychelles (Constitution "
               "and main codes)", LAWS_PAGE,
               covers=("legislation",),
               licence="Constitution: Government Printer 2010 edition, site 'All Rights Reserved'; "
                       "the codes are Laws.Africa PDFs: 'There is no copyright on the legislative "
                       "content of this document', PDF copy CC BY 4.0",
               commercial_use=None,  # CC BY 4.0 for the codes; not stated for the Constitution PDF
               ai_use=None,  # robots.txt has no AI/TDM signal; no terms page
               auth="none",
               rate_limit="unknown; no Crawl-delay in robots.txt; 2 s spacing, 7 requests "
                          "(2026-11-10), no 429",
               terms_url=f"{JBASE}/robots.txt",
               warning="Revised texts with an 'as at' date: the Constitution is revised up to "
                       "August 2018 (later amendment Acts are on gazette.sc); the codes are "
                       "Laws.Africa consolidations posted by the Judiciary, some with outstanding "
                       "amendments named in the metadata."),
    )
    caselaw_filters = {
        "court": "supreme, constitutional or appeal",
        "year": "decision year, e.g. 2026 (list starts 2025)",
    }
    legislation_filters = {
        "type": "act, si (statutory instruments) or bill (Gazette, 2020 on), or revised "
                "(the Constitution and codes on judiciary.sc/seychelles-law); default all",
        "year": "year of the instrument, e.g. 2025 (site keeps 2020 on)",
    }
    min_interval = {JHOST: 2.0, GHOST: 1.0}
    notes = ("Case law: Supreme Court and Constitutional Court decisions listed on judiciary.sc, "
             "2025 on (Court of Appeal list empty). Legislation: the Constitution (revised to "
             "2018) and the Penal, Civil, Criminal Procedure and Civil Procedure Codes as posted "
             "on judiciary.sc; Acts, S.I.s and Bills as gazetted, 2020 on, not consolidated.")
    gaps = (
        ("Court of Appeal decisions: judiciary.sc's Court of Appeal table is empty; not published "
         "online"),
        ("Judgments before 2025: not listed on judiciary.sc (SeyLII is non-official and its "
         "terms prohibit scraping)"),
        ("Acts before 2020 other than the Constitution and the four codes on judiciary.sc: not "
         "published by an official host (legalaffairs.gov.sc does not resolve); SeyLII has "
         "consolidated Acts but its terms say 'Scraping and bulk downloading from this website "
         "is strictly prohibited', so it is not used"),
        ("Constitution amendments after August 2018: not merged into the judiciary.sc text; the "
         "amendment Acts from 2020 are on gazette.sc"),
        ("Employment Act, Companies Act and other principal Acts before 2020: not on any official "
         "host, so a title search for them finds only later amendments, regulations and Bills"),
        "Gazette items before 2020: not published online (paid request by email only)",
        "Judgment PDFs with no text layer: scans only, no text",
    )
    samples = {
        "caselaw_query": "constitution",
        "decision_id": "[2026] SCCC 4",
        "legislation_query": "trusts",
        "law_id": "Act 14 of 2026",
        "provision": "2",
    }

    # ---- case law ----

    async def _decisions(self) -> list[dict]:
        hit = _cache.get("decisions")
        if hit and time.monotonic() - hit[0] < 3600:
            return hit[1]
        r = await _http.get(DECISIONS)
        if r.status_code != 200 or "tablepress" not in r.text:
            raise SourceError("judiciary.sc decisions page failed (or a bot check was served)",
                              r.status_code)
        rows = _decision_rows(r.text)
        if not rows:
            raise SourceError("judiciary.sc decisions page had no parsable rows", "no rows")
        _cache["decisions"] = (time.monotonic(), rows)
        return rows

    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        q = _http.clean(query)
        rows = await self._decisions()
        if _CIT.match(q):
            cid = _norm_cit(q)
            rows = [r for r in rows if r["id"] == cid]
        elif q:
            words = q.lower().split()
            rows = [r for r in rows if all(
                w in " ".join((r["title"], r["number"], r["related"], r["id"], r["bench"], r["type"],
                               r["summary"])).lower() for w in words)]
        if filters.get("court"):
            c = _http.clean(filters["court"]).lower().replace("court of ", "").replace(" court", "")
            if c not in _COURT_FILTER:
                raise BadRequest(f"court {filters['court']!r}: use supreme, constitutional or appeal")
            rows = [r for r in rows if r["id"].split()[1] == _COURT_FILTER[c]]
        if filters.get("year"):
            y = str(filters["year"]).strip()
            if not re.fullmatch(r"(19|20)\d\d", y):
                raise BadRequest(f"year {filters['year']!r}: use a 4-digit year, e.g. 2026")
            rows = [r for r in rows if r["date"].startswith(y)]
        limit = max(1, min(int(limit), 50))
        start = (max(1, int(page)) - 1) * limit
        items = [DecisionHit(id=r["id"], title=r["title"], court=r["court"], date=r["date"],
                             case_number=r["number"],
                             snippet=(f"WARNING: {r['warn']}. " if r["warn"] else "")
                             + ("WARNING: judiciary.sc links another case's PDF to this row, so no "
                                "judgment text is available; Source is the official list page. "
                                if r["wrong_pdf"] else "")
                             + r["summary"][:300],
                             url=DECISIONS if r["wrong_pdf"] else r["url"])
                 for r in rows[start:start + limit]]
        note = ("judiciary.sc list only (2025 on); all words must match name, case number, "
                "citation or keywords (not subjects or judgment text: try a party name or one keyword); "
                "newest first. Some judgment PDFs are scans with no text "
                "layer: get_decision then fails, open the Source URL.")
        if filters.get("court") and _COURT_FILTER[c] == "SCCA":
            note = ("Court of Appeal decisions are not published online on judiciary.sc (its "
                    "Court of Appeal table is empty), so 0 hits does not mean there are none. ") + note
        return Results(items=items, total=len(rows), note=note)

    async def get_decision(self, id):
        cid = _norm_cit(id)
        if ("dec", cid) in _cache:
            return _cache[("dec", cid)]
        row = next((r for r in await self._decisions() if r["id"] == cid), None)
        if not row:
            raise NotFound(f"no decision {cid} in the judiciary.sc list (it starts in 2025)")
        if row["wrong_pdf"]:
            raise SourceError(f"{cid} ({row['title']}): judiciary.sc links another case's PDF to this "
                              f"row ({row['url'].rsplit('/', 1)[1]}), so the real judgment text is "
                              "not available from the official list. Not returned, to avoid citing "
                              "the wrong case", "wrong PDF")
        text = await _pdf(row["url"], None, cid)
        meta = {k: v for k, v in (("Bench", row["bench"]), ("Decision type", row["type"]),
                                  ("Related case", row["related"])) if v}
        d = Decision(id=cid, title=row["title"], text=_paras(text.split("\n")), url=row["url"],
                     court=row["court"], date=row["date"], case_number=row["number"],
                     summary=row["summary"], metadata=meta)
        msgs = []
        nc = _NC_DATE.search(text)
        if nc and _date(nc[1]):
            meta["Date in the judgment's neutral citation line"] = _date(nc[1])
            if _date(nc[1]) != row["date"]:
                msgs.append(f"the judgment's own neutral citation line gives {_date(nc[1])}")
            elif row["warn"] and "case name says" in row["warn"]:
                meta["Date note"] = ("the judgment text agrees with the list's Date column, so the "
                                     "date in the case name is probably the hearing date; cite "
                                     f"{row['date']}")
        if row["warn"] or msgs:
            meta["Source data warning"] = row["warn"] or _warn_text(msgs)
        return _http.lru_put(_cache, ("dec", cid), d, 8)

    # ---- legislation ----

    async def _gsearch(self, params: dict) -> tuple[list[dict], int | None]:
        r = await _http.get(f"{GBASE}/s?" + urlencode(params))
        if r.status_code != 200 or "views-exposed-form-repository-search" not in r.text:
            raise SourceError("gazette.sc search failed", r.status_code)
        return _gazette_rows(r.text)

    @staticmethod
    def _type(v) -> str:
        t = _TYPES.get(_http.clean(v).lower())
        if not t:
            raise BadRequest(f"type {v!r}: use act, si or bill")
        return t

    @staticmethod
    def _norm_law_id(raw: str) -> tuple[str, str, str]:
        m = _LAW_ID.match(raw or "")
        if not m:
            raise BadRequest(f"law id {raw!r}: use the id from search_legislation, e.g. "
                             "'Act 14 of 2026', 'SI 69 of 2026' or 'Bill 17 of 2026'")
        kind = {"act": "act", "bill": "bill"}.get(m[1].lower(), "si")
        return kind, str(int(m[2])), m[3]

    async def _laws(self) -> list[dict]:
        hit = _cache.get("laws")
        if hit and time.monotonic() - hit[0] < _LAWS_TTL:
            return hit[1]
        r = await _http.get(LAWS_PAGE)
        rows = _laws_rows(r.text) if r.status_code == 200 else []
        if not any(x["id"] == "Constitution" for x in rows):
            raise SourceError("judiciary.sc Laws of Seychelles page failed or changed layout",
                              r.status_code)
        _cache["laws"] = (time.monotonic(), rows)
        return rows

    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        params = {"type": "All", "search": "", "year": "", "no": ""}
        q = _http.clean(query)
        revised = _http.clean(filters.get("type") or "").lower() == "revised"
        limit = max(1, min(int(limit), GPER_PAGE))
        start = (max(1, int(page)) - 1) * limit
        local = []
        if revised or not (_LAW_ID.match(q) or filters.get("type") or filters.get("year")):
            words = q.lower().split()
            local = sorted((r for r in await self._laws()
                            if all(w in f"{r['title']} {r['id']}".lower() for w in words)),
                           key=lambda r: r["id"] != "Constitution")  # the current Constitution first
            if revised and filters.get("year"):
                raise BadRequest("the revised texts have no year filter")
        if revised:
            return Results(items=[LawHit(id=r["id"], title=r["title"], type="Revised text",
                                         status=_law_status(r), url=r["url"]) for r in local[start:start + limit]],
                           total=len(local),
                           note="Laws of Seychelles page on judiciary.sc: the Constitution and "
                                "codes as revised/consolidated (each text gives its 'as at' date).")
        head = [LawHit(id=r["id"], title=r["title"], type="Revised text", status=_law_status(r),
                       url=r["url"])
                for r in local[start:start + limit]]
        if len(head) == limit:
            return Results(items=head, total=None,
                           note="Revised texts from judiciary.sc first, then the Official Gazette.")
        start, limit = max(0, start - len(local)), limit - len(head)
        if _LAW_ID.match(q):
            kind, no, year = self._norm_law_id(q)
            params.update(type=kind, no=no, year=year)
        else:
            params["search"] = q
        if filters.get("type"):
            params["type"] = self._type(filters["type"])
        if filters.get("year"):
            y = str(filters["year"]).strip()
            if not re.fullmatch(r"(19|20)\d\d", y):
                raise BadRequest(f"year {filters['year']!r}: use a 4-digit year, e.g. 2025")
            params["year"] = y
        if not (params["search"] or params["year"] or params["no"] or params["type"] != "All"):
            if head:
                return Results(items=head, total=len(head), note="Revised texts from judiciary.sc.")
            raise BadRequest("give title words (e.g. 'trusts'), an id like 'Act 14 of 2026', "
                             "or a type/year filter")
        p0 = start // GPER_PAGE
        rows, total = await self._gsearch({**params, "page": p0})
        rows = rows[start % GPER_PAGE:]
        if len(rows) < limit and total and total > (p0 + 1) * GPER_PAGE:
            rows += (await self._gsearch({**params, "page": p0 + 1}))[0]
        items = head + [LawHit(id=r["id"], title=r["title"], type={"act": "Act", "si": "S.I.",
                                                                   "bill": "Bill"}[r["kind"]],
                               number=r["id"], url=r["url"]) for r in rows[:limit]]
        if params["type"] == "All" or local:
            total = None  # the source's count includes gazette issues, which are left out
        return Results(items=items, total=total,
                       note=("Revised texts from judiciary.sc first (Constitution, codes), then "
                             if local else "") + "Official Gazette, 2020 on; texts as enacted "
                            "(not consolidated); newest first. Acts passed before 2020 (e.g. the "
                            "Employment Act) are not online at an official host, so not finding "
                            "one here does not mean it does not exist.")

    async def _law(self, raw_id: str) -> dict:
        rid = _http.clean(raw_id)
        if not _LAW_ID.match(rid):
            key = "Constitution" if rid.lower() in ("constitution", CONSTITUTION_SLUG) else rid
            if ("law", key) in _cache:
                return _cache[("law", key)]
            row = next((r for r in await self._laws() if r["id"].lower() == key.lower()), None)
            if not row:
                raise BadRequest(f"law id {raw_id!r}: use the id from search_legislation, e.g. "
                                 "'Constitution', 'penal-code', 'Act 14 of 2026' or 'SI 69 of 2026'")
            text = await _pdf(row["url"], None, row["id"])
            mark = "ARRANGEMENT OF ARTICLES" if row["id"] == "Constitution" else "Contents"
            doc = {"id": row["id"], "title": row["title"], "url": row["url"],
                   "blocks": _ordered_parse(text, mark),
                   "meta": {"Type": "Revised text (judiciary.sc)", **_la_meta(text)}}
            return _http.lru_put(_cache, ("law", row["id"]), doc, 6)
        kind, no, year = self._norm_law_id(raw_id)
        lid = f"{_TYPE_WORD[kind]} {no} of {year}"
        if ("law", lid) in _cache:
            return _cache[("law", lid)]
        rows, _ = await self._gsearch({"type": kind, "search": "", "year": year, "no": no})
        row = next((r for r in rows if r["id"] == lid), None)
        if not row:
            raise NotFound(f"no {lid} on gazette.sc (it keeps 2020 on; try search_legislation)")
        text = await _pdf(row["url"], row["size"], lid)
        doc = {"id": lid, "title": row["title"], "url": row["url"], "blocks": _parse_law(text),
               "meta": {"Type": {"act": "Act", "si": "S.I.", "bill": "Bill"}[kind]}}
        return _http.lru_put(_cache, ("law", lid), doc, 6)

    async def get_legislation_toc(self, id):
        doc = await self._law(id)
        entries = []
        for b in doc["blocks"]:
            if b["kind"] == "heading":
                entries.append(TocEntry(title=_http.clean(b["title"]), level=0))
            elif b["kind"] in ("section", "article"):
                entries.append(TocEntry(title=b["title"], level=1, provision=b["label"]))
            elif b["kind"] == "schedule":
                entries.append(TocEntry(title=b["label"], level=0, provision=b["label"]))
        return Toc(id=doc["id"], title=doc["title"], url=doc["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        doc = await self._law(id)
        label = _norm_provision(provision)
        kinds = (("article",) if re.match(r"(?i)\s*art", provision) else ()) + ("section", "schedule", "article")
        b = next((b for k in kinds for b in doc["blocks"] if b["kind"] == k
                  and b["label"].lower() == label.lower()), None)
        if not b:
            raise NotFound(f"no provision {provision!r} in {doc['id']}: use a label from "
                           "get_legislation_toc (e.g. '5' for section 5, 'Schedule')")
        return Provision(law_id=doc["id"], law_title=doc["title"], provision=b["label"],
                         text=_block_md(b), url=doc["url"])

    async def get_legislation_text(self, id):
        doc = await self._law(id)
        text = "\n\n".join(t for t in (_block_md(b) for b in doc["blocks"]) if t.strip())
        return LawText(id=doc["id"], title=doc["title"], text=text, url=doc["url"],
                       metadata=doc["meta"])
