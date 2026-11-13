"""Costa Rica: consolidated legislation from SINALEVI (Sistema Nacional de Legislación
Vigente), the Procuraduría General de la República's half of SCIJ.

Gotchas this code encodes (verified 2026-11-06 from a UK IP):
  * Old SCIJ links (pgrweb.go.cr/scij/...nrm_texto_completo.aspx?nValor1=1&nValor2={id})
    redirect to sinalevi.go.cr/ResultadosNormativa/Informacion?param1={id}. The id
    (IdFichaNorma, nValor2 / param1) is the norm's record number; it is the law id here.
  * The page is an empty shell; the text comes from POST
    /ResultadosNormativa/_CargarTextoCompleto (idFichaNorma, version, busqueda) as JSON
    {"html": ...}. version=-1 answers {"redireccionar": true, "direccion": "...param2={v}"}
    with the latest version id v; param2=0 means the id does not exist (no 404).
    /_CargarFicha (same pattern) gives the record card: title, date, version date.
  * The full-text HTML is one Word-made <html> document per article, each followed by a
    "Ficha Artículo {label}" link (labels: "16 BIS", "1 Transitorio", ...). Headings
    (TÍTULO, CAPÍTULO...) sit at the start of the next article's chunk.
  * Search: GET /BusquedaSimple/_CambiarResultados returns a JSON array, newest first,
    paged in 50s (cantidadResultados=50, pagina=n). It does not return a total.
    selectedBuscarEn=F searches the record (title, number), T the text.
  * No robots.txt on sinalevi.go.cr or pgrweb.go.cr (404). Terms: none beyond the footer
    "© Procuraduría de la República. Todos los derechos reservados."
  * Case law is not offered: Nexus PJ (nexuspj.poder-judicial.go.cr) carries a legal
    notice (Reglamento de datos personales del Poder Judicial, art. 37) prohibiting
    "la construcción de bases de datos paralelas mediante la utilización de herramientas
    robotizadas, de inteligencia artificial", and loads a bot-protection script.
"""
from __future__ import annotations

import html as _html
import json
import re
import unicodedata

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import LawHit, LawText, Provision, Results, Toc, TocEntry

HOST = "https://sinalevi.go.cr"
SEARCH = f"{HOST}/BusquedaSimple/_CambiarResultados"
TEXT = f"{HOST}/ResultadosNormativa/_CargarTextoCompleto"
FICHA = f"{HOST}/ResultadosNormativa/_CargarFicha"
PAGE = 50  # server page size
TYPES = {  # IdTipoNorma, from the search form (2026-11-06)
    "C": (1, "Constitución Política"), "TI": (15, "Tratados Internacionales"),
    "I": (7, "Normas internacionales sin aprobar"), "L": (8, "Ley"), "D": (5, "Decreto Ejecutivo"),
    "DTE": (6, "Decreto TSE"), "R": (12, "Reglamento"), "RM": (13, "Reglamento municipal"),
    "A": (3, "Acuerdo"), "AM": (2, "Acuerdo municipal"), "Z": (16, "Directriz"), "CIR": (4, "Circular"),
    "S": (14, "Resolución"), "O": (9, "Ordenanza"), "OC": (10, "Opinión Consultiva"),
    "OP": (11, "Opinión"), "AV": (17, "Aviso"),
}
_MARK = re.compile(r'<div class="pb-5 pt-2">\s*<a class="enlaceFicha"[^>]*>\s*Ficha Artículo([^<]*)</a>\s*</div>', re.I)
_HEADING = re.compile(r"^(T[IÍ]TULO|CAP[IÍ]TULO|SECCI[OÓ]N|LIBRO|PARTE)\b|^(TRANSITORIOS?|DISPOSICIONES [A-ZÁÉÍÓÚ ]+)$", re.I)
_ARTICLE = re.compile(r"^(ART[IÍ]CULO|Art[ií]culo|Transitorio|TRANSITORIO)\s+[\wº°]")
_ROMAN = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}
_cache: dict[str, dict] = {}


def _url(id: str) -> str:
    return f"{HOST}/ResultadosNormativa/Informacion?param1={id}&param2=&param3=1&param4="


