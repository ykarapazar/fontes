from world_legal_mcp.jurisdictions.ge import _clean_number


def test_mixed_script_number_dropped():
    assert _clean_number("N875-Vრს-Xმპ") == ""
    assert _clean_number("N786") == "N786"
    assert _clean_number("") == ""
