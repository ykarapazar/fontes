"""Guyana: Laws of Guyana (Revised Edition, L.R.O. 1/2022) from the Ministry of Legal Affairs.

Legislation (mola.gov.gy, Laravel):
  * /laws-of-guyana lists every chapter of the Laws of Guyana (one PDF per chapter, 9 a page).
    The page's own search box calls /ajax-search-law?page=N&search=Q (X-Requested-With:
    XMLHttpRequest, as its jQuery does), which returns the matching cards: "Chapter 008:01
    Criminal Law (Offences) Act" with the chapter PDF. Used for search and to resolve ids.
  * PDFs are text-layer Revised Edition prints of the Regional Law Revision Centre, like
    Trinidad and Tobago's and The Bahamas': an Arrangement of Sections, then the body.
  Id: the chapter number "8:01" (Cap. 8:01). A PDF is only fetched when the site's own search
  lists it for that chapter, and a HEAD request caps its size (MAX_PDF).

Case law: the Supreme Court of Judicature (supremecourt.gy) publishes no judgments online
(2026-11). The Caribbean Court of Justice, Guyana's final court of appeal, is served here
read-only through the `ccj` adapter: its appellate (AJ) list, kept to rows that are
Guyanese. The list marks the country ("[2020] CCJ 4 (AJ) GY") only from 2020 on; for older
rows bb.ccj_appeals reads page 1 of the judgment PDF ("On appeal from ... Guyana"). Ids are
the CCJ citation.

Acts after the 2022 Revised Edition (checked 2026-11-10): parliament.gov.gy lists Acts
1928 to June 2025 (Low Search: /publications/acts-of-parliament/result/<base64 JSON>),
robots.txt 404, but every Act PDF sampled (1/2016, 16/2022, 5/2024, 1/2025, 14/2025) is a
scan with only the Gazette running heads as text: no OCR here, so not built. The list
also stops at June 2025 (e.g. Guyana Development Bank Act 2026 missing). The Official
Gazette site (officialgazette.gov.gy) has Content-Signal ai-train=no and was not used.
"""
from __future__ import annotations

import re

from lxml import html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import LawHit, LawText, Provision, Results, Toc, TocEntry
from . import bb as _bb
from . import ccj as _ccj   # read-only: CCJ appellate judgments from Guyana
from .bb import ccj_appeals

HOST = "mola.gov.gy"
BASE = f"https://{HOST}"
LIST_URL = f"{BASE}/laws-of-guyana"
SEARCH_URL = f"{BASE}/ajax-search-law"
SITE_PAGE = 9                 # cards per page (fixed by the site)
MAX_PDF = 40_000_000          # bytes; larger PDFs are refused
_AJAX = {"X-Requested-With": "XMLHttpRequest"}
_CAP = re.compile(r"^(?:chapter|chap\.?|cap\.?)?\s*0*(\d{1,3})\s*[:.]\s*(\d{1,3})$", re.I)
_CARD_CAP = re.compile(r"^Chapter\s+(\d{1,3}):(\d{1,3})\b\s*[-–—]?\s*(.*)$", re.I)

_cache: dict = {}             # search key -> (cards, last page)
_laws: dict = {}              # law id -> parsed law (small LRU)


def _law_id(s: str) -> str:
    m = _CAP.match(_http.clean(s))
    if not m:
        raise BadRequest("Use a chapter number from search_legislation, e.g. '8:01' "
                         "(Criminal Law (Offences) Act, Cap. 8:01).")
    return f"{int(m[1])}:{int(m[2]):02d}"


