import asyncio

from world_legal_mcp.jurisdictions import is_


def _run(monkeypatch, **kw):
    async def fake(q, v):
        return {"webVerdicts": {"total": 1, "items": [
            {"id": "s-AC188192-B55F-45E0-8476-55C7EDD3EDE5", "title": "t", "court": "Hæstiréttur",
             "caseNumber": "1/2023", "verdictDate": "2024-01-01T00:00:00Z", "keywords": [], "presentings": "x"}]}}
    monkeypatch.setattr(is_, "_gql", fake)
    return asyncio.run(is_.Iceland.__new__(is_.Iceland).search_caselaw(**kw))


def test_free_text_gets_loose_match_note(monkeypatch):
    r = _run(monkeypatch, query="húsaleigu", filters={"court": "supreme"})
    assert "keyword" in r.note and "rank" in r.note


def test_filter_only_search_has_no_loose_note(monkeypatch):
    r = _run(monkeypatch, query="", filters={"court": "supreme"})
    assert "rank" not in r.note


def test_keyword_search_warns_keywords_are_broad(monkeypatch):
    r = _run(monkeypatch, query="húsaleigu", filters={"court": "supreme", "keyword": "Húsaleigusamningur"})
    assert "commercial" in r.note and "no residential-only filter" in r.note


def test_hits_mentioning_term_flagged_in_source_order(monkeypatch):
    def row(i, pres):
        return {"id": f"g-{i:08d}-0000-0000-0000-000000000000", "title": "t", "court": "d", "caseNumber": "1/1",
                "verdictDate": "2024-01-01T00:00:00Z", "keywords": [], "presentings": pres}

    async def fake(q, v):
        return {"webVerdicts": {"total": 2, "items": [row(1, "hótel"), row(2, "Ágreiningur um húsaleigu íbúðar")]}}
    monkeypatch.setattr(is_, "_gql", fake)
    r = asyncio.run(is_.Iceland.__new__(is_.Iceland).search_caselaw(
        query="húsaleigu", filters={"court": "supreme"}))
    # source order kept so pages line up; the matching hit is named by its position instead
    assert r.items[0].id.startswith("g-00000001") and "1 of 2" in r.note and "(hits 2)" in r.note


def test_merged_paging_slices_by_offset(monkeypatch):
    """No court filter: both backends fetched from page 1 up to page*limit, merged by date, sliced."""
    calls = []

    def row(court, i):
        pre = "s-%08X-0000-0000-0000-000000000000" if court == "s" else "g-%08x-0000-0000-0000-000000000000"
        return {"id": pre % i, "title": "leigusamningur" if i % 3 == 0 else "x", "court": court, "caseNumber": f"{i}/1",
                "verdictDate": f"2024-01-{31 - i // 2:02d}T00:00:00Z", "keywords": [], "presentings": ""}

    async def fake(q, v):
        inp = v["input"]
        c = "s" if inp["court"] == [is_.SUPREME] else "g"
        calls.append((c, inp["page"], inp["pageSize"]))
        base = (inp["page"] - 1) * 10
        return {"webVerdicts": {"total": 40, "items": [row(c, base + i) for i in range(10)]}}
    monkeypatch.setattr(is_, "_gql", fake)
    j = is_.Iceland.__new__(is_.Iceland)
    big = asyncio.run(j.search_caselaw("leigusamningur", limit=20, page=1))
    calls.clear()
    p2 = asyncio.run(j.search_caselaw("leigusamningur", limit=10, page=2))
    assert [h.id for h in big.items[10:]] == [h.id for h in p2.items]
    assert calls == [("s", 1, 10), ("s", 2, 10), ("g", 1, 10), ("g", 2, 10)]
    assert "(hits 13, 15, 18, 20)" in p2.note and p2.total == 80


def test_note_says_when_no_hit_mentions_term(monkeypatch):
    r = _run(monkeypatch, query="húsaleigu", filters={"court": "supreme"})
    assert "none of the 1 hits" in r.note


def test_keyword_only_search_gets_keyword_note(monkeypatch):
    r = _run(monkeypatch, query="", filters={"court": "supreme", "keyword": "Húsaleigusamningur"})
    assert "commercial" in r.note and "no such ruling" in r.note


def test_no_confirmed_match_leads_the_note(monkeypatch):
    r = _run(monkeypatch, query="húsaleigu", filters={"court": "supreme"})
    assert r.note.startswith("NO CONFIRMED MATCH")
