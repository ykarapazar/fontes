"""Live smoke tests against mejlis.gov.tm (laws, codes) and court.gov.tm (Constitution, Plenum)."""
import re

from world_legal_mcp import server


async def test_tm_restarted_numbering_and_article_heading():
    # The Constitution PDF starts with the 2016 enacting law (articles 1-3): those get "1:N".
    toc = await server.get_legislation_toc("tm", "constitution")
    assert "1:3" in toc, toc[:800]
    art = await server.get_legislation_provision("tm", "law-384", "2-nji madda")
    assert "2-nji madda" in art, art[:500]


async def test_tm_constitution_pdf_and_article_6_1():
    hits = await server.search_legislation("tm", "Konstitusiýa", filters={"type": "constitution"})
    assert 'constitution' in hits, hits
    art = await server.get_legislation_provision("tm", "constitution", "6¹")
    assert "Halk Maslahaty" in art, art[:500]
    ru = await server.get_legislation_provision("tm", "constitution-ru", "1")
    assert "Туркменистан" in ru, ru[:500]


async def test_tm_russian_law_list_and_text():
    out = await server.search_legislation("tm", "ахалтекинских", filters={"lang": "ru"})
    ids = re.findall(r'"(law-\d+-ru)"', out)
    assert ids, out
    text = await server.get_legislation_text("tm", ids[0], max_chars=3000)
    assert "Статья 1" in text, text[:500]


async def test_tm_plenum_year_filter_and_date_number_id():
    out = await server.search_caselaw("tm", "", limit=5, filters={"year": "2025"})
    years = re.findall(r"- Date: (\d{4})", out)
    assert years and all(y == "2025" for y in years), out
    dec = await server.get_decision("tm", "28.04.1997 № 5", max_chars=3000)
    assert "Parahorçulyk" in dec and "K A R A R Y № 5" in dec, dec[:500]
