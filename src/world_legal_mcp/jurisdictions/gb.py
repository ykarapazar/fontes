"""United Kingdom: case law from Find Case Law (TNA), legislation from legislation.gov.uk.

Ported from uk-legal-mcp. Gotchas this code encodes:
  * Find Case Law's /atom.xml is full-text only: neutral citations do NOT match,
    so get_decision converts "[2026] EWHC 2093 (Ch)" -> "ewhc/ch/2026/2093" locally.
  * order=relevance is supported (default); also date / updated / transformation. The feed
    gives no hit count, only the last page number. Dates: from_date_0/1/2 (day, month, year).
  * Coverage is 2003 onward; older and many first-instance decisions are only on
    BAILII, which has no API and forbids scraping.
  * Open Justice Licence v2.0: re-use (incl. commercial) is fine; "computational
    analysis" (programmatic bulk searching to identify/extract/enrich records)
    needs a separate, free licence. API limit 1,000 req / 5 min per IP (429).
  * legislation.gov.uk: a bare provision number is requested as section/N; the
    site 303-redirects to regulation/article/rule for instruments.
  * /search/data.feed 301-redirects to /{type|all}[/{year}]/data.feed and drops `page`
    on the way, so the final URL is built directly. Order is the site's own (not by
    relevance); the feed has no hit count, but its per-type facet counts add up to it.
  * A provision's data.xml carries every annotation of its enclosing Part/Chapter too
    (CDPA s.9: 18 Part I extent orders); only the provision's own are listed in full.
  * Big Acts' /data.xml run to several MB, so parsed XML is cached in-process.
"""
from __future__ import annotations

import calendar
import re

from lxml import etree

from .._http import get, localname, text
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

CASELAW = "https://caselaw.nationalarchives.gov.uk"
LEGISLATION = "https://www.legislation.gov.uk"
_ATOM = "{http://www.w3.org/2005/Atom}"
_TNA = "{https://caselaw.nationalarchives.gov.uk}"
_AKN = "{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}"
_LEG = "{http://www.legislation.gov.uk/namespaces/legislation}"
_UKM = "{http://www.legislation.gov.uk/namespaces/metadata}"
_OS = "{http://a9.com/-/spec/opensearch/1.1/}"
_DC = "{http://purl.org/dc/elements/1.1/}"
_DCT = "{http://purl.org/dc/terms/}"

_ORDERS = {"relevance", "-date", "date", "-updated", "updated", "-transformation", "transformation"}

# "[2024] UKSC 1", "[2026] EWCA Civ 1161", "[2026] EWHC 2093 (Ch)", "[2024] UKUT 12 (AAC)"
_NCN_RE = re.compile(
    r"^\[(\d{4})\]\s+([A-Za-z]+)(?:\s+([A-Za-z]+))?\s+(\d+)(?:\s*\(([A-Za-z]+)\))?$"
)

_xml_cache: dict[str, bytes] = {}


# =========================================================================== #
# Case law — Find Case Law
# =========================================================================== #
def citation_to_slug(ref: str) -> str:
    ref = ref.strip()
    m = _NCN_RE.match(ref)
    if m:
        year, court, div1, num, div2 = m.groups()
        parts = [court.lower()]
        if div1 or div2:
            parts.append((div1 or div2).lower())
        parts += [year, num]
        return "/".join(parts)
    ref = re.sub(r"^https?://caselaw\.nationalarchives\.gov\.uk/(id/)?", "", ref)
    ref = re.sub(r"/data\.xml$", "", ref)
    return ref.strip("/")


def _date_params(name: str, value, *, end: bool) -> list[tuple[str, str]]:
    """'2022' / '2022-06' / '2022-06-15' -> the site's day/month/year form fields."""
    m = re.fullmatch(r"(\d{4})(?:-(\d{1,2})(?:-(\d{1,2}))?)?", str(value).strip())
    if not m or not 1 <= int(m.group(2) or 1) <= 12 or not 1 <= int(m.group(3) or 1) <= 31:
        raise BadRequest(f"invalid {name} {value!r}. Use YYYY, YYYY-MM or YYYY-MM-DD.")
    y, mo, d = m.groups()
    if end:   # a bare year / month means the end of that period
        mo = mo or "12"
        d = d or str(calendar.monthrange(int(y), int(mo))[1])
    return [(f"{name}_0", str(int(d or 1))), (f"{name}_1", str(int(mo or 1))), (f"{name}_2", y)]


def _phrase(query: str) -> str | None:
    """A plain 2-4 word query as an exact phrase, or None when it is not one. The site's loose
    word match otherwise ranks party-name hits ("Contract Natural Gas") over the topic."""
    q = query.strip()
    if '"' in q or re.search(r"\b(AND|OR|NOT)\b|[()*]", q) or not 2 <= len(q.split()) <= 4:
        return None
    return f'"{q}"'


