"""DIFC Courts (Dubai International Financial Centre): case law from difccourts.ae.

The DIFC Courts publish every judgment and order as plain HTML on their Concrete CMS
site. No API; the listing page is a server-rendered search form.
  * Search: GET /rules-decisions/judgments-orders[/<court>]?keywords=..&year=YYYY
    &ccm_paging_p=N  -> 12 results per page, newest first, no hit count.
    `keywords` searches the full text (a phrase from deep inside a judgment finds
    it; a neutral citation such as "[2026] DIFC CA 003" finds that judgment).
    An unmatched keyword gives an empty list, not the default listing.
  * Document: GET /rules-decisions/judgments-orders/<court>/<slug> -> full text in
    div.content_set_detail. Unknown slug -> HTTP 404.

Ids are the site's own path below /judgments-orders/, e.g.
"court-appeal/al-buhaira-...-2026-difc-ca-003". A full URL or a neutral citation
("[2026] DIFC CA 003") is also accepted by get_decision.

Verified 2026-11-05:
  * robots.txt (www.difccourts.ae) disallows only /menu and /videos.
  * Terms of Use (difccourts.ae/terms-of-use) allow personal, non-commercial use only
    and forbid storing, copying or redistributing content without written permission.
  * DIFC legislation (difc.ae / difc.com legal database) sits behind a Vercel
    Security Checkpoint (JS challenge, HTTP 429 to this client): no legislation methods.
  * Claim numbers are not unique ids: one case has many orders plus the judgment.
  * Small Claims Tribunal and many arbitration/CFI orders use pseudonymised party
    names (e.g. "Paul v Peyton").
"""
from __future__ import annotations

import re

import lxml.html

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, Results

HOST = "www.difccourts.ae"
BASE = f"https://{HOST}/rules-decisions/judgments-orders"
PER_PAGE = 12  # fixed by the site

_COURTS = {   # path segment -> court name
    "court-appeal": "DIFC Court of Appeal",
    "court-first-instance": "DIFC Court of First Instance",
    "arbitration": "DIFC Court of First Instance (Arbitration)",
    "technology-and-construction-division": "DIFC Court of First Instance (Technology and Construction Division)",
    "digital-economy-court": "DIFC Digital Economy Court",
    "small-claims-tribunal": "DIFC Small Claims Tribunal",
    "enforcement": "DIFC Courts (Enforcement)",
    "court-administrative-orders": "DIFC Courts (Administrative Orders)",
    "joint-judicial-committee": "Joint Judicial Committee (Dubai Courts / DIFC Courts)",
}
_COURT_ALIASES = {"ca": "court-appeal", "cfi": "court-first-instance", "arb": "arbitration",
                  "tcd": "technology-and-construction-division", "dec": "digital-economy-court",
                  "sct": "small-claims-tribunal", "enf": "enforcement",
                  "admin": "court-administrative-orders", "jjc": "joint-judicial-committee"}
_PATH = re.compile(r"^[a-z0-9-]+/[a-z0-9-]+$")
_CITATION = re.compile(r"\[(\d{4})\]\s*DIFC\s+([A-Z]{2,4})\s+(\d{1,4})", re.I)
_CLAIM = re.compile(r"\b(CA|CFI|ARB|TCD|DEC|SCT|ENF)[ -]?(\d{3})[/-](\d{4})\b")


def _doc_type(label: str) -> str:
    """'October 28, 2026  Court of Appeal - Orders' -> 'Orders'."""
    return _http.clean(label.split(" -", 1)[1]).strip(", ") if " -" in label else ""


def _case_number(*texts: str) -> str:
    for t in texts:
        m = _CLAIM.search(t or "")
        if m:
            return f"{m[1]} {m[2]}/{m[3]}"
    return ""


def _citation(title: str) -> str:
    m = _CITATION.search(title or "")
    return f"[{m[1]}] DIFC {m[2].upper()} {int(m[3]):03d}" if m else ""


