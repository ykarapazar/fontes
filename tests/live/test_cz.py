"""Live smoke tests against rozhodnuti.justice.cz and e-Sbírka. Needs network."""
import re

from world_legal_mcp import server


async def test_cz_search_caselaw_filters():
    out = await server.search_caselaw("cz", "nájem bytu", limit=3,
                                      filters={"court": "VSPH", "date_from": "2024-01-01"})
    assert "Czechia (cz) case law" in out and 'get_decision("cz", "ECLI:CZ:VSPH:' in out
    years = re.findall(r"- Date: (\d{4})", out)
    assert years and all(int(y) >= 2024 for y in years)
    bad = await server.search_caselaw("cz", "nájem", filters={"court": "XX"})
    assert bad.startswith("Bad request (cz)")


async def test_cz_get_decision():
    out = await server.get_decision("cz", "ECLI:CZ:OSTP:2025:17.C.197.2025.1", max_chars=5000)
    assert out.startswith("# Okresní soud v Teplicích, 17 C 197/2025")
    assert "## Výrok" in out and "[Jméno žalobce]" in out



async def test_cz_provision_labels():
    for law, label in (("89/2012 Sb.", "§ 2"), ("89/2012", "2"), ("sb/2012/89", "par. 2")):
        out = await server.get_legislation_provision("cz", law, label)
        assert out.startswith("# Zákon č. 89/2012 Sb., občanský zákoník: § 2"), (law, label)
        assert "dobrými mravy" in out


async def test_cz_supreme_court_sbirka():
    out = await server.search_caselaw("cz", "úroky z prodlení", limit=3, filters={"court": "NS"})
    assert 'get_decision("cz", "sbirka:' in out
    out = await server.get_decision("cz", "ECLI:CZ:NS:2025:25.CDO.2340.2024.1", max_chars=3000)
    assert "25 Cdo 2340/2024" in out and "Právní věta" in out
    old = await server.get_decision("cz", "sbirka:22718", max_chars=2000)
    assert "Kr II 8/19" in old


async def test_cz_supreme_administrative_court():
    out = await server.search_caselaw("cz", "", limit=3,
                                      filters={"court": "NSS", "case_number": "4 As 41/2026"})
    assert 'get_decision("cz", "nssoud:786898")' in out
    out = await server.get_decision("cz", "ECLI:CZ:NSS:2026:4.As.41.2026.46", max_chars=3000)
    assert "4 As 41/2026-46" in out and "Nejvyšší správní soud" in out
