"""Poland: legislation from the Sejm ELI API, case law from the Ministry of Justice
Portal Orzeczeń Sądów Powszechnych (common courts).

Gotchas this code encodes (verified 2026-11-05 from a UK IP):
  * Sejm ELI API (api.sejm.gov.pl/eli) has title/metadata search only, no full text.
    The default order is newest first, not relevance.
  * An act's own text.html is its ORIGINAL wording (the 1964 Kodeks cywilny HTML has
    no art. 449^1). The consolidated wording is a separate act, an Obwieszczenie
    ("tekst jednolity") listed under references["Inf. o tekście jednolitym"]. Recent ones
    are often PDF-only (textHTML false), so we use the newest one that has HTML and say
    which newer PDF-only consolidations exist. as_of is its legalStatusDate (stan prawny).
  * In a tekst jednolity HTML, <section id="part_1"> is the announcement and
    <section id="part_2"> the consolidated act. Articles quoted inside the announcement
    sit in a .cite-box and are skipped. Superscript article numbers are <SUP>:
    data-id "arti_449_1" = "art. 449^1". Footnote refs are a.gloss-link (dropped).
  * The API's per-unit text.html/artykul=N fragment needs the full structural path
    (ksiega=.../tytul=.../artykul=...), so we fetch the whole text once and cache it.
  * api.sejm.gov.pl has no robots.txt (its WAF answers /robots.txt with "Request Rejected").
  * orzeczenia.ms.gov.pl is a Tapestry app. Search is a GET with 18 path segments,
    values Tapestry-encoded ("$N" = empty, "$0020" = space). 10 hits per page, fixed.
    Decision ids are the portal's own document ids
    ("155515000004027_VIII_GC_000386_2020_Uz_2021-05-13_001"); /content/$N/<id> has the
    text, /details/$N/<id> the metadata. The portal has a CAPTCHA bot check.
  * SAOS (saos.org.pl, academic) is NOT used: its robots.txt disallows /api/ for all agents.
"""
from __future__ import annotations

import asyncio
import re
from urllib.parse import quote, unquote

from lxml import html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from .._http import require_iso as _date
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

ELI = "https://api.sejm.gov.pl/eli"
ISAP = "https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id="
MS = "https://orzeczenia.ms.gov.pl"

_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_DOC_ID = re.compile(r"^\d{15}_[0-9A-Za-z_]+_\d{4}-\d{2}-\d{2}_\d{3}$")
_STRUCT = ("book", "part", "titl", "bran", "chpt", "schp")
_PARSER = lhtml.HTMLParser(encoding="utf-8")
_SUPERS = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #
async def _fetch(url: str, what: str, **kw):
    # orzeczenia.ms.gov.pl occasionally drops a connection with no response;
    # one retry (still throttled by min_interval) fixes it. api.sejm.gov.pl reset both an
    # immediate try and its retry (ReadError, two health runs 2026-11-10), so wait 2 s first.
    for attempt in (1, 2):
        try:
            r = await _http.get(url, **kw)
            break
        except Exception as e:  # network error
            if attempt == 1:
                await asyncio.sleep(2)
            else:
                raise SourceError(f"{what}: network error {type(e).__name__} {e}", "network") from e
    if r.status_code == 404:
        raise NotFound(f"{what}: not found")
    if r.status_code != 200:
        raise SourceError(f"{what} failed", r.status_code)
    return r


async def _json(url: str, what: str, **kw):
    r = await _fetch(url, what, **kw)
    try:
        return r.json()
    except ValueError as e:
        raise SourceError(f"{what}: unexpected non-JSON reply (WAF block page?)", r.status_code) from e


