"""Belize: judgments of the Senior Courts (Belize Judiciary website) and the Laws of Belize
(Attorney General's Ministry).

Case law (www.belizejudiciary.org, WordPress):
  * Judgments are a "judgment" post type with the full text as HTML in the post body (about
    1,500 in 2026-11: High Court / former Supreme Court, Court of Appeal, Privy Council
    appeals from Belize). The WordPress REST search (/wp/v2/judgment?search=) returns nothing,
    so full-text search goes through the site's own Relevanssi endpoint
    /wp-json/relevanssi/v1/search (keyword, type=judgment, per_page, page; X-WP-Total).
    An empty query lists the newest judgments from /wp/v2/judgment.
  * The site's own front end searches through a third-party developer host
    (m.belize.demetriuscharles.com); not official, not used.
  * Id: the WordPress post id ("7614"); the judgment's page URL or slug also works.

Final appeals (court filter):
  * court=ccj: the Caribbean Court of Justice, Belize's final court since 2010, read through the
    `ccj` adapter and kept to appeals from Belize (bb.ccj_appeals: country from the CCJ list, else
    from page 1 of the judgment PDF).
  * court=jcpc: the Judicial Committee of the Privy Council (final court before 2010), read through
    the `gb` adapter's Find Case Law search (court=ukpc, the word "Belize", and "Belize" in the
    case title, which Find Case Law ends with "(Belize)"). Find Case Law has UKPC judgments from
    Nov 2009 only; older Privy Council appeals are on BAILII (forbids scraping), except the few
    the Judiciary site hosts (found by the default search).
  * get_decision takes a CCJ citation ("[2019] CCJ 15 (AJ)") or a UKPC one ("[2011] UKPC 23").

Legislation (agm.gov.bz):
  * The Laws of Belize pages: Substantive and Subsidiary Laws (Revised Edition 2020, by
    chapter), Acts and Statutory Instruments since 2020/2021, as text-layer PDFs under
    /uploads/laws/<13-hex upload id>_<name>.pdf.
  * Search is the site's own form (POST /laws, action=1004): ranked, at most 10 hits, no paging.
  * Id: the PDF file name ("639762f72be2e_Cap_101_Criminal_Code_Act.pdf"). "Cap 101"
    (substantive chapter) and "Cap 101s" (its subsidiary laws) also work and resolve
    through the site search. A bad id is refused by format; a HEAD request checks the file
    is a PDF under MAX_PDF before download.
"""
from __future__ import annotations

import html as htmllib
import re
from urllib.parse import quote

from lxml import html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc, TocEntry
from . import ccj as _ccj
from .bb import ccj_appeals
from .gb import UnitedKingdom

JUD_HOST = "www.belizejudiciary.org"
AGM_HOST = "agm.gov.bz"
JUD = f"https://{JUD_HOST}"
WP = f"{JUD}/wp-json/wp/v2/judgment"
RELEVANSSI = f"{JUD}/wp-json/relevanssi/v1/search"
AGM = f"https://{AGM_HOST}"
PDF_BASE = f"{AGM}/uploads/laws/"
MAX_PDF = 40_000_000
_HIT_FIELDS = "id,date,title,link,slug,categories,excerpt"
_DEC_ID = re.compile(r"^\d{1,7}$")
_SLUG = re.compile(r"^(?:https?://(?:www\.)?belizejudiciary\.org)?/?(?:judgment/)?([a-z0-9][a-z0-9-]{2,200})/?$",
                   re.I)
_PDF_ID = re.compile(r"^(?:https?://(?:www\.)?agm\.gov\.bz)?/?(?:uploads/laws/)?"
                     r"([0-9a-f]{13}_[A-Za-z0-9._()-]{1,200}\.pdf)$", re.I)
_CAP_ID = re.compile(r"^cap(?:ter|\.)?\s*(\d{1,3}(?:\.\d{1,2})?)(s?)$", re.I)

# WordPress categories -> court (site labels; checked in this order)
_CATS = (({322, 588, 590, 596}, "Judicial Committee of the Privy Council (appeal from Belize)"),
         ({586, 587}, "High Court of Belize (inferior appeal)"),
         ({4, 161, 585}, "Court of Appeal of Belize"),
         ({5, 56, 57}, "High Court of Belize"))

