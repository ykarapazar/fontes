"""Live smoke tests for Rwanda (amategeko.gov.rw: judgments and Official Gazette laws).
Needs network; 1 s per request per host."""
from world_legal_mcp import server


async def test_rw_caselaw_filters_and_url_id():
    out = await server.search_caselaw("rw", "", limit=5, filters={"court": "Supreme Court", "year": "2008"})
    assert "RS/INCONST/PÉN.0001/08/CS" in out and "Court: Supreme Court" in out, out[:800]
    assert "court must be one of" in await server.search_caselaw("rw", "x", filters={"court": "Moon Court"})
    d = await server.get_decision("rw", "https://amategeko.gov.rw/view/doc/8322/8637", max_chars=2000)
    assert "MURORUNKWERE" in d and "2008-09-26" in d, d[:800]
    assert "numeric document id" in await server.get_decision("rw", "../etc/passwd")


async def test_rw_gazette_law_english_column():
    toc = await server.get_legislation_toc("rw", "3949")
    assert "Article 335: Commencement" in toc and "Ingingo ya" not in toc, toc[-1500:]
    p = await server.get_legislation_provision("rw", "3949", "Article One")
    assert "Purpose of this Law" in p and "Intego" not in p, p[:800]
    p2 = await server.get_legislation_provision("rw", "3949", "art. 2")
    assert "territory of Rwanda" in p2, p2[:800]
    assert "has no article" in await server.get_legislation_provision("rw", "3949", "999")
