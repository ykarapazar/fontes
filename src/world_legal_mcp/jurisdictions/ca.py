"""Canada (federal): SCC judgments from the Court's Lexum/Decisia site, federal
consolidated Acts and regulations from Justice Laws (XML).

Gotchas this code encodes:
  * decisions.scc-csc.ca (run by Lexum for the Supreme Court) has no API. Search is
    the Decisia results page, fetched with `iframe=true` (the page without it is an
    empty shell around an iframe). 25 hits per source page; we slice to `limit`.
  * The decision id is Lexum's item number ("20353"). Neutral or report citations
    ("2024 SCC 10", "[1988] 2 SCR 712") are also accepted by get_decision and
    resolved with the search form's citation field (one extra request).
  * Justice Laws has no search API. search_legislation matches titles against the
    official index Legis.xml (~5 MB, fetched once per process and kept in memory).
    Full-text search is only on the website.
  * Law XML is one file per Act/regulation (Criminal Code ~6 MB); a few parsed
    files are kept in memory. Sections are direct children of <Body>, schedules
    follow <Body>.
  * The Constitution Acts are not in the XML set. Law id "Const": the one-page HTML
    consolidation /eng/Const/FullText.html (~380 kB, THE CONSTITUTION ACTS 1867 to 1982:
    Constitution Act 1867, Canada Act 1982, Constitution Act 1982 incl. the Charter),
    parsed once per process. Section numbers repeat across the Acts (the ids are
    duplicated in the HTML), so provision labels carry the Act: "1867 s. 91", "1982 s. 7",
    "Canada Act 1982 s. 1", "1867 schedule-1". A bare "section-7" resolves only when one
    Act has it; "charter s. 7" means 1982. Endnotes (amendment history) are left out.
    The page states no "current to" date. The other instruments of the Constitution of
    Canada (Manitoba Act 1870, Alberta Act ...) sit only in the 1990 "report version"
    (/eng/ConstRpt/), which is not kept up to date; not served.
  * French: same ids for Acts at /fra/; regulation ids differ (SOR -> DORS).
    This adapter serves English.
"""
from __future__ import annotations

import re
from datetime import date

from lxml import etree
from lxml import html as lhtml

from .._http import clean, get, html_to_md, lru_put
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

SCC = "https://decisions.scc-csc.ca"
LAWS = "https://laws-lois.justice.gc.ca"
_SCC_PAGE = 25          # hits per Decisia results page
_COLLECTIONS = {"judgments": "1", "leave": "2"}

_xml_cache: dict[str, bytes] = {}
_index: list[dict] = []


# =========================================================================== #
# Case law — Supreme Court of Canada (Lexum / Decisia)
# =========================================================================== #
def _scc_params(query: str, filters: dict) -> dict[str, str]:
    dates: dict[str, date] = {}
    for k in ("date_from", "date_to"):
        v = str(filters.get(k, "") or "")
        if v:
            try:
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
                    raise ValueError
                dates[k] = date.fromisoformat(v)
            except ValueError:
                raise BadRequest(f"invalid {k} {v!r}. Use a real date as YYYY-MM-DD, e.g. 2020-01-31.") from None
    if len(dates) == 2 and dates["date_from"] > dates["date_to"]:
        raise BadRequest(f"date_from {filters['date_from']} is after date_to {filters['date_to']}.")
    order = str(filters.get("order", "relevance") or "relevance")
    if order not in ("relevance", "date"):
        raise BadRequest(f"invalid order {order!r}. Choose 'relevance' or 'date' (newest first).")
    col = str(filters.get("collection", "judgments") or "judgments")
    if col not in _COLLECTIONS:
        raise BadRequest(f"invalid collection {col!r}. Choose 'judgments' or 'leave'.")
    return {"cont": query or "", "ref": str(filters.get("citation", "") or ""),
            "d1": str(filters.get("date_from", "") or ""), "d2": str(filters.get("date_to", "") or ""),
            "p": str(filters.get("party", "") or ""), "col": _COLLECTIONS[col], "su": "",
            "or": "date" if order == "date" else "", "iframe": "true"}


