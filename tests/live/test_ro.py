"""Live smoke tests against scj.ro (ÎCCJ decisions) and cdep.ro (legislation index). Needs network."""
from world_legal_mcp import server

URL = ("https://www.scj.ro/1093/Detalii-jurisprudenta?customQuery%5B0%5D.Key=id"
       "&customQuery%5B0%5D.Value=200000")


async def test_ro_decision_by_id_and_url():
    for did in ("200000", URL):
        out = await server.get_decision("ro", did, max_chars=3000)
        assert "Decizia nr. 3493/2021" in out and "Contencios Administrativ" in out
        assert "2021-06-09" in out


async def test_ro_unknown_decision_and_bad_id():
    assert "Not found" in await server.get_decision("ro", "999999999")
    assert "Bad request" in await server.get_decision("ro", "ECLI:RO:x")


async def test_ro_civil_code_by_number_year_type():
    out = await server.search_legislation("ro", "", limit=5, filters={
        "number": "287", "year": "2009", "type": "lege"})
    assert "LEGE privind Codul civil" in out and "ida=90254" in out
    assert "in force" in out and "DECRET" not in out


async def test_ro_bad_type_filter():
    out = await server.search_legislation("ro", "codul civil", filters={"type": "statute"})
    assert "Bad request" in out


async def test_ro_constitution_text_and_label_variants():
    out = await server.search_legislation("ro", "constitutia", limit=10, filters={"type": "constitutie"})
    assert "ida=15346" in out and "CONSTITUŢIA ROMÂNIEI din 1991" in out
    for p in ("Articolul 21", "21", "art. 21"):
        prov = await server.get_legislation_provision("ro", "15346", p)
        assert "Accesul liber la justiţie" in prov and "termen rezonabil" in prov
    assert "Not found" in await server.get_legislation_provision("ro", "15346", "999")
    assert "Not found" in await server.get_legislation_provision("ro", "90254", "1")
