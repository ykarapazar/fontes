"""Germany (federal): case law from NeuRIS (gated) or, without permission, the Federal Fiscal
Court's own site; consolidated federal law from gesetze-im-internet.de.

Gotchas this code encodes:
  * NeuRIS (testphase.rechtsinformationen.bund.de) is the federal Rechtsinformationsportal
    API, run by DigitalService GmbH for the BMJV. Still labelled a trial service; the old
    `/v1/case-law` path returns 410, use `/v1/rechtsprechung`. Federal courts only
    (BGH, BVerfG, BFH, BVerwG, BAG, BSG, BPatG); no Land courts.
  * Its robots.txt is `Disallow: /` for everyone, but the API is documented for
    application use (docs.rechtsinformationen.bund.de: "you may ... build applications
    that utilise it", 600 req/min per IP). Same template reading as nl/at (unconfirmed).
  * Decision ids are NeuRIS document numbers (KORE303742016). An ECLI is resolved with
    the `ecli` filter. Full text comes from `/v1/rechtsprechung/{id}.html`.
  * NeuRIS legislation is incomplete (no BGB, StGB, GG on 2026-11-05), so legislation
    comes from gesetze-im-internet.de (GII): one xml.zip per law (current version only),
    ids are GII slugs (bgb, gg, stgb, bgbeg). There is no search API: titles are matched
    against gii-toc.xml (1.3 MB, fetched once per process and kept in memory).
  * GII per-provision pages: "§ 823" -> __823.html, "Art 1" -> art_1.html,
    "Art 224 § 1" -> art_224__1.html.
  * Case-law routing: with WLM_PERMITTED=de every case-law call goes to NeuRIS (all federal
    courts). Without it, NeuRIS is skipped and calls go to bundesfinanzhof.de (BFH only):
    robots.txt allows it with Crawl-Delay 60, so the host is throttled to one request a minute.
  * BFH search: GET /de/entscheidungen/entscheidungen-online/ with tx_solr[q], [page],
    [searchTerms][aktenzeichen|ecli|norm] and [creationDateRange][start|end] (decision date,
    dd.mm.yyyy; the form defaults to 01.01.2010, so we always send a start). 10 rows per page,
    no hit count, only the last page number. Detail pages /de/entscheidung/entscheidungen-online/
    detail/STRE.../ use the NeuRIS document numbers, so ids are the same on both routes.
"""
from __future__ import annotations

import io
import re
import zipfile
from urllib.parse import quote

import lxml.html
from lxml import etree

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError, permitted_codes
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

RIS = "https://testphase.rechtsinformationen.bund.de"
GII = "https://www.gesetze-im-internet.de"
BFH = "https://www.bundesfinanzhof.de"
_BFH_SEARCH = f"{BFH}/de/entscheidungen/entscheidungen-online/"

_COURTS = {c.lower(): c for c in ("BGH", "BVerfG", "BFH", "BVerwG", "BAG", "BSG", "BPatG")}
_DOCNR_RE = re.compile(r"^[A-Z]{2,6}\d{6,}$")
_ECLI_RE = re.compile(r"^ECLI:DE:[A-Za-z]+:\d{4}:\S+$", re.I)
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_.\-]*$")
# Topics/courts that the BFH (tax court only) can never answer; searching them just returns noise.
_NON_BFH_RE = re.compile(r"k(?:ü|ue)ndigung|arbeitsgericht|miet(?:vertrag|recht|er\b)|oberlandesgericht|landgericht|"
                         r"amtsgericht|\b(?:olg|lg|ag|bag|bgh)\b", re.I)
_AZ_RE = re.compile(r"^[IVX]{1,5}\s+[A-Z]{1,3}\s+\d{1,4}/\d{2}$")   # BFH file number: IX R 16/25
_LABEL_RE = re.compile(r"^(§+|par\.?|paragraph|art\.?|artikel|article)?\s*(\d+\s*[a-z]?)\.?$", re.I)

_law_cache: dict[str, dict] = {}
_gii_toc: list[tuple[str, str]] = []   # (slug, title)


