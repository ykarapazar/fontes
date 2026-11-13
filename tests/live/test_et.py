"""Live smoke tests for Ethiopia: House of Peoples' Representatives published-laws library
(hopr.gov.et, Federal Negarit Gazeta PDFs). Needs network. Throttled to one request per second."""
from urllib.parse import quote

from world_legal_mcp import server
from world_legal_mcp.jurisdictions.et import Ethiopia, eth_num

LAW = Ethiopia.samples["law_id"]


def test_et_ethiopic_numerals():
    assert [eth_num(x) for x in ("፩", "፲፪", "፷፪", "፩፻፹፫")] == [1, 12, 62, 183]


async def test_et_search_by_number_and_type_filter():
    out = await server.search_legislation("et", "1183", filters={"type": "proclamation"})
    assert "1183/2012" in out and "hopr.gov.et" in out, out
    assert "Bad request" in await server.search_legislation("et", "x", filters={"type": "law"})


async def test_et_provision_label_variants_bilingual():
    a = await server.get_legislation_provision("et", LAW, "Article 2")
    b = await server.get_legislation_provision("et", LAW, "፪")
    assert "Administrative Agency" in a and "የአስተዳደር ተቋም" in a, a[:1500]
    assert "Administrative Agency" in b, b[:800]


async def test_et_viewfiles_link_as_id():
    url = "https://www.hopr.gov.et/Home/ViewFiles?path=" + quote("/admin/Files/" + LAW, safe="")
    out = await server.get_legislation_toc("et", url)
    assert "Article 62" in out and "SECTION FIVE" in out, out[:1500]
