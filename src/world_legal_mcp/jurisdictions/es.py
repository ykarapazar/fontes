"""Spain: consolidated state and regional legislation from the BOE open-data API.

Gotchas this code encodes:
  * Every request needs `Accept: application/json` or `application/xml`, else HTTP 400.
    The list endpoint answers JSON; `/texto` and `/texto/bloque/{id}` answer XML only.
  * Search is an Elasticsearch-style JSON string in the `query` parameter. Words inside
    `titulo:(a b)` are OR-ed, so each word gets its own `titulo:w` joined with `and`.
    The API gives no hit count (total = None); paging is offset/limit.
  * Block ids are irregular ("a1" in one law, "art1902" in the Código Civil, "a4-2" for
    Artículo 41), so provisions are resolved by their heading text, never by guessing ids.
    The whole consolidated text (`/texto`, ~3 MB for the Código Civil) is fetched once
    and kept in a small in-memory LRU; TOC, provision and full text all come from it.
  * Each block keeps every historical version; the current one is the last version whose
    fecha_vigencia is not in the future.
  * Old codes label disposiciones only "Primera." under a "DISPOSICIONES TRANSITORIAS"
    heading; the label is rebuilt as "Disposición transitoria primera".
  * Reuse terms (boe.es aviso legal, 2024 licence) require every reused consolidated text
    to say it is informative only and give the last-update date: _NOTICE is appended.

Case law covers the Constitutional Court (Tribunal Constitucional) only, from its own
database "Buscador de jurisprudencia constitucional" (hj.tribunalconstitucional.es).
Ordinary courts are not offered: CENDOJ (poderjudicial.es) puts its search behind an image
CAPTCHA and restricts reuse to personal use (commercial use, mass download and
database-building need a CGPJ reuse procedure).

TC gotchas:
  * Search is stateful ASP.NET MVC: GET the search page for an anti-forgery token (form
    field + cookie), POST the form to BuscarAjax (needs X-Requested-With, else it answers
    "{}"), then GET Resolucion/List, which reads the search from the session cookie. The
    three steps run under one lock so concurrent searches cannot swap sessions.
  * The list is always ordered by date (newest first), never by relevance; page sizes are
    10/20/30/40/50 only, so the adapter fetches the covering source page(s) and slices.
  * Decisions live at Resolucion/Show/{internal number}; the adapter exposes the TC's own
    designation ("STC 31/2010", "ATC 31/2010", "DTC 1/2004") and also accepts the ECLI
    (ECLI:ES:TC:2010:31, autos end in "A", declaraciones in "D"). A designation is resolved
    with a number/year search, cached in memory.
  * www.tribunalconstitucional.es (main site, aviso legal) sits behind a JavaScript
    proof-of-work browser check and is never fetched; hj. has no such check.
"""
from __future__ import annotations

import asyncio
import datetime
import json
import re
import unicodedata

import lxml.html
from lxml import etree

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

API = "https://www.boe.es/datosabiertos/api/legislacion-consolidada"
_ID_RE = re.compile(r"^BOE-[A-Z]-\d{4}-\d+$")
_HEAD_LEVEL = {"libro": 0, "anexo": 0, "titulo": 1, "capitulo": 2, "seccion": 3, "subseccion": 4}
_DISP = {"adicionales": "adicional", "transitorias": "transitoria",
         "derogatorias": "derogatoria", "finales": "final"}
_SCOPES = {"state": "1", "regional": "2"}
_NOTICE = ("_Texto consolidado de carácter meramente informativo; solo el BOE publicado tiene "
           "carácter oficial. Basado en datos de la Agencia Estatal Boletín Oficial del Estado "
           "(https://www.boe.es); última actualización {date}._")
_NOTICE_OUTDATED = ("_Texto consolidado de carácter meramente informativo; solo el BOE publicado tiene "
                    "carácter oficial. Basado en datos de la Agencia Estatal Boletín Oficial del Estado "
                    "(https://www.boe.es); consolidado solo hasta {date}, sin las reformas posteriores._")

_OUTDATED = ("the BOE flags this text as out of date: recent amendments are not yet merged, "
             "so check the BOE before relying on it")

_laws: dict[str, dict] = {}

