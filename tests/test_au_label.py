"""Australia: Constitution headings are '51. Title' (trailing full stop); offline."""
from world_legal_mcp.jurisdictions import au


def test_constitution_section_heading_gets_a_label():
    assert au._label("51. Legislative powers of the Parliament.", None) == "s 51"
    assert au._label("18 Unconscionable conduct", None) == "s 18"
    assert au._label("18 Unconscionable conduct", "Sch 2") == "Sch 2 s 18"


def test_bare_number_resolves_to_that_label():
    assert au._norm_provision("51") == "s 51"
    assert au._norm_provision("section 51") == "s 51"


def test_renamed_act_number_is_flagged_as_original_enactment():
    renamed = au._hit({"id": "C2004A00109", "name": "Competition and Consumer Act 2010",
                       "collection": "Act", "number": 51, "year": 1974,
                       "makingDate": "1974-08-24T00:00:00", "status": "InForce"})
    assert "original enactment" in renamed.number
    plain = au._hit({"id": "C2010A00140", "name": "Some Act 2010", "collection": "Act",
                     "number": 140, "year": 2010, "makingDate": "2010-12-15T00:00:00"})
    assert plain.number == "No. 140, 2010"
