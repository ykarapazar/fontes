"""Mauritius: judgments of the subordinate courts and recent legislation, both from the
Supreme Court of Mauritius website (supremecourt.govmu.org, the Judiciary's own site), the
Constitution and consolidated Acts (Attorney General's Revised Laws), Acts as passed 2009-2023
(National Assembly), and Privy Council judgments in Mauritian appeals (Find Case Law, through the gb adapter's code).

Gotchas this code encodes:
  * Privy Council (the final court): UKPC judgments on Find Case Law, Nov 2009 on, full-text
    search, filtered to Mauritian appeals by title "(Mauritius)" or header "From the Supreme
    Court of Mauritius" (bs.jcpc_hits, shared). Id: the neutral citation, "[2026] UKPC 29".
  * One Drupal site. `/judgment-search` and `/legislation-search` are plain GET views
    (robots.txt disallowed only /search/, /admin/, /user/... until 2026-11-10, when it
    changed to `Disallow: /` for every agent). Since then the source is needs_permission:
    off (subordinate-court judgments, 2024+ library) unless the operator permits "mu". Ten rows a
    page, `page` is 0-based, no hit count is printed (only a "last page" pager link).
  * The public judgment collection holds the subordinate courts only (Intermediate,
    Industrial, District courts, Court of Rodrigues, Children's Court), from 2020 on.
    Supreme Court judgments (SCJ) are not in it (2025 SCJ 100 → no row; years before 2020
    → no rows, checked 2026-11-06).
  * Judgment id = the source's document number, e.g. "2026 INT 291" (year, court code,
    number). `field_document_number=` is an exact match, so get_decision looks the id up
    with one small search, then reads the text-layer PDF under /system/files/judgment/.
  * `/legislation-search` renders five views on one page (acts, bills, proclamations,
    government notices = "regulation", reprints), each with its own pager slot in
    `page=a,b,c,d,e`. `title=` filters all five; `field_document_number=` is exact.
    The library starts in 2024 (nothing for 1960-2023, checked 2026-11-06) and holds the
    texts as enacted / as gazetted, not consolidated. These pages are ~0.5-0.8 MB each.
  * Law id = the document number, e.g. "Act No. 10 of 2026", "GN No. 175 of 2026".
    Act PDFs have an "ARRANGEMENT OF SECTIONS" list, then "An Act" and the body; sections
    are "N. Heading" lines in ascending order, Parts/Sub-Parts are headings, schedules
    follow. GN regulations have no headings: "1. These regulations may be cited as...".
  * Revised Laws (Attorney General's Office, SharePoint): the anonymous REST list
    `_api/web/lists/getbytitle('Documents')/items` gives every file under "Laws of Mauritius/"
    (~170 KB JSON); "A-Z Acts/" holds ~690 consolidated PDFs, some twice under different file
    names (deduped by squashed title, newest kept). File names are the only titles, some
    squashed ("SUGARINDUSTRYLABOURWELFAREFUNDACTNo47of1974"), so title words match with spaces
    ignored. Id = the path under "Laws of Mauritius/" without ".pdf". The Constitution is
    "Constitutions/THE CONSTITUTION, GN 54 of 1968" (Issue 1, amendments to 2011; Parts II-III
    of that volume, related laws and case notes, are cut). The AG search API returns 500.
    PDFs repeat a running header ("Revised Laws of Mauritius" / "C35 – 1 [Issue 7]"), dropped;
    the body starts where section 1 comes round again after the ARRANGEMENT list.
  * Acts as passed 2009-2023: National Assembly page `acts-2/`, one wpDataTable per year
    ("for year 2025"; the 2009 table has no year, cells say "Act No 22 of 2009"); 2018 is
    missing there, so 2018 comes from the AG list (ACTS/ACTS2018/ACTnn18.pdf, no titles).
  * MauritiusLII (Peachjam) is not used: robots.txt disallows /judgments/ and sets
    `Content-Signal: ai-input=no` (checked 2026-11-06).
"""
from __future__ import annotations

import collections
import html as _h
import re
import time
from urllib.parse import quote, unquote, urlencode

from .. import _http
from .bs import JCPC_ALIASES, JCPC_SOURCE, is_jcpc_id, jcpc_decision, jcpc_hits
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError, permitted_codes
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

HOST = "supremecourt.govmu.org"
GATED = ("supremecourt.govmu.org is off: its robots.txt disallows all automated access "
         "(Disallow: /, since 2026-11-10). Subordinate-court judgments and the 2024+ legislation "
         "library need the Supreme Court's permission (operator: permit 'mu').")
BASE = f"https://{HOST}"
PER_PAGE = 10

# court filter -> field_court id, labels as on /judgment-by-year (2026-11-06)
COURTS = {
    "intermediate": "80508", "industrial": "80507", "rodrigues": "80509",
    "children": "84703", "bail": "80554",
    "port louis 1": "86", "port louis 2": "87", "port louis 3": "80461",
    "black river": "88", "flacq": "80462", "grand port": "80463",
    "lower plaines wilhems": "80464", "riviere du rempart": "80465", "moka": "80466",
    "pamplemousses": "80467", "savanne": "80468", "upper plaines wilhems": "80469",
}
# court codes in document numbers seen with a known court (2026-11)
_CODES = {"INT": "Intermediate Court", "ROD": "Court of Rodrigues"}

# legislation view blocks: filter value -> (block name, pager slot, document-number word)
_TYPES = {
    "act": ("act", 0, "Act"), "bill": ("bill", 1, "Bill"),
    "proclamation": ("proclamation", 2, "Proclamation"),
    "gn": ("regulation", 3, "GN"), "reprint": ("reprint", 4, "Reprint"),
}
_LOCAL_TYPES = ("revised", "enacted")
_TYPE_ALIASES = {"consolidated": "revised", "constitution": "revised", "revised law": "revised",
                 "as passed": "enacted", "passed": "enacted", "regulation": "gn", "regulations": "gn", "acts": "act", "bills": "bill",
                 "government notice": "gn", "reprints": "reprint", "proclamations": "proclamation"}
_TYPE_NAMES = {"act": "Act", "bill": "Bill", "proclamation": "Proclamation",
               "regulation": "Government Notice", "reprint": "Reprint"}

_DEC_ID = re.compile(r"^\s*(\d{4})\s+([A-Za-z]{2,4}\d?)\s+(\d{1,5})\s*$")
_LAW_ID = re.compile(r"(?i)^\s*(act|gn|g\.n\.|bill|proclamation|reprint)\s*(?:no\.?)?\s*(\d{1,4})\s*"
                     r"(?:of|/)\s*(\d{4})\s*$")

