"""Czechia: case law from rozhodnuti.justice.cz, legislation from e-Sbírka.

Gotchas this code encodes:
  * rozhodnuti.justice.cz (Ministry of Justice) publishes anonymised decisions of
    district, regional and high courts since 2020 only; NS, NSS and ÚS are not in it.
    Search uses the website backend /api/finaldoc (no auth). It has no relevance
    sort: we ask for newest-published first. searchText is repeated once per word,
    with searchMode=ALL (all words must occur), like the website.
  * The id is the ECLI. /api/finaldoc?ecli= resolves it to the internal uuid;
    a bare uuid is accepted too. Anonymised spans come as placeholders
    ("Jméno žalobce") and are rendered as [Jméno žalobce].
  * e-Sbírka REST (/sbr-cache) is the backend of e-sbirka.gov.cz. A law is
    addressed by its staleUrl "/sb/{year}/{number}"; without a date suffix the
    metadata call returns the current consolidated version. Its text comes as
    flat "fragments" (1000 per page, the civil code has 11 pages) with a depth
    (hloubka): a § is its Paragraf fragment plus every deeper fragment after it.
    There is no per-§ endpoint, so pages are fetched in order and kept in memory.
  * Supreme Court: sbirka.nsoud.cz (WordPress) is the official Sbírka; its search is a
    GET form with /strana/N/ paging. rozhodnuti.nsoud.cz (all NS decisions) is
    robots-blocked for '*'. Supreme Administrative Court: vyhledavac.nssoud.cz is an
    ASP.NET form; the blank form is posted back with the text field filled, the court
    tree's leaf ids go in '<field>Selected', and later pages come from
    /Home/MyResTRowsCont (40 rows each).
"""
from __future__ import annotations

import re
from urllib.parse import quote, urlencode

import lxml.html

from markdownify import markdownify as _md

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

RJ = "https://rozhodnuti.justice.cz"
SBR = "https://e-sbirka.gov.cz/sbr-cache"
_SBR_PAGE = 100   # fixed e-Sbírka search page size (see search_legislation)
ESBIRKA = "https://e-sbirka.gov.cz"
SBIRKA = "https://sbirka.nsoud.cz"
NSSV = "https://vyhledavac.nssoud.cz"

_COURTS = {
    "KSBR": "Krajský soud v Brně", "KSCB": "Krajský soud v Českých Budějovicích",
    "KSHK": "Krajský soud v Hradci Králové", "KSBRJI": "Krajský soud v Brně, pobočka Jihlava",
    "KSBRZL": "Krajský soud v Brně, pobočka Zlín",
    "KSPLKV": "Krajský soud v Plzni, pobočka Karlovy Vary", "KSOS": "Krajský soud v Ostravě",
    "KSPH": "Krajský soud v Praze", "KSPL": "Krajský soud v Plzni",
    "KSUL": "Krajský soud v Ústí nad Labem", "MSBR": "Městský soud v Brně",
    "MSPH": "Městský soud v Praze", "NS": "Nejvyšší soud", "NSS": "Nejvyšší správní soud",
    "OSBI": "Okresní soud Brno-Venkov", "OSBK": "Okresní soud v Blansku",
    "OSBN": "Okresní soud v Benešově", "OSBR": "Okresní soud v Berouně",
    "OSBU": "Okresní soud v Bruntále", "OSBV": "Okresní soud v Břeclavi",
    "OSCB": "Okresní soud v Českých Budějovicích", "OSCH": "Okresní soud v Chebu",
    "OSCK": "Okresní soud v Českém Krumlově", "OSCL": "Okresní soud v České Lípě",
    "OSCR": "Okresní soud v Chrudimi", "OSCV": "Okresní soud v Chomutově",
    "OSDC": "Okresní soud v Děčíně", "OSDO": "Okresní soud v Domažlicích",
    "OSFM": "Okresní soud ve Frýdku-Místku", "OSHB": "Okresní soud v Havlíčkově Brodě",
    "OSHK": "Okresní soud v Hradci Králové", "OSHO": "Okresní soud v Hodoníně",
    "OSNJ": "Okresní soud v Novém Jičíně", "OSJC": "Okresní soud v Jičíně",
    "OSJE": "Okresní soud v Jeseníku", "OSJH": "Okresní soud v Jindřichově Hradci",
    "OSJI": "Okresní soud v Jihlavě", "OSJN": "Okresní soud v Jablonci nad Nisou",
    "OSKD": "Okresní soud v Kladně", "OSKH": "Okresní soud v Kutné Hoře",
    "OSKI": "Okresní soud v Karviné", "OSKM": "Okresní soud v Kroměříži",
    "OSKO": "Okresní soud v Kolíně", "OSKT": "Okresní soud v Klatovech",
    "OSKV": "Okresní soud v Karlových Varech", "OSLI": "Okresní soud v Liberci",
    "OSLN": "Okresní soud v Lounech", "OSLT": "Okresní soud v Litoměřicích",
    "OSMB": "Okresní soud v Mladé Boleslavi", "OSME": "Okresní soud v Mělníku",
    "OSMO": "Okresní soud v Mostě", "OSNA": "Okresní soud v Náchodě",
    "OSNB": "Okresní soud v Nymburce", "OSOL": "Okresní soud v Olomouci",
    "OSOP": "Okresní soud v Opavě", "OSOV": "Okresní soud v Ostravě",
    "OSPB": "Okresní soud v Příbrami", "OSPE": "Okresní soud v Pelhřimově",
    "OSPI": "Okresní soud v Písku", "OSPJ": "Okresní soud Plzeň-jih",
    "OSPM": "Okresní soud Plzeň-město", "OSPR": "Okresní soud v Přerově",
    "OSPS": "Okresní soud Plzeň-sever", "OSPT": "Okresní soud v Prachaticích",
    "OSPU": "Okresní soud v Pardubicích", "OSPV": "Okresní soud v Prostějově",
    "OSPY": "Okresní soud Praha-východ", "OSPZ": "Okresní soud Praha-západ",
    "OSRA": "Okresní soud v Rakovníku", "OSRK": "Okresní soud v Rychnově nad Kněžnou",
    "OSRO": "Okresní soud v Rokycanech", "OSSM": "Okresní soud v Semilech",
    "OSSO": "Okresní soud v Sokolově", "OSST": "Okresní soud ve Strakonicích",
    "OSSU": "Okresní soud v Šumperku", "OSSY": "Okresní soud ve Svitavách",
    "OSTA": "Okresní soud v Táboře", "OSTC": "Okresní soud v Tachově",
    "OSTP": "Okresní soud v Teplicích", "OSTR": "Okresní soud v Třebíči",
    "OSTU": "Okresní soud v Trutnově", "OSUH": "Okresní soud v Uherském Hradišti",
    "OSUL": "Okresní soud v Ústí nad Labem", "OSUO": "Okresní soud v Ústí nad Orlicí",
    "OSVS": "Okresní soud ve Vsetíně", "OSVY": "Okresní soud ve Vyškově",
    "OSZL": "Okresní soud ve Zlíně", "OSZN": "Okresní soud ve Znojmě",
    "OSZR": "Okresní soud ve Žďáru nad Sázavou", "US": "Ústavní soud",
    "VSOL": "Vrchní soud v Olomouci", "VSPH": "Vrchní soud v Praze", "NONE": "nezadán",
    "OSVSVM": "Okresní soud ve Vsetíně pobočka Valašské Meziřičí",
    "OSBUKR": "Okresní soud v Bruntále - pobočka Krnov",
    "KSULLI": "Krajský soud v Ústí nad Labem pobočka Liberec",
    "KSOSOL": "Krajský soud v Ostravě pobočka Olomouc",
    "KSHKPA": "Krajský soud v Hradci Králové pobočka Pardubice",
    "OSKIHA": "Okresní soud v Karviné pobočka Havířov",
    "KSCBTA": "Krajský soud v Českých Budějovicích pobočka v Táboře",
}

