import asyncio

from world_legal_mcp.jurisdictions import ht


def test_search_note_says_codes_and_nationality_absent(monkeypatch):
    async def lib():
        return []
    monkeypatch.setattr(ht, "_library", lib)
    r = asyncio.run(ht.Haiti().search_legislation("code pénal", limit=20, page=1, filters={}))
    assert "Penal Code" in r.note and "nationality law" in r.note and "NOT" in r.note


def test_warning_does_not_claim_nationality_law():
    w = ht.Haiti.sources[0].warning
    assert "no nationality law" in w
