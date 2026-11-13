import asyncio

from world_legal_mcp.jurisdictions import cv


def test_juris_search_sorts_newest_first_with_query(monkeypatch):
    class R:
        status_code, headers = 200, {"content-type": "application/json"}

        def json(self):
            return {"records": [], "queryRecordCount": 0}
    seen = {}

    async def fake_get(url, params=None, headers=None):
        seen.update(params)
        return R()
    monkeypatch.setattr(cv._http, "get", fake_get)
    asyncio.run(cv._juris_search("despedimento", "stj", "", 10, 1))
    assert seen["sorts[dataAcordao]"] == "-1" and seen["queries[freesearch]"] == "despedimento"


def test_legislation_flags_scanned_constitution_and_labour_code(monkeypatch):
    async def cats():
        return {"1": "Leis Constitucionais"}

    async def files(cid):
        return [{"ID": 3368, "post_title": "07 - CONSTITUIÇÃO DA REPÚBLICA de 1992", "linkdownload": ""}]
    monkeypatch.setattr(cv, "_law_cats", cats)
    monkeypatch.setattr(cv, "_tc_files", files)
    r = asyncio.run(cv.CaboVerde().search_legislation("Constituição"))
    assert "SCANNED" in r.items[0].snippet and "Código Laboral" not in r.note
    r = asyncio.run(cv.CaboVerde().search_legislation("Código do Trabalho"))
    assert "Not held" in r.note


def test_int_year_accepted_and_scanned_laws_have_no_toc(monkeypatch):
    class R:
        status_code, headers = 200, {"content-type": "application/json"}

        def json(self):
            return {"records": [], "queryRecordCount": 0}
    seen = {}

    async def fake_get(url, params=None, headers=None):
        seen.update(params)
        return R()
    monkeypatch.setattr(cv._http, "get", fake_get)
    r = asyncio.run(cv.CaboVerde().search_caselaw("trabalho", filters={"court": "stj", "year": 2025}))
    assert seen["queries[initial_date]"] == "01/01/2025" and "No decision" in r.note

    async def cats():
        return {"1": "Leis Constitucionais"}

    async def files(cid):
        return [{"ID": 3363, "post_title": "03 - CONSTITUIÇÃO DA REPÚBLICA de 1980", "linkdownload": ""}]
    monkeypatch.setattr(cv, "_law_cats", cats)
    monkeypatch.setattr(cv, "_tc_files", files)
    res = asyncio.run(cv.CaboVerde().search_legislation("Constituição"))
    assert res.items[0].has_toc is False and "SCANNED" in res.items[0].snippet