_TYPES = {"rozsudek": "JUDGEMENT", "usneseni": "ORDER_T", "rozhodnuti": "RESOLUTION"}
_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)
_STATUS = {"AKTUALNE_PLATNY": "in force", "ZRUSENY": "repealed",
           "VYHLASENY_BEZ_UCINNOSTI": "published, not yet in force",
           "PLATNY_BEZ_UCINNOSTI": "valid, not yet in force"}
# structural fragment types -> markdown heading level
_STRUCT = {"Cast": 2, "Hlava": 2, "Dil": 3, "Oddil": 3, "Pododdil": 3}


def _clean(html: str) -> str:
    return re.sub(r"\s+", " ", _md(html or "", strip=["a", "img"], heading_style="ATX")).strip()


async def _json(method: str, url: str, what: str, **kw):
    # rozhodnuti.justice.cz now and then stalls a search that normally takes 5 s (one word) to
    # 19 s (two words) until its gateway answers 504 at ~60 s or our 60 s read timeout fires
    # (seen 2026-11-10) while the same query otherwise answers. So: one retry on a network error or
    # 502/503/504 (all calls here are reads, searches included). Worst case ~2 min.
    for attempt in (1, 2):
        try:
            r = await (_http.post if method == "POST" else _http.get)(url, **kw)
        except Exception as e:  # network error
            if attempt == 2:
                raise SourceError(f"{what}: {type(e).__name__} {e}".rstrip(), "network") from e
            continue
        if r.status_code not in (502, 503, 504):
            break
    if r.status_code == 404:
        raise NotFound(f"{what}: not found")
    if r.status_code != 200:
        raise SourceError(f"{what} failed", r.status_code)
    try:
        return r.json()
    except ValueError as e:
        raise SourceError(f"{what}: unexpected non-JSON reply", r.status_code) from e


# --------------------------------------------------------------------------- #
# Case law
# --------------------------------------------------------------------------- #
def _case_number(cn: dict) -> str:
    if not cn:
        return ""
    return f"{cn.get('senate', '')} {cn.get('registry', '')} {cn.get('index', '')}/{cn.get('year', '')}".strip()


def _court(code: str) -> str:
    return _COURTS.get(code or "", code or "")


def _hit(item: dict) -> DecisionHit:
    m = item.get("metadata") or {}
    court, cn = _court(m.get("courtCode", "")), _case_number(m.get("caseNumber") or {})
    title = f"{court}, {cn}" + (f" – {m['caseSubject'].strip(' ,')}" if m.get("caseSubject") else "")
    snippet = re.sub(r"\s+", " ", item.get("verdictText") or "").strip()
    return DecisionHit(id=m.get("ecli") or item["uuid"], title=title, court=court,
                       date=m.get("decisionAt") or "", case_number=cn,
                       snippet=snippet[:300], url=f"{RJ}/rozhodnuti/?id={item['uuid']}")


def _paras(blocks) -> str:
    out = []
    for b in blocks or []:
        t = "".join(f"[{x.get('text', '').strip()}]" if x.get("anonStyle") == "ANON"
                    else x.get("text", "") for x in b.get("texts") or [])
        t = re.sub(r"[ \t]+", " ", t).strip()
        if t:
            out.append(t)
    return "\n\n".join(out)


def _date(v: str, name: str) -> str:
    if not _ISO.match(str(v)):
        raise BadRequest(f"{name} must be YYYY-MM-DD, got {v!r}")
    return str(v)


