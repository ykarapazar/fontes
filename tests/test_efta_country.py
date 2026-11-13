import asyncio

import pytest

from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions import efta


def test_country_with_direct_is_explained(monkeypatch):
    async def fake(name):
        return []
    monkeypatch.setattr(efta, "_list", fake)
    j = next(v for v in vars(efta).values()
             if isinstance(v, type) and hasattr(v, "search_caselaw") and v.__module__ == efta.__name__)()
    with pytest.raises(BadRequest, match="only applies to referrals"):
        asyncio.run(j.search_caselaw("Norway", filters={"type": "direct", "country": "Norway"}))


def test_efta_states_no_legislation_plainly():
    j = next(v for v in vars(efta).values()
             if isinstance(v, type) and hasattr(v, "search_caselaw") and v.__module__ == efta.__name__)()
    assert "no legislation" in j.notes
    assert any("not available here" in g and "'eu'" in g for g in j.gaps)
    assert not any("not researched" in g for g in j.gaps)
