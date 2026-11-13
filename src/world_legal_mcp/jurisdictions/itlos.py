"""ITLOS (International Tribunal for the Law of the Sea, Hamburg): the case pages on
www.itlos.org (TYPO3, server-rendered HTML).

  * Case list: GET /en/main/cases/list-of-cases/ -> one <div class="fs-list-cases-item">
    per case ("Case No. 37", "Cases Nos 3 & 4") linking to the case page by slug.
    About 36 cases (2026-11-05); no dates on the list. Fetched at most once per _TTL
    seconds and kept in memory; search filters it locally (the site's own ke-search is
    disallowed by robots.txt, and so is every URL with ?id=).
  * Case page: GET <slug> -> h1 title, an "Overview of the case" accordion (narrative),
    then sections (<h2>: Institution of Proceedings, Written Proceedings, Orders,
    Judgment, Advisory Opinion, Press Releases, ...) listing PDF links under
    /fileadmin/itlos/documents/. Incidental proceedings sometimes live on sub-pages.

Terms (www.itlos.org/en/special/disclaimer/, read 2026-11-05) allow downloading and
copying website resources for personal, non-commercial use, with the Tribunal named as
source, but the texts of the ITLOS Reports (judgments, advisory opinions, orders) and
of the Pleadings series "may not be reproduced, translated, stored in a retrieval system
... without prior written permission from the Registrar". The PDFs on the case pages are
those Reports texts, so this adapter does NOT extract their text: get_decision returns
the case record (overview + every document with date and direct PDF link).

Ids: the ITLOS list-of-cases number ("31", "Case No. 31"); the joined Southern Bluefin
Tuna cases are "3-4" ("3" and "4" also work).
"""
from __future__ import annotations

import re
import time
import unicodedata
from urllib.parse import urljoin, urlsplit

from lxml import html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, Results

HOST = "www.itlos.org"
BASE = f"https://{HOST}"
LIST_URL = f"{BASE}/en/main/cases/list-of-cases/"
COURT = "International Tribunal for the Law of the Sea"
_TTL = 6 * 3600

_MONTHS = ("january", "february", "march", "april", "may", "june", "july", "august",
           "september", "october", "november", "december")
_DMY = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(" + "|".join(_MONTHS) + r")\s+(\d{4})\b", re.I)
_TYPES = {
    "prompt_release": "prompt release",
    "provisional_measures": "provisional measures",
    "advisory": "advisory opinion",
}

_list_cache: dict = {}            # {"t": monotonic time, "rows": [...]}
_case_cache: dict = {}            # case id -> parsed record (small LRU)


def _fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[\"“”'’‘]", "", s)


def _dmy(s: str) -> str:
    """First '21 May 2024' in s -> '2024-05-21'; else ''."""
    m = _DMY.search(s or "")
    if not m:
        return ""
    return f"{m[3]}-{_MONTHS.index(m[2].lower()) + 1:02d}-{int(m[1]):02d}"


def _norm_id(s: str) -> str:
    """'ITLOS Case No. 31' / 'C31' / 'Cases Nos 3 & 4' -> '31' / '3-4'."""
    s = _http.clean(s).lower()
    s = re.sub(r"^(itlos\s*)?(list of cases:?\s*)?(cases?\s*)?(nos?\.?\s*)?(c(?=\d))?", "", s)
    s = re.sub(r"\s*(&|and|-|/|,)\s*", "-", s).strip(" .")
    return s


# --------------------------------------------------------------------------- #
# Source access
# --------------------------------------------------------------------------- #
async def _fetch(url: str, what: str) -> str:
    r = await _http.get(url)
    if r.status_code == 404:
        raise NotFound(f"ITLOS page not found: {url}")
    if r.status_code != 200:
        raise SourceError(_http.error("ITLOS", f"{what} failed", r.status_code), r.status_code)
    return r.text


