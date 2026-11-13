"""Live checks for Argentina (InfoLEG on argentina.gob.ar) beyond the shared conformance suite.

argentina.gob.ar asks for Crawl-delay 10, so each new request here waits 10 s;
the Código Civil y Comercial page is fetched once and cached in-process.
"""

from world_legal_mcp import server

CCYC = "235975"   # Ley 26.994, Código Civil y Comercial (InfoLEG id)


async def test_ccyc_id_variants_and_labels():
    for law in (CCYC, "ley-26994-235975",
                "https://www.argentina.gob.ar/normativa/nacional/ley-26994-235975/actualizacion"):
        out = await server.get_legislation_provision("ar", law, "art. 1716")
        assert "Deber de reparar" in out
    assert "responsabilidad parental" in await server.get_legislation_provision("ar", CCYC, "700 bis")
    out = await server.get_legislation_provision("ar", CCYC, "Artículo 1 (de la ley)")
    assert "Apruébase el Código Civil y Comercial" in out


async def test_toc_headings():
    out = await server.get_legislation_toc("ar", CCYC, keyword="reparar")
    assert "Artículo 1716 – Deber de reparar" in out


async def test_index_search_and_law_number():
    out = await server.search_legislation("ar", "código penal")
    assert "Código Penal" in out and "16546" in out
    assert "Deber de reparar" in await server.get_legislation_provision("ar", "ley 26.994", "1716")


async def test_infoleg_full_text_search():
    out = await server.search_legislation("ar", '"identidad de genero"')
    assert "26743" in out and "197860" in out
    out = await server.search_legislation("ar", "codigo de comercio", filters={"type": "decreto_ley"})
    assert "Decreto/Ley" in out
    assert "Bad request (ar)" in await server.search_legislation("ar", "x", filters={"type": "resolucion"})


async def test_bad_id_and_no_caselaw():
    assert "Bad request (ar)" in await server.get_legislation_text("ar", "not-an-id")
    assert "is not supported" in await server.search_caselaw("ar", "arriola")
