"""Live smoke tests against eakta.birosag.hu. Needs network."""
import re

from world_legal_mcp import server


async def test_hu_search_caselaw_filters():
    out = await server.search_caselaw("hu", "munkaviszony", limit=3,
                                      filters={"court": "Kúria", "branch": "munkaügyi",
                                               "year_from": "2023"})
    assert "Hungary (hu) case law" in out and 'get_decision("hu", "Kúria Mfv.' in out
    years = re.findall(r"### \d+\. Kúria \S+ \((\d{4})\)", out)
    assert years and all(int(y) >= 2023 for y in years)
    bad = await server.search_caselaw("hu", "munkaviszony", filters={"branch": "xx"})
    assert bad.startswith("Bad request (hu)")


async def test_hu_get_decision():
    out = await server.get_decision("hu", "Kúria Pfv.21761/2017/4", max_chars=5000)
    assert out.startswith("# Kúria Pfv.21761/2017/4")
    assert "- Date: 2018-09-24" in out and "Kollégium: polgári" in out
    assert "A Kúria" in out and "ítélete" in out
