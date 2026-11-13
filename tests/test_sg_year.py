import asyncio

import pytest

from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions.sg import Singapore as Adapter


def _adapter():
    return Adapter.__new__(Adapter)


def test_year_spec_says_single_year():
    assert "One year only" in Adapter.caselaw_filters["year"]


@pytest.mark.parametrize("y", ["2022-", ">=2022", "2022-2024"])
def test_range_rejected_plainly(y):
    with pytest.raises(BadRequest, match="date range"):
        asyncio.run(_adapter().search_caselaw("x", limit=1, page=1, filters={"year": y}))


def test_no_legislation_pointer_names_sso():
    assert not Adapter.supports(_adapter(), "search_legislation")
    assert any("sso.agc.gov.sg" in s.url for s in Adapter.sources)
    assert all("legislation" not in s.covers for s in Adapter.sources)
