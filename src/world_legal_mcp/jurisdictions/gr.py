"""Greece: Areios Pagos case law and Government Gazette (ΦΕΚ) legislation.

Sources (keyless; verified 2026-11-05):
  * Άρειος Πάγος (www.areiospagos.gr), classic ASP, windows-1253.
    Search: POST /nomologia/apofaseis_result.asp?S=1 with X_TMHMA (chamber),
    X_SUB_TMHMA (section), x_number + X_TELESTIS_number (1 "=", 2 ">=", 3 "<="),
    x_ETOS + X_TELESTIS_ETOS. No free-text search (the site sends that to Google).
    Subject index: GET /nomologia/apofaseis_result.asp?s=2&code=N, codes listed on
    /nomologia/apofaseis.asp. Decision: GET /nomologia/apofaseis_DISPLAY.asp?cd=<30 chars>.
  * Εθνικό Τυπογραφείο (search.et.gr): the site's React app calls a keyless JSON API at
    searchetv99.azurewebsites.net/api (POST /simplesearch: full text, or one ΦΕΚ by
    issue/number/year; POST /searchlegislation: laws/π.δ. by number and year). The
    "data" field is a JSON string. ΦΕΚ PDFs sit on a public Azure blob:
    ia37rg02wpsa01.blob.core.windows.net/fek/{issue:02}/{year}/{year}{issue:02}{number:05}.pdf

Gotchas this code encodes (verified 2026-11-05):
  * Areios Pagos result rows carry no date; the decision date is read from the closing
    "Δημοσιεύθηκε ... στις 12 Μαρτίου 2020" line. Unknown cd -> HTTP 404. A year listing
    is capped at 3000 rows (~1.8 MB), so it is cached and paged in memory.
  * The subject index (θεματολόγιο) is mostly 2007–2010 decisions.
  * ΦΕΚ text is the gazette as published, not consolidated. Pre-~2000 issues are mostly
    scans without a text layer; those raise SourceError (no OCR).
  * simplesearch results come oldest first; the last element is a
    {"search_stemmedQuery": ...} marker, not a hit. Snippets are base64, accentless.
  * searchlegislation search_LawID: 1 = Νόμος, 2 = Προεδρικό Διάταγμα (seen on ν. 4624/2019
    and π.δ. 18/1989); other values are shown raw.
"""
from __future__ import annotations

import base64
import html as _html
import io
import json
import re
import unicodedata
from urllib.parse import unquote_to_bytes

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

AP = "www.areiospagos.gr"
AP_BASE = f"https://{AP}/nomologia/"
ET_API_HOST = "searchetv99.azurewebsites.net"
ET_API = f"https://{ET_API_HOST}/api"
BLOB_HOST = "ia37rg02wpsa01.blob.core.windows.net"
COURT = "Άρειος Πάγος"
ENC = "windows-1253"

_CHAMBERS = {"civil": "1", "criminal": "2", "3068": "3", "4239": "4", "4842": "5", "all": "6"}
_SECTIONS = {"Α": "2", "Α1": "13", "Α2": "12", "Β": "3", "Β1": "4", "Β2": "5", "Γ": "6",
             "Δ": "7", "Ε": "8", "ΣΤ": "9", "Ζ": "10", "ΟΛΟΜΕΛΕΙΑ": "11",
             "Α ΠΟΙΝ. ΔΙΑΚ.": "15", "Β ΠΟΙΝ. ΔΙΑΚ.": "16"}
_ISSUES = {"Α": 1, "Β": 2, "Γ": 3, "Δ": 4, "Ν.Π.Δ.Δ.": 5, "Α.Π.Σ.": 6, "ΠΑΡΑΡΤΗΜΑ": 7,
           "Δ.Ε.Β.Ι.": 8, "Α.ΕΙ.Δ.": 9, "Α.Σ.Ε.Π.": 10, "ΑΕ-ΕΠΕ": 11, "Δ.Δ.Σ.": 12,
           "Ο.Π.Κ.": 13, "Υ.Ο.Δ.Δ.": 14, "Α.Α.Π.": 15}
