import asyncio

import pytest

from world_legal_mcp.base import SourceError
from world_legal_mcp.jurisdictions import ps
from world_legal_mcp.models import LawHit


def _run(crashing, hit_pages):
    ps._search_cache.clear()

    async def fake(q, n):
        if n in crashing:
            raise SourceError("Error (ps): search failed (HTTP 500).", 500)
        return [("law", LawHit(id=str(n), title="t", status="مُلغى"))] if n in hit_pages else [], 5

    orig, ps._search_page = ps._search_page, fake
    try:
        return asyncio.run(ps._search("x", "law", 2, 1))
    finally:
        ps._search_page = orig
        ps._search_cache.clear()


def test_crashed_pages_are_skipped_and_flagged():
    r = _run({1, 3}, {2, 4})
    assert [h.id for h in r.items] == ["2", "4"]
    assert "INCOMPLETE" in r.note and "1, 3" in r.note
    assert "own label" in r.note and "date" in r.note


def test_incomplete_note_leads():
    r = _run({1}, {2})
    assert r.note.startswith("INCOMPLETE")


def test_crash_with_no_hits_raises_not_empty():
    with pytest.raises(SourceError, match="NOT a 'no results'"):
        _run({1, 3}, set())


def test_all_pages_crashing_raises():
    with pytest.raises(SourceError):
        _run({1, 2, 3, 4, 5}, set())


def test_no_title_match_is_stated():
    assert ps._missing_words("قانون الأحوال الشخصية", ["قانون بشأن الأحوال المدنية", "قانون المخالفات"])
    assert not ps._missing_words("قانون الأحوال الشخصية", ["قرار بقانون معدل للأحوال الشخصية"])
    assert not ps._missing_words("قانون العمل", ["قانون العمل رقم 7 لسنة 2000"])


def _fake_pages(by_query):
    ps._search_cache.clear()

    async def fake(q, n):
        r = by_query.get(q, {}).get(n)
        if r is None and n > 1:
            return [], 1
        if isinstance(r, Exception):
            raise r
        return r or [], 1

    orig, ps._search_page = ps._search_page, fake
    try:
        return asyncio.run(ps._search("قانون العمل", "law", 3, 1))
    finally:
        ps._search_page = orig
        ps._search_cache.clear()


def test_crashed_page_one_retries_with_palestinian():
    boom = SourceError("Error (ps): search failed (HTTP 500).", 500)
    good = [("law", LawHit(id="9", title="قانون العمل الفلسطيني رقم (7) لسنة 2000م"))]
    r = _fake_pages({"قانون العمل": {1: boom}, "قانون العمل الفلسطيني": {1: good}})
    assert [h.id for h in r.items] == ["9"]
    assert "retried" in r.note and "INCOMPLETE" not in r.note


def test_empty_result_says_nothing_matches():
    r = _fake_pages({"قانون العمل": {1: []}, "قانون العمل الفلسطيني": {1: []}})
    assert not r.items and "NOTHING on Maqam" in r.note


def test_base_law_absent_is_stated():
    hit = [("law", LawHit(id="1", title="قانون معدل لقانون العمل رقم 3 لسنة 1990"))]
    r = _fake_pages({"قانون العمل": {1: hit}})
    assert "No hit is titled" in r.note
