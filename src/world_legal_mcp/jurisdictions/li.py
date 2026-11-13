"""Liechtenstein: consolidated legislation from Lilex (www.gesetze.li), the official
law database run by the Rechtsdienst der Regierung, and the Supreme Court's (OGH)
own decisions 2020-2025 from www.ogh.li.

Gotchas this code encodes:
  * Ids: the LGBl-Nr as the site shows it, "1921.015" (Verfassung) or "1982.060.001"
    (one act of several in an LGBl issue). URLs use a 10-digit form: year + 3-digit
    number + 3-digit sub-number, "1921015000". Both are accepted, plus "LGBl. 1921 Nr. 15".
  * Search is one GET (/konso/suche) that returns every hit on one page, no paging and
    no snippets; we page locally. Default list is "geltend" (in force). An unknown
    law page answers HTTP 500, which we map to NotFound.
  * The law page /konso/<id> holds title and version list (selected option = current
    version, "01.01.2026" or "01.02.2021 - 31.12.2025"); the text is an iframe at
    /konso/html/<id>?version=N, served as application/octet-stream (UTF-8 HTML).
  * Text HTML: div.art with <a name="art:1"> ("Art. 1") or <a name="par:1"> ("§ 1");
    the ABGB has both, so "Art. 1" and "§ 1" are different provisions there. Marginal
    headings are div.sacht, inside the article or just before it (anchor
    "vorpar:4;sacht:1"). Headings are div.tit1/tit2/... with tit*m numbering lines
    ("I. Hauptstück") before them. After div.tits come the transitional provisions of
    amending acts (their own "Art. 1"...), then div.fntext footnotes; both are kept in
    the full text but not in the TOC.
  * Every page carries a Citrix NetScaler cookie script (sets an "MC" cookie); content
    is served in full without it, so it does not gate access. robots.txt is a 404.
  * Case law: www.gerichtsentscheide.li and www.gerichtsentscheidungen.li (the official
    portal of the Liechtenstein courts, linked from gesetze.li and stgh.li) both serve
    robots.txt "User-agent: * / Disallow: /" (checked 2026-11-06, again 2026-11-10).
  * OGH (www.ogh.li, robots.txt 404): one page per year, /entscheidungen/<year>, with
    every item (AZ, "Urteil vom dd.mm.yyyy", tags = Schlagworte + cited norms) and one
    PDF (text layer) under /files/attachments/. Items before mid-2020 only link to the
    robots-blocked portal, so we read the years >= 2020 from the year <select>. Labels
    are irregular ("OGH 2022.94", "2025.37", "OGH 2021.30+31"; one 2020 PDF bundles 15
    decisions; subtitles have typos like "ovm"), so the id is the PDF file stem
    ("sv-2024-34-ogh-2025-68"). The site's own filter is a keyword ASP.NET postback,
    so we search the cached year lists locally.
"""
from __future__ import annotations

import copy
import datetime
import re

import lxml.html

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc, TocEntry

BASE = "https://www.gesetze.li"
OGH = "https://www.ogh.li"

_MONTHS = {m: i for i, m in enumerate((
    "januar", "februar", "märz", "april", "mai", "juni", "juli", "august", "september",
    "oktober", "november", "dezember"), 1)}
_STATUS = {"in force": "1", "geltend": "1", "repealed": "2", "aufgehoben": "2",
           "all": "0", "beides": "0"}
_STATUS_LABEL = {"1": "in force", "2": "repealed", "0": ""}
_SCOPE = {"national": "1", "landesrecht": "1", "treaties": "2", "staatsverträge": "2",
          "all": "0", "beides": "0"}
_IN = {"text": "text", "fulltext": "text", "volltext": "text", "title": "titel",
       "titel": "titel", "abbreviation": "abk_list", "abk": "abk_list", "abkürzung": "abk_list"}
_HEADING = re.compile(r"^(?:tit\d+m?|tit\d+ue|htit\d+)$")

_law_cache: dict[str, dict] = {}


def _de_date(s: str) -> str:
    """First 'vom 5. Oktober 1921' style date in s -> ISO; else ''."""
    m = re.search(r"(\d{1,2})\.\s*([A-Za-zÄäÖöÜü]+)\s+(\d{4})", s or "")
    if not m or m[2].lower() not in _MONTHS:
        return ""
    try:
        return datetime.date(int(m[3]), _MONTHS[m[2].lower()], int(m[1])).isoformat()
    except ValueError:
        return ""


