import asyncio

from world_legal_mcp.jurisdictions import ca


def test_charter_phrase_resolves_to_1982():
    law = {"secs": {("1867", "7"): "", ("1982", "7"): ""}, "scheds": {}}
    assert ca._const_key("section 7 of the Charter", law) == ("s", "1982", "7")


def test_search_notes(monkeypatch):
    async def idx():
        return [{"id": "B-9.01", "title": "Broadcasting Act", "type": "act", "number": "", "current": ""}]
    monkeypatch.setattr(ca, "_load_index", idx)
    r = asyncio.run(ca._search_legislation("Online Streaming Act", {}, 20, 1))
    assert "French titles" in r.note and "B-9.01" in r.note
    r = asyncio.run(ca._search_legislation("Code criminel", {}, 20, 1))
    assert "French titles" in r.note and "B-9.01" not in r.note
