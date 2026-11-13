"""Israel: legislation. Search and metadata from the Knesset's open OData service
(official); consolidated section text from the Open Law Book (ספר החוקים הפתוח) on
Hebrew Wikisource (crowd-maintained, non-official, CC BY-SA). Hebrew, untranslated.

No case law: supremedecisions.court.gov.il / elyon1.court.gov.il answer even
/robots.txt with a "זוהתה פעילות בלתי מורשת" (unauthorised activity) block page,
and the Courts Administration gives bulk/automated access to decisions only
under a signed undertaking (כתב התחייבות). gov.il is a Cloudflare challenge and
data.gov.il's robots.txt disallows /api/. So none of them is used.

Gotchas this code encodes:
  * Our law id is the Knesset's IsraelLawID (e.g. 2000292 = חוק החוזים (חלק כללי)).
    KNS_IsraelLaw gives name, status, basic-law flag and dates; it has no text.
    The Knesset's only official texts are the as-published gazette PDFs of the
    original law and each amendment (fs.knesset.gov.il); there is no free
    official consolidated text (Nevo/Takdin are paid).
  * Gazette PDFs: KNS_LawBinding (filter IsraelLawID) lists the original law
    (BindingTypeDesc "מקורי") and each amending law (LawID = the bill's BillID);
    KNS_DocumentBill rows with GroupTypeDesc "חוק - פרסום ברשומות" give the
    Sefer HaChukim scan (TIF/PDF/DOC) on fs.knesset.gov.il. We only link them:
    older PDFs are scans whose text layer comes out one word per line in
    reversed order, so they are not usable as text. fs.knesset.gov.il has no
    robots.txt (404).
  * Text comes from the Wikisource article page /wiki/<title> (robots.txt allows
    article pages and disallows /w/ and /api/, so we never use the MediaWiki API).
    The title is the Knesset name without the year suffix (", התשל"ג-1973") and
    without "[נוסח חדש]"/"[נוסח משולב]"; "חוק-יסוד" is written "חוק יסוד". The page
    links to main.knesset.gov.il/apps/legislation/main/laws/<IsraelLawID>; we
    require that link to match, so a same-named law never gets the wrong text.
  * Page markup (Open Law Book templates): div.law-number id="סעיף_25" +
    div.law-desc (section heading) + div.law-main (law-numberN / law-contentN
    pairs); headings h1.law-part, h2.law-section, h3.law-subsection,
    h4.law-subsubsection. Schedules use ids like "תוספת_2_פרט_1".
"""
from __future__ import annotations

import io
import re
from urllib.parse import quote

from lxml import html as lxml_html

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import LawHit, LawText, Provision, Results, Toc, TocEntry

ODATA = "https://knesset.gov.il/Odata/ParliamentInfo.svc"
WIKI = "https://he.wikisource.org/wiki/"
KNESSET_LAW = "https://main.knesset.gov.il/apps/legislation/main/laws/"

_STATUS = {"in force": "תקף", "repealed": "בטל"}
_HEADINGS = {"law-part": 0, "law-section": 1, "law-subsection": 2, "law-subsubsection": 3}

_meta_cache: dict[str, dict] = {}
_page_cache: dict[str, tuple[str, str, list]] = {}      # law id -> (wiki url, title, blocks)
_gazette_cache: dict[str, dict] = {}
_pdf_cache: dict[str, list] = {}                         # PDF url -> pages of lines


# --------------------------------------------------------------------------- #
# Knesset OData
# --------------------------------------------------------------------------- #
async def _odata(path: str) -> dict:
    url = f"{ODATA}/{path}"
    r = await _http.get(url)
    if r.status_code != 200:
        raise SourceError("Knesset OData request failed", r.status_code)
    try:
        return r.json()
    except ValueError as e:
        raise SourceError("Knesset OData: unexpected non-JSON reply", r.status_code) from e


def _lit(s: str) -> str:
    return "'" + s.replace("'", "''") + "'"


