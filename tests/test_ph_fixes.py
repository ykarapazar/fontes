import asyncio

from world_legal_mcp.jurisdictions import ph


def _row(title, date):
    return {"citation": title, "url": "juri1996/mar1996/gr_1_1996.html", "date": date}


def test_phrase_matches_ranked_first(monkeypatch):
    rows = [_row("MAURO P. MAGTIBAY vs. X", "1996-03-28"), _row("ANG TIBAY vs. CIR", "1940-02-27")]

    async def fake(module, params):
        return {"data": rows, "total": 2}
    monkeypatch.setattr(ph, "_api", fake)
    res = asyncio.run(ph.Philippines().search_caselaw("Ang Tibay"))
    assert res.items[0].title.startswith("ANG TIBAY")
    assert "one year, no ranges" in res.note


def test_zero_hit_says_topic_search_unsupported(monkeypatch):
    async def fake(module, params):
        return {"data": [], "total": 0}
    monkeypatch.setattr(ph, "_api", fake)
    res = asyncio.run(ph.Philippines().search_caselaw("illegal dismissal"))
    assert "cannot work" in res.note
    assert "leave the query empty" in res.note


def test_revised_penal_code_maps_to_act_3815(monkeypatch):
    seen = {}

    async def fake(module, params):
        seen.update(module=module, **params)
        return {"data": [{"act_number": "Act No. 3815", "description": "An Act Revising the Penal Code",
                          "url": "statutes/acts/act1930/act_3815_1930.html", "date": "1930-12-08"}],
                "total": 1}
    monkeypatch.setattr(ph, "_api", fake)
    res = asyncio.run(ph.Philippines().search_legislation("Revised Penal Code", filters={"type": "act"}))
    assert seen["search"] == "3815" and res.items[0].id == "act_3815_1930"


def test_labor_code_maps_to_pd_442(monkeypatch):
    seen = {}

    async def fake(module, params):
        seen.update(module=module, **params)
        return {"data": [{"pd_number": "Presidential Decree No. 442", "citation": "Labor Code of the Philippines",
                          "url": "statutes/presdecs/pd1974/pd_442_1974.html", "date": "1974-05-01"}],
                "total": 1}
    monkeypatch.setattr(ph, "_api", fake)
    for q, f in (("Labor Code", None), ("Labor Code of the Philippines", {"type": "pd"})):
        res = asyncio.run(ph.Philippines().search_legislation(q, filters=f))
        assert seen["module"] == "presidential" and seen["search"] == "442"
        assert res.items[0].id == "pd_442_1974"


def test_party_name_hits_carry_caveat(monkeypatch):
    async def fake(module, params):
        return {"data": [{"gr_number": "245918", "citation": "A vs. LABOR UNION",
                          "url": "juri2022/nov2022/gr_245918_2022.html", "date": "2022-11-29"}],
                "total": 1}
    monkeypatch.setattr(ph, "_api", fake)
    res = asyncio.run(ph.Philippines().search_caselaw("labor"))
    assert "NOT the legal issue" in res.note
    res = asyncio.run(ph.Philippines().search_caselaw("245918"))
    assert "NOT the legal issue" not in res.note
