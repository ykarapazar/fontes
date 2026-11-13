"""Bahrain: legislation and Constitutional Court judgments from the Legislation and Legal
Opinion Commission (هيئة التشريع والرأي القانوني, LLOC), www.lloc.gov.bh.

Gotchas this code encodes (verified 2026-11-06 from a UK IP):
  * legalaffairs.gov.bh (the old name) answers 403 from an AWS load balancer to any
    non-browser client; www.legalaffairs.gov.bh has a bad TLS cert. The live site is
    www.lloc.gov.bh (ASP.NET MVC, no robots.txt).
  * Search is POST /legislation/search with the body '{PostParam: {...}, PageNum: n,
    PageSize: n}' (not strict JSON), a RequestVerificationToken header taken from the
    search page (#token, paired with the antiforgery cookie) and X-Requested-With. Without
    those it answers 200 with a "page not available" page. Keywords need >= 3 letters.
  * One database holds every instrument; TypeID picks the kind (K law/decree-law, D decree,
    O royal order, R decision, CC Constitutional Court judgment, ...).
  * Ids are the source's own: type letter(s) + number + 2-digit year (L1901 = decree-law
    19/2001; CC ids are a sequence + publication year). /Legislation/id/<id> is the record
    page; /Legislation/HTM/<id> the text as published (Word HTML); /FullAr/<id>.docx the
    consolidated text ("with amendments"). An amending law's FullAr link points to the
    *amended* law's docx, so it is only used when its id equals the requested id.
  * Article headings are padded with tatweel and spaces ("مـــادة ( 91 )"), decree articles
    use ordinal words ("المادة الأولى"). Labels: "91", "5 مكرر", "الأولى".
  * The record date in lists is the Official Gazette publication date, not the judgment date.
"""
from __future__ import annotations

import io
import json
import re
import zipfile
from html import unescape

from lxml import etree

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

HOST = "https://www.lloc.gov.bh"
SEARCH_PAGE = f"{HOST}/Legislation/Search"
SEARCH = f"{HOST}/legislation/search"
RECORD = HOST + "/Legislation/id/{id}"
HTM = HOST + "/Legislation/HTM/{id}"

_ID = re.compile(r"^[A-Z]{1,2}\d{3,}$")
# Type codes of the search form (legislation type filter) -> label
_TYPES = {"K": "قانون أو مرسوم بقانون", "O": "أمر ملكي أو أميري", "D": "مرسوم", "R": "قرار",
          "C": "تعميم", "N": "إعلان", "B": "بيان", "OT": "اخرى"}
_AR_MONTHS = {m: i for i, m in enumerate((
    "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر",
    "نوفمبر", "ديسمبر"), 1)}
_AR_MONTHS.update({"ابريل": 4, "إبريل": 4, "اغسطس": 8, "أغسطس": 8, "اكتوبر": 10})
_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")
_INVISIBLE = re.compile("[​-‏‪-‮﻿]")
_W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

_token: list[str] = []          # the search page's antiforgery token (cookie is in the client)
_laws: dict = {}                # id -> parsed record (small LRU)


# --------------------------------------------------------------------------- #
# Text helpers
# --------------------------------------------------------------------------- #
def _light(s: str) -> str:
    """Heading text as shown: no tatweel, markdown marks or harakat; Western digits."""
    s = _INVISIBLE.sub("", s).replace("ـ", "").translate(_DIGITS)
    s = re.sub("[*#_ً-ْ]", "", s)  # markdown, harakat / tanween
    return re.sub(r"\s+", " ", s).strip()


def _norm(s: str) -> str:
    """For matching only: _light plus unified alif / ta marbuta / ya."""
    return re.sub("[أإآ]", "ا", _light(s)).replace("ة", "ه").replace("ى", "ي")


