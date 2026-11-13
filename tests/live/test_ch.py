"""Live smoke tests against Fedlex (SPARQL + www.fedlex.admin.ch filestore) and search.bger.ch.
Needs network; 1-2 s spacing per request."""
from world_legal_mcp import server


async def test_ch_provision_label_variants():
    a = await server.get_legislation_provision("ch", "210", "Art. 1")
    b = await server.get_legislation_provision("ch", "SR 210", "1")
    assert a == b and "Art. 1" in a
    assert "Dies ist keine amtliche Veröffentlichung" in a  # Art. 49 PublV notice
    dsg = await server.get_legislation_provision("ch", "235.1", "art. 5")
    assert "Begriffe" in dsg and "Personendaten" in dsg


async def test_ch_schlusstitel_disposition():
    out = await server.get_legislation_provision("ch", "210", "Schlusstitel Art. 1")
    assert "Schlusstitel" in out


async def test_ch_decision_by_case_number_matches_aza_id():
    by_no = await server.get_decision("ch", "4A_640/2011", max_chars=3000)
    by_id = await server.get_decision("ch", "aza://19-12-2011-4A_640-2011", max_chars=3000)
    assert by_no == by_id and "Mietzins" in by_id


async def test_ch_bge_collection():
    out = await server.search_caselaw("ch", "Mietzinsherabsetzung", limit=3,
                                      filters={"collection": "bge"})
    assert 'get_decision("ch", "BGE ' in out
