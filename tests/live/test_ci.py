"""Live smoke tests for Côte d'Ivoire: Cour de cassation (eservices/sigcc.courdecassation.ci) and
Assemblée nationale laws (assnat.ci). Needs network. Throttled to one request per second per host."""
from world_legal_mcp import server


async def test_ci_caselaw_filters():
    out = await server.search_caselaw("ci", "", limit=5, filters={"matter": "pen", "nature": "REJET"})
    assert "sigcc.courdecassation.ci" in out and "REJET" in out, out
    assert "Bad request" in await server.search_caselaw("ci", "x", filters={"matter": "civil"})


async def test_ci_decision_pdf_text_and_id_variant():
    out = await server.get_decision("ci", "arret-n-201-24-du-27-fevrier-2024-2-1.pdf")
    assert "2024-02-27" in out and "LA COUR" in out and "201/24" in out, out[:800]


async def test_ci_provision_label_variants():
    a = await server.get_legislation_provision("ci", "loi-relatif-au-mariage", "Article 2")
    b = await server.get_legislation_provision("ci", "loi-relatif-au-mariage", "art. 2")
    assert "dix -huit ans" in a and "dix -huit ans" in b, a
    toc = await server.get_legislation_toc("ci", "loi-relatif-au-mariage")
    assert "CHAPITRE II" in toc and "CONTRACTER MARIAGE" in toc, toc[:1500]


async def test_ci_law_search_accent_insensitive():
    out = await server.search_legislation("ci", "acces information")
    assert "2013-867" in out, out
