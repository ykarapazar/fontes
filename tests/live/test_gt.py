"""Live smoke tests against the CC Guatemala PDF store (jurisprudencia.cc.gob.gt). Needs network."""
from world_legal_mcp import server

ID = "850297.3670-2022"  # amparo appeal, 24 Aug 2022


async def test_gt_id_variants_date_and_clean_text():
    for id in (ID, f"{ID}.pdf", f"https://jurisprudencia.cc.gob.gt/Sentencias/{ID}.pdf"):
        out = await server.get_decision("gt", id)
        assert "2022-08-24" in out and "3670-2022" in out, id
    assert "POR TANTO" in out and "promovió" in out
    assert "Página 2 de 20" not in out  # running page headers stripped


async def test_gt_joined_cases_link_with_encoded_space():
    url = "https://jurisprudencia.cc.gob.gt/Sentencias/850891.3450-2021%20y%203475-2021.pdf"
    out = await server.get_decision("gt", url)
    assert "3450-2021 y 3475-2021" in out and "2022-11-10" in out


async def test_gt_bad_and_missing_ids():
    assert (await server.get_decision("gt", "3670-2022")).startswith("Bad request (gt)")
    missing = await server.get_decision("gt", "1.1-1900")
    assert "not found" in missing.lower()
    nosearch = await server.search_caselaw("gt", "amparo")
    assert "not supported" in nosearch
