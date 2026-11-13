"""Ireland: legislation from the Irish Statute Book (eISB) and the Law Reform Commission's
Revised Acts. No case law.

Gotchas this code encodes:
  * Search uses the eISB site's own Solr title index (`/solr/all_leg_title/select`, the
    endpoint its search page calls). The Oireachtas API has no text search, so it is not used.
  * Texts: the LRC Revised Act (consolidated, HTML) is preferred; when the LRC has not
    revised an Act (404), the eISB ELI XML *as enacted* is used. Every text says which.
  * eISB XML is a custom schema: characters are empty elements (<emdash/>, <afada/>,
    <odq/>, <unicode ch="03BF"/>), footnotes are inline <fn>. Both formats share the
    part/chapter/sect/schedule structure and the SEC<n>/SCHED<n> ids, so one walker serves both.
  * Statutory Instruments have no XML, only table-layout HTML: full text only, no TOC.
  * Pre-1922 Acts have no ELI text: unless the LRC revised them, they come from eISB's legacy
    page /<year>/en/act/pub/<NNNN>/print.html (table layout, sections anchored secN/schedN,
    margin-note titles in <small>), turned into the same structure for the walker.
  * The Constitution (id "cons") is a hand-made HTML page at /eli/cons/en/html, no XML: parts
    are <h3>, unnumbered sub-headings <h4>-<h6>, articles anchored articleN; two article
    headings are malformed on the site (19, 44). Labels are 'article/N' and 'preamble'.
  * Case law: judgments.courts.ie robots.txt is `Disallow: /`; BAILII Ireland is behind an
    anti-bot wall. Both are left out.
"""
from __future__ import annotations

import copy
import datetime
import re
import unicodedata

import lxml.html
from lxml import etree

from .._http import clean, get, html_to_md, lru_put, text
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import LawHit, LawText, Provision, Results, Toc, TocEntry

EISB = "https://www.irishstatutebook.ie"
LRC = "https://revisedacts.lawreform.ie"
SOLR = f"{EISB}/solr/all_leg_title/select"
_STRUCT = ("part", "chapter", "sect", "schedule", "article")  # "article": Constitution only
_CHARS = {"emdash": "—", "endash": "–", "odq": "“", "cdq": "”", "osq": "‘", "csq": "’",
          "euro": "€", "pound": "£", "nbsp": " "}
_DROP = {"graphic", "hr1", "hr", "img", "colgroup", "col"}
_cache: dict = {}


# --------------------------------------------------------------------------- ids
def _parse_id(raw: str) -> tuple[str, str, str]:
    """-> (year, 'act'|'si'|'prv', number). Accepts ELI paths/URLs, 'S.I. No. 484 of 2014',
    'Act 30 of 2014', 'No. 30 of 2014', '30/2014'."""
    s = clean(raw)
    m = re.search(r"(?:^|/eli/)(\d{4})/(act|si|prv)/(\d+)\b", s, re.I)
    if m:
        return m[1], m[2].lower(), str(int(m[3]))
    m = re.fullmatch(r"Private\s+Act\s*(?:No\.?\s*)?(\d+)\s*(?:/|of)\s*(\d{4})", s, re.I)
    if m:
        return m[2], "prv", str(int(m[1]))
    m = re.fullmatch(r"(S\.?\s*I\.?|SI)\s*(?:No\.?)?\s*(\d+)\s*(?:/|of)\s*(\d{4})\.?", s, re.I)
    if m:
        return m[3], "si", str(int(m[2]))
    m = re.fullmatch(r"(?:Act\s*)?(?:No\.?\s*)?(\d+)\s*(?:/|of)\s*(\d{4})", s, re.I)
    if m:
        return m[2], "act", str(int(m[1]))
    raise BadRequest(f"Unrecognised Irish legislation id {raw!r}. Use an ELI path like "
                     "'2014/act/30' or '2014/si/484' (as search_legislation returns), "
                     "'Act 30 of 2014' / 'S.I. No. 484 of 2014', '2023/prv/1' (Private Act) "
                     "or 'cons' (the Constitution).")


