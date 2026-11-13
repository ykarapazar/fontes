"""Lebanon: Constitutional Council decisions and the Constitution, from cc.gov.lb.

Source: the Constitutional Council's own site (المجلس الدستوري, www.cc.gov.lb, Wagtail CMS
behind Cloudflare). Official, but narrow: the Council's decisions on the constitutionality
of laws (1995 onwards) and on parliamentary election challenges (1996 onwards), plus the
Constitution (Arabic, and the site's English translation). No ordinary-court case law and
no general legislation database exists on an official, open source.

Verified 2026-11-05/06:
  * robots.txt (www.cc.gov.lb): "User-agent: * / Allow: /" with Cloudflare content signals
    "Content-Signal: search=yes,ai-train=no,use=reference", stated as a condition of access
    and an EU DSM art. 4 reservation. ai-input is not set ("neither grants nor restricts").
    It disallows named crawlers (ClaudeBot, GPTBot, CCBot ...); we send the project's own
    User-Agent. No terms-of-use page; footer says "جميع الحقوق محفوظة" (all rights reserved).
  * Decision lists: /ar/القرارات/قرارات-دستورية-القوانين/ and /ar/القرارات/قرارات-الطعون-النيابية/.
    With "X-Requested-With: XMLHttpRequest" the same URL answers JSON
    {html, paginationHtml, current_page, total_pages}; 4 decisions per page, newest first.
    Filters are substring matches on single fields: number, date (YYYY-MM-DD; day-first
    dates give HTTP 500), appeal, applicants, law (constitutional list), year (election
    year, electoral list). The electoral "constituency" filter returns HTTP 500.
  * The decision number is stored in mixed forms ("12 / 2026", "10/ 2026", "3\\1995"), so
    get_decision tries a few exact spellings before falling back to the bare number.
  * Decision text is a PDF only: /documents/<doc id>/<file>.pdf -> 302 to a CloudFront
    bucket. The text layer uses Arabic presentation forms (normalised here with NFKC) and
    has glyph-mapping faults: recent PDFs drop some letters (shown as U+FFFD), 1990s PDFs
    scramble digits. The metadata from the HTML list (number, date, law, parties) is clean.
  * Presidential-election list: no decisions ("no challenge received since 1994").
  * The Constitution is HTML: an index page links six Part pages; each has chapter tabs
    and one accordion item per article ("المادة 1" / "Article 1") or preamble paragraph
    ("فقرة (أ)" / "Par (a)"). The Council's laws (Law 250/1993, internal rules, election
    law) are PDF-only and not offered here.
  * Not used: legiliban.ul.edu.lb (Lebanese University Centre for Legal Informatics, the
    only broad legislation + case-law database). Non-official (academic), and its
    "اتفاقية رفع المسؤولية" (CustomPage.aspx?id=3) allows use of its data only for the
    user's personal, non-commercial use and claims all IP in the data; hosting it for
    others would need the Centre's permission. Its robots.txt returns HTTP 500.
"""
from __future__ import annotations

import re
import unicodedata
from urllib.parse import quote, urljoin

import lxml.html

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

HOST = "www.cc.gov.lb"
ROOT = f"https://{HOST}"
PER_PAGE = 4  # fixed by the site
COURT = "المجلس الدستوري"

# kind -> (list path, query field, label)
_LISTS = {
    "constitutional": ("/ar/القرارات/قرارات-دستورية-القوانين/", "law", "قرارات دستورية القوانين"),
    "electoral": ("/ar/القرارات/قرارات-الطعون-النيابية/", "applicants", "قرارات الطعون النيابية"),
}
_KIND_ALIASES = {"constitutionality": "constitutional", "c": "constitutional",
                 "parliamentary": "electoral", "election": "electoral", "e": "electoral"}
_ID = re.compile(r"^(constitutional|electoral)/(\d{1,3})/(\d{4})$")
_NUM = re.compile(r"(\d{1,3})\s*[/\\]\s*(\d{2,4})")
_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")

