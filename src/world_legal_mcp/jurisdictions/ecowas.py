"""ECOWAS Community Court of Justice (CCJ, Abuja): decisions from the Court's own site,
courtecowas.org (WordPress + WPML, behind Cloudflare).

Verified 2026-11-05/06:
  * robots.txt: "User-agent: * / Allow: /", "Disallow: /wp-admin/" but
    "Allow: /wp-admin/admin-ajax.php". Cloudflare content signals "search=yes,
    ai-train=no, use=reference", stated as a condition of access and an EU DSM art. 4
    reservation; ai-input is not set ("neither grants nor restricts"). Named AI crawlers
    (ClaudeBot, GPTBot, CCBot ...) are disallowed; we send the project's own User-Agent.
  * Terms (/legal-notice/, /disclaimer-and-warning/): content "may be reused under specific
    conditions, provided that appropriate credit is given, and any changes are clearly
    indicated"; texts "may be reproduced, provided the source is acknowledged". Only the
    Reports of Cases / Official Journal versions are authentic. Nothing on automated access.
  * Decision list: the "Decisions of the Court" page loads its table with
    POST /wp-admin/admin-ajax.php action=ccj_cases_pagination&page=N&dec_type=&sort_by=
    -> {"data": {"table_data": "<tr>...", "pagination": "..."}}; 10 rows per page, no
    page-size or text-search parameter. Columns: title, decision number
    (ECW/CCJ/JUD/06/08), year filed, nature, type, decision date (dd/mm/yyyy), PDF links
    per language (ENG/FR/PT). 208 rows (21 pages) on 2026-11-06. The list is fetched at
    most once per _TTL and kept in memory (no disk cache).
  * The "Search Cases" page (GET /pending-cases-and-decisions/search-cases/?case_num=)
    matches only an exact suit number, judgment number or full title. Used here only to
    resolve a suit number (ECW/CCJ/APP/08/08) to its judgment number.
  * The WP REST API (/wp-json/wp/v2/ccj-cases) has titles and taxonomies but no decision
    number, date or file; not used. The per-case pages (/ccj-cases/<slug>/) are empty.
  * Decisions are PDFs under /wp-content/uploads/. About half are scans without a text
    layer (no OCR here): get_decision then raises SourceError with the link.

Ids: the decision number exactly as the list gives it ("ECW/CCJ/JUD/19/15"; the list has
typos such as "ECW/CCJ/.JUD/55/26", matched loosely). The list repeats ~20 decisions;
repeats are merged. Three numbers are shared by a judgment and a ruling: the ruling's id is
"ECW/CCJ/JUD/01/26 (Ruling)". Add "#FR" / "#PT" for another language version.
"""
from __future__ import annotations

import asyncio
import io
import re
import time
import unicodedata

from lxml import html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, Results

HOST = "courtecowas.org"
ROOT = f"https://{HOST}"
AJAX_URL = f"{ROOT}/wp-admin/admin-ajax.php"
LIST_PAGE = f"{ROOT}/pending-cases-and-decisions/decisions-of-the-court/"
SEARCH_PAGE = f"{ROOT}/pending-cases-and-decisions/search-cases/"
COURT = "ECOWAS Community Court of Justice"
_TTL = 12 * 3600
_MAX_PAGES = 60

_NUMBER = re.compile(r"^ECW\s*/\s*CCJ\b", re.I)
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_LANGS = {"ENG": "ENG", "EN": "ENG", "FR": "FR", "FRE": "FR", "PT": "PT", "POR": "PT"}
_TYPES = ("judgement", "opinion", "order", "ruling")

_list_cache: dict = {}          # {"t": monotonic time, "rows": [...]}
_lock = asyncio.Lock()