_laws: dict = {}
_AMENDED = ("Revised Edition 2020 text. Acts passed after 2020 that amend it are separate PDFs and are NOT "
            "applied here; search_legislation '<law name> Amendment' to check for later changes.")


def _court_from_cats(cats) -> str:
    cats = set(cats or ())
    return next((name for ids, name in _CATS if cats & ids), "")


def _court_from_title(title: str) -> str:
    """Court from the case title; the site's categories are often wrong (High Court claims
    filed under Court of Appeal), so they are only a fallback."""
    t = title.lower()
    if "privy council" in t or "ukpc" in t:
        return _CATS[0][1]
    if re.search(r"\b(civil|criminal) appeal|court of appeal|\bcriminal application|\bcivil application", t):
        return "Court of Appeal of Belize"
    if re.search(r"\b(high court|claim|indictment|action|divorce|petition|inferior appeal|"
                 r"probate|adoption|fixed date)\b", t):
        return "High Court of Belize"
    return ""


def _court_from_text(text: str) -> str:
    head = text[:1500].upper()
    if "PRIVY COUNCIL" in head or "UKPC" in head:
        return _CATS[0][1]
    if "COURT OF APPEAL OF BELIZE" in head[:400] or "IN THE COURT OF APPEAL" in head:
        return "Court of Appeal of Belize"
    if "HIGH COURT" in head:
        return "High Court of Belize"
    if "SUPREME COURT OF BELIZE" in head:
        return "Supreme Court of Belize (now the High Court)"
    return ""


def _case_number(title: str) -> str:
    m = re.match(r"^(.{0,80}?\bNos?\.?\s*[A-Z]?\d[\w./]*(?:\s*(?:and|&|,)\s*\d[\w./]*)*"
                 r"(?:\s+of\s*\d{4})?)", title, re.I)
    return _http.clean(m[1]) if m else ""


def _title(post: dict) -> str:
    return _http.clean(htmllib.unescape(re.sub(r"<[^>]+>", "", post.get("title", {}).get("rendered", ""))))


def _snippet(excerpt_html: str) -> str:
    s = _http.clean(htmllib.unescape(re.sub(r"<[^>]+>", " ", excerpt_html or "")))
    s = re.sub(r"\s*\(Search hits:.*$", "", s)
    return s[:400]


def _hit(post: dict, with_date: bool = False) -> DecisionHit:
    title = _title(post)
    snip = _snippet(post.get("excerpt", {}).get("rendered", ""))
    if with_date and post.get("date"):
        snip = f"[Posted on site: {post['date'][:10]}] {snip}".strip()
    court = _court_from_title(title) or _court_from_cats(post.get("categories"))
    return DecisionHit(id=str(post["id"]), title=title, court=court, date="", case_number=_case_number(title),
                       snippet=snip,
                       url=post.get("link") or f"{JUD}/?p={post['id']}")


async def _json(url: str, params: dict, who: str):
    r = await _http.get(url, params=params)
    if r.status_code == 404:
        raise NotFound(f"{who}: not found.")
    if r.status_code != 200 or "json" not in r.headers.get("content-type", ""):
        raise SourceError(_http.error(who, url, r.status_code), r.status_code)
    return r


# --------------------------------------------------------------------------- #
# Privy Council appeals from Belize (Find Case Law, through the gb adapter)
# --------------------------------------------------------------------------- #
_FINAL = {"ccj": "ccj", "caribbean court of justice": "ccj",
          "jcpc": "jcpc", "ukpc": "jcpc", "privy council": "jcpc"}
_BELIZE = re.compile(r"\bBelize(an)?\b", re.I)


async def _jcpc(query: str, *, limit: int, page: int) -> Results:
    gb = UnitedKingdom()
    hits, p = [], 1
    while p <= 5:
        r = await gb.search_caselaw(f"Belize {query}".strip(), limit=50, page=p, filters={"court": "ukpc"})
        hits += [h for h in r.items if _BELIZE.search(h.title)]
        if len(r.items) < 50:
            break
        p += 1
    limit, page = max(1, min(int(limit), 50)), max(1, int(page))
    return Results(items=hits[(page - 1) * limit: page * limit], total=len(hits),
                   note=("Privy Council judgments on appeal from Belize on Find Case Law (Nov 2009 on), "
                         "newest first; all words must match the judgment text. Older ones: BAILII (not "
                         "reachable here) or the default search of the Judiciary site."))


