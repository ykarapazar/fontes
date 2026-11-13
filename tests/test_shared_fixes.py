"""Offline tests: scope-limit refusal leads with the pointer, stray top-level args point to
`filters`, TOC keyword ignores accents and lists entries on a miss, neutral zero header."""
import pytest
from mcp.server.fastmcp.exceptions import ToolError

from world_legal_mcp import render, server
from world_legal_mcp.base import Jurisdiction, Source
from world_legal_mcp.models import Results, Toc, TocEntry


class _J(Jurisdiction):
    code = "zy"
    name = "Noland"
    sources = (Source("Courts", "https://c.example", covers=("caselaw",)),)
    notes = "Read Acts at https://acts.example."


def test_unsupported_leads_with_pointer_not_failure():
    out = server._unsupported(_J(), "search_legislation")
    first = out.splitlines()[0]
    assert "https://acts.example" in first and "not a failure" in first


async def test_stray_top_level_arg_points_to_filters():
    with pytest.raises(ToolError) as e:
        await server.mcp.call_tool("search_caselaw", {"jurisdiction": "zz", "query": "q",
                                                      "date_from": "2022"})
    assert "inside `filters`" in str(e.value) and "date_from" in str(e.value)


def test_toc_keyword_accent_insensitive_and_lists_on_miss():
    t = Toc(id="x", title="Loi", url="u", entries=[TocEntry(title="Article 7 préavis", provision="7"),
                                                  TocEntry(title="Article 1", provision="1")])
    assert "Article 7" in render.toc(_J(), t, keyword="preavis")
    miss = render.toc(_J(), t, keyword="zzz")
    assert "no matching entries" in miss and "Article 1" in miss


def test_zero_header_is_neutral():
    h = render._header(_J(), "case law", "decisions", "q", Results([], total=0, note="n"), 10, 1)
    assert "not a finding" in h and "returned" not in h
