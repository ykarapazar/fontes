"""Indonesia: national legislation from JDIH Kementerian Sekretariat Negara (jdih.setneg.go.id),
the State Secretariat's legal documentation site (it publishes the official "Salinan" copies of
Undang-Undang, Perpu, PP, Perpres, Keppres and Inpres).

The site is a static Next.js app over its own JSON API on the same host (no key):
  * Search: POST /api/hukumproduk/produkhukum
      {"tentang": q, "p_lihan": "semua", "jns": ["UU"], "thn": ["2022"], "status": "",
       "terx": "All", "sortOrder": "desc", "length": n, "start": offset}
    -> {"data": [...], "jml": total}. `tentang` matches the title and also "27 tahun 2022".
  * Detail: POST /api/hukumproduk/detaildata {"jns","no","thn","k": ""} -> {"row": [..], "file": [..]};
    unknown -> 404 {"message": "Data tidak ditemukan"}.
  * Relations: POST /api/hukumproduk/status {idx, dc, dcs, dd, dds, dm, dms, dme, dmes, dt}
    -> HTML <label data-jns data-no data-thn data-original-title> snippets per relation.
  * PDF: GET /api/hukumproduk/pdf?l=uploads&f=<realName>&fl=<idperaturan>.
The text is the PDF's own text layer (scans that were OCR'd by the publisher): expect OCR slips
("Pasal I" for "Pasal 1", "(l)" for "(1)"). No OCR here. Texts are as enacted, not consolidated.

The site's own label for a law is "<JNS> <no>/<year>" (e.g. "UU 3/2024"); that is our id.

Verified 2026-11-05/06 (UK IP):
  * jdih.setneg.go.id/robots.txt: "User-agent: * / Disallow:" (everything allowed). No terms
    of use on the site; setneg.go.id only says "Copyrights (c) 2019 ... All Rights Reserved by
    Kementerian Sekretariat Negara RI". Statutes carry no copyright in Indonesia
    (UU 28/2014 on Copyright, Pasal 42 b).
  * Not used: peraturan.bpk.go.id (Cloudflare challenge on every page, incl. sitemap);
    peraturan.go.id and jdihn.go.id (timed out twice); putusan3.mahkamahagung.go.id (robots.txt
    "User-agent: * Disallow: /", Content-Signal ai-train=no, ClaudeBot/anthropic-ai disallowed;
    Cloudflare); mkri.id / jdih.mkri.id / jdih.mahkamahagung.go.id (Cloudflare challenge).
    So there is no case-law route.

The Constitution (UUD 1945) is not a JDIH Setneg type. It comes from the MPR (the body that
amends it): www.mpr.go.id/sosialisasi/uud-nri-1945 links the MPR Secretariat-General's book
(PDF, ~35 MB, text layer), which ends with the official consolidated text "dalam satu naskah"
(as amended 1999-2002). Only that last part is used; id "UUD 1945". mpr.go.id robots.txt only
names facebookexternalhit; footer "HAK CIPTA (c) SEKRETARIAT JENDERAL MPR RI"; no terms page.
Verified 2026-11-10 (UK IP). peraturan.go.id timed out again (3 tries, 2026-11-10).
"""
from __future__ import annotations

import re
from urllib.parse import parse_qs, quote, urlparse

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import LawHit, LawText, Provision, Results, Toc, TocEntry

HOST = "jdih.setneg.go.id"
SITE = f"https://{HOST}"
API = f"{SITE}/api/hukumproduk"
MAX_PDF = 30_000_000   # e.g. UU 6/2023 (Cipta Kerja) is an 85 MB scan: link it instead

TYPES = {  # jns code -> long names the user may type (lower case)
    "UU": ("undang-undang", "undang undang"),
    "PERPU": ("peraturan pemerintah pengganti undang-undang", "perppu"),
    "PP": ("peraturan pemerintah",),
    "PERPRES": ("peraturan presiden",),
    "KEPPRES": ("keputusan presiden",),
    "INPRES": ("instruksi presiden",),
    "PERMENSESNEG": ("peraturan menteri sekretaris negara",),
    "KEPMENSESNEG": ("keputusan menteri sekretaris negara",),
}
_LONG = sorted(((n, k) for k, ns in TYPES.items() for n in ns), key=lambda x: -len(x[0]))
_ID = re.compile(r"^([A-Za-z]+)\s*/?\s*(?:No\.?|Nomor)?\s*([\w./-]+?)\s*(?:/|\s+Tahun\s+)(\d{4})$", re.I)

