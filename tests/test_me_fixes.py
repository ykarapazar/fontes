import asyncio

import pytest

from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions import me

DB = [{"iddok": str(i), "djelovodni_broj": n, "datum": "2022-01-17"} for i, n in enumerate(
    ["U-III br.9/18", "U-III br.19/18", "U-I br. 9/18", "U-I br. 19/18"])]


def _patch(monkeypatch, calls):
    async def fake(self, form, start, length):
        calls.append((dict(form), start, length))
        rows = [r for r in DB if form.get("vrsta_predmeta", "svi") in ("svi", me.TYPES["U-I"])
                or r["djelovodni_broj"].startswith("U-III")]
        if form.get("vrsta_predmeta") == me.TYPES["U-I"]:
            rows = [r for r in DB if r["djelovodni_broj"].startswith("U-I ")]
        return {"data": rows[start:start + length], "recordsFiltered": len(rows)}
    monkeypatch.setattr(me.Montenegro, "_search", fake)


def _search(**kw):
    return asyncio.run(me.Montenegro().search_caselaw("", **kw))


def test_case_number_prefix_exact(monkeypatch):
    _patch(monkeypatch, [])
    r = _search(filters={"case_number": "U-I br. 9/18"})
    assert [h.case_number for h in r.items] == ["U-I br. 9/18"]


def test_page_size_does_not_change_source_request(monkeypatch):
    calls = []
    _patch(monkeypatch, calls)
    _search(limit=2)
    _search(limit=5)
    assert {c[2] for c in calls} == {me.MAX_LIMIT}


def test_year_range_newest_first(monkeypatch):
    calls = []
    _patch(monkeypatch, calls)
    r = _search(filters={"year": "2023-2025"})
    assert [c[0]["godina_pretraga"] for c in calls] == ["2025", "2024", "2023"]
    assert r.total == 12


def test_bad_year_range(monkeypatch):
    _patch(monkeypatch, [])
    with pytest.raises(BadRequest):
        _search(filters={"year": "2025-2023"})


def test_hit_date_is_not_decision_date():
    h = me._hit({"iddok": "1", "djelovodni_broj": "U-III br.339/24", "datum": "2024-02-20"})
    assert h.date == "" and "Datum upisa: 2024-02-20" in h.snippet


def test_decision_has_per_id_url_and_legislation_pointer(monkeypatch):
    class R:
        def __init__(self, status, body=b"", js=None):
            self.status_code, self.content, self._js = status, body, js
        def json(self):
            return self._js

    listing = {"poruka": "Uspjesno", "linkovi": [{
        "link": "<a href='./webfolder/x.docx'>", "naziv_fajla": "a.docx",
        "korisnicki_naziv": "339-24A.docx", "tip": "Odluka"}]}

    async def fake_get(url, **kw):
        return R(200, js=listing) if "obrada_fajlovi" in url else R(404)

    async def fake_search(self, form, start, length):
        return {"data": [], "recordsFiltered": 0}
    monkeypatch.setattr(me._http, "get", fake_get)
    monkeypatch.setattr(me.Montenegro, "_search", fake_search)
    d = asyncio.run(me.Montenegro().get_decision("43750"))
    assert d.url.endswith("obrada_fajlovi.php?iddok=43750")
    assert d.url in d.metadata["Citiranje"]
    assert "sluzbenilist.me" in me.Montenegro.notes
