"""United States, state courts: opinions of the supreme and appellate courts of all 50 states
and DC from CourtListener (Free Law Project). NON-OFFICIAL source: there is no official
source that covers state case law; each state court posts its own opinions, mostly as PDFs.

Verified 2026-11-27:
  * CourtListener is run by Free Law Project, a 501(c)(3) non-profit. Its case-law coverage
    page says it holds "over nine million legal decisions drawn from over two thousand
    courts" (wiki.free.law/c/courtlistener/help/data-coverage/case-law).
  * The v4 REST API needs a token (401 without one). Each user creates a free account and
    uses their own token: the terms (wiki.free.law/c/terms/courtlistener/...) say "Do not
    share, resell, pool, or transfer your ... API tokens" and "do not present it in a way
    that suggests Free Law Project produced, endorsed, or verified an AI-generated analysis".
    So the token comes from WLM_US_COURTLISTENER_KEY and the adapter is off without it.
  * Free accounts: "5 requests per minute, 50 requests per hour, and 125 requests per day"
    (API overview, documented); a 6th request in a minute got 429 "Expected available in
    5 seconds". _http waits out one Retry-After.
  * Search (/api/rest/v4/search/?type=o) ignores page and page_size: 20 hits per call and a
    cursor in `next`. A court id includes its child courts (court=texapp returns the
    Fort Worth Court of Appeals, txctapp2), so _COURTS lists only top-level courts.
  * One opinion cluster (= one decision) holds one or more opinions (lead, concurrence,
    dissent). /opinions/?cluster=N returns them with html_with_citations or plain_text.
    The case name, court and docket come from a search on cluster_id:N (one call, not two).
  * robots.txt on www.courtlistener.com answers 403 to non-browser clients (CloudFront);
    the API is the documented route for software.
"""
from __future__ import annotations

import os
import re
from urllib.parse import parse_qs, urlparse

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, Results

ROOT = "https://www.courtlistener.com"
API = f"{ROOT}/api/rest/v4"
ENV = "WLM_US_COURTLISTENER_KEY"
_HITS = 20          # fixed hits per search call
_MAX_ROWS = 100     # limit x page: at most 5 search calls (the free tier allows 5 a minute)
_cursors: dict = {}

