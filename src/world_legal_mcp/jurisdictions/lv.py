"""Latvia: anonymised court decisions from the E-lietas portāls (Tiesu administrācija). No legislation.

Gotchas this code encodes:
  * Case law comes from the JSON gateway behind elieta.lv's "Anonimizētie nolēmumi" page:
    `POST gateway.elieta.lv/api/v1/PublicMaterial` (Swagger at /swagger/v1/swagger.json;
    request shape taken from the SPA bundle portal-services-public-materials.js). It does
    full-text search over all anonymised decisions published since 2007, Supreme Court
    (Senāts) included. The same records are published as CC0 open data on data.gov.lv
    ("anonimizetie-nolemumi", CSV index + the same PDF download links).
  * `fullText` alone returns nothing: it needs `fullTextRule` (kkpCode from
    PublicDocumentSearchTypes: all / any / incl = phrase in inflected forms / none / excl).
  * Dates are unix seconds of local (Riga) midnight; read them in Europe/Riga or they slip
    a day. `materialRegisteredFrom/To` filter on the same field.
  * There is no get-by-id: get_decision looks the ECLI up with the `ecliCode` filter, then
    downloads the PDF(s) from `PublicMaterialDownload/{fileId}`. Decision text exists only
    as PDF (text layer, no OCR). pypdf's layout mode keeps words whole where the default
    mode splits Word-made runs; an indented line starts a new paragraph.
  * Decisions are anonymised by the courts ("/Persona A/", "/pers. B/", "/adrese A/").
  * Legislation is left out: likumi.lv's search (/search.php) is disallowed in robots.txt,
    and Latvijas Vēstnesis requires written agreement for re-use of official publications
    and likumi.lv consolidated texts (vestnesis.lv/atkalizmantosana; Oficiālo publikāciju un
    tiesiskās informācijas likums Art. 18). The Saeima's titania.saeima.lv is robots
    `Disallow: /`.
"""
from __future__ import annotations

import datetime
import io
import re
from zoneinfo import ZoneInfo

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, Results

API = "https://gateway.elieta.lv/api/v1"
PORTAL = "https://elieta.lv/web/#/pakalpojumi/anonimizetie-nolemumi"
RIGA = ZoneInfo("Europe/Riga")
MAX_LIMIT = 100

_TYPES = {"civil": "cl", "administrative": "al", "criminal": "kl", "administrative_offence": "apk"}
_COURTS = {  # facet ids (PublicCourtStructureUnit court.id) checked to return that court's decisions
    "Augstākā tiesa": "2acade14-9aed-4530-936e-7d04e4e03b23",  # Senāts; also 'supreme'
    "Rīgas apgabaltiesa": "14dabff4-fecc-4065-bb9c-68eae0f42ef3",
    "Kurzemes apgabaltiesa": "db8a18fd-10c0-4448-8183-f32879e09afd",
    "Latgales apgabaltiesa": "bc581728-aefd-4fa5-a240-1e7e9070096d",
    "Vidzemes apgabaltiesa": "fe5b94a4-7cf4-4b18-84e7-b58289e0bed6",
    "Zemgales apgabaltiesa": "22a9d346-f7ce-4eae-a7b6-c5ad1ac9df18",
    "Administratīvā apgabaltiesa": "24166431-610f-4b12-9ae8-ac2deea74b38",
    "Rīgas pilsētas tiesa": "07980853-b4cb-44c0-90a8-4c8bb3eb6b6f",
    "Rīgas pilsētas Latgales priekšpilsētas tiesa": "9da263e2-cf6b-4184-92bd-2b84a5825862",
    "Rīgas pilsētas Pārdaugavas tiesa": "d82ef248-9d58-4cab-b24e-54fb0a56a1fd",
    "Rīgas pilsētas Vidzemes priekšpilsētas tiesa": "2e4d152b-5f51-4651-8390-12f79834b419",
    "Rīgas rajona tiesa": "30ad04ef-704c-4591-b28e-45fe6ec29520",
    "Kurzemes rajona tiesa": "a357f4a8-c84d-402e-9cf3-afabfce08537",
    "Latgales rajona tiesa": "9eab42b5-0006-4fb2-9556-2ad67cf25e5f",
    "Vidzemes rajona tiesa": "313551b8-25c7-45b2-9e0b-843554bfbcf5",
    "Zemgales rajona tiesa": "f35e6abc-545c-42af-af1a-ac1c213ca62c",
    "Daugavpils tiesa": "6d74e688-6791-47a3-a429-19ce2d2609be",
    "Rēzeknes tiesa": "1f44484a-3d17-478b-986e-6739425d221f",
    "Ekonomisko lietu tiesa": "84a92f50-7dec-444a-9a30-70b927671da0",
    "Administratīvā rajona tiesa Rīgas tiesu nams": "162f6283-dc36-4928-ab3e-9ac80a7048ae",
    "Administratīvā rajona tiesa Liepājas tiesu nams": "228c67ce-78fa-49b3-8e73-be85c615f0ef",
    "Administratīvā rajona tiesa Rēzeknes tiesu nams": "cd6abc36-51bc-473a-a912-f7357bbbb6cb",
    "Administratīvā rajona tiesa Valmieras tiesu nams": "edcd67a6-07d5-4255-ae7b-4e7d35a584c3",
    "Administratīvā rajona tiesa Jelgavas tiesu nams": "feed0a53-a41f-4e81-a09a-2a9b8b2a5fed",
}
_COURT_KEYS = {"supreme": _COURTS["Augstākā tiesa"], "senāts": _COURTS["Augstākā tiesa"],
               "senats": _COURTS["Augstākā tiesa"], "augstākā tiesa": _COURTS["Augstākā tiesa"],
               "augstaka tiesa": _COURTS["Augstākā tiesa"]}
