"""Live smoke tests against jurisprudenta.csj.md (CSJ) and instante.justice.md (10 s Crawl-delay, so slow)."""
import re

from world_legal_mcp import server


async def test_md_csj_filters():
    out = await server.search_caselaw("md", "furt", limit=3,
                                      filters={"college": "penal", "date_from": "2014-01-01",
                                               "date_to": "2014-12-31"})
    assert 'get_decision("md", "penal/' in out, out
    years = re.findall(r"- Date: (\d{4})", out)
    assert years and all(y == "2014" for y in years)
    bad = await server.search_caselaw("md", "furt", filters={"college": "comercial"})
    assert bad.startswith("Bad request (md)")
    bad = await server.search_caselaw("md", "furt", filters={"instance": "Judecătoria Bălți"})
    assert bad.startswith("Bad request (md)")  # instance is for court='lower' only


async def test_md_csj_id_variants():
    for did in ("civil/82623", "https://jurisprudenta.csj.md/search_col_civil.php?id=82623"):
        out = await server.get_decision("md", did, max_chars=2000)
        assert out.startswith("# CSJ 2r-264/26"), (did, out[:200])
        assert "uzucapiune" in out


async def test_md_lower_courts():
    out = await server.search_caselaw("md", "furt", limit=2,
                                      filters={"court": "lower", "case_type": "penal",
                                               "instance": "curtea de apel centru"})
    ids = re.findall(r'get_decision\("md", "([0-9A-F-]{36})"\)', out)
    assert ids, out
    assert "Curtea de Apel Centru" in out
    dec = await server.get_decision("md", ids[0].lower(), max_chars=3000)
    assert "în numele Legii" in dec or "Dosarul nr." in dec


async def test_md_constitution_labels():
    for label in ("Articolul 59^1", "59¹", "591", "art. 59-1"):
        out = await server.get_legislation_provision("md", "constitutia", label)
        assert "Articolul 59^1" in out and "Avocatul Poporului" in out, (label, out[:300])
    out = await server.get_legislation_provision("md", "constitutia", "52")
    assert "Dreptul de petiţionare" in out  # PDF heading misspelt 'Artcolul 52'
    out = await server.search_legislation("md", "cod civil")
    assert "Only the Constitution" in out
