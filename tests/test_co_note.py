import asyncio

from world_legal_mcp.jurisdictions import co


def test_search_note_says_no_subject_search(monkeypatch):
    async def fake(params):
        return [{"count": "0"}] if "$select" in params else []
    monkeypatch.setattr(co, "_soql", fake)
    res = asyncio.run(co.Colombia().search_caselaw("aborto"))
    assert "NOT a subject or full-text search" in res.note
    assert "C-355/06" in res.note


def test_notes_upfront():
    assert "NOT by subject" in co.Colombia.notes