# Attorney General's Office (SharePoint): Revised Laws PDFs, listed by the anonymous REST API
AG_HOST = "attorneygeneral.govmu.org"
AG = f"https://{AG_HOST}"
_AG_LIST = (f"{AG}/_api/web/lists/getbytitle('Documents')/items"
            "?$select=FileRef,Modified&$top=5000")
_AG_DIR = "/Documents/Laws of Mauritius/"
CONSTITUTION_ID = "Constitutions/THE CONSTITUTION, GN 54 of 1968"   # Revised Laws issue, 2 MB
# National Assembly: Acts as passed, 2009 on, one page of wpDataTables (one table per year)
NA_HOST = "mauritiusassembly.govmu.org"
NA_ACTS = f"https://{NA_HOST}/mauritiusassembly/index.php/acts-2/"
_INDEX_TTL = 6 * 3600

_cache: dict = {}
_JCPC_MU = ("Mauritius", "From the Supreme Court of Mauritius")


# ---------- small parsers ----------

def _rows(html: str) -> list[str]:
    return re.findall(r"(?is)<tr>(.*?)</tr>", html)


def _file_url(row: str) -> str:
    m = re.search(r'\?file=([^"&]+)', row)
    if not m:
        return ""
    url = unquote(m[1]).split("#")[0]
    return url if url.startswith(BASE + "/system/files/") else ""


def _judgment_rows(html: str) -> list[dict]:
    out = []
    for row in _rows(html):
        title = re.search(r'document-title">(.*?)</span>', row, re.DOTALL)
        num = re.search(r"<li>([^<]*)</li>", row)
        url = _file_url(row)
        if not (title and num and url):
            continue
        by = re.search(r'delivered-by">(.*?)</span>', row, re.DOTALL)
        date = re.search(r'field-delivered-on[^>]*>\s*<a[^>]*>([^<]*)<', row)
        summ = re.search(r'(?s)views-field-field-summary"\s*>(.*?)</td>', row)
        out.append({"title": _http.clean(_unesc(title[1])), "number": _http.clean(num[1]),
                    "by": _http.clean(_unesc(re.sub(r"<[^>]+>", " ", by[1]))) if by else "",
                    "date": _http.iso_date(_http.clean(date[1])) if date else "",
                    "summary": _http.html_to_md(summ[1]) if summ else "", "url": url})
    return out


def _unesc(s: str) -> str:
    return _h.unescape(s or "")


def _law_blocks(html: str) -> dict[str, list[dict]]:
    """Legislation page -> {block name: [{title, number, url}]}."""
    parts = re.split(r'id="block-views-block-legislation-search-block-(\w+)"', html)
    out: dict[str, list[dict]] = {}
    for name, body in zip(parts[1::2], parts[2::2]):
        rows = []
        for row in _rows(body):
            cells = re.findall(r'class="openedDocument">(.*?)</a>', row, re.DOTALL)
            url = _file_url(row)
            if len(cells) < 2 or not url:
                continue
            rows.append({"title": _http.clean(_unesc(re.sub(r"<[^>]+>", " ", cells[0]))),
                         "number": _http.clean(_unesc(re.sub(r"<[^>]+>", " ", cells[1]))),
                         "url": url})
        out[name] = rows
    return out


def _court(number: str, by: str) -> str:
    code = number.split()[1] if len(number.split()) == 3 else ""
    if code in _CODES:
        return _CODES[code]
    if "Industrial Court" in by:
        return "Industrial Court"
    if "Intermediate Court" in by:
        return "Intermediate Court"
    if "District Magistrate" in by:
        return f"District Court ({code})" if code else "District Court"
    return f"Subordinate court ({code})" if code else ""


_NEWPARA = re.compile(r"""^(?:\(\w{1,6}\)|[a-z]\)|\d{1,3}[A-Z]?\.\s|[“"‘]|PART\b|Sub-Part\b|_{3,})""")


def _paras(lines: list[str]) -> str:
    """PDF lines (wrapped) -> markdown paragraphs. A paragraph ends after a short line or
    terminal punctuation; list items and quoted definitions start a new one."""
    out: list[str] = []
    cur, prev = "", ""
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue  # page break: may fall mid-sentence
        if re.fullmatch(r"\d{1,4}", ln):  # bare page number
            continue
        new = (not cur or _NEWPARA.match(ln) or len(prev) < 55
               or re.search(r"[.:;–—]$|[^\w]-$", prev))
        if new:
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
    return "\n\n".join(_md_safe(p) for p in out)


def _md_safe(p: str) -> str:
    return re.sub(r"^([#>*+])", r"\\\1", p)


# ---------- legislation text ----------

_WORD = re.compile(r"[^\W\d_]+")


def _despace(text: str) -> str:
    """Repair PDF extraction damage using the document's own vocabulary: stray spaces inside
    words ('rec ognised', 'Mauritiu s', '( c)') and line-end hyphens inside split words
    ('associa-/tion'). A split is joined only when the joined word occurs elsewhere in the
    document and one part is a fragment; real compounds ('non-citizen') are left alone."""
    from collections import Counter
    cnt = Counter(w.lower() for w in _WORD.findall(text))

    def frag(t: str) -> bool:
        t = t.lower()
        return (len(t) == 1 and t not in "aiày") or cnt[t] <= 5

    def dehyph(m):
        x, y = m[1], m[2]
        ok = cnt[(x + y).lower()] or (frag(x) and x.lower() not in _PREFIXES) or (y.lower() in _SUFFIXES and cnt[x.lower()] > 2)
        return x + y if ok and not cnt[(x + "-" + y).lower()] else m[0].replace("\n", "")

    text = re.sub(r"([^\W\d_]{2,})-\n([^\W\d_]+)", dehyph, text)

    def join_line(ln: str) -> str:
        toks = ln.split(" ")
        out = []
        for t in toks:
            m = re.fullmatch(r"([^\W\d_]+)(\W*)", t)
            if out and m and _WORD.fullmatch(out[-1]):
                x, y = out[-1], m[1]
                j, lo = cnt[(x + y).lower()], min(cnt[x.lower()], cnt[y.lower()])
                if j and (frag(x) or frag(y) or (lo <= 60 and j >= 5 * lo)) \
                        and not (x.isupper() and len(x) > 1):
                    out[-1] = x + t
                    continue
            out.append(t)
        return " ".join(out)

    for _ in range(2):
        text = "\n".join(join_line(ln) for ln in text.split("\n"))
    text = re.sub(r"\(\s+(\w{1,4})\)", r"(\1)", text)
    return text


