"""Pakistan: Islamabad High Court (mis.ihc.gov.pk) for judgments. Legislation from The Pakistan
Code (pakistancode.gov.pk, Ministry of Law and Justice) is active; the host's TLS chain is
incomplete, which _PakistanCodeLegislation works around.

Legislation, pakistancode.gov.pk (server-rendered HTML + PDF):
  * Search: GET /english/sHyuRxF?title=&cat=&year=&type=title&search=1 (the site's own search
    form). Title words, category id and/or year. All matches on one page, no paging, no count.
    Each hit links /english/UY2FqaJw1-apaUY2Fqa-{token}-sg-jjjjjjjjjjjjj; the token (e.g.
    "a50=" = Contract Act, 1872) is the site's own law id (its scripts pass it as apaUY2Fqa=),
    and is the id used here.
  * The law page carries only the title and a link to the consolidated PDF (/pdffiles/...pdf);
    there is no HTML text. The PDFs have a text layer: a CONTENTS list, then the text. The TOC
    and sections are read from that text (no OCR; a scan-only PDF yields a pointer to the PDF).
  * Unknown tokens give a page with no title and no PDF -> NotFound.

Case law, Islamabad High Court (mis.ihc.gov.pk "Case Law System", /frmSrchOrdr.aspx):
  * The page's own JSON web service: POST /ihc.asmx/srchDecision1 (keyword search over the
    court's judgment records) and /ihc.asmx/srchDecision (party name). All rows come back at
    once (the keyword search stops at 2000 rows). Each row links a judgment PDF under
    /attachments/judgements/{case}/{n}/{file}.pdf; that path is the id here.

Not used (checked 2026-11-06):
  * Supreme Court (www.supremecourt.gov.pk): Akamai "Access Denied" (403) to this client,
    even for robots.txt. Not worked around.
  * Federal Shariat Court (federalshariatcourt.gov.pk) and Lahore High Court judgments
    (data.lhc.gov.pk): connection timed out from here (2 tries each, 30-60 s).
  * Sindh High Court case law (caselaw.shc.gov.pk): redirects to a login page.

Verified 2026-11-06:
  * pakistancode.gov.pk/robots.txt: "User-agent: googlebot / Disallow: /pdffiles/" only
    (nothing for other agents); no terms of use; disclaimer page /english/Xki72HF.php
    ("for information purposes only ... refer to the ... Gazette notification(s)").
  * mis.ihc.gov.pk/robots.txt: 404. No terms of use; footer disclaimer only ("for
    information only ... not ... for official purposes").
"""
from __future__ import annotations

import json
import re
from urllib.parse import quote, unquote, urlsplit

from lxml import html as LH

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

PC_HOST = "pakistancode.gov.pk"
PC = f"https://{PC_HOST}/english"
_PRE, _SUF = "UY2FqaJw1-apaUY2Fqa-", "-sg-jjjjjjjjjjjjj"
IHC_HOST = "mis.ihc.gov.pk"
IHC = f"https://{IHC_HOST}"
IHC_COURT = "Islamabad High Court"
IHC_CAP = 2000
CATEGORIES = {   # the search form's category ids (pakistancode.gov.pk/english/, 2026-11-06)
    "1": "Criminal Laws", "2": "Civil Laws", "3": "Family Laws", "4": "Service Laws",
    "5": "Labour Laws", "6": "Police Laws", "7": "Companies Laws", "8": "Land/Property Laws",
    "9": "Islamic/Religious Laws", "10": "Banking/Financial Laws", "11": "Law of Evidence",
    "12": "Rent Laws", "13": "International Laws", "14": "Tenancy Laws",
    "15": "Land Reform Laws", "16": "Minorities Laws", "17": "Excise/Taxation Laws",
    "18": "Military Laws", "19": "Health/Medical Laws", "20": "Media Laws",
    "21": "Election Laws", "22": "Departmental Laws", "23": "General Laws",
}
REPORTED = {"all": "9999", "afr": "1", "important": "0"}

