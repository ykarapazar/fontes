"""Mozambique: case law of the Tribunal Supremo, the three Tribunais Superiores de Recurso and the
Conselho Constitucional, and the legislation the Tribunal Supremo publishes on its own site.

How the sources work (verified 2026-11-06, UK IP, honest User-Agent):

  * www.ts.gov.mz (Tribunal Supremo, WordPress). Four pages each hold one server-rendered Ninja
    Table of judgments, one row per decision: Processo (linked to the PDF), Espécie do Processo,
    Matéria Objecto de Recurso (the headnote), Relator, Sessão (d/m/yyyy):
      /acordaos-do-tribunal-supremo/ (~700 rows), /acordaos-do-tribunal-superior-de-recurso-de-
      {maputo,beira,nampula}/ (37 / 64 / 134 rows). There is no server-side search; the adapter
    reads the table (one request per court, kept in memory for a few hours) and filters it.
    The decision id is the PDF's own upload path without ".pdf" ("2024/01/Processo-2"): the
    Processo number is not unique across rows. PDFs have a text layer (checked 3 of 3).
  * www.ts.gov.mz/legislacao/: a list of ~110 PDFs (Constitution, laws, decrees, resolutions,
    TS directives), mostly copies of the Boletim da República. Same id scheme. Text comes from the
    PDF's text layer. Quality varies: the Labour Law (Lei 13/2023) is clean with "Artigo N"
    headings; the 2018 Constitution PDF has a broken font encoding (article numbers missing, some
    words garbled), some PDFs are scans (no text) and a few links are dead (redirect to the home page).
    Texts are as published, not consolidated.
  * cconstitucional.org.mz (Conselho Constitucional, WordPress + Document Library Pro): ~290
    acórdãos and deliberações at /jurisprudencia/<slug>/. Search uses WordPress's own search as an
    RSS feed (?s=..&post_type=dlp_document&feed=rss2, 10 per page, no hit count). The page has a
    short summary and a PDF; about half the PDFs checked are scans (no text layer), in which case
    the decision text is the page summary plus a pointer to the PDF.

robots.txt (2026-11-05/06): www.ts.gov.mz disallows /wp-admin/, /?s=, /page/*/?s=, /search/ (not
used here); cconstitucional.org.mz disallows only /wp-admin/. No Crawl-delay on either. Neither
site publishes terms of use; the TS footer says "Copyright © 2022-2024 | Tribunal Supremo | Todos
Direitos Reservados". Nothing on automated access.

Not used (2026-11-06):
  * mozlex.ts.gov.mz (TS legislation database): robots.txt says "A recolha automatizada do acervo
    (raspagem, descarga em massa) nao e autorizada" (automated collection, scraping and bulk
    download are not authorised); its terms page (/sobre#termos) answers 404.
  * mozjuris.ts.gov.mz (TS case-law database): Anubis proof-of-work bot challenge.
  * www.inm.gov.mz (Imprensa Nacional, Boletim da República; Drupal + Ubercart shop "eBR").
    Re-checked 2026-11-06: the server sends an incomplete TLS chain. It is reachable only through
    the OS trust store (_http uses truststore; macOS/Windows fetch the missing intermediate) and
    still fails on Linux. Each BR issue (I/II/III Série, Suplementos) is a shop product page
    (/pt-br/content/br-nº-211-de-051126-boletim-da-república-i-serie) with an HTML "Sumário" of the
    acts (titles and one-line summaries only, no text). The PDF itself is an Ubercart file product:
    price 0,00 MT for recent issues, but the site's own guide (/sites/default/files/
    Procedimentos_1.pdf) says to register, log in, "Comprar", check out and download from "Minha
    conta > arquivos". No public PDF link exists, so there is no text without an account: not used.
    Terms (/content/politica-de-privacidade, linked as "Termos & Condições"): "É proibida a cópia,
    total ou parcial do site, incluindo qualquer conteúdo ou formato digital pertencente ao site da
    INM,E.P, sem a prévia autorização da INM,E.P." (copying any site content needs prior
    authorisation), so a search over the HTML sumários is not built either. robots.txt:
    Crawl-delay 10; disallows /search/, /user/login/ etc.; /pt-br/bulletin and /content/ allowed.
  * www.parlamento.mz (Assembleia da República): parked domain.
"""
from __future__ import annotations

