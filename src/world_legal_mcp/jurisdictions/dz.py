"""Algeria: legislation from the Journal Officiel (joradp.dz, Secrétariat Général du
Gouvernement) and case law from the Cour constitutionnelle (cour-constitutionnelle.dz).

Gotchas this code encodes (verified 2026-11-06):
  * joradp.dz is an old ISAPI (.dll) site in cp1252. Search is a POST to
    /SCRIPTS/Jof_Rec.dll/RecPost that needs a session number ("Client") taken from the
    menu page /SCRIPTS/Jo_Con.dll/Fr; without it the answer is "Système réinitialisé".
    Paging is stateful: AffPost with dfon=3 is "next page" (20 texts per page).
  * Keywords (zdes) must be words from the site's own lexicon ("Descripteurs inexistants"
    otherwise); words are joined with '+', ztyp=1 = all words, 2 = any word. A text number
    (zntx, e.g. 08-09) and a nature (znat, e.g. "Loi") are separate fields.
  * Texts are only available as the PDF of the whole Journal Officiel issue
    (/FTP/jo-francais/{year}/F{year}{jo:03}.pdf, page = issue page). Issues before 2002
    (checked: 1994, 1996, 1998, 2000 and 2001 are scans, 2002-2004 have text) are scans with no text layer (no OCR here), so only the reference is returned for them.
    We cut the text from its heading on the given page to the next text after its
    "Fait à Alger" signature. These are texts as published, not consolidated.
  * Older PDFs (2008 and around) have a broken font map: é->Ø, è->Ł, ê->Œ, ù->ø, û->ß,
    em dash -> \\x97. _fix_glyphs repairs it.
  * The French edition is the official translation; the Arabic edition is authoritative.

Case law (cour-constitutionnelle.dz, WordPress, verified 2026-11-06):
  * The server sends an incomplete TLS certificate chain. It works through the OS trust
    store (_http uses truststore; macOS and Windows fetch the missing intermediate), but
    fails verification on Linux.
  * Decisions and opinions (avis) of the Court and of the former Conseil constitutionnel
    (1989-2020) are French posts, mostly one post per year and kind ("Décisions 2025",
    "Avis 1997"), each decision a WPBakery accordion section whose title is the decision's
    heading; a few posts hold one decision as plain content. No per-decision page exists.
  * Search: /wp-json/wp/v2/posts?categories=<decision categories>&search=... (MySQL LIKE,
    accent- and case-insensitive, all words, matched per post). We split the matching posts
    into decisions and keep those whose own text has every word. robots.txt allows all.
  * The id is the decision's heading as the Court cites it, number + Gregorian date:
    "Décision n° 01/D.C.C/EI/25 du 7 janvier 2025" (numbers alone repeat across series
    and years; spacing inside them varies, so matching ignores spaces and punctuation).
    get_decision searches the posts for "<month> <year>" of that date.
  * French edition only; the Arabic one (authoritative) is a separate set of posts.
"""
from __future__ import annotations

import io
import re
import time
import unicodedata
from html import unescape
from urllib.parse import urlencode

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

JORADP = "https://www.joradp.dz"
CC = "https://cour-constitutionnelle.dz"
# French categories holding decisions / avis (from /wp-json/wp/v2/categories, 2026-11-06):
# per-year "Avis 19xx/20xx" and "Année 19xx" (electoral), constitutionnalité, conformité,
# exception d'inconstitutionnalité, contentieux électoral, remplacement de députés,
# levée de l'immunité, autres / dernières décisions.
_CC_CATS = ("473,471,469,173,167,161,157,155,151,147,143,141,139,137,135,192,190,188,186,133,"
            "131,129,127,125,123,121,119,115,113,105,103,101,99,4,81,91,184,350,352,577,579,583,"
            "585,646,841,925,993,1036,1274")

_MONTHS = {m: i for i, m in enumerate(
    ("janvier", "fevrier", "mars", "avril", "mai", "juin", "juillet", "aout", "septembre",
     "octobre", "novembre", "decembre"), 1)}
# The "Nature" options of the joradp search form, as the site spells them.
_NATURES = ("Arrêté", "Arrêté de wali", "Arrêté inter", "Avis", "Barème", "Circulaire",
            "Circulaire inter", "Convention", "Décision", "Décision conjointe", "Décision inter",
            "Décision Org.Constit", "Déclaration", "Décret", "Décret exécutif",
            "Décret législatif", "Décret présidentiel", "Délibération", "Délibération du HCE",
            "Instruction", "Instruction inter", "Loi", "Loi organique", "Ordonnance",
            "Proclamation", "Rapport", "Règlement", "Résolution")
_C1 = str.maketrans({"\x97": "—", "\x96": "–", "\x92": "’", "\x9c": "œ"})   # cp1252 leftovers
_GLYPHS = str.maketrans({"Ø": "é", "Ł": "è", "Œ": "ê", "ø": "ù", "ß": "û", "˙": "Ç"})


def _fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().lower()


def _fr_date(s: str) -> str:
    """'... correspondant au 25 février 2008' or '25 Février 2008' -> '2008-02-25'."""
    f = _fold(s)
    pat = r"(\d{1,2})(?:er)? (" + "|".join(_MONTHS) + r") (\d{4})"
    m = re.search(r"correspondant au " + pat, f) or re.search(pat, f)
    if not m:
        return ""
    return f"{m[3]}-{_MONTHS[m[2]]:02d}-{int(m[1]):02d}"