def _parse_id(law_id: str) -> tuple[str, str]:
    """Any accepted id form -> (LGBl-Nr '1921.015' / '1982.060.001', url key '1921015000')."""
    raw = (law_id or "").strip()
    m = (re.search(r"/konso/(?:html/|pdf/)?(\d{10})\b", raw) or re.fullmatch(r"(\d{10})", raw))
    if m:
        y, n, s = m[1][:4], m[1][4:7], m[1][7:]
    else:
        m = re.fullmatch(r"(?:LGBl\.?\s*)?(\d{4})\s*(?:\.|Nr\.?)\s*(\d{1,3})(?:\.(\d{1,3}))?", raw, re.I)
        if not m:
            raise BadRequest(f"law id {law_id!r} is not an LGBl-Nr. Use e.g. '1921.015' (Verfassung), "
                             "'1003.001' (ABGB), '1926.004' (PGR), '1982.060.001', or the "
                             "10-digit form from a gesetze.li URL ('1921015000').")
        y, n, s = m[1], f"{int(m[2]):03d}", f"{int(m[3] or 0):03d}"
    return f"{y}.{n}" + (f".{s}" if s != "000" else ""), y + n + s


def _norm(label: str) -> tuple[str, str]:
    """'Art. 7a' -> ('art', '7a'); '§ 1' / 'par. 1' -> ('par', '1'); '5' -> ('', '5')."""
    s = (label or "").replace("\xa0", " ").strip().lower()
    kind = "par" if re.match(r"^(§|par|paragraph)", s) else "art" if s.startswith("art") else ""
    s = re.sub(r"^(§+|paragraph|par\.?|artikel|art\.?)\s*", "", s)
    return kind, s.strip().rstrip(".").strip()


def _refs_to_text(root) -> None:
    """Footnote reference links (<a href="#fn3"><sup>3</sup></a>) -> ' [3]'."""
    for a in root.xpath('.//a[starts-with(@href, "#fn")]'):
        num = _http.clean(a.text_content())
        tail = a.tail or ""
        a.clear()
        a.text = f" [{num}]" if num else ""
        a.tail = tail
        a.tag = "span"


async def _fetch(url: str) -> str:
    r = await _http.get(url)
    if r.status_code == 500:
        raise NotFound(f"no law at {url} (gesetze.li answers HTTP 500 for unknown ids)")
    if r.status_code != 200:
        raise SourceError(f"gesetze.li returned HTTP {r.status_code}", r.status_code)
    return r.content.decode("utf-8", errors="replace")


async def _load(law_id: str) -> dict:
    lgbl, key = _parse_id(law_id)
    if key in _law_cache:
        return _law_cache[key]
    page = lxml.html.fromstring(await _fetch(f"{BASE}/konso/{key}"))
    title = _http.clean(" ".join(page.xpath('//h2[contains(@class,"law-title")]//text()')))
    if not title:
        raise SourceError("gesetze.li law page has no title (layout changed?)")
    opt = page.xpath('//select[@name="version"]/option[@selected]')
    version = opt[0].get("value") if opt else ""
    as_of = _http.iso_date((re.findall(r"\d{2}\.\d{2}\.\d{4}", opt[0].text_content()) or [""])[0]) if opt else ""
    lr = page.xpath('//a[starts-with(@href, "/konso/gebietssystematik?lrstart=")]/text()')
    html = await _fetch(f"{BASE}/konso/html/{key}" + (f"?version={version}" if version else ""))
    law = _parse_text(html)
    law.update(lgbl=lgbl, key=key, title=title, as_of=as_of, version=version,
               lr=_http.clean(lr[0]) if lr else "", url=f"{BASE}/konso/{key}")
    return _http.lru_put(_law_cache, key, law, 8)


