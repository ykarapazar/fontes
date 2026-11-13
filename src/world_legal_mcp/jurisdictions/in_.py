"""India: central and state Acts from India Code (indiacode.gov.in), via its DSpace 9.1 REST API;
Supreme Court judgments reported in the S.C.R. from the "Indian Supreme Court Judgments" AWS Open
Data bucket (an unofficial mirror of the Supreme Court's e-SCR, scr.sci.gov.in).

The module is `in_.py` because `in` is a Python keyword; the registry keys adapters by
the class attribute `code`, so the file name does not matter.

Gotchas this code encodes (verified 2026-11-05 from a UK IP):
  * indiacode.nic.in now redirects to indiacode.gov.in (Angular DSpace frontend). The old
    host answers our User-Agent with an Akamai "Access Denied"; the new REST API under
    /server/api is open and anonymous.
  * Everything is one Solr search: /discover/search/objects?query=...&dsoType=ITEM. Field
    queries work (dc.identifier.act_id:"...", dc.identifier.collection:ACT|SECTION|SCHEDULE,
    dc.identifier.state_name:CENTRAL). Page size is capped at 100.
  * One item per Act (collection ACT) and one item per section (collection SECTION), linked
    by dc.identifier.act_id. Section text is HTML in dc.identifier.section_page_note,
    amendment footnotes in dc.identifier.section_footnote. Order = dc.identifier.order_number.
  * State adaptations of central Acts are separate ACT items with the *same title* (e.g. the
    Contract Act also appears for Chhattisgarh), so search defaults to state CENTRAL.
  * SCHEDULE items carry no text in their metadata, so schedules are not in the TOC/text.
  * Plain-word ranking is weak (BNS is 3rd for "Bharatiya Nyaya Sanhita"); we boost title
    matches. The source strips apostrophes from section text ("As son" for "A's son").
  * Item URIs still say test1.indiacode.nic.in; we link to indiacode.gov.in/handle/<handle>.

Supreme Court (verified 2026-11-10):
  * Public S3 bucket indian-supreme-court-judgments (ap-south-1, anonymous). One judgment = one
    path "<year>_<SCR volume>_<first page>_<last page>", e.g. 2024_10_108_125 = [2024] 10 S.C.R. 108;
    supplementary volumes are prefixed "S_" (S_1973_1_1_1002 = Kesavananda Bharati, [1973] Supp. S.C.R. 1).
    metadata/json/year=Y/<path>.json holds the e-SCR result-row HTML (parties, citation, neutral
    citation, coram, headnote, decision date, case no.); data/pdf/year=Y/english/<path>_EN.pdf the
    judgment as reported (text layer; pre-~2000 volumes are OCR, with OCR errors).
  * No search API. metadata/tar/year=Y/metadata.tar bundles a year's JSON files (0.3-6.5 MB);
    search downloads one year's tar and matches words against parties, citations, coram and
    headnote. So search needs a year; full-text search is not possible.
  * Only judgments reported in the S.C.R. (about 35k since 1950); unreported judgments are absent.
"""
from __future__ import annotations

import datetime
import html
import io
import json
import re
import tarfile

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc, TocEntry

HOST = "https://indiacode.gov.in"
SEARCH = HOST + "/server/api/discover/search/objects"
ITEMS = HOST + "/server/api/core/items/"
PAGE_MAX = 100

_ACT_ID = re.compile(r"^AC_[A-Z0-9_-]+$")
_UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)
_NUM_OF_YEAR = re.compile(r"^(?:act\s*(?:no\.?)?\s*)?(\d+[A-Z]?)\s*(?:of|/)\s*(\d{4})$", re.I)
_PROV = re.compile(r"^(?:section|sec\.?|s\.?|§)?\s*(\d+[a-z]*)\.?$", re.I)
_SOLR_SPECIAL = re.compile(r'([+\-!(){}\[\]^"~*?:\\/]|&&|\|\|)')

_sections: dict[str, list[dict]] = {}   # act_id -> section items (ordered)
_acts: dict[str, dict] = {}             # act_id -> ACT item


def _m(item: dict, key: str) -> str:
    vals = (item.get("metadata") or {}).get(key) or []
    return str(vals[0].get("value") or "") if vals else ""


