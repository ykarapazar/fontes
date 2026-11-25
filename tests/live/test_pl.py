"""Live smoke tests against the Sejm ELI API and orzeczenia.ms.gov.pl. Needs network."""
import re

from world_legal_mcp import server

DOC = "155515000004027_VIII_GC_000386_2020_Uz_2021-05-13_001"


async def test_pl_search_caselaw_filters():
    out = await server.search_caselaw("pl", "umowa najmu", limit=3,
                                      filters={"date_from": "2025-01-01", "sort": "date"})
    years = re.findall(r"- Date: (\d{4})", out)
    assert years and all(int(y) >= 2025 for y in years)
    bad = await server.search_caselaw("pl", "umowa najmu", filters={"sort": "x"})
    assert "Bad request" in bad


async def test_pl_get_decision():
    out = await server.get_decision("pl", DOC, max_chars=3000)
    assert out.startswith("# Sąd Okręgowy w Szczecinie VIII GC 386/20")
    assert "- Podstawa prawna:" in out and "WYROK" in out


async def test_pl_provision_labels():
    for law, label in (("DU/1964/93", "art. 415"), ("Dz.U. 1964 nr 16 poz. 93", "415"),
                       ("WDU19640160093", "Art. 415")):
        out = await server.get_legislation_provision("pl", law, label)
        assert out.startswith("# Ustawa z dnia 23 kwietnia 1964 r. - Kodeks cywilny: art. 415"), (law, label)
        assert "Kto z winy swej wyrządził drugiemu szkodę" in out
        assert "Consolidated text: Dz.U." in out
    out = await server.get_legislation_provision("pl", "DU/1964/93", "449¹")
    assert "art. 449^1" in out
