"""Japan: legislation from the e-Gov 法令API v2 (Digital Agency). No case law.

Gotchas this code encodes:
  * law_id is e-Gov's own id, e.g. 129AC0000000089 = 民法 (Meiji 29 Act No. 89).
    law_data also takes a 法令番号 ("明治二十九年法律第八十九号") or a law_revision_id
    (point-in-time text), so those are passed straight through. A law title ("民法")
    is resolved with an exact-title lookup on /laws.
  * We fetch law_data as XML (the standard 法令XML schema); the JSON body format is
    marked 試行版 (trial, may change) in the API spec.
  * Provision labels are the source's own ArticleTitle ("第七百九条"). Article Num
    attrs are "709", "398_2" (第三百九十八条の二) or ranges like "38:84" for blocks of
    deleted articles; "709", "art. 709", "第709条", "709条の2" are mapped onto them.
    Supplementary provisions are exposed whole as "附則" / "附則（<amending law no.>）".
  * /keyword (full-text search) pages by matching *sentences*, not laws: `limit`
    caps the sentence count and `offset` counts sentences, so a law can repeat on
    the next page. Title search (/laws) pages cleanly by law.
  * Case law (courts.go.jp 裁判例検索) is not implemented: on 2026-11-05 every search
    page redirects to /error_document/sorry.html (maintenance). Detail pages
    (/hanrei/<id>/detail2/index.html) still answer, with the full text only as PDF.
"""
from __future__ import annotations

import re
import unicodedata

from lxml import etree

from .._http import get, iso_date, lru_put
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import LawHit, LawText, Provision, Results, Toc, TocEntry

HOST = "https://laws.e-gov.go.jp"
API = f"{HOST}/api/2"
LAW_URL = HOST + "/law/{id}"

_LAW_TYPES = ("Constitution", "Act", "CabinetOrder", "ImperialOrder",
              "MinisterialOrdinance", "Rule", "Misc")
_LAW_ID = re.compile(r"^(?:\d{3}[A-Z][A-Z0-9]\d{10}(?:_\d{8}_[0-9A-Z]{15})?"
                     r"|\d{3}CONSTITUTION(?:_\d{8}_[0-9A-Z]{15})?)$")  # 321CONSTITUTION = 日本国憲法
_HEADINGS = {"Part": 2, "Chapter": 3, "Section": 4, "Subsection": 5, "Division": 6}
_INLINE = {"Sentence", "Ruby", "Rt", "Line", "Sup", "Sub", "Column", "QuoteStruct"}
_SKIP = {"TOC", "Rt", "ArticleRange"}
_STATUS = {"None": "in force", "Repeal": "repealed", "Expire": "expired",
           "LossOfEffectiveness": "lost effect"}

_cache: dict[str, "_Law"] = {}
_titles: dict[str, str] = {}


# =========================================================================== #
# Text helpers
# =========================================================================== #
def _ws(s: str) -> str:
    """Collapse ASCII whitespace only: the ideographic space (U+3000) is meaningful."""
    return re.sub(r"[ \t\r\n]+", " ", s).strip()


def _inline(el) -> str:
    """Text of an element, dropping ruby readings (<Rt>), columns joined by a full-width space."""
    if el is None:
        return ""
    def own(t):  # whitespace-only text/tails are XML formatting, not content
        return t if t and t.strip() else ""
    parts = [own(el.text)]
    first_col = True
    for c in el:
        if c.tag == "Rt":
            pass
        elif c.tag == "Column":
            if not first_col:
                parts.append("　")
            first_col = False
            parts.append(_inline(c))
        else:
            parts.append(_inline(c))
        parts.append(own(c.tail))
    return _ws("".join(parts))


def _child(el, tag: str):
    return el.find(tag)