# law id -> (language, index path, title)
_LAWS = {
    "constitution": ("ar", "/ar/الدستور-والقوانين/الدستور/", "الدستور اللبناني"),
    "constitution/en": ("en", "/en/constitution-and-laws/constitution/",
                        "The Lebanese Constitution (English translation by the Constitutional Council)"),
}
_LAW_ALIASES = {"الدستور": "constitution", "دستور": "constitution", "constitution/ar": "constitution",
                "en/constitution": "constitution/en", "constitution-en": "constitution/en"}
_ARABIC = re.compile(r"[؀-ۿ]")
_law_cache: dict = {}


def _url(path: str) -> str:
    return ROOT + quote(path)


def _norm(s: str) -> str:
    return _http.clean(unicodedata.normalize("NFKC", str(s or "")).translate(_DIGITS))


def _year(y: str) -> str:
    return y if len(y) == 4 else ("19" if int(y) > 50 else "20") + y.zfill(2)


async def _fetch(url: str, params: dict | None = None, *, xhr: bool = False, what: str = "page"):
    headers = {"X-Requested-With": "XMLHttpRequest"} if xhr else None
    r = await _http.get(url, params=params, headers=headers)
    if r.status_code == 404:
        raise NotFound(f"cc.gov.lb has no {what} at {url}.")
    if r.status_code != 200:
        raise SourceError(_http.error("cc.gov.lb", f"{what} failed", r.status_code), r.status_code)
    return r


def _parse_cards(html: str, kind: str) -> list[tuple[DecisionHit, dict]]:
    if not html.strip():
        return []
    tree = lxml.html.fromstring(f"<div>{html}</div>")
    out = []
    for card in tree.xpath('//div[contains(@class,"border-neutral-300") and contains(@class,"grid-cols-12")]'):
        head = card.xpath('./div[contains(@class,"text-xl")]')
        title = _norm(head[0].text_content()) if head else ""
        m = _NUM.search(title)
        if not m:
            continue
        num, year = str(int(m[1])), _year(m[2])
        fields = {}
        for lab in card.xpath('./div[contains(@class,"text-primary-500") and contains(@class,"col-span-4")]'):
            val = lab.getnext()
            if val is not None:
                fields[_norm(lab.text_content())] = _http.clean(val.text_content())
        pdf = next((a.get("href") for a in card.xpath('.//a[@href]')
                    if a.get("href", "").startswith("/documents/")), "")
        date = _http.iso_date(_norm(fields.get("التاريخ", "")))
        if kind == "constitutional":
            snippet = fields.get("القانون المطلوب ابطاله", "")
        else:
            snippet = " – ".join(v for v in (fields.get("الدائرة", ""), fields.get("المقعد", ""),
                                             fields.get("الفرقاء", "")) if v)
        hit = DecisionHit(
            id=f"{kind}/{num}/{year}",
            title=f"{COURT}، قرار رقم {num}/{year}",
            court=f"{COURT} ({_LISTS[kind][2]})",
            date=date,
            case_number=_norm(fields.get("رقم المراجعة", "")),
            snippet=snippet[:300],
            url=urljoin(ROOT, pdf) if pdf else _url(_LISTS[kind][0]),
        )
        out.append((hit, {"fields": fields, "pdf": urljoin(ROOT, pdf) if pdf else ""}))
    return out


async def _list_page(kind: str, params: dict, page: int) -> tuple[list, int]:
    p = dict(params)
    if page > 1:
        p["page"] = page
    r = await _fetch(_url(_LISTS[kind][0]), p, xhr=True, what="decision search")
    try:
        d = r.json()
    except ValueError:
        raise SourceError("Error (cc.gov.lb): decision search did not return JSON.") from None
    return _parse_cards(d.get("html") or "", kind), int(d.get("total_pages") or 1)


