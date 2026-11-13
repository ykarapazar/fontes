"""Cabo Verde (Cape Verde): judgments of the Supremo Tribunal de Justiça and the two Relação
courts (JURIS CV), decisions of the Tribunal Constitucional, the stj.cv selection, plus the core
laws the Tribunal Constitucional hosts. All in Portuguese.

JURIS CV (jurisprudencia.cv, CSMJ; built on Portugal's CSM platform, "Versão Beta"):
  * GET /items/loadItems is the site's own dynatable JSON feed: page, perPage, offset,
    queries[freesearch], queries[courts][]=1|2|3 (STJ, TRB, TRS; a plain queries[courts] is
    ignored), queries[initial_date]/[end_date] as DD/MM/YYYY, sorts[dataAcordao]=-1. It returns
    records (tribunal, ecli, dataAcordao, sumario) and queryRecordCount. /stats (2026-11-10):
    1,296 decisions, STJ 774, TRB 228, TRS 294.
  * Id: the site's ECLI-style code 'JURIS:CV:STJ:2026:1299'; /juris/<id>/ is the HTML page with
    labelled <h4> metadata and tabs #summary, #parcial-text, #integral-text ("Não disponível."
    when empty). No login needed. robots.txt Crawl-delay 10, so 10 s spacing.

Tribunal Constitucional (www.tribunalconstitucional.cv, WordPress + "WP File Download"):
  * Decisions are PDFs (text layer) in file categories: "Acórdãos do TC - Atual" (2016-;
    branches Fiscalização Preventiva / Sucessiva / Concreta, Amparo e Habeas Data, Eleitoral,
    Diversos, each split by year), "Decisões do STJ enquanto Tribunal Constitucional - 1995 a
    2015" and "Decisões Sumárias". The category tree is read from the <select> on the
    /index.php/acordaos/ page.
  * Search with a query and no year: the plugin's own search (POST admin-ajax task=search.display,
    the call the site's search box makes). It matches titles and metadata, not the full text,
    returns newest first, and has no paging; we take its 50 newest matches.
    With a `year` filter (or no query): the year's categories are listed in full
    (admin-ajax task=files.display, JSON) and titles are filtered locally.
  * Id: the plugin's file id ("3488"); the file's /index.php/download/<cat>/<slug>/<id>/... URL
    also works. task=file.display gives title, category and size (checked < MAX_PDF).
Supremo Tribunal de Justiça (www.stj.cv, WordPress/Elementor):
  * Each section page (1ª Cível, 2ª Criminal, 3ª Administrativa/Fiscal/Aduaneira) lists selected
    judgments as PDF links whose text is "Acórdão NN-YYYY – keywords". About 360 in 2026-11.
  * Id: the upload path "2025/05/Acordao-05-2024-....pdf" (or the full PDF URL). Only PDFs
    listed on a section page are fetched; a HEAD request checks the size first.
Legislation (Tribunal Constitucional file categories "Legislação Complementar" and "Leis
Constitucionais"): about 30 core texts as PDFs (Código Civil, Código Penal, CPP, CPC, Código do
Processo Administrativo, organic laws of the courts, nationality and aliens laws, the 1980/1992
constitutions and their revisions). They are copies of Boletim Oficial issues or compilations,
not consolidated. Articles are cut on their "Artigo N.º" headings.

Not used: the Boletim Oficial (boe.incv.cv, Imprensa Nacional de Cabo Verde). Its terms say
"6. É proibida a cópia, total ou parcial do site, incluindo qualquer conteúdo ou formato digital
pertencente ao site da INCV, sem a prévia autorização da INCV." (checked 2026-11-06).
"""
from __future__ import annotations

import html as htmllib
import re
import time
import unicodedata
from urllib.parse import quote, unquote

from lxml import html as lxml_html

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc, TocEntry

TC_HOST = "www.tribunalconstitucional.cv"
JURIS_HOST = "jurisprudencia.cv"
JURIS = f"https://{JURIS_HOST}"
JURIS_COURTS = {"stj": ("1", "Supremo Tribunal de Justiça"), "trb": ("2", "Tribunal da Relação de Barlavento"),
                "trs": ("3", "Tribunal da Relação de Sotavento")}
STJ_HOST = "www.stj.cv"
TC = f"https://{TC_HOST}"
STJ = f"https://{STJ_HOST}"
AJAX = f"{TC}/wp-admin/admin-ajax.php?juwpfisadmin=false&action=wpfd&"
TREE_PAGE = f"{TC}/index.php/acordaos/"
STJ_SECTIONS = {
    "civel": ("1ª Secção Cível", f"{STJ}/index.php/1a-sec-civel/"),
    "criminal": ("2ª Secção Criminal", f"{STJ}/index.php/testes/"),
    "administrativo": ("3ª Secção Administrativa, Fiscal e Aduaneira", f"{STJ}/index.php/3a-sec-adm-fisc-ad/"),
}
MAX_PDF = 40_000_000
TTL = 3600.0
SEARCH_CAP = 50                 # the plugin errors on limit=100; 50 is its largest working page

