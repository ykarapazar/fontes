"""WTO dispute settlement (World Trade Organization): the dispute pages on www.wto.org.

There is no disputes API. (The WTO API portal, apiportal.wto.org, offers only ePing, QR,
Timeseries and TFAD, behind a key.) The site builds its dispute pages from static
JavaScript data files, which this adapter reads as data. It never runs them.
  * /library/disputes/dispute_case_arrays_e.js: `ds_array[n] = {code, title, origin,
    destination, start_date "YYYY/MM/DD", subject, short_title, agreement, update_date,
    status "ST6#2024_04_26|...", third_party, one_page_sum, reports_adopted, pan_agree}`.
    Countries are WTO codes joined by '#' (EEC = EC/EU). There are 646 disputes as of 2026-11-06.
  * /library/disputes/dispute_arrays_e.js: lookup tables ds_status (code -> name),
    ds_subject, ds_agreement and ds_article (the agreement article ids in "A9_810").
  * /library/news/news_vars_e.js: `country[...] = {code: "MYS", name: "Malaysia", ...}`.
  These three files (~0.9 MB in all) are fetched at most once per _TTL and kept in memory.
  They are windows-1252 text with HTML entities.
  * Case page /english/tratop_e/dispu_e/cases_e/ds{n}_e.htm: server-side HTML. Its
    "Summary of the dispute to date" (consultations, panel/AB proceedings with the
    "Summary of key findings", implementation) is static, so that is the decision text. The
    status, key facts and document boxes are written by JavaScript from the arrays above.
    An unknown number redirects to /error/error_404.htm, which answers HTTP 200.
  * Panel and Appellate Body report texts are on docs.wto.org, whose robots.txt says
    "Disallow: /". This adapter never fetches them. It gives a Documents Online search
    link (WT/DS{n}/*) for a human to follow, plus the wto.org one-page summary PDF where
    one exists.

Ids: "DS600". get_decision also accepts "ds600", "600", "WT/DS600" and "DS 600".
"""
from __future__ import annotations

import html as _html
import re
import time
from urllib.parse import quote

from lxml import html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, Results

HOST = "www.wto.org"
BASE = f"https://{HOST}"
CASES_JS = f"{BASE}/library/disputes/dispute_case_arrays_e.js"
LOOKUP_JS = f"{BASE}/library/disputes/dispute_arrays_e.js"
COUNTRY_JS = f"{BASE}/library/news/news_vars_e.js"
COURT = "WTO Dispute Settlement Body"
_TTL = 6 * 3600

_ID = re.compile(r"^(?:WT\s*/\s*)?(?:DS\s*)?(\d{1,4})$", re.I)
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

_data: dict = {}              # {"t": monotonic, "cases": {n: dict}, "status": {...}, ...}
_page_cache: dict = {}        # n -> parsed case page (small LRU)


# --------------------------------------------------------------------------- #
# Parsing the JavaScript data files (as text, never executed)
# --------------------------------------------------------------------------- #
def _decode(r) -> str:
    return r.content.decode("cp1252", errors="replace")


def _u(s: str) -> str:
    """HTML entities and &nbsp; to plain text, whitespace collapsed."""
    return _http.clean(_html.unescape(s or ""))


def _objects(js: str, array: str) -> list[tuple[str, dict]]:
    """Every `array[index] = { key: "value", ... };` as (index, {key: value})."""
    out = []
    pat = re.compile(re.escape(array) + r"\[([^\]]*)\]\s*=\s*\{(.*?)\n\s*\};", re.S)
    for m in pat.finditer(js):
        fields = dict(re.findall(r'(\w+):\s*"((?:[^"\\]|\\.)*)"', m[2]))
        out.append((m[1], fields))
    return out


def _slash_date(s: str) -> str:
    """'2021/01/15' or '2024_04_26' -> '2021-01-15'."""
    m = re.match(r"^(\d{4})[/_-](\d{2})[/_-](\d{2})$", (s or "").strip())
    return f"{m[1]}-{m[2]}-{m[3]}" if m else ""