# --------------------------------------------------------------------------- #
# Legislation: ids and labels
# --------------------------------------------------------------------------- #
def _parse_law_id(id: str) -> str:
    """'DU/1964/93' | 'Dz.U. 1964 nr 16 poz. 93' | 'Dz.U. 2024 poz. 1061' | 'WDU19640160093'
    | an eli.gov.pl / api.sejm.gov.pl URL -> 'DU/1964/93'."""
    s = re.sub(r"\s+", " ", unquote(id or "")).strip()
    m = re.search(r"(?:^|/)(DU|MP)/(\d{4})/(\d+)(?:/|$)", s, re.I)
    if m:
        return f"{m[1].upper()}/{m[2]}/{int(m[3])}"
    m = re.match(r"^W(DU|MP)(\d{4})\d{3}(\d{4})$", s, re.I)
    if m:
        return f"{m[1].upper()}/{m[2]}/{int(m[3])}"
    m = re.match(r"^(Dz\.?\s?U\.?|M\.?\s?P\.?)\s*(?:z\s*)?(\d{4})(?:\s*r\.)?\s*(?:,?\s*nr\s*\d+)?\s*,?\s*poz\.?\s*(\d+)$",
                 s, re.I)
    if m:
        pub = "DU" if m[1].upper().startswith("DZ") else "MP"
        return f"{pub}/{m[2]}/{int(m[3])}"
    raise BadRequest(f"Unrecognised Polish act id {id!r}. Use the ELI id from search_legislation, "
                     "e.g. 'DU/1964/93' (also 'Dz.U. 1964 nr 16 poz. 93' or 'WDU19640160093').")


def _norm_provision(p: str) -> tuple[str, str]:
    """-> (kind, number): ('arti', '449^1') | ('para', '5') | ('', '415') when bare."""
    s = re.sub(r"([⁰¹²³⁴⁵⁶⁷⁸⁹]+)", lambda m: "^" + m[1].translate(_SUPERS), (p or "").strip())
    kind = ""
    m = re.match(r"^(artyku[łl]|art\.?|article)\s*", s, re.I)
    if m:
        kind, s = "arti", s[m.end():]
    else:
        m = re.match(r"^(§|par\.?|paragraf)\s*", s, re.I)
        if m:
            kind, s = "para", s[m.end():]
    s = re.sub(r"\s+", "", s).rstrip(".")
    m = re.match(r"^(\d+[a-z]*)(?:\((\d+)\)|[\^_](\d+))?$", s, re.I)
    if not m:
        raise BadRequest(f"Unrecognised provision {p!r}; use e.g. 'art. 415', '415', "
                         "'art. 449^1' or '§ 5'.")
    sup = m[2] or m[3]
    return kind, m[1].lower() + (f"^{sup}" if sup else "")


def _label(kind: str, num: str) -> str:
    return f"art. {num}" if kind == "arti" else f"§ {num}"


# --------------------------------------------------------------------------- #
# Legislation: HTML of the act
# --------------------------------------------------------------------------- #
def _kind(el) -> str:
    m = re.search(r"\bunit_(\w+)", el.get("class") or "")
    return m[1] if m else ""


def _is_unit(el) -> bool:
    return el.tag == "div" and " unit " in f" {el.get('class') or ''} "


def _t(el) -> str:
    return _http.clean("".join(el.itertext())) if el is not None else ""


def _child(el, tag: str, cls: str = ""):
    for c in el:
        if c.tag == tag and (not cls or cls in (c.get("class") or "").split()):
            return c
    return None


def _parse(content: bytes):
    return lhtml.document_fromstring(content, parser=_PARSER)


def _struct_heading(div) -> str:
    # libxml2 closes <h3> at its <P> children, so the heading is h3 + the <p>s after it.
    parts = []
    for c in div:
        if c.tag == "div" and "unit-inner" in (c.get("class") or ""):
            break
        if c.tag in ("h3", "p"):
            parts.append(c)
    title = next((_t(x) for c in parts for x in c.xpath("descendant-or-self::*[contains(@class,'pro-title-unit')]")), "")
    full = _http.clean(" ".join(_t(c) for c in parts))
    num = _http.clean(full.replace(title, "", 1)) if title else full
    return f"{num} – {title}" if title and num else (title or num)


