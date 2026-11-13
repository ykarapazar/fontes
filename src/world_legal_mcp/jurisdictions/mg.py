"""Madagascar: decisions of the High Constitutional Court (HCC) and the laws and regulations
published in the Journal Officiel, as held by CNLegis (Secrétariat Général du Gouvernement).

Case law (www.hcc.gov.mg, WordPress):
  * Every decision, avis and arrêt is a post with the full text as HTML in the body
    (D1 international conventions, D2 exceptions of unconstitutionality, D3 national
    legislation, AV opinions, AR arrêts incl. election results, DB deliberations).
    Search is the WordPress REST API (?rest_route=/wp/v2/posts&search=, X-WP-Total).
  * Id: the WordPress post id ("10128"); the page URL (https://www.hcc.gov.mg/?p=10128)
    also works. Some posts are the Malagasy version of a French decision.
  * The Cour Suprême site (www.coursupreme.mg) was a bare hosting placeholder in 2026-11;
    no ordinary-court case law is online from an official source.

Legislation (www.cnlegis.gov.mg, Direction du CNLegis, Primature):
  * Laws, ordinances, decrees and arrêtés from the Journal Officiel: references since 1897,
    full texts (HTML, French and sometimes Malagasy) since 1998. Texts are as published
    (original, not consolidated); amending laws quote the new articles inline.
  * Search is the site's own two-step form: POST the words (or number) to the form page,
    which stores the query in the PHP session, then POST page_data_result_* for a JSON
    page of rows that already carry the full text. The two steps run under a lock so
    concurrent searches cannot swap sessions.
  * Id: the site's own "int_name" ("L2001-022" = Loi n°2001-022, "D2017-012" = Décret,
    "O…" ordonnance, "A35460/2026" arrêté). There is no per-text page; `url` is the
    site's search-by-number page (or the text's PDF when the site has one).
  * Older texts: a few have full HTML (Loi 66-003 on obligations); some have only a header
    and a "Cliquez-ici" link to a text-layer PDF under /uploads/ (Ordonnance 62-041), which
    get_legislation_* then read. A sample of 2026-11-10 (laws and ordinances numbered 62-0*,
    75-0*, 85-0*, 93-0*) found about 90% reference-only (no HTML, no PDF).
  * The Constitution of 11 December 2010 is full text (id "Co2010"); CNLegis lists no later
    revision (search "révision constitution" finds the 2007 one only).
  * The Journal Officiel scans behind "UTILISATEUR JOURNAL OFFICIEL" need a login: not used.
"""
from __future__ import annotations

import asyncio
import html as htmllib
import re

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc, TocEntry

HCC_HOST = "www.hcc.gov.mg"
CNL_HOST = "www.cnlegis.gov.mg"
HCC = f"https://{HCC_HOST}/"
CNL = f"https://{CNL_HOST}/"
CNL_NUM_PAGE = f"{CNL}page_cherche_dir_numeros/"
MAX_BYTES = 40_000_000

# WordPress category -> (filter value, label). Only these hold decisions.
_CATS = {7: ("d1", "Décision D1 – Conventions internationales"),
         8: ("d2", "Décision D2 – Exceptions d'inconstitutionnalité"),
         9: ("d3", "Décision D3 – Législation nationale"),
         4: ("av", "Avis"),
         3: ("ar", "Arrêt"),
         20: ("ar", "Arrêt (élections)"),
         24: ("db", "Délibération")}
_FILTER_CATS: dict[str, list[int]] = {}
for _c, (_f, _) in _CATS.items():
    _FILTER_CATS.setdefault(_f, []).append(_c)
_HIT_FIELDS = "id,date,link,title,categories,excerpt"
_DEC_ID = re.compile(r"^(?:https?://(?:www\.)?hcc\.gov\.mg/?\?p=)?(\d{1,7})$", re.I)
_CASE_NO = re.compile(r"n\s*°\s*(\d+\s*-\s*HCC\s*/\s*[A-Z]{1,3}\d?)", re.I)

