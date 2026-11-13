"""Haiti: a small set of laws from the document library of the Conseil Supérieur du Pouvoir
Judiciaire (CSPJ, cspj.ht), the constitutional body that governs the judiciary.

How the source works (verified 2026-11-06, UK IP, honest User-Agent):
  * WordPress site. Its "Bibliothèque de documents" page is filled by a script, but the files
    behind it are in the public WordPress REST API:
    GET /wp-json/wp/v2/media?mime_type=application/pdf&per_page=100 (header X-WP-Total).
    In 2026-11 it held 22 PDFs: ~17 laws and decree-laws (some are full Le Moniteur issues),
    plus a judges' ethics guide and two non-legislative files, which are filtered out here.
  * The id is the WordPress media id ("1396"); GET /wp-json/wp/v2/media/<id> gives the PDF url
    and its size (media_details.filesize). The url shown is the PDF itself.
  * Texts come from the PDFs' own text layer (pypdf, no OCR). 6 of 17 laws are scans with no
    text layer; for those the text methods raise SourceError and point to the PDF. Some text
    layers are the publisher's own poor OCR (e.g. id 1392, the 1961 juvenile law).
  * Titles are the uploader's file titles; date and Le Moniteur number are read from them when
    present. The texts are as published (not consolidated).

Terms: cspj.ht has no terms-of-use page; the footer says only "Droit d'auteur © 2026 Conseil
Supérieur du Pouvoir Judiciaire". Nothing on automated access. robots.txt (2026-11-05):
"User-agent: * / Disallow: /wp-admin/ / Allow: /wp-admin/admin-ajax.php", no Crawl-delay.

Constitution (added 2026-11-10): the Cour de cassation site (courdecassation.ht, Django, no robots.txt
(404), no terms page) links two static PDFs from /publication/: "constitution1" = the 1987 original
(text layer, 497 "Article" lines) and "constitution2" = the 2011 amended text, a scan with no text
layer. Only the 1987 original is readable here, under the id "constitution-1987"; it is NOT the
in-force text (2011 amendment missing). The static URL carries a content hash, so it is looked up
from /publication/ each time.

Not used (2026-11-05/06): see research/ht.md (Cour de cassation database empty, Parliament
TLS broken, Le Moniteur has no live site, budget.gouv.ht in maintenance, laloidemabouche.ht
bot challenge, mjsp.gouv.ht and primature.gouv.ht hold no legal texts).
"""
from __future__ import annotations

import html
import re
import unicodedata

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import LawHit, LawText, Provision, Results, Toc, TocEntry

HOST = "cspj.ht"
BASE = f"https://{HOST}"
API = BASE + "/wp-json/wp/v2/media"
SOURCE = "CSPJ document library"
MAX_BYTES = 40_000_000
MAX_LIMIT = 50
CC_BASE = "https://www.courdecassation.ht"
CONST_ID = "constitution-1987"
CONST_TITLE = "Constitution de la République d'Haïti (1987, texte original; amendement de 2011 non inclus)"

_LAWLIKE = re.compile(r"\b(lois?|d[ée]crets?(-lois?)?|constitution|codes?|arr[êe]t[ée]s?)\b", re.I)
_MONTHS = {"janvier": 1, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6, "juillet": 7,
           "aout": 8, "septembre": 9, "octobre": 10, "novembre": 11, "decembre": 12}
_FR_DATE = re.compile(r"\b(1er|\d{1,2})\s+([a-zéèêûô0]+)\s+(\d{4})\b", re.I)
_MONITEUR = re.compile(r"MONITEUR\s+((?:SP[ÉE]CIAL\s+)?NO\.?\s*\d+)", re.I)
_ART = re.compile(r"^(?:Article|ARTICLE|Art)[\s.\-]*"
                  r"(premier|1er|ler|\d+(?:\.\d+)*(?:\s?(?:bis|ter|quater))?)"
                  r"(?=\s*(?:modifi\S*\s*)?(?:[.:\-–—]|$|\s+[A-ZÀ-Ý«]))", re.I)
_HEAD = re.compile(r"^(LIVRE|TITRE|CHAPITRE|SECTION|Livre|Titre|Chapitre|Section)\b")
_HEAD_LEVEL = {"livre": 0, "titre": 0, "chapitre": 1, "section": 2}
_cache: dict = {}


def _fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def fr_date(s: str) -> str:
    """First French date in s ('vendredi 9 mai 2014', '1er juillet 1941') as YYYY-MM-DD, else ''."""
    for d, mon, y in _FR_DATE.findall(s):
        m = _MONTHS.get(_fold(mon).replace("0", "o"))
        if m:
            return f"{y}-{m:02d}-{1 if d.lower() == '1er' else int(d):02d}"
    return ""


def _title(m: dict) -> str:
    return _http.clean(html.unescape(m.get("title", {}).get("rendered", "")))


