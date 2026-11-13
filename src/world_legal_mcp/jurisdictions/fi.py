"""Finland: consolidated legislation from the Finlex open data API, KKO/KHO precedents
from the Finlex website.

Gotchas this code encodes:
  * Legislation: Finlex avoin data REST API (opendata.finlex.fi), Akoma Ntoso XML, keyless,
    CC BY 4.0. Every request must send a User-Agent (we send the project's own).
    `act/statute-consolidated/{year}/{number}/{lang}@latest/main.akn` returns the current
    consolidated text as a ZIP (about 10x smaller than the XML route); we unzip in memory.
  * Pre-1930s numbers carry a suffix: Rikoslaki is 1889/39-001 (39-087, 39-101 are other
    acts from the same issue). Our id is "number/year" as Finns cite it ("39-001/1889",
    "731/1999"); a bare "39/1889" resolves to the lowest suffix. "/swe" on the id selects
    the Swedish text (e.g. "39-001/1889/swe").
  * Search: the list route returns only URIs, so we use the non-list route, which returns
    whole AKN documents (titles included) for `titleContains`. Title substring match only,
    no full text, no relevance order; max 10 per API page.
  * Paging: Finlex announced that `page` paging is replaced by keyset paging
    (`lastSeen=/akn/fi/...`) in week 47/2026. If `page` is rejected we fall back to
    walking pages with `lastSeen` (see _api_page).
  * Consolidated texts can hold two versions of a section: an amendment not yet in force,
    then an authorial note ("... tulee voimaan 1.3.2028. Aiempi sanamuoto kuuluu:") and
    the wording in force. We return both, in source order, with the note.
  * Case law is NOT in the open data API or ZIPs (every judgment type 404s). KKO and KHO
    precedents are read from www.finlex.fi, a Next.js site: the page HTML has no body, the
    text is in the React Server Components payload (self.__next_f.push). _rsc_rows /
    _rsc_html turn that tree back into HTML. Search = keyword match on the yearly
    precedent lists (asiasanat), not full text.
"""
from __future__ import annotations

import datetime
import io
import json
import re
import time
import zipfile
from html import escape

import lxml.html
from lxml import etree

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

API = "https://opendata.finlex.fi/finlex/avoindata/v1/akn/fi"
WEB = "https://www.finlex.fi"
AKN = "{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}"
FINLEX = "{http://data.finlex.fi/schema/finlex}"

_COURTS = {"KKO": ("korkein-oikeus", "Korkein oikeus"),
           "KHO": ("korkein-hallinto-oikeus", "Korkein hallinto-oikeus")}
_LANGS = {"fin": ("fi", "lainsaadanto"), "swe": ("sv", "lagstiftning")}


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #
async def _get(url: str, what: str, **kw):
    try:
        r = await _http.get(url, **kw)
    except Exception as e:  # network error
        raise SourceError(f"{what}: {e}", "network") from e
    if r.status_code == 404:
        raise NotFound(f"{what}: not found")
    if r.status_code != 200:
        raise SourceError(f"{what} failed", r.status_code)
    return r


# --------------------------------------------------------------------------- #
# Legislation
# --------------------------------------------------------------------------- #
_ID = re.compile(r"^\s*(\d+)(?:-(\d+))?\s*/\s*(\d{4})(?:\s*/\s*(fin|swe))?\s*$", re.I)
_ID_YF = re.compile(r"^\s*(\d{4})\s*/\s*(\d+)(?:-(\d+))?(?:\s*/\s*(fin|swe))?\s*$", re.I)


def _parse_id(law_id: str) -> tuple[str, str, str | None, str]:
    """-> (year, number, suffix or None, lang). Accepts '39-001/1889', '39/1889',
    '1889/39-001' (API order), optional '/swe'."""
    s = re.sub(r"^(sd|finlex)\s*", "", str(law_id or "").strip(), flags=re.I)
    m = _ID.match(s)
    if m and 1700 <= int(m[3]) <= 2100:
        return m[3], m[1], m[2], (m[4] or "fin").lower()
    m = _ID_YF.match(s)
    if m and 1700 <= int(m[1]) <= 2100:
        return m[1], m[2], m[3], (m[4] or "fin").lower()
    raise BadRequest(f"bad law id {law_id!r}: use number/year as Finlex cites it, e.g. "
                     "'39-001/1889' (Rikoslaki), '731/1999'; add '/swe' for Swedish")


def _make_id(year: str, num: str, lang: str) -> str:
    return f"{num}/{year}" + ("/swe" if lang == "swe" else "")


def _web_url(year: str, num: str, lang: str) -> str:
    loc, path = _LANGS[lang]
    return f"{WEB}/{loc}/{path}/{year}/{num}"


