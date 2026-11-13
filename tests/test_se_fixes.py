import asyncio

from world_legal_mcp.jurisdictions import se


def _run(filters=None, query="hyra", reply=None):
    sent = {}

    async def fake(method, url, what, **kw):
        sent.update(kw["json"] if "json" in kw else {})
        return reply or {"publiceringLista": [], "total": 0}
    orig, se._json = se._json, fake
    try:
        asyncio.run(se.Sweden().search_caselaw(query, filters=filters))
    finally:
        se._json = orig
    return sent


def test_citation_uses_exact_phrase():
    for q in ("NJA 2024 s. 386", "NJA 2024:33", "nja 2024  s 386"):
        b = _run(query=q)
        assert b["sokfras"]["andLista"] == [] and b["sokfras"]["exaktFras"] == " ".join(q.split())
    assert _run(query="skadestånd")["sokfras"]["andLista"] == ["skadestånd"]


def test_hovratt_group_and_court_names_in_error():
    assert _run({"court": "HovR"})["filter"]["domstolKodLista"] == list(se._HOVRATT)
    try:
        _run({"court": "xx"})
    except se.BadRequest as e:
        assert "HSV (Svea hovrätt)" in str(e)


def test_empty_text_gets_note():
    async def fake(method, url, what, **kw):
        return {"id": "x", "gruppKorrelationsnummer": "g", "innehall": "", "malNummerLista": ["T 1-26"],
                "bilagaLista": [{"filnamn": "a.pdf", "fillagringId": "1"}]}
    orig, se._json = se._json, fake
    try:
        d = asyncio.run(se.Sweden().get_decision("ff8aed0e-97f3-4605-8644-b29f42cdc189"))
    finally:
        se._json = orig
    assert "no body text" in d.text and "Bilagor" in d.text


def test_plain_unwraps_json_array_strings():
    assert se._plain('["NJA 1988 s. 89","NJA 1988:15"]') == "NJA 1988 s. 89; NJA 1988:15"
    assert se._plain("NJA 1977 not C 165") == "NJA 1977 not C 165"
    assert se._plain("[oparsbar") == "[oparsbar"


def test_search_legislation_fixed_page_size_sliced_by_offset():
    calls = []

    async def fake(method, url, what, **kw):
        p = kw["params"]
        calls.append((p["sz"], p["p"]))
        base = (p["p"] - 1) * p["sz"]
        return {"dokumentlista": {"@traffar": "200", "dokument": [
            {"beteckning": f"2000:{base + i + 1}", "dok_id": f"sfs-2000-{base + i + 1}"} for i in range(p["sz"])]}}
    orig, se._json = se._json, fake
    try:
        r = asyncio.run(se.Sweden().search_legislation("x", limit=25, page=2))   # hits 26-50
        assert calls == [(100, 1)] and [h.id for h in r.items] == [f"2000:{n}" for n in range(26, 51)]
        assert "boundary" not in r.note
        calls.clear()
        r = asyncio.run(se.Sweden().search_legislation("x", limit=20, page=5))   # hits 81-100
        assert calls == [(100, 1)] and [h.id for h in r.items] == [f"2000:{n}" for n in range(81, 101)]
        calls.clear()
        r = asyncio.run(se.Sweden().search_legislation("x", limit=30, page=4))   # hits 91-120
        assert calls == [(100, 1), (100, 2)] and [h.id for h in r.items] == [f"2000:{n}" for n in range(91, 121)]
        assert r.total == 200 and "boundary" in r.note
    finally:
        se._json = orig