# Official Law Reports (CCJELR), English, as hosted by the Court (checked 2026-11-10 via the
# WP media search: 2004-2009 in one volume, then one volume per year to 2017; no later
# volume online). Volume label -> PDF.
REPORTS_URL = f"{ROOT}/wp-content/uploads/2024/09/CCJE-LAW-REPORT-{{}}-ENGLISH.pdf"
REPORT_VOLUMES = ("2004-2009",) + tuple(str(y) for y in range(2010, 2018))
_vol_cache: dict = {}
_vol_lock = asyncio.Lock()
_FOOTER = re.compile(r"^Community Court of Justice, ECOW\s*AS\b.*CCJELR\)?$", re.I)
_TOC_ENTRY = re.compile(r"^(\d{1,2})\.\s*(ECW\b.*?)\s*(?::\s*|\s)(\d{1,3})$")  # page after ':' or a space, never the tail of a number
_BODY_NO = re.compile(r"^(?:JUDG[E]?MENT|RULING|INTERIM RULING|ADVISORY OPINION|ORDER|OPINION)\s*"
                      r"N\s*[°ºoO]?\s*\.?\s*:?\s*(ECW\s*/.*)$", re.I)


def _fold(s: str) -> str:
    """Lower-case, accents stripped ('République' ~ 'republique')."""
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def _pad_no(s: str) -> str:
    """Zero-pad one-digit number segments ('JUD/9/20' -> 'JUD/09/20'), as the Court writes them."""
    return re.sub(r"(?<=/)(\d)(?=/|$|[^\d])", r"0\1", s)


def _key(number: str) -> str:
    """Loose form of a decision/suit number for matching: 'ECW/CCJ/.JUD/55/26' -> 'ECWCCJJUD5526'."""
    return re.sub(r"[^A-Z0-9]", "", _pad_no(_fold(number)).upper())


def _parse_rows(table_html: str) -> list[dict]:
    root = lhtml.fromstring(f"<table>{table_html}</table>")
    rows = []
    for tr in root.xpath("//tr[td]"):
        tds = tr.xpath("./td")
        if len(tds) < 8:
            continue
        cells = [_http.clean(td.text_content()) for td in tds]
        files = {}
        for a in tds[7].xpath(".//a[@onclick]"):
            m = re.search(r"downloadFile\('([^']+)'", a.get("onclick"))
            lang = _http.clean(a.text_content()).upper()
            if m and lang:
                files.setdefault(_LANGS.get(lang, lang), m[1])
        if not cells[2]:
            continue
        rows.append({"title": cells[1], "number": cells[2], "year": cells[3],
                     "nature": cells[4], "type": cells[5],
                     "date": _http.iso_date(cells[6]), "files": files})
    return rows


async def _list_page(n: int) -> tuple[list[dict], int]:
    r = await _http.post(AJAX_URL, data={"action": "ccj_cases_pagination", "dec_type": "",
                                         "page": str(n), "sort_by": ""})
    if r.status_code != 200:
        raise SourceError(_http.error("ECOWAS Court", "decision list failed", r.status_code),
                          r.status_code)
    try:
        data = r.json()["data"]
        rows = _parse_rows(data["table_data"])
        last = max([int(p) for p in re.findall(r'data-page="(\d+)"', data["pagination"])] + [n])
    except (ValueError, KeyError, TypeError):
        raise SourceError("Error (ECOWAS Court): unexpected decision-list payload.",
                          r.status_code) from None
    return rows, last


def _merge(rows: list[dict]) -> list[dict]:
    """The list repeats many decisions (same number and type, other upload): keep the first
    listing and add the language files of the repeats. A few numbers are shared by two
    decisions of different types (a judgment and a ruling); the judgment keeps the plain
    number as id and the other gets 'ECW/CCJ/JUD/01/26 (Ruling)'."""
    groups: dict = {}
    for r in rows:
        g = groups.setdefault((_key(r["number"]), _fold(r["type"])), r)
        if g is not r:
            for lang, url in r["files"].items():
                g["files"].setdefault(lang, url)
    out = list(groups.values())
    by_num: dict = {}
    for r in out:
        by_num.setdefault(_key(r["number"]), []).append(r)
    for same in by_num.values():
        same.sort(key=lambda r: _fold(r["type"]) != "judgement")
        for i, r in enumerate(same):
            r["id"] = r["number"] if i == 0 else f"{r['number']} ({r['type'] or 'other'})"
    return out


