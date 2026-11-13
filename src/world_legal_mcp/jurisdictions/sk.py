"""Slovakia: case law from the Supreme Court open-data API, legislation from Slov-Lex.

Gotchas this code encodes:
  * Case law is the Najvyšší súd SR (Supreme Court) only, via its documented open-data
    API www.nsud.sk/ws/opendata.php (no auth, "free for any purpose, commercial or not").
    searchDecision returns only a bare list of internal ids (no paging, no metadata,
    no order), so we sort them newest-id-first and call getDecision for the requested
    page: one request per hit. Its date filters (art_datum_od/do) are silently ignored,
    so we offer none. art_obsah matches the text as a phrase (no stemming).
    getDecision returns its own "ID" empty; the public id is the ECLI, resolved back
    with searchDecision&art_ecli.
  * The Ministry of Justice portal (all courts) runs on obcan.justice.sk/pilot/api/…,
    and obcan.justice.sk/robots.txt disallows /pilot, so lower courts are not covered.
  * Slov-Lex search is the backend of the www.slov-lex.sk SPA:
    api-gateway.slov-lex.sk/vyhladavanie/predpisZbierky/rozsirene (Solr-like JSON).
    `text=` is full-text with good relevance; `cislo=40/1964` looks up one law and
    its `iri` is the version in force today (/SK/ZZ/1964/40/20260731).
  * The consolidated text is the static mirror static.slov-lex.sk/static{iri}.html,
    clean nested divs (class "paragraf Skupina", id "paragraf-1"…). Served without a
    charset, so we decode UTF-8 ourselves. The Constitution uses "ustavnyclanok" (Čl.).
"""
from __future__ import annotations

import re

from lxml import html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

NSUD = "https://www.nsud.sk"
NSUD_API = f"{NSUD}/ws/opendata.php"
SLOVLEX = "https://www.slov-lex.sk"
SL_API = "https://api-gateway.slov-lex.sk/vyhladavanie/predpisZbierky/rozsirene"
SL_STATIC = "https://static.slov-lex.sk/static"
COURT = "Najvyšší súd Slovenskej republiky"

_KOLEGIUM = {"1": "Občianskoprávne", "2": "Obchodnoprávne", "3": "Správne", "4": "Trestnoprávne"}
_ECLI = re.compile(r"^ECLI:SK:NSSR:\d{4}:[\w.]+$", re.I)

# structural units -> markdown heading level; provision units; everything else is body
_STRUCT = {"cast": 2, "hlava": 2, "diel": 3, "oddiel": 3, "pododdiel": 3, "skupinaParagrafov": 4}
_PROV = ("paragraf", "clanok", "ustavnyclanok")


async def _get(url: str, what: str, **kw):
    try:
        r = await _http.get(url, **kw)
    except Exception as e:  # network error
        raise SourceError(f"{what}: {e}", "network") from e
    if r.status_code == 404:
        raise NotFound(f"{what}: not found")
    if r.status_code != 200:
        raise SourceError(f"{what} failed", r.status_code)
    return r


async def _json(url: str, what: str, **kw):
    r = await _get(url, what, **kw)
    try:
        return r.json()
    except ValueError as e:
        raise SourceError(f"{what}: unexpected non-JSON reply", r.status_code) from e


# --------------------------------------------------------------------------- #
# Case law (Supreme Court open data)
# --------------------------------------------------------------------------- #
def _subject_phrases(q: str) -> list[str]:
    """The query, then its trailing word groups of 2+ words ('výpoveď z nájmu bytu' -> 'z nájmu bytu',
    'nájmu bytu'), for matching against subject lines."""
    w = q.split()
    return [" ".join(w[i:]) for i in range(max(len(w) - 1, 1))] if len(w) > 1 else [q]


def _stem(w: str) -> str:
    """Crude stem for the subject-line search, which matches substrings: drop the last 2 letters of long words."""
    return w[:-2] if len(w) > 5 else w


