"""Laos (Lao PDR): legislation *index* search (titles and metadata only) in the Official Gazette
of the Lao PDR (laoofficialgazette.gov.la), run by the Ministry of Justice.

How the source works (verified 2026-11-06, UK IP, honest User-Agent):
  * Yii PHP site. Global title search: GET /index.php?r=site/searchtip&s=<words>, a grid
    (#legals-grid) of 10 rows per page, paged with &Document_page=N, with a summary line
    "ສະແດງ 11-20 ຂອງ 402 ຜົນທີ່ໄດ້ຮັບ." ("showing 11-20 of 402 results"). A second grid
    (#legalsconsult-grid) lists drafts open for comment; it is ignored. The grid's
    Document[legal_type_id] / Document[agency_id] filters are ignored by searchtip.
  * Row columns: title, responsible agency, act date, date published in the Gazette, type,
    status ("ປັດຈຸບັນ" = current), link to /index.php?r=site/display&id=N, English PDF
    (empty in every row seen), Lao PDF in /kcfinder/upload/files/.
  * The id is the Gazette's own display id ("2468"); the url is that display page.
  * Lao has two spellings of the vowel sara am (precomposed "ຳ" and "ໍ" + "າ"); titles use
    both and the search matches bytes, so a query with no hits is retried once in the other form.

Why there is no text (get_legislation_*): the Gazette's own "About" page says the binding
texts are PDF images ("ສະບັບພີດີເອັບ (ເອກະສານ ທີ່ຢູ່ໃນຮູບແບບເປັນຮູບພາບ)"), and every PDF checked
(2 on the Gazette, 3 on na.gov.la) is a scan with no text layer. No OCR here. The host is also
slow: ~20 KB/s, a 1-2 MB PDF took 50-65 s.

Terms (About page, /index.php?r=site/display&id=12, section "ລິຂະສິດ" / Copyright): free access
for every kind of user; altering copied texts is a criminal offence; printing them as books needs
the Ministry of Justice's permission. Nothing on automated access. No robots.txt (the path
answers the home page as HTML).

Not used (2026-11-06):
  * moj.gov.la: robots.txt "Disallow: /" for all user agents.
  * na.gov.la (National Assembly): robots.txt allows all and /ນິຕິກຳ/ບັນດາກົດໝາຍ/ lists 186 law
    PDFs, but they are scans without a text layer, and the Gazette already indexes the same laws.
  * People's Supreme Court: spc.gov.la / www.spc.gov.la do not resolve; peoplecourt.gov.la timed
    out. No case law source found.
"""
from __future__ import annotations

import re
from urllib.parse import urlencode

from lxml import html as lhtml

from .. import _http
from ..base import BadRequest, Jurisdiction, Source, SourceError
from ..models import LawHit, Results

HOST = "www.laoofficialgazette.gov.la"
BASE = f"https://{HOST}"
SEARCH = BASE + "/index.php"
DISPLAY = BASE + "/index.php?r=site/display&id={id}"
TERMS = DISPLAY.format(id=12)
SOURCE = "Official Gazette of the Lao PDR"
PAGE_SIZE = 10                 # fixed by the source
MAX_LIMIT = 20                 # at most 2-3 source pages per call: the host is slow
_SUMMARY = re.compile(r"(\d+)\s*-\s*(\d+)\s*ຂອງ\s*(\d+)")
# The source searches Lao titles only (an English word matches stray words such as "Civil Aviation"
# or file names), so these common English names are searched by their Lao title.
_ENGLISH = {
    "constitution": "ລັດຖະທຳມະນູນ",
    "civil code": "ປະມວນກົດໝາຍແພ່ງ",
    "criminal code": "ປະມວນກົດໝາຍອາຍາ",
    "criminal law": "ອາຍາ",
    "criminal procedure": "ຄະດີອາຍາ",
    "land law": "ທີ່ດິນ",
    "labour law": "ແຮງງານ",
    "labor law": "ແຮງງານ",
    "labour": "ແຮງງານ",
    "labor": "ແຮງງານ",
    "employment": "ແຮງງານ",
}
NO_DATE_NOTE = ("Title index only; texts are scanned Lao PDFs (see the link in each hit). The Gazette "
                "has no date filter and hits cannot be narrowed by year; read the Date line of each hit.")


def _variant(q: str) -> str:
    """The other spelling of sara am: 'ຳ' <-> 'ໍາ'."""
    if "ຳ" in q:
        return q.replace("ຳ", "ໍາ")
    return q.replace("ໍາ", "ຳ")


