"""Shared server/render behaviour reported by lawyers: headers, TOC keyword, flags, bad arguments."""
import asyncio

import pytest

from world_legal_mcp import render, server
from world_legal_mcp.base import Jurisdiction, Source
from world_legal_mcp.models import DecisionHit, LawHit, Results, Toc, TocEntry


class _J(Jurisdiction):
    code, name = "xx", "Xland"
    sources = (Source("S", "https://s.example", covers=("caselaw", "legislation")),)

    async def get_legislation_toc(self, id):
        ...


def _toc(*titles_provs):
    return Toc("i", "Code", "https://u", [TocEntry(t, 0, p) for t, p in titles_provs])


def test_keyword_word_start_not_substring():
    t = _toc(("Part I", ""), ("Article 1", "Article 1"), ("Art. 2", "Art. 2"))
    out = render.toc(_J(), t, keyword="art")
    assert "Article 1" in out and "Art. 2" in out and "Part I" not in out


def test_keyword_ignores_spaces_and_dots():
    t = _toc(("Art. L. 124-11", "L. 124-11"), ("Art. L. 5", "L. 5"))
    out = render.toc(_J(), t, keyword="L.124-11")
    assert "L. 124-11" in out and "1 of 2" in out


def test_toc_zero_match_explains_title_only_and_note_survives():
    t = _toc(("Dictamen", ""))
    t.note = "no article split"
    out = render.toc(_J(), t, keyword="52")
    assert "no article split" in out and "numbers and titles only" in out


def test_headers():
    j = _J()
    h = lambda r: render.caselaw_results(j, "q", r, limit=5, page_no=1).splitlines()[0]
    assert "count not reported" in h(Results([], total=None))
    assert "found for" not in h(Results([], total=7, query_ignored=True))
    assert "not a finding" in h(Results([], total=0, note="n"))
    assert "0 decisions found" in h(Results([], total=0))


def test_per_hit_flags():
    j = _J()
    r = render.caselaw_results(j, "q", Results([DecisionHit("a", "T", has_text=False)], total=1), limit=5, page_no=1)
    assert "get_decision" not in r
    r = render.legislation_results(j, "q", Results([LawHit("a", "T", has_toc=False)], total=1), limit=5, page_no=1)
    assert "Contents:" not in r
    r = render.legislation_results(j, "q", Results([LawHit("a", "T")], total=1), limit=5, page_no=1)
    assert "Contents:" in r


def test_no_contents_line_when_toc_unsupported():
    class N(Jurisdiction):
        code, name = "nn", "N"
    r = render.legislation_results(N(), "q", Results([LawHit("a", "T")], total=1), limit=5, page_no=1)
    assert "Contents:" not in r


def test_sources_line_narrowed_to_kind():
    class M(Jurisdiction):
        code, name = "mm2", "M"
        sources = (Source("Court", "https://c", covers=("caselaw",)),
                   Source("Laws", "https://l", covers=("legislation",)))
    assert server._sources_line(M(), "search_legislation") == "Laws (https://l)"


def test_unknown_top_level_args_rejected_and_query_optional():
    async def go():
        with pytest.raises(Exception, match="Unknown argument|extra_forbidden|Extra inputs"):
            await server.mcp.call_tool("search_caselaw", {"jurisdiction": "al", "query": "x", "date_from": "2022"})
    asyncio.run(go())
    assert server.mcp._tool_manager.get_tool("search_caselaw").parameters["required"] == ["jurisdiction"]


def test_no_filters_message():
    class F(Jurisdiction):
        code, name = "ff", "F"
    msg = server._check_filters(F(), {"year": 1}, "caselaw")
    assert "no caselaw filters at all" in msg
