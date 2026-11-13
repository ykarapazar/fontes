"""Georgia: legislation from the Legislative Herald (Matsne), case law from the courts'
decision database (ECD) plus Constitutional Court decisions published in Matsne.

Gotchas this code encodes (verified 2026-11-05 from a UK IP):
  * matsne.gov.ge robots.txt sets Crawl-delay: 10, so Matsne calls are spaced 10 s apart.
    /search/ is disallowed there; /{lang}/document/search and /document/view are not.
  * Matsne document ids are numeric (Civil Code = 31702). /ka/document/view/{id} is the
    current Georgian consolidated text; /en/document/view/{id}?impose=translateEn is the
    Legislative Herald's English translation, when one exists. We expose the English text
    as id "{id}/en" (like fi's "/swe"); we never translate.
  * An unknown Matsne id answers HTTP 200 with an "Access Denied" page.
  * Matsne search in /en/ matches English titles, so it only finds translated acts.
  * Superscript article numbers (მუხლი 18<sup>1</sup>) are kept as "18¹".
  * ECD (ecd.court.ge) is a JSON POST API behind the public search page. Its id is
    "{instance}-{documentId}" (1 = first instance, 2 = appeal, 3 = Supreme Court). It only
    holds decisions dated 2018-01 to 2020-04 (~44.5k); nothing newer. Texts are anonymised
    and come as plain text. DecisionDate can differ from the date printed in the decision.
  * supremecourt.ge has its own search, but robots.txt disallows /ka/getCases*, so it is
    not used.
"""
from __future__ import annotations

import datetime
import re
from urllib.parse import urlencode

import lxml.html

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

MATSNE = "https://matsne.gov.ge"
ECD = "https://ecd.court.ge"

_SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
_UNSUP = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")
_STATUS = {"in_force": "active", "expired": "expired", "pending": "toBeActivated"}
_STATUS_LABEL = {"panel-success": "in force", "panel-info": "not yet in force",
                 "panel-danger": "expired"}
_GROUPS = {"law": "1000003", "constitutional_court": "1093052", "treaty": "1319499",
           "resolution": "458", "order": "1000006", "edict": "1000005", "decree": "1065776",
           "presidential_decree": "4829717", "eu_law": "3591321"}
_WINDOW = 100  # Matsne's largest page size
_INSTANCES = {"first": 1, "appeal": 2, "supreme": 3}
_CATEGORIES = {"criminal": 1, "civil": 2, "administrative": 3}

# Article headings: "მუხლი 18¹. title" (Georgian), "Article 18¹ – title" (English).
_ART = re.compile(r"^(?:მუხლი|Article)\s+(\d+[⁰¹²³⁴⁵⁶⁷⁸⁹]*)(?=[\s.:–—-]|$)")
_HEAD = re.compile(r"^(წიგნი|კარი|ნაწილი|თავი|განყოფილება|ქვეთავი|"
                   r"Book|Part|Title|Chapter|Section|Subsection)\b", re.I)
_HEAD_LEVEL = {"წიგნი": 0, "book": 0, "კარი": 1, "ნაწილი": 1, "part": 1, "title": 1,
               "თავი": 2, "chapter": 2, "განყოფილება": 3, "ქვეთავი": 3, "section": 3,
               "subsection": 3}
_KA_MONTHS = {"იანვ": 1, "თებერ": 2, "მარტ": 3, "აპრილ": 4, "მაის": 5, "ივნის": 6,
              "ივლის": 7, "აგვისტ": 8, "სექტემბ": 9, "ოქტომბ": 10, "ნოემბ": 11, "დეკემბ": 12}

_docs: dict = {}