def _parse_list(page: str) -> list[dict]:
    root = lhtml.fromstring(page)
    rows = []
    for item in root.xpath("//div[contains(@class,'fs-list-cases-item')]"):
        h3 = item.xpath("./h3")
        links = item.xpath(".//a[@href]")
        if len(h3) < 2 or not links:
            continue
        label = _http.clean(h3[0].text_content())               # "Case No. 37"
        nums = re.findall(r"\d+", label)
        if not nums:
            continue
        rows.append({"id": "-".join(nums), "nums": set(nums), "label": label,
                     "title": _http.clean(h3[1].text_content()),
                     "url": urljoin(BASE, links[0].get("href"))})
    if not rows:
        raise SourceError("Error (ITLOS): list of cases had no entries (page layout changed?).")
    return rows


async def _cases() -> list[dict]:
    if _list_cache and time.monotonic() - _list_cache["t"] < _TTL:
        return _list_cache["rows"]
    rows = _parse_list(await _fetch(LIST_URL, "list of cases"))
    _list_cache.update(t=time.monotonic(), rows=rows)
    return rows


async def _row(ident: str) -> dict:
    cid = _norm_id(ident)
    if not re.fullmatch(r"\d+(-\d+)*", cid):
        raise BadRequest("Give an ITLOS case number as the list of cases shows it: 31, "
                         "'Case No. 31', or 3-4 for the joined Southern Bluefin Tuna cases.")
    cid = "-".join(p.lstrip("0") or "0" for p in cid.split("-"))
    nums = set(cid.split("-"))
    for c in await _cases():
        if c["id"] == cid or nums <= c["nums"]:
            return c
    raise NotFound(f"ITLOS has no case {cid} in its list of cases ({LIST_URL}).")


def _parse_case(row: dict, page: str) -> dict:
    root = lhtml.fromstring(page)
    box = root.xpath("//div[contains(@class,'fs-content-container')]")
    if not box:
        raise SourceError(f"Error (ITLOS): case page {row['url']} has no content block.")
    box = box[0]
    h1 = box.xpath(".//h1")
    rec = {"id": row["id"], "label": row["label"], "url": row["url"],
           "title": _http.clean(h1[0].text_content()) if h1 else row["title"],
           "overview": [], "docs": [], "pages": []}

    case_path = urlsplit(row["url"]).path
    seen_docs: dict[str, dict] = {}
    pages: dict[str, str] = {}            # sub-page path -> label (later listing wins)

    def add_link(a, section: str, sub: str):
        href = a.get("href") or ""
        url = urljoin(row["url"], href)
        parts = urlsplit(url)
        if parts.hostname != HOST:
            return
        label = _http.clean(a.text_content()) or parts.path.rsplit("/", 1)[-1]
        if parts.path.lower().endswith(".pdf") and parts.path.startswith("/fileadmin/"):
            doc = {"title": label, "section": section, "sub": sub, "url": url,
                   "date": _dmy(label)}
            if url in seen_docs:              # later, better-labelled listing wins
                seen_docs[url].update({k: v for k, v in doc.items() if v})
            else:
                seen_docs[url] = doc
                rec["docs"].append(doc)
        elif parts.path.startswith(case_path) and parts.path != case_path and not parts.query:
            pages[parts.path] = label

    # "Overview of the case" and similar accordions: narrative text
    for card in box.xpath(".//div[contains(@class,'fs-accordion')]//div[contains(@class,'card')]"):
        head = _http.clean(" ".join(card.xpath(".//*[contains(@class,'card-header')]//text()")))
        body = card.xpath(".//div[contains(@class,'card-body')]")
        if not body:
            continue
        for a in body[0].xpath(".//a[@href]"):
            add_link(a, "Mentioned in the overview", "")
        md = _http.html_to_md(lhtml.tostring(body[0], encoding="unicode"))
        if md:
            rec["overview"].append((head or "Overview", md))

    section, sub = "", ""
    for el in box.iter("h2", "h3", "strong", "a"):
        if el.xpath("ancestor::div[contains(@class,'fs-accordion')]"):
            continue
        if el.tag in ("h2", "h3"):
            section, sub = _http.clean(el.text_content()), ""
        elif el.tag == "strong":
            sub = _http.clean(el.text_content())
        elif el.get("href"):
            add_link(el, section or "Documents", sub)
    rec["pages"] = [(label, f"{BASE}{path}") for path, label in pages.items()]
    return rec


