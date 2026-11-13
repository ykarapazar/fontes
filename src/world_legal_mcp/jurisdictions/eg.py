"""Egypt: Supreme Constitutional Court (المحكمة الدستورية العليا) judgments, full text, Arabic.

Gotchas this code encodes (verified 2026-11-06 from a UK IP):
  * Source: the Court's own portal www.sccourt.gov.eg/newportal (Angular SPA). It reads a
    JSON API at /DjangoPortal/api/... (base address from newportal/assets/config/
    environment.json). No key, no login for judgments. www.sccourt.gov.eg/robots.txt is a
    404 (no rules); the portal has no terms page (its "privacy" and "disclaimer" footer
    links have no target); footer says only "جميع الحقوق محفوظة © 2025".
  * Search: POST /api/RulesInsert/search-in-rules-based-on-request-es (what the portal's
    "البحث الحر" uses). It ignores pageNo/pageSize and returns at most ~25 rulings, newest
    first for text queries; we page over that list locally. Filters that work:
    ruleNumber (int), courtYear ([judicial year]), ruleSubjectTypeCode ([type code]),
    ruleDateFrom/To (YYYY-MM-DD) - but dates combined with ruleText always return 0, so
    that combination is refused. The text index looks partial: words found in old
    judgments' text do not always hit; the exact number lookup (number + judicial year
    + type) reaches judgments back to the 1970s-80s.
  * Id: the portal's caseId (its own record id, used by get-rule-details-by-case-id).
    Also accepted: the Court's citation "الدعوى 37 لسنة 9 قضائية دستورية", "37/9",
    "37/9 دستورية" or "37/9/1" (type code); these are looked up by number.
  * Text: details JSON gives htmlFIleBase64 = a public static HTML page
    /DjangoPortalResources/Rules_Html/{ruleId}_{year}_{number}_{type}_2.html; the
    judgment is <div id='wrap'>. The details JSON has no ruling date, so get_decision
    also runs the number lookup to get it.
  * Unknown caseId: details return data=[]; a non-numeric one returns HTTP 500.
  * TLS: the server offers only TLS 1.2 with RSA key exchange (AES256-GCM-SHA384).
    Python's default SSL context excludes that cipher, so the handshake fails
    (SSLV3_ALERT_HANDSHAKE_FAILURE). _http's shared client sets ctx.set_ciphers("DEFAULT")
    for this reason, so the handshake works.
  * Not used:
      - cc.gov.eg (محكمة النقض, Court of Cassation): its usage policy (May 2026) requires a
        paid personal subscription and says "يُحظر الاستخراج الآلى أو الجَمْعى لمحتوى الموقع
        بأى وسيلة — برامج الزحف أو النصوص البرمجية أو الاستدعاء المتكرّر المبرمَج";
        robots.txt also disallows /legal/GetJudgment*.
      - Legislation: no free official source. Al-Amiria (Official Gazette publisher,
        alamiria.com) shows a few featured texts; its archive needs a paid account.
"""
from __future__ import annotations

import datetime
import re

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, Results

HOST = "https://www.sccourt.gov.eg"
API = f"{HOST}/DjangoPortal/api"
SEARCH = f"{API}/RulesInsert/search-in-rules-based-on-request-es"
DETAILS = f"{API}/RulesInsert/get-rule-details-by-case-id"
COURT = "المحكمة الدستورية العليا"
MAX_HITS = 25  # the source returns at most this many per query
# ruleSubjectTypeCode -> name, from /api/RulesSubjectTypeLkp/get-all-rules-subject-type-lkp
TYPES = {1: "دستورية", 2: "تفسير تشريعى", 3: "تنازع", 4: "رد", 5: "طلبات أعضاء", 6: "منازعة تنفيذ",
         7: "مخاصمة", 8: "تحكيم", 9: "بطلان", 10: "رقابة دستورية سابقة", 11: "اغفال طلبات",
         13: "تظلم من امر تقدير رسوم", 14: "تفسير احكام"}
_NORM = str.maketrans("أإآىةيـ", "اااايه ")
_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
_CASEINFO = re.compile(r"الدعوى\s+(\d+)\s+لسنة\s+(\d+)\s*(?:قضائية)?\s*[-–«\"]*\s*([^-–\"»]+)")
_NO_MATCH = "عدد النتائج:0"
_cache: dict[str, Decision] = {}


