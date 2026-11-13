"""Barbados: judgments and the consolidated laws published by the Barbados Judicial System
(www.barbadoslawcourts.gov.bb, the Supreme Court's own site).

Case law
--------
/judgments/ is a search form (POST, no token) that redirects to a plain GET view:
/case-search-results/?asId=as0&search=<words in the judgment>&court[0]=<court>&page=N,
10 rows a page, "1-10 of 92 results shown". Optional fields used here: casename, judge,
decision_date=between|after|before with date_between_start_date / date_between_end_date /
date_after / date_before (YYYY-MM-DD). Each row links /judgments/<slug>; that page carries
the whole judgment as HTML (section.pdf-content) plus the PDF. The id is the slug. The site
says coverage is "initially ... from 2007 until 2022".

Legislation
-----------
/laws/consolidated-laws/statutes-of-barbados (~540 Acts, by chapter "CAP") and
/laws/consolidated-laws/subsidiary-legislation-of-barbados (~700 instruments) each list
every item on one page, linking a PDF. The PDFs are scans of the printed revised editions
(1971 and L.R.O. 1985 and later reprints) with the source's own OCR text layer: older
texts, OCR errors, marginal notes run into the text. The id is the PDF path below
assets/content/pdfs/ without ".pdf", e.g. "statutes/OccupiersLiabilityCAP208"; a chapter
("Cap. 208", "CAP208") is also accepted. Sections are cut from the PDF text by their
running numbers ("1.", "2.", "3A.").

Final appeals (Caribbean Court of Justice)
------------------------------------------
Barbados's final court is the CCJ (appellate jurisdiction, since 2005). court=ccj searches the
`ccj` adapter's judgment lists (imported read-only, no HTTP code of its own) and keeps the
appeals from Barbados. The CCJ list names the country only for most judgments since 2020
("[2026] CCJ 10 (AJ) BB"); for older rows the country is read from page 1 of the judgment PDF
("ON APPEAL FROM THE COURT OF APPEAL OF BARBADOS", "CCJ Appeal No. BBCR2019/001"), lazily, at
most CCJ_PROBES PDFs per call, and remembered in memory. ccj_appeals() is shared with bz.py.

robots.txt (2026-11-05): Crawl-delay: 10; disallows only /admin/, /includes/, /config/,
/logs/, /backup/ and similar. The site's "Terms & Conditions" footer link is empty (no
terms page). Legislation is not taken from barbadosparliament-laws.com (robots.txt
"Disallow: /").
"""
from __future__ import annotations

import io
import re
import time
from urllib.parse import quote, urlencode, urlsplit

from lxml import html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)
from . import ccj as _ccj

HOST = "www.barbadoslawcourts.gov.bb"
BASE = f"https://{HOST}"
SRC = "Barbados Judicial System"
SRC_PAGE = 10                       # rows per page of the judgment search (fixed by the site)
_TTL = 6 * 3600
_SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,200}$", re.I)
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LISTS = {"statutes": f"{BASE}/laws/consolidated-laws/statutes-of-barbados",
         "subsidiary": f"{BASE}/laws/consolidated-laws/subsidiary-legislation-of-barbados"}
_DIRS = {"statutes": "statutes", "subsidiary": "subsidiary_legislation_of_barbados"}
COURTS = {
    "coa": "Court Of Appeal", "ca": "Court Of Appeal", "appeal": "Court Of Appeal",
    "court of appeal": "Court Of Appeal",
    "hc": "High Court", "high": "High Court", "high court": "High Court",
    "registrar": "Registrar’s Court", "registrar's court": "Registrar’s Court",
    "magistrate": "Magistrate’s Court", "magistrates": "Magistrate’s Court",
    "magistrate's court": "Magistrate’s Court",
}

_lists: dict = {}                   # kind -> (monotonic time, [rows])
_pdfs: dict = {}                    # law id -> (title, url, text)
_decisions: dict = {}