# --------------------------------------------------------------------------- #
# Legislation
# --------------------------------------------------------------------------- #
def _parse_law_id(id: str) -> str:
    """'89/2012 Sb.' | '89/2012' | 'sb/2012/89' | '/sb/2012/89/2026-01-01' -> '/sb/2012/89'."""
    s = re.sub(r"\s+", " ", id or "").strip()
    m = re.match(r"^(?:č\.\s*)?(\d+)\s*/\s*(\d{4})(\s*Sb\.?(\s*m\.\s*s\.?)?)?$", s, re.I)
    if m:
        return f"/{'sm' if m.group(4) else 'sb'}/{m.group(2)}/{m.group(1)}"
    m = re.match(r"^/?(sb|sm)/(\d{4})/(\d+)(?:/[\d-]+)?$", s, re.I)
    if m:
        return f"/{m.group(1).lower()}/{m.group(2)}/{m.group(3)}"
    raise BadRequest(f"Unrecognised Czech law id {id!r}. Use the collection citation, "
                     "e.g. '89/2012 Sb.' (also '89/2012' or 'sb/2012/89').")


def _norm_provision(p: str) -> str:
    """'§ 2' | '2' | 'par. 2' | '§2a' -> '§ 2a'."""
    s = re.sub(r"^(§+|par\.?|paragraf)\s*", "", (p or "").strip(), flags=re.I).strip()
    if not re.match(r"^\d+[a-z]?$", s, re.I):
        raise BadRequest(f"Unrecognised provision {p!r}; use e.g. '§ 2'.")
    return f"§ {s.lower()}"


def _label(frag: dict) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", frag.get("xhtml") or "")).strip()


class _Law:
    """Metadata + lazily fetched fragment pages of one consolidated version."""

    def __init__(self, meta: dict):
        self.meta = meta
        self.stale = meta["staleUrl"]
        self.pages: list[list[dict]] = []
        self.npages: int | None = None

    @property
    def id(self) -> str:
        return self.meta.get("kodDokumentuSbirky") or self.stale

    @property
    def title(self) -> str:
        return self.meta.get("uplnaCitace") or self.meta.get("nazev") or self.id

    @property
    def url(self) -> str:
        return ESBIRKA + (self.meta.get("eli") or self.stale)

    @property
    def as_of(self) -> str:
        return (self.meta.get("datumUcinnostiZneniOd") or "")[:10]

    async def page(self, n: int) -> list[dict] | None:
        while len(self.pages) <= n:
            if self.npages is not None and len(self.pages) >= self.npages:
                return None
            d = await _json("GET", f"{SBR}/dokumenty-sbirky/{quote(self.stale, safe='')}"
                            f"/fragmenty?cisloStranky={len(self.pages)}", "e-Sbírka text")
            self.npages = int(d.get("pocetStranek") or 0)
            self.pages.append(d.get("seznam") or [])
        return self.pages[n]

    async def fragments(self):
        n = 0
        while (p := await self.page(n)) is not None:
            for f in p:
                yield f
            n += 1


_laws: dict[str, _Law] = {}   # staleUrl (undated) -> current version, small in-process cache


async def _law(id: str) -> _Law:
    key = _parse_law_id(id)
    if key not in _laws:
        url = f"{SBR}/dokumenty-sbirky/{quote(key, safe='')}"
        try:
            r = await _http.get(url)
        except Exception as e:
            raise SourceError(f"e-Sbírka: {e}", "network") from e
        if r.status_code in (400, 404):
            raise NotFound(f"No law {id!r} in e-Sbírka")
        if r.status_code != 200:
            raise SourceError("e-Sbírka metadata failed", r.status_code)
        if len(_laws) >= 4:
            _laws.pop(next(iter(_laws)))
        _laws[key] = _Law(r.json())
    return _laws[key]


def _render(frags: list[dict]) -> str:
    out: list[str] = []
    pending_heading = False
    for f in frags:
        kind, x = f.get("kodTypuFragmentu", ""), f.get("xhtml") or ""
        if kind.startswith("Virtual") or not x.strip():
            continue
        t = _clean(x)
        if kind in _STRUCT:
            out.append(f"{'#' * _STRUCT[kind]} {t}")
            pending_heading = True
            continue
        if kind == "Nadpis_pod" and pending_heading:
            out[-1] += f" – {t}"
        elif kind == "Paragraf":
            out.append(f"#### {t}")
        elif kind.startswith("Nadpis"):
            out.append(f"**{t}**")
        else:
            out.append(t)
        pending_heading = False
    return "\n\n".join(out)


# --------------------------------------------------------------------------- #
# Supreme Court: Sbírka soudních rozhodnutí a stanovisek (sbirka.nsoud.cz)
# Supreme Administrative Court: Vyhledávač NSS (vyhledavac.nssoud.cz)
# --------------------------------------------------------------------------- #
_SB_SEARCH = f"{SBIRKA}/rozsirene-vyhledavani-ve-sbirce/"
_SB_PARTS = {"T": "criminal", "O": "civil, commercial and administrative", "S": "opinions (stanoviska)"}
_SB_ID = re.compile(r"^\s*sbirka:(\d+)\s*$", re.I)
_NSS_ID = re.compile(r"^\s*(?:nssoud|NSS):(\d+)\s*$", re.I)
_NSS_PAGE = 40                      # rows per result page (fixed by the site)
_RJ_PAGE = 100                      # rozhodnuti.justice.cz max page size; always asked for, so
                                    # same-day ties (unstable with a query) keep one order per page


def _txt(el) -> str:
    return re.sub(r"\s+", " ", el.text_content()).strip() if el is not None else ""


