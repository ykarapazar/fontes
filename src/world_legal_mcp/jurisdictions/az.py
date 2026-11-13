"""Azerbaijan: legislation and higher-court decisions from e-qanun.az, the Ministry of
Justice's Unified Electronic Database of Legal Acts (Hüquqi aktların vahid elektron bazası).

Gotchas this code encodes (verified 2026-11-06 from a UK IP):
  * e-qanun.az is a Next.js shell; the data comes from the JSON API at api.e-qanun.az
    (no key). Neither host has a robots.txt (both 404). No terms-of-use page exists; the
    footer only says "© | e-qanun.az | Bütün Haqqlar Qorunur" (All Rights Reserved).
  * Every act, including court decisions, is a "framework" with a numeric id
    (Civil Code = 46944, Constitution = 897). GET /framework/{id} gives the requisites and
    an htmlUrl (e-qanun.az/frameworks/{id//1000}/f_{id}.html): the current consolidated
    text as Word-made HTML. Its charset varies per file (windows-1251 or windows-1254),
    so we decode by the file's own <meta charset>, as the site's viewer does.
  * The HTML files answer 403 unless the request carries a Referer from e-qanun.az
    (hotlink protection; the site's own viewer sends it). We send the act's public viewer
    page as Referer; the User-Agent stays the project's own.
  * An unknown framework id answers HTTP 500 (not 404).
  * Search: GET /getDetailSearch. The API returns 500 unless `array=` is present (empty =
    all types). `name` with title=true searches titles, text=true searches the text.
    Omitting statusId returns every status.
  * Case law here is only what the database publishes as acts: Constitutional Court
    decisions (type 73, ~470) and Supreme Court Plenum decisions (type 87, ~114, i.e.
    guidance resolutions, not individual cases). Ordinary court judgments are not in it;
    supremecourt.gov.az and courts.gov.az did not answer from the UK (timed out
    2026-11-06).
"""
from __future__ import annotations

import re
from urllib.parse import urlencode

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

API = "https://api.e-qanun.az"
SITE = "https://e-qanun.az"

_COURTS = {"constitutional": "73", "supreme": "87"}
_TYPES = {"constitution": "25", "constitutional_law": "28", "law": "29", "code": "107",
          "presidential_decree": "31", "presidential_order": "84", "cabinet_decision": "32",
          "cabinet_order": "85", "ministry_act": "33", "parliament_decision": "83",
          "treaty": "120", "constitutional_court": "73", "supreme_court": "87"}
_STATUS = {"in_force": "1", "repealed": "2"}

# "Maddə 1. title", "Maddə 2-1. title"
_ART = re.compile(r"^Maddə\s+(\d+(?:-\d+)*)\s*\.")
# Structural headings in codes/laws: "ÜMUMİ HİSSƏ", "Birinci bölmə", "1-ci fəsil.",
# "Fəsil 1", "§ 1. ...". Kept short so body sentences never match.
_HEAD = re.compile(r"^(?:[A-ZÇƏĞİÖŞÜ ]+ HİSSƏ|\w+ (?:bölmə|BÖLMƏ)|\d+(?:-\d+)?-(?:ci|cı|cu|cü) "
                   r"(?:fəsil|FƏSİL)\.?|[IVXLC]+ (?:fəsil|FƏSİL)\.?|(?:Fəsil|FƏSİL) [\dIVXLC]+\.?"
                   r"|§\s*\d+.*|(?i:ke[çÇ][iİ]d(?: və yekun)? m[üÜ]dd[əƏ]alar[ıI]))$")
# After the last article: "Məcəlləyə əlavə və dəyişikliklər etmiş qanunlar:" (amendment list).
_TAIL = re.compile(r"^.{0,60}(?:əlavə|dəyişiklik|ƏLAVƏ|DƏYİŞİKLİK).{0,60}"
                   r"(?:qanunlar|aktlar|siyahısı|SİYAHISI)\s*:?$")

_docs: dict = {}


def _court(type_name) -> str:
    t = _http.clean(type_name)
    if t.upper().startswith("KONSTİTUSİYA MƏHKƏMƏSİ"):
        return "Konstitusiya Məhkəməsi"
    return "Ali Məhkəmə (Plenum)" if "Ali Məhkəmə" in t else t


def _check_id(raw) -> str:
    s = str(raw or "").strip()
    m = re.fullmatch(r"(?:https?://(?:www\.)?e-qanun\.az/framework/)?(\d+)/?", s)
    if not m:
        raise BadRequest(f"Bad e-qanun id {raw!r}: use the numeric framework id, e.g. "
                         "'46944' (Civil Code) or an e-qanun.az/framework/<id> URL.")
    return m[1]