async def _search_caselaw(query: str, *, court: str | None, party: str | None,
                          judge: str | None, order: str, limit: int, page_no: int,
                          date_from=None, date_to=None) -> Results:
    if order not in _ORDERS:
        raise BadRequest(f"invalid order {order!r}. Choose from: {', '.join(sorted(_ORDERS))}.")
    phrase = _phrase(query)
    by_date = order in ("date", "-date")
    # The source's date order lists every document containing the words, even in passing. So for a
    # date order, fetch the relevance top 50 and sort those by date here.
    src_order, src_limit, src_page = ("relevance", 50, 1) if by_date else (order, limit, page_no)
    params: list[tuple[str, str]] = [
        ("query", phrase or query), ("order", src_order),
        ("per_page", str(src_limit)), ("page", str(src_page)),
    ]
    for c in (court or "").split(","):
        if c.strip():
            params.append(("court", c.strip().lower()))
    if party:
        params.append(("party", party))
    if judge:
        params.append(("judge", judge))
    if date_from:
        params += _date_params("from_date", date_from, end=False)
    if date_to:
        params += _date_params("to_date", date_to, end=True)

    async def fetch(q: str):
        params[0] = ("query", q)
        r = await get(f"{CASELAW}/atom.xml", params=params)
        if r.status_code != 200 or not r.content.lstrip().startswith(b"<"):
            raise SourceError("Find Case Law search failed", r.status_code)
        return etree.fromstring(r.content)

    feed = await fetch(phrase or query)
    sub = False
    if phrase and feed.find(f"{_ATOM}entry") is None:   # no exact phrase: fall back to a looser match
        phrase = None
        w = query.split()
        # 3-4 words: try all but one word as a phrase plus the remaining word, before all words anywhere
        cands = ([f'"{" ".join(w[:-1])}" AND {w[-1]}', f'{w[0]} AND "{" ".join(w[1:])}"']
                 if len(w) >= 3 else [])
        for q in cands + [query]:
            feed = await fetch(q)
            if feed.find(f"{_ATOM}entry") is not None:
                sub = q != query
                break

    hits = []
    for e in feed.findall(f"{_ATOM}entry"):
        ncn = slug = ""
        for ident in e.findall(f"{_TNA}identifier"):
            if ident.get("type") == "ukncn":
                ncn, slug = (ident.text or "").strip(), ident.get("slug", "")
        if not slug:
            xml_link = e.find(f"{_ATOM}link[@type='application/akn+xml']")
            if xml_link is not None:
                slug = citation_to_slug(xml_link.get("href", ""))
        if not slug:
            continue
        # The neutral citation is the id people cite; use it when it maps back to the slug.
        hit_id = ncn if ncn and citation_to_slug(ncn) == slug else slug
        title = text(e.find(f"{_ATOM}title")) or ncn or slug
        hits.append(DecisionHit(
            id=hit_id,
            title=f"{title} {ncn}" if ncn and ncn not in title else title,
            court=text(e.find(f"{_ATOM}author/{_ATOM}name")),
            date=(e.findtext(f"{_ATOM}published", "") or "")[:10],
            snippet=text(e.find(f"{_ATOM}summary")),
            url=f"{CASELAW}/{slug}",
        ))

    if by_date:
        hits.sort(key=lambda h: h.date, reverse=order == "-date")
        hits = hits[(page_no - 1) * limit:page_no * limit]
    last = feed.find(f"{_ATOM}link[@rel='last']")
    m = re.search(r"[?&]page=(\d+)", last.get("href", "")) if last is not None else None
    note = ("Ordered by relevance; " if order == "relevance" else
            "The best 50 relevance matches, re-sorted by date (the source's own date order lists every "
            "document with the words, even in passing); older matches beyond the top 50 are not shown. ")
    note += ("matched as the exact phrase (a query of 5+ words, or with quotes or AND/OR, is matched loosely); "
             if phrase else
             "no exact phrase found: matched as a phrase of all but one word plus the remaining word; "
             if sub else "words matched loosely, not as a phrase; ")
    note += ("a hit may only mention the topic in passing (check each hit); neutral citations are "
             "not searchable. Covers 2003 onward: older cases (e.g. House of Lords, UKHL) are not "
             "in this source, only on BAILII.")
    if m and not by_date:
        note = f"About {m.group(1)} pages of results. " + note
    return Results(items=hits, total=None, note=note)


def _x(root, path: str, attr: str | None = None) -> str:
    """Find the first element by local-name path (a/b) under root."""
    xp = ".//" + "/".join(f"*[local-name()='{p}']" for p in path.split("/"))
    els = root.xpath(xp)
    if not els:
        return ""
    return (els[0].get(attr) or "") if attr else text(els[0])


