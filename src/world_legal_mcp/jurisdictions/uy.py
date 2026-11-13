"""Uruguay: consolidated legislation from IMPO (Dirección Nacional de Impresiones y
Publicaciones Oficiales) and case law from the Poder Judicial's Base de Jurisprudencia
Nacional (BJN Pública).

Gotchas this code encodes (verified 2026-11-05 from a UK IP):
  * IMPO: append `?json=true` to any public norm or article URL
    (www.impo.com.uy/bases/{base}/{num}-{year}[/{article}]). The reply is ISO-8859-1
    and has raw CR/LF inside strings (json.loads(strict=False)). An unknown id is
    *not* a 404: it is HTTP 200 with an HTML page "Acceso no válido ... no posee ningún
    servicio vigente" (the same page IMPO shows for subscription-only content).
  * IMPO robots.txt asks Crawl-Delay: 10 and disallows /cgi-bin/, which is where IMPO's
    own search engine lives. So there is no keyword search: search_legislation only
    resolves code names (a fixed, verified list) and "ley N de YYYY" style references.
  * A whole code is one big JSON (Código Civil ~1.7 MB, ~2 min to download from the UK);
    a single article is ~2 KB, so provisions are fetched per article unless the whole
    norm is already cached.
  * In the whole-norm JSON, `titulosArticulo` (the headings above an article) only
    appears when the headings change, as HTML with <br> between levels. Article text is
    hard-wrapped; a paragraph starts with an indented line. "(*)" marks a note.
  * Repealed article ranges are one entry: "Artículo 131-144", url key "131_144".
  * BJN (bjn.poderjudicial.gub.uy, no robots.txt) is a JBoss Seam/RichFaces app: every
    search is a stateful AJAX POST in a server session, and a decision opens only by
    "clicking" its row, then GET hojaInsumo2.seam?cid=N. There is no permalink and no
    public decision id, so a decision id here is the source's own fields
    "<número> | <sede> | <fecha ISO>" (número + sede alone is not unique: a court can
    issue an interlocutoria and a definitiva with the same number). get_decision re-finds
    it through the "número de sentencia" field of the selective search. Form field names
    (j_idNN) are read from the page each time, not hard-coded.
  * BJN paging is next-page clicks only; page sizes are 10/20/50/100/200.
"""
from __future__ import annotations

import asyncio
import json
import re
from datetime import date
import unicodedata

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

IMPO = "https://www.impo.com.uy"
BJN = "https://bjn.poderjudicial.gub.uy/BJNPUBLICA"
SELECTIVA = f"{BJN}/busquedaSelectiva.seam"

# Codes and the Constitution as IMPO files them (each path verified 2026-11-05).
CODES = (
    ("constitucion/1967-1967", "Constitución de la República", ("constitucion", "constitucion de la republica")),
    ("codigo-civil/16603-1994", "Código Civil", ("codigo civil", "cc")),
    ("codigo-penal/9155-1933", "Código Penal", ("codigo penal", "cp")),
    ("codigo-comercio/817-1865", "Código de Comercio", ("codigo de comercio", "codigo comercio")),
    ("codigo-general-proceso/15982-1988", "Código General del Proceso",
     ("codigo general del proceso", "cgp")),
    ("codigo-proceso-penal-2017/19293-2014", "Código del Proceso Penal (2017)",
     ("codigo del proceso penal", "codigo proceso penal", "cpp")),
    ("codigo-ninez-adolescencia/17823-2004", "Código de la Niñez y la Adolescencia",
     ("codigo de la ninez y la adolescencia", "codigo de la ninez", "cna")),
    ("codigo-tributario/14306-1974", "Código Tributario", ("codigo tributario",)),
    ("codigo-aduanero/19276-2014", "Código Aduanero", ("codigo aduanero",)),
    ("codigo-rural/10024-1941", "Código Rural", ("codigo rural",)),
    ("leyes/18331-2008", "Ley Nº 18331 – Protección de Datos Personales",
     ("proteccion de datos personales", "ley de proteccion de datos personales", "habeas data")),
)
_TYPES = {"ley": "leyes", "leyes": "leyes", "decreto": "decretos", "decretos": "decretos",
          "decreto ley": "decretos-ley", "decreto-ley": "decretos-ley", "decretos-ley": "decretos-ley"}
