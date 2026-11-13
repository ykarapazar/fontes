"""Caribbean Court of Justice (CCJ): judgments from ccj.org.

ccj.org is WordPress. The two official judgment lists are Ninja Tables whose rows the
page loads from admin-ajax.php (not documented; it is what the public pages use):
  * Original Jurisdiction:  /original-jurisdiction-judgments/  (table 18497)
  * Appellate Jurisdiction: /judges-main/                      (table 18384)
Each page embeds its table's "data_request_url"
(admin-ajax.php?action=wp_ajax_ninja_tables_public_action&table_id=…&target_action=get-all-data…),
which returns every row as JSON: delivery date, neutral citation, parties and an HTML
"details" cell with the PDF links (judgment, then summaries / translations / separate
judgments). The OJ table also has a parties description and keywords. Both lists are
fetched at most once per _TTL seconds and kept in memory (no disk cache).

The citation column is hand-typed and messy ("{2019] CCJ 3 (OJ)", "[2016] CCJ 1 (0J)",
"2020 CCJ 4 AJ GY", "[2019] CCJ 09 (AJ)"), so ids are the normalised core neutral
citation "[YYYY] CCJ N (AJ|OJ)"; the source's own string (with country / type suffix such
as "GY" or "(AO)") is kept as case_number. "<citation>#n" opens the n-th PDF of a row.
Old links point at www.ccj.org / www.caribbeancourtofjustice.org, which 301 to ccj.org;
they are rewritten to https://ccj.org directly. Judgments are text-layer PDFs (pypdf).
"""
from __future__ import annotations

import re
import time
from urllib.parse import unquote, urlsplit

from lxml import html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, Results

HOST = "ccj.org"
COURT = "Caribbean Court of Justice"
LISTS = {
    "OJ": f"https://{HOST}/original-jurisdiction-judgments/",
    "AJ": f"https://{HOST}/judges-main/",
}
_TTL = 6 * 3600
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# core of a CCJ neutral citation, tolerant of the list's typos
_CITE = re.compile(r"(\d{4})\s*\]?\s*CCJ\s*0*(\d+)\s*[(\[{]?\s*([AO0])J\b", re.I)
_OLD_HOSTS = ("ccj.org", "www.ccj.org", "caribbeancourtofjustice.org", "www.caribbeancourtofjustice.org")

# country codes the list appends to appellate citations ("[2020] CCJ 20 (AJ) BB")
_COUNTRY = {"BB": "Barbados", "BZ": "Belize", "DM": "Dominica", "GY": "Guyana", "LC": "Saint Lucia"}

_cache: dict = {}        # {"t": monotonic time, "rows": [...]}


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #
def _key(s: str) -> tuple[str, str, str] | None:
    m = _CITE.search(s or "")
    if not m:
        return None
    return m[1], str(int(m[2])), "AJ" if m[3].upper() == "A" else "OJ"


def _cite(key: tuple[str, str, str]) -> str:
    return f"[{key[0]}] CCJ {key[1]} ({key[2]})"


def _country(cite: str) -> str:
    m = re.search(r"\bCCJ\b.*?\b([A-Z]{2})\b\)?\s*$", cite or "")
    return _COUNTRY.get(m[1], "") if m else ""


def _plain(s: str) -> str:
    return _http.clean(re.sub(r"<[^>]+>", " ", s or ""))


def _date(s: str) -> str:
    m = re.match(r"^\s*(\d{4})[/-](\d{1,2})[/-](\d{1,2})", s or "")
    return f"{m[1]}-{int(m[2]):02d}-{int(m[3]):02d}" if m else ""


_ROLE = re.compile(r"(?i)^(first|second|third|fourth|fifth)?\s*(appellants?|respondents?|claimants?|"
                   r"defendants?|applicants?|intervener|amicus curiae)$")


def _parties(cell: str) -> list[str]:
    parts = [_plain(p) for p in re.split(r"(?i)<br\s*/?>", cell or "")]
    return [p for p in parts if p and not _ROLE.match(p)]


def _pdf_url(href: str) -> str:
    u = urlsplit(href.strip())
    if (u.hostname or "").lower() in _OLD_HOSTS:
        return f"https://{HOST}{u.path}"
    return href.strip()


def _docs(cell: str) -> list[dict]:
    out = []
    if not cell:
        return out
    for a in lhtml.fragment_fromstring(cell, create_parent="div").xpath(".//a[@href]"):
        url = _pdf_url(a.get("href"))
        name = unquote(urlsplit(url).path.rsplit("/", 1)[-1])
        out.append({"url": url, "label": _http.clean(a.text_content()) or name, "file": name})
    return out


