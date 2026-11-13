"""Côte d'Ivoire: Cour de cassation judgments (eservices.courdecassation.ci) and the laws listed by
the Assemblée nationale (assnat.ci). French.

How the sources work (verified 2026-11-06, UK IP, honest User-Agent):

Case law, Cour de cassation (the highest court of the ordinary courts):
  * GET https://eservices.courdecassation.ci/search/stoppages with search (keywords; matched
    against the "Objet de l'arrêt" subject line, not the full text), matter (civ_com|soc|pen),
    nature (REJET, CASSATION, ...), start_date / end_date (YYYY-MM-DD), nb_page (1-based).
    10 cards per page: nature, "ARRET N°201/24", "Objet de l'Arrêt : ...", and a link to the
    PDF in sigcc.courdecassation.ci/pdfjs/web/viewer.html?file=/uploads/stoppages/<slug>.pdf.
    The sidebar "Nombre d'arrêts par nature" counts the hits for the current filters; their sum
    is the total. ~100 judgments in all, 2023-2024.
  * The id is the PDF's own file name without ".pdf" ("arret-n-201-24-du-27-fevrier-2024-2-1").
    The PDFs have a text layer; parties are anonymised to initials by the court.

Legislation, Assemblée nationale:
  * The "Lois" section (/?-lois-82-) lists ~135 entries, 12 per page (&debut_articles=12n):
    laws, ratification laws and some resolutions, mostly 2012-2020. There is no title search
    (the site search mixes in news and comments), so the 12 listing pages are read once and
    kept in memory for SEARCH_TTL, and search filters titles locally.
  * The id is the SPIP article slug ("loi-relatif-au-mariage"). The article page has the full
    title and, for most laws, a PDF under /IMG/pdf/ with a text layer: the law as adopted by
    the Assemblée, not a consolidated text. Some entries have only a one-line summary.

Terms and robots.txt (2026-11-06):
  * courdecassation.ci, eservices. and sigcc.: robots.txt allows all for "*" (courdecassation.ci
    only blocks SEO bots and wordfence query strings). No terms of use or mentions légales page
    on either site (WordPress page list checked); footer "© Copyright 2026 . Tous Droits Réservés".
  * assnat.ci: robots.txt is "User-agent: *" with no rules. No terms page; footer
    "Copyright ©2019 assnat.ci - Tous droits resevés".

Not used:
  * sgg.gouv.ci (Secrétariat général du Gouvernement, Journal officiel) and coursupreme.ci: TLS
    certificate expired; not fetched.
  * conseil-constitutionnel.ci: robots.txt allows the site (Crawl-delay 10, /search/ disallowed),
    but its "Lois et décrets" pages are empty ("aucun contenu"); its decisions are PDFs not
    wired here.
  * Juriscope (juriscope.org): non-official (association); official sources exist.
"""
from __future__ import annotations

import re
import time
import unicodedata
from urllib.parse import urlencode

from lxml import html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc, TocEntry

ES_HOST = "eservices.courdecassation.ci"
PDF_HOST = "sigcc.courdecassation.ci"
CC_SEARCH = f"https://{ES_HOST}/search/stoppages"
CC_PDF = f"https://{PDF_HOST}/uploads/stoppages/{{id}}.pdf"
CC_VIEW = f"https://{PDF_HOST}/pdfjs/web/viewer.html?file=/uploads/stoppages/{{id}}.pdf"
CC_NAME = "Cour de cassation"
CC_PAGE = 10                     # fixed by the source

AN_HOST = "www.assnat.ci"
AN_BASE = f"https://{AN_HOST}/"
AN_LIST = AN_BASE + "?-lois-82-"
AN_ART = AN_BASE + "?{id}"
AN_NAME = "Assemblée nationale"
AN_PAGE = 12                     # fixed by the source
AN_MAX_PAGES = 30                # safety stop for the index walk
SEARCH_TTL = 6 * 3600

