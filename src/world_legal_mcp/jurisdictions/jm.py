"""Jamaica: judgments of the Supreme Court and the Court of Appeal (official court sites), and
Privy Council judgments in Jamaican appeals.

Privy Council (the final court): UKPC judgments on Find Case Law, Nov 2009 on, full-text
search through the gb adapter's code, filtered to Jamaican appeals by title "(Jamaica)" or
header "From the Court of Appeal of Jamaica" (bs.jcpc_hits, shared). Id: the neutral
citation, "[2026] UKPC 16".

Both courts run Drupal sites built by the Court Administration Division:

  * Supreme Court (supremecourt.gov.jm): the public view /content/judgments has an exposed
    form: title (party names, "contains"), neutral citation, case number and year (taxonomy
    term id, "tid"). 10 rows a page, ?page=N (0-based). Columns: case number, title,
    presiding judge, delivery date. The view defaults to the current year, so we always
    send tid (All or the year's term).
  * Court of Appeal (courtofappeal.gov.jm): /civil-judgments and /criminal-judgments list a
    whole year on one page (field_year_target_id=<term id>; the "All years" view returns
    HTTP 500 for civil). There is no title search, so year lists are fetched (default: the
    last CA_DEFAULT_YEARS years, or the `year` filter), kept in memory for _TTL (no disk
    cache) and searched there. Columns: citation (neutral citation, or "SCCA 87/2004" for
    old appeals), title, delivery date.

Each judgment is a Drupal node (/node/N) with metadata fields and one PDF (text layer).
Ids are "<court>/<node>", court = jmsc | jmca (the courts' own neutral-citation codes),
e.g. "jmsc/9181" = [2026] JMSC Civ 75; older nodes are listed under a path alias, so their
id is the alias slug ("jmsc/adminstrator-general-v-lewis-patrick-lewis" = /content/<slug>). get_decision also takes a neutral citation
("[2026] JMCA Civ 39"), resolved through the court's own list.

Legislation is not covered: the consolidated Laws of Jamaica (laws.moj.gov.jm) answers
HTTP 503 "Website Maintenance Notice" (pointing to LIPJ) on http and https (checked
2026-11-10; earlier it served an incomplete TLS chain), LIPJ's terms need written consent,
and japarliament.gov.jm has only
as-passed Acts PDFs (no consolidated text) behind Crawl-delay: 15.
"""
from __future__ import annotations

import re
import time
from urllib.parse import quote, urljoin

from lxml import html as lhtml

from .. import _http
from .bs import JCPC_SOURCE, is_jcpc_id, jcpc_decision, jcpc_hits
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, Results

SC_HOST = "supremecourt.gov.jm"
CA_HOST = "courtofappeal.gov.jm"
SC = f"https://{SC_HOST}"
CA = f"https://{CA_HOST}"
COURTS = {"jmsc": "Supreme Court of Judicature of Jamaica", "jmca": "Court of Appeal of Jamaica"}
HOSTS = {"jmsc": SC, "jmca": CA}
CA_LISTS = {"Civil": f"{CA}/civil-judgments", "Criminal": f"{CA}/criminal-judgments"}
SC_PAGE = 10                      # rows per page in the Supreme Court view (fixed by the site)
_TTL = 6 * 3600
_ID = re.compile(r"^(jmsc|jmca)/(\d{1,7}|[a-z0-9][a-z0-9%._-]{0,250})$", re.I)
_CITE = re.compile(r"\[?\s*(\d{4})\s*\]?\s*JM\s*(SC|CA)\s+([A-Za-z]+)\.?\s*(\d+)", re.I)
_YEAR = re.compile(r"^\d{4}$")