def _url(fid: str) -> str:
    return f"{SITE}/framework/{fid}"


async def _api(path: str, params: dict | None = None) -> dict:
    url = f"{API}/{path}" + (f"?{urlencode(params)}" if params else "")
    r = await _http.get(url, headers={"Accept-Language": "AZ"})
    if r.status_code != 200:
        raise SourceError(_http.error("e-qanun", "API request failed", r.status_code),
                          r.status_code)
    try:
        return r.json()
    except ValueError:
        raise SourceError("e-qanun: API answer is not JSON (blocked or changed?)", 200) from None


async def _search(query: str, types: str, *, limit: int, page: int,
                  status: str = "", fulltext: bool = False) -> tuple[list[dict], int | None]:
    params = {"start": (page - 1) * limit, "length": limit, "orderColumn": 8,
              "orderDirection": "desc", "codeType": 1, "dateType": 1, "secondType": 2,
              "specialDate": "false", "array": types}
    if query.strip():
        params["name"] = query.strip()
        params["text" if fulltext else "title"] = "true"
    if status:
        params["statusId"] = status
    js = await _api("getDetailSearch", params)
    if not isinstance(js, dict) or "data" not in js:
        raise SourceError("e-qanun: unexpected search payload", 200)
    return js.get("data") or [], js.get("totalCount")


async def _doc(fid: str) -> dict:
    """Requisites + parsed paragraphs of one act (cached in-process, a few docs)."""
    if fid in _docs:
        return _docs[fid]
    r = await _http.get(f"{API}/framework/{fid}", headers={"Accept-Language": "AZ"})
    if r.status_code == 500:
        raise NotFound(f"e-qanun has no act with id {fid} (the API answers HTTP 500 for "
                       "unknown ids).")
    if r.status_code != 200:
        raise SourceError(_http.error("e-qanun", "API request failed", r.status_code),
                          r.status_code)
    data = (r.json() or {}).get("data") or {}
    req = data.get("requisite") or {}
    html_url = data.get("htmlUrl") or ""
    if not req or not html_url:
        raise NotFound(f"e-qanun act {fid} has no published text.")
    h = await _http.get(html_url, headers={"Referer": _url(fid)})
    if h.status_code != 200:
        raise SourceError(_http.error("e-qanun", "text file request failed", h.status_code),
                          h.status_code)
    raw = h.content
    m = re.search(rb"charset=[\"']?([\w-]+)", raw[:3000], re.I)
    try:
        html = raw.decode(m[1].decode() if m else "utf-8", errors="replace")
    except LookupError:
        html = raw.decode("utf-8", errors="replace")
    # Word's <![if !supportFootnotes]> markers are not comments; drop them. The amendment
    # endnotes ("[7] 24 iyun 2005-ci il 949-IIQD nömrəli Qanun...") sit in a trailing
    # endnote-list div: kept in the full text, never inside an article.
    html = re.sub(r"<!\[(?:if [^\]]*|endif)\]>", "", html)
    cut = re.search(r"<div[^>]*mso-element:\s*(?:endnote|footnote)-list", html)
    paras = [re.sub(r"\*{4}", "", p) for p in _http.html_paragraphs(html[:cut.start()] if cut else html)]
    notes = [re.sub(r"\*{4}", "", p) for p in _http.html_paragraphs(html[cut.start():])] if cut else []
    title = _http.clean(req.get("title")) or f"e-qanun {fid}"
    doc = {"id": fid, "title": title, "url": _url(fid), "req": req,
           "text": "\n\n".join(paras + (["---"] + notes if notes else []))}
    doc["paras"] = paras
    doc["entries"], doc["spans"] = _structure(paras)
    return _http.lru_put(_docs, fid, doc, 3)


def _plain(p: str) -> str:
    return _http.clean(re.sub(r"^#+\s*", "", p.replace("*", "").replace("\\", "")))