MAX_PDF = 40_000_000
MATTERS = {"civ_com": "civile et commerciale", "soc": "sociale", "pen": "pénale"}
NATURES = ("CASSATION", "CASSATION RENVOI", "CASSATION SANS RENVOI", "CONTINUATION DES POURSUITES",
           "DESSAISISSEMENT", "DISCONTINUATION DES POURSUITES", "INCOMPETENCE", "IRRECEVABILITE",
           "RADIATION", "REJET")
MONTHS = {m: i for i, m in enumerate(("janvier", "fevrier", "mars", "avril", "mai", "juin", "juillet",
                                       "aout", "septembre", "octobre", "novembre", "decembre"), 1)}
_SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{2,250}$")
_ARTICLE = re.compile(r"^(?:Article|ARTICLE|Art\.)\s*(\d+(?:\s*(?:bis|ter|quater|nouveau))?|premier|1er)\b"
                      r"\s*[:.\-–]?\s*(.*)$")
_HEADING = re.compile(r"^(TITRE|CHAPITRE|Chapitre|SECTION|Section|LIVRE|Livre|Titre|Paragraphe)\b")
_BREAK_BEFORE = re.compile(r"^(Attendu|Vu |Sur le|PAR CES MOTIFS|LA COUR|Casse|Rejette|Déclare|Renvoie|"
                           r"Met les|Ainsi fait|Mais attendu|Considérant|Arrêt n)")

_cache: dict = {}
_index: dict = {}                # {"at": time, "items": [LawHit]}


_LABOUR = re.compile(r"licenci|travail|salari|employeur|preavis|prud|embauche|demission|harcelement")


def _fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in s if not unicodedata.combining(c)).lower().replace("’", "'")


def fr_date(s: str) -> str:
    """First '27 février 2024' / '27-fevrier-2024' / '1er août 1983' in s -> ISO; else ''."""
    m = re.search(r"\b(\d{1,2})(?:er)?[\s-]+(" + "|".join(MONTHS) + r")[\s-]+(\d{4})\b", _fold(s))
    if not m:
        return ""
    d, mo, y = int(m[1]), MONTHS[m[2]], int(m[3])
    return f"{y:04d}-{mo:02d}-{d:02d}" if 1 <= d <= 31 else ""


def reflow(text: str) -> str:
    """pdf_text lines (hard-wrapped) -> paragraphs: a line is joined to the previous one unless the
    previous ends a sentence/clause or the line starts an article, heading or a judgment section."""
    out: list[str] = []
    for block in text.split("\n\n"):              # pdf_text separates pages by a blank line
        for ln in block.split("\n"):
            ln = ln.strip()
            if not ln or re.fullmatch(r"[-_\s\d]{1,6}", ln):   # page numbers, rules
                continue
            starts = bool(_ARTICLE.match(ln) or _HEADING.match(ln) or _BREAK_BEFORE.match(ln)
                          or ln.isupper())
            if (out and ln.isupper() and not _ARTICLE.match(ln) and not _HEADING.match(ln)
                    and _HEADING.match(out[-1]) and out[-1].isupper() and not re.search(r"[.;:]$", out[-1])):
                out[-1] += " " + ln          # heading wrapped onto a second line
            elif out and not starts and not re.search(r"[.;:!?»]$", out[-1]) and not out[-1].isupper():
                out[-1] = out[-1].rstrip("-") + ("" if out[-1].endswith("-") else " ") + ln
            else:
                out.append(ln)
    return "\n\n".join(out)


async def _pdf(url: str, source: str) -> str:
    """Download a PDF (size checked first) and return its reflowed text."""
    if url in _cache:
        return _cache[url]
    h = await _http.request("HEAD", url)
    if h.status_code == 404:
        raise NotFound(f"No document at {url}.")
    if h.status_code != 200:
        raise SourceError(_http.error(source, "PDF not available", h.status_code), h.status_code)
    size = int(h.headers.get("content-length") or 0)
    if size > MAX_PDF:
        raise SourceError(f"Error ({source}): PDF is {size // 1_000_000} MB, over the 40 MB cap. Open {url}.")
    r = await _http.get(url)
    if r.status_code != 200 or not r.content.startswith(b"%PDF"):
        raise SourceError(_http.error(source, "PDF download failed", r.status_code), r.status_code)
    if len(r.content) > MAX_PDF:
        raise SourceError(f"Error ({source}): PDF over the 40 MB cap. Open {url}.")
    text = reflow(_http.pdf_text(r.content))
    return _http.lru_put(_cache, url, text, 16)