_ca_cache: dict = {}             # (kind, year) -> (monotonic time, rows)
_ca_years: dict[str, dict[str, str]] = {}   # kind -> {"2026": term id}
CA_DEFAULT_YEARS = 3             # Court of Appeal years searched when no year filter is given
_sc_years: dict[str, str] = {}   # "2026" -> taxonomy term id
_COURT_ALIASES = {
    "jmsc": "jmsc", "sc": "jmsc", "supreme": "jmsc", "supreme court": "jmsc",
    "jmca": "jmca", "ca": "jmca", "appeal": "jmca", "court of appeal": "jmca",
    "jcpc": "jcpc", "ukpc": "jcpc", "privy council": "jcpc", "pc": "jcpc",
}
_JCPC_JM = ("Jamaica", "From the Court of Appeal of Jamaica")


def _cite(s: str) -> str:
    """Normalise a Jamaican neutral citation: '2026] JMCA App 17' -> '[2026] JMCA App 17'."""
    m = _CITE.search(s or "")
    if not m:
        return ""
    kind = m[3].capitalize()
    return f"[{m[1]}] JM{m[2].upper()} {kind} {int(m[4])}"


def _cell(td) -> str:
    return _http.clean(td.text_content()) if td is not None else ""


def _node(href: str) -> str:
    """Key of a node link: '/node/9181' -> '9181', '/content/some-case-v-other' -> the slug."""
    m = re.match(r"^(?:https?://[^/]+)?/(?:node/(\d+)|content/([^/?#]+))$", href or "")
    return (m[1] or m[2]) if m else ""


def _page_url(court: str, key: str) -> str:
    return f"{HOSTS[court]}/node/{key}" if key.isdigit() else f"{HOSTS[court]}/content/{key}"


# --------------------------------------------------------------------------- #
# Supreme Court
# --------------------------------------------------------------------------- #
async def _sc_get(params: dict) -> lhtml.HtmlElement:
    qs = "&".join(f"{k}={quote(str(v))}" for k, v in params.items())
    r = await _http.get(f"{SC}/content/judgments?{qs}")
    if r.status_code != 200:
        raise SourceError(_http.error("Supreme Court of Jamaica", "judgment list failed", r.status_code),
                          r.status_code)
    doc = lhtml.fromstring(r.text)
    if not _sc_years:
        for o in doc.xpath('//select[@name="tid"]/option'):
            if _YEAR.match((o.text or "").strip()):
                _sc_years[o.text.strip()] = o.get("value")
    return doc


def _sc_rows(doc) -> list[DecisionHit]:
    out = []
    for tr in doc.xpath('//table[thead//th[contains(@class,"views-field-field-case-number")]]/tbody/tr'):
        a = tr.xpath('.//td[contains(@class,"views-field-title")]//a[@href]')
        nid = _node(a[0].get("href")) if a else ""
        if not nid:
            continue
        num = _cell((tr.xpath('.//td[contains(@class,"views-field-field-case-number")]') or [None])[0])
        judge = _cell((tr.xpath('.//td[contains(@class,"views-field-field-presiding")]') or [None])[0])
        date = _cell((tr.xpath('.//td[contains(@class,"views-field-field-date-of-delivery")]') or [None])[0])
        title = _cell(a[0]) or f"{COURTS['jmsc']} {num}"
        out.append(DecisionHit(
            id=f"jmsc/{nid}", title=title, court=COURTS["jmsc"],
            date=date[:10] if re.match(r"^\d{4}-\d{2}-\d{2}", date) else _http.iso_date(date),
            case_number=num, snippet=judge, url=_page_url("jmsc", nid)))
    return out


def _sc_has_next(doc, page0: int) -> bool:
    return any(int(m) > page0 for h in doc.xpath('//a/@href')
               for m in re.findall(r"[?&]page=(\d+)", h))


async def _sc_year(year: str) -> str:
    if not _sc_years:
        await _sc_get({"title": "", "tid": "All"})
    tid = _sc_years.get(year)
    if not tid:
        raise BadRequest(f"The Supreme Court list has no year {year}; years run "
                         f"{min(_sc_years, default='1962')}-{max(_sc_years, default='')}.")
    return tid


