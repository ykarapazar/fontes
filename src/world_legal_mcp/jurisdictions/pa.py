"""Panama: legislation and Supreme Court rulings from Legispan, the Asamblea Nacional's
legislative database (legispan.asamblea.gob.pa).

Gotchas this code encodes (verified 2026-11-06 from a UK IP):
  * Legispan is an Angular app over a JSON API at /api/search. GET /api/search/norm
    takes page, limit, q (Typesense full text over title + text), type[type],
    number, authority[authority], publishedAt_start / publishedAt_end (YYYY-MM-DD);
    it answers {count, page, limit, data: [{original: {...}, highlights}]}.
    With q the order is relevance; without q we sort newest first.
  * GET /api/search/norm/{uuid} gives one record with `content` (the text layer of the
    norm's PDF), `normUrl` (PDF) and `lawUrl` (the norm cut out of the Gaceta, PDF).
    An unknown uuid answers HTTP 500, not 404.
  * Records are the texts as published in the Gaceta Oficial, one per norm, not
    consolidated; "TEXTO UNICO" records are the official consolidated texts.
  * `content` is empty for most older records; we then read the PDF's text layer
    (s3-legispan.asamblea.gob.pa). Old scans have no text layer: no OCR, we say so.
    Some recent records' `content` is the whole Gaceta issue, not just the norm.
  * Court rulings published in the Gaceta (type FALLO, ~1,000, mostly Corte Suprema
    Pleno unconstitutionality rulings and Sala Tercera nullity rulings, and SENTENCIA)
    are served as case law. Their text is the Gaceta's own OCR layer: expect typos.
  * robots.txt: none (the app answers /robots.txt with its index page; the S3 host
    answers AccessDenied). Terms: only a privacy policy (/privacy-policy), silent on
    automated access.
  * Not used: gacetaoficial.gob.pa (Incapsula bot challenge), www.organojudicial.gob.pa
    (WAF 403 to this client), www.asamblea.gob.pa (TLS chain missing the Sectigo
    intermediate).
"""
from __future__ import annotations

import re
import unicodedata

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc, TocEntry

HOST = "https://legispan.asamblea.gob.pa"
API = f"{HOST}/api/search/norm"
CASE_TYPES = ("FALLO", "SENTENCIA")
_UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)
_ART = re.compile(r"^(?:ART[IÍ]CULO|Art[ií]culo)\s+(\d+)\s*([A-Za-z]{0,6})?\s*[.:\-–—º°]", re.M)
_HEAD = re.compile(r"^(T[IÍ]TULO|CAP[IÍ]TULO|SECCI[OÓ]N|LIBRO|PARTE)\b|^(DISPOSICIONES [A-ZÁÉÍÓÚ ]+)$", re.I)
_NOISE = re.compile(
    r"^(No\.\s*\d+[\s-]*[A-Z]?\s*Gaceta Oficial Digital,.*|Gaceta Oficial Digital|"
    r"Para verificar la autenticidad de una representaci[oó]n.*|en el sitio web www\.gacetaoficial\.gob\.pa.*|"
    r"GO[0-9A-F]{12,14}|G\.O\.\s*\d+[\s-]*[A-Z]?)$")
_PINNED = (("codigo de trabajo", "DECRETO DE GABINETE", "252", 1971, "Código de Trabajo"),
           ("codigo fiscal", "LEY", "8", 1956, "Código Fiscal"))
_LAWQ = re.compile(r"^\s*(ley|decreto ejecutivo|decreto ley|decreto de gabinete|decreto|acuerdo|resoluci[oó]n|"
                   r"texto [uú]nico|fallo)?\s*(?:n[°º.o]*\s*)?(\d{1,6})\s*(?:de\s*(?:\d{1,2}\s+de\s+\w+\s+de\s+)?(\d{4}))?\s*$", re.I)
_START = re.compile(r"^[ÓO]RGANO JUDICIAL\s*$")
_END = re.compile(r"^ES (?:FIEL )?COPIA\b|^REP[UÚ]BLICA DE PANAM[AÁ]\s*$")
CONSTITUTION_ID = "fa4ac4d2-e118-492d-8b39-9002c0b2046e"  # Texto Único de la Constitución Política (2004)
_cache: dict[str, dict] = {}


