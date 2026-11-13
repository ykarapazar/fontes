"""Live smoke tests for Cameroon (coursupreme.cm, www.prc.cm). Needs network; 1 s per request."""
from world_legal_mcp import server


async def test_cm_english_common_law_judgment():
    out = await server.search_caselaw("cm", "SENDZE", filters={"language": "en"})
    assert "final-judgment-no-06com-of-0203-2023" in out, out[:800]
    dec = await server.get_decision("cm", "Common Law Division/final-judgment-no-06com-of-0203-2023")
    assert "COMMON LAW DIVISION" in dec and "2023-03-02" in dec, dec[:800]


async def test_cm_decision_id_from_url():
    url = ("https://coursupreme.cm/publication/detail/Section%20Civile/"
           "arret--n%C2%B0-20civ-du-04-avril-2024?lang=fr")
    out = await server.get_decision("cm", url)
    assert "UNICS" in out and "20/CIV" in out, out[:800]


async def test_cm_provision_label_variants():
    for label in ("Article 1", "article 1er", "1", "art. 1"):
        out = await server.get_legislation_provision("cm", "151", label)
        assert "Ministère des Relations Extérieures" in out, (label, out[:600])


async def test_cm_type_filter_and_scans():
    out = await server.search_legislation("cm", "", filters={"type": "ordonnance"})
    assert "Ordonnance" in out and "Décret" not in out, out[:800]
    scan = await server.get_legislation_text("cm", "8245")      # Loi 2026/003: image-only PDF
    assert "scanned image" in scan, scan[:600]
    assert "article number" in await server.get_legislation_text("cm", "../x")
