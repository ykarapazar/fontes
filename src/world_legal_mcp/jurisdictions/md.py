"""Moldova: case law from the Supreme Court of Justice (jurisprudenta.csj.md) and from the
courts of appeal and district courts (Portalul Național al Instanțelor de Judecată,
instante.justice.md). Legislation: the Constitution only (the Presidency's official
consolidated PDF, presedinte.md).

What is not here, and why (checked 2026-11-06 / 2026-11-10 from a UK IP):
  * Laws: legis.md (Registrul de stat al actelor juridice) and parlament.md answer every
    request, robots.txt included, with a Cloudflare "Just a moment..." managed challenge
    (HTTP 403). A bot challenge means we do not use them. monitorul.gov.md (Monitorul
    Oficial, Moldpres) shows only issue tables of contents for free; the texts need a paid
    subscription and its terms forbid copying and redistribution. lex.justice.md (old
    register) does not answer.
  * cauta.csj.md (CSJ analytic search) did not answer.

Gotchas this code encodes:
  * CSJ: each college is a separate jqGrid JSON endpoint (col_civil_grid.php,
    col_penal_grid.php) with its own column names; the decision itself is a PDF at
    search_col_<college>.php?id=N. Ids are per college, so our id is '<college>/<N>'.
    `records` in the grid reply is the unfiltered count, so Results.total is None.
    An unknown id still returns HTTP 200 'application/pdf' with the text
    "Couldn't retrieve array data."
  * instante.justice.md: a Drupal view, 10 rows per page (`page` is 0-based), results
    table with a PDF link `pigd_integration/pdf/<GUID>`; the GUID is our id. An unknown
    GUID returns an empty 200 PDF. robots.txt asks for Crawl-delay: 10.
  * Dates in the lower-court table are not zero-padded ('2024-04-9').
  * Decisions are anonymised by the courts with '*****'.
  * Constitution PDF (presedinte.md/app/webroot/Constitutia_RM/Constitutia_2024_ro.pdf):
    running header 'CONSTITUŢIA REPUBLICII MOLDOV A' + page number on every page; the
    superscript of inserted articles is flattened ('Articolul 591' is 59^1; no article
    number is above 143); one heading is misspelt 'Artcolul 52'; words are hyphenated
    across lines, sometimes as 'indepen -'.
"""
from __future__ import annotations

import json
import re
import unicodedata
from datetime import date
from urllib.parse import parse_qs, urlencode, urlsplit

from lxml import html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc, TocEntry

CSJ = "https://jurisprudenta.csj.md/"
INST = "https://instante.justice.md"
INST_LIST = INST + "/ro/hotaririle-instantei"
INST_PDF = INST + "/ro/pigd_integration/pdf/{id}"
CSJ_NAME = "Curtea Supremă de Justiție"
CONST_PAGE = "https://presedinte.md/rom/constitutia-republicii-moldova"
CONST_PDF = "https://presedinte.md/app/webroot/Constitutia_RM/Constitutia_2024_ro.pdf"
CONST_ID = "constitutia"
CONST_TITLE = "Constituția Republicii Moldova (29 iulie 1994, republicată)"

# college -> (grid endpoint, PDF page, date column, [(field, label)] after number+date)
_COLLEGES = {
    "civil": ("col_civil_grid.php", "search_col_civil.php", "data_examinare",
              "Colegiul civil, comercial și de contencios administrativ",
              ("partile_dosar", "obiectul_litigiului", "problema_juridica", "procedura_examinare")),
    "penal": ("col_penal_grid.php", "search_col_penal.php", "data_pronuntare",
              "Colegiul penal",
              ("partea_dosar", "infractiunea_crime", "art_cp_cpp", "procedura_examinare")),
}
# instante.justice.md "Instanțe judecătorești" option values (2026-11)
_INSTANCES = {
    "1": "Circumscripția Centru", "2": "Curtea de Apel Centru", "3": "Judecătoria Chișinău",
    "4": "Judecătoria Criuleni", "5": "Judecătoria Hîncești", "6": "Judecătoria Strășeni",
    "7": "Judecătoria Căușeni", "8": "Circumscripția Nord", "9": "Curtea de Apel Nord",
    "10": "Judecătoria Bălți", "11": "Judecătoria Drochia", "12": "Judecătoria Edineț",
    "13": "Judecătoria Orhei", "14": "Judecătoria Soroca", "15": "Judecătoria Ungheni",
    "16": "Circumscripția Sud", "17": "Curtea de Apel Sud, sediul Cahul",
    "19": "Curtea de Apel Sud, sediul Comrat", "20": "Judecătoria Cahul",
    "21": "Judecătoria Comrat", "22": "Judecătoria Cimișlia",
}
_CASE_TYPES = {"civil": "1", "contraventional": "2", "penal": "3"}
_MONTHS = {"ianuarie": 1, "februarie": 2, "martie": 3, "aprilie": 4, "mai": 5, "iunie": 6,
           "iulie": 7, "august": 8, "septembrie": 9, "octombrie": 10, "noiembrie": 11,
           "decembrie": 12}
