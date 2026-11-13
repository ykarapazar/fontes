"""Live smoke tests against the Bahamian sources (courtofappeal.org.bs, courts.bs,
laws.bahamas.gov.bs) and Privy Council appeals on Find Case Law. Needs network; 1 s per request per host."""
from world_legal_mcp import server


async def test_bs_court_filters_and_ids():
    ca = await server.search_caselaw("bs", "Zenard Rolle", filters={"court": "ca", "year": "2026"})
    assert "ca/4967" in ca and "sc/" not in ca, ca
    sc = await server.search_caselaw("bs", "S.V.R.", filters={"court": "supreme"})
    assert "sc/2026/11/RULING-S.V.R.-v.-S.L.R.pdf" in sc and "2016/FAM/div/00340" in sc and "ca/" not in sc, sc
    bad = await server.search_caselaw("bs", "x", filters={"court": "magistrates"})
    assert "ca (Court of Appeal) or sc" in bad, bad


async def test_bs_bad_ids_never_fetch():
    assert "Give an id" in await server.get_decision("bs", "sc/../../etc/passwd")
    unlisted = await server.get_decision("bs", "sc/2026/11/not-listed.pdf")
    assert "has no PDF" in unlisted, unlisted
    assert "Use a law id" in await server.get_legislation_text("bs", "Penal Code")
    assert "Did you mean" in await server.get_legislation_text("bs", "sub/1873-0015")


async def test_bs_provision_label_variants():
    out = await server.get_legislation_provision("bs", "1873-0015", "section 290")
    assert "Whoever intentionally causes the death" in out, out[:800]
    sub = await server.search_legislation("bs", "Penal Code", filters={"kind": "amd"})
    assert "amd/" in sub and "Amending legislation" in sub, sub


async def test_bs_privy_council_appeals():
    out = await server.search_caselaw("bs", "Rubis", filters={"court": "jcpc", "year": "2026"})
    assert "[2026] UKPC 9" in out and "Privy Council" in out and "ca/" not in out, out
    # 2014-19 titles carry no country: found through the header phrase; other countries' cases are not
    old = await server.search_caselaw("bs", "Newbold", filters={"court": "privy council"})
    assert "[2014] UKPC 12" in old, old
    tt = await server.search_caselaw("bs", "Ramdeen", filters={"court": "jcpc"})   # Trinidad, untitled country
    assert "[2014] UKPC 7" not in tt, tt
    d = await server.get_decision("bs", "[2026] UKPC 9")
    assert "Rubis Bahamas" in d and "From the Court of Appeal of the Commonwealth of The Bahamas" in d, d[:1500]


async def test_bs_constitution_first_and_by_article():
    hits = await server.search_legislation("bs", "constitution", limit=3)
    assert "### 1. The Constitution" in hits and "1973-1080" in hits, hits
    art = await server.get_legislation_provision("bs", "1973-1080", "art. 15")
    assert "fundamental rights and freedoms" in art.lower(), art[:600]
