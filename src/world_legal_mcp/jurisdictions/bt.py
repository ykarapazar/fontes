"""Bhutan: Acts and international conventions from the Depository of Laws
(legislation.gov.bt), the official law portal linked from the Office of the Attorney
General (oag.gov.bt). English text; the Dzongkha text sits beside it at the source.

How the site works (verified 2026-11-06 from a UK IP, honest User-Agent):
  * legislation.gov.bt is an Angular app; it reads a JSON API at www.legislation.gov.bt/api.
    Public (no-login) endpoints live under /p/…; everything else answers 403
    "Forbidden resource" (admin, Bearer token) and is not used.
  * Catalogue: GET /p/legislations/current | /p/legislations/repealed | /p/conventions
    ?limit=500&page=1 -> {"data": [...], "count", ...}. `count` counts joined PDF rows,
    not laws (current: count 187, 149 Acts). Amended Acts appear inside "current".
  * Title search GET /p/legislations/adv/search-title?Keywords=… ignores `page` and
    `limit` (always the first 50), so search runs locally over the cached catalogue.
  * Text: GET /p/legislation/sections/{id} -> flat list of {type, clause_eng, clause_dzo}
    with type HEADING_1 (Part/Chapter/Article), HEADING_2 (its name), SUBSECTION_H1
    (marginal heading; in amendment Acts it carries the section number itself) and
    CLAUSE (HTML; usually starts with the section number "3."). An unknown id gives [].
    The Constitution has one CLAUSE per Article, numbered 1., 2., … inside it.
  * Texts are as enacted: amendments are separate Acts (e.g. Penal Code 2004 = id 111,
    amendments 2011 = 246, 2021 = 260); the `changes` field is empty in what we saw.
  * Human page: https://legislation.gov.bt/legislations/view/{id}.
  * Lag (checked 2026-11-10): newest Acts listed are from 2023 (Civil Liability, National
    Digital Identity, Pay Revision Acts 2023); 2024-2026 Acts (e.g. Budget Appropriation
    Acts FY 2023-24 on) are missing. No /p/ endpoint for Bills or newer Acts answered (/p/bills… 404). The
    parliament sites are no fallback: nab.gov.bt serves a *.systems.gov.bt certificate and
    nationalcouncil.bt timed out. All 13 sampled Acts had section text.
  * robots.txt: 404 on legislation.gov.bt and www.legislation.gov.bt (2026-11-05/06).
    No terms of use, licence or copyright notice on the site or in the app bundle.

Not used:
  * Delegated legislation (rules/regulations; own id space under
    /p/delegated-legislation/…) and Bills: left out to keep ids unambiguous.
  * Case law: judiciary.gov.bt timed out; nab.gov.bt (National Assembly) serves a TLS
    certificate for another host name; no other official judgment source found.
"""
from __future__ import annotations

import re
import time
from urllib.parse import urlsplit

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import LawHit, LawText, Provision, Results, Toc, TocEntry

HOST = "www.legislation.gov.bt"
API = f"https://{HOST}/api"
VIEW = "https://legislation.gov.bt/legislations/view/"
CATALOGUE_TTL = 6 * 3600
_ID = re.compile(r"^\d{1,6}$")
_NUM = re.compile(r"^(\d{1,4}[A-Za-z]?)(?:\.|\s)\s*\D")
_ARTICLE = re.compile(r"^Article\s+(\d{1,3}[A-Za-z]?)$", re.I)
_STATUSES = ("enacted", "amended", "repealed")
_TYPES = ("act", "convention")
_DUP_NOTE = ("Some Acts are listed twice at the source under the same title and year (different "
             "ids, often a bilingual and an English-only copy of the same Act, not two Acts); "
             "they are marked 'duplicate listing'. Compare the texts before relying on one. ")
_cat: dict = {}
_sections: dict = {}


async def _json(path: str, params: dict | None = None):
    r = await _http.get(API + path, params=params)
    if r.status_code != 200:
        raise SourceError(_http.error("legislation.gov.bt", "request failed", r.status_code), r.status_code)
    try:
        return r.json()
    except ValueError:
        raise SourceError("legislation.gov.bt: answer was not JSON (site changed or blocked?)")