async def _page(method: str, url: str, what: str, **kw) -> str:
    try:
        r = await (_http.post if method == "POST" else _http.get)(url, **kw)
    except Exception as e:  # network error
        raise SourceError(f"{what}: {e}", "network") from e
    if r.status_code == 404:
        raise NotFound(f"{what}: not found")
    if r.status_code != 200:
        raise SourceError(f"{what} failed", r.status_code)
    return r.text


def _ecli_case(ecli: str) -> tuple[str, str, str]:
    """'ECLI:CZ:NS:2025:25.CDO.2340.2024.1' -> ('NS', '25 CDO 2340/2024', 'suffix')."""
    m = re.fullmatch(r"ECLI:CZ:(NSS?):\d{4}:(\d+)\.([A-Z]+)\.(\d+)\.(\d{4})\.(\d+)", ecli.strip(), re.I)
    if not m:
        raise BadRequest(f"Cannot read a case number from {ecli!r}")
    return m[1].upper(), f"{m[2]} {m[3]} {m[4]}/{m[5]}", m[6]


async def _sbirka_search(query: str, limit: int, page: int, filters: dict) -> Results:
    per = 10 if limit <= 10 else 30
    params = {"inContent": query or "", "postPerPage": per,
              "orderBy": "relevance" if query else "date", "order": "DESC"}
    if p := filters.get("part"):
        if str(p).upper() not in _SB_PARTS:
            raise BadRequest(f"part must be one of {', '.join(_SB_PARTS)}")
        params["kind"] = str(p).upper()
    if v := filters.get("date_from"):
        params["dateFrom"] = _date(v, "date_from")
    if v := filters.get("date_to"):
        params["dateTo"] = _date(v, "date_to")
    if v := filters.get("case_number"):
        params["fileNumber"] = str(v)
    start = (max(1, page) - 1) * limit
    first = start // per + 1
    hits, last = [], 1
    for sp in (first, first + 1):
        if sp > first and (sp > last or len(hits) >= start - (first - 1) * per + limit):
            break
        url = _SB_SEARCH + (f"strana/{sp}/" if sp > 1 else "")
        try:
            html = await _page("GET", url, "Sbírka NS search", params=params)
        except NotFound:
            break
        doc = lxml.html.fromstring(html)
        nums = [int(a.text_content()) for a in doc.xpath('//ul[contains(@class,"pagination")]//a')
                if a.text_content().strip().isdigit()]
        last = max(nums + [sp])
        for art in doc.xpath('//article[@class="listing-item"]'):
            a = art.find(".//h2/a")
            m = re.search(r"/sbirka/(\d+)/", a.get("href", "")) if a is not None else None
            if not m:
                continue
            ps = art.findall(".//p")
            info = " | ".join(_txt(s) for s in ps[0].findall("span")) if ps else ""
            date = re.search(r"Datum: (\d{2}\.\d{2}\.\d{4})", info)
            cn = re.search(r"Sp\. zn\.: ([^|]+)", info)
            court = info.rsplit("|", 1)[-1].strip() if "|" in info else ""
            hits.append(DecisionHit(
                id=f"sbirka:{m[1]}", title=_txt(a), court=court or "Nejvyšší soud",
                date=_http.iso_date(date[1]) if date else "",
                case_number=cn[1].strip() if cn else "",
                snippet=_txt(ps[1])[:300] if len(ps) > 1 else "", url=a.get("href")))
    off = start - (first - 1) * per
    exact = last == 1 or (first >= last and not hits[off + limit:])
    return Results(items=hits[off:off + limit],
                   total=len(hits) if last == 1 else None,
                   note=("Sbírka soudních rozhodnutí a stanovisek (the Supreme Court's official "
                         "collection, 1919-; it also holds some lower-court decisions it "
                         f"selected). {'' if exact else 'The site gives no total, only page numbers; '}"
                         "sorted by relevance with a query, else newest first. NS decisions "
                         "outside the Sbírka are not reachable (rozhodnuti.nsoud.cz robots.txt "
                         "disallows all crawlers)."))


async def _sbirka_decision(post_id: str) -> Decision:
    url = f"{SBIRKA}/sbirka/{post_id}/"
    doc = lxml.html.fromstring(await _page("GET", url, f"Sbírka NS {post_id}"))
    title = _txt(doc.find(".//h1"))
    table = doc.xpath('//table[contains(@class,"content-table")]')
    if not title or not table:
        raise SourceError(f"Sbírka NS {post_id}: page layout not recognised", 200)
    meta, text = {}, ""
    for tr in table[0].xpath("./tr|./tbody/tr"):
        tds = tr.findall("td")
        if len(tds) < 2:
            continue
        k = _txt(tds[0]).split(":", 1)[0].strip()
        if not k:
            text = _http.html_to_md(lxml.html.tostring(tds[1], encoding=str))
            text = re.sub(r"^\W*Sbírkový text rozhodnutí\W*", "", text)
        else:
            meta[k] = _txt(tds[1])
    if not text:
        raise NotFound(f"Sbírka NS {post_id}: no decision text on the page")
    ecli = re.search(r"ECLI:CZ:[A-Z]+:\d{4}:[\w.]+", title)
    head = [f"**Právní věta:** {meta['Právní věta']}"] if meta.get("Právní věta") else []
    sb = f"{meta.get('Číslo rozhodnutí', '')}/{meta.get('Rok', '')}".strip("/")
    return Decision(
        id=f"sbirka:{post_id}", title=title, text="\n\n".join(head + [text]), url=url,
        court=meta.get("Soud", "Nejvyšší soud"),
        date=_http.iso_date(meta.get("Datum rozhodnutí", "")),
        case_number=meta.get("Spisová značka", ""),
        metadata={k: v for k, v in {
            "ECLI": ecli[0] if ecli else "", "Sbírka": f"č. {sb}, sešit {meta.get('Sešit', '')}",
            "Type": meta.get("Typ rozhodnutí", ""), "Part": meta.get("Druh", ""),
            "Keywords": meta.get("Heslo", ""), "Provisions": meta.get("Předpisy", "")}.items() if v})


