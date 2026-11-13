from world_legal_mcp.jurisdictions import ee


def test_joustunud_status_is_explained():
    assert "not repealed" in ee._status_label("JOUSTUNUD")
    assert ee._status_label("KEHTIV") == "KEHTIV"
    assert ee._status_label(None) == ""


def test_in_force_drops_one_off_and_title_hits_lead_full_text(monkeypatch):
    import asyncio

    def hit(i, status):
        return {"id": i, "title": f"T{i}", "reportStatus": status}

    async def fake(path, what, json=None, headers=None):
        g = json["general"]
        if g["searchInTitle"]:
            rows = [hit("1", "JOUSTUNUD"), hit("2", "KEHTIV")]
        else:
            rows = [hit("2", "KEHTIV"), hit("3", "KEHTIV")]
        return {"results": rows, "kehtivad": 9, "koik": 9}

    monkeypatch.setattr(ee, "_api_json", fake)
    a = ee.EE() if hasattr(ee, "EE") else [v for v in vars(ee).values() if isinstance(v, type) and hasattr(v, "search_legislation")][0]()
    r = asyncio.run(a.search_legislation("x", limit=10, page=1, filters={"in_text": "true"}))
    assert [h.id for h in r.items] == ["2", "3"]
    assert r.total == 2


def test_provision_says_no_dated_wording():
    assert "no as-at-date" in ee._CURRENT_ONLY


def test_word_start_ranks_before_compound_noise():
    assert ee._word_start("Töölepingu seadus", ["tööleping"])
    assert not ee._word_start("Patendikoostöölepinguga tasud", ["tööleping"])


def test_title_search_hides_compound_only_noise(monkeypatch):
    import asyncio

    async def fake(path, what, json=None, headers=None):
        rows = [{"id": "1", "title": "Töölepingu seadus", "reportStatus": "KEHTIV"},
                {"id": "2", "title": "Patendikoostöölepingu seadus", "reportStatus": "KEHTIV"}]
        return {"results": rows, "kehtivad": 2, "koik": 2}

    monkeypatch.setattr(ee, "_api_json", fake)
    cls = [v for v in vars(ee).values() if isinstance(v, type) and hasattr(v, "search_legislation")][0]
    r = asyncio.run(cls().search_legislation("tööleping", limit=10, page=1, filters={}))
    assert [h.id for h in r.items] == ["1"]
    assert r.total == 1
