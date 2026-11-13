import asyncio

from world_legal_mcp.jurisdictions import afchpr


def _run(coro):
    return asyncio.run(coro)


def test_advisory_date_filter_uses_received_for_pending(monkeypatch):
    rows = [
        {"id": "AO 001/2024", "title": "t", "received": "2024-10-10", "decided": "", "status": "Pending"},
        {"id": "AO 001/2021", "title": "t", "received": "2020-01-01", "decided": "2021-07-16", "status": "Finalised"},
    ]

    async def fake():
        return rows
    monkeypatch.setattr(afchpr, "_advisory_rows", fake)
    j = afchpr.AfCHPR()
    r = _run(j.search_caselaw("", filters={"kind": "advisory", "date_from": "2024-01-01"}))
    assert [h.id for h in r.items] == ["AO 001/2024"]
    r = _run(j.search_caselaw("", filters={"kind": "advisory", "date_to": "2024-12-31"}))
    assert {h.id for h in r.items} == {"AO 001/2024", "AO 001/2021"}


def test_pending_date_filter_is_applied_on_reception_date(monkeypatch):
    seen = []

    async def fake(params):
        seen.append(params)
        rows = [{"case_number": f"00{i}/2026", "reception_date": d, "case_status": {"en_title": "Pending"}}
                for i, d in ((2, "2026-03-05"), (1, "2025-06-01"))]
        return {"total": 2, "rows": rows}
    monkeypatch.setattr(afchpr, "_api", fake)
    r = _run(afchpr.AfCHPR().search_caselaw("", filters={"status": "pending", "date_from": "2026-01-01"}))
    assert [h.id for h in r.items] == ["002/2026"]
    assert r.total == 1
    assert "from_date" not in seen[0]


def test_gaps_point_to_treaty_text():
    assert any("au.int/en/treaties/african-charter" in g for g in afchpr.AfCHPR.gaps)


def test_empty_search_explains_names_are_not_matched(monkeypatch):
    async def fake(params):
        return {"rows": [], "total": 0}
    monkeypatch.setattr(afchpr, "_api", fake)
    r = _run(afchpr.AfCHPR().search_caselaw("Ogiek"))
    assert "006/2012" in r.note and "Matches application number" in r.note


def test_rules_of_court_listed_as_gap():
    assert any("Rules of Court" in g for g in afchpr.AfCHPR.gaps)


def test_legislation_refusal_names_treaty_and_rules_sources():
    from world_legal_mcp import server
    msg = server._unsupported(afchpr.AfCHPR(), "search_legislation")
    first = msg.splitlines()[0]
    assert "au.int/en/treaties/african-charter-human-and-peoples-rights" in first
    assert "african-court.org" in first
