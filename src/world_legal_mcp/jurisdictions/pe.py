"""Peru: Tribunal Constitucional case files (case law) and El Peruano, the official gazette
(legislation as published).

Gotchas this code encodes (verified 2026-11-06 from a UK IP):
  * Case law: www.tc.gob.pe (WordPress). robots.txt is only `Crawl-delay: 30`, so this
    host is throttled to one request per 30 s: a search costs one request, a decision two
    or three (search for the case's internal id_exp, case page, document).
    The server itself is sometimes slow: on 2026-11-10 one search answered after >60 s
    (the shared client's read timeout), the next ones in <1 s. TC requests get 120 s.
  * Search is the Court's "Consulta de causas" form, a plain GET:
    /consultas-de-causas/?bus=tc&action=search&n_exp=&a_exp=&tip_exp=&demdt=&demdo=&ponte=&pagina=N
    It matches the case number, claimant (demdt), defendant (demdo) and reporting judge
    (ponte), NOT the text. 20 rows a page; the page count is in the bootpag script, there
    is no hit count. Free-text query words go to the claimant field.
  * A hit is a case file (expediente) as the site numbers it: "04393-2022-AA". The site's
    process codes differ from the Court's citation suffixes: AA = PA/TC (amparo),
    HC = PHC/TC, HD = PHD/TC, AC = PC/TC (cumplimiento), AI = PI/TC
    (inconstitucionalidad), CC = CC/TC, Q = Q/TC. Both forms are accepted.
  * The case page (/consultas-de-causas/detalles-consulta/?id_exp=N) lists every
    published resolution with a PDF and, for recent ones, an HTML copy, both under
    /jurisprudencia/<publication year>/<file>.pdf|.html. get_decision on an expediente
    returns its latest "Sentencia" (else the latest resolution); a single resolution can
    be fetched by its path, e.g. "2026/00009-2026-AI Admisibilidad".
  * Older PDFs (e.g. 2013) are scans without a text layer: get_decision then says so and
    gives the PDF link (no OCR).
  * The search SPA jurisprudencia.sedetc.gob.pe (full-text search) runs on an
    undocumented backend API; not used.
  * Legislation: busquedas.elperuano.pe (Editora Perú, the official gazette). robots.txt
    allows everything. Pages are server-rendered React Router; the data is in the
    `streamController.enqueue("...")` turbo-stream payload, decoded by _turbo() below.
    Search: /?query=..&start=N&ci=only (20 a page, newest first, full text);
    tipoDispositivo only works together with tipoPublicacion. ci=only keeps individual
    norms; without it every daily booklet is inlined and a page is ~28 MB.
  * A norm is /dispositivo/<tipoPublicacion>/<OP number>; id here is "NL/2471915-1".
    Recent norms have htmlContent (its <title> is sometimes another norm's: ignored);
    older ones only a PDF under /api/archivo/file/... Texts are AS PUBLISHED, not
    consolidated: later amendments are separate norms.
  * Blocked/not used (2026-11-06): Poder Judicial jurisprudencia.pj.gob.pe answers 403
    (WAF) even to robots.txt; SPIJ (spij.minjus.gob.pe, MINJUS consolidated legislation)
    times out; Congress leyes.congreso.gob.pe serves law texts only as PDFs and its
    robots.txt says `Disallow: /*.pdf$`; www2.congreso.gob.pe robots.txt disallows all
    agents but Googlebot. Rechecked 2026-11-10: SPIJ still connect-timeout; the Archivo
    Digital's search (LeyNumePP.aspx, ASP.NET postback) and detail pages are HTML, but every
    text link is Documentos/Leyes/<n>.pdf, under the PDF rule (which sits above the
    `User-agent: *` line, i.e. ungrouped; we honour its evident intent).
  * Constitution: the Congress's official consolidated edition, one PDF on www3.congreso.gob.pe
    (robots allows /Docs/). Part of it is set in a font without a ToUnicode map; _glyphs()
    decodes those runs (glyph id = ASCII - 29, accents in Mac glyph order). Each amended
    article carries a "(*) ... cuyo texto es el siguiente: “...”" note with the new text, and
    some of those quotes never close, so section detection ignores quotes for this text.
"""
from __future__ import annotations

import json
import re
import unicodedata
from urllib.parse import quote, urlencode

from lxml import html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

TC = "https://www.tc.gob.pe"
CAUSAS = f"{TC}/consultas-de-causas/"
DETALLE = f"{TC}/consultas-de-causas/detalles-consulta/"
JURIS = f"{TC}/jurisprudencia"
COURT = "Tribunal Constitucional"
EP = "https://busquedas.elperuano.pe"
CONST_PDF = "https://www3.congreso.gob.pe/Docs/constitucion/constitucion/Constitucion-web_2026.pdf"
CONST_PAGE = "https://www.congreso.gob.pe/constitucion-del-peru-y-reglamento/"
CONST_ID = "constitucion"

# citation suffix (as in "Exp. 00123-2020-PA/TC") -> the site's process code
_PROC = {"PA": "AA", "AA": "AA", "PHC": "HC", "HC": "HC", "PHD": "HD", "HD": "HD", "PC": "AC",
         "AC": "AC", "PI": "AI", "AI": "AI", "CC": "CC", "PCC": "CC", "Q": "Q", "RQ": "Q"}
_EXP = re.compile(r"^\s*(?:exp(?:ediente)?\.?\s*(?:n\.?\s*[°º.]*\s*)?)?(\d{1,5})\s*-\s*((?:19|20)\d\d)"
                  r"\s*-\s*([A-Z]{1,3})(?:\s*/\s*TC)?\s*$", re.I)
