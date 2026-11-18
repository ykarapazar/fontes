"""Vietnam: legislation from the Ministry of Justice database (vbpl.vn) and the Government
Portal's legal documents system (vanban.chinhphu.vn), and case law = the Supreme People's
Court precedents (án lệ) from anle.toaan.gov.vn. Vietnamese only.

Gotchas this code encodes (verified 2026-11-06 from a UK IP):
  * vanban.chinhphu.vn is ASP.NET WebForms: search = GET the list page for __VIEWSTATE, then
    POST the form. The page-size select (max 500) caps the hit set, but rows still come 50
    a page; further pages
    are GridView postbacks (`__EVENTARGUMENT=Page$N`) carrying the results page's view state.
    The texts are the PDFs as published (original wording, not consolidated);
    older ones (e.g. the 2015 Civil Code) are scanned images and raise SourceError.
  * vbpl.vn (Ministry of Justice national database; Next.js, rebuilt 2026; verified 2026-11-10):
    its search runs through /api/, which robots.txt disallows, but robots.txt allows the rest
    and lists sitemap.xml. The index's "Trung ương" block names 12 sitemaps (~58k central
    documents, ~4 MB each); search loads them once (24 h cache) and matches the URL slug
    (unaccented title words + number). A detail page works by its trailing id alone
    (/van-ban/chi-tiet/32801 or a UUID); the document is the "initialDoc" object in the
    React flight data (self.__next_f.push chunks); its content "$2b" points to a text row
    "2b:T<hex UTF-8 byte length>,<html>". Old laws write bare "Điều 57" without a dot.
    www.vbpl.vn has a wrong certificate. congbobanan.toaan.gov.vn (published judgments) and
    phapdien.moj.gov.vn reset/timed out from the UK.
  * anle.toaan.gov.vn serves an incomplete TLS chain (leaf CN=toaan.gov.vn without the
    "GlobalSign RSA OV SSL CA 2018" intermediate). It works only because _http verifies
    against the OS trust store, which fetches the intermediate on macOS/Windows; on Linux
    _http loads it from intermediates.pem. It is Oracle WebCenter: the keyword search is an
    ADF postback, but the list of all precedents (~90, 10 a page) is plain GET
    (`?selectedPage=N`), so search reads that list (cached in memory for 6 h) and matches
    number, title and field locally. Full text: precedents 01-26 (2016-2018) are inline HTML
    on the detail page; 27-82 are Word-made PDFs with a text layer (0.5 MB, ~20 s from the UK);
    the 2026 ones (83-90) are ~6 MB scanned PDFs (minutes to download, no text layer), so
    PDFs over 3 MB are not read and raise SourceError pointing to the page.
"""
from __future__ import annotations

import asyncio
import html as _html
import json
import re
import time as _time
import unicodedata

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc, TocEntry

VC = "https://vanban.chinhphu.vn"
VC_LIST = VC + "/he-thong-van-ban?classid=1&mode=1"
VC_DETAIL = VC + "/?pageid=27160&docid={id}"
_FORM = "ctrl_191017_163$"
_PAGE = 50  # rows per result page (the page-size select is ignored on a plain postback)

VB = "https://vbpl.vn"

AL = "https://anle.toaan.gov.vn"
AL_LIST = AL + "/webcenter/portal/anle/anle?selectedPage={p}&docType=AnLe&mucHienThi=9009"
AL_DETAIL = AL + "/webcenter/portal/anle/chitietanle?dDocName={id}"
AL_FILE = AL + "/webcenter/ShowProperty?nodeId=/UCMServer/{id}"
AL_COURT = "Hội đồng Thẩm phán Tòa án nhân dân tối cao"
_AL_TTL = 6 * 3600
_AL_MAX_PDF = 3 * 2**20  # text-layer PDFs are ~0.5 MB; the scanned 2026 ones ~6 MB

_clean = _http.clean
_texts: dict = {}
_al_index: dict = {}  # "rows" -> (time, [row dicts])


def _fold(s: str) -> str:
    """Vietnamese-insensitive matching: lower case, diacritics dropped, đ -> d."""
    s = (s or "").replace("đ", "d").replace("Đ", "D")
    s = unicodedata.normalize("NFD", s)
    return _clean("".join(c for c in s if unicodedata.category(c) != "Mn").lower())


def _strip(h: str) -> str:
    return _clean(_html.unescape(re.sub(r"<[^>]+>", " ", h or "")))


# --------------------------------------------------------------------------- #
# PDF text -> paragraphs
# --------------------------------------------------------------------------- #
_BLOCK_START = re.compile(
    r"^(Điều\s+\d|Chương\s+[IVXLC\d]|Mục\s+\d|Phần\s+(thứ|[IVXLC\d])|\d+\.\s|\d+\.\d+\.?\s|[a-zđ]\)\s"
    r"|[-–•+]\s|Nguồn án lệ|Vị trí nội dung|Khái quát nội dung|Nội dung án lệ|Quy định của pháp luật"
    r"|Từ khóa|NHẬN THẤY|NHẬN ĐỊNH|XÉT THẤY|QUYẾT ĐỊNH|Căn cứ|Theo đề nghị|\[\d+\]|“?Điều\s+\d)")


