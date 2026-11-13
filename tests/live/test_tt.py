"""Live smoke tests for Trinidad and Tobago (ttlawcourts.org judgments, laws.gov.tt Acts).
Needs network; 1 s per request per host."""

from world_legal_mcp import server

BECKLES = "beckles-wendell-v-attorney-general-trinidad-and-tobago"


async def test_tt_caselaw_filters_and_ids():
    out = await server.search_caselaw("tt", "", limit=10, filters={"date": "2026-10-30"})
    assert BECKLES in out and "3 decisions" in out, out[:600]
    by_no = await server.search_caselaw("tt", "", filters={"case_number": "CV.2020-02873"})
    assert "smith-sylvester-v-salome-hinds-krystal" in by_no, by_no[:600]
    bad = await server.search_caselaw("tt", "x", filters={"date": "30/10/2026"})
    assert "YYYY-MM-DD" in bad
    # the full node URL works as an id too
    d = await server.get_decision("tt", "https://www.ttlawcourts.org/recent-judgments/" + BECKLES, max_chars=3000)
    assert "WENDELL BECKLES" in d and "Court of Appeal" in d and "2026-10-30" in d, d[:800]
    assert "No judgment" in await server.get_decision("tt", "no-such-judgment-xyz")


async def test_tt_current_law_prefers_unofficial_update():
    # record 418 is the 1939 Arbitration Act, Chap. 5:01; the chapter now holds Act 11 of 2023
    toc = await server.get_legislation_toc("tt", "418")
    assert "Objects of Act" in toc, toc[:1200]
    p = await server.get_legislation_provision("tt", "418", "section 3")
    assert "This Act binds the State" in p and "119228" in p, p


async def test_tt_unchaptered_act_and_provision_variants():
    hits = await server.search_legislation("tt", "Anti-Gang")
    assert "u119113" in hits and "No. 4 of 2021" in hits, hits[:800]
    p = await server.get_legislation_provision("tt", "u119113", "s. 5(1)")
    assert "gang leader" in p, p[:800]
    asterisked = await server.get_legislation_provision("tt", "524", "40")   # printed as "*40." in the PDF
    assert "change in the title of an officer" in asterisked, asterisked[:800]
    assert "has no section" in await server.get_legislation_provision("tt", "524", "999")
    assert "law id from search_legislation" in await server.get_legislation_text("tt", "Interpretation Act")


async def test_tt_privy_council_appeals():
    # the final court: JCPC judgments in appeals from T&T, via Find Case Law
    hits = await server.search_caselaw("tt", "Gajadhar", filters={"court": "privy council"})
    assert "[2026] UKPC 35" in hits and "Privy Council" in hits, hits[:800]
    d = await server.get_decision("tt", "ukpc/2026/35", max_chars=3000)
    assert "Court of Appeal of the Republic of Trinidad and Tobago" in d, d[:800]


async def test_tt_acts_as_passed_by_year():
    # Acts after the 2016 revision: the Chronological List gives each Act as passed
    year = await server.search_legislation("tt", "Procurement", filters={"year": "2026"})
    assert "u126243" in year and "No. 22 of 2026" in year, year[:800]
    p = await server.get_legislation_provision("tt", "u126243", "section 3")
    assert "public-private partnership" in p, p[:800]
    assert "year must be" in await server.search_legislation("tt", "", filters={"year": "1700"})
