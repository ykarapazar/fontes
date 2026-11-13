"""Live smoke tests against DoJ Hong Kong e-Legislation open data (DATA.GOV.HK). Needs network."""
from world_legal_mcp import server


async def test_hk_search_by_cap_number_and_chinese_title():
    out = await server.search_legislation("hk", "Cap. 622", limit=2)
    assert 'get_legislation_toc("hk", "cap622")' in out and "Companies Ordinance" in out
    zh = await server.search_legislation("hk", "基本法", limit=3)
    assert '"A101!zh-Hant"' in zh and "中華人民共和國香港特別行政區基本法" in zh


async def test_hk_section_label_variants():
    for prov in ("s2", "s.2", "section 2", "2"):
        out = await server.get_legislation_provision("hk", "cap622", prov)
        assert "2. Interpretation" in out and "accounting transaction" in out, prov
    sch = await server.get_legislation_provision("hk", "Cap. 622", "sch2/s1")
    assert "Particulars and statements relating to company" in sch


async def test_hk_basic_law_articles_en_and_zh():
    en = await server.get_legislation_provision("hk", "A101", "Article 24")
    assert "permanent residents" in en
    zh = await server.get_legislation_provision("hk", "A101!zh-Hant", "第二十四條")
    assert "永久性居民" in zh


async def test_hk_toc_has_schedule_paths():
    out = await server.get_legislation_toc("hk", "cap622", keyword="Schedule 2")
    assert 'provision "sch2"' in out or '"sch2"' in out
