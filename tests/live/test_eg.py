"""Live smoke tests against the Supreme Constitutional Court portal (sccourt.gov.eg). Needs network."""
from world_legal_mcp import server


async def test_eg_citation_variants():
    for did in ("421", "37/9", "الدعوى 37 لسنة 9 قضائية دستورية", "37/9/1"):
        out = await server.get_decision("eg", did, max_chars=3000)
        assert "الدعوى 37 لسنة 9" in out and "1990-05-19" in out, did
        assert "Rules_Html/421_9_37_1_2.html" in out, did
    bad = await server.get_decision("eg", "قانون العقوبات")
    assert bad.startswith("Bad request (eg)")


async def test_eg_filters_and_exact_number():
    out = await server.search_caselaw("eg", "حرية التعبير", filters={"judicial_year": "31", "type": "دستورية"})
    assert "الدعوى 121 لسنة 31" in out
    exact = await server.search_caselaw("eg", "الدعوى 15 لسنة 42", filters={"type": "تنازع"})
    assert "تنازع" in exact and "15 لسنة 42" in exact
    bad = await server.search_caselaw("eg", "الملكية", filters={"date_from": "2020-01-01"})
    assert bad.startswith("Bad request (eg)")


async def test_eg_unknown_case():
    out = await server.get_decision("eg", "99999999")
    assert "not found" in out.lower()
