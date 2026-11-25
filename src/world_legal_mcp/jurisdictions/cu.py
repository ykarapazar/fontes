"""Cuba: legislation from the Gaceta Oficial de la República de Cuba, read from the Gazette's own
site (www.gacetaoficial.gob.cu) and from the issues the Ministry of Justice (MINJUS) reposts on
www.minjus.gob.cu ("Publicaciones > Normas Jurídicas").

How the sources work (verified 2026-11-10, UK IP, honest User-Agent):
  * www.gacetaoficial.gob.cu (Drupal 7, DESOFT). GET /es/normas-juridicas is a norm database view
    with GET filters: field_tipo_de_norma_tid (Ley=11, Decreto Ley=12, Constitución=4777, ...),
    field_numero_v_value (number), field_anno_norma_value[value][year], field_estado_norma_juridica_tid,
    body_value ("Resumen" contains). 20 rows a page (&page=N, 0-based). Each row: title linking
    to a norm page (/es/ley-189-de-2026-de-asamblea-nacional-del-poder-popular), the norm code
    ("Identificador de norma", GOC-2026-540-O78; older norms have none), status, summary.
    The norm page has no text, only "Publicado en" linking the issue page
    (/es/gaceta-oficial-no-78-ordinaria-de-2026), which links the issue PDF (text layer;
    goc-2026-o78.pdf, older ones go_x_024_2011.pdf). About 103 Leyes and 340 Decretos-Leyes are
    indexed (Decretos-Leyes back to 1934, mostly as later republications).
  * MINJUS: GET /es/publicaciones/normas_juridicas is one page listing ~64 Gazette issue PDFs
    (2019-2026) with MINJUS's own titles. Used first for those issues (faster host).
  * ids: a Gazette issue "GOC-2026-O26" (O = Ordinaria, EX = Extraordinaria, ES = Edición
    Especial), a norm code "GOC-2026-227-O26" (opens just that norm of its issue), or a
    gacetaoficial.gob.cu norm page slug ("decreto-ley-143-de-2011-de-consejo-de-estado") for norms
    without a code (opens the whole issue). "Constitución" = GOC-2025-487-ES9, the 2019
    Constitution as reformed in 2025, republished whole.
  * Texts are as published in the Gazette, not consolidated, except the Constitution (republished
    in full after the 2025 reform).
  * Site search (/search/) is disallowed in robots.txt and on MINJUS behind Drupal "antibot"; not used.

Terms: neither site has a terms-of-use page. gacetaoficial.gob.cu footer: "Todos los Derechos
Reservados | © DESOFT 2019"; its help page (/es/node/123105) says nothing on automated use.
robots.txt (2026-11-10): "Crawl-delay: 10", disallows /search/, /admin/, /user/*, /node/add/ etc.
(the norm view /es/normas-juridicas and /sites/default/files/ are allowed); requests are spaced
10 s. The norm form has a "feed_me" anti-spam honeypot field; it is never sent. MINJUS:
"2020. MINJUS. Todos los derechos reservados.", Drupal default robots.txt, no Crawl-delay.
gacetaoficial.gob.cu answers intermittently (connect timeouts from the UK; unreachable on
2026-11-06, reachable 2026-11-10): one retry, then a clear error.

Not used (2026-11-06):
  * www.tsp.gob.cu (Tribunal Supremo Popular): its terms forbid automated access ("Se compromete
    a no acceder, o intentar acceder, a ninguno de los servicios utilizando medios automatizados,
    incluidos secuencias de comandos o rastreadores web."). It publishes no decision database
    anyway (only bulletins/journal PDFs). So no case law for Cuba.
  * www.parlamentocubano.gob.cu: lists the same Gazette PDFs but only by file name, no titles.
"""
from __future__ import annotations

import re
from urllib.parse import unquote

import httpx
from lxml import html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from .._http import fold_marks as _fold
from ..models import LawHit, LawText, Provision, Results, Toc, TocEntry