HJ = "https://hj.tribunalconstitucional.es/HJ/es"
_TYPES = {"S": ("SENTENCIA", "STC"), "A": ("AUTO", "ATC"), "D": ("DECLARACION", "DTC")}
_ABBR = {"STC": "S", "SENTENCIA": "S", "ATC": "A", "AUTO": "A", "DTC": "D", "DECLARACION": "D"}
_DEC_RE = re.compile(r"^(STC|ATC|DTC|SENTENCIA|AUTO|DECLARACION)\s*(\d+)\s*/\s*(\d{4})$")
_ECLI_RE = re.compile(r"^ECLI:ES:TC:(\d{4}):(\d+)([AD]?)$")
_MONTHS = {m: i for i, m in enumerate(("enero febrero marzo abril mayo junio julio agosto "
                                       "septiembre octubre noviembre diciembre").split(), 1)}
_hj_lock = asyncio.Lock()
_hj_token: list[str] = []          # [anti-forgery form token] once fetched
_shows: dict[str, str] = {}         # "STC 31/2010" -> Show URL


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _today() -> str:
    return datetime.date.today().strftime("%Y%m%d")


def _ymd(s) -> str:
    """'20260907T125934Z' / '18890724' -> '2026-09-07'."""
    m = re.match(r"^(\d{4})(\d{2})(\d{2})", str(s or ""))
    return f"{m[1]}-{m[2]}-{m[3]}" if m else ""


def _fold(s: str) -> str:
    """Lower-case, accents stripped: 'Disposición' -> 'disposicion'."""
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def _key(label: str) -> str:
    """Lookup key: 'Artículo 1902', 'art. 1902', '1902', 'Art 1.902' -> '1902'."""
    k = _fold(label).strip()
    k = re.sub(r"^(articulos?|arts?)\b\.?", "", k)
    k = re.sub(r"(?<!\d)\d{1,3}(?:\.\d{3})+(?!\d)", lambda m: m[0].replace(".", ""), k)  # 1.902 -> 1902
    k = re.sub(r"(?<=\d)[^a-z0-9]+(?=\d)", "_", k)  # '1.1' '1,5' '1-1' '1/1' '1 1' stay distinct from '11' '15'
    return re.sub(r"[^a-z0-9_]", "", k)


def _check_id(law_id: str) -> str:
    law_id = (law_id or "").strip().upper()
    if not _ID_RE.match(law_id):
        raise BadRequest(f"law id {law_id!r} is not a BOE identifier (e.g. BOE-A-1889-4763 for "
                         "the Código Civil). Find it with search_legislation.")
    return law_id


async def _get(url: str, accept: str, **kw):
    r = await _http.get(url, headers={"Accept": accept}, **kw)
    if r.status_code == 404:
        raise NotFound(f"BOE has no consolidated text at {url.removeprefix(API)}")
    if r.status_code != 200:
        raise SourceError(f"BOE open-data API returned HTTP {r.status_code}: "
                          f"{_http.clean(r.text)[:200]}", r.status_code)
    return r


# --------------------------------------------------------------------------- #
# Parsing the consolidated text
# --------------------------------------------------------------------------- #
def _current(bloque):
    """The version in force today (last one not starting in the future), and a 'not yet' flag."""
    versions = bloque.findall("version")
    if not versions:
        return None, False
    live = [v for v in versions if v.get("fecha_vigencia", "") <= _today()]
    return (live[-1], False) if live else (versions[-1], True)


def _visible(bq) -> bool:
    """BOE hides some editorial notes after a date (caduca=, class noDesdeYYYYMMDD)."""
    if bq.get("caduca") and bq.get("caduca") < _today():
        return False
    m = re.search(r"noDesde(\d{8})", bq.get("class") or "")
    return not (m and _today() >= m[1])


def _paras(version) -> list[str]:
    out = []
    for el in version:
        tag = _http.localname(el)
        if tag == "p":
            t = _http.text(el)
            if t:
                out.append(f"**{t}**" if el.get("class") == "articulo" else t)
        elif tag == "blockquote":
            if _visible(el):
                out += [f"> {t}" for t in (_http.text(p) for p in el.iter("p")) if t]
        elif tag:
            out += _http.html_paragraphs(etree.tostring(el, encoding="unicode"))
    return out