_PAGENO = re.compile(r"^[-–_.]\s*[\dtlIO]{1,3}\s*[-–_.]?$|^\d{1,3}\s*[-–_]$")
_HEADER = re.compile(r"^(SALINAN|Menimbang|Mengingat|[A-Z.]{0,3}[PF]R[EI]S[IT]D[EI]N|"
                     r".{0,6}[BUL]{1,3}IK INDONES.A)$")
_SKNO = re.compile(r"^SK\s*No\b", re.I)
_DOTS = re.compile(r"(\.\s*){3}$|…$")
_PASAL = re.compile(r"^\W{0,3}Pasa[l1I7]\s*([0-9IlOT]{1,3}[A-Z]?)$")
_LN = re.compile(r"^LEMBARAN NEGARA REPUBLIK INDONESIA TAHUN")
_STRUCT = re.compile(r"^(BAB|Bagian|Paragraf)\s+\S+")
_START = re.compile(r"^(\(\w{1,3}\)|[a-zA-Z0-9]{1,3}\.\s|[a-z]\)\s|Menimbang|Mengingat|Menetapkan|"
                    r"MEMUTUSKAN|Dengan Persetujuan|Agar setiap|Disahkan|Diundangkan|Ditetapkan)")
_CLOSING = re.compile(r"^Agar setiap orang")
_text_cache: dict = {}
_VARIANTS = {"perlindungan": "pelindungan", "pelindungan": "perlindungan"}  # official titles use 'Pelindungan'

MPR = "https://www.mpr.go.id"
UUD_ID = "UUD 1945"
UUD_PAGE = f"{MPR}/sosialisasi/uud-nri-1945"
UUD_TITLE = "Undang-Undang Dasar Negara Republik Indonesia Tahun 1945 (dalam satu naskah)"
_UUD = re.compile(r"^(uud|undang[- ]undang dasar)(\s+nri)?(\s+(negara republik indonesia\s+)?"
                  r"(tahun\s+)?1945)?$|^(constitution|konstitusi)$", re.I)
_UUD_Q = re.compile(r"undang[- ]undang dasar|\buud\b|konstitusi|constitution", re.I)
_UUD_DROP = re.compile(r"^\d{6,}_BUKU|^[-—–_]\s*[\dlIO]{1,3}\s*[-—–_]$|"
                       r"^[^A-Za-z]{0,12}:\s*Perubahan\s+(Pertama|Kedua|Ketiga|Keempat)$")


def _uud_lines(data: bytes) -> list[str]:
    """Lines of the consolidated part of the MPR book. pypdf's layout mode keeps each ayat
    number '(2)' on its text line; plain mode puts them in a separate column on many pages."""
    import io

    from pypdf import PdfReader
    pages = PdfReader(io.BytesIO(data)).pages
    start = next((i for i in range(len(pages) - 1, -1, -1)
                  if "DALAM SATU NASKAH" in (pages[i].extract_text() or "")), None)
    if start is None:
        return []
    lines = []
    for pg in pages[start:]:
        for ln in pg.extract_text(extraction_mode="layout").splitlines():
            ln = _http.clean(ln)
            if ln and not _UUD_DROP.match(ln):
                ln = re.sub(r"^Pasa[l1I]\s*(\d+)\s*([A-J]?)\s*\**\)?$", r"Pasal \1\2", ln)
                lines.append("Pasal 28I" if ln == "Pasal 281" else ln)
    first = next((i for i, ln in enumerate(lines) if ln == "PEMBUKAAN"), 0)
    return lines[first:]


def _uud_hit() -> LawHit:
    return LawHit(id=UUD_ID, title=UUD_TITLE, type="Undang-Undang Dasar", number="1945",
                  date="1945-08-18", status="in force (as amended 1999-2002)", url=UUD_PAGE)


def _s(v) -> str:
    return "" if v is None else str(v).strip()


def _upper(s: str) -> bool:
    letters = [c for c in s if c.isalpha()]
    return len(letters) >= 3 and sum(c.isupper() for c in letters) / len(letters) > 0.9