_TOKEN = re.compile(r"^[A-Za-z0-9+/=]{2,60}$")
_PAGE = re.compile(r"^Page \d+ of \d+$")
_LABEL = re.compile(r"^(?:\d{1,3}\[)?\[?(\d+[A-Z]{0,3}(?:\s*(?:to|-|–)\s*\d+[A-Z]{0,3})?)\.\s*(.*)$")
_PAREN = re.compile(r"^\((\d+[A-Z]{1,3})\)\s+(.*)$")   # amended-in sections shown as '(2E) Removal ...'
_NEWPARA = re.compile(r"^(\(\w{1,6}\)|\d+[A-Z]{0,3}\.\s|\d{1,3}\[|Explanation|Illustration|Exception|"
                      r"Provided|CHAPTER|PART\b|SCHEDULE|THE [A-Z])")
_IHC_DOC = re.compile(r"^judgements/[\w.\-()/%,&+ ]+\.pdf$", re.I)

_law_cache: dict = {}
_search_cache: dict = {}
_ihc_meta: dict = {}
_shortened: dict = {}   # keyword search key -> the shorter phrase that actually matched


# --------------------------------------------------------------------------- #
# legislation helpers
# --------------------------------------------------------------------------- #
def _token(id) -> str:
    s = unquote(str(id).strip())
    if s.startswith("http"):
        s = urlsplit(s).path.rsplit("/", 1)[-1]
    if s.startswith(_PRE) and s.endswith(_SUF):
        s = s[len(_PRE):-len(_SUF)]
    if not _TOKEN.match(s):
        raise BadRequest("Use the Pakistan Code law id from search_legislation, e.g. 'a50=' "
                         "(Contract Act, 1872), or the law's pakistancode.gov.pk URL.")
    return s


def _law_url(token: str) -> str:
    return f"{PC}/{_PRE}{quote(token, safe='')}{_SUF}"


def _norm(label: str) -> str:
    s = _http.clean(label).lower()
    s = re.sub(r"^(section|sec\.?|s\.|article|art\.?|ss\.)\s*", "", s)
    s = re.sub(r"\s*(to|–|-)\s*", "-", s)
    s = re.sub(r"[\s.]", "", s)
    s = re.sub(r"(?<=\d)-(?=[a-z]+$)", "", s)    # '337-A' -> '337a', '203-GG' -> '203gg'
    return s


def _label(raw: str) -> str:
    """Display label: '19A', '239-266'."""
    return re.sub(r"\s*(?:to|–|-)\s*", "-", _http.clean(raw)).upper()


def _paras(lines: list[str]) -> str:
    """PDF lines -> markdown paragraphs (re-joins wrapped lines)."""
    out: list[str] = []
    for ln in lines:
        if out and not _NEWPARA.match(ln) and not re.search(r"[.:;—_]$", out[-1]):
            out[-1] += " " + ln
        else:
            out.append(ln)
    return "\n\n".join(out)


def _split(text: str) -> tuple[list[tuple[str, str, int]], list[str], list[tuple[str, int]]]:
    """Consolidated-law PDF text -> (contents entries [(label, title, level)], body lines,
    section starts [(label, line index)])."""
    lines = [ln for ln in text.splitlines() if ln.strip() and not _PAGE.match(ln.strip())]
    contents: list[tuple[str, str, int, int]] = []     # label, title, level, line index
    start = 0
    seen: set[str] = set()
    for i, ln in enumerate(lines):
        m = _LABEL.match(ln)
        if m:
            lab = _label(m[1])
            if lab in seen:          # numbering restarts: the body begins
                start = i
                break
            seen.add(lab)
            contents.append((lab, _http.clean(m[2]), 1, i))
        elif contents and ln[:1].islower():      # wrapped title
            lab, t, lv, k = contents[-1]
            contents[-1] = (lab, f"{t} {ln}", lv, k)
        elif contents and not re.fullmatch(r"[_\-\s]+", ln):
            top = ln.isupper() or bool(re.match(r"(CHAPTER|PART)\b", ln))
            if top and contents[-1][0] == "" and contents[-1][2] == 0:   # wrapped heading
                contents[-1] = ("", f"{contents[-1][1]} {ln}", 0, contents[-1][3])
            else:
                contents.append(("", ln, 0 if top else 2, i))
    if start:
        # the text proper starts where the law's title line (first line of the PDF) repeats
        top = next((k for k in range(start - 1, 0, -1) if lines[k] == lines[0]), start)
        contents = [c for c in contents if c[3] < top]
        start = top
    else:                        # no contents list: the whole text is the body
        contents = []
    body = lines[start:]
    order = [c[0] for c in contents if c[0]]
    titles = {c[0]: c[1] for c in contents if c[0]}
    starts: list[tuple[str, int]] = []
    pos = -1
    for i, ln in enumerate(body):
        m = _LABEL.match(ln) or (_PAREN.match(ln) if order else None)
        if not m:
            continue
        lab = _label(m[1])
        if not order:           # no contents: take numbered lines in rising order
            n = int(re.match(r"\d+", lab)[0])
            if not starts or n >= int(re.match(r"\d+", starts[-1][0])[0]):
                if lab not in {s for s, _ in starts}:
                    starts.append((lab, i))
            continue
        if lab not in titles:
            continue
        k = order.index(lab)
        if k <= pos or k > pos + 6:
            continue
        want, got = re.findall(r"\w+", titles[lab].lower())[:1], re.findall(r"\w+", m[2].lower())[:1]
        if want and got and want != got and want != ["repealed"]:
            continue    # a numbered list item inside a section, not the next section
        starts.append((lab, i))
        pos = k
    if not contents:
        contents = [(lab, _http.clean(_LABEL.match(body[i])[2])[:120], 1, i) for lab, i in starts]
    return [c[:3] for c in contents], body, starts


