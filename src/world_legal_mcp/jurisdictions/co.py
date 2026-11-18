"""Colombia: Corte Constitucional judgments (sentencias C, T and SU since 1992) and
consolidated legislation from Función Pública's Gestor Normativo.

Gotchas this code encodes (verified 2026-11-05 from a UK IP):
  * Search: the Court publishes the metadata of every sentencia as an open dataset on
    datos.gov.co (Socrata id v2k4-2t8s, CC BY-SA 4.0, updated monthly). SoQL, no key:
    `$q` is a full-text match over the metadata columns (number, magistrate, process,
    chamber), NOT over the judgment text. There is no official full-text search that
    robots.txt allows: the Court's own buscador is an SPA over /API/, which robots.txt
    disallows.
  * The dataset id is the sentencia number as the Court writes it: "T-001/24",
    "C-155A/93", "SU-214/16". That is the decision id here.
  * Text: www.corteconstitucional.gov.co/relatoria/{yyyy}/{T-001-24}.htm (allowed in
    robots.txt). SU files drop the hyphen: SU214-16.htm. The pages are Word-made HTML in
    windows-1252, prefixed by a script and an .rtf link. An unknown file is NOT a 404:
    it is HTTP 200 with the site's Angular shell ("data-beasties-container").
  * The dataset can list a sentencia before its text is on the relatoria (e.g. recent
    2026 numbers): get_decision then says so.
  * Legislation: Función Pública's Gestor Normativo (DAFP, an official national body),
    checked 2026-11-06. Consolidated texts with amendment notes ("Modificado por...",
    "TEXTO ANTERIOR", struck-through inexequible parts) of the Constitution, laws, decrees
    and the codes the Gestor carries (penal, CPACA, CGP, comercio, recursos naturales...).
    It is a selection, not every Colombian norm: e.g. the Código Civil (Ley 84 de 1873) is
    not in it.
      - Needs the OS trust store (`truststore` in _http): the host serves an incomplete TLS
        chain, which macOS/Windows complete by fetching the intermediate; on Linux
        _http loads it from intermediates.pem. http:// gives 503.
      - robots.txt: "Disallow:" (empty) for every agent.
      - Terms ("Política de Privacidad y Condiciones de Uso", Limitaciones de acceso) forbid
        any manual or automatic process to capture or copy portal content without the
        Función Pública's written consent. So the source is needs_permission: off unless
        the operator sets WLM_PERMITTED=co.
      - Search: gestornormativo/gestion/funphp/funajax.php?t=ejecuta_busqueda_avanzada2
        (the GET the advanced-search page itself makes) with tipdoc/nrodoc/ano/palabras.
        It returns ALL hits in one HTML list ("Número de documentos encontrados: N"), no
        server paging; `pagina` is ignored. `palabras` matches the Gestor's own summary /
        keywords, not the full text, and finds little; type + number + year is reliable.
      - Text: gestornormativo/norma.php?i={id}; the id is the Gestor's record number. The
        page claims ISO-8859-1 in a meta tag but the body is UTF-8. The norm is in
        div.descripcion-contenido; per-article "Jurisprudencia Vigencia" cards are hidden
        cross-reference lists and are dropped. Article anchors (name="34") are missing for
        many articles, so articles are split on bold "ARTÍCULO N" paragraphs instead. The
        Constitution repeats "ARTÍCULO TRANSITORIO 1" (each Acto Legislativo restarts the
        count): repeats get " (2)", " (3)" labels.
      - Not used: Secretaría del Senado basedoc (every page: "Derechos de autor reservados -
        Prohibida su reproducción"); SUIN-Juriscol (Angular SPA, no public document
        endpoint); Régimen Legal de Bogotá (empty to a non-browser).
  * Other courts: Corte Suprema relatoría hosts (consultajurisprudencial / jurisprudencia
    .ramajudicial.gov.co) answer 403 "Bloqueo por WafPolicy..." to this client; Consejo de
    Estado SAMAI robots.txt disallows /*.aspx?* (its search and document pages).
"""
from __future__ import annotations

import re

from lxml import html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc, TocEntry

