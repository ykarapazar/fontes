"""Live smoke tests against SINALEVI (sinalevi.go.cr). Needs network."""
from world_legal_mcp import server


async def test_cr_search_by_number_and_filters():
    out = await server.search_legislation("cr", "7472", filters={"type": "L"}, limit=5)
    assert "26481" in out and "Promoción de la Competencia" in out and "1994-12-20" in out
    bad = await server.search_legislation("cr", "ley", filters={"type": "XX"})
    assert bad.startswith("Bad request (cr)")


async def test_cr_provision_label_variants():
    for label in ("16 bis", "Artículo 16 BIS", "art. 16 bis"):
        out = await server.get_legislation_provision("cr", "26481", label)
        assert "Artículo 16 bis" in out, label
    for label in ("Transitorio I", "transitorio 1", "1 transitorio"):
        out = await server.get_legislation_provision("cr", "26481", label)
        assert "Transitorio I.-" in out, label


async def test_cr_id_variants_and_unknown():
    url = "https://pgrweb.go.cr/scij/Busqueda/Normativa/Normas/nrm_texto_completo.aspx?nValor1=1&nValor2=871"
    out = await server.get_legislation_provision("cr", url, "1")
    assert "Costa Rica es una República democrática" in out
    missing = await server.get_legislation_toc("cr", "99999999")
    assert "not found" in missing.lower()
    bad = await server.get_legislation_toc("cr", "Ley 7472")
    assert bad.startswith("Bad request (cr)")
