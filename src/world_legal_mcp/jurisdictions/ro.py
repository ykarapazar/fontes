"""Romania: High Court of Cassation and Justice (ÎCCJ) decisions by id from scj.ro, a
legislation *index* search (metadata only) from the Chamber of Deputies database (cdep.ro),
and the full text of the Constitution (revised 2003) from the Chamber's own pages.

What is not here, and why (checked 2026-11-05 from a UK IP):
  * Case-law search: scj.ro loads results only from /Home/GetPage, which robots.txt
    disallows ("Disallow: /home/getpage"). So we only fetch single decision pages
    (/1093/Detalii-jurisprudenta?...id=N), which robots.txt allows.
  * iccj.ro and ccr.ro (Constitutional Court) answer with a "Verifying your browser..."
    JavaScript challenge. ReJust (rejust.ro) is a Blazor app with Cloudflare Turnstile.
  * Legislation text: legislatie.just.ro (Portal Legislativ) drops HTTPS connections
    without a reply, and its free SOAP API (plain HTTP) issues tokens but Search fails
    server-side ("actively refused ... :8983", its Solr backend is down). Rechecked
    2026-11-10: same (HTTPS and HTTP->HTTPS redirect: empty reply; SOAP Search: Solr
    refused). cdep.ro act pages carry metadata (publication, amendments, status) but no
    text. The one exception is the Constitution: the Chamber publishes the revised text
    (Law 429/2003) on /ords/pls/dic/site2015.page?den=act2_1&par1=1..8, one page per Title.
    It is served under the cdep.ro legis id of the Constitution, 15346.

Gotchas this code encodes:
  * scj.ro returns HTTP 200 with an empty `jurisprudence_details` block for unknown ids.
  * cdep.ro search is an Oracle PL/SQL form: POST every field or it fails with ORA-06550.
    `nrc` is the 1-based index of the first hit; pages are fixed at 100 rows, oldest first.
  * cdep.ro status column: "V" = in force (vigoare), "A" = repealed (abrogat), "-" = none.
"""
from __future__ import annotations

import re
from urllib.parse import parse_qs, urlsplit

from lxml import html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc, TocEntry

SCJ = "https://www.scj.ro"
SCJ_DECISION = SCJ + "/1093/Detalii-jurisprudenta?customQuery%5B0%5D.Key=id&customQuery%5B0%5D.Value={id}"
CDEP = "https://www.cdep.ro/ords/pls/legis/"
CDEP_ACT = CDEP + "legis_pck.htp_act?ida={id}"
CONST_ID = "15346"   # cdep.ro legis id of "CONSTITUŢIA ROMÂNIEI din 1991" (in force, revised 2003)
CONST_PAGE = "https://www.cdep.ro/ords/pls/dic/site2015.page?den=act2_1&par1={n}"
CONST_URL = "https://www.cdep.ro/ords/pls/dic/site.page?id=339"
CONST_TITLE = "Constituţia României (republicată, revizuită prin Legea nr. 429/2003)"
CONST_TITLES = 8     # Titles I-VIII, one page each
COURT = "Înalta Curte de Casaţie şi Justiţie"

_MONTHS = {"ianuarie": 1, "februarie": 2, "martie": 3, "aprilie": 4, "mai": 5, "iunie": 6,
           "iulie": 7, "august": 8, "septembrie": 9, "octombrie": 10, "noiembrie": 11,
           "decembrie": 12}
_STATUS = {"V": "in force (V)", "A": "repealed (A)"}
_MATCH = {"all": "and", "any": "or", "exact": "exact"}
# cdep.ro "Tipul actului" option values (from legis_pck.interogare, 2026-11)
_TYPES = {"lege": "1", "hotarare": "2", "decret": "3", "decret-lege": "4", "ordin": "5",
          "ordonanta": "13", "ordonanta_urgenta": "18", "decizie": "17", "cod": "33",
          "constitutie": "22", "regulament": "12", "norme": "11"}

_clean = _http.clean
_const: dict = {}