async def _solr(params) -> dict:
    r = await get(SOLR, params=params)
    if r.status_code != 200:
        raise SourceError(f"Irish Statute Book search returned HTTP {r.status_code}", r.status_code)
    try:
        return r.json()["response"]
    except (ValueError, KeyError):
        raise SourceError("Irish Statute Book search returned an unexpected payload", r.status_code)


def _eli_html(y: str, kind: str, n: str) -> str:
    return f"{EISB}/eli/{y}/{kind}/{n}/{'made' if kind == 'si' else 'enacted'}/en/html"


# --------------------------------------------------------------------------- XML/HTML normalising
def _swap(el, s: str) -> None:
    """Replace an element by the string s, keeping its tail."""
    parent = el.getparent()
    if parent is None:
        return
    txt, prev = s + (el.tail or ""), el.getprevious()
    if prev is not None:
        prev.tail = (prev.tail or "") + txt
    else:
        parent.text = (parent.text or "") + txt
    parent.remove(el)


def _char(tag: str, el) -> str | None:
    if tag in _CHARS:
        return _CHARS[tag]
    if tag == "unicode" and el.get("ch"):
        try:
            return chr(int(el.get("ch"), 16))
        except ValueError:
            return ""
    if len(tag) == 5 and tag.lower().endswith("fada"):   # afada -> á, Efada -> É
        return unicodedata.normalize("NFC", tag[0] + "́")
    return None


def _normalise_xml(root) -> None:
    """eISB XML: footnotes inline as ' (footnote n: …)', character elements to text."""
    for fn in list(root.iter("fn")):
        n = text(fn.find("marker"))
        for su in list(fn.iter("su")):
            if su.getparent() is not None and su.getparent().tag != "marker":
                _swap(su, "")
        body = " ".join(text(p) for p in fn.iter("p"))
        _swap(fn, f" (footnote {n}: {body})" if body else "")
    for el in list(root.iter()):
        if not isinstance(el.tag, str):
            continue
        if el.tag in _DROP:
            _swap(el, "")
            continue
        c = _char(el.tag, el)
        if c is not None:
            _swap(el, c)


def _kind(el) -> str:
    if not isinstance(el.tag, str):
        return ""
    if el.tag == "section":
        cls = (el.get("class") or "").split()
        return cls[0] if cls and cls[0] in _STRUCT else ""
    return el.tag if el.tag in _STRUCT else ""


def _is_title(el) -> bool:
    return el.tag == "title" or (el.tag == "div" and el.get("class") == "title")


def _is_number(el) -> bool:
    return el.tag == "number" or (el.tag == "div" and el.get("class") == "number")


def _heading(el) -> tuple[str, str]:
    """(number, title) of a structural element."""
    num = title = ""
    for c in el:
        if not isinstance(c.tag, str):
            continue
        if _is_number(c) and not num:
            num = text(c).rstrip(".")
        elif _is_title(c) and not title:
            ps = [text(p) for p in c.iter("p")] or [text(c)]
            title = " — ".join(p for p in ps if p)
    return num, title


def _label(el, in_schedule: bool) -> str:
    k, eid = _kind(el), el.get("id") or ""
    if k == "sect" and not in_schedule:
        m = re.fullmatch(r"SEC(\w+)", eid)
        n = m[1] if m else (el.get("data-number") or _heading(el)[0])
        return f"section/{n}" if n else ""
    if k == "schedule":
        m = re.fullmatch(r"SCHED(\w*)", eid)
        n = m[1] if m else (el.get("data-number") or "")
        return f"schedule/{n}" if n else "schedule"
    if k == "article":
        n = el.get("data-number") or ""
        return "preamble" if n == "preamble" else f"article/{n}"
    return ""


def _head_text(el) -> str:
    num, title = _heading(el)
    if _kind(el) == "sect":
        return f"Section {num} — {title}" if title else f"Section {num}"
    if _kind(el) == "article":
        n = el.get("data-number")
        return "Preamble" if n == "preamble" else f"Article {n}"
    return title or num or _kind(el).title()


def _html(el) -> str:
    return etree.tostring(el, encoding="unicode", method="html", with_tail=False)


