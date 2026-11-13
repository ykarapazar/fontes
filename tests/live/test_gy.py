"""Live smoke tests against the Laws of Guyana (mola.gov.gy). Needs network; 1 s per request."""
from world_legal_mcp import server


async def test_gy_search_and_chapter_ids():
    out = await server.search_legislation("gy", "Marriage")
    assert "45:01" in out and "Marriage Act" in out, out
    by_cap = await server.search_legislation("gy", "Cap. 8:01")
    assert "8:01" in by_cap and "Criminal Law (Offences) Act" in by_cap, by_cap


async def test_gy_bad_ids_never_fetch():
    assert "Use a chapter number" in await server.get_legislation_text("gy", "../laws/x.pdf")
    assert "has no Chapter" in await server.get_legislation_text("gy", "999:99")


async def test_gy_provision_label_variants():
    out = await server.get_legislation_provision("gy", "Cap. 008:01", "section 100")
    assert "convicted of murder" in out, out[:800]
    toc = await server.get_legislation_toc("gy", "8:01")
    assert "100. Murder" in toc, toc[:800]


async def test_gy_constitution_articles():
    out = await server.get_legislation_provision("gy", "1:01", "article 40")
    assert "Art. 40" in out and "fundamental rights" in out.lower(), out[:800]


async def test_gy_ccj_appeals_only_from_guyana():
    out = await server.search_caselaw("gy", "Mustapha", limit=5)
    assert "[2019] CCJ 13 (AJ)" in out, out[:800]
    marked = await server.search_caselaw("gy", "", limit=50, filters={"date_from": "2021-01-01"})
    assert "(AJ)" in marked and "(OJ)" not in marked
    dec = await server.get_decision("gy", "[2019] CCJ 13 (AJ)")
    assert "Guyana" in dec, dec[:500]
    # a Barbados appeal: served by the ccj adapter, not gy
    assert "not an appeal from Guyana" in await server.get_decision("gy", "[2020] CCJ 1 (AJ)")
