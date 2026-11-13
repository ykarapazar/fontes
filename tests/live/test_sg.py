"""Live smoke tests against elitigation.sg/gd. Needs network."""
import re

import pytest

from world_legal_mcp import server
from world_legal_mcp.base import permitted_codes

pytestmark = pytest.mark.skipif("sg" not in permitted_codes(),
                                reason="source needs permission: set WLM_PERMITTED=sg")


async def test_sg_search_year_filter():
    out = await server.search_caselaw("sg", "negligence", limit=3, filters={"year": "2020"})
    assert "Singapore (sg) case law" in out
    ids = re.findall(r'get_decision\("sg", "(\d{4})_SG[A-Z]+_\d+"\)', out)
    assert ids
    bad = await server.search_caselaw("sg", "negligence", filters={"year": "20x0"})
    assert bad.startswith("Bad request (sg)")


async def test_sg_citation_variants_and_summary():
    a = await server.get_decision("sg", "[2024] SGCA 1", max_chars=3000)
    b = await server.get_decision("sg", "2024_SGCA_1", max_chars=3000)
    assert a == b
    assert a.startswith("# WKM v WKN")
    assert "2024-02-07" in a and "Court of Appeal" in a


async def test_sg_bracketed_court_and_not_found():
    out = await server.get_decision("sg", "[2026] SGHC(I) 25", max_chars=2000)
    assert "Terraform Labs" in out and "Singapore International Commercial Court" in out
    missing = await server.get_decision("sg", "[2024] SGCA 9999")
    assert missing.startswith("Not found (sg)")
