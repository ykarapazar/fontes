"""Bosnia and Herzegovina: Constitutional Court decisions (ustavnisud.ba) and Federation
of BiH laws as published (fbihvlada.gov.ba).

Case law: Ustavni sud Bosne i Hercegovine, https://www.ustavnisud.ba/bs/odluke.
  * The search page is a jQuery front end over JSON endpoints, used here as the page uses
    them (GET, no token, no login):
      - /{lang}/api/odluke?submit=1&tp=..&bp=..&a=..&oa=..&dos=..&doe=..&vp[]=..&vo[]=..&sp=..
        -> {"items": [...], "envelope": "<SOAP request it forwarded>"}. ALL hits come back
        in one response (no paging; "diskriminacija" = 1,238 items, 1.4 MB), so the list
        is kept in a small in-memory LRU and paged here. Without `sp` the order is oldest
        first, so sp=DatumDesc is always sent. tp = full text and case number (words AND,
        "quoted phrase", -word excludes); bp = exact case number "AP-4580/22" (with the
        hyphen); a = applicant; oa = challenged act; dos/doe = "DD.MM.YYYY."; vp[] case type
        (1 AP appeals, 2 U abstract review etc.); vo[] decision type (TYPES below).
        fp=1 = "decisions from the last session" (used for an empty query).
      - /{lang}/api/odlukaDetails?odlukaId=N -> one item (id "0" and empty lists when the
        id does not exist).
    Item keys: id (the Court's decision id), case_number, date ("YYYY-MM-DDT00:00:00"),
    title (applicant), decision_type, item_type (AP/U), disputed_act, conclusion (the
    operative part), keywords / infringement / not_infringement / publications ({title}
    lists), decision_url (the PDF, text layer present).
  * Languages: lang bs/hr/sr/en. Decisions are in one of the three official languages;
    English translations exist for a minority (mostly leading cases). In a non-bs search
    items without that version come back with id "-1"; they are dropped.
    Hit ids are the Court's numeric id for bs, "{lang}:{id}" otherwise ("en:12209").
  * Anonymisation: applicants who objected are shown by initials ("F.C.").

Legislation: Vlada Federacije BiH, "Hronološki registar zakona objavljenih u Službenim
novinama FBiH" (one page per year 1996-, https://fbihvlada.gov.ba/bs/zakoni lists them).
  * Each registry lists the year's gazette issues and links each law to its text as an
    HTML page: /bs/<slug> (about 2019 on, CMS page; text in div.content-section) or
    /bosanski/zakoni/YYYY/zakoni/N.htm(l) (older static pages, windows-1250 or utf-8).
    Before ~2019 each law has a Bosnian and a Croatian page; the language label is taken
    from the registry as written (a few labels are swapped at the source).
  * Text is the law AS PUBLISHED in the gazette: amendments are separate laws. No
    consolidated text. Search matches registry titles only (diacritics optional); it reads
    the year registries newest first until it has enough hits (`year` reads one).
  * The id is the page path on fbihvlada.gov.ba ("bs/1-zakon-o-advokaturi-..." or
    "bosanski/zakoni/2016/zakoni/5.html").

State-level legislation (Parlamentarna skupština BiH, www.parlament.ba), added 2026-11-10:
  * Constitution of BiH ("ustav-bih"): the Parliament's PDF /data/dokumenti/pdf/vazniji-propisi/
    Ustav BiH - B.pdf (Bosnian translation of Annex 4) plus Amandman I (2009, the only
    amendment). That PDF uses a legacy font: } ~ ` | stand for c-acute, c-caron, z-caron,
    d-stroke (and ^ ] @ \\ [ for the capitals); they are mapped back here. A few words are
    glued in the source ("sena" for "se na"). The Constitutional Court's own copy
    (ustavnisud.ba/bs/ustav-bosne-i-hercegovine, PDF) has a broken text layer (syllables
    split by spaces), so it is not used; only its preamble is plain HTML.
  * Consolidated acts ("pa/<lawId>"): the Parliament's "Prečišćeni tekstovi zakona"
    (/law/Read?categoryId=3, 14 pages of 10, 135 entries, each a dated unofficial consolidation;
    several entries are successive versions of one law). Each /law/LawDetails?lawId=N page links the
    text-layer PDF (/law/DownloadDocument?lawDocumentId=..&langTag=bs). Search shows the newest
    version of each act and skips the Parliament's own rules of procedure (Poslovnik) and the
    drafting rules (Jedinstvena pravila), which are not acts. The list is a SELECTION: BiH has
    more state acts than the Parliament consolidates. robots.txt disallows only /olaw/OLawDetails*,
    /oact/OActDetails*, /session/... etc.; /law/* is not listed.

Verified 2026-11-06 (UK IP, project User-Agent):
  * www.ustavnisud.ba/robots.txt: "User-agent: * / Disallow:" (everything allowed), no
    AI/Content-Signal lines; pages carry <meta name="robots" content="index, follow">.
    No terms-of-use page; footer "Copyrights @ 2026 Ustavni sud BiH Sva prava zadržana."
    Behind Cloudflare, but no challenge was served to this client.
  * fbihvlada.gov.ba and www.fbihvlada.gov.ba robots.txt: "User-agent: * / Disallow:".
    No terms-of-use page (only "Pravila privatnosti", about personal data); footer
    "Copyright 2021. Vlada Federacije Bosne i Hercegovine".
  * Not used:
      - csd.pravosudje.ba / pravosudje.ba (ordinary courts' case law): registration and paid.
      - sluzbenilist.ba (Službeni glasnik BiH, state gazette) and slglasnik.org (RS gazette):
        paid subscriptions.
      - parlament.ba /olaw/OLawDetails* (law pages of the legislative database, adopted-as-
        published acts): robots.txt disallows them. The consolidated-text list above is used.
      - skupstinabd.ba (Brčko District laws, PDFs of each act + amendments, not
        consolidated): free, robots allow; left for later (one small district).
      - sg.skupstinabd.ba (Brčko gazette): login ("autorizacija").
      - paragraf.ba: commercial.
"""
from __future__ import annotations

