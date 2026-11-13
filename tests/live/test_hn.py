"""Live smoke tests against the TSC Biblioteca Virtual (www.tsc.gob.hn/biblioteca). Needs network."""
from world_legal_mcp import server

CONSTITUCION = "177"
LEY_208_2026 = "1587"  # Gaceta copy: the PDF's first page carries the tail of the previous norm


async def test_hn_search_filters():
    out = await server.search_legislation("hn", "transparencia beneficiario", filters={"match": "all"})
    assert "1563" in out and "127-2026" in out
    bad = await server.search_legislation("hn", "ley", filters={"order": "random"})
    assert bad.startswith("Bad request (hn)")


async def test_hn_provision_label_variants_and_id_forms():
    for label in ("4", "Artículo 4", "art. 4", "ARTICULO 4"):
        out = await server.get_legislation_provision("hn", CONSTITUCION, label)
        assert "republicana, democrática y representativa" in out, label
    url = "https://www.tsc.gob.hn/biblioteca/index.php/leyes/177-constitucion-de-la-republica-de-honduras"
    assert "idioma oficial" in await server.get_legislation_provision("hn", url, "6")
    assert (await server.get_legislation_toc("hn", "Constitución")).startswith("Bad request (hn)")
    assert "not found" in (await server.get_legislation_toc("hn", "999999")).lower()


async def test_hn_gaceta_copy_trimmed_and_dated():
    out = await server.get_legislation_text("hn", LEY_208_2026)
    assert "37,256" in out and "2026-09-26" in out
    assert "PRESIDENTA CICH" not in out  # previous norm's signatures cut off


async def test_hn_gaceta_month_search_and_issue_text():
    # ENAG La Gaceta Digital: issues of a month matched on their contents summary; an issue opens whole.
    out = await server.search_legislation("hn", "196-2026", limit=5, filters={"gaceta_month": "2026-10"})
    assert "20261002-37261" in out, out
    text = await server.get_legislation_text("hn", "20261002-37261")
    assert "37,261" in text and "enag.gob.hn" in text, text[:500]