import io
import re
import time
import unicodedata
from urllib.parse import unquote, urlencode, urlsplit

from lxml import etree
from lxml import html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

TS_HOST = "www.ts.gov.mz"
TS = f"https://{TS_HOST}"
UPLOADS = TS + "/wp-content/uploads/"
CC_HOST = "cconstitucional.org.mz"
CC = f"https://{CC_HOST}"
MAX_PDF = 40_000_000           # bytes; larger PDFs are refused
TABLE_TTL = 6 * 3600           # seconds a court table / the legislation list is kept in memory
CC_PAGE = 10                   # WordPress feed size, fixed by the site

COURTS = {  # filter value -> (court name, listing page)
    "ts": ("Tribunal Supremo", "/acordaos-do-tribunal-supremo/"),
    "tsr-maputo": ("Tribunal Superior de Recurso de Maputo",
                   "/acordaos-do-tribunal-superior-de-recurso-de-maputo/"),
    "tsr-beira": ("Tribunal Superior de Recurso da Beira",
                  "/acordaos-do-tribunal-superior-de-recurso-da-beira/"),
    "tsr-nampula": ("Tribunal Superior de Recurso de Nampula",
                    "/acordaos-do-tribunal-superior-de-recurso-de-nampula/"),
}
CC_NAME = "Conselho Constitucional"
COURT_FILTER = {"ts": ["ts"], "tsr-maputo": ["tsr-maputo"], "tsr-beira": ["tsr-beira"],
                "tsr-nampula": ["tsr-nampula"], "tsr": ["tsr-maputo", "tsr-beira", "tsr-nampula"],
                "cc": []}
UPLOAD_ID = re.compile(r"^\d{4}/\d{2}/[^/?#]+$")
CC_SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")
MONTHS = {m: i for i, m in enumerate(("janeiro", "fevereiro", "marco", "abril", "maio", "junho", "julho",
                                      "agosto", "setembro", "outubro", "novembro", "dezembro"), 1)}

_cache: dict = {}          # key -> (time, value): court tables and the legislation list
_pdf_cache: dict = {}      # url -> text


def _fold(s: str) -> str:
    """Lower-case, accents stripped: 'Acórdão' -> 'acordao'."""
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")


def _bound(v, name: str, end: bool) -> str:
    """'2022' or '2022-05-31' -> comparable 'YYYY-MM-DD' lower bound (end=False) or upper bound."""
    v = _http.clean(v)
    if re.fullmatch(r"\d{4}", v):
        return v + ("-12-31" if end else "-01-01")
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
        return v
    raise BadRequest(f"{name} must be a year (2022) or a date (2022-05-31).")


def _words(q: str) -> list[str]:
    return [w for w in _fold(_http.clean(q)).split() if w]


def _pt_date(s: str, year: str = "") -> str:
    """'25 de Agosto de 2023' (or '25 de Agosto' + year) -> '2023-08-25'; else ''."""
    m = re.search(r"\b(\d{1,2})\s+de\s+([A-Za-zçÇ]+)(?:\s+de\s+(\d{4}))?", _fold(s))
    if not m or m[2] not in MONTHS or not (m[3] or year):
        return ""
    return f"{m[3] or year}-{MONTHS[m[2]]:02d}-{int(m[1]):02d}"


def _upload_id(href: str) -> str:
    """'http://ts.gov.mz/wp-content/uploads/2024/01/Processo-2.pdf' -> '2024/01/Processo-2'."""
    path = unquote(urlsplit(href).path)
    m = re.search(r"/wp-content/uploads/(\d{4}/\d{2}/[^/]+)\.pdf$", path, re.I)
    return m[1] if m else ""