_ID_RE = re.compile(r"^([a-z0-9-]+)/(\d+)-(\d{4})$")

_laws: dict[str, dict] = {}
_bjn_lock = asyncio.Lock()


def _fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", re.sub(r"[^\w/-]+", " ", s)).strip()


def _tags(s: str) -> str:
    return _http.clean(re.sub(r"<[^>]+>", " ", s or ""))


# --------------------------------------------------------------------------- #
# IMPO
# --------------------------------------------------------------------------- #
def _law_id(id: str) -> str:
    """'codigo-civil/16603-1994', an IMPO URL, 'ley 19889-2020', '19.889/2020' -> base/num-year."""
    s = str(id or "").strip()
    m = re.search(r"impo\.com\.uy/bases/([a-z0-9-]+)/(\d+)-(\d{4})", s, re.I)
    if m:
        return f"{m[1].lower()}/{m[2]}-{m[3]}"
    s2 = s.lower().strip("/")
    s2 = re.sub(r"^bases/", "", s2)
    if _ID_RE.match(s2):
        return s2
    f = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    f = re.sub(r"(?<=\d)\.(?=\d)", "", f)                 # 19.889 -> 19889
    f = re.sub(r"\b(n|no|nro|numero)\b\.?", " ", f)       # Nº / nro.
    f = re.sub(r"\s+", " ", f.replace(",", " ")).strip()
    m = re.fullmatch(r"(?:(decretos?[- ]ley|decretos?|ley(?:es)?)\s*)?(\d+)\s*(?:-|/|\bde\b|\bdel\b|\s)\s*(\d{4})", f)
    if m:
        kind = (m[1] or "ley").replace(" ", "-")
        base = "decretos-ley" if "ley" in kind and "decreto" in kind else _TYPES[kind]
        return f"{base}/{m[2]}-{m[3]}"
    raise BadRequest("IMPO ids look like 'leyes/19889-2020', 'decretos/122-2021' or "
                     f"'codigo-civil/16603-1994' (path after impo.com.uy/bases/); got {id!r}.")


def _url(lid: str, art: str = "") -> str:
    return f"{IMPO}/bases/{lid}" + (f"/{art}" if art else "")


def _decode(r) -> dict:
    ctype = r.headers.get("content-type", "")
    body = r.content.decode("latin-1")
    if "json" not in ctype and not body.lstrip().startswith("{"):
        if "Acceso no v" in body:
            return {}
        raise SourceError("IMPO: unexpected non-JSON reply", r.status_code)
    try:
        return json.loads(body, strict=False)
    except ValueError as e:
        raise SourceError("IMPO: unreadable JSON", r.status_code) from e


async def _impo_json(lid: str, art: str = "") -> dict:
    url = _url(lid, art)
    try:
        r = await _http.get(url, params={"json": "true"})
    except Exception as e:
        raise SourceError(f"IMPO: {e}", "network") from e
    if r.status_code == 404:
        raise NotFound(f"IMPO: no norm {lid}" + (f" article {art}" if art else ""))
    if r.status_code != 200:
        raise SourceError("IMPO request failed", r.status_code)
    d = _decode(r)
    if not d:
        raise NotFound(f"IMPO: no public document at {url} (IMPO answers 'Acceso no válido' for "
                       "unknown ids and for subscription-only content).")
    return d


def _title(d: dict) -> str:
    kind = _http.clean(d.get("tipoNorma"))
    num = _http.clean(d.get("nroNorma"))
    name = _http.clean(d.get("nombreNorma"))
    head = kind if kind.lower().startswith(("código", "codigo", "constituci")) or not num else f"{kind} Nº {num}"
    if kind.isupper():
        head = kind.title()
    return f"{head} – {name}" if name else head