import html as _html
import re
import unicodedata
from urllib.parse import urljoin, urlsplit

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

US_HOST = "www.ustavnisud.ba"
US = f"https://{US_HOST}"
COURT = "Ustavni sud Bosne i Hercegovine"
LANGS = ("bs", "hr", "sr", "en")
CASE_TYPES = {"AP": "1", "U": "2"}
TYPES = {  # decision-type filter -> the Court's vrsteOdluka id
    "admissibility": "1",   # Odluka o dopustivosti
    "merits": "2",          # Odluka o meritumu
    "interim": "3",         # Odluka o privremenoj mjeri
    "other": "4",           # Rješenje, zaključak, obavještenje i ostali akti
    "non-enforcement": "5",  # Rješenje o neizvršenju
    "discontinuance": "6",  # Odluka o obustavi postupka
}
_CASE_RE = re.compile(r"(AP|U)\s*-\s*(\d+)\s*/\s*(\d{2,4})", re.I)
_lists: dict = {}       # search params -> items (the API returns every hit at once)

FB_HOST = "fbihvlada.gov.ba"
FB = f"https://{FB_HOST}"
FB_ID = re.compile(r"(?:bs|hr|sr|en)/[a-z0-9][a-z0-9-]*|bosanski/zakoni/\d{4}/zakoni/[\w.-]+\.html?")
PA_HOST = "www.parlament.ba"
PA = f"https://{PA_HOST}"
PA_ID = re.compile(r"pa/\d+")
CONST_ID = "ustav-bih"
CONST_TITLE = "Ustav Bosne i Hercegovine (Aneks 4 Općeg okvirnog sporazuma za mir)"
CONST_PDF = f"{PA}/data/dokumenti/pdf/vazniji-propisi/Ustav%20BiH%20-%20B.pdf"
AMEND_PDF = f"{PA}/data/dokumenti/pdf/Amandman%20I%20na%20Ustav%20BiH-2009.-B%20.pdf"
_FONT = str.maketrans({"}": "ć", "~": "č", "`": "ž", "|": "đ", "{": "š",
                       "^": "Č", "]": "Ć", "@": "Ž", "[": "Š", "\\": "Đ"})
_registries: dict = {}  # "years" -> {year: url}; year -> parsed entries
_laws: dict = {}        # law id -> (title, paragraphs)
_ART = re.compile(r"^[*_\s]*Čl(?:an|anak)\s+(\d+)\s*\.?\s*([a-z])?\s*\.?[*_]*\s*(?:\n|$|\()", re.I)


def _s(v) -> str:
    return _http.clean(v) if isinstance(v, (str, int)) else ""


def _fold(s: str) -> str:
    s = str(s).lower().replace("đ", "dj")
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


# --------------------------------------------------------------------------- #
# Constitutional Court
# --------------------------------------------------------------------------- #
def _split_id(ident: str) -> tuple[str, str]:
    ident = _http.clean(ident)
    m = re.fullmatch(r"(?:(bs|hr|sr|en)\s*:\s*)?(\d+)", ident, re.I)
    if not m:
        return "", ident
    return (m[1] or "bs").lower(), m[2]


def _titles(lst) -> list[str]:
    return [_s(x.get("title")) for x in lst or [] if isinstance(x, dict) and _s(x.get("title"))]


def _case_title(item: dict) -> str:
    cn, who = _s(item.get("case_number")), _s(item.get("title"))
    return f"{COURT}, {cn}" + (f" ({who})" if who else "")


def _hit(item: dict, lang: str) -> DecisionHit:
    ident = item["id"] if lang == "bs" else f"{lang}:{item['id']}"
    bits = [_s(item.get("decision_type")), _s(item.get("disputed_act")) and
            f"Osporeni akt: {_s(item.get('disputed_act'))}"]
    kw = _titles(item.get("keywords"))
    if kw:
        bits.append("Ključne riječi: " + "; ".join(kw))
    return DecisionHit(id=ident, title=_case_title(item), court=COURT,
                       date=_http.iso_date(_s(item.get("date"))[:10]),
                       case_number=_s(item.get("case_number")),
                       snippet="; ".join(b for b in bits if b)[:300],
                       url=urljoin(US, _s(item.get("decision_url"))) if _s(item.get("decision_url")) else
                       f"{US}/{lang}/odluke")


def _dmy(v: str, name: str) -> str:
    v = _http.clean(v)
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", v)
    if not m:
        raise BadRequest(f"{name} must be YYYY-MM-DD, got {v!r}.")
    return f"{m[3]}.{m[2]}.{m[1]}."


async def _us_json(url: str, params) -> dict:
    r = await _http.get(url, params=params)
    if r.status_code != 200:
        raise SourceError(_http.error("ustavnisud.ba", "decision search failed", r.status_code), r.status_code)
    try:
        d = r.json()
    except ValueError:
        raise SourceError(_http.error("ustavnisud.ba", "not JSON (block page?)", r.status_code, r.text[:150]))
    if not isinstance(d, dict):
        raise SourceError(f"ustavnisud.ba: unexpected payload {str(d)[:200]}")
    return d


