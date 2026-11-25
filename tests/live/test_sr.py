"""Live smoke tests for Suriname (rechtspraak.sr decisions, dna.sr laws).
Needs network; 1 s per request per host."""

from world_legal_mcp import server

GRONDWET = "geldende-teksten-t-m-2005/grondwet-van-de-republiek-suriname"


async def test_sr_decision_ids_and_filters():
    # SRU number in any case, or the page URL
    for ident in ("SRU-HvJ-1991-6", "sru-hvj-1991-6", "https://rechtspraak.sr/sru-hvj-1991-6/"):
        d = await server.get_decision("sr", ident, max_chars=3000)
        assert "GR-13074" in d and "1991-08-23" in d and "Hof van Justitie" in d, d[:800]
    assert (await server.get_decision("sr", "SRU-HvJ-1991-99999")).startswith("Not found (sr)")
    assert (await server.get_decision("sr", "12345")).startswith("Bad request (sr)")
    # court filter: every hit comes from that court; later pages come from the load-more endpoint
    out = await server.search_caselaw("sr", "huur", limit=10, page=2,
                                      filters={"court": "Kantongerecht Eerste Kanton", "sort": "newest"})
    assert out.count("- Court: Kantongerecht Eerste Kanton") >= 5 and "Hof van Justitie" not in out, out[:1200]
    assert (await server.search_caselaw("sr", "huur", filters={"court": "Supreme"})).startswith("Bad request (sr)")


async def test_sr_legislation_articles():
    hits = await server.search_legislation("sr", "grondwet")
    assert GRONDWET in hits, hits[:800]
    toc = await server.get_legislation_toc("sr", GRONDWET)
    assert "HOOFDSTUK V – GRONDRECHTEN" in toc and 'provision "186"' in toc, toc[:1200]
    # "Artikel 10" in the PDF is glued to footnote numbers elsewhere; label forms all work
    for p in ("Artikel 10", "art. 10", "10"):
        out = await server.get_legislation_provision("sr", GRONDWET, p)
        assert "eerlijke en openbare" in out, out[:800]
    assert (await server.get_legislation_provision("sr", GRONDWET, "999")).startswith("Not found (sr)")
    assert (await server.get_legislation_toc("sr", "wetten-na-2005/no-such-law-xyz")).startswith("Not found (sr)")
