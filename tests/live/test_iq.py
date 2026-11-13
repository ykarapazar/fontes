"""Live smoke tests against the Kurdistan Parliament legislation database (legislation.krd).
Needs network. 1 s spacing per request."""
import pytest

from world_legal_mcp import server
from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions.iq import Iraq


async def test_iq_search_language_and_year_filters():
    out = await server.search_legislation("iq", "الاستثمار", limit=10, filters={"year": "2006", "language": "ar"})
    assert "3475" in out and "قانون الاستثمار" in out, out
    r = await Iraq().search_legislation("قانون العمل", limit=50, filters={"language": "ar"})
    assert r.items and all("یاسا" not in h.title for h in r.items)


async def test_iq_arabic_provision_label_variants():
    a = await server.get_legislation_provision("iq", "3475", "المادة الخامسة والعشرون")
    b = await Iraq().get_legislation_provision("https://legislation.krd/law-detail/?id=3475", "art. 25")
    assert "وقائع كوردستان" in a and b.provision == "25" and "الأسباب الموجبة" not in b.text


async def test_iq_kurdish_text_toc():
    toc = await Iraq().get_legislation_toc("2284")
    labels = [e.provision for e in toc.entries if e.provision]
    assert labels[:3] == ["1", "2", "3"] and "25" in labels


async def test_iq_bad_input():
    with pytest.raises(BadRequest):
        await Iraq().get_legislation_text("investment-law")
    with pytest.raises(BadRequest):
        await Iraq().search_legislation("", limit=5)