def _parse_id(raw: str) -> tuple[str, str, str]:
    """'UU 27/2022', 'UU/27/2022', 'UU No. 27 Tahun 2022', 'Undang-Undang Nomor 27 Tahun 2022'
    or a detailperaturan URL -> ("UU", "27", "2022")."""
    s = _http.clean(raw)
    if "detailperaturan" in s:
        q = parse_qs(urlparse(s).query)
        if all(q.get(k) for k in ("jns", "no", "thn")):
            return q["jns"][0].upper(), q["no"][0], q["thn"][0]
    low = s.lower()
    for name, code in _LONG:
        if low.startswith(name):
            s = code + s[len(name):]
            break
    m = _ID.match(s)
    if not m or m[1].upper() not in TYPES:
        raise BadRequest("Use the id from search_legislation, e.g. 'UU 27/2022' or 'PP 35/2021' "
                         f"(types: {', '.join(TYPES)}), or 'Undang-Undang Nomor 27 Tahun 2022'.")
    return m[1].upper(), m[2], m[3]


def _law_id(jns, no, thn) -> str:
    return f"{jns} {no}/{thn}"


def _url(jns, no, thn) -> str:
    return f"{SITE}/detailperaturan?jns={quote(jns)}&no={quote(no)}&thn={quote(thn)}"


def _title(r: dict) -> str:
    return _http.clean(f"{_s(r.get('nama_jenis')) or _s(r.get('jns'))} Nomor {_s(r.get('no_peraturan'))} "
                       f"Tahun {_s(r.get('tahun'))} tentang {_s(r.get('tentang'))}")


async def _post(path: str, body: dict, what: str):
    r = await _http.post(f"{API}/{path}", json=body)
    if r.status_code == 404:
        return None
    if r.status_code != 200:
        raise SourceError(_http.error(HOST, f"{what} failed", r.status_code), r.status_code)
    try:
        return r.json()
    except ValueError:
        raise SourceError(_http.error(HOST, f"{what}: not JSON", r.status_code), r.status_code)


# ---------------------------------------------------------------- PDF text -> markdown
def _lines(raw: str) -> list[str]:
    """Drop running headers ("PRESIDEN / REPUBLIK INDONESIA", "-3-"), the "SK No ..." print
    code and the catchword that repeats the next page's first words."""
    out: list[str] = []
    for pg in raw.split("\n\n"):
        lines = pg.split("\n")
        head = 0
        for i, ln in enumerate(lines[:6]):
            if _PAGENO.match(ln) or _HEADER.match(ln):
                head = i + 1
        lines = lines[head:]
        for i, ln in enumerate(lines):
            if _SKNO.match(ln) and len(lines) - i <= 3:
                lines = lines[:i]
                break
        lines = [ln for ln in lines if not _SKNO.match(ln)]
        if lines and _DOTS.search(lines[-1]) and len(lines[-1]) < 60:
            lines = lines[:-1]
        out.extend(lines)
    return out


def _paragraphs(lines: list[str]) -> list[str]:
    """Re-join hard-wrapped lines; headings (Pasal, BAB, upper-case titles) stand alone."""
    paras: list[str] = []
    cur: list[str] = []
    prev_alone = True
    for ln in lines:
        alone = bool(_PASAL.match(ln) or _STRUCT.match(ln) or _upper(ln))
        if alone or prev_alone or _START.match(ln):
            if cur:
                paras.append(" ".join(cur))
            cur = [ln]
        else:
            cur.append(ln)
        prev_alone = alone
    if cur:
        paras.append(" ".join(cur))
    return [re.sub(r"\s+", " ", p).strip() for p in paras if p.strip()]


def _mend(paras: list[str]) -> list[str]:
    """Re-join words the PDF text layer split ("untu k", "didas arkan", "m emenuhi"): two adjacent
    lower-case fragments are glued when the joined word occurs elsewhere in the same text and one
    fragment is a stray (a single letter, or seen at most once as a word of its own)."""
    cnt: dict[str, int] = {}
    for p in paras:
        for w in re.findall(r"(?<![\w-])[a-z]+(?![\w-])", p):
            cnt[w] = cnt.get(w, 0) + 1

    def join(p):
        out = p
        while True:   # restart after each join: pairs overlap ("dibuat untu k")
            for m in re.finditer(r"(?<![\w-])(?=([a-z]+) ([a-z]+)(?![\w-]))", out):
                a, b = m[1], m[2]
                j = cnt.get(a + b, 0)
                if (min(len(a), len(b)) == 1 and j >= 2) or (min(cnt.get(a, 0), cnt.get(b, 0)) <= 1 and j >= 1):
                    out = out[:m.start()] + a + b + out[m.start() + len(a) + 1 + len(b):]
                    break
            else:
                return out
    return [join(p) for p in paras]


