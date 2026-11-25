"""Live smoke tests against WTO dispute pages (www.wto.org). Needs network; 1 s per request."""
from world_legal_mcp import server


async def test_wto_filters_and_number_search():
    out = await server.search_caselaw("wto", "gasoline", limit=10, filters={
        "complainant": "Venezuela", "respondent": "USA", "adopted": "true",
        "date_from": "1995-01-01", "date_to": "1995-12-31"})
    assert "DS2" in out and "DS4:" not in out, out          # DS4 is Brazil's gasoline case
    exact = await server.search_caselaw("wto", "WT/DS600", limit=5)
    assert "DS600" in exact and "Palm Oil" in exact
    bad = await server.search_caselaw("wto", "x", filters={"adopted": "maybe"})
    assert "Bad request" in bad and "adopted" in bad


async def test_wto_decision_summary_and_metadata():
    out = await server.get_decision("wto", "ds600", max_chars=30000)
    assert "Malaysia" in out and "European Union" in out
    assert "Summary of key findings" in out and "ILUC" in out
    assert "1pagesum_e/ds600sum_e.pdf" in out and "docs.wto.org" in out
    assert "<p" not in out


async def test_wto_id_variants_and_unknown():
    out = await server.get_decision("wto", "2", max_chars=4000)
    assert "Gasoline" in out and "Venezuela" in out
    missing = await server.get_decision("wto", "DS9999")
    assert "Not found" in missing and "DS9999" in missing
    bad = await server.get_decision("wto", "ARB/10/7")
    assert "Bad request" in bad