_NSS_FORM: dict = {}


async def _nss_form() -> dict:
    """Blank search form of vyhledavac.nssoud.cz: field list + NSS court-tree ids."""
    if _NSS_FORM:
        return _NSS_FORM
    doc = lxml.html.fromstring(await _page("GET", f"{NSSV}/", "Vyhledávač NSS form"))
    form = doc.find(".//form")
    if form is None:
        raise SourceError("Vyhledávač NSS: search form not found", 200)
    data, fields = [], {}
    for i in form.xpath(".//input|.//select|.//textarea"):
        n = i.get("name")
        if not n or (i.get("type") in ("radio", "checkbox") and i.get("checked") is None):
            continue
        data.append((n, i.get("value") or ""))
        if n.endswith(".TechnickyNazev") and "vyhledavaciPodminkaHodnota" in n:
            fields.setdefault(i.get("value"), n.rsplit(".", 1)[0])
    tree = next((v for n, v in data if n == fields.get("soudsenat", "") + ".ciselnikTreeData"), "")
    i = tree.find('title:"Nejvyšší správní soud"')
    sub = tree[i:]
    depth, end = 0, len(sub)
    for k, ch in enumerate(sub):    # cut the NSS node's subtree out of the JS literal
        depth += ch == "["
        depth -= ch == "]"
        if depth < 0 or (depth == 0 and ch == "}"):
            end = k
            break
    ids = re.findall(r"id:(\d+)", sub[:end]) if i >= 0 else []
    if not ids or not {"textDokumentu", "oznacenivecivcelku", "soudsenat"} <= fields.keys():
        raise SourceError("Vyhledávač NSS: search form layout not recognised", 200)
    _NSS_FORM.update(data=data, fields=fields, nss=",".join(ids))
    return _NSS_FORM


def _nss_rows(doc) -> list[DecisionHit]:
    hits = []
    for tr in doc.xpath('//tr[.//a[contains(@href,"/DokumentOriginal/Html/")]]'):
        tds = [_txt(td) for td in tr.findall("td")]
        a = tr.xpath('.//a[contains(@href,"/DokumentOriginal/Html/")]')[0]
        m = re.search(r"/Html/(\d+)", a.get("href", ""))
        if not m or len(tds) < 8:
            continue
        cj = re.sub(r"\s*-\s*", "-", tds[3])
        court = "Nejvyšší správní soud" if "NSS" in tds[4] or not tds[4] else tds[4]
        hits.append(DecisionHit(
            id=f"nssoud:{m[1]}", title=f"{court}, {cj}", court=court,
            date=_http.iso_date(tds[2]), case_number=cj,
            snippet=" | ".join(x for x in (tds[5], tds[6], tds[4], tds[8] if len(tds) > 8 else "") if x)[:300],
            url=f"{NSSV}/DokumentDetail/Index/{m[1]}"))
    return hits


async def _nss_search(query: str, limit: int, page: int, filters: dict,
                      regional: bool = False) -> Results:
    if filters.get("part"):
        raise BadRequest("courts 'NSS'/'SPRAVNI' take only 'case_number', 'date_from' and "
                         "'date_to' besides the query ('part' is for court 'NS')")
    form = await _nss_form()
    f = form["fields"]
    put = {f["textDokumentu"] + ".HodnotaText": query or "",
           f["oznacenivecivcelku"] + ".HodnotaText": str(filters.get("case_number") or "")}
    for key, suffix in (("date_from", "Od"), ("date_to", "Do")):
        if v := filters.get(key):
            y, mo, d = (int(x) for x in _date(v, key)[:10].split("-"))
            put[f"{f['datumvydanirozhodnuti']}.HodnotaDatumACas{suffix}"] = f"{d}. {mo}. {y}"
    data = [(n, put.get(n, v)) for n, v in form["data"]]
    if not regional:
        data.append((f["soudsenat"] + ".HodnotaCiselnikPolozkySelected", form["nss"]))
    hdr = {"Content-Type": "application/x-www-form-urlencoded"}
    html = await _page("POST", f"{NSSV}/Home/Index?formular=1&zobrazeniVysledkuVolba=2",
                       "Vyhledávač NSS search", content=urlencode(data), headers=hdr)
    m = re.search(r"Počet nalezených záznamů:\s*(\d+)", html)
    total = int(m[1]) if m else 0
    start = (max(1, page) - 1) * limit
    hits = _nss_rows(lxml.html.fromstring(html)) if total else []
    first = start // _NSS_PAGE
    off = start - first * _NSS_PAGE
    if first:
        hits = []
    k = first or 1                  # the form response already holds source page 0
    if total and len(hits) < off + limit and k * _NSS_PAGE < total:
        params = re.search(r"var currParams = '(.*?)';", html)
        sort = re.search(r"var currSort = '(.*?)';", html)
        if not params or not sort:
            raise SourceError("Vyhledávač NSS: paging parameters not found", 200)
        while len(hits) < off + limit and k * _NSS_PAGE < total:
            body = urlencode({"vyhledavaciPodminky": params[1].encode().decode("unicode_escape"),
                              "zobrazeniVysledkuId": "2", "pageNum": k, "resultOrder": sort[1]})
            more = await _page("POST", f"{NSSV}/Home/MyResTRowsCont", "Vyhledávač NSS page",
                               content=body, headers=hdr)
            if len(more.strip()) <= 5:
                break
            hits += _nss_rows(lxml.html.fromstring(f"<table>{more}</table>"))
            k += 1
    return Results(items=hits[off:off + limit], total=total,
                   note="Vyhledávač NSS full-text search (stemmed), newest first; "
                        + ("NSS plus regional courts' administrative sections (as far as "
                           "they were sent to the NSS database)." if regional else
                           "Supreme Administrative Court decisions only."))


