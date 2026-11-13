from world_legal_mcp.jurisdictions import mn


def test_strip_keeps_comparisons():
    assert mn._strip("a < b and c > d") == "a < b and c > d"
    assert mn._strip("x &lt; y болон z &gt; w") == "x < y болон z > w"


def test_strip_escaped_and_cut_markup():
    assert mn._strip('түрээс&lt;span style="x"&gt;ийн&lt;/span&gt; a') == "түрээсийн a"
    assert mn._strip('текст &lt;span style="font-size:11') == "текст"
    assert "alert" not in mn._strip("<script>alert(1)</script>ok")


def test_orphan_tag_tail_in_snippet():
    row = ('<tr width="100%;" style="height: 20px;"><td><a href="/single_case/1?id=3&court_cat=1">C</a></td>'
           '<td><a href="/single_case/1?id=3&court_cat=1">2024-01-01</a></td>'
           '<td><a href="/single_case/1?id=3&court_cat=1">N</a></td>'
           '<td>Хайлтын товч:</td><td>0pt"&gt;Санхүүгийн түрээс&lt;span style="x</td></tr>')
    assert mn._rows(row, 1, 3)[0].snippet == "Санхүүгийн түрээс"


def test_word_junk():
    t = 'a: 0pt; mso:x;} </style> <![endif]--><!--[if gte mso 9]><xml> <o:x/> </xml><![endif]--> текст'
    assert mn._strip(t) == "текст"
    assert mn._strip("текст <style> p {x") == "текст"


def test_no_dates_still_sends_a_range():
    assert mn._date_range({}).startswith("1990/01/01 - ")
    assert mn._date_range({"date_from": "2022-01-01"}).startswith("2022/01/01 - ")


def test_date_mismatch_flagged(monkeypatch):
    import asyncio
    from types import SimpleNamespace

    page = ('<th>x</th>Шийдвэрийн мэдээлэл<table><tr><th>Дугаар</th><td>2025/ШЦТ/1</td></tr>'
            '<tr><th>Огноо</th><td>2026-11-12 </td></tr></table><!--Холбоотой'
            '<div class="undsen"><p>2025 11 12 2025/ШЦТ/1</p><div id="editor">')

    async def fake_get(url, **kw):
        return SimpleNamespace(status_code=200, text=page)

    monkeypatch.setattr(mn._http, "get", fake_get)
    d = asyncio.run(mn.Mongolia().get_decision("2/1/1"))
    assert "2025-11-12" in d.metadata["Date note"]
    assert d.date == "2025-11-12"


def test_search_note_warns_about_source_dates(monkeypatch):
    import asyncio

    async def fake(params, page):
        return [], 0

    monkeypatch.setattr(mn, "_search_page", fake)
    r = asyncio.run(mn.Mongolia().search_caselaw("x"))
    assert "number filter" in r.note
