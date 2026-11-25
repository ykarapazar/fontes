"""Live smoke tests against FJUD (judgment.judicial.gov.tw) and law.moj.gov.tw. Needs network."""
from world_legal_mcp import server


async def test_tw_article_label_variants():
    for prov in ("第 184 條", "184", "art. 184", "第184條", "第１８４條"):
        out = await server.get_legislation_provision("tw", "B0000001", prov)
        assert "第 184 條" in out and "因故意或過失，不法侵害他人之權利者" in out, prov
    for prov in ("第191條之1", "191-1", "第 191-1 條"):
        out = await server.get_legislation_provision("tw", "B0000001", prov)
        assert "第 191-1 條" in out and "商品製造人" in out, prov


async def test_tw_law_id_variants_and_criminal_code():
    url = "https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=C0000001"
    out = await server.get_legislation_provision("tw", url, "271")
    assert "中華民國刑法" in out and "殺人者" in out
    bad = await server.get_legislation_toc("tw", "Z9999999")
    assert "Not found" in bad and "Z9999999" in bad


async def test_tw_case_number_search_and_old_format_decision():
    out = await server.search_caselaw("tw", "最高法院95台上1", limit=5)
    assert "TPSV,95,台上,1,20060105" in out
    dec = await server.get_decision("tw", "TPSV%2c95%2c%e5%8f%b0%e4%b8%8a%2c1%2c20060105")
    assert "最高法院" in dec and "2006-01-05" in dec and "返還保證金" in dec
