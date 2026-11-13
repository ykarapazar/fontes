"""Live smoke tests against the Supreme Court of Nigeria API (supreme-cms.supremecourt.gov.ng). Needs network."""
import re

from world_legal_mcp import server


async def test_ng_suit_number_query_and_filter():
    out = await server.search_caselaw("ng", "SC309/74", limit=3)
    assert 'get_decision("ng", "122")' in out and "SC309/74" in out, out
    out = await server.search_caselaw("ng", "", limit=5, filters={"suit_no": "91/2002"})
    assert "SC 91/2002" in out or "SC91/2002" in out, out


async def test_ng_date_filters():
    out = await server.search_caselaw("ng", "", limit=10,
                                      filters={"date_from": "1976-01-01", "date_to": "1976-12-31"})
    dates = re.findall(r"- Date: (\d{4})", out)
    assert dates and set(dates) == {"1976"}, out
    bad = await server.search_caselaw("ng", "x", filters={"date_from": "1976"})
    assert "YYYY-MM-DD" in bad


async def test_ng_decision_by_url_and_bad_ids():
    out = await server.get_decision("ng", "https://supremecourt.gov.ng/judgment-delivered/122", max_chars=3000)
    assert "- Identifier: 122" in out and "Idundun" in out and "Okumagba" in out
    assert "no judgment with that id" in await server.get_decision("ng", "999999")
    assert "numeric case id" in await server.get_decision("ng", "Idundun v Okumagba")


async def test_ng_constitution_consolidated_section():
    from world_legal_mcp.jurisdictions.ng import Nigeria
    j = Nigeria()
    hits = (await j.search_legislation("constitution", limit=5)).items
    assert hits[0].id == "faolex:nig164561"
    p = await j.get_legislation_provision("constitution", "section 16A")   # added by the 2023 alteration
    assert p.text.startswith("16A.") and "food security" in p.text.lower()


async def test_ng_nass_act_and_filters():
    from world_legal_mcp.base import BadRequest
    from world_legal_mcp.jurisdictions.ng import Nigeria
    j = Nigeria()
    r = await j.search_legislation("evidence", filters={"source": "nass"})
    assert any(h.id == "nass:5945" for h in r.items), r.items
    p = await j.get_legislation_provision("nass:5945", "1")
    assert "Evidence may be given" in p.text
    try:
        await j.search_legislation("x", filters={"source": "lfn"})
        raise AssertionError("bad source accepted")
    except BadRequest:
        pass


async def test_ng_plac_lfn_2004_act():
    from world_legal_mcp.jurisdictions.ng import Nigeria
    j = Nigeria()
    p = await j.get_legislation_provision("plac:18", "1")
    assert "false pretence" in p.text.lower(), p.text[:200]
    toc = await j.get_legislation_toc("plac:18")
    assert len(toc.entries) >= 15
    r = await j.search_legislation("advance fee fraud", filters={"source": "plac"})   # reads the 69-page index
    assert any(h.id == "plac:18" for h in r.items), r.items
