"""Andorra: Tribunal Constitucional decisions (tribunalconstitucional.ad) and consolidated
legislation from the Portal Jurídic del Principat d'Andorra (portaljuridicandorra.ad).

Gotchas this code encodes (verified 2026-11-06):
  * Case law: the Tribunal Constitucional site (Drupal) has an advanced-search view at
    /cercador-avançat (GET: keys, title = case number, field_data_value(_1) = date
    from/to, type_1[] = aute|sentencia, field_tipus_target_id[] = process type). 25 rows a
    page, second pager on the page, so paging is "page=,N". The first column is the
    document's Drupal node id; that nid is our decision id. /node/<nid> redirects to
    /sentencia/<case> or /aute/<case>; the full text is the node's field-contingut.
    robots.txt disallows /search/ (Drupal core search), which we don't use.
    An empty search form returns no table, so a blank query asks for both document types.
  * Legislation: Portal Jurídic is run by the BOPA service (Govern + Consell General). Its
    search tiki-searchbopa.php?find=... lists every hit at once in four tabs (laws in force,
    regulations in force, earlier laws, earlier regulations). robots.txt sets Crawl-Delay: 10
    and disallows tiki-index.php (the title/date search form posts there, so not used).
    Ids are wiki page names: L2022030 (Llei 30/2022), L19930903G / R20261104A (date-coded).
    A law page is one HTML page (up to ~0.5 MB): <h2>-<h5 class="showhide_heading"> headings,
    articles are usually <h5>, disposicions <h4>, text in between with <br>.
    Its legal notice allows personal use only ("Només està autoritzat l'ús personal de les
    imatges i els arxius que es poden descarregar del web. El seu ús comercial no està
    permès."), so results carry a personal-use warning.
  * The Constitution is not on Portal Jurídic. The Consell General publishes it only as PDFs
    (consellgeneral.ad/fitxers/documents/constitucio: one booklet per language, plus one PDF
    per title/chapter; the "Constitució d'Andorra Català.pdf" has broken word spacing). We
    read the Catalan booklet (const-cat, ~450 KB, text layer). Each page's text comes out as
    body, running header, page number, and then, on a page that opens a Títol, the big
    title: _constitution() moves that title back to the top of its page and drops the
    header and number. Kerning splits ("T ribunal", "L 'himne") and end-of-line hyphenation
    are repaired. Id "CONSTITUCIO"; robots.txt only disallows */@@search; no legal notice.
  * BOPA (bopa.ad) is a React app whose search goes through Azure Functions with function
    keys embedded in its JavaScript; not used.
  * Ordinary courts: justicia.ad (TLS verifies again on 2026-11-10) only iframes the CGPJ/CENDOJ
    search at jurisprudencia.poderjudicial.es/andorra. Its search.action POST answers 403 to a
    plain client (the page's JS sends XHR headers), the JS has a CAPTCHA flow, and its Avís legal
    allows personal consultation only, no bulk download, database reuse only via the CGPJ.
    Not used.
"""
from __future__ import annotations

import re
from html import escape
from urllib.parse import quote, urlencode

from lxml import etree, html

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from .._http import check_date as _check_date
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

TC = "https://www.tribunalconstitucional.ad"
TC_HOST = "www.tribunalconstitucional.ad"
TC_SEARCH = TC + "/cercador-avan%C3%A7at"
TC_PAGE = 25
PJ = "https://portaljuridicandorra.ad/"
PJ_HOST = "portaljuridicandorra.ad"
CG_HOST = "www.consellgeneral.ad"
CONST_ID = "CONSTITUCIO"
CONST_PAGE = f"https://{CG_HOST}/fitxers/documents/constitucio"
CONST_PDF = CONST_PAGE + "/const-cat"
CONST_TITLE = "Constitució del Principat d'Andorra (1993)"

