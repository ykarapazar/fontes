"""Hungary: case law from the Bírósági Határozatok Gyűjteménye (eakta.birosag.hu).

No legislation: the Nemzeti Jogszabálytár's terms (jog.gov.hu/felhasznalasi-feltetelek)
forbid automated requests, bulk download and building databases from its texts
without MKIFK's written permission, so it is not used.

Gotchas this code encodes:
  * eakta.birosag.hu is the courts' official collection of anonymised decisions
    (Kúria, ítélőtáblák, törvényszékek, járásbíróságok). Its website backend
    POST /AnonimizaltHatarozat/Search (form-encoded, no auth) returns JSON with
    the hits. A hit has the year only, no full date. The full text is only a PDF
    (/anonimizalt-hatarozat-pdf/?birosagName=&ugyszam=&azonosito=<IndexId>);
    pypdf extracts it, and the decision date is read from its closing line
    ("Budapest, 2018. szeptember 24."). Our id is "<court> <case number>",
    e.g. "Kúria Pfv.21761/2017/4", resolved to the IndexId by a search.
    Anonymised spans carry the mark Ⓜ, which the website shows as a space.
"""
from __future__ import annotations

import re
from urllib.parse import urlencode

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, Results

EAKTA = "https://eakta.birosag.hu"

_KOLLEGIUM = ("büntető", "gazdasági", "közigazgatási", "munkaügyi", "polgári")
_SORT = {"court": "BirosagiSzint", "newest": "HatarozatEveCsokkeno",
         "oldest": "HatarozatEveNovekvo", "indexed": "IndexelesIdejeCsokkeno"}
_MONTHS = {m: i for i, m in enumerate(
    ("január", "február", "március", "április", "május", "június", "július",
     "augusztus", "szeptember", "október", "november", "december"), 1)}

_index_cache: dict[str, str] = {}                    # decision id -> IndexId


