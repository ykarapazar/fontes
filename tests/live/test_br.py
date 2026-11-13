"""Live smoke tests against STF jurisprudência and normas.leg.br. Needs network."""
from world_legal_mcp import server

CC = "urn:lex:br:federal:lei:2002-01-10;10406"


async def test_br_provision_labels_and_alias():
    for law, label in ((CC, "Art. 186"), ("cc", "186"), (f"https://normas.leg.br/?urn={CC}", "art. 186")):
        out = await server.get_legislation_provision("br", law, label)
        assert "Art. 186" in out and "comete ato ilícito" in out, (law, label)


async def test_br_amended_and_inserted_articles():
    """Current text, not the original: art. 3 was rewritten in 2015 and its incisos repealed."""
    out = await server.get_legislation_provision("br", "cc", "3º")
    assert "menores de 16 (dezesseis) anos" in out and "(Revogado)" in out
    ins = await server.get_legislation_provision("br", "cc", "1.358-A")
    assert "Art. 1.358-A" in ins and "condôminos" in ins


async def test_br_search_legislation_by_number():
    out = await server.search_legislation("br", "10406", limit=3)
    assert CC in out


async def test_br_stf_sumulas_and_bad_input():
    out = await server.search_caselaw("br", "tráfico", limit=3, filters={"base": "sumulas"})
    assert "Súmula" in out
    bad = await server.search_caselaw("br", "x", filters={"base": "stj"})
    assert bad.startswith("Bad request (br)")
