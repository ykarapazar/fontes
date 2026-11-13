"""Singapore: case law from the SG Courts judgments viewer (elitigation.sg/gd).

No legislation: Singapore Statutes Online (sso.agc.gov.sg) answers this project's
honest User-Agent with a CloudFront "Request blocked" 403 on every path, robots.txt
included (checked 2026-11-05), and its terms put automated extraction under
extra conditions. A blocked source is not used.

Gotchas this code encodes:
  * The judgments viewer is the page judiciary.gov.sg embeds as "Judgments and
    case summaries". Its pages link to the Judiciary's terms of use
    (supremecourt.gov.sg/terms-of-use -> judiciary.gov.sg/terms-of-use): free to
    read, no commercial reproduction without written permission.
  * Search: GET /gd/Home/Index?SearchPhrase=…&CurrentPage=n, HTML, fixed 10 hits a
    page (PageSize is ignored), "Total Judgment(s) Found : N". Filter=SUPCT
    already covers every court (SGCA … SGDC, SGFC, SGMC).
  * Document: /gd/s/<id>, id = neutral citation with brackets/spaces/parens
    dropped: "[2026] SGHC(I) 25" -> "2026_SGHCI_25". Unknown ids give 200 with
    <title>Page Not Found. The judgment is in #divJudgement, the court's own
    case summary (when there is one) in #divCaseSummary.
"""
from __future__ import annotations

import datetime
import re
from urllib.parse import urlencode

from lxml import html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, Results

GD = "https://www.elitigation.sg/gd"
PAGE_SIZE = 10                     # fixed by the site

_SORT = {"relevance": "Score", "date": "DateOfDecision", "title": "Title"}
_COURTS = {
    "SGCA": "Court of Appeal",
    "SGHC": "General Division of the High Court", "SGHCA": "Appellate Division of the High Court",
    "SGHCF": "High Court (Family Division)", "SGHCI": "Singapore International Commercial Court",
    "SGHCR": "High Court (Registrar)", "SGDC": "District Court", "SGMC": "Magistrate's Court",
    "SGFC": "Family Court", "SGYC": "Youth Court",
}
_ID = re.compile(r"(\d{4})_([A-Z]+)_(\d+)")

_doc_cache: dict[str, Decision] = {}


def _norm_id(raw: str) -> str:
    """'[2024] SGCA 1', '2024 SGCA 1', '2024_SGCA_1', '[2026] SGHC(I) 25' -> '2024_SGCA_1'."""
    s = _http.clean(raw).upper()
    m = re.fullmatch(r"\[?(\d{4})\]?[\s_]*([A-Z]+)\s*\(?([A-Z]?)\)?[\s_]*(\d+)", s)
    if not m:
        raise BadRequest(f"Not a Singapore neutral citation: {raw!r}. "
                         "Use e.g. '[2024] SGCA 1' or '2024_SGCA_1'.")
    return f"{m[1]}_{m[2]}{m[3]}_{int(m[4])}"


def _court(id_: str) -> str:
    m = _ID.fullmatch(id_)
    return _COURTS.get(m[2], m[2]) if m else ""


def _date(s: str) -> str:
    """'29 Sep 2015' / '7 February 2024' (first date in s) -> ISO, else ''."""
    m = re.search(r"(\d{1,2})\s+([A-Za-z]{3,9})\s+(\d{4})", s or "")
    if not m:
        return ""
    for fmt, mon in (("%d %B %Y", m[2]), ("%d %b %Y", m[2][:3])):
        try:
            return datetime.datetime.strptime(f"{m[1]} {mon} {m[3]}", fmt).date().isoformat()
        except ValueError:
            continue
    return ""


async def _fetch(url: str, what: str) -> str:
    try:
        r = await _http.get(url)
    except Exception as e:
        raise SourceError(f"elitigation.sg {what}: {e}", "network") from e
    if r.status_code != 200:
        raise SourceError(f"elitigation.sg {what} failed", r.status_code)
    return r.text


