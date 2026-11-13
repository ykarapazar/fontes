import asyncio

from world_legal_mcp.jurisdictions import ly

RULINGS = [
    {"id": "a", "title": "مدني 1/70ق: الفصل من العمل", "case": "1/70ق", "brief": "الفصل من العمل", "tags": [],
     "sections": [], "chamber": ly.CHAMBERS["civil"], "court": "c", "date": "2023-05-01", "url": "u"},
    {"id": "b", "title": "مدني 2/70ق: الإثبات", "case": "2/70ق", "brief": "الإثبات", "tags": [],
     "sections": [("", "الفصل في الدعوى من العمل")], "chamber": ly.CHAMBERS["civil"], "court": "c",
     "date": "2021-05-01", "url": "u"},
]


def _search(monkeypatch, query, filters=None):
    async def rulings():
        return RULINGS
    monkeypatch.setattr(ly, "_rulings", rulings)
    return asyncio.run(ly.Libya().search_caselaw(query, filters=filters))


def test_title_hits_first_and_body_only_warning(monkeypatch):
    r = _search(monkeypatch, "الفصل من العمل")
    assert [h.id for h in r.items] == ["a", "b"]
    assert "body text" not in r.note
    r = _search(monkeypatch, "الفصل من العمل", {"date_to": "2022"})
    assert [h.id for h in r.items] == ["b"] and "only somewhere in the body text" in r.note


def test_date_filters(monkeypatch):
    assert [h.id for h in _search(monkeypatch, "العمل", {"date_from": "2022-01-01"}).items] == ["a"]
    assert [h.id for h in _search(monkeypatch, "العمل", {"date_to": "2021-12-31"}).items] == ["b"]
    assert "date_from" in ly.Libya.caselaw_filters


def test_journal_year_note_says_query_ignored(monkeypatch):
    async def journals():
        return [{"uuid": "u1", "judicial_year": 45, "number": "1", "is_available": False}]
    monkeypatch.setattr(ly, "_journals", journals)
    r = asyncio.run(ly.Libya().search_caselaw("الإيجار", filters={"journal_year": "45"}))
    assert "NOT a text match" in r.note and "ignored" in r.note and "not online" in r.note


def test_missing_codes_listed():
    assert any("Constitutional Declaration" in g for g in ly.Libya.gaps)


def test_legislation_title_matches_first(monkeypatch):
    def row(i, title):
        return {"id": i, "title": {"rendered": title}, "categories": [83], "excerpt": {"rendered": ""}}
    rows = [row(1, "قانون بشأن الأنشطة"), row(2, "موسوعة (قانون المرافعات المدنية والتجارية)")]

    class R:
        status_code, headers, text = 200, {"content-type": "application/json", "x-wp-totalpages": "1"}, ""

        def json(self):
            return rows

    async def get(*a, **k):
        return R()
    monkeypatch.setattr(ly._http, "get", get)
    r = asyncio.run(ly.Libya().search_legislation("المرافعات المدنية والتجارية"))
    assert [h.id for h in r.items] == ["2", "1"] and r.total == 2
    assert "journal_year" not in r.note