# --------------------------------------------------------------------------- #
# Laws of Belize (agm.gov.bz)
# --------------------------------------------------------------------------- #
def _law_kind(title: str) -> tuple[str, str]:
    """(type, number) from a listing title."""
    m = re.match(r"(?i)^cap\.?\s*(\d+(?:\.\d+)?)(s?)\b", title)
    if m:
        num = f"Cap. {int(float(m[1])) if '.' not in m[1] else m[1]}"
        return ("Subsidiary Laws (R.E. 2020)", num) if m[2] else ("Substantive Law (R.E. 2020)", num)
    m = re.match(r"(?i)^(Act|SI)\s+No\.?\s*(\d+)\s+(?:of\s+)?(\d{4})", title)
    if m:
        kind = "Act" if m[1].lower() == "act" else "Statutory Instrument"
        return kind, f"{m[1].upper() if m[1].lower() == 'si' else 'Act'} No. {int(m[2])} of {m[3]}"
    return "", ""


async def _agm_search(query: str) -> list[tuple[str, str]]:
    """The site's own search: [(file name, title)], at most 10, ranked by the site."""
    r = await _http.post(f"{AGM}/laws", data={"action": "1004", "doc-search-input": query})
    if r.status_code != 200:
        raise SourceError(_http.error(AGM_HOST, "law search failed", r.status_code), r.status_code)
    doc = lhtml.fromstring(r.text)
    out = []
    for a in doc.xpath('//table[@id="documents-search"]//a[@href]'):
        m = _PDF_ID.match(a.get("href", ""))
        if m:
            out.append((m[1], _http.clean(a.text_content())))
    return out


_PAGE_JUNK = re.compile(
    r"^(?:\[\s*\]|.*\[CAP\.\s*\d+[\w.]*\s+\d+|\d+\s+\[CAP\.\s*\d+[\w.]*\s.*|"
    r"THE (?:SUBSTANTIVE|SUBSIDIARY) LAWS OF BELIZE REVISED EDITION \d{4}|"
    r"Printed by Authority of the|Government of Belize)$")
_SEC = re.compile(r"^(\d+[A-Z]{0,2})\.\s*(\S.*)$")
_SCHED = re.compile(r"^((?:FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH|SEVENTH|EIGHTH|NINTH|TENTH)\s+)?SCHEDULE\b.*$")


_RULE_TOC = re.compile(r"^(.*?)\s*[.\u2026]{2,}\s*Rule\s+(\d+\.\d+)\s*$")
_RULE_JUNK = re.compile(r"^(?:Senior Courts \d+|\[No\. \d+.*|TABLE OF CONTENTS)$")


