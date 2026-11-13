import asyncio

import pytest

from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions import bt

ROWS = {
    "7": {"id": 7, "type": "ACT", "title_eng": "Property Tax Act 2022", "documentYear": 2023, "status": "ENACTED"},
    "9": {"id": 9, "type": "ACT", "title_eng": "Civil Liability Act 2023", "documentYear": 2023, "status": "ENACTED"},
    "17": {"id": 17, "type": "ACT", "title_eng": "Biodiversity Act 2022", "documentYear": 2022,
           "commencementDate": "2022-07-15", "status": "ENACTED"},
    "5": {"id": 5, "type": "ACT", "title_eng": "Old Act 2010", "documentYear": 2010, "status": "ENACTED"},
}


def _search(monkeypatch, year, query=""):
    async def cat():
        return ROWS
    monkeypatch.setattr(bt, "_catalogue", cat)
    return asyncio.run(bt.Bhutan().search_legislation(query, limit=10, page=1, filters={"year": year}))


def test_year_range(monkeypatch):
    r = _search(monkeypatch, "2022-2023")
    assert sorted(h.id for h in r.items) == ["17", "7", "9"]
    assert "document year" in r.note


def test_since(monkeypatch):
    async def cat():
        return ROWS
    monkeypatch.setattr(bt, "_catalogue", cat)
    r = asyncio.run(bt.Bhutan().search_legislation("Act", limit=10, page=1, filters={"since": "2022"}))
    assert sorted(h.id for h in r.items) == ["17", "7", "9"]
    assert "2024 onward" in r.note


def test_single_year(monkeypatch):
    assert [h.id for h in _search(monkeypatch, "2010").items] == ["5"]


def test_bad_year(monkeypatch):
    with pytest.raises(BadRequest):
        _search(monkeypatch, "2024-2022")
    with pytest.raises(BadRequest):
        _search(monkeypatch, "abc")


def test_commencement_date_not_year(monkeypatch):
    rows = dict(ROWS, **{"103": {"id": 103, "type": "ACT", "title_eng": "Livestock Act of Bhutan, 2001",
                                  "documentYear": 2001, "commencementDate": "2021-06-25", "status": "ENACTED"}})

    async def cat():
        return rows
    monkeypatch.setattr(bt, "_catalogue", cat)
    r = asyncio.run(bt.Bhutan().search_legislation("", limit=10, page=1, filters={"year": "2021"}))
    assert r.items == []
    r = asyncio.run(bt.Bhutan().search_legislation("Livestock", limit=10, page=1, filters={}))
    assert r.items[0].date == "2021-06-25" and "commencement date" in r.note


def test_duplicate_listing_flagged(monkeypatch):
    rows = {
        "1": {"id": 1, "type": "ACT", "title_eng": "Fiscal Act 2021", "documentYear": 2021, "status": "ENACTED",
              "documentCopies": [{"language": "BILINGUAL"}]},
        "2": {"id": 2, "type": "ACT", "title_eng": "Fiscal Act 2021", "documentYear": 2021, "status": "ENACTED",
              "documentCopies": [{"language": "ENG"}]},
        "3": {"id": 3, "type": "ACT", "title_eng": "Tax Act 2021", "documentYear": 2021, "status": "ENACTED"},
    }

    async def cat():
        return rows
    monkeypatch.setattr(bt, "_catalogue", cat)
    r = asyncio.run(bt.Bhutan().search_legislation("Act", limit=10, page=1, filters={"year": "2021"}))
    t = {h.id: h.title for h in r.items}
    assert "duplicate listing" in t["1"] and "BILINGUAL" in t["1"] and "ENG" in t["2"]
    assert "duplicate" not in t["3"]
    assert "listed twice" in r.note
