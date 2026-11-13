import asyncio

from world_legal_mcp.jurisdictions import uz


def test_filter_note(monkeypatch):
    async def fake(kind, params, *, limit, page):
        return [], 0
    monkeypatch.setattr(uz, "_search", fake)
    r = asyncio.run(uz.Uzbekistan().search_caselaw("приговор", filters={"branch": "criminal"}))
    assert "ONLY" in r.note and "2016" in r.note and "without the filter" in r.note
    r = asyncio.run(uz.Uzbekistan().search_caselaw("приговор"))
    assert "ONLY" not in r.note


def test_toc_without_entries(monkeypatch):
    async def fake(did):
        return {"id": did, "title": "T", "url": "u", "entries": []}
    monkeypatch.setattr(uz, "_doc", fake)
    t = asyncio.run(uz.Uzbekistan().get_legislation_toc("8549958"))
    assert t.entries and "no articles" in t.entries[0].title


def test_filter_falls_back_to_court_name(monkeypatch):
    async def fake(kind, params, *, limit, page):
        if "court_form" in params or "instance" in params:
            return [], 0
        return [{"id": "6182601", "title": "Приговор от имени Республики Узбекистан",
                 "badge": "Приговор Сергелинского районного суда города Ташкента, от 26.08.2020 г.",
                 "status": ""},
                {"id": "1", "title": "x", "badge": "Постановление Пленума, от 01.01.2020 г. № 1",
                 "status": ""}], 2
    monkeypatch.setattr(uz, "_search", fake)
    for f in ({"branch": "criminal"}, {"instance": "first"}):
        r = asyncio.run(uz.Uzbekistan().search_caselaw("приговор", filters=f))
        assert [i.id for i in r.items] == ["6182601"] and "matched by court name" in r.note


def test_title_search_drops_generic_words(monkeypatch):
    seen = []

    async def fake(kind, params, *, limit, page):
        seen.append(params["searchtitle"])
        if params["searchtitle"] == "персональных данных":
            return [{"id": "1", "title": "О персональных данных",
                     "badge": "Закон Республики Узбекистан, от 02.07.2019 г. № ЗРУ-547",
                     "status": ""}], 1
        return [], 0
    monkeypatch.setattr(uz, "_search", fake)
    r = asyncio.run(uz.Uzbekistan().search_legislation("Закон о защите персональных данных"))
    assert seen[-1] == "персональных данных" and r.total == 1 and "generic words" in r.note
