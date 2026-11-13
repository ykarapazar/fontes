"""Rwanda: Portal of Rwandan Laws and Case Laws (amategeko.gov.rw), run by the Rwanda Law
Reform Commission (legislation) and the Judiciary (judgments, law reports).

The site is a React app over a JSON API at apis.amategeko.gov.rw/v1/site/:

* `documents/search?start=&length=&language=en|rw|fr&search=<full text>[&section=..]`
  `[&collection=<court id>][&category=<id>][&year=YYYY][&decisionsStatus=1|2]`
  Elasticsearch over the documents' PDF text; one hit per file with `document_id`,
  `file_id`, name, date, case/law number, court (`collection`) and highlights.
  `language` keeps files in that language. `recordsFiltered` is the hit count.
  Sections: 1.1 laws in force, 1.2 abrogated laws, 2.1 judgments, 2.2.x law reports.
* `documents-files/table?document=<document_id>` lists a document's files (one per
  language set); `documents-files/<file_id>` adds `file_url`, a one-hour presigned link
  to the PDF on files.amategeko.gov.rw (MinIO).

The id is the portal's document_id. Judgments are one-language PDFs. Laws are the Official
Gazette pages: Kinyarwanda, English and French side by side in three columns, as published
(not consolidated; amending laws are separate documents). The English column is cut out by
the x position of the text (pypdf), then split into articles ("Article One:", "Article 2:").

`documents-files/text/<id>` (per-page text) answered 502 twice and the API was briefly down
after it, so it is not used. PDFs are fetched with a Range header so a huge file is refused
after MAX_PDF bytes instead of downloaded.

robots.txt (2026-11-05): amategeko.gov.rw and backend.amategeko.gov.rw "Disallow:" (all
allowed); apis. has none (404); files. has none (MinIO answers AccessDenied XML).
"""
from __future__ import annotations

import io
import re
from urllib.parse import urlencode, urlsplit

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

WEB = "https://amategeko.gov.rw"
API_HOST = "apis.amategeko.gov.rw"
FILES_HOST = "files.amategeko.gov.rw"
API = f"https://{API_HOST}/v1/site/"
MAX_PDF = 25 * 1024 * 1024
LANGS = ("en", "rw", "fr")

COURTS = {   # dropdowns/collections?language=en (2026-11-06)
    "supreme court": 2, "court of appeal": 3, "high court": 13, "commercial high court": 5,
    "military high court": 6, "international tribunal for rwanda": 7, "intermediate court": 10,
    "commercial court": 9, "military court": 8, "primary court": 11,
}
CATEGORIES = {   # dropdowns/categories?language=en
    "administrative": 11, "business": 15, "civil": 13, "criminal": 9, "diplomatic": 7,
    "fundamental": 5, "human rights": 6, "judicial": 10, "security": 8, "taxation": 12,
}
LAW_STATUS = {"in_force": ("section", "1.1"), "repealed": ("section", "1.2"),
              "all": ("sections", "1.1,1.2")}

_decisions: dict = {}
_laws: dict = {}


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #
async def _api(path: str, what: str):
    r = await _http.get(API + path)
    if r.status_code != 200:
        hint = "The portal's API is having trouble; try again later." if r.status_code in (502, 503, 504) else ""
        raise SourceError(_http.error("amategeko.gov.rw", what, r.status_code, hint), r.status_code)
    try:
        j = r.json()
    except ValueError:
        raise SourceError(f"Error (amategeko.gov.rw): {what}: not JSON.", "payload") from None
    if j.get("error") or "data" not in j:
        raise SourceError(f"Error (amategeko.gov.rw): {what}: {j.get('message', 'unexpected payload')}.",
                          j.get("status", "payload"))
    return j["data"]