def _render_unit(div, out: list[str], depth: int = 0) -> None:
    kind = _kind(div)
    if kind in _STRUCT:
        out.append(f"{'#' * min(6, 2 + depth)} {_struct_heading(div)}")
    head = _t(_child(div, "h3")) if kind not in _STRUCT else ""
    pending = head
    inner = _child(div, "div", "unit-inner")
    for c in (inner if inner is not None else []):
        if not isinstance(c.tag, str):
            continue
        if _is_unit(c):
            if pending:
                out.append(f"**{pending}**" if kind == "arti" else pending)
                pending = ""
            _render_unit(c, out, depth + (1 if kind in _STRUCT else 0))
        elif "cite-box" in (c.get("class") or ""):
            sub: list[str] = []
            for u in _top_units(c):
                _render_unit(u, sub, 6)
            if not sub:
                sub = [_t(c)]
            out.extend("> " + s.lstrip("#").strip() for s in sub if s)
        else:
            t = _t(c) if c.tag != "table" else _http.html_to_md(lhtml.tostring(c, encoding="unicode"))
            if not t:
                continue
            if pending:
                t = (f"**{pending}** {t}" if kind == "arti" else f"{pending} {t}")
                pending = ""
            out.append(t)
    if pending:
        out.append(f"**{pending}**" if kind == "arti" else pending)


class _Law:
    def __init__(self, key: str, meta: dict, src: dict, newer_pdf: list[dict], root):
        self.key, self.meta, self.src, self.newer_pdf = key, meta, src, newer_pdf
        self.root = root            # the section holding the act's own text
        self.consolidated = bool((src.get("references") or {}).get("Tekst jednolity dla aktu"))

    @property
    def title(self) -> str:
        return (self.meta.get("title") or self.key).rstrip(".")

    @property
    def url(self) -> str:
        return ISAP + self.meta["address"] if self.meta.get("address") else f"{ELI}/acts/{self.key}"

    @property
    def text_url(self) -> str:
        return f"{ELI}/acts/{self.src['ELI']}/text.html"

    @property
    def as_of(self) -> str:
        if not self.consolidated:
            return self.src.get("legalStatusDate") or ""
        return self.src.get("legalStatusDate") or self.src.get("announcementDate") or ""

    def note(self) -> str:
        if not self.consolidated:
            if (self.meta.get("references") or {}).get("Akty zmieniające"):
                return ("Original text as published: amendments are not applied and no consolidated "
                        "text with HTML exists. Check ISAP for the current wording.")
            return ""
        s = (f"Consolidated text: {self.src.get('displayAddress', self.src['ELI'])}"
             f" (stan prawny {self.as_of or 'unknown'}).")
        if self.newer_pdf:
            s += (" Newer consolidated text(s) published as PDF only, not used here: "
                  + ", ".join(f"{n.get('displayAddress', n['ELI'])}"
                              + (f" (stan prawny {n['legalStatusDate']})" if n.get("legalStatusDate") else "")
                              for n in self.newer_pdf) + ".")
        return s

    def warning(self) -> str:
        if not (self.consolidated and self.newer_pdf):
            return ""
        n = self.newer_pdf[0]
        return (f"**NOT THE CURRENT TEXT:** this is the consolidated text as of {self.as_of or 'unknown'}; "
                f"a newer one, {n.get('displayAddress', n['ELI'])}"
                + (f" (stan prawny {n['legalStatusDate']})" if n.get("legalStatusDate") else "")
                + f", exists only as PDF: {ELI}/acts/{n['ELI']}/text.pdf. Later amendments are not reflected below.")

    def units(self, kind: str) -> list:
        """Top-level provisions of the act: articles, or § where the act has no articles."""
        xp = (f".//div[contains(concat(' ',@class,' '),' unit_{kind} ')]"
              "[not(ancestor::*[contains(@class,'cite-box')])]")
        if kind == "para":
            xp += "[not(ancestor::div[contains(concat(' ',@class,' '),' unit_arti ')])]"
        return self.root.xpath(xp)

    def provisions(self) -> tuple[str, list]:
        arts = self.units("arti")
        return ("arti", arts) if arts else ("para", self.units("para"))


def _num(div) -> str:
    """data-id 'arti_449_1' -> '449^1'; 'para_5' -> '5'."""
    parts = (div.get("data-id") or "").split("_")[1:]
    return (parts[0].lower() + "".join(f"^{x}" for x in parts[1:])) if parts else ""


