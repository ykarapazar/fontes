import pytest

from world_legal_mcp.jurisdictions import nl

E_ = "ECLI:NL:HR:2019:1734"


@pytest.mark.parametrize("u", [
    "https://deeplink.rechtspraak.nl/uitspraak?id=" + E_,
    "https://uitspraken.rechtspraak.nl/details?id=" + E_,
    "https://uitspraken.rechtspraak.nl/details?id=" + E_ + "&showbutton=true",
    "https://uitspraken.rechtspraak.nl/details?x=1&id=" + E_ + "&showbutton=true",
    "https://uitspraken.rechtspraak.nl/#!/details?id=" + E_,
    "https://uitspraken.rechtspraak.nl/details?id=" + E_ + "#frag",
    "https://uitspraken.rechtspraak.nl/details?id=ECLI%3ANL%3AHR%3A2019%3A1734",
    "https://uitspraken.rechtspraak.nl/inziendocument?id=" + E_,
])
def test_url_forms(u):
    m = nl._URL_ECLI_RE.match(u)
    assert m and nl.unquote(m.group(1)) == E_


@pytest.mark.parametrize("u", [
    "https://evil.example/x?id=" + E_,
    "https://deeplink.rechtspraak.nl.evil.com/x?id=" + E_,
    "https://uitspraken.rechtspraak.nl/details?id=" + E_ + ":garbage",
])
def test_url_rejected(u):
    assert not nl._URL_ECLI_RE.match(u)
