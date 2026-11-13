import asyncio

import pytest

from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions import ec


def _fake(calls, total=679):
    async def fake_api(path, crit):
        p = crit["paginacion"]["page"]
        calls.append(p)
        n0 = (p - 1) * ec.PAGE
        return {"totalFilas": total, "dato": [{"resolucion": {"numero": f"{i}-19-JP/25"}}
                                              for i in range(n0, min(n0 + ec.PAGE, total))]}
    return fake_api


def test_search_caselaw_fetches_source_pages_and_slices(monkeypatch):
    calls = []
    monkeypatch.setattr(ec, "_api", _fake(calls))
    r = asyncio.run(ec.Ecuador().search_caselaw("consulta previa", limit=25, page=2))
    assert calls == [2, 3]                          # rows 25..49 sit on source pages 2-3 (20 rows each)
    assert [h.id for h in r.items] == [f"{i}-19-JP/25" for i in range(25, 50)]
    assert r.total == 679
    with pytest.raises(BadRequest):
        asyncio.run(ec.Ecuador().search_caselaw("consulta previa", limit=ec.MAX_LIMIT + 1))
