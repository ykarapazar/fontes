"""Live smoke tests: India's legislation through Lexifina's record, and the Indian Supreme Court Judgments
AWS Open Data bucket. Needs network."""
from world_legal_mcp import server

ITA = "india/national/acts/central/acts/information-technology-act-2000"


async def test_in_legislation_from_lexifina():
    out = await server.search_legislation("in", "Information Technology Act 2000", limit=5)
    assert "The Information Technology Act, 2000" in out and ITA in out and "courts" not in out
    out = await server.get_legislation_provision("in", ITA, "sec-001")
    assert "Short title" in out and "Lexifina" in out


async def test_in_sc_search_default_years_and_finds_by_party():
    out = await server.search_caselaw("in", "Kesavananda Bharati", limit=3)
    assert "No year given" in out and "S_1973_1_1_1002" not in out
    out = await server.search_caselaw("in", "Kesavananda Bharati", limit=3, filters={"year": "1973"})
    assert "KESAVANANDA BHARATI" in out and "S_1973_1_1_1002" in out


async def test_in_sc_id_variants():
    for cid in ("2024_10_108_125", "[2024] 10 S.C.R. 108", "2024 INSC 735"):
        out = await server.get_decision("in", cid)
        assert "Vijay Singh" in out and "2024-09-25" in out and "2024 INSC 735" in out, cid
    assert (await server.get_decision("in", "AIR 1973 SC 1461")).startswith("Bad request (in)")
