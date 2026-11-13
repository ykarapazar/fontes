"""Paraguay: laws from the Biblioteca y Archivo Central del Congreso Nacional (BACN,
www.bacn.gov.py) and Supreme Court decisions from the Corte Suprema de Justicia's
Sistema de Información de Jurisprudencia (www.csj.gov.py/jurisprudencia).

Gotchas this code encodes (verified 2026-11-06 from a UK IP):
  * BACN: a law page is /leyes-paraguayas/{id}/{any-slug}; the slug is ignored, but
    without one the site 302s to /error. An unknown id is HTTP 200 with the title
    "no contiene titulo" and no `entry-content` block.
  * BACN pages are mostly UTF-8 but carry stray cp1252 bytes (dates such as
    "Miércoles"), so bytes are decoded leniently (_decode).
  * BACN search: /buscar.php?j=si&s=... (the site's own typeahead) returns *every*
    full-text hit as JSON (title, category, id), across all site sections, in id
    order, not by relevance. We keep the "Leyes Paraguayas" hits, rank those whose
    title holds the query words (or the asked law number) first, then page locally.
  * BACN texts are the law as enacted (with the original PDF linked), not consolidated.
    Article headings vary: "Artículo 1°.-", "Art.1°.-", "ARTICULO 1 - TITLE",
    "Artículo 1.º". Quoted articles inside amending laws ("“Art. 207.-") are not
    split out. Big codes are split over several pages (Código Civil: 5293 = Título
    preliminar + Libro I, then 5299, 522, 524, 528 for Libros II-V).
  * CSJ is an ASP.NET MVC app: GET Home/Criterios (anti-forgery token + cookie), POST
    Home/Busqueda (stores the criteria in the ASP.NET session), then POST
    Jurisprudencias/GetData (DataTables server-side paging, JSON). The three steps run
    under one lock because the criteria live in the shared client's session cookie.
  * CSJ decisions: id = CodigoJurisprudencia. home/detalle?codigo=N (HTML fragment:
    metadata + "Análisis" headnotes) and home/DocumentoJurisprudencia?codigo=N (the
    decision itself: Word 97 .doc for older ones, PDF with the court's own text layer for
    recent ones). Neither needs the session.
  * CSJ search is accent-sensitive (its own FAQ says so); "@" = AND, "#" = OR.
"""
from __future__ import annotations

import asyncio
import datetime
import json
import re
import unicodedata
from urllib.parse import quote

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)
from .al import word_paragraphs  # OLE2 .doc / .docx reader (stdlib only)

BACN = "https://www.bacn.gov.py"
CSJ = "https://www.csj.gov.py/jurisprudencia"

_search_cache: dict[str, list[dict]] = {}
_law_cache: dict[str, dict] = {}
_csj_lock = asyncio.Lock()

_MONTHS = {m: i for i, m in enumerate(("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
                                        "agosto", "septiembre", "octubre", "noviembre", "diciembre"), 1)}
_MONTHS["setiembre"] = 9
_STOP = {"de", "del", "la", "el", "los", "las", "y", "que", "en", "por", "a", "o", "n", "no", "ley"}


def _fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", re.sub(r"[^\w]+", " ", s)).strip()


def _decode(b: bytes) -> str:
    """UTF-8 with stray cp1252 bytes (BACN mixes both)."""
    s = b.decode("utf-8", "surrogateescape")
    return re.sub(r"[\udc80-\udcff]+",
                  lambda m: bytes(ord(c) - 0xDC00 for c in m[0]).decode("cp1252", "replace"), s)


def _es_date(s: str) -> str:
    """'martes, 18 de diciembre de 2001' -> '2001-12-18'; else ''."""
    m = re.search(r"(\d{1,2})\s+de\s+([a-záéíóú]+)\s+de\s+(\d{4})", s or "", re.I)
    if not m or _fold(m[2]) not in _MONTHS:
        return ""
    try:
        return datetime.date(int(m[3]), _MONTHS[_fold(m[2])], int(m[1])).isoformat()
    except ValueError:
        return ""