def _hit(x: dict) -> LawHit:
    lid = str(x["IsraelLawID"])
    kind = "חוק יסוד" if x.get("IsBasicLaw") else ("חוק תקציב" if x.get("IsBudgetLaw") else "")
    snippet = []
    if x.get("LatestPublicationDate"):
        snippet.append(f"פרסום אחרון: {_http.iso_date(x['LatestPublicationDate'])}")
    if x.get("ValidityFinishDate"):
        snippet.append(f"תוקף עד: {_http.iso_date(x['ValidityFinishDate'])}")
    return LawHit(id=lid, title=_http.clean(x.get("Name")), type=kind, number=lid,
                  date=_http.iso_date(x.get("PublicationDate")),
                  status=_http.clean(x.get("LawValidityDesc")), snippet="; ".join(snippet),
                  url=KNESSET_LAW + lid)


async def _meta(lid: str) -> dict:
    if not re.fullmatch(r"\d{5,8}", lid):
        raise BadRequest(f"Law id must be the Knesset IsraelLawID (digits), e.g. '2000292'; got {lid!r}")
    if lid in _meta_cache:
        return _meta_cache[lid]
    d = await _odata(f"KNS_IsraelLaw()?$filter=IsraelLawID%20eq%20{lid}&$format=json")
    rows = d.get("value") or []
    if not rows:
        raise NotFound(f"No Israeli law with IsraelLawID {lid} in the Knesset database")
    return _http.lru_put(_meta_cache, lid, rows[0], 200)


async def _bill_pdfs(ids: list) -> dict:
    """BillID -> as-published Sefer HaChukim PDF url (KNS_DocumentBill)."""
    if not ids:
        return {}
    flt = "%20or%20".join(f"BillID%20eq%20{i}" for i in ids)
    docs = (await _odata(f"KNS_DocumentBill()?$filter={flt}&$format=json")).get("value") or []
    pdf: dict = {}
    for d in docs:
        path = d.get("FilePath") or ""
        if d.get("GroupTypeDesc") == "חוק - פרסום ברשומות" and path.lower().endswith(".pdf"):
            pdf.setdefault(d["BillID"], path)
    rest = [i for i in ids if i not in pdf]          # older laws: files sit in KNS_DocumentLaw
    if rest:
        flt = "%20or%20".join(f"LawID%20eq%20{i}" for i in rest)
        for d in (await _odata(f"KNS_DocumentLaw()?$filter={flt}&$format=json")).get("value") or []:
            path = d.get("FilePath") or ""
            if d.get("GroupTypeDesc") == "חוק - פרסום ברשומות" and path.lower().endswith(".pdf"):
                pdf.setdefault(d["LawID"], path)
    return pdf


async def _gazette(lid: str) -> dict:
    """Official as-published gazette PDF links: the original law and the latest
    amendment, plus the amending laws' BillIDs. {} when the Knesset has none."""
    if lid in _gazette_cache:
        return _gazette_cache[lid]
    rows = (await _odata(f"KNS_LawBinding()?$filter=IsraelLawID%20eq%20{lid}&$format=json")).get("value") or []
    orig = [r["LawID"] for r in rows if r.get("BindingTypeDesc") == "מקורי"]
    amend = sorted({r["LawID"] for r in rows if r.get("BindingTypeDesc") == "מתקן"})
    want = {"original": orig[:1], "latest": amend[-1:]}
    out: dict = {"amendments": str(len(amend)), "amendment_ids": amend} if amend else {}
    if orig:
        out["original_id"] = orig[0]
    pdf = await _bill_pdfs(sorted({i for v in want.values() for i in v}))
    for k, v in want.items():
        if v and v[0] in pdf:
            out[k] = pdf[v[0]]
    return _http.lru_put(_gazette_cache, lid, out, 200)


# --------------------------------------------------------------------------- #
# Gazette PDF text layer -> logical (RTL) lines
# --------------------------------------------------------------------------- #
_HEB = re.compile(r"[\u05D0-\u05EA]")
_RUN = re.compile(r"[0-9A-Za-z]+|\s+|.")
_MIRROR = str.maketrans("()[]{}<>", ")(][}{><")