_ISSUE_NAME = {v: k for k, v in _ISSUES.items()}
_LAW_TYPE = {"1": ("Νόμος", "ν."), "2": ("Προεδρικό Διάταγμα", "π.δ.")}
_LATIN = str.maketrans("ABEZHIKMNOPTYX", "ΑΒΕΖΗΙΚΜΝΟΡΤΥΧ")
_MONTHS = {m: i for i, m in enumerate(
    "ιανουαριου φεβρουαριου μαρτιου απριλιου μαιου ιουνιου ιουλιου αυγουστου "
    "σεπτεμβριου οκτωβριου νοεμβριου δεκεμβριου".split(), 1)}

_AP_ID = re.compile(r"^[0-9A-Z]{20,40}$")
_NUM_YEAR = re.compile(r"^(?:ΑΠ|Α\.Π\.|AP)?\s*(\d{1,4})\s*/\s*(\d{4})$", re.I)
_FEK = re.compile(r"^(?:ΦΕΚ\s*)?([Α-ΩA-Z][Α-ΩA-Z.\-]*?)\s*['΄’`]?\s*(\d{1,6})\s*/\s*(\d{4})$")
_LAW = re.compile(r"^(?:(ν|ν\.δ|π\.δ|n|pd)\.?\s*)?(\d{1,5})\s*/\s*(\d{4})$", re.I)
_ART = re.compile(r"^Άρθρο\s+(\d+[Α-Ω]?|[Α-Ωα-ωάέήίόύώϊΐ]+)\s*$")
_HEADING = re.compile(r"^(ΜΕΡΟΣ|ΚΕΦΑΛΑΙΟ|ΤΜΗΜΑ|ΤΙΤΛΟΣ|ΒΙΒΛΙΟ)\s+\S+\s*$")

_subjects: dict[str, list[tuple[str, str]]] = {}
_lists: dict = {}
_texts: dict = {}


def _fold(s: str) -> str:
    """Lower case, no accents, final sigma folded: for matching only."""
    s = unicodedata.normalize("NFD", (s or "").lower().replace("ς", "σ"))
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def _stems(query: str) -> list[str]:
    # drop one letter only: two would let 'μισθωση' (lease) match 'μισθωτου' (employee)
    return [w[:-1] if len(w) > 5 else w for w in re.findall(r"\w+", _fold(query)) if len(w) > 1]


def _year(f: dict) -> str:
    y = f.get("year", "")
    if y and not re.fullmatch(r"\d{4}", y):
        raise BadRequest("year must be YYYY, e.g. 2020.")
    return y


def _greek_date(text: str) -> str:
    for key in ("δημοσιευθηκε", "κριθηκε"):
        for m in re.finditer(key + r".{0,200}?(\d{1,2})\s+([α-ω]+)\s+(\d{4})", _fold(text), re.S):
            if m[2] in _MONTHS:
                return f"{m[3]}-{_MONTHS[m[2]]:02d}-{int(m[1]):02d}"
    return ""


# --------------------------------------------------------------------------- #
# Areios Pagos
# --------------------------------------------------------------------------- #
def _ap_rows(page: str) -> list[DecisionHit]:
    out = []
    for m in re.finditer(r'apofaseis_DISPLAY\.asp\?cd=(\w+)&amp;apof=[^&"]*&amp;info=([^"]*)">'
                         r'([^<]+)</a>.*?class="black10">(.*?)</td>', page, re.S):
        cd, info, num, snip = m[1], m[2], _http.clean(m[3]), m[4]
        info = _http.clean(unquote_to_bytes(info.replace("+", " ")).decode(ENC, "replace"))
        info = re.sub(r"\s*-\s*", " - ", info)
        snip = _http.clean(re.sub(r"<[^>]+>", " ", _html.unescape(snip.replace("&nbsp", " "))))
        out.append(DecisionHit(
            id=cd, title=f"{COURT} {num}" + (f" ({info})" if info else ""), court=COURT,
            case_number=num, snippet=snip[:300], url=f"{AP_BASE}apofaseis_DISPLAY.asp?cd={cd}"))
    return out


