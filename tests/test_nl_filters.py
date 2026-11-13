import asyncio

from world_legal_mcp.jurisdictions import nl


class _R:
    status_code = 200
    url = "x"
    history: list = []

    def __init__(self, payload=None, content=b""):
        self._p, self.content = payload, content

    def json(self):
        return self._p


def test_caselaw_court_area_type_filters(monkeypatch):
    sent = {}

    async def fake_post(url, json=None, headers=None, **kw):
        sent.update(json)
        return _R({"Results": [], "ResultCount": 0})

    monkeypatch.setattr(nl._http, "post", fake_post)
    res = asyncio.run(nl._search_caselaw("ontslag wegens dringende reden", field="alle",
                                         sort="uitspraak", limit=5, start=0, period=None,
                                         court="hoge_raad", area="arbeidsrecht", kind="uitspraak"))
    assert sent["Instanties"] == [{"NodeType": 1, "Identifier": "Spirit.Npi.Ecli.Domain.TypeHr", "level": 0}]
    assert sent["Rechtsgebieden"][0]["NodeType"] == 3
    assert sent["Contentsoorten"] == [{"NodeType": 7, "Identifier": "uitspraak", "level": 0}]
    assert "quotes" in res.note


def test_legislation_exact_title_first(monkeypatch):
    def rec(bwb, title):
        return (f'<srw:record xmlns:srw="http://www.loc.gov/zing/srw/"><srw:recordData>'
                f'<dcterms:identifier xmlns:dcterms="http://purl.org/dc/terms/">{bwb}</dcterms:identifier>'
                f'<dcterms:title xmlns:dcterms="http://purl.org/dc/terms/">{title}</dcterms:title>'
                f'</srw:recordData></srw:record>')
    xml = ('<srw:searchRetrieveResponse xmlns:srw="http://www.loc.gov/zing/srw/"><srw:records>'
           + rec("BWBR0006797", "Wijzigingswet Wetboek van Strafrecht, enz.")
           + rec("BWBR0001854", "Wetboek van Strafrecht")
           + "</srw:records></srw:searchRetrieveResponse>").encode()

    async def fake_get(url, params=None, **kw):
        assert params["maximumRecords"] == "100"
        return _R(content=xml)

    monkeypatch.setattr(nl._http, "get", fake_get)
    res = asyncio.run(nl._search_wetten("Wetboek van Strafrecht", current_only=True, limit=1, page=1))
    assert [h.id for h in res.items] == ["BWBR0001854"]


def test_multiword_query_is_anded_and_court_name_hint(monkeypatch):
    terms = []

    async def fake_post(url, json=None, headers=None, **kw):
        terms.append(json["SearchTerms"][0]["Term"])
        return _R({"Results": [], "ResultCount": 0})

    monkeypatch.setattr(nl._http, "post", fake_post)
    res = asyncio.run(nl._search_caselaw("Hoge Raad ontslag", field="alle", sort="uitspraak",
                                         limit=5, start=0, period=None))
    assert terms == ["Hoge AND Raad AND ontslag", '"Hoge Raad ontslag"', '"Hoge Raad ontslag"', "Hoge Raad ontslag"]  # AND, phrase, loose
    assert "loose match" in res.note and "hoge_raad" in res.note


def test_date_sort_and_kingdom_court_notes(monkeypatch):
    async def fake_post(url, json=None, headers=None, **kw):
        return _R({"Results": [{"TitelEmphasis": "ECLI:NL:OGEAA:2017:728",
                                "Titel": "Gerecht in Eerste Aanleg van Aruba, 19-09-2017, X"}],
                   "ResultCount": 1})

    monkeypatch.setattr(nl._http, "post", fake_post)
    res = asyncio.run(nl._search_caselaw("ontslag", field="alle", sort="uitspraak",
                                         limit=5, start=0, period=None))
    assert "not relevance" in res.note and "Aruba" in res.note and "arbeidsrecht" in res.note


def test_legislation_topic_word_falls_back_to_title_words(monkeypatch):
    xml = ('<srw:searchRetrieveResponse xmlns:srw="http://www.loc.gov/zing/srw/"><srw:records>'
           '<srw:record><srw:recordData>'
           '<dcterms:identifier xmlns:dcterms="http://purl.org/dc/terms/">BWBR0005290</dcterms:identifier>'
           '<dcterms:title xmlns:dcterms="http://purl.org/dc/terms/">Burgerlijk Wetboek Boek 7</dcterms:title>'
           '</srw:recordData></srw:record></srw:records></srw:searchRetrieveResponse>').encode()
    empty = b'<srw:searchRetrieveResponse xmlns:srw="http://www.loc.gov/zing/srw/"><srw:records/></srw:searchRetrieveResponse>'

    async def fake_get(url, params=None, **kw):
        return _R(content=xml if "arbeidsovereenkomst" not in params["query"] else empty)

    monkeypatch.setattr(nl._http, "get", fake_get)
    res = asyncio.run(nl._search_wetten("Burgerlijk Wetboek Boek 7 arbeidsovereenkomst",
                                        current_only=True, limit=5, page=1))
    assert [h.id for h in res.items] == ["BWBR0005290"] and "arbeidsovereenkomst" in res.note


def test_date_sort_prefers_exact_phrase(monkeypatch):
    terms, fields = [], []

    async def fake_post(url, json=None, headers=None, **kw):
        terms.append(json["SearchTerms"][0]["Term"])
        fields.append(json["SearchTerms"][0]["Field"])
        return _R({"Results": [{"TitelEmphasis": "ECLI:NL:RBROT:2026:1",
                                "Titel": "Rechtbank Rotterdam, 12-06-2026, X"}], "ResultCount": 1})

    monkeypatch.setattr(nl._http, "post", fake_post)
    res = asyncio.run(nl._search_caselaw("ontslag dringende reden", field="alle", sort="uitspraak",
                                         limit=5, start=0, period=None))
    assert terms == ["ontslag AND dringende AND reden", '"ontslag dringende reden"'] and "exact phrase" in res.note
    assert fields[1] == "Samenvatting"  # summary phrase tried first, so passing mentions don't lead
