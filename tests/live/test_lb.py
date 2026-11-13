"""Live smoke tests against the Lebanese Constitutional Council site (www.cc.gov.lb).
Needs network; 1 s per request."""
import re

from world_legal_mcp import server


async def test_lb_electoral_list_and_filters():
    out = await server.search_caselaw("lb", "", limit=3,
                                      filters={"type": "electoral", "election_year": "2022"})
    ids = re.findall(r"electoral/\d+/(\d{4})", out)
    assert ids and set(ids) <= {"2022", "2023"}, out
    bad = await server.search_caselaw("lb", "x", filters={"type": "supreme"})
    assert "constitutional" in bad and "electoral" in bad
    bad = await server.search_caselaw("lb", "x", filters={"election_year": "2022"})
    assert "type=electoral" in bad


async def test_lb_decision_round_trip_and_bad_id():
    out = await server.search_caselaw("lb", "عفو", limit=4, filters={"number": "12"})
    assert "constitutional/12/2026" in out, out
    dec = await server.get_decision("lb", "constitutional/12/2026", max_chars=3000)
    assert "2026-10-12" in dec and "القانون رقم 70" in dec, dec[:1500]
    bad = await server.get_decision("lb", "12/2026")
    assert "constitutional/12/2026" in bad


async def test_lb_provision_label_variants():
    for prov in ("المادة 19", "19", "مادة 19"):
        out = await server.get_legislation_provision("lb", "constitution", prov)
        assert "المادة 19" in out and "مجلس دستوري" in out, out[:600]
    for prov in ("Article 19", "art. 19"):
        out = await server.get_legislation_provision("lb", "constitution/en", prov)
        assert "Article 19" in out and "Constitutional Council" in out, out[:600]
    pre = await server.get_legislation_provision("lb", "constitution", "فقرة (ب)")
    assert "عربي الهوية" in pre or "عربي" in pre, pre[:600]
