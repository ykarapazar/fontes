"""Offline tests for the Egypt adapter: zero-match padding rows and the cap note."""
import asyncio

from world_legal_mcp.jurisdictions import eg


def _row(i, para):
    return {"caseId": i, "ruleNumber": i, "ruleDate": f"2026-01-{i:02d}", "matchedParagraph": para,
            "caseInfo": f"الدعوى {i} لسنة 9 قضائية «دستورية»"}


def _run(monkeypatch, rows, **kw):
    async def fake(body):
        return rows
    monkeypatch.setattr(eg, "_search", fake)
    return asyncio.run(eg.Egypt().search_caselaw(kw.pop("query", ""), limit=10, page=1, filters=kw))


def test_zero_match_rows_dropped(monkeypatch):
    rows = [_row(1, "بحث فى النص: عدد النتائج:0 x"), _row(2, "<mark>خصوصية</mark>")]
    res = _run(monkeypatch, rows, query="خصوصية")
    assert [h.id for h in res.items] == ["2"]


def test_all_zero_match_says_so(monkeypatch):
    res = _run(monkeypatch, [_row(1, "بحث فى النص: عدد النتائج:0")], query="خصوصية")
    assert not res.items and "No ruling's text matched" in res.note


def test_cap_note_mentions_date_to(monkeypatch):
    rows = [_row(i % 28 + 1, "") for i in range(25)]
    res = _run(monkeypatch, rows, date_from="2022-01-01")
    assert "NOT shown" in res.note and "date_to" in res.note


def _capture(monkeypatch, replies):
    bodies = []

    async def fake(body):
        bodies.append(body)
        return replies[len(bodies) - 1]
    monkeypatch.setattr(eg, "_search", fake)
    return bodies


def test_multiword_asks_adjacent_then_near(monkeypatch):
    bodies = _capture(monkeypatch, [[], [_row(2, "<mark>المادة</mark> <mark>53</mark>")]])
    res = asyncio.run(eg.Egypt().search_caselaw("الدستور المادة 53", limit=10, page=1, filters={}))
    assert [b["slop"] for b in bodies] == [0, 5]
    assert [h.id for h in res.items] == ["2"] and "within 5 words" in res.note


def test_single_word_not_phrase_search(monkeypatch):
    bodies = _capture(monkeypatch, [[_row(1, "<mark>تمييز</mark>")]])
    asyncio.run(eg.Egypt().search_caselaw("التمييز", limit=10, page=1, filters={}))
    assert len(bodies) == 1 and bodies[0]["slop"] is None


def test_date_window_cap_note_explains_windows(monkeypatch):
    rows = [_row(i % 28 + 1, "") for i in range(25)]
    res = _run(monkeypatch, rows, date_from="2022-01-01", date_to="2022-12-31")
    assert "newest 25" in res.note and "2023" in res.note and "e.g. date_from 2022-01-01" not in res.note


def test_single_word_drops_shorter_root_hits(monkeypatch):
    rows = [_row(1, "في خصوص الاتهامات"), _row(2, "حرمة <mark>الخصوصية</mark>")]
    res = _run(monkeypatch, rows, query="الخصوصية")
    assert [h.id for h in res.items] == ["2"]