def _render(el, level: int = 2) -> str:
    """Markdown for a structural element (or a container div), headings by depth."""
    out, buf = [], []

    def flush():
        if buf:
            md = html_to_md("".join(buf))
            if md:
                out.append(md)
            buf.clear()

    if _kind(el):
        out.append(f"{'#' * min(level, 6)} {_head_text(el)}")
    for c in el:
        if not isinstance(c.tag, str) or _is_title(c) or _is_number(c):
            continue
        if _kind(c):
            flush()
            out.append(_render(c, level + 1))
        else:
            buf.append(_html(c))
    flush()
    return "\n\n".join(p for p in out if p)


# --------------------------------------------------------------------------- fetching
class _Doc:
    def __init__(self, id, title, url, version, as_of, parts, note, date=""):
        self.id, self.title, self.url, self.version = id, title, url, version
        self.as_of, self.parts, self.note, self.date = as_of, parts, note, date


def _long_date(s: str) -> str:
    try:
        return datetime.datetime.strptime(clean(s), "%d %B %Y").date().isoformat()
    except ValueError:
        return ""


def _is_cons(raw: str) -> bool:
    s = clean(raw).lower().replace(EISB, "").replace("http://www.irishstatutebook.ie", "").strip("/ ")
    return bool(re.fullmatch(r"(?:eli/)?cons(?:/en(?:/html)?)?|(?:the )?constitution(?: of ireland)?"
                             r"|bunreacht(?: na h[ée]ireann)?", s))


async def _load(raw_id: str) -> _Doc:
    if _is_cons(raw_id):
        if "cons" not in _cache:
            lru_put(_cache, "cons", await _load_cons(), 4)
        return _cache["cons"]
    y, kind, n = _parse_id(raw_id)
    key = f"{y}/{kind}/{n}"
    if key in _cache:
        return _cache[key]
    if kind == "act":
        doc = await _load_revised(key, y, n) or (
            await _load_pre1922(key, y, n) if int(y) < 1922 else await _load_enacted(key, y, n))
    elif kind == "prv":
        doc = await _load_pre1922(key, y, n, "prv")
    else:
        doc = await _load_si(key, y, n)
    return lru_put(_cache, key, doc, 4)


async def _load_revised(key, y, n) -> _Doc | None:
    url = f"{LRC}/eli/{y}/act/{n}/revised/en/html"
    r = await get(url)
    if r.status_code == 404:
        return None
    if r.status_code != 200:
        raise SourceError(f"Law Reform Commission Revised Acts returned HTTP {r.status_code} for {key}",
                          r.status_code)
    tree = lxml.html.fromstring(r.content)
    main = tree.xpath('//div[contains(concat(" ", @class, " "), " cell medium-9 ")]'
                      '[div[@class="body"]]')
    if not main:
        raise SourceError(f"unexpected Revised Act page layout for {key}", r.status_code)
    main = main[0]
    for bad in main.xpath('.//div[@class="acttoc" or @class="new-blue-header" or @class="sect-tab"]'
                          ' | .//style | .//script'):
        _swap(bad, "")
    title = clean((tree.findtext(".//title") or "").split("|")[0]) or key
    page_txt = text(main)
    m = re.search(r"Updated to (\d{1,2} \w+ \d{4})", page_txt)
    as_of = _long_date(m[1]) if m else ""
    updated = m[1] if m else "an unstated date"
    m = re.search(r"as of (\d{1,2} \w+ \d{4}), this Act is up to date[^.]*\.", page_txt)
    note = (f"Revised Act (Law Reform Commission administrative consolidation); the text reflects the law "
            f"as updated to {updated}, so later amendments are not incorporated."
            + (f" The LRC page also states: \"{m[0]}\" (the LRC's own statement, not verified here)." if m else "")
            + " Not an official text; check annotations for commencement.")
    parts = [d for d in main if d.tag == "div" and d.get("class") in ("frontmatter", "body", "backmatter")]
    # the LRC puts its annotations in the front matter; read them after the operative text
    notes_div = [a for p in parts if p.get("class") == "frontmatter"
                 for a in p.xpath('./div[@class="annotations"]')]
    for a in notes_div:
        a.getparent().remove(a)
    parts += notes_div
    # the front matter prints the title block twice around an emptied "ARRANGEMENT OF SECTIONS"
    # (the TOC is dropped above; get_legislation_toc serves it): keep only the second title block
    for fm in (p for p in parts if p.get("class") == "frontmatter"):
        kids = list(fm)
        arr = next((i for i, c in enumerate(kids) if text(c).upper() == "ARRANGEMENT OF SECTIONS"), None)
        first = next((i for i, c in enumerate(kids) if text(c).startswith("Number ")), None)
        if arr is not None and first is not None and first < arr:
            for c in kids[first:arr + 1]:
                fm.remove(c)
    return _Doc(key, title, url, "revised", as_of, parts, note)


