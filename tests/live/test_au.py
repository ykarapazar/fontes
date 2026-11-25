"""Live smoke tests against the Federal Register of Legislation API. Needs network."""
from world_legal_mcp import server


async def test_au_search_legislation_collection_filter():
    out = await server.search_legislation("au", "Corporations Act 2001", limit=3,
                                          filters={"collection": "Act"})
    assert "C2004A00818" in out and "Corporations Act 2001" in out


async def test_au_provision_label_variants():
    for p in ("18", "section 18", "s.18"):
        out = await server.get_legislation_provision("au", "C2004A00109", p)
        assert ": s 18" in out


async def test_au_schedule_section_is_australian_consumer_law():
    out = await server.get_legislation_provision("au", "C2004A00109", "Sch 2 s 18")
    assert "Misleading or deceptive conduct" in out and "in trade or commerce" in out


async def test_au_toc_has_schedule_labels():
    out = await server.get_legislation_toc("au", "C2004A00109", keyword="Australian Consumer Law")
    assert 'provision "Sch 2"' in out