def _ar_date(s: str) -> str:
    """'17-سبتمبر-2026' or '31 يناير 2024' -> '2026-09-17'; else ''."""
    m = re.search(r"(\d{1,2})\s*[-\s]\s*([ء-ي]+)\s*[-\s]\s*(\d{4})", (s or "").translate(_DIGITS))
    if not m or m[2] not in _AR_MONTHS:
        return ""
    return f"{m[3]}-{_AR_MONTHS[m[2]]:02d}-{int(m[1]):02d}"


def _clean_md(paras: list[str]) -> list[str]:
    return [p for p in (_INVISIBLE.sub("", p).strip() for p in paras) if p]


# Article heading: "مادة (5)", "المادة 5 مكرراً (أ)", "المادة الأولى", "المادة الحادية عشرة:"
_ART_NUM = re.compile(r"^(?:ال)?ماد[هة]\s*\(?\s*(\d+)\s*\)?\s*(مكرر[اً]*\s*(?:\(\s*[ء-ي]\s*\))?)?"
                      r"\s*(?:$|[:.\-–])")
_ART_WORD = re.compile(r"^(?:ال)?ماد[هة]\s+(ال\S+(?:\s+(?:و|بعد\s+)?ال\S+){0,2})\s*(مكرر[اً]*)?\s*(?:$|[:.\-–])")
_STRUCT = {"الكتاب": 0, "الجزء": 0, "الباب": 1, "الفصل": 2, "الفرع": 3, "القسم": 3}
_STRUCT_RE = re.compile(r"^(الكتاب|الجزء|الباب|الفصل|الفرع|القسم)\s+\S+")


def _article_label(para: str) -> str:
    n = _light(para)
    m = _ART_NUM.match(n)
    if m:
        bis = re.sub(r"\s+", " ", (m[2] or "")).strip()
        if bis:
            bis = "مكرر" + (" " + re.sub(r"\s", "", bis[bis.find("("):]) if "(" in bis else "")
        return f"{m[1]} {bis}".strip()
    m = _ART_WORD.match(n)
    if m and len(n) < 60:
        return (m[1] + (" مكرر" if m[2] else "")).strip()
    return ""


def _struct_level(para: str) -> int | None:
    n = _norm(para)
    m = _STRUCT_RE.match(n)
    if m and len(n) <= 60 and not n.endswith((".", "،")):
        return _STRUCT[m[1]]
    return None


def _wanted(provision: str) -> str:
    """User input ('Madde 5', 'art. 5', 'المادة (5)', '٥', 'المادة الأولى') -> comparable key."""
    s = _norm(provision)
    s = re.sub(r"^(?:ال)?ماد[هة]\s*", "", s)
    s = re.sub(r"^(?:art(?:icle)?\.?|madde|m\.|م\.?)\s*(?=\d)", "", s, flags=re.I)
    return _key(s)


def _key(label: str) -> str:
    s = _norm(label)
    s = re.sub(r"مكرر[اً]*", "مكرر", s)
    return re.sub(r"[\s()]", "", s)