def _paras(raw: str) -> list[str]:
    """IMPO hard-wrapped text (may hold <i>/<b>) -> markdown paragraphs."""
    out: list[str] = []
    new = True
    for line in (raw or "").replace("\r", "").replace("\xa0", " ").split("\n"):
        if not line.strip():
            new = True
            continue
        if new or line[:1].isspace():
            out.append(line.strip())
        else:
            out[-1] += " " + line.strip()
        new = False
    html = "".join(f"<p>{p}</p>" for p in out)
    return _http.html_paragraphs(html)


def _notes(raw: str) -> str:
    t = _http.html_to_md(raw or "")
    return re.sub(r"\s*\n\s*", " ", t).strip()


def _headings(raw: str) -> list[str]:
    s = re.sub(r"(?is)<i>.*?</i>", " ", raw or "")
    parts = [_tags(p) for p in re.split(r"(?i)<br\s*/?>", s)]
    return [p for p in parts if p and p != "(*)"]


def _key(label: str) -> str:
    """'Artículo 1319', 'art. 1319', '1319' -> '1319'; '131-144' / '131_144' -> '131_144'."""
    s = _fold(label)
    s = re.sub(r"^(articulos?|arts?)\b\s*", "", s)
    s = re.sub(r"\s*[-_]\s*", "_", s)
    return re.sub(r"\s+", " ", s).strip()


def _art_key(a: dict) -> str:
    u = str(a.get("urlArticulo") or "")
    return u.rstrip("/").rsplit("/", 1)[-1] if u else (
        a.get("nroArticulo", "") + (f"_{a['secArticulo']}" if a.get("secArticulo") else ""))


def _parse(lid: str, d: dict) -> dict:
    arts = d.get("articulos") or []
    lookup: dict[str, dict] = {}
    for a in arts:
        lookup.setdefault(_key(_art_key(a)), a)
        lookup.setdefault(_key(a.get("tituloArticulo", "")), a)
    return {"id": lid, "title": _title(d), "data": d, "arts": arts, "lookup": lookup,
            "url": _url(lid)}


def _label(a: dict) -> str:
    return _http.clean(a.get("tituloArticulo") or a.get("nombreArticulo")) or f"Artículo {_art_key(a)}"


def _art_md(a: dict, level: int = 2) -> list[str]:
    out = [f"{'#' * level} {_label(a)}"] + _paras(a.get("textoArticulo", ""))
    notes = _notes(a.get("notasArticulo", ""))
    if notes:
        out.append(f"> Notas (IMPO): {notes}")
    return out


