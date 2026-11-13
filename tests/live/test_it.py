"""Live smoke tests against Normattiva (api.normattiva.it + www.normattiva.it). Needs network."""
from world_legal_mcp import server

L241 = "urn:nir:stato:legge:1990-08-07;241"
CC = "urn:nir:stato:regio.decreto:1942-03-16;262"


async def test_it_citation_query_parsed_into_filters():
    out = await server.search_legislation("it", "legge 241/1990", limit=3)
    assert L241 in out and "procedimento amministrativo" in out
    same = await server.search_legislation("it", "procedimento", limit=3,
                                           filters={"type": "LEGGE", "number": "241", "year": "1990"})
    assert L241 in same


async def test_it_provision_label_variants_and_bis():
    a = await server.get_legislation_provision("it", L241, "3")
    b = await server.get_legislation_provision("it", L241, "Art. 3")
    assert a == b and "Motivazione del provvedimento" in a
    bis = await server.get_legislation_provision("it", L241, "art. 14-ter")
    assert "Conferenza simultanea" in bis


async def test_it_codice_civile_annexes():
    cc = await server.get_legislation_provision("it", CC, "articolo 2043")
    assert "fatto illecito" in cc and "danno ingiusto" in cc
    preleggi = await server.get_legislation_provision("it", CC, "art. 12 (all. 1)")
    assert "Interpretazione della legge" in preleggi
    toc = await server.get_legislation_toc("it", CC, keyword="2043")
    assert "art. 2043" in toc


async def test_it_unknown_article_is_not_found():
    out = await server.get_legislation_provision("it", L241, "art. 999")
    assert "not found" in out.lower()


async def test_it_costituzione_search_and_transitional_provisions():
    out = await server.search_legislation("it", "Costituzione", limit=3)
    assert "urn:nir:stato:costituzione:1947-12-27" in out
    art1 = await server.get_legislation_provision("it", "urn:nir:stato:costituzione:1947-12-27", "art. 1")
    assert "fondata sul lavoro" in art1
    xviii = await server.get_legislation_provision("it", "urn:nir:stato:costituzione:1947-12-27",
                                                   "art. XVIII (all. 1)")
    assert "promulgata dal Capo provvisorio" in xviii
