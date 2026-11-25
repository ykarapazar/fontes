"""Bolivia: Tribunal Agroambiental resolutions (case law); the Cámara de Diputados'
register of promulgated laws and LexiVox (unofficial: constitution, laws since 1825).

Gotchas this code encodes (verified 2026-11-06 from a UK IP):
  * Case law: arbol.tribunalagroambiental.bo/consultas (Yii app of the Tribunal
    Agroambiental, the top court of Bolivia's agro-environmental jurisdiction). robots.txt
    is `User-agent: * / Disallow:` (allows all). The "Buscador de Resoluciones" is a form
    whose results come from a POST to index.php?r=site/buscar_simple with the form's
    `_csrf` token (Yii; the token is tied to the session cookie, which the shared httpx
    client keeps). Full-text search; it returns at most 200 rows, newest first, no hit
    count and no paging (its `pagina` parameter is ignored), so paging is done here.
  * A hit is a resolution: "AAP-S1-0181-2026" with the site's numeric idresolucion
    (12757). The id here is that idresolucion (the site's own id, used in its URLs); the
    resolution number cannot be looked up on its own (searching for it finds nothing).
    The full text is Word-made HTML at index.php?r=site/visorresoluciondoshtml&idresolucion=N.
  * Legislation: diputados.gob.bo (WordPress). robots.txt is 404 (no rules). Promulgated
    laws are the custom post type `leyes` with taxonomy estado_de_ley=3 ("Ley Promulgada"),
    exposed by the standard WP REST API /wp-json/wp/v2/ley; `search` also matches the ACF
    description, X-WP-Total gives the hit count. Coverage: laws of the Plurinational
    Assembly, Ley N° 1 (2010) to about Ley N° 1512 (2023); 1,290 entries, thin after 2019.
  * Law texts are the PDFs as promulgated (not consolidated), found via the media record
    in acf.archivo_ley. Older PDFs carry the site's own OCR text layer (noisy: "ART~CULO",
    "l." for "I."); newer ones (e.g. Ley 1512) are plain scans with no text layer: those
    raise a clear error with the PDF link (no OCR here). Some PDFs are large (Ley 439,
    Código Procesal Civil, is 31 MB), so parsed texts are kept in a small in-memory cache.
  * LexiVox (www.lexivox.org, DeveNet S.R.L., unofficial; checked 2026-11-10): robots.txt 404,
    meta robots ALL; terminos.html allows reuse with attribution under GFDL / CC BY-SA 3.0.
    Search is GET packages/lexml/buscar_normas.php (search_xml, id_pais=25, id_tipo_norma,
    nro_norma, paging sacb524current=1,16,31...; 15 per page; "Total: <b>N registro(s)</b>";
    the date fields are ignored and word queries match any word). Norm pages are
    norms/<id>.html (ids BO-CPE-20090207, BO-L-N1650 for post-2009 laws, BO-L-1715 older);
    the text is the div#normTxtId (HTML headings, '<strong>Artículo 1°.-</strong>'). Newest
    law on 2026-11-10: Ley N° 1694 (7 Nov 2025); recent ones are for registered subscribers.
  * Not used (2026-11-06):
    - Tribunal Constitucional Plurinacional, buscador.tcpbolivia.bo: Angular SPA whose
      /api answers 401 unless each request carries an X-Hash signature computed by the
      app (X-Client-ID "angular-app"), and the app has a captcha component: an
      anti-automation scheme, so not built on.
    - Tribunal Supremo de Justicia, genesis.tsj.bo (jurisprudencia.tsj.bo now redirects
      to tsj.bo): Vue SPA backed by apigenesis.tsj.bo, which answers 401 without the
      `username`/`apikey` headers hard-coded in the site's JS. Using the official
      client's credentials would impersonate it; needs the court's permission.
    - Gaceta Oficial del Estado Plurinacional (gacetaoficialdebolivia.gob.bo): the name
      does not resolve from the local resolver (it does via 8.8.8.8, 181.115.190.188).
"""
from __future__ import annotations

import re
from urllib.parse import urlencode

import httpx

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from .._http import fold_marks as _fold
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

TA_HOST = "arbol.tribunalagroambiental.bo"
TA = f"https://{TA_HOST}/consultas/web/index.php"
COURT = "Tribunal Agroambiental"
DIP = "https://diputados.gob.bo"
REST = f"{DIP}/wp-json/wp/v2"
PROMULGADA = 3     # estado_de_ley term id of "Ley Promulgada"
MAX_ROWS = 200     # the Tribunal Agroambiental search never returns more

_TIPOS = {
    "1": "AUTO INTERLOCUTORIO DEFINITIVO", "2": "AUTO NACIONAL AGRARIO",
    "3": "SENTENCIA AGRARIA NACIONAL", "4": "AUTO NACIONAL AGROAMBIENTAL",
    "5": "SENTENCIA AGROAMBIENTAL NACIONAL", "6": "SENTENCIA AGROAMBIENTAL PLURINACIONAL",
    "7": "AUTO AGROAMBIENTAL PLURINACIONAL", "8": "RESOLUCIÓN AMBIENTAL PLURINACIONAL",
    "9": "ENMIENDA COMPLEMENTACIÓN ACLARACIÓN", "10": "AUTO AMBIENTAL DE ADMISIÓN",
    "11": "AUTO INTERLOCUTORIO AMBIENTAL DEFINITIVO", "12": "SEGUIMIENTO CUMPLIMIENTO Y SUPERVISIÓN",
    "13": "AUTO INTERLOCUTORIO SIMPLE AMBIENTAL",
}
_MESES = {m: i for i, m in enumerate(("enero febrero marzo abril mayo junio julio agosto "
                                      "septiembre octubre noviembre diciembre").split(), 1)}
