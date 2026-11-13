"""Live smoke tests against sodnapraksa.si and PISRS. Needs network."""
import re

from world_legal_mcp import server


async def test_si_search_caselaw_filters():
    out = await server.search_caselaw("si", "najemna pogodba", limit=3,
                                      filters={"court": "vsrs", "date_from": "2024-01-01"})
    assert "Slovenia (si) case law" in out and 'get_decision("si", "ECLI:SI:VSRS:' in out
    years = re.findall(r"- Date: (\d{4})", out)
    assert years and all(int(y) >= 2024 for y in years)
    bad = await server.search_caselaw("si", "najem", filters={"court": "xx"})
    assert bad.startswith("Bad request (si)")


async def test_si_get_decision():
    out = await server.get_decision("si", "ECLI:SI:VSRS:1999:U.938.95", max_chars=5000)
    assert out.startswith("# Vrhovno sodišče Republike Slovenije U 938/95")
    assert "## Izrek" in out and "## Obrazložitev" in out and "ZDen" in out


async def test_si_search_legislation():
    out = await server.search_legislation("si", "obligacijski zakonik", limit=3)
    assert 'get_legislation_toc("si", "ZAKO1263")' in out


async def test_si_provision_labels():
    for law, label in (("ZAKO1263", "1. člen"), ("zako1263", "1"), ("ZAKO1263", "čl. 1")):
        out = await server.get_legislation_provision("si", law, label)
        assert out.startswith("# Obligacijski zakonik (OZ): 1. člen"), (law, label)
        assert "temeljna načela" in out
    out = await server.get_legislation_provision("si", "ZAKO1263", "382a")
    assert "382.a člen" in out and "Pogodbene obresti nehajo teči" in out