def _labels(tokens: list[str]) -> list[str]:
    """Pasal numbers, fixing OCR'd 'I'/'l'/'O'/'T' for digits when the sequence confirms it."""
    out, last = [], 0
    for i, t in enumerate(tokens):
        c = t.translate(str.maketrans("IlOT", "1107"))
        nxt = tokens[i + 1] if i + 1 < len(tokens) else ""
        fits = c.isdigit() and (int(c) == last + 1 or (nxt.isdigit() and int(nxt) == int(c) + 1))
        out.append(c if c != t and fits else t)
        m = re.match(r"\d+", out[-1])
        if m:
            last = int(m[0])
    return out


def _structure(paras: list[str]):
    """-> (toc entries, {label: markdown}, penjelasan markdown)."""
    cut = next((i for i, p in enumerate(paras) if _LN.match(p)), len(paras))
    pj = next((i for i in range(cut, len(paras)) if paras[i].startswith("PENJE")), cut + 1)
    body, penj = paras[:cut], paras[pj:]
    heads = [(i, _PASAL.match(p)[1]) for i, p in enumerate(body) if _PASAL.match(p)]
    labels = _labels([t for _, t in heads])
    starts = {i: lab for (i, _), lab in zip(heads, labels)}
    entries: list[TocEntry] = []
    arts: dict[str, str] = {}
    cur_label, cur = None, []

    def flush():
        if cur_label is not None:
            arts[cur_label] = "\n\n".join(cur)

    i = 0
    while i < len(body):
        p = body[i]
        if i in starts:
            flush()
            lab = starts[i]
            n, base = 2, lab
            while lab in arts or lab == cur_label:
                lab, n = f"{base} ({n})", n + 1
            cur_label, cur = lab, [f"**Pasal {lab}**"]
            entries.append(TocEntry(title=f"Pasal {lab}", level=2, provision=lab))
        elif _STRUCT.match(p) or _CLOSING.match(p):
            flush()
            cur_label, cur = None, []
            if _STRUCT.match(p):
                title = p
                while i + 1 < len(body) and i + 1 not in starts and _upper(body[i + 1]) \
                        and not _STRUCT.match(body[i + 1]):
                    i += 1
                    title += " " + body[i]
                entries.append(TocEntry(title=title, level=0 if p.startswith("BAB") else 1))
        elif cur_label is not None:
            cur.append(p)
        i += 1
    flush()
    penj_md = "\n\n".join(penj)
    if penj_md:
        entries.append(TocEntry(title="Penjelasan (elucidation)", level=0, provision="Penjelasan"))
    return entries, arts, penj_md


def _md(paras: list[str]) -> str:
    out = []
    for p in paras:
        out.append(f"**{p}**" if _PASAL.match(p) or _STRUCT.match(p) else p)
    return "\n\n".join(out)