def _heading_level(version) -> int | None:
    """Level of a heading block from its first <p class>, or None if it is not a heading."""
    for p in version.findall("p"):
        base = re.sub(r"_(num|tit)$", "", p.get("class") or "")
        return _HEAD_LEVEL.get(base, 1 if p.get("class") in ("centro_redonda", "centro_negrita")
                               else None)
    return None


def _label(head: str, attr: str, group: str) -> str:
    """'Artículo 1. Objeto.' -> 'Artículo 1'; 'Primera.' under DISPOSICIONES FINALES ->
    'Disposición final primera'; 'Arts. 127 a 130.' -> 'Artículos 127 a 130'."""
    m = re.match(r"^((?:Arts?\.\s*)?[^.]*?)(?:\.\s|\.?$)", head) if head else None
    lab = _http.clean(m[1] if m and m[1] else attr)
    lab = re.sub(r"^Arts\.?\s+", "Artículos ", lab)
    lab = re.sub(r"^Art\.?\s+", "Artículo ", lab)
    lab = re.sub(r"^(Artículos? \d+) A ", r"\1 a ", lab)
    if re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúñ]+", lab) and group:
        kind = _DISP.get(_fold(group).split()[-1])
        if kind:
            lab = f"Disposición {kind} {lab.lower()}"
    return lab


def _parse(xml: bytes) -> list[dict]:
    """Consolidated text -> ordered blocks: {id, kind, label, title, level, paras}."""
    try:
        root = etree.fromstring(xml)
    except etree.XMLSyntaxError:
        raise SourceError("BOE returned a text that is not XML")
    blocks, level, group, seen = [], 0, "", set()
    for b in root.iter("bloque"):
        v, future = _current(b)
        if v is None:
            continue
        paras = _paras(v)
        if future:
            paras.insert(0, f"_No vigente todavía: en vigor desde {_ymd(v.get('fecha_vigencia'))}._")
        tipo = b.get("tipo")
        art = v.find("p[@class='articulo']")
        hl = _heading_level(v)
        if tipo == "encabezado" or (tipo == "precepto" and art is None and hl is not None):
            title = " — ".join(_http.text(p) for p in v.findall("p")
                               if _http.text(p) and not (p.get("class") or "").startswith("parrafo"))
            level = hl if hl is not None else 1
            group = title if _fold(title).startswith("disposicion") else ""
            if group:
                level = 1
            blocks.append({"id": b.get("id"), "kind": "head", "label": "", "title": title,
                           "level": level, "paras": paras})
            continue
        if tipo == "precepto":
            head = _http.text(art) if art is not None else ""
            label = _label(head, b.get("titulo") or b.get("id"), group)
        elif tipo in ("preambulo", "parte_dispositiva") and paras:
            head, label = "Preámbulo", "Preámbulo"
        else:  # firma, parte_final, ...: in the full text, not in the TOC
            blocks.append({"id": b.get("id"), "kind": "other", "label": "", "title": "",
                           "level": level, "paras": paras})
            continue
        if label in seen:
            label = f"{label} [{b.get('id')}]"
        seen.add(label)
        blocks.append({"id": b.get("id"), "kind": "prov", "label": label,
                       "title": (head or label).rstrip(". "), "level": level + 1, "paras": paras})
    if not blocks:
        raise SourceError("BOE returned a consolidated text with no blocks")
    return blocks


def _consolidated_to(xml: bytes) -> str:
    """Latest amendment date merged into the text (YYYYMMDD), '' if none can be read."""
    try:
        root = etree.fromstring(xml)
    except etree.XMLSyntaxError:
        return ""
    dates = [v.get("fecha_vigencia", "") for v in root.iter("version")]
    return max((d for d in dates if d <= _today()), default="")


def _notice(law: dict) -> str:
    return (_NOTICE_OUTDATED if law["outdated"] else _NOTICE).format(date=law["as_of"])


