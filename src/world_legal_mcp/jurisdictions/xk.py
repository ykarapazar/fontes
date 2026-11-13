"""Kosovo: Constitutional Court decisions (gjk-ks.org) and the Official Gazette (gzk.rks-gov.net).

No ordinary-court case law: gjyqesori-rks.org (Kosovo Judicial Council) answers 403
to our client and its robots.txt sets `Content-Signal: ai-train=no` (checked 2026-11-05).

Gotchas this code encodes:
  * Case law: the Constitutional Court's Vue site reads a public JSON backend at
    api.webgjk-ks.org. POST /publish/CdmsCase/getAllFilteredDecisions (searchText is
    required; null returns nothing; case numbers like "KI143/25" are not searchable)
    gives 10..n hits with `totalCount`; GET /publish/CdmsCase/getDecisionByID/<id>
    gives the case plus `caseDocuments` whose `documentContent` is the PDF's text
    (idLanguage 1 = Albanian, 2 = English, 3 = Serbian). Old cases can have an
    empty Albanian text (scanned); we fall back to English, then Serbian.
    The id is the backend's numeric case id ("9585"); "9585/en" or "9585/sr"
    picks the language of the text. The hit date is the decision date read from
    the summary ("… i 6 tetorit 2026, publikuar më …"), else the publication date.
  * Legislation: ASP.NET WebForms. GET SearchIn.aspx?Index=2&so=<1 title|2 keywords|
    10 content>&s=<query> runs a search; the server decodes `s` as Windows-1252,
    so the query is sent in that encoding. 20 hits per page; further pages are
    __doPostBack(...$lbNext) postbacks carrying the page's __VIEWSTATE. Titles in
    the index sometimes carry double spaces, so phrases can miss: search one word
    or the law number ("04/L-077"). ActDocumentDetail.aspx?ActID=<id> holds the
    act's text (the PDF's text layer, lines split by <br>, page numbers and
    running heads interleaved); some acts have no HTML text, then the PDF comes
    from an image-button postback. Texts are the act as published in the
    Gazette, not consolidated; amendments are separate acts (and a few
    consolidated versions are separate ActIDs). Albanian only (the site's other
    languages are a per-session switch).
  * robots.txt of gzk.rks-gov.net disallows /gzk.asmx (a SOAP service); not used.
"""
from __future__ import annotations

import html as _html
import re
import unicodedata
from urllib.parse import quote

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

API = "https://api.webgjk-ks.org"
GJK = "https://gjk-ks.org"
GZK = "https://gzk.rks-gov.net"
COURT = "Gjykata Kushtetuese"

_LANGS = {"sq": 1, "en": 2, "sr": 3}
_MONTHS = {
    # Albanian (genitive forms start the same), English, Serbian (Latin)
    "janar": 1, "shkurt": 2, "mars": 3, "prill": 4, "maj": 5, "qershor": 6, "korrik": 7,
    "gusht": 8, "shtator": 9, "tetor": 10, "nëntor": 11, "nentor": 11, "dhjetor": 12,
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6, "july": 7,
    "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
    "januar": 1, "februar": 2, "mart": 3, "jun": 6, "jul": 7, "avgust": 8, "septembar": 9,
    "oktobar": 10, "novembar": 11, "decembar": 12,
    # Serbian genitive ("6. oktobra 2026") drops the vowel before the final r
    "septembr": 9, "oktobr": 10, "novembr": 11, "decembr": 12,
}
_SEARCH_IN = {"title": "1", "keywords": "2", "content": "10"}
# The Gazette's title search is a phrase match that misses "LIGJI NR. 03/L-212 I PUNËS" for its own
# name; the act is found by its number, so a plain request for it is routed there.
_LABOUR_LAW = {"ligji i punes", "ligji per punen", "ligji i punes nr. 03/l-212", "labour law",
               "labor law", "the labour law", "law on labour", "zakon o radu"}
_PAGE = 20                      # gzk hits per page
_MAX_SOURCE_PAGES = 10          # each further page is one postback of a ~250 KB page

