import asyncio

from world_legal_mcp.jurisdictions import wto

D = {
    "cases": {
        332: {"code": "DS332", "title": "Brazil - Retreaded Tyres", "start_date": "2005/06/20"},
        623: {"code": "DS623", "title": "US - IRA", "start_date": "2024/03/26", "status": "S1#2026_02_23"},
    },
    "status": {"S1": "Panel report under appeal"}, "subject": {},
}


def _search(monkeypatch, q, **f):
    async def load():
        return D
    monkeypatch.setattr(wto, "_load", load)
    monkeypatch.setattr(wto, "_members", lambda *a: [])
    monkeypatch.setattr(wto, "_agreements", lambda *a: [])
    return asyncio.run(wto.WTO().search_caselaw(q, filters=f or None))


def test_dead_words_named(monkeypatch):
    r = _search(monkeypatch, "Appellate Body report tyres retreaded Brazil")
    assert r.total == 0
    assert "'appellate'" in r.note and "'report'" in r.note and "'tyres'" not in r.note


def test_appeal_status_note(monkeypatch):
    r = _search(monkeypatch, "", status="appeal")
    assert r.total == 1 and "not indexed" in r.note


def test_agreement_texts_pointer():
    j = wto.WTO()
    assert "legal_e.htm" in j.notes
    assert any("Anti-Dumping" in g for g in j.gaps)