# --------------------------------------------------------------------------- #
# Case law
# --------------------------------------------------------------------------- #
def _court_of(text: str) -> str:
    head = text[:1500].upper()
    for key, name in (("COURT OF APPEAL", "Court of Appeal"), ("HIGH COURT", "High Court"),
                      ("MAGISTRATE", "Magistrate's Court"), ("REGISTRAR", "Registrar's Court")):
        if key in head:
            return name
    return ""


def _decision_date(text: str) -> str:
    m = re.search(r"(?i)date[s]?\s+of\s+(?:decision|judgment|ruling)\s*:?\s*(.{0,60})", text)
    return _http.en_date(m[1]) if m else ""


def _rows(doc) -> list[DecisionHit]:
    out = []
    for tr in doc.xpath('//table[contains(@class,"case-search-results")]/tbody/tr'):
        a = tr.xpath('./td[2]//a[starts-with(@href,"judgments/")]')
        slug = a[0].get("href").split("/", 1)[1].strip("/") if a else ""
        if not slug:
            continue
        tds = tr.xpath("./td")
        cell = [_http.clean(td.text_content()) for td in tds]
        snip = tr.xpath('./td[2]//span[contains(@class,"advsea-extract")]')
        title = _http.clean(a[0].text_content()) or slug
        court = cell[2] if len(cell) > 2 else ""
        if "Appeal, Civil" in court and re.search(r"(?i)\bv\.?\s+(the\s+)?(queen|r\b|dpp|director of public)|"
                                                  r"^(the\s+queen|r|dpp)\s+v\b", title):
            court = "Court Of Appeal, Criminal Division (the site labels it Civil Division)"
        out.append(DecisionHit(
            id=slug, title=title,
            court=court,
            date=_http.iso_date(cell[4]) if len(cell) > 4 else "",
            snippet=_http.clean(snip[0].text_content()) if snip else (cell[3] if len(cell) > 3 else ""),
            url=f"{BASE}/judgments/{quote(slug)}"))
    return out


async def _search_page(params: list, page: int):
    r = await _http.get(f"{BASE}/case-search-results/?{urlencode(params + [('page', page)])}")
    if r.status_code != 200:
        raise SourceError(_http.error(SRC, "judgment search failed", r.status_code), r.status_code)
    doc = lhtml.fromstring(r.text)
    m = re.search(r"(\d+)\s*-\s*(\d+)\s+of\s+(\d+)\s+results", r.text)
    first, total = (int(m[1]), int(m[3])) if m else (0, 0)
    rows = _rows(doc)
    if page > 1 and first != (page - 1) * SRC_PAGE + 1:   # past the last page the site repeats page 1
        rows = []
    return rows, total


async def _decision(slug: str) -> Decision:
    hit = _decisions.get(slug)
    if hit:
        return hit
    url = f"{BASE}/judgments/{quote(slug)}"
    r = await _http.get(url)
    if r.status_code == 404:
        raise NotFound(f"{SRC} has no judgment {url}.")
    if r.status_code != 200:
        raise SourceError(_http.error(SRC, f"judgment {slug} failed", r.status_code), r.status_code)
    doc = lhtml.fromstring(r.text)
    h1 = doc.xpath("//h1")
    title = _http.clean(h1[0].text_content()) if h1 else ""
    body = doc.xpath('//section[contains(@class,"pdf-content")]')
    pdf = doc.xpath('//a[contains(@class,"download-pdfs")]/@href')
    pdf_url = f"{BASE}/{quote(pdf[0].lstrip('/'), safe='/')}" if pdf else ""
    text = _http.html_to_md(lhtml.tostring(body[0], encoding="unicode")) if body else ""
    if len(text) < 200 and pdf_url.lower().endswith(".pdf"):
        p = await _http.get(pdf_url)
        if p.status_code != 200:
            raise SourceError(_http.error(SRC, f"PDF for {slug} failed", p.status_code), p.status_code)
        text = _http.pdf_text(p.content)
    if len(text) < 200:
        if not title or (not body and not pdf):
            raise NotFound(f"{url} is not a judgment page.")
        raise SourceError(f"Error ({SRC}): {url} has no text (scanned PDF, no OCR here); read it there.",
                          "pdf")
    meta = {"PDF": pdf_url} if pdf_url else {}
    d = Decision(id=slug, title=title or f"{SRC} {slug}", text=text, url=url,
                 court=_court_of(text), date=_decision_date(text), metadata=meta)
    return _http.lru_put(_decisions, slug, d, 32)


