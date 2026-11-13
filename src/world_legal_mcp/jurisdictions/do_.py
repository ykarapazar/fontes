"""Dominican Republic: contentious-electoral judgments of the Tribunal Superior Electoral
(TSE) from its public judgment viewer, visorpdf.tse.do. File is `do_.py` because `do` is
a Python keyword (same convention as in_.py / is_.py); the code is still "do".

Gotchas this code encodes (verified 2026-11-06 from a UK IP):
  * GET https://visorpdf.tse.do/?pos={page}&y={year|all}&s={text} returns an HTML table,
    60 rows a page, newest publication first: Sentencia No. (link to
    /documento/contenciosas/{opaque token}), Fecha (publication date, "11 Dic 2024"),
    Expediente, Relativo a. `s` matches the sentence number, expediente and "relativo a"
    text only, not the full text. No hit count; pagination links are windowed.
  * The sentence number ("TSE/0087/2024") is the id. get_decision finds its row with
    s={id}, then opens the detail page (Síntesis, Fecha de publicación) whose iframe
    points at /file-upload/{n}.pdf (certified copy, text layer) or .docx (some entries
    hold only the síntesis, not the full judgment).
  * The decision date is not a column; it is written out in "relativo a" / the text:
    "a los ocho (8) días del mes de enero del año dos mil veinticuatro (2024)".
  * The viewer covers expediente years 2021-2026. Older judgments (2012-2020) sit on
    tse.do WordPress pages and are not wired in.
  * robots.txt (tse.do and visorpdf.tse.do, 2026-11-05/06): "User-agent: * /
    Content-Signal: search=yes,ai-train=no,use=reference / Allow: /", with named AI
    crawlers (ClaudeBot, GPTBot, ...) disallowed; our UA is not one of them. No
    Crawl-delay. Terms (tse.do/terminos-de-uso) are silent on automated access.

Not built (see the report): Tribunal Constitucional (Azure Front Door 406 to our UA),
Poder Judicial / SCJ (Azure Application Gateway 403; www times out), legislation from
Consultoría Jurídica (Cloudflare managed challenge on its search API), Senado (robots
Crawl-delay 120 s, AI crawlers disallowed) and Cámara de Diputados SIL (bills of the
current period only; enacted texts are scanned PDFs without a usable text layer).
"""
from __future__ import annotations

import io
import re
import unicodedata
import zipfile
from urllib.parse import urlencode

from lxml import etree, html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, Results

HOST = "https://visorpdf.tse.do"
COURT = "Tribunal Superior Electoral"
PAGE = 60  # server page size
_MONTHS = {m: i for i, m in enumerate(
    ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
     "septiembre", "octubre", "noviembre", "diciembre"), 1)}
_MONTHS["setiembre"] = 9
_MON3 = {k[:3]: v for k, v in _MONTHS.items()}
_DATE_WORDS = re.compile(
    r"\((\d{1,2})\)\s*d[ií]as?\s+del\s+mes\s+de\s+([a-zé]+)\s+del?\s+(?:año\s+)?[^()]{0,80}\((\d{4})\)", re.I)
_DATE_SHORT = re.compile(r"(\d{1,2})\s+([A-Za-z]{3})[a-z]*\.?\s+(\d{4})")
_RUNNING_DATE = re.compile(r"^Del (\d{1,2}) de ([a-zé]+) de (\d{4})$", re.I | re.M)
_BOILER = re.compile(r"P[áa]gina \d+ de \d+|.*Tel[ée]fonos: 809-535-0075.*|Avenida Jim[ée]nez Moya, esquina.*")
_ID = re.compile(r"TSE\s*[-/]\s*(\d{1,4})\s*[-/]\s*(\d{4})", re.I)
_W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
_hits: dict[str, tuple[DecisionHit, str]] = {}  # id -> (hit, publication date)


def _norm_id(id) -> str:
    m = _ID.search(str(id or "")) or re.fullmatch(r"\s*(\d{1,4})\s*/\s*(\d{4})\s*", str(id or ""))
    if not m:
        raise BadRequest("Dominican TSE decision ids are sentence numbers like 'TSE/0087/2024' "
                         f"(also 'TSE-0087-2024' or '87/2024'); got {id!r}.")
    return f"TSE/{int(m[1]):04d}/{m[2]}"


def _word_date(s: str) -> str:
    m = _DATE_WORDS.search(s or "")
    if m and m[2].lower() in _MONTHS:
        return f"{m[3]}-{_MONTHS[m[2].lower()]:02d}-{int(m[1]):02d}"
    return ""


def _running_date(s: str) -> str:
    """Certified copies repeat 'Del 8 de enero de 2024' as a page header."""
    m = _RUNNING_DATE.search(s or "")
    if m and m[2].lower() in _MONTHS:
        return f"{m[3]}-{_MONTHS[m[2].lower()]:02d}-{int(m[1]):02d}"
    return ""


