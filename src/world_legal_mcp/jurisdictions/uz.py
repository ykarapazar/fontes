"""Uzbekistan: legislation and court decisions from lex.uz, the National Database of
Legislation (Qonunchilik ma'lumotlari milliy bazasi), run by the "Adolat" National Legal
Information Centre under the Ministry of Justice. It is the official publication channel
for Uzbek legislation.

Gotchas this code encodes (verified 2026-11-06 from a UK IP):
  * lex.uz has no robots.txt (404) and no meta robots. Its "Условия предоставления
    информации" (/ru/axborot) allow use "only for personal purposes" and forbid copying or
    distribution for profit without written permission: hence the warning below.
  * One document = one numeric id per language version (the Russian and Uzbek texts of an
    act have different ids). New ids can be negative ("-8569942"). /ru/docs/{id} is the
    current consolidated text; an unknown id answers 404.
  * The text sits in #divCont as one div per element, typed by class: ACT_TITLE,
    TEXT_HEADER_DEFAULT (part/section/chapter), CLAUSE_DEFAULT (article heading), ACT_TEXT,
    CHANGES_ORIGINS (official amendment notes). COMMENT (incl. the non-official "LexUz
    commentary") and INDEXES_ON_REF (classifier tags) are hidden on the site; we drop them.
    Inserted articles are "Статья 26<sup>1</sup>": shown as 26¹, labelled "Статья 26-1".
  * Search is an ASP.NET WebForms page: GET /ru/search/{nat|court}?... gives page 1 (20
    rows); later pages are __doPostBack POSTs carrying __VIEWSTATE, with a pager window of
    10 page links. We walk the pager (a few POSTs) to reach deeper pages.
  * The version list (?ONDATE=dd.mm.yyyy) includes future dates for amendments not yet in
    force; as_of is the newest version date not after today.
"""
from __future__ import annotations

import re
from urllib.parse import urlencode

from lxml import etree, html

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

SITE = "https://lex.uz"
_PAGE = 20          # rows per search page (fixed by the site)
_MAX_HOPS = 6       # pager POSTs we allow to reach a deep page

_LANGS = {"ru": "1", "uz": "3", "uz-cyrl": "3", "uz-latn": "4", "en": "2"}
_TYPES = {"constitution": "4131", "code": "3964", "law": "3968", "decree": "3973",
          "resolution": "3972", "order": "588", "regulation": "487", "decision": "491"}
_STATUS = {"in_force": "Y", "repealed": "R", "not_in_force": "N"}
_STATUS_NAME = {"y": "in force", "r": "repealed", "n": "not in force"}
_BRANCH = {"civil": "F", "economic": "H", "criminal": "J"}
_INSTANCE = {"first": "1", "appeal": "2", "cassation": "3", "supervisory": "4"}
# Court-name patterns, used only when lex.uz's own tag finds nothing (most decisions are untagged).
_BRANCH_RE = {"civil": r"гражданск", "economic": r"экономическ", "criminal": r"приговор|уголовн"}
_INSTANCE_RE = {"first": r"^(?!.*(?:апелляц|кассац|надзор)).*(?:приговор|районн|городск)", "appeal": r"апелляц",
                "cassation": r"кассац", "supervisory": r"надзор"}

_SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
_DROP = ("COMMENT", "INDEXES_ON_REF")
# "Статья 26-1. ...", "Article 5. ...", "5-модда. ...", "26-1-modda. ..."
_ART = re.compile(r"^(?:(Статья|Article|Модда|Modda)\s+(\d+(?:-\d+)?)"
                  r"|(\d+(?:-\d+)?)\s*-\s*(модда|modda))\s*\.", re.I)

_docs: dict = {}


