"""Live smoke tests for Mauritius: Privy Council (Find Case Law), AG Revised Laws, National
Assembly Acts. The Supreme Court site is gated (robots.txt). Needs network."""

from world_legal_mcp import server



async def test_mu_supreme_court_site_is_gated():
    # supremecourt.govmu.org robots.txt: Disallow: / for every agent since 2026-11-10.
    # Off unless the operator permits "mu"; nothing below may touch that host.
    for out in (await server.get_decision("mu", "2026 INT 291"),
                await server.get_legislation_text("mu", "Act No. 10 of 2026"),
                await server.search_legislation("mu", "abuse", filters={"type": "act"}),
                await server.search_caselaw("mu", "", filters={"court": "Industrial"})):
        assert out.startswith("Bad request (mu)") and "permission" in out, out[:300]
    hits = await server.search_caselaw("mu", "Hurnam", limit=5)   # Privy Council only
    assert "[2026] UKPC 29" in hits and "permission" in hits, hits


async def test_mu_privy_council_appeals():
    out = await server.search_caselaw("mu", "Alteo", filters={"court": "jcpc"})
    assert "[2026] UKPC 27" in out and "Privy Council" in out, out
    mixed = await server.search_caselaw("mu", "Hurnam", limit=5)   # Privy Council first, then local courts
    assert "[2026] UKPC 29" in mixed, mixed
    d = await server.get_decision("mu", "[2026] UKPC 29")
    assert "Hurnam" in d and "From the Supreme Court of Mauritius" in d, d[:1500]


async def test_mu_constitution_revised_laws_and_acts_as_passed():
    hits = await server.search_legislation("mu", "constitution", limit=3)
    assert "Constitutions/THE CONSTITUTION, GN 54 of 1968" in hits, hits
    s15 = await server.get_legislation_provision("mu", "constitution", "15")
    assert "Protection of freedom of movement" in s15
    rev = await server.search_legislation("mu", "companies", filters={"type": "revised"})
    assert "A-Z Acts/C/Companies Act, No. 15 of 2001" in rev, rev
    toc = await server.get_legislation_toc("mu", "A-Z Acts/C/Companies Act, No. 15 of 2001")
    assert "Short title" in toc
    old = await server.get_legislation_provision("mu", "Act No. 20 of 2023", "1")
    assert "Financial Crimes Commission" in old, old[:500]
