"""African Court on Human and Peoples' Rights (AfCHPR, Arusha): contentious cases from
AJUDATA, the Court's own case database at ajudata.african-court.org.

AJUDATA replaced the older case pages at african-court.org/cpmt, which the Court says
are "no longer updated and will be permanently closed on 31 December 2026".
Neither service below is documented; both are what the AJUDATA pages themselves use.

  * Case list/search: GET /apidata/all?start=N&full_search=…[&defendantsKeys[]=id]
    [&cases_status[]=id][&from_date=YYYY-MM-DD&to_date=…] -> Laravel paginator JSON
    {total, per_page: 50, data: [...]}. 50 rows a page, fixed (length is ignored);
    `start` picks the page. Rows carry case_number ("004/2013"), slug ("0042013"),
    reception_date, end_date (date of the final decision), applicant, defendants,
    case_status, the Charter/treaty articles invoked (with violation finding) and
    thematics. full_search matches case number, parties, articles and themes, not
    decision text (checked: "Ouragan", a word only in the Konaté judgment, gives 0).
    from_date/to_date filter on judgment date.
  * Case page: GET /details-case/{slug} -> server-rendered HTML; table#case-details
    lists each decision (type + date badge) and separate/dissenting opinions, each
    with per-language PDF links /download-file/{file id}/{hash}.pdf (EN/FR/AR/PT/SP/SW).
    An unknown slug gives HTTP 200 with no <h1>.
  * Decisions are PDFs with a text layer (checked); text via _http.pdf_text, no OCR.

Ids: a case is its application number ("004/2013"); a document is
"<application number>#<file id>" ("004/2013#2034" = Konaté v. Burkina Faso, merits
judgment, English), which get_decision lists for every case.

  * Advisory opinions (checked 2026-11-10): GET /advisory-finalised and /advisory-pending
    -> server-rendered table#advisory (title, received, decided, status, link to
    /details-advisory/{slug}); the details page has table#advisory-details, same layout as
    a case page, with plain /download-file/ links. Request numbers ("001/2013") overlap
    application numbers, so advisory ids carry an "AO " prefix: "AO 001/2013",
    "AO 001/2013#1099".

Not covered: AfricanLII (robots.txt: Content-Signal ai-input=no, use=reference, and
Disallow: / for ClaudeBot / anthropic-ai).
"""
from __future__ import annotations

import datetime
import html as html_lib
import re
import time
import unicodedata
from urllib.parse import urlsplit

from lxml import html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, Results

HOST = "ajudata.african-court.org"
BASE = f"https://{HOST}/"
API = BASE + "apidata/all"
COURT = "African Court on Human and Peoples' Rights"
PAGE = 50                     # the source's fixed page size
_TTL = 6 * 3600

_CASENO = re.compile(r"^(\d{1,3})\s*/\s*(\d{4})$")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_STATUS = {"pending": "1", "finalised": "2", "finalized": "2", "struck out": "4",
           "transferred": "3", "transferred to commission": "3"}

_detail_cache: dict = {}      # case number -> parsed case page (small LRU)
_row_cache: dict = {}         # case number -> API row (small LRU)
_states: dict = {}            # {"t": monotonic, "map": {folded name: (id, name)}}
_advisory: dict = {}          # {"t": monotonic, "rows": [...]} advisory requests
_AO = re.compile(r"^(?:AO|advisory(?:\s+opinion)?|request)\s*(?:no\.?\s*)?(\d{1,3})\s*/\s*(\d{4})$", re.I)


# --------------------------------------------------------------------------- #
# Small parsers
# --------------------------------------------------------------------------- #
def _fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").replace("’", "'")
    return "".join(c for c in s if not unicodedata.combining(c)).lower().strip()


def _norm_caseno(s: str) -> str:
    """'Application No. 4/2013' -> '004/2013'; '' if it is not an application number."""
    s = re.sub(r"(?i)^(application|app\.?|requête|requete)\s*(no\.?|n[°o])?\s*", "", _http.clean(s))
    m = _CASENO.match(s)
    return f"{int(m[1]):03d}/{m[2]}" if m else ""


def _slug(caseno: str) -> str:
    return caseno.replace("/", "")


def _case_url(caseno: str) -> str:
    return BASE + "details-case/" + _slug(caseno)


