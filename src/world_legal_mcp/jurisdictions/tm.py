"""Turkmenistan: laws, codes and Mejlis resolutions from mejlis.gov.tm, the Constitution
and the Supreme Court Plenum resolutions from court.gov.tm.

Gotchas this code encodes (verified 2026-11-06 from a UK IP):
  * mejlis.gov.tm (Parliament, Laravel): robots.txt "User-agent: * / Disallow:" (all
    allowed), no terms page, footer "2026 Ähli hukuklar goralan" (All rights reserved).
    /{laws|codes|mejlis-decrees}?lang=tm|ru&ajax=true returns the whole list as JSON
    ([{id, title_tm|title_ru, published_date}]; ~370 laws, 22 codes, ~460 decrees).
    lang=en gives the Russian titles, so only tm and ru are offered. Without ?lang= the
    pages redirect to the home page. The act page /single-{law|code|decree}/{id}?lang=..
    has the title in <h4 class="text_title"> and the full text in <div class="text_content">;
    an unknown id is a 404. Large pages are sometimes cut off mid-transfer
    ("incomplete chunked read"); that is reported, not retried.
  * Article headings are bold paragraphs ("**1-nji madda. ...**", "**Статья 1. ...**"),
    Word-made, so bold markers are split inside words ("**1-nji ma****dda.**") and long
    headings wrap into the next bold paragraph. Codes start with the enacting law
    (articles 1-4) before the code's own articles 1..n, so numbering restarts: the
    longest run gets plain labels ("5"), the others "k:5" (k = run number).
  * The Mejlis page of the Constitution has only the preamble. court.gov.tm (Supreme Court,
    React app over /api/, robots.txt allows all, no terms; the privacy policy covers only
    personal data) has the consolidated Constitution as text-layer PDFs (/api/constitution,
    tm and ru). Its line-wrapped text is rejoined into paragraphs here; article 6¹
    (Halk Maslahaty, 2023) comes out of the PDF as "61-njy madda" right after article 6.
  * Case law: the only public court material is the Supreme Court Plenum's collection of
    guiding resolutions (/api/collection-decision): one ~6 MB PDF, 686 pages, 87
    resolutions 1997-2025 as amended to 05.11.2025. Its "rus" link is the same Turkmen
    file. The table of contents (last pages, "M A Z M U N Y") gives each resolution's date,
    number and page range; page i of the PDF carries the printed page number i on its
    first line. No individual judgments are published.
"""
from __future__ import annotations

import asyncio
import re
import time

import httpx

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

MEJLIS = "https://mejlis.gov.tm"
COURT = "https://court.gov.tm"
PLENUM = "Türkmenistanyň Ýokary kazyýetiniň Plenumy"
MAX_BYTES = 40_000_000
LIST_TTL = 3600
_KINDS = {"law": ("laws", "single-law", "Kanun", "Закон"),
          "code": ("codes", "single-code", "Kodeks", "Кодекс"),
          "decree": ("mejlis-decrees", "single-decree", "Mejlisiň karary", "Постановление Меджлиса")}
_LAW_ID = re.compile(r"^(?:(law|code|decree)-(\d+)|(constitution))(?:-(tm|ru))?$")
_DEC_ID = re.compile(r"^(\d{4})-(\d{2})-(\d{2})/(\d+)$")
_DEC_ALT = re.compile(r"^(\d{1,2})\.(\d{1,2})\.(\d{4})\D*?(?:№|no\.?|karar)?\s*(\d+)$", re.I)
_SUP = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")
_ART = re.compile(r"^(\d+)([⁰¹²³⁴⁵⁶⁷⁸⁹]*)\s*-\s*[a-zçäöüýňž]+\s+m\s?a\s?d\s?d\s?a\b|^Статья\s+(\d+)(?:[-.](\d+))?([⁰¹²³⁴⁵⁶⁷⁸⁹]*)\b",
                  re.I)
_SECT = re.compile(r"^(?:[IVXLCІ]+|\d+)\s*(?:-\s*\w+\s+)?(BÖLEK|BÖLÜM|BAP)\b|^(ЧАСТЬ|РАЗДЕЛ|ГЛАВА)\s+[IVXLC\d]+",
                   re.I)