_MONTHS = {m: i for i, m in enumerate(("janvier", "février", "mars", "avril", "mai", "juin", "juillet",
                                         "août", "septembre", "octobre", "novembre", "décembre"), 1)}
_MONTHS.update({"fevrier": 2, "aout": 8, "decembre": 12})
_FR_DATE = re.compile(r"\b(\d{1,2})(?:er)?\s+(" + "|".join(_MONTHS) + r")\s+(\d{4})\b", re.I)

# CNLegis
_LAW_ID = re.compile(r"^[A-Za-z]{0,4}\d[\w./-]{0,60}$")
_LIMIT_RE = re.compile(r"(\d+)(?:&nbsp;|\s)*r[ée]sultat", re.I)
_session_lock = asyncio.Lock()
_rows: dict = {}          # int_name (upper) -> CNLegis row


def _fr_date(s: str) -> str:
    m = _FR_DATE.search(s or "")
    if not m:
        return ""
    try:
        import datetime
        return datetime.date(int(m[3]), _MONTHS[m[2].lower()], int(m[1])).isoformat()
    except ValueError:
        return ""


def _plain(html: str) -> str:
    return _http.clean(htmllib.unescape(re.sub(r"<[^>]+>", " ", html or "")))


# --------------------------------------------------------------------------- #
# HCC (case law)
# --------------------------------------------------------------------------- #
def _court(cats) -> str:
    kinds = [_CATS[c][1] for c in cats or () if c in _CATS]
    return "Haute Cour Constitutionnelle" + (f" ({kinds[0]})" if kinds else "")


def _hit(post: dict) -> DecisionHit:
    title = _plain(post.get("title", {}).get("rendered", ""))
    m = _CASE_NO.search(title)
    snippet = re.sub(r"\s*(Voir Plus|Lire la suite)\s*(…|&#8230;|\.\.\.)?\s*$", "", _plain(
        post.get("excerpt", {}).get("rendered", "")))
    return DecisionHit(id=str(post["id"]), title=title, court=_court(post.get("categories")),
                       date=_fr_date(title), case_number=re.sub(r"\s+", "", m[1]) if m else "",
                       snippet=snippet[:400], url=post.get("link") or f"{HCC}?p={post['id']}")


async def _hcc(params: dict, what: str):
    r = await _http.get(HCC, params=params)
    if r.status_code in (400, 404) and "rest_post_invalid_id" in r.text:
        raise NotFound(f"HCC: no decision {what}.")
    if r.status_code != 200 or "json" not in r.headers.get("content-type", ""):
        raise SourceError(_http.error(HCC_HOST, what, r.status_code), r.status_code)
    if len(r.content) > MAX_BYTES:
        raise SourceError(f"{HCC_HOST}: response over {MAX_BYTES} bytes refused.")
    return r


# --------------------------------------------------------------------------- #
# CNLegis (legislation)
# --------------------------------------------------------------------------- #
async def _cnl_search(form: str, data_ep: str, query: str, offset: int, limit: int) -> tuple[list[dict], int | None]:
    async with _session_lock:
        r = await _http.post(f"{CNL}{form}/", data={"txt_recherche": query})
        if r.status_code != 200:
            raise SourceError(_http.error(CNL_HOST, "search form", r.status_code), r.status_code)
        m = _LIMIT_RE.search(r.text)
        total = int(m[1]) if m else None
        if total is not None and offset >= total:   # past the end the site answers an empty text/html body
            return [], total
        r = await _http.post(f"{CNL}{data_ep}", data={"var_pg_limit": f"{offset},{limit}"})
    if r.status_code != 200 or "json" not in r.headers.get("content-type", ""):
        raise SourceError(_http.error(CNL_HOST, "search results", r.status_code), r.status_code)
    if len(r.content) > MAX_BYTES:
        raise SourceError(f"{CNL_HOST}: response over {MAX_BYTES} bytes refused.")
    try:
        rows = r.json().get("aaData") or []
    except ValueError:
        raise SourceError(f"{CNL_HOST}: search results were not JSON.") from None
    if not isinstance(rows, list):
        rows = []
    for row in rows:
        if row.get("int_name"):
            _http.lru_put(_rows, row["int_name"].upper(), row, 64)
    return rows, total


