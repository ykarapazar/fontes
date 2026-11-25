"""Live smoke tests against matsne.gov.ge (10 s Crawl-delay, so slow) and ecd.court.ge."""
import re

from world_legal_mcp import server


async def test_ge_search_caselaw_filters():
    out = await server.search_caselaw("ge", "იჯარის ხელშეკრულება", limit=3,
                                      filters={"court": "supreme", "category": "civil",
                                               "date_from": "2019-01-01"})
    assert 'get_decision("ge", "3-' in out
    bad = await server.search_caselaw("ge", "იჯარა", filters={"court": "district"})
    assert bad.startswith("Bad request (ge)")


async def test_ge_constitutional_court():
    out = await server.search_caselaw("ge", "", limit=2, filters={"court": "constitutional"})
    ids = re.findall(r'get_decision\("ge", "(\d+)"\)', out)
    assert ids, out
    dec = await server.get_decision("ge", ids[0], max_chars=3000)
    assert "საკონსტიტუციო სასამართლო" in dec


async def test_ge_english_translation():
    out = await server.search_legislation("ge", "Civil Code", limit=3,
                                          filters={"language": "en"})
    assert 'get_legislation_toc("ge", "31702/en")' in out
    for law, label in (("31702/en", "Article 18¹"), ("31702/en", "18^1")):
        prov = await server.get_legislation_provision("ge", law, label)
        assert prov.startswith("# Civil Code of Georgia: Article 18¹"), (law, label)
        assert "personal data" in prov


async def test_ge_georgian_provision_labels():
    for label in ("მუხლი 18¹", "18-1"):
        out = await server.get_legislation_provision("ge", "31702", label)
        assert out.startswith("# საქართველოს სამოქალაქო კოდექსი: მუხლი 18¹"), label
        assert "პერსონალური მონაცემ" in out