def _xml(data: bytes, what: str):
    try:
        return etree.fromstring(data, parser=etree.XMLParser(huge_tree=True, recover=True))
    except etree.XMLSyntaxError as e:
        raise SourceError(f"{what}: unparseable XML", "xml") from e


def _meta(act) -> dict:
    """Title, number, dates, type and status from an AKN <act>."""
    def frbr(name):
        el = act.find(f".//{AKN}FRBRWork/{AKN}FRBRdate[@name='{name}']")
        return el.get("date", "") if el is not None else ""
    uri = act.find(f".//{AKN}FRBRWork/{AKN}FRBRuri")
    path = uri.get("value", "") if uri is not None else ""
    lang_el = act.find(f".//{AKN}FRBRExpression/{AKN}FRBRlanguage")
    cons = act.find(f".//{AKN}FRBRExpression/{AKN}FRBRdate[@name='dateConsolidated']")
    typ = act.find(f".//{AKN}references/{AKN}TLCConcept[@eId='act']")
    if typ is None:
        typ = next((c for c in act.iter(f"{AKN}TLCConcept")
                    if "type-statute" in c.get("href", "")), None)
    force = act.find(f".//{FINLEX}isInForce")
    status = ""
    if force is not None:
        status = "in force" if force.get("value") == "true" else "not in force"
    m = re.search(r"/(\d{4})/([\w-]+)$", path)
    return {"year": m[1] if m else "", "num": m[2] if m else "",
            "lang": lang_el.get("language", "fin") if lang_el is not None else "fin",
            "title": _http.text(act.find(f".//{AKN}preface//{AKN}docTitle")),
            "date": frbr("dateIssued") or "",
            "as_of": cons.get("date", "") if cons is not None else "",
            "type": typ.get("showAs", "") if typ is not None else "",
            "status": status}


async def _law_zip(year: str, num: str, lang: str) -> bytes:
    url = f"{API}/act/statute-consolidated/{year}/{num}/{lang}%40latest/main.akn"
    r = await _get(url, f"Finlex {num}/{year}")
    try:
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            name = "main.xml" if "main.xml" in z.namelist() else next(
                n for n in z.namelist() if n.endswith(".xml"))
            return z.read(name)
    except (zipfile.BadZipFile, StopIteration) as e:
        raise SourceError(f"Finlex {num}/{year}: unexpected payload (not an AKN zip)",
                          r.status_code) from e


async def _api_page(route: str, params: dict, api_page: int, limit: int, what: str):
    """One API page. Uses `page`; if the API rejects it (keyset paging, announced for
    week 47/2026), walks the light JSON list route with `lastSeen` instead."""
    r = await _http.get(f"{API}/{route}", params={**params, "page": api_page, "limit": limit})
    if r.status_code == 200:
        return r
    if r.status_code == 404:
        raise NotFound(f"{what}: not found")
    if r.status_code != 400:
        raise SourceError(f"{what} failed", r.status_code)
    last = None
    for _ in range(api_page - 1):  # keyset fallback: find the last uri of the previous page
        q = {**params, "limit": limit, "format": "json", **({"lastSeen": last} if last else {})}
        lr = await _get(f"{API}/{route}/list", what, params=q)
        items = lr.json() or []
        if not items:
            return None
        last = re.sub(r"^https?://[^/]+/finlex/avoindata/v1", "", items[-1]["akn_uri"])
    q = {**params, "limit": limit, **({"lastSeen": last} if last else {})}
    return await _get(f"{API}/{route}", what, params=q)


async def _resolve(year: str, num: str, suffix: str | None, lang: str) -> tuple[str, bytes]:
    """-> (number with suffix, AKN xml). A bare old number tries the lowest suffix."""
    if suffix is not None:
        return f"{num}-{suffix}", await _law_zip(year, f"{num}-{suffix}", lang)
    try:
        return num, await _law_zip(year, num, lang)
    except NotFound:
        pass
    found: list[str] = []
    for page in range(1, 21):  # old years have few consolidated acts; stay gentle
        r = await _get(f"{API}/act/statute-consolidated/list", f"Finlex list {year}",
                       params={"format": "json", "limit": 10, "page": page, "startYear": year,
                               "endYear": year, "langAndVersion": f"{lang}@latest"})
        items = r.json() or []
        for it in items:
            m = re.search(rf"/{year}/({num}-\d+)/", it.get("akn_uri", ""))
            if m:
                found.append(m[1])
        if len(items) < 10:
            break
    if not found:
        raise NotFound(f"no consolidated act {num}/{year} in Finlex")
    best = min(found, key=lambda n: int(n.split("-")[1]))
    return best, await _law_zip(year, best, lang)


class _Node:
    """A provision found in the body: label, xml element, heading level."""
    __slots__ = ("label", "el", "level", "title")

    def __init__(self, label, el, level, title):
        self.label, self.el, self.level, self.title = label, el, level, title


