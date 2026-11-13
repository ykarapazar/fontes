import asyncio

from world_legal_mcp.jurisdictions import hu


def _run(query, filters, monkeypatch, reply=None):
    seen = []

    async def fake(form):
        seen.append(dict(form))
        return reply or {"List": [], "Count": 0}
    monkeypatch.setattr(hu, "_search", fake)
    res = asyncio.run(hu.Hungary().search_caselaw(query, limit=5, page=1, filters=filters))
    return res, seen[0]


def test_case_number_query_uses_azonosito(monkeypatch):
    _, form = _run("Pfv.21761/2017/4", {}, monkeypatch)
    assert form["Azonosito"] == "Pfv.21761/2017/4"
    assert "KeresoSzavak[]" not in form


def test_unaccented_zero_hits_warns(monkeypatch):
    res, _ = _run("felmondas munkaviszony", {}, monkeypatch)
    assert "accents" in res.note


def test_constitutional_court_note(monkeypatch):
    res, _ = _run("alkotmány", {"court": "Alkotmánybíróság"}, monkeypatch)
    assert "not in this collection" in res.note
