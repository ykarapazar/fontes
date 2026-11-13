"""Benin: Cour constitutionnelle decisions (courconstitutionnelle.bj) and the laws, decrees and
ordinances published by the Secrétariat général du Gouvernement (sgg.gouv.bj). French.

How the sources work (verified 2026-11-06, UK IP, honest User-Agent):

Case law, Cour constitutionnelle (~6,500 ordinary "DCC" decisions plus electoral EL/EP/EG ones,
1990s to date):
  * GET /fr/search-decision with decision_number ("DCC18-062") or applicant (requérant name),
    or decision_type (1 DCC, 2 EL, 3 EP, 6 EG) alone. The keyword field (search=) is broken on the
    site's side (HTTP 500, "Impossible to connect, please check your Algolia Application Id"), and
    when applicant and decision_type/dates are combined the site ignores all but the type, so only
    one criterion is sent. /fr/decision-type/<slug>/<year> lists one type for one year.
    10 cards per page (&page=n), "Total : N décisions".
  * The id is the decision number ("DCC20-001"); /fr/decisions/<id> names the PDF
    (/files/decisions/DCC20-001_26_janvier_2020.pdf). The PDFs carry an OCR text layer (some
    OCR noise); the court publishes parties' names.

Legislation, Secrétariat général du Gouvernement (official gazette publisher):
  * GET /recherche/?type=loi|decret|ordonnance|accord|decision&keywords=&begin=&end=&offset=<page>
    (20 per page, "Documents retrouvés (N)"). Keywords match title and description.
  * The id is the site's slug ("loi-98-004", "decret-2026-649"); /doc/<id>/ has the title and
    /doc/<id>/download the PDF. The PDF is the text as promulgated (not consolidated). Older PDFs
    carry an OCR text layer; many recent ones are image-only scans with no text: those return a
    SourceError pointing at the PDF (no OCR here).

Terms and robots.txt (2026-11-06):
  * courconstitutionnelle.bj: robots.txt "User-agent: * / Disallow:" (allow all, no Crawl-delay).
    No terms / mentions légales page; footer "© Cour Constitutionnelle du Bénin - 2023".
  * sgg.gouv.bj: robots.txt "User-agent: * / Disallow:" (allow all, no Crawl-delay).
    /mentions-legales/ exists but has no text; footer "© Présidence de la République du Bénin - 2026".

Not used:
  * legis.cdij.bj (CDIJ, Ministry of Justice law database): robots.txt allows all, but its
    mentions légales say "Toute reproduction, distribution, modification, adaptation, retransmission
    ou publication, même partielle, de ces éléments est strictement interdite sans l'accord écrit du
    Centre de Documentation et d'Information Juridique" -> needs permission; not built.
  * cdij.bj: "L'utilisateur ne peut en aucune manière réutiliser, céder ou exploiter pour son propre
    compte tout ou partie des éléments ou travaux du Site" -> not used.
  * coursupreme.bj: no decisions published on the site (static page only).
  * assemblee-nationale.bj: "Site en maintenance" (503). cour-constitutionnelle.bj: no DNS.
"""
from __future__ import annotations

import re
from urllib.parse import urlencode

from lxml import html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc, TocEntry

CC_HOST = "courconstitutionnelle.bj"
CC_BASE = f"https://{CC_HOST}/fr"
CC_SEARCH = CC_BASE + "/search-decision"
CC_DEC = CC_BASE + "/decisions/{id}"
CC_NAME = "Cour constitutionnelle"
CC_PAGE = 10                     # fixed by the source
CC_TYPES = {"DCC": ("1", "decisions-ordinaires-dcc"), "EL": ("2", "decisions-electorales-legislatives-el"),
            "EP": ("3", "decisions-electorales-presidentielles-ep"),
            "EG": ("6", "decisions-electorales-generales-eg")}

SGG_HOST = "sgg.gouv.bj"
SGG_BASE = f"https://{SGG_HOST}"
SGG_SEARCH = SGG_BASE + "/recherche/"
SGG_DOC = SGG_BASE + "/doc/{id}/"
SGG_PDF = SGG_BASE + "/doc/{id}/download"
SGG_NAME = "Secrétariat général du Gouvernement"
SGG_PAGE = 20                    # fixed by the source
SGG_TYPES = ("loi", "decret", "ordonnance", "accord", "decision")

