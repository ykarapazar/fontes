import pytest

from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions import sr

OCR = """Artikel I
1. Voor de toepassing van deze wet wordt verstaan onder:
a. Minister: de minister.
Artikel2
1. Onderscheid is verboden.
Artikel3
Tekst drie.
Artikel S
Tekst acht.
Artikel l0
Tekst tien.
Artikel 13
Tekst dertien.
"""


def test_ocr_headings_split():
    _, sections = sr._split(OCR)
    assert set(sections) == {"1", "2", "3", "8", "10", "13"}
    assert "Onderscheid is verboden" in sections["2"]
    assert "Voor de toepassing" in sections["1"]


def test_roman_headings_not_remapped():
    assert sr._ocr_head("Artikel II") == "Artikel II"
    assert sr._ocr_head("Artikel I") == "Artikel 1"


def test_site_date():
    assert sr._site_date("2022", False) == "01/01/2022"
    assert sr._site_date("2022", True) == "31/12/2022"
    assert sr._site_date("2024-02", True) == "29/02/2024"
    assert sr._site_date("2022-03-16", False) == "16/03/2022"
    with pytest.raises(BadRequest):
        sr._site_date("last year", False)


def test_date_filters_declared():
    assert {"since", "until"} <= set(sr.Suriname.caselaw_filters)


def test_ocr_poor_detection():
    bad = ("a. Mnister: de ministerbelast met de plaa* waar personen onder het ge\"ag volgen, "
           "de werlaremer in artikel l6I3a, afl<omst en raq sekse, valrvereniging. ") * 3
    assert sr._ocr_poor(bad)
    assert not sr._ocr_poor("Artikel 1\n1. Voor de toepassing van deze wet wordt verstaan onder: de minister. " * 20)


def _sr_hits(nums):
    return "".join(f'<h5 class="sru-number"><a href="https://rechtspraak.sr/sru-hvj-2020-{n}/">SRU-HvJ-2020-{n}</a></h5>'
                   f'<div class="sru-list"><ul></ul></div>' for n in nums)


def test_caselaw_paging_fetches_and_slices(monkeypatch):
    import asyncio
    calls = []

    async def post(url, data):
        calls.append(data.get("paged", 1))
        if url == sr.SEARCH:
            return "Gevonden: 491 uitspraken" + '<div class="load_moredata">' + _sr_hits(range(1, 11))
        n = data["paged"]
        return _sr_hits(range((n - 1) * 10 + 1, n * 10 + 1))
    monkeypatch.setattr(sr, "_post", post)
    j = sr.Suriname()
    r = asyncio.run(j.search_caselaw("kort geding", limit=25, page=2))
    assert calls == [1, 3, 4, 5]             # form (total) + source pages 3..5 for hits 26-50
    assert [h.id for h in r.items] == [f"SRU-HvJ-2020-{n}" for n in range(26, 51)] and r.total == 491
    calls.clear()
    r = asyncio.run(j.search_caselaw("kort geding", limit=5, page=6))
    assert calls == [1, 3] and [h.id for h in r.items] == [f"SRU-HvJ-2020-{n}" for n in range(26, 31)]
