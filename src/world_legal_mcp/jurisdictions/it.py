"""Italy: national legislation from Normattiva (Istituto Poligrafico e Zecca dello Stato for the
Presidenza del Consiglio dei Ministri). Search via the Normattiva open-data API; texts from
www.normattiva.it by URN:NIR. No case law (see `notes`).

Gotchas this code encodes (verified 2026-11-05 from a UK IP):
  * Search is the open-data API (api.normattiva.it/.../bff-opendata/v1/api/v1/ricerca/avanzata,
    keyless JSON POST). Title/text words are OR-ed and results come sorted by date, never by
    relevance ("codice civile" -> 2,532 hits, newest first). Quotes and AND are not supported
    ("codice AND civile" returns an empty body). Number + year filters are exact, so a query
    like "r.d. 262/1942" or "legge 241/1990" is parsed into number/year/type filters.
  * The open-data API has no text endpoint (only search + bulk collections), so texts come
    from www.normattiva.it/uri-res/N2Ls?<urn>. The resolver is lenient: it accepts
    urn:nir:stato:<denominazione dotted lower-case>:<date>;<number> for every act type
    (even ministerial "decreto"), which is how ids are built from search hits. An unknown
    URN gives an HTML page titled "Normattiva - Errore" with HTTP 200.
  * The act page embeds the whole article tree (2.6 MB / 6-12 s for the Codice civile).
    `~artN` selects one article, but only for the right annex: the Codice civile is annex 2
    of R.D. 262/1942 (`;262:2~art2043`); the preleggi are annex 1. An unknown article
    silently returns the act's first article, so the returned heading is checked.
  * Tree links carry art.flagTipoArticolo = annex number (0 = the act's own articles) and
    idSottoArticolo (1 = plain, 2 = bis, 3 = ter...). We label the biggest annex's articles
    "art. N" and the others "art. N (atto)" / "art. N (all. K)".
  * The AJAX article endpoint and the whole-act export (/esporta/attoCompleto) are bound to
    the server session: they return the error page unless the same act was just opened with
    the same cookies. get_legislation_text opens the act and exports it under one lock.
  * Texts are the version in force today ("vigente"); the site says they are not official,
    the Gazzetta Ufficiale is.
"""
from __future__ import annotations

import asyncio
import re
import unicodedata

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import LawHit, LawText, Provision, Results, Toc, TocEntry

API = "https://api.normattiva.it/t/normattiva.api/bff-opendata/v1/api/v1"
SITE = "https://www.normattiva.it"

_URN_RE = re.compile(r"^urn:nir:[a-z.]+:[a-z.]+:\d{4}-\d{2}-\d{2}(;[0-9a-z.-]+)?$")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# "262/1942", "n. 262 del 1942", "n.262 1942"
_NUM_YEAR_RE = re.compile(r"(?<![\d/])\b(?:n\.?\s*)?(\d+)\s*(?:/|del|\s)\s*((?:18|19|20)\d{2})\b", re.I)
# "91/92", "n. 241 del 90": a citation with a 2-digit year. Not a date ("12/03/20", "del 12 marzo"),
# a season ("2023/24") or an article reference ("art. 3/12").
_SHORT_YEAR_RE = re.compile(
    r"(?<![/\d])(?<!art\. )(?<!art )(?!(?:18|19|20)\d{2}\b)(\d{1,4})\s*(?:/\s*|\bdel\s+)(\d{2})"
    r"(?![\d/]|\s*(?:gen|feb|mar|apr|mag|giu|lug|ago|set|ott|nov|dic)[^\W\d_]*)", re.I)