async def _load_enacted(key, y, n) -> _Doc:
    url = f"{EISB}/eli/{y}/act/{n}/enacted/en/xml"
    r = await get(url)
    if r.status_code == 404:
        raise NotFound(f"No Act {n} of {y} on the Irish Statute Book.")
    if r.status_code != 200 or b"<act" not in r.content[:2000]:
        raise SourceError(f"Irish Statute Book returned HTTP {r.status_code} for {key}", r.status_code)
    try:
        root = etree.fromstring(r.content, etree.XMLParser(recover=True, resolve_entities=False))
    except etree.XMLSyntaxError as e:
        raise SourceError(f"Irish Statute Book XML for {key} did not parse: {e}", r.status_code)
    for toc in list(root.iter("acttoc")):
        _swap(toc, "")
    _normalise_xml(root)
    meta = root.find("metadata")
    title = clean(text(meta.find("title"))) if meta is not None else key
    d = re.sub(r"\D", "", text(meta.find("dateofenactment")) if meta is not None else "")
    date = f"{d[:4]}-{d[4:6]}-{d[6:8]}" if len(d) == 8 else ""
    parts = [c for c in root if c.tag in ("frontmatter", "body", "backmatter")]
    note = ("Text as enacted (Irish Statute Book); the Law Reform Commission has not published "
            "a Revised Act for it, so later amendments are NOT shown.")
    return _Doc(key, title or key, _eli_html(y, "act", n), "enacted", "", parts, note, date)


async def _load_si(key, y, n) -> _Doc:
    url = _eli_html(y, "si", n)
    r = await get(url)
    if r.status_code == 404:
        raise NotFound(f"No S.I. No. {n} of {y} on the Irish Statute Book.")
    if r.status_code != 200:
        raise SourceError(f"Irish Statute Book returned HTTP {r.status_code} for {key}", r.status_code)
    tree = lxml.html.fromstring(r.content)
    act = tree.xpath('//div[@id="act"]')
    if not act:
        raise SourceError(f"unexpected Irish Statute Book page layout for {key}", r.status_code)
    title = clean(text(tree.find(".//h1"))) or clean(tree.findtext(".//title")) or key
    note = "Statutory Instrument as made (Irish Statute Book); later amendments are NOT shown."
    return _Doc(key, title, url, "made", "", [act[0]], note)


def _section(cls: str, number: str, title: str, body_html: str, **attrs):
    """A synthetic structural element the walker/renderer understands, for plain-HTML pages."""
    el = etree.Element("section", {"class": cls, **attrs})
    if number:
        etree.SubElement(el, "div", {"class": "number"}).text = number
    if title:
        etree.SubElement(el, "div", {"class": "title"}).text = title
    if body_html.strip():
        el.append(lxml.html.fragment_fromstring(body_html, create_parent="div"))
    return el


