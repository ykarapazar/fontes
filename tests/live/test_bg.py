"""Live smoke tests against constcourt.bg (Constitutional Court) and parliament.bg (laws). Needs network."""
from world_legal_mcp import server


async def test_bg_decision_by_id_and_url():
    for did in ("10462", "https://www.constcourt.bg/bg/act-10462"):
        out = await server.get_decision("bg", did, max_chars=3000)
        assert "решение № 18 от 27.10.2026" in out and "11/2026" in out
        assert "2026-10-27" in out


async def test_bg_caselaw_year_filter_and_bad_type():
    out = await server.search_caselaw("bg", "", limit=2, filters={"year": "1995", "act_type": "all"})
    assert "1995-12-21" in out and "act-1809" in out
    assert "act_type must be one of" in await server.search_caselaw("bg", "", filters={"act_type": "xx"})
    assert "needs a 'year'" in await server.search_caselaw("bg", "", filters={"act_type": "all"})


async def test_bg_provision_label_variants():
    for p in ("1", "чл. 1", "art. 1", "Чл. 1"):
        out = await server.get_legislation_provision("bg", "166967", p)
        assert ": Чл. 1\n" in out
    assert ": § 93\n" in await server.get_legislation_provision("bg", "166967", "§ 93")
    assert "not found" in await server.get_legislation_provision("bg", "166967", "999")


async def test_bg_legislation_search():
    out = await server.search_legislation("bg", "ратифициране", limit=3)
    assert "Закон за ратифициране" in out and "parliament.bg/bg/laws/ID/" in out


async def test_bg_constitution_consolidated():
    assert "parliament.bg/bg/const" in await server.search_legislation("bg", "конституция", limit=2)
    out = await server.get_legislation_provision("bg", "const", "Чл. 1")
    assert "република с парламентарно управление" in out
    assert "бр.66 от 06.08.2024" in await server.get_legislation_text("bg", "const", max_chars=3000)


async def test_bg_legislation_year_archive():
    out = await server.search_legislation("bg", "наказателния кодекс", limit=3,
                                          filters={"year": "2010", "month": "3"})
    assert "laws/ID/9787" in out and "2010-03-24" in out
    assert "month must be" in await server.search_legislation("bg", "", filters={"month": "3"})
