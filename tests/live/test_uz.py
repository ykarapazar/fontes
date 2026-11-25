"""Live smoke tests against lex.uz (National Database of Legislation of Uzbekistan)."""
import re


from world_legal_mcp import server



async def test_uz_legislation_filters():
    out = await server.search_legislation("uz", "Гражданский кодекс", limit=20, page=2,
                                          filters={"lang": "ru"})
    assert 'get_legislation_toc("uz", "111181")' in out, out
    bad = await server.search_legislation("uz", "кодекс", filters={"status": "maybe"})
    assert bad.startswith("Bad request (uz)")


async def test_uz_provision_label_variants():
    for label in ("Статья 1", "1", "ст. 1", "art. 1", "статья 1."):
        out = await server.get_legislation_provision("uz", "111181", label)
        assert "Статья 1." in out and "основные начала" in out.lower(), label
    for label in ("26-1", "26¹", "Статья 26^1"):
        out = await server.get_legislation_provision("uz", "111181", label)
        assert "Статья 26¹." in out and "неплатежеспособность" in out.lower(), label


async def test_uz_caselaw_branch_filter_and_decision():
    out = await server.search_caselaw("uz", "", limit=5, filters={"lang": "ru", "branch": "economic"})
    ids = re.findall(r'get_decision\("uz", "(-?\d+)"\)', out)
    assert ids, out
    dec = await server.get_decision("uz", "https://lex.uz/ru/docs/6676132", max_chars=3000)
    assert "ВЕРХОВНОГО СУДА" in dec and "4-12-2306/3" in dec


async def test_uz_bad_and_unknown_id():
    bad = await server.get_legislation_toc("uz", "civil-code")
    assert bad.startswith("Bad request (uz)")
    missing = await server.get_legislation_toc("uz", "999999999")
    assert missing.startswith("Not found (uz)")