def _parse_results(page_html: str) -> tuple[list[DecisionHit], int | None]:
    doc = lhtml.fromstring(page_html)
    m = re.search(r"([\d,]+)\s+result\(s\)", page_html)
    total = int(m.group(1).replace(",", "")) if m else None
    hits = []
    for li in doc.xpath("//div[@id='decisia-results']//ul[contains(@class,'collectionItemList')]/li"):
        a = li.xpath(".//span[@class='title']/a")
        if not a:
            continue
        im = re.search(r"/item/(\d+)/", a[0].get("href", ""))
        if not im:
            continue
        item = im.group(1)
        cites = [clean(x.text_content()) for x in
                 li.xpath(".//span[@class='citation' or @class='report-citation']")]
        date = clean("".join(li.xpath(".//span[@class='publicationDate']//text()")))
        name = clean(a[0].text_content())
        snip = li.xpath(".//p[contains(@class,'snippet')]")
        hits.append(DecisionHit(
            id=item,
            title=f"{name}, {cites[0]}" if cites else name,
            court="Supreme Court of Canada",
            date=date if re.fullmatch(r"\d{4}-\d{2}-\d{2}", date) else "",
            snippet=clean(snip[0].text_content())[:400] if snip else "",
            url=f"{SCC}/scc-csc/scc-csc/en/item/{item}/index.do",
        ))
    if total is None and not hits and "result(s)" not in page_html and "No result" not in page_html:
        raise SourceError("unexpected SCC search page (layout changed?)")
    return hits, (total if total is not None else (0 if not hits else None))


async def _scc_search_page(params: dict, src_page: int) -> tuple[list[DecisionHit], int | None]:
    r = await get(f"{SCC}/scc-csc/en/d/s/index.do", params={**params, "page": str(src_page)})
    if r.status_code != 200:
        raise SourceError("SCC decisions search failed", r.status_code)
    return _parse_results(r.text)


async def _search_caselaw(query: str, filters: dict, limit: int, page_no: int) -> Results:
    if not (query or "").strip() and not any(filters.get(k) for k in ("citation", "party")):
        raise BadRequest("give a query, or a citation/party filter (date filters alone are not enough).")
    params = _scc_params(query, filters)
    limit = max(1, min(limit, _SCC_PAGE))
    start = (page_no - 1) * limit
    src = start // _SCC_PAGE + 1
    hits, total = await _scc_search_page(params, src)
    off = start - (src - 1) * _SCC_PAGE
    items = hits[off:off + limit]
    if len(items) < limit and len(hits) == _SCC_PAGE:
        more, _ = await _scc_search_page(params, src + 1)
        items += more[:limit - len(items)]
    return Results(items=items, total=total,
                   note="Supreme Court of Canada only (1876 onward). Ids are Lexum item numbers; "
                        "get_decision also takes a citation like '2024 SCC 10'.")


_ITEM_RE = re.compile(r"(?:/item/)?(\d{1,7})(?:/index\.do.*)?$")


async def _resolve(ref: str) -> str:
    s = ref.strip()
    m = _ITEM_RE.search(s) if re.fullmatch(r"\d{1,7}|.*?/item/\d+.*", s) else None
    if m:
        return m.group(1)
    if not s:
        raise BadRequest("empty id. Give a Lexum item number ('20353') or a citation "
                         "('2024 SCC 10', '[1988] 2 SCR 712').")
    hits, _ = await _scc_search_page(_scc_params("", {"citation": s}), 1)
    if not hits:
        raise NotFound(f"no SCC judgment with citation {s!r}. Use search_caselaw(\"ca\", ...) to find it.")
    return hits[0].id


async def _get_decision(ref: str) -> Decision:
    item = await _resolve(ref)
    r = await get(f"{SCC}/scc-csc/scc-csc/en/item/{item}/index.do", params={"iframe": "true"})
    if r.status_code == 404:
        raise NotFound(f"no SCC item {item}.")
    if r.status_code != 200:
        raise SourceError(f"could not fetch SCC item {item}", r.status_code)
    doc = lhtml.fromstring(r.text)
    title_el = doc.xpath("//div[@id='decisia-document-header']//h3[@class='title']")
    body = doc.xpath("//div[@id='document-content']")
    if not title_el or not body:
        raise NotFound(f"SCC item {item} is not a judgment page (no title/content).")
    meta: dict[str, str] = {}
    for tr in doc.xpath("//div[@id='decisia-document-header']//div[@class='metadata']//tr"):
        tds = tr.xpath("./td")
        if len(tds) >= 2:
            label = clean(tds[0].text_content())
            val = "; ".join(clean(t) for t in tds[1].xpath(".//text()") if clean(t))
            if label and val:
                meta[label] = val
    name = clean(title_el[0].text_content())
    cite = meta.get("Neutral citation") or meta.get("Report citation") or ""
    text_md = html_to_md(etree.tostring(body[0], encoding="unicode", method="html"))
    if not text_md:
        raise SourceError(f"SCC item {item} has no text (PDF only?)")
    keep = {k: v for k, v in meta.items() if k in (
        "Neutral citation", "Report citation", "Judges", "On appeal from", "Subjects", "Collection")}
    return Decision(
        id=item,
        title=f"{name}, {cite}" if cite else name,
        text=text_md,
        url=f"{SCC}/scc-csc/scc-csc/en/item/{item}/index.do",
        court="Supreme Court of Canada",
        date=meta.get("Date", "")[:10] if re.match(r"\d{4}-\d{2}-\d{2}", meta.get("Date", "")) else "",
        case_number=meta.get("Case number", ""),
        metadata=keep,
    )


