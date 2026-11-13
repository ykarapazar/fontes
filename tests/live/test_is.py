"""Live smoke tests against island.is court rulings (GraphQL at island.is/api/graphql).
Needs network. Throttled to one request per second."""
from world_legal_mcp import server

FOSS = "s-AC188192-B55F-45E0-8476-55C7EDD3EDE5"     # Hæstiréttur 33/2023, Fosshótel v Íþaka
LR = "g-7008b376-b90d-4756-afb0-cfe53085b078"       # Landsréttur 716/2025, Súðavíkurhreppur


async def test_is_court_filter_and_bad_filter():
    out = await server.search_caselaw("is", "leigusamningur", limit=5, filters={"court": "supreme"})
    assert "Hæstiréttur" in out and "Landsréttur" not in out and 'get_decision("is", "s-' in out
    out = await server.search_caselaw("is", "", limit=3, filters={"court": "hd-reykjavik",
                                                                  "date_from": "2020-01-01",
                                                                  "date_to": "2020-12-31"})
    assert "Héraðsdómur Reykjavíkur" in out and "2020-" in out
    bad = await server.search_caselaw("is", "leigusamningur", filters={"court": "mars"})
    assert bad.startswith("Bad request (is)")


async def test_is_supreme_court_rich_text_and_url_id():
    a = await server.get_decision("is", FOSS)
    b = await server.get_decision("is", f"https://island.is/domar/{FOSS.lower()}")
    assert a == b and "Dómur Hæstaréttar" in a and "force majeure" in a.lower()


async def test_is_pdf_decision_text():
    out = await server.get_decision("is", LR)
    assert "Landsréttur" in out and "716/2025" in out
    assert "Hestfjarðaralmenning" in out and "offset=60000" in out
    tail = await server.get_decision("is", LR, offset=60000)
    assert "D ó m s o r ð" in tail and "958.500 krónur" in tail


async def test_is_unknown_id():
    out = await server.get_decision("is", "g-00000000-0000-0000-0000-000000000000")
    assert "not found" in out.lower() or "no island.is verdict" in out.lower()
