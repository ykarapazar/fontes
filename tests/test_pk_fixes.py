import asyncio
import types

from world_legal_mcp import _http
from world_legal_mcp.jurisdictions import pk

LAW = """THE TEST ACT, 2016
CONTENTS
1. Short title
2. Definitions
2A. Authority
2B. Removal of members
3. Offences
THE TEST ACT, 2016
1. Short title.__ This Act.
2. Definitions.__ In this Act.
(2A) Authority.__ There is an Authority.
(1) The Authority shall consist.
(2B) Removal of members.__ The Government may remove.
(2) In case of vacancy.
3. Offences.__ Whoever offends.
"""


def test_amended_in_sections_found():
    _, _, starts = pk._split(LAW)
    assert [lab for lab, _ in starts] == ["1", "2", "2A", "2B", "3"]


def test_categories_include_general():
    assert pk.CATEGORIES["23"] == "General Laws"


def _page(titles):
    items = "".join(
        f"<div class='accordion-section'><div class='accordion-section-title'>"
        f"<a href='https://pakistancode.gov.pk/english/UY2FqaJw1-apaUY2Fqa-t{i}=-sg-jjjjjjjjjjjjj'>{t}</a></div>"
        f"<div class='accordion-section-content'>General Laws | </div></div>"
        for i, t in enumerate(titles))
    return f"<html><body><div id='all_laws'>{items}</div></body></html>"


def test_long_title_falls_back_to_shorter_phrase(monkeypatch):
    pk._search_cache.clear()
    seen = []

    async def fake_get(url, params=None, **kw):
        seen.append(params["title"])
        full = params["title"] == "Constitution of the Islamic"
        return types.SimpleNamespace(status_code=200, text=_page(
            ["Constitution of the Islamic Republic of Pakistan"] if full else []))

    monkeypatch.setattr(_http, "get", fake_get)
    res = asyncio.run(pk.Pakistan().search_legislation("Constitution of the Islamic Republic of Pakistan"))
    assert [h.title for h in res.items] == ["Constitution of the Islamic Republic of Pakistan"]
    assert len(seen) > 1
    pk._search_cache.clear()


def test_parties_note_says_keyword_unused(monkeypatch):
    pk._search_cache.clear()

    async def fake_post(url, **kw):
        return types.SimpleNamespace(status_code=200, json=lambda: {"d": "[]"})

    monkeypatch.setattr(_http, "post", fake_post)
    res = asyncio.run(pk.Pakistan().search_caselaw("xyzzyqqzz", filters={"parties": "Federation of Pakistan"}))
    assert "NOT applied" in res.note
    pk._search_cache.clear()


def test_caselaw_multiword_falls_back_to_shorter_phrase(monkeypatch):
    pk._search_cache.clear()
    pk._shortened.clear()
    seen = []

    async def fake_post(url, content=None, headers=None, **kw):
        import json as _j
        kw_ = _j.loads(content)["PKYWRD"]
        seen.append(kw_)
        return types.SimpleNamespace(status_code=200, json=lambda: {"d": "[]"})

    monkeypatch.setattr(_http, "post", fake_post)
    monkeypatch.setattr(pk, "_ihc_rows", lambda payload: [object()] if seen[-1] == "fundamental rights" else [])
    res = asyncio.run(pk.Pakistan().search_caselaw("fundamental rights Article 199"))
    assert seen == ["fundamental rights Article 199", "fundamental rights Article", "fundamental rights"]
    assert "'fundamental rights' only" in res.note
    pk._search_cache.clear()
    pk._shortened.clear()


def test_category_empty_retries_without_category(monkeypatch):
    pk._search_cache.clear()
    seen = []

    async def fake_get(url, params=None, **kw):
        seen.append(params["cat"])
        return types.SimpleNamespace(status_code=200, text=_page([] if params["cat"] else ["Pakistan Penal Code"]))

    monkeypatch.setattr(_http, "get", fake_get)
    res = asyncio.run(pk.Pakistan().search_legislation("Penal Code", filters={"category": "1"}))
    assert [h.title for h in res.items] == ["Pakistan Penal Code"]
    assert "Criminal Laws" in res.note
    pk._search_cache.clear()


def test_caselaw_rows_with_query_words_ranked_first(monkeypatch):
    pk._search_cache.clear()
    pk._shortened.clear()
    mk = lambda i, sn: pk.DecisionHit(id=i, title="A v B", court="c", date="", case_number="", snippet=sn, url="")

    async def fake_post(url, content=None, headers=None, **kw):
        return types.SimpleNamespace(status_code=200, json=lambda: {"d": "[]"})

    monkeypatch.setattr(_http, "post", fake_post)
    monkeypatch.setattr(pk, "_ihc_rows", lambda payload: [mk("x", "Winding up"), mk("y", "Bail, After Arrest")])
    res = asyncio.run(pk.Pakistan().search_caselaw("bail"))
    assert [h.id for h in res.items] == ["y", "x"]
    assert "re-ordered" in res.note
    pk._search_cache.clear()


def test_caselaw_year_on_capped_slice_is_partial_not_refused(monkeypatch):
    pk._search_cache.clear()
    pk._shortened.clear()
    n = pk.IHC_CAP
    rows = [pk.DecisionHit(id=f"d{i}", title="A v B", court="c", date="",
                           case_number="Crl-1-2025" if i == 0 else "Crl-1-2020", snippet="bail", url="")
            for i in range(n)]

    async def fake_post(url, content=None, headers=None, **kw):
        return types.SimpleNamespace(status_code=200, json=lambda: {"d": "[]"})

    monkeypatch.setattr(_http, "post", fake_post)
    monkeypatch.setattr(pk, "_ihc_rows", lambda payload: rows)
    res = asyncio.run(pk.Pakistan().search_caselaw("bail", filters={"case_year": "2025"}))
    assert [h.id for h in res.items] == ["d0"]
    assert "partial" in res.note
    pk._search_cache.clear()
