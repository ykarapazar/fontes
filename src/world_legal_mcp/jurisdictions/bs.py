"""The Bahamas: Statute Law of The Bahamas (Law Reform and Revision Commission), judgments
of the Court of Appeal and the Supreme Court (the courts' own sites), and Privy Council
judgments in Bahamian appeals (Find Case Law, through the gb adapter's code).

Legislation (laws.bahamas.gov.bs, Joomla "iLAWS"):
  * /cms/legislation/index/by-alphabetical.html is one page listing all current legislation:
    item number ("1873-0015"), title, and kind (principal Act, subsidiary legislation, amending
    Act), grouped by letter and parent Act. It is fetched once and searched in memory.
  * The PDF of the current version is linked from the Acts "in Alphabetical Order" page, one
    letter per POST (submit4=<letter>); the parent Act's letter page also links its subsidiary
    and amending legislation. PDFs are text-layer Revised Edition prints (LRO 1/2017 etc.).
  * The site's own search is /cms/search/search.php, which robots.txt disallows: not used.
  Ids are the item number for a principal Act ("1873-0015" = Penal Code), "sub/<item>" for
  subsidiary legislation and "amd/<item>" for amending Acts/Regulations (the source reuses
  item numbers across these kinds).

Case law:
  * Privy Council (the final court): UKPC judgments on Find Case Law, Nov 2009 on, searched
    full text through gb._search_caselaw and filtered to Bahamian appeals by title/header
    (jcpc_hits below; mu.py and jm.py reuse it). Id: the neutral citation, "[2026] UKPC 9".
  * Court of Appeal (www.courtofappeal.org.bs): the site's own search form (POST
    judgments.php, action=result; case name, keywords, file number, year), 15 rows a page via
    skip=N. Each judgment has a page judgments.php?action=view&judgment=N with catchwords,
    judges, date added and one PDF. Id: "ca/<N>".
  * Supreme Court (courts.bs, WordPress): /judgments/ lists every published judgment (2,390
    in 2026-11) on one page: title with case number, judge, date, PDF. Fetched once, kept in
    memory for _TTL and searched there. Id: "sc/<upload path>" ("sc/2026/11/RULING-S.V.R.-v.-S.L.R.pdf").
Every PDF id is checked against the source's own list or page before download, and a HEAD
request caps the size (MAX_PDF), so a bad id cannot trigger an arbitrary or huge download.
"""
from __future__ import annotations

import re
import time
from dataclasses import replace
from urllib.parse import unquote, urljoin

from lxml import html as lhtml

from .. import _http
from . import gb as _gb
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc, TocEntry

LAWS_HOST = "laws.bahamas.gov.bs"
SC_HOST = "courts.bs"
CA_HOST = "www.courtofappeal.org.bs"
LAWS = f"https://{LAWS_HOST}/cms"
INDEX_URL = f"{LAWS}/legislation/index/by-alphabetical.html"
LETTER_URL = f"{LAWS}/legislation/acts_only/by-alphabetical-order.html"
SC_LIST = f"https://{SC_HOST}/judgments/"
CA = f"https://{CA_HOST}"
COURTS = {"sc": "Supreme Court of The Bahamas", "ca": "Court of Appeal of The Bahamas"}
_COURT_ALIASES = {"sc": "sc", "supreme": "sc", "supreme court": "sc",
                  "ca": "ca", "coa": "ca", "appeal": "ca", "court of appeal": "ca",
                  "jcpc": "jcpc", "ukpc": "jcpc", "privy council": "jcpc", "pc": "jcpc"}
CA_PAGE = 15                  # rows per Court of Appeal result page (fixed by the site)
CA_YEAR_MAX = 150            # most Court of Appeal matches crawled (10 pages) to filter by year client-side
MAX_PDF = 40_000_000          # bytes; larger PDFs are refused
_TTL = 6 * 3600
_KINDS = {"prn": ("PRINCIPAL", "Act", ""), "subx": ("SUBORDINATE", "Subsidiary legislation", "sub/"),
          "amdx": ("AMENDING", "Amending legislation", "amd/")}
_PREFIX = {"": "prn", "sub/": "subx", "amd/": "amdx"}
_ITEM = r"\d{4}-\d{3}[0-9A-Z]"
_LAW_ID = re.compile(rf"^(sub/|amd/)?({_ITEM})$", re.I)
_SC_ID = re.compile(r"^sc/(\d{4}/\d{2}/[^/?#]{1,200}\.pdf)$", re.I)
_CA_ID = re.compile(r"^ca/(\d{1,7})$", re.I)
_YEAR = re.compile(r"^(\d{4})(?:\s*[-–]\s*(\d{4})?)?$")   # 2022, 2020-2024 or 2022- (from 2022 on)

_cache: dict = {}             # key -> (monotonic time, value)
_laws: dict = {}              # law id -> parsed law (small LRU)


def _cached(key):
    hit = _cache.get(key)
    return hit[1] if hit and time.monotonic() - hit[0] < _TTL else None


def _store(key, value):
    return _http.lru_put(_cache, key, (time.monotonic(), value), 32)[1]


