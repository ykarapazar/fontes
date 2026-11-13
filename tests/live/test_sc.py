"""Live smoke tests against judiciary.sc (decisions list) and gazette.sc (Acts, S.I.s, Bills).
Needs network. Throttled: 2 s per request on judiciary.sc, 1 s on gazette.sc."""
from world_legal_mcp import server


async def test_sc_law_id_variants_provision_labels_and_errors():
    a = await server.get_legislation_provision("sc", "Act 14 of 2026", "2")
    b = await server.get_legislation_provision("sc", "act no. 14/2026", "s. 2")
    c = await server.get_legislation_provision("sc", "Act 14 2026", "section 2")
    assert a == b == c
    assert "Amendment of section 2" in a and "Trusts Act, 2021" in a
    toc = await server.get_legislation_toc("sc", "Act 14 of 2026")
    assert "1. Short title" in toc and "6. Amendment of section 37" in toc
    assert (await server.get_legislation_toc("sc", "trusts act")).startswith("Bad request (sc)")
    assert "not found" in (await server.get_legislation_text("sc", "Act 999 of 2026")).lower()


async def test_sc_legislation_type_filter_and_si():
    out = await server.search_legislation("sc", "trusts", limit=5, filters={"type": "bill"})
    assert "Bill 14 of 2026" in out and "Act 14 of 2026" not in out
    bad = await server.search_legislation("sc", "trusts", filters={"type": "treaty"})
    assert bad.startswith("Bad request (sc)")
    si = await server.get_legislation_provision("sc", "S.I. 69 of 2026", "regulation 1")
    assert "may be cited as" in si


async def test_sc_decision_citation_variants_court_filter_and_errors():
    hits = await server.search_caselaw("sc", "", limit=5, filters={"court": "constitutional",
                                                                    "year": "2026"})
    assert "SCCC" in hits and "SCSC" not in hits
    a = await server.search_caselaw("sc", "2026 SCCC 4")
    assert "Valabhji" in a
    bad = await server.search_caselaw("sc", "", filters={"court": "Privy Council"})
    assert bad.startswith("Bad request (sc)")
    assert (await server.get_decision("sc", "valabhji v republic")).startswith("Bad request (sc)")
    assert "not found" in (await server.get_decision("sc", "[2026] SCSC 9999")).lower()


async def test_sc_constitution_and_codes_from_judiciary_laws_page():
    hits = await server.search_legislation("sc", "constitution", limit=5)
    assert hits.index("Constitution") < hits.index("Act ") if "Act " in hits else "Constitution" in hits
    art = await server.get_legislation_provision("sc", "constitution", "article 27")
    assert "Right to equal protection of the law" in art
    assert "Members of the Commission" in await server.get_legislation_provision(
        "sc", "Constitution", "115A")
    codes = await server.search_legislation("sc", "", filters={"type": "revised"})
    assert "penal-code" in codes and "criminal-procedure-code-1952-cap-54" in codes
    murder = await server.get_legislation_provision("sc", "penal-code", "s. 193")
    assert "Murder" in murder and "malice aforethought" in murder
    assert "22 October 2021" in await server.get_legislation_text("sc", "penal-code")