def _law_title(row: dict) -> str:
    head = _http.clean(f"{row.get('type_txt', '')} n°{row.get('num_txt', '')}")
    date = _http.iso_date(row.get("date_txt"))
    if date:
        y, mth, d = date.split("-")
        head += f" du {int(d)} {list(_MONTHS)[int(mth) - 1]} {y}"
    obj = _plain(row.get("objet_txt")) or _plain(row.get("objet_txt_mg"))
    return f"{head} {obj}".strip() if obj else head


def _law_url(row: dict) -> str:
    pdf = (row.get("version_pdf_fr") or row.get("version_pdf_mg") or "").strip()
    return f"{CNL}jqupload_2/uploads/{pdf}" if pdf else CNL_NUM_PAGE


def _jo(row: dict) -> str:
    """'J.O. n°N du D, p. P' from the row, leaving out the site's placeholders
    ('VOIR_J.O', '00-00-0000', page 0), which are not citations."""
    num, date, page = (_http.clean(str(row.get(k) or "")) for k in ("num_jo", "date_jo", "page_jo"))
    if not num or "VOIR" in num.upper():
        return ""
    out = f"J.O. n°{num}"
    if date and not re.fullmatch(r"[0\s/.-]+", date):
        out += f" du {date}"
    if page and page != "0":
        out += f", p. {page}"
    return out


def _law_hit(row: dict) -> LawHit:
    return LawHit(id=row["int_name"], title=_law_title(row), type=row.get("type_txt", ""),
                  number=row.get("num_txt", ""), date=_http.iso_date(row.get("date_txt")),
                  status=row.get("etat_txt", ""), url=_law_url(row),
                  snippet=_jo(row))


async def _law(id: str) -> dict:
    id = (id or "").strip()
    if not _LAW_ID.match(id):
        raise BadRequest("Use a CNLegis law id from search_legislation, e.g. 'L2001-022' (Loi n°2001-022) "
                         "or 'D2017-012' (Décret).")
    row = _rows.get(id.upper())
    if row:
        return row
    num = re.sub(r"^[A-Za-z]+", "", id)
    rows, _ = await _cnl_search("page_num_find_direct", "page_num_data_find_direct", num, 0, 50)
    exact = [r for r in rows if (r.get("int_name") or "").upper() == id.upper()]
    if not exact and num == id:  # bare number: accept when only one text has it
        exact = [r for r in rows if r.get("num_txt") == num]
        if len(exact) > 1:
            raise BadRequest(f"Several texts carry number {num}: "
                             + ", ".join(r["int_name"] for r in exact) + ". Use one of these ids.")
    if not exact:
        raise NotFound(f"CNLegis: no text with id {id}.")
    return exact[0]


_PDF_LINK = re.compile(r'href="(https?://(?:www\.)?cnlegis\.gov\.mg/[^"]+\.pdf)"', re.I)
_pdfs: dict = {}          # PDF url -> text


async def _pdf_md(url: str) -> str:
    """Text-layer PDF -> paragraphs, one per article ('' for a scan or a failed fetch)."""
    if url in _pdfs:
        return _pdfs[url]
    r = await _http.get(url, max_bytes=MAX_BYTES)
    if r.status_code != 200 or not r.content.startswith(b"%PDF"):
        return ""
    t = _http.pdf_text(r.content)
    t = re.sub(r"\n(?=Art(?:icle|\.)\s*(?:premier|1\s*er|\d))", "\n\n", t, flags=re.I) if len(t) >= 200 else ""
    return _http.lru_put(_pdfs, url, t, 8)