def _id_note(id: str, title: str) -> str:
    """A law number typed as the id opens whichever record has that number: say so."""
    for rec, _y, ley in BASE_CODES.values():
        if id == ley.split()[-1] and id != rec:
            return (f"Id {id} is a SINALEVI record number, not the law number: this record is '{title}'. "
                    f"{ley} is record id {rec}.")
    return ""


def _norm_id(id) -> str:
    s = str(id or "").strip()
    m = re.search(r"(?:param1|nValor2)=(\d+)", s) or re.fullmatch(r"(\d{1,9})", s)
    if not m:
        raise BadRequest("Costa Rican law ids are SINALEVI record numbers (IdFichaNorma), e.g. '871' "
                         "(Constitución Política) or '15437' (Código Civil), or a sinalevi.go.cr / "
                         f"pgrweb.go.cr/scij link with param1= / nValor2=; got {id!r}.")
    return str(int(m[1]))


def _roman(s: str) -> int | None:
    s = s.upper()
    if not s or any(c not in _ROMAN for c in s):
        return None
    n = 0
    for a, b in zip(s, s[1:] + " "):
        v = _ROMAN[a]
        n += -v if b in _ROMAN and _ROMAN[b] > v else v
    return n


def _label(raw: str) -> str:
    """'16 BIS' -> '16 bis'; '1 Transitorio' -> 'Transitorio 1'."""
    s = _http.clean(raw).lower()
    m = re.fullmatch(r"(\w+)\s+transitorio", s)
    if m:
        return f"Transitorio {m[1]}"
    return s


def _key(label: str) -> str:
    """Normalise a user's provision label for lookup."""
    s = _http.clean(label).lower().replace("º", "").replace("°", "")
    s = re.sub(r"^(art[ií]culo|art\.?)\s*", "", s).strip(" .-")
    trans = bool(re.search(r"\btransitorio\b", s))
    s = re.sub(r"\btransitorio\b", "", s).strip(" .-")
    s = re.sub(r"^0+(?=\d)", "", s)
    s = re.sub(r"(?<=\d)[\s-]*(bis|ter|qu[aá]ter|quinquies|sexies|septies|octies|novies|decies)\b", r" \1", s)
    parts = s.split()
    if trans and parts and (r := _roman(parts[0])) is not None and not parts[0].isdigit():
        parts[0] = str(r)
    return ("t:" if trans else "") + " ".join(parts)


async def _post(url: str, data: dict) -> dict:
    r = await _http.post(url, data=data)
    if r.status_code != 200:
        raise SourceError(_http.error("SINALEVI", "request failed", r.status_code), r.status_code)
    try:
        return r.json()
    except ValueError as e:
        raise SourceError("SINALEVI: unexpected non-JSON reply", r.status_code) from e


async def _version(id: str) -> str:
    d = await _post(FICHA, {"idFichaNorma": id, "version": -1})
    m = re.search(r"param2=(\d+)", str(d.get("direccion", "")))
    if not m:
        raise SourceError(f"SINALEVI: no version redirect for norm {id}: {str(d)[:200]}", 200)
    if m[1] == "0":
        raise NotFound(f"No SINALEVI norm with id {id}.")
    return m[1]


def _ficha(h: str) -> dict:
    t = _http.clean(_html.unescape(re.sub(r"<[^>]+>", " ", h)))
    head = re.search(r'estilo-headerCard">\s*(.*?)\s*</div>', h, re.S)
    head = _http.clean(_html.unescape(head[1])) if head else ""
    title = re.search(r'k-card-title pb-3"><b>(.*?)</b>', h, re.S)
    out = {"head": head, "title": _http.clean(_html.unescape(title[1])) if title else ""}
    m = re.match(r"(.*?):\s*([\w-]+)\s+del\s+(\d{2}/\d{2}/\d{4})", head)
    if m:
        out.update(type=m[1], number=m[2], date=_http.iso_date(m[3]))
    if m := re.search(r"Versión de la Norma:\s*(\d+ de \d+)\s*del\s*(\d{2}/\d{2}/\d{4})", t):
        out.update(version=m[1], as_of=_http.iso_date(m[2]))
    for k, lab in (("issuer", "Ente Emisor:"), ("in_force_from", "Fecha de vigencia desde:")):
        if m := re.search(re.escape(lab) + r"\s*(.*?)\s*(?:Fecha de vigencia|Versión de la Norma|$)", t):
            out[k] = _http.iso_date(m[1]) or m[1]
    return out