def _split_rules(full: str) -> tuple[list[TocEntry], dict[str, str]]:
    """Court rules (Senior Courts Civil Procedure Rules 2025): the Part tables of contents list
    'Title....Rule 10.5' and the body starts each rule '10.5-(1)'. Returns (toc, {rule: text})."""
    lines = [ln.strip() for ln in full.splitlines() if ln.strip()]
    titles: dict[str, str] = {}
    buf: list[str] = []
    skip = False
    for ln in lines:
        if skip:                     # the Part's own title line
            skip = False
            continue
        m = _RULE_TOC.match(ln)
        if m:
            titles.setdefault(m[2], _http.clean(" ".join(buf + [m[1]])))
            buf = []
        elif re.match(r"^PART \d+$", ln) or ln.isupper() or _RULE_JUNK.match(ln):
            buf = []
            skip = bool(re.match(r"^PART \d+$", ln))
        elif len(ln) < 90 and ln[-1:] not in ".;:,":
            buf.append(ln)
        else:
            buf = []
    if len(titles) < 5:
        return [], {}
    pos: list[tuple[str, int]] = []
    k = 0
    for lab in titles:
        for i in range(k, len(lines) if not pos else min(k + 400, len(lines))):
            if re.match(rf"^{re.escape(lab)}(?:\s*[\u2013\u2014-]|\s|$)", lines[i]):
                pos.append((lab, i))
                k = i + 1
                break
    if len(pos) < 5:
        return [], {}
    parts = [i for i, ln in enumerate(lines) if re.match(r"^PART \d+$", ln)]
    texts: dict[str, str] = {}
    toc: list[TocEntry] = []
    last_part = None
    for n, (lab, i) in enumerate(pos):
        end = pos[n + 1][1] if n + 1 < len(pos) else len(lines)
        stop = next((x for x in parts if x > i), len(lines))
        chunk = [ln for ln in lines[i:min(end, stop)] if not _RULE_JUNK.match(ln)]
        texts[lab] = "\n".join(chunk)
        part = max((x for x in parts if i - 200 < x < i and lines[x] == f"PART {lab.split('.')[0]}"),
                   default=None)
        if part is not None and part != last_part:
            last_part = part
            toc.append(TocEntry(title=f"{lines[part]} \u2013 {lines[part + 1]}".strip(), level=0))
        toc.append(TocEntry(title=f"{lab}. {titles[lab]}".strip(), level=1, provision=lab))
    return toc, texts


def _split(text: str) -> tuple[list[TocEntry], dict[str, str], str]:
    toc, texts, full = _split_sections(text)
    if not toc:
        toc, texts = _split_rules(full)
    return toc, texts, full


def _split_sections(text: str) -> tuple[list[TocEntry], dict[str, str], str]:
    """Cut a Revised Edition PDF into sections using its Arrangement of Sections (after
    bs.py/tt.py). Body sections start '12.' or '12.-(1)'. Returns (toc, {label: text}, full)."""
    lines = [ln for ln in text.splitlines() if not _PAGE_JUNK.match(ln.strip())]
    full = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
    flat = [ln.strip() for ln in lines if ln.strip()]
    start = next((i for i, ln in enumerate(flat)
                  if re.match(r"^ARRANGEMENT OF (SECTIONS|ARTICLES|REGULATIONS|RULES|PARAGRAPHS)\b", ln.upper())),
                 None)
    arrangement: list[tuple[str, str]] = []
    headings: dict[str, list[str]] = {}
    body_at = None
    if start is not None:
        pending: list[str] = []
        seen = set()
        after_part = after_sec = False
        for i in range(start + 1, len(flat)):
            ln = flat[i]
            m = _SEC.match(ln)
            if m and not m[2].startswith(("-", "–")):
                if m[1] in seen:            # numbering restarts: a numbered sub-title or the body
                    nxt = next((_SEC.match(x) for x in flat[i + 1:i + 40] if _SEC.match(x)), None)
                    if nxt and int(re.match(r"\d+", nxt[1])[0]) > int(re.match(r"\d+", arrangement[-1][0])[0]):
                        pending.append(ln)   # "2. Rescue, Escape ..." sub-title; the list goes on
                        after_sec = False
                        continue
                    body_at = i
                    break
                seen.add(m[1])
                arrangement.append((m[1], m[2]))
                if pending:
                    headings[m[1]] = pending
                    pending = []
                after_part, after_sec = False, True
                continue
            elif m:                          # "1.-(1)" can only be the body
                body_at = i
                break
            elif re.match(r"^(PART|CHAPTER|TITLE)\s+[IVXLC\d]+\b", ln) and len(ln) < 90:
                if ln.startswith("CHAPTER") and not pending and arrangement:
                    continue                 # running "CHAPTER 1" title block on later pages
                pending.append(ln)
                after_part = True
            elif after_part and len(ln) < 90:
                pending[-1] = f"{pending[-1]} – {ln}"   # "PART I" then its title line
                after_part = False
            elif re.match(r"^(\d+ of \d{4}|S\.I\.|R\.E\.|\[|CAP)", ln) or ln.isupper():
                pass
            elif after_sec and not arrangement[-1][1].endswith("."):
                lab, t = arrangement[-1]     # wrapped heading line
                arrangement[-1] = (lab, f"{t} {ln}")
                continue
            elif len(ln) < 90 and arrangement:
                pending.append(ln)           # mixed-case sub-heading ("Standard Tests for ...")
            after_sec = False
    if not arrangement or body_at is None:
        return [], {}, full
    # the body restarts at the first section label; step back to its PART heading
    body = flat[body_at:]
    labels = [lab for lab, _ in arrangement]
    pos: list[tuple[str, int]] = []
    k = 0
    for i, s in enumerate(body):
        for j in range(k, min(k + 4, len(labels))):
            if re.match(rf"^{re.escape(labels[j])}\.(\s|-|–|$)", s):
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
        end = pos[n + 1][1] if n + 1 < len(pos) else (sched_at or len(body))
        chunk = body[i:end]
        while len(chunk) > 1 and re.match(r"^(PART|CHAPTER)\b|^[A-Z][a-z]+(?: [a-z]+)*$", chunk[-1]) \
                and len(chunk[-1]) < 60 and not chunk[-1].endswith((".", ";", ",")):
            chunk = chunk[:-1]               # the next section's Part heading / title
        texts[lab] = "\n".join(chunk)
    if sched_at is not None:
        texts["Schedule"] = "\n".join(body[sched_at:])
    toc = []
    titles = dict(arrangement)
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
    s = re.sub(r"(?i)^(section|sec\.?|s\.|s|art\.?|article|reg\.?|regulation|rule|r\.)\s*", "", s).strip().rstrip(".")
    m = re.match(r"^(\d+(?:\.\d+)?[A-Za-z]{0,2})(?:\s*\(.*)?$", s)
    return m[1].upper() if m else s