async def _ap_get(url: str, **kw) -> str:
    r = await (_http.post(url, **kw) if "data" in kw else _http.get(url, **kw))
    if r.status_code != 200:
        raise SourceError(_http.error("Areios Pagos", "request failed", r.status_code), r.status_code)
    return r.content.decode(ENC, "replace")


async def _ap_search(number: str, year: str, f: dict, op_number: str = "1") -> list[DecisionHit]:
    chamber = _CHAMBERS.get((f.get("chamber") or "all").lower())
    if not chamber:
        raise BadRequest(f"chamber must be one of: {', '.join(_CHAMBERS)}.")
    section = f.get("section", "")
    if section and section.upper() not in _SECTIONS:
        raise BadRequest(f"section must be one of: {', '.join(_SECTIONS)}.")
    data = {"X_TMHMA": chamber, "X_SUB_TMHMA": _SECTIONS.get(section.upper(), "1") if section else "1",
            "X_TELESTIS_number": op_number, "x_number": number,
            "X_TELESTIS_ETOS": "1", "x_ETOS": year}
    key = ("ap", tuple(sorted(data.items())))
    if key in _lists:
        return _lists[key]
    page = await _ap_get(AP_BASE + "apofaseis_result.asp?S=1", data=data)
    return _http.lru_put(_lists, key, _ap_rows(page), 8)


async def _ap_subjects() -> list[tuple[str, str]]:
    if "list" not in _subjects:
        page = await _ap_get(AP_BASE + "apofaseis.asp")
        _subjects["list"] = [(c, _http.clean(_html.unescape(n).replace("_", " ")))
                             for c, n in re.findall(r'apofaseis_result\.asp\?s=2&code=(\d+)">(.*?)</span>', page)]
    return _subjects["list"]


async def _ap_subject_hits(query: str) -> tuple[list[DecisionHit], list[str]]:
    stems = _stems(query)
    if not stems:
        raise BadRequest("Give a decision number ('1/2020'), a year ('2020') or subject words.")
    subjects = await _ap_subjects()
    names = [(c, n) for c, n in subjects if all(s in _fold(n) for s in stems)]
    if not names and len(stems) > 1:
        # no heading has every word ('αγωγή αποζημίωση'): use the most specific single word
        per = [[(c, n) for c, n in subjects if s in _fold(n)] for s in stems]
        per = [p for p in per if p]
        names = min(per, key=len) if per else []
    hits: list[DecisionHit] = []
    for code, _ in names[:3]:
        key = ("subj", code)
        if key not in _lists:
            _http.lru_put(_lists, key, _ap_rows(await _ap_get(f"{AP_BASE}apofaseis_result.asp?s=2&code={code}")), 8)
        hits += _lists[key]
    return hits, [n for _, n in names]


# --------------------------------------------------------------------------- #
# Εθνικό Τυπογραφείο (ΦΕΚ)
# --------------------------------------------------------------------------- #
async def _et(route: str, body: dict) -> list[dict]:
    r = await _http.post(f"{ET_API}/{route}", json=body)
    if r.status_code != 200:
        raise SourceError(_http.error("ET", f"{route} failed", r.status_code), r.status_code)
    try:
        d = r.json()
        rows = json.loads(d.get("data") or "[]") if d.get("status") == "ok" else None
    except ValueError:
        rows = None
    if rows is None:
        raise SourceError(_http.error("ET", f"unexpected {route} payload", r.status_code), r.status_code)
    return [x for x in rows if x.get("search_PrimaryLabel")]


def _simple(text: str = "", year: str = "", issue: str = "", number: str = "") -> dict:
    return {"selectYear": [year] if year else [], "selectIssue": [issue] if issue else [],
            "documentNumber": number, "searchText": text, "categoryIds": [], "datePublished": "",
            "dateReleased": "", "tags": [], "entity": []}