_PREFIXES = {"non", "re", "anti", "co", "ex", "pre", "sub", "self", "semi", "inter", "vice", "ultra",
             "cross", "counter", "half", "quasi", "pro", "de", "un", "in"}
_SUFFIXES = {"ing", "ed", "tion", "ment", "ly", "ness", "ance", "ence", "ions", "ings"}

_ORD = ("FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH|SEVENTH|SEVNTH|EIGHTH|NINTH|TENTH|ELEVENTH|"
        "TWELFTH")
_SCHED = re.compile(rf"(?i)^(?:({_ORD})\s+)?SCHEDULE(?:\s+[A-Z0-9]{{1,3}})?$")
_HEAD = re.compile(r"^(?:PART\s+[IVXLC]+[A-Z]?|Sub-Part\s+[A-Z]{1,2}|CHAPTER\s+[IVXLC]+[A-Z]?)\b.*$")
_SEC = re.compile(r"^(\d{1,4})([A-Z]{0,2})(\.)?\s+(\S.*)$")


def _parse_law(text: str) -> list[dict]:
    """Law text -> blocks {kind: preamble|heading|section|schedule, label, title, lines}."""
    lines = text.split("\n")
    start = 0
    arr = next((i for i, ln in enumerate(lines) if "ARRANGEMENT OF" in ln), None)
    if arr is not None:
        start = next((i for i in range(arr, len(lines)) if lines[i].strip() == "An Act"), None)
        if start is None:  # Revised Laws: the body starts where section 1 comes round again
            ones = [i for i in range(arr, len(lines)) if re.match(r"1\.?\s+\S", lines[i].strip())]
            start = ones[1] if len(ones) > 1 else arr
            while start > arr + 1 and _HEAD.match(lines[start - 1].strip()):
                start -= 1
    blocks = [{"kind": "preamble", "label": "", "title": "", "lines": lines[:start]}]
    last, last_suf, in_sched = 0, "", False
    for ln in lines[start:]:
        s = ln.strip()
        m = _SCHED.match(s)
        if m and last:
            in_sched = True
            label = f"{m[1].capitalize()} Schedule" if m[1] else "Schedule"
            if m[1] and m[1].upper() == "SEVNTH":
                label = "Seventh Schedule"
            blocks.append({"kind": "schedule", "label": label, "title": s, "lines": [ln]})
            continue
        if not in_sched:
            b = blocks[-1]
            if b["kind"] == "heading" and len(b["lines"]) == 1 and s and s == s.upper() \
                    and re.search(r"[A-Z]", s) and not _SEC.match(s) and not _HEAD.match(s):
                b["title"] += " " + s  # heading wrapped onto a second line
                continue
            if _HEAD.match(s) and len(s) < 140:
                blocks.append({"kind": "heading", "label": "", "title": s, "lines": [ln]})
                continue
            m = _SEC.match(s)
            if m:
                n, suf, dot = int(m[1]), m[2], m[3]
                ok = (n == last + 1 and (dot or not suf)) or (dot and n == last and suf > last_suf) \
                    or (dot and not suf and last + 1 < n <= last + 3)
                if ok:
                    last, last_suf = n, suf
                    rest = m[4]
                    rng = re.match(r"[–-]\s*(\d{1,4})([A-Z]{0,2})\.", rest)   # "49. – 101. —": repealed range
                    end = 0
                    if rng and int(rng[1]) > n:
                        last, last_suf, end = int(rng[1]), rng[2], int(rng[1])
                    title = rest if len(rest) <= 90 and not rest.endswith((".", ",", ";")) \
                        else (rest[:70].rsplit(" ", 1)[0] + " …")
                    blocks.append({"kind": "section", "label": f"{n}{suf}",
                                   "title": f"{n}{suf}. {title}", "lines": [ln], "end": end})
                    continue
        blocks[-1]["lines"].append(ln)
    return blocks


def _block_md(b: dict) -> str:
    if b["kind"] == "section":
        first, rest = b["lines"][0].strip(), b["lines"][1:]
        m = _SEC.match(first)
        body_first = m[4] if m else first
        if b["title"].endswith(body_first):  # a real heading line
            return f"### {b['title']}\n\n" + _paras(rest)
        return f"### {b['label']}.\n\n" + _paras([body_first] + rest)
    if b["kind"] in ("heading", "schedule"):
        return f"## {_http.clean(b['title'])}\n\n" + _paras(b["lines"][1:])
    return _paras(b["lines"])


def _norm_provision(p: str) -> str:
    s = _http.clean(p)
    m = re.fullmatch(rf"(?i)(?:the\s+)?(?:({_ORD})\s+)?schedule", s)
    if m:
        return f"{m[1].capitalize()} Schedule" if m[1] else "Schedule"
    m = re.fullmatch(r"(?i)(?:sections?|sec\.?|s\.?|ss\.?|regulations?|reg\.?|r\.?|§)?\s*"
                     r"(\d{1,4})\s*([A-Za-z]{0,2})\.?", s)
    if m:
        return f"{m[1]}{m[2].upper()}"
    return s


# ---------- Revised Laws (AG) and Acts as passed (National Assembly) ----------

def _squash(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _ag_title(stem: str) -> str:
    """File name -> title. Names come as 'COMPANIES ACT, No 15 of 2001', 'CompaniesActNo.15of2001',
    'Information and Communication Technologies Act-I9' or 'TOBACCOPRODUCTIONANDMARKETINGACT'."""
    t = re.sub(r"(?<=Act)I\d+$|-I\d+$", "", stem).strip()
    if " " not in t:
        t = re.sub(r"ACT(?=Cap\d|Cap$|No\d|$)", " ACT ", t).replace("Cap", " Cap ")
        t = re.sub(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])", " ", t)
        t = re.sub(r"(?<=[a-z])(No\.?|of)\s", r" \1 ", t)
        t = re.sub(r"(?<=[A-Z])(ACT|No)(?= \d|$)", r" \1", t)
    return re.sub(r"\s+", " ", t)