# =========================================================================== #
# Legislation — Justice Laws Website (consolidated federal Acts and regulations)
# =========================================================================== #
_REG_RE = re.compile(r"^(SOR|SI|C\.R\.C\.)", re.I)


def _norm_law_id(law_id: str) -> str:
    s = (law_id or "").strip()
    s = re.sub(r"^https?://laws-lois\.justice\.gc\.ca/eng/(acts|regulations|XML)/", "", s)
    if re.match(r"^(https?://laws-lois\.justice\.gc\.ca/eng/Const(/|$)|const(itution)?( acts?)?$|charter$)", s, re.I):
        return "Const"
    s = re.sub(r"(/.*|\.xml)$", "", s)
    s = s.replace("_", " ").strip()
    if not s:
        raise BadRequest("empty law id. Use the Justice Laws id, e.g. 'C-46' (Criminal Code), "
                         "'SOR-2002-227', 'C.R.C., c. 870'.")
    if re.fullmatch(r"[a-z]-[\d.]+", s):
        s = s.upper()
    return s


def _is_reg(law_id: str) -> bool:
    return bool(_REG_RE.match(law_id))


def _html_base(law_id: str) -> str:
    if law_id == "Const":
        return f"{LAWS}/eng/Const"
    return f"{LAWS}/eng/{'regulations' if _is_reg(law_id) else 'acts'}/{law_id.replace(' ', '_')}"


async def _load_index() -> list[dict]:
    if _index:
        return _index
    r = await get(f"{LAWS}/eng/XML/Legis.xml")
    if r.status_code != 200 or not r.content.lstrip().startswith(b"<"):
        raise SourceError("could not fetch the Justice Laws index (Legis.xml)", r.status_code)
    root = etree.fromstring(r.content)
    for el in root.iter("Act", "Regulation"):
        if el.findtext("Language") != "eng":
            continue
        _index.append({"id": el.findtext("UniqueId") or "", "title": clean(el.findtext("Title")),
                       "type": "act" if el.tag == "Act" else "regulation",
                       "number": el.findtext("OfficialNumber") or "",
                       "current": el.findtext("CurrentToDate") or ""})
    return _index


_CONST_TITLE = ("The Constitution Acts, 1867 to 1982 (Constitution Act 1867, Canada Act 1982, Constitution "
                "Act 1982 incl. the Canadian Charter of Rights and Freedoms)")
_CONST_ENTRY = {"id": "Const", "title": _CONST_TITLE, "type": "constitution", "number": "", "current": ""}


async def _search_legislation(query: str, filters: dict, limit: int, page_no: int) -> Results:
    kind = str(filters.get("type", "") or "").lower()
    if kind not in ("", "act", "regulation"):
        raise BadRequest(f"invalid type {kind!r}. Choose 'act' or 'regulation'.")
    q = clean(query).lower()
    words = re.findall(r"\w+", q)
    if not words:
        raise BadRequest("give some words from the title, or an id such as 'C-46'.")
    scored = []
    if kind != "regulation" and all(re.search(rf"\b{re.escape(w)}", _CONST_TITLE.lower()) for w in words):
        scored.append((0, 0, _CONST_ENTRY))
    for e in await _load_index():
        if kind and e["type"] != kind:
            continue
        t = e["title"].lower()
        if e["id"].lower() == q:
            score = 0
        elif t == q:
            score = 1
        elif all(re.search(rf"\b{re.escape(w)}", t) for w in words):
            score = 2 if t.startswith(q) else 3 + (e["type"] == "regulation")
        else:
            continue
        scored.append((score, len(t), e))
    scored.sort(key=lambda x: (x[0], x[1]))
    start = (page_no - 1) * limit
    items = [LawHit(id=e["id"], title=e["title"], type=e["type"], number=e["number"],
                    status="", url=(f"{LAWS}/eng/Const/" if e["id"] == "Const"
                                    else f"{_html_base(e['id'])}/index.html"),
                    snippet=f"Current to {e['current']}" if e["current"] else "")
             for _, _, e in scored[start:start + limit]]
    note = ("Title search over the official Justice Laws index (federal only, English titles only: "
            "French titles such as 'Code criminel' are not searched; the Criminal Code is C-46). "
            "Full-text search: laws-lois.justice.gc.ca/Search.")
    if not scored and "streaming" in q:
        note += (" Acts that only amend another Act have no entry of their own; e.g. the Online "
                 "Streaming Act (S.C. 2023, c. 8) amends the Broadcasting Act (B-9.01).")
    return Results(items=items, total=len(scored), note=note)