# --------------------------------------------------------------------------- #
# Court of Appeal
# --------------------------------------------------------------------------- #
def _ca_parse(doc, kind: str) -> list[dict]:
    rows = []
    for tr in doc.xpath('//table[thead//th[contains(@class,"views-field-nothing")]]/tbody/tr'):
        a = tr.xpath('.//td[contains(@class,"views-field-title")]//a[@href]')
        nid = _node(a[0].get("href")) if a else ""
        if not nid:
            continue
        raw = _cell((tr.xpath('.//td[contains(@class,"views-field-nothing")]') or [None])[0])
        t = tr.xpath('.//td[contains(@class,"views-field-field-date")]//time/@datetime')
        rows.append({"nid": nid, "raw": raw, "cite": _cite(raw), "title": _cell(a[0]),
                     "date": t[0][:10] if t else "", "kind": kind})
    return rows


async def _ca_fetch(url: str, kind: str):
    r = await _http.get(url)
    if r.status_code != 200:
        raise SourceError(_http.error("Court of Appeal of Jamaica", f"{kind.lower()} judgment list failed",
                                      r.status_code), r.status_code)
    return lhtml.fromstring(r.text)


async def _ca_list(kind: str, year: str) -> list[dict]:
    """One year of one Court of Appeal list (the site's "All years" view returns HTTP 500
    for civil judgments, so lists are fetched a year at a time and cached in memory)."""
    hit = _ca_cache.get((kind, year))
    if hit and time.monotonic() - hit[0] < _TTL:
        return hit[1]
    url = CA_LISTS[kind]
    years = _ca_years.get(kind)
    if years is None:   # first call: the default view (current year) also carries the year menu
        doc = await _ca_fetch(url, kind)
        years = {(o.text or "").strip(): o.get("value") for o in
                 doc.xpath('//select[@name="field_year_target_id"]/option')
                 if _YEAR.match((o.text or "").strip())}
        if not years:
            raise SourceError(f"Error (Court of Appeal of Jamaica): no year menu on {url}.", "layout")
        _ca_years[kind] = years
        sel = doc.xpath('//select[@name="field_year_target_id"]/option[@selected]/text()')
        if sel and sel[0].strip() in years:
            _http.lru_put(_ca_cache, (kind, sel[0].strip()), (time.monotonic(), _ca_parse(doc, kind)), 64)
            if sel[0].strip() == year:
                return _ca_cache[(kind, year)][1]
    if year not in years:
        return []
    doc = await _ca_fetch(f"{url}?field_year_target_id={years[year]}", kind)
    return _http.lru_put(_ca_cache, (kind, year), (time.monotonic(), _ca_parse(doc, kind)), 64)[1]


async def _ca_rows(years: list[str]) -> list[dict]:
    return [row for y in years for kind in CA_LISTS for row in await _ca_list(kind, y)]


def _ca_hit(row: dict) -> DecisionHit:
    return DecisionHit(
        id=f"jmca/{row['nid']}", title=row["title"] or f"{COURTS['jmca']} {row['raw']}",
        court=COURTS["jmca"], date=row["date"], case_number=row["cite"] or row["raw"],
        snippet=f"{row['kind']} judgment", url=_page_url("jmca", row["nid"]))


# --------------------------------------------------------------------------- #
# Node pages
# --------------------------------------------------------------------------- #
def _fields(article) -> dict[str, object]:
    """Drupal 'label / value' field pairs of a node: <div><div>Label</div><div>value</div></div>."""
    out: dict[str, object] = {}
    for div in article.xpath(".//div[count(div)>=2]"):
        kids = div.xpath("./div")
        label = _http.clean(kids[0].text_content())
        if label and len(label) < 40 and not kids[0].xpath(".//div|.//a") and label not in out:
            out[label] = kids[1]
    return out