def _nature(s: str) -> str:
    """User spelling of a nature -> the form's option, or ''."""
    f = _fold(s)
    for n in _NATURES:
        if _fold(n) == f:
            return n
    return ""


def _fix_glyphs(text: str) -> str:
    """Repair one page of a 2000s-era JO PDF whose font maps é/è/ê… to Ø/Ł/Œ…, and the
    doubled degree signs of bold headings ("n°° 05-02 du … 1426°°")."""
    text = text.translate(_C1)
    if re.search(r"\wØ\w|Ø\b", text):
        text = text.translate(_GLYPHS)
    return re.sub(r"°°", "", re.sub(r"(?<=n)°°", "°", text))


_SECTION_HEAD = re.compile(r"^(LOIS|ORDONNANCES|DECRETS|ARRETES|DECISIONS|AVIS|CONVENTIONS|ACCORDS|"
                           r"ANNONCES|COMMUNICATIONS|RESOLUTIONS|PROCLAMATIONS|DELIBERATIONS|"
                           r"DECLARATIONS|RAPPORTS|CIRCULAIRES|INSTRUCTIONS)\b[A-Z ,\'’-]*$")


def _columns(layout: str) -> list[str]:
    """Reading order for a two-column page laid out by pypdf's layout mode: find the gutter
    (the character column that is blank on most lines), then emit each band between
    full-width lines as left column, then right column."""
    rows = [r for r in layout.splitlines() if not _is_header(r.strip())]
    # The running header's date sometimes wraps onto its own row at the top of the page.
    while rows and (not rows[0].strip() or re.fullmatch(r"\d{1,2}(?:er)? \w+ \d{4}", rows[0].strip())):
        rows.pop(0)
    full = [r for r in rows if r.strip()]
    if not full:
        return rows
    width = sorted(len(r) for r in full)[len(full) * 3 // 4]   # robust to one over-long line
    if width < 60:
        return rows

    def hits(i):
        return sum(1 for r in full if len(r) > i and r[i] != " ")
    lo, hi = int(width * 0.35), int(width * 0.65)
    g = min(range(lo, hi), key=lambda i: (hits(i), abs(i - width / 2)))
    if hits(g) > len(full) * 0.3:          # no clear gutter: one column
        return rows
    out, left, right = [], [], []
    for r in rows:
        text, ind = r.strip(), len(r) - len(r.lstrip())
        heading = ind >= g * 0.3 and _SECTION_HEAD.match(text)   # centred "DECRETS", "LOIS" …
        cut = g
        if r[g - 1:g + 2].strip():         # a wide (bold) line may run into the gutter
            gap = [m.end() for m in re.finditer(r"   +", r[:g + 12]) if m.end() >= g * 0.6]
            cut = min(gap, key=lambda e: abs(e - g)) if gap else (g if r[g:g + 1] == " " else None)
        if cut is None or heading:         # a full-width line
            out += left + right + [r]
            left, right = [], []
        else:
            left.append(r[:cut])
            right.append(r[cut:])
    return out + left + right


def _pdf_pages(data: bytes) -> list[list[str]]:
    """Cleaned, non-empty lines per PDF page in reading order (empty pages kept, so
    index = page - 1). Like _http.pdf_text, but column-aware: the JO is set in two
    columns and pypdf's plain mode interleaves them on recent issues."""
    from pypdf import PdfReader
    out = []
    for p in PdfReader(io.BytesIO(data)).pages:
        try:
            rows = _columns(p.extract_text(extraction_mode="layout") or "")
        except Exception:               # layout mode fails on a few odd pages
            rows = (p.extract_text() or "").splitlines()
        out.append([ln for ln in (_http.clean(x) for x in _fix_glyphs("\n".join(rows)).split("\n")) if ln])
    return out


# --------------------------------------------------------------------------- #
# Journal Officiel (legislation)
# --------------------------------------------------------------------------- #
_ID = re.compile(r"^(?P<title>.+?)\s*[—–-]+\s*JO n° ?(?P<jo>\d{1,3})/(?P<year>\d{4}),? p\. ?(?P<page>\d+)$",
                 re.I)
_SHORT = re.compile(r"^(?P<nat>[^\d]+?)\s*(?:n\s*°|no\.?|n°)?\s*(?P<num>\d{2,4}-\d{1,4}(?:\s*bis)?)$", re.I)
_TEXT_START = re.compile(
    r"^(Loi|Loi organique|Ordonnance|Décret(?: présidentiel| exécutif| législatif)?|Arrêté"
    r"(?: interministériel)?|Décision|Avis|Instruction|Circulaire|Délibération|Règlement|"
    r"Résolution|Proclamation|Déclaration|Convention|Rapport)\b.*\b(n ?°|du)\b")
_ART = re.compile(r"^(?:Article|Art\.)\s*(1er|\d+(?:\s*(?:bis|ter|quater|quinquies|sexies|"
                  r"septies|octies|nonies|decies))?(?:\s*\d+)?)\s*\.?\s*[—–-]", re.I)
_HEAD = re.compile(r"^(LIVRE|Livre|TITRE|Titre|CHAPITRE|Chapitre|Section|Sous-section|"
                   r"Dispositions)\b")
_issues: dict[tuple[int, int], tuple[float, list[list[str]]]] = {}


def _jo_url(year: int, jo: int, page: int = 0) -> str:
    """The French PDF, as the site's JoOpen() builds it: one PDF per issue from 1994,
    one scanned PDF per page before."""
    if year < 1994:
        part = "Jo6283" if year < 1984 else "Jo8499"
        return f"{JORADP}/{part}/{year}/{jo:03d}/Fp{page}.pdf"
    return f"{JORADP}/FTP/jo-francais/{year}/F{year}{jo:03d}.pdf" + (f"#page={page}" if page else "")


async def _session() -> str:
    r = await _http.get(f"{JORADP}/SCRIPTS/Jo_Con.dll/Fr")
    m = re.search(r'name="Client" type="hidden" value="(\d+)"', r.text)
    if r.status_code != 200 or not m:
        raise SourceError("joradp.dz: no search session number on the menu page", r.status_code)
    return m[1]


def _post_body(fields: dict) -> bytes:
    return urlencode(fields, encoding="cp1252", errors="replace").encode("ascii")


async def _jo_post(path: str, fields: dict) -> str:
    r = await _http.post(f"{JORADP}/SCRIPTS/{path}", content=_post_body(fields),
                         headers={"Content-Type": "application/x-www-form-urlencoded"})
    if r.status_code != 200:
        raise SourceError("joradp.dz search failed", r.status_code)
    html = r.content.decode("cp1252", errors="replace")
    err = re.search(r"id=cor>([^<]*)", html)
    if err and "inexistant" not in err[1] and "Aucun r" not in err[1]:   # no hits is not an error
        raise SourceError(f"joradp.dz: {_http.clean(err[1])}", r.status_code)
    return html


def _cell(s: str) -> str:
    return _http.clean(_http.html_to_md(s).replace("\\", ""))


def _parse_hits(html: str) -> list[LawHit]:
    hits = []
    for block in re.split(r'<tr bgcolor="#78a7b9">', html)[1:]:
        m = re.search(r'JoOpen\("(\d{4})","(\d+)","(\d+)","F"\)', block)
        if not m:
            continue
        year, jo, pg = int(m[1]), int(m[2]), int(m[3])
        rows = [_cell(c) for c in re.findall(r"<tr><td colspan=6>(.*?)</td></tr>", block, re.S)]
        rows = [r for r in rows if r]
        if not rows:
            continue
        title_line = rows[0]
        desc = rows[-1] if len(rows) > 2 and not rows[-1].startswith("JO N°") else ""
        top = re.split(r"<tr><td></td><td colspan=5>", block)[1:]
        rels = [_fold(_cell(t.split("</td>")[0])) for t in top]
        status = "abrogé" if any(r.startswith("abroge") for r in rels) else \
            "modifié" if any(r.startswith("modifie") for r in rels) else ""
        num = re.search(r"n° ?(\S+)", title_line)
        nat = re.match(r"^(.*?)\s+(?:n°|du)(?=\s)", title_line)
        hits.append(LawHit(
            id=f"{title_line} — JO n° {jo}/{year} p. {pg}",
            title=f"{title_line} {desc}".strip() if desc else title_line,
            type=nat[1] if nat else "",
            number=num[1] if num else "",
            date=_fr_date(title_line),
            status=status,
            snippet=next((r for r in rows[1:] if r.startswith("JO N°")), ""),
            url=_jo_url(year, jo, pg)))
    return hits


def _total(html: str) -> int | None:
    m = re.search(r"de (\d+)</td>", html)
    return int(m[1]) if m else (0 if "inexistant" in html or "Aucun r" in html else None)


_EMPTY = {"Start": "0", "zsec": "", "zmin": "", "znat": "", "znjo": "", "znjd": "", "znjf": "",
          "zntx": "", "zntd": "", "zntf": "", "zdes": "", "ztyp": "1"}


def _dmy(v: str, name: str) -> str:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v or ""):
        raise BadRequest(f"{name} must be YYYY-MM-DD, got {v!r}")
    return f"{v[8:10]}/{v[5:7]}/{v[:4]}"