# --------------------------------------------------------------------------- #
# Cour de cassation
# --------------------------------------------------------------------------- #
def _cc_hits(h: str) -> tuple[list[DecisionHit], int]:
    doc = lhtml.fromstring(h)
    hits = []
    for card in doc.xpath('//article[contains(@class, "stoppage-card")]'):
        link = card.xpath('.//a[contains(@href, "/uploads/stoppages/")]/@href')
        m = re.search(r"/uploads/stoppages/([^/?#]+)\.pdf", link[0]) if link else None
        if not m:
            continue
        did = m[1]
        nature = _http.clean(" ".join(card.xpath('.//p[contains(@class, "post-category")]//text()')))
        lis = [_http.clean(li.text_content()) for li in card.xpath(".//li")]
        num = next((re.sub(r"(?i)^arr[eê]t\s*n°\s*", "", x) for x in lis if re.match(r"(?i)arr[eê]t", x)), "")
        obj = next((re.sub(r"^Objet de l'Arrêt\s*:\s*", "", x) for x in lis if x.startswith("Objet")), "")
        title = f"{CC_NAME} (Côte d'Ivoire), arrêt n° {num}" if num else f"{CC_NAME} (Côte d'Ivoire) {did}"
        hits.append(DecisionHit(id=did, title=title, court=CC_NAME, date=fr_date(did), case_number=num,
                                snippet="; ".join(x for x in (nature, obj) if x), url=CC_VIEW.format(id=did)))
    side = doc.xpath('//*[contains(text(), "Nombre d")]/ancestor::*[1]/following-sibling::*[1]')
    counts = re.findall(r"\((\d+)\)", " ".join(side[0].itertext())) if side else []
    if not counts:  # fall back to the whole page text after the heading
        tail = h[h.find("Nombre d"):]
        tail = tail[:tail.find("Autres liens")] if "Autres liens" in tail else ""
        counts = re.findall(r"\((\d+)\)", re.sub(r"<[^>]+>", " ", tail))
    return hits, sum(int(c) for c in counts)


# --------------------------------------------------------------------------- #
# Assemblée nationale
# --------------------------------------------------------------------------- #
def _law_meta(title: str) -> tuple[str, str, str]:
    """(type, number, date) from a title like 'Loi n° 2013-867 du 23 Décembre 2013 relative à ...'."""
    t = _fold(title)
    typ = next((x.capitalize() for x in ("loi", "ordonnance", "resolution", "decret", "annexe") if t.startswith(x)), "")
    typ = {"Resolution": "Résolution", "Decret": "Décret"}.get(typ, typ)
    m = re.search(r"n\s*°\s*([0-9]{2,4}\s*-\s*[0-9]+|[0-9]+[a-z]?)\b", t)
    num = re.sub(r"\s+", "", m[1]).upper() if m else ""
    return typ, num, fr_date(title)


async def _an_index() -> list[LawHit]:
    if _index and time.monotonic() - _index["at"] < SEARCH_TTL:
        return _index["items"]
    items: list[LawHit] = []
    seen: set[str] = set()
    for n in range(AN_MAX_PAGES):
        url = AN_LIST + (f"&debut_articles={n * AN_PAGE}" if n else "")
        r = await _http.get(url)
        if r.status_code != 200:
            raise SourceError(_http.error(AN_NAME, "law list failed", r.status_code), r.status_code)
        doc = lhtml.fromstring(r.text)
        new = 0
        for a in doc.xpath('//font[@size="3"]/strong/a[starts-with(@href, "./?")]'):
            slug = a.get("href")[3:]
            title = _http.clean(a.text_content())
            if title.endswith(("(…)", "(...)")):  # the list truncates long titles
                title = title.rsplit("(", 1)[0].strip() + " …"
            if not title or slug in seen or slug.startswith("-"):
                continue
            seen.add(slug)
            new += 1
            typ, num, date = _law_meta(title)
            items.append(LawHit(id=slug, title=title, type=typ, number=num, date=date,
                                url=AN_ART.format(id=slug)))
        last = re.findall(r"debut_articles=(\d+)", r.text)
        if not new or not last or n * AN_PAGE >= max(int(x) for x in last):
            break
    _index.update(at=time.monotonic(), items=items)
    return items


