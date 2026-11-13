"""Estonia: consolidated legislation from Riigi Teataja (www.riigiteataja.ee). No case law.

Gotchas this code encodes:
  * Riigi Teataja was relaunched on 2026-06-01 as an Angular SPA; every /akt/... page is
    the same JS shell. Data comes from the SPA's backend, `public-api/api/v1/`.
  * Act text: `akt/{id}/xml` is the documented open-data route (RT FAQ "9. Avaandmed",
    which replaced the old /akt/{id}.xml). It returns the full consolidated act XML
    (tyviseadus schema): sisu > osa/peatykk/jagu/jaotis > paragrahv > loige > alampunkt.
    A bad id gives a JSON 500 there, so we read `akt/{id}` (JSON metadata, clean 404)
    first; it also carries the status (KEHTIV / KEHTINUD ...) and the English
    translation id (tolkeSeosId).
  * Ids are Riigi Teataja *version* ids (globaalID): every consolidated wording of an act
    has its own id. Search returns the wording valid today by default; an old id still
    opens the old wording, with its status in the metadata.
  * Search: `POST otsing/tervik-tekst` is what the SPA uses (undocumented; body found in
    the SPA bundle). Title search by default, full text with in_text=true. 30 hits per
    call; `searchAfter` is a plain zero-based offset. `status` must be one of
    KEHTIVAD_KEHTETUTETA / KEHTETUD / JOUSTUVAD / KOIK_OTSITAVAD. The documented
    `api/oigusakt_otsing/1/otsi` only does title-substring listing without ranking.
  * § numbers can carry a superscript (§ 11¹: paragrahvNr ylaIndeks="1"); kuvatavNr holds
    it as escaped "<sup>1</sup>" text, running text as real <sup> elements.
  * robots.txt disallows `*/akt/{id}/*` for ~5,600 listed (old, personal-data) acts and
    all of `*/kohtulahendid/*` and `*/kohtuteave/*` (court decisions). We read robots.txt
    once per process and refuse the listed ids. Case law is left out entirely: Riigi
    Teataja's decision routes and the Supreme Court's rikos.rik.ee (Disallow: /) are
    both closed to robots.
  * English translations exist for many acts (not authentic texts). We serve Estonian
    only and point to the translation page when the source links one.
"""
from __future__ import annotations

import re

from lxml import etree

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import LawHit, LawText, Provision, Results, Toc, TocEntry

SITE = "https://www.riigiteataja.ee"
API = f"{SITE}/public-api/api/v1"
PAGE = 30  # hits per search call, fixed by the source
MAX_PAGES = 20  # source pages scanned per search

_STATUS = {"in_force": "KEHTIVAD_KEHTETUTETA", "repealed": "KEHTETUD",
           "upcoming": "JOUSTUVAD", "all": "KOIK_OTSITAVAD"}
_COUNT = {"KEHTIVAD_KEHTETUTETA": "kehtivad", "KEHTETUD": "kehtetud",
          "JOUSTUVAD": "joustuvad", "KOIK_OTSITAVAD": "koik"}
_STRUCT = ("osa", "peatykk", "jagu", "jaotis", "alljaotis")
_SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
_UNSUP = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")

_STATUS_GLOSS = {"JOUSTUNUD": "JOUSTUNUD (entered into force, not repealed; a one-off act, "
                              "not a maintained consolidated text)"}

_CURRENT_ONLY = ("\n\n(Fontes note: only the current consolidated wording is served; "
                 "no as-at-date wording of earlier versions.)")

_laws: dict = {}
_blocked: set[str] | None = None


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #
async def _robots_blocked() -> set[str]:
    """Act ids robots.txt disallows (`Disallow: */akt/{id}/*`), read once per process."""
    global _blocked
    if _blocked is None:
        r = await _http.get(f"{SITE}/robots.txt")
        if r.status_code != 200:
            raise SourceError("could not read riigiteataja.ee/robots.txt", r.status_code)
        _blocked = set(re.findall(r"(?im)^Disallow:\s*\*/akt/(\d+)/", r.text))
    return _blocked


def _word_start(title, words) -> bool:
    """True if every query word starts a word of the title (not just sits inside a compound)."""
    ts = [t.casefold() for t in re.findall(r"\w+", title or "")]
    return all(any(t.startswith(w) for t in ts) for w in words)


def _status_label(raw) -> str:
    st = _http.clean(raw)
    return _STATUS_GLOSS.get(st, st)