_SECT_RANK = {"bölek": 0, "часть": 0, "bölüm": 1, "раздел": 1, "bap": 2, "глава": 2}
_TOC_ENTRY = re.compile(r"(?s)(?:^|\n)(\d{1,3})\.\s*(.+?)\((\d\d\.\d\d\.\d{4})\s*ýyl,\s*karar\s*№\s*(\d+)\)"
                        r"[\s.]*?(\d+)\s*-\s*(\d+)")

_lists: dict = {}       # (kind, lang) -> (time, items)
_docs: dict = {}        # law id -> (title, url, date, paragraphs, metadata)
_pdf_urls: dict = {}
_plenum: list = []      # parsed Plenum collection (filled once)
_plenum_lock = asyncio.Lock()


async def _fetch(url: str, what: str, params: dict | None = None) -> httpx.Response:
    host = url.split("/")[2]
    try:
        r = await _http.get(url, params=params)
    except httpx.HTTPError as e:
        raise SourceError(f"Error ({host}): {what} failed ({type(e).__name__}: the transfer was "
                          "cut off or timed out); try again later", "") from None
    if r.status_code == 404:
        raise NotFound(f"{host} has no {what}.")
    if r.status_code != 200:
        raise SourceError(_http.error(host, what, r.status_code), r.status_code)
    return r


def _json(r: httpx.Response, host: str):
    try:
        return r.json()
    except ValueError:
        raise SourceError(f"{host}: answer is not JSON (blocked or changed?)", 200) from None


async def _pdf(kind: str, lang: str) -> tuple[str, bytes]:
    """court.gov.tm PDF named by /api/{kind}; size checked with HEAD first (<= 40 MB)."""
    key = (kind, lang)
    if key not in _pdf_urls:
        rows = _json(await _fetch(f"{COURT}/api/{kind}", "PDF list"), "court.gov.tm")
        url = (rows or [{}])[0].get("tm_pdf" if lang == "tm" else "rus_pdf") or ""
        if not url.startswith("https://court.gov.tm/"):
            raise SourceError(f"court.gov.tm: no {lang} PDF listed at /api/{kind}", 200)
        _pdf_urls[key] = url
    url = _pdf_urls[key]
    try:
        h = await _http.request("HEAD", url)
    except httpx.HTTPError:
        raise SourceError("Error (court.gov.tm): PDF size check failed; try again later", "") from None
    size = int(h.headers.get("Content-Length") or 0)
    if h.status_code != 200 or not size or size > MAX_BYTES:
        raise SourceError(f"court.gov.tm: PDF {url} unavailable or too large "
                          f"(HTTP {h.status_code}, {size} bytes; limit {MAX_BYTES})", h.status_code)
    return url, (await _fetch(url, "PDF")).content


# ---------- text shaping ----------

def _tidy(p: str) -> str:
    p = p.replace("\xad", "").replace("****", "").replace("** **", " ")
    plain = _plain(p)
    if p.startswith("**") and p.endswith("**") and plain:
        return f"**{plain}**"
    return p


def _plain(p: str) -> str:
    return _http.clean(p.replace("*", "").replace("\\", "").replace("#", ""))


def _upper(ln: str) -> bool:
    return ln == ln.upper() and len(re.findall(r"[^\W\d_]", ln)) > 3


def _pdf_paragraphs(lines: list[str]) -> list[str]:
    """Rejoin the line-wrapped text of a PDF: a new paragraph starts at a heading or a
    numbered item, or after a line ending a sentence."""
    out: list[str] = []
    for ln in lines:
        if not ln or ln.isdigit():
            continue
        upper = _upper(ln)
        new = (not out or re.search(r"[.:;!?»]$", out[-1]) or _ART.match(ln) or _SECT.match(ln)
               or re.match(r"^(\d{1,3}[.)]|[a-zа-я]\))\s", ln) or upper != _upper(out[-1]))
        if new:
            out.append(ln)
        elif out[-1].endswith(" -"):
            out[-1] = out[-1][:-2] + "-" + ln
        else:
            out[-1] += " " + ln
    return out


