"""Montenegro: Constitutional Court decisions from the Court's own archive (ustavnisud.me).

Source: "Sudska arhiva" at https://www.ustavnisud.me/ustavnisud/arhiva.php, the Court's
digitised decisions since 1964 (Council of Europe / EU project). The page is a DataTables
front end over two endpoints, used here exactly as the page uses them:
  * Search: POST upit.php (form fields; DataTables `draw/start/length`). JSON
    {"recordsTotal", "recordsFiltered", "data": [rows]}. Row keys: iddok (the archive's
    document id), djelovodni_broj (case number, e.g. "U-III br.339/24"), datum (registry
    date of the case, not the decision date), vrsta_dokumenta (procedure type),
    komitent (applicant; empty in anonymised recent cases), osporeni_akt (challenged act),
    kljucne_rijeci_tagovi, sadrzaj_fajlova (the files' text as indexed: letters with
    diacritics are dropped, cut at 65,535 chars; empty for many cases).
      - left_search: matches content and all attributes; diacritics fold ("pravicno" ==
        "pravično"); a multi-word query is one phrase against the de-diacritised text, so
        use single words.
      - djelovodni_broj: substring of the case number exactly as stored (spacing varies:
        "U-III br.339/24" vs "U-I br. 5/13"), so search by "339/24".
      - vrsta_predmeta: one of the <select> option strings (TYPES below).
      - godina_pretraga: year. Sending DataTables `order[...]` breaks the PHP (SQL error),
        so results come in the source's own order.
  * Files: GET obrada_fajlovi.php?iddok=N -> {"poruka": "Uspjesno", "linkovi": [{link,
    naziv_fajla, korisnicki_naziv, tip, datum}]}. Each call copies the files to a
    time-stamped ./webfolder/ name (the link the page offers); unknown id -> empty list.
    Files are .docx (most since ~2014), .doc (Word 97, e.g. 2020) or .pdf (older; the
    ones checked are scans with no text layer, so no text without OCR).
  * There is no per-decision page: `url` is the archive search page.

Verified 2026-11-05/06:
  * robots.txt (www.ustavnisud.me): "User-agent: * / Allow: /" plus sitemaps; no
    Content-Signal, no AI clause. The site has no terms-of-use page; footer
    "© 2026 Ustavni sud Crne Gore. Sva prava zadržana."
  * Not used:
      - sudovi.me (courts portal, case law of all other courts): Cloudflare "Attention
        Required" block page (403) from the UK, and its robots.txt disallows AI user
        agents (ClaudeBot, Claude-User, ChatGPT-User, ...) with Content-Signal ai-train=no.
      - sluzbenilist.me (Official Gazette): acts are shown only as page images (JPEG), no
        text without OCR. regis.sluzbenilist.me (consolidated texts) is a paid subscription
        portal whose terms forbid free users any copying ("Besplatnim korisnicima strogo je
        zabranjeno svako kopiranje, reprodukovanje ili distribuiranje prečišćenih propisa").
"""
from __future__ import annotations

import datetime
import io
import re
import struct
import zipfile

from lxml import etree

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import Decision, DecisionHit, Results

HOST = "www.ustavnisud.me"
BASE = f"https://{HOST}/ustavnisud"
ARCHIVE = f"{BASE}/arhiva.php"
COURT = "Ustavni sud Crne Gore"
MAX_LIMIT = 50
_rows: dict = {}          # iddok -> search row (small LRU, enriches get_decision)

