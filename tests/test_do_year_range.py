import asyncio

import pytest

from world_legal_mcp.base import BadRequest
from world_legal_mcp.models import DecisionHit
from world_legal_mcp.jurisdictions import do_


def _run(year, monkeypatch, query=""):
    async def fake(q, y, pos):
        return [DecisionHit(id=f"TSE/0001/{y}", title="t", court="c", date="", case_number="", snippet="", url="u")], False
    monkeypatch.setattr(do_, "_list", fake)
    return asyncio.run(do_.DominicanRepublic().search_caselaw(query, limit=10, filters={"year": year}))


def test_range_newest_first(monkeypatch):
    res = _run("2022-2024", monkeypatch)
    assert [h.id[-4:] for h in res.items] == ["2024", "2023", "2022"]
    assert res.total == 3


def test_note_says_subject_search_unsupported(monkeypatch):
    assert "SUBJECT SEARCH NOT SUPPORTED" in _run("2022", monkeypatch, "recurso de casación").note


def test_bad_year(monkeypatch):
    with pytest.raises(BadRequest):
        _run("2019", monkeypatch)


def test_duplicate_listing_flagged(monkeypatch):
    rows = "".join(f"<tr><td>11 Oct 2022</td><td>TSE-09-0002-2022</td><td>Recurso x</td>"
                   f"<td><a href='https://v/documento/{u}'>TSE/0014/2022</a></td></tr>" for u in ("a", "b"))
    page = f"<html><form id='filter'></form><table><tbody>{rows}</tbody></table></html>".encode()

    async def fake(url):
        return page
    monkeypatch.setattr(do_, "_fetch", fake)
    hits, _ = asyncio.run(do_._list("", "2022", 1))
    assert "Duplicate listing" not in hits[0].snippet and "Duplicate listing" in hits[1].snippet
    assert do_._hits["TSE/0014/2022"][0].url.endswith("/a")


def test_note_warns_some_entries_are_summary_only(monkeypatch):
    assert "síntesis" in _run("2022", monkeypatch).note


def test_multi_word_query_is_anded_locally(monkeypatch):
    sent = []

    async def fake(q, y, pos):
        sent.append(q)
        return [DecisionHit(id="TSE/0001/2024", title="t", court="c", date="", case_number="",
                            snippet="la impugnación de la resolución", url="u"),
                DecisionHit(id="TSE/0002/2024", title="t", court="c", date="", case_number="",
                            snippet="recurso de apelación", url="u")], False
    monkeypatch.setattr(do_, "_list", fake)
    res = asyncio.run(do_.DominicanRepublic().search_caselaw("impugnacion resolución", limit=10))
    assert sent == ["impugnacion"] or sent == ["resolución"]
    assert [h.id for h in res.items] == ["TSE/0001/2024"]


def test_notes_lead_with_legislation_pointer():
    assert do_.DominicanRepublic.notes.startswith("NO LEGISLATION TEXT")
    assert "consultoria.gov.do" in do_.DominicanRepublic.notes
