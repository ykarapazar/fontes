"""Argentina: national legislation from InfoLEG on argentina.gob.ar/normativa ("Leyes Argentinas").

No case law: every official route found is closed to us (see `notes`).
SAIJ (saij.gob.ar) was dropped on 2026-11-05: its Reglamento de uso (Res. MJyDH 1427/2011)
forbids "intentar obtener los contenidos del sitio web por cualquier otro medio distinto de
los que se pongan a disposición de los Usuarios" (cl. 3 d) and deep linking (cl. 3 b), and
allows downloads only for personal use (cl. 2 b). CSJN's sentencias (sj.csjn.gov.ar) are
behind reCAPTCHA; datos.csjn.gov.ar holds no judgments and its /api/ is robots-disallowed.

Search (added 2026-11-10) goes to InfoLEG's own legacy search on servicios.infoleg.gob.ar
(buscarNormas.do): a plain GET with the form fields as query parameters, no captcha, no honeypot,
no robots.txt (404). It is full-text with stemming over every national norm, newest first, 50 per
page (`desplazamiento=AP&irAPagina=N`), quoted phrases supported. Hits carry the InfoLEG id, which
is the same id argentina.gob.ar uses, so we link to argentina.gob.ar, not infoleg.gob.ar.
infoleg.gob.ar's footer licenses content CC BY 2.5 AR, but its older "Aviso legal" (?page_id=762)
says linking to the site and putting its data in databases need written permission: we only query
live, store nothing, and link to argentina.gob.ar (CC BY 4.0, same Ministry, same data).

Gotchas this code encodes (verified 2026-11-05):
  * argentina.gob.ar terms: content licensed CC BY 4.0, nothing on automated access.
    robots.txt: Crawl-delay 10; /buscar, /search and /sites/default/files/infoleg/ are
    disallowed. The norm search is a POST form with a honeypot (and Turnstile on the
    advanced form) and has no GET URL, so we do not use it. search_legislation only
    filters the site's own GET index pages (national codes + national constitution).
  * A norm is addressed by its InfoLEG id: /normativa/nacional/norma-<id> (summary),
    /actualizacion (consolidated text, HTTP 500 when the norm has none), /texto (original).
    Human URLs add a slug: /normativa/nacional/ley-26994-235975.
  * Metadata comes as schema.org JSON-LD (legislationIdentifier, name, dates).
  * Text is InfoLEG's legacy HTML inside div.infoleg-norma-body: articles start with
    "ARTICULO N°.-" / "ARTICULO N° —", headings are centred divs ("CAPITULO 1<br><br>Derecho"
    -> two lines, merged here), amendment notes "(Artículo sustituido por ...)" follow the
    article. Codes approved by a law sit in "ANEXO I": like cl.py, the largest group keeps
    plain labels ("Artículo 1"); the law's own articles become "Artículo 1 (de la ley)",
    other annexes "Artículo 1 (anexo II)". A thematic index table precedes some texts.
"""
from __future__ import annotations

import datetime
import json
import re
import unicodedata

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import LawHit, LawText, Provision, Results, Toc, TocEntry

HOST = "https://www.argentina.gob.ar"
NORMA = f"{HOST}/normativa/nacional/norma-"
SEARCH = "https://servicios.infoleg.gob.ar/infolegInternet/buscarNormas.do"
TYPES = {"ley": "1", "decreto_ley": "7", "decreto": "2", "any": ""}   # InfoLEG tipoNorma codes
_ES_MONTHS = {m: i for i, m in enumerate(("ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct",
                                           "nov", "dic"), 1)}
INDEX_PAGES = (f"{HOST}/normativa/codigos/nacionales", f"{HOST}/normativa/constituciones/nacional")

_STOP = {"de", "y", "el", "la", "las", "lo", "los", "del", "a", "en", "e", "o", "nacion", "republica"}
_SUFFIX = r"bis|ter|quater|quinquies|sexies|septies|octies|novies|decies"
_ART = re.compile(rf"^\s*(?:ART[IÍ]CULO|Art[ií]culo|ART\.|Art\.)\s*(\d+)\s*(?:[°º]|o\.)?\s*({_SUFFIX})?\b\s*(.*)$",
                  re.S)
