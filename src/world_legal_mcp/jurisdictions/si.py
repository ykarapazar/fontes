"""Slovenia: case law from sodnapraksa.si (Supreme Court portal), legislation from PISRS.

Gotchas this code encodes (verified 2026-11-05 from a UK IP):
  * sodnapraksa.si is a Vue SPA over a Solr-backed JSON API at /backend/api/ (no auth for
    search and documents; Keycloak is only for favourites/notes). POST search/documents
    takes {simpleSearch, query:{q}, page (0-based), pageSize, sortField, sortDirection,
    filterQueries (Solr fq strings), fieldList}. Date field for filters is `date`.
    The collection mixes court decisions (vsrs, viso, vdss, uprs) with SOPM/SOSC
    journal articles (copyrighted, excluded here), the NEGM damages table and CJEU (seu);
    we filter to court decisions only.
  * A decision is GET search/documents/orders/{numeric id}. The id we expose is the ECLI
    (resolved through a Solr query `ecli:"..."`); a bare numeric id works too.
  * PISRS (pisrs.si) is an Angular SPA over /api. Search is POST /api/filter/filter
    ?cursorMark=* with {simpleSearch, besedilo:{word1, word1InTitle, word1InContent},
    nazivZbirke}. 10 results per page, Solr cursor paging only, so page n costs n requests.
    robots.txt disallows the /iskanje UI route (not /api).
  * A law is addressed by its register id (zunanjiId, e.g. ZAKO1263 = OZ):
    /api/rezultat/zbirka/id/{id} gives metadata and the NPB (unofficial consolidated text)
    versions in ascending order; the last one is current. Its structured text is
    /api/rezultat/neuradno-precisceno-besedilo/{npbId}/details: a flat `besedilo` list
    (struktura: clen/odstavek/poglavje/...) plus a `kazalo` (TOC) pointing at element ids.
    An article is the run of elements from its TOC element to the next TOC element.
  * PISRS answers a 403 with a proof-of-work bot challenge (/api/a). We do not solve it:
    a 403 is reported as a SourceError.
  * 2026-11-10: every judiciary host on 84.39.221.x (sodnapraksa.si, www.sodnapraksa.si,
    www.sodisce.si) accepts the TCP connection and resets it at once (TLS ClientHello and
    plain HTTP alike), several tries. gov.si, pisrs.si and poslovanje-sodstva.sodisce.si
    (other IPs) answer. So the judiciary's own hosting is down or resets UK traffic; no
    moved site found. Code unchanged.
  * Terms flag: the EU e-Justice page on Slovenian case law (last updated 2016-12-09) says
    the JSON API at sodnapraksa.si/api2/ may be used only with the Supreme Court's prior
    permission. We use the new portal's own /backend/api (June 2026 relaunch), which has no
    stated terms; whether that rule carries over is unverified.
"""
from __future__ import annotations

import re
from urllib.parse import parse_qs, urlsplit

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from .._http import require_iso as _date
from ..models import (
    Decision,
    DecisionHit,
    LawHit,
    LawText,
    Provision,
    Results,
    Toc,
    TocEntry,
)

SP = "https://sodnapraksa.si/backend/api"
SP_WEB = "https://www.sodnapraksa.si"
PIS = "https://pisrs.si/api"
PIS_WEB = "https://pisrs.si"

# sodnapraksa document types that are court decisions
_COURTS = {
    "vsrs": "Vrhovno sodišče RS (Supreme Court)",
    "viso": "Višja sodišča (higher courts: Ljubljana, Maribor, Celje, Koper)",
    "vdss": "Višje delovno in socialno sodišče (Higher Labour and Social Court)",
    "uprs": "Upravno sodišče RS (Administrative Court)",
}
_FIELDS = ["id", "ecli", "date", "sessionDate", "ordinalNumber", "court", "documentType",
           "coreText"]
_LAW_ID = re.compile(r"^[A-Z]{4}\d+$")


async def _json(method: str, url: str, what: str, **kw):
    try:
        r = await (_http.post if method == "POST" else _http.get)(url, **kw)
    except Exception as e:  # network error
        host = url.split("/")[2]
        raise SourceError(f"{what}: cannot reach {host} ({str(e) or type(e).__name__}); the "
                          "site is down, resetting connections or blocking this network. Retry "
                          f"later or check https://{host} directly", "network") from e
    if r.status_code == 404:
        raise NotFound(f"{what}: not found")
    if r.status_code == 403 and "pisrs.si" in url:
        raise SourceError(f"{what}: PISRS refused the request and asks for its proof-of-work "
                          "bot check, which this server does not solve; try again later", 403)
    if r.status_code != 200:
        raise SourceError(f"{what} failed", r.status_code)
    try:
        return r.json()
    except ValueError as e:
        raise SourceError(f"{what}: unexpected non-JSON reply", r.status_code) from e


