"""Philippines: Supreme Court decisions and statutes from the LawPhil Project (lawphil.net).

NON-OFFICIAL source. LawPhil is run by the Arellano Law Foundation (a private, non-profit
law-school foundation), not by the State. It is used because no official route is open to
an automated client (checked 2026-11-05/06):
  * sc.judiciary.gov.ph (Supreme Court site): CloudFront "403 Request blocked" for this
    project's User-Agent, robots.txt included.
  * officialgazette.gov.ph: Cloudflare managed challenge ("Just a moment...") on every
    path, robots.txt included.
  * elibrary.judiciary.gov.ph (SC E-Library): pages load without a login and there is no
    robots.txt (404), but its FAQ (elibrary.judiciary.gov.ph/aboutus/faq) says: "Only
    authorized users can access the E-Library, which has the full text search and
    retrieval function. All others may access only the non-searchable decisions in the
    Jurisprudence Section of the Supreme Court Main Website." That is an access restriction
    needing authorisation, so it is not used.

LawPhil terms (lawphil.net/copyright.html): "The collection is licensed under a Creative
Commons Attribution-Non Commercial 4.0 Philippine license. Statutes, Issuances and Court
Decisions are works of the Philippine Government." The acceptable-use policy and disclaimer
are silent on automated access. No robots.txt (404).

How the site works (the site's own pages call these JSON endpoints, no key):
  * GET https://lawphil.net/api/public/<module>?search=&year=&month=&rows=&page=&sort=desc
    -> Laravel paginator {data, total, current_page, last_page}. `search` is a substring
    match over number / title / parties; no relevance ranking (sorted by date).
    Modules: jurisprudence (SC decisions 1901-), republic, acts, commonwealth,
    bataspambansa, presidential, execord.
  * Documents are static windows-1252 HTML: judjuris/juri2023/mar2023/gr_171746-48_2023.html,
    statutes/repacts/ra2012/ra_10173_2012.html. Recent items may be PDF only
    (.../pdf/<file>.pdf), read through the PDF text layer.
Ids are LawPhil's own file stems: decisions "juri2023/mar2023/gr_171746-48_2023",
laws "ra_10173_2012", "pd_442_1974", "eo_209_1987", plus "cons1987" for the Constitution.
Statute texts are as enacted (LawPhil notes amendments at the top), not consolidated.
"""
from __future__ import annotations

import html as _html
import re

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc, TocEntry

HOST = "lawphil.net"
SITE = f"https://{HOST}"
API = f"{SITE}/api/public"
COURT = "Supreme Court of the Philippines"
WARNING = ("Non-official source: the LawPhil Project (Arellano Law Foundation), CC BY-NC 4.0 "
           "(non-commercial use, attribution required). Check against the official printed text.")

# law-id prefix -> (API module, number field, title field, folder, per-year subfolder prefix, label)
LAW_TYPES = {
    "ra": ("republic", "ra_number", "description", "statutes/repacts", "ra", "Republic Act"),
    "act": ("acts", "act_number", "description", "statutes/acts", "act", "Act"),
    "ca": ("commonwealth", "ca_number", "description", "statutes/comacts", "ca", "Commonwealth Act"),
    "bp": ("bataspambansa", "bp_number", "description", "statutes/bataspam", "bp", "Batas Pambansa"),
    "pd": ("presidential", "pd_number", "citation", "statutes/presdecs", "pd", "Presidential Decree"),
    "eo": ("execord", "execord_number", "description", "executive/execord", "eo", "Executive Order"),
}
_TYPE_WORDS = [
    ("ra", r"r\.?\s*a\.?|republic\s+act"),
    ("ca", r"c\.?\s*a\.?|commonwealth\s+act"),
    ("bp", r"b\.?\s*p\.?|batas\s+pambansa"),
    ("pd", r"p\.?\s*d\.?|presidential\s+decree"),
    ("eo", r"e\.?\s*o\.?|executive\s+order"),
    ("act", r"act"),
]
_CODES = {"revised penal code": ("act", "3815"), "labor code": ("pd", "442"),
          "civil code": ("ra", "386"), "family code": ("eo", "209")}
CONSTITUTIONS = {"cons1987": "1987 Constitution of the Republic of the Philippines",
                 "cons1973": "1973 Constitution of the Republic of the Philippines",
                 "cons1943": "1943 Constitution of the Republic of the Philippines",
                 "cons1935": "1935 Constitution of the Philippines"}