# --------------------------------------------------------------------------- #
# Final appeals: CCJ judgments from the ccj adapter, kept to one country of origin
# --------------------------------------------------------------------------- #
CCJ_PROBES = 10                     # judgment PDFs read per call to find a row's country
_CCJ_COUNTRIES = {"BB": "Barbados", "BZ": "Belize", "GY": "Guyana", "DM": "Dominica", "LC": "Saint Lucia"}
_LISTED = re.compile(r"(?<![A-Za-z])(BB|BZ|GY|DM|LC)(?![A-Za-z])")
_FROM = re.compile(r"(?i)ON\s+APPEAL\s+FROM\b.{0,200}?\b(BARBADOS|BELIZE|GUYANA|DOMINICA|SAINT\s+LUCIA|"
                   r"ST\.?\s+LUCIA)\b", re.S)
_CCJ_NO = re.compile(r"(?i)CCJ\s+(?:Appeal|Application)\s+No\.?\s*(BB|BZ|GY|DM|LC)")
_origin: dict = {}                  # CCJ citation key -> country code from the PDF ("" = not found)


def _listed_origin(row: dict) -> str:
    """Country code the CCJ list itself gives: citation suffix or the PDF file name."""
    m = _LISTED.search(row["cite"]) or (row["docs"] and _LISTED.search(row["docs"][0]["file"]))
    return m[1] if m else ""


async def _pdf_origin(row: dict) -> str | None:
    """Country from page 1 of the judgment PDF; None when the PDF could not be fetched."""
    docs = row["docs"]
    url = docs[0]["url"] if docs else ""
    if urlsplit(url).hostname != _ccj.HOST or not url.lower().endswith(".pdf"):
        return ""
    r = await _http.get(url)
    if r.status_code != 200 or not r.content.startswith(b"%PDF"):
        return None
    from pypdf import PdfReader
    try:
        first = PdfReader(io.BytesIO(r.content)).pages[0].extract_text() or ""
    except Exception:            # broken PDF: country unknown, not retried
        first = ""
    m = _FROM.search(first)
    if m:
        name = re.sub(r"\s+", " ", m[1].upper()).replace("ST. ", "SAINT ").replace("ST ", "SAINT ")
        return next(k for k, v in _CCJ_COUNTRIES.items() if v.upper() == name)
    m = _CCJ_NO.search(first)
    return m[1].upper() if m else ""


