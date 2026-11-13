import asyncio
import datetime

import pytest

from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions import ar
from world_legal_mcp.models import LawHit


def _hit(i, title="x"):
    return LawHit(id=str(i), title=title, type="Ley", number=str(i))


@pytest.fixture
def calls(monkeypatch):
    seen = []

    async def fake(params, page=1):
        seen.append(dict(params))
        if params.get("texto", "").startswith('"') and "nada" in params["texto"]:
            return [], 0
        return [_hit(1)], 1

    async def idx():
        return [_hit(804, "Constitución de la Nación Argentina")]
    monkeypatch.setattr(ar, "_infoleg", fake)
    monkeypatch.setattr(ar, "_load_index", idx)
    return seen


def _search(q, **f):
    return asyncio.run(ar.Argentina().search_legislation(q, limit=10, page=1, filters=f))


def test_year_uses_publication_window_not_sanction(calls):
    _search("contrato", year="1974")
    p = calls[0]
    assert "anioSancion" not in p
    assert (p["anioPubDesde"], p["anioPubHasta"], p["mesPubHasta"], p["diaPubHasta"]) == ("1974", "1974", "12", "31")


def test_current_year_ends_yesterday():
    y = datetime.date.today().year
    w = ar._window(y, y)
    end = datetime.date(int(w["anioPubHasta"]), int(w["mesPubHasta"]), int(w["diaPubHasta"]))
    assert end < datetime.date.today()


def test_range_and_open_range(calls):
    _search("x", year="2022-2024")
    assert (calls[0]["anioPubDesde"], calls[0]["anioPubHasta"]) == ("2022", "2024")
    _search("x", year="2022-")
    assert calls[-1]["anioPubHasta"] == str(datetime.date.today().year)


def test_bad_year(calls):
    with pytest.raises(BadRequest):
        _search("x", year="2024-2022")
    with pytest.raises(BadRequest):
        _search("x", year="recent")


def test_empty_wide_range_falls_back_per_year(monkeypatch):
    seen = []

    async def fake(params, page=1):
        seen.append(params["anioPubDesde"] + "-" + params["anioPubHasta"])
        if params["anioPubDesde"] != params["anioPubHasta"]:
            return [], 0
        return [_hit(int(params["anioPubDesde"]))], 1
    monkeypatch.setattr(ar, "_infoleg", fake)
    items, total = asyncio.run(ar._by_year({"tipoNorma": "1"}, 2021, 2023, 0, 10))
    assert [h.id for h in items] == ["2023", "2022", "2021"] and total == 3


def test_multiword_query_tries_phrase_then_words(calls):
    _search("contrato de trabajo")
    assert calls[0]["texto"] == '"contrato de trabajo"'
    r = _search("nada de esto")
    assert calls[-1]["texto"] == "nada de esto" and "exact phrase" in r.note


def test_constitution_found_by_common_name_and_id(calls):
    assert _search("Constitución Nacional").items[0].id == "804"
    assert asyncio.run(ar._norm_id("constituciones/nacional")) == "804"


def test_named_law_lifted_and_alias_and_date_note(monkeypatch):
    rows = [_hit(1, "Ley 1 – OTRA COSA"), _hit(20744, "Ley 20744 – LEY DE CONTRATO DE TRABAJO – REGIMEN")]

    async def fake(params, page=1):
        if params.get("numero") == "25326":
            return [_hit(25326, "Ley 25326 – HABEAS DATA")], 1
        return ([rows[0]] if page == 1 else [rows[1]]), 60

    async def idx():
        return []
    monkeypatch.setattr(ar, "_infoleg", fake)
    monkeypatch.setattr(ar, "_load_index", idx)
    r = _search("contrato de trabajo")
    assert r.items[0].id == "20744"
    assert "publication dates, not sanction" in r.note
    assert _search("protección de datos personales").items[0].id == "25326"


def test_ley_de_prefix_finds_law_titled_without_it(monkeypatch):
    rows = [_hit(i, f"Ley {i} – NAVEGACION AEREA") for i in range(1, 4)]
    target = _hit(19550, "Ley 19550 – SOCIEDADES COMERCIALES - NUEVO REGIMEN")

    async def fake(params, page=1):
        return (rows + [target] if page == 1 else []), 60

    async def idx():
        return []
    monkeypatch.setattr(ar, "_infoleg", fake)
    monkeypatch.setattr(ar, "_load_index", idx)
    res = asyncio.run(ar.Argentina().search_legislation("Ley de Sociedades Comerciales", limit=2, page=1, filters={}))
    assert res.items[0].id == "19550"


def test_ley_de_prefix_dropped_from_phrase(calls):
    _search("Ley de Sociedades Comerciales")
    assert calls[0]["texto"] == '"Sociedades Comerciales"'


def test_code_beats_amending_and_partial_laws_with_same_title_start(monkeypatch):
    rows = [_hit(22686, "Ley 22686 – SOCIEDADES COMERCIALES - LEY Nº 19500 - INTRODUCENSE REFORMAS"),
            _hit(22491, "Ley 22491 – SOCIEDADES COMERCIALES - BALANCE"),
            _hit(19550, "Ley 19550 – SOCIEDADES COMERCIALES - NUEVO REGIMEN")]

    async def fake(params, page=1):
        return (rows if page == 1 else []), 70

    async def idx():
        return []
    monkeypatch.setattr(ar, "_infoleg", fake)
    monkeypatch.setattr(ar, "_load_index", idx)
    for q in ("Ley de Sociedades Comerciales", '"Sociedades Comerciales"'):
        res = asyncio.run(ar.Argentina().search_legislation(q, limit=3, page=1, filters={}))
        assert res.items[0].id == "19550", q