def _ag_items(rows: list[dict]) -> list[dict]:
    """SharePoint rows -> Revised Laws (A-Z Acts, deduped), the Constitution, and the 2018 Acts
    as passed (the only year the National Assembly page lacks)."""
    best: dict[str, dict] = {}
    out = []
    for x in rows:
        ref = x.get("FileRef") or ""
        if not (ref.startswith(_AG_DIR) and ref.lower().endswith(".pdf")):
            continue
        rel = ref[len(_AG_DIR):-4]
        stem = rel.rsplit("/", 1)[-1]
        url = AG + quote(ref)
        if rel == CONSTITUTION_ID:
            out.append({"id": rel, "title": "The Constitution of Mauritius (GN 54 of 1968)",
                        "type": "Constitution", "number": "GN 54 of 1968", "year": "1968",
                        "url": url, "key": "constitutionofmauritius"})
        elif rel.startswith("A-Z Acts/") and "constitution" not in stem.lower():
            title = _ag_title(stem)
            y = re.search(r"\b(1[89]\d\d|20\d\d)\b", title)
            item = {"id": rel, "title": title, "type": "Revised law", "number": "",
                    "year": y[1] if y else "", "url": url, "key": _squash(title),
                    "mod": x.get("Modified") or ""}
            k = _squash(re.sub(r"(?i)\bcap\b", "", title))
            if k not in best or item["mod"] > best[k]["mod"]:
                best[k] = item
        else:
            m = re.fullmatch(r"ACTS/ACTS2018/ACT(\d\d)18", rel)
            if m:
                n = int(m[1])
                out.append({"id": f"Act No. {n} of 2018", "title": f"Act No. {n} of 2018",
                            "type": "Act (as passed)", "number": f"Act No. {n} of 2018",
                            "year": "2018", "url": url, "key": f"actno{n}of2018"})
    return out + sorted(best.values(), key=lambda i: i["key"])


def _na_items(html: str) -> list[dict]:
    """National Assembly Acts page -> Acts as passed, 2009-2023 (2024 on: the Supreme Court
    library, which also has GNs)."""
    out = []
    for tb in re.findall(r"(?s)<table[^>]*wpDataTable[^>]*>(.*?)</table>", html):
        ty = re.search(r"for year\s+(\d{4})", re.sub(r"<[^>]+>", " ", tb))
        for row in re.findall(r"(?s)<tr[^>]*>(.*?)</tr>", tb):
            n = re.search(r">\s*Act\s+No\.?\s*(\d{1,3})(?:\s+of\s+(\d{4}))?\s*<", row)
            a = re.search(r'href="([^"]+\.pdf)"[^>]*data-link-text="([^"]*)"', row)
            y = (n[2] or (ty[1] if ty else "")) if n else ""
            if not (n and a and y) or int(y) >= 2024:
                continue
            title = _http.clean(_unesc(a[2]).replace("\u200b", ""))
            num = f"Act No. {int(n[1])} of {y}"
            out.append({"id": num, "title": title, "type": "Act (as passed)", "number": num,
                        "year": y, "url": a[1].replace("http://", "https://", 1),
                        "key": _squash(title)})
    return out


async def _index() -> list[dict]:
    hit = _cache.get("index")
    if hit and time.monotonic() - hit[0] < _INDEX_TTL:
        return hit[1]
    r = await _http.get(_AG_LIST, headers={"Accept": "application/json;odata=nometadata"})
    try:
        rows = r.json()["value"] if r.status_code == 200 else None
    except ValueError:
        rows = None
    if rows is None:
        raise SourceError("attorneygeneral.govmu.org document list failed", r.status_code)
    items = _ag_items(rows)
    r2 = await _http.get(NA_ACTS)
    if r2.status_code != 200 or "wpDataTable" not in r2.text:
        raise SourceError("mauritiusassembly.govmu.org Acts page failed", r2.status_code)
    items += _na_items(r2.text)
    items.sort(key=lambda i: (i["type"] == "Act (as passed)",
                              -int(i["year"]) if i["type"] == "Act (as passed)" else 0,
                              int(i["number"].split()[2]) if i["type"] == "Act (as passed)" else 0))
    _cache["index"] = (time.monotonic(), items)
    return items


_RUNNING = re.compile(r"^(?:[A-Z][A-Za-z0-9]{0,5}\s*[–-]\s*\d+[A-Z]?\s*\[Issue \d+\]|"
                      r"\[Issue \d+\]\s*[A-Z][A-Za-z0-9]{0,5}\s*[–-]\s*\d+[A-Z]?)$")


