"""Live smoke tests against the e-Gov 法令API v2 (laws.e-gov.go.jp). Needs network."""
import re

from world_legal_mcp import server


async def test_jp_article_label_variants():
    for prov in ("第七百九条", "709", "art. 709", "第709条", "第７０９条"):
        out = await server.get_legislation_provision("jp", "129AC0000000089", prov)
        assert "# 民法: 第七百九条" in out and "故意又は過失によって" in out, prov
    branch = await server.get_legislation_provision("jp", "129AC0000000089", "398の2")
    assert "第三百九十八条の二" in branch and "根抵当権" in branch
    deleted = await server.get_legislation_provision("jp", "129AC0000000089", "50")
    assert "第三十八条から第八十四条まで" in deleted and "削除" in deleted


async def test_jp_law_id_variants():
    for law_id in ("民法", "明治二十九年法律第八十九号"):
        out = await server.get_legislation_provision("jp", law_id, "1")
        assert "第一条" in out and "私権は、公共の福祉に適合しなければならない。" in out, law_id
    suppl = await server.get_legislation_provision("jp", "322AC0000000049", "附則")
    assert "# 労働基準法: 附則" in suppl and "勅令" in suppl


async def test_jp_fulltext_search_with_type_filter():
    out = await server.search_legislation("jp", "不法行為", limit=3,
                                          filters={"search": "text", "law_type": "Act"})
    assert "Full-text search" in out and "129AC0000000089" in out
    assert set(re.findall(r"- Type: (\w+)", out)) == {"Act"}