VERSION_CONSOLIDATED = ("consolidated text published by the Official Gazette; not an official "
                        "version (the Gazette's own disclaimer)")

_text_cache: dict[str, tuple[str, list[str]]] = {}


# --------------------------------------------------------------------------- #
# Case law: Constitutional Court
# --------------------------------------------------------------------------- #
async def _api(method: str, path: str, **kw) -> object:
    r = await _http.request(method, API + path, **kw)
    if r.status_code != 200:
        raise SourceError(f"api.webgjk-ks.org {path.split('/')[-1]} failed", r.status_code)
    try:
        d = r.json()
    except ValueError as e:
        raise SourceError("api.webgjk-ks.org: unexpected non-JSON reply", r.status_code) from e
    return d.get("data")


def _decision_date(summary_html: str, fallback: str) -> str:
    s = _http.clean(re.sub(r"<[^>]+>", " ", _html.unescape(summary_html or "")))
    m = re.search(r"(\d{1,2})\.?\s+([^\W\d_]+)\.?\s+(\d{4})\.?(?:\s*godine)?\s*,?\s*"
                  r"(?:publikuar|published|objavljen)", s, re.I)
    if m:
        word = m[2].lower()
        month = next((n for k, n in _MONTHS.items() if word.startswith(k)), 0)
        if month and 1 <= int(m[1]) <= 31:
            return f"{m[3]}-{month:02d}-{int(m[1]):02d}"
    return _http.iso_date(fallback)


def _parse_decision_id(id: str) -> tuple[str, str]:
    m = re.fullmatch(r"\s*(\d+)\s*(?:[/:]\s*(sq|en|sr))?\s*", id or "", re.I)
    if not m:
        raise BadRequest("Kosovo decision ids are the Constitutional Court's numeric case id "
                         "from search_caselaw, e.g. '9585' (optionally '9585/en' or '9585/sr').")
    return m[1], (m[2] or "sq").lower()


