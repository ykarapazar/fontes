"""Nepal: Supreme Court precedents from Nepal Kanoon Patrika (नेपाल कानून पत्रिका, nkp.gov.np),
the Supreme Court's own law report. Nepali only; nothing is translated.

How the site works (verified 2026-11-06 from a UK IP, honest User-Agent):
  * Search: GET /advance_search/?keywords=…&Submit=खोज्‍नुहोस्[&per_page=N]
      - Without the `Submit` parameter the form is not run and the home page comes back.
      - 20 hits per page, fixed; `per_page` is the 0-based row offset (20, 40, …).
      - Hit count heading "६७३ खोजी नतिजाहरु" (Nepali digits); no hits ->
        "तपाइँको खोजको कुनै नतिजा फेला पारेन".
      - Multi-word keywords narrow the result (AND / phrase), e.g. अंश 2609, अंश चलन 1269.
      - Other form fields: nirnaya_number (decision no., Nepali or ASCII digits),
        mudda_number (case no., e.g. 074-CR-0171), year (NKP volume year, BS),
        faisala_date_from / faisala_date_to ("YYYY/MM/DD" Bikram Sambat; "-" finds nothing),
        judge, badi / pratibadi (parties), ijlas_type (bench).
  * Document: GET /full_detail/{id}; an unknown id answers 302 -> /home.
    {id} is the site's own document id; the reported decision number (निर्णय नं.) differs.
  * Dates are Bikram Sambat (वि.सं.), not Gregorian, and there is no Gregorian date on the
    page. ISO `date` is therefore left empty and the BS date is given in the metadata.
  * Older full texts were converted from legacy (Preeti-style) fonts: Latin words inside
    them can come out as Devanagari gibberish (e.g. "(तष्mभ ष्mmझयचष्ब)ि" for
    "(time immemorial)") and case numbers likewise ("०७३–ल्ँ–००१५"). The search-list
    headnote is usually clean.
  * robots.txt: none (404) on nkp.gov.np. No terms-of-use page; the footer says
    "Copyright © 2026. All Rights Reserved by Supreme Court of Nepal." Nothing on
    automated access.

Not used:
  * Legislation (lawcommission.gov.np, Nepal Law Commission): robots.txt allows all with
    "Crawl-delay: 10", but Acts are published only as PDFs on giwmscdnone.gov.np whose text
    layer is broken (Kalimati/Mangal fonts without correct ToUnicode maps: "मन्िालय" for
    "मन्त्रालय", "गनन" for "गर्न"; same with pdftotext), so quoting them would misstate the
    law; and full GETs of several Act PDFs (e.g. मुलुकी देवानी संहिता, २०७४) are dropped by the
    CDN with an empty reply. No OCR / no workaround, so no legislation.
  * supremecourt.gov.np: F5 JavaScript challenge page; robots.txt redirects to the home page.
"""
from __future__ import annotations

import re
from urllib.parse import urlsplit

import lxml.html

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, Results

HOST = "nkp.gov.np"
BASE = f"https://{HOST}"
SUBMIT = "खोज्‍नुहोस्"        # with the zero-width joiner the site's own button uses
PAGE_SIZE = 20
COURT = "सर्वोच्च अदालत"
_ND = str.maketrans("०१२३४५६७८९", "0123456789")
_AD = str.maketrans("0123456789", "०१२३४५६७८९")
_BS_DATE = re.compile(r"^(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})$")
_ID = re.compile(r"^\d{1,9}$")
_DEC_NO = re.compile(r"^(?:नि\.\s*नं\.?|निर्णय\s*नं\.?|nirnaya[: ]|decision[: ])\s*#?\s*([0-9०-९]+)$", re.I)
_CASE_NO = re.compile(r"^[0-9०-९]{2,4}\s*[-–]\s*[A-Z]{2}\s*[-–]\s*[0-9०-९]{1,5}$")
_BENCHES = {"सिङ्गल बेञ्च इजलास": "8", "एक न्यायाधीशको इजलास": "9", "फूल बेन्च इजलास": "6",
            "डिभिजन वेन्च इजलास": "7", "स्पेशल बेञ्च इजलास": "11", "तीन न्यायाधीशको इजलास": "10",
            "एकल इजलास": "1", "संयुक्त इजलास": "2", "पूर्ण इजलास": "3", "विशेष इजलास": "4",
            "वृहद पूर्ण इजलास": "5"}
