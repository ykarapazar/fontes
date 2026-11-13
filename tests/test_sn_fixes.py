"""Senegal: Code du travail 'Article L.84' labels, notes (offline)."""
from world_legal_mcp.jurisdictions.sn import Senegal, _pdf_md


def test_labour_code_article_labels():
    md = _pdf_md("TITRE PREMIER : X\nArticle L.83.\nUn.\nArticle L.84.\nSont soumises\nArticle R.2.\nDeux.")
    labels = [p for _, _, p, _, _ in Senegal._sections(md) if p]
    assert labels == ["Article L.83", "Article L.84", "Article R.2"]


def test_provision_l84_and_bare_number(monkeypatch):
    import asyncio
    md = _pdf_md("Article L.83.\nUn.\nArticle L.84.\nSont soumises")

    async def doc(self, id):
        return ("Code du travail", "u", md, "", {})
    monkeypatch.setattr(Senegal, "_doc", doc)
    for q in ("L.84", "Article L.84", "84"):
        p = asyncio.run(Senegal().get_legislation_provision("mj-1", q))
        assert p.provision == "Article L.84" and "Sont soumises" in p.text


def test_supreme_year_note(monkeypatch):
    import asyncio
    from world_legal_mcp.models import Results

    async def js(self, q, limit, page):
        return Results([], total=1216, note="JURICAF")
    monkeypatch.setattr(Senegal, "_jc_search", js)
    r = asyncio.run(Senegal().search_caselaw("x", limit=5, page=1, filters={"court": "supreme", "year": 2022}))
    assert r.total is None
    assert "Cannot select Cour suprême decisions by year" in r.note


def test_supreme_multiword_total_dropped(monkeypatch):
    import asyncio
    from world_legal_mcp.jurisdictions import sn as m

    class R:
        status_code = 200
        text = "<html><body>202 290 résultats trouvés</body></html>"

    async def get(url, *a, **k):
        return R()
    monkeypatch.setattr(m._http, "get", get)
    r = asyncio.run(Senegal()._jc_search("licenciement 2022", 10, 1))
    assert r.total is None and "No reliable total" in r.note
    r = asyncio.run(Senegal()._jc_search("licenciement", 10, 1))
    assert r.total == 202290


def test_zero_default_court_note_names_court(monkeypatch):
    import asyncio
    from world_legal_mcp.jurisdictions import sn as m

    async def js(url, params):
        class R:
            headers = {"X-WP-Total": "0"}
        return [], R()
    monkeypatch.setattr(m, "_json", js)
    r = asyncio.run(Senegal().search_caselaw("bail", limit=5, page=1, filters={}))
    assert "Conseil constitutionnel" in r.note and "court" in r.note and "supreme" in r.note
