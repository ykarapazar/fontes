"""EFTA Court (Luxembourg): case law from eftacourt.int.

eftacourt.int is a single-page app; `eftacourt.int/config.js` points it at an
undocumented, keyless JSON API at api.eftacourt.int/api (verified 2026-11-05):
  * GET /api/cases     -> JSON array of every case (~460, ~0.9 MB):
      {id:"c-wp-10023", ref:"E-25/24", parties, status (Decided|Pending),
       type (Advisory Opinion|Direct Action|Other), procedure, source (state),
       referringCourt, language, subjectMatter[], keywords, description (HTML),
       diary[], dateSubmitted, hearingDate, judgmentDate, publishedIn,
       documents:["dc-10023-0", ...]}
  * GET /api/downloads -> JSON array of every document (~2300, ~0.6 MB):
      {id:"dc-10023-4", title:"25/24 Judgment (EN)", docType:"Judgment",
       language:"English", date, file:"https://efta_back.on-forge.com/storage/imports/<hash>.pdf"}
  * PDFs: the app rewrites storage URLs to https://eftacourt.int/files/<hash>.pdf/<name>.pdf
    (same origin, served as application/pdf). Judgments are text PDFs; pypdf extracts them.

There is no server-side search (/api/search is 404), so search runs over the case
list in memory. Both lists are kept for an hour (in memory only).

Gotchas:
  * Joined cases: each component case (E-31/24, E-32/24) has its own entry, often
    without a judgment; the judgment sits on a separate entry whose ref is
    "Joined Cases E-31/24 and E-32/24". get_decision follows that link.
  * Some decided cases end with an order (withdrawal, inadmissibility, costs)
    rather than a judgment; get_decision returns the order then.
  * Refs are not always a single number ("E-9/04 COSTS", "E-6/94r", joined lists).
  * The EFTA Court does not use ECLI.
"""
from __future__ import annotations

import re
import time
from urllib.parse import quote

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, Results

API = "https://api.eftacourt.int/api"
SITE = "https://eftacourt.int"
COURT = "EFTA Court"
TTL = 3600.0

_CASE_ID = re.compile(r"^c-wp-\d+$", re.I)
_DOC_ID = re.compile(r"^dc-\d+-\d+$", re.I)
_REF = re.compile(r"\bE?-?0*(\d{1,3})/(\d{2})\b", re.I)
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_STORAGE = re.compile(r"/storage/(?:imports|uploads)/([A-Za-z0-9]+\.pdf)(?:[?#].*)?$", re.I)

_TYPES = {"advisory": "Advisory Opinion", "direct": "Direct Action", "other": "Other"}
_STATUS = {"decided": "Decided", "pending": "Pending"}
# What get_decision returns, best first; English preferred within each.
_JUDGMENT = ("Judgment",)
_ORDERS = ("Order of the Court", "Decision", "Order of the President")

_cache: dict[str, tuple[float, list]] = {}


async def _list(name: str) -> list[dict]:
    hit = _cache.get(name)
    if hit and time.monotonic() - hit[0] < TTL:
        return hit[1]
    r = await _http.get(f"{API}/{name}", headers={"Accept": "application/json"})
    if r.status_code != 200:
        raise SourceError(_http.error("EFTA Court", f"/api/{name} failed", r.status_code), r.status_code)
    try:
        data = r.json()
    except ValueError:
        raise SourceError(_http.error("EFTA Court", f"/api/{name} returned non-JSON",
                                      r.status_code), r.status_code) from None
    if not isinstance(data, list):
        raise SourceError(f"Error (EFTA Court): unexpected /api/{name} payload.", r.status_code)
    _cache[name] = (time.monotonic(), data)
    return data


def _refs(text: str) -> list[str]:
    """Normalised case numbers in a ref/query: 'Joined Cases E-1/24 and E-7/24' -> ['E-1/24', 'E-7/24']."""
    return [f"E-{int(n)}/{y}" for n, y in _REF.findall(text or "")]