async def _pdf(file_id: int, page_url: str) -> bytes:
    rec = await _api(f"documents-files/{file_id}", "file record failed")
    url = (rec or {}).get("file_url") or ""
    if (urlsplit(url).hostname or "").lower() != FILES_HOST:
        raise SourceError(f"Error (amategeko.gov.rw): no PDF link for this document; open {page_url}", "no-file")
    r = await _http.get(url, headers={"Range": f"bytes=0-{MAX_PDF - 1}"})
    if r.status_code not in (200, 206):
        raise SourceError(_http.error("files.amategeko.gov.rw", "PDF download failed", r.status_code), r.status_code)
    total = re.search(r"/(\d+)$", r.headers.get("content-range", ""))
    if (total and int(total[1]) > MAX_PDF) or len(r.content) > MAX_PDF:
        raise SourceError(f"Error (amategeko.gov.rw): the PDF is larger than {MAX_PDF // 2**20} MB; "
                          f"read it at {page_url}", "too-large")
    if not r.content.startswith(b"%PDF"):
        raise SourceError("Error (amategeko.gov.rw): the file is not a PDF.", "payload")
    return r.content


def _doc_id(id) -> int:
    s = str(id or "").strip()
    m = re.search(r"/view/(?:toc/)?doc/(\d+)", s) or re.fullmatch(r"(\d{1,7})", s)
    if not m:
        raise BadRequest("Use the numeric document id from search, e.g. '3949', or a portal link "
                         "like https://amategeko.gov.rw/view/toc/doc/3949/4119.")
    return int(m[1])


def _langs(s) -> list[str]:
    return [x.strip().lower() for x in str(s or "").split(",") if x.strip()]


async def _file(doc_id: int) -> dict:
    """The document's file to read: the one with English, else the first."""
    data = await _api(f"documents-files/table?document={doc_id}", "file list failed")
    rows = [r for r in (data or {}).get("data") or [] if (r.get("document") or {}).get("id") == doc_id]
    if not rows:
        raise NotFound(f"No document {doc_id} on amategeko.gov.rw.")
    return next((r for r in rows if "en" in _langs(r.get("languages"))), rows[0])


def _snippet(hit: dict) -> str:
    hl = (hit.get("highlight") or {}).get("file_text") or []
    return _http.clean(re.sub(r"</?mark>", "", " … ".join(hl[:2])))[:400]


async def _search(query, limit, page, params: dict) -> tuple[list[dict], int | None]:
    limit = max(1, min(int(limit), 50))
    q = {"start": (max(1, int(page)) - 1) * limit, "length": limit, **params}
    if (query or "").strip():
        q["search"] = query.strip()
    data = await _api("documents/search?" + urlencode(q), "search failed")
    return data.get("data") or [], data.get("recordsFiltered")


def _lang_filter(f: dict) -> str:
    lang = f.get("language", "en").lower()
    if lang not in LANGS:
        raise BadRequest("language must be en, rw (Kinyarwanda) or fr.")
    return lang


def _year(f: dict, q: dict) -> None:
    """year: 2022 (one year), 2022-2025, 2022- (from) or -2025 (up to). The portal's own `year`
    takes one year; a range goes through its startDate/endDate (ISO dates)."""
    if "year" not in f:
        return
    m = re.fullmatch(r"(\d{4})?\s*(-)?\s*(\d{4})?", f["year"])
    if not m or not (m[1] or m[3]):
        raise BadRequest("year must be four digits, e.g. 2018, or a range: 2022-2025, 2022- (from) or -2025 (up to).")
    a, dash, b = m[1], m[2], m[3]
    if not dash:
        q["year"] = a
        return
    if a and b and int(a) > int(b):
        raise BadRequest("year range must run from the earlier to the later year, e.g. 2022-2025.")
    if a:
        q["startDate"] = f"{a}-01-01"
    if b:
        q["endDate"] = f"{b}-12-31"


_CASE_NO = re.compile(r"^(?:[A-Z]+/)*[A-Z]*\s?\d{3,6}/(\d{4})(?:/[A-Z/]+)?$")


