"""Liechtenstein (gesetze.li) adapter checks that the shared conformance suite does not cover."""
from world_legal_mcp import server


async def test_li_id_variants():
    a = await server.get_legislation_provision("li", "1921.015", "Art. 1")
    b = await server.get_legislation_provision("li", "LGBl. 1921 Nr. 15", "1")
    c = await server.get_legislation_provision("li", "https://www.gesetze.li/konso/1921015000", "art. 1")
    assert a == b == c and "Staatsverband" in a and "LGBl. 2003 Nr. 186" in a


async def test_li_abgb_paragraph_and_article_are_distinct():
    par = await server.get_legislation_provision("li", "1003.001", "§ 1")
    art = await server.get_legislation_provision("li", "1003.001", "Art. 1")
    assert "bürgerliche Recht" in par and "Mietvertrag" in art


async def test_li_search_abbreviation_and_title_first():
    out = await server.search_legislation("li", "PGR", filters={"in": "abbreviation"})
    assert "1926.004" in out
    out = await server.search_legislation("li", "Personen- und Gesellschaftsrecht", limit=2)
    assert "1926.004" in out.split("### 2.")[0]


async def test_li_bad_filter():
    out = await server.search_legislation("li", "Stiftung", filters={"status": "maybe"})
    assert out.startswith("Bad request") and "repealed" in out


async def test_li_ogh_search_year_and_tags():
    out = await server.search_caselaw("li", "Stiftung", filters={"year": "2023"})
    assert "Oberster Gerichtshof" in out and "2023-" in out and "2024-" not in out


async def test_li_ogh_decision_id_and_url_agree():
    a = await server.get_decision("li", "sv-2024-34-ogh-2025-68")
    b = await server.get_decision("li", "https://www.ogh.li/files/attachments/sv-2024-34-ogh-2025-68.pdf")
    assert a == b and "SV.2024.34" in a and "2025-11-07" in a and "Im Namen von Fürst und Volk" in a
