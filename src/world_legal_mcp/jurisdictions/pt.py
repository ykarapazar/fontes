"""Portugal: case law from DGSI and the Tribunal Constitucional; consolidated
legislation from the Procuradoria-Geral Distrital de Lisboa (PGDL) law base.

Sources (all keyless HTML; verified 2026-11-05):
  * DGSI (www.dgsi.pt, IGFEJ / Ministério da Justiça): Lotus Domino databases, one
    per court (jstj, jsta, jcon, jtrl, jtrp, jtrc, jtrg, jtre, jtca, jtcn).
    Search: GET /{db}.nsf/{view}?SearchView&Query=...&SearchMax=0&Start=N&Count=N
    Document: GET /{db}.nsf/0/{unid}?OpenDocument
  * Tribunal Constitucional (www.tribunalconstitucional.pt): GET search form
    /tc/acordaos/pesquisa.html?...&pesquisa=<q>&page=N and decision pages
    /tc/acordaos/YYYYNNNN.html (Acórdão NNN/YYYY).
  * PGDL (www.pgdlisboa.pt): consolidated texts ("versão actualizada") of
    Portuguese laws, by diploma id `nid` (Código Civil = 775).
    Text: /leis/lei_mostra_articulado.php?nid=N&tabela=leis&ficha=F&pagina=P
    (100 articles per page); whole diploma: /leis/lei_print_articulado.php?nid=N.

Gotchas this code encodes (verified 2026-11-05):
  * DGSI: `?SearchView` must be the first thing after the view UNID, so the URL is
    built by hand (httpx params would put it elsewhere). Dates follow the
    request's Accept-Language (en-GB: DD/MM/YYYY), so DGSI requests send en-US and
    read MM/DD/YYYY in rows, documents and `[DATAAC]` clauses. Wrapping the query
    in parentheses before `AND [DATAAC] ...` gives HTTP 404. The hit count is capped at 1000 ("... 1000 found" means >= 1000).
    SearchOrder=3 is "newest first" by document date, not strictly decision date.
    Search pages are UTF-8, document pages ISO-8859-1 (the header says so).
    Parties are anonymised (AA, BB, ...).
  * DGSI documents are two-column tables (label cell in white bold font, value
    cell); "Decisão Texto Integral" may be missing (summary-only records).
  * TC: 30 hits per page, page index 0-based; the decision HTML is a Word export
    between <div id="acimport"> and "<!-- fim do html (importado) -->". The page
    has no structured date; it is read from the closing "Lisboa, 26 de fevereiro
    de 2026" line.
  * PGDL pages are ISO-8859-1 (~500 KB each). Every page carries a <select
    name="artigo_id"> listing all articles of the diploma in order (used as the
    TOC); an article's position in that list fixes the page it is printed on
    (ficha = 100*k + 1). Article labels mix "Artigo" and "ARTIGO" and have
    suffixes ("Artigo 1067.º-A"). Subject search returns 100 rows per page,
    newest first, with "Resultados: N registos". Code-name search
    (busca=codigo) redirects straight to the diploma page on an exact name.
  * Diário da República (diariodarepublica.pt), the official consolidated
    source, is an OutSystems SPA with no public API; its private, deploy-versioned
    screenservices failed for this client, so it is not used.
"""
from __future__ import annotations

import html as _html
import re
from urllib.parse import quote

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

DGSI = "www.dgsi.pt"
TC = "www.tribunalconstitucional.pt"
PGDL = "www.pgdlisboa.pt"
TC_BASE = f"https://{TC}/tc/acordaos/"
PGDL_LEIS = f"https://{PGDL}/leis/"

# court filter -> (Domino database, search view UNID, court name)
_DB = {
    "stj": ("jstj", "954f0ce6ad9dd8b980256b5f003fa814", "Supremo Tribunal de Justiça"),
    "sta": ("jsta", "35fbbbf22e1bb1e680256f8e003ea931", "Supremo Tribunal Administrativo"),
    "conflitos": ("jcon", "35fbbbf22e1bb1e680256f8e003ea931", "Tribunal dos Conflitos"),
    "trl": ("jtrl", "33182fc732316039802565fa00497eec", "Tribunal da Relação de Lisboa"),
    "trp": ("jtrp", "56a6e7121657f91e80257cda00381fdf", "Tribunal da Relação do Porto"),
    "trc": ("jtrc", "8fe0e606d8f56b22802576c0005637dc", "Tribunal da Relação de Coimbra"),
    "trg": ("jtrg", "86c25a698e4e7cb7802579ec004d3832", "Tribunal da Relação de Guimarães"),
    "tre": ("jtre", "134973db04f39bf2802579bf005f080b", "Tribunal da Relação de Évora"),
    "tca": ("jtca", "170589492546a7fb802575c3004c6d7d", "Tribunal Central Administrativo Sul"),
    "tcn": ("jtcn", "89d1c0288c2dd49c802575c8003279c7", "Tribunal Central Administrativo Norte"),
}
_BY_DB = {db: (key, name) for key, (db, _, name) in _DB.items()}
# last letter of a Portuguese case number's instance suffix (".G1.S2") -> court
_SUFFIX = {"S": "stj", "L": "trl", "P": "trp", "C": "trc", "G": "trg", "E": "tre"}