async def _fetch_law(law_id: str):
    url = f"{LAWS}/eng/XML/{law_id.replace(' ', '_')}.xml"
    data = _xml_cache.get(url)
    if data is None:
        r = await get(url)
        if r.status_code == 404 or (r.status_code == 200 and b"<html" in r.content[:600].lower()):
            raise NotFound(f"Justice Laws has no law {law_id!r}. Ids look like 'C-46', "
                           "'SOR-2002-227', 'C.R.C., c. 870'; find one with search_legislation(\"ca\", ...).")
        if r.status_code != 200:
            raise SourceError(f"could not fetch {law_id!r} from Justice Laws", r.status_code)
        data = lru_put(_xml_cache, url, r.content, 4)
    root = etree.fromstring(data)
    if root.tag not in ("Statute", "Regulation"):
        raise SourceError(f"unexpected XML for {law_id!r} (root <{root.tag}>)")
    return root


_LIMS = "{http://justice.gc.ca/lims}"


def text(el) -> str:
    """Descendant text joined without extra spaces (keeps 'Act,' rather than 'Act ,')."""
    return "" if el is None else clean("".join(el.itertext()))


def _law_title(root, law_id: str) -> str:
    ident = root.find("Identification")
    if ident is None:
        return law_id
    return (text(ident.find("ShortTitle")) or text(ident.find("LongTitle"))
            or text(ident.find("InstrumentNumber")) or law_id)


def _as_of(root) -> str:
    return (root.get(f"{_LIMS}current-date") or "")[:10]


# --- rendering ------------------------------------------------------------- #
_SKIP = {"HistoricalNote", "MarginalNote", "Label", "TitleText", "ScheduleFormHeading",
         "RecentAmendments", "Footnote"}
_BLOCKS = {"Subsection", "Paragraph", "Subparagraph", "Clause", "Subclause", "Subsubclause",
           "Definition", "Provision", "ContinuedSectionSubsection", "ContinuedParagraph",
           "ContinuedSubparagraph", "ContinuedClause", "ContinuedDefinition", "Item"}


def _block(el, out: list[str]) -> None:
    """Render a legislative block: own Label + Text on one line, children below."""
    label = el.findtext("Label") or ""
    first = True
    for ch in el:
        if not isinstance(ch.tag, str) or ch.tag in _SKIP:
            continue
        if ch.tag == "Text":
            t = text(ch)
            if t:
                out.append(f"{label} {t}" if first and label else t)
                first = False
        elif ch.tag in _BLOCKS:
            if first and label:
                out.append(label)
                first = False
            _block(ch, out)
        elif ch.tag == "Repealed":
            out.append((f"{label} " if first and label else "") + text(ch))
            first = False
        elif ch.tag in ("TableGroup", "FormGroup", "Oath", "Group", "BillPiece", "SectionPiece"):
            t = text(ch)
            if t:
                out.append(t)
        else:
            _block(ch, out)
    if first and label:
        out.append(label)


def _render_section(sec) -> str:
    out: list[str] = []
    label = sec.findtext("Label") or ""
    note = text(sec.find("MarginalNote"))
    out.append(f"**{label}**" + (f" — {note}" if note else ""))
    body: list[str] = []
    for ch in sec:
        if not isinstance(ch.tag, str) or ch.tag in _SKIP:
            continue
        if ch.tag == "Text":
            body.append(text(ch))
        elif ch.tag == "Repealed":
            body.append(text(ch))
        else:
            if ch.tag == "Subsection" and ch.find("MarginalNote") is not None:
                body.append(f"_{text(ch.find('MarginalNote'))}_")
            _block(ch, body)
    out += [b for b in body if b.strip()]
    hist = "; ".join(text(h) for h in sec.iterfind("HistoricalNote/HistoricalNoteSubItem"))
    if hist:
        out.append(f"_History: {hist}_")
    return "\n\n".join(out)


def _render_schedule(sch) -> str:
    head = sch.find("ScheduleFormHeading")
    title = text(head) if head is not None else "Schedule"
    parts = [f"## {title}"]
    for ch in sch:
        if not isinstance(ch.tag, str) or ch.tag in ("ScheduleFormHeading",):
            continue
        if ch.tag == "Section":
            parts.append(_render_section(ch))
        elif ch.tag == "Heading":
            t = text(ch.find("TitleText"))
            if t:
                parts.append(f"### {t}")
        else:
            out: list[str] = []
            _block(ch, out)
            parts += [o for o in out if o.strip()]
    return "\n\n".join(parts)


