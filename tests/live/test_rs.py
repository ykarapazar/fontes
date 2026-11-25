"""Live smoke tests against www.vrh.sud.rs (10 s Crawl-delay: slow). Needs network."""
from world_legal_mcp import server

SLUG = "rev2-21802023-3520-35224"


async def test_rs_search_filters_and_bad_filter():
    out = await server.search_caselaw("rs", "", limit=5,
                                      filters={"case_number": "Rev2 2180/2023", "court": "sc"})
    assert "Serbia (rs)" in out and f'get_decision("rs", "{SLUG}")' in out, out[:600]
    assert "Rev 2180/2023" not in out          # same number, other register: filtered out
    bad = await server.search_caselaw("rs", "zastarelost", filters={"matter": "tax"})
    assert bad.startswith("Bad request (rs)")


async def test_rs_decision_id_variants():
    for did in (SLUG, f"https://www.vrh.sud.rs/sr-lat/{SLUG}", "Rev2 2180/2023"):
        out = await server.get_decision("rs", did, max_chars=4000)
        assert "Vrhovni sud" in out and "2026-10-14" in out, (did, out[:300])
        assert "ODBIJA SE kao neosnovana revizija" in out


async def test_rs_not_found():
    out = await server.get_decision("rs", "rev2-99999999-nonexistent")
    assert out.startswith("Not found (rs)"), out[:200]


async def test_rs_constitution_and_labels():
    for label in ("Члан 17", "član 17", "17", "чл. 17."):
        out = await server.get_legislation_provision("rs", "ustav", label)
        assert "Положај странаца" in out, (label, out[:300])   # Члан 17 lacks the centred class
    out = await server.get_legislation_provision("rs", "zakon-o-ustavnom-sudu", "Члан 8 (10/2023)")
    assert "Прелазна одредба" in out
    out = await server.search_legislation("rs", "pravo na pravično suđenje")
    assert 'get_legislation_toc("rs", "ustav")' in out