async def _law(law_id: str) -> dict:
    law_id = _check_id(law_id)
    if law_id in _laws:
        return _laws[law_id]
    r = await _get(f"{API}/id/{law_id}/metadatos", "application/json")
    try:
        meta = r.json()["data"][0]
    except (ValueError, KeyError, IndexError, TypeError):
        raise SourceError("BOE metadata payload was not understood")
    r = await _get(f"{API}/id/{law_id}/texto", "application/xml")
    outdated = _http.clean((meta.get("estado_consolidacion") or {}).get("texto")) == "Desactualizado"
    # For an out-of-date text fecha_actualizacion is just when the BOE last touched the record,
    # so show the date up to which amendments are actually merged instead.
    as_of = (_ymd(_consolidated_to(r.content)) if outdated else "") or _ymd(meta.get("fecha_actualizacion"))
    law = {"id": law_id, "meta": meta, "blocks": _parse(r.content), "outdated": outdated,
           "title": _http.clean(meta.get("titulo")) or law_id,
           "url": meta.get("url_html_consolidada") or f"https://www.boe.es/buscar/act.php?id={law_id}",
           "as_of": as_of}
    return _http.lru_put(_laws, law_id, law, 4)


def _rank(hits: list[dict], query: str) -> list[dict]:
    """Stable: exact-title hit first, then short state-level 'publishing' titles ending in the query."""
    q = _fold(query).strip(" .")

    def tier(d):
        t = _fold(_http.clean(d.get("titulo")) or "").strip(" .")
        if t == q:
            return 0
        if (t.endswith(q) and (d.get("ambito") or {}).get("codigo") == "1"
                and len(t) - len(q) <= 70):
            return 1
        return 2
    return sorted(hits, key=tier)


def _law_hit(d: dict) -> LawHit:
    status = "no longer in force" if d.get("vigencia_agotada") == "S" else "in force"
    if d.get("estatus_derogacion") == "S":
        status = "repealed"
    cons = _http.clean((d.get("estado_consolidacion") or {}).get("texto"))
    if cons and cons != "Finalizado":
        status += f" (consolidation: {cons})"
        if cons == "Desactualizado":
            status += " - " + _OUTDATED
    where = " · ".join(x for x in (_http.clean((d.get("ambito") or {}).get("texto")),
                                   _http.clean((d.get("departamento") or {}).get("texto"))) if x)
    return LawHit(id=d["identificador"], title=_http.clean(d.get("titulo")),
                  type=_http.clean((d.get("rango") or {}).get("texto")),
                  number=_http.clean(d.get("numero_oficial")), date=_ymd(d.get("fecha_disposicion")),
                  status=status, snippet=where,
                  url=d.get("url_html_consolidada")
                  or f"https://www.boe.es/buscar/act.php?id={d['identificador']}")


# --------------------------------------------------------------------------- #
# Tribunal Constitucional (hj.tribunalconstitucional.es)
# --------------------------------------------------------------------------- #
def _dec_key(id: str) -> tuple[str, int, int]:
    """'STC 31/2010', 'Sentencia 31/2010', 'ECLI:ES:TC:2010:31' -> ('S', 31, 2010)."""
    raw = _fold(_http.clean(id)).upper().replace(" ", "")
    m = _ECLI_RE.match(raw)
    if m:
        return (m[3] or "S", int(m[2]), int(m[1]))
    m = _DEC_RE.match(raw)
    if m:
        return (_ABBR[m[1]], int(m[2]), int(m[3]))
    raise BadRequest(f"decision id {id!r} not understood. Use the TC designation (e.g. 'STC 31/2010', "
                     "'ATC 31/2010', 'DTC 1/2004') or the ECLI ('ECLI:ES:TC:2010:31', autos end in A).")


def _dec_id(kind: str, num: int, year: int) -> str:
    return f"{_TYPES[kind][1]} {num}/{year}"


async def _hj(method: str, url: str, **kw):
    r = await _http.request(method, url, **kw)
    if r.status_code != 200:
        raise SourceError(f"Tribunal Constitucional (hj) returned HTTP {r.status_code}", r.status_code)
    if "Voight-Kampff" in r.text[:2000] or "captcha" in r.text[:5000].lower():
        raise SourceError("Tribunal Constitucional answered with a browser check; not bypassed.")
    return r


