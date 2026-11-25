"""Live smoke tests against decisions.scc-csc.ca and Justice Laws. Needs network."""
from world_legal_mcp import server


async def test_ca_search_caselaw_by_citation_filter():
    out = await server.search_caselaw("ca", "", limit=3, filters={"citation": "2024 SCC 10"})
    assert "Dickson v. Vuntut Gwitchin First Nation" in out and "20353" in out


async def test_ca_get_decision_by_neutral_citation():
    out = await server.get_decision("ca", "2024 SCC 10", max_chars=3000)
    assert "20353" in out and "39856" in out and "## Text" in out


async def test_ca_provision_label_variants():
    out = await server.get_legislation_provision("ca", "C-46", "s. 718.2(e)")
    assert "section-718.2" in out
    out = await server.get_legislation_provision("ca", "c-46", "718")
    assert "section-718" in out and "sentencing" in out.lower()


async def test_ca_search_legislation_regulation_filter():
    out = await server.search_legislation("ca", "Immigration and Refugee Protection Regulations",
                                          limit=3, filters={"type": "regulation"})
    assert "SOR-2002-227" in out


async def test_ca_constitution_charter_and_1867():
    out = await server.get_legislation_provision("ca", "Const", "charter s. 7")
    assert "life, liberty and security of the person" in out
    out = await server.get_legislation_provision("ca", "Const", "1867 s. 91")
    assert "Peace, Order, and good Government" in out


async def test_ca_constitution_ambiguous_section_is_refused():
    out = await server.get_legislation_provision("ca", "Const", "section-7")
    assert "Bad request" in out and "section 7" in out
