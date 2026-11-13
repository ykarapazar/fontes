"""Norway: Supreme Court (Høyesterett) decision pages from domstol.no. No legislation.

What is and is not here (verified 2026-11-05, our honest User-Agent, UK IP):
  * Legislation and most case law live on Lovdata. lovdata.no/robots.txt ends with
    `User-agent: * / Disallow: /`, and api.lovdata.no/robots.txt is `User-agent: * /
    Disallow: /` too, so the free NLOD bulk files (api.lovdata.no/v1/publicData/...) and the
    website are both off limits for an automated client. The per-document Lovdata API is
    paid. Result: no legislation, and no lower-court case law.
  * domstol.no (Domstoladministrasjonen) publishes one page per Supreme Court decision under
    /no/hoyesterett/avgjorelser/{year}/{category}/{slug}/ (about 6,300 pages, 2000 to today).
    Each page holds the court's own intro (date, HR number, case number, parties) and a
    summary; the full judgment is a PDF under /globalassets/, which robots.txt disallows.
    So get_decision returns the official summary page, not the full judgment, and links the PDF.
  * The site is an Optimizely (EPiServer) SPA. Pages are server-rendered with the content as
    JSON in `__INITIAL__DATA__ = {...}` (IContent.Name / MainIntro / MainBody). The decision
    lists and site search are filled client-side from /api and /Util, both disallowed by
    robots.txt. The allowed index is /sitemap.xml (~2.7 MB, every decision URL), so search
    matches the query against URL slugs: 2000-2006 and 2008-2021 slugs are descriptive
    titles ("foretaksstraff"), 2007 and 2022+ slugs are only the HR number. The sitemap is
    held in memory for a few hours; each returned hit costs one page fetch for title/date.
  * Ids: the HR number (e.g. HR-2026-2227-A) when the URL carries it, else the URL path after
    /avgjorelser/ (e.g. 2015/hoyesterett-straff/foretaksstraff). 2011-2016 HR numbers are
    zero-padded in places (HR-2015-02557-A); lookups ignore the padding.
"""
from __future__ import annotations

import json
import re
import time

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, Results

HOST = "https://www.domstol.no"
BASE = f"{HOST}/no/hoyesterett/avgjorelser/"
SITEMAP = f"{HOST}/sitemap.xml"
_HR = re.compile(r"\b(?:HR-)?(\d{4})-0*(\d+)-([A-Z])\b", re.I)
_SITEMAP_TTL = 6 * 3600
_MONTHS = {m: i for i, m in enumerate(
    ("januar", "februar", "mars", "april", "mai", "juni", "juli", "august", "september",
     "oktober", "november", "desember"), 1)}
_index: dict = {}       # "at", "entries": list of (path, year, category, slug)
_pages: dict = {}       # path -> parsed page (small LRU)


def _fold(s: str) -> str:
    s = s.lower().replace("æ", "ae").replace("ø", "o").replace("å", "a")
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def _hr_key(s: str) -> str | None:
    m = _HR.search(s or "")
    return f"HR-{m[1]}-{int(m[2])}-{m[3].upper()}" if m else None


def _court(category: str) -> str:
    c = category.lower()
    if "ankeutvalg" in c or "kjaremal" in c:
        return "Høyesteretts ankeutvalg"
    return "Høyesterett"


def _area(category: str) -> str:
    c = category.lower()
    return "straff" if "straff" in c else "sivil" if "sivil" in c else ""


async def _entries() -> list[tuple[str, str, str, str]]:
    if _index.get("entries") and time.monotonic() - _index["at"] < _SITEMAP_TTL:
        return _index["entries"]
    r = await _http.get(SITEMAP)
    if r.status_code != 200 or "<urlset" not in r.text[:500]:
        raise SourceError(_http.error("domstol.no", "sitemap unavailable", r.status_code), r.status_code)
    out = []
    for loc in re.findall(r"<loc>\s*([^<]+?)\s*</loc>", r.text):
        if not loc.startswith(BASE):
            continue
        parts = loc[len(BASE):].strip("/").split("/")
        if len(parts) != 3:
            continue
        m = re.fullmatch(r"(?:avgjorelser-)?(\d{4})", parts[0])
        if m:
            out.append(("/".join(parts), m[1], parts[1], parts[2]))
    if not out:
        raise SourceError("domstol.no sitemap has no Supreme Court decision URLs (layout changed?)")
    out.sort(key=lambda e: (e[1], int(_HR.search(e[3])[2]) if _HR.search(e[3]) else 0), reverse=True)
    _index.update(at=time.monotonic(), entries=out)
    return out