def _structure(paras: list[str]) -> tuple[list[TocEntry], dict[str, tuple[int, int]]]:
    entries: list[TocEntry] = []
    spans: dict[str, tuple[int, int]] = {}
    open_label, open_start = None, 0
    i = 0
    while i < len(paras):
        p = _plain(paras[i])
        art = _ART.match(p)
        head = None if art else _HEAD.match(re.sub(r"\[\d+\]$", "", p)) if len(p) < 100 else None
        if art:
            if open_label:
                spans[open_label] = (open_start, i)
            label, n = f"Maddə {art[1]}", 2
            while label in spans:
                label, n = f"Maddə {art[1]} ({n})", n + 1
            open_label, open_start = label, i
            entries.append(TocEntry(title=p, level=1, provision=label))
        elif open_label and _TAIL.match(p):
            spans[open_label] = (open_start, i)
            open_label = None
        elif head:
            if open_label:
                spans[open_label] = (open_start, i)
            open_label = None
            title = p
            nxt = _plain(paras[i + 1]) if i + 1 < len(paras) else ""
            if nxt and len(nxt) < 200 and not _ART.match(nxt) and not _HEAD.match(nxt):
                title, i = f"{p} {nxt}", i + 1
            entries.append(TocEntry(title=title, level=0))
        i += 1
    if open_label:
        spans[open_label] = (open_start, len(paras))
    return entries, spans


def _norm_provision(raw: str) -> str:
    """'Maddə 5', 'maddə 2-1', 'Article 5', 'art. 5', '5.' -> '5' / '2-1'."""
    s = _http.clean(raw).lower()
    s = re.sub(r"^(maddə|madde|mad\.|m\.|article|art\.?)\s*", "", s)
    m = re.fullmatch(r"(\d+(?:-\d+)*)\.?", s)
    if not m:
        raise BadRequest(f"Bad provision {raw!r}: use an article label such as 'Maddə 5', "
                         "'5' or '2-1' for an inserted article.")
    return m[1]


def _label(doc: dict, raw: str) -> str:
    if raw in doc["spans"]:
        return raw
    want = f"Maddə {_norm_provision(raw)}"
    if want in doc["spans"]:
        return want
    raise NotFound(f"{doc['title']} ({doc['id']}) has no article {raw!r}. "
                   "Use get_legislation_toc to see the article labels.")