DOC_TYPES = {"sentencia": "Sentència", "aute": "Aute"}
PROCESS = {
    "incidental": "7", "competence": "8", "prior-opinion": "9", "empara": "10",
    "direct": "11", "other": "12", "legal-aid": "13", "conflict": "14",
}
SCOPES = ("in-force", "earlier", "all")
LAW_TYPES = ("llei", "reglament")
_TABS = {"1": ("llei", "in force"), "2": ("reglament", "in force"),
         "3": ("llei", "earlier version / no longer in force"),
         "4": ("reglament", "earlier version / no longer in force")}

_MONTHS = {m: i for i, m in enumerate(("gener", "febrer", "març", "abril", "maig", "juny", "juliol",
                                       "agost", "setembre", "octubre", "novembre", "desembre"), 1)}
_LAW_ID = re.compile(r"^[LR]\d{7}(?:\d[A-Z])?$")
_NID = re.compile(r"^\d{1,7}$")

_pages: dict[str, tuple] = {}
_repeal_notes: dict[str, str] = {}


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def cat_date(s: str, year: str = "") -> str:
    """First Catalan date in s ('del 13 de juliol del 2026', "de l'1 d'abril de 1995",
    '1r de març') -> ISO; `year` fills in a date without one. '' if none."""
    m = re.search(r"\b(\d{1,2})(?:r|er)?\s+(?:de\s+|d['’]\s*)(" + "|".join(_MONTHS) +
                  r")(?:\s+(?:de|del)\s+(\d{4}))?", str(s or ""), re.I)
    if not m or not (m[3] or year):
        return ""
    y, mo, d = int(m[3] or year), _MONTHS[m[2].lower()], int(m[1])
    return f"{y:04d}-{mo:02d}-{d:02d}" if 1 <= d <= 31 else ""


async def _get(url: str, what: str):
    r = await _http.get(url)
    if r.status_code == 404:
        raise NotFound(f"{what}: nothing at {url}.")
    if r.status_code != 200:
        raise SourceError(f"{what}: HTTP {r.status_code} for {url}", r.status_code)
    return r


def _cells(tr) -> list[str]:
    return [_http.clean(td.text_content()) for td in tr.xpath("./td")]


# --------------------------------------------------------------------------- #
# Tribunal Constitucional
# --------------------------------------------------------------------------- #
def _decision_nid(raw: str) -> tuple[str, str]:
    """-> ('nid', '19378') or ('path', 'sentencia/2026-32-re')."""
    s = (raw or "").strip()
    s = re.sub(r"^https?://(?:www\.)?tribunalconstitucional\.ad", "", s)
    s = re.sub(r"[?#].*$", "", s).strip("/")
    m = re.fullmatch(r"(?:node/)?(\d{1,7})", s)
    if m:
        return "nid", m[1]
    if re.fullmatch(r"(?:sentencia|aute)/[a-z0-9-]{1,60}", s.lower()):
        return "path", s.lower()
    raise BadRequest(f"decision id {raw!r}: use the numeric id from search_caselaw (e.g. 19378) "
                     "or a Tribunal Constitucional URL like /sentencia/2026-32-re.")


async def _tc_search(params: list[tuple[str, str]], src_page: int) -> tuple[list, bool]:
    q = list(params) + ([("page", f",{src_page}")] if src_page else [])
    r = await _get(TC_SEARCH + "?" + urlencode(q), "Tribunal Constitucional search")
    root = html.fromstring(r.content)
    if not root.xpath('//div[contains(@class,"view-registres-bulk")]'):
        raise SourceError("Tribunal Constitucional search page has an unexpected layout.")
    rows = root.xpath('//table[contains(@class,"views-table")]/tbody/tr')
    has_next = bool(root.xpath('//li[contains(@class,"pager__item--next")]'))
    return rows, has_next


