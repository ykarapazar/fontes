"""ICJ (International Court of Justice, The Hague): case records and the document
search on www.icj-cij.org. Case law, plus the Statute and the Rules of Court (HTML pages); the ICJ is an international court, not a country.

What the site gives a plain HTTP client (checked 2026-11-05/06):
  * Document search: GET /advanced-search?search_api_fulltext=...&field_document_group_type=..
    &field_doc_incidental_proceedings=..&field_date_of_the_document[min|max]=YYYY-MM-DD
    &items_per_page=10|25|50|100&page=<0-based> -> server-rendered HTML (Drupal Search API),
    "About N results", one row per document: title, PDF link, case link, type, ISO date.
    The full-text index appears to cover the PDFs' contents (hits mention words only found
    inside the judgment).
  * Case record: GET /case/{n} -> HTML listing every document of the case (title, date,
    description, procedure, language files, appended opinions). Concluded cases group them
    under type headings; pending cases list them under "Latest Developments". An unknown
    case number answers HTTP 500, not 404.
  * Every judgment, order, advisory opinion, summary and press release is a PDF under
    /sites/default/files/case-related/{n}/{NNN}-{yyyymmdd}-{type}-{seq}-{sub}-{lang}.pdf.
    Those PDFs answer 403 with `cf-mitigated: challenge` (a Cloudflare bot challenge) to
    this client. We do not get around that: no PDF text is fetched. get_decision returns
    the HTML metadata and the PDF links for a human to open.

Ids: a case is its ICJ case number ("178"); a document is its file name without the
language suffix, lower-cased ("178-20220722-jud-01-00"; appended opinions "...-01-01").
"""
from __future__ import annotations

import re
from urllib.parse import urlencode

from lxml import html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc, TocEntry

HOST = "www.icj-cij.org"
BASE = f"https://{HOST}"
COURT = "International Court of Justice"

_DOC_ID = re.compile(r"^0*(\d+)-(\d{8})-([a-z]{3})-(\d{2})-(\d{2})$")
_FILE = re.compile(r"/(\d+-\d{8}-[A-Za-z]{3}-\d{2}-\d{2})-([A-Za-z]+)\.pdf$")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# file-name type code -> section label (used when a pending case lists everything
# under "Latest Developments")
_KINDS = {
    "jud": "Judgments", "adv": "Advisory opinions", "ord": "Orders", "sum": "Summaries",
    "pre": "Press releases", "app": "Institution of proceedings", "spe": "Institution of proceedings",
    "req": "Institution of proceedings", "wri": "Written proceedings", "int": "Intervention",
    "ora": "Oral proceedings", "cor": "Correspondence", "oth": "Other documents",
}
_ORDER = ["Judgments", "Advisory opinions", "Orders", "Summaries", "Press releases",
          "Institution of proceedings", "Written proceedings", "Intervention",
          "Oral proceedings", "Correspondence", "Other documents"]
_DECISION_KINDS = ("jud", "adv", "ord")

# search filter values -> the site's own option ids
_TYPES = {
    # 492 is labelled "Judgments, Advisory Opinions and Orders" but the site returns only
    # judgments + advisory opinions for it (185 = 153 + 32, no orders; with a proceedings filter 0).
    # 493 is the real union (868 = 683 orders + 153 + 32).
    "decisions": "493",
    "decisions_with_opinions": "493",
    "judgments": "486", "advisory_opinions": "489", "orders": "483",
    "opinions": "494",             # opinions and declarations appended to decisions
    "summaries": "495", "press_releases": "496",
    "applications": "477", "written": "480", "oral": "482", "other": "481",
    "correspondence": "497", "all": "All",
}
_PROCEEDINGS = {
    "provisional_measures": "409", "preliminary_objections": "410", "counter_claims": "411",
    "intervention": "412", "discontinuance": "414", "jurisdiction_admissibility": "413",
}

_case_cache: dict = {}
_case_ids: dict[str, str] = {}   # ICJ case number -> the search form's internal case option id
_case_names: dict[str, str] = {}  # ICJ case number -> case name

_STOP = {"the", "and", "for", "case", "cases", "v", "vs", "versus", "judgment", "judgments", "order",
         "orders", "icj", "court", "decision", "merits", "provisional", "measures", "advisory", "opinion"}


