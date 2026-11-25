"""Senegal: Conseil constitutionnel decisions and the consolidated Constitution
(conseilconstitutionnel.sn), plus laws, decrees and codes published by the Secrétariat
général du Gouvernement on the Prime Minister's site (primature.sn).

Case law: conseilconstitutionnel.sn (WordPress).
  * Decisions are the "docs" post type; the site's own REST API answers
    /wp-json/wp/v2/docs?search=&page=&per_page= with X-WP-Total, newest first.
    The id is the post slug ("decision-n-5-e-2019"), which is also the page URL /docs/<slug>/.
  * Only 41 decisions are online (2019, 2022-2026). Most are embedded scanned PDFs with no
    text layer (checked 2026-11-06: 2023, 2024, 2025 and 2026 files are all scans); this
    server does no OCR, so for those get_decision returns the reference and the PDF link.
    A few (5/E/2019, 21/E/2022, 2/C/2026) are full HTML text.
  * WordPress search matches the title and the HTML body, so it finds words inside the
    PDF-only decisions' titles only.

Constitution: the Conseil's page /la-constitution/ (REST: /wp-json/wp/v2/pages?slug=...),
  the Constitution of 22 January 2001 consolidated by the Conseil itself with a note under
  each amended article. Last modified 2024-02-09, so later revisions are missing. id
  "constitution".

Legislation: primature.sn (Drupal, Secrétariat général du Gouvernement).
  * Two listings: /publications/lois-et-reglements/lois-et-decrets (about 40 laws and
    decrees, mostly 2020-2024, full text in HTML) and /publications/lois-et-reglements/codes
    (18 codes; the page only holds an exposé des motifs and links to PDF attachments, which
    answered 404 on 2026-11-06). The site's /search/ is disallowed by robots.txt, so the
    listings (about 6 pages) are fetched and filtered locally, kept in memory 6 hours.
  * The id is the node slug under /publications/lois-et-reglements/.
  * Texts are as published, not consolidated.

Legislation: Ministry of Justice (justice.sec.gouv.sn, WordPress), added 2026-11-10.
  * Its "Textes" page lists nothing in static HTML, but the WordPress REST media endpoint
    /wp-json/wp/v2/media?mime_type=application/pdf lists every PDF it hosts (133 on
    2026-11-10). The index keeps titles that name a loi / code / décret / acte uniforme and
    drops reports, guides and macOS "._" duplicates. The id is "mj-<media id>".
  * The PDFs have a text layer: Code pénal, Code de procédure pénale (both a JURISCONSULT
    compilation with amendment notes), COCC, Code de la famille, Code du travail, OHADA
    uniform acts, the 2014 judicial-organisation laws, magistrates' statute, ... Plain
    "Article 12" lines are bolded so the same article splitter works.
  * robots.txt (Yoast) allows everything; no terms or legal-notice page (mentions-legales is
    a 404); footer "© 2026 Direction de la Dématérialisation et de l'Automatisation".

Case law, Cour suprême (added 2026-11-10): JURICAF (juricaf.org, run by AHJUCAF, the association of
francophone supreme courts; UNOFFICIAL, the Cour suprême's own site is down). Terms
(/static/mentionslegales): free access, data under ODbL 1.0. robots.txt: `User-agent: *` allows
/arret/ and /recherche/+/facet_pays..., but DISALLOWS `?page=` and `?tri=`; Fontes is not named. So
search gives page 1 only (10 hits, by relevance), never page 2+, and the archive cannot be walked
here. Filter court=supreme searches the Cour suprême facet; a decision is fetched by id
("SENEGAL-COURSUPREME-20241127-40", /arret/<id>, allowed). Facet count 2026-11-10: 11,580 Sénégal
decisions (Cour suprême 7,458, Cour de cassation 4,095 (pre-2008), Conseil constitutionnel few),
newest 2025-04-23. Not complete.

Not used (2026-11-05/06, rechecked 2026-11-10): www.jo.gouv.sn (Journal officiel; connection timeout on http and
https), www.coursupreme.gouv.sn (Cour suprême; "Plateforme en cours d'optimisation"
maintenance page; coursupreme.sn is a parked domain), justice.sec.gouv.sn (Ministry of
Justice "Textes" page timed out), www.sgg.sn and www.justice.gouv.sn (TLS certificate
errors), www.vie-publique.sn (JO archive, but a civic NGO, not official).
"""
from __future__ import annotations

import re
import time
from urllib.parse import quote, unquote, urljoin