DATASET = "https://www.datos.gov.co/resource/v2k4-2t8s.json"
DATASET_PAGE = "https://www.datos.gov.co/Justicia-y-Derecho/Sentencias-proferidas-por-la-Corte-Constitucional/v2k4-2t8s"
RELATORIA = "https://www.corteconstitucional.gov.co/relatoria"
COURT = "Corte Constitucional"
TYPES = ("C", "T", "SU")
_ID = re.compile(r"^\s*(?:sentencia\s+)?(SU|C|T)\s*-?\s*(\d{1,4})\s*([A-Z]?)\s*"
                 r"(?:/|-|\s+de\s+)\s*(\d{2}|\d{4})\s*$", re.I)
_URL = re.compile(r"/relatoria/(\d{4})/(SU|C|T)-?(\d{1,4})([A-Z]?)-(\d{2})\.htm", re.I)
_cache: dict[str, Decision] = {}


def _norm_id(id: str) -> tuple[str, str, str]:
    """'T-001/24', 'T-001-24', 'Sentencia SU-214 de 2016', relatoria URL ->
    (canonical id 'SU-214/16', year '2016', file stem 'SU214-16')."""
    s = str(id or "").strip()
    m = _URL.search(s)
    if m:
        kind, num, suf, yy = m[2].upper(), m[3], m[4].upper(), m[5]
    else:
        m = _ID.match(s)
        if not m:
            raise BadRequest("Colombian Corte Constitucional ids are sentencia numbers like 'T-001/24', "
                             f"'C-355/06' or 'SU-214/16'; got {id!r}.")
        kind, num, suf, yy = m[1].upper(), m[2], m[3].upper(), m[4][-2:]
    year = ("19" if int(yy) >= 92 else "20") + yy
    num = num.zfill(3)
    canon = f"{kind}-{num}{suf}/{yy}"
    stem = f"{kind}{'' if kind == 'SU' else '-'}{num}{suf}-{yy}"
    return canon, year, stem


def _url(year: str, stem: str) -> str:
    return f"{RELATORIA}/{year}/{stem}.htm"


def _q(s: str) -> str:
    return "'" + str(s).replace("'", "''") + "'"


def _hit(row: dict) -> DecisionHit:
    sid = _http.clean(row.get("sentencia"))
    try:
        _, year, stem = _norm_id(sid)
        url = _url(year, stem)
    except BadRequest:
        url = DATASET_PAGE
    bits = [row.get("proceso"), row.get("sala"),
            f"M.P. {row['magistrado_a']}" if row.get("magistrado_a") else "",
            f"Exp. {row.get('expediente_tipo', '')}-{row['expediente_numero']}" if row.get("expediente_numero") else ""]
    return DecisionHit(
        id=sid, title=f"Sentencia {sid}", court=COURT,
        date=_http.iso_date(row.get("fecha_sentencia")),
        case_number=f"{row.get('expediente_tipo', '')}-{row['expediente_numero']}" if row.get("expediente_numero") else "",
        snippet=" · ".join(_http.clean(b) for b in bits if _http.clean(b)), url=url)


async def _soql(params: dict) -> list[dict]:
    r = await _http.get(DATASET, params=params)
    if r.status_code in (502, 503, 504):   # transient on datos.gov.co (503, health run 2026-11-10)
        r = await _http.get(DATASET, params=params)
    if r.status_code != 200:
        raise SourceError(_http.error("datos.gov.co", "dataset query failed", r.status_code), r.status_code)
    try:
        data = r.json()
    except ValueError as e:
        raise SourceError("datos.gov.co: unexpected non-JSON reply", r.status_code) from e
    if not isinstance(data, list):
        raise SourceError(f"datos.gov.co: unexpected reply {str(data)[:200]}", r.status_code)
    return data


# --- Legislation: Función Pública Gestor Normativo ---------------------------------------