def _pdf_url(uid: str) -> str:
    return UPLOADS + uid + ".pdf"


def _ts_id(id: str) -> str:
    """Accept '2024/01/Processo-2', with '.pdf', or the full PDF url."""
    id = _http.clean(id)
    if "/wp-content/uploads/" in id:
        id = _upload_id(id) or id
    id = re.sub(r"\.pdf$", "", id, flags=re.I)
    return id if UPLOAD_ID.match(id) else ""


async def _cached(key, loader):
    hit = _cache.get(key)
    if hit and time.monotonic() - hit[0] < TABLE_TTL:
        return hit[1]
    value = await loader()
    _http.lru_put(_cache, key, (time.monotonic(), value), 16)
    return value


async def _get_html(url: str, who: str) -> str:
    r = await _http.get(url)
    if r.status_code == 404:
        raise NotFound(f"{who}: {url} not found.")
    if r.status_code != 200:
        raise SourceError(_http.error(who, f"request failed: {url}", r.status_code), r.status_code)
    return r.text


# The 2018 Constitution PDF (and a few others) has a font whose text layer is shifted by 30 code points:
# letters, digits, spaces and punctuation come out as other characters ("FQ" for "do", control characters
# for digits and spaces), and the accents are glyph numbers. The plain pdf_text drops the control
# characters, which loses the digits (article numbers) and the word spaces, so the layer is read here.
_ACCENTS = {"º": "ã", "È": "í", "Á": "ç", "Ä": "ê", "Ã": "é", "Õ": "ú", "¸": "â", "Î": "ó", "Ð": "õ",
            "¶": "á", "´": "à", "ſ": "fi", "ƀ": "fl", "ō": "-", "Ō": "-", "\x9c": "É", "\x8d": "À",
            "\xa0": "Í"}
_SHIFTED = re.compile(r"[\x02-\x1f]|[ſƀ]")


def _unshift(seg: str) -> str:
    return "".join(_ACCENTS.get(c) or ("" if c == " " else chr(ord(c) + 30) if 3 <= ord(c) <= 0x5c else c)
                   for c in seg)


def _fix_line(line: str) -> str:
    """Decode the font-shifted segments of a line (separated by the shifted space, \\x02); segments
    with ASCII lower-case letters, and the word ARTIGO, are real text and stay."""
    if not _SHIFTED.search(line):
        return line
    return " ".join(x if re.search(r"[a-z]", x) or x.strip() == "ARTIGO" else _unshift(x)
                    for x in line.split("\x02"))


def _pdf_text(data: bytes) -> str:
    """Like _http.pdf_text, with the shifted font above decoded. '' when there is no text layer."""
    from pypdf import PdfReader
    pages = []
    for p in PdfReader(io.BytesIO(data)).pages:
        lines = [_http.clean(_fix_line(ln)) for ln in (p.extract_text() or "").split("\n")]
        pages.append("\n".join(ln for ln in lines if ln))
    return re.sub(r"\n{3,}", "\n\n", "\n\n".join(p for p in pages if p)).strip()


async def _pdf(url: str, who: str) -> str:
    """Text layer of a PDF the source lists; refuses >MAX_PDF and dead links. '' = scan.
    When a HEAD gives no Content-Length, the GET's own max_bytes cap enforces MAX_PDF."""
    if url in _pdf_cache:
        return _pdf_cache[url]
    h = await _http.request("HEAD", url)
    ctype = h.headers.get("content-type", "")
    if h.status_code == 404 or (h.status_code == 200 and "pdf" not in ctype):
        raise NotFound(f"{who}: the PDF {url} is no longer on the site (the link is dead).")
    if h.status_code != 200:
        raise SourceError(_http.error(who, f"PDF failed: {url}", h.status_code), h.status_code)
    size = int(h.headers.get("content-length") or 0)
    if size > MAX_PDF:
        raise SourceError(f"Error ({who}): {url} is {size // 1_000_000} MB; "
                          f"PDFs over {MAX_PDF // 1_000_000} MB are not downloaded. Read it there.", "too-large")
    r = await _http.get(url, max_bytes=MAX_PDF)
    if r.status_code != 200 or not r.content.startswith(b"%PDF"):
        raise SourceError(_http.error(who, f"PDF failed: {url}", r.status_code), r.status_code)
    return _http.lru_put(_pdf_cache, url, _pdf_text(r.content), 8)