def _us_date(s: str) -> str:
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", s or "")
    return f"{m[3]}-{int(m[1]):02d}-{int(m[2]):02d}" if m else ""


def _fek_parts(label: str) -> tuple[int, str, str]:
    m = _FEK.match(_http.clean(label).upper().translate(_LATIN))
    if not m:
        raise BadRequest("ΦΕΚ id looks like 'Α 137/2019' (issue, number/year); laws also as 'ν. 4624/2019'.")
    issue = _ISSUES.get(m[1].rstrip("'΄’`") or "")
    if not issue:
        raise BadRequest(f"Unknown ΦΕΚ issue {m[1]!r}; use one of {', '.join(_ISSUES)}.")
    return issue, str(int(m[2])), m[3]


def _fek_label(issue: int, number: str, year: str) -> str:
    return f"{_ISSUE_NAME[issue]} {number}/{year}"


def _pdf_url(issue: int, number: str, year: str) -> str:
    return f"https://{BLOB_HOST}/fek/{issue:02d}/{year}/{year}{issue:02d}{int(number):05d}.pdf"


def _law_hit(r: dict) -> LawHit:
    issue, number, year = _fek_parts(r["search_PrimaryLabel"])
    typ, abbr = _LAW_TYPE.get(r.get("search_LawID", ""), (r.get("search_LawID", ""), ""))
    law_no = r.get("search_LawProtocolNumber", "")
    desc = _http.clean(r.get("search_Description", ""))
    snippet = ""
    if r.get("search_MatchedText"):
        try:
            snippet = _http.clean(base64.b64decode(r["search_MatchedText"]).decode("utf-8", "replace"))[:300]
        except ValueError:
            pass
    fek = _fek_label(issue, number, year)
    if law_no:
        title = f"{abbr or typ} {law_no}/{year} (ΦΕΚ {fek})" + (f": {desc}" if desc else "")
    else:
        title = f"ΦΕΚ {fek}"
    return LawHit(id=fek, title=title, type=typ or "ΦΕΚ", number=law_no or fek,
                  date=_us_date(r.get("search_PublicationDate") or r.get("search_IssueDate", "")),
                  snippet=snippet, url=_pdf_url(issue, number, year))


async def _resolve(law_id: str) -> tuple[int, str, str, str]:
    """id -> (issue, number, year, title). Accepts 'Α 137/2019' or 'ν. 4624/2019'."""
    s = _http.clean(law_id)
    m = _LAW.match(s)
    if m:
        rows = await _et("searchlegislation", {"legislationCatalogues": "", "legislationNumber": m[2],
                                                "selectYear": [m[3]]})
        if not rows:
            raise NotFound(f"No law/decree {m[2]}/{m[3]} found in the ΦΕΚ index.")
        h = _law_hit(rows[0])
        return (*_fek_parts(h.id), h.title)
    issue, number, year = _fek_parts(s)
    return issue, number, year, f"ΦΕΚ {_fek_label(issue, number, year)}"


# Running page header, e.g. "ΕΦΗΜΕΡΙ∆Α T ΗΣ ΚΥΒΕΡΝΗΣΕΩΣ3382 Τεύχος A’ 137/29.08.2019"; pypdf
# sometimes glues it into the middle of a body line, so it is cut out, not line-dropped.
_RUNNING = re.compile(r"ΕΦΗΜΕΡΙ[Δ∆]Α\s*T?\s*Η?Σ\s*ΚΥΒΕΡΝΗΣΕΩΣ\s*(?:\d+\s*)?Τεύχος\s+\S+\s*\d+/"
                      r"\d{1,2}\.\s*\d{1,2}\.\s*\d{4}\s*(?:\d+\s*$)?", re.M)


def _pdf_lines(data: bytes) -> list[str]:
    from pypdf import PdfReader
    lines = []
    for p in PdfReader(io.BytesIO(data)).pages:
        page = _RUNNING.sub(" ", (p.extract_text() or "").replace("∆", "Δ"))
        for ln in page.splitlines():
            ln = _http.clean(ln)
            if ln and not re.fullmatch(r"\d{1,5}", ln):
                lines.append(ln)
    return lines