def _check_id(raw) -> str:
    s = str(raw or "").strip()
    m = re.fullmatch(r"(?:https?://(?:www\.)?lex\.uz(?:/(?:ru|uz|en|oz))?/docs/)?(-?\d+)"
                     r"(?:[/?#].*)?", s)
    if not m:
        raise BadRequest(f"Bad lex.uz id {raw!r}: use the numeric document id, e.g. '111181' "
                         "(Civil Code, Part 1, Russian text) or a lex.uz/ru/docs/<id> URL.")
    return m[1]


def _url(did: str) -> str:
    return f"{SITE}/ru/docs/{did}"


def _choice(filters: dict, key: str, table: dict, numeric: bool = False) -> str:
    v = str(filters.get(key, "")).strip().lower()
    if not v:
        return ""
    if v in table:
        return table[v]
    if numeric and v.isdigit():
        return v
    raise BadRequest(f"Bad {key} {v!r}: use one of {', '.join(table)}"
                     + (", or a numeric lex.uz id." if numeric else "."))


_TITLE_FILLER = {"закон", "закона", "о", "об", "обо", "в", "и", "на", "по", "защите", "республики",
                "узбекистан", "республика", "law", "of", "the", "on"}


def _text_params(query: str, filters: dict, default_fulltext: bool) -> dict:
    q = " ".join(str(query or "").split())
    if q and not 3 <= len(q) <= 100:
        raise BadRequest("lex.uz needs a query of 3 to 100 characters.")
    ft = str(filters.get("fulltext", "")).strip().lower()
    if ft not in ("", "true", "false", "1", "0", "yes", "no"):
        raise BadRequest(f"Bad fulltext {ft!r}: use 'true' or 'false'.")
    fulltext = ft in ("true", "1", "yes") if ft else default_fulltext
    return {("query" if fulltext else "searchtitle"): q} if q else {}


# ------------------------------------------------------------------ search
def _rows(doc) -> list[dict]:
    out = []
    for tr in doc.xpath('//tr[contains(@class,"dd-table__main-item")]'):
        a = tr.xpath('.//div[contains(@class,"dd-table__main-left-desc")]//a[contains(@href,"/docs/")]')
        if not a:
            continue
        m = re.search(r"/docs/(-?\d+)", a[0].get("href", ""))
        if not m:
            continue
        badge = _http.clean(" ".join(tr.xpath('.//span[contains(@class,"badge")]//text()')))
        st = tr.xpath('.//i[contains(@class,"status_code_")]/@class')
        sm = re.search(r"status_code_(\w)", st[0]) if st else None
        out.append({"id": m[1], "title": _http.clean(a[0].text_content()), "badge": badge,
                    "status": _STATUS_NAME.get(sm[1].lower(), "") if sm else ""})
    return out


def _badge(badge: str) -> tuple[str, str, str]:
    """'Закон Республики Узбекистан, от 25.12.2023 г. № ЗРУ-887' -> (kind, date, number).
    Uzbek: '..., 29.07.2016 йилдаги 13-сон'."""
    dm = re.search(r"(\d{2}\.\d{2}\.\d{4})", badge)
    kind = _http.clean(re.split(r",\s*(?:от\s|\d{2}\.\d{2}\.\d{4})", badge)[0]) if dm else badge
    nm = re.search(r"№\s*(\S+)", badge) or re.search(r"(\S+?)-(?:сон|son)\b", badge)
    return kind.rstrip(","), _http.iso_date(dm[1]) if dm else "", nm[1] if nm else ""


def _pager(text: str) -> dict[int, str]:
    return {int(n): f"ucFoundActsControl$rptPaging$ctl{c}$lbPaging"
            for c, n in re.findall(r"rptPaging\$ctl(\d+)\$lbPaging&#39;,&#39;&#39;\)\">(\d+)<", text)}


async def _fetch(method: str, url: str, **kw):
    r = await (_http.get(url) if method == "GET" else _http.post(url, **kw))
    if r.status_code != 200:
        raise SourceError(_http.error("lex.uz", "search request failed", r.status_code),
                          r.status_code)
    if not any(m in r.text for m in ("dd-table__main", "refind__result-export__title",
                                     "refindHeader__notFound")):
        raise SourceError("lex.uz: unexpected search page (blocked or changed?)", 200)
    return r