async def _page(q: str, n: int) -> tuple[list[LawHit], int]:
    params = {"r": "site/searchtip", "s": q}
    if n > 1:
        params["Document_page"] = str(n)
    # The host now and then refuses a connection (ConnectError, 1 of 4 test runs on
    # 2026-11-10; the next request went through): one retry on a network error.
    try:
        r = await _http.get(SEARCH + "?" + urlencode(params))
    except Exception:  # network error
        r = await _http.get(SEARCH + "?" + urlencode(params))
    if r.status_code != 200:
        raise SourceError(_http.error(SOURCE, "search failed", r.status_code), r.status_code)
    doc = lhtml.fromstring(r.text)
    grid = doc.xpath('//div[@id="legals-grid"]')
    if not grid:
        raise SourceError(f"Error ({SOURCE}): search page changed (no results grid).", 200)
    grid = grid[0]
    summary = _http.clean(" ".join(grid.xpath('.//div[@class="summary"]//text()')))
    m = _SUMMARY.search(summary)
    total = int(m[3]) if m else 0
    hits = []
    for tr in grid.xpath('.//table[@class="items"]/tbody/tr'):
        tds = tr.xpath("./td")
        link = tr.xpath('.//a[contains(@href, "r=site/display")]/@href')
        idm = re.search(r"[?&]id=(\d+)", link[0]) if link else None
        if len(tds) < 6 or not idm:
            continue
        cell = [_http.clean(td.text_content()) for td in tds]
        pdf = tr.xpath('.//a[contains(@href, "/kcfinder/upload/files/")]/@href')
        good = [p for p in pdf if p.rsplit("/", 1)[-1].lower() != "null.pdf"]
        bits = [cell[1]]
        if cell[3]:
            bits.append(f"published in the Gazette {_http.iso_date(cell[3]) or cell[3]}")
        if good:
            bits.append("Lao PDF (scan): " + BASE + good[-1].replace(" ", "%20"))
        elif pdf:
            bits.append("the Gazette's PDF link for this record is broken (null.pdf); open the Source page")
        status = cell[5]
        if not cell[2] and not cell[4]:
            # The Gazette flags these "current" although they carry no date or type; showing that flag
            # next to the dated current entry made lawyers read two current Constitutions.
            status = ""
            bits.append("record has no date or type in the Gazette and its status is not shown "
                        "(the Gazette's own 'current' flag is unreliable for such records); "
                        "cite the hit of the same title that has a Date line, if any")
        hits.append(LawHit(id=idm[1], title=cell[0], type=cell[4], date=_http.iso_date(cell[2]),
                           status=status, snippet="; ".join(b for b in bits if b),
                           url=DISPLAY.format(id=idm[1])))
    return hits, total


class Laos(Jurisdiction):
    code = "la"
    name = "Laos"
    languages = ("lo",)
    aliases = ("laos", "lao pdr", "lao", "lao people's democratic republic")
    sources = (
        Source(
            name="Official Gazette of the Lao PDR (Ministry of Justice): search index",
            url=BASE + "/",
            covers=("legislation",),
            licence="free access for all users; altering copied texts is a criminal offence; "
                    "republishing as books needs Ministry of Justice permission",
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit="unknown; 1 s spacing, no 429 seen in ~15 requests (2026-11); host is slow "
                       "(~20 KB/s) and drops some TLS connections",
            terms_url=TERMS,
            warning=("Titles and metadata only: the Gazette's texts are scanned Lao PDFs (no text "
                     "layer); open the PDF. Copied texts must not be altered; printing them as books "
                     "needs Ministry of Justice permission."),
        ),
    )
    min_interval = {HOST: 1.0}
    notes = ("Legislation index only: title search over the Official Gazette (laws, decrees, "
             "decisions, ~2,600 acts, Lao), with links to the scanned PDFs. No text, no case law.")
    gaps = (
        "Full text of all legislation: scans only, no text (Gazette PDFs are images; no OCR); titles and metadata only",
        "Case law (People's Supreme Court): site down / unreachable (spc.gov.la does not resolve, peoplecourt.gov.la timed out, 2026-11-06)",
        "English versions: not published online (English PDF column empty in every row seen)",
    )
    samples = {"legislation_query": "ກົດໝາຍວ່າດ້ວຍ ສະພາແຫ່ງຊາດ"}

    async def search_legislation(self, query, *, limit, page, filters):
        q = _http.clean(query)[:100]
        q = _ENGLISH.get(q.lower(), q)
        if not q:
            raise BadRequest("Give words from the title, in Lao, e.g. 'ກົດໝາຍວ່າດ້ວຍ ແຮງງານ'.")
        limit = max(1, int(limit))
        if limit > MAX_LIMIT:
            raise BadRequest(f"limit must be at most {MAX_LIMIT} for this source (the host is slow); use page to walk further.")
        start = (max(1, int(page)) - 1) * limit
        first = start // PAGE_SIZE + 1
        hits, total = await _page(q, first)
        if not total and _variant(q) != q:
            q = _variant(q)
            hits, total = await _page(q, first)
        if start >= total:
            return Results(items=[], total=total,
                           note=NO_DATE_NOTE)
        last = (start + limit - 1) // PAGE_SIZE + 1
        for n in range(first + 1, last + 1):
            if (n - 1) * PAGE_SIZE >= total:
                break
            more, _ = await _page(q, n)
            hits += more
        off = start - (first - 1) * PAGE_SIZE
        return Results(items=hits[off:off + limit], total=total,
                       note=NO_DATE_NOTE)
