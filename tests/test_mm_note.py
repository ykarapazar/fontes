import asyncio

from world_legal_mcp.jurisdictions import mm


def test_empty_search_says_major_statutes_not_collected(monkeypatch):
    async def fake_list(kind):
        return []
    monkeypatch.setattr(mm, "_list", fake_list)
    r = asyncio.run(mm.Myanmar().search_legislation("Penal Code", limit=10, page=1, filters={}))
    assert r.total == 0
    assert "Penal Code" in r.note and "NOT in it" in r.note


def test_type_word_matches_amending_laws(monkeypatch):
    async def fake_list(kind):
        return [{"id": "x-ဥပဒေ.pdf", "title": "ပြင်ဆင်ဥပဒေ", "type": kind, "posted": ""}] if kind == "amendment" else []
    monkeypatch.setattr(mm, "_list", fake_list)
    r = asyncio.run(mm.Myanmar().search_legislation("amendment", limit=10, page=1, filters={}))
    assert r.total == 1


def test_english_zero_hit_note_mentions_burmese(monkeypatch):
    async def fake_rcms(path, body):
        return {"total": 0, "results": [], "total_pages": 0}
    monkeypatch.setattr(mm, "_rcms", fake_rcms)
    r = asyncio.run(mm.Myanmar().search_caselaw("bail", limit=5, page=1, filters={"date_from": "2020-01-01"}))
    assert "Burmese" in r.note and "အာမခံ" in r.note
    r = asyncio.run(mm.Myanmar().search_caselaw("အာမခံ", limit=5, page=1, filters={}))
    assert "No match for this English query" not in r.note
