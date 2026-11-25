"""Live smoke tests against the Lao Official Gazette (laoofficialgazette.gov.la). Needs network.
Throttled to one request per second; the host is slow."""
from world_legal_mcp import server


async def test_la_search_paging_across_source_pages():
    p1 = await server.search_legislation("la", "ກົດໝາຍວ່າດ້ວຍ", limit=15, page=1)
    p2 = await server.search_legislation("la", "ກົດໝາຍວ່າດ້ວຍ", limit=15, page=2)
    assert "laoofficialgazette.gov.la/index.php?r=site/display&id=" in p1
    ids1 = set(__import__("re").findall(r"id=(\d+)", p1))
    ids2 = set(__import__("re").findall(r"id=(\d+)", p2))
    assert len(ids1) >= 15 and ids2 and not (ids1 & ids2) - {"12"}, (ids1, ids2)


async def test_la_sara_am_spelling_variant():
    # Titles spell "ດຳລັດ" (decree) both ways; a no-hit spelling is retried in the other form.
    # Query in the decomposed form; the Gazette title uses the precomposed one.
    a = await server.search_legislation("la", "ດໍາລັດວ່າດ້ວຍ ການຂົນສົ່ງສິນຄ້າອັນຕະລາຍ", limit=5)
    assert "ຂົນສົ່ງສິນຄ້າອັນຕະລາຍ" in a and "scan" in a.lower(), a


async def test_la_text_not_supported_and_empty_query():
    assert "Bad request" in await server.search_legislation("la", "   ")
    out = await server.get_legislation_text("la", "2468")
    assert "not supported" in out, out