def _id(path: str) -> str:
    slug = path.rsplit("/", 1)[-1]
    return slug.upper() if _HR.fullmatch(slug) else path


async def _resolve(id: str) -> str:
    s = re.sub(r"^https?://(www\.)?domstol\.no/no/hoyesterett/avgjorelser/", "", (id or "").strip(), flags=re.I)
    s = s.split("?")[0].strip("/")
    if not s:
        raise BadRequest("Give a decision id from search_caselaw, e.g. 'HR-2026-2227-A' or "
                         "'2015/hoyesterett-straff/foretaksstraff', or a domstol.no decision URL.")
    key = _hr_key(s) if _HR.fullmatch(s) else None
    for path, *_ in await _entries():
        if key and _hr_key(path.rsplit("/", 1)[-1]) == key:
            return path
        if not key and path.lower() == s.lower():
            return path
    if key:
        # A few pages of every year are filed under a title slug: look them up by the HR number
        # on the page itself (only when the year has few of them).
        cands = [p for p, y, _c, sl in await _entries() if y == key.split("-")[1] and not _num_slug(sl)]
        if len(cands) <= 12:
            for path in cands:
                try:
                    if _hr_key((await _page(path))["hr"]) == key:
                        return path
                except (NotFound, SourceError):
                    continue
        raise NotFound(f"{s} has no page of its own on domstol.no (older pages are filed under a "
                       f"title slug; search_caselaw with words from the subject, or a year filter).")
    raise NotFound(f"No domstol.no Supreme Court decision page at {s!r}.")


def _num_slug(slug: str) -> bool:
    return bool(re.fullmatch(r"(?:HR-)?\d{4}-0*\d+-[A-Z]", slug, re.I))


def _date(intro: str) -> str:
    m = re.search(r"(\d{1,2})\.\s*([a-zæøå]+)\s+(\d{4})", intro, re.I)
    if m and m[2].lower() in _MONTHS:
        return f"{m[3]}-{_MONTHS[m[2].lower()]:02d}-{int(m[1]):02d}"
    m = re.search(r"\b(\d{1,2}\.\d{1,2}\.\d{4})\b", intro)
    return _http.iso_date(m[1]) if m else ""


async def _page(path: str) -> dict:
    if path in _pages:
        return _pages[path]
    url = BASE + path + "/"
    r = await _http.get(url)
    if r.status_code == 404:
        raise NotFound(f"No domstol.no decision page at {path!r}.")
    if r.status_code != 200:
        raise SourceError(_http.error("domstol.no", "decision page failed", r.status_code), r.status_code)
    i = r.text.rfind("__INITIAL__DATA__ = ")
    try:
        data, _ = json.JSONDecoder().raw_decode(r.text[i + len("__INITIAL__DATA__ = "):])
        c = data["IContent"]
    except (ValueError, KeyError, TypeError):
        raise SourceError("domstol.no page has no content JSON (layout changed?)", r.status_code) from None
    intro_html = (c.get("MainIntro") or {}).get("Value") or ""
    body_html = (c.get("MainBody") or {}).get("Value") or ""
    pdf = re.search(r'href="([^"]+\.pdf)"', body_html, re.I)
    body_html = re.sub(r"(?is)<p[^>]*>\s*<a [^>]*\.pdf[^>]*>.*?</a>\s*</p>|<a [^>]*\.pdf[^>]*>.*?</a>", "", body_html)
    intro = _http.html_to_md(intro_html)
    body = _http.html_to_md(body_html)
    m = _HR.search(intro)
    hr = m[0].upper() if m else (_id(path) if _HR.fullmatch(path.rsplit("/", 1)[-1]) else "")
    cn = re.search(r"sak\s*nr\.?\s*([\w/.-]+\w)", intro, re.I) or re.search(r"\b(\d{4}/\d+)\b", intro)
    meta = {}
    for k, v in re.findall(r"\*\*([^*:]+)\*\*\s*:?\s*([^\n]+)", body):
        meta[_http.clean(k).rstrip(":")] = _http.clean(v.lstrip(": "))
    page = dict(url=url, name=_http.clean(c.get("Name")), intro=intro, body=body, hr=hr,
                case_number=cn[1] if cn else "", date=_date(intro),
                pdf=pdf[1] if pdf else "", meta=meta)
    return _http.lru_put(_pages, path, page, 128)