class Uruguay(Jurisdiction):
    code = "uy"
    name = "Uruguay"
    languages = ("es",)
    aliases = ("uruguay", "ury")
    sources = (
        Source(
            name="IMPO – Banco de Datos de normativa (Dirección Nacional de Impresiones y Publicaciones Oficiales)",
            url="https://www.impo.com.uy/datos-abiertos/",
            covers=("legislation",),
            licence=("Licencia de Datos Abiertos – Uruguay v0.1 for the ?json=true open data (IMPO Datos "
                     "Abiertos page, since July 2018: commercial and non-commercial use, attribution to "
                     "IMPO + licence + dataset required); but IMPO's 'Condiciones de Uso del Banco de "
                     "Datos' still say use is personal and forbid copying, passing to third parties and "
                     "commercialisation"),
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit=("robots.txt Crawl-Delay: 10 (honoured: 10 s spacing); no 429 seen in ~15 requests "
                        "(2026-11-05). Whole codes download slowly (~15 KB/s)"),
            terms_url="https://www.impo.com.uy/politica-de-privacidad-y-seguridad/",
            warning=("IMPO licenses its JSON as open data (Licencia de Datos Abiertos – Uruguay, attribution "
                     "required), but its Banco de Datos terms forbid copying, redistribution and commercial "
                     "use; get IMPO's explicit confirmation before redistributing or using texts commercially."),
        ),
        Source(
            name="Base de Jurisprudencia Nacional Pública (BJN), Poder Judicial",
            url="https://bjn.poderjudicial.gub.uy/BJNPUBLICA/busquedaSelectiva.seam",
            covers=("caselaw",),
            licence="unknown; no terms or licence page found for BJN (free access without login per its user manual)",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit=("unknown; 1 s spacing, no 429 seen in ~15 requests (2026-11-05); "
                        "no robots.txt on bjn.poderjudicial.gub.uy (404)"),
            terms_url="",
        ),
    )
    caselaw_filters = {
        "date_from": "decision date from, YYYY-MM-DD",
        "date_to": "decision date to, YYYY-MM-DD",
        "number": "sentence number as BJN writes it, e.g. '207/2020' or 'SEF-0006-000036/2016'",
        "sort": "'relevance' (default), 'date_desc' or 'date_asc'",
    }
    min_interval = {"www.impo.com.uy": 10.0, "bjn.poderjudicial.gub.uy": 1.0}
    notes = ("Legislation: IMPO consolidated texts (laws, decrees, codes, Constitution); IMPO's search is "
             "robots-disallowed, so look up by code name or 'ley N de YYYY'. Case law: BJN (all courts), "
             "ids are 'número | sede | fecha'.")
    gaps = (
        ("Legislation keyword search: IMPO's search under /cgi-bin/ is disallowed by robots.txt "
         "(code name or law number only)"),
        ("IMPO subscription-only content: answers 'Acceso no válido' (paid; which texts, "
         "unverified)"),
        "Newest court decisions: the BJN index lags ~2 months",
        "Parliament (parlamento.gub.uy): CloudFront 403 to our client",
        "Departmental (regional) decrees: not researched yet",
    )
    samples = {
        "caselaw_query": "daño moral",
        "decision_id": "207/2020 | Tribunal Apelaciones Civil 1ºTº | 2020-11-11",
        "legislation_query": "código civil",
        "law_id": "codigo-civil/16603-1994",
        "provision": "Artículo 1319",
    }

    # ----------------------------------------------------------------- legislation
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        q = (query or "").strip()
        if not q:
            raise BadRequest("Give a code name ('código civil') or a law reference ('ley 19889 de 2020').")
        note = ("IMPO's own search is under /cgi-bin/, which its robots.txt disallows, so a search by law "
                "title or topic (e.g. 'protección de datos personales') is NOT supported: only the main codes "
                "and the Constitution by name, and references with number AND year like 'ley 18331 de 2008' / "
                "'decretos/122-2021'.")
        fq = _fold(q)
        hits: list[LawHit] = []
        bare = re.fullmatch(r"(?:ley\s*)?(?:n[º°o.]*\s*)?(\d{3,7})", _fold(re.sub(r"(?<=\d)\.(?=\d)", "", q)))
        for lid, title, names in CODES:
            if bare and lid.startswith("leyes/") and lid.split("/")[1].split("-")[0] == bare[1]:
                hits.append(LawHit(id=lid, title=title, type="Ley", number=bare[1], url=_url(lid)))
            elif any(fq == n or fq.startswith(n + " ") or n in fq for n in names if len(n) > 3) or fq in names:
                num = lid.split("/")[1].split("-")[0]
                hits.append(LawHit(id=lid, title=title, type=title.split(" ")[0], number=num, url=_url(lid)))
        if not hits:
            try:
                lid = _law_id(q)
            except BadRequest:
                lid = ""
            if lid:
                try:
                    d = await _impo_json(lid)
                except NotFound:
                    d = {}
                if d:
                    _http.lru_put(_laws, lid, _parse(lid, d), 4)
                    hits.append(LawHit(id=lid, title=_title(d), type=_http.clean(d.get("tipoNorma")),
                                       number=_http.clean(d.get("nroNorma")),
                                       date=_http.iso_date(d.get("fechaPromulgacion"))
                                       or _http.iso_date(d.get("fechaPublicacion")),
                                       status=_http.clean(d.get("leyenda")), url=_url(lid)))
            elif re.fullmatch(r"(?:ley\s*)?(?:n[º°o.]*\s*)?[\d.]{3,7}", fq):
                note = ("IMPO needs the year with the number: try 'ley 19889 de 2020' or 'leyes/19889-2020'. "
                        + note)
        start = (max(1, int(page)) - 1) * int(limit)
        return Results(items=hits[start:start + int(limit)], total=len(hits), note=note)

    async def _law(self, id) -> dict:
        lid = _law_id(id)
        if lid in _laws and _laws[lid]["arts"]:
            return _laws[lid]
        return _http.lru_put(_laws, lid, _parse(lid, await _impo_json(lid)), 4)

    async def get_legislation_toc(self, id):
        law = await self._law(id)
        entries: list[TocEntry] = []
        prev: list[str] = []
        for a in law["arts"]:
            heads = _headings(a.get("titulosArticulo", ""))
            if heads and heads != prev:
                same = 0
                while same < min(len(heads), len(prev)) and heads[same] == prev[same]:
                    same += 1
                entries += [TocEntry(title=h, level=0) for h in heads[same:]]
                prev = heads
            lab = _label(a)
            first = _paras(a.get("textoArticulo", ""))
            m = re.match(r"^\(([^)]{2,120})\)\.?-?", first[0]) if first else None
            entries.append(TocEntry(title=lab + (f" – {m[1]}" if m else ""), level=1, provision=lab))
        return Toc(id=law["id"], title=law["title"], url=law["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        lid = _law_id(id)
        key = _key(provision)
        if not re.fullmatch(r"\d+(_\d*)?( bis| ter)?", key):
            raise BadRequest(f"IMPO provisions are article numbers, e.g. 'Artículo 1319', '1319' or '131-144'; "
                             f"got {provision!r}.")
        law = _laws.get(lid)
        if law and law["arts"]:
            a = law["lookup"].get(key)
            if a is None:
                raise NotFound(f"IMPO {lid}: no article {provision!r}. Use labels from get_legislation_toc.")
            title, art = law["title"], a
        else:
            d = await _impo_json(lid, key.replace(" ", "-"))
            if not _paras(d.get("textoArticulo", "")):
                raise NotFound(f"IMPO {lid}: article {provision!r} has no text in the source.")
            got = re.search(r"\d+(?:\s*(?:bis|ter))?", _fold(d.get("nombreArticulo") or ""))
            if got and re.sub(r"\s+", " ", got.group()) != key.split("_")[0]:
                raise NotFound(f"IMPO {lid}: no article {provision!r} (the source answered "
                               f"{_http.clean(d.get('nombreArticulo'))!r}).")
            title = _title(d)
            art = {"tituloArticulo": _http.clean(d.get("nombreArticulo")) or f"Artículo {key}",
                   "textoArticulo": d.get("textoArticulo", ""), "notasArticulo": d.get("notasArticulo", ""),
                   "urlArticulo": f"/bases/{lid}/{key}"}
            path = _http.clean(d.get("tituloArticulo"))
            if path:
                art["_path"] = path
        lines = _art_md(art)
        if art.get("_path"):
            lines.insert(1, f"*{art['_path']}*")
        return Provision(law_id=lid, law_title=title, provision=_label(art), text="\n\n".join(lines),
                         url=_url(lid, _art_key(art)), as_of="")

    async def get_legislation_text(self, id):
        law = await self._law(id)
        d = law["data"]
        out: list[str] = []
        vistos = _paras(d.get("vistos", ""))
        out += vistos
        prev: list[str] = []
        for a in law["arts"]:
            heads = _headings(a.get("titulosArticulo", ""))
            if heads and heads != prev:
                same = 0
                while same < min(len(heads), len(prev)) and heads[same] == prev[same]:
                    same += 1
                out += [f"## {h}" for h in heads[same:]]
                prev = heads
            out += _art_md(a, level=3)
        firm = _http.clean(d.get("firmantes"))
        if firm:
            out.append(f"Firmantes: {firm}")
        meta = {k: v for k, v in (
            ("Tipo", _http.clean(d.get("tipoNorma"))), ("Número", _http.clean(d.get("nroNorma"))),
            ("Promulgación", _http.iso_date(d.get("fechaPromulgacion"))),
            ("Publicación (Diario Oficial)", _http.iso_date(d.get("fechaPublicacion"))),
            ("Estado", _http.clean(d.get("leyenda"))),
            ("Fuente", "IMPO, Licencia de Datos Abiertos – Uruguay")) if v}
        return LawText(id=law["id"], title=law["title"], text="\n\n".join(out), url=law["url"],
                       as_of="", metadata=meta)

    # ------------------------------------------------------------------- case law
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        q = (query or "").strip()
        number = str(filters.get("number") or "").strip()
        if re.fullmatch(r"\d+/\d{4}", q) and q in (number, ""):    # a bare número is not a text query
            number, q = q, ""
        if not q and not number:
            raise BadRequest("Give search words (e.g. 'daño moral') or filters={'number': '207/2020'}.")
        limit, page = max(1, int(limit)), max(1, int(page))
        a, b = (page - 1) * limit, page * limit
        size, clicks = 200, a // 200
        for s in (10, 20, 50, 100, 200):
            k = a // s
            if b <= (k + 1) * s and k <= 3:
                size, clicks = s, k
                break
        if b > (clicks + 1) * size:
            raise BadRequest("That page is too deep for BJN's next-page paging; narrow the query or use dates.")
        async with _bjn_lock:
            form = await _bjn_open()
            html = await _bjn_search(form, q, number, filters, size)
            for _ in range(clicks):
                html = await _bjn_post(form, {"formResultados": "formResultados",
                                              "formResultados:sigLink": "formResultados:sigLink"})
        rows = _bjn_rows(html)
        off = a - clicks * size
        hits = [DecisionHit(id=_did(r), title=f"{r['sede']} {r['numero']}", court=r["sede"],
                            date=r["date"], case_number=r["numero"],
                            snippet=" · ".join(x for x in (r["tipo"], r["proc"]) if x), url=SELECTIVA)
                for r in rows[off:off + limit]]
        m = re.search(r"([\d.]+)\s*resultado/s", html)
        total = int(m[1].replace(".", "")) if m else (0 if not rows else None)
        first = sum(1 for r in rows if _fold(r["sede"]).startswith("juzgado"))
        return Results(items=hits, total=total,
                       note=("BJN has no court-level filter and putting a court name in the query does not select "
                             "courts: results are mostly Suprema Corte and Tribunales de Apelaciones; first-instance "
                             "(Juzgado Letrado, 'Juzgado Ldo.') judgments are a small minority and cannot be "
                             f"requested ({first} of the {len(rows)} rows BJN returned for this query were Juzgados). "
                             "The url is the BJN search page; find a decision there by its número and sede. "
                             "Some decisions are anonymised (AA, BB), many are not."))

    async def get_decision(self, id):
        num, sede, date = _parse_did(id)
        async with _bjn_lock:
            form = await _bjn_open()
            html = await _bjn_search(form, "", num, {}, 200)
            rows = _bjn_rows(html)
            match = [i for i, r in enumerate(rows)
                     if _fold(r["numero"]) == _fold(num) and (not sede or _fold(r["sede"]) == _fold(sede))
                     and (not date or r["date"] == date)]
            if not match:
                raise NotFound(f"BJN: no decision {id!r}. Ids look like '207/2020 | Tribunal Apelaciones "
                               "Civil 1ºTº | 2020-11-11' (from search_caselaw).")
            if len(match) > 1:
                opts = "; ".join(_did(rows[i]) for i in match[:8])
                raise BadRequest(f"BJN: {id!r} matches {len(match)} decisions; use one of: {opts}")
            i = match[0]
            click = await _bjn_post(form, {"formResultados": "formResultados",
                                           f"formResultados:dataTable:{i}:linkTituloSentencia":
                                           f"formResultados:dataTable:{i}:linkTituloSentencia"})
            cid = re.search(r"hojaInsumo2\.seam\?cid=(\d+)", click) or re.search(r"hojaInsumo2\.seam\?cid=(\d+)", html)
            if not cid:
                raise SourceError("BJN: could not open the decision (no hoja de insumo link)", 200)
            r = await _http.get(f"{BJN}/hojaInsumo2.seam", params={"cid": cid[1]})
        if r.status_code != 200:
            raise SourceError("BJN hoja de insumo failed", r.status_code)
        return _parse_hoja(r.text, rows[i])


# --------------------------------------------------------------------------- #
# BJN helpers (JSF/Seam form flow)
# --------------------------------------------------------------------------- #
def _did(r: dict) -> str:
    return " | ".join(x for x in (r["numero"], r["sede"], r["date"]) if x)


def _parse_did(id: str) -> tuple[str, str, str]:
    parts = [p.strip() for p in str(id or "").split("|")]
    num = parts[0] if parts else ""
    if not re.search(r"\d+/\d{4}$", num):
        raise BadRequest("BJN ids look like '207/2020 | Tribunal Apelaciones Civil 1ºTº | 2020-11-11' "
                         f"(número | sede | fecha, from search_caselaw); got {id!r}.")
    sede = parts[1] if len(parts) > 1 else ""
    date = parts[2] if len(parts) > 2 else ""
    if date and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        raise BadRequest(f"BJN id date must be YYYY-MM-DD; got {date!r}.")
    return num, sede, date


async def _bjn_open() -> dict:
    """GET the selective-search page; return the form's action, ViewState and field names."""
    try:
        r = await _http.get(SELECTIVA)
    except Exception as e:
        raise SourceError(f"BJN: {e}", "network") from e
    if r.status_code != 200:
        raise SourceError("BJN search page failed", r.status_code)
    h = r.text
    act = re.search(r'<form id="formBusqueda"[^>]*action="([^"]+)"', h)
    vs = re.search(r'name="javax\.faces\.ViewState"[^>]*value="([^"]+)"', h)

    def name(suffix: str) -> str:
        m = re.search(r'name="(formBusqueda:[^"]*' + re.escape(suffix) + r')"', h)
        return m[1] if m else ""

    sort = re.search(r'<select name="(formBusqueda:[^"]+)"[^>]*>\s*<option value="RELEVANCIA"', h)
    search = re.search(r'id="(formBusqueda:[^"]*:Search)"', h)
    f = {"action": "https://bjn.poderjudicial.gub.uy" + act[1] if act else SELECTIVA,
         "viewstate": vs[1] if vs else "j_id1", "query": name(":cajaQuery"), "number": name(":ayudanteNumero"),
         "types": name(":todosLosTipos"), "importance": name(":todasLasImportancias"),
         "size": name(":cantPag"), "from": name(":fechaDesdeCalInputDate"),
         "to": name(":fechaHastaCalInputDate"), "sort": sort[1] if sort else "",
         "search": search[1] if search else ""}
    if not (f["query"] and f["number"] and f["search"]):
        raise SourceError("BJN: search form changed (fields not found)", r.status_code)
    return f


async def _bjn_post(form: dict, data: dict) -> str:
    body = {"AJAXREQUEST": "_viewRoot", "javax.faces.ViewState": form["viewstate"], **data}
    try:
        r = await _http.post(form["action"], data=body)
    except Exception as e:
        raise SourceError(f"BJN: {e}", "network") from e
    if r.status_code != 200:
        raise SourceError("BJN request failed", r.status_code)
    return r.text


def _dmy(iso: str, what: str) -> str:
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", str(iso).strip())
    if not m:
        raise BadRequest(f"{what} must be YYYY-MM-DD; got {iso!r}.")
    return f"{m[3]}/{m[2]}/{m[1]}"


async def _bjn_search(form: dict, query: str, number: str, filters: dict, size: int) -> str:
    sort = {"relevance": "RELEVANCIA", "date_desc": "FECHA_DESCENDENTE", "date_asc": "FECHA_ASCENDENTE"}
    s = str(filters.get("sort") or "relevance").lower()
    if s not in sort:
        raise BadRequest("sort must be 'relevance', 'date_desc' or 'date_asc'.")
    data = {"formBusqueda": "formBusqueda", form["query"]: query, form["number"]: number,
            form["search"]: form["search"]}
    for k in ("types", "importance"):
        if form[k]:
            data[form[k]] = "on"
    if form["size"]:
        data[form["size"]] = str(size)
    if form["sort"]:
        data[form["sort"]] = sort[s]
    d_from, d_to = filters.get("date_from"), filters.get("date_to")
    if (d_from or d_to) and form["from"] and form["to"]:
        # BJN rejects a one-sided range: fill the open end (earliest BJN year / today).
        data[form["from"]] = _dmy(d_from or "1900-01-01", "date_from")
        data[form["to"]] = _dmy(d_to or date.today().isoformat(), "date_to")
    html = await _bjn_post(form, data)
    err = re.search(r'class="rich-messages-label">([^<]+)', html)
    if err:
        if "No se encontraron" in err[1]:
            return ""
        raise BadRequest(f"BJN: {_tags(err[1])}")
    return html


def _bjn_rows(html: str) -> list[dict]:
    cells: dict[int, dict] = {}
    for m in re.finditer(r'formResultados:dataTable:(\d+):att2Sentencia_(fec|tipo|numero|sedeSentencia|procedimiento)"'
                         r'[^>]*>(.*?)</td>', html, re.S):
        cells.setdefault(int(m[1]), {})[m[2]] = _tags(m[3])
    rows = []
    for i in sorted(cells):
        c = cells[i]
        rows.append({"numero": c.get("numero", ""), "sede": c.get("sedeSentencia", ""),
                     "date": _http.iso_date(c.get("fec", "")), "tipo": c.get("tipo", ""),
                     "proc": c.get("procedimiento", "")})
    return rows


def _parse_hoja(h: str, row: dict) -> Decision:
    def cells(header: str) -> list[str]:
        """Values of the table whose header row has `header` (td order)."""
        m = re.search(r'<table[^>]*>(?:(?!</table>).)*?>' + header + r'</th>(.*?)</table>', h, re.S)
        return [_tags(x) for x in re.findall(r"<td[^>]*>(.*?)</td>", m[1], re.S)] if m else []

    meta: dict[str, str] = {}
    head = cells("N&uacute;mero")
    if len(head) >= 4:
        meta.update({"Importancia": head[2], "Tipo": head[3]})
    second = cells("Fecha")
    ficha = second[1] if len(second) >= 2 else ""
    if len(second) >= 3:
        meta["Procedimiento"] = second[2]
    for label in ("Materias", "Descriptores"):
        v = "; ".join(x for x in cells(label) if x)
        if v:
            meta[label] = v
    for label in ("Firmantes", "Redactores"):
        v = cells(label)
        names = [f"{v[i]} ({v[i + 1]})" if v[i + 1] else v[i] for i in range(0, len(v) - 1, 2) if v[i]]
        if names:
            meta[label] = "; ".join(names)
    abstract = "; ".join(x for x in cells("Abstract") if x)
    resumen = "; ".join(x for x in cells("Resumen") if x)
    if abstract:
        meta["Abstract"] = abstract
    body = re.search(r'<span id="textoSentenciaBox">(.*?)</span></span></div>', h, re.S)
    text = _http.html_to_md(re.sub(r'<span class="highlight">(.*?)</span>', r"\1", body[1], flags=re.S)) if body else ""
    if not text:
        raise SourceError("BJN: decision page has no text", 200)
    if ficha:
        meta["Ficha (IUE)"] = ficha
    note = ("No direct link: BJN has no permalinks and the Source URL below is only its search page. A decision "
            "page (hojaInsumo2.seam?cid=...) works only inside the session that opened it, so do not cite it. "
            "Cite by número, sede, fecha and Ficha (IUE); find it at " + SELECTIVA + " by número and sede.")
    return Decision(id=_did(row), title=f"{row['sede']} {row['numero']}", text=text, url=SELECTIVA,
                    court=row["sede"], date=row["date"], case_number=row["numero"],
                    summary=resumen, metadata=meta, note=note)
