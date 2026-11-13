"""Turkey: case law and legislation from the Ministry of Justice "Bedesten" backend
(the API behind mevzuat.adalet.gov.tr), plus the Constitutional Court (AYM) decision banks.

Gotchas this code encodes (verified 2026-11-05 from a UK IP):
  * Bedesten wants `AdaletApplicationName: UyapMevzuat` and a body
    {"data": {...}, "applicationName": "UyapMevzuat", "paging": true}. Errors come back
    as HTTP 200 with metadata.FMTY == "ERROR" (FEC ...RecordNotFoundException = not found).
  * Search syntax: unquoted words are OR-ed ("kira tespiti" -> 2.3M hits incl. criminal
    chambers; "\"kira tespiti\"" -> ~2.1k). Quotes, +required, -exclude, AND/OR/NOT work.
  * kararTarihi is UTC (21:00 the day before, 22:00 before 2016); the Turkish date is
    kararTarihiStr (dd.mm.yyyy), sometimes null. Date filters are shifted to match.
  * Without sortFields the order is neither relevance nor date; we default to newest first.
  * Legislation title search is `mevzuatAdi`; `phrase` is full text (basliktaAra is ignored).
  * mevzuatMaddeTree lists only the numbered articles. Ek / geçici / mükerrer articles are
    folded into the content of a neighbouring article, so they are found by slicing the
    full text (documentType MEVZUAT, one request, cached in-process).
  * Per-article content often ends with the *next* article's heading (headings precede
    articles in Turkish codes and the source splits after the heading).
  * mevzuatMaddeTree can keep stale copies of whole parts next to the current ones (Law 1136:
    a 2024 and a 2026 "Madde 12", the old one with another article's footnotes). The copy
    with the latest guncellemeTarihi is the current one; the others are dropped.
  * searchDocuments often has resmiGazeteTarihi null (16 of 20 KANUN hits, 2026-11); the
    date is in the full-text header ("Yayımlandığı Resmî Gazete : Tarih: 7/4/1969").
  * AYM (kararlarbilgibankasi / normkararlarbilgibankasi): JSON search; full text in
    data[0].icerik when you pass the uuid. Some queries hang server-side, so a short timeout.
  * Uyuşmazlık Mahkemesi: ASP.NET WebForms; search and paging are __doPostBack form posts
    (20 rows a page, no hit count); decisions are text-layer PDFs under /Uploads/. A full-text
    search takes ~20 s; a request sometimes hangs to the timeout, so one retry.
  * Sayıştay: jQuery DataTables endpoints (/Kararlar*/DataTablesList) need the anti-forgery
    token + cookie from the form page and the full columns[i][...] set (else HTTP 500).
    Date selects are years. Detail pages: label/value rows + div#metin.
  * Rekabet: GET /tr/Kararlar?PdfText=&page= (10 a page, "Toplam : N"); /Karar?kararId= is the PDF.
  * GİB özelge: JSON POST /api/gibportal/mevzuat/ozelge/list (status 2, ktype 99); the
    same body with "id" returns one ruling with its HTML text.
"""
from __future__ import annotations

import asyncio
import base64
import datetime
import re
from urllib.parse import urlencode

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

BEDESTEN = "https://bedesten.adalet.gov.tr"
ICTIHAT_URL = "https://mevzuat.adalet.gov.tr/ictihat/"
MEVZUAT_URL = "https://www.mevzuat.gov.tr/mevzuat?MevzuatNo={no}&MevzuatTur={tur}&MevzuatTertip={tertip}"
_HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "AdaletApplicationName": "UyapMevzuat",
    "Origin": "https://mevzuat.adalet.gov.tr",
    "Referer": "https://mevzuat.adalet.gov.tr/",
    "Accept-Language": "tr-TR,tr;q=0.9",
}

# court filter value -> Bedesten itemType, or AYM decision bank
_BEDESTEN_COURTS = {
    "yargitay": "YARGITAYKARARI",
    "danistay": "DANISTAYKARAR",
    "yerel_hukuk": "YERELHUKUK",
    "istinaf_hukuk": "ISTINAFHUKUK",
    "kyb": "KYB",
}
_COURT_NAMES = {"YARGITAYKARARI": "Yargıtay", "DANISTAYKARAR": "Danıştay",
                "YERELHUKUK": "Yerel Hukuk Mahkemesi", "ISTINAFHUKUK": "Bölge Adliye Mahkemesi",
                "KYB": "Kanun Yararına Bozma"}
# AYM: our id prefix -> (host, kararTipi)
_AYM = {
    "bb": ("kararlarbilgibankasi.anayasa.gov.tr", "BireyselBasvuru"),
    "norm": ("normkararlarbilgibankasi.anayasa.gov.tr", "NormDenetimi"),
}
_AYM_COURTS = {"aym_bb": "bb", "aym_norm": "norm", "aym": "bb"}  # plain "aym": individual applications
_UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
_AYM_ID = re.compile(rf"^aym:(bb|norm):({_UUID})$", re.I)

# Other official decision banks, one court filter value each (searched alone, like AYM)
UYUSMAZLIK = "https://kararlar.uyusmazlik.gov.tr/"
SAYISTAY = "https://www.sayistay.gov.tr"
REKABET = "https://www.rekabet.gov.tr"
GIB_LIST = "https://gib.gov.tr/api/gibportal/mevzuat/ozelge/list"
# Sayıştay kind -> (page path, form prefix, text field, chamber field, DataTables columns, date column)
_SAYISTAY = {
    "genel_kurul": ("KararlarGenelKurul", "KararlarGenelKurulAra", "KARARTAMAMI", "",
                    ("KARARNO", "KARARNO", "KARARTARIH", "KARAROZETI", ""), 2, "Genel Kurul"),
    "temyiz": ("KararlarTemyiz", "KararlarTemyizAra", "TEMYIZKARAR", "ILAMDAIRESI",
               ("TEMYIZTUTANAKTARIHI", "TEMYIZTUTANAKTARIHI", "ILAMDAIRESI", "TEMYIZKARAR", ""), 1,
               "Temyiz Kurulu"),
    "daire": ("KararlarDaire", "KararlarDaireAra", "WEBKARARMETNI", "YARGILAMADAIRESI",
              ("YARGILAMADAIRESI", "KARARTRH", "KARARNO", "YARGILAMADAIRESI", "WEBKARARMETNI", ""), 1,
              "Daire"),
}
_OTHER_COURTS = {"uyusmazlik": "uyusmazlik", "sayistay_gk": "genel_kurul",
                 "sayistay_temyiz": "temyiz", "sayistay_daire": "daire", "rekabet": "rekabet",
                 "gib_ozelge": "gib"}
_OTHER_ID = re.compile(rf"^(?:uyusmazlik:(?P<uy>\d{{4}}-\d+[\w-]*)|sayistay:(?P<sk>genel_kurul|temyiz|daire):"
                       rf"(?P<sid>\d+)|rekabet:(?P<rk>{_UUID})|gib:(?P<gib>\d+))$", re.I)

# mevzuat.gov.tr MevzuatTur id -> Bedesten type name (from /mevzuat/mevzuatTypes, 2026-11)
_TUR = {1: "KANUN", 19: "CB_KARARNAME", 3: "YONETMELIK", 21: "CB_YONETMELIK", 20: "CB_KARAR",
        22: "CB_GENELGE", 4: "KHK", 2: "TUZUK", 7: "KKY", 8: "UY", 9: "TEBLIGLER", 5: "MULGA"}
_TUR_ID = {v: k for k, v in _TUR.items()}
# common code abbreviations -> law number (all KANUN)
_ABBR = {"tbk": "6098", "tmk": "4721", "tck": "5237", "cmk": "5271", "hmk": "6100", "iik": "2004",
         "ttk": "6102", "iyuk": "2577", "anayasa": "2709", "kvkk": "6698"}
_TRIPLE = re.compile(r"^(\d{1,2})\.(\d)\.(\d+)$")

_SORTS = {"newest": "desc", "oldest": "asc", "source": None}
_FOLD = str.maketrans("çğıöşüâîû", "cgiosuaiu")


# --------------------------------------------------------------------------- #
# Helpers (HTML, dates and the cache come from _http)
# --------------------------------------------------------------------------- #
def _fold(s: str) -> str:
    """Turkish-aware lower-case ASCII fold, 1:1 in length ('GEÇİCİ' -> 'gecici')."""
    return (s or "").replace("İ", "i").replace("I", "ı").lower().translate(_FOLD)


_clean = _http.clean
_paragraphs = _http.html_paragraphs
_html_to_md = _http.html_to_md


def _tr_title(s: str) -> str:
    """'NEJLA DEMİRCİ' -> 'Nejla Demirci' (str.title() mangles the dotted İ)."""
    low = s.replace("İ", "i").replace("I", "ı").lower()
    return " ".join(w[:1].replace("i", "İ").replace("ı", "I").upper() + w[1:] for w in low.split())


_lru = _http.lru_put
_iso_from_tr = _http.iso_date


def _iso_from_utc(s: str) -> str:
    """'2010-01-27T22:00:00.000+00:00' -> Turkish calendar date '2010-01-28'."""
    try:
        dt = datetime.datetime.fromisoformat((s or "").replace("Z", "+00:00"))
    except ValueError:
        return ""
    return (dt + datetime.timedelta(hours=3)).date().isoformat()