async def _load_pre1922(key, y, n, seg="pub") -> _Doc:
    """Pre-1922 Acts (not revised by the LRC) and Private Acts (seg 'prv'): eISB's legacy page,
    sections anchored secN/schedN."""
    url = f"{EISB}/{y}/en/act/{seg}/{int(n):04d}/print.html"
    r = await get(url)
    if r.status_code == 404:
        what = "Private Act" if seg == "prv" else "pre-1922 Act"
        raise NotFound(f"No {what} {n} of {y} on the Irish Statute Book.")
    if r.status_code != 200:
        raise SourceError(f"Irish Statute Book returned HTTP {r.status_code} for {key}", r.status_code)
    tree = lxml.html.fromstring(r.content)
    act = tree.xpath('//div[@id="act"]')
    if not act:
        raise SourceError(f"unexpected Irish Statute Book page layout for {key}", r.status_code)
    raw = re.sub(r"</?(?:table|tbody|tr|td)\b[^>]*>", "", _html(act[0]))
    raw = re.sub(r'^<div[^>]*>|</div>\s*$', "", raw.strip())
    pieces = re.split(r'<a name="(sec|sched)(\w+)"></a>', raw)
    root = etree.Element("div")
    if pieces[0].strip():
        root.append(lxml.html.fragment_fromstring(pieces[0], create_parent="div"))
    for i in range(1, len(pieces) - 2, 3):
        kind, num, body = pieces[i], pieces[i + 1], pieces[i + 2]
        if kind == "sec":
            m = re.match(r"\s*<p[^>]*>\s*<small>(.*?)</small>\s*</p>", body, re.S)
            title = clean(lxml.html.fromstring(m[1]).text_content()) if m else ""
            body = body[m.end():] if m else body
            root.append(_section("sect", num, title, body, id=f"sec{num}", **{"data-number": num}))
        else:
            root.append(_section("schedule", "", f"Schedule {num}", body, id=f"sched{num}",
                                 **{"data-number": num}))
    title = clean(tree.findtext(".//title")) or key
    note = ("Private Act as published on the Irish Statute Book; later amendments are NOT shown."
            if seg == "prv" else
            "Pre-1922 Act as published on the Irish Statute Book (not revised by the Law Reform "
            "Commission): later amendments and repeals are NOT shown.")
    return _Doc(key, title, url, "private" if seg == "prv" else "pre-1922", "", [root], note)


async def _load_cons() -> _Doc:
    """Constitution of Ireland (English text) from eISB's hand-made page: parts <h3>, unnumbered
    sub-headings <h4>-<h6>, articles anchored articleN (19 and 44 have broken heading tags)."""
    url = f"{EISB}/eli/cons/en/html"
    r = await get(url)
    if r.status_code != 200:
        raise SourceError(f"Irish Statute Book returned HTTP {r.status_code} for the Constitution",
                          r.status_code)
    h = r.content.decode("utf-8", "replace")
    amend, contents = h.find(">AMENDING ACTS"), h.find(">CONTENTS")
    start = h.find("<h2", contents)
    end = h.rfind("<h2", start, h.find('id="index"'))
    if min(amend, contents, start, end) < 0:
        raise SourceError("unexpected layout of the Constitution page on the Irish Statute Book")
    acts = re.findall(r"([A-Z][\w-]+ Amendment of the Constitution\b.*?Act,? \d{4})\s*\[.*?\]\s*"
                      r"(\d{1,2} \w+,? \d{4})",
                      re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h[amend:contents])))
    body = re.sub(r'<p style="display: block; text-align: center[^>]*>\s*<b><b>[^<]*</b></b>\s*</p>',
                  "", h[start:end])        # centred 'THE FAMILY' label between Articles 40 and 41
    cuts = [(m.start(), int(m[1])) for m in re.finditer(r"<h([3-6])\b", body)]
    for m in re.finditer(r'<a name="article\d+[A-Za-z]?"', body):
        if not re.search(r"<h[3-6][^>]*>\s*$", body[max(0, m.start() - 80):m.start()]):
            cuts.append((m.start(), 5))      # Article 44: heading written as 'H5>' without '<'
    cuts.sort()
    root = etree.Element("div")
    pre = re.sub(r"(?s)^.*?</h2>", "", body[:cuts[0][0]])
    root.append(_section("article", "", "", pre, **{"data-number": "preamble"}))
    stack = [(0, root)]
    for (pos, lvl), (nxt, _) in zip(cuts, cuts[1:] + [(len(body), 0)]):
        seg = body[pos:nxt]
        a = re.match(r'(?:<h[3-6][^>]*>\s*)?<?a name="(part|article)(\w+)"', seg)  # 19: '<h5>a name
        content = re.sub(r"(?si)^.*?</h[3-6]>", "", seg, count=1)
        if a and a[1] == "article":
            el = _section("article", "", "", content, id=f"article{a[2]}",
                          **{"data-number": a[2].upper()})
            leaf = True
        else:
            head = re.search(r"(?si)^.*?</h[3-6]>", seg)
            title = clean(lxml.html.fromstring(head[0]).text_content()) if head else ""
            el = _section("part" if a else "chapter", "", title, content)
            leaf = False
        while stack[-1][0] >= lvl:
            stack.pop()
        stack[-1][1].append(el)
        if not leaf:
            stack.append((lvl, el))
    last = f"{acts[-1][0]} (signed {acts[-1][1]})" if acts else "an unstated date"
    note = (f"Constitution of Ireland, English text as on the Irish Statute Book, including amendments "
            f"up to the {last}. The Irish text prevails in case of conflict (Article 25.5.4).")
    as_of = _long_date(acts[-1][1].replace(",", "")) if acts else ""
    return _Doc("cons", "Constitution of Ireland (Bunreacht na hÉireann)", url, "constitution",
                as_of, [root], note)