async def ccj_appeals(country: str, query: str, *, limit: int, page: int,
                      date_from: str = "", date_to: str = "") -> Results:
    """CCJ appellate judgments in appeals from `country` (BB, BZ, ...), newest first."""
    j = _ccj.CCJ()
    f = {"jurisdiction": "AJ", **{k: v for k, v in (("date_from", date_from), ("date_to", date_to)) if v}}
    hits, p = [], 1
    while True:
        r = await j.search_caselaw(query, limit=50, page=p, filters=f)
        hits += r.items
        if not r.items or len(hits) >= (r.total or 0):
            break
        p += 1
    rows = await _ccj._rows()
    limit, page = max(1, min(int(limit), 50)), max(1, int(page))
    need = page * limit
    out, probes, unchecked = [], 0, 0
    for h in hits:
        row = rows.get(_ccj._key(h.id))
        if row is None:
            continue
        code = _listed_origin(row) or _origin.get(row["key"])
        if code is None:
            if probes >= CCJ_PROBES or len(out) >= need:
                unchecked += 1
                continue
            probes += 1
            code = await _pdf_origin(row)
            if code is None:
                unchecked += 1
                continue
            _origin[row["key"]] = code
        if code == country:
            out.append(h)
    note = (f"Caribbean Court of Justice appeals from {_CCJ_COUNTRIES[country]}, newest first. Matches "
            "citation and parties (all words), not judgment text. Country from the CCJ list, else from "
            "the judgment PDF's 'On appeal from' line.")
    if unchecked:
        note += (f" {unchecked} older matching CCJ judgment(s) not yet checked for their country (at most "
                 f"{CCJ_PROBES} PDFs read per call): repeat the call or ask the next page, or narrow by words "
                 "or dates.")
    return Results(items=out[(page - 1) * limit: need], total=None if unchecked else len(out), note=note)


# --------------------------------------------------------------------------- #
# Legislation
# --------------------------------------------------------------------------- #
def _cap(s: str) -> str:
    """'Cap. 208', 'CAP208', 'cap 47' -> '208' / '47' (leading zeros dropped, letter kept)."""
    m = re.search(r"(?i)\bcap\.?\s*0*(\d+[A-Z]?)\b", s or "")
    return m[1].upper() if m else ""


async def _list(kind: str) -> list[dict]:
    hit = _lists.get(kind)
    if hit and time.monotonic() - hit[0] < _TTL:
        return hit[1]
    r = await _http.get(LISTS[kind])
    if r.status_code != 200:
        raise SourceError(_http.error(SRC, f"{kind} list failed", r.status_code), r.status_code)
    doc = lhtml.fromstring(r.text)
    prefix = f"assets/content/pdfs/{_DIRS[kind]}/"
    rows, seen = [], set()
    for a in doc.xpath('//ul[contains(@class,"ap_results")]//a[@href]'):
        href = a.get("href").lstrip("/")
        if not href.startswith(prefix) or not href.lower().endswith(".pdf"):
            continue
        stem = href[len(prefix):-4]
        if stem in seen:
            continue
        seen.add(stem)
        title = _http.clean(a.text_content())
        rows.append({"id": f"{kind}/{stem}", "title": title, "kind": kind,
                     "cap": _cap(title) if kind == "statutes" else "",
                     "url": f"{BASE}/{quote(href, safe='/')}"})
    if not rows:
        raise SourceError(f"Error ({SRC}): no laws found on {LISTS[kind]} (layout changed?).", "layout")
    _lists[kind] = (time.monotonic(), rows)
    return rows


async def _find(ident: str) -> dict:
    ident = (ident or "").strip()
    kind, _, stem = ident.partition("/")
    if kind in LISTS and stem:
        row = next((r for r in await _list(kind) if r["id"] == ident), None)
        if not row:
            raise NotFound(f"No {kind} item {stem!r} on {LISTS[kind]}.")
        return row
    cap = _cap(ident) or (ident.upper().lstrip("0") if re.fullmatch(r"\d{1,3}[A-Za-z]?", ident) else "")
    if cap:
        row = next((r for r in await _list("statutes") if r["cap"] == cap), None)
        if not row:
            raise NotFound(f"No Statute of Barbados with chapter Cap. {cap} on {LISTS['statutes']}.")
        return row
    raise BadRequest("Give an id from search_legislation (e.g. 'statutes/OccupiersLiabilityCAP208', "
                     "'subsidiary/AdoptionRegulations,1986Cap212'A') or a chapter ('Cap. 208').")