_LAW_ID = re.compile(r"^(ra|act|ca|bp|pd|eo)_([\w.-]+?)_(\d{4})$")
_DEC_ID = re.compile(r"^juri(\d{4})/([a-z]{3})\1/([\w.-]+)$")
_MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
_doc_cache: dict = {}
_CASE_NO = re.compile(r"\d")


# --------------------------------------------------------------------------- #
# fetching
# --------------------------------------------------------------------------- #
async def _api(module: str, params: dict) -> dict:
    r = await _http.get(f"{API}/{module}", params=params)
    if r.status_code != 200:
        raise SourceError(_http.error("lawphil.net", f"{module} search failed", r.status_code), r.status_code)
    try:
        d = r.json()
    except ValueError:
        raise SourceError(_http.error("lawphil.net", f"{module} search: not JSON", r.status_code), r.status_code)
    if not isinstance(d, dict) or not isinstance(d.get("data"), list):
        raise SourceError(f"lawphil.net {module} search: unexpected payload {str(d)[:200]}")
    return d


async def _document(html_url: str, pdf_url: str) -> tuple[str, str, str]:
    """(kind, content, url): kind "html" (decoded HTML) or "pdf" (text layer); cached."""
    if html_url in _doc_cache:
        return _doc_cache[html_url]
    r = await _http.get(html_url)
    if r.status_code == 200 and "<html" in r.text[:2000].lower():
        out = ("html", r.content.decode("windows-1252", errors="replace"), html_url)
        return _http.lru_put(_doc_cache, html_url, out, 16)
    if r.status_code not in (200, 404):
        raise SourceError(_http.error("lawphil.net", "document fetch failed", r.status_code), r.status_code)
    if pdf_url:
        p = await _http.get(pdf_url)
        if p.status_code == 200 and p.content[:5] == b"%PDF-":
            txt = _http.pdf_text(p.content)
            if not txt:
                txt = f"LawPhil has this document only as a scanned PDF (no text layer): {pdf_url}"
            return _http.lru_put(_doc_cache, html_url, ("pdf", txt, pdf_url), 16)
        if p.status_code not in (200, 404):
            raise SourceError(_http.error("lawphil.net", "PDF fetch failed", p.status_code), p.status_code)
    raise NotFound(f"LawPhil has no document at {html_url}.")


def _body_html(page: str) -> str:
    """The document body: inside the page's main <blockquote>, minus the LawPhil footer."""
    m = re.search(r"(?is)<blockquote>(.*)</blockquote>", page)
    body = m[1] if m else page
    body = re.split(r'(?i)<a class="id">', body)[0]
    body = re.sub(r'(?is)<a class="nt">\s*(\d+)\s*</a>', r" [\1]", body)   # footnote marks
    body = re.sub(r"(?is)<hr[^>]*>", "", body)
    return body.replace("&#9;", " ").replace("\t", " ")


def _paras(page: str) -> list[str]:
    return [p for p in _http.html_paragraphs(_body_html(page)) if p.strip("* _")]


def _meta(page: str, name: str) -> str:
    m = re.search(rf'(?is)<meta\s+name="{name}"\s+content="([^"]*)"', page)
    return _http.clean(_html.unescape(m[1])) if m else ""


def _title_tag(page: str) -> str:
    m = re.search(r"(?is)<title>(.*?)</title>", page)
    return _http.clean(_html.unescape(m[1])) if m else ""


def _strip_tags(s: str) -> str:
    return _http.clean(_html.unescape(re.sub(r"<[^>]+>", " ", s or "")))


# --------------------------------------------------------------------------- #
# case law helpers
# --------------------------------------------------------------------------- #
def _dec_id(raw: str) -> str:
    s = str(raw or "").strip().replace("\\", "/")
    s = re.sub(r"^https?://(www\.)?lawphil\.net/judjuris/", "", s)
    s = re.sub(r"\.(html?|pdf)$", "", s).replace("/pdf/", "/")
    if not _DEC_ID.match(s):
        raise BadRequest("Use a LawPhil decision id from search_caselaw, e.g. "
                         "'juri2023/mar2023/gr_171746-48_2023', or a lawphil.net/judjuris/... URL.")
    return s


def _dec_urls(did: str) -> tuple[str, str]:
    folder, stem = did.rsplit("/", 1)
    return f"{SITE}/judjuris/{did}.html", f"{SITE}/judjuris/{folder}/pdf/{stem}.pdf"