from lxml import html as lxml_html

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from .._http import fold_ascii_ws as _fold
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

CC_HOST = "conseilconstitutionnel.sn"
CC = f"https://{CC_HOST}"
PM_HOST = "primature.sn"
PM = f"https://{PM_HOST}"
PM_BASE = f"{PM}/publications/lois-et-reglements"
PM_LISTS = ("lois-et-decrets", "codes")
JC_HOST = "juricaf.org"
JC = f"https://{JC_HOST}"
_JC_ID = re.compile(r"^SENEGAL-[A-Z]+-\d{8}-[A-Za-z0-9_.-]{1,40}$")
MJ_HOST = "justice.sec.gouv.sn"
MJ = f"https://{MJ_HOST}"
_MJ_KEEP = re.compile(r"\b(lois?|code|cocc|decret|acte uniforme|actes uniforme|traite|ordonnance)\b")
_MJ_DROP = re.compile(r"\b(guide|rapport|revue|repartition|communique|pv|interview|interviews|budget|outils|"
                      r"snpe|audit|republique du senegal)\b")
_PDF_ART = re.compile(r"^((?:Article|ARTICLE|Art\.)\s+(?:premier|PREMIER|1er|unique|UNIQUE|[LRD]\.\s?\d+(?:-\d+)?|\d+(?:-\d+)?(?:\s*(?:bis|ter|quater))?))"
                      r"\b\s*\.?\s*-?\s*(.*)$")
_PDF_HEAD = re.compile(r"^(?:TITRE|CHAPITRE|SECTION|LIVRE)\b\s+\S+")
CONSTITUTION = "constitution"
CONSTITUTION_TITLE = "Constitution de la République du Sénégal du 22 janvier 2001 (version consolidée)"
MAX_LIST_PAGES = 10                 # listing pages per list (4 and 2 on 2026-11-06)
LIST_TTL = 6 * 3600

_SLUG = re.compile(r"^[a-z0-9][a-z0-9_-]{0,119}$")
_MONTHS = {m: i for i, m in enumerate(
    ("janvier", "fevrier", "mars", "avril", "mai", "juin", "juillet", "aout", "septembre",
     "octobre", "novembre", "decembre"), 1)}
_CASE_NO = re.compile(r"(\d+)\s*[/-]?\s*([CE])\s*[/-]?\s*(\d{4})", re.I)
_PDF = re.compile(r"(?:file=|href=[\"'])([^&#\"']+\.pdf)", re.I)
# A bold article heading line: "**Article premier**", "**Article 25-2**", "**Article 2.-** text".
_ART = re.compile(r"^\*\*\s*(?:Article|Art\.)\s+(premier|1er|unique|[LRD]\.\s?\d+(?:-\d+)?|\d+(?:-\d+)?(?:\s*(?:bis|ter|quater))?)"
                  r"\b\s*\.?\s*-?\s*\*\*\s*\.?-?\s*(.*)$", re.I)
_HEAD = re.compile(r"^\*\*\s*((?:TITRE|CHAPITRE|SECTION|LIVRE|PREAMBULE|PRÉAMBULE)\b[^*]*)\*\*\s*(.*)$", re.I)

_lists: dict = {}       # "all" -> (monotonic time, [LawHit])
_docs: dict = {}        # law id -> (title, url, md, as_of, metadata)


def _fr_date(s: str) -> str:
    """First '13 septembre 2024' / '1er avril 2016' in s -> '2024-09-13'; else ''."""
    m = re.search(r"\b(\d{1,2})(?:er)? (" + "|".join(_MONTHS) + r") (\d{4})\b", _fold(s))
    return f"{m[3]}-{_MONTHS[m[2]]:02d}-{int(m[1]):02d}" if m else ""


def _slug(id: str, what: str) -> str:
    s = str(id or "").strip()
    if s.startswith(("https://conseilconstitutionnel.sn/", "https://primature.sn/")):
        s = s.strip("/").rsplit("/", 1)[-1]          # a page URL from a hit
    s = s.lower()
    if not _SLUG.match(s):
        raise BadRequest(f"{what} id must be a page slug such as {'decision-n-5-e-2019' if what == 'decision' else 'code-penal'}, "
                         f"as returned by search; got {id!r}.")
    return s


def _words_match(q: str, title: str) -> bool:
    t = _fold(title)
    return all(w in t for w in _fold(q).split())