def _dmy(s: str) -> str:
    """'05 Dec 2014' -> '2014-12-05'."""
    try:
        return datetime.datetime.strptime(_http.clean(s), "%d %b %Y").date().isoformat()
    except ValueError:
        return ""


def _parties(row: dict) -> str:
    app = _http.clean((row.get("applicant") or {}).get("en_designation"))
    resp = ", ".join(_http.clean(d.get("en_title")) for d in row.get("defendants") or [] if d.get("en_title"))
    resp = resp or _http.clean(row.get("en_respondent"))
    return f"{app} v. {resp}" if app and resp else app or resp


def _title(row: dict) -> str:
    p = _parties(row)
    return f"{p} (Application {row['case_number']})" if p else f"{COURT} Application {row['case_number']}"


def _articles(row: dict) -> list[str]:
    out = []
    for a in row.get("articles") or []:
        treaty = _http.clean(((a.get("traity") or {}).get("en_short_code")) or "")
        name = _http.clean(a.get("en_article_designation"))
        finding = _http.clean((a.get("pivot") or {}).get("violation_status"))
        label = f"{treaty} art. {a.get('article')}".strip()
        out.append(f"{label} ({name}): {finding}" if finding else f"{label} ({name})")
    return out


# --------------------------------------------------------------------------- #
# Source access
# --------------------------------------------------------------------------- #
async def _api(params: dict) -> dict:
    r = await _http.get(API, params=params)
    if r.status_code != 200:
        raise SourceError(_http.error("AfCHPR", "case search failed", r.status_code), r.status_code)
    try:
        d = r.json()
        rows, total = d["data"], int(d["total"])
    except (ValueError, KeyError, TypeError):
        raise SourceError("Error (AfCHPR): unexpected case-search payload.", r.status_code) from None
    for row in rows:
        if row.get("case_number"):
            _http.lru_put(_row_cache, row["case_number"], row, 128)
    return {"rows": rows, "total": total}


async def _state_id(name: str) -> str:
    """Respondent name -> AJUDATA defendant id, from the filter list on the home page
    (only States and bodies that have been sued are listed)."""
    if not _states or time.monotonic() - _states["t"] > _TTL:
        r = await _http.get(BASE)
        if r.status_code != 200:
            raise SourceError(_http.error("AfCHPR", "respondent list failed", r.status_code), r.status_code)
        root = lhtml.fromstring(r.text)
        m = {}
        for o in root.xpath("//select[@id='defendants']/option[@value]"):
            # the name sits in data-content as HTML ('<span …>Burkina Faso</span> <span …>(7)</span>'),
            # some entities double-encoded ('Cote d&#039;Ivoire')
            label = re.sub(r"<[^>]+>", " ", o.get("data-content") or o.text_content())
            label = re.sub(r"\(\d+\)\s*$", "", html_lib.unescape(html_lib.unescape(label)))
            if _http.clean(label):
                m[_fold(_http.clean(label))] = (o.get("value"), _http.clean(label))
        if not m:
            raise SourceError("Error (AfCHPR): respondent list not found on the home page.")
        _states.update(t=time.monotonic(), map=m)
    m, want = _states["map"], _fold(name)
    if want in m:
        return m[want][0]
    hits = [v[0] for k, v in m.items() if want in k]
    if len(hits) == 1:
        return hits[0]
    raise BadRequest(f"Unknown respondent '{name}'. Known: "
                     + ", ".join(sorted(v[1] for v in m.values())) + ".")


def _norm_ao(s: str) -> str:
    """'AO 1/2013', 'advisory opinion 001/2013' -> 'AO 001/2013'; '' otherwise."""
    m = _AO.match(_http.clean(s))
    return f"AO {int(m[1]):03d}/{m[2]}" if m else ""