# --------------------------------------------------------------------------- #
# Matsne
# --------------------------------------------------------------------------- #
def _parse_matsne_id(raw: str) -> tuple[str, str]:
    """'31702', '31702/en', 'en:31702' or a matsne URL -> (id, 'ka'|'en')."""
    s = str(raw or "").strip()
    m = re.search(r"matsne\.gov\.ge/(ka|en)/document/view/(\d+)(\?impose=translateEn)?", s)
    if m:
        return m[2], ("en" if m[3] else "ka")
    m = re.fullmatch(r"(?:(ka|en):)?(\d+)(?:/(ka|en))?", s, re.I)
    if not m:
        raise BadRequest(f"Bad Matsne id {raw!r}: use the numeric document id, e.g. '31702' "
                         "(Civil Code, Georgian) or '31702/en' (its English translation).")
    return m[2], (m[1] or m[3] or "ka").lower()


def _make_id(num: str, lang: str) -> str:
    return f"{num}/en" if lang == "en" else num


def _doc_url(num: str, lang: str) -> str:
    if lang == "en":
        return f"{MATSNE}/en/document/view/{num}?impose=translateEn"
    return f"{MATSNE}/ka/document/view/{num}"


def _strip_bold(p: str) -> str:
    return _http.clean(p.replace("**", ""))


async def _matsne_get(url: str) -> str:
    r = await _http.get(url)
    if r.status_code != 200:
        raise SourceError(_http.error("Matsne", "request failed", r.status_code), r.status_code)
    return r.text


async def _doc(num: str, lang: str) -> dict:
    """Fetch and parse one Matsne document page (cached in-process, a few docs)."""
    key = (num, lang)
    if key in _docs:
        return _docs[key]
    html = await _matsne_get(_doc_url(num, lang))
    if "<title>Access Denied</title>" in html[:500]:
        raise NotFound(f"Matsne has no document {num} (it answered 'Access Denied', which it "
                       "does for unknown ids).")
    if 'id="maindoc"' not in html:
        raise SourceError("Matsne: document page without a document body (layout changed?)", 200)
    if lang == "en" and 'impose=translateEn">' not in html:
        raise NotFound(f"Matsne document {num} has no English translation; use id '{num}' "
                       "for the Georgian text.")
    hdr = {}
    m = re.search(r'class="document-header-mini[^"]*">(.*?)</div>\s*</div>', html, re.S)
    if m:
        cells = re.findall(r'<div[^>]*title="([^"]*)">(.*?)</div>', m[0], re.S)
        keys = ("number", "date", "published", "regcode", "title", "issuer")
        hdr = {k: _http.clean(re.sub(r"<[^>]+>", "", v)) for k, (_, v) in zip(keys, cells)}
    as_of = re.search(r'class="active list-group-item">([^<]*)<', html)
    html = re.sub(r"<sup>\s*(\d+)\s*</sup>", lambda x: x[1].translate(_SUP), html)
    root = lxml.html.fromstring(html)
    main = root.get_element_by_id("maindoc")
    for a in main.xpath('.//a[@class="hide"]'):
        a.drop_tree()
    paras = _http.html_paragraphs(lxml.html.tostring(main, encoding="unicode"))
    t = re.search(r"<title>(.*?)\s*\|", html, re.S)
    title = (hdr.get("title") if lang == "ka" else "") or (_http.clean(t[1]) if t else "") \
        or hdr.get("title") or f"Matsne {num}"
    doc = {"id": _make_id(num, lang), "num": num, "lang": lang, "title": title,
           "url": _doc_url(num, lang), "paras": paras, "hdr": hdr,
           "as_of": _http.iso_date(as_of[1].strip()) if as_of else ""}
    doc["entries"], doc["spans"] = _structure(paras)
    return _http.lru_put(_docs, key, doc, 4)


