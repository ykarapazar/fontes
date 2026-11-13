"""Monaco (Legimonaco) adapter checks that the shared conformance suite does not cover."""
from world_legal_mcp import server

CC = "code/code-civil"


async def test_mc_provision_label_variants():
    a = await server.get_legislation_provision("mc", CC, "Article 1")
    b = await server.get_legislation_provision("mc", "https://legimonaco.mc/code/code-civil/", "1er")
    c = await server.get_legislation_provision("mc", "/code/code-civil@2025.09.30", "art. 1")
    assert a == b == c and "promulgation par le Prince" in a


async def test_mc_decision_by_idbd_equals_path():
    a = await server.get_decision(
        "mc", "jurisprudence/commission-arbitrale-loyers-commerciaux/2024/05-15-30935")
    b = await server.get_decision("mc", "30935")
    assert a == b and "COMMISSION ARBITRALE DES LOYERS COMMERCIAUX" in a


async def test_mc_court_and_date_filters():
    out = await server.search_caselaw("mc", "licenciement", limit=5,
                                      filters={"court": "cour-revision", "date_from": "2020-01-01"})
    assert "Court: Cour de révision" in out and "Court: Cour d'appel" not in out
    bad = await server.search_caselaw("mc", "x", filters={"court": "nope"})
    assert "cour-revision" in bad


async def test_mc_legislation_type_filter_and_code_first():
    out = await server.search_legislation("mc", "code civil", limit=3)
    assert "code/code-civil" in out.split("### 2.")[0]
    law = await server.search_legislation("mc", "baux commerciaux", limit=3,
                                          filters={"type": "law"})
    assert "tnc/loi/1948/11-24-490" in law and "Type: Code" not in law
