"""Live smoke tests against the ITLOS case pages (www.itlos.org). Needs network; 1 s per request."""
from world_legal_mcp import server


async def test_itlos_search_by_number_title_and_type():
    out = await server.search_caselaw("itlos", "Case No. 31", limit=5)
    assert "Small Island States" in out and "SAIGA" not in out
    tuna = await server.search_caselaw("itlos", "Southern Bluefin Tuna", limit=5)
    assert "3-4" in tuna
    pr = await server.search_caselaw("itlos", "", limit=50, filters={"type": "prompt_release"})
    assert "Camouco" in pr and "Advisory Opinion" not in pr
    bad = await server.search_caselaw("itlos", "x", filters={"type": "merits"})
    assert "Bad request" in bad


async def test_itlos_case_record_lists_decisions_with_links():
    out = await server.get_decision("itlos", "ITLOS Case No. 2", max_chars=30000)
    assert "SAIGA" in out and "Overview of the case" in out
    assert "/fileadmin/itlos/documents/cases/case_no_2/published/C2-J-1_Jul_99.pdf" in out
    assert "1999-07-01" in out          # date of the Judgment of 1 July 1999
    joined = await server.get_decision("itlos", "4", max_chars=2000)
    assert "Southern Bluefin Tuna" in joined


async def test_itlos_bad_and_unknown_ids():
    missing = await server.get_decision("itlos", "999")
    assert "Not found" in missing and "999" in missing
    doc = await server.get_decision("itlos", "31#C31_Adv_Op_21.05.2024_corr")
    assert "not reproduced" in doc