def _hit(m: dict) -> LawHit:
    t = _title(m)
    kind = _LAWLIKE.search(t)
    mon = _MONITEUR.search(t)
    size = (m.get("media_details") or {}).get("filesize") or 0
    bits = []
    if mon:
        bits.append("Le Moniteur " + _http.clean(mon[1]))
    if size:
        bits.append(f"PDF {size / 1e6:.1f} MB")
    return LawHit(id=str(m["id"]), title=t, type=kind[1].capitalize() if kind else "",
                  date=fr_date(t), snippet="; ".join(bits), url=m["source_url"])


async def _library() -> list[dict]:
    out, n = [], 1
    while n <= 5:
        r = await _http.get(f"{API}?mime_type=application/pdf&per_page=100&page={n}"
                            "&_fields=id,title,source_url,media_details")
        if r.status_code != 200:
            raise SourceError(_http.error(SOURCE, "library listing failed", r.status_code), r.status_code)
        out += r.json()
        if n >= int(r.headers.get("X-WP-TotalPages", "1") or 1):
            break
        n += 1
    seen, laws = set(), []
    for m in out:   # newest first; drop re-uploads with the same title
        t = _title(m)
        if _LAWLIKE.search(t) and _fold(t) not in seen:
            seen.add(_fold(t))
            laws.append(m)
    return laws


def _paras(lines: list[str]) -> str:
    """Join PDF layout lines into paragraphs: break after a line ending a sentence or clause."""
    out, cur = [], []
    for ln in lines:
        if not ln:
            if cur:
                out.append(" ".join(cur))
                cur = []
            continue
        if cur and (_ART.match(ln) or _HEAD.match(ln)):
            out.append(" ".join(cur))
            cur = []
        cur.append(ln)
        if re.search(r"[.:;]$", ln):
            out.append(" ".join(cur))
            cur = []
    if cur:
        out.append(" ".join(cur))
    return "\n\n".join(out)


def _label(raw: str) -> str:
    raw = raw.lower().replace(" ", "")
    return "1" if raw in ("premier", "1er", "ler") else raw


def norm_provision(p: str) -> str:
    """'Article 5', 'art. 5', 'Art 5.1', '5', 'Article 1er' -> '5' / '5.1' / '1'; keeps ' (2)'."""
    p = _http.clean(p)
    rep = re.search(r"\s*\((\d+)\)$", p)
    suffix = f" ({rep[1]})" if rep and rep[1] != "1" else ""
    p = p[:rep.start()] if rep else p
    p = re.sub(r"^(article|art)[\s.\-]*", "", p, flags=re.I).strip(" .-")
    return _label(p) + suffix


async def _const_url() -> str:
    r = await _http.get(CC_BASE + "/publication/")
    m = re.search(r'href="(/static/pdfs/constitution1\.[0-9a-f]+\.pdf)"', r.text) if r.status_code == 200 else None
    if not m:
        raise SourceError(_http.error(SOURCE, "Constitution link not found on courdecassation.ht", r.status_code),
                          r.status_code)
    return CC_BASE + m[1]


async def _doc(id: str) -> dict:
    if id != CONST_ID and not re.fullmatch(r"\d{1,7}", id or ""):
        raise BadRequest("Haitian law ids are CSPJ library media ids, digits only, e.g. '1396', "
                         f"or '{CONST_ID}'.")
    if id in _cache:
        return _cache[id]
    if id == CONST_ID:
        m = {"title": {"rendered": CONST_TITLE}, "source_url": await _const_url(), "media_details": {}}
    else:
        m = await _media(id)
    return await _parse(id, m)


async def _media(id: str) -> dict:
    r = await _http.get(f"{API}/{id}?_fields=id,title,source_url,mime_type,media_details")
    if r.status_code in (400, 401, 404):
        raise NotFound(f"No document {id} in the CSPJ library.")
    if r.status_code != 200:
        raise SourceError(_http.error(SOURCE, "document lookup failed", r.status_code), r.status_code)
    m = r.json()
    if m.get("mime_type") != "application/pdf" or not _LAWLIKE.search(_title(m)):
        raise NotFound(f"Document {id} in the CSPJ library is not a law PDF.")
    return m