DEC_ROOTS = {"18": "Tribunal Constitucional",
             "82": "Supremo Tribunal de Justiça (como Tribunal Constitucional, 1995-2015)",
             "216": "Tribunal Constitucional (decisão sumária)"}
LAW_ROOTS = ("47", "199")       # Legislação Complementar, Leis Constitucionais
ALL_FILES_CAT = "179"           # "Todos os ficheiros": a flat category holding some 2020 decisions

_TC_ID = re.compile(r"^(?:https?://(?:www\.)?tribunalconstitucional\.cv/index\.php/download/\d+/[^/]+/)?(\d{1,6})"
                    r"(?:/.*)?$", re.I)
_STJ_ID = re.compile(r"^(?:https?://(?:www\.)?stj\.cv/wp-content/uploads/)?(\d{4}/\d{2}/[A-Za-z0-9._-]{1,250}\.pdf)$",
                     re.I)
_CASE_NO = re.compile(r"(?i)\b(ac[oó]rd[aã]o|acard[aã]o|acr[oó]d[aã]o|ac[oó]d[aã]o|parecer|decis[aã]o sum[aá]ria)"
                      r"(?:\s*n\.?\s*[º°o]?)?\s*[–-]?\s*(\d{1,3})\s*[-/]\s*(\d{4})")
_MONTHS = {m: i + 1 for i, m in enumerate(
    ("janeiro", "fevereiro", "marco", "abril", "maio", "junho", "julho", "agosto", "setembro",
     "outubro", "novembro", "dezembro"))}

_cache: dict = {}
_docs: dict = {}


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _fold(s: str) -> str:
    """Lower-case, accents stripped: for matching Portuguese titles."""
    return "".join(c for c in unicodedata.normalize("NFKD", s.lower()) if not unicodedata.combining(c))


def _matches(query: str, title: str) -> bool:
    t = _fold(title)
    return all(w in t for w in _fold(query).split())


def _cached(key):
    hit = _cache.get(key)
    return hit[1] if hit and time.monotonic() - hit[0] < TTL else None


def _store(key, value):
    _http.lru_put(_cache, key, (time.monotonic(), value), 64)
    return value


def _clean_title(t: str) -> str:
    t = _http.clean(htmllib.unescape(t or ""))
    return re.sub(r"^\d{1,3}\s*-\s+", "", t)       # the site's ordering prefix "03 - "


def _case_number(title: str) -> str:
    m = _CASE_NO.search(title)
    if not m:
        return ""
    kind = _fold(m[1])
    label = ("Parecer" if kind.startswith("parecer") else
             "Decisão Sumária" if kind.startswith("decis") else "Acórdão")
    return f"{label} n.º {int(m[2])}/{m[3]}"


def _year_of(title: str) -> str:
    m = _CASE_NO.search(title)
    return m[3] if m else ""


def _pt_date(text: str) -> str:
    """Decision date from the signing line 'Praia, 14 de fevereiro de 2020' (last one wins)."""
    found = re.findall(r"Praia\s*,\s*(?:aos\s+)?(\d{1,2})\s*[º°]?\s*de\s+([A-Za-zçÇ]+)\s+de\s+(\d{4})", text)
    for d, mon, y in reversed(found):
        m = _MONTHS.get(_fold(mon))
        if m and 1 <= int(d) <= 31:
            return f"{y}-{m:02d}-{int(d):02d}"
    return ""


def _pdf_body(raw: str) -> str:
    lines = [ln for ln in raw.split("\n") if not re.fullmatch(r"\d{1,4}", ln.strip())]   # page numbers
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


async def _pdf(url: str, size: int | None, who: str) -> str:
    if size is None:
        h = await _http.request("HEAD", url)
        if h.status_code == 404:
            raise NotFound(f"{who}: no PDF at {url}.")
        if h.status_code != 200:
            raise SourceError(_http.error(who, f"PDF check failed: {url}", h.status_code), h.status_code)
        size = int(h.headers.get("content-length") or 0)
    if size > MAX_PDF:
        raise SourceError(f"Error ({who}): {url} is {size // 1_000_000} MB, over the "
                          f"{MAX_PDF // 1_000_000} MB limit; read it there.", "too-large")
    r = await _http.get(url, headers={"Connection": "close"})
    if r.status_code == 404:
        raise NotFound(f"{who}: no PDF at {url}.")
    if r.status_code != 200 or not r.content.startswith(b"%PDF"):
        raise SourceError(_http.error(who, f"PDF failed: {url}", r.status_code), r.status_code)
    raw = _http.pdf_text(r.content)
    if len(raw) < 200:
        raise SourceError(f"Error ({who}): {url} has no text layer (scanned; no OCR here); read it there.",
                          "no-text")
    return _pdf_body(raw)


