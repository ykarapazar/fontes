import asyncio
from types import SimpleNamespace

from world_legal_mcp import _http
from world_legal_mcp.jurisdictions import ci
from world_legal_mcp.models import LawHit


def test_code_query_note(monkeypatch):
    async def idx():
        return [LawHit(id="x", title="Loi portant code de procédure civile", url="u")]
    monkeypatch.setattr(ci, "_an_index", idx)
    a = ci.CoteDIvoire()
    r = asyncio.run(a.search_legislation("Code du travail", limit=10, page=1, filters={}))
    assert "not in this list" in r.note
    r = asyncio.run(a.search_legislation("mariage", limit=10, page=1, filters={}))
    assert "not in this list" not in r.note


def _card(slug, num):
    return (f'<article class="stoppage-card"><p class="post-category">CASSATION</p><ul>'
            f'<li>ARRET N°{num}</li><li>Objet de l\'Arrêt : Contrat de travail</li></ul>'
            f'<a href="/uploads/stoppages/{slug}.pdf">pdf</a></article>')


def test_duplicate_number_note(monkeypatch):
    page = ("<html>Jurisprudence " + _card("arret-n-161-24-du-15-fevrier-2024-1-1", "0161/24")
            + _card("arret-n-161-24-du-15-fevrier-2024-2-1", "161/24") + "</html>")

    async def get(url, **k):
        return SimpleNamespace(status_code=200, text=page)
    monkeypatch.setattr(_http, "get", get)
    r = asyncio.run(ci.CoteDIvoire().search_caselaw("Contrat de travail", limit=10, page=1, filters={}))
    assert "same case number" in r.note and "headnote" in r.note


def test_no_pdf_law_returns_summary_only(monkeypatch):
    page = ('<html><body><article><h2>Loi n°1 du 1 mai 2012 X</h2><p class="mt-10"><font size="3"><strong>'
            '<p>Résumé de la loi</p></strong></font></p></article><h4>Coopération parlementaire</h4></body></html>')

    async def get(url, **k):
        return SimpleNamespace(status_code=200, text=page)
    monkeypatch.setattr(_http, "get", get)
    ci._cache.clear()
    a = ci.CoteDIvoire()
    t = asyncio.run(a.get_legislation_text("loi-x-test"))
    assert "Coopération" not in t.text and "Résumé" in t.text and "no text" in t.metadata["Note"]
    try:
        asyncio.run(a.get_legislation_toc("loi-x-test"))
    except ci.NotFound as e:
        assert "no table of contents" in str(e)
    else:
        raise AssertionError


def test_zero_hit_hint(monkeypatch):
    async def get(url, **k):
        return SimpleNamespace(status_code=200, text="<html>Jurisprudence</html>")
    monkeypatch.setattr(_http, "get", get)
    r = asyncio.run(ci.CoteDIvoire().search_caselaw("licenciement", limit=10, page=1, filters={}))
    assert "Contrat de travail" in r.note and "matter" in r.note


def test_note_not_overgeneralised_and_flags_open(monkeypatch):
    async def get(url, **k):
        return SimpleNamespace(status_code=200, text="<html>Jurisprudence</html>")
    monkeypatch.setattr(_http, "get", get)
    r = asyncio.run(ci.CoteDIvoire().search_caselaw("licenciement", limit=10, page=1, filters={}))
    assert "filed under" not in r.note
    assert "open the decision" in r.note and "civ_com" in r.note


def test_get_decision_uppercase_header_gives_case_number(monkeypatch):
    async def pdf(url, source):
        return "ARRÊT N° 161/24 DU 15 FÉVRIER 2024\n\nLA COUR,"
    monkeypatch.setattr(ci, "_pdf", pdf)
    d = asyncio.run(ci.CoteDIvoire().get_decision("arret-n-161-24-du-15-fevrier-2024-1"))
    assert d.case_number == "161/24" and "161/24" in d.title


def test_labour_term_widens_to_travail(monkeypatch):
    seen = []

    async def get(url, **k):
        seen.append(url)
        body = "" if "search=travail" not in url else _card("arret-n-161-24-du-15-fevrier-2024-2-1", "161/24")
        return SimpleNamespace(status_code=200, text="<html>Jurisprudence " + body + "</html>")
    monkeypatch.setattr(_http, "get", get)
    r = asyncio.run(ci.CoteDIvoire().search_caselaw("licenciement abusif", limit=10, page=1, filters={}))
    assert len(r.items) == 1 and "NOT filtered" in r.note