# State -> top-level CourtListener court ids: every state court CourtListener files as supreme
# (S) or appellate (SA). SA also holds a few others (Delaware Chancery and Superior Court,
# Massachusetts Superior Court, Appellate Tax Board...); child courts are included. From /api/rest/v4/courts/?jurisdiction=S and SA, 2026-11-27.
_COURTS = {
    "AL": "ala alactapp alacrimapp alacivapp", "AK": "alaska alaskactapp", "AZ": "ariz arizctapp",
    "AR": "ark arkctapp", "CA": "cal calctapp calappdeptsuper", "CO": "colo coloctapp",
    "CT": "conn connappct connsuperct", "DE": "del delch delorphct delsuperct", "DC": "dc",
    "FL": "fla fladistctapp", "GA": "ga gactapp", "HI": "haw hawapp", "ID": "idaho idahoctapp",
    "IL": "ill illappct", "IN": "ind indctapp", "IA": "iowa iowactapp", "KS": "kan kanctapp",
    "KY": "ky kyctapphigh kyctapp", "LA": "la lacterrapp lactapp", "ME": "me",
    "MD": "md mdctspecapp mdch",
    "MA": "mass massappct massdistctapp masssuperct massdistct masstaxbd",
    "MI": "mich michctapp michchanct", "MN": "minn minnctapp", "MS": "miss missctapp",
    "MO": "mo moctapp", "MT": "mont", "NE": "neb nebctapp", "NV": "nev nevapp", "NH": "nh",
    "NJ": "nj njsuperctappdiv njch", "NM": "nm nmctapp",
    "NY": "ny nychanct nyoytermct nyappdiv nyappterm nyhospcommn", "NC": "nc ncctapp ncsuperct",
    "ND": "nd ndctapp", "OH": "ohio ohioctapp", "OK": "okla oklacivapp oklacrimapp",
    "OR": "or orctapp", "PA": "pa pasuperct pacommwct", "RI": "ri risuperct", "SC": "sc scctapp",
    "SD": "sd", "TN": "tenn tennctapp tenncrimapp tennsuperct", "TX": "tex texcrimapp texapp texjpml",
    "UT": "utah utahctapp", "VT": "vt vtsuperct", "VA": "va vactapp", "WA": "wash washctapp",
    "WV": "wva wvactapp", "WI": "wis wisctapp", "WY": "wyo",
}
_NAMES = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR", "california": "CA",
    "colorado": "CO", "connecticut": "CT", "delaware": "DE", "district of columbia": "DC",
    "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID", "illinois": "IL",
    "indiana": "IN", "iowa": "IA", "kansas": "KS", "kentucky": "KY", "louisiana": "LA",
    "maine": "ME", "maryland": "MD", "massachusetts": "MA", "michigan": "MI", "minnesota": "MN",
    "mississippi": "MS", "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
    "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY",
    "north carolina": "NC", "north dakota": "ND", "ohio": "OH", "oklahoma": "OK", "oregon": "OR",
    "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC", "south dakota": "SD",
    "tennessee": "TN", "texas": "TX", "utah": "UT", "vermont": "VT", "virginia": "VA",
    "washington": "WA", "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY",
}
_TYPES = {"010combined": "Opinion", "015unamimous": "Unanimous opinion", "020lead": "Lead opinion",
          "025plurality": "Plurality opinion", "030concurrence": "Concurrence",
          "035concurrenceinpart": "Concurring in part", "040dissent": "Dissent",
          "050addendum": "Addendum", "060remittitur": "Remittitur", "070rehearing": "Rehearing",
          "080onthemerits": "On the merits", "090onmotiontostrike": "On motion to strike"}


def _key() -> str:
    return os.environ.get(ENV, "").strip()


def _state(v) -> str:
    s = re.sub(r"\s+", " ", str(v or "")).strip()
    code = s.upper() if s.upper() in _COURTS else _NAMES.get(s.lower(), "")
    if not code:
        raise BadRequest("state must be a US state or DC, as a two-letter code or a name "
                         "(e.g. 'TX' or 'Texas').")
    return code


def _year(v, name: str) -> int | None:
    if v in (None, ""):
        return None
    if not re.fullmatch(r"\d{4}", str(v).strip()):
        raise BadRequest(f"{name} must be a year, YYYY.")
    return int(v)


async def _api(path: str, params: dict) -> dict:
    r = await _http.get(f"{API}/{path}", params=params, headers={"Authorization": f"Token {_key()}"})
    if r.status_code == 401:
        raise SourceError(f"CourtListener refused the token ({ENV}). Check it on your "
                          "CourtListener profile page.", 401)
    if r.status_code == 429:
        raise SourceError("CourtListener's limit for a free account is reached (5 requests a "
                          "minute, 50 an hour, 125 a day). Try again later.", 429)
    if r.status_code != 200:
        raise SourceError(f"CourtListener {path} request failed", r.status_code)
    try:
        return r.json()
    except ValueError:
        raise SourceError(f"CourtListener {path} did not answer JSON", r.status_code) from None


async def _page(params: dict, n: int) -> dict:
    """Search results page n (0-based, 20 hits each), following cursors from page 0 if needed."""
    key = tuple(sorted(params.items()))
    cursor = None
    if n:
        cursor = _cursors.get((key, n))
        if cursor is None:
            prev = await _page(params, n - 1)
            if not prev.get("next"):
                return {"count": prev.get("count"), "results": []}
            cursor = parse_qs(urlparse(prev["next"]).query).get("cursor", [""])[0]
    data = await _api("search/", {**params, **({"cursor": cursor} if cursor else {})})
    if data.get("next"):
        _http.lru_put(_cursors, (key, n + 1),
                      parse_qs(urlparse(data["next"]).query).get("cursor", [""])[0], 200)
    return data


