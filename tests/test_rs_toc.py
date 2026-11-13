import types

import pytest

from world_legal_mcp import render
from world_legal_mcp.jurisdictions import rs


@pytest.mark.asyncio
async def test_toc_matches_latin_article_keyword(monkeypatch):
    html = ('<div class="text-content"><div class="text-center">Члан 2.</div><p>Први.</p>'
            '<div class="text-center">Члан 32а.</div><p>Други.</p></div><aside>')

    async def fake_get(url, **kw):
        return types.SimpleNamespace(status_code=200, text=html)
    monkeypatch.setattr(rs._http, "get", fake_get)
    rs._laws.clear()
    j = rs.Serbia()
    toc = await j.get_legislation_toc("ustav")
    out = render.toc(j, toc, keyword="Član 32a")
    assert "Члан 32а" in out and "Члан 2 " not in out
    assert "Члан 2 " in render.toc(j, toc, keyword="član 2")
    rs._laws.clear()


@pytest.mark.asyncio
async def test_named_law_not_in_corpus_says_so():
    j = rs.Serbia()
    res = await j.search_legislation("zakon o radu")
    assert res.total == 0 and "NOT available" in res.note
