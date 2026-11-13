"""Live smoke tests against the Tribunal Agroambiental (case law) and the Cámara de Diputados (legislation).
Needs network."""
from world_legal_mcp import server


async def test_bo_provision_labels():
    for law, label in (("254", "Artículo 1"), ("Ley N° 254", "art. 1"), ("0254", "1"),
                       ("https://diputados.gob.bo/leyes/ley-no-254/", "Artículo 1º")):
        out = await server.get_legislation_provision("bo", law, label)
        assert "Bolivia (bo)" in out and "Constitucional" in out, (law, label)


async def test_bo_scan_without_text_layer():
    out = await server.get_legislation_text("bo", "1512")
    assert out.startswith("Error (bo)") and "text layer" in out and ".pdf" in out


async def test_bo_caselaw_type_filter_and_bad_id():
    out = await server.search_caselaw("bo", "servidumbre", filters={"type": "6"}, limit=3)
    assert "Tribunal Agroambiental" in out and "get_decision(\"bo\"" in out
    bad = await server.get_decision("bo", "AAP-S1-0181-2026")
    assert bad.startswith("Bad request (bo)")


async def test_bo_lexivox_constitution_and_old_law():
    hits = await server.search_legislation("bo", "Constitución Política del Estado", limit=3)
    assert "BO-CPE-20090207" in hits and "Unofficial source" in hits
    art = await server.get_legislation_provision("bo", "BO-CPE-20090207", "Artículo 410")
    assert "supremacía" in art.lower() or "norma suprema" in art.lower()
    toc = await server.get_legislation_toc("bo", "bo-cpe-20090207")
    assert "Artículo 411" in toc and "Artículo transitorio 10" in toc
    old = await server.get_legislation_provision("bo", "https://www.lexivox.org/norms/BO-L-1715.xhtml", "1")
    assert "Servicio Nacional de Reforma Agraria" in old


async def test_bo_lexivox_law_number_search():
    out = await server.search_legislation("bo", "Ley 1650", limit=5)
    assert "BO-L-N1650" in out and "BO-L-1650" in out
