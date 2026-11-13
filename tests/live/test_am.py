"""Live smoke tests against www.arlis.am (Armenian Legal Information System)."""
import re

from world_legal_mcp import server


async def test_am_cassation_search_year_filter():
    out = await server.search_caselaw("am", "վարձակալության", limit=3, filters={"year": "2015"})
    ids = re.findall(r'get_decision\("am", "(\d+)"\)', out)
    assert ids, out
    years = re.findall(r"- Date: (\d{4})", out)
    assert years and all(y == "2015" for y in years), out
    bad = await server.search_caselaw("am", "x", filters={"court": "district"})
    assert bad.startswith("Bad request (am)")


async def test_am_decision_case_number():
    dec = await server.get_decision("am", "https://www.arlis.am/hy/acts/163951/latest",
                                    max_chars=3000)
    assert "3-1920 (ՎԴ)" in dec
    assert "ՎՃՌԱԲԵԿ ԴԱՏԱՐԱՆ" in dec


async def test_am_provision_label_variants():
    for label in ("Հոդված 1071¹", "1071^1", "art. 1071¹"):
        out = await server.get_legislation_provision("am", "29", label)
        assert "Հոդված 1071¹" in out.splitlines()[0], (label, out[:200])
        assert "Անշարժ գույքի սեփականատիրոջ պատասխանատվությունը" in out
    out = await server.get_legislation_provision("am", "29", "59.1")
    assert "Հոդված 59.1" in out.splitlines()[0]


async def test_am_legislation_status_filter():
    out = await server.search_legislation("am", "քաղաքացիական օրենսգիրք", limit=3,
                                          filters={"status": "in_force"})
    assert "ՀՕ-239" in out
    bad = await server.search_legislation("am", "օրենք", filters={"status": "maybe"})
    assert bad.startswith("Bad request (am)")
