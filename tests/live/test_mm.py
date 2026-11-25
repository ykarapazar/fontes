"""Live smoke tests for Myanmar: laws and procedures posted by the Supreme Court of the Union
(unionsupremecourt.gov.mm, PDFs) and law-report rulings from its RCMS (rcms.usc.gov.mm, needs the
OS trust store: fails on Linux). Needs network. Throttled to one request per second."""
from world_legal_mcp import server
from world_legal_mcp.jurisdictions.mm import Myanmar

CPC = Myanmar.samples["law_id"]
CRPC = "1783905167-mm-6a543b8fb81bf-THE-CODE-OF-CRIMINAL-PROCEDURE.pdf"


async def test_mm_search_type_filter_and_file_name_words():
    out = await server.search_legislation("mm", "companies", filters={"type": "law"})
    assert "Myanmar-Companies-Law" in out, out
    out = await server.search_legislation("mm", "", filters={"type": "amendment"})
    assert "Amending law" in out and "CODE OF CIVIL" not in out, out
    assert "Bad request" in await server.search_legislation("mm", "x", filters={"type": "decree"})


async def test_mm_crpc_lettered_sections_and_full_url_id():
    url = "https://www.unionsupremecourt.gov.mm/uploads/legislative/" + CRPC
    out = await server.get_legislation_provision("mm", url, "section 99A")
    assert "99A" in out and "forfeit" in out.lower(), out[:1500]
    toc = await server.get_legislation_toc("mm", CRPC, keyword="Section 565")
    assert "Section 565" in toc, toc[-1500:]


async def test_mm_unknown_id_not_found():
    out = await server.get_legislation_text("mm", "123-not-listed.pdf")
    assert "not in the Supreme Court" in out or "Not found" in out, out


async def test_mm_caselaw_fulltext_with_type_and_year_filters():
    # "Necessary Parties" appears only in the ruling's text, not in its title or headnote
    out = await server.search_caselaw("mm", "Necessary Parties", filters={"type": "civil", "year": "၂၀၁၀"})
    assert "1571733531" in out and "2010-02-11" in out, out[:1500]
    assert "Bad request" in await server.search_caselaw("mm", "x", filters={"type": "tax"})


async def test_mm_english_report_title_and_url_id():
    out = await server.get_decision("mm", "https://rcms.usc.gov.mm/precedentDetail/1594786037")
    assert out.startswith("# MA MO E AND OTHERS V. MA KUN HLAING") and "Letters Patent Appeal No. 10 of 1940" in out, out[:800]
    assert "s. 115 of the Evidence Act" in out, out[:3000]


async def test_mm_decision_bad_and_unknown_ids():
    assert "Bad request" in await server.get_decision("mm", "abc")
    assert "Not found" in await server.get_decision("mm", "999999999")


async def test_mm_law_reports_run_to_2022():
    # the court's law reports (and RCMS) end with the 2022 volume; nothing later is published
    out = await server.search_caselaw("mm", "", filters={"year": "2022"})
    assert "2022-" in out and "no law reports after 2022" in out, out[:800]
