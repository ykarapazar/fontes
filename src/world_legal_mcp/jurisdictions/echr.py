"""European Court of Human Rights: case law from HUDOC (hudoc.echr.coe.int).

HUDOC has no documented API. Both services below are the ones the official HUDOC
single-page app calls; they are keyless and answer the project User-Agent.
  * Search: GET /app/query/results?query=...&select=...&sort=...&start=N&length=N
    -> {"resultcount": n, "results": [{"columns": {...}}]}
  * Full text: GET /app/conversion/docx/html/body?library=ECHR&id=<itemid>
    -> HTML fragment (Word export, ~1 MB with inline CSS for a Grand Chamber
    judgment). An unknown itemid gives HTTP 204 with an empty body.

Gotchas this code encodes (verified 2026-11-05):
  * `sort` must be present (empty = relevance) or the query service answers 404.
  * Free-text words are AND-ed ("surveillance journalist" == "surveillance AND
    journalist"); quotes make a phrase. Field syntax: appno:"58170/13",
    ecli:"ECLI:CE:ECHR:...", respondent:"TUR", article:"10-1", importance:"1",
    kpdate>="2020-01-01T00:00:00.0Z", documentcollectionid2:"GRANDCHAMBER".
  * Every judgment exists as several items (EN, FR, translations, legal summaries,
    press releases), all sharing appno/ECLI. Search defaults to English
    judgments + decisions; ECLI / application number lookups prefer the English
    judgment.
  * itemids: 001-NNNNNN (judgments, decisions, communicated cases),
    002-NNNNN (Case-Law Information Note summaries), 003-NNNNNNN-NNNNNNNN
    (press releases, advisory-opinion summaries).
  * The Convention itself is published only as PDF (echr.coe.int
    /documents/d/echr/convention_eng); www.coe.int (treaty office) blocks this
    client at Cloudflare. No legislation methods.
"""
from __future__ import annotations

import re

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, Results

HOST = "hudoc.echr.coe.int"
QUERY = f"https://{HOST}/app/query/results"
BODY = f"https://{HOST}/app/conversion/docx/html/body"
PUBLIC = f"https://{HOST}/eng?i="

_SELECT = ("itemid,docname,appno,kpdate,doctype,doctypebranch,importance,conclusion,article,"
           "respondent,ecli,languageisocode,documentcollectionid2,separateopinion")
_ITEMID = re.compile(r"^\d{3}-\d+(-\d+)?$")
_ECLI = re.compile(r"^ECLI:CE:ECHR:\d{4}:\w+$", re.I)
_APPNO = re.compile(r"^\d{1,6}/\d{2}$")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_LANG = re.compile(r"^[A-Z]{3}$")

_COLLECTIONS = {
    "judgments": "JUDGMENTS", "decisions": "DECISIONS", "grandchamber": "GRANDCHAMBER",
    "chamber": "CHAMBER", "committee": "COMMITTEE", "communicated": "COMMUNICATEDCASES",
    "advisory": "ADVISORYOPINIONS", "summaries": "CLIN",
}
_DEFAULT_COLLECTIONS = ("judgments", "decisions")
_BRANCH = {"GRANDCHAMBER": "Grand Chamber", "CHAMBER": "Chamber", "COMMITTEE": "Committee",
           "ADMISSIBILITY": "Admissibility decision", "ADMISSIBILITYCOM": "Committee decision"}
_IMPORTANCE = {"1": "Key case", "2": "High", "3": "Medium", "4": "Low"}


def _court(c: dict) -> str:
    branch = _BRANCH.get(c.get("doctypebranch") or "", "")
    return f"European Court of Human Rights ({branch})" if branch else "European Court of Human Rights"


def _case_number(c: dict) -> str:
    return ", ".join(a for a in (c.get("appno") or "").split(";") if a)


async def _query(query: str, *, sort: str = "", start: int = 0, length: int = 10) -> dict:
    r = await _http.get(QUERY, params={"query": query, "select": _SELECT, "sort": sort,
                                       "start": start, "length": length})
    if r.status_code != 200:
        raise SourceError(_http.error("HUDOC", "search failed", r.status_code,
                                      "Check the query syntax (balanced quotes/parentheses)."),
                          r.status_code)
    try:
        data = r.json()
    except ValueError:
        raise SourceError(_http.error("HUDOC", "search returned non-JSON", r.status_code),
                          r.status_code) from None
    if not isinstance(data, dict) or "results" not in data:
        raise SourceError("Error (HUDOC): unexpected search payload.", r.status_code)
    return data