def _render_judgment_body(body) -> str:
    """Flatten AKN judgment body: numbered paragraphs, headings, quoted blocks."""
    out: list[str] = []
    pending: str | None = None
    for node in body.iter():
        tag = localname(node)
        if tag in ("paragraph", "subparagraph"):
            if pending:  # previous num had no text paragraph (e.g. table only)
                out.append(pending)
            pending = None
        elif tag == "num":
            pending = text(node)
        elif tag == "heading":
            t = text(node)
            if t:
                out.append(f"**{t}**")
        elif tag == "p":
            t = text(node)
            if not t:
                continue
            if pending:
                t = f"{pending} {t}"
                pending = None
            out.append(t)
    return "\n\n".join(out)


# Find Case Law's Atom feed labels each judgment from its raw court code (<uk:court>);
# get_decision only sees the raw code, so map it to the same label search_caselaw shows.
_COURT_LABELS = {
    "UKSC": "United Kingdom Supreme Court", "UKPC": "Privy Council",
    "EWCA-Civil": "Court of Appeal (Civil Division)",
    "EWCA-Criminal": "Court of Appeal (Criminal Division)",
    "EWCOP": "Court of Protection",
    "EWCOP-T1": "Court of Protection (District judges)",
    "EWCOP-T2": "Court of Protection (Circuit judges)",
    "EWCOP-T3": "Court of Protection (High court judges)",
    "EWFC": "Family Court (High court judges)",
    "EWFC-B": "Family Court (District and circuit judges)",
    "EWCR": "Crown Court", "EAT": "Employment Appeal Tribunal",
    "UKIPT": "Investigatory Powers Tribunal",
    "EWHC-BPD-Admiralty": "High Court (Admiralty Court)",
    "EWHC-BPD-Appeals": "High Court (Business and Property Division Appeals List)",
    "EWHC-BPD-Commercial": "High Court (Commercial Court)",
    "EWHC-BPD-Commercial-Circuit": "High Court (Circuit Commercial Court)",
    "EWHC-BPD-IPEC": "High Court (Intellectual Property Enterprise Court)",
    "EWHC-BPD-Patents": "High Court (Patents Court)",
    "EWHC-BPD-TCC": "High Court (Technology and Construction Court)",
    "EWHC-Chancery-Business": "High Court (Business List)",
    "EWHC-Chancery-BusinessAndProperty": "High Court (Business and Property Courts)",
    "EWHC-Chancery-InsolvencyAndCompanies": "High Court (Insolvency and Companies List)",
    "EWHC-Chancery-IPEC": "High Court (Intellectual Property Enterprise Court)",
    "EWHC-Chancery-Patents": "High Court (Patents Court)",
    "EWHC-Chancery-PropertyTrustsProbate": "High Court (Property, Trusts and Probate List)",
    "EWHC-Family": "High Court (Family Division)",
    "EWHC-KBD": "High Court (King's Bench Division)",
    "EWHC-KBD-Admin": "High Court (Administrative Court)",
    "EWHC-KBD-Admiralty": "High Court (Admiralty Division)",
    "EWHC-KBD-BusinessAndProperty": "High Courts (Business and Property Courts)",
    "EWHC-KBD-Commercial": "High Court (Commercial Court)",
    "EWHC-KBD-Planning": "High Court (Planning Court)",
    "EWHC-Mercantile": "High Court (Mercantile Court)",
    "EWHC-SeniorCourtsCosts": "High Court (Senior Court Costs Office)",
    "UKFTT-GRC": "First-tier Tribunal (General Regulatory Chamber)",
    "UKFTT-TC": "First-tier Tribunal (Tax Chamber)",
    "UKUT-AAC": "Upper Tribunal (Administrative Appeals Chamber)",
    "UKUT-IAC": "Upper Tribunal (Immigration and Asylum Chamber)",
    "UKUT-LC": "Upper Tribunal (Lands Chamber)",
    "UKUT-TCC": "Upper Tribunal (Tax and Chancery Chamber)",
}