def _plain(line: str) -> str:
    return _http.clean(re.sub(r"[*_#]+", "", line))


def _split(h: str) -> list[tuple[str, str]]:
    """Full-text HTML -> [(label, markdown)], last item label '' (text after the last article)."""
    start = h.find("<html")
    body = h[start:] if start >= 0 else h
    body = re.sub(r"(?i)<!?\[(?:if [^\]]*|endif)\]>?", " ", body)  # Word list-marker leftovers: <![if !supportLists]>
    body = re.sub(r"(?i)<(/?)h[1-6]\b", r"<\1p", body)  # Word uses <h1> for ordinary article paragraphs
    out, pos = [], 0
    for m in _MARK.finditer(body):
        out.append((_label(m[1]), _http.html_to_md(body[pos:m.start()])))
        pos = m.end()
    tail = re.sub(r"(?is)<script\b.*?</script>", "", body[pos:])
    tail = _http.html_to_md(tail)
    if tail:
        out.append(("", tail))
    return out


async def _load(id: str) -> dict:
    id = _norm_id(id)
    if id in _cache:
        return _cache[id]
    ver = await _version(id)
    card = _ficha((await _post(FICHA, {"idFichaNorma": id, "version": ver})).get("html", ""))
    d = await _post(TEXT, {"idFichaNorma": id, "version": ver, "busqueda": ""})
    h = d.get("html")
    if not h:
        raise SourceError(f"SINALEVI: no text for norm {id}: {str(d)[:200]}", 200)
    parts = _split(h)
    title = card.get("title") or _http.clean(_html.unescape(
        (re.search(r'id="DatosNorma"[^>]*value="([^"]*)"', h) or [None, id])[1]))
    if card.get("number") and card.get("type") and card["number"] != "0":
        title = title if card["number"] in title else f"{card['type']} N° {card['number']}: {title}"
    law = {"id": id, "title": title, "card": card, "parts": parts, "url": _url(id)}
    return _http.lru_put(_cache, id, law, 6)


# The source lists newest first, so a base code is buried under its amendments: (record id, year) by name.
BASE_CODES = {"codigo penal": ("5027", 1970, "Ley 4573"), "codigo civil": ("15437", 1885, "Ley 30"),
              "codigo de trabajo": ("8045", 1943, "Ley 2"),
              "codigo procesal penal": ("41297", 1996, "Ley 7594")}


def _base(q: str):
    q = "".join(c for c in unicodedata.normalize("NFD", q.lower()) if not unicodedata.combining(c))
    return BASE_CODES.get(re.sub(r"\s+", " ", q).strip(" .,;"))


def _hit(r: dict) -> LawHit:
    num = str(r.get("NumeroNormativa") or "")
    sub = _http.clean(r.get("IdSubNumeroNormativa"))
    if sub and sub != "0":
        num += f"-{sub}"
    id = str(r.get("IdFichaNorma"))
    return LawHit(id=id, title=_http.clean(r.get("NombreNormativa")) or f"{r.get('NombreTipoNorma')} {num}",
                  type=_http.clean(r.get("NombreTipoNorma")), number=num,
                  date=_http.iso_date(r.get("FechaNormativa")), status=_http.clean(r.get("EstadoNorma")),
                  snippet=_http.clean(r.get("DescEnteEmisor")), url=_url(id))


async def _search_page(params: dict, n: int) -> list[dict]:
    r = await _http.get(SEARCH, params={**params, "cantidadResultados": PAGE, "pagina": n})
    if r.status_code != 200:
        raise SourceError(_http.error("SINALEVI", "search failed", r.status_code), r.status_code)
    try:
        data = json.loads(r.text)
    except ValueError as e:
        raise SourceError("SINALEVI: unexpected non-JSON search reply", r.status_code) from e
    if not isinstance(data, list):
        raise SourceError(f"SINALEVI: unexpected search reply {str(data)[:200]}", r.status_code)
    return data


