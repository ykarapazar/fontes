import asyncio

import pytest

from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions import mn
from world_legal_mcp.models import DecisionHit

TOTAL = 210


def _fake(seen):
    async def fake(params, page):
        seen.append(page)
        return [DecisionHit(id=f"1/3/{i}", title="t")
                for i in range((page - 1) * 10 + 1, min(page * 10, TOTAL) + 1)], TOTAL
    return fake


def test_limit_25_page_2_fetches_pages_3_to_5_and_slices(monkeypatch):
    seen = []
    monkeypatch.setattr(mn, "_search_page", _fake(seen))
    r = asyncio.run(mn.Mongolia().search_caselaw("x", limit=25, page=2))
    assert seen == [3, 4, 5]
    assert [h.id for h in r.items] == [f"1/3/{i}" for i in range(26, 51)] and r.total == TOTAL


def test_stops_at_end_of_results(monkeypatch):
    seen = []
    monkeypatch.setattr(mn, "_search_page", _fake(seen))
    r = asyncio.run(mn.Mongolia().search_caselaw("x", limit=25, page=9))  # hits 201-225 of 210
    assert seen == [21]
    assert [h.id for h in r.items] == [f"1/3/{i}" for i in range(201, 211)]


def test_limit_over_cap_rejected(monkeypatch):
    monkeypatch.setattr(mn, "_search_page", _fake([]))
    with pytest.raises(BadRequest, match="limit"):
        asyncio.run(mn.Mongolia().search_caselaw("x", limit=mn.MAX_LIMIT + 1))
