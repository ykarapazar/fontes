"""Live smoke tests against rechtspraak.nl and wetten.overheid.nl. Needs network."""
import datetime
import re

from world_legal_mcp import server


async def test_nl_search_caselaw():
    out = await server.search_caselaw("nl", "huurrecht ontbinding", limit=3,
                                      filters={"sort": "uitspraak", "period": "vorig_jaar"})
    assert "Netherlands (nl) case law" in out and 'get_decision("nl", "ECLI:NL:' in out
    years = re.findall(r"- Date: (\d{4})", out)
    assert years and set(years) == {str(datetime.date.today().year - 1)}


async def test_nl_search_caselaw_page2_and_bad_filter():
    p1 = await server.search_caselaw("nl", "huurrecht ontbinding", limit=3)
    p2 = await server.search_caselaw("nl", "huurrecht ontbinding", limit=3, page=2)
    assert "### 4." in p2 and p1 != p2
    bad = await server.search_caselaw("nl", "huur", filters={"period": "eeuw"})
    assert bad.startswith("Bad request (nl)") and "eeuw" in bad


async def test_nl_get_decision():
    out = await server.get_decision("nl", "ecli:nl:rbams:2023:3197", max_chars=5000)
    assert out.startswith("# Rechtbank Amsterdam")
    assert "- Identifier: ECLI:NL:RBAMS:2023:3197" in out and "## Text" in out
    assert "- Source: https://" in out



async def test_nl_get_legislation_provision_bw_labels():
    for label in ("6:2", "2", "art. 6:2 BW"):
        out = await server.get_legislation_provision("nl", "BWBR0005289", label)
        assert out.startswith("# Burgerlijk Wetboek Boek 6: 6:2"), label
        assert "**Artikel 6:2**" in out and "redelijkheid en billijkheid" in out


async def test_nl_get_legislation_toc_keyword():
    out = await server.get_legislation_toc("nl", "BWBR0001840", keyword="1")
    assert '- Artikel 1 → provision "1"' in out and "Filtered by '1'" in out
