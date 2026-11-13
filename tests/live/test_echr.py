"""Live smoke tests against HUDOC (hudoc.echr.coe.int). Needs network; 1 s per request."""
import re

from world_legal_mcp import server


async def test_echr_filters_respondent_article_gc_date():
    out = await server.search_caselaw("echr", "surveillance", limit=3, filters={
        "collection": "grandchamber", "respondent": "GBR", "article": "8",
        "date_from": "2021-01-01", "date_to": "2021-12-31", "sort": "date"})
    assert "BIG BROTHER WATCH" in out, out
    assert "Grand Chamber" in out
    dates = re.findall(r"- Date: (\d{4})", out)
    assert dates and set(dates) == {"2021"}


async def test_echr_ecli_and_appno_resolve_to_english_judgment():
    for ident in ("ECLI:CE:ECHR:2021:0525JUD005817013", "58170/13"):
        out = await server.get_decision("echr", ident, max_chars=3000)
        assert "001-210077" in out and "BIG BROTHER WATCH" in out, out[:500]
        assert "Resolved from" in out


async def test_echr_appno_search_and_language_filter():
    out = await server.search_caselaw("echr", "47143/06", limit=5, filters={"language": "FRE"})
    assert "ZAKHAROV" in out and "001-159324" not in out   # 001-159324 is the English text
    bad = await server.get_decision("echr", "not an id")
    assert "itemid" in bad
