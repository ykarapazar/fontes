"""Live checks against CourtListener. Needs network and WLM_US_COURTLISTENER_KEY (a free
account allows 5 requests a minute: this file spends 4)."""
import os

import pytest

from world_legal_mcp import server

pytestmark = pytest.mark.skipif(not os.environ.get("WLM_US_COURTLISTENER_KEY"),
                                reason="needs WLM_US_COURTLISTENER_KEY")


async def test_us_states_search_by_state_name_says_unofficial():
    out = await server.search_caselaw("us-states", "duty of care", limit=3,
                                      filters={"state": "Florida", "year_from": "2020"})
    assert "Unofficial source" in out and "Free Law Project" in out
    assert 'get_decision("us-states"' in out and "Florida" in out


async def test_us_states_decision_by_link():
    out = await server.get_decision(
        "us-states", "https://www.courtlistener.com/opinion/10348460/binion/", max_chars=3000)
    assert "Binion" in out and "02-23-00270-CV" in out and "Fort Worth" in out
    assert "Unofficial source" in out
