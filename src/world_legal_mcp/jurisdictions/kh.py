"""Cambodia: laws and regulations published by the Council for the Development of Cambodia
(CDC, cdc.gov.kh), mostly in the CDC's unofficial English translations.

How the source works (verified 2026-11-06, UK IP, honest User-Agent):
  * One WordPress page, /laws-and-regulations/, lists ~180 documents under "LEGAL FRAMEWORK",
    grouped by <h3 class="parent"> category (Business, Codes & Ancillary Laws, Constitution,
    Land, Tax & Accounting, ...). Each entry is a link to a PDF in /wp-content/uploads/YYYY/MM/.
    There is no search, so the list is fetched once, kept in memory for _TTL, and searched here.
  * The id is the PDF's own upload path, e.g. "2022/04/THE-CONSTITUTION.pdf".
  * English PDFs have a clean text layer. The Khmer originals are either scanned (no text) or
    typed in a legacy ASCII font (Limon: "RBHraCRkm" for "ព្រះរាជក្រម"), so their text cannot be
    quoted; such a document raises SourceError pointing to the PDF.
  * The page says: "English translation of the provisions of laws and regulations quoted herein
    is unofficial and any provision ... shall be ultimately interpreted according to the
    official Khmer versions." Texts are as published (often as enacted, not consolidated):
    e.g. the Constitution is the 1993 text without later amendments.
  * robots.txt (2026-11-05/06): only /wp-admin/ disallowed. No terms-of-use page (none in the
    page sitemap), nothing on automated access.

Not used (2026-11-06):
  * moj.gov.kh, ccc.gov.kh (Constitutional Council), senate.gov.kh, ocm.gov.kh (Royal Gazette):
    F5 "Request Rejected" firewall page even for robots.txt.
  * mef.gov.kh: Cloudflare "Just a moment..." challenge. moc.gov.kh: 403 maintenance page.
  * nac.org.kh (National Assembly law lists by legislature): PDFs are scanned or in legacy
    Khmer fonts; list pages intermittently answer HTTP 500.
  * supremecourt.gov.kh (judgment lists): the judgment PDFs on asset.cambodia.gov.kh mostly
    answer 404; the one that loaded was a scan with no text layer. No usable case law.
  * archive.eccc.gov.kh (ECCC documents): robots.txt answers HTTP 500 (treated as full
    disallow) and pages carry <meta name="robots" content="noindex">.
"""
from __future__ import annotations

import re
import time
from urllib.parse import unquote

from lxml import html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import LawHit, LawText, Provision, Results, Toc, TocEntry

HOST = "cdc.gov.kh"
BASE = f"https://{HOST}"
LIST_URL = f"{BASE}/laws-and-regulations/"
UPLOADS = f"{BASE}/wp-content/uploads/"
SOURCE = "Council for the Development of Cambodia"
MAX_BYTES = 15_000_000          # largest PDF we download (HEAD-checked first)
_TTL = 6 * 3600
_ID = re.compile(r"^(\d{4}/\d{2}/[^/\\?#]{1,250}\.pdf)$", re.I)
# The "Law on Investment (2021)" entry links to an HTML page; its English PDF is this upload.
_LOI_2021 = ("https://cdc.gov.kh/law-on-investment-2021/", "2022/04/LOI_English-Updated-13Dec21.pdf")
_KHMER = re.compile(r"[ក-៿]|(?:^|[_\-\s])(?:kh|khmer)(?:[_\-\s.]|$)|in-khmer", re.I)
_ENGLISH = re.compile(r"\b(?:the|of|and|shall|article)\b", re.I)
_ART = re.compile(r"^(?:article|art\.)\s*(\d{1,4})\s*(?:\((?:new|bis|ter|\d{1,2})\))?\s*(?:$|[:.\-–]\s*(.*)$)",
                  re.I)
_HEAD = re.compile(r"^(BOOK|PART|TITLE|CHAPTER|SECTION|Book|Part|Title|Chapter|Section)\s+"
                   r"([IVXLCDM]+|\d+|[A-Z]{3,}|One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten)\b(?!\s+of\b)")
_LEVEL = {"book": 0, "part": 0, "title": 0, "chapter": 1, "section": 2}

_list_cache: dict = {}
_text_cache: dict = {}