async def _parse(id: str, m: dict) -> dict:
    size = (m.get("media_details") or {}).get("filesize") or 0
    if not size:
        h = await _http.request("HEAD", m["source_url"])
        size = int(h.headers.get("content-length", "0") or 0)
    if size > MAX_BYTES:
        raise SourceError(f"Error ({SOURCE}): PDF is {size / 1e6:.0f} MB, too large to fetch here. "
                          f"Open it: {m['source_url']}", 413)
    g = await _http.get(m["source_url"])
    if g.status_code != 200 or not g.content.startswith(b"%PDF"):
        raise SourceError(_http.error(SOURCE, "PDF download failed", g.status_code), g.status_code)
    text = _http.pdf_text(g.content)
    if not text:
        raise SourceError(f"Error ({SOURCE}): this PDF is a scan with no text layer (no OCR here). "
                          f"Open it: {m['source_url']}", 200)
    lines = text.split("\n")
    entries, spans, counts, start = [], {}, {}, None
    for i, ln in enumerate(lines):
        if re.search(r"\.{5,}", ln):          # table-of-contents line with dot leaders
            continue
        a, h = _ART.match(ln), _HEAD.match(ln)
        if (a or h) and start:
            spans[start[0]] = (start[1], i)
            start = None
        if a:
            lab = _label(a[1])
            counts[lab] = counts.get(lab, 0) + 1
            if counts[lab] > 1:
                lab = f"{lab} ({counts[lab]})"
            entries.append(TocEntry(title=ln[:120], level=3, provision=lab))
            start = (lab, i)
        elif h:
            entries.append(TocEntry(title=ln[:120], level=_HEAD_LEVEL[h[1].lower()]))
    if start:
        spans[start[0]] = (start[1], len(lines))
    d = {"id": id, "title": _title(m), "url": m["source_url"], "lines": lines,
         "entries": entries, "spans": spans}
    return _http.lru_put(_cache, id, d, 8)


class Haiti(Jurisdiction):
    code = "ht"
    name = "Haiti"
    languages = ("fr",)
    aliases = ("haiti", "haïti", "republic of haiti", "république d'haïti", "ayiti")
    sources = (
        Source(
            name="Conseil Supérieur du Pouvoir Judiciaire (CSPJ): document library",
            url=BASE + "/bibliotheque-de-documents/",
            covers=("legislation",),
            licence="unknown: no terms page; footer 'Droit d'auteur © 2026 Conseil Supérieur du "
                    "Pouvoir Judiciaire'. Haitian laws are official texts.",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~40 requests (2026-11)",
            terms_url=BASE + "/",
            warning=("Small selection (~17 laws on justice, family, foreigners, corruption, "
                     "trafficking, free zones; no nationality law) uploaded by the CSPJ, as published, not consolidated; "
                     "check Le Moniteur for amendments."),
        ),
        Source(
            name="Cour de cassation d'Haïti: Constitution PDF (1987 original)",
            url=CC_BASE + "/publication/",
            covers=("legislation",),
            licence="unknown: no terms page; no robots.txt (404). The Constitution is an official text.",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~4 requests (2026-11-10)",
            terms_url=CC_BASE + "/",
            warning="Constitution text is the 1987 original; the 2011 amended PDF on the same page is a scan.",
        ),
    )
    min_interval = {HOST: 1.0, "www.courdecassation.ht": 1.0}
    notes = ("Legislation only, and only a small set: ~17 laws and decree-laws (French) from the "
             "judiciary council's (CSPJ) library, text from the PDFs where they have a text layer. "
             "No case law online.")
    gaps = (
        "Most Haitian legislation (only ~17 laws are in the CSPJ library): Le Moniteur has no live site; Parliament TLS broken",
        "6 of the ~17 laws: scans only, no text (no OCR)",
        "Constitution: only the 1987 original is readable (court site); the 2011 amended PDF is a scan",
        "Case law (Cour de cassation): not published online (its database is empty, 2026-11)",
    )
    samples = {"legislation_query": "loi", "law_id": "1396", "provision": "5"}

    async def search_legislation(self, query, *, limit, page, filters):
        words = _fold(_http.clean(query)).split()
        if not words:
            raise BadRequest("Give words from the title, in French, e.g. 'corruption' or 'loi adoption'.")
        limit = max(1, min(int(limit), MAX_LIMIT))
        hits = [m for m in await _library() if all(w in _fold(_title(m)) for w in words)]
        if all(w in _fold(CONST_TITLE) for w in words):
            hits.insert(0, {"id": CONST_ID, "title": {"rendered": CONST_TITLE},
                            "source_url": CC_BASE + "/publication/", "media_details": {}})
        start = (max(1, int(page)) - 1) * limit
        return Results(items=[_hit(m) for m in hits[start:start + limit]], total=len(hits),
                       note="Title search over the CSPJ's small law library (~17 texts), not a "
                            "full legislation database. The Civil Code, Penal Code, other codes and the "
                            "nationality law are NOT in it: look for them elsewhere.")

    async def get_legislation_toc(self, id):
        d = await _doc(id)
        return Toc(id=id, title=d["title"], url=d["url"], entries=d["entries"])

    async def get_legislation_provision(self, id, provision):
        d = await _doc(id)
        lab = norm_provision(provision)
        if lab not in d["spans"]:
            raise NotFound(f"No article {provision!r} in {id}. Labels look like '5', '5.1', '1 (2)'; "
                           "see get_legislation_toc.")
        a, b = d["spans"][lab]
        return Provision(law_id=id, law_title=d["title"], provision=lab,
                         text=_paras(d["lines"][a:b]), url=d["url"])

    async def get_legislation_text(self, id):
        d = await _doc(id)
        return LawText(id=id, title=d["title"], text=_paras(d["lines"]), url=d["url"])
