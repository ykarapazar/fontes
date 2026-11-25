"""Live smoke tests against the E-lietas portāls gateway (gateway.elieta.lv). Needs network.
Throttled to one request per second."""
from world_legal_mcp import server

SENATS = "ECLI:LV:AT:2020:1111.C24127717.16.S"  # Senāts, civil, rent arrears, 11.11.2020


async def test_lv_supreme_court_and_date_filters():
    out = await server.search_caselaw("lv", "īres līgums", limit=5,
                                      filters={"court": "supreme", "process_type": "civil",
                                               "date_from": "2020-01-01", "date_to": "2020-12-31"})
    assert "Augstākās tiesas Senāts" in out and SENATS in out
    assert "2020-" in out and "2021-" not in out


async def test_lv_decision_text_and_ecli_variants():
    a = await server.get_decision("lv", SENATS)
    b = await server.get_decision("lv", SENATS.lower())
    assert a == b
    assert "Senāta spriedums" in a and "SKC-792/2020" in a and "[1.1] Sākotnēji" in a
    assert "/pers. B/" in a  # anonymised by the court


async def test_lv_bad_filter_and_unknown_ecli():
    bad = await server.search_caselaw("lv", "īres līgums", filters={"process_type": "tax"})
    assert bad.startswith("Bad request (lv)")
    out = await server.get_decision("lv", "ECLI:LV:AT:2020:0101.X00000000.1.S")
    assert "Not found" in out
