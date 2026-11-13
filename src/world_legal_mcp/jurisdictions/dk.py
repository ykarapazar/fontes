"""Denmark: legislation from Retsinformation (Civilstyrelsen). No case law.

Gotchas this code encodes:
  * A document is addressed by its ELI path: `lta/2016/193` (Lovtidende A, year,
    number), also `ltb`, `ltc`, `mt`, `retsinfo`, `fob`, `ft/<accn>` and
    `accn/<accession number>`. `<ELI>/xml` is the official LexDania XML.
  * Search uses the website's own JSON (`/api/documentsearch?t=&ps=&page=`),
    which is undocumented; `page` is 0-based. `h=false` drops historical versions; without it the
    old consolidations of the same law fill the first pages.
  * Laws are republished as consolidations (LBK, "lovbekendtgørelse"). Each LBK
    is a snapshot: later amending acts are listed in the XML <Meta><Change>
    elements but are NOT worked into the text until the next LBK. We say so.
  * Older documents (e.g. Grundloven 1953) have an XML with metadata only. For
    those the text comes from the site's own `POST /api/document/eli/...`
    (body {"isRawHtml": false}), whose `documentHtml` is split on "§ N.".
  * In an LBK, <Ikraft> blocks quote the commencement sections of amending acts
    ("§ 60. Loven træder i kraft ..."). They are kept in the full text but are
    not provisions of this law, so they get no TOC label.
  * Case law: Domsdatabasen (Domstolsstyrelsen) gives programmatic access only
    after an approved application (bekendtgørelse om Domsdatabasen § 5), and
    domstol.dk sits behind a Cloudflare challenge; neither is used.
"""
from __future__ import annotations

import re

from lxml import etree

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import LawHit, LawText, Provision, Results, Toc, TocEntry

RI = "https://www.retsinformation.dk"
_ID = re.compile(r"^(?:(?:lta|ltb|ltc|mt|retsinfo|fob)/\d{4}/\d+|(?:ft|accn)/[A-Za-z0-9]{5,})$")
_STRUCTURAL_SKIP = {"Ikraft"}
_cache: dict = {}


def _norm_id(id: str) -> str:
    s = re.sub(r"^https?://(www\.)?retsinformation\.dk", "", (id or "").strip(), flags=re.I).strip("/")
    s = re.sub(r"/(xml|html|pdf|rawhtml|dan(/html)?)$", "", s, flags=re.I)
    s = re.sub(r"^eli/", "", s, flags=re.I)
    if re.fullmatch(r"[A-Z]\d{11}", s):
        s = "accn/" + s
    s = re.sub(r"^[A-Za-z]+", lambda m: m[0].lower(), s)
    if not _ID.match(s):
        raise BadRequest(f"{id!r} is not a Retsinformation ELI id. Use the id from search_legislation, "
                         "e.g. 'lta/2016/193', a retsinformation.dk/eli/... URL, or an accession "
                         "number like 'A20160019329'.")
    return s


def _key(label: str) -> str:
    """'§ 7 a.' / '7a' / 'par. 7 a' -> '7a'."""
    s = re.sub(r"^\s*(paragraf|par\.?|section|sec\.?|§+)\s*", "", label.strip().lower())
    return re.sub(r"[\s.§]", "", s)


def _label(explicatus: str) -> str:
    return _http.clean(explicatus).rstrip(".").replace("§", "§ ").replace("§  ", "§ ").replace("§ §", "§§")


# --------------------------------------------------------------------------- #
# LexDania XML -> markdown blocks
# --------------------------------------------------------------------------- #
def _table(el) -> str:
    rows = [[_http.text(td) for td in tr if _http.localname(td) == "Td"] for tr in el.iter("Tr")]
    rows = [r for r in rows if any(r)]
    if not rows:
        return ""
    md = ["| " + " | ".join(rows[0]) + " |", "|" + " --- |" * len(rows[0])]
    md += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(md)


