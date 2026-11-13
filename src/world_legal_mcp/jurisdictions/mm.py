"""Myanmar: law-report rulings (precedents) and a small set of laws, court procedures and amending
laws, all from the Supreme Court of the Union. Burmese, plus the Code of Civil Procedure and the
Code of Criminal Procedure in English.

Case law: Rulings and Case Management System (RCMS, rcms.usc.gov.mm), verified 2026-11-06.

  * The site is a JavaScript app, but it reads a public JSON API on https://rcms.usc.gov.mm:8000
    (an Elasticsearch pass-through, no login, no key). We call that API directly, with the
    project's own User-Agent, like the app does: POST /api/searchPrecedent/<page>/ (fixed 10 hits a
    page; body = an Elasticsearch bool query), POST /api/getPrecedent/ (one ruling's metadata),
    POST /api/getPrecedentDetail/ (its text, one HTML paragraph per child document).
  * ~6,900 rulings from the law reports (တရားစီရင်ထုံး), mostly 1920s to Dec 2022: the Supreme Court
    of the Union and its predecessors (colonial-era High Court reports are in English, later ones in
    Burmese). Text is Unicode HTML (no Zawgyi/legacy-font problem). The id is RCMS's own numeric
    precedent id. A few records carry a bad date (one reads 0011-04-18).
  * The query matches the title/headnote/case number/type fields and the full text of the ruling
    (has_child on the text paragraphs), each word as a substring (*word*), all words required, like
    the site's own search. Dates are the site's published_date (the judgment date in the report).
  * Needs the OS trust store (_http uses truststore): rcms.usc.gov.mm does not send its
    intermediate certificate. macOS/Windows fetch it; on Linux (OpenSSL) the TLS check fails and
    case law is unreachable.

Laws: www.unionsupremecourt.gov.mm (verified 2026-11-06, UK IP, honest User-Agent).

  * Three short HTML lists, paged with ?page=N (6 rows a page): /laws (~12-15 laws incl. the CPC and
    CrPC in English), /legislativetwo (~8 court procedures), /lawsofamendment (~6 amending laws).
    Each row is an <h3> title and a link to /uploads/legislative/<file>.pdf, plus the date the
    file was posted (not the date of the law). The id is that file name, the only identifier the
    site has. The lists are small, so search reads all of them (5 pages) and matches the query
    against the title and the file name (file names carry English words such as "Companies").
  * The PDFs have a text layer, but many Burmese ones were made with legacy (non-Unicode) fonts:
    pypdf yields letters in visual order or substituted (ဖ for ခ, ြ for ပ) and some lose every
    vowel sign. Texts whose layer is plainly broken are refused (SourceError with the PDF link);
    the rest are served as extracted, with a warning.
  * Sections: English "12. ..." / "35A. ..."; Burmese "၁၂။ ...". The first run of numbers in a
    Burmese law is often its table of contents, so the longest run of sequential numbers wins.

Terms and robots.txt (2026-11-06):
  * www.unionsupremecourt.gov.mm/robots.txt: "User-agent: * / Disallow:" (everything allowed),
    no Crawl-delay. No terms-of-use page; footer "Copyright © 2020 Supreme Court of the Union.
    All Rights Reserved." Page meta robots "index, follow".
  * rcms.usc.gov.mm: no robots.txt (the app answers /robots.txt with its HTML shell; :8000 gives
    404). No terms page; the app's footer: "Copyright © 2020 - The Supreme Court of The Union. All
    Rights Reserved." Nothing about personal use or automated access.

Not used:
  * Commercial Judgment System (cjs.usc.gov.mm, API rcms.usc.gov.mm:8071): ~316 judgments (148 of
    them Supreme Court, up to 2026, rechecked 2026-11-10), one PDF each. Recent ones (2024-) are image scans with no text layer; older ones have a Unicode text
    layer whose Burmese comes out with letters out of order. Its disclaimer: "for public
    information purposes only and should not be relied on as an official certified copy of a
    judgement". Not added: the precedents above are the better source.
  * e-Library (elib.usc.gov.mm): a book reader with user accounts (login), not decisions.
  * Law reports (unionsupremecourt.gov.mm/ruling): one PDF per year, broken legacy-font text;
    superseded by RCMS, which has the same reports as text.
  * Myanmar Law Information System (mlis.gov.mm): connection times out.
  * Pyidaungsu Hluttaw (pyidaungsu.hluttaw.mm): JavaScript-only site, no server-rendered content.
  * myanmar-law-library.org: private individual's site; its legal notice forbids linking without
    prior authorisation.
"""
from __future__ import annotations

