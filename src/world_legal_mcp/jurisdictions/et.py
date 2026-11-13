"""Ethiopia: federal laws as published in the Federal Negarit Gazette, from the "Published laws"
library of the House of Peoples' Representatives (hopr.gov.et). Amharic and English.

How the source works (verified 2026-11-06, UK IP, honest User-Agent):

  * GET https://www.hopr.gov.et/Home/PublishedLaws with SearchQuery (substring of the Amharic title
    or description; law numbers like "1183" work, English words mostly don't), SelectedFolderId
    (1 directives, 2 regulations, 3 proclamations, 4 decisions) and PageNumber (1-based). 15 rows
    a page; "ከ 933 ሕጎች ውስጥ 15 ይታያሉ" gives the total. Each row has the title, a description and a
    link /Home/ViewFiles?path=/admin/Files/<file>.pdf. ~930 entries, 1995-2026.
  * The id is that file path after "/admin/Files/" (the site has no other identifier). The PDF is
    served at /admin/Files/<file>; the ViewFiles page wraps it in an iframe whose title is the
    law's title. Some older rows point at a Windows path ("C:\\inetpub\\...") that 404s, and a few
    rows link to the wrong PDF (e.g. a row titled 263/1995 links to Proc. 152/1999): the library
    is maintained by hand.
  * The PDFs are Negarit Gazette issues with a text layer, two columns: Amharic left, English
    right. pypdf yields each page's Amharic column, then its English column, so lines are split by
    script into an English and an Amharic stream. Article headings are "12. Title" (English) and
    "፲፪. ርዕስ" (Amharic, Ethiopic numerals). Law numbers carry the Ethiopian-calendar year in the
    titles ("1183/2012") and the Gregorian year in the English text ("1183/2020").

Terms and robots.txt (2026-11-06):
  * www.hopr.gov.et/robots.txt: 404 (no rules). The footer links "Terms of use" (/Home/Terms) and
    "Privacy statement", but the Terms page has no text (Amharic and English versions checked).
    Footer: "© Copyright House of People's Representatives of Ethiopia, 2026. All rights reserved."

Not used:
  * Federal Supreme Court (fsc.gov.et, cassation decisions): HTTPS connection fails; plain HTTP
    answers 404 for every path. No official case-law source reachable.
  * Ministry of Justice (moj.gov.et): TLS certificate expired; not fetched.
  * negaritgazeta.gov.et and hof.gov.et do not resolve; hofethiopia.gov.et does not connect.
  * abyssinialaw.com, metaappz.com, lawethiopia.com: private, non-official. WorldLII: behind a
    Cloudflare challenge. EthioLII: Peachjam/AfricanLII family (excluded).
"""
from __future__ import annotations

import re
from urllib.parse import quote, unquote, urlencode

from lxml import html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import LawHit, LawText, Provision, Results, Toc, TocEntry

HOST = "www.hopr.gov.et"
BASE = f"https://{HOST}"
LIST = BASE + "/Home/PublishedLaws"
VIEW = BASE + "/Home/ViewFiles?path="
FILES = "/admin/Files/"
NAME = "House of Peoples' Representatives"
PAGE = 15                        # fixed by the source
MAX_PDF = 40_000_000
FOLDERS = {"directive": "1", "regulation": "2", "proclamation": "3", "decision": "4"}
TYPES = (("አዋጅ", "Proclamation (አዋጅ)"), ("ደንብ", "Regulation (ደንብ)"),
         ("መመሪያ", "Directive (መመሪያ)"), ("ውሳኔ", "Decision (ውሳኔ)"))