def _lines(el, prefix: str = "") -> list[str]:
    """Markdown paragraphs for a provision-like element (Paragraf, Stk, Indentatio, Ikraft...)."""
    out: list[str] = []
    tag = _http.localname(el)
    ex = el.find("Explicatus")
    pend = prefix
    if ex is not None and _http.text(ex):
        e = _http.text(ex)
        pend += f"**{e}** " if tag == "Paragraf" else f"*{e}* " if tag == "Stk" else f"{e} "

    def flush(buf):
        nonlocal pend
        if buf:
            out.append(_http.clean(pend + " ".join(buf)))
            pend = ""

    for ch in el:
        t = _http.localname(ch)
        if t in (None, "Explicatus"):
            continue
        if t == "Exitus":
            buf: list[str] = []
            for sub in ch:
                st = _http.localname(sub)
                if st == "Linea":
                    buf.append(_http.text(sub))
                    continue
                flush(buf)
                buf = []
                if st == "Index":
                    for item in sub:
                        if _http.localname(item):
                            out += _lines(item)
                elif st == "Table":
                    out.append(_table(sub))
                elif st == "Nota":
                    out += _lines(sub, "Note ")
            flush(buf)
        elif t == "Rubrica":
            out.append(f"*{_http.text(ch)}*")
        elif t == "Table":
            out.append(_table(ch))
        elif t == "Nota":
            out += _lines(ch, "Note ")
        else:
            out += _lines(ch, pend)
            pend = ""
    if pend.strip():
        out.insert(0, _http.clean(pend))
    return [p for p in out if p]


def _blocks_xml(body) -> list[tuple[str, int, str, str]]:
    """(kind, level, label, markdown) with kind 'heading' | 'prov' | 'text'."""
    blocks: list[tuple[str, int, str, str]] = []

    def walk(el, level):
        for ch in el:
            t = _http.localname(ch)
            if t in (None, "Explicatus", "Rubrica"):
                continue
            if t == "Paragraf":
                ex = ch.find("Explicatus")
                label = _label(_http.text(ex)) if ex is not None else ""
                blocks.append(("prov" if label else "text", level, label, "\n\n".join(_lines(ch))))
            elif t not in _STRUCTURAL_SKIP and ch.find(".//Paragraf") is not None:
                head = " – ".join(x for x in (_http.text(ch.find("Explicatus")),
                                              _http.text(ch.find("Rubrica"))) if x)
                if head:
                    blocks.append(("heading", level, "", head))
                walk(ch, level + 1 if head else level)
            else:
                md = "\n\n".join(_lines(ch))
                if md:
                    blocks.append(("text", level, "", md))

    walk(body, 0)
    return blocks


# --------------------------------------------------------------------------- #
# Site HTML (older documents without an XML body) -> markdown blocks
# --------------------------------------------------------------------------- #
_PROV_START = re.compile(r"^\*{0,2}(§\s*\d+(?:\s*[a-zæøå])?)\.\*{0,2}\s", re.I)


def _blocks_html(html: str) -> list[tuple[str, int, str, str]]:
    paras = _http.html_paragraphs(html)
    if "Den fulde tekst" in paras:  # drop the site's own overview list
        paras = paras[paras.index("Den fulde tekst") + 1:]
    blocks: list[tuple[str, int, str, str]] = []
    seen: set[str] = set()
    for p in paras:
        m = _PROV_START.match(p)
        if m and _key(m[1]) not in seen:
            seen.add(_key(m[1]))
            blocks.append(("prov", 1, _label(m[1]), p))
        elif p.startswith("#"):
            blocks.append(("heading", 0, "", re.sub(r"\s*\(\\?\*\s*\d+\)", "", p.lstrip("# ")).strip()))
        elif blocks and blocks[-1][0] == "prov":
            k, lv, lb, md = blocks[-1]
            blocks[-1] = (k, lv, lb, md + "\n\n" + p)
        else:
            blocks.append(("text", 0, "", p))
    return blocks


def _dmy(s: str) -> str:
    return _http.iso_date((s or "").replace("/", "."))