async def _search(q: str, page: int) -> tuple[list[dict], int]:
    """One page of the site's own search: cards [{id, title, volume, pdf}], last page number."""
    key = (q.lower(), page)
    if key in _cache:
        return _cache[key]
    r = await _http.get(SEARCH_URL, params={"page": page, "search": q}, headers=_AJAX)
    if r.status_code != 200:
        raise SourceError(_http.error(HOST, "law search failed", r.status_code), r.status_code)
    if not r.content.strip():
        return [], 0
    doc = lhtml.fromstring(r.content)
    cards = []
    for card in doc.xpath('//div[@class="choose-card"]'):
        a = card.xpath('.//a[h6]')
        if not a:
            continue
        href = a[0].get("href", "")
        title = _http.clean(a[0].text_content())
        m = _CARD_CAP.match(title)
        if not m or not href.startswith(f"{BASE}/laws/") or not href.lower().endswith(".pdf"):
            continue
        vol = _http.clean("".join(card.xpath("./p/text()")))
        cards.append({"id": f"{int(m[1])}:{int(m[2]):02d}", "title": m[3] or title, "volume": vol,
                      "pdf": href.replace(" ", "%20")})
    pages = [int(x) for x in re.findall(r"ajax-search-law\?page=(\d+)", r.text)]
    last = max(pages + [page if cards else 0])
    return _http.lru_put(_cache, key, (cards, last), 64)


_PAGE_JUNK = re.compile(
    r"^(?:L\.R\.O\. \d+/\d{4}|LAWS OF GUYANA|\d+ Cap\. \d+:\d+ .*|.* Cap\. \d+:\d+ \d+|"
    r"SECTION|ARTICLE|REGULATION|RULE|PARAGRAPH|ARRANGEMENT OF [A-Z]+[—\- ]+Continued)$")
_SEC = re.compile(r"^\*?\s*(\d+[A-Z]{0,2})(?:\.\s+|\s+(?=[A-Z][a-z]))(\S.*)$")  # "99 Child destruction." (dot missing in source)
_SCHED = re.compile(r"^((?:FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH|SEVENTH|EIGHTH|NINTH|TENTH)\s+)?SCHEDULE\b.*$")
_AMD = re.compile(r"^\[[^\]]*\d{4}[^\]]*\]$")    # marginal amendment note "[21 of 2010]"