# --------------------------------------------------------------------------- #
# Case law (NeuRIS)
# --------------------------------------------------------------------------- #
async def _ris_json(path: str, params: dict) -> dict:
    r = await _http.get(RIS + path, params=params, headers={"Accept": "application/json"})
    if r.status_code != 200:
        raise SourceError(_http.error("NeuRIS", f"{path} failed", r.status_code), r.status_code)
    try:
        return r.json()
    except ValueError:
        raise SourceError("NeuRIS returned a non-JSON answer", r.status_code)


def _strip_rn(s: str) -> str:
    """NeuRIS JSON glues Randnummer link text onto sentences ("...Einbauküche.20")."""
    return re.sub(r"(?<=[.!?:;)])\d+(?=\s|$)", "", s)


def _decision_url(docnr: str) -> str:
    return f"{RIS}/gerichtsentscheidungen/{docnr}"


def _decision_hit(m: dict) -> DecisionHit:
    it = m.get("item") or {}
    docnr = it.get("documentNumber", "")
    names = [n for n in (it.get("decisionName") or []) if n]
    files = it.get("fileNumbers") or []
    court = it.get("courtName") or it.get("courtType") or ""
    line = _http.clean(it.get("titleLine")).strip("()")
    matches = (_http.clean(re.sub(r"</?mark>", "", t.get("text") or "")).strip("()")
               for t in m.get("textMatches") or [])
    match = next((t for t in matches if t and t not in line), "")
    snippet = _strip_rn(" — ".join(x for x in (line, match) if x))
    return DecisionHit(
        id=docnr,
        title=_http.clean(names[0] if names else it.get("headline") or f"{court} {', '.join(files)}"),
        court=court, date=_http.iso_date(it.get("decisionDate")), case_number=", ".join(files),
        snippet=snippet[:400], url=_decision_url(docnr))


async def _resolve_ecli(ecli: str) -> str:
    d = await _ris_json("/v1/rechtsprechung", {"ecli": ecli, "size": 1})
    for m in d.get("member") or []:
        if (m.get("item") or {}).get("ecli", "").lower() == ecli.lower():
            return m["item"]["documentNumber"]
    raise NotFound(f"no federal decision with ECLI {ecli} in NeuRIS")


def _decision_md(html: bytes) -> str:
    root = lxml.html.fromstring(html)
    for el in root.xpath("//template | //script | //style | //h1"
                         " | //a[contains(@class, 'border-number-link')]"):
        el.drop_tree()
    # Randnummer lists (<dl class="border-number"><dt>1</dt><dd>..</dd>) -> "[1] text".
    for dl in root.xpath("//dl[contains(@class, 'border-number')]"):
        num = _http.clean(dl.findtext("dt"))
        dd = dl.find("dd")
        if dd is not None and num:
            first = dd.find(".//p")
            if first is not None:
                first.text = f"[{num}] " + (first.text or "")
            dd.tag = "div"
            dl.addprevious(dd)
        dl.drop_tree()
    body = root.find("body")
    return _http.html_to_md(etree.tostring(body if body is not None else root,
                                           encoding="unicode", method="html"))


# --------------------------------------------------------------------------- #
# Case law without permission (bundesfinanzhof.de)
# --------------------------------------------------------------------------- #
def _de_dmy(iso: str) -> str:
    y, m, d = iso.split("-")
    return f"{d}.{m}.{y}"


async def _bfh_page(params: dict) -> lxml.html.HtmlElement:
    r = await _http.get(_BFH_SEARCH, params=params)
    if r.status_code != 200:
        raise SourceError(_http.error("bundesfinanzhof.de", "search", r.status_code), r.status_code)
    return lxml.html.fromstring(r.content)


def _bfh_rows(root) -> list[DecisionHit]:
    out = []
    for tr in root.xpath('//tr[td[@data-label="Aktenzeichen"]]'):
        cell = {td.get("data-label"): _http.clean(td.text_content()) for td in tr.xpath("./td")}
        a = tr.xpath('.//a[contains(@href, "/detail/")]')
        m = re.search(r"/detail/([A-Z]{2,6}\d{6,})", a[0].get("href", "")) if a else None
        if not m:
            continue
        az = cell.get("Aktenzeichen", "")
        snippet = " · ".join(v for v in (cell.get("Senat", ""), cell.get("V/NV", "") and
                                         f"V/NV: {cell['V/NV']}") if v)
        out.append(DecisionHit(id=m[1], title=cell.get("Titel") or f"BFH {az}", court="BFH",
                               date=_http.iso_date(cell.get("Entscheidung vom", "")), case_number=az,
                               snippet=snippet, url=f"{BFH}/de/entscheidung/entscheidungen-online/detail/{m[1]}/"))
    return out


