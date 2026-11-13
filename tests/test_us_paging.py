import asyncio

import pytest

from world_legal_mcp.jurisdictions import us


def _rows(p, n):
    # every 5th granule is front matter (skipped); section numbers run on across pages
    return [{"granuleId": f"USCODE-2024-title42-chap1-front{i}" if i % 5 == 4 else
             f"USCODE-2024-title42-chap1-sec{(p - 1) * 100 + i}", "title": "t"} for i in range(n)]


def test_uscode_search_pages_over_kept_hits(monkeypatch):
    calls = []

    async def fake_search(query, limit, page_no):
        calls.append((limit, page_no))
        return {"count": 250, "results": _rows(page_no, 100 if page_no < 3 else 50)}

    monkeypatch.setattr(us, "_search", fake_search)
    j = us.UnitedStates()
    r = asyncio.run(j.search_legislation("civil rights", limit=25, page=1, filters={}))
    assert calls == [(100, 1)] and len(r.items) == 25 and r.total == 250
    assert "upper bound" in r.note
    kept = [f"42 USC {(p - 1) * 100 + i}" for p in (1, 2, 3) for i in range(100 if p < 3 else 50)
            if i % 5 != 4]
    calls.clear()
    r = asyncio.run(j.search_legislation("civil rights", limit=25, page=4, filters={}))
    assert calls == [(100, 1), (100, 2)] and [h.id for h in r.items] == kept[75:100]
    calls.clear()
    r = asyncio.run(j.search_legislation("civil rights", limit=50, page=4, filters={}))
    assert calls == [(100, 1), (100, 2), (100, 3)]
    assert [h.id for h in r.items] == kept[150:200] and r.total == 200 and "upper bound" not in r.note
    with pytest.raises(Exception, match="1000"):
        asyncio.run(j.search_legislation("civil rights", limit=50, page=21, filters={}))


def test_caselaw_search_pages_over_kept_hits(monkeypatch):
    calls = []

    async def fake_search(query, limit, page_no):
        calls.append((limit, page_no))
        rows = [{"granuleId": f"USCOURTS-ca1-20-{(page_no - 1) * 100 + i}-0" if i % 4 else "junk",
                 "title": "t"} for i in range(100 if page_no < 2 else 40)]
        return {"count": 140, "results": rows}

    monkeypatch.setattr(us, "_search", fake_search)
    j = us.UnitedStates()
    kept = [f"USCOURTS-ca1-20-{(p - 1) * 100 + i}-0" for p in (1, 2)
            for i in range(100 if p < 2 else 40) if i % 4]
    r = asyncio.run(j.search_caselaw("Fourth Amendment", limit=25, page=4, filters={}))
    assert calls == [(100, 1), (100, 2)] and [h.id for h in r.items] == kept[75:100]
    assert r.total == len(kept) == 105
    with pytest.raises(Exception, match="1000"):
        asyncio.run(j.search_caselaw("Fourth Amendment", limit=50, page=21, filters={}))
