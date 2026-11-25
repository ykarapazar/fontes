"""Live smoke tests against api.webgjk-ks.org and gzk.rks-gov.net. Needs network."""
import re

from world_legal_mcp import server


async def test_xk_search_caselaw_filters():
    out = await server.search_caselaw("xk", "pronës", limit=3,
                                      filters={"language": "en", "referral": "KI"})
    assert "Kosovo (xk) case law" in out
    nums = re.findall(r"- Case number: (\S+)", out)
    assert nums and all(n.startswith("KI") for n in nums)
    assert re.search(r'get_decision\("xk", "\d+/en"\)', out)
    bad = await server.search_caselaw("xk", "pronës", filters={"referral": "zz"})
    assert bad.startswith("Bad request (xk)")


async def test_xk_get_decision_english():
    out = await server.get_decision("xk", "9583/en", max_chars=3000)
    assert out.startswith("# Gjykata Kushtetuese KI145/26")
    assert "- Language of text: en" in out and "- Published: 2026-10-30" in out
    assert "Constitutional Court of the Republic of Kosovo" in out


async def test_xk_legislation_search_and_provision():
    out = await server.search_legislation("xk", "04/L-077", limit=3)
    assert "- Number: 04/L-077" in out and 'get_legislation_toc("xk", "2828")' in out
    prov = await server.get_legislation_provision("xk", "3702", "Neni 24")
    assert "**Neni 24 [Barazia para Ligjit]**" in prov
    assert "Të gjithë janë të barabartë para ligjit" in prov