# --------------------------------------------------------------------------- #
# Tribunal Supremo / Tribunais Superiores de Recurso (ts.gov.mz tables)
# --------------------------------------------------------------------------- #
async def _table(court: str) -> list[dict]:
    name, path = COURTS[court]

    async def load():
        doc = lhtml.fromstring(await _get_html(TS + path, "Tribunal Supremo"))
        rows = []
        for tr in doc.xpath('//table[contains(@class, "ninja_footable")]//tr[@data-row_id]'):
            tds = tr.xpath("./td")
            href = tr.xpath(".//td[1]//a/@href")
            uid = _upload_id(href[0]) if href else ""
            if len(tds) < 5 or not uid:
                continue
            materia = _http.html_to_md(etree.tostring(tds[2], encoding="unicode"))
            cell = [_http.clean(td.text_content()) for td in tds]
            rows.append({"id": uid, "court": name, "processo": cell[0], "especie": cell[1],
                         "materia": materia, "relator": cell[3], "date": _http.iso_date(cell[4])})
        if not rows:
            raise SourceError(f"Error (Tribunal Supremo): the judgments table on {TS + path} changed "
                              "(no rows found).", 200)
        return rows
    return await _cached(("table", court), load)


def _ts_hit(row: dict) -> DecisionHit:
    snippet = "; ".join(x for x in (row["especie"], _http.clean(row["materia"])) if x)
    return DecisionHit(id=row["id"], title=f"{row['court']}, processo {row['processo']}", court=row["court"],
                       date=row["date"], case_number=row["processo"], snippet=snippet[:300],
                       url=_pdf_url(row["id"]))


async def _ts_matches(words: list[str], courts: list[str]) -> list[dict]:
    out = []
    for c in courts:
        for row in await _table(c):
            hay = _fold(" ".join((row["court"], row["processo"], row["especie"], row["materia"],
                                  row["relator"], row["date"])))
            if all(w in hay for w in words):
                out.append(row)
    return sorted(out, key=lambda r: r["date"], reverse=True)


async def _ts_decision(uid: str) -> Decision:
    row = None
    for c in COURTS:
        row = next((r for r in await _table(c) if r["id"] == uid), None)
        if row:
            break
    if not row:
        raise NotFound(f"Tribunal Supremo: no judgment with id {uid!r} in the TS/TSR tables. "
                       "Use an id from search_caselaw, e.g. '2024/01/Processo-2'.")
    url = _pdf_url(uid)
    text = await _pdf(url, "Tribunal Supremo")
    if len(text) < 200:
        text = (f"{row['materia']}\n\n[The PDF is a scan without a text layer; read the judgment at {url}]")
    meta = {k: v for k, v in (("Espécie do processo", row["especie"]), ("Relator", row["relator"]),
                              ("Sessão", row["date"])) if v}
    return Decision(id=uid, title=f"{row['court']}, processo {row['processo']}", text=text, url=url,
                    court=row["court"], date=row["date"], case_number=row["processo"],
                    summary=row["materia"], metadata=meta)


# --------------------------------------------------------------------------- #
# Conselho Constitucional (cconstitucional.org.mz)
# --------------------------------------------------------------------------- #
def _cc_meta(title: str) -> tuple[str, str]:
    """'Acórdão n.º 12/CC/2024 de 2 de Outubro' -> ('12/CC/2024', '2024-10-02')."""
    m = re.search(r"(\d+)\s*/\s*CC\s*/\s*(\d{2,4})", title, re.I)
    number, year = "", ""
    if m:
        year = m[2] if len(m[2]) == 4 else ("20" + m[2] if int(m[2]) < 50 else "19" + m[2])
        number = f"{m[1]}/CC/{year}"
    return number, _pt_date(title, year)