def _case_no_from_stem(did: str) -> str:
    stem = did.rsplit("/", 1)[1]
    m = re.match(r"^(gr|am|ac|bm|oca|ipi|udk)_(.+)_\d{4}$", stem)
    if not m:
        return ""
    kind = {"gr": "G.R. No.", "am": "A.M. No.", "ac": "A.C. No.", "bm": "B.M. No."}.get(m[1], m[1].upper() + " No.")
    return f"{kind} {m[2].upper()}"


def _dec_hit(r: dict) -> DecisionHit | None:
    path = (r.get("url") or r.get("pdf_path") or "").replace("\\", "/")
    try:
        did = _dec_id(path)
    except BadRequest:
        return None
    num = _http.clean(r.get("gr_number") or r.get("am_number") or "") or _case_no_from_stem(did)
    title = _strip_tags(r.get("citation")) or f"{COURT} {num}"
    html_url, pdf_url = _dec_urls(did)
    snippet = "; ".join(x for x in (f"Ponente: {r['ponente']}" if r.get("ponente") else "",
                                    _strip_tags(r.get("reference"))) if x)
    return DecisionHit(id=did, title=title, court=COURT, date=_http.iso_date(r.get("date")),
                       case_number=num, snippet=snippet,
                       url=html_url if r.get("url") else pdf_url)


# --------------------------------------------------------------------------- #
# legislation helpers
# --------------------------------------------------------------------------- #
def _law_id(raw: str) -> str:
    s = str(raw or "").strip()
    s = re.sub(r"^https?://(www\.)?lawphil\.net/.*/", "", s)
    s = re.sub(r"\.(html?|pdf)$", "", s).lower()
    if s in CONSTITUTIONS or _LAW_ID.match(s):
        return s
    raise BadRequest("Use a LawPhil law id from search_legislation, e.g. 'ra_10173_2012' "
                     "(Data Privacy Act), 'ra_386_1949' (Civil Code), 'pd_442_1974', "
                     "'eo_209_1987', or 'cons1987' for the 1987 Constitution.")


def _law_urls(lid: str) -> tuple[str, str]:
    if lid in CONSTITUTIONS:
        return f"{SITE}/consti/{lid}.html", ""
    m = _LAW_ID.match(lid)
    _, _, _, folder, sub, _ = LAW_TYPES[m[1]]
    base = f"{SITE}/{folder}/{sub}{m[3]}"
    return f"{base}/{lid}.html", f"{base}/pdf/{lid}.pdf"


def _law_hit(kind: str, r: dict) -> LawHit | None:
    _, numkey, titlekey, folder, sub, label = LAW_TYPES[kind]
    path = (r.get("url") or r.get("pdf_path") or "").replace("\\", "/")
    stem = re.sub(r"\.(html?|pdf)$", "", path.rsplit("/", 1)[-1]).lower()
    if not _LAW_ID.match(stem):
        return None
    number = _http.clean(r.get(numkey))
    desc = _strip_tags(r.get(titlekey) or r.get("description") or r.get("citation"))
    html_url, pdf_url = _law_urls(stem)
    return LawHit(id=stem, title=f"{number}: {desc}" if desc else number or stem, type=label,
                  number=number, date=_http.iso_date(r.get("date")),
                  snippet=_http.clean(r.get("tenure") or ""),
                  url=html_url if r.get("url") else pdf_url)


_PROV = re.compile(r"^\**\s*(Article|Art|Section|Sec|SECTION|ARTICLE|SEC|ART)\s*\.?\s*(\d+[A-Za-z]?(?:-[A-Za-z0-9]+)?)\s*\.",
                   re.I)
_HEAD = re.compile(r"^\**\s*(PRELIMINARY\s+TITLE|PRELIMINARY\s+ARTICLE|BOOK|TITLE|CHAPTER|PART|ARTICLE|RULE|SUBCHAPTER)\b"
                   r"\s*([IVXLC]+|\d+|[A-Z]+)?", re.I)


def _norm_label(kind: str, num: str) -> str:
    return f"{'Article' if kind.lower().startswith('art') else 'Section'} {num.upper() if num[-1:].isalpha() and len(num) <= 3 else num}"