class Kosovo(Jurisdiction):
    code = "xk"
    name = "Kosovo"
    languages = ("sq", "sr", "en")
    aliases = ("kosovo", "kosova", "kosovë", "rks")
    sources = (
        Source(
            name="Gjykata Kushtetuese e Republikës së Kosovës (Constitutional Court), gjk-ks.org",
            url=GJK,
            covers=("caselaw",),
            licence="no licence or terms of use published (only a privacy policy); site footer "
                    "'© Gjykata Kushtetuese e Kosovës'. Law 04/L-065 art. 12 excluded official "
                    "materials from copyright (successor law 08/L-205 not checked)",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 in ~20 requests (2026-11)",
            terms_url=f"{GJK}/PrivacyPolicy",
        ),
        Source(
            name="Gazeta Zyrtare e Republikës së Kosovës (Official Gazette, Office of the Prime Minister), "
                 "gzk.rks-gov.net",
            url=GZK,
            covers=("legislation",),
            licence="no licence or terms of use published; footer 'Copyright ZKM - MAP © 2022'. "
                    "Law 04/L-065 art. 12 excluded laws and official materials from copyright "
                    "(successor law 08/L-205 not checked)",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1.5 s spacing, no 429 in ~30 requests (2026-11)",
            terms_url=f"{GZK}/AboutUs.aspx?index=12",
        ),
    )
    caselaw_filters = {
        "language": "language of titles and summaries: sq (default), en, sr; hit ids then "
                    "open the text in that language",
        "referral": "type of referral, e.g. KI (individual), KO (state organs), KK (municipalities)",
        "date_from": "publication date on or after YYYY-MM-DD",
        "date_to": "publication date on or before YYYY-MM-DD",
    }
    legislation_filters = {
        "search_in": "title (default), keywords or content",
    }
    min_interval = {"api.webgjk-ks.org": 1.0, "gzk.rks-gov.net": 1.5}
    notes = ("Case law: Constitutional Court only (2009-), sq/en/sr. Legislation: Official Gazette, "
             "Albanian: Constitution, codes and laws as published; the Gazette's consolidated versions "
             "are separate acts titled '(KONSOLIDUAR)'.")
    gaps = (
        ("Ordinary-court case law (gjyqesori-rks.org): 403 to our client; robots.txt sets "
         "Content-Signal ai-train=no"),
        ("Consolidated laws: the Gazette has acts as published; it has consolidated only some laws "
         "(158 '(KONSOLIDUAR)' acts on 2026-11-10, all reachable: search 'konsoliduar'); for the rest "
         "read the act with its amending acts"),
        ("Serbian and English texts of legislation: the site's language is a per-session switch; "
         "not built yet"),
        "Old Constitutional Court documents with no text in any language: scans only, no text",
        ("Kosovo Specialist Chambers (repository.scp-ks.org): not built; its legal notice allows "
         "reuse only for private, information or education use and asks written permission for "
         "anything else"),
    )
    samples = {
        "caselaw_query": "pronës",
        "decision_id": "9583",
        "legislation_query": "detyrimeve",
        "law_id": "3702",
        "provision": "24",
    }

    # ------------------------------ case law ------------------------------ #
    async def search_caselaw(self, query, *, limit, page, filters):
        if not (query or "").strip():
            raise BadRequest("Kosovo case-law search needs words to search for (the source returns "
                             "nothing for an empty query).")
        lang = str(filters.get("language") or "sq").lower()
        if lang not in _LANGS:
            raise BadRequest("language must be sq, en or sr")
        referral = filters.get("referral")
        if referral is not None:
            referral = str(referral).strip().upper()
            if not re.fullmatch(r"K[A-Z]{1,2}", referral):
                raise BadRequest("referral is a case-number prefix such as KI, KO or KK")
        dates = {}
        for key in ("date_from", "date_to"):
            v = filters.get(key)
            if v is not None:
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(v).strip()):
                    raise BadRequest(f"{key}={v!r}: use YYYY-MM-DD, e.g. 2022-01-31")
                dates[key] = str(v).strip()
        # the source ignores dateTo unless dateFrom is also set
        if "date_to" in dates and "date_from" not in dates:
            dates["date_from"] = "2000-01-01"
        body = {"searchText": query.strip(), "dateFrom": dates.get("date_from"),
                "dateTo": dates.get("date_to"),
                "referralType": referral, "actList": None, "procedureList": None,
                "pageNumber": page, "pageSize": limit, "language": lang}
        rows = await _api("POST", "/publish/CdmsCase/getAllFilteredDecisions", json=body) or []
        total = int(rows[0].get("totalCount") or 0) if rows else 0
        suf = {"sq": "", "en": "EN", "sr": "SR"}[lang]
        items = []
        for x in rows[:limit]:
            cid = str(x["id"])
            if suf:   # translated fields are present only when the translation exists
                x = x | {k: x[k + suf] for k in ("title", "description", "complainant") if x.get(k + suf)}
                x["titleFilter"] = x.get(f"title{suf}Filter") or x.get("titleFilter")
            items.append(DecisionHit(
                id=cid if lang == "sq" else f"{cid}/{lang}",
                title=self._title(x),
                court=COURT,
                date=_decision_date(x.get("description") or "", x.get("entryDate") or ""),
                case_number=_http.clean(x.get("caseNumber")),
                snippet=_http.clean(x.get("title"))[:300],
                url=f"{GJK}/decisions/details/{cid}",
            ))
        note = "Constitutional Court only; search matches words in titles/summaries, not case numbers."
        if dates:
            note += " Date filters apply to the publication date on the court's site."
        return Results(items=items, total=total, note=note)

    @staticmethod
    def _title(c: dict) -> str:
        kind = _http.clean(c.get("titleFilter") or "")
        parts = [f"{COURT} {_http.clean(c.get('caseNumber'))}"]
        if _http.clean(c.get("complainant")) not in ("", "None"):
            parts.append(_http.clean(c["complainant"]))
        t = ", ".join(parts)
        return f"{t} ({kind})" if kind else t

    async def get_decision(self, id):
        cid, lang = _parse_decision_id(id)
        data = await _api("GET", f"/publish/CdmsCase/getDecisionByID/{cid}")
        if isinstance(data, list):
            data = data[0] if data else None
        if not data or not data.get("case"):
            raise NotFound(f"no Constitutional Court case with id {cid}")
        c = data["case"]
        docs = {d.get("idLanguage"): d for d in data.get("caseDocuments") or []}
        order = [lang] + [x for x in ("sq", "en", "sr") if x != lang]
        text, used, pdf = "", "", ""
        for l in order:
            d = docs.get(_LANGS[l]) or {}
            t = (d.get("documentContent") or "").strip()
            if len(t) > 200:
                text, used, pdf = t, l, d.get("documentUrl") or ""
                break
        suf = {"sq": "", "en": "EN", "sr": "SR"}[used or lang]
        summary_html = c.get("description" + suf) or c.get("description") or ""
        summary = _http.html_to_md(summary_html)
        if not text:
            text = summary or "(no text layer; see the PDF on the decision page)"
        else:
            text = _clean_pdf_text(text)
        meta = {"Language of text": used or lang, "Published": _http.iso_date(c.get("entryDate"))}
        for l, n in _LANGS.items():
            if docs.get(n, {}).get("documentUrl"):
                meta[f"PDF ({l})"] = docs[n]["documentUrl"]
        kinds = [o.get("title" + suf) or o.get("title") for o in data.get("filterCaseOptions") or []]
        if kinds:
            meta["Outcome"] = "; ".join(_http.clean(k) for k in kinds if k)
        procs = [p.get("title" + suf) or p.get("title") for p in data.get("procedureTypes") or []]
        if procs:
            meta["Procedure"] = "; ".join(_http.clean(p) for p in procs if p)
        subject = _http.clean(c.get("title" + suf) or c.get("title"))
        if subject:
            meta["Subject"] = subject
        c["titleFilter"] = (data.get("filterCaseOptions") or [{}])[0].get("title" + suf) or ""
        return Decision(
            id=id.strip(),
            title=self._title(c),
            text=text,
            url=f"{GJK}/decisions/details/{cid}",
            court=COURT,
            date=_decision_date(summary_html, c.get("entryDate") or ""),
            case_number=_http.clean(c.get("caseNumber")),
            summary=summary,
            metadata=meta,
        )

    # ----------------------------- legislation ---------------------------- #
    async def search_legislation(self, query, *, limit, page, filters):
        q = (query or "").strip()
        if not q:
            raise BadRequest("Kosovo legislation search needs words from the title, or a law "
                             "number like '04/L-077'.")
        field = str(filters.get("search_in") or "title").lower()
        if field not in _SEARCH_IN:
            raise BadRequest("search_in must be title, keywords or content")
        routed = field == "title" and _fold(q) in _LABOUR_LAW
        if routed:
            q = "03/L-212"
        so = _SEARCH_IN[field]
        start = (page - 1) * limit
        last_page = (start + limit - 1) // _PAGE + 1
        if last_page > _MAX_SOURCE_PAGES:
            raise BadRequest(f"the Gazette pages by postback; only the first "
                             f"{_MAX_SOURCE_PAGES * _PAGE} hits are reachable. Narrow the query.")
        total, rows = await self._gzk_search(q, so, last_page)
        words = [w for w in _fold(q).split() if len(w) > 2]
        loose = False
        if not rows and field == "title" and len(_fold(q).split()) > 1 and words:
            # The Gazette's phrase match returns nothing for a name with a short word in it
            # ("Kushtetuta e Republikës"); search its longest word and keep titles with every word.
            _, cand = await self._gzk_search(max(words, key=len), so, _MAX_SOURCE_PAGES)
            rows = [r for r in cand if all(w in _fold(r[1]) for w in words)]
            total = len(rows)
            loose = bool(rows)
        items = []
        for act_id, title, date in rows[start:start + limit]:
            num = re.search(r"\b(?:NR|NO|BR)\.?\s*([0-9]{2}/L-\d+|[\w-]*\d[\w./-]*)", title, re.I)
            items.append(LawHit(
                id=act_id,
                title=title,
                type=re.split(r"\s+(?=\(|[\w-]*NR\b|NR\.|NO\.|PËR\b|MBI\b|\d)", title, maxsplit=1)[0][:40],
                number=num[1] if num else "",
                date=date,
                url=f"{GZK}/ActDetail.aspx?ActID={act_id}",
            ))
        return Results(items=items, total=total,
                       note=("Recognised as the Labour Law and looked up by its number 03/L-212 "
                             "(the Gazette's title search misses it by name). " if routed else
                             "The Gazette's phrase search found nothing; matched on the longest word "
                             "and kept titles containing every word. " if loose else "")
                            + "Acts as published in the Official Gazette; amendments are separate acts. "
                            "Hits titled '(KONSOLIDUAR)' are the Gazette's consolidated texts, not "
                            "official versions. The title search matches loosely and can miss a "
                            "law's own name or English words (titles are Albanian): to find a known "
                            "law search its number, e.g. '03/L-212' (Labour Law) or '04/L-077'.")

    async def _gzk_search(self, q: str, so: str, last_page: int):
        url = f"{GZK}/SearchIn.aspx?Index=2&so={so}&s={_cp1252(q)}"
        s = first = await _gzk_get(url)
        rows = _hits(s)
        n = 1
        while n < last_page and len(rows) >= n * _PAGE:
            nxt = re.search(r"(ctl00\$MainContent\$gvAktet\$ctl\d+\$lbNext)", s)
            if not nxt:
                break
            form = _hidden(s) | {"__EVENTTARGET": nxt[1], "__EVENTARGUMENT": "",
                                 "ctl00$MainContent$txtSeach": q,
                                 "ctl00$MainContent$rblSearchOn": so}
            r = await _http.post(url, data=form)
            if r.status_code != 200:
                raise SourceError("gzk.rks-gov.net search paging failed", r.status_code)
            s = r.text
            rows += _hits(s)
            n += 1
        return _total(first), rows

    async def _act(self, id: str) -> tuple[str, list[str]]:
        act_id = (id or "").strip()
        if not re.fullmatch(r"\d+", act_id):
            raise BadRequest("Kosovo law ids are the Gazette's numeric ActID from "
                             "search_legislation, e.g. '2828' (Law 04/L-077 on Obligational Relationships).")
        if act_id in _text_cache:
            return _text_cache[act_id]
        url = f"{GZK}/ActDocumentDetail.aspx?ActID={act_id}"
        s = await _gzk_get(url)
        m = re.search(r'id="MainContent_lblActName">(.*?)</span>', s, re.S)
        title = _http.clean(_html.unescape(re.sub(r"<[^>]+>", " ", m[1]))) if m else ""
        if not title:
            raise NotFound(f"no act with ActID {act_id} in the Official Gazette")
        m = re.search(r'id="MainContent_txtDocument">(.*?)</span>', s, re.S)
        raw = m[1] if m else ""
        lines = [_http.clean(_html.unescape(re.sub(r"<[^>]+>", "", ln))) for ln in re.split(r"<br\s*/?>", raw)]
        if sum(len(x) for x in lines) < 200:
            form = _hidden(s) | {"ctl00$MainContent$imgPDF.x": "8", "ctl00$MainContent$imgPDF.y": "8"}
            r = await _http.post(url, data=form)
            if r.status_code != 200 or "pdf" not in r.headers.get("content-type", ""):
                raise SourceError(f"ActID {act_id} has no text on the Gazette site", r.status_code)
            lines = _pdf_lines(_http.pdf_text(r.content).split("\n"))
            if sum(len(x) for x in lines) < 200:
                raise SourceError(f"ActID {act_id}: the Gazette PDF has no text layer (scanned); "
                                  f"open {GZK}/ActDetail.aspx?ActID={act_id}", "no text")
        return _http.lru_put(_text_cache, act_id, (title, _paragraphs(lines)), 8)

    async def get_legislation_text(self, id):
        title, paras = await self._act(id)
        return LawText(id=id.strip(), title=title, text="\n\n".join(paras),
                       url=f"{GZK}/ActDetail.aspx?ActID={id.strip()}",
                       metadata={"Version": VERSION_CONSOLIDATED if re.search(r"konsolidu|consolidated", title, re.I)
                                 else "as published in the Official Gazette (not consolidated)"})

    async def get_legislation_toc(self, id):
        title, paras = await self._act(id)
        entries = []
        for kind, label, text in _structure(paras):
            if kind == "heading":
                entries.append(TocEntry(title=text, level=0))
            elif kind == "article":
                entries.append(TocEntry(title=text, level=1, provision=label))
        return Toc(id=id.strip(), title=title, url=f"{GZK}/ActDetail.aspx?ActID={id.strip()}",
                   entries=entries)

    async def get_legislation_provision(self, id, provision):
        title, paras = await self._act(id)
        want = _norm_label(provision)
        struct = _structure(paras)
        for i, (kind, label, _t) in enumerate(struct):
            if kind == "article" and label.lower() == want:
                body = []
                for k2, _l2, t2 in struct[i + 1:]:
                    if k2 != "para":
                        break
                    body.append(t2)
                text = "\n\n".join([f"**{struct[i][2]}**"] + body)
                return Provision(law_id=id.strip(), law_title=title, provision=label, text=text,
                                 url=f"{GZK}/ActDetail.aspx?ActID={id.strip()}")
        raise NotFound(f"no article {provision!r} in ActID {id}; see get_legislation_toc")


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _fold(q: str) -> str:
    return " ".join(unicodedata.normalize("NFKD", q).encode("ascii", "ignore").decode().lower().split())


