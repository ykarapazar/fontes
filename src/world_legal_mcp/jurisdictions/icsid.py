"""ICSID (International Centre for Settlement of Investment Disputes, World Bank Group):
the ICSID case database at icsid.worldbank.org.

Neither service below is documented; both are what the official case-database pages use.
  * Case list: GET /api/all/cases -> {"data": {"GetAllCasesResult": [...]}}, ~1.6 MB,
    every registered case (1,162 on 2026-11-05). Only caseno, claimant, respondent,
    status and dateregistered (M/D/YYYY h:mm:ss AM) are filled; subject, sector,
    instruments and the "casedecisions" entries are empty placeholders. The list is
    fetched at most once per _TTL seconds and kept in memory (no disk cache).
  * Case record: GET /cases/case-database/case-detail?CaseNo=ARB/10/7 -> server-rendered
    HTML with three tabs: #proceeding (subject, sector, instruments, rules, then per
    proceeding: parties, tribunal, counsel, status, outcome), #materials ("Published
    Decisions" titles and "Available on the ICSID Website" PDF links on
    icsidfiles.worldbank.org) and #procedural_details (date/development tables).
    An unknown case number gives HTTP 200 with an empty <h1 class="h2">.
  * Decisions and awards are PDFs on icsidfiles.worldbank.org (…/OnlineAwards/C1000/
    DC9012_En.pdf). The ones checked have a text layer; text is extracted with pypdf.
    Scanned PDFs (no text layer) are not OCR'd: the adapter says so and gives the link.

Ids: a case is its ICSID case number ("ARB/10/7", "ARB(AF)/12/1", "UNCT/13/2"); a
published document is "<case number>#<file stem>" ("ARB/10/7#DC9012_En"), which
get_decision lists for every case.
"""
from __future__ import annotations

import re
import time
import unicodedata
from urllib.parse import quote, urlsplit

from lxml import html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, Results

HOST = "icsid.worldbank.org"
FILES_HOST = "icsidfiles.worldbank.org"
LIST_URL = f"https://{HOST}/api/all/cases"
DETAIL_URL = f"https://{HOST}/cases/case-database/case-detail?CaseNo="
COURT = "ICSID"
_TTL = 6 * 3600

_CASENO = re.compile(r"^[A-Z]+(\(AF\))?/\d{2}/\d+\b.*$")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

_list_cache: dict = {}            # {"t": monotonic time, "rows": [...]}
_detail_cache: dict = {}          # caseno -> parsed record (small LRU)


# --------------------------------------------------------------------------- #
# Small parsers
# --------------------------------------------------------------------------- #
def _fold(s: str) -> str:
    """Lower-case, accents stripped, for matching 'Sàrl' with 'sarl'."""
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


# ICSID styles respondents by the State's formal name; lawyers type the short name.
_STATE_STYLE = {
    "argentina": "argentine republic", "mexico": "united mexican states", "italy": "italian republic",
    "france": "french republic", "greece": "hellenic republic", "portugal": "portuguese republic",
    "lebanon": "lebanese republic", "gabon": "gabonese republic", "slovakia": "slovak republic",
    "kyrgyzstan": "kyrgyz republic", "usa": "united states of america", "us": "united states of america",
    "uae": "united arab emirates",
}


def _mdy(s: str) -> str:
    """'1/20/2021 12:00:00 AM' -> '2021-01-20'."""
    m = re.match(r"^\s*(\d{1,2})/(\d{1,2})/(\d{4})", s or "")
    return f"{m[3]}-{int(m[1]):02d}-{int(m[2]):02d}" if m else ""


def _detail_url(caseno: str) -> str:
    return DETAIL_URL + quote(caseno, safe="/()")