def _walk(doc: _Doc):
    """Yield (element, depth, in_schedule) for every structural element, in order."""
    def rec(el, depth, in_sched):
        for c in el:
            k = _kind(c)
            if k:
                yield c, depth, in_sched
                yield from rec(c, depth + 1, in_sched or k == "schedule")
    for p in doc.parts:
        yield from rec(p, 0, False)


def _norm_provision(p: str) -> str:
    s = clean(p).lower().rstrip(".")
    if s == "preamble":
        return s
    m = re.fullmatch(r"(?:article|art)[\s./]*(\d+[a-z]?)(\s*[.(].*)?", s)
    if m:
        if m[2]:
            raise BadRequest(f"Sub-article references like {p!r} are not supported; ask for the whole "
                             f"article, e.g. 'article/{m[1]}', and read the sub-paragraph in it.")
        return f"article/{m[1]}"
    m = re.fullmatch(r"(?:section|sect|sec|ss|s)?[\s./]*(\d+[a-z]*)", s)
    if m:
        return f"section/{m[1]}"
    m = re.fullmatch(r"(?:schedule|sched|sch)[\s./]*(\d+[a-z]*)?", s)
    if m:
        return f"schedule/{m[1]}" if m[1] else "schedule"
    raise BadRequest(f"Unrecognised provision {p!r}. Use a label from get_legislation_toc, "
                     "e.g. 'section/2' (or 's.2', '2'), 'schedule/1', or for the Constitution "
                     "'article/40' (or 'Article 40') and 'preamble'.")