def _parse_id(law_id: str) -> str:
    s = str(law_id or "").strip()
    m = re.fullmatch(r"(?:https?://(?:www\.)?riigiteataja\.ee/(?:\w\w/)?(?:akt|eli/ee/[^/]+/[^/]+)/)?"
                     r"(\d{5,12})(?:\.xml|/consolide|/xml)?/?", s, re.I)
    if not m:
        raise BadRequest(f"id {law_id!r}: use a Riigi Teataja act id from search_legislation, "
                         "e.g. '120062026018' (or its riigiteataja.ee/akt/... URL)")
    return m[1]


async def _api_json(path: str, what: str, **kw):
    r = await (_http.post(f"{API}/{path}", **kw) if "json" in kw else _http.get(f"{API}/{path}", **kw))
    if r.status_code == 404:
        raise NotFound(f"{what}: not found")
    if r.status_code != 200:
        raise SourceError(f"Riigi Teataja {what} failed", r.status_code)
    try:
        return r.json()
    except ValueError as e:
        raise SourceError(f"Riigi Teataja {what}: unexpected non-JSON reply", r.status_code) from e


async def _law(law_id: str) -> dict:
    aid = _parse_id(law_id)
    if aid in _laws:
        return _laws[aid]
    if aid in await _robots_blocked():
        raise SourceError(f"riigiteataja.ee/robots.txt disallows automated access to act {aid}; "
                          f"open {SITE}/akt/{aid} in a browser", "robots")
    meta = await _api_json(f"akt/{aid}", f"act {aid}", headers={"Accept": "application/json"})
    r = await _http.get(f"{API}/akt/{aid}/xml")
    if r.status_code != 200 or not r.content.lstrip().startswith(b"<"):
        raise SourceError(f"Riigi Teataja act {aid} XML failed", r.status_code)
    try:
        root = etree.fromstring(r.content, etree.XMLParser(huge_tree=True, resolve_entities=False))
    except etree.XMLSyntaxError as e:
        raise SourceError(f"Riigi Teataja act {aid}: unreadable XML ({e})") from e
    md = _child(root, "metaandmed")
    title = _http.clean(_http.text(_find(root, "aktinimi/nimi/pealkiri"))) or \
        _http.clean((meta.get("aktiParameetrid") or {}).get("pealkiri"))
    sisu = _child(root, "sisu")
    if sisu is None:
        raise SourceError(f"Riigi Teataja act {aid}: XML has no <sisu> body")
    tr = meta.get("tolkeSeosId")
    law = {
        "id": aid, "title": title or aid, "url": f"{SITE}/akt/{aid}", "body": sisu,
        "as_of": _date(_find(md, "kehtivus/kehtivuseAlgus")),
        "meta": {k: v for k, v in (
            ("abbreviation", _txt(_find(md, "lyhend"))),
            ("issuer", _txt(_find(md, "valjaandja"))),
            ("type", _txt(_find(md, "dokumentLiik"))),
            ("text type", _txt(_find(md, "tekstiliik"))),
            ("status", str(meta.get("aktiStaatus") or "")),
            ("valid from", _date(_find(md, "kehtivus/kehtivuseAlgus"))),
            ("valid until", _date(_find(md, "kehtivus/kehtivuseLopp"))),
            ("adopted", _date(_find(md, "vastuvoetud/aktikuupaev"))),
            ("in force since", _date(_find(md, "vastuvoetud/joustumine"))),
            ("act group id", _txt(_find(md, "terviktekstiGrupiID"))),
            ("English translation (unofficial)", f"{SITE}/en/akt/{tr}" if tr else ""),
        ) if v},
    }
    return _http.lru_put(_laws, aid, law, 6)


# --------------------------------------------------------------------------- #
# XML helpers
# --------------------------------------------------------------------------- #
def _child(el, name):
    if el is None:
        return None
    return next((c for c in el if _http.localname(c) == name), None)


def _find(el, path: str):
    for name in path.split("/"):
        el = _child(el, name)
    return el


def _txt(el) -> str:
    return _http.clean(_http.text(el)) if el is not None else ""


def _date(el) -> str:
    return _http.iso_date(_txt(el)[:10])


def _sup(s: str) -> str:
    """'§ 11<sup>1</sup>.' (escaped markup in kuvatavNr) -> '§ 11¹.'"""
    return re.sub(r"<sup>\s*(\d+)\s*</sup>", lambda m: m[1].translate(_SUP), s or "")