_MESES["setiembre"] = 9

_csrf: dict[str, str] = {}
_searches: dict[tuple, list[DecisionHit]] = {}
_laws: dict[int, dict] = {}
_texts: dict[int, tuple[str, str]] = {}     # law number -> (pdf url, text)


def es_date(s) -> str:
    """First '19 de noviembre de 2013' (Spanish month name) anywhere in s -> '2013-11-19'."""
    m = re.search(r"\b(\d{1,2})\s*(?:º|°|ro)?\s+de\s+(" + "|".join(_MESES) + r")\s+(?:de|del)\s+(\d{4})\b",
                  str(s or ""), re.I)
    if not m:
        return ""
    day, month, year = int(m[1]), _MESES[m[2].lower()], int(m[3])
    return f"{year:04d}-{month:02d}-{day:02d}" if 1 <= day <= 31 else ""


# --------------------------------------------------------------------------- #
# Tribunal Agroambiental
# --------------------------------------------------------------------------- #
async def _token(refresh: bool = False) -> str:
    if refresh or "t" not in _csrf:
        r = await _http.get(TA, params={"r": "site/busquedaresoluciones"})
        if r.status_code != 200:
            raise SourceError(_http.error("tribunalagroambiental.bo", "search form failed", r.status_code),
                              r.status_code)
        m = re.search(r'name="_csrf" value="([^"]+)"', r.text)
        if not m:
            raise SourceError("tribunalagroambiental.bo: no _csrf token on the search form", r.status_code)
        _csrf["t"] = m[1]
    return _csrf["t"]


def _rows(html: str) -> list[DecisionHit]:
    hits = []
    for tr in re.findall(r"(?is)<tr>(.*?)</tr>", html):
        m = re.search(r"idresolucion=(\d+)\"[^>]*>([^<]+)</a>", tr)
        if not m:
            continue
        exp = re.search(r"idproceso=\d+\"[^>]*>([^<]*)</a>", tr)
        tds = re.findall(r"(?is)<td>(.*?)</td>", tr)
        snippet = _http.clean(re.sub(r"<[^>]+>", "", tds[-1])) if len(tds) >= 3 else ""
        number = _http.clean(m[2])
        hits.append(DecisionHit(
            id=m[1], title=f"{COURT} {number}", court=COURT,
            case_number=_http.clean(exp[1]) if exp else "",
            snippet=snippet.strip(". ")[:400], url=_decision_url(m[1])))
    return hits


_YEAR = re.compile(r"\b(?:19|20)\d{2}\b")
_NO_DATE = ("The source has no date filter and does not search dates: narrow by words, "
            "number or title instead and read the dates in the results.")
_NO_DATE_REG = ("The source has no date filter and does not search dates, and its search hits show no date "
                "(only the title words, which may contain a year): open a law to see its date.")
_RES_NO = re.compile(r"^[A-Z]{2,5}-[A-Z0-9]{1,4}-\d{1,5}-\d{4}$", re.I)
_CONST = re.compile(r"constitucional|\btcp\b", re.I)
_TSJ = re.compile(r"corte suprema|tribunal supremo|\btsj\b|supremo de justicia", re.I)


def _case_notes(query: str, capped: bool) -> str:
    notes = []
    if capped:
        notes.append("The source returns at most the 200 newest matches; add words or a "
                     "type filter to narrow.")
    if _TSJ.search(query):
        notes.append("The Supreme Court (Tribunal Supremo de Justicia) is not in this source: "
                     "only the Tribunal Agroambiental is searched.")
    if _RES_NO.fullmatch(query):
        notes.append("The source cannot find a resolution by its number: search by topic words and "
                     "open a hit by its numeric id (get_decision accepts the idresolucion).")
    if _YEAR.search(query):
        notes.append(_NO_DATE)
    if _CONST.search(query):
        notes.append("The Constitutional Court (TCP) is not in this source: these are Tribunal "
                     "Agroambiental resolutions only, even where they discuss constitutional actions.")
    return " ".join(notes)


_SCAN_NOTE = ("Some (mostly newer) Chamber PDFs are scans without text: reading them fails, and "
              "LexiVox may have the text (id 'BO-L-N<number>').")
_CODE_NOTE = ("For codes the source's Number is the number of the law that approved them, and an older "
              "or amending law can have the same number (e.g. Código Penal 1972 and Ley 1768 of 1997 both "
              "show 1768): check the title and date.")
_BODY_DATE = re.compile(r"\bLEY\s+DE\s+(\d{1,2}\s*(?:º|°)?\s+DE\s+[A-ZÁÉÍÓÚa-z]+\s+DE\s+\d{4})", re.I)


def _body_date_warning(title: str, md: str) -> str:
    """LexiVox title date vs the 'LEY DE <date>' line in the body, when they differ."""
    m = _BODY_DATE.search(md[:3000])
    a, b = es_date(title), es_date(m[1]) if m else ""
    if a and b and a != b:
        return (f"The title date ({a}) differs from the date in the text ('{m[1]}', {b}); "
                "check the Gaceta Oficial for the promulgation date.")
    return ""


def _decision_url(idres: str) -> str:
    return f"{TA}?{urlencode({'r': 'site/visorresoluciondoshtml', 'idresolucion': idres})}"


