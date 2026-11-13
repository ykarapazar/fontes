"""Live smoke tests against the Belizean sources (belizejudiciary.org, agm.gov.bz).
Needs network; 1 s per request per host."""
from world_legal_mcp import server


async def test_bz_decision_id_variants_and_court():
    by_id = await server.get_decision("bz", "7614")
    assert "Editor Noh" in by_id and "High Court of Belize" in by_id, by_id[:800]
    by_url = await server.get_decision(
        "bz", "https://www.belizejudiciary.org/judgment/indictment-no-21-of-2024-the-king-v-editor-noh/")
    assert "Editor Noh" in by_url and "7614" in by_url, by_url[:800]
    pc = await server.get_decision("bz", "4634")
    assert "Privy Council" in pc and "Kirk Gordon" in pc, pc[:800]


async def test_bz_bad_ids_never_fetch():
    assert "Give a judgment id" in await server.get_decision("bz", "../../wp-admin")
    assert "Use a law id" in await server.get_legislation_text("bz", "../../etc/passwd")
    assert "Use a law id" in await server.get_legislation_text("bz", "https://example.com/x.pdf")
    gone = await server.get_legislation_text("bz", "000000000000a_No_Such_Act.pdf")
    assert "No PDF" in gone, gone


async def test_bz_law_id_variants_and_provision_labels():
    hits = await server.search_legislation("bz", "Criminal Code")
    assert "639762f72be2e_Cap_101_Criminal_Code_Act.pdf" in hits and "Substantive Law" in hits, hits
    out = await server.get_legislation_provision("bz", "Cap 101", "section 106")
    assert "commits" in out and "murder" in out, out[:800]
    same = await server.get_legislation_provision("bz", "639762f72be2e_Cap_101_Criminal_Code_Act.pdf", "s. 106")
    assert "imprisonment for life" in same, same[:800]


async def test_bz_final_appeals_ccj_and_privy_council():
    ccj = await server.search_caselaw("bz", "salazar", filters={"court": "ccj"})
    assert "[2019] CCJ 15 (AJ)" in ccj, ccj[:800]
    pc = await server.search_caselaw("bz", "Fuller", filters={"court": "jcpc"})
    assert "[2011] UKPC 23" in pc and "Bahamas" not in pc, pc[:800]
    d = await server.get_decision("bz", "[2011] UKPC 23", max_chars=2000)
    assert "Fuller" in d, d[:800]
    assert "court must be" in await server.search_caselaw("bz", "x", filters={"court": "hc"})
