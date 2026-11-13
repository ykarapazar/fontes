"""Serbia: case law from the Supreme Court's practice database (www.vrh.sud.rs).

Gotchas this code encodes (verified 2026-11-06 from a UK IP):
  * The database ("Baza sudske prakse Suda") holds selected, anonymised decisions of the
    Vrhovni sud (from 2023), its predecessor the Vrhovni kasacioni sud (2010-2022) and the
    Vrhovni sud Srbije (before 2010). Search is GET /sr-lat/solr-search-page/results;
    court_type sc / vks / vs narrows to one court, no court_type searches all three.
  * `keywords` words are OR-ed (Solr); AND / OR / quotes work. `phrase` is an exact
    text match. The page size must be one of 10/25/50/100/250/500/1000 (anything else
    falls back to 10); `page` is 0-based.
  * The id is the decision page's path slug ("rev2-21802023-3520-35224"), the source's
    own URL; the title is "<register> <number>/<year>" plus the court's subject
    descriptors. A case number ("Rev2 2180/2023") is also accepted: it is resolved
    through the subject_number search.
  * robots.txt: Crawl-delay 10 and Disallow /search/ (Drupal's own search, not used);
    the Solr results page and decision pages are allowed. Hence 10 s spacing.
  * Legislation: the state Legal Information System (pravno-informacioni-sistem.rs) terms
    forbid any automated extraction without written consent. What we do serve is what the
    Constitutional Court publishes as HTML under www.ustavni.sud.rs/ustav-rs-i-propisi/:
    the consolidated Constitution (with Amendments I-XXIX, 2022), the 2006 Constitutional
    Law and the Law on the Constitutional Court (an "unofficial consolidated text", the
    page says so). Pages are flat <div>s: centred divs ('text-center') carry part titles,
    article headings and 'Члан N.'; the body divs between them are sometimes left unclosed,
    so we split the raw HTML on the centred divs instead of walking the tree.
    parlament.gov.rs has laws as adopted (PDF), current convocation only: not built.
"""
from __future__ import annotations

import html
import re
from urllib.parse import quote, unquote, urlencode, urlsplit

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc, TocEntry

HOST = "www.vrh.sud.rs"
VRH = f"https://{HOST}"
SEARCH = f"{VRH}/sr-lat/solr-search-page/results"
COURTS = {"sc": "Vrhovni sud", "vks": "Vrhovni kasacioni sud", "vs": "Vrhovni sud Srbije"}
MATTERS = {"civil": "19", "administrative": "9", "criminal": "33", "trial-delay": "8"}
SORTS = {"relevance": "by_relevance", "newest": "by_date_down", "oldest": "by_date_up",
         "title": "by_title"}
PAGE_SIZES = (10, 25, 50, 100, 250, 500, 1000)
_CASE = re.compile(r"^\s*([A-Za-zŽžĆćČčŠšĐđ][A-Za-zŽžĆćČčŠšĐđ0-9 .\-]{0,15}?)\s+(\d+/\d{2,4})\b")

_docs: dict = {}

US_HOST = "www.ustavni.sud.rs"
US_LAWS = f"https://{US_HOST}/ustav-rs-i-propisi/"
# our id -> (page slug, title, Latin title, type, adoption date)
LAWS = {
    "ustav": ("ustav-republike-srbije", "Устав Републике Србије", "Ustav Republike Srbije",
              "Устав", "2006-11-08"),
    "ustavni-zakon": ("ustavni-zakon", "Уставни закон за спровођење Устава Републике Србије (2006)",
                      "Ustavni zakon za sprovođenje Ustava Republike Srbije (2006)",
                      "Уставни закон", "2006-11-10"),
    "zakon-o-ustavnom-sudu": ("zakon-o-ustavnom-sudu", "Закон о Уставном суду",
                              "Zakon o Ustavnom sudu", "Закон", "2007-11-26"),
}
_laws: dict = {}
_LAT2CYR = dict(zip("abvgdđežzijklmnoprstćufhcčšABVGDĐEŽZIJKLMNOPRSTĆUFHCČŠ",
                    "абвгдђежзијклмнопрстћуфхцчшАБВГДЂЕЖЗИЈКЛМНОПРСТЋУФХЦЧШ"))

