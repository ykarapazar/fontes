import asyncio
import json

import pytest

from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions import am
from world_legal_mcp.jurisdictions.am import Armenia as Adapter


def test_date_range_goes_into_form():
    form = am._base_form("x", {"date_from": "2022-01-01"}, True)
    assert json.loads(form["enactment_date"]) == {"start": "2022-01-01", "end": ""}


@pytest.mark.parametrize("d", ["2022", "01.01.2022"])
def test_bad_date_rejected(d):
    with pytest.raises(BadRequest, match="YYYY-MM-DD"):
        am._base_form("x", {"date_to": d}, True)


def test_sort():
    assert am._order({"sort": "newest"}) == "enactment_date DESC"
    assert am._order({}) == ""
    with pytest.raises(BadRequest):
        am._order({"sort": "x"})


def test_order_reaches_source(monkeypatch):
    seen = {}

    async def fake(form, page, order=""):
        seen["order"] = order
        return [{"id": "1", "title": "t"}], 1
    monkeypatch.setattr(am, "_search_page", fake)
    r = asyncio.run(Adapter.__new__(Adapter).search_caselaw("x", filters={"sort": "newest"}))
    assert seen["order"] == "enactment_date DESC" and "oldest first" not in r.note


def test_legislation_status_note(monkeypatch):
    async def fake(form, page, order=""):
        return [{"id": "1", "title": "t", "Կարգավիճակ": "Գործում է"}], 1
    monkeypatch.setattr(am, "_search_page", fake)
    r = asyncio.run(Adapter.__new__(Adapter).search_legislation("x"))
    assert "replaced" in r.note


def test_old_constitution_marked_superseded(monkeypatch):
    async def fake(form, page, order=""):
        return [{"id": "1", "title": "t", "Կարգավիճակ": "Գործում է"},
                {"id": "143723", "title": "t", "Կարգավիճակ": "Գործում է"}], 2
    monkeypatch.setattr(am, "_search_page", fake)
    r = asyncio.run(Adapter.__new__(Adapter).search_legislation("x", filters={"status": "any"}))
    assert "superseded" in r.items[0].status and "superseded" not in r.items[1].status


def test_duplicate_article_number_noted(monkeypatch):
    paras = ["**Հոդված 1.** a", "**Հոդված 1.** b"]
    ents, spans = am._structure(paras)
    doc = {"id": "9", "title": "T", "url": "u", "paras": paras, "spans": spans, "status": ""}

    async def fake(num):
        return doc
    monkeypatch.setattr(am, "_doc", fake)
    p = asyncio.run(Adapter.__new__(Adapter).get_legislation_provision("9", "1"))
    assert "Հոդված 1 (2)" in p.text


def test_constitution_bare_article_resolves_to_2015_text():
    doc = {"id": "143723", "title": "T",
           "spans": {"Հոդված 1": (0, 1), "Հոդված 1 (2)": (1, 2)}}
    assert am._find_label(doc, "1") == "Հոդված 1 (2)"
    assert am._find_label(doc, "Հոդված 1") == "Հոդված 1 (2)"
    assert am._find_label(doc, "1 (2)") == "Հոդված 1 (2)"
    other = {"id": "5", "title": "T", "spans": {"Հոդված 1": (0, 1), "Հոդված 1 (2)": (1, 2)}}
    assert am._find_label(other, "1") == "Հոդված 1"


def test_in_force_search_drops_old_constitutions(monkeypatch):
    seen = {}

    async def fake(form, limit, page, order=""):
        seen.update(form)
        if form.get("simple_text") == "Աշխատանք":
            return [{"id": "29", "title": "C"}], 1
        return [{"id": "1", "title": "A"}, {"id": "143723", "title": "B"}], 2

    monkeypatch.setattr(am, "_search", fake)
    r = asyncio.run(Adapter().search_legislation("Սահմանադրություն", filters={"status": "in_force"}))
    assert [h.id for h in r.items] == ["143723"] and seen["status"] == "1"
    r = asyncio.run(Adapter().search_legislation("Աշխատանք", filters={}))
    assert seen["status"] == "1" and "Constitution" not in r.note
    seen.clear()
    asyncio.run(Adapter().search_legislation("Աշխատանք", filters={"status": "any"}))
    assert "status" not in seen
