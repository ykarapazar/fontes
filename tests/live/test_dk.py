"""Live smoke tests against Retsinformation (www.retsinformation.dk). Needs network; 1 s spacing."""
from world_legal_mcp import server


async def test_dk_search_in_force_and_historical():
    cur = await server.search_legislation("dk", "straffeloven", limit=5)
    assert 'get_legislation_toc("dk", "lta/' in cur and "historisk" not in cur
    old = await server.search_legislation("dk", "straffeloven", limit=5, filters={"historical": "true"})
    assert "historisk" in old
    bad = await server.search_legislation("dk", "straffeloven", filters={"historical": "maybe"})
    assert bad.startswith("Bad request (dk)")


async def test_dk_provision_label_and_id_variants():
    a = await server.get_legislation_provision("dk", "lta/2016/193", "§ 36")
    b = await server.get_legislation_provision("dk", "https://www.retsinformation.dk/eli/lta/2016/193", "36")
    assert a == b and "§ 36." in a and "urimeligt" in a
    c = await server.get_legislation_provision("dk", "lta/2016/193", "9a")
    assert "§ 9 a" in c


async def test_dk_later_amendments_flagged():
    out = await server.get_legislation_provision("dk", "lta/2016/193", "§ 1")
    assert "later amending act(s) are not yet worked into" in out


async def test_dk_old_law_html_fallback():
    out = await server.get_legislation_provision("dk", "lta/1953/169", "§ 3")
    assert "Grundlov" in out and "Den dømmende magt er hos domstolene" in out