def _tokens(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]{3,}", s.lower()) if w not in _STOP}


async def _load_cases() -> None:
    if not _case_ids:
        r = await _http.get(f"{BASE}/advanced-search")
        if r.status_code != 200 or "cf-mitigated" in r.headers:
            raise SourceError(_http.error("ICJ", "case list failed", r.status_code), r.status_code)
        for o in lhtml.fromstring(r.text).xpath("//select[@id='select-case-list']/option"):
            m = re.match(r"\s*(\d+)\s*-", o.text or "")
            if m:
                _case_ids[m[1]] = o.get("value")
                _case_names[m[1]] = re.sub(r"^\s*\d+\s*-\s*\d+\s*-\s*", "", o.text or "")


async def _match_cases(query: str) -> list[str]:
    """Case numbers whose name best matches the party/subject words of the query: at most 3 cases
    and at least half of the query's words, else none (the query is then a plain text search)."""
    q = _tokens(query)
    if not q:
        return []
    await _load_cases()
    hits = {n: len(q & _tokens(name)) for n, name in _case_names.items()}
    best = max(hits.values(), default=0)
    top = [n for n, h in hits.items() if h == best]
    # several cases may share one title (e.g. 4 "Armed Activities" cases): a 3+ word match allows up to 5
    return top if best and best * 2 >= len(q) and len(top) <= (5 if best >= 3 else 3) else []


async def _case_option(n: str) -> str:
    """The advanced-search form lists every case as <option value=ID>N - N - name</option>."""
    await _load_cases()
    if n not in _case_ids:
        raise BadRequest(f"ICJ lists no case number {n}; get_decision with a case number or "
                         "list-of-all-cases on icj-cij.org shows them.")
    return _case_ids[n]

_PDF_NOTE = ("Full text: the ICJ publishes this only as PDF, and icj-cij.org serves its PDFs "
             "behind a Cloudflare bot challenge, so this tool cannot read them. Open the PDF "
             "link in a browser.")


def _case_url(n: str) -> str:
    return f"{BASE}/case/{int(n)}"


def _t(el) -> str:
    return _http.clean((el.text_content() if el is not None else "").replace("&nbsp;", " "))


def _first(el, xp):
    r = el.xpath(xp)
    return r[0] if r else None


def _files(el) -> dict[str, str]:
    """{language label: absolute PDF url} from a .file-buttons block directly under el."""
    out = {}
    for a in el.xpath("./div[contains(@class,'file-buttons')]/a[@href]"):
        out[_t(a) or "PDF"] = a.get("href") if a.get("href").startswith("http") else BASE + a.get("href")
    return out


def _doc_from(urls: list[str]):
    """(id, kind, date) from the first case-related PDF url, or None."""
    for u in urls:
        m = _FILE.search(u or "")
        if m:
            did = m[1].lower()
            d = _DOC_ID.match(did)
            date = f"{d[2][:4]}-{d[2][4:6]}-{d[2][6:]}"
            return did, d[3], date
    return None


def _norm_doc_id(s: str) -> str:
    """'178-20220722-JUD-01-00-EN.pdf', '178-20220722-jud-01-00' -> '178-20220722-jud-01-00'."""
    s = s.strip().rsplit("/", 1)[-1]
    s = re.sub(r"(?i)\.pdf$", "", s).lower()
    s = re.sub(r"-(en|fr|bi|bic|ar|es|ru|zh)$", "", s)
    m = _DOC_ID.match(s)
    return f"{int(m[1]):03d}-{m[2]}-{m[3]}-{m[4]}-{m[5]}" if m else ""