async def _search(kind: str, params: dict, *, limit: int, page: int) -> tuple[list[dict], int | None]:
    url = f"{SITE}/ru/search/{kind}?{urlencode(params)}"
    r = await _fetch("GET", url)
    tm = re.search(r"найдено\s+(\d+)", r.text)
    total = int(tm[1]) if tm else 0
    offset = (page - 1) * limit
    if offset >= total:
        return [], total
    first, last = offset // _PAGE + 1, min((offset + limit - 1) // _PAGE + 1, (total - 1) // _PAGE + 1)
    cur, rows, hops = 1, [], 0
    while True:
        if cur >= first:
            rows += _rows(html.fromstring(r.text))
        if cur >= last:
            break
        want = max(cur + 1, first)
        links = _pager(r.text)
        if not links:
            break
        step = want if want in links else max(n for n in links if n <= want) \
            if any(n <= want for n in links) else min(links)
        hops += 1
        if hops > _MAX_HOPS or step == cur:
            raise BadRequest(f"lex.uz search pages go by a pager; page {page} is too deep to "
                             "reach. Narrow the query or filters instead.")
        d = html.fromstring(r.text)
        form = {i.get("name"): i.get("value") or ""
                for i in d.xpath('//form[@id="Form1"]//input[@type="hidden"]') if i.get("name")}
        form.update({"__EVENTTARGET": links[step], "__EVENTARGUMENT": ""})
        r = await _fetch("POST", url, data=form)
        cur = step
    start = offset - (first - 1) * _PAGE
    return rows[start:start + limit], total


# ---------------------------------------------------------------- documents
def _inner_md(div) -> str:
    s = etree.tostring(div, encoding=str, method="html")
    s = re.sub(r"<sup>\s*(\d+)\s*</sup>", lambda m: m[1].translate(_SUP), s)
    s = re.sub(r"<br\s*/?>", " ", s)
    return _http.clean(_http.html_to_md(s)) if "<table" not in s else _http.html_to_md(s).strip()


def _label_num(div) -> tuple[str, str] | None:
    s = etree.tostring(div, encoding=str, method="html")
    s = re.sub(r"<sup>\s*(\d+)\s*</sup>", r"-\1", s)
    t = _http.clean(html.fromstring(s).text_content() if s.strip() else "")
    m = _ART.match(t)
    if not m:
        return None
    if m[1]:
        return f"{m[1]} {m[2]}", m[2]
    return f"{m[3]}-{m[4]}", m[3]


