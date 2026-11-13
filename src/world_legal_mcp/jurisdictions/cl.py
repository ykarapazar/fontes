"""Chile: consolidated legislation from BCN Ley Chile (Biblioteca del Congreso Nacional).

Gotchas this code encodes:
  * Search: nuevo.leychile.cl/servicios/Consulta/listaresultadosimple (JSON, no key),
    the backend of the Ley Chile site. Reply is [items, header, facets]; paging is
    itemsporpagina + npagina (the older `cantidad`/`page_num` are ignored), and
    header.totalitems is the hit count. Dates come as "30-MAY-2000" with Spanish
    month abbreviations (ENE, ABR, AGO, DIC).
  * Text: www.leychile.cl/Consulta/obtxml?opt=7&idNorma=N returns the latest
    consolidated version as one XML document (EsquemaIntercambioNorma). An unknown
    idNorma gives HTTP 200 with an empty body. There is no per-article endpoint,
    so the whole norm is fetched once and kept in a small in-memory cache
    (the Código Civil is ~3 MB).
  * Parts are nested EstructuraFuncional elements with tipoParte (Libro, Título,
    Artículo, ...), NombreParte (the article number) and TituloParte (heading).
    Texto is plain text, hard-wrapped at ~60 chars; a paragraph starts with an
    indented line.
  * "Doble Articulado": a decree that fixes the text of other laws holds them inside
    its own articles. The Código Civil (idNorma 172986) is DFL 1 of 2000, whose
    article 2 contains the Code; the Code's articles are named "2314 (DEL ART. 2)".
    Labels drop that suffix. When a number repeats, the largest embedded body
    (the Code) keeps the plain label ("Artículo 1") and the others keep the
    source's qualifier ("Artículo 1 (del art. 3)"); the decree's own articles
    become "Artículo 1 (de la norma)".
  * Transitory articles reuse numbers: they are labelled "Artículo 1 transitorio".
  * fechaVersion 2222-02-02 is BCN's marker for an amendment whose entry into force
    is deferred or not yet fixed. Such parts are flagged; as_of ignores the marker.
  * Texto is laid out in two columns: the law's text on the left and BCN's amendment
    notes ("LEY N° 19.611 Art. único Nº 2 D.O. 16.06.1999") in a right-hand margin that
    starts at column 12-70. _split_margin() separates the two; notes are shown apart
    from the text. Stray spaces inside words ("alg una") are in BCN's own text.
  * Search has no date sort, but fc_pb="2022 TO 2026" restricts by publication year.
  * Case law is not offered: juris.pjud.cl (Poder Judicial) robots.txt disallows
    every user agent (checked 2026-11-05).
"""
from __future__ import annotations

import html
import re
import unicodedata
from collections import Counter

from lxml import etree

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import LawHit, LawText, Provision, Results, Toc, TocEntry

SEARCH = "https://nuevo.leychile.cl/servicios/Consulta/listaresultadosimple"
XML = "https://www.leychile.cl/Consulta/obtxml"
_later: dict[str, str] = {}   # idNorma -> "later amending laws" note ("" = none found)
WEB = "https://www.bcn.cl/leychile/navegar"
NS = "{http://www.leychile.cl/esquemas}"
DEFERRED = "2222-02-02"

_MONTHS = {"ENE": 1, "FEB": 2, "MAR": 3, "ABR": 4, "MAY": 5, "JUN": 6, "JUL": 7,
           "AGO": 8, "SEP": 9, "SET": 9, "OCT": 10, "NOV": 11, "DIC": 12}
_cache: dict[str, dict] = {}


def _date(s) -> str:
    """'30-MAY-2000' (Spanish month) or ISO -> 'YYYY-MM-DD'; else ''."""
    s = str(s or "").strip()
    m = re.match(r"^(\d{1,2})-([A-Za-z]{3})-(\d{4})$", s)
    if m and m[2].upper() in _MONTHS:
        return f"{m[3]}-{_MONTHS[m[2].upper()]:02d}-{int(m[1]):02d}"
    return _http.iso_date(s)


