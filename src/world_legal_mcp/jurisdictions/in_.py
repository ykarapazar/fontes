"""India: Supreme Court judgments reported in the S.C.R. from the "Indian Supreme Court Judgments" AWS Open
Data bucket (an unofficial mirror of the Supreme Court's e-SCR, scr.sci.gov.in). Legislation is read from
Lexifina's record (see lexifina_countries.py), not from India Code: India Code's terms (indiacode.gov.in/info/term-of-use,
read 2026-11-05) forbid automated access and API use without the Legislative Department's written permission, and
they bind India Code, not Lexifina's published record of the Acts. The India Code reader was removed on 2026-11-27.

The module is `in_.py` because `in` is a Python keyword; the registry keys adapters by
the class attribute `code`, so the file name does not matter.

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

from .. import _http, lexifina
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError, kind_of
from ..models import Decision, DecisionHit, LawHit, Results
from ._lexifina_data import COUNTRIES
from .lexifina_countries import _Lexifina, source_for

_lex = COUNTRIES.get("in", {})   # filled in by scripts/lexifina_countries.py

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


class India(_Lexifina):
    code = "in"
    name = "India"
    languages = ("en",)
    aliases = ("india", "ind")
    via_lexifina = False        # the Supreme Court is read live; only the legislation comes from Lexifina
    _slug = _lex.get("slug", "india")
    _coverage = _lex.get("coverage", "")
    sources = (
        source_for(_lex) if _lex else Source(name="Lexifina global law record", url=lexifina.REPO,
                                             covers=("legislation",), official=False, warning=lexifina.CREDIT),
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
    min_interval = {"indian-supreme-court-judgments.s3.ap-south-1.amazonaws.com": 0.5}
    gaps = (
        "Legislation: read from Lexifina's record, not live; India Code (indiacode.gov.in) itself is not used because its terms forbid automated access without written permission",
        "Constitution: legislative.gov.in (official PDFs) answers our User-Agent with an Akamai 403; Constitute Project text is non-commercial and flags a 2024 amendment not incorporated; not built",
        "Supreme Court, unreported judgments: not in e-SCR or the AWS mirror; official sci.gov.in judgment search is behind a CAPTCHA",
        "Supreme Court full-text search: the mirror has no search index; search matches parties, citations, coram and headnote within one year",
        "High Courts (AWS Open Data, unofficial, CC BY 4.0): source exists, not built",
    )
    samples = {
        "caselaw_query": "Kesavananda Bharati 1973",
        "decision_id": "2024_10_108_125",
        "legislation_query": "Information Technology Act 2000",
        "law_id": "india/national/acts/central/acts/information-technology-act-2000",
        "provision": "sec-001",
    }

    def supports(self, method: str) -> bool:
        if kind_of(method) == "legislation":
            return lexifina.enabled() and Jurisdiction.supports(self, method)
        return Jurisdiction.supports(self, method)

    @property
    def notes(self) -> str:
        sc = ("Supreme Court: S.C.R.-reported judgments 1950 to date from an unofficial AWS Open Data "
              "mirror of e-SCR; search one year at a time (parties, citation, coram, headnote). ")
        if not lexifina.enabled():
            return sc + "Legislation: off, WLM_LEXIFINA=0 turns off Lexifina."
        return (sc + "Legislation: read through Lexifina's record (not the official publisher, not live; "
                f"India Code is not used, its terms bar automated access). What the record holds: {self._coverage}.")

    async def search_legislation(self, query, *, limit, page, filters):
        """Lexifina's phrase search ranks court judgments (in its "acts/courts" folder) above Acts, so court
        folders are dropped and an Act whose title matches the query comes first."""
        r = await super().search_legislation(query, limit=limit, page=page, filters=filters)
        r.items = [i for i in r.items if not re.search(r"/acts/(?:courts|tribunals)/", i.id)]
        if page == 1:
            found = (await lexifina.call("find_provision", query=query, jurisdiction=self._slug))["structuredContent"]
            have = {i.id for i in r.items}
            top = [LawHit(id=x["path"], title=x.get("title") or x["path"], url=lexifina.REPO)
                   for x in found.get("results", []) if x.get("kind") == "act" and x["path"] not in have]
            r.items = (top + r.items)[:limit]
            if top and r.note.startswith("None of these acts has those words in its title"):   # true of the phrase hits only
                r.note = r.note.split("not be in Lexifina's record. ", 1)[-1]
            r.total = None
        return r

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
