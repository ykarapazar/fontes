import asyncio

from world_legal_mcp.jurisdictions import hn


def test_constitution_as_of_note():
    law = {"title": "Constitución de la República de Honduras", "as_of": ""}
    assert "2004" in hn._as_of(law)
    assert hn._as_of({"title": "Código Penal", "as_of": ""}) == ""
    assert hn._as_of({"title": "Constitución de la República", "as_of": "2020-01-01"}) == "2020-01-01"


def test_missing_title_note(monkeypatch):
    html = ('<html><form id="searchForm"></form><div class="searchintro"><span class="badge">1</span></div>'
            '<dl class="search-results"><dt class="result-title"><a href="/biblioteca/index.php/leyes/149-x">'
            'Ley de Conciliación</a></dt><dd class="result-text">Código Civil</dd></dl></html>')

    class R:
        status_code = 200
        content = html.encode()

    async def fake(*a, **k):
        return R()

    monkeypatch.setattr(hn._http, "get", fake)
    res = asyncio.run(hn.Honduras().search_legislation("Código Civil"))
    assert "may not hold" in res.note
    assert "CEDIJ" in res.note and "unverified" in res.note


def test_broad_match_drops_single_word_hits(monkeypatch):
    def row(i, t):
        return (f'<dt class="result-title"><a href="/biblioteca/index.php/leyes/{i}-x">{t}</a></dt>'
                '<dd class="result-text">x</dd>')
    html = ('<html><meta charset="utf-8"><form id="searchForm"></form><div class="searchintro"><span class="badge">2</span></div>'
            '<dl class="search-results">' + row(1, "Código Procesal Civil") + row(2, "Servicio Civil") + "</dl></html>")

    class R:
        status_code = 200
        content = html.encode()

    async def fake(*a, **k):
        return R()

    monkeypatch.setattr(hn._http, "get", fake)
    res = asyncio.run(hn.Honduras().search_legislation("Código Civil", filters={"match": "any"}))
    assert [i.title for i in res.items] == ["Código Procesal Civil"]
    assert "left out" in res.note


def test_summary_only_hits_flagged(monkeypatch):
    def row(i, t):
        return (f'<dt class="result-title"><a href="/biblioteca/index.php/leyes/{i}-x">{t}</a></dt>'
                '<dd class="result-text">x</dd>')
    html = ('<html><meta charset="utf-8"><form id="searchForm"></form><div class="searchintro"><span class="badge">2</span></div>'
            '<dl class="search-results">' + row(1, "Código del Trabajo") + row(2, "Ley de Conciliación") + "</dl></html>")

    class R:
        status_code = 200
        content = html.encode()

    async def fake(*a, **k):
        return R()

    monkeypatch.setattr(hn._http, "get", fake)
    res = asyncio.run(hn.Honduras().search_legislation("Código del Trabajo"))
    assert "summary only" not in res.items[0].snippet
    assert "summary only" in res.items[1].snippet