def _decision_url(d: dict) -> str:
    """The court's own page for the file number (slug = file number, lower-case, no '/')."""
    slug = re.sub(r"[^a-z0-9]", "", (d.get("cislo") or "").lower())
    if slug and (d.get("cislo") or "").isascii():
        return f"{NSUD}/rozhodnutia/{slug}/"
    if d.get("subor"):
        return f"{NSUD}/data/att/{d['subor']}"
    return f"{NSUD}/rozhodnutia/"


async def _nsud_decision(nid: str) -> dict:
    d = await _json(NSUD_API, "nsud.sk decision", params=[("getDecision", ""), ("id", nid)])
    if not isinstance(d, dict) or not (d.get("ecli") or d.get("cislo")):
        raise NotFound(f"No Supreme Court decision with internal id {nid}")
    return d


def _nsud_text(obsah: str) -> str:
    paras = [_http.clean(p) for p in re.split(r"\n\s*\n|\n", obsah or "")]
    return "\n\n".join(p for p in paras if p)


# --------------------------------------------------------------------------- #
# Legislation (Slov-Lex)
# --------------------------------------------------------------------------- #
def _parse_law_id(id: str) -> tuple[str, str, str]:
    """'40/1964 Zb.' | '40/1964' | 'SK/ZZ/1964/40' | '/SK/ZZ/1964/40/20260731' -> (year, n, version)."""
    s = _http.clean(id)
    m = re.match(r"^(?:č\.\s*)?(\d+)\s*/\s*(\d{4})(?:\s*(?:Zb\.?|Z\.\s*z\.?))?$", s, re.I)
    if m:
        return m.group(2), m.group(1), ""
    m = re.match(r"^/?SK/ZZ/(\d{4})/(\d+)(?:/(\d{8}|vyhlasene_znenie))?/?$", s, re.I)
    if m:
        return m.group(1), m.group(2), m.group(3) or ""
    raise BadRequest(f"Unrecognised Slovak law id {id!r}. Use the collection citation, "
                     "e.g. '40/1964 Zb.' or '311/2001 Z. z.' (also '40/1964' or 'SK/ZZ/1964/40').")


def _norm_provision(p: str) -> str:
    """'§ 2' | '2' | 'par. 2' | '§2a' -> '§ 2a';  'Čl. 5' | 'čl 5' | 'art. 5' -> 'Čl. 5'."""
    s = _http.clean(p)
    m = re.match(r"^(?:čl(?:ánok)?|cl|art(?:icle)?)\.?\s*(\d+[a-z]*)$", s, re.I)
    if m:
        return f"Čl. {m.group(1).lower()}"
    s = re.sub(r"^(§+|par\.?|paragraf)\s*", "", s, flags=re.I).strip()
    if not re.match(r"^\d+[a-z]*$", s, re.I):
        raise BadRequest(f"Unrecognised provision {p!r}; use e.g. '§ 2' (or 'Čl. 5' for articles).")
    return f"§ {s.lower()}"


def _kind(el) -> str:
    cls = (el.get("class") or "").split()
    return cls[0] if len(cls) > 1 and cls[1] == "Skupina" else ""


def _txt(el) -> str:
    """Element text with footnote markers kept as ^1)."""
    for a in el.xpath('.//a[sup]'):
        a.text, a[:] = f"^{_http.text(a)}", []
    return _http.text(el)


def _parts(el):
    """(oznacenie, nadpis, texts, sub-units, closing texts) of one Skupina div."""
    ozn = nad = ""
    texts, subs, tail = [], [], []
    for c in el:
        if not isinstance(c.tag, str) or c.tag != "div":
            continue
        cls = c.get("class") or ""
        if _kind(c):
            subs.append(c)
        elif cls.endswith("Oznacenie"):
            ozn = _txt(c)
        elif "Nadpis" in cls:
            nad = _txt(c)
        elif cls.split()[:1] in (["text"], ["text2"]):
            t = _txt(c)
            if t:  # text2 is closing text (e.g. signatures): it goes after the sub-units
                (tail if cls.startswith("text2") else texts).append(t)
    return ozn, nad, texts, subs, tail


