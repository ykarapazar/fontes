"""Live smoke tests against bdlaws.minlaw.gov.bd and supremecourt.gov.bd. Needs network."""
import re

from world_legal_mcp import server


async def test_bd_legislation_search_modes():
    out = await server.search_legislation("bd", "1872", limit=10, filters={"search_in": "year"})
    assert "The Contract Act, 1872" in out and '"26"' in out, out
    out = await server.search_legislation("bd", "undue influence", limit=5, filters={"search_in": "text"})
    assert "The Contract Act, 1872" in out, out
    assert "search_in must be" in await server.search_legislation("bd", "x", filters={"search_in": "body"})


async def test_bd_provision_label_variants_and_footnotes():
    for label in ("19A", "s. 19A", "section 19a"):
        out = await server.get_legislation_provision("bd", "act-26.html", label)
        assert "19A." in out and "undue influence" in out.lower(), out
    assert "Indian Contract (Amendment) Act, 1899" in out          # footnote kept
    rep = await server.get_legislation_provision("bd", "26", "80")  # inside '76-123. [Repealed]'
    assert "Sale of Goods Act, 1930" in rep


async def test_bd_bengali_act():
    toc = await server.get_legislation_toc("bd", "952")
    assert "বাংলাদেশ শ্রম আইন, ২০০৬" in toc and "৩ক" in toc
    out = await server.get_legislation_provision("bd", "952", "3ক")   # ASCII digit accepted
    assert "ঠিকাদার সংস্থা রেজিস্ট্রেশন" in out


async def test_bd_caselaw_division_filter_and_ids():
    out = await server.search_caselaw("bd", "bail", limit=5, filters={"division": "high_court"})
    courts = set(re.findall(r"- Court: (.+)", out))
    assert courts == {"Supreme Court of Bangladesh, High Court Division"}, out
    ids = re.findall(r'get_decision\("bd", "([^"]+\.pdf)"\)', out)
    assert ids, out
    dec = await server.get_decision(
        "bd", "https://supremecourt.gov.bd/resources/documents/3618580_Death_Reference_1-No.32of2019.pdf",
        max_chars=3000)
    assert "Death Reference No. 32 of 2019" in dec and "2026-06-30" in dec, dec
    assert "PDF file name" in await server.get_decision("bd", "../etc/passwd")
    assert "needs a query" in await server.search_caselaw("bd", "")
