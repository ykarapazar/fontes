"""Live smoke tests against Legislation Malta (legislation.mt). Needs network.
Throttled to one request per second; uses the small Employment and Industrial Relations Act
(Cap. 452) so the PDF parse stays quick."""
from world_legal_mcp import server


async def test_mt_search_title_chapter_language_and_bad_filter():
    out = await server.search_legislation("mt", "employment and industrial relations", limit=5)
    assert 'get_legislation_toc("mt", "cap/452")' in out
    out = await server.search_legislation("mt", "452", limit=3)
    assert "Employment and Industrial Relations Act" in out and "Cap. 452" in out
    out = await server.search_legislation("mt", "Impiegi", limit=20, filters={"language": "mt"})
    assert '"cap/452/mlt"' in out and "Kap. 452" in out
    bad = await server.search_legislation("mt", "civil code", filters={"language": "fr"})
    assert "Bad request" in bad


async def test_mt_id_variants_and_bad_id():
    a = await server.get_legislation_toc("mt", "cap/452", keyword="probation")
    b = await server.get_legislation_toc("mt", "Cap. 452", keyword="probation")
    c = await server.get_legislation_toc("mt", "https://legislation.mt/eli/cap/452/eng/pdf",
                                         keyword="probation")
    assert a == b == c
    bad = await server.get_legislation_toc("mt", "civil code")
    assert "Bad request" in bad
    missing = await server.get_legislation_text("mt", "cap/999999")
    assert "Not found" in missing


async def test_mt_provision_labels_marginal_heading_and_maltese():
    a = await server.get_legislation_provision("mt", "cap/452", "36")
    b = await server.get_legislation_provision("mt", "cap/452", "art. 36")
    c = await server.get_legislation_provision("mt", "cap/452", "Article 36")
    assert a == b == c
    assert "### 36." in a and "probationary period" in a
    mt = await server.get_legislation_provision("mt", "cap/452/mlt", "1")
    assert "Titolu fil-qosor" in mt and "Att dwar l-Impiegi" in mt
    none = await server.get_legislation_provision("mt", "cap/452", "999")
    assert "Not found" in none