def _structure(paras: list[str]) -> tuple[list[TocEntry], dict[str, list[str]]]:
    """Split law paragraphs into provisions: (toc, label -> paragraphs). Headings
    (BOOK/TITLE/CHAPTER, constitution "ARTICLE III") end the current provision; a
    repeated label gets " (2)", " (3)"."""
    toc: list[TocEntry] = []
    provs: dict[str, list[str]] = {}
    cur: list[str] | None = None
    article = ""          # constitution: sections are numbered per ARTICLE heading
    for p in paras:
        plain = p.replace("*", "").replace("_", "").strip()
        art_head = re.match(r"ARTICLE\s+([IVXLC]+)\b", plain)
        m = None if art_head else _PROV.match(plain)
        if m:
            label = _norm_label(m[1], m[2])
            if label.startswith("Section") and article:
                label = f"{article}, {label}"
            final, n = label, 1
            while final in provs:
                n += 1
                final = f"{label} ({n})"
            cur = provs[final] = [p]
            toc.append(TocEntry(title=_http.clean(plain)[:160], level=1, provision=final))
            continue
        h = _HEAD.match(plain)
        if art_head or (h and len(plain) < 200 and (plain[:6].isupper() or (h[2] and len(plain) < 120))):
            if art_head:
                article = f"Article {art_head[1]}"
            toc.append(TocEntry(title=_http.clean(plain)[:160], level=0))
            cur = None
            continue
        if cur is not None:
            cur.append(p)
    return toc, provs


async def _law(lid: str) -> dict:
    html_url, pdf_url = _law_urls(lid)
    kind, content, url = await _document(html_url, pdf_url)
    if kind == "html":
        paras = _paras(content)
        title = _meta(content, "description") or _title_tag(content)
        title = re.sub(r"^[A-Za-z ]+ - ", "", title) if " - " in title[:40] else title
        name = _title_tag(content)
        if lid in CONSTITUTIONS:
            title = CONSTITUTIONS[lid]
        elif name and title and name.lower() not in title.lower():
            title = f"{_http.clean(name)}: {title}"
    else:
        paras = [ln for ln in content.split("\n") if ln.strip()]
        title = lid
    if not paras:
        raise SourceError(f"lawphil.net: no text found in {url}")
    toc, provs = _structure(paras)
    return {"title": title or lid, "url": url, "paras": paras, "toc": toc, "provs": provs}


def _match_provision(provs: dict[str, list[str]], provision: str) -> str:
    want = _http.clean(provision)
    if want in provs:
        return want
    low = {k.lower(): k for k in provs}
    if want.lower() in low:
        return low[want.lower()]
    m = re.fullmatch(r"(?i)(?:(art(?:icle)?|sec(?:tion)?|s)\.?\s*)?(\d+[a-z]?(?:-[a-z0-9]+)?)", want)
    if m:
        num = m[2].upper() if m[2][-1:].isalpha() and len(m[2]) <= 3 else m[2]
        kinds = (["Article"] if m[1] and m[1].lower().startswith("art")
                 else ["Section"] if m[1] else ["Article", "Section"])
        for k in kinds:
            if f"{k} {num}" in provs:
                return f"{k} {num}"
        # constitution-style "Article III, Section 1": a bare number is ambiguous
        cands = [k for k in provs if k.endswith(f"Section {num}")]
        if len(cands) == 1:
            return cands[0]
    raise NotFound(f"No provision {provision!r} in this law. Use a label from get_legislation_toc, "
                   "e.g. 'Article 1', 'Section 2' or (Constitution) 'Article III, Section 1'.")


def _parse_law_query(q: str) -> tuple[str, str] | None:
    """'RA 10173' / 'Republic Act No. 386' / 'P.D. 442' -> ("ra", "10173")."""
    for kind, words in _TYPE_WORDS:
        m = re.fullmatch(rf"(?i)\s*(?:{words})\s*(?:no\.?|blg\.?|number)?\s*(\d+[a-z]?)\s*", q)
        if m:
            return kind, m[1]
    return None


