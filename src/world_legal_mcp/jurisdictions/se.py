"""Sweden: case law from Domstolsverket's Rättspraxis API, legislation from Riksdagen open data.

Gotchas this code encodes:
  * Rättspraxis (rattspraxis.etjanst.domstol.se) is Domstolsverket's open-data service
    (CC0, OpenAPI at /openapi/puh-openapi.yaml). POST /api/v1/sok returns every hit
    WITH its full HTML text (`innehall`), some of which embed base64 images, so even a
    3-hit search can be tens of MB. The only sort is by decision date; no relevance.
  * A "publicering" (id = uuid) is one document: a judgment (DOM_ELLER_BESLUT), a
    case report (REFERAT) or a notice (NOTIS). Several share a group
    (gruppKorrelationsnummer); the public page is /sok/publicering/<group>. An unknown
    uuid gives HTTP 200 with an empty body, not 404. get_decision also accepts a group
    uuid and then opens the group's REFERAT (or its first document).
  * Riksdagen's SFS documents (dok_id sfs-YYYY-N) are the consolidated text
    ("Ändrad: t.o.m. SFS ..."), one whole document per law, no per-section endpoint.
    The HTML has anchors <a class="paragraf" name="K3P1"> (chapter 3, § 1; "P1"
    without chapters) and <h3 name="K3"> chapter headings. A section whose current
    wording is about to be replaced appears twice: the new version anchored, the
    old version as plain "1 § /Rubriken upphör att gälla .../" text with no anchor.
    Both versions are kept under one label.
  * Riksdagen's dokumentlista defaults to date order; we ask for sort=rel.
"""
from __future__ import annotations

import json
import re
from urllib.parse import quote

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

RP = "https://rattspraxis.etjanst.domstol.se"
RP_API = f"{RP}/api/v1"
RD = "https://data.riksdagen.se"
RD_WEB = "https://www.riksdagen.se/sv/dokument-och-lagar/dokument/svensk-forfattningssamling"

_COURTS = {
    "HDO": "Högsta domstolen", "HFD": "Högsta förvaltningsdomstolen",
    "REGR": "Regeringsrätten", "ADO": "Arbetsdomstolen", "MDO": "Marknadsdomstolen",
    "HSV": "Svea hovrätt", "HGO": "Göta hovrätt", "HVS": "Hovrätten för Västra Sverige",
    "HSB": "Hovrätten över Skåne och Blekinge", "HNN": "Hovrätten för Nedre Norrland",
    "HON": "Hovrätten för Övre Norrland", "HYOD": "Svea hovrätts hyresrättsliga avgöranden",
    "KST": "Kammarrätten i Stockholm", "KGG": "Kammarrätten i Göteborg",
    "KJO": "Kammarrätten i Jönköping", "KSU": "Kammarrätten i Sundsvall",
    "MIOD": "Migrationsöverdomstolen", "MMOD": "Mark- och miljööverdomstolen",
    "MOD": "Miljööverdomstolen", "PMOD": "Patent- och marknadsöverdomstolen",
    "PBR": "Patentbesvärsrätten", "RHN": "Rättshjälpsnämnden", "DOV": "Domstolsverket",
}
_HOVRATT = ("HSV", "HGO", "HVS", "HSB", "HNN", "HON")   # the six hovrätter (HYOD is a Svea sub-series)
_FORMS = {"referat": "REFERAT", "dom": "DOM_ELLER_BESLUT", "notis": "NOTIS"}
_TYPES = {"prejudikat": "PREJUDIKAT", "vagledande": "VAGLEDANDE_MEN_EJ_PREJUDICERANDE",
          "ej_vagledande": "EJ_VAGLEDANDE", "provningstillstand": "PROVNINGSTILLSTAND",
          "forhandsavgorande": "FORHANDSAVGORANDE"}
_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)
_SFS = re.compile(r"^\d{4}:\d+$")
# a case-report citation: 'NJA 2024:33', 'NJA 2024 s. 386', 'HFD 2020 ref. 5', 'AD 2019 nr 12'
_CITE = re.compile(r"^[A-ZÅÄÖ]{2,5}\s+\d{4}(?::\d+|\s+(?:s\.?|ref\.?|nr\.?)\s*\d+)$", re.I)


