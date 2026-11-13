import asyncio

from world_legal_mcp.jurisdictions import hu


def _fake(monkeypatch):
    sent = []

    async def fake_search(form):
        sent.append(dict(form))
        start, n = int(sent[-1]["ResultStartIndex"]), int(sent[-1]["ResultCount"])
        return {"Success": True, "Count": 100,
                "List": [{"MeghozoBirosag": "Kúria", "Azonosito": f"Pfv.{i}/2020/1", "IndexId": str(i)}
                         for i in range(start, start + n)]}
    monkeypatch.setattr(hu, "_search", fake_search)
    return sent


def test_paging_offset_and_unstable_sort_note(monkeypatch):
    sent = _fake(monkeypatch)
    j = hu.Hungary()
    r = asyncio.run(j.search_caselaw("elbirtoklás", limit=5, page=6, filters={}))
    assert sent[-1]["ResultStartIndex"] == "25" and sent[-1]["ResultCount"] == "5"
    assert [h.case_number for h in r.items] == [f"Pfv.{i}/2020/1" for i in range(25, 30)]
    assert "sort='indexed'" in r.note          # default court sort: ties reorder on the source
    r = asyncio.run(j.search_caselaw("elbirtoklás", limit=25, page=2, filters={"sort": "indexed"}))
    assert sent[-1]["ResultStartIndex"] == "25" and sent[-1]["Rendezes"] == "IndexelesIdejeCsokkeno"
    assert "sort='indexed'" not in r.note