def _parse_text(html: str) -> dict:
    """Lilex text HTML -> {toc: [TocEntry], provisions: {label: (kind, num, md)}, text: md}."""
    root = lxml.html.fromstring(html)
    _refs_to_text(root)
    footnotes = {}
    for fn in root.xpath('//div[@class="fntext"]'):
        a = fn.xpath('.//a[starts-with(@name, "fn")]')
        if a:
            num = a[0].get("name")[2:]
            footnotes[num] = re.sub(rf"^{re.escape(num)}\s*", "", _http.clean(fn.text_content()))
            a[0].text = f"[{num}]"

    toc: list[TocEntry] = []
    provisions: dict[str, tuple[str, str, str]] = {}
    pending_m = ""            # "I. Hauptstück" line waiting for its title
    pending_sacht = ""        # marginal heading standing before the next article
    art_level = 0
    tits = root.xpath('//div[@class="tits"]')
    for el in root.xpath('//div[@class]'):
        cls = el.get("class").split()[0]
        if cls == "tits":
            if el is not tits[-1]:   # "Allgemeiner Teil" / "Besonderer Teil" (StGB): a part heading
                text = _http.clean(el.text_content())
                if text:
                    toc.append(TocEntry(title=text, level=0))
                continue
            break                    # last one: transitional provisions of amending acts, not in the TOC
        if el.xpath('ancestor::div[contains(concat(" ", @class, " "), " art ")]'):
            continue
        if _HEADING.match(cls) and not cls.startswith("htit"):
            text = re.sub(r"\s*\[\d+\]", "", _http.clean(el.text_content()))
            if not text:
                continue
            if cls.endswith("m"):
                pending_m = f"{pending_m} {text}".strip()
                continue
            level = max(int(re.search(r"\d+", cls)[0]) - 1, 0)
            toc.append(TocEntry(title=f"{pending_m}: {text}" if pending_m else text, level=level))
            art_level = level + 1
            pending_m = pending_sacht = ""
        elif cls == "sacht":
            pending_sacht = re.sub(r"\s*\[\d+\]", "", _http.clean(el.text_content()))
        elif cls == "art":
            anchor = el.xpath('./a[@name]')
            name = anchor[0].get("name") if anchor else ""
            m = re.match(r"^(art|par):(\w+)$", name)
            if not m:
                continue
            kind, num = m[1], m[2]
            label = _http.clean(anchor[0].tail or "") or (f"Art. {num}" if kind == "art" else f"§ {num}")
            inner = el.xpath('./div[@class="sacht"]')
            sacht = " – ".join(x for x in (pending_sacht, _http.clean(inner[0].text_content()) if inner else "") if x)
            sacht = re.sub(r"\s*\[\d+\]", "", sacht)
            pending_sacht = pending_m = ""
            if label in provisions:   # same label twice in one act: keep both, number the later one
                n = 2
                while f"{label} ({n})" in provisions:
                    n += 1
                label = f"{label} ({n})"
            art = copy.deepcopy(el)
            for x in art.xpath('./div[@class="sacht"]'):
                x.drop_tree()
            a0 = art.xpath('./a[@name]')[0]
            a0.tail = ""
            marks = []   # footnote markers right after the label go on the heading line
            while (a0.getnext() is not None and a0.getnext().tag == "span"
                   and not (a0.tail or "").strip()):
                marks.append(_http.clean(a0.getnext().text_content()))
                a0.getnext().drop_tree()   # its tail moves onto a0
            html_art = lxml.html.tostring(art, encoding="unicode")
            body = _http.html_to_md(html_art)
            refs = re.findall(r"\[(\d+)\]", " ".join(marks) + html_art)
            head = f"### {label}" + (f" – {sacht}" if sacht else "") + "".join(f" {m}" for m in marks)
            notes = [f"[{r}] {footnotes[r]}" for r in dict.fromkeys(refs) if r in footnotes]
            md = head + ("\n\n" + body if body else "") + ("\n\nFussnoten:\n\n" + "\n\n".join(notes) if notes else "")
            provisions[label] = (kind, num.lower(), md)
            toc.append(TocEntry(title=label + (f" – {sacht}" if sacht else ""), level=art_level, provision=label))

    body = root.xpath("//body")
    text = _http.html_to_md(lxml.html.tostring(body[0] if body else root, encoding="unicode"))
    return {"toc": toc, "provisions": provisions, "text": text}


_ogh_index: list[dict] = []


async def _ogh_page(year: str) -> lxml.html.HtmlElement:
    r = await _http.get(f"{OGH}/entscheidungen/{year}" if year else f"{OGH}/entscheidungen-des-ogh")
    if r.status_code != 200:
        raise SourceError(f"ogh.li returned HTTP {r.status_code}", r.status_code)
    return lxml.html.fromstring(r.content.decode("utf-8", errors="replace"))