# --------------------------------------------------------------------------- #
# Case law
# --------------------------------------------------------------------------- #
_ORD = re.compile(r"^(?:(?P<c>[A-ZČŠŽ]{2,6})\s+)?(?P<t>[A-ZČŠŽ]?[a-zčšž]+)\s+(?P<n>.*\d.*)$")


def _split_ordinal(s: str) -> tuple[str, str]:
    """'VSL sodba III Cp 1870/98' -> ('sodba', 'III Cp 1870/98'); 'Sodba U 938/95' -> ('Sodba', 'U 938/95')."""
    s = _http.clean(s)
    m = _ORD.match(s)
    return (m["t"], m["n"]) if m else ("", s)


def _sp_id(doc: dict) -> str:
    return doc.get("ecli") or str(doc.get("id") or "")


def _sp_url(doc: dict) -> str:
    return f"{SP_WEB}/dokument/{doc.get('documentType') or 'vsrs'}/{doc.get('id')}"


def _sp_date(doc: dict) -> str:
    return _http.iso_date(doc.get("sessionDate") or doc.get("date") or "")


def _hit(doc: dict) -> DecisionHit:
    court = _http.clean(doc.get("court"))
    _, cn = _split_ordinal(doc.get("ordinalNumber") or "")
    snippet = _http.clean(re.sub(r"<[^>]+>", " ", doc.get("coreText") or ""))
    return DecisionHit(id=_sp_id(doc), title=f"{court} {cn}".strip() or _sp_id(doc),
                       court=court, date=_sp_date(doc), case_number=cn,
                       snippet=snippet[:300], url=_sp_url(doc))


# --------------------------------------------------------------------------- #
# Legislation
# --------------------------------------------------------------------------- #
def _law_id(id: str) -> str:
    """'ZAKO1263' | 'zako1263' | 'https://pisrs.si/pregledPredpisa?id=ZAKO1263' -> 'ZAKO1263'."""
    s = (id or "").strip()
    if s.startswith("http"):
        s = (parse_qs(urlsplit(s).query).get("id") or [""])[0]
    s = s.upper()
    if not _LAW_ID.match(s):
        raise BadRequest(f"Unrecognised PISRS id {id!r}. Use the register id, e.g. 'ZAKO1263' "
                         "(Obligacijski zakonik); search_legislation shows it.")
    return s


def _norm_provision(p: str) -> str:
    """'1. člen' | '1' | 'člen 1' | 'čl. 1' | 'art. 1' | '382a' | '382.a člen' -> '1. člen' / '382.a člen'."""
    s = (p or "").strip().lower()
    s = re.sub(r"(article|člen|clen|čl|art)\.?", " ", s)
    s = re.sub(r"\s+", "", s)
    m = re.fullmatch(r"(\d+)\.?([a-zčšž])?\.?", s)
    if not m:
        raise BadRequest(f"Unrecognised provision {p!r}; use e.g. '1. člen' or '382.a člen'.")
    return f"{m[1]}.{m[2]} člen" if m[2] else f"{m[1]}. člen"


def _label(text: str) -> str:
    """Article label from a 'N. člen' element: '1. člen', '382.a člen', '376. člen (črtan)' -> '376. člen'."""
    m = re.match(r"^\s*(\d+)\s*\.\s*([a-zčšž])?\s*\.?\s*člen\b", text or "")
    if not m:
        return ""
    return f"{m[1]}.{m[2]} člen" if m[2] else f"{m[1]}. člen"


def _el_md(el: dict) -> str:
    v = el.get("vsebina") or ""
    t = _http.html_to_md(v) if "<" in v else _http.clean(v)
    if not t or re.fullmatch(r"[-_*\s]*", t):
        return ""
    kind = el.get("struktura")
    if kind in ("del", "poglavje"):
        return f"## {t}"
    if kind in ("oddelek", "pododdelek", "odsek"):
        return f"### {t}"
    if kind == "clen":
        return f"#### {t}" if _label(t) else f"**{t}**"
    if kind == "naslov":
        return f"# {t}"
    return t