_NOISE = [re.compile(p) for p in (
    r"(?i)^T\w{1,3}\s+L\w{1,4}S\s+OF\s+B\w{4,8}$",              # THE LAWS OF BARBADOS (OCR'd)
    r"(?i)^Pr\w*\s+(in England\s+)?by\b",                       # Printed by ...
    r"(?i)\b\w*thor\w*\s+of\s+the\s+Gov\w*",                     # by the authority of the Government (OCR'd)
    r"(?i)^by\s+authority\b",
)]
_HEADER = re.compile(r"\bCAP\s*\.?\s*\d")                     # running heads use upper-case CAP.


def _clean_law(text: str) -> str:
    out = []
    for ln in text.splitlines():
        if ln and (any(p.search(ln) for p in _NOISE) or (_HEADER.search(ln) and len(ln) < 100)):
            continue
        out.append(ln)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip()


_SEC = re.compile(r"^(\d{1,3}[A-Z]{0,2})\.\s*(?=\S)")


def _next_labels(label: str) -> set[str]:
    m = re.match(r"^(\d+)([A-Z]*)$", label)
    n, suf = int(m[1]), m[2]
    out = {str(n + 1), f"{n}A" if not suf else f"{n}{chr(ord(suf[-1]) + 1)}"}
    if suf:
        out.add(f"{n}{suf}A")
    return out


def _skip_labels(label: str) -> set[str]:
    """Plain numbers two or three ahead: the OCR often loses a number that follows a margin
    note on the same line ("perishing 8. Where ..."), so the body chain would otherwise break."""
    n = int(re.match(r"\d+", label)[0])
    return {str(n + 2), str(n + 3)}


def _chain(lines: list[str], start: int) -> list[tuple[str, int]]:
    out = [("1", start)]
    expect = _next_labels("1")
    skip = _skip_labels("1")
    for i in range(start + 1, len(lines)):
        m = _SEC.match(lines[i])
        if m and (m[1] in expect or m[1] in skip):
            out.append((m[1], i))
            expect = _next_labels(m[1])
            skip = _skip_labels(m[1])
    return out


def _sections(text: str) -> list[tuple[str, str]]:
    """Cut a law's OCR text into (label, text) by its running section numbers. The arrangement
    of sections also starts "1.", so the longest chain wins (the later one, the body, if nearly as long)."""
    lines = text.splitlines()
    chains = [_chain(lines, i) for i, ln in enumerate(lines) if re.match(r"^1\.\s*\S", ln)]
    top = max((len(c) for c in chains), default=0)
    # the body comes after the arrangement, but OCR can drop numbers from it: take the latest
    # chain that is nearly as long as the longest
    best = max((c for c in chains if len(c) >= 0.8 * top), key=lambda c: c[0][1], default=[])
    if not best:
        return []
    out = []
    for k, (label, i) in enumerate(best):
        j = best[k + 1][1] if k + 1 < len(best) else len(lines)
        out.append((label, "\n".join(lines[i:j]).strip()))
    return out


_FOOTNOTE = re.compile(r"(?m)^\W{0,2}This (?:Act|Law|Order) was formerly [^\n]*(?:\n[^\n(]{0,40}\d{4}-\d+\.?)?[^\n]*(?:\n|$)")


def _drop_margin(text: str) -> str:
    """Drop runs of 3+ very short lines: the scan's margin column (side notes, years, the next
    entry's "Cap." heading) that the text layer prints as a block. Words of the margin that
    share a line with the text cannot be separated."""
    text = _FOOTNOTE.sub("", text)    # printed footnote on the old title, not part of the section
    lines, out, run = text.splitlines(), [], []
    for ln in lines + [""]:
        if ln.strip() and len(ln.strip()) <= 20 and not ln.lstrip().startswith("("):
            run.append(ln)
            continue
        if len(run) < 3:
            out += run
        run = []
        out.append(ln)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out[:-1])).strip()


