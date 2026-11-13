"""Live smoke tests against El Peruano (legislation) and the Tribunal Constitucional (case law).
Needs network. The TC asks for 30 s between requests, so the case-law test takes about a minute."""
from world_legal_mcp import server


async def test_pe_provision_labels():
    for law, label in (("NL/2428226-2", "Artículo 1"), ("NL/2428226-2", "art. 1"), ("2428226-2", "1"),
                       ("https://busquedas.elperuano.pe/dispositivo/NL/2428226-2", "Artículo 1º")):
        out = await server.get_legislation_provision("pe", law, label)
        assert "Peru (pe)" in out and "Objeto de la Ley" in out, (law, label)
    pre = await server.get_legislation_provision("pe", "NL/2428226-2", "Artículo II")
    assert "Seguridad jurídica" in pre
    disp = await server.get_legislation_provision("pe", "NL/2428226-2", "Disposiciones complementarias finales – Tercera")
    assert "Vigencia" in disp
    bad = await server.get_legislation_provision("pe", "Ley 32421", "1")
    assert bad.startswith("Bad request (pe)")


async def test_pe_legislation_type_filter():
    out = await server.search_legislation("pe", "", filters={"type": "LEY", "date_from": "2025-08-15",
                                                              "date_to": "2025-08-15"}, limit=20)
    assert "NL/2428226-2" in out and "Nueva Ley de Nacionalidad" in out


async def test_pe_decision_citation_form():
    bad = await server.get_decision("pe", "00002-2020-XX/TC")
    assert bad.startswith("Bad request (pe)")
    out = await server.get_decision("pe", "Exp. N.° 0002-2020-CC/TC")
    assert "00002-2020-CC" in out and "Sentencia 778/2020" in out and "RAZÓN DE RELATORÍA" in out


async def test_pe_constitution_consolidated():
    hits = await server.search_legislation("pe", "Constitución Política del Perú", limit=3)
    assert "constitucion" in hits
    art = await server.get_legislation_provision("pe", "constitucion", "art. 2")
    assert "Toda persona tiene derecho" in art and "�" not in art
    # an article set in the PDF's un-mapped font, decoded
    art97 = await server.get_legislation_provision("pe", "Constitución Política del Perú", "Artículo 97")
    assert "Ley Nº 31988" in art97 and "Cámara de Diputados" in art97
    toc = await server.get_legislation_toc("pe", "constitucion", keyword="Decimosexta")
    assert "Decimosexta" in toc
