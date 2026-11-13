import asyncio

from world_legal_mcp.jurisdictions import ccj


def _row(cite, date):
    return {"key": ccj._key(cite), "cite": cite, "date": date, "jur": "AJ", "claimants": ["Yard"],
            "defendants": ["The Queen"], "desc": "", "keywords": "", "docs": [], "title": "Yard v The Queen"}


def test_country_code_searchable(monkeypatch):
    rows = {("2020", "20", "AJ"): _row("[2020] CCJ 20 (AJ) BB", "2020-05-01"),
            ("2020", "21", "AJ"): _row("[2020] CCJ 21 (AJ) GY", "2020-06-01")}

    async def fake():
        return rows
    monkeypatch.setattr(ccj, "_rows", fake)
    res = asyncio.run(ccj.CCJ().search_caselaw("Barbados", filters={"jurisdiction": "AJ"}))
    assert [i.id for i in res.items] == ["[2020] CCJ 20 (AJ)"]
    assert ccj._country("[2019] CCJ 9 (OJ)") == ""
    assert ccj._country("2020 CCJ 4 AJ (BZ)") == "Belize"
