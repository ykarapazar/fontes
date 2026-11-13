import asyncio
import datetime

from world_legal_mcp.jurisdictions import fi


def test_since_covers_range(monkeypatch):
    seen = []

    async def fake(court, year, kind="precedent"):
        seen.append(year)
        return []

    monkeypatch.setattr(fi, "_year_list", fake)
    a = fi.Adapter() if hasattr(fi, "Adapter") else [v for v in vars(fi).values() if isinstance(v, type) and hasattr(v, "search_caselaw")][0]()
    this = datetime.date.today().year
    r = asyncio.run(a.search_caselaw("irtisanominen", limit=5, page=1, filters={"since": 2022}))
    assert set(seen) == set(range(2022, this + 1))
    assert f"2022–{this}" in r.note