def _split(text: str) -> tuple[list[TocEntry], dict[str, str], str]:
    """Cut a Revised Edition PDF text into sections using its Arrangement of Sections
    (adapted from bs.py / tt.py). Returns (toc, {label: text}, full text)."""
    lines = [ln for ln in text.splitlines() if not _PAGE_JUNK.match(ln.strip())]
    full = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
    flat = [ln.strip() for ln in lines if ln.strip()]
    start = next((i for i, ln in enumerate(flat)
                  if re.match(r"^ARRANGEMENT OF (SECTIONS|ARTICLES|REGULATIONS|RULES|PARAGRAPHS|CLAUSES)\b",
                              ln.upper())), None)
    arrangement: list[tuple[str, str]] = []
    headings: dict[str, list[str]] = {}
    body_at = None
    if start is not None:
        pending: list[str] = []
        seen = set()
        wrap = False                        # the previous line was an entry (or its wrapped tail)
        for i in range(start + 1, len(flat)):
            ln = flat[i]
            m = _SEC.match(ln)
            if m:
                if m[1] in seen:            # numbering restarts: the body begins
                    body_at = i
                    break
                seen.add(m[1])
                arrangement.append((m[1], m[2]))
                wrap = True
                if pending:
                    headings[m[1]] = pending
                    pending = []
            elif ln.isupper() and len(ln) < 90:
                pending.append(ln)
                wrap = False
            elif wrap and ln[:1].islower():           # wrapped heading line
                lab, t = arrangement[-1]
                arrangement[-1] = (lab, f"{t} {ln}")
            else:
                wrap = False                # e.g. the schedules list after the last entry
    if not arrangement or body_at is None:
        return [], {}, full
    body = flat[body_at:]
    labels = [lab for lab, _ in arrangement]
    titles = dict(arrangement)
    pos: list[tuple[str, int]] = []
    k = 0
    for i, s in enumerate(body):
        for j in range(k, min(k + 4, len(labels))):
            if re.match(rf"^\*?\s*{re.escape(labels[j])}\.(\s|$)", s):
                pos.append((labels[j], i))
                k = j + 1
                break
        if k >= len(labels):
            break
    if not pos:
        return [], {}, full
    sched_at = None
    for i in range(pos[-1][1] + 1, len(body)):
        if _SCHED.match(body[i]) and body[i].split()[-1].isupper():
            sched_at = i
            break
    texts: dict[str, str] = {}
    for n, (lab, i) in enumerate(pos):
        nxt = pos[n + 1][0] if n + 1 < len(pos) else ""
        end = pos[n + 1][1] if nxt else (sched_at or len(body))
        chunk = body[i:end]
        # drop what belongs to the next section: its marginal note, amendment note, cross-heading
        notes = {titles[lab2].lower().rstrip(".") for lab2, _ in pos[n + 1:n + 8]}
        while len(chunk) > 1:
            if _AMD.match(chunk[-1]) or (chunk[-1].isupper() and len(chunk[-1]) < 90):
                chunk.pop()
                continue
            # the marginal note, possibly wrapped over several lines ("Child" / "destruction.")
            k = next((k for k in range(1, 7) if len(chunk) > k
                      and " ".join(chunk[-k:]).lower().rstrip(".") in notes), 0)
            if not k:
                break
            del chunk[-k:]
        if len(chunk) > 1 and nxt and len(chunk[-1]) < 60 and chunk[-1][:1].isupper() \
                and not chunk[-1].endswith((".", ";", ":", ",", "—", "-")):
            chunk.pop()                     # a cross-heading such as "Murder"
        texts[lab] = "\n".join(chunk)
    if sched_at is not None:
        texts["Schedule"] = "\n".join(body[sched_at:])
    toc = []
    for lab, _ in pos:
        for h in headings.get(lab, []):
            toc.append(TocEntry(title=h, level=0))
        toc.append(TocEntry(title=f"{lab}. {titles.get(lab, '')}".strip(), level=1, provision=lab))
    if "Schedule" in texts:
        toc.append(TocEntry(title="Schedule(s)", level=0, provision="Schedule"))
    return toc, texts, full


def _norm_prov(p: str) -> str:
    s = _http.clean(p)
    if re.match(r"(?i)^(the\s+)?(first|second|third|fourth|fifth)?\s*sched", s):
        return "Schedule"
    art = re.match(r"(?i)^(article|art\.?)\s*", s)
    s = re.sub(r"(?i)^(section|sec\.?|s\.|s|article|art\.?|regulation|reg\.?|rule|r\.)\s*", "", s).strip().rstrip(".")
    m = re.match(r"^(\d+[A-Za-z]{0,2})(?:\s*\(.*)?$", s)
    return ("Art. " if art else "") + m[1].upper() if m else s


async def _pdf(url: str) -> str:
    h = await _http.request("HEAD", url)
    if h.status_code == 404:
        raise NotFound(f"{HOST}: {url} is gone (HTTP 404).")
    size = int(h.headers.get("content-length") or 0)
    if size > MAX_PDF:
        raise SourceError(f"Error ({HOST}): {url} is {size // 1_000_000} MB, over the "
                          f"{MAX_PDF // 1_000_000} MB limit; read it there.", "too-large")
    r = await _http.get(url)
    if r.status_code != 200 or not r.content.startswith(b"%PDF"):
        raise SourceError(_http.error(HOST, f"PDF failed: {url}", r.status_code), r.status_code)
    text = _http.pdf_text(r.content)
    if len(text) < 200:
        raise SourceError(f"Error ({HOST}): {url} has no text layer (scanned; no OCR here); read it there.",
                          "no-text")
    return text