def _structure(paras: list[str]) -> tuple[list[TocEntry], dict[str, tuple[int, int]]]:
    """TOC entries and article spans (label -> paragraph range) from the paragraphs."""
    entries: list[TocEntry] = []
    spans: dict[str, tuple[int, int]] = {}
    open_label, open_start, head_level = None, 0, -1
    i = 0

    def close(end):
        if open_label:
            spans[open_label] = (open_start, end)

    while i < len(paras):
        p = _strip_bold(paras[i])
        bold = paras[i].startswith("**")
        art = _ART.match(p)
        head = _HEAD.match(p) if (not art and len(p) < 120
                                  and (bold or not p[0].isascii())) else None
        if art:
            close(i)
            prefix = "Article" if p.startswith("Article") else "მუხლი"
            label = f"{prefix} {art[1]}"
            n = 2
            while label in spans or label == open_label:
                label, n = f"{prefix} {art[1]} ({n})", n + 1
            open_label, open_start = label, i
            entries.append(TocEntry(title=p, level=head_level + 1, provision=label))
        elif head:
            close(i)
            open_label = None
            level = _HEAD_LEVEL.get(head[1].lower(), 1)
            title = p
            nxt = _strip_bold(paras[i + 1]) if i + 1 < len(paras) else ""
            if nxt and len(nxt) < 200 and not _ART.match(nxt) and not _HEAD.match(nxt):
                title, i = f"{p}. {nxt}", i + 1
            head_level = max(head_level, level) if head_level < 0 else level
            entries.append(TocEntry(title=title, level=level))
        i += 1
    close(len(paras))
    return entries, spans


def _norm_provision(raw: str) -> str:
    """'მუხლი 18¹', 'Article 18^1', 'art. 18-1', '18' -> '18¹' / '18'."""
    s = _http.clean(raw).lower()
    s = re.sub(r"^(მუხლი|მუხ\.?|article|art\.?)\s*", "", s)
    m = re.fullmatch(r"(\d+)\s*(?:[\^_-]\s*(\d+)|([⁰¹²³⁴⁵⁶⁷⁸⁹]+))?\.?", s)
    if not m:
        raise BadRequest(f"Bad provision {raw!r}: use an article number such as 'მუხლი 5', "
                         "'Article 5', '5' or '18¹' / '18^1' for inserted articles.")
    return m[1] + ((m[2] or "").translate(_SUP) or m[3] or "")


def _find_label(doc: dict, raw: str) -> str:
    if raw in doc["spans"]:
        return raw
    num = _norm_provision(raw)
    for label in doc["spans"]:
        if label.split(" ", 1)[1] == num:
            return label
    raise NotFound(f"{doc['title']} ({doc['id']}) has no article {raw!r}. "
                   "Use get_legislation_toc to see the article labels.")


async def _matsne_search(lang: str, params: dict, limit: int, page: int) -> tuple[list, int | None]:
    """Run a Matsne document search -> ([(num, title, panel_class, fields, has_en)], total)."""
    params = {**params, "limit": limit, "page": page}
    html = await _matsne_get(f"{MATSNE}/{lang}/document/search?{urlencode(params)}")
    if "document-search-result-items" not in html and "search-result-info" not in html:
        raise SourceError("Matsne: unexpected search page (layout changed or blocked)", 200)
    m = re.search(r"(?:Search count|სულ მოიძებნა):\s*(\d+)", html)
    total = int(m[1]) if m else None
    out = []
    i = html.find("document-search-result-items")
    j = html.find("pagination-wrapper", i)
    body = html[i:j if j > 0 else None] if i >= 0 else ""
    for blk in re.split(r'<div class="panel (?=panel-\w+ document-search-result-item)', body)[1:]:
        a = re.search(r'<p><a href="/\w+/document/view/(\d+)">(.*?)</a></p>', blk, re.S)
        if not a:
            continue
        pb = blk[blk.find("panel-body"):blk.find("panel-footer") if "panel-footer" in blk else None]
        fields = [_http.clean(x) for x in re.findall(r"<small>([^<]*)</small>", pb)]
        fields = [f for f in fields if f and f != "●"]
        title = _http.clean(re.sub(r"<[^>]+>", "", a[2]))
        out.append((a[1], title, blk.split(" ", 1)[0], fields, 'impose=translateEn">' in blk))
    return out, total