def _esc(s: str) -> str:
    return _SOLR_SPECIAL.sub(r"\\\1", s)


def _url(item: dict) -> str:
    h = item.get("handle")
    return f"{HOST}/handle/{h}" if h else f"{HOST}/items/{item.get('uuid', '')}"


def _label(raw: str) -> str:
    """'Section 10', 's. 10', '§10', '19a' -> '10' / '19A'."""
    m = _PROV.match(_http.clean(raw))
    if not m:
        raise BadRequest(f"provision must be a section number like '10', 's. 10' or "
                         f"'Section 19A', got {raw!r}")
    return m[1].upper()


async def _search(query: str, *, size: int, page0: int = 0) -> dict:
    r = await _http.get(SEARCH, params={"query": query, "size": size, "page": page0,
                                        "dsoType": "ITEM"})
    if r.status_code != 200:
        raise SourceError(_http.error("India Code", "search failed", r.status_code), r.status_code)
    try:
        return r.json()["_embedded"]["searchResult"]
    except (ValueError, KeyError):
        raise SourceError("India Code: unexpected search reply (block page?)", r.status_code)


def _objects(sr: dict) -> list[dict]:
    return [o["_embedded"]["indexableObject"] for o in (sr.get("_embedded") or {}).get("objects", [])]


async def _act(law_id: str) -> dict:
    """Resolve an India Code act_id, item uuid or 'N of YYYY' (central Act) to the ACT item."""
    lid = _http.clean(law_id)
    if lid in _acts:
        return _acts[lid]
    if _UUID.match(lid):
        r = await _http.get(ITEMS + lid.lower())
        if r.status_code == 404:
            raise NotFound(f"no India Code item {lid}")
        if r.status_code != 200:
            raise SourceError(_http.error("India Code", "item fetch failed", r.status_code), r.status_code)
        item = r.json()
        if _m(item, "dc.identifier.collection") != "ACT":
            raise BadRequest(f"{lid} is not an Act item (it is a {_m(item, 'dc.identifier.collection') or 'non-Act'} item)")
        return _http.lru_put(_acts, lid, item, 64)
    if _ACT_ID.match(lid):
        q = f'dc.identifier.act_id:"{lid}" AND dc.identifier.collection:ACT'
    elif m := _NUM_OF_YEAR.match(lid):
        q = (f'dc.identifier.act_number:"{m[1]}" AND dc.date.act_year:{m[2]} '
             f'AND dc.identifier.collection:ACT AND dc.identifier.state_name:CENTRAL')
    else:
        raise BadRequest("law id must be an India Code act id (AC_CEN_3_20_00035_187209_1523268996428), "
                         "an item uuid, or a central Act number like '9 of 1872'; "
                         "use search_legislation to find it")
    hits = _objects(await _search(q, size=5))
    if not hits:
        raise NotFound(f"no Act {lid} on India Code")
    item = hits[0]
    _http.lru_put(_acts, _m(item, "dc.identifier.act_id"), item, 64)
    return _http.lru_put(_acts, lid, item, 64)


async def _all_sections(act_id: str) -> list[dict]:
    if act_id in _sections:
        return _sections[act_id]
    q = f'dc.identifier.act_id:"{act_id}" AND dc.identifier.collection:SECTION'
    items, page0 = [], 0
    while True:
        sr = await _search(q, size=PAGE_MAX, page0=page0)
        items += _objects(sr)
        page0 += 1
        if page0 >= (sr.get("page") or {}).get("totalPages", 0):
            break
    items.sort(key=lambda it: int(_m(it, "dc.identifier.order_number") or 0))
    return _http.lru_put(_sections, act_id, items, 8)


def _section_md(it: dict) -> str:
    num = _m(it, "dc.identifier.section_number")
    head = f"## Section {num}. {_http.clean(_m(it, 'dc.title'))}".rstrip()
    body = _http.html_to_md(_m(it, "dc.identifier.section_page_note"))
    notes = _http.html_to_md(_m(it, "dc.identifier.section_footnote"))
    out = [head, body]
    if notes:
        out.append("Footnotes:\n\n" + notes)
    return "\n\n".join(p for p in out if p)


