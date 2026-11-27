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


def _india_fake(monkeypatch, found, phrase_acts):
    from world_legal_mcp import lexifina

    async def call(tool, **a):
        if tool == "find_provision":
            return {"structuredContent": {"results": found}}
        return {"content": [], "structuredContent": {
            "matches": [], "acts": phrase_acts, "match": "phrase", "matched_by": "index", "summary": ""}}
    monkeypatch.setattr(lexifina, "call", call)


def test_india_legislation_comes_from_lexifina_not_india_code():
    j = in_.India()
    leg = [s for s in j.sources if "legislation" in s.covers]
    assert len(leg) == 1 and "Lexifina" in leg[0].name and not leg[0].official and not leg[0].needs_permission
    assert "indiacode.gov.in" in " ".join(j.gaps) and "India Code" in j.notes   # why India Code itself is not used
    assert j.supports("get_legislation_toc") and j.supports("search_caselaw")
    assert not getattr(j, "via_lexifina", True) and j.lexifina_legislation


def test_india_legislation_off_with_lexifina_but_caselaw_stays(monkeypatch):
    monkeypatch.setenv("WLM_LEXIFINA", "0")
    j = in_.India()
    assert not j.supports("search_legislation") and j.supports("search_caselaw") and j.supports("get_decision")


def test_india_search_puts_the_act_first_and_drops_court_folders(monkeypatch):
    it = "india/national/acts/central/acts/information-technology-act-2000"
    _india_fake(monkeypatch, [{"path": it, "title": "The Information Technology Act, 2000", "kind": "act"},
                              {"path": it + "/sec-001.md", "title": "s 1", "kind": "provision"}],
                [{"path": "india/national/acts/courts/high-courts/delhi/principal/2022/09/27", "title": "",
                  "matching_provisions": 20},
                 {"path": "india/national/acts/central/acts/other-act-2001", "title": "Other Act, 2001",
                  "matching_provisions": 3}])
    r = asyncio.run(in_.India().search_legislation("Information Technology Act 2000", limit=10, page=1, filters={}))
    assert [i.id for i in r.items] == [it, "india/national/acts/central/acts/other-act-2001"]
    assert "None of these acts" not in r.note and r.total is None