_GENERIC = {"संविधान", "संविधानको", "धारा", "उपधारा", "दफा", "उपदफा", "नं", "नं.", "ऐन", "ऐनको",
            "नियम", "नियमको", "अनुच्छेद", "खण्ड"}
WINDOW = 100                # source rows re-ranked per query (5 requests)
_cache: dict = {}
RERANK_WINDOW = 100   # source pages fetched to rank by headnote match (5 requests)
_SUFFIXES = ("हरूको", "हरूमा", "हरू", "लाई", "को", "का", "की", "मा", "ले")


def _stems(query: str) -> list[str]:
    out = []
    for w in re.split(r"[\s,;]+", query):
        for sfx in _SUFFIXES:
            if w.endswith(sfx) and len(w) - len(sfx) >= 3:
                w = w[:-len(sfx)]
                break
        if len(w) >= 3:
            out.append(w)
    return out


def _score(h: DecisionHit, stems: list[str]) -> int:
    text = f"{h.title} {h.snippet}"
    return sum(st in text for st in stems)


def _score(h: DecisionHit, phrase: str, terms: list[str], pool: list[DecisionHit] | None = None) -> float:
    t = f"{h.title} {h.snippet}"
    # Rarer words weigh more: in a pool where "धारा" is everywhere, "गोपनीयता" must decide.
    texts = [f"{x.title} {x.snippet}" for x in pool or [h]]
    wt = {w: len(texts) / max(1, sum(w in x for x in texts)) for w in terms}
    return 10 * (phrase in t) + sum(wt[w] * (3 * (w in t) + min(t.count(w), 3)) for w in terms)


def _ascii(s: str) -> str:
    return (s or "").translate(_ND)


def _bs(s: str) -> str:
    """'२०८१/११/११' -> '2081-11-11' (still Bikram Sambat); '' if not a date."""
    m = _BS_DATE.match(_ascii(_http.clean(s)).replace("।", "/"))
    return f"{m[1]}-{int(m[2]):02d}-{int(m[3]):02d}" if m else ""


def _bs_filter(v, name: str) -> str:
    d = _bs(str(v or ""))
    if not d or not (1 <= int(d[5:7]) <= 12 and 1 <= int(d[8:10]) <= 32):
        raise BadRequest(f"{name} must be a valid Bikram Sambat date like 2080-01-01 (or 2080/01/01; "
                         f"month 1-12, day 1-32), got {v!r}. NKP has no Gregorian dates.")
    return d.replace("-", "/")


def _root(html: str):
    return lxml.html.fromstring(html)


async def _get(url: str, params: dict | None = None):
    r = await _http.get(url, params=params)
    if r.status_code != 200:
        raise SourceError(_http.error("nkp.gov.np", "request failed", r.status_code), r.status_code)
    return r


def _total(root) -> int | None:
    for h in root.xpath("//div[contains(@class,'main-listing')]/h2"):
        t = _http.clean(h.text_content())
        if "कुनै नतिजा" in t:
            return 0
        m = re.match(r"([0-9०-९]+)\s*खोजी", t)
        if m:
            return int(_ascii(m[1]))
    return None


