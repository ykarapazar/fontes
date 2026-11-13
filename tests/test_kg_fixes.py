from world_legal_mcp.jurisdictions.kg import _stem


def test_stem_case_endings():
    assert _stem("право собственности") == "прав собств"


def test_code_names_in_genitive_not_cut_short():
    assert _stem("Уголовный кодекс") == '"Уголовного кодекса"'
    assert _stem("Уголовного кодекса") == '"Уголовного кодекса"'
    assert _stem("Гражданский кодекс") == '"Гражданского кодекса"'


def test_code_name_is_phrase_so_procedure_code_not_matched():
    assert _stem("Уголовный кодекс статья 82") == '"Уголовного кодекса" статья 82'


def test_zero_hits_multiword_note(monkeypatch):
    import asyncio
    from world_legal_mcp.jurisdictions import kg

    class R:
        headers = {"x-wp-total": "0"}

    async def fake(url, params=None):
        return [], R()

    monkeypatch.setattr(kg, "_json", fake)
    res = asyncio.run(kg.Kyrgyzstan().search_caselaw("трудовой договор"))
    assert "every word must appear" in res.note
