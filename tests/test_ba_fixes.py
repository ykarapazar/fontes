import asyncio

import pytest

from world_legal_mcp.base import SourceError
from world_legal_mcp.jurisdictions import ba


@pytest.mark.parametrize("s,want", [("II/3", "Član II"), ("II(3)(e)", "Član II"), ("Član II", "Član II"),
                                    ("VI", "Član VI"), ("Aneks 4", "Aneks IV"), ("Amandman I", "Amandman I")])
def test_norm_const_subparagraph(s, want):
    assert ba._norm_const(s) == want


def test_500_message(monkeypatch):
    async def boom(url, params):
        raise SourceError("x", 500)
    monkeypatch.setattr(ba, "_us_json", boom)
    ba._lists.clear()
    a = next(c for c in vars(ba).values() if isinstance(c, type) and hasattr(c, "search_caselaw") and c.__module__ == ba.__name__)()
    with pytest.raises(SourceError, match="ordinary court"):
        asyncio.run(a.search_caselaw("Vrhovni sud"))


@pytest.mark.parametrize("q,want", [("pravo na pravično suđenje", "pravo AND na AND pravično AND suđenje"),
                                    ("diskriminacija", "diskriminacija"),
                                    ("a AND b", "a AND b"),
                                    ('"x y" z', '"x y" AND z')])
def test_and_words(q, want):
    assert ba._and_words(q) == want


def test_multiword_query_sent_with_and(monkeypatch):
    seen = []

    async def fake(url, params):
        seen.append(dict(params))
        return {"items": []}
    monkeypatch.setattr(ba, "_us_json", fake)
    ba._lists.clear()
    a = next(c for c in vars(ba).values() if isinstance(c, type) and hasattr(c, "search_caselaw") and c.__module__ == ba.__name__)()
    asyncio.run(a.search_caselaw("Vrhovni sud"))
    assert seen[0]["tp"] == "Vrhovni AND sud"


def test_constitution_title_accepted_as_id(monkeypatch):
    ba._laws.clear()
    ba._laws[ba.CONST_ID] = (ba.CONST_ID, ba.CONST_TITLE, ["Član II"])
    a = next(c for c in vars(ba).values() if isinstance(c, type) and hasattr(c, "search_caselaw") and c.__module__ == ba.__name__)()
    for g in ("Ustav Bosne i Hercegovine", "Ustav BiH", ba.CONST_TITLE):
        assert asyncio.run(a._law(g))[0] == ba.CONST_ID