# --------------------------------------------------------------------------- #
# Case law
# --------------------------------------------------------------------------- #
async def _search(form: list[tuple[str, str]]) -> dict:
    try:
        r = await _http.post(f"{EAKTA}/AnonimizaltHatarozat/Search?Area=", content=urlencode(form),
                             headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"})
    except Exception as e:
        raise SourceError(f"eakta.birosag.hu search: {e}", "network") from e
    if r.status_code != 200:
        raise SourceError("eakta.birosag.hu search failed", r.status_code)
    try:
        d = r.json()
    except ValueError as e:
        raise SourceError("eakta.birosag.hu search: unexpected non-JSON reply", r.status_code) from e
    if not d.get("Success"):
        raise BadRequest(f"eakta.birosag.hu rejected the search: {d.get('Message') or 'no reason given'}")
    return d


def _val(x) -> str:
    return "" if x in (None, "None") else _http.clean(re.sub(r";?\s*</?br\s*/?>", "; ", str(x)))


def _plain(html) -> str:
    s = re.sub(r"<[^>]+>", "", re.sub(r"</?br\s*/?>", " … ", str(html or "")))
    return _http.clean(s.replace("Ⓜ", " "))


def _pdf_url(court: str, number: str, index_id: str) -> str:
    return f"{EAKTA}/anonimizalt-hatarozat-pdf/?" + urlencode(
        {"birosagName": court, "ugyszam": number, "azonosito": index_id})


def _unmark(text: str) -> str:
    """Anonymised spans carry Ⓜ, which the website shows as a space."""
    lines = (ln for ln in text.split("\n") if ln.replace("Ⓜ", "").strip() or not ln)
    return "\n".join(_http.clean(ln.replace("Ⓜ", " ")) for ln in lines)


def _decision_date(text: str) -> str:
    found = re.findall(r"(\d{4})\.\s*(" + "|".join(_MONTHS) + r")\s+(\d{1,2})\.", text[-3000:])
    if not found:
        return ""
    y, m, d = found[-1]
    return f"{y}-{_MONTHS[m]:02d}-{int(d):02d}"


def _year(v, name: str) -> str:
    if not re.fullmatch(r"\d{4}", str(v).strip()):
        raise BadRequest(f"{name} must be a year like 2020, got {v!r}")
    return str(v).strip()

_CASE_NO = re.compile(r"[A-Za-zÁÉÍÓÖŐÚÜŰáéíóöőúüű]+\.?[IVXivx]*\.?\s?\d+/\d{4}(/\d+)?(-\d+)?")


def _empty_hint(q: str, f: dict) -> str:
    hint = ""
    if "alkotmánybír" in str(f.get("court", "")).lower():
        hint += (" The Constitutional Court (Alkotmánybíróság) is not in this collection, so zero "
                 "here does not mean no such decisions exist.")
    if q and q.isascii() and re.search(r"[a-z]", q):
        hint += (" The source matches Hungarian accents exactly: retry with accents "
                 "(e.g. 'felmondás' not 'felmondas'); an unaccented word often finds nothing.")
    return hint


class Hungary(Jurisdiction):
    code = "hu"
    name = "Hungary"
    languages = ("hu",)
    aliases = ("hungary", "magyarország", "magyarorszag", "hun")
    sources = (
        Source(
            name="Bírósági Határozatok Gyűjteménye (eakta.birosag.hu, Országos Bírósági Hivatal)",
            url=EAKTA,
            covers=("caselaw",),
            licence="Not stated (published free of charge for information; reuse terms not found)",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="Not published; 1 request/s self-imposed, no 429 seen in a handful of "
                       "requests (2026-11-05)",
            terms_url=f"{EAKTA}/felhasznalasi-feltetelek",
        ),
    )
    caselaw_filters = {
        "court": "Court name as eakta writes it, e.g. 'Kúria', 'Fővárosi Ítélőtábla', "
                 "'Fővárosi Törvényszék'",
        "branch": "Kollégium: " + ", ".join(_KOLLEGIUM),
        "year_from": "Decision year from (YYYY)",
        "year_to": "Decision year to (YYYY)",
        "type": "Határozat típusa, e.g. 'elvi bírósági határozatok', 'jogegységi határozatok'",
        "case_number": "Case number (ügyszám), e.g. 'Pfv.21761/2017/4'",
        "sort": "court (Kúria first, default), newest, oldest, indexed (newest added first)",
    }
    min_interval = {"eakta.birosag.hu": 1.0}
    notes = ("Case law only: anonymised published decisions from all court levels (eakta.birosag.hu; "
             "lower courts publish a selection only), "
             "full text as PDF. Legislation is not offered: the Nemzeti Jogszabálytár's terms "
             "forbid automated use without written permission (njt.jog.gov.hu).")
    gaps = (
        "Legislation (Nemzeti Jogszabálytár, consolidated): terms forbid automated use (automated requests, bulk download); needs permission",
        "Magyar Közlöny official gazette (acts as published): source exists and works but not built yet",
        "Constitutional Court (Alkotmánybíróság) decisions: not researched yet",
    )
    samples = {
        "caselaw_query": "elbirtoklás",
        "decision_id": "Kúria Pfv.21761/2017/4",
    }

    # ----------------------------------------------------------------- caselaw
    async def search_caselaw(self, query, *, limit, page, filters) -> Results[DecisionHit]:
        f = dict(filters or {})
        unknown = set(f) - set(self.caselaw_filters)
        if unknown:
            raise BadRequest(f"Unknown filter(s): {', '.join(sorted(unknown))}. "
                             f"Supported: {', '.join(self.caselaw_filters)}")
        sort = f.get("sort", "court")
        if sort not in _SORT:
            raise BadRequest(f"sort must be one of {', '.join(_SORT)}")
        form = [("ResultCount", str(limit)), ("ResultStartIndex", str((page - 1) * limit)),
                ("Rendezes", _SORT[sort])]
        q = _http.clean(query)
        if q and not f.get("case_number") and _CASE_NO.fullmatch(q):
            f["case_number"], q = q, ""          # a bare case number is not a text search
        if q:
            form += [("KeresoSzavak[]", q), ("KeresoSzoOperatorok[]", "Osszes")]
        if f.get("court"):
            form.append(("MeghozoBirosag", str(f["court"])))
        if f.get("branch"):
            if f["branch"] not in _KOLLEGIUM:
                raise BadRequest(f"branch must be one of {', '.join(_KOLLEGIUM)}")
            form.append(("Kollegium", f["branch"]))
        if f.get("year_from"):
            form.append(("MeghozatalIdejeTol", _year(f["year_from"], "year_from")))
        if f.get("year_to"):
            form.append(("MeghozatalIdejeIg", _year(f["year_to"], "year_to")))
        if f.get("type"):
            form.append(("HatarozatTipus", str(f["type"])))
        if f.get("case_number"):
            form.append(("Azonosito", str(f["case_number"])))
        if len(form) == 3:
            raise BadRequest("Give a search query or at least one filter.")
        d = await _search(form)
        hits = []
        for x in d.get("List") or []:
            court, number = _val(x.get("MeghozoBirosag")), _val(x.get("Azonosito"))
            did = f"{court} {number}"
            if x.get("IndexId"):
                _http.lru_put(_index_cache, did, x["IndexId"], 500)
            year = _val(x.get("HatarozatEve"))
            hits.append(DecisionHit(
                id=did, title=f"{did} ({year})" if year else did, court=court,
                case_number=number,
                snippet=_plain(x.get("Rezume")) or _plain(x.get("Szoveg"))[:400],
                url=_pdf_url(court, number, x.get("IndexId") or "")))
        total = d.get("Count")
        note = "Hits carry the decision year only; the full date is in the text."
        if sort != "indexed":   # source reorders tied hits even between identical requests
            note += (" The source orders hits of the same court level/year differently from one "
                     "request to the next, so pages can repeat or skip hits; sort='indexed' pages stably.")
        if not hits:
            note += _empty_hint(q, f)
        return Results(items=hits, total=total if isinstance(total, int) else None, note=note)

    async def get_decision(self, id) -> Decision:
        did = _http.clean(id)
        court, _, number = did.rpartition(" ")
        if not court or "/" not in number:
            raise BadRequest(f"Decision id must be '<court> <case number>', e.g. "
                             f"'Kúria Pfv.21761/2017/4'; got {id!r}")
        d = await _search([("ResultCount", "5"), ("ResultStartIndex", "0"),
                           ("Azonosito", number), ("MeghozoBirosag", court)])
        x = next((x for x in d.get("List") or []
                  if _val(x.get("Azonosito")) == number and _val(x.get("MeghozoBirosag")) == court), None)
        if not x or not x.get("IndexId"):
            raise NotFound(f"No decision {did} on eakta.birosag.hu")
        url = _pdf_url(court, number, x["IndexId"])
        try:
            r = await _http.get(url)
        except Exception as e:
            raise SourceError(f"eakta.birosag.hu PDF {did}: {e}", "network") from e
        if r.status_code != 200 or "pdf" not in r.headers.get("content-type", ""):
            raise SourceError(f"eakta.birosag.hu PDF {did} not available", r.status_code)
        text = _unmark(_http.pdf_text(r.content))
        rel = "; ".join(f"{_val(k.get('KapcsolodoBirosag'))} {_val(k.get('KapcsolodoUgyszam'))}"
                        for k in x.get("KapcsolodoHatarozatok") or [])
        meta = {"Kollégium": _val(x.get("Kollegium")), "Jogterület": _val(x.get("JogTerulet")),
                "Egyedi azonosító": _val(x.get("EgyediAzonosito")),
                "Határozat éve": _val(x.get("HatarozatEve")),
                "Kapcsolódó határozatok": rel,
                "Jogszabályhelyek": _val(x.get("Jogszabalyhelyek"))}
        return Decision(id=did, title=did, text=text, url=url, court=court,
                        date=_decision_date(text), case_number=number,
                        summary=_plain(x.get("Rezume")),
                        metadata={k: v for k, v in meta.items() if v})