async def _decision(court: str, nid: str) -> Decision:
    host = HOSTS[court]
    page_url = _page_url(court, nid)
    r = await _http.get(page_url)
    if r.status_code == 404:
        raise NotFound(f"{COURTS[court]} has no page {page_url}.")
    if r.status_code != 200:
        raise SourceError(_http.error(COURTS[court], f"node {nid} failed", r.status_code), r.status_code)
    doc = lhtml.fromstring(r.text)
    art = [a for a in doc.xpath('//article')
           if a.xpath('.//a[contains(@href,"/sites/default/files/judgments/")]')]
    pdfs = art[0].xpath('.//a[contains(@href,"/sites/default/files/judgments/")]/@href') if art else []
    if not pdfs:
        raise NotFound(f"{page_url} is not a judgment (no judgment PDF attached).")
    f = _fields(art[0])

    def val(*labels):
        for lb in labels:
            if lb in f:
                el = f[lb]
                t = el.xpath(".//time/@datetime")
                return t[0][:10] if t else _http.clean(el.text_content())
        return ""

    title_el = doc.xpath("//h1[contains(@class,'node__title')]") or doc.xpath("//title")
    title = _http.clean(title_el[0].text_content()) if title_el else ""
    title = re.sub(r"\s*\|\s*(Supreme Court|Court of Appeal)\s*$", "", title)
    cite = _cite(val("Neutral Citation")) or val("Neutral Citation")
    case_no = val("Case Number")
    date = val("Date of Delivery", "Date")
    pdf = urljoin(host + "/", pdfs[0])
    p = await _http.get(pdf)
    if p.status_code != 200:
        raise SourceError(_http.error(COURTS[court], f"PDF for node {nid} failed", p.status_code), p.status_code)
    text = _http.pdf_text(p.content)
    if len(text) < 200:
        raise SourceError(f"Error ({COURTS[court]}): {pdf} has no text layer (scanned; no OCR here); "
                          "read it there.", "pdf")
    # headnote: the node's free-text paragraph(s), outside the label/value fields
    notes = [_http.clean(x.text_content()) for x in art[0].xpath(".//p")]
    meta = {k: v for k, v in (
        ("Neutral citation", cite),
        ("Presiding judge", val("Presiding Judge")), ("Judgment type", val("Judgment Type")),
        ("Node page", page_url)) if v}
    return Decision(
        id=f"{court}/{nid}", title=title or f"{COURTS[court]} {cite or case_no or nid}",
        text=text, url=pdf, court=COURTS[court],
        date=date if re.match(r"^\d{4}-\d{2}-\d{2}$", date) else "",
        case_number=case_no or cite, summary="\n\n".join(n for n in notes if n), metadata=meta)