async def _cc_feed(q: str, n: int) -> list[DecisionHit]:
    params = {"s": q, "post_type": "dlp_document", "feed": "rss2"}
    if n > 1:
        params["paged"] = str(n)
    r = await _http.get(CC + "/?" + urlencode(params))
    if r.status_code == 404:  # WordPress answers 404 past the last page
        return []
    if r.status_code != 200 or b"<rss" not in r.content[:2000]:
        raise SourceError(_http.error(CC_NAME, "search failed", r.status_code), r.status_code)
    root = etree.fromstring(r.content)
    hits = []
    for it in root.iter("item"):
        link = it.findtext("link") or ""
        m = re.search(r"/jurisprudencia/([a-z0-9-]+)/?$", link)
        if not m:
            continue
        title = _http.clean(it.findtext("title"))
        number, date = _cc_meta(title)
        if not date:
            pub = re.search(r"(\d{1,2}) (\w{3}) (\d{4})", it.findtext("pubDate") or "")
            mon = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
                   "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
            date = f"{pub[3]}-{mon.get(pub[2], 1):02d}-{int(pub[1]):02d}" if pub else ""
        hits.append(DecisionHit(id=m[1], title=title, court=CC_NAME, date=date, case_number=number,
                                snippet=_http.clean(it.findtext("description"))[:300], url=link))
    return hits


async def _cc_decision(slug: str) -> Decision:
    url = f"{CC}/jurisprudencia/{slug}/"
    doc = lhtml.fromstring(await _get_html(url, CC_NAME))
    title = _http.clean(" ".join(doc.xpath('//h1[contains(@class, "entry-title")]//text()')))
    left = doc.xpath('//div[@class="dlp-single-left"]')
    if not title or not doc.xpath('//*[contains(@class, "type-dlp_document")]'):
        raise NotFound(f"{CC_NAME}: no decision at {url}.")
    summary = _http.html_to_md(etree.tostring(left[0], encoding="unicode")) if left else ""
    pdfs = doc.xpath('//a[contains(@class, "dlp-download-link")]/@href')
    meta = {}
    for div in doc.xpath('//div[@id="dlp-document-info-list"]/div'):
        label = _http.clean("".join(div.xpath('./span[@class="dlp-document-info-title"]//text()'))).rstrip(":")
        value = _http.clean("".join(div.xpath("./text()")))
        if label and value and label != "File Type":
            meta[{"Categories": "Categoria", "Tags": "Etiquetas"}.get(label, label)] = value
    text = ""
    if pdfs:
        meta["PDF"] = pdfs[0]
        text = await _pdf(pdfs[0], CC_NAME)
    if len(text) < 200:
        note = (f"[The PDF is a scan without a text layer; read the decision at {pdfs[0]}]" if pdfs
                else "[The page links no PDF.]")
        text = "\n\n".join(x for x in (summary, note) if x)
    number, date = _cc_meta(title)
    return Decision(id=slug, title=title, text=text, url=url, court=CC_NAME, date=date,
                    case_number=number, summary=summary, metadata=meta)


# --------------------------------------------------------------------------- #
# Legislation (ts.gov.mz/legislacao/)
# --------------------------------------------------------------------------- #
_LAW_TYPE = re.compile(r"^\s*(?:\d+\.\s*)?(Constituição|Decreto[- ]Lei|Decreto Presidencial|Decreto|Lei|"
                       r"Resolução|Despachos?(?: Presidencial| Ministerial)?|Directiva|Diploma Ministerial|"
                       r"Circular|Aviso)", re.I)