def _date(s: str) -> str:
    """Trailing CDC date stamp 'Law on Insolvency_071016' -> '2007-10-16' (YYMMDD)."""
    m = re.search(r"_\s*(\d{2})(\d{2})(\d{2})\b", s or "")
    if not m or not (1 <= int(m[2]) <= 12 and 1 <= int(m[3]) <= 31):
        return ""
    yy = int(m[1])
    return f"{1900 + yy if yy >= 50 else 2000 + yy}-{m[2]}-{m[3]}"


def _title(s: str) -> str:
    s = _http.clean(s).lstrip("» ").strip()
    return _http.clean(re.sub(r"\s*_\s*\d{6}\s*$", "", s)) or s


def _norm_id(id: str) -> str:
    s = unquote(_http.clean(id))
    for prefix in (UPLOADS, UPLOADS.replace("https://", "http://"), "/wp-content/uploads/"):
        if s.startswith(prefix):
            s = s[len(prefix):]
    if not _ID.match(s):
        raise BadRequest(f"Not a CDC document id: {id!r}. Use the upload path from search_legislation, "
                         f"e.g. '2022/04/THE-CONSTITUTION.pdf'.")
    return s


async def _list() -> list[dict]:
    hit = _list_cache.get("all")
    if hit and time.monotonic() - hit[0] < _TTL:
        return hit[1]
    r = await _http.get(LIST_URL)
    if r.status_code != 200:
        raise SourceError(_http.error(SOURCE, "law list failed", r.status_code), r.status_code)
    doc = lhtml.fromstring(r.text)
    h = doc.xpath('//h3[normalize-space()="LEGAL FRAMEWORK"]')
    if not h:
        raise SourceError(f"Error ({SOURCE}): law list page changed (no LEGAL FRAMEWORK section).", 200)
    items, seen, cat = [], set(), ""
    for el in h[0].getparent().iter("h3", "a"):
        if el.tag == "h3":
            if "parent" in (el.get("class") or ""):
                cat = _http.clean(el.text_content())
            continue
        href = (el.get("href") or "").strip()
        if href.rstrip("/") == _LOI_2021[0].rstrip("/"):
            href = UPLOADS + _LOI_2021[1]
        if not href.startswith(UPLOADS):
            continue
        id = unquote(href[len(UPLOADS):])
        if not _ID.match(id) or id in seen:
            continue
        seen.add(id)
        raw = _http.clean(el.text_content())
        khmer = bool(_KHMER.search(id))
        items.append({"id": id, "title": _title(raw) or id, "category": cat or "General",
                      "date": _date(raw) or _date(id), "url": UPLOADS + id, "khmer": khmer})
    _http.lru_put(_list_cache, "all", (time.monotonic(), items), 1)
    return items


async def _meta(id: str) -> dict:
    for it in await _list():
        if it["id"] == id:
            return it
    name = re.sub(r"\.pdf$", "", id.rsplit("/", 1)[-1], flags=re.I).replace("-", " ").replace("_", " ")
    return {"id": id, "title": _http.clean(name), "category": "", "date": _date(id),
            "url": UPLOADS + id, "khmer": bool(_KHMER.search(id))}


async def _lines(id: str) -> tuple[dict, list[str]]:
    meta = await _meta(id)
    if id in _text_cache:
        return meta, _text_cache[id]
    url = meta["url"]
    h = await _http.request("HEAD", url)
    if h.status_code == 404:
        raise NotFound(f"No CDC document {id!r} (HTTP 404).")
    if h.status_code != 200:
        raise SourceError(_http.error(SOURCE, "document lookup failed", h.status_code), h.status_code)
    size = int(h.headers.get("content-length") or 0)
    if not size or size > MAX_BYTES:
        raise SourceError(f"Error ({SOURCE}): {id} is {size or 'of unknown'} bytes; only PDFs up to "
                          f"{MAX_BYTES // 1_000_000} MB are read. Open it directly: {url}", 413)
    r = await _http.get(url)
    if r.status_code != 200 or not r.content.startswith(b"%PDF"):
        raise SourceError(_http.error(SOURCE, "PDF download failed", r.status_code), r.status_code)
    text = _http.pdf_text(r.content)
    if len(_ENGLISH.findall(text)) < 20:
        raise SourceError(f"Error ({SOURCE}): {id} has no usable text layer (a scan or a Khmer original "
                          f"typed in a legacy, non-Unicode font); no OCR here. Open the PDF: {url}", 200)
    lines = [ln for ln in text.splitlines() if not re.fullmatch(r"\d{1,4}|-\s*\d{1,4}\s*-", ln)]
    return meta, _http.lru_put(_text_cache, id, lines, 6)