async def _search(query: str, tipo: str) -> list[DecisionHit]:
    key = (query, tipo)
    if key in _searches:
        return _searches[key]
    url = f"{TA}?r=site%2Fbuscar_simple&pagina=1"
    for refresh in (False, True):
        data = {"_csrf": await _token(refresh), "pal_res": query, "tipores": tipo}
        try:
            r = await _http.post(url, data=data, headers={"X-Requested-With": "XMLHttpRequest"})
        except httpx.TransportError:    # the source sometimes drops the connection: retry once
            if refresh:
                raise
            _csrf.pop("t", None)
            continue
        if r.status_code != 400:
            break
    if r.status_code != 200:
        raise SourceError(_http.error("tribunalagroambiental.bo", "search failed", r.status_code), r.status_code)
    if "table-striped" not in r.text:
        raise SourceError("tribunalagroambiental.bo: unexpected search response", r.status_code)
    return _http.lru_put(_searches, key, _rows(r.text), 50)


def _decision_id(id: str) -> str:
    s = str(id or "").strip()
    m = re.search(r"idresolucion=(\d+)", s) or re.fullmatch(r"(\d{1,7})", s)
    if not m:
        raise BadRequest("Tribunal Agroambiental decision ids are the site's numeric idresolucion "
                         "from search_caselaw, e.g. '12757' (resolution numbers such as "
                         "'AAP-S1-0181-2026' cannot be looked up directly; search for them).")
    return m[1]


def _md_table(md: str) -> dict[str, str]:
    """'| **Expediente N°:** | 7031-RCN-2026 |' rows of the header table -> {label: value}."""
    out = {}
    for label, value in re.findall(r"^\|\s*\*\*([^|*]+?)\s*:?\s*\*\*\s*:?\s*\|\s*([^|]*?)\s*\|\s*$", md, re.M):
        label = _http.clean(label).rstrip(" :")
        if label and value and label not in out:
            out[label] = _http.clean(value)
    return out


# --------------------------------------------------------------------------- #
# Cámara de Diputados: promulgated laws
# --------------------------------------------------------------------------- #
def _law_number(id) -> int:
    s = str(id or "").strip()
    m = (re.search(r"/leyes/(?:ley-no|plp-ley-d-n)-(\d+)", s)
         or re.fullmatch(r"(?:ley\s*)?(?:n(?:ro|o|º|°)?\.?\s*[º°]?\s*)?0*(\d{1,5})", s, re.I))
    if not m:
        raise BadRequest("Bolivian law ids are the law number, e.g. '439' or 'Ley N° 439' "
                         "(laws of the Plurinational Assembly, N° 1 of 2010 onwards).")
    return int(m[1])


def _nro(rec: dict) -> int | None:
    m = re.search(r"(\d+)\s*$", str((rec.get("acf") or {}).get("ley_nro") or ""))
    return int(m[1]) if m else None


async def _rest(path: str, params: dict):
    r = await _http.get(f"{REST}/{path}", params=params)
    if r.status_code == 400 and "invalid_page_number" in r.text:
        return [], 0
    if r.status_code != 200:
        raise SourceError(_http.error("diputados.gob.bo", "request failed", r.status_code), r.status_code)
    try:
        data = r.json()
    except ValueError:
        raise SourceError("diputados.gob.bo: unexpected (non-JSON) answer from the WP REST API", r.status_code)
    return data, int(r.headers.get("X-WP-Total", "0") or 0)


_FIELDS = "id,slug,link,title,acf"


async def _law(n: int) -> dict:
    if n in _laws:
        return _laws[n]
    recs, _ = await _rest("ley", {"slug": f"ley-no-{n}", "estado_de_ley": PROMULGADA, "_fields": _FIELDS})
    rec = next((x for x in recs if _nro(x) == n), None)
    if rec is None:
        recs, _ = await _rest("ley", {"search": str(n), "estado_de_ley": PROMULGADA, "per_page": 50,
                                      "_fields": _FIELDS})
        rec = next((x for x in recs if _nro(x) == n), None)
    if rec is None:
        raise NotFound(f"No promulgated Ley N° {n} in the Cámara de Diputados register "
                       "(it covers laws from 2010 to about N° 1512 of 2023).")
    return _http.lru_put(_laws, n, rec, 500)


def _law_title(rec: dict, n: int) -> str:
    desc = _http.clean((rec.get("acf") or {}).get("descripcion")).rstrip(".")
    return f"Ley N° {n}" + (f" – {desc}" if desc else "")


def _law_hit(rec: dict) -> LawHit | None:
    n = _nro(rec)
    if n is None:
        return None
    acf = rec.get("acf") or {}
    return LawHit(id=str(n), title=_law_title(rec, n)[:300], type="Ley", number=str(n),
                  date=es_date(acf.get("titulo")), status=_http.clean(acf.get("estado_de_ley")),
                  url=rec.get("link") or f"{DIP}/leyes/ley-no-{n}/")


def _slug_note(recs: list[dict]) -> str:
    """Warn when a register entry's own link slug names a different law number than the entry."""
    bad = []
    for x in recs:
        n = _nro(x)
        m = re.search(r"-(\d+)/?$", str(x.get("link") or ""))
        if n is not None and m and int(m[1]) != n:
            bad.append(f"Ley N° {n} (link ends in {m[1]})")
    return (" Source data error: the register's own link for " + "; ".join(bad) +
            " names a different law number than the entry; the link is shown as the source gives it, "
            "check the number on the page.") if bad else ""


# The source's OCR garbles headings ("ART~CULO", "ART/CULO", "AKT~CULO", "T~TULO"); only
# these heading words are repaired, any other noise is left as the source has it.
_OCR_FIX = ((re.compile(r"(?m)^A\S{1,4}CULO(?=\s+\d)"), "ARTÍCULO"),
            (re.compile(r"(?m)^T[~/]TULO\b"), "TÍTULO"),
            (re.compile(r"(?m)^CAP[~/]TULO\b"), "CAPÍTULO"))


