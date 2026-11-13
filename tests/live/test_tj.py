"""Live smoke tests against constcourt.tj and president.tj (Tajikistan)."""
import re

from world_legal_mcp import server


async def test_tj_constitution_article_variants_ru_and_tg():
    for prov in ("Статья 2", "2", "ст. 2"):
        out = await server.get_legislation_provision("tj", "constcourt-501", prov)
        assert "Статья 2" in out and "таджикский язык" in out, out[:400]
    tg = await server.get_legislation_provision("tj", "constcourt-305", "Моддаи 2")
    assert "забони тоҷикӣ" in tg, tg[:400]


async def test_tj_decision_date_from_text():
    out = await server.get_decision("tj", "544", max_chars=3000)
    assert "2016-02-04" in out and "П О С Т А Н О В Л Е Н И Е" in out, out[:600]
    bad = await server.get_decision("tj", "abc")
    assert bad.startswith("Bad request (tj)"), bad[:200]


async def test_tj_president_number_filter_round_trip_and_points():
    out = await server.search_legislation("tj", "", limit=5,
                                          filters={"source": "president", "type": "decrees", "number": "1132"})
    ids = re.findall(r'get_legislation_\w+\("tj", "(\d+)"', out)
    assert "54676" in ids, out
    p = await server.get_legislation_provision("tj", "54676", "п. 2")
    assert "Правительству Республики Таджикистан" in p, p[:400]
    bad = await server.search_legislation("tj", "x", filters={"type": "laws"})
    assert bad.startswith("Bad request (tj)"), bad[:200]


async def test_tj_unknown_president_id_not_found():
    out = await server.get_legislation_text("tj", "99999999")
    assert out.startswith("Bad request (tj)") or out.startswith("Not found (tj)"), out[:300]
    out = await server.get_legislation_text("tj", "9999999")
    assert out.startswith("Not found (tj)"), out[:300]


async def test_tj_mmk_codes_number_and_languages():
    out = await server.search_legislation("tj", "кодекс", limit=5, filters={"source": "mmk"})
    assert re.search(r'get_legislation_\w+\("tj", "mmk-\d+"', out), out[:800]
    assert "December 2019" in out                      # the frozen-database warning
    out = await server.search_legislation("tj", "", limit=3, filters={"source": "mmk", "number": "1108"})
    assert "mmk-312" in out and "ИСЛАМСКОЙ БАНКОВСКОЙ" in out, out[:800]
    tg = await server.get_legislation_provision("tj", "mmk-312-tj", "Моддаи 1")
    assert "Мафҳумҳои асосӣ" in tg, tg[:400]
    bad = await server.search_legislation("tj", "x", filters={"source": "mmk", "lang": "en"})
    assert bad.startswith("Bad request (tj)"), bad[:200]


async def test_tj_mmk_constitution_consolidated_2016():
    out = await server.get_legislation_provision("tj", "mmk-1", "ст. 2")
    assert "таджикский язык" in out, out[:400]
    full = await server.get_legislation_text("tj", "mmk-1", max_chars=2000)
    assert "22 мая 2016" in full, full[:800]
