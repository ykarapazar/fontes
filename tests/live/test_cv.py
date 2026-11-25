"""Live smoke tests against the Cabo Verde sources (tribunalconstitucional.cv, stj.cv).
Needs network; 1 s per request per host."""
from world_legal_mcp import server


async def test_cv_tc_decision_and_url_id():
    out = await server.get_decision("cv", "3488")
    assert "Acórdão n.º 3/2020" in out and "2020-02-14" in out and "amparo" in out, out[:800]
    url = ("https://www.tribunalconstitucional.cv/index.php/download/179/todos-os-ficheiros/3488/"
           "Acordao%203-2020.pdf")
    assert "Acórdão n.º 3/2020" in await server.get_decision("cv", url)


async def test_cv_stj_section_and_year_filters():
    hits = await server.search_caselaw("cv", "habeas corpus", filters={"section": "criminal", "year": "2025"})
    assert "Supremo Tribunal de Justiça, 2ª Secção Criminal" in hits and "-2025" in hits, hits[:1500]
    assert "Tribunal Constitucional" not in hits.split("STJ:")[0], hits[:1500]
    bad = await server.search_caselaw("cv", "x", filters={"section": "penal"})
    assert "Bad request" in bad, bad


async def test_cv_bad_ids_never_fetch():
    assert "Bad request" in await server.get_decision("cv", "../../wp-admin")
    assert "Bad request" in await server.get_legislation_text("cv", "Código Civil")
    out = await server.get_decision("cv", "2099/01/Not-Listed.pdf")
    assert "Not found" in out, out


async def test_cv_civil_code_provision_labels():
    hits = await server.search_legislation("cv", "Código Civil")
    assert "323" in hits, hits[:1500]
    a = await server.get_legislation_provision("cv", "323", "Artigo 483.º")
    assert "Princípio geral" in a and "dolo ou mera culpa" in a, a[:800]
    b = await server.get_legislation_provision("cv", "323", "art. 1º")
    assert "Fontes imediatas" in b, b[:800]


async def test_cv_juris_stj_search_and_decision():
    """JURIS CV (CSMJ): STJ archive with full text; 10 s spacing (robots Crawl-delay)."""
    hits = await server.search_caselaw("cv", "", limit=3, filters={"court": "stj", "year": "1994"})
    assert "JURIS:CV:STJ:1994:" in hits and "1994-" in hits and "Court: Tribunal da Relação" not in hits, hits[:1500]
    out = await server.get_decision("cv", "JURIS:CV:STJ:2026:1299", max_chars=2000)
    assert "Supremo Tribunal de Justiça" in out and "2026-02-27" in out and "Acordam" in out, out[:1500]
    assert "commercial use is forbidden" in out