_ETH = re.compile(r"[\u1200-\u137f]")
_LAT = re.compile(r"[A-Za-z]")
_ETH_DIGITS = {c: i for i, c in enumerate("፩፪፫፬፭፮፯፰፱", 1)}
_ETH_TENS = {c: 10 * i for i, c in enumerate("፲፳፴፵፶፷፸፹፺", 1)}
_EN_ART = re.compile(r"^(\d{1,3})\s*\.\s*([A-Z\"“].*)")
_AM_ART = re.compile(r"^([፩-፼]+)\s*\.?\s*([\u1200-\u135a\"“«].*)")
_EN_PART = re.compile(r"^(PART|CHAPTER|SECTION|SUB-SECTION)\b")
_AM_PART = re.compile(r"^(ክፍል|ምዕራፍ|ንዑስ ክፍል)\b")
_NEW_PARA = re.compile(r"^(\d{1,3}\s*/|\(?[a-z]\)|\([ivx]+\)|[፩-፼]+/|[ሀ-ፐ]\)|WHEREAS|NOW,? THEREFORE)")
_END = re.compile(r"[.;:።፤፡!?]$")
_JUNK = re.compile(r"Negarit\s*G|ነጋሪት\s*ጋዜጣ\s*ቁጥር|[¶¤ÈÃÇêœ‰Ø±¹þÜ]|^Unit Price$|^ÃNÇ")

_PUA = re.compile(r"[\ue000-\uf8ff\u200b-\u200f\ufeff]")

_NUMQ = re.compile(r"(\d{1,4})(?:\s*/\s*(\d{4}))?")
NUM_PAGES = 10                   # source pages read for a number search (150 rows)
NOT_HELD = ("Not in this library (searched 2026-11-12): the FDRE Constitution (1995), the Civil Code "
            "(1960), the Civil Procedure Code (Decree 52/1965), the Labour Proclamation (1156/2019 = 1156/2011 EC) "
            "and the Criminal Code (Proclamation 414/2004 = 414/1996 EC). A hit that amends a "
            "code (e.g. 141/1991 on the Criminal Code) is not the code itself.")

_cache: dict = {}


def eth_num(s: str) -> int:
    """Ethiopic numeral (below 10000) -> int: '፲፪' -> 12, '፩፻፹፫' -> 183."""
    total, cur = 0, 0
    for c in s:
        if c in _ETH_DIGITS:
            cur += _ETH_DIGITS[c]
        elif c in _ETH_TENS:
            cur += _ETH_TENS[c]
        elif c == "፻":
            total += (cur or 1) * 100
            cur = 0
        else:
            return -1
    return total + cur


def _split_streams(text: str) -> tuple[list[str], list[str]]:
    """pdf_text output -> (English lines, Amharic lines), running heads and page numbers dropped."""
    en, am = [], []
    for ln in text.split("\n"):
        ln = _PUA.sub("", ln).strip()        # Symbol-font bullets (U+F0B7) before headings
        if not ln or _JUNK.search(ln) or re.fullmatch(r"[\d\s.…]+|[፩-፼ሺ\s]+", ln):
            continue
        (am if len(_ETH.findall(ln)) > len(_LAT.findall(ln)) else en).append(ln)
    return en, am


def _paras(lines: list[str], art: re.Pattern, part: re.Pattern) -> list[str]:
    out: list[str] = []
    for ln in lines:
        starts = bool(art.match(ln) or part.match(ln) or _NEW_PARA.match(ln))
        if out and not starts and not _END.search(out[-1]) and not part.match(out[-1]):
            out[-1] = out[-1][:-1] + ln if out[-1].endswith("-") and ln[:1].islower() else out[-1] + " " + ln
        else:
            out.append(ln)
    return out


def _articles(paras: list[str], art: re.Pattern, num) -> list[tuple[int, int, str]]:
    """(paragraph index, article number, heading) for headings that number on in sequence (a jump
    of up to 3 is allowed, so one heading merged into a paragraph doesn't end the run)."""
    found, last = [], 0
    for i, p in enumerate(paras):
        m = art.match(p)
        if not m:
            continue
        n = num(m[1])
        if last < n <= last + 3:               # tolerate a heading lost to a bad text layer
            found.append((i, n, _http.clean(m[2])[:100]))
            last = n
    return found