_HEAD = re.compile(r"^(LIBRO|T[IÍ]TULO|CAP[IÍ]TULO|SECCI[OÓ]N|PAR[AÁ]GRAFO|PARTE|ANEXO|DISPOSICIONES)\b", re.I)
_ANNEX = re.compile(r"^ANEXO\s+([IVXLC]+|\d+|[A-Z])\b", re.I)
_SLUG = re.compile(r"^([a-z_]+)-([0-9a-z-]+)-(\d+)$")
_YEARS = re.compile(r"^(\d{4})(?:\s*[-–:]\s*(\d{4})?)?$")
_CONSTITUTION = "804"   # InfoLEG id of the Constitución Nacional (the index page entry)
_LAWNO = re.compile(r"^(ley|decreto|decreto_ley)[\s-]*(?:n[º°.o]*\s*)?(\d[\d.]*)$", re.I)

# Common names whose InfoLEG title differs (Ley 25326 is titled 'HABEAS DATA - REGIMEN LEGAL').
_ALIASES = {"proteccion datos personales": "25326"}

_laws: dict[str, dict] = {}
_index: list[LawHit] = []


def _fold(s: str) -> str:
    return unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()


def _plain(p: str) -> str:
    """Markdown paragraph -> plain text for pattern matching (bold/italics dropped)."""
    return _http.clean(re.sub(r"[*_]+", "", p))


def _key(label: str) -> str:
    """'Art. 1716º' == 'artículo 1716' == '1716'; '700 bis' kept."""
    s = _fold(re.sub(r"[º°ª]", " ", label or ""))  # before folding: NFKD turns º into 'o'
    s = re.sub(r"(?<=\d)\.(?=\d{3}(?!\d))", "", s)  # Spanish thousands separator: 1.716 == 1716
    s = s.replace(".", " ")
    s = re.sub(r"^\s*(articulos?|arts?)\b", "", s)
    return re.sub(r"\s+", " ", s).strip()


# --------------------------------------------------------------------------- #
# Ids and the GET index pages
# --------------------------------------------------------------------------- #
def _hit(href: str, title: str) -> LawHit | None:
    m = _SLUG.match(href.rstrip("/").rsplit("/", 1)[-1])
    if not m:
        return None
    return LawHit(id=m[3], title=_http.clean(title), type=m[1].replace("_", " ").capitalize(),
                  number=m[2].replace("-", "/"), url=f"{HOST}/normativa/nacional/{m[0]}")


async def _load_index() -> list[LawHit]:
    if _index:
        return _index
    hits: dict[str, LawHit] = {}
    for url in INDEX_PAGES:
        r = await _http.get(url)
        if r.status_code != 200:
            raise SourceError(f"argentina.gob.ar index page {url} failed", r.status_code)
        for href, title in re.findall(r'href="(/normativa/nacional/[^"#?]+)"[^>]*>([^<]+)</a>', r.text):
            h = _hit(href, title)
            if h and h.id not in hits:
                hits[h.id] = h
    _index[:] = hits.values()
    return _index


def _es_date(s: str) -> str:
    """'09-mar-2026' -> '2026-03-09'."""
    m = re.fullmatch(r"(\d{1,2})-([a-z]{3})-(\d{4})", _fold(s).strip())
    return f"{m[3]}-{_ES_MONTHS[m[2]]:02d}-{int(m[1]):02d}" if m and m[2] in _ES_MONTHS else ""