# --------------------------------------------------------------------------- #
class Jamaica(Jurisdiction):
    code = "jm"
    name = "Jamaica"
    languages = ("en",)
    aliases = ("jamaica", "jam", "jamaican courts")
    _terms = ("© the Court; no licence stated. Terms of Use page has a privacy policy and "
              "disclaimer only ('makes the information on this website available as a public "
              "service'); silent on reuse and automated access (read 2026-11-05)")
    sources = (
        JCPC_SOURCE,
        Source(
            name="Supreme Court of Jamaica judgments (supremecourt.gov.jm)",
            url=f"{SC}/content/judgments",
            covers=("caselaw",),
            licence=_terms,
            commercial_use=None,
            ai_use=None,   # robots.txt: Drupal default (only /admin/, /search/, /user/... disallowed); no AI clause
            auth="none",
            rate_limit="unknown; no Crawl-delay; 1 s spacing, no 429 in ~15 requests (2026-11)",
            terms_url=f"{SC}/content/terms-use",
        ),
        Source(
            name="Court of Appeal of Jamaica judgments (courtofappeal.gov.jm)",
            url=f"{CA}/content/judgmentsmemoranda-reasonsendorsements",
            covers=("caselaw",),
            licence=_terms,
            commercial_use=None,
            ai_use=None,   # robots.txt: Drupal default, same as the Supreme Court; no AI clause
            auth="none",
            rate_limit=("unknown; no Crawl-delay; 1 s spacing, the two judgment lists cached in "
                        "memory 6 h; no 429 in ~10 requests (2026-11)"),
            terms_url=f"{CA}/content/terms-use",
        ),
    )
    caselaw_filters = {
        "court": "jcpc (Privy Council, final court), jmca (Court of Appeal) or jmsc (Supreme Court); default all",
        "year": ("year of the judgment, YYYY (without it the Court of Appeal is searched for the "
                 "last 3 years only)"),
    }
    min_interval = {SC_HOST: 1.0, CA_HOST: 1.0, "caselaw.nationalarchives.gov.uk": 0.3}
    notes = ("Privy Council (final court) judgments in Jamaican appeals, Nov 2009 on, full-text search, "
             "from Find Case Law (UK National Archives). "
             "Supreme Court and Court of Appeal judgments from the courts' own sites (mostly "
             "1990s-; older PDFs are often scans without text). Search matches party names / title "
             "and neutral citation, not full text. No legislation: the Laws of Jamaica site "
             "(laws.moj.gov.jm) is down for maintenance (HTTP 503, 2026-11-10).")
    gaps = (
        ("Privy Council judgments before Nov 2009: only on BAILII (no API, forbids scraping); Find Case "
         "Law's UKPC collection starts 2009"),
        ("Privy Council country filter is heuristic (Find Case Law has no country field): title "
         "'(Jamaica)' or header 'From the Court of Appeal of Jamaica'; a judgment with neither is missed "
         "(e.g. [2017] UKPC 21, header 'From the Court of Appeal Jamaica')"),
        ("Consolidated legislation and the Constitution (Laws of Jamaica, laws.moj.gov.jm): site down, "
         "HTTP 503 'Website Maintenance Notice' pointing to LIPJ (http and https, 2026-11-10)"),
        ("LIPJ portal (lipj.gov.jm, ~18k acts/regulations): needs permission (terms §3 'lawful, "
         "non-commercial purposes'; §6 no exploiting portal functionality without prior written consent)"),
        "As-passed Acts PDFs (japarliament.gov.jm): source exists but not built yet (no consolidated text, Crawl-delay 15)",
        "Older judgments: scans only, no text (no OCR)",
        "Parish and other lower courts: not researched yet",
    )
    samples = {
        "caselaw_query": "Marksman",
        "decision_id": "jmsc/9181",   # A.C. v Marksman Limited [2026] JMSC Civ 75
    }

    # ------------------------------------------------------------------ #
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        f = {k: str(v).strip() for k, v in (filters or {}).items() if str(v).strip()}
        court = ""
        if "court" in f:
            court = _COURT_ALIASES.get(f["court"].lower(), "")
            if not court:
                raise BadRequest("court must be jcpc (Privy Council), jmca (Court of Appeal) or "
                                 "jmsc (Supreme Court).")
        year = f.get("year", "")
        if year and not _YEAR.match(year):
            raise BadRequest("year must be YYYY, e.g. 2024.")
        q = _http.clean(query or "")
        cite = _cite(q) if re.search(r"JM\s*(SC|CA)", q, re.I) else ""
        if cite:
            court = court or ("jmsc" if "JMSC" in cite else "jmca")
            year = year or cite[1:5]
        this = int(_http.today()[:4])
        limit = max(1, min(int(limit), 50))
        page = max(1, int(page))
        start, end = (page - 1) * limit, page * limit

        # Privy Council first: Find Case Law full-text search, filtered to Jamaican appeals
        jc = await jcpc_hits(*_JCPC_JM, q, year) if court in ("", "jcpc") and not cite else []
        jc_items = jc[start:end]
        start, end = max(0, start - len(jc)), max(0, end - len(jc))

        # Court of Appeal: in-memory search of the full lists
        ca_hits: list[DecisionHit] = []
        if court in ("", "jmca"):
            words = [w.lower() for w in re.findall(r"\w+", q) if w.lower() not in ("v", "vs")]
            years = [year] if year else [str(this - i) for i in range(CA_DEFAULT_YEARS)]
            for row in await _ca_rows(years):
                if cite:
                    if row["cite"] != cite:
                        continue
                elif words:
                    hay = f"{row['title']} {row['raw']} {row['cite']}".lower()
                    if not all(re.search(rf"\b{re.escape(w)}", hay) for w in words):
                        continue
                ca_hits.append(_ca_hit(row))
            ca_hits.sort(key=lambda h: h.date, reverse=True)
        items = jc_items + ca_hits[start:end]
        total: int | None = len(jc) + len(ca_hits)

        # Supreme Court: the site's own filtered view, 10 rows a page
        if court in ("", "jmsc"):
            params = {"title": "" if cite else q, "tid": await _sc_year(year) if year else "All"}
            if cite:
                params["field_neutral_citation_value"] = cite
            sc_start, sc_end = max(0, start - len(ca_hits)), end - len(ca_hits)
            if sc_end <= 0:            # this page is all Court of Appeal hits
                total = None
            p0 = sc_start // SC_PAGE
            while sc_end > 0 and p0 * SC_PAGE < sc_end:
                doc = await _sc_get({**params, "page": p0})
                rows = _sc_rows(doc)
                items += [h for i, h in enumerate(rows, p0 * SC_PAGE) if sc_start <= i < sc_end]
                if len(rows) < SC_PAGE or not _sc_has_next(doc, p0):
                    total = len(jc) + len(ca_hits) + p0 * SC_PAGE + len(rows)   # last page: exact
                    break
                total = None                                          # more pages: count unknown
                p0 += 1
        note = ("" if year or court in ("jmsc", "jcpc") else
                f"Court of Appeal: only {this - CA_DEFAULT_YEARS + 1}-{this} searched; "
                "set filter year for older judgments. ")
        note += ("Privy Council: full-text search (all words), 2009 on, listed first. Local courts: "
                 "matches party names / title and neutral citation, not full text (Supreme Court: the "
                "query must appear as one phrase in the title). "
                "Court of Appeal hits first (newest first), then Supreme Court (A-Z by title).")
        if not items and not cite and court != "jcpc":
            # a zero count would read as "no such judgments": local search is title-only
            note = ("No title matches. This is NOT a subject search: Jamaican local-court judgments "
                    "are searched by party name / title only, so a topic word such as 'negligence' "
                    "finds nothing even where such judgments exist; try a party name. " + note)
            total = None
        return Results(items=items, total=total, note=note)

    # ------------------------------------------------------------------ #
    async def get_decision(self, id):
        ident = (id or "").strip()
        if is_jcpc_id(ident):
            return await jcpc_decision(ident)
        m = _ID.match(ident)
        if m:
            return await _decision(m[1].lower(), m[2])
        cite = _cite(ident)
        if not cite or not re.search(r"JM\s*(SC|CA)", ident, re.I):
            raise BadRequest("Give an id from search_caselaw ('[2026] UKPC 16', 'jmsc/9181', 'jmca/5481') or a "
                             "Jamaican neutral citation ('[2026] JMSC Civ 75', '[2026] JMCA Civ 39').")
        if "JMCA" in cite:
            row = next((r for r in await _ca_rows([cite[1:5]]) if r["cite"] == cite), None)
            if not row:
                raise NotFound(f"The Court of Appeal judgment lists have no {cite}.")
            return await _decision("jmca", row["nid"])
        doc = await _sc_get({"title": "", "tid": "All", "field_neutral_citation_value": cite})
        hits = _sc_rows(doc)   # the citation filter is an exact match
        if not hits:
            raise NotFound(f"The Supreme Court judgment list has no {cite} (the citation filter is "
                           "exact; try search_caselaw with a party name).")
        return await _decision("jmsc", hits[0].id.split("/")[1])