def _structure(paras: list[str]) -> list[dict]:
    """Headings and articles with their paragraph ranges and provision labels."""
    items = []
    for i, p in enumerate(paras):
        plain = _plain(p)
        m = _ART.match(plain)
        if m:
            if m[1]:
                num, sub = int(m[1]), m[2].translate(_SUP)
            else:
                num, sub = int(m[3]), (m[4] or m[5].translate(_SUP))
            items.append({"kind": "art", "i": i, "num": num, "sub": sub, "title": plain})
            continue
        s = _SECT.match(plain)
        if s and len(plain) < 300:
            items.append({"kind": "sect", "i": i, "rank": _SECT_RANK[(s[1] or s[2]).lower()], "title": plain})
    # wrapped bold headings: following all-bold paragraphs belong to the heading
    for it in items:
        j = it["i"] + 1
        if paras[it["i"]].endswith("**"):
            while j < len(paras) and paras[j].startswith("**") and paras[j].endswith("**") \
                    and not any(x["i"] == j for x in items) and len(it["title"]) < 250:
                it["title"] += " " + _plain(paras[j])
                j += 1
    # article 6¹ printed as "61" right after 6 (PDF without superscripts)
    prev = None
    for it in items:
        if it["kind"] != "art":
            continue
        if prev is not None and not it["sub"] and it["num"] > prev + 1 \
                and str(it["num"])[:-1] == str(prev):
            it["sub"], it["num"] = str(it["num"])[-1], prev
        else:
            prev = it["num"]
    # runs of article numbers; a restart begins a new run
    runs, last = [], None
    for it in items:
        if it["kind"] == "art":
            if last is None or it["num"] < last:
                runs.append([])
            runs[-1].append(it)
            last = it["num"]
    for n, it in enumerate(items):
        it["end"] = items[n + 1]["i"] if n + 1 < len(items) else len(paras)
    # the longest run wins; on a tie the run with the most text (the Criminal Code starts with
    # a list of bare article headings, then the full text)
    main = max(range(len(runs)), key=lambda k: (len(runs[k]), sum(x["end"] - x["i"] for x in runs[k]))) \
        if runs else -1
    for k, run in enumerate(runs):
        for it in run:
            label = f"{it['num']}-{it['sub']}" if it["sub"] else str(it["num"])
            it["label"] = label if k == main else f"{k + 1}:{label}"
    return items


def _years(year: str):
    """'2023' -> (2023, 2023); '2022-2024' -> (2022, 2024); '2022-' -> (2022, 9999); '' -> None."""
    if not year:
        return None
    m = re.fullmatch(r"(\d{4})(?:\s*-\s*(\d{4})?)?", year)
    if not m:
        raise BadRequest("year must be four digits (2023), a range (2022-2024) or open-ended (2022-)")
    lo = int(m[1])
    hi = int(m[2]) if m[2] else (9999 if "-" in year else lo)
    if hi < lo:
        raise BadRequest("year range must run upward, e.g. 2022-2024")
    return lo, hi


def _in_years(date: str, span) -> bool:
    return not span or (date[:4].isdigit() and span[0] <= int(date[:4]) <= span[1])


def _norm_prov(s: str) -> str:
    s = re.sub("[⁰¹²³⁴⁵⁶⁷⁸⁹]+", lambda m: "-" + m[0].translate(_SUP), str(s or "").strip().lower())
    m = re.match(r"^(\d+):\s*(.*)$", s)
    run, s = (m[1] + ":", m[2]) if m else ("", s)
    m = re.search(r"(\d+)(?:\s*[-.]\s*(\d+)(?!\s*-?\s*[a-zçäöüýňž]))?", s)
    if not m:
        return ""
    return run + (f"{m[1]}-{m[2]}" if m[2] else m[1])


# ---------- legislation ----------

def _parse_id(id: str):
    m = _LAW_ID.match(str(id or "").strip().lower())
    if not m:
        raise BadRequest("law id is law-N, code-N, decree-N or constitution, optionally with "
                         "-ru (e.g. code-6, law-384-ru); see search_legislation")
    return (m[1] or "constitution"), m[2], (m[4] or "tm")


async def _list(kind: str, lang: str) -> list[dict]:
    hit = _lists.get((kind, lang))
    if hit and time.monotonic() - hit[0] < LIST_TTL:
        return hit[1]
    rows = _json(await _fetch(f"{MEJLIS}/{_KINDS[kind][0]}", f"{kind} list",
                              {"lang": lang, "ajax": "true"}), "mejlis.gov.tm")
    if not isinstance(rows, list):
        raise SourceError("mejlis.gov.tm: list answer changed", 200)
    _lists[(kind, lang)] = (time.monotonic(), rows)
    return rows