# Short code -> the archive's own <select> value (the variant that holds the cases).
TYPES = {
    "R": "R Podnesci gradjana koji se odnose na pitanja o kojima Ustavni sud ne vodi postupak",
    "U-I": "U-I Postupak za ocjenu saglasnosti zakona sa Ustavom i potvrdjenim i objavljenim međunarodnim ugovorima",
    "U-II": "U-II Postupak za ocjenu saglasnosti drugih propisa i opštih akata sa Ustavom i zakonom",
    "U-III": "U-III Postupak odlučivanja o ustavnoj žalbi",
    "UZ-III": "Uz-III Postupak odlučivanja o ustavnoj zalbi",
    "U-IV": "U-IV Postupak odlučivanja da li je predsjednik Crne Gore povrijedio Ustav",
    "U-V": "U-V Postupak odlučivanja o sukobu nadležnosti",
    "U-VI": "U-VI Postupak odlučivanja o izbornim sporovima i sporovima u vezi sa referendumom",
    "U-VII": "U-VII Postupak odlučivanja o izbornim sporovima i sporovima u vezi sa rešerendumom",
    "U-VIII": "U-VIII Praćenje  i obavještavanje Skupštine o uočenim pojavama neustavnosti i nezakonitosti",
}
_MONTHS = {m: i for i, m in enumerate(("januar", "februar", "mart", "april", "maj", "jun", "jul",
                                        "avgust", "septembar", "oktobar", "novembar", "decembar"), 1)}
_DATE_RE = re.compile(r"\b(\d{1,2})\.?\s*(" + "|".join(_MONTHS) + r")a?\s+(\d{4})\b", re.I)
_CASE_RE = re.compile(r"\bU[žz]?\s*-\s*[IVX]+\s*br\.?\s*\d+\s*/\s*\d{2,4}|\bU\s+br\.?\s*\d+\s*/\s*\d{2,4}", re.I)


def _this_year() -> int:
    return datetime.date.today().year


def _s(v) -> str:
    return _http.clean(v) if v not in (None, "None", "null") else ""


def _norm_case(s: str) -> str:
    return re.sub(r"[\s.]", "", s.lower().replace("ž", "z"))


def _type_code(row: dict) -> str:
    m = re.match(r"(U[žz]?-[IVX]+|R|U)\b", _s(row.get("djelovodni_broj")) or _s(row.get("vrsta_dokumenta")))
    return m.group(1) if m else ""


def _title(case_no: str) -> str:
    return f"{COURT}, {case_no}" if case_no else COURT


def _hit(row: dict) -> DecisionHit:
    case_no = _s(row.get("djelovodni_broj"))
    bits = [("Podnosilac", _s(row.get("komitent"))), ("Osporeni akt", _s(row.get("osporeni_akt"))),
            ("Ključne riječi", _s(row.get("kljucne_rijeci_tagovi")).strip(" ,"))]
    reg = _http.iso_date(row.get("datum"))
    snippet = "; ".join(f"{k}: {v}" for k, v in [("Datum upisa", reg), *bits] if v)
    return DecisionHit(id=str(row["iddok"]), title=_title(case_no), court=COURT,
                       date="", case_number=case_no,
                       snippet=snippet[:300], url=ARCHIVE)


# --------------------------------------------------------------------------- #
# Word files -> text (no extra dependencies)
# --------------------------------------------------------------------------- #
_W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def docx_paragraphs(data: bytes) -> list[str]:
    """Paragraph texts of a .docx (main document part), cleaned, empty ones dropped."""
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        root = etree.fromstring(z.read("word/document.xml"))
    out = []
    for p in root.iter(f"{_W}p"):
        buf = []
        for el in p.iter(f"{_W}t", f"{_W}tab", f"{_W}br"):
            buf.append((el.text or "") if el.tag == f"{_W}t" else " ")
        line = _http.clean("".join(buf))
        if line:
            out.append(line)
    return out