def _court(path: str) -> str:
    return _COURTS.get(path.split("/", 1)[0], "DIFC Courts")


def _path_of(url: str) -> str:
    return url.split("/judgments-orders/", 1)[1].strip("/") if "/judgments-orders/" in url else ""


async def _fetch(url: str, params: dict | None = None, what: str = "page") -> str:
    r = await _http.get(url, params=params)
    if r.status_code == 404:
        raise NotFound(f"DIFC Courts has no {what} at {url}.")
    if r.status_code != 200:
        raise SourceError(_http.error("DIFC Courts", f"{what} failed", r.status_code), r.status_code)
    return r.text


def _parse_list(html: str) -> list[DecisionHit]:
    tree = lxml.html.fromstring(html)
    hits = []
    for div in tree.xpath('//div[contains(concat(" ", normalize-space(@class), " "), " each_result ")]'):
        a = div.xpath(".//h4/a")
        if not a or "/judgments-orders/" not in (a[0].get("href") or ""):
            continue
        href = a[0].get("href")
        path = _path_of(href)
        title = _http.clean(a[0].text_content())
        label = _http.clean(" ".join(p.text_content() for p in div.xpath('.//p[contains(@class,"label_small")]')))
        desc = div.xpath('.//p[contains(@class,"content_desc")]')
        snippet = ""
        if desc:
            for link in desc[0].xpath(".//a"):
                link.drop_tree()
            snippet = _http.clean(desc[0].text_content())
        hits.append(DecisionHit(
            id=path, title=title or f"DIFC Courts {path}", court=_court(path), date=_http.en_date(label),
            case_number=_case_number(title, snippet), snippet=snippet[:300],
            url=f"{BASE}/{path}"))
    return hits


