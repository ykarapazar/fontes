"""Andorra adapter checks that the shared conformance suite does not cover."""

from world_legal_mcp import server


async def test_ad_decision_by_nid_equals_path():
    a = await server.get_decision("ad", "19378")
    b = await server.get_decision("ad", "https://www.tribunalconstitucional.ad/sentencia/2026-32-re")
    assert a == b and "2026-32-RE" in a and "Sentència" in a
    bad = await server.get_decision("ad", "../../etc")
    assert "Bad request" in bad


async def test_ad_doc_type_and_date_filters():
    out = await server.search_caselaw("ad", "", limit=5,
                                      filters={"doc_type": "aute", "date_from": "2025-01-01"})
    assert "Aute" in out and "Sentència" not in out
    bad = await server.search_caselaw("ad", "x", filters={"process": "nope"})
    assert "Bad request" in bad


async def test_ad_provision_label_variants():
    a = await server.get_legislation_provision("ad", "L2022030", "Article 1")
    b = await server.get_legislation_provision("ad", "https://portaljuridicandorra.ad/L2022030", "art. 1")
    assert a == b and "Personalitat" in a


async def test_ad_constitution():
    hits = await server.search_legislation("ad", "Constitució")
    assert "CONSTITUCIO" in hits
    a = await server.get_legislation_provision("ad", "CONSTITUCIO", "Article 10")
    b = await server.get_legislation_provision("ad", "constitucio", "art. 10")
    assert a == b and "dret a la jurisdicció" in a and "consellgeneral.ad" in a
    toc = await server.get_legislation_toc("ad", "CONSTITUCIO")
    assert "Títol VIII. Del Tribunal Constitucional" in toc and "Article 107" in toc
