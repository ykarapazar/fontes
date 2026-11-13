"""Live smoke tests against the Jamaican courts' judgment sites (supremecourt.gov.jm,
courtofappeal.gov.jm). Needs network; 1 s per request per host."""
from world_legal_mcp import server


async def test_jm_party_search_both_courts_and_filters():
    out = await server.search_caselaw("jm", "West Indies Petroleum", limit=10,
                                      filters={"court": "jmca", "year": "2026"})
    assert "jmca/5481" in out and "[2026] JMCA Civ 39" in out, out
    sc = await server.search_caselaw("jm", "Marksman", filters={"court": "supreme"})
    assert "jmsc/9181" in sc and "SU2023CV04084" in sc and "jmca/" not in sc, sc
    bad = await server.search_caselaw("jm", "x", filters={"court": "parish"})
    assert "jmca (Court of Appeal) or jmsc" in bad


async def test_jm_neutral_citation_as_id_and_query():
    ca = await server.get_decision("jm", "[2026] JMCA Civ 39", max_chars=1500)
    assert "Identifier: jmca/5481" in ca and "WEST INDIES PETROLEUM" in ca, ca[:800]
    sc = await server.get_decision("jm", "[2026] JMSC Civ 75", max_chars=1500)
    assert "Identifier: jmsc/9181" in sc and "2026-06-16" in sc and "Negligence" in sc, sc[:1500]
    hit = await server.search_caselaw("jm", "[2026] JMSC Civ 75")
    assert "jmsc/9181" in hit, hit


async def test_jm_alias_slug_ids_and_errors():
    # pre-2020s Supreme Court nodes are listed under a path alias; the slug is the id
    old = await server.get_decision("jm", "jmsc/adminstrator-general-v-lewis-patrick-lewis", max_chars=800)
    assert "HCV 2008/03891" in old and "2010-11-12" in old, old
    lst = await server.get_decision("jm", "jmsc/9341")          # a weekly court list, not a judgment
    assert "not a judgment" in lst
    assert "no page" in await server.get_decision("jm", "jmca/99999999")
    assert "neutral citation" in await server.get_decision("jm", "Marksman")


async def test_jm_privy_council_appeals():
    out = await server.search_caselaw("jm", "General Legal Council", filters={"court": "jcpc", "year": "2026"})
    assert "[2026] UKPC 16" in out and "jmca/" not in out and "Trinidad" not in out, out
    d = await server.get_decision("jm", "ukpc/2026/16")
    assert "McFarlane" in d and "From the Court of Appeal of Jamaica" in d, d[:1500]
