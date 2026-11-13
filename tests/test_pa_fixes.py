import asyncio

from world_legal_mcp.jurisdictions import pa

ISSUE = """CONTENIDO
CORTE SUPREMA DE JUSTICIA
Fallo N° S/N
POR EL CUAL SE DECLARA NULA RESOLUCION TIERRAS ANATI ADJUDICACION

ALCALDÍA DE COLÓN
Acuerdo 3

REPÚBLICA DE PANAMÁ
ÓRGANO JUDICIAL
CORTE SUPREMA DE JUSTICIA
Panamá, nueve de febrero. La demanda de nulidad contra la resolucion de tierras ANATI sobre adjudicacion.
ES COPIA AUTENTICA DE SU ORIGINAL

REPÚBLICA DE PANAMÁ
ÓRGANO JUDICIAL
Aclaracion de sentencia sobre decreto ejecutivo seguridad publica.
REPÚBLICA DE PANAMÁ
PROVINCIA DE HERRERA
Acuerdo municipal ajeno.
"""


def test_ruling_cut_out_of_issue():
    seg = pa._ruling(ISSUE, "POR EL CUAL SE DECLARA NULA RESOLUCION TIERRAS ANATI ADJUDICACION")
    assert "demanda de nulidad" in seg and "ajeno" not in seg and "Aclaracion" not in seg
    seg2 = pa._ruling(ISSUE, "Aclaracion de sentencia sobre decreto ejecutivo seguridad publica")
    assert "Aclaracion" in seg2 and "ajeno" not in seg2 and "demanda" not in seg2
    assert pa._ruling(ISSUE, "SOBRE OTRA COSA DISTINTA TOTALMENTE") == ""


def _hit(title, id_, kind="FALLO"):
    return {"original": {"id": id_, "title": title, "type": {"type": kind}, "authority": {"authority": "CSJ"},
                         "keywords": [{"keyword": "Propiedad horizontal"}], "lawBranches": []}, "highlights": []}


def test_caselaw_drops_issue_wide_matches(monkeypatch):
    async def fake(params, limit, page):
        return {"count": 2, "data": [_hit("DEMANDA DE INCONSTITUCIONALIDAD DE LA LEY", "a"),
                                     _hit("NULIDAD DE ACUERDO MUNICIPAL", "b")]}
    monkeypatch.setattr(pa, "_search", fake)
    r = asyncio.run(pa.Panama().search_caselaw("inconstitucionalidad"))
    assert [h.id for h in r.items] == ["a"] and "left out" in r.note
    r = asyncio.run(pa.Panama().search_caselaw("hábeas corpus"))
    assert r.items == []


def test_texto_unico_first(monkeypatch):
    async def fake(params, limit, page):
        if params.get("type[type]") == "TEXTO UNICO":
            return {"count": 1, "data": [_hit("TEXTO UNICO DEL CODIGO PENAL", "cp", "TEXTO UNICO")]}
        return {"count": 9, "data": [_hit("LEY SOBRE JUBILADOS", "x", "LEY")]}
    monkeypatch.setattr(pa, "_search", fake)
    r = asyncio.run(pa.Panama().search_legislation("Código Penal", limit=5))
    assert [h.id for h in r.items] == ["cp", "x"]


def test_scanned_constitution_points_to_2004_text(monkeypatch):
    async def rec(id):
        return {"id": id, "type": {"type": "CONSTITUCION POLITICA"}, "content": "", "normUrl": None}
    monkeypatch.setattr(pa, "_record", rec)
    pa._cache.clear()
    try:
        asyncio.run(pa._load("30392aa1-ab05-4605-87ce-72e91a0a9f51"))
    except Exception as e:
        assert pa.CONSTITUTION_ID in str(e) and "no text layer" in str(e)
    else:
        raise AssertionError("expected an error")