def _hit(r: dict) -> DecisionHit:
    cites = ", ".join(r.get("citation") or [])
    return DecisionHit(
        id=str(r["cluster_id"]), title=_http.clean(r.get("caseName")) or str(r["cluster_id"]),
        court=_http.clean(r.get("court")), date=r.get("dateFiled") or "",
        case_number="; ".join(x for x in (_http.clean(r.get("docketNumber")), cites) if x),
        snippet=_http.clean(re.sub(r"<[^>]+>", "", " ".join(
            o.get("snippet") or "" for o in r.get("opinions") or [])))[:300],
        url=ROOT + (r.get("absolute_url") or f"/opinion/{r['cluster_id']}/"))


SOURCE = Source(
    "CourtListener (Free Law Project, a non-profit): opinions of state supreme and appellate courts",
    ROOT,
    covers=("caselaw",),
    licence="Court opinions are generally public domain (CourtListener terms); no licence stated "
            "for the database itself",
    commercial_use=None,
    ai_use=None,   # terms allow AI clients and agents with the user's own credentials; no opt-out
    auth=f"free key: your own CourtListener API token (env {ENV}); the terms forbid sharing it",
    rate_limit="documented: 5 requests/minute, 50/hour, 125/day per free account (API overview, "
               "2026-11); 429 with a few seconds' Retry-After on the 6th request in a minute "
               "(measured 2026-11-27)",
    terms_url="https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies",
    warning="CourtListener is a free collection of US case law (over nine million decisions, by "
            "Free Law Project's count), built by the non-profit Free Law Project from court "
            "websites and scanned reporters. It is not the courts' own publication, and Free Law "
            "Project does not produce, endorse or check your AI's analysis of it. Check the "
            "opinion against the court's copy (linked when CourtListener has one) before relying on it.",
    official=False,
    probe={"caselaw_query": "duty of care", "decision_id": "10348460",
           "filters": {"state": "TX"}},
)