def _paragraphs(lines: list[str]) -> list[str]:
    """PDF lines -> paragraphs: join wrapped lines, undo hyphenation, keep headings apart."""
    out: list[str] = []
    cur = ""
    for ln in lines:
        if not cur and out and _ART.match(out[-1]) and not _ART.match(ln):
            out.append(ln)  # the line after "Άρθρο N" is the article's title
            continue
        head = _ART.match(ln) or _HEADING.match(ln)
        new = (not cur or head
               or (re.search(r"[.:;»]$", cur) and re.match(r"(\d+[.)]|[α-ω]{1,2}[΄']?\)|[Α-Ω«])", ln)))
        if new or head:
            if cur:
                out.append(cur)
            cur = ln
            if head:
                out.append(cur)
                cur = ""
            continue
        if re.search(r"[Α-Ωα-ωά-ώ]-$", cur) and re.match(r"[α-ωά-ώ]", ln):
            cur = cur[:-1] + ln
        else:
            cur += " " + ln
    if cur:
        out.append(cur)
    return out


async def _fek_text(issue: int, number: str, year: str) -> list[str]:
    key = (issue, number, year)
    if key in _texts:
        return _texts[key]
    r = await _http.get(_pdf_url(issue, number, year))
    if r.status_code in (400, 404):
        raise NotFound(f"ΦΕΚ {_fek_label(issue, number, year)} not found.")
    if r.status_code != 200 or not r.content.startswith(b"%PDF"):
        raise SourceError(_http.error("ET", "ΦΕΚ PDF download failed", r.status_code), r.status_code)
    paras = _paragraphs(_pdf_lines(r.content))
    if sum(len(p) for p in paras) < 200:
        raise SourceError(f"ΦΕΚ {_fek_label(issue, number, year)} is a scan without a text layer "
                          f"(no OCR here); open the PDF: {_pdf_url(issue, number, year)}", "scan")
    return _http.lru_put(_texts, key, paras, 4)


def _articles(paras: list[str]) -> list[tuple[str, int]]:
    """(label, paragraph index) for each 'Άρθρο N' heading; repeated labels get ' (2)'."""
    seen: dict[str, int] = {}
    out = []
    for i, p in enumerate(paras):
        if _ART.match(p):
            seen[p] = seen.get(p, 0) + 1
            out.append((p if seen[p] == 1 else f"{p} ({seen[p]})", i))
    return out


def _render(paras: list[str]) -> str:
    out = []
    for p in paras:
        if _ART.match(p):
            out.append(f"### {p}")
        elif _HEADING.match(p):
            out.append(f"## {p}")
        else:
            out.append(p)
    return "\n\n".join(out)


def _norm_prov(s: str) -> str:
    s = _fold(_http.clean(s))
    s = re.sub(r"^(αρθρο|αρθ\.?|αρ\.?|article|art\.?)\s*", "", s)
    return re.sub(r"\s+", " ", s).strip(" .")


