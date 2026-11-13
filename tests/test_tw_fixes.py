import asyncio

from world_legal_mcp.jurisdictions import tw


def test_court_filter_maps_and_keys(monkeypatch):
    seen = []

    async def fake_hash(query, court=""):
        seen.append(court)
        return "", 0

    monkeypatch.setattr(tw, "_query_hash", fake_hash)
    j = tw.Taiwan()
    asyncio.run(j.search_caselaw("損害賠償", limit=5, page=1, filters={"court": "supreme"}))
    asyncio.run(j.search_caselaw("損害賠償", limit=5, page=1, filters={"court": "tpa"}))
    asyncio.run(j.search_caselaw("損害賠償", limit=5, page=1, filters={}))
    assert seen == ["TPS", "TPA", ""]
    assert "court" in j.caselaw_filters


def test_constitution_provision_carries_amendment_note(monkeypatch):
    class L:
        pcode, title, url, as_of, meta, blocks = "A0000001", "憲法", "u", "1947-01-01", {}, []

        def find(self, p):
            return "第 27 條", "text"

    async def fake_load(id):
        return L()

    monkeypatch.setattr(tw, "_load_law", fake_load)
    p = asyncio.run(tw.Taiwan().get_legislation_provision("A0000001", "27"))
    assert "A0000002" in p.text and "text" in p.text


def test_chinese_court_name_and_bad_court(monkeypatch):
    seen = []

    async def fake_hash(query, court=""):
        seen.append(court)
        return "", 0

    monkeypatch.setattr(tw, "_query_hash", fake_hash)
    j = tw.Taiwan()
    asyncio.run(j.search_caselaw("損害賠償", limit=5, page=1, filters={"court": "最高法院"}))
    assert seen == ["TPS"]
    import pytest
    with pytest.raises(Exception, match="unknown court"):
        asyncio.run(j.search_caselaw("損害賠償", limit=5, page=1, filters={"court": "某法院"}))


def test_toc_provision_label_has_no_spaces():
    html = ('<a id="hlLawName">法</a><div class="law-reg-content"><div class="row">'
            '<div class="col-no"><a name="1">第 1 條</a></div><div class="law-article">'
            '<div>x</div></div></div></div>')
    law = tw._Law("N0030001", html)
    assert law.toc[0].provision == "第1條" and law.toc[0].title == "第 1 條"
    assert law.find("第1條")[0] == "第 1 條"


def test_search_caselaw_fetches_source_pages_and_slices(monkeypatch):
    from world_legal_mcp.models import DecisionHit
    pages = []

    async def fake_hash(query, court=""):
        return "h", 1000

    async def fake_page(q, n):
        pages.append(n)
        return [DecisionHit(id=str((n - 1) * 20 + i + 1), title="t", url="u") for i in range(20)]

    monkeypatch.setattr(tw, "_query_hash", fake_hash)
    monkeypatch.setattr(tw, "_result_page", fake_page)
    j = tw.Taiwan()
    r = asyncio.run(j.search_caselaw("損害賠償", limit=25, page=2, filters={}))
    assert pages == [2, 3] and [h.id for h in r.items] == [str(i) for i in range(26, 51)]
    assert "500" in r.note
    pages.clear()
    r = asyncio.run(j.search_caselaw("損害賠償", limit=50, page=1, filters={}))
    assert pages == [1, 2, 3] and len(r.items) == 50
    import pytest
    with pytest.raises(Exception, match="at most"):
        asyncio.run(j.search_caselaw("損害賠償", limit=101, page=1, filters={}))
    with pytest.raises(Exception, match="first 500"):
        asyncio.run(j.search_caselaw("損害賠償", limit=50, page=11, filters={}))