_CYR2LAT = {ord(c): l for l, c in _LAT2CYR.items() if l.islower()} | {ord("џ"): "dž", ord("љ"): "lj", ord("њ"): "nj"}


def _cyr(s: str) -> str:
    """Serbian Latin -> Cyrillic (dž/lj/nj first), lower-cased: for matching only."""
    s = s.lower().replace("dž", "џ").replace("lj", "љ").replace("nj", "њ")
    return "".join(_LAT2CYR.get(c, c) for c in s)


def _date_param(s: str, name: str) -> str:
    iso = _http.iso_date(s)
    if not iso:
        raise BadRequest(f"{name} must be a date like '2024-01-31' or '31.01.2024'.")
    y, m, d = iso.split("-")
    return f"{d}-{m}-{y}"


def _slug(id: str) -> str:
    """URL, '/sr-lat/<slug>' or '<slug>' -> decoded slug; '' if it isn't one."""
    s = _http.clean(id)
    if s.startswith("http"):
        u = urlsplit(s)
        if (u.hostname or "").lower() not in (HOST, "vrh.sud.rs"):
            raise BadRequest(f"Not a {HOST} URL: {id!r}.")
        s = u.path
    s = unquote(s).strip("/")
    s = re.sub(r"^sr-lat/", "", s)
    return s if re.fullmatch(r"[\w\-]+", s) and "-" in s else ""


def _court_name(head: str) -> str:
    h = head.upper()
    if "VRHOVNI KASACIONI SUD" in h:
        return COURTS["vks"]
    if "VRHOVNI SUD SRBIJE" in h:
        return COURTS["vs"]
    if "VRHOVNI SUD" in h:
        return COURTS["sc"]
    return ""


def _strip(s: str) -> str:
    return _http.clean(html.unescape(re.sub(r"<[^>]+>", "", s or "")))


