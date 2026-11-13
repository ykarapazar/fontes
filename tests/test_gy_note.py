import asyncio

from world_legal_mcp.jurisdictions import gy


def test_search_note_says_post_2022_acts_not_covered(monkeypatch):
    async def fake(q, page):
        return [], 1
    monkeypatch.setattr(gy, "_search", fake)
    cls = next(v for v in vars(gy).values() if isinstance(v, type) and hasattr(v, "search_legislation") and v.__module__ == gy.__name__)
    res = asyncio.run(cls().search_legislation("Data Protection Act"))
    assert "parliament.gov.gy" in res.note and "1/2022" in res.note


def test_search_note_does_not_place_cybercrime_act_after_revision(monkeypatch):
    async def fake(q, page):
        return [], 1
    monkeypatch.setattr(gy, "_search", fake)
    cls = next(v for v in vars(gy).values() if isinstance(v, type) and hasattr(v, "search_legislation") and v.__module__ == gy.__name__)
    res = asyncio.run(cls().search_legislation("Cybercrime"))
    assert "Cybercrime Act 2018" in res.note
    assert "after the L.R.O. 1/2022 revision (31 Dec 2022), e.g." not in res.note


def test_caselaw_zero_hits_says_topic_search_unsupported(monkeypatch):
    from world_legal_mcp.models import Results

    async def fake(*a, **k):
        return Results(items=[], total=0, note="CCJ note.")
    monkeypatch.setattr(gy, "ccj_appeals", fake)
    res = asyncio.run(gy.Guyana().search_caselaw("negligence"))
    assert "Topic search is not supported" in res.note and "empty query" in res.note


def test_caselaw_zero_hits_says_supreme_court_not_online(monkeypatch):
    from world_legal_mcp.models import Results

    async def fake(*a, **k):
        return Results(items=[], total=0, note="CCJ note.")
    monkeypatch.setattr(gy, "ccj_appeals", fake)
    res = asyncio.run(gy.Guyana().search_caselaw("negligence"))
    assert "High Court judgments are not published online" in res.note