def _num_heading(el) -> tuple[str, str]:
    num = el.find(f"{AKN}num")
    head = el.find(f"{AKN}heading")
    n = _http.clean(_http.text(num))
    h = re.sub(r"\s*\(\d{1,2}\.\d{1,2}\.\d{4}/\d+\)\s*$", "", _http.text(head))
    return n, _http.clean(h)


def _walk(body) -> list[_Node]:
    """Chapters and sections in document order, with labels like '3 luku 1 §'."""
    out: list[_Node] = []

    def rec(el, chapter: str, depth: int):
        for c in el:
            name = _http.localname(c)
            if name in ("part", "title", "book"):
                n, h = _num_heading(c)
                out.append(_Node("", c, depth, " ".join(x for x in (n, h) if x)))
                rec(c, chapter, depth + 1)
            elif name == "chapter":
                n, h = _num_heading(c)
                out.append(_Node(n, c, depth, " ".join(x for x in (n, h) if x)))
                rec(c, n, depth + 1)
            elif name == "section":
                n, h = _num_heading(c)
                label = f"{chapter} {n}".strip()
                out.append(_Node(label, c, depth, f"{n} {h}".strip()))
            elif name == "hcontainer" and c.get("name") in ("statuteProvisionsWrapper",):
                rec(c, chapter, depth)
            elif name not in ("hcontainer",):
                rec(c, chapter, depth)
    rec(body, "", 0)
    return out


def _norm_label(s: str) -> tuple[str, str]:
    """'3:1', '3 luku 1 §', 'RL 3 luku 1§', '1 §', '§ 1', '2a', '3 luku' -> (chapter, section)."""
    s = str(s or "").strip().lower().replace("\xa0", " ")
    s = re.sub(r"^[a-zäöå]{1,6}\.?\s+(?=\d)", "", s)  # leading law abbreviation: 'RL 3:1'
    m = re.fullmatch(r"(\d+\s*[a-z]?)\s*(?::|luku|l\.|kap\.?|kapitlet)\s*(?:§\s*)?(\d+\s*[a-z]?)?\s*§?", s)
    if m:
        return m[1].replace(" ", ""), (m[2] or "").replace(" ", "")
    m = re.fullmatch(r"(?:§|pykälä|pyk\.)?\s*(\d+\s*[a-z]?)\s*(?:§|pykälä)?", s)
    if m:
        return "", m[1].replace(" ", "")
    raise BadRequest(f"bad provision {s!r}: use '3 luku 1 §' (or '3:1'), '1 §', or a chapter "
                     "'3 luku'")


def _label_key(label: str) -> tuple[str, str]:
    m = re.fullmatch(r"(?:(\d+\s*[a-z]?)\s*(?:luku|kap\.?))?\s*(?:(\d+\s*[a-z]?)\s*§)?",
                     label.lower())
    if not m:
        return ("?", label)
    return ((m[1] or "").replace(" ", ""), (m[2] or "").replace(" ", ""))


# --- AKN -> markdown -------------------------------------------------------- #
def _md(el, out: list[str], prefix: str = "") -> str:
    """Append markdown paragraphs for an AKN element; returns an unused prefix."""
    name = _http.localname(el)
    if name is None:
        return prefix
    if name in ("part", "title", "book", "chapter"):
        n, h = _num_heading(el)
        out.append(f"## {n} {h}".strip())
        for c in el:
            if _http.localname(c) not in ("num", "heading"):
                _md(c, out)
        return ""
    if name == "section":
        n, h = _num_heading(el)
        out.append(f"### {n} {h}".strip())
        for c in el:
            if _http.localname(c) not in ("num", "heading"):
                _md(c, out)
        return ""
    if name in ("paragraph", "subparagraph", "point", "item", "list"):
        num = el.find(f"{AKN}num")
        p = (prefix + " " + _http.text(num)).strip() if num is not None else prefix
        for c in el:
            if _http.localname(c) != "num":
                p = _md(c, out, p)
        return p
    if name == "hcontainer":
        head = el.find(f"{AKN}heading")
        if el.get("name") == "noteAuthorial":
            t = _http.text(el)
            if t:
                out.append(f"*{t}*")
            return prefix
        if head is not None and _http.text(head):
            out.append(f"#### {_http.text(head)}")
        for c in el:
            if _http.localname(c) != "heading":
                _md(c, out)
        return prefix
    if name == "crossHeading":
        out.append(f"#### {_http.text(el)}")
        return prefix
    if name == "table":
        rows = [[_http.text(td) for td in tr if _http.localname(td) in ("td", "th")]
                for tr in el.iter(f"{AKN}tr")]
        rows = [r for r in rows if r]
        if rows:
            w = max(len(r) for r in rows)
            rows = [r + [""] * (w - len(r)) for r in rows]
            lines = ["| " + " | ".join(c.replace("|", "/") for c in rows[0]) + " |",
                     "|" + " --- |" * w]
            lines += ["| " + " | ".join(c.replace("|", "/") for c in r) + " |" for r in rows[1:]]
            out.append("\n".join(lines))
        return prefix
    if name in ("p", "heading", "num", "docTitle"):
        t = _http.text(el)
        if t:
            out.append(f"{prefix} {t}".strip())
            return ""
        return prefix
    for c in el:
        prefix = _md(c, out, prefix)
    return prefix