async def _search(fields: dict, page: int) -> tuple[str, int | None]:
    client = await _session()
    html = await _jo_post("Jof_Rec.dll/RecPost", {**_EMPTY, **fields, "Client": client})
    for _ in range(page - 1):
        html = await _jo_post("JOF_Rec.dll/AffPost", {"Client": client, "dfon": "3", "dval": "1"})
    return html, _total(html)


async def _resolve(law_id: str) -> tuple[str, int, int, int]:
    """id -> (title line, year, jo, page). Accepts the full id or 'Loi n° 08-09' / 'loi 08-09'."""
    s = _http.clean(law_id)
    m = _ID.match(s)
    if m:
        return m["title"], int(m["year"]), int(m["jo"]), int(m["page"])
    m = _SHORT.match(s)
    nat = _nature(m["nat"]) if m else ""
    if not nat:
        raise BadRequest("law id looks like 'Loi n° 08-09' (nature + number) or the full id from "
                         "search_legislation, e.g. 'Loi n° 08-09 du 25 Février 2008 — JO n° 21/2008 p. 3'")
    html, _ = await _search({"znat": nat, "zntx": m["num"].replace(" ", ""), "ztyp": "2"}, 1)
    hits = [h for h in _parse_hits(html) if _fold(h.type) == _fold(nat)]
    if not hits:
        raise NotFound(f"no {nat} n° {m['num']} in the Journal Officiel index")
    mm = _ID.match(hits[0].id)
    return mm["title"], int(mm["year"]), int(mm["jo"]), int(mm["page"])