async def _constitution() -> list[dict]:
    """Constitution as a flat list of {"kind": "heading"|"article", "label", "title", "text"}."""
    if "items" in _const:
        return _const["items"]
    items = []
    for n in range(1, CONST_TITLES + 1):
        r = await _http.get(CONST_PAGE.format(n=n))
        if r.status_code != 200:
            raise SourceError(_http.error("cdep.ro", f"Constitution title {n}", r.status_code),
                              r.status_code)
        page = r.content.decode("utf-8", "replace")
        found = 0
        for row in re.split(r"(?i)<TR\b", page):
            art = re.search(r"(?i)<B>\s*ARTICOLUL\s+(\d+)\s*</B>", row)
            if art:
                side = re.search(r'(?is)<A NAME="t\d[^"]*">(.*?)</A>', row[:art.start()])
                body = re.split(r"(?i)</TABLE>", row[art.end():])[0]
                body = re.sub(r"(?is)</?(td|tr)\b[^>]*>", "", body)
                items.append({"kind": "article", "label": f"Articolul {art[1]}",
                              "title": _clean(lhtml.fromstring(side[1]).text_content()) if side else "",
                              "text": _http.html_to_md(body)})
                found += 1
            elif re.search(r"(?i)COLSPAN=2", row):
                head = re.search(r'(?is)<A NAME="t\d[^"]*">(.*?)</A>', row)
                if head:
                    h = _clean(re.sub(r"(?i)<BR\s*/?>", " - ", head[1]))
                    items.append({"kind": "heading", "label": "", "title": _clean(re.sub(r"<[^>]+>", "", h)),
                                  "text": ""})
        if not found:
            raise SourceError(f"cdep.ro: no articles on Constitution page {n} (layout changed?)")
    _const["items"] = items
    return items


def _const_id(raw: str) -> None:
    s = _clean(raw).lower()
    if s.startswith("http"):
        s = (parse_qs(urlsplit(s).query).get("ida") or [s])[0]
    s = s.translate(str.maketrans("ăâîşșţț", "aaisstt"))
    if s in (CONST_ID, "constitutia", "constitutie", "constitution"):
        return
    if re.fullmatch(r"\d{1,7}", s):
        raise NotFound(f"cdep.ro act {s}: only the Constitution ({CONST_ID}) has a text here; "
                       "other acts are index entries only (legislatie.just.ro, which has the "
                       "texts, is unreachable). See the act's url for its Monitorul Oficial details.")
    raise BadRequest(f"Romanian law ids are cdep.ro ids from search_legislation, e.g. '{CONST_ID}' "
                     f"(the Constitution), got {raw!r}")


def _art_label(raw: str) -> str:
    m = re.fullmatch(r"(?:art(?:icolul|\.)?\s*)?(\d{1,3})", _clean(raw).lower())
    if not m:
        raise BadRequest(f"Give an article like 'Articolul 21' (or '21', 'art. 21'), got {raw!r}")
    return f"Articolul {int(m[1])}"


def _art_md(it: dict) -> str:
    head = f"**{it['label']}**" + (f" - {it['title']}" if it["title"] else "")
    return f"{head}\n\n{it['text']}"


def _ro_date(s: str) -> str:
    """'9 iunie 2021' (anywhere in s) -> '2021-06-09'; else ''."""
    m = re.search(r"(\d{1,2})\s+([a-zăâîşșţț]+)\s+(\d{4})", (s or "").lower())
    if not m or m[2] not in _MONTHS:
        return ""
    return f"{m[3]}-{_MONTHS[m[2]]:02d}-{int(m[1]):02d}"


def _decision_id(raw: str) -> str:
    s = _clean(raw)
    if s.startswith("http"):
        q = parse_qs(urlsplit(s).query)
        s = (q.get("customQuery[0].Value") or [""])[0]
    if not re.fullmatch(r"\d{1,9}", s):
        raise BadRequest(f"Romanian decision ids are scj.ro numeric ids like '200000' (or the "
                         f"scj.ro 'Detalii-jurisprudenta' URL), got {raw!r}")
    return s


def _law_hits(doc) -> list:
    items = []
    for a in doc.xpath('//a[starts-with(@href, "legis_pck.htp_act?ida=")]'):
        ida = a.get("href").rsplit("=", 1)[-1]
        td = a.getparent()
        cells = td.getparent().xpath("./td")
        label = _clean(a.text_content())
        desc = _clean(" ".join(t for t in td.xpath(".//text()")[1:])).replace(label, "", 1).strip()
        desc = re.sub(r"\s+([,.;:)])", r"\1", desc)
        m = re.match(r"^(.*?)(?:\s*nr\.\s*([\d.]+))?/(\d{2}-\d{2}-\d{4})$", label)
        status = _clean(cells[-1].text_content()) if len(cells) >= 3 else ""
        items.append(LawHit(
            id=ida, title=desc or label, type=(m[1] if m else "").strip(),
            number=(m[2] or "") if m else "", date=_http.iso_date(m[3]) if m else "",
            status=_STATUS.get(status, ""),
            snippet=label if ida == CONST_ID else f"{label} | index entry only: no text, so "
            "get_legislation_toc and get_legislation_provision answer 'Not found'",
            url=CDEP_ACT.format(id=ida), has_toc=(ida == CONST_ID)))
    return items


