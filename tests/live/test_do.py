"""Live smoke tests against the TSE judgment viewer (visorpdf.tse.do). Needs network."""
from world_legal_mcp import server


async def test_do_id_variants_and_errors():
    for id in ("TSE/0087/2024", "TSE-87-2024", "87/2024"):
        out = await server.get_decision("do", id)
        assert "TSE-01-0302-2023" in out and "2024-01-08" in out, id
    bad = await server.get_decision("do", "Sentencia 87")
    assert bad.startswith("Bad request (do)")
    missing = await server.get_decision("do", "TSE/9999/2021")
    assert "not found" in missing.lower()


async def test_do_year_filter():
    out = await server.search_caselaw("do", "", filters={"year": "2023"}, limit=5)
    assert "TSE-" in out and "-2023" in out
    bad = await server.search_caselaw("do", "nulidad", filters={"year": "23"})
    assert bad.startswith("Bad request (do)")


async def test_do_summary_only_docx_is_flagged():
    out = await server.get_decision("do", "TSE/0328/2024")
    assert "Fuerza del Pueblo" in out and "only the summary" in out