def _to_md(*els) -> str:
    out: list[str] = []
    for el in els:
        _md(el, out)
    return "\n\n".join(p for p in out if p.strip())


# --------------------------------------------------------------------------- #
# Case law: Finlex website, React Server Components payload
# --------------------------------------------------------------------------- #
_RSC_PUSH = re.compile(r"self\.__next_f\.push\(\[1,(\".*?\")\]\)</script>", re.S)
_ROW = re.compile(r"([0-9a-f]+):")
_REF = re.compile(r"\$L?([0-9a-f]+)")


def _rsc_rows(page_html: str) -> dict:
    """Next.js flight payload -> {row id: parsed JSON}. Text rows ('T<hexlen>,') kept as str."""
    try:
        t = "".join(json.loads(c) for c in _RSC_PUSH.findall(page_html))
    except ValueError as e:
        raise SourceError("Finlex page: unreadable RSC payload", "rsc") from e
    rows, i = {}, 0
    while i < len(t):
        m = _ROW.match(t, i)
        if not m:
            j = t.find("\n", i)
            i = len(t) if j < 0 else j + 1
            continue
        rid, i = m[1], m.end()
        mt = re.compile(r"T([0-9a-f]+),").match(t, i)
        if mt:
            body = t[mt.end():].encode()[:int(mt[1], 16)].decode("utf-8", "ignore")
            rows[rid], i = body, mt.end() + len(body)
            continue
        j = t.find("\n", i)
        j = len(t) if j < 0 else j
        raw, i = t[i:j], j + 1
        try:
            rows[rid] = None if raw[:1] in "IHE" else json.loads(raw)
        except ValueError:
            rows[rid] = None
    return rows


def _rsc_html(node, rows: dict, depth: int = 0) -> str:
    """Render an RSC element tree to plain HTML (only real lower-case HTML tags kept)."""
    if depth > 300 or node is None or isinstance(node, bool):
        return ""
    if isinstance(node, (int, float)):
        return str(node)
    if isinstance(node, str):
        if node == "$undefined":
            return ""
        m = _REF.fullmatch(node)
        if m:
            return _rsc_html(rows.get(m[1]), rows, depth + 1)
        if node.startswith("$$"):
            node = node[1:]
        elif node.startswith("$"):
            return ""
        return escape(node)
    if isinstance(node, list):
        if len(node) == 4 and node[0] == "$" and isinstance(node[1], str):
            tag, props = node[1], node[3] if isinstance(node[3], dict) else {}
            inner = _rsc_html(props.get("children"), rows, depth + 1)
            if re.fullmatch(r"[a-z][a-z0-9]*", tag) and tag not in ("svg", "path", "button"):
                attr = f' datetime="{escape(props["dateTime"])}"' if props.get("dateTime") else ""
                return f"<{tag}{attr}>{inner}</{tag}>"
            return "" if tag in ("svg", "path") else inner
        return "".join(_rsc_html(x, rows, depth + 1) for x in node)
    return ""


def _rsc_find(rows: dict, pred) -> list:
    """All elements (in row order) satisfying pred(tag, props)."""
    found = []

    def rec(n, depth=0):
        if depth > 200:
            return
        if isinstance(n, list):
            if len(n) == 4 and n[0] == "$" and isinstance(n[1], str) and isinstance(n[3], dict):
                if pred(n[1], n[3]):
                    found.append(n)
                    return
                rec(n[3].get("children"), depth + 1)
                return
            for x in n:
                rec(x, depth + 1)
    for v in rows.values():
        rec(v)
    return found


def _cls(props, name: str) -> bool:
    return name in str(props.get("className") or "")


_DEC_ID = re.compile(r"^\s*(?:ECLI:FI:)?(KKO|KHO)\s*[:\s]\s*(\d{4})\s*[:\s]\s*(\d+)\s*$", re.I)
# Published decisions that are not precedents. Fontes ids (Finlex has no unique ECLI for
# them: KHO 'muut' and 'lyhyet' share the T-numbering): 'KKO:muut:2025:1424',
# 'KKO:VL:2026:258', 'KHO:muut:2025:3030', 'KHO:lyhyt:2021:H4774'. The Finlex titles
# 'KKO 1424/2025' and 'KKO VL:2026-258' are accepted too.
_KINDS = {"precedent": ("ennakkopaatokset", "", ("KKO", "KHO")),
          "other": ("muut-paatokset", "muut", ("KKO", "KHO")),
          "leave": ("valitusluvat", "VL", ("KKO",)),
          "short": ("lyhyet-ratkaisuselosteet", "lyhyt", ("KHO",))}
