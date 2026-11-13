import asyncio

import pytest

from world_legal_mcp.base import SourceError
from world_legal_mcp.jurisdictions import cl

RAW = (
    "     Art. 159. El contrato de trabajo terminará en los              L. 19.010\n"
    "siguientes casos:                                                   Art. 1º\n"
    "1.-  Mutuo acuerdo de las partes.\n"
    "     Toda persona tiene un derecho.                                 CPR Art. 19° N° 4\n"
    "                                                                    D.O. 24.10.1980\n"
)


def test_margin_notes_split_from_text():
    body, notes = cl._split_margin(RAW)
    assert "L. 19.010" not in body and "D.O." not in body
    assert cl._paras(body)[0] == "Art. 159. El contrato de trabajo terminará en los siguientes casos: 1.- Mutuo acuerdo de las partes."
    assert cl._paras(body)[1] == "Toda persona tiene un derecho."
    assert "CPR Art. 19° N° 4" in " ".join(notes) and "D.O. 24.10.1980" in " ".join(notes)


def test_table_row_stays_in_text():
    body, notes = cl._split_margin("Renta anual            1.000            2%\n")
    assert notes == [] and "2%" in body


def test_search_year_filter_and_title_first(monkeypatch):
    seen = {}

    class R:
        status_code = 200

        def json(self):
            mk = lambda n, t: {"IDNORMA": n, "NORMA": f"Ley {n}", "TITULO_NORMA": t, "RESUMEN": "<R>a &#241; b</R>"}
            return [[mk(1, "MODERNIZA RELACIONES"), mk(2, "FIJA LA CONSTITUCION POLITICA DE LA REPUBLICA")],
                    {"totalitems": 2}, []]

    async def fake(url, params=None, **kw):
        seen.update(params)
        return R()

    monkeypatch.setattr(cl._http, "get", fake)
    res = asyncio.run(cl.Chile().search_legislation("Constitución Política de la República", limit=10, page=1,
                                                    filters={"year_from": "2022"}))
    assert seen["fc_pb"] == "2022 TO 2100"
    assert [h.id for h in res.items] == ["2", "1"]
    assert res.items[1].snippet == "a ñ b"


def _law(xml_text):
    xml = ('<Norma xmlns="http://www.leychile.cl/esquemas" fechaVersion="2020-01-01"><Identificador><TiposNumeros>'
           '<TipoNumero><Tipo>Ley</Tipo><Numero>1</Numero></TipoNumero></TiposNumeros></Identificador>'
           '<Metadatos><TituloNorma>T</TituloNorma></Metadatos><EstructurasFuncionales>'
           '<EstructuraFuncional tipoParte="Artículo" idParte="9"><Texto>%s</Texto><Metadatos>'
           '<NombreParte>primero</NombreParte></Metadatos></EstructuraFuncional></EstructurasFuncionales></Norma>'
           % xml_text).encode()
    j = cl.Chile()
    cl._cache["1"] = cl._parse("1", xml)
    return j


def test_empty_article_is_an_error_not_a_blank():
    j = _law("   ")
    with pytest.raises(SourceError):
        asyncio.run(j.get_legislation_provision("1", "Artículo primero"))


def test_amending_act_is_flagged():
    j = _law('Artículo primero.- Introdúcense las siguientes modificaciones en la ley N° 19.628, sobre vida privada:')
    t = asyncio.run(j.get_legislation_text("1"))
    assert "19.628" in t.metadata["Nota"]


def test_ordinal_article_numeric_alias():
    assert cl._ordinal_num("primero") == "1" and cl._ordinal_num("Décimo") == "10"
    assert cl._ordinal_num("159") == "" and cl._ordinal_num("primero bis") == ""


def test_pdf_word_splits_are_mended():
    texts = ["la vida privada y la vida digna. La vida\n", "el derecho civil, el derecho penal.", "la vid a privada de recho a la manifesta ción",
             "la manifestación libre", "de la ley y la ley y la ley"]
    out = cl._mend_splits([texts[2] + " de la ley", texts[0], texts[1], texts[3], texts[4]])
    assert out[0] == "la vida privada derecho a la manifestación de la ley"
    assert out[4] == texts[4]


def test_search_warns_when_hits_are_amending_acts(monkeypatch):
    class R:
        status_code = 200

        def json(self):
            mk = lambda n, t: {"IDNORMA": n, "NORMA": f"Ley {n}", "TITULO_NORMA": t}
            return [[mk(1, "MODIFICA LA LEY Nº 19.628, SOBRE X"), mk(2, "MODIFICA LA LEY Nº 20.000")], {"totalitems": 2}, []]

    async def fake(url, params=None, **kw):
        return R()

    monkeypatch.setattr(cl._http, "get", fake)
    res = asyncio.run(cl.Chile().search_legislation("vida privada", limit=5))
    assert "ley 19628" in res.note
    assert cl._AMENDING.match("Ley 1 – FIJA EL TEXTO") is None


def test_base_law_added_when_results_amend_it(monkeypatch):
    def mk(n, t, num):
        return {"IDNORMA": n, "NORMA": f"Ley {num}", "NUMERO": num, "TITULO_NORMA": t}

    class R:
        status_code = 200

        def __init__(self, items):
            self.items = items

        def json(self):
            return [self.items, {"totalitems": 9}, []]

    async def fake(url, params=None, **kw):
        if params["cadena"] == "ley 19628":
            return R([mk("141599", "SOBRE PROTECCION DE LA VIDA PRIVADA", "19628")])
        return R([mk("1", "MODIFICA LA LEY Nº 19.628, SOBRE X", "19812"), mk("2", "MODIFICA LA LEY N° 19.628", "21214")])

    monkeypatch.setattr(cl._http, "get", fake)
    res = asyncio.run(cl.Chile().search_legislation("protección de la vida privada", limit=2))
    assert [h.id for h in res.items] == ["141599", "1"]
    assert "base statute" in res.note