def _norm_id(id: str) -> str:
    s = str(id or "").strip()
    m = re.search(r"idNorma=(\d+)", s, re.I) or re.fullmatch(r"(?:idNorma[:\s]*)?(\d+)", s, re.I)
    if not m:
        raise BadRequest(f"Ley Chile ids are the numeric idNorma, e.g. '172986' (Código Civil); got {id!r}.")
    return m[1]


def _url(nid: str, part: str = "") -> str:
    return f"{WEB}?idNorma={nid}" + (f"&idParte={part}" if part else "")


_MARGIN = re.compile(r"^(.*?\S)\s{5,}(\S.*)$")
# What a margin note looks like ("LEY N° 19.611 Art. único", "CPR Art. 19° N° 2", "D.O. 24.10.1980", "1° N° 5");
# keeps a wide-spaced table row in the text column from being taken for a note.
_NOTE = re.compile(r"D\.O\.|\bArt\b|\bN[°º]|\bL(?:EY|\.)|\bCPR\b|\b[dD][fFlLtT]|[úu]nico\b|\d{2}\.\d{2}\.\d{4}|^\d+[°º]")


_AMENDING = re.compile(r"^[^–]*–\s*(modifica|introduce modificaciones)\b", re.I)
_AMENDING_NOTE = (" Most hits here are acts that amend another law: the source ranks by full text and may not list the "
                  "base statute for a phrase query. Search the base law's number (e.g. 'ley 19628') to find it.")
_AMENDED_NO = re.compile(r"\bLEY\s+N[°º]?\s*(\d{1,2}\.?\d{3})\b", re.I)


def _amended_number(hits) -> str:
    """The law number most often named by the amending acts in a result list ('' if none)."""
    seen = Counter(_AMENDED_NO.search(h.title)[1].replace(".", "")
                   for h in hits if _AMENDING.match(h.title) and _AMENDED_NO.search(h.title))
    return seen.most_common(1)[0][0] if seen else ""


def _split_margin(raw: str) -> tuple[str, list[str]]:
    """Separate the text column from BCN's right-hand margin of amendment notes."""
    body, notes = [], []
    for line in (raw or "").splitlines():
        m = _MARGIN.match(line)
        if m and m.start(2) >= 12 and _NOTE.search(m[2]):
            body.append(m[1])
            notes.append(m[2].strip())
        elif line.strip() and len(line) - len(line.lstrip()) >= 10 and _NOTE.search(line):
            notes.append(line.strip())
        else:
            body.append(line)
    return "\n".join(body), notes


def _note_line(notes: list[str]) -> list[str]:
    n = _http.clean(" ".join(notes))
    return [f"> Notas de modificación (Ley Chile): {n}"] if n else []


def _paras(raw: str) -> list[str]:
    """Hard-wrapped Ley Chile text -> paragraphs (a new one starts at an indented line)."""
    out: list[str] = []
    for line in (raw or "").replace("\xa0", " ").splitlines():
        if not line.strip():
            if out and out[-1]:
                out.append("")
            continue
        if line[:1].isspace() or not out or not out[-1]:
            out.append(line.strip())
        else:
            out[-1] += " " + line.strip()
    return [_http.clean(p) for p in out if p.strip()]


_ORD = ("primero segundo tercero cuarto quinto sexto séptimo octavo noveno décimo undécimo duodécimo "
        "decimotercero decimocuarto decimoquinto decimosexto decimoséptimo decimoctavo decimonoveno vigésimo").split()
_ORD_NUM = {unicodedata.normalize("NFKD", w).encode("ascii", "ignore").decode(): str(i) for i, w in enumerate(_ORD, 1)}


def _ordinal_num(name: str) -> str:
    """'primero' -> '1' (acts number their articles with words); '' when the name is not an ordinal word."""
    m = re.match(r"^(\S+)((?:\s+\S+)*)$", unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode().lower().strip())
    return _ORD_NUM.get(m[1], "") if m and not m[2].strip() else ""


