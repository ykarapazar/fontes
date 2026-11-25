"""Live smoke tests against the Corte Constitucional del Ecuador Buscador de Sentencias. Needs network."""
from world_legal_mcp import server


async def test_ec_id_variants_and_old_numbering():
    out = await server.get_decision("ec", "Sentencia No. 1296-19-JP/25", max_chars=3000)
    assert "1296-19-JP/25" in out and "2025-11-13" in out and "Waorani" in out
    old = await server.get_decision("ec", "001-10-SEP-CC", max_chars=3000)
    assert "001-10-SEP-CC" in old and "0315-09-EP" in old
    bad = await server.get_decision("ec", "Ley 2021-526")
    assert bad.startswith("Bad request (ec)")


async def test_ec_unknown_decision():
    out = await server.get_decision("ec", "9999-99-XX/99")
    assert "Not found" in out and "9999-99-XX/99" in out


async def test_ec_filters():
    out = await server.search_caselaw("ec", "", filters={"case": "1296-19-JP"}, limit=5)
    assert "1296-19-JP/25" in out
    dated = await server.search_caselaw("ec", "consulta previa", filters={"date_from": "2023-11-01",
                                                                          "date_to": "2023-11-30"}, limit=20)
    assert "51-23-IN/23" in dated
    bad = await server.search_caselaw("ec", "x", filters={"date_from": "01/11/2023"})
    assert bad.startswith("Bad request (ec)")
