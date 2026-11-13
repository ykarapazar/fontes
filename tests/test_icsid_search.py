import asyncio

from world_legal_mcp.jurisdictions import icsid

ROWS = [
    {"caseno": "ARB/26/38", "claimant": "Petersen", "respondent": "Argentine Republic ",
     "status": "Pending", "caseproceedings": [{"dateregistered": "3/1/2026 12:00:00 AM"}]},
    {"caseno": "ARB/03/17", "claimant": "TSA Spectrum de Argentina", "respondent": "Argentine Republic",
     "status": "Concluded", "caseproceedings": [{"dateregistered": "1/1/2003 12:00:00 AM"}]},
    {"caseno": "ARB/10/7", "claimant": "Philip Morris", "respondent": "Oriental Republic of Uruguay",
     "status": "Concluded", "caseproceedings": [{"dateregistered": "3/1/2010 12:00:00 AM"}]},
]


def _run(monkeypatch, query, filters=None):
    async def fake():
        return ROWS
    monkeypatch.setattr(icsid, "_cases", fake)
    return asyncio.run(icsid.ICSID().search_caselaw(query, filters=filters)) if hasattr(icsid, "ICSID") else None


def test_short_name_matches_formal_style(monkeypatch):
    r = _run(monkeypatch, "Argentina")
    assert r.total == 2 and "argentine republic" in r.note


def test_respondent_filter_and_dates(monkeypatch):
    r = _run(monkeypatch, "", {"respondent": "Argentina", "date_from": "2022-01-01"})
    assert [i.id for i in r.items] == ["ARB/26/38"]


def test_note_explains_subject_not_searchable(monkeypatch):
    r = _run(monkeypatch, "annulment")
    assert r.total == 0 and "annulment" in r.note and "not that no such case exists" in r.note