async def _hj_search(form: dict, page: int, size: int) -> list[str]:
    """Run one search; return the HTML of list page `page` ("" when nothing matches).
    Caller holds _hj_lock (the search lives in the session cookie)."""
    for attempt in (1, 2):
        if not _hj_token:
            r = await _hj("GET", f"{HJ}/Busqueda/Index")
            m = re.search(r'name="__RequestVerificationToken" type="hidden" value="([^"]+)"', r.text)
            if not m:
                raise SourceError("Tribunal Constitucional search page has no form token")
            _hj_token[:] = [m[1]]
        r = await _http.post(f"{HJ}/Busqueda/BuscarAjax", headers={"X-Requested-With": "XMLHttpRequest"},
                             data={"__RequestVerificationToken": _hj_token[0], **form})
        try:
            js = r.json() if r.status_code == 200 else {}
        except ValueError:
            js = {}
        if str(js.get("success")) == "1":
            break
        msg = _http.clean(js.get("message"))
        if msg:  # the source's own answer, e.g. "No se han encontrado resultados"
            if "encontrado" in _fold(msg):
                return ""
            if "inesperado" in _fold(msg):  # the site's generic failure, not a message about the query
                raise SourceError("Tribunal Constitucional search failed on this query (the site returned an "
                                  "unexpected error); try simpler wording.")
            raise BadRequest(f"Tribunal Constitucional search refused the query: {msg}")
        _hj_token.clear()  # token/session expired (500 or "{}"): new token, one more try
        if attempt == 2:
            raise SourceError(f"Tribunal Constitucional search failed (HTTP {r.status_code})",
                              r.status_code)
    r = await _hj("GET", f"{HJ}/Resolucion/List",
                  params={"sortOrder": "desc", "resultsPerPage": size, "page": page})
    return r.text


def _hit_date(title: str, year: str) -> str:
    """'..., de 27 de mayo (BOE ...' + '2026' -> '2026-05-27'."""
    m = re.search(r",\s*de (\d{1,2}) de (\w+)", title)
    mon = _MONTHS.get(_fold(m[2])) if m else None
    return f"{year}-{mon:02d}-{int(m[1]):02d}" if mon else ""


def _parse_list(page_html: str) -> tuple[list[DecisionHit], int | None]:
    if not page_html:
        return [], 0
    doc = lxml.html.fromstring(page_html)
    m = re.search(r"encontrado\s*<b>\s*([\d.]+)", page_html)
    total = int(m[1].replace(".", "")) if m else None
    hits = []
    for li in doc.xpath("//ul[@id='resolution-list']/li"):
        a = li.find(".//a[@class='resolucion-item']")
        if a is None:
            continue
        head = _http.text(a)
        m = re.match(r"^(?:(.*?)\.\s+)?(SENTENCIA|AUTO|DECLARACI[OÓ]N)\s+(\d+)/(\d{4})", head)
        if not m:
            continue
        kind = _ABBR[_fold(m[2]).upper()]
        did = _dec_id(kind, int(m[3]), int(m[4]))
        url = "https://hj.tribunalconstitucional.es" + a.get("href")
        _http.lru_put(_shows, did, url, 500)
        rows = {_http.text(tr[0]): _http.text(tr[1]) for tr in li.iter("tr") if len(tr) >= 2}
        hits.append(DecisionHit(
            id=did, title=re.sub(r"\s*\(BOE.*$", "", head),
            court=f"Tribunal Constitucional{f' ({m[1]})' if m[1] else ''}",
            date=_hit_date(head, m[4]), case_number=rows.get("Tipo de Proceso", ""),
            snippet=rows.get("Síntesis Descriptiva", ""), url=url))
    return hits, total


async def _show_url(kind: str, num: int, year: int) -> str:
    did = _dec_id(kind, num, year)
    if did in _shows:
        return _shows[did]
    form = {"TIPO_RESOLUCION": _TYPES[kind][0], "NUMERO_RESOLUCION": num, "ANNO_RESOLUCION": year}
    async with _hj_lock:
        hits, _ = _parse_list(await _hj_search(form, 1, 10))
    for h in hits:
        if h.id == did:
            return h.url
    raise NotFound(f"The Tribunal Constitucional database has no {did}.")


def _ficha(doc) -> dict[str, str]:
    out = {}
    try:
        ft = doc.get_element_by_id("ficha-tecnica")
    except KeyError:
        return out
    for tr in ft.iter("tr"):
        cells = [c for c in tr if isinstance(c.tag, str)]
        if len(cells) >= 2:
            out[_http.text(cells[0])] = _http.text(cells[1])
    return out


