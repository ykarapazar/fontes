import asyncio

import pytest

from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions import xk


def _caselaw(monkeypatch, filters):
    seen = {}

    async def api(method, path, **kw):
        seen.update(kw["json"])
        return []
    monkeypatch.setattr(xk, "_api", api)
    r = asyncio.run(xk.Kosovo().search_caselaw("prona", limit=5, page=1, filters=filters))
    return seen, r


def test_date_from_to(monkeypatch):
    body, r = _caselaw(monkeypatch, {"date_from": "2022-01-01", "date_to": "2022-12-31"})
    assert body["dateFrom"] == "2022-01-01" and body["dateTo"] == "2022-12-31"
    assert "publication date" in r.note


def test_date_to_alone_gets_a_from(monkeypatch):
    body, _ = _caselaw(monkeypatch, {"date_to": "2022-12-31"})
    assert body["dateFrom"] and body["dateTo"] == "2022-12-31"


def test_bad_date(monkeypatch):
    with pytest.raises(BadRequest):
        _caselaw(monkeypatch, {"date_from": "2022"})


def test_consolidated_version(monkeypatch):
    async def act(self, id):
        return "KUSHTETUTA E REPUBLIKËS SË KOSOVËS (KONSOLIDUAR)", ["x"]
    monkeypatch.setattr(xk.Kosovo, "_act", act)
    t = asyncio.run(xk.Kosovo().get_legislation_text("97703"))
    assert "consolidated" in t.metadata["Version"] and "not consolidated" not in t.metadata["Version"]


def test_labour_law_name_routed_to_number(monkeypatch):
    urls = []

    async def get(url):
        urls.append(url)
        return ""
    monkeypatch.setattr(xk, "_gzk_get", get)
    r = asyncio.run(xk.Kosovo().search_legislation("Ligji i punës", limit=5, page=1, filters={}))
    assert "03%2FL-212" in urls[0] or "03/L-212" in urls[0]
    assert "03/L-212" in r.note


def test_multiword_title_falls_back_to_longest_word(monkeypatch):
    urls = []
    row = ("3702", "KUSHTETUTA E REPUBLIKËS SË KOSOVËS", "2008-04-09")

    async def get(url):
        urls.append(url)
        return "PAGE"
    monkeypatch.setattr(xk, "_gzk_get", get)
    monkeypatch.setattr(xk, "_total", lambda s: 0 if len(urls) == 1 else 2)
    monkeypatch.setattr(xk, "_hits", lambda s: [] if len(urls) == 1 else [row, ("1", "KODI PENAL", "2019-01-01")])
    r = asyncio.run(xk.Kosovo().search_legislation("Kushtetuta e Republikës", limit=5, page=1, filters={}))
    assert [i.id for i in r.items] == ["3702"]
    assert "longest word" in r.note and "Searched by" not in r.note
