"""Armenia: legislation and Court of Cassation decisions from ARLIS (www.arlis.am), the
unified website for the official publication of legal acts, run by the Ministry of
Justice's "Official Bulletin" (Pashtonakan Teghekagir) CJSC.

Gotchas this code encodes (verified 2026-11-06 from a UK IP):
  * www.arlis.am has no robots.txt (it redirects to a 404 page) and publishes no terms of
    use; the footer only says "© ... All rights reserved".
  * Search is a JSON endpoint behind the site's own search page:
    /hy/search/page/{n}?{url-encoded JSON of the form fields}&order_by=
    with header X-Requested-With: XMLHttpRequest. It returns {"status", "html"}; the HTML
    holds 10 result cards per page and the total in a `result_count` script.
    text_filter 1 = title only, 2 = title and text. catalog_id 4 = Court of Cassation
    decisions, 3 = ECHR judgments (Armenian translations).
  * An act's id is ARLIS's numeric id; /hy/acts/{id}/latest is the current version. A base
    act id (Civil Code = 29) shows the latest official incorporation (consolidated text);
    search may also return the id of an incorporation itself (e.g. 230025).
  * Unknown ids redirect to /hy/error/404.
  * Act pages are old Word-made HTML (upper-case tags). Article headings are two-cell
    tables ("Հոդված 1." | title), flattened here into one paragraph. Inserted articles are
    either "Հոդված 59.1." or "Հոդված 204<sup>1</sup>" (kept as "204¹").
  * Court of Cassation decisions carry no number field; the case number is in the title
    ("... ԳՈՐԾ ԹԻՎ 3-1920 (ՎԴ)-Ի ՄԱՍԻՆ").
"""
from __future__ import annotations

import json
import re
from urllib.parse import quote

import lxml.html

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

ARLIS = "https://www.arlis.am"
PAGE_SIZE = 10  # fixed by ARLIS
MAX_LIMIT = 100  # 11 source pages at 1 s spacing, ~20 s

_SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
_COURTS = {"cassation": 4, "echr": 3}
_STATUS = {"in_force": "1", "not_in_force": "2", "suspended": "3", "partly_in_force": "4"}
_ANY = "any"

# "Հոդված 5.", "Հոդված 59.1.", "Հոդված 204¹."
_ART = re.compile(r"^Հոդված\s*(\d+(?:\.\d+)*[⁰¹²³⁴⁵⁶⁷⁸⁹]*)(?=[\s.:]|$)")
# Section / subsection / chapter / paragraph headings (spaced letters removed first).
_HEAD = re.compile(r"^(?:\S*?(ԵՆԹԱԲԱԺԻՆ|ԲԱԺԻՆ)\d*|(ԳԼՈՒԽ)\d*\S*|(§).*)$")
_HEAD_LEVEL = {"ԲԱԺԻՆ": 0, "ԵՆԹԱԲԱԺԻՆ": 1, "ԳԼՈՒԽ": 2, "§": 3}

_docs: dict = {}


def _act_url(num: str) -> str:
    return f"{ARLIS}/hy/acts/{num}/latest"


def _parse_id(raw) -> str:
    """'29', 'arlis:29' or an arlis.am act URL -> '29'."""
    s = str(raw or "").strip()
    m = re.search(r"arlis\.am/(?:\w\w/)?acts/(\d+)", s) or re.fullmatch(r"(?:arlis:)?(\d+)", s, re.I)
    if not m:
        raise BadRequest(f"Bad ARLIS id {raw!r}: use the numeric act id from a search, e.g. "
                         "'29' (Civil Code) or '163951' (a Court of Cassation decision).")
    return m[1]


async def _get(url: str, **kw) -> str:
    r = await _http.get(url, **kw)
    if r.status_code == 404 or "/error/404" in str(r.url):
        raise NotFound("ARLIS has no such act (it answered with its 404 page).")
    if r.status_code != 200:
        raise SourceError(_http.error("ARLIS", "request failed", r.status_code), r.status_code)
    return r.text