class Andorra(Jurisdiction):
    code = "ad"
    name = "Andorra"
    languages = ("ca",)
    aliases = ("andorra", "principat d'andorra", "principality of andorra", "and")
    sources = (
        Source(
            "Tribunal Constitucional del Principat d'Andorra: sentències and autes",
            TC + "/",
            covers=("caselaw",),
            licence=("unknown: the legal notice names the court as owner, says 'Tots els drets "
                     "reservats' and is silent on reuse or automated access (checked 2026-11-06)"),
            commercial_use=None,
            ai_use=None,   # robots.txt: Drupal default, only /search/ etc. disallowed; no AI opt-out
            auth="none",
            rate_limit=("unknown, nothing documented; 1 s spacing, no 429 seen in ~10 requests "
                        "(2026-11). robots.txt: Drupal default, no Crawl-delay (2026-11-06)"),
            terms_url=TC + "/avis-legal",
        ),
        Source(
            "Portal Jurídic del Principat d'Andorra (BOPA service, Govern d'Andorra / Consell "
            "General): consolidated laws and Government regulations",
            PJ,
            covers=("legislation",),
            licence=("Govern d'Andorra legal notice: all rights reserved; only personal use of "
                     "downloadable files is authorised, commercial use not permitted"),
            commercial_use=False,
            ai_use=None,   # robots.txt has no AI-specific rules
            auth="none",
            rate_limit="robots.txt Crawl-Delay: 10 (checked 2026-11-06); 10 s spacing",
            terms_url=PJ + "AdvertenciaLegal",
            warning=("Personal use only: Portal Jurídic terms allow personal use only, no commercial use; consolidated "
                     "texts are unofficial (the BOPA is the only authentic version)."),
        ),
        Source(
            "Consell General del Principat d'Andorra: Constitució (Catalan booklet PDF)",
            CONST_PAGE,
            covers=("legislation",),
            licence=("unknown: consellgeneral.ad has no legal notice or terms page (checked "
                     "2026-11-10); the Constitution is an official text"),
            commercial_use=None,
            ai_use=None,   # robots.txt: only */@@search disallowed, no AI rules (2026-11-10)
            auth="none",
            rate_limit=("unknown, nothing documented; 1 s spacing; one ~450 KB PDF, kept in a small "
                        "in-memory cache; no 429 seen in ~10 requests (2026-11)"),
            terms_url=f"https://{CG_HOST}/robots.txt",
        ),
    )
    caselaw_filters = {
        "case_number": "Tribunal Constitucional case number, e.g. 2026-32-RE",
        "doc_type": "sentencia or aute",
        "process": "process type: " + ", ".join(PROCESS),
        "date_from": "decision date from, YYYY-MM-DD",
        "date_to": "decision date to, YYYY-MM-DD",
    }
    legislation_filters = {
        "type": "llei (laws) or reglament (Government regulations)",
        "scope": "in-force (default), earlier or all",
    }
    min_interval = {TC_HOST: 1.0, PJ_HOST: 10.0, CG_HOST: 1.0}
    notes = ("Catalan. Case law: Tribunal Constitucional judgments (sentències) and orders (autes) "
             "since 1993; ordinary courts (justicia.ad) not covered. Legislation: the Constitution "
             "(Consell General, id CONSTITUCIO) and Portal Jurídic consolidated laws and regulations "
             "(personal use only).")
    gaps = (
        ("Official gazette (BOPA, bopa.ad): search runs through Azure Functions keyed from its "
         "public JS; no official key or open endpoint"),
        ("Ordinary courts (Tribunal Superior de Justícia, Tribunal de Corts, Batllia): justicia.ad embeds "
         "the CGPJ (CENDOJ) search at jurisprudencia.poderjudicial.es/andorra, which answers 403 "
         "without browser XHR headers, has a CAPTCHA flow, and whose notice allows personal "
         "consultation only, no bulk download, reuse for databases only via a CGPJ procedure"),
        ("Decrets legislatius: no separate type in Portal Jurídic; their consolidated texts are "
         "reached only where filed as the law's text refós"),
    )
    samples = {
        "caselaw_query": "expressio",
        "decision_id": "19378",
        "legislation_query": "persona i familia",
        "law_id": "L2022030",
        "provision": "Article 1",
    }

    # ------------------------------------------------------------------ caselaw
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        params: list[tuple[str, str]] = [("keys", (query or "").strip())]
        if filters.get("case_number"):
            params.append(("title", _http.clean(filters["case_number"])))
        if filters.get("date_from"):
            params.append(("field_data_value", _check_date("date_from", filters["date_from"])))
        if filters.get("date_to"):
            params.append(("field_data_value_1", _check_date("date_to", filters["date_to"])))
        dt = filters.get("doc_type")
        if dt and dt not in DOC_TYPES:
            raise BadRequest(f"doc_type {dt!r}: use sentencia or aute.")
        for t in ([dt] if dt else DOC_TYPES):
            params.append(("type_1[]", t))
        pr = filters.get("process")
        if pr:
            if pr not in PROCESS:
                raise BadRequest(f"process {pr!r} unknown; use one of: {', '.join(PROCESS)}.")
            params.append(("field_tipus_target_id[]", PROCESS[pr]))

        limit = max(1, min(int(limit), 50))
        start = (max(1, int(page)) - 1) * limit
        items: list[DecisionHit] = []
        src = start // TC_PAGE
        skip = start % TC_PAGE
        more = True
        while len(items) < limit and more:
            rows, more = await _tc_search(params, src)
            for tr in rows[skip:]:
                c = _cells(tr)
                link = tr.xpath('.//td[contains(@class,"views-field-title")]//a/@href')
                if len(c) < 5 or not _NID.match(c[0]):
                    continue
                case_no = c[2]
                kind = {"Sentencia": "Sentència"}.get(c[4], c[4])
                items.append(DecisionHit(
                    id=c[0], title=f"Tribunal Constitucional, {kind} {case_no}".strip(),
                    court="Tribunal Constitucional", date=_http.iso_date(c[1]),
                    case_number=case_no,
                    snippet="; ".join(x for x in (c[3], c[5] if len(c) > 5 else "") if x),
                    url=f"{TC}/node/{c[0]}" if not link else TC + re.sub(r"\?.*$", "", link[0])))
                if len(items) >= limit:
                    break
            src, skip = src + 1, 0
            if not rows:
                break
        return Results(items=items, total=None,
                       note="Tribunal Constitucional only; text in Catalan. Ids are the site's node ids.")

    async def get_decision(self, id):
        kind, val = _decision_nid(id)
        url = f"{TC}/node/{val}" if kind == "nid" else f"{TC}/{val}"
        r = await _get(url, "Tribunal Constitucional decision")
        root = html.fromstring(r.content)
        art = root.xpath('//article[contains(@class,"node--type-sentencia") or '
                         'contains(@class,"node--type-aute")]')
        if not art:
            raise NotFound(f"{url} is not a Tribunal Constitucional judgment or order. "
                           "Use an id from search_caselaw.")
        art = art[0]
        nid = art.get("data-history-node-id") or val
        body = art.xpath('.//div[contains(@class,"field--name-field-contingut")]')
        text = _http.html_to_md(etree.tostring(body[0], encoding="unicode", method="html")) if body else ""
        if not text:
            raise SourceError(f"Tribunal Constitucional page {url} has no decision text.")
        case_no = _http.clean(root.xpath('string(//h1[contains(@class,"title")])'))
        is_sent = "node--type-sentencia" in (art.get("class") or "")
        label = "Sentència" if is_sent else "Aute"
        head = "\n".join(text.split("\n\n")[:12])
        parties = re.search(r"^\*?\(([^)\n]{3,200})\)\*?$", head, re.M)
        m = re.search(r"(?:Sentència|Aute)\s+(?:del?\s+|de l['’])\s*([^\n*]{6,40}?\d{4})", head)
        date = cat_date(m[1]) if m else ""
        bopa = re.search(r"BOPA núm\.[^\n*]*", head)
        title = f"Tribunal Constitucional, {label} {case_no}"
        if parties:
            title += f" ({_http.clean(parties[1])})"
        meta = {"Document": label}
        if bopa:
            meta["BOPA"] = _http.clean(bopa[0])
        return Decision(id=str(nid), title=title, text=text, url=str(r.url),
                        court="Tribunal Constitucional", date=date, case_number=case_no,
                        metadata=meta)

    # ------------------------------------------------------------- legislation
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        filters = filters or {}
        q = (query or "").strip()
        if not q:
            raise BadRequest("Portal Jurídic needs search words, e.g. 'persona i família'.")
        typ = filters.get("type")
        if typ and typ not in LAW_TYPES:
            raise BadRequest(f"type {typ!r}: use llei or reglament.")
        scope = filters.get("scope") or "in-force"
        if scope not in SCOPES:
            raise BadRequest(f"scope {scope!r}: use one of {', '.join(SCOPES)}.")
        r = await _get(PJ + "tiki-searchbopa.php?" + urlencode({"find": q}), "Portal Jurídic search")
        root = html.fromstring(r.content)
        tabs = root.xpath('//div[starts-with(@id,"contentleslleis_search-")]')
        if not tabs:
            raise SourceError("Portal Jurídic search page has an unexpected layout.")
        hits: list[LawHit] = []
        for tab in tabs:
            n = tab.get("id").rsplit("-", 1)[-1]
            if n not in _TABS:
                continue
            kind, status = _TABS[n]
            if typ and kind != typ:
                continue
            if scope == "in-force" and status != "in force":
                continue
            if scope == "earlier" and status == "in force":
                continue
            for a in tab.xpath('.//a[@data-object]'):
                lid = a.get("data-object")
                if not _LAW_ID.match(lid or ""):
                    continue
                title = _http.clean(a.text_content())
                hits.append(_law_hit(lid, title, kind, status))
        qw = re.findall(r"\w+", q.lower())
        hits.sort(key=lambda h: (h.status != "in force", h.type != "Llei", -_phrase_run(qw, h.title)))
        if re.search(r"constituci|constitution", q, re.I) and typ != "reglament" and scope != "earlier":
            hits.insert(0, LawHit(id=CONST_ID, title=CONST_TITLE, type="Constitució",
                                  date="1993-04-28", status="in force", url=CONST_PAGE))
        await self._confirm_repeals(hits, _flag_status(hits))
        note = "Consolidated texts are unofficial; the BOPA is authentic. Catalan."
        ql = re.sub(r"\s+", " ", q.lower())
        if hits and not any(ql in h.title.lower() for h in hits):
            note += (f" No title contains the exact phrase {q!r}; hits are word matches only. "
                     "Not finding a title does not prove no such law exists (unverified).")
        start = (max(1, int(page)) - 1) * limit
        return Results(items=hits[start:start + limit], total=len(hits), note=note)

    async def _law(self, raw: str):
        lid = (raw or "").strip()
        lid = re.sub(r"^https?://(?:www\.)?portaljuridicandorra\.ad/", "", lid).strip("/")
        lid = re.sub(r"[?#].*$", "", lid).upper()
        if lid in (CONST_ID, "CONSTITUCIÓ", "CONSTITUTION") or "CONSELLGENERAL.AD" in lid:
            return await _constitution()
        if not _LAW_ID.match(lid):
            raise BadRequest(f"law id {raw!r}: use a Portal Jurídic id from search_legislation, "
                             "e.g. L2022030 (Llei 30/2022) or R20261104A.")
        if lid in _pages:
            return _pages[lid]
        r = await _get(PJ + lid, "Portal Jurídic")
        root = html.fromstring(r.content)
        data = root.xpath('//div[@id="page-data"]')
        h1 = root.xpath('//div[@id="page-data"]//h1')
        if not data or not h1:
            raise NotFound(f"no Portal Jurídic text {lid}. Use an id from search_legislation.")
        data = data[0]
        for junk in data.xpath('.//div[@id="toc"] | .//img | .//script | .//div[@class="amaga"]'):
            junk.getparent().remove(junk)
        title = _http.clean(h1[0].text_content())
        h1[0].getparent().remove(h1[0])
        return _http.lru_put(_pages, lid, (lid, title, data), 3)

    async def _confirm_repeals(self, hits, newer_by_id):
        """Upgrade 'probably repealed' to 'repealed' when the newer law's own text names the old one."""
        for h in hits:
            for n in newer_by_id.get(h.id, []):
                try:
                    _, _, data = await self._law(n.id)
                except (SourceError, NotFound):
                    continue
                if h.number and re.search(r"derogad[ae]s?\b[^.]{0,80}?\b" + re.escape(h.number) + r"(?!\d)",
                                          data.text_content()):
                    h.status = (f"repealed: {n.title.split(',')[0]} ({n.id}) repeals it in its derogatòria "
                                "although the portal still lists it as in force; check that law's entry "
                                "into force")
                    break

    async def _repeal_note(self, lid: str, title: str) -> str:
        """One-line repeal warning for a law fetched by id ('' when none is found)."""
        if lid in _repeal_notes:
            return _repeal_notes[lid]
        note = ""
        key = _title_key(title)
        if key and re.match(r"^L\d{7,8}[A-Z]?$", lid):
            try:
                found = await self.search_legislation(key, limit=50, filters={"type": "llei"})
            except (SourceError, BadRequest):
                return ""
            if lid not in {h.id for h in found.items}:
                me = _law_hit(lid, title, "llei", "in force")
                found.items.append(me)
                await self._confirm_repeals(found.items, _flag_status(found.items))
                if me.status.startswith("repealed"):
                    note = me.status
            else:
                note = next((h.status for h in found.items if h.id == lid and h.status.startswith("repealed")), "")
        _repeal_notes[lid] = note
        return note

    async def get_legislation_toc(self, id):
        lid, title, data = await self._law(id)
        entries = [TocEntry(title=h, level=max(0, lvl - 2), provision=lab)
                   for lvl, h, lab, _ in _sections(data)]
        return Toc(id=lid, title=title, url=_url(lid), entries=entries)

    async def get_legislation_provision(self, id, provision):
        lid, title, data = await self._law(id)
        want = _norm(provision)
        if not want:
            raise BadRequest("provision is empty; use a label from get_legislation_toc, e.g. 'Article 1'.")
        for _, head, label, body in _sections(data):
            if label and _norm(label) == want:
                warn = await self._repeal_note(lid, title)
                warn = f"> ⚠ Status: {warn}\n\n" if warn else ""
                return Provision(law_id=lid, law_title=title, provision=label,
                                 text=warn + f"**{head}**\n\n{body}".strip(), url=_url(lid),
                                 as_of=_http.today())
        raise NotFound(f"no {provision!r} in {lid}. See get_legislation_toc for the labels.")

    async def get_legislation_text(self, id):
        lid, title, data = await self._law(id)
        text = _http.html_to_md(etree.tostring(data, encoding="unicode", method="html"))
        if not text:
            raise SourceError(f"Portal Jurídic page {lid} has no text.")
        meta = ({"Note": "Consolidated text without official character; the BOPA is the authentic version."}
                if lid != CONST_ID else {"Source": "Consell General, Catalan booklet PDF " + CONST_PDF})
        warn = await self._repeal_note(lid, title) if lid != CONST_ID else ""
        if warn:
            meta["Status"] = warn
        return LawText(id=lid, title=title, text=text, url=_url(lid), as_of=_http.today(), metadata=meta)