def _decision_date_label(pars: list[str]) -> str:
    """BAM/first-instance headers carry 'KARAR TARİHİ : 05/11/2026' (the bare 'TARİHİ' line is the
    lower court's date); ISO date or ''."""
    m = re.search(r"KARAR\s+TAR[İI]H[İI]\s*:\s*(\d{1,2})[./](\d{1,2})[./](\d{4})", " ".join(pars[:40]))
    return f"{m[3]}-{int(m[2]):02d}-{int(m[1]):02d}" if m else ""


def _parse_date(v: str, name: str) -> datetime.date:
    v = (v or "").strip()
    iso = _iso_from_tr(v) or v
    try:
        return datetime.date.fromisoformat(iso)
    except ValueError:
        raise BadRequest(f"{name} must be a date like 2024-01-31 (or 31.01.2024), got {v!r}")


def _bool(v) -> bool:
    return str(v).strip().lower() in ("1", "true", "yes", "evet", "on")


async def _bpost(path: str, data: dict, *, paging: bool = False) -> dict:
    body = {"data": data, "applicationName": "UyapMevzuat"}
    if paging:
        body["paging"] = True
    r = await _http.post(BEDESTEN + path, json=body, headers=_HEADERS)
    if r.status_code != 200:
        raise SourceError(_http.error("Bedesten", f"{path} failed", r.status_code,
                                      "The source allows ~10 requests / 30 s; try again shortly."
                                      if r.status_code == 429 else ""), r.status_code)
    try:
        j = r.json()
    except ValueError:
        raise SourceError(f"Bedesten {path}: non-JSON reply (block page?)", r.status_code)
    meta = j.get("metadata") or {}
    if meta.get("FMTY") == "ERROR":
        msg = meta.get("FMU") or meta.get("FMTE") or "error"
        code = f"{meta.get('FMC', '')} {meta.get('FEC', '')}"
        if re.search(r"NOT_FOUND|NotFound|MEVZUAT_ERROR_0005", code):
            raise NotFound(msg)
        if "PARAMETER_VALIDATION" in code:
            raise BadRequest("query rejected by the source: it needs at least 3 letters/digits and "
                             "no special characters (quotes around a phrase are fine)")
        raise SourceError(f"Bedesten {path}: {msg}", meta.get("FMC", ""))
    return j.get("data") or {}


def _decode(d: dict, url: str) -> str:
    if "pdf" in str(d.get("mimeType", "")).lower():
        raise SourceError(f"This text is published only as PDF, which this server does not "
                          f"convert. Open it at {url}", "pdf")
    raw = base64.b64decode(d.get("content") or "")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp1254", "replace")


# --------------------------------------------------------------------------- #
# Article labels
# --------------------------------------------------------------------------- #
_KINDS = {"": "Madde", "ek": "Ek Madde", "gecici": "Geçici Madde", "ek gecici": "Ek Geçici Madde",
          "mukerrer": "Mükerrer Madde"}
# start of an article paragraph, on folded text with leading markdown stripped
_ART_START = re.compile(r"^(ek gecici |gecici |ek |mukerrer )?madde\s+(\d+)(?:\s*/\s*([a-z]))?[\s*]*[-–—:]")
_LABEL_IN = re.compile(
    r"^(?:(?P<ek>ek)\s*)?(?:(?P<gec>gec(?:ici)?)\.?\s*)?(?:(?P<muk>muk(?:errer)?)\.?\s*)?"
    r"(?:madde|mad\.?|md\.?|m\.?|art(?:icle|\.)?)?\s*(?P<num>\d+)(?:\s*/\s*(?P<suf>[a-z]))?\.?$")
DIGER = "Diğer Bilgiler"


def _label(kind: str, num: str, suf: str = "") -> str:
    return f"{_KINDS[kind]} {num}" + (f"/{suf.upper()}" if suf else "")


def _norm_label(s: str) -> str:
    """'m. 5', '5', 'madde 5', 'geç. m. 1', 'Ek Madde 1', 'Madde 5/a' -> canonical label."""
    f = _clean(_fold(s)).rstrip(" -–—:")
    if f in ("diger bilgiler", "diger"):
        return DIGER
    m = _LABEL_IN.match(f)
    if not m:
        raise BadRequest(f"Provision {s!r} not understood. Use e.g. 'Madde 5', '5', 'm. 5', "
                         f"'Madde 5/A', 'Geçici Madde 1', 'Ek Madde 1' or '{DIGER}'.")
    kind = " ".join(k for k, g in (("ek", "ek"), ("gecici", "gec"), ("mukerrer", "muk")) if m[g])
    if kind not in _KINDS:
        raise BadRequest(f"Provision {s!r} not understood.")
    return _label(kind, str(int(m["num"])), m["suf"] or "")


def _art_start(par: str) -> str:
    """Canonical label if this paragraph starts an article, else ''."""
    m = _ART_START.match(_fold(par.lstrip("*_# ")))
    return _label((m[1] or "").strip(), str(int(m[2])), m[3] or "") if m else ""


_END_OF_LAW = re.compile(r"sayili .*(islenemeyen hukumler|ek ve degisiklik getiren)")


def _segments(pars: list[str]) -> dict[str, tuple[int, int]]:
    """label -> (start, end) paragraph span for every article in a full law text.
    Stops at the appendix ('... SAYILI KANUNA İŞLENEMEYEN HÜKÜMLER', amendment table)."""
    starts: list[tuple[str, int]] = []
    end = len(pars)
    for i, p in enumerate(pars):
        if _END_OF_LAW.search(_fold(p)):
            end = i
            break
        lab = _art_start(p)
        if lab:
            starts.append((lab, i))
    out: dict[str, tuple[int, int]] = {}
    for n, (lab, i) in enumerate(starts):
        nxt = starts[n + 1][1] if n + 1 < len(starts) else end
        out.setdefault(lab, (i, nxt))
    return out


# --------------------------------------------------------------------------- #
# Legislation: id resolution, tree, full text
# --------------------------------------------------------------------------- #
class _Law:
    __slots__ = ("mid", "tur", "tertip", "no", "title", "url")

    def __init__(self, hit: dict):
        self.mid = str(hit["mevzuatId"])
        self.tur = int((hit.get("mevzuatTur") or {}).get("id") or 0)
        self.tertip = int(hit.get("mevzuatTertip") or 5)
        self.no = str(hit.get("mevzuatNo") or "")
        self.title = _clean(hit.get("mevzuatAdi"))
        self.url = hit.get("url") or MEVZUAT_URL.format(no=self.no, tur=self.tur, tertip=self.tertip)

    @property
    def id(self) -> str:
        return f"{self.tur}.{self.tertip}.{self.no}"


_laws: dict[str, _Law] = {}
_trees: dict[str, dict] = {}
_fulltexts: dict[str, list[str]] = {}


async def _find(no: str, types: list[str] | None) -> list[dict]:
    data = {"pageSize": 10, "pageNumber": 1, "mevzuatNo": no}
    if types:
        data["mevzuatTurList"] = types
    return (await _bpost("/mevzuat/searchDocuments", data, paging=True)).get("mevzuatList") or []


async def _resolve(law_id: str) -> _Law:
    key = _clean(law_id)
    if key in _laws:
        return _laws[key]
    f = _fold(key).replace(" ", "")
    hits: list[dict] = []
    if m := _TRIPLE.match(key):
        tur, tertip, no = int(m[1]), int(m[2]), m[3]
        if tur not in _TUR:
            raise BadRequest(f"Unknown MevzuatTur {tur} in {law_id!r}. Known: "
                             + ", ".join(f"{k}={v}" for k, v in _TUR.items()))
        hits = [h for h in await _find(no, [_TUR[tur]]) if int(h.get("mevzuatTertip") or 0) == tertip]
    elif f in _ABBR:
        hits = await _find(_ABBR[f], ["KANUN"])
    elif m := re.match(r"^([a-z_]+)[/:\-]?(\d+)$", f):
        t = m[1].upper()
        if t not in _TUR_ID:
            raise BadRequest(f"Unknown legislation type {m[1]!r}. Use one of {', '.join(_TUR_ID)}.")
        hits = await _find(m[2], [t])
    elif key.isdigit():
        hits = await _find(key, ["KANUN"])
        if not hits:  # maybe a Bedesten mevzuatId
            root = await _tree(key)
            no = str(root.get("title") or "")
            hits = [h for h in (await _find(no, None) if no.isdigit() else [])
                    if str(h["mevzuatId"]) == key]
    else:
        raise BadRequest(f"Bad law id {law_id!r}. Use the id from search_legislation "
                         "('1.5.6098' = MevzuatTur.Tertip.No), a law number ('6098'), "
                         "'KANUN 6098', 'KHK 375', or an abbreviation (TBK, TMK, TCK, HMK, ...).")
    if not hits:
        raise NotFound(f"No legislation found for {law_id!r}.")
    hits.sort(key=lambda h: int(h.get("mevzuatTertip") or 0) != 5)  # prefer the current series
    law = _Law(hits[0])
    _lru(_laws, law.id, law, 200)
    return _lru(_laws, key, law, 200)


async def _tree(mid: str) -> dict:
    if mid not in _trees:
        _lru(_trees, mid, await _bpost("/mevzuat/mevzuatMaddeTree", {"mevzuatId": mid}), 8)
    return _trees[mid]