async def _fetch(method: str, url: str, what: str, **kw):
    try:
        r = await (_http.post if method == "POST" else _http.get)(url, **kw)
    except Exception as e:  # network error
        raise SourceError(f"{what}: {type(e).__name__} {e}".strip(), "network") from e
    if r.status_code == 404:
        raise NotFound(f"{what}: not found")
    if r.status_code != 200:
        raise SourceError(f"{what} failed", r.status_code)
    return r


async def _json(method: str, url: str, what: str, **kw):
    r = await _fetch(method, url, what, **kw)
    if not r.content.strip():
        return None
    try:
        return r.json()
    except ValueError as e:
        raise SourceError(f"{what}: unexpected non-JSON reply", r.status_code) from e


# --------------------------------------------------------------------------- #
# Case law
# --------------------------------------------------------------------------- #
def _court(p: dict) -> str:
    d = p.get("domstol") or {}
    return d.get("domstolNamn") or _COURTS.get(d.get("domstolKod", ""), d.get("domstolKod", ""))


def _title(p: dict) -> str:
    court, cn = _court(p), ", ".join(p.get("malNummerLista") or [])
    base = p.get("benamning") or f"{court} {cn}".strip()
    refs = p.get("referatNummerLista") or []
    return f"{refs[0]} ({base})" if refs else base


def _url(p: dict) -> str:
    return f"{RP}/sok/publicering/{p.get('gruppKorrelationsnummer') or p['id']}"


def _hit(p: dict) -> DecisionHit:
    return DecisionHit(id=p["id"], title=_title(p), court=_court(p),
                       date=p.get("avgorandedatum") or "",
                       case_number=", ".join(p.get("malNummerLista") or []),
                       snippet=_http.clean(p.get("sammanfattning"))[:300], url=_url(p))


def _date(v, name: str) -> str:
    if not _ISO.match(str(v)):
        raise BadRequest(f"{name} must be YYYY-MM-DD, got {v!r}")
    return str(v)


def _choice(v, table: dict, name: str) -> str:
    k = str(v).strip().lower()
    if k not in table:
        raise BadRequest(f"{name} must be one of {', '.join(table)}, got {v!r}")
    return table[k]


# --------------------------------------------------------------------------- #
# Legislation
# --------------------------------------------------------------------------- #
def _parse_law_id(id: str) -> str:
    """'SFS 1962:700' | '1962:700' | 'sfs-1962-700' -> Riksdagen dok_id 'sfs-1962-700'."""
    s = _http.clean(id)
    m = re.match(r"^(?:SFS\s*)?(\d{4})\s*:\s*(\d+)$", s, re.I)
    if m:
        return f"sfs-{m[1]}-{m[2]}"
    if re.match(r"^sfs-\d{4}-[\w-]+$", s, re.I):
        return s.lower()
    raise BadRequest(f"Unrecognised Swedish law id {id!r}. Use the SFS number, e.g. "
                     "'1962:700' (also 'SFS 1962:700' or 'sfs-1962-700').")


def _num(s: str) -> str:
    """'2a' -> '2 a'."""
    return re.sub(r"^(\d+)\s*([a-z])$", r"\1 \2", s.strip().lower())


def _label(chapter: str, sec: str) -> str:
    return f"{_num(chapter)} kap. {_num(sec)} §" if chapter else f"{_num(sec)} §"


_TRANS = "Övergångsbestämmelser"
_TOK = re.compile(
    r'<h(?P<hl>[234])\b(?P<ha>[^>]*)>(?P<h>.*?)</h(?P=hl)>'
    r'|<a class="paragraf" name="(?:K(?P<k>\d+[a-z]?))?P(?P<p>\d+[a-z]?)"[^>]*>.*?</a>'
    r'|\n[ \t]*(?P<old>\d+(?: ?[a-z])?) §(?=[ \t]*/)', re.S)


def _md(html: str) -> str:
    """SFS HTML chunk -> markdown. Paragraphs (stycken) are separated only by empty
    <p><a name=..></a></p> markers and <br>, which html_to_md would run together,
    so split on them first. Runs of <pre> lines (hard-wrapped lists) become one paragraph."""
    html = re.sub(r"</pre>\s*<pre>", " ", html)
    html = re.sub(r'</?pre>|<p>\s*<a name="[^"]*"></a>\s*</p>|<br\s*/?>', "\x00", html)
    return "\n\n".join(md for piece in html.split("\x00")
                       if (md := _http.html_to_md(f"<div>{piece}</div>")))


