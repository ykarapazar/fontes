import asyncio

import pytest

from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions import bj
from world_legal_mcp.models import DecisionHit


def _hit(i):
    return DecisionHit(id=i, title=i, court="c", date="", case_number=i, snippet="", url="u")


def _search(monkeypatch, year, totals, page=1, limit=10, query=""):
    calls = []

    async def fake(self, base, params, start, lim):
        y = int(base.rsplit("/", 1)[-1]) if not params else 0
        calls.append(y)
        n = totals.get(y, 0)
        return [_hit(f"{y}-{k}") for k in range(start, min(n, start + lim))], n
    monkeypatch.setattr(bj.Benin, "_cc_window", fake)
    res = asyncio.run(bj.Benin().search_caselaw(query, limit=limit, page=page,
                                                filters={"type": "DCC", "year": year} if year else {}))
    return res, calls


def test_year_range_newest_first_and_spans_years(monkeypatch):
    res, _ = _search(monkeypatch, "2024-2026", {2026: 3, 2025: 5, 2024: 4}, limit=6)
    assert [h.id for h in res.items] == ["2026-0", "2026-1", "2026-2", "2025-0", "2025-1", "2025-2"]


def test_year_range_page_two_and_total(monkeypatch):
    res, _ = _search(monkeypatch, "2024-2026", {2026: 3, 2025: 5, 2024: 4}, page=2, limit=6)
    assert [h.id for h in res.items][:2] == ["2025-3", "2025-4"] and res.total == 12


def test_bad_year_range(monkeypatch):
    with pytest.raises(BadRequest):
        _search(monkeypatch, "2026-2022", {})


def test_subject_query_says_not_possible(monkeypatch):
    from world_legal_mcp.base import NotFound
    with pytest.raises(NotFound, match="not possible"):
        _search(monkeypatch, None, {}, query="constitutionnalité loi")


def test_year_range_total_counts_unfetched_years(monkeypatch):
    res, _ = _search(monkeypatch, "2024-2026", {2026: 30, 2025: 5, 2024: 4}, limit=10)
    assert len(res.items) == 10 and res.total == 39


def test_scanned_decision_returns_register_details(monkeypatch):
    async def page(did):
        return {"head": "DCC25-293 du 12 décembre 2025", "pdf": "https://x/f.pdf",
                "meta": {"Objet de la requête": "Recours X"}}

    async def pdf(url, source):
        return ""
    monkeypatch.setattr(bj, "_cc_decision_page", page)
    monkeypatch.setattr(bj, "_pdf", pdf)
    d = asyncio.run(bj.Benin().get_decision("DCC25-293"))
    assert "image-only scan" in d.text and "https://x/f.pdf" in d.text and d.summary == "Recours X"


def test_range_note_explains_total(monkeypatch):
    res, _ = _search(monkeypatch, "2024-2026", {2026: 3})
    assert "sum of the per-year counts" in res.note


def test_missing_article_lists_labels_found(monkeypatch):
    from world_legal_mcp.base import NotFound

    async def law(lid):
        return {"title": "t", "url": "u", "text": "Article 2 : a\n\nArticle 3 : b"}
    monkeypatch.setattr(bj, "_sgg_law", law)
    with pytest.raises(NotFound, match="found in the text layer: 2, 3"):
        asyncio.run(bj.Benin().get_legislation_provision("loi-89-003", "1"))


def test_ocr_unreliable_labels():
    assert bj._ocr_unreliable(["166", "2"]) and bj._ocr_unreliable(["2", "3"])
    assert not bj._ocr_unreliable(["1", "2", "3"]) and not bj._ocr_unreliable([])


def test_provision_not_found_warns_on_garbled_ocr(monkeypatch):
    from world_legal_mcp.base import NotFound

    async def fake(lid):
        return {"title": "t", "url": "u", "text": "Article 166 - x\n\nArticle 2 - y".replace("\n\n", "\n\n")}
    monkeypatch.setattr(bj, "_sgg_law", fake)
    with pytest.raises(NotFound, match="garbled"):
        asyncio.run(bj.Benin().get_legislation_provision("loi-1989-003", "1"))
    toc = asyncio.run(bj.Benin().get_legislation_toc("loi-1989-003"))
    assert "garbled" in toc.note