def _fix_cmaps(reader) -> None:
    """HadasaMFO font subsets (Reshumot, InDesign, ~2014+) number their low glyphs in
    ASCII order (0x0E ',', 0x0F '.', 0x10 '/', 0x11-0x1A digits) but the ToUnicode map
    sends some of them to Hebrew letters (',' -> פ, '.' -> ר, '3' -> ס). Repair those
    entries in memory before extracting."""
    seen = set()
    for p in reader.pages:
        for fo in (p.get("/Resources") or {}).get("/Font", {}).values():
            tu = fo.get_object().get("/ToUnicode")
            if tu is None or id(tu.get_object()) in seen:
                continue
            st = tu.get_object()
            seen.add(id(st))
            try:
                s = st.get_data().decode("latin1")
            except Exception:
                continue
            pairs = re.findall(r"<([0-9A-Fa-f]{4})>\s*<([0-9A-Fa-f]{4})>", s)
            if not any(int(c, 16) == 0x11 + i and int(u, 16) == 0x30 + i for c, u in pairs for i in range(10)):
                continue
            new = s
            for c, u in pairs:
                k = int(c, 16)
                if 0x0E <= k <= 0x1A and 0x5D0 <= int(u, 16) <= 0x5EA:
                    ch = ",./"[k - 0x0E] if k < 0x11 else chr(0x30 + k - 0x11)
                    new = re.sub(rf"<{c}>(\s*)<{u}>", rf"<{c}>\g<1><{ord(ch):04X}>", new)
            if new != s:
                try:
                    st.set_data(new.encode("latin1"))
                except Exception:
                    pass


def _frag(t: str) -> str:
    """pypdf already reverses fragments that contain Hebrew; others (digits,
    punctuation) are still in visual order: reverse their runs, keep digit runs."""
    t = t.replace("\n", "")
    return t if _HEB.search(t) else "".join(reversed(_RUN.findall(t)))


def _page_lines(page) -> list[str]:
    """One page -> logical lines: fragments grouped by baseline, ordered right to
    left; fragments sharing an x (one OCR word split at a hyphen or bracket) are in
    visual order, so reversed."""
    items = []

    def visit(t, cm, tm, _fd, _fs):
        if t.strip():
            items.append((tm[5] * cm[3] + cm[5], tm[4] * cm[0] + cm[4], t))
    page.extract_text(visitor_text=visit)
    rows: list = []
    for y, x, t in items:
        row = next((r for r in rows if abs(r[0] - y) <= 3), None)
        if row:
            row[1].append((x, t))
        else:
            rows.append([y, [(x, t)]])
    out = []
    for _, frs in sorted(rows, key=lambda r: -r[0]):
        groups: list = []
        for x, t in frs:
            if groups and abs(groups[-1][0] - x) < 0.5:
                groups[-1][1].append(t)
            else:
                groups.append([x, [t]])
        groups.sort(key=lambda g: -g[0])
        out.append(" ".join(_join([_frag(t) for t in reversed(g[1])]) for g in groups))
    return out


def _join(frags: list[str]) -> str:
    """Fragments of one x-group: some PDFs give a whole run of words one x, so put a
    space between two fragments that meet letter-to-letter."""
    out = ""
    for f in frags:
        if out and f and (out[-1].isalnum() and f[0].isalnum()):
            out += " "
        out += f
    return out


def _clean_line(s: str) -> str:
    s = re.sub(r"[\ufeff\u200e\u200f]", " ", s)
    s = re.sub(r"\s*\xad\s*", "-", s)                                 # OCR soft hyphen: חוק-יסוד
    s = re.sub(r"\(\s+", "(", s)
    s = re.sub(r"\s+\)", ")", s)
    s = re.sub(r"(\d) (?=[\u05D0-\u05EA](?:[\s(),.;:]|$))", r"\1", s)    # "13 א" -> "13א"
    s = re.sub(r"\s+([,.:;])(?=\s|$)", r"\1", s)
    return _http.clean(s)