# --------------------------------------------------------------------------- #
# Constitution (Consell General PDF)
# --------------------------------------------------------------------------- #
def _url(lid: str) -> str:
    return CONST_PAGE if lid == CONST_ID else PJ + lid


_CLITICS = {"se", "lo", "la", "li", "los", "les", "hi", "ne", "ho", "me", "te", "nos", "vos", "en"}


def _const_lines(text: str) -> list[str]:
    """Booklet text (pages split by blank lines) -> body lines in reading order."""
    out: list[str] = []
    started = False
    for page in text.split("\n\n"):
        lines = [ln.strip() for ln in page.split("\n") if ln.strip()]
        nums = [i for i, ln in enumerate(lines) if ln.isdigit()]
        if not nums or nums[-1] == 0:
            continue
        k = nums[-1]
        body, tail = lines[:k - 1], lines[k + 1:]
        if tail and re.match(r"(Títol|Preàmbul)\b", tail[0]):
            body = tail + body
            started = True
        elif started:
            body = body + tail
        if started:
            out += body
        if started and any(ln.startswith("Casa de la Vall") for ln in body):
            break
    return out


def _const_html(lines: list[str]) -> str:
    """Body lines -> HTML that _sections() understands (h2 Títol, h3 Capítol, h4/h5 provisions)."""
    fix = [re.sub(r"([IVX]) \.", r"\1.", re.sub(r"\b([TL]) (?=[a-zà-ÿ’'])", r"\1", ln)) for ln in lines]
    parts: list[str] = []
    para = ""
    pre = False    # inside the preamble: each clause is a paragraph
    sign = False   # after "Casa de la Vall": signature lines, one per paragraph
    i = 0

    def end_para():
        nonlocal para
        if para:
            parts.append(f"<p>{escape(para)}</p>")
        para = ""

    while i < len(fix):
        ln = fix[i]
        if ln == "Preàmbul" or re.fullmatch(r"Article \d+", ln) or re.match(
                r"Disposició (addicional|transitòria|derogatòria|final)", ln):
            end_para()
            tag = "h4" if ln.startswith("Disposició") else "h5"
            pre = ln == "Preàmbul"
            parts.append(f"<{tag}>{escape(ln)}</{tag}>")
        elif re.fullmatch(r"Títol [IVX]+", ln) and i + 1 < len(fix):
            end_para()
            parts.append(f"<h2>{escape(ln)}. {escape(fix[i + 1])}</h2>")
            i += 1
        elif re.match(r"Capítol [IVX]+\.", ln):
            end_para()
            head = ln
            while i + 1 < len(fix) and not fix[i + 1].startswith("Article"):
                i += 1
                head += " " + fix[i]
            parts.append(f"<h3>{escape(head)}</h3>")
        elif re.match(r"(\d+|[a-z])[.)] ", ln) or not para or sign or ln.startswith("Casa de la Vall") \
                or (pre and para.endswith(",") and ln[:1].isupper()):  # preamble clauses
            sign = sign or ln.startswith("Casa de la Vall")
            end_para()
            para = ln
        elif para.endswith("-") and re.search(r"\w-$", para) and ln[:1].islower():
            nxt = re.match(r"[a-zà-ÿ]+", ln)
            keep = nxt and nxt[0] in _CLITICS and re.search(r"r-$", para)
            para = para + ln if keep else para[:-1] + ln
        else:
            para += " " + ln
        i += 1
    end_para()
    return "<div>" + "".join(parts) + "</div>"


