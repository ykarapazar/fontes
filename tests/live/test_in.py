"""Live smoke tests against India Code's DSpace REST API (indiacode.gov.in/server/api) and the
Indian Supreme Court Judgments AWS Open Data bucket. Needs network."""
import re

from world_legal_mcp import server
import pytest

from world_legal_mcp.base import permitted_codes

needs_permission = pytest.mark.skipif("in" not in permitted_codes(),
                                      reason="source needs permission: set WLM_PERMITTED=in")

ICA = "AC_CEN_3_20_00035_187209_1523268996428"   # Indian Contract Act, 1872


@needs_permission
async def test_in_search_defaults_to_central_acts():
    out = await server.search_legislation("in", "Indian Contract Act", limit=5)
    assert "The Indian Contract Act, 1872" in out and ICA in out
    assert "Chhattisgarh" not in out        # state adaptation filtered out by default
    out = await server.search_legislation("in", "Bharatiya Nyaya Sanhita", limit=3,
                                          filters={"year": "2023"})
    assert "AC_CEN_5_23_00048_2023-45_1719292564123" in out


@needs_permission
async def test_in_provision_label_and_law_id_variants():
    for law_id, prov in ((ICA, "s. 10"), ("9 of 1872", "Section 10"), ("Act 9 of 1872", "10")):
        out = await server.get_legislation_provision("in", law_id, prov)
        assert "Section 10. What agreements are contracts" in out, (law_id, prov)
        assert "free consent" in out
    bns = await server.get_legislation_provision("in", "45 of 2023", "§ 10")
    assert "Bharatiya Nyaya Sanhita" in bns and "lowest punishment" in bns


@needs_permission
async def test_in_lettered_section_and_footnote():
    out = await server.get_legislation_provision("in", ICA, "19a")
    assert "Section 19A" in out and "undue influence" in out
    assert re.search(r"Ins\. by Act 6 of 1899", out)


@needs_permission
async def test_in_bad_inputs():
    assert (await server.get_legislation_provision("in", "contract act", "10")).startswith("Bad request (in)")
    assert (await server.get_legislation_provision("in", ICA, "9999")).startswith("Not found (in)")


async def test_in_sc_search_default_years_and_finds_by_party():
    out = await server.search_caselaw("in", "Kesavananda Bharati", limit=3)
    assert "No year given" in out and "S_1973_1_1_1002" not in out
    out = await server.search_caselaw("in", "Kesavananda Bharati", limit=3, filters={"year": "1973"})
    assert "KESAVANANDA BHARATI" in out and "S_1973_1_1_1002" in out


async def test_in_sc_id_variants():
    for cid in ("2024_10_108_125", "[2024] 10 S.C.R. 108", "2024 INSC 735"):
        out = await server.get_decision("in", cid)
        assert "Vijay Singh" in out and "2024-09-25" in out and "2024 INSC 735" in out, cid
    assert (await server.get_decision("in", "AIR 1973 SC 1461")).startswith("Bad request (in)")