# --------------------------------------------------------------------------- #
# Federation of BiH laws
# --------------------------------------------------------------------------- #
def _decode(r) -> str:
    raw = r.content
    m = re.search(rb"charset=[\"']?([\w-]+)", raw[:2000], re.I)
    enc = (m[1].decode() if m else r.encoding or "utf-8").lower()
    try:
        return raw.decode(enc)
    except (LookupError, UnicodeDecodeError):
        return raw.decode("cp1250", "replace")


def _fb_get_text(r, what: str) -> str:
    if r.status_code == 404:
        raise NotFound(f"fbihvlada.gov.ba has no page {what}.")
    if r.status_code != 200:
        raise SourceError(_http.error("fbihvlada.gov.ba", f"{what} failed", r.status_code), r.status_code)
    return _decode(r)


def _content(page: str) -> str:
    """The article body of a CMS page, or the whole body of an old static page."""
    i = page.find('class="content-section"')
    if i < 0:
        return page
    j = page.find('<div class="col-md-4">', i)
    return page[page.find(">", i) + 1: j if j > 0 else None]


def _registry_entries(page: str, base_url: str, year: int) -> list[dict]:
    body = _content(page)
    body = re.sub(r'(?is)<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
                  lambda m: f"\x01{m[1]}\x02{m[2]}\x03", body)
    body = re.sub(r"(?s)<[^>]+>", " ", body)
    body = _html.unescape(body).replace("\xa0", " ")
    gaz = re.compile(r"broj\s*(\d+\s*/\s*\d{2,4})\s*/?\s*[(/]?\s*(\d{1,2})\.\s*(\d{1,2})\.")
    out, number, date = [], "", ""
    for m in re.finditer(r"\x01([^\x02]*)\x02([^\x03]*)\x03|" + gaz.pattern, body):
        if m[1] is None:
            number = re.sub(r"\s", "", m[3])
            try:
                date = f"{year:04d}-{int(m[5]):02d}-{int(m[4]):02d}"
            except ValueError:
                date = ""
            continue
        url = urljoin(base_url, _html.unescape(m[1]).strip())
        parts = urlsplit(url)
        path = parts.path.lstrip("/")
        if not parts.netloc.endswith(FB_HOST) or not FB_ID.fullmatch(path) or "registar" in path:
            continue
        title = _http.clean(m[2])
        lang = ""
        lm = re.search(r"\((bosanski|hrvatski|srpski)\s+jezik\)\s*$", title, re.I)
        if lm:
            lang = {"bosanski": "bs", "hrvatski": "hr", "srpski": "sr"}[lm[1].lower()]
            title = title[:lm.start()].strip()
        title = re.sub(r"^\d+\.\s*", "", title)
        if title[:5].upper() == "ZAKON":
            title = "Zakon" + title[5:]
        if title:
            out.append({"id": path, "title": title, "lang": lang, "number": number, "date": date})
    return out


def _paragraphs(page: str) -> list[str]:
    return _http.html_paragraphs(_content(page))


def _is_heading(p: str) -> bool:
    """A short article title line such as 'Predmet zakona' or '(Sadržaj zakona)'."""
    t = re.sub(r"[*_]", "", p).strip()
    return (0 < len(t) <= 90 and not _ART.match(p) and t[-1] not in ".:;," and "\n" not in t
            and t != t.upper())   # upper-case lines are chapter headings / the law's title


def _articles(paras: list[str]) -> list[tuple[str, int, str]]:
    """(label, first paragraph index, heading) per article; a title line just before
    'Član N.' belongs to that article. Duplicate labels are numbered 'Član 5 (2)'."""
    seen: dict[str, int] = {}
    out = []
    for i, p in enumerate(paras):
        m = _ART.match(p) if len(p) < 200 else None
        inline = ""
        if not m and len(p) < 200 and p.count("\n") == 1:   # "Title  \nČlan 54." in one paragraph
            first, second = (x.strip() for x in p.split("\n"))
            m = _ART.match(second) if _is_heading(first) else None
            if m:
                inline, p = _http.clean(re.sub(r"[*_]", "", first)), second
        if not m:
            continue
        word = "Članak" if p.lstrip("*_ ").lower().startswith("članak") else "Član"
        label = f"{word} {m[1]}{m[2] or ''}"
        seen[label] = seen.get(label, 0) + 1
        if seen[label] > 1:
            label = f"{label} ({seen[label]})"
        start = i - 1 if i > 0 and _is_heading(paras[i - 1]) and (not out or out[-1][1] < i - 1) else i
        heading = _http.clean(re.sub(r"[*_]", "", p))
        if start < i or inline:
            heading += " – " + (inline or _http.clean(re.sub(r"[*_]", "", paras[start])))
        out.append((label, start, heading))
    return out


def _norm_prov(s: str) -> str:
    """'5', 'čl. 5', 'Član 5.', 'Članak 5', 'art 5', '5a' -> '5a' (plus ' (2)' if given)."""
    s = _http.clean(s)
    m = re.fullmatch(r"(?:čl(?:an|anak)?|cl(?:an|anak)?|art(?:icle)?|član|clan)?\.?\s*(\d+)\s*\.?\s*([a-z])?\s*\.?"
                     r"\s*(\(\d+\))?", s, re.I)
    if not m:
        raise BadRequest(f"Provision must look like 'Član 5' or '5', got {s!r}.")
    return f"{m[1]}{(m[2] or '').lower()}" + (f" {m[3]}" if m[3] else "")


