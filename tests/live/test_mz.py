"""Live smoke tests against the Tribunal Supremo (ts.gov.mz) and the Conselho Constitucional
(cconstitucional.org.mz). Needs network. Throttled to one request per second per host."""
from world_legal_mcp import server


async def test_mz_court_filter_cc_number_search_and_slug_roundtrip():
    out = await server.search_caselaw("mz", "12/CC/2024", limit=5, filters={"court": "cc"})
    assert "cconstitucional.org.mz/jurisprudencia/" in out and "Tribunal Supremo" not in out, out
    d = await server.get_decision("mz", "acordao-n-o-12-cc-2024-de-2-de-outubro")
    assert "12/CC/2024" in d and "2024-10-02" in d, d[:500]


async def test_mz_tsr_filter_only_returns_tsr():
    out = await server.search_caselaw("mz", "apelação", limit=10, filters={"court": "tsr"})
    assert "Tribunal Superior de Recurso" in out and "Tribunal Supremo," not in out, out
    assert "Bad request" in await server.search_caselaw("mz", "x", filters={"court": "tribunal"})


async def test_mz_decision_id_variants():
    # The PDF url and the path with '.pdf' resolve to the same judgment.
    url = "https://www.ts.gov.mz/wp-content/uploads/2024/01/Processo-2.pdf"
    a = await server.get_decision("mz", url, max_chars=2000)
    b = await server.get_decision("mz", "2024/01/Processo-2.pdf", max_chars=2000)
    assert "02/1999" in a and "arrendamento" in a.lower() and a == b, a[:500]


async def test_mz_provision_label_variants():
    law = "2024/05/Lei-No-13-2023-de-25-de-Agosto-NOVA-LEI-DO-TRABALHO-BR_165_I_SEI_RIE_2Ao__230831_091658"
    for label in ("Artigo 5", "art. 5", "5"):
        out = await server.get_legislation_provision("mz", law, label)
        assert "Princípios e interpretação do Direito do Trabalho" in out, (label, out[:400])
