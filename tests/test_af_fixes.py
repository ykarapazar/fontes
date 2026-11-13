"""Offline tests for the Afghanistan adapter: multi-word search fallback, damaged PDFs, old-issue hint."""
import asyncio

import pytest

from world_legal_mcp import _http
from world_legal_mcp.base import SourceError
from world_legal_mcp.jurisdictions import af


def _row(serial, rec, title):
    return {"serial": serial, "rec": rec, "title": title, "date": "", "status": "", "notes": "", "btn": "b"}


def test_multiword_falls_back_to_all_words(monkeypatch):
    rows = [_row("1291", "5549", "موافقتنامه میان دولت و دولت امارات متحده عربی"),
            _row("1", "2", "موافقتنامه دیگر")]
    queries = []

    async def fake_search(q, lang):
        queries.append(q)
        yield ([] if " " in q else rows), None, "u"

    monkeypatch.setattr(af, "_search", fake_search)
    monkeypatch.setattr(af, "_has_next", lambda d: False)
    res = asyncio.run(af.Afghanistan().search_legislation("موافقتنامه امارات"))
    assert [h.id for h in res.items] == ["1291-5549"]
    assert queries == ["موافقتنامه امارات", "موافقتنامه", "امارات"]
    assert "exact phrase" in res.note
    assert "usually unreadable" in af._hit(rows[0], "u").snippet


def test_tatweel_and_spelling_variants_are_found(monkeypatch):
    rows = [_row("1409", "15587", "موافقتنامه میان دولت و امارت مـتحده عربی درمــورد خدمـات هوایی")]

    async def fake_search(q, lang):
        yield ([] if q == "امارات متحده عربی" else rows if q == "عربی" else []), None, "u"

    monkeypatch.setattr(af, "_search", fake_search)
    monkeypatch.setattr(af, "_has_next", lambda d: False)
    res = asyncio.run(af.Afghanistan().search_legislation("امارات متحده عربی"))
    assert [h.id for h in res.items] == ["1409-15587"]
    assert "Contents calls will usually fail" in af._hit(rows[0], "u").snippet


def test_garbled_pdf_without_headings_points_to_text(monkeypatch):
    d = {"row": _row("1450", "16575", "t"), "id": "1450-16575", "url": "u", "readable": True,
         "scan": False, "text": "هادۀ اول:\nمتن"}

    async def fake_doc(i):
        return d

    monkeypatch.setattr(af, "_doc", fake_doc)
    for call in (af.Afghanistan().get_legislation_toc("1450-16575"),
                 af.Afghanistan().get_legislation_provision("1450-16575", "1")):
        with pytest.raises(af.NotFound, match="get_legislation_text"):
            asyncio.run(call)


def test_damaged_pdf_is_explained(monkeypatch):
    async def fake_search(q, lang):
        yield [_row("645", "1970", "t")], lhtml_stub(), "u"

    def lhtml_stub():
        from lxml import html
        return html.fromstring("<form></form>")

    async def fake_download(url, data):
        return b"%PDF"

    def boom(pdf):
        raise ValueError("Invalid object in /Pages")

    monkeypatch.setattr(af, "_search", fake_search)
    monkeypatch.setattr(af, "_download", fake_download)
    monkeypatch.setattr(_http, "pdf_text", boom)
    af._doc_cache.clear()
    with pytest.raises(SourceError, match="damaged or unreadable"):
        asyncio.run(af._doc("645-1970"))


def test_single_word_retries_related_form(monkeypatch):
    rows = [_row("1450", "16575", "قانون بخش صرافان و خدمات پولی")]
    queries = []

    async def fake_search(q, lang):
        queries.append(q)
        yield (rows if q == "صرافان" else []), None, "u"

    monkeypatch.setattr(af, "_search", fake_search)
    monkeypatch.setattr(af, "_has_next", lambda d: False)
    res = asyncio.run(af.Afghanistan().search_legislation("صرافی"))
    assert [h.id for h in res.items] == ["1450-16575"]
    assert queries == ["صرافی", "صرافان"]
    assert "related form" in res.note
    assert "Contents call above" not in af._hit(_row("1291", "1", "x"), "u").snippet


def test_old_gazette_hit_has_no_contents_offer():
    assert af._hit(_row("1291", "5549", "t"), "u").has_toc is False
    assert af._hit(_row("1450", "16575", "t"), "u").has_toc is False


def test_garbled_text_gets_warning(monkeypatch):
    d = {"row": _row("1450", "16575", "t"), "id": "1450-16575", "url": "u", "readable": True,
         "scan": False, "text": "هادۀ اول: قاًوى\\nمتن"}

    async def fake_doc(i):
        return d

    monkeypatch.setattr(af, "_doc", fake_doc)
    r = asyncio.run(af.Afghanistan().get_legislation_text("1450-16575"))
    assert "garbled" in r.metadata["Warning"]


def test_hits_offer_no_contents_line():
    h = af._hit(_row("1450", "16575", "قانون صرافی"), "u")
    assert h.has_toc is False
    assert "get_legislation_text" in h.snippet