def _fold(s) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", str(s or "").lower()) if not unicodedata.combining(c))


def _words(s, size=5) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", _fold(s)) if len(w) >= size}


def _ruling(raw: str, title: str) -> str:
    """The Gaceta issue holds many norms; cut out the one ruling whose title matches best
    (rulings start at 'ÓRGANO JUDICIAL' and end at 'ES COPIA AUTENTICA' or the next norm).
    Returns '' when it cannot be told apart."""
    lines = raw.replace("\r", "").split("\n")
    starts = [i for i, ln in enumerate(lines) if _START.match(ln.strip())]
    want = _words(title)
    best, best_score = "", 0.0
    for k, a in enumerate(starts):
        stop = starts[k + 1] if k + 1 < len(starts) else len(lines)
        for j in range(a + 1, stop):
            ln = lines[j].strip()
            if _END.match(ln):
                nxt = [x.strip() for x in lines[j + 1:j + 8] if x.strip()][:2]
                if ln.startswith("ES") or not any(_START.match(x) for x in nxt):
                    stop = j + 1
                    break
        seg = "\n".join(lines[max(a - 1, 0):stop])
        have = _words(seg)
        score = len(want & have) / len(want) if want else 0
        if score > best_score:
            best, best_score = seg, score
    return best if best_score >= 0.6 else ""


def _url(id: str) -> str:
    return f"{HOST}/norms/{id}"


def _norm_id(id) -> str:
    m = _UUID.search(str(id or ""))
    if not m:
        raise BadRequest("Panamanian ids are Legispan record ids (UUIDs), e.g. "
                         "'54406cf4-9654-41b4-8654-6bb94f67f429' (Ley 81 de 2019), or a "
                         f"legispan.asamblea.gob.pa/norms/<id> link; got {id!r}.")
    return m[0].lower()


def _date(s) -> str:
    return _http.iso_date(str(s or "")[:10])


def _reflow(raw: str) -> str:
    """PDF text layer -> paragraphs: drop Gaceta page furniture, rejoin wrapped lines."""
    lines = [_http.clean(ln) for ln in raw.replace("\r", "").split("\n")]
    # Legispan's PDF cover sheet ends with "Palabras Claves:" in the first lines.
    head = next((i for i, ln in enumerate(lines[:40]) if ln.startswith("Palabras Claves")), -1)
    lines = lines[head + 1:]
    paras: list[str] = []
    cur, gap = "", False
    for ln in lines:
        if _NOISE.match(ln) or re.fullmatch(r"\d{1,4}|\\? ?\.\.\.", ln):  # page furniture, page numbers
            continue
        if not ln:
            gap = True  # blank line: paragraph or page break; decided by the next line
            continue
        new = (not cur or _ART.match(ln) or _HEAD.match(ln) or re.match(r"^(\d{1,3}|[a-z])[.)]\s", ln)
               or (cur[-1] in ".:;" and (gap or ln[0].isupper() or ln[0] in "\"“«")))
        gap = False
        if new:
            if cur:
                paras.append(cur)
            cur = ln
        else:
            cur = cur[:-1] + ln if cur.endswith("-") and ln[:1].islower() else f"{cur} {ln}"
    if cur:
        paras.append(cur)
    return "\n\n".join(re.sub(r"\s{2,}", " ", p) for p in paras)


def _articles(text: str) -> list[tuple[str, int, int]]:
    """[(label, start, end)] of the law's own articles. Quoted articles inside an
    amending provision are skipped: an article number is accepted only when it is the
    next one expected (or a bis/ter of the last), or when the expected one never comes."""
    cands = [(m.start(), int(m[1]), (m[2] or "").lower()) for m in _ART.finditer(text)]
    out: list[tuple[str, int]] = []
    last = 0
    for i, (pos, n, suf) in enumerate(cands):
        later = {c[1] for c in cands[i + 1:]}
        if suf and suf not in ("bis", "ter", "quater", "a", "b", "c"):
            suf = ""
        if suf and n == last:
            out.append((f"{n} {suf}", pos))
        elif not suf and (n == last + 1 or (n > last + 1 and (last + 1) not in later)):
            out.append((str(n), pos))
            last = n
    return [(lab, pos, out[k + 1][1] if k + 1 < len(out) else len(text)) for k, (lab, pos) in enumerate(out)]