def _paragraphs(text: str) -> list[str]:
    """pdf_text lines -> paragraphs: a line ending in . : ; closes a paragraph,
    otherwise the next line continues it. Page breaks and bare page numbers are dropped."""
    for rx, rep in _OCR_FIX:
        text = rx.sub(rep, text)
    out: list[str] = []
    cur = ""
    for ln in text.splitlines():
        ln = ln.strip()
        if not ln or re.fullmatch(r"[-–\s]*\d{1,4}[-–\s]*", ln):
            continue
        starts = bool(_ART.match(ln) or _HEAD.match(ln))
        if cur and (starts or re.search(r"[.:;]\s*$", cur)):
            out.append(cur)
            cur = ln
        else:
            cur = f"{cur} {ln}" if cur else ln
    if cur:
        out.append(cur)
    return out


_ART = re.compile(r"^ART[IÍ]CULO\s+(\d{1,4})\s*(?:[º°.\-–)]|\(|\s|$)", re.I)
_HEAD = re.compile(r"^(LIBRO|T[IÍ]TULO|CAP[IÍ]TULO|SECCI[OÓ]N)\b\s*(.*)$")
_HEAD_LEVEL = {"LIBRO": 0, "TITULO": 1, "TÍTULO": 1, "CAPITULO": 2, "CAPÍTULO": 2, "SECCION": 3, "SECCIÓN": 3}
_DISP = re.compile(r"^DISPOSICI(?:O|Ó)N(?:ES)?\s+(TRANSITORIAS?|FINAL(?:ES)?|ADICIONAL(?:ES)?|"
                   r"ABROGATORIAS?|DEROGATORIAS?|ABROGATORIAS?\s+Y\s+DEROGATORIAS?)\b", re.I)
_ORD = re.compile(r"^(PRIMERA|SEGUNDA|TERCERA|CUARTA|QUINTA|SEXTA|S[EÉ]PTIMA|OCTAVA|NOVENA|D[EÉ]CIMA"
                  r"(?:\s+(?:PRIMERA|SEGUNDA|TERCERA|CUARTA|QUINTA|SEXTA|S[EÉ]PTIMA|OCTAVA|NOVENA))?|"
                  r"[UÚ]NICA)\s*[.\-–(]", re.I)


def _singular(s: str) -> str:
    """'TRANSITORIAS' -> 'transitoria', 'FINALES' -> 'final', 'abrogatorias y derogatorias' too."""
    return re.sub(r"\b(\w+?)(?:(?<=l)es|s)\b", r"\1", _http.clean(s).lower())


def _structure(paras: list[str]) -> tuple[list[TocEntry], dict[str, list[str]]]:
    """TOC entries and provision label -> paragraphs. Article headings only count when they
    run on from the previous article (N in last+1..last+5), so articles quoted inside
    amending laws ("se modifica el Artículo 113 ...") are body text."""
    toc: list[TocEntry] = []
    prov: dict[str, list[str]] = {}
    cur: list[str] | None = None
    last, disp = 0, ""
    for p in paras:
        m = _ART.match(p)
        if m and last < int(m[1]) <= last + 5:
            last = int(m[1])
            label = f"Artículo {last}"
            cur = prov.setdefault(label, [])
            head = re.match(r"^ART[IÍ]CULO\s+\d+\s*[º°.\-–]*\s*(\([^)]{1,150}\))?", p, re.I)
            toc.append(TocEntry(title=f"{label} {head[1] or ''}".strip(), level=4, provision=label))
            disp = ""
            cur.append(p)
            continue
        d = _DISP.match(p)
        if d:
            disp = _singular(d[1])
            toc.append(TocEntry(title=_http.clean(p)[:150], level=1))
            cur = None
            continue
        o = _ORD.match(p) if disp else None
        if o:
            label = f"Disposición {disp} {o[1].lower()}"
            cur = prov.setdefault(label, [])
            toc.append(TocEntry(title=label, level=2, provision=label))
            cur.append(p)
            continue
        h = _HEAD.match(p)
        if h and len(p) < 200:
            toc.append(TocEntry(title=_http.clean(p), level=_HEAD_LEVEL.get(h[1].upper(), 1)))
            cur = None
            continue
        if cur is not None:
            cur.append(p)
    return toc, prov


async def _law_text(n: int) -> tuple[dict, str, str]:
    rec = await _law(n)
    if n in _texts:
        return rec, *_texts[n]
    media = (rec.get("acf") or {}).get("archivo_ley")
    if not media:
        raise NotFound(f"Ley N° {n} has no attached file in the Cámara de Diputados register; see {rec.get('link')}")
    m, _ = await _rest(f"media/{int(media)}", {"_fields": "source_url,mime_type"})
    pdf = (m or {}).get("source_url") if isinstance(m, dict) else ""
    if not pdf:
        raise SourceError(f"diputados.gob.bo: no file URL for Ley N° {n}")
    r = await _http.get(pdf)
    if r.status_code != 200:
        raise SourceError(_http.error("diputados.gob.bo", f"PDF of Ley N° {n} failed", r.status_code), r.status_code)
    text = _http.pdf_text(r.content)
    if len(text) < 200:
        raise _Scan(f"Ley N° {n}: the PDF is a scan without a text layer (no OCR here); "
                          f"read it at {pdf} (LexiVox has a text: id 'BO-L-N{n}')")
    _http.lru_put(_texts, n, (pdf, text), 6)
    return rec, pdf, text