# --------------------------------------------------------------------------- #
# Documents
# --------------------------------------------------------------------------- #
def _docx_paragraphs(data: bytes) -> tuple[list[str], str]:
    """Consolidated .docx -> (paragraphs, last-modified ISO date). Footnotes (amendment
    notes) are inlined in brackets where they are referenced; text boxes are skipped."""
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
        doc = etree.fromstring(z.read("word/document.xml"))
        notes = {}
        if "word/footnotes.xml" in z.namelist():
            for fn in etree.fromstring(z.read("word/footnotes.xml")).iter(_W + "footnote"):
                t = _http.clean("".join(x.text or "" for x in fn.iter(_W + "t")))
                if t:
                    notes[fn.get(_W + "id")] = t
        modified = ""
        if "docProps/core.xml" in z.namelist():
            m = re.search(rb"<dcterms:modified[^>]*>(\d{4}-\d{2}-\d{2})", z.read("docProps/core.xml"))
            modified = m[1].decode() if m else ""
    except (zipfile.BadZipFile, KeyError, etree.XMLSyntaxError) as e:
        raise SourceError(f"LLOC consolidated text is not a readable .docx ({e})") from e

    def ptext(p) -> str:
        out = []
        for el in p.iter(_W + "t", _W + "tab", _W + "br", _W + "footnoteReference"):
            if el.tag == _W + "t":
                out.append(el.text or "")
            elif el.tag == _W + "footnoteReference":
                note = notes.get(el.get(_W + "id"), "")
                note = re.sub(r"^\(\s*\)\s*", "", note)
                if note:
                    out.append(f" [{note}]")
            else:
                out.append(" ")
        return _http.clean("".join(out))

    paras = []
    body = doc.find(_W + "body")
    for el in (body if body is not None else []):
        if el.tag == _W + "p":
            if el.find(".//" + _W + "txbxContent") is not None:
                continue  # decorative text box: its text repeats nearby
            t = ptext(el)
            if t and el.find(f"{_W}pPr/{_W}numPr") is not None:
                t = "- " + t  # Word auto-numbering (أ، ب، 1، 2): the letters are not in the text
            if t:
                paras.append(t)
        elif el.tag == _W + "tbl":
            rows = []
            for tr in el.iter(_W + "tr"):
                cells = [" ".join(t for t in (ptext(p) for p in tc.iter(_W + "p")) if t)
                         for tc in tr.iter(_W + "tc")]
                if any(cells):
                    rows.append(cells)
            if rows and max(len(r) for r in rows) == 1:
                paras += [r[0] for r in rows if r[0]]
            elif rows:
                width = max(len(r) for r in rows)
                lines = ["| " + " | ".join(r + [""] * (width - len(r))) + " |" for r in rows]
                lines.insert(1, "|" + " --- |" * width)
                paras.append("\n".join(lines))
    return _clean_md(paras), modified


async def _fetch(url: str) -> "httpx.Response":  # noqa: F821
    r = await _http.get(url)
    if r.status_code == 404:
        raise NotFound(f"LLOC has no file at {url}")
    if r.status_code != 200:
        raise SourceError(_http.error("LLOC", f"GET {url}", r.status_code), r.status_code)
    return r


def _check_id(id: str) -> str:
    i = (id or "").strip().upper()
    i = re.sub(r"^.*/(?:ID|HTM)/", "", i)
    if not _ID.match(i):
        raise BadRequest(f"Bad LLOC id {id!r}: expected the source's id, e.g. 'L1901' "
                         "(decree-law 19/2001, the Civil Code) or 'CC0124' (a Constitutional "
                         "Court judgment); search_legislation / search_caselaw return them.")
    return i


def _parse_items(html: str) -> list[dict]:
    """Result list (search or record page) -> one dict per record."""
    out = []
    for chunk in re.split(r'<div class="legislation (?:even|odd)">', html)[1:]:
        title = _http.clean(unescape(re.search(r'class="ArTitle">([^<]*)', chunk)[1])) \
            if 'class="ArTitle"' in chunk else ""
        m = re.search(r'href="/(?:PDF/|Legislation/HTM/|FullEn/)([A-Za-z]+\d+)', chunk)
        if not m or not title:
            continue
        rid = m[1].upper()
        en = re.search(r'class="EnTitle">([^<]*)', chunk)
        dt = re.search(r'class="dt">.*?class="hvalue">([^<]*)', chunk, re.S)
        og = re.search(r'class="og">.*?class="hvalue">([^<]*)', chunk, re.S)
        links = re.findall(r'href="(/(?:PDF|FullAr|FullEn)/[^"]+|/Legislation/HTM/[^"]+)"', chunk)
        amends = re.findall(r'href="/Legislation/id/([A-Za-z]+\d+)"[^>]*>([^<]*)', chunk)
        out.append({
            "id": rid, "title": title,
            "en_title": _http.clean(unescape(en[1])) if en else "",
            "date": _ar_date(dt[1]) if dt else "",
            "og": _http.clean(og[1]) if og else "",
            "pdf": next((HOST + u for u in links if u.startswith("/PDF/")), ""),
            "htm": next((HOST + u for u in links if u.startswith("/Legislation/HTM/")), ""),
            "full_ar": next((HOST + u for u in links if u.upper() == f"/FULLAR/{rid}.DOCX"), ""),
            "full_ar_other": next((u.split("/")[-1].split(".")[0] for u in links
                                   if u.startswith("/FullAr/") and u.upper() != f"/FULLAR/{rid}.DOCX"), ""),
            "full_en": next((HOST + u for u in links if u.upper() == f"/FULLEN/{rid}.DOCX"), ""),
            "amends": [(a.upper(), _http.clean(unescape(t))) for a, t in amends],
        })
    return out