def _words(q: str) -> list[str]:
    words = [w.strip(".,;:()[]\"'").lower() for w in (q or "").split()]
    return [w for w in words if w and w not in ("v", "v.", "vs", "vs.", "and", "the", "of")]


_CONST_SUBJECT = re.compile(r"constitutional|constitution of|articles?\s+\d", re.I)


def _matches(words: list[str], hay: str) -> bool:
    hay = hay.lower()
    return all(w in hay for w in words)


async def _pdf(url: str, who: str) -> str:
    """Text of a PDF the source itself lists; refuses anything over MAX_PDF."""
    h = await _http.request("HEAD", url)
    if h.status_code == 404:
        raise NotFound(f"{who}: {url} is gone (HTTP 404).")
    size = int(h.headers.get("content-length") or 0)
    if size > MAX_PDF:
        raise SourceError(f"Error ({who}): {url} is {size // 1_000_000} MB, over the "
                          f"{MAX_PDF // 1_000_000} MB limit; read it there.", "too-large")
    r = await _http.get(url)
    if r.status_code != 200 or not r.content.startswith(b"%PDF"):
        raise SourceError(_http.error(who, f"PDF failed: {url}", r.status_code), r.status_code)
    text = _http.pdf_text(r.content)
    if len(text) < 200:
        raise SourceError(f"Error ({who}): {url} has no text layer (scanned; no OCR here); read it there.",
                          "no-text")
    return text


# --------------------------------------------------------------------------- #
# Privy Council (JCPC) appeals, via the gb adapter's Find Case Law code.
# Shared with mu.py and jm.py (they import jcpc_hits / jcpc_decision from here).
# --------------------------------------------------------------------------- #
JCPC_SOURCE = replace(
    _gb.UnitedKingdom.sources[0],
    name="Find Case Law, The National Archives (UK): Judicial Committee of the Privy Council judgments",
    url=_gb.CASELAW)
JCPC_COURT = "Judicial Committee of the Privy Council"
JCPC_ALIASES = ("jcpc", "ukpc", "privy council", "pc")
_UKPC_ID = re.compile(r"^(?:\[\d{4}\]\s*UKPC\s*\d+|ukpc/\d{4}/\d+)$", re.I)
_JCPC_BS = ("Bahamas", "From the Court of Appeal of the Commonwealth of The Bahamas")
_JCPC_PAGES = 6               # x 50 hits; the widest country set (Mauritius) is ~130 in 2026-11
_NOT_COUNTRY = re.compile(r"appellant|respondent|^no\.?\s*\d", re.I)   # '(No 2)' etc.


async def _ukpc_all(query: str) -> list[DecisionHit]:
    out: list[DecisionHit] = []
    for p in range(1, _JCPC_PAGES + 1):
        res = await _gb._search_caselaw(query, court="ukpc", party=None, judge=None,
                                        order="-date", limit=50, page_no=p)
        out += res.items
        if len(res.items) < 50:
            break
    return out


async def jcpc_hits(word: str, phrase: str, query: str, year: str = "") -> list[DecisionHit]:
    """Every UKPC judgment on Find Case Law in an appeal from one country that matches `query`.

    Find Case Law has no country field. Most titles end with the country in brackets,
    '... (The Bahamas)'; most 2014-19 titles do not. So: (a) full-text hits for query + `word`
    whose title ends with '(<word>)' or '(The <word>)', plus (b) hits for '"<phrase>"' + query
    (the header line 'From the Court of Appeal of ...', a phrase search) whose title names no
    other country. Newest first."""
    q = _http.clean(query or "")
    key = ("jcpc", word, q)
    hits = _cached(key)
    if hits is None:
        own = re.compile(rf"\((?:the\s+)?{re.escape(word)}\)$", re.I)
        tail = re.compile(r"\(([^()]*)\)$")

        def bare(h):   # gb appends the neutral citation to the title
            return h.title.removesuffix(h.id).strip()
        found = {h.id: h for h in await _ukpc_all(f"{q} {word}".strip()) if own.search(bare(h))}
        for h in await _ukpc_all(f'"{phrase}" {q}'.strip()):   # phrase first: 'word "phrase"' finds nothing
            m = tail.search(bare(h))
            if not m or own.search(bare(h)) or _NOT_COUNTRY.search(m[1]):
                found.setdefault(h.id, h)
        hits = _store(key, sorted(found.values(), key=lambda h: h.date, reverse=True))
    for h in hits:
        h.court = JCPC_COURT
    return [h for h in hits if not year or h.date[:4] == year]


def is_jcpc_id(ident: str) -> bool:
    return bool(_UKPC_ID.match(_http.clean(ident or "")))


async def jcpc_decision(ident: str) -> Decision:
    d = await _gb._get_judgment(_http.clean(ident))
    d.court = JCPC_COURT
    return d


# --------------------------------------------------------------------------- #
# Supreme Court (courts.bs)
# --------------------------------------------------------------------------- #
def _sc_split(title: str) -> tuple[str, str]:
    """'BETWEEN A AND B - 2026/CLE/gen/00555' -> ('BETWEEN A AND B', '2026/CLE/gen/00555')."""
    m = re.match(r"^(.*\S)\s+[-–—]\s+([^-–—]*\d[^-–—]*)$", title)
    return (m[1], m[2].strip()) if m else (title, "")