async def _an_law(lid: str) -> dict:
    if not _SLUG.match(lid or ""):
        raise BadRequest("A law id is the Assemblée nationale article slug from search_legislation, "
                         "e.g. 'loi-relatif-au-mariage'.")
    key = ("an", lid)
    if key in _cache:
        return _cache[key]
    url = AN_ART.format(id=lid)
    r = await _http.get(url)
    if r.status_code != 200:
        raise SourceError(_http.error(AN_NAME, "law page failed", r.status_code), r.status_code)
    doc = lhtml.fromstring(r.text)
    art = doc.xpath("//article[.//h2]")
    h2 = art[0].xpath(".//h2") if art else []
    if not art or not h2:
        raise NotFound(f"No law '{lid}' at the Assemblée nationale site.")
    title = _http.clean(h2[0].text_content())
    pdfs = [p for p in doc.xpath('//a[contains(@href, "IMG/pdf/")]/@href')]
    body = ""
    if pdfs:
        href = pdfs[0]
        pdf = AN_BASE + href[href.index("IMG/pdf/"):]
        body = await _pdf(pdf, AN_NAME)
    if not body:   # the page markup is broken: only the bold summary line is the law's own; the rest is site chrome
        body = _http.clean(" ".join(" ".join(art[0].xpath('.//font[@size="3"]/strong')[0].itertext()).split())) \
            if art[0].xpath('.//font[@size="3"]/strong') else ""
    return _http.lru_put(_cache, key, {"title": title, "url": url, "text": body, "pdf": bool(pdfs)}, 32)


def _norm_prov(p: str) -> str:
    s = _fold(_http.clean(p))
    s = re.sub(r"^(article|art\.?)\s*", "", s).strip(" .:")
    s = {"premier": "1", "1er": "1"}.get(s, s)
    return re.sub(r"\s+", " ", s)


