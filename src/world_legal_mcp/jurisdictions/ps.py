"""Palestine: court judgments and legislation from Maqam (maqam.najah.edu), An-Najah
National University's Faculty of Law. NON-OFFICIAL (academic) source.

Why not an official source (checked 2026-11-05/06, from this machine, via _http):
  * High Judicial Council (www.courts.gov.ps / courts.gov.ps), Official Gazette Bureau
    (lab.pna.ps, mjr.lab.pna.ps "المرجع الإلكتروني للجريدة الرسمية"), Supreme Constitutional
    Court (www.tscc.pna.ps), www.ogb.gov.ps: TCP connect timeout, robots.txt unreadable.
    tcc.ps / tcc.gov.ps / dft.gov.ps / hjc.ps: no DNS. Not used.
  * Al-Muqtafi (muqtafi.birzeit.edu, Birzeit University, academic): connect timeout; it
    also requires (free) registration for its databases. Not used.
  * Ministry of Justice (moj.pna.ps): reachable, robots.txt "Allow: /", but it is an
    Angular SPA with no legislation or judgment database of its own (its "Legal Databases"
    page is a list of links). Not used.

Maqam (verified 2026-11-06):
  * robots.txt: HTTP 404 (Django "page not found") -> no restrictions published.
  * Terms (/pages/terms-of-use/): about accounts and contributions; silent on automated
    access or reuse. Notice (/pages/notice/): content is "for citation and guidance only,
    not to be relied on officially before the courts" -> Source.warning.
  * Judgment and legislation pages are public. The advanced search forms on /judgments/
    and /legislation/ say "please log in first" -> not used. The site-wide header search
    (/search/?q=, a GET form shown to anonymous visitors) is public and returns a mix of
    legislation, judgments, General Assembly decisions and gazette issues, ~19 per page.
  * Site bug: that search answers HTTP 500 (Django TemplateDoesNotExist,
    generalauthoritydecision.html) whenever a results page contains a General Assembly
    decision. Reported as SourceError; another wording or page usually works.
  * Judgment page: metadata <dl> (year, number, decision date, court, litigation type,
    classification) + "النص" card. Recent Court of Cassation rulings have the full text in
    HTML; many older ones only a short subject line in HTML and the full text as a PDF
    ("النص الكامل"), which get_decision reads (text layer only, size-checked first).
  * Legislation page: metadata <dl>, then one <dt><a href=".../item/N/">المادة (n)</a>
    <dd> per article. Some laws (regulations, orders) have no article split, only a PDF.
"""
from __future__ import annotations

import re
from urllib.parse import urljoin

import lxml.html

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

HOST = "maqam.najah.edu"
ROOT = f"https://{HOST}"
MAX_PDF = 40 * 1024 * 1024
MAX_SOURCE_PAGES = 5          # search pages read to fill one page of one record type
_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")
_BIDI = re.compile("[‎‏‪-‮⁦-⁩]")
_search_cache: dict = {}
_law_cache: dict = {}

SOURCE = Source(
    name="Maqam – موسوعة القوانين وأحكام المحاكم الفلسطينية (An-Najah National University, "
         "Faculty of Law) – non-official (academic)",
    url=ROOT,
    covers=("caselaw", "legislation"),
    licence="unknown (no licence stated; terms of use silent on reuse)",
    commercial_use=None,
    ai_use=None,
    auth="none",
    rate_limit="unknown; 1 s spacing, no 429 seen in ~40 requests (2026-11)",
    terms_url=f"{ROOT}/pages/terms-of-use/",
    warning="Non-official academic source (An-Najah National University): the site says its "
            "content is for citation and guidance only and cannot be relied on officially "
            "before the courts; check the Official Gazette (الوقائع الفلسطينية).",
    official=False,
)


def _clean(s) -> str:
    return _http.clean(_BIDI.sub("", str(s or "")))


async def _fetch(url: str, *, params: dict | None = None, what: str = "page") -> str:
    r = await _http.get(url, params=params)
    if r.status_code == 404:
        raise NotFound(f"Maqam has no {what} at {url}.")
    if r.status_code == 500 and "TemplateDoesNotExist" in r.text:
        raise SourceError(_http.error(
            "maqam.najah.edu", f"{what} failed", 500,
            "The site's search crashes when a results page contains a General Assembly "
            "decision. Try other wording or another page."), 500)
    if r.status_code != 200:
        raise SourceError(_http.error("maqam.najah.edu", f"{what} failed", r.status_code),
                          r.status_code)
    return r.text