class _Law:
    def __init__(self, id: str, meta: dict, npb_id, body: dict | None):
        self.id, self.meta, self.npb_id = id, meta, npb_id
        self.elements: list[dict] = (body or {}).get("besedilo") or []
        self.kazalo: list[dict] = (body or {}).get("kazalo") or []
        self.pos = {e.get("id"): i for i, e in enumerate(self.elements)}

    @property
    def title(self) -> str:
        return _http.clean(self.meta.get("naslov")) or self.id

    @property
    def url(self) -> str:
        return f"{PIS_WEB}/pregledPredpisa?id={self.id}"

    def articles(self) -> list[tuple[dict, str, int, int]]:
        """(kazalo entry, label or '', start index, end index) for every TOC entry, in order."""
        starts = [(k, self.pos.get(k.get("idStrukturniElement"))) for k in self.kazalo]
        starts = [(k, i) for k, i in starts if i is not None]
        out, seen = [], set()
        for n, (k, i) in enumerate(starts):
            end = starts[n + 1][1] if n + 1 < len(starts) else len(self.elements)
            lab = ""
            if k.get("struktura") == "clen":
                lab = next((x for e in self.elements[i:end] if e.get("struktura") == "clen"
                            and (x := _label(e.get("vsebina") or ""))), "")
                if lab in seen:   # quoted articles in amending acts' transitional provisions
                    lab = ""
                seen.add(lab)
            out.append((k, lab, i, max(end, i + 1)))
        return out

    def render(self, a: int = 0, b: int | None = None) -> str:
        return "\n\n".join(t for e in self.elements[a:b] if (t := _el_md(e)))


_laws: dict[str, _Law] = {}


async def _law(id: str) -> _Law:
    key = _law_id(id)
    if key in _laws:
        return _laws[key]
    d = await _json("GET", f"{PIS}/rezultat/zbirka/id/{key}", "PISRS record")
    data = d.get("data") or {}
    meta = data.get("evidencniPodatki")
    if not meta:
        raise NotFound(f"No regulation {key!r} in PISRS")
    versions = (data.get("besedilo") or {}).get("npbVerzije") or []
    if not versions:
        raise NotFound(f"PISRS has no consolidated text for {key} ({meta.get('naslov', '')}); "
                       f"read the Uradni list publication at {PIS_WEB}/pregledPredpisa?id={key}")
    npb = versions[-1]["id"]   # ascending: Osnovni, NPB 1, ..., NPB n
    body = await _json("GET", f"{PIS}/rezultat/neuradno-precisceno-besedilo/{npb}/details",
                       "PISRS consolidated text")
    return _http.lru_put(_laws, key, _Law(key, meta, npb, body.get("data")), 3)