async def _get_judgment(reference: str) -> Decision:
    slug = citation_to_slug(reference)
    if not slug:
        raise BadRequest("empty id. Give a neutral citation ('[2024] UKSC 1') or "
                         "Find Case Law slug ('uksc/2024/1').")
    r = await get(f"{CASELAW}/{slug}/data.xml")
    if r.status_code == 404:
        old = (" House of Lords (UKHL) judgments are not in Find Case Law at all."
               if slug.startswith("ukhl/") else "")
        raise NotFound(f"Find Case Law has no judgment at '{slug}' (read from {reference!r}). "
                       "Either the citation is wrong or the judgment is not in this source "
                       "(coverage is 2003 onward, and not every court)." + old +
                       " Find the id with search_caselaw(\"gb\", ...), or try BAILII.")
    if r.status_code != 200 or not r.content.lstrip().startswith(b"<"):
        raise SourceError(f"could not fetch judgment '{slug}'", r.status_code)
    root = etree.fromstring(r.content)
    if localname(root) != "akomaNtoso":
        raise SourceError(f"unexpected response for '{slug}' (not LegalDocML)")

    ncn = _x(root, "proprietary/cite")
    persons = list(root.iter(_AKN + "TLCPerson"))
    judges = [p.get("showAs", "") for p in persons if (p.get("eId") or "").startswith("judge-")]
    parties = [p.get("showAs", "") for p in persons if not (p.get("eId") or "").startswith("judge-")]
    decision_id = ncn if ncn and citation_to_slug(ncn) == slug else slug
    metadata = {k: v for k, v in (("Neutral citation", ncn if ncn != decision_id else ""),
                                  ("Judges", "; ".join(j for j in judges if j)),
                                  ("Parties", "; ".join(p for p in parties if p))) if v}

    parts = []
    header = root.find(f".//{_AKN}header")
    if header is not None:
        h = "\n\n".join(t for t in (text(p) for p in header.iter(_AKN + "p")) if t)
        if h:
            parts.append("### Header\n\n" + h)
    body = root.find(f".//{_AKN}judgmentBody")
    if body is not None:
        parts.append("### Judgment\n\n" + _render_judgment_body(body))

    return Decision(
        id=decision_id,
        title=_x(root, "FRBRWork/FRBRname", "value") or ncn or slug,
        text="\n\n".join(parts),
        url=f"{CASELAW}/{slug}",
        court=_COURT_LABELS.get(_x(root, "proprietary/court"), _x(root, "proprietary/court")),
        date=_x(root, "FRBRWork/FRBRdate", "date")[:10],
        case_number=_x(root, "proprietary/caseNumber"),
        metadata=metadata,
    )


# =========================================================================== #
# Legislation — legislation.gov.uk
# =========================================================================== #
def _norm_id(doc_id: str) -> str:
    s = doc_id.strip()
    s = re.sub(r"^https?://(www\.)?legislation\.gov\.uk/", "", s)
    s = re.sub(r"^id/", "", s)
    s = re.sub(r"/(contents|data\.\w+)$", "", s)
    s = s.strip("/")
    if not s:
        raise BadRequest("empty law id. Use type/year/number, e.g. 'ukpga/2006/46'.")
    return s


def _norm_provision(p: str) -> str:
    s = p.strip().strip("/").rstrip(".").strip()
    if not s:
        raise BadRequest("empty provision. Use e.g. 'section/172', 's.172', 'reg 3', "
                         "'schedule/1/paragraph/2'.")
    if "/" in s:
        return _clean_label(s)  # already a path such as section/172 or schedule/1/paragraph/2
    s = re.sub(r"^(?:schedule|sch)\.?\s*(\w+)\s*,?\s*(?:paragraph|para)\.?\s*(\w+)$",
               r"schedule/\1/paragraph/\2", s, flags=re.I)
    s = re.sub(r"^(?:schedule|sch)\.?\s*(?=\w+$)", "schedule/", s, flags=re.I)
    s = re.sub(r"^part\.?\s*(?=\w+$)", "part/", s, flags=re.I)
    s = re.sub(r"^(s|sec|section)\.?\s*(?=\d)", "section/", s, flags=re.I)
    s = re.sub(r"^(reg|regulation)\.?\s*(?=\d)", "regulation/", s, flags=re.I)
    s = re.sub(r"^(art|article)\.?\s*(?=\d)", "article/", s, flags=re.I)
    s = re.sub(r"^(r|rule)\.?\s*(?=\d)", "rule/", s, flags=re.I)
    if "/" not in s:
        s = f"section/{s}"  # site redirects to regulation/article/rule as needed
    return _clean_label(s)


def _clean_label(s: str) -> str:
    """section/009 -> section/9, section/3a -> section/3A (the site is case-sensitive)."""
    return re.sub(r"^(section|regulation|article|rule)/0*(\d+)([A-Za-z]*)$",
                  lambda m: f"{m.group(1)}/{m.group(2)}{m.group(3).upper()}", s)


async def _fetch(path: str):
    """GET {LEGISLATION}/{path}/data.xml -> parsed CLML root. Raises on failure."""
    url = f"{LEGISLATION}/{path}/data.xml"
    data = _xml_cache.get(url)
    if data is None:
        r = await get(url)
        if r.status_code == 404:
            raise NotFound(f"legislation.gov.uk has no '{path}'. Law ids are type/year/number "
                           "(e.g. 'ukpga/2006/46'); see get_legislation_toc for provision labels.")
        if r.status_code != 200 or not r.content.lstrip().startswith(b"<"):
            raise SourceError(f"could not fetch '{path}' from legislation.gov.uk", r.status_code)
        data = r.content
        if len(_xml_cache) > 8:
            _xml_cache.clear()
        _xml_cache[url] = data
    root = etree.fromstring(data)
    if localname(root) != "Legislation":
        raise SourceError(f"unexpected response for '{path}' (not CLML)")
    return root


