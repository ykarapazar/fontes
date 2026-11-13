import asyncio

import pytest

from world_legal_mcp.jurisdictions import bg
from world_legal_mcp.base import BadRequest


def _run(year, monkeypatch):
    async def fake(y, t, n):
        return [{"id": y, "kind": "решение", "line": "", "judge": "", "disp": "", "date": f"{y}-01-01", "case": ""}]
    monkeypatch.setattr(bg, "_cc_list", fake)
    return asyncio.run(bg.Bulgaria().search_caselaw("", limit=10, page=1, filters={"year": year}))


def test_year_range_combines_years_newest_first(monkeypatch):
    res = _run("2022-2024", monkeypatch)
    assert [h.date[:4] for h in res.items] == ["2024", "2023", "2022"]


def test_bad_year_range(monkeypatch):
    with pytest.raises(BadRequest):
        _run("2024-2022", monkeypatch)


def test_zero_topic_hits_note_gives_listing_fallback(monkeypatch):
    async def fake(y, t, n):
        return [{"id": "1", "kind": "решение", "line": "", "judge": "", "disp": "x", "date": "2024-01-01", "case": ""}]
    async def dec(self, id):
        return type("D", (), {"text": "нищо"})()
    monkeypatch.setattr(bg, "_cc_list", fake)
    monkeypatch.setattr(bg.Bulgaria, "get_decision", dec)
    res = asyncio.run(bg.Bulgaria().search_caselaw("собственост", limit=10, page=1, filters={"year": "2024"}))
    assert not res.items and "empty query" in res.note and "1 acts" in res.note


def test_topic_scans_full_text_when_list_has_no_match(monkeypatch):
    async def fake(y, t, n):
        return [{"id": str(i), "kind": "решение", "line": "", "judge": "", "disp": "x",
                 "date": "2024-01-01", "case": ""} for i in (1, 2)]

    async def dec(self, id):
        return type("D", (), {"text": "Правото на частна Собственост е гарантирано" if id == "2" else "друго"})()
    monkeypatch.setattr(bg, "_cc_list", fake)
    monkeypatch.setattr(bg.Bulgaria, "get_decision", dec)
    res = asyncio.run(bg.Bulgaria().search_caselaw("собственост", limit=10, page=1, filters={"year": "2024"}))
    assert [h.id for h in res.items] == ["2"] and "full text" in res.note