async def _nss_decision(doc_id: str) -> Decision:
    url = f"{NSSV}/DokumentDetail/Index/{doc_id}"
    det = lxml.html.fromstring(await _page("GET", url, f"Vyhledávač NSS {doc_id}"))
    meta: dict[str, str] = {}
    for d in det.xpath("//div[@data-field-id]"):
        v = d.xpath('.//span[contains(@class,"det-textval")]')
        meta.setdefault(d.get("data-field-id"), _txt(v[0]) if v else "")
    if not meta:
        raise NotFound(f"Vyhledávač NSS: no document {doc_id}")
    try:
        raw = await _http.get(f"{NSSV}/DokumentOriginal/Html/{doc_id}")
        text = _http.html_to_md(raw.content.decode("utf-8", "replace")) if raw.status_code == 200 else ""
    except Exception as e:  # network error
        raise SourceError(f"Vyhledávač NSS {doc_id} text: {e}", "network") from e
    if not text:
        raise NotFound(f"Vyhledávač NSS {doc_id}: no text published for this document")
    cj = re.sub(r"\s*-\s*", "-", meta.get("cj") or meta.get("oznacenivecivcelku", ""))
    senate = meta.get("soudsenat", "")
    court = "Nejvyšší správní soud" if "NSS" in senate or not senate else senate
    return Decision(
        id=f"nssoud:{doc_id}", title=f"{court}, {cj}", text=text, url=url, court=court,
        date=_http.iso_date(meta.get("datumvydanirozhodnuti", "")), case_number=cj,
        metadata={k: v for k, v in {
            "ECLI": meta.get("ecli", ""), "Senate": senate, "Judge rapporteur": meta.get("soudcezpravodaj", ""),
            "Type": meta.get("druhdokumentuavyrokrozhodnuti", ""), "Outcome": meta.get("vyrokrozhodnuti", ""),
            "Area": meta.get("oblastupravy", ""), "Published in Sb. NSS": meta.get("sbnsspublikovano", "")}.items() if v})


async def _by_ecli(ecli: str) -> Decision:
    court, cn, suffix = _ecli_case(ecli)
    if court == "NS":
        res = await _sbirka_search("", 30, 1, {"case_number": cn})
        for h in res.items:
            d = await _sbirka_decision(h.id.split(":", 1)[1])
            if d.metadata.get("ECLI", "").upper() == ecli.upper():
                return d
        raise NotFound(f"{ecli} is not in the Sbírka soudních rozhodnutí a stanovisek. Other "
                       "Supreme Court decisions are only on rozhodnuti.nsoud.cz, whose "
                       "robots.txt disallows all crawlers, so Fontes cannot fetch them")
    res = await _nss_search("", 40, 1, {"case_number": f"{cn}-{suffix}"})
    for h in res.items:
        if h.case_number.replace(" ", "").upper() == f"{cn}-{suffix}".replace(" ", "").upper():
            return await _nss_decision(h.id.split(":", 1)[1])
    raise NotFound(f"No Supreme Administrative Court document {ecli} on vyhledavac.nssoud.cz")