async def _json(url: str, params: dict):
    r = await _http.get(url, params=params)
    if r.status_code == 400 and "invalid_page_number" in r.text:
        return None, r
    if r.status_code != 200 or "json" not in r.headers.get("content-type", ""):
        raise SourceError(_http.error("conseilconstitutionnel.sn", "request failed", r.status_code), r.status_code)
    return r.json(), r


# --------------------------------------------------------------------------- #
# Conseil constitutionnel (case law)
# --------------------------------------------------------------------------- #
def _decision_parts(post: dict) -> tuple[str, str, str, str]:
    """-> (display title, case number, title as on the site, content HTML)."""
    raw_title = _http.clean(lxml_html.fromstring(f"<p>{post['title']['rendered'] or ' '}</p>").text_content())
    m = _CASE_NO.search(raw_title) or _CASE_NO.search(post.get("slug", ""))
    cn = f"{int(m[1])}/{m[2].upper()}/{m[3]}" if m else ""
    title = f"Conseil constitutionnel, décision n° {cn}" if cn else f"Conseil constitutionnel, {raw_title}"
    return title, cn, raw_title, post.get("content", {}).get("rendered", "")


def _decision_text(html: str) -> tuple[str, str, str]:
    """-> (markdown text, decision date, pdf url)."""
    md = _http.html_to_md(html)
    pdf = _PDF.search(html)
    if pdf and len(md) < 400:     # an embedded PDF viewer or a bare "Télécharger" file block
        return "", "", unquote(pdf[1])
    m = re.search(r"s[ée]ance du\s+([^\n]{0,40})", md, re.I)
    return md, _fr_date(m[1]) if m else "", ""


# --------------------------------------------------------------------------- #
# Ministry of Justice PDFs (legislation)
# --------------------------------------------------------------------------- #
def _mj_title(media: dict) -> str:
    raw = (media.get("title") or {}).get("rendered") or ""
    return _http.clean(lxml_html.fromstring(f"<p>{raw or ' '}</p>").text_content()).replace("_", " ")


def _mj_type(t: str) -> str:
    f = _fold(t)
    if re.search(r"\bactes? uniforme", f):
        return "Acte uniforme (OHADA)"
    if re.search(r"\b(code|cocc)\b", f) and not re.match(r"(decret|loi)", f):
        return "Code"
    if re.match(r"(j\.?o\b|lois?\b)", f) or re.search(r"\bloi\b", f):
        return "Loi"
    if "decret" in f:
        return "Decret"
    return "Texte"


async def _mj_index() -> list[LawHit]:
    """The Ministry of Justice's legal PDFs, from its WordPress media endpoint."""
    items = []
    for p in (1, 2, 3):
        r = await _http.get(f"{MJ}/wp-json/wp/v2/media",
                            params={"mime_type": "application/pdf", "per_page": 100, "page": p,
                                    "_fields": "id,date,title,source_url"})
        if r.status_code == 400:
            break
        if r.status_code != 200 or "json" not in r.headers.get("content-type", ""):
            raise SourceError(_http.error(MJ_HOST, "media listing failed", r.status_code), r.status_code)
        for m in r.json():
            t = _mj_title(m)
            f = _fold(t)
            if t.startswith(".") or not _MJ_KEEP.search(f) or _MJ_DROP.search(f):
                continue
            num = re.search(r"\b(\d{2,4}\s*-\s*\d+)\b", t)
            items.append(LawHit(id=f"mj-{m['id']}", title=t, type=_mj_type(t),
                                number=re.sub(r"\s", "", num[1]) if num else "",
                                date=_fr_date(t), status="as published (Ministry of Justice PDF)",
                                url=m.get("source_url", "")))
        if int(r.headers.get("X-WP-TotalPages", 1) or 1) <= p:
            break
    return items


def _pdf_md(text: str) -> str:
    """pdf_text lines -> markdown with bold article and heading lines for _sections."""
    out = []
    for ln in text.split("\n"):
        if a := _PDF_ART.match(ln):
            out.append(f"**{a[1]}** {a[2]}".rstrip())
        elif _PDF_HEAD.match(ln) and len(ln) < 160 and "....." not in ln:
            out.append(f"**{ln}**")
        else:
            out.append(ln)
    return "\n".join(out)


