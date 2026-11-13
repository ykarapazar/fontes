import asyncio

import pytest
from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions.dz import Algeria


def test_arabic_query_message_names_language():
    with pytest.raises(BadRequest, match="French"):
        asyncio.run(Algeria().search_caselaw("دستور", limit=5, page=1, filters={}))


def test_empty_query_message_unchanged():
    with pytest.raises(BadRequest, match="keywords"):
        asyncio.run(Algeria().search_caselaw("  ", limit=5, page=1, filters={}))