def _parse_case(caseno: str, page: str, table: str = "case-details") -> dict:
    root = lhtml.fromstring(page)
    h1 = root.xpath("//h1")
    if not h1 or not _http.clean(h1[0].text_content()):
        if caseno.startswith("AO "):
            raise NotFound(f"The African Court has no advisory request {caseno[3:]}; search with "
                           "kind=advisory to list them.")
        raise NotFound(f"The African Court has no application {caseno}. "
                       "Application numbers look like 004/2013.")
    sub = root.xpath("//header/following-sibling::p[1]") or root.xpath("//h1/following-sibling::p[1]")
    parties = _http.clean(sub[0].text_content()).replace(" vs ", " v. ") if sub else ""
    rec = {"caseno": caseno, "parties": parties, "decisions": [], "docs": []}
    current, current_date = "", ""
    for tr in root.xpath(f"//table[@id='{table}']/tbody/tr"):
        tds = tr.xpath("./td")
        if len(tds) < 3:
            continue
        badge = tds[1].xpath(".//span[contains(@class,'badge')]")
        date = _dmy(badge[0].text_content()) if badge else ""
        for b in badge:
            b.drop_tree()
        label = _http.clean(tds[1].text_content())
        is_opinion = "ajudata-opinion-row" in (tds[1].get("class") or "")
        if not is_opinion:
            current, current_date = label, date
        else:
            date = date or current_date
        links = [(_http.clean(a.text_content()), a.get("href")) for a in tds[2].xpath(".//a[@href]")
                 if "/download-file/" in (a.get("href") or "")]
        entry = {"label": label, "date": date, "opinion": is_opinion,
                 "of": current if is_opinion else "", "files": []}
        for lang, href in links:
            m = re.search(r"/download-file/(\d+)/", href)
            if not m:
                continue
            entry["files"].append({"id": f"{caseno}#{m[1]}", "fid": m[1], "lang": lang, "url": href})
            rec["docs"].append({"id": f"{caseno}#{m[1]}", "fid": m[1], "lang": lang, "url": href,
                                "label": label, "date": date, "of": entry["of"]})
        rec["decisions"].append(entry)
    return rec


def _adv_url(ao: str) -> str:
    return BASE + "details-advisory/" + _slug(ao[3:])


async def _case(caseno: str) -> dict:
    if caseno in _detail_cache:
        return _detail_cache[caseno]
    ao = caseno.startswith("AO ")
    r = await _http.get(_adv_url(caseno) if ao else _case_url(caseno))
    if r.status_code != 200:
        raise SourceError(_http.error("AfCHPR", f"case {caseno} failed", r.status_code), r.status_code)
    rec = _parse_case(caseno, r.text, "advisory-details" if ao else "case-details")
    return _http.lru_put(_detail_cache, caseno, rec, 32)


async def _advisory_rows() -> list[dict]:
    if _advisory and time.monotonic() - _advisory["t"] < _TTL:
        return _advisory["rows"]
    rows, seen = [], set()
    for path in ("advisory-finalised", "advisory-pending"):
        r = await _http.get(BASE + path)
        if r.status_code != 200:
            raise SourceError(_http.error("AfCHPR", "advisory list failed", r.status_code), r.status_code)
        for tr in lhtml.fromstring(r.text).xpath("//table[@id='advisory']/tbody/tr[td]"):
            tds = tr.xpath("./td")
            link = tr.xpath(".//a[contains(@href,'/details-advisory/')]/@href")
            m = re.search(r"/details-advisory/(\d{3})(\d{4})$", link[0]) if link else None
            if len(tds) < 5 or not m:
                continue
            ao = f"AO {m[1]}/{m[2]}"
            if ao in seen:
                continue
            seen.add(ao)
            rows.append({"id": ao, "title": _http.clean(tds[1].text_content()),
                         "received": tds[2].get("data-order") or "", "decided": tds[3].get("data-order") or "",
                         "status": _http.clean(tds[4].text_content())})
    _advisory.update(t=time.monotonic(), rows=rows)
    return rows


async def _row(caseno: str) -> dict | None:
    if caseno not in _row_cache:
        for row in (await _api({"start": 0, "full_search": caseno}))["rows"]:
            if row.get("case_number") == caseno:
                break
    return _row_cache.get(caseno)