def _ogh_items(root, year: str) -> list[dict]:
    out = []
    for it in root.xpath('//div[@class="item"]'):
        link = it.xpath('.//a[contains(@class,"item__docslink")]')
        href = link[0].get("href", "") if link else ""
        m = re.search(r"/files/attachments/([^/?#]+)\.pdf$", href, re.I)
        if not m:
            continue
        sub = _http.clean(" ".join(it.xpath('.//span[@class="item__subtitle"]//text()')))
        d = re.search(r"(\d{2}\.\d{2}\.\d{4})", sub)
        out.append(dict(
            id=m[1], url=href, year=year,
            az=_http.clean(" ".join(it.xpath("./h2//text()"))),
            label=_http.clean(link[0].text_content()),
            type=(re.match(r"^\s*(\w+)", sub) or [None, ""])[1],
            date=_http.iso_date(d[1]) if d else "",
            tags=[_http.clean(t) for t in it.xpath('./div[contains(@class,"item__tags")]/span/text()')
                  if _http.clean(t)]))
    return out


async def _ogh_load() -> list[dict]:
    """Every OGH item with its own PDF (years >= 2020), newest first; cached per process."""
    if _ogh_index:
        return _ogh_index
    first = await _ogh_page("")
    years = sorted({o for o in first.xpath('//select//option/@value') if o.isdigit() and int(o) >= 2020},
                   reverse=True)
    if not years:
        raise SourceError("ogh.li decisions page has no year list (layout changed?)")
    sel = first.xpath('//select//option[@selected]/@value')
    items = []
    for y in years:
        items += _ogh_items(first if sel and sel[0] == y else await _ogh_page(y), y)
    items.sort(key=lambda i: i["date"], reverse=True)
    _ogh_index[:] = items
    return _ogh_index


def _ogh_id(raw: str) -> str:
    s = (raw or "").strip()
    m = re.search(r"/files/attachments/([^/?#]+?)(?:\.pdf)?$", s, re.I) or re.fullmatch(
        r"([\w.+-]+?)(?:\.pdf)?", s, re.I)
    if not m:
        raise BadRequest(f"decision id {raw!r} is not an ogh.li id. Use the id from search_caselaw, "
                         "e.g. 'sv-2024-34-ogh-2025-68', or the PDF URL.")
    return m[1]