async def _resolve(id: str) -> tuple[str, str]:
    """(PDF file name, title) for a law id."""
    lid = _http.clean(id)
    m = _PDF_ID.match(lid)
    if m:
        name = m[1]
        stem = re.sub(r"^[0-9a-f]{13}_|\.pdf$", "", name, flags=re.I)
        return name, _http.clean(stem.replace("_", " "))
    m = _CAP_ID.match(lid)
    if m:
        num, sub = m[1], m[2].lower()
        want = re.compile(rf"(?i)^cap\.?\s*0*{re.escape(num)}{sub}\s")
        for name, title in await _agm_search(f"Cap {num}{sub}"):
            if want.match(title):
                return name, title
        raise NotFound(f"No 'Cap {num}{sub}' on the Laws of Belize search. Use search_legislation.")
    raise BadRequest("Use a law id from search_legislation (a PDF file name such as "
                     "'639762f72be2e_Cap_101_Criminal_Code_Act.pdf'), or a chapter: 'Cap 101' "
                     "(substantive law) / 'Cap 101s' (its subsidiary laws).")


async def _law(id: str) -> dict:
    name, title = await _resolve(id)
    if name in _laws:
        return _laws[name]
    url = PDF_BASE + quote(name)
    h = await _http.request("HEAD", url)
    if h.status_code == 404 or (h.status_code == 200 and "pdf" not in h.headers.get("content-type", "")):
        raise NotFound(f"No PDF '{name}' on agm.gov.bz (re-uploaded or wrong name). Use search_legislation.")
    if h.status_code != 200:
        raise SourceError(_http.error(AGM_HOST, f"PDF check failed: {url}", h.status_code), h.status_code)
    size = int(h.headers.get("content-length") or 0)
    if size > MAX_PDF:
        raise SourceError(f"Error ({AGM_HOST}): {url} is {size // 1_000_000} MB, over the "
                          f"{MAX_PDF // 1_000_000} MB limit; read it there.", "too-large")
    r = await _http.get(url)
    if r.status_code != 200 or not r.content.startswith(b"%PDF"):
        raise SourceError(_http.error(AGM_HOST, f"PDF failed: {url}", r.status_code), r.status_code)
    raw = _http.pdf_text(r.content)
    if len(raw) < 200:
        raise SourceError(f"Error ({AGM_HOST}): {url} has no text layer (scanned; no OCR here); read it there.",
                          "no-text")
    toc, sections, full = _split(raw)
    kind, number = _law_kind(title)
    asat = re.search(r"AS AT\s+(\d{1,2})(?:ST|ND|RD|TH)?\s+([A-Z]+),?\s+(\d{4})", raw[:1500], re.I)
    as_of = _http.en_date(f"{asat[2]} {asat[1]}, {asat[3]}") if asat else ""
    meta = {k: v for k, v in (("Type", kind), ("Number", number),
                              ("Revised Edition as at", as_of), ("PDF", url)) if v}
    if kind.endswith("(R.E. 2020)"):
        meta["Note"] = _AMENDED
    law = {"id": name, "title": title, "url": url, "toc": toc, "sections": sections, "text": full,
           "meta": meta, "as_of": as_of}
    return _http.lru_put(_laws, name, law, 8)