def _blocks(el, out: list[str]) -> None:
    """Flatten a 法令XML subtree into markdown paragraphs."""
    tag = el.tag
    if not isinstance(tag, str) or tag in _SKIP:
        return
    if tag in _HEADINGS:
        out.append("#" * _HEADINGS[tag] + " " + _inline(_child(el, f"{tag}Title")))
        for c in el:
            if c.tag != f"{tag}Title":
                _blocks(c, out)
        return
    if tag == "LawTitle":
        out.append("# " + _inline(el))
        return
    if tag == "SupplProvision":
        out.append("## " + _suppl_label(el))
        for c in el:
            if c.tag != "SupplProvisionLabel":
                _blocks(c, out)
        return
    if tag == "Article":
        out.append(f"**{_inline(_child(el, 'ArticleTitle'))}**{_inline(_child(el, 'ArticleCaption'))}")
        for c in el:
            if c.tag not in ("ArticleTitle", "ArticleCaption"):
                _blocks(c, out)
        return
    if tag in ("Paragraph", "Item") or re.fullmatch(r"Subitem\d+", tag):
        cap = _child(el, "ParagraphCaption")
        if cap is not None and _inline(cap):
            out.append(_inline(cap))
        head = [_inline(c) for c in el if c.tag in (
            "ParagraphNum", "ItemTitle", f"{tag}Title", "ParagraphSentence", "ItemSentence",
            f"{tag}Sentence")]
        line = "　".join(h for h in head if h)
        if line:
            out.append(line)
        for c in el:
            if c.tag not in ("ParagraphCaption", "ParagraphNum", "ItemTitle", f"{tag}Title",
                             "ParagraphSentence", "ItemSentence", f"{tag}Sentence"):
                _blocks(c, out)
        return
    if tag == "TableRow":
        cells = [_inline(c) for c in el]
        if any(cells):
            out.append(" ／ ".join(cells))
        return
    if all(c.tag in _INLINE for c in el if isinstance(c.tag, str)):
        t = _inline(el)
        if t:
            out.append(t)
        return
    if el.text and el.text.strip():
        out.append(_ws(el.text))
    for c in el:
        _blocks(c, out)


def _md(el) -> str:
    out: list[str] = []
    _blocks(el, out)
    return "\n\n".join(out)


def _suppl_label(el) -> str:
    label = re.sub(r"\s|　", "", _inline(_child(el, "SupplProvisionLabel"))) or "附則"
    amend = el.get("AmendLawNum")
    return f"{label}（{amend}）" if amend else label