async def _law(token: str) -> dict:
    hit = _law_cache.get(token)
    if hit:
        return hit
    url = _law_url(token)
    r = await _http.get(url)
    if r.status_code != 200:
        raise SourceError(_http.error(PC_HOST, "law page failed", r.status_code), r.status_code)
    root = LH.fromstring(r.text or "<html/>")
    t = root.find(".//title")
    title = _http.clean(t.text_content()) if t is not None else ""
    if title.lower() in ("", "the pakistan code", "pakistan code"):
        title = ""
    pdfs = [a.get("href") for a in root.xpath("//div[@id='download']//a[@href]")
            if a.get("href", "").lower().endswith(".pdf")]
    if not title and not pdfs:
        raise NotFound(f"pakistancode.gov.pk has no law with id {token!r}.")
    if not pdfs:
        m = re.search(r"pdffiles/[\w.\-]+\.pdf", r.text)
        pdfs = [f"https://{PC_HOST}/{m[0]}"] if m else []
    if not pdfs:
        raise SourceError(f"pakistancode.gov.pk law {token}: no PDF link on the page.")
    pdf = pdfs[0] if pdfs[0].startswith("http") else f"https://{PC_HOST}/{pdfs[0].lstrip('/')}"
    p = await _http.get(pdf)
    if p.status_code != 200 or not p.content.startswith(b"%PDF"):
        raise SourceError(_http.error(PC_HOST, "PDF fetch failed", p.status_code), p.status_code)
    try:
        text = _http.pdf_text(p.content)
    except Exception:
        text = ""
    contents, body, starts = _split(text) if text else ([], [], [])
    m = re.search(r"^Date:\s*(\d{1,2}-\d{1,2}-\d{4})$", text, re.M)
    data = {"title": title or token, "url": url, "pdf": pdf, "text": text, "as_of": _http.iso_date(m[1]) if m else "",
            "contents": contents, "body": body, "starts": starts}
    return _http.lru_put(_law_cache, token, data, 8)


# --------------------------------------------------------------------------- #
# case-law helpers
# --------------------------------------------------------------------------- #
def _ihc_date(s: str) -> str:
    m = re.match(r"(\d{1,2})-([A-Za-z]{3})-(\d{4})$", _http.clean(s))
    if not m:
        return ""
    mon = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    k = m[2].lower()
    return f"{m[3]}-{mon.index(k) + 1:02d}-{int(m[1]):02d}" if k in mon else ""


def _dash(s) -> str:
    s = _http.clean(s)
    return "" if s.lower() in ("-", "nil", "none", "null", "citation awaited") else s