_DOC = re.compile(r"(?:^|/jurisprudencia/)((?:19|20)\d\d)/([^/]+?)(?:\.(?:pdf|html?))?\s*$", re.I)
# process names a lawyer types as words -> the site's process code (the search never matches text)
_PROC_WORDS = {"habeas corpus": "HC", "amparo": "AA", "habeas data": "HD", "cumplimiento": "AC",
               "accion de cumplimiento": "AC", "inconstitucionalidad": "AI",
               "accion de inconstitucionalidad": "AI", "competencia": "CC", "conflicto de competencia": "CC"}
_CODE = re.compile(r"^\s*c[oó]digo\b", re.I)
_NAMED_LAW = re.compile(r"^\s*ley\s+(?!n[º°o]?\.?\s*\d|\d)", re.I)
_SENT_DATE = re.compile(r"a\s+los\s+(\d{1,2})\s+d[ií]as\s+del\s+mes\s+de\s+(\w+)\s+(?:de|del)\s+((?:19|20)\d\d)", re.I)
_MONTHS = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
           "octubre", "noviembre", "diciembre")
_PUBS = ("NL", "EX", "SE", "BO")
_LAWID = re.compile(r"^\s*(?:(NL|EX|SE|BO)\s*/\s*)?(\d{4,8}-\d{1,2})\s*$", re.I)

_idexp: dict[str, str] = {}        # expediente -> id_exp
_dec: dict[str, Decision] = {}
_norms: dict[str, dict] = {}


# --------------------------------------------------------------------------- #
# Tribunal Constitucional
# --------------------------------------------------------------------------- #
def _exp(id: str) -> tuple[str, int, str, str] | None:
    """'4393-2022-PA/TC', 'Exp. N.° 04393-2022-AA' -> ('04393-2022-AA', 4393, '2022', 'AA')."""
    m = _EXP.match(str(id or ""))
    if not m:
        return None
    code = _PROC.get(m[3].upper())
    if not code:
        raise BadRequest(f"Unknown process code {m[3]!r}; use AA/PA, HC/PHC, HD/PHD, AC/PC, AI/PI, CC or Q.")
    return f"{int(m[1]):05d}-{m[2]}-{code}", int(m[1]), m[2], code


async def _tc_get(url: str, **kw):
    r = await _http.get(url, timeout=120, **kw)  # slow host at times (>60 s seen 2026-11-10)
    if r.status_code == 404:
        return None
    if r.status_code != 200:
        raise SourceError(_http.error("tc.gob.pe", "request failed", r.status_code), r.status_code)
    return r


def _cell(tr, title: str) -> str:
    el = tr.xpath(f".//*[@data-title='{title}']")
    return _http.clean(el[0].text_content()) if el else ""


async def _causas(params: dict, pagina: int) -> tuple[list[DecisionHit], int]:
    q = {"bus": "tc", "action": "search", "n_exp": "", "a_exp": "", "tip_exp": "", "demdt": "",
         "demdo": "", "ponte": "", **params, "pagina": pagina}
    r = await _tc_get(CAUSAS, params=q)
    if r is None:
        raise SourceError("tc.gob.pe: case search page not found", 404)
    doc = lhtml.fromstring(r.text)
    hits = []
    for tr in doc.xpath("//tbody[@id='body_tabla_lanzado']/tr[.//a[contains(@href,'id_exp=')]]"):
        exp = _cell(tr, "Nro. Expediente")
        m = re.search(r"id_exp=(\d+)", tr.xpath(".//a[contains(@href,'id_exp=')]/@href")[0])
        if not exp or not m:
            continue
        _http.lru_put(_idexp, exp.upper(), m[1], 2000)
        dem, ddo, pj = _cell(tr, "Demandante"), _cell(tr, "Demandado"), _cell(tr, "Nro. PJ")
        title = f"Exp. {exp}" + (f" — {dem} c. {ddo}" if dem or ddo else "")
        hits.append(DecisionHit(id=exp, title=title[:300], court=COURT, case_number=exp,
                                snippet=f"Expediente judicial (PJ): {pj}" if pj else "",
                                url=f"{DETALLE}?id_exp={m[1]}"))
    m = re.search(r"bootpag\(\{\s*total:\s*(\d+)", r.text)
    return hits, int(m[1]) if m else 1


async def _id_exp(exp: str, num: int, year: str, code: str) -> str:
    if exp in _idexp:
        return _idexp[exp]
    await _causas({"n_exp": num, "a_exp": year, "tip_exp": code}, 1)
    if exp not in _idexp:
        raise NotFound(f"No Tribunal Constitucional case file {exp}.")
    return _idexp[exp]


def _docpath(url: str) -> str:
    m = _DOC.search(url.replace("%20", " "))
    return f"{m[1]}/{m[2]}" if m else ""


