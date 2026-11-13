"""Iraq: Kurdistan Region legislation from the Kurdistan Parliament's legislation database,
legislation.krd (قاعدة التشريعات / بنکەی یاسادانان), in Arabic and Kurdish.

Federal Iraqi sources are not usable from here (checked 2026-11-06 from a UK IP):
  * Federal Supreme Court (iraqfsc.iq), Council of Representatives (parliament.iq):
    Cloudflare "Just a moment..." challenge (403) on every path, robots.txt included.
  * Supreme Judicial Council (hjc.iq, sjc.iq) and its Iraqi Legal Database
    (iraqld.hjc.iq, iraqld.e-sjc-services.iq -> iraqld.msla.iq): 403 block pages
    ("Attention Required! | Cloudflare" / "تم منع هذا الطلب — مسلة").
  * Ministry of Justice / Al-Waqai Al-Iraqiya gazette (moj.gov.iq): connection times out.

Gotchas this code encodes (legislation.krd, verified 2026-11-06):
  * Search is POST /search keyword=...; it is a substring match on titles only, returns
    every hit on one page (no paging, no count) and answers HTTP 500 {"message":
    "Resource not found"} for very common words ('قانون', 'كوردستان'). We page locally.
  * Each law exists twice, as separate records with their own ids: an Arabic text and a
    Kurdish (Sorani) text. Hits mix both; the `language` filter picks one.
  * /law-detail/?id=<n> holds the enacted (original) text in one <pre>, line by line.
    Labels on the page are Kurdish (ژمارەی یاسا = number, ساڵی دەرچوون = year,
    بەرکارە = in force). Unknown id -> HTTP 500; non-numeric id -> 400.
  * Consolidated amended texts (/amends-detail/?id=) are PDF/Word only: not used.
  * Article headings are ordinal words: Arabic 'المادة( الخامسة والعشرون):', Kurdish
    'ماددەی بیست وپێنجەم:' (often with heh + ZWNJ instead of ە). Provision labels are the
    article numbers.
"""
from __future__ import annotations

import datetime
import re
from html import unescape

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import LawHit, LawText, Provision, Results, Toc, TocEntry

HOST = "https://legislation.krd"
NAME = "legislation.krd"
_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")
_KU_LETTERS = re.compile("[ڕڵۆێڤ]|ژمار|ساڵ|یاسا|بڕیار")

# Ordinals. Matching is done on _norm() text: no ZWNJ/tatweel/harakat, ە/ة -> ه, unified
# alif/kaf/yeh.
_AR_UNITS = {"الاولى": 1, "الاول": 1, "الحاديه": 1, "الحادي": 1, "الثانيه": 2, "الثاني": 2,
             "الثالثه": 3, "الثالث": 3, "الرابعه": 4, "الرابع": 4, "الخامسه": 5, "الخامس": 5,
             "السادسه": 6, "السادس": 6, "السابعه": 7, "السابع": 7, "الثامنه": 8, "الثامن": 8,
             "التاسعه": 9, "التاسع": 9, "العاشره": 10, "العاشر": 10}
_AR_TENS = {"العشرون": 20, "العشرين": 20, "الثلاثون": 30, "الثلاثين": 30, "الاربعون": 40,
            "الاربعين": 40, "الخمسون": 50, "الخمسين": 50, "الستون": 60, "الستين": 60,
            "السبعون": 70, "السبعين": 70, "الثمانون": 80, "الثمانين": 80, "التسعون": 90,
            "التسعين": 90}
_KU = {"یهکهم": 1, "دووهم": 2, "سییهم": 3, "سێیهم": 3, "چوارهم": 4, "پینجهم": 5,
       "پێنجهم": 5, "شهشهم": 6, "حهوتهم": 7, "ههشتهم": 8, "نویهم": 9, "نۆیهم": 9,
       "دهیهم": 10, "یازدهم": 11, "دوازدهم": 12, "سیازدهم": 13, "سێزدهم": 13,
       "چواردهم": 14, "پازدهم": 15, "شازدهم": 16, "شانزدهم": 16, "حهڤدهم": 17,
       "حهفدهم": 17, "ههژدهم": 18, "نۆزدهم": 19, "بیستهم": 20, "سیههم": 30, "سییههم": 30,
       "چلهم": 40, "پهنجاههم": 50, "پهنجایهم": 50}