async def _tree_or_empty(mid: str) -> dict:
    try:
        return await _tree(mid)
    except NotFound:  # some texts (e.g. many Cumhurbaşkanı Kararları) have no article tree
        return {}


async def _fulltext(law: _Law) -> list[str]:
    if law.mid not in _fulltexts:
        d = await _bpost("/mevzuat/getDocumentContent",
                         {"documentType": "MEVZUAT", "id": law.mid})
        _lru(_fulltexts, law.mid, _paragraphs(_decode(d, law.url)), 4)
    return _fulltexts[law.mid]


def _art_label(n: dict) -> str:
    m = re.match(r"Madde No:\s*(\d+)(?:\s*/\s*([A-Za-z]))?", n.get("maddeBaslik") or "")
    if m:
        return _label("", str(int(m[1])), m[2] or "")
    if not n.get("children") and _fold(n.get("maddeBaslik") or "") == "diger bilgiler":
        return DIGER
    return ""


def _current(tree: dict) -> dict:
    """The tree without stale copies: where a label occurs more than once, keep the node
    with the latest guncellemeTarihi and drop headings left with no articles; siblings
    that lost a stale copy are put back in article order."""
    best: dict[str, dict] = {}
    for n in _all(tree):
        lab = _art_label(n)
        if lab and (lab not in best or (n.get("guncellemeTarihi") or "") > (best[lab].get("guncellemeTarihi") or "")):
            best[lab] = n
    keep = {id(n) for n in best.values()}

    def first_no(n):
        nos = [int(x["maddeNo"]) for x in _all(n, True) if _art_label(x) and str(x.get("maddeNo") or "").isdigit()]
        return min(nos) if nos else float("inf")

    def rec(n):
        kids, pruned = [], False
        for ch in n.get("children") or []:
            if _art_label(ch):
                if id(ch) in keep:
                    kids.append(ch)
                else:
                    pruned = True
                continue
            had = any(_art_label(x) for x in _all(ch))
            sub = rec(ch)
            if had and not any(_art_label(x) for x in _all(sub)):
                pruned = True
                continue
            kids.append(sub)
        if pruned:
            kids.sort(key=first_no)
        return {**n, "children": kids}
    return rec(tree)


def _all(n: dict, self_too: bool = False):
    if self_too:
        yield n
    for ch in n.get("children") or []:
        yield ch
        yield from _all(ch)


def _as_of(tree: dict) -> str:
    """Last update of the consolidated text in the source (tree root), Turkish date."""
    return _iso_from_utc(tree.get("guncellemeTarihi") or "")


_RG_HEAD = re.compile(r"Resm[iî] Gazete\s*:\s*Tarih\s*:\s*([\d/.]+)\s*Sayı\s*:\s*(\d+)")


def _rg_date(pars: list[str]) -> str:
    """Resmî Gazete date (ISO) from a full text's header, or ''."""
    m = _RG_HEAD.search(" ".join(pars[:12]).replace("*", ""))
    return _iso_from_tr(m[1]) if m else ""


def _walk(tree: dict):
    """Yield (level, node, label) for every tree node; label '' for headings."""
    def rec(n, level):
        for ch in n.get("children") or []:
            yield level, ch, _art_label(ch)
            yield from rec(ch, level + 1)
    yield from rec(_current(tree), 0)


# --------------------------------------------------------------------------- #
# The adapter
# --------------------------------------------------------------------------- #
_hits: dict[str, DecisionHit] = {}   # documentId -> hit, so get_decision can show metadata

# Words found in nearly every decision: they never narrow a Bedesten search.
_GENERIC = {"dava", "davasi", "davasinda", "davasindan", "davalar", "karar", "karari", "kararlar",
            "mahkeme", "mahkemesi", "mahkemesinin"}
# The subject line of istinaf / first-instance / Danistay texts ("DAVA : Kira Bedelinin Tespiti")
_SUBJ_LINE = re.compile(r"^[\s*]*(?:DAVA(?:NIN)?\s*(?:KONUSU|TÜRÜ)?|İSTEMİN\s+KONUSU|TALEP(?:\s+KONUSU)?)"
                        r"\s*:\s*([^\n]{3,200})", re.M)
# Yargitay states it in the first sentence: "Taraflar arasındaki kira bedelinin tespiti davasından ..."
_SUBJ_SENT = re.compile(r"(?:Taraflar arasındaki|Uyuşmazlık,?)\s+(.{3,160}?)\s+davas[ıi]", re.S)
# Current Yargitay format: "I. DAVA Davaci vekili; ... ileri surerek; <relief> karar verilmesini talep etmistir."
_SUBJ_RELIEF = re.compile(r"\bI\.\s*DAVA\b(.{0,4000}?)(?:karar\s+verilmesini\s+)?(?:talep\s+etmiş|istemiş)(?:tir|lerdir)", re.S)
_SUBJ_MAX = 10                       # hits per page whose subject is read
_subjects: dict[str, str] = {}       # documentId -> subject ("" = none stated)


def _subject(text: str) -> str:
    """The decision's own statement of what the case is about, or ''."""
    t = re.sub(r"<[^>]+>", "\n", text)
    m = _SUBJ_LINE.search(t)
    if m and re.search(r"\w{3}", m[1]):
        return re.sub(r"\s+", " ", m[1]).strip(" :")
    flat = re.sub(r"\s+", " ", t)
    m = _SUBJ_SENT.search(flat[:6000])
    if m:
        return m[1].strip() + " davası"
    m = _SUBJ_RELIEF.search(flat[:8000])
    if not m or re.search(r"\bII\.\s*CEVAP\b", m[1]):
        return ""
    relief = re.split(r"(?:sürerek|belirterek|açıklayarak)\s*[;,]", m[1])[-1].strip(" ;,")
    return "Claim: " + (relief if len(relief) <= 200 else relief[:200].rsplit(" ", 1)[0] + "…")


def _stems(q: str) -> list[str]:
    """Folded word stems of the query (Turkish suffixes vary: 'tespiti' ~ 'tespit', 'tahliye' ~ 'tahliyesi')."""
    words = [w for w in re.findall(r"\w+", _fold(q)) if w not in _GENERIC and len(w) > 2
             and w not in ("and", "or", "not", "ve", "veya")]
    return [w[:max(4, len(w) - 2)] for w in words]


def _subject_match(subject: str, stems: list[str]) -> bool:
    words = re.findall(r"\w+", _fold(subject))
    return bool(stems) and all(any(w.startswith(st) for w in words) for st in stems)
_say_tokens: dict[str, str] = {}     # Sayıştay kind -> anti-forgery form token (cookie kept by _http)


