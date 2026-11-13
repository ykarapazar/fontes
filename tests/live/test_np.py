"""Live smoke tests against Nepal Kanoon Patrika (nkp.gov.np). Needs network.
Throttled to one request per 1.5 s."""
import re

from world_legal_mcp import server


async def test_np_bs_date_and_bench_filters():
    out = await server.search_caselaw("np", "बकसपत्र", limit=5, filters={
        "date_from": "2080-01-01", "date_to": "2080/12/30", "bench": "संयुक्त इजलास"})
    dates = re.findall(r"फैसला मिति \(वि\.सं\.\) (\d{4})-", out)
    assert dates and set(dates) == {"2080"}, out
    assert "सर्वोच्च अदालत, संयुक्त इजलास" in out
    bad = await server.search_caselaw("np", "बकसपत्र", filters={"date_from": "2023"})
    assert "Bikram Sambat" in bad


async def test_np_decision_number_filter_and_id_variants():
    out = await server.search_caselaw("np", "", limit=3, filters={"decision_number": "११५१२"})
    assert 'get_decision("np", "10608")' in out, out
    for did in ("10608", "नि.नं. ११५१२", "https://nkp.gov.np/full_detail/10608/?keywords=x"):
        d = await server.get_decision("np", did, max_chars=1500)
        assert "- Identifier: 10608" in d and "ने.का.प. २०८२, अङ्क १२, नि.नं. ११५१२" in d, did
        assert "फैसला मिति (वि.सं.): 2081-11-11" in d


async def test_np_case_number_and_not_found():
    d = await server.get_decision("np", "10605", max_chars=1500)
    assert "- Case number: ०७९-CI-०४४३" in d and "संयुक्त इजलास" in d
    assert "No NKP document" in await server.get_decision("np", "99999999")
    assert "Bad request" in await server.get_decision("np", "Basnet v Basnet")
