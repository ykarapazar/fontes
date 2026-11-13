"""Live smoke tests against the Afghan Ministry of Justice laws database (laws.moj.gov.af).
Needs network; plain HTTP, ASP.NET postbacks, 2 s spacing."""
from world_legal_mcp import server


async def test_af_search_by_gazette_number():
    # Latin digits are turned into the Persian digits the database stores.
    out = await server.search_legislation("af", "1452", limit=5)
    assert "1452-16577" in out and "in force" in out, out


async def test_af_provision_label_variants():
    a = await server.get_legislation_provision("af", "1452-16577", "مادۀ سوم")
    b = await server.get_legislation_provision("af", "1452-16577", "art. 3")
    assert "احتساب" in a and "احتساب" in b, a


async def test_af_legacy_font_pdf_is_refused_clearly():
    # Penal Code 2017 (Gazette 1260): legacy Arabic fonts, text layer is gibberish.
    out = await server.get_legislation_text("af", "1260-4414")
    assert "legacy fonts" in out, out


async def test_af_bad_id():
    assert "Bad request" in await server.get_legislation_text("af", "penal code")
