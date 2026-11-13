"""Luxembourg (Legilux) adapter checks that the shared conformance suite does not cover."""
from world_legal_mcp import server


async def test_lu_provision_label_variants():
    a = await server.get_legislation_provision("lu", "eli/etat/leg/code/civil", "Art. 1er")
    b = await server.get_legislation_provision("lu", "eli/etat/leg/code/civil", "1")
    c = await server.get_legislation_provision("lu", "eli/etat/leg/code/civil/", "article 1er")
    assert a == b == c and "Art. 1er" in a and "lois" in a.lower()


async def test_lu_id_variants_resolve_to_latest_consolidation():
    url = ("https://legilux.public.lu/eli/etat/leg/loi/2018/08/01/a686/"
           "consolide/20251226/fr")
    a = await server.get_legislation_provision("lu", url, "Art. 1er")
    b = await server.get_legislation_provision("lu", "eli/etat/leg/loi/2018/08/01/a686",
                                               "1")
    assert a == b and "Commission nationale" in a


async def test_lu_search_ranks_code_first():
    out = await server.search_legislation("lu", "code civil", limit=3)
    assert "eli/etat/leg/code/civil" in out.split("### 2.")[0]


async def test_lu_long_titles_do_not_break_search():
    # Virtuoso rejected sort rows over ~11 kB until titles were capped.
    out = await server.search_legislation("lu", "travail", limit=5)
    assert "Code du travail" in out and not out.startswith("Error")


async def test_lu_cassation_lists_by_case_number_and_opens_one_pdf():
    out = await server.search_caselaw("lu", "CAS-2022-00031", limit=3)
    assert "2023/20230112_CAS-2022-00031" in out and "Cour de cassation" in out
    dec = await server.get_decision("lu", "2023/20230112_CAS-2022-00031_2_pseudonymisé")
    assert "Audience publique de la Cour de cassation" in dec


async def test_lu_cassation_text_search_needs_a_narrow_set():
    wide = await server.search_caselaw("lu", "responsabilité", filters={"year": "2023"})
    assert "narrow with date_from/date_to" in wide
    narrow = await server.search_caselaw(
        "lu", "cassation", filters={"date_from": "2023-01-12", "date_to": "2023-01-12"})
    assert "Text searched in" in narrow and "CAS-2022-00031" in narrow