def _provision_label(provision: str) -> str:
    s = _http.clean(provision)
    m = re.fullmatch(r"(?:art(?:[ií]culo)?\.?\s*)?(?:n[º°o]?\.?\s*)?(\d{1,4})\s*[º°.]?", s, re.I)
    if m:
        return f"Artículo {int(m[1])}"
    m = re.fullmatch(r"disposici[oó]n(?:es)?\s+((?:abrogatorias?\s+y\s+derogatorias?)|\w+)\s+(.+)", s, re.I)
    if m:
        return f"Disposición {_singular(m[1])} {m[2].lower()}"
    return s


# --------------------------------------------------------------------------- #
# LexiVox (unofficial, GFDL / CC BY-SA): constitution, laws, decree-laws, codes
# --------------------------------------------------------------------------- #
LX = "https://www.lexivox.org"
LX_SEARCH = f"{LX}/packages/lexml/buscar_normas.php"
LX_CPE = "BO-CPE-20090207"
LX_PAGE = 15       # LexiVox search pages hold 15 hits
_LX_TYPES = {"constitucion": "1", "cpe": "1", "ley": "3", "decreto ley": "4", "decreto supremo": "5",
             "ds": "5", "decreto presidencial": "6", "codigo": "8", "codigos": "8"}
_lx: dict[str, tuple[str, str]] = {}       # LexiVox id -> (title, markdown body)


def _lx_id(id) -> str | None:
    """'BO-L-N1650', 'bo-cpe-20090207' or a lexivox.org/norms/... URL -> 'BO-L-N1650'; else None."""
    s = str(id or "").strip()
    m = re.search(r"lexivox\.org/norms/(BO-[\w.-]+?)\.x?html", s, re.I) or re.fullmatch(r"(BO-[A-Z]+-[\w.-]+)", s, re.I)
    return m[1].upper() if m else None


async def _lx_norm(lid: str) -> tuple[str, str]:
    if lid in _lx:
        return _lx[lid]
    url = f"{LX}/norms/{lid}.html"
    r = await _http.get(url)
    if r.status_code == 404 or "Norma inexistente" in r.text[:3000]:
        raise NotFound(f"No LexiVox norm {lid}; search_legislation gives the ids (e.g. 'BO-L-N1650').")
    if r.status_code != 200:
        raise SourceError(_http.error("lexivox.org", f"norm {lid} failed", r.status_code), r.status_code)
    h = r.text
    i = h.find('id="normTxtId"')
    j = h.find('<div class="cierre"', i)
    if i < 0:
        raise SourceError(f"lexivox.org: no norm text block on {url}")
    md = _http.html_to_md(h[h.find(">", i) + 1:j if j > 0 else None])
    t = re.search(r"<title>(.*?)</title>", h, re.S)
    title = _http.clean(re.sub(r"<[^>]+>", "", t[1])) if t else lid
    title = re.sub(r"^Bolivia:\s*", "", title)
    md = re.sub(r"^#\s*Bolivia:[^\n]*\n+", "", md)
    return _http.lru_put(_lx, lid, (title, md), 8)


_LX_ART = re.compile(r"^\*\*\s*Art[ií]culo\s+((?:[a-záéíóú]+\s+)?(?:\d{1,4}(?:\s*bis)?|[uú]nico))\s*[°º]?", re.I)


def _lx_structure(md: str) -> tuple[list[TocEntry], dict[str, list[str]], list[str]]:
    """LexiVox markdown -> TOC, provision label -> paragraphs, paragraphs. Headings are
    markdown (## Título ..., ##### Disposición ...); articles are '**Artículo 1°.- (...)**',
    '**Artículo transitorio 10°.-**', '**Artículo único.-**'."""
    toc: list[TocEntry] = []
    prov: dict[str, list[str]] = {}
    paras = [p.strip() for p in md.split("\n\n") if p.strip()]
    cur: list[str] | None = None
    for p in paras:
        h = re.match(r"^(#{1,6})\s+(.+)$", p)
        if h and "\n" not in p:
            toc.append(TocEntry(title=_http.clean(h[2])[:150], level=max(0, len(h[1]) - 2)))
            cur = None
            continue
        m = _LX_ART.match(p)
        if m:
            label = "Artículo " + re.sub(r"\s+", " ", m[1].lower().replace("unico", "único"))
            base, k = label, 2
            while label in prov:
                label, k = f"{base} ({k})", k + 1
            cur = prov.setdefault(label, [])
            head = re.match(r"^\*\*[^*]*?(\([^)]{1,150}\))\s*\*\*", p)
            toc.append(TocEntry(title=f"{label} {head[1] if head else ''}".strip(), level=4, provision=label))
        if cur is not None:
            cur.append(p)
    return toc, prov, paras


_ABR = re.compile(r"(\d{1,2})/([a-z]{3})[a-z]*/(\d{4})", re.I)


def _abro_before(abro: str, date: str) -> bool:
    """True when the 'd/mmm/yyyy' repeal date is before the norm's own ISO date."""
    m = _ABR.search(abro)
    mon = next((i for k, i in _MESES.items() if k[:3] == m[2].lower()), 0) if m else 0
    return bool(mon and date and f"{int(m[3]):04d}-{mon:02d}-{int(m[1]):02d}" < date)