def _cp1252(q: str) -> str:
    """The Gazette decodes ?s= as Windows-1252; fold what that cannot hold (č, ć, đ)."""
    out = []
    for ch in q:
        try:
            ch.encode("cp1252")
            out.append(ch)
        except UnicodeEncodeError:
            out.append(unicodedata.normalize("NFKD", ch).encode("ascii", "ignore").decode() or " ")
    return quote("".join(out), encoding="cp1252")


async def _gzk_get(url: str) -> str:
    r = await _http.get(url)
    if r.status_code != 200:
        raise SourceError("gzk.rks-gov.net request failed", r.status_code)
    return r.text


def _hidden(s: str) -> dict[str, str]:
    return {m[1]: _html.unescape(m[2]) for m in
            re.finditer(r'<input type="hidden" name="([^"]+)" id="[^"]*" value="([^"]*)"', s)}


def _total(s: str) -> int | None:
    m = re.search(r'id="MainContent_lblActCount">\s*(\d+)', s)
    return int(m[1]) if m else None


def _hits(s: str) -> list[tuple[str, str, str]]:
    out = []
    for m in re.finditer(r'id="MainContent_gvAktet_hlActi_(\d+)" href="ActDetail\.aspx\?ActID=(\d+)">(.*?)</a>'
                         r'(.*?)(?=id="MainContent_gvAktet_hlActi_|$)', s, re.S):
        d = re.search(r'lblgaPublishedDate_\d+">([^<]*)<', m[4])
        out.append((m[2], _http.clean(_html.unescape(m[3])), _http.iso_date(d[1]) if d else ""))
    return out