def _ihc_rows(payload: dict) -> list[DecisionHit]:
    d = payload.get("d")
    if not d or d == '"empty"':
        return []
    try:
        rows = json.loads(d)
    except ValueError:
        raise SourceError("mis.ihc.gov.pk: unexpected search payload")
    hits = []
    for r in rows:
        att = str(r.get("ATTACHMENTS") or "").strip()
        if not att.lower().endswith(".pdf"):
            continue
        doc = att.lstrip("/").removeprefix("attachments/")
        title = _http.clean(r.get("PARTIES") or r.get("TITLE") or "")
        title = re.sub(r"\s*-?\s*\bVS\b\s*-?\s*", " v ", title)
        case = _http.clean(r.get("CASENO"))
        afr = {1: "Approved for reporting", 0: "Important"}.get(r.get("O_AFR"), "")
        meta = {"Subject": _dash(r.get("O_SUBJECT")).rstrip(", "), "Bench": _dash(r.get("BENCHNAME")),
                "Author": _dash(r.get("AUTHOR_JUDGES")), "Citation": _dash(r.get("O_CITATION")),
                "Description": _dash(r.get("O_REMARKS")), "Laws discussed": _dash(r.get("O_UNDERSECTION")),
                "Head note": _dash(r.get("O_IHC_HEADNOTE") or r.get("HEADNOTE")), "Category": afr}
        h = DecisionHit(id=doc, title=title or f"{IHC_COURT} {case}", court=IHC_COURT,
                        date=_ihc_date(r.get("DDATE") or ""), case_number=case,
                        snippet="; ".join(v for v in (meta["Subject"], meta["Description"][:300],
                                                      meta["Laws discussed"][:150],
                                                      meta["Citation"], afr) if v),
                        url=f"{IHC}/attachments/{quote(doc)}")
        _ihc_meta[doc] = {"title": h.title, "date": h.date, "case_number": case, **meta}
        while len(_ihc_meta) > 3000:
            _ihc_meta.pop(next(iter(_ihc_meta)))
        hits.append(h)
    return hits