async def _infoleg(params: dict, page: int = 1) -> tuple[list[LawHit], int]:
    """One page (50 rows) of InfoLEG's search -> (hits, total)."""
    q = dict(params)
    if page > 1:
        q.update(desplazamiento="AP", irAPagina=str(page))
    r = await _http.get(SEARCH, params=q)
    if r.status_code != 200 or "busquedaNormasForm" not in r.text:
        raise SourceError("InfoLEG search failed", r.status_code)
    html = re.sub(r"(?is)<script\b.*?</script>", "", r.text)
    m = re.search(r"Cantidad de Normas Encontradas:\s*(?:<[^>]+>\s*)*([\d.]+)", html)
    total = int(m[1].replace(".", "")) if m else 0
    hits = []
    for row in re.findall(r'(?s)<td valign="top" class="vr_azul11">(.*?)</tr>', html):
        a = re.search(r'verNorma\.do[^"]*\?id=(\d+)"[^>]*>(.*?)</a>(.*?)<br', row, re.S)
        if not a:
            continue
        name = _http.clean(re.sub(r"<[^>]+>", " ", a[2]))
        typ, _, num = name.partition(" ")
        date = re.search(r"verBoletin\.do[^>]*>([^<]+)</a>", row)
        tit = re.search(r"<b>(.*?)</b>(.*?)(?:<span[^>]*>(.*?)</span>|</td>)", row, re.S)
        title = " – ".join(x for x in (_http.clean(re.sub(r"<[^>]+>", " ", t)) for t in
                                        ((tit[1], tit[2]) if tit else ())) if x)
        hits.append(LawHit(id=a[1], title=f"{name} – {title}" if title else name, type=typ,
                           number=num.replace(" ", ""), date=_es_date(date[1]) if date else "",
                           snippet=_http.clean(re.sub(r"<[^>]+>", " ", tit[3] or "")) if tit else "",
                           url=f"{NORMA}{a[1]}"))
    return hits, total


async def _norm_id(id: str) -> str:
    s = (id or "").strip()
    if re.fullmatch(r"\d+", s):
        return s
    if _fold(s).strip("/ ") in ("constitucion", "constitucion nacional", "constituciones/nacional",
                                "constitucion de la nacion argentina"):
        return _CONSTITUTION
    m = (re.search(r"norma-(\d+)", s) or re.search(r"/normativa/nacional/[a-z_]+-[0-9a-z-]+-(\d+)(?:[/?#]|$)", s)
         or _SLUG.match(s))
    if m:
        return m[m.lastindex]
    m = _LAWNO.match(s)
    if m:
        no = m[2].replace(".", "")
        hits, _ = await _infoleg({"tipoNorma": TYPES[m[1].lower()], "numero": no})
        ids = {h.id for h in hits if h.number.split("/")[0] == no}
        if len(ids) == 1:
            return ids.pop()
        if not ids:
            raise NotFound(f"InfoLEG has no {m[1]} number {no}.")
        raise BadRequest(f"{s!r} matches several norms (InfoLEG ids {', '.join(sorted(ids))}); give the InfoLEG id.")
    raise BadRequest(f"Argentine norm ids are InfoLEG ids ('235975'), a slug ('ley-26994-235975'), an "
                     f"argentina.gob.ar/normativa URL, or 'ley 26994' for a national code; got {id!r}.")


def _window(y0: int, y1: int) -> dict:
    """InfoLEG's publication-date range 1 Jan y0 .. 31 Dec y1. It returns nothing when the end date is
    today or later, so the end is held at yesterday."""
    end = min(datetime.date(y1, 12, 31), datetime.date.today() - datetime.timedelta(days=1))
    return {"diaPubDesde": "1", "mesPubDesde": "1", "anioPubDesde": str(y0),
            "diaPubHasta": str(end.day), "mesPubHasta": str(end.month), "anioPubHasta": str(end.year)}


async def _slice(params: dict, start: int, limit: int) -> tuple[list[LawHit], int]:
    """Rows [start, start+limit) of InfoLEG's 50-row pages."""
    sp = start // 50 + 1
    hits, total = await _infoleg(params, sp)
    if start % 50 + limit > 50 and sp * 50 < total:
        hits += (await _infoleg(params, sp + 1))[0]
    return hits[start % 50: start % 50 + limit], total