_PAGE_NO = re.compile(r"^[-–]?\s*[ivxlc\d]{1,4}\s*[-–]?$", re.I)
_TOC_LINE = re.compile(r"\.{5,}\s*\d*\s*$|\]\s*\.+\s*\d+\s*$")
_RUNNING_HEAD = re.compile(r"^(GAZETA ZYRTARE|SLU[ŽZ]BENI LIST|OFFICIAL GAZETTE)\b.*/", re.I)
_ARTICLE = re.compile(r"^(?:Neni|NENI|Article|ARTICLE|Član|ČLAN|Člen|Madde|MADDE)\s+(\d+[a-zA-Z]?)\.?\s*(\[[^\]]*\])?\s*$")
_HEADING = re.compile(r"^(?:KAPITULLI|PJESA|LIBRI|TITULLI|NËNKAPITULLI|CHAPTER|PART|BOOK|TITLE|"
                      r"GLAVA|POGLAVLJE|DEO|DIO|KNJIGA)\s+[IVXLC\d]+\.?(?:\s|$)(?!.*[,;]\s*$)", re.I)


def _paragraphs(lines: list[str]) -> list[str]:
    """PDF lines -> paragraphs: drop page numbers, running heads and TOC leader lines,
    join wrapped lines, and give article and chapter headings their own paragraph."""
    paras, cur, seen_head = [], [], False

    def flush():
        if cur:
            paras.append(_http.clean(" ".join(cur)))
            cur.clear()

    for ln in lines:
        if not ln:
            flush()
            continue
        if _PAGE_NO.match(ln) or _TOC_LINE.search(ln):
            continue
        if _RUNNING_HEAD.match(ln):
            if seen_head:
                continue
            seen_head = True
        if _ARTICLE.match(ln) or _HEADING.match(ln):
            flush()
            cur.append(ln)
            if _ARTICLE.match(ln) and _ARTICLE.match(ln)[2]:   # "Neni 8 [Shteti Laik]" is complete
                flush()
            continue
        cur.append(ln)
    flush()
    return [p for p in paras if p]


