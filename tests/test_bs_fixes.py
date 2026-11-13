import asyncio

import pytest

from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions import bs
from world_legal_mcp.models import DecisionHit


def _sc(monkeypatch):
    rows = [{"path": f"{y}/01/a.pdf", "title": f"A v B {y}", "name": f"A v B {y}", "number": "", "judge": "",
             "date": f"{y}-01-01", "pdf": ""} for y in (2019, 2021, 2022, 2024)]

    async def fake():
        return rows
    monkeypatch.setattr(bs, "_sc_rows", fake)


def _search(year, monkeypatch):
    _sc(monkeypatch)
    return asyncio.run(bs.Bahamas().search_caselaw("", limit=10, filters={"court": "sc", "year": year}))


def test_year_range(monkeypatch):
    assert [h.date[:4] for h in _search("2021-2022", monkeypatch).items] == ["2022", "2021"]


def test_year_open_ended_and_single(monkeypatch):
    assert [h.date[:4] for h in _search("2022-", monkeypatch).items] == ["2024", "2022"]
    assert [h.date[:4] for h in _search("2021", monkeypatch).items] == ["2021"]


def test_year_backwards(monkeypatch):
    with pytest.raises(BadRequest):
        _search("2024-2020", monkeypatch)


def test_amending_act_link_parsed(monkeypatch):
    page = (b'<table><tr><td class="hasTip amd"><a href="/cms/images/LEGISLATION/AMENDING/2024/2024-0007A/'
            b'2024-0007A.pdf" target="_blank">amended by... Penal Code (Amendment) Act, 2024&nbsp;</a></td></tr></table>')

    class R:
        status_code = 200
        content = page

    async def fake_post(*a, **k):
        return R()
    monkeypatch.setattr(bs._http, "post", fake_post)
    bs._cache.clear()
    rows = asyncio.run(bs._letter("P"))
    assert rows[0]["folder"] == "AMENDING" and rows[0]["item"] == "2024-0007"


def test_garbled_text_detected_and_warned(monkeypatch):
    bad = "#1& %his Act' (hich amends the enal ode # Ch. 84 &' ma) *e cited as the enal ode" * 5
    assert bs._garbled(bad)
    assert not bs._garbled("This Act may be cited as the Penal Code (Amendment) Act, 2024. " * 5)
    law = {"id": "amd/x", "title": "T", "url": "u", "toc": [], "sections": {"1": "garbage"},
           "text": bad, "meta": {}, "garbled": True}

    async def fake(i):
        return law
    monkeypatch.setattr(bs, "_law", fake)
    p = asyncio.run(bs.Bahamas().get_legislation_provision("amd/x", "1"))
    assert p.text.startswith("WARNING") and "garbled" in p.text
    assert "garbled" in asyncio.run(bs.Bahamas().get_legislation_text("amd/x")).text


def test_constitution_subject_first(monkeypatch):
    names = ["Bahamas Constitution Party v X", "In re Article 28 of the Constitution of The Bahamas",
             "Union of Teachers Constitution application"]
    rows = [{"path": f"{i}/a.pdf", "title": n, "name": n, "number": "", "judge": "",
             "date": f"202{i}-01-01", "pdf": ""} for i, n in enumerate(names)]

    async def fake():
        return rows
    monkeypatch.setattr(bs, "_sc_rows", fake)
    r = asyncio.run(bs.Bahamas().search_caselaw("constitution", filters={"court": "sc"}))
    assert r.items[0].title.startswith("In re Article 28")
    assert "within each of the two groups" in r.note
