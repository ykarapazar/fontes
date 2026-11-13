import asyncio

from world_legal_mcp.jurisdictions import np


def test_note_states_scope_and_ordering(monkeypatch):
    async def fake(params, offset):
        return [], 0

    monkeypatch.setattr(np, "_search_page", fake)
    r = asyncio.run(np.Nepal().search_caselaw("गोपनीयता", limit=5, page=1, filters={}))
    assert "High Court" in r.note and "not by relevance" in r.note


def test_rerank_by_headnote(monkeypatch):
    def h(i, snip):
        return np.DecisionHit(id=str(i), title="t", court="c", date="", snippet=snip, url="u")

    async def fake(params, offset):
        return [h(1, "चोरी"), h(2, "गोपनीयताको हक उल्लङ्घन")], 2

    monkeypatch.setattr(np, "_search_page", fake)
    r = asyncio.run(np.Nepal().search_caselaw("गोपनीयताको हक", limit=5, page=1, filters={}))
    assert [x.id for x in r.items] == ["2", "1"] and "1 do" in r.note
    r = asyncio.run(np.Nepal().search_caselaw("नदेखिने शब्द", limit=5, page=1, filters={}))
    assert "None of the first 2" in r.note


def test_phrase_beats_single_word_and_zero_hit_hint(monkeypatch):
    def h(i, snip):
        return np.DecisionHit(id=str(i), title="t", court="c", date="", snippet=snip, url="u")

    async def fake(params, offset):
        return [h(1, "हक हक हक हक"), h(2, "गोपनीयताको हक")], 2

    monkeypatch.setattr(np, "_search_page", fake)
    r = asyncio.run(np.Nepal().search_caselaw("गोपनीयताको हक", limit=5, page=1, filters={}))
    assert [x.id for x in r.items] == ["2", "1"]

    async def none(params, offset):
        return [], 0

    monkeypatch.setattr(np, "_search_page", none)
    r = asyncio.run(np.Nepal().search_caselaw("निजताको हक", limit=5, page=1, filters={}))
    assert "गोपनीयता" in r.note and "re-ranked" not in r.note


def test_rare_query_word_outweighs_common_ones(monkeypatch):
    def h(i, snip):
        return np.DecisionHit(id=str(i), title="t", court="c", date="", snippet=snip, url="u")

    async def fake(params, offset):
        return [h(1, "संविधानको धारा १६८ संविधानको धारा २८ २८"), h(2, "संविधानको धारा १३२"),
                h(3, "संविधानको धारा २८ गोपनीयता"), h(4, "संविधानको धारा ८८")], 4

    monkeypatch.setattr(np, "_search_page", fake)
    r = asyncio.run(np.Nepal().search_caselaw("संविधानको धारा २८ गोपनीयता", limit=5, page=1, filters={}))
    assert r.items[0].id == "3"
