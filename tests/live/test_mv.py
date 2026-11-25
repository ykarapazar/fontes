"""Live checks for the Maldives adapter (MvLaw, Dhivehi legislation)."""
from world_legal_mcp import server


async def test_mv_provision_labels_ids_and_errors():
    a = await server.get_legislation_provision("mv", "139", "2")
    b = await server.get_legislation_provision("mv", " 139 ", "Article 2")
    c = await server.get_legislation_provision("mv", "139", "2 ވަނަ މާއްދާ")
    assert a == b == c and "މަޤްޞަދު" in a and "(ހ)" in a
    assert (await server.get_legislation_toc("mv", "whistleblower act")).startswith("Bad request (mv)")
    assert "not found" in (await server.get_legislation_text("mv", "999999")).lower()
    assert "not found" in (await server.get_legislation_provision("mv", "139", "999")).lower()


async def test_mv_constitution_article_without_dot():
    # Article 303 of the 2008 Constitution is numbered "303" (no dot) at the source.
    out = await server.get_legislation_provision("mv", "6", "303")
    assert "303." in out and "ޕްރޮޖެކްޓް" in out


async def test_mv_filters_and_search():
    out = await server.search_legislation("mv", "", limit=5, filters={"category": "constitution"})
    assert "1932" in out
    hits = await server.search_legislation("mv", "32/2021", limit=3)
    assert "163" in hits and "32/2021" in hits
    bad = await server.search_legislation("mv", "", filters={"category": "treaty"})
    assert bad.startswith("Bad request (mv)")


async def test_mv_gazette_laws_mvlaw_lacks():
    # Act 17/2026 is in the Government Gazette but not (yet) in MvLaw.
    hits = await server.search_legislation("mv", "17/2026", limit=3, filters={"source": "gazette"})
    assert '"gazette/7561"' in hits and "17/2026" in hits
    page = await server.get_legislation_provision("mv", "https://gazette.gov.mv/gazette/7561", "3")
    assert "Page 3" in page and "7809.pdf" in page
    assert "page 1" in (await server.get_legislation_provision("mv", "gazette/7561", "page 99"))
    bad = await server.search_legislation("mv", "", filters={"source": "gazette", "year": "2020"})
    assert bad.startswith("Bad request (mv)")
