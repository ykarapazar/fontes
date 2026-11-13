import asyncio

from world_legal_mcp.jurisdictions import mc


def test_word_query_unstemmed_prefix():
    q = mc._word_query("licenciement abusif")["simple_query_string"]
    assert q["fields"] == ["enBody.exact"] and q["query"] == "licenciement* abusif*"
    assert mc._word_query("de")["simple_query_string"]["query"] == "de"
    assert mc._word_query('"licenciement abusif"') is None
    assert mc._word_query("licen*") is None


def test_search_falls_back_to_stemmed_when_exact_empty(monkeypatch):
    seen = []

    async def fake_es(q):
        seen.append(q["query"]["bool"]["must"][2])
        hits = [] if len(seen) == 1 else [{"_source": {"path": "/jurisprudence/x/1/", "title": "T",
                                                       "date": "2024-01-01", "jurisdiction": ""}}]
        return {"hits": {"hits": hits, "total": {"value": len(hits)}}}

    monkeypatch.setattr(mc, "_es", fake_es)
    res = asyncio.run(mc.Monaco().search_caselaw("responsabilite"))
    assert "enBody.exact" in seen[0]["simple_query_string"]["fields"]
    assert "enBody.exact" not in seen[1]["simple_query_string"]["fields"]
    assert len(res.items) == 1


def test_word_search_ranks_by_relevance(monkeypatch):
    seen = []

    async def fake_es(q):
        seen.append(q)
        return {"hits": {"hits": [], "total": {"value": 0}}}

    monkeypatch.setattr(mc, "_es", fake_es)
    asyncio.run(mc.Monaco().search_caselaw("bail commercial"))
    should = seen[0]["query"]["bool"]["should"]
    assert any("match_phrase" in c for c in should)
    assert any("simple_query_string" in c for c in should)


def test_tpi_filter_note_points_to_labour_court(monkeypatch):
    async def fake_es(q):
        return {"hits": {"hits": [], "total": {"value": 0}}}

    monkeypatch.setattr(mc, "_es", fake_es)
    res = asyncio.run(mc.Monaco().search_caselaw(
        "licenciement", filters={"court": "tribunal-premiere-instance"}))
    assert "tribunal-travail" in res.note
    res = asyncio.run(mc.Monaco().search_caselaw("licenciement"))
    assert "tribunal-travail" not in res.note


def test_code_du_travail_searches_contrat_de_travail(monkeypatch):
    seen = []

    async def fake_es(q):
        seen.append(q)
        return {"hits": {"hits": [], "total": {"value": 0}}}

    monkeypatch.setattr(mc, "_es", fake_es)
    res = asyncio.run(mc.Monaco().search_legislation("code du travail"))
    assert "contrat de travail" in str(seen[0]) and "729" in res.note


def test_toc_untitled_articles_show_opening_words(monkeypatch):
    from lxml import html as lh

    page = lh.fromstring(
        '<html><body><div id="content"><section class="art" data-title="Article 4">'
        '<p>Remplacé par la loi n° 1.583</p><p>La période d\'essai est le délai nécessaire.</p>'
        '</section></div></body></html>')

    async def fake_page(pid):
        return page

    monkeypatch.setattr(mc, "_page", fake_page)
    toc = asyncio.run(mc.Monaco().get_legislation_toc("tnc/loi/1963/03-16-729"))
    assert toc.entries[0].provision == "Article 4"
    assert "période d'essai" in toc.entries[0].title
    assert "full text" in toc.note