async def _case(id_exp: str) -> tuple[dict, list[dict]]:
    r = await _tc_get(DETALLE, params={"id_exp": id_exp})
    if r is None:
        raise NotFound(f"No Tribunal Constitucional case page id_exp={id_exp}.")
    doc = lhtml.fromstring(r.text)
    info: dict[str, str] = {}
    for title in ("Nro. expediente", "Fecha de ingreso", "Colegiado", "Ponente",
                  "Fecha de Devolución al PJ", "Oficio de Devolución del TC"):
        info[title] = next((_http.clean(e.text_content()) for e in doc.xpath(f"//*[@data-title='{title}']")), "")
    docs = []
    for tr in doc.xpath("//tr[td[@data-title='Tipo de Resolución']]"):
        pdf = tr.xpath(".//td[@data-title='Ver Publicación']//a/@href")
        htm = tr.xpath(".//td[@data-title='Ver Publicación (Formato HTML)']//a/@href")
        if not pdf and not htm:
            continue
        web = _cell(tr, "Fecha de Public. Web")
        docs.append({"tipo": _cell(tr, "Tipo de Resolución"),
                     "date": _http.iso_date(web.split(" ")[0]) if web else "",
                     "fallo": _cell(tr, "Fallo"), "peruano": _cell(tr, "Public. Diario El Peruano"),
                     "pdf": pdf[0].strip() if pdf else "", "html": htm[0].strip() if htm else "",
                     "path": _docpath((htm or pdf)[0])})
    return info, docs


def _sent_date(text: str) -> str:
    """Date the Court signed the ruling ("a los 14 días del mes de enero de 2020"), else ''."""
    m = _SENT_DATE.search(text[:3000])
    mon = _fold(m[2]) if m else ""
    mon = "septiembre" if mon == "setiembre" else mon
    if not m or mon not in _MONTHS:
        return ""
    return f"{m[3]}-{_MONTHS.index(mon) + 1:02d}-{int(m[1]):02d}"


def _pick(docs: list[dict]) -> dict:
    sent = [d for d in docs if d["tipo"].lower().startswith("sentencia")] or docs
    return max(enumerate(sent), key=lambda p: (p[1]["date"], p[0]))[1]


async def _doc_text(html_url: str, pdf_url: str) -> tuple[str, str]:
    """Text of one resolution: the HTML copy if there is one, else the PDF's text layer."""
    if html_url:
        r = await _tc_get(quote(html_url, safe=":/"))
        if r is not None:
            try:  # recent files are UTF-8, older .htm exports Windows-1252
                page = r.content.decode("utf-8")
            except UnicodeDecodeError:
                page = r.content.decode("cp1252", errors="replace")
            return _http.html_to_md(page), html_url
    if pdf_url:
        r = await _tc_get(quote(pdf_url, safe=":/"))
        if r is not None:
            if not r.content.startswith(b"%PDF"):
                raise SourceError(f"tc.gob.pe: {pdf_url} is not a PDF", r.status_code)
            text = _http.pdf_text(r.content)
            if len(text) < 200:
                raise SourceError(f"tc.gob.pe: this resolution is a scanned PDF without a text layer "
                                  f"(no OCR here); read it at {pdf_url}", 200)
            return text, pdf_url
    return "", ""


# --------------------------------------------------------------------------- #
# El Peruano
# --------------------------------------------------------------------------- #
def _turbo(page: str) -> dict:
    """React Router's turbo-stream payload in the page -> plain loaderData dict."""
    m = re.search(r'streamController\.enqueue\(("(?:[^"\\]|\\.)*")\)', page)
    if not m:
        raise SourceError("El Peruano: page carries no data payload (layout changed?)", 200)
    arr = json.loads(json.loads(m[1]).split("\n", 1)[0])

    def d(i):
        if not isinstance(i, int) or i < 0:
            return None
        v = arr[i]
        if isinstance(v, dict):
            return {arr[int(k[1:])]: d(x) for k, x in v.items()}
        if isinstance(v, list):
            return v if v and isinstance(v[0], str) else [d(x) for x in v]
        return v
    return (d(0) or {}).get("loaderData") or {}


def _ymd(s) -> str:
    s = str(s or "")
    return f"{s[:4]}-{s[4:6]}-{s[6:8]}" if re.fullmatch(r"\d{8}", s) else ""


def _law_id(id: str) -> tuple[str, str]:
    s = str(id or "").strip()
    m = re.search(r"/dispositivo/([A-Z]{2})/(\d{4,8}-\d{1,2})", s) or _LAWID.match(s)
    if not m:
        raise BadRequest("El Peruano ids are '<publication>/<OP number>', e.g. 'NL/2428226-2' "
                         f"(from search_legislation); got {id!r}.")
    return (m[1] or "NL").upper(), m[2]


def _law_title(tipo: str, num: str, sumilla: str) -> str:
    head = _http.clean(f"{tipo} {num}")
    sumilla = _http.clean(sumilla)
    return f"{head} — {sumilla}" if head and sumilla else head or sumilla


_HEAD = re.compile(r"^(T[ÍI]TULO|CAP[ÍI]TULO|SECCI[ÓO]N|LIBRO|DISPOSICI[ÓO]N(ES)?\b|ANEXO)", re.I)
_NAMED_LAW = re.compile(r"^\s*ley\s+(?!n[º°o]?\.?\s*\d|\d)", re.I)
_ART = re.compile(r"^\**\s*(?:Art[íi]culo|Art\.)\s+(\d+[º°]?(?:\s*-?\s*[A-Z])?(?![\w])|[IVXL]+(?![\w])|[úu]nico)\s*\.?", re.I)
_ORD = re.compile(r"^\**\s*(PRIMERA|SEGUNDA|TERCERA|CUARTA|QUINTA|SEXTA|S[ÉE]PTIMA|S[ÉE]TIMA|OCTAVA|NOVENA|"
                  r"D[ÉE]CIMA(?:\s+\w+)?|DECIMO\w+|UND[ÉE]CIMA|DUOD[ÉE]CIMA|[ÚU]NICA)\b\.?", re.I)