def _pdf_pages(data: bytes) -> list[list[str]]:
    """Gazette PDF -> pages of logical Hebrew lines. Scanned issues carry an OCR text
    layer whose brackets are stored as visual glyphs; detect that ((א) read as )א()
    and mirror them."""
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(data))
    _fix_cmaps(reader)
    pages = [_page_lines(p) for p in reader.pages]
    flat = [ln for pg in pages for ln in pg]
    bad = sum(len(re.findall(r"\)[\u05D0-\u05EA0-9]{1,3}\(", ln)) for ln in flat)
    good = sum(len(re.findall(r"\([\u05D0-\u05EA0-9]{1,3}\)", ln)) for ln in flat)
    if bad > good:
        pages = [[ln.translate(_MIRROR) for ln in pg] for pg in pages]
    return [[c for c in (_clean_line(ln) for ln in pg) if c] for pg in pages]


async def _gazette_doc(gid: str) -> tuple[str, str, str, list, dict]:
    """'<IsraelLawID>/original' or '<IsraelLawID>/<BillID>' -> (law id, title, pdf url,
    pages, metadata) from the official Sefer HaChukim PDF."""
    m = re.fullmatch(r"(\d{5,8})/(original|\d{3,8})", gid)
    if not m:
        raise BadRequest("Official gazette text ids look like '2000046/original' (the law as first "
                         "published) or '2000046/155642' (an amending law's BillID, listed in "
                         f"get_legislation_text metadata); got {gid!r}")
    lid, which = m.groups()
    meta = await _meta(lid)
    g = await _gazette(lid)
    bill = g.get("original_id") if which == "original" else int(which)
    if bill is None or (which != "original" and bill not in g.get("amendment_ids", [])):
        raise NotFound(f"No {'original' if which == 'original' else 'amending law ' + which} gazette "
                       f"publication for IsraelLawID {lid} in the Knesset database; see {KNESSET_LAW}{lid}")
    url = g.get("original") if which == "original" else None
    url = url or (await _bill_pdfs([bill])).get(bill)
    if not url:
        raise NotFound(f"The Knesset database has no Sefer HaChukim PDF for BillID {bill} "
                       f"(IsraelLawID {lid}); see {KNESSET_LAW}{lid}")
    if url not in _pdf_cache:
        r = await _http.get(url)
        if r.status_code != 200 or not r.content.startswith(b"%PDF"):
            raise SourceError("fs.knesset.gov.il gazette PDF request failed", r.status_code)
        _http.lru_put(_pdf_cache, url, _pdf_pages(r.content), 20)
    pages = _pdf_cache[url]
    if sum(len(ln) for pg in pages for ln in pg) < 40:
        raise NotFound(f"The gazette PDF has no text layer (scan only): {url}")
    name = _http.clean(meta.get("Name"))
    title = name if which == "original" else f"{name} – חוק מתקן (BillID {bill})"
    md = {"IsraelLawID": lid, "BillID": str(bill), "PDF": url, "רשומה רשמית": KNESSET_LAW + lid,
          "מקור הנוסח": "ספר החוקים (רשומות), PDF רשמי; טקסט שחולץ משכבת הטקסט (OCR בסריקות ישנות)",
          "נוסח": ("נוסח משולב רשמי כפי שפורסם" if "נוסח משולב" in " ".join(pages[0][:6])
                   else "כפי שפורסם, ללא תיקונים מאוחרים" if which == "original" else "חוק מתקן כפי שפורסם")}
    return lid, title, url, pages, md


# --------------------------------------------------------------------------- #
# Open Law Book (Hebrew Wikisource) article pages
# --------------------------------------------------------------------------- #
def _titles(name: str) -> list[str]:
    """Wikisource title candidates for a Knesset law name."""
    t = _http.clean(name)
    t = re.sub(r",?\s*ה?תש[^,]*?[-–]\s*\d{4}\s*$", "", t)         # ", התשל"ג-1973"
    t = re.sub(r",?\s*\d{4}\s*$", "", t)                         # ", 1965"
    out = []
    for v in (t, re.sub(r"\s*\[(?:נוסח (?:חדש|משולב)|ה?תש[^\]]*)\]", "", t)):
        for w in (v, v.replace("חוק-יסוד", "חוק יסוד")):
            if _http.clean(w) not in out:
                out.append(_http.clean(w))
    return out


def _cls(el) -> str:
    return el.get("class", "") if isinstance(el.tag, str) else ""


def _label(anchor: str) -> str:
    return _http.clean(anchor.replace("_", " "))