# --------------------------------------------------------------------------- #
# Tribunal Constitucional (WP File Download)
# --------------------------------------------------------------------------- #
async def _tree() -> dict[str, dict]:
    """catid -> {root, branch, name, leaf} from the category <select> on the acórdãos page."""
    got = _cached("tree")
    if got is not None:
        return got
    r = await _http.get(TREE_PAGE)
    if r.status_code != 200:
        raise SourceError(_http.error(TC_HOST, "category list failed", r.status_code), r.status_code)
    sel = re.search(r'<select id="filter_catid".*?</select>', r.text, re.S)
    if not sel:
        raise SourceError(f"Error ({TC_HOST}): category list not found on {TREE_PAGE}.", "layout")
    opts = re.findall(r'<option\s+value="(\d+)">\s*(-*)\s*([^<]*)', sel[0])
    tree: dict[str, dict] = {}
    stack: list[str] = []
    for cid, dashes, name in opts:
        lvl = len(dashes)
        stack = stack[:lvl] + [cid]
        tree[cid] = {"name": _http.clean(htmllib.unescape(name)), "path": list(stack), "leaf": True}
        if lvl and stack[lvl - 1] in tree:
            tree[stack[lvl - 1]]["leaf"] = False
    return _store("tree", tree)


def _root(tree, cid: str) -> str:
    return tree[cid]["path"][0] if cid in tree else ""


def _court(tree, cid: str) -> str:
    return DEC_ROOTS.get(_root(tree, cid), "Tribunal Constitucional")


def _branch(tree, cid: str) -> str:
    path = tree.get(cid, {}).get("path", [])
    return tree[path[1]]["name"] if len(path) > 2 and _root(tree, cid) != "216" else ""


def _is_decision(tree, cid: str, title: str) -> bool:
    if _root(tree, cid) in DEC_ROOTS:
        return True
    return cid == ALL_FILES_CAT and bool(_CASE_NO.search(title))


def _tc_url(link: str) -> str:
    base, _, rest = link.partition("/index.php/")
    return f"{base}/index.php/{quote(unquote(rest))}"


async def _tc_json(params: str, who: str):
    r = await _http.get(AJAX + params)
    if r.status_code != 200:
        raise SourceError(_http.error(TC_HOST, who, r.status_code), r.status_code)
    try:
        return r.json()
    except ValueError:
        raise SourceError(f"Error ({TC_HOST}): {who}: unexpected reply (not JSON).", "payload") from None


async def _tc_files(cid: str) -> list[dict]:
    got = _cached(("files", cid))
    if got is not None:
        return got
    data = await _tc_json(f"task=files.display&view=files&id={cid}", f"file list {cid}")
    return _store(("files", cid), data.get("files") or [])


async def _tc_file(fid: str) -> dict:
    data = await _tc_json(f"task=file.display&view=file&id={fid}", f"file {fid}")
    f = data.get("file") if isinstance(data, dict) else None
    if not f or str(f.get("ID")) != fid or f.get("post_type") != "wpfd_file":
        raise NotFound(f"No file {fid} on {TC_HOST}. Use search_caselaw / search_legislation.")
    return f


def _tc_hit(tree, f: dict) -> DecisionHit:
    title = _clean_title(f.get("post_title", ""))
    cid = str(f.get("catid", ""))
    branch = _branch(tree, cid)
    snippet = "; ".join(x for x in (branch, f"publicado no site {f['created']}" if f.get("created") else "") if x)
    return DecisionHit(id=str(f["ID"]), title=title, court=_court(tree, cid), date="",
                       case_number=_case_number(title), snippet=snippet,
                       url=_tc_url(f.get("linkdownload", "")) if f.get("linkdownload") else TREE_PAGE)


async def _tc_search(query: str) -> list[DecisionHit]:
    """The plugin's own search: up to SEARCH_CAP newest title/metadata matches."""
    key = ("search", _fold(query))
    got = _cached(key)
    if got is not None:
        return got
    tree = await _tree()
    r = await _http.post(AJAX + "task=search.display", data={"q": query, "limit": str(SEARCH_CAP)})
    if r.status_code != 200:
        raise SourceError(_http.error(TC_HOST, "search failed", r.status_code), r.status_code)
    hits = []
    for row in re.findall(r"<tr>(.*?)</tr>", r.text, re.S):
        a = re.search(r'data-id="(\d+)" href="([^"]+)"[^>]*>([^<]*)</a>', row)
        if not a:
            continue
        cid = re.search(r"/index\.php/download/(\d+)/", a[2])
        cid = cid[1] if cid else ""
        title = _clean_title(a[3])
        if not _is_decision(tree, cid, title):
            continue
        created = re.search(r'class="created">([^<]*)<', row)
        hits.append(_tc_hit(tree, {"ID": a[1], "post_title": title, "catid": cid, "linkdownload": a[2],
                                   "created": created[1].strip() if created else ""}))
    return _store(key, hits)