def _is_heading_line(ln: str) -> bool:
    letters = [c for c in ln if c.isalpha()]
    return len(letters) >= 4 and all(c.isupper() for c in letters)


_VOWEL_MARKED = "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ"
# pypdf often breaks a syllable after its initial consonant(s): "l ập", "tr ước", "ch ịu".
# A lone consonant cluster is never a Vietnamese word, so glue it to a following vowel.
_SPLIT_SYLLABLE = re.compile(
    r"(?<![\wÀ-ỹ])((?:ngh|ng|nh|ch|tr|th|kh|ph|gh|gi|qu|[bcdđghklmnpqrstvx]))"
    r" (?=[" + _VOWEL_MARKED + _VOWEL_MARKED.upper() + "])", re.I)
_GAZETTE = re.compile(r"^\d*\s*CÔNG BÁO\s*/\s*Số .*?/\s*Ngày [\d-]+\s*\d*$")


# ... and after an i/y, u or o glide: "nhi ệm", "thu ộc", "ho ặc" (only vowels that
# rarely start a word are matched).
_SPLIT_GLIDE = re.compile(r"(?<![\wÀ-ỹ])((?:ngh|ng|nh|ch|tr|th|kh|ph|gh|gi|qu|[bcdđghklmnpqrstvx])"
                          r"(?:[iy] (?=[ềếểễệỀẾỂỄỆ])|u (?=[ồốổỗộỒỐỔỖỘ])|o (?=[ặạẶẠ])))", re.I)


def _fix_syllables(s: str) -> str:
    s = _SPLIT_SYLLABLE.sub(r"\1", s)
    return _SPLIT_GLIDE.sub(lambda m: m[1][:-1], s)


def _reflow(text: str) -> list[str]:
    """pdf_text lines -> paragraphs: join wrapped lines, keep structural starts separate,
    drop page numbers and Official Gazette running heads, mend split syllables."""
    pars: list[str] = []
    prev_heading = False
    for ln in text.splitlines():
        ln = _fix_syllables(_clean(ln))
        if not ln or re.fullmatch(r"\d{1,4}", ln) or _GAZETTE.match(ln):
            continue
        heading = _is_heading_line(ln)
        if heading and prev_heading:  # a heading wrapped over two lines
            pars[-1] += " " + ln
            continue
        new = (not pars or heading or prev_heading or _BLOCK_START.match(ln)
               or re.search(r"[.:;!?”]$", pars[-1])
               or (_ART.match(pars[-1]) and ln[:1].isupper()))  # article heading ends
        if new:
            pars.append(ln)
        else:
            pars[-1] += " " + ln
        prev_heading = heading
    return pars


# --------------------------------------------------------------------------- #
# Legislation (vanban.chinhphu.vn)
# --------------------------------------------------------------------------- #
def _hidden_fields(h: str) -> dict:
    return {n: _html.unescape(v) for n, v in
            re.findall(r'<input type="hidden" name="([^"]+)" id="[^"]*" value="([^"]*)"', h)}


async def _vc_post(form: dict) -> str:
    r = await _http.post(VC_LIST, data=form)
    if r.status_code != 200:
        raise SourceError(_http.error("vanban.chinhphu.vn", "search failed", r.status_code), r.status_code)
    return r.text


def _parse_vc_rows(h: str) -> list[LawHit]:
    out = []
    for m in re.finditer(r"docid=(\d+)[^']*'>\s*<span class=\"code\">([^<]*)</span>\s*"
                         r"<span class=\"issue-v2\">([^<]*)</span>.*?<span class=\"substract\">(.*?)</span>",
                         h, re.S):
        number, title = _clean(_html.unescape(m[2])), _strip(m[4])
        out.append(LawHit(id=m[1], title=title or number, number=number,
                          date=_http.iso_date(_clean(m[3])), url=VC_DETAIL.format(id=m[1])))
    return out


_ART = re.compile(r"^Điều\s+(\d+[a-zđ]?)\s*[.:]", re.I)
_TOC_HEAD = re.compile(r"^(Phần\s+(thứ\s+\S+|[IVXLC\d]+)|Chương\s+[IVXLC\d]+|Mục\s+\d+)\b", re.I)
_LABEL_IN = re.compile(r"^(?:dieu|d\.|art(?:icle|\.)?|article)?\s*(\d+[a-z]?)\.?$")