# --------------------------------------------------------------------------- #
# State level: Constitution and the Parliament's consolidated acts (parlament.ba)
# --------------------------------------------------------------------------- #
_NEW_PARA = re.compile(r"^(?:Čl(?:an|anak)\s+\d|(?:Član|Aneks)\s+[IVX]+$|\(\d+\)|\d+[.)]\s|[a-zčćšđž]\)\s|[IVXL]+\.\s|\*{3})")
_STANDALONE = re.compile(r"(?:Član|Aneks) [IVX]+")   # a Roman-numbered heading line stands alone
_ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII", 9: "IX", 10: "X",
          11: "XI", 12: "XII"}
_PA_VERSION = re.compile(r"\s*[-–]\s*(?:Neslužbeni|Tehnički)\s+prečišćeni\s+tekst.*$", re.I | re.S)


def _lines_to_paras(text: str) -> list[str]:
    """Reflow PDF lines into paragraphs: a line opens a new one when it looks like an article,
    a numbered item or follows a line that ended a sentence."""
    paras: list[str] = []
    for ln in text.split("\n"):
        ln = _http.clean(ln)
        if not ln:
            continue
        if paras and not _NEW_PARA.match(ln) and not _STANDALONE.fullmatch(paras[-1]) and not (
                paras[-1][-1] in ".;:!?”\"" and (ln[0].isupper() or ln[0].isdigit() or ln[0] in "(„\"")):
            paras[-1] += " " + ln
        else:
            paras.append(ln)
    return paras


def _const_paras(const_pdf: bytes, amend_pdf: bytes) -> list[str]:
    t = _http.pdf_text(const_pdf).translate(_FONT)
    t = re.sub(r"(?m)^\d{1,2}$", "", t)                          # page numbers
    t = re.sub(r"^USTA V\s*BOSNE I HERCEGOVINE\s*USTA V\s*BOSNE I HERCEGOVINE\s*", "", t)
    paras = _lines_to_paras(t)
    paras.append("Amandman I")
    paras += _lines_to_paras(_http.pdf_text(amend_pdf))
    return paras


def _const_articles(paras: list[str]) -> list[tuple[str, int, str]]:
    out = [("Preambula", 0, "Preambula")]
    for i, p in enumerate(paras):
        if re.fullmatch(r"(?:Član|Aneks) [IVX]+", p) or p == "Amandman I":
            out.append((p, i, p))
    return out


def _norm_const(s: str) -> str:
    """'VI', 'čl. VI', 'Član 6', 'Aneks 1', 'amandman I', 'preambula' -> the TOC label."""
    s = _http.clean(s)
    s = re.sub(r"(?<=[IVX])\s*[/(][\w/().\s]*$", "", s)   # 'II/3', 'II(3)(e)' -> the whole article
    m = re.fullmatch(r"(?:(čl(?:an|anak)?|cl(?:an|anak)?|član|art(?:icle)?|aneks|annex|amandman|amendment)\.?\s*)?"
                     r"([IVX]+|\d{1,2})\s*\.?", s, re.I)
    if re.fullmatch(r"preambula|preamble", s, re.I):
        return "Preambula"
    if not m:
        raise BadRequest(f"Provision must look like 'Član VI', 'Aneks I', 'Amandman I' or 'Preambula', got {s!r}.")
    kind = (m[1] or "član").lower()
    num = m[2].upper()
    if num.isdigit():
        num = _ROMAN.get(int(num), num)
    word = "Aneks" if kind in ("aneks", "annex") else "Amandman" if kind in ("amandman", "amendment") else "Član"
    return f"{word} {num}"


def _law_url(ident: str) -> str:
    if ident == CONST_ID:
        return CONST_PDF
    if PA_ID.fullmatch(ident):
        return f"{PA}/law/LawDetails?lawId={ident[3:]}"
    return f"{FB}/{ident}"


def _pa_entries(page: str) -> list[dict]:
    out = []
    for m in re.finditer(r'LawDetails\?lawId=(\d+)"[^>]*>\s*<p class="title">([^<]*)</p>\s*<p class="date">([^<]*)</p>', page):
        title = _http.clean(_html.unescape(m[2]))
        base = _PA_VERSION.sub("", title)
        out.append({"id": f"pa/{m[1]}", "title": title, "base": base, "date": _http.iso_date(_http.clean(m[3]))})
    return out


# --------------------------------------------------------------------------- #

def _and_words(q: str) -> str:
    """ustavnisud.ba answers HTTP 500 to plain space-separated words; it needs an explicit AND."""
    toks = re.findall(r'"[^"]*"|\S+', q)
    if len(toks) < 2 or any(t.upper() in ("AND", "OR", "NOT") for t in toks):
        return q
    return " AND ".join(toks)