async def _decisions() -> list[dict]:
    async with _lock:
        if _list_cache and time.monotonic() - _list_cache["t"] < _TTL:
            return _list_cache["rows"]
        rows, last = await _list_page(1)
        n = 1
        while n < min(last, _MAX_PAGES):
            n += 1
            more, last = await _list_page(n)
            if not more:
                break
            rows += more
        rows = _merge(rows)
        _list_cache.update(t=time.monotonic(), rows=rows)
        return rows


async def _suit_to_numbers(suit: str) -> list[str]:
    """Judgment numbers the Court's exact-match Search Cases page gives for a suit number."""
    r = await _http.get(SEARCH_PAGE, params={"case_num": suit, "date_from": "", "date_to": ""})
    if r.status_code != 200:
        raise SourceError(_http.error("ECOWAS Court", "case search failed", r.status_code),
                          r.status_code)
    root = lhtml.fromstring(r.text)
    out = []
    for tr in root.xpath("//main//table//tr[count(td)>=5]"):
        cells = [_http.clean(td.text_content()) for td in tr.xpath("./td")]
        if _NUMBER.match(cells[3]):
            out.append(cells[3])
    return out


def _langs(row: dict) -> str:
    return ", ".join(row["files"]) or "no file"


_SCAN: dict = {}        # PDF url -> True (scan, no text layer) / False (has text)
_SCAN_CHECK_MAX = 5     # each check downloads the whole PDF: only for the first hits of a page


async def _is_scan(row: dict):
    """True/False whether the decision's first PDF is a scan; None when it cannot be checked."""
    url = _file_url(row, "")
    if not url:
        return None
    if url not in _SCAN:
        try:
            r = await _http.get(url)
            if r.status_code != 200 or not r.content.startswith(b"%PDF"):
                return None
            text = await asyncio.to_thread(_http.pdf_text, r.content)
        except Exception:
            return None
        _http.lru_put(_SCAN, url, len(text) < 200, 200)
    return _SCAN[url]


def _hit(row: dict, scan=None) -> DecisionHit:
    status = ("scan, no text layer: get_decision gives the link only" if scan else "text layer present"
              ) if scan is not None else "scan or text not checked; about half of the PDFs are scans without text"
    bits = [b for b in (row["type"], row["nature"] and f"{row['nature']}",
                        row["year"] and f"filed {row['year']}", f"PDF: {_langs(row)} ({status})") if b]
    return DecisionHit(id=row["id"], title=row["title"] or f"{COURT} {row['number']}",
                       court=COURT, date=row["date"], case_number=row["number"],
                       snippet="; ".join(bits), url=_file_url(row, "") or LIST_PAGE)


def _file_url(row: dict, lang: str) -> str:
    files = row["files"]
    if lang:
        return files.get(lang, "")
    return files.get("ENG") or next(iter(files.values()), "")


# --------------------------------------------------------------------------- #
# Law Reports (CCJELR) volumes
# --------------------------------------------------------------------------- #
def _norm_no(s: str) -> str:
    """'ECW/CCJ/ADV .OPN/01/05' -> 'ECW/CCJ/ADV.OPN/01/05'; 'ECW/JUD/01/05' -> 'ECW/CCJ/JUD/01/05'."""
    s = re.sub(r"\s+", "", s).rstrip(".,;:")
    return _pad_no(re.sub(r"^ECW/(?!CCJ/)", "ECW/CCJ/", s, flags=re.I))


def _volume_for(number: str) -> list[str]:
    """Volumes that may report a decision: its year's volume, then the next one."""
    m = re.search(r"/(\d{2})\s*$", number)
    if not m:
        return []
    out = []
    for y in (2000 + int(m[1]), 2001 + int(m[1])):
        v = "2004-2009" if 2004 <= y <= 2009 else str(y)
        if v in REPORT_VOLUMES and v not in out:
            out.append(v)
    return out


