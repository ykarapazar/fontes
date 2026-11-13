import asyncio

import pytest

from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions import no

ENTRIES = [
    ("avgjorelser-2024/hoyesterett---sivil/HR-2024-708-A", "2024", "hoyesterett---sivil", "HR-2024-708-A"),
    ("avgjorelser-2023/hoyesterett---sivil/HR-2023-9-A", "2023", "hoyesterett---sivil", "HR-2023-9-A"),
    ("avgjorelser-2021/hoyesterett---sivil/x", "2021", "hoyesterett---sivil", "oppsigelse"),
    ("avgjorelser-2024/hoyesteretts-ankeutvalg---sivil/2024-1218-U", "2024", "hoyesteretts-ankeutvalg---sivil", "2024-1218-U"),
]


def _search(monkeypatch, query="", **filters):
    async def entries():
        return ENTRIES

    async def page(path):
        return {"name": "", "body": "", "date": "", "hr": "", "case_number": "", "url": path, "title": path,
                "intro": "", "meta": {}, "pdf": ""}
    monkeypatch.setattr(no, "_entries", entries)
    monkeypatch.setattr(no, "_page", page)
    monkeypatch.setattr(no, "_title", lambda p: p["title"])
    return asyncio.run(no.Norway().search_caselaw(query, limit=10, page=1, filters=filters))


def test_year_range(monkeypatch):
    assert _search(monkeypatch, year="2023-2024").total == 3
    assert _search(monkeypatch, year=[2023, 2024]).total == 3
    assert _search(monkeypatch, year=2024).total == 2


def test_backwards_range(monkeypatch):
    with pytest.raises(BadRequest):
        _search(monkeypatch, year="2024-2023")


def test_empty_topic_note_explains(monkeypatch):
    r = _search(monkeypatch, "oppsigelse arbeidstaker", year="2024")
    assert r.total == 0 and "robots.txt" in r.note


def test_bare_number_slug_resolves(monkeypatch):
    async def entries():
        return ENTRIES
    monkeypatch.setattr(no, "_entries", entries)
    assert asyncio.run(no._resolve("HR-2024-1218-U")).endswith("2024-1218-U")


def test_hr_number_of_slugged_page_resolves(monkeypatch):
    entries = [("avgjorelser-2024/hoyesteretts-ankeutvalg---sivil/opphevelse-x", "2024", "c", "opphevelse-x")]

    async def ents():
        return entries

    async def page(path):
        return {"hr": "HR-2024-729-U"}
    monkeypatch.setattr(no, "_entries", ents)
    monkeypatch.setattr(no, "_page", page)
    assert asyncio.run(no._resolve("HR-2024-729-U")) == entries[0][0]


def test_topic_matches_titles_of_number_slugs(monkeypatch):
    async def ents():
        return ENTRIES[:2]

    async def page(path):
        t = "Oppsigelse var gyldig" if "708" in path else "Annet"
        return {"name": t, "body": "", "date": "", "hr": "", "case_number": "", "url": path, "intro": "",
                "meta": {}, "pdf": ""}
    monkeypatch.setattr(no, "_entries", ents)
    monkeypatch.setattr(no, "_page", page)
    r = asyncio.run(no.Norway().search_caselaw("oppsigelse", limit=10, page=1, filters={"year": 2024}))
    assert r.total == 1


def test_english_query_note_is_plain(monkeypatch):
    r = _search(monkeypatch, "employee dismissal")
    assert r.total == 0
    assert "Norwegian" in r.note and "oppsigelse" in r.note and "120" not in r.note and "slug" not in r.note


def test_partial_count_is_flagged(monkeypatch):
    r = _search(monkeypatch, "oppsigelse", area="sivil")
    assert r.total == 1 and "partial" in r.note


def test_legislation_gap_gives_lovdata_url():
    g = " ".join(no.Norway.gaps)
    assert "https://lovdata.no/dokument/NL/lov/" in g and "2005-05-20-28" in g


def test_title_match_count_is_flagged(monkeypatch):
    async def ents():
        return ENTRIES[:2]

    async def page(path):
        return {"name": "Oppsigelse", "body": "", "date": "", "hr": "", "case_number": "", "url": path,
                "intro": "", "meta": {}, "pdf": ""}
    monkeypatch.setattr(no, "_entries", ents)
    monkeypatch.setattr(no, "_page", page)
    r = asyncio.run(no.Norway().search_caselaw("oppsigelse", limit=10, page=1, filters={"year": 2024}))
    assert "not searched" in r.note
