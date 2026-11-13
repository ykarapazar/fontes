from world_legal_mcp.jurisdictions import al


def test_amending_act_is_flagged():
    a = {"title": "PËR DISA SHTESA DHE NDRYSHIME NË LIGJIN NR.7850, DATË 29.7.1994, “KODI CIVIL”"}
    assert "AMENDING" in al._amending_warning(a)
    assert al._amending_warning({"title": "Kodi i Procedurave Administrative"}) == ""


def test_generic_unifying_words_known():
    assert {"unifikues", "njesues"} <= al._GENERIC


def test_base_code_query_says_not_available():
    assert "NOT AVAILABLE" in al._base_law_note("Kodi Civil")
    assert "NOT AVAILABLE" in al._base_law_note("ligj 7850")
    assert al._base_law_note("Kodi i Procedurave Administrative") == ""


def test_act_rank_puts_base_law_before_amending_order():
    q = al._fold("Për mbrojtjen e të dhënave personale")
    law = {"type": "Ligj", "number": "124", "date": "2024-12-19", "kind": "Akt bazë",
           "title": "Për mbrojtjen e të dhënave personale"}
    order = {"type": "Urdhër", "number": "35", "date": "2021-03-31", "kind": "Akt ndryshues",
             "title": "Për një ndryshim ... Mbrojtjen e të Dhënave Personale"}
    assert sorted([order, law], key=lambda a: al._act_rank(a, q))[0] is law