class CoteDIvoire(Jurisdiction):
    code = "ci"
    name = "Côte d'Ivoire"
    languages = ("fr",)
    aliases = ("cote d'ivoire", "côte d'ivoire", "ivory coast", "civ")
    sources = (
        Source(
            name="Cour de cassation de Côte d'Ivoire: jurisprudence (eservices / sigcc)",
            url=CC_SEARCH,
            covers=("caselaw",),
            licence="no terms published; footer '© Copyright 2026. Tous Droits Réservés'",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~25 requests (2026-11)",
            terms_url="https://courdecassation.ci/",
        ),
        Source(
            name="Assemblée nationale de Côte d'Ivoire: lois (assnat.ci)",
            url=AN_LIST,
            covers=("legislation",),
            licence="no terms published; footer 'Copyright ©2019 assnat.ci - Tous droits réservés'",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~25 requests (2026-11)",
            terms_url=AN_BASE,
            warning="Texts as adopted by the Assemblée nationale (not consolidated, mostly 2012-2020); "
                    "the Journal officiel is the authentic version.",
        ),
    )
    caselaw_filters = {
        "matter": "civ_com (civil & commercial), soc (social) or pen (criminal)",
        "nature": "outcome: " + ", ".join(NATURES),
        "from": "decision date on or after, YYYY-MM-DD",
        "to": "decision date on or before, YYYY-MM-DD",
    }
    min_interval = {ES_HOST: 1.0, PDF_HOST: 1.0, AN_HOST: 1.0}
    notes = ("Cour de cassation judgments (~100, 2023-2024, PDF full text, anonymised; keyword search "
             "covers the subject line only; most are anonymised, but some copies name the parties in full) and ~135 laws listed by the Assemblée nationale (as adopted, "
             "mostly 2012-2020). French.")
    gaps = (
        ("Cour de cassation judgments outside 2023-2024: not published online (~100 judgments in "
         "all)"),
        "Journal officiel and Cour suprême (sgg.gouv.ci, coursupreme.ci): TLS certificate expired",
        ("Conseil constitutionnel decisions: robots allows (Crawl-delay 10), PDFs; source exists "
         "but not built yet"),
        ("Decrees, ordinances, consolidated texts and laws outside ~2012-2020: not on assnat.ci; "
         "JO site cert expired (above)"),
        "Full-text case-law search: the Cour de cassation search matches the subject line only",
    )
    samples = {
        "caselaw_query": "Succession",
        "decision_id": "arret-n-201-24-du-27-fevrier-2024-2-1",
        "legislation_query": "mariage",
        "law_id": "loi-relatif-au-mariage",
        "provision": "1",
    }

    # ---- case law --------------------------------------------------------- #
    async def search_caselaw(self, query, *, limit, page, filters):
        params = {"search": _http.clean(query)[:200], "matter": "", "nature": ""}
        f = filters or {}
        if f.get("matter"):
            if f["matter"] not in MATTERS:
                raise BadRequest(f"matter must be one of {', '.join(MATTERS)}.")
            params["matter"] = f["matter"]
        if f.get("nature"):
            nat = _http.clean(f["nature"]).upper()
            if nat not in NATURES:
                raise BadRequest(f"nature must be one of: {', '.join(NATURES)}.")
            params["nature"] = nat
        for k, p in (("from", "start_date"), ("to", "end_date")):
            if f.get(k):
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", f[k]):
                    raise BadRequest(f"{k} must be YYYY-MM-DD.")
                params[p] = f[k]
        limit = max(1, min(int(limit), 30))
        start = (max(1, int(page)) - 1) * limit
        first, last = start // CC_PAGE + 1, (start + limit - 1) // CC_PAGE + 1
        hits: list[DecisionHit] = []
        total = 0
        for n in range(first, last + 1):
            if n > first and (n - 1) * CC_PAGE >= total:
                break
            r = await _http.get(CC_SEARCH + "?" + urlencode({**params, "nb_page": str(n)}))
            if r.status_code != 200:
                raise SourceError(_http.error(CC_NAME, "search failed", r.status_code), r.status_code)
            if "stoppage" not in r.text and "Jurisprudence" not in r.text:
                raise SourceError(f"Error ({CC_NAME}): search page changed.", 200)
            more, total = _cc_hits(r.text)
            hits += more
        off = start - (first - 1) * CC_PAGE
        items = hits[off:off + limit]
        widened = False
        if not hits and params["search"] and _LABOUR.search(_fold(params["search"])):
            # employment terms live in the full text, not the subject line: list the labour-subject decisions
            r = await _http.get(CC_SEARCH + "?" + urlencode({**params, "search": "travail", "nb_page": "1"}))
            if r.status_code == 200:
                hits, total = _cc_hits(r.text)
                items = hits[:limit]
                widened = bool(items)
        note = ("Keywords match only the short subject line ('objet', e.g. 'Contrat de travail'), not the "
                "headnote or full text: a term such as 'licenciement abusif' can appear inside a judgment "
                "and still return 0, and a hit shows only the outcome and subject line, so open the decision "
                "to see the headnote. To find labour cases, search a broad subject (e.g. 'Contrat de travail', "
                "matter=soc) and read the decisions. The same case number and date can also exist as "
                "separate judgments in different matters (soc and civ_com), with different outcome labels.")
        if widened:
            note = (f"No subject line contains '{params['search']}'; showing decisions whose subject mentions "
                    "'travail' (employment). They are NOT filtered on your term: open each decision and read the "
                    "headnote (e.g. 'Licenciement abusif') to check. ") + note
        if not items:
            note += (" No hit does not mean no case: the subject line may be worded differently. "
                     "Try query 'Contrat de travail' with filters {\"matter\": \"soc\"}.")
        keys = [(h.date, re.sub(r"^0+", "", h.case_number)) for h in items if h.case_number]
        if len(set(keys)) < len(keys):
            note += (" Some entries share the same case number and date: the court published separate "
                     "judgments under one number (different PDFs and ids, sometimes a different outcome "
                     "label); each id is its own document. One copy may name the parties in full "
                     "where the other is anonymised to initials: handle names with care.")
        return Results(items=items, total=total, note=note)

    async def get_decision(self, id):
        did = (id or "").strip().removesuffix(".pdf")
        if not _SLUG.match(did) or not did.startswith("arret"):
            raise BadRequest("A decision id is the PDF name from search_caselaw, "
                             "e.g. 'arret-n-201-24-du-27-fevrier-2024-2-1'.")
        text = await _pdf(CC_PDF.format(id=did), CC_NAME)
        if not text:
            raise SourceError(f"Error ({CC_NAME}): the PDF has no text layer. Open {CC_VIEW.format(id=did)}.")
        m = re.search(r"Arrêt\s*n°\s*([\w/ -]+?)\s+du\s+(\d{1,2}(?:er)?\s+\w+\s+\d{4})", text, re.I)
        num = _http.clean(m[1]) if m else ""
        date = (fr_date(m[2]) if m else "") or fr_date(did)
        first = text.split("\n\n", 1)[0]
        meta = {"Formation": first} if len(first) < 80 and first.isupper() else {}
        title = f"{CC_NAME} (Côte d'Ivoire), arrêt n° {num}" if num else f"{CC_NAME} (Côte d'Ivoire) {did}"
        return Decision(id=did, title=title, text=text, url=CC_VIEW.format(id=did), court=CC_NAME,
                        date=date, case_number=num, metadata=meta)

    # ---- legislation ------------------------------------------------------ #
    async def search_legislation(self, query, *, limit, page, filters):
        words = [w for w in re.split(r"[\s,;]+", _fold(_http.clean(query))) if w]
        if not words:
            raise BadRequest("Give words from the law's title, in French, e.g. 'mariage' or 'code penal'.")
        items = await _an_index()
        hits = [h for h in items if all(w in _fold(h.title) or w in h.id for w in words)]
        limit = max(1, int(limit))
        start = (max(1, int(page)) - 1) * limit
        note = ("Title search over the Assemblée nationale's law list (texts as adopted, "
                "not consolidated; mostly 2012-2020).")
        if any(w.startswith("constitution") or w in ("code", "travail", "penale", "procedure", "civil") for w in words):
            note += (" The Constitution and the codes (Code civil, Code du travail, Code de procédure "
                     "pénale, etc.) are not in this list; only laws that ratify or amend them appear, so "
                     "a hit with 'code' in its title is an amending law, not the code. Journal officiel "
                     "site is unreachable (see list_jurisdictions).")
        return Results(items=hits[start:start + limit], total=len(hits), note=note)

    async def get_legislation_text(self, id):
        law = await _an_law(id)
        meta = {} if law["pdf"] else {"Note": "The Assemblée nationale site has no text for this law, only the one-line summary "
                                      "shown below. The law's text is not available through this source."}
        return LawText(id=id, title=law["title"], text=law["text"], url=law["url"], metadata=meta)

    async def get_legislation_toc(self, id):
        law = await _an_law(id)
        entries = []
        for para in law["text"].split("\n\n"):
            m = _ARTICLE.match(para)
            if m:
                lab = _norm_prov(m[1])
                head = f"Article {lab}"
                rest = _http.clean(m[2])
                entries.append(TocEntry(title=head + (f" – {rest[:80]}" if rest else ""), level=1, provision=lab))
            elif _HEADING.match(para) and len(para) < 200:
                entries.append(TocEntry(title=para, level=0))
        if not any(e.provision for e in entries):
            raise NotFound(f"'{id}' has no table of contents: the Assemblée nationale site "
                           "holds no text for this law, only a one-line summary (get_legislation_text).")
        return Toc(id=id, title=law["title"], url=law["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        law = await _an_law(id)
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
                return Provision(law_id=id, law_title=law["title"], provision=want,
                                 text="\n\n".join(out), url=law["url"])
        raise NotFound(f"No article '{provision}' in '{id}'. Labels look like '5' or 'Article 5'.")
