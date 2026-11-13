import asyncio

from world_legal_mcp.jurisdictions import au


def test_search_breaks_relevance_ties_by_name_and_skips_by_offset(monkeypatch):
    sent = {}

    class R:
        def json(self):
            return {"value": [], "@odata.count": 0}

    async def fake(path, params=None):
        sent.update(params)
        return R()
    monkeypatch.setattr(au, "_api", fake)
    asyncio.run(au._search("Competition and Consumer Act", None, 5, 6))
    assert sent["$orderby"] == "searchContexts/text/relevance desc,name asc"
    assert sent["$top"] == "5" and sent["$skip"] == "25"