_ABBREV = {  # common citation abbreviations -> denominazioneAtto
    "l": "LEGGE", "legge": "LEGGE", "l. cost": "LEGGE COSTITUZIONALE",
    "legge costituzionale": "LEGGE COSTITUZIONALE",
    "d.lgs": "DECRETO LEGISLATIVO", "dlgs": "DECRETO LEGISLATIVO", "d. lgs": "DECRETO LEGISLATIVO",
    "decreto legislativo": "DECRETO LEGISLATIVO",
    "d.l": "DECRETO-LEGGE", "dl": "DECRETO-LEGGE", "decreto-legge": "DECRETO-LEGGE",
    "decreto legge": "DECRETO-LEGGE",
    "d.p.r": "DECRETO DEL PRESIDENTE DELLA REPUBBLICA", "dpr": "DECRETO DEL PRESIDENTE DELLA REPUBBLICA",
    "d.p.c.m": "DECRETO DEL PRESIDENTE DEL CONSIGLIO DEI MINISTRI",
    "dpcm": "DECRETO DEL PRESIDENTE DEL CONSIGLIO DEI MINISTRI",
    "r.d": "REGIO DECRETO", "rd": "REGIO DECRETO", "regio decreto": "REGIO DECRETO",
    "d.m": "DECRETO MINISTERIALE", "decreto": "DECRETO",
}
_TREE_TOKEN_RE = re.compile(
    r'<li class="box_(?:articoli|allegati|allegati_small)"><span>(?P<box>.*?)</span>'
    r'|data-target="#coll_\d+"[^>]*>(?P<head>.*?)</a></div><span class="snippets"><div[^>]*>'
    r'(?P<snip>.*?)</div>'
    r"|showArticle\('(?P<link>/atto/caricaArticolo\?[^']*)'[^>]*>(?P<text>[^<]*)</a>", re.S)

_page_cache: dict[str, dict] = {}
_session_lock = asyncio.Lock()


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _plain(html: str) -> str:
    return _http.clean(_http.html_to_md(html).replace("\n", " ")) if html else ""


def _heading(html: str) -> str:
    """TOC heading text: _plain minus bold '*' markers and the ((...)) amendment brackets."""
    return _http.clean(re.sub(r"\*+|\(\(|\)\)", "", _plain(html)))


def _slug(denominazione: str) -> str:
    """'DECRETO DEL PRESIDENTE DELLA REPUBBLICA' -> 'decreto.del.presidente.della.repubblica'."""
    s = unicodedata.normalize("NFKD", denominazione).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z]+", ".", s).strip(".")


def _urn(a: dict) -> str:
    date = str(a.get("dataEmanazione") or a.get("dataGU") or "")[:10]  # Costituzione: no dataEmanazione
    num = _http.clean(a.get("numeroAttoAlfanumerico") or a.get("numeroAtto") or "")
    urn = f"urn:nir:stato:{_slug(a.get('denominazioneAtto') or '')}:{date}"
    return f"{urn};{num.lower()}" if num and num != "0" else urn


def _url(urn: str) -> str:
    return f"{SITE}/uri-res/N2Ls?{urn}"


def _check_urn(id: str) -> str:
    urn = (id or "").strip().split("~")[0].lower()
    urn = re.sub(r"(;[0-9a-z.-]+):\d+$", r"\1", urn)  # drop an annex suffix (";262:2")
    if not _URN_RE.match(urn):
        raise BadRequest(f"{id!r} is not a URN:NIR. Use e.g. 'urn:nir:stato:legge:1990-08-07;241' "
                         "(L. 241/1990) or 'urn:nir:stato:regio.decreto:1942-03-16;262' "
                         "(Codice civile). Find ids with search_legislation.")
    return urn


def _norm(s: str) -> str:
    """Keep only digits and letters, plus a dot between digits: art. 9.1 is not art. 91."""
    s = re.sub(r"(\d)\.(\d)", r"\1_\2", s.lower())
    return re.sub(r"[^0-9a-z_]", "", s).replace("_", ".")


def _art_key(label: str) -> str:
    """'art. 768 bis' / 'Art. 768-bis' / '768bis' / 'articolo 12 (all. 1)' / 'art. 9.1'
    -> '768bis' / '12all1' / '9.1'."""
    s = label.lower().replace("allegato", "all").replace("articolo", "")
    return re.sub(r"^0+(?=\d)", "", _norm(re.sub(r"\bart\b\.?", "", s)))  # "009" == "9"


def _roman_int(s: str) -> int:
    vals = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100}
    n = 0
    for a, b in zip(s, s[1:] + " "):
        n += -vals[a] if vals.get(b, 0) > vals[a] else vals[a]
    return n


def _art_label(text: str) -> tuple[str, str]:
    """Tree link text '2 bis' / 'art. 768 bis' -> ('2 bis', '2bis')."""
    t = _http.clean(re.sub(r"(?i)^art\.?\s*", "", text))
    return t, _norm(t)


def _reset_session() -> None:
    jar = _http.get_client().cookies.jar
    for c in [c for c in jar if "normattiva" in c.domain]:
        jar.clear(c.domain, c.path, c.name)


