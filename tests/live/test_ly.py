"""Live smoke tests for Libya: Ministry of Justice legislation (aladel.gov.ly) and Supreme Court
rulings and journal volumes (alolya.gov.ly). Needs network. Throttled to one request per second."""
from world_legal_mcp import server


async def test_ly_search_type_filter():
    out = await server.search_legislation("ly", "", limit=3, filters={"type": "treaty"})
    assert "اتفاقية" in out or "البروتوكول" in out or "الإعلان" in out, out[:800]
    assert "Bad request" in await server.search_legislation("ly", "x", filters={"type": "decree"})


async def test_ly_ordinal_articles_and_label_variants():
    # Family law 10/1984 numbers its articles in words ("المادة الحادية عشرة").
    a = await server.get_legislation_provision("ly", "1246", "المادة الحادية عشرة")
    b = await server.get_legislation_provision("ly", "1246", "art. 11")
    assert "الحادية عشرة" in a and a == b, a[:600]
    toc = await server.get_legislation_toc("ly", f"https://aladel.gov.ly/home/?p=1246")
    assert "الباب الأول" in toc and 'provision "75"' in toc, toc[:1500]


async def test_ly_pdf_post_text_layer():
    # Civil Code part 1 is only a linked PDF (presentation-form Arabic, folded with NFKC).
    out = await server.get_legislation_provision("ly", "3950", "مادة 1")
    assert "النصوص التشريعية" in out, out[:800]


async def test_ly_bad_id():
    assert "Bad request" in await server.get_legislation_text("ly", "civil-code")


async def test_ly_supreme_court_chambers_and_id_variants():
    out = await server.search_caselaw("ly", "دستورية", limit=3, filters={"chamber": "constitutional"})
    assert "الطعن الدستوري" in out and "الطعن المدني" not in out, out[:800]
    assert "Bad request" in await server.search_caselaw("ly", "x", filters={"chamber": "family"})
    a = await server.get_decision("ly", "3b18df15-bc9c-499a-b7cb-a5f4f1f903ed")
    b = await server.get_decision("ly", "https://www.alolya.gov.ly/article/3b18df15-bc9c-499a-b7cb-a5f4f1f903ed?from=%2F")
    assert a == b and "673/70ق" in a and "## المنطوق" in a and "حكمت المحكمة" in a, a[:800]


async def test_ly_supreme_court_journal_volumes():
    out = await server.search_caselaw("ly", "", limit=5, filters={"journal_year": "60"})
    assert "books/a892df95-b081-4fd1-9d3b-d261717b48f5" in out, out[:800]
    assert "not online" in await server.search_caselaw("ly", "", limit=2, filters={"journal_year": "12"})
    vol = await server.get_decision("ly", "books/a892df95-b081-4fd1-9d3b-d261717b48f5")
    assert "طعن الأحوال الشخصية" in vol, vol[:800]