def _id_clause(text: str) -> str | None:
    """Field clause when the text is an ECLI or application number(s), else None."""
    if _ECLI.match(text):
        return f'ecli:"{text.upper()}"'
    nos = [n for n in re.split(r"[\s;,]+", text) if n]
    if nos and all(_APPNO.match(n) for n in nos):
        return "(" + " OR ".join(f'appno:"{n}"' for n in nos) + ")"
    return None


def _plain_phrase(query: str) -> bool:
    """True for plain multi-word text (no quotes, operators or fields), e.g. a typed case name."""
    return len(query.split()) > 1 and not re.search(r'["():<>=]|\b(AND|OR|NOT)\b', query)


def _quoted_name(query: str) -> str | None:
    """Inner text when the whole query is one quoted multi-word phrase, e.g. "Big Brother Watch"."""
    m = re.fullmatch(r'"([^"]+)"', query)
    return m.group(1).strip() if m and len(m.group(1).split()) > 1 else None


class ECHR(Jurisdiction):
    code = "echr"
    name = "European Court of Human Rights"
    languages = ("en", "fr")
    aliases = ("ecthr", "hudoc", "strasbourg", "coe", "council of europe", "cedh")
    sources = (
        Source(
            name="HUDOC (European Court of Human Rights)",
            url="https://hudoc.echr.coe.int",
            covers=("caselaw",),
            licence=("© ECHR-CEDH; reproduction allowed free of charge, with acknowledgment, for "
                     "private use or information/education about the Court's work"),
            commercial_use=False,   # disclaimer: other uses, incl. commercial, need prior written permission
            ai_use=None,            # no robots.txt (SPA HTML served) and no AI/TDM clause in the terms
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~20 requests (2026-11)",
            terms_url="https://www.echr.coe.int/disclaimer",
        ),
        # Pointer only: no legislation tools; named so "not supported" messages say where to read the text.
        Source(
            name="European Convention on Human Rights and Protocols (official PDF, read it there; not available through this server)",
            url="https://www.echr.coe.int/documents/d/echr/convention_eng",
            covers=("legislation",),
            auth="none",
            terms_url="https://www.echr.coe.int/disclaimer",
        ),
    )
    caselaw_filters = {
        "collection": ("comma list of judgments, decisions, grandchamber, chamber, committee, "
                       "communicated, advisory, summaries, or 'all' (default: judgments,decisions)"),
        "language": "HUDOC language code: ENG (default), FRE, TUR, RUS, ... or 'any'",
        "respondent": "respondent State, ISO 3166 alpha-3, e.g. GBR, TUR (comma list allowed)",
        "article": "Convention article as HUDOC tags it, e.g. 8, 10-1, P1-1",
        "importance": "1 (key case), 2, 3 or 4; returns that level or higher",
        "date_from": "YYYY-MM-DD",
        "date_to": "YYYY-MM-DD",
        "sort": "relevance (default) or date (newest first)",
    }
    min_interval = {HOST: 1.0}
    notes = ("Case law only (ECtHR judgments, decisions, communicated cases, advisory opinions, "
             "Commission decisions) via HUDOC. Ids are HUDOC itemids; ECLI and application numbers "
             "also work. Non-commercial reuse only. Convention and Protocol text is not available "
             "here (search_legislation is unsupported): read it as a PDF at "
             "https://www.echr.coe.int/documents/d/echr/convention_eng")
    gaps = (
        "Convention and Protocols text: only a PDF on echr.coe.int; coe.int treaty office blocks our client (Cloudflare)",
        "Press releases: in HUDOC but filtered out of search; not built",
        "Execution of judgments (Committee of Ministers, HUDOC-EXEC): not researched yet",
        "Parties' pleadings and case files: not researched yet",
    )
    samples = {
        "caselaw_query": '"bulk interception"',
        "decision_id": "001-210077",   # Big Brother Watch and Others v. UK [GC], 25 May 2021
    }

    # ------------------------------------------------------------------ #
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        f = {k: str(v).strip() for k, v in (filters or {}).items() if str(v).strip()}
        query = (query or "").strip()
        # Press releases (003-...) carry the JUDGMENTS tag too; the HUDOC app hides them the same way.
        parts = ["contentsitename:ECHR", "(NOT (doctype=PR OR doctype=HFCOMOLD OR doctype=HECOMOLD))"]
        if query:
            parts.append(_id_clause(query) or f"({query})")

        coll = [c.strip().lower() for c in f.get("collection", "").split(",") if c.strip()]
        coll = coll or list(_DEFAULT_COLLECTIONS)
        if "all" not in coll:
            bad = [c for c in coll if c not in _COLLECTIONS]
            if bad:
                raise BadRequest(f"Unknown collection {bad}. Use: {', '.join(_COLLECTIONS)} or all.")
            parts.append("(" + " OR ".join(f'documentcollectionid2:"{_COLLECTIONS[c]}"'
                                           for c in coll) + ")")
        else:
            parts.append('(documentcollectionid2:"CASELAW")')

        lang = f.get("language", "ENG").upper()
        if lang != "ANY":
            if not _LANG.match(lang):
                raise BadRequest("language must be a 3-letter HUDOC code (ENG, FRE, TUR, ...) or 'any'.")
            parts.append(f'(languageisocode:"{lang}")')

        if "respondent" in f:
            codes = [c.strip().upper() for c in f["respondent"].split(",") if c.strip()]
            if not all(re.fullmatch(r"[A-Z]{3}", c) for c in codes):
                raise BadRequest("respondent must be ISO 3166 alpha-3 codes, e.g. GBR or TUR,FRA.")
            parts.append("(" + " OR ".join(f'respondent:"{c}"' for c in codes) + ")")
        want_art = None
        if "article" in f:
            art = re.sub(r"(?i)^(art(icle)?\.?\s*)", "", f["article"]).lower()
            if not re.fullmatch(r"(p\d+-)?\d+(-\d+)*(-[a-z])?", art):
                raise BadRequest("article must look like 8, 10-1, 5-1-c or P1-1.")
            art = "P" + art[1:] if art.startswith("p") else art
            parts.append(f'(article:"{art}")')
            want_art = art
        if "importance" in f:
            if f["importance"] not in _IMPORTANCE:
                raise BadRequest("importance must be 1 (key case), 2, 3 or 4.")
            levels = [str(i) for i in range(1, int(f["importance"]) + 1)]
            parts.append("(" + " OR ".join(f'importance:"{i}"' for i in levels) + ")")
        for key, op in (("date_from", ">="), ("date_to", "<=")):
            if key in f:
                if not _DATE.match(f[key]):
                    raise BadRequest(f"{key} must be YYYY-MM-DD.")
                parts.append(f'(kpdate{op}"{f[key]}T00:00:00.0Z")')

        sort = f.get("sort", "relevance").lower()
        if sort not in ("relevance", "date"):
            raise BadRequest("sort must be relevance or date.")
        limit = max(1, min(int(limit), 50))
        page = max(1, int(page))
        data, phrase = None, False
        name = query if _plain_phrase(query) else _quoted_name(query)
        if query and name and not _id_clause(query):
            # A typed case name (quoted or not) ranks poorly in full text; try it as a case-name phrase first.
            p2 = [f'(docname:"{name}")' if x == f"({query})" else x for x in parts]
            data = await _query(" AND ".join(p2), sort="kpdate Descending" if sort == "date" else "",
                                start=(page - 1) * limit, length=limit)
            phrase = bool(data.get("resultcount"))
        if not phrase:
            data = await _query(" AND ".join(parts), sort="kpdate Descending" if sort == "date" else "",
                                start=(page - 1) * limit, length=limit)
        items = []
        for row in data["results"]:
            c = row.get("columns") or {}
            if not c.get("itemid"):
                continue
            # HUDOC matches article:"9" inside other tags (39, 37-1); keep exact tag or "N-..." sub-tags.
            if want_art and not any(t.strip().lower() == want_art.lower()
                                    or t.strip().lower().startswith(want_art.lower() + "-")
                                    for t in (c.get("article") or "").split(";")):
                continue
            items.append(DecisionHit(
                id=c["itemid"],
                title=_http.clean(c.get("docname")) or f"ECtHR {_case_number(c)}",
                court=_court(c),
                date=_http.iso_date(c.get("kpdate")),
                case_number=_case_number(c),
                snippet=_http.clean(c.get("conclusion"))[:300],
                url=PUBLIC + c["itemid"],
            ))
        note = ((f"Matched as a phrase in case names (\"{name}\"); to search the full text, quote the phrase or join words with AND. "
                 if phrase else "Words are AND-ed; quote phrases. ") + "Defaults: English judgments and decisions "
                "(filters language, collection).")
        if want_art:
            note += (" Article filter is post-filtered to exact tags (HUDOC matches substrings), so "
                     "pages may hold fewer than limit hits and the total is unknown.")
        return Results(items=items, total=None if want_art else data.get("resultcount"), note=note)

    # ------------------------------------------------------------------ #
    async def _resolve(self, ident: str) -> dict:
        """Metadata row for an itemid, ECLI or application number."""
        if _ITEMID.match(ident):
            data = await _query(f'contentsitename:ECHR AND itemid:"{ident}"', length=1)
            if not data["results"]:
                raise NotFound(f"HUDOC has no item {ident}.")
            return data["results"][0]["columns"]
        clause = _id_clause(ident)
        if not clause:
            raise BadRequest("Give a HUDOC itemid (e.g. 001-210077), an ECLI "
                             "(ECLI:CE:ECHR:2021:0525JUD005817013) or an application number (58170/13).")
        base = f"contentsitename:ECHR AND (NOT (doctype=PR)) AND {clause}"
        # Prefer the English judgment, then English decision, then anything.
        for extra in ('(documentcollectionid2:"JUDGMENTS") AND (languageisocode:"ENG")',
                      '(documentcollectionid2:"DECISIONS") AND (languageisocode:"ENG")',
                      '(documentcollectionid2:"JUDGMENTS" OR documentcollectionid2:"DECISIONS")',
                      '(documentcollectionid2:"CASELAW")'):
            data = await _query(f"{base} AND {extra}", sort="kpdate Descending", length=1)
            if data["results"]:
                return data["results"][0]["columns"]
        raise NotFound(f"HUDOC has no judgment or decision for {ident}.")

    async def get_decision(self, id):
        ident = (id or "").strip()
        c = await self._resolve(ident)
        itemid = c["itemid"]
        r = await _http.get(BODY, params={"library": "ECHR", "id": itemid})
        if r.status_code == 204 or (r.status_code == 200 and not r.content):
            raise NotFound(f"HUDOC has no document text for {itemid}.")
        if r.status_code != 200:
            raise SourceError(_http.error("HUDOC", f"document {itemid} failed", r.status_code),
                              r.status_code)
        text = _http.html_to_md(r.text)
        if not text:
            raise SourceError(f"Error (HUDOC): empty document text for {itemid}.")
        meta = {"ECLI": c.get("ecli") or "",
                "Respondent": (c.get("respondent") or "").replace(";", ", "),
                "Articles": (c.get("article") or "").replace(";", ", "),
                "Importance": _IMPORTANCE.get(c.get("importance") or "", ""),
                "Conclusion": _http.clean(c.get("conclusion")).replace(";", "; "),
                "Separate opinions": {"TRUE": "yes", "FALSE": "no"}.get(c.get("separateopinion") or "", ""),
                "Language": c.get("languageisocode") or "",
                "Document type": c.get("doctype") or "",
                "Collections": (c.get("documentcollectionid2") or "").replace(";", ", ")}
        if ident != itemid:
            meta["Resolved from"] = ident
        return Decision(
            id=itemid,
            title=_http.clean(c.get("docname")) or f"ECtHR {_case_number(c)}",
            text=text,
            url=PUBLIC + itemid,
            court=_court(c),
            date=_http.iso_date(c.get("kpdate")),
            case_number=_case_number(c),
            metadata={k: v for k, v in meta.items() if v},
        )
