"""Live smoke tests against the nsud.sk open-data API and Slov-Lex. Needs network."""
from world_legal_mcp import server


async def test_sk_search_caselaw_filters():
    out = await server.search_caselaw("sk", "nájom bytu", limit=3, filters={"subject": "nájmu"})
    assert "Slovakia (sk) case law" in out and 'get_decision("sk", "ECLI:SK:NSSR:' in out
    bad = await server.search_caselaw("sk", "nájom", filters={"case_number": "4 Cdo 154"})
    assert bad.startswith("Bad request (sk)")


async def test_sk_get_decision_id_variants():
    for did in ("ECLI:SK:NSSR:2021:5019200331.1", "124230"):
        out = await server.get_decision("sk", did, max_chars=3000)
        assert out.startswith("# Najvyšší súd Slovenskej republiky, 4Usam/1/2020"), did
        assert "kasačnú sťažnosť" in out



async def test_sk_provision_labels():
    for law, label in (("40/1964 Zb.", "§ 2"), ("40/1964", "2"), ("SK/ZZ/1964/40", "par. 2")):
        out = await server.get_legislation_provision("sk", law, label)
        assert out.startswith("# 40/1964 Zb. Občiansky zákonník: § 2"), (law, out[:120])
    out = await server.get_legislation_provision("sk", "460/1992 Zb.", "čl. 1")
    assert "zvrchovaný, demokratický a právny štát" in out
