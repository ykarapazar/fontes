"""Offline tests for the legislation.gov.uk side of the UK adapter: search URL (no 301), exact-title
ranking, hit count, and provision annotations. Fixtures in tests/fixtures/gb were recorded live
(2026-11-11): the /all/data.feed search for "Legal Services Act" and CDPA 1988 s.9 data.xml."""
from pathlib import Path

import httpx
import pytest

from world_legal_mcp import _http
from world_legal_mcp.jurisdictions import gb

FIX = Path(__file__).parent / "fixtures" / "gb"


class Leg:
    """Mock legislation.gov.uk. /search/data.feed answers 301 as the real site does."""

    def __init__(self):
        self.calls: list[httpx.Request] = []

    def __call__(self, req: httpx.Request) -> httpx.Response:
        self.calls.append(req)
        path = req.url.path
        if path == "/search/data.feed":
            return httpx.Response(301, headers={"Location": "https://www.legislation.gov.uk/all/data.feed"})
        if path.endswith("/data.feed"):
            return httpx.Response(200, content=(FIX / "search_legal_services_act.feed").read_bytes())
        if path == "/ukpga/1988/48/section/9/data.xml":
            return httpx.Response(200, content=(FIX / "cdpa_section_9.xml").read_bytes())
        return httpx.Response(404)


@pytest.fixture
def leg(monkeypatch):
    mock = Leg()
    monkeypatch.setattr(_http, "_client", httpx.AsyncClient(transport=httpx.MockTransport(mock)))
    monkeypatch.setattr(_http, "_intervals", {})
    gb._xml_cache.clear()
    return mock


async def _search(query="Legal Services Act", **filters):
    return await gb.UnitedKingdom().search_legislation(query, limit=5, page=2, filters=filters)


@pytest.mark.parametrize("filters, path", [
    ({}, "/all/data.feed"),
    ({"doc_type": "ukpga"}, "/ukpga/data.feed"),
    ({"year": "2007"}, "/2007/data.feed"),
    ({"doc_type": "ukpga", "year": "2007"}, "/ukpga/2007/data.feed"),
])
async def test_search_calls_the_final_url(leg, filters, path):
    await _search(**filters)
    (req,) = leg.calls
    assert req.url.path == path
    params = dict(req.url.params)
    assert params["page"] == "2" and params["results-count"] == "5"
    assert params["title"] == "Legal Services Act"
    assert "type" not in params and "year" not in params


async def test_search_bad_doc_type(leg):
    with pytest.raises(gb.BadRequest):
        await _search(doc_type="../x")


async def test_search_exact_title_first_and_total(leg):
    res = await _search()
    ids = [h.id for h in res.items]
    # source order: asp/2025/8, asp/2010/16, ukpga/2007/29, ...; the exact short title goes first
    assert ids[0] == "ukpga/2007/29"
    assert ids[1:] == ["asp/2025/8", "asp/2010/16", "ukpga/1997/35", "ukpga/1990/41"]
    assert res.total == 87          # sum of the feed's per-type counts (77 + 5 + 3 + 2)


async def test_provision_inherited_annotations_are_trimmed(leg):
    p = await gb._get_provision("ukpga/1988/48", "9")
    assert p.provision == "section/9" and "unknown authorship" in p.text
    # the section's own amendments stay, in full and labelled as on the site
    assert "**F1** S. 9(2)(aa)(ab) substituted" in p.text
    assert "**F2** S. 9(2)(c) repealed" in p.text
    # the 18 Part-level extent/modification orders do not swamp the text
    assert "S.I. 1989/988" not in p.text and "Cayman Islands" not in p.text
    assert "18 more annotations" in p.text and "Part I" in p.text
    assert p.url in p.text
    assert len(p.text) < 4000


class Case:
    """Mock Find Case Law: empty Atom feed, 404 for any judgment."""

    def __init__(self):
        self.calls: list[httpx.Request] = []

    def __call__(self, req: httpx.Request) -> httpx.Response:
        self.calls.append(req)
        if req.url.path == "/atom.xml":
            return httpx.Response(200, content=b'<feed xmlns="http://www.w3.org/2005/Atom"></feed>')
        return httpx.Response(404)


@pytest.fixture
def case(monkeypatch):
    mock = Case()
    monkeypatch.setattr(_http, "_client", httpx.AsyncClient(transport=httpx.MockTransport(mock)))
    monkeypatch.setattr(_http, "_intervals", {})
    return mock


