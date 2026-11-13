import asyncio
from types import SimpleNamespace

from world_legal_mcp.jurisdictions import tt


def _search(monkeypatch, **kw):
    seen = []

    async def fake_get(url, *a, **k):
        seen.append(url)
        return SimpleNamespace(status_code=200, text="<html><body></body></html>")
    monkeypatch.setattr(tt._http, "get", fake_get)
    res = asyncio.run(tt.TT().search_caselaw("Attorney General", **kw))
    return res, seen


def test_note_says_names_only_and_zero_is_not_none(monkeypatch):
    res, _ = _search(monkeypatch)
    assert "not judgment text" in res.note and "does not mean" in res.note


def test_date_filter_echoed_and_no_range(monkeypatch):
    res, seen = _search(monkeypatch, filters={"date": "2022-06-01"})
    assert "2022-06-01" in res.note and "no date range" in res.note
    assert "field_date_of_delivery_value=2022-06-01" in seen[0]


def test_court_of_appeal_filter_is_applied(monkeypatch):
    res, seen = _search(monkeypatch, filters={"court": "court of appeal"})
    assert "field_case_number_value=C.A" in seen[0]
    assert "Court of Appeal" in res.note


def test_legislation_multiword_falls_back_to_single_words(monkeypatch):
    async def fake_titles(term):
        return [tt.LawHit(id="1020", title="Married Persons Act", type="Act")] if term == "Married" else []

    async def fake_recent():
        return []

    async def fake_year(y):
        return []
    monkeypatch.setattr(tt.TT, "_dll_titles", staticmethod(fake_titles))
    monkeypatch.setattr(tt, "_recent_rows", fake_recent)
    monkeypatch.setattr(tt, "_year_rows", fake_year)
    res = asyncio.run(tt.TT().search_legislation("Married Women"))
    assert [h.id for h in res.items] == ["1020"] and "any one of its words" in res.note


def test_total_counted_from_last_source_page(monkeypatch):
    def page(n):
        body = "".join(
            f"<tr><td class='views-field-title'><a href='/recent-judgments/c{i}'>Case {i}</a></td></tr>"
            for i in range(n))
        return ("<html><body><table class='views-table'><tbody>" + body +
                "</tbody></table><li class='pager__item--last'><a href='?page=2'>x</a></li></body></html>")
    seen = []

    async def fake_get(url, *a, **k):
        seen.append(url)
        return SimpleNamespace(status_code=200, text=page(3 if "page=2" in url else 10))
    monkeypatch.setattr(tt._http, "get", fake_get)
    res = asyncio.run(tt.TT().search_caselaw("Fletcher", limit=5))
    assert res.total == 23
    assert "MAIN SUBJECTS" in res.note and "cannot be searched" in res.note