async def _tc_year(year: str) -> list[DecisionHit]:
    """Every decision filed under `year` (full listing of that year's categories)."""
    tree = await _tree()
    cats = [cid for cid, c in tree.items() if c["leaf"] and _root(tree, cid) in DEC_ROOTS
            and any(tree[p]["name"] == year for p in c["path"])]
    hits = []
    for cid in cats:
        hits += [_tc_hit(tree, f) for f in await _tc_files(cid)]
    return hits


async def _tc_decision(fid: str) -> Decision:
    tree = await _tree()
    f = await _tc_file(fid)
    cid = str(f.get("catid", ""))
    title = _clean_title(f.get("post_title", ""))
    if not _is_decision(tree, cid, title) or f.get("ext") != "pdf":
        raise NotFound(f"File {fid} on {TC_HOST} is not a decision. Use search_caselaw.")
    url = _tc_url(f["linkdownload"])
    text = await _pdf(url, int(f.get("size") or 0), TC_HOST)
    meta = {k: v for k, v in (("Categoria", " > ".join(tree[p]["name"] for p in tree.get(cid, {}).get("path", []))),
                              ("Publicado no site", f.get("created", "")), ("PDF", url)) if v}
    return Decision(id=fid, title=title, text=text, url=url, court=_court(tree, cid), date=_pt_date(text),
                    case_number=_case_number(title), metadata=meta)


# --------------------------------------------------------------------------- #
# Supremo Tribunal de Justiça (section pages)
# --------------------------------------------------------------------------- #
async def _stj_list(section: str) -> list[DecisionHit]:
    got = _cached(("stj", section))
    if got is not None:
        return got
    label, page = STJ_SECTIONS[section]
    r = await _http.get(page)
    if r.status_code != 200:
        raise SourceError(_http.error(STJ_HOST, f"section page failed: {page}", r.status_code), r.status_code)
    hits, seen = [], set()
    for href, inner in re.findall(r'<a [^>]*href="(https://www\.stj\.cv/wp-content/uploads/[^"]+\.pdf)"[^>]*>(.*?)</a>',
                                  r.text, re.S):
        m = _STJ_ID.match(href)
        title = _http.clean(htmllib.unescape(re.sub(r"<[^>]+>", " ", inner)))
        if not m or m[1] in seen or not title:
            continue
        seen.add(m[1])
        hits.append(DecisionHit(id=m[1], title=title, court=f"Supremo Tribunal de Justiça, {label}",
                                case_number=_case_number(title), url=f"{STJ}/wp-content/uploads/{m[1]}"))
    return _store(("stj", section), hits)


async def _stj_decision(path: str) -> Decision:
    for sec in STJ_SECTIONS:
        hit = next((h for h in await _stj_list(sec) if h.id == path), None)
        if hit:
            break
    else:
        raise NotFound(f"'{path}' is not listed on the STJ's jurisprudence pages. Use search_caselaw.")
    text = await _pdf(hit.url, None, STJ_HOST)
    return Decision(id=hit.id, title=hit.title, text=text, url=hit.url, court=hit.court, date=_pt_date(text),
                    case_number=hit.case_number, metadata={"PDF": hit.url})


# --------------------------------------------------------------------------- #
# JURIS CV (jurisprudencia.cv, CSMJ): STJ and the two Relação courts, HTML full text
# --------------------------------------------------------------------------- #
_JURIS_ID = re.compile(r"^(?:https?://(?:www\.)?jurisprudencia\.cv/juris/)?(?:ECLI|JURIS):CV:(STJ|TRB|TRS):(\d{4}):(\d{1,6})/?$",
                       re.I)