def _key(label: str) -> str:
    """Normalise a provision label for matching: 'Art. 2314º' == 'artículo 2314' == '2314'."""
    s = unicodedata.normalize("NFKD", re.sub(r"[º°ª]", " ", label or "")).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"(?<=\d)\.(?=\d{3}(?!\d))", "", s)  # thousands separator: 2.314 == 2314
    s = re.sub(r"[º°ª.]", " ", s)
    s = re.sub(r"^\s*(articulos?|arts?)\b", "", s)
    s = re.sub(r"\btrans(itorio|it)?\b", "transitorio", s)
    return re.sub(r"\s+", " ", s).strip()


def _meta(e, tag: str) -> str:
    md = e.find(NS + "Metadatos")
    return _http.clean(md.findtext(NS + tag)) if md is not None else ""


def _parts(e):
    box = e.find(NS + "EstructurasFuncionales")
    return box.findall(NS + "EstructuraFuncional") if box is not None else []


# --------------------------------------------------------------------------- #
# Parsing one norm
# --------------------------------------------------------------------------- #
_WORD = re.compile(r"[^\W\d_]+")
_PAIR = re.compile(r"(?<![^\W\d_])([^\W\d_]+)(?= ([^\W\d_]+)(?![^\W\d_]))")
_SUFFIX = ("ción", "ciones", "sión")


def _mend_splits(texts: list[str]) -> list[str]:
    """BCN's PDF-derived text has stray spaces inside words ('vid a', 'de recho'). Rejoin a pair when one half
    occurs nowhere else in the norm and the joined word does (or the right half is a -ción/-sión ending)."""
    freq: dict[str, int] = {}
    for t in texts:
        for w in _WORD.findall(t.lower()):
            freq[w] = freq.get(w, 0) + 1

    def mend(t: str) -> str:
        cuts = []
        for m in _PAIR.finditer(t):
            a, b = m[1].lower(), m[2].lower()
            rare = min(freq[a], freq[b]) <= 1
            if rare and (freq.get(a + b, 0) >= 1 or (b in _SUFFIX and freq[a] <= 1 and len(a) > 3)):
                cuts.append(m.end())
        for i in reversed(cuts):
            t = t[:i] + t[i + 1:]
        return t

    return [mend(t) for t in texts]