def _parse_case(n: str, page: str) -> dict:
    root = lhtml.fromstring(page)
    h1 = _first(root, "//main//h1[contains(@class,'title')]")
    title = _t(h1)
    if not title:
        raise NotFound(f"ICJ has no case {n}. Case numbers are the ICJ's own (1-2xx), "
                       "e.g. 178 for The Gambia v. Myanmar; see https://www.icj-cij.org/list-of-all-cases.")
    docs: list[dict] = []
    section = ""
    for node in root.xpath("//main//div[contains(@class,'cases-documents')]/*"):
        cls = node.get("class") or ""
        if node.tag == "h4" and "document-type" in cls:
            section = _t(node)
            continue
        if "cases-document" not in cls:
            continue
        head = _first(node, "./div[contains(@class,'title-wrapper')]/*[contains(@class,'title')]")
        files = _files(node)
        info = _doc_from(list(files.values()) + ([head.get("href")] if head is not None and head.get("href") else []))
        base = {
            "title": _t(head),
            "variant": _t(_first(node, "./div[contains(@class,'title-wrapper')]/small")),
            "description": _t(_first(node, "./h6[contains(@class,'other-title')]")),
            "procedure": re.sub(r"^Procedure\(s\):\s*", "", _t(_first(node, "./h6[contains(@class,'procedure')]"))),
            "section": section,
        }
        parent = None
        if info:
            parent = {**base, "id": info[0], "kind": info[1], "date": info[2], "files": files, "parent": ""}
            docs.append(parent)
        for sub in node.xpath("./div[contains(@class,'subdocuments')]/div[contains(@class,'subdocument')]"):
            sfiles = _files(sub)
            a = _first(sub, "./a[@href]")
            sinfo = _doc_from(list(sfiles.values()) + ([a.get("href")] if a is not None else []))
            if not sinfo:
                continue
            docs.append({"id": sinfo[0], "kind": sinfo[1], "date": sinfo[2], "files": sfiles,
                         "title": _t(_first(sub, "./a/h6")) or _t(a), "variant": "",
                         "description": "", "procedure": "",
                         "section": section, "parent": parent["id"] if parent else "",
                         "group": "" if parent else base["title"]})
    seen, uniq = set(), []
    for d in docs:
        if d["id"] not in seen:
            seen.add(d["id"])
            uniq.append(d)
    return {"n": str(int(n)), "title": title, "docs": uniq}


async def _case(n: str) -> dict:
    n = str(int(n))
    if n in _case_cache:
        return _case_cache[n]
    r = await _http.get(_case_url(n))
    if r.status_code in (404, 500):   # the site answers 500 for an unknown case number
        raise NotFound(f"ICJ has no case {n} (HTTP {r.status_code}); see "
                       "https://www.icj-cij.org/list-of-all-cases for case numbers.")
    if r.status_code != 200 or "cf-mitigated" in r.headers:
        raise SourceError(_http.error("ICJ", f"case {n} failed", r.status_code), r.status_code)
    return _http.lru_put(_case_cache, n, _parse_case(n, r.text), 32)


def _section(d: dict) -> str:
    sec = d["section"]
    if not sec or sec.lower().startswith("latest"):
        return _KINDS.get(d["kind"], "Other documents")
    return sec


def _links(files: dict[str, str]) -> str:
    return "; ".join(f"{lang}: {u}" for lang, u in files.items())


def _pdf(d: dict) -> str:
    f = d["files"]
    return f.get("English") or next(iter(f.values()), "")


# --------------------------------------------------------------------------- #
_LAWS = {
    "statute": ("Statute of the International Court of Justice", f"{BASE}/statute",
                "statute charter united nations international court justice 1945"),
    "rules": ("Rules of Court (1978, as amended)", f"{BASE}/rules",
              "rules of court 1978 procedure practice"),
}
_ARTICLE = re.compile(r"(?i)^article\s+(\d+(?:\s*(?:bis|ter))?)\.?$")
_law_cache: dict = {}


def _law_id(id: str) -> str:
    low = (id or "").lower()
    if "rules" in low or "règlement" in low:
        return "rules"
    if "statute" in low or "statut" in low or "/statute" in low:
        return "statute"
    raise NotFound(f"ICJ legislation ids are 'statute' (Statute of the Court) and 'rules' (Rules of Court); got {id!r}.")