# --------------------------------------------------------------------------- #
class _PakistanCodeLegislation:
    """Legislation from the Pakistan Code (mixed into `Pakistan` since the truststore change).

    pakistancode.gov.pk sends an incomplete TLS chain (2026-11-06): its certificate is issued by
    "GoGetSSL RSA DV CA", but the server sends "GoGetSSL RSA DV SSL CA 2" instead of that
    intermediate. A client using only bundled CAs fails with CERTIFICATE_VERIFY_FAILED; _http
    checks certificates against the OS trust store (truststore), which completes the chain on
    macOS/Windows; on Linux _http loads the intermediate from intermediates.pem. This class is
    already in Pakistan's bases and SOURCE in Pakistan.sources.
    """
    SOURCE = Source(
        name="The Pakistan Code (pakistancode.gov.pk), Ministry of Law and Justice",
        url=f"{PC}/",
        covers=("legislation",),
        licence="unknown: no terms of use or licence; footer '© Copyright 2022 - Ministry of Law "
                "and Justice'",
        commercial_use=None,
        ai_use=None,     # robots.txt only blocks googlebot from /pdffiles/; no AI/TDM clause
        auth="none",
        rate_limit="unknown; 1 s spacing, no 429 seen in ~15 requests (2026-11)",
        terms_url=f"{PC}/Xki72HF.php",
        warning="Pakistan Code texts are 'for information purposes only' and 'under review'; "
                "the Gazette notification is the authentic text.",
    )
    legislation_filters = {
        "category": "category id or name, e.g. '2' or 'Civil Laws' "
                    "(1 Criminal, 2 Civil, 3 Family, 5 Labour, 7 Companies, 10 Banking/Financial, ...23 General). "
                    "The site's own tagging is patchy: the Penal Code and Code of Criminal "
                    "Procedure sit under 23 General Laws, not 1 Criminal",
        "year": "year of the law, e.g. '1872'",
    }

    # ------------------------------------------------------------------ legislation
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        f = {k: _http.clean(v) for k, v in (filters or {}).items() if _http.clean(v)}
        q = _http.clean(query)
        cat = f.get("category", "")
        if cat and cat not in CATEGORIES:
            by_name = {v.lower(): k for k, v in CATEGORIES.items()}
            cat = by_name.get(cat.lower()) or by_name.get(f"{cat.lower()} laws", "")
            if not cat:
                raise BadRequest("category must be an id 1-23 or a name such as 'Civil Laws'; "
                                 f"got {f['category']!r}.")
        year = f.get("year", "")
        if year and not re.fullmatch(r"\d{4}", year):
            raise BadRequest(f"year must be four digits, e.g. 1872; got {year!r}.")
        if not (q or cat or year):
            raise BadRequest("Give words of the law's title, or a year or category filter.")
        key = (q.lower(), cat, year)
        rows = _search_cache.get(key)
        if rows is None:
            r = await _http.get(f"{PC}/sHyuRxF", params={"title": q, "cat": cat, "year": year,
                                                         "type": "title", "search": "1"})
            if r.status_code != 200:
                raise SourceError(_http.error(PC_HOST, "search failed", r.status_code), r.status_code)
            rows = self._parse_search(r.text)
            words = q.split()
            while not rows and len(words) > 1:   # the site's title match fails on some long phrases
                words.pop()
                r = await _http.get(f"{PC}/sHyuRxF", params={"title": " ".join(words), "cat": cat,
                                                             "year": year, "type": "title", "search": "1"})
                if r.status_code != 200:
                    break
                rows = [h for h in self._parse_search(r.text)
                        if all(w in h.title.lower() for w in re.findall(r"\w+", q.lower())
                               if w not in ("of", "the", "and"))]
            rows = _http.lru_put(_search_cache, key, rows, 32)
        if not rows and cat:   # the site files some laws under another category (Penal Code under General Laws)
            wider = await self.search_legislation(
                query, limit=limit, page=page, filters={k: v for k, v in f.items() if k != "category"})
            if wider.items:
                return Results(items=wider.items, total=wider.total,
                               note=wider.note + f" Nothing is filed under category {cat} "
                                    f"({CATEGORIES[cat]}) for this title, so these are the matches "
                                    "without the category filter (the site files them under other categories).")
        limit = max(1, int(limit))
        start = (max(1, int(page)) - 1) * limit
        capped = len(rows) >= 100
        return Results(items=rows[start:start + limit], total=None if capped else len(rows),
                       note="Searches law titles (federal laws). Ids are the site's own law tokens, "
                            "e.g. 'a50=' for the Contract Act, 1872."
                            + (" No match under this category: the site files some laws elsewhere "
                               "(e.g. Penal Code under 23 General Laws); retry without the category."
                               if not rows and cat else "")
                            + (" The list may be capped at 100 rows (inferred, unverified): narrow "
                               "with a title word, year or category." if capped else ""))

    @staticmethod
    def _parse_search(page: str) -> list[LawHit]:
        root = LH.fromstring(page or "<html/>")
        hits, seen = [], set()
        for sec in root.xpath("//div[@id='all_laws']//div[contains(@class,'accordion-section')]"
                              "[div[contains(@class,'accordion-section-title')]]"):
            a = sec.find(".//div[@class='accordion-section-title']/a")
            if a is None:
                a = next(iter(sec.xpath(".//div[contains(@class,'accordion-section-title')]//a")), None)
            if a is None:
                continue
            href = a.get("href", "")
            try:
                tok = _token(href)
            except BadRequest:
                continue
            if tok in seen:
                continue
            seen.add(tok)
            info = sec.xpath(".//div[contains(@class,'accordion-section-content')]")
            parts = [_http.clean(x) for x in (info[0].text_content() if info else "").split("|")]
            cat = parts[0] if parts else ""
            number = parts[1] if len(parts) > 1 else ""
            m = re.search(r"Promulgation Date:\s*([A-Za-z]+)\s+(\d{1,2})\s+(\d{4})", info[0].text_content() if info else "")
            date = _http.en_date(f"{m[1]} {m[2]}, {m[3]}") if m else ""
            title = _http.clean(a.text_content())
            kind = next((w for w in ("Ordinance", "Order", "Act", "Regulation", "Rules", "Code",
                                     "Constitution") if re.search(rf"\b{w}\b", title)), "")
            hits.append(LawHit(id=tok, title=title, type=kind,
                               number="" if number.startswith("of ") else number, date=date,
                               status="under review" if "under review" in title.lower() else "",
                               snippet=cat, url=_law_url(tok)))
        return hits

    async def get_legislation_toc(self, id):
        tok = _token(id)
        law = await _law(tok)
        entries = [TocEntry(f"{lab}. {t}" if lab else t, lv, lab) for lab, t, lv in law["contents"]]
        if not entries:
            raise SourceError(f"{law['title']}: no text layer in the PDF, so no contents; "
                              f"read it at {law['pdf']}")
        found = {lab for lab, _ in law["starts"]}
        return Toc(id=tok, title=law["title"], url=law["url"],
                   entries=[e if not e.provision or e.provision in found
                            else TocEntry(e.title, e.level, "") for e in entries])

    async def get_legislation_provision(self, id, provision):
        tok = _token(id)
        law = await _law(tok)
        want = _norm(str(provision))
        if not want:
            raise BadRequest("Give a section label as the TOC shows it, e.g. '10' or '19A'.")
        starts = law["starts"]
        idx = next((k for k, (lab, _) in enumerate(starts) if _norm(lab) == want), None)
        if idx is None:     # inside a repealed range such as '239-266'
            for k, (lab, _) in enumerate(starts):
                m = re.fullmatch(r"(\d+)-(\d+)", _norm(lab))
                if m and want.isdigit() and int(m[1]) <= int(want) <= int(m[2]):
                    idx = k
                    break
        if idx is None:
            raise NotFound(f"{law['title']} has no section {provision!r} in the Pakistan Code text; "
                           "see get_legislation_toc.")
        lab, i = starts[idx]
        end = starts[idx + 1][1] if idx + 1 < len(starts) else len(law["body"])
        text = _paras(law["body"][i:end])
        return Provision(law_id=tok, law_title=law["title"], provision=lab,
                         text=f"## Section {lab}\n\n{text}", url=law["url"], as_of=law["as_of"])

    async def get_legislation_text(self, id):
        tok = _token(id)
        law = await _law(tok)
        if not law["text"]:
            text = ("The Pakistan Code has this law only as a scanned PDF (no text layer), so no "
                    f"text can be returned here. Read it at: {law['pdf']}")
        else:
            text = _paras(law["body"] or law["text"].splitlines())
        return LawText(id=tok, title=law["title"], text=text, url=law["url"], as_of=law["as_of"],
                       metadata={"PDF": law["pdf"]})


