"""Live smoke tests against the EFTA Court API (api.eftacourt.int + eftacourt.int PDFs). 1 s per request."""
import re

from world_legal_mcp import server


async def test_efta_filters_country_type_date():
    out = await server.search_caselaw("efta", "", limit=5, filters={
        "country": "Iceland", "type": "advisory", "date_from": "2020-01-01", "sort": "date"})
    assert "c-wp-" in out, out
    years = re.findall(r"- Date: (\d{4})", out)
    assert years and all(int(y) >= 2020 for y in years)
    bad = await server.search_caselaw("efta", "x", filters={"type": "appeal"})
    assert "Bad request" in bad


async def test_efta_case_number_lookup_and_joined_cases():
    out = await server.search_caselaw("efta", "E-31/24", limit=5)
    assert "c-wp-10257" in out and "Joined Cases E-31/24 and E-32/24" in out, out
    # The component case has no judgment of its own; the joined judgment is returned.
    d = await server.get_decision("efta", "E-31/24", max_chars=3000)
    assert "JUDGMENT OF THE COURT" in d and "Joined Cases E-31/24 and E-32/24" in d, d[:800]
    assert "Resolved from" in d


async def test_efta_document_id_and_qualified_ref():
    no = await server.get_decision("efta", "dc-10023-5", max_chars=2000)   # E-25/24 judgment, Norwegian
    assert "EFTA-DOMSTOLENS DOM" in no, no[:500]
    costs = await server.get_decision("efta", "E-9/04 COSTS", max_chars=2000)
    assert "ORDER OF THE COURT" in costs and "Taxation of costs" in costs, costs[:500]
    bad = await server.get_decision("efta", "not an id")
    assert "c-wp-10023" in bad
