"""Ecuador: Corte Constitucional del Ecuador, sentencias and dictámenes (case law only).

Gotchas this code encodes (verified 2026-11-06 from a UK IP):
  * Source: the Court's public "Buscador de Sentencias" (Angular SPA at
    buscador.corteconstitucional.gob.ec/buscador-externo/). Its own backend is a JSON API
    on the same host under /buscador-externo/rest/api/. Every call is a POST whose body is
    {"dato": base64(encodeURIComponent(JSON.stringify(criteria)))}; see _dato().
      - sentencia/100_BUSCR_SNTNCIA: full-text search (field textoSentencia) over the
        decision texts, plus filters (numeroCausa, fechaDecision "YYYY-MM-DD;YYYY-MM-DD").
        The criteria object must carry every key the SPA sends, or the API answers
        "El criterio de búsqueda no contiene metadata". Pages are 20 rows whatever
        pageSize says; total is `totalFilas`.
      - sentencia/100_OBT_FCHA_SNTNCA {numSentencia}: the decision's record (ficha): case,
        action type, reporting judge, decision summary, keywords, and the PDF link. An
        unknown number returns numero "NO EXISTE".
  * id = the Court's own decision number: "1296-19-JP/25" (since 2019), or the older
    form "001-10-SEP-CC" / "0001-10-SEE-CC" (2008-2019). Prefixes like "Sentencia No."
    are stripped.
  * Full text is the signed PDF on esacc.corteconstitucional.gob.ec/storage/api/v1/
    10_DWL_FL/<base64 {"carpeta","uuid"}>; text layer extracted with _http.pdf_text (no OCR).
    The ficha gives that link as http://; we use https.
  * Human page: /buscador-externo/principal/fichaSentencia?numero=<id> (SPA route).
  * Hosts have no robots.txt (buscador answers 404; esacc redirects to its app) and no
    terms-of-use page; 1 s spacing.
  * Legislation not built. Registro Oficial (registroficial.gob.ec) only offers whole
    gazette issues as PDFs (no per-norm search; WordPress REST API needs authorization);
    the Asamblea Nacional "Leyes aprobadas" list links the gazette PDFs, whose law pages
    are image scans without a text layer (checked ro_38.pdf, 2026); gob.ec/regulaciones
    needs a login.
"""
from __future__ import annotations

import base64
import datetime
import json
import re
from urllib.parse import quote

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, Results

HOST = "https://buscador.corteconstitucional.gob.ec"
API = f"{HOST}/buscador-externo/rest/api/"
FICHA = f"{HOST}/buscador-externo/principal/fichaSentencia?numero="
STORAGE = "https://esacc.corteconstitucional.gob.ec/storage/api/v1/10_DWL_FL/"
COURT = "Corte Constitucional del Ecuador"
_COVERAGE_NOTE = ("Only the Corte Constitucional is searched. Corte Nacional de Justicia, lower-court and "
                  "pre-2008 Tribunal Constitucional decisions are not available.")
_CNJ_NOTE = ("The count below is NOT Corte Nacional de Justicia decisions: those are not searchable here. "
             "Hits are Corte Constitucional decisions whose text merely mentions the Corte Nacional. ")
_CNJ = re.compile(r"corte\s+nacional|\bCNJ\b", re.I)
PAGE = 20  # rows per source page, fixed by the API
MAX_LIMIT = 50  # at most 4 source requests (1 s spacing) per call

# Every key the SPA sends; the API refuses a criteria object without them.
_CRITERIA = {"numSentencia": "", "numeroCausa": "", "textoSentencia": "", "motivo": "", "metadata": "",
             "subBusqueda": "", "tipoLegitimado": 0, "legitimados": "", "tipoAcciones": [], "materias": [],
             "intereses": [], "decisiones": [], "jueces": [], "derechoDemandado": [], "derechosTratado": [],
             "derechosVulnerado": [], "temaEspecificos": [], "conceptos": [], "fechaNotificacion": "",
             "fechaDecision": "", "sort": "", "precedenteAprobado": "", "precedentePropuesto": "",
             "tipoNormas": [], "asuntos": [], "analisisMerito": "", "novedad": "", "merito": ""}

_ID = re.compile(r"^\s*(?:(?:sentencia|dictamen|auto)\s*)?(?:n(?:o|ro|ú?m)?\s*[.°º]*\s*)?"
                 r"(\d{1,4}-\d{2}-[A-Z]{1,6}(?:/\d{2}|-CC))\s*$", re.I)
_CASE = re.compile(r"^\s*(?:caso\s*(?:n[o.°º]*\s*)?)?(\d{1,5}-\d{2}-[A-Z]{1,4})\s*$", re.I)
_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")

_dec: dict[str, Decision] = {}


def _dato(criteria: dict) -> dict:
    """The SPA's wire format: base64 of encodeURIComponent(JSON)."""
    s = quote(json.dumps(criteria, ensure_ascii=False, separators=(",", ":")), safe="-_.!~*'()")
    return {"dato": base64.b64encode(s.encode()).decode()}


