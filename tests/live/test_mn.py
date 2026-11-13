"""Live smoke tests against shuukh.mn (Mongolian court decisions database)."""
import re

from world_legal_mcp import server


async def test_mn_supreme_search_date_filter():
    out = await server.search_caselaw("mn", "түрээс", limit=3,
                                      filters={"date_from": "2024-01-01", "date_to": "2024-12-31"})
    assert re.search(r'get_decision\("mn", "1/3/\d+"\)', out), out
    years = re.findall(r"- Date: (\d{4})", out)
    assert years and all(y == "2024" for y in years), out
    bad = await server.search_caselaw("mn", "x", filters={"level": "district"})
    assert bad.startswith("Bad request (mn)")


async def test_mn_criminal_supreme_number_format():
    out = await server.search_caselaw("mn", "хулгай", limit=2, filters={"category": "criminal"})
    assert re.search(r'get_decision\("mn", "2/3/\d+"\)', out), out
    assert "ХШТ" in out


async def test_mn_decision_by_url_and_metadata():
    dec = await server.get_decision("mn", "https://shuukh.mn/single_case/11071?id=3&court_cat=1",
                                    max_chars=3000)
    assert "001/хт2026/00115" in dec
    assert "101/2024/07666/И" in dec
    bad = await server.get_decision("mn", "11071")
    assert bad.startswith("Bad request (mn)")


async def test_mn_nonexistent_id_stops_at_size_cap():
    # shuukh.mn answers a made-up id with a 16-95 MB page; the adapter must stop at 5 MB.
    out = await server.get_decision("mn", "1/3/999999998")
    assert out.startswith("Not found (mn)"), out[:300]