def _title(root, doc_id: str) -> str:
    md = root.find(f"{_UKM}Metadata")
    return (text(md.find(_DC + "title")) if md is not None else "") or doc_id


def _as_of(root) -> str:
    return (root.findtext(f"{_UKM}Metadata/{_DCT}valid") or "")[:10]


def _meta(root) -> dict[str, str]:
    md = root.find(f"{_UKM}Metadata")
    out: dict[str, str] = {}
    if md is None:
        return out
    for label, tag in (("Type", "DocumentMainType"), ("Status", "DocumentStatus")):
        el = md.find(f".//{_UKM}{tag}")
        if el is not None and el.get("Value"):
            out[label] = el.get("Value")
    for label, tag in (("Enacted", "EnactmentDate"), ("Made", "Made"),
                       ("Coming into force", "ComingIntoForce")):
        el = md.find(f".//{_UKM}{tag}")
        if el is not None and el.get("Date"):
            out[label] = el.get("Date")
    return out


# Chapter numbers for primary legislation ("2006 c. 46"); instruments use "No.".
_CHAPTER_TYPES = {"ukpga", "ukla", "ukppa", "nia", "apni", "aep", "aosp", "apgb", "gbla", "mwa"}
_SI_TYPES = {"uksi", "ssi", "wsi", "nisr", "nisi", "ukmo", "ukci", "uksro", "nisro"}


def _number(doc_type: str, year: str, num: str) -> str:
    if not num:
        return ""
    if doc_type in _CHAPTER_TYPES:
        return f"{year} c. {num}"
    if doc_type in _SI_TYPES:
        return f"{year} No. {num}"
    if doc_type.startswith("eu"):
        return f"{year}/{num}"
    return f"{year} {doc_type} {num}"   # e.g. "2010 asp 13"


def _title_rank(title: str, query: str) -> int:
    """0: the short title is the query (year aside), 1: it starts with the query, 2: other.
    Applied within one page of results only; the site itself does not rank by relevance."""
    t = re.sub(r"\s+", " ", title).strip().lower()
    q = re.sub(r"\s+", " ", query).strip().lower()
    if not q:
        return 2
    if t == q or re.fullmatch(re.escape(q) + r"( \d{4})?", t):
        return 0
    return 1 if t.startswith(q) else 2


async def _search_legislation(query: str, *, search_in: str, doc_type: str | None,
                              year: str | None, limit: int, page_no: int) -> Results:
    if not query.strip():
        raise BadRequest("empty query. Give words from the title or text of the legislation.")
    if search_in not in ("title", "text"):
        raise BadRequest(f"invalid search_in {search_in!r}. Choose 'title' or 'text'.")
    if year and not re.fullmatch(r"\d{4}", year):
        raise BadRequest(f"invalid year {year!r}. Use a 4-digit year, e.g. 2006.")
    if doc_type and not re.fullmatch(r"[a-z]+", doc_type.strip().lower()):
        raise BadRequest(f"invalid doc_type {doc_type!r}. Use a type code such as ukpga, uksi, asp.")
    params = {"results-count": str(limit), "page": str(page_no), search_in: query}
    # /search/data.feed?type=&year= 301-redirects here (and loses `page`): call it directly.
    path = "/".join(x for x in ((doc_type or "").strip().lower(), year or "") if x) or "all"
    r = await get(f"{LEGISLATION}/{path}/data.feed", params=params)
    if r.status_code != 200 or not r.content.lstrip().startswith(b"<"):
        raise SourceError("legislation.gov.uk search failed", r.status_code)
    feed = etree.fromstring(r.content)

    hits = []
    for e in feed.findall(f"{_ATOM}entry"):
        doc_id = _norm_id(e.findtext(f"{_ATOM}id", ""))
        dtype = doc_id.split("/")[0]
        y = e.find(f"{_UKM}Year")
        n = e.find(f"{_UKM}Number")
        created = e.find(f"{_UKM}CreationDate")
        summary = text(e.find(f"{_ATOM}summary"))
        title = text(e.find(f"{_ATOM}title")) or doc_id
        if summary.startswith("urn:") or summary == title:
            summary = ""
        elif len(summary) > 300:
            summary = summary[:300] + "…"
        hits.append(LawHit(
            id=doc_id,
            title=title,
            type=dtype,
            number=_number(dtype, y.get("Value", "") if y is not None else "",
                           n.get("Value", "") if n is not None else ""),
            date=(created.get("Date", "") if created is not None else "")[:10],
            snippet=summary,
            url=f"{LEGISLATION}/{doc_id}",
        ))

    if search_in == "title":
        hits.sort(key=lambda h: _title_rank(h.title, query))   # stable: source order otherwise

    total_txt = feed.findtext(f"{_OS}totalResults")
    total = int(total_txt) if total_txt and total_txt.isdigit() else None
    counts = [f.get("value", "") for f in feed.iter(f"{_LEG}facetType")]
    if total is None and counts and all(c.isdigit() for c in counts):
        total = sum(int(c) for c in counts)   # every document has exactly one type
    if total is None and not hits and page_no > 1:
        first = await _search_legislation(query, search_in=search_in, doc_type=doc_type,
                                          year=year, limit=limit, page_no=1)
        return Results(items=[], total=first.total,
                       note=f"Page {page_no} is past the last page of results.")
    note = ""
    if not doc_type:
        facets = []
        for f in feed.iter(f"{_LEG}facetType"):
            code = re.search(r"[?&]type=(\w+)", f.get("href", ""))
            facets.append(f"{code.group(1) if code else f.get('type')} {f.get('value')}")
        if facets:
            note = ("By type: " + ", ".join(facets[:8])
                    + ' (narrow with filters={"doc_type": "<code>"})')
    return Results(items=hits, total=total, note=note)


