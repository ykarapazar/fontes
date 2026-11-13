import asyncio

import pytest

from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions import bb
from world_legal_mcp.models import DecisionHit


def test_search_caselaw_fetches_source_pages_and_slices(monkeypatch):
    calls = []

    async def fake_page(params, page):
        calls.append(page)
        n0 = (page - 1) * bb.SRC_PAGE
        return [DecisionHit(id=f"j{i}", title=f"J{i}", url="u") for i in range(n0, min(n0 + bb.SRC_PAGE, 92))], 92

    monkeypatch.setattr(bb, "_search_page", fake_page)
    r = asyncio.run(bb.Barbados().search_caselaw("negligence", limit=15, page=2))
    assert calls == [2, 3]                          # rows 15..29 sit on source pages 2-3 (10 rows each)
    assert [h.id for h in r.items] == [f"j{i}" for i in range(15, 30)]
    assert r.total == 92
    with pytest.raises(BadRequest):                 # no silent cap: say why limit=25 is refused
        asyncio.run(bb.Barbados().search_caselaw("negligence", limit=25))