GESTOR = "https://www.funcionpublica.gov.co/eva/gestornormativo"
GESTOR_SEARCH = f"{GESTOR}/gestion/funphp/funajax.php"
# tipodoc values of the Gestor's advanced-search form (consulta_avanzada.php, 2026-11-06)
DOC_TYPES = {
    "acto legislativo": "2", "acuerdo": "3", "auto": "1205", "circular": "6", "circular conjunta": "184",
    "circular externa": "825", "concepto": "7", "constitución política": "8", "decreto": "11",
    "decreto ley": "986", "directiva": "13", "estatutos": "905", "ley": "18", "reglamento": "989",
    "resolución": "29", "sentencia": "30",
}
_TYPE_RX = "|".join(sorted((re.escape(t).replace("ó", "[oó]") for t in DOC_TYPES), key=len, reverse=True))
_CITE = re.compile(rf"^\s*({_TYPE_RX})\s+(?:n[°ºo.]*\s*)?(\d+)\s+de\s+(\d{{4}})\s*$", re.I)
_HIT = re.compile(r'<a href="norma\.php\?i=(\d+)"[^>]*>\s*<h5[^>]*>(.*?)</h5>\s*(?:<p[^>]*>(.*?)</p>)?', re.S)
_ART = re.compile(r"^ART[ÍI]CULO\s+(TRANSITORIO\b\s*)?(\d+(?:-?[A-Z]|-\d+|\s(?-i:[A-Z])(?=\.))?\b|[ÚU]NICO\b)?\s*(BIS\b|TRANSITORIO\b)?",
                  re.I)
_HEAD = re.compile(r"^(T[ÍI]TULO|CAP[ÍI]TULO|LIBRO|PARTE|SECCI[ÓO]N)\b", re.I)
_laws: dict[str, dict] = {}


def _law_url(id: str) -> str:
    return f"{GESTOR}/norma.php?i={id}"


def _plain(md: str) -> str:
    return _http.clean(re.sub(r"[*_#]+", "", md))


def _type_code(t: str) -> str:
    key = _http.clean(t).lower().replace("constitucion", "constitución").replace("resolucion", "resolución")
    if key not in DOC_TYPES:
        raise BadRequest(f"type must be one of: {', '.join(DOC_TYPES)}; got {t!r}.")
    return DOC_TYPES[key]


async def _gestor_search(params: dict) -> tuple[list[LawHit], int | None]:
    r = await _http.get(GESTOR_SEARCH, params={"t": "ejecuta_busqueda_avanzada2", **params})
    if r.status_code != 200:
        raise SourceError(_http.error("Función Pública", "Gestor Normativo search failed", r.status_code),
                          r.status_code)
    h = r.content.decode("utf-8", errors="replace")
    m = re.search(r"documentos encontrados:\s*(\d+)", h)
    if not m:
        raise SourceError(f"Función Pública: unexpected search reply {_http.clean(h[:200])!r}", r.status_code)
    hits = []
    for i, title, desc in _HIT.findall(h):
        title = _plain(_http.html_to_md(title))
        cm = re.match(rf"({_TYPE_RX})\s+(\d+)\s+de\s+(\d{{4}})", title, re.I)
        hits.append(LawHit(id=i, title=title, type=cm[1] if cm else "", number=cm[2] if cm else "",
                           snippet=_plain(_http.html_to_md(desc or ""))[:400], url=_law_url(i)))
    return hits, int(m[1])


async def _law_id(id) -> str:
    """'41249', a norma.php?i= link, or a citation 'Ley 1437 de 2011' -> the Gestor's record number."""
    s = _http.clean(id)
    if m := (re.search(r"norma(?:_pdf)?\.php\?i=(\d+)", s) or re.fullmatch(r"(\d{1,9})", s)):
        return m[1]
    if m := _CITE.match(s):
        hits, _ = await _gestor_search({"tipdoc": _type_code(m[1]), "nrodoc": m[2], "ano": m[3]})
        want = f"{m[1]} {m[2]} de {m[3]}".lower()
        exact = [h for h in hits if h.title.lower().startswith(want)]
        if not exact:
            raise NotFound(f"Función Pública's Gestor Normativo has no {s!r} (it carries a selection of "
                           "Colombian norms, not all of them).")
        return exact[0].id
    raise BadRequest("Colombian law ids are Gestor Normativo record numbers, e.g. '4125' (Constitución "
                     "Política), '41249' (Ley 1437 de 2011), a funcionpublica.gov.co norma.php?i= link, or a "
                     f"citation like 'Ley 1437 de 2011'; got {id!r}.")