def _case_no(s) -> str:
    """Upper-cased, spaces folded, stray trailing punctuation dropped (the portal has 'SC,' and 'SC–')."""
    return re.sub(r"[^A-Z0-9]+$", "", re.sub(r"\s+", " ", str(s or "").upper()).strip())


async def _amenders(title: str, own_id: str) -> list[tuple[str, str, str]]:
    """(id, title, date) of laws on the portal whose title says they amend the law titled `title`."""
    m = re.search(r"N[°ºo]?\s*([\w./-]+)\s+OF\s+(\d\d/\d\d/\d{4})", title or "", re.I)
    if not m:
        return []
    pat = re.compile(r"(?:AMENDING|MODIFYING|AMENDS|MODIFIES)\s+(?:THE\s+)?LAW\s+N[°ºo]?\s*" + re.escape(m[1])
                     + r"\s+OF\s+" + re.escape(m[2]), re.I)
    try:
        rows, _ = await _search(f"amending law {m[1]} of {m[2]}", 20, 1, {"language": "en", "section": "1.1"})
    except SourceError:
        return []
    out = []
    for h in rows:
        s = h.get("_source") or {}
        name = _http.clean(s.get("document_name"))
        if str(s.get("document_id")) != own_id and pat.search(name):
            out.append((str(s.get("document_id")), name, _http.iso_date(s.get("document_date"))))
    return out


def _date_ok(date: str, case_no: str) -> bool:
    """A judgment cannot be dated before the year in its case number ('.../2020/CA' dated 1921:
    a typo on the portal)."""
    m = re.search(r"/(\d{4})(?:/|$)", case_no or "")
    return not (date and m and int(date[:4]) < int(m[1]))


# Names lawyers use for codes the portal files under another title (law ids checked 2026-11-12).
LAW_HINTS = {
    "penal code": ("offences and penalties in general",
                   "No law is titled 'Penal Code'. The criminal code is Law 68/2018 determining offences "
                   "and penalties in general; the amending laws follow it."),
    "criminal code": ("offences and penalties in general",
                      "No law is titled 'Criminal Code'. The criminal code is Law 68/2018 determining "
                      "offences and penalties in general; the amending laws follow it."),
    "civil code": (None,
                   "No document titled 'Civil Code' turned up on the portal (only Law 22/99 supplementing "
                   "Book One of it, id 5395). Its subjects are now in separate laws: contracts, Law "
                   "45/2011 (id 4551); persons and family, Law 71/2024 (id 5922)."),
}


# --------------------------------------------------------------------------- #
# Gazette columns and articles
# --------------------------------------------------------------------------- #
_JUNK = re.compile(r"^(?:Official Gazette .*|Igazeti ya Leta .*|Journal Officiel .*|\d{1,4})$", re.I)