async def _law(id: str) -> dict:
    lid = _law_id(id)
    if lid in _laws:
        return _laws[lid]
    a, b = lid.split(":")
    cards, _ = await _search(f"{int(a):03d}:{b}", 1)
    card = next((c for c in cards if c["id"] == lid), None)
    if card is None:
        raise NotFound(f"The Laws of Guyana list ({LIST_URL}) has no Chapter {lid}.")
    raw = await _pdf(card["pdf"])
    toc, sections, full = _split(raw)
    sched = sections.get("Schedule", "")
    if "ARRANGEMENT OF ARTICLES" in sched[:3000]:   # e.g. the Constitution, scheduled to Cap. 1:01
        stoc, arts, _ = _split(sched)
        for e in stoc:
            toc.append(TocEntry(title=e.title, level=e.level + 1, provision=f"Art. {e.provision}" if e.provision else ""))
        sections.update({f"Art. {k}": v for k, v in arts.items() if k != "Schedule"})
    rev = re.search(r"\bL\.R\.O\. \d+/\d{4}\b", raw[:500])
    act = re.search(r"\bAct\s*\n?\s*(\d+ of \d{4})", raw[:800])
    meta = {k: v for k, v in (("Chapter", f"Cap. {lid}"), ("Volume", card["volume"]),
                              ("Original Act", act[1] if act else ""), ("Revision", rev[0] if rev else ""),
                              ("PDF", card["pdf"])) if v}
    law = {"id": lid, "title": f"{card['title']}, Cap. {lid}", "url": card["pdf"], "toc": toc,
           "sections": sections, "text": full, "meta": meta}
    return _http.lru_put(_laws, lid, law, 8)


