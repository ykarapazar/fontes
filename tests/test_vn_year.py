import asyncio

import pytest

from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions import vn


def _run(year, monkeypatch):
    rows = [{"id": f"TAND{y}", "number": f"01/{y}/AL", "name": "hợp đồng", "date": f"{y}-05-01",
             "field": "", "status": "", "applies": ""} for y in (2020, 2022, 2024)]

    async def fake():
        return rows
    monkeypatch.setattr(vn, "_al_list", fake)
    return asyncio.run(vn.Vietnam().search_caselaw("hợp đồng", filters={"year": year}))


def test_since(monkeypatch):
    assert [h.date[:4] for h in _run("2022-", monkeypatch).items] == ["2022", "2024"]


def test_single_and_range(monkeypatch):
    assert len(_run(2022, monkeypatch).items) == 1
    assert len(_run("2020-2022", monkeypatch).items) == 2


def test_bad(monkeypatch):
    with pytest.raises(BadRequest):
        _run("abc", monkeypatch)
