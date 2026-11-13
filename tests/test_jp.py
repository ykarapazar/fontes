from lxml import etree

from world_legal_mcp import render
from world_legal_mcp.jurisdictions import jp

XML = """<r><law_info><law_id>129AC0000000089</law_id></law_info>
<revision_info><law_title>T</law_title></revision_info>
<law_full_text><Law><LawBody><MainProvision>
<Article Num="709"><ArticleTitle>第七百九条</ArticleTitle><ArticleCaption>（不法行為）</ArticleCaption></Article>
<Article Num="398_2"><ArticleTitle>第三百九十八条の二</ArticleTitle></Article>
</MainProvision></LawBody></Law></law_full_text></r>"""


def test_constitution_id_is_accepted():
    assert jp._LAW_ID.match("321CONSTITUTION")
    assert jp._LAW_ID.match("129AC0000000089")
    assert not jp._LAW_ID.match("民法")


def test_toc_keyword_arabic_number():
    law = jp._Law(etree.fromstring(XML.encode()))
    t = jp.Toc(id="x", title="T", url="u", entries=law.toc)
    assert "第七百九条" in render.toc(jp.Japan(), t, keyword="709")
    assert "第三百九十八条の二" in render.toc(jp.Japan(), t, keyword="398の2")


def test_courts_source_listed():
    assert any("courts.go.jp" in s.url for s in jp.Japan.sources)


def test_case_law_source_listed_first():
    assert "courts.go.jp" in jp.Japan.sources[0].url


def test_title_search_ranks_exact_match_first(monkeypatch):
    import asyncio

    class R:
        def json(self):
            return {"laws": [{"law_info": {"law_id": str(i)},
                              "revision_info": {"law_title": t}}
                             for i, t in enumerate(["中小企業投資育成株式会社法", "会社法施行法", "会社法"])]}

    async def fake(path, params):
        return R()

    monkeypatch.setattr(jp, "_api", fake)
    res = asyncio.run(jp.Japan().search_legislation("会社法", limit=20, page=1, filters={}))
    assert [h.title for h in res.items][:2] == ["会社法", "会社法施行法"]
