"""Live smoke tests against Domstolsverket Rättspraxis and Riksdagen open data. Needs network."""
import re

from world_legal_mcp import server


async def test_se_search_caselaw_filters():
    out = await server.search_caselaw("se", "skadestånd", limit=3,
                                      filters={"court": "HDO", "form": "referat",
                                               "date_from": "2020-01-01", "date_to": "2021-12-31"})
    assert "Sweden (se) case law" in out and "NJA 2021" in out
    years = re.findall(r"- Date: (\d{4})", out)
    assert years and all(2020 <= int(y) <= 2021 for y in years)
    bad = await server.search_caselaw("se", "skadestånd", filters={"court": "XX"})
    assert bad.startswith("Bad request (se)")


async def test_se_get_decision_and_group_id():
    out = await server.get_decision("se", "f876d0f7-4d67-4ea7-a097-2cef89daf082", max_chars=5000)
    assert out.startswith("# NJA 2021 s. 1197 (En amerikansk bulldogg)")
    assert "- Court: Högsta domstolen" in out
    # the group id from the public URL opens the same group's case report
    grp = await server.get_decision("se", "1b1714bb-45d7-4ffc-99ba-838aa54d6a97", max_chars=3000)
    assert grp.startswith("# HFD 2026 ref. 42")


async def test_se_search_legislation():
    out = await server.search_legislation("se", "brottsbalk", limit=3)
    assert 'get_legislation_toc("se", "1962:700")' in out


async def test_se_provision_labels():
    for law, label in (("1962:700", "3 kap. 1 §"), ("SFS 1962:700", "3:1"),
                       ("sfs-1962-700", "3 kap 1 §")):
        out = await server.get_legislation_provision("se", law, label)
        assert out.startswith("# Brottsbalk (1962:700): 3 kap. 1 §"), (law, label)
        assert "döms för mord" in out
    # chaptered law without a chapter -> clear bad request; law without chapters takes "5 §"
    bad = await server.get_legislation_provision("se", "1962:700", "1 §")
    assert bad.startswith("Bad request (se)")
    mbl = await server.get_legislation_provision("se", "1976:580", "§ 2")
    assert "2 §" in mbl and "ideell natur" in mbl
