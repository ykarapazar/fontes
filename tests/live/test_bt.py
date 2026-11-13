"""Live smoke tests against the Depository of Laws (www.legislation.gov.bt/api). Needs network;
1 s spacing per request."""
from world_legal_mcp import server


async def test_bt_constitution_articles():
    out = await server.get_legislation_provision("bt", "79", "art. 7")
    assert out and "Article 7 – Fundamental Rights" in out and "freedom of speech" in out
    same = await server.get_legislation_provision(
        "bt", "https://legislation.gov.bt/legislations/view/79", "Article 7")
    assert same == out


async def test_bt_penal_code_section_variants():
    a = await server.get_legislation_provision("bt", "111", "3")
    b = await server.get_legislation_provision("bt", "111", "Section 3")
    assert a == b and "Classes of crime" in a and "felony" in a
    dup = await server.get_legislation_provision("bt", "111", "Section 265 (2)")
    assert "unauthorized hearing" in dup  # the source numbers two sections 265


async def test_bt_status_filter_and_bad_input():
    out = await server.search_legislation("bt", "narcotic", limit=5, filters={"status": "repealed"})
    assert 'get_legislation_toc("bt", "141")' in out and "Status: repealed" in out, out
    assert "Act of Bhutan 2015" not in out  # the 2015 Act is in force, filtered out
    bad = await server.search_legislation("bt", "act", filters={"status": "maybe"})
    assert bad.startswith("Bad request (bt)")
    assert "Bad request" in await server.get_legislation_toc("bt", "../etc")
    assert "No Act" in await server.get_legislation_toc("bt", "999999")