def _lx_hits(html: str) -> list[LawHit]:
    hits = []
    for block in re.split(r"<h3>", html)[1:]:
        m = re.search(r'<a href="[^"]*/norms/(BO-[\w.-]+?)\.x?html"[^>]*>([^<]+)</a>', block)
        if not m:
            continue
        title = re.sub(r"^Bolivia:\s*", "", _http.clean(m[2]))
        typ = re.search(r'title="Tipo de norma">([^<]*)<', block)
        num = re.search(r'title="N[uú]mero">([^<]*)<', block)
        abro = re.search(r"Abrogada el:\s*([^<]*)<", block)
        status = f"Abrogada el {_http.clean(abro[1])}" if abro else ""
        if abro and _abro_before(abro[1], es_date(title)):
            status += " (earlier than the norm's own date: probably a data error in LexiVox; unverified)"
        hits.append(LawHit(id=m[1].upper(), title=title[:300], type=_http.clean(typ[1]) if typ else "",
                           number=_http.clean(num[1]) if num else "", date=es_date(title),
                           status=status,
                           url=f"{LX}/norms/{m[1]}.html"))
    return hits


async def _lx_search(query: str, tipo: str, nro: str, page: int, limit: int) -> Results:
    first = (max(1, page) - 1) * limit
    items: list[LawHit] = []
    total = 0
    p = first // LX_PAGE
    while len(items) < first % LX_PAGE + limit:
        params = {"search_xml": query, "id_pais": "25", "search_home": "Buscar",
                  "sacb524current": str(p * LX_PAGE + 1)}
        if tipo:
            params["id_tipo_norma"] = tipo
        if nro:
            params["nro_norma"] = nro
        r = await _http.get(LX_SEARCH, params=params)
        if r.status_code != 200:
            raise SourceError(_http.error("lexivox.org", "search failed", r.status_code), r.status_code)
        t = re.search(r"Total:\s*<b>\s*([\d.,]+)", r.text)
        total = int(re.sub(r"\D", "", t[1])) if t else 0
        got = _lx_hits(r.text)
        items += got
        p += 1
        if len(got) < LX_PAGE or p * LX_PAGE >= total:
            break
    off = first % LX_PAGE
    return Results(items=items[off:off + limit], total=total,
                   note=("LexiVox (unofficial, not consolidated): constitution, laws, decree-laws and codes; "
                         "ids look like 'BO-L-N1650'. filters={'source': 'diputados'} searches the "
                         "official Cámara de Diputados register (laws 2010–2023)."
                         + (" " + _NO_DATE if _YEAR.search(query) else "")
                         + (" " + _CODE_NOTE if any("digo" in h.type and h.number for h in items) else "")))


def _dip_note(num: str, q: str) -> str:
    return (f"Read as law number {num} (Ley {num}). " + _SCAN_NOTE
            + (" " + _NO_DATE_REG if _YEAR.search(q) else ""))


class _Scan(SourceError):
    """The Chamber PDF has no text layer."""