async def _doc(did: str) -> dict:
    if did in _docs:
        return _docs[did]
    r = await _http.get(_url(did))
    if r.status_code == 404:
        raise NotFound(f"lex.uz has no document with id {did}.")
    if r.status_code != 200:
        raise SourceError(_http.error("lex.uz", "document request failed", r.status_code),
                          r.status_code)
    d = html.fromstring(r.text)
    cont = d.xpath('//div[@id="divCont"]')
    if not cont:
        raise SourceError("lex.uz: document page has no text block (blocked or changed?)", 200)
    raw_title = _http.clean((d.xpath("//title/text()") or [""])[0]).replace("\xa0", " ")
    # "<number>-сон dd.mm.yyyy. <title>" or "dd.mm.yyyy. <title>"
    hm = re.match(r"^\s*(.*?)(\d{2}\.\d{2}\.\d{4})\.\s*(.*)$", raw_title)
    number = re.sub(r"-(?:сон|son)\s*$", "", hm[1].strip()) if hm else ""
    date = _http.iso_date(hm[2]) if hm else ""
    title = (hm[3] if hm else raw_title).strip() or f"lex.uz {did}"

    paras: list[str] = []
    entries: list[TocEntry] = []
    spans: dict[str, tuple[int, int]] = {}
    nums: dict[str, str] = {}
    meta: dict[str, str] = {}
    open_label = None
    for el in cont[0]:
        cls = (el.get("class") or "").split()
        kind = cls[0] if cls else ""
        if not kind or kind in _DROP:
            continue
        inner = el.xpath('./div[@name]')
        if not inner:
            continue
        md = _inner_md(inner[0])
        if not md:
            continue
        if kind == "ACCEPTING_BODY":
            meta["court"] = _http.clean(inner[0].text_content())
        if kind == "TEXT_HEADER_DEFAULT":
            if open_label:
                spans[open_label] = (spans[open_label][0], len(paras))
                open_label = None
            entries.append(TocEntry(title=md, level=0))
            paras.append(f"## {md}")
            continue
        if kind == "CLAUSE_DEFAULT":
            ln = _label_num(inner[0])
            if open_label:
                spans[open_label] = (spans[open_label][0], len(paras))
                open_label = None
            if ln:
                label, num = ln
                n = 2
                while label in spans:
                    label, n = f"{ln[0]} ({n})", n + 1
                nums.setdefault(num, label)
                spans[label] = (len(paras), len(paras))
                open_label = label
                entries.append(TocEntry(title=md, level=1, provision=label))
            paras.append(f"### {md}")
            continue
        if kind == "ACT_TITLE":
            paras.append(f"# {md}")
            continue
        if kind == "PUBLICATION_ORIGIN" and open_label:
            spans[open_label] = (spans[open_label][0], len(paras))
            open_label = None
        paras.append(md)
    if open_label:
        spans[open_label] = (spans[open_label][0], len(paras))

    versions = [_http.iso_date(v) for v in re.findall(r"ONDATE=(\d{2}\.\d{2}\.\d{4})'\)", r.text)]
    now = _http.today()
    past = sorted(v for v in versions if v and v <= now)
    doc = {"id": did, "title": title, "url": _url(did), "date": date, "number": number,
           "paras": paras, "entries": entries, "spans": spans, "nums": nums, "meta": meta,
           "as_of": past[-1] if past else "", "text": "\n\n".join(paras)}
    if not paras:
        raise NotFound(f"lex.uz document {did} has no published text.")
    return _http.lru_put(_docs, did, doc, 3)