# --------------------------------------------------------------------------- #
# Search
# --------------------------------------------------------------------------- #
def _card_fields(card: str) -> dict:
    out = {}
    for lab, val in re.findall(r'act-card__about-title[^>]*>(.*?)</div>\s*<div class="act-card__'
                               r'(?:about-value|status)[^>]*>(.*?)</div>', card, re.S):
        out[_http.clean(lab).rstrip("`'՝ ")] = _http.clean(re.sub(r"<[^>]+>", " ", val))
    return out


async def _search_page(form: dict, page: int, order: str = "") -> tuple[list[dict], int | None]:
    blob = quote(json.dumps(form, ensure_ascii=False, separators=(",", ":")))
    r = await _http.get(f"{ARLIS}/hy/search/page/{page}?{blob}&order_by={quote(order)}",
                        headers={"X-Requested-With": "XMLHttpRequest",
                                 "Accept": "application/json"})
    if r.status_code != 200:
        raise SourceError(_http.error("ARLIS", "search failed", r.status_code), r.status_code)
    try:
        js = r.json()
    except ValueError:
        raise SourceError("ARLIS: search answer is not JSON (blocked or changed?)", 200) from None
    if js.get("status") == -1:
        raise SourceError(f"ARLIS refused the search: {_http.clean(js.get('message'))[:200]}", 200)
    html = js.get("html") or ""
    m = re.search(r"result_count'\)\.innerHTML = `\(<b>\$\{(\d+)\}", html)
    total = int(m[1]) if m else (0 if "act-card" not in html else None)
    hits = []
    for card in re.split(r'<div class="act-card\s', html)[1:]:
        a = re.search(r'<a href="/\w+/acts/(\d+)/latest"[^>]*>\s*<span[^>]*>(.*?)</span>', card, re.S)
        if not a:
            continue
        hits.append({"id": a[1], "title": _http.clean(re.sub(r"<[^>]+>", "", a[2])),
                     **_card_fields(card)})
    return hits, total


async def _search(form: dict, limit: int, page: int, order: str = "") -> tuple[list[dict], int | None]:
    """ARLIS pages are 10 long; fetch the source pages covering hits (page-1)*limit+1 .. page*limit."""
    limit = int(limit or PAGE_SIZE)
    if limit > MAX_LIMIT:
        raise BadRequest(f"limit {limit}: ARLIS serves 10 results per request; use limit <= {MAX_LIMIT} "
                         "and the page parameter for more.")
    limit = max(1, limit)
    start = (max(1, int(page or 1)) - 1) * limit
    first, last = start // PAGE_SIZE + 1, (start + limit - 1) // PAGE_SIZE + 1
    hits, total = await _search_page(form, first, order)
    for src in range(first + 1, last + 1):
        if len(hits) < (src - first) * PAGE_SIZE or (total is not None and total <= (src - 1) * PAGE_SIZE):
            break
        more, _ = await _search_page(form, src, order)
        hits += more
    off = start % PAGE_SIZE
    return hits[off:off + limit], total


def _base_form(query: str, filters: dict, fulltext_default: bool) -> dict:
    form: dict = {}
    q = _http.clean(query)
    if len(q) > 200:
        raise BadRequest("ARLIS accepts at most 200 characters of search text.")
    ft = str(filters.get("fulltext", "true" if fulltext_default else "false")).lower()
    if ft not in ("true", "false"):
        raise BadRequest("fulltext: use 'true' (title and text) or 'false' (title only).")
    if q:
        form["simple_text"] = q
        form["text_filter"] = "2" if ft == "true" else "1"
    if filters.get("year"):
        y = str(filters["year"]).strip()
        if not re.fullmatch(r"\d{4}", y):
            raise BadRequest(f"year {y!r}: use a 4-digit year, e.g. '2018'.")
        form["year"] = y
    dates = {}
    for key, name in (("date_from", "start"), ("date_to", "end")):
        if filters.get(key):
            d = str(filters[key]).strip()
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
                raise BadRequest(f"{key} {d!r}: use YYYY-MM-DD, e.g. '2022-01-01'.")
            dates[name] = d
    if dates:
        form["enactment_date"] = json.dumps({"start": "", "end": "", **dates})
    return form


