import asyncio

import lxml.html

from world_legal_mcp.jurisdictions import ie


class _R:
    status_code = 200

    def __init__(self, data):
        self._d = data

    def json(self):
        return {"response": self._d}


def test_search_retries_as_prefix_and_hints(monkeypatch):
    seen = []

    async def fake_get(url, params=None, **kw):
        q = dict(params)["q"]
        seen.append(q)
        if q.endswith("*"):
            return _R({"numFound": 1, "docs": [{"type": "act", "year": "1977", "act": "10",
                                                "title": "Unfair Dismissals Act, 1977"}]})
        return _R({"numFound": 0, "docs": []})

    monkeypatch.setattr(ie, "get", fake_get)
    res = asyncio.run(ie.Ireland().search_legislation("unfair dismissal"))
    assert seen == ["unfair dismissal", "unfair* dismissal*"]
    assert res.items[0].id == "1977/act/10" and "beginnings" in res.note

    async def none(url, params=None, **kw):
        return _R({"numFound": 0, "docs": []})

    monkeypatch.setattr(ie, "get", none)
    res = asyncio.run(ie.Ireland().search_legislation("GDPR"))
    assert not res.items and "title words" in res.note


def test_revised_annotations_come_last(monkeypatch):
    html = ('<html><head><title>X | Y</title></head><body><div class="cell medium-9 ">'
            '<div class="frontmatter"><p>Preamble</p><div class="annotations"><p>ANNOT</p></div></div>'
            '<div class="body"><section class="sect" id="SEC1"><div class="number">1</div>'
            '<p>Operative</p></section></div></div></body></html>')

    class R:
        status_code = 200
        content = html.encode()

    async def fake_get(url, **kw):
        return R()

    monkeypatch.setattr(ie, "get", fake_get)
    doc = asyncio.run(ie._load_revised("2000/act/1", "2000", "1"))
    out = "\n".join(ie._render(p) for p in doc.parts)
    assert out.index("Operative") < out.index("ANNOT")


def test_prefix_search_ranks_matching_act_first(monkeypatch):
    async def fake_get(url, params=None, **kw):
        if dict(params)["q"].endswith("*"):
            return _R({"numFound": 2, "docs": [
                {"type": "si", "year": "1994", "leg": "279", "title": "S.I. No. 279/1994 - Circuit Court Rules"},
                {"type": "act", "year": "1977", "act": "10", "title": "Unfair Dismissals Act, 1977"}]})
        return _R({"numFound": 0, "docs": []})

    monkeypatch.setattr(ie, "get", fake_get)
    res = asyncio.run(ie.Ireland().search_legislation("unfair dismissal"))
    assert [i.id for i in res.items] == ["1977/act/10", "1994/si/279"]


def test_text_dedups_title_block_and_moves_section_annotations(monkeypatch):
    html = ('<html><head><title>X | Y</title></head><body><div class="cell medium-9 ">'
            '<div class="frontmatter"><p>Intro</p><p>Number 1 of 2000</p><p>TITLEONE</p>'
            '<p>ARRANGEMENT OF SECTIONS</p><p>Number 1 of 2000</p><p>TITLETWO</p></div>'
            '<div class="body"><section class="sect" id="SEC1"><div class="number">1</div>'
            '<p>Operative1</p><div class="annotations"><p>ANNOT1</p></div></section>'
            '<section class="sect" id="SEC2"><div class="number">2</div><p>Operative2</p></section>'
            '</div></div></body></html>')

    class R:
        status_code = 200
        content = html.encode()

    async def fake_get(url, **kw):
        return R()

    monkeypatch.setattr(ie, "get", fake_get)
    ie._cache.clear()
    out = asyncio.run(ie.Ireland().get_legislation_text("2000/act/1")).text
    ie._cache.clear()
    assert "TITLEONE" not in out and "ARRANGEMENT" not in out and out.count("TITLETWO") == 1
    assert out.index("Operative2") < out.index("ANNOT1")


def test_revised_note_separates_consolidation_date_from_lrc_banner():
    html = ("<html><head><title>X Act | LRC</title></head><body><div class='cell medium-9 '>"
            "<div class='body'><p>Updated to 3 July 2023</p>"
            "<p>as of 3 November 2026, this Act is up to date with all changes known to be in force.</p>"
            "</div></div></body></html>").encode()

    class R:
        status_code = 200
        content = html

    async def fake_get(url, **kw):
        return R()

    import pytest
    mp = pytest.MonkeyPatch()
    mp.setattr(ie, "get", fake_get)
    try:
        doc = asyncio.run(ie._load_revised("2000/act/1", "2000", "1"))
    finally:
        mp.undo()
    assert "reflects the law as updated to 3 July 2023" in doc.note
    assert "later amendments are not incorporated" in doc.note
    assert "LRC's own statement, not verified" in doc.note


def test_notes_point_to_wrc_for_employment_decisions():
    assert "workplacerelations.ie" in ie.Ireland.notes