def _key(label: str) -> str:
    s = _http.clean(label).lower().replace("º", "").replace("°", "")
    s = re.sub(r"^(art[ií]culo|art\.?)\s*", "", s).strip(" .-")
    m = re.fullmatch(r"(\d+)\s*-?\s*([a-z]*)", s)
    return f"{int(m[1])} {m[2]}".strip() if m else s


async def _record(id: str) -> dict:
    r = await _http.get(f"{API}/{id}")
    if r.status_code in (404, 500):
        raise NotFound(f"No Legispan record {id} (the source answers HTTP {r.status_code} for unknown ids).")
    if r.status_code != 200:
        raise SourceError(_http.error("Legispan", "record request failed", r.status_code), r.status_code)
    try:
        return r.json()
    except ValueError as e:
        raise SourceError("Legispan: unexpected non-JSON reply", r.status_code) from e


async def _pdf(url: str) -> str:
    r = await _http.get(url)
    if r.status_code != 200 or not r.content.startswith(b"%PDF"):
        raise SourceError(_http.error("Legispan", f"PDF not available ({url})", r.status_code), r.status_code)
    return _http.pdf_text(r.content)


async def _load(id) -> dict:
    id = _norm_id(id)
    if id in _cache:
        return _cache[id]
    o = await _record(id)
    raw = o.get("content") or ""
    whole_issue = "CONTENIDO" in raw[:2500]  # `content` is the whole Gaceta issue, not the norm
    if len(raw.strip()) < 200 or whole_issue:
        for u in (o.get("normUrl"), o.get("lawUrl")):
            if u:
                try:
                    pdf = await _pdf(u)
                except SourceError:
                    continue
                if len(pdf) > 1500:  # more than the Legispan cover sheet
                    raw = pdf
                    break
    isolated = False
    if whole_issue or "CONTENIDO" in raw[:2500]:
        if _type(o) in CASE_TYPES and (seg := _ruling(raw, _http.clean(o.get("title")))):
            raw, isolated = seg, True
    text = _reflow(raw)
    if len(text) < 200:
        hint = ""
        if _type(o) == "CONSTITUCION POLITICA":
            hint = f" The Constitution in force is the Texto Único of 2004: {CONSTITUTION_ID} (this record is an earlier version)."
        raise SourceError(f"Legispan record {id} has no text layer (scanned PDF; this server does no OCR).{hint} "
                          f"Read the PDF: {o.get('normUrl') or _url(id)}", 200)
    return _http.lru_put(_cache, id, {"o": o, "text": text, "isolated": isolated}, 6)


def _type(o: dict) -> str:
    return _http.clean((o.get("type") or {}).get("type"))


def _authority(o: dict) -> str:
    return _http.clean((o.get("authority") or {}).get("authority"))


def _law_title(o: dict) -> str:
    t, num, yr = _type(o), _http.clean(o.get("number")), o.get("year") or ""
    title = _http.clean(o.get("title"))
    lead = f"{t.title()} {num} de {yr}".strip() if num else t.title()
    return f"{lead}: {title}" if title else lead


def _case_number(o: dict) -> str:
    return _http.clean(o.get("nomenclature")) or _http.clean(o.get("number"))


def _snip(h: dict) -> str:
    for x in h.get("highlights") or []:
        s = x.get("snippet") or ""
        if x.get("field") == "content" and s:
            return _http.clean(re.sub(r"</?mark>", "", s))[:300]
    return ""


