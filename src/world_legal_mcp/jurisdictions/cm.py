"""Cameroon: Supreme Court judgments (coursupreme.cm) and presidential acts (prc.cm).

Case law (coursupreme.cm, the Cour suprême's own JEE CMS):
  * GET /search?critere=Q&lang=fr|en&page=N (0-based, 9 a page) is the site's full-text
    search over all its publications; only titles that read as a judgment (ARRET, JUDGMENT,
    JUGEMENT) are kept. With no query, /publication/arret?lang=..&page=N (1-based) lists the
    "Arrêts de la Cour suprême" newest first.
  * Each judgment has a French and an English page with different slugs; the text sits in
    the page of its original language only (civil-law divisions in French, Common Law
    Division in English). Hence the `language` filter.
  Id: the page path after /publication/detail/, e.g.
  "Section Civile/arret--n°-20civ-du-04-avril-2024" (category / slug, as the site uses it).

Legislation (www.prc.cm, Présidence de la République, Joomla):
  * Laws, ordinances and decrees are articles in /fr/actualites/actes/{lois,ordonnances,decrets}.
    Smart Search (/fr/chercher?q=..) is site-wide; hits outside those three categories are
    dropped. With no query, the category listing (8 a page) is used.
  * Text: older acts (mostly before 2015) carry the full text as HTML. Newer ones carry only a
    page image and a PDF (via /fr/multimedia/documents/..); its text layer is used when it has
    one, otherwise the act is reported as a scan (no OCR here).
  Id: the Joomla article number, e.g. "151" (https://www.prc.cm/fr/actualites/actes/151).
  Not consolidated: each act is the text as signed.
"""
from __future__ import annotations

import re
from urllib.parse import quote, unquote, urlsplit

from lxml import html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

CS_HOST = "coursupreme.cm"
CS = f"https://{CS_HOST}"
PRC_HOST = "www.prc.cm"
PRC = f"https://{PRC_HOST}"
MAX_PDF = 40_000_000           # bytes; larger PDFs are refused (HEAD-checked first)
MAX_SOURCE_PAGES = 4           # source pages read per search call at most
CS_PAGE = 9                    # hits per page on coursupreme.cm (fixed by the site)
PRC_LIST_PAGE = 8              # articles per category page on prc.cm (fixed by the site)
PRC_SEARCH_PAGE = 50           # Smart Search honours &limit=

_TYPES = {"loi": "lois", "ordonnance": "ordonnances", "decret": "decrets"}
_TYPE_NAMES = {"lois": "Loi", "ordonnances": "Ordonnance", "decrets": "Décret"}
_JUDGMENT = re.compile(r"^\W*(?:A\s*R\s*R\s*[EÊÉ]\s*T|(?:FINAL\s+)?JUDG(?:E)?MENT|JUGEMENT)\b", re.I)
_MONTHS = {m: i for i, ms in enumerate((
    ("janvier", "january", "jan"), ("fevrier", "février", "february", "feb"), ("mars", "march", "mar"),
    ("avril", "april", "apr"), ("mai", "may"), ("juin", "june", "jun"), ("juillet", "july", "jul"),
    ("aout", "août", "august", "aug"), ("septembre", "september", "sept", "sep"),
    ("octobre", "october", "oct"), ("novembre", "november", "nov"),
    ("decembre", "décembre", "december", "dec")), 1) for m in ms}
_DATE_WORDS = re.compile(r"(\d{1,2})\s*(?:er|st|nd|rd|th)?\s+([A-Za-zÀ-ÿ]+)\.?,?\s+(\d{4})")
_DATE_NUM = re.compile(r"\b(\d{1,2})\s*/\s*(\d{1,2})\s*/\s*(\d{4})\b")
_CASE_NO = re.compile(r"\bN\s*[°o]\s*\.?\s*:?\s*(\d[\w.]*(?:\s*/\s*[A-Z][\w.]*)*(?:/\d{4})?)", re.I)
_ART = re.compile(r"^(?:\*\*)?\s*(?:ARTICLE|Article|Art\.)\s*(\d+)\s*(er|ère|ER|bis|ter|quater)?\b", re.M)
_HEAD = re.compile(r"^(?:\*\*)?\s*(TITRE|CHAPITRE|SECTION|PARTIE|LIVRE)\b", re.I)

_search_cache: dict = {}
_doc_cache: dict = {}


# ----------------------------------------------------------------------------- helpers