def _cards(page_html: str) -> tuple[list[DecisionHit], int | None]:
    doc = lhtml.fromstring(page_html)
    m = re.search(r"Total Judgment\(s\) Found\s*:\s*(\d+)", page_html)
    total = int(m[1]) if m else None
    hits = []
    for card in doc.xpath('//div[contains(@class,"gd-card-body")]'):
        a = card.xpath('.//a[contains(@class,"gd-heardertext")]')
        if not a:
            continue
        mm = re.search(r"/gd/s/([^/?#]+)", a[0].get("href", ""))
        if not mm:
            continue
        id_ = mm[1]
        info = [_http.clean(t.text_content()).strip("| ").strip()
                for t in card.xpath('.//span[contains(@class,"gd-addinfo-text")]')]
        cit = next((i for i in info if re.match(r"\[\d{4}\]", i)), "")
        date = next((_date(i) for i in info if i.startswith("Decision Date")), "")
        case_no = next((i for i in info if i and i != cit and not i.startswith("Decision Date")), "")
        snip = card.xpath('.//div[contains(@class,"search-highlight")]')
        snippet = _http.clean(snip[0].text_content())[:400] if snip else ""
        hits.append(DecisionHit(
            id=id_, title=_http.clean(a[0].text_content()) or cit, court=_court(id_), date=date,
            case_number=case_no, snippet=snippet, url=f"{GD}/s/{id_}"))
    return hits, total


def _first(doc, cls: str) -> str:
    els = doc.xpath(f'//*[contains(concat(" ", normalize-space(@class), " "), " {cls} ")]')
    return _http.clean(_http.text(els[0])) if els else ""


def _parse_decision(id_: str, page_html: str) -> Decision:
    url = f"{GD}/s/{id_}"
    if re.search(r"<title>\s*Page Not Found", page_html, re.I):
        raise NotFound(f"No Singapore judgment {id_} at elitigation.sg ({url}).")
    doc = lhtml.fromstring(page_html)
    body = doc.xpath('//div[@id="divJudgement"]')
    if not body:
        raise SourceError(f"elitigation.sg: no judgment text in {url} (layout changed?)", 200)
    text = _http.html_to_md(lhtml.tostring(body[0], encoding="unicode"))
    if not text:
        raise SourceError(f"elitigation.sg: empty judgment text in {url}", 200)
    summ = doc.xpath('//div[@id="divCaseSummary"]')
    summary = _http.html_to_md(lhtml.tostring(summ[0], encoding="unicode")) if summ else ""

    names = doc.xpath('//*[contains(@class,"HN-CaseName")]')
    name = _http.clean(_http.text(names[0])) if names else ""
    cit = _first(doc, "HN-NeutralCit") or _http.clean(doc.findtext(".//title")) or id_
    coram = _first(doc, "HN-Coram")
    date = _date(_first(doc, "Judg-Date-Reserved"))
    if not date and coram:
        dates = re.findall(r"\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4}", coram)
        date = _date(dates[-1]) if dates else ""
    case_no = _first(doc, "CaseNumber")
    meta = {"Neutral citation": cit}
    if coram:
        meta["Coram"] = coram
    author = _first(doc, "Judg-Author").rstrip(":")
    if author:
        meta["Author"] = author
    cw = [_http.clean(e.text_content()) for e in doc.xpath('//*[contains(@class,"catchwords")]')]
    if cw:
        meta["Catchwords"] = " ".join(c for c in cw if c)
    v = re.search(r"Version No \d+:\s*([^<]+?)\s*<", page_html)
    if v:
        meta["Version"] = _http.clean(v[1])
    return Decision(id=id_, title=name or cit, text=text, url=url, court=_court(id_),
                    date=date, case_number=case_no, summary=summary, metadata=meta)