def _main_paras(main) -> list[str]:
    """law-main -> paragraphs: '(א) text', nested levels indented by marker only."""
    out, num = [], ""
    for el in main.iter():
        c = _cls(el)
        if re.search(r"\blaw-number\d\b", c):
            num = _http.clean(el.text_content())
        elif re.search(r"\blaw-content\d\b", c):
            txt = _http.clean(el.text_content())
            if txt:
                out.append(f"{num} {txt}".strip())
            num = ""
    if not out:
        txt = _http.clean(main.text_content())
        if txt:
            out.append(txt)
    return out


def _blocks(doc) -> list[tuple]:
    """Ordered blocks: ("h", level, text) | ("s", label, heading_line, [paras]) | ("p", text)."""
    law = doc.xpath('//div[@id="law-content"]')
    if not law:
        raise SourceError("Wikisource page has no Open Law Book content (div#law-content)")
    blocks, cur, skip_toc = [], None, False
    for ch in law[0]:
        c = _cls(ch)
        if not c and ch.tag in ("p",) and not _http.clean(ch.text_content()).strip():
            continue
        if ch.tag in ("h1", "h2", "h3", "h4", "h5"):
            cur = None
            if "law-title" in c:
                continue
            txt = _http.clean(ch.text_content())
            if txt == "תוכן עניינים":
                skip_toc = True
                continue
            skip_toc = False
            lvl = next((v for k, v in _HEADINGS.items() if re.search(rf"\b{k}\b", c)), 1)
            blocks.append(("h", lvl, txt))
        elif re.search(r"\blaw-number\b", c):
            skip_toc = False
            anchor = ch.get("id") or ""
            num = _http.clean(ch.text_content())
            cur = ["s", _label(anchor) if anchor else num, num, []]
            blocks.append(cur)
        elif "law-desc" in c and cur is not None:
            cur[2] = f"{cur[2]} {_http.clean(ch.text_content())}".strip()
        elif "law-main" in c and cur is not None:
            cur[3] += _main_paras(ch)
        elif "law-cleaner" in c or ch.tag == "hr" or skip_toc:
            continue
        elif ch.xpath('.//*[contains(@class,"law-note")]') or "law-note" in c:
            continue                                           # publication list: metadata
        else:
            txt = _http.clean(ch.text_content())
            if txt and not txt.endswith("מתוך"):
                cur = None
                blocks.append(("p", txt))
    return blocks


def _publications(doc) -> str:
    notes = doc.xpath('//div[@id="law-content"]//div[contains(@class,"law-note")]')
    if not notes:
        return ""
    return _http.clean(re.sub(r"^\d+\s*", "", _http.clean(notes[0].text_content())))


async def _page(lid: str) -> tuple[str, str, list, str]:
    if lid in _page_cache:
        return _page_cache[lid]
    meta = await _meta(lid)
    name = _http.clean(meta.get("Name"))
    for title in _titles(name):
        url = WIKI + quote(title.replace(" ", "_"))
        r = await _http.get(url)
        if r.status_code == 404:
            continue
        if r.status_code != 200:
            raise SourceError("he.wikisource.org page request failed", r.status_code)
        ids = set(re.findall(r"legislation/main/laws/(\d+)", r.text))
        if ids and lid not in ids:
            continue                                         # same title, different law
        if 'id="law-content"' not in r.text:
            continue                                         # disambiguation or plain page
        doc = lxml_html.fromstring(r.content)
        res = (url, name, _blocks(doc), _publications(doc))
        return _http.lru_put(_page_cache, lid, res, 20)
    g = await _gazette(lid)
    pdf = f" Official as-published gazette PDF: {g['original']}." if g.get("original") else ""
    raise NotFound(f"No consolidated text for {name} (IsraelLawID {lid}) in the Open Law Book "
                   f"on Hebrew Wikisource.{pdf} Official record and gazette PDFs: {KNESSET_LAW}{lid}")