def _parse(text: str) -> dict:
    en_l, am_l = _split_streams(text)
    en = _paras(en_l, _EN_ART, _EN_PART)
    am = _paras(am_l, _AM_ART, _AM_PART)
    return {"en": en, "am": am,
            "en_arts": _articles(en, _EN_ART, int),
            "am_arts": _articles(am, _AM_ART, eth_num)}


def _article_text(paras: list[str], arts: list, n: int, part: re.Pattern) -> str:
    for k, (i, num, _) in enumerate(arts):
        if num == n:
            end = arts[k + 1][0] if k + 1 < len(arts) else len(paras)
            body = paras[i:end]
            cut = next((k for k in range(1, len(body)) if part.match(body[k])), len(body))
            return "\n\n".join(body[:cut])         # stop at the next part's heading
    return ""


def _norm_id(id: str) -> str:
    s = (id or "").strip()
    if "ViewFiles?path=" in s:
        s = unquote(s.split("ViewFiles?path=", 1)[1])
    elif "/admin/Files/" in s and "%" in s:
        s = unquote(s)
    if "/admin/Files/" in s:
        s = s.split("/admin/Files/", 1)[1]
    s = s.lstrip("/")
    if not s.lower().endswith(".pdf") or ".." in s or len(s) > 400:
        raise BadRequest("A law id is the file path from search_legislation, e.g. "
                         "'2026/7/31/0b0e807b-b35e-4fed-8042-c768ecafdc04_1400.pdf' (a hopr.gov.et "
                         "ViewFiles link also works).")
    return s


def _view_url(lid: str) -> str:
    return VIEW + quote(FILES + lid, safe="")


async def _law(lid: str) -> dict:
    lid = _norm_id(lid)
    if lid in _cache:
        return _cache[lid]
    view = _view_url(lid)
    r = await _http.get(view)
    if r.status_code != 200:
        raise SourceError(_http.error(NAME, "law page failed", r.status_code), r.status_code)
    frame = lhtml.fromstring(r.text).xpath("//iframe/@title")
    title = _http.clean(frame[0].rsplit("|", 1)[0]) if frame else ""
    pdf = BASE + FILES + quote(lid)
    h = await _http.request("HEAD", pdf)
    if h.status_code == 404:
        raise NotFound(f"The hopr.gov.et library has no file at {pdf} (some older entries link to a "
                       f"missing file). Try another entry for the same law.")
    if h.status_code != 200:
        raise SourceError(_http.error(NAME, "PDF not available", h.status_code), h.status_code)
    size = int(h.headers.get("content-length") or 0)
    if size > MAX_PDF:
        raise SourceError(f"Error ({NAME}): PDF is {size // 1_000_000} MB, over the 40 MB cap. Open {view}.")
    r = await _http.get(pdf)
    if r.status_code != 200 or not r.content.startswith(b"%PDF") or len(r.content) > MAX_PDF:
        raise SourceError(_http.error(NAME, "PDF download failed", r.status_code), r.status_code)
    text = _http.pdf_text(r.content)
    if not text:
        raise SourceError(f"Error ({NAME}): the PDF has no text layer (scanned). Open {view}.")
    law = {"title": title or lid.rsplit("/", 1)[-1], "url": view, **_parse(text)}
    return _http.lru_put(_cache, lid, law, 16)


def _prov_num(p: str) -> int:
    s = _http.clean(p).strip(" .:")
    s = re.sub(r"(?i)^(article|art\.?|አንቀጽ|አንቀፅ)\s*", "", s).strip(" .:")
    if s.isascii() and s.isdigit():
        return int(s)
    n = eth_num(s) if s else -1
    if n > 0:
        return n
    raise BadRequest(f"Provision '{p}' not understood. Use an article number: '5', 'Article 5' or '፭'.")