HOST = "www.minjus.gob.cu"
BASE = f"https://{HOST}"
LISTING = BASE + "/es/publicaciones/normas_juridicas"
SOURCE = "Ministerio de Justicia de Cuba (Gaceta Oficial reposts)"
GHOST = "www.gacetaoficial.gob.cu"
GBASE = f"https://{GHOST}"
GSOURCE = "Gaceta Oficial de la República de Cuba (gacetaoficial.gob.cu)"
NORMS = GBASE + "/es/normas-juridicas"
PER_PAGE = 20
CONSTITUTION = "GOC-2025-487-ES9"   # 2019 Constitution as reformed in 2025, republished whole
MAX_BYTES = 40 * 1024 * 1024
_TYPES = {"constitucion": 4777, "ley": 11, "decreto-ley": 12, "decreto ley": 12, "ley decreto": 5062,
          "ley-decreto": 5062, "codigo de comercio": 4330, "decreto": 13, "decreto presidencial": 4583,
          "resolucion": 14, "resolucion conjunta": 15, "acuerdo": 16, "instruccion": 18}
_STATUS = {"vigente": 25, "derogada": 26, "modificada": 27, "edicion actualizada": 3857,
           "anotada y concordada": 4535}
# Updated editions the Gazette site posts under /es/algunas-legislaciones-cubanas (base text not in
# its norm database).
_EDITIONS = {"codigo civil": ("CODIGO-CIVIL", "Ley No. 59 de 1987, Código Civil (edición actualizada "
                              "al 8 de noviembre de 2022)",
                              GBASE + "/sites/default/files/codigo_civil_actualizado_0.pdf", "2022-11-08")}
_EDS = {"O": "ordinaria", "EX": "extraordinaria", "ES": "edicion-especial"}
_ED_CODE = {v: k for k, v in _EDS.items()}
_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)+$")
_ISSUE_SLUG = re.compile(r"gaceta-oficial-no-(\d+)-(ordinaria|extraordinaria|edicion-especial)-de-(\d{4})$")
_QTYPE = re.compile(r"^(constituci[oó]n|decreto[- ]ley|ley[- ]decreto|decreto presidencial|decreto|ley)"
                    r"(?:\s+(?:no\.?\s*)?(\d+))?(?:\s*(?:de|/)\s*(\d{4}))?$", re.I)

_FILE = re.compile(r"/(goc-\d{4}-[a-z]*\d+[a-z]?)[^/]*\.pdf$", re.I)
_ID = re.compile(r"^GOC-(\d{4})-(?:\d+-)?([A-Z]*\d+[A-Z]?)$")
_NORM = re.compile(r"^GOC-\d{4}-\d+-[A-Z]+\d+$")
_ART = re.compile(r"^(?:ART[ÍI]CULO|Art[íi]culo)\s+(\d+)(?:\.\d+)?\s*(?:bis|ter)?\s*(?:[.\-–:]|$)")
_HEAD = re.compile(r"^(T[ÍI]TULO|CAP[ÍI]TULO|SECCI[ÓO]N|DISPOSICI[ÓO]N(?:ES)?)\b(?![a-záéíóú])")
_LEVEL = {"T": 1, "C": 2, "S": 3, "D": 1}
_PAGE_JUNK = re.compile(
    r"^(\d{1,5}|_+|\d{2}/\d{2}/\d{4}\s*GOC-\S+"
    r"|(?:Gaceta Oficial|GACETA OFICIAL)(?: de la República)?\s*(?:\d{1,2} de [a-z]+ de \d{4})?\s*\d*)$")