def _parse_volume(vol: str, data: bytes) -> dict:
    from pypdf import PdfReader
    pages = []
    for p in PdfReader(io.BytesIO(data)).pages:
        lines = [_http.clean(ln) for ln in (p.extract_text() or "").splitlines()]
        lines = [ln for ln in lines if ln]
        while lines and (_FOOTER.match(lines[-1]) or re.fullmatch(r"\d{1,3}|[ivxlc]{1,6}", lines[-1])):
            lines.pop()
        # some pages extract with the page number and running footer first
        if len(lines) > 1 and _FOOTER.match(lines[1]) and re.fullmatch(r"\d{1,3}|[ivxlc]{1,6}", lines[0]):
            lines = lines[2:]
        elif lines and _FOOTER.match(lines[0]):
            lines = lines[1:]
        pages.append(lines)
    # Printed page 1 is where the first reported decision starts (its "SUIT N°" heading);
    # everything before it is front matter holding the table of contents.
    raw_toc, first = [], None
    for i, lines in enumerate(pages):
        if any(re.match(r"^SUIT\s*N", ln, re.I) or _BODY_NO.match(ln) for ln in lines):
            first = i
            break
        raw_toc += lines
    if first is None:
        raise SourceError(f"Error (ECOWAS Court): Law Report {vol} has no readable decisions.")
    toc = []                     # join wrapped entry lines, then read "N. numbers: page"
    for ln in raw_toc:
        if toc and re.match(r"^\d{1,2}\.\s*ECW\b", toc[-1]) and not _TOC_ENTRY.match(toc[-1]) \
                and not re.match(r"^\d{1,2}\.\s*ECW\b", ln):
            toc[-1] += " " + ln
        else:
            toc.append(ln)
    entries = []
    for ln in toc:
        m = _TOC_ENTRY.match(ln)
        if not m:
            if entries and not entries[-1]["done"] and not re.match(
                    r"^(Table of Contents|Foreword|Judges|JUDG(E)?MENTS AND|Community Court)", ln, re.I):
                entries[-1]["title"] += " " + ln
            elif entries:
                entries[-1]["done"] = True
            continue
        nums = [_norm_no(x[x.index("ECW"):].rstrip(") ") if "ECW" in x else x)
                for x in re.split(r"\s+[-–]\s*|–|-(?=RULING)", m[2]) if x.strip()]
        entries.append({"suit": nums[0] if len(nums) > 1 else "", "toc_no": nums[-1],
                        "start": int(m[3]), "title": "", "done": False})
    out = []
    for k, e in enumerate(entries):
        a = first + e["start"] - 1
        b = first + entries[k + 1]["start"] - 1 if k + 1 < len(entries) else len(pages)
        body = pages[a:b]
        head = [ln for lines in body[:2] for ln in lines]
        no = next((_norm_no(m[1]) for m in map(_BODY_NO.match, head) if m), "")
        date = ""
        for ln in head[:12]:
            d = re.search(r"(\d{1,2})\s*(?:ST|ND|RD|TH)?\s*(?:DAY\s+)?(?:OF\s+)?([A-Z]+),?\s+(\d{4})", ln, re.I)
            if d and (date := _http.en_date(f"{d[2]} {d[1]}, {d[3]}")):
                break
        out.append({"id": no or e["toc_no"], "aliases": {_key(no), _key(e["toc_no"])} - {""},
                    "numbers": sorted({no, e["toc_no"]} - {""}),
                    "suit": e["suit"], "title": _http.clean(e["title"]).rstrip(".") or f"{COURT} {no}",
                    "date": date, "page": e["start"], "pdf_page": a + 1,
                    "text": "\n\n".join("\n".join(lines) for lines in body if lines)})
    # A few numbers are printed twice in one volume (two decisions, or a misprint): those
    # decisions, and any filed in a volume their number's year does not point to, take
    # their Law Report citation as id, e.g. "(2010) CCJELR 213".
    count: dict = {}
    for c in out:
        count[_key(c["id"])] = count.get(_key(c["id"]), 0) + 1
    for c in out:
        if count[_key(c["id"])] > 1 or vol not in _volume_for(c["id"]):
            c["id"] = f"({vol}) CCJELR {c['page']}"
    return {"vol": vol, "url": REPORTS_URL.format(vol), "cases": out}