def _parse(nid: str, xml: bytes) -> dict:
    try:
        root = etree.fromstring(xml)
    except etree.XMLSyntaxError as e:
        raise SourceError(f"Ley Chile: unreadable XML for idNorma {nid}", 200) from e
    boxes = [e for e in root.iter(NS + "Texto") if e.text]
    for e, t in zip(boxes, _mend_splits([e.text for e in boxes])):
        e.text = t
    ident = root.find(NS + "Identificador")
    tn = ident.find(f"{NS}TiposNumeros/{NS}TipoNumero") if ident is not None else None
    kind = _http.clean(tn.findtext(NS + "Tipo")) if tn is not None else ""
    number = _http.clean(tn.findtext(NS + "Numero")) if tn is not None else ""
    md = root.find(NS + "Metadatos")
    long_title = _http.clean(md.findtext(NS + "TituloNorma")) if md is not None else ""
    common = _http.clean(md.findtext(f"{NS}NombresUsoComun/{NS}NombreUsoComun")) if md is not None else ""
    title = " ".join(x for x in (kind, number) if x)
    title = f"{title} – {long_title or common}" if title else (long_title or common or f"idNorma {nid}")

    # Walk the tree: nodes = [(depth, element, owner_top_article_or_None, in_nested_body)]
    nodes: list[tuple[int, object, str, bool]] = []

    def walk(e, depth, top, nested):
        for p in _parts(e):
            nodes.append((depth, p, top, nested))
            is_top_art = depth == 0 and p.get("tipoParte") == "Artículo"
            walk(p, depth + 1, (_meta(p, "NombreParte").split(" ")[0] if is_top_art else top),
                 nested or p.get("tipoParte") == "Doble Articulado")

    walk(root, 0, "", False)
    arts = [(d, p, top, nested) for d, p, top, nested in nodes if p.get("tipoParte") == "Artículo"]
    # The largest embedded body (e.g. the Code inside a DFL) wins plain labels on clashes.
    sizes: dict[str, int] = {}
    for _, _, top, nested in arts:
        if nested:
            sizes[top] = sizes.get(top, 0) + 1
    primary = max(sizes, key=sizes.get) if sizes else None

    def base(p) -> str:
        name = re.sub(r"\s*\(DEL ART\.?\s*[^)]*\)\s*$", "", _meta(p, "NombreParte"), flags=re.I)
        if not name:
            return ""
        return f"Artículo {name}" + (" transitorio" if p.get("transitorio") == "transitorio" else "")

    count: dict[str, int] = {}
    for _, p, _, _ in arts:
        b = base(p)
        count[b] = count.get(b, 0) + 1
    labels: dict = {}
    used: set[str] = set()
    for _, p, top, nested in arts:
        b = base(p)
        if not b:
            lab = f"idParte {p.get('idParte')}"
        elif count[b] == 1 or (nested and top == primary):
            lab = b
        elif nested:
            lab = f"{b} (del art. {top})"
        else:
            lab = f"{b} (de la norma)"
        if lab in used:
            lab = f"{lab} [idParte {p.get('idParte')}]"
        used.add(lab)
        labels[p] = lab

    versions = [p.get("fechaVersion", "") for _, p, _, _ in nodes] + [root.get("fechaVersion", "")]
    real = [v for v in versions if v and v != DEFERRED]
    as_of = root.get("fechaVersion", "")
    if as_of == DEFERRED or not as_of:
        as_of = max(real) if real else ""

    lookup: dict[str, object] = {}
    for _, p, _, _ in arts:
        lab = labels[p]
        lookup.setdefault(_key(lab), p)
    for _, p, _, _ in arts:  # the source's own name, e.g. "2314 (DEL ART. 2)"
        raw = _meta(p, "NombreParte") + (" transitorio" if p.get("transitorio") == "transitorio" else "")
        lookup.setdefault(_key(raw), p)
    for _, p, _, _ in arts:  # 'Artículo primero' is also reachable as 'Artículo 1'
        if n := _ordinal_num(_meta(p, "NombreParte")):
            lookup.setdefault(n + (" transitorio" if p.get("transitorio") == "transitorio" else ""), p)

    return {"id": nid, "title": title, "root": root, "nodes": nodes, "labels": labels,
            "lookup": lookup, "as_of": as_of, "url": _url(nid),
            "repealed": root.get("derogado") == "derogado"}


def _flags(p) -> str:
    f = []
    if p.get("derogado") == "derogado":
        f.append("derogado")
    if p.get("fechaVersion") == DEFERRED:
        f.append("modificación con vigencia diferida")
    return f" ({', '.join(f)})" if f else ""


def _heading(p) -> str:
    return _meta(p, "TituloParte") or _meta(p, "NombreParte") or p.get("tipoParte", "")


def _own_text(p) -> tuple[list[str], list[str]]:
    """A part's paragraphs plus those of its non-article descendants (not nested articles),
    and BCN's amendment notes from the margin."""
    raw, notes = _split_margin(p.findtext(NS + "Texto") or "")
    out = _paras(raw)
    for c in _parts(p):
        if c.get("tipoParte") != "Artículo":
            o, n = _own_text(c)
            out, notes = out + o, notes + n
    return out, notes


def _amends(root) -> str:
    """Name of the law this norm amends when its first article only modifies another law, else ''."""
    for p in _parts(root):
        if p.get("tipoParte") == "Artículo":
            m = re.search(r"modificaciones?\s+en\s+(?:el|la)\s+(.{3,80}?)(?:,|:|\.\s)",
                          (p.findtext(NS + "Texto") or "")[:600].replace("\n", " "), re.I)
            return re.sub(r"\s+", " ", m[1]) if m else ""
    return ""


