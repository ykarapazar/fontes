import asyncio

import pytest

from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions import ch


def _search(monkeypatch, coll, **filters):
    seen = {}

    async def fake(url, params=None):
        seen.update(params)
        return object()
    monkeypatch.setattr(ch, "_bger_html", fake)
    monkeypatch.setattr(ch, "_total", lambda root: 0)
    monkeypatch.setattr(ch, "_bge_hits", lambda root: [])
    monkeypatch.setattr(ch, "_aza_hits", lambda root: [])
    asyncio.run(ch.Switzerland().search_caselaw(
        "Kündigung", limit=5, page=1, filters={"collection": coll, **filters}))
    return seen


def test_bge_accepts_year(monkeypatch):
    p = _search(monkeypatch, "bge", date_from="2022", date_to="2024")
    assert (p["from_year"], p["to_year"]) == ("2022", "2024")


def test_aza_year_becomes_whole_year(monkeypatch):
    p = _search(monkeypatch, "aza", date_from="2022", date_to="2022")
    assert (p["from_date"], p["to_date"]) == ("01.01.2022", "31.12.2022")


def test_bad_date_still_rejected(monkeypatch):
    with pytest.raises(BadRequest):
        _search(monkeypatch, "bge", date_from="22")
