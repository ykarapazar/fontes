"""Live checks for the UN Treaty Collection adapter (hits treaties.un.org)."""

from world_legal_mcp import server



async def test_search_by_chapter():
    out = await server.search_legislation("untc", "law of the sea", limit=10, filters={"chapter": "XXI"})
    assert "XXI-6" in out and "Montego Bay" in out
    out = await server.search_legislation("untc", "xxi-6-a", limit=3)
    assert "Agreement relating to the implementation of Part XI" in out


async def test_status_sections():
    out = await server.get_legislation_provision("untc", "XXI-6", "parties")
    assert "Parties" in out and "| Participant" in out
    out = await server.get_legislation_provision("untc", "XXI-1", "reservations")
    assert "Declarations and Reservations" in out


async def test_article_from_ctc():
    toc = await server.get_legislation_toc("untc", "XXI-6", keyword="territorial")
    assert 'provision "Article 3"' in toc
    out = await server.get_legislation_provision("untc", "XXI-6", "art. 3")
    assert "12 nautical miles" in out


async def test_errors():
    assert (await server.get_legislation_toc("untc", "ZZ-1")).startswith("Bad request (untc)")
    assert (await server.get_legislation_toc("untc", "XXI-999")).startswith("Not found (untc)")
