"""US state courts (CourtListener): offline checks with the API faked."""
import pytest

from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions import us_states as U


def _row(n):
    return {"cluster_id": n, "caseName": f"Case {n}", "court": "Texas Supreme Court",
            "dateFiled": "2024-01-02", "docketNumber": f"24-{n}", "citation": [],
            "absolute_url": f"/opinion/{n}/case-{n}/", "opinions": []}


@pytest.fixture
def fake(monkeypatch):
    """20 hits per call over 45 results, cursor paging like the real API."""
    calls = []

    async def api(path, params):
        calls.append(dict(params))
        n = int(params.get("cursor") or 0)
        rows = [_row(i) for i in range(n * 20, min(n * 20 + 20, 45))]
        nxt = f"{U.API}/search/?cursor={n + 1}" if n * 20 + 20 < 45 else None
        return {"count": 45, "next": nxt, "results": rows}
    monkeypatch.setenv(U.ENV, "t")
    monkeypatch.setattr(U, "_api", api)
    U._cursors.clear()
    return calls


def test_off_without_token(monkeypatch):
    monkeypatch.delenv(U.ENV, raising=False)
    j = U.UnitedStatesStates()
    assert not j.supports("search_caselaw") and "Inactive" in j.notes


@pytest.mark.parametrize("v,code", [("TX", "TX"), ("tx", "TX"), ("Texas", "TX"),
                                    ("new  york", "NY"), ("West Virginia", "WV"), ("dc", "DC")])
def test_state_names(v, code):
    assert U._state(v) == code


async def test_state_checked_default_all(fake):
    j = U.UnitedStatesStates()
    with pytest.raises(BadRequest):
        await j.search_caselaw("duty of care", limit=5, page=1, filters={"state": "Ontario"})
    assert fake == []
    await j.search_caselaw("duty of care", limit=5, page=1, filters={})   # no state: all of them
    assert fake[-1]["court"].split() == " ".join(U._COURTS.values()).split()


async def test_paging_slices_across_cursor_pages(fake):
    j = U.UnitedStatesStates()
    r = await j.search_caselaw("duty of care", limit=15, page=2, filters={"state": "Texas"})
    assert [h.id for h in r.items] == [str(i) for i in range(15, 30)] and r.total == 45
    assert all(c["court"] == U._COURTS["TX"] for c in fake)
    r = await j.search_caselaw("duty of care", limit=10, page=5, filters={"state": "TX"})
    assert [h.id for h in r.items] == [str(i) for i in range(40, 45)]


async def test_year_filters_and_cap(fake):
    j = U.UnitedStatesStates()
    await j.search_caselaw("x", limit=5, page=1, filters={"state": "FL", "year_from": "2020",
                                                          "year_to": "2024"})
    assert fake[-1]["filed_after"] == "2020-01-01" and fake[-1]["filed_before"] == "2024-12-31"
    with pytest.raises(BadRequest):
        await j.search_caselaw("x", limit=50, page=3, filters={"state": "FL"})


async def test_decision_id_forms(monkeypatch):
    monkeypatch.setenv(U.ENV, "t")
    seen = []

    async def api(path, params):
        seen.append((path, params))
        if path == "search/":
            return {"results": [_row(10348460)]}
        return {"results": [{"type": "010combined", "author_str": "", "per_curiam": False,
                             "html_with_citations": "<p>Held: affirmed.</p>", "download_url": "https://c/x.pdf"}]}
    monkeypatch.setattr(U, "_api", api)
    j = U.UnitedStatesStates()
    for ref in ("10348460", "https://www.courtlistener.com/opinion/10348460/binion/"):
        d = await j.get_decision(ref)
        assert d.id == "10348460" and "affirmed" in d.text and d.metadata["Court's copy"] == "https://c/x.pdf"
    with pytest.raises(BadRequest):
        await j.get_decision("USREPORTS-347-483")


async def test_lead_opinion_before_dissent(monkeypatch):
    monkeypatch.setenv(U.ENV, "t")

    async def api(path, params):
        if path == "search/":
            return {"results": [_row(1)]}
        return {"results": [{"type": "040dissent", "author_str": "B", "html_with_citations": "<p>No.</p>"},
                            {"type": "020lead", "author_str": "A", "html_with_citations": "<p>Yes.</p>"}]}
    monkeypatch.setattr(U, "_api", api)
    d = await U.UnitedStatesStates().get_decision("1")
    assert d.text.index("Lead opinion, A") < d.text.index("Dissent, B")


def test_every_answer_discloses_the_source():
    s = U.SOURCE
    assert not s.official and "Free Law Project" in s.warning and "not the courts' own" in s.warning
    assert "endorse" in s.warning
