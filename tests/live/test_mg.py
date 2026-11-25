"""Live smoke tests against the Malagasy sources (hcc.gov.mg, cnlegis.gov.mg).
Needs network; 1-1.5 s per request per host."""
from world_legal_mcp import server


async def test_mg_decision_id_variants_and_type_filter():
    by_id = await server.get_decision("mg", "10128")
    assert "04-HCC/D2" in by_id and "2026-10-28" in by_id, by_id[:800]
    by_url = await server.get_decision("mg", "https://www.hcc.gov.mg/?p=10128")
    assert "SAHONDRARIMALALA" in by_url, by_url[:800]
    d1 = await server.search_caselaw("mg", "ratification", limit=3, filters={"type": "d1"})
    assert "HCC/D1" in d1 and "HCC/D2" not in d1, d1[:1500]
    bad = await server.search_caselaw("mg", "x", filters={"type": "zz"})
    assert "Bad request" in bad


async def test_mg_bad_ids_never_fetch():
    assert "Bad request" in await server.get_decision("mg", "../../wp-admin")
    assert "Bad request" in await server.get_legislation_text("mg", "../../etc/passwd")


async def test_mg_law_number_search_and_provision_labels():
    hits = await server.search_legislation("mg", "2017-012")
    assert "L2017-012" in hits and "D2017-012" in hits, hits[:1500]
    a = await server.get_legislation_provision("mg", "L2017-012", "art. 242 (nouveau)")
    assert "petits litiges" in a.lower(), a[:800]
    first = await server.get_legislation_provision("mg", "L2017-012", "article premier")
    assert "a pour objet" in first, first[:800]


async def test_mg_constitution_and_old_pdf_text():
    out = await server.get_legislation_provision("mg", "Co2010", "Article 54")
    assert "Premier ministre" in out
    # O62-041 has only a header in HTML; the text comes from the PDF CNLegis links to.
    out = await server.get_legislation_provision("mg", "O62-041", "Article 2")
    assert "Journal officiel" in out