async def _constitution():
    if CONST_ID in _pages:
        return _pages[CONST_ID]
    r = await _get(CONST_PDF, "Consell General: Constitució")
    if not r.content.startswith(b"%PDF"):
        raise SourceError("Consell General: the Constitution PDF link no longer returns a PDF.")
    lines = _const_lines(_http.pdf_text(r.content))
    data = html.fromstring(_const_html(lines))
    if len(data.xpath(".//h5[starts-with(., 'Article')]")) != 107:
        raise SourceError("Consell General: Constitution PDF layout changed (expected 107 articles).")
    return _http.lru_put(_pages, CONST_ID, (CONST_ID, CONST_TITLE, data), 3)


# --------------------------------------------------------------------------- #
# Portal Jurídic helpers
# --------------------------------------------------------------------------- #
def _law_hit(lid: str, title: str, kind: str, status: str) -> LawHit:
    m = re.match(r"^(\w+)\s+(\d+/\d{4})", title)
    number = m[2] if m else ""
    if re.match(r"^[LR]\d{8}[A-Z]$", lid):
        date = f"{lid[1:5]}-{lid[5:7]}-{lid[7:9]}"
    else:
        date = cat_date(title, number.split("/")[-1] if number else "")
    typ = title.split(" ", 1)[0].strip(",") if title else kind.capitalize()
    return LawHit(id=lid, title=title, type=typ, number=number, date=date, status=status,
                  url=_url(lid))


