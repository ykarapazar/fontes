"""Live smoke tests against the BOE open-data API (www.boe.es). Needs network; 1 s spacing."""
from world_legal_mcp import server


async def test_es_provision_label_variants():
    a = await server.get_legislation_provision("es", "BOE-A-1889-4763", "Artículo 1902")
    b = await server.get_legislation_provision("es", "BOE-A-1889-4763", "art. 1902")
    c = await server.get_legislation_provision("es", "BOE-A-1889-4763", "1902")
    assert a == b == c and "culpa o negligencia" in a
    assert "meramente informativo" in a  # BOE reuse terms


async def test_es_old_code_disposiciones_labels():
    toc = await server.get_legislation_toc("es", "BOE-A-1889-4763", keyword="transitoria")
    assert '"Disposición transitoria primera"' in toc
    p = await server.get_legislation_provision("es", "BOE-A-1889-4763", "Disposición transitoria primera")
    assert "legislación anterior al Código" in p


async def test_es_filters_scope_and_text_search():
    out = await server.search_legislation("es", "Enjuiciamiento Civil", limit=5,
                                          filters={"scope": "state", "in_force": "yes"})
    assert "BOE-A-2000-323" in out and "Autonómico" not in out
    txt = await server.search_legislation("es", "desahucio precario", limit=3,
                                          filters={"search_in": "text"})
    assert 'BOE-A-' in txt


async def test_es_bad_id_and_missing_provision():
    bad = await server.get_legislation_provision("es", "Codigo Civil", "1902")
    assert "BOE-A-1889-4763" in bad
    missing = await server.get_legislation_provision("es", "BOE-A-1889-4763", "Artículo 99999")
    assert "not found" in missing


async def test_es_tc_decision_id_variants():
    a = await server.get_decision("es", "STC 31/2010", max_chars=3000)
    b = await server.get_decision("es", "ECLI:ES:TC:2010:31", max_chars=3000)
    assert a == b and "ECLI:ES:TC:2010:31" in a and "Estatuto de Autonomía de Cataluña" in a
    auto = await server.get_decision("es", "ECLI:ES:TC:2010:31A", max_chars=2000)
    assert "AUTO 31/2010" in auto and "ECLI:ES:TC:2010:31A" in auto
    bad = await server.get_decision("es", "31-2010")
    assert "STC 31/2010" in bad  # the error says what a good id looks like


async def test_es_tc_search_filters():
    out = await server.search_caselaw("es", "Estatuto de Autonomía de Cataluña", limit=5,
                                      filters={"type": "sentencia", "date_from": "2010-06-01",
                                               "date_to": "2010-06-30"})
    assert "STC 31/2010" in out and "ATC " not in out