async def _fetch(url: str, what: str) -> str:
    r = await _http.get(url)
    if r.status_code != 200:
        raise SourceError(_http.error("WTO", f"{what} failed", r.status_code), r.status_code)
    return _decode(r)


async def _load() -> dict:
    if _data and time.monotonic() - _data["t"] < _TTL:
        return _data
    cases_js = await _fetch(CASES_JS, "dispute list")
    lookup_js = await _fetch(LOOKUP_JS, "dispute lookup tables")
    country_js = await _fetch(COUNTRY_JS, "member list")

    cases = {}
    for idx, f in _objects(cases_js, "ds_array"):
        if idx.isdigit() and f.get("code"):
            cases[int(idx)] = f
    if len(cases) < 100:
        raise SourceError("Error (WTO): the dispute list has an unexpected format.", "payload")
    status = {f["status_code"]: _u(f.get("status_name", "")) for _, f in _objects(lookup_js, "ds_status")
              if f.get("status_code")}
    subject = {f["subject_id"]: _u(f.get("subject_name", "")) for _, f in _objects(lookup_js, "ds_subject")
               if f.get("subject_id")}
    agreement = {f["agreement_id"]: _u(f.get("agreement_short_name") or f.get("agreement_name", ""))
                 for _, f in _objects(lookup_js, "ds_agreement") if f.get("agreement_id")}
    article = {f["article_id"]: _u(f.get("article_name", "")) for _, f in _objects(lookup_js, "ds_article")
               if f.get("article_id")}
    country = {c: _u(n) for c, n in re.findall(
        r'country\[country\.length\]\s*=\s*\{\s*code:\s*"([^"]*)",\s*name:\s*"([^"]*)"', country_js)}
    _data.clear()
    _data.update(t=time.monotonic(), cases=cases, status=status, subject=subject,
                 agreement=agreement, article=article, country=country)
    return _data


# --------------------------------------------------------------------------- #
# Record helpers
# --------------------------------------------------------------------------- #
def _members(d: dict, codes: str, start: str) -> list[str]:
    out = []
    for c in filter(None, (codes or "").split("#")):
        if c == "EEC":   # the site's own rule: EC before the Lisbon Treaty date, EU after
            out.append("European Union" if start >= "2009/12/01" else "European Communities")
        else:
            out.append(d["country"].get(c, c))
    return out


def _statuses(d: dict, c: dict) -> list[tuple[str, str]]:
    """[(status name, ISO date)], newest last as the source lists them."""
    out = []
    for part in filter(None, (c.get("status") or "").split("|")):
        bits = part.split("#")
        out.append((d["status"].get(bits[0], bits[0]), _slash_date(bits[1]) if len(bits) > 1 else ""))
    return out


def _status_line(d: dict, c: dict) -> str:
    return "; ".join(f"{n} ({dt})" if dt else n for n, dt in _statuses(d, c))


def _agreements(d: dict, codes: str) -> list[str]:
    """'A9_810#A9_826#A22_48' -> ['GATT 1994: I:1, III:2', 'Technical Barriers to Trade (TBT): 2.1']."""
    by: dict[str, list[str]] = {}
    for code in filter(None, (codes or "").split("#")):
        ag, _, art = code.partition("_")
        name = d["agreement"].get(ag, ag)
        lst = by.setdefault(name, [])
        a = d["article"].get(art, art)
        if a and a not in lst:
            lst.append(a)
    return [f"{k}: {', '.join(v)}" if v else k for k, v in by.items()]


def _title(d: dict, c: dict) -> str:
    resp = "; ".join(_members(d, c.get("destination", ""), c.get("start_date", "")))
    title = _u(c.get("title", ""))
    return f"{c['code']}: {resp} — {title}" if resp else f"{c['code']}: {title}"


