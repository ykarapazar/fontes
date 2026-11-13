import asyncio

import pytest

from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions import mz


def test_shifted_font_lines_are_decoded():
    # "Os tribunais ... em 2018," in the PDF's font-shifted text layer (shift 30, \x02 = space, digits < \x20)
    assert mz._fix_line("QU\x02VTKDWPCKU\x02GO\x02\x14\x12\x13\x1a\x0e") == "os tribunais em 2018,"
    assert mz._fix_line("ARTIGO\x02\x14\x13\x13") == "ARTIGO 211"
    assert mz._fix_line("FGſPKÁºQ") == "definição"
    assert mz._fix_line("Texto normal do artigo.") == "Texto normal do artigo."


def test_constitution_articles_skip_the_revision_law():
    text = ("ARTIGO 1\n(Alterações)\nFicam alterados.\n“ARTIGO 8\n(Estado unitário)\nAlterado.\n"
            "CONSTITUIÇÃO DA REPÚBLICA\nPreâmbulo\nTexto.\nARTIGO 1\n(República de Moçambique)\nÉ um Estado.\n"
            "ARTIGO 2\n(Soberania)\nA soberania reside no povo.")
    _, spans = mz._articles(text)
    a, b = spans["Artigo 1"]
    assert text.split("\n")[a:b][1] == "(República de Moçambique)"
    assert "Artigo 8" not in spans


def test_legislation_note_names_missing_codes(monkeypatch):
    async def none():
        return []
    monkeypatch.setattr(mz, "_laws", none)
    r = asyncio.run(mz.Mozambique().search_legislation("Código Civil", limit=5, page=1, filters={}))
    assert "Código Civil" in r.note and "not in this source" in r.note


def test_caselaw_date_filter(monkeypatch):
    rows = [{"id": f"x/{y}", "court": "TS", "processo": str(y), "especie": "", "materia": "", "relator": "",
             "date": f"{y}-03-01"} for y in (2020, 2022, 2025)]

    async def table(c):
        return rows if c == "ts" else []
    monkeypatch.setattr(mz, "_table", table)
    r = asyncio.run(mz.Mozambique().search_caselaw("2", limit=10, page=1,
                                                   filters={"court": "ts", "date_from": 2022, "date_to": "2022"}))
    assert [h.id for h in r.items] == ["x/2022"]
    with pytest.raises(BadRequest):
        asyncio.run(mz.Mozambique().search_caselaw("2", limit=10, page=1,
                                                   filters={"court": "cc", "date_from": "2022"}))