_CAPS_U = re.compile(r"(?<=[A-ZÁÉÍÓÚÑ])u(?=[A-ZÁÉÍÓÚÑ])")   # some issues' fonts give "ARTÍCuLO"
_MONTHS = {m: i + 1 for i, m in enumerate(
    "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split())}
_PARA_START = re.compile(r"^(?:POR CUANTO|POR TANTO|RESUELVO|HAGO SABER|[a-zñ]\)|\d+\.\s|[A-ZÁÉÍÓÚÑ ]{6,}$)")

_list_cache: dict = {}
_doc_cache: dict = {}
_page_cache: dict = {}


def _norm_id(raw: str) -> str:
    m = _ID.match(_http.clean(raw).upper().replace(" ", ""))
    if not m:
        raise BadRequest("Cuban ids look like 'GOC-2026-O26' (Gaceta issue), 'GOC-2026-227-O26' "
                         "(a norm in it), a gacetaoficial.gob.cu norm slug "
                         "('decreto-ley-143-de-2011-de-consejo-de-estado') or 'Constitución'; "
                         "find them with search_legislation.")
    return f"GOC-{m[1]}-{m[2]}"


async def _listing() -> list[dict]:
    if "all" in _list_cache:
        return _list_cache["all"]
    r = await _http.get(LISTING)
    if r.status_code != 200:
        raise SourceError(_http.error(SOURCE, "listing failed", r.status_code), r.status_code)
    doc = lhtml.fromstring(r.content)
    doc.make_links_absolute(BASE)
    items, seen = [], set()
    for a in doc.xpath('//div[contains(@class,"views-field-title")]//a[not(@download)]'):
        href = a.get("href") or ""
        m = _FILE.search(unquote(href))
        title = _http.clean(a.text_content())
        if not m or not title:
            continue
        id_ = m[1].upper()
        if id_ in seen:
            continue
        seen.add(id_)
        items.append({"id": id_, "title": title.rstrip(" ."), "url": href})
    if not items:
        raise SourceError(f"Error ({SOURCE}): listing page changed (no Gazette PDFs found).", 200)
    _list_cache["all"] = items
    return items


def _type_number(title: str) -> tuple[str, str]:
    m = re.search(r"\b(Decreto[- ]Ley|Ley|Decreto Presidencial|Decreto|Resoluci[óo]n|C[óo]digo)\b"
                  r"(?:\s+(?:No\.?\s*)?(\d+(?:/\d{4})?))?", title, re.I)
    if not m:
        return "Gaceta Oficial", ""
    return m[1].title().replace("Decreto Ley", "Decreto-Ley"), m[2] or ""


def _es_date(s: str) -> str:
    m = re.search(r"(\d{1,2})\s+DE\s+([A-ZÁÉÍÓÚ]+)\s+DE\s+(\d{4})", s.upper())
    if not m or _fold(m[2]) not in _MONTHS:
        return ""
    return f"{m[3]}-{_MONTHS[_fold(m[2])]:02d}-{int(m[1]):02d}"


def _reflow(lines: list[str]) -> str:
    """PDF lines -> paragraphs: join wrapped lines, undo end-of-line hyphenation."""
    paras: list[str] = []
    for ln in lines:
        if not paras or _ART.match(ln) or _HEAD.match(ln) or _PARA_START.match(ln) \
                or paras[-1].endswith((".", ":", ";")) or paras[-1].isupper():
            paras.append(ln)
        elif re.search(r"\w ?-$", paras[-1]) and ln[:1].islower():
            paras[-1] = re.sub(r" ?-$", "", paras[-1]) + ln
        else:
            paras[-1] += " " + ln
    return "\n\n".join(paras)


def _parse(raw: str) -> dict:
    """Split a Gazette issue into norms and articles."""
    lines = [_CAPS_U.sub("U", ln) for ln in raw.split("\n") if ln and not _PAGE_JUNK.match(ln)]
    head = raw[:600]
    date = _es_date(head)
    # SUMARIO titles: chunks between dotted leaders, the ones carrying a norm code.
    first_code = next((i for i, ln in enumerate(lines) if _NORM.match(ln)), None)
    sumario = " ".join(lines[:first_code]) if first_code is not None else ""
    titles = {}
    for chunk in re.split(r"\.{4,}\s*\d+", sumario):
        prev = 0
        for m in re.finditer(r"\((GOC-\d{4}-\d+-[A-Z]+\d+)\)", chunk):
            t = _http.clean(chunk[prev: m.start()])[-250:]
            prev = m.end()
            t = re.sub(r"^.*?\b(?=(?:Ley|Decreto|Resoluci|Acuerdo|Instrucci|Dictamen|C[óo]digo|Constituci)\w*\b)",
                       "", t, count=1, flags=re.I)
            titles.setdefault(m[1], t or m[1])
    norms: list[dict] = []
    cur = {"code": "", "title": "", "lines": []}
    for ln in lines:
        if _NORM.match(ln):
            norms.append(cur)
            cur = {"code": ln, "title": titles.get(ln, ln), "lines": []}
        else:
            cur["lines"].append(ln)
    norms.append(cur)
    preamble = norms.pop(0)
    if not norms:                      # no norm code lines: whole issue is one norm
        norms = [{"code": "", "title": "", "lines": preamble["lines"]}]
    entries: list[TocEntry] = []
    provs: dict[str, tuple[str, str]] = {}   # label -> (heading line, text)
    order: list[tuple[str, int, str]] = []   # (norm code, article no, label)
    for nm in norms:
        if nm["code"]:
            entries.append(TocEntry(title=f"{nm['title']} ({nm['code']})" if nm["title"] != nm["code"]
                                    else nm["code"], level=0))
        level, last, i, L = 0, 0, 0, nm["lines"]
        while i < len(L):
            ln = L[i]
            h = _HEAD.match(ln)
            if h and ln.isupper():
                level = _LEVEL[_fold(h[1])[0].upper()]
                t = ln
                bare = re.match(r"^\S+\s+[IVXLC\d]+\w*$", ln)   # "TÍTULO I": its name is on the next line
                if i + 1 < len(L) and L[i + 1].isupper() and not _ART.match(L[i + 1]) \
                        and (bare or not _HEAD.match(L[i + 1])):
                    t += " - " + L[i + 1]
                    i += 1
                entries.append(TocEntry(title=t, level=level))
                i += 1
                continue
            a = _ART.match(ln)
            if a and last < int(a[1]) <= last + 5:
                n = last = int(a[1])
                j = i + 1
                while j < len(L) and not (_ART.match(L[j]) or (_HEAD.match(L[j]) and L[j].isupper())):
                    j += 1
                label = f"Artículo {n}"
                if label in provs:
                    label = f"Artículo {n} ({nm['code']})"
                provs[label] = (nm["code"], _reflow(L[i:j]))
                order.append((nm["code"], n, label))
                entries.append(TocEntry(title=_http.clean(ln)[:120], level=level + 1, provision=label))
                i = j
                continue
            i += 1
    body, bodies = [], {}
    if preamble["lines"] and norms[0]["code"]:
        body.append(_reflow(preamble["lines"]))
    for nm in norms:
        if nm["code"]:
            body.append(f"## {nm['title']} ({nm['code']})" if nm["title"] != nm["code"] else f"## {nm['code']}")
        body.append(_reflow(nm["lines"]))
        bodies[nm["code"]] = body[-1]
    return {"date": date, "entries": entries, "provs": provs, "order": order,
            "text": "\n\n".join(b for b in body if b), "norms": [n["code"] for n in norms if n["code"]],
            "titles": {n["code"]: n["title"] for n in norms if n["code"]}, "bodies": bodies}


def _narrow(item: dict, p: dict, code: str) -> tuple[dict, dict]:
    """Just one norm (by its code) of a parsed issue."""
    entries, on = [], False
    for e in p["entries"]:
        if e.level == 0:
            on = e.title == code or e.title.endswith(f"({code})")
        elif on:
            entries.append(e)
    q = dict(p, entries=entries, provs={k: v for k, v in p["provs"].items() if v[0] == code},
             order=[o for o in p["order"] if o[0] == code], text=p["bodies"][code], norms=[code])
    title = p["titles"].get(code, code)
    return {"id": code, "title": title if title != code else f"{code} ({item['title']})",
            "url": item["url"], "issue": item["id"]}, q


async def _gget(url: str, **kw):
    """GET on gacetaoficial.gob.cu, which often drops connections: one retry, then SourceError."""
    for attempt in (1, 2):
        try:
            return await _http.get(url, **kw)
        except httpx.TransportError as e:
            err = type(e).__name__
    raise SourceError(f"Error ({GSOURCE}): {GHOST} did not answer ({err}); the host is often "
                      "unreachable from abroad, try again later.", 504)


def _title(page: str) -> str:
    """Page title without the site name: '<title>Ley 189 de 2026 ... | Gaceta Oficial'."""
    m = re.search(r"<title>(.*?)</title>", page, re.S)
    return _http.clean(lhtml.fromstring(f"<p>{m[1]}</p>").text_content()).rsplit(" | ", 1)[0] if m else ""


async def _gpage(slug: str) -> str:
    """A gacetaoficial.gob.cu page by slug (norm or issue page), cached."""
    if slug in _page_cache:
        return _page_cache[slug]
    r = await _gget(f"{GBASE}/es/{slug}")
    if r.status_code == 404:
        raise NotFound(f"No page '{slug}' on {GHOST}; use search_legislation for ids.")
    if r.status_code != 200:
        raise SourceError(_http.error(GSOURCE, "page failed", r.status_code), r.status_code)
    _http.lru_put(_page_cache, slug, r.text, 64)
    return r.text


async def _gissue(issue: str, slug: str = "") -> dict:
    """Issue id (GOC-2011-EX24) -> {id, title, url of the PDF} from the issue page."""
    if not slug:
        m = re.match(r"^GOC-(\d{4})-(O|EX|ES)(\d+)$", issue)
        if not m:
            raise NotFound(f"{issue} is not a Gazette issue code the site can be asked for.")
        slug = f"gaceta-oficial-no-{int(m[3])}-{_EDS[m[2]]}-de-{m[1]}"
    page = await _gpage(slug)
    pdf = re.search(r'href="((?:https?://[^"/]+)?/sites/default/files/[^"]+\.pdf)"', page)
    if not pdf:
        raise NotFound(f"The {GHOST} page for {issue} links no PDF.")
    url = pdf[1] if pdf[1].startswith("http") else GBASE + pdf[1]
    return {"id": issue, "title": _title(page) or issue, "url": url}


async def _issue(issue: str, slug: str = "", item: dict | None = None) -> tuple[dict, dict]:
    if issue in _doc_cache:
        return _doc_cache[issue]
    if not slug and not item:
        try:
            item = next((x for x in await _listing() if x["id"] == issue), None)
        except (SourceError, httpx.TransportError):
            item = None                        # MINJUS down: the Gazette site may still answer
    source, get = (SOURCE, _http.get) if item and HOST in item["url"] else (GSOURCE, _gget)
    item = item or await _gissue(issue, slug)
    r = await get(item["url"], max_bytes=MAX_BYTES)
    if r.status_code != 200 or not r.content.startswith(b"%PDF"):
        raise SourceError(_http.error(source, "PDF download failed", r.status_code), r.status_code)
    raw = _http.pdf_text(r.content)
    if not raw:
        raise SourceError(f"Error ({source}): {issue} has no text layer (scan); open {item['url']}.", 200)
    out = (item, _parse(raw))
    _http.lru_put(_doc_cache, issue, out, 8)
    return out


async def _doc(id_: str) -> tuple[dict, dict]:
    raw = _http.clean(id_)
    if _fold(raw) in ("constitucion", "constitucion de la republica", "constitution"):
        raw = CONSTITUTION
    ekey = _fold(raw).replace("-", " ")      # search returns the id 'CODIGO-CIVIL'
    if ekey in _EDITIONS:
        id_, title, url, as_of = _EDITIONS[ekey]
        item, p = await _issue(id_, item={"id": id_, "title": title, "url": url})
        return item, dict(p, date=as_of)              # date of the update, not of the base law
    if _SLUG.match(raw) and not raw.startswith("goc-"):     # norm page slug on gacetaoficial.gob.cu
        page = await _gpage(raw)
        if "node-norma-juridica" not in page:
            raise BadRequest(f"'{raw}' is not a norm page on {GHOST}.")
        code = re.search(r"Identificador de norma:.*?field-item even\">\s*(GOC-[\w-]+)", page, re.S)
        pub = re.search(r'Publicado en:.*?href="/es/([^"]+)"', page, re.S)
        if code and _NORM.match(code[1]):
            return await _doc(code[1])
        if not pub:
            raise NotFound(f"{GHOST} gives no Gazette issue for '{raw}'.")
        m = _ISSUE_SLUG.search(pub[1])
        issue = f"GOC-{m[3]}-{_ED_CODE[m[2]]}{m[1]}" if m else pub[1].upper()
        item, p = await _issue(issue, pub[1])
        title = _title(page) or raw
        return {"id": raw, "title": f"{title} (in {item['title']}, whole issue)", "url": item["url"],
                "issue": item["id"]}, p
    issue = _norm_id(raw)
    item, p = await _issue(issue)
    code = raw.upper().replace(" ", "")
    if _NORM.match(code) and code in p["norms"]:
        return _narrow(item, p, code)
    return item, p


def _label(p: str, parsed: dict) -> str:
    s = _http.clean(p)
    if s in parsed["provs"]:
        return s
    code = re.search(r"GOC-\d{4}-\d+-[A-Z]+\d+", s.upper())
    bare = re.sub(r"GOC-\S+", "", s.upper())
    m = re.search(r"(\d+)", bare)
    if m and re.match(r"\s*(?:\.\d+|[-\s]*(?:BIS|TER|QU[AÁ]TER)\b)", bare[m.end():]):
        raise NotFound(f"No sub-article '{s}': only whole numbered articles (e.g. 'Artículo 5') are "
                       "indexed; bis/ter/.N sub-articles are not available.")
    if not m:
        raise BadRequest("Give an article number, e.g. 'Artículo 5', 'art. 5' or '5' "
                         "(add the norm code, e.g. '5 GOC-2026-228-O26', for a later norm in the issue).")
    n = int(m[1])
    for c, num, label in parsed["order"]:
        if num == n and (not code or c == code[0]):
            return label
    raise NotFound(f"No article {n}" + (f" in {code[0]}" if code else "") + " in this Gazette issue.")


class Cuba(Jurisdiction):
    code = "cu"
    name = "Cuba"
    languages = ("es",)
    aliases = ("cuba", "cub")
    sources = (
        Source(
            name=GSOURCE,
            url=NORMS,
            covers=("legislation",),
            licence="unknown; footer says 'Todos los Derechos Reservados | © DESOFT 2019', no licence or terms page",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="robots.txt Crawl-delay: 10 (obeyed, 10 s spacing). Host often times out on "
                       "connect from abroad (unreachable 2026-11-06, reachable 2026-11-10)",
            terms_url=GBASE + "/es/node/123105",
        ),
        Source(
            name=SOURCE,
            url=LISTING,
            covers=("legislation",),
            licence="unknown; site says 'Todos los derechos reservados', no licence or terms page",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 2 s spacing, no 429 seen in ~25 requests (2026-11). "
                       "Host often times out on connect (Cuban network)",
            terms_url=BASE + "/es",
        ),
    )
    min_interval = {HOST: 2.0, GHOST: 10.0}
    legislation_filters = {
        "type": "Constitución, Ley, Decreto-Ley, Ley-Decreto, Decreto, Decreto Presidencial, "
                "Resolución, Resolución Conjunta, Acuerdo, Instrucción, Código de Comercio",
        "number": "norm number, e.g. 189",
        "year": "one year of the norm, YYYY (the source filters a single year only, no range: "
                "run 2020, 2021, ... separately)",
        "status": "as the Gazette records it: Vigente, Modificada, Derogada, Edición Actualizada, "
                  "Anotada y Concordada (many norms carry none)",
    }
    notes = ("Legislation only: the Gaceta Oficial's own norm database and issue PDFs (as published, "
             "not consolidated; text layer), plus MINJUS reposts. Id 'Constitución' = the 2019 "
             "Constitution as reformed and republished whole in 2025; 'Código Civil' = the site's "
             "2022 updated edition (later amendments not applied). The Gazette site obeys a 10 s crawl delay and often times out from abroad. No case law source.")
    gaps = (
        "Case law: Tribunal Supremo terms forbid access 'utilizando medios automatizados'; it has no decision database anyway",
        "Primary acts: the Gazette's norm database indexes ~103 Leyes and ~340 Decretos-Leyes; older acts "
        "appear mostly as later republications, so completeness for pre-2019 in-force acts is unverified "
        "(2026-11-10: Leyes 75, 76, 85, 113, 65 are indexed; Ley 41/1983 and Ley 51/1985 are not, and "
        "the site's issue archive starts in 1990, so pre-1990 acts never republished are not online). "
        "Ley 59/1987 Código Civil is not indexed (served from the site's 2022 updated edition, id "
        "'Código Civil'); Código Penal Ley 151/2022 and Código de las Familias Ley 156/2022 are indexed",
        "Consolidation: texts as published, amendments not applied (except the Constitution's 2025 republication)",
        "Norms without a code (mostly pre-2019) open as their whole Gazette issue, not split out",
    )
    samples = {
        "legislation_query": "ley",
        "law_id": "GOC-2019-EX5",
        "provision": "Artículo 1",
    }

    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        q = _http.clean(query)
        m = _QTYPE.match(q)
        typ = _fold(filters.get("type", "")) or (_fold(m[1]) if m else "")
        num = _http.clean(filters.get("number", "")) or (m[2] if m and m[2] else "")
        year = _http.clean(filters.get("year", "")) or (m[3] if m and m[3] else "")
        status = _fold(filters.get("status", ""))
        params: dict = {}
        if typ:
            if typ not in _TYPES:
                raise BadRequest(f"Unknown type '{filters.get('type') or typ}'; use one of: "
                                 + self.legislation_filters["type"])
            params["field_tipo_de_norma_tid"] = _TYPES[typ]
        if num:
            if not num.isdigit():
                raise BadRequest("number is digits only, e.g. 189.")
            params["field_numero_v_value"] = num
        if year:
            if not re.fullmatch(r"\d{4}", year):
                raise BadRequest("year is YYYY, e.g. 2026.")
            params["field_anno_norma_value[value][year]"] = year
        if status:
            if status not in _STATUS:
                raise BadRequest(f"Unknown status; use one of: {self.legislation_filters['status']}")
            params["field_estado_norma_juridica_tid"] = _STATUS[status]
        if q and not m:
            params["body_value"] = q
        if not params:
            raise BadRequest("Give words from the norm's summary (e.g. 'registro civil'), a type and "
                             "number ('Ley 189', 'Decreto-Ley 143 de 2011') or filters.")
        try:
            res = await self._gsearch(params, limit, page, q)
            if page == 1 and not filters:
                if "constitucion" in _fold(q):
                    res.items.insert(0, LawHit(
                        id="Constitución", title="Constitución de la República de Cuba (2019, reformada y "
                        "republicada en 2025; texto completo)", type="Constitución", status="Vigente",
                        url=GBASE + "/es/normas-juridicas"))
                for key, (id_, title, url, _) in _EDITIONS.items():
                    if key in _fold(q):
                        res.items.insert(0, LawHit(id=id_, title=title, type="Ley", status="Edición Actualizada",
                                                   url=url))
                        res.note += (f" Entry 1 ('{id_}') is the site's updated edition of the base law as of "
                                     f"{_EDITIONS[key][3]}; later amendments (e.g. any Decreto-Ley listed below that "
                                     "modifies it) are NOT applied to it: check them separately.")
            return res
        except SourceError:
            if not q or filters:
                raise
            res = await self._msearch(q, limit, page)
            res.note = f"{GHOST} did not answer; fell back to: " + res.note
            return res

    async def _gsearch(self, params: dict, limit: int, page: int, q: str = "") -> Results:
        start = (page - 1) * limit
        hits, total, more = [], None, False
        for sp in range(start // PER_PAGE, (start + limit - 1) // PER_PAGE + 1):
            r = await _gget(NORMS, params={**params, "page": sp} if sp else params)
            if r.status_code != 200:
                raise SourceError(_http.error(GSOURCE, "norm search failed", r.status_code), r.status_code)
            doc = lhtml.fromstring(r.content)
            rows = doc.xpath('//div[contains(@class,"node-norma-juridica")]')
            # a norm whose whole summary is the query ("Código Penal.") goes first on its page
            rows = sorted(rows, key=lambda x: _fold(_http.clean(x.xpath('string(.//div[contains(@class,"field-name-body")]//p)'))
                                                    ).rstrip(". ") != _fold(q))
            for n, row in enumerate(rows):
                if sp * PER_PAGE + n < start or len(hits) >= limit:
                    continue
                a = row.xpath(".//h2//a")
                if not a:
                    continue
                title = _http.clean(a[0].text_content())
                txt = _http.clean(row.text_content())
                code = re.search(r"Identificador de norma:\s*(GOC-\d{4}-\d+-[A-Z]+\d+)", txt)
                st = ", ".join(_http.clean(x.text_content()) for x in
                               row.xpath('.//div[contains(@class,"field-name-field-estado-norma-juridica")]'
                                         '//div[contains(concat(" ",@class," ")," field-item ")]'))
                summ = re.search(r"Resumen:\s*(.*?)\s*(?:Leer más|$)", txt)
                typ, num = _type_number(title)
                slug = (a[0].get("href") or "").rsplit("/", 1)[-1]
                hits.append(LawHit(
                    id=code[1] if code else slug, title=title, type=typ,
                    number=num, status=st, snippet=(summ[1] if summ else "")[:300],
                    url=GBASE + (a[0].get("href") or "")))
            more = bool(doc.xpath('//li[contains(@class,"pager-next")]'))
            if not more:
                total = sp * PER_PAGE + len(rows)
                break
        if total is None:           # more pages exist: count the last one for the total
            last = re.search(r"[?&]page=(\d+)", (doc.xpath('//li[contains(@class,"pager-last")]//a/@href')
                                                   or [""])[0])
            if last and int(last[1]) > sp:
                r = await _gget(NORMS, params={**params, "page": int(last[1])})
                if r.status_code == 200:
                    total = int(last[1]) * PER_PAGE + len(lhtml.fromstring(r.content).xpath(
                        '//div[contains(@class,"node-norma-juridica")]'))
        for h in hits:      # the original of a norm with a "copia corregida" carries no status itself
            if not h.status:
                twin = next((x for x in hits if x is not h and x.title == h.title and x.status), None)
                if twin:
                    h.status = (f"{twin.status.replace('Copia corregida, ', '')} (estado tomado de la "
                                f"copia corregida {twin.id}; esta es la versión original)")
        note = ("Gaceta Oficial norm database (gacetaoficial.gob.cu); words match the "
                "norm summary ('Resumen'), not the full text; accents matter "
                "('Código Penal', not 'codigo penal').")
        if len({x.title for x in hits}) < len(hits):
            note += (" Entries with the same title are separate Gazette publications of one norm number "
                     "(e.g. the original and its 'copia corregida', or the text before and after a "
                     "referendum), not errors: compare each entry's 'Nota'. The Gazette does not say "
                     "which replaced which; a 'copia corregida' is the corrected republication of the original.")
        return Results(items=hits, total=total, note=note)

    async def _msearch(self, q: str, limit: int, page: int) -> Results:
        words = _fold(q).split()
        hits = []
        for it in await _listing():
            hay = _fold(it["title"] + " " + it["id"])
            if all(w in hay for w in words):
                typ, num = _type_number(it["title"])
                hits.append(LawHit(id=it["id"], title=it["title"], type=typ, number=num, url=it["url"]))
        start = (page - 1) * limit
        return Results(items=hits[start:start + limit], total=len(hits),
                       note="Searches MINJUS's titles of ~64 reposted Gazette issues only, "
                            "not the full Gaceta Oficial.")

    async def get_legislation_toc(self, id):
        item, p = await _doc(id)
        entries = p["entries"] or [TocEntry(
            title="(whole Gazette item, no article split: read it with get_legislation_text and look for the article there)", level=0)]
        return Toc(id=item["id"], title=item["title"], url=item["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        item, p = await _doc(id)
        label = _label(provision, p)
        code, text = p["provs"][label]
        return Provision(law_id=item["id"], law_title=item["title"], provision=label,
                         text=text, url=item["url"], as_of=p["date"])

    async def get_legislation_text(self, id):
        item, p = await _doc(id)
        meta = {"Fecha de publicación": p["date"]} if p["date"] else {}
        if p["norms"]:
            meta["Normas"] = ", ".join(p["norms"])
        return LawText(id=item["id"], title=item["title"], text=p["text"], url=item["url"],
                       as_of=p["date"], metadata=meta)