def _hay(d: dict, c: dict) -> str:
    """Lower-case text the search words are matched against."""
    return " ".join([
        c["code"], _u(c.get("title", "")), _u(c.get("short_title", "")),
        *_members(d, c.get("origin", ""), c.get("start_date", "")),
        *_members(d, c.get("destination", ""), c.get("start_date", "")),
        *(d["subject"].get(s, "") for s in c.get("subject", "").split("#")),
        *_agreements(d, c.get("agreement", "")),
    ]).lower()


def _case_url(n: int) -> str:
    return f"{BASE}/english/tratop_e/dispu_e/cases_e/ds{n}_e.htm"


def _dol_url(n: int) -> str:
    q = quote(f"(@meta_Symbol WT/DS{n}/*)", safe="()@/*")
    return (f"https://docs.wto.org/dol2fe/Pages/FE_Search/FE_S_S006.aspx?Query={q}"
            "&Language=ENGLISH&Context=FomerScriptedSearch&languageUIChanged=true")


def _num(ident: str) -> int:
    m = _ID.match(re.sub(r"\s+", " ", (ident or "").strip()))
    if not m:
        raise BadRequest("Give a WTO dispute number: DS600 (also accepted: 600, ds600, WT/DS600).")
    return int(m[1])


# --------------------------------------------------------------------------- #
# Case page
# --------------------------------------------------------------------------- #
def _parse_page(n: int, page: str) -> str:
    """The 'Summary of the dispute to date' section as markdown."""
    root = lhtml.fromstring(page)
    h2 = root.xpath("//h2[@id='summary']")
    if not h2:
        raise SourceError(f"Error (WTO): the page for DS{n} has no dispute summary section.", "payload")
    parts = []
    for el in h2[0].itersiblings():
        if el.tag == "script" or el.tag is lhtml.HtmlComment:
            continue
        if el.tag == "p" and el.xpath(".//script"):
            # "The summary below was up-to-date at <script>": the date comes from the arrays
            continue
        parts.append(lhtml.tostring(el, encoding="unicode", with_tail=True))
    body = "".join(parts)
    body = re.sub(r"(?is)<a[^>]*class=\"backToTop\"[^>]*>.*?</a>", "", body)
    # accordion header ("Summary of key findings") is an <h4> with a link; keep it as a heading
    return _http.html_to_md(body)


async def _page(n: int) -> str:
    if n in _page_cache:
        return _page_cache[n]
    r = await _http.get(_case_url(n))
    if r.status_code == 404 or "/error/" in str(r.url):
        raise NotFound(f"WTO has no page for DS{n}.")
    if r.status_code != 200:
        raise SourceError(_http.error("WTO", f"DS{n} failed", r.status_code), r.status_code)
    return _http.lru_put(_page_cache, n, _parse_page(n, _decode(r)), 32)


