"""Live smoke tests against conseilconstitutionnel.sn and primature.sn. Needs network."""
from world_legal_mcp import server


async def test_sn_scanned_decision_gives_pdf_link():
    out = await server.get_decision("senegal", "decision-n-20-e-2024")
    assert "décision n° 20/E/2024" in out and "scanned images" in out
    assert "/wp-content/uploads/2026/10/20E2024-cc.pdf" in out


async def test_sn_caselaw_year_filter():
    out = await server.search_caselaw("sn", "", limit=5, filters={"year": "2019"})
    assert "décision n° 5/E/2019" in out and "2019-03-21" in out


async def test_sn_constitution_provision_variants():
    out = await server.get_legislation_provision("sn", "constitution", "art. 25-2")
    assert "Article 25-2" in out
    out = await server.get_legislation_provision("sn", "constitution", "premier")
    assert "Article premier" in out


async def test_sn_decree_by_type_filter():
    out = await server.search_legislation("sn", "2024-1982", limit=5, filters={"type": "decret"})
    assert "decret-ndeg-2024-1982-du-13-septembre-2024-portant-repartition-des" in out
    out = await server.get_legislation_provision(
        "sn", "decret-ndeg-2024-1982-du-13-septembre-2024-portant-repartition-des", "Article 1")
    assert "TOTAL POUR LE TERRITOIRE NATIONAL" in out


async def test_sn_ministry_of_justice_code_pdf():
    out = await server.search_legislation("sn", "code pénal", limit=10)
    assert "mj-2948" in out and "justice.sec.gouv.sn" in out
    out = await server.get_legislation_provision("sn", "mj-2948", "art. 4")
    assert "Article 4" in out and "Nul crime" in out
    out = await server.get_legislation_provision("sn", "mj-6040", "premier")
    assert "ARTICLE PREMIER" in out and "créancier" in out


async def test_sn_cour_supreme_via_juricaf():
    out = await server.search_caselaw("sn", "licenciement", limit=5, filters={"court": "supreme"})
    assert "SENEGAL-COURSUPREME-" in out and "JURICAF" in out, out
    dec = await server.get_decision("sn", "SENEGAL-COURSUPREME-20241127-40")
    assert "COUR SUPRÊME" in dec and "Cour suprême" in dec, dec[:500]