class Czechia(Jurisdiction):
    code = "cz"
    name = "Czechia"
    languages = ("cs",)
    aliases = ("cze", "czechia", "czech republic")
    sources = (
        Source(
            name="rozhodnuti.justice.cz (Ministry of Justice)",
            url=RJ,
            covers=("caselaw",),
            licence="unknown: published as open data by the Ministry of Justice "
                    "(rozhodnuti.justice.cz/opendata), no licence stated; not in the NKOD catalogue",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown, none documented; no 429 in ~30 requests (2026-11); using 1 s spacing",
            terms_url=f"{RJ}/opendata/",
        ),
        Source(
            name="e-Sbírka (Ministry of the Interior)",
            url=ESBIRKA,
            covers=("legislation",),
            licence="NKOD terms for the e-Sbírka open data: no copyrighted works, no database "
                    "rights, no personal data (CC0-equivalent); legal texts are exempt under "
                    "§ 3 of the Czech Copyright Act. The /sbr-cache REST API itself is undocumented",
            commercial_use=True,
            ai_use=None,
            auth="none",
            rate_limit="unknown, none documented; no 429 in ~40 requests (2026-11); using 1 s spacing",
            terms_url="https://data.gov.cz/datové-sady?klíčová-slova=e-Sbírka",
        ),
        Source(
            name="Sbírka soudních rozhodnutí a stanovisek (Nejvyšší soud), sbirka.nsoud.cz",
            url=SBIRKA,
            covers=("caselaw",),
            licence="no terms page; court decisions are official works exempt from copyright "
                    "(§ 3 Czech Copyright Act 121/2000)",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="none documented; robots.txt 'User-agent: * Disallow:' (allows all); "
                       "no 429 in ~15 requests (2026-11-10); using 1 s spacing",
            terms_url=f"{SBIRKA}/o-sbirce/",
        ),
        Source(
            name="Vyhledávač NSS (Nejvyšší správní soud), vyhledavac.nssoud.cz",
            url=NSSV,
            covers=("caselaw",),
            licence="no terms page; court decisions are official works exempt from copyright "
                    "(§ 3 Czech Copyright Act 121/2000)",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="none documented; robots.txt 404 (www.nssoud.cz robots asks Crawl-Delay "
                       "10, not binding here); using 2 s spacing",
            terms_url=f"{NSSV}/Napoveda",
        ),
    )
    caselaw_filters = {
        "court": "court code, e.g. 'MSPH' (Městský soud v Praze), 'VSPH', 'KSBR', 'OSTP'; "
                 "'NS' = Supreme Court (Sbírka), 'NSS' = Supreme Administrative Court, "
                 "'SPRAVNI' = NSS plus regional administrative-justice decisions",
        "part": "court 'NS' only: Sbírka part 'T' (criminal), 'O' (civil/commercial/"
                "administrative) or 'S' (opinions)",
        "case_number": "court 'NS'/'NSS'/'SPRAVNI' only: spisová značka, e.g. '25 Cdo 2340/2024'",
        "type": "decision type: 'rozsudek' (judgment), 'usneseni' (order), 'rozhodnuti'",
        "date_from": "decided on or after, YYYY-MM-DD",
        "date_to": "decided on or before, YYYY-MM-DD",
    }
    min_interval = {"rozhodnuti.justice.cz": 1.0, "e-sbirka.gov.cz": 1.0,
                    "sbirka.nsoud.cz": 1.0, "vyhledavac.nssoud.cz": 2.0}
    notes = ("Case law: by default district, regional and high courts (rozhodnuti.justice.cz, "
             "since 2020, anonymised). court='NS' searches the Supreme Court's official "
             "Sbírka (1919-, ids 'sbirka:25671'); court='NSS' searches the Supreme "
             "Administrative Court (ids 'nssoud:786898', the Vyhledávač NSS document id; "
             "court='SPRAVNI' adds regional administrative decisions). ECLI:CZ:NS: and "
             "ECLI:CZ:NSS: ids resolve through those sources. "
             "Laws: cite as '89/2012 Sb.', provisions as '§ 2'.")
    gaps = (
        "Supreme Administrative Court (NSS): regional administrative decisions there (court 'SPRAVNI') are whatever the NSS database "
        "holds, completeness unverified",
        "Constitutional Court (ÚS): nalus.usoud.cz works (HTML search) but not built yet",
        "Supreme Court (NS): only decisions published in the Sbírka are reachable; the full "
        "decision database rozhodnuti.nsoud.cz has robots.txt 'User-agent: * Disallow: /' "
        "(only DG_JUSTICE_CRAWLER allowed), so it is not used",
        "Lower-court decisions before 2020: rozhodnuti.justice.cz starts in 2020; older sources not researched yet",
        "Regional and municipal regulations: not researched yet",
    )
    samples = {
        "caselaw_query": "nájem bytu",
        "decision_id": "ECLI:CZ:OSTP:2025:17.C.197.2025.1",
        "legislation_query": "občanský zákoník",
        "law_id": "89/2012 Sb.",
        "provision": "§ 2",
    }

    # ----------------------------------------------------------------- caselaw
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        top = str(filters.get("court") or "").upper()
        if top == "NS":
            return await _sbirka_search(query or "", limit, page, filters)
        if top in ("NSS", "SPRAVNI"):
            return await _nss_search(query or "", limit, page, filters, regional=top == "SPRAVNI")
        if filters.get("part") or filters.get("case_number"):
            raise BadRequest("filters 'part' and 'case_number' need court 'NS', 'NSS' or 'SPRAVNI'")
        if limit > _RJ_PAGE:
            raise BadRequest(f"limit can be at most {_RJ_PAGE} for this source")
        params: list[tuple[str, str | int]] = [
            ("limit", _RJ_PAGE), ("searchMode", "ALL"),
            ("sortBy", "PUBLISHED_AT"), ("sortDirection", "DESC")]
        params += [("searchText", w) for w in (query or "").split()]
        if c := filters.get("court"):
            c = str(c).upper()
            if c not in _COURTS:
                raise BadRequest(f"Unknown court code {c!r}. Examples: MSPH, VSPH, VSOL, KSBR, OSTP.")
            params.append(("courtCodes", c))
        if t := filters.get("type"):
            if str(t).lower() not in _TYPES:
                raise BadRequest(f"type must be one of {', '.join(_TYPES)}")
            params.append(("type", _TYPES[str(t).lower()]))
        if v := filters.get("date_from"):
            params.append(("issuedFrom", _date(v, "date_from")))
        if v := filters.get("date_to"):
            params.append(("issuedTo", _date(v, "date_to")))
        start = (max(1, page) - 1) * limit
        rows, d = [], {}
        for k in range(start // _RJ_PAGE, (start + limit - 1) // _RJ_PAGE + 1):
            d = await _json("GET", f"{RJ}/api/finaldoc", "rozhodnuti.justice.cz search",
                            params=params + [("page", k)])
            rows += d.get("items") or []
            if len(d.get("items") or []) < _RJ_PAGE:
                break
        off = start % _RJ_PAGE
        return Results(items=[_hit(i) for i in rows[off:off + limit]],
                       total=d.get("totalElements"),
                       note="Sorted newest-published first (the source has no relevance ranking); "
                            "lower courts only, since 2020."
                            + (" With a query the source's order of same-day decisions can shift "
                               "between its 100-hit pages, so hits near every 100th may repeat or "
                               "be missed." if (query or "").strip() else ""))

    async def get_decision(self, id):
        s = (id or "").strip()
        if m := _SB_ID.match(s):
            return await _sbirka_decision(m[1])
        if m := _NSS_ID.match(s):
            return await _nss_decision(m[1])
        if re.match(r"ECLI:CZ:NSS?:", s, re.I):
            return await _by_ecli(s)
        if _UUID.match(s):
            uuid = s.lower()
        elif s.upper().startswith("ECLI:CZ:"):
            d = await _json("GET", f"{RJ}/api/finaldoc", "rozhodnuti.justice.cz lookup",
                            params={"ecli": s.upper(), "limit": 1, "page": 0})
            if not d.get("items"):
                raise NotFound(f"No decision {s!r} on rozhodnuti.justice.cz (it covers "
                               "district/regional/high courts since 2020)")
            uuid = d["items"][0]["uuid"]
        else:
            raise BadRequest(f"Use an ECLI (ECLI:CZ:...), a rozhodnuti.justice.cz uuid, "
                             f"'sbirka:<n>' or 'nssoud:<n>', got {id!r}")
        doc = await _json("GET", f"{RJ}/api/finaldoc/{uuid}", "rozhodnuti.justice.cz decision")
        m = doc.get("metadata") or {}
        court, cn = _court(m.get("courtCode", "")), _case_number(m.get("caseNumber") or {})
        parts = [_paras(doc.get("header"))]
        for head, key in (("Výrok", "verdict"), ("Odůvodnění", "justification"),
                          ("Poučení", "information")):
            if body := _paras(doc.get(key)):
                parts.append(f"## {head}\n\n{body}")
        solver = m.get("solver") or {}
        judge = " ".join(x for x in (solver.get("titlesBefore"), solver.get("firstName"),
                                     solver.get("lastName")) if x)
        meta = {"Type": m.get("type") or "", "Published": m.get("publishedAt") or "",
                "Judge": judge, "Subject": m.get("caseSubject") or ""}
        return Decision(id=m.get("ecli") or uuid, title=f"{court}, {cn}", text="\n\n".join(p for p in parts if p),
                        url=f"{RJ}/rozhodnuti/?id={uuid}", court=court, date=m.get("decisionAt") or "",
                        case_number=cn, metadata={k: v for k, v in meta.items() if v})

    # ------------------------------------------------------------- legislation
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        # Relevance ties come back in a different order per page size and no secondary sort key
        # is accepted, so always ask for the same page size and slice by offset.
        start = (max(1, page) - 1) * limit
        rows, total = [], None
        for sp in range(start // _SBR_PAGE, (start + limit - 1) // _SBR_PAGE + 1):
            body = {"fulltext": query, "start": sp, "pocet": _SBR_PAGE,   # 'start' is a page number, not an offset
                    "razeni": ["+relevance"]}
            d = await _json("POST", f"{SBR}/jednoducha-vyhledavani", "e-Sbírka search", json=body)
            rows += d.get("seznam") or []
            total = d.get("pocetCelkem")
            if len(d.get("seznam") or []) < _SBR_PAGE:
                break
        off = start % _SBR_PAGE
        items = []
        for x in rows[off:off + limit]:
            kod = x.get("kodDokumentuSbirky") or ""
            m = re.match(r"^(\d+/\d{4})", kod)
            items.append(LawHit(id=kod or x["staleUrl"], title=x.get("nazev") or kod,
                                number=m.group(1) if m else "", date=x.get("datum") or "",
                                status=_STATUS.get(x.get("stavDokumentuSbirky", ""),
                                                   x.get("stavDokumentuSbirky", "")),
                                url=ESBIRKA + x["staleUrl"]))
        return Results(items=items, total=total)

    async def get_legislation_toc(self, id):
        law = await _law(id)
        entries: list[TocEntry] = []
        heading = ""
        async for f in law.fragments():
            kind = f.get("kodTypuFragmentu", "")
            level = max(0, int(f.get("hloubka") or 2) - 2)
            if kind in _STRUCT:
                entries.append(TocEntry(title=_label(f), level=level))
            elif kind == "Nadpis_pod" and entries and not entries[-1].provision:
                entries[-1].title += f" – {_label(f)}"
            elif kind == "Nadpis_nad":
                heading = _label(f)
            elif kind == "Paragraf":
                lab = _label(f)
                entries.append(TocEntry(title=f"{lab} – {heading}" if heading else lab,
                                        level=level, provision=lab))
                heading = ""
        return Toc(id=law.id, title=law.title, url=law.url, entries=entries)

    async def get_legislation_provision(self, id, provision):
        want = _norm_provision(provision)
        law = await _law(id)
        frags: list[dict] = []
        depth = None
        prev_heading = None
        async for f in law.fragments():
            kind = f.get("kodTypuFragmentu", "")
            if depth is None:
                if kind == "Paragraf" and _label(f).lower() == want:
                    depth = f.get("hloubka")
                    frags = ([prev_heading] if prev_heading else []) + [f]
                prev_heading = f if kind == "Nadpis_nad" else None
            elif (f.get("hloubka") or 0) > depth:
                frags.append(f)
            else:
                break
        if not frags:
            raise NotFound(f"{want} not found in {law.id}")
        par = next(f for f in frags if f.get("kodTypuFragmentu") == "Paragraf")
        return Provision(law_id=law.id, law_title=law.title, provision=want, text=_render(frags),
                         url=ESBIRKA + (par.get("staleUrl") or law.stale), as_of=law.as_of)

    async def get_legislation_text(self, id):
        law = await _law(id)
        frags = [f async for f in law.fragments()]
        meta = {"Version": law.meta.get("typZneni") or "",
                "Published": (law.meta.get("datumCasVyhlaseni") or "")[:10],
                "In force from": (law.meta.get("datumUcinnostiOd") or "")[:10]}
        return LawText(id=law.id, title=law.title, text=_render(frags), url=law.url,
                       as_of=law.as_of, metadata={k: v for k, v in meta.items() if v})