def _norm_prov(p: str) -> str:
    p = _http.clean(p).replace("_", " ")
    p = re.sub(r"^(?:סעיף|סע['׳]|ס['׳]|section|sec\.?|s\.|article|art\.?)\s*", "", p, flags=re.I)
    p = p.rstrip(".").replace("״", "").replace('"', "").replace("׳", "").replace("'", "")
    p = re.sub(r"^0+(?=\d)", "", p)                       # '012' -> '12'
    return re.sub(r"^(\d+)\s+(?=[\u05d0-\u05ea])", r"\1", p)    # '1 א' -> '1א'


def _sec_md(b) -> str:
    return "\n\n".join([f"**{b[2]}**"] + b[3])


# --------------------------------------------------------------------------- #
class Israel(Jurisdiction):
    code = "il"
    name = "Israel"
    languages = ("he",)
    aliases = ("israel", "isr", "ישראל")
    sources = (
        Source(name="Knesset OData (ParliamentInfo) – Israeli law database (official)",
               url="https://knesset.gov.il/Odata/ParliamentInfo.svc/",
               covers=("legislation",),
               licence="no licence stated; laws are not copyright-protected (Copyright Act 2007, s. 6)",
               commercial_use=None, ai_use=None, auth="none",
               rate_limit="unknown; 1 s spacing, no 429 seen in ~20 requests (2026-11)",
               terms_url="https://main.knesset.gov.il/"),
        Source(name="Sefer HaChukim (ספר החוקים, Reshumot) as-published PDFs on fs.knesset.gov.il (official)",
               url="https://fs.knesset.gov.il/",
               covers=("legislation",),
               licence="no licence stated; laws are not copyright-protected (Copyright Act 2007, s. 6)",
               commercial_use=None, ai_use=None, auth="none",
               rate_limit="unknown; 1 s spacing, no 429 seen in ~25 PDF requests (2026-11); no robots.txt (404)",
               terms_url="https://main.knesset.gov.il/",
               warning="Text is machine-read from the PDF's text layer: scans (roughly pre-2005) carry OCR "
                       "with about 1-5% misread words, and numbers/punctuation or margin headings can land "
                       "out of place; check the linked PDF before quoting.",
               probe={"law_id": "2000046/original", "provision": "עמוד 1"}),
        Source(name="Open Law Book (ספר החוקים הפתוח), Hebrew Wikisource – non-official "
                    "(crowd-maintained, Wikimedia Foundation)",
               url="https://he.wikisource.org/wiki/ספר_החוקים_הפתוח",
               covers=("legislation",),
               licence="CC BY-SA 4.0 (Wikimedia Terms of Use s. 7)",
               commercial_use=True, ai_use=None, auth="none",
               rate_limit="unknown for article pages; 1 s spacing, no 429 seen (2026-11)",
               terms_url="https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use",
               warning="Consolidated text is volunteer-maintained on Wikisource, not an official "
                       "version; check the Knesset gazette PDFs before relying on it.",
               official=False),
    )
    legislation_filters = {
        "status": "in force | repealed",
        "basic_law": "true: Basic Laws (חוקי יסוד) only",
        "since": "year (2022) or date (2022-06-30): laws whose latest publication (original or amendment) is on or after it",
    }
    min_interval = {"knesset.gov.il": 1.0, "fs.knesset.gov.il": 1.0, "he.wikisource.org": 1.0}
    notes = ("Legislation only, in Hebrew: Knesset law database (official metadata, id = IsraelLawID) "
             "+ consolidated text from the non-official Open Law Book on Wikisource + official as-published "
             "text from the Sefer HaChukim PDFs (ids '<IsraelLawID>/original' and '<IsraelLawID>/<BillID>' "
             "for each amending law). No case law: the court sites block automated access and require a "
             "signed undertaking.")
    gaps = (
        "Case law (Supreme Court sites): blocks our client (unauthorised-activity page); bulk access needs permission (signed undertaking)",
        "Official consolidated text: not published online free (Nevo/Takdin are paid); the consolidated text here is non-official Wikisource; the official text is per publication (original law + each amending law), except the few laws the Knesset re-published as נוסח משולב",
        "Official gazette text quality: read from the PDF text layer; pre-~2005 scans are OCR (about 1-5% misread words in samples), and later born-digital PDFs can misplace numbers, punctuation and margin headings; sections are not split (pages only)",
        "Mandate-era ordinances (פקודה): the official PDF is the Dinei Medinat Israel [נוסח חדש] republication where the Knesset database holds it (KNS_DocumentLaw); scanned OCR, same quality caveats",
        "Search covers law names only (Knesset OData), not the text; regulations (תקנות, Kovetz HaTakanot on gov.il, Cloudflare-walled): not covered",
    )
    samples = {
        "legislation_query": "חוק החוזים",
        "law_id": "2000292",
        "provision": "סעיף 25",
    }

    # ------------------------------------------------------------- legislation
    async def search_legislation(self, query, *, limit, page, filters) -> Results[LawHit]:
        f = dict(filters or {})
        conds = []
        q = _http.clean(query)
        if q:
            # the Knesset WAF answers HTTP 473 to more than three substringof() clauses:
            # match the three longest words
            words = sorted(dict.fromkeys(q.split()), key=len, reverse=True)[:3]
            conds += [f"substringof({_lit(w)},Name)" for w in words]
        if f.get("status"):
            s = str(f["status"]).strip().lower()
            if s not in _STATUS:
                raise BadRequest(f"status must be one of {', '.join(_STATUS)}")
            conds.append(f"LawValidityDesc eq {_lit(_STATUS[s])}")
        if f.get("basic_law"):
            b = str(f["basic_law"]).strip().lower()
            if b not in ("true", "false"):
                raise BadRequest("basic_law must be true or false")
            conds.append(f"IsBasicLaw eq {b}")
        if f.get("since"):
            m = re.fullmatch(r"(\d{4})(?:-(\d{2})-(\d{2}))?", str(f["since"]).strip())
            if not m:
                raise BadRequest("since must be a year (2022) or a date (2022-06-30)")
            conds.append(f"LatestPublicationDate ge datetime'{m[1]}-{m[2] or '01'}-{m[3] or '01'}T00:00:00'")
        if not conds:
            raise BadRequest("Give a search query (Hebrew words of the law's name) or a filter.")
        base = ("KNS_IsraelLaw()?$filter=" + quote(" and ".join(conds))
                + "&$format=json&$inlinecount=allpages&$top={top}&$skip={skip}"
                + "&$orderby=" + quote("IsFavoriteLaw desc,IsBasicLaw desc,LatestPublicationDate desc"))
        # Knesset OData caps $top at 100: fetch a larger limit as consecutive chunks of 100 so that the
        # requested page size, the render numbering and the page offset stay consistent
        limit = int(limit)
        d, rows = None, []
        while len(rows) < limit:
            top = min(100, limit - len(rows))
            part = await _odata(base.format(top=top, skip=(page - 1) * limit + len(rows)))
            d = d or part
            got = part.get("value") or []
            rows += got
            if len(got) < top:
                break
        d = dict(d or {}, value=rows)
        items = [_hit(x) for x in d.get("value") or []]
        for x in d.get("value") or []:
            _http.lru_put(_meta_cache, str(x["IsraelLawID"]), x, 200)
        try:
            total = int(d.get("odata.count"))
        except (TypeError, ValueError):
            total = None
        return Results(items=items, total=total,
                       note="Searches law names (Hebrew; the three longest words must appear). Text by id is the "
                            "non-official Open Law Book (Wikisource); '<id>/original' gives the official "
                            "Sefer HaChukim text as first published.")

    @staticmethod
    async def _official(lid: str):
        """Gazette document for a '/'-id, or for a plain id with no Open Law Book page
        (falls back to the original as published). None: use Wikisource."""
        if "/" in lid:
            return await _gazette_doc(lid)
        try:
            await _page(lid)
            return None
        except NotFound:
            if not (await _gazette(lid)).get("original_id"):
                raise
            doc = await _gazette_doc(f"{lid}/original")
            doc[4]["הערה"] = "אין דף בספר החוקים הפתוח; מוצג החוק המקורי כפי שפורסם, ללא תיקונים"
            return doc

    async def get_legislation_toc(self, id) -> Toc:
        lid = _http.clean(id)
        doc = await self._official(lid)
        if doc:
            _, title, pdf, pages, _ = doc
            return Toc(id=lid, title=title, url=pdf,
                       entries=[TocEntry(title=f"עמוד {n} – {(pg[0] if pg else '')[:80]}", provision=f"עמוד {n}")
                                for n, pg in enumerate(pages, 1)])
        url, title, blocks, _ = await _page(lid)
        entries = []
        for b in blocks:
            if b[0] == "h":
                entries.append(TocEntry(title=b[2], level=b[1]))
            elif b[0] == "s":
                entries.append(TocEntry(title=b[2], level=4, provision=b[1]))
        return Toc(id=lid, title=title, url=url, entries=entries)

    async def get_legislation_provision(self, id, provision) -> Provision:
        lid = _http.clean(id)
        doc = await self._official(lid)
        if doc:
            _, title, pdf, pages, _ = doc
            m = re.fullmatch(r"(?:עמוד|עמ['׳]?|page|p\.?)?\s*(\d+)", _http.clean(provision), flags=re.I)
            if not m:
                raise BadRequest("The official gazette text is split by PDF page: give 'עמוד 1', 'page 1' or '1'")
            n = int(m.group(1))
            if not 1 <= n <= len(pages):
                raise NotFound(f"No page {n} in {title}: the PDF has {len(pages)} pages. Official "
                               "'/original' and '/<BillID>' texts are split by PDF page only, not by "
                               "section, so '12' means page 12; for section numbers use the plain id "
                               f"'{lid.split('/')[0]}' (non-official Open Law Book)")
            return Provision(law_id=lid, law_title=title, provision=f"עמוד {n}",
                             text="\n\n".join(pages[n - 1]), url=f"{pdf}#page={n}")
        url, title, blocks, _ = await _page(lid)
        want = _norm_prov(provision)
        if not want:
            raise BadRequest("Give a provision, e.g. 'סעיף 25' or '25'")
        secs = [b for b in blocks if b[0] == "s"]
        hit = (next((b for b in secs if b[1] == _http.clean(provision)), None)
               or next((b for b in secs if _norm_prov(b[1]) == want), None))
        if not hit:
            raise NotFound(f"No provision {provision!r} in {title}. Labels look like "
                           f"'סעיף 1', 'סעיף 214א', 'תוספת 2 פרט 1'; see get_legislation_toc.")
        anchor = quote(hit[1].replace(" ", "_"))
        return Provision(law_id=lid, law_title=title, provision=hit[1], text=_sec_md(hit),
                         url=f"{url}#{anchor}")

    async def get_legislation_text(self, id) -> LawText:
        lid = _http.clean(id)
        doc = await self._official(lid)
        if doc:
            law, title, pdf, pages, md = doc
            g = await _gazette(law)
            if g.get("amendment_ids"):
                md["חוקים מתקנים (ids)"] = ", ".join(f"{law}/{b}" for b in g["amendment_ids"])
            return LawText(id=lid, title=title, url=pdf, metadata=md,
                           text="\n\n".join(f"### עמוד {n}\n\n" + "\n".join(pg)
                                              for n, pg in enumerate(pages, 1) if pg))
        url, title, blocks, pubs = await _page(lid)
        parts = []
        for b in blocks:
            if b[0] == "h":
                parts.append("#" * min(b[1] + 2, 6) + " " + b[2])
            elif b[0] == "s":
                parts.append(_sec_md(b))
            else:
                parts.append(b[1])
        meta = await _meta(lid)
        g = await _gazette(lid)
        md = {"IsraelLawID": lid, "סטטוס": _http.clean(meta.get("LawValidityDesc")),
              "פרסומים (ס״ח)": pubs, "רשומה רשמית": KNESSET_LAW + lid,
              "ס״ח רשמי – החוק המקורי (PDF)": g.get("original", ""),
              "ס״ח רשמי – התיקון האחרון (PDF)": g.get("latest", ""),
              "מספר חוקים מתקנים": g.get("amendments", ""),
              "נוסח רשמי כטקסט (id)": f"{lid}/original" if g.get("original_id") else "",
              "מקור הנוסח": "ספר החוקים הפתוח (ויקיטקסט), לא נוסח רשמי"}
        return LawText(id=lid, title=title, text="\n\n".join(parts), url=url,
                       metadata={k: v for k, v in md.items() if v})
