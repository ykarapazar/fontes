import pytest

from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions import gr


def test_stems_keep_lease_apart_from_employee():
    stem = gr._stems("μίσθωση")[0]
    assert stem in gr._fold("Μίσθωση εργασίας")
    assert stem not in gr._fold("Αποδοχές μισθωτού")


async def test_year_range_rejected():
    with pytest.raises(BadRequest, match="one year"):
        await gr.Greece().search_caselaw("2022-2024", limit=3, page=1, filters={})


async def test_capped_year_note(monkeypatch):
    async def fake(*a, **k):
        return [gr.DecisionHit(id="x", title="t", court="c", case_number="1/2022")] * 3000
    monkeypatch.setattr(gr, "_ap_search", fake)
    r = await gr.Greece().search_caselaw("2022", limit=3, page=1, filters={"chamber": "civil"})
    assert "may be a cap" in r.note


async def test_capped_year_combines_chambers(monkeypatch):
    async def fake(number, year, f, op_number="1"):
        ch = f.get("chamber", "all")
        n = {"all": 3000, "civil": 2127, "criminal": 1412}.get(ch, 0)
        return [gr.DecisionHit(id=f"{ch}{i}", title="t", court="c", case_number=f"{i}/2022") for i in range(n)]
    monkeypatch.setattr(gr, "_ap_search", fake)
    r = await gr.Greece().search_caselaw("2022", limit=3, page=1, filters={})
    assert r.total == 3000 + 2127 + 1412


async def test_lease_note_says_no_civil_heading(monkeypatch):
    async def subj(q):
        return [], ["Μίσθωση εργασίας", "Μίσθωση έργου"]
    monkeypatch.setattr(gr, "_ap_subject_hits", subj)
    r = await gr.Greece().search_caselaw("μίσθωση", limit=3, page=1, filters={})
    assert "no heading for the civil lease" in r.note


async def test_multiword_falls_back_to_most_specific_word(monkeypatch):
    async def subs():
        return [("1", "Αγωγή αναγνωριστική"), ("2", "Αγωγή αρνητική"), ("3", "Αποζημίωση")]
    async def rows(url, **k):
        return ""
    monkeypatch.setattr(gr, "_ap_subjects", subs)
    monkeypatch.setattr(gr, "_ap_get", rows)
    gr._lists.clear()
    hits, names = await gr._ap_subject_hits("αγωγή αποζημίωση")
    assert names == ["Αποζημίωση"]
