"""Live smoke tests against the DIFC Courts site (www.difccourts.ae). Needs network; 1 s per request."""
import re

from world_legal_mcp import server
import pytest

from world_legal_mcp.base import permitted_codes

needs_permission = pytest.mark.skipif("difc" not in permitted_codes(),
                                      reason="source needs permission: set WLM_PERMITTED=difc")
pytestmark = needs_permission

SLUG = "court-appeal/al-buhaira-national-insurance-company-v-arab-war-risks-insurance-syndicate-2026-difc-ca-003"


async def test_difc_court_and_year_filters():
    out = await server.search_caselaw("difc", "insurance", limit=5,
                                      filters={"court": "ca", "year": "2024"})
    assert "DIFC Court of Appeal" in out, out
    dates = re.findall(r"- Date: (\d{4})", out)
    assert dates and set(dates) == {"2024"}, out
    bad = await server.search_caselaw("difc", "x", filters={"court": "supreme"})
    assert bad.startswith("Bad request (difc)") and "supreme" in bad


async def test_difc_citation_and_url_resolve_to_judgment():
    for ident in ("[2026] DIFC CA 003",
                  "https://www.difccourts.ae/rules-decisions/judgments-orders/" + SLUG):
        out = await server.get_decision("difc", ident, max_chars=3000)
        assert SLUG in out and "Al Buhaira" in out, out[:800]
        assert "CA 003/2026" in out and "Resolved from" in out


async def test_difc_full_text_keyword_and_bad_ids():
    out = await server.search_caselaw("difc", "insurable interest would be hypothetical", limit=3)
    assert SLUG in out, out
    assert "No decisions on this page" in await server.search_caselaw("difc", "zzqxjvwk")
    missing = await server.get_decision("difc", "court-appeal/no-such-case-xyz")
    assert missing.startswith("Not found (difc)"), missing
    bad = await server.get_decision("difc", "not an id")
    assert bad.startswith("Bad request (difc)")