def _norm_caseno(s: str) -> str:
    s = re.sub(r"(?i)^ICSID\s+CASE\s+NO\.?\s*", "", _http.clean(s))
    s = re.sub(r"\s*/\s*", "/", s)
    s = re.sub(r"^[a-z]+(\(af\))?/", lambda m: m[0].upper(), s, flags=re.I)
    return re.sub(r"^([A-Z]+(?:\(AF\))?/\d{2}/)0+(?=\d)", r"\1", s)  # ARB/10/07 -> ARB/10/7


# --------------------------------------------------------------------------- #
# Source access
# --------------------------------------------------------------------------- #
async def _cases() -> list[dict]:
    if _list_cache and time.monotonic() - _list_cache["t"] < _TTL:
        return _list_cache["rows"]
    r = await _http.get(LIST_URL)
    if r.status_code != 200:
        raise SourceError(_http.error("ICSID", "case list failed", r.status_code), r.status_code)
    try:
        rows = r.json()["data"]["GetAllCasesResult"]
    except (ValueError, KeyError, TypeError):
        raise SourceError("Error (ICSID): unexpected case-list payload.", r.status_code) from None
    if not isinstance(rows, list):
        raise SourceError("Error (ICSID): unexpected case-list payload.", r.status_code)
    _list_cache.update(t=time.monotonic(), rows=rows)
    return rows


def _row_registered(c: dict) -> str:
    return _mdy(((c.get("caseproceedings") or [{}])[0] or {}).get("dateregistered") or "")


def _row_title(c: dict) -> str:
    cl, rs = _http.clean(c.get("claimant")), _http.clean(c.get("respondent"))
    if cl and rs:
        return f"{cl} v. {rs}"
    return cl or rs or f"ICSID Case No. {c.get('caseno')}"


def _rows_text(el) -> list[str]:
    """'- **Label** value' lines for the <li class="row"> label/value pairs under el."""
    out = []
    for li in el.xpath(".//li[contains(@class,'row')]"):
        label = _http.clean(" ".join(li.xpath(".//label//text()"))).rstrip(":")
        vals = li.xpath(".//div[contains(@class,'rightcol')]")
        if not vals:
            continue
        v = vals[0]
        for br in v.xpath(".//br"):
            br.tail = "; " + (br.tail or "")
        value = _http.clean(v.text_content()).strip("; ")
        if label and value:
            out.append(f"- **{label}:** {value}")
    return out


def _parse_detail(caseno: str, page: str) -> dict:
    root = lhtml.fromstring(page)
    h1 = root.xpath("//h1[contains(concat(' ', normalize-space(@class), ' '), ' h2 ')]")
    title = _http.clean(h1[0].text_content()) if h1 else ""
    if not title:
        raise NotFound(f"ICSID has no case {caseno}. Case numbers look like ARB/10/7, "
                       "ARB(AF)/12/1, CONC/16/1 or UNCT/13/2.")
    rec: dict = {"caseno": caseno, "title": title, "meta": {}, "proceeding_md": [],
                 "docs": [], "published": [], "history_md": []}

    tab = root.xpath("//div[@id='proceeding']")
    if tab:
        tab = tab[0]
        top = tab.xpath(".//ul[contains(@class,'proceedingcaselist1')]")
        if top:
            rec["proceeding_md"] += _rows_text(top[0])
        procs = tab.xpath(".//ul[contains(@class,'proceedingcaseproceedings')]")
        if procs:
            for node in procs[0]:
                if node.tag == "h3":
                    rec["proceeding_md"].append(f"\n### {_http.clean(node.text_content())}")
                elif node.tag == "ul":
                    h4 = _http.clean(" ".join(node.xpath("./h4//text()")))
                    if h4:
                        rec["proceeding_md"].append(f"\n#### {h4}")
                    rec["proceeding_md"] += _rows_text(node)
        for line in rec["proceeding_md"]:
            m = re.match(r"- \*\*(.+?):\*\* (.*)", line)
            # first value wins, except status/outcome: the latest proceeding's is the case's
            if m and (m[1] not in rec["meta"] or m[1] in ("Status of Proceeding", "Outcome of Proceeding")):
                rec["meta"][m[1]] = m[2]

    mat = root.xpath("//div[@id='materials']")
    if mat:
        proceeding, section = "", ""
        for node in mat[0]:
            if node.tag == "h3":
                proceeding = _http.clean(node.text_content())
            elif node.tag == "h4":
                section = _http.clean(node.text_content())
            elif node.tag == "p":
                label = _http.clean(" ".join(node.xpath("./span//text()")))
                links = node.xpath(".//a[@href]")
                if not links and section.startswith("Published") and label:
                    rec["published"].append((proceeding, label))
                for a in links:
                    href = a.get("href")
                    stem = re.sub(r"\.pdf$", "", urlsplit(href).path.rsplit("/", 1)[-1], flags=re.I)
                    rec["docs"].append({"id": f"{caseno}#{stem}", "stem": stem, "title": label,
                                        "language": _http.clean(a.text_content()),
                                        "date": _http.en_date(label), "proceeding": proceeding,
                                        "url": href})

    det = root.xpath("//div[@id='procedural_details']")
    if det:
        for node in det[0]:
            if node.tag == "h3":
                rec["history_md"].append(f"\n### {_http.clean(node.text_content())}")
            elif node.tag == "table":
                for tr in node.xpath(".//tbody/tr"):
                    tds = [_http.clean(td.text_content()) for td in tr.xpath("./td")]
                    if len(tds) >= 2 and tds[1]:
                        rec["history_md"].append(f"- {tds[0]}: {tds[1]}")
    return rec