class Serbia(Jurisdiction):
    code = "rs"
    name = "Serbia"
    languages = ("sr",)
    aliases = ("serbia", "srbija", "србија", "srb")
    sources = (
        Source(
            name="Vrhovni sud (Supreme Court of Serbia): Baza sudske prakse",
            url=f"{VRH}/sr-lat/baza-sudske-prakse-suda",
            covers=("caselaw",),
            licence=("No licence stated; site footer claims copyright for the Court over all "
                     "site material. Court decisions are not copyright works under the Serbian "
                     "Copyright Act (Zakon o autorskom i srodnim pravima, čl. 6)."),
            commercial_use=None,
            ai_use=None,   # robots.txt has no AI/TDM opt-out; no terms page found
            auth="none",
            rate_limit=("robots.txt Crawl-delay: 10 (read 2026-11-06); using 10 s spacing, "
                        "no 429 seen"),
            terms_url=f"{VRH}/robots.txt",
        ),
        Source(
            name="Ustavni sud (Constitutional Court): Ustav RS i propisi",
            url=US_LAWS + "ustav-republike-srbije",
            covers=("legislation",),
            licence=("No licence or terms page; footer '© Република Србија Уставни суд'. "
                     "Laws are not copyright works under the Serbian Copyright Act (čl. 6)."),
            commercial_use=None,
            ai_use=None,   # robots.txt: no AI/TDM opt-out; the law pages are allowed
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 in ~8 requests (2026-11-10)",
            terms_url=f"https://{US_HOST}/robots.txt",
            probe={"legislation_query": "ustav", "law_id": "ustav", "provision": "Члан 32"},
        ),
    )
    caselaw_filters = {
        "court": "'sc' Vrhovni sud (2023-), 'vks' Vrhovni kasacioni sud (2010-2022), "
                 "'vs' Vrhovni sud Srbije (-2009); default all",
        "matter": "'civil', 'criminal', 'administrative' or 'trial-delay'",
        "phrase": "exact text the decision must contain",
        "case_number": "case number, e.g. '2180/2023' or 'Rev2 2180/2023'",
        "date_from": "decision date from, e.g. '2024-01-31'",
        "date_to": "decision date to, e.g. '2024-12-31'",
        "sort": "'relevance' (default with a query), 'newest', 'oldest' or 'title'",
    }
    min_interval = {HOST: 10.0, US_HOST: 1.0}
    notes = ("Case law: selected, anonymised Supreme Court decisions (Vrhovni sud and its "
             "predecessors). Legislation: only the consolidated Constitution, the 2006 "
             "Constitutional Law and the Law on the Constitutional Court (Cyrillic, by article); "
             "the state legal information system's terms forbid automated access.")
    gaps = (
        ("Consolidated legislation (pravno-informacioni-sistem.rs): terms forbid automated use "
         "without written consent ('Строго је забрањено')"),
        ("Laws as adopted (parlament.gov.rs PDFs): not built: current convocation (2024-) only, "
         "amending acts as passed, never consolidated"),
        ("Appellate and first-instance courts (sudskapraksa.sud.rs): connection timed out "
         "(2026-11-06)"),
        "Supreme Court decisions outside the court's selection: not published online",
        "Constitutional Court: not researched yet",
    )
    samples = {
        "caselaw_query": "zastarelost",
        "decision_id": "rev2-21802023-3520-35224",
        "legislation_query": "ustav",
        "law_id": "ustav",
        "provision": "Члан 32",
    }

    # ------------------------------------------------------------------ search
    async def _search(self, params: dict, *, limit: int, page: int):
        limit = max(1, int(limit))
        size = next((s for s in PAGE_SIZES if s >= limit), PAGE_SIZES[-1])
        limit = min(limit, size)
        offset = (max(1, int(page)) - 1) * limit
        hits, total = [], None
        src_page = offset // size
        skip = offset % size
        while len(hits) < limit:
            q = dict(params, results=str(size), page=str(src_page))
            r = await _http.get(f"{SEARCH}?{urlencode(q)}")
            if r.status_code != 200:
                raise SourceError(_http.error("Vrhovni sud", "search failed", r.status_code),
                                  r.status_code)
            h = r.text
            m = re.search(r"od ukupno\s+([\d.]+)\s+rezultat", h)
            if m:
                total = int(m[1].replace(".", ""))
            elif "search-results-title" not in h and "solr-search-form" not in h:
                raise SourceError("Vrhovni sud search page has an unexpected layout.")
            page_hits = []
            for li in re.findall(r'<li class="search-result">(.*?)</li>', h, re.S):
                a = re.search(r'<h3[^>]*>\s*<a href="([^"]+)"[^>]*>(.*?)</a>', li, re.S)
                if not a:
                    continue
                slug = _slug(a[1])
                if not slug:
                    continue
                summ = _strip((re.search(r'result-summary">(.*?)</div>', li, re.S) or ["", ""])[1])
                snip = _strip((re.search(r'search-snippet">(.*?)</p>', li, re.S) or ["", ""])[1])
                title = _strip(a[2])
                dm = re.search(r"Datum:\s*([\d.]+)", summ)
                cm = _CASE.match(title)
                page_hits.append(DecisionHit(
                    id=slug, title=title, court=COURTS.get(params.get("court_type", ""), ""),
                    date=_http.iso_date(dm[1].rstrip(".")) if dm else "",
                    case_number=f"{cm[1]} {cm[2]}" if cm else "",
                    snippet=snip.strip(" .")[:300], url=f"{VRH}/sr-lat/{quote(slug)}"))
            hits += page_hits[skip:]
            skip = 0
            src_page += 1
            if len(page_hits) < size or (total is not None and src_page * size >= total):
                break
        return hits[:limit], (total if total is not None else (None if hits else 0))

    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        f = {k: _http.clean(v) for k, v in (filters or {}).items() if _http.clean(v)}
        params: dict[str, str] = {}
        q = _http.clean(query)
        if q:
            params["keywords"] = q
        if "court" in f:
            c = f["court"].lower()
            if c not in COURTS:
                raise BadRequest("court must be 'sc' (Vrhovni sud), 'vks' (Vrhovni kasacioni "
                                 "sud) or 'vs' (Vrhovni sud Srbije).")
            params["court_type"] = c
        if "matter" in f:
            mt = f["matter"].lower()
            if mt not in MATTERS:
                raise BadRequest("matter must be one of: " + ", ".join(MATTERS) + ".")
            params["matter"] = MATTERS[mt]
        if "phrase" in f:
            params["phrase"] = f["phrase"]
        register = ""
        if "case_number" in f:
            cm = _CASE.match(f["case_number"]) or re.fullmatch(r"\s*()(\d+/\d{2,4})\s*", f["case_number"])
            if not cm:
                raise BadRequest("case_number must look like '2180/2023' or 'Rev2 2180/2023'.")
            register, params["subject_number"] = cm[1], cm[2]
        if "date_from" in f:
            params["date_from[date]"] = _date_param(f["date_from"], "date_from")
        if "date_to" in f:
            params["date_to[date]"] = _date_param(f["date_to"], "date_to")
        sort = f.get("sort", "").lower() or ("relevance" if q else "newest")
        if sort not in SORTS:
            raise BadRequest("sort must be 'relevance', 'newest', 'oldest' or 'title'.")
        params["sorting"] = SORTS[sort]
        if not params.keys() - {"sorting"}:
            raise BadRequest("Give a query or a filter (court, matter, phrase, case_number, dates).")
        hits, total = await self._search(params, limit=limit, page=page)
        if register:
            hits = [h for h in hits if h.case_number.lower() == f"{register} {params['subject_number']}".lower()]
            total = None
        return Results(hits, total=total, note=(
            "Selected Supreme Court decisions only (Vrhovni sud / Vrhovni kasacioni sud / "
            "Vrhovni sud Srbije), anonymised. Query words are OR-ed: use AND to require all."))

    # ------------------------------------------------------------------ decision
    async def _resolve_case_number(self, register: str, number: str) -> str:
        hits, _ = await self._search({"subject_number": number, "sorting": "by_date_down"},
                                     limit=50, page=1)
        want = f"{register} {number}".lower()
        for h in hits:
            if h.case_number.lower() == want:
                return h.id
        raise NotFound(f"No decision {register} {number} in the Supreme Court practice database.")

    async def get_decision(self, id):
        slug = _slug(id)
        if not slug:
            cm = _CASE.match(_http.clean(id))
            if not cm:
                raise BadRequest(f"Bad Vrhovni sud decision id {id!r}. Use the page slug from a "
                                 f"search (e.g. 'rev2-21802023-3520-35224'), its URL, or a case "
                                 f"number such as 'Rev2 2180/2023'.")
            slug = await self._resolve_case_number(cm[1], cm[2])
        if slug in _docs:
            return _docs[slug]
        url = f"{VRH}/sr-lat/{quote(slug)}"
        r = await _http.get(url)
        if r.status_code == 404:
            raise NotFound(f"No Vrhovni sud page {slug!r}.")
        if r.status_code != 200:
            raise SourceError(_http.error("Vrhovni sud", f"fetching {slug}", r.status_code),
                              r.status_code)
        h = r.text
        if "node-court-practice" not in h:
            raise NotFound(f"{url} is not a court decision page.")
        tm = re.search(r'<h1 id="page-title">(.*?)</h1>', h, re.S)
        title = _strip(tm[1]) if tm else slug
        a = h.find('<div class="field field-name-body')
        b = h.find('<div class="files-wrapper"', a)
        if b < 0:
            b = h.find("</article>", a)
        if a < 0:
            raise SourceError(f"Vrhovni sud page for {slug} has no text block (layout changed?).")
        text = _http.html_to_md(h[a:b])
        head = text[:400]
        dm = re.search(r"\b(\d{1,2}\.\d{1,2}\.\d{4})\b", head)
        cm = _CASE.match(title)
        pdf = re.search(r'href="(/sr-lat/vks-search-download-file/\d+)"', h)
        meta = {"PDF": f"{VRH}{pdf[1]}"} if pdf else {}
        d = Decision(id=slug, title=title, text=text, url=url, court=_court_name(head),
                     date=_http.iso_date(dm[1]) if dm else "",
                     case_number=f"{cm[1]} {cm[2]}" if cm else "", metadata=meta)
        return _http.lru_put(_docs, slug, d, 16)


    # ------------------------------------------------------------------ legislation
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        q = _cyr(_http.clean(query))
        hits = []
        names_law = q.startswith("закон ")   # a statute name, not a topic: no article-text matching
        for lid, (_, title, lat, typ, date) in LAWS.items():
            snippet = ""
            if q and not all(w in _cyr(title) for w in q.split()):
                if names_law:
                    continue
                law = await _law(lid)
                art = next((a for a in law["articles"]
                            if all(w in _cyr(a[2]) for w in q.split())), None)
                if not art:
                    continue
                snippet = _http.clean(art[2].replace("**", ""))[:300]
            hits.append(LawHit(id=lid, title=title, type=typ, date=date, status="на снази",
                               snippet=snippet, url=US_LAWS + LAWS[lid][0]))
        start = (max(1, page) - 1) * limit
        missing = (f"'{query}' is NOT available through this server (not in the corpus). "
                   if names_law and not hits else "")
        return Results(hits[start:start + limit], total=len(hits), note=missing + (
            "Only the Constitution, the 2006 Constitutional Law and the Law on the "
            "Constitutional Court are available for Serbia (texts as published by the "
            "Constitutional Court); other laws are on pravno-informacioni-sistem.rs, whose "
            "terms forbid automated use."))

    async def get_legislation_toc(self, id):
        law = await _law(id)
        return Toc(id=law["id"], title=law["title"], url=law["url"], entries=law["toc"])

    async def get_legislation_provision(self, id, provision):
        law = await _law(id)
        label = _art_label(provision)
        for lab, head, text in law["articles"]:
            if lab == label:
                return Provision(law_id=law["id"], law_title=law["title"], provision=f"Члан {lab}",
                                 text=text, url=law["url"])
        raise NotFound(f"No article {provision!r} in {law['title']}; labels look like 'Члан 32' "
                       "or 'član 32'.")

    async def get_legislation_text(self, id):
        law = await _law(id)
        return LawText(id=law["id"], title=law["title"], text=law["text"], url=law["url"],
                       metadata={"Објављено": law["intro"]} if law["intro"] else {})