# --------------------------------------------------------------------------- #
class Greece(Jurisdiction):
    code = "gr"
    name = "Greece"
    languages = ("el",)
    aliases = ("greece", "hellas", "ελλάδα", "ellada")
    sources = (
        Source(
            name="Άρειος Πάγος – Νομολογία (Supreme Civil and Criminal Court)",
            url="https://www.areiospagos.gr/nomologia/apofaseis.asp",
            covers=("caselaw",),
            licence=("Areios Pagos terms: further use allowed on the sole condition that texts are "
                     "not altered or distorted and that the source and publication date are cited"),
            commercial_use=True,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~20 requests (2026-11-05)",
            terms_url="https://www.areiospagos.gr/nomologia/apofaseis.asp",
        ),
        Source(
            name="Εθνικό Τυπογραφείο – Αναζήτηση ΦΕΚ (Government Gazette, Presidency of the Government)",
            url="https://search.et.gr/el/",
            covers=("legislation",),
            licence="Terms of use (search.et.gr/el/oroi-xrisis): personal, informational, non-commercial use",
            commercial_use=False,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~25 requests (2026-11-05)",
            terms_url="https://search.et.gr/el/oroi-xrisis/",
            warning=("search.et.gr terms allow only personal, informational, non-commercial use and "
                     "forbid reproduction for non-personal use and conversion/copying/transmission "
                     "of its content without permission; hosting this for others needs the "
                     "Εθνικό Τυπογραφείο's explicit permission. To check legislation yourself, search "
                     "the gazette at https://search.et.gr/el/."),
            needs_permission=True,
        ),
    )
    caselaw_filters = {
        "chamber": "civil, criminal, all (default), 3068, 4239, 4842 (special procedures under those laws)",
        "section": "Α, Α1, Α2, Β, Β1, Β2, Γ, Δ, Ε, ΣΤ, Ζ, ΟΛΟΜΕΛΕΙΑ",
        "year": "YYYY (with a subject-word query: keep only that year)",
    }
    legislation_filters = {
        "year": "YYYY. With words, first matches law/decree titles of that year, else full text.",
        "issue": "ΦΕΚ issue for full-text search: Α (default; laws, decrees), Β, Γ, Δ, ... or 'all'",
    }
    min_interval = {AP: 1.0, ET_API_HOST: 1.0, BLOB_HOST: 1.0}
    notes = ("Case law: Areios Pagos only (2006 onward, anonymised), searched by number "
             "('1/2020'), year ('2024', large), or words matched to the subject index's fixed headings "
             "(first 3 matching headings; index mostly 2007–2010); no "
             "free text. Legislation: ΦΕΚ gazette text as published, NOT consolidated; ids are ΦΕΚ "
             "labels ('Α 137/2019'), laws also as 'ν. 4624/2019'. Council of State: bot-challenged, not covered.")
    gaps = (
        "ΦΕΚ legislation when hosted for others: needs permission (terms: 'personal, informational, non-commercial use')",
        "Council of State (administrative) case law: bot check / blocks our client",
        "Consolidated legislation: not published online officially (only the ΦΕΚ gazette as published)",
        "ΦΕΚ issues before ~2000: scans only, no text (no OCR)",
        "Areios Pagos before 2006, and appeal/first-instance courts: not researched yet",
    )
    samples = {
        "caselaw_query": "Μίσθωση εργασίας",
        "decision_id": "748DU89FA34LSZPK7Z51H5YW5N5H6D",  # ΑΠ 1/2020 (Ολομέλεια, ποινικές)
        "legislation_query": "Αστικός Κώδικας",
        "law_id": "Α 137/2019",  # ν. 4624/2019 (GDPR implementation)
        "provision": "Άρθρο 5",
    }

    # ----------------------------------------------------------------- case law
    async def search_caselaw(self, query, *, limit, page, filters):
        q = _http.clean(query)
        year = _year(filters)
        note = ""
        m = _NUM_YEAR.match(q)
        if m:
            hits = await _ap_search(m[1], m[2], filters)
        elif re.fullmatch(r"\d{4}", q):
            hits = await _ap_search("1", q, filters, op_number="2")
            note = "Year listing, ordered by chamber/section then number."
            if len(hits) >= 3000 and not filters.get("section") and (filters.get("chamber") or "all").lower() == "all":
                # the site caps one search at 3000: rebuild the year from the per-chamber searches
                seen = {h.id for h in hits}
                for ch in ("civil", "criminal", "3068", "4239", "4842"):
                    more = await _ap_search("1", q, {**filters, "chamber": ch}, op_number="2")
                    hits = hits + [h for h in more if h.id not in seen]
                    seen.update(h.id for h in more)
                note += " Combined from the civil, criminal and special-procedure listings (the site caps one search at 3000)."
            elif len(hits) >= 3000:
                note += (" The site caps a search at 3000, so this total may be a cap, not the "
                         "number of decisions in the year.")
        elif re.fullmatch(r"\d{4}\s*[-–—]\s*\d{4}", q):
            raise BadRequest("Year ranges are not supported: the site takes one year per search. "
                             "Run each year separately ('2022', '2023', '2024').")
        else:
            hits, names = await _ap_subject_hits(q)
            if year:
                hits = [h for h in hits if h.case_number.endswith("/" + year)]
            sect = filters.get("section", "").upper()
            chamber = (filters.get("chamber") or "").lower()
            if sect:
                hits = [h for h in hits if re.search(rf"- {re.escape(sect)}\)$", h.title)]
            if chamber in ("civil", "criminal"):
                word = "ΠΟΛΙΤΙΚΕΣ" if chamber == "civil" else "ΠΟΙΝΙΚΕΣ"
                hits = [h for h in hits if word in h.title]
            stems = _stems(q)
            partial = any(not all(s in _fold(n) for s in stems) for n in names)
            note = ("Subject-index search (no free text at Areios Pagos; index mostly 2007–2010). "
                    + ("No heading contains all your words, so only the most specific word was used. " if partial else "")
                    + (f"Matched: {'; '.join(names[:3])}" + (" …" if len(names) > 3 else "")
                       + ". Only decisions filed under these headings are returned, not every decision on the topic."
                       if names else "No subject heading matched; try a number like '1/2020' or a year."))
            if names and "μισθωση" in _fold(q) and not any(_fold(n) == "μισθωση" for n in names) \
                    and not any("πραγματοσ" in _fold(n) for n in names):
                note += (" There is no heading for the civil lease (μίσθωση πράγματος, ΑΚ 574 ff.): "
                         "these are employment/work-contract decisions. Search by number ('1/2020') or year instead.")
        start = (page - 1) * limit
        return Results(items=hits[start:start + limit], total=len(hits), note=note)

    async def get_decision(self, id):
        cd = _http.clean(id)
        m = _NUM_YEAR.match(cd)
        if m:
            hits = await _ap_search(m[1], m[2], {})
            if not hits:
                raise NotFound(f"No Areios Pagos decision {m[1]}/{m[2]}.")
            if len(hits) > 1:
                raise BadRequest(f"{m[1]}/{m[2]} matches {len(hits)} decisions (numbering is per "
                                 "chamber); use one id: " + ", ".join(f"{h.id} {h.title}" for h in hits))
            cd = hits[0].id
        if not _AP_ID.match(cd):
            raise BadRequest("Areios Pagos id is the 30-character 'cd' code from search "
                             "(e.g. 748DU89FA34LSZPK7Z51H5YW5N5H6D), or a number like '1/2020'.")
        url = f"{AP_BASE}apofaseis_DISPLAY.asp?cd={cd}"
        r = await _http.get(url)
        if r.status_code == 404:
            raise NotFound(f"No Areios Pagos decision with id {cd}.")
        if r.status_code != 200:
            raise SourceError(_http.error("Areios Pagos", "decision fetch failed", r.status_code), r.status_code)
        page = r.content.decode(ENC, "replace")
        body = re.search(r'(?s)<font face="Arial" size="3">(.*?)<p align="center"><A HREF="apofaseis\.asp"', page)
        if not body:
            raise SourceError("Areios Pagos: unexpected decision page layout.", r.status_code)
        head = re.search(r"Απόφαση\s*<b>\s*(\d+)\s*/\s*(\d{4})\s*</b>(?:&nbsp;?|\s)*\(([^)]*)\)", body[1])
        number = f"{head[1]}/{head[2]}" if head else ""
        info = _http.clean(head[3]) if head else ""
        text_html = body[1][head.end():] if head else body[1]
        text = _http.html_to_md(text_html.replace("&nbsp", " "))
        return Decision(
            id=cd, title=f"{COURT} {number}" + (f" ({info})" if info else ""), text=text, url=url,
            court=COURT, date=_greek_date(text[-1500:]), case_number=number,
            metadata={"Τμήμα": info} if info else {})

    # -------------------------------------------------------------- legislation
    async def search_legislation(self, query, *, limit, page, filters):
        q = _http.clean(query)
        year = _year(filters)
        issue = (filters.get("issue") or "Α").upper().translate(_LATIN)
        if issue != "ALL" and issue not in _ISSUES:
            raise BadRequest(f"issue must be one of {', '.join(_ISSUES)} or 'all'.")
        note = "ΦΕΚ text as published (not consolidated)."
        m = _LAW.match(q)
        if m:
            rows = await _et("searchlegislation", {"legislationCatalogues": "", "legislationNumber": m[2],
                                                    "selectYear": [m[3]]})
        elif _FEK.match(q.upper().translate(_LATIN)):
            i, n, y = _fek_parts(q)
            rows = await _et("simplesearch", _simple(year=y, issue=str(i), number=n))
        else:
            if not _stems(q):
                raise BadRequest("Give words, a law number ('ν. 4624/2019') or a ΦΕΚ label ('Α 137/2019').")
            rows = []
            if year:
                key = ("leg", year)
                if key not in _lists:
                    _http.lru_put(_lists, key, await _et("searchlegislation", {
                        "legislationCatalogues": "", "legislationNumber": "", "selectYear": [year]}), 8)
                stems = _stems(q)
                rows = [r for r in _lists[key] if all(s in _fold(r.get("search_Description", "")) for s in stems)]
                if rows:
                    note += f" Matched law/decree titles of {year}."
            if not rows:
                key = ("ft", q, year, issue)
                if key not in _lists:
                    found = await _et("simplesearch", _simple(q, year, "" if issue == "ALL" else str(_ISSUES[issue])))
                    found.sort(key=lambda r: _us_date(r.get("search_PublicationDate", "")), reverse=True)
                    _http.lru_put(_lists, key, found, 8)
                rows = _lists[key]
                note += " Full-text search of the gazette, newest first."
        start = (page - 1) * limit
        return Results(items=[_law_hit(r) for r in rows[start:start + limit]], total=len(rows), note=note)

    async def get_legislation_text(self, id):
        issue, number, year, title = await _resolve(id)
        paras = await _fek_text(issue, number, year)
        return LawText(id=_fek_label(issue, number, year), title=title, text=_render(paras),
                       url=_pdf_url(issue, number, year),
                       metadata={"Note": "Government Gazette text as published, not consolidated"})

    async def get_legislation_toc(self, id):
        issue, number, year, title = await _resolve(id)
        paras = await _fek_text(issue, number, year)
        arts = dict((i, label) for label, i in _articles(paras))
        entries = []
        for i, p in enumerate(paras):
            if i in arts:
                nxt = paras[i + 1] if i + 1 < len(paras) else ""
                heading = nxt if nxt and len(nxt) < 150 and not re.search(r"[.:;]$", nxt) and not _ART.match(nxt) else ""
                entries.append(TocEntry(title=f"{arts[i]} – {heading}" if heading else arts[i],
                                        level=1, provision=arts[i]))
            elif _HEADING.match(p):
                entries.append(TocEntry(title=p, level=0))
        return Toc(id=_fek_label(issue, number, year), title=title, url=_pdf_url(issue, number, year),
                   entries=entries)

    async def get_legislation_provision(self, id, provision):
        issue, number, year, title = await _resolve(id)
        paras = await _fek_text(issue, number, year)
        arts = _articles(paras)
        want = _norm_prov(provision)
        for k, (label, i) in enumerate(arts):
            if _norm_prov(label) == want:
                end = arts[k + 1][1] if k + 1 < len(arts) else len(paras)
                chunk = [p for p in paras[i:end] if not _HEADING.match(p)]
                return Provision(law_id=_fek_label(issue, number, year), law_title=title,
                                 provision=label, text=_render(chunk), url=_pdf_url(issue, number, year))
        raise NotFound(f"{provision!r} not found in ΦΕΚ {_fek_label(issue, number, year)}; "
                       "see get_legislation_toc for labels (e.g. 'Άρθρο 5').")