class Bolivia(Jurisdiction):
    code = "bo"
    name = "Bolivia"
    languages = ("es",)
    aliases = ("bolivia", "bol", "estado plurinacional de bolivia")
    sources = (
        Source(
            name="Tribunal Agroambiental – Buscador de Resoluciones (SISAGRO consultas)",
            url=f"{TA}?r=site/busquedaresoluciones",
            covers=("caselaw",),
            licence=("unknown: no terms-of-use or licence page on tribunalagroambiental.bo "
                     "(checked 2026-11-06); court resolutions are official texts"),
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit=("unknown; robots.txt allows all, no crawl-delay (2026-11-06); 1 s spacing, "
                        "no 429 seen in ~10 requests"),
            terms_url=f"https://{TA_HOST}/robots.txt",
        ),
        Source(
            name="Cámara de Diputados – Leyes Promulgadas (WP REST API), laws as promulgated",
            url=f"{DIP}/leyes-promulgadas/",
            covers=("legislation",),
            licence=("unknown: no terms-of-use page; site footer says '©2025. Cámara de Diputados. "
                     "Todo los derechos reservados.' (checked 2026-11-06); laws are official texts"),
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit=("unknown; robots.txt is 404 (no rules, 2026-11-06); 1 s spacing, "
                        "no 429 seen in ~15 requests"),
            terms_url=f"{DIP}/robots.txt",
            warning=("Bolivian law texts here are the laws as promulgated (PDF, partly OCR'd by the "
                     "source), not consolidated: check later amending laws."),
        ),
        Source(
            name="LexiVox – Bolivian legislation (constitution, laws, decree-laws, codes; unofficial)",
            url=f"{LX}/packages/lexml/buscar_normas.php",
            covers=("legislation",),
            licence=("GFDL / CC BY-SA 3.0: lexivox.org/terminos.html lets reusers copy, modify and "
                     "redistribute the content with attribution (link to the source URL); each norm "
                     "page says 'Derechos GFDL' (checked 2026-11-10). Run by DeveNet S.R.L., La Paz"),
            commercial_use=True,
            ai_use=None,
            auth="none",
            rate_limit=("unknown; robots.txt is 404 and pages carry meta robots ALL (2026-11-10); "
                        "1 s spacing, no 429 seen in ~15 requests"),
            terms_url=f"{LX}/terminos.html",
            official=False,
            warning=("LexiVox is a private, unofficial compilation of Bolivian norms as published "
                     "(texts transcribed from the Gaceta Oficial, not consolidated, no legal "
                     "authority): check the Gaceta Oficial and later amending laws."),
        ),
    )
    caselaw_filters = {
        "type": "tipo de resolución, code or name: " + ", ".join(f"{k}={v}" for k, v in _TIPOS.items()),
    }
    legislation_filters = {
        "source": "'lexivox' (default: all Bolivian norms, unofficial) or 'diputados' (official "
                  "Cámara de Diputados register, laws 2010–2023)",
        "type": "LexiVox norm type: constitucion, ley, decreto ley, decreto supremo, codigo",
        "number": "norm number, e.g. '1650' (with type 'ley' for LexiVox; also works with source 'diputados')",
    }
    min_interval = {TA_HOST: 1.0, "diputados.gob.bo": 1.0, "www.lexivox.org": 1.0}
    notes = ("Case law: Tribunal Agroambiental only (full text; the TCP and TSJ search APIs are "
             "closed to automated clients). Legislation: the 2009 Constitution and laws, decree-laws "
             "and codes from 1825 to Nov 2025 via LexiVox (unofficial, GFDL; ids 'BO-...'), and "
             "laws 2010–2023 as promulgated via the official Cámara de Diputados register "
             "(numeric ids). Nothing is consolidated.")
    gaps = (
        ("Constitutional Court (TCP): API needs app-computed X-Hash headers plus a captcha (bot "
         "check); needs permission"),
        ("Supreme Court (TSJ): API needs a key hard-coded in the site's JS; needs the court's "
         "permission"),
        ("Official source for laws before 2010 or after ~2023 and for the Constitution: the "
         "Gaceta Oficial (gacetaoficialdebolivia.gob.bo) did not resolve (2026-11-06, 2026-11-10) "
         "and its print notice reserves electronic reproduction; covered only via LexiVox "
         "(unofficial)"),
        ("LexiVox: newest laws missing (latest Ley N° 1694 of 7 Nov 2025 on 2026-11-10; recent "
         "publications are for registered subscribers); texts as published, not consolidated "
         "(some codes as 'Texto ordenado')"),
        "Newer Chamber law PDFs (e.g. Ley 1512): scans only, no text (LexiVox id 'BO-L-N1512' has it)",
        "Senate (senado.gob.bo) and lower courts: not researched yet",
    )
    samples = {
        "caselaw_query": "servidumbre",
        "decision_id": "12757",
        "legislation_query": "Código Procesal Constitucional",
        "law_id": "254",
        "provision": "Artículo 1",
    }

    # ----------------------------------------------------------------- case law
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        tipo = str(filters.get("type") or "").strip()
        if tipo and tipo not in _TIPOS:
            match = [k for k, v in _TIPOS.items() if v.lower() == tipo.lower()]
            if not match:
                raise BadRequest("Unknown type; use one of: " + ", ".join(f"{k} ({v})" for k, v in _TIPOS.items()))
            tipo = match[0]
        query = _http.clean(query)
        if not query:
            raise BadRequest("The Tribunal Agroambiental search needs words to search for; "
                             "use double quotes for a phrase, e.g. '\"servidumbre de paso\"'.")
        rows = await _search(query, tipo)
        start = (max(1, page) - 1) * limit
        capped = len(rows) >= MAX_ROWS
        return Results(items=rows[start:start + limit], total=None if capped else len(rows),
                       note=_case_notes(query, capped))

    async def get_decision(self, id):
        idres = _decision_id(id)
        url = _decision_url(idres)
        r = await _http.get(url)
        if r.status_code == 404:
            raise NotFound(f"No Tribunal Agroambiental resolution idresolucion={idres}.")
        if r.status_code != 200:
            raise SourceError(_http.error("tribunalagroambiental.bo", "resolution failed", r.status_code),
                              r.status_code)
        html = r.text
        i = html.find("Ficha Jurisprudencial</a>")
        j = html.find('<a class="btn btn-success"', i + 1) if i >= 0 else -1
        body = html[i + len("Ficha Jurisprudencial</a>"):j if j > 0 else None] if i >= 0 else ""
        text = _http.html_to_md(body)
        if len(text) < 50:
            raise NotFound(f"No Tribunal Agroambiental resolution text for idresolucion={idres}.")
        num = re.search(r"viewdos&amp;resolucion=([^\"&]+)", html)
        number = _http.clean(num[1]) if num else ""
        meta = _md_table(text[:4000])
        heading = re.match(r"\*\*([^*\n]{5,150})\*\*", text)
        title = f"{COURT} {number}" if number else f"{COURT} {_http.clean(heading[1]) if heading else idres}"
        if number:
            meta["Resolución"] = number
        if heading:
            meta["Encabezado"] = _http.clean(heading[1])
        meta["PDF (con firmas)"] = (f"https://{TA_HOST}/consultas/web/mostrarpdf.php?"
                                    + urlencode({"gestion": number[-4:] if number else "", "tipo": "R",
                                                 "nombre": idres}))
        return Decision(id=idres, title=title, text=text, url=url, court=COURT,
                        date=es_date(meta.get("Fecha", "")),
                        case_number=meta.get("Expediente N°", "") or meta.get("Expediente", ""),
                        metadata=meta)

    # ------------------------------------------------------------- legislation
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        src = _fold(str(filters.get("source") or "lexivox")).strip()
        if src not in ("lexivox", "diputados"):
            raise BadRequest("source must be 'lexivox' or 'diputados'.")
        if src == "lexivox":
            q = _http.clean(query)
            m = re.fullmatch(r"ley\s*(?:n(?:ro|o|º|°)?\.?\s*[º°]?\s*)?(\d{1,5})", q, re.I)
            typ = _fold(str(filters.get("type") or "")).strip()
            if typ and typ not in _LX_TYPES:
                raise BadRequest("type must be one of: " + ", ".join(sorted(set(_LX_TYPES) - {"cpe", "ds", "codigos"})))
            tipo, nro = _LX_TYPES.get(typ, ""), str(filters.get("number") or "").strip()
            if m:   # "Ley 439": that law number (LexiVox has same-numbered pre-2009 laws too)
                tipo, nro, q = "3", m[1], ""
            res = await _lx_search(q, tipo, nro, page, limit)
            if m and _YEAR.search(m[1]):
                res.note += (f" '{query}' was read as law number {m[1]}; " + _NO_DATE)
            if page == 1 and re.search(r"constituci[oó]n", q, re.I) and not nro:
                title, _ = await _lx_norm(LX_CPE)
                cpe = LawHit(id=LX_CPE, title=title, type="Constitución Política del Estado",
                             date="2009-02-07", url=f"{LX}/norms/{LX_CPE}.html")
                res.items = [cpe] + [h for h in res.items if h.id != LX_CPE][:max(0, limit - 1)]
            return res
        params = {"estado_de_ley": PROMULGADA, "per_page": max(1, min(100, limit)), "page": max(1, page),
                  "_fields": _FIELDS}
        q = _http.clean(query)
        m = re.fullmatch(r"ley\s*(?:n(?:ro|o|º|°)?\.?\s*[º°]?\s*)?(\d{1,5})", q, re.I)
        if not m and re.fullmatch(r"\d{1,5}", str(filters.get("number") or "").strip()):
            m = [None, str(filters["number"]).strip()]     # number filter: that law number
        if m:  # "Ley 439": go straight to that law
            try:
                hit = _law_hit(await _law(int(m[1])))
                return Results(items=[hit] if hit else [], total=1 if hit else 0,
                               note=_dip_note(m[1], q) + (_slug_note([_laws[int(m[1])]]) if hit else ""))
            except NotFound:
                return Results(items=[], total=0, note=_dip_note(m[1], q))
        if q:
            params["search"] = q
        recs, total = await _rest("ley", params)
        items = [h for h in (_law_hit(x) for x in recs) if h]
        return Results(items=items, total=total,
                       note="Register covers laws of the Plurinational Assembly from 2010 to about Ley N° 1512 (2023). "
                            "Some (mostly newer) PDFs are scans without text: the text tools then switch to the "
                            "unofficial LexiVox text of the same law (id 'BO-L-N<number>'). The type filter does not apply here."
                            + (" " + _NO_DATE_REG if _YEAR.search(q) else "") + _slug_note(recs))

    async def _scan_lx(self, n: int, e: "_Scan") -> str:
        """Scanned Chamber PDF: the LexiVox id of the same law (unofficial text), else the scan error."""
        lid = f"BO-L-N{n}"
        try:
            await _lx_norm(lid)
        except (NotFound, SourceError):
            raise e
        return lid

    async def get_legislation_toc(self, id):
        lid = _lx_id(id)
        if lid:
            title, md = await _lx_norm(lid)
            return Toc(id=lid, title=title, url=f"{LX}/norms/{lid}.html", entries=_lx_structure(md)[0])
        n = _law_number(id)
        try:
            rec, pdf, text = await _law_text(n)
        except _Scan as e:
            return await self.get_legislation_toc(await self._scan_lx(n, e))
        toc, _ = _structure(_paragraphs(text))
        return Toc(id=str(n), title=_law_title(rec, n), url=rec.get("link") or pdf, entries=toc)

    async def get_legislation_provision(self, id, provision):
        lid = _lx_id(id)
        if lid:
            title, md = await _lx_norm(lid)
            _, prov, _ = _lx_structure(md)
            label = _provision_label(provision)
            key = next((k for k in prov if _fold(k) == _fold(label)), None)
            if key is None:
                raise NotFound(f"No {label!r} in {lid}; get_legislation_toc lists the labels "
                               "(e.g. 'Artículo 1', 'Artículo transitorio 1', 'Artículo único').")
            return Provision(law_id=lid, law_title=title, provision=key, text="\n\n".join(prov[key]),
                             url=f"{LX}/norms/{lid}.html", as_of=es_date(title))
        n = _law_number(id)
        try:
            rec, pdf, text = await _law_text(n)
        except _Scan as e:
            return await self.get_legislation_provision(await self._scan_lx(n, e), provision)
        _, prov = _structure(_paragraphs(text))
        label = _provision_label(provision)
        key = next((k for k in prov if _fold(k) == _fold(label)), None)
        if key is None:
            raise NotFound(f"No {label!r} in Ley N° {n}; get_legislation_toc lists the labels "
                           f"(e.g. 'Artículo 1', 'Disposición transitoria primera').")
        return Provision(law_id=str(n), law_title=_law_title(rec, n), provision=key,
                         text="\n\n".join(prov[key]), url=pdf,
                         as_of=es_date((rec.get("acf") or {}).get("titulo")))

    async def get_legislation_text(self, id):
        lid = _lx_id(id)
        if lid:
            title, md = await _lx_norm(lid)
            return LawText(id=lid, title=title, text=md, url=f"{LX}/norms/{lid}.html", as_of=es_date(title),
                           metadata={"Fuente": "LexiVox (unofficial, GFDL)",
                                     **({"Aviso": w} if (w := _body_date_warning(title, md)) else {})})
        n = _law_number(id)
        try:
            rec, pdf, text = await _law_text(n)
        except _Scan as e:
            return await self.get_legislation_text(await self._scan_lx(n, e))
        acf = rec.get("acf") or {}
        return LawText(id=str(n), title=_law_title(rec, n), text="\n\n".join(_paragraphs(text)), url=pdf,
                       as_of=es_date(acf.get("titulo")),
                       metadata={"Fecha": _http.clean(acf.get("titulo")), "Estado": _http.clean(acf.get("estado_de_ley")),
                                 "Gestión": str(acf.get("gestion") or ""), "Ficha": rec.get("link") or ""})
