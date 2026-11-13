"""Live smoke tests against the ICSID case database (icsid.worldbank.org). Needs network; 1 s per request."""
import re

from world_legal_mcp import server


async def test_icsid_filters_and_case_number_search():
    out = await server.search_caselaw("icsid", "Philip Morris", limit=10, filters={
        "respondent": "Uruguay", "status": "concluded", "type": "ARB",
        "date_from": "2010-01-01", "date_to": "2010-12-31"})
    assert "ARB/10/7" in out and "ARB/21/3" not in out, out
    exact = await server.search_caselaw("icsid", "ICSID Case No. arb/10/7", limit=5)
    assert "ARB/10/7" in exact and len(re.findall(r"ARB/\d+/\d+", exact)) >= 1
    bad = await server.search_caselaw("icsid", "x", filters={"status": "open"})
    assert "pending or concluded" in bad


async def test_icsid_case_record_lists_documents():
    out = await server.get_decision("icsid", "ARB/10/7", max_chars=20000)
    assert "Philip Morris" in out and "Oriental Republic of Uruguay" in out
    assert "ARB/10/7#DC9012_En" in out          # Award of the Tribunal, July 8, 2016
    assert "Procedural details" in out


async def test_icsid_award_text_from_pdf():
    out = await server.get_decision("icsid", "ARB/10/7#DC9012_En", max_chars=3000)
    assert "2016-07-08" in out and "icsidfiles.worldbank.org" in out, out[:800]
    missing = await server.get_decision("icsid", "ARB/10/7#DC0000_En")
    assert "DC9012_En" in missing          # NotFound lists what is available
    unknown = await server.get_decision("icsid", "ARB/99/999")
    assert "no case" in unknown.lower()