MAX_PDF = 40_000_000
MONTHS = {"janv": 1, "fevr": 2, "mars": 3, "avr": 4, "mai": 5, "juin": 6, "juil": 7, "aout": 8,
          "sept": 9, "oct": 10, "nov": 11, "dec": 12}
_DEC_ID = re.compile(r"^(DCC|EL|EP|EG)\s*(\d{2})\s*-\s*(\d{1,4})$", re.I)
_LAW_ID = re.compile(r"^(loi|decret|ordonnance|accord|decision|arrete)-[0-9a-z][0-9a-z-]{1,40}$")
_ARTICLE = re.compile(r"^(?:Article|ARTICLE|Art\.)\s*(\d+(?:\s*(?:bis|ter|quater|nouveau))?|premier|1er|ler)"
                      r"(?![\w])\s*[:.\-–—]*\s*(.*)$")
_HEADING = re.compile(r"^(TITRE|CHAPITRE|Chapitre|SECTION|Section|LIVRE|Livre|Titre|Paragraphe)\b")
_BREAK_BEFORE = re.compile(r"^(Considérant|CONSIDERANT|Vu |VU |Saisie|Ensemble|Ouï|Après en avoir|"
                           r"Sur |DECIDE|DÉCIDE|Que |Mais |En conséquence|La présente décision|"
                           r"Ont siégé|Le Rapporteur|Le Président)")

_cache: dict = {}