def _number(title: str) -> str:
    m = re.search(r"رقم\s*\(?\s*([\d.]+)\s*\)?\s*لسنة\s*(\d{4})", title.translate(_DIGITS))
    return f"{m[1]}/{m[2]}" if m else ""


def _type(title: str) -> str:
    m = re.match(r"^(.*?)\s+رقم\b", title)
    return m[1] if m else ""


# --------------------------------------------------------------------------- #
# Search
# --------------------------------------------------------------------------- #
async def _get_token(refresh: bool = False) -> str:
    if _token and not refresh:
        return _token[0]
    r = await _fetch(SEARCH_PAGE)
    m = re.search(r'id="token" value="([^"]+)"', r.text)
    if not m:
        raise SourceError("LLOC search page has no request token (layout changed?)")
    _token[:] = [m[1]]
    return m[1]


async def _search(query: str, *, types: str, limit: int, page: int, filters: dict) -> tuple[list[dict], int | None]:
    query = _http.clean(query)
    phrase = ""
    if len(query) > 1 and query[0] == query[-1] == '"':
        phrase, query = query[1:-1].strip(), ""
    for w in (query, phrase):
        if w and len(w) < 3:
            raise BadRequest("LLOC needs a search term of at least 3 letters.")
    years = {}
    for k, field in (("year_from", "YearFrom"), ("year_to", "YearTo"), ("number", "LegNum")):
        v = str(filters.get(k, "") or "").strip()
        if v and not v.isdigit():
            raise BadRequest(f"{k} must be a whole number, got {v!r}")
        years[field] = v
    search_in = (filters.get("search_in") or "title").strip().lower()
    if search_in not in ("title", "text"):
        raise BadRequest("search_in must be 'title' or 'text'")
    if not (query or phrase or any(years.values()) or types == "CC"):
        raise BadRequest("Give a query (>= 3 letters, Arabic) or a number / year filter.")
    params = {"IsSearchTitle": search_in == "title", "LegNum": years["LegNum"],
              "YearFrom": years["YearFrom"], "YearTo": years["YearTo"], "OGFrom": "", "OGTo": "",
              "TypeID": types, "SourceID": "", "CategoryID": "", "KeywordAll": query,
              "KeywordAny": "", "KeywordPhrase": phrase, "KeywordNot": "", "IsSearchTreaty": False,
              "IsSearchWomen": False, "IsSearchEnglish": False, "SortBy": "SortDate"}
    body = ("{PostParam: " + json.dumps(params, ensure_ascii=False)
            + f", PageNum: {max(1, int(page))}, PageSize: {max(1, min(int(limit), 50))}}}")
    for attempt in (1, 2):
        tok = await _get_token(refresh=attempt == 2)
        r = await _http.post(SEARCH, content=body.encode("utf-8"), headers={
            "Content-Type": "application/json; charset=utf-8", "RequestVerificationToken": tok,
            "X-Requested-With": "XMLHttpRequest", "Referer": SEARCH_PAGE})
        if r.status_code == 499:  # the site's own "no records" status
            return [], 0
        if r.status_code != 200:
            raise SourceError(_http.error("LLOC", "search", r.status_code), r.status_code)
        if "<!DOCTYPE" not in r.text[:500]:
            break
    else:
        raise SourceError("LLOC search answered with its 'page not available' page (token rejected?)")
    m = re.search(r'class="results">[^<(]*\(\s*(\d+)', r.text)
    total = int(m[1]) if m else None
    return _parse_items(r.text)[:limit], total