def _note(m) -> str:
    """<muutmismarge> -> '[RT I, 31.12.2013, 1 - jõust. 13.06.2014]' as the site shows it."""
    am = _child(m, "avaldamismarge")
    pre = _txt(_child(m, "tavatekst"))
    ref = ""
    if am is not None:
        osa, art = _txt(_child(am, "RTosa")), _txt(_child(am, "RTartikkel"))
        day = _date(_child(am, "avaldamineKuupaev"))
        if day:
            y, mo, d = day.split("-")
            ref = f"{osa}, {d}.{mo}.{y}, {art}"
        else:
            ref = f"{osa} {_txt(_child(am, 'RTaasta'))}, {_txt(_child(am, 'RTnr'))}, {art}"
    j = _date(_child(m, "joustumine"))
    if j:
        y, mo, d = j.split("-")
        ref += f" - jõust. {d}.{mo}.{y}"
    out = " ".join(x for x in (pre, ref.strip()) if x)
    return f"[{out}]" if out else ""


def _inline(el) -> str:
    """Running text of a sisuTekst-like element: <sup> as superscript, links as their
    text, <reavahetus/> as a line break, amendment marks as bracketed notes."""
    out = [el.text or ""]
    for c in el:
        name = _http.localname(c)
        if name == "sup":
            out.append(_http.text(c).translate(_SUP))
        elif name == "reavahetus":
            out.append("\x00")  # source newlines are layout whitespace; only this breaks
        elif name == "viide":
            out.append(_http.text(_child(c, "kuvatavTekst")))
        elif name == "muutmismarge":
            out.append(" " + _note(c))
        elif name:
            out.append(_inline(c))
        out.append(c.tail or "")
    s = _sup("".join(out)).replace("\xa0", " ")
    return "  \n".join(_http.clean(ln) for ln in s.split("\x00") if ln.strip())


def _item(el) -> list[str]:
    """A loige / alampunkt: '(1) text [note]', then its sub-points as own paragraphs."""
    head, body, subs = _sup(_txt(_child(el, "kuvatavNr"))), [], []
    for c in el:
        name = _http.localname(c)
        if name == "sisuTekst" or name == "tavatekst":
            body.append(_inline(c))
        elif name == "muutmismarge":
            body.append(_note(c))
        elif name in ("loige", "alampunkt"):
            subs += _item(c)
    first = " ".join(x for x in [head, *body] if x)
    return ([first] if first else []) + subs


def _label(p) -> str:
    nr = _child(p, "paragrahvNr")
    n = _txt(nr)
    sup = nr.get("ylaIndeks") if nr is not None else None
    return f"§ {n}{(sup or '').translate(_SUP)}" if n else ""


def _para_heading(p) -> str:
    num = _sup(_txt(_child(p, "kuvatavNr"))) or f"{_label(p)}."
    return " ".join(x for x in (num, _txt(_child(p, "paragrahvPealkiri"))) if x)


def _para(p) -> list[str]:
    out = [f"**{_para_heading(p)}**"]
    for c in p:
        name = _http.localname(c)
        if name in ("loige", "alampunkt"):
            out += _item(c)
        elif name in ("sisuTekst", "tavatekst"):
            out.append(_inline(c))
        elif name == "muutmismarge":
            out.append(_note(c))
    return [x for x in out if x]


def _struct_heading(el) -> str:
    name = _http.localname(el)
    return " ".join(x for x in (_sup(_txt(_child(el, "kuvatavNr"))),
                                _txt(_child(el, f"{name}Pealkiri"))) if x)


def _walk(el, depth: int = 0):
    """Yield (kind, element, depth) over the body: 'struct', 'para' or 'other'."""
    for c in el:
        name = _http.localname(c)
        if not name or name.endswith("Nr") or name.endswith("Pealkiri"):
            continue
        if name in _STRUCT:
            yield "struct", c, depth
            yield from _walk(c, depth + 1)
        elif name == "paragrahv":
            yield "para", c, depth
        elif any(_http.localname(d) == "paragrahv" for d in c.iter()):
            yield from _walk(c, depth)
        else:
            yield "other", c, depth


def _to_md(body) -> str:
    out: list[str] = []
    for kind, el, depth in _walk(body):
        if kind == "struct":
            out.append(f"{'#' * min(6, depth + 2)} {_struct_heading(el)}")
        elif kind == "para":
            out += _para(el)
        else:
            t = _note(el) if _http.localname(el) == "muutmismarge" else _inline(el)
            if t:
                out.append(t)
    return "\n\n".join(out)


