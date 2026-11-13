"""Live smoke tests against the Caribbean Court of Justice judgment lists (ccj.org). Needs network; 1 s per request."""
from world_legal_mcp import server


async def test_ccj_filters_and_citation_search():
    out = await server.search_caselaw("ccj", "Mirchandani", limit=5, filters={
        "jurisdiction": "appellate", "date_from": "2005-01-01", "date_to": "2005-12-31"})
    assert "[2005] CCJ 1 (AJ)" in out, out
    none = await server.search_caselaw("ccj", "Mirchandani", filters={"jurisdiction": "OJ"})
    assert "[2005] CCJ 1 (AJ)" not in none
    # the source lists this one as "[2016] CCJ 1 (0J)" (zero for O); typed variants still match
    exact = await server.search_caselaw("ccj", "[2016] CCJ 01 (OJ)", limit=5)
    assert "[2016] CCJ 1 (OJ)" in exact, exact
    bad = await server.search_caselaw("ccj", "x", filters={"jurisdiction": "XX"})
    assert "AJ (appellate) or OJ (original)" in bad


async def test_ccj_judgment_text_and_other_documents():
    out = await server.get_decision("ccj", "[2013] CCJ 3 (OJ)", max_chars=4000)
    assert "MYRIE" in out and "2013-10-04" in out and "ccj.org/wp-content/uploads" in out, out[:800]
    assert "[2013] CCJ 3 (OJ)#2" in out           # executive summary listed as another document
    summary = await server.get_decision("ccj", "[2013] CCJ 3 (OJ)#2", max_chars=2000)
    assert "Myrie" in summary or "MYRIE" in summary


async def test_ccj_typo_citation_and_errors():
    # listed as "[2021] CCJ 8 (AJ) BB" although delivered 2022-03-24; its PDF says [2022] CCJ 8 (AJ)
    out = await server.get_decision("ccj", "[2022] CCJ 8 (AJ)", max_chars=1500)
    assert "SANDY LANE" in out.upper() and "2022-03-24" in out, out[:800]
    missing = await server.get_decision("ccj", "[2005] CCJ 99 (AJ)")
    assert "no [2005] CCJ 99 (AJ)" in missing
    bad = await server.get_decision("ccj", "Myrie")
    assert "neutral citation" in bad
