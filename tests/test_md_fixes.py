import asyncio
from types import SimpleNamespace

import pytest

from world_legal_mcp import _http
from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions import md

ROW = ('<table class="views-table"><tbody><tr>'
       '<td class="views-field-solr-document-5">Judecătoria Cahul</td>'
       '<td class="views-field-Numarul-dosarului">2-1</td>'
       '<td class="views-field-solr-document-1">2999-12-31</td>'
       '<td class="views-field-nothing"><a href="/pdf/F0FD4EC1-AFAE-4ABF-AC50-5493EBCEFF7D">x</a></td>'
       '</tr></tbody></table>Rezultate: <b>1</b>')


def test_future_date_dropped(monkeypatch):
    async def get(url, **k):
        return SimpleNamespace(status_code=200, text=ROW)
    monkeypatch.setattr(_http, "get", get)
    items, _ = asyncio.run(md.Moldova()._lower_page({}))
    assert items[0].date == md._FUTURE


def test_future_date_read_from_pdf(monkeypatch):
    async def get(url, **k):
        return SimpleNamespace(status_code=200, text=ROW)
    async def pdf(url, what):
        return "Dosarul nr. 2-1\n31 decembrie 2025\n"
    monkeypatch.setattr(_http, "get", get)
    monkeypatch.setattr(md, "_pdf", pdf)
    monkeypatch.setattr(md, "_head", lambda t: ("2-1", "2025-12-31"))
    res = asyncio.run(md.Moldova()._search_lower("x", 3, 1, {}))
    assert res.items[0].date == "2025-12-31"


def test_lower_date_filter_message():
    with pytest.raises(BadRequest, match="no date search"):
        asyncio.run(md.Moldova().search_caselaw("x", limit=3, page=1, filters={
            "court": "lower", "date_from": "2022-01-01"}))


def _csj(monkeypatch, rows):
    sent = {}
    async def post(url, data=None, **k):
        sent.update(data)
        return SimpleNamespace(status_code=200, json=lambda: {"page": 1, "rows": rows})
    monkeypatch.setattr(_http, "post", post)
    return sent


def test_college_alone_is_a_filter_and_zero_hits_say_so(monkeypatch):
    sent = _csj(monkeypatch, [])
    res = asyncio.run(md.Moldova().search_caselaw("", limit=3, page=1, filters={
        "court": "csj", "college": "penal"}))
    assert sent["_search"] == "false" and res.total == 0 and "subject field" in res.note


def test_no_filter_still_refused():
    with pytest.raises(BadRequest):
        asyncio.run(md.Moldova().search_caselaw("", limit=3, page=1, filters={"court": "csj"}))


def test_lower_note_explains_blank_date_and_points_to_get_decision(monkeypatch):
    async def get(url, **k):
        return SimpleNamespace(status_code=200, text=ROW)
    monkeypatch.setattr(_http, "get", get)
    res = asyncio.run(md.Moldova().search_caselaw("divorț", filters={"court": "lower"}, limit=1, page=1))
    assert "get_decision" in res.note and "future" in res.note


def test_lower_note_says_case_number_is_portal_internal(monkeypatch):
    async def get(url, **k):
        return SimpleNamespace(status_code=200, text=ROW.replace("2999-12-31", "2025-01-01"))
    monkeypatch.setattr(_http, "get", get)
    res = asyncio.run(md.Moldova()._search_lower("divorț", limit=1, page=1, filters={}))
    assert "internal number" in res.note and "get_decision" in res.note
