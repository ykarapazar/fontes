"""Live smoke tests against Riigi Teataja. Needs network."""
import pytest

from world_legal_mcp import server
from world_legal_mcp.base import SourceError
from world_legal_mcp.jurisdictions import ee

VOS = "120062026018"  # Võlaõigusseadus, wording valid 2026-09-01..2026-12-31


async def test_ee_search_full_text_links_translation():
    out = await server.search_legislation("ee", "üürileping", limit=3,
                                          filters={"in_text": "true"})
    assert "Estonia (ee) legislation" in out and "riigiteataja.ee/akt/" in out
    assert "§ " in out  # full-text hits carry the matching § as snippet


async def test_ee_superscript_provision_variants():
    for label in ("§ 11¹", "11^1", "11.1", "para11b1"):
        out = await server.get_legislation_provision("ee", VOS, label)
        assert ": § 11¹" in out and "Püsiv andmekandja" in out


async def test_ee_repealed_section_and_url_id():
    out = await server.get_legislation_provision("ee", f"https://www.riigiteataja.ee/akt/{VOS}", "34")
    assert "Kehtetu" in out and "RT I, 31.12.2013, 1" in out


async def test_ee_robots_listed_act_is_refused():
    with pytest.raises(SourceError, match="robots.txt"):
        await ee._law("13310465")