_KU_TENS = {"بیست": 20, "سی": 30, "چل": 40, "پهنجا": 50, "شهست": 60, "حهفتا": 70}

_ART = re.compile(r"^(?:ال)?مادد?ه(?:ی)?\s*[\(\[]?\s*([^():：\-–]{1,40}?)\s*[\)\]]?\s*(?:[:：\-–.]\s*(.*))?$")
_HEADING = re.compile(r"^(?:(?:الباب|الفصل|الفرع|القسم|دهروازهی|بهشی)\s|الاسباب الموجبه|ه[وۆ]ی دهرکردن)")
_STATUS = {"بەرکارە": "in force (بەرکارە)",
           "هەڵوەشاوەتەوە": "repealed/annulled (هەڵوەشاوەتەوە): no longer in force, do not rely on it"}
_META = {"ژمارەی یاسا": "number", "ساڵی دەرچوون": "year", "یاسا پەیوەستەکان": "related laws"}


def _norm(s: str) -> str:
    """For matching only."""
    s = (s or "").translate(_DIGITS).replace("‌", "").replace("ـ", "")
    s = re.sub("[ً-ْ]", "", s)
    s = re.sub("[أإآ]", "ا", s)
    s = s.replace("ە", "ه").replace("ة", "ه").replace("ك", "ک").replace("ي", "ی").replace("ى", "ی")
    return re.sub(r"\s+", " ", s).strip()


for _d in (_AR_UNITS, _AR_TENS, _KU, _KU_TENS):
    for _k in list(_d):
        _d[_norm(_k)] = _d.pop(_k)


def _ordinal(words: str) -> int | None:
    """'5', 'الخامسة', 'الحادية عشرة', 'الخامسة والعشرون', 'بیست وپێنجەم' -> int."""
    w = _norm(words).replace("(", " ").replace(")", " ").strip()
    m = re.match(r"^(\d+)", w)
    if m:
        return int(m[1])
    known = set(_KU) | set(_KU_TENS) | set(_AR_UNITS) | set(_AR_TENS)
    toks = []
    for t in w.split():
        if t == "و":
            continue
        toks.append(t[1:] if t.startswith("و") and t not in known and t[1:] in known else t)
    if not toks:
        return None
    a = toks[0]
    if a in _KU:
        return _KU[a]
    if a in _KU_TENS and len(toks) >= 2 and toks[1] in _KU:      # 'بیست' + 'یهکهم'
        return _KU_TENS[a] + _KU[toks[1]]
    if a in _AR_TENS:
        return _AR_TENS[a]
    if a in _AR_UNITS:
        unit = _AR_UNITS[a]
        if len(toks) >= 2 and toks[1] in ("عشر", "عشره"):
            return 10 + unit
        if len(toks) >= 2 and toks[1] in _AR_TENS:
            return _AR_TENS[toks[1]] + unit
        if len(toks) >= 3 and toks[1] == "بعد" and toks[2] in ("المائه", "المایه", "المئه"):
            return 100 + unit
        return unit
    if a in ("المائه", "المایه", "المئه"):
        return 100
    return None


def _number_year(title: str) -> tuple[str, str]:
    t = _norm(title)
    m = (re.search(r"رقم\s*\(?\s*(\d+)\s*\)?\s*(?:ل?سنه|لعام)\s*\(?(\d{4})", t)
         or re.search(r"ژماره\s*\(?\s*(\d+)\s*\)?\s*(?:ی|ى)?\s*(?:بو|بۆ)?\s*(?:ی\s*)?ساڵ[یى]\s*\(?(\d{4})", t))
    return (m[1], m[2]) if m else ("", "")


def _lang(title: str) -> str:
    return "ku" if _KU_LETTERS.search(title.replace("‌", "")) else "ar"


def _type(title: str) -> str:
    w = _http.clean(title).split()
    return re.sub(r"[()]", "", w[0]) if w else ""


def _check_id(id: str) -> str:
    m = re.search(r"(?:law-detail/?\?id=)?(\d+)\s*$", str(id or "").strip())
    if not m:
        raise BadRequest(f"Bad legislation.krd id {id!r}: expected the numeric id search_legislation "
                         "returns (e.g. '3475'), or a https://legislation.krd/law-detail/?id=<n> URL.")
    return m[1]


def _url(lid: str) -> str:
    return f"{HOST}/law-detail/?id={lid}"


_pages: dict = {}