def _fields(fields: list[str]) -> dict:
    """[type, issuer, number, date] with number/date optional -> dict."""
    d = {"type": fields[0] if fields else "", "issuer": fields[1] if len(fields) > 1 else ""}
    for f in fields[2:]:
        if re.fullmatch(r"\d{2}/\d{2}/\d{4}", f):
            d["date"] = _http.iso_date(f)
        else:
            d.setdefault("number", f)
    return d


# --------------------------------------------------------------------------- #
# ECD (courts' decision database)
# --------------------------------------------------------------------------- #
async def _ecd(path: str, payload: dict):
    r = await _http.post(f"{ECD}{path}", json=payload)
    if r.status_code != 200:
        raise SourceError(_http.error("ECD", "request failed", r.status_code), r.status_code)
    try:
        js = r.json()
    except ValueError:
        raise SourceError("ECD: response is not JSON (blocked or changed?)", 200) from None
    if not js.get("success"):
        raise SourceError(f"ECD: request refused: {_http.clean(js.get('data'))[:200]}", 200)
    return js.get("data")


def _ecd_url(inst, doc_id) -> str:
    return f"{ECD}/Decision/DecisionDocumentPdf?InstanceId={inst}&DecisionDocumentId={doc_id}"


def _ka_date(text: str) -> str:
    m = re.search(r"(\d{1,2})\s+([ა-ჰ]+),?\s+(\d{4})\s+წ", text) or \
        re.search(r"(\d{4})\s+წლის\s+(\d{1,2})\s+([ა-ჰ]+)", text)
    if not m:
        return ""
    if m.re.pattern.startswith("(\\d{4})"):
        y, d, mon = m[1], m[2], m[3]
    else:
        d, mon, y = m[1], m[2], m[3]
    month = next((n for k, n in _KA_MONTHS.items() if mon.startswith(k)), 0)
    try:
        return datetime.date(int(y), month, int(d)).isoformat() if month else ""
    except ValueError:
        return ""


def _title_rank(title: str, query: str) -> int:
    """0 if the title is the query (optionally with the 'საქართველოს' prefix), else 1."""
    norm = lambda x: re.sub(r"[\s„“”\"«»]+", " ", x).strip().lower()
    t, q = norm(title), norm(query)
    return 0 if t == q or t == f"საქართველოს {q}" or f"საქართველოს {t}" == q else 1


_TITLE_LEAD = re.compile(r"^(?:the\s+)?(?:(?:organic\s+)?law(?:\s+of\s+georgia)?\s+)?on\s+", re.I)


def _is_constitution(title: str, typ: str = "") -> bool:
    """Matsne files the 1995 Constitution under the Constitutional Court group with the Civil
    Code's number; it has no number of its own, so type/number are not reported."""
    return bool(re.match(r"constitution of georgia\b|საქართველოს კონსტიტუცია", title.strip(), re.I)
                and (not typ or "constitutional court" in typ.lower() or "საკონსტიტუციო" in typ))


def _clean_number(n: str) -> str:
    """Matsne's English pages mix Latin and Georgian letters in some numbers
    ('N875-Vრს-Xმპ'); such a number cannot be cited reliably, so leave it out."""
    n = (n or "").strip()
    return "" if re.search(r"[ა-ჰ]", n) and re.search(r"[A-Za-z]", n) else n


def _check_iso(v, name) -> str:
    v = str(v).strip()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
        raise BadRequest(f"{name} {v!r}: use YYYY-MM-DD")
    return v