def _heading_md(h) -> str:
    lvl = int(h.get("level", "1") or 1)
    label = text(h.find("Label"))
    title = text(h.find("TitleText"))
    t = " — ".join(x for x in (label, title) if x)
    return f"{'#' * min(lvl + 1, 6)} {t}" if t else ""


def _schedules(root) -> list:
    return [s for s in root if s.tag == "Schedule"]


def _schedule_title(sch, n: int) -> str:
    head = sch.find("ScheduleFormHeading")
    return (text(head) if head is not None else "") or f"Schedule {n}"


# --- provision labels -------------------------------------------------------- #
def _norm_provision(p: str) -> str:
    s = clean(p).lower()
    if not s:
        raise BadRequest("empty provision. Use e.g. 'section-718', 's. 718', '718.2', 'schedule-1'.")
    m = re.fullmatch(r"(?:schedule|sch\.?|annexe?)[\s-]*(\d+)", s)
    if m:
        return f"schedule-{m.group(1)}"
    s = re.sub(r"^(sections|section|sec\.?|ss?\.|ss?|article|art\.?)[\s-]*", "", s)
    m = re.match(r"^(\d+(?:\.\d+)*)", s)
    if not m:
        raise BadRequest(f"unrecognised provision {p!r}. Use e.g. 'section-718', 's. 718', "
                         "'718.2(e)' (resolves to section 718.2), 'schedule-1'.")
    return f"section-{m.group(1)}"



# --- Constitution Acts 1867 to 1982 (HTML only) ------------------------------ #
_const_cache: dict[str, dict] = {}
_CONST_ACTS = {"CONSTITUTION ACT, 1867": ("1867", "Constitution Act, 1867"),
               "CANADA ACT 1982": ("canada-act-1982", "Canada Act 1982"),
               "CONSTITUTION ACT, 1982": ("1982", "Constitution Act, 1982")}
_ACT_SHORT = {"1867": "1867", "canada-act-1982": "Canada Act 1982", "1982": "1982"}
_ORD = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"]


def _ctext(el) -> str:
    """Text of an HTML node without the 'End note (n)' markers."""
    import copy
    el = copy.deepcopy(el)
    for x in el.xpath('.//span[contains(@class,"wb-invisible")]|.//a[starts-with(@href,"#end") '
                      'or starts-with(@href,"endNotes")]'):
        x.drop_tree()
    return clean("".join(el.itertext()))


def _const_blocks(el):
    """Document-order blocks of the page: (kind, class, text|rows)."""
    for c in el:
        if not isinstance(c.tag, str):
            continue
        t, cls = c.tag, c.get("class") or ""
        if t in ("h2", "h3", "h4"):
            yield ("h" + t[1], cls, _ctext(c))
        elif t == "p":
            lab = c.xpath('.//span[@class="sectionLabel"]')
            yield ("p", "Section" if lab else cls, _ctext(c))
        elif t == "ul":
            for li in c.iterfind("li"):
                if li.find("p") is not None:
                    yield from _const_blocks(li)
                else:
                    yield ("p", "li", _ctext(li))
        elif t == "table":
            rows = [" | ".join(_ctext(td) for td in tr.iter("td", "th") if _ctext(td))
                    for tr in c.iter("tr")]
            yield ("p", "table", "\n".join(r for r in rows if r))
        elif t == "div" and "listItemBlock" in cls:
            yield ("p", "li", _ctext(c))
        elif t in ("section", "div", "header", "blockquote"):
            yield from _const_blocks(c)