async def _law(lid: str) -> dict:
    if lid in _pages:
        return _pages[lid]
    url = _url(lid)
    r = await _http.get(url)
    if r.status_code in (400, 404, 500):
        raise NotFound(f"{NAME} has no law with id {lid} (HTTP {r.status_code}).")
    if r.status_code != 200:
        raise SourceError(_http.error(NAME, f"GET {url}", r.status_code), r.status_code)
    html = r.text
    title = re.search(r"<h4>(.*?)</h4>", html, re.S)
    if not title:
        raise SourceError(f"{NAME}: no title on {url} (layout changed?)")
    title = _http.clean(unescape(re.sub(r"<[^>]+>", " ", title[1])))
    pre = re.search(r"<pre[^>]*>(.*?)</pre>", html, re.S)
    if not pre:
        raise NotFound(f"{NAME} has no HTML text for id {lid}; only the PDF/Word download at {url}.")
    lines = [_http.clean(unescape(re.sub(r"<[^>]+>", " ", ln))) for ln in pre[1].split("\n")]
    lines = [ln for ln in lines if ln]
    h5 = [_http.clean(unescape(re.sub(r"<[^>]+>", " ", x)))
          for x in re.findall(r"<h5>(.*?)</h5>", html, re.S)]
    meta = {}
    for x in h5:
        if ":" in x:
            k, v = (s.strip() for s in x.split(":", 1))
            if v:
                meta[k] = v
    status = re.search(r'<h5 class="h6 fields">(.*?)</h5>', html, re.S)
    status = _http.clean(unescape(re.sub(r"<[^>]+>", " ", status[1]))) if status else ""
    num, year = _number_year(title)
    d = {"id": lid, "title": title, "url": url, "lines": lines, "meta": meta, "status": status,
         "number": num, "year": year}
    return _http.lru_put(_pages, lid, d, 32)


def _articles(lines: list[str]) -> tuple[list[TocEntry], dict[str, tuple[int, int]]]:
    """TOC entries and {label: (first line, end line)} for each article."""
    entries, spans, starts = [], {}, []
    prev = 0
    for i, ln in enumerate(lines):
        n = _norm(ln)
        if len(n) > 200:
            continue
        m = _ART.match(n)
        if m and len(m[1]) <= 40 and (m[2] is not None or len(n) <= 60):
            num = _ordinal(m[1])
            if num is None or num <= 0:
                num = prev + 1
            label = str(num)
            k = 2
            while label in spans:
                label, k = f"{num}-{k}", k + 1
            prev = num
            spans[label] = (i, len(lines))
            starts.append(label)
            entries.append(TocEntry(title=ln.rstrip(":： "), level=1, provision=label))
        elif _HEADING.match(n) and len(n) <= 60:
            entries.append(TocEntry(title=ln, level=0))
    # Each article runs to the next article or structural heading.
    stops = sorted({s for s, _ in spans.values()} |
                   {i for i, ln in enumerate(lines) if _HEADING.match(_norm(ln)) and len(_norm(ln)) <= 60})
    for label, (s, _) in spans.items():
        nxt = [x for x in stops if x > s]
        spans[label] = (s, nxt[0] if nxt else len(lines))
    return entries, spans


def _label(provision: str) -> str:
    p = _norm(str(provision or ""))
    p = re.sub(r"(?i)^(?:art(?:icle)?\.?|madde)\s*", "", p)
    m = _ART.match(p)
    if m:
        p = m[1]
    p = p.strip(" ():.")
    m = re.match(r"^(\d+)(-\d+)?$", p)
    if m:
        return p
    n = _ordinal(p)
    if n is None:
        raise BadRequest(f"Unknown provision {provision!r}: use the article number from the TOC, "
                         "e.g. '5', 'المادة 5' or 'المادة الخامسة'.")
    return str(n)


