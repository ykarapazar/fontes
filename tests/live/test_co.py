"""Live smoke tests against the Corte Constitucional relatoría, datos.gov.co and Función Pública's
Gestor Normativo (legislation; needs WLM_PERMITTED=co and the OS trust store). Needs network."""
import pytest

from world_legal_mcp import server
from world_legal_mcp.base import permitted_codes


async def test_co_id_variants():
    for did in ("SU-214/16", "SU214-16", "Sentencia SU-214 de 2016",
                "https://www.corteconstitucional.gov.co/relatoria/2016/SU214-16.htm"):
        out = await server.get_decision("co", did, max_chars=3000)
        assert "Sentencia SU-214/16" in out and "2016-04-28" in out, did
        assert "relatoria/2016/SU214-16.htm" in out, did
    bad = await server.get_decision("co", "ley 1437 de 2011")
    assert bad.startswith("Bad request (co)")


async def test_co_filters_and_exact_number():
    out = await server.search_caselaw("co", "", filters={"type": "SU", "year": "2016", "magistrate": "rojas"}, limit=10)
    assert "SU-214/16" in out and "Alberto Rojas" in out
    exact = await server.search_caselaw("co", "C-355/06", limit=5)
    assert "C-355/06" in exact and "2006-05-10" in exact
    bad = await server.search_caselaw("co", "x", filters={"type": "X"})
    assert bad.startswith("Bad request (co)")


async def test_co_unknown_sentencia():
    out = await server.get_decision("co", "T-999/24")
    assert out.startswith("Not found (co)")


# --- Legislation: Función Pública Gestor Normativo (terms need written consent: WLM_PERMITTED=co) ---
needs_permission = pytest.mark.skipif("co" not in permitted_codes(),
                                      reason="source needs permission: set WLM_PERMITTED=co")


async def test_co_legislation_off_without_permission(monkeypatch):
    monkeypatch.delenv("WLM_PERMITTED", raising=False)
    out = await server.search_legislation("co", "Ley 1437 de 2011")
    assert out.startswith("Off by default (co)") and "WLM_PERMITTED" in out


@needs_permission
async def test_co_legislation_citation_search_and_filters():
    out = await server.search_legislation("co", "Ley 1437 de 2011", limit=5)
    assert "Ley 1437 de 2011" in out and "41249" in out
    out = await server.search_legislation("co", "", filters={"type": "ley", "number": "599", "year": "2000"})
    assert "Ley 599 de 2000" in out
    bad = await server.search_legislation("co", "x", filters={"type": "edicto"})
    assert bad.startswith("Bad request (co)")


@needs_permission
async def test_co_law_id_and_provision_variants():
    for law_id, prov in (("41249", "10"), ("Ley 1437 de 2011", "art. 10"),
                         ("https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=41249", "Artículo 10")):
        out = await server.get_legislation_provision("co", law_id, prov)
        assert "Deber de aplicación uniforme de las normas y la jurisprudencia" in out, (law_id, prov)
    # spaced and hyphenated suffixes in the Penal Code (Ley 599 de 2000)
    out = await server.get_legislation_provision("co", "Ley 599 de 2000", "134 A")
    assert "ACTOS DE DISCRIMINACIÓN" in out
    out = await server.get_legislation_provision("co", "Ley 599 de 2000", "243-A")
    assert "agravación punitiva" in out.lower()
    missing = await server.get_legislation_toc("co", "Ley 84 de 1873")  # Código Civil: not in the Gestor
    assert "not found" in missing.lower()


@needs_permission
async def test_co_constitution_toc_and_repeated_transitorios():
    toc = await server.get_legislation_toc("co", "4125", keyword="tutela")
    assert "86" in toc
    out = await server.get_legislation_provision("co", "4125", "Transitorio 1")
    assert "27 de octubre de 1991" in out
    out = await server.get_legislation_provision("co", "4125", "Transitorio 1 (2)")
    assert "27 de octubre de 1991" not in out
