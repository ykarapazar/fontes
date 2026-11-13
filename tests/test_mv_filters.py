import asyncio

import pytest

from world_legal_mcp.base import NotFound
from world_legal_mcp.jurisdictions import mv

ROWS = [
    {"id": 1, "title": "ޤާނޫނު A", "legislation_no": "1/2025", "implemented_at": "2025-03-01T00:00:00Z"},
    {"id": 2, "title": "ގަވާއިދު B", "legislation_no": "2022/R-1", "implemented_at": "2025-04-01T00:00:00Z"},
]


def test_search_with_filter_uses_filtered_list(monkeypatch):
    seen = []

    async def fake_list(self, params):
        seen.append(params)
        return {"data": ROWS, "next_page_url": None, "total": 2}
    monkeypatch.setattr(mv.Maldives, "_list", fake_list)
    r = asyncio.run(mv.Maldives().search_legislation("ޤާނޫނު", filters={"year": 2025}))
    assert [h.id for h in r.items] == ["1"]
    assert all("filter[search]" not in p and p["filter[effective_year]"] == "2025" for p in seen)


def test_missing_article_lists_real_numbers(monkeypatch):
    async def fake_law(self, raw):
        return {"id": "251", "title": "t", "url": "u", "as_of": "",
                "blocks": [{"kind": "article", "label": "10"}, {"kind": "article", "label": "14"}]}
    monkeypatch.setattr(mv.Maldives, "_law", fake_law)
    with pytest.raises(NotFound, match="articles 10 to 14"):
        asyncio.run(mv.Maldives().get_legislation_provision("251", "5"))