class _PdfLaw:
    """An act the Sejm ELI API holds only as PDF (e.g. the 1997 Constitution): the text layer of
    the PDF as published, split into articles. Same surface as _Law for the three legislation tools."""
    def __init__(self, key: str, meta: dict, blocks: list[tuple[str, str, list[str]]]):
        self.key, self.meta, self.blocks = key, meta, blocks      # (kind 'arti'|'head'|'pre', num/title, lines)
        self.text_url = f"{ELI}/acts/{key}/text.pdf"
        self.title = (meta.get("title") or key).rstrip(".")
        self.url = ISAP + meta["address"] if meta.get("address") else f"{ELI}/acts/{key}"
        self.as_of = meta.get("announcementDate") or ""
        self.note = ("Text extracted from the Sejm's PDF of the act as originally published "
                     "(not HTML): amendments are NOT applied and extraction may drop or garble "
                     "characters. Check the wording against the PDF / ISAP before relying on it.")

    def body(self, lines: list[str]) -> str:
        return re.sub(r"\s*\n\s*", " ", "\n".join(lines)).strip()


_PDF_NOISE = re.compile(r"^(Dziennik Ustaw Nr \d+ - \d+ -|Poz\s*\.\s*\d+)$")
_PDF_ART = re.compile(r"^Art\.\s*(\d+[a-z]*)\.$")


async def _pdf_law(key: str, meta: dict) -> _PdfLaw:
    r = await _fetch(f"{ELI}/acts/{key}/text.pdf", f"Sejm ELI PDF {key}")
    try:
        raw = await asyncio.to_thread(_http.pdf_text, r.content)
    except Exception as e:
        raise SourceError(f"{key}: cannot read the PDF at {ELI}/acts/{key}/text.pdf "
                          f"({type(e).__name__})", "pdf") from e
    if not raw:
        raise SourceError(f"{key} exists only as a scanned PDF without a text layer, so Fontes "
                          f"cannot read it: {ELI}/acts/{key}/text.pdf", "pdf-no-text")
    lines = [ln for ln in raw.replace("\xad\n", "").splitlines()
             if ln.strip() and not _PDF_NOISE.match(ln.strip())]
    blocks: list[tuple[str, str, list[str]]] = [("pre", "", [])]
    i = 0
    while i < len(lines):
        ln = lines[i].strip()
        if m := _PDF_ART.match(ln):
            blocks.append(("arti", m[1].lower(), []))
        elif re.match(r"^(Rozdział|Dział|Tytuł) [IVXLC\d]+[a-z]?$", ln):
            title = [ln]
            while i + 1 < len(lines) and lines[i + 1].isupper():
                i += 1
                title.append(lines[i].strip())
            blocks.append(("head", " - ".join(title), []))
            blocks.append(("skip", "", []))     # unnumbered sub-headings up to the next article
        else:
            blocks[-1][2].append(ln)
        i += 1
    if not any(b[0] == "arti" for b in blocks):
        t = (meta.get("title") or "").rstrip(".")
        raise NotFound(f"{key} is a real act ({t}) but its text has no numbered articles (Art. N), "
                       "so there is no article to fetch; for the act you want, find its id with "
                       "search_legislation" if t else
                       f"{key} has no numbered articles (Art. N); find the act's id with search_legislation")
    return _PdfLaw(key, meta, blocks)


_laws: dict[str, _Law] = {}