async def _detail(caseno: str) -> dict:
    if caseno in _detail_cache:
        return _detail_cache[caseno]
    r = await _http.get(_detail_url(caseno))
    if r.status_code != 200:
        raise SourceError(_http.error("ICSID", f"case {caseno} failed", r.status_code), r.status_code)
    return _http.lru_put(_detail_cache, caseno, _parse_detail(caseno, r.text), 32)


# --------------------------------------------------------------------------- #
class ICSID(Jurisdiction):
    code = "icsid"
    name = "ICSID (World Bank investment arbitration)"
    languages = ("en", "fr", "es")
    aliases = ("international centre for settlement of investment disputes",
               "investment arbitration", "world bank arbitration", "ciadi", "cirdi")
    sources = (
        Source(
            name="ICSID case database (icsid.worldbank.org, icsidfiles.worldbank.org)",
            url="https://icsid.worldbank.org/cases/case-database",
            covers=("caselaw",),
            licence=("© ICSID / World Bank Group; WBG Terms and Conditions (2025-07-25): "
                     "non-commercial use with attribution, no derivative or commercial use "
                     "(ICSID's own /user-agreement page answers 403 to this client)"),
            commercial_use=False,
            ai_use=None,   # robots.txt allows /api and case pages; no AI/TDM clause in the WBG terms
            auth="none",
            rate_limit=("unknown; 1 s spacing, case list cached in memory 6 h; "
                        "no 429 seen in ~10 requests (2026-11)"),
            terms_url="https://www.worldbank.org/ext/en/legal/terms-conditions",
        ),
    )
    caselaw_filters = {
        "status": "pending or concluded",
        "type": "case-number prefix: ARB, ARB(AF), CONC, CONC(AF), UNCT, ADHOC, ADM",
        "respondent": "text the respondent's name must contain, e.g. Argentina",
        "date_from": "registered on or after YYYY-MM-DD",
        "date_to": "registered on or before YYYY-MM-DD",
    }
    min_interval = {HOST: 1.0, FILES_HOST: 1.0}
    notes = ("ICSID investment arbitration cases (World Bank). Search covers case number, parties "
             "and status; get_decision on a case number gives the case record and its published "
             "decisions; '<case no>#<doc>' gives an award's text (from PDF). Non-commercial reuse only.")
    gaps = (
        "Decisions listed as published but not on the ICSID website: not published online by ICSID (titles only)",
        "Scanned award PDFs: scans only, no text (no OCR)",
    )
    samples = {
        "caselaw_query": "Uruguay",
        "decision_id": "ARB/10/7",   # Philip Morris v. Uruguay
    }

    # ------------------------------------------------------------------ #
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        f = {k: str(v).strip() for k, v in (filters or {}).items() if str(v).strip()}
        status = f.get("status", "").lower()
        if status and status not in ("pending", "concluded"):
            raise BadRequest("status must be pending or concluded.")
        ctype = f.get("type", "").upper()
        if ctype and not re.fullmatch(r"[A-Z]+(\(AF\))?", ctype):
            raise BadRequest("type must be a case-number prefix such as ARB, ARB(AF), CONC or UNCT.")
        for key in ("date_from", "date_to"):
            if key in f and not _DATE.match(f[key]):
                raise BadRequest(f"{key} must be YYYY-MM-DD.")
        resp = _fold(f.get("respondent", ""))
        styled = {}                      # short name typed -> ICSID's formal style
        if resp in _STATE_STYLE:
            styled[resp] = resp = _STATE_STYLE[resp]

        q = (query or "").strip()
        exact = _norm_caseno(q) if _CASENO.match(_norm_caseno(q)) else ""
        words = [_fold(w) for w in re.findall(r'"[^"]+"|\S+', q)]
        words = [w.strip('"') for w in words if w.strip('"') and w.lower() not in ("v", "v.", "vs", "vs.")]
        alts = [(w, _STATE_STYLE.get(w)) for w in words]
        styled.update({w: a for w, a in alts if a})

        hits = []
        for c in await _cases():
            cno = c.get("caseno") or ""
            reg = _row_registered(c)
            if status and (c.get("status") or "").lower() != status:
                continue
            if ctype and cno.split("/")[0].upper() != ctype:
                continue
            if resp and resp not in _fold(c.get("respondent") or ""):
                continue
            if "date_from" in f and (not reg or reg < f["date_from"]):
                continue
            if "date_to" in f and (not reg or reg > f["date_to"]):
                continue
            if exact:
                if cno.upper() != exact and not cno.upper().startswith(exact + " "):
                    continue
            else:
                hay = _fold(" ".join(str(c.get(k) or "") for k in ("caseno", "claimant", "respondent", "status")))
                if not all(w in hay or (a and a in hay) for w, a in alts):
                    continue
            hits.append(c)
        hits.sort(key=_row_registered, reverse=True)

        limit = max(1, min(int(limit), 50))
        page = max(1, int(page))
        items = [DecisionHit(
            id=c["caseno"],
            title=_row_title(c),
            court=COURT,
            date=_row_registered(c),
            case_number=c["caseno"],
            snippet=f"Status: {c.get('status') or '?'}; registered {_row_registered(c) or '?'}",
            url=_detail_url(c["caseno"]),
        ) for c in hits[(page - 1) * limit: page * limit]]
        note = ("Matches case number, claimant, respondent and status (all words, "
                "accents ignored); newest registration first; date = registration date. "
                "Subject/sector/treaty standards (e.g. fair and equitable treatment, expropriation) "
                "and decision types (e.g. annulment) are not searchable here, so 0 results means no "
                "case with those words in its number, parties or status, not that no such case exists. "
                "Annulment decisions and awards are reached through a case record: get_decision with "
                "the case number lists them.")
        if styled:
            note += " " + "; ".join(f"'{k}' also matched as ICSID's '{v}'" for k, v in styled.items()) + "."
        return Results(items=items, total=len(hits), note=note)

    # ------------------------------------------------------------------ #
    async def get_decision(self, id):
        ident = (id or "").strip()
        caseno, _, stem = ident.partition("#")
        if not stem and re.search(r"\s+DC\d+", ident):          # "ARB/10/7 DC9012_En"
            caseno, stem = re.split(r"\s+(?=DC\d+)", ident, maxsplit=1)
        caseno, stem = _norm_caseno(caseno), stem.strip()
        if not _CASENO.match(caseno):
            raise BadRequest("Give an ICSID case number (ARB/10/7, ARB(AF)/12/1, UNCT/13/2) or a "
                             "document id as get_decision lists it (ARB/10/7#DC9012_En).")
        rec = await _detail(caseno)
        if stem:
            return await self._document(rec, stem)
        return self._case(rec)

    def _case(self, rec: dict) -> Decision:
        parts = [f"# {rec['title']}", "## Case details", *rec["proceeding_md"]]
        if rec["docs"]:
            parts += ["", "## Decisions and awards available on the ICSID website",
                      "Open one with get_decision and the id shown in brackets."]
            proc = None
            for d in rec["docs"]:
                if d["proceeding"] != proc:
                    proc = d["proceeding"]
                    parts.append(f"\n### {proc}" if proc else "")
                parts.append(f"- {d['title']} ({d['language']}) [{d['id']}] {d['url']}")
        else:
            parts += ["", "## Decisions and awards",
                      "None published on the ICSID website for this case."]
        if rec["published"]:
            parts += ["", "## Published decisions (listed by ICSID; may be published elsewhere)"]
            parts += [f"- {p}: {t}" if p else f"- {t}" for p, t in rec["published"]]
        if rec["history_md"]:
            parts += ["", "## Procedural details", *rec["history_md"]]
        text = re.sub(r"\n{3,}", "\n\n", "\n".join(parts)).strip()
        meta = {k: v for k, v in rec["meta"].items()
                if k in ("Subject of Dispute", "Economic Sector", "Instrument(s) Invoked",
                         "Applicable Rules", "Status of Proceeding", "Outcome of Proceeding")}
        meta["Published documents"] = str(len(rec["docs"]))
        return Decision(
            id=rec["caseno"],
            title=rec["title"],
            text=text,
            url=_detail_url(rec["caseno"]),
            court=COURT,
            date=_http.en_date(rec["meta"].get("Date Registered", "")),
            case_number=rec["caseno"],
            summary=rec["meta"].get("Outcome of Proceeding", ""),
            metadata=meta,
        )

    async def _document(self, rec: dict, stem: str) -> Decision:
        doc = next((d for d in rec["docs"] if d["stem"].lower() == stem.lower()), None)
        if doc is None:
            known = ", ".join(d["stem"] for d in rec["docs"]) or "none"
            raise NotFound(f"Case {rec['caseno']} has no document {stem} on the ICSID website "
                           f"(available: {known}).")
        if urlsplit(doc["url"]).hostname != FILES_HOST or not doc["url"].lower().endswith(".pdf"):
            raise SourceError(f"Error (ICSID): {doc['id']} is not a PDF on {FILES_HOST}; "
                              f"open it at {doc['url']}.")
        r = await _http.get(doc["url"])
        if r.status_code != 200:
            raise SourceError(_http.error("ICSID", f"document {doc['id']} failed", r.status_code),
                              r.status_code)
        text = _http.pdf_text(r.content)
        if len(text) < 200:
            raise SourceError(f"Error (ICSID): {doc['id']} is a scanned PDF without a text layer "
                              f"(no OCR here); read it at {doc['url']}.", "pdf")
        return Decision(
            id=doc["id"],
            title=f"{rec['title']}: {doc['title']}",
            text=text,
            url=doc["url"],
            court=COURT,
            date=doc["date"],
            case_number=rec["caseno"],
            metadata={k: v for k, v in {"Document": doc["title"], "Language": doc["language"],
                                        "Proceeding": doc["proceeding"],
                                        "Case record": _detail_url(rec["caseno"])}.items() if v},
        )
