"""Guatemala: Corte de Constitucionalidad judgments by id, read from the court's own PDF
store (jurisprudencia.cc.gob.gt/Sentencias/<n>.<expediente>.pdf).

What is not here, and why (checked 2026-11-06 from a UK IP, plain httpx with our UA):
  * Case-law search: the CC's search portal (consultajur.cc.gob.gt/wcJur/Portal/...) and
    its main site (www.cc.gob.gt, incl. any terms page) answer with a Cloudflare
    "Just a moment..." challenge. So there is no search: get_decision only, for ids/links
    the user already has (they are what web searches for CC rulings return).
  * Legislation: www.congreso.gob.gt answers even /robots.txt with an Incapsula block;
    the gazette (www.dca.gob.gt) and SAT (portal.sat.gob.gt) with Cloudflare blocks.
  * Organismo Judicial / CENADOJ: www.oj.gob.gt is unreachable over https and gives a WAF
    403 over http; ww2.oj.gob.gt times out; jurisprudencia.oj.gob.gt has a broken TLS
    chain (unable to get local issuer certificate).
  * Retried 2026-11-10: congreso.gob.gt (www/bare, http/https) still Incapsula 403 even on
    robots.txt; dca.gob.gt Cloudflare 403; www.oj.gob.gt https no connection, http WAF 403;
    jurisprudencia.oj.gob.gt 403; ww2.oj.gob.gt timeout; www.cc.gob.gt robots.txt answers
    (User-agent: * Allow: /) but its pages are a Cloudflare 403.
  * Unofficial constitution copies considered and not used (2026-11-10): Constitute Project
    (terms: content "solely for providing information to users of this site", commercial use
    "expressly prohibited"); Georgetown PDBA guate93.html (official texts public domain, but
    commercial use of PDBA materials needs prior permission, and its copy lacks Art. 281).

Gotchas this code encodes:
  * The PDF file name is "<internal number>.<expediente(s)>.pdf", e.g.
    "850297.3670-2022.pdf" or "850891.3450-2021 y 3475-2021.pdf" (joined cases). The
    internal number cannot be derived from the expediente, so the id is the file stem.
  * Unknown files answer a small HTTP 404 page; /Sentencias/ itself is 403 (no listing).
  * Every page starts with a running header (expediente, "Página n de m", court name);
    we strip it. The text layer splits some words around accented letters
    ("promovi ó", "indemnizaci ón"); we rejoin the common patterns, others stay.
  * The date is written in words: "Guatemala, veinticuatro de agosto de dos mil veintidós."
  * robots.txt (jurisprudencia.cc.gob.gt, 2026-11-05/06): Cloudflare-managed,
    "User-agent: * / Content-Signal: search=yes,ai-train=no,use=reference / Allow: /",
    Amazonbot disallowed; no Crawl-delay.
"""
from __future__ import annotations

import re
import unicodedata
from urllib.parse import quote, unquote

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision

HOST = "https://jurisprudencia.cc.gob.gt"
COURT = "Corte de Constitucionalidad"
_ID = re.compile(r"(\d{1,9})\.(\d{1,5}-\d{4}(?:(?:\s*,\s*|\s+y\s+)\d{1,5}-\d{4})*)", re.I)
_HEADER = re.compile(r"^(Expedientes?\b.*|\d{1,5}-\d{4}(\s*(,|y)\s*\d{1,5}-\d{4})*|P[áa]gina \d+ de \d+|"
                     r"CORTE DE CONSTITUCIONALIDAD|REP[ÚU]BLICA DE GUATEMALA,? C\.? ?A\.?)$", re.I)
_MONTHS = {m: i for i, m in enumerate(
    ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
     "septiembre", "octubre", "noviembre", "diciembre"), 1)}
_MONTHS["setiembre"] = 9
_DATE = re.compile(r"Guatemala,\s+([a-záéíóúñ ]{3,40}?)\s+de\s+(" + "|".join(_MONTHS) +
                   r")\s+de\s+((?:dos\s+mil|mil\s+novecientos)[a-záéíóúñ ]{0,40}?)\s*\.", re.I)
_NUM = {"un": 1, "uno": 1, "primero": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6,
        "siete": 7, "ocho": 8, "nueve": 9, "diez": 10, "once": 11, "doce": 12, "trece": 13,
        "catorce": 14, "quince": 15, "dieciseis": 16, "diecisiete": 17, "dieciocho": 18,
        "diecinueve": 19, "veinte": 20, "treinta": 30, "cuarenta": 40, "cincuenta": 50,
        "sesenta": 60, "setenta": 70, "ochenta": 80, "noventa": 90, "novecientos": 900}
_cache: dict[str, Decision] = {}


def _norm_id(id) -> str:
    s = _http.clean(unquote(str(id or ""))).removesuffix(".pdf").removesuffix(".PDF")
    m = _ID.search(s.rsplit("/", 1)[-1])
    if not m:
        raise BadRequest("Guatemalan ids are the CC's PDF file names without '.pdf', e.g. "
                         "'850297.3670-2022' (internal number . expediente), or a "
                         f"jurisprudencia.cc.gob.gt/Sentencias/... link; got {id!r}.")
    return f"{m[1]}.{m[2]}"


def _url(id: str) -> str:
    return f"{HOST}/Sentencias/{quote(id)}.pdf"


