"""Live smoke tests against e-qanun.az (Ministry of Justice legal-acts database)."""
import re

import pytest

from world_legal_mcp import server
from world_legal_mcp.base import permitted_codes

pytestmark = pytest.mark.skipif("az" not in permitted_codes(),
                                reason="source needs permission: set WLM_PERMITTED=az")


async def test_az_court_filter():
    out = await server.search_caselaw("az", "", limit=3, filters={"court": "constitutional"})
    ids = re.findall(r'get_decision\("az", "(\d+)"\)', out)
    assert ids, out
    dec = await server.get_decision("az", ids[0], max_chars=3000)
    assert "Konstitusiya Məhkəməsi" in dec
    bad = await server.search_caselaw("az", "x", filters={"court": "district"})
    assert "Bad request" in bad


async def test_az_legislation_type_filter():
    out = await server.search_legislation("az", "Mülki Məcəllə", limit=5,
                                          filters={"type": "code", "status": "in_force"})
    assert 'get_legislation_toc("az", "46944")' in out


async def test_az_provision_label_variants():
    for label in ("Maddə 1", "1", "art. 1", "maddə 1."):
        out = await server.get_legislation_provision("az", "46944", label)
        assert "Maddə 1." in out and "Mülki Məcəllə" in out, label
    out = await server.get_legislation_provision("az", "46944", "90-1")
    assert "Maddə 90-1" in out


async def test_az_constitution_and_bad_id():
    out = await server.get_legislation_provision("az", "https://e-qanun.az/framework/897", "Maddə 2")
    assert "Xalqın suverenliyi" in out
    bad = await server.get_legislation_toc("az", "civil-code")
    assert "Bad request" in bad
