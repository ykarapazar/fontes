"""Honduras: legislation from the Biblioteca Virtual of the Tribunal Superior de Cuentas
(www.tsc.gob.hn/biblioteca), the state audit court's public library of Honduran norms.

Gotchas this code encodes (verified 2026-11-06 from a UK IP):
  * The library is a Joomla site. One record = one Joomla article (numeric id) in a
    category (Leyes, Códigos, Reglamentos, Acuerdos y Decretos de Creación, Tratados,
    Normas, Manuales, Planes, Marcos Rectores, Varios). The article page holds the issuer,
    the decree number and "Descargar" links to PDFs under www.tsc.gob.hn/web/leyes/:
    the first PDF is the norm, later ones are its reforms ("Descargar reformas ...").
    Texts are NOT consolidated: reforms are separate PDFs, listed in metadata.
  * index.php?option=com_content&view=article&id=N opens any record; an unknown id
    answers a small HTTP 404 page (cheap to validate).
  * Search is Joomla com_search (titles and the short article body, not the PDFs). It
    returns at most 50 hits per query (the site's search limit), so `total` is only
    exact below 50.
  * Recent records' PDFs are pages cut from La Gaceta (two columns, page furniture,
    sometimes the tail of the previous norm on the first page). We drop the furniture,
    start at the norm's own decree number and read the Gaceta number/date as `as_of`.
    Old scans have no text layer: no OCR, we say so.
  * robots.txt (www.tsc.gob.hn, 2026-11-05/06): only /wp-admin/ disallowed; no Crawl-delay.
    No terms of use page on the site; nothing on automated access or reuse.
  * ENAG La Gaceta Digital (www.enag.gob.hn, Joomla + eDocman, checked 2026-11-10): every
    Gazette issue from 2015 as a PDF with a text layer, listed by month
    (/index.php/gaceta-digital/<year>/<mes>, 12 a page, &start=N) with a contents summary;
    download /index.php/gaceta-digital/<YYYYMMDD-NNNNN>/download. Its keyword search
    (buscar-documentos) ORs words and missed "196-2026" in an issue summary, so it is not used.
    robots.txt standard Joomla; no terms page.
  * Not used: www.poderjudicial.gob.hn / CEDIJ (case law and legislation; TCP connect
    timeout from this network on every try, 2026-11-06), www.congresonacional.hn (TLS
    certificate not valid for the hostname), congresonacional.hn (read timeout). Retried
    2026-11-10: poderjudicial.gob.hn (www and bare, http and https) connect timeout again;
    congresonacional.hn answered once (Next.js shell, robots.txt 404, no law database seen)
    and then timed out on three further tries.
"""
from __future__ import annotations

import re
from urllib.parse import parse_qs, urljoin, urlsplit

from lxml import html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from .._http import article_key as _key, fold_marks as _fold
from ..models import LawHit, LawText, Provision, Results, Toc, TocEntry

HOST = "https://www.tsc.gob.hn"
BIB = f"{HOST}/biblioteca/index.php"
SEARCH_CAP = 50  # the site's com_search returns at most this many hits
ENAG = "https://www.enag.gob.hn/index.php/gaceta-digital"
ENAG_SOURCE = "ENAG – La Gaceta Digital (Diario Oficial de la República de Honduras)"
ENAG_PER_PAGE = 12
_ENAG_ID = re.compile(r"^(\d{4})(\d{2})(\d{2})-(\d{5})$")
_ART = re.compile(r"^(?:ART[IÍ]CULO|Art[ií]culo)\s+(\d+)\s*([A-Za-z]{0,6})?\s*[.:\-–—º°]", re.M)
_HEAD = re.compile(r"^(T[IÍ]TULO|CAP[IÍ]TULO|SECCI[OÓ]N|LIBRO|PARTE)\b|^(DISPOSICIONES [A-ZÁÉÍÓÚ ]+)$", re.I)
_NOISE = re.compile(r"^(La Gaceta|A\.|B\.|Secci[oó]n [AB] Acuerdos y Leyes|"
                    r"REP[UÚ]BLICA DE HONDURAS\s*-\s*TEGUCIGALPA.*No\.\s*[\d,.]+)$", re.I)
