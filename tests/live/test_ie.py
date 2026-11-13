"""Live smoke tests against the Irish Statute Book and LRC Revised Acts. Needs network."""
from world_legal_mcp import server


async def test_ie_search_legislation_si_filter():
    out = await server.search_legislation("ie", "freedom of information fees", limit=3,
                                          filters={"type": "si", "year": "2014"})
    assert "Ireland (ie)" in out and "2014/si/484" in out


async def test_ie_revised_provision_with_label_variant():
    out = await server.get_legislation_provision("irl", "Act 30 of 2014", "s. 2")
    assert "section/2" in out and "Revised Act (Law Reform Commission" in out
    assert "“Commissioner” means" in out


async def test_ie_enacted_fallback_says_so():
    out = await server.get_legislation_provision("ie", "2025/act/1", "1")
    assert "Text as enacted" in out and "/section/1/enacted/en/html" in out


async def test_ie_si_full_text():
    out = await server.get_legislation_text("ie", "S.I. No. 484 of 2014", max_chars=3000)
    assert "as made" in out and "€20.00 per hour" in out


async def test_ie_constitution_search_and_article_variants():
    out = await server.search_legislation("ie", "constitution", limit=3)
    assert "Constitution of Ireland" in out and "cons" in out
    a = await server.get_legislation_provision("ie", "cons", "Article 40.3")
    b = await server.get_legislation_provision("ie", "bunreacht", "40")
    assert a == b and "article/40" in a and "equal before the law" in a
    a44 = await server.get_legislation_provision("ie", "cons", "art. 44")   # broken heading on eISB
    assert "homage of public worship" in a44


async def test_ie_pre1922_act_by_section():
    out = await server.get_legislation_provision("ie", "1861/act/100", "s. 18")
    assert "Pre-1922 Act" in out and "grievous bodily" in out and "print.html#sec18" in out