# --------------------------------------------------------------------------- #
# Provision numbers
# --------------------------------------------------------------------------- #
_KD = {"〇": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
_KU = {"十": 10, "百": 100, "千": 1000}
_ART_RE = re.compile(
    r"^(?:art(?:icle)?\.?|§)?\s*第?\s*([0-9〇一二三四五六七八九十百千]+)\s*条?"
    r"((?:\s*(?:の|-|_)\s*[0-9〇一二三四五六七八九十百千]+)*)$", re.I)


def _num(s: str) -> int:
    if s.isdigit():
        return int(s)
    total = cur = 0
    for ch in s:
        if ch in _KD:
            cur = cur * 10 + _KD[ch] if cur else _KD[ch]
        else:
            total += (cur or 1) * _KU[ch]
            cur = 0
    return total + cur


def _arabic(num: str) -> str:
    """" [709]" / " [398の2]" suffix so a TOC keyword filter like '709' finds 第七百九条."""
    if not re.fullmatch(r"\d+(?:_\d+)*", num):
        return ""
    return f" [{num.replace('_', 'の')}]"


def _key(s: str) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", s))


# =========================================================================== #
# Law fetch + index
# =========================================================================== #
class _Law:
    def __init__(self, root):
        info = root.find("law_info")
        rev = root.find("revision_info")
        self.law_id = info.findtext("law_id", "")
        self.law_num = info.findtext("law_num", "")
        self.title = rev.findtext("law_title", "") if rev is not None else ""
        self.as_of = iso_date(rev.findtext("amendment_enforcement_date", "") if rev is not None else "")
        self.revision_id = rev.findtext("law_revision_id", "") if rev is not None else ""
        self.category = rev.findtext("category", "") if rev is not None else ""
        self.status = _status(rev)
        self.url = LAW_URL.format(id=self.law_id)
        self.law = root.find("law_full_text/Law")
        if self.law is None:
            raise SourceError("e-Gov law_data has no law_full_text/Law element")
        self.title = self.title or _inline(self.law.find("LawBody/LawTitle"))
        self.articles: dict[str, object] = {}   # Article Num -> element
        self.labels: dict[str, object] = {}     # NFKC label -> element
        self.toc: list[TocEntry] = []
        self._index()

    def _add(self, label: str, el, title: str, level: int):
        key = _key(label)
        if key in self.labels:  # e.g. two extract 附則 for the same amending law
            n = 2
            while _key(f"{label}#{n}") in self.labels:
                n += 1
            label, key = f"{label}#{n}", _key(f"{label}#{n}")
        self.labels[key] = (label, el)
        self.toc.append(TocEntry(title=title, level=level, provision=label))

    def _walk_main(self, el, level: int):
        for c in el:
            if c.tag in _HEADINGS:
                self.toc.append(TocEntry(title=_inline(c.find(f"{c.tag}Title")), level=level))
                self._walk_main(c, level + 1)
            elif c.tag == "Article":
                label = _inline(c.find("ArticleTitle"))
                self.articles[c.get("Num", "")] = c
                self._add(label, c, label + _inline(c.find("ArticleCaption")) + _arabic(c.get("Num", "")),
                          level)

    def _index(self):
        body = self.law.find("LawBody")
        main = body.find("MainProvision")
        if main is not None:
            if main.find(".//Article") is None:
                self._add("本則", main, "本則", 0)
            else:
                self._walk_main(main, 0)
        for c in body:
            if c.tag == "SupplProvision":
                label = _suppl_label(c)
                self._add(label, c, label, 0)
            elif c.tag.startswith("Appdx"):
                t = next((_inline(x) for x in c if isinstance(x.tag, str) and x.tag.endswith("Title")), "")
                if t:
                    self._add(t, c, t, 0)

    def find(self, provision: str):
        p = provision.strip()
        if not p:
            raise BadRequest("empty provision. Use an article such as '第七百九条', '709', "
                             "'art. 709', '第709条' or '398の2', or '附則'.")
        hit = self.labels.get(_key(p))
        if hit:
            return hit
        m = _ART_RE.match(_key(p))
        if m:
            nums = [_num(m[1])] + [_num(x) for x in re.findall(r"[0-9〇一二三四五六七八九十百千]+", m[2])]
            num = "_".join(map(str, nums))
            el = self.articles.get(num)
            if el is None and len(nums) == 1:  # blocks of deleted articles: Num="38:84"
                for k, v in self.articles.items():
                    a, _, b = k.partition(":")
                    if b and a.isdigit() and b.isdigit() and int(a) <= nums[0] <= int(b):
                        el = v
                        break
            if el is not None:
                label = _inline(el.find("ArticleTitle"))
                return label, el
        raise NotFound(f"{self.title} ({self.law_id}) has no provision {provision!r}. Labels look "
                       "like '第七百九条' (or '709', '398の2'), '附則'; see get_legislation_toc.")


def _status(rev) -> str:
    if rev is None:
        return ""
    s = _STATUS.get(rev.findtext("repeal_status", "") or "None", rev.findtext("repeal_status", ""))
    cur = rev.findtext("current_revision_status", "")
    if cur and cur != "CurrentEnforced":
        s = f"{s} ({cur})"
    return s


async def _api(path: str, params: dict):
    r = await get(f"{API}/{path}", params=params)
    if r.status_code == 404:
        return None
    if r.status_code == 400:
        try:
            msg = r.json().get("message", "")
        except ValueError:
            msg = r.text[:200]
        raise BadRequest(f"e-Gov rejected the request: {msg}")
    if r.status_code != 200:
        raise SourceError(f"e-Gov 法令API {path} failed", r.status_code)
    return r


async def _resolve_title(title: str) -> str:
    if title in _titles:
        return _titles[title]
    r = await _api("laws", {"law_title": title, "limit": 100, "response_format": "json"})
    laws = (r.json().get("laws") or []) if r is not None else []
    exact = []
    for x in laws:
        rev = x.get("current_revision_info") or x.get("revision_info") or {}
        if rev.get("law_title") == title or rev.get("abbrev") and title in rev["abbrev"].split(","):
            exact.append((rev.get("repeal_status") not in (None, "None"), x["law_info"]["law_id"]))
    if not exact:
        cands = ", ".join(f"{(x.get('revision_info') or {}).get('law_title')} "
                          f"({x['law_info']['law_id']})" for x in laws[:5])
        raise NotFound(f"no law titled {title!r}." + (f" Close: {cands}." if cands else "")
                       + " Use a law_id such as '129AC0000000089' (民法).")
    return lru_put(_titles, title, sorted(exact)[0][1], 64)


async def _load(law_id: str) -> _Law:
    key = unicodedata.normalize("NFKC", law_id or "").strip()
    key = re.sub(rf"^{re.escape(HOST)}/law/", "", key).strip("/")
    if not key:
        raise BadRequest("empty law id. Use an e-Gov law_id such as '129AC0000000089' (民法).")
    if key in _cache:
        return _cache[key]
    ident = key
    if not (_LAW_ID.match(key) or key.endswith("号")):
        ident = await _resolve_title(law_id.strip())
        if ident in _cache:
            return _cache[ident]
    r = await _api(f"law_data/{ident}", {"response_format": "xml"})
    if r is None:
        raise NotFound(f"e-Gov has no law {law_id!r}. Ids look like '129AC0000000089' (民法); "
                       "a 法令番号 ('明治二十九年法律第八十九号') or exact title ('民法') also works.")
    if not r.content.lstrip().startswith(b"<"):
        raise SourceError("e-Gov law_data returned a non-XML body")
    law = lru_put(_cache, key, _Law(etree.fromstring(r.content)), 4)
    return lru_put(_cache, ident, law, 4)


def _clip(s: str, n: int = 300) -> str:
    return s if len(s) <= n else s[:n] + "…"


# =========================================================================== #
# Adapter
# =========================================================================== #
class Japan(Jurisdiction):
    code = "jp"
    name = "Japan"
    languages = ("ja",)
    aliases = ("jpn", "japan", "nippon", "日本")
    sources = (
        Source("Case law: 裁判所 裁判例検索 (courts.go.jp), NOT wired in, search down since 2026-11-05 (e-Gov has no case law)",
               "https://www.courts.go.jp/app/hanrei_jp/search1", covers=(),
               licence="not reviewed", terms_url="https://www.courts.go.jp/"),
        Source("e-Gov 法令検索 / 法令API Version 2 (Digital Agency)", HOST,
               covers=("legislation",),
               licence="Public Data License 1.0 (公共データ利用規約 第1.0版, CC BY 4.0-compatible; "
                       "attribution required, mark edits) per e-Gov terms. Statutes are also "
                       "outside copyright (Copyright Act art. 13)",
               commercial_use=True, ai_use=None, auth="none",
               rate_limit="unknown (not in the OpenAPI spec); 1 s spacing, no 429 seen in "
                          "~25 requests (2026-11)",
               terms_url="https://www.e-gov.go.jp/terms"),
    )
    legislation_filters = {
        "search": "title (default: partial match on law names; falls back to text when "
                  "nothing matches) | text (full-text search of law bodies; supports "
                  "e-Gov AND/OR/NOT and * ? wildcards)",
        "law_type": "comma-separated: " + ", ".join(_LAW_TYPES),
    }
    min_interval = {"laws.e-gov.go.jp": 1.0}
    notes = ("Legislation only, Japanese text (e-Gov 法令API). Official English translations "
             "for some laws: japaneselawtranslation.go.jp (not wired in). Case law "
             "(courts.go.jp) not available: search under maintenance 2026-11.")
    gaps = (
        "Case law (courts.go.jp 裁判例検索): site down (search under maintenance, 2026-11-05)",
        "Case law by id (courts.go.jp /hanrei/<id>/ detail pages and PDFs): source exists and works but not built yet",
        "Official English translations (japaneselawtranslation.go.jp): not built yet",
        "Local ordinances (条例): not researched yet",
    )
    samples = {
        "legislation_query": "民法",
        "law_id": "129AC0000000089",
        "provision": "第七百九条",
    }

    async def search_legislation(self, query, *, limit, page, filters):
        query = (query or "").strip()
        if not query:
            raise BadRequest("empty query. Give a law name ('民法') or words to find in law texts.")
        mode = (filters.get("search") or "").strip().lower()
        if mode not in ("", "title", "text"):
            raise BadRequest(f"search={mode!r}: use 'title' or 'text'.")
        params: dict = {"response_format": "json"}
        if lt := (filters.get("law_type") or "").strip():
            bad = [t for t in lt.split(",") if t.strip() not in _LAW_TYPES]
            if bad:
                raise BadRequest(f"law_type {', '.join(bad)!r} unknown. Use: {', '.join(_LAW_TYPES)}.")
            params["law_type"] = ",".join(t.strip() for t in lt.split(","))
        limit, page = max(1, int(limit)), max(1, int(page))

        if mode in ("", "title"):
            # The API lists by promulgation date, so the core act can sit past page 1.
            # Fetch the first 100 and rank exact title, then prefix, then shortest.
            r = await _api("laws", {**params, "law_title": query, "limit": 100, "offset": 0})
            d = r.json() if r is not None else {}
            items = [_hit(x, x.get("current_revision_info") or x.get("revision_info") or {})
                     for x in d.get("laws") or []]
            items.sort(key=lambda h: (0 if h.title == query else 1 if h.title.startswith(query) else 2,
                                      len(h.title)))
            items = items[(page - 1) * limit:page * limit]
            if items or mode == "title" or page > 1:
                return Results(items=items, total=d.get("total_count"),
                               note="Title search (partial match on law names). For words in "
                                    "the text use filters={'search': 'text'}.")

        r = await _api("keyword", {**params, "keyword": query, "limit": limit,
                                   "offset": (page - 1) * limit})
        d = r.json() if r is not None else {}
        items = []
        for x in d.get("items") or []:
            snip = " … ".join(re.sub(r"<[^>]+>", "", s.get("text", "")) for s in x.get("sentences") or [])
            items.append(_hit(x, x.get("revision_info") or {}, _clip(snip)))
        note = ("Full-text search of law bodies. total counts laws; paging counts matching "
                "sentences, so a law can repeat on the next page.")
        if mode == "":
            note = "No law title matched; showing full-text results. " + note
        return Results(items=items, total=d.get("total_count"), note=note)

    async def get_legislation_toc(self, id):
        law = await _load(id)
        return Toc(id=law.law_id, title=law.title, url=law.url, entries=law.toc)

    async def get_legislation_provision(self, id, provision):
        law = await _load(id)
        label, el = law.find(provision)
        return Provision(law_id=law.law_id, law_title=law.title, provision=label,
                         text=_md(el), url=law.url, as_of=law.as_of)

    async def get_legislation_text(self, id):
        law = await _load(id)
        meta = {k: v for k, v in (("法令番号", law.law_num), ("law_revision_id", law.revision_id),
                                  ("分類", law.category), ("Status", law.status)) if v}
        return LawText(id=law.law_id, title=law.title, text=_md(law.law), url=law.url,
                       as_of=law.as_of, metadata=meta)


def _hit(x: dict, rev: dict, snippet: str = "") -> LawHit:
    info = x.get("law_info") or {}
    lid = info.get("law_id", "")
    return LawHit(
        id=lid, title=rev.get("law_title") or info.get("law_num", lid),
        type=info.get("law_type", ""), number=info.get("law_num", ""),
        date=iso_date(info.get("promulgation_date", "")),
        status=_STATUS.get(rev.get("repeal_status") or "None", rev.get("repeal_status") or ""),
        snippet=snippet, url=LAW_URL.format(id=lid),
    )