_TAG = {v[1].lower(): k for k, v in _KINDS.items() if v[1]}
_OTHER_ID = re.compile(r"^\s*(KKO|KHO)\s*:\s*(muut|VL|lyhyt)\s*:\s*(\d{4})\s*:\s*([A-Z]?\d+)\s*$", re.I)
_TITLE_ID = re.compile(r"^\s*KKO\s+(?:(\d+)/(\d{4})|VL\s*:\s*(\d{4})-(\d+))\s*$", re.I)


def _parse_dec(did: str) -> tuple[str, str, str, str]:
    """-> (court, year, num, kind)."""
    s = str(did or "")
    m = _DEC_ID.match(s)
    if m:
        return m[1].upper(), m[2], str(int(m[3])), "precedent"
    m = _OTHER_ID.match(s)
    if m:
        court, kind = m[1].upper(), _TAG[m[2].lower()]
        if court not in _KINDS[kind][2]:
            raise BadRequest(f"{s!r}: {court} has no '{m[2]}' decisions")
        num = m[4].upper()
        return court, m[3], num if num[0].isalpha() else str(int(num)), kind
    m = _TITLE_ID.match(s)
    if m:
        if m[1]:
            return "KKO", m[2], str(int(m[1])), "other"
        return "KKO", m[3], str(int(m[4])), "leave"
    raise BadRequest(f"bad decision id {did!r}: use 'ECLI:FI:KKO:2025:1' / 'KHO:2025:1' "
                     "(precedents), 'KKO:muut:2025:1424' or 'KHO:muut:2025:3030' (other "
                     "published decisions), 'KKO:VL:2026:258' (leave to appeal granted) or "
                     "'KHO:lyhyt:2021:H4774' (short summaries)")


def _fontes_id(court: str, year: str, num: str, kind: str) -> str:
    if kind == "precedent":
        return f"ECLI:FI:{court}:{year}:{num}"
    return f"{court}:{_KINDS[kind][1]}:{year}:{num}"


def _title_key(court: str, kind: str, title: str) -> tuple[str, str] | None:
    """Finlex list title -> (year, url number)."""
    if kind == "precedent":
        m = _DEC_ID.match(title)
        return (m[2], str(int(m[3]))) if m else None
    if kind == "leave":
        m = re.fullmatch(r"KKO\s+VL:(\d{4})-(\d+)", title)
        return (m[1], m[2]) if m else None
    if court == "KKO":
        m = re.fullmatch(r"KKO\s+(\d+)/(\d{4})", title)
        return (m[2], m[1]) if m else None
    m = re.fullmatch(r"KHO\s+\d{1,2}\.\d{1,2}\.(\d{4})/([A-Z]?\d+)", title)
    return (m[1], m[2]) if m else None


def _dec_url(court: str, year: str, num: str, kind: str = "precedent") -> str:
    return f"{WEB}/fi/oikeuskaytanto/{_COURTS[court][0]}/{_KINDS[kind][0]}/{year}/{num}"


_LIST_CACHE: dict = {}


async def _year_list(court: str, year: int, kind: str = "precedent") -> list[tuple[str, str, str]]:
    """[(Fontes id, Finlex title, keywords)] for one court-year-kind, newest first."""
    key = (court, year, kind)
    hit = _LIST_CACHE.get(key)
    current = year >= datetime.date.today().year
    if hit and (not current or time.time() - hit[0] < 6 * 3600):
        return hit[1]
    url = f"{WEB}/fi/oikeuskaytanto/{_COURTS[court][0]}/{_KINDS[kind][0]}/{year}"
    try:
        r = await _get(url, f"Finlex {court} {kind} {year} list")
    except NotFound:
        return _http.lru_put(_LIST_CACHE, key, (time.time(), []), 64)[1]
    rows = _rsc_rows(r.text)
    items = []
    for li in _rsc_find(rows, lambda t, p: t == "li" and _cls(p, "documentListItem")):
        frag = lxml.html.fragment_fromstring(_rsc_html(li, rows), create_parent="div")
        h3 = frag.find(".//h3")
        title = _http.clean(h3.text_content()) if h3 is not None else ""
        yn = _title_key(court, kind, title)
        if not yn:
            continue
        chips = [_http.clean(d.text_content()) for d in frag.xpath(".//div[span] | .//div[not(*)]")]
        items.append((_fontes_id(court, yn[0], yn[1], kind), title,
                      "; ".join(c for c in chips if c)))
    return _http.lru_put(_LIST_CACHE, key, (time.time(), items), 64)[1]