# --------------------------------------------------------------------------- #
# Supreme Court: AWS Open Data mirror of e-SCR
# --------------------------------------------------------------------------- #
SC_BUCKET = "https://indian-supreme-court-judgments.s3.ap-south-1.amazonaws.com"
_SC_PATH = re.compile(r"^(?:S_)?((?:19[5-9]|20\d)\d)_(\d{1,2})_(\d+)_(\d+)$")
_SC_SCR = re.compile(r"^\[?((?:19[5-9]|20\d)\d)\]?\s*(Supp\.?\s*)?(\d{1,2})?\s*S\.?\s*C\.?\s*R\.?\s*(\d+)$", re.I)
_SC_NC = re.compile(r"^((?:19[5-9]|20\d)\d)\s*INSC\s*(\d+)$", re.I)
_SC_SINCE = re.compile(r"\b(since|from|after)\s+((?:19[5-9]|20\d)\d)\b", re.I)
_SC_YEAR = re.compile(r"\b((?:19[5-9]|20\d)\d)\b")
SC_MAX_YEARS = 5
_SC_STOP = frozenset("v vs versus a an the of to in on for and or by with at as is".split())
_sc_years: dict[str, list[dict]] = {}   # year -> parsed metadata rows


def _sc_field(h: str, label: str) -> str:
    m = re.search(label + r"\s*:\s*</span>\s*<font[^>]*>(.*?)</font>", h, re.S)
    return _http.clean(html.unescape(re.sub(r"<[^>]+>", " ", m[1]))) if m else ""


def _sc_meta(d: dict) -> dict:
    """Parse one e-SCR result row (metadata JSON) into plain fields."""
    h, path = d.get("raw_html") or "", d.get("path") or ""
    strip = lambda x: _http.clean(html.unescape(re.sub(r"<[^>]+>", " ", x or "")))
    title = re.search(r"aria-label=\"(.*?)\s*pdf\"", h, re.S)
    scr = re.search(r"class='escrText'>(.*?)</span>", h, re.S)
    nc = re.search(r"class='ncDisplay'>(.*?)</span>", h, re.S)
    coram = re.search(r"Coram\s*:(.*?)</strong>", h, re.S)
    head = re.search(r"Coram\s*:.*?</strong>\s*<br>(.*?)<br>\s*<strong class='caseDetailsTD'", h, re.S)
    return {
        "path": path,
        "year": _sc_y(path),
        "title": strip(title[1]) if title else "",
        "scr": strip(scr[1]) if scr else "",
        "nc": strip(nc[1]) if nc else "",
        "coram": strip(re.sub(r"<sup.*?</sup>", "*", coram[1], flags=re.S)) if coram else "",
        "headnote": strip(head[1]) if head else "",
        "date": _http.iso_date(_sc_field(h, "Decision Date")),
        "case_number": _sc_field(h, "Case No"),
        "disposal": _sc_field(h, "Disposal Nature"),
        "bench": _sc_field(h, "Bench"),
    }


def _sc_y(path: str) -> str:
    """Year of a dataset path; supplementary volumes are prefixed 'S_' (S_1973_1_1_1002)."""
    return path.removeprefix("S_")[:4]


def _sc_pdf_url(path: str) -> str:
    return f"{SC_BUCKET}/data/pdf/year={_sc_y(path)}/english/{path}_EN.pdf"


async def _sc_year(year: str) -> list[dict]:
    """All reported judgments of one year (one metadata.tar download, kept in memory)."""
    if year in _sc_years:
        return _sc_years[year]
    r = await _http.get(f"{SC_BUCKET}/metadata/tar/year={year}/metadata.tar")
    if r.status_code in (403, 404):
        raise NotFound(f"no Supreme Court judgments for {year} in the dataset (it covers 1950 to date)")
    if r.status_code != 200:
        raise SourceError(_http.error("SC judgments (AWS)", "metadata fetch failed", r.status_code), r.status_code)
    rows = []
    with tarfile.open(fileobj=io.BytesIO(r.content)) as tf:
        for m in tf.getmembers():
            if m.isfile() and m.name.endswith(".json"):
                try:
                    rows.append(_sc_meta(json.load(tf.extractfile(m))))
                except ValueError:
                    continue
    rows.sort(key=lambda x: (x["date"], x["path"]))
    return _http.lru_put(_sc_years, year, rows, SC_MAX_YEARS)