# ---------------------------------------------------------------------- #
# Constitution
def _parse_part(html: str) -> tuple[str, list[tuple[str, str, str]]]:
    """Part page -> (part title, [(chapter, label, text_md)])."""
    tree = lxml.html.fromstring(html)
    h3 = tree.xpath('//h3[contains(@class,"p-5")]')
    part = _http.clean(h3[0].text_content()) if h3 else ""
    chapters = {b.get("data-tab"): _http.clean(b.text_content())
                for b in tree.xpath('//button[@data-tab]')}
    items = []
    for tab in tree.xpath('//div[contains(@class,"tab-content") and @id]'):
        chapter = chapters.get(tab.get("id"), "")
        for acc in tab.xpath('.//div[contains(@class,"accordion-item")]'):
            label = acc.xpath('.//div[contains(@class,"accordion-title")]//h2')
            body = acc.xpath('.//div[contains(@class,"accordion-content")]')
            if not label or not body:
                continue
            text = _http.html_to_md(lxml.html.tostring(body[0], encoding="unicode"))
            items.append((chapter, _http.clean(label[0].text_content()), text))
    return part, items


async def _constitution(law_id: str) -> dict:
    if law_id in _law_cache:
        return _law_cache[law_id]
    lang, path, title = _LAWS[law_id]
    index_url = _url(path)
    tree = lxml.html.fromstring((await _fetch(index_url, what="constitution index")).text)
    parts, seen = [], set()
    for a in tree.xpath('//div[@id="content-container"]//a[@href]'):
        href = a.get("href")
        full = urljoin(index_url, href)
        if full.startswith(index_url) and full != index_url and full not in seen:
            seen.add(full)
            parts.append(full)
    if not parts:
        raise SourceError(f"Error (cc.gov.lb): no Part links on {index_url}.")
    sections = []
    for url in parts:
        part, items = _parse_part((await _fetch(url, what="constitution part")).text)
        sections.append((part, url, items))
    data = {"title": title, "url": index_url, "lang": lang, "sections": sections}
    return _http.lru_put(_law_cache, law_id, data, 4)


def _law_id(id: str) -> str:
    k = _http.clean(id).lower().strip("/")
    k = _LAW_ALIASES.get(k, k)
    if k not in _LAWS:
        raise NotFound(f"Unknown law id {id!r}. cc.gov.lb has: {', '.join(_LAWS)} "
                       "(the Arabic Constitution and its English translation).")
    return k


def _find(data: dict, provision: str):
    want = _norm(provision)
    items = [(part, url, ch, label, text) for part, url, its in data["sections"]
             for ch, label, text in its]
    for it in items:
        if _norm(it[3]) == want:
            return it
    m = re.fullmatch(r"(?:art(?:icle)?\.?|المادة|مادة|م\.?)?\s*(\d+)", want, re.I)
    if m:
        for it in items:
            mm = re.fullmatch(r"(?:Article|المادة)\s*(\d+)", _norm(it[3]))
            if mm and int(mm[1]) == int(m[1]):
                return it
    m = re.fullmatch(r"(?:par(?:agraph)?\.?|فقرة|preamble)?\s*\(?\s*(\w)\s*\)?", want, re.I)
    if m:
        for it in items:
            mm = re.fullmatch(r"(?:Par|فقرة)\s*\(\s*(\w)\s*\)", _norm(it[3]))
            if mm and mm[1].lower() == m[1].lower():
                return it
    return None