def _label_of(md: str) -> str | None:
    """Article label of a paragraph that opens an article, else None.
    '**ARTÍCULO 15A.**' -> '15A', '243-A', '319-1'; '**ARTÍCULO** **TRANSITORIO 1.**' -> 'Transitorio 1'."""
    if not md.startswith("**"):
        return None  # article headings are bold; plain "Artículo 5 de la Ley..." is running text
    m = _ART.match(re.sub(r"(\d)\s*[oº°]\.?(?=\W|$)", r"\1", _plain(md)))  # '2o.', '5º' ordinals
    if not m or not (m[1] or m[2] or m[3]):
        return None
    num = (m[2] or "").upper().replace(" ", "")
    num = "Único" if num in ("ÚNICO", "UNICO") else num
    trans = bool(m[1]) or (m[3] or "").upper() == "TRANSITORIO"
    label = num + (" bis" if (m[3] or "").upper() == "BIS" else "")
    return ("Transitorio " + label).strip() if trans else label


def _is_heading(md: str) -> bool:
    p = _plain(md)
    if not p or len(p) > 150 or not md.startswith("**") or p.startswith(("(", "Ver ", "NOTA")):
        return False
    letters = [c for c in p if c.isalpha()]
    return bool(_HEAD.match(p)) or (bool(letters) and sum(c.isupper() for c in letters) / len(letters) > 0.8)


def _key(label: str) -> str:
    s = _http.clean(label).lower().replace("º", "").replace("°", "").replace("unico", "único")
    s = re.sub(r"^(art[ií]culo|art\.?)\s*", "", s)
    trans = bool(re.search(r"\btransitorio\b", s))
    s = re.sub(r"\btransitorio\b", "", s)
    s = re.sub(r"[\s.:-]+", "", s)
    return ("t:" if trans else "") + s


async def _load_law(id) -> dict:
    lid = await _law_id(id)
    if lid in _laws:
        return _laws[lid]
    url = _law_url(lid)
    r = await _http.get(url)
    if r.status_code != 200:
        raise SourceError(_http.error("Función Pública", "Gestor Normativo request failed", r.status_code),
                          r.status_code)
    h = r.content.decode("utf-8", errors="replace")  # meta says ISO-8859-1; the bytes are UTF-8
    doc = lhtml.fromstring(h)
    body = doc.xpath('//div[contains(concat(" ", @class, " "), " descripcion-contenido ")]')
    if not body:
        raise NotFound(f"No norm {lid} in Función Pública's Gestor Normativo ({url}).")
    for el in body[0].xpath('.//button | .//div[contains(concat(" ", @class, " "), " card ")]'):
        el.getparent().remove(el)  # hidden "Jurisprudencia Vigencia" cross-reference cards
    paras = _http.html_paragraphs(lhtml.tostring(body[0], encoding="unicode"))
    if sum(len(p) for p in paras) < 200:
        raise NotFound(f"Gestor Normativo record {lid} has no text ({url}).")
    title = _http.clean(doc.findtext(".//title") or "")
    title = re.sub(r"\s*-\s*Gestor Normativo.*$", "", title) or f"Gestor Normativo {lid}"
    page_text = _http.clean(doc.text_content())
    meta = {}
    for k, rx in (("Fecha de expedición", r"Fecha de Expedici[oó]n:\s*([^:]{0,40}?\d{4})"),
                  ("Entrada en vigencia", r"Fecha de Entrada en Vigencia:\s*([^:]{0,40}?\d{4})"),
                  ("Medio de publicación", r"Medio de Publicaci[oó]n:\s*(.{0,120}?\d{4})")):
        if m := re.search(rx, page_text):
            meta[k] = _http.clean(m[1])
    # Split into articles: [(label, paragraphs)], label "" for text before the first article
    parts: list[tuple[str, list[str]]] = [("", [])]
    seen: dict[str, int] = {}
    for p in paras:
        label = _label_of(p)
        if label is None:
            parts[-1][1].append(p)
            continue
        if label:
            n = seen[_key(label)] = seen.get(_key(label), 0) + 1
            label = label if n == 1 else f"{label} ({n})"
        parts.append((label, [p]))
    law = {"id": lid, "title": title, "url": url, "paras": paras, "parts": parts, "meta": meta}
    return _http.lru_put(_laws, lid, law, 4)