def _plain(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")


def _words_to_int(s: str) -> int | None:
    """'veinticuatro' -> 24, 'dos mil veintidós' -> 2022, 'mil novecientos noventa y nueve' -> 1999."""
    total = cur = 0
    for w in _plain(s).split():
        if w == "y":
            continue
        if w == "mil":
            total += (cur or 1) * 1000
            cur = 0
        elif w in _NUM:
            cur += _NUM[w]
        elif w.startswith("veinti") and w[6:] in _NUM:
            cur += 20 + _NUM[w[6:]]
        else:
            return None
    return total + cur


def _date(text: str) -> str:
    m = _DATE.search(text[:3000])
    if not m:
        return ""
    d, y = _words_to_int(m[1]), _words_to_int(m[3])
    if not d or not y or not 1 <= d <= 31:
        return ""
    return f"{y:04d}-{_MONTHS[m[2].lower()]:02d}-{d:02d}"


def _fix(s: str) -> str:
    s = re.sub(r"([A-Za-zÁÉÍÓÚÑáéíóúñü]) ([áéíóú])(?![A-Za-zÁÉÍÓÚÑáéíóúñü])", r"\1\2", s)  # "promovi ó" -> "promovió"
    s = re.sub(r"([a-zñ]) (ón|ía|ías|ían|ás|és)\b", r"\1\2", s)                   # "indemnizaci ón"
    s = re.sub(r"\b([Aa]rt) (ículos?)\b", r"\1\2", s)
    s = re.sub(r"\b([b-df-np-tv-xzB-DF-NP-TV-XZ]) ([áéíóú][a-zñ])", r"\1\2", s)   # "S éptimo", "p úblico"
    return re.sub(r" +([,.;:)])", r"\1", s)


def _is_heading(ln: str) -> bool:
    letters = [c for c in ln if c.isalpha()]
    return len(ln) <= 90 and len(letters) >= 4 and all(c.isupper() for c in letters)


def _reflow(raw: str) -> str:
    """PDF text layer -> paragraphs: drop running page headers, rejoin wrapped lines."""
    lines: list[str] = []
    for pg in raw.split("\n\n"):
        pl = pg.split("\n")
        k = 0
        while k < len(pl) and k < 7 and _HEADER.match(pl[k]):
            k += 1
        lines += pl[k:]
    paras: list[str] = []
    cur = ""
    for ln in (_http.clean(x) for x in lines):
        if not ln:
            continue
        head = _is_heading(ln)
        new = (not cur or head or _is_heading(cur)
               or (cur[-1] in ".:" and (ln[0].isupper() or ln[0] in "\"“«(")))
        if new:
            if cur:
                paras.append(cur)
            cur = ln
        else:
            cur = cur[:-1] + ln if cur.endswith("-") and ln[:1].islower() else f"{cur} {ln}"
    if cur:
        paras.append(cur)
    return "\n\n".join(_fix(p) for p in paras)


class Guatemala(Jurisdiction):
    code = "gt"
    name = "Guatemala"
    languages = ("es",)
    aliases = ("guatemala", "gtm")
    sources = (
        Source(
            name="Corte de Constitucionalidad – sentencias PDF (jurisprudencia.cc.gob.gt)",
            url=HOST + "/Sentencias/",
            covers=("caselaw",),
            licence=("unknown: no licence on the PDF host; the CC's terms (www.cc.gob.gt) sit behind a "
                     "Cloudflare challenge; robots.txt Content-Signal search=yes, ai-train=no, use=reference"),
            commercial_use=None,   # terms not readable
            ai_use=False,          # robots.txt content signal ai-train=no (ai-input not set)
            auth="none",
            rate_limit=("unknown; 1 s spacing, no 429 seen in ~10 requests (2026-11-06); "
                        "no Crawl-delay in robots.txt"),
            terms_url="https://www.cc.gob.gt/",
            warning=("Constitutional Court rulings by id only (no search: the CC's search portal blocks "
                     "automated clients); robots.txt reserves the content against AI training "
                     "(ai-train=no, use=reference)."),
        ),
    )
    min_interval = {"jurisprudencia.cc.gob.gt": 1.0}
    notes = ("Case law: Corte de Constitucionalidad rulings by PDF id only (no search). Congress, "
             "gazette and Organismo Judicial sites block automated clients; no legislation.")
    gaps = (
        "Case-law search (CC portal consultajur.cc.gob.gt): bot check / blocks our client (Cloudflare); rulings by id only",
        "Legislation (Congreso, gazette dca.gob.gt, SAT): bot check / blocks our client (Incapsula / Cloudflare; again 2026-11-10); no usable unofficial copy (Constitute: non-commercial, site-only use; PDBA: commercial use needs permission, Art. 281 missing)",
        "Supreme Court and ordinary-court case law (Organismo Judicial / CENADOJ): unreachable (WAF 403, timeouts, bad TLS; 2026-11-06, again 2026-11-10)",
    )
    samples = {"decision_id": "850297.3670-2022"}

    async def get_decision(self, id):
        id = _norm_id(id)
        if id in _cache:
            return _cache[id]
        url = _url(id)
        r = await _http.get(url)
        if r.status_code == 404:
            raise NotFound(f"No CC ruling PDF {id} at jurisprudencia.cc.gob.gt (HTTP 404).")
        if r.status_code != 200 or not r.content.startswith(b"%PDF"):
            raise SourceError(_http.error("CC Guatemala", f"PDF not available ({url})", r.status_code),
                              r.status_code)
        raw = unicodedata.normalize("NFC", _http.pdf_text(r.content))  # text layer has combining accents
        if len(raw) < 200:
            raise SourceError(f"CC Guatemala: {id} has no text layer (scanned PDF; no OCR here).", 200)
        text = _reflow(raw)
        exp = id.split(".", 1)[1]
        d = Decision(id=id, title=f"{COURT} {exp}", text=text, url=url, court=COURT,
                     date=_date(re.sub(r"\s+", " ", raw)), case_number=exp)
        return _http.lru_put(_cache, id, d, 16)