def _law_id(raw: str) -> str:
    s = _http.clean(raw).lower()
    if s.startswith("http"):
        s = urlsplit(s).path
    s = unquote(s).strip("/").split("/")[-1]
    for lid, (slug, *_rest) in LAWS.items():
        if s in (lid, slug):
            return lid
    if s in ("устав", "constitution", "ustav-rs"):
        return "ustav"
    raise NotFound(f"Serbian law ids here are {', '.join(LAWS)}; got {raw!r}. Other laws are "
                   "not available (pravno-informacioni-sistem.rs forbids automated use).")


def _art_label(raw: str) -> str:
    s = _cyr(_http.clean(raw))
    s = re.sub(r"^(члан|чл\.?|арт\.?|артицле|art\.?)\s*", "", s).rstrip(". ")
    m = re.fullmatch(r"(\d{1,3}[а-шђјљњћџ]?)\.?\s*(?:\((\d+/\d{4})\))?", s)
    if not m:
        raise BadRequest(f"Article labels look like 'Члан 32', 'član 32', '32' or, for an "
                         f"amending act's own articles, 'Члан 8 (10/2023)'; got {raw!r}")
    return m[1] + (f" ({m[2]})" if m[2] else "")


_CENTRED = re.compile(r'<(?:div|p) class="text-center">(.*?)</(?:div|p)>', re.S)
_ART = re.compile(r"^Члан\s+(\d{1,3}[а-шђјљњћџ]?)\.?$")


