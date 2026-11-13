"""Live smoke tests against govinfo and uscode.house.gov. Needs network.

Only test_us_search_caselaw_supreme_court spends a govinfo search request (the DEMO_KEY
fallback allows ~10/day); the rest use keyless endpoints. get_decision needs pypdf.
"""
import os

import pytest

from world_legal_mcp import server


async def test_us_decision_by_us_reports_citation():
    pytest.importorskip("pypdf")
    out = await server.get_decision("us", "347 U.S. 483", max_chars=3000)
    assert "Brown v. Board of Education" in out and "USREPORTS-347-483" in out
    assert "1954-05-17" in out and "## Text" in out


async def test_us_search_caselaw_supreme_court():
    out = await server.search_caselaw("us", "separate but equal", limit=3,
                                      filters={"collection": "USREPORTS"})
    if "rate limit reached" in out and not os.environ.get("WLM_US_GOVINFO_KEY"):
        pytest.skip("govinfo DEMO_KEY quota used up (~10/day); set WLM_US_GOVINFO_KEY")
    assert "USREPORTS-" in out and 'get_decision("us"' in out
    assert "USCOURTS-" not in out


async def test_us_provision_label_variants():
    for law, prov in (("42 U.S.C.", "§ 1983"), ("title 42", "sec. 1983"),
                      ("42 USC 1983", "42 U.S.C. 1983")):
        out = await server.get_legislation_provision("us", law, prov)
        assert "Civil action for deprivation of rights" in out, (law, prov)
    out = await server.get_legislation_provision("us", "42 USC", "1320a–7b")
    assert "Criminal penalties" in out


async def test_us_citation_search_and_title_toc():
    out = await server.search_legislation("us", "42 U.S.C. § 1983")
    assert "42 USC 1983" in out and "uscode.house.gov/us/usc/t42/s1983/" in out
    out = await server.get_legislation_toc("us", "42 USC", keyword="deprivation of rights")
    assert 'provision "1983"' in out


async def test_us_supreme_court_recent_terms():
    """Opinions after the last govinfo volume (586) come from supremecourt.gov term lists."""
    pytest.importorskip("pypdf")
    out = await server.get_decision("us", "24-809", max_chars=3000)
    if "Access Denied" in out or "403" in out[:300]:
        pytest.skip("supremecourt.gov Akamai edge refused the request (random 403)")
    assert "Goldey v. Fields" in out and "606 U.S. 942" in out and "2025-06-30" in out
    out = await server.search_caselaw("us", "Goldey Fields", filters={"collection": "SUPREMECOURT"})
    assert "606 U.S. 942" in out


async def test_us_constitution():
    out = await server.search_legislation("us", "constitution")
    assert "US Constitution" in out
    out = await server.get_legislation_provision("us", "US Constitution", "amendment 14")
    assert "equal protection of the laws" in out
    out = await server.get_legislation_provision("us", "U.S. Const.", "art. I sec. 8")
    assert "To regulate Commerce with foreign Nations" in out


async def test_us_statutes_at_large_by_citation():
    """Any page inside an act resolves to its granule; provisions are Stat. pages. Keyless."""
    pytest.importorskip("pypdf")
    out = await server.search_legislation("us", "1 Stat. 51")
    assert "STATUTE-1-Pg50" in out and "Territory Northwest of the river Ohio" in out
    assert "1789-08-07" in out
    out = await server.get_legislation_provision("us", "1 Stat. 50", "p. 51")
    assert "[[Page 1 Stat. 51]]" in out
    out = await server.get_legislation_text("us", "Pub. L. 85-1", max_chars=2000)
    assert "STATUTE-71-Pg3" in out and "Inauguration Day" in out


async def test_us_public_law_sections():
    """104th Congress on: PLAW text, provisions are sections. Keyless."""
    out = await server.search_legislation("us", "Public Law 119-1")
    assert "Laken Riley Act" in out and "Pub. L. 119-1" in out
    out = await server.get_legislation_provision("us", "PL 119-1", "sec. 2")
    assert "DETENTION OF CERTAIN ALIENS WHO COMMIT THEFT" in out
    out = await server.get_legislation_toc("us", "Pub. L. 119-1")
    assert 'provision "3"' in out