async def _sc_path(id: str) -> str:
    """Resolve a dataset path, an S.C.R. citation or a neutral citation to the dataset path."""
    i = _http.clean(id)
    if m := _SC_PATH.match(i):
        return i
    if m := _SC_SCR.match(i):
        supp = "S_" if m[2] else ""
        prefix = f"data/pdf/year={m[1]}/english/{supp}{m[1]}_{int(m[3] or 1)}_{int(m[4])}_"
        r = await _http.get(SC_BUCKET + "/", params={"list-type": "2", "prefix": prefix, "max-keys": "5"})
        if r.status_code != 200:
            raise SourceError(_http.error("SC judgments (AWS)", "listing failed", r.status_code), r.status_code)
        keys = re.findall(r"<Key>[^<]*/((?:S_)?\d{4}_\d+_\d+_\d+)_EN\.pdf</Key>", r.text)
        if not keys:
            raise NotFound(f"no judgment starting at {i} in the dataset")
        return keys[0]
    if m := _SC_NC.match(i):
        want = f"{m[1]} INSC {int(m[2])}"
        hit = next((x for x in await _sc_year(m[1]) if x["nc"].upper() == want), None)
        if hit is None:
            raise NotFound(f"no reported judgment {want} in the dataset (only S.C.R.-reported judgments are included)")
        return hit["path"]
    raise BadRequest("Supreme Court id must be a dataset path like '2024_10_108_125', an S.C.R. "
                     "citation like '[2024] 10 SCR 108' or '[1973] Supp. SCR 1', or a neutral citation like '2024 INSC 735'")