def _collapse(hits):
    """The library sometimes lists one law twice (different PDFs); show it once and name the other copy."""
    seen: dict = {}
    out = []
    for h in hits:
        key = (h.number, re.sub(r"[\s\-]", "", h.title))
        if key in seen:
            k = seen[key]
            k.snippet = (k.snippet + f" [The library lists this proclamation twice with different PDFs and marks "
                         f"neither as official; this is the first listed. The other copy: {h.id}]").strip()
        else:
            seen[key] = h
            out.append(h)
    return out


class Ethiopia(Jurisdiction):
    code = "et"
    name = "Ethiopia"
    languages = ("am", "en")
    aliases = ("ethiopia", "eth", "ኢትዮጵያ")
    sources = (
        Source(
            name="House of Peoples' Representatives: published laws (Federal Negarit Gazeta PDFs, hopr.gov.et)",
            url=LIST,
            covers=("legislation",),
            licence="Terms of use page is empty; footer '© Copyright House of People's Representatives "
                    "of Ethiopia, 2026. All rights reserved.'",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~25 requests (2026-11)",
            terms_url=BASE + "/Home/Terms",
            warning="Negarit Gazeta issues as originally published (not consolidated); the library is "
                    "kept by hand and a few entries link to a missing or wrong PDF.",
        ),
    )
    legislation_filters = {"type": "proclamation, regulation, directive or decision"}
    min_interval = {HOST: 1.0}
    notes = ("Federal proclamations, regulations, directives and decisions (~930, 1995-2026) as published in the Federal Negarit "
             "Gazeta, from the House of Peoples' Representatives library. Search is on the Amharic title "
             "(or the law number, e.g. '1183'); texts are bilingual Amharic/English. No official case-law "
             "source is reachable (Federal Supreme Court site down).")
    gaps = (
        "Case law (Federal Supreme Court cassation decisions): fsc.gov.et HTTPS fails, HTTP gives 404 (2026-11-06)",
        "Laws missing or mislinked in the HoPR library: negaritgazeta.gov.et does not resolve (2026-11-06)",
        "Ministry of Justice publications: moj.gov.et TLS certificate expired (2026-11-06)",
        "Regional state laws: not researched yet",
    )
    samples = {
        "legislation_query": "1183",
        "law_id": "2026/2/23/80f4209b-5489-4138-a9d7-4d58a3adba69_Upploads_04012023140149_1183_2012 "
                  "የፌደራል የአስተዳደር ሥነ-ሥርዓት አዋጅ (1) (1).pdf",
        "provision": "2",
    }

    async def search_legislation(self, query, *, limit, page, filters):
        params = {"SearchQuery": _http.clean(query)[:200]}
        nq = _NUMQ.fullmatch(params["SearchQuery"])    # a law number: match it exactly, not as a substring
        f = filters or {}
        if f.get("type"):
            t = f["type"].strip().lower().rstrip("s")
            if t not in FOLDERS:
                raise BadRequest("type must be one of: " + ", ".join(FOLDERS) + ".")
            params["SelectedFolderId"] = FOLDERS[t]
        limit = max(1, min(int(limit), 45))
        start = (max(1, int(page)) - 1) * limit
        first, last = start // PAGE + 1, (start + limit - 1) // PAGE + 1
        hits: list[LawHit] = []
        total = 0
        if nq:
            first, last = 1, NUM_PAGES
        for n in range(first, last + 1):
            if n > first and (n - 1) * PAGE >= total:
                break
            r = await _http.get(LIST + "?" + urlencode({**params, "PageNumber": str(n)}))
            if r.status_code != 200:
                raise SourceError(_http.error(NAME, "search failed", r.status_code), r.status_code)
            doc = lhtml.fromstring(r.text)
            cnt = re.search(r"ከ\s*(\d+)\s*ሕጎች", doc.text_content())
            if not cnt:
                raise SourceError(f"Error ({NAME}): law list page changed.", 200)
            total = int(cnt[1])
            page_start = len(hits)
            for row in doc.xpath('//tr[.//div[contains(@class, "law-title")]]'):
                href = row.xpath('.//a[contains(@href, "ViewFiles?path=")]/@href')
                if not href:
                    continue
                lid = _norm_id(href[0])
                title = _http.clean(row.xpath('string(.//div[contains(@class, "law-title")])'))
                desc = _http.clean(row.xpath('string(.//div[contains(@class, "law-description")])'))
                typ = next((t for k, t in TYPES if k in title.split(" ቁጥር")[0] or title.startswith(k)), "")
                num = re.search(r"(\d{1,4}\s*/\s*\d{4})", title)
                hits.append(LawHit(id=lid, title=title, type=typ,
                                   number=re.sub(r"\s", "", num[1]) if num else "",
                                   snippet=desc if desc != title else "", url=_view_url(lid)))
            if not nq:    # the source lists in publication order; a short title is the law ABOUT the topic
                hits[page_start:] = sorted(hits[page_start:], key=lambda h: len(h.title))
        note = ("Matches the Amharic title or the law number (e.g. '1183'); years in titles "
                "are Ethiopian calendar (2012 EC = 2019/20). " + NOT_HELD)
        if not hits and _LAT.search(params["SearchQuery"]) and not _ETH.search(params["SearchQuery"]):
            note = ("The source searches Amharic titles only, so an English word finds nothing. Search in "
                    "Amharic (e.g. 'ኢንቨስትመንት' for investment: Investment Proclamation 1180/2012) or by "
                    "law number. " + note)
        if nq:
            y = int(nq[2]) if nq[2] else 0
            hits = [h for h in hits if h.number.split("/")[0] == nq[1].lstrip("0")
                    and (not y or int(h.number.split("/")[1]) in (y, y - 7, y - 8))]
            hits = _collapse(hits)
            total = len(hits)
            return Results(items=hits[start:start + limit], total=total, note=note)
        off = start - (first - 1) * PAGE
        return Results(items=_collapse(hits[off:off + limit]), total=total, note=note)

    async def get_legislation_text(self, id):
        law = await _law(id)
        parts = []
        if law["en"]:
            parts.append("## English\n\n" + "\n\n".join(law["en"]))
        if law["am"]:
            parts.append("## አማርኛ (Amharic)\n\n" + "\n\n".join(law["am"]))
        return LawText(id=_norm_id(id), title=law["title"], text="\n\n".join(parts), url=law["url"])

    async def get_legislation_toc(self, id):
        law = await _law(id)
        arts = law["en_arts"] or law["am_arts"]
        paras = law["en"] if law["en_arts"] else law["am"]
        part = _EN_PART if law["en_arts"] else _AM_PART
        starts = {i for i, _, _ in arts}
        entries = []
        for i, p in enumerate(paras):
            if i in starts:
                n, head = next((n, h) for j, n, h in arts if j == i)
                entries.append(TocEntry(title=f"Article {n} – {head[:100]}", level=1, provision=str(n)))
            elif part.match(p) and len(p) < 200 and i > (arts[0][0] if arts else 0) - 3:
                entries.append(TocEntry(title=p, level=0))
        if not arts:
            raise NotFound(f"No article structure found in '{id}'. Use get_legislation_text.")
        return Toc(id=_norm_id(id), title=law["title"], url=law["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        n = _prov_num(provision)
        law = await _law(id)
        en = _article_text(law["en"], law["en_arts"], n, _EN_PART)
        am = _article_text(law["am"], law["am_arts"], n, _AM_PART)
        if not en and not am:
            raise NotFound(f"No article {n} in '{id}'. Labels look like '5', 'Article 5' or '፭'.")
        text = "\n\n".join(x for x in (en and "**English**\n\n" + en, am and "**አማርኛ**\n\n" + am) if x)
        return Provision(law_id=_norm_id(id), law_title=law["title"], provision=str(n), text=text,
                         url=law["url"])
