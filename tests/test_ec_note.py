import asyncio

from world_legal_mcp.jurisdictions import ec


def test_search_caselaw_notes_coverage(monkeypatch):
    async def fake_api(path, crit):
        return {"dato": [], "totalFilas": 0}

    monkeypatch.setattr(ec, "_api", fake_api)
    r = asyncio.run(ec.Ecuador().search_caselaw("Corte Nacional de Justicia"))
    assert "Only the Corte Constitucional" in r.note
    assert "NOT Corte Nacional" in r.note
    r = asyncio.run(ec.Ecuador().search_caselaw("habeas corpus"))
    assert "NOT Corte Nacional" not in r.note
