"""Live smoke tests against Maqam (maqam.najah.edu, An-Najah National University).
Needs network; 1 s per request."""
from world_legal_mcp import server


async def test_ps_search_splits_record_types():
    cases = await server.search_caselaw("ps", "القانون الأساسي", limit=3)
    assert "6309" in cases and "/judgments/" in cases and "/legislation/" not in cases, cases
    laws = await server.search_legislation("ps", "القانون الأساسي", limit=3)
    assert "622" in laws and "/judgments/" not in laws, laws


async def test_ps_decision_pdf_fallback_and_id_variants():
    # Old constitutional ruling: HTML has only the subject line; full text comes from the PDF.
    dec = await server.get_decision("ps", "https://maqam.najah.edu/judgments/6309/", max_chars=4000)
    assert "2013-03-18" in dec and "الهيئة الحاكمة" in dec, dec[:1500]
    bad = await server.get_decision("ps", "abc")
    assert "11179" in bad


async def test_ps_provision_label_variants():
    for prov in ("المادة (4)", "المادة 4", "مادة ٤", "4", "art. 4"):
        out = await server.get_legislation_provision("ps", "11", prov)
        assert "المادة (4)" in out and "الإسلام هو الدين الرسمي" in out, out[:600]
    missing = await server.get_legislation_provision("ps", "11", "999")
    assert "999" in missing