_COURT_KEYS |= {k.casefold(): v for k, v in _COURTS.items()}
_RULES = {"all": "all", "any": "any", "phrase": "incl"}
_UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)
_ECLI = re.compile(r"ECLI:LV:[A-Z0-9]+:\d{4}:[A-Z0-9.]+", re.I)

_cache: dict = {}


def _date(ts) -> str:
    if not isinstance(ts, int) or ts <= 0:
        return ""
    return datetime.datetime.fromtimestamp(ts, RIGA).date().isoformat()


def _ts(s: str, end: bool = False) -> int:
    try:
        d = datetime.date.fromisoformat(str(s).strip())
    except ValueError:
        raise BadRequest(f"date {s!r}: use YYYY-MM-DD, e.g. '2024-01-31'") from None
    t = datetime.datetime.combine(d, datetime.time.max if end else datetime.time.min, RIGA)
    return int(t.timestamp())


def _court(it: dict) -> str:
    inst = it.get("institution") or {}
    return _http.clean(inst.get("departmentName") or inst.get("name"))


def _files(it: dict) -> list[str]:
    return [f["id"] for f in it.get("materialFiles") or []
            if f.get("id") and not f.get("isLimitedAccess")]


def _id(it: dict) -> str:
    """The ECLI; the PDF file id only when the source gives no ECLI."""
    return _http.clean(it.get("ecliCode")) or (_files(it) or [""])[0]


def _url(it: dict) -> str:
    fs = _files(it)
    return f"{API}/PublicMaterialDownload/{fs[0]}" if fs else PORTAL


def _title(it: dict) -> str:
    return " ".join(x for x in (_court(it), _http.clean(it.get("caseNumber"))) if x) or _id(it)


async def _search(body: dict) -> dict:
    r = await _http.post(f"{API}/PublicMaterial", json=body,
                         headers={"Accept": "application/json"})
    if r.status_code != 200:
        raise SourceError("E-lietas portāls decision search failed", r.status_code)
    try:
        d = r.json()
    except ValueError as e:
        raise SourceError("E-lietas portāls: unexpected non-JSON reply", r.status_code) from e
    if not isinstance(d, dict) or not isinstance(d.get("items"), list):
        raise SourceError("E-lietas portāls: unexpected search payload", r.status_code)
    return d


def _pdf_text(data: bytes) -> str:
    from pypdf import PdfReader
    try:
        reader = PdfReader(io.BytesIO(data))
        pages = [pg.extract_text(extraction_mode="layout") or "" for pg in reader.pages]
    except Exception as e:  # pypdf's own error types
        raise SourceError(f"decision PDF could not be read ({type(e).__name__})") from None
    paras: list[str] = []
    buf = ""
    for pg in pages:
        for ln in pg.replace("\xa0", " ").split("\n"):
            s = ln.strip()
            if not s or re.fullmatch(r"\d{1,3}|\d{1,3} ?(?:/|no|of) ?\d{1,3}", s):  # page numbers
                if not s and buf:
                    paras.append(buf)
                    buf = ""
                continue
            if re.match(r"\s{3,}", ln) and buf:  # indented line starts a paragraph
                paras.append(buf)
                buf = ""
            buf = f"{buf} {s}" if buf else s
    if buf:
        paras.append(buf)
    return "\n\n".join(p for p in (_http.clean(p) for p in paras) if p)


