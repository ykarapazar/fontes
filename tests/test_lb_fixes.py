import asyncio

from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions import lb
from world_legal_mcp.models import DecisionHit

IDS = ["constitutional/12/2026", "constitutional/12/2025", "constitutional/3/2022",
       "constitutional/2/2012", "constitutional/1/2012"]


def _hit(i):
    return DecisionHit(id=i, title=i, court="c", date="", case_number="", snippet="", url="u")


def _run(monkeypatch, **filters):
    async def fake(kind, params, page):
        rows = IDS[(page - 1) * 4: page * 4]
        return [(_hit(i), {}) for i in rows], 2
    monkeypatch.setattr(lb, "_list_page", fake)
    return asyncio.run(lb.Lebanon().search_caselaw("", filters=filters))


def test_number_is_exact(monkeypatch):
    r = _run(monkeypatch, number="12")
    assert [h.id for h in r.items] == IDS[:2] and r.total == 2


def test_year_range(monkeypatch):
    assert [h.id for h in _run(monkeypatch, year="2022-").items] == IDS[:3]
    assert [h.id for h in _run(monkeypatch, year="2022").items] == [IDS[2]]


def test_zero_hit_note_scope(monkeypatch):
    r = _run(monkeypatch, year="2023-2024")
    assert r.items == [] and r.total == 0 and "Court of Cassation" in r.note
    try:
        _run(monkeypatch, year="22")
    except BadRequest:
        pass
    else:
        raise AssertionError


def test_bare_year_date_points_to_year_filter(monkeypatch):
    import pytest
    with pytest.raises(BadRequest, match="year filter"):
        _run(monkeypatch, date="2022")


def test_year_uses_date_when_number_year_is_wrong(monkeypatch):
    rows = [("constitutional/1/2023", "2023-01-05"), ("constitutional/22/2019", "2022-12-22"),
            ("constitutional/1/2022", "2022-04-14"), ("constitutional/2/2021", "2021-12-21")]

    async def fake(kind, params, page):
        return [(DecisionHit(id=i, title=i, court="c", date=d, case_number="", snippet="", url="u"), {})
                for i, d in rows], 1
    monkeypatch.setattr(lb, "_list_page", fake)
    r = asyncio.run(lb.Lebanon().search_caselaw("", filters={"year": "2022"}))
    assert [h.id for h in r.items] == ["constitutional/22/2019", "constitutional/1/2022"]


def test_empty_legislation_says_statutes_missing(monkeypatch):
    async def fake(law_id):
        return {"title": "t", "url": "u", "lang": "en", "sections": []}
    monkeypatch.setattr(lb, "_constitution", fake)
    r = asyncio.run(lb.Lebanon().search_legislation("labour code"))
    assert r.items == [] and r.note.startswith("Not in Fontes")
