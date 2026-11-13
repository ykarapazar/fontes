import asyncio

from world_legal_mcp.jurisdictions import lu


def test_year_filter_accepts_int():
    assert lu._years_from({"year": 2023}, "") == [2023]


def test_notes_say_case_law_is_cassation_only():
    assert "No case law" not in lu.Luxembourg.notes
    assert "Cour de cassation" in lu.Luxembourg.notes


def test_phrase_rank_in_query(monkeypatch):
    seen = []

    async def fake(q):
        seen.append(q)
        return []

    monkeypatch.setattr(lu, "_sparql", fake)
    asyncio.run(lu.Luxembourg().search_legislation("protection des données", limit=5, page=1, filters={}))
    assert "ORDER BY DESC(?p)" in seen[0] and '"protection des données"' in seen[0]


def _cands(monkeypatch, n):
    ents = [{"stem": f"20240301_CAS-2023-{i:05d}", "date": "2024-03-01", "case": f"CAS-2023-{i:05d}"} for i in range(n)]

    async def res():
        return {2024: ("u", 1)}

    async def entries(y):
        return "u", ents

    monkeypatch.setattr(lu, "_resources", res)
    monkeypatch.setattr(lu, "_entries", entries)


def test_wide_text_search_checks_newest_40_and_flags_incomplete(monkeypatch):
    _cands(monkeypatch, 60)
    opened = []

    async def txt(y, e, url):
        opened.append(e["stem"])
        return "licenciement abusif"

    monkeypatch.setattr(lu, "_pdf_text", txt)
    r = asyncio.run(lu.Luxembourg().search_caselaw(
        "licenciement", limit=5, page=1, filters={"date_from": "2024-03-01"}))
    assert len(opened) == lu._SCAN_MAX and r.total == lu._SCAN_MAX
    assert "INCOMPLETE" in r.note and "60 decisions" in r.note


def test_month_of_25_is_searched(monkeypatch):
    _cands(monkeypatch, 25)

    async def txt(y, e, url):
        return "licenciement abusif" if e["stem"].endswith("00003") else "autre"

    monkeypatch.setattr(lu, "_pdf_text", txt)
    r = asyncio.run(lu.Luxembourg().search_caselaw(
        "licenciement", limit=5, page=1, filters={"date_from": "2024-03-01", "date_to": "2024-03-31"}))
    assert r.total == 1


def test_date_from_alone_reaches_latest_year(monkeypatch):
    seen = []

    async def res():
        return {2023: ("u", 1), 2024: ("u", 1), 2025: ("u", 1)}

    async def entries(y):
        seen.append(y)
        return "u", []

    monkeypatch.setattr(lu, "_resources", res)
    monkeypatch.setattr(lu, "_entries", entries)
    asyncio.run(lu.Luxembourg().search_caselaw("", limit=5, page=1, filters={"date_from": "2023-01-01"}))
    assert sorted(seen) == [2023, 2024, 2025]


def test_snippet_stays_aligned_with_non_ascii_text(monkeypatch):
    _cands(monkeypatch, 1)

    async def txt(y, e, url):
        return "« » ’ " * 60 + "le licenciement abusif " + "x" * 300

    monkeypatch.setattr(lu, "_pdf_text", txt)
    r = asyncio.run(lu.Luxembourg().search_caselaw("licenciement", limit=5, page=1, filters={"year": 2024}))
    assert "licenciement" in r.items[0].snippet


def test_incomplete_note_gives_continuation_count(monkeypatch):
    _cands(monkeypatch, 100)

    async def txt(y, e, url):
        return "licenciement"

    monkeypatch.setattr(lu, "_pdf_text", txt)
    r = asyncio.run(lu.Luxembourg().search_caselaw("licenciement", limit=5, page=1, filters={"year": 2024}))
    assert "about 2 more searches" in r.note