async def _law(id: str) -> _Law:
    key = _parse_law_id(id)
    if key in _laws:
        return _laws[key]
    meta = await _json(f"{ELI}/acts/{key}", f"Sejm ELI act {key}")
    refs = meta.get("references") or {}
    src, newer = None, []
    if refs.get("Tekst jednolity dla aktu"):           # the id is itself a tekst jednolity
        src = meta if meta.get("textHTML") else None
    else:
        tjs = sorted(refs.get("Inf. o tekście jednolitym") or [],
                     key=lambda r: tuple(int(x) for x in r["id"].split("/")[1:]), reverse=True)
        for r in tjs[:4]:
            m = await _json(f"{ELI}/acts/{r['id']}", f"Sejm ELI act {r['id']}")
            if m.get("textHTML"):
                src = m
                break
            newer.append(m)
        if src is None and meta.get("textHTML"):
            src, newer = meta, []
    if src is None:
        return _http.lru_put(_laws, key, await _pdf_law(key, meta), 3)
    r = await _fetch(f"{ELI}/acts/{src['ELI']}/text.html", f"Sejm ELI text {src['ELI']}")
    doc = _parse(r.content)
    for a in doc.xpath("//a[contains(@class,'gloss-link')]|//script|//div[@id='toc']"):
        a.drop_tree()
    for sup in doc.xpath("//sup"):
        sup.text = "^" + (sup.text or "")
    sections = doc.xpath("//section[starts-with(@id,'part_')]")
    want = "part_2" if (src.get("references") or {}).get("Tekst jednolity dla aktu") else "part_1"
    root = next((s for s in sections if s.get("id") == want), sections[0] if sections else doc)
    return _http.lru_put(_laws, key, _Law(key, meta, src, newer, root), 3)


# --------------------------------------------------------------------------- #
# Case law: Portal Orzeczeń Sądów Powszechnych
# --------------------------------------------------------------------------- #
_TAP_SAFE = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.:")


def _tap(v) -> str:
    """Tapestry 5 URL encoding of one path value."""
    s = str(v or "").strip()
    if not s:
        return "$N"
    return "".join(c if c in _TAP_SAFE else f"${ord(c):04x}" for c in s)


def _doc_id(id: str) -> str:
    s = (id or "").strip().rstrip("/")
    s = s.rsplit("/", 1)[-1] if "/" in s else s
    if not _DOC_ID.match(s):
        raise BadRequest(f"Unrecognised decision id {id!r}. Use the portal document id from "
                         "search_caselaw, e.g. '155515000004027_VIII_GC_000386_2020_Uz_2021-05-13_001'.")
    return s


def _check_page(doc, what: str) -> None:
    if doc.xpath("//*[@id='captchaImage']"):
        raise SourceError(f"{what}: the portal answered with a CAPTCHA bot check; try again later", 429)


def _dl(doc) -> dict[str, str]:
    out = {}
    for dt in doc.xpath("//div[@id='content']//dl/dt"):
        dd = dt.getnext()
        if dd is not None and dd.tag == "dd":
            out[_t(dt).rstrip(":")] = _t(dd)
    return out


