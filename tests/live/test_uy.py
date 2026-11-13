"""Live smoke tests against IMPO (legislation) and BJN (case law). Needs network."""
from world_legal_mcp import server


async def test_uy_law_reference_lookup():
    out = await server.search_legislation("uy", "Ley Nº 19.889 de 2020", limit=5)
    assert "Uruguay (uy)" in out and "leyes/19889-2020" in out and "URGENTE CONSIDERACION" in out.upper()
    free = await server.search_legislation("uy", "responsabilidad extracontractual", limit=5)
    assert "robots.txt disallows" in free and "No results" in free


async def test_uy_provision_labels():
    for law, label in (("codigo-civil/16603-1994", "Artículo 1319"), ("codigo-civil/16603-1994", "art. 1319"),
                       ("https://www.impo.com.uy/bases/codigo-civil/16603-1994", "1319")):
        out = await server.get_legislation_provision("uy", law, label)
        assert "Artículo 1319" in out and "Todo hecho ilícito del hombre" in out, (law, label)
    bad = await server.get_legislation_provision("uy", "codigo civil", "1")
    assert bad.startswith("Bad request (uy)")


async def test_uy_caselaw_number_filter():
    out = await server.search_caselaw("uy", "", filters={"number": "207/2020"}, limit=50)
    assert "207/2020 | Tribunal Apelaciones Civil 1ºTº | 2020-11-11" in out
    assert "207/2020 | Tribunal Apelaciones Civil 1ºTº | 2020-06-12" in out
