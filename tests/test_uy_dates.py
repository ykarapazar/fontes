import asyncio

from world_legal_mcp.jurisdictions import uy


def _run(filters):
    captured = {}

    async def fake_post(form, data):
        captured.update(data)
        return ""

    orig = uy._bjn_post
    uy._bjn_post = fake_post
    try:
        form = {"query": "q", "number": "n", "search": "s", "types": "", "importance": "",
                "size": "", "sort": "", "from": "f", "to": "t"}
        asyncio.run(uy._bjn_search(form, "daño moral", "", filters, 10))
    finally:
        uy._bjn_post = orig
    return captured


def test_open_ended_from_gets_end_date():
    d = _run({"date_from": "2022-01-01"})
    assert d["f"] == "01/01/2022" and d["t"]


def test_open_ended_to_gets_start_date():
    d = _run({"date_to": "2022-01-01"})
    assert d["t"] == "01/01/2022" and d["f"] == "01/01/1900"


def test_no_dates_sends_none():
    d = _run({})
    assert "f" not in d and "t" not in d
