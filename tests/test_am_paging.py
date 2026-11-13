import asyncio

import pytest

from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions import am

TOTAL = 1209


def _fake(seen):
    async def fake(form, page, order=""):
        seen.append(page)
        return [{"id": str(i), "title": "t"} for i in range((page - 1) * 10 + 1, page * 10 + 1)], TOTAL
    return fake


def test_limit_25_page_2_fetches_pages_3_to_5_and_slices(monkeypatch):
    seen = []
    monkeypatch.setattr(am, "_search_page", _fake(seen))
    r = asyncio.run(am.Armenia().search_caselaw("x", limit=25, page=2))
    assert seen == [3, 4, 5]
    assert [h.id for h in r.items] == [str(i) for i in range(26, 51)] and r.total == TOTAL


def test_legislation_limit_25_gives_25(monkeypatch):
    seen = []
    monkeypatch.setattr(am, "_search_page", _fake(seen))
    r = asyncio.run(am.Armenia().search_legislation("x", limit=25, filters={"status": "any"}))
    assert seen == [1, 2, 3] and [h.id for h in r.items] == [str(i) for i in range(1, 26)]


def test_limit_over_cap_rejected(monkeypatch):
    monkeypatch.setattr(am, "_search_page", _fake([]))
    with pytest.raises(BadRequest, match="limit"):
        asyncio.run(am.Armenia().search_caselaw("x", limit=am.MAX_LIMIT + 1))