# --------------------------------------------------------------------------- #
class WTO(Jurisdiction):
    code = "wto"
    name = "WTO dispute settlement (World Trade Organization)"
    languages = ("en",)
    aliases = ("world trade organization", "world trade organisation", "wto disputes",
               "dispute settlement body", "dsb", "appellate body", "omc")
    sources = (
        Source(
            name="WTO dispute pages and dispute data files (www.wto.org)",
            url="https://www.wto.org/english/tratop_e/dispu_e/dispu_status_e.htm",
            covers=("caselaw",),
            licence=("© World Trade Organization. Unrestricted official documents and legal texts "
                     "are free for public use; other material may be reproduced for non-commercial "
                     "purposes with attribution, and the WTO must be informed. Commercial use "
                     "needs written permission."),
            commercial_use=False,
            ai_use=None,   # robots.txt: "Allow: /" for every agent; no AI/TDM clause in the terms
            auth="none",
            rate_limit=("unknown; 1 s spacing; data files cached in memory 6 h; "
                        "no 429 seen in ~20 requests (2026-11)"),
            terms_url="https://www.wto.org/english/info_e/copyrights_permissions_e.htm",
            warning=("WTO case summaries are Secretariat material: reuse is non-commercial with "
                     "attribution to the WTO, and the summaries are not official or exhaustive."),
        ),
    )
    caselaw_filters = {
        "complainant": "member name or WTO code that brought the dispute, e.g. Malaysia or MYS",
        "respondent": "member name or WTO code complained against, e.g. European Union or EEC",
        "third_party": "member name or WTO code among the third parties",
        "status": "text the current status must contain, e.g. 'adopted', 'consultations', 'appeal', 'settled'",
        "adopted": "true: a panel/AB report was adopted; false: none adopted",
        "date_from": "consultations requested on or after YYYY-MM-DD",
        "date_to": "consultations requested on or before YYYY-MM-DD",
    }
    min_interval = {HOST: 1.0}
    notes = ("WTO disputes DS1 onwards. Search covers number, title, short title, parties, subject and "
             "agreements cited. get_decision('DS600') gives the Secretariat's summary of the dispute "
             "(incl. key panel/AB findings); report texts on docs.wto.org are not fetched (robots). The agreement texts "
             "themselves (GATT 1994, Anti-Dumping Agreement, SCM, TRIPS ...) are not covered: read "
             "them at https://www.wto.org/english/docs_e/legal_e/legal_e.htm.")
    gaps = (
        ("WTO agreement texts (GATT 1994, Anti-Dumping Agreement etc.): no legislation search; "
         "official texts at https://www.wto.org/english/docs_e/legal_e/legal_e.htm"),
        ("Panel and Appellate Body report texts (docs.wto.org): robots.txt disallows ('Disallow: "
         "/')"),
        ("Submissions, arbitration awards and other WT/DS documents: on docs.wto.org, robots.txt "
         "disallows"),
        "French and Spanish versions of the dispute pages: not built yet (English only)",
        "GATT-era disputes before 1995: not researched yet",
    )
    samples = {
        "caselaw_query": "palm oil",
        "decision_id": "DS600",   # EU and Certain Member States — Palm Oil (Malaysia)
    }

    # ------------------------------------------------------------------ #
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        f = {k: str(v).strip() for k, v in (filters or {}).items() if str(v).strip()}
        for key in ("date_from", "date_to"):
            if key in f and not _DATE.match(f[key]):
                raise BadRequest(f"{key} must be YYYY-MM-DD.")
        adopted = f.get("adopted", "").lower()
        if adopted and adopted not in ("true", "false", "yes", "no"):
            raise BadRequest("adopted must be true or false.")
        d = await _load()

        def who(key: str, c: dict, want: str) -> bool:
            want = want.lower()
            codes = [x for x in c.get(key, "").split("#") if x]
            names = _members(d, c.get(key, ""), c.get("start_date", ""))
            return any(want == x.lower() for x in codes) or any(want in n.lower() for n in names)

        q = (query or "").strip()
        m = _ID.match(q)
        exact = int(m[1]) if m and re.search(r"(?i)ds|^\d+$", q) else None
        words = [w.strip('"').lower() for w in re.findall(r'"[^"]+"|\S+', q)]
        words = [w for w in words if w and w not in ("v", "v.", "vs", "vs.", "—", "-")]

        hits = []
        for n, c in d["cases"].items():
            start = _slash_date(c.get("start_date", ""))
            if "complainant" in f and not who("origin", c, f["complainant"]):
                continue
            if "respondent" in f and not who("destination", c, f["respondent"]):
                continue
            if "third_party" in f and not who("third_party", c, f["third_party"]):
                continue
            if "status" in f and f["status"].lower() not in _status_line(d, c).lower():
                continue
            if adopted and (c.get("reports_adopted", "").upper() == "TRUE") != (adopted in ("true", "yes")):
                continue
            if "date_from" in f and (not start or start < f["date_from"]):
                continue
            if "date_to" in f and (not start or start > f["date_to"]):
                continue
            if exact is not None:
                if n != exact:
                    continue
            elif words:
                hay = _hay(d, c)
                if not all(w in hay for w in words):
                    continue
            hits.append((n, c))
        hits.sort(key=lambda x: x[0], reverse=True)

        limit = max(1, min(int(limit), 50))
        page = max(1, int(page))
        items = []
        for n, c in hits[(page - 1) * limit: page * limit]:
            comp = "; ".join(_members(d, c.get("origin", ""), c.get("start_date", "")))
            short = _u(c.get("short_title", ""))
            snippet = "; ".join(x for x in (
                short, f"Complainant: {comp}" if comp else "", f"Status: {_status_line(d, c)}") if x)
            items.append(DecisionHit(
                id=c["code"], title=_title(d, c), court=COURT,
                date=_slash_date(c.get("start_date", "")), case_number=c["code"],
                snippet=snippet, url=_case_url(n)))
        note = ("Matches DS number, title, short title, parties, subject and agreements "
                "(all words); newest dispute first; date = consultations requested.")
        if not hits and words and exact is None:
            alls = [_hay(d, c) for c in d["cases"].values()]
            dead = [w for w in words if not any(w in h for h in alls)]
            if dead:
                note += (" No dispute contains: " + ", ".join(f"'{w}'" for w in dead)
                         + ". Words such as 'report' or 'Appellate Body' are not searchable; "
                           "search by title, party or subject words only.")
        if "appeal" in f.get("status", "").lower() or "appellate" in q.lower():
            note += (" Appellate Body reports are not indexed as separate decisions: status 'appeal' "
                     "lists disputes whose panel report is under appeal (pending), not AB rulings; "
                     "get_decision on a dispute gives the Secretariat summary of AB findings.")
        return Results(items=items, total=len(hits), note=note)

    # ------------------------------------------------------------------ #
    async def get_decision(self, id):
        n = _num(id)
        d = await _load()
        c = d["cases"].get(n)
        if c is None:
            raise NotFound(f"WTO has no dispute DS{n} (known: DS1–DS{max(d['cases'])}).")
        summary_md = await _page(n)
        start = c.get("start_date", "")
        comp = _members(d, c.get("origin", ""), start)
        resp = _members(d, c.get("destination", ""), start)
        third = _members(d, c.get("third_party", ""), start)
        subjects = [d["subject"].get(s, s) for s in c.get("subject", "").split("#") if s]
        cited = _agreements(d, c.get("agreement", ""))
        panel_cited = _agreements(d, c.get("pan_agree", ""))
        onepage = (f"{BASE}/english/tratop_e/dispu_e/cases_e/1pagesum_e/ds{n}sum_e.pdf"
                   if c.get("one_page_sum") == "Y" else "")
        short = _u(c.get("short_title", ""))

        facts = [
            ("Short title", short),
            ("Complainant", "; ".join(comp)),
            ("Respondent", "; ".join(resp)),
            ("Third parties", "; ".join(third)),
            ("Consultations requested", _slash_date(start)),
            ("Current status", _status_line(d, c)),
            ("Reports adopted", "yes" if c.get("reports_adopted", "").upper() == "TRUE" else "no"),
            ("Subject", ", ".join(subjects)),
            ("Agreements cited (consultations request)", "; ".join(cited)),
            ("Agreements cited (panel request)", "; ".join(panel_cited)),
            ("Summary up to date at", _slash_date(c.get("update_date", ""))),
            ("One-page summary of key findings (PDF)", onepage),
            ("Panel / Appellate Body reports and all documents (WTO Documents Online)", _dol_url(n)),
        ]
        title = _title(d, c)
        text = "\n".join([
            f"# {title}", "", "## Key facts",
            *(f"- **{k}:** {v}" for k, v in facts if v), "",
            "## Summary of the dispute to date",
            "Prepared by the WTO Secretariat under its own responsibility; for general information "
            "only and not intended to affect the rights and obligations of Members.", "",
            summary_md,
        ]).strip()
        statuses = _statuses(d, c)
        return Decision(
            id=c["code"],
            title=title,
            text=text,
            url=_case_url(n),
            court=COURT,
            date=_slash_date(start),
            case_number=c["code"],
            summary=_status_line(d, c),
            metadata={k: v for k, v in facts if v and k not in ("Consultations requested",)}
            | ({"Status date": statuses[-1][1]} if statuses and statuses[-1][1] else {}),
        )