class Turkey(Jurisdiction):
    code = "tr"
    name = "Türkiye"
    languages = ("tr",)
    aliases = ("tur", "turkey", "turkiye", "türkiye")
    sources = (
        Source("Bedesten (Adalet Bakanlığı, mevzuat.adalet.gov.tr backend)", "https://mevzuat.adalet.gov.tr",
               covers=("caselaw", "legislation"),
               licence="No published terms (undocumented public-site API). Court decisions and "
                       "legislation are excluded from copyright, FSEK (Law 5846) art. 31 (unverified "
                       "on an official terms page)",
               commercial_use=None, ai_use=None, auth="none",
               rate_limit="~10 req/30 s per IP, 429 + Retry-After (measured by yargi-mcp; "
                          "3.5 s spacing, no 429 seen in ~40 requests, 2026-11)",
               terms_url="https://mevzuat.adalet.gov.tr"),
        Source("Anayasa Mahkemesi Kararlar Bilgi Bankası", "https://kararlarbilgibankasi.anayasa.gov.tr",
               covers=("caselaw",),
               licence="No published terms. Decisions are excluded from copyright, FSEK art. 31 "
                       "(unverified on an official terms page)",
               commercial_use=None, ai_use=None, auth="none",
               rate_limit="unknown; 1 s spacing, no 429 seen in ~15 requests (2026-11)",
               terms_url="https://www.anayasa.gov.tr"),
        Source("Uyuşmazlık Mahkemesi Karar Arama", "https://kararlar.uyusmazlik.gov.tr",
               covers=("caselaw",),
               licence="No published terms; no robots.txt (404, 2026-11-10). Decisions are excluded "
                       "from copyright, FSEK art. 31 (unverified on an official terms page)",
               commercial_use=None, ai_use=None, auth="none",
               rate_limit="unknown; 1 s spacing, no 429 seen in ~10 requests (2026-11)",
               terms_url="https://www.uyusmazlik.gov.tr"),
        Source("Sayıştay Kararlar (Genel Kurul, Temyiz Kurulu, Daire)", "https://www.sayistay.gov.tr/KararlarDaire",
               covers=("caselaw",),
               licence="No terms page found (only an information-security policy); robots.txt has "
                       "no Disallow (2026-11-10). FSEK art. 31 (unverified on an official terms page)",
               commercial_use=None, ai_use=None, auth="none",
               rate_limit="unknown; 1 s spacing, no 429 or WAF block seen in ~12 requests (2026-11)",
               terms_url="https://www.sayistay.gov.tr/pages/145-bilgi-guvenligi-politikasi"),
        Source("Rekabet Kurumu Kurul Kararı Arama", "https://www.rekabet.gov.tr/tr/Kararlar",
               covers=("caselaw",),
               licence="No terms page found; no robots.txt (error page, 2026-11-10). Board decisions "
                       "are official texts, FSEK art. 31 (unverified on an official terms page)",
               commercial_use=None, ai_use=None, auth="none",
               rate_limit="unknown; 1 s spacing, no 429 seen in ~6 requests (2026-11)",
               terms_url="https://www.rekabet.gov.tr"),
        Source("Gelir İdaresi Başkanlığı Özelgeler", "https://gib.gov.tr/mevzuat/ozelgeler",
               covers=("caselaw",),
               licence="No terms page found; robots.txt 'User-agent: * Allow: /' (2026-11-10). "
                       "Advance tax rulings, not court decisions",
               commercial_use=None, ai_use=None, auth="none",
               rate_limit="unknown; 1 s spacing, no 429 seen in ~5 requests (2026-11)",
               terms_url="https://gib.gov.tr"),
    )
    caselaw_filters = {
        "court": "yargitay | danistay | istinaf_hukuk (regional appeal) | yerel_hukuk (first "
                 "instance) | kyb (kanun yararına bozma) | aym_bb (Constitutional Court, "
                 "individual applications) | aym_norm (Constitutional Court, norm review) | "
                 "uyusmazlik (Court of Jurisdictional Disputes) | sayistay_gk / sayistay_temyiz / "
                 "sayistay_daire (Court of Accounts: General Assembly, Appeals Board, chambers) | "
                 "rekabet (Competition Board) | gib_ozelge (tax rulings). Comma-separate Bedesten "
                 "courts; the others are searched one at a time. Default all five Bedesten courts.",
        "chamber": "exact chamber name (birimAdi), e.g. '3. Hukuk Dairesi', 'Hukuk Genel Kurulu', "
                   "'12. Ceza Dairesi', '6. Daire' (Danıştay); for sayistay_daire / sayistay_temyiz "
                   "the Daire number ('4'). Not for AYM, uyusmazlik, rekabet, gib_ozelge.",
        "date_from": "decision date from, YYYY-MM-DD (Sayıştay: year only; not uyusmazlik / rekabet)",
        "date_to": "decision date to, YYYY-MM-DD",
        "sort": "newest (default) | oldest | source (the source's own order; AYM: relevance)",
        "exact": "true = search the whole query as one phrase. Unquoted words are OR-ed: "
                 "quote phrases (\"kira tespiti\") or set exact. Also +must, -exclude, AND/OR/NOT.",
        "subject_only": "true = keep only decisions whose subject (DAVA: line; Yargıtay: first "
                        "sentence) has all the search words, from one source page at a time "
                        "(Bedesten courts only). Without it those hits are listed first.",
    }
    legislation_filters = {
        "type": "KANUN, CB_KARARNAME, YONETMELIK, CB_YONETMELIK, CB_KARAR, CB_GENELGE, KHK, "
                "TUZUK, KKY (kurum yönetmeliği), UY (üniversite), TEBLIGLER, MULGA (repealed); "
                "comma-separated. Default all.",
        "search_in": "title (default; falls back to full text when no title matches) | text",
        "exact": "true = full-text query as one exact phrase (search_in=text)",
        "number": "official number, e.g. 6098 (a query of only digits is treated as a number)",
        "sort": "newest | oldest (Resmî Gazete date); default: source order",
    }
    min_interval = {
        "bedesten.adalet.gov.tr": 3.5,
        "kararlarbilgibankasi.anayasa.gov.tr": 1.0,
        "normkararlarbilgibankasi.anayasa.gov.tr": 1.0,
        "kararlar.uyusmazlik.gov.tr": 1.0,
        "www.sayistay.gov.tr": 1.0,
        "www.rekabet.gov.tr": 1.0,
        "gib.gov.tr": 1.0,
    }
    notes = ("Yargıtay, Danıştay, BAM civil chambers, first-instance civil and AYM decisions "
             "(AYM norm review is read from normkararlarbilgibankasi.anayasa.gov.tr, same terms as "
             "the individual-application bank), plus Uyuşmazlık Mahkemesi, Sayıştay, Rekabet Kurulu and "
             "GİB özelge banks (court=...); consolidated legislation "
             "with per-article text. Quote multi-word phrases: unquoted words are OR-ed. "
             "Bedesten is slow on purpose (3.5 s between requests); an Uyuşmazlık text search takes "
             "~20 s server-side and sometimes over 60 s (2026-11-10). Newest Yargıtay data lags ~5 weeks (2026-11-07).")
    gaps = (
        "Yargıtay decisions from the last ~5 weeks: not yet in Bedesten (source lag, 2026-11-07)",
        ("KİK (public procurement board) decisions: ekapv2.kik.gov.tr API requires AES-signed "
         "request headers (anti-automation); not built"),
        ("BTK board decisions: the only search is www.btk.tr/api/, which robots.txt disallows "
         "for all user agents"),
        ("BDDK board decisions, Sigorta Tahkim Komisyonu awards: no official search endpoint "
         "(yargi-mcp uses a third-party web-search API); not built"),
        ("Yargıtay Karar Arama (karararama.yargitay.gov.tr), which could fill the Bedesten lag: "
         "connection times out from a UK IP (2026-11-10)"),
        ("Resmî Gazete (as-published texts, daily index): source exists (HTML only) but not built "
         "yet"),
        ("KVKK decisions: kvkk.gov.tr has no search endpoint (yargi-mcp uses a third-party "
         "web-search API); mostly decision summaries; not built"),
        "SPK, EPDK, RTÜK, BDDK and Ombudsman decisions: not researched yet",
        ("Professional-body rules never published in the Resmî Gazete, e.g. the TBB Meslek Kuralları "
         "(Türkiye Barolar Birliği): not in Bedesten (no title match, 2026-11-11); the TBB publishes "
         "them itself"),
        ("Regional administrative courts (Bölge İdare Mahkemeleri): not researched yet (Bedesten "
         "item types unverified)"),
        ("Regional appeal criminal chambers (BAM ceza daireleri) and first-instance criminal "
         "courts: no Bedesten item type queried (only ISTINAFHUKUK and YERELHUKUK, civil)"),
    )
    samples = {
        "caselaw_query": '"kira tespiti"',
        "decision_id": "605770700",
        "legislation_query": "borçlar kanunu",
        "law_id": "1.5.6098",
        "provision": "Madde 1",
    }

    # ----------------------------------------------------------------- case law
    async def search_caselaw(self, query, *, limit, page, filters):
        q = (query or "").strip()
        if _bool(filters.get("exact", "")) and '"' not in q and q:
            q = f'"{q}"'
        sort = str(filters.get("sort") or "newest").lower()
        if sort not in _SORTS:
            raise BadRequest(f"sort must be one of {', '.join(_SORTS)}")
        d_from = _parse_date(filters["date_from"], "date_from") if filters.get("date_from") else None
        d_to = _parse_date(filters["date_to"], "date_to") if filters.get("date_to") else None

        courts = [c.strip().lower() for c in str(filters.get("court") or "").split(",") if c.strip()]
        aym = [c for c in courts if c in _AYM_COURTS]
        other = [c for c in courts if c in _OTHER_COURTS]
        if (aym or other) and len(courts) > 1:
            raise BadRequest(f"{(aym or other)[0]} cannot be combined with other courts; search it separately. "
                             "Only the Bedesten courts (yargitay, danistay, istinaf_hukuk, yerel_hukuk, kyb) combine.")
        if aym:
            if filters.get("chamber"):
                raise BadRequest("chamber is not supported for AYM searches.")
            r = await self._search_aym(_AYM_COURTS[aym[0]], q, limit, page, sort, d_from, d_to)
        elif other:
            r = await self._search_other(_OTHER_COURTS[other[0]], q, limit, page, sort, d_from, d_to,
                                         filters.get("chamber"))
        else:
            items = []
            for c in courts:
                v = _BEDESTEN_COURTS.get(c) or (c.upper() if c.upper() in _COURT_NAMES else "")
                if not v:
                    raise BadRequest(f"Unknown court {c!r}. Use: "
                                     f"{', '.join([*_BEDESTEN_COURTS, *_AYM_COURTS, *_OTHER_COURTS])}.")
                items.append(v)
            bq = q
            terms = re.findall(r'"[^"]*"|\S+', q)
            dropped = [t for t in terms if not t.startswith('"') and _fold(t) in _GENERIC]
            if dropped and len(dropped) < len(terms):
                terms = [t for t in terms if t not in dropped]
                q = bq = " ".join(terms)
            if len(terms) > 1 and not re.search(r"\b(AND|OR|NOT)\b|(^|\s)[+-]", q):
                bq = " ".join(f"+{w}" for w in terms)   # the source ORs bare words and quoted phrases: require all
            r = await self._search_bedesten(bq, items, filters.get("chamber"), limit, page, sort, d_from, d_to)
            if bq != q:
                r.note = ('All words and quoted phrases are required (words not necessarily adjacent). '
                          'Quote a phrase ("kira tespiti") or pass exact=true for adjacent words; '
                          "use OR for alternatives.")
            if dropped and len(dropped) < len(re.findall(r'"[^"]*"|\S+', query or "")):
                r.note = (f"Left out {', '.join(dropped)}: it appears in nearly every decision. " + r.note).strip()
            if q and r.items:
                await self._mark_subjects(r, q, _bool(filters.get("subject_only", "")), limit, page,
                                          items, filters.get("chamber"), sort, d_from, d_to)
        if not aym and not other and q and sort != "source":
            r.note = " ".join(x for x in (r.note, "Ordered by date within each group: the source has no relevance "
                              "ranking and no subject search, so the subject of each hit on this page is read "
                              "from its text (first 10 hits; up to ~40 s, as the court site limits request rates). Words found in nearly every decision (dava, karar, mahkeme) do not "
                              "narrow the result. To narrow, add distinctive words, chamber or a date range; "
                              "sort=source gives the source's own order.") if x)
        return r

    async def _hit_subject(self, did: str) -> str | None:
        """Subject of one decision (cached); None when its text could not be read."""
        if did in _subjects:
            return _subjects[did]
        try:
            d = await _bpost("/emsal-karar/getDocumentContent", {"documentId": did})
            subj = _subject(_decode(d, ""))
        except (SourceError, NotFound, ValueError):
            return None
        return _lru(_subjects, did, subj, 2000)

    async def _mark_subjects(self, r, q, only, limit, page, items, chamber, sort, d_from, d_to):
        """Read each hit's subject line (DAVA: / first sentence), show it, and put hits whose
        subject has the search words first. subject_only=true keeps only those."""
        stems = _stems(q)
        if not stems:
            return
        sem = asyncio.Semaphore(3)

        async def one(h):
            async with sem:
                return await self._hit_subject(h.id)
        # The court site allows about one request per 3.5 s, so 10 reads take ~40 s; more would
        # pass the ~60 s many MCP clients wait for a reply.
        checked, rest = r.items[:_SUBJ_MAX], r.items[_SUBJ_MAX:]
        subs = await asyncio.gather(*(one(h) for h in checked))
        for h in rest:
            h.snippet = ("Subject: not checked (only the first 10 hits are read)" + (" " + h.snippet if h.snippet else "")).strip()
        on, off = [], []
        for h, sub in zip(checked, subs):
            if sub is None:
                tag, ok = "Subject: could not be read", False
            elif not sub:
                tag, ok = "Subject: not stated in the usual place; the words may appear only in passing", False
            else:
                ok = _subject_match(sub, stems)
                tag = (sub if sub.startswith("Claim: ") else f"Subject: {sub}") + (
                    "" if ok else " (the search words are NOT in the subject)")
            h.snippet = (tag + (" " + h.snippet if h.snippet else "")).strip()
            (on if ok else off).append(h)
        r.items = on + ([] if only else off + rest)
        what = (f"{len(on)} of the {len(subs)} decisions checked on this page have all the search words in "
                "their subject (the DAVA: line, or the claim the decision states)")
        if only:
            r.incomplete = True
            r.total = len(on)
            r.note = (f"subject_only: {what}; only those are shown. This checks one source page "
                      f"({len(subs)} decisions, the {'newest' if sort != 'oldest' else 'oldest'} first); "
                      f"page={page + 1} checks the next {limit}. " + r.note)
        else:
            r.note = (f"{what}; they are listed first, the rest after (within this page only, so the "
                      "order inside a page depends on limit). Pass subject_only=true to drop the others. " + r.note)

    async def _search_bedesten(self, q, item_types, chamber, limit, page, sort, d_from, d_to):
        if limit > 30:
            raise BadRequest(f"limit must be <= 30 for Yargıtay/Danıştay/istinaf searches (the source serves "
                             f"10 per page and limits request rates), got {limit}")
        if sum(c.isalnum() for c in q) < 3:
            raise BadRequest("query needs at least 3 letters/digits (no special characters)")
        data = {"pageSize": 10, "phrase": q}   # the source serves at most 10 per page, whatever is asked
        if item_types:
            data["itemTypeList"] = item_types
        if chamber:
            data["birimAdi"] = str(chamber).strip()
        # Bedesten stores the Turkish date as 21:00 (pre-2016: 22:00) UTC of the day before.
        # Bedesten ignores the date filter unless BOTH bounds are present, so fill the open one.
        if d_from or d_to:
            d_from = d_from or datetime.date(1900, 1, 1)
            d_to = d_to or datetime.date(2100, 1, 1)
            data["kararTarihiStart"] = f"{d_from - datetime.timedelta(days=1)}T21:00:00.000Z"
            data["kararTarihiEnd"] = f"{d_to}T20:59:59.999Z"
        if _SORTS[sort]:
            # DOCUMENT_ID breaks same-date ties so pages never overlap; the source ignores a
            # lowercase "asc" (returns newest first), so send the direction in capitals.
            data["sortFields"] = ["KARAR_TARIHI", "DOCUMENT_ID"]
            data["sortDirection"] = _SORTS[sort].upper()
        start = (page - 1) * limit             # first wanted hit, 0-based; source pages hold 10
        rows, res = [], {}
        for sp in range(start // 10 + 1, (start + limit - 1) // 10 + 2):
            res = await _bpost("/emsal-karar/searchDocuments", {**data, "pageNumber": sp}, paging=True)
            got = res.get("emsalKararList") or []
            rows += got
            if len(got) < 10:
                break
        hits = []
        for h in rows[start % 10:start % 10 + limit]:
            it = (h.get("itemType") or {}).get("name", "")
            birim = _clean(h.get("birimAdi"))
            base = _COURT_NAMES.get(it, "")
            court = birim if (not base or re.search(r"Mahkeme|Yargıtay|Danıştay", birim)) else f"{base} {birim}".strip()
            esas, karar = _clean(h.get("esasNo")), _clean(h.get("kararNo"))
            case = ", ".join(x for x in (f"E. {esas}" if esas else "", f"K. {karar}" if karar else "") if x)
            did = str(h["documentId"])
            hit = DecisionHit(id=did, title=f"{court} {case}".strip() or did, court=court,
                              date=_iso_from_tr(h.get("kararTarihiStr") or "") or _iso_from_utc(h.get("kararTarihi") or ""),
                              case_number=case, url=ICTIHAT_URL + did)
            _lru(_hits, did, hit, 1000)
            hits.append(hit)
        return Results(hits, total=res.get("total"))

    async def _search_aym(self, kind, q, limit, page, sort, d_from, d_to):
        host, tipi = _AYM[kind]
        body = {"kararTipi": tipi, "query": q, "page": page, "size": limit}
        if _SORTS[sort]:
            body.update(sort="kararTarihi", order=_SORTS[sort])
        if d_from:
            body["kararTarihiStart"] = d_from.isoformat()
        if d_to:
            body["kararTarihiEnd"] = d_to.isoformat()
        j = await self._aym_post(host, body)
        return Results([self._aym_hit(kind, h) for h in (j.get("data") or [])[:limit]], total=j.get("total"))

    @staticmethod
    async def _aym_post(host, body) -> dict:
        # A reused keep-alive connection hangs until timeout (verified 2026-11), so close it.
        # Even so a call (0.4 s search, ~1 s full text) now and then hangs to the timeout
        # (1 of 4 test runs, 2026-11-10): 15 s timeout, one retry on a network error.
        url = f"https://{host}/api/core/public/search"
        try:
            r = await _http.post(url, json=body, timeout=15.0, headers={"Connection": "close"})
        except Exception:  # network error
            r = await _http.post(url, json=body, timeout=15.0, headers={"Connection": "close"})
        if r.status_code != 200:
            raise SourceError(_http.error("Anayasa Mahkemesi", "search failed", r.status_code), r.status_code)
        try:
            return r.json()
        except ValueError:
            raise SourceError("Anayasa Mahkemesi: non-JSON reply", r.status_code)

    @staticmethod
    def _aym_meta(kind, h) -> tuple[str, str, str, str]:
        """(title, court, case_number, url) in AYM's own citation style."""
        host, tipi = _AYM[kind]
        enc = base64.urlsafe_b64encode(f"kbb:{h['id']}".encode()).decode().rstrip("=")
        url = f"https://{host}/kbb/pages/search/{tipi}?id={enc}"
        if kind == "bb":
            case = f"B. No: {h.get('basvuruNo', '')}"
            court = _clean(f"Anayasa Mahkemesi {h.get('kararVerenBirimLabel') or ''}")
            name = _tr_title(_clean(h.get("basvuruAdi")))
            title = f"{name} Başvurusu, {case}" if name else f"Anayasa Mahkemesi {case}"
        else:
            case = ", ".join(x for x in (f"E. {h['esasNo']}" if h.get("esasNo") else "",
                                         f"K. {h['kararNo']}" if h.get("kararNo") else "") if x)
            court = "Anayasa Mahkemesi"
            title = f"Anayasa Mahkemesi {case}"
        return title, court, case, url

    def _aym_hit(self, kind, h) -> DecisionHit:
        title, court, case, url = self._aym_meta(kind, h)
        return DecisionHit(id=f"aym:{kind}:{h['id']}", title=title, court=court,
                           date=(h.get("kararTarihi") or "")[:10], case_number=case,
                           snippet=_clean(re.sub(r"<[^>]+>", " ", h.get("kararKonusu") or ""))[:400],
                           url=url)

    async def get_decision(self, id):
        did = (id or "").strip()
        if m := _AYM_ID.match(did):
            return await self._get_aym(m[1].lower(), m[2].lower())
        if m := _OTHER_ID.match(did):
            return await self._get_other(m)
        if not did.isdigit():
            raise BadRequest(f"Bad decision id {id!r}. Use a Bedesten documentId (digits, e.g. "
                             "'605770700') or an id from search_caselaw: 'aym:bb:<uuid>', "
                             "'uyusmazlik:2026-366', 'sayistay:daire:40189', 'rekabet:<uuid>', 'gib:38890'.")
        url = ICTIHAT_URL + did
        d = await _bpost("/emsal-karar/getDocumentContent", {"documentId": did})
        pars = _paragraphs(_decode(d, url))
        if not pars:
            raise SourceError(f"Empty decision text for {did}", "empty")
        hit = _hits.get(did)
        if hit:
            title, court, date, case = hit.title, hit.court, hit.date, hit.case_number
        else:  # header looks like "(Kapatılan) 6. Hukuk Dairesi 2009/10893 E. , 2010/660 K."
            head = _clean(pars[0].replace("*", ""))
            m = re.match(r"^(.*?)\s*(\d{4}/\d+)\s*E\.\s*,\s*(\d{4}/\d+)\s*K\.", head)
            court = m[1].strip() if m else ""
            case = f"E. {m[2]}, K. {m[3]}" if m else ""
            title = f"{court} {case}".strip() if m else head[:120] or did
            dates = re.findall(r"(\d{1,2})[./](\d{1,2})[./](\d{4}) tarihinde", " ".join(pars[-5:]))
            date = f"{dates[-1][2]}-{int(dates[-1][1]):02d}-{int(dates[-1][0]):02d}" if dates else ""
            date = _decision_date_label(pars) or date
        return Decision(id=did, title=title, text="\n\n".join(pars), url=url, court=court,
                        date=date, case_number=case)

    async def _get_aym(self, kind, uuid):
        host, tipi = _AYM[kind]
        j = await self._aym_post(host, {"kararTipi": tipi, "id": uuid})
        rows = j.get("data") or []
        if not rows:
            raise NotFound(f"No {tipi} decision with id {uuid}")
        h = rows[0]
        title, court, case, url = self._aym_meta(kind, h)
        meta = {
            "Karar türü": _clean(h.get("kararTuruBasvuruSonucuLabel") or h.get("kararTuruDosyaSonucuLabel")),
            "Başvuru tarihi": h.get("basvuruTarihi") or "",
            "Resmî Gazete": _clean(f"{h.get('resmiGazeteTarihi') or ''} sayı {h['resmiGazeteSayisi']}")
            if h.get("resmiGazeteSayisi") else "",
            "Basın duyurusu": h.get("basinDuyurusuUrl") or "",
        }
        return Decision(id=f"aym:{kind}:{uuid}", title=title, text=_html_to_md(h.get("icerik") or ""),
                        url=url, court=court, date=(h.get("kararTarihi") or "")[:10], case_number=case,
                        summary=_html_to_md(h.get("kararKonusu") or ""),
                        metadata={k: v for k, v in meta.items() if v})

    # ------------------------------------------- other official decision banks
    async def _search_other(self, kind, q, limit, page, sort, d_from, d_to, chamber):
        q = q.replace('"', "").strip()   # these banks match the text as typed; no query syntax
        if kind == "gib":
            return await self._search_gib(q, limit, page, sort, d_from, d_to)
        if kind in _SAYISTAY:
            return await self._search_sayistay(kind, q, limit, page, sort, d_from, d_to, chamber)
        if d_from or d_to or chamber or sort == "oldest":
            raise BadRequest(f"court={'uyusmazlik' if kind == 'uyusmazlik' else kind} supports only a "
                             "query (no date, chamber or oldest sort).")
        if kind == "uyusmazlik":
            return await self._search_uyusmazlik(q, limit, page)
        return await self._search_rekabet(q, limit, page)

    @staticmethod
    async def _paged(fetch, size: int, limit: int, page: int):
        """limit rows from offset (page-1)*limit of a source with fixed `size`-row pages.
        fetch(n) -> (rows, total) for source page n (1-based)."""
        start = (page - 1) * limit
        first, last = start // size + 1, (start + limit - 1) // size + 1
        rows, total = [], None
        for n in range(first, last + 1):
            got, total = await fetch(n)
            rows += got
            if len(got) < size:
                break
        off = start - (first - 1) * size
        return rows[off:off + limit], total

    async def _search_uyusmazlik(self, q, limit, page):
        state = {}

        def hidden(h):
            return {n: (re.search(rf'name="{n}"[^>]*value="([^"]*)"', h) or (None, ""))[1]
                    for n in ("__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION")}

        async def call(send, *a, **kw):
            # Now and then a request hangs until the read timeout while the same call
            # otherwise answers in 0.5 s (landing page) / ~20 s (search) (2/3 test runs,
            # 2026-11-10): one retry on a network error. Form posts here only search.
            try:
                return await send(*a, **kw)
            except Exception:  # network error
                return await send(*a, **kw)

        async def form(data):
            # a full-text search takes ~20 s server-side (verified 2026-11), so a long timeout
            r = await call(_http.post, UYUSMAZLIK, data=data, timeout=45.0)
            if r.status_code != 200:
                raise SourceError(_http.error("Uyuşmazlık Mahkemesi", "search failed", r.status_code), r.status_code)
            return r.text

        async def fetch(n):
            if "html" not in state:   # page 1: the landing page lists all, newest first
                r = await call(_http.get, UYUSMAZLIK, timeout=20.0)
                if r.status_code != 200:
                    raise SourceError(_http.error("Uyuşmazlık Mahkemesi", "page failed", r.status_code), r.status_code)
                state["html"] = r.text
                if q:
                    state["html"] = await form({**hidden(r.text), "txtSearch": q,
                                                "rblSearchScope": "All", "btnSearch": "Ara"})
            if n > 1:
                state["html"] = await form({**hidden(state["html"]), "txtSearch": q, "rblSearchScope": "All",
                                            "__EVENTTARGET": "GridView1", "__EVENTARGUMENT": f"Page${n}"})
            h = state["html"]
            cur = re.search(r"<span>(\d+)</span>", h[h.find('id="GridView1"'):])
            if n > 1 and cur and int(cur[1]) != n:   # past the last page
                return [], None
            hits = []
            for esas, karar, tarih, href in re.findall(
                    r"<td>([^<]*)</td><td>([^<]*)</td><td>([^<]*)</td><td>\s*<a href='Uploads/([^']+)\.pdf'", h):
                case = f"E. {_clean(esas)}, K. {_clean(karar)}"
                did = f"uyusmazlik:{href}"
                hit = DecisionHit(id=did, title=f"Uyuşmazlık Mahkemesi {case}", court="Uyuşmazlık Mahkemesi",
                                  date=_iso_from_tr(tarih), case_number=case, url=f"{UYUSMAZLIK}Uploads/{href}.pdf")
                hits.append(_lru(_hits, did, hit, 1000))
            return hits, None

        rows, _ = await self._paged(fetch, 20, limit, page)
        return Results(rows, total=None, note="The source shows no hit count; 20 rows per source page.")

    async def _search_rekabet(self, q, limit, page):
        async def fetch(n):
            # the site ignores the filters unless every form field is sent
            params = {"sayfaAdi": "", "YayinlanmaTarihi": "", "PdfText": q, "KararTuruID": "",
                      "KararSayisi": "", "KararTarihi": ""}
            if n > 1:
                params["page"] = str(n)
            r = await _http.get(f"{REKABET}/tr/Kararlar", params=params)
            if r.status_code != 200:
                raise SourceError(_http.error("Rekabet Kurumu", "search failed", r.status_code), r.status_code)
            h = r.text
            total = re.search(r"Toplam\s*:\s*(\d+)", h)
            hits = []
            for tbl in re.findall(r'class="equalDivide">(.*?)</table>', h, re.S):
                cells = [_clean(re.sub(r"<[^>]+>", " ", c)) for c in re.findall(r"<td[^>]*>(.*?)</td>", tbl, re.S)]
                kid = re.search(rf"/Karar\?kararId=({_UUID})", tbl)
                if not kid or len(cells) < 6:
                    continue
                # cells: yayım tarihi, karar sayısı, (davalar link), karar tarihi, karar türü, (blank), konu
                did = f"rekabet:{kid[1]}"
                case = f"K. {cells[1]}" if cells[1] else ""
                hit = DecisionHit(id=did, title=f"Rekabet Kurulu {cells[1]}".strip(), court="Rekabet Kurulu",
                                  date=_iso_from_tr(cells[3]), case_number=case,
                                  snippet=(f"[{cells[4]}] " if cells[4] else "") + cells[-1][:400],
                                  url=f"{REKABET}/Karar?kararId={kid[1]}")
                hits.append(_lru(_hits, did, hit, 1000))
            return hits, int(total[1]) if total else None

        rows, total = await self._paged(fetch, 10, limit, page)
        return Results(rows, total=total)

    async def _sayistay_token(self, kind, fresh=False) -> str:
        path = _SAYISTAY[kind][0]
        if fresh or kind not in _say_tokens:
            r = await _http.get(f"{SAYISTAY}/{path}")
            m = re.search(r'name="__RequestVerificationToken"[^>]*value="([^"]+)"', r.text)
            if r.status_code != 200 or not m:
                raise SourceError(_http.error("Sayıştay", "form page failed", r.status_code), r.status_code)
            _say_tokens[kind] = m[1]
        return _say_tokens[kind]

    async def _search_sayistay(self, kind, q, limit, page, sort, d_from, d_to, chamber):
        path, pre, text_f, ch_f, cols, date_col, label = _SAYISTAY[kind]
        form = [("draw", "1"), ("start", str((page - 1) * limit)), ("length", str(limit)),
                ("search[value]", ""), ("search[regex]", "false")]
        for i, c in enumerate(cols):
            form += [(f"columns[{i}][data]", c), (f"columns[{i}][name]", ""),
                     (f"columns[{i}][searchable]", "true"), (f"columns[{i}][orderable]", "true"),
                     (f"columns[{i}][search][value]", ""), (f"columns[{i}][search][regex]", "false")]
        form += [("order[0][column]", str(date_col)), ("order[0][dir]", _SORTS[sort] or "desc")]
        if q:
            form.append((f"{pre}.{text_f}", q))
        dkey = "KARARTARIH" if kind == "genel_kurul" else "KARARTRH"
        if d_from:   # the form takes years only
            form.append((f"{pre}.{dkey}Baslangic", str(d_from.year)))
        if d_to:
            form.append((f"{pre}.{dkey}Bitis", str(d_to.year)))
        if chamber:
            if not ch_f or not re.match(r"^\d+", str(chamber).strip()):
                raise BadRequest("chamber for Sayıştay Daire / Temyiz searches is the Daire number, e.g. '4' "
                                 "or '4. Daire'; Genel Kurul has none.")
            form.append((f"{pre}.{ch_f}", re.match(r"^\d+", str(chamber).strip())[0]))
        j = None
        for fresh in (False, True):
            body = urlencode(form + [("__RequestVerificationToken", await self._sayistay_token(kind, fresh))])
            r = await _http.post(f"{SAYISTAY}/{path}/DataTablesList", content=body, headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest"})
            if r.status_code == 200 and "json" in r.headers.get("content-type", ""):
                j = r.json()
                break
        if j is None:
            raise SourceError(_http.error("Sayıştay", "search failed", r.status_code), r.status_code)
        hits = []
        for h in (j.get("data") or [])[:limit]:
            did = f"sayistay:{kind}:{h['Id']}"
            if kind == "genel_kurul":
                case, date, snip, court = f"K. {_clean(h.get('KARARNO'))}", h.get("KARARTARIH"), h.get("KARAROZETI"), "Sayıştay Genel Kurulu"
            elif kind == "temyiz":
                case, date, snip = "", h.get("TEMYIZTUTANAKTARIHI"), h.get("TEMYIZKARAR")
                court = f"Sayıştay Temyiz Kurulu ({h.get('ILAMDAIRESI')}. Daire ilamı)"
            else:
                case = ", ".join(x for x in (f"K. {_clean(h.get('KARARNO'))}" if h.get("KARARNO") else "",
                                             f"İlam {_clean(h.get('ILAMNO'))}" if h.get("ILAMNO") else "",
                                             f"m. {h['MADDENO']}" if h.get("MADDENO") else "") if x)
                date, snip = h.get("KARARTRH"), f"[{_clean(h.get('WEBKARARKONUSU'))}] {h.get('WEBKARARMETNI') or ''}"
                court = f"Sayıştay {h.get('YARGILAMADAIRESI')}. Daire"
            date = _iso_from_tr(date)
            title = f"{court} {case}".strip() if case else f"{court} {date}".strip()
            hit = DecisionHit(id=did, title=title, court=court, date=date, case_number=case,
                              snippet=_clean(snip)[:400], url=f"{SAYISTAY}/{path}/Detay/{h['Id']}/")
            hits.append(_lru(_hits, did, hit, 1000))
        note = "Sayıştay date filters work by year only." if (d_from or d_to) else ""
        return Results(hits, total=j.get("recordsFiltered"), note=note)

    async def _search_gib(self, q, limit, page, sort, d_from, d_to):
        body = {"status": 2, "deleted": False, "ktype": 99}
        if q:   # the site sends the same term for all three; they are OR-ed
            body.update(title=q, kanunNo=q, description=q)
        if d_from:
            body["ozelgeStartDate"] = f"{d_from}T00:00:00.000Z"
        if d_to:
            body["ozelgeEndDate"] = f"{d_to}T23:59:59.999Z"
        params = {"page": page - 1, "size": limit, "sortFieldName": "ozelgeTarih",
                  "sortType": "ASC" if sort == "oldest" else "DESC"}
        c = await self._gib_post(body, params)
        return Results([self._gib_hit(it) for it in (c.get("content") or [])[:limit]],
                       total=c.get("totalElements"))

    @staticmethod
    async def _gib_post(body, params) -> dict:
        r = await _http.post(GIB_LIST, params=params, json=body)
        if r.status_code != 200:
            raise SourceError(_http.error("Gelir İdaresi Başkanlığı", "özelge search failed", r.status_code), r.status_code)
        try:
            return r.json().get("resultContainer") or {}
        except ValueError:
            raise SourceError("Gelir İdaresi Başkanlığı: non-JSON reply", r.status_code)

    @staticmethod
    def _gib_hit(it) -> DecisionHit:
        no = _clean(it.get("ozelgeNo"))
        kanun = _clean(it.get("kanunTitle"))
        hit = DecisionHit(id=f"gib:{it['id']}", title=_clean(it.get("title")) or f"Özelge {no}",
                          court="Gelir İdaresi Başkanlığı (özelge)", date=(it.get("ozelgeTarih") or "")[:10],
                          case_number=f"Sayı {no}" if no else "",
                          snippet=f"{kanun} ({it.get('kanunNo')})" if kanun else "",
                          url=it.get("siteLink") or f"https://gib.gov.tr/mevzuat/kanun/{it.get('kanunId')}/ozelge/{it['id']}")
        return _lru(_hits, hit.id, hit, 1000)

    async def _get_other(self, m) -> Decision:
        if m["gib"]:
            c = await self._gib_post({"status": 2, "deleted": False, "ktype": 99, "id": int(m["gib"])},
                                     {"page": 0, "size": 1})
            rows = c.get("content") or []
            if not rows or str(rows[0].get("id")) != m["gib"]:
                raise NotFound(f"No özelge with id {m['gib']}")
            hit = self._gib_hit(rows[0])
            return Decision(id=hit.id, title=hit.title, text=_html_to_md(rows[0].get("description") or ""),
                            url=hit.url, court=hit.court, date=hit.date, case_number=hit.case_number,
                            metadata={"Kanun": hit.snippet} if hit.snippet else {})
        if m["sk"]:
            kind, sid = m["sk"].lower(), m["sid"]
            path = _SAYISTAY[kind][0]
            url = f"{SAYISTAY}/{path}/Detay/{sid}/"
            r = await _http.get(url)
            if r.status_code == 500:  # the source answers an unknown id with 500; retry once to rule out an outage
                r = await _http.get(url)
            h = r.text
            i = h.find('id="metin"')
            if r.status_code in (404, 500) or (r.status_code == 200 and i < 0):
                raise NotFound(f"No Sayıştay {kind} decision with id {sid}")
            if r.status_code != 200:
                raise SourceError(_http.error("Sayıştay", "decision failed", r.status_code), r.status_code)
            meta = {_clean(_http.html_to_md(k)).strip("*"): _clean(_http.html_to_md(v)) for k, v in re.findall(
                r'<div class="col-3">(.*?)</div>\s*<div class="col-9">(.*?)</div>', h[:i], re.S)}
            end = h.find('<div class="mt-auto', i)
            text = "\n\n".join(_paragraphs("<div " + h[i:end if end > 0 else None]))
            if not text:
                raise SourceError(f"Empty Sayıştay decision text for {sid}", "empty")
            hit = _hits.get(f"sayistay:{kind}:{sid}")
            label = {"genel_kurul": "Sayıştay Genel Kurulu", "temyiz": "Sayıştay Temyiz Kurulu",
                     "daire": f"Sayıştay {meta.get('Daire', '')}. Daire"}[kind]
            if kind == "temyiz":
                case = ", ".join(x for x in (f"Dosya {meta['Dosya No']}" if meta.get("Dosya No") else "",
                                             f"Tutanak {meta['Tutanak No']}" if meta.get("Tutanak No") else "") if x)
                date = _iso_from_tr(meta.get("Tutanak Tarihi"))
            else:
                case = hit.case_number if hit else (f"K. {meta['Karar No']}" if meta.get("Karar No") else "")
                date = _iso_from_tr(meta.get("Karar Tarihi"))
            title = f"{label} {case}".strip() if case else f"{label} {date}"
            return Decision(id=f"sayistay:{kind}:{sid}", title=title, text=text, url=url, court=label,
                            date=date, case_number=case, metadata={k: v for k, v in meta.items() if v})
        # PDFs: Uyuşmazlık Mahkemesi and Rekabet Kurulu
        if m["uy"]:
            did, url, court = f"uyusmazlik:{m['uy']}", f"{UYUSMAZLIK}Uploads/{m['uy']}.pdf", "Uyuşmazlık Mahkemesi"
        else:
            did, url, court = f"rekabet:{m['rk'].lower()}", f"{REKABET}/Karar?kararId={m['rk'].lower()}", "Rekabet Kurulu"
        r = await _http.get(url)
        if r.status_code == 404 or (r.status_code == 200 and not r.content.startswith(b"%PDF")):
            raise NotFound(f"No {court} decision {did}")
        if r.status_code != 200:
            raise SourceError(_http.error(court, "decision failed", r.status_code), r.status_code)
        text = _http.pdf_text(r.content)
        if not text:
            raise SourceError(f"{court} PDF has no text layer; open {url}", "pdf")
        hit = _hits.get(did)
        if hit:
            title, date, case = hit.title, hit.date, hit.case_number
        else:
            flat = text.replace("\n", " ")
            if m["uy"]:
                e = re.search(r"ESAS NO\s*:\s*(\d{4}/\d+)", flat)
                k = re.search(r"KARAR NO\s*:\s*(\d{4}/\d+)", flat)
                d = re.search(r"KARAR TR?\s*:\s*([\d./]+)", flat)
                case = ", ".join(x for x in (f"E. {e[1]}" if e else "", f"K. {k[1]}" if k else "") if x)
            else:
                k = re.search(r"Karar Sayısı\s*:\s*(\S+)", flat)
                d = re.search(r"Karar Tarihi\s*:\s*([\d./]+)", flat)
                case = f"K. {k[1]}" if k else ""
            date = _iso_from_tr(d[1]) if d else ""
            title = f"{court} {case}".strip()
        return Decision(id=did, title=title, text=text, url=url, court=court, date=date, case_number=case)

    # -------------------------------------------------------------- legislation
    async def search_legislation(self, query, *, limit, page, filters):
        q = _clean(query)
        types = []
        for t in str(filters.get("type") or "").split(","):
            t = t.strip().upper()
            if t:
                if t not in _TUR_ID:
                    raise BadRequest(f"Unknown type {t!r}. Use: {', '.join(_TUR_ID)}.")
                types.append(t)
        search_in = str(filters.get("search_in") or "").lower()
        if search_in not in ("", "title", "text"):
            raise BadRequest("search_in must be 'title' or 'text'")
        number = str(filters.get("number") or "").strip()
        if not number and q.isdigit():
            number, q = q, ""
        if number and not number.isdigit():
            raise BadRequest(f"number must be digits, got {number!r}")
        sort = str(filters.get("sort") or "").lower()
        if sort and sort not in ("newest", "oldest"):
            raise BadRequest("sort must be newest or oldest")

        if limit > 20:
            raise BadRequest(f"limit must be <= 20 for Bedesten legislation searches, got {limit}")
        base = {"pageSize": limit, "pageNumber": page}
        if types:
            base["mevzuatTurList"] = types
        if number:
            base["mevzuatNo"] = number
        if sort:
            base.update(sortFields=["RESMI_GAZETE_TARIHI"], sortDirection=_SORTS[sort].upper())  # "asc" is ignored
        note = ""

        def text_query(phrase=q):
            return {**base, "phrase": phrase, "basliktaAra": False, "tamCumle": _bool(filters.get("exact", ""))}

        if not q:
            res = await _bpost("/mevzuat/searchDocuments", base, paging=True)
        elif search_in == "text":
            res = await _bpost("/mevzuat/searchDocuments", text_query(), paging=True)
        else:
            res = await _bpost("/mevzuat/searchDocuments", {**base, "mevzuatAdi": q}, paging=True)
            if _fold(q) == "anayasa" and page == 1 and not number and (not types or "KANUN" in types):
                # the source matches whole title words: "Anayasa" misses "...Anayasası" (Law 2709)
                const = await _bpost("/mevzuat/searchDocuments", {**base, "mevzuatAdi": "Anayasası",
                                     "mevzuatTurList": ["KANUN"], "mevzuatNo": "2709"}, paging=True)
                top = const.get("mevzuatList") or []
                if top:
                    old = res.get("mevzuatList") or []
                    rest = [h for h in old if h.get("mevzuatNo") != top[0].get("mevzuatNo")]
                    res = {**res, "mevzuatList": top[:1] + rest,
                           "total": (res.get("total") or 0) + (len(rest) == len(old))}
            if not res.get("total") and search_in == "":
                # unquoted words are OR-ed ("Meslek Kuralları" -> 2,079 unrelated texts): use the phrase
                quote = len(q.split()) > 1 and '"' not in q
                res = await _bpost("/mevzuat/searchDocuments",
                                   text_query(f'"{q}"' if quote else q), paging=True)
                if res.get("total"):
                    note = (f"No title matches; these are full-text matches{' for the exact phrase' if quote else ''}. "
                            "Rules never published in the Resmî Gazete (e.g. TBB Meslek Kuralları) are not "
                            "in this source.")
        if search_in == "text" and len(q.split()) > 1 and '"' not in q and not _bool(filters.get("exact", "")):
            note = "Full-text words are OR-ed; pass exact=true for the exact phrase."
        hits, fetched, undated = [], False, 0
        for h in (res.get("mevzuatList") or [])[:limit]:
            law = _Law(h)
            _lru(_laws, law.id, law, 200)
            rg = (h.get("resmiGazeteTarihi") or "")[:10]
            # Bedesten's index often lacks the date; it is in the text header. Read it for a
            # cached text, and fetch at most one text: the exact title or number match.
            if not rg and (law.mid in _fulltexts or (not fetched and (
                    _fold(law.title) == _fold(q) or (number and law.no == number)))):
                fetched = fetched or law.mid not in _fulltexts
                try:
                    rg = _rg_date(await _fulltext(law))
                except SourceError:
                    pass
            undated += not rg
            snippet = ", ".join(x for x in (f"Resmî Gazete {rg}" if rg else "",
                                            f"sayı {h['resmiGazeteSayisi']}" if h.get("resmiGazeteSayisi") else "") if x)
            hits.append(LawHit(id=law.id, title=law.title, type=(h.get("mevzuatTur") or {}).get("name", ""),
                               number=law.no, date=rg,
                               status="mülga (repealed)" if law.tur == 5 else "",
                               snippet=snippet, url=law.url))
        if undated:
            note = " ".join(x for x in (note, "Results without a date: the source's index lacks the "
                                               "Resmî Gazete date (get_legislation_text shows it).") if x)
        return Results(hits, total=res.get("total"), note=note)

    async def get_legislation_toc(self, id):
        law = await _resolve(id)
        tree = await _tree_or_empty(law.mid)
        entries, have = [], set()
        for level, node, lab in _walk(tree):
            if lab and lab != DIGER:
                t = _clean(node.get("title"))
                entries.append(TocEntry(f"{lab} - {t}" if t else lab, level, lab))
                have.add(lab)
            elif lab == DIGER:
                entries.append(TocEntry(f"{DIGER} (işlenemeyen hükümler, yürürlük tablosu)", level, DIGER))
            else:
                entries.append(TocEntry(_clean(node.get("maddeBaslik")) or "(başlıksız)", level, ""))
        # ek / geçici / mükerrer articles are not in the tree: take them from the full text
        try:
            extra = [lab for lab in _segments(await _fulltext(law)) if lab not in have]
        except SourceError:
            extra = []
        if extra:
            entries.append(TocEntry("Ek, geçici ve diğer maddeler (tam metinden)", 0, ""))
            entries += [TocEntry(lab, 1, lab) for lab in extra]
        if not entries:
            raise NotFound(f"No table of contents for {law.title}; use get_legislation_text.")
        return Toc(id=law.id, title=law.title, url=law.url, entries=entries)

    async def get_legislation_provision(self, id, provision):
        law = await _resolve(id)
        label = _norm_label(provision)
        tree = await _tree_or_empty(law.mid)
        node = next((n for _, n, lab in _walk(tree) if lab == label), None)
        if node:
            d = await _bpost("/mevzuat/getDocumentContent",
                             {"documentType": "MADDE", "id": str(node["maddeId"])})
            pars = _paragraphs(_decode(d, law.url))
            if label != DIGER:
                # cut where an article folded into this one (ek / geçici) begins
                for i, p in enumerate(pars):
                    lab = _art_start(p)
                    if lab and lab != label and i > 0:
                        pars = pars[:i]
                        break
        else:
            pars = await _fulltext(law)
            span = _segments(pars).get(label)
            if not span:
                raise NotFound(f"{label} not found in {law.title} ({law.id}). "
                               "See get_legislation_toc for the labels.")
            pars = pars[span[0]:span[1]]
        return Provision(law_id=law.id, law_title=law.title, provision=label,
                         text="\n\n".join(pars), url=law.url, as_of=_as_of(tree))

    async def get_legislation_text(self, id):
        law = await _resolve(id)
        pars = await _fulltext(law)
        head = " ".join(pars[:12])
        meta = {}
        for k, rx in (("Kanun numarası", r"Kanun Numarası\s*:\s*(\d+)"),
                      ("Kabul tarihi", r"Kabul Tarihi\s*:\s*([\d/.]+)"),
                      ("Resmî Gazete", _RG_HEAD.pattern)):
            if m := re.search(rx, head.replace("*", "")):
                meta[k] = " sayı ".join(m.groups())
        return LawText(id=law.id, title=law.title, text="\n\n".join(pars), url=law.url, metadata=meta,
                       as_of=_as_of(_trees.get(law.mid) or {}))   # only if the tree is already fetched