async def _law(lid: str) -> dict:
    if lid in _law_cache:
        return _law_cache[lid]
    title, url, _ = _LAWS[lid]
    r = await _http.get(url)
    if r.status_code != 200 or "cf-mitigated" in r.headers:
        raise SourceError(_http.error("ICJ", f"{title} page failed", r.status_code), r.status_code)
    root = lhtml.fromstring(r.text)
    body = root.xpath('//main//div[contains(@class,"manila")]')
    if not body:
        raise SourceError(f"ICJ {title} page has no recognisable text container (layout changed?).")
    arts: list[dict] = []
    cur = None
    for el in body[0]:
        txt = re.sub(r"\s+", " ", el.text_content()).strip()
        if el.tag == "h1" or not txt or set(txt) <= {"_"}:
            continue
        m = _ARTICLE.match(txt)
        if m:
            label = "Article " + re.sub(r"\s+", " ", m[1].lower())
            cur = {"label": label, "parts": []}
            arts.append(cur)
        elif cur is not None:
            # keep the source's (a), (b)... labels: markdown would renumber them 1, 2...
            for ol in el.xpath('descendant-or-self::ol[@type="a"]'):
                ol.tag = "ul"
                for i, li in enumerate(ol.xpath("./li")):
                    li.text = f"({chr(97 + i)}) " + (li.text or "")
            md = _http.html_to_md(lhtml.tostring(el, encoding="unicode")) or txt
            cur["parts"].append(md)
    for a in arts:
        a["text"] = "\n\n".join(a["parts"])
    if not arts:
        raise SourceError(f"ICJ {title} page yielded no articles (layout changed?).")
    return _http.lru_put(_law_cache, lid, {"id": lid, "title": title, "url": url, "arts": arts}, 4)


def _art_key(s: str) -> str:
    m = re.search(r"(\d+)\s*(bis|ter)?", (s or "").lower())
    return f"Article {m[1]}" + (f" {m[2]}" if m and m[2] else "") if m else ""