async def test_caselaw_date_range_and_relevance_default(case):
    res = await gb.UnitedKingdom().search_caselaw(
        "negligence", limit=5, page=1, filters={"date_from": "2022", "date_to": "2023-02"})
    params = dict(case.calls[0].url.params)
    assert params["order"] == "relevance"
    assert (params["from_date_0"], params["from_date_1"], params["from_date_2"]) == ("1", "1", "2022")
    assert (params["to_date_0"], params["to_date_1"], params["to_date_2"]) == ("28", "2", "2023")
    assert "2003 onward" in res.note and "relevance" in res.note


def _feed(*dates):
    ents = "".join(
        f'<entry><title>C{i}</title><published>{d}T00:00:00Z</published>'
        f'<tna:identifier xmlns:tna="https://caselaw.nationalarchives.gov.uk" type="ukncn" '
        f'slug="uksc/{d[:4]}/{i}">[{d[:4]}] UKSC {i}</tna:identifier></entry>'
        for i, d in enumerate(dates, 1))
    return f'<feed xmlns="http://www.w3.org/2005/Atom">{ents}</feed>'.encode()


async def test_caselaw_date_order_resorts_relevance_top(monkeypatch):
    calls = []

    def mock(req):
        calls.append(req)
        return httpx.Response(200, content=_feed("2019-01-01", "2026-01-01", "2024-01-01"))
    monkeypatch.setattr(_http, "_client", httpx.AsyncClient(transport=httpx.MockTransport(mock)))
    monkeypatch.setattr(_http, "_intervals", {})
    res = await gb.UnitedKingdom().search_caselaw("x", limit=2, page=1, filters={"order": "-date"})
    assert calls[0].url.params["order"] == "relevance" and calls[0].url.params["per_page"] == "50"
    assert [h.date for h in res.items] == ["2026-01-01", "2024-01-01"]
    assert "re-sorted by date" in res.note


async def test_caselaw_three_words_try_subphrase_before_loose(case):
    await gb.UnitedKingdom().search_caselaw("unfair dismissal reasonableness", limit=5, page=1, filters={})
    qs = [c.url.params["query"] for c in case.calls]
    assert qs == ['"unfair dismissal reasonableness"', '"unfair dismissal" AND reasonableness',
                  'unfair AND "dismissal reasonableness"', "unfair dismissal reasonableness"]


async def test_caselaw_multiword_query_is_phrase_then_loose_fallback(case):
    res = await gb.UnitedKingdom().search_caselaw(
        "unfair dismissal", limit=5, page=1, filters={"order": "-date"})
    assert case.calls[0].url.params["query"] == '"unfair dismissal"'
    assert case.calls[1].url.params["query"] == "unfair dismissal"   # empty feed: loose fallback
    assert "loosely" in res.note
    case.calls.clear()
    await gb.UnitedKingdom().search_caselaw('"a b" c', limit=5, page=1, filters={})
    assert len(case.calls) == 1 and case.calls[0].url.params["query"] == '"a b" c'


async def test_caselaw_bad_date(case):
    with pytest.raises(gb.BadRequest):
        await gb.UnitedKingdom().search_caselaw("x", limit=5, page=1, filters={"date_from": "2022-13"})


async def test_get_decision_not_found_is_not_contradictory(case):
    with pytest.raises(gb.NotFound) as e:
        await gb.UnitedKingdom().get_decision("[2007] UKHL 17")
    msg = str(e.value)
    assert "UKHL" in msg and "not in Find Case Law" in msg and "resolved" not in msg


def test_search_note_does_not_claim_all_words_match():
    import asyncio
    from unittest.mock import AsyncMock, patch
    from world_legal_mcp.jurisdictions import gb

    class R:
        status_code = 200
        content = b'<feed xmlns="http://www.w3.org/2005/Atom"/>'

    with patch.object(gb, "get", AsyncMock(return_value=R())):
        res = asyncio.run(gb._search_caselaw("x", court=None, party=None, judge=None,
                                             order="-date", limit=5, page_no=1))
    assert "all words must match" not in res.note
    assert "loosely" in res.note


def test_eu_retained_body_is_rendered():
    """Retained EU law (eur/...) holds its text under <EURetained>, not Primary/Secondary."""
    from lxml import etree
    ns = "http://www.legislation.gov.uk/namespaces/legislation"
    root = etree.fromstring(
        f'<Legislation xmlns="{ns}"><EURetained><EUBody><EUChapter><P1group><Title>Lawfulness</Title>'
        '<P1><Pnumber>Article 6</Pnumber><P1para><P2><Pnumber>1</Pnumber><P2para>'
        '<Text>Processing shall be lawful only if consent is given.</Text></P2para></P2></P1para></P1>'
        '</P1group></EUChapter></EUBody></EURetained></Legislation>')
    out = gb._render_document(root)
    assert "Processing shall be lawful only if consent is given." in out and "Lawfulness" in out