_TOC_DEPTH = {"ContentsPart": 0, "ContentsSchedule": 0, "ContentsChapter": 1,
              "ContentsPblock": 2, "ContentsPsubBlock": 3}


def _rel_path(uri: str, doc_id: str) -> str:
    m = re.search(rf"/{re.escape(doc_id)}/(.+)$", uri or "")
    return m.group(1) if m else ""


async def _get_toc(doc_id: str) -> Toc:
    doc_id = _norm_id(doc_id)
    root = await _fetch(f"{doc_id}/contents")
    entries: list[TocEntry] = []
    depth = 0
    contents = root.find(f".//{_LEG}Contents")
    if contents is not None:
        for el in contents.iter():
            tag = localname(el)
            if tag not in _TOC_DEPTH and tag != "ContentsItem":
                continue
            if tag in _TOC_DEPTH:
                depth = level = _TOC_DEPTH[tag]
            else:
                level = depth + 1
            num = text(el.find(f"{_LEG}ContentsNumber"))
            title = text(el.find(f"{_LEG}ContentsTitle"))
            entries.append(TocEntry(
                title=" — ".join(x for x in (num, title) if x) or "(untitled)",
                level=level,
                provision=_rel_path(el.get("DocumentURI", ""), doc_id),
            ))
    if not entries:
        raise NotFound(f"'{doc_id}' has no contents table; try get_legislation_text.")
    return Toc(id=doc_id, title=_title(root, doc_id), url=f"{LEGISLATION}/{doc_id}/contents",
               entries=entries)


# CLML body renderer (shared by provision + full text)
_HEAD = {"Part": "## ", "Chapter": "### ", "Pblock": "#### ", "PsubBlock": "#### ",
         "Schedule": "## ", "P1group": "**"}
_PARA = {"P", "P1", "P2", "P3", "P4", "P5", "P6", "P7"}
_SKIP = {"Number", "Title", "TitleBlock", "Pnumber", "Reference", "Metadata",
         "Versions", "Resources", "Commentaries", "Commentary", "Contents"}


def _emit(el, out: list[str]) -> None:
    """Append one markdown paragraph per heading/text block. No indentation: the
    (1)/(a) labels carry the nesting, and 4+ leading spaces would render as code."""
    tag = localname(el)
    if tag is None or tag in _SKIP:
        return
    if tag in _HEAD:
        num = text(el.find(f"{_LEG}Number"))
        title = text(el.find(f"{_LEG}Title"))
        if not title:
            tb = el.find(f"{_LEG}TitleBlock")
            title = text(tb) if tb is not None else ""
        heading = " — ".join(x for x in (num, title) if x)
        if heading:
            mark = _HEAD[tag]
            out.append(f"{mark}{heading}{'**' if mark == '**' else ''}")
        ref = text(el.find(f"{_LEG}Reference"))
        if ref:
            out.append(f"_{ref}_")
        for ch in el:
            _emit(ch, out)
    elif tag in _PARA:
        num = text(el.find(f"{_LEG}Pnumber"))
        label = f"**{num}**" if tag == "P1" and num else (f"({num})" if num else "")
        body = el.find(f"{_LEG}{tag}para")
        if body is None:
            body = el
        first = True
        for ch in body:
            ctag = localname(ch)
            if ctag == "Text":
                t = text(ch)
                if not t:
                    continue
                out.append(f"{label + ' ' if first and label else ''}{t}")
                first = False
            elif ctag == "Pnumber":
                continue
            else:
                if first and label:
                    out.append(label)
                    first = False
                _emit(ch, out)
    elif tag == "Text":
        t = text(el)
        if t:
            out.append(t)
    else:
        for ch in el:
            _emit(ch, out)


_COMMENTARY_LABEL = {"F": "F (amendment)", "C": "C (modification)", "I": "I (commencement)",
                     "E": "E (extent)", "M": "M (marginal citation)", "X": "X (editorial)",
                     "P": "P (subordinate)"}