async def _volume(vol: str) -> dict:
    async with _vol_lock:
        if vol in _vol_cache:
            return _vol_cache[vol]
        url = REPORTS_URL.format(vol)
        r = await _http.get(url, timeout=120)
        if r.status_code != 200 or not r.content.startswith(b"%PDF"):
            raise SourceError(_http.error("ECOWAS Court", f"Law Report {vol} failed", r.status_code),
                              r.status_code)
        parsed = await asyncio.to_thread(_parse_volume, vol, r.content)
        return _http.lru_put(_vol_cache, vol, parsed, 2)


def _cite(vol: dict, c: dict) -> str:
    return f"({vol['vol']}) CCJELR {c['page']}"


def _report_hit(vol: dict, c: dict) -> DecisionHit:
    return DecisionHit(id=c["id"], title=c["title"], court=COURT, date=c["date"], case_number=c["id"],
                       snippet=_cite(vol, c) + (f"; suit {c['suit']}" if c["suit"] else ""),
                       url=f"{vol['url']}#page={c['pdf_page']}")


_CITE = re.compile(r"^\(\s*(\d{4})(?:\s*-\s*(\d{4}))?\s*\)\s*CCJELR\s*(\d{1,3})$", re.I)


async def _report_case(ident: str) -> tuple[dict, dict] | None:
    """A reported decision by Law Report citation ('(2010) CCJELR 213') or decision number."""
    m = _CITE.match(ident)
    if m:
        v = f"{m[1]}-{m[2]}" if m[2] else m[1]
        if v not in REPORT_VOLUMES:
            raise NotFound(f"No ECOWAS Law Report volume ({v}) online; volumes: "
                           f"{', '.join(REPORT_VOLUMES)}.")
        vol = await _volume(v)
        c = next((c for c in vol["cases"] if c["page"] == int(m[3])), None)
        return (vol, c) if c else None
    k = _key(ident)
    for v in _volume_for(ident):
        vol = await _volume(v)
        same = [c for c in vol["cases"] if k in c["aliases"] or _key(c["id"]) == k]
        if len(same) > 1:
            raise BadRequest(f"{ident} is printed for {len(same)} decisions in the ({v}) Law Report; "
                             "use one of: " + "; ".join(f"{c['id']} ({c['title']})" for c in same))
        if same:
            return vol, same[0]
    return None