# --------------------------------------------------------------------------- #
class AfCHPR(Jurisdiction):
    code = "afchpr"
    name = "African Court on Human and Peoples' Rights"
    languages = ("en", "fr", "ar", "pt")
    aliases = ("african court", "african court on human and peoples' rights",
               "african court on human and peoples rights", "cour africaine",
               "cadhp", "ajudata")
    sources = (
        Source(
            name="AJUDATA, the African Court's case database (ajudata.african-court.org)",
            url="https://ajudata.african-court.org/",
            covers=("caselaw",),
            licence=("© African Court on Human and Peoples' Rights, \"All Rights Reserved\" "
                     "(site footer); no terms-of-use page and no clause on automated access"),
            commercial_use=None,
            ai_use=None,   # no robots.txt (404) on ajudata or www.african-court.org; no AI/TDM clause
            auth="none",
            rate_limit=("unknown; 1 s spacing, no 429 seen in ~25 requests (2026-11); "
                        "page size fixed at 50 by the source"),
            terms_url="https://www.african-court.org/afchpr/",
        ),
        # Pointers only (nothing is fetched from them): they let the legislation refusal name
        # the treaty and Rules of Court pages up front.
        Source(
            name="African Union treaty page: African Charter on Human and Peoples' Rights and the Court's Protocol",
            url="https://au.int/en/treaties/african-charter-human-and-peoples-rights",
            covers=("legislation",),
            licence="not researched; link only, nothing is fetched from it",
        ),
        Source(
            name="African Court website (Rules of Court)",
            url="https://www.african-court.org/",
            covers=("legislation",),
            licence="not researched; link only, nothing is fetched from it",
        ),
    )
    caselaw_filters = {
        "respondent": "respondent State or body, e.g. Tanzania, Burkina Faso, Cote d'Ivoire",
        "status": "pending, finalised, struck out or transferred",
        "date_from": "judgment date on or after YYYY-MM-DD",
        "date_to": "judgment date on or before YYYY-MM-DD",
        "kind": "'advisory' to search the advisory-opinion requests instead of contentious cases",
    }
    min_interval = {HOST: 1.0}
    notes = ("African Court on Human and Peoples' Rights, contentious cases from its AJUDATA "
             "database. Search covers application number, parties, rights invoked and themes "
             "(not decision text); get_decision on an application number lists its decisions, "
             "'<no>#<file id>' gives a judgment's text (from PDF). Advisory opinions: kind=advisory, "
             "ids 'AO 001/2013'.")
    gaps = (
        ("Full-text search: AJUDATA search matches number, parties, articles and themes only, not "
         "decision text"),
        "Pleadings, applications and hearing records: not researched yet",
        ("Legislation: the African Charter on Human and Peoples' Rights and the Court's Protocol "
         "are treaties, not searchable here; read them on the African Union treaty page "
         "https://au.int/en/treaties/african-charter-human-and-peoples-rights"),
        ("Legislation: the Court's Rules of Court (procedural rules) are not covered here; look "
         "for them on the Court's own website https://www.african-court.org/"),
    )
    samples = {
        "caselaw_query": "Tanzania",
        "decision_id": "004/2013#2034",   # Konaté v. Burkina Faso, judgment (merits), 5 Dec 2014, EN
    }

    # ------------------------------------------------------------------ #
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        f = {k: str(v).strip() for k, v in (filters or {}).items() if str(v).strip()}
        params: dict = {}
        if "status" in f:
            st = _STATUS.get(f["status"].lower())
            if not st:
                raise BadRequest("status must be pending, finalised, struck out or transferred.")
            params["cases_status[]"] = st
        for key, src in (("date_from", "from_date"), ("date_to", "to_date")):
            if key in f:
                if not _DATE.match(f[key]):
                    raise BadRequest(f"{key} must be YYYY-MM-DD.")
                params[src] = f[key]
        pend_dates = f.get("status", "").lower() == "pending" and ("date_from" in f or "date_to" in f)
        if pend_dates:       # the source dates by final decision, so it drops every pending case
            params.pop("from_date", None)
            params.pop("to_date", None)
        q = (query or "").strip()
        kind = f.get("kind", "").lower()
        if kind and kind not in ("advisory", "contentious"):
            raise BadRequest("kind must be 'advisory' or 'contentious'.")
        if kind == "advisory" or _norm_ao(q):
            return await self._search_advisory(q, f, limit, page)
        if "respondent" in f:
            params["defendantsKeys[]"] = await _state_id(f["respondent"])
        exact = _norm_caseno(q)
        if q:
            params["full_search"] = exact or q

        limit = max(1, min(int(limit), PAGE))
        page = max(1, int(page))
        first, last = (page - 1) * limit, page * limit       # absolute offsets wanted
        rows, total, start = [], None, first // PAGE * PAGE
        if pend_dates:       # filter on date received here, so read every page
            start, last = 0, float("inf")
        while start < last:
            res = await _api({**params, "start": start})
            total = res["total"]
            rows += res["rows"]
            if len(res["rows"]) < PAGE or start + PAGE >= total:
                break
            start += PAGE
        if pend_dates:
            rows = [r for r in rows
                    if (r.get("reception_date") or "") >= f.get("date_from", "")
                    and (r.get("reception_date") or "9999") <= f.get("date_to", "9999-99-99")]
            total = len(rows)
            rows = rows[first: first + limit]
        else:
            skip = first - first // PAGE * PAGE
            rows = rows[skip: skip + limit]
        if exact:
            rows = [r for r in rows if r.get("case_number") == exact] or rows

        items = []
        for r in rows:
            cno = r["case_number"]
            status = _http.clean((r.get("case_status") or {}).get("en_title"))
            bits = [f"Status: {status or '?'}", f"received {r.get('reception_date') or '?'}"]
            if r.get("end_date"):
                bits.append(f"decided {r['end_date']}")
            arts = _articles(r)
            if arts:
                bits.append("rights: " + "; ".join(arts[:4]) + ("; …" if len(arts) > 4 else ""))
            items.append(DecisionHit(
                id=cno, title=_title(r), court=COURT,
                date=r.get("end_date") or r.get("reception_date") or "",
                case_number=cno, snippet=". ".join(bits), url=_case_url(cno)))
        none = ("No match. Names of communities or nicknames of cases are not searched (e.g. the Ogiek "
                "case is Application 006/2012, listed as The African Commission on Human and Peoples' "
                "Rights v. Republic of Kenya); search the respondent State, the applicant or a theme "
                "such as 'Indigenous peoples'. " if not items and q and not exact else "")
        return Results(items=items, total=total,
                       note=(none + "Matches application number, parties, rights invoked and themes, not "
                             "decision text; newest application first; date = final decision date, "
                             "or date received while pending. The outcome (violation found or not) is only shown in "
                             "the rights text of each hit and cannot be filtered. "
                             "Advisory opinions: kind=advisory."))

    async def _search_advisory(self, q, f, limit, page):
        rows = await _advisory_rows()
        ao = _norm_ao(q)
        words = [] if ao else [_fold(w) for w in q.split() if w]
        hits = []
        for r in rows:
            if ao and r["id"] != ao:
                continue
            if words and not all(w in _fold(f"{r['title']} {r['id']}") for w in words):
                continue
            d = r["decided"] or r["received"]      # pending requests: date received
            if "date_from" in f and (not d or d < f["date_from"]):
                continue
            if "date_to" in f and (not d or d > f["date_to"]):
                continue
            hits.append(r)
        hits.sort(key=lambda r: r["received"], reverse=True)
        limit = max(1, min(int(limit), PAGE))
        page = max(1, int(page))
        items = [DecisionHit(id=r["id"], title=r["title"] or f"{COURT} advisory request {r['id'][3:]}",
                             court=COURT, date=r["decided"] or r["received"], case_number=r["id"][3:],
                             snippet=f"Status: {r['status'] or '?'}; received {r['received'] or '?'}",
                             url=_adv_url(r["id"]))
                 for r in hits[(page - 1) * limit: page * limit]]
        return Results(items=items, total=len(hits),
                       note=("Advisory-opinion requests (AJUDATA); matches title and number; newest "
                             "request first; get_decision on an 'AO' id lists its documents."))

    # ------------------------------------------------------------------ #
    async def get_decision(self, id):
        ident = (id or "").strip()
        caseno, _, fid = ident.partition("#")
        caseno, fid = _norm_ao(caseno) or _norm_caseno(caseno), fid.strip()
        if not caseno or (fid and not fid.isdigit()):
            raise BadRequest("Give an African Court application number (004/2013), an advisory "
                             "request ('AO 001/2013') or a document id as get_decision lists it "
                             "(004/2013#2034).")
        rec = await _case(caseno)
        if fid:
            return await self._document(rec, fid)
        return await self._case_record(rec)

    async def _case_record(self, rec: dict) -> Decision:
        caseno = rec["caseno"]
        if caseno.startswith("AO "):
            adv = next((r for r in await _advisory_rows() if r["id"] == caseno), {})
            title = adv.get("title") or f"{COURT} advisory request {caseno[3:]}"
            meta = {k: v for k, v in {"Request": caseno[3:], "Requested by": rec["parties"].removeprefix(
                "Introduced by "), "Received": adv.get("received", ""), "Decided": adv.get("decided", ""),
                "Status": adv.get("status", "")}.items() if v}
            row, parts = None, [f"# {title}", "## Request details"] + [f"- **{k}:** {v}" for k, v in meta.items()]
        else:
            row = await _row(caseno)
            title = _title(row) if row else (f"{rec['parties']} (Application {caseno})"
                                             if rec["parties"] else f"{COURT} Application {caseno}")
            parts = [f"# {title}", "## Case details", f"- **Application:** {caseno}"]
            meta = {}
        if row:
            app = row.get("applicant") or {}
            meta = {
                "Applicant": _http.clean(app.get("en_designation")),
                "Applicant type": _http.clean((app.get("applicant_type") or {}).get("en_title")),
                "Respondent": ", ".join(_http.clean(d.get("en_title")) for d in row.get("defendants") or []),
                "Received": row.get("reception_date") or "",
                "Status": _http.clean((row.get("case_status") or {}).get("en_title")),
                "Implementation": _http.clean((row.get("status") or {}).get("en_designation_status")),
                "Final decision": row.get("end_date") or "",
                "Themes": ", ".join(_http.clean(t.get("en_thematic")) for t in row.get("thematics") or []
                                    if t.get("en_thematic")),
            }
            meta = {k: v for k, v in meta.items() if v}
            parts += [f"- **{k}:** {v}" for k, v in meta.items()]
            arts = _articles(row)
            if arts:
                parts += ["", "## Rights invoked (and the Court's finding)"] + [f"- {a}" for a in arts]
        if rec["decisions"]:
            parts += ["", "## Decisions", "Open one with get_decision and the id shown in brackets."]
            for d in rec["decisions"]:
                head = d["label"] + (f", {d['date']}" if d["date"] else "")
                files = "; ".join(f"{f['lang']} [{f['id']}]" for f in d["files"]) or "no file published"
                parts.append(f"{'  - ' if d['opinion'] else '- '}{head}: {files}")
        else:
            parts += ["", "## Decisions", "None published for this case yet."]
        meta["Published documents"] = str(len(rec["docs"]))
        return Decision(
            id=caseno, title=title, text="\n".join(parts).strip(),
            url=_adv_url(caseno) if caseno.startswith("AO ") else _case_url(caseno),
            court=COURT, date=(row or {}).get("end_date") or meta.get("Decided", ""),
            case_number=caseno.removeprefix("AO "),
            metadata=meta)

    async def _document(self, rec: dict, fid: str) -> Decision:
        doc = next((d for d in rec["docs"] if d["fid"] == fid), None)
        if doc is None:
            known = ", ".join(f"{d['id']} ({d['label']}, {d['lang']})" for d in rec["docs"]) or "none"
            raise NotFound(f"Application {rec['caseno']} has no document {fid} "
                           f"(available: {known}).")
        if urlsplit(doc["url"]).hostname != HOST:
            raise SourceError(f"Error (AfCHPR): {doc['id']} is not on {HOST}; open it at {doc['url']}.")
        r = await _http.get(doc["url"])
        if r.status_code != 200:
            raise SourceError(_http.error("AfCHPR", f"document {doc['id']} failed", r.status_code),
                              r.status_code)
        if not r.content.startswith(b"%PDF"):
            raise SourceError(f"Error (AfCHPR): {doc['id']} is not a PDF; open it at {doc['url']}.")
        text = _http.pdf_text(r.content)
        if len(text) < 200:
            raise SourceError(f"Error (AfCHPR): {doc['id']} is a scanned PDF without a text layer "
                              f"(no OCR here); read it at {doc['url']}.", "pdf")
        what = f"{doc['label']} ({doc['of']})" if doc["of"] else doc["label"]
        ao = rec["caseno"].startswith("AO ")
        if ao:
            by = rec["parties"].removeprefix("Introduced by ")
            title = f"Advisory request {rec['caseno'][3:]}" + (f" ({by})" if by else "") + f": {what}"
        else:
            parties = rec["parties"] or f"Application {rec['caseno']}"
            title = f"{parties} (Application {rec['caseno']}): {what}"
        return Decision(
            id=doc["id"], title=title,
            text=text, url=doc["url"], court=COURT, date=doc["date"],
            case_number=rec["caseno"].removeprefix("AO "),
            metadata={k: v for k, v in {"Document": what, "Language": doc["lang"],
                                        "Case record": _adv_url(rec["caseno"]) if ao
                                        else _case_url(rec["caseno"])}.items() if v})