class Slovenia(Jurisdiction):
    code = "si"
    name = "Slovenia"
    languages = ("sl",)
    aliases = ("svn", "slovenia", "slovenija")
    sources = (
        Source(
            name="Sodna praksa (sodnapraksa.si, Supreme Court of Slovenia)",
            url=SP_WEB,
            covers=("caselaw",),
            licence="unknown: no terms of use published on sodnapraksa.si; court decisions are "
                    "official texts not protected by copyright (ZASP art. 9). The journal "
                    "articles also in the database (SOPM/SOSC) are copyrighted and not used",
            commercial_use=None,
            ai_use=None,
            auth="none (Keycloak login only for favourites/notes, not used)",
            rate_limit="unknown, none documented; no 429 in ~15 requests (2026-11); using 1 s spacing",
            terms_url=f"{SP_WEB}/zasebnost-in-piskotki",
        ),
        Source(
            name="PISRS (Pravni informacijski sistem RS, Government of Slovenia)",
            url=PIS_WEB,
            covers=("legislation",),
            licence="unknown: the PISRS terms page (/pogoji-uporabe) is an unfilled placeholder "
                    "(2026-11-05); legislation is not protected by copyright (ZASP art. 9). "
                    "Texts are unofficial consolidations (NPB); only Uradni list RS is authentic",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown, none documented; no 429 in ~15 requests (2026-11); using 1 s "
                       "spacing. A 403 triggers a proof-of-work bot check, which we do not solve",
            terms_url=f"{PIS_WEB}/pogoji-uporabe",
        ),
    )
    caselaw_filters = {
        "court": "court collection: 'vsrs' (Supreme Court), 'viso' (higher courts), "
                 "'vdss' (Higher Labour and Social Court), 'uprs' (Administrative Court)",
        "date_from": "decided on or after, YYYY-MM-DD",
        "date_to": "decided on or before, YYYY-MM-DD",
        "sort": "'relevance' (default) or 'date' (newest first)",
    }
    legislation_filters = {
        "fulltext": "'yes' to search the text as well as titles (default: titles only)",
    }
    min_interval = {"sodnapraksa.si": 1.0, "pisrs.si": 1.0}
    notes = ("Case law: Supreme, higher, labour-appeal and Administrative Court decisions "
             "(anonymised, selected; no first-instance or Constitutional Court). Laws: PISRS "
             "unofficial consolidated texts, ids like 'ZAKO1263' (OZ), articles as '1. člen'.")
    gaps = (
        "Constitutional Court (us-rs.si): blocks our client (403, 2026-11-05)",
        ("First-instance courts: not in sodnapraksa.si (selected higher-court decisions only); not "
         "researched yet"),
        "PISRS when it serves its proof-of-work challenge (403): bot check, not solved",
        ("Authentic legislation (Uradni list RS): PISRS consolidations are unofficial; Uradni list "
         "not researched yet"),
        ("sodnapraksa.si unreachable since 2026-11-10 (connection reset on 80/443, also sodisce.si "
         "on the same network): outage or block of UK traffic; case law unavailable while it lasts"),
    )
    samples = {
        "caselaw_query": "najemna pogodba",
        "decision_id": "ECLI:SI:VSRS:1999:U.938.95",
        "legislation_query": "obligacijski zakonik",
        "law_id": "ZAKO1263",
        "provision": "1. člen",
    }

    # ----------------------------------------------------------------- caselaw
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        court = str(filters.get("court") or "").lower()
        if court and court not in _COURTS:
            raise BadRequest(f"court must be one of {', '.join(_COURTS)}, got {court!r}")
        types = [court] if court else list(_COURTS)
        fq = ["docType:(" + " OR ".join(f'"{t}"' for t in types) + ")"]
        lo = _date(filters["date_from"], "date_from") if filters.get("date_from") else "*"
        hi = _date(filters["date_to"], "date_to") if filters.get("date_to") else "*"
        if lo != "*" or hi != "*":
            fq.append(f"date:[{lo + 'T00:00:00Z' if lo != '*' else '*'} TO "
                      f"{hi + 'T23:59:59Z' if hi != '*' else '*'}]")
        sort = str(filters.get("sort") or "relevance").lower()
        if sort not in ("relevance", "date"):
            raise BadRequest("sort must be 'relevance' or 'date'")
        body = {"simpleSearch": True, "query": {"q": query or "*"}, "page": max(0, page - 1),
                "pageSize": limit, "sortField": "score" if sort == "relevance" else "date",
                "sortDirection": "DESC", "filterQueries": fq, "fieldList": _FIELDS}
        d = await _json("POST", f"{SP}/search/documents", "sodnapraksa.si search", json=body)
        if d.get("warnings"):
            raise SourceError(f"sodnapraksa.si search: {d['warnings'][0]}", 200)
        return Results(items=[_hit(x) for x in (d.get("docs") or [])[:limit]],
                       total=d.get("hits"),
                       note="Selected, anonymised decisions of the Supreme, higher, labour-appeal "
                            "and Administrative Courts; Solr query syntax works.")

    async def get_decision(self, id):
        s = (id or "").strip()
        if s.isdigit():
            num = s
        elif s.upper().startswith("ECLI:SI:"):
            d = await _json("GET", f"{SP}/search/documents", "sodnapraksa.si ECLI lookup",
                            params=[("query", f'ecli:"{s.upper()}"'), ("simpleSearch", "false"),
                                    ("page", 0), ("pageSize", 1), ("fieldList", "id")])
            if not d.get("docs"):
                raise NotFound(f"No decision {s!r} on sodnapraksa.si")
            num = str(d["docs"][0]["id"])
        else:
            raise BadRequest(f"Use an ECLI (ECLI:SI:...) or a sodnapraksa.si numeric id, got {id!r}")
        doc = await _json("GET", f"{SP}/search/documents/orders/{num}", "sodnapraksa.si decision")
        if not doc.get("id"):
            raise NotFound(f"No decision {s!r} on sodnapraksa.si")
        court = _http.clean(doc.get("court"))
        kind, cn = _split_ordinal(doc.get("ordinalNumber") or "")
        core = _http.html_to_md(doc.get("coreText") or "")
        parts = []
        for head, key in (("Izrek", "ruling"), ("Obrazložitev", "motivation")):
            if body := _http.html_to_md(doc.get(key) or ""):
                parts.append(f"## {head}\n\n{body}")
        if not parts and core:   # some entries carry only the headnote
            parts.append(f"## Jedro\n\n{core}")
        laws = "; ".join(_http.clean(f"{x.get('krap') or x.get('name', '')} {x.get('valueType', '')} "
                                     f"{x.get('value', '')}") for x in doc.get("legislation") or [])
        meta = {"Type": kind, "Department": doc.get("department") or "",
                "Areas": ", ".join(doc.get("areas") or []),
                "Keywords": ", ".join(doc.get("keywords") or []),
                "Legal basis": laws, "Registry number": doc.get("registryNumber") or ""}
        return Decision(id=_sp_id(doc), title=f"{court} {cn}".strip(), text="\n\n".join(parts),
                        url=_sp_url(doc), court=court, date=_sp_date(doc), case_number=cn,
                        summary=core, metadata={k: _http.clean(v) for k, v in meta.items() if v})

    # ------------------------------------------------------------- legislation
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        ft = str(filters.get("fulltext") or "no").lower()
        if ft not in ("yes", "no", "true", "false"):
            raise BadRequest("fulltext must be 'yes' or 'no'")
        start = (page - 1) * limit
        if start + limit > 200:
            raise BadRequest("PISRS pages by cursor, 10 rows per request; only the first 200 "
                             "results are reachable here. Narrow the query instead.")
        body = {"simpleSearch": True, "nazivZbirke": ["Register predpisov"],
                "besedilo": {"word1": query, "word1InTitle": True,
                             "word1InContent": ft in ("yes", "true")}}
        cursor, d, rows = "*", {}, []
        while len(rows) < start + limit:   # Solr cursor: walk 10 rows at a time
            d = (await _json("POST", f"{PIS}/filter/filter", "PISRS search",
                             params={"cursorMark": cursor}, json=body)).get("data") or {}
            rows += d.get("seznam") or []
            nxt = d.get("nextCursorMark")
            if not d.get("seznam") or not nxt or nxt == cursor:
                break
            cursor = nxt
        rows = rows[start:start + limit]
        items = [LawHit(id=x["zunanjiId"], title=_http.clean(x.get("nazivAkta")) or x["zunanjiId"],
                        number=x.get("sop") or "",
                        date=x.get("datumObjave") or "",
                        status=((x.get("semafor") or {}).get("naziv") or ""),
                        url=f"{PIS_WEB}/pregledPredpisa?id={x['zunanjiId']}")
                 for x in rows if x.get("zunanjiId")]
        return Results(items=items, total=d.get("numOfAllResultsForIndex"),
                       note="PISRS returns 10 per page; titles only unless filters={'fulltext': 'yes'}.")

    async def get_legislation_toc(self, id):
        law = await _law(id)
        entries = []
        for k, lab, _, _ in law.articles():
            name = _http.clean(k.get("kazaloIme"))
            if lab and name.endswith(lab):
                name = f"{lab} – {name[:-len(lab)].strip()}".rstrip(" –")
            entries.append(TocEntry(title=name, level=int(k.get("zamik") or 0), provision=lab))
        return Toc(id=law.id, title=law.title, url=law.url, entries=entries)

    async def get_legislation_provision(self, id, provision):
        want = _norm_provision(provision)
        law = await _law(id)
        for _, lab, a, b in law.articles():
            if lab == want:
                return Provision(law_id=law.id, law_title=law.title, provision=want,
                                 text=law.render(a, b), url=law.url)
        raise NotFound(f"{want} not found in {law.id} ({law.title})")

    async def get_legislation_text(self, id):
        law = await _law(id)
        m = law.meta
        meta = {"Abbreviation": m.get("kratica") or "", "Type": m.get("vrstaAkta") or "",
                "Uradni list RS": m.get("ulStLeto") or "", "Published": m.get("objavljeno") or "",
                "In force from": m.get("veljaOd") or "",
                "Status": (m.get("semafor") or {}).get("naziv") or "",
                "Amendments": _http.clean(re.sub(r"<[^>]+>", "", m.get("citat") or ""))}
        return LawText(id=law.id, title=law.title, text=law.render(), url=law.url,
                       metadata={k: v for k, v in meta.items() if v})