def _parse(lines: list[str]) -> tuple[list[tuple[str, int, str]], list[str]]:
    """Mark structure: returns (marks, lines) where marks = [(kind, line index, label/title)].
    kind 'h<level>' for Book/Part/Chapter/Section headings, 'a' for articles."""
    marks, seen = [], {}
    for i, ln in enumerate(lines):
        if len(ln) > 120:
            continue
        m = _ART.match(ln)
        if m:
            n = m[1]
            seen[n] = seen.get(n, 0) + 1
            label = f"Article {n}" + (f" ({seen[n]})" if seen[n] > 1 else "")
            marks.append(("a", i, label))
            continue
        m = _HEAD.match(ln)
        if m:
            title = ln
            nxt = lines[i + 1] if i + 1 < len(lines) else ""
            if (re.fullmatch(r"\S+\s+\S+\s*:?", ln) and nxt.isupper() and len(nxt) < 100
                    and not _ART.match(nxt) and not _HEAD.match(nxt)):
                title = f"{ln.rstrip(' :')}: {nxt}"
            marks.append((f"h{_LEVEL[m[1].lower()]}", i, title))
    return marks, lines


def _md(lines: list[str], marks) -> str:
    at = {i: (k, t) for k, i, t in marks}
    out = []
    for i, ln in enumerate(lines):
        k, t = at.get(i, ("", ""))
        if k == "a":
            out.append(f"\n\n### {ln}\n")
        elif k:
            out.append(f"\n\n## {ln}\n")
        else:
            out.append(ln + "\n")
    return re.sub(r"\n{3,}", "\n\n", "".join(out)).strip()


def _label(provision: str) -> str:
    s = _http.clean(provision)
    m = re.fullmatch(r"(?:article|art\.?|arts?)?\s*(\d{1,4})\s*(\(\d{1,2}\))?", s, re.I)
    if not m:
        raise BadRequest(f"Provision {provision!r} not understood; use an article label such as "
                         f"'Article 5' (or '5', 'art. 5').")
    return f"Article {int(m[1])}" + (f" {m[2]}" if m[2] else "")


