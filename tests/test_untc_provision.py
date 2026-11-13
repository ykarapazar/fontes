from world_legal_mcp.jurisdictions.untc import _norm_provision


def test_norm_provision_numbers():
    assert _norm_provision("Article 03") == "Article 3"
    assert _norm_provision("art 3") == "Article 3"
    assert _norm_provision("Annex 2 art 3") == "Annex II Article 3"
    assert _norm_provision("Annex 02 Article 03") == "Annex II Article 3"
    assert _norm_provision("Annex II Article 3") == "Annex II Article 3"
    assert _norm_provision("Article iv") == "Article IV"


def test_norm_provision_bare_annex():
    for raw in ("Annex II", "Annex IV", "Annex XX", "Annex 12"):
        assert _norm_provision(raw) == raw
    assert _norm_provision("Annex IV Article 5") == "Annex IV Article 5"
    assert _norm_provision("annex 4 5") == "Annex IV Article 5"


def test_english_start_skips_chinese_copy():
    from world_legal_mcp.jurisdictions.untc import _english_start
    zh = "\n".join("本协定各缔约方，作为公约缔约方，按照决定建立的行动平台" for _ in range(30))
    text = (zh + "\nPARIS AGREEMENT\nUNITED NATIONS\n2015\n\nPARIS AGREEMENT\n"
            "The Parties to this Agreement,\nBeing Parties,\nArticle 1\nFor the purpose\n")
    assert text[_english_start(text):].startswith("PARIS AGREEMENT\nUNITED NATIONS")
    en = "PREAMBLE\nThe Parties,\nArticle 1\nFor the purpose\n"
    assert _english_start(en) == 0


def test_search_ranks_exact_title_first():
    import asyncio
    from world_legal_mcp.jurisdictions import untc
    rows = [{"id": "VII-6", "title": "Protocol amending the Paris Agreement", "conclusion": "", "chapter": "C"},
            {"id": "XXVII-7-d", "title": "Paris Agreement", "conclusion": "Paris, 12 December 2015",
             "chapter": "C"}]
    untc._chapters.clear()
    for n in range(1, 30):
        untc._chapters[n] = (__import__("time").monotonic(), rows if n == 1 else [])
    res = asyncio.run(untc.UNTC().search_legislation("Paris Agreement", limit=5))
    assert res.items[0].id == "XXVII-7-d"
