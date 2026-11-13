"""Live smoke tests against the Constitutional Court of Montenegro archive (ustavnisud.me). Needs network."""
import re

from world_legal_mcp import server


async def test_me_case_number_query_and_filter():
    out = await server.search_caselaw("me", "", limit=5, filters={"case_number": "U-III br. 339/24"})
    assert "U-III br.339/24" in out and 'get_decision("me", "43750")' in out, out
    out = await server.search_caselaw("me", "", limit=5, filters={"case_number": "x"})
    assert "number/year" in out


async def test_me_type_and_year_filters():
    out = await server.search_caselaw("me", "", limit=5, filters={"type": "U-III", "year": "2024"})
    nums = re.findall(r"U-III br\. ?\d+/24", out)
    assert nums, out
    assert "must be one of" in await server.search_caselaw("me", "", filters={"type": "U-XX"})


async def test_me_decision_by_case_number_doc_file():
    # U-III br. 2/20 is published as a Word 97 .doc: the built-in reader must give the text.
    out = await server.get_decision("me", "U-III br. 2/20", max_chars=4000)
    assert "38077" in out and "ODBACUJE SE ustavna žalba" in out, out
    assert "2020-06-18" in out


async def test_me_bad_ids():
    assert "no document with id" in await server.get_decision("me", "99999999")
    assert "numeric document id" in await server.get_decision("me", "Kadić")