def _id(id: str, kind: str) -> str:
    s = _clean(id).translate(_DIGITS).split("?")[0].strip("/")
    m = re.fullmatch(rf"(?:https?://{re.escape(HOST)}/)?(?:{kind}/)?(\d+)", s)
    if not m:
        raise BadRequest(f"Bad {kind} id {id!r}: use Maqam's numeric id, e.g. "
                         f"{'11179' if kind == 'judgments' else '11'} (from search results).")
    return m[1]


def _dl(tree, xpath: str = '//dl[contains(@class,"mb-0")]') -> dict[str, str]:
    """First metadata <dl> -> {label: value}."""
    out: dict[str, str] = {}
    for dl in tree.xpath(xpath)[:1]:
        for dt in dl.xpath("./dt"):
            dd = dt.getnext()
            if dd is not None and dd.tag == "dd":
                out[_clean(dt.text_content()).rstrip(":")] = _clean(dd.text_content())
    return out


async def _pdf(url: str) -> str:
    """Text layer of a PDF, refusing anything over MAX_PDF."""
    h = await _http.request("HEAD", url)
    if h.status_code != 200:
        return ""
    size = int(h.headers.get("Content-Length") or 0)
    if size > MAX_PDF:
        return ""
    r = await _http.get(url)
    if r.status_code != 200 or len(r.content) > MAX_PDF or not r.content.startswith(b"%PDF"):
        return ""
    try:
        return _http.pdf_text(r.content)
    except Exception:  # broken PDF: keep the HTML text
        return ""


# ---------------------------------------------------------------------- #
# Site search (mixed record types)
def _parse_search(html: str) -> tuple[list[tuple[str, object]], int]:
    tree = lxml.html.fromstring(html)
    out = []
    for li in tree.xpath('//h4[contains(., "Search results")]/following-sibling::ul[1]/li'):
        a = li.xpath('./a[@href]')
        if not a:
            continue
        href = a[0].get("href").split("?")[0]
        title = _clean(a[0].text_content())
        snip = li.xpath('./div[contains(@class,"text-muted")]')
        snippet = _clean(snip[0].text_content()).lstrip(".")[:300] if snip else ""
        fields = _dl(li, './dl')
        if m := re.fullmatch(r"/judgments/(\d+)/", href):
            out.append(("judgment", _decision_hit(m[1], title, fields.get("المحكمة", ""), snippet)))
        elif m := re.fullmatch(r"/legislation/(\d+)/", href):
            out.append(("law", _law_hit(m[1], title, fields, snippet)))
    pages = [int(p) for p in re.findall(r"[?&;]page=(\d+)", html)]
    return out, max(pages, default=1)


async def _search_page(q: str, n: int) -> tuple[list, int]:
    key = (q, n)
    if key not in _search_cache:
        params = {"q": q} | ({"page": str(n)} if n > 1 else {})
        html = await _fetch(f"{ROOT}/search/", params=params, what="search")
        _http.lru_put(_search_cache, key, _parse_search(html), 32)
    return _search_cache[key]


def _norm(s: str) -> str:
    return re.sub("[\u064b-\u065f]", "", s).translate(str.maketrans("أإآة", "اااه"))


def _missing_words(q: str, titles: list[str]) -> bool:
    """True if no title contains every distinctive word of the query (Arabic, ال stripped)."""
    words = [w[2:] if w.startswith("ال") else w for w in re.findall(r"[\u0621-\u064a]{3,}", _norm(q))]
    words = [w for w in words if w not in ("قانون", "قرار", "بقانون", "بشان")]
    return bool(words) and not any(all(w in _norm(t) for w in words) for t in titles)


async def _collect(q: str, kind: str, want: int, page: int):
    hits, last, n, skipped, first_err = [], 0, 0, [], None
    while len(hits) < want and n < MAX_SOURCE_PAGES * page:
        n += 1
        try:
            items, last = await _search_page(q, n)
        except SourceError as e:
            if e.status != 500:
                raise
            first_err = first_err or e
            skipped.append(n)
            continue
        hits += [h for k, h in items if k == kind]
        if n >= last:
            break
    return hits, last, n, skipped, first_err