# DGSI formats dates by Accept-Language (en-GB gives DD/MM/YYYY); pin US order.
_US = {"Accept-Language": "en-US"}
_DOC_ID = re.compile(r"^(j[a-z]+)/([0-9a-f]{32})$", re.I)
_DOC_URL = re.compile(r"dgsi\.pt/(j[a-z]+)\.nsf/[0-9a-f]+/([0-9a-f]{32})", re.I)
_TC_ID = re.compile(r"^(?:tc[:/ ]\s*)?(?:ac[oó]rd[aã]o\s*)?(?:n\.?\s*º?\s*)?(\d{1,4})/(\d{2}|\d{4})$", re.I)
_TC_FILE = re.compile(r"(?:^tc:|acordaos/)(\d{4})(\d{4})(?:\.html)?$", re.I)
_DATE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_MONTHS = {m: i for i, m in enumerate(
    ("janeiro fevereiro março abril maio junho julho agosto setembro outubro novembro dezembro").split(), 1)}


def _us_date(s: str) -> str:
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", s or "")
    return f"{m[3]}-{int(m[1]):02d}-{int(m[2]):02d}" if m else ""


def _strip(fragment: str) -> str:
    """HTML fragment -> one clean line ("<br>" becomes "; ")."""
    s = re.sub(r"(?i)<br\s*/?>", "; ", fragment or "")
    s = re.sub(r"(?i)</?(?:b|i|u|em|strong|font|span|mark|a|sup|sub)\b[^>]*>", "", s)  # inline: no word break
    s = _html.unescape(re.sub(r"<[^>]+>", " ", s))
    s = re.sub(r"\s*;\s*(;\s*)*", "; ", _http.clean(s))
    return s.strip("; ").strip()


_DATE_WINDOW = 20


def _check_date(f: dict, key: str) -> str:
    v = f.get(key, "")
    if v and not _DATE.match(v):
        raise BadRequest(f"{key} must be YYYY-MM-DD.")
    return v


def _year(yy: str) -> str:
    if len(yy) == 4:
        return yy
    return ("20" if int(yy) <= int(_http.today()[2:4]) else "19") + yy


# --------------------------------------------------------------------------- #
# DGSI
# --------------------------------------------------------------------------- #
def _domino_query(q: str) -> str:
    """DGSI answers HTTP 500 when the query starts with a "phrase" and continues with the
    words AND/OR; the symbols & and | mean the same and work (verified 2026-11-12)."""
    if not q.startswith('"'):
        return q
    parts = re.split(r'("[^"]*")', q)
    return "".join(p if p.startswith('"') else re.sub(r"\bAND\b", "&", re.sub(r"\bOR\b", "|", p))
                   for p in parts)


async def _dgsi_search(court: str, query: str, *, start: int, count: int, order: int) -> str:
    db, view, _ = _DB[court]
    url = (f"https://{DGSI}/{db}.nsf/{view}?SearchView&Query={quote(query, safe='')}"
           f"&SearchMax=0&SearchOrder={order}&Start={start}&Count={count}")
    r = await _http.get(url, headers=_US)
    if r.status_code != 200:
        raise SourceError(_http.error("DGSI", "search failed", r.status_code,
                                      "Check the query syntax (Domino full-text: AND, OR, "
                                      "\"phrase\", [FIELD] = value)."), r.status_code)
    return r.text


def _dgsi_rows(page: str, court: str) -> list[DecisionHit]:
    db, _, name = _DB[court]
    out = []
    for row in re.findall(r'(?s)<tr valign="top"[^>]*>(.*?)</tr>', page):
        cells = re.findall(r"(?s)<td[^>]*>(.*?)</td>", row)
        link = re.search(r'href="/[^/]+\.nsf/[0-9a-f]+/([0-9a-f]{32})\?OpenDocument[^"]*">([^<]*)</a>', row)
        if not link or len(cells) < 5:
            continue
        unid, proc = link[1], _http.clean(_html.unescape(link[2]))
        date = _us_date(_strip(cells[1]))
        out.append(DecisionHit(
            id=f"{db}/{unid}",
            title=f"Acórdão do {name}, processo {proc}",
            court=name,
            date=date,
            case_number=proc,
            snippet=_strip(cells[4])[:300] + (f" (relator: {_strip(cells[3])})" if _strip(cells[3]) else ""),
            url=f"https://{DGSI}/{db}.nsf/0/{unid}?OpenDocument",
        ))
    return out