# --------------------------------------------------------------------------- #
class Finland(Jurisdiction):
    code = "fi"
    name = "Finland"
    languages = ("fi", "sv")
    aliases = ("finland", "suomi", "finland (sv)", "fin")
    sources = (
        Source(
            name="Finlex avoin data (Ministry of Justice / Legal Register Centre)",
            url="https://opendata.finlex.fi/finlex/avoindata/v1",
            covers=("legislation",),
            licence="CC BY 4.0 (Finlex FAQ); statutes themselves are public domain "
                    "(Copyright Act 404/1961 s. 9)",
            commercial_use=True,
            ai_use=None,
            auth="none",
            rate_limit=("not published: guide says volumes 'may be restricted', answered "
                        "with 429; no 429 in ~30 requests (2026-11-05); using 1 s spacing"),
            terms_url="https://www.finlex.fi/en/faq",
        ),
        Source(
            name="Finlex website (www.finlex.fi), KKO/KHO published decisions",
            url="https://www.finlex.fi/fi/oikeuskaytanto",
            covers=("caselaw",),
            licence="public, 'no restrictions on use' (Finlex FAQ); court decisions are "
                    "public domain (Copyright Act s. 9); no personal-data misuse",
            commercial_use=True,
            ai_use=None,
            auth="none",
            rate_limit="not published; no 429 in ~15 requests (2026-11-05); using 1 s spacing",
            terms_url="https://www.finlex.fi/en/faq",
        ),
    )
    caselaw_filters = {
        "court": "'KKO' (Supreme Court) or 'KHO' (Supreme Administrative Court); default both",
        "year": "decision year YYYY; default the last 3 years",
        "since": "first decision year YYYY of a range up to this year (one list fetch per "
                 "court and year, so wide ranges are slow); not with year",
        "kind": "'precedent' (default, ennakkopäätökset), 'other' (muut päätökset: KKO 1995-, "
                "KHO 2013-), 'leave' (KKO leave-to-appeal grants, 2025-), 'short' (KHO "
                "lyhyet ratkaisuselosteet, 1946-2021) or 'all'",
    }
    legislation_filters = {
        "language": "'fin' (default) or 'swe' (Swedish text)",
        "in_force": "'true' or 'false'",
        "year": "statute year YYYY",
    }
    min_interval = {"opendata.finlex.fi": 1.0, "www.finlex.fi": 1.0}
    notes = ("Consolidated legislation (Finnish, Swedish via '/swe' on the id) from the "
             "Finlex open data API; KKO/KHO published decisions from finlex.fi "
             "(precedents by default; filter kind= for other decisions, leave grants and "
             "short summaries). Ids: '39-001/1889', "
             "'ECLI:FI:KKO:2025:1', 'KKO:muut:2025:1424', 'KHO:lyhyt:2021:H4774'.")
    gaps = (
        "Other courts (courts of appeal, district, administrative and special courts): not researched yet",
        "KKO/KHO: Finlex publishes only selected decisions (precedents plus chosen 'other' "
        "decisions, KKO leave grants from 2025, KHO short summaries 1946-2021); unpublished "
        "decisions are not reachable. Search matches the list keywords, not full text; "
        "some KKO 'other' entries carry only a short summary",
        "Case law in the Finlex open data API: not published (every judgment type 404s); read from finlex.fi instead",
        "Original Statute Book texts, authority regulations and the Treaty Series: adapter queries consolidated statutes (statute-consolidated) only",
        "Åland legislation: not researched yet",
    )
    samples = {
        "caselaw_query": "vahingonkorvaus",
        "decision_id": "ECLI:FI:KKO:2025:1",
        "legislation_query": "rikoslaki",
        "law_id": "39-001/1889",
        "provision": "3 luku 1 §",
    }

    _laws: dict = {}

    # ---- case law --------------------------------------------------------- #
    async def search_caselaw(self, query, *, limit, page, filters):
        court = str(filters.get("court") or "").upper()
        if court and court not in _COURTS:
            raise BadRequest(f"court {court!r}: use 'KKO' or 'KHO'")
        kind = str(filters.get("kind") or "precedent").lower()
        if kind not in _KINDS and kind != "all":
            raise BadRequest(f"kind {kind!r}: use one of {', '.join(_KINDS)} or 'all'")
        this = datetime.date.today().year
        if filters.get("year"):
            if not re.fullmatch(r"\d{4}", str(filters["year"])) or not 1926 <= int(filters["year"]) <= this:
                raise BadRequest(f"year {filters['year']!r}: use YYYY, 1926-{this}")
            years = [int(filters["year"])]
        elif filters.get("since"):
            if not re.fullmatch(r"\d{4}", str(filters["since"])) or not 1926 <= int(filters["since"]) <= this:
                raise BadRequest(f"since {filters['since']!r}: use YYYY, 1926-{this}")
            years = list(range(this, int(filters["since"]) - 1, -1))
        else:
            years = [this, this - 1, this - 2]
        q = str(query or "").strip()
        want = None
        try:
            want = _parse_dec(q) if re.search(r"\d{4}", q) and re.match(r"\s*(ECLI|KKO|KHO)", q, re.I) else None
        except BadRequest:
            want = None
        if want:
            court, years, kind, q = want[0], [int(want[1])], want[3], ""
        kinds = list(_KINDS) if kind == "all" else [kind]
        words = [w for w in re.split(r"\s+", q.lower()) if w]
        hits = []
        for y in years:
            for c in ([court] if court else list(_COURTS)):
                for k in kinds:
                    if c not in _KINDS[k][2]:
                        continue
                    for fid, title, kw in await _year_list(c, y, k):
                        if want and fid != _fontes_id(*want):
                            continue
                        if all(w in f"{fid} {title} {kw}".lower() for w in words):
                            cc, yy, nn, kk = _parse_dec(fid)
                            hits.append(DecisionHit(
                                id=fid, title=title, court=_COURTS[cc][1],
                                case_number=title, snippet=kw[:300],
                                url=_dec_url(cc, yy, nn, kk)))
        n = max(1, int(limit))
        start = (max(1, int(page)) - 1) * n
        span = f"{years[-1]}–{years[0]}" if len(years) > 1 else str(years[0])
        return Results(items=hits[start:start + n], total=len(hits),
                       note=(f"Keyword (asiasana) match on the Finlex KKO/KHO lists ({kind}) for "
                             f"{span}, newest first; not full text. Use filter since=YYYY "
                             "(range up to this year) or year=YYYY for older years and kind= for non-precedent decisions (other: KKO "
                             "from 1995, KHO from 2013; leave: KKO from 2025; short: KHO "
                             "1946-2021)."))

    async def get_decision(self, id):
        court, year, num, kind = _parse_dec(id)
        url = _dec_url(court, year, num, kind)
        did = _fontes_id(court, year, num, kind)
        r = await _get(url, f"Finlex {did}")
        rows = _rsc_rows(r.text)
        arts = _rsc_find(rows, lambda t, p: t == "section" and _cls(p, "akomaNtoso"))
        art = next((a for a in arts if a[3].get("lang") == "fi"), arts[0] if arts else None)
        if art is None:
            raise SourceError(f"Finlex {did}: no decision text on the page",
                              r.status_code)
        text = _http.html_to_md(_rsc_html(art[3].get("children"), rows))
        if not text:
            raise NotFound(f"{did} has no published text (for older decisions Finlex "
                           "may have only the title/index text)")
        meta: dict[str, str] = {}
        for dl in _rsc_find(rows, lambda t, p: t == "dl" and _cls(p, "listContainer")):
            frag = lxml.html.fragment_fromstring(_rsc_html(dl, rows), create_parent="div")
            for dt in frag.iter("dt"):
                dd = dt.getnext()
                if dd is None or dd.tag != "dd":
                    continue
                k = _http.clean(dt.text_content())
                if k in meta:
                    continue
                if k == "Asiasanat":
                    v = "; ".join(_http.clean(d.text_content()) for d in dd.xpath("./div/div"))
                else:
                    t = dd.find(".//time")
                    v = t.get("datetime") if t is not None and t.get("datetime") else \
                        _http.clean(dd.text_content())
                meta[k] = v or _http.clean(dd.text_content())
        date = meta.get("Antopäivä", "")
        return Decision(
            id=did, title=did.removeprefix("ECLI:FI:"), text=text, url=url,
            court=_COURTS[court][1],
            date=date if re.fullmatch(r"\d{4}-\d{2}-\d{2}", date) else _http.iso_date(date),
            case_number=meta.get("Diaarinumero", ""),
            metadata={k: v for k, v in meta.items()
                      if k != "Antopäivä" and (kind != "precedent" or k != "ECLI-tunnus")})

    # ---- legislation ------------------------------------------------------ #
    async def search_legislation(self, query, *, limit, page, filters):
        lang = str(filters.get("language") or "fin").lower()
        if lang not in _LANGS:
            raise BadRequest(f"language {lang!r}: use 'fin' or 'swe'")
        params: dict = {"titleContains": str(query or "").strip(),
                        "langAndVersion": f"{lang}@latest"}
        if not params["titleContains"]:
            raise BadRequest("give a word from the statute title, e.g. 'rikoslaki'")
        if filters.get("in_force") not in (None, ""):
            v = str(filters["in_force"]).lower()
            if v not in ("true", "false"):
                raise BadRequest("in_force: use 'true' or 'false'")
            params["isInForce"] = v
        if filters.get("year"):
            if not re.fullmatch(r"\d{4}", str(filters["year"])):
                raise BadRequest(f"year {filters['year']!r}: use YYYY")
            params["startYear"] = params["endYear"] = str(filters["year"])
        n = min(max(1, int(limit)), 20)
        offset = (max(1, int(page)) - 1) * n
        acts = []
        for p in range(offset // 10 + 1, (offset + n - 1) // 10 + 2):
            r = await _api_page("act/statute-consolidated", params, p, 10, "Finlex search")
            if r is None:
                break
            root = _xml(r.content, "Finlex search")
            got = [a for a in root.iter(f"{AKN}act")]
            acts += [(p, i, a) for i, a in enumerate(got)]
            if len(got) < 10:
                break
        lo = offset % 10
        acts = acts[lo:lo + n]
        hits = []
        for _, _, a in acts:
            m = _meta(a)
            if not m["year"]:
                continue
            hits.append(LawHit(
                id=_make_id(m["year"], m["num"], lang), title=m["title"] or f"{m['num']}/{m['year']}",
                type=m["type"], number=f"{m['num'].split('-')[0]}/{m['year']}",
                date=m["date"], status=m["status"], url=_web_url(m["year"], m["num"], lang)))
        return Results(items=hits, total=None, note=(
            "Title substring match (Finlex titleContains), no relevance order, max 20 per "
            "page. Finnish text by default; filter language='swe' for Swedish."))

    async def _law(self, law_id: str):
        year, num, suffix, lang = _parse_id(law_id)
        key = (year, num, suffix, lang)
        if key in self._laws:
            return self._laws[key]
        full_num, data = await _resolve(year, num, suffix, lang)
        root = _xml(data, f"Finlex {law_id}")
        act = root if _http.localname(root) == "act" else root.find(f".//{AKN}act")
        body = act.find(f"{AKN}body") if act is not None else None
        if body is None:
            raise SourceError(f"Finlex {law_id}: no body in the AKN document", "xml")
        m = _meta(act)
        law = {"id": _make_id(year, full_num, lang), "title": m["title"] or f"{full_num}/{year}",
               "url": _web_url(year, full_num, lang), "as_of": m["as_of"], "meta": m,
               "body": body, "nodes": _walk(body)}
        if "-" in full_num:  # '39/1889' and '39-001/1889' share one cached copy
            n, sfx = full_num.split("-", 1)
            _http.lru_put(self._laws, (year, n, sfx, lang), law, 8)
        return _http.lru_put(self._laws, key, law, 8)

    async def get_legislation_toc(self, id):
        law = await self._law(id)
        entries, seen = [], set()
        for nd in law["nodes"]:
            if nd.label and nd.label in seen:
                continue  # second (older/newer) wording of the same section
            seen.add(nd.label)
            entries.append(TocEntry(title=nd.title or nd.label, level=nd.level,
                                    provision=nd.label))
        return Toc(id=law["id"], title=law["title"], url=law["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        law = await self._law(id)
        want = _norm_label(provision)
        if want[1]:
            match = [nd for nd in law["nodes"] if _http.localname(nd.el) == "section"
                     and (_label_key(nd.label) == want
                          or not want[0] and _label_key(nd.label)[1] == want[1])]
            chapters = {_label_key(nd.label)[0] for nd in match}
            if len(chapters) > 1:
                raise BadRequest(f"{want[1]} § occurs in several chapters of {law['title']}: "
                                 f"give the chapter too, e.g. '{match[0].label}' or "
                                 f"'{_label_key(match[0].label)[0]}:{want[1]}'")
        else:
            match = [nd for nd in law["nodes"] if _http.localname(nd.el) == "chapter"
                     and _label_key(nd.label)[0] == want[0]]
        if not match:
            raise NotFound(f"no provision {provision!r} in {law['title']}; labels look like "
                           f"'{next((nd.label for nd in law['nodes'] if nd.label), '1 §')}'")
        els = []
        for nd in match:  # keep the authorial note between two wordings of one section
            prev = nd.el.getprevious()
            if els and prev is not None and prev.get("name") == "noteAuthorial":
                els.append(prev)
            els.append(nd.el)
        return Provision(law_id=law["id"], law_title=law["title"], provision=match[0].label,
                         text=_to_md(*els), url=law["url"], as_of=law["as_of"])

    async def get_legislation_text(self, id):
        law = await self._law(id)
        m = law["meta"]
        meta = {k: v for k, v in (("type", m["type"]), ("status", m["status"]),
                                  ("issued", m["date"]),
                                  ("language", "Swedish" if m["lang"] == "swe" else "Finnish"))
                if v}
        return LawText(id=law["id"], title=law["title"], text=_to_md(law["body"]),
                       url=law["url"], as_of=law["as_of"], metadata=meta)