class DIFC(Jurisdiction):
    code = "difc"
    name = "DIFC Courts (Dubai International Financial Centre)"
    languages = ("en",)
    aliases = ("difc courts", "difcc", "dubai international financial centre",
               "dubai international financial centre courts")
    sources = (
        Source(
            name="DIFC Courts (difccourts.ae) – Judgments & Orders",
            url=BASE,
            covers=("caselaw",),
            licence=("© DIFC Courts; Terms of Use allow personal, non-commercial use only; no "
                     "copying, storing or redistribution without express written permission"),
            commercial_use=False,  # Terms of Use 2.2(d), 2.3
            ai_use=None,           # robots.txt allows all but /menu, /videos; no AI/TDM clause in the terms
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~20 requests (2026-11)",
            terms_url="https://www.difccourts.ae/terms-of-use",
            needs_permission=True,
            warning=("The DIFC Courts' Terms of Use allow only personal, non-commercial use and forbid "
                     "storing, copying or redistributing site content without the Courts' express "
                     "written permission; explicit permission is needed for automated or hosted use."),
        ),
    )
    caselaw_filters = {
        "court": ("court-appeal (ca), court-first-instance (cfi), arbitration (arb), "
                  "technology-and-construction-division (tcd), digital-economy-court (dec), "
                  "small-claims-tribunal (sct), enforcement (enf), court-administrative-orders (admin), "
                  "joint-judicial-committee (jjc)"),
        "year": "YYYY, 2007 onwards (publication year)",
    }
    min_interval = {HOST: 1.0}
    notes = ("Case law only: DIFC Courts judgments and orders (English, common law, 2007 onwards). "
             "Ids are the site's path, e.g. court-appeal/<slug>; neutral citations like "
             "'[2026] DIFC CA 003' also work. DIFC legislation is behind a bot wall.")
    gaps = (
        "All case law is gated: Terms of Use allow 'personal, non-commercial use only'; needs the Courts' written permission",
        "DIFC laws and regulations: difc.com legal database is behind a Vercel bot check (JS challenge, HTTP 429)",
        "DIFC Courts' rules and practice directions: not researched yet",
    )
    samples = {
        "caselaw_query": "insurable interest",
        # Al Buhaira National Insurance Co v Arab War Risks Insurance Syndicate [2026] DIFC CA 003
        "decision_id": ("court-appeal/al-buhaira-national-insurance-company-v-arab-war-risks-"
                        "insurance-syndicate-2026-difc-ca-003"),
    }

    # ------------------------------------------------------------------ #
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        f = {k: str(v).strip() for k, v in (filters or {}).items() if str(v).strip()}
        url = BASE
        if "court" in f:
            c = f["court"].lower()
            c = _COURT_ALIASES.get(c, c)
            if c not in _COURTS:
                raise BadRequest(f"Unknown court {f['court']!r}. Use one of: {', '.join(_COURTS)} "
                                 f"(or short codes {', '.join(_COURT_ALIASES)}).")
            url = f"{BASE}/{c}"
        params = {"keywords": (query or "").strip()}
        if "year" in f:
            if not re.fullmatch(r"20\d{2}", f["year"]) or int(f["year"]) < 2007:
                raise BadRequest("year must be YYYY, 2007 or later.")
            params["year"] = f["year"]

        limit = max(1, min(int(limit), 2 * PER_PAGE))
        page = max(1, int(page))
        start = (page - 1) * limit
        src_page = start // PER_PAGE + 1
        skip = start % PER_PAGE
        items: list[DecisionHit] = []
        while len(items) < limit:
            p = dict(params)
            if src_page > 1:
                p.update(ccm_paging_p=src_page, ccm_order_by="ak_date", ccm_order_by_direction="desc")
            hits = _parse_list(await _fetch(url, p, "search"))
            items += hits[skip:]
            skip = 0
            if len(hits) < PER_PAGE:
                break
            src_page += 1
        return Results(items=items[:limit], total=None,
                       note="Full-text keyword search, newest first; the site gives no hit count.")

    # ------------------------------------------------------------------ #
    async def _resolve_citation(self, cite: str) -> str:
        res = await self.search_caselaw(cite, limit=PER_PAGE, page=1, filters={})
        for h in res.items:
            if _citation(h.title) == cite:
                return h.id
        raise NotFound(f"DIFC Courts has no judgment cited {cite}.")

    async def get_decision(self, id):
        ident = (id or "").strip()
        if "/judgments-orders/" in ident:
            path = _path_of(ident.split("?", 1)[0].split("#", 1)[0])
        elif _CITATION.fullmatch(ident):
            path = await self._resolve_citation(_citation(ident))
        else:
            path = ident.strip("/")
        if not _PATH.match(path):
            raise BadRequest("Give the DIFC Courts path id from search_caselaw (e.g. court-appeal/"
                             "al-buhaira-national-insurance-company-v-arab-war-risks-insurance-syndicate-"
                             "2026-difc-ca-003), its full URL, or a neutral citation like [2026] DIFC CA 003.")
        url = f"{BASE}/{path}"
        tree = lxml.html.fromstring(await _fetch(url, what="judgment or order"))
        body = tree.xpath('//div[contains(@class,"content_set_detail")]')
        if not body:
            raise SourceError(f"Error (DIFC Courts): no document body on {url}.")
        text = _http.html_to_md(lxml.html.tostring(body[0], encoding="unicode"))
        if not text:
            raise SourceError(f"Error (DIFC Courts): empty document text on {url}.")
        title = _http.clean(" ".join(tree.xpath('//div[contains(@class,"each_result")]//h4//text()')))
        label = _http.clean(" ".join(
            p.text_content() for p in tree.xpath('//div[contains(@class,"each_result")]//p[contains(@class,"label_small")]')))
        meta = {"Neutral citation": _citation(title), "Document type": _doc_type(label)}
        if ident != path:
            meta["Resolved from"] = ident
        return Decision(
            id=path,
            title=title or f"DIFC Courts {path}",
            text=text,
            url=url,
            court=_court(path),
            date=_http.en_date(label),
            case_number=_case_number(title, text[:500]),
            metadata={k: v for k, v in meta.items() if v},
        )
