import asyncio

import pytest

from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions import in_


def _row(year, title, headnote):
    return {"path": f"{year}_1_1_2", "year": str(year), "title": title, "scr": "", "nc": "", "coram": "",
            "headnote": headnote, "date": f"{year}-01-01", "case_number": ""}


def _search(monkeypatch, query, year):
    data = {"2022": [_row(2022, "A v B", "Article 21 - personal liberty"), _row(2022, "C v D", "Penal Code 2021")],
            "2023": [_row(2023, "E v F", "Right to life under Article 21")]}

    async def fake(y):
        return data[y]
    monkeypatch.setattr(in_, "_sc_year", fake)
    return asyncio.run(in_.India().search_caselaw(query, limit=10, page=1, filters={"year": year}))


def test_year_range_and_stopwords(monkeypatch):
    r = _search(monkeypatch, "Article 21 right to life", "2022-2023")
    assert [h.id for h in r.items] == ["2023_1_1_2"]
    assert "2022-2023" in r.note


def test_whole_word_and_partial_fallback(monkeypatch):
    r = _search(monkeypatch, "21", "2022")
    assert [h.id for h in r.items] == ["2022_1_1_2"]          # not "2021"
    r = _search(monkeypatch, "Article 21 cruelty", "2022")
    assert len(r.items) == 1 and "showing" in r.note


def test_range_too_long(monkeypatch):
    with pytest.raises(BadRequest):
        _search(monkeypatch, "x", "2010-2024")


def test_since_year_in_query(monkeypatch):
    seen = []

    async def fake(y):
        seen.append(y)
        return [_row(y, "A v B", "Article 21")]
    monkeypatch.setattr(in_, "_sc_year", fake)
    monkeypatch.setattr(in_.datetime, "date", type("D", (), {"today": staticmethod(lambda: type("T", (), {"year": 2026})())}))
    r = asyncio.run(in_.India().search_caselaw("Article 21 since 2022", limit=10, page=1, filters={}))
    assert seen == ["2022", "2023", "2024", "2025", "2026"] and len(r.items) == 5
    assert "2022-2026" in r.note
    with pytest.raises(BadRequest):
        asyncio.run(in_.India().search_caselaw("Article 21 since 2015", limit=10, page=1, filters={}))


def test_no_year_defaults_to_latest_window(monkeypatch):
    seen = []

    async def fake(y):
        seen.append(y)
        return [_row(y, "A v B", "arbitration award")]
    monkeypatch.setattr(in_, "_sc_year", fake)
    monkeypatch.setattr(in_.datetime, "date", type("D", (), {"today": staticmethod(lambda: type("T", (), {"year": 2026})())}))
    r = asyncio.run(in_.India().search_caselaw("arbitration award", limit=10, page=1, filters={}))
    assert seen == ["2022", "2023", "2024", "2025", "2026"] and len(r.items) == 5
    assert "No year given" in r.note and "2022-2026" in r.note


def test_india_legislation_refusal_names_manual_route():
    from world_legal_mcp.jurisdictions.in_ import India
    src = next(s for s in India.sources if s.needs_permission)
    assert "indiacode.gov.in" in src.warning and "by hand" in src.warning