# --------------------------------------------------------------------------- #
# Records
# --------------------------------------------------------------------------- #
async def _record(rid: str) -> dict:
    r = await _fetch(RECORD.format(id=rid))
    items = [i for i in _parse_items(r.text) if i["id"] == rid]
    if not items:
        raise NotFound(f"LLOC has no record {rid!r} (search_legislation / search_caselaw give valid ids).")
    return items[0]


async def _load(rid: str) -> dict:
    """Record + text paragraphs: consolidated docx if LLOC has one for this id, else the
    text as published (HTM), else the PDF's text layer."""
    if rid in _laws:
        return _laws[rid]
    rec = await _record(rid)
    paras, as_of, version = [], "", ""
    if rec["full_ar"]:
        r = await _fetch(rec["full_ar"])
        paras, as_of = _docx_paragraphs(r.content)
        version = "consolidated text with amendments (LLOC .docx)"
    if not paras:
        url = rec["htm"] or HTM.format(id=rid)
        r = await _http.get(url)
        if r.status_code == 200 and len(r.text) > 500:
            paras = _clean_md(_http.html_paragraphs(r.text))
            as_of, version = rec["date"], "text as published in the Official Gazette (not consolidated)"
    if not paras and rec["pdf"]:
        r = await _fetch(rec["pdf"])
        txt = _http.pdf_text(r.content)
        paras = _clean_md(txt.split("\n"))
        as_of, version = rec["date"], "text layer of the published PDF (not consolidated)"
    if not paras:
        raise SourceError(f"LLOC has no readable text for {rid} (scanned PDF only: {rec['pdf']})")
    rec = dict(rec, paras=paras, as_of=as_of, version=version)
    return _http.lru_put(_laws, rid, rec, 8)


def _sections(paras: list[str]) -> tuple[list[TocEntry], dict[str, tuple[int, int]], list[str]]:
    """TOC entries, provision key -> (start, end) paragraph span, and markdown paragraphs."""
    entries, spans, md = [], {}, []
    heads = []                     # (index, kind, label/level)
    i = 0
    while i < len(paras):
        p = paras[i]
        label = _article_label(p)
        lvl = None if label else _struct_level(p)
        if label:
            heads.append((len(md), "art", label))
            md.append(f"**{p.strip('*# ')}**" if len(_norm(p)) < 60 else p)
        elif lvl is not None:
            title = p.strip("*# ")
            nxt = paras[i + 1] if i + 1 < len(paras) else ""
            if nxt and len(_norm(nxt)) < 60 and not _article_label(nxt) and _struct_level(nxt) is None \
                    and not _norm(nxt).endswith((".", "،", ":")):
                title += " - " + nxt.strip("*# ")
                i += 1
            heads.append((len(md), "struct", lvl))
            md.append("#" * min(lvl + 2, 5) + " " + title)
        else:
            md.append(p)
        i += 1
    cur, seen = -1, {}
    for n, (idx, kind, val) in enumerate(heads):
        if kind == "struct":
            cur = val
            entries.append(TocEntry(md[idx].lstrip("# "), level=val))
            continue
        end = next((h[0] for h in heads[n + 1:]), len(md))
        label = val
        seen[_key(label)] = seen.get(_key(label), 0) + 1
        if seen[_key(label)] > 1:
            label = f"{val} ({seen[_key(val)]})"
        spans[_key(label)] = (idx, end)
        entries.append(TocEntry(md[idx].strip("*"), level=cur + 1, provision=label))
    return entries, spans, md