class Azerbaijan(Jurisdiction):
    code = "az"
    name = "Azerbaijan"
    languages = ("az",)
    aliases = ("azerbaijan", "azərbaycan", "azerbaycan")
    sources = (
        Source(
            name="e-qanun.az, Unified Electronic Database of Legal Acts (Ministry of Justice)",
            url="https://e-qanun.az",
            covers=("legislation", "caselaw"),
            licence="unknown: no terms page; footer says 'Bütün Haqqlar Qorunur' (All Rights "
                    "Reserved). Official texts are excluded from copyright under the "
                    "Azerbaijani Copyright Law (art. 7; unverified)",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~80 requests (2026-11)",
            terms_url="",
            needs_permission=True,
            warning=("e-qanun.az serves its text files only with an e-qanun.az Referer header "
                     "(hotlink protection); this adapter sends one. Off until the operator "
                     "decides that is acceptable."),
        ),
    )
    caselaw_filters = {
        "court": "'constitutional' (Constitutional Court decisions) or 'supreme' (Supreme "
                 "Court Plenum decisions). Default: both",
        "fulltext": "'true' to search the text, not just titles (default: titles)",
    }
    legislation_filters = {
        "type": ", ".join(_TYPES) + ", or an e-qanun type id",
        "status": "'in_force' or 'repealed'. Default: all",
        "fulltext": "'true' to search the text, not just titles (default: titles)",
    }
    min_interval = {"api.e-qanun.az": 1.0, "e-qanun.az": 1.0}
    notes = ("Ministry of Justice database (Azerbaijani only): current consolidated texts. "
             "Case law = Constitutional Court and Supreme Court Plenum decisions only.")
    gaps = (
        ("Everything (e-qanun.az): text files need an e-qanun.az Referer (hotlink protection); off"
         " until the operator permits it"),
        ("Ordinary court judgments: not in e-qanun; supremecourt.gov.az and courts.gov.az time out"
         " from the UK (2026-11-06)"),
        ("Supreme Court individual cases: only Plenum guidance resolutions are published in the "
         "database"),
    )
    samples = {
        "caselaw_query": "Mülki Məcəllə",
        "decision_id": "59521",
        "legislation_query": "Mülki Məcəllə",
        "law_id": "46944",
        "provision": "Maddə 1",
    }

    @staticmethod
    def _fulltext(filters: dict) -> bool:
        v = str(filters.get("fulltext", "")).strip().lower()
        if v not in ("", "true", "false", "1", "0", "yes", "no"):
            raise BadRequest(f"Bad fulltext {v!r}: use 'true' or 'false'.")
        return v in ("true", "1", "yes")

    # ---------------------------------------------------------------- case law
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        court = str(filters.get("court", "")).strip().lower()
        if court and court not in _COURTS:
            raise BadRequest(f"Bad court {court!r}: use 'constitutional' or 'supreme'.")
        types = _COURTS[court] if court else ",".join(_COURTS.values())
        rows, total = await _search(query, types, limit=limit, page=page,
                                    fulltext=self._fulltext(filters))
        items = []
        for x in rows[:limit]:
            fid = str(x["id"])
            items.append(DecisionHit(id=fid, title=_http.clean(x.get("title")) or f"e-qanun {fid}",
                                     court=_court(x.get("typeName")),
                                     date=_http.iso_date(x.get("acceptDate")),
                                     case_number=_http.clean(x.get("citation")), url=_url(fid)))
        return Results(items=items, total=total,
                       note="Only Constitutional Court and Supreme Court Plenum decisions; "
                            "ordinary court judgments are not published here.")

    async def get_decision(self, id):
        doc = await _doc(_check_id(id))
        req = doc["req"]
        type_name = _http.clean(req.get("typeName"))
        meta = {k: v for k, v in (("Növ", type_name),
                                  ("Status", _http.clean(req.get("statusName"))),
                                  ("Qüvvəyə minmə tarixi", _http.iso_date(req.get("effectDate"))),
                                  ("Dövlət reyestri kodu", _http.clean(req.get("registerCode"))))
                if v}
        for f in req.get("fields") or []:
            meta[f"{_http.clean(f.get('name'))}: {_http.clean(f.get('fieldName'))}"] = \
                _http.clean(f.get("fieldValue"))
        return Decision(id=doc["id"], title=doc["title"], text=doc["text"],
                        url=doc["url"], court=_court(type_name), date=_http.iso_date(req.get("acceptDate")),
                        case_number=_http.clean(req.get("citation")), metadata=meta)

    # ------------------------------------------------------------- legislation
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        t = str(filters.get("type", "")).strip().lower()
        if t and t not in _TYPES and not t.isdigit():
            raise BadRequest(f"Bad type {t!r}: use one of {', '.join(_TYPES)}, or a numeric "
                             "e-qanun type id.")
        st = str(filters.get("status", "")).strip().lower()
        if st and st not in _STATUS:
            raise BadRequest(f"Bad status {st!r}: use 'in_force' or 'repealed'.")
        rows, total = await _search(query, _TYPES.get(t, t), limit=limit, page=page,
                                    status=_STATUS.get(st, ""), fulltext=self._fulltext(filters))
        items = [LawHit(id=str(x["id"]), title=_http.clean(x.get("title")) or f"e-qanun {x['id']}",
                        type=_http.clean(x.get("typeName")), number=_http.clean(x.get("citation")),
                        date=_http.iso_date(x.get("acceptDate")),
                        status=_http.clean(x.get("statusName")), url=_url(str(x["id"])))
                 for x in rows[:limit]]
        return Results(items=items, total=total)

    async def get_legislation_toc(self, id):
        doc = await _doc(_check_id(id))
        return Toc(id=doc["id"], title=doc["title"], url=doc["url"], entries=doc["entries"])

    async def get_legislation_provision(self, id, provision):
        doc = await _doc(_check_id(id))
        label = _label(doc, provision)
        a, b = doc["spans"][label]
        return Provision(law_id=doc["id"], law_title=doc["title"], provision=label,
                         text="\n\n".join(doc["paras"][a:b]), url=doc["url"],
                         as_of=await _as_of(doc))

    async def get_legislation_text(self, id):
        doc = await _doc(_check_id(id))
        req = doc["req"]
        meta = {k: v for k, v in (("Növ", _http.clean(req.get("typeName"))),
                                  ("Nömrə", _http.clean(req.get("citation"))),
                                  ("Qəbul tarixi", _http.iso_date(req.get("acceptDate"))),
                                  ("Status", _http.clean(req.get("statusName"))))
                if v}
        return LawText(id=doc["id"], title=doc["title"], text=doc["text"],
                       url=doc["url"], as_of=await _as_of(doc), metadata=meta)


async def _as_of(doc: dict) -> str:
    """Effect date of the newest consolidated version (getVersions lists newest first)."""
    if "as_of" not in doc:
        try:
            js = await _api("getVersions", {"id": doc["id"]})
            rows = js.get("data") if isinstance(js, dict) else None
            doc["as_of"] = _http.iso_date((rows or [{}])[0].get("effectDate")) if rows else ""
        except SourceError:
            doc["as_of"] = ""
    return doc["as_of"]
