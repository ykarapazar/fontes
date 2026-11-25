"""Live smoke tests for Bosnia and Herzegovina: Constitutional Court (ustavnisud.ba) and
Federation of BiH laws (fbihvlada.gov.ba). Needs network."""
from world_legal_mcp import server


async def test_ba_case_number_lists_all_decisions_and_english():
    out = await server.search_caselaw("ba", "U-5/98", limit=10)
    for i in ("12200", "12207", "12209", "12216"):
        assert f'get_decision("ba", "{i}")' in out, out
    out = await server.search_caselaw("ba", "", limit=10, filters={"case_number": "U-5/98", "language": "en"})
    assert 'get_decision("ba", "en:12209")' in out, out
    out = await server.get_decision("ba", "en:12209", max_chars=3000)
    assert "PARTIAL DECISION" in out and "2000-07-01" in out, out
    # a case number with several decisions asks for one id
    assert (await server.get_decision("ba", "U-5/98")).startswith("Bad request (ba)")


async def test_ba_filters_and_bad_values():
    out = await server.search_caselaw("ba", "diskriminacija", limit=5, filters={
        "case_type": "U", "decision_type": "merits", "date_from": "2000-01-01", "date_to": "2000-12-31"})
    assert "U-5/98" in out, out
    assert (await server.search_caselaw("ba", "x", filters={"case_type": "Z"})).startswith("Bad request (ba)")
    assert (await server.search_caselaw("ba", "x", filters={"date_from": "1.1.2020"})).startswith("Bad request (ba)")
    assert (await server.get_decision("ba", "999999999")).startswith("Not found (ba)")


async def test_ba_decision_by_case_number_has_summary():
    out = await server.get_decision("ba", "AP-4580/22", max_chars=4000)
    assert "1388899" in out and "ODLUKU O DOPUSTIVOSTI" in out, out


async def test_ba_fbih_law_year_filter_and_provision_variants():
    out = await server.search_legislation("ba", "zakon o radu", limit=10, filters={"year": "2016"})
    assert "bosanski/zakoni/2016/zakoni/5.html" in out and "26/16" in out, out
    law = "bosanski/zakoni/2016/zakoni/5.html"
    for label in ("Član 54", "54", "čl. 54.", "art 54"):
        out = await server.get_legislation_provision("ba", law, label)
        assert "Neplaćeno odsustvo" in out, (label, out)
    assert (await server.search_legislation("ba", "x", filters={"year": "1900"})).startswith("Bad request (ba)")


async def test_ba_constitution_and_amendment_from_parliament():
    out = await server.search_legislation("ba", "ustav", limit=5, filters={"level": "state"})
    assert 'get_legislation_toc("ba", "ustav-bih")' in out, out
    out = await server.get_legislation_provision("ba", "ustav-bih", "Član VI")
    assert "devet članova" in out and "Ustavni sud" in out, out
    out = await server.get_legislation_provision("ba", "ustav-bih", "amandman 1")
    assert "Brčko" in out, out


async def test_ba_state_consolidated_act_provision():
    out = await server.search_legislation("ba", "zakon o strancima", limit=5, filters={"level": "state"})
    assert "pa/1210" in out, out
    out = await server.get_legislation_provision("ba", "pa/1210", "Član 1")
    assert "ovim zakonom" in out.lower(), out
