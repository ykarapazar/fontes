"""Live smoke tests against www.icj-cij.org (HTML pages only; PDFs are bot-challenged). Needs network; 1 s per request."""
from world_legal_mcp import server


async def test_icj_search_filters():
    out = await server.search_caselaw("icj", "genocide", limit=5, filters={
        "type": "judgments", "proceedings": "preliminary_objections",
        "date_from": "2022-07-01", "date_to": "2022-07-31"})
    assert "178-20220722-jud-01-00" in out, out
    bad = await server.search_caselaw("icj", "x", filters={"type": "awards"})
    assert "type must be one of" in bad


async def test_icj_case_record_lists_documents():
    out = await server.get_decision("icj", "ICJ case 178", max_chars=20000)
    assert "Gambia v. Myanmar" in out and "## Judgments" in out
    assert "[178-20220722-jud-01-00]" in out and "[178-20220722-jud-01-01]" in out   # judgment + Judge Xue
    unknown = await server.get_decision("icj", "999")
    assert "no case 999" in unknown.lower()


async def test_icj_document_id_variants():
    # file name with language suffix and upper case, as linked on the site
    out = await server.get_decision("icj", "178-20220722-JUD-01-00-EN.pdf", max_chars=6000)
    assert "Judgment of 22 July 2022" in out and "Dissenting Opinion of Judge Xue" in out
    assert "Summary of the Judgment of 22 July 2022" in out and "Cloudflare" in out
    old = await server.get_decision("icj", "1-19490409-jud-01-00")      # Corfu Channel merits
    assert "Corfu Channel" in old and "001-19490409-jud-01-00" in old