async def _fetch_act(urn: str) -> str:
    r = await _http.get(_url(urn))
    if r.status_code != 200:
        raise SourceError(f"Normattiva returned HTTP {r.status_code} for {urn}", r.status_code)
    html = r.text
    if "<title>Normattiva - Errore" in html:
        raise NotFound(f"Normattiva has no act {urn}. Check the URN with search_legislation.")
    if 'id="albero"' not in html:
        raise SourceError(f"unexpected Normattiva page for {urn} (no article tree)", r.status_code)
    return html


def _body(html: str) -> str:
    i = html.find('<div class="bodyTesto">')
    if i < 0:
        return ""
    j = html.find('<div class="d-flex justify-content-between px-5', i)
    return html[i:j if j > 0 else None]


def _act_title(html: str) -> str:
    h2 = re.search(r'<div id="titoloAtto"[^>]*>\s*<h2[^>]*>(.*?)</h2', html, re.S)
    head = _heading(re.sub(r"(?s)<!--.*?-->", "", h2.group(1))) if h2 else ""
    h3 = re.search(r"</div>\s*<h3[^>]*>(.*?)</h3>", html[h2.end() if h2 else 0:], re.S)
    sub = re.sub(r"\s*\(\w{8,9}\)\s*$", "", _heading(h3.group(1))) if h3 else ""
    return f"{head} — {sub}" if head and sub else head or sub


def _parse_act(urn: str, html: str) -> dict:
    a = html.find('<div id="albero">')
    tree = html[a:html.find('class="bodyTesto"', a)]
    raw, section, n_by_annex = [], "", {}
    for m in _TREE_TOKEN_RE.finditer(tree):
        if m.group("box") is not None:
            box = _heading(m.group("box"))
            if box != "Allegati":
                section = box
                raw.append(("sec", box))
        elif m.group("head") is not None:
            lines = [_heading(x) for x in re.split(r"<br\s*/?>", m.group("snip"))]
            raw.append(("head", " — ".join(x for x in [_heading(m.group("head")), *lines] if x)))
        else:
            link, text = m.group("link"), m.group("text")
            if "imUpdate=true" in link:
                continue
            annex = int(re.search(r"flagTipoArticolo=(\d+)", link).group(1))
            shown, key = _art_label(text)
            n_by_annex[annex] = n_by_annex.get(annex, 0) + 1
            raw.append(("art", (annex, shown, key, section, link.replace("&amp;", "&"))))
    if not n_by_annex:
        raise SourceError(f"no articles found in the Normattiva tree for {urn}")
    primary = max(n_by_annex, key=lambda k: (n_by_annex[k], k))
    entries, arts = [], {}
    for kind, v in raw:
        if kind == "sec":
            entries.append(TocEntry(title=v, level=0))
        elif kind == "head":
            entries.append(TocEntry(title=v, level=1))
        else:
            annex, shown, key, sec, link = v
            qual = "" if annex == primary else " (atto)" if annex == 0 else f" (all. {annex})"
            label = f"art. {shown}{qual}"
            full = _art_key(label)
            if full in arts:
                continue
            arts[full] = (annex, key, label, link)
            entries.append(TocEntry(title=label, level=2, provision=label))
    export = re.search(r"esporta/attoCompleto\?([^\"']*)", html)
    return {"title": _act_title(html) or urn, "entries": entries, "arts": arts,
            "export": export.group(1).replace("&amp;", "&") if export else ""}


async def _act(urn: str) -> dict:
    if urn not in _page_cache:
        _http.lru_put(_page_cache, urn, _parse_act(urn, await _fetch_act(urn)), 8)
    return _page_cache[urn]


def _law_hit(a: dict) -> LawHit:
    title = _http.clean(str(a.get("titoloAtto") or "").strip("[] "))
    title = re.sub(r"\s*\(\w{8,9}\)\s*$", "", title)
    desc = _http.clean(a.get("descrizioneAtto"))
    urn = _urn(a)
    return LawHit(id=urn, title=f"{desc} — {title}" if desc and title else desc or title or urn,
                  type=_http.clean(a.get("denominazioneAtto")),
                  number=_http.clean(a.get("numeroAttoAlfanumerico") or a.get("numeroAtto")),
                  date=str(a.get("dataEmanazione") or a.get("dataGU") or "")[:10],
                  snippet=f"GU n. {_http.clean(a.get('numeroGU'))} del {a.get('dataGUStr', '')}".strip(),
                  url=_url(urn))