def _meta(o: dict) -> dict[str, str]:
    prom = o.get("promulgation") or {}
    meta = {"Tipo": _type(o), "Número": _http.clean(o.get("number")), "Nomenclatura": _http.clean(o.get("nomenclature")),
            "Entidad": _authority(o), "Gaceta Oficial": _http.clean(prom.get("number")),
            "Publicada en Gaceta": _date(prom.get("publishedAt")),
            "Ramas del derecho": ", ".join(_http.clean(b.get("lawBranch")) for b in o.get("lawBranches") or []),
            "Palabras clave": ", ".join(_http.clean(k.get("keyword")) for k in o.get("keywords") or []),
            "PDF": o.get("normUrl") or ""}
    aff = [f"{_http.clean((a.get('AffectedBy') or {}).get('type', {}).get('type'))} "
           f"{_http.clean((a.get('AffectedBy') or {}).get('number'))} "
           f"({_date((a.get('AffectedBy') or {}).get('publishedAt'))})" for a in o.get("affectedBy") or []]
    if aff:
        meta["Afectada por"] = "; ".join(aff)
    return {k: v for k, v in meta.items() if v}


async def _search(params: dict, limit: int, page: int) -> dict:
    if not 1 <= limit <= 100:
        raise BadRequest("limit must be 1-100.")
    p = {"page": page, "limit": limit, **{k: v for k, v in params.items() if v}}
    if not p.get("q"):
        p.update(sortKey="publishedAt", sortOrder="desc")
    r = await _http.get(API, params=p)
    if r.status_code != 200:
        raise SourceError(_http.error("Legispan", "search failed", r.status_code), r.status_code)
    try:
        d = r.json()
    except ValueError as e:
        raise SourceError("Legispan: unexpected non-JSON search reply", r.status_code) from e
    if not isinstance(d, dict) or "data" not in d:
        raise SourceError(f"Legispan: unexpected search reply {str(d)[:200]}", r.status_code)
    return d


def _years(filters: dict, params: dict) -> None:
    for k, edge, suffix in (("year_from", "publishedAt_start", "01-01"), ("year_to", "publishedAt_end", "12-31"),
                            ("year", None, None)):
        y = _http.clean(filters.get(k))
        if not y:
            continue
        if not re.fullmatch(r"1[89]\d\d|20\d\d", y):
            raise BadRequest(f"{k} must be four digits, e.g. 2019; got {y!r}.")
        if edge:
            params[edge] = f"{y}-{suffix}"
        else:
            params["publishedAt_start"], params["publishedAt_end"] = f"{y}-01-01", f"{y}-12-31"