def _order(filters: dict) -> str:
    s = str(filters.get("sort", "oldest")).lower()
    if s not in ("oldest", "newest"):
        raise BadRequest("sort: use 'oldest' (ARLIS default order) or 'newest' (by date, newest first).")
    return "enactment_date DESC" if s == "newest" else ""


def _case_number(title: str) -> str:
    m = re.search(r"ԳՈՐԾ\s+ԹԻՎ\s+(.+?)(?:\s*-\s*Ի)?\s+ՄԱՍԻՆ\s*$", title)
    return _http.clean(m[1]) if m else ""


# --------------------------------------------------------------------------- #
# Act pages
# --------------------------------------------------------------------------- #
def _flatten_heading_tables(root) -> None:
    """Two-cell article heading tables -> one paragraph '**Հոդված 1. title**'."""
    for table in root.xpath("//table"):
        rows = table.xpath(".//tr")
        if len(rows) != 1:
            continue
        cells = [_http.clean(td.text_content()) for td in rows[0].xpath("./td")]
        cells = [c for c in cells if c]
        if cells and cells[0].startswith("Հոդված"):
            p = lxml.html.Element("p")
            strong = lxml.html.Element("strong")
            strong.text = " ".join(cells)
            p.append(strong)
            table.getparent().replace(table, p)


async def _doc(num: str) -> dict:
    if num in _docs:
        return _docs[num]
    html = await _get(_act_url(num))
    if 'id="act_body"' not in html:
        raise SourceError("ARLIS: act page without a body (layout changed or blocked?)", 200)
    info = {}
    for lab, val in re.findall(r'act-info__label[^>]*>(.*?)</div>\s*<div class="act-info__value'
                               r'[^>]*>(.*?)</div>', html, re.S):
        info[_http.clean(lab)] = _http.clean(re.sub(r"<[^>]+>", " ", val))
    t = re.search(r'act-info__title[^>]*>(.*?)</div>', html, re.S) or \
        re.search(r"<title>(.*?)</title>", html, re.S)
    title = _http.clean(re.sub(r"<[^>]+>", "", t[1])) if t else f"ARLIS {num}"
    i = html.find('id="act_body"')
    j = html.find('id="act_sidebar"', i)
    body = html[html.find(">", i) + 1:j if j > 0 else None]
    body = re.sub(r"(?is)<sup>(?:\s|<[^>]+>)*(\d+)(?:\s|<[^>]+>)*</sup>",
                  lambda x: x[1].translate(_SUP), body)
    root = lxml.html.fromstring(f"<div>{body}</div>")
    for a in root.xpath("//a[contains(@href, '/acts/files/')]"):
        a.drop_tree()  # "⚖" links to related decisions and the "contents" link
    _flatten_heading_tables(root)
    paras = _http.html_paragraphs(lxml.html.tostring(root, encoding="unicode"))
    paras = [re.sub(r"\*{4,}", "**", p) for p in paras if _http.clean(p.replace("*", ""))]
    st = info.get("Կարգավիճակ", "")
    doc = {"id": num, "title": title, "url": _act_url(num), "paras": paras, "info": info,
           "status": st}
    doc["entries"], doc["spans"] = _structure(paras)
    return _http.lru_put(_docs, num, doc, 3)


def _plain(p: str) -> str:
    return _http.clean(p.replace("*", ""))