def _bfh_last_page(root) -> int:
    hrefs = " ".join(root.xpath("//a/@href"))
    pages = [int(n) for t in re.findall(r"tx_solr%5Bpage%5D=(\d+)|tx_solr\[page\]=(\d+)", hrefs)
             for n in t if n]
    return max(pages, default=1)


def _bfh_md(body) -> str:
    parts = []
    for el in body:
        cls = el.get("class") or ""
        if el.tag == "h2" or el.tag == "h3":
            parts.append(("## " if el.tag == "h2" else "### ") + _http.clean(el.text_content()))
        elif "m-decisions" in cls:
            for sub in el:
                if sub.tag == "h3":
                    parts.append("### " + _http.clean(sub.text_content()))
                elif sub.tag == "ol":
                    for li in sub.xpath("./li"):
                        rd = li.get("data-rd")
                        txt = "\n\n".join(_http.clean(p.text_content()) for p in li.xpath("./*")
                                           ) or _http.clean(li.text_content())
                        parts.append(f"[{rd}] {txt}" if rd else txt)
                else:
                    parts.append(_http.clean(sub.text_content()))
    return "\n\n".join(p for p in parts if p.strip())


async def _bfh_decision(ref: str) -> Decision:
    url = f"{BFH}/de/entscheidung/entscheidungen-online/detail/{quote(ref)}/"
    r = await _http.get(url)
    if r.status_code == 404:
        raise NotFound(f"no BFH decision {ref} on bundesfinanzhof.de")
    if r.status_code != 200:
        raise SourceError(_http.error("bundesfinanzhof.de", f"decision {ref}", r.status_code), r.status_code)
    root = lxml.html.fromstring(r.content)
    art = root.xpath('//article[contains(@class,"m-article--full")][.//div[@class="m-article__body"]]')
    body = root.xpath('//div[@class="m-article__body"]')
    if not art or not body:
        raise NotFound(f"no BFH decision {ref} on bundesfinanzhof.de (page has no decision text)")
    art, body = art[-1], body[0]
    head = _http.clean(" ".join(art.xpath('.//div[@class="m-article__header"]//text()')))
    intro = _http.clean(" ".join(art.xpath('.//div[@class="m-article__intro"]//text()')))
    m = re.match(r"^(\w+)\s+vom\s+(.+?),\s*(.+)$", head)
    kind, date, az = (m[1], _bfh_date(m[2]), m[3]) if m else ("", "", head)
    pick = lambda c: _http.clean(" ".join(body.xpath(f'./p[contains(@class,"{c}")]//text()')))
    leits = body.xpath('./h2[normalize-space()="Leitsätze"]/following-sibling::div[1]')
    meta = {k: v for k, v in (("ECLI", pick("ecli")), ("Dokumenttyp", kind),
                              ("Spruchkörper", pick("spruchkoerper")), ("Normen", pick("norms")),
                              ("Vorinstanzen", pick("vorinstanz"))) if v}
    return Decision(id=ref, title=intro or f"BFH {az}", text=_bfh_md(body), url=url, court="BFH",
                    date=date, case_number=az,
                    summary="\n\n".join(_http.clean(p.text_content()) for p in leits[0]) if leits else "",
                    metadata=meta)


def _bfh_date(s: str) -> str:
    """'02. September 2026' -> '2026-09-02'."""
    months = ("januar februar märz april mai juni juli august september oktober november "
              "dezember").split()
    m = re.match(r"(\d{1,2})\.\s*(\w+)\s+(\d{4})", s.strip())
    if m and m[2].lower() in months:
        return f"{m[3]}-{months.index(m[2].lower()) + 1:02d}-{int(m[1]):02d}"
    return _http.iso_date(s)