# --------------------------------------------------------------------------- #
class ECOWAS(Jurisdiction):
    code = "ecowas"
    name = "ECOWAS Community Court of Justice"
    languages = ("en", "fr", "pt")
    aliases = ("ecowas court", "community court of justice", "cour de justice de la cedeao",
               "cedeao", "tribunal de justiça da cedeao", "economic community of west african states")
    sources = (
        Source(
            name="ECOWAS Community Court of Justice website (courtecowas.org)",
            url=LIST_PAGE,
            covers=("caselaw",),
            licence=("© ECOWAS Community Court of Justice; reuse allowed with credit and changes "
                     "indicated (Legal Notice); robots.txt Content-Signal search=yes, ai-train=no, "
                     "use=reference"),
            commercial_use=None,   # terms allow reuse with credit; silent on commercial use
            ai_use=False,          # robots.txt content signal ai-train=no (ai-input not set)
            auth="none",
            rate_limit=("unknown; 1 s spacing, decision list (21 requests) cached in memory 12 h; "
                        "no 429 seen in ~110 requests (2026-11-06)"),
            terms_url=f"{ROOT}/legal-notice/",
            warning=("Credit the ECOWAS Court of Justice when reusing; only the Reports of Cases / "
                     "Official Journal texts are authentic; the site reserves its content against AI "
                     "training (robots.txt ai-train=no, use=reference)."),
        ),
        Source(
            name="ECOWAS Court Law Reports (CCJELR), English volumes 2004-2017 (courtecowas.org)",
            url=REPORTS_URL.format("2010"),
            covers=("caselaw",),
            licence=("© ECOWAS Community Court of Justice; reuse allowed with credit and changes "
                     "indicated (Legal Notice); robots.txt Content-Signal search=yes, ai-train=no, "
                     "use=reference"),
            commercial_use=None,
            ai_use=False,
            auth="none",
            rate_limit=("same host as the decision list (1 s spacing); one 3-7 MB PDF per volume, "
                        "2 volumes kept in memory; no 429 seen (2026-11-10)"),
            terms_url=f"{ROOT}/legal-notice/",
            warning=("Credit the ECOWAS Court of Justice when reusing; the site reserves its content "
                     "against AI training (robots.txt ai-train=no, use=reference)."),
            probe={"caselaw_query": "Habre", "decision_id": "ECW/CCJ/JUD/06/10",
                   "filters": {"report_year": "2010"}},
        ),
    )
    caselaw_filters = {
        "type": "judgement, opinion, order or ruling",
        "nature": "nature of case as the Court lists it, e.g. Human Rights, Trade Disputes",
        "year_filed": "year the case was filed, e.g. 2019",
        "date_from": "decided on or after YYYY-MM-DD",
        "date_to": "decided on or before YYYY-MM-DD",
        "report_year": ("search one official Law Report volume (full text, authentic) instead of the "
                        "online list: 2004-2009 or a year 2010-2017"),
    }
    min_interval = {HOST: 1.0}
    notes = ("ECOWAS Court of Justice decisions: the official Law Reports 2004-2017 (English, full "
             "text; search with report_year) and the Court's online list (about 210, mostly 2015 "
             "onwards, English with some French/Portuguese; about half are scans without text).")
    gaps = (
        ("Text of decisions from 2018 on that are only scans (about half of the online list): no text "
         "layer (no OCR); Law Reports after 2017 are not online (2021-2024 volumes in preparation, "
         "Court news 2025)"),
        ("Decisions 2004-2017 not selected for the Law Reports and missing from the online list: not "
         "published online"),
        "Case files and pending-case documents: the Court's per-case pages are empty (not published online)",
        ("ECOWAS treaties, protocols and Community acts: not available here (no legislation source). "
         "The Court's Basic Texts page, https://courtecowas.org/about_us/basic-text/, links the "
         "Revised ECOWAS Treaty, the Court Protocol A/P1/7/91 and Supplementary Protocol A/SP.1/01/05 "
         "as PDFs; the Community acts are in the ECOWAS Official Journal at https://www.ecowas.int"),
    )
    samples = {
        "caselaw_query": "Togo",
        "decision_id": "ECW/CCJ/JUD/19/15",   # Hope Democratic Party & Anor v. Nigeria & 5 Ors
    }

    # ------------------------------------------------------------------ #
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        f = {k: str(v).strip() for k, v in (filters or {}).items() if str(v).strip()}
        dtype = f.get("type", "").lower().replace("judgment", "judgement")
        if dtype and dtype not in _TYPES:
            raise BadRequest("type must be judgement, opinion, order or ruling.")
        if "year_filed" in f and not re.fullmatch(r"\d{4}", f["year_filed"]):
            raise BadRequest("year_filed must be a year such as 2019.")
        for k in ("date_from", "date_to"):
            if k in f and not _DATE.match(f[k]):
                raise BadRequest(f"{k} must be YYYY-MM-DD.")
        nature = _fold(f.get("nature", ""))
        q = (query or "").strip()
        if "report_year" in f:
            return await self._search_reports(q, f, dtype, limit, page)

        rows = await _decisions()
        wanted = None                       # set of _key()s when the query is a number
        if _NUMBER.match(q):
            k = _key(q)
            keys = {_key(r["number"]) for r in rows}
            if k in keys:
                wanted = {k}
            elif "APP" in k:                # a suit number: ask the Court's exact search
                wanted = {_key(n) for n in await _suit_to_numbers(q)}
            if not wanted:
                wanted = {x for x in keys if k in x}
        words = [w for w in (_fold(w.strip('"')) for w in re.findall(r'"[^"]+"|\S+', q))
                 if w and w not in ("v", "v.", "vs", "vs.")]

        hits = []
        for r in rows:
            if dtype and _fold(r["type"]) != dtype:
                continue
            if nature and nature not in _fold(r["nature"]):
                continue
            if "year_filed" in f and r["year"] != f["year_filed"]:
                continue
            if "date_from" in f and (not r["date"] or r["date"] < f["date_from"]):
                continue
            if "date_to" in f and (not r["date"] or r["date"] > f["date_to"]):
                continue
            if wanted is not None:
                if _key(r["number"]) not in wanted:
                    continue
            elif words:
                hay = _fold(f"{r['title']} {r['number']}")
                if not all(w in hay for w in words):
                    continue
            hits.append(r)
        hits.sort(key=lambda r: r["date"], reverse=True)
        if not hits and q and (_CITE.match(q) or (_NUMBER.match(q) and _volume_for(q))):
            found = await _report_case(_norm_no(q) if _NUMBER.match(q) else q)
            if found:
                return Results(items=[_report_hit(*found)], total=1,
                               note=f"Found in the official Law Report {_cite(*found)}.")

        if not hits:
            raise NotFound(
                f"0 decisions in the Court's online list for {q!r} with these filters. The list "
                "search matches case title and decision number only (all words), not subject matter: "
                "for a topic use the nature filter (e.g. Human Rights; query 'v' lists all). Decisions "
                "of 2004-2017 (e.g. Media Foundation for West Africa v Gambia, 2012; Haruna Warkani, "
                "2012) are mostly not in this list: search them with report_year (2004-2009, or 2010 "
                "to 2017) and the party name.")
        limit = max(1, min(int(limit), 50))
        page = max(1, int(page))
        shown = hits[(page - 1) * limit: page * limit]
        scans = await asyncio.gather(*(_is_scan(r) for r in shown[:_SCAN_CHECK_MAX]))
        scans = list(scans) + [None] * (len(shown) - len(scans))
        return Results(items=[_hit(r, sc) for r, sc in zip(shown, scans)],
                       total=len(hits),
                       note=("Matches case title and decision number only (all words, accents ignored), "
                             "not subject matter: for a topic use the nature filter (e.g. Human Rights; "
                             "query 'v' lists all) or report_year for full-text search of the 2004-2017 "
                             "Law Reports, which hold older decisions (e.g. 2012) that are not in this "
                             "list. Newest first; date = decision date as the Court lists it. About half "
                             "of the PDFs are scans without text: each of the first 5 hits says whether its PDF is "
                             "a scan; for the rest get_decision tells."))

    async def _search_reports(self, q, f, dtype, limit, page):
        v = re.sub(r"\s+", "", f["report_year"])
        if v in [str(y) for y in range(2004, 2010)]:
            v = "2004-2009"
        if v not in REPORT_VOLUMES:
            raise BadRequest("report_year must be 2004-2009 (one volume) or a year 2010-2017.")
        vol = await _volume(v)
        words = [w for w in (_fold(w.strip('"')) for w in re.findall(r'"[^"]+"|\S+', q))
                 if w and w not in ("v", "v.", "vs", "vs.")]
        kq = _key(q) if _NUMBER.match(q) else ""
        hits = []
        for c in vol["cases"]:
            kind = {"JUD": "judgement", "JUG": "judgement", "RUL": "ruling", "ADV": "opinion"}.get(
                (re.search(r"/(JUD|JUG|RUL|ADV)", " ".join(c["numbers"])) or [""] * 2)[1], "")
            if dtype and kind and kind != dtype:
                continue
            if "date_from" in f and (not c["date"] or c["date"] < f["date_from"]):
                continue
            if "date_to" in f and (not c["date"] or c["date"] > f["date_to"]):
                continue
            if kq:
                if not any(kq in a for a in c["aliases"] | {_key(c["suit"])}):
                    continue
            elif words:
                hay = _fold(f"{c['title']} {c['id']} {c['suit']} {c['text']}")
                if not all(w in hay for w in words):
                    continue
            hits.append(c)
        limit = max(1, min(int(limit), 50))
        page = max(1, int(page))
        return Results(items=[_report_hit(vol, c) for c in hits[(page - 1) * limit: page * limit]],
                       total=len(hits),
                       note=(f"Law Report ({v}) CCJELR, in report order; full-text match (all words, "
                             "accents ignored). Reported decisions only; English."))

    # ------------------------------------------------------------------ #
    async def get_decision(self, id):
        ident = (id or "").strip()
        if _CITE.match(ident):
            found = await _report_case(ident)
            if not found:
                m = _CITE.match(ident)
                v = f"{m[1]}-{m[2]}" if m[2] else m[1]
                vol = await _volume(v)
                near = [c for c in vol["cases"] if c["page"] >= int(m[3])][:2]
                raise NotFound(
                    f"No decision starts at {ident}: the number after CCJELR is the page where a "
                    "reported decision starts, not a case number" +
                    (("; the next ones start at " + "; ".join(f"{_cite(vol, c)} ({c['title'][:60]})"
                                                              for c in near)) if near else "") +
                    ". To find a case, search with report_year and the party name.")
            return self._report_decision(*found)
        number, _, lang = ident.partition("#")
        number, lang = number.strip(), lang.strip().upper()
        if not lang and _NUMBER.match(number) and not number.endswith(")") and _volume_for(number):
            found = await _report_case(_norm_no(number))
            if found:
                return self._report_decision(*found)
        if not _NUMBER.match(number):
            raise BadRequest("Give an ECOWAS Court decision number such as ECW/CCJ/JUD/19/15, "
                             "optionally with a language: ECW/CCJ/JUD/45/26#PT, or a Law Report "
                             "citation such as (2010) CCJELR 213.")
        if lang and lang not in _LANGS:
            raise BadRequest("Language must be ENG, FR or PT, e.g. ECW/CCJ/JUD/45/26#FR.")
        lang = _LANGS.get(lang, "")
        m = re.match(r"^(.*?)\s*\(([^)]*)\)$", number)
        number, qual = (m[1], _fold(m[2])) if m else (number, "")
        k = _key(number)
        same = [r for r in await _decisions() if _key(r["number"]) == k]
        row = next((r for r in same if _fold(r["type"] or "other") == qual), None) if qual else \
            next((r for r in same if r["id"] == r["number"]), None)
        if row is None:
            raise NotFound(f"The ECOWAS Court site lists no decision {number}. Decision numbers "
                           "look like ECW/CCJ/JUD/19/15 (search by party name to find one).")
        url = _file_url(row, lang)
        if not url:
            raise NotFound(f"{row['number']} has no {lang or 'downloadable'} version on the Court's "
                           f"site (available: {_langs(row)}).")
        r = await _http.get(url)
        if r.status_code != 200:
            raise SourceError(_http.error("ECOWAS Court", f"decision {row['number']} failed",
                                          r.status_code), r.status_code)
        if not r.content.startswith(b"%PDF"):
            raise SourceError(f"Error (ECOWAS Court): {row['number']} is not a PDF; open it at {url}.")
        text = _http.pdf_text(r.content)
        if len(text) < 200:
            raise SourceError(f"Error (ECOWAS Court): {row['number']} ({row['title']}, "
                              f"{row['date'] or 'undated'}) is a scanned PDF without a text layer "
                              f"(no OCR here); read it at {url}.", "pdf")
        used = lang or next(lg for lg, u in row["files"].items() if u == url)
        meta = {"Decision number": row["number"], "Type": row["type"], "Nature of case": row["nature"],
                "Year filed": row["year"], "Language": used,
                "Other versions": ", ".join(f"{row['id']}#{lg}" for lg in row["files"] if lg != used)}
        return Decision(
            id=row["id"] if not lang else f"{row['id']}#{lang}",
            title=row["title"] or f"{COURT} {row['number']}",
            text=text,
            url=url,
            court=COURT,
            date=row["date"],
            case_number=row["number"],
            metadata={k: v for k, v in meta.items() if v},
        )

    @staticmethod
    def _report_decision(vol: dict, c: dict) -> Decision:
        meta = {"Law Report": _cite(vol, c), "Decision number": c["id"] if _NUMBER.match(c["id"]) else
                " / ".join(c["numbers"]), "Suit number": c["suit"], "Language": "ENG",
                "Note": "Reported text as published in the Court's official Law Report volume "
                        "(includes the report's summary where it gives one)."}
        return Decision(id=c["id"], title=c["title"], text=c["text"],
                        url=f"{vol['url']}#page={c['pdf_page']}", court=COURT, date=c["date"],
                        case_number=c["id"] if _NUMBER.match(c["id"]) else c["suit"],
                        metadata={k: v for k, v in meta.items() if v})