async def _catalogue() -> dict[str, dict]:
    """id -> law row, from the three public listings (about 250 rows, cached 6 h)."""
    if _cat and time.time() - _cat["at"] < CATALOGUE_TTL:
        return _cat["rows"]
    rows: dict[str, dict] = {}
    for path in ("/p/legislations/current", "/p/legislations/repealed", "/p/conventions"):
        d = await _json(path, {"limit": "500", "page": "1"})
        if not isinstance(d, dict) or not isinstance(d.get("data"), list):
            raise SourceError(f"legislation.gov.bt: unexpected listing payload from {path}")
        for x in d["data"]:
            if x.get("id") is not None and (x.get("title_eng") or "").strip():
                rows.setdefault(str(x["id"]), x)
    _cat.update(at=time.time(), rows=rows)
    return rows


def _title(x: dict) -> str:
    return _http.clean(x.get("title_eng"))


def _date(x: dict) -> str:
    return (x.get("enactmentDate") or x.get("commencementDate") or "")[:10]


def _year(x: dict) -> int:
    """Year of the Act: the source's documentYear, else the year of its date."""
    return int(x.get("documentYear") or _date(x)[:4] or 0)


def _hit(x: dict) -> LawHit:
    return LawHit(id=str(x["id"]), title=_title(x), type=x.get("type") or "",
                  date=_date(x), status=(x.get("status") or "").lower(),
                  snippet=_http.clean(x.get("title_dzo")), url=VIEW + str(x["id"]))


def _law_id(id) -> str:
    raw = _http.clean(str(id or ""))
    if raw.startswith("http"):
        u = urlsplit(raw)
        m = re.match(r"^/legislations/view/(\d+)/?$", u.path or "")
        if (u.hostname or "").lower() not in ("legislation.gov.bt", HOST) or not m:
            raise BadRequest("Give a law id from search_legislation (e.g. 111) or a "
                             "https://legislation.gov.bt/legislations/view/… URL.")
        raw = m[1]
    if not _ID.match(raw):
        raise BadRequest(f"Bad id {id!r}: use the numeric id from search_legislation, e.g. 111 "
                         "(Penal Code of Bhutan 2004).")
    return raw


async def _law(id) -> tuple[dict, list[dict]]:
    lid = _law_id(id)
    meta = (await _catalogue()).get(lid)
    if not meta:  # only catalogued ids are fetched, so a bad id costs no text download
        raise NotFound(f"No Act or convention with id {lid} in the Depository of Laws.")
    if lid not in _sections:
        d = await _json(f"/p/legislation/sections/{lid}")
        if not isinstance(d, list):
            raise SourceError(f"legislation.gov.bt: unexpected sections payload for {lid}")
        if not d:
            raise NotFound(f"The Depository of Laws has no text for id {lid} ({_title(meta)}).")
        _http.lru_put(_sections, lid, d, 8)
    return meta, _sections[lid]


def _parse(sections: list[dict]):
    """-> (toc entries, units, full text). A unit is a provision: {label, title, parts}."""
    toc: list[TocEntry] = []
    units: list[dict] = []
    seen: dict[str, dict] = {}
    full: list[str] = []
    h1 = h2 = sub = ""
    cur = None

    def start(label: str, title: str) -> dict:
        nonlocal cur
        base, k = label, 2
        while label.lower() in seen:
            label, k = f"{base} ({k})", k + 1
        cur = {"label": label, "title": title, "parts": []}
        seen[label.lower()] = cur
        units.append(cur)
        toc.append(TocEntry(title=f"{label} – {title}" if title else label, level=2, provision=label))
        return cur

    for s in sections:
        kind = s.get("type") or ""
        md = _http.html_to_md(s.get("clause_eng") or "").strip()
        if not md:
            continue
        if kind == "HEADING_1":
            h1, h2, sub, cur = md, "", "", None
            toc.append(TocEntry(title=md, level=0))
            full.append(f"## {md}")
        elif kind == "HEADING_2":
            h2, sub = md, ""
            if not _ARTICLE.match(h1):
                cur = None
            toc.append(TocEntry(title=md, level=1))
            full.append(f"### {md}")
        elif kind == "SUBSECTION_H1":
            full.append(f"#### {md}")
            m = _NUM.match(md)
            if m and not _ARTICLE.match(h1):  # amendment Acts: "2. In the Code, Section 4 … is amended"
                u = start(f"Section {m[1]}", "")
                u["parts"].append(md)
                u["amending"] = True  # quoted inserted text that follows belongs to it
                sub = ""
            elif cur and (_ARTICLE.match(h1) or cur.get("amending")):
                cur["parts"].append(f"**{md}**")
            else:
                sub, cur = md, None
        elif kind == "CLAUSE":
            full.append(md)
            art = _ARTICLE.match(h1)
            m = _NUM.match(md)
            if art:
                if not cur or cur["label"] != f"Article {art[1]}":
                    start(f"Article {art[1]}", h2)
                cur["parts"].append(md)
            elif m:
                start(f"Section {m[1]}", sub)["parts"].append(md)
                sub = ""
            elif cur:
                cur["parts"].append(md)
            else:
                start("Preamble" if not units else (h2 or h1 or "Text"), sub)["parts"].append(md)
                sub = ""
    return toc, units, "\n\n".join(full)


