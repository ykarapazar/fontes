import asyncio

from world_legal_mcp.jurisdictions import cv
from world_legal_mcp.models import DecisionHit


def test_article_stops_before_next_division_heading():
    text = ("Artigo 121.º\nReabilitação\n1. Texto.\n2. Lei especial regulará.\nLIVRO II\nParte especial\n"
            "TÍTULO I\nCrimes\nArtigo 122.º\nHomicídio\n1. Quem matar.")
    _, arts = cv._articles(text)
    assert arts["121"].endswith("2. Lei especial regulará.")
    assert arts["122"].startswith("Artigo 122")


def test_tc_year_listing_drops_duplicate_decisions(monkeypatch):
    def h(i, t):
        return DecisionHit(id=i, title=t, court="", case_number=cv._case_number(t), url="")

    async def fake(y):
        return [h("1", "Acórdão 21-2022 - A v B"), h("2", "Acórdão 21-2022 - A v B"), h("3", "Acórdão 22-2022 - C")]
    monkeypatch.setattr(cv, "_tc_year", fake)
    r = asyncio.run(cv.CaboVerde().search_caselaw("", filters={"court": "tc", "year": "2022"}))
    assert [x.id for x in r.items] == ["1", "3"] and r.total == 2
    assert "titles only" in r.note


def test_legislation_note_flags_missing_labour_code_and_scans(monkeypatch):
    async def cats():
        return {"1": "Leis Constitucionais"}

    async def files(cid):
        return [{"ID": 3368, "post_title": "07 - CONSTITUIÇÃO DA REPÚBLICA de 1992", "linkdownload": ""}]
    monkeypatch.setattr(cv, "_law_cats", cats)
    monkeypatch.setattr(cv, "_tc_files", files)
    r = asyncio.run(cv.CaboVerde().search_legislation("Constituição"))
    assert "Código Laboral" not in r.note and "scans" in r.note


def test_juris_search_retries_quoted_phrase_on_site_500(monkeypatch):
    import asyncio

    class R:
        def __init__(self, code, body=None):
            self.status_code, self.headers, self._b = code, {"content-type": "application/json"}, body

        def json(self):
            return self._b

    seen = []

    async def fake_get(url, params=None, headers=None):
        seen.append(params["queries[freesearch]"])
        if len(seen) == 1:
            return R(500)
        return R(200, {"records": [{"ecli": "JURIS:CV:STJ:2012:323", "tribunal": "STJ"}], "queryRecordCount": 1})

    monkeypatch.setattr(cv._http, "get", fake_get)
    res = asyncio.run(cv._juris_search("despedimento", "stj", "", 10, 1))
    assert seen == ["despedimento", '"despedimento"'] and len(res.items) == 1 and "exact phrase" in res.note


def test_juris_search_note_states_newest_match_date(monkeypatch):
    class R:
        status_code, headers = 200, {"content-type": "application/json"}

        def json(self):
            return {"records": [{"ecli": "JURIS:CV:STJ:2019:949", "tribunal": "STJ",
                                 "dataAcordao": "2019-11-28"}], "queryRecordCount": 1}

    async def fake_get(url, params=None, headers=None):
        return R()
    monkeypatch.setattr(cv._http, "get", fake_get)
    res = asyncio.run(cv._juris_search("despedimento", "stj", "", 10, 1))
    assert "newest decision containing the search words is dated 2019-11-28" in res.note and "no later decision" in res.note
