import asyncio

import pytest

from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions import cz

_F = {"textDokumentu": "t", "oznacenivecivcelku": "c", "soudsenat": "s",
      "datumvydanirozhodnuti": "d"}


def test_nss_date_filters_sent(monkeypatch):
    sent = {}

    async def form():
        return {"fields": _F, "data": [("d.HodnotaDatumACasOd", ""), ("d.HodnotaDatumACasDo", "")],
                "nss": "278"}

    async def page(method, url, what, content="", **kw):
        sent.update(dict(p.split("=") for p in content.split("&")))
        return "<html></html>"
    monkeypatch.setattr(cz, "_nss_form", form)
    monkeypatch.setattr(cz, "_page", page)
    asyncio.run(cz._nss_search("x", 5, 1, {"date_from": "2022-01-05", "date_to": "2022-12-31"}))
    assert sent["d.HodnotaDatumACasOd"] == "5.+1.+2022"
    assert sent["d.HodnotaDatumACasDo"] == "31.+12.+2022"


def test_nss_part_rejected():
    with pytest.raises(BadRequest):
        asyncio.run(cz._nss_search("x", 5, 1, {"part": "T"}))


def test_sbirka_note_has_no_conflicting_estimate(monkeypatch):
    items = "".join(f'<article class="listing-item"><h2><a href="https://s/sbirka/{i}/">T{i}</a></h2>'
                    '<p><span>Datum: 01.01.2023</span></p></article>' for i in range(10))
    html = f'<ul class="pagination"><li><a>1</a></li><li><a>6</a></li></ul>{items}'

    async def page(*a, **kw):
        return html
    monkeypatch.setattr(cz, "_page", page)
    r = asyncio.run(cz._sbirka_search("x", 5, 1, {}))
    assert r.total is None and "About" not in r.note