def _gutters(lines: list[str], n: int) -> list[int] | None:
    """Cut points between n side-by-side columns of pypdf layout-mode lines. In the
    window around each k/n of the text width: the middle of the longest run of
    character positions (almost) no line uses; where the columns nearly touch, the
    position where most lines start a word after two or more spaces."""
    occ = [0] * (max(len(ln) for ln in lines) + 1)
    for ln in lines:
        for i, ch in enumerate(ln):
            if ch != " ":
                occ[i] += 1
    used = [i for i, v in enumerate(occ) if v]
    lo, hi = used[0], used[-1]
    tol = max(1, len(lines) // 50)
    cuts = []
    for k in range(1, n):
        a, b = lo + (hi - lo) * (2 * k - 1) // (2 * n), lo + (hi - lo) * (2 * k + 1) // (2 * n)
        best, i = (0, 0), a
        while i < b:
            j = i
            while j < b and occ[j] <= tol:
                j += 1
            if j - i > best[0]:
                best = (j - i, (i + j) // 2)
            i = j + 1
        if best[0] >= 2:
            cuts.append(best[1])
            continue
        starts = [0] * len(occ)
        for ln in lines:
            for m in re.finditer(r"  (?=\S)", ln):
                starts[m.end()] += 1
        peak = max(range(a, b), key=lambda x: starts[x])
        if starts[peak] < len(lines) // 4:
            return None
        cuts.append(peak)
    return cuts


_HEADSTART = re.compile(r"(?<= )(?:Article|Ingingo ya)\s+\w+\s*:")


def _snap(ln: str, c: int) -> int:
    """Move a cut to where this line's column really starts: an article heading
    pushed right by an overflowing neighbour, or the start of a word it splits."""
    h = [m.start() for m in _HEADSTART.finditer(ln, max(0, c - 20), c)]
    if h and h[-1] > 10:
        return h[-1]
    if 0 < c < len(ln) and ln[c - 1] != " " and ln[c] != " ":
        k = ln.rfind(" ", max(0, c - 15), c)
        if k >= 0:
            return k + 1
    return c


def _column_text(data: bytes, langs: list[str], want: str) -> tuple[str, str]:
    """(text, language) of one language column of a side-by-side gazette PDF, cut
    per page from pypdf's layout-mode text. Pages whose columns cannot be found are
    skipped; with fewer than two languages the whole text is returned."""
    from pypdf import PdfReader
    order = [x for x in ("rw", "en", "fr") if x in langs]
    if len(order) < 2:
        return _http.pdf_text(data), (order[0] if order else "")
    pick = want if want in order else order[0]
    col = order.index(pick)
    out = []
    for p in PdfReader(io.BytesIO(data)).pages:
        lines = [ln for ln in (p.extract_text(extraction_mode="layout") or "").splitlines()
                 if ln.strip() and not _JUNK.match(ln.strip())]
        cuts = _gutters(lines, len(order)) if lines else None
        if cuts is None:
            continue
        page = []
        for ln in lines:
            b = [0, *(_snap(ln, c) for c in cuts), len(ln)]
            page.append(_http.clean(ln[b[col]:b[col + 1]]))
        out.append("\n".join(ln for ln in page if ln and not _JUNK.match(ln)))
    text = re.sub(r"\n{3,}", "\n\n", "\n\n".join(p for p in out if p)).strip()
    return (text, pick) if text else (_http.pdf_text(data), "")


_WORDNUM = {"one": "1", "premier": "1", "première": "1", "mbere": "1"}
_ART = re.compile(r"^(?:Article|Ingingo ya)\s+(One|premier|première|mbere|\d{1,4})\s*(bis|ter|quater)?\s*[:.]\s*(.*)$",
                  re.I)
_HEAD = re.compile(r"^(?:(?:PART|TITLE|CHAPTER|SUB-CHAPTER|TITRE|CHAPITRE|IGICE|INTERURO|UMUTWE)\s+[A-Z0-9ÉIVX]+\b"
                   r"|PREMIÈRE PARTIE\b|(?:Section|Sub-section|Icyiciro)\s+(?:One|\d+|[A-Za-z]+)\s*:)")


def _label(num: str, suffix: str | None) -> str:
    n = _WORDNUM.get(num.lower(), num)
    return f"{int(n)}{(' ' + suffix.lower()) if suffix else ''}" if n.isdigit() else n


def _articles(text: str) -> tuple[list[TocEntry], dict[str, str]]:
    lines = text.splitlines()
    hits = [(i, _label(m[1], m[2]), m[3]) for i, ln in enumerate(lines) if (m := _ART.match(ln.strip()))]
    firsts = [k for k, (_, lab, _) in enumerate(hits) if lab == "1"]
    if not firsts:
        return [], {}
    hits = hits[firsts[-1] if len(firsts) > 1 else firsts[0]:]
    kept, prev = [], 0
    for i, lab, title in hits:
        n = int(lab.split()[0])
        if n >= prev and lab not in {k[1] for k in kept}:
            kept.append((i, lab, title))
            prev = n
    toc: list[TocEntry] = []
    texts: dict[str, str] = {}
    pending: list[str] = []          # part/chapter headings that open the next article
    for k, (i, lab, _title) in enumerate(kept):
        end = kept[k + 1][0] if k + 1 < len(kept) else len(lines)
        body = [ln.strip() for ln in lines[i:end]]
        toc += [TocEntry(title=h, level=0) for h in pending]
        toc.append(TocEntry(title=body[0], level=1, provision=lab))
        pending = []
        cut = next((j for j in range(1, len(body)) if _HEAD.match(body[j])), None)
        if cut is not None and k + 1 < len(kept):
            pending = [h for h in body[cut:] if _HEAD.match(h)]
            body = body[:cut]
        texts[lab] = "\n".join(body).strip()
    return toc, texts


def _norm_prov(p: str) -> str:
    s = _http.clean(p)
    s = re.sub(r"(?i)^(article|art\.?|ingingo ya|ingingo|a\.)\s*", "", s).strip().rstrip(".:")
    m = re.fullmatch(r"(?i)(one|premier|première|mbere|\d{1,4})\s*(bis|ter|quater)?", s)
    return _label(m[1], m[2]) if m else s.lower()


# --------------------------------------------------------------------------- #
class RW(Jurisdiction):
    code = "rw"
    name = "Rwanda"
    languages = ("rw", "en", "fr")
    aliases = ("rwanda", "republic of rwanda", "repubulika y'u rwanda", "république du rwanda")
    sources = (
        Source(
            name="Portal of Rwandan Laws and Case Laws (amategeko.gov.rw), Rwanda Law Reform Commission "
                 "and Judiciary of Rwanda",
            url=WEB,
            covers=("caselaw", "legislation"),
            licence=("No licence stated. Legal notice: laws are 'property of Rwanda Law Reform Commission "
                     "(RLRC)', law reports and judgments 'property of the Judiciary'; © Government of the "
                     "Republic of Rwanda"),
            commercial_use=None,
            ai_use=None,        # no AI/TDM clause; robots.txt allows everything
            auth="none",
            rate_limit=("unknown; 1 s spacing per host. No 429 in ~30 requests (2026-11), but the API "
                        "answered 502 for a while after a per-page text request"),
            terms_url=f"{WEB}/legal",
            warning=("Laws are the Official Gazette texts as published, not consolidated; the portal says "
                     "they do not replace the Gazette."),
        ),
    )
    caselaw_filters = {
        "court": "Supreme Court, Court of Appeal, High Court, Commercial High Court, Intermediate Court, "
                 "Primary Court, Commercial Court, Military High Court, Military Court",
        "year": "year of the decision: 2023, or a range 2022-2025, 2022- (from) or -2025 (up to)",
        "language": "en (default), rw (Kinyarwanda; most judgments) or fr",
        "status": "reported (in the Rwanda Law Reports) or unreported",
    }
    legislation_filters = {
        "status": "in_force (default), repealed or all",
        "category": "fundamental, human rights, diplomatic, criminal, security, judicial, administrative, "
                    "taxation, civil or business",
        "year": "year of the Gazette: 2018, or a range 2015-2018, 2015- (from) or -2018 (up to)",
        "language": "en (default), rw or fr: only laws with a text in that language",
    }
    min_interval = {API_HOST: 1.0, FILES_HOST: 1.0}
    notes = ("Official RLRC/Judiciary portal: laws in force and repealed as published in the Official "
             "Gazette (English column of the trilingual text, split into articles) and judgments of the "
             "Supreme Court, Court of Appeal, High Court, Commercial High Court, Military High Court, "
             "Intermediate, Primary, Commercial and Military Courts (only what the portal has uploaded). "
             "Full-text search.")
    gaps = (
        ("Consolidated laws: the portal has Gazette texts as published only; amending laws are "
         "separate documents"),
        ("Kinyarwanda and French text of laws: only the English column is split into articles; not "
         "built yet"),
        ("Law reports (portal sections 2.2.x): source exists and works but not built yet (judgments"
         " section only)"),
        "Judgment and law PDFs without a text layer: scans only, no text",
    )
    samples = {
        "caselaw_query": "penal code adultery",
        "decision_id": "8322",        # Re MURORUNKWERE, Supreme Court 2008
        "legislation_query": "offences and penalties in general",
        "law_id": "3949",             # Law Nº 68/2018 determining offences and penalties in general
        "provision": "2",
    }

    # ------------------------------------------------------------------ #
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        f = {k: str(v).strip() for k, v in (filters or {}).items() if str(v).strip()}
        q: dict = {"language": _lang_filter(f), "section": "2.1"}
        if "court" in f:
            cid = COURTS.get(f["court"].lower())
            if cid is None:
                raise BadRequest("court must be one of: " + ", ".join(c.title() for c in COURTS) + ".")
            q["collection"] = cid
        if "status" in f:
            st = {"reported": 1, "unreported": 2}.get(f["status"].lower())
            if st is None:
                raise BadRequest("status must be reported or unreported.")
            q["decisionsStatus"] = st
        _year(f, q)
        want = _case_no(query)
        by_no = _CASE_NO.match(want)
        if by_no:       # the case itself ranks below the judgments citing it: narrow by date, keep exact matches
            qn, window = dict(q), ""
            if "year" not in q and "startDate" not in q:
                qn["startDate"] = f"{by_no[1]}-01-01"
                qn["endDate"] = f"{int(by_no[1]) + 3}-12-31"
                window = (f" Searched decisions dated {by_no[1]} to {int(by_no[1]) + 3} (from the case "
                          f"number's year); a case decided later is not covered: add filters.year, e.g. "
                          f"'{by_no[1]}-', to search other years.")
            rows, _ = await _search(query, 50, 1, qn)
            rows = [h for h in rows if _case_no((h.get("_source") or {}).get("document_case_no")) == want]
            if not rows:
                by_no = None
        paged = bool(by_no)
        if not by_no:       # up to 50 records come at once so copies can be folded before paging
            rows, total = await _search(query, 50, 1, q)
            paged = total is not None and total <= 50
            if not paged:
                rows, total = await _search(query, limit, page, q)
        hits, seen, bad = [], {}, 0
        for h in rows:
            s = h.get("_source") or {}
            num = _http.clean(s.get("document_case_no"))
            court = _http.clean(s.get("document_collection_name"))
            date = _http.iso_date(s.get("document_date"))
            if not _date_ok(date, num):
                date, bad = "", bad + 1
            title = _http.clean(s.get("document_name")) or f"{court} {num}"
            key = (_case_no(num), court, date) if num else None
            if key in seen:     # the same judgment is often uploaded several times (copies, reports)
                seen[key].snippet = (seen[key].snippet + f" [also uploaded as id {s.get('document_id')}]")[:480]
                continue
            hit = DecisionHit(
                id=str(s.get("document_id")), title=title, court=court, date=date, case_number=num,
                snippet=_snippet(h) or _http.clean(s.get("document_keywords")).strip(" ,")[:400],
                url=f"{WEB}/view/doc/{s.get('document_id')}/{s.get('file_id')}")
            if key:
                seen[key] = hit
            hits.append(hit)
        if paged:       # fold copies over the whole result set, then page
            total = len(hits)
            lim = max(1, min(int(limit), 50))
            hits = hits[(max(1, int(page)) - 1) * lim:][:lim]
        note = ("Full-text search of the judgment PDFs; default language English (use language=rw for the "
                "larger Kinyarwanda set). ")
        note += ("The total counts distinct judgments: copies of one judgment (reported/unreported, "
                 "re-uploads) are listed once." if paged else
                 "The total counts portal records: one judgment is often uploaded several times "
                 "(reported/unreported, copies); copies on this page are listed once.")
        if by_no:
            note = "Case number matched exactly." + window + " " + note
        if bad:
            note += f" {bad} hit(s) have a date on the portal that precedes the case number's year (a portal error), so the date is left blank."
        return Results(items=hits, total=total, note=note)

    async def get_decision(self, id):
        did = _doc_id(id)
        if did in _decisions:
            return _decisions[did]
        f = await _file(did)
        doc = f.get("document") or {}
        if not str(doc.get("section", "")).startswith("2"):
            raise NotFound(f"Document {did} is legislation, not a judgment; use get_legislation_text.")
        url = f"{WEB}/view/doc/{did}/{f['id']}"
        text = _http.pdf_text(await _pdf(f["id"], url))
        if not text:
            raise SourceError(f"Error (amategeko.gov.rw): the judgment PDF has no text layer; read it at {url}",
                              "no-text")
        court = _http.clean((doc.get("collection") or {}).get("name_en"))
        num = _http.clean(doc.get("case_no"))
        meta = {"Language": f.get("languages") or ""}
        for k, v in (("Decision type", (doc.get("decisionsTypes") or {}).get("name_en")),
                     ("Judgment type", (doc.get("relations") or {}).get("name")),
                     ("Status", (doc.get("decisionsStatus") or {}).get("name_en")),
                     ("Volume", (doc.get("volume") or {}).get("name_en") if isinstance(doc.get("volume"), dict) else ""),
                     ("Keywords", _http.clean(doc.get("keywords")).strip(" ,"))):
            if v:
                meta[k] = _http.clean(v)
        date = _http.iso_date(doc.get("date"))
        if not _date_ok(date, num):     # portal typo (e.g. 1921 for 2021): take the date from the judgment header
            fixed = _http.en_date(text[:1500])
            date = fixed if fixed and _date_ok(fixed, num) else ""
            meta["Date note"] = ("the portal's date for this judgment is wrong; "
                                 + (f"{date} is read from the judgment's header." if date else "not shown."))
        d = Decision(id=str(did), title=_http.clean(doc.get("name")) or f"{court} {num}", text=text, url=url,
                     court=court, date=date, case_number=num, metadata=meta)
        return _http.lru_put(_decisions, did, d, 16)

    # ------------------------------------------------------------------ #
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        f = {k: str(v).strip() for k, v in (filters or {}).items() if str(v).strip()}
        status = f.get("status", "in_force").lower()
        if status not in LAW_STATUS:
            raise BadRequest("status must be in_force, repealed or all.")
        key, val = LAW_STATUS[status]
        q: dict = {"language": _lang_filter(f), key: val}
        if "category" in f:
            cid = next((v for k, v in CATEGORIES.items() if f["category"].lower().startswith(k.split()[0])), None)
            if cid is None:
                raise BadRequest("category must be one of: " + ", ".join(CATEGORIES) + ".")
            q["category"] = cid
        _year(f, q)
        hint = LAW_HINTS.get(re.sub(r"[^a-z ]", "", (query or "").lower()).strip())
        if hint and hint[0]:
            query = hint[0]
        rows, total = await _search(query, limit, page, q)
        hits = []
        for h in rows:
            s = h.get("_source") or {}
            sec = s.get("document_section")
            hits.append(LawHit(
                id=str(s.get("document_id")), title=_http.clean(s.get("document_name")),
                type=_http.clean(s.get("document_sub_category_name") or s.get("document_category_name")),
                number=_http.clean(s.get("document_case_no")), date=_http.iso_date(s.get("document_date")),
                status={"1.1": "in force", "1.2": "repealed"}.get(sec, ""), snippet=_snippet(h),
                url=f"{WEB}/view/toc/doc/{s.get('document_id')}/{s.get('file_id')}"))
        return Results(items=hits, total=total,
                       note=((hint[1] + " ") if hint else "") +
                            "Full-text search of the Gazette texts. Texts are as published: amending laws "
                            "are separate entries, not merged into the law they amend.")

    async def _law(self, id) -> dict:
        did = _doc_id(id)
        if did in _laws:
            return _laws[did]
        f = await _file(did)
        doc = f.get("document") or {}
        sec = str(doc.get("section", ""))
        if not sec.startswith("1"):
            raise NotFound(f"Document {did} is a judgment, not legislation; use get_decision.")
        url = f"{WEB}/view/toc/doc/{did}/{f['id']}"
        langs = _langs(f.get("languages"))
        text, lang = _column_text(await _pdf(f["id"], url), langs, "en")
        if not text:
            raise SourceError(f"Error (amategeko.gov.rw): the law PDF has no text layer; read it at {url}",
                              "no-text")
        toc, arts = _articles(text)
        title = _http.clean(doc.get("name"))
        meta = {"Status": {"1": "", "1.1": "in force", "1.2": "repealed"}.get(sec, sec),
                "Number": _http.clean(doc.get("case_no")),
                "Gazette date": _http.iso_date(doc.get("date")),
                "Category": _http.clean((doc.get("category") or {}).get("name_en")
                                        if isinstance(doc.get("category"), dict) else ""),
                "Languages in the PDF": ", ".join(langs),
                "Language shown": lang or "all columns (could not separate them)"}
        law = {"id": str(did), "title": title, "url": url, "text": text, "toc": toc, "arts": arts,
               "meta": {k: v for k, v in meta.items() if v}}
        return _http.lru_put(_laws, did, law, 8)

    async def get_legislation_toc(self, id):
        law = await self._law(id)
        entries = law["toc"] or [TocEntry(title="(no articles found; use get_legislation_text)", level=0)]
        return Toc(id=law["id"], title=law["title"], url=law["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        law = await self._law(id)
        lab = _norm_prov(provision)
        if lab not in law["arts"]:
            via = [k for k, v in law["arts"].items()
                   if re.search(rf"Articles?\s+{re.escape(lab)}\s+of\s+(?:the\s+)?Law", v, re.I)]
            if via:     # an amending law: its own article numbers differ from the article it changes
                raise NotFound(f"{law['title']} has no article '{provision}' of its own. It amends article "
                               f"{lab} of the law it modifies, in its article {', '.join(via)}: use "
                               f"get_legislation_provision with provision '{via[0]}'.")
            raise NotFound(f"{law['title']} has no article '{provision}'. Labels are article numbers "
                           f"such as '1' or '2' (see get_legislation_toc).")
        am = await _amenders(law["title"], law["id"])
        if am:
            found = "; ".join(f"{t} (id {i}, {d})" for i, t, d in am[:5])
            hits = []
            for i, t, d in am[:5]:
                try:
                    a = (await self._law(i))["arts"]
                except (SourceError, NotFound):
                    continue
                pat = re.compile(rf"Articles?\s+{re.escape(lab)}\s+of\s+(?:the\s+)?Law", re.I)
                hits += [f"> Amended by law {i}, its article {k}:\n> " + v.replace("\n", "\n> ")
                         for k, v in a.items() if pat.search(v)]
            tail = (f"The portal has amending law(s): {found}. This article may have been changed or "
                    "replaced there; check them with get_legislation_text before relying on it.")
            if hits:
                tail += ("\n\nAN AMENDING ARTICLE FOUND, so the text above is superseded in whole or part; "
                         "read this:\n\n" + "\n\n".join(hits))
        else:
            tail = ("Amending laws are separate documents and may have changed it; search_legislation for "
                    "'amending law' with this law's number to find them.")
        text = (law["arts"][lab] + "\n\n> Note: this is the article as published in the Gazette of "
                f"{law['meta'].get('Gazette date') or 'its date'}, not necessarily the current text. " + tail)
        return Provision(law_id=law["id"], law_title=law["title"], provision=lab, text=text,
                         url=law["url"], as_of=law["meta"].get("Gazette date", ""))

    async def get_legislation_text(self, id):
        law = await self._law(id)
        return LawText(id=law["id"], title=law["title"], text=law["text"], url=law["url"],
                       as_of=law["meta"].get("Gazette date", ""), metadata=law["meta"])