def _type_code(s) -> int:
    """'1', 'دستورية', 'منازعة تنفيذ' -> type code; BadRequest otherwise."""
    s = _http.clean(s).translate(_DIGITS).strip('«»"\' ')
    if s.isdigit() and int(s) in TYPES:
        return int(s)
    key = s.translate(_NORM).replace(" ", "")
    for code, name in TYPES.items():
        if name.translate(_NORM).replace(" ", "") == key:
            return code
    raise BadRequest("type must be a Supreme Constitutional Court case type: "
                     + ", ".join(f"{c} = {n}" for c, n in TYPES.items()) + f"; got {s!r}.")


def _parse_ref(s: str) -> tuple[int, int, int] | None:
    """Court citation -> (number, judicial year, type code) or None.
    'الدعوى 37 لسنة 9 قضائية دستورية', '37/9', '37/9 دستورية', '37/9/1'."""
    s = _http.clean(s).translate(_DIGITS)
    m = re.fullmatch(r"(?:الدعوى|القضية|دعوى)?\s*(?:رقم\s*)?(\d{1,5})\s*(?:/|لسنة)\s*(\d{1,3})\s*"
                     r"(?:قضائية|ق\.?)?\s*[/\-]?\s*(.*)", s)
    if not m:
        return None
    rest = m[3].strip(' «»"\'')
    return int(m[1]), int(m[2]), _type_code(rest) if rest else 1


def _strip_tags(s) -> str:
    return _http.clean(re.sub(r"<[^>]+>", "", str(s or "")))


def _title(number, year, type_name) -> str:
    return f"الدعوى {number} لسنة {year} قضائية «{_http.clean(type_name)}»"


def _hit(row: dict) -> DecisionHit:
    m = _CASEINFO.search(row.get("caseInfo") or "")
    number, year, tname = (m[1], m[2], m[3]) if m else (row.get("ruleNumber"), "", "")
    title = _title(number, year, tname) if m else _http.clean(row.get("caseInfo")) or f"{COURT} {number}"
    snippet = _strip_tags(row.get("matchedParagraph")) or _http.clean(row.get("subject"))
    warding = _http.clean(row.get("ruleWarding"))
    if warding:
        snippet = f"{snippet} — {warding}" if snippet else warding
    return DecisionHit(id=str(row["caseId"]), title=title, court=COURT,
                       date=_http.iso_date(row.get("ruleDate")),
                       case_number=f"{number} لسنة {year} {_http.clean(tname)}".strip() if m else "",
                       snippet=snippet[:500], url=_http.clean(row.get("filePath")))


async def _search(body: dict) -> list[dict]:
    r = await _http.post(SEARCH, json=body)
    if r.status_code != 200:
        raise SourceError(_http.error("sccourt.gov.eg", "search failed", r.status_code), r.status_code)
    try:
        d = r.json()
    except ValueError as e:
        raise SourceError("sccourt.gov.eg: unexpected non-JSON search reply", r.status_code) from e
    data = d.get("data") if isinstance(d, dict) else None
    if not isinstance(data, list):
        raise SourceError(f"sccourt.gov.eg: search refused: {str(d)[:200]}", r.status_code)
    rows = [x for x in data if isinstance(x, dict) and x.get("caseId")]
    rows.sort(key=lambda x: x.get("ruleDate") or "", reverse=True)
    return rows


async def _lookup(number: int, year: int, tcode: int) -> dict | None:
    rows = await _search({"ruleNumber": number, "courtYear": [year], "ruleSubjectTypeCode": [tcode]})
    return next((x for x in rows if str(x.get("ruleNumber")) == str(number)), None)