_GUID = re.compile(r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}")
_LOWER_PAGE = 10

_clean = _http.clean


def _fold(s: str) -> str:
    """Lower-case, no diacritics, ş/ţ cedilla and comma forms alike: for name matching."""
    s = unicodedata.normalize("NFKD", _clean(s).lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def _ymd(s: str) -> str:
    """'2024-04-9' -> '2024-04-09'; else ''."""
    m = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", _clean(s))
    return f"{m[1]}-{int(m[2]):02d}-{int(m[3]):02d}" if m else ""


_FUTURE = "future"


def _ro_date(s: str) -> str:
    """First line that starts with a date like '18 martie 2026' -> '2026-03-18'; else ''.
    (Dates inside sentences in the heading are usually the lower court's.)"""
    d = r"(\d{1,2})\s+([a-zăâîșşțţ]+)\s+(\d{4})"
    for pat in (r"(?m)^" + d + r"\b", d + r"\s+textul corespunde"):  # 2nd: reflowed pages
        for m in re.finditer(pat, (s or "").lower()):
            if m[2] in _MONTHS:
                return f"{m[3]}-{_MONTHS[m[2]]:02d}-{int(m[1]):02d}"
    return ""


def _parse_id(raw: str) -> tuple[str, str]:
    """-> ('csj', 'civil/82623') or ('lower', GUID). Accepts the source URLs too."""
    s = _clean(raw)
    m = re.search(r"search_col_(civil|penal)\.php\?id=(\d+)", s)
    if m:
        return "csj", f"{m[1]}/{m[2]}"
    m = re.fullmatch(r"(civil|penal)/(\d{1,9})", s.lower())
    if m:
        return "csj", f"{m[1]}/{m[2]}"
    m = _GUID.search(s)
    if m and (s == m[0] or "pigd_integration/pdf/" in s):
        return "lower", m[0].upper()
    raise BadRequest("Moldovan decision ids are 'civil/82623' or 'penal/27675' (Supreme Court, "
                     "college/id) or a GUID like '7FEA82B5-B40F-4342-8EE5-02ED9DB73FA6' "
                     f"(instante.justice.md PDF id), got {raw!r}")


def _instance(v: str) -> str:
    v = _clean(v)
    if v in _INSTANCES:
        return v
    hits = [k for k, name in _INSTANCES.items() if _fold(v) and _fold(v) in _fold(name)]
    if len(hits) == 1:
        return hits[0]
    exact = [k for k in hits if _fold(_INSTANCES[k]) == _fold(v)]
    if len(exact) == 1:
        return exact[0]
    raise BadRequest(f"instance must name one court, e.g. 'Judecătoria Chișinău' or "
                     f"'Curtea de Apel Nord' (one of: {', '.join(_INSTANCES.values())}), got {v!r}")


def _iso_filter(filters, key) -> str:
    v = _clean(filters.get(key))
    if v:
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
                raise ValueError
            date.fromisoformat(v)
        except ValueError:
            raise BadRequest(f"{key} must be a real date, YYYY-MM-DD, got {v!r}") from None
    return v


async def _pdf(url: str, what: str) -> str:
    r = await _http.get(url)
    if r.status_code != 200:
        raise SourceError(_http.error(urlsplit(url).hostname, what, r.status_code), r.status_code)
    if not r.content.startswith(b"%PDF"):
        raise NotFound(f"No decision {what} at the source.")
    text = _reflow(_http.pdf_text(r.content))
    if not text:
        raise SourceError(f"{what} is a scanned PDF with no text layer (no OCR here); "
                          f"open it at {url}")
    return text


def _reflow(text: str) -> str:
    """Some CSJ PDFs extract one word per line; join those pages back into running text."""
    pages = []
    for pg in text.split("\n\n"):
        lines = pg.splitlines()
        if len(lines) > 20 and sum(" " not in ln for ln in lines) > 0.8 * len(lines):
            pg = _clean(" ".join(lines))
        pages.append(pg)
    return "\n\n".join(pages)


def _head(text: str) -> tuple[str, str]:
    """(case number, decision date) from the first lines of a Moldovan decision."""
    head = "\n".join(text.splitlines()[:40])
    m = re.search(r"Dosarul\s+nr\.?\s*([0-9][\w\-/]*)", head)
    return (m[1] if m else ""), _ro_date(head)


class Moldova(Jurisdiction):
    code = "md"
    name = "Moldova"
    languages = ("ro",)
    aliases = ("moldova", "republica moldova", "mda")
    sources = (
        Source(
            name="Curtea Supremă de Justiție (Supreme Court of Justice), jurisprudenta.csj.md",
            url=CSJ,
            covers=("caselaw",),
            licence=("unknown: no terms page on csj.md or jurisprudenta.csj.md; published "
                     "under CSM Regulation 472/21 (2008), 'accesul ... este gratuit'"),
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit=("unknown; no robots.txt on jurisprudenta.csj.md (404), www.csj.md asks "
                        "Crawl-delay 10; 2 s spacing, no 429 in ~12 requests (2026-11-06)"),
            terms_url="https://www.csj.md/",
        ),
        Source(
            name="Președinția Republicii Moldova: Constituția (consolidated PDF), presedinte.md",
            url=CONST_PAGE,
            covers=("legislation",),
            licence=("no terms page on presedinte.md; official texts (acte normative) are "
                     "excluded from copyright, Legea 139/2010 art. 7"),
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit=("unknown; robots.txt 'Allow: /'; one PDF per session (cached), "
                        "1 s spacing (2026-11-10)"),
            terms_url=CONST_PAGE,
        ),
        Source(
            name="Portalul Național al Instanțelor de Judecată (courts of appeal and district "
                 "courts), instante.justice.md",
            url=INST_LIST,
            covers=("caselaw",),
            licence=("unknown: no terms page on instante.justice.md; published under CSM "
                     "Regulation 472/21 (2008), 'accesul ... este gratuit'"),
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit=("robots.txt Crawl-delay: 10 (honoured: 10 s spacing); no 429 in "
                        "~6 requests (2026-11-06)"),
            terms_url=INST,
        ),
    )
    caselaw_filters = {
        "court": "'csj' (Supreme Court, default) or 'lower' (courts of appeal and district "
                 "courts on instante.justice.md; slow: 10 s per request)",
        "college": "csj only: 'civil' (civil, commercial and administrative; default) or 'penal'",
        "date_from": "csj only: decision date from, YYYY-MM-DD",
        "date_to": "csj only: decision date to, YYYY-MM-DD",
        "parties": "words in the parties / case name",
        "legal_issue": "csj only: words in the legal issue ('problema de drept'; penal: articles, "
                       "e.g. 'art. 186')",
        "case_number": "case number, e.g. '2ra-80/25' (csj) or '1-23098994-26-1-10072023' (lower)",
        "case_type": "lower only: 'civil', 'contraventional' or 'penal'",
        "instance": "lower only: one court, e.g. 'Judecătoria Chișinău', 'Curtea de Apel Nord'",
    }
    min_interval = {"jurisprudenta.csj.md": 2.0, "instante.justice.md": 10.0,
                    "presedinte.md": 1.0}
    notes = ("In Romanian. Supreme Court (CSJ) decisions searchable by subject and legal issue; "
             "lower courts searchable by topic, parties, court. Full texts are PDFs (text layer). "
             "Legislation: the Constitution only (consolidated to 20.10.2024, by article); "
             "laws sit behind a Cloudflare bot challenge (legis.md).")
    gaps = (
        "Laws and codes (legis.md, State Register of Legal Acts; parlament.md): Cloudflare bot "
         "check blocks our client (403, 2026-11-06, re-checked 2026-11-10)",
        "Monitorul Oficial (monitorul.gov.md): texts behind a paid subscription; terms forbid "
         "copying and redistribution",
        "CSJ analytic search (cauta.csj.md): site down / unreachable (no answer, 2026-11-06)",
        "Constitutional Court decisions: not researched yet",
    )
    samples = {
        "caselaw_query": "uzucapiune",
        "decision_id": "civil/82623",
        "legislation_query": "Constituția",
        "law_id": CONST_ID,
        "provision": "Articolul 20",
    }

    # ------------------------------------------------------------------ search
    async def search_caselaw(self, query, *, limit, page, filters):
        court = _clean(filters.get("court") or "csj").lower()
        if court not in ("csj", "lower"):
            raise BadRequest(f"court must be 'csj' or 'lower', got {court!r}")
        limit = max(1, min(int(limit), 50))
        page = max(1, int(page))
        if court == "csj":
            for k in ("case_type", "instance"):
                if filters.get(k):
                    raise BadRequest(f"filter {k!r} is for court='lower' only")
            return await self._search_csj(_clean(query), limit, page, filters)
        for k in ("college", "date_from", "date_to"):
            if filters.get(k):
                why = (" (the lower-court portal has no date search: leave the date out and read "
                       "the Date of each hit)" if k != "college" else "")
                raise BadRequest(f"filter {k!r} is for court='csj' only{why}")
        return await self._search_lower(_clean(query), min(limit, _LOWER_PAGE), page, filters)

    async def _search_csj(self, q, limit, page, filters):
        college = _clean(filters.get("college") or "civil").lower()
        if college not in _COLLEGES:
            raise BadRequest(f"college must be 'civil' or 'penal', got {college!r}")
        grid, _, date_col, _, cols = _COLLEGES[college]
        # The grid takes one flat list of rules (nested groups are ignored): all must match.
        rules = [{"field": field, "op": "cn", "data": v} for field, v in (
            (cols[1], q), (cols[0], _clean(filters.get("parties"))),
            (cols[2], _clean(filters.get("legal_issue"))),
            ("nr_dosar", _clean(filters.get("case_number")))) if v]
        for key, op in (("date_from", "ge"), ("date_to", "le")):
            if _iso_filter(filters, key):
                rules.append({"field": date_col, "op": op, "data": _clean(filters[key])})
        if not rules and not filters.get("college"):
            raise BadRequest("Give words to search for in the subject, or a filter.")
        flt = {"groupOp": "AND", "rules": rules}
        form = {"_search": "true", "rows": str(limit), "page": str(page), "sidx": date_col,
                "sord": "desc", "filters": json.dumps(flt, ensure_ascii=False)}
        if not rules:  # the grid answers an empty rule list with a non-JSON page
            form.update(_search="false", filters="")
        r = await _http.post(CSJ + grid, data=form)
        if r.status_code != 200:
            raise SourceError(_http.error("jurisprudenta.csj.md", "search failed", r.status_code),
                              r.status_code)
        try:
            data = r.json()
        except ValueError:
            raise SourceError("jurisprudenta.csj.md: search returned no JSON", r.status_code)
        rows = data.get("rows") or []
        if int(data.get("page") or page) < page:
            rows = []  # jqGrid clamps a page past the end to the last page
        court = f"{CSJ_NAME}, {_COLLEGES[college][3]}"
        items = []
        for row in rows[:limit]:
            c = [_clean(x) for x in row["cell"]]
            number, date, parties, subject, issue, procedure = c[1:7]
            items.append(DecisionHit(
                id=f"{college}/{row['id']}", title=f"CSJ {number}: {parties}" if parties else f"CSJ {number}",
                court=court, date=_ymd(date), case_number=number,
                snippet=" | ".join(x for x in (subject, issue, procedure) if x)[:400],
                url=f"{CSJ}{_COLLEGES[college][1]}?id={row['id']}"))
        note = (f"CSJ {college} college, newest first; the query matches the subject field "
                "(substring, all filters AND). Use college='penal' for criminal cases.")
        if not items and page == 1:
            return Results(items, total=0, note=(
                note + " No decisions match: the search only looks at the subject field, so "
                "try fewer or other words (e.g. 'locațiune' or 'reziliere' alone)."))
        return Results(items, total=None, note=note)

    async def _search_lower(self, q, limit, page, filters):
        params = {"Instance": "All", "Numarul_dosarului": _clean(filters.get("case_number")),
                  "Denumirea_dosarului": _clean(filters.get("parties")), "date": "",
                  "Tematica_dosarului": q, "Tipul_dosarului": "All"}
        if filters.get("instance"):
            params["Instance"] = _instance(filters["instance"])
        ct = _fold(filters.get("case_type") or "")
        if ct:
            if ct not in _CASE_TYPES:
                raise BadRequest(f"case_type must be one of {', '.join(_CASE_TYPES)}, got {ct!r}")
            params["Tipul_dosarului"] = _CASE_TYPES[ct]
        if not (q or params["Numarul_dosarului"] or params["Denumirea_dosarului"]
                or params["Instance"] != "All" or ct):
            raise BadRequest("Give words for the case topic (e.g. 'furt'), or a filter.")
        start = (page - 1) * limit  # the site pages by 10; at most two site pages per call
        first, rows, total = start // _LOWER_PAGE, [], None
        for site_page in range(first, (start + limit - 1) // _LOWER_PAGE + 1):
            got, total = await self._lower_page({**params, "page": str(site_page)})
            rows += got
            if len(got) < _LOWER_PAGE:
                break
        skip = start - first * _LOWER_PAGE
        items = rows[skip:skip + limit]
        for it in items:
            if it.date == _FUTURE:  # read the real date from the PDF instead
                try:
                    it.date = _head(await _pdf(it.url, it.id))[1]
                except Exception:
                    it.date = ""
        return Results(items, total=total, note=(
            "Courts of appeal and district courts, as listed by instante.justice.md; the query "
            "matches the case topic field (e.g. 'furt', 'divorț'). No date filter exists for these "
            "courts; read each hit's Date. When the portal lists no date or one in the "
            "future (a typo on its side), the date is read from the decision PDF; if that fails "
            "it is blank, so check get_decision before citing. The 'Case number' shown here is the "
            "portal's internal number; the official number to cite (e.g. 2-61/2025) is in the "
            "title and first lines of get_decision. 10 s between requests."))

    async def _lower_page(self, params):
        url = INST_LIST + "?" + urlencode(params)
        r = await _http.get(url)
        if r.status_code != 200:
            raise SourceError(_http.error("instante.justice.md", "search failed", r.status_code),
                              r.status_code)
        doc = lhtml.fromstring(r.text)
        m = re.search(r"Rezultate:\s*<b>(\d+)</b>", r.text)
        total = int(m[1]) if m else 0
        items = []
        for tr in doc.xpath('//table[contains(@class,"views-table")]/tbody/tr'):
            cell = {td.get("class", "").split()[-1]: td for td in tr.xpath("./td")}
            def f(name):
                return _clean(_http.text(cell[name])) if name in cell else ""
            href = (cell["views-field-nothing"].xpath(".//a/@href") or [""])[0] \
                if "views-field-nothing" in cell else ""
            g = _GUID.search(href)
            if not g:
                continue
            dt = _ymd(f("views-field-solr-document-1"))
            if dt > date.today().isoformat():
                dt = _FUTURE  # the portal sometimes lists a date in the future: not a decision date
            court, number = f("views-field-solr-document-5"), f("views-field-Numarul-dosarului")
            name, topic = f("views-field-Denumirea-dosarului"), f("views-field-Tematica-dosarului")
            items.append(DecisionHit(
                id=g[0].upper(), title=f"{court} {number}: {name}"[:300],
                court=court, date=dt, case_number=number,
                snippet=" | ".join(x for x in (f("views-field-Tipul-dosarului"), topic,
                                               "judge " + f("views-field-solr-document-3")) if x)[:400],
                url=INST_PDF.format(id=g[0].upper())))
        return items, total

    # ------------------------------------------------------------------ decision
    async def get_decision(self, id):
        kind, did = _parse_id(id)
        if kind == "csj":
            college, n = did.split("/")
            url = f"{CSJ}{_COLLEGES[college][1]}?id={n}"
            court = f"{CSJ_NAME}, {_COLLEGES[college][3]}"
        else:
            url, court = INST_PDF.format(id=did), ""
        text = await _pdf(url, did)
        number, date = _head(text)
        prefix = "CSJ" if kind == "csj" else "Dosarul nr."
        title = f"{prefix} {number}" if number else (f"CSJ {did}" if kind == "csj" else f"Decizie {did}")
        meta = {"Sursa": "PDF; date and case number read from its first lines"}
        if kind == "lower" and "(dispozitiv)" in text[:600] and len(text) < 4000:
            meta["Notă"] = ("Only the operative part (dispozitiv) is published for this "
                            "decision; the reasons are not available at the source.")
        return Decision(id=did, title=title, text=text, url=url, court=court, date=date,
                        case_number=number, metadata=meta)

    # ------------------------------------------------------------------ constitution
    async def search_legislation(self, query, *, limit, page, filters):
        q = _fold(query)
        art = await _constitution()
        snippet = ""
        if q and not any(w in q for w in ("constitu", "конституц")):
            words = q.split()
            hit = next((a for a in art["articles"] if all(w in _fold(a[2]) for w in words)), None)
            if not hit:
                return Results([], total=0, note=_CONST_NOTE)
            snippet = f"Articolul {hit[0]}: {_clean(hit[2])[:300]}"
        items = [] if page > 1 else [LawHit(
            id=CONST_ID, title=CONST_TITLE, type="Constituție", date="1994-07-29",
            status="în vigoare (text consolidat la 20.10.2024)", snippet=snippet, url=CONST_PDF)]
        return Results(items, total=1, note=_CONST_NOTE)

    async def get_legislation_toc(self, id):
        art = await _constitution(id)
        return Toc(id=CONST_ID, title=CONST_TITLE, url=CONST_PDF, entries=art["toc"])

    async def get_legislation_provision(self, id, provision):
        art = await _constitution(id)
        label = _art_label(provision)
        for lab, head, body in art["articles"]:
            if lab == label:
                return Provision(law_id=CONST_ID, law_title=CONST_TITLE,
                                 provision=f"Articolul {lab}", text=f"**Articolul {lab}**\n\n{body}",
                                 url=CONST_PDF, as_of="2024-10-20")
        raise NotFound(f"No article {provision!r} in the Constitution; labels look like "
                       "'Articolul 20', '59^1' or 'Articolul II' (final provisions).")

    async def get_legislation_text(self, id):
        art = await _constitution(id)
        return LawText(id=CONST_ID, title=CONST_TITLE, text=art["text"], url=CONST_PDF,
                       as_of="2024-10-20",
                       metadata={"Sursa": "Președinția Republicii Moldova, PDF oficial (Moldpres 2024)",
                                 "Pagina": CONST_PAGE})


_CONST_NOTE = ("Only the Constitution is available for Moldova; laws and codes are on legis.md, "
               "which blocks automated clients.")
_const_cache: dict = {}
_ART_RE = re.compile(r"^Art(?:i)?colul\s+([0-9]+|[IVX]+)\b\s*(.*)$")
_HEAD_RE = re.compile(r"^(Titlul|Capitolul|Sec[tţț]iunea)\b")


def _sup(num: str) -> str:
    """'591' -> '59^1' (inserted articles: no Moldovan article number exceeds 143)."""
    return f"{num[:-1]}^{num[-1]}" if num.isdigit() and int(num) > 143 else num


def _art_label(raw: str) -> str:
    s = _clean(raw).replace("¹", "^1").replace("²", "^2").replace("³", "^3")
    s = re.sub(r"(?i)^(articolul|art\.?|article)\s*", "", s).strip()
    m = re.fullmatch(r"(\d{1,3})\s*(?:\^|-|/|\.)\s*(\d)", s)
    if m:
        return f"{m[1]}^{m[2]}"
    if re.fullmatch(r"\d{1,4}", s):
        return _sup(str(int(s)))
    if re.fullmatch(r"(?i)[IVX]+", s):
        return s.upper()
    raise BadRequest(f"Article labels look like 'Articolul 20', '59^1' or 'II', got {raw!r}")


def _join(lines: list[str]) -> str:
    """Re-flow PDF lines into paragraphs: a paragraph starts with '(n)' or 'a)'."""
    paras: list[str] = []
    for ln in lines:
        if paras and not re.match(r"^(\(\d+\)|[a-z]\d?\)|-\s)", ln):
            prev = paras[-1]
            if re.search(r"\w ?-$", prev):
                paras[-1] = re.sub(r" ?-$", "", prev) + ln
            else:
                paras[-1] = prev + " " + ln
        else:
            paras.append(ln)
    return "\n\n".join(_clean(p) for p in paras)


async def _constitution(id: str = CONST_ID) -> dict:
    if _clean(id).lower() not in (CONST_ID, "constitutia", "constituția", "constitution", "const"):
        raise NotFound(f"Only the Constitution ('{CONST_ID}') is available for Moldova, got {id!r}")
    if "c" in _const_cache:
        return _const_cache["c"]
    r = await _http.get(CONST_PDF)
    if r.status_code != 200 or not r.content.startswith(b"%PDF"):
        raise SourceError(_http.error("presedinte.md", "Constitution PDF", r.status_code), r.status_code)
    # kerning splits 'AV' / 'VA' in upper-case words: 'A VÂND', 'A VOCATUL', 'MOLDOV A'
    lines = [re.sub(r"\bA V(?=[A-ZÂ]{2})|(?<=[A-Z]{4})V A\b",
                    lambda m: m[0].replace(" ", ""), ln.strip())
             for ln in _http.pdf_text(r.content).splitlines()]
    out, skip = [], False
    for i, ln in enumerate(lines):
        if ln.startswith("CONSTITUŢIA REPUBLICII MOLDOVA") and len(ln) < 32:
            skip = True  # running header, next line is the page number
            continue
        if skip and re.fullmatch(r"\d{1,2}", ln):
            skip = False
            continue
        skip = False
        if ln == "CUPRINS":
            break
        if ln:
            out.append(ln)
    start = next(i for i, ln in enumerate(out) if ln.startswith("NOI, reprezentan"))
    out = out[start:]
    # blocks in document order: ("head", TocEntry) or ("art", [label, heading, lines])
    blocks: list = []
    pre: list[str] = []
    i = 0
    while i < len(out):
        ln = out[i]
        if _HEAD_RE.match(ln) and i + 1 < len(out) and out[i + 1].isupper():
            lvl = 0 if ln.startswith("Titlul") else 1 if ln.startswith("Capitolul") else 2
            j = i + 2  # upper-case headings can run over several lines
            while j < len(out) and out[j].isupper() and not _HEAD_RE.match(out[j]) \
                    and not _ART_RE.match(out[j]):
                j += 1
            name = _join([" ".join(out[i + 1:j])]).capitalize()
            blocks.append(("head", TocEntry(title=f"{_sup_head(ln)} {name}", level=lvl)))
            i = j
            continue
        m = _ART_RE.match(ln)
        if m:
            head = m[2].lstrip(" -.").strip()
            # the heading is the next line unless the body starts at once ('(1) ...')
            if not head and i + 1 < len(out) and not out[i + 1].startswith("(") \
                    and not re.fullmatch(r"[IVX]+", m[1]):
                head = out[i + 1]
                i += 1
                # multi-line heading: continue while a '(1)' paragraph follows shortly
                while i + 1 < len(out) and not out[i + 1].startswith("(") \
                        and not _ART_RE.match(out[i + 1]) \
                        and any(x.startswith("(1)") for x in out[i + 2:i + 4]):
                    head += " " + out[i + 1]
                    i += 1
            blocks.append(("art", [_sup(m[1]), head, []]))
            i += 1
            continue
        if blocks and blocks[-1][0] == "art":
            blocks[-1][1][2].append(ln)
        elif not blocks:
            pre.append(ln)
        i += 1
    entries, articles, full = [], [], ["## Preambul", _join(pre)]
    for kind, b in blocks:
        if kind == "head":
            entries.append(b)
            full.append(f"{'#' * (b.level + 2)} {b.title}")
            continue
        lab, head, body = b
        text = ((f"*{head}*\n\n" if head else "") + _join(body)).strip()
        articles.append((lab, head, text))
        entries.append(TocEntry(title=f"Articolul {lab}" + (f" – {head}" if head else ""),
                                level=3, provision=f"Articolul {lab}"))
        full.append(f"**Articolul {lab}**\n\n{text}")
    data = {"toc": entries, "articles": articles, "text": "\n\n".join(full)}
    _const_cache["c"] = data
    return data


def _sup_head(s: str) -> str:
    """'Capitolul III1' -> 'Capitolul III^1', 'Titlul V1' -> 'Titlul V^1'."""
    return re.sub(r"\b([IVX]+)(\d)$", r"\1^\2", s)