def _dgsi_total(page: str) -> int | None:
    m = re.search(r"<h4>\s*[\d.,]+ documents? returned; ([\d.,]+) found", page) \
        or re.search(r"<h4>\s*([\d.,]+) documents? found", page)
    if not m:
        return 0 if "No documents found" in page else None
    n = int(re.sub(r"\D", "", m[1]))
    return None if n >= 1000 else n


def _dgsi_fields(page: str) -> dict[str, str]:
    """Label -> raw HTML value of a DGSI document's two-column table."""
    labels = list(re.finditer(
        r'<td[^>]*bgcolor="#71B2CF"[^>]*><b><font[^>]*color="#FFFFFF"[^>]*>([^<]+)</font></b></td>', page))
    fields = {}
    for i, m in enumerate(labels):
        end = labels[i + 1].start() if i + 1 < len(labels) else len(page)
        value = re.sub(r"(?s)</td>\s*</tr>\s*(<tr[^>]*>\s*<td[^>]*>\s*<img[^>]*>\s*</td>.*)?$", "",
                       page[m.end():end].strip())
        fields[_http.clean(m[1]).rstrip(" :")] = value
    return fields


# --------------------------------------------------------------------------- #
# Tribunal Constitucional
# --------------------------------------------------------------------------- #
def _tc_search_url(query: str, f: dict, page0: int) -> str:
    def parts(d: str):
        return (d[8:10], d[5:7], d[0:4]) if d else ("", "", "")
    d1, d2 = parts(f.get("date_from", "")), parts(f.get("date_to", ""))
    q = {"acnum": "", "acano": "", "procnum": "", "procano": "", "seccao": "", "especie": "",
         "relator": "", "datadia": d1[0], "datames": d1[1], "dataano": d1[2], "prepesquisa": "",
         "pesquisatipo": "basica", "pesquisa": query, "pesquisanegativa": "",
         "datadia2": d2[0], "datames2": d2[1], "dataano2": d2[2], "page": str(page0)}
    return TC_BASE + "pesquisa.html?" + "&".join(f"{k}={quote(v, safe='')}" for k, v in q.items())


def _tc_rows(page: str) -> list[DecisionHit]:
    """Result rows: [acórdão link, processo, formação, espécie, data, relator] (two
    layouts exist, with and without td classes; the column order is the same)."""
    out = []
    for row in re.findall(r"(?s)<tr[^>]*>(.*?)</tr>", page):
        a = re.search(r'<a href="(\d{8})\.html"[^>]*>(\d+)/\d+</a>', row)
        cells = [_strip(c) for c in re.findall(r"(?s)<td[^>]*>(.*?)</td>", row)]
        if not a or len(cells) < 6:
            continue
        _, proc, form, kind, date, relator = cells[:6]
        bits = [b for b in (kind, form and f"formação: {form}", relator and f"relator: {relator}") if b]
        out.append(DecisionHit(
            id=f"tc:{a[1]}",
            title=f"Acórdão do Tribunal Constitucional n.º {int(a[2])}/{a[1][:4]}",
            court="Tribunal Constitucional",
            date=_http.iso_date(date),
            case_number=proc,
            snippet=", ".join(bits),
            url=f"{TC_BASE}{a[1]}.html",
        ))
    return out


def _tc_file(ident: str) -> str | None:
    m = _TC_FILE.search(ident)
    if m:
        return m[1] + m[2]
    m = _TC_ID.match(ident)
    if m:
        return f"{_year(m[2])}{int(m[1]):04d}"
    return None


def _pt_date(text: str) -> str:
    found = re.findall(r"lisboa,?\s+(\d{1,2})\.?º?\s+de\s+([a-zç]+)\s+de\s+(\d{4})", text.lower())
    for d, mon, y in reversed(found):
        if mon in _MONTHS:
            return f"{y}-{_MONTHS[mon]:02d}-{int(d):02d}"
    return ""


# --------------------------------------------------------------------------- #
# PGDL legislation
# --------------------------------------------------------------------------- #
_LAW_CACHE: dict = {}
_TEXT_CACHE: dict = {}
_CODE_NAMES: dict = {}


def _latin(r) -> str:
    return r.content.decode("cp1252", "replace")


def _nid(ident: str) -> str:
    s = (ident or "").strip()
    m = re.search(r"nid=(\d+)", s) or re.fullmatch(r"(?:pgdl:)?(\d+)", s, re.I)
    if not m:
        raise BadRequest("Give a PGDL diploma id (nid), e.g. 775 for the Código Civil; "
                         "find ids with search_legislation.")
    return m[1]


def _art_label(raw: str) -> str:
    """'ARTIGO 51.º', 'Artigo 1083.º ' -> 'Artigo 51.º', 'Artigo 1083.º'."""
    s = _http.clean(_html.unescape(raw))
    m = re.match(r"(?i)artigo\s+(\d+)\s*\.?\s*º?\s*(-\s*[A-Z]+)?", s)
    if not m:
        return s
    return f"Artigo {m[1]}.º" + (f"-{m[2].strip('- ').upper()}" if m[2] else "")


