"""Live smoke tests for Barbados (barbadoslawcourts.gov.bb judgments and consolidated laws).
Needs network; the site's robots.txt asks for 10 s between requests, so these are slow."""
from world_legal_mcp import server


async def test_bb_caselaw_filters_and_ids():
    out = await server.search_caselaw("bb", "", filters={"casename": "popo", "court": "hc"})
    assert "wendy-popo-v-ag" in out and "2022-02-18" in out, out[:800]
    bad = await server.search_caselaw("bb", "x", filters={"court": "privy council"})
    assert bad.startswith("Bad request (bb)")
    bad = await server.search_caselaw("bb", "x", filters={"date_from": "18/02/2022"})
    assert bad.startswith("Bad request (bb)")
    # the full page URL works as an id; text comes from the page's HTML body
    d = await server.get_decision("bb", "https://www.barbadoslawcourts.gov.bb/judgments/wendy-popo-v-ag",
                                  max_chars=3000)
    assert "Identifier: wendy-popo-v-ag" in d and "High Court" in d and "2022-02-18" in d, d[:800]
    assert "Not found (bb)" in await server.get_decision("bb", "no-such-judgment-xyz")


async def test_bb_law_by_chapter_and_provision_variants():
    hits = await server.search_legislation("bb", "Cap. 195")
    assert "statutes/ContributoryNegligenceCAP195" in hits, hits[:800]
    p = await server.get_legislation_provision("bb", "Cap. 208", "s. 4")
    assert "Section 4" in p, p[:800]
    p3 = await server.get_legislation_provision("bb", "statutes/OccupiersLiabilityCAP208", "section 10")
    assert "Section 10" in p3, p3[:600]
    assert "Cap. 9999" in await server.get_legislation_toc("bb", "Cap. 9999")


async def test_bb_subsidiary_filter():
    out = await server.search_legislation("bb", "adoption", filters={"kind": "subsidiary"})
    assert "subsidiary/AdoptionRegulations,1986Cap212'A" in out and "statutes/" not in out, out[:800]


async def test_bb_ccj_final_appeals():
    # CCJ appeals from Barbados only: a pre-2020 row (country read from the PDF) and a listed one
    out = await server.search_caselaw("bb", "carlton hall", filters={"court": "ccj"})
    assert "[2020] CCJ 1 (AJ)" in out and "Caribbean Court of Justice" in out, out[:800]
    gy = await server.search_caselaw("bb", "mustapha", filters={"court": "ccj"})   # Guyana appeal
    assert "CCJ 13 (AJ)" not in gy, gy[:800]
    d = await server.get_decision("bb", "[2020] CCJ 1 (AJ)", max_chars=3000)
    assert "COURT OF APPEAL OF BARBADOS" in d, d[:800]