class UnitedStatesStates(Jurisdiction):
    code = "us-states"
    name = "United States (state courts)"
    languages = ("en",)
    aliases = ("us states", "us-state", "state courts")
    sources = (SOURCE,)
    caselaw_filters = {
        "state": "a state or DC, two-letter code or name ('TX', 'New York'): its supreme court "
                 "and appellate courts. Default: all 50 states and DC",
        "year_from": "YYYY, filed on or after",
        "year_to": "YYYY, filed on or before",
    }
    min_interval = {"www.courtlistener.com": 1.0}
    gaps = (
        ("State statutes and codes: not in CourtListener, and not live from the legislatures. "
         "Lexifina's record (not the official publisher) has statutes for 49 states (not New Mexico), "
         "DC, American Samoa, Guam and the Northern Mariana Islands, readable with get_law_on_date "
         "and get_law_history (Arkansas: catalogue entries only; Wyoming: as enacted)"),
        ("State trial courts: mostly not published online, so mostly not covered (a few are: "
         "e.g. Delaware Chancery and Superior Court, Massachusetts Superior Court)"),
        ("Free accounts allow 5 requests a minute and 125 a day: a search is 1 request, a "
         "decision 2"),
        "Federal courts: use jurisdiction 'us' (official sources: govinfo, supremecourt.gov)",
    )
    samples = {"caselaw_query": "duty of care", "decision_id": "10348460"}

    # Off until the user's own token is set: no tool is offered and list_jurisdictions says why.
    def supports(self, method: str) -> bool:
        return bool(_key()) and super().supports(method)

    @property
    def notes(self) -> str:
        if not _key():
            return (f"Inactive: needs your own free CourtListener API token. Create an account at "
                    f"courtlistener.com and set {ENV} (see docs/KEYS.md).")
        return ("Opinions of the supreme and appellate courts of all 50 states and DC, from "
                "CourtListener (Free Law Project, non-profit; not an official source). Filter "
                "state ('TX', 'New York') narrows a search to one state; ids are CourtListener "
                "cluster ids.")

    async def search_caselaw(self, query, *, limit, page, filters):
        if not (query or "").strip():
            raise BadRequest("give search words, e.g. 'duty of care'.")
        st = _state(filters["state"]) if filters.get("state") else ""
        y_from, y_to = (_year(filters.get(k), k) for k in ("year_from", "year_to"))
        if y_from and y_to and y_from > y_to:
            raise BadRequest(f"year_from ({y_from}) is after year_to ({y_to}).")
        if limit * page > _MAX_ROWS:
            raise BadRequest(f"this search reaches only the first {_MAX_ROWS} results (limit x page "
                             f"<= {_MAX_ROWS}); narrow the query or add year_from/year_to.")
        params = {"q": query, "type": "o",
                  "court": _COURTS[st] if st else " ".join(_COURTS.values())}
        if y_from:
            params["filed_after"] = f"{y_from}-01-01"
        if y_to:
            params["filed_before"] = f"{y_to}-12-31"
        start, end = (page - 1) * limit, page * limit
        first, last = start // _HITS, (end - 1) // _HITS
        rows, total = [], None
        for n in range(first, last + 1):
            data = await _page(params, n)
            total = data.get("count", total)
            rows += [(n * _HITS + i, r) for i, r in enumerate(data.get("results") or [])]
            if not data.get("next"):
                break
        hits = [_hit(r) for i, r in rows if start <= i < end and r.get("cluster_id")]
        return Results(items=hits, total=total, note=(
            f"{st or 'All states and DC'}: supreme and appellate courts, CourtListener relevance order. Free accounts "
            "allow 5 requests a minute and 125 a day."))

    async def get_decision(self, id):
        ref = _http.clean(id)
        m = re.fullmatch(r"(?:https?://(?:www\.)?courtlistener\.com)?/?(?:opinion/)?(\d{1,12})(?:/.*)?", ref)
        if not m:
            raise BadRequest("id is a CourtListener cluster id from search_caselaw, e.g. '10348460' "
                             "(or a courtlistener.com/opinion/... link).")
        cid = m[1]
        found = (await _api("search/", {"q": f"cluster_id:{cid}", "type": "o"})).get("results") or []
        if not found:
            raise NotFound(f"no CourtListener decision with cluster id {cid}.")
        hit = found[0]
        ops = (await _api("opinions/", {"cluster": cid, "fields": "id,type,author_str,per_curiam,"
                                        "html_with_citations,plain_text,download_url"})).get("results") or []
        parts, meta = [], {}
        for o in sorted(ops, key=lambda o: o.get("type") or "999"):   # lead, concurrences, dissents
            body = _http.html_to_md(o["html_with_citations"]) if o.get("html_with_citations") \
                else (o.get("plain_text") or "").strip()
            if not body:
                continue
            head = _TYPES.get(o.get("type"), "Opinion")
            if o.get("author_str"):
                head += f", {o['author_str']}"
            elif o.get("per_curiam"):
                head += ", per curiam"
            parts.append(f"## {head}\n\n{body}" if len(ops) > 1 else body)
            if o.get("download_url") and "Court's copy" not in meta:
                meta["Court's copy"] = o["download_url"]
        if not parts:
            raise SourceError(f"CourtListener has no opinion text for cluster {cid}.", 200)
        if hit.get("citation"):
            meta["Citations"] = ", ".join(hit["citation"])
        if hit.get("status"):
            meta["Status"] = hit["status"]
        if hit.get("judge"):
            meta["Judges"] = _http.clean(hit["judge"])
        h = _hit(hit)
        return Decision(id=cid, title=h.title, text="\n\n".join(parts), url=h.url, court=h.court,
                        date=h.date, case_number=_http.clean(hit.get("docketNumber")),
                        summary=_http.clean(hit.get("syllabus")), metadata=meta)