async def _issue(year: int, jo: int) -> list[list[str]]:
    key = (year, jo)
    if key in _issues and time.monotonic() - _issues[key][0] < 3600:
        return _issues[key][1]
    r = await _http.get(_jo_url(year, jo))
    if r.status_code == 404:
        raise NotFound(f"no PDF for Journal Officiel n° {jo}/{year}")
    if r.status_code != 200 or not r.content.startswith(b"%PDF"):
        raise SourceError(f"joradp.dz: could not fetch JO n° {jo}/{year}", r.status_code)
    pages = _pdf_pages(r.content)
    return _http.lru_put(_issues, key, (time.monotonic(), pages), 4)[1]


def _is_header(ln: str) -> bool:
    """Running page headers, bare page numbers and the printer's footer. Case-sensitive: the
    body phrase "sera publiée au Journal officiel de la République" is not a header."""
    return ("JOURNAL OFFICIEL DE LA" in ln or ln.startswith("Imprimerie officielle")
            or re.fullmatch(r"\d{1,4}", ln) is not None)


def _start_pattern(title: str) -> re.Pattern:
    num = re.search(r"n° ?(\d{2,4}-\d{1,4})", title)
    if num:
        return re.compile(r"\bn\s*" + re.escape(num[1]) + r"\b")   # on folded text: '°' is gone
    d = _fr_date(title)
    if d:
        y, mo, dd = d.split("-")
        month = next(k for k, v in _MONTHS.items() if v == int(mo))
        return re.compile(rf"\b{int(dd)}(?:er)? {month} {y}\b")
    return re.compile(re.escape(_fold(title)[:20]))


def _cut(pages: list[list[str]], page: int, title: str) -> list[str]:
    """The lines of one text, from its heading on `page` to its signature."""
    lines = [ln for p in pages[page - 1:] for ln in p
             if not _is_header(ln) and not re.fullmatch(r"[—–_-]+", ln)]
    pat, nat = _start_pattern(title), _fold(title.split(" n°")[0].split(" du ")[0])
    start = None
    for i, ln in enumerate(lines):
        f = _fold(ln)
        if re.match(re.escape(nat) + r"\b", f) and (pat.search(f) or pat.search(_fold(" ".join(lines[i:i + 3])))):
            start = i
            break
    if start is None:
        return []
    end, signed = len(lines), False
    for i in range(start + 1, len(lines)):
        ln = lines[i]
        if ln.startswith("Fait à Alger"):
            signed = True
            continue
        caps = len(ln) > 3 and ln == ln.upper() and re.search(r"[A-Z]{4}", ln) and not ln.endswith(".")
        # A new text starts: after the signature, or (texts without one, e.g. "Par arrêté du …")
        # a heading right after a line that closed a sentence.
        if (signed and (_TEXT_START.match(ln) or caps)) or \
                ((_TEXT_START.match(ln) or _SECTION_HEAD.match(ln) or re.match(r"MINIST[EÈ]RE [A-Z]", ln))
                 and lines[i - 1].endswith(".") and i - start > 3):
            end = i
            break
    return lines[start:end]


def _paragraphs(lines: list[str]) -> list[str]:
    """Join hard-wrapped PDF lines into paragraphs."""
    out: list[str] = []
    for ln in lines:
        new = (not out or _ART.match(ln) or _HEAD.match(ln) or ln.startswith(("Vu ", "Fait à"))
               or re.match(r"^(\d+|[a-z])\s*[-—).]\s", ln) or out[-1].endswith((".", ";", ":"))
               or (ln.isupper() and len(ln) > 3))
        if new:
            out.append(ln)
        else:
            out[-1] = out[-1][:-1] + ln if out[-1].endswith("-") and not out[-1].endswith(" -") \
                else f"{out[-1]} {ln}"
    return out


def _label(raw: str) -> str:
    raw = re.sub(r"\s+", " ", raw.strip().lower())
    return "1" if raw == "1er" else raw


def _articles(pars: list[str]) -> tuple[list[TocEntry], dict[str, str]]:
    toc, arts, cur = [], {}, None
    for p in pars:
        m = _ART.match(p)
        if m and _label(m[1]) not in arts:
            cur = _label(m[1])
            arts[cur] = p
            toc.append(TocEntry(title=p[:90] + ("…" if len(p) > 90 else ""), level=1, provision=cur))
        elif _HEAD.match(p) and len(p) < 160:
            cur = None
            toc.append(TocEntry(title=p, level=0))
        elif cur:
            arts[cur] += "\n\n" + p
    return toc, arts


async def _law(law_id: str) -> tuple[str, str, list[str], str]:
    """-> (id, title, paragraphs, url)."""
    if _fold(law_id).startswith("constitution"):
        c = await _constitution()
        return c["id"], c["title"], c["pars"], c["url"]
    title, year, jo, page = await _resolve(law_id)
    url = _jo_url(year, jo, page)
    if year < 1994:
        raise SourceError(f"JO n° {jo}/{year} exists only as scanned page images (no text layer); "
                          f"open it at {url}")
    canon = f"{title} — JO n° {jo}/{year} p. {page}"
    pages = await _issue(year, jo)
    if not any(pages):
        raise SourceError(f"JO n° {jo}/{year} is a scan without a text layer (issues before 2002); "
                          f"open it at {url}")
    if page > len(pages):
        raise NotFound(f"JO n° {jo}/{year} has no page {page}")
    lines = _cut(pages, page, title)
    if not lines:
        raise SourceError(f"could not find the heading of {title} on page {page} of JO n° {jo}/{year}; "
                          f"open it at {url}")
    pars = _paragraphs(lines)
    head = pars[0] = re.sub(r"\bn\s+°", "n°", pars[0])
    return canon, head if len(head) < 300 else title, pars, url