def _title(p: dict) -> str:
    name, hr = p["name"], p["hr"]
    if name and hr and hr.lower() not in name.lower():
        return f"{name} ({hr})"
    return name or hr or p["url"]


class Norway(Jurisdiction):
    code = "no"
    name = "Norway"
    languages = ("nb", "nn")
    aliases = ("nor", "norway", "norge", "noreg")
    sources = (
        Source(
            name="Domstoladministrasjonen: domstol.no, Høyesterett decision pages (summaries)",
            url="https://www.domstol.no/no/hoyesterett/avgjorelser/",
            covers=("caselaw",),
            licence="Court decisions are not protected by copyright (åndsverkloven § 14); "
                    "no licence or terms page published for the summaries",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~25 requests (2026-11)",
            terms_url="https://www.domstol.no/robots.txt",
        ),
    )
    caselaw_filters = {
        "year": "decision year, e.g. 2024, or a range '2022-2024' (pages exist for 2000 to today)",
        "court": "'avdeling' (Høyesterett in chambers/plenary) or 'ankeutvalg' (Appeals Selection "
                 "Committee, incl. the old kjæremålsutvalg)",
        "area": "'sivil' or 'straff'",
    }
    min_interval = {"www.domstol.no": 1.0}
    notes = ("Supreme Court only, and only the court's own summary page per decision: the full "
             "judgment PDFs and Lovdata (all legislation and lower courts) disallow automated "
             "access in robots.txt.")
    gaps = (
        "Legislation (Lovdata, https://lovdata.no/ ; a statute is at https://lovdata.no/dokument/NL/lov/"
         "YYYY-MM-DD-NN, e.g. arbeidsmiljøloven lov/2005-06-17-62, straffeloven lov/2005-05-20-28, "
         "personopplysningsloven lov/2018-06-15-38): not fetched here, robots.txt disallows "
         "(lovdata.no and api.lovdata.no 'Disallow: /'); open those pages in a browser",
        "Appeal and district court case law (Lovdata): robots.txt disallows; the per-document API"
         " is paid",
        "Full Supreme Court judgment texts (PDFs under /globalassets/): robots.txt disallows; "
         "summary page only",
        "Supreme Court decisions before 2000: not on domstol.no; other sources not researched yet",
        "Full-text search: domstol.no /api and /Util are disallowed by robots.txt; search matches"
         " URL slugs only",
    )
    samples = {
        "caselaw_query": "foretaksstraff",
        "decision_id": "HR-2026-2227-A",
    }

    async def search_caselaw(self, query, *, limit, page, filters):
        y = filters.get("year") or ""
        if isinstance(y, (list, tuple)):
            y = f"{min(y)}-{max(y)}" if len(y) > 1 else (y[0] if y else "")
        year = str(y).strip()
        m = re.fullmatch(r"(\d{4})(?:\s*-\s*(\d{4}))?", year)
        if year and not m:
            raise BadRequest(f"year must be a four-digit year like 2024 or a range like 2022-2024, got {year!r}.")
        y_lo, y_hi = (m[1], m[2] or m[1]) if m else ("", "")
        if y_lo > y_hi:
            raise BadRequest(f"year range {year!r} runs backwards; write it as {y_hi}-{y_lo}.")
        court = str(filters.get("court") or "").strip().lower()
        if court and court not in ("avdeling", "ankeutvalg"):
            raise BadRequest(f"court must be 'avdeling' or 'ankeutvalg', got {court!r}.")
        area = str(filters.get("area") or "").strip().lower()
        if area and area not in ("sivil", "straff"):
            raise BadRequest(f"area must be 'sivil' or 'straff', got {area!r}.")
        q = (query or "").strip()
        key = _hr_key(q)
        tokens = [] if key else [t for t in _fold(q).split() if t not in ("*",)]
        hits, numbered, by_title = [], [], False
        for path, y, cat, slug in await _entries():
            if year and not y_lo <= y <= y_hi:
                continue
            if court and (court == "ankeutvalg") != (_court(cat) != "Høyesterett"):
                continue
            if area and _area(cat) != area:
                continue
            if key and _hr_key(slug) != key:
                continue
            hay = f" {_fold(slug)} {_fold(cat)} "
            if tokens and not all(t in hay for t in tokens):
                if not _num_slug(slug):
                    continue
                numbered.append((path, y, cat))
                continue
            hits.append((path, y, cat))
        if tokens and not hits and 0 < len(numbered) <= 120:
            # HR-number-only URLs carry no subject: match the words against each page's title and summary.
            for path, y, cat in numbered:
                p = await _page(path)
                if all(t in f" {_fold(p['name'] + ' ' + p['body'])} " for t in tokens):
                    hits.append((path, y, cat))
            if hits:
                tokens, by_title = [], True
        limit = max(1, int(limit))
        start = (max(1, int(page)) - 1) * limit
        items = []
        for path, y, cat in hits[start:start + limit]:
            p = await _page(path)
            snippet = next((x for x in p["body"].split("\n\n")
                            if len(x) > 80 and not re.match(r"\W*Domm(ere|arar)\b", x)), "")
            items.append(DecisionHit(
                id=_id(path), title=_title(p), court=_court(cat), date=p["date"],
                case_number=p["hr"] or p["case_number"], snippet=_http.clean(snippet)[:300],
                url=p["url"]))
        note = ("Matches words in each decision's URL (2000-2021 URLs mostly carry a subject title; "
                "2007 and 2022+ only the HR number, so list those with the year filter). "
                "Summaries only; the full judgment is a linked PDF.")
        if tokens and not hits:
            note = ("No match, but this does not mean there is no such case law. The search takes Norwegian "
                    "words, not English (for dismissal try 'oppsigelse' or 'avskjed'). Since 2022 the court's "
                    "page addresses carry only the case number, so for recent cases add a year (e.g. year "
                    "2024) and area ('sivil' for civil cases) to the search; the subject words are then "
                    "checked against each decision's title and summary. "
                    "domstol.no's own search is closed to automated clients (robots.txt).")
        elif by_title:
            note = (f"The count of {len(hits)} counts only decisions whose title or short summary contains "
                    "the words; the full judgments are not searched, so decisions that use the words only "
                    "in the judgment text are not counted. Summaries only; the full judgment is a linked PDF.")
        elif tokens and numbered:
            note = (f"The count of {len(hits)} is partial: it covers only URL-word matches. {len(numbered)} "
                    "further decisions whose URL is just a case number were not checked against their "
                    "titles or summaries, so decisions on this subject may be missing from the count. ") + note
        return Results(items, total=len(hits), note=note)

    async def get_decision(self, id):
        path = await _resolve(id)
        p = await _page(path)
        cat = path.split("/")[1]
        parts = ["*Official summary page from domstol.no. The full judgment is a PDF"
                 + (f" ({p['pdf']})" if p["pdf"] else "")
                 + ", which this tool does not fetch (robots.txt disallows it).*"]
        parts += [x for x in (p["intro"], p["body"]) if x]
        meta = dict(p["meta"])
        if p["pdf"]:
            meta["Full judgment (PDF)"] = p["pdf"]
        if p["case_number"] and p["case_number"] != p["hr"]:
            meta["Saksnummer"] = p["case_number"]
        area = _area(cat)
        if area:
            meta["Sakstype"] = area
        return Decision(id=_id(path), title=_title(p), text="\n\n".join(parts), url=p["url"],
                        court=_court(cat), date=p["date"], case_number=p["hr"] or p["case_number"],
                        metadata=meta)
