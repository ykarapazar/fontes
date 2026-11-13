import asyncio

import pytest

from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions import tm


def _paras():
    toc = [f"*{n}-nji madda. Title {n}*" for n in (1, 2, 3)]
    body = []
    for n in (1, 2, 3):
        body += [f"**{n}-nji madda. Title {n}**", f"Text one of {n}.", f"Text two of {n}."]
    return toc + body


def test_full_text_run_wins_over_bare_heading_list():
    items = [i for i in tm._structure(_paras()) if i["kind"] == "art"]
    assert [i["label"] for i in items[3:]] == ["1", "2", "3"]
    assert [i["label"] for i in items[:3]] == ["1:1", "1:2", "1:3"]


def test_years():
    assert tm._years("2023") == (2023, 2023)
    assert tm._years("2022-2024") == (2022, 2024)
    assert tm._years("2022-") == (2022, 9999)
    assert tm._years("") is None
    for bad in ("2024-2022", "22", "abc"):
        with pytest.raises(BadRequest):
            tm._years(bad)


def _plenum(monkeypatch):
    items = [{"id": f"{y}-01-01/1", "n": 1, "title": "miras", "date": f"{y}-01-01", "number": "1",
              "pages": "1-2", "text": "miras"} for y in (2019, 2022, 2024)]

    async def fake():
        return "u", items
    monkeypatch.setattr(tm, "_plenum_items", fake)


def test_caselaw_year_range_and_russian_note(monkeypatch):
    _plenum(monkeypatch)
    res = asyncio.run(tm.Turkmenistan().search_caselaw("miras", filters={"year": "2022-"}))
    assert [h.date[:4] for h in res.items] == ["2024", "2022"]
    assert "Turkmen only" not in res.note
    res = asyncio.run(tm.Turkmenistan().search_caselaw("наследство"))
    assert res.total == 0 and "Turkmen only" in res.note


def test_decision_note(monkeypatch):
    _plenum(monkeypatch)
    d = asyncio.run(tm.Turkmenistan().get_decision("2024-01-01/1"))
    assert "renumbered" in d.metadata["Note"]
