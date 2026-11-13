import asyncio

from world_legal_mcp.jurisdictions import pe


def test_sent_date():
    t = "En Lima, a los 14 días del mes de enero de 2020, el Pleno"
    assert pe._sent_date(t) == "2020-01-14"
    assert pe._sent_date("a los 3 días del mes de setiembre de 2019") == "2019-09-03"
    assert pe._sent_date("sin fecha") == ""


def test_process_words_become_filter(monkeypatch):
    seen = []

    async def fake(params, pagina):
        seen.append(dict(params))
        return [], 1
    monkeypatch.setattr(pe, "_causas", fake)
    for q, f in (("habeas corpus", None), ("amparo", {"year": 2022, "process": "AA"})):
        asyncio.run(pe.Peru().search_caselaw(q, filters=f))
    assert seen[0]["tip_exp"] == "HC" and "demdt" not in seen[0]
    assert seen[1]["tip_exp"] == "AA" and seen[1]["a_exp"] == "2022" and "demdt" not in seen[1]


def _fake_site(monkeypatch, hits_for):
    seen = []

    class R:
        status_code = 200
        text = ""

    async def fake_get(url):
        seen.append(url)
        return R()
    monkeypatch.setattr(pe._http, "get", fake_get)
    monkeypatch.setattr(pe, "_turbo", lambda t: {"routes/_index": {"results": {
        "totalHits": len(hits_for(seen[-1])), "hits": hits_for(seen[-1])}}})
    return seen


def _hit(op, num, sumilla):
    return {"op": op, "tipoPublicacion": "NL", "tipoDispositivo": "LEY", "numeroDispositivo": num,
            "sumilla": sumilla, "fechaPublicacion": "20110703"}


def test_named_law_found_first_by_title(monkeypatch):
    hits = [_hit("1-1", "N° 32595", "Ley que crea el Banco de Datos"),
            _hit("2-1", "N° 29733", "Ley de Protección de Datos Personales")]
    seen = _fake_site(monkeypatch, lambda u: hits)
    res = asyncio.run(pe.Peru().search_legislation("Ley de Protección de Datos Personales"))
    assert res.items[0].number == "29733" and "No LEY" not in res.note
    assert "tipoDispositivo=LEY" in seen[0]


def test_named_law_missing_says_so(monkeypatch):
    hits = [_hit("1-1", "N° 29263", "Ley que modifica el Código Penal y la Ley General del Ambiente")]
    _fake_site(monkeypatch, lambda u: hits)
    res = asyncio.run(pe.Peru().search_legislation("Ley General del Ambiente"))
    assert "No LEY titled" in res.note and "does not show the law does not exist" in res.note


def test_code_query_without_the_code_says_so(monkeypatch):
    hits = [{"op": "9-1", "tipoPublicacion": "BO", "tipoDispositivo": "Edicto Matrimonial",
             "numeroDispositivo": "", "sumilla": "Artículo 250° del Código Civil", "fechaPublicacion": "20261112"}]
    _fake_site(monkeypatch, lambda u: hits)
    res = asyncio.run(pe.Peru().search_legislation("Código Civil"))
    assert "None of the hits is the 'Código Civil' itself" in res.note


def test_pdf_page_split_into_articles():
    page = "TÍTULO PRELIMINAR\nDISPOSICIONES GENERALES\nArtículo 1. Objeto\ntexto uno\nArtículo 2. Definiciones\ntexto dos"
    secs = pe._sections(pe._split_pdf([page]))
    assert [lab for lab, _, _ in secs if lab] == ["Artículo 1", "Artículo 2"]


def test_process_word_header_not_a_match(monkeypatch):
    async def fake(params, pagina):
        return [], 1
    monkeypatch.setattr(pe, "_causas", fake)
    r = asyncio.run(pe.Peru().search_caselaw("habeas data"))
    assert r.query_ignored and "process type" in r.note


def test_ley_filter_asks_normal_and_extraordinary_editions(monkeypatch):
    seen = []

    async def fake_get(url):
        seen.append(url)

        class R:
            status_code = 200
            text = ""
        return R()
    monkeypatch.setattr(pe._http, "get", fake_get)
    monkeypatch.setattr(pe, "_turbo", lambda t: {"routes/_index": {"results": {"totalHits": 1, "hits": [
        _hit("1-1", "N° 32110", "Ley x")]}}})
    r = asyncio.run(pe.Peru().search_legislation("", filters={"type": "LEY"}))
    assert any("tipoPublicacion=NL" in u for u in seen) and any("tipoPublicacion=EX" in u for u in seen)
    assert r.total == 2


def test_constitution_has_no_gazette_warning():
    assert not any(s.warning for s in pe.Peru.sources if "El Peruano" in s.name)