def _cfb_streams(data: bytes, wanted: set[str]) -> dict[str, bytes]:
    """Minimal OLE2 / Compound File reader: the named top-level streams' bytes."""
    if data[:8] != b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
        raise ValueError("not an OLE2 file")
    ssz = 1 << struct.unpack_from("<H", data, 0x1E)[0]
    msz = 1 << struct.unpack_from("<H", data, 0x20)[0]
    n_fat, dir_start = struct.unpack_from("<II", data, 0x2C)
    cutoff, mfat_start, n_mfat, difat_start, n_difat = struct.unpack_from("<IIIII", data, 0x38)

    def sector(n):
        return data[(n + 1) * ssz:(n + 2) * ssz]

    difat = list(struct.unpack_from("<109I", data, 0x4C))
    s = difat_start
    for _ in range(n_difat):
        vals = struct.unpack(f"<{ssz // 4}I", sector(s))
        difat += vals[:-1]
        s = vals[-1]
    fat: list[int] = []
    for n in difat[:n_fat]:
        fat += struct.unpack(f"<{ssz // 4}I", sector(n))

    def chain(start, table):
        seen, n = [], start
        while n < 0xFFFFFFFA and len(seen) <= len(table):
            seen.append(n)
            n = table[n]
        return seen

    directory = b"".join(sector(n) for n in chain(dir_start, fat))
    entries = []
    for i in range(0, len(directory), 128):
        e = directory[i:i + 128]
        nlen = struct.unpack_from("<H", e, 64)[0]
        name = e[:max(0, nlen - 2)].decode("utf-16-le", "ignore")
        entries.append((name, e[66], *struct.unpack_from("<II", e, 116)))
    root_start = entries[0][2]
    ministream = b"".join(sector(n) for n in chain(root_start, fat))
    minifat: list[int] = []
    for n in chain(mfat_start, fat)[:n_mfat]:
        minifat += struct.unpack(f"<{ssz // 4}I", sector(n))
    out = {}
    for name, typ, start, size in entries:
        if typ != 2 or name not in wanted:
            continue
        if size < cutoff:
            raw = b"".join(ministream[n * msz:(n + 1) * msz] for n in chain(start, minifat))
        else:
            raw = b"".join(sector(n) for n in chain(start, fat))
        out[name] = raw[:size]
    return out


def doc_paragraphs(data: bytes) -> list[str]:
    """Paragraph texts of a Word 97-2003 .doc (main text via the piece table), cleaned."""
    st = _cfb_streams(data, {"WordDocument", "0Table", "1Table"})
    wd = st["WordDocument"]
    if struct.unpack_from("<H", wd, 0)[0] != 0xA5EC:
        raise ValueError("not a Word document")
    flags = struct.unpack_from("<H", wd, 0x0A)[0]
    table = st["1Table" if flags & 0x0200 else "0Table"]
    ccp_text = struct.unpack_from("<i", wd, 0x4C)[0]
    fc_clx, lcb_clx = struct.unpack_from("<II", wd, 0x01A2)
    clx = table[fc_clx:fc_clx + lcb_clx]
    i = 0
    while i < len(clx) and clx[i] == 0x01:              # skip Prc (property) blocks
        i += 3 + struct.unpack_from("<H", clx, i + 1)[0]
    if i >= len(clx) or clx[i] != 0x02:
        raise ValueError("no piece table")
    lcb = struct.unpack_from("<I", clx, i + 1)[0]
    plc = clx[i + 5:i + 5 + lcb]
    n = (lcb - 4) // 12
    cps = struct.unpack_from(f"<{n + 1}I", plc, 0)
    text = []
    for k in range(n):
        fc = struct.unpack_from("<I", plc, 4 * (n + 1) + 8 * k + 2)[0]
        cnt = cps[k + 1] - cps[k]
        if fc & 0x40000000:
            off = (fc & ~0x40000000) // 2
            text.append(wd[off:off + cnt].decode("cp1252", "replace"))
        else:
            text.append(wd[fc:fc + 2 * cnt].decode("utf-16-le", "replace"))
    body = "".join(text)[:ccp_text]
    body = re.sub(r"\x13[^\x13\x14\x15]*\x14?|\x15", "", body)     # field codes: keep results only
    body = body.replace("\x07", "\r").replace("\x0b", "\r").replace("\x0c", "\r")
    lines = [_http.clean(re.sub(r"[\x00-\x08\x0e-\x1f]", "", ln)) for ln in body.split("\r")]
    return [ln for ln in lines if ln]