async def _law_md(row: dict) -> str:
    html = (row.get("html_fichier_fr") or "").replace("http://localhost/legisapplications/", CNL)
    text = _http.html_to_md(html)
    if len(text) < 50:
        text = _http.html_to_md(row.get("html_fichier_mg") or "")
    # Some older texts (e.g. O62-041) have only a header and a "Cliquez-ici" link to a PDF
    # with a text layer: use it when the HTML has no article of its own.
    pdf = _PDF_LINK.search(html)
    pdf_url = pdf[1] if pdf else (_law_url(row) if _law_url(row) != CNL_NUM_PAGE else "")
    if pdf_url and not any(_ART.match(p) for p in text.split("\n\n")):
        ptext = await _pdf_md(pdf_url)
        if len(ptext) > len(text):
            text = f"{ptext}\n\n(Text from the PDF linked by CNLegis: {pdf_url})"
    if len(text) < 50:
        where = f" The PDF is at {_law_url(row)}." if _law_url(row) != CNL_NUM_PAGE else ""
        raise NotFound(f"CNLegis has only the reference of {row.get('int_name')}, no full text online.{where}")
    return text


_ART = re.compile(r"^[*_\s]*Art(?:icle|\.)[*_\s.]*(premier|1\s*er|\d+(?:\s*[.-]\s*\d+)*)"
                  r"(?:[*_\s]*(bis|ter|quater|quinquies)\b)?", re.I)


def _norm_num(n: str, suffix: str = "") -> str:
    n = re.sub(r"\s+", "", n.lower())
    n = "1" if n in ("premier", "1er") else n
    return n + (f" {suffix.lower()}" if suffix else "")


def _split(text: str) -> tuple[list[TocEntry], dict[str, str]]:
    """Article paragraphs -> TOC + {label: text}. A number repeated (an amending law
    quoting new articles, or a second article series) gets ' (2)', ' (3)'."""
    paras = text.split("\n\n")
    entries, parts, seen = [], {}, {}
    cur, buf = None, []

    def flush():
        if cur:
            parts[cur] = "\n\n".join(buf)

    for p in paras:
        m = _ART.match(p)
        if m:
            flush()
            num = _norm_num(m[1], m[2] or "")
            seen[num] = seen.get(num, 0) + 1
            cur = f"Article {num}" + (f" ({seen[num]})" if seen[num] > 1 else "")
            buf = [p]
            entries.append(TocEntry(title=_http.clean(re.sub(r"[*_]", "", p))[:120], provision=cur))
        elif cur:
            buf.append(p)
    flush()
    return entries, parts


def _norm_prov(p: str) -> str:
    p = _http.clean(re.sub(r"\(\s*(?:nouveau|nouvelle|modifié|abrogé)\s*\)", " ", p, flags=re.I)).strip(" .")
    m = re.match(r"^(?:art(?:icle|\.)?\s*)?(premier|1\s*er|\d+(?:\s*[.-]\s*\d+)*)(?:\s*(bis|ter|quater|quinquies))?"
                 r"(?:\s*\((\d+)\))?$", p, re.I)
    if not m:
        return p
    label = f"Article {_norm_num(m[1], m[2] or '')}"
    return label + (f" ({m[3]})" if m[3] and m[3] != "1" else "")


