import asyncio

from world_legal_mcp.jurisdictions import ecowas


def test_toc_entry_page_is_not_tail_of_number():
    assert not ecowas._TOC_ENTRY.match("22. ECW/CCJ/APP/03/11 & ECW/CCJ/APP/03/11")
    m = ecowas._TOC_ENTRY.match("22. ECW/CCJ/APP/03/11 & ECW/CCJ/APP/03/11 -RULING N O. ECW/CCJ/RUL/10/12): 257")
    assert m and m[3] == "257"
    m = ecowas._TOC_ENTRY.match("4. ECW/CCJ/APP/15/10  - ECW/CCJ/RUL/02/12: 43")
    assert m and m[3] == "43"


def test_search_note_points_to_nature_and_report_year(monkeypatch):
    rows = [{"title": "A v. B", "number": "ECW/CCJ/JUD/01/20", "id": "ECW/CCJ/JUD/01/20", "year": "2019",
             "nature": "Human Rights", "type": "Judgement", "date": "2020-01-01", "files": {"ENG": "u"}}]

    async def fake():
        return rows
    monkeypatch.setattr(ecowas, "_decisions", fake)
    res = asyncio.run(ecowas.ECOWAS().search_caselaw("A v B"))
    assert res.total == 1
    assert "nature" in res.note and "report_year" in res.note and "title" in res.note


def test_zero_hits_error_explains_title_only_and_report_year(monkeypatch):
    async def fake():
        return []
    monkeypatch.setattr(ecowas, "_decisions", fake)
    import pytest
    from world_legal_mcp.base import NotFound
    with pytest.raises(NotFound) as e:
        asyncio.run(ecowas.ECOWAS().search_caselaw("Media Foundation"))
    assert "title and decision number only" in str(e.value) and "report_year" in str(e.value)


def test_hit_snippet_warns_about_scans():
    row = {"title": "A v. B", "number": "ECW/CCJ/JUD/01/20", "id": "ECW/CCJ/JUD/01/20", "year": "2019",
           "nature": "", "type": "Judgement", "date": "2020-01-01", "files": {"ENG": "u"}}
    assert "scans" in ecowas._hit(row).snippet


def test_missing_citation_names_next_decisions(monkeypatch):
    import pytest
    from world_legal_mcp.base import NotFound
    vol = {"vol": "2012", "url": "u", "cases": [{"page": 43, "title": "Media Foundation v Gambia"}]}

    async def fake_report_case(ident):
        return None

    async def fake_volume(v):
        return vol
    monkeypatch.setattr(ecowas, "_report_case", fake_report_case)
    monkeypatch.setattr(ecowas, "_volume", fake_volume)
    with pytest.raises(NotFound) as e:
        asyncio.run(ecowas.ECOWAS().get_decision("(2012) CCJELR 11"))
    assert "page where a reported decision starts" in str(e.value) and "CCJELR 43" in str(e.value)


def test_hit_shows_scan_status():
    row = {"title": "A v. B", "number": "ECW/CCJ/JUD/01/20", "id": "ECW/CCJ/JUD/01/20", "year": "2019",
           "nature": "Human Rights", "type": "Judgement", "date": "2020-01-01", "files": {"ENG": "u"}}
    assert "scan, no text layer" in ecowas._hit(row, True).snippet
    assert "text layer present" in ecowas._hit(row, False).snippet
    assert "not checked" in ecowas._hit(row).snippet


def test_search_checks_scan_status_of_first_hits(monkeypatch):
    rows = [{"title": f"A v. B{i}", "number": f"ECW/CCJ/JUD/0{i}/20", "id": f"ECW/CCJ/JUD/0{i}/20",
             "year": "2019", "nature": "Human Rights", "type": "Judgement", "date": "2020-01-01",
             "files": {"ENG": "u"}} for i in range(1, 8)]

    async def fake():
        return rows

    async def fake_scan(row):
        return True
    monkeypatch.setattr(ecowas, "_decisions", fake)
    monkeypatch.setattr(ecowas, "_is_scan", fake_scan)
    res = asyncio.run(ecowas.ECOWAS().search_caselaw("v", limit=7))
    assert sum("scan, no text layer" in h.snippet for h in res.items) == 5
    assert sum("not checked" in h.snippet for h in res.items) == 2


def test_legislation_gap_names_court_basic_texts():
    assert any("courtecowas.org/about_us/basic-text" in g for g in ecowas.ECOWAS.gaps)