import json
import re
import time
from urllib.parse import quote, unquote

from lxml import html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, SourceError
from ..base import Source
from ..models import Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc, TocEntry

HOST = "www.unionsupremecourt.gov.mm"
BASE = f"https://{HOST}/"
FILES = BASE + "uploads/legislative/"
NAME = "Supreme Court of the Union"
MAX_PDF = 40_000_000
LISTS = {"law": "laws", "procedure": "legislativetwo", "amendment": "lawsofamendment"}
TYPE_NAMES = {"law": "Law (ဥပဒေ)", "procedure": "Procedure (လုပ်ထုံးလုပ်နည်း)",
              "amendment": "Amending law (ပြင်ဆင်သည့်ဥပဒေ)"}
LIST_TTL = 6 * 3600

RCMS = "rcms.usc.gov.mm"
RCMS_API = f"https://{RCMS}:8000/api/"
RCMS_PAGE = f"https://{RCMS}/precedentDetail/"
RCMS_PDF = f"https://{RCMS}:8084/api/v1/pdf/download/"
RCMS_NAME = "Supreme Court of the Union (RCMS)"
RCMS_FIELDS = ["court", "precedent_year", "precedent_sub_type", "precedent_no_scr", "precedent_type",
               "precedent_name_scr"]
CASE_TYPES = {"criminal": "ရာဇဝတ်မှု", "civil": "တရားမမှု", "writ": "စာချွန်တော်"}

_MY_DIGITS = str.maketrans("၀၁၂၃၄၅၆၇၈၉", "0123456789")
_EN_SEC = re.compile(r"^(\d{1,3})([A-Z]{0,2})(?:\s*[-–]\s*(\d{1,3}))?\.\s+(\S.*)")
_MY_SEC = re.compile(r"^([၀-၉]{1,3})\s*။\s*(.*)")
_NEW_PARA = re.compile(r"^(\(|\[|Explanation|Illustration|Provided|PART |CHAPTER |ORDER |SCHEDULE|THE \w+ SCHEDULE"
                       r"|အခန်း|အပိုင်း)")
_END = re.compile(r"[.;:—–\-။၊*]$")
_PAGE = re.compile(r"^Page \d+ of \d+$")

_lists: dict = {}
_cache: dict = {}


def _norm_id(id: str) -> str:
    s = unquote((id or "").strip())
    if "/uploads/legislative/" in s:
        s = s.split("/uploads/legislative/", 1)[1]
    if not s.lower().endswith(".pdf") or "/" in s or ".." in s or len(s) > 300:
        raise BadRequest("A law id is the PDF file name from search_legislation, e.g. "
                         "'1783905146-mm-6a543b7ad236b-THE-CODE-OF-CIVIL-PROCEDURE.pdf' (the full "
                         "unionsupremecourt.gov.mm/uploads/legislative/... link also works).")
    return s


def _pdf_url(lid: str) -> str:
    return FILES + quote(lid)