async def _search(q: str, kind: str, limit: int, page: int) -> Results:
    q = _clean(q)
    if not q:
        raise BadRequest("Maqam's public search needs a query (Arabic works best, e.g. "
                         "'القانون الأساسي').")
    limit, page = max(1, int(limit)), max(1, int(page))
    want = page * limit
    hits, last, n, skipped, first_err = await _collect(q, kind, want, page)
    retried = ""
    if kind == "law" and (skipped or _missing_words(q, [h.title for h in hits[:want]])) \
            and "فلسطيني" not in q:
        # The site ranks judgments first and often crashes on page 1; adding "الفلسطيني"
        # (Palestinian) usually surfaces the base law (e.g. قانون العمل الفلسطيني).
        alt = await _collect(f"{q} الفلسطيني", kind, want, page)
        if alt[0] and not alt[3] and not _missing_words(q, [h.title for h in alt[0][:want]]):
            hits, last, n, skipped, first_err = alt
            retried = f" Search was retried as '{q} الفلسطيني' because the plain wording failed or missed the law."
    if first_err and (len(skipped) == n or not hits):
        pgs = ", ".join(map(str, skipped))
        raise SourceError(_http.error(
            "maqam.najah.edu", "search failed", 500,
            f"The site's search crashed (a site bug, it happens when a results page contains a "
            f"General Assembly decision) on source page(s) {pgs} and no matching {kind} was "
            f"read from the other pages, so this is NOT a 'no results' answer: matches may "
            f"exist. Retry with shorter or different wording (e.g. one distinctive word, or "
            f"without the leading 'ال'). Page 1 of the site's own results often crashes "
            f"for broad legal terms; that is Maqam's bug, not a sign the law is missing."), 500)
    label = "judgments" if kind == "judgment" else "laws"
    broken = ""
    if skipped:
        pgs = ", ".join(map(str, skipped))
        broken = (f" INCOMPLETE: the site's search crashed (HTTP 500, a site bug) on source "
                  f"page(s) {pgs}, which were skipped, so matches on them are missing; "
                  f"this is not proof that nothing else exists.")
    status = ""
    if any("ملغ" in re.sub("[\u064b-\u065f]", "", getattr(h, "status", "") or "") for h in hits):
        status = (" Status is Maqam's own label, not checked against the Official Gazette; "
                  "'مُلغى' (repealed) can refer to an earlier version of a text that was "
                  "amended and may still be in force.")
    law = ""
    if kind == "law":
        law = (" Results are relevance-ranked and often amendments rather than the base law: "
               "check Type/Number; a base code missing from the hits is not shown to be absent "
               "from Maqam (retry with its short title or number).")
        if any(re.sub("[\u064b-\u065f]", "", h.status or "").find("ملغ") >= 0
               and h.title.startswith("القانون الأساسي") for h in hits):
            law += (" The Basic Law (القانون الأساسي), amended 2003, is generally treated as "
                    "the operative constitution; Maqam's 'مُلغى' label on its entries refers "
                    "to earlier versions or is a data error (unverified: check the Official "
                    "Gazette).")
    items = hits[(page - 1) * limit:want]
    if kind == "law" and items and _missing_words(q, [h.title for h in items]):
        law += (f" NO RETURNED TITLE MATCHES '{q}': the law you asked for is not among these "
                f"hits, it may not be on Maqam under that name (or the site's search did not "
                f"rank it). Do not treat these as the law you asked for.")
    if kind == "law" and not items and not skipped:
        law += (f" NOTHING on Maqam matches '{q}': the law may not be published there "
                f"(not proof it does not exist; check the Official Gazette).")
    elif kind == "law" and items and not skipped:
        nq = _norm(q)
        if nq.startswith("قانون") and not re.search(r"\d", nq) \
                and not any(_norm(h.title).startswith(nq) for h in hits):
            law += (f" No hit is titled '{q}' itself (they are amendments or other laws "
                    f"that mention it): the base law was not found on Maqam under that title.")
    return Results(
        items=items, total=None,
        note=f"{retried.strip() + ' ' if retried else ''}{broken.strip() + ' ' if broken else ''}Maqam's site search mixes {label} with other record types "
             f"({last or '?'} source pages of ~19); non-official academic source, Arabic only. "
             f"No date or court filter exists: sort by the dates shown.{status}{law}")


