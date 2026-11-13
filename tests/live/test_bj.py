"""Live smoke tests for Benin: Cour constitutionnelle (courconstitutionnelle.bj) and SGG laws
(sgg.gouv.bj). Needs network. Throttled to one request per second per host."""
from world_legal_mcp import server


async def test_bj_caselaw_number_and_type_year():
    out = await server.search_caselaw("bj", "DCC 18-62")
    assert "DCC18-062" in out and "2018-03-08" in out, out
    out = await server.search_caselaw("bj", "", limit=3, filters={"type": "EP", "year": "2021"})
    assert "EP21-" in out, out
    assert "Bad request" in await server.search_caselaw("bj", "x", filters={"type": "DCC"})


async def test_bj_decision_id_variant():
    out = await server.get_decision("bj", "dcc 20-1")
    assert "DCC20-001" in out and "2020-01-26" in out and "ADANDOGBESSI" in out, out[:800]
    assert "Page 1 sur" not in out


async def test_bj_law_id_and_provision_variants():
    a = await server.get_legislation_provision("bj", "Loi n° 98-004", "Article premier")
    b = await server.get_legislation_provision("bj", "98-004", "art. 1")
    assert "apprentis" in a and "apprentis" in b, a
    toc = await server.get_legislation_toc("bj", "loi-98-004")
    assert "TITRE" in toc and 'provision "3"' in toc, toc[:1500]


async def test_bj_law_search_type_filter():
    out = await server.search_legislation("bj", "", filters={"type": "decret", "from": "2026-01-01",
                                                             "to": "2026-03-31"})
    assert "decret-2026-" in out, out[:800]
