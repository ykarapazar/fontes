"""Live smoke tests against Areios Pagos (www.areiospagos.gr) and the Government Gazette
search API + PDF store (search.et.gr). Needs network; every host is spaced at 1 s."""
import re

import pytest

from world_legal_mcp import server
from world_legal_mcp.base import permitted_codes

needs_permission = pytest.mark.skipif("gr" not in permitted_codes(),
                                      reason="Gazette source needs permission: set WLM_PERMITTED=gr")


async def test_gr_number_search_and_decision_round_trip():
    out = await server.search_caselaw("gr", "1/2020", limit=10, filters={"chamber": "criminal"})
    ids = re.findall(r'get_decision\("gr", "([0-9A-Z]{30})"', out)
    assert "748DU89FA34LSZPK7Z51H5YW5N5H6D" in ids and "ΠΟΛΙΤΙΚΕΣ" not in out, out
    dec = await server.get_decision("gr", "748DU89FA34LSZPK7Z51H5YW5N5H6D", max_chars=3000)
    assert "Date: 2020-03-12" in dec and "ΑΡΕΙΟΥ ΠΑΓΟΥ" in dec


async def test_gr_ambiguous_number_and_subject_search():
    out = await server.get_decision("gr", "1/2020")
    assert re.search(r"\b\d+ decisions\b", out), out
    subj = await server.search_caselaw("gr", "μίσθωση εργασίας", limit=5, filters={"year": "2018"})
    assert "227/2018" in subj and "Μίσθωση εργασίας" in subj, subj


@needs_permission
async def test_gr_law_number_resolves_to_fek():
    out = await server.search_legislation("gr", "ν. 4624/2019", limit=3)
    assert "Α 137/2019" in out and "ΠΡΟΣΤΑΣΙΑΣ ΔΕΔΟΜΕΝΩΝ" in out, out
    for prov in ("Άρθρο 5", "5", "άρθρο 5"):
        p = await server.get_legislation_provision("gr", "ν. 4624/2019", prov)
        assert "δημόσιοι φορείς επιτρέπεται" in p, p


@needs_permission
async def test_gr_scanned_fek_is_reported_not_ocred():
    out = await server.get_legislation_text("gr", "Α 8/1989")
    assert "scan without a text layer" in out, out