def _slug(title: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", _fold(title))).strip("-")[:120] or "ley"


# --------------------------------------------------------------------------- #
# BACN (legislation)
# --------------------------------------------------------------------------- #
def _law_id(id: str) -> str:
    s = str(id or "").strip()
    m = re.search(r"bacn\.gov\.py/leyes-paraguayas/(\d+)", s, re.I) or re.fullmatch(r"(\d+)", s)
    if not m:
        raise BadRequest("Paraguay law ids are BACN document ids such as '2608' (Ley 213, Código del "
                         "Trabajo) or a www.bacn.gov.py/leyes-paraguayas/<id>/... URL; use "
                         f"search_legislation to find one. Got {id!r}.")
    return m[1]


def _law_url(lid: str, title: str = "") -> str:
    return f"{BACN}/leyes-paraguayas/{lid}/{_slug(title)}"


# BACN splits the Civil Code (Ley 1183/1985) into five records; each holds only some books.
_CIVIL = {"5293": "Libro Primero (arts. 1-188)", "5299": "Libro Segundo", "522": "Libro Tercero",
          "524": "Libro Cuarto", "528": "Libro Quinto"}
_CIVIL_NOTE = ("The Civil Code (Ley 1183/1985) is split by BACN into five records: "
               + "; ".join(f"{i} = {n}" for i, n in _CIVIL.items())
               + ". An article may be in a different record than the one you opened.")
# Ley 729/1961 was repealed by art. 412 of Ley 213/1993 (text read on BACN, 2026-11).
_OLD_LABOUR, _NEW_LABOUR = "2515", "2608"
_LABOUR_NOTE = ("Ley 729/1961 (id 2515) is the OLD Labour Code, repealed by art. 412 of Ley 213/1993 "
                "(id 2608), the current Labour Code (amended by Ley 496/1995 and later laws).")


def _law_parts(title: str) -> tuple[str, str]:
    """'Ley Nº 7701/2026 / QUE ...' -> ('Ley', '7701/2026')."""
    m = re.match(r"\s*(ley|decreto(?:[- ]ley)?|resoluci[oó]n)\s*n?[º°o]?\.?\s*([\d.]+(?:/\d{2,4})?)", title, re.I)
    return (m[1].capitalize(), m[2].replace(".", "")) if m else ("", "")


async def _bacn_get(url: str):
    try:
        r = await _http.get(url)
    except Exception as e:
        raise SourceError(f"BACN: {e}", "network") from e
    if r.status_code != 200:
        raise SourceError("BACN request failed", r.status_code)
    return r


_HEAD = re.compile(r"^(pre[aá]mbulo|parte|libro|t[ií]tulo|cap[ií]tulo|secci[oó]n)\b", re.I)
_ART = re.compile(r"^(?:\*\*)?\s*(?:art[ií]culo|art\.)\s*(\d+)\s*(?:bis|ter)?", re.I)


def _is_heading(p: str) -> bool:
    plain = p.replace("*", "").strip()
    return bool(_HEAD.match(plain)) and len(plain) < 200 and not _ART.match(plain)


async def _law(lid: str) -> dict:
    if lid in _law_cache:
        return _law_cache[lid]
    r = await _bacn_get(f"{BACN}/leyes-paraguayas/{lid}/ley")
    html = _decode(r.content)
    i = html.find('class="entry-content"')
    t = re.search(r"<h1 class=\"entry-title\">(.*?)</h1>", html, re.S)
    if i < 0 or not t:
        raise NotFound(f"BACN: no law with id {lid}.")
    title = _http.clean(re.sub(r"<[^>]+>", " ", t[1]))
    body = html[i:html.find('<footer class="entry-footer"', i)]
    meta = {}
    for k, v in re.findall(r"<strong>\s*Fecha de (Promulgaci[oó]n|Publicaci[oó]n):\s*</strong>\s*([\d-]+)", body):
        meta[_fold(k)] = _http.iso_date(v)
    pdfs = re.findall(r'href="(https?://www\.bacn\.gov\.py/descarga/[^"]+)"', body)
    body = re.sub(r"(?is)<iframe.*?</iframe>|<ol class=\"breadcrumb\">.*?</ol>|<h4>\s*<strong>Descargar.*?</h4>"
                  r"|<!--.*?-->", "", body)
    body = body[body.find(">") + 1:]
    paras = [p for p in _http.html_paragraphs(body) if p.strip("*_ ​")]
    paras = [p.replace("​", "").strip() for p in paras]
    # TOC: headings (joined with a following all-caps name line) and articles
    entries, arts, cur, seen = [], {}, None, set()
    k = 0
    while k < len(paras):
        p = paras[k]
        plain = p.replace("*", "").strip()
        m = _ART.match(plain)
        if m:
            label = m[1]
            n = 2
            while label in seen:
                label, n = f"{m[1]} ({n})", n + 1
            seen.add(label)
            cur = label
            arts[label] = [p]
            head = re.sub(r"^(?:art[ií]culo|art\.)\s*", "Artículo ", plain, flags=re.I)
            entries.append(TocEntry(title=_http.clean(head)[:120], level=2, provision=label))
        elif _is_heading(p):
            cur = None
            nxt = paras[k + 1].replace("*", "").strip() if k + 1 < len(paras) else ""
            if (len(plain.split()) <= 3 and nxt and not _ART.match(nxt) and not _is_heading(nxt)
                    and len(nxt) < 150 and not nxt.endswith((".", ":", ";"))):
                plain, k = f"{plain} – {nxt}", k + 1
            lvl = 0 if re.match(r"(parte|libro|pre)", _fold(plain)) else 1
            entries.append(TocEntry(title=plain, level=lvl))
        elif cur:
            arts[cur].append(p)
        k += 1
    law = {"id": lid, "title": title, "paras": paras, "entries": entries, "arts": arts,
           "meta": meta, "pdfs": pdfs, "url": _law_url(lid, title)}
    return _http.lru_put(_law_cache, lid, law, 8)


def _prov_label(law: dict, provision: str) -> str:
    s = _http.clean(provision)
    if s in law["arts"]:
        return s
    m = re.fullmatch(r"(?:art[ií]culo|art[sº]?\.?|arts?)?\s*(\d+)\s*[°º]?\.?(?:\s*\((\d+)\))?", s, re.I)
    if not m:
        raise BadRequest(f"Provision labels look like '5', 'Artículo 5' or 'art. 5'; got {provision!r}.")
    label = m[1] + (f" ({m[2]})" if m[2] else "")
    if label not in law["arts"]:
        raise NotFound(f"BACN: {law['title']} has no article {label} (see get_legislation_toc).")
    return label


# --------------------------------------------------------------------------- #
# CSJ (case law)
# --------------------------------------------------------------------------- #
_TYPES = {"2": "2", "acuerdo y sentencia": "2", "acuerdo": "2", "sentencia": "2", "ays": "2",
          "1": "1", "auto interlocutorio": "1", "auto": "1", "ai": "1"}
_COLS = ("CodigoJurisprudencia", "TipoResolucionJudicial.DescripcionTipoResolucionJudicial",
         "NoResolucionJudicial", "FechaResolucionJudicial", "CaratulaPublicacion",
         "Sala.DescripcionSala", "")


def _dmy(v: str, name: str) -> str:
    iso = _http.iso_date(v)
    if not iso:
        raise BadRequest(f"{name} must be a date like 2020-05-31 or 31/05/2020; got {v!r}.")
    y, m, d = iso.split("-")
    return f"{d}/{m}/{y}"


def _net_date(v) -> str:
    m = re.search(r"/Date\((-?\d+)\)/", str(v or ""))
    if not m or int(m[1]) < 0:
        return ""
    # midnight Asunción time = 03:00/04:00 UTC, so the UTC date is the local date
    return datetime.datetime.fromtimestamp(int(m[1]) / 1000, datetime.timezone.utc).date().isoformat()


async def _csj(method: str, path: str, **kw):
    try:
        r = await (_http.post if method == "POST" else _http.get)(f"{CSJ}/{path}", **kw)
    except Exception as e:
        raise SourceError(f"CSJ: {e}", "network") from e
    if r.status_code != 200:
        raise SourceError(f"CSJ {path} failed", r.status_code)
    return r


def _case_number(kind: str, num, date: str) -> str:
    return f"{kind} Nº {num}" + (f"/{date[:4]}" if date else "")


class Paraguay(Jurisdiction):
    code = "py"
    name = "Paraguay"
    languages = ("es",)
    aliases = ("paraguay", "republica del paraguay")
    sources = (
        Source(
            name="Biblioteca y Archivo Central del Congreso Nacional (BACN) – Leyes Paraguayas",
            url=f"{BACN}/leyes-paraguayas",
            covers=("legislation",),
            licence="unknown (no terms of use published; official public-sector site, laws are public)",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~20 requests (2026-11)",
            terms_url=f"{BACN}/",
            warning="Texts are the laws as enacted (BACN copy), not consolidated; check amending laws.",
        ),
        Source(
            name="Corte Suprema de Justicia – Sistema de Información de Jurisprudencia",
            url=f"{CSJ}/",
            covers=("caselaw",),
            licence="unknown (no terms of use published; official court site)",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1.5 s spacing, no 429 seen in ~25 requests (2026-11)",
            terms_url=f"{CSJ}/Home/PreguntasFrecuentes",
        ),
    )
    caselaw_filters = {
        "year": "Year of the decision, e.g. '2021' (1993-current).",
        "type": "'acuerdo y sentencia' (judgment) or 'auto interlocutorio' (interlocutory order).",
        "number": "Resolution number, digits only, e.g. '1032' (combine with year).",
        "date_from": "Earliest decision date, YYYY-MM-DD (use with date_to; replaces year).",
        "date_to": "Latest decision date, YYYY-MM-DD.",
        "materia": "Subject area as the court names it, e.g. 'Civil y Comercial', 'Penal', "
                   "'Constitucional', 'Laboral', 'Administrativa'.",
    }
    min_interval = {"www.bacn.gov.py": 1.0, "www.csj.gov.py": 1.5}
    notes = ("Constitution (BACN id 9580) and laws as enacted from the Congress library (BACN, not "
             "consolidated); Supreme Court decisions since 1993 with official headnotes. CSJ search is "
             "accent-sensitive.")
    gaps = (
        ("Consolidated legislation: BACN publishes laws only as enacted; no consolidated source "
         "researched yet"),
        ("Decrees and other subordinate regulations: only 'Leyes Paraguayas' are searched; not "
         "researched yet"),
        ("Appeal and first-instance courts: the CSJ database holds Supreme Court decisions only; "
         "not researched yet"),
        "Supreme Court decisions before the 1990s: not in the CSJ database (filter covers 1993 on)",
    )
    samples = {
        "caselaw_query": "usucapión",
        "decision_id": "278",
        "legislation_query": "codigo del trabajo",
        "law_id": "2608",
        "provision": "47",
    }

    # ----------------------------------------------------------- legislation
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        q = _http.clean(query)
        if len(q) < 2:
            raise BadRequest("Give at least two characters to search BACN.")
        key = q.lower()
        hits = _search_cache.get(key)
        if hits is None:
            # BACN titles read "Ley Nº 1183 / ..."; a literal "ley 1183" finds nothing, so
            # send just the number and let the law-number boost below rank it.
            lm = re.fullmatch(r"(?i)ley\s*(?:n[º°o.]*\s*)?(\d[\d.]*)", q)
            r = await _bacn_get(f"{BACN}/buscar.php?j=si&s={quote(lm[1].replace('.', '') if lm else q)}")
            try:
                data = json.loads(_decode(r.content) or "[]")
            except ValueError as e:
                raise SourceError("BACN: unexpected search reply", r.status_code) from e
            hits = [d for d in data if d.get("nombre_categoria") == "Leyes Paraguayas"]
            if "constitucion" in _fold(q) and not any(str(d.get("id_documento")) == "9580" for d in hits):
                # BACN's search for "Constitución Nacional" omits the Constitution (id 9580) entirely
                r2 = await _bacn_get(f"{BACN}/buscar.php?j=si&s={quote('Constitución de la República del Paraguay')}")
                try:
                    hits += [d for d in json.loads(_decode(r2.content) or "[]")
                             if str(d.get("id_documento")) == "9580"]
                except ValueError:
                    pass
            words = [w for w in _fold(q).split() if w not in _STOP]
            num = re.search(r"\b(\d[\d.]*)\b", q)
            num = num[1].replace(".", "") if num else ""

            def score(d):
                t = _fold(d.get("titulo_documento"))
                s = sum(1 for w in words if re.search(rf"\b{re.escape(w)}\b", t))
                if "constitucion" in words and t.startswith("constitucion de la republica"):
                    s += 10  # the Constitution itself, whatever the extra words ("nacional", ...)
                if num and _law_parts(d.get("titulo_documento", ""))[1].split("/")[0] == num:
                    s += 10
                return -s, str(d.get("id_documento")) == _OLD_LABOUR, len(t)
            hits = sorted(hits, key=score)
            _http.lru_put(_search_cache, key, hits, 16)
        start = (page - 1) * limit
        items = []
        for d in hits[start:start + limit]:
            title = _http.clean(d.get("titulo_documento"))
            kind, number = _law_parts(title)
            items.append(LawHit(id=str(d["id_documento"]), title=title, type=kind, number=number,
                                url=_law_url(str(d["id_documento"]), title)))
        ids = {i.id for i in items}
        extra = ""
        if ids & set(_CIVIL):
            extra += " " + _CIVIL_NOTE
        if _OLD_LABOUR in ids:
            extra += " " + _LABOUR_NOTE
        return Results(items=items, total=len(hits),
                       note="BACN full-text search; titles matching the query listed first. "
                            "Texts are as enacted, not consolidated." + extra)

    async def get_legislation_toc(self, id):
        law = await _law(_law_id(id))
        title = law["title"]
        if law["id"] in _CIVIL:
            title += f" [{_CIVIL[law['id']]}. {_CIVIL_NOTE}]"
        return Toc(id=law["id"], title=title, url=law["url"], entries=law["entries"])

    async def get_legislation_provision(self, id, provision):
        law = await _law(_law_id(id))
        if not law["arts"]:
            raise NotFound(f"BACN: no articles recognised in {law['title']}; use get_legislation_text.")
        try:
            label = _prov_label(law, provision)
        except NotFound:
            if law["id"] not in _CIVIL:
                raise
            for other in _CIVIL:  # the article may sit in another Civil Code record
                if other == law["id"]:
                    continue
                alt = await _law(other)
                try:
                    label = _prov_label(alt, provision)
                except NotFound:
                    continue
                return Provision(law_id=alt["id"], law_title=alt["title"], provision=label,
                                 text="\n\n".join(alt["arts"][label]), url=alt["url"])
            raise NotFound(f"BACN: no article {provision!r} in any of the five Civil Code records "
                           f"({', '.join(_CIVIL)}).")
        return Provision(law_id=law["id"], law_title=law["title"], provision=label,
                         text="\n\n".join(law["arts"][label]), url=law["url"])

    async def get_legislation_text(self, id):
        law = await _law(_law_id(id))
        text = "\n\n".join(law["paras"])
        if not text:
            raise NotFound(f"BACN: {law['title']} has no text on the page; see the PDF: "
                           + ", ".join(law["pdfs"]))
        meta = {"Promulgación": law["meta"].get("promulgacion", ""),
                "Publicación": law["meta"].get("publicacion", ""),
                "PDF": " ".join(law["pdfs"]),
                "Version": "as enacted (not consolidated)"}
        return LawText(id=law["id"], title=law["title"], text=text, url=law["url"],
                       metadata={k: v for k, v in meta.items() if v})

    # ---------------------------------------------------------------- caselaw
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        f = dict(filters or {})
        q = _http.clean(query)
        form = {"PalabrasTexto": q, "TipoResolucion": "", "Numero": "", "Anno": "", "RangoFecha": "",
                "NormasReferencia": ""}
        if f.get("type"):
            t = _TYPES.get(_fold(str(f["type"])))
            if not t:
                raise BadRequest("type must be 'acuerdo y sentencia' or 'auto interlocutorio'.")
            form["TipoResolucion"] = t
        if f.get("number"):
            n = str(f["number"]).replace(".", "").strip()
            if not n.isdigit():
                raise BadRequest(f"number must be digits only, e.g. '1032'; got {f['number']!r}.")
            form["Numero"] = n
        if f.get("year"):
            y = str(f["year"]).strip()
            if not re.fullmatch(r"(19|20)\d\d", y):
                raise BadRequest(f"year must look like 2021; got {f['year']!r}.")
            form["Anno"] = y
        if f.get("date_from") or f.get("date_to"):
            a = _dmy(f.get("date_from") or "1990-01-01", "date_from")
            b = _dmy(f.get("date_to") or _http.today(), "date_to")
            form["RangoFecha"], form["Anno"] = f"{a} - {b}", ""
        if not any(form.values()) and not f.get("materia"):
            raise BadRequest("Give a query or at least one filter (year, type, number, dates, materia).")
        dt = {"draw": "1", "start": str((page - 1) * limit), "length": str(limit),
              "order[0][column]": "3", "order[0][dir]": "desc", "search[value]": "", "search[regex]": "false"}
        for i, c in enumerate(_COLS):
            dt.update({f"columns[{i}][data]": c, f"columns[{i}][name]": "", f"columns[{i}][searchable]": "true",
                       f"columns[{i}][orderable]": "true", f"columns[{i}][search][value]": "",
                       f"columns[{i}][search][regex]": "false"})
        async with _csj_lock:
            r = await _csj("GET", "Home/Criterios")
            tok = re.search(r'name="__RequestVerificationToken" type="hidden" value="([^"]+)"', r.text)
            if not tok:
                raise SourceError("CSJ: search form changed (no anti-forgery token)", r.status_code)
            data: dict = {"__RequestVerificationToken": tok[1], **form}
            if f.get("materia"):
                block = re.search(r'name="Materias">(.*?)</select>', r.text, re.S)
                opts = {_fold(n): v for v, n in re.findall(r'<option value="(\d+)">([^<]*)</option>',
                                                           block[1] if block else "")}
                want = _fold(str(f["materia"]))
                ids = [v for n, v in opts.items() if want == n] or [v for n, v in opts.items() if want in n]
                if not ids:
                    raise BadRequest(f"Unknown materia {f['materia']!r}. Known: "
                                     + ", ".join(sorted(n.title() for n in opts)))
                data["Materias"] = ids
            await _csj("POST", "Home/Busqueda", data=data, headers={"X-Requested-With": "XMLHttpRequest"})
            r = await _csj("POST", "Jurisprudencias/GetData", data=dt,
                           headers={"X-Requested-With": "XMLHttpRequest"})
        try:
            res = r.json()
        except ValueError as e:
            raise SourceError("CSJ: unexpected search reply", r.status_code) from e
        items = []
        for x in res.get("data") or []:
            date = _net_date(x.get("FechaResolucionJudicial"))
            kind = _http.clean((x.get("TipoResolucionJudicial") or {}).get("DescripcionTipoResolucionJudicial"))
            sala = _http.clean((x.get("Sala") or {}).get("DescripcionSala"))
            num = _case_number(kind, x.get("NoResolucionJudicial"), date)
            items.append(DecisionHit(
                id=str(x["CodigoJurisprudencia"]),
                title=_http.clean(x.get("CaratulaPublicacion")) or f"Corte Suprema de Justicia {num}",
                court=f"Corte Suprema de Justicia – {sala.title()}" if sala else "Corte Suprema de Justicia",
                date=date, case_number=num,
                snippet=_http.clean(x.get("NormasReferencia")),
                url=f"{CSJ}/home/detalle?codigo={x['CodigoJurisprudencia']}"))
        return Results(items=items, total=res.get("recordsFiltered"),
                       note="CSJ search is accent-sensitive (try both spellings, joined with '#'); "
                            "'@' = AND. Sorted by decision date (newest first), NOT by relevance: the court "
                            "matches the word anywhere in the full text, so top hits may only quote it. "
                            "To narrow by subject use filters {\"materia\": \"Constitucional\"} (or Penal, Civil y Comercial, ...).")

    async def get_decision(self, id):
        cid = str(id or "").strip()
        m = re.search(r"codigo=(\d+)", cid) or re.fullmatch(r"(\d+)", cid)
        if not m:
            raise BadRequest(f"CSJ decision ids are numbers (CodigoJurisprudencia), e.g. '278'; got {id!r}.")
        cid = m[1]
        try:
            r = await _csj("GET", "home/detalle", params={"codigo": cid})
        except SourceError as e:
            if e.status == 500:  # CSJ answers an unknown codigo with HTTP 500
                raise NotFound(f"CSJ: no decision with code {cid} (CSJ returned HTTP 500).") from e
            raise
        html = r.text
        head = re.search(r"<h5[^>]*>(.*?)</h5>", html, re.S)
        if not head or "DocumentoJurisprudencia" not in html and "Análisis" not in html:
            raise NotFound(f"CSJ: no decision with code {cid}.")
        caratula = re.search(r"DocumentoJurisprudencia\?codigo=\d+\"[^>]*>.*?</a>\s*<b>(.*?)</b>", html, re.S)
        fields = {}
        for lab, val in re.findall(r'<label[^>]*>(.*?)</label>\s*<input[^>]*value="([^"]*)"', html, re.S):
            val = _http.clean(_http.html_to_md(val))
            fields[_http.clean(lab)] = "" if val.upper() == "N/A" else val
        date = _es_date(fields.get("Fecha resolución judicial", ""))
        kind = fields.get("Tipo resolución judicial", "")
        num = _case_number(kind, fields.get("Número resolución judicial", ""), date) if kind else \
            _http.clean(_http.html_to_md(head[1]))
        sala = fields.get("Sala", "")
        heads = []
        for li in re.findall(r'<li class="text-justify">(.*?)</li>', html, re.S):
            tags = [_http.clean(_http.html_to_md(b)) for b in re.findall(r"<b>(.*?)</b>", li, re.S)]
            res = re.search(r'<span class="resumen">(.*?)</span>', li, re.S)
            body = _http.html_to_md(res[1]) if res else ""
            if body:
                heads.append(f"**{' – '.join(t for t in tags if t)}**: {body}" if tags else body)
        normas = re.search(r"Normas de Referencia</h4>(.*?)</ul>", html, re.S)
        summary = "\n\n".join(heads)
        text, note = "", ""
        if "DocumentoJurisprudencia" in html:
            d = await _csj("GET", "home/DocumentoJurisprudencia", params={"codigo": cid})
            data = d.content
            try:
                if data[:4] == b"%PDF":
                    text = _http.pdf_text(data)
                elif data[:2] == b"PK" or data[:8] == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
                    text = "\n\n".join(word_paragraphs(data))
            except Exception:
                text = ""
            if not text:
                note = "The decision file has no readable text layer; only the official headnotes are shown."
        else:
            note = "The court lists no decision file; only the official headnotes are shown."
        if not text:
            text = (f"_{note}_\n\n" if note else "") + (summary or "(no text available)")
        meta = {k: v for k, v in fields.items() if v and k not in (
            "Fecha resolución judicial", "Número resolución judicial", "Tipo resolución judicial", "Sala")}
        if normas:
            meta["Normas de referencia"] = "; ".join(
                _http.clean(_http.html_to_md(a)) for a in re.findall(r"<a>(.*?)</a>", normas[1], re.S))
        meta["Documento original"] = f"{CSJ}/home/DocumentoJurisprudencia?codigo={cid}"
        title = _http.clean(_http.html_to_md(caratula[1])) if caratula else ""
        return Decision(
            id=cid, title=title or f"Corte Suprema de Justicia {num}", text=text,
            url=f"{CSJ}/home/detalle?codigo={cid}",
            court=f"Corte Suprema de Justicia – {sala.title()}" if sala else "Corte Suprema de Justicia",
            date=date, case_number=num, summary=summary, metadata=meta)