class Indonesia(Jurisdiction):
    code = "id"
    name = "Indonesia"
    languages = ("id",)
    aliases = ("indonesia", "republik indonesia", "idn", "ri", "jdih", "setneg")
    sources = (
        Source(
            name="JDIH Kementerian Sekretariat Negara (jdih.setneg.go.id) – Produk Hukum",
            url=f"{SITE}/peraturan",
            covers=("legislation",),
            licence=("no licence published; statutes are not copyright-protected "
                     "(UU 28/2014 Pasal 42); site footer 'All Rights Reserved by Kementerian "
                     "Sekretariat Negara RI'"),
            commercial_use=None,
            ai_use=None,   # robots.txt allows everything; no content signals, no AI/TDM clause
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~25 requests (2026-11-06)",
            terms_url="",
        ),
        Source(
            name="Majelis Permusyawaratan Rakyat (www.mpr.go.id) – UUD NRI 1945",
            url=UUD_PAGE,
            covers=("legislation",),
            licence=("no licence published; the Constitution is not copyright-protected "
                     "(UU 28/2014 Pasal 42); site footer 'HAK CIPTA (c) SEKRETARIAT JENDERAL MPR RI'; "
                     "the book says 'MILIK NEGARA, TIDAK DIPERDAGANGKAN'"),
            commercial_use=None,
            ai_use=None,   # robots.txt only names facebookexternalhit; no AI/TDM clause
            auth="none",
            rate_limit="unknown; 1 s spacing, one page + one ~35 MB PDF per load, cached (2026-11-10)",
            terms_url="",
        ),
    )
    legislation_filters = {
        "type": f"document type code, comma-separated: UUD (the Constitution), {', '.join(TYPES)}",
        "year": "year(s) enacted, comma-separated, e.g. '2022' or '2022,2023'",
    }
    min_interval = {HOST: 1.0, "www.mpr.go.id": 1.0}
    notes = ("Legislation only: the Constitution (UUD 1945, consolidated, from the MPR), national "
             "laws and presidential/government regulations (UU, Perpu, PP, Perpres, Keppres, Inpres) and State Secretariat ministerial regulations/decrees "
             "(Permensesneg, Kepmensesneg) from the State Secretariat's JDIH, as "
             "enacted (not consolidated), text from the official PDF's OCR layer. No case-law "
             "source is open to automated access (Supreme Court and Constitutional Court sites "
             "block bots).")
    gaps = (
        "Supreme Court case law (putusan3.mahkamahagung.go.id): robots.txt disallows (Disallow: /, ai-train=no)",
        "Constitutional Court decisions (mkri.id, jdih.mkri.id): bot check / blocks our client (Cloudflare challenge)",
        "Other ministries' and regional regulations: peraturan.bpk.go.id is Cloudflare-challenged; peraturan.go.id, jdihn.go.id timed out (2026-11)",
        "Undang-Undang before 1990 and some later years (earliest UU 7/1983; none for 2004) and Perpu "
        "before 1998: not in JDIH Setneg; BPK (Cloudflare), peraturan.go.id and jdihn.go.id "
        "(timeouts), DPR (403) not usable (2026-11-10)",
        "Consolidated texts of acts: not published by JDIH Setneg (as enacted only); peraturan.bpk.go.id "
        "(Cloudflare challenge) and peraturan.go.id (timed out 2026-11-05..10) not usable",
    )
    samples = {
        "legislation_query": "pelindungan data pribadi",
        "law_id": "UU 27/2022",       # Personal Data Protection Law
        "provision": "1",
    }

    # ------------------------------------------------------------------ #
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        f = {k: str(v).strip() for k, v in (filters or {}).items() if str(v).strip()}
        jns = [x.strip().upper() for x in f.get("type", "").split(",") if x.strip()]
        bad = [x for x in jns if x not in TYPES and x != "UUD"]
        if bad:
            raise BadRequest(f"type must be one of UUD, {', '.join(TYPES)}; got {', '.join(bad)}.")
        # The Constitution (MPR source) is listed first on page 1 when asked for.
        uud = ("UUD" in jns or (not jns and _UUD_Q.search(query or ""))) and \
            (not f.get("year") or "1945" in f["year"])
        if "UUD" in jns:
            jns.remove("UUD")
            if not jns:
                items = [_uud_hit()] if uud and int(page) <= 1 else []
                return Results(items=items, total=1,
                               note="UUD 1945 as amended, consolidated text from the MPR.")
        thn = [x.strip() for x in f.get("year", "").split(",") if x.strip()]
        if any(not re.fullmatch(r"\d{4}", y) for y in thn):
            raise BadRequest(f"year must be YYYY (comma-separated for several), got {f['year']!r}.")
        limit = max(1, min(int(limit), 50))
        q = (query or "").strip()
        words = q.lower().split()
        notes = []

        async def fetch(text, length, start):
            body = {"tentang": text, "p_lihan": "semua", "jns": jns, "thn": thn,
                    "status": "", "terx": "All", "sortOrder": "desc", "length": length, "start": start}
            d = await _post("produkhukum", body, "search")
            if not isinstance(d, dict) or not isinstance(d.get("data"), list):
                raise SourceError(f"{HOST} search: unexpected payload {str(d)[:200]}")
            return d

        def hit_words(r):
            return _title(r).lower()

        if len(words) > 1:
            # The source ORs the words (any word matches), so the count is meaningless: fetch
            # the matches and keep only titles that contain every word (or its spelling variant).
            rows, start = [], 0
            while start < 5000:
                d = await fetch(q, 1000, start)
                rows += d["data"]
                start += 1000
                if len(d["data"]) < 1000 or start >= (d.get("jml") or 0):
                    break
            rows = [r for r in rows if all(w in hit_words(r) or _VARIANTS.get(w, w) in hit_words(r)
                                           for w in words)]
            off = (max(1, int(page)) - 1) * limit
            d = {"data": rows[off:off + limit], "jml": len(rows)}
            notes.append("all words of the query must appear in the title")
        else:
            d = await fetch(q, limit, (max(1, int(page)) - 1) * limit)
            alt = _VARIANTS.get(q.lower())
            if not d["data"] and alt:
                d = await fetch(alt, limit, (max(1, int(page)) - 1) * limit)
                notes.append(f"no title has '{q}'; showing '{alt}' (the official spelling)")
        items = []
        for r in d["data"]:
            jn, no, th = _s(r.get("jns")), _s(r.get("no_peraturan")), _s(r.get("tahun"))
            items.append(LawHit(
                id=_law_id(jn, no, th), title=_title(r), type=_s(r.get("nama_jenis")),
                number=f"{no}/{th}", date=_s(r.get("tgl_di"))[:10],
                status=_s(r.get("status_hukum")), url=_url(jn, no, th)))
        total = d.get("jml")
        if uud:
            items = ([_uud_hit()] + items)[:limit] if int(page) <= 1 else items
            total = total + 1 if isinstance(total, int) else total
        extra = ("; ".join(notes) + ". ") if notes else ""
        if not total and not uud:
            extra += ("Not found in JDIH Setneg (only UU, Perpu, PP, Perpres, Keppres, Inpres and "
                      "Setneg regulations; pre-1983 ordinances such as the KUHPerdata (Burgerlijk "
                      "Wetboek, 1847) are not included). ")
        return Results(items=items, total=total if isinstance(total, int) else None,
                       note=(extra + "Texts are as enacted (not consolidated); search matches title, "
                             "number and year (e.g. '27 tahun 2022'). Result order is "
                             "set by the source and is not guaranteed (not reliably by date or "
                             "relevance); total counts substring matches, so it can far exceed "
                             "exact matches."))

    async def _detail(self, id):
        jns, no, thn = _parse_id(id)
        d = await _post("detaildata", {"jns": jns, "no": no, "thn": thn, "k": ""}, "detail")
        rows = (d or {}).get("row") or []
        if not rows:
            raise NotFound(f"JDIH Setneg has no {_law_id(jns, no, thn)}. Search with "
                           "search_legislation to find the right id.")
        return jns, no, thn, rows[0], d.get("file") or []

    async def _uud(self):
        """The Constitution from the MPR book: only its final consolidated text."""
        if UUD_ID in _text_cache:
            return _text_cache[UUD_ID]
        r = await _http.get(UUD_PAGE)
        m = re.search(r'href="([^"]+\.pdf)"[^>]*class="btn-unduh"', r.text) if r.status_code == 200 else None
        if not m:
            raise SourceError(_http.error("www.mpr.go.id", "UUD 1945 page: no PDF link", r.status_code),
                              r.status_code)
        pdf_url = m[1] if m[1].startswith("http") else MPR + m[1]
        r = await _http.get(pdf_url, timeout=180)
        if r.status_code != 200 or not r.content.startswith(b"%PDF"):
            raise SourceError(_http.error("www.mpr.go.id", "UUD 1945 PDF", r.status_code), r.status_code)
        lines = _uud_lines(r.content)
        if not lines:
            raise SourceError(f"UUD 1945 PDF at {pdf_url}: consolidated part not found (layout changed?)")
        paras = _paragraphs(lines)
        entries, arts, _ = _structure(paras)
        # Transitional (ATURAN PERALIHAN) and additional (ATURAN TAMBAHAN) articles restart at I.
        names = {"I": "Peralihan I", "II": "Peralihan II", "III": "Peralihan III",
                 "I (2)": "Tambahan I", "II (2)": "Tambahan II"}
        arts = {names.get(k, k): v for k, v in arts.items()}
        out = []
        for e in entries:
            if e.provision == "I":
                out.append(TocEntry(title="ATURAN PERALIHAN", level=0))
            if e.provision == "I (2)":
                out.append(TocEntry(title="ATURAN TAMBAHAN", level=0))
            lab = names.get(e.provision, e.provision)
            if lab != e.provision:   # 'Peralihan I' -> heading 'Aturan Peralihan Pasal I'
                head = f"Aturan {lab.split()[0]} Pasal {lab.split()[1]}"
                arts[lab] = re.sub(r"^\*\*Pasal [^*]+\*\*", f"**{head}**", arts[lab])
                e = TocEntry(title=head, level=e.level, provision=lab)
            out.append(e)
        start = next((i for i, p in enumerate(paras) if p.startswith("PEMBUKAAN")), None)
        first = next((i for i, p in enumerate(paras) if _PASAL.match(p) or _STRUCT.match(p)), None)
        if start is not None and first:
            arts["Pembukaan"] = "\n\n".join(["**PEMBUKAAN**"] + paras[start + 1:first])
            out.insert(0, TocEntry(title="Pembukaan (Preamble)", level=0, provision="Pembukaan"))
        meta = {"id": UUD_ID, "title": UUD_TITLE, "url": UUD_PAGE, "pdf": pdf_url, "others": [],
                "row": {"nama_jenis": "Undang-Undang Dasar", "tgl_di": "1945-08-18"},
                "as_of": "2002-08-10"}
        return _http.lru_put(_text_cache, UUD_ID, (meta, paras, (out, arts, "")), 8)

    async def _law(self, id):
        """-> (meta dict, paragraphs, (toc, articles, penjelasan)); cached per law."""
        if _UUD.match(_http.clean(id)):
            return await self._uud()
        jns, no, thn = _parse_id(id)
        key = _law_id(jns, no, thn)
        if key in _text_cache:
            return _text_cache[key]
        jns, no, thn, row, files = await self._detail(id)
        url = _url(jns, no, thn)
        pdfs = [f for f in files if _s(f.get("realName")).lower().endswith(".pdf")]
        if not pdfs:
            raise SourceError(f"{HOST} has no PDF for {key}; see {url}")
        f0 = pdfs[0]
        pdf_url = (f"{API}/pdf?l=uploads&f={quote(_s(f0.get('realName')))}"
                   f"&fl={quote(_s(row.get('idperaturan')))}")
        if int(f0.get("size") or 0) > MAX_PDF:
            raise SourceError(f"The PDF of {key} is {int(f0['size']) // 1_000_000} MB, too large to "
                              f"read here. Open it at {pdf_url}")
        r = await _http.get(pdf_url, timeout=120)
        if r.status_code != 200 or not r.content.startswith(b"%PDF"):
            raise SourceError(_http.error(HOST, f"PDF of {key}", r.status_code), r.status_code)
        raw = _http.pdf_text(r.content)
        if len(raw) < 200:
            raise SourceError(f"The PDF of {key} is a scan without a text layer; read it at {pdf_url}")
        paras = _mend(_paragraphs(_lines(raw)))
        meta = {"id": key, "title": _title(row), "url": url, "pdf": pdf_url, "row": row,
                "others": [_s(x.get("realName")) for x in pdfs[1:]]}
        return _http.lru_put(_text_cache, key, (meta, paras, _structure(paras)), 8)

    async def get_legislation_toc(self, id):
        meta, _, (entries, _, _) = await self._law(id)
        if not any(e.provision for e in entries):
            raise SourceError(f"No 'Pasal' headings found in the text of {meta['id']}; "
                              "use get_legislation_text.")
        return Toc(id=meta["id"], title=meta["title"], url=meta["url"], entries=entries)

    async def get_legislation_provision(self, id, provision):
        meta, _, (_, arts, penj) = await self._law(id)
        p = _http.clean(str(provision))
        if re.fullmatch(r"(?i)penjelasan|elucidation|explanation", p):
            if not penj:
                raise NotFound(f"{meta['id']} has no Penjelasan in its PDF.")
            return Provision(law_id=meta["id"], law_title=meta["title"], provision="Penjelasan",
                             text=penj, url=meta["url"])
        lab = re.sub(r"(?i)^(pasal|art(icle)?\.?|§)\s*", "", p).strip()
        lab = lab.upper() if re.fullmatch(r"\d+[a-z]", lab) else lab
        if meta["id"] == UUD_ID:   # 'Preamble', 'Aturan Peralihan Pasal I', 'tambahan ii'
            m = re.fullmatch(r"(?i)(?:aturan\s+)?(peralihan|tambahan)\s+(?:pasal\s+)?([ivx]+)", lab)
            lab = ("Pembukaan" if re.fullmatch(r"(?i)pembukaan|preamble|preambule", lab)
                   else f"{m[1].capitalize()} {m[2].upper()}" if m else lab)
        if lab not in arts:
            raise NotFound(f"{meta['id']} has no Pasal {lab!r}. Labels look like '1', '27A' "
                           "(see get_legislation_toc), or 'Penjelasan'"
                           + ("; for UUD 1945 also 'Pembukaan', 'Peralihan I', 'Tambahan II'."
                              if meta["id"] == UUD_ID else "."))
        text = arts[lab]
        st = _s(meta["row"].get("status_hukum"))
        if meta["id"] != UUD_ID:
            if not st:   # the detail record has no status_hukum; the search row does
                jn, no, th = _parse_id(meta["id"])
                try:
                    d = await _post("produkhukum", {"tentang": f"{no} tahun {th}", "p_lihan": "semua",
                                                    "jns": [jn], "thn": [th], "status": "", "terx": "All",
                                                    "sortOrder": "desc", "length": 50, "start": 0}, "status")
                    st = next((_s(r.get("status_hukum")) for r in (d or {}).get("data", [])
                               if _s(r.get("no_peraturan")) == no), "")
                except SourceError:
                    pass
            rel = await self._relations(meta["row"]) if st and st != "berlaku" else {}
            by = "; ".join(f"{k}: {v}" for k, v in rel.items() if k.endswith(" by"))
            text = (f"_As enacted in {meta['id'].split('/')[-1]} (not consolidated); text is the PDF's OCR "
                    "layer, so check figures, numbering and names against the PDF (e.g. 'Fribadi' for "
                    "'Pribadi', '1O.' for '10.')"
                    + (f"; status at JDIH Setneg: {st}, so later laws have amended or repealed "
                       "part of the law; this text may not be current ("
                       + (f"JDIH lists, for the law as a whole: {by}; JDIH does not say which Pasal each "
                          "one changed, so check those laws for the current wording of this Pasal"
                          if by else "JDIH links no amending law to this one, so the current wording of this Pasal is "
                            "not available here; look for it in the consolidated text at peraturan.bpk.go.id")
                       + ")" if st and st != "berlaku" else "")
                    + "._\n\n" + text)
        return Provision(law_id=meta["id"], law_title=meta["title"], provision=lab,
                         text=text, url=meta["url"], as_of=meta.get("as_of", ""))

    async def get_legislation_text(self, id):
        meta, paras, _ = await self._law(id)
        row = meta["row"]
        md = {"PDF": meta["pdf"], "Type": _s(row.get("nama_jenis")),
              "Enacted (ditetapkan)": _s(row.get("tgl_di"))[:10],
              "Promulgated (diundangkan)": _s(row.get("diundangkan"))[:10]}
        if row.get("ln"):
            md["Lembaran Negara"] = f"{row['ln']}/{_s(row.get('tahun'))}"
        if row.get("tln"):
            md["Tambahan Lembaran Negara"] = _s(row["tln"])
        if meta["others"]:
            md["Other files (not read)"] = "; ".join(meta["others"])
        md.update(await self._relations(row))
        return LawText(id=meta["id"], title=meta["title"], text=_md(paras), url=meta["url"],
                       as_of=meta.get("as_of", ""), metadata={k: v for k, v in md.items() if v})

    async def _relations(self, row) -> dict[str, str]:
        """Amended / repealed by and amends / repeals, as '<JNS> <no>/<year> (title)'."""
        keys = {"dc": "dicabut", "dcs": "dicabut_sebagian", "dd": "diubah", "dds": "diubah_sebagian",
                "dm": "mencabut", "dms": "mencabutsebagian", "dme": "mengubah", "dmes": "mengubahsebagian"}
        body = {k: _s(row.get(v)) for k, v in keys.items()}
        if not any(body.values()):
            return {}
        body.update(idx=_s(row.get("idperaturan")), dt="")
        try:
            d = await _post("status", body, "relations") or {}
        except SourceError:
            return {}
        labels = {"dc": "Repealed by", "dcs": "Partly repealed by", "du": "Amended by",
                  "dus": "Partly amended by", "mc": "Repeals", "mcs": "Partly repeals",
                  "me": "Amends", "mes": "Partly amends"}
        out = {}
        for k, name in labels.items():
            v = d.get(k)
            html = "".join(v) if isinstance(v, list) else _s(v)
            refs = re.findall(r'data-jns="([^"]*)" data-no="([^"]*)" data-thn="([^"]*)"[^>]*?'
                              r'data-original-title="([^"]*)"', html)
            if refs:
                out[name] = "; ".join(f"{_law_id(j, n, t)} ({_http.clean(ti)})" for j, n, t, ti in refs)
        return out