def _despace(text: str) -> str:
    """Repair stray spaces/hyphens the PDF text layer puts inside words ('rec ognised', 'with-out').
    Two fragments are joined only when the joined word occurs intact elsewhere in the same
    document and one fragment is a rare token or a lone letter (never 'in to' -> 'into')."""
    cnt = collections.Counter(re.findall(r"[A-Za-z]+", text))
    hyph = collections.Counter(re.findall(r"[A-Za-z]+-[a-z]+", text))

    def joinable(a, b):
        c = a + b
        if cnt[c] < 2:
            return False
        if c.lower() == "is":
            return len(a) == len(b) == 1 and a == "i"
        lone = any(len(x) == 1 and x not in "aAiI" for x in (a, b))
        return len(c) >= 3 and (lone or min(cnt[a], cnt[b]) <= max(3, cnt[c] // 4))

    def dehyphen(m):
        c = m[1] + m[3]
        return c + m[2] if cnt[c] and hyph[m[1] + "-" + m[3]] <= 1 else f"{m[1]}-{m[3]}{m[2]}"

    out = []
    for line in text.split("\n"):
        parts = re.findall(r"[A-Za-z]+|[^A-Za-z]+", line)
        res, i = [], 0
        while i < len(parts):
            cur = parts[i]
            i += 1
            if cur[0].isalpha() and not (res and res[-1][-1:] in "’'"):
                while i + 1 < len(parts) and parts[i] == " " and parts[i + 1][0].isalpha() \
                        and joinable(cur, parts[i + 1]):
                    cur += parts[i + 1]
                    i += 2
            res.append(cur)
        out.append("".join(res))
    return re.sub(r"\b([A-Za-z]+)-(\n)([a-z]+)\b", dehyphen, "\n".join(out))


def _strip_running(text: str) -> str:
    """Drop Revised Laws page headers ('Revised Laws of Mauritius' / 'C35 – 1 [Issue 7]')."""
    lines = text.split("\n")
    drop = set()
    for i, ln in enumerate(lines):
        if _RUNNING.match(ln.strip()):
            drop.add(i)
            if i and (i == 1 or not lines[i - 2].strip()) and len(lines[i - 1]) < 90:
                drop.add(i - 1)
    return "\n".join(ln for i, ln in enumerate(lines) if i not in drop)


class Mauritius(Jurisdiction):
    code = "mu"
    name = "Mauritius"
    languages = ("en", "fr")
    aliases = ("mus", "mauritius", "maurice")
    sources = (
        JCPC_SOURCE,
        Source("Supreme Court of Mauritius website (supremecourt.govmu.org): judgment search "
               "(subordinate courts) and legislation library",
               BASE,
               covers=("caselaw", "legislation"),
               licence="© Supreme Court of Mauritius; Terms and Conditions §3: material 'may be "
                       "reproduced free of charge in any format or medium provided it is reproduced "
                       "accurately and not used in a misleading context; and the source of the "
                       "material must be identified and the copyright status acknowledged'",
               commercial_use=None,   # free reproduction 'in any format or medium'; commerce not mentioned
               ai_use=None,           # robots.txt has no AI/TDM signal; terms silent
               auth="none",
               rate_limit="unknown; no Crawl-delay in robots.txt; 1 s spacing, no 429 seen in "
                          "~35 requests (2026-11-06)",
               terms_url=f"{BASE}/basic-page/4527",
               needs_permission=True,   # robots.txt `Disallow: /` for every agent since 2026-11-10
               warning="Personal use only: the site says it is 'maintained for your personal use and viewing'. "
                       "Reproduce accurately with attribution: '© Supreme Court of Mauritius'. "
                       "The site's texts are for convenience of reference; official versions are "
                       "in the Mauritius Reports / SCJ and the Government Gazette. "
                       "Currently OFF by default (robots.txt Disallow: / since 2026-11-10): "
                       "subordinate-court judgments and the 2024+ library are unavailable."),
        Source("Revised Laws of Mauritius, Attorney General's Office (attorneygeneral.govmu.org)",
               f"{AG}/Pages/Laws%20of%20Mauritius/A-Z%20Acts/ActsAZ.aspx",
               covers=("legislation",),
               licence="© Government of Mauritius; terms of use: copies may be made, but the texts "
                       "should not be published, disseminated or incorporated 'for commercial use "
                       "without the prior approval of the Solicitor General'",
               commercial_use=False,  # commercial use needs the Solicitor General's prior approval
               ai_use=None,           # no robots.txt (404); terms silent on AI/TDM
               auth="none",
               rate_limit="unknown; no robots.txt; one list request (SharePoint REST, ~170 KB, "
                          "cached 6 h) plus one PDF per law; 1 s spacing",
               terms_url=f"{AG}/Pages/Laws%20of%20Mauritius/Constitution/termofuse.aspx",
               warning="Non-commercial use only without the Solicitor General's prior approval. "
                       "The site's Revised Laws are updated to 30 June 2017 (some later issues); "
                       "the authoritative text is the printed Revised Laws. The PDF text layer of some laws "
                       "(the Constitution, bilingual codes) has stray spaces inside words: "
                       "check any quotation against the PDF."),
        Source("National Assembly of Mauritius (mauritiusassembly.govmu.org): Acts as passed",
               NA_ACTS,
               covers=("legislation",),
               licence="no reuse terms; disclaimer page only (accuracy not guaranteed, verify with "
                       "the relevant department)",
               commercial_use=None,
               ai_use=None,   # robots.txt path serves an HTML page (no robots rules)
               auth="none",
               rate_limit="unknown; one 2 MB page (cached 6 h) plus one PDF per Act; 1 s spacing",
               terms_url=f"https://{NA_HOST}/mauritiusassembly/index.php/disclaimer/"),
    )
    caselaw_filters = {
        "court": "jcpc (Privy Council, final court) or, off by default (needs the Supreme Court's "
                 "permission), one of: " + ", ".join(COURTS),
        "year": "delivery year, e.g. 2025 (Privy Council from 2009, subordinate courts from 2020)",
        "since": "first delivery year of a range running to today, e.g. 2022 (instead of year)",
    }
    legislation_filters = {
        "type": "revised (consolidated Revised Laws + Constitution, AG), enacted (Acts as passed "
                "2009-2023), or act, gn (government notices/regulations), bill, proclamation, "
                "reprint (Supreme Court library, 2024 on); default: revised + enacted first, "
                "then the 2024+ library",
        "year": "year of the instrument, e.g. 2025",
    }
    min_interval = {HOST: 1.0, "caselaw.nationalarchives.gov.uk": 0.3, AG_HOST: 1.0, NA_HOST: 1.0}
    notes = ("Case law: Privy Council (final court) judgments in Mauritian appeals, Nov 2009 on, full text, "
             "from Find Case Law (UK National Archives); subordinate courts (Intermediate, Industrial, "
             "District, Rodrigues, Children's Court), 2020 on, OFF by default (the source's robots.txt "
             "disallows all automated access since 2026-11-10; court=intermediate etc. fail unless the "
             "operator holds the Supreme Court's permission); no Supreme Court (SCJ) judgments are "
             "published online by an allowed source. "
             "Legislation: the Constitution and ~660 Acts as consolidated in the Revised Laws of "
             "Mauritius (Attorney General's Office; updated to June 2017, some later issues); Acts as "
             "passed 2009-2023 (National Assembly; 2018 from the AG); Acts, GNs, Bills, Proclamations "
             "and Reprints as enacted, 2024 on (Supreme Court library). Amendments after a Revised "
             "Laws issue are not merged: read the later amending Acts.")
    gaps = (
        ("Privy Council judgments before Nov 2009: only on BAILII (no API, forbids scraping); Find Case "
         "Law's UKPC collection starts 2009"),
        ("Privy Council country filter is heuristic (Find Case Law has no country field): title "
         "'(Mauritius)' or header 'From the Supreme Court of Mauritius'; a judgment with neither is "
         "missed (e.g. [2016] UKPC 30, [2015] UKPC 14 'From the Court of Appeal of Mauritius')"),
        "Supreme Court (SCJ) judgments: not published in the site's judgment collection (checked "
         "2026-11-06)",
        "Subordinate-court judgments before 2020: not published online on the site",
        ("Consolidated Acts: the AG's Revised Laws stop at 30 June 2017 for most Acts (a few "
         "later issues); later amendments are only in the amending Acts as passed; no official "
         "up-to-date consolidation online. Whether the AG's A-Z list holds every Act in force is "
         "unverified (~660 titles); title search only (AG search API returns 500)"),
        ("Acts as passed: the National Assembly tables miss some PDFs (rows without links); 2018 "
         "Acts from the AG list have no titles (number only); Acts as passed before 2009 not "
         "online (their text is in the Revised Laws)"),
        "MauritiusLII judgments: robots.txt disallows /judgments/ and sets Content-Signal ai-"
         "input=no",
    )
    samples = {
        "caselaw_query": "habeas corpus",
        "decision_id": "[2026] UKPC 29",
        "legislation_query": "companies",
        "law_id": "A-Z Acts/C/Companies Act, No. 15 of 2001",
        "provision": "4",
    }

    # ---- case law ----

    async def _jpage(self, params: dict, page0: int) -> str:
        r = await _http.get(f"{BASE}/judgment-search?" + urlencode({**params, "page": page0}))
        if r.status_code != 200 or "views-form-judgment-search-page-judgment-search" not in r.text:
            raise SourceError("supremecourt.govmu.org judgment search failed", r.status_code)
        return r.text

    def _year(self, v) -> str:
        y = str(v).strip()
        if not re.fullmatch(r"(19|20)\d\d", y):
            raise BadRequest(f"year {v!r}: use a 4-digit year, e.g. 2025")
        return y

    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        params: dict[str, str] = {}
        q = _http.clean(query)
        court = _http.clean(filters.get("court", "")).lower()
        since = self._year(filters["since"]) if filters.get("since") else ""
        if since and filters.get("year"):
            raise BadRequest("use either year (one year) or since (that year to today), not both")
        limit = max(1, min(int(limit), PER_PAGE))
        start = (max(1, int(page)) - 1) * limit
        jc: list[DecisionHit] = []
        if not _DEC_ID.match(q) and (not court or court in JCPC_ALIASES):
            year = self._year(filters["year"]) if filters.get("year") else ""
            jc = await jcpc_hits(*_JCPC_MU, q, year)   # Privy Council first
            if since:
                jc = [h for h in jc if h.date[:4] >= since]
        jnote = "Privy Council hits first (full-text search, all words, newest first, 2009 on). "
        if court in JCPC_ALIASES:
            return Results(items=jc[start:start + limit], total=len(jc), note=jnote.replace(" first", ""))
        if self.code not in permitted_codes():
            if _DEC_ID.match(q) or court:
                raise BadRequest(GATED + " Privy Council judgments remain: court=jcpc.")
            return Results(items=jc[start:start + limit], total=len(jc),
                           note=jnote.replace(" first", "") + GATED)
        items = jc[start:start + limit]
        limit, start = limit - len(items), max(0, start - len(jc))
        if _DEC_ID.match(q):
            params["field_document_number"] = self._norm_dec_id(q)
        elif q:
            params["search_inner"] = q
        if filters.get("court"):
            c = _http.clean(filters["court"]).lower().replace("-", " ")
            c = re.sub(r"\s*(district\s+)?court\b|\bdivision\b|\bst\b|\bnd\b|\brd\b|'s", "", c).strip()
            c = {"port louis 1st": "port louis 1"}.get(c, c)
            if c not in COURTS:
                raise BadRequest(f"court {filters['court']!r}: use one of {', '.join(COURTS)}")
            params["field_court"] = COURTS[c]
        if filters.get("year"):
            params["from_year"] = params["to_year"] = self._year(filters["year"])
        if since:
            params["from_year"], params["to_year"] = since, str(time.localtime().tm_year)
        if not params and not jc:
            raise BadRequest("give search words, a document number like '2026 INT 291', or a filter")
        if not params or not limit:
            return Results(items=items, total=None, note=jnote + "Then subordinate courts, 2020 on.")
        p0 = start // PER_PAGE
        html = await self._jpage(params, p0)
        rows = _judgment_rows(html)[start % PER_PAGE:]
        if len(rows) < limit and len(_judgment_rows(html)) == PER_PAGE and \
                f"page={p0 + 1}" in html.replace("&amp;", "&"):
            rows += _judgment_rows(await self._jpage(params, p0 + 1))
        items += [DecisionHit(id=r["number"], title=r["title"], court=_court(r["number"], r["by"]),
                              date=r["date"], case_number=r["number"], snippet=r["summary"][:300],
                              url=r["url"]) for r in rows[:limit]]
        return Results(items=items, total=None,
                       note=(jnote if jc else "")
                       + "Subordinate courts: 2020 on; full-text search; newest first.")

    @staticmethod
    def _norm_dec_id(raw: str) -> str:
        m = _DEC_ID.match(raw or "")
        if not m:
            raise BadRequest(f"decision id {raw!r}: use the id from search_caselaw, e.g. '2026 INT 291' "
                             "(subordinate courts) or '[2026] UKPC 29' (Privy Council)")
        return f"{m[1]} {m[2].upper()} {m[3]}"

    async def get_decision(self, id):
        if is_jcpc_id(id):
            return await jcpc_decision(id)
        did = self._norm_dec_id(id)
        if self.code not in permitted_codes():
            raise BadRequest(GATED)
        if ("dec", did) in _cache:
            return _cache[("dec", did)]
        html = await self._jpage({"field_document_number": did}, 0)
        row = next((r for r in _judgment_rows(html) if r["number"].upper() == did), None)
        if not row:
            raise NotFound(f"no judgment {did} on supremecourt.govmu.org (Supreme Court SCJ "
                           "judgments are not published there)")
        r = await _http.get(row["url"])
        if r.status_code != 200 or not r.content.startswith(b"%PDF"):
            raise SourceError(f"judgment PDF for {did} failed", r.status_code)
        text = _http.pdf_text(r.content)
        if not text:
            raise SourceError(f"judgment PDF for {did} has no text layer (scanned)", "no text")
        meta = {"Delivered by": row["by"]} if row["by"] else {}
        cause = re.search(r"(?im)^Cause Number:\s*(.+)$", text)
        if cause:
            meta["Cause number"] = _http.clean(cause[1])
        d = Decision(id=did, title=row["title"], text=_paras(text.split("\n")), url=row["url"],
                     court=_court(did, row["by"]), date=row["date"], case_number=did,
                     summary=row["summary"], metadata=meta)
        return _http.lru_put(_cache, ("dec", did), d, 8)

    # ---- legislation ----

    async def _lpage(self, params: dict) -> dict[str, list[dict]]:
        r = await _http.get(f"{BASE}/legislation-search?" + urlencode(params))
        blocks = _law_blocks(r.text) if r.status_code == 200 else {}
        if len(blocks) != 5:  # all five views render even when empty; anything else = bad page
            raise SourceError("supremecourt.govmu.org legislation search failed", r.status_code)
        return blocks

    @staticmethod
    def _type(v) -> str:
        t = _http.clean(v).lower()
        t = _TYPE_ALIASES.get(t, t)
        if t not in _TYPES and t not in _LOCAL_TYPES:
            raise BadRequest(f"type {v!r}: use revised, enacted, act, gn, bill, proclamation or reprint")
        return t

    async def _local(self, q: str, year: str, kind: str) -> list[LawHit]:
        """Title (or number) match over the Revised Laws, the Constitution and Acts as passed
        2009-2023: every query word must appear in the title (spaces ignored)."""
        items = await _index()
        if kind == "revised":
            items = [i for i in items if i["type"] in ("Constitution", "Revised law")]
        elif kind == "enacted":
            items = [i for i in items if i["type"] == "Act (as passed)"]
        if _LAW_ID.match(q):
            lid = self._norm_law_id(q)
            items = [i for i in items if i["number"] == lid]
        else:
            words = [_squash(w) for w in q.split() if _squash(w) not in ("", "the")]
            items = [i for i in items if all(w in i["key"] for w in words)]
        if year:
            items = [i for i in items if i["year"] == year]
        # a Revised law (as at 2017) whose title an Act as passed reuses may have been replaced by it
        def base(t):
            return re.sub(r"[^a-z]", "", re.sub(r"(,?\s*no\.?\s*\d+)?\s*(of\s*)?\d{4}\s*$", "",
                                                re.sub(r"^the\s+", "", t.lower())))
        later = {}
        for i in items:
            if i["type"] == "Act (as passed)":
                later.setdefault(base(i["title"]), []).append(i["number"])
        def warn(i):
            acts = later.get(base(i["title"])) if i["type"] == "Revised law" else None
            return (f"A later Act with the same title is listed ({', '.join(acts)}): this Revised law "
                    "may have been repealed or replaced by it (unverified); read that Act's repeal "
                    "provisions.") if acts else ""
        # only a year is known; the date field must be YYYY-MM-DD or empty, so the year goes in the title
        return [LawHit(snippet=warn(i), id=i["id"], type=i["type"], number=i["number"], date="", url=i["url"],
                       title=i["title"] if not i["year"] or i["year"] in i["title"]
                       else f'{i["title"]} ({i["year"]})') for i in items]

    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        params: dict[str, str] = {}
        q = _http.clean(query)
        kind = self._type(filters["type"]) if filters.get("type") else ""
        if kind in _LOCAL_TYPES or not kind:
            if not q and not filters.get("year") and not kind:
                raise BadRequest("give title words (e.g. 'companies'), a number like "
                                 "'Act No. 10 of 2026', a year filter, or type=revised")
            year = self._year(filters["year"]) if filters.get("year") else ""
            lim, pg = max(1, min(int(limit), 50)), max(1, int(page))
            loc = await self._local(q, year, kind)
            lnote = ("Revised Laws (consolidated, AG; mostly to June 2017) and the Constitution, "
                     "then Acts as passed 2009-2023; title words must all match. "
                     "No in-force status is given by the source: a Revised law is as at June 2017 "
                     "and may since have been repealed or replaced by a later Act as passed "
                     "listed here, so read the later Act's repeal provisions before relying on it. ")
            if kind:
                return Results(items=loc[(pg - 1) * lim:pg * lim], total=len(loc), note=lnote)
            if self.code not in permitted_codes():
                return Results(items=loc[(pg - 1) * lim:pg * lim], total=len(loc),
                               note=lnote + GATED)
            if (pg - 1) * lim < len(loc):
                return Results(items=loc[(pg - 1) * lim:pg * lim], total=None,
                               note=lnote + "Later pages: the Supreme Court library (2024 on).")
            page = pg - -(-len(loc) // lim)   # pages left for the 2024+ library
        if self.code not in permitted_codes():
            raise BadRequest(GATED + " Use type=revised or type=enacted (2009-2023).")
        if _LAW_ID.match(q):
            params["field_document_number"] = self._norm_law_id(q)
        elif q:
            params["title"] = q
        if filters.get("year"):
            params["from_year"] = params["to_year"] = self._year(filters["year"])
        if not params:
            raise BadRequest("give title words (e.g. 'domestic abuse'), a number like "
                             "'Act No. 10 of 2026', or a year filter")
        limit = max(1, min(int(limit), PER_PAGE))
        page = max(1, int(page))
        if filters.get("type"):
            block, slot, _ = _TYPES[self._type(filters["type"])]
            start = (page - 1) * limit
            p0 = start // PER_PAGE
            slots = ["0"] * 5
            slots[slot] = str(p0)
            rows = (await self._lpage({**params, "page": ",".join(slots)})).get(block, [])
            rows = [(block, r) for r in rows[start % PER_PAGE:]]
            if len(rows) < limit and len(rows) + start % PER_PAGE == PER_PAGE:
                slots[slot] = str(p0 + 1)
                rows += [(block, r) for r in
                         (await self._lpage({**params, "page": ",".join(slots)})).get(block, [])]
            note = "Titles searched; newest first; texts as enacted (library starts 2024)."
        else:
            blocks = await self._lpage({**params, "page": ",".join([str(page - 1)] * 5)})
            order = ["act", "regulation", "bill", "proclamation", "reprint"]
            rows, i = [], 0
            while any(i < len(blocks.get(b, [])) for b in order):   # round-robin over types
                rows += [(b, blocks[b][i]) for b in order if i < len(blocks.get(b, []))]
                i += 1
            note = ("All types mixed: each page holds up to 10 per type; set filter type= "
                    "(act, gn, bill, proclamation, reprint) for paging within one type. "
                    "Texts as enacted, 2024 on.")
        items = [LawHit(id=r["number"], title=r["title"], type=_TYPE_NAMES.get(b, b),
                        number=r["number"], url=r["url"]) for b, r in rows[:limit]]
        return Results(items=items, total=None, note=note)

    @staticmethod
    def _norm_law_id(raw: str) -> str:
        m = _LAW_ID.match(raw or "")
        if not m:
            raise BadRequest(f"law id {raw!r}: use an id from search_legislation, e.g. "
                             "'Act No. 10 of 2026', 'GN No. 175 of 2026', 'constitution' or "
                             "'A-Z Acts/C/Companies Act, No. 15 of 2001'")
        kind = m[1].lower().replace(".", "")
        word = {"act": "Act", "gn": "GN", "bill": "Bill", "proclamation": "Proclamation",
                "reprint": "Reprint"}[kind]
        return f"{word} No. {int(m[2])} of {m[3]}"

    async def _local_law(self, lid: str) -> dict:
        """Revised law, the Constitution, or an Act as passed 2009-2023, from the index."""
        item = next((i for i in await _index() if i["id"].lower() == lid.lower()), None)
        if not item:
            raise NotFound(f"no law {lid!r}: use an id from search_legislation (e.g. "
                           "'A-Z Acts/C/Companies Act, No. 15 of 2001', 'constitution', "
                           "'Act No. 5 of 2019')")
        r = await _http.get(item["url"])
        if r.status_code != 200 or not r.content.startswith(b"%PDF"):
            raise SourceError(f"PDF for {item['id']} failed", r.status_code)
        text = _http.pdf_text(r.content)
        if not text:
            raise SourceError(f"PDF for {item['id']} has no text layer (scanned)", "no text")
        meta = {"Type": item["type"]}
        title = item["title"]
        if item["type"] in ("Constitution", "Revised law"):
            issue = re.search(r"\[Issue \d+\]", text[:300])
            if issue:
                meta["Revised Laws issue"] = issue[0].strip("[]")
            text = _despace(_strip_running(text))
            cut = text.find("\nLAWS RELATED TO THE CONSTITUTION")
            if item["type"] == "Constitution":
                text = _despace(text)
                meta["Text layer"] = ("stray spaces inside words were repaired automatically where "
                                      "unambiguous; check any quotation against the PDF")
            if item["type"] == "Constitution" and cut > 0:
                text = text[:text.rfind("\n", 0, cut)]   # drop PART II-III (related laws, case notes)
                meta["Left out"] = "Parts II-III of the AG volume (related laws, constitutional jurisprudence)"
            meta["Note"] = ("Consolidated as at this Revised Laws issue; later amendments are in the "
                            "amending Acts as passed")
            if " " not in item["id"].rsplit("/", 1)[-1]:   # squashed file name: take the PDF's title
                t = next((ln.strip() for ln in text.split("\n")[:8]
                          if re.search(r"\b(ACT|CODE|ORDINANCE)\b", ln) and ln.strip().isupper()), "")
                title = t or title
        doc = {"id": item["id"], "title": title, "url": item["url"], "text": text,
               "blocks": _parse_law(text), "meta": meta}
        return _http.lru_put(_cache, ("law", item["id"]), doc, 6)

    async def _law(self, raw_id: str) -> dict:
        rid = _http.clean(raw_id)
        if rid.lower() in ("constitution", "the constitution", "constitution of mauritius"):
            rid = CONSTITUTION_ID
        if not _LAW_ID.match(rid):
            if ("law", rid) in _cache:
                return _cache[("law", rid)]
            if rid.startswith(("A-Z Acts/", "Constitutions/")):
                return await self._local_law(rid)
        lid = self._norm_law_id(rid)
        if ("law", lid) in _cache:
            return _cache[("law", lid)]
        if lid.startswith("Act ") and int(lid[-4:]) < 2024:
            return await self._local_law(lid)
        if self.code not in permitted_codes():
            raise BadRequest(GATED)
        blocks = await self._lpage({"field_document_number": lid})
        hit = next(((b, r) for b, rows in blocks.items() for r in rows
                    if r["number"].lower() == lid.lower()), None)
        if not hit:
            raise NotFound(f"no {lid} in the Supreme Court legislation library (it starts in 2024; "
                           "try search_legislation)")
        block, row = hit
        r = await _http.get(row["url"])
        if r.status_code != 200 or not r.content.startswith(b"%PDF"):
            raise SourceError(f"PDF for {lid} failed", r.status_code)
        text = _http.pdf_text(r.content)
        if not text:
            raise SourceError(f"PDF for {lid} has no text layer (scanned)", "no text")
        head = text.split("\n")[:12]
        meta = {"Type": _TYPE_NAMES.get(block, block)}
        for ln in head:
            if ln.startswith("Government Gazette of Mauritius"):
                meta["Gazette"] = ln
            elif ln.startswith("Proclaimed by"):
                meta["Commencement"] = ln
        doc = {"id": lid, "title": row["title"], "url": row["url"], "text": text,
               "blocks": _parse_law(text), "meta": meta}
        return _http.lru_put(_cache, ("law", lid), doc, 6)

    async def get_legislation_toc(self, id):
        doc = await self._law(id)
        entries = []
        for b in doc["blocks"]:
            if b["kind"] == "heading":
                entries.append(TocEntry(title=_http.clean(b["title"]), level=0))
            elif b["kind"] == "section":
                entries.append(TocEntry(title=b["title"], level=1, provision=b["label"]))
            elif b["kind"] == "schedule":
                entries.append(TocEntry(title=b["label"], level=0, provision=b["label"]))
        return Toc(id=doc["id"], title=doc["title"], url=doc["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        doc = await self._law(id)
        label = _norm_provision(provision)
        b = next((b for b in doc["blocks"] if b["kind"] in ("section", "schedule")
                  and b["label"].lower() == label.lower()), None)
        if not b and label.isdigit():   # inside a repealed range such as "49. – 101. —"
            b = next((b for b in doc["blocks"] if b["kind"] == "section" and b.get("end")
                      and int(re.match(r"\d+", b["label"])[0]) <= int(label) <= b["end"]), None)
        if b and label.isdigit() and b.get("end") and b["label"] != label:
            raise NotFound(f"{provision!r} falls inside {b['label']}-{b['end']} of {doc['id']}, which "
                           "the source prints as one dash entry with no article text (the source does not "
                           "say why); check the printed Revised Laws")
        if not b:
            raise NotFound(f"no provision {provision!r} in {doc['id']}: use a label from "
                           "get_legislation_toc (e.g. '5' for section 5, 'First Schedule')")
        return Provision(law_id=doc["id"], law_title=doc["title"], provision=b["label"],
                         text=_block_md(b), url=doc["url"],
                         note=("Text extracted from a PDF: words may be split (e.g. 'Mauritiu s'); "
                               "check against the official PDF before quoting.")
                         if doc["url"].lower().endswith(".pdf") else "")

    async def get_legislation_text(self, id):
        doc = await self._law(id)
        text = "\n\n".join(t for t in (_block_md(b) for b in doc["blocks"]) if t.strip())
        return LawText(id=doc["id"], title=doc["title"], text=text, url=doc["url"],
                       metadata=doc["meta"])
