import asyncio

from world_legal_mcp import server


def run(c):
    return asyncio.run(c)


def test_list_no_query_is_compact():
    out = run(server.list_jurisdictions())
    assert len(out) < 30000
    assert "- jp:" in out and "- echr:" in out


def test_list_exact_code_is_full_and_single():
    out = run(server.list_jurisdictions("in"))
    assert out.count("\n## ") + out.startswith("## ") == 1
    assert "Source:" in out


def test_unsupported_names_only_matching_sources():
    msg = run(server.search_caselaw("jp", "x"))
    assert "e-Gov" not in msg.split("Notes:")[0].split("Supported for")[0] or "courts.go.jp" in msg
    msg = run(server.search_caselaw("au", "x"))
    assert "legislation.gov.au" not in msg.split("Notes:")[0]
    assert "hcourt.gov.au" in msg


def test_unsupported_legislation_points_to_notes_and_marks_gated():
    msg = run(server.search_legislation("echr", "Article 6"))
    assert "echr.coe.int/documents/d/echr/convention_eng" in msg
    msg = run(server.search_legislation("sg", "Employment Act"))
    assert "sso.agc.gov.sg" in msg and "off by default" in msg


def test_ie_caselaw_points_to_decisions():
    assert "workplacerelations.ie" in run(server.search_caselaw("ie", "unfair dismissal"))


def test_no_date_filter_message():
    msg = run(server.search_legislation("au", "Privacy Act", filters={"year_from": 2022}))
    assert "no date filter" in msg