def _phrase_run(qw: list[str], title: str) -> int:
    """Longest run of consecutive query words that also appears consecutively in the title."""
    tw = re.findall(r"\w+", title.lower())
    best = 0
    for i in range(len(qw)):
        for j in range(i + best + 1, len(qw) + 1):
            if any(tw[k:k + j - i] == qw[i:j] for k in range(len(tw))):
                best = j - i
            else:
                break
    return best


def _title_key(title: str) -> str:
    t = re.sub(r"\s*\(Text refós[^)]*\)\s*$", "", title)
    m = re.match(r"^\w+ \d+/\d{4},\s*del? \d+ d[e’'] ?\w+,?\s*(.*)$", t)
    return (m[1] if m else "").strip().lower()


def _flag_status(hits: list[LawHit]) -> dict[str, list[LawHit]]:
    """The portal lists repealed or not-yet-effective laws as 'in force'; say what we can see."""
    cutoff = f"{int(_http.today()[:4]) - 1}{_http.today()[4:]}"
    live = [h for h in hits if h.status == "in force" and h.id != CONST_ID]
    pending: dict[str, list[LawHit]] = {}
    for h in live:
        newer = [o for o in live if o is not h and o.date > h.date
                 and (k := _title_key(o.title)) and k == _title_key(h.title)]
        if newer:
            pending[h.id] = newer
            h.status = (f"listed as in force by the portal, but a newer law with the same title exists "
                        f"({newer[0].title.split(',')[0]}): probably repealed or replaced, check its "
                        "final provisions (unverified)")
        elif h.date and h.date >= cutoff:
            h.status = ("listed as in force by the portal; recent law, so entry into force may be later "
                        "than publication: check its final provisions and the BOPA date (unverified)")
    return pending


