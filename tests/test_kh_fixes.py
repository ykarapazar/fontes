import asyncio

from world_legal_mcp.jurisdictions import kh


def _items():
    def it(id, title, date=""):
        return {"id": id, "title": title, "category": "Business", "date": date, "url": kh.UPLOADS + id,
                "khmer": False}
    return [it("2022/04/a.pdf", "Labor Law", "1997-03-13"),
            it("2022/05/LAW-MARKS_020207-.pdf", "Law on Marks", "2002-02-07"),
            it("2022/05/b.pdf", "Law on Taxation", "2021-06-01"),
            it("2022/05/c.pdf", "Law on Civil Code Implementation")]


def _search(monkeypatch, q, **f):
    async def fake():
        return _items()
    monkeypatch.setattr(kh, "_list", fake)
    return asyncio.run(kh.Cambodia().search_legislation(q, limit=20, page=1, filters=f))


def test_labour_spelling(monkeypatch):
    assert [h.title for h in _search(monkeypatch, "Labour Law").items] == ["Labor Law"]


def test_year_word_does_not_match_inside_digits(monkeypatch):
    assert _search(monkeypatch, "2020").total == 0


def test_date_from(monkeypatch):
    r = _search(monkeypatch, "", date_from="2020")
    assert [h.title for h in r.items] == ["Law on Taxation"] and "undated" in r.note


def test_code_notes(monkeypatch):
    assert "Civil Code itself is not" in _search(monkeypatch, "Civil Code").note
    assert "Criminal" in _search(monkeypatch, "Penal").note


def test_criminal_code_listed_as_not_covered():
    assert any("Criminal Code" in g for g in kh.Cambodia.gaps)
