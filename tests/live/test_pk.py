"""Live smoke tests against mis.ihc.gov.pk (Islamabad High Court). Needs network."""
from world_legal_mcp import server

RFA56 = "judgements/211268/2/R.F.A_NO._56_OF_2026_(contested)_639294682208399606.pdf"


async def test_pk_caselaw_parties_and_reported_filters():
    out = await server.search_caselaw("pk", "Shawana", limit=5, filters={"parties": "Shawana"})
    assert "Regular First Appeal-56-2026" in out and "Dr Kamran Nazir Ahmed v Dr Shawana" in out, out
    out = await server.search_caselaw("pk", "khula", limit=3, filters={"reported": "afr"})
    assert out.count("Approved for reporting") == 3, out


async def test_pk_decision_by_url_with_metadata():
    out = await server.get_decision("pk", f"https://mis.ihc.gov.pk/attachments/{RFA56}", max_chars=3000)
    assert "Regular First Appeal-56-2026" in out and "Muhammad Asif" in out, out
    assert "R.F.A NO. 56 OF 2026" in out and "2026-10-30" in out, out


async def test_pk_bad_input():
    assert "at least 5 letters" in await server.search_caselaw("pk", "x", filters={"parties": "ab"})
    assert "Bad request" in await server.get_decision("pk", "../etc/passwd")
    assert "reported must be" in await server.search_caselaw("pk", "bail", filters={"reported": "x"})