async def _case(ident: str) -> dict:
    row = await _row(ident)
    if row["id"] in _case_cache:
        return _case_cache[row["id"]]
    rec = _parse_case(row, await _fetch(row["url"], f"case {row['id']}"))
    return _http.lru_put(_case_cache, row["id"], rec, 16)


def _is_decision(section: str) -> bool:
    return bool(re.match(r"(?i)(judgments?|advisory opinion|orders?|award)\b", section))


def _pick_order(decisions: list[dict], overview: list) -> list[dict]:
    """The order that decided the case, not a procedural one (hearing dates, joinder): the one
    the overview says the Tribunal 'delivered' (by date), else an unnumbered 'Order of ...'
    (procedural orders carry a number like 'Order 2019/2'), else the first listed."""
    text = " ".join(md for _, md in overview)
    dates = []
    for m in re.finditer(r"delivered its (?:Order|Judgment)[^.]{0,40}?\bon\s+(\d{1,2}(?:st|nd|rd|th)?\s+\w+\s+\d{4})", text, re.I):
        dates.append(_dmy(m[1]))
    for m in re.finditer(r"\bOn\s+(\d{1,2}(?:st|nd|rd|th)?\s+\w+\s+\d{4}),?\s+the Tribunal delivered its (?:Order|Judgment)", text, re.I):
        dates.append(_dmy(m[1]))
    for d in dates:
        hit = [x for x in decisions if x["date"] == d]
        if hit:
            return hit
    plain = [x for x in decisions if not re.search(r"\bOrder\s+\d{4}/\d+", x["title"])]
    return plain or decisions