async def _api(path: str, criteria: dict):
    r = await _http.post(API + path, json=_dato(criteria))
    if r.status_code != 200:
        raise SourceError(_http.error("buscador.corteconstitucional.gob.ec", "request failed",
                                      r.status_code), r.status_code)
    try:
        d = r.json()
    except ValueError:
        raise SourceError("buscador.corteconstitucional.gob.ec: answer is not JSON", r.status_code)
    if d.get("tipoMensaje") not in ("exito", None):
        raise SourceError(f"buscador.corteconstitucional.gob.ec: {d.get('mensaje') or d.get('tipoMensaje')}")
    return d


def _norm_id(id: str) -> str:
    m = _ID.match(str(id or ""))
    if not m:
        raise BadRequest(f"Not a Corte Constitucional decision number: {id!r}. Use e.g. '1296-19-JP/25' "
                         "(since 2019) or '001-10-SEP-CC' (2008-2019).")
    return m[1].upper()


def _ms_date(v) -> str:
    """Epoch milliseconds (Ecuador midnight, UTC-5) -> YYYY-MM-DD."""
    if not v:
        return ""
    if isinstance(v, str):
        return v[:10] if _ISO.match(v[:10]) else ""
    dt = datetime.datetime.fromtimestamp(v / 1000, tz=datetime.timezone(datetime.timedelta(hours=-5)))
    return dt.date().isoformat()


def _date_arg(v: str, name: str) -> str:
    v = str(v).strip()
    if not _ISO.match(v):
        raise BadRequest(f"Filter {name} must be YYYY-MM-DD, got {v!r}.")
    return v


def _pdf_url(doc: dict) -> str:
    uuid = doc.get("uuid") or ""
    if uuid.startswith("http"):
        return "https://" + uuid.split("://", 1)[1]
    if doc.get("repositorio") == "HDFS" and uuid:
        blob = json.dumps({"carpeta": doc.get("carpeta", ""), "uuid": uuid}, separators=(",", ":"))
        return STORAGE + base64.b64encode(blob.encode()).decode()
    return ""


def _hit(row: dict) -> DecisionHit | None:
    r = row.get("resolucion") or {}
    num = _http.clean(r.get("numero"))
    if not num:
        return None
    causa = (r.get("causa") or [{}])[0]
    snippet = " … ".join(_http.clean(re.sub(r"<[^>]+>", "", s)) for s in (row.get("highlight") or {}).get("contenido", [])[:2])
    if not snippet:
        snippet = _http.clean(r.get("motivo"))[:300]
    kind = _http.clean((r.get("documento") or [{}])[0].get("nombre")).capitalize() or "Sentencia"
    return DecisionHit(id=num, title=f"{COURT}, {kind} {num}", court=COURT, date=_ms_date(r.get("fechadecision")),
                       case_number=_http.clean(causa.get("numero")), snippet=snippet[:400],
                       url=FICHA + quote(num, safe="/-"))