_KEEP_INHERITED = {"F", "I"}   # amendments and commencement of the enclosing Part still matter


def _short(s: str, n: int = 200) -> str:
    return s if len(s) <= n else s[:n].rstrip() + "…"


def _annotations(root, target=None, url: str = "") -> str:
    """Annotations, labelled as on the site (C1, F1, ...). With `target` (the provision's
    element), annotations referenced only from outside it (the enclosing Part/Chapter
    headings) are inherited: amendments and commencement are kept, shortened; the rest
    (extent, modification orders, ...) are counted, not listed."""
    comms = root.findall(f".//{_LEG}Commentaries/{_LEG}Commentary")
    if not comms:
        return ""
    own: set[str] = set()
    if target is not None:
        for el in target.iter():
            ref = el.get("Ref") if localname(el) == "CommentaryRef" else el.get("CommentaryRef")
            if ref:
                own.add(ref)
    counters: dict[str, int] = {}
    lines = ["## Annotations (Statute Law Database)", ""]
    hidden: dict[str, int] = {}
    for c in comms:
        typ = c.get("Type", "?")
        counters[typ] = counters.get(typ, 0) + 1
        label = f"**{typ}{counters[typ]}**"
        if target is None or c.get("id") in own:
            lines.append(f"- {label} {text(c)}")
        elif typ in _KEEP_INHERITED:
            lines.append(f"- {label} (enclosing {_scope(root, target)}) {_short(text(c))}")
        else:
            hidden[typ] = hidden.get(typ, 0) + 1
    if hidden:
        kinds = ", ".join(f"{n} {_COMMENTARY_LABEL.get(k, k)}" for k, n in hidden.items())
        lines.append(f"\n_{sum(hidden.values())} more annotations apply to the enclosing "
                     f"{_scope(root, target)} ({kinds}); not shown. See {url}_")
    lines.append("\nKey: " + "; ".join(_COMMENTARY_LABEL.get(k, k) for k in counters))
    return "\n".join(lines)


def _scope(root, target) -> str:
    """'Part I, Chapter I': the headings enclosing the provision."""
    names = []
    for anc in reversed(list(target.iterancestors())):
        if localname(anc) in ("Part", "Chapter", "Schedule"):
            num = text(anc.find(f"{_LEG}Number"))
            if num:
                names.append(num)
    return ", ".join(names) or "Act"


def _render_document(root, target=None, url: str = "") -> str:
    out: list[str] = []
    for top in root:
        if localname(top) in ("Primary", "Secondary"):
            for ch in top:
                if localname(ch) in ("PrimaryPrelims", "SecondaryPrelims"):
                    lt = ch.find(f".//{_LEG}LongTitle")
                    if lt is not None and text(lt):
                        out.append(f"_{text(lt)}_")
                else:
                    _emit(ch, out)
    ann = _annotations(root, target, url)
    if ann:
        out.append(ann)
    return "\n\n".join(out).strip()


async def _get_provision(doc_id: str, provision: str) -> Provision:
    doc_id = _norm_id(doc_id)
    prov = _norm_provision(provision)
    root = await _fetch(f"{doc_id}/{prov}")
    ident = root.findtext(f"{_UKM}Metadata/{_DC}identifier") or ""
    resolved = _rel_path(ident, doc_id) or prov  # section/3 -> regulation/3 after redirect
    asked = prov.split("/")[0]
    # "section"/bare numbers are generic (the site redirects section/3 to regulation/3 on an SI);
    # an explicit reg/article/rule must not silently become another kind.
    if asked in ("regulation", "article", "rule") and resolved.split("/")[0] != asked:
        raise NotFound(f"no '{doc_id}/{prov}': {doc_id} has no {asked} "
                       f"{prov.split('/', 1)[1]} (the site resolves it to '{resolved}'). "
                       "Use that provision path explicitly if it is what you want.")
    url = f"{LEGISLATION}/{doc_id}/{resolved}"
    ids = {ident.replace("http://www.legislation.gov.uk/", "http://www.legislation.gov.uk/id/"), ident}
    target = next((el for el in root.iter() if el.get("IdURI") in ids), None)
    if target is not None and localname(target.getparent()) == "P1group":
        target = target.getparent()   # the section heading belongs to the section
    return Provision(
        law_id=doc_id,
        law_title=_title(root, doc_id),
        provision=resolved,
        text=_render_document(root, target, url),
        url=url,
        as_of=_as_of(root),
    )


async def _get_text(doc_id: str) -> LawText:
    doc_id = _norm_id(doc_id)
    root = await _fetch(doc_id)
    return LawText(id=doc_id, title=_title(root, doc_id), text=_render_document(root),
                   url=f"{LEGISLATION}/{doc_id}", as_of=_as_of(root), metadata=_meta(root))


