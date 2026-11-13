from world_legal_mcp.jurisdictions import echr


def test_plain_phrase():
    assert echr._plain_phrase("Big Brother Watch")
    assert not echr._plain_phrase("Big")
    assert not echr._plain_phrase('"bulk interception"')
    assert not echr._plain_phrase("privacy AND surveillance")
    assert not echr._plain_phrase("appno:58170/13")


def test_quoted_name():
    assert echr._quoted_name('"Big Brother Watch"') == "Big Brother Watch"
    assert echr._quoted_name('"bulk"') is None
    assert echr._quoted_name('"a b" AND "c d"') is None
    assert echr._quoted_name("Big Brother Watch") is None


def test_unsupported_legislation_points_to_convention_pdf():
    j = echr.ECHR()
    assert not j.supports("search_legislation")
    assert any("convention_eng" in s.url and "legislation" in s.covers for s in j.sources)