class Iraq(Jurisdiction):
    code = "iq"
    name = "Iraq"
    languages = ("ar", "ckb")
    aliases = ("iraq", "العراق", "جمهورية العراق", "kurdistan", "kurdistan region", "krg",
               "إقليم كوردستان", "هەرێمی کوردستان")
    sources = (
        Source("Kurdistan Parliament legislation database (قاعدة التشريعات), legislation.krd "
               "(Kurdistan Region of Iraq only)",
               HOST, covers=("legislation",),
               licence="unknown: no terms or copyright notice on legislation.krd (official "
                       "legislative texts of the Kurdistan Region)",
               commercial_use=None, ai_use=None, auth="none",
               rate_limit="unknown; 1 s spacing, no 429 seen in ~30 requests (2026-11)",
               terms_url=f"{HOST}/about",
               warning="Kurdistan Region legislation only (not federal Iraqi law). Texts are as "
                       "enacted; amendments are separate records."),
    )
    legislation_filters = {
        "language": "ar (Arabic texts) | ku (Kurdish/Sorani texts); default both",
        "year": "year of the law in its title (YYYY)",
        "year_from": "first year (YYYY) of a range, e.g. 2022 for 2022 onward",
        "year_to": "last year (YYYY) of a range; default the current year when year_from is set",
    }
    min_interval = {"legislation.krd": 1.0}
    notes = ("Kurdistan Region laws, decisions, regulations and instructions (1992 on) in Arabic "
             "and Kurdish from legislation.krd; title search only. Federal Iraqi sources "
             "(Federal Supreme Court, Supreme Judicial Council legal database, MoJ gazette, "
             "parliament.iq) block automated access or are unreachable: no case law.")
    gaps = (
        "Federal Iraqi legislation (parliament.iq, Iraqi Legal Database iraqld): bot check / blocks our client (Cloudflare 403)",
        "Federal case law (Federal Supreme Court iraqfsc.iq, Supreme Judicial Council): bot check / blocks our client (Cloudflare)",
        "Al-Waqai Al-Iraqiya gazette (moj.gov.iq): site down / unreachable (timeout, 2026-11-06)",
        "Kurdistan consolidated amended texts (/amends-detail/): PDF/Word only; not built yet",
        "Kurdistan Region case law: not researched yet",
    )
    samples = {
        "legislation_query": "العمل",
        "law_id": "3475",
        "provision": "1",
    }

    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        q = _http.clean(query)
        if not q:
            raise BadRequest("legislation.krd needs a search word (it searches titles), e.g. 'الاستثمار'.")
        lang = (filters.get("language") or "").strip().lower()
        if lang not in ("", "ar", "ku", "ckb"):
            raise BadRequest("language must be 'ar' or 'ku'")
        lang = "ku" if lang == "ckb" else lang
        year = str(filters.get("year", "") or "").strip()
        if year and not re.fullmatch(r"\d{4}", year):
            raise BadRequest(f"year must be YYYY, got {year!r}")
        yf, yt = (str(filters.get(k, "") or "").strip() for k in ("year_from", "year_to"))
        for v in (yf, yt):
            if v and not re.fullmatch(r"\d{4}", v):
                raise BadRequest(f"year_from / year_to must be YYYY, got {v!r}")
        if year and (yf or yt):
            raise BadRequest("use either year or year_from/year_to, not both")
        if yf or yt:
            yf, yt = yf or "1992", yt or str(datetime.date.today().year)
            if int(yf) > int(yt) or int(yt) - int(yf) > 9:
                raise BadRequest("year_from..year_to must be an ascending range of at most 10 years")
        years = [year] if year else [str(y) for y in range(int(yf), int(yt) + 1)] if yf else []
        r = await _http.post(f"{HOST}/search", data={"keyword": q})
        pages, note = [], ""
        seen_year = seen_ku = 0
        if r.status_code == 500 and years:
            # Too-common word: the site only answers specific keywords. Search the year phrase
            # as it appears in titles instead and keep the hits whose title contains the word.
            for y in years:
                for kw in ((f"لسنة {y}", f"سنة {y}") if lang != "ku" else ()) + \
                          ((f"ساڵی {y}",) if lang != "ar" else ()):
                    rr = await _http.post(f"{HOST}/search", data={"keyword": kw})
                    if rr.status_code != 200:
                        raise SourceError(_http.error(NAME, f"search {kw!r}", rr.status_code), rr.status_code)
                    pages.append(rr.text)
            yrs = years[0] if len(years) == 1 else f"{years[0]}-{years[-1]}"
            note = f" '{q}' alone is too common for the site, so titles of {yrs} were searched and filtered by it."
        elif r.status_code == 500:
            raise SourceError(_http.error(NAME, f"search {q!r}", 500,
                                          "The site fails on very common words (e.g. 'قانون'); "
                                          "use a more specific title word, or add the year or "
                                          "year_from/year_to filter to list those years' laws."), 500)
        elif r.status_code != 200:
            raise SourceError(_http.error(NAME, f"search {q!r}", r.status_code), r.status_code)
        else:
            pages.append(r.text)
        hits, seen = [], set()
        for text in pages:
            for m in re.finditer(r'href="/law-detail/\?id=(\d+)"[^>]*>\s*<div class="ms-4">\s*<h4>(.*?)</h4>',
                                 text, re.S):
                title = _http.clean(unescape(re.sub(r"<[^>]+>", " ", m[2])))
                num, yr = _number_year(title)
                if m[1] in seen or (lang and _lang(title) != lang) or (years and yr not in years):
                    continue
                if note:
                    seen_year += 1
                    seen_ku += _lang(title) == "ku"
                if note and _norm(q) not in _norm(title):
                    continue
                seen.add(m[1])
                hits.append(LawHit(id=m[1], title=title, type=_type(title), number=num, date="",
                                   url=_url(m[1]), snippet=f"year {yr}; {'Kurdish' if _lang(title) == 'ku' else 'Arabic'} text" if yr else ""))
        limit, page = max(1, min(int(limit), 50)), max(1, int(page))
        start = (page - 1) * limit
        if not hits and note:
            note += (f" The source lists {seen_year} record(s) of that period ({seen_year - seen_ku} Arabic, "
                     f"{seen_ku} Kurdish) and none has '{q}' in its title, so it holds no such record "
                     "for that period. Most recent records are Kurdish-titled instructions (ڕێنمایی); "
                     "Kurdish laws say یاسا, not قانون, so search that word too. Note that a plain "
                     "year query such as 'لسنة 2024' matches Arabic titles only; search 'ساڵی 2024' "
                     "for the Kurdish ones.")
        elif not hits:
            note += (f" Not found: the source has no record whose title contains the exact phrase '{q}'. "
                     "It matches titles as one phrase, so extra words or numbers can miss; try one key "
                     "word, with the year filter, or the Kurdish word (e.g. کار for labour). If a "
                     "key-word search does not show the law either, treat it as not held in this "
                     "source and look for it in the official gazette.")
        elif not years and re.search(r"(?:^|\s)ل?سنة\s*\d{4}$", q) and lang != "ku":
            note += (" This phrase matches Arabic titles only; Kurdish-titled records of that year "
                     "are not included; search 'ساڵی <year>' for those.")
        if hits:
            note += (" A hit only means the words occur somewhere in a title (e.g. 'قانون العمل' also "
                     "matches 'قانون العمل بقانون ...'): read the titles. If the law you want is not "
                     "among them, this source does not hold it under that title; it is not a "
                     "complete list of a year's legislation.")
        return Results(hits[start:start + limit], len(hits),
                       note="Kurdistan Region only; title search (substring), Arabic and Kurdish "
                            "records mixed unless filtered. Texts as enacted. No hit only means no "
                            "record title contains that word." + note)

    async def get_legislation_text(self, id):
        d = await _law(_check_id(id))
        meta = {_META.get(k, k): v for k, v in d["meta"].items()}
        if d["status"]:
            meta["status"] = _STATUS.get(d["status"], d["status"])
        meta["language"] = "Kurdish (Sorani)" if _lang(d["title"]) == "ku" else "Arabic"
        return LawText(id=d["id"], title=d["title"], text="\n\n".join(d["lines"]), url=d["url"],
                       as_of="", metadata=meta)

    async def get_legislation_toc(self, id):
        d = await _law(_check_id(id))
        entries, _ = _articles(d["lines"])
        if not any(e.provision for e in entries):
            raise NotFound(f"{NAME} id {d['id']}: no numbered articles found; use get_legislation_text.")
        return Toc(id=d["id"], title=d["title"], url=d["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        d = await _law(_check_id(id))
        label = _label(provision)
        _, spans = _articles(d["lines"])
        if label not in spans:
            raise NotFound(f"{NAME} id {d['id']} has no article {label} "
                           f"(articles: {', '.join(list(spans)[:10])}{'…' if len(spans) > 10 else ''}).")
        s, e = spans[label]
        lines = d["lines"][s:e]
        text = "**" + lines[0] + "**" + ("\n\n" + "\n\n".join(lines[1:]) if len(lines) > 1 else "")
        return Provision(law_id=d["id"], law_title=d["title"], provision=label, text=text,
                         url=d["url"], as_of="")
