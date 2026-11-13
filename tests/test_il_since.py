import asyncio

from world_legal_mcp.jurisdictions import il


def test_il_since_filter_builds_odata_condition(monkeypatch):
    seen = {}

    async def fake(path):
        seen["p"] = path
        return {"value": [], "odata.count": "0"}

    monkeypatch.setattr(il, "_odata", fake)
    adapter = il.Israel()
    assert "since" in adapter.legislation_filters
    asyncio.run(adapter.search_legislation("חוק", limit=5, page=1, filters={"since": 2025}))
    assert "LatestPublicationDate" in seen["p"] and "2025-01-01" in seen["p"]