def _const_hit(lang: str) -> LawHit:
    return LawHit(id="constitution" + ("-ru" if lang == "ru" else ""),
                  title="Türkmenistanyň Konstitusiýasy" if lang == "tm" else "Конституция Туркменистана",
                  type="Konstitusiýa" if lang == "tm" else "Конституция", date="2016-09-14",
                  status="consolidated (amended to 21.01.2023)", url=f"{COURT}/api/constitution")


async def _doc(id: str):
    kind, num, lang = _parse_id(id)
    key = f"{kind}-{num}-{lang}" if num else f"constitution-{lang}"
    if key in _docs:
        return _docs[key]
    if kind == "constitution":
        url, data = await _pdf("constitution", lang)
        text = await asyncio.to_thread(_http.pdf_text, data)
        if len(text) < 1000:
            raise SourceError("court.gov.tm: Constitution PDF has no text layer", 200)
        paras = _pdf_paragraphs(text.splitlines())
        amend = re.findall(r"(\d\d\.\d\d\.\d{4})\s*(?:ý\.|г\.)", text[:8000])
        as_of = max((_http.iso_date(d) for d in amend), default="")
        title = _const_hit(lang).title
        meta = {"Source": "court.gov.tm (Supreme Court) PDF", "Amended to": as_of}
        return _http.lru_put(_docs, key, (title, url, "2016-09-14", paras, meta, as_of), 8)
    url = f"{MEJLIS}/{_KINDS[kind][1]}/{num}?lang={lang}"
    r = await _fetch(url, f"{kind} {num}")
    m = re.search(r'(?s)<h4 class="text_title">(.*?)</h4>.*?<div class="text_content">(.*?)</div>\s*</div>', r.text)
    if not m:
        raise SourceError("mejlis.gov.tm: act page has no text block (redirected or changed?)", 200)
    title = _plain(_http.html_to_md(m[1])).rstrip("*").strip() or f"{kind} {num}"
    paras = [_tidy(p) for p in _http.html_paragraphs(m[2])]
    paras = [p for p in paras if _plain(p)]
    if not paras:
        raise NotFound(f"mejlis.gov.tm: {kind} {num} has no text in {lang}")
    row = next((x for x in await _list(kind, lang) if str(x.get("id")) == num), {})
    date = _http.iso_date(row.get("published_date", ""))
    meta = {"Type": _KINDS[kind][2 if lang == "tm" else 3], "Date (as listed)": date, "Language": lang}
    return _http.lru_put(_docs, key, (title, url, date, paras, meta, ""), 8)


# ---------- Plenum collection ----------

def _parse_plenum(text: str) -> list[dict]:
    pages = text.split("\n\n")
    body = {}
    for i, pg in enumerate(pages):
        lines = pg.split("\n")
        if i and lines[0].isdigit():
            body[int(lines[0])] = lines[1:]
    start = next((n for n, ls in body.items() if ls[:1] == ["M A Z M U N Y"]), None)
    if start is None:
        raise SourceError("court.gov.tm: table of contents not found in the Plenum collection", 200)
    toc = "\n".join(ln for n in sorted(body) if n >= start for ln in body[n])
    out = []
    for m in _TOC_ENTRY.finditer(toc):
        a, b = int(m[5]), int(m[6])
        lines = [ln for n in range(a, b + 1) for ln in body.get(n, [])]
        paras = _pdf_paragraphs(lines)
        out.append({"id": f"{_http.iso_date(m[3])}/{m[4]}", "n": int(m[1]),
                    "title": _http.clean(m[2]), "date": _http.iso_date(m[3]), "number": m[4],
                    "pages": f"{a}-{b}", "text": "\n\n".join(paras)})
    if len(out) < 50:
        raise SourceError(f"court.gov.tm: only {len(out)} resolutions parsed from the collection", 200)
    return out