def _norm_label(s: str) -> str:
    """'Điều 5', 'dieu 5', '5', 'art. 5', 'Article 5' -> 'Điều 5'."""
    m = _LABEL_IN.match(_fold(s).replace("dieu", "dieu "))
    if not m:
        raise BadRequest(f"Provision {s!r} not understood. Use e.g. 'Điều 5' or '5'.")
    return f"Điều {m[1]}"


async def _vc_doc(id: str) -> dict:
    id = _clean(id)
    m = re.search(r"docid=(\d+)", id)
    id = m[1] if m else id
    if not re.fullmatch(r"\d{1,8}", id):
        raise BadRequest(f"Bad id {id!r}: use the numeric docid from search_legislation "
                         f"(e.g. '183188'), or a vanban.chinhphu.vn ?docid= URL.")
    if id in _texts:
        return _texts[id]
    url = VC_DETAIL.format(id=id)
    r = await _http.get(url)
    if r.status_code != 200:
        raise SourceError(_http.error("vanban.chinhphu.vn", "document page failed", r.status_code), r.status_code)
    h = r.text
    title = re.search(r'id="ctrl_\d+_\d+_lb_noidung">(.*?)</span>', h, re.S)
    meta = {}
    for k, v in re.findall(r'<td class="col1"[^>]*>([^<]+)</td>\s*<td>(.*?)</td>', h, re.S):
        if "Tài liệu" not in k:
            meta[_clean(k)] = _strip(v)
    if not title or not _strip(title[1]) or not meta.get("Số ký hiệu"):
        raise NotFound(f"No document with docid {id} on vanban.chinhphu.vn.")
    pdfs = list(dict.fromkeys(re.findall(r'href="(https://datafiles\.chinhphu\.vn/[^"]+\.pdf)"[^>]*class="view-file"', h)))
    text = ""
    for pdf in pdfs:
        p = await _http.get(pdf)
        if p.status_code == 200 and p.content[:5] == b"%PDF-":
            text = _http.pdf_text(p.content)
            if len(text) > 200:
                break
    if len(text) <= 200:
        why = "has no PDF attachment" if not pdfs else "is a scanned PDF without a text layer (no OCR here)"
        raise SourceError(f"vanban.chinhphu.vn document {id} {why}. Open it at {url}", "no-text")
    pars = _reflow(text)
    doc = {"id": id, "title": _strip(title[1]), "url": url, "meta": meta, "pdf": pdf, "pars": pars}
    return _http.lru_put(_texts, id, doc, 8)


def _segments(pars: list[str]) -> list[tuple[str, int, int]]:
    """(label, start, end) for each article; the first occurrence of a number wins, so
    articles quoted inside amending provisions (they start with “) are not split out."""
    starts, seen = [], set()
    for i, p in enumerate(pars):
        m = _ART.match(p)
        if m:
            lab = f"Điều {m[1]}"
            if lab not in seen:
                seen.add(lab)
                starts.append((lab, i))
        elif _TOC_HEAD.match(p) and starts:
            starts.append(("", i))  # heading ends the previous article
    out = []
    for n, (lab, i) in enumerate(starts):
        if lab:
            end = starts[n + 1][1] if n + 1 < len(starts) else len(pars)
            out.append((lab, i, end))
    return out


# --------------------------------------------------------------------------- #
# Legislation: vbpl.vn (Ministry of Justice national database)
# --------------------------------------------------------------------------- #
_VB_ID = re.compile(r"(?:https?://(?:www\.)?vbpl\.vn/van-ban/chi-tiet/)?([a-z0-9-]*--)?"
                    r"(\d{1,7}|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/?")
_VB_NUM = re.compile(r"(?:^|-)so-(\d+[a-z]?)-((?:19|20)\d\d)-([a-z]+\d*)(?:-([a-z]+\d*))?")
# slug prefix -> rank: constitution, codes, laws, consolidated texts, ordinances, resolutions
_VB_TIER = (("hien-phap-", 0), ("bo-luat-", 1), ("luat-", 2), ("van-ban-hop-nhat-", 3),
            ("phap-lenh-", 4), ("nghi-quyet-", 5), ("lenh-", 6))
_vb_index: dict = {}  # "slugs" -> (time, [slug])
_vb_lock = asyncio.Lock()


async def _vb_slugs() -> list[str]:
    """All central (Trung ương) document slugs from the sitemap index (12 files, ~58k
    entries), cached for 24 h. Search runs on these because the site's own search is
    under /api/, which robots.txt disallows."""
    async with _vb_lock:
        hit = _vb_index.get("slugs")
        if hit and _time.time() - hit[0] < 24 * 3600:
            return hit[1]
        r = await _http.get(VB + "/sitemap.xml")
        if r.status_code != 200:
            raise SourceError(_http.error("vbpl.vn", "sitemap index failed", r.status_code), r.status_code)
        central = r.text.split("Trung ương", 1)[-1].split("Địa phương", 1)[0]
        maps = re.findall(r"<loc>([^<]+)</loc>", central)
        if not maps:
            raise SourceError("vbpl.vn: no central sitemaps in the index (layout changed?)")
        slugs = []
        for u in maps:
            s = await _http.get(u, timeout=120)
            if s.status_code != 200:
                raise SourceError(_http.error("vbpl.vn", "sitemap failed", s.status_code), s.status_code)
            slugs += re.findall(r"<loc>https://vbpl\.vn/van-ban/chi-tiet/([^<]+)</loc>", s.text)
        _vb_index["slugs"] = (_time.time(), slugs)
        return slugs