async def _law(id: str) -> dict:
    lid = _law_id(id)
    if lid in _laws:
        return _laws[lid]
    slug, title, *_ = LAWS[lid]
    url = US_LAWS + slug
    r = await _http.get(url)
    if r.status_code != 200:
        raise SourceError(_http.error(US_HOST, f"law page {slug}", r.status_code), r.status_code)
    body = r.text
    i = body.find('<div class="text-content">')
    if i < 0:
        raise SourceError(f"{US_HOST}: law page {slug} has no text block (layout changed?)")
    # the text block ends at the list of PDF downloads, else at the side menu
    j = min((k for k in (body.find('<ul class="proper-list"', i), body.find("<aside", i))
             if k > 0), default=len(body))
    block = body[i:j]
    m = re.search(r'<div class="intro">(.*?)</div>', block, re.S)
    intro = _strip(m[1]) if m else ""
    if m:
        block = block[:m.start()] + block[m.end():]
    # a few headings and 'Члан N.' lines lack the class (Устав, Члан 17): centre them
    block = re.sub(r'<div>\s*(Члан\s+\d{1,3}[а-шђјљњћџ]?\.)\s*</div>',
                   r'<div class="text-center">\1</div>', block)
    block = re.sub(r'<div>([^<.]{1,100})</div>(\s*<div class="text-center">\s*Члан\s)',
                   r'<div class="text-center">\1</div>\2', block)
    parts = _CENTRED.split(block)  # [body, centred, body, centred, ...]
    pre, toc, articles, out = [], [], [], []
    cur, pending, last_struct = None, "", False
    amend = ""  # 'СЛЕДЕ ОДРЕДБЕ ИЗМЕНЕ 99/2011 ...': later articles belong to that amending act

    def flush_body(chunk):
        nonlocal amend, cur, pending
        md = _http.html_to_md(chunk).strip()
        am = re.search(r"СЛЕДЕ ОДРЕДБЕ[^\n]*?(\d+/\d{4})[^\n]*", md)
        if am:  # the amending act's own articles follow: label them 'N (99/2011)'
            flush_text(md[:am.start()])
            amend = am[1]
            toc.append((_http.clean(am[0]).rstrip(':'), 0, len(articles)))
            cur = None
            # what is left before the next 'Члан' is at most a heading ('"Прелазна одредба')
            pending = _http.clean(md[am.end():].strip(' "„“\n')) or pending
            return
        flush_text(md)

    def flush_text(md):
        if md.strip():
            (cur[2] if cur else pre).append(md.strip())

    flush_body(parts[0])
    for k in range(1, len(parts), 2):
        c = _strip(parts[k])
        if c and c.replace("\xa0", "").strip():
            a = _ART.match(c.strip('"„“ '))
            if a:
                cur = [a[1] + (f" ({amend})" if amend else ""), pending.strip('"„“ '), []]
                articles.append(cur)
                pending, last_struct = "", False
            elif c.isupper() or re.match(r"^([IVX]+|\d+)\.\s", c) or "ДЕО" in c \
                    or re.match(r"^[а-шђјљњћџ]\)\s", c):  # 'г) Облици рада': subsection heading, not an article head
                lvl = 1 if re.match(r"^(\d+\.|[а-шђјљњћџ]\))\s", c) else 0
                if last_struct and toc and toc[-1][1] == lvl and lvl == 0:
                    toc[-1] = (f"{toc[-1][0]} – {c}", lvl, len(articles))
                else:
                    toc.append((c, lvl, len(articles)))
                last_struct, pending = True, ""
            else:
                pending, last_struct = c, False
        flush_body(parts[k + 1])
    if not articles:
        raise SourceError(f"{US_HOST}: no articles found on {slug} (layout changed?)")
    entries, full, arts = [], [], []
    if pre:
        full.append("\n\n".join(pre))
    ti = 0
    for n, (lab, head, chunks) in enumerate(articles):
        while ti < len(toc) and toc[ti][2] == n:
            t, lvl, _ = toc[ti]
            entries.append(TocEntry(title=t, level=lvl))
            full.append(f"{'#' * (lvl + 2)} {t}")
            ti += 1
        text = f"**Члан {lab}.**" + (f" {head}" if head else "") + "\n\n" + "\n\n".join(chunks)
        arts.append((lab, head, text.strip()))
        # "Član N" is listed too: the keyword filter is a plain substring match on the
        # title, and lawyers type the Latin form.
        entries.append(TocEntry(title=f"Члан {lab} (Član {lab.translate(_CYR2LAT)})"
                                + (f" – {head}" if head else ""), level=2,
                                provision=f"Члан {lab}"))
        full.append(text.strip())
    law = {"id": lid, "title": title, "url": url, "intro": intro, "toc": entries,
           "articles": arts, "text": "\n\n".join(full)}
    return _http.lru_put(_laws, lid, law, 4)