async def _mj_doc(media_id: str) -> tuple[str, str, str, str, dict]:
    r = await _http.get(f"{MJ}/wp-json/wp/v2/media/{media_id}", params={"_fields": "id,title,source_url,mime_type,date"})
    if r.status_code in (404, 401):
        raise NotFound(f"No Ministry of Justice document mj-{media_id}.")
    if r.status_code != 200:
        raise SourceError(_http.error(MJ_HOST, "media request failed", r.status_code), r.status_code)
    m = r.json()
    if m.get("mime_type") != "application/pdf":
        raise NotFound(f"mj-{media_id} is not a PDF text at justice.sec.gouv.sn.")
    url, title = m["source_url"], _mj_title(m)
    p = await _http.get(url, max_bytes=40 * 2**20)
    if p.status_code == 404:
        raise NotFound(f"The PDF of mj-{media_id} is missing at justice.sec.gouv.sn ({url}).")
    if p.status_code != 200:
        raise SourceError(_http.error(MJ_HOST, "PDF request failed", p.status_code), p.status_code)
    text = _http.pdf_text(p.content)
    if len(text) < 200:
        text = (f"# {title}\n\nThis PDF has no text layer (a scan) and this server does no OCR. "
                f"Open the original: {url}")
    return title, url, _pdf_md(text), "", {"source": "Ministère de la Justice (PDF as published, not consolidated)",
                                           "PDF": url}


