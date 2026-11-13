import asyncio

from world_legal_mcp import _http
from world_legal_mcp.jurisdictions import et


def _row(title, f):
    return (f'<tr><td><div class="law-title">{title}</div><div class="law-description">d</div>'
            f'<a href="/Home/ViewFiles?path=/admin/Files/{f}.pdf">x</a></td></tr>')


def _search(monkeypatch, rows, query):
    class R:
        status_code = 200
        text = "<html><body>ከ 3 ሕጎች ውስጥ 3 ይታያሉ<table>" + "".join(rows) + "</table></body></html>"

    async def fake(url, **kw):
        return R()
    monkeypatch.setattr(_http, "get", fake)
    return asyncio.run(et.Ethiopia().search_legislation(query, limit=10, page=1, filters={}))


ROWS = [_row("አዋጅ ቁጥር 1414/2018 ብድር", "a"), _row("አዋጅ ቁጥር 414/1996 x", "b"),
        _row("አዋጅ ቁጥር 1183/2012 የፌደራል ሥነ- ሥርዓት", "c"), _row("አዋጅ ቁጥር 1183/2012 የፌደራል ሥነ-ሥርዓት", "d")]


def test_number_is_exact(monkeypatch):
    res = _search(monkeypatch, ROWS, "414")
    assert [h.number for h in res.items] == ["414/1996"] and res.total == 1


def test_gregorian_year_maps_to_ethiopian(monkeypatch):
    assert len(_search(monkeypatch, ROWS, "414/2004").items) == 1
    assert _search(monkeypatch, ROWS, "414/2010").items == []


def test_duplicate_marked_and_gap_note(monkeypatch):
    res = _search(monkeypatch, ROWS, "1183")
    assert len(res.items) == 1 and res.total == 1 and "lists this proclamation twice" in res.items[0].snippet
    assert "Constitution" in res.note and "Civil Code" in res.note
    assert "Civil Procedure" in res.note and "1156" in res.note


def test_short_title_ranks_first_within_page(monkeypatch):
    rows = [_row("አዋጅ ቁጥር 1415/2018 በአውሮፓ ኢንቨስትመንት ባንክ መካከል የተደረገውን የብድር ስምምነት ለማፅደቅ የወጣ አዋጅ", "a"),
            _row("አዋጅ ቁጥር 1180/2012 የኢንቨስትመንት አዋጅ", "b")]
    res = _search(monkeypatch, rows, "ኢንቨስትመንት")
    assert res.items[0].number == "1180/2012"


def test_english_query_gets_amharic_hint(monkeypatch):
    class R:
        status_code = 200
        text = "<html><body>ከ 0 ሕጎች ውስጥ 0 ይታያሉ<table></table></body></html>"

    async def fake(url, **kw):
        return R()
    monkeypatch.setattr(_http, "get", fake)
    res = asyncio.run(et.Ethiopia().search_legislation("investment", limit=5, page=1, filters={}))
    assert res.items == [] and "Amharic" in res.note and "1180/2012" in res.note