# The Constitution: the JO prints it after its promulgation decree (n° 20-442) with no text
# heading of its own, so _cut cannot find it. The SGG offers the 2020 text as its own PDF;
# later revisions are laws "portant révision constitutionnelle" that the JO index lists under
# "Modifié par" on decree 20-442 and that restate each changed article in full
# (« Art. 87. — … »). We apply those restated articles to the 2020 text.
_CONST_PDF = f"{JORADP}/TRV/FConsti.pdf"
_const: dict[str, tuple[float, dict]] = {}


def _restated(pars: list[str]) -> dict[str, list[str]]:
    """Articles a revision law restates in quotes: label -> paragraphs, quotes removed."""
    out: dict[str, list[str]] = {}
    cur = None
    for p in pars:
        q = re.match(r"^«\s*(.*)", p)
        if q and _ART.match(q[1]):
            cur = _label(_ART.match(q[1])[1])
            out[cur] = [q[1]]
        elif _ART.match(p):              # the revision law's own next article
            cur = None
        elif cur and not re.fullmatch(r"»\s*\.?", p):   # a stray closing quote cut off by the columns
            out[cur].append(p)
    return {k: v[:-1] + [re.sub(r"\s*»\s*\.?\s*$", "", v[-1])] for k, v in out.items()}


def _apply(pars: list[str], new: dict[str, list[str]], ref: str) -> list[str]:
    """Replace (or add, after the preceding article) whole articles in a paragraph list. A
    restatement with "(… sans changement …)" gaps is put before the old text, not over it."""
    blocks: list[tuple[str | None, list[str]]] = []
    for p in pars:
        m = _ART.match(p)
        if m or _HEAD.match(p) or not blocks:
            blocks.append((_label(m[1]) if m else None, [p]))
        else:
            blocks[-1][1].append(p)
    seen = {k for k, _ in blocks}
    out = []
    for k, ps in blocks:
        if k in new and "sans changement" in " ".join(new[k]):
            out += new[k] + [f"[{ref} restates this article only in part (the parts marked « sans "
                             f"changement » are unchanged). The article before that revision:]"] + ps
        else:
            out += new.get(k, ps) if k else ps
        nxt = str(int(k) + 1) if k and k.isdigit() else None
        while nxt in new and nxt not in seen:
            out += new[nxt]
            seen.add(nxt)
            nxt = str(int(nxt) + 1)
    return out


async def _constitution() -> dict:
    if "c" in _const and time.monotonic() - _const["c"][0] < 3600:
        return _const["c"][1]
    r = await _http.get(_CONST_PDF)
    if r.status_code != 200 or not r.content.startswith(b"%PDF"):
        raise SourceError("joradp.dz: could not fetch the Constitution PDF", r.status_code)
    lines = [ln for p in _pdf_pages(r.content) for ln in p
             if not _is_header(ln) and not re.fullmatch(r"[—–_-]+", ln)]
    pars = _paragraphs(lines)
    # Revisions since 2020, oldest first, from the JO index entry of the promulgation decree.
    html, _ = await _search({"znat": "Décret présidentiel", "zntx": "20-442", "ztyp": "2"}, 1)
    flat = _http.clean(unescape(re.sub(r"<[^>]+>", " ", html)))
    revs = sorted({(m[3], int(m[2]), f"{m[1]} — JO n° {m[2]}/{m[3]} p. {m[4]}") for m in re.finditer(
        r"(Loi n° \d{2}-\d{1,3} du \d{1,2} \S+ \d{4}) JO N° (\d+) du \d{1,2} \S+ (\d{4}), Page (\d+)"
        r" Portant révision constitutionnelle", flat)})
    applied, as_of = [], "2020-12-30"
    for _, _, rid in revs:
        canon, _, rpars, _ = await _law(rid)
        new = _restated(rpars)
        if new:
            pars = _apply(pars, new, canon.split(" — ")[0])
            applied.append(f"{canon} (art. {', '.join(new)})")
            as_of = max(as_of, _fr_date(canon))
    c = {"id": "Constitution",
         "title": "Constitution de la République algérienne démocratique et populaire "
                  "(révision constitutionnelle du 1er novembre 2020" +
                  (", avec les révisions ultérieures)" if applied else ")"),
         "pars": pars, "url": _CONST_PDF, "as_of": as_of, "applied": applied}
    return _http.lru_put(_const, "c", (time.monotonic(), c), 1)[1]

# --------------------------------------------------------------------------- #
# Cour constitutionnelle (case law)
# --------------------------------------------------------------------------- #
_MONTH_NAMES = ("janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
                "septembre", "octobre", "novembre", "décembre")
_SECTION = re.compile(r"\[vc_tta_section\b(.*?)\](.*?)\[/vc_tta_section\]", re.S)
_HEADING = re.compile(r"^(Décision|Avis)\b\s*(?:(?:n|N)\s*°\s*(.*?))?\s+(?:du|Du)\s+(.+)$")
_cc_posts: dict[str, list[dict]] = {}