def _fold(s: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def fr_date(s: str) -> str:
    """First '26 février 2026' / '27 janv. 1998' / '1er août 1990' in s -> ISO; else ''."""
    m = re.search(r"\b(\d{1,2})(?:er)?[\s_-]+(janv|fevr|mars|avr|mai|juin|juil|aout|sept|oct|nov|dec)"
                  r"[a-z]*\.?[\s_-]+(\d{4})\b", _fold(s))
    if not m or not 1 <= int(m[1]) <= 31:
        return ""
    return f"{int(m[3]):04d}-{MONTHS[m[2]]:02d}-{int(m[1]):02d}"


def reflow(text: str) -> str:
    """pdf_text lines (hard-wrapped) -> paragraphs: join a line to the previous one unless the
    previous ends a sentence/clause or the line starts an article, heading or decision section."""
    out: list[str] = []
    for block in text.split("\n\n"):              # pdf_text separates pages by a blank line
        for ln in block.split("\n"):
            ln = ln.strip()
            if not ln or re.fullmatch(r"[-_\s\d]{1,6}|Page \d+ sur \d+", ln):   # page numbers, rules
                continue
            starts = bool(_ARTICLE.match(ln) or _HEADING.match(ln) or _BREAK_BEFORE.match(ln))
            if out and not starts and not re.search(r"[.;:!?»]$", out[-1]) and not _HEADING.match(out[-1]):
                out[-1] = out[-1].rstrip("-") + ("" if out[-1].endswith("-") else " ") + ln
            else:
                out.append(ln)
    return "\n\n".join(out)


async def _pdf(url: str, source: str) -> str:
    """Download a PDF (size checked first, 40 MB cap) and return its reflowed text ('' if no text layer)."""
    if url in _cache:
        return _cache[url]
    h = await _http.request("HEAD", url)
    if h.status_code == 404:
        raise NotFound(f"No document at {url}.")
    if h.status_code != 200:
        raise SourceError(_http.error(source, "PDF not available", h.status_code), h.status_code)
    size = int(h.headers.get("content-length") or 0)
    if not size or size > MAX_PDF:
        raise SourceError(f"Error ({source}): PDF size {'unknown' if not size else f'{size // 1_000_000} MB'}"
                          f" (cap 40 MB). Open {url}.")
    r = await _http.get(url)
    if r.status_code != 200 or not r.content.startswith(b"%PDF"):
        raise SourceError(_http.error(source, "PDF download failed", r.status_code), r.status_code)
    text = reflow(_http.pdf_text(r.content))
    return _http.lru_put(_cache, url, text, 16)


def _page_window(limit: int, page: int, size: int) -> tuple[int, int, int]:
    limit = max(1, min(int(limit), 30))
    start = (max(1, int(page)) - 1) * limit
    return limit, start, start // size + 1


# --------------------------------------------------------------------------- #
# Cour constitutionnelle
# --------------------------------------------------------------------------- #
def _norm_dec_id(s: str) -> str:
    m = _DEC_ID.match(_http.clean(s).replace(" ", "") if s else "")
    if not m:
        raise BadRequest("A decision id is the Cour constitutionnelle number, e.g. 'DCC20-001', "
                         "'EP21-010' (types DCC, EL, EP, EG).")
    return f"{m[1].upper()}{m[2]}-{int(m[3]):03d}"


def _cc_hits(h: str) -> tuple[list[DecisionHit], int | None]:
    doc = lhtml.fromstring(h)
    hits = []
    for card in doc.xpath('//div[contains(@class, "card-body")][.//a[contains(@href, "/fr/decisions/")]]'):
        href = card.xpath('.//a[contains(@href, "/fr/decisions/")]/@href')[0]
        did = href.rstrip("/").rsplit("/", 1)[-1]
        head = _http.clean(" ".join(card.xpath('.//h4//text()')))
        fields: dict[str, str] = {}
        for p in card.xpath('.//p[contains(@class, "card-text")]'):
            txt = "".join(p.itertext())
            for m in re.finditer(r"(Type de décision|Requérant|Table analytique|Index matière|Objet de la requête)"
                                 r"\s*:\s*(.*?)(?=(?:Type de décision|Requérant|Table analytique|Index matière|"
                                 r"Objet de la requête)\s*:|Lire|$)", txt, re.S):
                fields[m[1]] = _http.clean(m[2])
        title = f"{CC_NAME} (Bénin), décision {head or did}"
        snip = "; ".join(f"{k}: {v}" for k, v in fields.items() if v and k != "Type de décision")
        hits.append(DecisionHit(id=did, title=title, court=CC_NAME, date=fr_date(head), case_number=did,
                                snippet=snip[:400], url=CC_DEC.format(id=did)))
    m = re.search(r"Total\s*:\s*(\d+)\s*d", h)
    return hits, (int(m[1]) if m else None)


async def _cc_decision_page(did: str) -> dict:
    key = ("cc", did)
    if key in _cache:
        return _cache[key]
    r = await _http.get(CC_DEC.format(id=did))
    if r.status_code in (404, 500):
        raise NotFound(f"No Cour constitutionnelle decision '{did}' (the source answers HTTP 500 for unknown ids).")
    if r.status_code != 200:
        raise SourceError(_http.error(CC_NAME, "decision page failed", r.status_code), r.status_code)
    doc = lhtml.fromstring(r.text)
    h1 = doc.xpath('//h1[contains(@class, "card-title")]')
    pdf = doc.xpath('//a[contains(@href, "/files/decisions/")]/@href')
    if not h1:
        raise NotFound(f"No Cour constitutionnelle decision '{did}'.")
    meta: dict[str, str] = {}
    for h2 in doc.xpath('//div[contains(@class, "card-body")]/h2'):
        t = _http.clean(h2.text_content())
        if ":" in t:
            k, v = t.split(":", 1)
            meta[_http.clean(k)] = _http.clean(v)
        elif t:
            meta["Type de décision"] = t
    info = {"head": _http.clean(h1[0].text_content()), "pdf": pdf[0] if pdf else "", "meta": meta}
    return _http.lru_put(_cache, key, info, 32)


# --------------------------------------------------------------------------- #
# Secrétariat général du Gouvernement
# --------------------------------------------------------------------------- #
def _norm_law_id(s: str) -> str:
    s = _fold(_http.clean(s)).strip("/ ")
    s = re.sub(r"^https?://sgg\.gouv\.bj/doc/", "", s).split("/")[0]
    m = re.match(r"^(loi|decret|ordonnance)\s*(?:n\s*[°o]?\s*)?(\d{2,4}\s*-\s*\d+)$", s)
    if m:
        s = f"{m[1]}-{m[2].replace(' ', '')}"
    elif re.fullmatch(r"\d{2,4}-\d{1,4}", s):
        s = "loi-" + s
    if not _LAW_ID.match(s):
        raise BadRequest("A law id is the SGG slug from search_legislation, e.g. 'loi-98-004' "
                         "or 'decret-2026-649' ('98-004' is read as a loi).")
    return s


def _sgg_hits(h: str) -> tuple[list[LawHit], int | None]:
    doc = lhtml.fromstring(h)
    hits = []
    for a in doc.xpath('//aside[contains(@class, "doc")]'):
        link = a.xpath('.//a[contains(@class, "doc-title")]')
        if not link:
            continue
        lid = link[0].get("href", "").strip("/").rsplit("/", 1)[-1]
        head = _http.clean(link[0].text_content())
        desc = _http.clean(" ".join(a.xpath('.//p[contains(@class, "doc-desc")]//text()')))
        typ = _http.clean(" ".join(a.xpath('.//i[contains(@class, "cat")]//text()')))
        num = _http.clean(" ".join(a.xpath('.//i[contains(@class, "num")]//text()')))
        size = next((_http.clean(b.text_content()) for b in a.xpath('.//b')
                     if re.search(r"\b(Ko|Mo)$", b.text_content())), "")
        hits.append(LawHit(id=lid, title=f"{head} {desc}".strip(), type=typ.capitalize(), number=num,
                           date=fr_date(head), snippet=f"PDF {size}" if size else "",
                           url=SGG_DOC.format(id=lid)))
    m = re.search(r"Documents retrouvés\s*\((\d+)\)", h)
    return hits, (int(m[1]) if m else None)


async def _sgg_law(lid: str) -> dict:
    key = ("sgg", lid)
    if key in _cache:
        return _cache[key]
    url = SGG_DOC.format(id=lid)
    r = await _http.get(url)
    if r.status_code == 404:
        raise NotFound(f"No document '{lid}' at sgg.gouv.bj." + (
            " The Code pénal (Loi 2018-16) is not published on this site, and no other official "
            "source for it is wired in." if lid == "loi-2018-16" else ""))
    if r.status_code != 200:
        raise SourceError(_http.error(SGG_NAME, "document page failed", r.status_code), r.status_code)
    doc = lhtml.fromstring(r.text)
    h1 = doc.xpath('//div[@id="banner"]//h1')
    if not h1 or not doc.xpath('//a[@id="btnDownload"]'):
        raise NotFound(f"No document '{lid}' at sgg.gouv.bj.")
    desc = doc.xpath('//div[@id="banner"]//h1/following-sibling::p[1]')
    title = _http.clean(h1[0].text_content() + " " + (desc[0].text_content() if desc else ""))
    pdf = SGG_PDF.format(id=lid)
    text = await _pdf(pdf, SGG_NAME)
    if not text:
        raise SourceError(f"Error ({SGG_NAME}): '{lid}' is a scanned PDF without a text layer "
                          f"(no OCR here). Open {pdf}.")
    return _http.lru_put(_cache, key, {"title": title, "url": url, "text": text}, 16)


def _norm_prov(p: str) -> str:
    s = _fold(_http.clean(p))
    s = re.sub(r"^(article|art\.?)\s*", "", s).strip(" .:-")
    s = {"premier": "1", "1er": "1", "ler": "1"}.get(s, s)
    return re.sub(r"\s+", " ", s)


def _ocr_unreliable(labels: list[str]) -> bool:
    """True when the article numbers found do not run 1, 2, 3 ... upward: the scan's OCR is garbled."""
    nums = [int(x) for x in labels if x.isdigit()]
    return bool(nums) and (nums[0] != 1 or any(b < a for a, b in zip(nums, nums[1:])))


_OCR_WARN = ("The article headings below come from OCR of a scan and are garbled or incomplete (numbers out of "
             "order or missing); whether any article exists cannot be confirmed from them. ")


class Benin(Jurisdiction):
    code = "bj"
    name = "Benin"
    languages = ("fr",)
    aliases = ("bénin", "benin", "ben")
    sources = (
        Source(
            name="Cour constitutionnelle du Bénin: décisions (courconstitutionnelle.bj)",
            url=CC_BASE + "/decisions",
            covers=("caselaw",),
            licence="no terms published; footer '© Cour Constitutionnelle du Bénin - 2023'",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~20 requests (2026-11)",
            terms_url=CC_BASE,
        ),
        Source(
            name="Secrétariat général du Gouvernement du Bénin: lois, décrets, ordonnances (sgg.gouv.bj)",
            url=SGG_BASE + "/documentheque/lois/",
            covers=("legislation",),
            licence="no terms (mentions légales page is empty); footer "
                    "'© Présidence de la République du Bénin - 2026'",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~20 requests (2026-11)",
            terms_url=SGG_BASE + "/mentions-legales/",
            warning="Texts as promulgated, not consolidated; many recent PDFs are image-only scans "
                    "with no extractable text.",
        ),
    )
    caselaw_filters = {
        "type": "DCC (ordinary), EL (legislative elections), EP (presidential), EG (general elections); "
                "only with an empty query",
        "year": "decision year, e.g. 2025, or a range 2022-2026 (newest first); needs type",
    }
    legislation_filters = {
        "type": "loi (default), decret, ordonnance, accord, decision",
        "from": "signature date on or after, YYYY-MM-DD",
        "to": "signature date on or before, YYYY-MM-DD",
    }
    min_interval = {CC_HOST: 1.0, SGG_HOST: 1.0}
    notes = ("Cour constitutionnelle decisions (~6,500 DCC plus electoral; search by decision number or "
             "applicant name, the site's keyword search is broken) and laws/decrees/ordinances from the "
             "SGG (as promulgated, PDF; many recent scans have no text layer). French.")
    gaps = (
        "Cour suprême decisions: not published online (coursupreme.bj is a static page only)",
        ("CDIJ law database (legis.cdij.bj): terms forbid reproduction 'sans l'accord écrit'; "
         "needs permission"),
        "Text of many recent laws and decrees: image-only scans, no text layer (no OCR here)",
        ("Keyword search of Constitutional Court decisions: broken at the source (Algolia HTTP "
         "500)"),
        "Assemblée nationale texts: site in maintenance (503, 2026-11-06)",
        "Code pénal (Loi 2018-16) and the 1990 Constitution (Loi 90-32): not on sgg.gouv.bj as searchable "
        "text (2026-11); the 1990 Constitution and some decisions are scanned PDFs",
        "Lower courts: not researched yet",
        "Arrêtés: the law-id pattern accepts 'arrete-' but search never queries that SGG type",
    )
    samples = {
        "caselaw_query": "Président de la République",
        "decision_id": "DCC20-001",
        "legislation_query": "code",
        "law_id": "loi-98-004",
        "provision": "2",
    }

    # ---- case law --------------------------------------------------------- #
    async def search_caselaw(self, query, *, limit, page, filters):
        q = _http.clean(query)
        f = {k: _http.clean(str(v)) for k, v in (filters or {}).items() if v}
        typ, year = f.get("type", "").upper(), f.get("year", "")
        if typ and typ not in CC_TYPES:
            raise BadRequest(f"type must be one of {', '.join(CC_TYPES)}.")
        yr = re.fullmatch(r"((?:19|20)\d{2})(?:\s*-\s*((?:19|20)\d{2}))?", year)
        if year and not yr:
            raise BadRequest("year must be four digits, e.g. 2025, or a range like 2022-2026.")
        if yr and yr[2] and int(yr[2]) < int(yr[1]):
            raise BadRequest("In a year range the first year must not be after the second.")
        if year and not typ:
            raise BadRequest("year needs a type filter too (DCC, EL, EP or EG).")
        if q and (typ or year):
            raise BadRequest("The site ignores filters combined with a query: use either a query "
                             "(decision number or applicant name) or type/year filters.")
        if q and _DEC_ID.match(q.replace(" ", "")):
            base, params = CC_SEARCH, {"decision_number": _norm_dec_id(q)}
            note = "Search by decision number."
        elif q:
            base, params = CC_SEARCH, {"applicant": q[:100]}
            note = ("The query is matched against the applicant (requérant) name; the site's keyword "
                    "search is out of order, so a subject or keyword search is not possible here. "
                    "Use type/year filters to browse.")
        elif typ and yr and yr[2]:
            limit = max(1, min(int(limit), 30))
            start, hits, total = (max(1, int(page)) - 1) * limit, [], 0
            for y in range(int(yr[2]), int(yr[1]) - 1, -1):
                # once the page is full, one request per remaining year still gives its count
                got, t = await self._cc_window(f"{CC_BASE}/decision-type/{CC_TYPES[typ][1]}/{y}", {},
                                               max(0, start - total), max(1, limit - len(hits)))
                total += t or 0
                hits += got[:max(0, limit - len(hits))]
            return Results(items=hits, total=total,
                           note=f"{typ} decisions of {yr[1]}-{yr[2]}, newest year first; the total is the sum of the "
                                f"per-year counts listed on the site.")
        elif typ and year:
            base, params = f"{CC_BASE}/decision-type/{CC_TYPES[typ][1]}/{year}", {}
            note = f"{typ} decisions of {year}, newest first."
        elif typ:
            base, params = CC_SEARCH, {"decision_type": CC_TYPES[typ][0]}
            note = f"All {typ} decisions, newest first."
        else:
            base, params = CC_BASE + "/decisions", {}
            note = "All decisions, newest first."
        hits, total = await self._cc_window(base, params, (max(1, int(page)) - 1) * max(1, min(int(limit), 30)),
                                            max(1, min(int(limit), 30)))
        if not hits and q:
            raise NotFound(f"No applicant (requérant) named '{q}' at the Cour constitutionnelle. This does NOT "
                           "mean there are no decisions on that subject: the site's keyword search is out of "
                           "order, so a subject search is not possible here. Browse with type/year filters "
                           "(e.g. type DCC, year 2022-2026) and read the 'Objet de la requête' lines.")
        return Results(items=hits, total=total, note=note)

    async def _cc_window(self, base, params, start, limit):
        """Up to `limit` cards of one listing from offset `start` (10 per page at the source) and
        the listing's total. Returns ([], total) when start is beyond the end."""
        first = start // CC_PAGE + 1
        last = (start + limit - 1) // CC_PAGE + 1
        hits: list[DecisionHit] = []
        total = None
        for n in range(first, last + 1):
            if total is not None and (n - 1) * CC_PAGE >= total:
                break
            qs = {**params, **({"page": str(n)} if n > 1 else {})}
            r = await _http.get(base + ("?" + urlencode(qs) if qs else ""))
            if r.status_code == 404 and not params:
                return [], 0
            if r.status_code != 200:
                raise SourceError(_http.error(CC_NAME, "search failed", r.status_code), r.status_code)
            more, t = _cc_hits(r.text)
            total = t if t is not None else total
            hits += more
            if not more:
                if total is None and n > 1:       # window past the end: still report the size
                    total = (await self._cc_window(base, params, 0, 1))[1]
                break
        off = start - (first - 1) * CC_PAGE
        return hits[off:off + limit], total

    async def get_decision(self, id):
        did = _norm_dec_id(id)
        info = await _cc_decision_page(did)
        url = CC_DEC.format(id=did)
        if not info["pdf"]:
            raise SourceError(f"Error ({CC_NAME}): no PDF linked for {did}. Open {url}.")
        text = await _pdf(info["pdf"], CC_NAME)
        scanned = not text
        if scanned:
            text = (f"(No text available: the court's PDF is an image-only scan and this server does no OCR. "
                    f"Read the decision at {info['pdf']}. Only the register details below are available.)")
        meta = {k: v for k, v in info["meta"].items() if v}
        meta["PDF"] = info["pdf"]
        return Decision(id=did, title=f"{CC_NAME} (Bénin), décision {info['head']}", text=text, url=url,
                        court=CC_NAME, date=fr_date(info["head"]), case_number=did,
                        summary=meta.pop("Objet de la requête", ""), metadata=meta)

    # ---- legislation ------------------------------------------------------ #
    async def search_legislation(self, query, *, limit, page, filters):
        f = {k: _http.clean(str(v)) for k, v in (filters or {}).items() if v}
        typ = _fold(f.get("type", "loi"))
        if typ not in SGG_TYPES:
            raise BadRequest(f"type must be one of {', '.join(SGG_TYPES)}.")
        params = {"type": typ, "keywords": _http.clean(query)[:200]}
        for k, p in (("from", "begin"), ("to", "end")):
            if f.get(k):
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", f[k]):
                    raise BadRequest(f"{k} must be YYYY-MM-DD.")
                params[p] = f[k]
        limit, start, first = _page_window(limit, page, SGG_PAGE)
        last = (start + limit - 1) // SGG_PAGE + 1
        hits: list[LawHit] = []
        total = None
        for n in range(first, last + 1):
            if total is not None and (n - 1) * SGG_PAGE >= total:
                break
            r = await _http.get(SGG_SEARCH + "?" + urlencode({**params, **({"offset": str(n)} if n > 1 else {})}))
            if r.status_code != 200:
                raise SourceError(_http.error(SGG_NAME, "search failed", r.status_code), r.status_code)
            more, t = _sgg_hits(r.text)
            total = t if t is not None else total
            hits += more
            if not more:
                break
        off = start - (first - 1) * SGG_PAGE
        return Results(items=hits[off:off + limit], total=total,
                       note="Texts as promulgated (PDF), not consolidated; recent scans may have no text layer.")

    async def get_legislation_text(self, id):
        lid = _norm_law_id(id)
        law = await _sgg_law(lid)
        return LawText(id=lid, title=law["title"], text=law["text"], url=law["url"],
                       metadata={"PDF": SGG_PDF.format(id=lid), "Note": "Text layer is OCR of the signed original."})

    async def get_legislation_toc(self, id):
        lid = _norm_law_id(id)
        law = await _sgg_law(lid)
        entries, seen = [], set()
        for para in law["text"].split("\n\n"):
            m = _ARTICLE.match(para)
            if m:
                lab = _norm_prov(m[1])
                if lab in seen:
                    continue
                seen.add(lab)
                rest = _http.clean(m[2])
                entries.append(TocEntry(title=f"Article {lab}" + (f" – {rest[:80]}" if rest else ""),
                                        level=1, provision=lab))
            elif _HEADING.match(para) and len(para) < 200:
                entries.append(TocEntry(title=para, level=0))
        if not entries:
            raise NotFound(f"'{lid}' has no article structure in its text. Use get_legislation_text.")
        labels = [e.provision for e in entries if e.provision]
        note = (_OCR_WARN + f"Read the PDF at {SGG_PDF.format(id=lid)}.") if _ocr_unreliable(labels) else ""
        return Toc(id=lid, title=law["title"], url=law["url"], entries=entries, note=note)

    async def get_legislation_provision(self, id, provision):
        lid = _norm_law_id(id)
        law = await _sgg_law(lid)
        want = _norm_prov(provision)
        paras = law["text"].split("\n\n")
        for i, para in enumerate(paras):
            m = _ARTICLE.match(para)
            if m and _norm_prov(m[1]) == want:
                out = [para]
                for nxt in paras[i + 1:]:
                    if _ARTICLE.match(nxt) or _HEADING.match(nxt):
                        break
                    out.append(nxt)
                return Provision(law_id=lid, law_title=law["title"], provision=want,
                                 text="\n\n".join(out), url=law["url"])
        labels = []
        for para in paras:
            m = _ARTICLE.match(para)
            if m and _norm_prov(m[1]) not in labels:
                labels.append(_norm_prov(m[1]))
        have = (f"Articles found in the text layer: {', '.join(labels[:30])}{' ...' if len(labels) > 30 else ''}. "
                if labels else "No article headings were recognised in the text layer. ")
        warn = _OCR_WARN if _ocr_unreliable(labels) else ""
        raise NotFound(f"No article '{provision}' in '{lid}'. {have}{warn}The text layer can miss headings "
                       f"(OCR), so this does NOT show the article is absent; use get_legislation_text or "
                       f"read the PDF at {SGG_PDF.format(id=lid)}.")
