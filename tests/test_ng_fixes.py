import asyncio

from world_legal_mcp.jurisdictions import ng

_BODY = "\n".join(
    ["Section :", "1. Alpha.", "2. Beta.", "3. Gamma.", "4. Delta.", "5. Epsilon."]
    + ["1.—(1) Alpha text one.", "more", "2.—(1) Beta text.", "more",
       "3.—(1) Gamma text.", "more", "4. Delta text.", "more", "5.—(1) Epsilon text.", "more"])


def test_split_finds_dash_sections_not_arrangement():
    order, secs = ng._split(_BODY)
    assert order == ["1", "2", "3", "4", "5"]
    assert secs["3"].startswith("3.—(1) Gamma text.")


def test_split_arrangement_only_gives_nothing():
    assert ng._split("1. Alpha.\n2. Beta.\n3. Gamma.\n4. Delta.\n")[0] == []


def test_caselaw_notes(monkeypatch):
    rows = [{"case_id": 65, "caseTitle": "A v B", "suitNo": "SC 91/2002", "judgement": "x",
             "dateJudgement": "2012-10-19", "citation": " (2007) 1NILR 261"},
            {"case_id": 75, "caseTitle": "A v B", "suitNo": "SC91/2002", "judgement": "x",
             "dateJudgement": "2007-01-26", "citation": "(2007) 1NILR 261"},
            {"case_id": 530, "petitioner": "INEC", "respondent": "LPP", "suitNo": "SC/CV/505/2026",
             "judgement": "", "dateJudgement": "2026-10-08"}]

    async def fake(url, params=None, what="request"):
        return {"success": True, "data": rows}
    monkeypatch.setattr(ng, "_json", fake)
    ng._search_cache.clear()
    res = asyncio.run(ng.Nigeria().search_caselaw("", filters={"date_from": "2000-01-01"}))
    assert [h.id for h in res.items] == ["75", "530"]     # 65's 2012 date contradicts its (2007) citation
    assert "same judgment twice with different dates" in res.note and "id 65" in res.note
    assert "scanned PDFs" in res.note and "between 2013 and 2022" in res.note


def test_legislation_not_found_note(monkeypatch):
    async def cat():
        return []
    monkeypatch.setattr(ng, "_catalogue_load", cat)
    monkeypatch.setattr(ng, "_plac_load", cat)
    res = asyncio.run(ng.Nigeria().search_legislation("Criminal Code"))
    assert res.total == 0 and "Criminal Code Act" in res.note


def test_title_search_finds_untitled_recent_rows(monkeypatch):
    calls = []

    async def fake(url, params=None, what="request"):
        calls.append(dict(params))
        if "caseTitle" in params:
            return {"data": []}
        return {"data": [{"case_id": 518, "petitioner": "INDEPENDENT NATIONAL ELECTORAL COMMISSION (INEC)",
                          "respondent": "ZENITH LABOUR PARTY", "suitNo": "SC/CV/495/2026",
                          "judgement": "", "dateJudgement": "2026-10-08"},
                         {"case_id": 9, "petitioner": "X", "respondent": "Y", "suitNo": "SC/1/2026",
                          "judgement": "", "dateJudgement": "2026-01-08"}]}
    monkeypatch.setattr(ng, "_json", fake)
    ng._search_cache.clear()
    res = asyncio.run(ng.Nigeria().search_caselaw("INEC", filters={"date_from": "2026-01-01"}))
    assert [h.id for h in res.items] == ["518"]


def test_duplicate_judgment_flagged_in_search_and_decision(monkeypatch):
    a = {"case_id": 65, "caseTitle": "A v B", "suitNo": "SC 91/2002", "judgement": "x",
         "dateJudgement": "2012-10-19", "citation": " (2007) 1NILR 261"}
    b = {"case_id": 75, "caseTitle": "A v B", "suitNo": "SC91/2002", "judgement": "x",
         "dateJudgement": "2007-01-26", "citation": "(2007) 1NILR 261"}

    async def fake(url, params=None, what="request"):
        if what == "judgment":
            return {"data": dict(a)}
        return {"data": [a, b]}
    monkeypatch.setattr(ng, "_json", fake)
    ng._search_cache.clear()
    res = asyncio.run(ng.Nigeria().search_caselaw("A v B"))
    assert [h.id for h in res.items] == ["75"]
    assert "same judgment twice with different dates" in res.note and "2012-10-19" in res.note
    dec = asyncio.run(ng.Nigeria().get_decision("65"))
    assert "id 75 (2007-01-26)" in dec.metadata["Note"]


def test_split_prefers_act_body_over_longer_regulations_run():
    act = ["1. Alpha text", "x", "2. Beta text", "x", "3. Gamma text", "x", "4. Delta text", "x",
           "5. Eps text", "x", "6. Zeta text", "x"]
    regs = [f"{n}. Reg {n} " + "long text " * 200 for n in (1, 2, 3)]
    order, _ = ng._split("\n".join(act + regs))
    assert order == ["1", "2", "3", "4", "5", "6"]


def test_decision_date_follows_citation_year(monkeypatch):
    a = {"case_id": 65, "caseTitle": "A v B", "suitNo": "SC 91/2002", "judgement": "x" * 10,
         "dateJudgement": "2012-10-19", "citation": "(2007) 1NILR 261"}
    b = dict(a, case_id=75, suitNo="SC91/2002", dateJudgement="2007-01-26")

    async def fake(url, params=None, what="request"):
        return {"success": True, "data": a if "passed" in url else [a, b]}
    monkeypatch.setattr(ng, "_json", fake)
    d = asyncio.run(ng.Nigeria().get_decision("65"))
    assert d.date == "2007-01-26"


def test_caselaw_topic_query_zero_hits_says_no_text_search(monkeypatch):
    async def fake(url, params=None, what="request"):
        return {"success": True, "data": []}
    monkeypatch.setattr(ng, "_json", fake)
    ng._search_cache.clear()
    res = asyncio.run(ng.Nigeria().search_caselaw("breach of contract"))
    assert "cannot search the judgment text" in res.note


def test_multiword_title_found_when_not_contiguous(monkeypatch):
    row = {"case_id": 75, "caseTitle": "Adetoun Oladeji (Nig.) Ltd v Nigerian Breweries Plc",
           "suitNo": "SC91/2002", "judgement": "x", "dateJudgement": "2007-01-26"}

    async def fake(url, params=None, what="request"):
        t = params.get("caseTitle", "").lower()
        if t and t in row["caseTitle"].lower():
            return {"data": [row]}
        return {"data": []}
    monkeypatch.setattr(ng, "_json", fake)
    ng._search_cache.clear()
    res = asyncio.run(ng.Nigeria().search_caselaw("Adetoun Oladeji Nigerian Breweries"))
    assert [h.id for h in res.items] == ["75"]
