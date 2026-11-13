import asyncio

from world_legal_mcp.jurisdictions import jm


def test_empty_local_search_says_title_only(monkeypatch):
    async def no_rows(*a, **k):
        return []

    async def no_year(y):
        return "1"

    class Doc:
        def xpath(self, *a, **k):
            return []

    async def sc_get(params):
        return Doc()

    monkeypatch.setattr(jm, "_sc_get", sc_get)
    monkeypatch.setattr(jm, "_sc_year", no_year)
    monkeypatch.setattr(jm, "_sc_rows", lambda d: [])
    monkeypatch.setattr(jm, "_ca_rows", no_rows)
    adapter = next(v for v in vars(jm).values()
                   if isinstance(v, type) and v.__module__ == jm.__name__ and hasattr(v, "search_caselaw"))()
    r = asyncio.run(adapter.search_caselaw("negligence", filters={"court": "jmsc", "year": "2026"}))
    assert r.items == [] and r.total is None
    assert "NOT a subject search" in r.note