class Pakistan(_PakistanCodeLegislation, Jurisdiction):
    code = "pk"
    name = "Pakistan"
    languages = ("en",)
    aliases = ("pakistan", "pak", "islamic republic of pakistan", "pakistan code",
               "islamabad high court")
    sources = (
        Source(
            name="Islamabad High Court (mis.ihc.gov.pk) – Case Law System",
            url=f"{IHC}/frmSrchOrdr.aspx",
            covers=("caselaw",),
            licence="unknown: no terms of use or licence; footer disclaimer only",
            commercial_use=None,
            ai_use=None,     # robots.txt 404; no AI/TDM clause
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~10 requests (2026-11); a broad "
                       "keyword search returns up to 2000 rows (~2 MB, ~9 s)",
            terms_url="",
        ),
        _PakistanCodeLegislation.SOURCE,
    )
    caselaw_filters = {
        "parties": "party name (min. 5 letters); searches case titles instead of the keyword index",
        "case_year": "year the case was filed, e.g. '2024' (matched on the year in the case number)",
        "reported": "all (default) | afr (approved for reporting) | important",
    }
    min_interval = {PC_HOST: 1.0, IHC_HOST: 1.0}
    notes = ("Case law: Islamabad High Court judgments only (Supreme Court site blocks automated "
             "clients). Legislation from the Pakistan Code.")
    gaps = (
        "Supreme Court judgments (supremecourt.gov.pk): Akamai 'Access Denied' (403) blocks our "
         "client",
        "Federal Shariat Court and Lahore High Court: site down / unreachable (connection "
         "timeout, 2026-11-06)",
        "Sindh High Court case law (caselaw.shc.gov.pk): needs a login (whether registration is "
         "public is unverified)",
        "Peshawar and Balochistan High Courts, lower courts and provincial legislation: not "
         "researched yet",
    )
    samples = {
        "caselaw_query": "khula",
        "decision_id": "judgements/211268/2/R.F.A_NO._56_OF_2026_(contested)_639294682208399606.pdf",
        "legislation_query": "contract",
        "law_id": "a50=",
        "provision": "10",
    }

    # ------------------------------------------------------------------ case law
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        f = {k: _http.clean(v) for k, v in (filters or {}).items() if _http.clean(v)}
        q = _http.clean(query).replace("'", " ")
        rep = f.get("reported", "all").lower()
        if rep not in REPORTED:
            raise BadRequest(f"reported must be all, afr or important; got {rep!r}.")
        cy = f.get("case_year", "0")
        if cy != "0" and not re.fullmatch(r"\d{4}", cy):
            raise BadRequest(f"case_year must be four digits, e.g. 2024; got {cy!r}.")
        parties = f.get("parties", "").replace("'", " ")
        if parties:
            if len(parties) < 5:
                raise BadRequest("parties needs at least 5 letters (the court's own minimum).")
            key = ("p", parties.lower(), rep)
            method = "srchDecision"
            body = {"PCASENO": "0", "PJUG": "0", "PADV": "0", "PYEAR": "0", "pPrty": parties,
                    "PDDATE": "01-01-1900", "PLANDMARK": "1", "PAFR": REPORTED[rep]}
        else:
            if len(q) < 3:
                raise BadRequest("Give a keyword (3+ letters), or a parties filter.")
            key = ("k", q.lower(), rep)
            method = "srchDecision1"
            body = {"PKYWRD": q, "PCSEKWYR": "0", "PAFR": REPORTED[rep], "PISSWS": "0"}
        rows = _search_cache.get(key)
        shortened = ""
        if rows is None:
            r = await _http.post(f"{IHC}/ihc.asmx/{method}", content=json.dumps(body),
                                 headers={"Content-Type": "application/json; charset=utf-8"})
            if r.status_code != 200:
                raise SourceError(_http.error(IHC_HOST, "search failed", r.status_code), r.status_code)
            try:
                payload = r.json()
            except ValueError:
                raise SourceError("mis.ihc.gov.pk: search did not return JSON")
            rows = _ihc_rows(payload)
            words = q.split()
            while not rows and not parties and len(words) > 1:   # index matches one exact phrase: shorten it
                words.pop()
                used = " ".join(words)
                if len(used) < 3:
                    break
                r = await _http.post(f"{IHC}/ihc.asmx/{method}", content=json.dumps({**body, "PKYWRD": used}),
                                     headers={"Content-Type": "application/json; charset=utf-8"})
                if r.status_code != 200:
                    break
                try:
                    rows = _ihc_rows(r.json())
                except ValueError:
                    break
                if rows:
                    shortened = used
            rows = _http.lru_put(_search_cache, key, rows, 16)
            if shortened:
                _shortened[key] = shortened
        shortened = _shortened.get(key, "")
        capped = method == "srchDecision1" and len(rows) >= IHC_CAP
        year_partial = False
        if cy != "0":  # the court's server ignores its year field: filter on the case number's year
            rows = [h for h in rows if re.search(rf"[-/\s]{cy}$", h.case_number or "")]
            if capped:  # the 2000-row slice is not ordered by filing year: only a partial answer is possible
                if not rows:
                    raise BadRequest(f"'{q}' matches 2000+ decisions, and the court returns only a slice of them "
                                     f"that is not ordered by filing year; none of that slice was filed in {cy}, "
                                     "which does not prove there are none. Use a more specific keyword "
                                     "(e.g. 'post arrest bail'), or the parties filter.")
                year_partial = True
        ranked = ""
        if not parties:   # the court's order is by date: put rows whose subject/laws/headnote contain the words first
            ws = [w for w in re.findall(r"\w+", q.lower())
                  if len(w) > 2 and w not in ("the", "and", "for")]
            def score(h):
                m = _ihc_meta.get(h.id, {})
                t = " ".join([h.title, h.snippet] + [str(m.get(k, "")) for k in ("Laws discussed", "Head note")]).lower()
                return -sum(w in t for w in ws)
            if ws and all(isinstance(h, DecisionHit) for h in rows):
                rows = sorted(rows, key=score)
                ranked = (" Results are re-ordered so decisions whose subject, laws discussed or head note "
                          "contain your words come first" + (" (within the 2000 rows the court returned)"
                          if capped else "") + "; the court's index does not rank by relevance.")
        limit = max(1, int(limit))
        start = (max(1, int(page)) - 1) * limit
        note = ("Islamabad High Court only. "
                + ("The court's search stops at 2000 rows (not ordered by filing year): narrow the keyword."
                   if capped else "Keyword search uses the court's own index (not always the "
                   "judgment's wording)." if not parties else
                   f"Matched on party names only: the keyword '{q}' was NOT applied, so the count is "
                   "all decisions for that party name.")
                + (f" Year {cy} was applied only to the first 2000 rows the court returned (not ordered by "
                   "filing year), so this list is partial: decisions from that year outside the slice are "
                   "missing. A more specific keyword gives a complete year list." if year_partial else "")
                + (f" The court's index matches the keyword as one exact phrase and nothing matched all of "
                   f"'{q}', so these are the results for '{shortened}' only (the other words were NOT applied)."
                   if shortened else "")
                + (" The court's index matches the keyword as one exact phrase, so several words "
                   "that never appear together give no result: try 1-2 words (e.g. 'fundamental "
                   "rights')." if not rows and not parties and len(q.split()) > 2 else ""))
        return Results(items=rows[start:start + limit], total=None if capped else len(rows), note=note + ranked,
                       query_ignored=bool(parties))

    async def get_decision(self, id):
        s = unquote(str(id).strip())
        if s.startswith("http"):
            s = urlsplit(s).path
        s = s.lstrip("/").removeprefix("attachments/")
        if not _IHC_DOC.match(s) or ".." in s:
            raise BadRequest("Use the judgment id from search_caselaw, e.g. 'judgements/211268/2/"
                             "R.F.A_NO._56_OF_2026_(contested)_639294682208399606.pdf', or its "
                             "mis.ihc.gov.pk URL.")
        url = f"{IHC}/attachments/{quote(s)}"
        r = await _http.get(url)
        if r.status_code == 404:
            raise NotFound(f"mis.ihc.gov.pk has no judgment file {s}.")
        if r.status_code != 200 or not r.content.startswith(b"%PDF"):
            raise SourceError(_http.error(IHC_HOST, "judgment fetch failed", r.status_code), r.status_code)
        try:
            text = _http.pdf_text(r.content)
        except Exception:
            text = ""
        meta = dict(_ihc_meta.get(s, {}))
        title = meta.pop("title", "")
        date = meta.pop("date", "")
        case = meta.pop("case_number", "")
        head = text[:2500]
        if not date:
            m = re.search(r"(?:Date of (?:Decision|Judgment|Order|Announcement)|Announced on)\s*[:.\-]*\s*(\d{1,2}[./-]\d{1,2}[./-]\d{4})",
                          text, re.I)
            if not m:  # filename 'decided_on_17.09.2026' / '02.11.2026_W.P_...'; order-sheet row dates are hearings, not decisions
                m = re.search(r"(?:decided_on_|^)(\d{1,2}\.\d{1,2}\.\d{4})", s.rsplit("/", 1)[-1])
            date = _http.iso_date(re.sub(r"[/\-\s]", ".", m[1])) if m else ""
        if not case:  # the order-sheet line right after the 'JUDICIAL DEPARTMENT' header, else a 'Xxx No. N of YYYY' line
            m = (re.search(r"JUDICIAL DEPARTMENT\)?\.?[ \t]*\n[ \t]*([^\n]{3,80}\d[^\n]*)\n", head, re.I)
                 or re.search(r"^(?:\(\d+\)[ \t]*)?((?:[A-Z][\w.()]*[ \t]+){1,5}(?i:No)\.?[ \t]*[\d\-/A-Z]+[ \t]+(?:of|OF)[ \t]+\d{4})",
                              head, re.M))
            case = re.sub(r"^\(\d+\)\s*", "", _http.clean(m[1])) if m else ""
        if not title:
            m = re.search(r"\n(.{3,120})\n(?:Vs\.?|V/S|Versus)\n(.{3,120})\n", head, re.I)
            title = f"{_http.clean(m[1])} v {_http.clean(m[2])}" if m else f"{IHC_COURT} {case or s.rsplit('/', 1)[-1]}"
        if len(text) < 200:
            text = ("The court publishes this judgment only as a scanned PDF (no text layer), so no "
                    f"text can be returned here. Read it at: {url}")
        return Decision(id=s, title=title, text=text, url=url, court=IHC_COURT, date=date,
                        case_number=case, summary=meta.pop("Head note", ""),
                        metadata={k: v for k, v in meta.items() if v} | {"PDF": url})
