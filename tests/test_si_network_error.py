import asyncio

import pytest

from world_legal_mcp.base import SourceError
from world_legal_mcp.jurisdictions import si


def test_empty_network_error_is_explained(monkeypatch):
    async def boom(*a, **k):
        raise ConnectionResetError()

    monkeypatch.setattr(si._http, "post", boom)
    with pytest.raises(SourceError) as ei:
        asyncio.run(si._json("POST", "https://sodnapraksa.si/backend/api/x", "sodnapraksa.si search"))
    m = str(ei.value)
    assert "cannot reach sodnapraksa.si" in m and "ConnectionResetError" in m and "Retry" in m