async def _juris_search(q: str, court: str, year: str, limit: int, page: int) -> Results:
    params: dict = {"page": page, "perPage": limit, "offset": (page - 1) * limit}
    params["sorts[dataAcordao]"] = "-1"   # newest first, also with a query (the site's default order is not by date)
    if q:
        params["queries[freesearch]"] = q
    if court:
        params["queries[courts][]"] = JURIS_COURTS[court][0]
    if year:
        params["queries[initial_date]"], params["queries[end_date]"] = f"01/01/{year}", f"31/12/{year}"
    hdr = {"X-Requested-With": "XMLHttpRequest", "Accept": "application/json"}
    r = await _http.get(f"{JURIS}/items/loadItems", params=params, headers=hdr)
    quoted = False
    if r.status_code >= 500 and q and not q.startswith('"'):
        # the site's search crashes on some bare words (e.g. despedimento); the same word as an exact phrase works
        r = await _http.get(f"{JURIS}/items/loadItems", params={**params, "queries[freesearch]": f'"{q}"'},
                            headers=hdr)
        quoted = r.status_code == 200
    if r.status_code != 200 or "json" not in r.headers.get("content-type", ""):
        err = _http.error(JURIS_HOST, "search failed", r.status_code)
        if r.status_code >= 500 and (court or year):
            err += (" The JURIS CV site itself fails on some term and court/year combinations (seen: "
                    "'despedimento'); try another wording or fewer words.")
        raise SourceError(err, r.status_code)
    data = r.json()
    hits = [DecisionHit(id=x["ecli"], title=f"{x.get('tribunal', '')} {x['ecli']}".strip(),
                        court=_http.clean(x.get("tribunal")), date=_http.iso_date(x.get("dataAcordao")),
                        snippet=_http.clean(htmllib.unescape(re.sub(r"<[^>]+>", "", x.get("sumario") or "")))[:300],
                        url=f"{JURIS}/juris/{x['ecli']}/")
            for x in data.get("records", []) if _JURIS_ID.match(x.get("ecli") or "")]
    newest = ""
    if q and page == 1 and hits and hits[0].date:
        scope = f" in {year}" if year else ""
        newest = (f"Sorted newest first: the newest decision{scope} containing the search words is dated "
                  f"{hits[0].date}; no later decision{scope} in the index contains them (that is not the date "
                  f"of the court's latest decision: later ones on other topics are not listed). ")
    elif q and page == 1 and not hits:
        newest = ("No decision in the index contains these words" + (f" in {year}" if year else "")
                  + (" for this court" if court else "") + ". ")
    return Results(items=hits, total=data.get("queryRecordCount"), note=(
        newest + "JURIS CV (CSMJ): STJ (~770 acórdãos, 1994-) and Relação de Barlavento/Sotavento (2017-); "
        + ("site free-text search" if q else "newest first")
        + ("; the site crashed on the bare query, so it was re-run as an exact phrase" if quoted else "")
        + ". Not every STJ judgment is in it. "
        "The year filter works here too (whole calendar year; no other date range). "
        "Tribunal Constitucional: court=tc; stj.cv's own selection: section=..."))


async def _juris_decision(ecli: str) -> Decision:
    url = f"{JURIS}/juris/{ecli}/"
    r = await _http.get(url)
    if r.status_code == 404:
        raise NotFound(f"No decision {ecli} on JURIS CV.")
    if r.status_code != 200 or 'id="integral-text"' not in r.text:
        if r.status_code == 200 and ecli not in r.text:
            raise NotFound(f"No decision {ecli} on JURIS CV.")
        raise SourceError(_http.error(JURIS_HOST, f"decision page failed: {url}", r.status_code), r.status_code)
    doc = lxml_html.fromstring(r.content)
    meta = {}
    for h in doc.iter("h4"):
        k, v = h.find(".//strong[@class='content-title']"), h.find(".//span[@class='content']")
        if k is not None and v is not None and _http.clean(v.text_content()):
            meta[_http.clean(k.text_content()).rstrip(":")] = _http.clean(v.text_content())

    def tab(tid: str) -> str:
        el = doc.find(f".//div[@id='{tid}']")
        if el is None:
            return ""
        title = el.find("h4")
        if title is not None:
            el.remove(title)
        out = _http.html_to_md(lxml_html.tostring(el, encoding="unicode"))
        return "" if _fold(out).strip(" .") == "nao disponivel" else out

    text = tab("integral-text") or tab("parcial-text")
    if not text:
        raise NotFound(f"JURIS CV shows no text for {ecli}.")
    court = JURIS_COURTS[ecli.split(":")[2].lower()][1]
    num = meta.get("Nº Convencional") or meta.get("Processo") or ""
    return Decision(id=ecli, title=f"{court} {num or ecli}".strip(), text=text, url=url, court=court,
                    date=_http.iso_date(meta.pop("Data do Acordão", "")), case_number=meta.pop("Processo", ""),
                    summary=tab("summary"), metadata={**meta, "ECLI (JURIS CV)": ecli, "PDF": url + "pdf"})


# --------------------------------------------------------------------------- #
# Legislation (TC file categories)
# --------------------------------------------------------------------------- #
_ART = re.compile(r"^(?:ARTIGO|Artigo|ART\.|Art\.)\s*(\d{1,4}|[IVXLC]{1,6})\s*\.?\s*[º°o]?\s*(?:[-–]\s*([A-Z]))?\.?$")


_DIV = re.compile(r"(?i)^(?:livro|t[ií]tulo|cap[ií]tulo|sec[cç][aã]o|subsec[cç][aã]o)\s+(?:[IVXLC]+|\d+|[úu]nico)\s*$")