_GACETA = re.compile(r"TEGUCIGALPA,\s*M\.\s*D\.\s*C\.,?\s*(\d{1,2})\s+DE\s+([A-ZÁÉÍÓÚ]+)\s+DEL?\s+(\d{4})\s+No\.\s*([\d,.]+)",
                     re.I)
_NUMBER = re.compile(r"\b(Decreto(?:\s+(?:Ejecutivo|Legislativo))?|Acuerdo(?:\s+Ejecutivo)?|Resoluci[oó]n)\s*"
                     r"(?:No\.?|N[úu]mero|N[°º]\.?)\s*(?:N[°º]\.?\s*)?([A-Z]{0,6}-?\d[\w-]*)", re.I)
_MONTHS = {m: i for i, m in enumerate(("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                                       "septiembre", "octubre", "noviembre", "diciembre"), 1)}
_MONTHS["setiembre"] = 9
_cache: dict[str, dict] = {}


def _url(id: str) -> str:
    return f"{BIB}?option=com_content&view=article&id={id}"


def _norm_id(id) -> str:
    s = _http.clean(str(id or ""))
    if re.fullmatch(r"\d{1,6}", s):
        return str(int(s))
    m = re.search(r"(\d{8})\s*-\s*(\d{5})", s)
    if m and ("enag.gob.hn" in s or re.fullmatch(r"\d{8}\s*-\s*\d{5}", s)):
        return f"{m[1]}-{m[2]}"
    if "tsc.gob.hn" in s:
        u = urlsplit(s)
        q = parse_qs(u.query).get("id")
        if q and q[0].isdigit():
            return str(int(q[0]))
        m = re.search(r"/biblioteca/index\.php/[\w-]+/(\d+)(?:-|$)", u.path)
        if m:
            return str(int(m[1]))
    raise BadRequest("Honduran ids are TSC Biblioteca Virtual record numbers, e.g. '177' (Constitución de la "
                     "República) or a www.tsc.gob.hn/biblioteca/index.php/<categoría>/<n>-... link, "
                     "or a La Gaceta issue on ENAG as '<YYYYMMDD>-<issue no.>', e.g. '20261002-37261'; "
                     f"got {id!r}.")


def _gaceta(text: str) -> tuple[str, str]:
    """(La Gaceta issue number, ISO date) from Gaceta page furniture, or ('', '')."""
    m = _GACETA.search(text[:3000])
    if not m or m[2].lower() not in _MONTHS:
        return "", ""
    return m[4].rstrip(".,"), f"{m[3]}-{_MONTHS[m[2].lower()]:02d}-{int(m[1]):02d}"


def _reflow(raw: str) -> str:
    """PDF text layer -> paragraphs: drop Gaceta page furniture, rejoin wrapped lines."""
    paras: list[str] = []
    cur, gap = "", False
    for ln in (_http.clean(x) for x in raw.replace("\r", "").split("\n")):
        if _NOISE.match(ln) or re.fullmatch(r"\d{1,4}", ln):  # page furniture, page numbers
            continue
        if not ln:
            gap = True
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


def _trim_gaceta(text: str, number: str) -> str:
    """A Gaceta copy starts with page furniture and often the tail of the previous norm:
    start at the first mention of our decree number (and the issuing body just before it)."""
    if not number:
        return text
    m = re.search(rf"(?<![\w-]){re.escape(number)}(?![\w-])", text[:8000], re.I)
    if not m:
        return text
    head = text[max(0, m.start() - 80):m.start()]
    body = re.search(r"Poder (?:Legislativo|Ejecutivo|Judicial)", head)
    k = body.start() if body else max((h.start() for h in re.finditer(r"\b(?:DECRETO|ACUERDO|Decreto|Acuerdo)\b", head)),
                                      default=None)
    return text[m.start() - len(head) + k:] if k is not None else text[m.start():]


def _articles(text: str) -> list[tuple[str, int, int]]:
    """[(label, start, end)] of the norm's own articles. Quoted articles inside an
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


def _number(s: str) -> tuple[str, str]:
    """(instrument type, number) from text like 'Decreto Ejecutivo Número PCM-39-2023'."""
    m = _NUMBER.search(s or "")
    return (_http.clean(m[1]).title(), m[2].rstrip(".,")) if m else ("", "")


async def _article(id: str) -> dict:
    r = await _http.get(_url(id))
    if r.status_code == 404:
        raise NotFound(f"No TSC Biblioteca Virtual record {id} (HTTP 404).")
    if r.status_code != 200:
        raise SourceError(_http.error("TSC Biblioteca Virtual", "record request failed", r.status_code), r.status_code)
    doc = lhtml.fromstring(r.content)
    art = doc.xpath('//div[contains(@class,"com-content-article")]')
    body = doc.xpath('//div[contains(@class,"com-content-article__body")]')
    if not art or not body:
        raise SourceError(f"TSC Biblioteca Virtual: record {id} page has no article body", r.status_code)
    # Opened by id, Joomla puts the menu heading in an <h1> and the record title in the last heading.
    heads = art[0].xpath('.//div[@class="page-header"]/*[self::h1 or self::h2]')
    title = _http.text(heads[-1]) if heads else ""
    cat = _http.text((art[0].xpath('.//dd[contains(@class,"category-name")]/a') or [None])[0])
    pdfs = []
    for a in body[0].xpath(".//a[@href]"):
        href = urljoin(str(r.url), a.get("href"))
        if href.lower().split("?")[0].endswith(".pdf"):
            pdfs.append((_http.text(a) or "Descargar", href))
    intro = [_http.text(p) for p in body[0].xpath("./p | ./div")]
    intro = [t for t in intro if t and not t.lower().startswith("descargar")]
    return {"id": id, "title": title, "category": cat, "pdfs": pdfs, "intro": intro,
            "body_html": lhtml.tostring(body[0], encoding="unicode")}


async def _pdf(url: str) -> str:
    r = await _http.get(url)
    if r.status_code != 200 or not r.content.startswith(b"%PDF"):
        raise SourceError(_http.error("TSC Biblioteca Virtual", f"PDF not available ({url})", r.status_code),
                          r.status_code)
    return _http.pdf_text(r.content)


async def _enag_month(month: str) -> list[dict]:
    """La Gaceta issues ENAG lists for one month 'YYYY-MM': [{id, date, summary}]."""
    m = re.fullmatch(r"(\d{4})-(\d{2})", month)
    if not m or not 1 <= int(m[2]) <= 12:
        raise BadRequest("gaceta_month is YYYY-MM, e.g. 2026-10.")
    if month in _cache:
        return _cache[month]
    name = [k for k, v in _MONTHS.items() if v == int(m[2]) and k != "setiembre"][0]
    out: list[dict] = []
    for start in range(0, 100, ENAG_PER_PAGE):          # ~25 issues a month: 2-3 pages
        r = await _http.get(f"{ENAG}/{m[1]}/{name}", params={"start": start} if start else None)
        if r.status_code == 404:
            raise NotFound(f"ENAG lists no La Gaceta issues for {month} (Gaceta Digital starts in 2015).")
        if r.status_code != 200:
            raise SourceError(_http.error(ENAG_SOURCE, "month listing failed", r.status_code), r.status_code)
        t = r.text
        rows = list(re.finditer(r'aria-label="(\d{8}) - (\d{5})"', t))
        for k, row in enumerate(rows):
            end = rows[k + 1].start() if k + 1 < len(rows) else len(t)
            d = re.search(r'edocman-description-details[^>]*>(.*?)</div>', t[row.end():end], re.S)
            summ = _http.clean(lhtml.fromstring(f"<div>{d[1]}</div>").text_content()) if d else ""
            id_ = f"{row[1]}-{row[2]}"
            if all(x["id"] != id_ for x in out):
                out.append({"id": id_, "date": f"{row[1][:4]}-{row[1][4:6]}-{row[1][6:]}", "summary": summ})
        if f"start={start + ENAG_PER_PAGE}" not in t:
            break
    return _http.lru_put(_cache, month, out, 12)


async def _enag_load(id: str) -> dict:
    m = _ENAG_ID.match(id)
    url = f"{ENAG}/{id}/download"
    r = await _http.get(url)
    if r.status_code == 404:
        raise NotFound(f"No La Gaceta issue {id} on ENAG; find ids with search_legislation and "
                       "filters gaceta_month=YYYY-MM.")
    if r.status_code != 200 or not r.content.startswith(b"%PDF"):
        raise SourceError(_http.error(ENAG_SOURCE, "issue download failed", r.status_code), r.status_code)
    text = _reflow(_http.pdf_text(r.content))
    if len(text) < 200:
        raise SourceError(f"La Gaceta {id} has no text layer (scan; no OCR here). Read the PDF: {url}", 200)
    no = f"{int(m[4]):,}"
    return _http.lru_put(_cache, id, {
        "id": id, "title": f"La Gaceta No. {no} ({m[1]}-{m[2]}-{m[3]}), whole issue", "category": "La Gaceta",
        "pdfs": [("PDF", url)], "intro": [], "text": text, "kind": "", "number": "", "gaceta": no,
        "as_of": f"{m[1]}-{m[2]}-{m[3]}", "url": url}, 6)


async def _load(id) -> dict:
    id = _norm_id(id)
    if id in _cache:
        return _cache[id]
    if _ENAG_ID.match(id):
        return await _enag_load(id)
    a = await _article(id)
    kind, number = _number(" ".join(a["intro"][:6]))
    gaceta, as_of = "", ""
    if a["pdfs"]:
        pdf_url = a["pdfs"][0][1]
        if urlsplit(pdf_url).hostname != "www.tsc.gob.hn":
            raise SourceError(f"Record {id}'s document is hosted elsewhere ({pdf_url}); open it there.", 200)
        raw = await _pdf(pdf_url)
        gaceta, as_of = _gaceta(raw)
        text = _reflow(raw)
        if gaceta:
            text = _trim_gaceta(text, number)
        if len(text) < 200:
            raise SourceError(f"Record {id}'s PDF has no text layer (scanned; this server does no OCR). "
                              f"Read the PDF: {pdf_url}", 200)
    else:
        text = _http.html_to_md(a["body_html"])
        if len(text) < 50:
            raise SourceError(f"Record {id} has no text and no PDF at the source: {_url(id)}", 200)
    return _http.lru_put(_cache, id, {**a, "text": text, "kind": kind, "number": number,
                                      "gaceta": gaceta, "as_of": as_of}, 6)


def _as_of(law: dict) -> str:
    """The Constitution copy is the 1982 text with reforms to 2004; say so where the text is read."""
    if law["as_of"] or not _fold(law["title"]).startswith("constitucion de la republica"):
        return law["as_of"]
    return "1982 text with reforms to 2004 only; later reforms (La Gaceta decrees) are not applied"


def _meta(law: dict) -> dict[str, str]:
    meta = {"Categoría": law["category"], "Emisor": law["intro"][0] if law["intro"] else "",
            "Instrumento": f"{law['kind']} No. {law['number']}" if law["number"] else "",
            "La Gaceta": f"No. {law['gaceta']} ({law['as_of']})" if law["gaceta"] else "",
            "PDF": law["pdfs"][0][1] if law["pdfs"] else ""}
    if len(law["pdfs"]) > 1:
        meta["Reformas y anexos (PDF, no incorporados al texto)"] = "; ".join(
            f"{_http.clean(lab)}: {u}" for lab, u in law["pdfs"][1:])
    return {k: v for k, v in meta.items() if v}


class Honduras(Jurisdiction):
    code = "hn"
    name = "Honduras"
    languages = ("es",)
    aliases = ("honduras", "hnd")
    sources = (
        Source(
            name="Biblioteca Virtual del Tribunal Superior de Cuentas (TSC) – laws, codes, regulations "
                 "and decrees as published (PDF, mostly La Gaceta copies)",
            url="https://www.tsc.gob.hn/biblioteca/",
            covers=("legislation",),
            licence=("unknown: no licence or terms of use on www.tsc.gob.hn; robots.txt disallows only "
                     "/wp-admin/ (checked 2026-11-06)"),
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; no Crawl-delay; 1 s spacing, no 429 seen in ~25 requests (2026-11-06)",
            terms_url="https://www.tsc.gob.hn/robots.txt",
        ),
        Source(
            name=ENAG_SOURCE,
            url=ENAG,
            covers=("legislation",),
            licence=("unknown: no licence or terms page; the site says a Congreso–ENAG agreement gives "
                     "'acceso universal y gratuito a la legislación hondureña' published in La Gaceta "
                     "(checked 2026-11-10)"),
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; robots.txt standard Joomla (no Crawl-delay; /index.php/ allowed); 2 s spacing",
            terms_url="https://www.enag.gob.hn/index.php/convenio-interinstitucional",
        ),
    )
    legislation_filters = {
        "match": "how search words combine: all (default), any, or exact (phrase)",
        "order": "newest (default), oldest, popular or alpha",
        "gaceta_month": "YYYY-MM: search La Gaceta issues of that month on ENAG (2015-) instead of the TSC library",
    }
    min_interval = {"www.tsc.gob.hn": 1.0, "www.enag.gob.hn": 2.0}
    notes = ("Laws, codes, regulations and decrees from the Tribunal Superior de Cuentas' Biblioteca Virtual: "
             "texts as published (often La Gaceta pages), not consolidated; reforms are separate PDFs. "
             "Whole La Gaceta issues 2015- from ENAG (id 'YYYYMMDD-NNNNN', found with filter gaceta_month). "
             "No case law: the Poder Judicial (CEDIJ) site was unreachable.")
    gaps = (
        "Case law (Poder Judicial / CEDIJ): site down / unreachable (TCP timeout from the UK, 2026-11-06 and 2026-11-10)",
        "Consolidated texts: not in the TSC library (reforms are separate PDFs); Congreso site has a bad TLS cert / timeout (2026-11-06; intermittent, mostly timeouts 2026-11-10)",
        "Older laws in the library: scans only, no text (no OCR)",
        "Primary acts not in the TSC library: only via whole La Gaceta issues on ENAG from 2015 (found by month, "
        "matched on ENAG's issue summary); pre-2015 Gazette not listed (ENAG's keyword search is imprecise, not used)",
        "Constitution: the TSC copy is the 1982 text with reforms to 2004; later reforms only as decrees in La Gaceta, not applied",
        "La Gaceta issues: articles indexed for the issue's first norm only; read others with get_legislation_text",
    )
    samples = {
        "legislation_query": "transparencia",
        "law_id": "177",  # Constitución de la República de Honduras (1982, reforms to 2004)
        "provision": "1",
    }

    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        q = _http.clean(query)
        if len(q) < 3:
            raise BadRequest("Give search words (at least 3 characters), e.g. 'transparencia' or 'código penal'.")
        if not 1 <= limit <= SEARCH_CAP:
            raise BadRequest(f"limit must be 1-{SEARCH_CAP}.")
        match = _http.clean(filters.get("match") or "all").lower()
        match = {"exact": "exact", "phrase": "exact", "all": "all", "any": "any"}.get(match, match)
        if match not in ("all", "any", "exact"):
            raise BadRequest(f"match must be all, any or exact; got {match!r}.")
        if filters.get("gaceta_month"):
            return await self._search_gaceta(q, filters["gaceta_month"], limit, page)
        order = _http.clean(filters.get("order") or "newest").lower()
        if order not in ("newest", "oldest", "popular", "alpha"):
            raise BadRequest(f"order must be newest, oldest, popular or alpha; got {order!r}.")
        note = ("Searches titles and record summaries (not the PDF texts); the source returns at most "
                f"{SEARCH_CAP} hits per query. Texts are as published, not consolidated.")
        start = (page - 1) * limit
        if start >= SEARCH_CAP:
            return Results([], total=None, note=note)
        r = await _http.get(f"{BIB}/component/search/", params={
            "searchword": q, "searchphrase": match, "ordering": order, "areas[0]": "content",
            "limit": limit, "limitstart": start})
        if r.status_code != 200:
            raise SourceError(_http.error("TSC Biblioteca Virtual", "search failed", r.status_code), r.status_code)
        doc = lhtml.fromstring(r.content)
        tot = doc.xpath('//div[@class="searchintro"]//span[contains(@class,"badge")]')
        if not tot and not doc.xpath('//form[@id="searchForm"]'):
            raise SourceError("TSC Biblioteca Virtual: unexpected search page", r.status_code)
        total = int(_http.text(tot[0])) if tot and _http.text(tot[0]).isdigit() else 0
        items = []
        for dt in doc.xpath('//dl[contains(@class,"search-results")]/dt[contains(@class,"result-title")]'):
            a = (dt.xpath(".//a[@href]") or [None])[0]
            if a is None:
                continue
            m = re.search(r"/biblioteca/index\.php/[\w-]+/(\d+)-", a.get("href", ""))
            if not m:
                continue
            nxt = dt.xpath("following-sibling::*")
            dd: dict[str, str] = {}
            for el in nxt:
                if el.tag == "dt":
                    break
                dd[(el.get("class") or "").split()[0] if el.get("class") else ""] = _http.text(el)
            snippet = re.sub(r"\s*Descargar.*$", "", dd.get("result-text", ""))
            kind, number = _number(snippet)
            items.append(LawHit(id=m[1], title=_http.text(a), type=dd.get("result-category", "").strip("() "),
                                number=f"{kind} {number}".strip() if number else "",
                                snippet=snippet[:300], url=_url(m[1])))
            if len(items) >= limit:
                break
        phrase = " ".join(_fold(q).split())
        if items and len(phrase.split()) > 1 and not any(phrase in " ".join(_fold(i.title).split()) for i in items):
            if match == "any":  # broad match pads the list with titles holding one common word; keep the closest
                words = phrase.split()
                close = [i for i in items if all(w in _fold(i.title) for w in words)]
                if close and len(close) < len(items):
                    note += (f" Broad match: {len(items) - len(close)} hits on this page that contain only one of "
                             "the words in the title were left out.")
                    items, total = close, len(close)
            note += (f" No record title on this page contains '{q}' as a phrase: the library may not hold that "
                     "law (e.g. the Código Civil was not found by title); these hits only mention the words. This source "
                     "has no link to such a law; look for it at the Poder Judicial's CEDIJ "
                     "(www.poderjudicial.gob.hn) or the Congreso Nacional (www.congresonacional.hn); both were "
                     "unreachable from here, so whether they hold it is unverified.")
        if len(phrase.split()) > 1:
            for i in items:
                if phrase not in " ".join(_fold(i.title).split()):
                    i.snippet = "[Title does not contain the phrase; matched on the summary only] " + i.snippet
        return Results(items, total=total if total < SEARCH_CAP else None, note=note)

    async def _search_gaceta(self, q, month, limit, page):
        words = [w for w in _fold(q).split() if w not in ("gaceta", "la")]
        hits = [x for x in await _enag_month(_http.clean(month))
                if all(w in _fold(x["summary"] + " " + x["id"]) for w in words)]
        start = (page - 1) * limit
        items = [LawHit(id=x["id"], title=f"La Gaceta No. {int(x['id'][-5:]):,} ({x['date']})",
                        type="La Gaceta", date=x["date"], snippet=x["summary"][:300],
                        url=f"{ENAG}/{x['id']}/download") for x in hits[start:start + limit]]
        return Results(items, total=len(hits),
                       note="La Gaceta issues of that month on ENAG, matched against ENAG's contents "
                            "summary of each issue (all words; 'gaceta' alone lists the month). "
                            "Each hit is a whole issue, as published.")

    async def get_legislation_toc(self, id):
        law = await _load(id)
        text = law["text"]
        entries: list[TocEntry] = []
        pos = 0
        for label, start, end in _articles(text):
            for ln in text[pos:start].split("\n\n"):
                if _HEAD.match(ln) and len(ln) < 120:
                    entries.append(TocEntry(title=ln, level=0))
            entries.append(TocEntry(title=text[start:end].split("\n\n", 1)[0][:140], level=1, provision=label))
            pos = end
        return Toc(id=law["id"], title=law["title"], url=law.get("url") or _url(law["id"]), entries=entries)

    async def get_legislation_provision(self, id, provision):
        law = await _load(id)
        want = _key(provision)
        if not want:
            raise BadRequest("Give an article number, e.g. '1', 'art. 5', 'Artículo 12' or '16 bis'.")
        for label, start, end in _articles(law["text"]):
            if _key(label) == want:
                paras = law["text"][start:end].strip().split("\n\n")
                while len(paras) > 1 and _HEAD.match(paras[-1]) and len(paras[-1]) < 120:
                    paras.pop()  # the next section's heading
                return Provision(law_id=law["id"], law_title=law["title"], provision=label,
                                 text="\n\n".join(paras), url=law.get("url") or _url(law["id"]), as_of=_as_of(law))
        raise NotFound(f"No article {provision!r} in {law['id']} ({law['title']}). "
                       "See get_legislation_toc for the labels.")

    async def get_legislation_text(self, id):
        law = await _load(id)
        return LawText(id=law["id"], title=law["title"], text=law["text"], url=law.get("url") or _url(law["id"]),
                       as_of=_as_of(law), metadata=_meta(law))
