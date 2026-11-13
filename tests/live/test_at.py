"""Live smoke tests against the RIS OGD API (data.bka.gv.at). Needs network; 2 s spacing per request."""
from world_legal_mcp import server


async def test_at_court_filter_vfgh():
    out = await server.search_caselaw("at", "Gleichheitsgrundsatz", limit=3, filters={"court": "vfgh"})
    assert "VfGH" in out and 'get_decision("at", "JFT_' in out


async def test_at_decision_by_ecli_matches_doc_number():
    by_ecli = await server.get_decision("at", "ECLI:AT:OGH0002:2026:0030OB00192.25V.0325.000",
                                        max_chars=3000)
    by_id = await server.get_decision("at", "JJT_20260325_OGH0002_0030OB00192_25V0000_000",
                                      max_chars=3000)
    assert by_ecli == by_id and "3Ob192/25v" in by_id
    assert "Paragraph 508" not in by_id  # screen-reader duplicates stripped


async def test_at_provision_label_variants():
    a = await server.get_legislation_provision("at", "10001622", "1090")
    b = await server.get_legislation_provision("at", "10001622", "par. 1090")
    assert a == b and "§ 1090" in a and "Bestandvertrag" in a
    bvg = await server.get_legislation_provision("at", "10000138", "Art. 7")
    assert "Art. 7" in bvg and "gleich" in bvg


async def test_at_rechtssatz_doc_type():
    out = await server.search_caselaw("at", "Mietzinsminderung", limit=3,
                                      filters={"doc_type": "rechtssatz", "court": "ogh"})
    assert "(Rechtssatz)" in out and 'get_decision("at", "JJR_' in out
