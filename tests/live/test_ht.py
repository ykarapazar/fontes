"""Live smoke tests against the CSPJ document library (cspj.ht). Needs network. 1 s spacing."""
from world_legal_mcp import server


async def test_ht_search_accent_insensitive_with_moniteur_date():
    out = await server.search_legislation("ht", "prevention repression corruption", limit=5)
    assert "1396" in out and "2014-05-09" in out and "Le Moniteur NO.87" in out, out


async def test_ht_provision_label_variants():
    a = await server.get_legislation_provision("ht", "1396", "Article 5.1")
    b = await server.get_legislation_provision("ht", "1396", "art. 5.1")
    assert "De la concussion" in a and a == b, a


async def test_ht_repeated_article_numbers_get_suffix():
    # The 'loi sur les étrangers' file bundles several acts, each starting at Article 1er.
    out = await server.get_legislation_provision("ht", "1406", "Article 1er (2)")
    assert "loi du 13 Mai 1935" in out, out


async def test_ht_scan_and_bad_id():
    scan = await server.get_legislation_text("ht", "1402")
    assert "no text layer" in scan and "cspj.ht/wp-content/uploads" in scan, scan
    assert "Bad request" in await server.get_legislation_toc("ht", "abc")


async def test_ht_constitution_1987_from_court_site():
    out = await server.search_legislation("ht", "constitution", limit=5)
    assert "constitution-1987" in out, out
    art = await server.get_legislation_provision("ht", "constitution-1987", "Article 1er")
    assert "Haïti" in art or "Haiti" in art, art