def _norm_label(provision: str) -> tuple[str, str]:
    """'§ 11¹', '11^1', '11.1', '11b1', 'para11b1', 'paragrahv 5' -> ('11', '1') / ('5', '')."""
    s = str(provision or "").strip()
    s = re.sub(r"[⁰¹²³⁴⁵⁶⁷⁸⁹]+", lambda m: "^" + m[0].translate(_UNSUP), s).lower()
    s = re.sub(r"^(?:§+|paragrahv|para|par\.?|section|sec\.?|s\.)\s*", "", s).rstrip(". ")
    m = re.fullmatch(r"(\d+)(?:\s*(?:\^|b|\.|-|\s)\s*(\d+))?", s)
    if not m:
        raise BadRequest(f"provision {provision!r}: use a § number as the TOC shows it, "
                         "e.g. '§ 5', '5', '§ 11¹' or '11^1'")
    return str(int(m[1])), (str(int(m[2])) if m[2] else "")


# --------------------------------------------------------------------------- #
class Estonia(Jurisdiction):
    code = "ee"
    name = "Estonia"
    languages = ("et",)
    aliases = ("estonia", "eesti", "est")
    sources = (
        Source(
            name="Riigi Teataja (State Gazette, Ministry of Justice and Digital Affairs)",
            url=SITE,
            covers=("legislation",),
            licence=("Legal acts are not protected by copyright (Copyright Act § 5 p 1); RT "
                     "publishes all acts as XML open data (RT FAQ '9. Avaandmed'). RT Act § 12(1): "
                     "texts shown elsewhere must refer to the Riigi Teataja text."),
            commercial_use=True,
            ai_use=None,
            auth="none",
            rate_limit=("not published (behind Cloudflare); no 429 in ~40 requests "
                        "(2026-11-05); using 1 s spacing"),
            terms_url=f"{SITE}/kkk",
        ),
    )
    legislation_filters = {
        "status": "'in_force' (default: in force on today's date), 'repealed', 'upcoming' "
                  "(not yet in force) or 'all'",
        "in_text": "'true' to search the full text as well as titles (default: titles only)",
    }
    min_interval = {"www.riigiteataja.ee": 1.0}
    notes = ("Consolidated legislation in Estonian from Riigi Teataja; ids are RT version ids "
             "('120062026018'), provisions '§ 5' / '§ 11¹'. English translations (unofficial) "
             "are linked where RT has one. No case law here: robots.txt closes the court-decision routes; "
             "look up Supreme Court (Riigikohus) judgments on the court's own site, www.riigikohus.ee "
             "(Lahendid), or the courts' decision search at www.kohus.ee, by hand.")
    gaps = (
        "Case law (Supreme Court and all courts; read them at www.riigikohus.ee / www.kohus.ee yourself): robots.txt disallows RT's decision routes and rikos.rik.ee ('Disallow: /')",
        "About 5,600 old acts (personal data): robots.txt disallows their /akt/ pages",
        "English translations of acts: linked only, text not served; source works but not built",
        "Local government regulations: not researched yet",
    )
    samples = {
        "legislation_query": "võlaõigusseadus",
        "law_id": "120062026018",   # Võlaõigusseadus, wording valid 2026-09-01..2026-12-31
        "provision": "§ 1",
    }

    async def search_legislation(self, query, *, limit, page, filters):
        q = _http.clean(query)
        if not q:
            raise BadRequest("give words from the act title in Estonian, e.g. 'võlaõigusseadus'")
        st = str(filters.get("status") or "in_force").lower()
        if st not in _STATUS:
            raise BadRequest(f"status {st!r}: use one of {', '.join(_STATUS)}")
        it = str(filters.get("in_text") or "false").lower()
        if it not in ("true", "false"):
            raise BadRequest("in_text: use 'true' or 'false'")
        in_text = it == "true"
        n = max(1, int(limit))
        offset = (max(1, int(page)) - 1) * n
        valid = f"{_http.today()}T00:00:00.000+02:00"
        skip = st == "in_force"  # the source's in-force list also holds JOUSTUNUD one-off acts
        want = offset + n
        hits, seen, total, exhausted = [], set(), None, True
        # With in_text, acts whose title matches come first (the source's text hits are in
        # title order, not relevance), then the remaining full-text hits.
        words = [w.casefold() for w in re.findall(r"\w+", q)]
        for title_only in ((True, False) if in_text else (True,)):
            src = 0
            for _ in range(MAX_PAGES):
                body = {"general": {"searchText": q, "searchText2": "", "searchInTitle": title_only,
                                    "searchInText": not title_only, "logicalOperator": "AND",
                                    "morphSearch": False, "searchAfter": src},
                        "precise": {"status": _STATUS[st], "validDate": valid,
                                    "excludedFilterList": []}}
                d = await _api_json("otsing/tervik-tekst", "search", json=body,
                                    headers={"Accept": "application/json"})
                got = d.get("results") or []
                total = d.get(_COUNT[_STATUS[st]], d.get("koik"))
                src += len(got)
                for h in got:
                    if h["id"] in seen or (skip and h.get("reportStatus") == "JOUSTUNUD"):
                        continue
                    seen.add(h["id"])
                    h["_rank"] = (0 if title_only else 1, 0 if _word_start(h.get("title"), words) else 1)
                    hits.append(h)
                if len(got) < PAGE:
                    break
                if len(hits) >= want:
                    exhausted = False
                    break
            else:
                exhausted = False
            if len(hits) >= want:
                exhausted = exhausted and not (in_text and title_only)
                break
        if not in_text and any(h["_rank"] == (0, 0) for h in hits):
            # titles only: drop acts that merely contain the word inside a compound
            # (e.g. 'koostöölepingu' for 'tööleping') when real word matches exist
            hits = [h for h in hits if h["_rank"] == (0, 0)]
        if exhausted or (skip or in_text):
            total = len(hits) if exhausted else None
        hits.sort(key=lambda h: h["_rank"])
        hits = hits[offset:want]
        items = []
        for h in hits:
            ctx = []
            for c in (h.get("contexts") or [])[:2]:
                where = " ".join(x for x in (f"§ {c['paragraph']}" if c.get("paragraph") else "",
                                             f"lg {c['loige']}" if c.get("loige") else "") if x)
                txt = _http.clean(re.sub(r"<[^>]+>", "", c.get("html") or ""))
                if txt:
                    ctx.append(f"{where}: {txt}" if where else txt)
            tr = h.get("connectedTranslationId")
            if tr:
                ctx.append(f"English translation: {SITE}/en/akt/{tr}")
            items.append(LawHit(
                id=str(h["id"]),
                title=_http.clean(h.get("title")) + (f" ({h['abbreviation']})" if h.get("abbreviation") else ""),
                type=" / ".join(x for x in (h.get("reportIssuer"), h.get("reportType")) if x),
                number=_http.clean(h.get("number")),
                date=_http.iso_date((h.get("reportDateStart") or "")[:10]),
                status=_status_label(h.get("reportStatus")),
                snippet=" … ".join(ctx)[:500],
                url=f"{SITE}/akt/{h['id']}",
            ))
        return Results(items=items, total=total if isinstance(total, int) else None,
                       note=("Titles only unless in_text=true (titles that merely contain your word inside a compound, e.g. 'koostöölepingu' for 'tööleping', are hidden when titles with the word itself exist); ids are version ids (date = this "
                             "wording valid from). Estonian texts; English translations are "
                             "unofficial and only linked. 'in_force' lists acts with status "
                             "KEHTIV only; one-off acts (JOUSTUNUD, e.g. government orders) "
                             "show with status 'all'. With in_text=true, acts whose title "
                             "matches are listed first (titles with a word that starts with your word before "
                             "compounds that merely contain it, e.g. 'koostöölepingu' for 'tööleping'), then other full-text hits (title "
                             "order, not relevance). Only the current consolidated text is "
                             "served: no as-at-date wording; the 'repealed' filter lists "
                             "repealed acts, not earlier wordings of current ones."))

    async def get_legislation_toc(self, id):
        law = await _law(id)
        entries = []
        for kind, el, depth in _walk(law["body"]):
            if kind == "struct":
                entries.append(TocEntry(title=_struct_heading(el), level=depth))
            elif kind == "para":
                entries.append(TocEntry(title=_para_heading(el), level=depth, provision=_label(el)))
        return Toc(id=law["id"], title=law["title"], url=law["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        law = await _law(id)
        want = _norm_label(provision)
        for kind, el, _ in _walk(law["body"]):
            if kind != "para":
                continue
            nr = _child(el, "paragrahvNr")
            if (_txt(nr), (nr.get("ylaIndeks") or "") if nr is not None else "") == want:
                return Provision(law_id=law["id"], law_title=law["title"], provision=_label(el),
                                 text="\n\n".join(_para(el)) + _CURRENT_ONLY, url=law["url"], as_of=law["as_of"])
        raise NotFound(f"no {provision!r} in {law['title']} ({law['id']}); labels look like "
                       "'§ 5' or '§ 11¹' (see get_legislation_toc)")

    async def get_legislation_text(self, id):
        law = await _law(id)
        return LawText(id=law["id"], title=law["title"], text=_to_md(law["body"]),
                       url=law["url"], as_of=law["as_of"], metadata=dict(law["meta"]))