class Georgia(Jurisdiction):
    code = "ge"
    name = "Georgia"
    languages = ("ka", "en")
    aliases = ("georgia", "sakartvelo", "საქართველო")
    sources = (
        Source(
            name="Legislative Herald of Georgia (Matsne), Ministry of Justice",
            url="https://matsne.gov.ge",
            covers=("legislation", "caselaw"),
            licence="unknown: no open licence; site footer says 'All Rights Reserved'",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="robots.txt Crawl-delay: 10, so 10 s spacing; no 429 seen in ~20 "
                       "requests (2026-11)",
            terms_url="https://matsne.gov.ge/en/node/207",
        ),
        Source(
            name="Courts of Georgia decision database (ecd.court.ge)",
            url="https://ecd.court.ge/Decision",
            covers=("caselaw",),
            licence="unknown: no terms published",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~20 requests (2026-11)",
            terms_url="",
        ),
    )
    caselaw_filters = {
        "court": "'first' (city/district courts), 'appeal', 'supreme' (all from ECD, "
                 "2018-01 to 2020-04 only) or 'constitutional' (Constitutional Court, "
                 "current, from Matsne). Default: all ECD courts",
        "category": "ECD only: 'civil', 'administrative' or 'criminal'",
        "case_number": "ECD only: the 18-digit ECD case number",
        "date_from": "ECD only: decision date from, YYYY-MM-DD",
        "date_to": "ECD only: decision date to, YYYY-MM-DD",
    }
    legislation_filters = {
        "language": "'ka' (default, Georgian consolidated text) or 'en' (official English "
                    "translations only; ids end in '/en')",
        "status": "'in_force', 'expired' or 'pending'",
        "type": "law, constitutional_court, treaty, resolution, order, edict, decree, "
                "presidential_decree, eu_law, or a Matsne group id",
        "fulltext": "'true' to search the text, not just titles (default: titles)",
    }
    min_interval = {"matsne.gov.ge": 10.0, "ecd.court.ge": 1.0}
    notes = ("Legislation: Matsne (Georgian consolidated text; English translations for many "
             "acts via language='en'). Case law: ECD holds only 2018-01 to 2020-04; "
             "Constitutional Court via court='constitutional'.")
    gaps = (
        "Supreme Court decisions after April 2020: supremecourt.ge robots.txt disallows /ka/getCases*",
        "First-instance and appeal decisions outside 2018-01 to 2020-04: not in ECD; other sources not researched yet",
        "English text of acts without a Legislative Herald translation: not published online",
    )
    samples = {
        "caselaw_query": "იჯარის ხელშეკრულება",
        "decision_id": "3-238176",
        "legislation_query": "სამოქალაქო კოდექსი",
        "law_id": "31702",
        "provision": "მუხლი 1",
    }

    # ---------------------------------------------------------------- case law
    async def search_caselaw(self, query, *, limit, page, filters):
        court = str(filters.get("court") or "").strip().lower()
        if court == "constitutional":
            extra = [k for k in ("category", "case_number", "date_from", "date_to") if filters.get(k)]
            if extra:
                raise BadRequest(f"{', '.join(extra)}: not available with court='constitutional'")
            params = {"group": _GROUPS["constitutional_court"], "type": "all"}
            if query:
                params.update(query=query, query_target="all")
            rows, total = await _matsne_search("ka", params, limit, page)
            items = []
            for num, title, _, fields, _ in rows:
                f = _fields(fields)
                items.append(DecisionHit(id=num, title=title, court=f["issuer"],
                                         date=f.get("date", ""), case_number=f.get("number", ""),
                                         url=_doc_url(num, "ka")))
            return Results(items, total=total)
        if court and court not in _INSTANCES:
            raise BadRequest(f"court {court!r}: use first, appeal, supreme or constitutional")
        cat = str(filters.get("category") or "").strip().lower()
        if cat and cat not in _CATEGORIES:
            raise BadRequest(f"category {cat!r}: use civil, administrative or criminal")
        payload = {"Texts": [query] if query else [], "Skip": (page - 1) * limit, "Take": limit,
                   "CaseNo": str(filters.get("case_number") or "").strip(),
                   "InstanceId": _INSTANCES.get(court, ""),
                   "CaseCategoryId": _CATEGORIES.get(cat, ""),
                   "DecisionDateFrom": _check_iso(filters["date_from"], "date_from")
                   if filters.get("date_from") else None,
                   "DecisionDateTo": _check_iso(filters["date_to"], "date_to")
                   if filters.get("date_to") else None}
        data = await _ecd("/Decision/DecisionDocuments", payload)
        items = []
        for it in (data or {}).get("Items") or []:
            snippet = "; ".join(x for x in [it.get("TypeName"), it.get("CaseCategoryName"),
                                            *(it.get("LitigationTypeName") or [])] if x)
            items.append(DecisionHit(
                id=it["Id"], title=f"{_http.clean(it.get('CourtName'))} {it.get('CaseNo', '')}".strip(),
                court=_http.clean(it.get("CourtName")), date="",
                case_number=it.get("CaseNo", ""), snippet=_http.clean(snippet),
                url=_ecd_url(it.get("InstanceId"), it.get("DecisionDocumentId"))))
        return Results(items, total=(data or {}).get("Total"),
                       note="ECD only holds decisions dated 2018-01 to 2020-04; for the "
                            "Constitutional Court use court='constitutional'. No date is shown "
                            "here: ECD's date is its bulk-upload date, not the decision date "
                            "(date_from/date_to filter on it too). get_decision shows the "
                            "date printed in the decision; cite that.")

    async def get_decision(self, id):
        s = str(id or "").strip()
        if re.fullmatch(r"\d+", s):  # Constitutional Court act in Matsne
            doc = await _doc(s, "ka")
            h = doc["hdr"]
            return Decision(id=s, title=doc["title"], text="\n\n".join(doc["paras"]),
                            url=doc["url"], court=h.get("issuer", ""),
                            date=_http.iso_date(h.get("date", "")),
                            case_number=h.get("number", ""),
                            metadata={k: v for k, v in (("Published", h.get("published", "")),
                                                        ("Registration code", h.get("regcode", "")))
                                      if v})
        m = re.fullmatch(r"([123])-(\d+)", s)
        if not m:
            raise BadRequest(f"Bad decision id {id!r}: use an ECD id such as '3-238176' "
                             "(instance-documentId) or a Matsne document id for the "
                             "Constitutional Court.")
        data = await _ecd("/Decision/DecisionDocumentText",
                          {"InstanceId": int(m[1]), "DecisionDocumentId": int(m[2])})
        raw = (data or {}).get("RawData") or ""
        if not raw.strip():
            raise NotFound(f"ECD has no text for decision {s}")
        lines = [_http.clean(ln) for ln in re.split(r"\r?\n", raw)]
        text = "\n\n".join(ln for ln in lines if ln)
        head = text[:1500]
        nums = [n for n in re.findall(r"(?:#|№|N)\s*([^\s,#]+)", head)
                if not re.fullmatch(r"\d{12,}", n) and re.search(r"\d", n)]
        court = "საქართველოს უზენაესი სასამართლო" if m[1] == "3" else ""
        if not court:
            c = re.search(r"([ა-ჰ]+(?:ის)? (?:საქალაქო|რაიონული|სააპელაციო) სასამართლო)", head)
            court = c[1] if c else ""
        case_no = nums[0] if nums else ""
        title = f"{court} {case_no}".strip() or f"ECD decision {s}"
        return Decision(id=s, title=title, text=text, url=_ecd_url(m[1], m[2]), court=court,
                        date=_ka_date(head), case_number=case_no,
                        metadata={"ECD case id": str(data.get("CaseId", ""))})

    # ------------------------------------------------------------- legislation
    async def search_legislation(self, query, *, limit, page, filters):
        lang = str(filters.get("language") or "ka").strip().lower()
        if lang not in ("ka", "en"):
            raise BadRequest(f"language {lang!r}: use 'ka' or 'en'")
        params: dict = {}
        if query:
            params["query"] = query
            if str(filters.get("fulltext") or "").lower() in ("true", "1", "yes"):
                params["query_target"] = "text"
        if filters.get("status"):
            st = str(filters["status"]).strip().lower()
            if st not in _STATUS:
                raise BadRequest(f"status {st!r}: use in_force, expired or pending")
            params["status"] = _STATUS[st]
        if filters.get("type"):
            t = str(filters["type"]).strip().lower()
            if t not in _GROUPS and not t.isdigit():
                raise BadRequest(f"type {t!r}: use one of {', '.join(_GROUPS)} or a Matsne group id")
            params["group"] = _GROUPS.get(t, t)
        # Matsne sorts by date, newest first, so amendments and court rulings that quote a
        # code's name bury the code itself. Fetch a wide window and put exact title matches first.
        wide = bool(query) and page * limit <= _WINDOW
        rows, total = await _matsne_search(lang, params, _WINDOW if wide else limit,
                                           1 if wide else page)
        if wide and not rows and _TITLE_LEAD.match(query):
            # Matsne matches the phrase literally: "Law on Entrepreneurs" misses "On Entrepreneurs"
            params["query"] = _TITLE_LEAD.sub("", query).strip()
            rows, total = await _matsne_search(lang, params, _WINDOW, 1)
        if wide:
            rows = sorted(rows, key=lambda r: _title_rank(r[1], query))
            rows = rows[(page - 1) * limit:page * limit]
        items = []
        for num, title, panel, fields, has_en in rows:
            f = _fields(fields)
            if _is_constitution(title, f["type"]):
                f["type"], f["number"] = "Constitution", ""
            f["number"] = _clean_number(f.get("number", ""))
            if f.get("number", "").rstrip("-") in ("", "N"):
                f.pop("number", None)
            hl = "en" if lang == "en" and has_en else "ka"
            items.append(LawHit(id=_make_id(num, hl), title=title, type=f["type"],
                                number=f.get("number", ""), date=f.get("date", ""),
                                status=_STATUS_LABEL.get(panel, ""),
                                snippet=f["issuer"], url=_doc_url(num, hl)))
        note = ("English titles only match acts with an official English translation."
                if lang == "en" else "")
        return Results(items, total=total, note=note)

    async def get_legislation_toc(self, id):
        doc = await _doc(*_parse_matsne_id(id))
        return Toc(id=doc["id"], title=doc["title"], url=doc["url"], entries=doc["entries"])

    async def get_legislation_provision(self, id, provision):
        doc = await _doc(*_parse_matsne_id(id))
        label = _find_label(doc, provision)
        a, b = doc["spans"][label]
        paras = doc["paras"][a:b]
        head = _strip_bold(paras[0])
        text = "\n\n".join([f"**{head}**", *paras[1:]])
        return Provision(law_id=doc["id"], law_title=doc["title"], provision=label, text=text,
                         url=doc["url"], as_of=doc["as_of"] if doc["lang"] == "ka" else "")

    async def get_legislation_text(self, id):
        doc = await _doc(*_parse_matsne_id(id))
        h = doc["hdr"]
        meta = {"Number": "" if _is_constitution(doc["title"]) else _clean_number(h.get("number", "")), "Adopted": _http.iso_date(h.get("date", "")),
                "Issuer": h.get("issuer", ""), "Published": h.get("published", ""),
                "Registration code": h.get("regcode", "")}
        if doc["lang"] == "en":
            meta["Language"] = ("English translation by the Legislative Herald; the Georgian "
                                f"text is authoritative (Georgian consolidated as of {doc['as_of']})")
        return LawText(id=doc["id"], title=doc["title"], text="\n\n".join(doc["paras"]),
                       url=doc["url"], as_of=doc["as_of"] if doc["lang"] == "ka" else "",
                       metadata={k: v for k, v in meta.items() if v})