def _vb_number(name: str):
    """('31/2024/QH15', '2024', match) from a slug name; agency codes lose diacritics."""
    m = _VB_NUM.search(name)
    if not m:
        return "", "", None
    two = m[4] and (m.end() == len(name) or m[3] in ("tt", "nd", "qd", "nq", "ttlt", "ct", "vbhn"))
    code = m[3] + (f"-{m[4]}" if two else "")
    end = m.end() if two else m.end(3)
    return f"{m[1]}/{m[2]}/{code.upper()}", m[2], (m.start(), end)


def _vb_hit(slug: str) -> LawHit:
    name = slug.split("--")[0]
    number, _, span = _vb_number(name)
    title = name.replace("-", " ")
    if name.endswith("-so-khong-so"):  # vbpl.vn's own docNum is "Không số" (e.g. the 1995 Civil Code)
        number, title = "Không số", title[:-len(" so khong so")] + " (vbpl.vn lists it as 'Không số': no number; open it for its date)"
    elif span:
        title = (name[:span[0]].replace("-", " ") + f" số {number} " +
                 name[span[1]:].replace("-", " ")).strip()
    return LawHit(id=slug, title=_clean(title[:1].upper() + title[1:]), number=number, date="",
                  url=f"{VB}/van-ban/chi-tiet/{slug}")


def _rsc(h: str) -> str:
    """Join the Next.js flight-data chunks embedded in the page."""
    return "".join(json.loads('"' + c + '"')
                   for c in re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)</script>', h, re.S))


async def _vb_doc(id: str) -> dict:
    key = _VB_ID.fullmatch(_clean(id))[2]
    if key in _texts:
        return _texts[key]
    url = f"{VB}/van-ban/chi-tiet/{key}"
    r = await _http.get(url, timeout=60)
    if r.status_code == 404:
        raise NotFound(f"No document {key} on vbpl.vn.")
    if r.status_code != 200:
        raise SourceError(_http.error("vbpl.vn", "document page failed", r.status_code), r.status_code)
    big = _rsc(r.text)
    i = big.find('"initialDoc":')
    try:
        doc = json.JSONDecoder().raw_decode(big, i + len('"initialDoc":'))[0] if i >= 0 else None
    except ValueError:
        raise SourceError("vbpl.vn: document data not readable (layout changed?)")
    if not isinstance(doc, dict) or not doc.get("title"):
        raise NotFound(f"No document {key} on vbpl.vn.")
    c = (doc.get("documentContent") or {}).get("content") or ""
    if re.fullmatch(r"\$[0-9a-f]+", c):  # reference to a text row "<ref>:T<hex byte length>,<html>"
        b = big.encode()
        t = re.search(rb"(?:^|[\n\]}])" + re.escape(c[1:].encode()) + rb":T([0-9a-f]+),", b)
        c = b[t.end():t.end() + int(t[1], 16)].decode("utf-8", "replace") if t else ""
    pars = [re.sub(r"\*\*", "", p).strip() for p in _http.html_paragraphs(c)]
    pars = [re.sub(r"^(Điều\s+\d+[a-zđ]?)$", r"\1.", p) for p in pars if p]  # old laws: bare "Điều 5"
    if sum(map(len, pars)) < 200:
        raise SourceError(f"vbpl.vn document {key} has no text on the page (it may only offer "
                          f"a file). Open it at {url}", "no-text")

    def val(k):
        v = doc.get(k)
        return _clean(str((v.get("name") if isinstance(v, dict) else v) or ""))

    meta = {"Số ký hiệu": val("docNum"), "Loại văn bản": val("docType"),
            "Cơ quan ban hành": val("agencyName"), "Ngày ban hành": _http.iso_date(doc.get("issueDate")),
            "Ngày có hiệu lực": _http.iso_date(doc.get("effFrom")),
            "Ngày hết hiệu lực": _http.iso_date(doc.get("effTo")), "Tình trạng hiệu lực": val("effStatus"),
            "Văn bản hợp nhất": "có" if doc.get("isConsolidatedDocument") else "không"}
    d = {"id": _clean(id), "title": _clean(doc["title"]), "url": url,
         "meta": {k: v for k, v in meta.items() if v}, "pars": pars}
    return _http.lru_put(_texts, key, d, 8)