def _label(el) -> str:
    return _parts(el)[0]


def _render(el, out: list[str]) -> None:
    kind = _kind(el)
    ozn, nad, texts, subs, tail = _parts(el)
    if kind in _STRUCT or kind in _PROV:
        level = _STRUCT.get(kind, 5) if kind in _STRUCT else 4
        head = " – ".join(x for x in (ozn, nad) if x)
        if head:
            out.append(f"{'#' * level} {head}")
        out.extend(texts)
    elif kind == "predpis":
        out.extend(texts)
    else:  # odsek, pismeno, bod, ...: label inline with its first text
        if ozn and texts:
            texts[0] = f"{ozn} {texts[0]}"
        elif ozn or nad:
            texts.insert(0, " ".join(x for x in (ozn, nad) if x))
        out.extend(texts)
    for s in subs:
        _render(s, out)
    out.extend(tail)


class _Law:
    def __init__(self, doc: dict, root):
        self.doc = doc
        self.root = root
        self.predpis = root.get_element_by_id("predpis")
        self._provs: dict[str, object] | None = None

    @property
    def id(self) -> str:
        return _http.clean(self.doc.get("cislo") or self.doc["iri"])

    @property
    def title(self) -> str:
        return f"{self.id} {self.doc.get('nazov') or ''}".strip()

    @property
    def url(self) -> str:
        y, n = self.doc["iri"].split("/")[3:5]
        return f"{SLOVLEX}/ezbierky/pravne-predpisy/SK/ZZ/{y}/{n}/"

    @property
    def version_url(self) -> str:
        return f"{SL_STATIC}{self.doc['iri']}.html"

    @property
    def as_of(self) -> str:
        v = self.doc["iri"].rsplit("/", 1)[-1]
        return f"{v[:4]}-{v[4:6]}-{v[6:]}" if re.fullmatch(r"\d{8}", v) else ""

    def provisions(self) -> dict:
        if self._provs is None:
            self._provs = {}
            for el in self.predpis.iter("div"):
                if _kind(el) in _PROV:
                    lab = _label(el)
                    try:
                        key = _norm_provision(lab)
                    except BadRequest:
                        continue
                    self._provs.setdefault(key, el)
        return self._provs


_laws: dict[str, _Law] = {}   # iri -> parsed version, small in-process cache


async def _law(id: str) -> _Law:
    year, num, version = _parse_law_id(id)
    d = await _json(SL_API, "Slov-Lex lookup", params={"cislo": f"{num}/{year}", "rows": 10, "start": 0})
    prefix = f"/SK/ZZ/{year}/{num}/"
    doc = next((x for x in d.get("docs") or [] if (x.get("iri") or "").startswith(prefix)), None)
    if doc is None:
        raise NotFound(f"No law {num}/{year} in Slov-Lex")
    if version:
        doc = {**doc, "iri": prefix + version}
    iri = doc["iri"]
    if iri not in _laws:
        r = await _get(f"{SL_STATIC}{iri}.html", "Slov-Lex text")
        root = lhtml.fromstring(r.content.decode("utf-8", "replace"))
        try:
            law = _Law(doc, root)
        except KeyError as e:
            raise SourceError("Slov-Lex text: no #predpis in page", r.status_code) from e
        _http.lru_put(_laws, iri, law, 4)
    return _laws[iri]