def text_date(s: str) -> str:
    """'du 04 avril 2024', 'of 01rd July 2021', 'du 02/03/ 2023' -> ISO; '' if none.
    (French/English month names; could be shared by other francophone adapters.)"""
    s = s.replace("/ ", "/")
    for d, mon, y in _DATE_WORDS.findall(s):
        m = _MONTHS.get(mon.lower())
        if m and 1 <= int(d) <= 31:
            return f"{y}-{m:02d}-{int(d):02d}"
    m = _DATE_NUM.search(s)
    if m and 1 <= int(m[1]) <= 31 and 1 <= int(m[2]) <= 12:
        return f"{m[3]}-{int(m[2]):02d}-{int(m[1]):02d}"
    return ""


async def _get(url: str, what: str, host: str, **kw):
    r = await _http.get(url, **kw)
    if r.status_code == 404:
        raise NotFound(f"{what} not found ({url})")
    if r.status_code != 200:
        raise SourceError(_http.error(host, what, r.status_code), r.status_code)
    return r


async def _paged(fetch, page: int, limit: int, size: int) -> tuple[list, int | None]:
    """(items [offset, offset+limit), total or None) of a filtered stream read source page by
    source page, repeated ids dropped (the site's search can list a document twice).
    `fetch(n)` returns (kept items, raw count) for source page n (0-based). The total is known
    only when the stream was read to its end."""
    want = page * limit
    kept, seen, n, total = [], set(), 0, None
    while len(kept) < want and n < MAX_SOURCE_PAGES * page:
        items, raw = await fetch(n)
        for it in items:
            if it.id not in seen:
                seen.add(it.id)
                kept.append(it)
        n += 1
        if raw < size:
            total = len(kept)
            break
    return kept[(page - 1) * limit:want], total


# ----------------------------------------------------------------------------- case law

def _cs_id(id: str) -> str:
    s = unquote(_http.clean(id))
    s = re.sub(r"^https?://(?:www\.)?coursupreme\.cm", "", s)
    s = re.sub(r"^/?publication/detail/", "", s).split("?")[0].strip("/")
    if s.count("/") != 1 or ".." in s or not all(s.split("/")):
        raise BadRequest("Use an id from search_caselaw, e.g. "
                         "'Section Civile/arret--n°-20civ-du-04-avril-2024'.")
    return s


def _cs_url(id: str, lang: str) -> str:
    return f"{CS}/publication/detail/{quote(id, safe='/')}?lang={lang}"


def _cs_hits(content: bytes) -> list[DecisionHit]:
    doc = lhtml.fromstring(content)
    hits = []
    for item in doc.xpath('//div[contains(@class,"items-leading")]/div[contains(@class,"item")]'):
        a = item.xpath('.//header[contains(@class,"article-header")]//a[@href]')
        if not a:
            continue
        href = a[0].get("href", "")
        if "/publication/detail/" not in href:
            continue
        title = _http.clean(a[0].text_content())
        if not _JUDGMENT.match(title):
            continue
        id = _cs_id(href)
        cat = _http.clean(" ".join(item.xpath('.//dd[@class="category-name"]/a/text()'))) or id.split("/")[0]
        teaser = _http.clean(a[0].get("title", "")) if a[0].get("title", "") != title else ""
        cn = _CASE_NO.search(title)
        hits.append(DecisionHit(id=id, title=title, court=f"Cour suprême du Cameroun, {cat}",
                                date=text_date(title), case_number=_http.clean(cn[1]) if cn else "",
                                snippet=teaser, url=_cs_url(id, "fr")))
    return hits


async def _cs_page(q: str, lang: str, n: int) -> tuple[list, int]:
    key = ("cs", q.lower(), lang, n)
    if key in _search_cache:
        return _search_cache[key]
    if q:
        url, params = f"{CS}/search", {"critere": q, "lang": lang, "page": n}
    else:
        url, params = f"{CS}/publication/arret", {"lang": lang, "page": n + 1}
    r = await _get(url, "judgment search", CS_HOST, params=params)
    raw = len(re.findall(rb'class="item col-sm-4', r.content))
    hits = _cs_hits(r.content)
    for h in hits:
        h.url = _cs_url(h.id, lang)
    return _http.lru_put(_search_cache, key, (hits, raw), 64)