def _row(jur: str, v: dict) -> dict | None:
    if jur == "OJ":
        cite, date = _plain(v.get("neutralcitationnumber")), _date(v.get("deliverydate"))
        claim, deft, details = v.get("claimant"), v.get("defendant"), v.get("details")
        desc, kw = _plain(v.get("partiesdescription")), _plain(v.get("keywords"))
    else:
        cite, date = _plain(v.get("ninja_column_2")), _date(v.get("ninja_column_1"))
        claim, deft, details = v.get("ninja_column_3"), v.get("ninja_column_4"), v.get("ninja_column_5")
        desc, kw = "", ""
    key = _key(cite)
    if not key:
        return None
    docs = _docs(details)
    if date and key[0] != date[:4]:
        # A typo'd citation column ("[2021] CCJ 8 (AJ) BB" for a 2022 judgment): trust the
        # row's own download link when it carries a citation of the delivery year.
        key = next((k for k in map(_key, (d["label"] for d in docs)) if k and k[0] == date[:4]), key)
    a, b = _parties(claim), _parties(deft)
    title = " v ".join(x for x in (
        (a[0] + (" and others" if len(a) > 1 else "")) if a else "",
        (b[0] + (" and others" if len(b) > 1 else "")) if b else "") if x)
    return {"key": key, "cite": cite, "date": date, "jur": jur, "claimants": a, "defendants": b,
            "title": title or f"{COURT} {_cite(key)}", "desc": desc, "keywords": kw, "docs": docs}


async def _table(jur: str) -> list[dict]:
    r = await _http.get(LISTS[jur])
    if r.status_code != 200:
        raise SourceError(_http.error("CCJ", f"{jur} judgment list failed", r.status_code), r.status_code)
    m = re.search(r'"data_request_url":"([^"]+)"', r.text)
    if not m:
        raise SourceError(f"Error (CCJ): the {jur} judgment page no longer embeds its table "
                          f"data URL; see {LISTS[jur]}.", "layout")
    url = m[1].replace("\\/", "/").replace("\\u0026", "&")
    if urlsplit(url).hostname != HOST:
        raise SourceError(f"Error (CCJ): unexpected table data URL {url}.", "layout")
    d = await _http.get(url)
    try:
        data = d.json()
    except ValueError:
        data = None
    if d.status_code != 200 or not isinstance(data, list):
        raise SourceError(_http.error("CCJ", f"{jur} judgment table failed", d.status_code), d.status_code)
    return [x for x in (_row(jur, (e or {}).get("value") or {}) for e in data) if x]


async def _rows() -> dict[tuple, dict]:
    if _cache and time.monotonic() - _cache["t"] < _TTL:
        return _cache["rows"]
    rows: dict[tuple, dict] = {}
    for jur in LISTS:
        for row in await _table(jur):
            rows.setdefault(row["key"], row)
    _cache.update(t=time.monotonic(), rows=rows)
    return rows