def _articles(text: str) -> tuple[list[TocEntry], dict[str, str]]:
    """Cut on 'Artigo N.º' heading lines. Numbering restarts (a decree's own articles before
    the code it approves, amending laws in a BO copy) start a new run; the longest run gets
    plain labels ("483"), the others "5 (parte 2)"."""
    lines = text.split("\n")
    heads = []
    for i, ln in enumerate(lines):
        m = _ART.match(ln.strip())
        if m:
            heads.append((i, m[1] + (f"-{m[2]}" if m[2] else "")))
    runs: list[list[tuple[int, str]]] = []
    prev = "start"
    for i, lab in heads:
        num = int(re.match(r"\d+", lab)[0]) if lab[0].isdigit() else None
        if prev == "start" or (num is None) != (prev is None) or lab == "1":
            runs.append([])                  # numbering restarts: a new act or part
        elif lab in {x for _, x in runs[-1]}:
            continue                         # repeated label inside a run: a quoted article, keep as text
        runs[-1].append((i, lab))
        prev = num
    if not runs:
        return [], {}
    main = max(range(len(runs)), key=lambda k: len(runs[k]))
    flat = []
    for k, run in enumerate(runs):
        for i, lab in run:
            flat.append((i, lab if k == main else f"{lab} (parte {k + 1})"))
    toc, texts = [], {}
    for n, (i, lab) in enumerate(flat):
        end = flat[n + 1][0] if n + 1 < len(flat) else len(lines)
        for j in range(i + 1, end):     # the next book/title/chapter heading is not part of the article
            if _DIV.match(lines[j].strip()):
                end = j
                break
        chunk = "\n".join(lines[i:end]).strip()
        texts[lab] = chunk
        nxt = next((x.strip() for x in lines[i + 1:i + 3] if x.strip()), "")
        head = nxt if len(nxt) < 90 and not nxt.endswith((".", ";", ":")) else ""
        toc.append(TocEntry(title=f"{lines[i].strip()} {head}".strip(), level=0, provision=lab))
    return toc, texts


def _norm_prov(p: str) -> str:
    s = _http.clean(p)
    s = re.sub(r"(?i)^(artigo|art\.?|article)\s*", "", s)
    m = re.match(r"(?i)^(\d{1,4}|[IVXLC]{1,6})\s*\.?\s*[º°o]?\s*(?:[-–]\s*([A-Z]))?\.?\s*(?:\(?\s*parte\s*(\d+)\s*\)?)?$", s)
    if not m:
        return s
    lab = m[1].upper() + (f"-{m[2].upper()}" if m[2] else "")
    return f"{lab} (parte {m[3]})" if m[3] else lab


async def _law_cats() -> dict[str, str]:
    """leaf catid -> label ("Legislação Complementar > Códigos")."""
    tree = await _tree()
    return {cid: " > ".join(tree[p]["name"] for p in c["path"]) for cid, c in tree.items()
            if c["leaf"] and c["path"][0] in LAW_ROOTS}


def _law_number(title: str) -> str:
    m = re.search(r"(?i)\b(lei(?: constitucional)?|decreto[- ]legislativo|decreto[- ]lei)\s*(?:n\.?\s*[º°o]?\s*)?"
                  r"(\d{1,3}\s*[-/]\s*[IVX]{1,4}\s*[-/]\s*\d{2,4}|\d{1,3}\s*[-/]\s*\d{2,4})", title)
    return f"{m[1].capitalize()} n.º {re.sub(r'\s*-\s*', '/', m[2])}" if m else ""


SCANNED_LAWS = {"3363", "3366", "3359", "3360", "3368"}   # 1980 Constitution, its 3 revisions and the 1992 one: image-only PDFs (verified: no text layer)


async def _law(id: str) -> dict:
    m = _TC_ID.match(_http.clean(id))
    if not m:
        raise BadRequest("Use a law id from search_legislation: the Tribunal Constitucional file id, "
                         "e.g. '323' (Código Civil).")
    fid = m[1]
    if fid in _docs:
        return _docs[fid]
    cats = await _law_cats()
    f = await _tc_file(fid)
    cid = str(f.get("catid", ""))
    if cid not in cats or f.get("ext") != "pdf":
        raise NotFound(f"File {fid} on {TC_HOST} is not one of its legislation texts. Use search_legislation.")
    url = _tc_url(f["linkdownload"])
    text = await _pdf(url, int(f.get("size") or 0), TC_HOST)
    toc, arts = _articles(text)
    title = _clean_title(f.get("post_title", ""))
    meta = {k: v for k, v in (("Categoria", cats[cid]), ("Número", _law_number(title)),
                              ("Publicado no site", f.get("created", "")), ("PDF", url)) if v}
    law = {"id": fid, "title": title, "url": url, "text": text, "toc": toc, "arts": arts, "meta": meta}
    return _http.lru_put(_docs, fid, law, 6)


