import asyncio

from world_legal_mcp.jurisdictions import de


def test_az_regex():
    assert de._AZ_RE.match("IX R 16/25") and de._AZ_RE.match("VI B 3/24")
    assert not de._AZ_RE.match("Mietminderung Wohnraum")


def test_unavailable_court_message():
    try:
        asyncio.run(de.Germany()._bfh_search("x", limit=3, page=1, filters={"court": "BGH"}))
    except Exception as e:
        assert "not available in this setup" in str(e) and "OLG" in str(e)
    else:
        raise AssertionError("expected BadRequest")


def test_compound_law_name(monkeypatch):
    toc = [("lksg", "Gesetz über die unternehmerischen Sorgfaltspflichten zur Vermeidung von "
                     "Menschenrechtsverletzungen in Lieferketten"),
           ("bgb", "Bürgerliches Gesetzbuch")]
    monkeypatch.setattr(de, "_gii_toc", toc)
    r = asyncio.run(de.Germany().search_legislation("Lieferkettensorgfaltspflichtengesetz",
                                                    limit=5, page=1, filters={}))
    assert [h.id for h in r.items] == ["lksg"]


def test_non_tax_query_returns_empty_with_note():
    for q in ("Kündigung Arbeitsverhältnis", "Oberlandesgericht Urteil Mietvertrag"):
        r = asyncio.run(de.Germany()._bfh_search(q, limit=5, page=1, filters={}))
        assert r.items == [] and r.total == 0
        assert "nothing was searched" in r.note and "source pages" not in r.note


def test_tax_query_not_blocked():
    assert not de._NON_BFH_RE.search("Steuer Gewinnermittlung")
    assert not de._NON_BFH_RE.search("Lohnsteuer Arbeitnehmer Reisekosten")


def test_bfh_note_says_not_relevance_ranked_and_hides_internal_setting(monkeypatch):
    import lxml.html

    async def fake(params):
        return lxml.html.fromstring("<html><body></body></html>")
    monkeypatch.setattr(de, "_bfh_page", fake)
    r = asyncio.run(de.Germany()._bfh_search("Gewinnermittlung", limit=5, page=1, filters={}))
    assert "NOT by relevance" in r.note and "WLM_PERMITTED" not in r.note
    assert "double quotes" in r.note
