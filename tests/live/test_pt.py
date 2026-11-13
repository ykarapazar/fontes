"""Live smoke tests against DGSI, the Tribunal Constitucional and PGDL (www.pgdlisboa.pt).
Needs network. Every host is spaced at 1 s, and PGDL pages are ~0.5 MB, so this is slow."""
import re

from world_legal_mcp import server


async def test_pt_dgsi_court_and_date_filter():
    out = await server.search_caselaw("pt", "indemnização", limit=2, filters={
        "court": "trl", "date_from": "2023-01-01", "date_to": "2023-12-31"})
    assert "Tribunal da Relação de Lisboa" in out
    dates = re.findall(r"- Date: (\d{4})-\d\d-\d\d", out)
    assert len(dates) == 2 and set(dates) == {"2023"}, out


async def test_pt_decision_id_variants():
    for ident in ("jstj/28e9313db456f62880258354005e7fba", "2478/16.1T8GMR.G1.S2"):
        out = await server.get_decision("pt", ident, max_chars=3000)
        assert "Date: 2018-11-27" in out and "ALEXANDRE REIS" in out and "## Sumário" in out


async def test_pt_constitutional_court_round_trip():
    out = await server.search_caselaw("pt", "liberdade de expressão", limit=2,
                                      filters={"court": "tc", "date_from": "2020-01-01"})
    ids = re.findall(r'get_decision\("pt", "(tc:\d{8})"', out)
    assert ids, out
    dec = await server.get_decision("pt", ids[0], max_chars=3000)
    assert "Tribunal Constitucional" in dec and "Processo n.º" in dec
    by_number = await server.get_decision("pt", "tc:205/2026", max_chars=500)
    assert "Identifier: tc:20260205" in by_number and "Date: 2026-02-26" in by_number


async def test_pt_civil_code_provision_labels():
    for prov in ("Artigo 1022.º", "1022", "art. 1022"):
        out = await server.get_legislation_provision("pt", "775", prov)
        assert "CÓDIGO CIVIL" in out and "Locação é o contrato" in out
    suffixed = await server.get_legislation_provision("pt", "775", "1067-A")
    assert "Artigo 1067.º-A" in suffixed and "discriminado" in suffixed