def _decision_hit(id: str, title: str, court: str, snippet: str = "") -> DecisionHit:
    m = re.search(r"رقم\s*(\d+\s*/\s*\d+)", title)
    d = re.search(r"\d{4}-\d{2}-\d{2}", title)
    return DecisionHit(id=id, title=title, court=court, date=d[0] if d else "",
                       case_number=m[1].replace(" ", "") if m else "", snippet=snippet,
                       url=f"{ROOT}/judgments/{id}/")


def _law_hit(id: str, title: str, fields: dict, snippet: str = "") -> LawHit:
    num = re.search(r"رقم\s*\(?\s*(\d+)\s*\)?", title.translate(_DIGITS))
    year = re.search(r"لسنة\s*(\d{4})", title.translate(_DIGITS))
    number = "/".join(x for x in (num[1] if num else "", year[1] if year else "") if x)
    return LawHit(id=id, title=title, type=fields.get("نوع التشريع", ""), number=number,
                  status=fields.get("حالة التشريع", ""), snippet=snippet,
                  url=f"{ROOT}/legislation/{id}/")


# ---------------------------------------------------------------------- #
# Legislation pages
def _key(label: str) -> str:
    s = _clean(label).translate(_DIGITS).lower()
    s = re.sub(r"^(?:ال)?مادة|^art(?:icle)?\.?", "", s)
    return re.sub(r"[\s()\[\]{}.:\-–]", "", s)


async def _law(id: str) -> dict:
    lid = _id(id, "legislation")
    if lid in _law_cache:
        return _law_cache[lid]
    url = f"{ROOT}/legislation/{lid}/"
    tree = lxml.html.fromstring(await _fetch(url, what="law"))
    meta = _dl(tree)
    title = meta.get("العنوان") or _clean((tree.xpath("//title/text()") or [""])[0])
    if not title:
        raise SourceError(f"Error (maqam.najah.edu): no title on {url}.")
    entries, arts = [], []
    for block in tree.xpath('//div[contains(@class,"card-body")][.//a[contains(@href,"/item/")]]'):
        for el in block.iter("h6", "dt"):
            if el.tag == "h6":
                head = _clean(el.text_content())
                if head:
                    entries.append(TocEntry(title=head, level=0))
                continue
            a = el.xpath('.//a[contains(@href,"/item/")]')
            dd = el.getnext()
            if not a or dd is None or dd.tag != "dd":
                continue
            label = _clean(a[0].text_content())
            paras = _http.html_paragraphs(lxml.html.tostring(dd, encoding="unicode"))
            body = "\n\n".join(paras)
            heading = paras[0].split("  \n")[0].strip(" :") if paras else ""
            entries.append(TocEntry(title=f"{label} – {heading}" if heading else label,
                                    level=1, provision=label))
            arts.append((label, body, urljoin(ROOT, a[0].get("href"))))
    if entries and all(e.level == 1 for e in entries):
        entries = [TocEntry(e.title, 0, e.provision) for e in entries]
    pdf = next((urljoin(ROOT, h) for h in tree.xpath('//a[contains(@href,"/media/")]/@href')
                if h.lower().endswith(".pdf")), "")
    data = {"id": lid, "title": title, "url": url, "meta": meta, "entries": entries,
            "arts": arts, "pdf": pdf}
    return _http.lru_put(_law_cache, lid, data, 8)