class Liechtenstein(Jurisdiction):
    code = "li"
    name = "Liechtenstein"
    languages = ("de",)
    aliases = ("liechtenstein", "fl", "fürstentum liechtenstein")
    sources = (
        Source(
            name="Lilex – Gesetzesdatenbank des Fürstentums Liechtenstein (Rechtsdienst der Regierung)",
            url=BASE,
            covers=("legislation",),
            licence="unknown (no licence or terms of use published; Impressum/Datenschutz are silent on reuse)",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~25 requests (2026-11); no robots.txt (404)",
            terms_url=f"{BASE}/impressum",
        ),
        Source(
            name="Fürstlicher Oberster Gerichtshof – Entscheidungen (www.ogh.li)",
            url=f"{OGH}/entscheidungen-des-ogh",
            covers=("caselaw",),
            licence=("Impressum: site texts are copyright; commercial use needs prior written "
                     "permission (court decisions themselves are official works)"),
            commercial_use=False,
            ai_use=None,
            auth="none",
            rate_limit="unknown; robots.txt 404 (no Crawl-delay); 1 s spacing, no 429 in ~20 requests (2026-11-10)",
            terms_url=f"{OGH}/impressum",
            warning=("ogh.li Impressum: commercial use of the site's texts needs the court's prior "
                     "written permission."),
            probe={"caselaw_query": "Stiftung", "decision_id": "sv-2024-34-ogh-2025-68"},
        ),
    )
    caselaw_filters = {
        "year": "decision year, 2020-2025 (the years ogh.li publishes itself), or a range '2022-2025'",
    }
    legislation_filters = {
        "status": "in force (default) | repealed | all",
        "scope": "national (Landesrecht) | treaties (Staatsverträge) | all (default)",
        "in": "where the words must appear: text (full text, default) | title | abbreviation",
        "lr": "LR-Nr (systematic number) or its leading digits, e.g. 216 (PGR), 1 (state law); "
              "query may then be empty",
    }
    min_interval = {"www.gesetze.li": 1.0, "www.ogh.li": 1.0}
    notes = ("Consolidated law in German from gesetze.li, ids are LGBl-Nr (1921.015 = Verfassung, "
             "1003.001 = ABGB). Case law: Supreme Court (OGH) decisions 2020-2025 as published on "
             "ogh.li (about 230; search by case number, keyword tag or cited norm, full text via PDF).")
    gaps = (
        "Case law of all courts incl. the full OGH archive before mid-2020 (gerichtsentscheide.li, "
         "gerichtsentscheidungen.li): robots.txt disallows (Disallow: /, rechecked 2026-11-10)",
        "OGH on ogh.li: a selection only (decisions the court chose to post, 2020-2025, none for "
         "2026 yet); search is over case number, tags and cited norms, not the full text",
        "Earlier versions of a law (version list on gesetze.li): source exists and works but not "
         "built yet (current version only)",
    )
    samples = {
        "legislation_query": "Personen- und Gesellschaftsrecht",
        "law_id": "1921.015",
        "provision": "Art. 1",
        "caselaw_query": "Stiftung",
        "decision_id": "sv-2024-34-ogh-2025-68",
    }

    async def search_caselaw(self, query, *, limit, page, filters) -> Results:
        items = await _ogh_load()
        year = str(filters.get("year") or "").strip()
        m = re.fullmatch(r"(\d{4})(?:\s*[-–]\s*(\d{4}))?", year)
        if year and not m:
            raise BadRequest(f"year {year!r}: use a 4-digit year or a range like '2022-2025' (2020-2025)")
        y0, y1 = (m[1], m[2] or m[1]) if m else ("", "")
        words = [w.lower() for w in re.findall(r"[\w§]+", query or "")]
        hits = []
        for i in items:
            hay = " ".join([i["az"], i["label"], i["type"], i["date"], i["id"], *i["tags"]]).lower()
            if (not year or y0 <= i["date"][:4] <= y1) and all(w in hay for w in words):
                hits.append(DecisionHit(
                    id=i["id"], title=f"OGH {i['az']}", court="Fürstlicher Oberster Gerichtshof",
                    date=i["date"], case_number=i["az"], snippet="; ".join(i["tags"])[:300],
                    url=i["url"]))
        start = (page - 1) * limit
        note = ("OGH decisions the court posts on ogh.li (2020-2025, newest first); matches "
                "case number, keyword tags and cited norms, not the full text.")
        if not hits and re.search(r"\b20\d\d\s*[-–]\s*20\d\d\b", query or ""):
            note += (" The query looks like a year range: put the years in the year filter "
                     "(filters={'year': '2022-2025'}) and keep the query to keywords.")
        return Results(items=hits[start:start + limit], total=len(hits), note=note)

    async def get_decision(self, id) -> Decision:
        stem = _ogh_id(id)
        url = f"{OGH}/files/attachments/{stem}.pdf"
        meta = next((i for i in await _ogh_load() if i["id"].lower() == stem.lower()), None)
        if meta:
            url = meta["url"]
        r = await _http.get(url)
        if r.status_code == 404:
            raise NotFound(f"no OGH decision {stem!r} on ogh.li")
        if r.status_code != 200 or not r.content.startswith(b"%PDF"):
            raise SourceError(f"ogh.li returned HTTP {r.status_code} (not a PDF) for {url}", r.status_code)
        text = _http.pdf_text(r.content)
        if not text:
            raise SourceError(f"ogh.li PDF {url} has no text layer")
        md = {}
        if meta:
            md = {"Entscheidungsart": meta["type"], "Bezeichnung": meta["label"],
                  "Schlagworte / Normen": "; ".join(meta["tags"])}
        return Decision(id=stem, title=f"OGH {meta['az']}" if meta else f"OGH {stem}", text=text, url=url,
                        court="Fürstlicher Oberster Gerichtshof", date=meta["date"] if meta else "",
                        case_number=meta["az"] if meta else "",
                        metadata={k: v for k, v in md.items() if v})

    async def search_legislation(self, query, *, limit, page, filters) -> Results:
        q = (query or "").strip()
        f = {k: str(v).strip().lower() for k, v in (filters or {}).items() if str(v).strip()}
        for k, table in (("status", _STATUS), ("scope", _SCOPE), ("in", _IN)):
            if k in f and f[k] not in table:
                raise BadRequest(f"filter {k}={f[k]!r}: use {self.legislation_filters[k]}")
        lr = f.get("lr", "")
        if lr and not re.fullmatch(r"0?\.?\d+(\.\d+)*", lr):
            raise BadRequest(f"filter lr={lr!r}: an LR-Nr like 216 or 0.101, or leading digits like 21")
        params = {"search_text": "", "search_loc": _IN.get(f.get("in", ""), "text"), "lrnr": lr,
                  "lgblid_von": "", "observe_date": datetime.date.today().strftime("%d.%m.%Y"),
                  "compl_list": _STATUS.get(f.get("status", ""), "1"),
                  "rechts_gebiet": _SCOPE.get(f.get("scope", ""), "0")}
        try:
            params["lgblid_von"] = _parse_id(q)[0]
        except BadRequest:
            params["search_text"] = q
        if not q and not lr:
            raise BadRequest("give a query (words, an abbreviation like PGR, or an LGBl-Nr like "
                             "1921.015) or the lr filter")
        r = await _http.get(f"{BASE}/konso/suche", params=params)
        if r.status_code != 200:
            raise SourceError(f"gesetze.li search returned HTTP {r.status_code}", r.status_code)
        doc = lxml.html.fromstring(r.content.decode("utf-8", errors="replace"))
        total_el = doc.xpath('//div[contains(@class,"treffer")]/span/text()')
        rows = doc.xpath('//table[contains(@class,"results")]/tbody/tr')
        if not total_el and not rows:
            return Results(items=[], total=0)
        status = _STATUS_LABEL[params["compl_list"]]
        hits = []
        for tr in rows:
            tds = tr.xpath("./td")
            a = tr.xpath('.//a[starts-with(@href, "/konso/")]')
            if len(tds) < 3 or not a:
                continue
            m = re.match(r"/konso/(\d{10})", a[0].get("href"))
            if not m:
                continue
            title = _http.clean(a[0].text_content())
            lgbl, key = _parse_id(m[1])
            t = re.match(r"^([A-ZÄÖÜ]\w+) vom ", title)
            lrnr = _http.clean(tds[1].text_content())
            hits.append(LawHit(id=lgbl, title=title, type=t[1] if t else "", number=f"LGBl. {lgbl}",
                               date=_de_date(title), status=status,
                               snippet=f"LR {lrnr}" if lrnr else "", url=f"{BASE}/konso/{key}"))
        if params["search_text"]:   # the source does not rank: titles naming the query first
            words = [w.lower() for w in re.findall(r"\w+", q)]

            def rank(h):
                t = h.title.lower()
                return (0 if t.startswith(q.lower()) or f"({q.lower()})" in t
                        else 1 if all(w in t for w in words) else 2)
            hits.sort(key=rank)
        total = int(total_el[0]) if total_el and total_el[0].strip().isdigit() else len(hits)
        start = (page - 1) * limit
        return Results(items=hits[start:start + limit], total=total,
                       note="Hits are not ranked by the source; titles containing the query are listed first.")

    async def get_legislation_toc(self, id) -> Toc:
        law = await _load(id)
        return Toc(id=law["lgbl"], title=law["title"], url=law["url"], entries=law["toc"])

    async def get_legislation_provision(self, id, provision) -> Provision:
        law = await _load(id)
        provs = law["provisions"]
        hit = provs.get(_http.clean(provision))
        if hit is None:
            kind, num = _norm(provision)
            cands = [(lab, v) for lab, v in provs.items()
                     if v[1] == num and (not kind or v[0] == kind) and "(" not in lab]
            if not cands:
                raise NotFound(f"{law['title']} has no provision {provision!r}; see get_legislation_toc "
                               "for labels like 'Art. 1' or '§ 1'.")
            label, hit = cands[0]
        else:
            label = _http.clean(provision)
        return Provision(law_id=law["lgbl"], law_title=law["title"], provision=label, text=hit[2],
                         url=law["url"], as_of=law["as_of"])

    async def get_legislation_text(self, id) -> LawText:
        law = await _load(id)
        meta = {"LGBl-Nr": law["lgbl"], "LR-Nr": law["lr"], "Fassung (version)": law["version"]}
        return LawText(id=law["lgbl"], title=law["title"], text=law["text"], url=law["url"],
                       as_of=law["as_of"], metadata={k: v for k, v in meta.items() if v})