# --------------------------------------------------------------------------- #
class ITLOS(Jurisdiction):
    code = "itlos"
    name = "ITLOS (International Tribunal for the Law of the Sea)"
    languages = ("en",)
    aliases = ("international tribunal for the law of the sea", "law of the sea tribunal",
               "tidm", "tribunal international du droit de la mer", "unclos tribunal")
    sources = (
        Source(
            name="ITLOS case pages (www.itlos.org)",
            url=LIST_URL,
            covers=("caselaw",),
            licence=("ITLOS Terms and Conditions of Use: download and copy for personal, "
                     "non-commercial use (academic, research, private study), Tribunal acknowledged "
                     "as source; ITLOS Reports and Pleadings texts may not be reproduced or stored "
                     "in a retrieval system without the Registrar's written permission"),
            commercial_use=False,
            ai_use=None,   # robots.txt: User-agent * Allow /, no AI/TDM clause in the terms
            auth="none",
            rate_limit=("unknown; 1 s spacing, case list cached in memory 6 h; "
                        "no 429 seen in ~8 requests (2026-11)"),
            terms_url=f"{BASE}/en/special/disclaimer/",
            warning=("ITLOS terms: personal, non-commercial use only, acknowledge the Tribunal as "
                     "source. Judgment/order texts (ITLOS Reports) need the Registrar's permission "
                     "to reproduce, so only the case record and PDF links are given here."),
        ),
    )
    caselaw_filters = {
        "type": "prompt_release, provisional_measures or advisory (matched on the case title)",
    }
    min_interval = {HOST: 1.0}
    notes = ("ITLOS cases (list of ~36). Search matches case number and title; get_decision gives "
             "the case overview and every document (orders, judgments, advisory opinions, "
             "pleadings) with date and PDF link. Judgment texts are not reproduced (ITLOS terms). "
             "Statute, Rules of the Tribunal and UNCLOS are not served here; the official texts are "
             f"listed at {BASE}/en/main/basic-texts-and-other-documents/ (Statute = Annex VI to UNCLOS).")
    gaps = (
        f"Statute, Rules of the Tribunal (ITLOS/8) and UNCLOS: no legislation source here; read the official texts at {BASE}/en/main/basic-texts-and-other-documents/",
        "Text of judgments, orders and advisory opinions (ITLOS Reports): needs permission (Registrar's written permission)",
        "Text of pleadings (Pleadings series): needs permission (Registrar's written permission)",
        "Site search (ke-search) and ?id= URLs: robots.txt disallows; search matches case number and title only",
    )
    samples = {
        "caselaw_query": "Saiga",
        "decision_id": "2",          # The M/V "SAIGA" (No. 2) Case, Judgment of 1 July 1999
    }

    # ------------------------------------------------------------------ #
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        f = {k: str(v).strip().lower() for k, v in (filters or {}).items() if str(v).strip()}
        ctype = f.get("type", "")
        if ctype and ctype not in _TYPES:
            raise BadRequest("type must be prompt_release, provisional_measures or advisory.")

        q = (query or "").strip()
        cid = _norm_id(q)
        exact = set(cid.split("-")) if re.fullmatch(r"\d+(-\d+)*", cid) and q else set()
        words = [_fold(w).strip('"') for w in re.findall(r'"[^"]+"|\S+', q)]
        words = [w for w in words if w and w not in ("v", "v.", "vs", "vs.", "case", "the")]

        hits = []
        for c in await _cases():
            title = _fold(c["title"])
            if ctype and _TYPES[ctype] not in title:
                continue
            if exact:
                if not exact <= c["nums"]:
                    continue
            elif not all(w in f"{title} {_fold(c['label'])}" for w in words):
                continue
            hits.append(c)

        limit = max(1, min(int(limit), 50))
        page = max(1, int(page))
        items = [DecisionHit(id=c["id"], title=c["title"], court=COURT, case_number=c["label"],
                             url=c["url"])
                 for c in hits[(page - 1) * limit: page * limit]]
        note = ("Matches case number and title only (all words); newest case first. "
                             "The list has no dates; get_decision shows each document's date.")
        if re.fullmatch(r"(19|20)\d\d", q):
            note = (f"ITLOS cannot be searched or filtered by date: the case list carries no dates, so "
                    f"'{q}' is read as a case number, not a year. Cases are numbered in order of "
                    "filing (newest case first); open a case with get_decision to see its dates.")
        return Results(items=items, total=len(hits), note=note)

    # ------------------------------------------------------------------ #
    async def get_decision(self, id):
        ident = (id or "").strip()
        if "#" in ident or ".pdf" in ident.lower():
            raise BadRequest("ITLOS ids are case numbers (31, 'Case No. 31', 3-4). Document texts "
                             "are not reproduced here (ITLOS terms); get_decision on the case "
                             "lists every PDF link.")
        rec = await _case(ident)

        parts = [f"# {rec['title']}", f"{rec['label']}, {COURT}. Source: ITLOS ({rec['url']})."]
        for head, md in rec["overview"]:
            parts += ["", f"## {head}", md]
        if rec["docs"]:
            parts += ["", "## Documents",
                      "PDFs on itlos.org. Their text is not reproduced here: the ITLOS Reports and "
                      "Pleadings may not be reproduced without the Registrar's written permission."]
            last = None
            for d in rec["docs"]:
                head = " / ".join(x for x in (d["section"], d["sub"]) if x)
                if head != last:
                    parts += ["", f"### {head}"]
                    last = head
                parts.append(f"- {d['title']}: {d['url']}")
        if rec["pages"]:
            parts += ["", "## Related pages"] + [f"- {t}: {u}" for t, u in rec["pages"]]
        text = re.sub(r"\n{3,}", "\n\n", "\n".join(parts)).strip()

        decisions = [d for d in rec["docs"] if _is_decision(d["section"])]
        final = [d for d in decisions if re.match(r"(?i)(judgment|advisory opinion|award)", d["section"])]
        main = (final or _pick_order(decisions, rec["overview"]) or [{}])[0]
        meta = {"Decisions listed": str(len(decisions)), "Documents listed": str(len(rec["docs"]))}
        if main:
            meta["Main decision"] = f"{main['title']} ({main['url']})"
        return Decision(
            id=rec["id"],
            title=rec["title"],
            text=text,
            url=rec["url"],
            court=COURT,
            date=main.get("date", ""),
            case_number=rec["label"],
            metadata=meta,
        )
