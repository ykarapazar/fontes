"""Offline tests for the Seychelles adapter (no network)."""
from world_legal_mcp.jurisdictions import sc


def test_row_warning_flags_inconsistent_dates_and_pdf():
    url = "https://www.judiciary.sc/wp-content/uploads/2026/09/06102025-cc40_2025-x.pdf"
    w = sc._row_warning("A v B (CC 40 of 2025) [2025] SCSC 138 (25 August 2025)", "2025-10-06", url)
    assert "25 August 2025" in w and "2025-10-06" in w
    url2 = "https://www.judiciary.sc/wp-content/uploads/2026/09/23052025-ca30_2021-x.pdf"
    assert "23-05-2025" in sc._row_warning("A v B [2025] SCSC 170 (18 November 2025)", "2025-11-18", url2)
    assert sc._row_warning("A v B [2025] SCSC 1 (6 October 2025)", "2025-10-06", url) == ""


def test_civil_code_articles_inside_schedule_get_provisions():
    text = "\n".join(["Civil Code Act", "ARRANGEMENT OF", "", "1. Short title", "",
                      "ENACTED by the President.", "1. This Act may be cited.", "",
                      "2. Code", "Schedule", "Civil Code of Seychelles", "Article 1",
                      "This is the Code.", "Article 1381", "Text of 1381.",
                      "Delicts and quasi-delicts", "Article 1382",
                      "(1) Every human act that causes harm.", "Article 19-143", "[Vacant]"])
    blocks = sc._parse_law(text)
    arts = {b["label"]: b for b in blocks if b["kind"] == "article"}
    assert set(arts) == {"1", "1381", "1382", "19-143"}
    assert arts["1382"]["title"] == "Article 1382 – Delicts and quasi-delicts"
    assert "Delicts" not in sc._block_md(arts["1381"])
    assert "Every human act" in sc._block_md(arts["1382"])
    assert sc._norm_provision("Article 1382") == "1382"


def test_1979_constitution_flagged_superseded():
    assert "superseded" in sc._law_status({"url": "https://x/the-constitution-of-seychelles-1979.pdf"})
    assert sc._law_status({"url": "https://x/penal-code.pdf"}) == ""


def test_row_linking_another_cases_pdf_is_detected():
    bad = "https://www.judiciary.sc/wp-content/uploads/2026/09/23052025-ca30_2021-mauritian.pdf"
    assert sc._other_case_pdf("CA 30 of 2024; CA 33 of 2024", "2025-11-18", bad)
    good = "https://www.judiciary.sc/wp-content/uploads/2026/09/06102025-cc40_2025-x.pdf"
    assert not sc._other_case_pdf("CC 40 of 2025", "2025-10-06", good)
    assert not sc._other_case_pdf("CC 40 of 2025", "2025-08-25", good)  # date differs, same case


def test_neutral_citation_line_date():
    m = sc._NC_DATE.search("x\nNeutral Citation: Bluemoonstudio Inc vBybit (CC40/2025) 6th October 2025\n")
    assert sc._date(m[1]) == "2025-10-06"


def test_title_date_follows_listed_date_when_pdf_agrees():
    url = "https://www.judiciary.sc/wp-content/uploads/2026/09/06102025-cc40_2025-x.pdf"
    t = "A v B (CC 40 of 2025) [2025] SCSC 138 (25 August 2025)"
    assert sc._title_date(t, "2025-10-06", url).endswith("[2025] SCSC 138 (6 October 2025)")
    assert sc._title_date(t, "2025-08-25", url) == t  # PDF name disagrees: leave the site's title