class Palestine(Jurisdiction):
    code = "ps"
    name = "Palestine"
    languages = ("ar",)
    aliases = ("palestine", "state of palestine", "فلسطين", "pse")
    sources = (SOURCE,)
    min_interval = {HOST: 1.0}
    notes = ("Non-official academic source (Maqam, An-Najah University): Court of Cassation, "
             "High Court, Constitutional Court rulings and laws in force in the West Bank/Gaza. "
             "Official sites (courts.gov.ps, lab.pna.ps) were unreachable. Arabic only.")
    gaps = (
        "Official court judgments (courts.gov.ps, High Judicial Council): site unreachable (TCP "
         "timeout, 2026-11-05/06)",
        "Official Gazette (lab.pna.ps, mjr.lab.pna.ps): site unreachable (TCP timeout, "
         "2026-11-05/06)",
        "Supreme Constitutional Court site (tscc.pna.ps): site unreachable (TCP timeout, "
         "2026-11-05/06)",
        "Al-Muqtafi (Birzeit University): connect timeout; its databases need a free registration"
         " we have not done",
        "Maqam advanced search: needs a login, not used (public header search only)",
    )
    samples = {
        "caselaw_query": "القانون الأساسي",
        "decision_id": "11179",
        "legislation_query": "الشركات",
        "law_id": "11",
        "provision": "المادة (1)",
    }

    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        return await _search(query, "judgment", limit, page)

    async def get_decision(self, id):
        did = _id(id, "judgments")
        url = f"{ROOT}/judgments/{did}/"
        html = await _fetch(url, what="judgment")
        tree = lxml.html.fromstring(html)
        title = _clean((tree.xpath("//title/text()") or [""])[0])
        meta = _dl(tree)
        if not title or not meta:
            raise SourceError(f"Error (maqam.najah.edu): unexpected judgment page at {url}.")
        body = tree.xpath('//h4[contains(@class,"card-title")][normalize-space()="النص"]/..')
        text = ""
        if body:
            for h in body[0].xpath("./h4"):
                h.drop_tree()
            text = _http.html_to_md(lxml.html.tostring(body[0], encoding="unicode"))
        pdf = next((urljoin(ROOT, h) for h in tree.xpath('//a[contains(@href,"/media/")]/@href')
                    if h.lower().endswith(".pdf")), "")
        summary = ""
        if len(text) < 1500 and pdf:
            full = await _pdf(pdf)
            if full:
                summary, text = text, full
        if not text:
            raise SourceError(f"Error (maqam.najah.edu): judgment {did} has no readable text "
                              f"(see {pdf or url}).")
        cites = [_clean(b.text_content())
                 for b in tree.xpath('//h4[contains(.,"النصوص القانونية المذكورة")]'
                                     '/following-sibling::ul[1]//b')]
        hit = _decision_hit(did, title, meta.get("المحكمة", ""))
        metadata = {k: v for k, v in meta.items() if k in ("نوع التقاضي", "التصنيفات")}
        if pdf:
            metadata["PDF"] = pdf
        if cites:
            metadata["النصوص القانونية المذكورة"] = "؛ ".join(cites)
        return Decision(id=did, title=title, text=text, url=url, court=hit.court,
                        date=hit.date or _http.iso_date(meta.get("تاريخ الفصل", "")),
                        case_number=hit.case_number, summary=summary, metadata=metadata)

    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        return await _search(query, "law", limit, page)

    async def get_legislation_toc(self, id):
        law = await _law(id)
        entries = law["entries"]
        if not law["arts"]:
            entries = [TocEntry(title=f"No article split on Maqam; full text is a PDF: "
                                      f"{law['pdf'] or law['url']}")]
        return Toc(id=law["id"], title=law["title"], url=law["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        law = await _law(id)
        want = _key(provision)
        if not want:
            raise BadRequest("Give an article, e.g. 'المادة (5)', 'المادة 5', '5' or 'art. 5'.")
        for label, body, url in law["arts"]:
            if _key(label) == want:
                return Provision(law_id=law["id"], law_title=law["title"], provision=label,
                                 text=f"**{label}**\n\n{body}", url=url)
        if not law["arts"]:
            raise NotFound(f"Law {law['id']} has no article split on Maqam; read the full "
                           f"text with get_legislation_text or the PDF: {law['pdf'] or law['url']}")
        raise NotFound(f"No article {provision!r} in law {law['id']} ({law['title']}). "
                       f"Labels look like {law['arts'][0][0]!r}; see get_legislation_toc.")

    async def get_legislation_text(self, id):
        law = await _law(id)
        parts, cur = [], 0
        for e in law["entries"]:
            if not e.provision:
                parts.append(f"## {e.title}")
                continue
            label, body, _ = law["arts"][cur]
            cur += 1
            parts.append(f"**{label}**\n\n{body}")
        text = "\n\n".join(parts)
        if not text and law["pdf"]:
            text = await _pdf(law["pdf"])
        if not text:
            raise SourceError(f"Error (maqam.najah.edu): law {law['id']} has no readable text "
                              f"(see {law['pdf'] or law['url']}).")
        meta = dict(law["meta"])
        meta.pop("العنوان", None)
        if law["pdf"]:
            meta["PDF"] = law["pdf"]
        return LawText(id=law["id"], title=law["title"], text=text, url=law["url"],
                       metadata=meta)
