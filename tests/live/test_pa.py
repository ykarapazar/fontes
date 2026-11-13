"""Live smoke tests against Legispan (legispan.asamblea.gob.pa). Needs network."""
from world_legal_mcp import server

LEY81 = "54406cf4-9654-41b4-8654-6bb94f67f429"  # Ley 81 de 2019, protección de datos personales


async def test_pa_law_number_query_and_bad_filter():
    out = await server.search_legislation("pa", "Ley 81 de 2019")
    assert LEY81 in out and "DATOS PERSONALES" in out
    bad = await server.search_legislation("pa", "ley", filters={"year": "19"})
    assert bad.startswith("Bad request (pa)")


async def test_pa_provision_label_variants_and_id_forms():
    for label in ("2", "Artículo 2", "art. 2"):
        out = await server.get_legislation_provision("pa", LEY81, label)
        assert "Principio de lealtad" in out, label
    url = f"https://legispan.asamblea.gob.pa/norms/{LEY81}"
    assert "Esta Ley comenzará a regir" in await server.get_legislation_provision("pa", url, "47")
    assert (await server.get_legislation_toc("pa", "Ley 81")).startswith("Bad request (pa)")
    assert "not found" in (await server.get_legislation_toc("pa", "00000000-0000-0000-0000-000000000000")).lower()


async def test_pa_caselaw_court_filter_and_decision():
    out = await server.search_caselaw("pa", "inconstitucionalidad",
                                      filters={"court": "CORTE SUPREMA DE JUSTICIA - PLENO"}, limit=3)
    assert "CORTE SUPREMA DE JUSTICIA - PLENO" in out
    d = await server.get_decision("pa", "bbb019cd-471b-4ba7-b4ae-6b42d4e79cba")
    assert "VISTOS" in d and "30403-B" in d
    notcase = await server.get_decision("pa", LEY81)
    assert "not a ruling" in notcase