def _loose(s: str) -> str:
    """Decision number without spaces/punctuation: '01/ D.C.C/ C.C/25' -> '01DCCCC25'."""
    return re.sub(r"[^0-9A-Z]", "", _fold(s).upper())


def _fr_long(iso: str) -> str:
    y, m, d = iso.split("-")
    return f"{int(d)} {_MONTH_NAMES[int(m) - 1]} {y}"


def _cc_record(heading: str, body: str, link: str, anchor: str) -> dict | None:
    heading = _http.clean(heading.replace("\u00ab", " ").replace("\u00bb", " ").replace("″", " "))
    m = _HEADING.match(heading)
    date = _fr_date(heading)
    if not m or not date:
        return None
    text = _http.html_to_md(re.sub(r"\[/?vc_[^\]]*\]", "\n", body))
    if len(text) < 100:
        return None
    kind = m[1]
    number = re.sub(r"\s*([/-])\s*|(?<=\.)\s+", r"\1", _http.clean(m[2] or "")).strip(" .")
    cid = f"{kind} n° {number} du {_fr_long(date)}" if number else f"{kind} du {_fr_long(date)}"
    head = text[:400]
    court = "Conseil constitutionnel" if re.search(r"Conseil constitutionnel", head, re.I) and \
        not re.search(r"Cour constitutionnelle", head, re.I) else "Cour constitutionnelle"
    return {"id": cid, "kind": kind, "number": number, "date": date, "title": heading,
            "court": court, "text": text, "url": link + (f"#{anchor}" if anchor else "")}


def _cc_split(post: dict) -> list[dict]:
    html = re.sub(r'<div class="pdfprnt-buttons.*?</div>', "", post["content"]["rendered"], flags=re.S)
    html = html.replace("&Prime;", "\u00bb").replace("&#8243;", "\u00bb")
    out = []
    for attrs, body in _SECTION.findall(html):
        t = re.search(r"title=\s*\u00bb?(.*?)\s*\u00bb?\s+tab_id=\s*\u00bb?\s*([\w-]*)", attrs, re.S)
        if t:
            rec = _cc_record(_http.html_to_md(t[1]), body, post["link"], t[2])
            if rec:
                out.append(rec)
    if not out and "[vc_tta_section" not in html:     # one decision as the whole post
        rec = _cc_record(_http.html_to_md(post["title"]["rendered"]), html, post["link"], "")
        if rec:
            out.append(rec)
    return out


async def _cc_search(terms: str) -> list[dict]:
    """Decisions in every post the site's own search matches, deduplicated, newest first."""
    if terms in _cc_posts:
        return _cc_posts[terms]
    posts, page = [], 1
    while True:
        r = await _http.get(f"{CC}/wp-json/wp/v2/posts", params={
            "categories": _CC_CATS, "search": terms, "per_page": 100, "page": page,
            "_fields": "id,link,title,content"})
        if r.status_code != 200:
            raise SourceError("cour-constitutionnelle.dz: search failed", r.status_code)
        posts += r.json()
        if page >= int(r.headers.get("X-WP-TotalPages") or 1) or page >= 3:
            break
        page += 1
    seen, out = set(), []
    for post in posts:
        for d in _cc_split(post):
            key = (_loose(d["number"]), d["date"], d["kind"])
            if key not in seen:
                seen.add(key)
                out.append(d)
    out.sort(key=lambda d: d["date"], reverse=True)
    return _http.lru_put(_cc_posts, terms, out, 8)


def _snippet(text: str, words: list[str]) -> str:
    f = _fold(text)
    i = min((f.find(w) for w in words if f.find(w) >= 0), default=0)
    return _http.clean(text[max(0, i - 80): i + 220])


