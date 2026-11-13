"""Live smoke tests against Find Case Law and legislation.gov.uk. Needs network."""
from world_legal_mcp import server


async def test_gb_search_caselaw():
    out = await server.search_caselaw("gb", "unfair prejudice director", limit=3,
                                      filters={"court": "ewhc/ch"})
    assert "United Kingdom (gb) case law" in out and 'get_decision("gb"' in out
    assert "/ewhc/ch/" in out


async def test_gb_get_decision_by_neutral_citation():
    out = await server.get_decision("uk", "[2024] UKSC 1", max_chars=3000)
    assert "uksc/2024/1" in out and "## Text" in out and "Judgment" in out


async def test_gb_get_decision_by_slug():
    out = await server.get_decision("gb", "uksc/2024/1", max_chars=2000)
    assert "- Identifier: [2024] UKSC 1" in out


async def test_gb_search_legislation():
    out = await server.search_legislation("gb", "Companies Act 2006", limit=3,
                                          filters={"doc_type": "ukpga"})
    assert "ukpga/2006/46" in out and "2006 c. 46" in out


async def test_gb_get_legislation_provision():
    out = await server.get_legislation_provision("gb", "ukpga/2006/46", "s.172")
    assert ": section/172" in out and "success of the company" in out


async def test_gb_bare_number_redirects_to_regulation():
    out = await server.get_legislation_provision("gb", "uksi/2013/3134", "3")
    assert ": regulation/3" in out


async def test_gb_toc_has_schedule_paths():
    out = await server.get_legislation_toc("gb", "ukpga/2006/46", keyword="schedule/1")
    assert 'provision "schedule/1' in out


async def test_gb_search_exact_title_first_with_count():
    out = await server.search_legislation("gb", "Legal Services Act", limit=5)
    assert "### 1. Legal Services Act 2007" in out and "unknown number" not in out


async def test_gb_provision_inherited_annotations_trimmed():
    out = await server.get_legislation_provision("gb", "ukpga/1988/48", "9")
    assert "**F1** S. 9(2)(aa)(ab)" in out and "more annotations apply to the enclosing Part I" in out
    assert "S.I. 1989/988" not in out