def _parse_query(query: str) -> dict:
    """Pull 'type number/year' citations out of a free-text query."""
    q, body = _http.clean(query), {}
    if q.lower().rstrip(".") in ("costituzione", "cost", "costituzione della repubblica italiana",
                                 "constitution"):
        return {"denominazioneAtto": "COSTITUZIONE"}
    m = _NUM_YEAR_RE.search(q)
    if not m and (sm := _SHORT_YEAR_RE.search(q)):
        raise BadRequest(f"year must be 4 digits (e.g. 1992) in citation {sm.group(0)!r}.")
    if m:
        body["numeroProvvedimento"], body["annoProvvedimento"] = m.group(1), m.group(2)
        rest = _http.clean(q[:m.start()] + " " + q[m.end():]).lower().rstrip(".,")
        rest = re.sub(r"\s*\.\s*", ".", rest).rstrip(".")
        typ = _ABBREV.get(rest) or _ABBREV.get(rest.replace(".", ""))
        if typ:
            body["denominazioneAtto"] = typ
        elif rest:
            body["titoloRicerca"] = rest
    elif q:
        body["titoloRicerca"] = q
    return body


# --------------------------------------------------------------------------- #
# Adapter
# --------------------------------------------------------------------------- #
class Italy(Jurisdiction):
    code = "it"
    name = "Italy"
    languages = ("it",)
    aliases = ("ita", "italy", "italia")
    sources = (
        Source(
            "Normattiva open-data API (Istituto Poligrafico e Zecca dello Stato)",
            "https://dati.normattiva.it/",
            covers=("legislation",),
            licence=("CC BY 4.0 from 2026-01-01 (dati.normattiva.it 'Dati disponibili' page, read "
                     "2026-11-05; CC BY-NC 4.0 during the 2025 trial)"),
            commercial_use=True,
            ai_use=None,
            auth="none",
            rate_limit=("unknown (not documented); 1 s spacing, no 429 seen in ~20 requests "
                        "(2026-11-05)"),
            terms_url="https://dati.normattiva.it/",
        ),
        Source(
            "Normattiva — www.normattiva.it (texts by URN:NIR)",
            "https://www.normattiva.it/",
            covers=("legislation",),
            licence=("reproduction allowed if the source is named and the text is said to be "
                     "non-authentic and free (Note legali); only the Gazzetta Ufficiale is official"),
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit=("unknown (not documented); 1 s spacing, no 429 seen in ~25 requests "
                        "(2026-11-05). Codice civile pages are 2.6 MB and take 6-12 s."),
            terms_url="https://www.normattiva.it/staticPage/legal",
        ),
    )
    legislation_filters = {
        "search_in": "title (default) or text (words in the text of the act)",
        "type": "denominazione as Normattiva spells it, e.g. LEGGE, DECRETO LEGISLATIVO, "
                "DECRETO-LEGGE, REGIO DECRETO, DECRETO DEL PRESIDENTE DELLA REPUBBLICA",
        "number": "act number, e.g. 241",
        "year": "year of the act, e.g. 1990 (one year only; for a span use year_from / year_to)",
        "year_from": "first year of a span, e.g. 2022 (acts from 1 Jan of that year onward)",
        "year_to": "last year of a span, e.g. 2024 (acts up to 31 Dec of that year)",
        "order": "recente (default, newest first) or vecchio (oldest first)",
    }
    min_interval = {"api.normattiva.it": 1.0, "www.normattiva.it": 1.0}
    notes = ("National legislation from Normattiva, text in force today. Law id = URN:NIR (Codice "
             "civile: urn:nir:stato:regio.decreto:1942-03-16;262; Costituzione: "
             "urn:nir:stato:costituzione:1947-12-27, transitional provisions as 'art. XVIII (all. 1)'). "
             "Search ORs words and sorts by date; cite as 'legge 241/1990' or use type/number/year filters. No case law: "
             "Cassazione (Italgiure) is unreachable from outside Italy; Corte costituzionale search "
             "works (no captcha, 2026-11) but is not built yet.")
    gaps = (
        "Corte costituzionale decisions: source exists and works but not built yet (2026-11 validation: POST search works, no captcha)",
        "Corte di cassazione case law (Italgiure): site down / unreachable from outside Italy (2026-11)",
        "Administrative, appeal and lower-court case law: not researched yet",
        "Regional legislation: not researched yet (Normattiva is national law only)",
    )
    samples = {
        "legislation_query": "r.d. 262/1942",
        "law_id": "urn:nir:stato:regio.decreto:1942-03-16;262",
        "provision": "art. 2043",
    }

    async def search_legislation(self, query, *, limit, page, filters):
        body = _parse_query(query or "")
        search_in = str(filters.get("search_in", "title")).strip().lower()
        if search_in not in ("title", "text"):
            raise BadRequest("search_in must be 'title' or 'text'.")
        if search_in == "text" and "titoloRicerca" in body:
            body["testoRicerca"] = body.pop("titoloRicerca")
        if filters.get("type"):
            body["denominazioneAtto"] = _http.clean(filters["type"]).upper()
        for key, api in (("number", "numeroProvvedimento"), ("year", "annoProvvedimento")):
            if filters.get(key):
                v = _http.clean(filters[key])
                if not (v.isascii() and v.isdigit()):
                    raise BadRequest(f"{key} must be digits, got {v!r}.")
                if key == "year" and not re.fullmatch(r"(?:18|19|20)\d{2}", v):
                    raise BadRequest(f"year must be 4 digits (e.g. 1992), got {v!r}.")
                if key == "number" and int(v) == 0:
                    raise BadRequest(f"number must be positive, got {v!r}.")
                body[api] = str(int(v)) if key == "number" else v
        for key, api, tail in (("year_from", "dataInizioEmanazione", "-01-01"),
                               ("year_to", "dataFineEmanazione", "-12-31")):
            if filters.get(key):
                v = _http.clean(filters[key])
                if not re.fullmatch(r"(?:18|19|20)\d{2}", v):
                    raise BadRequest(f"{key} must be 4 digits (e.g. 2022), got {v!r}.")
                if "annoProvvedimento" in body:
                    raise BadRequest("use either year or year_from/year_to, not both.")
                body[api] = v + tail
        if (body.get("dataInizioEmanazione", "") > body.get("dataFineEmanazione", "9999")):
            raise BadRequest("year_from must not be after year_to.")
        if not body:
            raise BadRequest("give a query (words in the title, or a citation like 'legge "
                             "241/1990') or a type/number/year filter.")
        order = str(filters.get("order", "recente")).strip().lower()
        if order not in ("recente", "vecchio"):
            raise BadRequest("order must be 'recente' or 'vecchio'.")
        body["orderType"] = order
        body["paginazione"] = {"paginaCorrente": max(1, int(page)),
                               "numeroElementiPerPagina": max(1, min(int(limit), 100))}
        r = await _http.post(f"{API}/ricerca/avanzata", json=body)
        if r.status_code != 200:
            raise SourceError(f"Normattiva search returned HTTP {r.status_code}", r.status_code)
        try:
            data = r.json()
        except ValueError:
            raise SourceError("Normattiva search returned no JSON (unsupported query syntax? "
                              "AND/quotes are not supported)", r.status_code)
        if denom := body.get("denominazioneAtto"):
            known = {v.upper() for v in _ABBREV.values()}
            if not data.get("listaAtti") and denom not in known:
                raise BadRequest(f"type {denom!r} matched nothing. Use Normattiva's spelling, "
                                 "e.g. LEGGE, DECRETO LEGISLATIVO, DECRETO-LEGGE, REGIO DECRETO.")
        items = [_law_hit(a) for a in data.get("listaAtti") or []]
        note = ("Title words are OR-ed and results are sorted by date, not relevance; narrow with "
                "a citation ('d.lgs. 196/2003') or type/number/year filters.")
        return Results(items[:limit], total=data.get("numeroAttiTrovati"),
                       note=note if "titoloRicerca" in body or "testoRicerca" in body else "")

    async def get_legislation_toc(self, id):
        urn = _check_urn(id)
        act = await _act(urn)
        return Toc(id=urn, title=act["title"], url=_url(urn), entries=act["entries"])

    async def get_legislation_provision(self, id, provision):
        urn = _check_urn(id)
        key = _art_key(provision or "")
        if not re.match(r"^[0-9ivxlc]", key):
            raise BadRequest(f"provision {provision!r} not understood. Use e.g. 'art. 2043', "
                             "'2043', 'art. 2 bis', 'art. 12 (all. 1)' or 'art. XVIII (all. 1)'.")
        act = await _act(urn)
        if key not in act["arts"]:
            raise NotFound(f"{provision!r} not found in {urn}. See get_legislation_toc for the labels.")
        annex, art, label, link = act["arts"][key]
        # Roman-numbered articles (Costituzione, Disposizioni transitorie I-XVIII) open by number.
        roman = re.fullmatch(r"[ivxlc]+", art)
        frag = f"{urn}{f':{annex}' if annex else ''}~art{_roman_int(art) if roman else art}"
        url = _url(frag)
        # Normattiva serves articles by session state (after art. 9, ~art9.1 gives art. 9), so
        # each lookup starts a fresh session, under the lock.
        async with _session_lock:
            _reset_session()
            body = _body(await _fetch_act(frag))
            if not self._is_art(body, art, roman):
                # The URN resolver can serve a sibling (…;91~art9 gives art. 9.1): fall back to
                # the article's tree link, which needs the act opened in the same fresh session.
                _reset_session()
                await _fetch_act(urn)
                r = await _http.get(SITE + link)
                body, url = _body(r.text) or r.text, _url(urn)
                if r.status_code != 200 or not self._is_art(body, art, roman):
                    raise SourceError(f"Normattiva did not return {label} for {frag}")
        return Provision(law_id=urn, law_title=act["title"], provision=label,
                         text=self._trim(_http.html_to_md(body)), url=url, as_of=_http.today())

    @staticmethod
    def _trim(md: str) -> str:
        """Drop the promulgation preamble before the first '## Art.' heading and the trailing
        AVVERTENZA notes block that Normattiva serves around article 1 / the last article."""
        m = re.search(r"(?m)^## Art\.", md)
        if m:
            md = md[m.start():]
        m = re.search(r"(?m)^AVVERTENZA:", md)
        if m:
            md = md[:m.start()]
        return md.rstrip() + "\n"

    @staticmethod
    def _is_art(body: str, art: str, roman) -> bool:
        plain = re.sub(r"<[^>]+>", " ", body)
        m = (re.search(rf"(?<![A-Za-z])({art.upper()})(?![A-Za-z])", plain[:600]) if roman else
             re.search(r"Art\.\s*([0-9]+(?:\.[0-9]+)?(?:\s*-?\s*[a-z]+)?)", plain))
        return bool(m) and _norm(m.group(1)) == art

    async def get_legislation_text(self, id):
        urn = _check_urn(id)
        async with _session_lock:  # export is bound to the act last opened in this session
            _reset_session()
            html = await _fetch_act(urn)
            act = _parse_act(urn, html)
            _http.lru_put(_page_cache, urn, act, 8)
            if not act["export"]:
                raise SourceError(f"no whole-act export link on the Normattiva page for {urn}")
            r = await _http.get(f"{SITE}/esporta/attoCompleto?{act['export']}")
        if r.status_code != 200 or "Normattiva - Export" not in r.text:
            raise SourceError(f"Normattiva whole-act export failed for {urn}", r.status_code)
        parts = re.findall(r'<div class="bodyTesto">(.*?)(?=<div class="bodyTesto">|<footer|$)',
                           r.text, re.S)
        mds = [t for t in (_http.html_to_md(p) for p in parts) if t]
        # Big acts: the export silently stops (Codice civile at art. 1115) with a "..." block.
        truncated = bool(mds) and mds[-1].strip() == "..."
        if truncated:
            mds.pop()
        text = "\n\n".join(mds)
        if not text:
            raise SourceError(f"empty Normattiva export for {urn}", r.status_code)
        meta = {}
        if truncated:
            last = re.findall(r"Art\.\s*(\d+[\w-]*)", text)
            meta["truncated"] = f"Normattiva's export stops after art. {last[-1] if last else '?'}"
            text += (f"\n\n[{meta['truncated']} of {len(act['arts'])} articles. Use "
                     "get_legislation_toc + get_legislation_provision for the rest.]")
        return LawText(id=urn, title=act["title"], text=text, url=_url(urn), as_of=_http.today(),
                       metadata=meta)