async def _sc_rows() -> list[dict]:
    rows = _cached("sc")
    if rows is not None:
        return rows
    r = await _http.get(SC_LIST)
    if r.status_code != 200:
        raise SourceError(_http.error(COURTS["sc"], "judgment list failed", r.status_code), r.status_code)
    doc = lhtml.fromstring(r.content)
    rows = []
    for ul in doc.xpath('//ul[@class="judgements__row"]'):
        lis = ul.xpath("./li")
        href = (ul.xpath('.//a[@download]/@href') or [""])[0]
        m = re.match(r"^https?://(?:www\.)?courts\.bs/wp-content/uploads/(\d{4}/\d{2}/[^/?#]+\.pdf)$", href)
        if not m or len(lis) < 2:
            continue

        def cell(label):
            li = next((x for x in ul.xpath(".//li") if _http.clean(x.xpath("string(./div)")) == label), None)
            if li is None:
                return ""
            return _http.clean("".join(t for t in li.xpath("./text()|./a/text()")))

        title = cell("JUDGMENT")
        name, num = _sc_split(title)
        rows.append({"path": unquote(m[1]), "title": title, "name": name, "number": num,
                     "judge": cell("JUDGE"), "date": _http.en_date(cell("DATE")),
                     "pdf": f"https://{SC_HOST}/wp-content/uploads/{m[1]}"})
    if not rows:
        raise SourceError(f"Error ({COURTS['sc']}): no judgments found on {SC_LIST}; layout changed?", "layout")
    return _store("sc", rows)


def _sc_hit(row: dict) -> DecisionHit:
    return DecisionHit(id=f"sc/{row['path']}", title=row["name"] or row["title"], court=COURTS["sc"],
                       date=row["date"], case_number=row["number"], snippet=row["judge"], url=row["pdf"])


async def _sc_decision(path: str) -> Decision:
    row = next((x for x in await _sc_rows() if x["path"].lower() == path.lower()), None)
    if row is None:
        raise NotFound(f"The Supreme Court judgment list ({SC_LIST}) has no PDF {path}.")
    text = await _pdf(row["pdf"], COURTS["sc"])
    meta = {k: v for k, v in (("Judge", row["judge"]), ("Listed at", SC_LIST)) if v}
    return Decision(id=f"sc/{row['path']}", title=row["name"] or row["title"], text=text, url=row["pdf"],
                    court=COURTS["sc"], date=row["date"], case_number=row["number"], metadata=meta)


# --------------------------------------------------------------------------- #
# Court of Appeal (courtofappeal.org.bs)
# --------------------------------------------------------------------------- #
async def _ca_search(query: str, year: str, skip: int) -> tuple[list[DecisionHit], int]:
    form = {"action": "result", "query": query, "keywords": "", "filenumber": "", "day": "", "month": "",
            "year": year, "firstlevel": "", "secondlevel": "", "thirdlevel": "", "skip": str(skip),
            "submit": "Search"}
    key = ("ca", query.lower(), year, skip)
    hit = _cached(key)
    if hit is not None:
        return hit
    r = await _http.post(f"{CA}/judgments.php", data=form)
    if r.status_code != 200:
        raise SourceError(_http.error(COURTS["ca"], "judgment search failed", r.status_code), r.status_code)
    doc = lhtml.fromstring(r.content)
    m = re.search(r"Found\s+(\d+)\s+Judgments", doc.text_content())
    total = int(m[1]) if m else 0
    hits = []
    for tr in doc.xpath('//tr[td/a[contains(@href,"action=view")]]'):
        tds = tr.xpath("./td")
        a = tr.xpath('.//a[contains(@href,"action=view")]')[0]
        n = re.search(r"judgment=(\d+)", a.get("href", ""))
        if not n or len(tds) < 3:
            continue
        num = _http.clean(tds[0].text_content())
        hits.append(DecisionHit(
            id=f"ca/{n[1]}", title=_http.clean(a.text_content()) or f"{COURTS['ca']} {num}",
            court=COURTS["ca"], date=_http.iso_date(_http.clean(tds[2].text_content())),
            case_number=num, url=f"{CA}/judgments.php?action=view&judgment={n[1]}"))
    return _store(key, (hits, total))