class Slovakia(Jurisdiction):
    code = "sk"
    name = "Slovakia"
    languages = ("sk",)
    aliases = ("svk", "slovakia", "slovak republic", "slovensko")
    sources = (
        Source(
            name="Najvyšší súd SR open data (Supreme Court)",
            url=f"{NSUD}/opendata/",
            covers=("caselaw",),
            licence="open data, stated on nsud.sk/opendata: free for anyone, on equal terms, "
                    "for any purpose, commercial or non-commercial; no named licence",
            commercial_use=True,
            ai_use=None,
            auth="none",
            rate_limit="unknown, none documented; no 429 in ~30 requests (2026-11); using 1 s spacing",
            terms_url=f"{NSUD}/opendata/",
        ),
        Source(
            name="Slov-Lex (Ministry of Justice)",
            url=SLOVLEX,
            covers=("legislation",),
            licence="unknown: no terms page found; legal texts are excluded from copyright "
                    "(§ 5 of the Slovak Copyright Act 185/2015 Z. z.). The search API behind "
                    "www.slov-lex.sk is undocumented",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown, none documented; no 429 in ~25 requests (2026-11); using 1 s spacing",
            terms_url=SLOVLEX,
        ),
    )
    caselaw_filters = {
        "case_number": "file number (spisová značka) without spaces, e.g. '4Cdo/154/2025'",
        "subject": "words in the subject line (merito veci), e.g. 'nájmu'",
    }
    legislation_filters = {
        "year": "year of the collection (ročník), e.g. '2001'",
    }
    min_interval = {"www.nsud.sk": 1.0, "api-gateway.slov-lex.sk": 1.0, "static.slov-lex.sk": 1.0}
    notes = ("Case law: Supreme Court (Najvyšší súd SR) only, anonymised; lower courts are on "
             "obcan.justice.sk, whose API robots.txt forbids. Laws: cite as '40/1964 Zb.' or "
             "'311/2001 Z. z.', provisions as '§ 2' (Constitution: 'Čl. 1').")
    gaps = (
        "Lower courts (obcan.justice.sk, all courts): robots.txt disallows its /pilot API",
        "Constitutional Court: not researched yet",
        ("Supreme Administrative Court (Najvyšší správny súd) and the administrative courts: not "
         "searched (only the obcan.justice.sk portal is known, robots.txt disallows /pilot)"),
        ("Supreme Court decisions by date: the open-data API ignores its date filters, so none are "
         "offered"),
    )
    samples = {
        "caselaw_query": "nájom",
        "decision_id": "ECLI:SK:NSSR:2021:5019200331.1",
        "legislation_query": "občiansky zákonník",
        "law_id": "40/1964 Zb.",
        "provision": "§ 2",
    }

    # ----------------------------------------------------------------- caselaw
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        params = [("searchDecision", "")]
        args = {}
        if (query or "").strip():
            args["art_obsah"] = query.strip()
        if v := filters.get("case_number"):
            v = str(v).strip()
            if not re.fullmatch(r"[\wÀ-ž]+(?:/[\wÀ-ž]+)?(?:/\d{4})?", v):
                raise BadRequest(f"case_number must look like '4Cdo/154/2025' (no spaces), got {v!r}")
            args["nazov"] = v
        if v := filters.get("subject"):
            args["art_merito"] = str(v).strip()
        if not args:
            raise BadRequest("Give a query or a filter (case_number, subject).")
        ids = await _json(NSUD_API, "nsud.sk search", params=params + list(args.items()))
        if not isinstance(ids, list):
            raise SourceError("nsud.sk search: unexpected reply", 200)
        ids = sorted({str(i) for i in ids if str(i).isdigit()}, key=int, reverse=True)
        words = [w for w in (args.get("art_obsah") or "").split() if len(w) > 2]
        widened = False
        n_subj = 0
        if not ids and len(words) > 1 and "art_merito" not in args:
            # the phrase is not in any text: decisions containing every word, anywhere in the text
            sets = []
            for w in words:
                r = await _json(NSUD_API, "nsud.sk search",
                                params=params + [("art_obsah", w)] + [(k, v) for k, v in args.items()
                                                                      if k not in ("art_obsah",)])
                sets.append({str(i) for i in r if str(i).isdigit()} if isinstance(r, list) else set())
            ids = sorted(set.intersection(*sets), key=int, reverse=True)
            widened = bool(ids)
            if len(ids) > 1:
                # words in the text alone rank nothing: put decisions whose subject line has a query
                # word (stem: 'výpov' finds 'výpoveďou') first, the more words the higher
                score = dict.fromkeys(ids, 0)
                for w in words:
                    r = await _json(NSUD_API, "nsud.sk search",
                                    params=params + [("art_merito", _stem(w))])
                    for i in {str(i) for i in r} if isinstance(r, list) else ():
                        if i in score:
                            score[i] += 1
                ids.sort(key=lambda i: -score[i])
                n_subj = sum(1 for v in score.values() if v)
        if args.get("art_obsah") and "art_merito" not in args:
            # no ranking at the source, and a phrase in the text misses inflected subject lines
            # ("výpovede z nájmu bytu"): add decisions whose subject line has the phrase or its
            # trailing words, longest phrase first, then the rest newest-first
            ids, rest = [], ids
            for ph in _subject_phrases(args["art_obsah"]):
                top = await _json(NSUD_API, "nsud.sk search", params=params + [("art_merito", ph)])
                if isinstance(top, list):
                    ids += sorted({str(i) for i in top if str(i).isdigit()} - set(ids), key=int,
                                  reverse=True)
            ids += [i for i in rest if i not in ids]
        items = []
        for nid in ids[(page - 1) * limit: page * limit]:
            d = await _nsud_decision(nid)
            cn = d.get("cislo") or ""
            subj = _http.clean(d.get("merito"))
            items.append(DecisionHit(
                id=d.get("ecli") or nid, title=f"{COURT}, {cn}" + (f" – {subj}" if subj else ""),
                court=COURT, date=_http.iso_date(d.get("datum")), case_number=cn,
                snippet=subj, url=_decision_url(d)))
        wide = (f"No decision has '{args['art_obsah']}' as an exact phrase, so these contain all of the "
                f"words {words} somewhere in the text (not necessarily together; endings must match "
                "exactly, e.g. 'zamestnanec' will not find 'zamestnanca'). " +
                (f"Only the first {n_subj} have" if n_subj else "None has") +
                " a query word in the subject line; the rest merely contain "
                "the words and are often about something else, so judge each by its subject line, or "
                "search a single distinctive word. " if widened else "")
        return Results(items=items, total=len(ids),
                       note=wide + "Supreme Court only; the source has no ranking: decisions with the phrase in "
                            "the subject line (or its last words) come first, then the rest, each group by the "
                            "source's record number (newest-added first, NOT by decision date: old and "
                            "recent decisions are mixed and the source cannot sort or filter by date, so "
                            "check each Date); the "
                            "text is matched as a phrase, without stemming; combine query and "
                            "'subject' only to intersect, a subject-only search is wider.")

    async def get_decision(self, id):
        s = (id or "").strip()
        if s.isdigit():
            nid = s
        elif _ECLI.match(s):
            ids = await _json(NSUD_API, "nsud.sk lookup",
                              params=[("searchDecision", ""), ("art_ecli", s.upper())])
            if not ids:
                raise NotFound(f"No decision {s!r} in the Supreme Court open data")
            nid = str(ids[0])
        elif re.fullmatch(r"[\wÀ-ž]+/\d+/\d{4}", s):
            ids = await _json(NSUD_API, "nsud.sk lookup",
                              params=[("searchDecision", ""), ("nazov", s)])
            if not ids:
                raise NotFound(f"No Supreme Court decision with file number {s!r}")
            nid = str(max(int(i) for i in ids))
        else:
            raise BadRequest(f"Use a Supreme Court ECLI (ECLI:SK:NSSR:...), a file number like "
                             f"'3Cdo/128/2018' or the numeric open-data id, got {id!r}")
        d = await _nsud_decision(nid)
        cn = d.get("cislo") or ""
        meta = {"Kolégium": _KOLEGIUM.get(str(d.get("kolegium")), ""),
                "Senát": d.get("senat") or "", "Sudca": d.get("sudca") or "",
                "Merito veci": _http.clean(d.get("merito")),
                "PDF": f"{NSUD}/data/att/{d['subor']}" if d.get("subor") else ""}
        return Decision(id=d.get("ecli") or nid, title=f"{COURT}, {cn}",
                        text=_nsud_text(d.get("obsah")), url=_decision_url(d), court=COURT,
                        date=_http.iso_date(d.get("datum")), case_number=cn,
                        metadata={k: v for k, v in meta.items() if v})

    # ------------------------------------------------------------- legislation
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        params = {"text": query, "rows": limit, "start": (page - 1) * limit}
        if y := filters.get("year"):
            if not re.fullmatch(r"\d{4}", str(y)):
                raise BadRequest(f"year must be YYYY, got {y!r}")
            params["rocnik"] = str(y)
        d = await _json(SL_API, "Slov-Lex search", params=params)
        today = _http.today()
        items = []
        for x in d.get("docs") or []:
            cislo = _http.clean(x.get("cislo"))
            od, do = (x.get("ucinnyOd") or "")[:10], (x.get("ucinnyDo") or "")[:10]
            status = ("not yet in force" if od and od > today
                      else "no longer in force" if do and do < today else "in force")
            y, n = (x.get("iri") or "/SK/ZZ/0/0").split("/")[3:5]
            items.append(LawHit(id=cislo or x["iri"], title=_http.clean(x.get("nazov")) or cislo,
                                type=x.get("typPredp_value") or "",
                                number=cislo, date=(x.get("vyhlaseny") or "")[:10], status=status,
                                url=f"{SLOVLEX}/ezbierky/pravne-predpisy/SK/ZZ/{y}/{n}/"))
        return Results(items=items, total=d.get("numFound"))

    async def get_legislation_toc(self, id):
        law = await _law(id)
        entries: list[TocEntry] = []

        def walk(el, depth):
            for c in el:
                if not isinstance(c.tag, str):
                    continue
                k = _kind(c)
                if k in _STRUCT:
                    ozn, nad, *_ = _parts(c)
                    entries.append(TocEntry(title=" – ".join(x for x in (ozn, nad) if x), level=depth))
                    walk(c, depth + 1)
                elif k in _PROV:
                    ozn, nad, *_ = _parts(c)
                    try:
                        prov = _norm_provision(ozn)
                    except BadRequest:
                        prov = ""
                    entries.append(TocEntry(title=f"{ozn} – {nad}" if nad else ozn,
                                            level=depth, provision=prov))
                elif k == "" and c.tag == "div" and not (c.get("class") or "").startswith("text"):
                    walk(c, depth)

        walk(law.predpis, 0)
        return Toc(id=law.id, title=law.title, url=law.url, entries=entries)

    async def get_legislation_provision(self, id, provision):
        want = _norm_provision(provision)
        law = await _law(id)
        el = law.provisions().get(want)
        if el is None:
            raise NotFound(f"{want} not found in {law.id}")
        out: list[str] = []
        _render(el, out)
        return Provision(law_id=law.id, law_title=law.title, provision=want,
                         text="\n\n".join(out), url=f"{law.version_url}#{el.get('id')}",
                         as_of=law.as_of)

    async def get_legislation_text(self, id):
        law = await _law(id)
        out: list[str] = []
        _render(law.predpis, out)
        for part, head in (("prilohy", "Prílohy"), ("poznamky", "Poznámky")):
            try:
                el = law.root.get_element_by_id(part)
            except KeyError:
                continue
            body = _http.html_to_md(lhtml.tostring(el, encoding="unicode"))
            if body:
                out.append(f"## {head}\n\n{body}")
        meta = {"Version": law.doc["iri"], "Type": law.doc.get("typPredp_value") or "",
                "Published": (law.doc.get("vyhlaseny") or "")[:10]}
        return LawText(id=law.id, title=law.title, text="\n\n".join(out), url=law.url,
                       as_of=law.as_of, metadata={k: v for k, v in meta.items() if v})