# --------------------------------------------------------------------------- #
# Legislation (gesetze-im-internet.de)
# --------------------------------------------------------------------------- #
_XML2HTML = {"P": "p", "BR": "br", "DL": "dl", "DT": "dt", "DD": "dd", "LA": "span",
             "SP": "span", "B": "b", "I": "i", "U": "u", "SUP": "sup", "SUB": "sub",
             "pre": "pre", "table": "table", "row": "tr", "entry": "td", "Title": "p",
             "Subtitle": "p", "FnR": "span", "NB": "span", "small": "span"}


def _content_md(el) -> str:
    """GII <Content> XML (P, BR, DL/DT/DD, CALS tables) -> markdown."""
    if el is None:
        return ""
    el = etree.fromstring(etree.tostring(el))  # work on a copy
    for x in el.iter():
        if not isinstance(x.tag, str):
            continue
        tag = _XML2HTML.get(x.tag)
        if tag:
            x.tag = tag
        elif x.tag in ("tgroup", "tbody", "thead", "Content"):
            x.tag = "div" if x.tag == "Content" else x.tag
        elif x.tag in ("colspec", "IMG", "img"):
            x.tag = "span"
            x.text = ""
        else:
            x.tag = "span"
        x.attrib.clear()
    html = etree.tostring(el, encoding="unicode", method="html")
    html = re.sub(r"</?(tgroup|tbody|thead)\b[^>]*>", "", html)
    # DT/DD pairs read best as "a) text" on one line.
    html = re.sub(r"(?s)<dt>(.*?)</dt>\s*<dd>", r"<p>\1 ", html).replace("</dd>", "</p>")
    html = re.sub(r"</?dl>", "", html)
    return _http.html_to_md(html)


def _label(enbez: str) -> str:
    """'Art 1' -> 'Art. 1'; '§ 823' stays; others ('Präambel', 'Anlage 1') unchanged."""
    s = _http.clean(enbez)
    return re.sub(r"^Art\b\.?\s*", "Art. ", s)


def _key(label: str) -> tuple[str, str] | None:
    """Normalise a label to (kind, number): '§ 823' -> ('§', '823'), 'Art. 1' -> ('art', '1')."""
    m = _LABEL_RE.match(_http.clean(label))
    if not m:
        return None
    kind = (m[1] or "").lower().rstrip(".")
    kind = "art" if kind in ("art", "artikel", "article") else ("§" if kind else "")
    return kind, m[2].replace(" ", "").lower()


def _provision_url(slug: str, enbez: str) -> str:
    s = _http.clean(enbez)
    if re.match(r"^(Art|§)\s*\d", s):
        f = re.sub(r"§\s*", "__", re.sub(r"^Art\s*", "art_", s)).replace(" ", "").lower()
        if re.fullmatch(r"[a-z0-9_]+", f):
            return f"{GII}/{slug}/{f}.html"
    return f"{GII}/{slug}/index.html"


def _slug(law_id: str) -> str:
    s = _http.clean(law_id).lower()
    m = re.match(r"^https?://www\.gesetze-im-internet\.de/([^/]+)", s)
    if m:
        s = m[1]
    if not _SLUG_RE.match(s):
        raise BadRequest(f"law id {law_id!r} is not a gesetze-im-internet.de id. Use the "
                         "slug from search_legislation, e.g. 'bgb', 'gg', 'stgb'.")
    return s


