import asyncio
from types import SimpleNamespace

import pytest

from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions import ro


def _page(first, count, last_start=None):
    rows = "".join(
        f'<tr><td><a href="legis_pck.htp_act?ida={n}">L. nr.{n}/01-01-2025</a> LEGE {n}</td>'
        f"<td>x</td><td>V</td></tr>" for n in range(first, first + count))
    links = f'<a href="legis_pck.rezultate?nrc={last_start}">x</a>' if last_start else ""
    return f"<html><body><table>{rows}</table>{links}</body></html>"


def _run(monkeypatch, filters, page=1, limit=3):
    # 250 hits in the source, 100 rows per source page: nrc 1, 101, 201 (50 rows)
    async def post(url, data=None, **kw):
        n = int(data["nrc"])
        body = _page(n, min(100, 250 - n + 1), last_start=201)
        return SimpleNamespace(status_code=200, content=body.encode())
    monkeypatch.setattr(ro._http, "post", post)
    return asyncio.run(ro.Romania().search_legislation("", limit=limit, page=page, filters=filters))


def test_newest_first(monkeypatch):
    r = _run(monkeypatch, {"year": "2025", "order": "newest"})
    assert r.total == 250
    assert [h.id for h in r.items] == ["250", "249", "248"]
    assert "newest first" in r.note and "Contents" in r.note


def test_newest_page_two(monkeypatch):
    assert [h.id for h in _run(monkeypatch, {"year": "2025", "order": "newest"}, page=2).items] == \
        ["247", "246", "245"]


def test_default_oldest_and_note(monkeypatch):
    r = _run(monkeypatch, {"year": "2025"})
    assert [h.id for h in r.items] == ["1", "2", "3"]
    assert "oldest first" in r.note and "single year" in r.note


def test_bad_order(monkeypatch):
    with pytest.raises(BadRequest):
        _run(monkeypatch, {"year": "2025", "order": "x"})


def test_hit_without_text_says_so_and_hint(monkeypatch):
    async def post(url, data=None, **kw):
        return SimpleNamespace(status_code=200, content=_page(1, 2).encode())
    monkeypatch.setattr(ro._http, "post", post)
    s = ro.Romania().search_legislation
    r = asyncio.run(s("Codul civil", limit=3, page=1, filters={}))
    assert all("index entry only" in h.snippet for h in r.items)
    assert "ranked" in r.note
    r = asyncio.run(s("Codul civil", limit=3, page=1, filters={"number": "287"}))
    assert "number 287, year 2009" not in r.note


def test_typed_title_search_puts_main_law_first(monkeypatch):
    titles = ["LEGE pentru modificarea Legii nr. 287/2009 privind Codul civil",
              "LEGE privind Codul civil", "LEGE privind Codul fiscal"]
    rows = "".join(f'<tr><td><a href="legis_pck.htp_act?ida={i}">L. nr.{i}/01-01-2025</a> {t}</td>'
                   "<td>x</td><td>V</td></tr>" for i, t in enumerate(titles, 1))

    async def post(url, data=None, **kw):
        return SimpleNamespace(status_code=200, content=f"<table>{rows}</table>".encode())
    monkeypatch.setattr(ro._http, "post", post)
    r = asyncio.run(ro.Romania().search_legislation(
        "Codul civil", limit=3, page=1, filters={"type": "lege", "match": "exact"}))
    assert [h.id for h in r.items] == ["2", "1", "3"]
    assert "title matches ranked" in r.note
    r = asyncio.run(ro.Romania().search_legislation(
        "Codul civil", limit=3, page=1, filters={"type": "lege", "in_text": "true"}))
    assert "by date, not by relevance" in r.note


def test_name_search_ranks_main_law_across_types(monkeypatch):
    seen = []

    async def post(url, data=None, **kw):
        seen.append(data["tip"])
        main = '<tr><td><a href="legis_pck.htp_act?ida=9">L. nr.287/17-07-2009</a> LEGE privind Codul civil</td><td>x</td><td>V</td></tr>'
        amend = '<tr><td><a href="legis_pck.htp_act?ida=1">L. nr.5/01-01-1950</a> LEGE pentru modificarea Codului civil</td><td>x</td><td>V</td></tr>'
        body = f"<html><body><table>{amend}{main if data['tip'] == '1' else ''}</table></body></html>"
        return SimpleNamespace(status_code=200, content=body.encode())
    monkeypatch.setattr(ro._http, "post", post)
    r = asyncio.run(ro.Romania().search_legislation("Codul civil", limit=2, page=1, filters={}))
    assert seen == ["1", "18", "13"]
    assert r.items[0].id == "9" and "ranked" in r.note


def test_in_text_ranks_by_stem_and_supported_notes():
    titles = {1: "HOTĂRÂRE privind Posta", 2: "LEGE pentru modificarea Legii privind protecţia consumatorilor",
              3: "LEGE privind Codul consumului"}

    async def post(url, data=None, **kw):
        rows = "".join(
            f'<tr><td><a href="legis_pck.htp_act?ida={n}">L. nr.{n}/01-01-2025</a> {t}</td>'
            f"<td>x</td><td>V</td></tr>" for n, t in titles.items())
        return SimpleNamespace(status_code=200, content=f"<table>{rows}</table>".encode())
    ro._http.post, old = post, ro._http.post
    try:
        r = asyncio.run(ro.Romania().search_legislation(
            "protectia consumatorilor", limit=3, page=1, filters={"in_text": "true", "match": "exact"}))
    finally:
        ro._http.post = old
    assert r.items[0].id == "3"
    sup = ro.Romania().supported()
    assert "get_legislation_text (Constitution only)" in sup and "get_decision" in sup