# =========================================================================== #
# Adapter
# =========================================================================== #
class UnitedKingdom(Jurisdiction):
    code = "gb"
    name = "United Kingdom"
    languages = ("en",)
    aliases = ("uk",)
    sources = (
        Source("Find Case Law, The National Archives", CASELAW,
               covers=("caselaw",),
               licence="Open Justice Licence v2.0: free re-use incl. commercial; "
                       "'computational analysis' (programmatic bulk searching to identify, "
                       "extract or enrich records) needs a separate, free licence",
               commercial_use=True,
               ai_use=False,   # robots.txt disallows ClaudeBot, anthropic-ai, GPTBot, Google-Extended, ...
               auth="none",
               rate_limit="documented: 1,000 requests / rolling 5 min per IP, HTTP 429 when "
                          "exceeded (API docs, checked 2026-11)",
               terms_url=f"{CASELAW}/open-justice-licence"),
        Source("legislation.gov.uk, The National Archives", LEGISLATION,
               covers=("legislation",),
               licence="Open Government Licence v3.0",
               commercial_use=True,
               ai_use=True,    # robots.txt has no AI opt-out (only Crawl-delay: 5, no PDF/DOCX)
               auth="none",
               rate_limit="documented: 1,500 requests / 5 min per user, requests blocked until the "
                          "5-min average drops (fair-use policy, checked 2026-11)",
               terms_url=f"{LEGISLATION}/fair-use-policy"),
    )
    caselaw_filters = {
        "court": "court code(s), comma-separated: uksc, ukpc, ewca/civ, ewca/crim, ewhc/ch, "
                 "ewhc/kb, ewhc/qb, ewhc/comm, ewhc/admin, ewhc/fam, ewhc/tcc, ewhc/pat, "
                 "ewhc/ipec, ewcop, ewfc, eat, ukut/aac, ukut/iac, ukut/lc, ukut/tcc, ukftt/tc, ukftt/grc",
        "party": "a word from a party's name (exact word match)",
        "judge": "a word from a judge's name (exact word match)",
        "date_from": "decisions published on or after this date: YYYY, YYYY-MM or YYYY-MM-DD",
        "date_to": "decisions published on or before this date (a bare year means its last day)",
        "order": "relevance (default) / -date (newest first) / date / -updated / updated",
    }
    legislation_filters = {
        "search_in": "title (default, words from the short title) or text (full text, broader)",
        "doc_type": "ukpga (UK Act), uksi (UK SI), asp (Scottish Act), asc/anaw (Welsh Act), "
                    "nia (NI Act), ssi, wsi, nisr, ukla, ukppa, eur (retained EU), ...",
        "year": "restrict to a year, e.g. 2006",
    }
    min_interval = {
        "caselaw.nationalarchives.gov.uk": 0.3,   # documented 1,000 / 5 min = 3.3/s
        "www.legislation.gov.uk": 0.3,            # documented 1,500 / 5 min = 5/s
    }
    notes = ("Legislation: England & Wales, Scotland, NI and UK-wide. Case law: England & Wales and "
             "UK-wide courts only (Scottish and NI cases only via UKSC/UKPC), 2003 onward (older: BAILII, "
             "no API). search_caselaw requires ALL words to match; neutral citations are not "
             "searchable, pass them to get_decision directly. Law ids are type/year/number, "
             "e.g. ukpga/2006/46 (Companies Act 2006).")
    gaps = (
        "Case law before 2003 and many first-instance decisions: only on BAILII, which forbids scraping",
        "Hosted or bulk use of Find Case Law: needs the free computational-analysis licence (not yet obtained)",
        "Original-print PDFs of legislation: robots.txt disallows PDF/DOCX",
        "Scottish and Northern Irish court judgments outside Find Case Law: not researched yet",
    )
    samples = {
        "caselaw_query": "unfair prejudice director",
        "decision_id": "[2024] UKSC 1",
        "legislation_query": "Companies Act",
        "law_id": "ukpga/2006/46",
        "provision": "section/172",
    }

    async def search_caselaw(self, query, *, limit, page, filters):
        return await _search_caselaw(
            query, court=filters.get("court"), party=filters.get("party"), judge=filters.get("judge"),
            order=str(filters.get("order", "relevance")), limit=min(limit, 50), page_no=page,
            date_from=filters.get("date_from"), date_to=filters.get("date_to"),
        )

    async def get_decision(self, id):
        return await _get_judgment(id)

    async def search_legislation(self, query, *, limit, page, filters):
        year = filters.get("year")
        return await _search_legislation(
            query, search_in=str(filters.get("search_in", "title")), doc_type=filters.get("doc_type"),
            year=str(year).strip() if year else None, limit=limit, page_no=page,
        )

    async def get_legislation_toc(self, id):
        return await _get_toc(id)

    async def get_legislation_provision(self, id, provision):
        return await _get_provision(id, provision)

    async def get_legislation_text(self, id):
        return await _get_text(id)
