"""Live smoke tests against qbz.gov.al and gjykataelarte.gov.al. Needs network."""
import re

from world_legal_mcp import server


async def test_al_search_caselaw_filters():
    out = await server.search_caselaw("al", "pronesi", limit=3,
                                      filters={"category": "civil", "date_from": "2026-01-01"})
    assert "Albania (al) case law" in out and "Kolegji Civil" in out
    dates = re.findall(r"- Date: (\d{4})-\d\d-\d\d", out)
    assert dates and all(int(y) >= 2026 for y in dates)
    bad = await server.search_caselaw("al", "pronesi", filters={"category": "xx"})
    assert bad.startswith("Bad request (al)")


async def test_al_get_decision():
    out = await server.get_decision("al", "31001-02718-00-2014", max_chars=5000)
    assert out.startswith("# KOMISIONI I VERIFIKIMIT")
    assert "- Date: 2017-01-24" in out and "Kolegji Administrativ" in out
    assert "GJYKATA E LARTË" in out.upper()


async def test_al_provision_label_and_eli_variants():
    out = await server.get_legislation_provision("al", "/eli/ligj/2015/04/30/44", "neni 5")
    assert "Neni 5" in out and "Parimi i transparencës" in out
    out = await server.get_legislation_provision("al", "12004", "5")
    assert "Parimi i transparencës" in out


async def test_al_joint_colleges_and_archive():
    # Joint Colleges unifying decisions, listed by the court itself (1999 on)
    out = await server.search_caselaw("al", "penal", limit=5, filters={"category": "joint", "date_to": "2000"})
    assert "Kolegjet e Bashkuara" in out and "Vendim Unifikues Penal" in out, out[:800]
    d = await server.get_decision("al", "media/vendim_nr_2_15861_8d60692917.doc", max_chars=3000)
    assert "KOLEGJET E BASHKUARA" in d and "2022-11-18" in d, d[:800]
    # pre-2005 decisions: monthly volumes
    vols = await server.search_caselaw("al", "shkurt", filters={"archive_year": "1999"})
    assert "media/shkurt_1999_340_815c79f3e9.doc" in vols, vols[:800]
    assert (await server.get_decision("al", "media/not_listed.doc")).startswith("Not found (al)")