async def _laws() -> list[LawHit]:
    async def load():
        doc = lhtml.fromstring(await _get_html(TS + "/legislacao/", "Tribunal Supremo"))
        seen, out = set(), []
        for a in doc.xpath('//div[contains(@class, "entry-content")]//a[contains(@href, ".pdf")]'):
            uid = _upload_id(a.get("href", ""))
            title = _http.clean(a.text_content())
            if not uid or not title or uid in seen:
                continue
            seen.add(uid)
            t = _LAW_TYPE.match(title)
            num = re.search(r"n[.ºo°\s]*\.?\s*(\d+[A-Za-z]?(?:[./][A-Z]+)*[/.-]\s*\d{2,4})", title, re.I)
            year = re.search(r"\b(19|20)\d{2}\b", title)
            out.append(LawHit(id=uid, title=title, type=t[1] if t else "",
                              number=num[1].replace(" ", "") if num else "",
                              date=_pt_date(title, year[0] if year else ""), url=_pdf_url(uid)))
        if not out:
            raise SourceError("Error (Tribunal Supremo): the legislation page changed (no PDFs).", 200)
        return out
    return await _cached("laws", load)


async def _law(id: str) -> tuple[LawHit, str]:
    uid = _ts_id(id)
    if not uid:
        raise BadRequest("Give a law id from search_legislation, e.g. "
                         "'2024/05/Lei-No-13-2023-de-25-de-Agosto-NOVA-LEI-DO-TRABALHO-BR_165_I_SEI_RIE_2Ao__230831_091658'.")
    hit = next((h for h in await _laws() if h.id == uid), None)
    if not hit:
        raise NotFound(f"Tribunal Supremo: no document {uid!r} on {TS}/legislacao/.")
    text = await _pdf(hit.url, "Tribunal Supremo")
    if len(text) < 200:
        raise SourceError(f"Error (Tribunal Supremo): {hit.url} is a scan without a text layer "
                          "(no OCR here); read it there.", "no-text")
    return hit, text


_ART = re.compile(r"^[“\"']?\s*(?:ARTIGO|Artigo|Art\.º)\s+(\d+(?:\.º|º)?(?:\s?-?[A-Z])?)(?![\d/])\s*(.*)$")
_HEAD = re.compile(r"^(TÍTULO|TITULO|CAPÍTULO|CAPITULO|SECÇÃO|SECÇAO|SECÇÃO|SUBSECÇÃO|LIVRO|PARTE)\b", re.I)


def _norm_art(n: str) -> str:
    return re.sub(r"[\s.º-]", "", n).upper()


def _articles(text: str) -> tuple[list[TocEntry], dict[str, tuple[int, int]]]:
    """TOC entries and article spans (first occurrence of each number wins:
    amending laws quote the articles they change)."""
    lines = text.split("\n")
    entries, starts = [], []
    # The 2018 Constitution PDF opens with the revision law (Lei 1/2018), which quotes articles 8, 292...
    # before the republished Constitution starts; "Artigo N" means the Constitution's article there.
    first = next((i for i, ln in enumerate(lines[:-1]) if ln == "CONSTITUIÇÃO DA REPÚBLICA"
                  and lines[i + 1] == "Preâmbulo"), 0)
    for i, ln in enumerate(lines):
        if i < first:
            continue
        m = _ART.match(ln)
        if m:
            label = "Artigo " + _norm_art(m[1])
            heading = m[2] or (lines[i + 1] if i + 1 < len(lines) and lines[i + 1].startswith("(") else "")
            starts.append((i, label))
            entries.append(TocEntry(title=_http.clean(f"{label} {heading}"), level=1, provision=label))
        elif _HEAD.match(ln) and len(ln) < 80:
            entries.append(TocEntry(title=ln, level=0))
    spans: dict[str, tuple[int, int]] = {}
    for k, (i, label) in enumerate(starts):
        end = starts[k + 1][0] if k + 1 < len(starts) else len(lines)
        spans.setdefault(label, (i, end))
    seen, toc = set(), []
    for e in entries:  # drop repeated article labels from the TOC too
        if e.provision and e.provision in seen:
            continue
        seen.add(e.provision)
        toc.append(e)
    return toc, spans


def _provision_label(p: str) -> str:
    m = re.match(r"^\s*(?:artigo|art\.?º?|article|art)?\s*\.?\s*(\d+\s*(?:\.º|º)?\s*-?\s*[A-Za-z]?)\s*$", p, re.I)
    return "Artigo " + _norm_art(m[1]) if m else ""


