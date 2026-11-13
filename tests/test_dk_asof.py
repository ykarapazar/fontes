from world_legal_mcp.jurisdictions.dk import Denmark


def _law(doctype):
    return {"status": "Valid", "changes": [], "as_of": "1953-06-05", "doctype": doctype}


def test_non_consolidated_text_not_presented_as_current():
    law = dict(_law("LOV"), changes=["1990-01-01: Lov nr 1"])
    note = Denmark._caveat(law)
    assert "signing date" in note and "not a currency date" in note


def test_valid_act_without_amendments_states_currency():
    note = Denmark._caveat(_law("LOV"))
    assert "signing date" in note and "lists no later amending acts" in note


def test_consolidated_text_has_no_signing_note():
    assert "signing date" not in Denmark._caveat(_law("LBK"))


def test_bills_not_marked_in_force(monkeypatch):
    import asyncio
    from types import SimpleNamespace
    from world_legal_mcp import _http

    doc = {"title": "Forslag til Danmarks Riges Grundlov", "documentType": "Lovforslag som fremsat",
           "retsinfoLink": "/eli/ft/200512L00004", "isHistoryFlag": False,
           "offentliggoerelsesDato": "2005-10-06T00:00:00"}

    async def fake_get(*a, **k):
        return SimpleNamespace(status_code=200, json=lambda: {"documents": [doc], "resultCount": 1})
    monkeypatch.setattr(_http, "get", fake_get)
    res = asyncio.run(Denmark().search_legislation("Grundlov", filters={"historical": "true"}))
    assert "ikke gældende" in res.items[0].status


def test_decisions_not_marked_in_force(monkeypatch):
    import asyncio
    from types import SimpleNamespace
    from world_legal_mcp import _http

    doc = {"title": "Erstatningsansvarsloven § 1", "documentType": "Endelig adm. afgørelse",
           "retsinfoLink": "/eli/retsinfo/2020/10125", "isHistoryFlag": False,
           "offentliggoerelsesDato": "2021-09-29T00:00:00"}

    async def fake_get(*a, **k):
        return SimpleNamespace(status_code=200, json=lambda: {"documents": [doc], "resultCount": 1})

    monkeypatch.setattr(_http, "get", fake_get)
    res = asyncio.run(Denmark().search_legislation("x"))
    assert "gældende-status" in res.items[0].status and "decisions" in res.note