async def _later_amendments(law: dict, label: str) -> list[str]:
    """Amending Acts (2021-) whose sections name this section of an R.E. 2020 law (best effort)."""
    title = re.sub(r"(?i)^cap\.?\s*\d+(?:\.\d+)?\s+|\s+act$", "", law["title"]).strip()
    words = re.findall(r"\w+", title.lower())
    if not words or not label[:1].isdigit():
        return []
    want = re.compile(rf"(?is)^\S+\s+(?:\(\d+\)\s*)?The principal Act is [^.]{{0,100}}?\bsection\s+{re.escape(label)}\b")
    out = []
    try:
        for name, t in (await _agm_search(f"{title} Amendment"))[:10]:
            if _law_kind(t)[0] != "Act" or "amendment" not in t.lower() or not all(w in t.lower() for w in words):
                continue
            amd = await _law(name)
            for lab, txt in amd["sections"].items():
                if want.search(txt):
                    out.append(f"{_law_kind(t)[1]} ({t}), s. {lab}: {_http.clean(txt)}")
    except (SourceError, NotFound, BadRequest):
        return out
    return out


# --------------------------------------------------------------------------- #
class Belize(Jurisdiction):
    code = "bz"
    name = "Belize"
    languages = ("en",)
    aliases = ("belize", "blz", "british honduras")
    sources = (
        Source(
            name="Judgments of the Senior Courts of Belize, Belize Judiciary (belizejudiciary.org)",
            url=f"{JUD}/",
            covers=("caselaw",),
            licence=("'© 2024 Belize Supreme Court Judiciary' footer; no licence or terms-of-use page "
                     "(checked 2026-11-06)"),
            commercial_use=None,
            ai_use=None,    # no robots.txt (404); no AI/TDM clause anywhere on the site
            auth="none",
            rate_limit=("unknown; no robots.txt, no Crawl-delay; 1 s spacing, no 429 in ~25 requests "
                        "(2026-11)"),
            terms_url=f"{JUD}/",
        ),
        Source(
            name="Laws of Belize, Attorney General's Ministry (agm.gov.bz)",
            url=f"{AGM}/laws/law_substantive",
            covers=("legislation",),
            licence=("'© 2022 By The Attorney General's Ministry of Belize - All Rights Reserved' footer; "
                     "no terms-of-use page (checked 2026-11-06)"),
            commercial_use=None,
            ai_use=None,    # /robots.txt is not a robots file (serves the home page); no AI/TDM clause
            auth="none",
            rate_limit=("unknown; no robots.txt, no Crawl-delay; 1 s spacing, no 429 in ~25 requests "
                        "(2026-11)"),
            terms_url=f"{AGM}/",
        ),
        _ccj.CCJ.sources[0],               # court=ccj, through the ccj adapter
        UnitedKingdom.sources[0],          # court=jcpc: Find Case Law (UKPC), through the gb adapter
    )
    caselaw_filters = {
        "court": ("ccj (Caribbean Court of Justice: final appeals from Belize, 2010-) or jcpc (Privy "
                  "Council appeals from Belize on Find Case Law, Nov 2009-); default: the Belize "
                  "Judiciary site (High Court, Court of Appeal, some Privy Council)"),
        "date_from": "court=ccj only: delivered on or after YYYY-MM-DD (Judiciary site: no dates searchable)",
        "date_to": "court=ccj only: delivered on or before YYYY-MM-DD",
    }
    min_interval = {JUD_HOST: 1.0, AGM_HOST: 1.0, _ccj.HOST: 1.0, "caselaw.nationalarchives.gov.uk": 0.3}
    notes = ("Full-text judgments (High Court / former Supreme Court, Court of Appeal, Privy Council "
             "appeals; mostly 2000-) from the Belize Judiciary site; final appeals with court=ccj (Caribbean "
             "Court of Justice, 2010-) or court=jcpc (Privy Council, Find Case Law 2009-). Laws of "
             "Belize Revised Edition 2020 plus Acts and SIs since 2020 as PDFs from the Attorney "
             "General's Ministry (site search: 10 hits max).")
    gaps = (
        "Full-text legislation search: the AGM site search returns at most 10 hits, no paging",
        "Magistrates' courts and tribunals: not researched yet",
        "Laws before the 2020 Revised Edition and historical versions: not researched yet",
        ("CCJ appeals (court=ccj): matched on citation and parties only, not judgment text (the CCJ"
         " lists have no full-text search)"),
        ("Privy Council appeals from Belize before Nov 2009: not on Find Case Law; BAILII forbids "
         "scraping; only the few the Judiciary site hosts"),
    )
    samples = {
        "caselaw_query": "manslaughter",
        "decision_id": "7614",            # Indictment No 21 of 2024, The King v Editor Noh (High Court)
        "legislation_query": "Criminal Code",
        "law_id": "Cap 101",              # Criminal Code, Cap. 101 (R.E. 2020)
        "provision": "106",
    }

    # ------------------------------------------------------------------ #
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        q = _http.clean(query or "")
        f = {k: _http.clean(v) for k, v in (filters or {}).items() if _http.clean(v)}
        court = f.get("court", "").lower()
        if court and court not in _FINAL:
            raise BadRequest("court must be ccj (Caribbean Court of Justice) or jcpc (Privy Council); "
                             "leave it out for the Belize Judiciary site.")
        for d in (f.get("date_from", ""), f.get("date_to", "")):
            if d and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
                raise BadRequest("date_from / date_to must be YYYY-MM-DD.")
        if (f.get("date_from") or f.get("date_to")) and _FINAL.get(court) != "ccj":
            raise BadRequest("date_from / date_to work with court=ccj only: the Belize Judiciary site cannot "
                             "filter by date. Its hits show only the date a judgment was posted on the site, "
                             "which can be years after the decision (read the judgment for its date), so "
                             "do not treat it as the decision date.")
        if _FINAL.get(court) == "ccj":
            return await ccj_appeals("BZ", q, limit=limit, page=page,
                                     date_from=f.get("date_from", ""), date_to=f.get("date_to", ""))
        if _FINAL.get(court) == "jcpc":
            return await _jcpc(q, limit=limit, page=page)
        limit = max(1, min(int(limit), 50))
        page = max(1, int(page))
        if q:
            r = await _json(RELEVANSSI, {"keyword": q, "type": "judgment", "per_page": limit, "page": page,
                                         "_fields": _HIT_FIELDS}, JUD_HOST)
            note = ("Full-text search (site's Relevanssi index), ranked by relevance. Court in hits is read from "
                    "the case title; get_decision reads it from the judgment heading. No decision dates "
                    "in the source's metadata; hits show the date the judgment was posted on the site.")
        else:
            r = await _json(WP, {"per_page": limit, "page": page, "_fields": _HIT_FIELDS}, JUD_HOST)
            note = "No query: newest judgments posted on the site."
        data = r.json()
        if not isinstance(data, list):           # Relevanssi returns an object when nothing matches
            data = []
        total = r.headers.get("x-wp-total")
        return Results(items=[_hit(p, with_date=True) for p in data], total=int(total) if total and total.isdigit() else None,
                       note=note)

    async def get_decision(self, id):
        ident = _http.clean(id)
        if re.search(r"(?i)\bCCJ\b", ident):
            return await _ccj.CCJ().get_decision(ident)
        if re.search(r"(?i)\bUKPC\b", ident):
            return await UnitedKingdom().get_decision(ident)
        fields = "id,date,title,link,slug,categories,content"
        if _DEC_ID.match(ident):
            try:
                r = await _json(f"{WP}/{ident}", {"_fields": fields}, JUD_HOST)
            except NotFound:
                raise NotFound(f"No judgment with id {ident} on belizejudiciary.org.") from None
            post = r.json()
        else:
            m = _SLUG.match(ident)
            if not m:
                raise BadRequest("Give a judgment id from search_caselaw (e.g. '7614'), its "
                                 "belizejudiciary.org/judgment/<slug>/ URL, or a CCJ / UKPC citation "
                                 "('[2019] CCJ 15 (AJ)', '[2011] UKPC 23').")
            r = await _json(WP, {"slug": m[1].lower(), "_fields": fields}, JUD_HOST)
            posts = r.json()
            if not posts:
                raise NotFound(f"No judgment with slug '{m[1]}' on belizejudiciary.org.")
            post = posts[0]
        if not isinstance(post, dict) or "content" not in post:
            raise SourceError(_http.error(JUD_HOST, "unexpected judgment payload", r.status_code), "payload")
        text = _http.html_to_md(post["content"].get("rendered", ""))
        title = _title(post)
        court = _court_from_text(text) or _court_from_cats(post.get("categories"))
        meta = {"Posted on site (NOT the decision date)": post.get("date", "")[:10]}
        meta["Decision date"] = "not in the source's metadata; read it from the judgment text (heading or last page)"
        return Decision(id=str(post["id"]), title=title, text=text, url=post.get("link", ""), court=court,
                        date="", case_number=_case_number(title), metadata=meta)

    # ------------------------------------------------------------------ #
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        q = _http.clean(query or "")
        if not q:
            raise BadRequest("Give search words (title words or a chapter like 'Cap 101').")
        limit = max(1, min(int(limit), 50))
        page = max(1, int(page))
        rows = await _agm_search(q) if page == 1 or limit < 10 else []
        have = {m[1] for _, t in rows if (m := re.match(r"(?i)^cap\.?\s*0*(\d+(?:\.\d+)?)\s", t))}
        for _, t in rows[:]:     # the site often lists only a law's subsidiary laws; add the Act itself
            m = re.match(r"(?i)^cap\.?\s*0*(\d+(?:\.\d+)?)s\s", t)
            if m and m[1] not in have:
                have.add(m[1])
                rows += [(n, t2) for n, t2 in await _agm_search(f"Cap {m[1]}")
                         if re.match(rf"(?i)^cap\.?\s*0*{re.escape(m[1])}\s", t2) and (n, t2) not in rows]
        words = re.findall(r"\w+", q.lower())
        def rank(r):
            tw = re.findall(r"\w+", r[1].lower())
            hit = sum(w in tw for w in words)
            return (-hit, bool(re.match(r"(?i)^cap\.?\s*\d+(?:\.\d+)?s\s", r[1])), len(tw) - hit)
        rows.sort(key=rank)
        start = (page - 1) * limit
        items = []
        for name, title in rows[start:start + limit]:
            kind, number = _law_kind(title)
            items.append(LawHit(id=name, title=title, type=kind, number=number,
                                url=PDF_BASE + quote(name)))
        return Results(items=items, total=None,
                       note=("Laws of Belize site search: ranked, at most 10 hits, no further pages. "
                             "Cap. N = Revised Edition 2020 chapter; 'Cap Ns' = its subsidiary laws; later "
                             "amending Acts are separate items."))

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
        text = law["sections"][label]
        if "Note" in law["meta"]:
            text += f"\n\n(Note: {law['meta']['Note']})"
            later = await _later_amendments(law, label)
            if later:
                text += ("\n\nLATER AMENDMENTS found in separate Acts (NOT merged into the text above; the "
                         "section as amended is the text above changed as they say; others may exist):\n- "
                         + "\n- ".join(later))
        return Provision(law_id=law["id"], law_title=law["title"], provision=label,
                         text=text, url=law["url"], as_of=law["as_of"])

    async def get_legislation_text(self, id):
        law = await _law(id)
        return LawText(id=law["id"], title=law["title"], text=law["text"], url=law["url"],
                       as_of=law["as_of"], metadata=law["meta"])