class Madagascar(Jurisdiction):
    code = "mg"
    name = "Madagascar"
    languages = ("fr", "mg")
    aliases = ("madagasikara", "république de madagascar", "malagasy")
    sources = (
        Source(name="Haute Cour Constitutionnelle (hcc.gov.mg)", url=HCC, covers=("caselaw",),
               licence="unknown; no terms of use published (footer: 'Copyright © HCC 2020')",
               commercial_use=None, ai_use=None, auth="none",
               rate_limit="unknown; 1 s spacing, no 429 seen in ~10 requests (2026-11); no robots.txt (404)",
               terms_url=""),
        Source(name="CNLegis – Centre National LEGIS, Primature (cnlegis.gov.mg)", url=CNL,
               covers=("legislation",),
               licence="unknown; no terms of use published (footer: '© 2018 DIRCNLEGIS')",
               commercial_use=None, ai_use=False, auth="none",
               rate_limit="unknown; 1.5 s spacing, no 429 seen in ~15 requests (2026-11)",
               terms_url="https://www.cnlegis.gov.mg/robots.txt"),
    )
    caselaw_filters = {"type": "d1 (conventions internationales), d2 (exceptions d'inconstitutionnalité), "
                               "d3 (législation nationale), av (avis), ar (arrêts), db (délibérations)"}
    legislation_filters = {}
    min_interval = {HCC_HOST: 1.0, CNL_HOST: 1.5}
    notes = ("Case law: High Constitutional Court only (decisions, avis, arrêts; French, some Malagasy). "
             "Legislation: Journal Officiel texts via CNLegis, full text since 1998, not consolidated.")
    gaps = (
        "Ordinary courts incl. the Cour Suprême: not published online (coursupreme.mg was a "
         "hosting placeholder, 2026-11)",
        ("Full texts of laws before 1998: mostly not online (CNLegis has references back to 1897; "
         "~90% of a 2026-11-10 sample of 1962-1993 laws/ordinances had no HTML or PDF text); a few "
         "major ones are full text (e.g. L66-003, O62-041)"),
        "Journal Officiel scans (CNLegis 'utilisateur Journal Officiel'): need a login, not used",
        "Ministry of Justice site (justice.gov.mg): wrong-host TLS certificate, unreachable",
    )
    samples = {"caselaw_query": "exception d'inconstitutionnalité", "decision_id": "10128",
               "legislation_query": "procédure civile", "law_id": "L2001-022", "provision": "Article 5"}

    # ---------------------------------------------------------------- case law
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        kind = ((filters or {}).get("type") or "").strip().lower()
        if kind and kind not in _FILTER_CATS:
            raise BadRequest(f"type must be one of {', '.join(_FILTER_CATS)}.")
        cats = _FILTER_CATS[kind] if kind else list(_CATS)
        params = {"rest_route": "/wp/v2/posts", "categories": ",".join(map(str, cats)),
                  "per_page": max(1, min(int(limit), 50)), "page": max(1, int(page)), "_fields": _HIT_FIELDS}
        q = (query or "").strip()
        if q:
            # WordPress matches ANY word and sorts by date unless told otherwise, so a name
            # like "Air Madagascar" drowned in newer decisions: sort by relevance.
            # Unquoted, WordPress needs every word somewhere in the text, not the phrase, so
            # "contrat de travail" hit decisions that only mention "travail" elsewhere: quote it.
            if " " in q and not q.startswith('"'):
                q = '"' + q.replace('"', "") + '"'
            params.update(search=q, orderby="relevance")
        r = await _http.get(HCC, params=params)
        if r.status_code == 400 and "rest_post_invalid_page_number" in r.text:
            return Results(items=[], total=None)
        if r.status_code != 200 or "json" not in r.headers.get("content-type", ""):
            raise SourceError(_http.error(HCC_HOST, "decision search", r.status_code), r.status_code)
        total = r.headers.get("X-WP-Total")
        items, seen = [], set()
        for p in r.json():   # the HCC site posts some decisions twice (e.g. 01-HCC/D2 of 2008)
            h = _hit(p)
            key = re.sub(r"\W+", "", h.title.lower())
            if key not in seen:
                seen.add(key)
                items.append(h)
        total = int(total) if total and total.isdigit() else None
        if total is not None and total <= len(r.json()):
            total = len(items)
        note = "High Constitutional Court only; no other Malagasy court publishes online."
        if not items and q.startswith('"'):
            note += " Multi-word queries are matched as an exact phrase; try fewer or different words."
        return Results(items=items, total=total, note=note)

    async def get_decision(self, id):
        m = _DEC_ID.match((id or "").strip())
        if not m:
            raise BadRequest("Give an HCC decision id from search_caselaw, e.g. '10128' "
                             "(or https://www.hcc.gov.mg/?p=10128).")
        r = await _hcc({"rest_route": f"/wp/v2/posts/{m[1]}",
                        "_fields": "id,date,link,title,categories,content"}, m[1])
        post = r.json()
        if not set(post.get("categories") or ()) & set(_CATS):
            raise NotFound(f"HCC: post {m[1]} is not a decision.")
        hit = _hit(post)
        text = _http.html_to_md(post.get("content", {}).get("rendered", ""))
        return Decision(id=hit.id, title=hit.title, text=text, url=hit.url, court=hit.court, date=hit.date,
                        case_number=hit.case_number,
                        metadata={"Publié sur hcc.gov.mg": (post.get("date") or "")[:10]})

    # ------------------------------------------------------------- legislation
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        q = (query or "").strip()
        if not q:
            raise BadRequest("CNLegis needs words from the title (objet) or a text number, e.g. '2001-022'.")
        limit = max(1, min(int(limit), 50))
        offset = (max(1, int(page)) - 1) * limit
        if re.fullmatch(r"\d[\d/-]*", q):
            rows, total = await _cnl_search("page_num_find_direct", "page_num_data_find_direct", q, offset, limit)
        else:
            rows, total = await _cnl_search("page_find_direct_mots", "page_data_result_direct_mots", q, offset, limit)
        note = "Texts as published in the Journal Officiel, not consolidated; newest first."
        low = q.lower()
        if "constitution" in low or "ive république" in low or "ivème république" in low:
            note += (" The Constitution of 11 December 2010 (IVe République) is not found by this search; "
                     "read it with get_legislation_toc / get_legislation_text, id 'Co2010'. The hits here "
                     "are amendments and decisions that mention it.")
        if re.search(r"code p[ée]nal|penal code", low):
            note += (" The base Code pénal itself did not appear in CNLegis in 2026-11, only the laws "
                     "amending it.")
        if re.search(r"code civil|civil code", low):
            note += (" CNLegis has no 'Code civil' text; the core civil-law texts it holds are Loi 66-003 "
                     "(théorie générale des obligations, id 'L66-003') and Ordonnance 62-041 ('O62-041').")
        return Results(items=[_law_hit(r) for r in rows if r.get("int_name")][:limit], total=total, note=note)

    async def get_legislation_text(self, id):
        row = await _law(id)
        meta = {k: v for k, v in (("Type", row.get("type_txt")), ("État", row.get("etat_txt")),
                                  ("Journal Officiel", _jo(row).removeprefix("J.O. ")),
                                  ("Ministère", row.get("ministere")),
                                  ("Notes", _http.html_to_md(row.get("notes") or "")
                                   if row.get("notes") not in (None, "", "undefined") else "")) if v}
        return LawText(id=row["int_name"], title=_law_title(row), text=await _law_md(row), url=_law_url(row),
                       metadata=meta)

    async def get_legislation_toc(self, id):
        row = await _law(id)
        entries, _ = _split(await _law_md(row))
        return Toc(id=row["int_name"], title=_law_title(row), url=_law_url(row), entries=entries)

    async def get_legislation_provision(self, id, provision):
        row = await _law(id)
        _, parts = _split(await _law_md(row))
        label = _norm_prov(provision)
        if label not in parts:
            raise NotFound(f"{row['int_name']}: no {label}. Use a label from get_legislation_toc, "
                           "e.g. 'Article 5' or 'Article 2 (2)'.")
        return Provision(law_id=row["int_name"], law_title=_law_title(row), provision=label,
                         text=parts[label], url=_law_url(row))