async def _list(kind: str) -> list[dict]:
    hit = _lists.get(kind)
    if hit and time.monotonic() - hit[0] < LIST_TTL:
        return hit[1]
    rows: list[dict] = []
    n = 1
    while n <= 10:
        url = BASE + LISTS[kind] + (f"?page={n}" if n > 1 else "")
        r = await _http.get(url)
        if r.status_code != 200:
            raise SourceError(_http.error(NAME, f"{LISTS[kind]} list failed", r.status_code), r.status_code)
        doc = lhtml.fromstring(r.text)
        for h in doc.xpath('//div[contains(@class, "portfolio-text")]/h3'):
            box = h.getparent()
            href = box.xpath('.//a[contains(@href, "/uploads/legislative/")]/@href')
            if not href:
                continue
            posted = re.search(r"\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4}", box.getparent().text_content())
            rows.append({"id": _norm_id(href[0]), "title": _http.clean(h.text_content()), "type": kind,
                         "posted": _http.iso_date(posted[0]) if posted else ""})
        if not doc.xpath(f'//a[contains(@href, "?page={n + 1}")]'):
            break
        n += 1
    _http.lru_put(_lists, kind, (time.monotonic(), rows), 8)
    return rows


async def _entry(lid: str) -> dict:
    for kind in LISTS:
        for row in await _list(kind):
            if row["id"] == lid:
                return row
    raise NotFound(f"'{lid}' is not in the Supreme Court's law lists. Use search_legislation for ids.")


def _usable(text: str) -> bool:
    """False for a text layer made with legacy Burmese fonts that lost its letters."""
    toks = re.findall(r"[က-ဿၐ-႟]+", text)
    my = sum(map(len, toks))
    lat = len(re.findall(r"[A-Za-z]", text))
    nonspace = len(re.sub(r"\s", "", text)) or 1
    if my + lat < 300 or (my + lat) / nonspace < 0.6:
        return False
    return not (my > lat and my / len(toks) < 2.5)


def _paras(lines: list[str]) -> list[str]:
    out: list[str] = []
    for ln in lines:
        starts = bool(_EN_SEC.match(ln) or _MY_SEC.match(ln) or _NEW_PARA.match(ln))
        if out and not starts and not _END.search(out[-1]):
            out[-1] += " " + ln
        else:
            out.append(ln)
    return out


def _sec(p: str):
    """(number, suffix, last number of a range, rest) for a section-start paragraph, else None."""
    m = _EN_SEC.match(p)
    if m:
        return int(m[1]), m[2], int(m[3] or m[1]), m[4]
    m = _MY_SEC.match(p)
    if m:
        n = int(m[1].translate(_MY_DIGITS))
        return n, "", n, m[2]
    return None


def _sections(paras: list[str]) -> list[tuple[int, str, str]]:
    """(paragraph index, label, heading) of the main run of sequential section numbers.

    Every "1." opens a candidate run (a table of contents, numbered illustrations, schedule
    rules); a number joins each run it continues (gaps up to 10 for omitted sections, out-of-order
    numbers are skipped). The longest run wins; on a tie the later one (the body after its TOC)."""
    runs: list[dict] = []
    for i, p in enumerate(paras):
        s = _sec(p)
        if not s:
            continue
        n, suf, end, rest = s
        entry = (i, f"{n}{suf}" if end == n else f"{n}-{end}", _http.clean(rest)[:90])
        for run in runs:
            if (n == run["last"] and suf and suf > run["sfx"]) or run["last"] < n <= run["last"] + 10:
                run["items"].append(entry)
                run["last"], run["sfx"] = end, suf
        if n == 1:
            runs.append({"items": [entry], "last": end, "sfx": suf})
    if not runs:
        return []
    return max(enumerate(runs), key=lambda kr: (len(kr[1]["items"]), kr[0]))[1]["items"]