class Mozambique(Jurisdiction):
    code = "mz"
    name = "Mozambique"
    languages = ("pt",)
    aliases = ("moçambique", "mocambique", "republic of mozambique", "república de moçambique")
    sources = (
        Source(
            name="Tribunal Supremo (ts.gov.mz): judgments tables of the TS and the Tribunais Superiores de "
                 "Recurso, and its legislation page",
            url=TS + "/",
            covers=("caselaw", "legislation"),
            licence="all rights reserved (site footer: 'Copyright © 2022-2024 | Tribunal Supremo | Todos "
                    "Direitos Reservados'); no terms of use published",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~30 requests (2026-11)",
            terms_url=TS + "/",
        ),
        Source(
            name="Conselho Constitucional (cconstitucional.org.mz): acórdãos and deliberações",
            url=CC + "/jurisprudencia/",
            covers=("caselaw",),
            licence="not stated (no terms of use published)",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~20 requests (2026-11)",
            terms_url=CC + "/",
        ),
    )
    caselaw_filters = {"court": "ts (Tribunal Supremo), tsr (all three Tribunais Superiores de Recurso), "
                                "tsr-maputo, tsr-beira, tsr-nampula, or cc (Conselho Constitucional). "
                                "Default: all.",
                       "date_from": "session date from, YYYY or YYYY-MM-DD (Tribunal Supremo and TSR only)",
                       "date_to": "session date to, YYYY or YYYY-MM-DD (Tribunal Supremo and TSR only)"}
    min_interval = {TS_HOST: 1.0, CC_HOST: 1.0}
    notes = ("Case law: Tribunal Supremo, the three Tribunais Superiores de Recurso (~930 judgments) and the "
             "Conselho Constitucional (~290). Legislation: ~110 PDFs the Tribunal Supremo hosts (Constitution, "
             "key laws, decrees), as published, not consolidated. Portuguese.")
    gaps = (
        "Consolidated legislation (MozLex, mozlex.ts.gov.mz): robots.txt bans it ('recolha "
         "automatizada ... nao e autorizada')",
        "Case-law database (mozjuris.ts.gov.mz, incl. Administrative Tribunal): Anubis bot "
         "challenge blocks our client",
        "Boletim da República (inm.gov.mz): PDFs need an account; terms bar copying ('É proibida "
         "a cópia') without authorisation",
        "Scanned PDFs (about half of the CC decisions checked, some laws): scans only, no text",
        "Provincial and district courts: not researched yet",
        "Assembleia da República (parlamento.mz): site down (parked domain, 2026-11-06)",
    )
    samples = {
        "caselaw_query": "arrendamento",
        "decision_id": "2024/01/Processo-2",
        "legislation_query": "Lei de Trabalho",
        "law_id": "2024/05/Lei-No-13-2023-de-25-de-Agosto-NOVA-LEI-DO-TRABALHO-BR_165_I_SEI_RIE_2Ao__230831_091658",
        "provision": "Artigo 1",
    }

    async def search_caselaw(self, query, *, limit, page, filters):
        words = _words(query)
        if not words:
            raise BadRequest("Give words from the subject, a process number or a judge, in Portuguese, "
                             "e.g. 'arrendamento' or '12/CC/2024'.")
        court = _http.clean((filters or {}).get("court", "")).lower()
        if court and court not in COURT_FILTER:
            raise BadRequest(f"court must be one of: {', '.join(COURT_FILTER)}.")
        f = filters or {}
        lo = _bound(f["date_from"], "date_from", False) if f.get("date_from") else ""
        hi = _bound(f["date_to"], "date_to", True) if f.get("date_to") else ""
        if (lo or hi) and court == "cc":
            raise BadRequest("The Conselho Constitucional's search cannot filter by date; drop date_from/"
                             "date_to, or search the Tribunal Supremo/TSR (court=ts or tsr).")
        limit = max(1, min(int(limit), 50))
        start = (max(1, int(page)) - 1) * limit
        ts_rows = await _ts_matches(words, COURT_FILTER[court] if court else list(COURTS))
        if lo or hi:
            ts_rows = [r for r in ts_rows if r["date"] and lo <= r["date"] <= (hi or "9999")]
        items = [_ts_hit(r) for r in ts_rows[start:start + limit]]
        use_cc = court in ("", "cc") and not (lo or hi)
        if use_cc and len(items) < limit:
            q = _http.clean(query)[:100]
            cc_start = max(0, start - len(ts_rows))
            need, off = limit - len(items), cc_start % CC_PAGE
            hits, n = [], cc_start // CC_PAGE + 1
            while True:
                more = await _cc_feed(q, n)
                hits += more
                if len(more) < CC_PAGE or len(hits) - off >= need:
                    break
                n += 1
            items += hits[off:off + need]
        total = None if use_cc else len(ts_rows)  # the CC search gives no count
        note = ("Tribunal Supremo / TSR hits first (newest first), then Conselho Constitucional hits "
                "(the CC site's own search; it gives no count)." if use_cc and court != "cc" else "")
        if (lo or hi) and court == "":
            note = "Date filter: Tribunal Supremo and TSR only (the Conselho Constitucional cannot be filtered by date)."
        return Results(items=items, total=total, note=note)

    async def get_decision(self, id):
        id = _http.clean(id)
        m = re.search(r"cconstitucional\.org\.mz/jurisprudencia/([a-z0-9-]+)", id)
        if m:
            return await _cc_decision(m[1])
        uid = _ts_id(id)
        if uid:
            return await _ts_decision(uid)
        if CC_SLUG.match(id):
            return await _cc_decision(id)
        raise BadRequest("Give an id from search_caselaw: a Tribunal Supremo PDF path such as "
                         "'2024/01/Processo-2', or a Conselho Constitucional slug such as "
                         "'acordao-n-o-12-cc-2024-de-2-de-outubro'.")

    async def search_legislation(self, query, *, limit, page, filters):
        words = _words(query)
        if not words:
            raise BadRequest("Give words from the title, in Portuguese, e.g. 'Lei de Trabalho' or '13/2023'.")
        limit = max(1, min(int(limit), 50))
        start = (max(1, int(page)) - 1) * limit
        hits = [h for h in await _laws() if all(w in _fold(h.title) for w in words)]
        return Results(items=hits[start:start + limit], total=len(hits),
                       note="Only the ~110 texts the Tribunal Supremo posts (Constitution, key laws, decrees); "
                            "as published in the Boletim da República, not consolidated. The Código Civil, "
                            "Código de Processo Civil, Lei da Família and similar codes are not "
                            "in this source.")

    async def get_legislation_text(self, id):
        hit, text = await _law(id)
        return LawText(id=hit.id, title=hit.title, text=text, url=hit.url,
                       metadata={k: v for k, v in (("Tipo", hit.type), ("Número", hit.number),
                                                   ("Data", hit.date)) if v})

    async def get_legislation_toc(self, id):
        hit, text = await _law(id)
        toc, _ = _articles(text)
        if not any(e.provision for e in toc):
            raise NotFound(f"Tribunal Supremo: no 'Artigo N' headings could be read in {hit.url} "
                           "(the PDF's text layer lacks them); use get_legislation_text.")
        return Toc(id=hit.id, title=hit.title, url=hit.url, entries=toc)

    async def get_legislation_provision(self, id, provision):
        label = _provision_label(provision)
        if not label:
            raise BadRequest("Give an article, e.g. 'Artigo 5', 'art. 5' or '5'.")
        hit, text = await _law(id)
        _, spans = _articles(text)
        if label not in spans:
            raise NotFound(f"{label} not found in {hit.title} (as read from the PDF's text layer).")
        a, b = spans[label]
        body = "\n".join(text.split("\n")[a:b]).strip()
        return Provision(law_id=hit.id, law_title=hit.title, provision=label, text=body, url=hit.url)