async def _by_year(params: dict, y0: int, y1: int, start: int, limit: int) -> tuple[list[LawHit], int]:
    """A year range as one query per year, newest year first (InfoLEG answers some wide ranges with 0)."""
    items, total, off = [], 0, start
    for y in range(y1, y0 - 1, -1):
        p = {**params, **_window(y, y)}
        first, t = await _infoleg(p, 1)
        total += t
        need = limit - len(items)
        if need > 0 and off < t:
            rows = first[off:off + need] if off + need <= 50 else (await _slice(p, off, need))[0]
            items += rows
        off = max(0, off - t)
    return items, total


# --------------------------------------------------------------------------- #
# Parsing a norm page
# --------------------------------------------------------------------------- #
def _lines(body: str) -> list[str]:
    """Body HTML -> paragraphs, split on hard breaks, index tables dropped."""
    out = []
    for p in _http.html_paragraphs(body):
        if p.startswith("|"):
            continue
        out += [x.strip() for x in p.split("  \n") if x.strip()]
    if any(_plain(x) == "INDICE TEMATICO" for x in out[:5]):   # skip the thematic index
        i = next(k for k, x in enumerate(out) if _plain(x) == "INDICE TEMATICO") + 1
        while i < len(out) and re.fullmatch(r"\*\*[^*]+\*\*", out[i]):
            i += 1
        out = out[i:]
    return out


def _parse(nid: str, html: str, consolidated: bool) -> dict:
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    try:
        ld = json.loads(m[1]) if m else {}
    except ValueError:
        ld = {}
    i = html.find("infoleg-norma-body")
    if i < 0:
        raise SourceError("argentina.gob.ar: page has no norm text (layout changed?)")
    j = html.find("</article>", i)
    body = html[html.index(">", i) + 1: j if j > 0 else len(html)]
    body = re.sub(r"(?is)<details\b.*?</details>", "", body)   # "Antecedentes normativos"

    items: list[list] = []       # ["h", text] | ["t", text] | ["a", group, num, [paras]]
    group, pending = "", None
    for line in _lines(body):
        pl = _plain(line)
        if not re.search(r"\w", pl):
            continue
        a = _ART.match(pl)
        if a:
            items.append(["a", group, a[1] + (f" {a[2].lower()}" if a[2] else ""), [line]])
            pending = None
            continue
        numbered = _HEAD.match(pl) and re.search(r"\d|\b[IVXLC]+\b", pl)
        if pending is not None and not numbered and len(pl) < 120 and not pl.startswith("("):
            pending[1] += f" – {pl}"
            pending = None
            continue
        if _HEAD.match(pl) and len(pl) < 160:
            an = _ANNEX.match(pl)
            if an:
                group = an[1].upper()
            items.append(["h", pl])
            # "CAPITULO 1" alone: the next short line is its title
            pending = items[-1] if re.fullmatch(r"\S+\s+\S+", pl) and not an else None
            continue
        pending = None
        if items and items[-1][0] == "a":
            items[-1][3].append(line)
        else:
            items.append(["t", line])

    # Labels: the biggest group keeps "Artículo N"; others get a suffix.
    counts: dict[str, int] = {}
    for it in items:
        if it[0] == "a":
            counts[it[1]] = counts.get(it[1], 0) + 1
    main = max(counts, key=counts.get) if counts else ""
    own = {"Ley": "de la ley", "Decreto": "del decreto"}.get(ld.get("legislationType"), "de la norma")
    labels, lookup = {}, {}
    for k, it in enumerate(items):
        if it[0] != "a":
            continue
        lab = f"Artículo {it[2]}"
        if it[1] != main:
            lab += f" ({own})" if it[1] == "" else f" (anexo {it[1]})"
        base, n = lab, 2
        while _key(lab) in lookup:
            lab, n = f"{base} ({n})", n + 1
        labels[k] = lab
        lookup[_key(lab)] = k
    title = " – ".join(x for x in (_http.clean(ld.get("legislationIdentifier")), _http.clean(ld.get("name"))) if x)
    return {"id": nid, "title": title or f"InfoLEG norma {nid}", "ld": ld, "items": items, "labels": labels,
            "lookup": lookup, "consolidated": consolidated,
            "url": f"{NORMA}{nid}/" + ("actualizacion" if consolidated else "texto"),
            "as_of": _http.today() if consolidated else _http.iso_date(ld.get("datePublished"))}