async def _law(row: dict) -> str:
    hit = _pdfs.get(row["id"])
    if hit:
        return hit
    r = await _http.get(row["url"])
    if r.status_code == 404:
        raise NotFound(f"{row['url']} is missing at the source.")
    if r.status_code != 200 or not r.content.startswith(b"%PDF"):
        raise SourceError(_http.error(SRC, f"PDF {row['id']} failed", r.status_code), r.status_code)
    text = _clean_law(_http.pdf_text(r.content))
    if len(text) < 200:
        raise SourceError(f"Error ({SRC}): {row['url']} has no text layer (scan; no OCR here); "
                          "read it there.", "pdf")
    return _http.lru_put(_pdfs, row["id"], text, 8)


def _norm_prov(p: str) -> str:
    m = re.fullmatch(r"(?i)\s*(?:s(?:ec(?:tion)?)?|art(?:icle)?|§)?\.?\s*(\d{1,3}[a-z]{0,2})\.?\s*", p or "")
    if not m:
        raise BadRequest("provision is a section number: '4', 's. 4', 'section 3A'.")
    return m[1].upper()


# --------------------------------------------------------------------------- #
class Barbados(Jurisdiction):
    code = "bb"
    name = "Barbados"
    languages = ("en",)
    aliases = ("barbados", "brb")
    _terms = ("'Copyright Barbados Judicial System 2015 - 2026. All Rights Reserved.' No licence; the "
              "'Terms & Conditions' footer link is empty (no terms page, checked 2026-11-05); silent on "
              "reuse and automated access")
    sources = (
        Source(
            name="Barbados Judicial System: judgments (barbadoslawcourts.gov.bb)",
            url=f"{BASE}/judgments/",
            covers=("caselaw",),
            licence=_terms,
            commercial_use=None,
            ai_use=None,   # robots.txt: Crawl-delay 10, no AI/TDM clause
            auth="none",
            rate_limit="robots.txt Crawl-delay: 10 (honoured: 10 s spacing); no 429 in ~12 requests (2026-11)",
            terms_url=f"{BASE}/robots.txt",
        ),
        Source(
            name="Barbados Judicial System: Consolidated Laws (barbadoslawcourts.gov.bb)",
            url=f"{BASE}/laws/consolidated-laws",
            covers=("legislation",),
            licence=_terms,
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="robots.txt Crawl-delay: 10 (honoured: 10 s spacing; law lists cached in memory 6 h)",
            terms_url=f"{BASE}/robots.txt",
            warning=("Laws are OCR text of scanned printed revised editions (1971 / L.R.O. 1985 and "
                     "later reprints): may predate amendments and contain OCR errors; check the PDF."),
        ),
        _ccj.CCJ.sources[0],          # court=ccj: final appeals, through the ccj adapter
    )
    caselaw_filters = {
        "court": ("ccj (Caribbean Court of Justice: final appeals from Barbados, 2005-), coa (Court of "
                  "Appeal), hc (High Court), registrar, magistrate; default all courts on the Judiciary site"),
        "judge": "judge as the site lists it, e.g. 'Reifer J', 'Goodridge JA'",
        "casename": "words in the case name",
        "date_from": "decided on or after, YYYY-MM-DD",
        "date_to": "decided on or before, YYYY-MM-DD",
    }
    legislation_filters = {"kind": "statutes (Acts, by chapter) or subsidiary (regulations, orders, rules); default both"}
    min_interval = {HOST: 10.0, _ccj.HOST: 1.0}
    notes = ("Judgments (Court of Appeal, High Court, Registrar, Magistrates; mostly 2007-2022) and "
             "the consolidated Laws of Barbados from the Judiciary's site. Laws are OCR'd scans of old "
             "revised editions. The site asks for 10 s between requests, so calls are slow. Final "
             "appeals (Caribbean Court of Justice, 2005-): court=ccj.")
    gaps = (
        ("Up-to-date consolidated laws: only OCR of scanned revised editions (1971 / L.R.O. 1985);"
         " later amendments may be missing"),
        "Barbados Parliament laws site (barbadosparliament-laws.com): robots.txt Disallow: /",
        ("Judgments outside 2007-2022: site coverage is 'initially ... from 2007 until 2022' (not "
         "published online)"),
        "Acts passed after the last printed revision: not researched yet",
        ("CCJ appeals (court=ccj): matched on citation and parties only, not judgment text (the CCJ"
         " lists have no full-text search)"),
        ("Privy Council appeals from Barbados (final court until 2005): Find Case Law has UKPC only"
         " from 2009, BAILII forbids scraping"),
    )
    samples = {
        "caselaw_query": "negligence",
        "decision_id": "wendy-popo-v-ag",
        "legislation_query": "occupiers liability",
        "law_id": "statutes/OccupiersLiabilityCAP208",
        "provision": "4",
    }

    # ------------------------------------------------------------------ #
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        f = {k: _http.clean(v) for k, v in (filters or {}).items() if _http.clean(v)}
        q = _http.clean(query or "")
        if f.get("court", "").lower() in ("ccj", "caribbean court of justice"):
            if f.get("judge") or f.get("casename"):
                raise BadRequest("court=ccj takes search words and date_from / date_to only.")
            for d in (f.get("date_from", ""), f.get("date_to", "")):
                if d and not _DATE.match(d):
                    raise BadRequest("date_from / date_to must be YYYY-MM-DD.")
            return await ccj_appeals("BB", q, limit=limit, page=page,
                                     date_from=f.get("date_from", ""), date_to=f.get("date_to", ""))
        params: list[tuple[str, str]] = [("asId", "as0")]
        if q:
            params.append(("search", q))
        if f.get("casename"):
            params.append(("casename", f["casename"]))
        if f.get("judge"):
            params.append(("judge", f["judge"]))
        court = "all"
        if f.get("court"):
            court = COURTS.get(f["court"].lower().replace("’", "'"), "")
            if not court:
                raise BadRequest("court must be ccj (Caribbean Court of Justice), coa (Court of Appeal), "
                                 "hc (High Court), registrar or magistrate.")
        params.append(("court[0]", court))
        d0, d1 = f.get("date_from", ""), f.get("date_to", "")
        for d in (d0, d1):
            if d and not _DATE.match(d):
                raise BadRequest("date_from / date_to must be YYYY-MM-DD.")
        if d0 and d1:
            params += [("decision_date", "between"), ("date_between_start_date", d0),
                       ("date_between_end_date", d1)]
        elif d0:
            params += [("decision_date", "after"), ("date_after", d0)]
        elif d1:
            params += [("decision_date", "before"), ("date_before", d1)]
        if not (q or f.get("casename") or f.get("judge") or d0 or d1):
            raise BadRequest("Give search words, or a casename / judge / date filter.")
        if int(limit) > 20:                       # 10 s per source page: keep calls short
            raise BadRequest(f"limit must be at most 20 for Barbados judgment searches (the site asks for 10 s "
                             f"between requests), got {limit}; use page to walk further.")
        limit = max(1, int(limit))
        page = max(1, int(page))
        start, end = (page - 1) * limit, page * limit
        items: list[DecisionHit] = []
        total = None
        p = start // SRC_PAGE + 1
        while (p - 1) * SRC_PAGE < end:
            rows, total = await _search_page(params, p)
            items += [h for i, h in enumerate(rows, (p - 1) * SRC_PAGE) if start <= i < end]
            if len(rows) < SRC_PAGE or p * SRC_PAGE >= (total or 0):
                break
            p += 1
        return Results(items=items, total=total,
                       note=("Searches the words of the judgment text (site coverage mostly 2007-2022). "
                             "The site's order: relevance. Court and Division are the site's own labels and are "
                             "sometimes wrong (criminal appeals shown as 'Civil Division'): check the heading of "
                             "the judgment before citing. Final appeals (CCJ): court=ccj."))

    async def get_decision(self, id):
        if re.search(r"(?i)\bCCJ\b", id or ""):
            return await _ccj.CCJ().get_decision(id)
        slug = (id or "").strip().strip("/")
        slug = re.sub(r"^(?:https?://[^/]+)?/?judgments/", "", slug)
        if not _SLUG.match(slug):
            raise BadRequest("Give a judgment id from search_caselaw, e.g. 'wendy-popo-v-ag', or a CCJ "
                             "citation such as '[2020] CCJ 1 (AJ)'.")
        return await _decision(slug)

    # ------------------------------------------------------------------ #
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        kind = _http.clean((filters or {}).get("kind", "")).lower()
        if kind and kind not in LISTS:
            raise BadRequest("kind must be statutes or subsidiary.")
        q = _http.clean(query or "")
        cap = _cap(q)
        words = [w.lower() for w in re.findall(r"\w+", re.sub(r"(?i)\bcap\.?\s*\d+\w*", "", q))]
        rows = []
        for k in ([kind] if kind else list(LISTS)):
            for r in await _list(k):
                hay = r["title"].lower()
                if cap and _cap(r["title"]) != cap:
                    continue
                if all(re.search(rf"\b{re.escape(w)}", hay) for w in words):
                    rows.append(r)
        limit = max(1, min(int(limit), 50))
        page = max(1, int(page))
        items = [LawHit(id=r["id"], title=r["title"],
                        type="Statute" if r["kind"] == "statutes" else "Subsidiary legislation",
                        number=f"Cap. {r['cap']}" if r["cap"] else "", url=r["url"])
                 for r in rows[(page - 1) * limit: page * limit]]
        return Results(items=items, total=len(rows),
                       note=("Matches words in the title (and 'Cap. N'); texts are old revised editions. This "
                             "source has no Acts passed after the last printed revision (e.g. recent Data "
                             "Protection, Sexual Harassment or Employment Rights Acts): 0 results does not mean "
                             "no such law; check the Barbados Parliament or Government Printing Department."))

    async def get_legislation_toc(self, id):
        row = await _find(id)
        secs = _sections(await _law(row))
        entries = [TocEntry(title=f"Section {lb}: {_http.clean(t.splitlines()[0])[len(lb) + 1:][:90].strip()}",
                            provision=lb) for lb, t in secs]
        if not entries:
            raise SourceError(f"Error ({SRC}): no numbered sections found in {row['url']}; "
                              "use get_legislation_text.", "parse")
        return Toc(id=row["id"], title=row["title"], url=row["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        row = await _find(id)
        want = _norm_prov(provision)
        secs = _sections(await _law(row))
        for k, (lb, t) in enumerate(secs):
            if lb == want:
                nxt = secs[k + 1][0] if k + 1 < len(secs) else ""
                gap = (f"\n\nNote: the OCR lost the number(s) between section {lb} and section {nxt}; "
                       "the text of the missing section(s) is inside this section's text above."
                       if nxt and nxt not in _next_labels(lb) else "")
                return Provision(law_id=row["id"], law_title=row["title"], provision=lb,
                                 text=(f"**Section {lb}**\n\nNOT QUOTABLE: this is OCR of a scan and the printed side "
                                       "headings (marginal notes) are mixed into the sentences (e.g. 'Apportion-' or "
                                       "'neglgence.' inside the text), with OCR typos; footnotes and the next entry's "
                                       "heading can be there too. This tool cannot give clean text: quote from the PDF "
                                       f"at the Source URL, not from below.\n\n---\n\n{_drop_margin(t)}{gap}"),
                                 url=row["url"])
        raise NotFound(f"No section {want} found in {row['title']} (OCR text; see get_legislation_toc).")

    async def get_legislation_text(self, id):
        row = await _find(id)
        return LawText(id=row["id"], title=row["title"], text=await _law(row), url=row["url"],
                       metadata={"Edition": "printed revised edition (see first page), OCR text layer"})