class India(Jurisdiction):
    code = "in"
    name = "India"
    languages = ("en",)
    aliases = ("india", "ind")
    sources = (
        Source(
            name="India Code (Legislative Department, Ministry of Law and Justice; run by NIC)",
            url="https://indiacode.gov.in/",
            covers=("legislation",),
            licence=("restrictive (Term of Use + Copyright Policy, both 'Last updated June 22, "
                     "2026', read 2026-11-05 from the site's JS bundle): personal, non-commercial "
                     "use only; 'Not use any automated means to access the Portal for any purpose "
                     "without our express written permission'; 'Use of API data requires written "
                     "authorization'; 'Data obtained through APIs must not be cached, stored, or "
                     "redistributed without permission'. No written permission held. Whether "
                     "s. 52(1)(q) Copyright Act 1957 overrides this for the Acts: unverified"),
            commercial_use=False,
            ai_use=False,
            auth=("none technically (anonymous REST API), but the terms require written "
                  "authorization from the Legislative Department for API/automated use"),
            rate_limit=("unknown; 1 s spacing, no 429 seen in ~25 requests (2026-11-05). "
                        "robots.txt returns HTTP 500 (no rules served)"),
            terms_url="https://indiacode.gov.in/info/term-of-use",
            needs_permission=True,
            warning=("India Code's terms forbid automated access and API use without the "
                     "Legislative Department's express written permission, and allow personal, "
                     "non-commercial use only. Use this source only if you hold that permission. "
                     "Without it, read the Act text by hand on indiacode.gov.in (search the "
                     "Act's title; the terms allow personal, non-commercial use) and cite "
                     "the section there; this tool cannot fetch it."),
        ),
        Source(
            name="Indian Supreme Court Judgments (AWS Open Data; Dattam Labs mirror of the Supreme Court's e-SCR)",
            url="https://registry.opendata.aws/indian-supreme-court-judgments/",
            covers=("caselaw",),
            licence=("dataset CC BY 4.0 (AWS Open Data registry, read 2026-11-10); the judgments "
                     "themselves are not copyright-protected for reproduction (s. 52(1)(q)(iv) "
                     "Copyright Act 1957); attribute the Supreme Court of India / e-SCR"),
            commercial_use=True,
            ai_use=True,
            auth="none (public S3 bucket, no AWS account)",
            rate_limit="none documented (Amazon S3); 0.5 s spacing, no 429/503 seen in ~30 requests (2026-11-10)",
            terms_url="https://registry.opendata.aws/indian-supreme-court-judgments/",
            official=False,
            warning="S.C.R.-reported judgments only; the official copy is at scr.sci.gov.in.",
        ),
    )
    caselaw_filters = {
        "year": ("S.C.R. year, 1950 to date, or a range like 2022-2024 / 2022- (up to 5 years; default "
                 "is the latest 5 years)"),
    }
    legislation_filters = {
        "state": "CENTRAL (default), a state name as India Code spells it (e.g. 'Maharashtra'), or 'all'",
        "year": "Act year, e.g. 2023",
    }
    min_interval = {"indiacode.gov.in": 1.0, "indian-supreme-court-judgments.s3.ap-south-1.amazonaws.com": 0.5}
    notes = ("Central and state Acts from India Code, section by section (off unless WLM_PERMITTED). "
             "Law ids are India Code act ids (AC_CEN_...), or '9 of 1872' for central Acts. "
             "Supreme Court: S.C.R.-reported judgments 1950 to date from an unofficial AWS Open Data "
             "mirror of e-SCR; search one year at a time (parties, citation, coram, headnote).")
    gaps = (
        "Legislation (India Code, all Acts): terms forbid automated use ('Not use any automated means'); needs written permission",
        "Constitution: legislative.gov.in (official PDFs) answers our User-Agent with an Akamai 403; Constitute Project text is non-commercial and flags a 2024 amendment not incorporated; not built",
        "Supreme Court, unreported judgments: not in e-SCR or the AWS mirror; official sci.gov.in judgment search is behind a CAPTCHA",
        "Supreme Court full-text search: the mirror has no search index; search matches parties, citations, coram and headnote within one year",
        "High Courts (AWS Open Data, unofficial, CC BY 4.0): source exists, not built",
        "Schedules of Acts: not published online as text in India Code's API (SCHEDULE items carry no text)",
        "Subordinate legislation (rules, regulations, notifications): not researched yet",
    )
    samples = {
        "caselaw_query": "Kesavananda Bharati 1973",
        "decision_id": "2024_10_108_125",
        "legislation_query": "Indian Contract Act",
        "law_id": "AC_CEN_3_20_00035_187209_1523268996428",
        "provision": "10",
    }

    async def search_caselaw(self, query, *, limit, page, filters):
        q = _http.clean(query)
        if not q:
            raise BadRequest("query is empty")
        if _SC_PATH.match(q) or _SC_SCR.match(q) or _SC_NC.match(q):
            d = await self.get_decision(q)
            return Results([DecisionHit(id=d.id, title=d.title, court=d.court, date=d.date,
                                        case_number=d.case_number, snippet=d.summary[:300],
                                        url=d.url)], total=1)
        year = str(filters.get("year") or "").strip()
        years: list[str] = []
        default_span = ""
        if year:
            m = re.fullmatch(r"((?:19[5-9]|20\d)\d)\s*(?:-|\u2013|to)\s*((?:19[5-9]|20\d)\d)?", year)
            if m:
                y0, y1 = int(m[1]), int(m[2] or datetime.date.today().year)
                if y1 < y0 or y1 - y0 + 1 > SC_MAX_YEARS:
                    raise BadRequest(f"year range must run forward and cover at most {SC_MAX_YEARS} years "
                                     f"(each year is a separate download), got {year!r}")
                years = [str(y) for y in range(y0, y1 + 1)]
            elif re.fullmatch(r"(19[5-9]|20\d)\d", year):
                years = [year]
            else:
                raise BadRequest(f"year must be four digits from 1950, like 2024, or a range like "
                                 f"2022-2024 (at most {SC_MAX_YEARS} years), got {year!r}")
        elif m := _SC_SINCE.search(q):
            y0 = int(m[2]) + (m[1].lower() == "after")
            y1 = datetime.date.today().year
            if y1 - y0 + 1 > SC_MAX_YEARS:
                raise BadRequest(f"'{m[0]}' spans {y1 - y0 + 1} years; search covers at most {SC_MAX_YEARS} "
                                 f"years at a time (each year is a separate download). Use filter year, "
                                 f"e.g. year={max(y0, y1 - SC_MAX_YEARS + 1)}-{y1}")
            years = [str(y) for y in range(y0, y1 + 1)]
            q = _http.clean(q[:m.start()] + q[m.end():])
        else:
            m = _SC_YEAR.search(q)
            if m:
                years = [m[1]]
                q = _http.clean(q[:m.start()] + q[m.end():])
            else:
                y1 = datetime.date.today().year
                years = [str(y) for y in range(y1 - SC_MAX_YEARS + 1, y1 + 1)]
                default_span = (f" No year given, so only the latest {SC_MAX_YEARS} years ({years[0]}-{years[-1]}) "
                                f"were searched; set filter year=YYYY-YYYY (up to {SC_MAX_YEARS} years) for other periods.")
        words = [w for w in re.findall(r"\w+", q.lower()) if w not in _SC_STOP]
        rows = [r for y in years for r in await _sc_year(y)]
        hay = [" ".join((r["title"], r["scr"], r["nc"], r["coram"], r["case_number"], r["headnote"])).lower()
               for r in rows]
        score = [sum(bool(re.search(r"\b" + re.escape(w) + r"\b", h)) for w in words) for h in hay]
        hits = [r for r, n in zip(rows, score) if n == len(words)]
        partial = ""
        if not hits and len(words) > 1:
            best = max(score, default=0)
            if best:
                hits = [r for r, n in zip(rows, score) if n == best]
                partial = (f" No judgment contains all of {', '.join(words)}; showing the {len(hits)} "
                           f"matching {best} of the {len(words)} words. Try fewer or different words.")
        span = years[0] if len(years) == 1 else f"{years[0]}-{years[-1]}"
        size = max(1, int(limit))
        start = (max(1, int(page)) - 1) * size
        items = [DecisionHit(id=r["path"], title=r["title"] or f"Supreme Court {r['scr']}",
                             court="Supreme Court of India", date=r["date"],
                             case_number=r["case_number"], snippet=r["headnote"][:300],
                             url=_sc_pdf_url(r["path"]))
                 for r in hits[start:start + size]]
        return Results(items, total=len(hits),
                       note=(f"S.C.R.-reported judgments of {span} only, matched on whole words in parties, "
                             f"citations, coram and headnote (no full-text search; a judgment can discuss "
                             f"a point its headnote does not mention). Unofficial mirror of e-SCR." + partial + default_span))

    async def get_decision(self, id):
        path = await _sc_path(id)
        r = await _http.get(f"{SC_BUCKET}/metadata/json/year={_sc_y(path)}/{path}.json")
        if r.status_code in (403, 404):
            raise NotFound(f"no judgment {path} in the dataset")
        if r.status_code != 200:
            raise SourceError(_http.error("SC judgments (AWS)", "metadata fetch failed", r.status_code), r.status_code)
        try:
            meta = _sc_meta(r.json())
        except ValueError:
            raise SourceError("SC judgments (AWS): unexpected metadata reply", r.status_code)
        url = _sc_pdf_url(path)
        p = await _http.get(url)
        if p.status_code in (403, 404):
            raise NotFound(f"no English text for {path} in the dataset")
        if p.status_code != 200:
            raise SourceError(_http.error("SC judgments (AWS)", "PDF fetch failed", p.status_code), p.status_code)
        text = _http.pdf_text(p.content)
        if not text:
            raise SourceError(f"SC judgments (AWS): {path} PDF has no text layer")
        md = {k: v for k, v in {
            "S.C.R. citation": meta["scr"], "Neutral citation": meta["nc"], "Coram": meta["coram"],
            "Disposal": meta["disposal"], "Bench": meta["bench"],
            "Note": "Unofficial mirror of the Supreme Court's e-SCR (AWS Open Data, CC BY 4.0).",
        }.items() if v}
        return Decision(id=path, title=meta["title"] or f"Supreme Court {meta['scr'] or path}",
                        text=text, url=url, court="Supreme Court of India", date=meta["date"],
                        case_number=meta["case_number"], summary=meta["headnote"], metadata=md)

    async def search_legislation(self, query, *, limit, page, filters):
        q = _http.clean(query)
        if not q:
            raise BadRequest("query is empty")
        words = _esc(q)
        parts = [f"(dc.title:({words})^10 OR ({words}))", "dc.identifier.collection:ACT"]
        state = _http.clean(filters.get("state", "CENTRAL"))
        if state.lower() != "all":
            if not re.fullmatch(r"[A-Za-z &.-]+", state):
                raise BadRequest(f"state must be CENTRAL, a state name or 'all', got {state!r}")
            parts.append(f'dc.identifier.state_name:"{state.upper() if state.lower() == "central" else state}"')
        if filters.get("year"):
            y = str(filters["year"]).strip()
            if not re.fullmatch(r"\d{4}", y):
                raise BadRequest(f"year must be four digits like 2023, got {y!r}")
            parts.append(f"dc.date.act_year:{y}")
        size = max(1, min(int(limit), PAGE_MAX))
        sr = await _search(" AND ".join(parts), size=size, page0=max(0, int(page) - 1))
        items = []
        for o in (sr.get("_embedded") or {}).get("objects", []):
            it = o["_embedded"]["indexableObject"]
            hl = next(iter((o.get("hitHighlights") or {}).values()), [])
            num, year = _m(it, "dc.identifier.act_number"), _m(it, "dc.date.act_year")
            st = _m(it, "dc.identifier.state_name")
            items.append(LawHit(
                id=_m(it, "dc.identifier.act_id") or it["uuid"],
                title=_http.clean(_m(it, "dc.title")),
                type="Central Act" if st == "CENTRAL" else f"{st} Act".strip(),
                number=f"{num} of {year}" if num and year else num,
                date=_http.iso_date(_m(it, "dc.date.enact_date")),
                status="repealed" if _m(it, "dc.identifier.repealed") == "true" else "not repealed",
                snippet=_http.clean(re.sub(r"</?em>", "", hl[0]))[:300] if hl else "",
                url=_url(it),
            ))
        return Results(items, total=(sr.get("page") or {}).get("totalElements"),
                       note="Defaults to central Acts (state=CENTRAL); use state='all' for state Acts too.")

    async def get_legislation_toc(self, id):
        act = await _act(id)
        act_id = _m(act, "dc.identifier.act_id")
        entries = [TocEntry(f"Section {n}. {_http.clean(_m(it, 'dc.title'))}", 0, n)
                   for it in await _all_sections(act_id)
                   if (n := _m(it, "dc.identifier.section_number"))]
        if not entries:
            raise NotFound(f"India Code has no section-level text for {act_id}")
        return Toc(id=act_id, title=_http.clean(_m(act, "dc.title")), url=_url(act), entries=entries)

    async def get_legislation_provision(self, id, provision):
        label = _label(provision)
        act = await _act(id)
        act_id = _m(act, "dc.identifier.act_id")
        if act_id in _sections:
            cands = _sections[act_id]
        else:
            cands = _objects(await _search(
                f'dc.identifier.act_id:"{act_id}" AND dc.identifier.collection:SECTION '
                f'AND dc.identifier.section_number:"{label}"', size=10))
        hit = next((it for it in cands
                    if _m(it, "dc.identifier.section_number").upper() == label), None)
        if hit is None:
            raise NotFound(f"no section {label} in {_m(act, 'dc.title') or act_id}")
        return Provision(law_id=act_id, law_title=_http.clean(_m(act, "dc.title")),
                         provision=label, text=_section_md(hit), url=_url(hit))

    async def get_legislation_text(self, id):
        act = await _act(id)
        act_id = _m(act, "dc.identifier.act_id")
        secs = await _all_sections(act_id)
        if not secs:
            raise NotFound(f"India Code has no section-level text for {act_id}")
        title = _http.clean(_m(act, "dc.title"))
        preamble = _http.html_to_md(_m(act, "dc.identifier.preamble_description"))
        text = "\n\n".join([f"# {title}", preamble] + [_section_md(it) for it in secs])
        meta = {k: v for k, v in {
            "Act number": _m(act, "dc.identifier.act_number"),
            "Enactment date": _http.iso_date(_m(act, "dc.date.enact_date")),
            "Enforcement date": _http.iso_date(_m(act, "dc.date.enforcement_date")),
            "Ministry": _m(act, "dc.identifier.ministry_name"),
            "Department": _m(act, "dc.identifier.department_name"),
            "State": _m(act, "dc.identifier.state_name"),
            "Repealed": _m(act, "dc.identifier.repealed"),
            "Note": "Assembled from India Code's per-section records; schedules are not included.",
        }.items() if v}
        return LawText(id=act_id, title=title, text=text, url=_url(act), metadata=meta)