def _parse_const(page: bytes) -> dict:
    doc = lhtml.fromstring(page)
    w = doc.xpath('//div[contains(@class,"wb-txthl")]')
    if not w:
        raise SourceError("Justice Laws Constitution page has an unexpected layout")
    secs: dict[tuple[str, str], str] = {}
    scheds: dict[tuple[str, int], str] = {}
    toc: list[TocEntry] = []
    text_parts: list[str] = []
    act, cur, note, buf, sched_n = "", None, "", [], {}

    def flush():
        nonlocal cur, buf
        if cur is not None and buf:
            kind, key, ident = cur
            md = "\n\n".join(buf)
            if kind == "s":
                secs[(key, ident)] = md
            else:
                scheds[(key, ident)] = md
            text_parts.append(md)
        cur, buf = None, []

    for kind, cls, t in _const_blocks(w[0]):
        if kind == "h2" and (cls == "Title-of-Act" or t.upper() in _CONST_ACTS):
            flush()
            key, title = _CONST_ACTS.get(t.upper(), (re.sub(r"\W+", "-", t.lower()), t.title()))
            act = key
            toc.append(TocEntry(title=title, level=0))
            text_parts.append(f"# {title}")
        elif kind == "h2" and cls == "scheduleLabel":
            flush()
            if t.upper().startswith("ENDNOTES"):
                break
            n = sched_n[act] = sched_n.get(act, 0) + 1
            cur, buf = ("sch", act, n), [f"## {t}"]
            toc.append(TocEntry(title=t, level=1, provision=f"{_ACT_SHORT[act]} schedule-{n}"))
        elif kind in ("h2", "h3", "h4"):
            flush()
            lvl = {"h2": 1, "h3": 2, "h4": 3}[kind]
            toc.append(TocEntry(title=t, level=lvl))
            text_parts.append("#" * (lvl + 1) + " " + t)
        elif cls == "MarginalNote":
            note = re.sub(r"^Marginal note:\s*", "", t)   # belongs to the next block
        elif cls == "Section" and re.match(r"^[0-9]+[A-Z]?(?:\.[0-9]+)?\b", t):
            flush()
            m = re.match(r"^([0-9]+[A-Z]?(?:\.[0-9]+)?)\b\s*(.*)$", t, re.S)
            label, body = m.group(1), m.group(2)
            cur = ("s", act, label)
            buf = [f"**{label}**" + (f" — {note}" if note else ""), body]
            toc.append(TocEntry(title=f"{label}" + (f" — {note}" if note else ""), level=2,
                                provision=f"{_ACT_SHORT[act]} s. {label}"))
            note = ""
        elif t:
            if cur is not None:
                if note:
                    buf.append(f"_{note}_")
                    note = ""
                buf.append(t)
            else:
                text_parts.append(t)
    flush()
    if not secs:
        raise SourceError("Justice Laws Constitution page: no sections found")
    return {"secs": secs, "scheds": scheds, "toc": toc, "text": "\n\n".join(text_parts)}


async def _const() -> dict:
    if "c" not in _const_cache:
        r = await get(f"{LAWS}/eng/Const/FullText.html")
        if r.status_code != 200 or b"CONSTITUTION ACT, 1867" not in r.content:
            raise SourceError("could not fetch the Constitution Acts page from Justice Laws", r.status_code)
        lru_put(_const_cache, "c", _parse_const(r.content), 1)
    return _const_cache["c"]


def _const_key(provision: str, law: dict) -> tuple[str, str, str]:
    """'1867 s. 91' / 'charter s. 7' / 'Canada Act 1982 s. 1' / '1867 schedule 1' -> (kind, act, id)."""
    s = clean(provision).lower()
    act = ""
    m = re.fullmatch(r"(.+?)\s+of\s+the\s+(?:canadian\s+)?charter(?:\s+of\s+rights(?:\s+and\s+freedoms)?)?", s)
    if m:
        s = "charter " + m.group(1)
    for pat, key in ((r"^canada act(?: 1982)?", "canada-act-1982"), (r"^(?:charter|1982)", "1982"),
                     (r"^(?:ca\.?\s*)?1867", "1867")):
        m = re.match(pat, s)
        if m:
            act, s = key, s[m.end():]
            break
    s = s.strip(" ,:/-")
    m = re.fullmatch(r"(?:(first|second|third|fourth|fifth|sixth)\s+)?(?:schedule|sch\.?)[\s-]*(\d+)?", s)
    if m:
        n = int(m.group(2)) if m.group(2) else (_ORD.index(m.group(1)) + 1 if m.group(1) else 1)
        found = [a for (a, k) in law["scheds"] if k == n and (not act or a == act)]
        if len(found) != 1:
            raise NotFound(f"no schedule {n} for {act or 'any Act'}. Labels like '1867 schedule-1' or "
                           "'1982 schedule-1'; see get_legislation_toc(\"ca\", \"Const\").")
        return "sch", found[0], n
    s = re.sub(r"^(sections|section|sec\.?|ss?\.|ss?|article|art\.?)[\s-]*", "", s)
    m = re.match(r"^(\d+[a-z]?(?:\.\d+)?)", s)
    if not m:
        raise BadRequest(f"unrecognised provision {provision!r}. Use e.g. '1867 s. 91', '1982 s. 7', "
                         "'charter s. 7', 'canada act 1982 s. 1', '1867 schedule-1'.")
    label = m.group(1).upper()
    found = [a for (a, k) in law["secs"] if k == label and (not act or a == act)]
    if not found:
        raise NotFound(f"no section {label} in {act or 'the Constitution Acts'}. See "
                       "get_legislation_toc(\"ca\", \"Const\") for the labels.")
    if len(found) > 1:
        raise BadRequest(f"section {label} exists in several Acts ({', '.join(_ACT_SHORT[a] for a in found)}): "
                         f"say which, e.g. '1867 s. {label}' or '1982 s. {label}' (Charter = 1982).")
    return "s", found[0], label