def _find(units: list[dict], provision: str) -> dict | None:
    p = _http.clean(provision).rstrip(".")
    by = {u["label"].lower(): u for u in units}
    m = re.match(r"^(?:s|sec|section|§)\.?\s*(\S+)$", p, re.I)
    if m:
        return by.get(f"section {m[1]}".lower())
    m = re.match(r"^(?:art|article)\.?\s*(\S+)$", p, re.I)
    if m:
        return by.get(f"article {m[1]}".lower())
    if re.fullmatch(r"\d{1,4}[A-Za-z]?", p):
        return by.get(f"section {p}".lower()) or by.get(f"article {p}".lower())
    return by.get(p.lower())


class Bhutan(Jurisdiction):
    code = "bt"
    name = "Bhutan"
    languages = ("en", "dz")
    aliases = ("bhutan", "btn", "druk yul")
    sources = (
        Source(
            name="Depository of Laws (legislation.gov.bt), Office of the Attorney General of Bhutan",
            url="https://legislation.gov.bt", covers=("legislation",),
            licence="none stated (no terms, licence or copyright notice on the site, 2026-11)",
            commercial_use=None, ai_use=None, auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~25 requests (2026-11)",
            terms_url="https://legislation.gov.bt",
        ),
    )
    legislation_filters = {
        "status": "enacted (in force, unamended), amended (in force, has amendments) or repealed",
        "type": "act or convention (international conventions Bhutan is party to)",
        "year": "year, e.g. 2022, or a range 2022-2023 (the source's document year; most Acts "
                "carry no exact date, and where there is one it is the commencement date)",
        "since": "year, e.g. 2022: Acts from that year onward (same document-year rule as year)",
    }
    min_interval = {HOST: 1.0}
    notes = ("Acts of Parliament (about 190, current and repealed) and international conventions, "
             "English text as enacted: amendments are separate Acts, not merged in. Newest Act listed "
             "is from 2023. "
             "No case law (no reachable official judgment source).")
    gaps = (
        "Case law: judiciary.gov.bt times out from the UK (2026-11-06)",
        "Delegated legislation (rules, regulations) and Bills: public API has them; not built yet",
        "Consolidated texts: not published; amendments are separate Acts at the source",
        "Acts after 2023: the Depository's newest Acts are from 2023 (title search for 2024 or "
        "2025 finds nothing, checked 2026-11-10); e.g. the Budget Appropriation Acts from FY "
        "2023-24 on are not there. No other reachable official source: nab.gov.bt (http and "
        "https redirect to a *.systems.gov.bt certificate), judiciary.gov.bt and "
        "nationalcouncil.bt time out, oag.gov.bt only links the Depository",
        "Dzongkha text of Acts: served by the source; not built yet (English only)",
    )
    samples = {"legislation_query": "penal code", "law_id": "111", "provision": "Section 3"}

    async def search_legislation(self, query, *, limit, page, filters):
        f = filters or {}
        status = _http.clean(str(f.get("status") or "")).lower()
        kind = _http.clean(str(f.get("type") or "")).lower()
        if status and status not in _STATUSES:
            raise BadRequest(f"status must be one of: {', '.join(_STATUSES)}")
        if kind and kind not in _TYPES:
            raise BadRequest(f"type must be one of: {', '.join(_TYPES)}")
        q = _http.clean(query or "").casefold()
        y = _http.clean(str(f.get("year") or ""))
        m = re.fullmatch(r"(\d{4})(?:\s*-\s*(\d{4}))?", y) if y else None
        if y and not m:
            raise BadRequest("year must be like 2022 or a range 2022-2023.")
        y1, y2 = (int(m[1]), int(m[2] or m[1])) if m else (0, 9999)
        since = _http.clean(str(f.get("since") or ""))
        if since:
            if not re.fullmatch(r"\d{4}", since):
                raise BadRequest("since must be a year like 2022.")
            y1 = max(y1, int(since))
            y = y or since
        if y and y1 > y2:
            raise BadRequest("year range must run from the earlier to the later year.")
        if not q and not (status or kind or y):
            raise BadRequest("Give words from the title (e.g. 'penal code') or a status/type/year filter.")
        words = q.split()
        rows = []
        for x in (await _catalogue()).values():
            hay = f"{_title(x)} {x.get('title_dzo') or ''}".casefold()
            if words and not all(w in hay for w in words):
                continue
            if status and (x.get("status") or "").lower() != status:
                continue
            if kind and (x.get("type") or "").lower() != kind:
                continue
            if y and not y1 <= _year(x) <= y2:
                continue
            rows.append(x)
        rows.sort(key=lambda x: (q not in _title(x).casefold(), -_year(x)))
        start = (page - 1) * limit
        titles = [_title(x).casefold() for x in rows]
        dup = _DUP_NOTE if len(set(titles)) < len(titles) else ""
        items = [_hit(x) for x in rows[start:start + limit]]
        for h, x in zip(items, rows[start:start + limit]):
            if titles.count(h.title.casefold()) > 1:
                langs = "/".join(sorted({(c.get("language") or "?") for c in x.get("documentCopies") or []}))
                h.title += f" [duplicate listing, id {h.id}" + (f", copy: {langs}" if langs else "") + "]"
        return Results(items=items, total=len(rows),
                       note=dup + "Title search; texts are as enacted (amendments are separate Acts). "
                            "A Date line, where shown, is the source's commencement date (not "
                            "assent or publication), and it can fall years after the Act's own "
                            "year; most Acts have no date in the source at all. The year filter "
                            "uses the source's document year (not a legal date). For the "
                            "commencement of an Act without a Date, read its commencement "
                            "section with get_legislation_provision. The newest Acts in the source are from "
                            "2023: nothing from 2024 onward is covered, so absence here does not "
                            "mean no such Act exists.")

    async def get_legislation_toc(self, id):
        meta, secs = await _law(id)
        toc, _, _ = _parse(secs)
        return Toc(id=str(meta["id"]), title=_title(meta), url=VIEW + str(meta["id"]), entries=toc)

    async def get_legislation_provision(self, id, provision):
        meta, secs = await _law(id)
        _, units, _ = _parse(secs)
        u = _find(units, provision)
        if not u:
            some = ", ".join(x["label"] for x in units[:8])
            raise NotFound(f"No provision {provision!r} in {_title(meta)}. Labels look like: {some}…")
        head = f"## {u['label']}" + (f" – {u['title']}" if u["title"] else "")
        return Provision(law_id=str(meta["id"]), law_title=_title(meta), provision=u["label"],
                         text=head + "\n\n" + "\n\n".join(u["parts"]), url=VIEW + str(meta["id"]))

    async def get_legislation_text(self, id):
        meta, secs = await _law(id)
        _, _, text = _parse(secs)
        md = {"Status": (meta.get("status") or "").lower(), "Type": meta.get("type") or "",
              "Title (Dzongkha)": _http.clean(meta.get("title_dzo")),
              "Version": "as enacted; later amendments are separate Acts"}
        if _date(meta):
            md["Commencement date"] = _date(meta)
        if meta.get("repealDate"):
            md["Repealed"] = meta["repealDate"][:10]
        return LawText(id=str(meta["id"]), title=_title(meta), text=text, url=VIEW + str(meta["id"]),
                       metadata={k: v for k, v in md.items() if v})