async def _ca_decision(n: str) -> Decision:
    page_url = f"{CA}/judgments.php?action=view&judgment={n}"
    r = await _http.get(page_url)
    if r.status_code == 404:
        raise NotFound(f"{COURTS['ca']} has no judgment {n}.")
    if r.status_code != 200:
        raise SourceError(_http.error(COURTS["ca"], f"judgment {n} failed", r.status_code), r.status_code)
    doc = lhtml.fromstring(r.content)
    table = doc.xpath('//table[@class="datatable"]')
    pdf = table[0].xpath('.//a[starts-with(@href,"download/")]/@href') if table else []
    if not pdf or not re.fullmatch(r"download/[\w.-]+\.pdf", pdf[0]):
        raise NotFound(f"{COURTS['ca']} has no judgment {n} ({page_url} shows no judgment PDF).")
    head = table[0].xpath('.//td[@class="headcell"]')[0]
    parts = [_http.clean(t) for t in head.xpath("./text()") if _http.clean(t)]
    case_no = re.sub(r"^Case #:\s*", "", parts[0]) if parts else ""
    title = " ".join(parts[1:]) or f"{COURTS['ca']} {case_no}"
    paras = [_http.clean(p.text_content()) for p in table[0].xpath(".//p")]
    catch = next((p for p in paras if p and not p.startswith("Pending before")), "")
    privy = next((p for p in paras if p.startswith("Pending before")), "")
    privy = re.sub(r"\s*Click the icon.*$", "", privy)
    last = table[0].xpath("./tr[last()]/td") or table[0].xpath(".//tr[last()]/td")
    kind_judges = _http.clean(last[0].text_content()) if last else ""
    added = _http.clean(last[1].text_content()) if len(last) > 1 else ""
    date = _http.iso_date(re.sub(r"^Date Added:\s*", "", added))
    pdf_url = urljoin(CA + "/", pdf[0])
    text = await _pdf(pdf_url, COURTS["ca"])
    kind, _, judges = kind_judges.partition(" by Justice(s) ")
    meta = {k: v for k, v in (("Type of matter", kind), ("Judges", judges),
                              ("Privy Council", privy.replace("Pending before Privy Council?:", "pending:").strip()),
                              ("Date note", "date the judgment was added to the site"), ("Judgment page", page_url)) if v}
    return Decision(id=f"ca/{n}", title=title, text=text, url=pdf_url, court=COURTS["ca"], date=date,
                    case_number=case_no, summary=catch, metadata=meta)


# --------------------------------------------------------------------------- #
# Legislation (laws.bahamas.gov.bs)
# --------------------------------------------------------------------------- #
async def _index() -> list[dict]:
    """All current legislation from the alphabetical index: item, kind, title, letter, parent."""
    rows = _cached("index")
    if rows is not None:
        return rows
    r = await _http.get(INDEX_URL)
    if r.status_code != 200:
        raise SourceError(_http.error(LAWS_HOST, "legislation index failed", r.status_code), r.status_code)
    doc = lhtml.fromstring(r.content)
    rows, letter, parent = [], "", ""
    for tr in doc.xpath('//tr[td[@class="alphaLetter"] or td[@class="itemno"]]'):
        lt = tr.xpath('./td[@class="alphaLetter"]')
        if lt:
            letter = _http.clean(lt[0].text_content())[:1].upper()
            continue
        item = _http.clean(tr.xpath('string(./td[@class="itemno"])'))
        td = tr.xpath('./td[@class="prn" or @class="subx" or @class="amdx"]')
        if not td or not re.fullmatch(_ITEM, item):
            continue
        kind = td[0].get("class")
        title = re.sub(r"^amended by\.\.\.\s*", "", _http.clean(td[0].text_content()))
        if kind == "prn":
            parent = title
        rows.append({"item": item, "kind": kind, "title": title, "letter": letter,
                     "parent": "" if kind == "prn" else parent,
                     "id": _KINDS[kind][2] + item})
    if len(rows) < 100:
        raise SourceError(f"Error ({LAWS_HOST}): the legislation index at {INDEX_URL} looks empty; "
                          "layout changed?", "layout")
    return _store("index", rows)


async def _letter(letter: str) -> list[dict]:
    """PDF links on one letter of the Acts list (Acts plus their subsidiary/amending items)."""
    rows = _cached(("letter", letter))
    if rows is not None:
        return rows
    r = await _http.post(LETTER_URL, data={"submit4": letter})
    if r.status_code != 200:
        raise SourceError(_http.error(LAWS_HOST, f"Acts list '{letter}' failed", r.status_code), r.status_code)
    doc = lhtml.fromstring(r.content)
    rows = []
    for a in doc.xpath('//a[@class="npWrap" or ancestor::td[contains(@class,"amd")]]'):   # amending Acts have no npWrap class
        m = re.match(rf"^/cms/images/LEGISLATION/(PRINCIPAL|SUBORDINATE|AMENDING)/\d{{4}}/({_ITEM})[A-Z]?/"
                     r"[\w.-]+\.pdf$", a.get("href", ""))
        if not m:
            continue
        tr = a.getparent()
        while tr is not None and tr.tag != "tr":
            tr = tr.getparent()
        notes = tr.xpath('.//*[@title="Legislation Notes"]/@data-bs-content') if tr is not None else []
        long_title = re.sub(r"^.*?<hr[^>]*>", "", notes[0]) if notes and "<hr" in notes[0] else ""
        comm = tr.xpath('.//*[@title="Date Commenced"]/@data-bs-content') if tr is not None else []
        ver = a.xpath('.//*[@title="Version"]')
        name = _http.clean("".join(a.xpath("./text()")))
        rows.append({"folder": m[1], "item": m[2], "pdf": f"https://{LAWS_HOST}{a.get('href')}",
                     "title": re.sub(r"^amended by\.\.\.\s*", "", name),
                     "version": _http.clean(ver[0].text_content()).strip("[]") if ver else "",
                     "long_title": _http.clean(lhtml.fromstring(f"<p>{long_title}</p>").text_content())
                     if long_title else "",
                     "commenced": _commenced(comm[0]) if comm else ""})
    return _store(("letter", letter), rows)