class Cambodia(Jurisdiction):
    code = "kh"
    name = "Cambodia"
    languages = ("en", "km")
    aliases = ("cambodia", "kampuchea", "kingdom of cambodia", "khm")
    sources = (
        Source(
            name="Council for the Development of Cambodia (CDC): Laws and Regulations",
            url=LIST_URL,
            covers=("legislation",),
            licence="unknown (no terms of use published)",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~15 requests (2026-11)",
            terms_url=LIST_URL,
            warning=("Unofficial English translations published by the CDC; the official Khmer text "
                     "prevails. Texts are as published (often as enacted, not consolidated)."),
        ),
    )
    legislation_filters = {"category": "CDC category, e.g. 'Business', 'Land', 'Tax & Accounting', "
                                       "'Codes & Ancillary Laws' (case-insensitive substring)",
                           "date_from": "YYYY[-MM-DD]: only laws whose date is known and not earlier. The date "
                                        "is read from the CDC file title (about half the list has none; "
                                        "those are left out when a date filter is set)",
                           "date_to": "YYYY[-MM-DD]: only laws whose date is known and not later"}
    min_interval = {HOST: 1.0}
    notes = ("Legislation only: ~180 laws, sub-decrees and prakas listed by the CDC, mostly unofficial "
             "English translations; Khmer originals are scans or legacy-font PDFs without usable text. "
             "No case law source is reachable.")
    gaps = (
        "Criminal Code and other penal codes: not in the CDC list (business-relevant laws only), so not covered by this source",
        "Royal Gazette and wider legislation (ocm.gov.kh, moj.gov.kh, senate.gov.kh): blocks our client (F5 'Request Rejected')",
        "Official Khmer texts: scans only, no text (or legacy-font PDFs with unusable text)",
        "Constitutional Council decisions (ccc.gov.kh): blocks our client (F5 firewall)",
        "Supreme Court judgments: PDFs mostly 404; the one that loaded was a scan with no text (2026-11-06)",
        "ECCC tribunal documents (archive.eccc.gov.kh): robots.txt disallows (HTTP 500, treated as disallow; noindex)",
    )
    samples = {
        "legislation_query": "arbitration",
        "law_id": "2022/04/THE-CONSTITUTION.pdf",
        "provision": "Article 1",
    }

    async def search_legislation(self, query, *, limit, page, filters):
        items = await _list()
        cat = _http.clean((filters or {}).get("category", "")).lower()
        if cat:
            cats = sorted({it["category"] for it in items})
            items = [it for it in items if cat in it["category"].lower()]
            if not items:
                raise BadRequest(f"Unknown category {filters['category']!r}. Categories: {', '.join(cats)}.")
        f = filters or {}
        lo, hi = _http.clean(f.get("date_from", "")), _http.clean(f.get("date_to", ""))
        undated = 0
        if lo or hi:
            undated = sum(1 for it in items if not it["date"])
            items = [it for it in items if it["date"] and (not lo or it["date"][:len(lo)] >= lo)
                     and (not hi or it["date"][:len(hi)] <= hi)]
        q = (query or "").lower()
        q = re.sub(r"\blabour\b", "labor", q)       # CDC titles use the US spelling
        words = [w for w in re.split(r"\s+", q) if w]

        def has(hay: str, w: str) -> bool:
            return bool(re.search(rf"(?<!\d){re.escape(w)}(?!\d)", hay)) if w.isdigit() else w in hay
        hits = [it for it in items
                if all(has(f"{it['title']} {it['category']} {it['id']}".lower(), w) for w in words)]
        note = "CDC list of business-relevant laws; English texts are unofficial translations."
        if re.search(r"\bcivil\s+code\b", q) and not any(re.fullmatch(r"(?:the\s+)?civil code", it["title"], re.I)
                                                          for it in items):
            note += (" The Civil Code itself is not in this list, only its implementing law and the "
                     "Code of Civil Procedure.")
        if re.search(r"criminal|penal", q):
            note += " Criminal and penal codes are not covered by this source (business-relevant laws only)."
        if lo or hi:
            note += (f" Date filter uses the date in the CDC file title; {undated} undated entries "
                     f"are left out.")
        start = (max(1, page) - 1) * limit
        out = [LawHit(id=it["id"], title=it["title"], type=it["category"], date=it["date"], url=it["url"],
                      number=(re.search(r"(?:#|No[._ ]?)\s*(\d+)", it["title"]) or [None, ""])[1],
                      snippet=("Khmer original (scan or legacy font: text not extractable)" if it["khmer"]
                               else "English (unofficial CDC translation)"))
               for it in hits[start:start + limit]]
        return Results(items=out, total=len(hits), note=note)

    async def get_legislation_toc(self, id):
        id = _norm_id(id)
        meta, lines = await _lines(id)
        marks, _ = _parse(lines)
        entries = [TocEntry(title=lines[i] if k == "a" else t, level=3 if k == "a" else int(k[1]),
                            provision=t if k == "a" else "") for k, i, t in marks]
        if not any(e.provision for e in entries):
            raise SourceError(f"Error ({SOURCE}): no article structure found in {id}; use "
                              f"get_legislation_text.", 200)
        return Toc(id=id, title=meta["title"], url=meta["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        id = _norm_id(id)
        label = _label(provision)
        meta, lines = await _lines(id)
        marks, _ = _parse(lines)
        for n, (k, i, t) in enumerate(marks):
            if k == "a" and t == label:
                end = marks[n + 1][1] if n + 1 < len(marks) else len(lines)
                seg = lines[i:end]
                return Provision(law_id=id, law_title=meta["title"], provision=label,
                                 text=_md(seg, [("a", 0, label)]), url=meta["url"])
        raise NotFound(f"{label} not found in {id}; see get_legislation_toc for the labels.")

    async def get_legislation_text(self, id):
        id = _norm_id(id)
        meta, lines = await _lines(id)
        marks, _ = _parse(lines)
        md = {"source": SOURCE, "language": "English (unofficial translation)"}
        if meta["category"]:
            md["category"] = meta["category"]
        return LawText(id=id, title=meta["title"], text=_md(lines, marks), url=meta["url"], metadata=md)