def _cs_body(content: bytes) -> tuple[str, str, str]:
    """(title, markdown text, pdf url) of a judgment page; text '' when the page is empty."""
    doc = lhtml.fromstring(content)
    title = _http.clean(" ".join(doc.xpath('//span[@class="article-title"]//text()')))
    body = doc.xpath('//div[@class="itemFullText"]')
    text, pdf = "", ""
    if body:
        for a in body[0].xpath('.//a[@href]'):
            if a.get("href", "").lower().endswith(".pdf"):
                pdf = CS + quote(a.get("href"), safe="/%()_-.") if a.get("href").startswith("/") else a.get("href")
        for el in body[0].xpath('.//table|.//thead|.//tbody|.//tr|.//td|.//th'):
            el.tag = "div"            # the court header is laid out as a table: flatten it
        text = _http.html_to_md(lhtml.tostring(body[0], encoding="unicode"))
    if not pdf:
        m = re.search(rb'(?:href|src)="(/images/webcsc_medias/files/[^"]+\.pdf)"', content, re.I)
        if m:
            pdf = CS + quote(m[1].decode("utf-8", "replace"), safe="/%()_-.")
    return title, text, pdf


# ----------------------------------------------------------------------------- legislation

def _prc_id(id: str) -> str:
    s = _http.clean(id)
    m = re.fullmatch(r"(?:https?://www\.prc\.cm/(?:fr|en)/[\w/-]*?/)?(\d{1,6})(?:-[\w-]*)?", s)
    if not m:
        raise BadRequest("Use an article number from search_legislation, e.g. '151' "
                         "(Décret N°2013/112 portant organisation du MINREX).")
    return m[1]


def _prc_hit(href: str, title: str, snippet: str = "") -> LawHit | None:
    m = re.match(r"^/fr/actualites/actes/(lois|ordonnances|decrets)/(\d+)-", urlsplit(href).path)
    if not m:
        return None
    cn = re.search(r"\bN\s*[°o]\s*\.?\s*(\d[\d\s]*/\s*\d+)", title, re.I)
    return LawHit(id=m[2], title=title, type=_TYPE_NAMES[m[1]],
                  number=re.sub(r"\s+", "", cn[1]) if cn else "", date=text_date(title),
                  snippet=snippet, url=f"{PRC}/fr/actualites/actes/{m[1]}/{m[2]}")


async def _prc_page(q: str, cat: str, n: int) -> tuple[list, int]:
    key = ("prc", q.lower(), cat, n)
    if key in _search_cache:
        return _search_cache[key]
    hits = []
    if q:
        r = await _get(f"{PRC}/fr/chercher", "act search", PRC_HOST,
                       params={"q": q, "limit": PRC_SEARCH_PAGE, "start": n * PRC_SEARCH_PAGE})
        doc = lhtml.fromstring(r.content)
        lis = doc.xpath('//ul[contains(@class,"search-results")]/li')
        for li in lis:
            a = li.xpath('.//h4[contains(@class,"result-title")]/a[@href]')
            if not a:
                continue
            h = _prc_hit(a[0].get("href", ""), _http.clean(a[0].text_content()),
                         _http.clean(" ".join(li.xpath('.//p[contains(@class,"result-text")]//text()'))))
            if h and (not cat or h.url.split("/")[-2] == cat):
                hits.append(h)
        raw = len(lis)
    else:
        r = await _get(f"{PRC}/fr/actualites/actes/{cat}", "act listing", PRC_HOST,
                       params={"start": n * PRC_LIST_PAGE})
        doc = lhtml.fromstring(r.content)
        seen = set()
        for a in doc.xpath('//h4/a[@href]|//h2/a[@href]'):
            h = _prc_hit(a.get("href", ""), _http.clean(a.text_content()))
            if h and h.id not in seen:
                seen.add(h.id)
                hits.append(h)
        raw = len(seen)
    return _http.lru_put(_search_cache, key, (hits, raw), 64)


async def _pdf_text(doc_href: str) -> tuple[str, str]:
    """(text, pdf url) of the PDF behind a /multimedia/documents/ page; text '' for a scan."""
    p = await _get(PRC + doc_href, "document page", PRC_HOST)
    m = re.search(rb'src="(/files/[^"]+\.pdf)"', p.content)
    if not m:
        return "", ""
    url = PRC + m[1].decode()
    h = await _http.request("HEAD", url, headers={"Accept-Encoding": "identity"})
    size = int(h.headers.get("content-length") or 0)
    if h.status_code != 200 or not size or size > MAX_PDF:
        return "", url
    r = await _get(url, "act PDF", PRC_HOST)
    lines = [ln for ln in _http.pdf_text(r.content).split("\n") if ln.strip().lower() != "www.prc.cm"]
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
    return (text if len(text) > 200 else ""), url


