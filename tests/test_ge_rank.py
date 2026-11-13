from world_legal_mcp.jurisdictions.ge import _title_rank


def test_exact_title_ranks_first():
    q = "სისხლის სამართლის კოდექსი"
    assert _title_rank("საქართველოს სისხლის სამართლის კოდექსი", q) == 0
    assert _title_rank("„საქართველოს სისხლის სამართლის კოდექსი“", q) == 0
    assert _title_rank("კონსტიტუციური წარდგინება საქართველოს სისხლის სამართლის კოდექსის", q) == 1
    assert _title_rank("საქართველოს კონსტიტუცია", "საქართველოს კონსტიტუცია") == 0


def test_title_lead_and_constitution():
    from world_legal_mcp.jurisdictions.ge import _TITLE_LEAD, _is_constitution
    assert _TITLE_LEAD.sub("", "Law on Entrepreneurs") == "Entrepreneurs"
    assert _TITLE_LEAD.sub("", "Law of Georgia on Entrepreneurs") == "Entrepreneurs"
    assert _is_constitution("CONSTITUTION OF GEORGIA", "Constitutional Court of the Republic of Georgia")
    assert not _is_constitution("Constitution of Georgia (Adopted 1921)", "Constitution of Georgia")