class Panama(Jurisdiction):
    code = "pa"
    name = "Panama"
    languages = ("es",)
    aliases = ("panama", "panamá", "pan")
    sources = (
        Source(
            name="Legispan – Asamblea Nacional de Panamá (texts as published in the Gaceta Oficial, "
                 "including Supreme Court rulings published there)",
            url="https://legispan.asamblea.gob.pa/",
            covers=("legislation", "caselaw"),
            licence=("unknown: no licence or terms of use; the site has only a privacy policy "
                     "(legispan.asamblea.gob.pa/privacy-policy), silent on reuse and automation (2026-11-06)"),
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit=("unknown; 1 s spacing, no 429 seen in ~40 requests (2026-11-06); no robots.txt "
                        "(the app serves its index page at /robots.txt; S3 host answers AccessDenied)"),
            terms_url="https://legispan.asamblea.gob.pa/privacy-policy",
        ),
    )
    legislation_filters = {
        "type": "Legispan norm type, e.g. LEY, DECRETO EJECUTIVO, DECRETO LEY, TEXTO UNICO (consolidated), "
                "CONSTITUCION POLITICA, ACUERDO, RESOLUCION",
        "number": "the norm's number, e.g. 81",
        "year": "year of the norm, e.g. 2019 (or year_from / year_to)",
        "year_from": "first year", "year_to": "last year",
        "authority": "issuing body as Legispan writes it, e.g. 'ASAMBLEA NACIONAL'",
    }
    caselaw_filters = {
        "type": "FALLO (default; rulings published in the Gaceta Oficial) or SENTENCIA",
        "court": "issuing body as Legispan writes it, e.g. 'CORTE SUPREMA DE JUSTICIA - PLENO' or "
                 "'CORTE SUPREMA DE JUSTICIA - SALA TERCERA DE LO CONTENCIOSO'",
        "year": "year of the ruling (or year_from / year_to)",
        "year_from": "first year", "year_to": "last year",
    }
    min_interval = {"legispan.asamblea.gob.pa": 1.0, "s3-legispan.asamblea.gob.pa": 1.0}
    notes = ("Laws, decrees and other norms as published in the Gaceta Oficial (not consolidated, except "
             "'TEXTO UNICO' records), plus ~1,000 Supreme Court rulings published there, from the "
             "Asamblea Nacional's Legispan. Old records are scans without text.")
    gaps = (
        "Case law not published in the Gaceta (Órgano Judicial site): WAF 403 blocks our client; "
         "needs permission for our User-Agent",
        "Consolidated texts other than 'TEXTO UNICO' records: not on Legispan; other sources not "
         "researched yet",
        "Old Gaceta records: scans only, no text",
        "Gaceta Oficial's own site (gacetaoficial.gob.pa): Incapsula bot check blocks our client "
         "(Legispan copies used)",
    )
    samples = {
        "caselaw_query": "inconstitucionalidad",
        "decision_id": "bbb019cd-471b-4ba7-b4ae-6b42d4e79cba",
        "legislation_query": "protección de datos personales",
        "law_id": "fa4ac4d2-e118-492d-8b39-9002c0b2046e",  # Texto Único de la Constitución Política (2004)
        "provision": "1",
    }

    # ---------------------------------------------------------------- legislation
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        q = _http.clean(query)
        params = {"type[type]": _http.clean(filters.get("type")).upper(),
                  "number": _http.clean(filters.get("number")),
                  "authority[authority]": _http.clean(filters.get("authority")).upper()}
        _years(filters, params)
        m = _LAWQ.match(q)
        if m and not params["number"]:  # "Ley 81 de 2019" / "81 de 2019" -> type, number, year
            params["number"] = m[2]
            if m[1] and not params["type[type]"]:
                params["type[type]"] = re.sub("Ó", "O", re.sub("Ú", "U", m[1].upper()))
            if m[3] and "publishedAt_start" not in params:
                params["publishedAt_start"], params["publishedAt_end"] = f"{m[3]}-01-01", f"{m[3]}-12-31"
            q = ""
        if not q and not any(params.values()):
            raise BadRequest("Give search words or a norm number, e.g. 'datos personales' or 'Ley 81 de 2019'.")
        params["q"] = q
        d = await _search(params, limit, page)
        hits = d["data"]
        if q and page == 1 and params["type[type]"] == "TEXTO UNICO" and not params["number"]:
            fq = _fold(q)  # same reordering when the caller already asked for consolidated texts
            hits = ([h for h in hits if fq in _fold((h.get("original") or {}).get("title"))]
                    + [h for h in hits if fq not in _fold((h.get("original") or {}).get("title"))])
        elif q and page == 1 and not params["type[type]"] and not params["number"]:
            # Relevance ranks by words in the whole text, so the code itself can sink; put
            # consolidated texts whose title contains the words first.
            try:
                tu = await _search({**params, "type[type]": "TEXTO UNICO"}, 25, 1)
            except SourceError:
                tu = {"data": []}
            fq = _fold(q)
            first = [h for h in tu["data"] if fq in _fold((h.get("original") or {}).get("title"))]
            seen = {(h.get("original") or {}).get("id") for h in first}
            hits = (first + [h for h in hits if (h.get("original") or {}).get("id") not in seen])[:limit]
        # Codes that Legispan holds as a single, differently named record (scan, not consolidated): pin them first,
        # unless the caller's type filter excludes that record type.
        pinned = None
        for key, typ, num, yr, name in _PINNED:
            if _fold(q).startswith(key):
                pinned = (typ, name)
                if page == 1 and not params["number"] and params["type[type]"] in ("", typ):
                    try:
                        cod = (await _search({"type[type]": typ, "number": num, "publishedAt_start": f"{yr}-01-01",
                                              "publishedAt_end": f"{yr}-12-31"}, 5, 1))["data"]
                    except SourceError:
                        cod = []
                    cod = [h for h in cod if key.upper() in _fold((h.get("original") or {}).get("title")).upper()]
                    ids = {(h.get("original") or {}).get("id") for h in cod}
                    hits = (cod + [h for h in hits if (h.get("original") or {}).get("id") not in ids])[:limit]
                break
        items = []
        for h in hits:
            o = h.get("original") or {}
            items.append(LawHit(id=o.get("id", ""), title=_law_title(o), type=_type(o),
                                number=_http.clean(o.get("number")), date=_date(o.get("publishedAt")),
                                snippet=_snip(h) or _authority(o), url=_url(o.get("id", ""))))
        note = ("Texts as published in the Gaceta Oficial (not consolidated); type 'TEXTO UNICO' "
                "gives official consolidated texts. With search words, hits are by relevance.")
        if "CONSTITUCION" in params["type[type]"] or "constituci" in _fold(q):
            note += (" The Constitution in force is the Texto Único of 2004, a TEXTO UNICO record "
                     f"({CONSTITUTION_ID}); the CONSTITUCION POLITICA records are earlier "
                     "versions (1904-1983), mostly scans without text.")
        if pinned:
            typ, name = pinned
            if params["type[type]"] not in ("", typ):
                note += (f" {name} is not a '{params['type[type]']}' record: Legispan holds it only as {typ}, so this "
                         "filter excludes it (the hits below are other norms). Search without the type filter.")
            elif "Trabajo" in name:
                note += (" Código de Trabajo: it is Decreto de Gabinete 252 de 1971 (listed first when found). Legispan holds "
                         "it only as a scan without a text layer, not consolidated: later amendments (e.g. Ley 44 de 1995) "
                         "are separate records, and no current, readable consolidated Código de Trabajo is in this source. "
                         "Its PDF is linked from the record's page (the error of get_legislation_text also gives the link). "
                         "The other hits are labour-ministry resolutions and decrees that cite the code, not the code.")
            else:
                note += (f" {name}: it is {typ.title()} 8 de 1956 (listed first when found). Legispan holds it only as a "
                         "scan without a text layer, not consolidated: no current, readable Código Fiscal text is in this "
                         "source; later amendments are separate records. Its PDF is linked from the record's page. "
                         "The other hits only cite or amend the code.")
        if "codigo civil" in _fold(q):
            note += (" Civil Code: Legispan holds it only as scans without a text layer (the 'Texto Único 1 de 1914' "
                     "record and Ley 2 de 1916, which approved the codes); no current, readable Código Civil text is "
                     "in this source and none of its records is marked as current. Use the PDFs linked in the error.")
        return Results(items, total=d.get("count"), note=note)

    async def get_legislation_toc(self, id):
        law = await _load(id)
        o, text = law["o"], law["text"]
        entries: list[TocEntry] = []
        arts = _articles(text)
        pos = 0
        for label, start, end in arts:
            for ln in text[pos:start].split("\n\n"):
                if _HEAD.match(ln) and len(ln) < 120:
                    entries.append(TocEntry(title=ln, level=0))
            first = text[start:end].split("\n\n", 1)[0]
            entries.append(TocEntry(title=first[:140], level=1, provision=label))
            pos = end
        return Toc(id=o["id"], title=_law_title(o), url=_url(o["id"]), entries=entries)

    async def get_legislation_provision(self, id, provision):
        law = await _load(id)
        o, text = law["o"], law["text"]
        want = _key(provision)
        if not want:
            raise BadRequest("Give an article number, e.g. '1', 'art. 5', 'Artículo 12' or '16 bis'.")
        for label, start, end in _articles(text):
            if _key(label) == want:
                return Provision(law_id=o["id"], law_title=_law_title(o), provision=label,
                                 text=text[start:end].strip(), url=_url(o["id"]),
                                 as_of=_date((o.get("promulgation") or {}).get("publishedAt")))
        raise NotFound(f"No article {provision!r} in Legispan record {o['id']} ({_law_title(o)}). "
                       "See get_legislation_toc for the labels.")

    async def get_legislation_text(self, id):
        law = await _load(id)
        o = law["o"]
        return LawText(id=o["id"], title=_law_title(o), text=law["text"], url=_url(o["id"]),
                       as_of=_date((o.get("promulgation") or {}).get("publishedAt")), metadata=_meta(o))

    # ---------------------------------------------------------------- case law
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        t = _http.clean(filters.get("type") or "FALLO").upper()
        if t not in CASE_TYPES:
            raise BadRequest(f"type must be one of {', '.join(CASE_TYPES)}; got {t!r}.")
        params = {"q": _http.clean(query), "type[type]": t,
                  "authority[authority]": _http.clean(filters.get("court")).upper()}
        _years(filters, params)
        d = await _search(params, limit, page)
        # Legispan matches the words against the whole Gaceta issue, so unrelated rulings come back.
        # Keep rulings whose own title, keywords or branch of law contain every word.
        terms = {w[:6] for w in _words(query, 3)}
        hits = [h for h in d["data"] if not terms or terms <= {w[:6] for w in _words(
            " ".join([_http.clean((h.get("original") or {}).get("title"))]
                     + [_http.clean(k.get("keyword")) for k in (h.get("original") or {}).get("keywords") or []]
                     + [_http.clean(b.get("lawBranch")) for b in (h.get("original") or {}).get("lawBranches") or []]), 3)}]
        dropped = len(d["data"]) - len(hits)
        items = []
        for h in hits:
            o = h.get("original") or {}
            items.append(DecisionHit(id=o.get("id", ""), title=_http.clean(o.get("title")) or
                                     f"{_authority(o)} {_case_number(o)}", court=_authority(o),
                                     date=_date(o.get("publishedAt")), case_number=_case_number(o),
                                     snippet=_snip(h), url=_url(o.get("id", ""))))
        note = ("Only rulings published in the Gaceta Oficial (mainly Corte Suprema unconstitutionality "
                "and Sala Tercera nullity rulings); text is the Gaceta's OCR layer.")
        if dropped:
            note += (f" {dropped} of {len(d['data'])} hits on this page were left out: Legispan matched the words "
                     "in other norms of the same Gaceta issue, not in the ruling's title or keywords "
                     f"(source count {d.get('count')} includes such hits).")
        if "habeas" in _fold(query):
            if "corpus" not in _fold(query):
                note += " 'habeas' alone also matches Habeas data rulings; search 'habeas corpus' for the writ of liberty."
            if not any("corpus" in _fold(i.title) for i in items):
                note += (" No habeas corpus ruling was found here: none of the rulings shown (if any) concerns "
                         "habeas corpus. Habeas corpus rulings are mostly not among the Gaceta rulings on Legispan.")
        elif not items:
            note += f" No ruling matches {_http.clean(query)!r}."
        return Results(items, total=None if dropped else d.get("count"), note=note)

    async def get_decision(self, id):
        law = await _load(id)
        o = law["o"]
        if _type(o) not in CASE_TYPES:
            raise NotFound(f"Legispan record {o['id']} is a {_type(o) or 'norm'}, not a ruling; "
                           "use get_legislation_text.")
        meta = _meta(o)
        if not law["isolated"] and "CONTENIDO" in law["text"][:2500]:
            meta["Nota"] = ("Legispan's text is the whole Gaceta issue; this ruling could not be cut out of it "
                            "automatically (the ruling's own pages are probably scans without text), so look for its title "
                          f"inside the text or read the PDF: {o.get('normUrl') or _url(o['id'])}")
        return Decision(id=o["id"], title=_http.clean(o.get("title")) or f"{_authority(o)} {_case_number(o)}",
                        text=law["text"], url=_url(o["id"]), court=_authority(o),
                        date=_date(o.get("publishedAt")), case_number=_case_number(o), metadata=meta)