# --------------------------------------------------------------------------- #
class Philippines(Jurisdiction):
    code = "ph"
    name = "Philippines"
    languages = ("en", "fil")
    aliases = ("philippines", "republic of the philippines", "phl", "pilipinas", "lawphil")
    sources = (
        Source(
            name="The LawPhil Project (lawphil.net), Arellano Law Foundation: non-official (NGO)",
            url=SITE,
            covers=("caselaw", "legislation"),
            licence="CC BY-NC 4.0 (Philippines) for the collection; the texts are works of the "
                    "Philippine Government",
            commercial_use=False,
            ai_use=None,   # no robots.txt (404), no AI/TDM clause in the terms
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~40 requests (2026-11)",
            terms_url=f"{SITE}/copyright.html",
            warning=WARNING,
            official=False,
        ),
    )
    caselaw_filters = {
        "year": "decision year, e.g. '2023' (one year only, no ranges: search each year in turn)",
        "month": "decision month 1-12 (use with year)",
    }
    legislation_filters = {
        "type": "ra (Republic Acts, default), act (Acts 1900-1935), ca (Commonwealth Acts), "
                "bp (Batas Pambansa), pd (Presidential Decrees), eo (Executive Orders)",
        "year": "year of enactment, e.g. '2012'",
    }
    min_interval = {HOST: 1.0}
    notes = ("Non-official: LawPhil (Arellano Law Foundation, CC BY-NC). Supreme Court decisions "
             "1901-present and statutes as enacted (RA, Acts, CA, BP, PD, EO, Constitutions). "
             "Official SC/Official Gazette sites block automated clients; the SC E-Library is "
             "restricted to authorised users.")
    gaps = (
        "Official Supreme Court site (sc.judiciary.gov.ph): CloudFront blocks our client (403); "
         "non-official LawPhil used",
        "Official Gazette (officialgazette.gov.ph): Cloudflare bot check on every path",
        "SC E-Library full-text search: needs permission ('Only authorized users can access the "
         "E-Library')",
        "Court of Appeals, Sandiganbayan, Court of Tax Appeals and lower courts: not researched "
         "yet",
        "Consolidated statutes: LawPhil has texts as enacted only; official source not researched"
         " yet",
    )
    samples = {
        "caselaw_query": "Estrada",
        "decision_id": "juri2023/mar2023/gr_171746-48_2023",
        "legislation_query": "data privacy",
        "law_id": "ra_10173_2012",
        "provision": "Section 3",
    }

    # ------------------------------------------------------------------ #
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        f = {k: str(v).strip() for k, v in (filters or {}).items() if str(v).strip()}
        limit = max(1, min(int(limit), 50))
        params = {"search": (query or "").strip(), "rows": limit, "page": max(1, int(page)), "sort": "desc"}
        if "year" in f:
            if not re.fullmatch(r"(19|20)\d{2}", f["year"]):
                raise BadRequest(f"year must be a 4-digit year like '2023', got {f['year']!r}.")
            params["year"] = f["year"]
        if "month" in f:
            mo = f["month"].lower()[:3]
            mo = str(_MONTHS.index(mo) + 1) if mo in _MONTHS else f["month"]
            if not re.fullmatch(r"([1-9]|1[0-2])", mo):
                raise BadRequest(f"month must be 1-12, got {f['month']!r}.")
            params["month"] = mo
        d = await _api("jurisprudence", params)
        order = "newest first"
        words = (query or "").strip()
        if words and 1 < (d.get("total") or 0) <= 50:
            # substring matches come back by date: put whole-phrase party-name matches first
            if len(d["data"]) < d["total"]:
                d = await _api("jurisprudence", {**params, "rows": 50, "page": 1})
            pat = re.compile(rf"(?<!\w){re.escape(words)}(?!\w)", re.I)
            rows = sorted(d["data"], key=lambda r: not pat.search(_strip_tags(r.get("citation"))))
            start = (params["page"] - 1) * limit
            d = {**d, "data": rows[start:start + limit]}
            order = "whole-phrase party-name matches first, then newest first"
        items = [h for h in (_dec_hit(r) for r in d["data"]) if h]
        note = ("Supreme Court decisions via LawPhil (non-official). Search matches only case numbers "
                f"and party names (not subject matter or the full text); {order}. The year filter takes "
                "one year, no ranges.")
        if items and words and not _CASE_NO.search(words):
            note += (" These hits matched the words in the party names (or case number), NOT the legal "
                     "issue: open a decision with get_decision before assuming it is on your topic.")
        if not items:
            note += (" Subject/topic searches (e.g. 'illegal dismissal') cannot work here: search a "
                     "party name or G.R. number instead, or leave the query empty and set year (and "
                     "month) to list that period's decisions newest first, then open them with "
                     "get_decision and read for the topic. LawPhil has no subject index.")
        return Results(items=items, total=d.get("total"), note=note)

    async def get_decision(self, id):
        did = _dec_id(id)
        html_url, pdf_url = _dec_urls(did)
        kind, content, url = await _document(html_url, pdf_url)
        meta: dict[str, str] = {"Source": "LawPhil Project (non-official), CC BY-NC 4.0"}
        if kind == "html":
            paras = _paras(content)
            text = "\n\n".join(paras)
            title = _meta(content, "subject") or _meta(content, "description")
            case_no = _title_tag(content)
            head = next((p for p in paras[:8] if re.search(r"\[\s*(G\.\s*R|A\.\s*M|A\.\s*C|B\.\s*M)", p)), "")
            date = _http.en_date(head) or _http.en_date(" ".join(paras[:8]))
            div = next((p for p in paras[:5] if re.search(r"(?i)DIVISION|EN BANC", p)), "")
            if div:
                meta["Division"] = _http.clean(div.replace("*", ""))
            m = re.search(r"^\*\*([^*]+?),?\s*\*?J\.?", "\n".join(paras[:20]), re.M)
            if m:
                meta["Ponente"] = _http.clean(m[1]).rstrip(",")
            meta["PDF"] = pdf_url
        else:
            text = content
            title = ""
            case_no = _case_no_from_stem(did)
            date = _http.en_date(content[:1500])
        if not text.strip():
            raise SourceError(f"lawphil.net: empty decision page {url}")
        case_no = case_no or _case_no_from_stem(did)
        return Decision(id=did, title=_http.clean(title) or f"{COURT} {case_no}", text=text, url=url,
                        court=COURT, date=date, case_number=case_no, metadata=meta)

    # ------------------------------------------------------------------ #
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        f = {k: str(v).strip().lower() for k, v in (filters or {}).items() if str(v).strip()}
        q = (query or "").strip()
        kind = f.get("type", "")
        if kind and kind not in LAW_TYPES:
            raise BadRequest(f"type must be one of {', '.join(LAW_TYPES)}, got {kind!r}.")
        exact = _parse_law_query(q)
        if not exact:
            # the base codes are not found by name (amending laws match first; RPC has no "Revised")
            name = re.sub(r"[^a-z ]", "", q.lower()).strip()
            name = re.sub(r" of the philippines$", "", name)
            exact = _CODES.get(name)
        if exact and (not kind or kind == exact[0]):
            kind, q = exact[0], exact[1]
        kind = kind or "ra"
        module, numkey = LAW_TYPES[kind][0], LAW_TYPES[kind][1]
        limit = max(1, min(int(limit), 50))
        params = {"search": q, "rows": limit, "page": max(1, int(page)), "sort": "desc"}
        if "year" in f:
            if not re.fullmatch(r"1[89]\d{2}|20\d{2}", f["year"]):
                raise BadRequest(f"year must be a 4-digit year like '2012', got {f['year']!r}.")
            params["year"] = f["year"]
        if exact and kind == exact[0]:
            # the API matches substrings ("386" also finds 10386): fetch more, keep exact numbers
            params.update(rows=50, page=1)
            d = await _api(module, params)
            rows = [r for r in d["data"]
                    if re.search(rf"(?:No\.|Blg\.)\s*{re.escape(q)}$", _http.clean(r.get(numkey)), re.I)]
            items = [h for h in (_law_hit(kind, r) for r in rows) if h]
            start = (max(1, int(page)) - 1) * limit
            return Results(items=items[start:start + limit], total=len(items),
                           note=f"{LAW_TYPES[kind][5]} {q} via LawPhil (non-official), as enacted.")
        d = await _api(module, params)
        items = [h for h in (_law_hit(kind, r) for r in d["data"]) if h]
        return Results(items=items, total=d.get("total"),
                       note=(f"Searched {LAW_TYPES[kind][5]}s only (filter type: ra, act, ca, bp, pd, eo). "
                             "Title/number match, newest first; texts as enacted, not consolidated. "
                             "1987 Constitution: id 'cons1987'."))

    async def get_legislation_toc(self, id):
        lid = _law_id(id)
        law = await _law(lid)
        return Toc(id=lid, title=law["title"], url=law["url"], entries=law["toc"])

    async def get_legislation_provision(self, id, provision):
        lid = _law_id(id)
        law = await _law(lid)
        label = _match_provision(law["provs"], provision)
        return Provision(law_id=lid, law_title=law["title"], provision=label,
                         text="\n\n".join(law["provs"][label]), url=law["url"],
                         note="Text as enacted, not consolidated: later amendments are not applied "
                              "(LawPhil lists them at the top of the full text; LawPhil is non-official).")

    async def get_legislation_text(self, id):
        lid = _law_id(id)
        law = await _law(lid)
        return LawText(id=lid, title=law["title"], text="\n\n".join(law["paras"]), url=law["url"],
                       metadata={"Source": "LawPhil Project (non-official), CC BY-NC 4.0",
                                 "Version": "as enacted (not consolidated)"})
