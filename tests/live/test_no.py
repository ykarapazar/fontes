"""Live smoke tests against domstol.no Supreme Court decision pages.
Needs network. Throttled to one request per second."""
from world_legal_mcp import server


async def test_no_slug_search_and_path_id_round_trip():
    out = await server.search_caselaw("no", "foretaksstraff", limit=3)
    assert "HR-2015-02557-A" in out and 'get_decision("no", "2015/hoyesterett-straff/foretaksstraff")' in out
    d = await server.get_decision("no", "2015/hoyesterett-straff/foretaksstraff")
    assert "2015-12-22" in d and "100 000 kroner" in d


async def test_no_filters_and_bad_filter():
    out = await server.search_caselaw("no", "", limit=2, filters={"year": "2025", "court": "avdeling",
                                                                  "area": "straff"})
    assert "Høyesterett" in out and "ankeutvalg" not in out and "HR-2025-" in out
    bad = await server.search_caselaw("no", "x", filters={"court": "lagmannsrett"})
    assert bad.startswith("Bad request (no)")


async def test_no_hr_number_url_and_summary_only_flag():
    a = await server.get_decision("no", "hr-2026-2227-a")
    b = await server.get_decision("no", "https://www.domstol.no/no/hoyesterett/avgjorelser/"
                                        "avgjorelser-2026/hoyesterett---sivil/HR-2026-2227-A/")
    assert a == b and "arbeidsmiljølova § 10-12" in a
    assert "Full judgment (PDF)" in a and "does not fetch" in a and "25-202049SIV-HRET" in a


async def test_no_unknown_id():
    out = await server.get_decision("no", "HR-2026-999999-A")
    assert "not found" in out.lower()
