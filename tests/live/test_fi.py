"""Live smoke tests against the Finlex open data API and finlex.fi. Needs network."""
from world_legal_mcp import server


async def test_fi_search_caselaw_filters():
    out = await server.search_caselaw("fi", "vahingonkorvaus", limit=3,
                                      filters={"court": "KKO", "year": "2025"})
    assert "Finland (fi) case law" in out and 'get_decision("fi", "ECLI:FI:KKO:2025:' in out
    assert "KHO:" not in out
    bad = await server.search_caselaw("fi", "vero", filters={"court": "HO"})
    assert bad.startswith("Bad request (fi)")


async def test_fi_get_decision_id_variants():
    for did in ("ECLI:FI:KKO:2025:1", "KKO:2025:1"):
        out = await server.get_decision("fi", did, max_chars=3000)
        assert out.startswith("# KKO:2025:1"), did
        assert "Date: 2025-01-07" in out and "R2022/667" in out


async def test_fi_provision_labels():
    for law, label in (("39-001/1889", "3 luku 1 §"), ("39/1889", "3:1"),
                       ("1889/39-001", "RL 3 luku 1§")):
        out = await server.get_legislation_provision("fi", law, label)
        assert out.startswith("# Rikoslaki: 3 luku 1 §"), (law, label)


async def test_fi_swedish_and_continuous_numbering():
    # Oikeustoimilaki numbers sections across chapters, so "33 §" alone is enough.
    out = await server.get_legislation_provision("fi", "228/1929/swe", "33 §")
    assert out.startswith("# Lag om rättshandlingar på förmögenhetsrättens område: 3 ")
    assert out.splitlines()[0].endswith(" 33 §")


async def test_fi_non_precedent_kinds():
    out = await server.search_caselaw("fi", "", limit=3,
                                      filters={"court": "KHO", "kind": "short", "year": "2021"})
    assert 'get_decision("fi", "KHO:lyhyt:2021:' in out
    for did, want in (("KHO:muut:2025:3030", "3562/2025"), ("KKO 1424/2025", "S2025/64"),
                      ("KKO:VL:2026:258", "S 1/2026/2199")):
        out = await server.get_decision("fi", did, max_chars=2000)
        assert want in out, did
    bad = await server.get_decision("fi", "KKO:lyhyt:2021:1")
    assert bad.startswith("Bad request (fi)")