def _pdf_url(file: str, name: str) -> str:
    m = _STORAGE.search(file or "")
    if not m:
        return file
    name = re.sub(r"[/\\]", "-", name or "document")
    name = re.sub(r'[:"*?<>|\x00-\x1f]', "", name).strip()[:120] or "document"
    return f"{SITE}/files/{m[1]}/{quote(name + '.pdf')}"


def _case_url(c: dict) -> str:
    return f"{SITE}/cases/{c['id']}"


def _title(c: dict) -> str:
    return _http.clean(c.get("parties")) or f"{COURT} {c.get('ref', '')}".strip()


def _haystack(c: dict) -> tuple[str, str]:
    """(high-weight text, everything) lower-cased for matching."""
    hi = " ".join([c.get("ref") or "", c.get("parties") or "", c.get("keywords") or "",
                   " ".join(c.get("subjectMatter") or [])])
    desc = _http.clean(re.sub(r"<[^>]+>", " ", c.get("description") or ""))
    rest = " ".join([desc, c.get("referringCourt") or "", c.get("source") or "",
                     c.get("procedure") or "", c.get("type") or ""])
    return hi.lower(), (hi + " " + rest).lower()


def _date(c: dict) -> str:
    return _http.iso_date(c.get("judgmentDate"))


def _pick(docs: list[dict], types: tuple[str, ...]) -> dict | None:
    for t in types:
        cands = [d for d in docs if d.get("docType") == t and d.get("file")]
        if cands:
            return next((d for d in cands if d.get("language") == "English"), cands[0])
    return None