def _hits(root) -> list[DecisionHit]:
    out = []
    for art in root.xpath("//div[contains(@class,'main-listing')]//article"):
        a = art.xpath(".//h3[contains(@class,'post-title')]/a")
        if not a:
            continue
        m = re.search(r"/full_detail/(\d+)", a[0].get("href", ""))
        if not m:
            continue
        title = _http.clean(a[0].text_content())
        details = art.xpath(".//div[contains(@class,'type-details')]")
        date_bs = bench = ""
        if details:
            spans = details[0].xpath("./span")
            if spans:
                date_bs = _bs(spans[0].text_content().split(":", 1)[-1])
            tags = details[0].xpath(".//i[contains(@class,'glyphicon-tag')]/following-sibling::a")
            bench = _http.clean(tags[0].text_content()) if tags else ""
        paras = [_http.clean(p.text_content()) for p in art.xpath("./p")]
        head = " · ".join(x for x in (f"फैसला मिति (वि.सं.) {date_bs}" if date_bs else "", bench) if x)
        snippet = " ".join(p for p in paras if p)
        out.append(DecisionHit(
            id=m[1], title=title, court=f"{COURT}, {bench}" if bench else COURT, date="",
            snippet=f"{head}. {snippet}".strip(". ") if head else snippet,
            url=f"{BASE}/full_detail/{m[1]}"))
    return out


async def _search_page(params: dict, offset: int) -> tuple[list[DecisionHit], int | None]:
    key = (tuple(sorted(params.items())), offset)
    if key in _cache:
        return _cache[key]
    q = dict(params, Submit=SUBMIT)
    if offset:
        q["per_page"] = str(offset)
    r = await _get(f"{BASE}/advance_search/", q)
    root = _root(r.text)
    total = _total(root)
    if total is None:
        raise SourceError("nkp.gov.np: search page without a result heading (layout changed?)")
    return _http.lru_put(_cache, key, (_hits(root), total), 64)


async def _resolve_decision_no(no: str) -> str:
    hits, total = await _search_page({"nirnaya_number": _ascii(no)}, 0)
    if not hits:
        raise NotFound(f"No NKP decision with निर्णय नं. {no}.")
    if len(hits) > 1:
        ids = ", ".join(f"{h.id} ({h.title})" for h in hits[:5])
        raise BadRequest(f"निर्णय नं. {no} matches {total} NKP entries (numbers repeat in some "
                         f"volumes); pass one of these document ids: {ids}")
    return hits[0].id