async def _doc(id: str) -> dict:
    """vbpl.vn ids (slug from search, URL, or UUID) vs vanban.chinhphu.vn numeric docids."""
    i = _clean(id)
    m = _VB_ID.fullmatch(i)
    if m and (m[1] or "vbpl.vn" in i or "-" in m[2]):
        return await _vb_doc(i)
    if re.search(r"docid=\d+", i) or re.fullmatch(r"\d{1,8}", i):
        return await _vc_doc(i)
    raise BadRequest(f"Bad id {i!r}: use an id from search_legislation (a vbpl.vn slug such as "
                     f"'bo-luat-dan-su-so-91-2015-qh13--95942', or a vanban.chinhphu.vn numeric "
                     f"docid such as '183188'), or a vbpl.vn / ?docid= URL.")


# --------------------------------------------------------------------------- #
# Case law: precedents (anle.toaan.gov.vn)
# --------------------------------------------------------------------------- #
async def _al_get(url: str, what: str, **kw):
    r = await _http.get(url, **kw)
    if r.status_code != 200:
        raise SourceError(_http.error("anle.toaan.gov.vn", what, r.status_code), r.status_code)
    return r


async def _al_page(url: str, what: str) -> str:
    """An HTML page with entities decoded (the site writes Vietnamese as &#7893; etc.)."""
    return _html.unescape((await _al_get(url, what)).text)


def _al_rows(h: str) -> list[dict]:
    out = []
    for chunk in re.split(r"<tr><td><a href='[^']*chitietanle\?dDocName=", h)[1:]:
        m = re.match(r"(TAND\d+)'>([^<]+)</a>.*?<span class=\"[^\"]*\">(.*?)</span>", chunk, re.S)
        if not m:
            continue
        cells = dict((_strip(k), _strip(v)) for k, v in re.findall(r"<td[^>]*>(.*?)</td>\s*<td[^>]*>(.*?)</td>", chunk, re.S))
        out.append({"id": m[1], "number": _clean(m[2]), "name": _strip(m[3]),
                    "date": _http.iso_date(cells.get("Ngày thông qua", "")),
                    "field": cells.get("Lĩnh vực", ""), "status": cells.get("Trạng thái", ""),
                    "applies": cells.get("Ngày áp dụng", "")})
    return out