async def _download(file_id: str) -> str:
    r = await _http.get(f"{API}/PublicMaterialDownload/{file_id}")
    if r.status_code in (400, 404):
        raise NotFound(f"no decision file {file_id} at the E-lietas portāls")
    if r.status_code != 200 or not r.content.startswith(b"%PDF"):
        raise SourceError(f"E-lietas portāls file {file_id} download failed", r.status_code)
    return _pdf_text(r.content)


class Latvia(Jurisdiction):
    code = "lv"
    name = "Latvia"
    languages = ("lv",)
    aliases = ("latvia", "latvija", "lva")
    sources = (
        Source(
            name="E-lietas portāls – anonimizētie nolēmumi (Tiesu administrācija / Court Administration)",
            url="https://elieta.lv/web/",
            covers=("caselaw",),
            licence=("CC0 1.0 (same decisions published as open data by Tiesu administrācija: "
                     "data.gov.lv dataset 'anonimizetie-nolemumi')"),
            commercial_use=True,
            ai_use=None,
            auth="none",
            rate_limit=("not published; no robots.txt on gateway.elieta.lv or elieta.lv; "
                        "no 429 in ~20 requests (2026-11-05); using 1 s spacing"),
            terms_url="https://elieta.lv/web/#/lietosanas-noteikumi",
        ),
    )
    caselaw_filters = {
        "process_type": "'civil', 'administrative', 'criminal' or 'administrative_offence'",
        "court": ("'supreme' or one exact court name, e.g. 'Rīgas apgabaltiesa' (appeal), "
                  "'Rīgas pilsētas tiesa' or 'Kurzemes rajona tiesa' (first instance); "
                  "one court per search"),
        "date_from": "decision date from, YYYY-MM-DD",
        "date_to": "decision date to, YYYY-MM-DD",
        "case_number": "case number, e.g. 'C24127717'",
        "match": "'all' words (default), 'any' word, or 'phrase' (phrase in inflected forms)",
    }
    min_interval = {"gateway.elieta.lv": 1.0}
    notes = ("Anonymised court decisions (all courts incl. Supreme Court, 2007–today) in Latvian "
             "from the Court Administration's E-lietas portāls; ids are ECLIs. No legislation: "
             "likumi.lv search is closed to robots and re-use needs Latvijas Vēstnesis' written consent. For statute text (Darba likums, "
             "Civillikums, etc.) read it yourself at https://likumi.lv (the official consolidated "
             "texts; search there by title).")
    gaps = (
        "Legislation (likumi.lv consolidated texts): robots.txt disallows search; re-use needs "
         "Latvijas Vēstnesis written consent; read it manually at https://likumi.lv",
        "Parliament texts (titania.saeima.lv): robots.txt disallows (Disallow: /)",
        "Decisions before 2007: not in the portal (anonymised decisions published from 2007); "
         "older ones not researched yet",
        "Constitutional Court (Satversmes tiesa) judgments: not available here; this source holds "
         "the ordinary, administrative and Supreme Court decisions only (the Court publishes its own "
         "judgments at satv.tiesa.gov.lv)",
    )
    samples = {
        "caselaw_query": "īres līgums",
        "decision_id": "ECLI:LV:AT:2020:1111.C24127717.16.S",  # Senāts, civil, 11.11.2020
    }

    async def search_caselaw(self, query, *, limit, page, filters):
        q = _http.clean(query)
        body: dict = {"orderBy": "registrationDate", "sortOrderDescending": True,
                      "page": max(1, int(page)), "limit": max(1, min(MAX_LIMIT, int(limit)))}
        match = str(filters.get("match") or "all").lower()
        if match not in _RULES:
            raise BadRequest(f"match {match!r}: use one of {', '.join(_RULES)}")
        if q:
            body |= {"fullText": q, "fullTextRule": _RULES[match]}
        pt = filters.get("process_type")
        if pt:
            if str(pt).lower() not in _TYPES:
                raise BadRequest(f"process_type {pt!r}: use one of {', '.join(_TYPES)}")
            body["processTypeCode"] = _TYPES[str(pt).lower()]
        ct = str(filters.get("court") or "").strip()
        if ct:
            cid = _COURT_KEYS.get(ct.casefold()) or (ct.lower() if _UUID.fullmatch(ct) else "")
            if not cid:
                raise BadRequest(
                    f"court {ct!r}: use 'supreme' or an exact court name, e.g. 'Rīgas apgabaltiesa' "
                    f"(appeal) or 'Rīgas pilsētas tiesa' (first instance). Names: "
                    f"{'; '.join(_COURTS)}. One court per search; the portal has no filter for a "
                    "whole court level")
            body["institutionSourceRegistryId"] = cid
        if filters.get("date_from"):
            body["materialRegisteredFrom"] = _ts(filters["date_from"])
        if filters.get("date_to"):
            body["materialRegisteredTo"] = _ts(filters["date_to"], end=True)
        if filters.get("case_number"):
            body["caseNumber"] = _http.clean(filters["case_number"])
        if len(body) == 4:
            raise BadRequest("give search words in Latvian (e.g. 'īres līgums') or a filter")
        d = await _search(body)
        items = []
        for it in d["items"]:
            hid = _id(it)
            if not hid:
                continue
            _http.lru_put(_cache, hid.upper(), it, 200)
            mt = _http.clean((it.get("materialType") or {}).get("name"))
            st = _http.clean((it.get("materialStatus") or {}).get("name"))
            items.append(DecisionHit(
                id=hid, title=_title(it), court=_court(it), date=_date(it.get("registrationDate")),
                case_number=_http.clean(it.get("caseNumber")),
                snippet="; ".join(x for x in (mt, st, _http.clean(it.get("contentDescription"))) if x),
                url=_url(it)))
        total = d.get("totalResults")
        cc = ("" if not re.search(r"satversmes\s+tiesa|constitutional\s+court", q, re.I) else
              "Constitutional Court (Satversmes tiesa) judgments are NOT available in this source: "
              "hits below are other courts' decisions that merely mention the court. ")
        return Results(items=items, total=total if isinstance(total, int) else None,
                       note=(cc + "Newest first, not by relevance: the portal matches the words anywhere in "
                             "the text, so top hits may only cite them in passing (use "
                             "match='phrase', process_type or court to narrow). Latvian full "
                             "text; decisions are anonymised and published only as PDF. "
                             "Senāts = Supreme Court."))

    async def get_decision(self, id):
        s = _http.clean(id)
        m = _ECLI.search(s)
        if m:
            ecli = m[0].upper()
            it = _cache.get(ecli)
            if it is None:
                d = await _search({"ecliCode": ecli, "page": 1, "limit": 5})
                it = next((x for x in d["items"] if _http.clean(x.get("ecliCode")).upper() == ecli), None)
                if it is None:
                    raise NotFound(f"no anonymised decision {ecli} at the E-lietas portāls")
            files = _files(it)
            if not files:
                raise NotFound(f"{ecli}: the portal lists no public file for this decision")
            text = "\n\n".join([await _download(f) for f in files])
            mt = _http.clean((it.get("materialType") or {}).get("name"))
            meta = {k: v for k, v in (
                ("ECLI", ecli),
                ("type", mt),
                ("process type", _http.clean((it.get("processType") or {}).get("name"))),
                ("status", _http.clean((it.get("materialStatus") or {}).get("name"))),
                ("status date", _date((it.get("materialStatus") or {}).get("date"))),
                ("application number", _http.clean(it.get("applicationNumber"))),
                ("portal", PORTAL),
            ) if v}
            return Decision(id=_id(it), title=_title(it), text=text, url=_url(it), court=_court(it),
                            date=_date(it.get("registrationDate")),
                            case_number=_http.clean(it.get("caseNumber")), metadata=meta)
        if _UUID.fullmatch(s):  # a file id, used only for records that have no ECLI
            return Decision(id=s.lower(), title=f"E-lietas portāls decision {s.lower()}",
                            text=await _download(s.lower()),
                            url=f"{API}/PublicMaterialDownload/{s.lower()}")
        raise BadRequest(f"id {id!r}: use an ECLI from search_caselaw, "
                         "e.g. 'ECLI:LV:AT:2020:1111.C24127717.16.S'")