class Ecuador(Jurisdiction):
    code = "ec"
    name = "Ecuador"
    languages = ("es",)
    aliases = ("ecuador", "ecu")
    sources = (
        Source(
            name="Corte Constitucional del Ecuador – Buscador de Sentencias (public JSON backend) "
                 "and signed decision PDFs (esacc storage)",
            url=f"{HOST}/buscador-externo/",
            covers=("caselaw",),
            licence=("unknown: no terms-of-use or licence page on buscador/esacc or "
                     "corteconstitucional.gob.ec (checked 2026-11-06); footer says '© Corte Constitucional "
                     "del Ecuador | Todos los derechos reservados'; court decisions are official texts"),
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit=("unknown; no robots.txt on either host (2026-11-06); 1 s spacing, no 429 seen "
                        "in ~15 requests (2026-11-06)"),
            terms_url="",  # none published (2026-11-06)
        ),
    )
    caselaw_filters = {
        "case": "case number (causa), e.g. '1296-19-JP'",
        "date_from": "earliest decision date, YYYY-MM-DD",
        "date_to": "latest decision date, YYYY-MM-DD",
    }
    min_interval = {"buscador.corteconstitucional.gob.ec": 1.0, "esacc.corteconstitucional.gob.ec": 1.0}
    notes = ("Case law: Corte Constitucional (2008 onwards), full-text search, full text from the signed "
             "PDF. No legislation: no official source offers per-norm text without login or OCR.")
    gaps = (
        ("Legislation: Registro Oficial's site search (?s=) matches edition summaries only and returns whole "
         "gazette PDFs, no per-norm text or consolidation; its REST API needs authorization"),
        "Laws via Asamblea Nacional 'Leyes aprobadas': the gazette law pages are scans only, no text",
        ("Constitution: Asamblea Nacional's text-layer PDF (constitucion_de_bolsillo.pdf) is the 2011 edition, "
         "stale (later amendments missing), so not wired (2026-11-10)"),
        "Regulations (gob.ec/regulaciones): needs a login",
        ("Corte Nacional de Justicia: busquedasentencias.cortenacional.gob.ec sends a reCAPTCHA v3 token "
         "(X-reCAPTCHA-Token) with every search call; Gaceta Judicial buscador answers HTTP 500 (2026-11-10)"),
        "Lower-court decisions: not researched yet",
        "Former Tribunal Constitucional decisions (before 2008): not researched yet",
    )
    samples = {
        "caselaw_query": "consulta previa",
        "decision_id": "1296-19-JP/25",
    }

    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        if int(limit or 10) > MAX_LIMIT:
            raise BadRequest(f"limit must be at most {MAX_LIMIT}, got {limit}; use page to walk further.")
        limit = max(1, int(limit or 10))
        page = max(1, int(page or 1))
        crit = dict(_CRITERIA)
        q = _http.clean(query)
        if q and _ID.match(q):
            crit["numSentencia"] = _norm_id(q)
        else:
            crit["textoSentencia"] = q
        if filters.get("case"):
            m = _CASE.match(str(filters["case"]))
            if not m:
                raise BadRequest(f"Filter case must look like '1296-19-JP', got {filters['case']!r}.")
            crit["numeroCausa"] = m[1].upper()
        lo, hi = filters.get("date_from"), filters.get("date_to")
        if lo or hi:
            crit["fechaDecision"] = (f"{_date_arg(lo, 'date_from') if lo else '2008-01-01'};"
                                     f"{_date_arg(hi, 'date_to') if hi else _http.today()}")
        crit["sort"] = "relevancia" if crit["textoSentencia"] else "desc"
        start, end = (page - 1) * limit, page * limit
        hits: list[DecisionHit] = []
        total = None
        src_page = start // PAGE + 1
        while (src_page - 1) * PAGE < end:
            crit["paginacion"] = {"page": src_page, "pageSize": PAGE, "total": 0, "contar": True}
            d = await _api("sentencia/100_BUSCR_SNTNCIA", crit)
            total = d.get("totalFilas")
            rows = d.get("dato") or []
            for i, row in enumerate(rows, (src_page - 1) * PAGE):   # slice by source row, so pages line up
                h = _hit(row) if start <= i < end else None
                if h:
                    hits.append(h)
            if len(rows) < PAGE or (total is not None and src_page * PAGE >= total):
                break
            src_page += 1
        note = (_CNJ_NOTE if _CNJ.search(query or "") else "") + _COVERAGE_NOTE
        return Results(items=hits, total=total, note=note)

    async def get_decision(self, id):
        num = _norm_id(id)
        if num in _dec:
            return _dec[num]
        d = await _api("sentencia/100_OBT_FCHA_SNTNCA", {"numSentencia": num})
        f = d.get("dato") or {}
        if not f or f.get("numero") in (None, "", "NO EXISTE"):
            raise NotFound(f"No Corte Constitucional decision {num}.")
        num = _http.clean(f["numero"])
        doc = f.get("documento") or {}
        pdf = _pdf_url(doc)
        body = ""
        if pdf:
            r = await _http.get(pdf)
            if r.status_code == 200 and r.content[:5] == b"%PDF-":
                body = _http.pdf_text(r.content)
            elif r.status_code not in (404,):
                raise SourceError(_http.error("esacc.corteconstitucional.gob.ec", "PDF download failed",
                                              r.status_code), r.status_code)
        if not body:
            body = (f"The decision PDF has no text layer or is not online; open it here: {pdf}"
                    if pdf else "No decision document is linked to this record.")
        causa = f.get("causa") or {}
        meta = {}
        for label, val in (
            ("Causa", causa.get("numero")),
            ("Tipo de acción", (causa.get("tipoAccion") or {}).get("nombre")),
            ("Juez ponente", (f.get("juez") or {}).get("nombreCompleto")),
            ("Fecha de notificación", _ms_date(f.get("fechaNotificacion"))),
            ("Materia", (f.get("materia") or {}).get("nombre")),
            ("Proceso de origen", f.get("procesoOrigen")),
            ("Número de origen", f.get("numeroOrigen")),
            ("Decisión", (f.get("decision") or {}).get("nombre")),
            ("Descriptores", (f.get("metadataSentencia") or "").strip(" ;")),
            ("Temas", "; ".join(_http.clean(t.get("nombre")) for t in f.get("temas") or [])),
            ("Precedente aprobado", f.get("precedenteAprobado")),
            ("PDF", pdf),
        ):
            v = _http.clean(val)
            if v:
                meta[label] = v
        kind = _http.clean(doc.get("nombreDocumento")).capitalize() or "Sentencia"
        dec = Decision(id=num, title=f"{COURT}, {kind} {num}", text=body, url=FICHA + quote(num, safe="/-"),
                       court=COURT, date=_ms_date(f.get("fechaDecision")), case_number=_http.clean(causa.get("numero")),
                       summary=_http.clean(f.get("motivo")), metadata=meta)
        return _http.lru_put(_dec, num, dec, 50)
