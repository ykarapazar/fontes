"""Live smoke tests against the LawPhil Project (lawphil.net, non-official). Needs network."""
from world_legal_mcp import server


async def test_ph_caselaw_year_month_filter_and_url_id():
    out = await server.search_caselaw("ph", "", limit=3, filters={"year": "1950", "month": "3"})
    assert 'get_decision("ph", "juri1950/mar1950/' in out and "1950-03" in out, out
    out = await server.get_decision("ph", "https://lawphil.net/judjuris/juri2023/mar2023/gr_171746-48_2023.html",
                                    max_chars=3000)
    assert "CIRIACO" in out and "2023-03-29" in out and "Non-official" in out
    assert "LawPhil decision id" in await server.get_decision("ph", "G.R. No. 171746")


async def test_ph_statute_number_query_and_type_filter():
    out = await server.search_legislation("ph", "Republic Act No. 386", limit=5)
    assert '"ra_386_1949"' in out and "ra_10386" not in out, out
    out = await server.search_legislation("ph", "Labor Code", limit=5, filters={"type": "pd"})
    assert "Presidential Decree" in out, out
    assert "type must be one of" in await server.search_legislation("ph", "x", filters={"type": "law"})


async def test_ph_provision_label_variants():
    for label in ("Article 2", "Art. 2", "2"):
        out = await server.get_legislation_provision("ph", "ra_386_1949", label)
        assert "fifteen days following the completion of their publication" in out, (label, out)
    out = await server.get_legislation_provision("ph", "cons1987", "Article III, Section 1")
    assert "due process of law" in out, out