def test_search_notes_civil_code_and_habeas(monkeypatch):
    async def srch(params, limit, page):
        return {"data": [], "count": 0}
    monkeypatch.setattr(pa, "_search", srch)
    j = pa.Panama()
    r = asyncio.run(j.search_legislation("Código Civil", filters={"type": "TEXTO UNICO"}))
    assert "Civil Code" in r.note and "scans" in r.note
    r = asyncio.run(j.search_caselaw("habeas"))
    assert "habeas corpus" in r.note
    r = asyncio.run(j.search_caselaw("habeas corpus"))
    assert "Habeas data" not in r.note


def test_texto_unico_filter_puts_code_title_first(monkeypatch):
    async def fake(params, limit, page):
        return {"count": 2, "data": [_hit("TEXTO UNICO DE LA CAJA DE SEGURO SOCIAL", "x", "TEXTO UNICO"),
                                     _hit("TEXTO UNICO DEL CODIGO PENAL", "cp", "TEXTO UNICO")]}
    monkeypatch.setattr(pa, "_search", fake)
    r = asyncio.run(pa.Panama().search_legislation("Código Penal", filters={"type": "TEXTO UNICO"}))
    assert [h.id for h in r.items] == ["cp", "x"]


def test_habeas_corpus_says_none_found(monkeypatch):
    async def fake(params, limit, page):
        return {"count": 1, "data": [_hit("SUSTRACCION DE MATERIA", "a")]}
    monkeypatch.setattr(pa, "_search", fake)
    r = asyncio.run(pa.Panama().search_caselaw("habeas", limit=5))
    assert "No habeas corpus ruling was found" in r.note


def test_codigo_de_trabajo_pinned(monkeypatch):
    cod = {"original": {"id": "7a0f567e-5b3e-42c1-a3b7-faa8386cad7b", "title": "POR EL CUAL SE APRUEBA EL CODIGO DE TRABAJO",
                        "type": {"type": "DECRETO DE GABINETE"}, "number": "252", "year": 1971}, "highlights": []}
    other = {"original": {"id": "x1", "title": "RESOLUCION SOBRE TRABAJO", "type": {"type": "RESOLUCION"}}, "highlights": []}

    async def fake(params, limit, page):
        return {"data": [cod] if params.get("number") == "252" else [other], "count": 1}
    monkeypatch.setattr(pa, "_search", fake)
    r = asyncio.run(pa.Panama().search_legislation("Código de Trabajo"))
    assert r.items[0].id == cod["original"]["id"] and "scan" in r.note


def _pin_fake(monkeypatch):
    cod = {"original": {"id": "c1", "title": "POR EL CUAL SE APRUEBA EL CODIGO DE TRABAJO",
                        "type": {"type": "DECRETO DE GABINETE"}, "number": "252"}, "highlights": []}
    fis = {"original": {"id": "f1", "title": "POR LA CUAL SE APRUEBA EL CODIGO FISCAL DE LA REPUBLICA",
                        "type": {"type": "LEY"}, "number": "8"}, "highlights": []}
    other = {"original": {"id": "x1", "title": "OTRA", "type": {"type": "TEXTO UNICO"}}, "highlights": []}

    async def fake(params, limit, page):
        n = params.get("number")
        return {"data": [cod] if n == "252" else [fis] if n == "8" else [other], "count": 1}
    monkeypatch.setattr(pa, "_search", fake)


def test_pinned_code_not_forced_into_wrong_type_filter(monkeypatch):
    _pin_fake(monkeypatch)
    r = asyncio.run(pa.Panama().search_legislation("Código de Trabajo", filters={"type": "TEXTO UNICO"}))
    assert [i.id for i in r.items] == ["x1"] and "excludes it" in r.note and "linked in the error" not in r.note


def test_codigo_fiscal_pinned(monkeypatch):
    _pin_fake(monkeypatch)
    r = asyncio.run(pa.Panama().search_legislation("Código Fiscal"))
    assert r.items[0].id == "f1" and "scan" in r.note
    r = asyncio.run(pa.Panama().search_legislation("Código Fiscal", filters={"type": "TEXTO UNICO"}))
    assert r.items[0].id == "x1" and "excludes it" in r.note