def _art_heading(first: str) -> str:
    """'ARTICULO 1716.- Deber de reparar. La violación…' -> 'Deber de reparar'."""
    m = re.match(r"(?i)art[ií]culo\s+\d+\s*[°º]?\s*(?:" + _SUFFIX + r")?\s*\.\s*-\s*([^.:]{2,90})\.", _plain(first))
    return m[1].strip() if m else ""


# --------------------------------------------------------------------------- #
# Adapter
# --------------------------------------------------------------------------- #
class Argentina(Jurisdiction):
    code = "ar"
    name = "Argentina"
    languages = ("es",)
    aliases = ("argentina", "arg")
    sources = (
        Source(
            name="InfoLEG – search (servicios.infoleg.gob.ar, Ministerio de Justicia)",
            url="https://servicios.infoleg.gob.ar/infolegInternet/",
            covers=("legislation",),
            licence="Creative Commons Reconocimiento 2.5 Argentina (infoleg.gob.ar footer)",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; no robots.txt (404); 2 s spacing, no 429 seen in ~10 requests (2026-11)",
            terms_url="https://www.infoleg.gob.ar/?page_id=762",
            warning=("Search results come from InfoLEG, whose Aviso legal asks for written permission to link to "
                     "infoleg.gob.ar or put its data in databases; Fontes queries it live, stores nothing and "
                     "links to argentina.gob.ar."),
        ),
        Source(
            name="InfoLEG – Leyes Argentinas (Ministerio de Justicia, argentina.gob.ar/normativa)",
            url="https://www.argentina.gob.ar/normativa",
            covers=("legislation",),
            licence="Creative Commons Attribution 4.0 International (argentina.gob.ar Términos y condiciones)",
            commercial_use=True,
            ai_use=None,
            auth="none",
            rate_limit="robots.txt Crawl-delay: 10 (checked 2026-11-05); 10 s spacing",
            terms_url="https://www.argentina.gob.ar/terminos-y-condiciones",
            warning=("CC BY 4.0: credit 'InfoLEG – Ministerio de Justicia de la Nación' when reusing. "
                     "Consolidated texts are not official; only the Boletín Oficial is authentic."),
        ),
    )
    legislation_filters = {
        "type": "ley (default), decreto_ley, decreto (incl. DNU) or any (every national norm, incl. resolutions)",
        "year": ("year of publication in the Boletín Oficial, e.g. '2012', or a range '2022-2026' or '2022-' "
                 "(to this year); InfoLEG's sanction-year field returns nothing, so this is the publication year"),
    }
    min_interval = {"www.argentina.gob.ar": 10.0, "servicios.infoleg.gob.ar": 2.0}
    notes = ("National legislation (consolidated where InfoLEG has it, per article) from argentina.gob.ar. "
             "Search is InfoLEG's full-text search over every national norm (laws by default; newest first; "
             "national codes and the constitution listed first on page 1). No case law: SAIJ's terms forbid "
             "non-interface access and CSJN's search is behind reCAPTCHA.")
    gaps = (
        ("Case law, all courts via SAIJ: terms forbid obtaining content 'por cualquier otro medio'"
         " than the interface"),
        ("Supreme Court (CSJN) judgments: sj.csjn.gov.ar is behind reCAPTCHA; datos.csjn.gov.ar "
         "has no judgments"),
        ("Buenos Aires Supreme Court (JUBA): official, reachable, provincial only; source exists "
         "but not built yet"),
        ("Consolidated text: InfoLEG has it only for norms it keeps updated; others come as the original text "
         "(a norm with no text online raises NotFound)"),
        ("Provincial legislation: SAIJ terms forbid automated use; provincial official sites not "
         "researched yet"),
    )
    samples = {
        "legislation_query": "código civil",
        "law_id": "235975",
        "provision": "Artículo 1716",
    }

    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        typ = (filters.get("type") or "ley").lower().replace("-", "_").replace(" ", "_")
        if typ not in TYPES:
            raise BadRequest(f"type must be one of {', '.join(TYPES)}; got {typ!r}.")
        params = {"tipoNorma": TYPES[typ]}
        years = None
        if filters.get("year"):
            ym = _YEARS.match(str(filters["year"]).strip())
            if not ym:
                raise BadRequest("year must be four digits, e.g. '2012', or a range such as '2022-2026' or '2022-'.")
            y0 = int(ym[1])
            y1 = int(ym[2]) if ym[2] else (datetime.date.today().year if re.search(r"[-–:]", filters["year"]) else y0)
            years = (y0, y1)
            if years[0] > years[1]:
                raise BadRequest(f"year range {filters['year']!r} ends before it starts.")
            params.update(_window(*years))
        q = (query or "").strip()
        m = _LAWNO.match(q)
        if m:
            params.update(tipoNorma=TYPES[m[1].lower()], numero=m[2].replace(".", ""))
        elif re.fullmatch(r"\d[\d.]*", q):
            params["numero"] = q.replace(".", "")
        elif q:
            params["texto"] = q
        phrase = bool(q) and "texto" in params and '"' not in q and len(q.split()) > 1
        if phrase:   # a bare multi-word query ORs the words (72,000 decrees); try the exact phrase first
            # 'Ley de Sociedades Comerciales': the law's own text never says 'Ley de ...', so quote the name only
            params["texto"] = f'"{re.sub(r"(?i)^ley(?: de)? ", "", q) if len(q.split()) > 3 else q}"'
        if len(params) == 1 and not params["tipoNorma"] and not q:
            raise BadRequest("Give search words, e.g. 'identidad de género', 'ley 26994' or a filter.")
        # InfoLEG pages by 50; take the rows [start, start+limit) from one or two of its pages.
        start = (page - 1) * limit
        note = ("InfoLEG full-text search, newest first (not ranked by relevance); quote a phrase for exact matches. "
                "Dates shown are Boletín Oficial publication dates, not sanction dates "
                "(the search list has no sanction date; get_legislation_text shows it as 'Sanción').")

        async def run():
            if years and years[0] != years[1]:
                rows, tot = await _slice(params, start, limit)
                if not tot and years[1] - years[0] < 10:
                    return await _by_year(params, *years, start, limit)
                return rows, tot
            return await _slice(params, start, limit)
        items, total = await run()
        if phrase and not total:
            params["texto"] = q
            items, total = await run()
            note += f" No norm contains the exact phrase {q!r}; these match its words separately."
        elif phrase:
            note += f" Matched as the exact phrase {q!r}."
        if page == 1 and not m and typ in ("ley", "any") and not filters.get("year"):
            # The national codes and the constitution, matched on their titles, go first.
            words = [w[:5] for w in re.split(r"\W+", _fold(q)) if w and w not in _STOP]   # 'nacional' ~ 'Nación'
            idx = [h for h in await _load_index() if words and all(w in _fold(f"{h.title} {h.type} {h.number}")
                                                                      for w in words)]
            if words and total > len(items) and typ in ("ley", "any") and "numero" not in params:
                # newest-first order buries a law named in the query: lift rows whose title has all its words
                more = []   # all of page 1, not just its first `limit` rows
                for pg in range(1, min(5, (total + 49) // 50) + 1):
                    more += (await _infoleg(params, pg))[0]
                ph = " ".join(w for w in re.split(r"\W+", _fold(q)) if w)
                bare = re.sub(r"^ley(?: de)? ", "", ph)   # 'ley de sociedades comerciales' -> the title 'SOCIEDADES COMERCIALES - ...'

                def tier(h):   # 0: title is 'LEY DE <phrase>'; 1: starts with it; 2: every word in it; 3: other
                    t = " ".join(w for w in re.split(r"\W+", _fold(h.title.partition(" – ")[2] or h.title)) if w)
                    return 0 if t.startswith(f"ley de {bare}") else 1 if t.startswith(bare) else \
                        2 if all(w in _fold(h.title) for w in words) else 3
                # within a tier the law itself before the laws that merely modify it
                def amends(h):   # 'LEY Nº 19500 - INTRODUCENSE REFORMAS', 'LEY 20744 - MODIFICACION'
                    t = _fold(h.title.partition(" – ")[2] or h.title)
                    return bool(re.search(r"modific|reform|\bley\b.*\d", t))
                # then the one whose subtitle says 'REGIMEN' (the code itself: 'NUEVO REGIMEN', 'REGIMEN LEGAL')
                items = sorted(more, key=lambda h: (tier(h), amends(h), "regimen" not in _fold(h.title)))[:limit]
            alias = _ALIASES.get(" ".join(w for w in re.split(r"\W+", _fold(q)) if w and w not in ("de", "la", "el", "los", "las", "del")))
            if alias:
                named = (await _infoleg({"tipoNorma": TYPES["ley"], "numero": alias}))[0]
                items = named + [h for h in items if h.id not in {n.id for n in named}]
                note += " Ley 25326 is titled 'HABEAS DATA - REGIMEN LEGAL' in InfoLEG."
            seen = {h.id for h in idx}
            items = (idx + [h for h in items if h.id not in seen])[:limit]
        return Results(items=items, total=total, note=note)

    async def _law(self, id) -> dict:
        nid = await _norm_id(id)
        if nid in _laws:
            return _laws[nid]
        r = await _http.get(f"{NORMA}{nid}/actualizacion")
        consolidated = r.status_code == 200 and "infoleg-norma-body" in r.text
        if not consolidated:
            if r.status_code not in (200, 404, 500):
                raise SourceError("argentina.gob.ar: norm page failed", r.status_code)
            r = await _http.get(f"{NORMA}{nid}/texto")
            if r.status_code in (404, 500) or (r.status_code == 200 and "infoleg-norma-body" not in r.text):
                raise NotFound(f"No InfoLEG norm with id {nid} (or it has no text online).")
            if r.status_code != 200:
                raise SourceError("argentina.gob.ar: norm page failed", r.status_code)
        return _http.lru_put(_laws, nid, _parse(nid, r.text, consolidated), 4)

    async def get_legislation_toc(self, id):
        law = await self._law(id)
        entries = []
        for k, it in enumerate(law["items"]):
            if it[0] == "h":
                entries.append(TocEntry(title=it[1], level=0))
            elif it[0] == "a":
                lab = law["labels"][k]
                head = _art_heading(it[3][0])
                entries.append(TocEntry(title=lab + (f" – {head}" if head else ""), level=1, provision=lab))
        return Toc(id=law["id"], title=law["title"], url=law["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        law = await self._law(id)
        k = law["lookup"].get(_key(provision))
        if k is None:
            raise NotFound(f"{law['title']}: no article {provision!r}. Use labels from get_legislation_toc, "
                           "e.g. 'Artículo 1716', '700 bis', 'Artículo 1 (de la ley)'.")
        lab = law["labels"][k]
        text = "\n\n".join([f"## {lab}"] + law["items"][k][3])
        return Provision(law_id=law["id"], law_title=law["title"], provision=lab, text=text,
                         url=law["url"], as_of=law["as_of"])

    async def get_legislation_text(self, id):
        law = await self._law(id)
        out = []
        for k, it in enumerate(law["items"]):
            if it[0] == "h":
                out.append(f"## {it[1]}")
            elif it[0] == "t":
                out.append(it[1])
            else:
                out.append(f"### {law['labels'][k]}")
                out += it[3]
        ld = law["ld"]
        md = {k: _http.clean(v) for k, v in (
            ("Norma", ld.get("legislationIdentifier")), ("Tipo", ld.get("legislationType")),
            ("Organismo", (ld.get("legislationPassedBy") or {}).get("name")),
            ("Sanción", ld.get("legislationDate")), ("Publicación (Boletín Oficial)", ld.get("datePublished")),
            ("Texto", "actualizado (InfoLEG)" if law["consolidated"] else "original (sin texto actualizado)"),
            ("Id InfoLEG", law["id"])) if v}
        return LawText(id=law["id"], title=law["title"], text="\n\n".join(out), url=law["url"],
                       as_of=law["as_of"], metadata=md)
