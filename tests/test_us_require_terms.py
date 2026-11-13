import pytest

from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions.us import _require_terms


@pytest.mark.parametrize("q", ["", "*", "OR", "AND", "NOT ab", 'NOT "ab cd"', "of the", "v", "x OR y", "a* b*"])
def test_rejected(q):
    with pytest.raises(BadRequest):
        _require_terms(q, "x")


@pytest.mark.parametrize("q", ["ab", "ab OR", "$$ 42", "Fourth Amendment", "ab NOT cd", "Brown v. Board", "1983"])
def test_accepted(q):
    _require_terms(q, "x")


@pytest.mark.parametrize("q", ["NOT (ab)", "-ab", "a b"])
def test_negation_only_rejected(q):
    with pytest.raises(Exception):
        _require_terms(q, "x")


@pytest.mark.parametrize("q", ["U.S.", "O.J.", "U.S. v. Smith", "self-defense"])
def test_initialisms_accepted(q):
    _require_terms(q, "x")


def test_year_filter_validation():
    from world_legal_mcp.jurisdictions.us import _year
    assert _year("2022", "year_from") == 2022
    assert _year(None, "year_from") is None
    with pytest.raises(BadRequest):
        _year("22", "year_from")


def test_popular_names_resolve_to_citation():
    from world_legal_mcp.jurisdictions.us import _POPULAR, _PL_RE
    assert _POPULAR["inflation reduction act"] == "Pub. L. 117-169"
    assert all(_PL_RE.match(v) for v in _POPULAR.values())


def test_popular_usc_names():
    from world_legal_mcp.jurisdictions.us import _POPULAR_USC, _law_id
    assert _law_id(_POPULAR_USC["clean air act"]) == ("42", "7401")
    assert _law_id(_POPULAR_USC["americans with disabilities act"]) == ("42", "12101")
