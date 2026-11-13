"""Malta TOC titles, offline: wrapped marginal notes must stay with their own article."""
from world_legal_mcp.jurisdictions import mt


def _titles(monkeypatch, rows):
    monkeypatch.setattr(mt, "_page_lines", lambda page: rows)
    return {b["label"]: (b["title"], b["meta"]) for b in mt._parse(["x"]) if b["kind"] == "article"}


def test_title_tail_after_next_article_number_stays_with_its_article(monkeypatch):
    t = _titles(monkeypatch, [
        ("  1.  Short title.", "Short title."),
        ("  2.  The principal has no action against the person.", "Action by third"),
        ("body", "party against"),
        ("", "principal or vice-"),
        ("", "versa."),
        ("  3.  The agent may deviate from the instructions.", "Powers of"),
        ("body", "agent."),
    ])
    assert t["2"][0] == "Action by third party against principal or vice- versa."
    assert t["3"][0] == "Powers of agent."


def test_title_start_above_the_number_joins_its_continuation(monkeypatch):
    # the first line of 3's note sits on the row above "3.", with its tail on the "3." row
    t = _titles(monkeypatch, [
        ("  1.  Short title.", "Short title."),
        ("  2.  Where the endorsement is made.", "Qualified endorsement."),
        ("", "Effect of restrictive"),
        ("  3.  Where the endorser prohibits transfer.", "endorsement."),
        ("", "Amended by:"),
        ("", "XI.2020.3."),
    ])
    assert t["2"][0] == "Qualified endorsement."
    assert t["3"] == ("Effect of restrictive endorsement.", "Amended by: XI.2020.3.")


def test_unrelated_digitless_line_after_amendments_is_not_pulled_into_next_title(monkeypatch):
    t = _titles(monkeypatch, [
        ("  1.  Short title.", "Short title."),
        ("  2.  Text.", "Rights."),
        ("", "Amended by:"),
        ("", "XI.2020.3."),
        ("  3.  Text.", "Duties."),
    ])
    assert t["2"] == ("Rights.", "Amended by: XI.2020.3.")
    assert t["3"][0] == "Duties."


def test_wide_gap_inside_body_line_is_not_a_note():
    page = "   CAP. 99.]       CODE      3\n\n" + "\n".join([
        "  7.  On engagement the employer shall explain".ljust(70) + "Conditions of",
        "  and shall deliver the written statement to".ljust(70) + "employment.",
        "  the employee about the conditions".ljust(70) + "Amended by:",
        "  the employer shall deliver".ljust(62) + "to the employee the terms",
    ])
    notes = [n for _, n in mt._page_lines(page)]
    assert "Conditions of" in notes
    assert "to the employee the terms" not in notes


def test_second_title_in_the_same_article_is_not_part_of_its_title(monkeypatch):
    t = _titles(monkeypatch, [
        ("  1.  Short title.", "Short title."),
        ("  2.  Text.", "Interdiction."),
        ("body", "General interdiction."),
        ("body", "Duration of"),
        ("  3.  Text.", "interdiction."),
        ("body", "Next."),
    ])
    assert t["2"][0] == "Interdiction."


def test_unfinished_title_goes_to_next_article_not_the_finished_sub_title(monkeypatch):
    t = _titles(monkeypatch, [
        ("  1.  Short title.", "Short title."),
        ("  2.  Text.", "Theft by"),
        ("body", "person."),
        ("", "Definition of"),
        ("", '"servant".'),
        ("", "Theft aggravated"),
        ("  3.  Text.", 'by "place".'),
    ])
    assert t["2"][0] == "Theft by person."
    assert t["3"][0] == 'Theft aggravated by "place".'


def test_article_number_left_of_the_body_column_stays_in_the_body():
    page = "152   CAP. 9.]     CRIMINAL CODE\n\n" + "\n".join([
        " " * 32 + "(a)  when it is committed on beehives;",
        "Theft aggravated" + " " * 9 + "271.   Theft is aggravated -",
        "by \"nature\".",
    ])
    rows = mt._page_lines(page)
    assert rows[2][1] == "Theft aggravated"
    assert rows[2][0].strip().startswith("271.")


def test_body_column_comes_from_note_rows_too():
    page = "154   CAP. 9.]     CRIMINAL CODE\n\n" + "\n".join([
        "Punishment for" + " " * 11 + "274.    Whosoever shall be guilty of theft with",
        "theft" + " " * 17 + "bodily harm shall be liable -",
        " " * 32 + "(a)  if the harm is grievous;",
        " " * 32 + "(b)  if the harm is slight;",
    ])
    rows = mt._page_lines(page)
    assert rows[2] == ("  bodily harm shall be liable -", "theft")


def test_art_regex_tolerates_footnote_asterisk():
    from world_legal_mcp.jurisdictions import mt
    for t, lab in [("6.* (1) No person", "6"), ("7.* (1) The Minister", "7"), ("6A.* (1) y", "6A")]:
        m = mt._ART.match(t)
        assert m and m[1] + m[2] == lab