class _Law:
    """One consolidated SFS text, split into sections."""

    def __init__(self, dok_id: str, html: str):
        self.dok_id = dok_id
        m = re.search(r"<h2>(.*?)</h2>", html, re.S)
        self.title = _http.clean(re.sub(r"<[^>]+>", "", m[1])) if m else dok_id
        hr = html.find("<hr")
        head = html[:hr] if hr >= 0 else ""
        self.meta = {_http.clean(k): _http.clean(re.sub(r"<[^>]+>", " ", v))
                     for k, v in re.findall(r"<b>([^<]+)</b>:(.*?)<br", head, re.S)}
        self.meta = {k: v for k, v in self.meta.items() if v and k != "Källa"}
        self.number = self.meta.get("SFS nr", "")
        self.id = self.number if _SFS.match(self.number) else dok_id
        toc_end = html.find("</div>", html.find('class="sfstoc"'))
        body = html[toc_end + 6:] if 'class="sfstoc"' in html else html[hr + 1:]
        self.entries: list[TocEntry] = []
        self.sections: dict[str, list[str]] = {}       # label -> text versions
        self.chapters: dict[str, list[str]] = {}       # "3 kap." -> section labels
        self.parts: list[str] = []                     # full text, in order
        self._parse(body)

    @property
    def url(self) -> str:
        return f"{RD_WEB}/_{self.dok_id}/"

    def _parse(self, body: str) -> None:
        chapter, label, start = "", None, 0
        entry: dict[str, TocEntry] = {}

        def flush(end: int):
            if label is None:
                return
            text = _md(body[start:end])
            block = f"#### {label}\n\n{text}".strip()
            if label in entry and not self.sections[label] and text:
                # sections have no titles of their own: show the opening words in the TOC
                # so its keyword filter finds them
                first = re.sub(r"[*_]", "", text.split("\n\n")[0])
                entry[label].title = f"{label} {first[:80]}{'…' if len(first) > 80 else ''}"
            self.sections.setdefault(label, []).append(block)
            self.parts.append(block)

        for m in _TOK.finditer(body):
            flush(m.start())
            label = None
            if m["hl"]:
                text = _http.clean(re.sub(r"<[^>]+>", "", m["h"]))
                if not text:
                    continue
                lvl = int(m["hl"])
                name = re.search(r'name="([^"]*)"', m["ha"])
                name = name[1] if name else ""
                if lvl == 3 and (name == "overgang" or text.startswith(_TRANS)):
                    chapter, label, start = "", _TRANS, m.end()
                    if _TRANS not in self.sections:
                        self.entries.append(TocEntry(title=_TRANS, level=1, provision=_TRANS))
                    continue
                prov = ""
                if lvl == 3 and (k := re.fullmatch(r"K(\d+[a-z]?)", name)):
                    chapter = k[1]
                    prov = f"{_num(chapter)} kap."
                    self.chapters.setdefault(prov, [])
                self.entries.append(TocEntry(title=text, level=lvl - 2, provision=prov))
                self.parts.append(f"**{text}**" if lvl == 4 else f"{'#' * lvl} {text}")
                continue
            if m["p"]:
                chapter, sec = m["k"] or "", m["p"]
            else:
                sec = m["old"]
            label, start = _label(chapter, sec), m.end()
            if label not in self.sections:
                entry[label] = TocEntry(title=label, level=3, provision=label)
                self.entries.append(entry[label])
                if chapter:
                    self.chapters.setdefault(f"{_num(chapter)} kap.", []).append(label)
                self.sections[label] = []
        flush(len(body))

    def text(self) -> str:
        return "\n\n".join(self.parts)

    def provision(self, p: str) -> tuple[str, str]:
        s = _http.clean(p).lower()
        if s.startswith("överg") or s.startswith("overg"):
            if _TRANS not in self.sections:
                raise NotFound(f"{self.title} has no Övergångsbestämmelser")
            return _TRANS, "\n\n".join(self.sections[_TRANS])
        m = re.fullmatch(r"(?:kap\.?\s*)?(\d+\s?[a-z]?)\s*kap\.?", s)
        if m:
            key = f"{_num(m[1].replace(' ', ''))} kap."
            if key not in self.chapters:
                raise NotFound(f"No chapter {key} in {self.title}")
            body = "\n\n".join(t for lab in self.chapters[key] for t in self.sections[lab])
            return key, body
        m = re.fullmatch(r"(?:(\d+\s?[a-z]?)\s*(?:kap\.?|:)\s*)?(?:§\s*)?(\d+)\s?([a-z])?\s*§?", s)
        if not m:
            raise BadRequest(f"Unrecognised provision {p!r}; use e.g. '3 kap. 1 §' or '3:1' "
                             "(or '5 §' in a law without chapters).")
        sec = m[2] + (m[3] or "")
        if m[1]:
            label = _label(m[1].replace(" ", ""), sec)
        elif self.chapters:
            raise BadRequest(f"{self.title} is divided into chapters; give the chapter too, "
                             f"e.g. '3 kap. {_num(sec)} §' or '3:{_num(sec).replace(' ', '')}'.")
        else:
            label = _label("", sec)
        if label not in self.sections:
            raise NotFound(f"No provision {label} in {self.title}")
        return label, "\n\n".join(self.sections[label])


