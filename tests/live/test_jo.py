"""Live smoke tests against the Constitutional Court of Jordan (www.cco.gov.jo).
Needs network. 1 s spacing per request."""
import pytest

from world_legal_mcp import server
from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions.jo import Jordan


async def test_jo_full_text_search_and_judgment_round_trip():
    out = await server.search_caselaw("jo", "الضمان الاجتماعي", limit=10)
    assert "ProvisionDetails/1009" in out, out
    dec = await server.get_decision("jo", "ProvisionDetails/1003", max_chars=20000)
    assert "2026-06-03" in dec and "5/2026" in dec and "المحكمة الدستورية" in dec


async def test_jo_year_filter_and_paging_across_site_pages():
    out = await server.search_caselaw("jo", "", limit=5, filters={"year": "2024"})
    assert "8/2024" in out and "1/2025" not in out
    first = await Jordan().search_caselaw("", limit=10, page=9)
    assert first.items and all(h.id.startswith("ProvisionDetails/") for h in first.items)


async def test_jo_interpretive_decision():
    r = await Jordan().search_caselaw("", limit=3, filters={"kind": "interpretation"})
    assert r.items and all(h.id.startswith("DecisionDetails/") for h in r.items)
    dec = await Jordan().get_decision("https://www.cco.gov.jo/ar/custompages/DecisionDetails/1004")
    assert dec.date == "2022-05-10" and dec.case_number == "1/2022"


async def test_jo_bad_id():
    with pytest.raises(BadRequest):
        await Jordan().get_decision("1003")