# --------------------------------------------------------------------------- #
class Chile(Jurisdiction):
    code = "cl"
    name = "Chile"
    languages = ("es",)
    aliases = ("chile", "chl")
    sources = (
        Source(
            name="BCN Ley Chile (Biblioteca del Congreso Nacional)",
            url="https://www.bcn.cl/leychile/",
            covers=("legislation",),
            licence=("Legal texts are excluded from copyright (Ley 17.336 art. 11 b); bcn.cl portal "
                     "metadata declares CC BY-SA 3.0 CL; no Ley Chile terms page found"),
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit=("unknown; 1 s spacing, no 429 seen in ~15 requests (2026-11-05); "
                        "no robots.txt on leychile.cl / bcn.cl"),
            terms_url="https://www.bcn.cl/portal/pagina/privacidad",
        ),
    )
    min_interval = {"nuevo.leychile.cl": 1.0, "www.leychile.cl": 1.0}
    notes = ("Consolidated national legislation (laws, DFL, decrees) from BCN Ley Chile, latest version. "
             "No case law: the Poder Judicial search (juris.pjud.cl) disallows all robots.")
    gaps = (
        "Case law (all Poder Judicial courts, incl. Corte Suprema): juris.pjud.cl robots.txt disallows all (2026-11-05)",
        "Tribunal Constitucional decisions: not researched yet",
        "Earlier versions of a norm: only the latest consolidated version is fetched; not built",
    )
    legislation_filters = {
        "year_from": "first year of publication in the Diario Oficial, e.g. 2022",
        "year_to": "last year of publication, e.g. 2025 (default: no upper limit)",
    }
    samples = {
        "legislation_query": "código civil",
        "law_id": "172986",
        "provision": "Artículo 2314",
    }

    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        q = (query or "").strip()
        if not q:
            raise BadRequest("Give search words, e.g. 'código del trabajo' or 'ley 19628'.")
        params = {"cadena": q, "exacta": "0", "tipoviene": "1",
                  "itemsporpagina": str(max(1, int(limit))), "npagina": str(max(1, int(page)))}
        yf, yt = (re.match(r"\d{4}", str((filters or {}).get(k) or "").strip()) for k in ("year_from", "year_to"))
        if yf or yt:
            params["fc_pb"] = f"{yf[0] if yf else 1810} TO {yt[0] if yt else 2100}"
        try:
            r = await _http.get(SEARCH, params=params)
        except Exception as e:
            raise SourceError(f"Ley Chile search: {e}", "network") from e
        if r.status_code != 200:
            raise SourceError("Ley Chile search failed", r.status_code)
        try:
            data = r.json()
            items, header = data[0], data[1]
        except (ValueError, IndexError, KeyError, TypeError) as e:
            raise SourceError("Ley Chile search: unexpected reply", r.status_code) from e
        hits = []
        for it in items[: int(limit)]:
            nid = str(it.get("IDNORMA") or "")
            if not nid:
                continue
            norma, full = _http.clean(it.get("NORMA")), _http.clean(it.get("TITULO_NORMA"))
            common = _http.clean(it.get("NOMBRES_USO_COMUN"))
            title = f"{norma} – {common or full}" if norma else (common or full)
            rep = _date(it.get("FECHA_DEROGACION"))
            hits.append(LawHit(
                id=nid, title=title, type=_http.clean(it.get("DESCRIPCION")),
                number=_http.clean(it.get("NUMERO")),
                date=_date(it.get("FECHA_PUBLICACION")) or _date(it.get("FECHA_PROMULGACION")),
                status=(f"derogada {rep}" if rep else ("derogada" if it.get("FECHA_DEROGACION") else "")),
                snippet=_http.clean(html.unescape(re.sub(r"<[^>]+>", " ", str(it.get("RESUMEN") or ""))))[:300],
                url=_url(nid)))
        base_note, base_id = "", ""
        num = _amended_number(hits)
        if num and sum(bool(_AMENDING.match(h.title)) for h in hits) * 2 >= len(hits) and not any(h.number == num for h in hits):
            try:
                rb = await _http.get(SEARCH, params={**params, "cadena": f"ley {num}", "itemsporpagina": "5", "npagina": "1"})
                top = next((x for x in rb.json()[0] if str(x.get("NUMERO")) == num and x.get("IDNORMA")), None)
            except Exception:
                top = None
            if top:
                base_id = str(top["IDNORMA"])
                norma, full = _http.clean(top.get("NORMA")), _http.clean(top.get("TITULO_NORMA"))
                hits.insert(0, LawHit(id=base_id, title=f"{norma} – {_http.clean(top.get('NOMBRES_USO_COMUN')) or full}",
                                      type=_http.clean(top.get("DESCRIPCION")), number=num,
                                      date=_date(top.get("FECHA_PUBLICACION")) or _date(top.get("FECHA_PROMULGACION")),
                                      status="", snippet="", url=_url(base_id)))
                del hits[max(1, int(limit)):]
                base_note = f" Hit 1 (Ley {num}) was added because most results amend it; it is the base statute."
        qk = _key(q)  # the source ranks by full-text hits; list titles containing the query first
        hits.sort(key=lambda h: (h.id != base_id, qk not in _key(h.title)))
        total = header.get("totalitems") if isinstance(header, dict) else None
        return Results(items=hits, total=int(total) if isinstance(total, (int, str)) and str(total).isdigit() else None,
                       note=("Ley Chile full-text search; ids are idNorma numbers (Código Civil = 172986). "
                             "Within a page, titles containing the whole query are listed first. "
                             "Filters year_from / year_to limit by publication year."
                             + base_note + _AMENDING_NOTE * (sum(bool(_AMENDING.match(h.title)) for h in hits) * 2 >= len(hits) > 0)))

    async def _law(self, id) -> dict:
        nid = _norm_id(id)
        if nid in _cache:
            return _cache[nid]
        try:
            r = await _http.get(XML, params={"opt": "7", "idNorma": nid})
        except Exception as e:
            raise SourceError(f"Ley Chile text: {e}", "network") from e
        if r.status_code == 404 or (r.status_code == 200 and not r.content.strip()):
            raise NotFound(f"Ley Chile: no norm with idNorma {nid}")
        if r.status_code != 200:
            raise SourceError("Ley Chile text failed", r.status_code)
        if not r.content.lstrip().startswith(b"<?xml") and b"<Norma" not in r.content[:500]:
            raise SourceError("Ley Chile text: unexpected non-XML reply", r.status_code)
        return _http.lru_put(_cache, nid, _parse(nid, r.content), 4)

    async def _later_amenders(self, law) -> str:
        """Laws published after the text's date that say they amend it. Ley Chile's consolidated text
        leaves out amendments it has not yet consolidated (e.g. Ley 21.719 on Ley 19.628)."""
        m = re.match(r"(Ley|Decreto con Fuerza de Ley|DFL)\s+(\d{3,6})\b", law["title"], re.I)
        if not m or not law["as_of"]:
            return ""
        if law["id"] in _later:
            return _later[law["id"]]
        num = m[2]
        dotted = f"{num[:-3]}.{num[-3:]}"
        try:
            hits = (await self.search_legislation(f"ley {num}", limit=20,
                                                  filters={"year_from": law["as_of"][:4]})).items
        except Exception:
            return ""   # best effort; not cached so a later call retries
        found = [h for h in hits if h.id != law["id"] and (h.date or "") > law["as_of"]
                 and re.match(r"(Ley|Decreto Ley|Decreto con Fuerza de Ley|DFL)\b", h.title)
                 and re.search(r"modific", f"{h.title} {h.snippet}", re.I)
                 and re.search(rf"\b(?:{num}|{re.escape(dotted)})\b", f"{h.title} {h.snippet}")]
        out = "; ".join(f"{h.title.split(' – ')[0]} ({h.date}, id {h.id})" for h in found[:3])
        if out:
            out = (f"Published after this text's date ({law['as_of']}) and say they amend it: {out}. "
                   "Ley Chile's consolidated text may not include those changes yet (for example ones with a later "
                   "start date); read the amending law before relying on this text.")
        return _http.lru_put(_later, law["id"], out, 200)

    async def get_legislation_toc(self, id):
        law = await self._law(id)
        entries = []
        for depth, p, _, _ in law["nodes"]:
            kind = p.get("tipoParte")
            if kind == "Artículo":
                lab = law["labels"][p]
                extra = _meta(p, "TituloParte")
                num = _ordinal_num(_meta(p, "NombreParte"))
                tr = " transitorio" if p.get("transitorio") == "transitorio" else ""
                entries.append(TocEntry(title=lab + (f" (= Artículo {num}{tr})" if num else "")
                                        + (f" – {extra}" if extra else "") + _flags(p),
                                        level=depth, provision=lab))
            elif kind != "Doble Articulado":
                entries.append(TocEntry(title=_heading(p) + _flags(p), level=depth))
        return Toc(id=law["id"], title=law["title"], url=law["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        law = await self._law(id)
        p = law["lookup"].get(_key(provision))
        if p is None:
            raise NotFound(f"Ley Chile {law['id']}: no article {provision!r}. "
                           f"Use labels from get_legislation_toc, e.g. 'Artículo 1' or '1 transitorio'.")
        lab = law["labels"][p]
        body, margin = _own_text(p)
        if not any(x.strip() for x in body) and p.get("derogado") != "derogado":
            raise SourceError(f"Ley Chile {law['id']}: article {lab!r} came back with no text "
                              "(the source may have sent an incomplete document); try again shortly.", 200)
        body += _note_line(margin)
        note = []
        if p.get("derogado") == "derogado":
            note.append("> Derogado (repealed) according to Ley Chile.")
        if p.get("fechaVersion") == DEFERRED:
            note.append("> Ley Chile marks this text as an amendment with deferred entry into force.")
        if later := await self._later_amenders(law):
            note.append("> " + later)
        text = "\n\n".join([f"## {lab}"] + note + body)
        return Provision(law_id=law["id"], law_title=law["title"], provision=lab, text=text,
                         url=_url(law["id"], p.get("idParte", "")), as_of=law["as_of"])

    async def get_legislation_text(self, id):
        law = await self._law(id)
        root = law["root"]
        out = _paras(root.findtext(f"{NS}Encabezado/{NS}Texto") or "")
        for depth, p, _, _ in law["nodes"]:
            kind = p.get("tipoParte")
            if kind == "Artículo":
                out.append(f"{'#' * min(6, depth + 2)} {law['labels'][p]}{_flags(p)}")
                raw, notes = _split_margin(p.findtext(NS + "Texto") or "")
                out += _paras(raw) + _note_line(notes)
            elif kind == "Doble Articulado":
                out += _paras(p.findtext(NS + "Texto") or "")
            else:
                out.append(f"{'#' * min(6, depth + 2)} {_heading(p)}{_flags(p)}")
                paras = _paras(p.findtext(NS + "Texto") or "")
                if _key(" ".join(paras)) != _key(_heading(p)):
                    out += paras
        out += _paras(root.findtext(f"{NS}Promulgacion/{NS}Texto") or "")
        for a in root.iter(NS + "Anexo"):
            out += _paras(a.findtext(NS + "Texto") or "")
        meta = {"Tipo y número": law["title"].split(" – ")[0]}
        if law["repealed"]:
            meta["Estado"] = "derogada"
        if amended := _amends(root):
            target = ""
            if m := re.search(r"N[°º]\s*(\d{1,2}\.?\d{3})", amended):
                num = m[1].replace(".", "")
                try:  # best effort: name the amended law's idNorma so it can be fetched directly
                    for h in (await self.search_legislation(num, limit=10)).items:
                        if h.number.replace(".", "") == num and h.type.lower().startswith("ley"):
                            target = f" (consolidated text: id {h.id})"
                            break
                except Exception:
                    pass
            meta["Nota"] = (f"This act mainly amends {amended}{target}; its articles are the amending text, not that "
                            "law's consolidated text (find the amended law with search_legislation if no id is given). "
                            "Articles are labelled with the source's ordinals, e.g. 'Artículo primero'.")
        if later := await self._later_amenders(law):
            meta["Later amendments"] = later
        return LawText(id=law["id"], title=law["title"], text="\n\n".join(out), url=law["url"],
                       as_of=law["as_of"], metadata=meta)

