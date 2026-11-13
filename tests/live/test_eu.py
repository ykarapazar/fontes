"""Live smoke tests against the Publications Office CELLAR (SPARQL + REST). Needs network."""
from world_legal_mcp import server


async def test_eu_decision_by_ecli_resolves_to_celex():
    out = await server.get_decision("eu", "ECLI:EU:C:2015:650", max_chars=3000)  # Schrems I
    assert out.startswith("# Maximillian Schrems v Data Protection Commissioner (C-362/14)")
    assert "Identifier: 62014CJ0362" in out and "Grand Chamber" in out


async def test_eu_caselaw_filters_general_court_orders():
    out = await server.search_caselaw("eu", "competition", limit=3,
                                      filters={"court": "gc", "doc_type": "order", "sort": "date"})
    assert "Court: General Court" in out and "Court of Justice" not in out
    assert "TO0" in out and "- Case number: T-" in out
    bad = await server.search_caselaw("eu", "x", filters={"court": "gc", "doc_type": "opinion"})
    assert bad.startswith("Bad request (eu)")


async def test_eu_provision_label_variants_use_consolidated_text():
    for label in ("6", "art. 6", "Article 6"):
        out = await server.get_legislation_provision("eu", "32016R0679", label)
        assert "### Article 6" in out and "Lawfulness of processing" in out
        assert "CELEX:02016R0679-" in out           # latest consolidated version
        assert "(a) the data subject has given consent" in out


async def test_eu_legislation_language_and_type_filters():
    out = await server.search_legislation("eu", "Datenschutz", limit=3,
                                          filters={"language": "DEU"})
    assert "results for 'Datenschutz'" in out and "### 1." in out
    assert "legal-content/DE/" in out
    out = await server.search_legislation("eu", "artificial intelligence", limit=3,
                                          filters={"doc_type": "regulation", "date_from": "2024"})
    assert "32024R1689" in out and "Type: Regulation" in out


async def test_eu_treaties_and_charter_by_celex():
    out = await server.get_legislation_provision("eu", "12016P/TXT", "Article 7")
    assert "Respect for private and family life" in out
    out = await server.get_legislation_provision("eu", "12016M/TXT", "art. 6")
    assert "same legal value as the Treaties" in out
    out = await server.get_legislation_provision("eu", "12016E/TXT", "Article 267")
    assert "preliminary ruling" in out


async def test_eu_search_treaties_doc_type():
    out = await server.search_legislation("eu", "Treaty on the Functioning", limit=5,
                                          filters={"doc_type": "treaty"})
    assert "12016E/TXT" in out and "Type: Treaty" in out