class Lebanon(Jurisdiction):
    code = "lb"
    name = "Lebanon"
    languages = ("ar", "en", "fr")
    aliases = ("lebanon", "lebanese republic", "liban", "لبنان", "المجلس الدستوري")
    sources = (
        Source(
            name="المجلس الدستوري / Constitutional Council of Lebanon (cc.gov.lb)",
            url=ROOT,
            covers=("caselaw", "legislation"),
            licence=("unknown: no terms of use; footer 'جميع الحقوق محفوظة' (all rights reserved); "
                     "robots.txt Content-Signal search=yes, ai-train=no, use=reference"),
            commercial_use=None,
            ai_use=False,  # robots.txt content signal ai-train=no (ai-input not set)
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~40 requests (2026-11-06)",
            terms_url=f"{ROOT}/robots.txt",
            warning=("cc.gov.lb reserves its content against AI training (robots.txt content signal "
                     "ai-train=no, use=reference): use these texts for reference and cite the Council's "
                     "page; decision PDFs have a faulty text layer, so check the PDF."),
        ),
    )
    caselaw_filters = {
        "type": "constitutional (default: constitutionality of laws, 1995-) or electoral (parliamentary election challenges, 1996-)",
        "number": "decision number, e.g. 12 (exact number, any year)",
        "date": "exact decision date YYYY-MM-DD (the source rejects a bare year)",
        "year": "decision year: 2022, a range 2020-2022, or open-ended 2022- (read from the Council's list, newest first)",
        "applicants": "constitutional only: petitioners (الجهة المستدعية), Arabic substring",
        "election_year": "electoral only: election year, e.g. 2022",
    }
    legislation_filters = {}
    min_interval = {HOST: 1.0, "d3eoo4vpw0ewa2.cloudfront.net": 1.0}
    notes = ("Constitutional Council only: its decisions (constitutionality of laws; parliamentary "
             "election challenges), Arabic PDFs, plus the Constitution (Arabic; 'constitution/en' for "
             "the English translation). Search is Arabic: the query matches the challenged law "
             "(constitutional) or the parties (electoral). No ordinary-court case law or general "
             "legislation: legiliban.ul.edu.lb's terms allow personal use only.")
    gaps = (
        "General legislation (all laws but the Constitution): no official open source; legiliban.ul.edu.lb needs permission (personal use only)",
        "Ordinary-court case law: no official open source; legiliban.ul.edu.lb needs permission (personal use only)",
        "The Council's own laws (Law 250/1993, internal rules, election law): PDF-only on cc.gov.lb, not built yet",
    )
    samples = {
        "caselaw_query": "الموازنة",
        # Decision 12/2026 on Law 70/2026 (general amnesty)
        "decision_id": "constitutional/12/2026",
        "legislation_query": "constitution",
        "law_id": "constitution",
        "provision": "المادة 19",
    }

    # ------------------------------------------------------------------ #
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        f = {k: _http.clean(v) for k, v in (filters or {}).items() if _http.clean(v)}
        kind = f.get("type", "constitutional").lower()
        kind = _KIND_ALIASES.get(kind, kind)
        if kind not in _LISTS:
            raise BadRequest("type must be 'constitutional' or 'electoral'.")
        path, qfield, _ = _LISTS[kind]
        params = {}
        if _http.clean(query):
            params[qfield] = _http.clean(query)
        if "number" in f:
            if not re.fullmatch(r"\d{1,3}", f["number"]):
                raise BadRequest("number must be the decision number, e.g. 12.")
            params["number"] = f["number"]
        if "date" in f:
            d = _http.iso_date(f["date"])
            if not d:
                raise BadRequest("date must be an exact day YYYY-MM-DD. For a year, a range or since a year, "
                                 "use the year filter (year: 2022, 2020-2022 or 2022-).")
            params["date"] = d
        if "applicants" in f:
            if kind != "constitutional":
                raise BadRequest("applicants is a constitutional-list filter; for electoral "
                                 "decisions the query itself matches the parties.")
            params["applicants"] = f["applicants"]
        if "election_year" in f:
            if kind != "electoral" or not re.fullmatch(r"(19|20)\d{2}", f["election_year"]):
                raise BadRequest("election_year (YYYY) works with type=electoral only.")
            params["year"] = f["election_year"]
        yr = None
        if "year" in f:
            m = re.fullmatch(r"((?:19|20)\d{2})?\s*(-)?\s*((?:19|20)\d{2})?", f["year"])
            if not m or not (m[1] or m[3]) or (not m[2] and m[3]):
                raise BadRequest("year must be YYYY, a range YYYY-YYYY, or open-ended YYYY- / -YYYY.")
            yr = (int(m[1] or 0), int(m[3] or 9999) if m[2] else int(m[1]))
            if yr[0] > yr[1]:
                raise BadRequest("year range is backwards.")

        limit = max(1, min(int(limit), 5 * PER_PAGE))
        page = max(1, int(page))
        start = (page - 1) * limit
        src_page = start // PER_PAGE + 1
        skip = start % PER_PAGE
        label = _LISTS[kind][2]
        if "number" in f or yr:
            # The source filters by substring (number also hits the year) and cannot filter by
            # year, so read its list (newest first) and filter exactly here.
            matches, complete = [], False
            for sp in range(1, 41):
                rows, total_pages = await _list_page(kind, params, sp)
                below = False
                for h, _ in rows:
                    _, n, y = h.id.split("/")
                    # The list is ordered by decision date and the number's year can be wrong
                    # at the source (22/2019 dated 2022-12-22), so the date's year decides.
                    y = h.date[:4] if re.fullmatch(r"\d{4}-\d\d-\d\d", h.date or "") else y
                    if "number" in f and int(n) != int(f["number"]):
                        continue
                    if yr and int(y) > yr[1]:
                        continue
                    if yr and int(y) < yr[0]:
                        below = True
                        continue
                    matches.append(h)
                if below or sp >= total_pages or not rows:
                    complete = True
                    break
            items, total = matches[start:start + limit], (len(matches) if complete else None)
            note = (f"{label}, newest first; "
                    + (f"{len(matches)} decisions match these filters."
                       if complete else f"read the 40 newest source pages only; {len(matches)} matches so far."))
            return Results(items=items, total=total, note=note + self._empty(items))
        items: list[DecisionHit] = []
        total_pages = 1
        while len(items) < limit:
            rows, total_pages = await _list_page(kind, params, src_page)
            items += [h for h, _ in rows][skip:]
            skip = 0
            if src_page >= total_pages or not rows:
                break
            src_page += 1
        total = None
        if total_pages == 1 and page == 1:
            total = len(items)
        count = (f"{total} decisions match this query" if total is not None
                 else f"up to {total_pages * PER_PAGE} matches ({total_pages} source pages of {PER_PAGE})")
        return Results(
            items=items[:limit], total=total,
            note=(f"{label}, newest first, {count}. The query matches the "
                  f"{'challenged law' if kind == 'constitutional' else 'parties'} field only (Arabic)."
                  + self._empty(items)))

    @staticmethod
    def _empty(items) -> str:
        return ("" if items else
                " This source holds only Constitutional Council decisions: no Court of Cassation, "
                "Council of State or other ordinary-court case law exists here, so 0 hits for those "
                "is not a search failure.")

    async def _locate(self, kind: str, num: str, year: str):
        tries = [f"{num} / {year}", f"{num}\\{year}", f"{num}/ {year}", f"{num}/{year}", f"{num} /{year}"]
        for t in tries:
            rows, _ = await _list_page(kind, {"number": t}, 1)
            for hit, extra in rows:
                if hit.id == f"{kind}/{num}/{year}":
                    return hit, extra
        page, total = 1, 1
        while page <= total and page <= 30:
            rows, total = await _list_page(kind, {"number": num}, page)
            for hit, extra in rows:
                if hit.id == f"{kind}/{num}/{year}":
                    return hit, extra
            if rows and all(h.id.rsplit("/", 1)[1] < year for h, _ in rows):
                break
            page += 1
        raise NotFound(f"cc.gov.lb lists no {kind} decision {num}/{year}.")

    async def get_decision(self, id):
        ident = _http.clean(id).lower().strip("/")
        m = _ID.fullmatch(ident)
        if not m:
            raise BadRequest("Give the id from search_caselaw: '<type>/<number>/<year>', e.g. "
                             "constitutional/12/2026 or electoral/18/2022.")
        kind, num, year = m[1], str(int(m[2])), m[3]
        hit, extra = await self._locate(kind, num, year)
        if not extra["pdf"]:
            raise SourceError(f"Error (cc.gov.lb): decision {num}/{year} has no PDF link.")
        r = await _fetch(extra["pdf"], what="decision PDF")
        if b"%PDF" not in r.content[:1024]:
            raise SourceError(f"Error (cc.gov.lb): {extra['pdf']} is not a PDF.")
        text = unicodedata.normalize("NFKC", _http.pdf_text(r.content))
        if not text.strip():
            raise SourceError(f"Error (cc.gov.lb): the PDF of decision {num}/{year} has no text layer.")
        meta = {k: v for k, v in extra["fields"].items() if v}
        meta["Note"] = ("Text from the source PDF's text layer, which has glyph errors (missing "
                        "letters, scrambled digits in older PDFs); the fields above come from the "
                        "Council's HTML list. Check the PDF.")
        return Decision(
            id=hit.id, title=hit.title, text=text, url=extra["pdf"], court=hit.court,
            date=hit.date, case_number=hit.case_number,
            summary=extra["fields"].get("القانون المطلوب ابطاله", ""), metadata=meta)

    # ------------------------------------------------------------------ #
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        q = _norm(query).lower()
        title_words = ("constitution", "دستور", "lebanon", "lebanese", "لبنان", "constitution libanaise")
        hits = []
        if not q or any(w in q for w in title_words):
            hits = [LawHit(id=k, title=v[2], type="Constitution" if v[0] == "en" else "دستور",
                           date="1926-05-23", status="in force", url=_url(v[1]))
                    for k, v in _LAWS.items()]
        else:
            law_id = "constitution" if _ARABIC.search(q) else "constitution/en"
            data = await _constitution(law_id)
            found = [(label, text) for _, _, its in data["sections"] for _, label, text in its
                     if q in _norm(text).lower()]
            if found:
                snippet = "; ".join(f"{lab}: {_norm(t)[:120]}" for lab, t in found[:3])
                hits = [LawHit(id=law_id, title=data["title"], type="دستور" if data["lang"] == "ar"
                               else "Constitution", date="1926-05-23", status="in force",
                               snippet=snippet[:300], url=data["url"])]
        limit, page = max(1, int(limit)), max(1, int(page))
        return Results(items=hits[(page - 1) * limit: page * limit], total=len(hits),
                       note=("" if hits else
                             "Not in Fontes: Lebanese statutes such as the Labour Code or Penal Code (the only "
                             "broad database, legiliban.ul.edu.lb, allows personal use only). ") +
                            ("Only the Constitution is offered (Arabic official text; 'constitution/en' "
                             "is the Council's English translation). A non-title query searches its articles."))

    async def get_legislation_toc(self, id):
        law_id = _law_id(id)
        data = await _constitution(law_id)
        entries = []
        for part, _, items in data["sections"]:
            entries.append(TocEntry(title=part, level=0))
            chapter = None
            for ch, label, _ in items:
                if ch != chapter:
                    chapter = ch
                    if ch:
                        entries.append(TocEntry(title=ch, level=1))
                entries.append(TocEntry(title=label, level=2, provision=label))
        return Toc(id=law_id, title=data["title"], url=data["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        law_id = _law_id(id)
        data = await _constitution(law_id)
        it = _find(data, provision)
        if not it:
            raise NotFound(f"No provision {provision!r} in {data['title']}. Use labels like "
                           f"{'المادة 19 or فقرة (أ)' if data['lang'] == 'ar' else 'Article 19 or Par (a)'}.")
        part, url, ch, label, text = it
        head = " – ".join(x for x in (part, ch) if x)
        return Provision(law_id=law_id, law_title=data["title"], provision=label,
                         text=f"### {label}\n\n{text}" + (f"\n\n_{head}_" if head else ""),
                         url=url, as_of=_http.today())

    async def get_legislation_text(self, id):
        law_id = _law_id(id)
        data = await _constitution(law_id)
        out = []
        for part, _, items in data["sections"]:
            out.append(f"## {part}")
            chapter = None
            for ch, label, text in items:
                if ch != chapter:
                    chapter = ch
                    if ch:
                        out.append(f"### {ch}")
                out.append(f"#### {label}\n\n{text}")
        return LawText(id=law_id, title=data["title"], text="\n\n".join(out), url=data["url"],
                       as_of=_http.today())