async def _law(id: str) -> dict:
    lid = _norm_id(id)
    if lid in _cache:
        return _cache[lid]
    row = await _entry(lid)
    url = _pdf_url(lid)
    h = await _http.request("HEAD", url)
    if h.status_code == 404:
        raise NotFound(f"The Supreme Court site lists '{lid}' but the file is missing ({url}).")
    if h.status_code != 200:
        raise SourceError(_http.error(NAME, "PDF not available", h.status_code), h.status_code)
    size = int(h.headers.get("content-length") or 0)
    if size > MAX_PDF:
        raise SourceError(f"Error ({NAME}): PDF is {size // 1_000_000} MB, over the 40 MB cap. Open {url}.")
    r = await _http.get(url)
    if r.status_code != 200 or not r.content.startswith(b"%PDF") or len(r.content) > MAX_PDF:
        raise SourceError(_http.error(NAME, "PDF download failed", r.status_code), r.status_code)
    text = _http.pdf_text(r.content)
    if not _usable(text):
        raise SourceError(f"Error ({NAME}): this PDF's text layer is unreadable (scanned, or legacy "
                          f"Burmese font encoding). Open it directly: {url}")
    lines = text.split("\n")
    head = lines[0] if lines else ""
    lines = [ln for ln in lines if ln and not _PAGE.match(ln) and ln != head]
    paras = _paras([head] + lines)
    law = {"id": lid, "title": row["title"], "url": url, "type": row["type"], "posted": row["posted"],
           "paras": paras, "secs": _sections(paras)}
    return _http.lru_put(_cache, lid, law, 12)


def _label(p: str) -> str:
    s = _http.clean(p).translate(_MY_DIGITS).strip(" .:")
    s = re.sub(r"(?i)^(section|sec\.?|s\.|ပုဒ်မ|article|art\.?)\s*", "", s).strip(" .:။")
    if not re.fullmatch(r"\d{1,3}[A-Za-z]{0,2}(-\d{1,3})?", s):
        raise BadRequest(f"Provision '{p}' not understood. Use a section number: '5', 'section 35A' or '၅'.")
    return s.upper()


# --------------------------------------------------------------------------- case law (RCMS)

async def _rcms(path: str, body: dict) -> dict:
    r = await _http.post(RCMS_API + path, content=json.dumps(body, ensure_ascii=False).encode(),
                         headers={"Content-Type": "application/json"})
    if r.status_code != 200 or "json" not in r.headers.get("content-type", ""):
        raise SourceError(_http.error(RCMS_NAME, f"{path.split('/')[0]} failed", r.status_code), r.status_code)
    return r.json()


def _plain(html: str) -> str:
    return _http.clean(lhtml.fromstring(f"<div>{html}</div>").text_content()) if html else ""


def _parts(src: dict) -> tuple[str, str]:
    """(parties, headnote) from precedent_name, usually '<p>A</p><p>နှင့်</p><p>B *</p>headnote'.

    The headnote is the text outside the <p>s, else the paragraphs after the last one carrying the
    report's footnote star (a following '( ... )' still describes a party)."""
    doc = lhtml.fromstring(f"<div>{src.get('precedent_name') or ''}</div>")
    paras = []
    for p in doc.xpath("./p"):
        t = _http.clean(p.text_content())
        if t and not re.fullmatch(r"[-–—_\s]+", t):
            paras.append(t)
        p.drop_tree()
    head = _http.clean(doc.text_content())
    if not head and len(paras) > 1:
        stars = [i for i, t in enumerate(paras) if "*" in t]
        cut = stars[-1] + 1 if stars else len(paras) - 1
        while cut < len(paras) - 1 and paras[cut].startswith("("):
            cut += 1
        paras, head = paras[:cut], " ".join(paras[cut:])
    return _http.clean(" ".join(paras).replace("*", "")), head


def _hit(src: dict) -> DecisionHit:
    parties, head = _parts(src)
    if not parties:  # English reports (1930s-40s): 'A v. B.* Headnote--...'
        m = re.match(r"(.{3,200}?\sv\.?\s.{2,200}?)\.?\s*\*", head, re.I)
        parties = m[1] if m else ""
    no = _http.clean(_plain(src.get("precedent_no")).replace("*", "")).rstrip(" ။")
    court = _plain(src.get("court"))
    court = court if re.search(r"\w", court) else ""
    return DecisionHit(id=str(src["id"]), title=parties or f"{court or 'Case'} {no}".strip(), court=court,
                       date=_http.iso_date(src.get("published_date")), case_number=no,
                       snippet=head[:300], url=RCMS_PAGE + str(src["id"]))