class Colombia(Jurisdiction):
    code = "co"
    name = "Colombia"
    languages = ("es",)
    aliases = ("colombia", "col")
    sources = (
        Source(
            name="Corte Constitucional – relatoría (sentencias, full text)",
            url="https://www.corteconstitucional.gov.co/relatoria/",
            covers=("caselaw",),
            licence="unknown: no terms or licence page found on corteconstitucional.gov.co (2026-11-05)",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit=("unknown; 1 s spacing, no 429 seen in ~20 requests (2026-11-05); robots.txt "
                        "explicitly allows /relatoria/, disallows /API/ and /sentencias/"),
            terms_url="https://www.corteconstitucional.gov.co/robots.txt",
        ),
        Source(
            name="datos.gov.co – 'Sentencias proferidas por la Corte Constitucional' (metadata, search)",
            url=DATASET_PAGE,
            covers=("caselaw",),
            licence="Creative Commons Attribution-ShareAlike 4.0 (dataset metadata); attribution: Corte Constitucional",
            commercial_use=True,
            ai_use=None,
            auth="none",
            rate_limit=("robots.txt Crawl-delay: 1; Socrata API without app token is throttled per IP "
                        "(undocumented amount); no 429 seen in ~15 requests (2026-11-05)"),
            terms_url="https://creativecommons.org/licenses/by-sa/4.0/",
        ),
        Source(
            name="Función Pública – Gestor Normativo (consolidated legislation)",
            url=f"{GESTOR}/consulta_avanzada.php",
            covers=("legislation",),
            licence=("no open licence: terms say the content 'podrá ser utilizada teniendo en cuenta las normas "
                     "que protegen el derecho a la propiedad intelectual' and forbid automated capture/copying "
                     "without written consent (checked 2026-11-06)"),
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit=("unknown; 1 s spacing, no 429 seen in ~25 requests (2026-11-06); robots.txt "
                        "'Disallow:' (allows all). TLS chain incomplete: the missing intermediate is "
                        "bundled (intermediates.pem) for Linux"),
            terms_url="https://www.funcionpublica.gov.co/politica-de-privacidad-y-condiciones-de-uso",
            needs_permission=True,
            warning=("Función Pública's terms forbid using 'ningún mecanismo o hardware u otro proceso manual o "
                     "automático para capturar, monitorizar como propio o copiar' the portal or its content "
                     "without its written consent. No consent held. The Gestor also says it is informative "
                     "only and does not vouch for a norm's current validity (vigencia)."),
        ),
    )
    legislation_filters = {
        "type": "norm type: " + ", ".join(DOC_TYPES),
        "number": "norm number, e.g. 1437",
        "year": "year of the norm, e.g. 2011",
    }
    caselaw_filters = {
        "type": "sentencia type: C (constitutionality), T (tutela) or SU (unification)",
        "year": "year of the judgment, e.g. 2024",
        "magistrate": "magistrado ponente name or part of it, e.g. 'Pardo'",
        "date_from": "earliest judgment date, YYYY-MM-DD",
        "date_to": "latest judgment date, YYYY-MM-DD",
    }
    min_interval = {"www.datos.gov.co": 1.0, "www.corteconstitucional.gov.co": 1.0,
                    "www.funcionpublica.gov.co": 1.0}
    notes = ("Corte Constitucional sentencias (C, T, SU) since 1992, full text. Search is NOT by "
             "subject or full text: it runs only over the Court's open metadata (number, magistrate, "
             "process), so you need the sentencia number. Legislation: Función "
             "Pública's Gestor Normativo, consolidated texts with amendment notes (a selection of norms, "
             "not all; no Código Civil); its terms need written consent for automated use (WLM_PERMITTED=co).")
    gaps = (
        "Consolidated legislation (Gestor Normativo): terms forbid automated 'capturar ... o copiar'; off unless WLM_PERMITTED=co",
        "Corte Suprema de Justicia decisions: relatoría hosts answer 403 'Bloqueo por WafPolicy' to our client",
        "Consejo de Estado decisions: SAMAI robots.txt disallows its search and document pages (/*.aspx?*)",
        "Norms outside the Gestor (e.g. Código Civil): Senado basedoc says 'Prohibida su reproducción'; SUIN has no endpoint",
        "Full-text search of Constitutional Court judgments: the Court's buscador API (/API/) is disallowed by robots.txt",
    )
    samples = {
        "caselaw_query": "Pardo Schlesinger",
        "decision_id": "T-001/24",
        "legislation_query": "Ley 1437 de 2011",
        "law_id": "4125",
        "provision": "86",
    }

    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        where: list[str] = []
        q = _http.clean(query)
        if q and _ID.match(q):
            where.append(f"sentencia = {_q(_norm_id(q)[0])}")
            q = ""
        if t := _http.clean(filters.get("type")).upper():
            if t not in TYPES:
                raise BadRequest(f"type must be one of C, T, SU; got {t!r}.")
            where.append(f"sentencia_tipo = {_q(t)}")
        if y := _http.clean(filters.get("year")):
            if not re.fullmatch(r"(19|20)\d\d", y):
                raise BadRequest(f"year must be four digits, e.g. 2024; got {y!r}.")
            where.append(f"date_extract_y(fecha_sentencia) = {int(y)}")
        if mag := _http.clean(filters.get("magistrate")):
            where.append(f"upper(magistrado_a) like {_q('%' + mag.upper() + '%')}")
        for key, op in (("date_from", ">="), ("date_to", "<=")):
            if v := _http.clean(filters.get(key)):
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
                    raise BadRequest(f"{key} must be YYYY-MM-DD; got {v!r}.")
                where.append(f"fecha_sentencia {op} '{v}T00:00:00'")
        if not q and not where:
            raise BadRequest("Give search words (a sentencia number, magistrate, process) or a filter.")
        base = {}
        if q:
            base["$q"] = q
        if where:
            base["$where"] = " AND ".join(where)
        rows = await _soql({**base, "$order": "fecha_sentencia DESC, sentencia DESC",
                            "$limit": limit, "$offset": (page - 1) * limit})
        count = await _soql({**base, "$select": "count(*)"})
        try:
            total = int(count[0]["count"])
        except (IndexError, KeyError, ValueError, TypeError):
            total = None
        return Results([_hit(r) for r in rows], total=total,
                       note=("NOT a subject or full-text search: only the Court's metadata (sentencia number, "
                             "magistrate, process, chamber) is searchable, so topic words such as 'aborto' or "
                             "'derecho a la salud' find nothing; the source offers no subject search. Look up a "
                             "judgment by its number (e.g. C-355/06, T-760/08) or filter by type, year, "
                             "magistrate or dates; dataset updated monthly."))

    async def get_decision(self, id):
        canon, year, stem = _norm_id(id)
        if canon in _cache:
            return _cache[canon]
        rows = await _soql({"$where": f"sentencia = {_q(canon)}", "$limit": 1})
        row = rows[0] if rows else {}
        stems = [stem] + ([stem.replace("SU", "SU-", 1)] if stem.startswith("SU") else [])
        html = url = ""
        for s in stems:
            url = _url(year, s)
            r = await _http.get(url)
            if r.status_code == 404:
                continue
            if r.status_code != 200:
                raise SourceError(_http.error("Corte Constitucional", "relatoría request failed", r.status_code),
                                  r.status_code)
            m = re.search(rb'charset\s*=\s*["\']?([\w-]+)', r.content[:3000], re.I)
            html = r.content.decode(m[1].decode() if m else "windows-1252", errors="replace")
            if "data-beasties-container" in html[:2000]:  # the site's SPA shell = soft 404
                html = ""
                continue
            break
        if not html:
            if row:
                raise NotFound(f"Sentencia {canon} is listed in the Court's dataset but its text is not "
                               f"(yet) on the relatoría ({_url(year, stem)}).")
            raise NotFound(f"No Corte Constitucional sentencia {canon}.")
        text = _http.html_to_md(html)
        text = re.sub(r"^\s*" + re.escape(stem) + r"\s*\n+", "", text)  # the .rtf link label
        if len(text) < 200:
            raise SourceError(f"Corte Constitucional: unexpectedly short page for {canon}", 200)
        meta = {k: _http.clean(row.get(f)) for k, f in (
            ("Proceso", "proceso"), ("Sala", "sala"), ("Magistrado(a) ponente", "magistrado_a"),
            ("Salvamento de voto", "sv_spv"), ("Aclaración de voto", "av_apv")) if _http.clean(row.get(f))}
        hit = _hit(row) if row else None
        d = Decision(id=canon, title=f"Sentencia {canon}", text=text, url=url, court=COURT,
                     date=hit.date if hit else "", case_number=hit.case_number if hit else "",
                     metadata=meta)
        return _http.lru_put(_cache, canon, d, 8)

    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        params: dict[str, str] = {}
        q = _http.clean(query)
        if m := _CITE.match(q):
            params.update(tipdoc=_type_code(m[1]), nrodoc=m[2], ano=m[3])
            q = ""
        if t := _http.clean(filters.get("type")):
            params["tipdoc"] = _type_code(t)
        if n := _http.clean(filters.get("number")):
            if not n.isdigit():
                raise BadRequest(f"number must be digits, e.g. 1437; got {n!r}.")
            params["nrodoc"] = n
        if y := _http.clean(filters.get("year")):
            if not re.fullmatch(r"(18|19|20)\d\d", y):
                raise BadRequest(f"year must be four digits, e.g. 2011; got {y!r}.")
            params["ano"] = y
        if q:
            params["palabras"] = q
        if not params:
            raise BadRequest("Give search words, a citation like 'Ley 1437 de 2011', or a filter.")
        hits, total = await _gestor_search(params)
        start = (page - 1) * limit
        return Results(hits[start:start + limit], total=total,
                       note=("Función Pública's Gestor Normativo: a selection of norms, not all. Words match "
                             "its summaries, not the full text; a citation ('Ley 1437 de 2011') or type + "
                             "number + year filters are reliable."))

    async def get_legislation_toc(self, id):
        law = await _load_law(id)
        entries: list[TocEntry] = []
        pending: list[str] = []  # headings sit at the end of the previous article's paragraphs
        for label, paras in law["parts"]:
            entries += [TocEntry(title=_plain(h), level=0) for h in pending]
            pending = []
            body = list(paras)
            while body and _is_heading(body[-1]):
                pending.insert(0, body.pop())
            if not label:
                continue
            first = _plain(body[0]) if body else label
            entries.append(TocEntry(title=first[:140], level=1, provision=label))
        return Toc(id=law["id"], title=law["title"], url=law["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        law = await _load_law(id)
        want = _key(provision)
        if not want or want == "t:":
            raise BadRequest("Give an article label, e.g. '86', '15A', 'art. 5' or 'Transitorio 1'.")
        for label, paras in law["parts"]:
            if label and _key(label) == want:
                body = list(paras)
                while len(body) > 1 and _is_heading(body[-1]):
                    body.pop()  # the next article's TÍTULO/CAPÍTULO headings
                return Provision(law_id=law["id"], law_title=law["title"], provision=label,
                                 text="\n\n".join(body), url=law["url"] + (f"#{label}" if label.isdigit() else ""))
        raise NotFound(f"No article {provision!r} in Gestor Normativo norm {law['id']} ({law['title']}). "
                       "See get_legislation_toc for the labels.")

    async def get_legislation_text(self, id):
        law = await _load_law(id)
        return LawText(id=law["id"], title=law["title"], text="\n\n".join(law["paras"]), url=law["url"],
                       metadata=law["meta"])