class CostaRica(Jurisdiction):
    code = "cr"
    name = "Costa Rica"
    languages = ("es",)
    aliases = ("costa rica", "cri")
    sources = (
        Source(
            name="SINALEVI – Sistema Nacional de Legislación Vigente (Procuraduría General de la República, SCIJ)",
            url="https://sinalevi.go.cr/",
            covers=("legislation",),
            licence=("unknown: no licence or terms page; footer says '© Procuraduría de la República. "
                     "Todos los derechos reservados.' (2026-11-06)"),
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit=("unknown; 1 s spacing, no 429 seen in ~25 requests (2026-11-06); "
                        "no robots.txt (404) on sinalevi.go.cr or pgrweb.go.cr"),
            terms_url="https://sinalevi.go.cr/Escritorio/SCIJ",
        ),
    )
    legislation_filters = {
        "type": "norm type: L (Ley), D (Decreto Ejecutivo), C (Constitución), TI (tratado), R (Reglamento), "
                "CIR (Circular), ... or the Spanish name, e.g. 'Ley'",
        "year": "year of the norm, e.g. 1994",
        "in": "'record' (default: title, number) or 'text' (search the norm's text)",
    }
    min_interval = {"sinalevi.go.cr": 1.0}
    notes = ("Consolidated laws, decrees and treaties from SINALEVI (PGR), updated daily; search is "
             "newest-first. No case law: the Poder Judicial's Nexus PJ forbids robotic/AI database building.")
    gaps = (
        "Case law (all courts, incl. Sala Constitucional; Nexus PJ): terms ban databases built with 'herramientas robotizadas'",
        "Earlier versions of a norm: SINALEVI serves them (version parameter); only the latest is built",
        "Municipal regulations: not researched yet",
        "Tribunal Supremo de Elecciones case law: not researched yet",
        "La Gaceta (Diario Oficial): not researched yet",
    )
    samples = {
        "legislation_query": "7472",
        "law_id": "871",
        "provision": "1",
    }

    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        q = _http.clean(query)
        if not q:
            raise BadRequest("Give search words (title words or a law number, e.g. '7472').")
        tipo = 0
        if t := _http.clean(filters.get("type")):
            up = t.upper()
            hit = TYPES.get(up) or next((v for v in TYPES.values() if v[1].lower() == t.lower()), None)
            if not hit:
                raise BadRequest("type must be one of " + ", ".join(f"{k} ({v[1]})" for k, v in TYPES.items())
                                 + f"; got {t!r}.")
            tipo = hit[0]
        year = 0
        if y := _http.clean(filters.get("year")):
            if not re.fullmatch(r"1[89]\d\d|20\d\d", y):
                raise BadRequest(f"year must be four digits, e.g. 1994; got {y!r}.")
            year = int(y)
        where = _http.clean(filters.get("in") or "record").lower()
        if where not in ("record", "text"):
            raise BadRequest(f"in must be 'record' or 'text'; got {where!r}.")
        text_default = where == "text" and not year and not tipo
        if text_default:
            tipo = TYPES["L"][0]  # text hits are otherwise buried under regulations and municipal rules
        params = {"opcionSelected": 1, "textBuscar": q, "textAnnio": year,
                  "selectedBuscarEn": "T" if where == "text" else "F", "TipoNorma": tipo,
                  "TipoPronunciamiento": 0, "ClaseAsunto": 0}
        start = (page - 1) * limit
        first = start // PAGE + 1
        rows = await _search_page(params, first)
        total = (first - 1) * PAGE + len(rows) if len(rows) < PAGE else None
        if len(rows) == PAGE and start % PAGE + limit > PAGE:
            more = await _search_page(params, first + 1)
            rows += more
            if len(more) < PAGE:
                total = first * PAGE + len(more)
        items = [_hit(r) for r in rows[start % PAGE:start % PAGE + limit]]
        extra = ""
        if (b := _base(q)) and where == "record":
            extra = (f"The base code is {b[2]} of {b[1]}, record id {b[0]}: get_legislation_toc('cr', '{b[0]}'). "
                     "Other laws of that name are amendments or commencement decrees. ")
            if page == 1 and not year and tipo in (0, 8) and b[0] not in [i.id for i in items]:
                base = await _search_page({**params, "textAnnio": b[1], "TipoNorma": 8}, 1)
                if top := next((r for r in base if str(r.get("IdFichaNorma")) == b[0]), None):
                    items = [_hit(top)] + items[:max(limit - 1, 0)]
        elif where == "text":
            bases = {v[0] for v in BASE_CODES.values()}
            if any(i.id in bases for i in items):
                items.sort(key=lambda i: i.id not in bases)  # stable: the base codes first, rest newest first
                extra = "Base codes (Código Civil, de Trabajo, Penal, Procesal Penal) are listed first when they match. "
        if text_default:
            extra += ("Text search without a type looks in laws (type='L') only, because regulations and municipal "
                     "rules otherwise fill the newest-first list; for decrees, regulations or treaties pass "
                     "type='D', 'R' or 'TI'. ")
        return Results(items, total=total,
                       note=extra + ("Newest first, not ranked by relevance: a base code sits behind its later amendments "
                             "and circulars, so add filters type='L' and the year of the base law "
                             "(Código Civil is Ley 30 of 1885, Código de Trabajo Ley 2 of 1943, Código Penal "
                             "Ley 4573 of 1970, Código Procesal Penal Ley 7594 of 1996) or search the law number. Search matches the norm's record "
                             "(title, number) unless filters in='text', which is also newest-first. "
                             "The id is SINALEVI's record number."))

    async def get_legislation_toc(self, id):
        law = await _load(id)
        entries: list[TocEntry] = []
        for label, md in law["parts"]:
            if not label:
                continue
            lines = [_plain(ln) for ln in md.split("\n\n")]
            lines = [ln for ln in lines if ln]
            heads = []
            for ln in lines:
                if _ARTICLE.match(ln):
                    break
                if _HEADING.match(ln) and len(ln) < 80:
                    heads.append(ln)
            entries += [TocEntry(title=t, level=0) for t in heads]
            first = next((ln for ln in lines if _ARTICLE.match(ln)),
                         next((ln for ln in lines if not _HEADING.match(ln)), ""))
            name = f"Artículo {label}" if not label.startswith("Transitorio") else label
            title = first[:140] if _ARTICLE.match(first) else (f"{name} – {first[:120]}" if first else name)
            entries.append(TocEntry(title=title, level=1,
                                    provision=label))
        return Toc(id=law["id"], title=law["title"], url=law["url"], entries=entries,
                   note=_id_note(law["id"], law["title"]))

    async def get_legislation_provision(self, id, provision):
        law = await _load(id)
        want = _key(provision)
        if not want or want == "t:":
            raise BadRequest("Give an article label, e.g. '1', '16 bis', 'art. 5' or 'Transitorio 1'.")
        for label, md in law["parts"]:
            if label and _key(label) == want:
                name = f"Artículo {label}" if not label.startswith("Transitorio") else label
                return Provision(law_id=law["id"], law_title=law["title"], provision=label,
                                 text=f"### {name}\n\n{md}", url=law["url"],
                                 as_of=law["card"].get("as_of", ""))
        raise NotFound(f"No article {provision!r} in SINALEVI norm {law['id']} ({law['title']}). "
                       "See get_legislation_toc for the labels.")

    async def get_legislation_text(self, id):
        law = await _load(id)
        text = "\n\n".join(md for _, md in law["parts"] if md)
        if not text:
            raise SourceError(f"SINALEVI: empty text for norm {law['id']}", 200)
        card = law["card"]
        meta = {k: card[c] for k, c in (("Tipo", "type"), ("Número", "number"), ("Fecha", "date"),
                                         ("Ente emisor", "issuer"), ("Vigencia desde", "in_force_from"),
                                         ("Versión", "version")) if card.get(c)}
        return LawText(id=law["id"], title=law["title"], text=text, url=law["url"],
                       as_of=card.get("as_of", ""), metadata=meta)