def _pid(id: str) -> str:
    s = (id or "").strip().rstrip("/")
    if "/precedentDetail" in s:
        s = s.rsplit("/", 1)[-1]
    if not re.fullmatch(r"\d{1,15}", s):
        raise BadRequest("A Myanmar ruling id is RCMS's numeric precedent id from search_caselaw, e.g. "
                         "'1571733531' (the rcms.usc.gov.mm/precedentDetail/... link also works).")
    return s


def _words(q: str) -> str:
    """Each word as *word* (substring), Elasticsearch special characters removed."""
    ws = [re.sub(r'[\\+\-=&|><!(){}\[\]^"~*?:/.,၊။]', "", w).lower() for w in _http.clean(q).split()]
    return " ".join(f"*{w}*" for w in ws if w)


class Myanmar(Jurisdiction):
    code = "mm"
    name = "Myanmar"
    languages = ("my", "en")
    aliases = ("myanmar", "burma", "mmr", "မြန်မာ")
    sources = (
        Source(
            name="Supreme Court of the Union: laws, procedures and amending laws (unionsupremecourt.gov.mm)",
            url=BASE + "laws",
            covers=("legislation",),
            licence="No terms of use published; footer 'Copyright © 2020 Supreme Court of the Union. "
                    "All Rights Reserved.'",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~40 requests (2026-11)",
            terms_url=BASE,
            warning="Text extracted from PDFs; many Burmese PDFs use legacy fonts, so letters can be "
                    "substituted or out of order. Check the PDF before quoting.",
        ),
        Source(
            name="Supreme Court of the Union: Rulings and Case Management System (rcms.usc.gov.mm)",
            url=f"https://{RCMS}/precedents",
            covers=("caselaw",),
            licence="No terms of use published; footer 'Copyright © 2020 - The Supreme Court of The "
                    "Union. All Rights Reserved.'",
            commercial_use=None,
            ai_use=None,
            auth="none (public JSON API behind the site's JavaScript app)",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~25 requests (2026-11)",
            terms_url=f"https://{RCMS}/",
        ),
    )
    caselaw_filters = {"type": "criminal, civil or writ (စာချွန်တော်, incl. Letters Patent Appeals)",
                       "year": "year of the ruling, e.g. 2012",
                       "date_from": "earliest ruling date, YYYY-MM-DD",
                       "date_to": "latest ruling date, YYYY-MM-DD"}
    legislation_filters = {"type": "law, procedure or amendment"}
    min_interval = {HOST: 1.0, RCMS: 1.0}
    notes = ("Case law: ~6,900 law-report rulings (Supreme Court and predecessors, 1920s to 2022; "
             "English before independence, Burmese after) as Unicode text, from the court's RCMS. Needs the OS certificate store: unreachable on "
             "Linux (incomplete TLS chain). Laws: a small selection (~30) of laws, court procedures and "
             "amending laws posted by the Supreme Court, incl. the Code of Civil Procedure and Code of "
             "Criminal Procedure in English. No full statute book is reachable (MLIS offline, Hluttaw "
             "JavaScript-only).")
    gaps = (
        "Full statute book (Myanmar Law Information System, mlis.gov.mm): site down / unreachable"
         " (timeout, 2026-11-06)",
        "Parliament laws (pyidaungsu.hluttaw.mm): JavaScript-only site with no server-rendered "
         "content; not built",
        ("Rulings after Dec 2022: none published; the court's own law-report list "
         "(unionsupremecourt.gov.mm/ruling) ends with the 2022 volume and RCMS likewise (checked 2026-11-10)"),
        ("Unreported Supreme Court commercial judgments (Commercial Judgment System, cjs.usc.gov.mm: 148 "
         "of ~316, up to 2026): recent ones scans only, older text garbled (checked 2026-11-10); not built"),
        "Burmese laws in legacy-font PDFs: broken text layer, refused (no usable text)",
        "Case law on Linux: rcms.usc.gov.mm sends an incomplete TLS chain; works only via the "
         "macOS/Windows trust store",
    )
    samples = {
        "caselaw_query": "ပဋိညာဉ်",
        "decision_id": "1571733531",
        "legislation_query": "procedure",
        "law_id": "1783905146-mm-6a543b7ad236b-THE-CODE-OF-CIVIL-PROCEDURE.pdf",
        "provision": "9",
    }

    async def search_caselaw(self, query, *, limit, page, filters):
        f = filters or {}
        must: list[dict] = []
        if f.get("type"):
            t = f["type"].strip().lower()
            if t not in CASE_TYPES:
                raise BadRequest("type must be one of: " + ", ".join(CASE_TYPES) + ".")
            must.append({"match": {"precedent_type": CASE_TYPES[t]}})
        lo, hi = f.get("date_from", ""), f.get("date_to", "")
        if f.get("year"):
            y = str(f["year"]).strip().translate(_MY_DIGITS)
            if not re.fullmatch(r"\d{4}", y):
                raise BadRequest("year is four digits, e.g. 2012.")
            lo, hi = max(lo, f"{y}-01-01"), min(hi or "9999", f"{y}-12-31")
        for k, v in (("gte", lo), ("lte", hi)):
            if v:
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
                    raise BadRequest("date_from / date_to look like 2012-01-31.")
                must.append({"range": {"published_date": {k: v}}})
        q = {"bool": {"must": must}}
        words = _words(query)
        if words:
            q["bool"]["should"] = [
                {"query_string": {"query": words, "default_operator": "AND", "fields": RCMS_FIELDS}},
                {"has_child": {"type": "detail", "query": {"query_string": {
                    "query": words, "default_operator": "AND", "default_field": "detail"}}}}]
            q["bool"]["minimum_should_match"] = 1
        body = {"query": q, "sort": [{"published_date": "desc"}, {"start_page": "asc"}]}
        limit = max(1, int(limit))
        start = (max(1, int(page)) - 1) * limit
        hits, total = [], None
        for p in range(start // 10 + 1, (start + limit - 1) // 10 + 2):
            data = await _rcms(f"searchPrecedent/{p}/", body)
            total = data.get("total", 0)
            res = data.get("results") or []
            hits += [(p, i, r["_source"]) for i, r in enumerate(res)]
            if len(res) < 10 or p >= (data.get("total_pages") or 0):
                break
        items = [_hit(src) for p, i, src in hits if start <= (p - 1) * 10 + i < start + limit]
        note = ("Law reports, 1920s-2022 (English before independence, Burmese after); the court "
                            "has published no law reports after 2022. Each word matches as a substring of the title, headnote, case number "
                            "or full text.")
        if not total and words and not re.search(r"[\u1000-\u109F]", query):
            note += (" No match for this English query. Rulings after independence (1948) are written in Burmese "
                     "and English words do not match them, and only older rulings are in English, so a date, "
                     "year or type filter (e.g. writ) can leave no English text; retry the query in Burmese "
                     "(e.g. အာမခံ for bail, စာချုပ် for contract) or without the filter.")
        return Results(items=items, total=total, note=note)

    async def get_decision(self, id):
        pid = _pid(id)
        data = await _rcms("getPrecedent/", {"query": {"match": {"id": pid}}})
        src = next((r["_source"] for r in data.get("results") or [] if str(r["_source"].get("id")) == pid), None)
        if not src:
            raise NotFound(f"No ruling '{pid}' in the Supreme Court's RCMS. Use search_caselaw for ids.")
        det = await _rcms("getPrecedentDetail/", {
            "searchBody": {"size": 1000, "query": {"parent_id": {"type": "detail", "id": pid}},
                           "sort": [{"id": "asc"}]}, "searchKey": "null"})
        text = _http.html_to_md("".join(r["_source"].get("detail") or "" for r in det.get("results") or []))
        if not text:
            raise SourceError(f"Error ({RCMS_NAME}): ruling {pid} has no text on RCMS. "
                              f"Open {RCMS_PAGE + pid}.")
        h = _hit(src)
        meta = {k: v for k, v in (
            ("Type", _plain(src.get("precedent_type"))),
            ("Proceeding", _plain(src.get("precedent_sub_type"))),
            ("Judge", _plain(src.get("judge"))),
            ("Against", _plain(src.get("additional"))),
            ("Law report", f"{_plain(src.get('precedent_year'))}, pp. {src.get('start_page')}-{src.get('end_page')}"
             if src.get("start_page") else ""),
            ("PDF", RCMS_PDF + pid if src.get("download") else "")) if v}
        return Decision(id=pid, title=h.title, text=text, url=h.url, court=h.court, date=h.date,
                        case_number=h.case_number, summary=_parts(src)[1], metadata=meta)

    async def search_legislation(self, query, *, limit, page, filters):
        f = filters or {}
        kinds = list(LISTS)
        if f.get("type"):
            t = f["type"].strip().lower().rstrip("s")
            if t not in LISTS:
                raise BadRequest("type must be one of: " + ", ".join(LISTS) + ".")
            kinds = [t]
        words = [w for w in _http.clean(query).lower().split() if w]
        rows = []
        for k in kinds:
            for row in await _list(k):
                hay = (row["title"] + " " + row["id"].replace("-", " ").replace("_", " ") + " " + k).lower()
                if all(w in hay for w in words):
                    rows.append(row)
        limit = max(1, int(limit))
        start = (max(1, int(page)) - 1) * limit
        items = [LawHit(id=r["id"], title=r["title"], type=TYPE_NAMES[r["type"]],
                        snippet=f"Posted on the Supreme Court site {r['posted']}" if r["posted"] else "",
                        url=_pdf_url(r["id"])) for r in rows[start:start + limit]]
        return Results(items=items, total=len(rows),
                       note="Matches the title (mostly Burmese), the English words in the file name or the type word "
                            "(law, procedure, amendment); a blank query with the type filter lists a type; "
                            "the whole collection is ~30 documents posted by the Supreme Court. The "
                            "Constitution, the Penal Code and most other statutes are NOT in it, so "
                            "0 results does not mean the law does not exist.")

    async def get_legislation_text(self, id):
        law = await _law(id)
        return LawText(id=law["id"], title=law["title"], text="\n\n".join(law["paras"]), url=law["url"],
                       metadata={"type": TYPE_NAMES[law["type"]], "posted": law["posted"]})

    async def get_legislation_toc(self, id):
        law = await _law(id)
        if len(law["secs"]) < 2:
            raise NotFound(f"No section structure found in '{law['id']}'. Use get_legislation_text.")
        entries = [TocEntry(title=f"Section {lab} – {head}", level=0, provision=lab)
                   for _, lab, head in law["secs"]]
        return Toc(id=law["id"], title=law["title"], url=law["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        want = _label(provision)
        law = await _law(id)
        secs = law["secs"]
        for k, (i, lab, _) in enumerate(secs):
            if lab == want or (lab.split("-")[0] == want):
                end = secs[k + 1][0] if k + 1 < len(secs) else len(law["paras"])
                body = law["paras"][i:end]
                # drop the next section's marginal heading (short line ending in '.')
                if k + 1 < len(secs) and len(body) > 1 and len(body[-1]) < 80 and body[-1].endswith(".") \
                        and not _sec(body[-1]):
                    body = body[:-1]
                return Provision(law_id=law["id"], law_title=law["title"], provision=lab,
                                 text="\n\n".join(body), url=law["url"])
        raise NotFound(f"No section {want} in '{law['id']}'. Labels look like '5', 'section 35A' or '၅'.")