async def _act(id: str) -> dict:
    if id in _doc_cache:
        return _doc_cache[id]
    r = await _get(f"{PRC}/fr/actualites/actes/{id}", f"act {id}", PRC_HOST)
    canon = re.search(rb'href="(/fr/actualites/actes/(lois|ordonnances|decrets)/' + id.encode() +
                      rb'-[^"?]*)', r.content)   # the article's own print / share link
    if not canon:
        raise NotFound(f"prc.cm article {id} is not a law, ordinance or decree.")
    doc = lhtml.fromstring(r.content)
    art = doc.xpath('//article')
    if not art:
        raise SourceError(_http.error(PRC_HOST, "unexpected act page", r.status_code))
    title = _http.clean(" ".join(art[0].xpath('.//h2//text()')))
    body = art[0].xpath('./div[@class="row-fluid"]')
    md, doc_href = "", ""
    if body:
        b = body[-1]
        links = [a.get("href") for a in b.xpath('.//a[@href]') if "/multimedia/documents/" in a.get("href", "")]
        doc_href = links[0] if links else ""
        for el in b.xpath('.//div[contains(@class,"tagsOfArticle")]|.//ul[contains(@class,"pagenav")]'):
            el.getparent().remove(el)
        md = _http.html_to_md(lhtml.tostring(b, encoding="unicode"))
        md = re.sub(r"\n*\**\s*_*\**\s*T[ée]l[ée]charger (?:la loi|le d[ée]cret|l'ordonnance|le texte)[^\n]*$",
                    "", md, flags=re.I).strip()
    source, pdf = "html", ""
    if not _ART.search(md) and doc_href:
        pdf_md, pdf = await _pdf_text(doc_href)
        if pdf_md:
            md, source = pdf_md, "pdf text layer"
        else:
            source = "scan"
    cat = canon[2].decode()
    law = {"id": id, "title": title, "type": _TYPE_NAMES[cat], "text": md, "source": source,
           "url": f"{PRC}{canon[1].decode()}", "pdf": pdf or (PRC + doc_href if doc_href else ""),
           "date": text_date(title)}
    return _http.lru_put(_doc_cache, id, law, 16)


def _require_text(law: dict) -> str:
    if law["source"] == "scan" or not law["text"]:
        raise SourceError(f"Act {law['id']} is published on prc.cm only as a scanned image without a text "
                          f"layer; open it at {law['pdf'] or law['url']}", "scan")
    return law["text"]


_AS_SIGNED = ("> Warning: text as signed on prc.cm, not consolidated. Later amending acts are not applied "
              "here and prc.cm does not link them; search for acts amending this one before relying on it.")


async def _amenders(law: dict) -> str:
    """Warning line naming acts on prc.cm whose title says they amend this one ('' if none found)."""
    cn = re.search(r"\bN\s*[°o]\s*\.?\s*(\d{4})\s*/\s*(\d+)", law["title"], re.I)
    if not cn:
        return ""
    num = f"{cn[1]}/{int(cn[2]):03d}"
    try:
        hits, _ = await _prc_page(f"modifiant et complétant loi {num} du", "", 0)
    except SourceError:
        return ""
    found = [h for h in hits if h.id != law["id"] and re.search(r"modifi", h.title, re.I)
             and re.search(rf"\bN\s*[°o]?\s*\.?\s*{cn[1]}\s*/\s*0*{int(cn[2])}\b", h.title.split("modifi", 1)[-1], re.I)]
    if not found:
        return ""
    return ("\n> Possibly amended by (titles on prc.cm that name this act; verify): "
            + "; ".join(f"{h.title.split(' du ')[0].strip()} (id {h.id})" for h in found) + ".")


def _label(num: str, suf: str | None) -> str:
    suf = (suf or "").lower()
    if suf in ("er", "ère"):
        suf = ""
    return f"Article {int(num)}{(' ' + suf) if suf else ''}"