def _commenced(s: str) -> str:
    m = re.search(r"(\d{1,2}) (\w+) (\d{4})", s or "")
    return _http.en_date(f"{m[2]} {m[1]}, {m[3]}") if m else ""


_PAGE_JUNK = re.compile(
    r"^(?:.*\[CH\.\s*\d+[A-Z]?\s*[–-]\s*\d+|CH\.\s*\d+[A-Z]?\s*[–-]\s*\d+\].*|"
    r"(?:LRO \d+/\d{4} )?STATUTE LAW OF THE BAHAMAS(?: LRO \d+/\d{4})?|"
    r"(?:Original )?SUBSIDIARY LEGISLATION|SECTION|REGULATION|ARTICLE|RULE|PARAGRAPH|"
    r"ARRANGEMENT OF [A-Z]+[—\- ]+Continued)$")
_SEC = re.compile(r"^\*?\s*(\d+[A-Z]{0,2})\.\s+(\S.*)$")
_SCHED = re.compile(r"^((?:FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH|SEVENTH|EIGHTH|NINTH|TENTH)\s+)?SCHEDULE\b.*$")


def _split(text: str) -> tuple[list[TocEntry], dict[str, str], str]:
    """Cut a Revised Edition PDF text into sections using its Arrangement of Sections (adapted
    from tt.py: the Regional Law Revision Centre prints both). Returns (toc, {label: text}, full)."""
    lines = [ln for ln in text.splitlines() if not _PAGE_JUNK.match(ln.strip())]
    full = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
    flat = [ln for ln in lines if ln.strip()]
    start = next((i for i, ln in enumerate(flat)
                  if re.match(r"^ARRANGEMENT OF (SECTIONS|ARTICLES|REGULATIONS|RULES|PARAGRAPHS|CLAUSES)\b",
                              ln.strip().upper())), None)
    arrangement: list[tuple[str, str]] = []
    headings: dict[str, list[str]] = {}
    body_at = None
    if start is not None:
        pending: list[str] = []
        seen = set()
        for i in range(start + 1, len(flat)):
            ln = flat[i].strip()
            m = _SEC.match(ln)
            if m:
                if m[1] in seen:            # numbering restarts: the body begins
                    body_at = i
                    break
                seen.add(m[1])
                arrangement.append((m[1], m[2]))
                if pending:
                    headings[m[1]] = pending
                    pending = []
            elif ln.isupper() and len(ln) < 90:
                pending.append(ln)
            elif arrangement and ln[:1].islower():    # wrapped heading line
                lab, t = arrangement[-1]
                arrangement[-1] = (lab, f"{t} {ln}")
    if not arrangement or body_at is None:
        return [], {}, full
    body = flat[body_at:]
    labels = [lab for lab, _ in arrangement]
    pos: list[tuple[str, int]] = []
    k = 0
    for i, ln in enumerate(body):
        s = ln.strip()
        for j in range(k, min(k + 4, len(labels))):
            if re.match(rf"^\*?\s*{re.escape(labels[j])}\.(\s|$)", s):
                pos.append((labels[j], i))
                k = j + 1
                break
        if k >= len(labels):
            break
    if not pos:
        return [], {}, full
    sched_at = None
    for i in range(pos[-1][1] + 1, len(body)):
        if _SCHED.match(body[i].strip()) and body[i].strip().split()[-1].isupper():
            sched_at = i
            break
    texts: dict[str, str] = {}
    for n, (lab, i) in enumerate(pos):
        end = pos[n + 1][1] if n + 1 < len(pos) else (sched_at or len(body))
        chunk = [x.strip() for x in body[i:end]]
        while len(chunk) > 1 and chunk[-1].isupper() and len(chunk[-1]) < 90:
            chunk.pop()                     # the next section's part heading
        texts[lab] = "\n".join(chunk)
    if sched_at is not None:
        texts["Schedule"] = "\n".join(x.strip() for x in body[sched_at:])
    toc = []
    titles = dict(arrangement)
    for lab, _ in pos:
        for h in headings.get(lab, []):
            toc.append(TocEntry(title=h, level=0))
        toc.append(TocEntry(title=f"{lab}. {titles.get(lab, '')}".strip(), level=1, provision=lab))
    if "Schedule" in texts:
        toc.append(TocEntry(title="Schedule(s)", level=0, provision="Schedule"))
    return toc, texts, full


_GARBLE_WARN = ("WARNING: the text layer of this PDF is garbled (letters are replaced by symbols, e.g. "
                "'#1& %his Act'). Do not quote or cite this text. This tool cannot give a readable version of this document; "
                "the content is only available by reading the PDF at the source URL.")


def _garbled(text: str) -> bool:
    """True when the PDF's font encoding broke: symbols stand in for letters."""
    letters = sum(c.isalpha() for c in text) or 1
    return len(re.findall(r"[#*&%+/<>]", text)) / letters > 0.01


