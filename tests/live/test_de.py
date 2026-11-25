"""Live smoke tests: NeuRIS (case law) and gesetze-im-internet.de (legislation). Needs network."""
from world_legal_mcp import server
import pytest

from world_legal_mcp.base import permitted_codes

needs_permission = pytest.mark.skipif("de" not in permitted_codes(),
                                      reason="source needs permission: set WLM_PERMITTED=de")


@needs_permission
async def test_de_court_filter_bverfg():
    out = await server.search_caselaw("de", "Menschenwürde", limit=3, filters={"court": "bverfg"})
    assert "BVerfG" in out and 'get_decision("de", "KVRE' in out


@needs_permission
async def test_de_decision_by_ecli_matches_doc_number():
    by_ecli = await server.get_decision("de", "ECLI:DE:BGH:2016:130416UVIIIZR198.15.0", max_chars=3000)
    by_id = await server.get_decision("de", "KORE303742016", max_chars=3000)
    assert by_ecli == by_id and "VIII ZR 198/15" in by_id
    assert "[1] Die Klägerin" in by_id  # Randnummern kept, no raw HTML


async def test_de_provision_label_variants():
    a = await server.get_legislation_provision("de", "bgb", "§ 823")
    b = await server.get_legislation_provision("de", "BGB", "823")
    assert a == b and "__823.html" in a
    gg = await server.get_legislation_provision("de", "gg", "Art. 1")
    assert gg == await server.get_legislation_provision("de", "gg", "1")
    assert "Würde des Menschen" in gg and "art_1.html" in gg


async def test_de_legislation_search_by_abbreviation():
    out = await server.search_legislation("de", "BGB", limit=3)
    assert "Bürgerliches Gesetzbuch" in out and '"bgb"' in out


@pytest.mark.skipif("de" in permitted_codes(), reason="BFH route is used only without WLM_PERMITTED=de")
async def test_de_bfh_route_without_permission():
    # One request (bundesfinanzhof.de robots Crawl-Delay 60).
    out = await server.search_caselaw("de", "Verständigungsvereinbarung", limit=3,
                                      filters={"court": "BFH", "date_from": "2025-01-01"})
    assert "I R 39/23" in out and "STRE202610201" in out and "2024-" not in out
    bad = await server.search_caselaw("de", "Mietminderung", filters={"court": "BGH"})
    assert bad.startswith("Bad request (de)") and "'BGH'" in bad