class Egypt(Jurisdiction):
    code = "eg"
    name = "Egypt"
    languages = ("ar",)
    aliases = ("egypt", "egy", "misr", "مصر")
    sources = (
        Source(
            name="المحكمة الدستورية العليا – Supreme Constitutional Court portal (judgments, full text)",
            url="https://www.sccourt.gov.eg/newportal/",
            covers=("caselaw",),
            licence=("none stated: no terms page; footer 'جميع الحقوق محفوظة © 2025 للمحكمة الدستورية "
                     "العليا' (all rights reserved). Court judgments are excluded from copyright under "
                     "Egyptian Law 82/2002 art. 141"),
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit=("unknown; 1 s spacing, no 429 seen in ~40 requests (2026-11-06); "
                        "robots.txt absent (404)"),
            terms_url="https://www.sccourt.gov.eg/newportal/",
        ),
    )
    caselaw_filters = {
        "type": "case type, name or code: دستورية (1, default for number lookups), تفسير تشريعى (2), "
                "تنازع (3), منازعة تنفيذ (6), ...",
        "judicial_year": "judicial year of the case (سنة قضائية), e.g. 9 for 'الدعوى 37 لسنة 9'",
        "number": "case number, e.g. 37",
        "date_from": "earliest ruling date, YYYY-MM-DD (only without search words)",
        "date_to": "latest ruling date, YYYY-MM-DD (only without search words)",
    }
    min_interval = {"www.sccourt.gov.eg": 1.0}
    notes = ("Supreme Constitutional Court judgments (Arabic, full text, since 1979). The source returns "
             "at most 25 rulings per query (newest first); narrow with filters or cite 'الدعوى 37 لسنة 9'. "
             "No legislation; Court of Cassation (cc.gov.eg) forbids automated access.")
    gaps = (
        "Court of Cassation case law: policy bans 'الاستخراج الآلى' (automated extraction) and is paid",
        "Legislation: no free official source; the Official Gazette (Al-Amiria) archive needs a paid account",
        "Constitutional Court rulings beyond ~25 per query: the source caps results; older ones only by exact number lookup",
        "Council of State and lower-court decisions: not researched yet",
    )
    samples = {
        "caselaw_query": "حرية التعبير",
        "decision_id": "421",
    }

    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        q = _http.clean(query)
        body: dict = {}
        ref = _parse_ref(q) if q else None
        if ref:
            body.update(ruleNumber=ref[0], courtYear=[ref[1]], ruleSubjectTypeCode=[ref[2]])
            q = ""
        if v := _http.clean(filters.get("type")):
            body["ruleSubjectTypeCode"] = [_type_code(v)]
        for key, field in (("judicial_year", "courtYear"), ("number", "ruleNumber")):
            if v := _http.clean(filters.get(key)).translate(_DIGITS):
                if not v.isdigit():
                    raise BadRequest(f"{key} must be a whole number, e.g. 9; got {v!r}.")
                body[field] = [int(v)] if field == "courtYear" else int(v)
        for key, field in (("date_from", "ruleDateFrom"), ("date_to", "ruleDateTo")):
            if v := _http.clean(filters.get(key)):
                try:
                    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
                        raise ValueError(v)
                    datetime.date.fromisoformat(v)
                except ValueError:
                    raise BadRequest(f"{key} must be a real date in YYYY-MM-DD format; got {v!r}.") from None
                if q:
                    raise BadRequest("The Court's search returns nothing when words and dates are combined; "
                                     "use date_from/date_to without search words, or judicial_year with words.")
                body[field] = v
        if body.get("ruleDateFrom") and body.get("ruleDateTo") and body["ruleDateFrom"] > body["ruleDateTo"]:
            raise BadRequest(f"date_from ({body['ruleDateFrom']}) is after date_to ({body['ruleDateTo']}).")
        near = False
        if q:
            body.update(ruleText=q, identical=False, slop=None)
            if len(q.split()) > 1:  # plain word search ORs the words (even "في"): ask for adjacent words
                body["slop"] = 0
        if not body:
            raise BadRequest("Give search words (Arabic), a case citation like 'الدعوى 37 لسنة 9' or a filter.")
        rows = await _search(body)
        if q and len(q.split()) > 1:
            rows = [r for r in rows if _NO_MATCH not in (r.get("matchedParagraph") or "")]
            if not rows:  # nothing with the words side by side: allow up to 5 words in between
                rows = await _search({**body, "slop": 5})
                near = True
        capped = len(rows) >= MAX_HITS
        if q:  # the source pads word searches with unrelated rulings flagged "عدد النتائج:0" (0 matches)
            rows = [r for r in rows if _NO_MATCH not in (r.get("matchedParagraph") or "")]
        stem_dropped = 0
        if q and len(q.split()) == 1:  # the source also returns rulings with only a shorter root (خصوص for خصوصية)
            core = q[2:] if q.startswith("ال") and len(q) > 4 else q
            kept = [r for r in rows if core in _strip_tags(r.get("matchedParagraph"))]
            stem_dropped, rows = len(rows) - len(kept), kept
        start = (page - 1) * limit
        note = (f"The Court's search returns at most {MAX_HITS} rulings per query, newest first; its word "
                "index is partial (it misses some older judgments) and loose (it can return rulings without "
                "your word). Narrow with type / judicial_year / number.")
        if capped:
            note += " This query hit the cap: older rulings in the same window are NOT shown."
            if not q and (body.get("ruleDateFrom") or body.get("ruleDateTo")):
                note += (" The source gives only the newest 25 rulings of the window, so each year (2022, 2023, "
                         "2024, 2025 ...) needs its own date_from/date_to window, and a busy year needs "
                         "narrower ones (e.g. one month); move date_to back to see older rulings.")
            elif not q:
                note += " Add date_from/date_to (without search words) or judicial_year to reach older ones."
        if q and rows:
            if len(q.split()) > 1:
                note += (" Hits have your words " + ("within 5 words of each other (none had them side by side)"
                         if near else "side by side, in order") + "; the source also matches word stems, "
                         "so check each snippet before relying on a hit.")
            else:
                note += (" The source matches word stems; hits whose snippet lacks your word were dropped"
                         f" ({stem_dropped} dropped), but the word may still sit outside the snippet: read the ruling.")
        if q and not rows:
            note = ("No ruling's text matched these words (the Court's word index is partial; try other "
                    "wording or a case citation). " + note)
        return Results([_hit(r) for r in rows[start:start + limit]], total=None, note=note)

    async def get_decision(self, id):
        s = _http.clean(id).translate(_DIGITS)
        hit_row = None
        if not s.isdigit():
            ref = _parse_ref(s)
            if not ref:
                raise BadRequest("Egyptian SCC ids are the portal's caseId (e.g. '421') or a citation like "
                                 f"'الدعوى 37 لسنة 9 قضائية دستورية' / '37/9'; got {id!r}.")
            hit_row = await _lookup(*ref)
            if not hit_row:
                raise NotFound(f"No Supreme Constitutional Court ruling in case {ref[0]} لسنة {ref[1]} "
                               f"«{TYPES[ref[2]]}».")
            s = str(hit_row["caseId"])
        if s in _cache:
            return _cache[s]
        r = await _http.get(DETAILS, params={"CaseiD": s})
        if r.status_code != 200:
            raise SourceError(_http.error("sccourt.gov.eg", "details request failed", r.status_code), r.status_code)
        try:
            rows = r.json().get("data") or []
        except (ValueError, AttributeError) as e:
            raise SourceError("sccourt.gov.eg: unexpected details reply", r.status_code) from e
        if not rows:
            raise NotFound(f"No Supreme Constitutional Court ruling with caseId {s}.")
        det = rows[0]
        url = _http.clean(det.get("htmlFIleBase64"))
        if not url.startswith("http"):
            raise NotFound(f"Case {s} has no published judgment text on the Court's portal.")
        number, year, tcode = det.get("ruleNumber"), det.get("courtYear"), det.get("ruleSubjectTypeCode")
        if hit_row is None and number and year and tcode:
            hit_row = await _lookup(int(number), int(year), int(tcode))
        h = await _http.get(url)
        if h.status_code == 404:
            raise NotFound(f"Judgment text for case {s} is missing on the portal ({url}).")
        if h.status_code != 200:
            raise SourceError(_http.error("sccourt.gov.eg", "judgment page failed", h.status_code), h.status_code)
        html = h.content.decode("utf-8", errors="replace")
        m = re.search(r"(?is)<div id=['\"]wrap['\"]>(.*)</div>", html)
        text = _http.html_to_md(m[1] if m else html)
        if len(text) < 200:
            raise SourceError(f"sccourt.gov.eg: unexpectedly short judgment page for case {s}", 200)
        tname = TYPES.get(tcode, "")
        journal = " ".join(x for x in (
            f"العدد {_http.clean(det.get('journalVersionNum'))}" if _http.clean(det.get("journalVersionNum")) else "",
            f"بتاريخ {_http.iso_date(det.get('journalPublishDate'))}" if det.get("journalPublishDate") else "") if x)
        meta = {k: v for k, v in (
            ("الطلبات", _http.clean(det.get("requests"))),
            ("النص المطعون فيه", _http.clean(det.get("briefSubject"))),
            ("القانون", _http.clean(det.get("law"))),
            ("المدعي", _http.clean(det.get("claimed"))),
            ("المدعى عليهم", _http.clean(det.get("defendent"))),
            ("الإحالة", _http.clean(det.get("courtSubject"))),
            ("تاريخ القيد", _http.iso_date(det.get("submissionDate"))),
            ("أوجه عدم القبول", _http.clean(det.get("disagreeReason")).strip(" -")),
            ("الجريدة الرسمية", journal),
        ) if v}
        d = Decision(id=s, title=_title(number, year, tname), text=text, url=url, court=COURT,
                     date=_http.iso_date((hit_row or {}).get("ruleDate")),
                     case_number=f"{number} لسنة {year} {tname}".strip(),
                     summary=_http.clean((hit_row or {}).get("ruleWarding")), metadata=meta)
        return _http.lru_put(_cache, s, d, 8)