_RD_SZ = 100  # fixed Riksdagen page size for search_legislation (see there)
_laws: dict[str, _Law] = {}   # dok_id -> parsed law, small in-process cache


async def _law(id: str) -> _Law:
    dok_id = _parse_law_id(id)
    if dok_id not in _laws:
        r = await _fetch("GET", f"{RD}/dokument/{quote(dok_id)}.html", f"Riksdagen {dok_id}")
        if 'class="paragraf"' not in r.text and "<h2>" not in r.text:
            raise NotFound(f"No SFS text for {id!r} at Riksdagen")
        _http.lru_put(_laws, dok_id, _Law(dok_id, r.text), 4)
    return _laws[dok_id]


def _plain(v: str) -> str:
    """Rättspraxis sometimes ships a list as a JSON string; show it as plain text."""
    v = (v or "").strip()
    if v.startswith("["):
        try:
            items = json.loads(v)
        except ValueError:
            return v
        if isinstance(items, list):
            return "; ".join(str(x) for x in items)
    return v


class Sweden(Jurisdiction):
    code = "se"
    name = "Sweden"
    languages = ("sv",)
    aliases = ("swe", "sweden", "sverige")
    sources = (
        Source(
            name="Rättspraxis open data (Domstolsverket / Sveriges Domstolar)",
            url=f"{RP}/sok/sokning",
            covers=("caselaw",),
            licence="CC0 1.0 (dataset 'Domstolars rättspraxis' on dataportal.se, publisher "
                    "Domstolsverket); documented API: /openapi/puh-openapi.yaml",
            commercial_use=True,
            ai_use=None,
            auth="none",
            rate_limit="unknown, none documented; no 429 in ~25 requests (2026-11); using 1 s spacing",
            terms_url="https://www.domstol.se/om-webbplatsen-och-digitala-kanaler/oppna-data/",
        ),
        Source(
            name="Riksdagens öppna data, SFS (Källa: Sveriges riksdag)",
            url=f"{RD}/",
            covers=("legislation",),
            licence="Riksdagen open data terms: free to use and redistribute with attribution "
                    "'Källa: Sveriges riksdag'; must not suggest the Riksdag stands behind the service",
            commercial_use=True,
            ai_use=None,
            auth="none",
            rate_limit="unknown, none documented; no 429 in ~20 requests (2026-11); using 1 s spacing",
            terms_url="https://www.riksdagen.se/sv/dokument-och-lagar/riksdagens-oppna-data/"
                      "anvandarstod/anvandningsvillkor/",
        ),
    )
    caselaw_filters = {
        "court": "court code, e.g. 'HDO' (Högsta domstolen), 'HFD', 'ADO', 'HSV' (Svea hovrätt), "
                 "'MIOD', 'KST'; 'HOVR' = all hovrätter (HSV, HGO, HVS, HSB, HNN, HON); "
                 "an unknown code lists every code with its court name",
        "form": "publication form: 'referat' (case report), 'dom' (judgment/decision), 'notis'",
        "type": "'prejudikat', 'vagledande', 'ej_vagledande', 'provningstillstand', "
                "'forhandsavgorande'",
        "sfs": "cited statute, SFS number, e.g. '1962:700' (Brottsbalken)",
        "case_number": "case number (målnummer), e.g. 'B 6705-20'",
        "date_from": "decided on or after, YYYY-MM-DD",
        "date_to": "decided on or before, YYYY-MM-DD",
    }
    min_interval = {"rattspraxis.etjanst.domstol.se": 1.0, "data.riksdagen.se": 1.0}
    notes = ("Case law: higher courts' case reports since 1981 and published judgments since "
             "March 2025, newest first (no relevance ranking). Laws: consolidated SFS texts "
             "from Riksdagen; cite as '1962:700', provisions as '3 kap. 1 §' or '3:1'.")
    gaps = (
        "Case reports before 1981 and judgments not chosen for publication: not in Rättspraxis",
        "Published judgments (not case reports) before March 2025: not in Rättspraxis",
        ("Earlier versions of laws (point in time): Riksdagen gives the current consolidated text "
         "only; not researched yet"),
        "Agency regulations (myndighetsföreskrifter): not researched yet",
    )
    samples = {
        "caselaw_query": "skadestånd",
        "decision_id": "f876d0f7-4d67-4ea7-a097-2cef89daf082",
        "legislation_query": "brottsbalk",
        "law_id": "1962:700",
        "provision": "3 kap. 1 §",
    }

    # ----------------------------------------------------------------- caselaw
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        f: dict = {}
        if c := filters.get("court"):
            c = str(c).strip().upper()
            if c in ("HOVR", "HOVRATT", "HOVRÄTT", "HOVRATTEN", "HOVRÄTTEN"):
                f["domstolKodLista"] = list(_HOVRATT)
            elif c not in _COURTS:
                raise BadRequest(f"Unknown court code {c!r}. Known: "
                                 + ", ".join(f"{k} ({v})" for k, v in _COURTS.items())
                                 + ". 'HOVR' selects all the hovrätter.")
            else:
                f["domstolKodLista"] = [c]
        if v := filters.get("form"):
            f["publiceringsformLista"] = [_choice(v, _FORMS, "form")]
        if v := filters.get("type"):
            f["avgorandeTypLista"] = [_choice(v, _TYPES, "type")]
        if v := filters.get("sfs"):
            if not _SFS.match(str(v).strip()):
                raise BadRequest(f"sfs must be an SFS number like '1962:700', got {v!r}")
            f["sfsNummerLista"] = [str(v).strip()]
        if v := filters.get("case_number"):
            f["malnummerLista"] = [_http.clean(v)]
        if filters.get("date_from") or filters.get("date_to"):
            f["intervall"] = {
                "fromDatum": _date(filters["date_from"], "date_from") if filters.get("date_from") else None,
                "toDatum": _date(filters["date_to"], "date_to") if filters.get("date_to") else None}
        terms = [t for t in (query or "").split() if any(c.isalnum() for c in t)]
        if (query or "").strip() and not terms:
            raise BadRequest(f"query has no searchable words: {query!r}")
        cite = _CITE.fullmatch((query or "").strip())
        # the AND list matches loosely (word-by-word across the text); a citation needs the exact phrase
        body = {"sokfras": {"andLista": [] if cite else terms, "orLista": [], "notLista": [],
                            "exaktFras": " ".join(query.split()) if cite else ""},
                "antalPerSida": limit, "sidIndex": max(0, page - 1), "asc": False,
                "sortorder": "avgorandedatum", "filter": f or None}
        d = await _json("POST", f"{RP_API}/sok", "Rättspraxis search", json=body) or {}
        return Results(items=[_hit(p) for p in d.get("publiceringLista") or []],
                       total=d.get("total"),
                       note="Newest decision first (the source has no relevance ranking).")

    async def get_decision(self, id):
        s = (id or "").strip().lower()
        if not _UUID.match(s):
            raise BadRequest(f"Use a Rättspraxis publication id (uuid, from search_caselaw), got {id!r}")
        p = await _json("GET", f"{RP_API}/publiceringar/{s}", "Rättspraxis decision")
        if not p:   # maybe a group id (the one in the public URL)
            g = await _json("GET", f"{RP_API}/publiceringar/grupp/{s}", "Rättspraxis group") or []
            if not g:
                raise NotFound(f"No decision {id!r} in Rättspraxis")
            p = next((x for x in g if x.get("publiceringsform") == "REFERAT"), g[0])
        meta = {
            "Referat": ", ".join(p.get("referatNummerLista") or []),
            "ECLI": p.get("ecliNummer") or "",
            "AD-domsnummer": p.get("arbetsdomstolenDomsnummer") or "",
            "Publiceringsform": p.get("publiceringsform") or "",
            "Typ": p.get("typ") or "",
            "Lagrum": "; ".join(x.get("referens", "") for x in p.get("lagrumLista") or []),
            "Rättsområde": "; ".join(p.get("rattsomradeLista") or []),
            "Nyckelord": "; ".join(p.get("nyckelordLista") or []),
            "Förarbeten": "; ".join(p.get("forarbeteLista") or []),
            "Litteratur": "; ".join(f"{x.get('forfattare', '')}, {x.get('titel', '')}".strip(", ")
                                    for x in p.get("litteraturLista") or []),
            "Hänvisningar": "; ".join(_plain(x.get("fritext", "")) for x in p.get("hanvisadePubliceringarLista") or []),
            "EU-/Europarätt": "; ".join(p.get("europarattsligaAvgorandenLista") or []),
            "Bilagor": "; ".join(f"{b.get('filnamn', '')} <{RP_API}/bilagor/{b.get('fillagringId', '')}>"
                                 for b in p.get("bilagaLista") or []),
            "Publicerad": (p.get("publiceringstid") or "")[:10],
        }
        text = _http.html_to_md(p.get("innehall") or "")
        if not text.strip():
            pdf = "see the PDF under Bilagor" if p.get("bilagaLista") else "no PDF is attached either"
            text = ("(Rättspraxis publishes no body text for this entry; "
                    f"{pdf}. Open the Source link for what the court has published.)")
        return Decision(id=p["id"], title=_title(p), text=text,
                        url=_url(p), court=_court(p), date=p.get("avgorandedatum") or "",
                        case_number=", ".join(p.get("malNummerLista") or []),
                        summary=_http.clean(p.get("sammanfattning")),
                        metadata={k: _http.clean(v) for k, v in meta.items() if _http.clean(v)})

    # ------------------------------------------------------------- legislation
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        # Riksdagen orders equal relevance scores differently for different page sizes (sz) and
        # can repeat/skip a hit across its own page edges, so always ask for one large fixed sz
        # and cut our page out by offset.
        start = (max(1, page) - 1) * limit
        docs, dl = [], {}
        for p in range(start // _RD_SZ + 1, (start + limit - 1) // _RD_SZ + 2):
            params = {"sok": query or "", "doktyp": "sfs", "utformat": "json", "sz": _RD_SZ,
                      "p": p, "sort": "rel", "sortorder": "desc"}
            d = (await _json("GET", f"{RD}/dokumentlista/", "Riksdagen search", params=params) or {})
            dl = d.get("dokumentlista") or {}
            rows = dl.get("dokument") or []
            rows = [rows] if isinstance(rows, dict) else rows
            docs += rows
            if len(rows) < _RD_SZ:
                break
        docs = docs[start % _RD_SZ:start % _RD_SZ + limit]
        items = []
        for x in docs:
            bet = x.get("beteckning") or ""
            items.append(LawHit(
                id=bet if _SFS.match(bet) else x.get("dok_id", ""),
                title=_http.clean(x.get("titel")), type="SFS", number=bet,
                date=_http.iso_date(x.get("datum")),
                snippet=_http.clean(re.sub(r"</?mark>", "", x.get("summary") or ""))[:300],
                url=f"{RD_WEB}/_{x.get('dok_id', '')}/"))
        total = dl.get("@traffar")
        note = "Consolidated texts (Svensk författningssamling). Källa: Sveriges riksdag."
        if start + limit > _RD_SZ:  # Riksdagen's own pages can repeat or skip a hit at their edges
            note += (f" Beyond hit {_RD_SZ}, Riksdagen's paging can repeat or skip a hit near each "
                     f"{_RD_SZ}-hit boundary; narrow the query rather than paging deep.")
        return Results(items=items, total=int(total) if str(total or "").isdigit() else None, note=note)

    async def get_legislation_toc(self, id):
        law = await _law(id)
        return Toc(id=law.id, title=law.title, url=law.url, entries=law.entries)

    async def get_legislation_provision(self, id, provision):
        law = await _law(id)
        label, text = law.provision(provision)
        return Provision(law_id=law.id, law_title=law.title, provision=label, text=text,
                         url=law.url)

    async def get_legislation_text(self, id):
        law = await _law(id)
        return LawText(id=law.id, title=law.title, text=law.text(), url=law.url,
                       metadata={**law.meta, "Källa": "Sveriges riksdag"})
