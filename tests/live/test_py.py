"""Live smoke tests against BACN (legislation) and CSJ (case law). Needs network."""
from world_legal_mcp import server


async def test_py_law_number_search():
    out = await server.search_legislation("py", "ley 213", limit=3)
    assert "Paraguay (py)" in out and "### 1. Ley Nº 213 / ESTABLECE EL CODIGO DEL TRABAJO" in out


async def test_py_provision_labels():
    for law, label in (("2608", "47"), ("2608", "Artículo 47"),
                       ("https://www.bacn.gov.py/leyes-paraguayas/2608/x", "art. 47")):
        out = await server.get_legislation_provision("py", law, label)
        assert "2608" in out and "47" in out and "Bad request" not in out, (law, label)
    bad = await server.get_legislation_toc("py", "codigo civil")
    assert bad.startswith("Bad request (py)")
    missing = await server.get_legislation_toc("py", "999999")
    assert missing.startswith("Not found (py)")


async def test_py_caselaw_filters_and_decision():
    out = await server.search_caselaw("py", "usucapión", filters={"year": "2023", "type": "Acuerdo y Sentencia"},
                                      limit=5)
    assert "Paraguay (py)" in out and "2023" in out and "No results" not in out
    dec = await server.get_decision("py", "278")
    assert "Paraguay (py)" in dec and "Normas de referencia" in dec
    assert (await server.get_decision("py", "99999999")).startswith("Not found (py)")


async def test_py_constitution():
    hits = await server.search_legislation("py", "constitucion de la republica", limit=3)
    assert "9580" in hits and "CONSTITUCION DE LA REPUBLICA DEL PARAGUAY" in hits, hits
    art = await server.get_legislation_provision("py", "9580", "Artículo 137")
    assert "SUPREMACIA DE LA CONSTITUCION" in art, art[:500]