class BosniaHerzegovina(Jurisdiction):
    code = "ba"
    name = "Bosnia and Herzegovina"
    languages = ("bs", "hr", "sr", "en")
    aliases = ("bosnia", "bosnia and herzegovina", "bih", "bosna i hercegovina", "bih-fbih",
               "ustavni sud bih", "constitutional court of bosnia and herzegovina")
    sources = (
        Source(
            name="Ustavni sud Bosne i Hercegovine (ustavnisud.ba) – decisions database",
            url=f"{US}/bs/odluke",
            covers=("caselaw",),
            licence=("unknown: no terms of use on the site (footer 'Copyrights @ 2026 Ustavni sud "
                     "BiH Sva prava zadržana.'); official court decisions"),
            commercial_use=None,
            ai_use=None,   # robots.txt allows all, no AI/TDM clause
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~25 requests (2026-11)",
            terms_url="",
        ),
        Source(
            name="Vlada Federacije BiH (fbihvlada.gov.ba) – Hronološki registar zakona (Federation laws as published)",
            url=f"{FB}/bs/zakoni",
            covers=("legislation",),
            licence=("unknown: no terms of use on the site (footer 'Copyright 2021. Vlada Federacije "
                     "Bosne i Hercegovine'); official legislative texts"),
            commercial_use=None,
            ai_use=None,   # robots.txt allows all, no AI/TDM clause
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~20 requests (2026-11)",
            terms_url="",
            warning=("Federation of BiH entity laws only, as published in Službene novine FBiH "
                     "(not consolidated; state, Republika Srpska and Brčko laws are not covered)."),
        ),
        Source(
            name="Parlamentarna skupština BiH (parlament.ba) – Ustav BiH and Prečišćeni tekstovi zakona (state level)",
            url=f"{PA}/law/Read?categoryId=3",
            covers=("legislation",),
            licence=("unknown: no terms of use found on the site; official Parliament publication. The "
                     "consolidated texts are the Parliament's UNOFFICIAL consolidations (Neslužbeni "
                     "prečišćeni tekst); only the Službeni glasnik BiH text is authentic"),
            commercial_use=None,
            ai_use=None,   # robots.txt: only /olaw/OLawDetails*, /oact/..., /session/... etc. disallowed; no AI/TDM clause
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~25 requests (2026-11)",
            terms_url="",
            warning=("State-level acts: the Constitution (with Amandman I) and the Parliament's unofficial "
                     "consolidated texts, a selection of state acts (not every act); the authentic text is "
                     "in Službeni glasnik BiH."),
        ),
    )
    caselaw_filters = {
        "case_number": "exact case number, e.g. 'AP-4580/22' or 'U-5/98'",
        "applicant": "applicant / requesting party name (podnositelj), e.g. 'Sejdić'",
        "challenged_act": "words from the challenged act (osporeni akt), e.g. 'Kantonalnog suda u Mostaru'",
        "case_type": "AP (individual appeals) or U (abstract review, vital national interest, referrals)",
        "decision_type": "one of " + ", ".join(TYPES),
        "date_from": "YYYY-MM-DD, decision date from",
        "date_to": "YYYY-MM-DD, decision date to",
        "language": "bs (default), hr, sr or en (English translations, leading cases only)",
        "sort": "newest (default), oldest",
    }
    legislation_filters = {
        "year": "YYYY (1996-), the year of publication in Službene novine FBiH; reads only that year",
        "language": "bs (default), hr, sr or all (before ~2019 each law has a Bosnian and a Croatian page)",
        "level": "state (Constitution + Parliament's consolidated state acts), fbih (Federation laws) or all "
                 "(default: state first, then Federation; the year filter implies fbih)",
    }
    min_interval = {US_HOST: 1.0, FB_HOST: 1.0, f"www.{FB_HOST}": 1.0, PA_HOST: 1.0}
    notes = ("Case law: Constitutional Court of BiH decisions (1997-, full text; English for leading "
             "cases). Legislation: the Constitution of BiH (with Amandman I), the Parliament's unofficial "
             "consolidated state acts (a selection) and Federation of BiH laws as published (1996-). "
             "Ordinary courts' case law and the state/RS gazettes are paid. "
             "Provisions of the Constitution are returned as whole articles ('II/3' gives Član II).")
    gaps = (
        "Ordinary courts' case law (csd.pravosudje.ba): needs registration and is paid",
        ("State-level acts: only the Parliament's selection of unofficial consolidated texts (135 "
         "entries, 81 distinct acts) is reached; the full set of acts as adopted sits behind /olaw/OLawDetails* "
         "(robots disallow) and Službeni glasnik BiH (paid)"),
        "Republika Srpska laws: Službeni glasnik RS (slglasnik.org) is paid",
        ("Brčko District laws (skupstinabd.ba): free, robots allow; source exists but not built "
         "yet"),
        ("Consolidated texts: no free official source found (FBiH laws as published only; "
         "paragraf.ba is commercial)"),
    )
    samples = {
        "caselaw_query": "diskriminacija",
        "decision_id": "12209",                  # U-5/98 III, 1 July 2000 ("constituent peoples")
        "legislation_query": "Zakon o radu",
        "law_id": "bosanski/zakoni/2016/zakoni/5.html",   # Zakon o radu (Sl. novine FBiH 26/16)
        "provision": "Član 1",
    }

    # ------------------------------------------------------------------ case law
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        f = {k: _http.clean(v) for k, v in (filters or {}).items() if _http.clean(v)}
        lang = f.get("language", "bs").lower()
        if lang not in LANGS:
            raise BadRequest(f"language must be one of {', '.join(LANGS)}, got {f['language']!r}.")
        sort = {"newest": "DatumDesc", "oldest": "DatumAsc"}.get(f.get("sort", "newest").lower())
        if not sort:
            raise BadRequest(f"sort must be newest or oldest, got {f['sort']!r}.")
        params: list[tuple[str, str]] = [("submit", "1"), ("sp", sort)]
        q = _http.clean(query)
        cm = _CASE_RE.fullmatch(q) if q else None
        cn = f.get("case_number") or (q if cm else "")
        if cn:
            m = _CASE_RE.fullmatch(cn)
            if not m:
                raise BadRequest(f"case_number must look like 'AP-4580/22' or 'U-5/98', got {cn!r}.")
            params.append(("bp", f"{m[1].upper()}-{m[2]}/{m[3]}"))
        if q and not cm:
            params.append(("tp", _and_words(q)))
        for key, name in (("applicant", "a"), ("challenged_act", "oa")):
            if key in f:
                params.append((name, f[key]))
        if "date_from" in f:
            params.append(("dos", _dmy(f["date_from"], "date_from")))
        if "date_to" in f:
            params.append(("doe", _dmy(f["date_to"], "date_to")))
        if "case_type" in f:
            ct = f["case_type"].upper()
            if ct not in CASE_TYPES:
                raise BadRequest(f"case_type must be AP or U, got {f['case_type']!r}.")
            params.append(("vp[]", CASE_TYPES[ct]))
        if "decision_type" in f:
            dt = f["decision_type"].lower()
            if dt not in TYPES:
                raise BadRequest(f"decision_type must be one of {', '.join(TYPES)}, got {f['decision_type']!r}.")
            params.append(("vo[]", TYPES[dt]))
        latest = len(params) == 2
        if latest:
            params.append(("fp", "1"))   # no criteria: decisions from the last session

        key = (lang, tuple(params))
        items = _lists.get(key)
        if items is None:
            try:
                d = await _us_json(f"{US}/{lang}/api/odluke", params)
            except SourceError as e:
                if e.status != 500:
                    raise
                raise SourceError(
                    "This database holds only Constitutional Court of BiH decisions: Supreme, appeal and "
                    "other ordinary court judgments are not available through Fontes. Separately, "
                    "ustavnisud.ba's decision search returned HTTP 500 for this query (it fails on a single "
                    "very broad or common word such as 'sud' or 'pravo', or on a lone quoted phrase; add a "
                    "second, more specific word, a case number or a filter).", 500)
            if not isinstance(d.get("items"), list):
                raise SourceError(f"ustavnisud.ba search: unexpected payload {str(d)[:200]}")
            items = [i for i in d["items"] if isinstance(i, dict) and str(i.get("id", "")).isdigit()
                     and i["id"] != "0"]
            _http.lru_put(_lists, key, items, 8)
        limit = max(1, min(int(limit), 50))
        start = (max(1, int(page)) - 1) * limit
        note = ("Constitutional Court of BiH decisions only (no Supreme, appeal or other ordinary court "
                "judgments; their quotations appear inside constitutional appeals). "
                "Full text search; words AND, \"exact phrase\", -word excludes. ")
        if latest:
            note = "No query given: decisions from the Court's last session. "
        if lang != "bs":
            note += f"Only decisions with a {lang} version are listed. "
        return Results(items=[_hit(i, lang) for i in items[start:start + limit]], total=len(items),
                       note=note.strip())

    async def get_decision(self, id):
        ident = _http.clean(id)
        m = _CASE_RE.fullmatch(ident)
        if m:
            r = await self.search_caselaw("", limit=50, page=1, filters={"case_number": ident})
            ids = [h.id for h in r.items]
            if not ids:
                raise NotFound(f"No Constitutional Court decision in case {ident!r}.")
            if len(ids) > 1:
                raise BadRequest(f"Case {ident} has {len(ids)} decisions: "
                                 + ", ".join(f"{h.id} ({h.date}, {h.snippet.split(';')[0]})" for h in r.items)
                                 + ". Pass one of these ids.")
            ident = ids[0]
        lang, num = _split_id(ident)
        if not lang:
            raise BadRequest("Give the Court's numeric decision id from search_caselaw (e.g. '12209', "
                             "or 'en:12209' for the English version) or a case number like 'AP-4580/22'.")
        item = await _us_json(f"{US}/{lang}/api/odlukaDetails", {"odlukaId": num})
        if _s(item.get("id")) in ("", "0", "-1") or not _s(item.get("decision_url")):
            raise NotFound(f"The Constitutional Court has no decision with id {num}"
                           + (f" in language {lang}." if lang != "bs" else "."))
        pdf_url = urljoin(US, _s(item.get("decision_url")))
        r = await _http.get(pdf_url)
        if r.status_code == 404:
            raise NotFound(f"Decision {ident}: the PDF is not on the server ({pdf_url}).")
        if r.status_code != 200 or not r.content.startswith(b"%PDF"):
            raise SourceError(_http.error("ustavnisud.ba", "decision PDF failed", r.status_code), r.status_code)
        text = _http.pdf_text(r.content)
        if not text:
            text = "(The PDF has no text layer; open the link.)"
        meta = {}
        for k, v in (("Vrsta odluke", _s(item.get("decision_type"))),
                     ("Vrsta predmeta", _s(item.get("item_type"))),
                     ("Podnositelj", _s(item.get("title"))),
                     ("Osporeni akt", _s(item.get("disputed_act"))),
                     ("Ključne riječi", "; ".join(_titles(item.get("keywords")))),
                     ("Povreda", "; ".join(_titles(item.get("infringement")))),
                     ("Nema povrede", "; ".join(_titles(item.get("not_infringement")))),
                     ("Objavljeno", "; ".join(_titles(item.get("publications"))))):
            if v:
                meta[k] = v
        return Decision(id=ident, title=_case_title(item), text=text, url=pdf_url, court=COURT,
                        date=_http.iso_date(_s(item.get("date"))[:10]),
                        case_number=_s(item.get("case_number")),
                        summary=_s(item.get("conclusion")), metadata=meta)

    # ------------------------------------------------------------------ legislation
    async def _years(self) -> dict[int, str]:
        years = _registries.get("years")
        if years:
            return years
        years = {}
        for p in range(1, 9):
            r = await _http.get(f"{FB}/bs/zakoni", params={"page": str(p)} if p > 1 else None)
            page = _fb_get_text(r, "law registry index")
            found = 0
            for href in re.findall(r'href="([^"]*registar-zakona[^"]*-(\d{4})-godini)"', page):
                years.setdefault(int(href[1]), urljoin(FB, href[0]))
                found += 1
            if not found or f"page={p + 1}" not in page:
                break
        if not years:
            raise SourceError("fbihvlada.gov.ba: no year registries found on /bs/zakoni (layout changed?)")
        _registries["years"] = years
        return years

    async def _registry(self, year: int, url: str) -> list[dict]:
        if year in _registries:
            return _registries[year]
        r = await _http.get(url)
        entries = _registry_entries(_fb_get_text(r, f"registry {year}"), str(r.url), year)
        _http.lru_put(_registries, year, entries, 40)
        return entries

    async def _state(self) -> list[dict]:
        """Constitution + the newest consolidated version of each state act (parlament.ba)."""
        if "pa" in _registries:
            return _registries["pa"]
        entries = []
        for p in range(1, 30):
            r = await _http.get(f"{PA}/law/Read", params={"page": str(p), "categoryId": "3"})
            if r.status_code != 200:
                raise SourceError(_http.error("parlament.ba", "consolidated-law list failed", r.status_code), r.status_code)
            found = _pa_entries(r.text)
            entries += found
            if len(found) < 10:
                break
        if not entries:
            raise SourceError("parlament.ba: no consolidated laws found on /law/Read?categoryId=3 (layout changed?)")
        seen, out = set(), [{"id": CONST_ID, "title": CONST_TITLE, "match": CONST_TITLE + " constitution amandman",
                             "date": "2009-03-26", "type": "Ustav", "status": "in force (with Amandman I)"}]
        for e in entries:   # the list is newest first
            if e["base"] in seen or re.match(r"(Poslovnik|Jedinstvena pravila)", e["base"]):
                continue
            seen.add(e["base"])
            out.append({"id": e["id"], "title": e["title"], "match": e["base"], "date": e["date"],
                        "type": "Zakon", "status": "unofficial consolidated text"})
        _registries["pa"] = out
        return out

    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        f = {k: _http.clean(v) for k, v in (filters or {}).items() if _http.clean(v)}
        lang = f.get("language", "bs").lower()
        if lang not in ("bs", "hr", "sr", "all"):
            raise BadRequest(f"language must be bs, hr, sr or all, got {f['language']!r}.")
        level = f.get("level", "fbih" if "year" in f else "all").lower()
        if level not in ("state", "fbih", "all"):
            raise BadRequest(f"level must be state, fbih or all, got {f['level']!r}.")
        words = _fold(query).split()
        limit = max(1, min(int(limit), 50))
        need = max(1, int(page)) * limit
        hits: list[LawHit] = []
        if level in ("state", "all"):
            for e in await self._state():
                t = _fold(e["match"])
                if all(re.search(r"\b" + re.escape(w), t) for w in words):
                    hits.append(LawHit(id=e["id"], title=e["title"], type=e["type"], date=e["date"],
                                       status=e["status"], url=_law_url(e["id"])))
        if level == "state":
            start = need - limit
            return Results(items=hits[start:start + limit], total=len(hits),
                           note="State level: the Constitution and the Parliament's unofficial consolidated "
                                "acts (a selection, newest version of each); titles searched.")
        years = await self._years()
        if "year" in f:
            if not re.fullmatch(r"\d{4}", f["year"]) or int(f["year"]) not in years:
                raise BadRequest(f"year must be one of {min(years)}-{max(years)}, got {f['year']!r}.")
            order = [int(f["year"])]
        else:
            order = sorted(years, reverse=True)
        scanned = 0
        for y in order:
            entries = await self._registry(y, years[y])
            scanned += 1
            for e in reversed(entries):   # newest issue first
                if lang != "all" and e["lang"] and e["lang"] != lang:
                    continue
                if lang not in ("all", "bs") and not e["lang"]:
                    continue
                t = _fold(e["title"])
                if all(re.search(r"\b" + re.escape(w), t) for w in words):
                    hits.append(LawHit(id=e["id"], title=e["title"], type="Zakon",
                                       number=f"Službene novine FBiH {e['number']}" if e["number"] else "",
                                       date=e["date"], url=f"{FB}/{e['id']}"))
            if len(hits) >= need:
                break
        complete = scanned == len(order)
        start = need - limit
        note = ("Federation of BiH laws as published (amendments are separate laws)" if level == "fbih" else
                "State acts first (Constitution + Parliament's unofficial consolidated texts), then Federation "
                "of BiH laws as published (amendments are separate laws)") + "; titles searched"
        if not complete:
            note += f"; Federation laws newest first, read back to {order[scanned - 1]} (use the year filter for older laws)"
        return Results(items=hits[start:start + limit], total=len(hits) if complete else None,
                       note=note + ".")

    async def _law(self, id: str) -> tuple[str, str, list[str]]:
        ident = _http.clean(id).strip("/")
        if ident.startswith("http"):
            ident = urlsplit(ident).path.strip("/")
        if _fold(ident) in (CONST_ID, "ustav", "constitution", "ustav bosne i hercegovine",
                            "ustav bih", _fold(CONST_TITLE)):
            ident = CONST_ID
        if ident != CONST_ID and not PA_ID.fullmatch(ident) and not FB_ID.fullmatch(ident):
            raise BadRequest("Give the law's id from search_legislation: 'ustav-bih' (Constitution), 'pa/1235' "
                             "(state act), or a Federation page path such as "
                             "'bosanski/zakoni/2016/zakoni/5.html' or 'bs/1-zakon-o-advokaturi-federacije-bosne-i-hercegovine'.")
        if ident in _laws:
            return _laws[ident]
        if ident == CONST_ID:
            rs = [await _http.get(u) for u in (CONST_PDF, AMEND_PDF)]
            for r in rs:
                if r.status_code != 200:
                    raise SourceError(_http.error("parlament.ba", "Constitution PDF failed", r.status_code), r.status_code)
            paras = _const_paras(rs[0].content, rs[1].content)
            if len("".join(paras)) < 20000 or not any(p == "Član XII" for p in paras):
                raise SourceError("parlament.ba: Constitution PDF text not as expected (layout changed?)")
            return _http.lru_put(_laws, ident, (ident, CONST_TITLE, paras), 16)
        if PA_ID.fullmatch(ident):
            r = await _http.get(f"{PA}/law/LawDetails", params={"lawId": ident[3:]})
            if r.status_code == 404 or (r.status_code == 200 and "DownloadDocument" not in r.text):
                raise NotFound(f"parlament.ba has no consolidated law {ident}.")
            if r.status_code != 200:
                raise SourceError(_http.error("parlament.ba", f"{ident} failed", r.status_code), r.status_code)
            m = re.search(r"(?is)<h1>(.*?)</h1>", r.text)
            title = _http.clean(_html.unescape(re.sub(r"<[^>]+>", " ", m[1]))) if m else ident
            links = re.findall(r'href="(/law/DownloadDocument\?[^"]*langTag=bs[^"]*)"', r.text) or \
                re.findall(r'href="(/law/DownloadDocument\?[^"]*)"', r.text)
            d = await _http.get(PA + _html.unescape(links[0]))
            if d.status_code != 200:
                raise SourceError(_http.error("parlament.ba", f"{ident} PDF failed", d.status_code), d.status_code)
            paras = _lines_to_paras(_http.pdf_text(d.content))
            if len("".join(paras)) < 200:
                raise SourceError(f"parlament.ba: {ident} PDF has no text layer.")
            return _http.lru_put(_laws, ident, (ident, title, paras), 16)
        r = await _http.get(f"{FB}/{ident}")
        page = _fb_get_text(r, ident)
        paras = _paragraphs(page)
        if not paras or len("".join(paras)) < 100:
            raise NotFound(f"fbihvlada.gov.ba page {ident} has no law text.")
        m = re.search(r'(?is)<h1 class="title">(.*?)</h1>', page)
        title = _http.clean(_html.unescape(re.sub(r"<[^>]+>", " ", m[1]))) if m else ""
        title = re.sub(r"^\d+\.\s*", "", title)
        if not title:   # old static page: the upper-case heading lines at the top
            head = []
            for p in paras[:6]:
                t = _http.clean(re.sub(r"[*_]", "", p))
                if head and (t != t.upper() or re.match(r"[IVX]+\s*[-.]", t)):
                    break
                head.append(t)
            title = re.sub(r"^Z\s*A\s*K\s*O\s*N\b", "ZAKON", " ".join(head))[:200] or ident
        return _http.lru_put(_laws, ident, (ident, title, paras), 16)

    async def get_legislation_toc(self, id):
        ident, title, paras = await self._law(id)
        arts = _const_articles(paras) if ident == CONST_ID else _articles(paras)
        entries = [TocEntry(title=heading, level=0, provision=label) for label, _, heading in arts]
        if not entries:
            entries = [TocEntry(title="(no articles found: read the full text)", level=0, provision="")]
        return Toc(id=ident, title=title, url=_law_url(ident), entries=entries)

    async def get_legislation_provision(self, id, provision):
        ident, title, paras = await self._law(id)
        const = ident == CONST_ID
        want = _norm_const(provision) if const else _norm_prov(provision)
        arts = _const_articles(paras) if const else _articles(paras)
        for k, (label, i, _) in enumerate(arts):
            if (label if const else _norm_prov(label)) == want:
                end = arts[k + 1][1] if k + 1 < len(arts) else len(paras)
                return Provision(law_id=ident, law_title=title, provision=label,
                                 text="\n\n".join(paras[i:end]), url=_law_url(ident))
        raise NotFound(f"No article {provision!r} in {title}. Use get_legislation_toc for the labels.")

    async def get_legislation_text(self, id):
        ident, title, paras = await self._law(id)
        status = ("Constitution of BiH with Amandman I (2009), Bosnian text from the Parliament's PDF" if ident == CONST_ID
                  else "unofficial consolidated text (Parliament of BiH); authentic text is in Službeni glasnik BiH"
                  if PA_ID.fullmatch(ident) else "text as published in Službene novine FBiH (not consolidated)")
        return LawText(id=ident, title=title, text="\n\n".join(paras), url=_law_url(ident),
                       metadata={"Status": status})
