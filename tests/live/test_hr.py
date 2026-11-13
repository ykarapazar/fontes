"""Live smoke tests against narodne-novine.nn.hr. Needs network."""
from world_legal_mcp import server


async def test_hr_search_legislation_titles_and_bad_filter():
    out = await server.search_legislation("hr", "Zakon o obveznim odnosima", limit=3)
    assert "Croatia (hr)" in out and 'get_legislation_toc("hr", "2005/35/707")' in out
    bad = await server.search_legislation("hr", "zakon", filters={"sort": "abc"})
    assert bad.startswith("Bad request (hr)")


async def test_hr_id_and_provision_label_variants():
    for law, label in (("2005/35/707", "Članak 8."), ("NN 35/2005 (707)", "8"),
                       ("https://narodne-novine.nn.hr/clanci/sluzbeni/2005_03_35_707.html", "čl. 8"),
                       ("eli/sluzbeni/2005/35/707", "art. 8")):
        out = await server.get_legislation_provision("hr", law, label)
        assert out.startswith("# Zakon o obveznim odnosima: Članak 8."), (law, label, out[:200])
        assert "Svatko je dužan uzdržati se" in out


async def test_hr_constitutional_court_decision():
    out = await server.search_caselaw("hr", "najmoprimac", limit=3)
    assert "Ustavni sud Republike Hrvatske" in out
    d = await server.get_decision("hr", "2024/95/1740", max_chars=5000)
    assert "U-III-5117/2022" in d and "Ustavna tužba se usvaja" in d


async def test_hr_not_found():
    out = await server.get_legislation_text("hr", "2005/35/99999")
    assert out.startswith("Not found (hr)"), out[:200]
