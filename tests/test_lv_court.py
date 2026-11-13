import asyncio

import pytest

from world_legal_mcp import _http
from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions import lv


def _run(filters, query="līgums"):
    seen = {}

    async def fake(body):
        seen.update(body)
        return {"items": [], "totalResults": 0}

    orig = lv._search
    lv._search = fake
    try:
        r = asyncio.run(lv.Latvia().search_caselaw(query, limit=5, page=1, filters=filters))
    finally:
        lv._search = orig
    return seen, r


def test_court_by_name_and_supreme():
    seen, r = _run({"court": "Rīgas apgabaltiesa"})
    assert seen["institutionSourceRegistryId"] == lv._COURTS["Rīgas apgabaltiesa"]
    assert "not by relevance" in r.note
    seen, _ = _run({"court": "supreme"})
    assert seen["institutionSourceRegistryId"] == lv._COURTS["Augstākā tiesa"]
    seen, _ = _run({"court": "Augstākā tiesa"})
    assert seen["institutionSourceRegistryId"] == lv._COURTS["Augstākā tiesa"]


def test_unknown_court_lists_names():
    with pytest.raises(BadRequest) as e:
        _run({"court": "apgabaltiesa"})
    assert "Rīgas apgabaltiesa" in str(e.value)


def test_constitutional_court_query_says_not_available():
    _, r = _run({"match": "phrase"}, query="Satversmes tiesa")
    assert "Satversmes tiesa" in r.note and "NOT available" in r.note
    _, r = _run({}, query="īres līgums")
    assert "NOT available" not in r.note


def test_legislation_gap_points_to_likumi_lv():
    assert "https://likumi.lv" in lv.Latvia.notes
