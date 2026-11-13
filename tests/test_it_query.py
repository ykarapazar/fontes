import pytest

from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions.it import _parse_query


@pytest.mark.parametrize("q", ["legge 91/92", "legge n. 241 del 90", "91/92", "n. 5 del 90"])
def test_short_year_rejected(q):
    with pytest.raises(BadRequest):
        _parse_query(q)


@pytest.mark.parametrize("q", [
    "bilancio 2023/24", "decreto 12/03/20", "decreto 17/12/2013",
    "decreto n. 123 del 12 marzo 2020", "legge n. 241 del 07 agosto 1990",
    "legge 241/1990 art. 3/12", "legge 2/1990 e 12/20", "Direttiva 95/46/CE"])
def test_not_short_citations(q):
    b = _parse_query(q)
    assert b.get("annoProvvedimento") != "2013" or "numeroProvvedimento" not in b


def test_full_date_not_split():
    assert "numeroProvvedimento" not in _parse_query("decreto 17/12/2013")


def test_del_with_day():
    b = _parse_query("legge n. 241 del 07 agosto 1990")
    assert "numeroProvvedimento" not in b or b["annoProvvedimento"] == "1990"


def test_full_citation():
    b = _parse_query("legge 241/1990")
    assert b["numeroProvvedimento"] == "241" and b["annoProvvedimento"] == "1990"


@pytest.mark.parametrize("q", ["241/90 e trasparenza", "241 / 90"])
def test_short_year_more_forms(q):
    with pytest.raises(BadRequest):
        _parse_query(q)


def test_month_not_citation():
    assert "numeroProvvedimento" not in _parse_query("n. 5 del 12 marzo")


def _search(filters, query="licenziamento"):
    import asyncio
    from types import SimpleNamespace
    from world_legal_mcp import _http
    from world_legal_mcp.jurisdictions.it import Italy
    sent = {}

    async def fake_post(url, json=None, **kw):
        sent.update(json)
        return SimpleNamespace(status_code=200, json=lambda: {"listaAtti": [], "numeroAttiTrovati": 0})

    orig, _http.post = _http.post, fake_post
    try:
        asyncio.run(Italy().search_legislation(query, limit=5, page=1, filters=filters))
    finally:
        _http.post = orig
    return sent


def test_year_range_filters():
    b = _search({"search_in": "text", "year_from": "2022"})
    assert b["dataInizioEmanazione"] == "2022-01-01" and "dataFineEmanazione" not in b
    b = _search({"year_from": "2022", "year_to": "2024"})
    assert (b["dataInizioEmanazione"], b["dataFineEmanazione"]) == ("2022-01-01", "2024-12-31")


@pytest.mark.parametrize("f", [{"year": "2022", "year_from": "2020"}, {"year_from": "2024", "year_to": "2022"},
                               {"year_from": "22"}])
def test_year_range_rejected(f):
    with pytest.raises(BadRequest):
        _search(f)