def _norm_provision(raw: str) -> str:
    """'Статья 5', 'ст. 26-1', '26¹', '26^1', 'Article 5', '5-modda', '5' -> '5' / '26-1'."""
    s = _http.clean(raw).lower()
    s = re.sub(r"[⁰¹²³⁴⁵⁶⁷⁸⁹]+", lambda m: "-" + m[0].translate(str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")), s)
    s = re.sub(r"^(статья|ст\.?|article|art\.?|модда|modda)\s*", "", s)
    s = re.sub(r"\s*-\s*(модда|modda)\.?$", "", s)
    m = re.fullmatch(r"(\d+)(?:\s*(?:-|\^|\.)\s*(\d+))?\.?", s)
    if not m:
        raise BadRequest(f"Bad provision {raw!r}: use an article label such as 'Статья 5', "
                         "'5', or '26-1' for an inserted article (Статья 26¹).")
    return m[1] + (f"-{m[2]}" if m[2] else "")


def _label(doc: dict, raw: str) -> str:
    if raw in doc["spans"]:
        return raw
    num = _norm_provision(raw)
    if num in doc["nums"]:
        return doc["nums"][num]
    raise NotFound(f"{doc['title']} ({doc['id']}) has no article {raw!r}. "
                   "Use get_legislation_toc to see the article labels.")


class Uzbekistan(Jurisdiction):
    code = "uz"
    name = "Uzbekistan"
    languages = ("uz", "ru")
    aliases = ("uzbekistan", "o'zbekiston", "oʻzbekiston", "ўзбекистон", "узбекистан")
    sources = (
        Source(
            name="lex.uz, National Database of Legislation (Ministry of Justice, 'Adolat' "
                 "National Legal Information Centre)",
            url="https://lex.uz",
            covers=("legislation", "caselaw"),
            licence="lex.uz terms (/ru/axborot): personal use only; copying or distribution "
                    "for profit needs the Centre's written permission",
            commercial_use=False,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~25 requests (2026-11)",
            terms_url="https://lex.uz/ru/axborot",
            warning=("Personal use only: lex.uz terms allow use of its information for personal purposes only; "
                     "copying, distribution or transfer for profit needs the Adolat Centre's "
                     "written permission."),
        ),
    )
    caselaw_filters = {
        "lang": "language version: ru, uz (Cyrillic), uz-latn, en. Default: all",
        "branch": "civil, economic or criminal",
        "instance": "first, appeal, cassation or supervisory",
        "fulltext": "'false' to search titles only (default: full text, since most "
                    "decisions are titled 'Дело № ...')",
    }
    legislation_filters = {
        "lang": "language version: ru, uz (Cyrillic), uz-latn, en. Default: all",
        "type": ", ".join(_TYPES) + ", or a numeric lex.uz form id",
        "status": "in_force, repealed or not_in_force. Default: all",
        "fulltext": "'true' to search the text, not just titles (default: titles)",
    }
    min_interval = {"lex.uz": 1.0}
    notes = ("Official Ministry of Justice database: current consolidated texts (Uzbek, "
             "Russian, some English) and selected court decisions. Each language version "
             "has its own id. Case-law branch filter: civil, economic or criminal (no administrative). "
             "Personal use only under the site terms.")
    gaps = (
        ("Use beyond personal purposes: lex.uz terms allow use 'only for personal purposes'; needs "
         "the Adolat Centre's permission"),
        ("Court decisions outside lex.uz's selection (most lower-court judgments): not published on"
         " lex.uz"),
        "English texts: only some acts have an English version on lex.uz",
        ("Full Supreme Court archive on public.sud.uz (the courts' publication portal): every "
         "decision file needs a captcha token (checked 2026-11-10); not used"),
        ("Administrative-court decisions by branch: the branch filter covers civil, economic and "
         "criminal only; administrative cases come only in unfiltered searches"),
    )
    samples = {
        "caselaw_query": "неплатежеспособности",
        "decision_id": "6676132",
        "legislation_query": "Гражданский кодекс",
        "law_id": "111181",
        "provision": "Статья 1",
    }

    # ---------------------------------------------------------------- case law
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        params = {}
        lang = _choice(filters, "lang", _LANGS)
        branch = _choice(filters, "branch", _BRANCH)
        inst = _choice(filters, "instance", _INSTANCE)
        if branch:
            params["court_form"] = branch
        if inst:
            params["instance"] = inst
        text = _text_params(query, filters, default_fulltext=True)
        params.update(text)
        params["lang"] = lang or ("" if text else "1")
        if not params["lang"]:
            del params["lang"]
        rows, total = await _search("court", params, limit=limit, page=page)
        by_name = False
        if (branch or inst) and not rows and page == 1:
            # lex.uz tags few decisions: search untagged and keep rows whose court name fits.
            for k in ("court_form", "instance"):
                params.pop(k, None)
            pats = [rx[next(k for k, c in codes.items() if c == v)]
                    for rx, codes, v in ((_BRANCH_RE, _BRANCH, branch),
                                         (_INSTANCE_RE, _INSTANCE, inst)) if v]
            allrows, _ = await _search("court", params, limit=50, page=1)
            rows = [x for x in allrows if all(
                re.search(p, x["badge"], re.I) for p in pats)][:limit]
            total, by_name = len(rows), bool(rows)
        items = []
        for x in rows:
            kind, date, number = _badge(x["badge"])
            items.append(DecisionHit(id=x["id"], title=x["title"] or f"{kind} {number}".strip(),
                                     court=kind, date=date, case_number=number,
                                     url=_url(x["id"])))
        note = ("Selected decisions only (mostly Supreme Court, Plenum resolutions and economic "
                "courts); parties are anonymised. Empty query lists Russian texts.") \
            if not text else ""
        if by_name:
            note = ("lex.uz has no branch/instance tag for these decisions; they were matched by "
                    "court name among the first 50 results of the unfiltered search, so the list "
                    "may be incomplete. Check the court and date shown. " + note).strip()
        elif branch or inst:
            note = ("A branch or instance filter keeps ONLY the ~430 decisions lex.uz itself tagged, "
                    "none dated after 2016 (mostly Higher Economic Court rulings; that court was "
                    "later abolished). The result is therefore not the newest case law: later "
                    "decisions exist (e.g. Supreme Court economic collegium rulings of 2023, "
                    "criminal sentences of 2020) but carry no tag, so a filtered search never "
                    "returns them. lex.uz cannot filter them by branch or instance; search "
                    "without the filter and put the court or type in the query (e.g. 'Приговор', "
                    "'Судебная коллегия по экономическим делам Верховного суда'), then judge "
                    "by the court and date shown. " + note).strip()
        return Results(items=items, total=total, note=note)

    async def get_decision(self, id):
        doc = await _doc(_check_id(id))
        return Decision(id=doc["id"], title=doc["title"], text=doc["text"], url=doc["url"],
                        court=doc["meta"].get("court", ""), date=doc["date"],
                        case_number=doc["number"])

    # ------------------------------------------------------------- legislation
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        params = {}
        lang = _choice(filters, "lang", _LANGS)
        form = _choice(filters, "type", _TYPES, numeric=True)
        status = _choice(filters, "status", _STATUS)
        if form:
            params["form_id"] = form
        if status:
            params["status"] = status
        text = _text_params(query, filters, default_fulltext=False)
        params.update(text)
        if lang or not text:
            params["lang"] = lang or "1"
        rows, total = await _search("nat", params, limit=limit, page=page)
        note = ""
        if not total and "searchtitle" in params:
            # Titles are matched literally: drop generic words ('Закон о защите ...')
            core = " ".join(w for w in params["searchtitle"].split()
                            if w.lower().strip("«»\"'") not in _TITLE_FILLER)
            if core != params["searchtitle"] and len(core) >= 3:
                rows, total = await _search("nat", {**params, "searchtitle": core},
                                            limit=limit, page=page)
                if total:
                    note = (f"No title contains the exact words; showing titles matching "
                            f"{core!r} (generic words dropped).")
            if not total:
                note = ("No title matched. lex.uz matches titles only by default: try fewer, "
                        "core words or filters {'fulltext': 'true'}.")
        items = []
        for x in rows:
            kind, date, number = _badge(x["badge"])
            items.append(LawHit(id=x["id"], title=x["title"], type=kind, number=number,
                                date=date, status=x["status"], url=_url(x["id"])))
        return Results(items=items, total=total, note=note)

    async def get_legislation_toc(self, id):
        doc = await _doc(_check_id(id))
        entries = doc["entries"] or [TocEntry(
            title="This act has no articles or headings of its own on lex.uz (typically an "
                  "amending act, or its text is only in another language version); use "
                  "get_legislation_text to read what is published.", level=0)]
        return Toc(id=doc["id"], title=doc["title"], url=doc["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        doc = await _doc(_check_id(id))
        label = _label(doc, provision)
        a, b = doc["spans"][label]
        return Provision(law_id=doc["id"], law_title=doc["title"], provision=label,
                         text="\n\n".join(doc["paras"][a:b]), url=doc["url"], as_of=doc["as_of"])

    async def get_legislation_text(self, id):
        doc = await _doc(_check_id(id))
        meta = {k: v for k, v in (("Дата", doc["date"]), ("Номер", doc["number"])) if v}
        return LawText(id=doc["id"], title=doc["title"], text=doc["text"], url=doc["url"],
                       as_of=doc["as_of"], metadata=meta)