class Denmark(Jurisdiction):
    code = "dk"
    name = "Denmark"
    languages = ("da",)
    aliases = ("dnk", "danmark", "danish")
    sources = (
        Source(
            name="Retsinformation (Civilstyrelsen)",
            url=RI,
            covers=("legislation",),
            licence="Civilstyrelsen open-data terms: free, non-exclusive, unlimited right of use "
                    "(copy, distribute, modify, commercial and non-commercial); laws are not "
                    "copyrighted (ophavsretsloven § 9). Must not imply endorsement by Civilstyrelsen. "
                    "ELI XML is the documented channel; search and the HTML fallback use the "
                    "website's own undocumented JSON",
            commercial_use=True,
            ai_use=True,
            auth="none",
            rate_limit="none documented for www.retsinformation.dk (terms: don't load the interface "
                       "unreasonably); no 429 in ~25 requests (2026-11); using 1 s spacing",
            terms_url=f"{RI}/api",
        ),
    )
    legislation_filters = {
        "historical": "'true' to include superseded/historical versions (default: in force only)",
    }
    min_interval = {"www.retsinformation.dk": 1.0}
    notes = ("Legislation only (consolidated acts, orders, circulars), Danish. Ids are ELI paths "
             "like 'lta/2016/193'; provisions '§ 1', '§ 7 a'. No case law: Domsdatabasen "
             "(domsdatabasen.dk) requires an approved API application.")
    gaps = (
        "Case law (all courts): Domsdatabasen API needs an approved application; domstol.dk is behind a Cloudflare challenge",
        "Amendments made after the latest consolidation (LBK): not in the text until Retsinformation issues the next LBK",
        "Greenland and Faroe Islands law: not researched yet",
    )
    samples = {
        "legislation_query": "aftaleloven",
        "law_id": "lta/2016/193",
        "provision": "§ 1",
    }

    # ------------------------------------------------------------- legislation
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        if not (query or "").strip():
            raise BadRequest("query is empty; give words from the title, e.g. 'aftaleloven'.")
        hist = str(filters.get("historical", "false")).strip().lower()
        if hist not in ("true", "false", "yes", "no", "1", "0"):
            raise BadRequest("historical must be 'true' or 'false'.")
        params = {"t": query.strip(), "ps": max(1, min(int(limit), 100)), "page": max(0, int(page) - 1)}
        if hist in ("false", "no", "0"):
            params["h"] = "false"
        r = await _http.get(f"{RI}/api/documentsearch", params=params)
        if r.status_code != 200:
            raise SourceError(_http.error("Retsinformation", "search failed", r.status_code), r.status_code)
        try:
            data = r.json()
        except ValueError:
            raise SourceError("Retsinformation search returned non-JSON", r.status_code) from None
        items = []
        for d in data.get("documents") or []:
            link = (d.get("retsinfoLink") or "").strip("/")
            if not link.startswith("eli/"):
                continue
            title = _http.clean(d.get("title"))
            pop = _http.clean(d.get("popularTitle"))
            if pop and pop.lower() not in title.lower():
                title = f"{title} ({pop})"
            dtype = _http.clean(d.get("documentType")).lower()
            bill = link.startswith("eli/ft/") or "forslag" in _http.clean(d.get("documentType")).lower()
            items.append(LawHit(
                id=link[4:], title=title or _http.clean(d.get("shortName")),
                type=_http.clean(d.get("documentType")), number=_http.clean(d.get("shortName")),
                date=_dmy(d.get("offentliggoerelsesDato")),
                status=("lovforslag (ikke gældende ret)" if bill
                        else "afgørelse (ikke lovtekst, ingen gældende-status)" if "afgørelse" in dtype
                        else "historisk" if d.get("isHistoryFlag") else "gældende"),
                snippet=_http.clean(d.get("ressortName")), url=f"{RI}/{link}"))
        note = "" if "h" not in params else "In-force documents only; filter historical='true' for older versions."
        if "h" not in params:
            note = ("historical='true' also returns bills (lovforslag) and old consolidations, ranked by text "
                    "match; an act with no earlier consolidation (e.g. the Grundlov, one text since 1953) "
                    "shows no older version.")
        if any(i.status.startswith("afgørelse") for i in items):
            note = (note + " " if note else "") + ("Items marked 'afgørelse' are complaint-board decisions, "
                    "not legislation; they have no in-force status.")
        return Results(items[:limit], total=data.get("resultCount"), note=note)

    async def _law(self, id: str) -> dict:
        lid = _norm_id(id)
        if lid in _cache:
            return _cache[lid]
        r = await _http.get(f"{RI}/eli/{lid}/xml")
        if r.status_code == 404:
            raise NotFound(f"No Retsinformation document {lid!r}. Find ids with search_legislation.")
        if r.status_code != 200 or b"<Dokument" not in r.content[:2000]:
            raise SourceError(_http.error("Retsinformation", f"XML for {lid} not available", r.status_code),
                              r.status_code)
        root = etree.fromstring(r.content)
        meta = root.find("Meta")
        m = (lambda tag: _http.clean(meta.findtext(tag)) if meta is not None else "")
        doctype = m("DocumentType").split(" ")[0].upper()
        date = m("DiesSigni")
        short = f"{doctype} nr {m('Number')} af {date[8:10]}/{date[5:7]}/{date[:4]}" if date else ""
        title = re.sub(r"\s*\(\*\s*\d+\)\s*", " ", m("DocumentTitle")).strip()
        changes = []
        if meta is not None and doctype in ("LOV", "LBK", "BEK"):
            # <Change> lists later amending acts for statutes/orders (other types use it for references)
            changes = [f"{_http.clean(d.text)}: {_http.clean(t.text)}"
                       for d, t in zip(meta.findall("Ref_Af"), meta.findall("Ref_Text"))
                       if _http.clean(d.text) > date]
        body = root.find("DokumentIndhold")
        blocks = _blocks_xml(body) if body is not None else []
        if not any(b[0] == "prov" for b in blocks):
            r2 = await _http.post(f"{RI}/api/document/eli/{lid}", json={"isRawHtml": False})
            try:
                html = r2.json()[0].get("documentHtml") or ""
            except (ValueError, IndexError, KeyError, AttributeError):
                html = ""
            if r2.status_code != 200 or not html:
                raise SourceError(_http.error("Retsinformation", f"no text for {lid}", r2.status_code),
                                  r2.status_code)
            blocks = _blocks_html(html)
        law = {"id": lid, "title": f"{title} ({short})" if short else title, "url": f"{RI}/eli/{lid}",
               "as_of": date, "status": m("Status"), "changes": changes, "blocks": blocks,
               "popular": m("PopularTitle"), "ministry": m("Ministry"), "doctype": doctype}
        return _http.lru_put(_cache, lid, law, 8)

    @staticmethod
    def _caveat(law: dict) -> str:
        notes = []
        if law["status"] and law["status"] != "Valid":
            notes.append(f"Status at Retsinformation: {law['status']} (this is not the current version; "
                         "search_legislation finds the current one).")
        if law["doctype"] != "LBK":
            if law["status"] == "Valid" and not law["changes"]:
                notes.append(f"'Text as of' is the signing date of the act ({law['as_of'] or 'unknown'}), not a "
                             "consolidation date. Retsinformation marks the act Valid and lists no later "
                             "amending acts, so this is the text it publishes as in force (no amendment "
                             "date applies).")
            else:
                notes.append(f"'Text as of' is the signing date of the original act ({law['as_of'] or 'unknown'}), "
                             "not a currency date. Retsinformation does not state here whether this wording "
                             "includes later amendments; verify the current wording at the source URL "
                             "before citing.")
        if law["changes"]:
            notes.append(f"{len(law['changes'])} later amending act(s) are not yet worked into this "
                         "consolidated text (see get_legislation_text metadata).")
        return "\n\n".join(f"_{n}_" for n in notes)

    async def get_legislation_toc(self, id):
        law = await self._law(id)
        entries = [TocEntry(title=md if kind == "heading" else label, level=lvl,
                            provision=label if kind == "prov" else "")
                   for kind, lvl, label, md in law["blocks"] if kind != "text"]
        return Toc(id=law["id"], title=law["title"], url=law["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        law = await self._law(id)
        want = _key(provision or "")
        if not want:
            raise BadRequest("provision is empty; use a label like '§ 1' or '§ 7 a'.")
        for kind, _lvl, label, md in law["blocks"]:
            if kind == "prov" and _key(label) == want:
                text = "\n\n".join(x for x in (md, self._caveat(law)) if x)
                return Provision(law_id=law["id"], law_title=law["title"], provision=label,
                                 text=text, url=law["url"], as_of=law["as_of"])
        m = re.fullmatch(r"(\d+)[a-z]?", want)
        if m:
            for kind, _lvl, label, _md in law["blocks"]:
                r = re.fullmatch(r"(\d+)[a-z]?-(\d+)[a-z]?", _key(label)) if kind == "prov" else None
                if r and int(r[1]) <= int(m[1]) <= int(r[2]):
                    raise NotFound(f"{provision!r} has no entry of its own in {law['id']}; it is covered by "
                                   f"the range entry {label!r} (request that label).")
        raise NotFound(f"{provision!r} not found in {law['id']}; get_legislation_toc lists the labels.")

    async def get_legislation_text(self, id):
        law = await self._law(id)
        parts = []
        for kind, lvl, _label, md in law["blocks"]:
            parts.append(f"{'#' * min(lvl + 2, 6)} {md}" if kind == "heading" else md)
        caveat = self._caveat(law)
        if caveat:
            parts.insert(0, caveat)
        meta = {k: v for k, v in (("Status", law["status"]), ("Populær titel", law["popular"]),
                                  ("Ministerium", law["ministry"])) if v}
        for i, c in enumerate(law["changes"], 1):
            meta[f"Senere ændring {i} (ikke indarbejdet)"] = c
        return LawText(id=law["id"], title=law["title"], text="\n\n".join(parts), url=law["url"],
                       as_of=law["as_of"], metadata=meta)
