"""Live smoke tests against the CDC laws list (cdc.gov.kh). Needs network.
Throttled to one request per second."""
from world_legal_mcp import server

CONST = "2022/04/THE-CONSTITUTION.pdf"


async def test_kh_category_filter_and_bad_category():
    out = await server.search_legislation("kh", "law", limit=50, filters={"category": "land"})
    assert "2022/05/LAND-LAW_010430-.pdf" in out and "2001-04-30" in out, out
    assert "Law on Commercial Arbitration" not in out
    bad = await server.search_legislation("kh", "law", filters={"category": "astrology"})
    assert "Bad request" in bad and "astrology" in bad


async def test_kh_provision_label_and_id_variants():
    for law in (CONST, "https://cdc.gov.kh/wp-content/uploads/" + CONST):
        for prov in ("Article 31", "31", "art. 31"):
            p = await server.get_legislation_provision("kh", law, prov)
            assert "Every Khmer citizens shall be equal before the law" in p, (law, prov)
    toc = await server.get_legislation_toc("kh", CONST, keyword="KING")
    assert "CHAPTER II : THE KING" in toc
    assert "Bad request" in await server.get_legislation_provision("kh", CONST, "Preamble")


async def test_kh_khmer_legacy_font_and_bad_ids():
    hits = await server.search_legislation("kh", "Land Law (2001)", filters={"category": "Land"})
    assert "Khmer original" in hits
    err = await server.get_legislation_text("kh", "2022/05/ច្បាប់ភូមិបាល២០០១.pdf")
    assert "no usable text layer" in err
    assert "Bad request" in await server.get_legislation_text("kh", "../../wp-config.php")