async def _al_list() -> list[dict]:
    """All published precedents, newest first (9-10 list pages, cached in memory)."""
    hit = _al_index.get("rows")
    if hit and _time.monotonic() - hit[0] < _AL_TTL:
        return hit[1]
    h = await _al_page(AL_LIST.format(p=1), "precedent list failed")
    m = re.search(r"Tổng số Án lệ đã công bố:\s*<span[^>]*>(\d+)</span>", h)
    if not m:
        raise SourceError("anle.toaan.gov.vn: precedent list not found (layout changed?)")
    rows = _al_rows(h)
    for p in range(2, -(-int(m[1]) // max(1, len(rows))) + 1):
        rows += _al_rows(await _al_page(AL_LIST.format(p=p), "precedent list failed"))
    _al_index["rows"] = (_time.monotonic(), rows)
    return rows


_AL_NUM = re.compile(r"^(?:an le\s*)?(?:so\s*)?(\d{1,3})(?:/(\d{4})(?:/al)?)?$")


def _al_title(number: str, name: str) -> str:
    return f"Án lệ số {number}: {name}" if name else f"Án lệ số {number}"


def _al_hit(r: dict) -> DecisionHit:
    snip = " · ".join(x for x in (r["field"], r["status"],
                                   f"áp dụng từ {r['applies']}" if r["applies"] else "") if x)
    return DecisionHit(id=r["id"], title=_al_title(r["number"], r["name"]), court=AL_COURT,
                       date=r["date"], case_number=r["number"], snippet=snip,
                       url=AL_DETAIL.format(id=r["id"]))


class Vietnam(Jurisdiction):
    code = "vn"
    name = "Vietnam"
    languages = ("vi",)
    aliases = ("viet nam", "việt nam")
    sources = (
        Source(
            name="Bộ Tư pháp: Cơ sở dữ liệu quốc gia về văn bản pháp luật (vbpl.vn)",
            url=VB,
            covers=("legislation",),
            licence="no licence or terms published (checked 2026-11-10); official Ministry of "
                    "Justice database",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~30 requests (2026-11)",
            terms_url=VB + "/",
        ),
        Source(
            name="Cổng Thông tin điện tử Chính phủ: Hệ thống văn bản (vanban.chinhphu.vn)",
            url=VC,
            covers=("legislation",),
            licence="© Cục Thông tin và Truyền thông Chính phủ; republication allowed with the "
                    "source named (site footer)",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~15 requests (2026-11)",
            terms_url=VC + "/",
            warning="Attribution required: name 'Cục Thông tin và Truyền thông Chính phủ' or "
                    "'www.chinhphu.vn' when republishing. Texts are as issued, not consolidated.",
        ),
        Source(
            name="Tòa án nhân dân tối cao: Trang tin điện tử về án lệ (anle.toaan.gov.vn)",
            url=AL,
            covers=("caselaw",),
            licence="© Tòa án nhân dân tối cao; republication allowed with the source named "
                    "(site footer)",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~40 requests (2026-11)",
            terms_url=AL + "/webcenter/portal/anle/home",
            warning="Attribution required: name 'Trang tin điện tử về án lệ (anle.toaan.gov.vn)' "
                    "when republishing.",
        ),
    )
    legislation_filters = {
        "year": "year in the document number, e.g. 2024",
        "type": "vbpl.vn document type as in the slug: hien-phap, bo-luat, luat, phap-lenh, "
                "nghi-quyet, van-ban-hop-nhat, nghi-dinh, ...",
        "source": "'chinhphu' searches vanban.chinhphu.vn (PDF texts as issued) instead of vbpl.vn",
    }
    caselaw_filters = {
        "year": "year the precedent was adopted, e.g. '2022', a range '2020-2024', or '2022-' "
                "for 2022 onward",
    }
    min_interval = {"vbpl.vn": 1.0, "vanban.chinhphu.vn": 1.0, "datafiles.chinhphu.vn": 1.0,
                    "anle.toaan.gov.vn": 1.0}
    notes = ("Legislation: the Ministry of Justice database vbpl.vn (all constitutions, codes, "
             "laws, ordinances, resolutions and lower central texts, HTML as issued; consolidated "
             "texts are separate documents), searched by URL slug; filter source=chinhphu for the "
             "Government Portal PDFs. "
             "Case law: only the Supreme People's Court precedents (án lệ, ~90), searched by "
             "number, title and field; the 2026 ones are scans and can't be read. Published "
             "judgments (congbobanan.toaan.gov.vn) are unreachable. Vietnamese only.")
    gaps = (
        ("Full-text / accented search on vbpl.vn: the site's search runs through /api/, which "
         "robots.txt disallows, so search matches the sitemap URL slugs (words of the title "
         "without diacritics, plus the number)"),
        ("Consolidated constitution: vbpl.vn has the 2013 Constitution as issued and the 2025 "
         "amending resolution 203/2025/QH15 separately, no consolidated text"),
        ("Possibly missing laws: gaps in the vbpl.vn law-number sequences (checked 2026-11-10): "
         "QH12 no. 4, QH13 nos. 25 and 34, QH15 no. 115, QH16 nos. 13, 14, 17, 19-21 (not "
         "verified that these numbers are laws); completeness before 2002 not verified; "
         "documents published only as a file have no text"),
        ("Published court judgments (congbobanan.toaan.gov.vn): connection reset / timed out from "
         "the UK (2026-11-06)"),
        "Codification (phapdien.moj.gov.vn): timed out from the UK",
        ("vanban.chinhphu.vn scanned PDFs (e.g. its copy of the 2015 Civil Code; vbpl.vn has the "
         "text) and the 2026 precedents 83-90: scans only, no text"),
    )
    samples = {
        "caselaw_query": "quyền sử dụng đất",
        "decision_id": "TAND332760",
        "legislation_query": "Luật Đất đai",
        "law_id": "luat-dat-dai-so-31-2024-qh15--177815",
        "provision": "Điều 3",
    }

    # -------------------------------------------------------------- legislation
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        q = _clean(query)
        if not q:
            raise BadRequest("Give a keyword, e.g. 'Luật Đất đai' or '31/2024/QH15'.")
        if len(q) > 100:
            raise BadRequest("The source accepts at most 100 characters.")
        year = str(filters.get("year", "")).strip()
        if year and not re.fullmatch(r"\d{4}", year):
            raise BadRequest(f"year must look like 2024, got {year!r}")
        src = _fold(str(filters.get("source", "")))
        if src not in ("", "vbpl", "chinhphu"):
            raise BadRequest(f"source must be 'vbpl' (default) or 'chinhphu', got {src!r}")
        if src != "chinhphu":
            return await self._vb_search(q, year, _fold(str(filters.get("type", ""))), limit, page)
        start = (max(1, page) - 1) * limit
        first, last = start // _PAGE + 1, (start + limit - 1) // _PAGE + 1
        if last > 10:
            raise BadRequest("The source returns at most 500 results per search; narrow the query.")
        r = await _http.get(VC_LIST)
        if r.status_code != 200:
            raise SourceError(_http.error("vanban.chinhphu.vn", "list page failed", r.status_code), r.status_code)
        form = _hidden_fields(r.text)
        if "__VIEWSTATE" not in form:
            raise SourceError("vanban.chinhphu.vn: search form not found (layout changed?)")
        fields = {_FORM + "txtSearchKeyword": q, _FORM + "drdDocCategory": "0",
                  _FORM + "drdDocOrg": "0", _FORM + "drdDocYear": year or "0",
                  _FORM + "drdRecordPerPage": "500"}  # caps the hit set (shown 50 a page)
        h = await _vc_post({**form, **fields, _FORM + "btnSearch": "Tìm kiếm"})
        m = re.search(r"\d+\s*-\s*\d+\s*\|\s*(\d+)", _strip(h))
        rows = _parse_vc_rows(h)
        total = int(m[1]) if m else len(rows)
        got = {1: rows}
        for sp in range(max(2, first), last + 1):
            if (sp - 1) * _PAGE >= total:
                break
            # GridView paging is a postback carrying the results page's own view state
            h = await _vc_post({**_hidden_fields(h), **fields, "__EVENTTARGET": _FORM + "grvDocument",
                                "__EVENTARGUMENT": f"Page${sp}"})
            got[sp] = _parse_vc_rows(h)
        rows = [x for sp in range(first, last + 1) for x in got.get(sp, [])]
        off = start - (first - 1) * _PAGE
        note = "Texts as issued (PDF), not consolidated; older scanned PDFs cannot be read."
        if total >= 500:
            note += " The source stops at 500 hits; narrow the query."
        return Results(items=rows[off:off + limit], total=total, note=note)

    async def _vb_search(self, q, year, typ, limit, page):
        words = re.sub(r"[^a-z0-9]+", " ", _fold(q)).split()
        typ = re.sub(r"[^a-z0-9]+", "-", typ).strip("-")
        if not words:
            raise BadRequest("Give a keyword, e.g. 'Luật Đất đai' or '31/2024/QH15'.")
        lead = "-".join(words) + "-"
        rows = []
        for n, slug in enumerate(await _vb_slugs()):
            name = slug.split("--")[0]
            toks = set(name.split("-"))
            if not all(w in toks or w.lstrip("0") in toks for w in words):
                continue
            if typ and not name.startswith(typ + "-"):
                continue
            number, y, _ = _vb_number(name)
            if year and y != year:
                continue
            tier = next((r for t, r in _VB_TIER if name.startswith(t)), 9)
            rows.append((not (name + "-").startswith(lead), tier, -int(y or 0), n, slug))
        rows.sort()
        start = (max(1, page) - 1) * limit
        note = ("vbpl.vn (Ministry of Justice): central documents matched on their URL slug, "
                "constitution/codes/laws first; titles in hits are unaccented. Texts are as "
                "issued; consolidated versions are separate 'van-ban-hop-nhat' documents. "
                "filters={'source': 'chinhphu'} searches vanban.chinhphu.vn instead.")
        hits = [_vb_hit(r[-1]) for r in rows[start:start + limit]]
        for h in hits:
            if h.number == "Không số":  # slug has no number: read the issue date and status from the page
                try:
                    m = (await _vb_doc(h.id))["meta"]
                except Exception:
                    continue
                h.date = m.get("Ngày ban hành", "")
                h.title = _clean(h.title.split(" (vbpl.vn")[0] + (f" (no number on vbpl.vn; {m['Tình trạng hiệu lực']})"
                                                                if m.get("Tình trạng hiệu lực") else " (no number on vbpl.vn)"))
        return Results(items=hits, total=len(rows), note=note)

    async def get_legislation_text(self, id):
        d = await _doc(id)
        meta = dict(d["meta"])
        if d.get("pdf"):
            meta["PDF"] = d["pdf"]
        if meta.get("Văn bản hợp nhất") != "có":
            meta["Ghi chú"] = "Văn bản gốc như được ban hành, không phải văn bản hợp nhất."
        return LawText(id=d["id"], title=d["title"], text="\n\n".join(d["pars"]), url=d["url"],
                       as_of="", metadata=meta)

    async def get_legislation_toc(self, id):
        d = await _doc(id)
        pars, entries = d["pars"], []
        arts = {i: lab for lab, i, _ in _segments(pars)}
        level = 0
        for i, p in enumerate(pars):
            if i in arts:
                entries.append(TocEntry(title=p[:160], level=level, provision=arts[i]))
            elif _TOC_HEAD.match(p):
                lvl = 0 if p.lower().startswith(("phần", "chương")) else 1
                nxt = pars[i + 1] if i + 1 < len(pars) and _is_heading_line(pars[i + 1]) else ""
                entries.append(TocEntry(title=_clean(f"{p} {nxt}")[:160], level=lvl))
                level = lvl + 1
        if not any(e.provision for e in entries):
            raise SourceError(f"No 'Điều N.' articles found in document {d['id']}; "
                              f"use get_legislation_text.", "no-articles")
        return Toc(id=d["id"], title=d["title"], url=d["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        label = _norm_label(provision)
        d = await _doc(id)
        for lab, i, end in _segments(d["pars"]):
            if lab == label:
                return Provision(law_id=d["id"], law_title=d["title"], provision=label,
                                 text="\n\n".join(d["pars"][i:end]), url=d["url"], as_of="")
        raise NotFound(f"{label} not found in {d['title']}.")

    # ----------------------------------------------------------------- case law
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        q = _fold(query).strip(" .\"“”")
        rows = await _al_list()
        m = _AL_NUM.match(q)
        # Words match whole; with diacritics typed they must match exactly ("hình sự" is not
        # "sử dụng"), without any they match either way.
        plain = q == _clean(unicodedata.normalize("NFC", query).lower()).strip(" .\"“”")
        norm = _fold if plain else (lambda x: unicodedata.normalize("NFC", x).lower())
        if m:  # a precedent number: '47', '47/2021/AL', 'án lệ số 47'
            hits = [r for r in rows if int(r["number"].split("/")[0]) == int(m[1])
                    and (not m[2] or f"/{m[2]}/" in r["number"])]
        else:
            words = [re.compile(rf"(?<!\w){re.escape(w)}(?!\w)")
                     for w in (x.strip(".,\"“”") for x in norm(query).split()) if w]
            hits = [r for r in rows
                    if all(w.search(norm(f"{r['number']} {r['name']} {r['field']}")) for w in words)]
        y = str((filters or {}).get("year", "")).strip()
        if y:
            ym = re.fullmatch(r"(\d{4})(?:\s*-\s*(\d{4})?)?", y)
            if not ym:
                raise BadRequest(f"year must look like 2022, 2020-2024 or 2022-, got {y!r}")
            lo = int(ym[1])
            hi = int(ym[2]) if ym[2] else (lo if "-" not in y else 9999)
            hits = [r for r in hits if r["date"][:4].isdigit() and lo <= int(r["date"][:4]) <= hi]
        start = (max(1, page) - 1) * limit
        return Results(items=[_al_hit(r) for r in hits[start:start + limit]], total=len(hits),
                       note="Only the Supreme People's Court precedents (án lệ) are searchable "
                            "here, not ordinary judgments; search by number, title and field, "
                            "newest first; narrow by date with filters={'year': '2022-'}. The "
                            "2026 ones are scanned and cannot be opened here.")

    async def get_decision(self, id):
        raw = _clean(id)
        m = re.search(r"TAND\d+", raw, re.I)
        if m:
            did = m[0].upper()
        else:
            n = _AL_NUM.match(_fold(raw))
            if not n or not n[2]:
                raise BadRequest(f"Bad id {id!r}: use the id from search_caselaw (e.g. "
                                 f"'TAND332760') or a precedent number such as '72/2024/AL'.")
            did = next((r["id"] for r in await _al_list()
                        if r["number"].lower() == f"{int(n[1]):02d}/{n[2]}/al"), "")
            if not did:
                raise NotFound(f"No precedent {raw} on anle.toaan.gov.vn.")
        url = AL_DETAIL.format(id=did)
        h = await _al_page(url, "precedent page failed")
        meta = {}
        tab = h[h.find('id="thuoctinh"'):h.find('id="vblienquan"')]
        for k, v in re.findall(r"<th[^>]*>(.*?)</th>\s*<td[^>]*>(.*?)</td>", tab, re.S):
            if _strip(v):
                meta[_strip(k)] = _strip(v)
        number = meta.pop("Số án lệ", "")
        if not number:
            raise NotFound(f"No precedent with id {did} on anle.toaan.gov.vn.")
        name = meta.pop("Tên án lệ", "")
        date = _http.iso_date(meta.get("Ngày thông qua", ""))
        body = re.search(r"<div\s+id='divPrint'>(.*?)<div id=\"fb-root\">", h, re.S)
        body = body[1] if body else ""
        if "pdfview?dDocName=" in body:
            try:
                r = await _al_get(AL_FILE.format(id=did), "precedent PDF failed", max_bytes=_AL_MAX_PDF)
            except SourceError as e:
                if e.status != 413:
                    raise
                r = None
            text = _http.pdf_text(r.content) if r is not None and r.content[:5] == b"%PDF-" else ""
            if len(text) < 200:
                raise SourceError(f"Precedent {number} is published only as a scanned PDF "
                                  f"(no text layer; no OCR here). Open it at {url}", "no-text")
            text = "\n\n".join(_reflow(text))
        else:
            text = _http.html_to_md(body)
            if len(text) < 200:
                raise SourceError(f"anle.toaan.gov.vn: no text found for precedent {number}. "
                                  f"Open it at {url}", "no-text")
        return Decision(id=did, title=_al_title(number, name), text=text, url=url, court=AL_COURT,
                        date=date, case_number=number, metadata=meta)
