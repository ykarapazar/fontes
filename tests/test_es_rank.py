from world_legal_mcp.jurisdictions import es


def _d(title, amb="1", cons="Finalizado"):
    return {"identificador": "X", "titulo": title, "ambito": {"codigo": amb, "texto": "x"},
            "estado_consolidacion": {"texto": cons}}


def test_exact_title_first():
    hits = [_d("Ley 4/2026, de 1 de octubre, " + "x" * 80 + " conforme al artículo 49 de la Constitución Española."),
            _d("Constitución Española.")]
    assert es._rank(hits, "Constitución Española")[0]["titulo"] == "Constitución Española."


def test_national_code_before_regional():
    hits = [_d("Ley 25/2010, del libro segundo del Código civil de Cataluña.", "2"),
            _d("Real Decreto de 24 de julio de 1889 por el que se publica el Código Civil.")]
    assert es._rank(hits, "Código Civil")[0]["titulo"].startswith("Real Decreto")


def test_outdated_flag_explained():
    assert "out of date" in es._law_hit(_d("Ley", "2", "Desactualizado")).status
    assert es._law_hit(_d("Ley")).status == "in force"


def test_outdated_text_date_is_last_amendment_not_today():
    xml = (b'<texto><bloque id="a1"><version fecha_vigencia="20080409"/>'
           b'<version fecha_vigencia="20190101"/><version fecha_vigencia="29990101"/></bloque></texto>')
    assert es._consolidated_to(xml) == "20190101"
    law = {"outdated": True, "as_of": "2019-01-01"}
    assert "hasta 2019-01-01" in es._notice(law)
    assert "última actualización" not in es._notice(law)


async def test_caselaw_search_in_summary(monkeypatch):
    seen = []

    async def fake(form, page, size):
        seen.append(form)
        return ""
    monkeypatch.setattr(es, "_hj_search", fake)
    adapter = es.Spain() if hasattr(es, "Spain") else next(
        v for v in vars(es).values() if isinstance(v, type) and hasattr(v, "caselaw_filters") and v.__module__ == es.__name__)()
    r = await adapter.search_caselaw("despido improcedente", limit=5, page=1, filters={"search_in": "summary"})
    assert seen[-1]["TIPO_BUSQUEDA_LIBRE"] == "6" and "exact phrase in the court's summary" in r.note
    assert r.note.startswith("This source holds Constitutional Court (TC) decisions only") and "Tribunal Supremo" in r.note
    r = await adapter.search_caselaw("despido improcedente", limit=5, page=1, filters={})
    assert seen[-1]["TIPO_BUSQUEDA_LIBRE"] == "0" and "search_in" in r.note


def test_provision_not_found_names_last_article_and_summary_note_says_phrase(monkeypatch):
    import asyncio
    import pytest
    from world_legal_mcp.base import NotFound

    law = {"id": "BOE-A-2015-11430", "outdated": False, "as_of": "x", "url": "u", "title": "t",
           "blocks": [{"kind": "prov", "label": "Artículo 91", "id": "a91", "paras": []},
                      {"kind": "prov", "label": "Artículo 92", "id": "a92", "paras": []},
                      {"kind": "prov", "label": "Disposición final primera", "id": "df1", "paras": []}]}

    async def fake_law(_id):
        return law
    monkeypatch.setattr(es, "_law", fake_law)
    src = es.Spain() if hasattr(es, "Spain") else next(
        v for v in vars(es).values() if isinstance(v, type) and v.__module__ == es.__name__
        and hasattr(v, "get_legislation_provision"))()
    with pytest.raises(NotFound, match="last numbered article is 'Artículo 92'"):
        asyncio.run(src.get_legislation_provision("BOE-A-2015-11430", "96"))
    assert "phrase" in src.caselaw_filters["search_in"]