def _structure(paras: list[str]) -> tuple[list[TocEntry], dict[str, tuple[int, int]]]:
    entries: list[TocEntry] = []
    spans: dict[str, tuple[int, int]] = {}
    open_label, open_start, level = None, 0, -1
    i = 0

    def close(end):
        if open_label:
            spans[open_label] = (open_start, end)

    while i < len(paras):
        p = _plain(paras[i])
        bold = paras[i].lstrip().startswith("**")
        art = _ART.match(p)
        head = None
        if not art and bold and len(p) < 200:
            head = _HEAD.match(re.sub(r"(?<=\w) (?=\w)", "", p.split(".")[0]) if not p.startswith("§")
                               else p)
        if art:
            close(i)
            label = f"Հոդված {art[1]}"
            n = 2
            while label in spans or label == open_label:
                label, n = f"Հոդված {art[1]} ({n})", n + 1
            open_label, open_start = label, i
            entries.append(TocEntry(title=p, level=level + 1, provision=label))
        elif head:
            close(i)
            open_label = None
            kind = head[1] or head[2] or head[3]
            level = _HEAD_LEVEL[kind]
            title = p
            while i + 1 < len(paras):
                nxt = _plain(paras[i + 1])
                if (paras[i + 1].lstrip().startswith("**") and len(nxt) < 200
                        and not _ART.match(nxt) and kind != "§"
                        and not _HEAD.match(re.sub(r"(?<=\w) (?=\w)", "", nxt.split(".")[0]))):
                    title, i = f"{title}. {nxt}", i + 1
                else:
                    break
            entries.append(TocEntry(title=title, level=level))
        i += 1
    close(len(paras))
    return entries, spans


def _norm_provision(raw: str) -> str:
    """'Հոդված 5', 'Article 5', 'art. 59.1', '204^1', '204¹' -> '5' / '59.1' / '204¹'."""
    s = _http.clean(raw).lower()
    s = re.sub(r"^(հոդված|հոդ\.?|article|art\.?|статья|ст\.?)\s*", "", s)
    m = re.fullmatch(r"(\d+(?:\.\d+)*)\s*(?:\^\s*(\d+)|([⁰¹²³⁴⁵⁶⁷⁸⁹]+))?\.?", s)
    if not m:
        raise BadRequest(f"Bad provision {raw!r}: use an article number such as 'Հոդված 5', "
                         "'5', '59.1', or '204¹' / '204^1' for superscript-numbered articles.")
    return m[1] + ((m[2] or "").translate(_SUP) or m[3] or "")


def _find_label(doc: dict, raw: str) -> str:
    if doc["id"] == _NEW_CONSTITUTION and "(" not in raw:
        # the Constitution's own text follows the amending articles of the adopting act
        n = _norm_provision(raw)
        if f"Հոդված {n} (2)" in doc["spans"]:
            return f"Հոդված {n} (2)"
    if raw in doc["spans"]:
        return raw
    if "(" in raw and f"Հոդված {raw}" in doc["spans"]:  # '1 (2)'
        return f"Հոդված {raw}"
    num = _norm_provision(raw)
    for label in doc["spans"]:
        if label.split(" ", 1)[1] == num:
            return label
    raise NotFound(f"{doc['title']} ({doc['id']}) has no article {raw!r}. "
                   "Use get_legislation_toc to see the article labels.")


# ARLIS still flags these two as in force; they were replaced by the 2015 Constitution.
_OLD_CONSTITUTIONS = {"1": "1995", "75780": "2005"}
_NEW_CONSTITUTION = "143723"
_OLD_NOTE = ("Superseded: this is the {y} Constitution text. ARLIS still flags it as in force, "
             "but the Constitution now in force is the 2015 one (ID 143723, an adopting act "
             "that quotes the new text; its articles follow the amending articles, so the "
             "Constitution's own Article 1 is 'Հոդված 1 (2)').")


def _as_of(doc: dict) -> str:
    m = re.search(r"\((\d{2}\.\d{2}\.\d{4})-", doc["status"])
    return _http.iso_date(m[1]) if m else ""