async def _law(law_id: str) -> dict:
    slug = _slug(law_id)
    if slug in _law_cache:
        return _law_cache[slug]
    r = await _http.get(f"{GII}/{slug}/xml.zip")
    if r.status_code == 404:
        raise NotFound(f"no law {slug!r} on gesetze-im-internet.de; search_legislation finds ids.")
    if r.status_code != 200 or not r.content.startswith(b"PK"):
        raise SourceError(_http.error("gesetze-im-internet.de", f"{slug}/xml.zip failed",
                                      r.status_code), r.status_code)
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        name = next((n for n in z.namelist() if n.lower().endswith(".xml")), None)
        if not name:
            raise SourceError(f"gesetze-im-internet.de: no XML in {slug}/xml.zip")
        root = etree.fromstring(z.read(name))
    norms = root.findall("norm")
    if not norms:
        raise SourceError(f"gesetze-im-internet.de: {slug} XML has no norms")
    head = norms[0].find("metadaten")
    title = _http.text(head.find("langue")) or _http.text(head.find("kurzue")) or slug
    abbr = _http.text(head.find("jurabk"))
    stand = "; ".join(_http.text(s.find("standkommentar")) for s in head.findall("standangabe")
                      if s.find("standkommentar") is not None)
    items = []   # (kind, level, label, heading, md)
    for n in norms[1:]:
        md_el = n.find("metadaten")
        g = md_el.find("gliederungseinheit")
        enbez = _http.text(md_el.find("enbez"))
        titel = _http.text(md_el.find("titel"))
        body = _content_md(n.find("textdaten/text/Content"))
        if g is not None and not enbez:
            kz = _http.text(g.find("gliederungskennzahl"))
            heading = " ".join(x for x in (_http.text(g.find("gliederungsbez")),
                                           _http.text(g.find("gliederungstitel"))) if x)
            items.append(("h", max(0, len(kz) // 3 - 1), "", heading, body))
        elif enbez:
            items.append(("p", 0, _label(enbez), enbez, titel, body))
    # Provisions sit one level below the heading that precedes them.
    entries, provs, level = [], {}, 0
    for it in items:
        if it[0] == "h":
            level = it[1] + 1
            entries.append(TocEntry(title=it[3], level=it[1]))
        else:
            _, _, label, enbez, titel, body = it
            entries.append(TocEntry(title=" ".join(x for x in (label, titel) if x),
                                    level=level, provision=label))
            provs.setdefault(label, (enbez, titel, body))
    law = {"slug": slug, "title": title, "abbr": abbr, "stand": stand, "items": items,
           "entries": entries, "provs": provs, "url": f"{GII}/{slug}/index.html"}
    return _http.lru_put(_law_cache, slug, law, 6)


async def _toc_index() -> list[tuple[str, str]]:
    if not _gii_toc:
        r = await _http.get(f"{GII}/gii-toc.xml")
        if r.status_code != 200:
            raise SourceError(_http.error("gesetze-im-internet.de", "gii-toc.xml failed",
                                          r.status_code), r.status_code)
        root = etree.fromstring(r.content, etree.XMLParser(load_dtd=False, no_network=True,
                                                            resolve_entities=False))
        for item in root.iter("item"):
            m = re.search(r"gesetze-im-internet\.de/([^/]+)/xml\.zip", item.findtext("link") or "")
            if m:
                _gii_toc.append((m[1], _http.clean(item.findtext("title"))))
    return _gii_toc


class Germany(Jurisdiction):
    code = "de"
    name = "Germany (federal)"
    languages = ("de",)
    aliases = ("germany", "deutschland", "deu", "bund")
    sources = (
        Source(
            name="NeuRIS – Rechtsinformationsportal des Bundes (API, trial service)",
            url="https://docs.rechtsinformationen.bund.de",
            covers=("caselaw",),
            licence="No licence stated; court decisions are public-domain official works "
                    "(§ 5 UrhG)",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="documented: 600 req/min per IP, 503 above "
                       "(docs.rechtsinformationen.bund.de/guides/rate-limiting, 2026-11-05)",
            terms_url="https://testphase.rechtsinformationen.bund.de/impressum",
            needs_permission=True,
            warning=("NeuRIS is a trial service whose robots.txt disallows all automated "
                     "access (Disallow: /). Get explicit permission from the operator "
                     "(DigitalService / BMJV) before relying on it."),
            probe={"caselaw_query": "Mietminderung", "decision_id": "KORE303742016"},
        ),
        Source(
            name="Bundesfinanzhof – Entscheidungen online (bundesfinanzhof.de)",
            url=_BFH_SEARCH,
            covers=("caselaw",),
            licence="Impressum: decisions are official works (§ 5 UrhG), free to use",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="robots.txt Crawl-Delay: 60 (2026-11-10); throttled to 1 request per 60 s",
            terms_url=f"{BFH}/de/impressum/",
            probe={"caselaw_query": "Verständigungsvereinbarung", "decision_id": "STRE202610201"},
        ),
        Source(
            name="Gesetze im Internet (Bundesamt für Justiz / BMJV)",
            url=GII,
            covers=("legislation",),
            licence="No licence stated; statutes are public-domain official works (§ 5 UrhG)",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen (2026-11-05)",
            terms_url=f"{GII}/hinweise.html",
        ),
    )
    caselaw_filters = {
        "court": "Federal court: BGH, BVerfG, BFH, BVerwG, BAG, BSG or BPatG (without "
                 "WLM_PERMITTED=de only BFH is available)",
        "date_from": "Decision date on or after, YYYY-MM-DD",
        "date_to": "Decision date on or before, YYYY-MM-DD",
    }
    min_interval = {"testphase.rechtsinformationen.bund.de": 0.5,
                    "www.gesetze-im-internet.de": 1.0,
                    "www.bundesfinanzhof.de": 60.0}
    notes = ("Federal level only. Case law: NeuRIS (all federal courts, needs WLM_PERMITTED=de); "
             "otherwise the Federal Fiscal Court (BFH) from its own site, 1 request/min. "
             "Legislation: current consolidated texts from gesetze-im-internet.de; ids are "
             "GII slugs ('bgb', 'gg', 'stgb').")
    gaps = (
        "BGH, BVerfG, BVerwG, BAG, BSG, BPatG case law: only via NeuRIS, whose robots.txt says 'Disallow: /'; off unless WLM_PERMITTED=de (needs permission)",
        "Federal courts' own sites (checked 2026-11-10): BGH and BSG searches sit under robots-disallowed /SiteGlobals/; BVerwG search is behind a bot challenge; BAG terms need permission for any use of texts/database; rechtsprechung-im-internet.de robots 'Disallow: /'",
        "BFH without permission: only decisions the court publishes online (V and NV), 2010 on; slow (robots Crawl-Delay 60 = 1 request/min)",
        "Land (state) court decisions (OLG, LG, AG, Land admin courts): no official API; per-Land portals not researched yet",
        "Land (state) legislation of the 16 Länder: per-Land portals not researched yet",
        "Earlier versions of federal laws: gesetze-im-internet.de serves the current version only",
    )
    samples = {
        "caselaw_query": "Verständigungsvereinbarung",
        "decision_id": "STRE202610201",
        "legislation_query": "Bürgerliches Gesetzbuch",
        "law_id": "bgb",
        "provision": "§ 823",
    }

    # ---------------------------------------------------------------- case law
    async def search_caselaw(self, query, *, limit, page, filters):
        if self.code not in permitted_codes():
            return await self._bfh_search(query, limit=limit, page=page, filters=filters)
        params = {"searchTerm": query, "size": max(1, min(int(limit), 100)),
                  "pageIndex": max(0, int(page) - 1)}
        court = (filters.get("court") or "").strip()
        if court:
            if court.lower() not in _COURTS:
                raise BadRequest(f"court {court!r} unknown. Use one of: {', '.join(_COURTS.values())}.")
            params["court"] = _COURTS[court.lower()]
        for key, param in (("date_from", "dateFrom"), ("date_to", "dateTo")):
            v = (filters.get(key) or "").strip()
            if v:
                if not _DATE_RE.match(v):
                    raise BadRequest(f"{key} must be YYYY-MM-DD, got {v!r}.")
                params[param] = v
        d = await _ris_json("/v1/rechtsprechung", params)
        items = [_decision_hit(m) for m in d.get("member") or []][:params["size"]]
        return Results(items=items, total=d.get("totalItems"),
                       note="Federal courts only (NeuRIS trial service); no Land courts.")

    async def get_decision(self, id):
        ref = _http.clean(id)
        if self.code not in permitted_codes():
            return await self._bfh_get(ref)
        if _ECLI_RE.match(ref):
            ref = await _resolve_ecli(ref)
        if not _DOCNR_RE.match(ref):
            raise BadRequest(f"{id!r} is not a NeuRIS document number (e.g. 'KORE303742016') "
                             "or a German ECLI.")
        meta = await _http.get(f"{RIS}/v1/rechtsprechung/{quote(ref)}",
                               headers={"Accept": "application/json"})
        if meta.status_code == 404:
            raise NotFound(f"no decision {ref} in NeuRIS")
        if meta.status_code != 200:
            raise SourceError(_http.error("NeuRIS", f"decision {ref}", meta.status_code),
                              meta.status_code)
        m = meta.json()
        r = await _http.get(f"{RIS}/v1/rechtsprechung/{quote(ref)}.html")
        if r.status_code != 200:
            raise SourceError(_http.error("NeuRIS", f"decision {ref} HTML", r.status_code),
                              r.status_code)
        files = m.get("aktenzeichenListe") or ([m["aktenzeichen"]] if m.get("aktenzeichen") else [])
        court = m.get("gericht") or ""
        meta_out = {k: v for k, v in (
            ("ECLI", m.get("ecli") or ""),
            ("Dokumenttyp", m.get("dokumenttyp") or ""),
            ("Spruchkörper", m.get("spruchkoerper") or ""),
            ("Normen", "; ".join(m.get("normenkette") or [])),
            ("Vorinstanzen", "; ".join(m.get("vorgehendeEntscheidungen") or [])),
        ) if v}
        return Decision(
            id=ref, title=_http.clean(m.get("kurztitel") or f"{court} {', '.join(files)}"),
            text=_decision_md(r.content), url=_decision_url(ref), court=court,
            date=_http.iso_date(m.get("datum")), case_number=", ".join(files),
            summary=_strip_rn(_http.clean(m.get("leitsatz") or m.get("orientierungssatz") or "")),
            metadata=meta_out)

    async def _bfh_search(self, query, *, limit, page, filters):
        court = (filters.get("court") or "").strip()
        if court and court.lower() != "bfh":
            raise BadRequest(f"court {court!r} is not available in this setup: only the Federal "
                             "Fiscal Court (court 'BFH', tax law) is searched. BGH, BVerfG, BVerwG, "
                             "BAG, BSG, BPatG are not available here; OLG/LG/AG and other "
                             "Land courts have no source here.")
        q = _http.clean(query)
        scope = ("BFH only: this is the tax court. No labour (BAG), civil (BGH), constitutional "
                 "(BVerfG) or Land/appeal/first-instance (OLG, LG, AG) decisions here.")
        if _NON_BFH_RE.search(q):
            return Results(items=[], total=0, note=(
                f"{scope} Your query is about a non-tax topic or a court that is not covered, so "
                "nothing was searched; the BFH would only return unrelated tax decisions."))
        params = {"tx_solr[q]": "" if _AZ_RE.match(q) else q, "tx_solr[creationDateRange][start]": "01.01.1900",
                  "tx_solr[creationDateRange][end]": _de_dmy(_http.today())}
        for key, param in (("date_from", "start"), ("date_to", "end")):
            v = (filters.get(key) or "").strip()
            if v:
                if not _DATE_RE.match(v):
                    raise BadRequest(f"{key} must be YYYY-MM-DD, got {v!r}.")
                params[f"tx_solr[creationDateRange][{param}]"] = _de_dmy(v)
        if _AZ_RE.match(q):
            params["tx_solr[searchTerms][aktenzeichen]"] = q
        # The site pages by 10; serve the requested window from the pages that cover it.
        limit = max(1, min(int(limit), 30))
        first, last = (page - 1) * limit, page * limit
        hits, last_page = [], 1
        for p in range(first // 10 + 1, (last - 1) // 10 + 2):
            root = await _bfh_page({**params, "tx_solr[page]": str(p)})
            last_page = _bfh_last_page(root)
            rows = _bfh_rows(root)
            hits += rows
            if len(rows) < 10 or p >= last_page:
                break
        start = first - (first // 10) * 10
        return Results(items=hits[start:start + limit], total=None,
                       note=(f"{scope} Hits are full-text matches that the court's site lists newest "
                             "first, NOT by relevance, so many may only mention the search word in "
                             "passing. All words must appear, so generic words like 'Steuer' add nothing; put an exact "
                             'phrase in double quotes ("Gewinnermittlung durch '
                             'Einnahmenüberschussrechnung") or add a date range, then read the decision. '
                             "The site gives no total; 1 request/min (robots Crawl-Delay 60), "
                             "so keep limit at 10 or less."))

    async def _bfh_get(self, ref):
        if _ECLI_RE.match(ref):
            if not ref.upper().startswith("ECLI:DE:BFH:"):
                raise BadRequest(f"{ref!r} is not a BFH ECLI; only BFH decisions "
                                 "are available here.")
            rows = _bfh_rows(await _bfh_page({"tx_solr[q]": "",
                                              "tx_solr[searchTerms][ecli]": ref,
                                              "tx_solr[creationDateRange][start]": "01.01.1900"}))
            if not rows:
                raise NotFound(f"no BFH decision with {ref} on bundesfinanzhof.de")
            ref = rows[0].id
        if not _DOCNR_RE.match(ref):
            raise BadRequest(f"{ref!r} is not a BFH document number (e.g. 'STRE202610201', from "
                             "search_caselaw) or a BFH ECLI.")
        return await _bfh_decision(ref)

    # ------------------------------------------------------------- legislation
    async def search_legislation(self, query, *, limit, page, filters):
        q = _http.clean(query).lower()
        if not q:
            raise BadRequest("query is empty.")
        words = q.split()
        hits = []
        for slug, title in await _toc_index():
            t = title.lower()
            if q == slug:
                rank = 0
            elif t == q:
                rank = 1
            elif all(w in t or w == slug for w in words):
                rank = 2 if t.startswith(q) else 3
            else:
                continue
            hits.append((rank, len(title), slug, title))
        if not hits and len(words) == 1 and len(q) > 12:
            # Popular compound names (Lieferkettensorgfaltspflichtengesetz): count the title's
            # long words, cut to a stem, that sit inside the query; two or more is a match.
            for slug, title in await _toc_index():
                stems = {w[:-2] if len(w) > 8 else w for w in re.findall(r"\w{10,}", title.lower())}
                n = sum(1 for st in stems if st in q)
                if n >= 2:
                    hits.append((4 - n, len(title), slug, title))
        hits.sort()
        size = max(1, int(limit))
        start = (max(1, int(page)) - 1) * size
        items = [LawHit(id=slug, title=title, url=f"{GII}/{slug}/index.html")
                 for _, _, slug, title in hits[start:start + size]]
        return Results(items=items, total=len(hits),
                       note="Title / id search over gesetze-im-internet.de (current federal "
                            "law only). Ids are GII slugs, e.g. 'bgb'.")

    async def get_legislation_toc(self, id):
        law = await _law(id)
        return Toc(id=law["slug"], title=law["title"], url=law["url"], entries=law["entries"])

    async def get_legislation_provision(self, id, provision):
        law = await _law(id)
        provs = law["provs"]
        label = _http.clean(provision)
        hit = label if label in provs else None
        if not hit:
            k = _key(label)
            if k is None:
                raise BadRequest(f"provision {provision!r} not understood. Use e.g. '§ 823', "
                                 "'823', 'Art. 1', or a label from get_legislation_toc.")
            cands = [p for p in provs if (pk := _key(p)) and pk[1] == k[1]
                     and (not k[0] or pk[0] == k[0])]
            if not cands:
                raise NotFound(f"{law['abbr'] or law['slug']} has no provision {provision!r}.")
            cands.sort(key=lambda p: 0 if _key(p)[0] == "§" else 1)
            hit = cands[0]
        enbez, titel, body = provs[hit]
        text = f"### {' '.join(x for x in (hit, titel) if x)}\n\n{body or '(no text)'}"
        return Provision(law_id=law["slug"], law_title=law["title"], provision=hit, text=text,
                         url=_provision_url(law["slug"], enbez))

    async def get_legislation_text(self, id):
        law = await _law(id)
        parts = []
        for it in law["items"]:
            if it[0] == "h":
                parts.append(f"{'#' * min(6, 2 + it[1])} {it[3]}")
                if it[4]:
                    parts.append(it[4])
            else:
                _, _, label, _, titel, body = it
                parts.append(f"#### {' '.join(x for x in (label, titel) if x)}")
                if body:
                    parts.append(body)
        md = {"Abkürzung": law["abbr"], "Stand": law["stand"]}
        return LawText(id=law["slug"], title=law["title"], text="\n\n".join(parts), url=law["url"],
                       metadata={k: v for k, v in md.items() if v})