# --------------------------------------------------------------------------- #
class CCJ(Jurisdiction):
    code = "ccj"
    name = "Caribbean Court of Justice"
    languages = ("en", "nl")
    aliases = ("caribbean court of justice", "caricom court", "ccj appellate", "ccj original")
    sources = (
        Source(
            name="CCJ judgment lists and PDFs (ccj.org)",
            url="https://ccj.org/judgments-proceedings/judgments/",
            covers=("caselaw",),
            licence=("© Caribbean Court of Justice; no licence stated (the Terms of Use page "
                     "is empty, 2026-11-05)"),
            commercial_use=None,
            ai_use=None,   # robots.txt: "User-agent: * / Disallow:" (allows all); no AI/TDM clause found
            auth="none",
            rate_limit=("unknown; 1 s spacing, both lists cached in memory 6 h; "
                        "no 429 seen in ~20 requests (2026-11)"),
            terms_url="https://ccj.org/terms-of-use/",
        ),
    )
    caselaw_filters = {
        "jurisdiction": "AJ (appellate: appeals from Barbados, Belize, Dominica, Guyana, Saint Lucia) "
                        "or OJ (original: Revised Treaty of Chaguaramas)",
        "date_from": "delivered on or after YYYY-MM-DD",
        "date_to": "delivered on or before YYYY-MM-DD",
    }
    min_interval = {HOST: 1.0}
    notes = ("Every published CCJ judgment (appellate and original jurisdiction, 2005-). Search "
             "matches citation, parties and (original jurisdiction) keywords, not full text; "
             "judgment text comes from the official PDF. Advisory opinions only if listed in the "
             "original-jurisdiction table.")
    gaps = (
        ("Full-text search: the judgment lists match citation, parties and (OJ) keywords only, not"
         " judgment text"),
        "Pleadings, hearing records and procedural orders: not researched yet",
    )
    samples = {
        "caselaw_query": "Shanique Myrie",
        "decision_id": "[2013] CCJ 3 (OJ)",   # Myrie v Barbados
    }

    # ------------------------------------------------------------------ #
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        f = {k: str(v).strip() for k, v in (filters or {}).items() if str(v).strip()}
        jur = f.get("jurisdiction", "").upper()
        jur = {"APPELLATE": "AJ", "ORIGINAL": "OJ"}.get(jur, jur)
        if jur and jur not in LISTS:
            raise BadRequest("jurisdiction must be AJ (appellate) or OJ (original).")
        for k in ("date_from", "date_to"):
            if k in f and not _DATE.match(f[k]):
                raise BadRequest(f"{k} must be YYYY-MM-DD.")

        q = (query or "").strip()
        exact = _key(q) if re.search(r"CCJ", q, re.I) else None
        words = [w.strip('"').lower() for w in re.findall(r'"[^"]+"|\S+', q)]
        words = [w for w in words if w and w not in ("v", "v.", "vs", "vs.")]

        hits = []
        for row in (await _rows()).values():
            if jur and row["jur"] != jur:
                continue
            if "date_from" in f and (not row["date"] or row["date"] < f["date_from"]):
                continue
            if "date_to" in f and (not row["date"] or row["date"] > f["date_to"]):
                continue
            if exact:
                if row["key"] != exact:
                    continue
            else:
                hay = " ".join([row["cite"], _cite(row["key"]), row["date"], *row["claimants"],
                                *row["defendants"], _country(row["cite"]), row["desc"], row["keywords"]]).lower()
                if not all(w in hay for w in words):
                    continue
            hits.append(row)
        hits.sort(key=lambda r: (r["date"], int(r["key"][1])), reverse=True)

        limit = max(1, min(int(limit), 50))
        page = max(1, int(page))
        items = []
        for row in hits[(page - 1) * limit: page * limit]:
            snippet = row["keywords"] or row["desc"] or "; ".join(
                x for x in ("; ".join(row["claimants"]), "; ".join(row["defendants"])) if x)
            items.append(DecisionHit(
                id=_cite(row["key"]),
                title=row["title"],
                court=f"{COURT} ({'Appellate' if row['jur'] == 'AJ' else 'Original'} Jurisdiction)",
                date=row["date"],
                case_number=row["cite"],
                snippet=snippet[:300],
                url=row["docs"][0]["url"] if row["docs"] else LISTS[row["jur"]],
            ))
        return Results(items=items, total=len(hits),
                       note=("Matches citation, parties, country (only where the list's citation "
                             "carries a code such as BB, BZ, DM, GY, LC; older appeals have none) "
                             "and (OJ) keywords, all words; not full text. For keyword search inside judgments use the CCJ Library "
                             "Catalogue (opac.ccj.org)."))

    # ------------------------------------------------------------------ #
    async def get_decision(self, id):
        ident = (id or "").strip()
        base, _, n = ident.partition("#")
        key = _key(base)
        if not key or (n and not n.strip().isdigit()):
            raise BadRequest("Give a CCJ neutral citation such as '[2013] CCJ 3 (OJ)' or "
                             "'[2026] CCJ 16 (AJ)', optionally '#2' for the row's 2nd PDF.")
        row = (await _rows()).get(key)
        if row is None:
            raise NotFound(f"The CCJ judgment lists have no {_cite(key)}.")
        cite = _cite(key)
        docs = row["docs"]
        if not docs:
            raise NotFound(f"{cite} is listed by the CCJ but has no PDF link; see {LISTS[row['jur']]}.")
        idx = int(n) if n.strip() else 1
        if not 1 <= idx <= len(docs):
            raise NotFound(f"{cite} has {len(docs)} document(s); use #1 to #{len(docs)}.")
        doc = docs[idx - 1]
        if urlsplit(doc["url"]).hostname != HOST or not doc["url"].lower().endswith(".pdf"):
            raise SourceError(f"Error (CCJ): {cite}#{idx} is not a PDF on {HOST}; open {doc['url']}.")
        r = await _http.get(doc["url"])
        if r.status_code != 200:
            raise SourceError(_http.error("CCJ", f"PDF for {cite} failed", r.status_code), r.status_code)
        text = _http.pdf_text(r.content)
        if len(text) < 200:
            raise SourceError(f"Error (CCJ): {doc['url']} is a scanned PDF without a text layer "
                              "(no OCR here); read it there.", "pdf")
        meta = {"Jurisdiction": "Appellate" if row["jur"] == "AJ" else "Original",
                "Citation as listed": row["cite"],
                "Document": f"{idx} of {len(docs)}: {doc['label']} ({doc['file']})"}
        if row["claimants"]:
            meta["Claimant / appellant"] = "; ".join(row["claimants"])
        if row["defendants"]:
            meta["Defendant / respondent"] = "; ".join(row["defendants"])
        others = [f"{cite}#{i} {d['label']} ({d['file']})" for i, d in enumerate(docs, 1) if i != idx]
        if others:
            meta["Other documents"] = "; ".join(others)
        return Decision(
            id=cite if idx == 1 else f"{cite}#{idx}",
            title=row["title"],
            text=text,
            url=doc["url"],
            court=f"{COURT} ({meta['Jurisdiction']} Jurisdiction)",
            date=row["date"],
            case_number=row["cite"],
            summary=row["keywords"],
            metadata=meta,
        )