class Nepal(Jurisdiction):
    code = "np"
    name = "Nepal"
    languages = ("ne",)
    aliases = ("nepal", "npl")
    sources = (
        Source(
            name="Nepal Kanoon Patrika (नेपाल कानून पत्रिका), Supreme Court of Nepal",
            url=BASE, covers=("caselaw",),
            licence="© Supreme Court of Nepal, all rights reserved (no licence stated; no terms of use page)",
            commercial_use=None, ai_use=None, auth="none",
            rate_limit="unknown; 1.5 s spacing, no 429 seen in ~40 requests (2026-11)",
            terms_url=BASE + "/credits",
            warning=("Official Supreme Court law report, all rights reserved; dates are Bikram Sambat "
                     "(वि.सं.), and older texts carry legacy-font conversion errors in Latin words."),
        ),
    )
    caselaw_filters = {
        "decision_number": "NKP decision number (निर्णय नं.), e.g. 11512 or ११५१२",
        "case_number": "case number (मुद्दा नं.), e.g. 074-CR-0171",
        "nkp_year": "NKP volume year in Bikram Sambat (साल), e.g. 2081",
        "date_from": "decision date from, Bikram Sambat YYYY-MM-DD, e.g. 2080-01-01",
        "date_to": "decision date to, Bikram Sambat YYYY-MM-DD, e.g. 2080-12-30",
        "bench": "bench (इजलास): " + ", ".join(_BENCHES),
        "judge": "judge name (न्यायाधीश), Nepali",
        "party": "party name (पक्ष), Nepali",
    }
    min_interval = {HOST: 1.5}
    notes = ("Supreme Court precedents reported in Nepal Kanoon Patrika since 2015 BS (1958), "
             "Nepali only; search in Nepali Unicode. Dates are Bikram Sambat. No legislation "
             "(Law Commission Acts are PDFs with a broken text layer).")
    gaps = (
        "Legislation (Nepal Law Commission Acts): broken PDF text layer (wrong font maps) and CDN"
         " drops full downloads; no text",
        "Supreme Court site (supremecourt.gov.np): F5 JavaScript challenge blocks our client",
        "High Courts, District Courts and unreported Supreme Court decisions: not researched yet",
        "English translations: not published (NKP is Nepali only)",
    )
    samples = {"caselaw_query": "बकसपत्र", "decision_id": "10608"}

    async def search_caselaw(self, query, *, limit, page, filters):
        params: dict[str, str] = {}
        if (query or "").strip():
            params["keywords"] = query.strip()
        f = filters or {}
        if f.get("decision_number"):
            no = _ascii(str(f["decision_number"]).strip())
            if not no.isdigit():
                raise BadRequest(f"decision_number must be digits, e.g. 11512, got {f['decision_number']!r}")
            params["nirnaya_number"] = no
        if f.get("case_number"):
            params["mudda_number"] = _ascii(str(f["case_number"]).strip())
        if f.get("nkp_year"):
            y = _ascii(str(f["nkp_year"]).strip())
            if not re.fullmatch(r"20\d\d", y):
                raise BadRequest(f"nkp_year must be a Bikram Sambat year like 2081, got {f['nkp_year']!r}")
            params["year"] = y
        if f.get("date_from"):
            params["faisala_date_from"] = _bs_filter(f["date_from"], "date_from")
        if f.get("date_to"):
            params["faisala_date_to"] = _bs_filter(f["date_to"], "date_to")
        if f.get("date_from") and f.get("date_to") and params["faisala_date_from"] > params["faisala_date_to"]:
            raise BadRequest(f"date_from {f['date_from']!r} is after date_to {f['date_to']!r}.")
        if f.get("bench"):
            b = _http.clean(str(f["bench"]))
            if b not in _BENCHES:
                raise BadRequest(f"bench must be one of: {', '.join(_BENCHES)}")
            params["ijlas_type"] = _BENCHES[b]
        if f.get("judge"):
            params["judge"] = _http.clean(str(f["judge"]))
        if f.get("party"):
            params["badi"] = _http.clean(str(f["party"]))
        if not params:
            raise BadRequest("Give a Nepali search word (e.g. बकसपत्र) or a filter.")

        start = (page - 1) * limit
        kw = params.get("keywords", "")
        if kw and start + limit <= WINDOW:
            # NKP lists hits newest first, not by relevance: re-rank the first WINDOW rows by
            # how often the query words occur in the title and headnote.
            pool: list[DecisionHit] = []
            cur = 0
            while True:
                hits, total = await _search_page(params, cur)
                pool += hits
                cur += PAGE_SIZE
                if len(hits) < PAGE_SIZE or cur >= min(total, WINDOW):
                    break
            # Provision words ("संविधानको धारा २८") and bare numbers are in nearly every headnote
            # and say nothing about the topic: rank by the remaining words when there are any.
            words = kw.split()
            terms = [w for w in words if w not in _GENERIC and not _ascii(w).isdigit()] or words
            score = {h.id: _score(h, kw, terms, pool) for h in pool}
            pool.sort(key=lambda h: -score[h.id])  # stable: ties keep newest first
            n = sum(1 for h in pool if score[h.id])
            note = "Dates are Bikram Sambat (वि.सं.); use BS dates in date filters. "
            note += "NKP lists decisions newest first, not by relevance. "
            if pool:
                note += (f"The first {len(pool)} hits were re-ranked here by the query words in the "
                         "title and headnote (" + (f"{n} document(s) mention them" if n else
                         f"None of the first {len(pool)} mention them in the headnote") + "). ")
            note += ("Only Supreme Court precedents in NKP; High Court and District Court "
                     "decisions are not covered.")
            if not total:
                note += (" No hits: NKP matches exact word forms; try the stem or another "
                         "word, e.g. गोपनीयता (not निजता) for privacy.")
            return Results(items=pool[start:start + limit], total=total, note=note)
        items: list[DecisionHit] = []
        off = cur = start // PAGE_SIZE * PAGE_SIZE
        while True:  # a requested page can straddle two source pages of 20
            hits, total = await _search_page(params, cur)
            items += hits
            cur += PAGE_SIZE
            if len(items) >= start - off + limit or len(hits) < PAGE_SIZE or cur >= total:
                break
        items = items[start - off:start - off + limit]
        return Results(items=items, total=total,
                       note="Dates are Bikram Sambat (वि.सं.); use BS dates in date filters. "
                            "NKP lists decisions newest first, not by relevance. Only Supreme "
                            "Court precedents; High Court and District Court decisions are not covered.")

    async def get_decision(self, id):
        raw = _http.clean(id)
        if raw.startswith("http"):
            u = urlsplit(raw)
            m = re.match(r"^/full_detail/(\d+)", u.path or "")
            if (u.hostname or "").lower() not in (HOST, "www." + HOST) or not m:
                raise BadRequest("Give an NKP document id (e.g. 10608) or a https://nkp.gov.np/full_detail/… URL.")
            raw = m[1]
        m = _DEC_NO.match(raw)
        if m:
            raw = await _resolve_decision_no(m[1])
        raw = _ascii(raw)
        if not _ID.match(raw):
            raise BadRequest(f"Bad id {id!r}: use the NKP document id from search (e.g. 10608), "
                             "or a decision number as 'नि.नं. 11512'.")
        url = f"{BASE}/full_detail/{raw}"
        r = await _http.get(url)
        if r.status_code != 200 or urlsplit(str(r.url)).path.rstrip("/") != f"/full_detail/{raw}":
            if r.status_code in (200, 301, 302, 404):
                raise NotFound(f"No NKP document with id {raw}.")
            raise SourceError(_http.error("nkp.gov.np", "request failed", r.status_code), r.status_code)
        root = _root(r.text)
        h1 = root.xpath("//div[@id='decision_summary']//h1")
        body = root.xpath("//div[contains(@id,'faisala_detail')]")
        if not h1 or not body:
            raise SourceError(f"nkp.gov.np: unexpected page layout for document {raw}")
        title = _http.clean(h1[0].text_content())
        meta: dict[str, str] = {}
        ed = {(_http.clean(s.text or "").rstrip(":")): _http.clean(s.xpath("string(./strong)"))
              for s in root.xpath("//div[@id='edition-info']/span")}
        dec_no = re.search(r"निर्णय नं\.\s*([0-9०-९]+)", title)
        if ed.get("साल") and ed.get("अंक") and dec_no:
            meta["NKP citation"] = f"ने.का.प. {ed['साल']}, अङ्क {ed['अंक']}, नि.नं. {dec_no[1]}"
        for k in ("भाग", "साल", "महिना", "अंक"):
            if ed.get(k):
                meta[f"NKP {k}"] = ed[k]
        pm = root.xpath("//div[@id='decision_summary']//div[contains(@class,'post-meta')]")
        date_bs = ""
        if pm:
            mm = re.search(r"फैसला मिति\s*:?\s*([0-9०-९/।.-]+)", pm[0].text_content())
            date_bs = _bs(mm[1]) if mm else ""
        if date_bs:
            meta["फैसला मिति (वि.सं.)"] = date_bs
        for img in body[0].xpath(".//img"):
            img.drop_tree()
        text = _http.html_to_md(lxml.html.tostring(body[0], encoding="unicode"))
        lines = text.split("\n\n")
        court = COURT
        if lines and lines[0].startswith(COURT):
            court = lines[0]
        case_number = next((_http.clean(x) for x in lines[:12] if _CASE_NO.match(_http.clean(x))), "")
        if len(text) < 50:
            raise SourceError(f"nkp.gov.np: document {raw} has no text")
        return Decision(id=raw, title=title, text=text, url=url, court=court, date="",
                        case_number=case_number, metadata=meta)