# --------------------------------------------------------------------------- #
class CaboVerde(Jurisdiction):
    code = "cv"
    name = "Cabo Verde"
    languages = ("pt",)
    aliases = ("cape verde", "cabo verde", "cpv", "cv")
    sources = (
        Source(
            name="Tribunal Constitucional de Cabo Verde (tribunalconstitucional.cv)",
            url=TREE_PAGE,
            covers=("caselaw", "legislation"),
            licence=("'Copyright © 2026 . Todos os direitos Reservados | Tribunal Constitucional de Cabo "
                     "Verde' footer; no terms-of-use page (checked 2026-11-06)"),
            commercial_use=None,
            ai_use=None,    # no robots.txt (404); no AI/TDM clause on the site
            auth="none",
            rate_limit=("unknown; no robots.txt, no Crawl-delay; 1 s spacing, no 429 in ~40 requests "
                        "(2026-11)"),
            terms_url=f"{TC}/",
        ),
        Source(
            name="Supremo Tribunal de Justiça de Cabo Verde, jurisprudência (stj.cv)",
            url=f"{STJ}/index.php/1a-sec-civel/",
            covers=("caselaw",),
            licence=("'© 2023 Supremo Tribunal de Justiça, All Rights Reserved' footer; no terms-of-use "
                     "page (checked 2026-11-06)"),
            commercial_use=None,
            ai_use=None,    # no robots.txt (404); no AI/TDM clause on the site
            auth="none",
            rate_limit=("unknown; no robots.txt, no Crawl-delay; 1 s spacing, no 429 in ~10 requests "
                        "(2026-11)"),
            terms_url=f"{STJ}/",
        ),
        Source(
            name="JURIS CV – Jurisprudência Cabo-verdiana (Conselho Superior da Magistratura Judicial)",
            url=f"{JURIS}/items",
            covers=("caselaw",),
            licence=("/advertencia: 'As informações que constam deste sítio são públicas e podem ser reproduzidas, "
                     "desde que a respectiva fonte seja mencionada. No entanto, é proibida a sua utilização para "
                     "fins comerciais ou ofensivos.' (checked 2026-11-10)"),
            commercial_use=False,
            ai_use=None,    # robots.txt: User-agent * disallows /sys/remote/ only; no AI/TDM clause
            auth="none (login optional, not used)",
            rate_limit=("robots.txt Crawl-delay: 10 (documented); 10 s spacing, no 429 in ~12 requests "
                        "(2026-11-10)"),
            terms_url=f"{JURIS}/advertencia",
            warning=("JURIS CV: reproduction allowed with the source named (jurisprudencia.cv, CSMJ); "
                     "commercial use is forbidden by its terms."),
            probe={"caselaw_query": "homicídio", "decision_id": "JURIS:CV:STJ:2026:1299",
                   "filters": {"court": "stj"}},
        ),
    )
    caselaw_filters = {
        "court": ("'stj' (Supremo Tribunal de Justiça on JURIS CV, 1994-), 'trb' / 'trs' (Relação de "
                  "Barlavento / Sotavento, JURIS CV), or 'tc' (Tribunal Constitucional, incl. the STJ's "
                  "1995-2015 constitutional decisions). Default: all three JURIS CV courts"),
        "year": ("YYYY. On JURIS CV (stj/trb/trs) it restricts to that calendar year. For the TC it lists "
                 "that year's decisions in full and the query matches titles only"),
        "section": ("the STJ's own site (stj.cv) selection by section: 'civel', 'criminal' or "
                    "'administrativo'"),
    }
    min_interval = {TC_HOST: 1.0, STJ_HOST: 1.0, JURIS_HOST: 10.0}
    notes = ("Supremo Tribunal de Justiça (~770 acórdãos, 1994-) and the two Relação courts from JURIS CV "
             "(CSMJ, HTML full text, non-commercial terms); Tribunal Constitucional decisions (acórdãos, "
             "pareceres, decisões sumárias; 1995-, court=tc) and the stj.cv selection (~360, 2021-, "
             "section=...) as PDFs; ~30 core laws (codes, court organic laws, "
             "constitutions) as hosted by the TC, not consolidated. The Boletim Oficial's terms forbid copying "
             "without INCV permission, so it is not used.")
    gaps = (
        "Boletim Oficial (all laws and decrees beyond ~30 TC-hosted texts): INCV terms forbid copying 'sem a prévia autorização'",
        ("STJ: JURIS CV holds ~770 acórdãos (1994-2026) with thin years (e.g. 2014, 2016: 2 each; "
         "1995-2006 almost none) and stj.cv ~360 (2021-); the rest of the STJ's judgments are not published online"),
        "First-instance and appeal court decisions: not researched yet",
        "Consolidated legislation: not researched yet",
    )
    samples = {
        "caselaw_query": "amparo",
        "decision_id": "3488",            # Acórdão n.º 3/2020, TC (recurso de amparo)
        "legislation_query": "Código",
        "law_id": "323",                  # Código Civil
        "provision": "483",
    }

    # ------------------------------------------------------------------ #
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        q = _http.clean(query or "")
        f = filters or {}
        limit = max(1, min(int(limit), 50))
        page = max(1, int(page))
        court = (f.get("court") or "").strip().lower()
        section = (f.get("section") or "").strip().lower()
        year = str(f.get("year") or "").strip()
        if court not in ("", "tc", *JURIS_COURTS):
            raise BadRequest("court must be 'stj', 'trb', 'trs' or 'tc'.")
        if section and section not in STJ_SECTIONS:
            raise BadRequest("section must be 'civel', 'criminal' or 'administrativo'.")
        if year and not re.fullmatch(r"(19|20)\d{2}", year):
            raise BadRequest("year must be YYYY, e.g. 2024.")
        if not section and court != "tc":
            return await _juris_search(q, court, year, limit, page)
        hits: list[DecisionHit] = []
        notes = []
        if court == "tc":
            if year or not q:
                y = year or _http.today()[:4]
                tc = await _tc_year(y)
                hits += [h for h in tc if not q or _matches(q, h.title)]
                notes.append(f"TC: full listing of {y}; the query matches titles only, not the decision text, "
                             "so 0 hits does not mean no decision deals with it")
            else:
                hits += await _tc_search(q)
                notes.append(f"TC: site search (titles/metadata, {SEARCH_CAP} newest matches; add a year "
                             "filter for a complete list)")
        if section:
            for sec in ([section] if section else list(STJ_SECTIONS)):
                hits += [h for h in await _stj_list(sec)
                         if (not q or _matches(q, h.title)) and (not year or _year_of(h.title) == year)]
            notes.append("STJ: selected judgments only, titles (number + keywords) filtered")
        seen, uniq = set(), []
        for h in hits:      # the TC files some decisions under two categories (same title, two file ids)
            k = (h.case_number, _fold(h.title)) if h.case_number else h.id
            if k not in seen:
                seen.add(k)
                uniq.append(h)
        hits = uniq
        hits.sort(key=lambda h: _year_of(h.title) or "0", reverse=True)
        start = (page - 1) * limit
        return Results(items=hits[start:start + limit], total=len(hits),
                       note="; ".join(notes) + ". Hit dates are not in the listings; get_decision reads them.")

    async def get_decision(self, id):
        ident = _http.clean(id)
        m = _JURIS_ID.match(ident)
        if m:
            return await _juris_decision(f"JURIS:CV:{m[1].upper()}:{m[2]}:{m[3]}")
        m = _STJ_ID.match(ident)
        if m:
            return await _stj_decision(m[1])
        m = _TC_ID.match(ident)
        if m:
            return await _tc_decision(m[1])
        raise BadRequest("Give a decision id from search_caselaw: a JURIS CV id ('JURIS:CV:STJ:2026:1299'), "
                         "a Tribunal Constitucional file id ('3488') or an stj.cv upload path "
                         "('2025/05/Acordao-05-2024-....pdf').")

    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        q = _http.clean(query or "")
        limit = max(1, min(int(limit), 50))
        page = max(1, int(page))
        cats = await _law_cats()
        hits = []
        for cid, label in cats.items():
            for f in await _tc_files(cid):
                title = _clean_title(f.get("post_title", ""))
                if q and not _matches(q, f"{title} {label}"):
                    continue
                hits.append(LawHit(id=str(f["ID"]), title=title, type=label.split(" > ")[-1],
                                   number=_law_number(title), url=_tc_url(f.get("linkdownload", "")),
                                   has_toc=str(f["ID"]) not in SCANNED_LAWS,
                                   snippet=(f"{label}; publicado no site {f.get('created', '')}".strip("; ")
                                            + ("; SCANNED PDF, no text layer: cannot be read with this tool, "
                                               "open the Source link" if str(f["ID"]) in SCANNED_LAWS else ""))))
        start = (page - 1) * limit
        note = ("About 30 core texts hosted by the Tribunal Constitucional; copies of Boletim "
                "Oficial issues or compilations, not consolidated.")
        if not hits or re.search(r"trabalh|laboral", _fold(q or "")):
            note += (" Not held: the Código Laboral / Código do Trabalho (cited as 'CL' in labour "
                     "decisions) and other laws outside the TC's list.")
        if any(h.id in SCANNED_LAWS for h in hits):
            note += (" The PDFs of the 1980 and 1992 Constitutions and the 1980 revisions are scans without a text layer: "
                     "get_legislation_text / _toc / _provision fail on them; read them at the source URL.")
        return Results(items=hits[start:start + limit], total=len(hits), note=note)

    async def get_legislation_toc(self, id):
        law = await _law(id)
        if not law["toc"]:
            raise NotFound(f"No 'Artigo' headings found in {law['title']}; use get_legislation_text.")
        return Toc(id=law["id"], title=law["title"], url=law["url"], entries=law["toc"])

    async def get_legislation_provision(self, id, provision):
        law = await _law(id)
        lab = _norm_prov(provision)
        text = law["arts"].get(lab)
        if text is None:
            raise NotFound(f"No article '{provision}' in {law['title']}. Labels are as get_legislation_toc "
                           "shows them, e.g. '483' or '5 (parte 2)'.")
        return Provision(law_id=law["id"], law_title=law["title"], provision=lab, text=text, url=law["url"])

    async def get_legislation_text(self, id):
        law = await _law(id)
        return LawText(id=law["id"], title=law["title"], text=law["text"], url=law["url"], metadata=law["meta"])
