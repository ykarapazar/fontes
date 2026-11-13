from world_legal_mcp.jurisdictions import bh


def test_licence_note_does_not_imply_free_reuse():
    src = bh.Bahrain.sources[0]
    assert src.needs_permission
    assert "does not lift the site's terms" in src.licence
    assert "needs LLOC's permission" in src.licence or "needs LLOC's permission" in src.licence.replace("reuse still ", "")


def test_warning_says_no_cassation_judgments():
    assert "not Court of Cassation" in bh.Bahrain.sources[0].warning