class Poland(Jurisdiction):
    code = "pl"
    name = "Poland"
    languages = ("pl",)
    aliases = ("pol", "poland", "polska")
    sources = (
        Source(
            name="Portal Orzeczeń Sądów Powszechnych (Ministry of Justice)",
            url=MS,
            covers=("caselaw",),
            licence="not stated on the portal; court judgments are official documents excluded "
                    "from copyright (art. 4 Polish Copyright Act); re-use of public-sector "
                    "information under the 2021 Open Data Act",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown, none documented; the portal has a CAPTCHA bot check (not "
                       "triggered in ~10 requests, 2026-11); using 1 s spacing",
            terms_url=f"{MS}/cookies",
        ),
        Source(
            name="Sejm ELI API (Chancellery of the Sejm)",
            url="https://api.sejm.gov.pl",
            covers=("legislation",),
            licence="not stated in the API docs; normative acts and official documents are excluded "
                    "from copyright (art. 4 Polish Copyright Act)",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown, none documented; no 429 in ~20 requests (2026-11); using 1 s spacing",
            terms_url="https://api.sejm.gov.pl/eli_pl.html",
        ),
    )
    caselaw_filters = {
        "case_number": "sygnatura, e.g. 'I C 100/24'",
        "date_from": "decided on or after, YYYY-MM-DD",
        "date_to": "decided on or before, YYYY-MM-DD",
        "legal_basis": "podstawa prawna as written by the court, e.g. 'art. 415 kc'",
        "sort": "'relevance' (default) or 'date' (newest decision first)",
    }
    legislation_filters = {
        "year": "year of publication, e.g. '1964'",
        "type": "act type as the source names it: 'Ustawa', 'Rozporządzenie', 'Obwieszczenie', ...",
        "publisher": "'DU' (Dziennik Ustaw, default both) or 'MP' (Monitor Polski)",
        "in_force": "'true' to list only acts in force",
    }
    min_interval = {"api.sejm.gov.pl": 1.0, "orzeczenia.ms.gov.pl": 1.0}
    notes = ("Case law: common courts only (Supreme, Administrative and Constitutional courts are not "
             "covered). Laws: title search only; text is the newest consolidated text that has HTML "
             "(newer PDF-only ones are named). Cite acts as 'DU/1964/93', provisions as 'art. 415'.")
    gaps = (
        "Supreme Court (sn.pl) and Constitutional Tribunal (trybunal.gov.pl): reachable, not "
         "researched yet",
        "Administrative courts (NSA/WSA, orzeczenia.nsa.gov.pl): robots.txt disallows /cbo/find "
         "and /cbo/search",
        "Newest consolidated texts published only as PDF: source exists but not built yet (older "
         "HTML consolidation served)",
        "Full-text legislation search: the Sejm ELI API has title/metadata search only",
        "Local law (voivodeship official journals): not researched yet",
    )
    samples = {
        "caselaw_query": "umowa najmu",
        "decision_id": "155515000004027_VIII_GC_000386_2020_Uz_2021-05-13_001",
        "legislation_query": "kodeks cywilny",
        "law_id": "DU/1964/93",
        "provision": "art. 415",
    }

    # ----------------------------------------------------------------- caselaw
    async def _search_page(self, query: str, filters: dict, page: int):
        segs = ["$N"] * 18
        segs[0] = _tap(query)
        if v := filters.get("case_number"):
            segs[1] = _tap(v)
        if v := filters.get("date_from"):
            segs[7] = _date(v, "date_from")
        if v := filters.get("date_to"):
            segs[8] = _date(v, "date_to")
        if v := filters.get("legal_basis"):
            segs[12] = _tap(v)
        sort = str(filters.get("sort") or "relevance").lower()
        if sort not in ("relevance", "date"):
            raise BadRequest("sort must be 'relevance' or 'date'")
        segs[15], segs[16] = ("data" if sort == "date" else "score"), "descending"
        segs[17] = str(page)
        r = await _fetch(f"{MS}/search/advanced/" + "/".join(segs), "Portal Orzeczeń search")
        doc = _parse(r.content)
        _check_page(doc, "Portal Orzeczeń search")
        m = re.search(r"Znaleziona liczba wyników\s*([\d\s\xa0]+)", _t(doc.body))
        total = int(re.sub(r"\D", "", m[1])) if m else 0
        hits = []
        for res in doc.xpath("//section[@id='results']//div[@class='single_result']"):
            a = next(iter(res.xpath(".//h4/a")), None)
            if a is None:
                continue
            did = a.get("href").rstrip("/").rsplit("/", 1)[-1]
            ps = [_t(p) for p in res.xpath("./div[@class='title']/p")]
            court = next((p for p in ps if p.startswith("Sąd")), "")
            date = next((p.split(":", 1)[1].strip() for p in ps if p.startswith("Data orzeczenia")), "")
            kind = ps[0] if ps and not ps[0].startswith(("Sąd", "Data")) else ""
            cn = _t(a)
            hits.append(DecisionHit(
                id=did, title=f"{court} {cn}".strip() + (f" ({kind})" if kind else ""),
                court=court, date=date if _ISO.match(date) else "", case_number=cn,
                snippet=_t(next(iter(res.xpath(".//blockquote")), None))[:300],
                url=f"{MS}/content/$N/{did}"))
        return hits, total

    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        start = (page - 1) * limit
        first, items, total = start // 10 + 1, [], 0
        p = first
        while len(items) < (start - (first - 1) * 10) + limit:
            hits, total = await self._search_page(query, filters, p)
            items += hits
            if len(hits) < 10:
                break
            p += 1
        off = start - (first - 1) * 10
        return Results(items=items[off:off + limit], total=total,
                       note="Common courts only (district, regional, appeal); published selection, "
                            "anonymised. 10 hits per source page. The source orders tied hits (same "
                            "score or date) differently from one request to the next, so pages can "
                            "repeat or skip hits.")

    async def get_decision(self, id):
        did = _doc_id(id)
        r = await _fetch(f"{MS}/content/$N/{did}", "Portal Orzeczeń decision")
        doc = _parse(r.content)
        _check_page(doc, "Portal Orzeczeń decision")
        # newer judgments carry extra classes ("single_result invalid"), so match on the token
        body = next(iter(doc.xpath("//div[@id='content']//div[contains(concat(' ', normalize-space(@class), ' '), ' single_result ')]")), None)
        head = _t(next(iter(doc.xpath("//div[@id='content']/h2")), None))
        if body is None or not head:
            raise NotFound(f"No decision {did!r} on the Portal Orzeczeń Sądów Powszechnych")
        text = _http.html_to_md(lhtml.tostring(body, encoding="unicode"))
        r2 = await _fetch(f"{MS}/details/$N/{did}", "Portal Orzeczeń details")
        meta = _dl(_parse(r2.content))
        m = re.match(r"^(.*?) - (.*?) (Sąd .*?) z (\d{4}-\d{2}-\d{2})$", head)
        cn = meta.get("Sygnatura") or (m[1] if m else "")
        court = meta.get("Sąd") or (m[3] if m else "")
        date = m[4] if m else (re.search(r"_(\d{4}-\d{2}-\d{2})_\d{3}$", did)[1])
        kind = m[2] if m else ""
        extra = {k: v for k, v in meta.items()
                 if k not in ("Tytuł", "Sygnatura", "Sąd", "Data orzeczenia", "Teza") and v}
        if kind:
            extra = {"Rodzaj": kind, **extra}
        return Decision(id=did, title=f"{court} {cn}".strip() + (f" ({kind})" if kind else ""),
                        text=text, url=f"{MS}/content/$N/{did}", court=court, date=date,
                        case_number=cn, summary=meta.get("Teza", ""), metadata=extra)

    # ------------------------------------------------------------- legislation
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        params: dict[str, str | int] = {"limit": limit, "offset": (page - 1) * limit}
        rerank = bool(query and query.strip()) and page * limit <= 500
        if rerank:  # the API is newest-first; fetch a window so the base act can be lifted
            params["limit"], params["offset"] = 500, 0
        if query and query.strip():
            params["title"] = query.strip()
        if v := filters.get("year"):
            if not re.fullmatch(r"\d{4}", str(v)):
                raise BadRequest(f"year must be four digits, got {v!r}")
            params["year"] = str(v)
        if v := filters.get("type"):
            params["type"] = str(v)
        if v := filters.get("publisher"):
            if str(v).upper() not in ("DU", "MP"):
                raise BadRequest("publisher must be 'DU' or 'MP'")
            params["publisher"] = str(v).upper()
        if str(filters.get("in_force", "")).lower() in ("1", "true", "yes"):
            params["inForce"] = "1"
        d = await _json(f"{ELI}/acts/search", "Sejm ELI search", params=params)
        raw = d.get("items") or []
        if rerank:
            q = query.strip().lower()
            # the base act is titled '... - <name>' (e.g. 'Ustawa z dnia 23 kwietnia 1964 r. - Kodeks cywilny')
            raw = sorted(raw, key=lambda x: not (x.get("type") == "Ustawa" and
                         re.match(r"^ustawa z dnia [\w ]+ r\.(?: -)? " + re.escape(q) + r"\.?$",
                                  (x.get("title") or "").lower())))
            raw = raw[(page - 1) * limit:page * limit]
        items = [LawHit(id=x["ELI"], title=x.get("title") or x["ELI"], type=x.get("type") or "",
                        number=x.get("displayAddress") or "", date=x.get("announcementDate") or "",
                        status=x.get("status") or "", url=ISAP + x["address"])
                 for x in raw]
        return Results(items=items, total=d.get("totalCount"),
                       note="Title search only (no full text), newest first (a base act titled '... - <query>' is listed first). For a code's current text "
                            "use the base act (e.g. 'DU/1964/93'), not its Obwieszczenie.")

    async def get_legislation_toc(self, id):
        law = await _law(id)
        if isinstance(law, _PdfLaw):
            return Toc(id=law.key, title=law.title, url=law.url, entries=[
                TocEntry(title=b[1], level=0) if b[0] == "head"
                else TocEntry(title=_label("arti", b[1]), level=1, provision=_label("arti", b[1]))
                for b in law.blocks if b[0] in ("head", "arti")])
        kind, provs = law.provisions()
        wanted = set(provs)
        entries = []
        for el in law.root.iter("div"):
            if el in wanted:
                entries.append(TocEntry(title=_t(_child(el, "h3")).rstrip("."),
                                        level=_depth(el), provision=_label(kind, _num(el))))
            elif _is_unit(el) and _kind(el) in _STRUCT and not el.xpath("ancestor::*[contains(@class,'cite-box')]"):
                entries.append(TocEntry(title=_struct_heading(el), level=_depth(el)))
        return Toc(id=law.key, title=law.title, url=law.url, entries=entries)

    async def get_legislation_provision(self, id, provision):
        want_kind, num = _norm_provision(provision)
        law = await _law(id)
        if isinstance(law, _PdfLaw):
            if want_kind == "para":
                raise NotFound(f"{law.key} is divided into articles, not §; try {_label('arti', num)!r}")
            b = next((b for b in law.blocks if b[0] == "arti" and b[1] == num), None)
            if b is None:
                raise NotFound(f"{_label('arti', num)} not found in {law.key}")
            return Provision(law_id=law.key, law_title=law.title, provision=_label("arti", num),
                             text=f"**{_label('arti', num)}** {law.body(b[2])}\n\n_{law.note}_",
                             url=law.text_url, as_of=law.as_of)
        kind, provs = law.provisions()
        if want_kind and want_kind != kind:
            raise NotFound(f"{law.key} is divided into {'articles' if kind == 'arti' else '§'}, "
                           f"not {'articles' if want_kind == 'arti' else '§'}; try {_label(kind, num)!r}")
        el = next((p for p in provs if _num(p) == num), None)
        if el is None:
            raise NotFound(f"{_label(kind, num)} not found in {law.key}")
        out: list[str] = [law.warning()] if law.warning() else []
        _render_unit(el, out)
        if note := law.note():
            out.append(f"_{note}_")
        return Provision(law_id=law.key, law_title=law.title, provision=_label(kind, num),
                         text="\n\n".join(out), url=f"{law.text_url}#{el.get('id', '')}",
                         as_of=law.as_of)

    async def get_legislation_text(self, id):
        law = await _law(id)
        if isinstance(law, _PdfLaw):
            parts = [f"**{_label('arti', b[1])}** {law.body(b[2])}" if b[0] == "arti"
                     else (f"## {b[1]}" if b[0] == "head" else law.body(b[2]))
                     for b in law.blocks if b[0] != "skip"]
            meta = {"Number": law.meta.get("displayAddress", ""), "Status": law.meta.get("status", ""),
                    "In force from": law.meta.get("entryIntoForce", ""), "Text": law.note,
                    "Text source": law.text_url}
            return LawText(id=law.key, title=law.title, text="\n\n".join(p for p in parts if p),
                           url=law.url, as_of=law.as_of, metadata={k: v for k, v in meta.items() if v})
        out: list[str] = [law.warning()] if law.warning() else []
        for u in _top_units(law.root):
            _render_unit(u, out)
        meta = {"Number": law.meta.get("displayAddress", ""), "Status": law.meta.get("status", ""),
                "In force from": law.meta.get("entryIntoForce", ""), "Text": law.note(),
                "Text source": law.text_url}
        return LawText(id=law.key, title=law.title, text="\n\n".join(out), url=law.url,
                       as_of=law.as_of, metadata={k: v for k, v in meta.items() if v})


def _top_units(root) -> list:
    """Units under root whose nearest unit ancestor is outside root."""
    out = []
    for u in root.iter("div"):
        if not _is_unit(u):
            continue
        for a in u.iterancestors():
            if a is root:
                out.append(u)
                break
            if _is_unit(a):
                break
    return out


def _depth(el) -> int:
    return sum(1 for a in el.iterancestors("div") if _is_unit(a) and _kind(a) in _STRUCT)
