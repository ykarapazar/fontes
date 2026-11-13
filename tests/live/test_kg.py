"""Live smoke tests against constsot.kg (Constitutional Court of the Kyrgyz Republic)."""
import re

from world_legal_mcp import server


async def test_kg_type_and_year_filters():
    out = await server.search_caselaw("kg", "", limit=3, filters={"type": "decision", "year": "1998"})
    assert re.findall(r'get_decision\("kg", "(\d+)"\)', out), out
    years = re.findall(r"- Date: (\d{4})", out)
    assert years and all(y == "1998" for y in years), out
    bad = await server.search_caselaw("kg", "x", filters={"type": "verdict"})
    assert bad.startswith("Bad request (kg)")


async def test_kg_decision_pdf_text_and_id_variants():
    for ident in ("26917", "constsot:26917"):
        dec = await server.get_decision("kg", ident, max_chars=3000)
        assert "Бир Дуйно" in dec and "П О С Т А Н О В Л Е Н И Е" in dec, dec[:500]


async def test_kg_non_act_post_rejected():
    # 29252 is a news post ("Дни открытых дверей..."), not a court act.
    out = await server.get_decision("kg", "29252")
    assert out.startswith("Not found (kg)"), out[:300]
