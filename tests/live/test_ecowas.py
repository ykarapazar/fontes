"""Live smoke tests against the ECOWAS Court of Justice site (courtecowas.org). Needs network;
1 s per request; the first call reads the whole decision list (~21 requests)."""
from world_legal_mcp import server


async def test_ecowas_search_filters_and_numbers():
    out = await server.search_caselaw("ecowas", "Togo", limit=20, filters={
        "type": "judgement", "date_from": "2020-06-01", "date_to": "2020-06-30"})
    assert "ECW/CCJ/JUD/09/20" in out, out          # Amnesty International Togo & 7 Ors v. Togo
    by_suit = await server.search_caselaw("ecowas", "ECW/CCJ/APP/08/08")
    assert "ECW/CCJ/JUD/06/08" in by_suit and "KORAOU" in by_suit, by_suit
    bad = await server.search_caselaw("ecowas", "x", filters={"type": "verdict"})
    assert "judgement, opinion, order or ruling" in bad


async def test_ecowas_shared_number_and_language_ids():
    out = await server.search_caselaw("ecowas", "ECW/CCJ/JUD/01/26")
    assert "ECW/CCJ/JUD/01/26 (Ruling)" in out and "LIGUE TOGOLAISE" in out, out
    pt = await server.search_caselaw("ecowas", "Hassan Kargbo")
    assert "ECW/CCJ/JUD/37/24" in pt and "PT" in pt


async def test_ecowas_decision_text_and_scanned_pdf():
    out = await server.get_decision("ecowas", "ecw/ccj/jud/19/15", max_chars=3000)
    assert "HOPE DEMOCRATIC PARTY" in out.upper() and "COMMUNITY COURT OF JUSTICE" in out, out[:800]
    scanned = await server.get_decision("ecowas", "ECW/CCJ/JUD/43/26")   # image-only PDF
    assert "text layer" in scanned and "courtecowas.org" in scanned
    missing = await server.get_decision("ecowas", "ECW/CCJ/JUD/99/99")
    assert "no decision" in missing.lower()


async def test_ecowas_law_reports_volume():
    out = await server.search_caselaw("ecowas", "Habre", filters={"report_year": "2010"})
    assert "(2010) CCJELR 43" in out and "ECW/CCJ/JUD/06/10" in out, out
    dec = await server.get_decision("ecowas", "ECW/CCJ/JUD/01/04", max_chars=3000)   # first reported case
    assert "AFOLABI" in dec.upper() and "(2004-2009) CCJELR 1" in dec, dec[:800]
    shared = await server.get_decision("ecowas", "ECW/CCJ/RUL/03/10")     # printed for two decisions
    assert "(2010) CCJELR 213" in shared and "Bad request" in shared
    bad = await server.search_caselaw("ecowas", "x", filters={"report_year": "2019"})
    assert "2010-2017" in bad