class EFTACourt(Jurisdiction):
    code = "efta"
    name = "EFTA Court"
    languages = ("en", "no", "is", "de")
    aliases = ("efta court", "eftacourt", "eea court", "efta-court")
    sources = (
        Source(
            name="EFTA Court website (eftacourt.int, api.eftacourt.int)",
            url="https://eftacourt.int/cases",
            covers=("caselaw",),
            licence="unknown (no reuse terms published; the Legal Notice page is empty, footer '© 2026 EFTA Court')",
            commercial_use=None,
            ai_use=None,   # robots.txt on api.eftacourt.int allows everything; eftacourt.int has none (404); no AI/TDM clause
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~20 requests (2026-11)",
            terms_url="https://eftacourt.int/legal-notice",
        ),
    )
    caselaw_filters = {
        "type": "advisory (advisory opinions), direct (direct actions) or other",
        "status": "decided or pending",
        "country": "EEA EFTA state the case comes from: Norway, Iceland, Liechtenstein (referrals only)",
        "subject": "subject-matter tag, substring match, e.g. 'state aid', 'financial services'",
        "date_from": "judgment date from, YYYY-MM-DD",
        "date_to": "judgment date to, YYYY-MM-DD",
        "sort": "relevance (default with a query) or date (newest first; default without one)",
    }
    min_interval = {"api.eftacourt.int": 1.0, "eftacourt.int": 1.0}
    notes = ("Case law only, no legislation (search_legislation is not available for this jurisdiction): EFTA Court judgments, advisory opinions and orders since 1994 (PDF text). "
             "Ids are the court's case ids (c-wp-10023); case numbers like E-25/24 also work.")
    gaps = (
        "Case documents other than the judgment or order (in the Court's downloads list): source works but not built",
        "Non-English versions of judgments: listed by the source, English preferred; not built",
        "Full-text search of judgments: no server-side search on api.eftacourt.int; search is over case metadata",
        "EEA Agreement and EEA-incorporated acts (legislation): not available here, only EFTA Court case law is. "
        "The EU text of a directive or regulation can be searched under jurisdiction 'eu'; the EEA-adapted version is not covered",
    )
    samples = {
        "caselaw_query": "state liability",
        "decision_id": "c-wp-10023",   # E-25/24 Dartride v Norway, 5 June 2025
    }

    # ------------------------------------------------------------------ #
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        f = {k: str(v).strip() for k, v in (filters or {}).items() if str(v).strip()}
        query = (query or "").strip()
        cases = await _list("cases")

        typ = f.get("type", "").lower()
        if typ and typ not in _TYPES:
            raise BadRequest("type must be advisory, direct or other.")
        status = f.get("status", "").lower()
        if status and status not in _STATUS:
            raise BadRequest("status must be decided or pending.")
        for key in ("date_from", "date_to"):
            if key in f and not _DATE.match(f[key]):
                raise BadRequest(f"{key} must be YYYY-MM-DD.")
        if "country" in f and typ == "direct":
            raise BadRequest("country only applies to referrals (advisory opinions); direct actions "
                             "(ESA v a state) have no referring country. Put the state name in the "
                             "query instead, e.g. query 'Norway' with type direct.")
        sort = f.get("sort", "relevance" if query else "date").lower()
        if sort not in ("relevance", "date"):
            raise BadRequest("sort must be relevance or date.")

        # A query made only of case numbers ("E-25/24", "Joined Cases E-1/24 and E-7/24") is a lookup.
        rest = re.sub(r"(?i)\b(joined|cases?|and)\b|[,;]", " ", _REF.sub(" ", query))
        refs = _refs(query) if not rest.strip() else []
        words = [w for w in re.findall(r"\w+", query.lower()) if w not in ("and", "or", "v")]
        scored = []
        for c in cases:
            if typ and c.get("type") != _TYPES[typ]:
                continue
            if status and c.get("status") != _STATUS[status]:
                continue
            if "country" in f and (c.get("source") or "").lower() != f["country"].lower():
                continue
            if "subject" in f and not any(f["subject"].lower() in s.lower()
                                          for s in c.get("subjectMatter") or []):
                continue
            d = _date(c)
            if "date_from" in f and not (d and d >= f["date_from"]):
                continue
            if "date_to" in f and not (d and d <= f["date_to"]):
                continue
            if refs:
                if not set(refs) & set(_refs(c.get("ref"))):
                    continue
                score = 10 if _refs(c.get("ref")) == refs else 1
            elif words:
                hi, everything = _haystack(c)
                if not all(w in everything for w in words):
                    continue
                score = sum(3 * hi.count(w) + everything.count(w) for w in words)
                if query.lower() in everything:
                    score += 10
            else:
                score = 0
            scored.append((score, d or _http.iso_date(c.get("dateSubmitted")), c))

        if sort == "date":
            scored.sort(key=lambda t: t[1], reverse=True)
        else:
            scored.sort(key=lambda t: (t[0], t[1]), reverse=True)
        limit = max(1, min(int(limit), 50))
        page = max(1, int(page))
        items = []
        for _, _, c in scored[(page - 1) * limit:page * limit]:
            items.append(DecisionHit(
                id=c["id"],
                title=_title(c),
                court=COURT,
                date=_date(c),
                case_number=_http.clean(c.get("ref")),
                snippet=" · ".join(x for x in (c.get("status"), c.get("type"),
                                               _http.clean(c.get("keywords"))[:250]) if x),
                url=_case_url(c),
            ))
        return Results(items=items, total=len(scored),
                       note=("All words must match (case name, keywords, subject, summary); "
                             "no full-text search of judgments. Date = judgment date."))

    # ------------------------------------------------------------------ #
    async def _resolve(self, ident: str) -> tuple[dict, dict | None]:
        """(case, chosen document or None) for a case id, case number or document id."""
        cases = await _list("cases")
        downloads = {d["id"]: d for d in await _list("downloads") if d.get("id")}
        if _DOC_ID.match(ident):
            doc = downloads.get(ident.lower())
            if not doc:
                raise NotFound(f"The EFTA Court has no document {ident}.")
            case = next((c for c in cases if doc["id"] in (c.get("documents") or [])), None)
            if not case:
                raise NotFound(f"Document {ident} belongs to no case.")
            return case, doc
        if _CASE_ID.match(ident):
            case = next((c for c in cases if c["id"] == ident.lower()), None)
            if not case:
                raise NotFound(f"The EFTA Court has no case {ident}.")
        else:
            want = _refs(ident)
            if not want:
                raise BadRequest("Give an EFTA Court case id (c-wp-10023), a case number (E-25/24) "
                                 "or a document id (dc-10023-4).")
            norm = _http.clean(re.sub(r"(?i)^e-?", "", ident)).lower()
            same = [c for c in cases
                    if _http.clean(re.sub(r"(?i)^e-?", "", c.get("ref") or "")).lower() == norm]
            exact = [c for c in cases if _refs(c.get("ref")) == want]
            bare = [c for c in exact if re.fullmatch(r"E-\d+/\d{2}", (c.get("ref") or "").strip())]
            case = (same or bare or exact or [None])[0]
            if not case:
                raise NotFound(f"The EFTA Court has no case {ident}.")
        return case, None

    async def _decision_doc(self, case: dict) -> tuple[dict | None, dict | None]:
        """(document, joined case it came from or None): own judgment, else the judgment of a
        joined-cases entry listing this case, else an order (withdrawal, costs, inadmissibility)."""
        cases = await _list("cases")
        downloads = {d["id"]: d for d in await _list("downloads") if d.get("id")}

        def docs(c):
            return [downloads[i] for i in c.get("documents") or [] if i in downloads]

        mine = set(_refs(case.get("ref")))
        joined = [c for c in cases if c is not case and len(_refs(c.get("ref"))) > 1
                  and mine and mine <= set(_refs(c.get("ref")))]
        for types in (_JUDGMENT, _ORDERS):
            if d := _pick(docs(case), types):
                return d, None
            for other in joined:
                if d := _pick(docs(other), types):
                    return d, other
        return None, None

    async def get_decision(self, id):
        ident = (id or "").strip()
        case, doc = await self._resolve(ident)
        via = None
        if doc is None:
            doc, via = await self._decision_doc(case)
        if doc is None:
            what = "is still pending" if case.get("status") == "Pending" else "has no judgment or order online"
            raise NotFound(f"EFTA Court case {case.get('ref')} ({case['id']}) {what}.")

        pdf_url = _pdf_url(doc["file"], f"{(via or case).get('ref', '')} {doc.get('title', '')}")
        r = await _http.get(pdf_url)
        if r.status_code == 404:
            raise NotFound(f"The PDF for {doc['id']} is missing at the source.")
        if r.status_code != 200 or not r.content.startswith(b"%PDF"):
            raise SourceError(_http.error("EFTA Court", f"document {doc['id']} failed", r.status_code),
                              r.status_code)
        text = _http.pdf_text(r.content)
        if len(text) < 200:
            raise SourceError(f"Error (EFTA Court): {doc['id']} has no extractable text (scanned PDF?). "
                              f"Read it at {pdf_url}")

        src = via or case
        ids = set(src.get("documents") or []) - {doc["id"]}
        others = [f"{d['id']}: {d.get('title', '')}" for d in await _list("downloads") if d.get("id") in ids]
        meta = {
            "Case number": _http.clean(case.get("ref")),
            "Document": f"{doc.get('title', '')} ({doc['id']}, {doc.get('language', '')})",
            "PDF": pdf_url,
            "Joined judgment in": f"{via.get('ref')} ({via['id']})" if via else "",
            "Status": case.get("status") or "",
            "Type": case.get("type") or "",
            "Procedure": case.get("procedure") or "",
            "Referring court": _http.clean(case.get("referringCourt")),
            "State": case.get("source") or "",
            "Subject matter": ", ".join(case.get("subjectMatter") or []),
            "Language of the case": case.get("language") or "",
            "Lodged": _http.iso_date(case.get("dateSubmitted")),
            "Hearing": _http.iso_date(case.get("hearingDate")),
            "Published in": _http.clean(case.get("publishedIn")),
            "Other documents": "; ".join(others),
        }
        if ident.lower() not in (case["id"], doc["id"]):
            meta["Resolved from"] = ident
        return Decision(
            id=doc["id"] if _DOC_ID.match(ident) else case["id"],
            title=_title(case),
            text=text,
            url=_case_url(case),
            court=COURT,
            date=_date(src) or _http.iso_date(doc.get("date")),
            case_number=_http.clean(case.get("ref")),
            summary=_http.clean(case.get("keywords")),
            metadata={k: v for k, v in meta.items() if v},
        )