def _norm_prov(p: str) -> str:
    s = _http.clean(p)
    if re.match(r"(?i)^(the\s+)?(first|second|third|fourth|fifth)?\s*sched", s):
        return "Schedule"
    s = re.sub(r"(?i)^(section|sec\.?|s\.|s|article|art\.?|regulation|reg\.?|rule|r\.)\s*", "", s).strip().rstrip(".")
    m = re.match(r"^(\d+[A-Za-z]{0,2})(?:\s*\(.*)?$", s)
    return m[1].upper() if m else s


async def _law(id: str) -> dict:
    lid = _http.clean(id)
    m = _LAW_ID.match(lid)
    if not m:
        raise BadRequest("Use a law id from search_legislation: an item number such as '1873-0015' "
                         "(Penal Code), 'sub/2010-0140' (subsidiary) or 'amd/2024-0007' (amending).")
    prefix, item = (m[1] or "").lower(), m[2].upper()
    lid = prefix + item
    if lid in _laws:
        return _laws[lid]
    kind = _PREFIX[prefix]
    row = next((x for x in await _index() if x["item"] == item and x["kind"] == kind), None)
    if row is None:
        other = [x["id"] for x in await _index() if x["item"] == item]
        hint = f" Did you mean {', '.join(sorted(set(other)))}?" if other else ""
        raise NotFound(f"No current {_KINDS[kind][1].lower()} {item} in the Statute Law index.{hint}")
    folder = _KINDS[kind][0]
    links = [x for x in await _letter(row["letter"]) if x["folder"] == folder and x["item"] == item]
    if len(links) > 1:
        links = [x for x in links if x["title"].lower() == row["title"].lower()] or links
    if not links:
        raise NotFound(f"{row['title']} ({item}) has no PDF on the Acts list for '{row['letter']}'.")
    link = links[0]
    raw = await _pdf(link["pdf"], LAWS_HOST)
    toc, sections, full = _split(raw)
    rev = re.search(r"\bLRO \d+/\d{4}\b", raw[:2000])
    chap = re.search(r"\bCHAPTER (\d+[A-Z]?)\b", raw[:2000])
    title = row["title"] + (f", Ch. {chap[1]}" if chap and kind == "prn" else "")
    meta = {k: v for k, v in (
        ("Item number", item), ("Kind", _KINDS[kind][1]), ("Under", row["parent"]),
        ("Long title", link["long_title"]), ("Commenced", link["commenced"]),
        ("Version", link["version"]), ("Revision", rev[0] if rev else ""), ("PDF", link["pdf"])) if v}
    law = {"id": lid, "title": title, "url": link["pdf"], "toc": toc, "sections": sections,
           "text": full, "meta": meta, "garbled": _garbled(full)}
    if law["garbled"]:
        law["toc"] = [TocEntry(title=_GARBLE_WARN)] + law["toc"]
        law["meta"] = {"Text warning": _GARBLE_WARN, **meta}
    return _http.lru_put(_laws, lid, law, 8)