_CONST_TITLE_SHORT = "The Constitution Acts, 1867 to 1982"
_CONST_URL = f"{LAWS}/eng/Const/FullText.html"


async def _get_toc(law_id: str) -> Toc:
    law_id = _norm_law_id(law_id)
    if law_id == "Const":
        return Toc(id="Const", title=_CONST_TITLE_SHORT, url=_CONST_URL, entries=(await _const())["toc"])
    root = await _fetch_law(law_id)
    body = root.find("Body")
    entries: list[TocEntry] = []
    hlevel = 0
    if body is not None:
        for el in body:
            if el.tag == "Heading":
                t = _heading_md(el).lstrip("# ")
                if t:
                    hlevel = max(0, int(el.get("level", "1") or 1) - 1)
                    entries.append(TocEntry(title=t, level=hlevel))
            elif el.tag == "Section":
                label = el.findtext("Label") or ""
                if not label:
                    continue
                note = text(el.find("MarginalNote"))
                if not note and el.find("Repealed") is not None:
                    note = text(el.find("Repealed"))
                entries.append(TocEntry(title=f"{label} — {note}" if note else label,
                                        level=hlevel + 1, provision=f"section-{label}"))
    for n, sch in enumerate(_schedules(root), 1):
        entries.append(TocEntry(title=_schedule_title(sch, n), level=0, provision=f"schedule-{n}"))
    if not entries:
        raise NotFound(f"{law_id!r} has no sections; try get_legislation_text.")
    return Toc(id=law_id, title=_law_title(root, law_id), url=f"{_html_base(law_id)}/index.html",
               entries=entries)


async def _get_provision(law_id: str, provision: str) -> Provision:
    law_id = _norm_law_id(law_id)
    if law_id == "Const":
        law = await _const()
        kind, act, ident = _const_key(provision, law)
        body = law["secs"][(act, ident)] if kind == "s" else law["scheds"][(act, ident)]
        label = f"{_ACT_SHORT[act]} " + (f"s. {ident}" if kind == "s" else f"schedule-{ident}")
        return Provision(law_id="Const", law_title=_CONST_TITLE_SHORT, provision=label, text=body,
                         url=_CONST_URL)
    label = _norm_provision(provision)
    root = await _fetch_law(law_id)
    base = _html_base(law_id)
    if label.startswith("schedule-"):
        n = int(label.split("-")[1])
        sch = _schedules(root)
        if not 1 <= n <= len(sch):
            raise NotFound(f"{law_id} has {len(sch)} schedule(s); no {label}.")
        return Provision(law_id=law_id, law_title=_law_title(root, law_id), provision=label,
                         text=_render_schedule(sch[n - 1]), url=f"{base}/index.html",
                         as_of=_as_of(root))
    num = label.split("-", 1)[1]
    body = root.find("Body")
    for sec in (body if body is not None else []):
        if sec.tag == "Section" and (sec.findtext("Label") or "") == num:
            return Provision(law_id=law_id, law_title=_law_title(root, law_id), provision=label,
                             text=_render_section(sec), url=f"{base}/{label}.html",
                             as_of=_as_of(root))
    raise NotFound(f"{law_id} has no section {num}. See get_legislation_toc(\"ca\", {law_id!r}).")


async def _get_text(law_id: str) -> LawText:
    law_id = _norm_law_id(law_id)
    if law_id == "Const":
        return LawText(id="Const", title=_CONST_TITLE_SHORT, text=(await _const())["text"],
                       url=_CONST_URL,
                       metadata={"Note": "Consolidation by the Department of Justice; endnotes "
                                         "(amendment history) omitted; page gives no 'current to' date"})
    root = await _fetch_law(law_id)
    parts: list[str] = []
    ident = root.find("Identification")
    if ident is not None and text(ident.find("LongTitle")):
        parts.append(f"_{text(ident.find('LongTitle'))}_")
    body = root.find("Body")
    for el in (body if body is not None else []):
        if el.tag == "Heading":
            h = _heading_md(el)
            if h:
                parts.append(h)
        elif el.tag == "Section":
            parts.append(_render_section(el))
        else:
            out: list[str] = []
            _block(el, out)
            parts += [o for o in out if o.strip()]
    parts += [_render_schedule(s) for s in _schedules(root)]
    meta = {k: v for k, v in (
        ("Consolidated number", text(ident.find("Chapter/ConsolidatedNumber")) if ident is not None else ""),
        ("Instrument number", text(ident.find("InstrumentNumber")) if ident is not None else ""),
        ("Last amended", (root.get(f"{_LIMS}lastAmendedDate") or "")[:10]),
        ("In force", root.get("in-force", "")),
    ) if v}
    return LawText(id=law_id, title=_law_title(root, law_id), text="\n\n".join(parts),
                   url=f"{_html_base(law_id)}/FullText.html", as_of=_as_of(root), metadata=meta)