def _prov_key(label: str) -> str:
    """Comparable key: 'Artigo 1067.º-A', 'art. 1067-a', '1067A' -> '1067A'."""
    s = re.sub(r"(?i)^\s*(artigo|article|art\.?)\s*", "", label or "")
    m = re.match(r"(?i)(\d+)\s*\.?\s*º?\s*-?\s*([a-z]{0,2})\s*$", s.strip())
    return f"{int(m[1])}{m[2].upper()}" if m else ""


async def _pgdl_get(url: str) -> str:
    r = await _http.get(url)
    if r.status_code != 200:
        raise SourceError(_http.error("PGDL", "request failed", r.status_code), r.status_code)
    return _latin(r)


async def _law_page(nid: str, k: int = 0) -> str:
    key = (nid, k)
    if key in _LAW_CACHE:
        return _LAW_CACHE[key]
    page = await _pgdl_get(f"{PGDL_LEIS}lei_mostra_articulado.php?nid={nid}&tabela=leis"
                           f"&ficha={100 * k + 1}&pagina={k + 1}&so_miolo=")
    if 'name="artigo_id"' not in page and "descricaomodulos" not in page:
        raise NotFound(f"PGDL has no diploma with nid={nid}.")
    return _http.lru_put(_LAW_CACHE, key, page, 6)


def _law_title(page: str) -> tuple[str, str]:
    """(title, diploma reference) from a PGDL diploma page."""
    m = re.search(r'(?s)class="descricaomodulos">(.*?)</td>', page)
    divs = [_strip(d) for d in re.findall(r"(?s)<div[^>]*>(.*?)</div>", m[1])] if m else []
    ref = divs[0] if divs else ""
    name = re.sub(r"\s*\(versão actualizada\)\s*$", "", divs[1]) if len(divs) > 1 else ""
    return (f"{name} ({ref})" if name and ref else name or ref), ref


def _articles(page: str) -> list[tuple[str, str, str]]:
    """[(artigo_id, label, heading)] from the article <select>."""
    i = page.find('name="artigo_id"')
    if i < 0:
        return []
    sel = page[i:page.find("</select>", i)]
    out = []
    for aid, raw in re.findall(r'(?s)<option[^>]*value="?(\d+A\w+)"?[^>]*>(.*?)</option>', sel):
        lab, _, head = raw.partition("<br>")
        head = _strip(head).strip("() ")
        out.append((aid, _art_label(lab), head))
    return out


def _untable(html: str) -> str:
    """PGDL lays everything out in tables; turn cells into paragraphs so <br> breaks survive."""
    html = re.sub(r"(?i)</?(table|tbody|tr|th)\b[^>]*>|</td>", "", html)
    return re.sub(r"(?i)<td\b[^>]*>", "<p>", html)


def _last_change(page: str) -> str:
    i = page.find("Contém as seguintes alterações")
    if i < 0:
        return ""
    m = re.search(r'lei_mostra_articulado\.php\?nid=\d+[^"]*">([^<]+)</a>', page[i:i + 20000])
    return _http.clean(m[1]) if m else ""


_CITATION = re.compile(r"(?i)\b(?:decreto[- ]lei|d\.?l\.?|lei)\s*(?:n\.?\s*º\s*)?\d+[\w-]*/\d{2,4}\b")


def _law_hit(nid: str, raw_title: str, summary: str) -> LawHit:
    t = _http.clean(_html.unescape(raw_title))
    m = re.search(r"(?i)\b((?:Decreto-Lei|DL|Decreto Regulamentar|Decreto Legislativo Regional|Lei Orgânica|"
                  r"Lei Constitucional|Lei|Portaria|Decreto|Resolução[\w ]*?|Despacho[\w ]*?|"
                  r"Regulamento[\w ]*?|Aviso|Declaração[\w ]*?))\s+n\.?\s*º\s*([\w-]+/(\d{2,4})),"
                  r"\s*de\s+(\d{1,2})\s+de\s+(\w+)", t)
    typ = num = date = ""
    if m:
        typ, num = m[1], m[2]
        mon = _MONTHS.get(m[5].lower())
        date = f"{_year(m[3])}-{mon:02d}-{int(m[4]):02d}" if mon else ""
    return LawHit(id=nid, title=t, type=typ, number=num, date=date,
                  snippet=_strip(summary)[:300],
                  url=f"{PGDL_LEIS}lei_mostra_articulado.php?nid={nid}&tabela=leis")