class Armenia(Jurisdiction):
    code = "am"
    name = "Armenia"
    languages = ("hy",)
    aliases = ("armenia", "hayastan", "Հայաստան")
    sources = (
        Source(
            name="ARLIS, Armenian Legal Information System (unified official publication "
                 "website; Ministry of Justice / Official Bulletin CJSC)",
            url="https://www.arlis.am",
            covers=("legislation", "caselaw"),
            licence="no licence or terms published (footer: '© All rights reserved'); the texts "
                    "are official documents, which Copyright Law HO-142-N art. 4(1)(c) excludes "
                    "from copyright",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~25 requests (2026-11)",
            terms_url="https://www.arlis.am/hy/about",
        ),
    )
    caselaw_filters = {
        "court": "'cassation' (Court of Cassation decisions, default) or 'echr' "
                 "(ECtHR judgments in Armenian, as published in ARLIS)",
        "year": "year of the decision, e.g. '2015'",
        "date_from": "decisions on or after this date, YYYY-MM-DD (e.g. '2022-01-01' for 'since 2022')",
        "date_to": "decisions on or before this date, YYYY-MM-DD",
        "sort": "'oldest' (default: ARLIS returns oldest decisions first) or 'newest' (newest first)",
        "fulltext": "'true' (default: search title and text) or 'false' (title only)",
    }
    legislation_filters = {
        "status": "'in_force', 'not_in_force', 'suspended', 'partly_in_force' or 'any'. Default: "
                  "'in_force' for a text search (repealed acts hidden); use 'any' to include repealed ones. "
                  "Not applied when year, date or number filters are given",
        "year": "year of adoption, e.g. '1998'",
        "date_from": "acts adopted on or after this date, YYYY-MM-DD",
        "date_to": "acts adopted on or before this date, YYYY-MM-DD",
        "sort": "'oldest' (default: ARLIS order) or 'newest' (newest first)",
        "number": "official act number, e.g. 'ՀՕ-239'",
        "fulltext": "'true' to search the text too (default: titles only)",
    }
    min_interval = {"www.arlis.am": 1.0}
    notes = ("Armenian-language texts from ARLIS, the official publication site. Case law is "
             "the Court of Cassation decisions ARLIS publishes, not every court, plus ARLIS's "
             "Armenian translations of ECtHR judgments (court=echr).")
    gaps = (
        "Lower-court decisions (datalex.am): site times out from the UK (2026-11)",
        "Constitutional Court decisions: not researched yet",
    )
    samples = {
        "caselaw_query": "վարձակալության",
        "decision_id": "163951",
        "legislation_query": "քաղաքացիական օրենսգիրք",
        "law_id": "29",
        "provision": "Հոդված 1",
    }

    # ---------------------------------------------------------------- case law
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        court = str(filters.get("court", "cassation")).lower()
        if court not in _COURTS:
            raise BadRequest(f"court {court!r}: use 'cassation' or 'echr'.")
        form = _base_form(query, filters, fulltext_default=True)
        form["catalog_id"] = _COURTS[court]
        order = _order(filters)
        hits, total = await _search(form, limit, page, order)
        items = []
        for h in hits:
            items.append(DecisionHit(
                id=h["id"], title=h["title"],
                court="Վճռաբեկ դատարան" if court == "cassation" else "ՄԻԵԴ",
                date=_http.iso_date(h.get("Ընդունման ամսաթիվ", "")),
                case_number=_case_number(h["title"]) if court == "cassation" else "",
                url=_act_url(h["id"])))
        return Results(items=items, total=total,
                       note="ARLIS holds selected Court of Cassation decisions (Armenian), "
                            "not all court rulings." + ("" if order else " Results come oldest first; use "
                            "filters sort='newest' and date_from/date_to (YYYY-MM-DD) for "
                            "recent decisions."))

    async def get_decision(self, id):
        num = _parse_id(id)
        doc = await _doc(num)
        info = doc["info"]
        meta = {k: v for k, v in info.items() if v}
        return Decision(
            id=num, title=doc["title"], text="\n\n".join(doc["paras"]), url=doc["url"],
            court=info.get("Ընդունող մարմին", ""),
            date=_http.iso_date(info.get("Ընդունման ամսաթիվ", "")),
            case_number=_case_number(doc["title"]), metadata=meta)

    # ------------------------------------------------------------- legislation
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        form = _base_form(query, filters, fulltext_default=False)
        st = str(filters.get("status") or "").lower()
        if st and st != _ANY and st not in _STATUS:
            raise BadRequest(f"status {st!r}: use one of {', '.join(_STATUS)}, {_ANY}.")
        if not st and form.get("simple_text") and not any(
                filters.get(k) for k in ("year", "date_from", "date_to", "number")):
            st = "in_force"  # ARLIS lists repealed acts first; a lawyer wants the law in force
        if st in _STATUS:
            form["status"] = _STATUS[st]
        if filters.get("number"):
            n = _http.clean(filters["number"])
            if len(n) > 20:
                raise BadRequest("number: at most 20 characters, e.g. 'ՀՕ-239'.")
            form["number"] = n
        if not form:
            raise BadRequest("Give search text or a filter (year, date_from, date_to, number, status).")
        hits, total = await _search(form, limit, page, _order(filters))
        if st == "in_force":  # ARLIS still flags the two replaced Constitutions as in force
            hits = [h for h in hits if h["id"] not in _OLD_CONSTITUTIONS]
        items = [LawHit(id=h["id"], title=h["title"], number=h.get("Ակտի համար", ""),
                        date=_http.iso_date(h.get("Ընդունման ամսաթիվ", "")),
                        status=h.get("Կարգավիճակ", "")
                        + (f" [superseded: {_OLD_CONSTITUTIONS[h['id']]} Constitution, replaced by "
                           "the 2015 one, ID 143723]" if h["id"] in _OLD_CONSTITUTIONS else ""),
                        url=_act_url(h["id"]))
                 for h in hits]
        note = ""
        if st == "in_force" and not filters.get("status"):
            note = ("Showing acts ARLIS flags as in force only; repealed acts are hidden "
                    "(filters status='any' to include them). ")
        if any(h["id"] in _OLD_CONSTITUTIONS or h["id"] == _NEW_CONSTITUTION for h in hits):
            note += ("Constitution: ARLIS still flags the 1995 (ID 1) and 2005 (ID 75780) texts as in "
                     "force; they were replaced by the 2015 Constitution (ID 143723), so they are "
                     "dropped with status='in_force' and marked superseded otherwise. ")
        return Results(items=items, total=total,
                       note=(note + "Status is ARLIS's own flag; an older text that a later act "
                             "replaced can still read 'in force'. Check the newest act on the subject."))

    async def get_legislation_toc(self, id):
        doc = await _doc(_parse_id(id))
        return Toc(id=doc["id"], title=doc["title"], url=doc["url"], entries=doc["entries"])

    async def get_legislation_provision(self, id, provision):
        doc = await _doc(_parse_id(id))
        label = _find_label(doc, provision)
        a, b = doc["spans"][label]
        text = "\n\n".join(doc["paras"][a:b])
        if doc["id"] != _NEW_CONSTITUTION and f"{label} (2)" in doc["spans"]:
            text = (f"_Note: this act has two articles numbered '{label}'. This is the first "
                    "(the act's own). The quoted text's article is "
                    f"'{label} (2)'; see get_legislation_toc._\n\n" + text)
        return Provision(law_id=doc["id"], law_title=doc["title"], provision=label,
                         text=text, url=doc["url"], as_of=_as_of(doc))

    async def get_legislation_text(self, id):
        doc = await _doc(_parse_id(id))
        meta = {k: v for k, v in doc["info"].items() if v}
        if doc["id"] in _OLD_CONSTITUTIONS:
            meta["Note"] = _OLD_NOTE.format(y=_OLD_CONSTITUTIONS[doc["id"]])
        return LawText(id=doc["id"], title=doc["title"], text="\n\n".join(doc["paras"]),
                       url=doc["url"], as_of=_as_of(doc), metadata=meta)