class Bahrain(Jurisdiction):
    code = "bh"
    name = "Bahrain"
    languages = ("ar",)
    aliases = ("bahrain", "البحرين", "mamlakat al-bahrayn")
    sources = (
        Source("Legislation and Legal Opinion Commission (هيئة التشريع والرأي القانوني), lloc.gov.bh",
               HOST, covers=("legislation", "caselaw"),
               licence="Site terms: content is copyright LLOC; modifying it or using it 'for any other "
                       "purposes' is called an infringement. Separately, Bahraini copyright law (22/2006 art. "
                       "4(b)) excludes legislation and judgments from copyright, but that does not "
                       "lift the site's terms on automated use: reuse still needs LLOC's permission.",
               commercial_use=None, ai_use=None, auth="none",
               rate_limit="unknown; 1 s spacing, no 429 seen in ~40 requests (2026-11)",
               terms_url=f"{HOST}/page/الشروط والاحكام",
               warning="LLOC's terms reserve copyright and forbid modifying content or using it 'for "
                       "other purposes'; texts are passed on unmodified for reference. Check the "
                       "official PDF before relying on them. Even with permission this source holds "
                       "legislation and Constitutional Court judgments only, not Court of Cassation "
                       "judgments.",
               needs_permission=True),
    )
    legislation_filters = {
        "type": "comma-separated LLOC type codes: K (law / decree-law), D (decree), O (royal/amiri "
                "order), R (decision), C (circular), N (announcement), B (statement), OT (other). "
                "Default: all of these.",
        "number": "instrument number, e.g. 19 (combine with year_from/year_to = 2001)",
        "year_from": "year of issue, from (YYYY)",
        "year_to": "year of issue, to (YYYY)",
        "search_in": "title (default) | text (full text)",
    }
    caselaw_filters = {
        "year_from": "year, from (YYYY)",
        "year_to": "year, to (YYYY)",
        "search_in": "title (default; the title holds only the case number) | text (full text)",
    }
    min_interval = {"www.lloc.gov.bh": 1.0}
    notes = ("Arabic. LLOC database of all Bahraini legislation (consolidated .docx where LLOC has "
             "one, else the text as published) and Constitutional Court judgments. No official "
             "open source for Court of Cassation judgments.")
    gaps = (
        ("Everything (lloc.gov.bh): terms forbid using content 'for any other purposes'; needs "
         "permission, off by default"),
        "Court of Cassation and lower-court judgments: no official open source found",
        ("English translations, treaties and legal opinions (LLOC /Legislation/English, /Treaty, "
         "/LegalOpinion): not built yet"),
        "Consolidated text where LLOC has no .docx: not published (text as published only)",
    )
    samples = {
        "legislation_query": "القانون المدني",
        "law_id": "L1901",
        "provision": "1",
        "caselaw_query": "دستورية",
        "decision_id": "CC0124",
    }

    # ---------------- legislation ----------------
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        raw = (filters.get("type") or "").upper().replace(" ", "")
        codes = [c for c in raw.split(",") if c]
        bad = [c for c in codes if c not in _TYPES]
        if bad:
            raise BadRequest(f"Unknown type {bad}; use {', '.join(_TYPES)}")
        items, total = await _search(query, types=",".join(codes or _TYPES), limit=limit, page=page,
                                     filters=filters)
        hits = [LawHit(id=i["id"], title=i["title"], type=_type(i["title"]), number=_number(i["title"]),
                       date=i["date"], snippet=f"Official Gazette no. {i['og']}" if i["og"] else "",
                       url=RECORD.format(id=i["id"])) for i in items]
        return Results(hits, total, note="Arabic only; words are AND-ed, \"quotes\" = exact phrase; "
                                         "searches titles unless search_in=text. Date = Official Gazette date.")

    async def get_legislation_text(self, id):
        law = await _load(_check_id(id))
        _, _, md = _sections(law["paras"])
        meta = {"version": law["version"], "official_gazette": law["og"], "pdf": law["pdf"]}
        if law["en_title"]:
            meta["english_title"] = law["en_title"]
        if law["full_en"]:
            meta["english_translation"] = law["full_en"]
        if law["full_ar_other"]:
            meta["consolidated_text_of_amended_law"] = law["full_ar_other"]
        for n, (aid, t) in enumerate(law["amends"], 1):
            meta[f"amends_{n}"] = f"{aid}: {t}"
        return LawText(id=law["id"], title=law["title"], text="\n\n".join(md),
                       url=RECORD.format(id=law["id"]), as_of=law["as_of"],
                       metadata={k: v for k, v in meta.items() if v})

    async def get_legislation_toc(self, id):
        law = await _load(_check_id(id))
        entries, _, _ = _sections(law["paras"])
        if not entries:
            raise NotFound(f"{law['id']} has no article headings; use get_legislation_text.")
        return Toc(id=law["id"], title=law["title"], url=RECORD.format(id=law["id"]), entries=entries)

    async def get_legislation_provision(self, id, provision):
        law = await _load(_check_id(id))
        entries, spans, md = _sections(law["paras"])
        key = _wanted(str(provision))
        if key not in spans:
            labels = [e.provision for e in entries if e.provision]
            raise NotFound(f"No article {provision!r} in {law['id']}. Labels look like: "
                           f"{', '.join(labels[:8])}{' …' if len(labels) > 8 else ''}")
        a, b = spans[key]
        label = next(e.provision for e in entries if e.provision and _key(e.provision) == key)
        return Provision(law_id=law["id"], law_title=law["title"], provision=label,
                         text="\n\n".join(md[a:b]), url=RECORD.format(id=law["id"]), as_of=law["as_of"])

    # ---------------- case law (Constitutional Court) ----------------
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        items, total = await _search(query, types="CC", limit=limit, page=page, filters=filters or {})
        hits = []
        for i in items:
            m = re.search(r"رقم\s+(.+)$", i["title"])
            num = re.sub(r"\s*/\s*", "/", m[1]).strip() if m else ""
            hits.append(DecisionHit(id=i["id"], title=i["title"], court="المحكمة الدستورية",
                                    date=i["date"], case_number=num,
                                    snippet=f"Official Gazette no. {i['og']}" if i["og"] else "",
                                    url=RECORD.format(id=i["id"])))
        return Results(hits, total, note="Constitutional Court only. Hit date = Official Gazette "
                                         "publication date; get_decision gives the judgment date. "
                                         "Titles hold only the case number: use search_in=text for topics.")

    async def get_decision(self, id):
        rid = _check_id(id)
        if not rid.startswith("CC"):
            raise BadRequest(f"{rid} is not a Constitutional Court judgment (ids start with CC); "
                             "use get_legislation_text for legislation.")
        d = await _load(rid)
        text = "\n\n".join(d["paras"])
        head = _norm(" ".join(d["paras"][:6]))
        m = re.search(r"(\d{1,2}\s+[ء-ي]+\s+\d{4})\s*م", head)
        date = _ar_date(m[1]) if m else ""
        m = re.search(r"رقم\s+(.+)$", d["title"])
        num = re.sub(r"\s*/\s*", "/", m[1]).strip() if m else ""
        meta = {"official_gazette": d["og"], "published": d["date"], "pdf": d["pdf"],
                "english_title": d["en_title"], "english_translation": d["full_en"]}
        return Decision(id=rid, title=d["title"], text=text, url=RECORD.format(id=rid),
                        court="المحكمة الدستورية", date=date or d["date"], case_number=num,
                        metadata={k: v for k, v in meta.items() if v})