def _pdf_lines(lines: list[str]) -> list[str]:
    """pdf_text drops blank lines; put paragraph breaks back before headings and
    numbered paragraphs, and after an article's title line."""
    out, title_next = [], False
    for ln in lines:
        art = _ARTICLE.match(ln)
        if art or _HEADING.match(ln):
            out += ["", ln]
            title_next = bool(art and not art[2])
            continue
        if title_next:
            out += [ln, ""]
            title_next = False
            continue
        if re.match(r"^(\d+(\.\d+)*\.|\(\d+\)|[a-z]\))\s", ln):
            out.append("")
        out.append(ln)
    return out


def _structure(paras: list[str]) -> list[tuple[str, str, str]]:
    """(kind, label, text) per paragraph; kind is article / heading / para. An article
    heading paragraph is "Neni 1 Fushë veprimtaria e ligjit"; repeated numbers (amending
    acts quoting articles) get labels like "5 (2)"."""
    out, seen = [], {}
    for p in paras:
        first = p.split(" [")[0]
        m = re.match(r"^(?:Neni|NENI|Article|ARTICLE|Član|ČLAN|Člen|Madde|MADDE)\s+(\d+[a-zA-Z]?)\b", first)
        if m and len(p) <= 200 and not re.search(r"[.;:]\s*$", p.split("]")[-1] if "]" in p else p):
            n = m[1].lower()
            seen[n] = seen.get(n, 0) + 1
            label = n if seen[n] == 1 else f"{n} ({seen[n]})"
            out.append(("article", label, p))
        elif _HEADING.match(p) and len(p) <= 200:
            out.append(("heading", "", p))
        else:
            out.append(("para", "", p))
    return out


def _norm_label(provision: str) -> str:
    p = _http.clean(provision).lower()
    p = re.sub(r"^(neni|article|art\.?|član|člen|madde|nr\.?|no\.?)\s*", "", p)
    return p.strip(" .")


def _clean_pdf_text(t: str) -> str:
    """Court PDF text: lines with trailing spaces, blank-line paragraphs, page numbers."""
    lines = [_http.clean(ln) for ln in t.replace("\r", "").split("\n")]
    out, cur = [], []
    for ln in lines:
        if not ln:
            if cur:
                out.append(" ".join(cur))
                cur = []
            continue
        if re.fullmatch(r"\d{1,3}", ln):
            continue
        cur.append(ln)
    if cur:
        out.append(" ".join(cur))
    return "\n\n".join(out)