class Algeria(Jurisdiction):
    code = "dz"
    name = "Algeria"
    languages = ("fr", "ar")
    aliases = ("dza", "algerie", "algérie", "الجزائر")
    sources = (
        Source("Journal Officiel de la République Algérienne (JORADP), Secrétariat Général du "
               "Gouvernement", JORADP,
               covers=("legislation",),
               licence="unknown (no terms of use published on joradp.dz)",
               commercial_use=None,
               ai_use=None,   # robots.txt is 404 (no rules); no AI/TDM statement anywhere
               auth="none",
               rate_limit="unknown; 1.5 s spacing, no 429 seen in ~30 requests (2026-11)",
               terms_url=f"{JORADP}/HFR/Index.htm"),
        Source("Cour constitutionnelle (and former Conseil constitutionnel) of Algeria", CC,
               covers=("caselaw",),
               licence="unknown (no terms of use, legal notice or copyright line on "
                       "cour-constitutionnelle.dz)",
               commercial_use=None,
               ai_use=None,   # robots.txt (Yoast): 'User-agent: * / Disallow:' allows all; no AI/TDM statement
               auth="none",
               rate_limit="unknown; 1 s spacing, no 429 seen in ~15 requests (2026-11)",
               terms_url=f"{CC}/robots.txt"),
    )
    caselaw_filters = {
        "kind": "decision or avis (opinion)",
        "date_from": "decided on or after, YYYY-MM-DD",
        "date_to": "decided on or before, YYYY-MM-DD",
    }
    legislation_filters = {
        "nature": "type of text as JORADP names it: Loi, Loi organique, Ordonnance, Décret, "
                  "Décret présidentiel, Décret exécutif, Arrêté, Arrêté inter, Décision, "
                  "Instruction, Circulaire, ...",
        "number": "text number, e.g. 08-09",
        "date_from": "signed on or after, YYYY-MM-DD",
        "date_to": "signed on or before, YYYY-MM-DD",
        "match": "all (default) or any of the keywords",
    }
    min_interval = {"www.joradp.dz": 1.5, "cour-constitutionnelle.dz": 1.0}
    notes = ("Legislation: Journal Officiel index since 1962, texts as published (not consolidated) "
             "in the French edition (official translation; Arabic is authoritative), full text only "
             "for issues from 2002 (older ones are scans). Law id 'Constitution': the 2020 text "
             "with later revision laws applied. Keywords must be JORADP lexicon words. "
             "Case law: decisions and opinions (avis) of the Constitutional Court and the former "
             "Constitutional Council, 1989 onward (French edition; Arabic is authoritative). "
             "cour-constitutionnelle.dz sends an incomplete TLS chain: it works with the OS trust "
             "store on macOS/Windows and fails on Linux. No Supreme Court or Council of State "
             "case law (coursupreme.dz did not respond).")
    gaps = (
        ("Supreme Court case law: coursupreme.dz connect timeout on http and https, www and bare "
         "(2026-11-05/06 and again 2026-11-10)"),
        "Council of State and lower-court decisions: not researched yet",
        "Tribunal des conflits, administrative courts of appeal and military courts: not researched yet",
        "Journal Officiel texts before 2002: scans only, no text layer and no OCR here (reference "
        "returned only; Arabic issues are scans too, 1990 and 2000 checked). Of the primary acts in the JO index (checked 2026-11-10), 1,794 date from "
        "before 2002 (Loi 399, Loi organique 3, Ordonnance 1,354, Décret législatif 38) against 475 "
        "with text from 2002 on; base texts of codes still in force such as the Code civil "
        "(Ord. 75-58), Code pénal (Ord. 66-156) and Code de la famille (Loi 84-11) are scan-only, "
        "their post-2002 amending acts are readable",
        "Arabic (authoritative) JO issues: /FTP/jo-arabe/{year}/A{year}{jo:03}.pdf, HTTP 200; 1975, 1990, 2000 and 2001 have no text layer; "
        "where a text layer exists its font map is broken differently per era (2003: custom-encoded glyph garbage; "
        "2008: letters in order but words reversed and ligatures mapped to 'J', '~', 's'; 2024: each line character-reversed, "
        "digits scrambled), so the Arabic text is not served (checked 2026-11-10)",
        "Laws are as published, not consolidated (no official consolidation on joradp.dz; "
        "mjustice.dz, droit.mjustice.dz and apn.dz timed out from the UK, 2026-11-10)",
        "Arabic (authoritative) edition of laws and Constitutional Court decisions: source has it, not built (French only)",
        "Constitutional Court on Linux: its TLS chain is incomplete, works only with the OS trust store (macOS/Windows)",
    )
    samples = {
        "caselaw_query": "procédure civile",
        "decision_id": "Décision n° 01/D.C.C/EI/25 du 7 janvier 2025",
        "legislation_query": "procédure civile",
        "law_id": "Loi n° 08-09",
        "provision": "13",
    }

    # ---- case law ----
    async def search_caselaw(self, query, *, limit, page, filters):
        kind = _fold(filters.get("kind", ""))
        if kind not in ("", "decision", "avis"):
            raise BadRequest("kind must be 'decision' or 'avis'")
        lo, hi = filters.get("date_from", ""), filters.get("date_to", "")
        for v, n in ((lo, "date_from"), (hi, "date_to")):
            if v:
                _dmy(v, n)
        q = _http.clean(query)
        words = list(dict.fromkeys(w for w in (_fold(t) for t in re.findall(r"\w+", q)) if len(w) > 1))
        if not words:
            if re.search(r"[^\W\d_]", q) and not re.search(r"[A-Za-z]", q):
                raise BadRequest("Algerian case law here is searched in the French edition of "
                                 "the Constitutional Court's site; Arabic keywords return "
                                 "nothing. Search in French, e.g. 'procédure pénale'")
            raise BadRequest("give one or more keywords, e.g. 'procédure pénale'")
        # the site's search returns nothing for long queries: send a few terms, filter on all
        hits = [d for d in await _cc_search(" ".join(words[:4]))
                if (not kind or _fold(d["kind"]) == kind)
                and (not lo or d["date"] >= lo) and (not hi or d["date"] <= hi)
                and all(w in _fold(d["title"] + " " + d["text"]) for w in words)]
        start = (page - 1) * limit
        items = [DecisionHit(id=d["id"], title=d["title"][:300], court=d["court"], date=d["date"],
                             case_number=d["number"], snippet=_snippet(d["text"], words), url=d["url"])
                 for d in hits[start:start + limit]]
        return Results(items, total=len(hits),
                       note="All words must match (accents ignored); newest first. French "
                            "edition (the Arabic one is authoritative).")

    async def get_decision(self, id):
        s = _http.clean(id)
        m = _HEADING.match(s)
        date = _fr_date(m[3]) if m else ""
        number = (m[2] or "") if m else re.sub(r"^(décision|decision|avis)\s*(n\s*°)?\s*", "", s, flags=re.I)
        if date:
            terms = f'"{_MONTH_NAMES[int(date[5:7]) - 1]} {date[:4]}"'
        else:
            y = re.search(r"(\d{2}|\d{4})\W*$", number)
            if not y:
                raise BadRequest("decision id looks like 'Décision n° 01/D.C.C/EI/25 du 7 janvier "
                                 "2025' (as search_caselaw returns it) or '01/D.C.C/EI/25'")
            yy = y[1]
            terms = yy if len(yy) == 4 else ("19" if int(yy) > 50 else "20") + yy
        key = _loose(number)
        for d in await _cc_search(terms):
            if (not date or d["date"] == date) and (key == _loose(d["number"]) if key or date else False) \
                    and (not m or _fold(d["kind"]) == _fold(m[1])):
                return Decision(id=d["id"], title=d["title"], text=d["text"], url=d["url"],
                                court=d["court"], date=d["date"], case_number=d["number"],
                                metadata={"type": d["kind"],
                                          "edition": "French (the Arabic edition is authoritative)"})
        raise NotFound(f"no Constitutional Court decision or avis {id!r}; ids look like "
                       "'Décision n° 01/D.C.C/EI/25 du 7 janvier 2025' (see search_caselaw)")

    # ---- legislation ----
    async def search_legislation(self, query, *, limit, page, filters):
        fields: dict[str, str] = {"ztyp": "2" if _fold(filters.get("match", "")) == "any" else "1"}
        if filters.get("nature"):
            nat = _nature(filters["nature"])
            if not nat:
                raise BadRequest("nature must be one of: " + ", ".join(_NATURES))
            fields["znat"] = nat
        if filters.get("number"):
            fields["zntx"] = str(filters["number"]).strip()
        if filters.get("date_from"):
            fields["zntd"] = _dmy(filters["date_from"], "date_from")
        if filters.get("date_to"):
            fields["zntf"] = _dmy(filters["date_to"], "date_to")
        q = _http.clean(query)
        m = _SHORT.match(q)
        if m and _nature(m["nat"]) and "zntx" not in fields:
            fields["znat"], fields["zntx"] = _nature(m["nat"]), m["num"].replace(" ", "")
        elif re.fullmatch(r"\d{2,4}-\d{1,4}", q) and "zntx" not in fields:
            fields["zntx"] = q
        elif q:
            fields["zdes"] = q   # urlencoded spaces arrive as '+', the site's word separator
        if len(fields) == 1:
            raise BadRequest("give keywords, a text number (08-09) or a filter")
        # The source pages by 20; map (page, limit) onto it.
        first = (page - 1) * limit
        src_page = first // 20 + 1
        if src_page > 25:
            raise BadRequest("page too deep for this source; narrow the search with filters")
        html, total = await _search(fields, src_page)
        hits = _parse_hits(html)
        off = first - (src_page - 1) * 20
        items = hits[off:off + limit]
        if len(items) < limit and off + limit > 20 and total and first + len(items) < total:
            html, _ = await _search(fields, src_page + 1)
            items += _parse_hits(html)[:limit - len(items)]
        if page == 1 and "constitution" in _fold(q) and not set(filters) - {"match"}:
            items = [LawHit(id="Constitution", type="Constitution", date="2020-12-30",
                            title="Constitution de la République algérienne démocratique et populaire "
                                  "(révision du 1er novembre 2020, avec ses révisions ultérieures)",
                            status="en vigueur", url=_CONST_PDF,
                            snippet="Text from the SGG with later revision laws applied")] + items[:limit - 1]
        note = ""
        if "inexistant" in html and not items:
            note = ("Keyword(s) not in the JORADP lexicon. Use lexicon words (e.g. 'famille', "
                    "'investissement', 'procédure civile'), a number like 08-09, or filters.")
        return Results(items, total=total, note=note or
                       "Texts as published in the Journal Officiel (French edition), not consolidated.")

    async def get_legislation_toc(self, id):
        canon, title, pars, url = await _law(id)
        toc, _ = _articles(pars)
        return Toc(id=canon, title=title, url=url, entries=toc)

    async def get_legislation_provision(self, id, provision):
        canon, title, pars, url = await _law(id)
        _, arts = _articles(pars)
        p = _fold(provision)
        p = re.sub(r"^(article|art\.?|art)\s*", "", p).strip(" .")
        key = _label(p)
        if key not in arts:
            raise NotFound(f"no article {provision!r} in {title[:80]}; labels look like "
                           f"'1', '13', '7 bis' (see get_legislation_toc)")
        as_of = (await _constitution())["as_of"] if canon == "Constitution" else ""
        return Provision(law_id=canon, law_title=title, provision=key, text=arts[key], url=url,
                         as_of=as_of)

    async def get_legislation_text(self, id):
        canon, title, pars, url = await _law(id)
        meta = {"edition": "French (official translation; Arabic is authoritative)",
                "version": "as published in the Journal Officiel, not consolidated"}
        as_of = ""
        if canon == "Constitution":
            c = await _constitution()
            as_of = c["as_of"]
            meta["version"] = ("2020 text as published by the SGG" +
                               ("; Fontes applied the articles restated by: " + "; ".join(c["applied"])
                                if c["applied"] else ""))
        return LawText(id=canon, title=title, text="\n\n".join(pars), url=url, as_of=as_of,
                       metadata=meta)
