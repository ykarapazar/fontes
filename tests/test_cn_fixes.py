import asyncio

import pytest

from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions import cn

HITS = [cn._hit("指导性案例201号：合同案", "1", "2022-12-30"),
        cn._hit("指导性案例100号：合同案", "2", "2018-06-01")]


def _s(monkeypatch, year):
    async def g():
        return HITS
    monkeypatch.setattr(cn, "_guiding_cases", g)
    return asyncio.run(cn.China().search_caselaw("合同", limit=10, page=1, filters={"year": year} if year else None))


def test_year_filter(monkeypatch):
    assert [h.id for h in _s(monkeypatch, "2022").items] == ["1"]
    assert [h.id for h in _s(monkeypatch, "2018-2022").items] == ["1", "2"]
    assert len(_s(monkeypatch, None).items) == 2


def test_bad_year(monkeypatch):
    with pytest.raises(BadRequest):
        _s(monkeypatch, "2024-2022")


def test_note_court_and_date(monkeypatch):
    n = _s(monkeypatch, None).note
    assert "publisher" in n and "posting" in n


def test_legislation_gap_points_to_official_site_for_manual_use():
    from world_legal_mcp.jurisdictions.cn import China
    gap = next(g for g in China.gaps if "flk.npc.gov.cn" in g)
    assert "https://flk.npc.gov.cn" in gap and "yourself" in gap