# --------------------------------------------------------------------------- adapter
class Ireland(Jurisdiction):
    code = "ie"
    name = "Ireland"
    languages = ("en",)
    aliases = ("irl", "eire", "éire", "irish", "republic of ireland")
    sources = (
        Source(
            name="Irish Statute Book (eISB, Office of the Attorney General)",
            url=EISB,
            covers=("legislation",),
            licence="Oireachtas (Open Data) PSI Licence, which incorporates CC BY 4.0 "
                    "(attribution required). Search uses the site's own Solr title index "
                    "(undocumented); texts use the documented ELI XML/HTML",
            commercial_use=True,
            ai_use=True,
            auth="none",
            rate_limit="none documented; robots.txt is 404 (no rules); no 429 in ~25 requests "
                       "(2026-11); using 1 s spacing",
            terms_url=f"{EISB}/eli/open-data.html",
        ),
        Source(
            name="Law Reform Commission Revised Acts",
            url=LRC,
            covers=("legislation",),
            licence="Legislative text: Oireachtas (Open Data) PSI Licence (CC BY 4.0); LRC "
                    "annotations: CC BY 4.0. Attribute the Houses of the Oireachtas and the LRC "
                    "separately",
            commercial_use=True,
            ai_use=True,
            auth="none",
            rate_limit="none documented; robots.txt allows all; no 429 in ~15 requests (2026-11); "
                       "using 1 s spacing",
            terms_url=f"{LRC}/open-data-licence",
        ),
    )
    legislation_filters = {
        "type": "'act' or 'si' (Statutory Instrument); default both",
        "year": "a year '2014' or a range '2010-2015'",
    }
    min_interval = {"www.irishstatutebook.ie": 1.0, "revisedacts.lawreform.ie": 1.0}
    notes = ("Legislation only (Constitution, Acts and S.I.s, English). Ids are ELI paths like "
             "'2014/act/30'; the Constitution is 'cons' (provisions 'article/40', 'preamble'); "
             "provisions 'section/2', 'schedule/1'. Pre-1922 Acts as published on eISB. Acts use the LRC Revised Act (consolidated) "
             "when one exists, else the text as enacted; each text says which. S.I.s: as made, "
             "full text only. No case law: judgments.courts.ie robots.txt disallows all crawling. "
             "Employment decisions (unfair dismissal etc.) are published by the Workplace Relations "
             "Commission (workplacerelations.ie) and the Labour Court; neither is wired here.")
    gaps = (
        "Case law (judgments.courts.ie): robots.txt disallows (`Disallow: /`); BAILII Ireland: bot check / blocks our client",
        "Employment decisions (unfair dismissal etc.): Workplace Relations Commission and Labour Court, "
        "workplacerelations.ie (not wired; search there directly)",
        "Consolidated text of Acts the LRC has not revised: not published online (eISB has them as enacted only)",
        "Pre-1922 Acts not revised by the LRC: text as published on eISB, later amendments/repeals not shown",
        "Private Acts: open by id ('2023/prv/1') but not in the eISB search index (listed at /isbc/patoc.html)",
        "Constitution: English text only (the Irish text, which prevails, is not wired)",
        "Statutory Instruments: as made, full text only (no XML, no TOC); consolidated S.I.s not researched yet",
    )
    samples = {
        "legislation_query": "freedom of information",
        "law_id": "2014/act/30",
        "provision": "section/2",
    }

    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        words = re.sub(r'[+\-&|!(){}\[\]^"~*?:\\/]', " ", (query or "")).lower().split()
        if not words:
            raise BadRequest("query is empty; give words from the title, e.g. 'freedom of information'.")
        fq = []
        t = (filters.get("type") or "").strip().lower()
        if t:
            if t not in ("act", "si"):
                raise BadRequest("type must be 'act' or 'si'.")
            fq.append(f"type:{t}")
        yr = (filters.get("year") or "").strip()
        if yr:
            m = re.fullmatch(r"(\d{4})(?:\s*-\s*(\d{4}))?", yr)
            if not m:
                raise BadRequest("year must be 'YYYY' or 'YYYY-YYYY'.")
            if m[2] and int(m[1]) > int(m[2]):
                raise BadRequest(f"year range {yr!r} is inverted; use '{m[2]}-{m[1]}'.")
            fq.append(f"year:[{m[1]} TO {m[2] or m[1]}]")
        limit, page = max(1, min(int(limit), 50)), max(1, int(page))
        params = [("q", " ".join(words)), ("wt", "json"), ("rows", str(limit)),
                  ("start", str((page - 1) * limit)), ("sort", "score desc,year desc"),
                  ("fl", "title,year,act,leg,type,link")] + [("fq", f) for f in fq]
        resp = await _solr(params)
        stemmed = False
        if not resp.get("numFound") and page == 1:
            # the index matches whole words only ('dismissal' misses 'Dismissals'): retry as prefixes
            params[0] = ("q", " ".join(w + "*" for w in words))
            params[params.index(("rows", str(limit)))] = ("rows", "50")   # rank the whole set, then cut
            resp = await _solr(params)
            stemmed = bool(resp.get("numFound"))
            if stemmed:
                # prefix matches come back in arbitrary order: Acts whose title starts with the words first
                q = " ".join(words)
                resp["docs"].sort(key=lambda d: (not clean(d.get("title")).lower().startswith(q),
                                                 d.get("type") != "act"))
                resp["docs"] = resp["docs"][:limit]
        items = []
        for d in resp.get("docs", []):
            kind, y = d.get("type", ""), str(d.get("year", ""))
            n = str(d.get("act") or d.get("leg") or "")
            if kind not in ("act", "si") or not (y and n.isdigit()):
                continue
            n = str(int(n))
            url = _eli_html(y, kind, n) if int(y) >= 1922 else (d.get("link") or _eli_html(y, kind, n))
            items.append(LawHit(
                id=f"{y}/{kind}/{n}", title=clean(d.get("title")),
                type="Act" if kind == "act" else "Statutory Instrument",
                number=f"{'S.I. ' if kind == 'si' else ''}No. {n} of {y}",
                url=url.replace("http://", "https://")))
        if (page == 1 and t != "si" and not yr
                and re.search(r"\b(constitution|bunreacht)\b", " ".join(words))):
            items.insert(0, LawHit(id="cons", title="Constitution of Ireland (Bunreacht na hÉireann)",
                                   type="Constitution", status="in force",
                                   url=f"{EISB}/eli/cons/en/html"))
        hint = (" Matched word beginnings because the exact words found nothing." if stemmed else
                "" if items else
                " Search matches words in the title only, not subject matter or short names: use "
                "the Act's title words (e.g. 'Data Protection Act 2018', not 'GDPR').")
        return Results(items, total=resp.get("numFound"),
                       note="Title search." + hint + " Acts open as the LRC Revised Act (consolidated) where one "
                            "exists, else as enacted; S.I.s as made. Act hit URLs point to the enacted "
                            "text; the provision/TOC/text tools return the Revised Act where one exists.")

    async def get_legislation_toc(self, id):
        doc = await _load(id)
        if doc.version == "made":
            raise BadRequest("Statutory Instruments have no structured text on eISB; "
                             "use get_legislation_text for the full S.I.")
        entries, seen = [], set()
        for el, depth, in_sched in _walk(doc):
            label = _label(el, in_sched)
            if label in seen:
                label = ""
            if _kind(el) == "sect" and in_sched:
                continue
            seen.add(label)
            entries.append(TocEntry(title=_head_text(el), level=depth, provision=label))
        if not entries:
            raise SourceError(f"no sections found in {doc.id}")
        return Toc(id=doc.id, title=f"{doc.title} ({doc.version})", url=doc.url, entries=entries)

    async def get_legislation_provision(self, id, provision):
        doc = await _load(id)
        if doc.version == "made":
            raise BadRequest("Statutory Instruments have no structured text on eISB; "
                             "use get_legislation_text for the full S.I.")
        want = _norm_provision(provision)
        if doc.version == "constitution" and re.fullmatch(r"section/\d+[a-z]?", want):
            want = "article/" + want.split("/")[1]     # bare '40' means Article 40 here
        # a lone schedule is "SCHED" in eISB XML but "SCHED1" in Revised Acts
        wants = {want, "schedule", "schedule/1"} if want in ("schedule", "schedule/1") else {want}
        for el, _depth, in_sched in _walk(doc):
            label = _label(el, in_sched)
            if label and label.lower() in wants:
                y, _, n = (doc.id.split("/") + ["", ""])[:3]
                anchor = el.get("id") or ""
                if doc.version == "enacted" and label.startswith("section/"):
                    url = f"{EISB}/eli/{y}/act/{n}/section/{label.split('/', 1)[1]}/enacted/en/html"
                else:
                    url = f"{doc.url}#{anchor}" if anchor else doc.url
                return Provision(law_id=doc.id, law_title=doc.title, provision=label,
                                 text=f"_{doc.note}_\n\n{_render(el, 3)}", url=url, as_of=doc.as_of)
        raise NotFound(f"No {want} in {doc.title} ({doc.id}); see get_legislation_toc.")

    async def get_legislation_text(self, id):
        doc = await _load(id)
        parts = doc.parts
        if doc.version == "revised":
            # per-section annotations (amendment notes) go after all the operative text
            parts = copy.deepcopy(parts)
            moved = [a for p in parts for a in p.xpath('.//div[@class="annotations"]')
                     if a.getparent() is not None and a.getparent() is not p]
            for a in moved:
                a.getparent().remove(a)
            parts = parts + moved
        body = "\n\n".join(md for md in (_render(p) for p in parts) if md)
        meta = {"version": doc.version, "note": doc.note}
        if doc.date:
            meta["date of enactment"] = doc.date
        return LawText(id=doc.id, title=doc.title, text=f"_{doc.note}_\n\n{body}", url=doc.url,
                       as_of=doc.as_of, metadata=meta)