class Portugal(Jurisdiction):
    code = "pt"
    name = "Portugal"
    languages = ("pt",)
    aliases = ("portugal", "portuguese", "portugues", "português", "prt")
    sources = (
        Source(
            name="DGSI – Bases Jurídico-Documentais (IGFEJ, Ministério da Justiça)",
            url="https://www.dgsi.pt",
            covers=("caselaw",),
            licence=("no published terms; court decisions are excluded from copyright "
                     "(Código do Direito de Autor, art. 7) — unverified for the database itself"),
            commercial_use=None,   # no terms page found
            ai_use=None,           # robots.txt 404 (2026-11-05); no AI/TDM clause found
            auth="none",
            rate_limit="unknown; 1 s spacing; occasional empty replies seen (2026-11)",
            terms_url="",
        ),
        Source(
            name="Tribunal Constitucional – Acórdãos",
            url="https://www.tribunalconstitucional.pt/tc/acordaos/",
            covers=("caselaw",),
            licence=("reproduction authorised for private purposes, citing the source and that "
                     "the online text is not authentic (page footer)"),
            commercial_use=False,  # only private-purpose reproduction is authorised
            ai_use=None,           # robots.txt empty (2026-11-05); no AI/TDM clause
            auth="none",
            rate_limit="unknown; 1 s spacing, no throttling seen (2026-11)",
            terms_url="https://www.tribunalconstitucional.pt/tc/infolegal.html",
        ),
        Source(
            name=("PGDL – Legislação (Procuradoria-Geral Distrital de Lisboa, Ministério Público); "
                  "unofficial consolidations"),
            url="https://www.pgdlisboa.pt/leis/lei_main.php",
            covers=("legislation",),
            licence=("© PGDL, 'Todos os direitos reservados' (footer); statutory texts themselves "
                     "are excluded from copyright (CDADC art. 7)"),
            commercial_use=None,   # all rights reserved notice, no reuse terms
            ai_use=None,           # robots.txt 404 (2026-11-05); no AI/TDM clause
            auth="none",
            rate_limit="unknown; 1 s spacing; pages are 0.5 MB, the full Código Civil 5 MB",
            terms_url="",
            warning=("Unofficial consolidated texts kept by a public prosecutor's office; only "
                     "the Diário da República is authentic. 'All rights reserved' and no reuse "
                     "terms: ask PGDL before systematic or commercial reuse."),
            official=False,
        ),
    )
    caselaw_filters = {
        "court": ("stj (default), sta, conflitos, trl, trp, trc, trg, tre, tca (TCA Sul), "
                  "tcn (TCA Norte) — DGSI; tc — Tribunal Constitucional"),
        "date_from": "YYYY-MM-DD (decision date)",
        "date_to": "YYYY-MM-DD",
        "sort": "relevance (default) or date (DGSI only; newest first among the 20 most relevant hits)",
    }
    legislation_filters = {}
    min_interval = {DGSI: 1.0, TC: 1.0, PGDL: 1.0}
    notes = ("Case law: DGSI (STJ, STA, Relações, TCAs, Conflitos) with Domino full-text "
             "syntax — words, AND/OR, \"phrase\", [PROCESSO] = \"...\"; Tribunal Constitucional via "
             "its own site (court=tc). Ids: 'jstj/<unid>', 'tc:20260205'; case numbers like "
             "2478/16.1T8GMR.G1.S2 and 'tc:205/2026' also work. Legislation: unofficial PGDL "
             "consolidations by nid (Código Civil = 775); provisions as 'Artigo 1022.º', '1022', "
             "'art. 1067-A'.")
    gaps = (
        ("Diário da República (official, authentic consolidated texts): SPA with no public API; its"
         " private endpoints failed for our client"),
        ("Official legislation text: PGDL consolidations used here are unofficial; only the Diário "
         "da República is authentic"),
        ("DGSI decisions: a selection, not every decision; some records are summary-only (no full "
         "text published)"),
        "First-instance courts: not researched yet",
        "Regional law (Azores, Madeira): not researched yet",
    )
    samples = {
        "caselaw_query": "arrendamento",
        "decision_id": "jstj/28e9313db456f62880258354005e7fba",  # STJ 2478/16.1T8GMR.G1.S2, 2018-11-27
        "legislation_query": "Código Civil",
        "law_id": "775",
        "provision": "Artigo 1022.º",
    }

    # ------------------------------------------------------------------ #
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        f = {k: str(v).strip() for k, v in (filters or {}).items() if str(v).strip()}
        query = (query or "").strip()
        court = f.get("court", "stj").lower()
        if court != "tc" and court not in _DB:
            raise BadRequest(f"Unknown court {court!r}. Use: {', '.join(_DB)} or tc.")
        d1, d2 = _check_date(f, "date_from"), _check_date(f, "date_to")
        sort = f.get("sort", "relevance").lower()
        if sort not in ("relevance", "date"):
            raise BadRequest("sort must be relevance or date.")
        limit = max(1, min(int(limit), 50))
        page = max(1, int(page))
        start = (page - 1) * limit

        if court == "tc":
            if not query:
                raise BadRequest("Give search words for the Tribunal Constitucional.")
            items, total = [], None
            for p0 in range(start // 30, (start + limit - 1) // 30 + 1):
                html = await _http.get(_tc_search_url(query, f, p0))
                if html.status_code != 200:
                    raise SourceError(_http.error("Tribunal Constitucional", "search failed",
                                                  html.status_code), html.status_code)
                rows = _tc_rows(html.text)
                m = re.search(r"#\s*\d+/(\d+)\s*resultado", html.text)
                total = int(m[1]) if m else (0 if not rows else total)
                items += [(p0 * 30 + i, h) for i, h in enumerate(rows)]
                if len(rows) < 30:
                    break
            items = [h for i, h in items if start <= i < start + limit]
            return Results(items=items, total=total,
                           note="Tribunal Constitucional basic search; 30 hits per source page.")

        parts = []
        if query:
            parts.append(query)  # "(x) AND [DATAAC] ..." gives HTTP 404
        if d1:
            parts.append(f"[DATAAC] >= {d1[5:7]}/{d1[8:10]}/{d1[0:4]}")
        if d2:
            parts.append(f"[DATAAC] <= {d2[5:7]}/{d2[8:10]}/{d2[0:4]}")
        if not parts:
            raise BadRequest("Give search words or a date filter.")
        q = _domino_query(" AND ".join(parts))
        if sort == "date":
            # SearchOrder=3 sorts every full-text hit (443 for a tenancy query, many only
            # mention the words in passing). Take the most relevant window, sort that by date.
            html = await _dgsi_search(court, q, start=1, count=_DATE_WINDOW, order=1)
            total = _dgsi_total(html)
            rows = sorted(_dgsi_rows(html, court), key=lambda h: h.date or "", reverse=True)
            if total is not None and total <= _DATE_WINDOW:
                note = f"Sorted by date (newest first); all {total} hits are included. "
            else:
                note = (f"NOT a complete date-ordered list: only the {_DATE_WINDOW} most relevant "
                        f"of {total if total is not None else 'many'} hits are sorted by date "
                        "(newest first); a newer decision ranked lower by relevance is not shown. "
                        "Narrow the query or use date_from/date_to to reach it. ")
            return Results(items=rows[start:start + limit], total=min(total, _DATE_WINDOW)
                           if total is not None else None, note=note)
        html = await _dgsi_search(court, q, start=start + 1, count=limit, order=1)
        total = _dgsi_total(html)
        note = "Domino full-text: words, AND/OR, \"phrase\", [PROCESSO] = \"case no.\"."
        if total is None:
            note += " The source reports at most 1000 hits; refine the query to see a count."
        return Results(items=_dgsi_rows(html, court), total=total, note=note)

    # ------------------------------------------------------------------ #
    async def get_decision(self, id):
        ident = (id or "").strip()
        tc = _tc_file(ident) if (ident.lower().startswith("tc") or "tribunalconstitucional" in ident) else None
        if tc:
            return await self._tc_decision(tc, ident)
        m = _DOC_ID.match(ident) or _DOC_URL.search(ident)
        if m:
            db, unid = m[1].lower(), m[2].lower()
            if db not in _BY_DB:
                raise BadRequest(f"Unknown DGSI database {db!r}. Known: {', '.join(_BY_DB)}.")
        elif re.fullmatch(r"[\w./-]+/\d{2}\.[\w.-]+", ident):  # Portuguese case number
            inst = re.findall(r"\.([A-Z])\d+", ident.upper())  # ".G1.S2" -> S, ".L1-9" -> L
            court = _SUFFIX.get(inst[-1] if inst else "S", "stj")
            html = await _dgsi_search(court, f'[PROCESSO] = "{ident}"', start=1, count=1, order=1)
            hits = _dgsi_rows(html, court)
            if not hits:
                raise NotFound(f"DGSI ({_DB[court][2]}) has no decision with processo {ident}.")
            db, unid = hits[0].id.split("/")
        else:
            raise BadRequest("Give a DGSI id like 'jstj/28e9313db456f62880258354005e7fba', a "
                             "case number like 2478/16.1T8GMR.G1.S2, or a TC id like "
                             "'tc:20260205' / 'tc:205/2026'.")
        url = f"https://{DGSI}/{db}.nsf/0/{unid}?OpenDocument"
        r = await _http.get(url, headers=_US)
        if r.status_code == 404 or (r.status_code == 200 and "Processo" not in r.text):
            raise NotFound(f"DGSI has no document {db}/{unid}.")
        if r.status_code != 200:
            raise SourceError(_http.error("DGSI", f"document {db}/{unid} failed", r.status_code),
                              r.status_code)
        fields = _dgsi_fields(r.text)
        court = _BY_DB[db][1]
        summary = _http.html_to_md(fields.pop("Sumário", ""))
        full = _http.html_to_md(fields.pop("Decisão Texto Integral", ""))
        text = "\n\n".join(p for p in (summary and f"## Sumário\n\n{summary}",
                                       full and f"## Texto integral\n\n{full}") if p)
        if not text:
            raise SourceError(f"Error (DGSI): no text in document {db}/{unid}.")
        proc = _strip(fields.pop("Processo", ""))
        date = ""
        for k in list(fields):
            if k.startswith("Data d"):
                date = date or _us_date(_strip(fields[k]))
                fields.pop(k)
        meta = {k: _strip(v) for k, v in fields.items() if k not in ("Texto Integral", "Privacidade")}
        if ident != f"{db}/{unid}":
            meta["Resolved from"] = ident
        return Decision(
            id=f"{db}/{unid}",
            title=f"Acórdão do {court}, processo {proc}",
            text=text,
            url=url,
            court=court,
            date=date,
            case_number=proc,
            summary=summary,
            metadata={k: v for k, v in meta.items() if v},
        )

    async def _tc_decision(self, file: str, ident: str) -> Decision:
        url = f"{TC_BASE}{file}.html"
        r = await _http.get(url)
        i = r.text.find('id="acimport"') if r.status_code == 200 else -1
        if r.status_code == 404 or (r.status_code == 200 and i < 0):
            raise NotFound(f"Tribunal Constitucional has no Acórdão page {file}.html.")
        if r.status_code != 200:
            raise SourceError(_http.error("Tribunal Constitucional", f"decision {file} failed",
                                          r.status_code), r.status_code)
        j = r.text.find("<!-- fim do html (importado) -->", i)
        text = _http.html_to_md(r.text[i + len('id="acimport">'):j if j > 0 else None])
        if not text:
            raise SourceError(f"Error (Tribunal Constitucional): empty decision {file}.")
        num = f"{int(file[4:])}/{file[:4]}"
        proc = re.search(r"(?i)Processo\s+n\.?\s*º\s*([\d]+/\d+)", text)
        meta = {"Resolved from": ident} if ident != f"tc:{file}" else {}
        return Decision(
            id=f"tc:{file}",
            title=f"Acórdão do Tribunal Constitucional n.º {num}",
            text=text,
            url=url,
            court="Tribunal Constitucional",
            date=_pt_date(text),
            case_number=proc[1] if proc else "",
            metadata=meta,
        )

    # ------------------------------------------------------------------ #
    async def _code_name_hit(self, query: str) -> LawHit | None:
        """Exact common name of a code ('Código Civil') -> that diploma, via busca=codigo."""
        if "names" not in _CODE_NAMES:
            main = await _pgdl_get(f"{PGDL_LEIS}lei_main.php")
            sel = re.search(r'(?s)<select[^>]*name="?buscacodigo"?[^>]*>(.*?)</select>', main)
            _CODE_NAMES["names"] = {_http.clean(_html.unescape(n)).casefold(): _http.clean(_html.unescape(n))
                                    for n in re.findall(r"<option[^>]*>([^<]+)", sel[1] if sel else "")
                                    if n.strip()}
            for k, n in list(_CODE_NAMES["names"].items()):  # "... Urbano (NRAU)" also by either part
                m = re.fullmatch(r"(.+?)\s*\(([^)]+)\)", k)
                if m:
                    _CODE_NAMES["names"].setdefault(m[1], n)
                    _CODE_NAMES["names"].setdefault(m[2], n)
        names = _CODE_NAMES["names"]
        # a citation after the name ("Código Penal Decreto-Lei 400/82") is not part of the name
        key = _http.clean(_CITATION.sub(" ", query)).casefold()
        key = _http.clean(key)
        if key == "arrendamento urbano":
            key = "novo regime do arrendamento urbano"
        # PGDL lists the Penal Code only as "Código Penal de 1982 Versão consolidada posterior a 1995"
        if key == "código penal" and key not in names:
            key = "código penal de 1982 versão consolidada posterior a 1995"
        name = names.get(key)
        if not name:
            return None
        page = await _pgdl_get(f"{PGDL_LEIS}lei_busca.php?busca=codigo&buscacodigo="
                               f"{quote(name, safe='', encoding='cp1252', errors='replace')}")
        m = re.search(r'var nidlei\s*=\s*"(\d+)"', page)
        if not m:
            return None
        title, ref = _law_title(page)
        _http.lru_put(_LAW_CACHE, (m[1], 0), page, 6)
        base = _law_hit(m[1], ref, "")
        if key == "código penal de 1982 versão consolidada posterior a 1995":
            return LawHit(id=m[1], title=title or ref, type="DL", number="400/82", date="1982-09-23",
                          snippet=("exact code-name match. Code = Decreto-Lei n.º 400/82, de 23 de "
                                   "Setembro; this is its consolidated text after the republication by "
                                   "Decreto-Lei n.º 48/95, de 15 de Março (cite DL 400/82, as amended)"),
                          url=base.url)
        return LawHit(id=m[1], title=title or ref, type=base.type, number=base.number,
                      date=base.date, snippet="exact code-name match", url=base.url)

    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        query = (query or "").strip()
        if not query:
            raise BadRequest("Give words to search PGDL legislation summaries, or a code name "
                             "such as 'Código Civil'.")
        limit = max(1, min(int(limit), 50))
        page = max(1, int(page))
        start = (page - 1) * limit
        items: list[LawHit] = []
        if page == 1:
            hit = await self._code_name_hit(query)
            if hit:
                items.append(hit)
        q = quote(query, safe="", encoding="cp1252", errors="replace")
        rows, total = [], None
        for k in range(start // 100, (start + limit - 1) // 100 + 1):
            html = await _pgdl_get(f"{PGDL_LEIS}lei_busca_assunto.php?buscajur={q}&exacta=&artigos="
                                   f"&ficha={100 * k + 1}&pagina={k + 1}&so_miolo=")
            m = re.search(r"Resultados:(?:&nbsp;|\s|<i>)*(\d+)", html)
            total = int(m[1]) if m else total
            found = re.findall(r'(?s)<b>\d+\.\s*<span[^>]*>.*?href=lei_mostra_articulado\.php\?nid=(\d+)'
                               r'&tabela=leis[^>]*>\((.*?)\)</a>.*?class=txt_base_n_l colspan=2>(.*?)<a', html)
            rows += [(k * 100 + i, r) for i, r in enumerate(found)]
            if len(found) < 100:
                break
        seen = {h.id for h in items}
        items += [_law_hit(*r) for i, r in rows if start <= i < start + limit and r[0] not in seen]
        return Results(items=items[:limit], total=total if total is not None else len(items),
                       note=("PGDL subject search over diploma summaries, newest first. An exact code "
                             "name (e.g. 'Código Civil') is matched first. "
                             "Unofficial consolidations."))

    async def get_legislation_toc(self, id):
        nid = _nid(id)
        page = await _law_page(nid)
        title, _ = _law_title(page)
        entries = [TocEntry(f"{lab} - {head}" if head else lab, 0, lab) for _, lab, head in _articles(page)]
        return Toc(id=nid, title=title, url=f"{PGDL_LEIS}lei_mostra_articulado.php?nid={nid}&tabela=leis",
                   entries=entries)

    async def get_legislation_provision(self, id, provision):
        nid = _nid(id)
        key = _prov_key(provision)
        if not key:
            raise BadRequest("Give an article like 'Artigo 1022.º', '1022' or 'art. 1067-A'.")
        page = await _law_page(nid)
        arts = _articles(page)
        pos = next((i for i, (_, lab, _) in enumerate(arts) if _prov_key(lab) == key), None)
        if pos is None:
            raise NotFound(f"PGDL diploma {nid} has no article {provision!r}; see get_legislation_toc.")
        aid, label, _ = arts[pos]
        if pos >= 100:
            page = await _law_page(nid, pos // 100)
        chunk = next((c for c in page.split('<table class="artigo"')
                      if f'div_cria_anotacao_{aid}"' in c), "")
        if not chunk:
            raise SourceError(f"Error (PGDL): article {label} not found on its page.")
        start = chunk.find("<td class=txt_base_b_l>")  # the article heading (drops preamble/sections)
        chunk = chunk[max(start, 0):chunk.find('<DIV id="div_cria_anotacao')]
        title, _ = _law_title(page)
        url = (f"{PGDL_LEIS}lei_mostra_articulado.php?artigo_id={aid}&nid={nid}&tabela=leis"
               f"&pagina={pos // 100 + 1}&ficha={100 * (pos // 100) + 1}#artigo")
        return Provision(law_id=nid, law_title=title, provision=label,
                         text=_http.html_to_md(_untable(chunk)), url=url)

    async def get_legislation_text(self, id):
        nid = _nid(id)
        if nid not in _TEXT_CACHE:
            html = await _pgdl_get(f"{PGDL_LEIS}lei_print_articulado.php?tabela=leis&artigo_id=&nid={nid}&nversao=")
            body = html[html.find("<!-- Cabeçalho do diploma -->"):] if "Cabeçalho do diploma" in html else html
            # one diploma is up to 5 MB of loosely nested HTML: convert cell by cell
            # (a single html_to_md call hits Python's recursion limit)
            cells = re.split(r"(?i)(?=<td\b)", body)
            text = "\n\n".join(md for c in cells if (md := _http.html_to_md(_untable(c))))
            _http.lru_put(_TEXT_CACHE, nid, text, 2)
        text = _TEXT_CACHE[nid]
        if len(text) < 50:
            raise NotFound(f"PGDL has no diploma with nid={nid}.")
        page = await _law_page(nid)
        title, ref = _law_title(page)
        meta = {"Diploma": ref, "Latest amendment listed": _last_change(page),
                "Status": "unofficial consolidation (PGDL)"}
        return LawText(id=nid, title=title, text=text,
                       url=f"{PGDL_LEIS}lei_mostra_articulado.php?nid={nid}&tabela=leis",
                       metadata={k: v for k, v in meta.items() if v})