def _fold(s: str) -> str:
    return _clean(s).lower().translate(str.maketrans("ăâîşșţț", "aaisstt"))


def _text(el) -> str:
    return _http.text(el) if el is not None else ""


class Romania(Jurisdiction):
    code = "ro"
    name = "Romania"
    languages = ("ro",)
    aliases = ("romania", "românia", "rou")
    sources = (
        Source(
            name="Înalta Curte de Casaţie şi Justiţie (High Court of Cassation and Justice), scj.ro",
            url=SCJ,
            covers=("caselaw",),
            licence=("unknown: no terms page on scj.ro (iccj.ro is behind a browser check); "
                     "court decisions are excluded from copyright (Law 8/1996 art. 9 lit. b)"),
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 in ~10 requests (2026-11-05)",
            terms_url=SCJ,
        ),
        Source(
            name="Camera Deputaţilor, Baza de date legislativă (cdep.ro), metadata only",
            url=CDEP + "legis_pck.frame",
            covers=("legislation",),
            licence=("unknown: no terms page; legal acts are excluded from copyright "
                     "(Law 8/1996 art. 9 lit. b)"),
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 in ~15 requests (2026-11-05)",
            terms_url=CDEP + "legis_pck.frame",
            warning=("cdep.ro states its information and act texts 'nu au caracter oficial' "
                     "(are not official); the official text is in Monitorul Oficial."),
        ),
        Source(
            name="Camera Deputaţilor, Constituţia României (cdep.ro), revised text 2003",
            url=CONST_URL,
            covers=("legislation",),
            licence=("no terms page; legal acts are excluded from copyright (Law 8/1996 art. 9 "
                     "lit. b); robots.txt only disallows /declaratii/"),
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 in ~12 requests (2026-11-10)",
            terms_url="https://www.cdep.ro/robots.txt",
        ),
    )
    legislation_filters = {
        "year": ("one calendar year, e.g. '2009' (the source has no working date range: for "
                 "'since 2022' make one call per year, with order='newest')"),
        "order": "'newest' to list the most recent acts first (default: oldest first; the source cannot rank by relevance)",
        "number": "act number, e.g. '287' (Legea nr. 287/2009 = Civil Code)",
        "in_text": "'true' to match words in the act text index instead of titles (default: titles)",
        "match": "'all' words (default), 'any' word, or 'exact' phrase",
        "type": "act type: " + ", ".join(f"'{t}'" for t in _TYPES)
                + " (ordonanta_urgenta = OUG, hotarare = Government decision)",
    }
    min_interval = {"www.scj.ro": 1.0, "www.cdep.ro": 1.0}
    notes = ("ÎCCJ decisions by scj.ro id only (robots.txt blocks scj.ro search). Legislation: "
             "index search on cdep.ro (number, date, status, Monitorul Oficial); full text only "
             "for the Constitution (id 15346, revised 2003). Other texts: legislatie.just.ro is "
             "unreachable/down. CCR and ReJust sit behind bot checks.")
    gaps = (
        ("ÎCCJ case-law search: robots.txt disallows scj.ro's /home/getpage, so decisions are "
         "fetched by id only"),
        ("Text of laws, codes and ordinances (consolidated and as published; the Constitution "
         "is covered): legislatie.just.ro drops our HTTPS connections and its SOAP search "
         "backend is down (2026-11-05, rechecked 2026-11-10)"),
        "Constitutional Court (ccr.ro) and iccj.ro: 'Verifying your browser' bot check",
        "Lower courts (ReJust, all courts): Blazor app behind a Cloudflare Turnstile bot check",
    )
    samples = {
        "decision_id": "200000",
        "legislation_query": "codul civil",
        "law_id": CONST_ID,
        "provision": "Articolul 21",
    }

    # ------------------------------------------------------------------ case law
    def supported(self):
        # get_legislation_toc/provision/text only open the Constitution: say so in the tool lists.
        return [m + (" (Constitution only)" if m in ("get_legislation_toc", "get_legislation_provision",
                                                      "get_legislation_text") else "")
                for m in super().supported()]

    async def get_decision(self, id):
        did = _decision_id(id)
        url = SCJ_DECISION.format(id=did)
        r = await _http.get(url)
        if r.status_code != 200:
            raise SourceError(_http.error("scj.ro", f"decision {did}", r.status_code), r.status_code)
        doc = lhtml.fromstring(r.text)
        box = doc.xpath('//div[@id="jurisprudence_details"]')
        content = box[0].xpath('.//div[@class="content"]') if box else []
        header = box[0].xpath('.//div[@class="header"]') if box else []
        if not content:
            raise NotFound(f"No ÎCCJ decision with scj.ro id {did}.")
        body = _http.html_to_md(lhtml.tostring(content[0], encoding="unicode"))
        if not body:
            raise NotFound(f"ÎCCJ decision {did} has no text on scj.ro.")
        ps = header[0].xpath("./p") if header else []
        lines = [_clean(t) for t in ps[0].xpath(".//text()")] if ps else []
        section = next((ln for ln in lines if ln.lower().startswith(("sec", "complet"))), "")
        spans = [_clean(_text(s)) for s in (ps[1].xpath(".//span") if len(ps) > 1 else [])]
        spans = [re.sub(r"\s+", " ", s) for s in spans if s]
        label = spans[0] if spans else ""
        date = _ro_date(" ".join(_text(p) for p in ps[2:])) if len(ps) > 2 else ""
        court = f"{COURT}, {section}" if section else COURT
        meta = {"Secţie": section} if section else {}
        if len(spans) > 1:
            meta["Dosar"] = spans[1]
        title = f"ÎCCJ{', ' + section if section else ''}, {label}" if label else f"ÎCCJ {did}"
        return Decision(id=did, title=title, text=body, url=url, court=court, date=date,
                        case_number=spans[1] if len(spans) > 1 else "", metadata=meta)

    # ------------------------------------------------------------------ legislation
    async def search_legislation(self, query, *, limit, page, filters):
        year = _clean(filters.get("year"))
        number = _clean(filters.get("number"))
        if year and not re.fullmatch(r"1[89]\d\d|20\d\d", year):
            raise BadRequest(f"year must be a 4-digit year like '2009', got {year!r}")
        if number and not re.fullmatch(r"[\d.]{1,10}", number):
            raise BadRequest(f"number must be digits like '287', got {number!r}")
        match = _clean(filters.get("match") or "all").lower()
        if match not in _MATCH:
            raise BadRequest("match must be 'all', 'any' or 'exact'")
        typ = _clean(filters.get("type")).lower()
        if typ and typ not in _TYPES:
            raise BadRequest(f"type must be one of {', '.join(_TYPES)}, got {typ!r}")
        order = _clean(filters.get("order")).lower()
        if order not in ("", "oldest", "newest"):
            raise BadRequest("order must be 'newest' or 'oldest'")
        in_text = str(filters.get("in_text", "")).strip().lower() in ("1", "true", "yes", "da")
        q = _clean(query)[:100]
        if not (q or year or number):
            raise BadRequest("Give words to search for, or a 'number' / 'year' filter.")
        limit = max(1, min(int(limit), 100))
        page = max(1, int(page))
        form = {
            "tip": _TYPES.get(typ, ""), "inc": "0", "nra": number,
            "cand": "3" if year else "0", "an": year,
            "dat1": ["1", "1", "2001"], "dat2": ["1", "1", "2000"],
            "emi": "", "dap1": ["1", "1", "2001"], "dap2": ["1", "1", "2000"], "publ": "-1",
            "sir": q, "sep": _MATCH[match], "sir_in": "1" if in_text else "0",
        }

        async def fetch(nrc, tip=None):
            r = await _http.post(CDEP + "legis_pck.rezultate",
                                 data={**form, "nrc": str(nrc), **({"tip": tip} if tip else {})})
            if r.status_code != 200:
                raise SourceError(_http.error("cdep.ro", "legislation search failed", r.status_code),
                                  r.status_code)
            return r.content.decode("utf-8", "replace")

        total = None
        if order == "newest":
            first = await fetch(1)
            last = max([int(n) for n in re.findall(r"nrc=(\d+)", first)] or [1])
            total = last - 1 + len(_law_hits(lhtml.fromstring(await fetch(last)))) if last > 1 \
                else len(_law_hits(lhtml.fromstring(first)))
            end = total - (page - 1) * limit
            start = max(1, end - limit + 1)
            rows = _law_hits(lhtml.fromstring(await fetch(start))) if end >= 1 else []
            items = rows[:end - start + 1][::-1]
        else:
            # A name search with no type: rank across the main act types (lege, OUG, OG)
            # instead of listing 3,000 hits oldest first.
            multi = bool(q and not (typ or year or number or order))
            ranked = bool(typ and q and not (in_text or year or number or order)) or multi
            start = 1 if ranked else (page - 1) * limit + 1
            if multi:
                items = []
                for t in ("lege", "ordonanta_urgenta", "ordonanta"):
                    part = _law_hits(lhtml.fromstring(await fetch(1, _TYPES[t])))
                    if len(part) >= 100:   # truncated: cannot rank the whole set
                        ranked = multi = False
                        break
                    items += part
            if not multi:
                items = _law_hits(lhtml.fromstring(await fetch(start)))
            if ranked and (multi or len(items) < 100):   # whole result set in hand: main laws first
                total = len(items)
                words = _fold(q).split()
                amend = lambda h: bool(re.search(r"modific|complet|aprob|respinge|abrog", _fold(h.title)))
                if in_text:   # titles need not contain the words: rank by shared word stems
                    stems = [w[:6] for w in words if len(w) > 3]
                    hits = lambda h: sum(s in _fold(h.title) for s in stems)
                    items.sort(key=lambda h: (not hits(h), amend(h), -hits(h), len(h.title)))
                else:
                    items.sort(key=lambda h: (not all(w in _fold(h.title) for w in words),
                                              amend(h), len(h.title)))
                items = items[(page - 1) * limit:][:limit]
            else:
                ranked = False
                items = (items if start == (page - 1) * limit + 1 else
                         _law_hits(lhtml.fromstring(await fetch((page - 1) * limit + 1))))[:limit]
        return Results(items, total=total, note=(
            ("Index only, newest first: " if order == "newest" else
             "Index only, title matches ranked (the main law, e.g. 'LEGE privind Codul civil', "
             "comes before amending acts; only laws, OUG and OG are ranked here, use filter "
             "type= for decisions, orders, etc.): " if ranked else
             "Index only, oldest first (the source cannot rank by relevance; add filter "
             "order='newest' for the most recent acts, or year/type/number to narrow; only a "
             "single year can be filtered, no range): ") +
            "cdep.ro gives number, date, status and Monitorul Oficial details at the url, but "
            "no text; legislatie.just.ro is unreachable. "
            + ("" if year or number or typ else
               "A search by name cannot put the main law first: to find a code or main law add "
               "its number and year, with type='lege' (Civil Code = number 287, year 2009). ") +
            "Only the Constitution "
            f"({CONST_ID}) opens in full: for every other hit, ignore the 'Contents' line, "
            "since get_legislation_toc/provision/text will answer 'Not found'."
            + (" in_text lists acts that mention the words, by date, not by relevance (without a "
               "type filter laws, OUG and OG are put first when their title shares a word stem "
               "with the query: a best guess, not a relevance score): to find the main law "
               "search its title (e.g. 'Codul consumului') instead." if in_text else "")))

    async def get_legislation_toc(self, id):
        _const_id(id)
        entries = [TocEntry(title=it["title"], level=0) if it["kind"] == "heading" else
                   TocEntry(title=f"{it['label']} - {it['title']}" if it["title"] else it["label"],
                            level=1, provision=it["label"])
                   for it in await _constitution()]
        return Toc(id=CONST_ID, title=CONST_TITLE, url=CONST_URL, entries=entries)

    async def get_legislation_provision(self, id, provision):
        _const_id(id)
        want = _art_label(provision)
        for it in await _constitution():
            if it["kind"] == "article" and it["label"] == want:
                return Provision(law_id=CONST_ID, law_title=CONST_TITLE, provision=want,
                                 text=_art_md(it), url=CONST_URL)
        raise NotFound(f"{want} not in the Constitution (Articolul 1-156).")

    async def get_legislation_text(self, id):
        _const_id(id)
        parts = [f"## {it['title']}" if it["kind"] == "heading" else _art_md(it)
                 for it in await _constitution()]
        return LawText(id=CONST_ID, title=CONST_TITLE, text="\n\n".join(parts), url=CONST_URL,
                       metadata={"Note": "Text as published on cdep.ro (not official; the official "
                                         "text is Monitorul Oficial nr. 767/2003)"})