class Senegal(Jurisdiction):
    code = "sn"
    name = "Senegal"
    languages = ("fr",)
    aliases = ("senegal", "sénégal")
    sources = (
        Source(
            name="Conseil constitutionnel du Sénégal (decisions and consolidated Constitution)",
            url=CC,
            covers=("caselaw", "legislation"),
            licence="unknown (no terms page; footer has no rights statement)",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1.5 s spacing, slow host, no 429 seen in ~15 requests (2026-11)",
            terms_url="",
        ),
        Source(
            name="Primature / Secrétariat général du Gouvernement (lois, décrets, codes)",
            url=f"{PM}/publications/lois-et-reglements",
            covers=("legislation",),
            licence="unknown (no terms page; footer '© Primature 2024')",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~12 requests (2026-11)",
            terms_url="",
        ),
        Source(
            name="Ministère de la Justice du Sénégal (codes, lois and décrets as PDF)",
            url=f"{MJ}/publications/textes/",
            covers=("legislation",),
            licence=("unknown (no terms or legal-notice page; footer '© 2026 Direction de la "
                     "Dématérialisation et de l'Automatisation')"),
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~10 requests (2026-11-10); robots.txt allows all",
            terms_url="",
        ),
        Source(
            name="JURICAF (AHJUCAF): Cour suprême decisions (unofficial)",
            url=JC,
            covers=("caselaw",),
            licence="ODbL 1.0 (database right held by AHJUCAF; /static/mentionslegales)",
            commercial_use=True,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~6 requests (2026-11-10)",
            terms_url=f"{JC}/static/mentionslegales",
            official=False,
            warning=("Cour suprême decisions come from JURICAF, the unofficial AHJUCAF database "
                     "(pseudonymised, ODbL licence, attribute JURICAF); its robots.txt forbids "
                     "paging, so only the first 10 hits of a search are shown."),
        ),
    )
    caselaw_filters = {"year": "year of the decision category, e.g. 2024 (2019, 2022-2026 online)",
                       "court": "supreme = Cour suprême decisions from JURICAF (unofficial; first 10 hits "
                                "only, no paging; default is the Conseil constitutionnel). year does not apply "
                                "to court=supreme"}
    legislation_filters = {"type": "constitution, loi, decret or code"}
    min_interval = {CC_HOST: 1.5, PM_HOST: 1.0, MJ_HOST: 1.0, JC_HOST: 1.0}
    notes = ("Case law: Conseil constitutionnel (41 decisions, most scanned PDFs without text); Cour suprême "
             "only through the unofficial JURICAF database (filter court=supreme, first 10 hits, no paging; "
             "get_decision by JURICAF id works). No appeal-court or first-instance (tribunal du travail) decisions. Journal officiel site unreachable (2026-11). "
             "Legislation: Constitution (consolidated to 2024-02), ~60 laws, decrees and codes from primature.sn, "
             "and ~60 PDF texts from the Ministry of Justice (Code pénal, CPP, COCC, Code de la famille, "
             "Code du travail, OHADA acts). Not every law: no Journal officiel online.")
    gaps = (
        ("Cour suprême: official site coursupreme.gouv.sn is a maintenance page (2026-11-10). JURICAF "
         "(unofficial, ODbL) holds ~7,458 decisions to 2025-04, but its robots.txt disallows ?page=, so "
         "search shows 10 hits per query and the archive cannot be listed or searched exhaustively"),
        ("Appeal courts (cours d'appel) and first-instance courts / tribunaux du travail: no decisions in any "
         "source here; Cour suprême decisions that review them can be read, the lower judgment cannot"),
        "Journal officiel: www.jo.gouv.sn connection timeout on http and https (2026-11-05/06 and 2026-11-10); jo.gouv.sn NXDOMAIN",
        ("Statutes not complete: no official full set of laws online; primature.sn and the Ministry of "
         "Justice publish a selection (~120 texts), as published, not consolidated"),
        "Most Conseil constitutionnel decisions (2023-2026 files): scans only, no text",
        ("Conseil constitutionnel decisions before 2019 and from 2020-2021: not published online "
         "(41 decisions)"),
        ("Codes (18 on primature.sn): PDF attachments answered 404 (2026-11-06); the Ministry of "
         "Justice PDFs cover the penal, criminal procedure, civil/commercial (COCC), family and labour codes"),
        ("Consolidated laws and Constitution changes after 2024-02: not published online; sgg.sn "
         "has TLS errors"),
    )
    samples = {
        "caselaw_query": "décision",
        "decision_id": "decision-n-5-e-2019",
        "legislation_query": "décret",
        "law_id": CONSTITUTION,
        "provision": "Article 1",
    }

    # ----------------------------------------------------------------- case law
    async def _jc_search(self, query, limit, page):
        if int(page) > 1:
            raise BadRequest("JURICAF's robots.txt forbids paging, so only page 1 (10 hits) is available; "
                             "narrow the query instead.")
        q = quote((query or "").strip() or "+", safe="") if (query or "").strip() else ""
        fac = "facet_pays:S%C3%A9n%C3%A9gal,facet_pays_juridiction:S%C3%A9n%C3%A9gal_%7C_Cour_supr%C3%AAme"
        r = await _http.get(f"{JC}/recherche/{q}+/{fac}")
        if r.status_code != 200:
            raise SourceError(_http.error("juricaf.org", "search failed", r.status_code), r.status_code)
        doc = lxml_html.fromstring(r.text)
        tm = re.search(r"([\d\s\u202f\xa0]+)\s*résultats? trouvés?", " ".join(doc.text_content().split()))
        total = int(re.sub(r"\D", "", tm[1])) if tm and re.sub(r"\D", "", tm[1]) else None
        hits = []
        for card in doc.xpath('//div[contains(@class,"bloc-search-item")]')[:limit]:
            a = card.xpath('.//a[contains(@href,"/arret/")]')
            if not a:
                continue
            aid = a[0].get("href").rsplit("/", 1)[-1]
            title = _http.clean(a[0].text_content())
            snip = _http.clean(" ".join(card.xpath('.//p[contains(@class,"card-text")]')[0].itertext())) \
                if card.xpath('.//p[contains(@class,"card-text")]') else ""
            m = re.search(r"-(\d{4})(\d{2})(\d{2})-", aid)
            hits.append(DecisionHit(id=aid, title=title, court="Cour suprême",
                                    date=f"{m[1]}-{m[2]}-{m[3]}" if m else "",
                                    case_number=aid.rsplit("-", 1)[-1], snippet=snip[:300],
                                    url=f"{JC}/arret/{aid}"))
        note = ("JURICAF (unofficial AHJUCAF database), Cour suprême only; first 10 hits by relevance, "
                "no paging (robots.txt). Newest decision in the base: 2025-04.")
        if total is not None and len((query or "").split()) > 1:
            # multi-word queries are matched loosely by JURICAF; its count is not a count of the Cour suprême
            # decisions containing the words (it can exceed the whole Cour suprême base), so do not show it
            total = None
            note = "No reliable total: JURICAF's count for a multi-word query is not meaningful. " + note
        return Results(hits, total=total, note=note)

    async def _jc_decision(self, id):
        r = await _http.get(f"{JC}/arret/{id}")
        if r.status_code == 404:
            raise NotFound(f"No JURICAF decision {id!r}.")
        if r.status_code != 200:
            raise SourceError(_http.error("juricaf.org", "decision fetch failed", r.status_code), r.status_code)
        doc = lxml_html.fromstring(r.text)
        art = doc.xpath('//article[@id="textArret"]')
        if not art:
            raise SourceError(f"Error (juricaf.org): no decision text on {JC}/arret/{id}.", 200)
        text = _http.html_to_md(lxml_html.tostring(art[0], encoding="unicode"))
        title = _http.clean(doc.xpath("//title")[0].text_content())
        m = re.search(r"-(\d{4})(\d{2})(\d{2})-", id)
        court = "Cour suprême" if "COURSUPREME" in id else ("Conseil constitutionnel" if "CONSEIL" in id else "Cour de cassation")
        return Decision(id=id, title=title, text=text, url=f"{JC}/arret/{id}", court=court,
                        date=f"{m[1]}-{m[2]}-{m[3]}" if m else "", case_number=id.rsplit("-", 1)[-1],
                        metadata={"source": "JURICAF (AHJUCAF), unofficial, ODbL 1.0; text pseudonymised"})

    async def search_caselaw(self, query, *, limit, page, filters):
        limit = max(1, min(int(limit), 50))
        court = str(filters.get("court", "") or "").strip().lower()
        if court in ("supreme", "cour supreme", "cour suprême"):
            res = await self._jc_search(query, limit, page)
            if str(filters.get("year", "") or "").strip():
                res.total = None  # the count is over all years, not the requested one
                res.note = ("Cannot select Cour suprême decisions by year: JURICAF's date filter is barred to "
                            "automated clients by its robots.txt. The hits are the best matches over all years, "
                            "not restricted to that year, so check each date; a year typed in the query only "
                            "matches text that mentions it. " + (res.note or ""))
            return res
        if court:
            raise BadRequest("court must be 'supreme' (Cour suprême via JURICAF) or omitted.")
        params = {"per_page": limit, "page": max(1, int(page)),
                  "_fields": "id,slug,link,title,content"}
        if (query or "").strip():
            params["search"] = query.strip()
        year = str(filters.get("year", "") or "").strip()
        if year:
            if not re.fullmatch(r"\d{4}", year):
                raise BadRequest("year must be four digits, e.g. 2024.")
            cats, _ = await _json(f"{CC}/wp-json/wp/v2/doc_category", {"slug": year, "_fields": "id,slug"})
            if not cats:
                return Results([], total=0, note=f"No decisions online for {year}.")
            params["doc_category"] = cats[0]["id"]
        data, r = await _json(f"{CC}/wp-json/wp/v2/docs", params)
        total = int(r.headers.get("X-WP-Total", 0) or 0)
        hits = []
        for post in data or []:
            title, cn, _, html = _decision_parts(post)
            md, date, pdf = _decision_text(html)
            snippet = "" if pdf else _http.clean(md[:240])
            hits.append(DecisionHit(id=post["slug"], title=title, court="Conseil constitutionnel",
                                    date=date, case_number=cn, snippet=snippet or "(scanned PDF only)",
                                    url=post["link"]))
        note = "Most decisions are scanned PDFs: only the reference and the PDF link are available."
        if not hits and (query or "").strip():
            note = ("No match in the Conseil constitutionnel (the default court: 41 decisions only, not the "
                    "Cour suprême; for Cour suprême case law such as leases or dismissals repeat the search with "
                    "filters {\"court\": \"supreme\"}). Only titles and HTML text are searched, and most decisions are scanned PDFs, so a "
                    "word from inside a scanned decision never matches even if decisions exist"
                    + (f" for {year}" if year else "") + ". Try query 'décision' (or no query) to list them. " + note)
        return Results(hits, total=total, note=note)

    async def get_decision(self, id):
        if str(id or "").startswith("SENEGAL-"):
            if not _JC_ID.match(id):
                raise BadRequest("JURICAF ids look like 'SENEGAL-COURSUPREME-20241127-40'.")
            return await self._jc_decision(id)
        slug = _slug(id, "decision")
        data, _ = await _json(f"{CC}/wp-json/wp/v2/docs", {"slug": slug, "_fields": "id,slug,link,title,content"})
        if not data:
            raise NotFound(f"No Conseil constitutionnel decision with id {slug!r}.")
        post = data[0]
        title, cn, raw_title, html = _decision_parts(post)
        md, date, pdf = _decision_text(html)
        meta = {"titre sur le site": raw_title}
        if pdf:
            meta["PDF"] = pdf
            md = (f"# {title}\n\nThe Conseil constitutionnel publishes this decision only as a PDF "
                  f"embedded in its page. The decision PDFs checked on 2026-11-06 are scanned images "
                  f"without a text layer, and this server does no OCR, so no text is given here.\n\n"
                  f"Open the original PDF: {pdf}\n\nDecision page: {post['link']}")
        if not md.strip():
            raise SourceError(f"Decision {slug} has an empty page at conseilconstitutionnel.sn.", 200)
        return Decision(id=post["slug"], title=title, text=md, url=post["link"],
                        court="Conseil constitutionnel", date=date, case_number=cn, metadata=meta)

    # -------------------------------------------------------------- legislation
    async def _index(self) -> list[LawHit]:
        hit = _lists.get("all")
        if hit and time.monotonic() - hit[0] < LIST_TTL:
            return hit[1]
        items = [LawHit(id=CONSTITUTION, title=CONSTITUTION_TITLE, type="Constitution", date="2001-01-22",
                        status="consolidated by the Conseil constitutionnel (2024-02-09)",
                        url=f"{CC}/la-constitution/")]
        seen = {CONSTITUTION}
        for lst in PM_LISTS:
            last = 0
            p = 0
            while p <= min(last, MAX_LIST_PAGES - 1):
                # A listing page (~1 s) now and then hangs to the read timeout (seen
                # 2026-11-10, 1 in 5 index builds): short timeout, one retry.
                url, params = f"{PM_BASE}/{lst}", {"page": p} if p else None
                try:
                    r = await _http.get(url, params=params, timeout=20.0)
                except Exception:  # network error
                    r = await _http.get(url, params=params, timeout=20.0)
                if r.status_code != 200:
                    raise SourceError(_http.error("primature.sn", f"listing {lst} failed", r.status_code), r.status_code)
                tree = lxml_html.fromstring(r.text)
                last = max([last] + [int(x) for x in re.findall(r"[?&]page=(\d+)", r.text)])
                for a in tree.xpath('//div[contains(@class,"region--content")]//a[@href]'):
                    href = a.get("href")
                    m = re.match(r"^(?:https://primature\.sn)?/publications/lois-et-reglements/([a-z0-9_-]+)$", href)
                    t = _http.clean(a.text_content())
                    if not m or not t or m[1] in PM_LISTS or m[1] in seen:
                        continue
                    seen.add(m[1])
                    num = re.search(r"n\s*°\s*(\d{2,4}\s*-\s*\d+)", t, re.I)
                    typ = "Code" if lst == "codes" else (t.split()[0].capitalize() if t else "")
                    items.append(LawHit(id=m[1], title=t, type=typ,
                                        number=re.sub(r"\s", "", num[1]) if num else "",
                                        date=_fr_date(t), url=f"{PM_BASE}/{m[1]}"))
                p += 1
        items += await _mj_index()
        return _http.lru_put(_lists, "all", (time.monotonic(), items), 1)[1]

    async def search_legislation(self, query, *, limit, page, filters):
        typ = _fold(filters.get("type", ""))
        if typ and typ not in ("constitution", "loi", "decret", "code"):
            raise BadRequest("type must be one of: constitution, loi, decret, code.")
        found = [h for h in await self._index()
                 if _words_match(query or "", h.title + " " + h.id.replace("-", " "))
                 and (not typ or _fold(h.type).startswith(typ))]
        limit = max(1, int(limit))
        start = (max(1, int(page)) - 1) * limit
        return Results(found[start:start + limit], total=len(found),
                       note="Titles only are searched. Texts are as published, not consolidated "
                            "(except the Constitution, consolidated to 2024-02).")

    async def _doc(self, id) -> tuple[str, str, str, str, dict]:
        slug = _slug(id, "law")
        if slug in _docs:
            return _docs[slug]
        if slug == CONSTITUTION:
            data, _ = await _json(f"{CC}/wp-json/wp/v2/pages",
                                  {"slug": "la-constitution", "_fields": "link,modified,content"})
            if not data:
                raise SourceError("The Constitution page is missing at conseilconstitutionnel.sn.", 404)
            md = _http.html_to_md(data[0]["content"]["rendered"])
            out = (CONSTITUTION_TITLE, data[0]["link"], md, data[0]["modified"][:10],
                   {"source": "Conseil constitutionnel (consolidation with notes on each amendment)"})
            return _http.lru_put(_docs, slug, out, 16)
        if m := re.fullmatch(r"mj-(\d+)", slug):
            return _http.lru_put(_docs, slug, await _mj_doc(m[1]), 16)
        url = f"{PM_BASE}/{slug}"
        r = await _http.get(url)
        if r.status_code == 404:
            raise NotFound(f"No text {slug!r} at primature.sn.")
        if r.status_code != 200:
            raise SourceError(_http.error("primature.sn", "text request failed", r.status_code), r.status_code)
        tree = lxml_html.fromstring(r.text)
        art = tree.xpath('//article[contains(@class,"node--view-mode-full")]')
        if not art:
            raise NotFound(f"{slug!r} is not a text page at primature.sn.")
        name = art[0].xpath('.//span[@property="schema:name"]/@content')
        title = _http.clean(name[0]) if name else slug
        body = art[0].xpath('.//div[contains(@class,"field--name-body")]')
        md = _http.html_to_md(lxml_html.tostring(body[0], encoding="unicode")) if body else ""
        meta = {}
        files = art[0].xpath('.//div[contains(@class,"field--name-field-pieces-jointes")]//a[@href]')
        if files:
            lines = [f"- {_http.clean(a.text_content())}: {urljoin(PM, a.get('href'))}" for a in files]
            md += ("\n\n## Pièces jointes\n\nThe page links these PDF attachments (not included here; "
                   "the ones checked on 2026-11-06 answered 404):\n\n" + "\n".join(lines))
            meta["pièces jointes"] = str(len(files))
            key = _fold(title).replace(" ", "")
            full = [h for h in await self._index() if h.id.startswith("mj-") and h.type == "Code"
                    and _fold(h.title).replace(" ", "") == key]
            if full:
                md += (f"\n\nThis page holds only the exposé des motifs or amending law, not the code itself. "
                       f"The full text of the code is the Ministry of Justice PDF: id {full[0].id} "
                       f"(get_legislation_text / get_legislation_toc).")
        if not md.strip():
            raise SourceError(f"Empty text page {slug!r} at primature.sn.", 200)
        return _http.lru_put(_docs, slug, (title, url, md, "", meta), 16)

    @staticmethod
    def _sections(md: str) -> list[tuple[str, int, str, int, int]]:
        """-> [(heading title, level, provision label or '', start line, end line)]."""
        lines = md.split("\n")
        heads = []
        for i, ln in enumerate(lines):
            a = _ART.match(ln.strip())
            if a:
                num = a[1].lower()
                num = "1" if num in ("premier", "1er") else re.sub(r"\s+", " ", num)
                if re.match(r"[lrd]\.", num):
                    num = num.upper().replace(" ", "")      # Code du travail: "Article L.84"
                heads.append([f"Article {a[1]}", 1, f"Article {num}", i])
                continue
            h = _HEAD.match(ln.strip())
            if h:
                nxt = next((x for x in lines[i + 1:i + 4] if x.strip()), "")
                sub = _http.clean(h[2] or (nxt.strip("* ") if nxt.startswith("**") and not _ART.match(nxt) else ""))
                heads.append([_http.clean(h[1]) + (f" — {sub}" if sub else ""), 0, "", i])
        out, seen = [], set()
        for k, (t, lvl, prov, i) in enumerate(heads):
            end = heads[k + 1][3] if k + 1 < len(heads) else len(lines)
            if prov in seen:
                prov = ""
            seen.add(prov)
            out.append((t, lvl, prov, i, end))
        return out

    async def get_legislation_toc(self, id):
        title, url, md, _, _ = await self._doc(id)
        entries = [TocEntry(title=t, level=lvl, provision=p) for t, lvl, p, _, _ in self._sections(md)]
        if not entries:
            entries = [TocEntry(title=title, level=0, provision="")]
        return Toc(id=_slug(id, "law"), title=title, url=url, entries=entries)

    async def get_legislation_provision(self, id, provision):
        title, url, md, as_of, _ = await self._doc(id)
        want = _fold(provision)
        want = re.sub(r"^(article|art\.?)\s*", "", want).strip(" .-")
        want = "1" if want in ("premier", "1er") else want
        lines = md.split("\n")
        for t, _, prov, s, e in self._sections(md):
            have = _fold(prov)[len("article "):]
            if prov and (have == want or (re.fullmatch(r"[lrd]\.\d+(?:-\d+)?", have) and have[2:] == want)):
                return Provision(law_id=_slug(id, "law"), law_title=title, provision=prov,
                                 text="\n".join(lines[s:e]).strip(), url=url, as_of=as_of)
        labels = [p for _, _, p, _, _ in self._sections(md) if p]
        if not labels:
            raise NotFound(f"No provision {provision!r} in {title}: this text is indexed by heading only, "
                           "its article numbers cannot be reached one by one. Use get_legislation_text.")
        raise NotFound(f"No provision {provision!r} in {title}. Use labels from the TOC, e.g. '{labels[0]}'.")

    async def get_legislation_text(self, id):
        title, url, md, as_of, meta = await self._doc(id)
        return LawText(id=_slug(id, "law"), title=title, text=md, url=url, as_of=as_of, metadata=meta)