_PROV = re.compile(r"^((?:Article|Disposició|Annex|Preàmbul|Exposició de motius)\b[^.]*?)(?:\.\s|\.?$)")


def _sections(data):
    """[(level, heading text, provision label or '', body markdown)] from page-data."""
    out = []
    cur = None
    buf: list[str] = []

    def flush():
        if cur is not None:
            body = _http.html_to_md("".join(buf))
            out.append((cur[0], cur[1], cur[2], body))

    pre = data.text or ""
    for el in data.iterchildren():
        if isinstance(el.tag, str) and re.fullmatch(r"h[2-6]", el.tag):
            flush()
            head = _http.clean(el.text_content())
            m = _PROV.match(head)
            cur = (int(el.tag[1]), head, _http.clean(m[1]) if m else "")
            buf = [el.tail or ""]
        elif cur is not None:
            buf.append(etree.tostring(el, encoding="unicode", method="html"))
        else:
            pre += etree.tostring(el, encoding="unicode", method="html")
    flush()
    return out


def _norm(label: str) -> str:
    s = _http.clean(label).lower().rstrip(".").replace("’", "'")
    s = re.sub(r"^(?:article|art\.?)\s*", "article ", s)
    if re.fullmatch(r"\d+(?:\s*(?:bis|ter|quater))?", s):
        s = "article " + s
    return re.sub(r"\s+", " ", s).strip()
