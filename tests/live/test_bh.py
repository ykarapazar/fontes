"""Live smoke tests against the Legislation and Legal Opinion Commission (www.lloc.gov.bh).
Needs network. 1 s spacing per request."""
import re

import pytest

from world_legal_mcp import server
from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions.bh import Bahrain
from world_legal_mcp.base import permitted_codes

pytestmark = pytest.mark.skipif("bh" not in permitted_codes(),
                                reason="source needs permission: set WLM_PERMITTED=bh")


async def test_bh_number_year_filter_and_provision_variants():
    out = await server.search_legislation("bh", "", limit=3, filters={
        "type": "K", "number": "19", "year_from": "2001", "year_to": "2001"})
    assert "L1901" in out and "القانون المدني" in out
    for label in ("128", "مادة 128", "المادة (128)", "art. 128", "١٢٨"):
        p = await server.get_legislation_provision("bh", "L1901", label)
        assert "العقد" in p.replace("ـ", "") and "شريعة المتعاقدين" in p
    first = await server.get_legislation_provision("bh", "l1901", "المادة الأولى")
    assert "يعمل بالقانون المدني" in first


async def test_bh_amending_law_uses_own_text_and_points_to_consolidated():
    t = await Bahrain().get_legislation_text("K3126")
    assert t.metadata.get("consolidated_text_of_amended_law") == "L2221"
    assert "not consolidated" in t.metadata["version"]
    assert "التنفيذ في المواد المدنية والتجارية" in t.text


async def test_bh_constitutional_court_round_trip():
    out = await server.search_caselaw("bh", "", limit=2, filters={"year_from": "2024"})
    ids = re.findall(r"\bCC\d{4}\b", out)
    assert ids, out
    dec = await server.get_decision("bh", "CC0124", max_chars=4000)
    assert "المحكمة الدستورية" in dec and "2024-01-31" in dec


async def test_bh_bad_id():
    with pytest.raises(BadRequest):
        await Bahrain().get_legislation_text("civil code")