def _split(text: str) -> list[tuple[str, str, int, int]]:
    """[(kind, label/heading, start, end)] over the act text; kind 'art' or 'head'."""
    marks = []
    for m in re.finditer(r"^.*$", text, re.M):
        line = m.group(0)
        a = _ART.match(line)
        if a:
            marks.append(("art", _label(a[1], a[2]), m.start()))
        elif _HEAD.match(line):
            marks.append(("head", _http.clean(line.replace("*", "")), m.start()))
    out = []
    for i, (k, lab, s) in enumerate(marks):
        e = marks[i + 1][2] if i + 1 < len(marks) else len(text)
        out.append((k, lab, s, e))
    return out


def _norm_provision(p: str) -> str:
    s = _http.clean(p).lower().replace("article", "").replace("art.", "").replace("art", "").strip(" .-")
    m = re.fullmatch(r"(\d+)\s*(er|ère|premier|bis|ter|quater)?", s)
    if not m:
        raise BadRequest("Use an article label from the TOC, e.g. 'Article 5', '5' or 'art. 5 bis'.")
    return _label(m[1], m[2] if m[2] not in ("premier",) else "er")


# ----------------------------------------------------------------------------- adapter

class Cameroon(Jurisdiction):
    code = "cm"
    name = "Cameroon"
    languages = ("fr", "en")
    aliases = ("cameroun", "republic of cameroon", "république du cameroun")
    sources = (
        Source(
            name="Cour suprême du Cameroun (coursupreme.cm)",
            url=f"{CS}/publication/arret",
            covers=("caselaw",),
            licence=("'Copyright © 2019 CSC. All Rights Reserved' (site footer); no terms of use or "
                     "licence page (checked 2026-11-06)"),
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit=("unknown; robots.txt 404 (no rules, no Crawl-delay); 1 s spacing, "
                        "no 429 in ~15 requests (2026-11)"),
            terms_url=f"{CS}/",
        ),
        Source(
            name="Présidence de la République du Cameroun (prc.cm), Actes: lois, ordonnances, décrets",
            url=f"{PRC}/fr/actualites/actes",
            covers=("legislation",),
            licence=("'Copyright © 2026 Présidence de la République du Cameroun - Tous droits réservés' "
                     "(site footer); the 'Règles de confidentialité' page is empty; no terms of use "
                     "(checked 2026-11-06)"),
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit=("unknown; robots.txt (Joomla default) only disallows system folders, no "
                        "Crawl-delay; 1 s spacing, no 429 in ~30 requests (2026-11)"),
            terms_url=f"{PRC}/fr/regles-de-confidentialite",
        ),
    )
    caselaw_filters = {"language": "'fr' (default: civil-law divisions) or 'en' (Common Law Division "
                                   "judgments are only in English)"}
    legislation_filters = {"type": "'loi', 'ordonnance' or 'decret' (default: all three when searching; "
                                   "'loi' when listing without a query)"}
    min_interval = {CS_HOST: 1.0, PRC_HOST: 1.0}
    notes = ("Case law: selected Supreme Court judgments (a few dozen) from coursupreme.cm, in French or "
             "English. Legislation: laws, ordinances and decrees as signed (not consolidated) from the "
             "Presidency's site; newer acts are often scans without text.")
    gaps = (
        "Text of newer acts (mostly 2015 onward): prc.cm carries scans only, no text (no OCR)",
        "Constitutional Council decisions: not published online (no official site found, 2026-11-06)",
        "Supreme Court judgments beyond the few dozen on coursupreme.cm: not published online",
        "Lower-court judgments: not published online (minjustice.cm LÉGALIS holds 0, 2026-11-06)",
        "Consolidated legislation: not published online (prc.cm gives acts as signed; LÉGALIS has 2 laws)",
    )
    samples = {
        "caselaw_query": "pourvoi",
        "decision_id": "Section Civile/arret--n°-20civ-du-04-avril-2024",
        "legislation_query": "organisation du Ministère",
        "law_id": "151",
        "provision": "Article 2",
    }

    # ---- case law
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        lang = ((filters or {}).get("language") or "fr").lower()
        if lang not in ("fr", "en"):
            raise BadRequest("language must be 'fr' or 'en'.")
        q = _http.clean(query or "")
        if q and len(q) < 3:
            raise BadRequest("The Supreme Court search needs at least 3 characters.")
        items, total = await _paged(lambda n: _cs_page(q, lang, n), page, limit, CS_PAGE)
        note = ("Full-text search of coursupreme.cm (judgments only); French and English pages are "
                "indexed separately (filter language='en' for the Common Law Division). The site has "
                "no date filter and the results are in its relevance order, not by date (without a "
                "query, the list is newest first); read the date of each hit.")
        return Results(items=items, total=total, note=note)

    async def get_decision(self, id):
        cid = _cs_id(id)
        title = text = pdf = ""
        lang = "fr"
        for lang in ("fr", "en"):
            r = await _get(_cs_url(cid, lang), f"judgment {cid}", CS_HOST)
            title, text, pdf = _cs_body(r.content)
            if len(text) > 200:
                break
        if not title:
            raise NotFound(f"No Supreme Court judgment at {cid!r}.")
        if len(text) <= 200:
            if pdf:
                raise SourceError(f"The page for {cid!r} has no text; the judgment is only a PDF: {pdf}", "")
            raise NotFound(f"The page {cid!r} has no text. Judgments are stored in their original language "
                           f"only: search again with filter language='en' (Common Law Division) or 'fr'.")
        cn = _CASE_NO.search(title)
        meta = {"category": cid.split("/")[0], "language": lang}
        if pdf:
            meta["pdf"] = pdf
        return Decision(id=cid, title=title, text=text, url=_cs_url(cid, lang),
                        court=f"Cour suprême du Cameroun, {cid.split('/')[0]}", date=text_date(title),
                        case_number=_http.clean(cn[1]) if cn else "", metadata=meta)

    # ---- legislation
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        t = ((filters or {}).get("type") or "").lower().replace("é", "e")
        if t and t not in _TYPES:
            raise BadRequest("type must be 'loi', 'ordonnance' or 'decret'.")
        q = _http.clean(query or "")
        if q:
            cat = _TYPES.get(t, "")
            fetch, size = (lambda n: _prc_page(q, cat, n)), PRC_SEARCH_PAGE
        else:
            cat = _TYPES[t or "loi"]
            fetch, size = (lambda n: _prc_page("", cat, n)), PRC_LIST_PAGE
        items, total = await _paged(fetch, page, limit, size)
        if q:
            for h in items:      # a search hit without text excerpt from 2015 on is usually a scan
                if not h.snippet and h.date >= "2015":
                    h.snippet = ("[Probably a scan without text layer: the text tools will return only "
                                 "the PDF link.]")
        return Results(items=items, total=total,
                       note="Acts as signed, not consolidated. Site-wide search that matches any of the "
                            "words, so a query for a code or a topic can return unrelated acts; only laws, ordinances "
                            "and decrees are kept. Only presidential acts are held: no codes as such "
                            "(the Labour Code, Loi 92/007, is not on prc.cm). Acts from about 2015 on, "
                            "including the 2016 Penal Code (Loi 2016/007, id 1828), are often scans "
                            "without text: the text tools then return only the PDF link.")

    async def get_legislation_toc(self, id):
        law = await _act(_prc_id(id))
        text = _require_text(law)
        entries, level = [], 0
        for kind, lab, s, e in _split(text):
            if kind == "head":
                entries.append(TocEntry(title=lab, level=0))
                level = 1
            else:
                first = _http.clean(text[s:e].split("\n", 1)[0].replace("*", ""))
                entries.append(TocEntry(title=first or lab, level=level, provision=lab))
        if not any(e.provision for e in entries):
            entries.append(TocEntry(title=law["title"], provision="text"))
        return Toc(id=law["id"], title=law["title"], url=law["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        law = await _act(_prc_id(id))
        text = _require_text(law)
        if _http.clean(provision).lower() == "text":
            return Provision(law_id=law["id"], law_title=law["title"], provision="text", text=f"{_AS_SIGNED}{await _amenders(law)}\n\n{text}",
                             url=law["url"], as_of=law["date"])
        want = _norm_provision(provision)
        parts = [text[s:e].strip() for k, lab, s, e in _split(text) if k == "art" and lab == want]
        if not parts:
            raise NotFound(f"{want} not found in act {law['id']} ({law['title']}).")
        return Provision(law_id=law["id"], law_title=law["title"], provision=want,
                         text=f"{_AS_SIGNED}{await _amenders(law)}\n\n" + "\n\n".join(parts), url=law["url"], as_of=law["date"])

    async def get_legislation_text(self, id):
        law = await _act(_prc_id(id))
        text = _require_text(law)
        meta = {"type": law["type"], "text source": law["source"],
                "status": "as signed, not consolidated; later amendments not applied"}
        if law["pdf"]:
            meta["pdf"] = law["pdf"]
        return LawText(id=law["id"], title=law["title"], text=text, url=law["url"], as_of=law["date"],
                       metadata=meta)