class Singapore(Jurisdiction):
    code = "sg"
    name = "Singapore"
    languages = ("en",)
    aliases = ("singapore", "sgp")
    sources = (
        Source(
            name="SG Courts judgments (elitigation.sg/gd, Singapore Judiciary)",
            url=f"{GD}/",
            covers=("caselaw",),
            licence="© Government of Singapore / Supreme Court; all rights reserved. Fair dealing "
                    "(private study, research, criticism, review) allowed; no commercial reuse "
                    "without prior written permission",
            commercial_use=False,
            ai_use=None,
            auth="none",
            rate_limit="Not published; 1 request/s self-imposed, no 429 seen in ~15 requests "
                       "(2026-11-05)",
            terms_url="https://www.judiciary.gov.sg/terms-of-use",
            warning="eLitigation's own Terms of Use (cl. 6.1) bar reproducing or displaying "
                    "site material without CrimsonLogic's prior written approval, and the "
                    "Judiciary terms bar commercial reuse without permission.",
            needs_permission=True,
        ),
        Source(
            name="Singapore Statutes Online (sso.agc.gov.sg): statutes live here, not queryable by "
                 "this server because it blocks automated clients; check it in a browser",
            url="https://sso.agc.gov.sg/",
            covers=(),
        ),
    )
    caselaw_filters = {
        "year": ("Year of decision (YYYY), e.g. 2023. One year only: the source has no date range, "
                 'so for "since 2022" run one search per year (sort=date) and merge'),
        "sort": "relevance (default with a query), date (newest first, default without), title",
    }
    min_interval = {"www.elitigation.sg": 1.0}
    notes = ("Case law only: written judgments of the Singapore courts (Court of Appeal, High "
             "Court, SICC, State and Family Courts) from elitigation.sg. Legislation is not "
             "offered: Singapore Statutes Online (sso.agc.gov.sg) blocks automated clients.")
    gaps = (
        ("Legislation (Singapore Statutes Online): CloudFront 403 'Request blocked' to our client; "
         "terms add conditions for automated use"),
        ("Case law (eLitigation): needs permission; terms bar reproducing material without "
         "CrimsonLogic's 'prior written approval'"),
        "Older and unreported judgments: only on LawNet (paid), not published online free",
        ("Government Gazette (egazette.gov.sg): source exists and works but not built yet (archive "
         "search is Algolia)"),
    )
    samples = {
        "caselaw_query": "negligence",
        "decision_id": "2024_SGCA_1",
    }

    async def search_caselaw(self, query, *, limit, page, filters) -> Results[DecisionHit]:
        f = dict(filters or {})
        q = _http.clean(query)
        year = str(f.get("year", "All")).strip() or "All"
        if year != "All" and not re.fullmatch(r"(19|20)\d{2}", year):
            raise BadRequest(f"year must be a single year like 2023, got {f['year']!r}. "
                             "eLitigation cannot filter by a date range: search one year at a time")
        sort = str(f.get("sort", "relevance" if q else "date")).strip().lower()
        if sort not in _SORT:
            raise BadRequest(f"sort must be one of {', '.join(_SORT)}, got {f['sort']!r}")
        limit, page = max(1, int(limit)), max(1, int(page))
        start = (page - 1) * limit
        hits: list[DecisionHit] = []
        total = None
        src_page = start // PAGE_SIZE + 1
        skip = start % PAGE_SIZE
        while len(hits) < limit:
            params = {"Filter": "SUPCT", "YearOfDecision": year, "SortBy": _SORT[sort],
                      "SortAscending": "True" if sort == "title" else "False",
                      "CurrentPage": src_page}
            if q:
                params["SearchPhrase"] = q
            got, total = _cards(await _fetch(f"{GD}/Home/Index?{urlencode(params)}", "search"))
            hits += got[skip:]
            skip = 0
            if len(got) < PAGE_SIZE or (total is not None and src_page * PAGE_SIZE >= total):
                break
            src_page += 1
        return Results(items=hits[:limit], total=total)

    async def get_decision(self, id) -> Decision:
        id_ = _norm_id(id)
        if id_ in _doc_cache:
            return _doc_cache[id_]
        d = _parse_decision(id_, await _fetch(f"{GD}/s/{id_}", f"judgment {id_}"))
        return _http.lru_put(_doc_cache, id_, d, 16)