class ICJ(Jurisdiction):
    code = "icj"
    name = "International Court of Justice (ICJ)"
    languages = ("en", "fr")
    aliases = ("international court of justice", "cij", "cour internationale de justice", "world court")
    sources = (
        Source(
            name="International Court of Justice website (www.icj-cij.org): case pages and document search",
            url="https://www.icj-cij.org/list-of-all-cases",
            covers=("caselaw", "legislation"),
            licence=("© International Court of Justice; site disclaimer: 'may not be reproduced or "
                     "used for commercial purposes'. No other licence stated."),
            commercial_use=False,
            ai_use=None,   # robots.txt is the stock Drupal file (no AI/TDM lines); no AI clause in the disclaimer
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~35 requests (2026-11)",
            terms_url="https://www.icj-cij.org/disclaimer",
            warning=("ICJ site terms: its information may not be reproduced or used for commercial "
                     "purposes (the Statute and Rules texts are read from its HTML pages). Decision texts are PDF-only and blocked by a bot challenge here: "
                     "you get metadata and links, not the text."),
        ),
    )
    caselaw_filters = {
        "type": ("document type: decisions (default: judgments, advisory opinions, orders), "
                 "decisions_with_opinions, judgments, advisory_opinions, orders, opinions, summaries, "
                 "press_releases, applications, written, oral, other, correspondence, all"),
        "proceedings": ("incidental proceedings: provisional_measures, preliminary_objections, "
                        "counter_claims, intervention, discontinuance, jurisdiction_admissibility"),
        "case": "ICJ case number to restrict to one case, e.g. 178 (Gambia v. Myanmar), 192 (South Africa v. Israel)",
        "date_from": "document dated on or after YYYY-MM-DD",
        "date_to": "document dated on or before YYYY-MM-DD",
    }
    min_interval = {HOST: 1.0}
    notes = ("ICJ judgments, advisory opinions and orders: search the Court's document index and "
             "open case records (case number, e.g. 178) or a document's details; also the Statute and the Rules of Court (ids 'statute', 'rules'). Texts are PDF-only "
             "behind a bot challenge, so no full text: metadata and PDF links. Non-commercial use only.")
    gaps = (
        "Full text of judgments, advisory opinions and orders: bot check / blocks our client (Cloudflare on every PDF); metadata and links only",
        "Pleadings, written and oral proceedings texts: bot check / blocks our client (same Cloudflare PDF block)",
        "Legislation: only the Statute of the Court and the Rules of Court (1978, as amended) from the Court's own pages, nothing else (Practice Directions are not included)",
        "Permanent Court of International Justice (1922-1946) records: not researched yet",
    )
    samples = {
        "caselaw_query": "genocide",
        "decision_id": "178",   # The Gambia v. Myanmar
        "legislation_query": "statute", "law_id": "statute", "provision": "Article 38",
    }

    # ------------------------------------------------------------------ #
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        q = (query or "").strip().lower()
        words = [w for w in re.findall(r"[a-zà-ÿ]{3,}", q) if w not in {"the", "and", "for", "icj", "article"}]
        named = {lid for lid in _LAWS if any(w in (lid, "statut", "règlement") for w in words)}
        topic = [w for w in words if w not in {"statute", "statut", "rules", "règlement", "court", "international",
                                               "justice", "icj"}]
        hits = []
        for lid, (title, url, _) in _LAWS.items():
            if named and lid not in named:
                continue
            snippet = ""
            if topic:
                found = [a["label"] for a in (await _law(lid))["arts"]
                         if all(w in a["text"].lower() for w in topic)]
                if not found and not named:
                    continue
                snippet = ("Articles containing all your words: " + "; ".join(found[:8])) if found else ""
            hits.append(LawHit(id=lid, title=title, type="Statute" if lid == "statute" else "Rules",
                               status="in force", url=url, snippet=snippet))
        if not hits:
            hits = [LawHit(id=lid, title=t, status="in force", url=u) for lid, (t, u, _) in _LAWS.items()]
            return Results(items=hits, total=len(hits), query_ignored=True,
                           note="Only two texts are held for the ICJ: its Statute and its Rules of Court; nothing matched your words.")
        return Results(items=hits[(page - 1) * limit:page * limit], total=len(hits))

    async def get_legislation_toc(self, id):
        law = await _law(_law_id(id))
        return Toc(id=law["id"], title=law["title"], url=law["url"],
                   entries=[TocEntry(title=a["label"], provision=a["label"]) for a in law["arts"]])

    async def get_legislation_provision(self, id, provision):
        law = await _law(_law_id(id))
        key = _art_key(provision)
        if not key:
            raise BadRequest("Give an article, e.g. 'Article 38' or '38'.")
        a = next((a for a in law["arts"] if a["label"].lower() == key.lower()), None)
        if a is None:
            raise NotFound(f"{law['title']} has no {key}. See get_legislation_toc for the articles.")
        return Provision(law_id=law["id"], law_title=law["title"], provision=a["label"],
                         text=f"**{a['label']}**\n\n{a['text']}", url=law["url"], as_of=_http.today())

    async def get_legislation_text(self, id):
        law = await _law(_law_id(id))
        text = "\n\n".join(f"**{a['label']}**\n\n{a['text']}" for a in law["arts"])
        return LawText(id=law["id"], title=law["title"], text=text, url=law["url"], as_of=_http.today())

    # ------------------------------------------------------------------ #
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        f = {k: str(v).strip() for k, v in (filters or {}).items() if str(v).strip()}
        typ = f.get("type", "decisions").lower()
        if typ not in _TYPES:
            raise BadRequest("type must be one of: " + ", ".join(_TYPES) + ".")
        proc = f.get("proceedings", "").lower()
        if proc and proc not in _PROCEEDINGS:
            raise BadRequest("proceedings must be one of: " + ", ".join(_PROCEEDINGS) + ".")
        case = f.get("case", "")
        if case and not case.isdigit():
            raise BadRequest("case must be an ICJ case number, e.g. 178.")
        for key in ("date_from", "date_to"):
            if key in f and not _DATE.match(f[key]):
                raise BadRequest(f"{key} must be YYYY-MM-DD.")

        limit = max(1, min(int(limit), 50))
        page = max(1, int(page))
        per = next(p for p in (10, 25, 50, 100) if p >= limit)
        start = (page - 1) * limit
        params = {
            "search_api_fulltext": (query or "").strip(),
            "field_document_group_type": _TYPES[typ],
            "field_doc_incidental_proceedings": _PROCEEDINGS.get(proc, "All"),
            "field_date_of_the_document[min]": f.get("date_from", ""),
            "field_date_of_the_document[max]": f.get("date_to", ""),
            "items_per_page": str(per),
            "sort_order": "DESC",
        }
        cases = [case] if case else await _match_cases(query or "")
        matched = bool(cases) and not case
        if cases:
            params["case_selection"] = "2"
            params["field_doc_case_code_1[]"] = [await _case_option(str(int(c))) for c in cases]
        src_page, skip = divmod(start, per)
        rows, total = await self._search_page({**params, "page": str(src_page)})
        if matched and not total:                         # name guess found nothing: plain search
            matched, cases = False, []
            params.pop("case_selection"); params.pop("field_doc_case_code_1[]")
            rows, total = await self._search_page({**params, "page": str(src_page)})
        ranked = how_order = False
        q = _tokens(query or "")
        if q and not cases and total and total <= 100:    # small enough to rank here
            if total > per:
                rows, _ = await self._search_page({**params, "items_per_page": "100", "page": "0"})
            else:
                rows = rows[:]
            rows.sort(key=lambda h: -len(q & _tokens(h.title.split(": ", 1)[0])))   # stable: newest first within a tie
            rows = rows[start:] if total > per else rows
            skip, ranked = (0 if total > per else skip), True
        elif cases and total and total <= 100:            # one case: its judgments and opinions before its orders
            if total > per:
                rows, _ = await self._search_page({**params, "items_per_page": "100", "page": "0"})
            rank = {"jud": 0, "adv": 0, "ord": 1}
            rows = sorted(rows, key=lambda h: rank.get(h.id.split("-")[2], 2))   # stable: newest first within a kind
            rows = rows[start:] if total > per else rows
            skip = 0 if total > per else skip
            how_order = True
        elif len(rows) == per and skip + limit > per:    # the slice runs into the next source page
            more, _ = await self._search_page({**params, "page": str(src_page + 1)})
            rows += more
        items = rows[skip:skip + limit]
        how = ("restricted to case(s) " + ", ".join(cases) + " (" + "; ".join(_case_names[c] for c in cases)
               + ") because the query names them; pass filters.case to choose another case; "
               + ("judgments and advisory opinions first, then orders, newest first; " if how_order else "")
               if matched else
               ("restricted to the case; judgments and advisory opinions first, then orders, newest first; " if how_order else "newest first; ") if cases else
               "hits whose case name contains the query words first, then newest first; " if ranked else
               "newest first; ")
        return Results(items=items, total=total,
                       note=("ICJ document search, " + how + "the site cannot sort by relevance and its "
                             "full-text matches loosely: to see one case, use filters.case with its "
                             "case number, e.g. 178 Gambia v. Myanmar, 192 South Africa v. Israel, "
                             "70 Nicaragua v. United States; "
                             "one hit per document (id opens its "
                             "details; its case number opens the whole case record). Texts are PDF-only "
                             "and not readable here."))

    async def _search_page(self, params: dict):
        r = await _http.get(f"{BASE}/advanced-search?{urlencode(params, doseq=True)}")
        if r.status_code != 200 or "cf-mitigated" in r.headers:
            raise SourceError(_http.error("ICJ", "search failed", r.status_code), r.status_code)
        root = lhtml.fromstring(r.text)
        head = _t(_first(root, "//div[contains(@class,'view-document-search')]/div[contains(@class,'view-header')]"))
        m = re.search(r"([\d,]+)\s+results?", head)
        total = int(m[1].replace(",", "")) if m else (0 if not root.xpath("//div[contains(@class,'views-row')]") else None)
        out = []
        for row in root.xpath("//div[contains(@class,'view-document-search')]//div[contains(@class,'views-row')]"):
            a = _first(row, "./h4/a[@href]")
            if a is None:
                continue
            href = a.get("href")
            info = _doc_from([href])
            case_a = _first(row, ".//p/a[contains(@href,'/case/')]")
            cm = re.search(r"/case/(\d+)", case_a.get("href")) if case_a is not None else None
            meta = _t(_first(row, "./p[b[starts-with(normalize-space(.),'Type')]]"))
            tm = re.search(r"Type:\s*(.*?)(?:\s*\|\s*Date:\s*(\d{4}-\d{2}-\d{2}))?$", meta)
            case_name = _t(case_a)
            title = _t(a)
            if not info:
                continue
            out.append(DecisionHit(
                id=info[0],
                title=f"{case_name}: {title}" if case_name else title,
                court=COURT,
                date=(tm[2] if tm and tm[2] else info[2]),
                case_number=cm[1] if cm else str(int(info[0].split("-")[0])),
                snippet=f"{tm[1] if tm else ''}; case {cm[1] if cm else '?'}".strip("; "),
                url=href if href.startswith("http") else BASE + href,
            ))
        return out, total

    # ------------------------------------------------------------------ #
    async def get_decision(self, id):
        ident = (id or "").strip()
        m = re.fullmatch(r"(?i)(?:ICJ\s+)?(?:case\s*(?:no\.?)?\s*)?(\d{1,3})", ident)
        if m:
            return self._case_record(await _case(m[1]))
        did = _norm_doc_id(ident)
        if not did:
            raise BadRequest("Give an ICJ case number (e.g. 178) or a document id as search_caselaw "
                             "and get_decision list it (e.g. 178-20220722-jud-01-00).")
        rec = await _case(did.split("-")[0])
        doc = next((d for d in rec["docs"] if d["id"] == did), None)
        if doc is None:
            raise NotFound(f"ICJ case {rec['n']} lists no document {did}; get_decision('{rec['n']}') "
                           "lists its documents.")
        return self._document(rec, doc)

    def _case_record(self, rec: dict) -> Decision:
        groups: dict[str, list[dict]] = {}
        for d in rec["docs"]:
            groups.setdefault(_section(d), []).append(d)
        parts = [f"# {rec['title']}", "", f"ICJ case {rec['n']}. {_PDF_NOTE}",
                 "Open a document's details with get_decision and the id in brackets."]
        for sec in sorted(groups, key=lambda s: _ORDER.index(s) if s in _ORDER else len(_ORDER)):
            parts += ["", f"## {sec}"]
            for d in groups[sec]:
                bits = [d["title"] or d.get("group") or d["id"]]
                if d["description"] and d["description"] != d["title"]:
                    bits.append(d["description"])
                if d["procedure"]:
                    bits.append(f"procedure: {d['procedure']}")
                indent = "  " if d["parent"] else ""
                parts.append(f"{indent}- {d['date']} {' - '.join(bits)} [{d['id']}] {_pdf(d)}")
        decisions = [d for d in rec["docs"] if d["kind"] in _DECISION_KINDS and not d["parent"]]
        latest = max((d["date"] for d in decisions), default="")
        return Decision(
            id=rec["n"],
            title=rec["title"],
            text="\n".join(parts).strip(),
            url=_case_url(rec["n"]),
            court=COURT,
            date=latest,
            case_number=rec["n"],
            metadata={"Documents listed": str(len(rec["docs"])),
                      "Judgments, advisory opinions and orders": str(len(decisions)),
                      "Full text": "PDF only, behind a Cloudflare bot challenge (not fetched)"},
        )

    def _document(self, rec: dict, doc: dict) -> Decision:
        title = doc["title"] or doc.get("group") or doc["id"]
        parts = [f"# {rec['title']}", f"## {title}", ""]
        for label, val in (("Date", doc["date"]), ("Type", _section(doc)),
                           ("Description", doc["description"]), ("Procedure", doc["procedure"]),
                           ("Version", doc["variant"]), ("Part of", doc.get("group", ""))):
            if val:
                parts.append(f"- **{label}:** {val}")
        if doc["parent"]:
            p = next((d for d in rec["docs"] if d["id"] == doc["parent"]), None)
            parts.append(f"- **Appended to:** {(p['title'] if p else '')} [{doc['parent']}]".replace(" []", ""))
        parts.append(f"- **Case:** {rec['title']} (ICJ case {rec['n']}) {_case_url(rec['n'])}")
        parts += ["", "### PDF files"] + [f"- {lang}: {u}" for lang, u in doc["files"].items()]
        kids = [d for d in rec["docs"] if d["parent"] == doc["id"]]
        if kids:
            parts += ["", "### Appended opinions and declarations"]
            parts += [f"- {k['title']} [{k['id']}] {_pdf(k)}" for k in kids]
        same_day = [d for d in rec["docs"] if d["date"] == doc["date"] and d["id"] != doc["id"]
                    and d["kind"] in ("sum", "pre")]
        if same_day:
            parts += ["", "### Summary and press release of the same date"]
            parts += [f"- {d['title']}: {d['description']} [{d['id']}] {_pdf(d)}" for d in same_day]
        parts += ["", _PDF_NOTE]
        return Decision(
            id=doc["id"],
            title=f"{rec['title']}: {title}",
            text="\n".join(parts).strip(),
            url=_pdf(doc) or _case_url(rec["n"]),
            court=COURT,
            date=doc["date"],
            case_number=rec["n"],
            summary=doc["description"],
            metadata={k: v for k, v in {"Type": _section(doc), "Procedure": doc["procedure"],
                                        "Case record": _case_url(rec["n"]),
                                        "Files": _links(doc["files"])}.items() if v},
        )