# --------------------------------------------------------------------------- #
class Bahamas(Jurisdiction):
    code = "bs"
    name = "The Bahamas"
    languages = ("en",)
    aliases = ("bahamas", "the bahamas", "commonwealth of the bahamas", "bah", "bhs")
    _courts_terms = ("no licence or terms of use; the site's only policy page is a privacy/data policy "
                     "(read 2026-11-05)")
    sources = (
        JCPC_SOURCE,
        Source(
            name="Statute Law of The Bahamas, Law Reform and Revision Commission (laws.bahamas.gov.bs)",
            url=f"{LAWS}/",
            covers=("legislation",),
            licence=("Government of The Bahamas Copyright: 'Any reproduction shall ensure its accuracy, and "
                     "the source and copyright status of the material is made evident to users. The website "
                     "may only be used for informational non-commercial purposes'"),
            commercial_use=False,
            ai_use=None,   # robots.txt: Joomla default (only /cms/administrator/, /cms/search/search.php ...); no AI clause
            auth="none",
            rate_limit=("unknown; no Crawl-delay; 1 s spacing, index and letter lists cached in memory 6 h; "
                        "no 429 in ~15 requests (2026-11)"),
            terms_url=f"{LAWS}/?view=article&id=115:copyright&catid=14:general-articles",
            warning=("Statute Law of The Bahamas: Government copyright, informational non-commercial use only; "
                     "not the authoritative text (that is the printed Revised Edition and the Official Gazette)."),
        ),
        Source(
            name="Court of Appeal of The Bahamas judgments (courtofappeal.org.bs)",
            url=f"{CA}/judgments.php",
            covers=("caselaw",),
            licence="© Court of Appeal of the Commonwealth of The Bahamas, all rights reserved; " + _courts_terms,
            commercial_use=None,
            ai_use=None,   # robots.txt disallows /library/, /images/, /admin/ ...; not judgments.php or /download/
            auth="none",
            rate_limit="unknown; no Crawl-delay; 1 s spacing, no 429 in ~10 requests (2026-11)",
            terms_url=f"{CA}/",
        ),
        Source(
            name="Supreme Court of The Bahamas judgments, The Judiciary of The Bahamas (courts.bs)",
            url=SC_LIST,
            covers=("caselaw",),
            licence="© The Judiciary of The Bahamas; " + _courts_terms,
            commercial_use=None,
            ai_use=None,   # no robots.txt (404); no AI/TDM clause
            auth="none",
            rate_limit=("unknown; no robots.txt; 1 s spacing, the one-page judgment list (~1.2 MB) cached "
                        "in memory 6 h; no 429 in ~10 requests (2026-11)"),
            terms_url=f"https://{SC_HOST}/privacy-and-data-usage-policy/",
        ),
    )
    caselaw_filters = {
        "court": "jcpc (Privy Council, final court), ca (Court of Appeal) or sc (Supreme Court); default all",
        "year": "year of the judgment, YYYY; or a range YYYY-YYYY, or YYYY- for that year on",
    }
    legislation_filters = {
        "kind": "act (principal Acts), sub (subsidiary legislation) or amd (amending legislation); default all",
    }
    min_interval = {LAWS_HOST: 1.0, SC_HOST: 1.0, CA_HOST: 1.0, "caselaw.nationalarchives.gov.uk": 0.3}
    notes = ("Privy Council (final court) judgments in Bahamian appeals, Nov 2009 on, full-text search, from "
             "Find Case Law (UK National Archives); Court of Appeal (2003-) and Supreme Court (mostly 2019-) "
             "judgments from the courts' own sites (Court of Appeal: case name and catchwords; Supreme Court: title only). Current Acts and subsidiary legislation from the "
             "Statute Law of The Bahamas (Revised Edition PDFs, title search only); post-2016 amendments "
             "are separate items listed under each Act.")
    gaps = (
        ("Privy Council judgments before Nov 2009: only on BAILII (no API, forbids scraping); Find Case "
         "Law's UKPC collection starts 2009"),
        ("Privy Council country filter is heuristic (Find Case Law has no country field): title "
         "'(Bahamas)' or header 'From the Court of Appeal of the Commonwealth of The Bahamas'; a judgment "
         "with neither (header worded otherwise, untitled country) is missed"),
        ("Full-text search: Bahamian court lists match case names (Court of Appeal also catchwords) only; the laws site search "
         "(/cms/search/search.php) is robots-disallowed"),
        "Supreme Court judgments before ~2019: not published online on courts.bs",
        ("Consolidated text with post-2016 amendments merged in: not published (amendments are "
         "separate items)"),
        "Magistrates' courts and tribunals: not researched yet",
    )
    samples = {
        "caselaw_query": "Attorney General",
        "decision_id": "ca/4967",           # Zenard Rolle v DPP, SCCrApp No. 20 of 2026
        "legislation_query": "Penal Code",
        "law_id": "1873-0015",              # Penal Code, Ch. 84
        "provision": "290",                 # Definition of murder
    }

    # ------------------------------------------------------------------ #
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        f = {k: str(v).strip() for k, v in (filters or {}).items() if str(v).strip()}
        court = ""
        if "court" in f:
            court = _COURT_ALIASES.get(f["court"].lower(), "")
            if not court:
                raise BadRequest("court must be jcpc (Privy Council), ca (Court of Appeal) or sc (Supreme Court).")
        year = f.get("year", "")
        ym = _YEAR.match(year) if year else None
        if year and not ym:
            raise BadRequest("year must be YYYY (2024), a range YYYY-YYYY (2020-2024) or YYYY- (2022 on).")
        lo = ym[1] if ym else ""
        hi = (ym[2] or ("9999" if "-" in year or "–" in year else ym[1])) if ym else ""
        if ym and lo > hi:
            raise BadRequest("year range runs backwards; write the earlier year first, e.g. 2020-2024.")

        def in_years(d: str) -> bool:
            return lo <= d[:4] <= hi
        q = _http.clean(query or "")
        limit = max(1, min(int(limit), 50))
        start = (max(1, int(page)) - 1) * limit
        end = start + limit

        jc = [h for h in await jcpc_hits(*_JCPC_BS, q) if not year or in_years(h.date)] if court in ("", "jcpc") else []
        items: list[DecisionHit] = jc[start:end]   # Privy Council first, then the local courts
        start, end = max(0, start - len(jc)), max(0, end - len(jc))
        ca_total = 0
        ca_skipped = ""
        if court in ("", "ca"):             # Court of Appeal: the site's own search
            if year:   # the site only filters on a full day+month+year, so filter by year here
                allca, skip = [], 0
                while True:
                    hits, total = await _ca_search(q, "", skip)
                    if total > CA_YEAR_MAX:   # bounded: never crawl hundreds of pages of the court's site
                        msg = (f"Court of Appeal: {total} decisions match '{q}' and the site cannot filter by "
                               f"year alone; narrow the query to at most {CA_YEAR_MAX} matches, or drop the year "
                               f"filter.")
                        if court == "ca":
                            raise BadRequest(msg)
                        ca_skipped, allca = msg + " Court of Appeal results are NOT included below.", []
                        break
                    allca += hits
                    skip += CA_PAGE
                    if skip >= total or not hits:
                        break
                allca = [h for h in allca if in_years(h.date)]
                ca_total = len(allca)
                items += allca[start:end]
            else:
                skip = start - start % CA_PAGE
                while True:
                    hits, ca_total = await _ca_search(q, year, skip)
                    items += [h for i, h in enumerate(hits, skip) if start <= i < end]
                    skip += CA_PAGE
                    if skip >= min(end, ca_total) or not hits:
                        break
        sc_total = 0
        const_first = False
        if court in ("", "sc"):             # then the Supreme Court list, newest first
            words = _words(q)
            sc = [r for r in await _sc_rows()
                  if (not year or in_years(r["date"])) and _matches(words, r["title"])]
            sc.sort(key=lambda r: r["date"], reverse=True)
            const_first = any(w.startswith("constitution") for w in words)
            if const_first:   # titles that name the Constitution as the subject first
                sc.sort(key=lambda r: not _CONST_SUBJECT.search(r["title"]))
            sc_total = len(sc)
            a, b = max(0, start - ca_total), max(0, end - ca_total)
            items += [_sc_hit(r) for r in sc[a:b]]
        note = ("Privy Council hits first (full-text search, all words, newest first, 2009 on), then Court of "
                "Appeal (the site matches the word in the case name or the catchwords, so a hit is not proof the case "
                "turns on it: open it with get_decision to see the catchwords; site order, oldest first; dates are "
                "the date added to the site), then Supreme Court (every word in the case title only, "
                + ("newest first within each of the two groups described next; " if const_first else "newest first; ") +
                "a word in a title, e.g. 'constitution', may be a party name rather than the subject; the court's "
                "list gives no subject or catchwords, so constitutional cases cannot be told apart here; for "
                "'constitution' titles saying 'Constitutional', 'Constitution of ...' or 'Article <n>' form the first "
                "group, all other titles the second, but that is a title guess: read each hit).")
        if ca_skipped:
            note = ca_skipped + " " + note
        return Results(items=items[:limit], total=len(jc) + ca_total + sc_total, note=note)

    # ------------------------------------------------------------------ #
    async def get_decision(self, id):
        ident = _http.clean(id)
        if is_jcpc_id(ident):
            return await jcpc_decision(ident)
        m = _CA_ID.match(ident)
        if m:
            return await _ca_decision(m[1])
        m = _SC_ID.match(ident)
        if m:
            return await _sc_decision(m[1])
        raise BadRequest("Give an id from search_caselaw: '[2026] UKPC 9' (Privy Council), 'ca/4967' "
                         "(Court of Appeal) or "
                         "'sc/2026/11/RULING-S.V.R.-v.-S.L.R.pdf' (Supreme Court).")

    # ------------------------------------------------------------------ #
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        f = {k: str(v).strip().lower() for k, v in (filters or {}).items() if str(v).strip()}
        kinds = {"act": "prn", "acts": "prn", "principal": "prn", "sub": "subx", "subsidiary": "subx",
                 "amd": "amdx", "amending": "amdx"}
        kind = ""
        if "kind" in f:
            kind = kinds.get(f["kind"], "")
            if not kind:
                raise BadRequest("kind must be act, sub (subsidiary) or amd (amending).")
        q = _http.clean(query or "")
        rows = await _index()
        m = re.fullmatch(_ITEM, q.upper())
        if m:
            hits = [r for r in rows if r["item"] == q.upper()]
        else:
            words = _words(q)
            hits = [r for r in rows if _matches(words, r["title"])]
            # exact / prefix title matches first, then principal Acts, then the rest
            ql = re.sub(r"^the\s+", "", q.lower())

            def _t(r):   # "The Constitution" counts as an exact match for "constitution"
                return re.sub(r"^the\s+", "", r["title"].lower())
            hits.sort(key=lambda r: (_t(r) != ql, not _t(r).startswith(ql), r["kind"] != "prn"))
        if kind:
            hits = [r for r in hits if r["kind"] == kind]
        limit = max(1, min(int(limit), 50))
        start = (max(1, int(page)) - 1) * limit
        items = [LawHit(id=r["id"], title=r["title"], type=_KINDS[r["kind"]][1], number=r["item"],
                        status="current", snippet=f"under {r['parent']}" if r["parent"] else "",
                        url=INDEX_URL) for r in hits[start:start + limit]]
        return Results(items=items, total=len(hits),
                       note=("Title search over the Statute Law index (current legislation). Acts are the "
                             "Revised Edition text; later amending Acts are separate items (amd/...)."))

    async def get_legislation_toc(self, id):
        law = await _law(id)
        entries = law["toc"] or [TocEntry(title="(no Arrangement of Sections found; use get_legislation_text)")]
        return Toc(id=law["id"], title=law["title"], url=law["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        law = await _law(id)
        label = _norm_prov(provision)
        if label not in law["sections"]:
            if not law["sections"]:
                raise NotFound(f"{law['title']}: sections could not be separated in this PDF; "
                               "use get_legislation_text.")
            raise NotFound(f"{law['title']} has no section '{provision}'. Use get_legislation_toc for the labels.")
        return Provision(law_id=law["id"], law_title=law["title"], provision=label,
                         text=(_GARBLE_WARN + "\n\n" if law["garbled"] else "") + law["sections"][label],
                         url=law["url"])

    async def get_legislation_text(self, id):
        law = await _law(id)
        return LawText(id=law["id"], title=law["title"],
                       text=(_GARBLE_WARN + "\n\n" if law["garbled"] else "") + law["text"], url=law["url"], metadata=law["meta"])