def _short_date(s: str) -> str:
    """'11 Dic 2024' / 'Wed 11 Dic 2024' -> '2024-12-11'."""
    m = _DATE_SHORT.search(s or "")
    if m and m[2].lower() in _MON3:
        return f"{m[3]}-{_MON3[m[2].lower()]:02d}-{int(m[1]):02d}"
    return ""


def _fold(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", (s or "").casefold()) if not unicodedata.combining(c))


async def _fetch(url: str) -> bytes:
    r = await _http.get(url)
    if r.status_code == 404:
        raise NotFound(f"Not found at the TSE viewer: {url}")
    if r.status_code != 200:
        raise SourceError(_http.error("TSE viewer", url, r.status_code), r.status_code)
    return r.content


async def _list(query: str, year: str, pos: int) -> tuple[list[DecisionHit], bool]:
    """One page of the viewer table -> (hits, has_next_page)."""
    url = f"{HOST}/?" + urlencode({"pos": pos, "y": year, "s": query})
    doc = lhtml.fromstring(await _fetch(url))
    if not doc.xpath("//form[@id='filter']"):
        raise SourceError("TSE viewer returned an unexpected page (no search form).", 200)
    hits, seen = [], set()
    for tr in doc.xpath("//table//tbody/tr"):
        a = tr.xpath(".//a[contains(@href,'/documento/')]")
        cells = [_http.text(td) for td in tr.xpath("./td")]
        if not a or len(cells) < 3:
            continue
        number = _http.clean(_http.text(a[0]))
        try:
            id = _norm_id(number)
        except BadRequest:
            continue
        relativo = cells[2]
        if id in seen:  # the viewer sometimes publishes one sentence twice, as two uploads
            relativo = f"[Duplicate listing: the TSE viewer lists {id} twice with identical data (second upload).] " + relativo
        hit = DecisionHit(
            id=id, title=f"{COURT} {id}", court=COURT,
            date=_word_date(relativo), case_number=_http.clean(cells[1]).rstrip(". "),
            snippet=(relativo[:400] + "…") if len(relativo) > 400 else relativo,
            url=a[0].get("href"))
        if id not in seen:  # get_decision reads the first upload
            _http.lru_put(_hits, id, (hit, _short_date(cells[0])), 500)
        seen.add(id)
        hits.append(hit)
    has_next = bool(doc.xpath("//ul[contains(@class,'pagination')]//a[normalize-space()='Siguiente']"))
    return hits, has_next


def _docx_text(data: bytes) -> str:
    root = etree.fromstring(zipfile.ZipFile(io.BytesIO(data)).read("word/document.xml"))
    paras = []
    for p in root.iter(f"{_W}p"):
        s = "".join((t.text or "") if t.tag == f"{_W}t" else " " for t in p.iter(f"{_W}t", f"{_W}tab"))
        if s.strip():
            paras.append(_http.clean(s))
    return "\n\n".join(paras)


def _strip_running(raw: str) -> str:
    """pdf_text output minus the running page header/footer of the certified copies."""
    pages = raw.split("\n\n")
    counts: dict[str, int] = {}
    for pg in pages:
        for ln in set(pg.split("\n")):
            counts[ln] = counts.get(ln, 0) + 1
    rep = {ln for ln, n in counts.items() if len(pages) > 2 and n > len(pages) / 2}
    out = []
    for pg in pages:
        out.append("\n".join(ln for ln in pg.split("\n")
                             if ln not in rep and not _BOILER.fullmatch(ln)))
    return "\n\n".join(p for p in out if p.strip())


class DominicanRepublic(Jurisdiction):
    code = "do"
    name = "Dominican Republic"
    languages = ("es",)
    aliases = ("dominican republic", "república dominicana", "republica dominicana", "rd", "dom")
    sources = (
        Source(
            name="Tribunal Superior Electoral – visor de sentencias (visorpdf.tse.do)",
            url=HOST + "/",
            covers=("caselaw",),
            licence=("No open licence stated; Términos de Uso §4 reserves the portal's content to the "
                     "TSE; robots.txt Content-Signal search=yes, ai-train=no, use=reference"),
            commercial_use=None,   # terms silent on reuse
            ai_use=False,          # robots.txt content signal ai-train=no (ai-input not set)
            auth="none",
            rate_limit=("unknown; 1 s spacing, no 429 seen in ~20 requests (2026-11-06); "
                        "no Crawl-delay in robots.txt"),
            terms_url="https://tse.do/terminos-de-uso/",
            warning=("Electoral court only (TSE contentious judgments, 2021+); the site reserves its "
                     "content against AI training (robots.txt ai-train=no, use=reference)."),
        ),
    )
    caselaw_filters = {"year": "expediente year, 2021 onwards (the viewer's 'Año de expediente'), or a range like '2022-2026'"}
    min_interval = {"visorpdf.tse.do": 1.0}
    notes = ("NO LEGISLATION TEXT through this server (Ley 20-23, Código Civil, decrees): read it on the official "
             "Consultoría Jurídica del Poder Ejecutivo site, https://consultoria.gov.do/ (open it in a browser; "
             "its search API sits behind a bot challenge that this server does not bypass). "
             "Case law: Tribunal Superior Electoral judgments only (2021+), listed by sentence number, "
             "expediente year or the short 'relativo a' line, not by topic. Constitutional Court and "
             "Supreme Court sites block automated clients.")
    gaps = (
        "Constitutional Court decisions: its Azure Front Door blocks our client (HTTP 406)",
        "Supreme Court and ordinary courts (Poder Judicial / SCJ): Azure gateway 403 to our client; www times out",
        "Legislation (laws, decrees, Gaceta) from Consultoría Jurídica: Cloudflare challenge on its search API",
        "Other legislation routes: Senado robots.txt Crawl-delay 120 s; Cámara SIL enacted texts are scans, no text",
        "TSE judgments 2012-2020: on tse.do WordPress pages; source works but not built yet",
    )
    samples = {"caselaw_query": "nulidad", "decision_id": "TSE/0087/2024"}

    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        year = str((filters or {}).get("year") or "all").strip()
        m = re.fullmatch(r"(20[2-9]\d)\s*-\s*(20[2-9]\d)", year)
        if m:
            lo, hi = sorted((int(m[1]), int(m[2])))
            years = [str(y) for y in range(hi, lo - 1, -1)]
        elif year == "all" or re.fullmatch(r"20[2-9]\d", year):
            years = [year]
        else:
            raise BadRequest(f"year must be an expediente year such as '2024' (2021 onwards) or a range such "
                             f"as '2022-2026'; got {year!r}.")
        limit = max(1, min(int(limit), PAGE))
        start = (max(1, int(page)) - 1) * limit
        need = start + limit
        # The viewer matches the whole query as one substring, so several words find nothing:
        # send the longest word and keep rows whose text holds every word (accent-insensitive).
        words = (query or "").split()
        q = max(words, key=len) if len(words) > 1 else (query or "")
        need_words = [_fold(w) for w in words] if len(words) > 1 else []
        items, total = [], None
        for i, y in enumerate(years):
            pos, has_next = 1, True
            while has_next and len(items) < need:
                got, has_next = await _list(q, y, pos)
                items += [h for h in got if all(w in _fold(f"{h.id} {h.case_number} {h.snippet}") for w in need_words)]
                pos += 1
            if len(items) >= need:
                break
            if i == len(years) - 1:
                total = len(items)
        return Results(items=items[start:need], total=total,
                       note=("SUBJECT SEARCH NOT SUPPORTED: this source matches only the sentence number "
                             "(e.g. 'TSE/0087/2024'), the expediente and the short 'relativo a' line, never the "
                             "judgment text, so a topic query (e.g. 'recurso de casación', 'cancelación "
                             "candidatura') returns 0 even when such judgments exist; a zero here does not mean "
                             "none exist. Use the year filter (one year '2024' or a range '2022-2026') with an "
                             "empty or short query and read the 'relativo a' lines. Electoral court only; "
                             "listed newest-published first. Several words are AND-ed against those same short fields. "
                             "The 'Open' line under each hit is only the get_decision call: for many entries "
                             "(especially .docx uploads) the source file holds only the síntesis (summary), not the "
                             "full judgment; get_decision states this in its 'Nota' line, so do not cite such an "
                             "entry as the full text."))

    async def get_decision(self, id):
        id = _norm_id(id)
        if id not in _hits:
            await _list(id, "all", 1)
        if id not in _hits:
            raise NotFound(f"No TSE judgment {id} in the viewer (it covers expedientes from 2021).")
        hit, published = _hits[id]
        page = lhtml.fromstring(await _fetch(hit.url))
        frame = page.xpath("//iframe/@src")
        if not frame:
            raise SourceError(f"TSE detail page for {id} has no document link.", 200)
        file_url = frame[0]
        data = await _fetch(file_url)
        ext, raw = file_url.rsplit(".", 1)[-1].lower(), ""
        if ext == "pdf":
            raw = _http.pdf_text(data)
            text = _strip_running(raw)
        elif ext == "docx":
            text = _docx_text(data)
        else:
            raise SourceError(f"TSE document for {id} is a .{ext} file this adapter cannot read: {file_url}", 200)
        if not text.strip():
            raise SourceError(f"TSE document for {id} has no text layer (scanned): {file_url}", 200)
        summary = ""
        for p in page.xpath("//p[.//span[contains(normalize-space(),'Síntesis')]]/following-sibling::p[1]"):
            summary = _http.clean(_http.text(p))
        meta = {"Fecha de publicación": published, "Documento": file_url}
        if ext == "docx" and len(text) < 3000:
            meta["Nota"] = "SUMMARY ONLY: the source file holds only the summary (síntesis), not the full judgment; do not cite it as the full text."
        return Decision(id=id, title=hit.title, text=text, url=hit.url, court=COURT,
                        date=hit.date or _running_date(raw) or _word_date(text), case_number=hit.case_number,
                        summary=summary, metadata={k: v for k, v in meta.items() if v})
