import asyncio

from world_legal_mcp.jurisdictions import ch


def _run(monkeypatch, rows, q="Strafgesetzbuch"):
    seen = {}

    async def fake(query):
        seen["q"] = query
        return rows
    monkeypatch.setattr(ch, "_sparql", fake)
    res = asyncio.run(ch.Switzerland().search_legislation(q, limit=5, page=1, filters={}))
    return res, seen["q"]


def _row(cc, sr, status):
    return {"cc": cc, "sr": sr, "title": "T", "abbr": "", "status": status, "date": "", "typ": ""}


def test_exact_phrase_ranks_before_scattered_words(monkeypatch):
    _, q = _run(monkeypatch, [], "Constitution fédérale")
    order = q.split("ORDER BY")[1]
    assert 'CONTAINS(LCASE(STR(?title)), "constitution fédérale")' in order


def test_reused_sr_number_is_flagged(monkeypatch):
    res, _ = _run(monkeypatch, [_row("a", "311.01", "In Kraft"), _row("b", "311.01", "Nicht mehr in Kraft")])
    assert "311.01" in res.note and "more than once" in res.note


def test_no_flag_without_duplicates(monkeypatch):
    res, _ = _run(monkeypatch, [_row("a", "210", "In Kraft")])
    assert "more than once" not in res.note