def _fold(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()


def _art_label(tok: str) -> str:
    tok = re.sub(r"\s+", "", tok.replace("º", "").replace("°", ""))
    if tok.lower() in ("unico", "único"):
        return "Artículo único"
    if re.fullmatch(r"[IVXL]+", tok.upper()):
        return f"Artículo {tok.upper()}"
    m = re.fullmatch(r"(\d+)-?([A-Za-z]?)", tok)
    return f"Artículo {m[1]}" + (f"-{m[2].upper()}" if m[2] else "")


def _sections(paras: list[str], quotes: bool = True) -> list[tuple[str, str, int]]:
    """Paragraphs -> [(provision label or '', heading text, start index)].
    Headings inside a quoted amendment (between “ and ”) are part of the article
    (quotes=False for texts whose quotes are unbalanced, e.g. the Constitution's notes)."""
    out, depth, section = [], 0, ""
    for i, p in enumerate(paras):
        plain = p.strip("*_ #")
        if depth <= 0:
            if _HEAD.match(plain) and plain.upper() == plain:
                section = plain
                out.append(("", plain, i))
            elif m := _ART.match(plain):
                out.append((_art_label(m[1]), plain, i))
            elif section.upper().startswith("DISPOSICI") and (m := _ORD.match(plain)):
                out.append((f"{section.capitalize()} – {m[1].capitalize()}", plain, i))
        if quotes:
            depth += p.count("“") - p.count("”")
    seen: dict[str, int] = {}
    uniq = []
    for label, head, i in out:  # a repeated label (e.g. two annexes) gets a suffix
        if label:
            seen[label] = seen.get(label, 0) + 1
            if seen[label] > 1:
                label = f"{label} ({seen[label]})"
        uniq.append((label, head, i))
    return uniq


# --------------------------------------------------------------------------- #
# Constitution: the Congress's official consolidated edition (PDF)
# --------------------------------------------------------------------------- #
# Part of the PDF is set in a subset font (Arimo, Type0/Identity-H) with no ToUnicode map
# and no cmap table: the codes are glyph ids. In that font glyph id = ASCII code - 29 and
# the accents follow the Macintosh standard glyph order; the few extra codes below were
# checked against the surrounding text (2026-11-10).
_GLYPH = {105: "á", 112: "é", 116: "í", 121: "ó", 126: "ú", 120: "ñ", 129: "ü", 157: "º",
          178: "“", 179: "”", 190: "fi", 191: "fl", 236: '"'}
_RUNNING = re.compile(r"^\d+\s*(CONSTITUCIÓN POLÍTICA DEL PERÚ|Edición del Congreso de la República)$")
_NEWPARA = re.compile(r"^(Art[íi]culo\s+\d+|\d{1,2}\.\s|[a-z]\)\s|(PRIMERA|SEGUNDA|TERCERA|CUARTA|QUINTA|SEXTA|"
                      r"S[ÉE]P?TIMA|OCTAVA|NOVENA|D[ÉE]CIMA|DECIMO\w+|UND[ÉE]CIMA|DUOD[ÉE]CIMA)\.)", re.I)


_ARTLINE = re.compile(r"^\**\s*Art[íi]culo\s+\S+?\s*[.\-–—]", re.I)


def _split_pdf(paras: list[str]) -> list[str]:
    """PDF text has one newline between lines, so a whole page is one paragraph: start a new
    paragraph at each 'Artículo N.' line and each all-caps heading line."""
    out: list[str] = []
    for p in paras:
        cur: list[str] = []
        for line in p.split("\n"):
            plain = line.strip("*_ #")
            if cur and (_ARTLINE.match(plain) or (_HEAD.match(plain) and plain.upper() == plain)):
                out.append("\n".join(cur))
                cur = []
            cur.append(line)
        out.append("\n".join(cur))
    return out


def _glyphs(s: str) -> str:
    out = []
    for ch in s:
        o = ord(ch)
        if ch in " \n":            # spacing pypdf inserted itself
            out.append(ch)
        elif 3 <= o <= 97:
            out.append(chr(o + 29))
        else:
            out.append(_GLYPH.get(o, "�"))
    return "".join(out)


def _const_text(data: bytes) -> str:
    from io import BytesIO

    from pypdf import PdfReader
    pages = []
    for p in PdfReader(BytesIO(data)).pages:
        parts: list[str] = []

        def visit(text, cm, tm, font, size, parts=parts):
            raw = font is not None and font.get("/Subtype") == "/Type0" and "/ToUnicode" not in font
            parts.append(_glyphs(text) if raw else text)
        p.extract_text(visitor_text=visit)
        pages.append("".join(parts))
    paras: list[str] = []
    cur: list[str] = []
    for line in "\n".join(pages).splitlines():
        line = _http.clean(line)
        if not line or _RUNNING.match(line):
            continue
        heading = (line.upper() == line and re.search(r"[A-ZÁÉÍÓÚÑ]{3}", line)) or \
            re.match(r"^(Cap[íi]tulo|CAP[ÍI]TULO|T[ÍI]TULO)\s+[IVXL]+\b", line)
        if (heading or _NEWPARA.match(line)) and cur:
            paras.append(" ".join(cur))
            cur = []
        cur.append(line)
        if heading:
            paras.append(" ".join(cur))
            cur = []
    if cur:
        paras.append(" ".join(cur))
    return "\n\n".join(paras)


async def _constitution() -> dict:
    if CONST_ID in _norms:
        return _norms[CONST_ID]
    r = await _http.get(CONST_PDF)
    if r.status_code != 200 or not r.content.startswith(b"%PDF"):
        raise SourceError(_http.error("Congreso (www3.congreso.gob.pe)", "Constitution PDF request failed",
                                      r.status_code), r.status_code)
    text = _const_text(r.content)
    m = re.search(r"Edición del Congreso de la República\s+(\w+) de (\d{4})", text)
    edition = f"{m[1]} de {m[2]}" if m else ""
    paras = [p for p in text.split("\n\n") if p.strip()]
    norm = {"id": CONST_ID, "url": CONST_PDF, "date": "1993-12-30", "text": text, "paras": paras, "noquote": True,
            "title": "Constitución Política del Perú de 1993 (texto actualizado, edición oficial del Congreso)",
            "meta": {"Edición": f"Edición oficial del Congreso de la República{', ' + edition if edition else ''}",
                     "Promulgación": "1993-12-29", "Publicación": "1993-12-30",
                     "Ficha": CONST_PAGE}}
    return _http.lru_put(_norms, CONST_ID, norm, 8)


def _is_const(id: str) -> bool:
    s = _fold(_http.clean(id)).replace(".", "")
    return s in ("constitucion", "cpp", "constitucion politica", "constitucion politica del peru",
                 "constitucion de 1993", "constitucion politica del peru de 1993", _fold(CONST_PDF).replace(".", ""))


async def _norm(id: str) -> dict:
    if _is_const(id):
        return await _constitution()
    pub, op = _law_id(id)
    key = f"{pub}/{op}"
    if key in _norms:
        return _norms[key]
    url = f"{EP}/dispositivo/{pub}/{op}"
    r = await _http.get(url)
    if r.status_code == 404:
        raise NotFound(f"No El Peruano norm {key}.")
    if r.status_code != 200:
        raise SourceError(_http.error("El Peruano", "norm request failed", r.status_code), r.status_code)
    data = next((v for k, v in _turbo(r.text).items() if k.startswith("routes/dispositivo")), None) or {}
    disp = data.get("dispositivo")
    if not disp:
        raise NotFound(f"No El Peruano norm {key}.")
    text = ""
    if data.get("htmlContent"):
        text = _http.html_to_md(re.sub(r"(?is)<head\b.*?</head>", "", data["htmlContent"]))
    from_pdf = not text
    if not text and disp.get("urlPDF"):
        p = await _http.get(EP + disp["urlPDF"].replace("*", "%2A"))
        if p.status_code != 200 or not p.content.startswith(b"%PDF"):
            raise SourceError(_http.error("El Peruano", "PDF request failed", p.status_code), p.status_code)
        text = _http.pdf_text(p.content)
    if not text:
        raise SourceError(f"El Peruano: {key} has no HTML and its PDF has no text layer (no OCR here); "
                          f"see {url}", 200)
    first = text.split("\n", 1)[0].strip("*# ")
    num = ""
    if m := re.search(r"N[º°o]\.?\s*([\w./-]+(?:-[\w./]+)*)", first):
        num = m[1]
    paras = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    if from_pdf:
        paras = _split_pdf(paras)
    norm = {"id": key, "url": url, "date": _ymd(disp.get("fechaPublicacion")), "text": text, "paras": paras,
            "title": _law_title(disp.get("tipoDispositivo") or "", f"N° {num}" if num else "",
                                disp.get("sumilla") or ""),
            "meta": {k: _http.clean(v) for k, v in (
                ("Tipo de dispositivo", disp.get("tipoDispositivo")),
                ("Publicación", disp.get("tipoPublicacion")),
                ("Fecha de publicación", _ymd(disp.get("fechaPublicacion"))),
                ("PDF", EP + disp["urlPDF"] if disp.get("urlPDF") else "")) if _http.clean(v)}}
    return _http.lru_put(_norms, key, norm, 8)


def _prov_key(s: str) -> str:
    s = _fold(_http.clean(s)).replace("º", "").replace("°", "")
    s = re.sub(r"^(art[ií]culo|art\.?)\s*", "", s).strip(" .")
    if re.fullmatch(r"\d+\s*-?\s*[a-z]?", s):
        m = re.fullmatch(r"(\d+)\s*-?\s*([a-z]?)", s)
        return f"art:{m[1]}" + (f"-{m[2]}" if m[2] else "")
    if re.fullmatch(r"[ivxl]+", s):
        return f"art:{s}"
    if s == "unico":
        return "art:unico"
    return s


class Peru(Jurisdiction):
    code = "pe"
    name = "Peru"
    languages = ("es",)
    aliases = ("peru", "perú", "per")
    sources = (
        Source(
            name="Tribunal Constitucional – Consulta de causas and published resolutions",
            url=CAUSAS,
            covers=("caselaw",),
            licence=("unknown: tc.gob.pe has no terms-of-use or licence page (checked 2026-11-06); "
                     "court decisions are official texts"),
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit=("robots.txt Crawl-delay: 30 (2026-11-06), honoured: one request per 30 s, "
                        "so a search takes ~30 s and a decision up to ~90 s"),
            terms_url="https://www.tc.gob.pe/robots.txt",
            # a resolution path costs one request; a case number costs three, which with the
            # 30 s crawl delay overruns the health check's 90 s budget
            probe={"caselaw_query": "MUNICIPALIDAD", "decision_id": "2026/00009-2026-AI Admisibilidad"},
        ),
        Source(
            name="El Peruano – Diario Oficial, Búsquedas (Editora Perú): norms as published",
            url=EP,
            covers=("legislation",),
            licence="unknown: no terms-of-use page found on busquedas.elperuano.pe or elperuano.pe (2026-11-06)",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit=("unknown; robots.txt allows all, no crawl-delay; 1 s spacing, "
                        "no 429 seen in ~15 requests (2026-11-06)"),
            terms_url="https://busquedas.elperuano.pe/robots.txt",
        ),        Source(
            name="Congreso de la República – Constitución Política del Perú, edición oficial (consolidated)",
            url=CONST_PAGE,
            covers=("legislation",),
            licence=("unknown: congreso.gob.pe has no terms-of-use or licence page found (2026-11-10); "
                     "the Constitution is an official text"),
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit=("unknown; one PDF (~2.4 MB) per call, cached in memory; robots.txt of "
                        "www3.congreso.gob.pe allows /Docs/ (2026-11-10)"),
            terms_url="https://www3.congreso.gob.pe/robots.txt",
        ),
    )
    caselaw_filters = {
        "number": "case number as the TC writes it, e.g. '00006-2019-CC' or '4393-2022-PA/TC'",
        "year": "year of the case number, e.g. 2022",
        "process": "AA/PA (amparo), HC/PHC, HD/PHD, AC/PC (cumplimiento), AI/PI (inconstitucionalidad), CC, Q",
        "claimant": "demandante name or part of it",
        "defendant": "demandado name or part of it, e.g. 'MUNICIPALIDAD DE MIRAFLORES'",
        "judge": "magistrado ponente surname",
    }
    legislation_filters = {
        "publication": "NL (Normas Legales, default when 'type' is set), EX (edición extraordinaria), "
                       "SE (separatas especiales), BO (boletín oficial)",
        "type": "tipo de dispositivo, e.g. 'LEY', 'DECRETO SUPREMO', 'DECRETO LEGISLATIVO', "
                "'DECRETO DE URGENCIA', 'RESOLUCIONES MINISTERIALES'",
        "date_from": "earliest publication date, YYYY-MM-DD",
        "date_to": "latest publication date, YYYY-MM-DD",
    }
    min_interval = {"www.tc.gob.pe": 30.0, "busquedas.elperuano.pe": 1.0, "www3.congreso.gob.pe": 1.0}
    notes = ("Case law: Tribunal Constitucional case files, found by case number, party or reporting "
             "judge (not full text); slow by design (site asks 30 s between requests). Legislation: "
             "El Peruano gazette, full-text search, norms as published (not consolidated), "
             "individual norms online from about 2009; the Constitution consolidated (Congress "
             "official edition, id 'constitucion').")
    gaps = (
        "Poder Judicial case law (ordinary courts, jurisprudencia.pj.gob.pe): WAF blocks our "
         "client (403, even robots.txt)",
        "Consolidated legislation (SPIJ, MINJUS): unreachable from the UK (connect timeout, "
         "2026-11-06 and 2026-11-10)",
        "Laws before about 2009 and consolidated laws: the Congress's Archivo Digital "
         "(leyes.congreso.gob.pe, every law since 1904) serves texts only as PDFs and its robots.txt "
         "has 'Disallow: /*.pdf$' (written above the 'User-agent: *' group, so formally ungrouped, "
         "but clearly meant for all robots; honoured)",
        "TC full-text search (jurisprudencia.sedetc.gob.pe): undocumented backend API, not used; "
         "search is by number/party",
        "Older TC resolutions (e.g. 2013): scans only, no text",
        "Individual norms in El Peruano before about 2009: not published online as single norms",
    )
    samples = {
        "caselaw_query": "MUNICIPALIDAD",
        "decision_id": "00002-2020-CC",
        "legislation_query": "Nueva Ley de Nacionalidad",
        "law_id": "NL/2428226-2",
        "provision": "Artículo 1",
    }

    # ----------------------------------------------------------------- case law
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        f = {k: _http.clean(v) for k, v in (filters or {}).items() if _http.clean(v)}
        params: dict = {}
        ignored = False
        q = _http.clean(query)
        num = f.get("number") or (q if q and _exp(q) else "")
        if num:
            e = _exp(num)
            if not e:
                raise BadRequest(f"number must look like '00006-2019-CC' or '4393-2022-PA/TC'; got {num!r}.")
            params.update(n_exp=e[1], a_exp=e[2], tip_exp=e[3])
            if q == num:
                q = ""
        if y := f.get("year"):
            if not re.fullmatch(r"(19|20)\d\d", y):
                raise BadRequest(f"year must be four digits, e.g. 2022; got {y!r}.")
            params["a_exp"] = y
        if p := f.get("process"):
            code = _PROC.get(p.upper())
            if not code:
                raise BadRequest("process must be one of AA/PA, HC/PHC, HD/PHD, AC/PC, AI/PI, CC, Q; "
                                 f"got {p!r}.")
            params["tip_exp"] = code
        word = _PROC_WORDS.get(_fold(q))
        if word:  # "habeas corpus", "amparo": a process type, not a party name
            params.setdefault("tip_exp", word)
            q = ""
            ignored = True
        claimant = " ".join(x for x in (q, f.get("claimant", "")) if x)
        if claimant:
            params["demdt"] = claimant
        if d := f.get("defendant"):
            params["demdo"] = d
        if j := f.get("judge"):
            params["ponte"] = j
        if not params:
            raise BadRequest("Give a case number, a party name or a filter (claimant, defendant, judge, "
                             "year, process).")
        per = 20
        first = (page - 1) * limit
        items: list[DecisionHit] = []
        pages = 1
        site = first // per + 1
        while len(items) < limit:
            hits, pages = await _causas(params, site)
            skip = first - (site - 1) * per if not items else 0
            items += hits[skip:]
            if len(hits) < per or site >= pages:
                break
            site += 1
        items = items[:limit]
        total = None
        if pages <= 1 and site == 1:
            total = len(hits)
        note = ("Searches the Court's case register (case number, claimant, defendant, reporting judge), "
                "not decision text; free words match the claimant. "
                f"{pages} page(s) of 20 case files at the source.")
        if ignored:
            note = (f"The words {_http.clean(query)!r} were read as the process type, not searched in any text: "
                    "this is the register of that process type, newest first, and the decision text is not "
                    "searchable here. Recent case files often have no published resolution yet "
                    "(get_decision then says so); add filters year to reach older, decided cases. ") + note
        return Results(items, total=total, note=note, query_ignored=ignored)

    async def get_decision(self, id):
        s = _http.clean(id)
        key = s.upper()
        if key in _dec:
            return _dec[key]
        e = _exp(s)
        if e:
            exp = e[0]
            id_exp = await _id_exp(*e)
            info, docs = await _case(id_exp)
            if not docs:
                raise NotFound(f"Case file {exp} has no published resolution yet "
                               f"({DETALLE}?id_exp={id_exp}).")
            doc = _pick(docs)
            text, url = await _doc_text(doc["html"], doc["pdf"])
            if not text:
                raise NotFound(f"The resolution files of {exp} are not on tc.gob.pe ({DETALLE}?id_exp={id_exp}).")
            meta = {k: v for k, v in info.items() if v and k != "Nro. expediente"}
            meta.update({"Tipo de resolución": doc["tipo"], "Fallo": doc["fallo"],
                         "Publicación en El Peruano": doc["peruano"],
                         "Ficha del expediente": f"{DETALLE}?id_exp={id_exp}"})
            others = [f"{d['tipo']} ({d['date']}): {d['path']}" for d in docs if d is not doc]
            if others:
                meta["Otras resoluciones (id para get_decision)"] = "; ".join(others)
            d = Decision(id=exp, title=f"{COURT}, Exp. {exp} — {doc['tipo']}", text=text, url=url,
                         court=COURT, date=doc["date"], case_number=exp,
                         metadata={k: v for k, v in meta.items() if v})
            return _http.lru_put(_dec, key, d, 8)
        m = _DOC.search(s.replace("%20", " "))
        if not m:
            raise BadRequest("Peruvian TC ids are case numbers like '00006-2019-CC' or '4393-2022-PA/TC', "
                             "or a resolution path like '2026/00009-2026-AI Admisibilidad'; "
                             f"got {id!r}.")
        path = f"{m[1]}/{m[2]}"
        text, url = await _doc_text(f"{JURIS}/{path}.html", "")
        if not text:  # older copies are .htm
            text, url = await _doc_text(f"{JURIS}/{path}.htm", f"{JURIS}/{path}.pdf")
        if not text:
            raise NotFound(f"No Tribunal Constitucional resolution file {path}.")
        exp = re.match(r"(\d{5}-\d{4}-[A-Z]{1,2})", m[2])
        d = Decision(id=path, title=f"{COURT}, {m[2]}", text=text, url=url, court=COURT,
                     case_number=exp[1] if exp else "")
        return _http.lru_put(_dec, key, d, 8)

    # -------------------------------------------------------------- legislation
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        f = {k: _http.clean(v) for k, v in (filters or {}).items() if _http.clean(v)}
        params: dict = {"ci": "only"}
        q = _http.clean(query)
        if q:
            params["query"] = q
        if t := f.get("type"):
            params["tipoDispositivo"] = t.upper()
        if p := f.get("publication"):
            if p.upper() not in _PUBS:
                raise BadRequest(f"publication must be one of {', '.join(_PUBS)}; got {p!r}.")
            params["tipoPublicacion"] = p.upper()
        for k, name in (("date_from", "fechaIni"), ("date_to", "fechaFin")):
            if v := f.get(k):
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
                    raise BadRequest(f"{k} must be YYYY-MM-DD; got {v!r}.")
                params[name] = v.replace("-", "")
        if not q and len(params) == 1:
            raise BadRequest("Give search words or a filter (type, publication, date_from, date_to).")
        per = 20

        async def run(params, want, first):
            start = first // per * per
            items: list[LawHit] = []
            total = None
            while len(items) < want:
                r = await _http.get(f"{EP}/?" + urlencode({**params, "start": start}))
                if r.status_code != 200:
                    raise SourceError(_http.error("El Peruano", "search failed", r.status_code), r.status_code)
                res = (_turbo(r.text).get("routes/_index") or {}).get("results") or {}
                total = res.get("totalHits")
                hits = res.get("hits") or []
                for h in hits[first - start if not items else 0:]:
                    if not h.get("op"):
                        continue
                    pub = h.get("tipoPublicacion") or h.get("rubro") or "NL"
                    num = _http.clean(h.get("numeroDispositivo"))
                    items.append(LawHit(
                        id=f"{pub}/{h['op']}",
                        title=_law_title(h.get("tipoDispositivo") or "", num, h.get("sumilla") or "")[:400],
                        type=_http.clean(h.get("tipoDispositivo")),
                        number=re.sub(r"^N[º°o]\.?\s*", "", num),
                        date=_ymd(h.get("fechaPublicacion")),
                        status="as published",
                        snippet=_http.clean(h.get("distributor")),
                        url=f"{EP}/dispositivo/{pub}/{h['op']}"))
                if len(hits) < per or not res.get("hasNext"):
                    break
                start += per
            return items[:want], total

        async def run_pubs(params, want, first):
            # the site's type filter only works together with one publication, and laws are
            # published in the normal edition (NL) or an extraordinary one (EX): ask both
            if params.get("tipoDispositivo") and not params.get("tipoPublicacion"):
                got = [await run({**params, "tipoPublicacion": pub}, first + want, 0) for pub in ("NL", "EX")]
                items = sorted(got[0][0] + got[1][0], key=lambda h: h.date, reverse=True)
                tot = [t for _, t in got]
                return items[first:first + want], sum(tot) if all(isinstance(t, int) for t in tot) else None
            return await run(params, want, first)

        # a named law ("Ley de ..."): the site ranks by date, so look for it among LEY norms
        # containing the exact phrase and put the one titled with that phrase first
        num = re.fullmatch(r"ley\s+n?[º°o]?\.?\s*(\d{4,5})", q, re.I)
        named = bool(_NAMED_LAW.match(q) or num) and page == 1 and not (f.get("type") or f.get("publication"))
        found = False
        items: list[LawHit] = []
        total = None
        if named:
            items, total = await run_pubs({**params, "query": num[1] if num else f'"{q}"',
                                           "tipoDispositivo": "LEY"}, 60, 0)
            key = _fold(q)
            exact = [h for h in items if (h.number == num[1] if num else
                                          _fold(h.title.split(" — ", 1)[-1]).startswith(key))]
            found = bool(exact)
            items = (exact + [h for h in items if h not in exact])[:limit]
        if not items:
            items, total = await run_pubs(params, limit, (page - 1) * limit)
        # a law-number query: put the norm itself first (results are newest first)
        if m := re.search(r"\b(\d{3,5}(?:-\d{4}-[A-Z/-]+)?)\b", q):
            items.sort(key=lambda h: 0 if re.search(rf"\b{re.escape(m[1])}\b", h.number) else 1)
        note = ("Official gazette, newest first; texts are as published, not consolidated. "
                "Individual norms online from about 2009 (older ones only in daily booklets).")
        if named and not found:
            note += (f" No LEY {'numbered' if num else 'titled'} {q!r} was found in this source's index; that does "
                     "not show the law does not exist. Laws published before about 2009 (e.g. Ley 27444, "
                     "Ley 28611) are not online here as single norms, and a later law can be missing or be "
                     "titled differently. The hits are other norms that contain these words, not that law. "
                     "To look for a later law, filter by type=LEY and date_from/date_to around its year, "
                     "or search its number.")
        elif _CODE.match(q) and not any(f"aprueba el {_fold(q)}" in _fold(h.title) for h in items):
            note += (f" None of the hits is the {q!r} itself: the hits are norms that mention it (marriage "
                     "notices, amendments). The main codes were enacted before about 2009 and this source "
                     "does not return them as single norms; absence here does not mean the code does not exist. "
                     "Search the amending norms with type=DECRETO LEGISLATIVO or LEY.")
        if page == 1 and re.search(r"constituci[oó]n", q, re.I):
            items = [LawHit(id=CONST_ID, title="Constitución Política del Perú de 1993 (texto actualizado)",
                            type="Constitución", date="1993-12-30", status="in force (consolidated, Congress "
                            "official edition)", url=CONST_PDF)] + items[:max(limit - 1, 0)]
            note += " First hit: the Constitution, consolidated (id 'constitucion')."
        return Results(items, total=total if isinstance(total, int) else None, note=note)

    async def get_legislation_text(self, id):
        n = await _norm(id)
        return LawText(id=n["id"], title=n["title"], text=n["text"], url=n["url"], as_of=n["date"],
                       metadata={**n["meta"], "Nota": "texto publicado, no consolidado"})

    async def get_legislation_toc(self, id):
        n = await _norm(id)
        secs = _sections(n["paras"], not n.get("noquote"))
        entries = [TocEntry(title=_http.clean(h)[:200], level=0 if not lab else 1, provision=lab)
                   for lab, h, _ in secs]
        if not entries:
            entries = [TocEntry(title="Texto completo", provision="texto")]
        return Toc(id=n["id"], title=n["title"], url=n["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        n = await _norm(id)
        want = _prov_key(provision)
        note = "" if _is_const(id) else ("Norm as published in El Peruano, not consolidated: "
                                         "check later amending norms.")
        secs = _sections(n["paras"], not n.get("noquote"))
        if want == "texto" and not any(lab for lab, _, _ in secs):
            return Provision(law_id=n["id"], law_title=n["title"], provision="texto", text=n["text"],
                             url=n["url"], as_of=n["date"],
                             note=note)
        for k, (lab, _, i) in enumerate(secs):
            if not lab or _prov_key(lab) != want and _fold(lab) != _fold(_http.clean(provision)):
                continue
            end = next((j for lab2, _, j in secs[k + 1:]), len(n["paras"]))
            return Provision(law_id=n["id"], law_title=n["title"], provision=lab,
                             text="\n\n".join(n["paras"][i:end]), url=n["url"], as_of=n["date"],
                             note=note)
        labels = [lab for lab, _, _ in secs if lab]
        raise NotFound(f"No provision {provision!r} in {n['id']}. Available: "
                       f"{', '.join(labels[:30]) or 'none (use get_legislation_text)'}.")