async def _plenum_items() -> tuple[str, list[dict]]:
    async with _plenum_lock:
        if not _plenum:
            url, data = await _pdf("collection-decision", "tm")
            text = await asyncio.to_thread(_http.pdf_text, data)
            _plenum.extend(await asyncio.to_thread(_parse_plenum, text))
            _pdf_urls["plenum"] = url
    return _pdf_urls["plenum"], _plenum


class Turkmenistan(Jurisdiction):
    code = "tm"
    name = "Turkmenistan"
    languages = ("tk", "ru")
    aliases = ("tkm", "turkmenistan", "türkmenistan")
    sources = (
        Source("Mejlis of Turkmenistan (mejlis.gov.tm)", MEJLIS, covers=("legislation",),
               licence="none stated; footer '2026 Ähli hukuklar goralan' (All rights reserved)",
               rate_limit="unknown; 1 s spacing, no 429 seen (2026-11)"),
        Source("Supreme Court of Turkmenistan (court.gov.tm)", COURT, covers=("caselaw", "legislation"),
               licence="none stated (no terms page; privacy policy covers only personal data)",
               rate_limit="unknown; 1 s spacing, no 429 seen (2026-11)"),
    )
    caselaw_filters = {"year": "year of the Plenum resolution, e.g. 2023, or a range: 2022-2025 "
                               "(2022- = since 2022)"}
    legislation_filters = {"type": "law | code | decree (Mejlis resolution) | constitution",
                           "year": "year as listed by mejlis.gov.tm, e.g. 2025, or a range: 2022-2025 "
                                    "(2022- = since 2022)",
                           "lang": "tm (default) | ru"}
    min_interval = {"mejlis.gov.tm": 1.0, "court.gov.tm": 1.0}
    notes = ("Laws, codes and Mejlis resolutions (Turkmen/Russian) from mejlis.gov.tm, Constitution "
             "from court.gov.tm. Case law = Supreme Court Plenum guiding resolutions only (87, 1997-2025).")
    gaps = (
        ("Individual court judgments: not published online (only Supreme Court Plenum guiding "
         "resolutions)"),
        ("Ministry-level regulations and more consolidated texts (Adalat, law.minjust.gov.tm): "
         "needs an account login"),
        "English texts: mejlis.gov.tm's lang=en gives Russian titles; not published online",
        "Very large acts (e.g. Civil Code): mejlis.gov.tm sometimes cuts the page off mid-transfer",
        "Presidential decrees and Cabinet resolutions: not researched yet",
    )
    samples = {"caselaw_query": "jeza", "decision_id": "1997-04-28/5",
               "legislation_query": "Raýat kodeksi", "law_id": "law-384", "provision": "1"}

    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        f = filters or {}
        lang = (f.get("lang") or "tm").lower()
        if lang not in ("tm", "ru"):
            raise BadRequest("lang must be tm or ru")
        typ = (f.get("type") or "").lower()
        if typ and typ not in (*_KINDS, "constitution"):
            raise BadRequest("type must be law, code, decree or constitution")
        span = _years(str(f.get("year") or "").strip())
        words = str(query or "").lower().split()
        hits = []
        if typ in ("", "constitution"):
            c = _const_hit(lang)
            if (not words or any(w[:7] in ("konstit", "конститу") for w in words)) \
                    and _in_years(c.date, span):
                hits.append(c)
        for kind in _KINDS:
            if typ and typ != kind:
                continue
            for row in await _list(kind, lang):
                title = _http.clean(row.get(f"title_{lang}") or "")
                date = _http.iso_date(row.get("published_date", ""))
                if words and not all(w in title.lower() for w in words):
                    continue
                if not _in_years(date, span):
                    continue
                hits.append(LawHit(id=f"{kind}-{row['id']}" + ("-ru" if lang == "ru" else ""),
                                   title=title, type=_KINDS[kind][2 if lang == "tm" else 3], date=date,
                                   url=f"{MEJLIS}/{_KINDS[kind][1]}/{row['id']}?lang={lang}"))
        hits =[h for h in hits if h.type in ("Konstitusiýa", "Конституция")] + \
            sorted([h for h in hits if h.type not in ("Konstitusiýa", "Конституция")],
                   key=lambda h: h.date, reverse=True)
        start = (page - 1) * limit
        return Results(hits[start:start + limit], total=len(hits),
                       note="Titles only are searched (titles rarely contain words like 'Kanun' or "
                            "'Karary'); to list acts by year or type, leave the query empty and use the "
                            "type and year filters. Dates are as listed by mejlis.gov.tm.")

    async def get_legislation_toc(self, id):
        title, url, _, paras, _, _ = await _doc(id)
        items = _structure(paras)
        ranks = sorted({it["rank"] for it in items if it["kind"] == "sect"})
        entries = [TocEntry(title=it["title"][:200],
                            level=ranks.index(it["rank"]) if it["kind"] == "sect" else len(ranks),
                            provision=it.get("label", "")) for it in items]
        if not entries:
            entries = [TocEntry(title="(no articles: whole text only)", level=0)]
        return Toc(id=id, title=title, url=url, entries=entries)

    async def get_legislation_provision(self, id, provision):
        title, url, _, paras, _, as_of = await _doc(id)
        want = _norm_prov(provision)
        if not want:
            raise BadRequest("provision is an article number, e.g. 5, 6-1 or 1:3 (see the TOC)")
        for it in _structure(paras):
            if it.get("label") == want:
                return Provision(law_id=id, law_title=title, provision=want,
                                 text="\n\n".join(paras[it["i"]:it["end"]]), url=url, as_of=as_of)
        raise NotFound(f"no article {provision!r} in {id} (see get_legislation_toc)")

    async def get_legislation_text(self, id):
        title, url, date, paras, meta, as_of = await _doc(id)
        return LawText(id=id, title=title, text="\n\n".join(paras), url=url, as_of=as_of,
                       metadata={k: v for k, v in meta.items() if v})

    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        span = _years(str((filters or {}).get("year") or "").strip())
        url, items = await _plenum_items()
        words = str(query or "").lower().split()
        ranked = []
        for it in items:
            if not _in_years(it["date"], span):
                continue
            t, body = it["title"].lower(), it["text"].lower()
            if words and not all(w in t or w in body for w in words):
                continue
            ranked.append((not all(w in t for w in words), -int(it["date"].replace("-", "")), it))
        ranked.sort(key=lambda x: x[:2])
        out = []
        for _, _, it in ranked[(page - 1) * limit:page * limit]:
            snip = ""
            if words:
                k = it["text"].lower().find(words[0])
                if k >= 0:
                    snip = _http.clean(it["text"][max(0, k - 100):k + 200])
            out.append(DecisionHit(id=it["id"], title=it["title"], court=PLENUM, date=it["date"],
                                   case_number=f"karar № {it['number']}", snippet=snip, url=url))
        note = ("Supreme Court Plenum guiding resolutions (as amended to 05.11.2025), "
                "not individual judgments; full text is searched.")
        if re.search("[\u0400-\u04ff]", str(query or "")):
            note += (" The collection is in Turkmen only (its 'Russian' PDF is the same Turkmen "
                     "file): search with Turkmen words, e.g. 'miras' for inheritance.")
        return Results(out, total=len(ranked), note=note)

    async def get_decision(self, id):
        s = str(id or "").strip()
        m = _DEC_ID.match(s)
        if m:
            key = s
        else:
            m = _DEC_ALT.match(s)
            if not m:
                raise BadRequest("decision id is YYYY-MM-DD/N (date/resolution number), e.g. 1997-04-28/5")
            key = f"{m[3]}-{int(m[2]):02d}-{int(m[1]):02d}/{m[4]}"
        url, items = await _plenum_items()
        it = next((x for x in items if x["id"] == key), None)
        if not it:
            raise NotFound(f"no Plenum resolution {key} in the collection")
        return Decision(id=it["id"], title=it["title"], text=it["text"], url=url, court=PLENUM,
                        date=it["date"], case_number=f"karar № {it['number']}",
                        metadata={"Collection": "Türkmenistanyň Ýokary kazyýetiniň Plenumynyň "
                                                "kararlarynyň ýygyndysy (amended to 05.11.2025)",
                                  "PDF pages": it["pages"],
                                  "Note": "Article numbers cited in a resolution are those of the act "
                                          "when it was adopted or amended; codes may since have been "
                                          "renumbered or replaced (e.g. the Civil Code, code-6, is "
                                          "dated 2025-06-28). Check the cited article against "
                                          "get_legislation_toc before relying on it."})
