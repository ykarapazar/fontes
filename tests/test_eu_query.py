from world_legal_mcp.jurisdictions.eu import _competition_noise, _fts


def test_dominance_matches_dominant():
    assert '"dominan*"' in _fts("abuse of dominance")
    assert '"dominant"' in _fts("abuse of dominant position")


def test_competition_noise_only_for_bare_competition():
    assert _competition_noise("competition")
    assert not _competition_noise("notice of competition")
    assert not _competition_noise("data protection")