# =========================================================================== #
# Adapter
# =========================================================================== #
class Canada(Jurisdiction):
    code = "ca"
    name = "Canada"
    languages = ("en", "fr")
    aliases = ("can", "canada")
    sources = (
        Source("Supreme Court of Canada judgments (decisions.scc-csc.ca, hosted by Lexum for the Court)",
               SCC,
               covers=("caselaw",),
               licence="Reasons for judgment: Reproduction of Federal Law Order (SI/97-5), free "
                       "reproduction incl. commercial if accurate and not presented as official. "
                       "Headnotes and editorial features (paragraph numbers, lists of authorities): "
                       "commercial reproduction needs the Court's written permission",
               commercial_use=None,
               ai_use=True,    # robots.txt (2026-11-05): only BUbiNG blocked + 2 item pages; no AI opt-out
               auth="none",
               rate_limit="unknown; 1 s spacing, no 429 seen (2026-11)",
               terms_url="https://scc-csc.ca/resources-ressources/terms-avis/"),
        Source("Justice Laws Website, Department of Justice Canada", LAWS,
               covers=("legislation",),
               licence="Open Government Licence – Canada (open.canada.ca XML dataset); also "
                       "Reproduction of Federal Law Order (not to be presented as official)",
               commercial_use=True,
               ai_use=True,    # no robots.txt (404, 2026-11-05); no AI clause in terms
               auth="none",
               rate_limit="unknown; 1 s spacing, no 429 seen (2026-11)",
               terms_url=f"{LAWS}/eng/FAQ/index.html"),
    )
    caselaw_filters = {
        "citation": "neutral or report citation, e.g. '2024 SCC 10' or '[1988] 2 SCR 712'",
        "party": "a party name",
        "date_from": "decision date from, YYYY-MM-DD",
        "date_to": "decision date to, YYYY-MM-DD",
        "order": "relevance (default) or date (newest first)",
        "collection": "judgments (default) or leave (applications for leave to appeal)",
    }
    legislation_filters = {
        "type": "act or regulation (default: both)",
    }
    min_interval = {
        "decisions.scc-csc.ca": 1.0,
        "laws-lois.justice.gc.ca": 1.0,
    }
    notes = ("Federal only. Case law = Supreme Court of Canada (Lexum); ids are Lexum item numbers, "
             "citations like '2024 SCC 10' also work. Legislation = Justice Laws consolidated Acts and "
             "regulations; ids like 'C-46' (Criminal Code), provisions like 'section-718' or 's. 718'. "
             "English text; French at the same sites (/fr/, /fra/). No provincial law, no lower courts.")
    gaps = (
        ("Provincial and territorial legislation: BC Laws API works (not built yet); Ontario "
         "e-Laws is a JS app; rest not researched"),
        "Federal Court, Federal Court of Appeal, Tax Court and tribunals: not researched yet",
        ("Provincial courts: CanLII terms prohibit scraping and it serves a JS challenge; official"
         " court sites not researched yet"),
        ("Constitution Acts 1867-1982: served (law id 'Const'); endnotes (amendment history) left "
         "out, page states no 'current to' date; other constitutional instruments (Manitoba Act, "
         "Constitution Act 1930 etc.) only in the 1990 /eng/ConstRpt/ report, not built"),
        "Federal legislation search is by title only (no full-text search over section text)",
        "French text: same sites at /fr/ and /fra/; source exists but not built yet",
    )
    samples = {
        "caselaw_query": "Charter section 7 fundamental justice",
        "decision_id": "20353",
        "legislation_query": "Criminal Code",
        "law_id": "C-46",
        "provision": "section-718",
    }

    async def search_caselaw(self, query, *, limit, page, filters):
        return await _search_caselaw(query, filters, limit, page)

    async def get_decision(self, id):
        return await _get_decision(id)

    async def search_legislation(self, query, *, limit, page, filters):
        return await _search_legislation(query, filters, limit, page)

    async def get_legislation_toc(self, id):
        return await _get_toc(id)

    async def get_legislation_provision(self, id, provision):
        return await _get_provision(id, provision)

    async def get_legislation_text(self, id):
        return await _get_text(id)