def _file_text(name: str, data: bytes) -> str:
    ext = name.rsplit(".", 1)[-1].lower()
    try:
        if ext == "docx":
            return "\n\n".join(docx_paragraphs(data))
        if ext == "doc":
            return "\n\n".join(doc_paragraphs(data))
        if ext == "pdf":
            return _http.pdf_text(data)
    except Exception:          # malformed file: fall back to the index text
        return ""
    return ""


# --------------------------------------------------------------------------- #
class Montenegro(Jurisdiction):
    code = "me"
    name = "Montenegro"
    languages = ("sr-Latn-ME", "cnr")
    aliases = ("montenegro", "crna gora", "mne", "ustavni sud crne gore", "constitutional court of montenegro")
    sources = (
        Source(
            name="Ustavni sud Crne Gore (ustavnisud.me) – Sudska arhiva",
            url=ARCHIVE,
            covers=("caselaw",),
            licence=("unknown: no terms of use or licence on the site (footer '© Ustavni sud Crne "
                     "Gore. Sva prava zadržana.'); official court decisions"),
            commercial_use=None,
            ai_use=None,   # robots.txt "Allow: /", no Content-Signal, no AI/TDM clause
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~30 requests (2026-11)",
            terms_url="",
        ),
    )
    caselaw_filters = {
        "case_number": "case number or its number/year part, e.g. 'U-III br. 339/24' or '339/24'",
        "type": "procedure: " + ", ".join(TYPES) + " (UZ-III = constitutional complaints before 2016)",
        "year": "YYYY, or a range 'YYYY-YYYY' / 'YYYY-' (up to 15 years), year the case was registered",
        "challenged_act": "words from the challenged law/act (osporeni akt), e.g. 'Zakon o radu'",
    }
    min_interval = {HOST: 1.0}
    notes = ("Case law only: Constitutional Court of Montenegro decisions (1964-) from the Court's "
             "archive. Search single words (diacritics optional). Ordinary courts (sudovi.me) block "
             "automated access; the Official Gazette shows acts only as page images. "
             "No legislation text here: laws (e.g. Krivični zakonik, Zakon o radu) are only in the "
             "Official Gazette as page scans (sluzbenilist.me) or as paid consolidated text "
             "(regis.sluzbenilist.me); read them there.")
    gaps = (
        "Ordinary courts' case law (sudovi.me): Cloudflare blocks our client (403) and robots.txt"
         " disallows AI agents",
        "Legislation as published (Official Gazette, sluzbenilist.me): scans only, acts shown as "
         "page images (JPEG), no text",
        ("Parliament's laws site (zakoni.skupstina.me): session agendas with bills (Predlog zakona) since "
         "2013, as proposed, no constitution, no consolidation; Content-Signal ai-train=no (2026-11-10)"),
        "Consolidated legislation (regis.sluzbenilist.me): paid; terms forbid copying ('strogo je"
         " zabranjeno svako kopiranje')",
        "Older Constitutional Court decisions filed as PDF scans: scans only, no text",
    )
    samples = {
        "caselaw_query": "Kadić",
        "decision_id": "24915",   # Už-III br. 305/14 (2014), .docx
    }

    # ------------------------------------------------------------------ #
    async def _search(self, form: dict, start: int, length: int) -> dict:
        data = {"draw": "1", "start": str(start), "length": str(length),
                "godina_pretraga": "svi", "mjesec_pretraga": "svi", "vrsta_predmeta": "svi", **form}
        r = await _http.post(f"{BASE}/upit.php", data=data)
        if r.status_code != 200:
            raise SourceError(_http.error("ustavnisud.me", "archive search failed", r.status_code), r.status_code)
        try:
            d = r.json()
        except ValueError:
            raise SourceError(_http.error("ustavnisud.me", "archive search: not JSON", r.status_code,
                                          r.text[:200]), r.status_code)
        if not isinstance(d, dict) or not isinstance(d.get("data"), list):
            raise SourceError(f"ustavnisud.me archive search: unexpected payload {str(d)[:200]}")
        for row in d["data"]:
            if row.get("iddok"):
                _http.lru_put(_rows, str(row["iddok"]), row, 256)
        return d

    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        f = {k: str(v).strip() for k, v in (filters or {}).items() if str(v).strip()}
        form: dict[str, str] = {}
        q = (query or "").strip()
        case_q = q if _CASE_RE.fullmatch(q) else ""
        if q and not case_q:
            form["left_search"] = q
        cn = f.get("case_number") or case_q
        if cn:
            m = re.search(r"\d+\s*/\s*\d{2,4}", cn)
            if not m:
                raise BadRequest(f"case_number must contain number/year, e.g. '339/24', got {cn!r}.")
            form["djelovodni_broj"] = re.sub(r"\s", "", m.group(0))
        if "type" in f:
            t = f["type"].upper().replace("Ž", "Z")
            if t not in TYPES:
                raise BadRequest(f"type must be one of {', '.join(TYPES)}, got {f['type']!r}.")
            form["vrsta_predmeta"] = TYPES[t]
        years: list[str] = [""]
        if "year" in f:
            m = re.fullmatch(r"((?:19|20)\d{2})\s*(?:(-|–|\.\.)\s*((?:19|20)\d{2})?)?", f["year"])
            if not m:
                raise BadRequest(f"year must be YYYY or a range like 2022-2026 or 2022-, got {f['year']!r}.")
            a = int(m[1])
            b = int(m[3]) if m[3] else (_this_year() if m[2] else a)
            if b < a or b - a >= 15:
                raise BadRequest(f"year range must run forward and span at most 15 years, got {f['year']!r}.")
            years = [str(y) for y in range(b, a - 1, -1)]      # newest year first
        if "challenged_act" in f:
            form["left_osporeni_akt"] = f["challenged_act"]

        limit = max(1, min(int(limit), MAX_LIMIT))
        offset = (max(1, int(page)) - 1) * limit
        note = ("Date shown in the snippet (Datum upisa) = the case's registry date, not the decision date "
                "(get_decision gives the decision date). Results are in the archive's own order (not by "
                "date). Search single words.")
        pref = re.match(r"U[žz]?-[IVX]+", cn or "", re.I)
        if cn and "-" in cn:
            # full case number: the archive matches only the number part, so narrow by the procedure
            # prefix and keep exact matches, looking through up to 4 archive pages
            if pref and "vrsta_predmeta" not in form:
                code = pref.group(0).upper().replace("Ž", "Z")
                if code in TYPES:
                    form["vrsta_predmeta"] = TYPES[code]
            if years != [""]:
                form["godina_pretraga"] = years[0] if len(years) == 1 else "svi"
            rows, total = [], 0
            for start in range(0, 4 * MAX_LIMIT, MAX_LIMIT):
                d = await self._search(form, start, MAX_LIMIT)
                rows += d["data"]
                total = int(d.get("recordsFiltered") or 0)
                if start + MAX_LIMIT >= total:
                    break
            want = _norm_case(cn)
            exact = [r for r in rows if _norm_case(_s(r.get("djelovodni_broj"))) == want]
            if exact:
                rows, total = exact, len(exact)
            else:
                note += f" No case numbered exactly {cn!r}; showing cases whose number contains it."
            return Results(items=[_hit(r) for r in rows[offset:offset + limit]], total=total, note=note)

        rows, total = await self._window(form, years, offset, limit)
        return Results(items=[_hit(r) for r in rows], total=total, note=note)

    async def _window(self, form: dict, years: list[str], offset: int, limit: int):
        """`limit` rows from `offset` over the years in turn. The archive has no stable order across
        page sizes, so it is always asked for fixed pages of MAX_LIMIT and sliced here."""
        out, total, pos = [], 0, offset
        for y in years:
            f = {**form, **({"godina_pretraga": y} if y else {})}
            need = limit - len(out)
            start = (pos // MAX_LIMIT) * MAX_LIMIT
            d = await self._search(f, start, MAX_LIMIT)
            n = int(d.get("recordsFiltered") or 0)
            total += n
            if need > 0 and pos < n:
                rows = d["data"]
                if len(rows) - (pos - start) < need and start + MAX_LIMIT < n:
                    rows = rows + (await self._search(f, start + MAX_LIMIT, MAX_LIMIT))["data"]
                got = rows[pos - start:pos - start + need]
                out += got
                pos += len(got)
            pos = max(0, pos - n)
        return out, total

    async def _resolve(self, ident: str) -> str:
        """A case number -> the archive's iddok (exactly one match required)."""
        r = await self.search_caselaw("", limit=MAX_LIMIT, page=1, filters={"case_number": ident})
        want = _norm_case(ident)
        ids = [h.id for h in r.items if _norm_case(h.case_number) == want]
        if not ids:
            raise NotFound(f"No Constitutional Court case numbered {ident!r} in the archive.")
        if len(ids) > 1:
            raise BadRequest(f"{ident!r} matches several archive documents: {', '.join(ids)}. "
                             "Pass one of these ids.")
        return ids[0]

    async def get_decision(self, id):
        ident = _http.clean(id)
        if _CASE_RE.fullmatch(ident):
            ident = await self._resolve(ident)
        if not ident.isdigit():
            raise BadRequest("Give the archive's numeric document id (from search_caselaw, e.g. '24915') "
                             "or a full case number such as 'U-III br. 339/24'.")
        r = await _http.get(f"{BASE}/obrada_fajlovi.php", params={"iddok": ident})
        if r.status_code != 200:
            raise SourceError(_http.error("ustavnisud.me", "file list failed", r.status_code), r.status_code)
        try:
            d = r.json()
        except ValueError:
            raise SourceError(_http.error("ustavnisud.me", "file list: not JSON", r.status_code))
        if d.get("poruka") != "Uspjesno":
            raise SourceError(f"ustavnisud.me file list: {str(d.get('poruka'))[:200]}")
        files = d.get("linkovi") or []
        if not files:
            raise NotFound(f"The Constitutional Court archive has no document with id {ident}.")

        parts, meta, labels = [], {}, []
        for i, fl in enumerate(files, 1):
            m = re.search(r"href='\.?/?([^']+)'", fl.get("link") or "")
            if not m:
                continue
            link = f"{BASE}/{m.group(1)}"
            label = _s(fl.get("korisnicki_naziv"))
            if label == "Sve":
                label = _s(fl.get("naziv_fajla"))
            labels += [label, _s(fl.get("naziv_fajla"))]
            kind = _s(fl.get("tip"))
            fr = await _http.get(link)
            txt = _file_text(_s(fl.get("naziv_fajla")) or link, fr.content) if fr.status_code == 200 else ""
            meta[f"Datoteka {i}"] = f"{kind}: {label} ({link}, generated per request)"
            if len(files) > 1:
                parts.append(f"## {kind or 'Dokument'}: {label}")
            parts.append(txt or "(No text: scanned PDF or unreadable file; open the file link above.)")
        text = "\n\n".join(parts)

        row = _rows.get(ident)
        if row is None:   # cold call: no earlier search filled the cache; find the row by a number/year in the file labels
            row, failed = {}, False
            tried: list[str] = []
            for m in re.finditer(r"(?<![\d/-])(\d{1,4})\s*[-/]\s*(\d{4}|\d{2})(?!\d)", " ".join(labels)):
                num = f"{m[1]}/{m[2]}"
                if num in tried or len(tried) >= 3:
                    continue
                tried.append(num)
                for q, narrow in ((num, True), (f"{m[1]} /{m[2]}", True), (f"{m[1]} /{m[2]}", False)):
                    # old numbers are stored with a space ("U.br. 40 /05"); the year filter is the registry year,
                    # which can differ from the number's year (case 68/04 registered 2005), so also try without it
                    form = {"djelovodni_broj": q}
                    if narrow and len(m[2]) == 2:   # "6/19" is a substring of "16/19", "26/19", ...
                        form["godina_pretraga"] = f"20{m[2]}" if int(m[2]) < 50 else f"19{m[2]}"
                    try:
                        for start in range(0, 4 * MAX_LIMIT, MAX_LIMIT):   # at most 4 pages
                            d = await self._search(form, start, MAX_LIMIT)
                            if _rows.get(ident) or start + MAX_LIMIT >= int(d.get("recordsFiltered") or 0):
                                break
                    except SourceError:
                        failed = True
                        break
                    row = _rows.get(ident) or {}   # exact iddok match only
                    if row:
                        break
                if row or failed:
                    break
            if not row:
                meta["Napomena"] = ("Metapodaci predmeta (vrsta postupka, datum upisa, podnosilac, osporeni akt) "
                                    "nisu učitani: " + ("pretraga arhive nije uspjela."
                                                        if failed else "red u arhivi nije pronađen."))
        if not any(len(p) > 200 for p in parts) and _s(row.get("sadrzaj_fajlova")):
            text += ("\n\n## Tekst iz indeksa arhive (slova sa dijakritikom izostavljena, skraćeno)\n\n"
                     + _s(row.get("sadrzaj_fajlova")))
        case_no = _s(row.get("djelovodni_broj"))
        if not case_no:
            m = _CASE_RE.search(text[:2000])
            case_no = re.sub(r"\s+", " ", m.group(0)) if m else ""
        if not case_no:   # file labels write the number as "Už-III br. 305-14"
            m = re.search(r"\b(U[žz]?-[IVX]+|U)\s*br\.?\s*(\d+)-(\d{2,4})\b", " ".join(labels))
            case_no = f"{m[1]} br. {m[2]}/{m[3]}" if m else ""
        dm = _DATE_RE.search(text[:3000])
        date = ""
        if dm:
            try:
                date = f"{int(dm[3]):04d}-{_MONTHS[dm[2].lower()]:02d}-{int(dm[1]):02d}"
            except (KeyError, ValueError):
                date = ""
        for k, v in (("Vrsta postupka", _s(row.get("vrsta_dokumenta"))),
                     ("Datum upisa predmeta", _http.iso_date(row.get("datum"))),
                     ("Podnosilac", _s(row.get("komitent"))),
                     ("Osporeni akt", _s(row.get("osporeni_akt"))),
                     ("Ključne riječi", _s(row.get("kljucne_rijeci_tagovi")).strip(" ,")),
                     ("Član Ustava", _s(row.get("clan_ustava_cg_atr19"))),
                     ("Član Konvencije", _s(row.get("clan_konvencije_atr20")))):
            if v:
                meta[k] = v
        link = f"{BASE}/obrada_fajlovi.php?iddok={ident}"
        meta["Citiranje"] = (f"Arhiva nema posebnu stranicu odluke. Veza po id-u {link} je stalna, ali vraća "
                             f"popis datoteka (JSON) sa svježom vezom do dokumenta; citirati broj predmeta "
                             f"{case_no or ident} i id dokumenta u arhivi ({ident}), arhiva: {ARCHIVE}")
        return Decision(id=ident, title=_title(case_no), text=text, url=link, court=COURT,
                        date=date, case_number=case_no, metadata=meta)