# --------------------------------------------------------------------------- #
class Guyana(Jurisdiction):
    code = "gy"
    name = "Guyana"
    languages = ("en",)
    aliases = ("guyana", "co-operative republic of guyana", "cooperative republic of guyana", "guy")
    sources = (
        Source(
            name="Laws of Guyana, Ministry of Legal Affairs (mola.gov.gy)",
            url=LIST_URL,
            covers=("legislation",),
            licence=("'Copyright @ Ministry of Legal Affairs. All rights reserved' (site footer); no terms of "
                     "use or licence page (checked 2026-11-05)"),
            commercial_use=None,
            ai_use=None,   # robots.txt: "User-agent: * / Disallow:" (allows all); no AI/TDM clause
            auth="none",
            rate_limit="unknown; no Crawl-delay; 1 s spacing, no 429 in ~15 requests (2026-11)",
            terms_url=f"{BASE}/",
        ),
        _ccj.CCJ.sources[0],
    )
    caselaw_filters = {
        "date_from": "delivered on or after YYYY-MM-DD",
        "date_to": "delivered on or before YYYY-MM-DD",
    }
    min_interval = {HOST: 1.0, _ccj.HOST: 1.0}
    notes = ("Laws of Guyana, Revised Edition (L.R.O. 1/2022, in force at 31 Dec 2022), one PDF per chapter "
             "from the Ministry of Legal Affairs; title search only. Case law: Caribbean Court of Justice "
             "appeals from Guyana (final court; via the `ccj` adapter; country from the CCJ list or the "
             "judgment PDF). The Supreme Court of Judicature does not publish judgments online.")
    gaps = (
        "Supreme Court of Judicature case law (Court of Appeal, High Court): not published online (2026-11)",
        "Acts after the L.R.O. 1/2022 revision (in force at 31 Dec 2022): parliament.gov.gy Act PDFs "
        "are scans without a text layer (no OCR) and its list stops at June 2025",
    )
    samples = {
        "legislation_query": "Criminal Law",
        "law_id": "8:01",               # Criminal Law (Offences) Act, Cap. 8:01
        "provision": "100",             # Murder
        "caselaw_query": "Attorney General of Guyana",
        "decision_id": "[2019] CCJ 13 (AJ)",   # Mustapha v Attorney General of Guyana
    }

    # ------------------------------------------------------------------ #
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        f = filters or {}
        res = await ccj_appeals("GY", query, limit=limit, page=page,
                                date_from=f.get("date_from", ""), date_to=f.get("date_to", ""))
        if not res.items and _http.clean(query or ""):
            res.note = ((res.note or "") + " Topic search is not supported: the CCJ list has no judgment "
                        "text or subject field, so a subject word such as 'negligence' finds only a party "
                        "name that contains it. Court of Appeal and High Court judgments are not published online, so a zero "
                        "is not proof that no Guyanese court has discussed the topic. To screen by topic, search with an empty query (optionally "
                        "with date_from/date_to) to list the Guyanese appeals newest first, then open the "
                        "likely ones with get_decision; or search the party names if you know them.").strip()
        return res

    async def get_decision(self, id):
        key = _ccj._key((id or "").partition("#")[0])
        row = (await _ccj._rows()).get(key) if key else None
        if row is not None:
            code = _bb._listed_origin(row) or _bb._origin.get(row["key"])
            if code is None:
                code = await _bb._pdf_origin(row)
            if row["jur"] != "AJ" or (code is not None and code != "GY"):
                raise NotFound(f"{_ccj._cite(key)} is not an appeal from Guyana; open it with the ccj adapter.")
        return await _ccj.CCJ().get_decision(id)

    # ------------------------------------------------------------------ #
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        q = _http.clean(query or "")
        m = _CAP.match(q)
        if m:                           # a chapter number: search as the site prints it
            q = f"{int(m[1]):03d}:{int(m[2]):02d}"
        limit = max(1, min(int(limit), 27))
        start = (max(1, int(page)) - 1) * limit
        end = start + limit
        items: list[LawHit] = []
        sp = start // SITE_PAGE + 1
        last = 0
        while True:
            cards, last = await _search(q, sp)
            base = (sp - 1) * SITE_PAGE
            items += [LawHit(id=c["id"], title=c["title"], type="Act (Revised Edition chapter)",
                             number=f"Cap. {c['id']}", status="in force at 31 Dec 2022 (L.R.O. 1/2022)",
                             snippet=c["volume"], url=c["pdf"])
                      for i, c in enumerate(cards, base) if start <= i < end]
            if not cards or sp >= last or sp * SITE_PAGE >= end:
                break
            sp += 1
        total = len(items) + start if last <= 1 else None
        note = ("Title search over the Laws of Guyana chapter list (Revised Edition 2022, the site's own search)."
                " Only the chapters of that revision (L.R.O. 1/2022) are listed. Acts passed after it (31 Dec 2022), and any Act the"
                " revision does not carry as a chapter (the Cybercrime Act 2018, Act No. 16 of 2018, is not in this"
                " list), are not covered here: check parliament.gov.gy."
                + (f" About {last} site pages of 9 results." if last > 1 else ""))
        return Results(items=items[:limit], total=total, note=note)

    async def get_legislation_toc(self, id):
        law = await _law(id)
        entries = law["toc"] or [TocEntry(title="(no Arrangement of Sections found; use get_legislation_text)")]
        return Toc(id=law["id"], title=law["title"], url=law["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        law = await _law(id)
        label = _norm_prov(provision)
        if label not in law["sections"]:
            if not law["sections"]:
                raise NotFound(f"{law['title']}: sections could not be separated in this PDF; "
                               "use get_legislation_text.")
            raise NotFound(f"{law['title']} has no section '{provision}'. Use get_legislation_toc for the labels.")
        return Provision(law_id=law["id"], law_title=law["title"], provision=label,
                         text=law["sections"][label], url=law["url"], as_of="2022-12-31")

    async def get_legislation_text(self, id):
        law = await _law(id)
        return LawText(id=law["id"], title=law["title"], text=law["text"], url=law["url"],
                       as_of="2022-12-31", metadata=law["meta"])