# --------------------------------------------------------------------------- #
# Adapter
# --------------------------------------------------------------------------- #
class Spain(Jurisdiction):
    code = "es"
    name = "Spain"
    languages = ("es",)
    aliases = ("esp", "spain", "españa", "espana")
    sources = (
        Source(
            "BOE — Agencia Estatal Boletín Oficial del Estado, Datos abiertos: legislación consolidada",
            "https://www.boe.es/datosabiertos/api/legislacion-consolidada",
            covers=("legislation",),
            licence=("BOE reuse conditions (licencia tipo, Resolución 27-06-2024, under Ley 37/2007): "
                     "attribution with link to boe.es, consolidated texts must be marked as "
                     "informative only with their last-update date"),
            commercial_use=True,
            ai_use=None,
            auth="none",
            rate_limit=("unknown: no limit in the API docs (APIconsolidada.pdf) or terms; robots.txt "
                        "has no Crawl-delay. 1 s spacing, no 429 seen in ~20 requests (2026-11-05)."),
            terms_url="https://www.boe.es/informacion/aviso_legal/index.php#reutilizacion",
        ),
        Source(
            "Tribunal Constitucional — Buscador de jurisprudencia constitucional (Sistema HJ)",
            "https://hj.tribunalconstitucional.es/",
            covers=("caselaw",),
            licence=("unknown: hj.tribunalconstitucional.es shows no aviso legal or reuse terms; the "
                     "main site's aviso legal sits behind a JavaScript browser check and could not be "
                     "read (2026-11-05). Court decisions are excluded from copyright (Ley de Propiedad "
                     "Intelectual art. 13)."),
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit=("unknown: nothing published; robots.txt is 404 (no rules). 1 s spacing; a search "
                        "costs 2-3 requests (token, POST, list). No 429 seen (2026-11-05)."),
            terms_url="https://www.tribunalconstitucional.es/es/Paginas/Aviso-legal.aspx",
        ),
    )
    caselaw_filters = {
        "type": "sentencia, auto or declaracion (default all three)",
        "date_from": "decision date from, YYYY-MM-DD",
        "date_to": "decision date to, YYYY-MM-DD",
        "search_in": "text (default, whole decision) or summary (síntesis descriptiva: far fewer, "
                     "more on-topic hits, but the words must appear next to each other in that order, as a "
                     "phrase: 'proceso de despido' works, 'despido nulo discriminación' finds nothing; "
                     "use one or two words)",
    }
    legislation_filters = {
        "search_in": "title (default) or text (full text of the consolidated law)",
        "scope": "state (estatal) or regional (autonómico); default both",
        "in_force": "yes, no, or all (default)",
    }
    min_interval = {"www.boe.es": 1.0, "hj.tribunalconstitucional.es": 1.0}
    notes = ("Consolidated state and autonomous-community law from the BOE (Spanish only). "
             "Law id = BOE identifier (Código Civil BOE-A-1889-4763). Case law covers the "
             "Constitutional Court only (id 'STC 31/2010' or its ECLI); ordinary courts (CENDOJ) "
             "are behind a CAPTCHA and restrict reuse to personal use.")
    gaps = (
        "Ordinary courts incl. Tribunal Supremo and TSJs (CENDOJ): image CAPTCHA; terms restrict reuse to personal use",
        "Legislation in co-official languages (Catalan, Basque, Galician): not researched yet",
    )
    samples = {
        "caselaw_query": "Estatuto de Autonomía de Cataluña",
        "decision_id": "STC 31/2010",
        "legislation_query": "Código Civil",
        "law_id": "BOE-A-1889-4763",
        "provision": "Artículo 1902",
    }

    async def search_caselaw(self, query, *, limit, page, filters):
        query = _http.clean(query.replace("&", " "))  # '&' makes the TC search crash upstream
        if not query:
            raise BadRequest("query is empty, e.g. 'derecho al olvido' or 'Estatuto de Autonomía'.")
        types = [_TYPES["S"][0], _TYPES["A"][0], _TYPES["D"][0]]
        t = _fold(str(filters.get("type", ""))).strip().upper()
        if t:
            if t not in _ABBR:
                raise BadRequest("type must be 'sentencia', 'auto' or 'declaracion'.")
            types = [_TYPES[_ABBR[t]][0]]
        where = {"text": "0", "summary": "6"}.get(str(filters.get("search_in", "text")).strip().lower())
        if not where:
            raise BadRequest("search_in must be 'text' (whole decision) or 'summary' (síntesis descriptiva).")
        form = {"TIPO_RESOLUCION": types, "TIPO_BUSQUEDA_LIBRE": where, "BUSQUEDA_LIBRE": query}
        for key, field in (("date_from", "FECHA_DESDE"), ("date_to", "FECHA_HASTA")):
            v = str(filters.get(key, "")).strip()
            if v:
                m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", v)
                if not m:
                    raise BadRequest(f"{key} must be YYYY-MM-DD, e.g. 2010-01-31.")
                form[field] = f"{m[3]}/{m[2]}/{m[1]}"
        limit = max(1, min(int(limit), 50))
        start = (max(1, int(page)) - 1) * limit
        size = next(n for n in (10, 20, 30, 40, 50) if n >= limit)
        first, last = start // size + 1, (start + limit - 1) // size + 1
        hits, total = [], None
        async with _hj_lock:
            for p in range(first, last + 1):
                if p > first:  # same search, next list page: no new POST needed
                    r = await _hj("GET", f"{HJ}/Resolucion/List",
                                  params={"sortOrder": "desc", "resultsPerPage": size, "page": p})
                    more, _ = _parse_list(r.text)
                else:
                    more, total = _parse_list(await _hj_search(form, p, size))
                hits += more
                if total is not None and p * size >= total:
                    break
        skip = start - (first - 1) * size
        return Results(hits[skip:skip + limit], total=total,
                       note="This source holds Constitutional Court (TC) decisions only, ordered by date (newest "
                            "first); it cannot rank by relevance. Tribunal Supremo, TSJ and Audiencia rulings "
                            "(e.g. despido nulo/improcedente) are in CENDOJ and cannot be searched here: it is "
                            "behind a CAPTCHA and limits reuse to personal use. Any hits below are TC "
                            "decisions"
                            + ("; hits contain all the words anywhere in the decision, any order; add filters "
                               "{\"search_in\":\"summary\"} to match only the court's own subject summary: fewer, "
                               "more on-topic hits, but the words must then appear together as an exact "
                               "phrase, so use one or two words."
                               if where == "0" else
                               "; hits contain the words as an exact phrase in the court's summary (several "
                               "words must appear next to each other in that order); if nothing is found try "
                               "one word or search_in=text."))

    async def get_decision(self, id):
        kind, num, year = _dec_key(id)
        did = _dec_id(kind, num, year)
        url = await _show_url(kind, num, year)
        r = await _hj("GET", url)
        doc = lxml.html.fromstring(r.content)
        try:
            body = doc.get_element_by_id("complete_resolucion")
        except KeyError:
            raise NotFound(f"The Tribunal Constitucional page for {did} has no text ({url}).")
        text = _http.html_to_md(etree.tostring(body, encoding="unicode"))
        f = _ficha(doc)
        head = doc.xpath("//li[@id='resolucion-identifier']/h2")
        title = _http.text(head[0]) if head else did
        boe = re.search(r"\((BOE[^)]*)\)", title)
        title = re.sub(r"\s*\(BOE.*$", "", title)
        organ = f.get("Órgano", "")
        ecli = next((_http.text(e) for e in doc.find_class("ecli")), "")
        meta = {"ECLI": ecli, "Órgano": organ, "BOE": boe[1] if boe else "",
                "Magistrados": f.get("Magistrados", ""),
                "Síntesis descriptiva": f.get("Síntesis Descriptiva", ""),
                "Resumen": f.get("Resumen", "")}
        return Decision(id=did, title=f"{organ}. {title}" if organ else title, text=text, url=url,
                        court=f"Tribunal Constitucional{f' ({organ})' if organ else ''}",
                        date=_http.iso_date(f.get("Fecha de resolución", "")),
                        case_number=f.get("Tipo y número de registro", ""),
                        summary=f.get("Síntesis Analítica", ""),
                        metadata={k: v for k, v in meta.items() if v})

    async def search_legislation(self, query, *, limit, page, filters):
        field = {"title": "titulo", "text": "texto"}.get(
            str(filters.get("search_in", "title")).strip().lower())
        if not field:
            raise BadRequest("search_in must be 'title' or 'text'.")
        words = re.findall(r"\w+", query or "")
        if not words:
            raise BadRequest("query needs at least one word, e.g. 'Código Civil' or 'arrendamientos'.")
        terms = [f"{field}:{w}" for w in words]
        scope = str(filters.get("scope", "")).strip().lower()
        if scope:
            if scope not in _SCOPES:
                raise BadRequest("scope must be 'state' or 'regional'.")
            terms.append(f"ambito@codigo:{_SCOPES[scope]}")
        in_force = str(filters.get("in_force", "all")).strip().lower()
        if in_force not in ("yes", "no", "all"):
            raise BadRequest("in_force must be 'yes', 'no' or 'all'.")
        if in_force != "all":
            terms.append(f"vigencia_agotada:{'N' if in_force == 'yes' else 'S'}")
        limit = max(1, min(int(limit), 50))
        q = json.dumps({"query": {"query_string": {"query": " and ".join(terms)}}}, ensure_ascii=False)
        r = await _get(API, "application/json",
                       params={"query": q, "limit": limit, "offset": (max(1, int(page)) - 1) * limit})
        try:
            data = r.json().get("data") or []
        except ValueError:
            raise SourceError("BOE search payload was not JSON", r.status_code)
        if field == "titulo":
            data = _rank(data, query)
        return Results([_law_hit(d) for d in data], total=None,
                       note="Consolidated texts are informative only; the BOE gives no hit count.")

    async def get_legislation_toc(self, id):
        law = await _law(id)
        entries = [TocEntry(title=b["title"], level=b["level"], provision=b["label"])
                   for b in law["blocks"] if b["kind"] in ("head", "prov") and b["title"]]
        return Toc(id=law["id"], title=law["title"], url=law["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        law = await _law(id)
        want = (provision or "").strip()
        if not want:
            raise BadRequest("provision is empty. Use e.g. 'Artículo 1902', 'art. 1902' or '1902'.")
        provs = [b for b in law["blocks"] if b["kind"] == "prov"]
        hit = (next((b for b in provs if b["label"] == want), None)
               or next((b for b in provs if b["id"] == want), None)
               or next((b for b in provs if _key(b["label"]) == _key(want)), None))
        if hit is None:
            arts = [b["label"] for b in provs if _key(b["label"]).isdigit()]
            last = f" Its last numbered article is {arts[-1]!r}." if arts else ""
            raise NotFound(f"{want!r} not found in {law['id']}.{last} See get_legislation_toc for the labels "
                           "(e.g. 'Artículo 1902', 'Disposición adicional primera').")
        notes = [_notice(law)]
        if law["outdated"]:
            notes.insert(0, f"_Aviso: {_OUTDATED}._")
        text = "\n\n".join(hit["paras"] + notes)
        return Provision(law_id=law["id"], law_title=law["title"], provision=hit["label"], text=text,
                         url=f"{law['url']}#{hit['id']}", as_of=law["as_of"])

    async def get_legislation_text(self, id):
        law = await _law(id)
        parts = []
        for b in law["blocks"]:
            if b["kind"] == "head":
                parts.append(f"{'#' * min(6, b['level'] + 2)} {b['title']}")
            else:
                parts += b["paras"]
        m = law["meta"]
        if law["outdated"]:
            parts.append(f"_Aviso: {_OUTDATED}._")
        parts.append(_notice(law))
        meta = {"Rango": _http.clean((m.get("rango") or {}).get("texto")),
                "Ámbito": _http.clean((m.get("ambito") or {}).get("texto")),
                "Publicado": f"{_http.clean(m.get('diario'))} {_ymd(m.get('fecha_publicacion'))}".strip(),
                "ELI": m.get("url_eli", "")}
        return LawText(id=law["id"], title=law["title"], text="\n\n".join(parts), url=law["url"],
                       as_of=law["as_of"], metadata={k: v for k, v in meta.items() if v})
