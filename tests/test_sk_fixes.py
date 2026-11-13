import asyncio

from world_legal_mcp.jurisdictions import sk


def _install(monkeypatch, replies, calls):
    async def fake_json(url, what, **kw):
        p = dict(kw["params"])
        calls.append(p)
        if "getDecision" in p:
            return {"ecli": "E" + p["id"], "cislo": "1Cdo/1/2020", "merito": "m", "datum": ""}
        return replies(p)
    monkeypatch.setattr(sk, "_json", fake_json)


def _cls():
    return next(v for v in vars(sk).values()
                if isinstance(v, type) and issubclass(v, sk.Jurisdiction) and v is not sk.Jurisdiction)


def test_get_decision_by_file_number(monkeypatch):
    calls = []
    _install(monkeypatch, lambda p: ["5", "9"] if p.get("nazov") == "3Cdo/128/2018" else [], calls)
    d = asyncio.run(_cls()().get_decision("3Cdo/128/2018"))
    assert d.id == "E9"


def test_subject_hits_ranked_first(monkeypatch):
    calls = []
    _install(monkeypatch,
             lambda p: ["1", "2", "3"] if "art_obsah" in p else ["1"], calls)
    res = asyncio.run(_cls()().search_caselaw("nájom", limit=3))
    assert [h.id for h in res.items] == ["E1", "E3", "E2"]


def test_subject_hits_outside_text_match_and_suffix_phrases(monkeypatch):
    calls = []

    def replies(p):
        if "art_obsah" in p:
            return ["1"]
        return {"výpoveď z nájmu bytu": [], "z nájmu bytu": ["4"], "nájmu bytu": ["4", "7"]}[p["art_merito"]]
    _install(monkeypatch, replies, calls)
    res = asyncio.run(_cls()().search_caselaw("výpoveď z nájmu bytu", limit=10))
    assert [h.id for h in res.items] == ["E4", "E7", "E1"]


def test_note_says_not_date_sorted(monkeypatch):
    calls = []
    _install(monkeypatch, lambda p: ["5", "9"], calls)
    r = asyncio.run(_cls()().search_caselaw("náhrada škody"))
    assert "NOT by decision date" in r.note


def test_multiword_falls_back_to_all_words(monkeypatch):
    calls = []

    def replies(p):
        if p.get("art_obsah") == "výpoveď zamestnanec":
            return []
        return {"výpoveď": ["1", "2", "3"], "zamestnanec": ["2", "3", "9"]}.get(p.get("art_obsah"), [])
    _install(monkeypatch, replies, calls)
    res = asyncio.run(_cls()().search_caselaw("výpoveď zamestnanec", limit=10))
    assert [h.id for h in res.items] == ["E3", "E2"]
    assert "all of the words" in res.note


def test_multiword_subject_word_ranked_first_and_note_says_rest_is_weak(monkeypatch):
    calls = []

    def replies(p):
        if p.get("art_merito") == "výpov":
            return ["2"]
        if p.get("art_merito"):
            return []
        if p.get("art_obsah") == "výpoveď zamestnanec":
            return []
        return {"výpoveď": ["1", "2", "3"], "zamestnanec": ["1", "2", "3"]}.get(p.get("art_obsah"), [])
    _install(monkeypatch, replies, calls)
    res = asyncio.run(_cls()().search_caselaw("výpoveď zamestnanec", limit=10))
    assert [h.id for h in res.items] == ["E2", "E3", "E1"]
    assert "Only the first 1 have a query word in the subject line" in res.note
