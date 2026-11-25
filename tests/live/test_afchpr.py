"""Live smoke tests against AJUDATA, the African Court's case database. Needs network; 1 s per request."""
from world_legal_mcp import server


async def test_afchpr_filters_and_application_number():
    out = await server.search_caselaw("afchpr", "Konate", limit=10, filters={
        "respondent": "Burkina Faso", "status": "finalised",
        "date_from": "2016-01-01", "date_to": "2016-12-31"})
    assert "004/2013" in out and "036/2019" not in out, out      # 036/2019 is v. Côte d'Ivoire, pending
    exact = await server.search_caselaw("afchpr", "Application No. 4/2013", limit=5)
    assert "004/2013" in exact and "Konat" in exact
    bad = await server.search_caselaw("afchpr", "x", filters={"status": "open"})
    assert "Bad request" in bad
    unknown = await server.search_caselaw("afchpr", "x", filters={"respondent": "Atlantis"})
    assert "Bad request" in unknown and "Atlantis" in unknown


async def test_afchpr_case_record_lists_documents():
    out = await server.get_decision("afchpr", "004/2013", max_chars=20000)
    assert "Konat" in out and "Burkina Faso" in out
    assert "Judgments (Merits), 2014-12-05" in out and "004/2013#2034" in out
    assert "Dissenting Opinion" in out


async def test_afchpr_judgment_text_from_pdf():
    out = await server.get_decision("afchpr", "004/2013#2034", max_chars=3000)
    assert "2014-12-05" in out and "ajudata.african-court.org/download-file/2034/" in out, out[:800]
    missing = await server.get_decision("afchpr", "004/2013#1")
    assert "004/2013#2034" in missing          # NotFound lists what is available
    unknown = await server.get_decision("afchpr", "999/2099")
    assert "Not found" in unknown and "999/2099" in unknown


async def test_afchpr_advisory_opinions():
    out = await server.search_caselaw("afchpr", "vagrancy", filters={"kind": "advisory"})
    assert "AO 001/2018" in out, out
    rec = await server.get_decision("afchpr", "advisory opinion 1/2013")
    assert "AO 001/2013#1099" in rec and "SERAP" in rec, rec[:800]
    doc = await server.get_decision("afchpr", "AO 001/2013#1099", max_chars=2000)
    assert "AFRICAN COURT" in doc.upper() and "Advisory opinion" in doc, doc[:600]
