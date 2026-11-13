from world_legal_mcp.jurisdictions.cr import _key


def test_bis_and_zero_variants():
    for v in ("16 bis", "16bis", "16-bis", "Artículo 16 BIS", "art. 16-BIS"):
        assert _key(v) == "16 bis"
    assert _key("016") == "16"
    assert _key("16") == "16"
    assert _key("1 Transitorio") == "t:1"


def test_other_latin_suffixes():
    for suf in ("ter", "quater", "quinquies", "sexies"):
        for v in (f"16 {suf}", f"16{suf}", f"16-{suf}", f"016{suf}", f"Artículo 16 {suf.upper()}"):
            assert _key(v) == f"16 {suf}"
    assert _key("16 quáter") == "16 quáter"
    assert _key("16terx") == "16terx"


def test_cl_key_thousands_and_ordinal():
    from world_legal_mcp.jurisdictions.cl import _key
    assert _key("Art. 2.314º") == _key("artículo 2314") == "2314"


def test_cr_split_strips_word_list_markers():
    from world_legal_mcp.jurisdictions.cr import _split
    h = ('<html><body><p>Son causas:</p><p><![if !supportLists]>a.<![endif]>Cuando el trabajador falte</p>'
         '<div class="pb-5 pt-2"><a class="enlaceFicha" href="#">Ficha Artículo 81</a></div></body></html>')
    (label, md), = _split(h)
    assert label == "81" and "supportLists" not in md and "endif" not in md
    assert "a. Cuando el trabajador falte" in md


def test_cr_base_code_lookup_and_prepend():
    import asyncio
    from world_legal_mcp.jurisdictions import cr
    assert cr._base("Código Penal")[0] == "5027" and cr._base(" código civil.")[0] == "15437"
    assert cr._base("Código Procesal Penal")[0] == "41297"

    async def fake(params, n):
        if params["textAnnio"] == 1970:
            return [{"IdFichaNorma": 5027, "NumeroNormativa": "4573", "NombreNormativa": "Código Penal"}]
        return [{"IdFichaNorma": 1, "NumeroNormativa": "10886", "NombreNormativa": "Reforma Código Penal"}]
    orig, cr._search_page = cr._search_page, fake
    try:
        res = asyncio.run(cr.CostaRica().search_legislation("Código Penal"))
    finally:
        cr._search_page = orig
    assert [i.id for i in res.items] == ["5027", "1"] and "5027" in res.note


def test_cr_text_search_defaults_to_laws_and_cpp_is_base_code(monkeypatch):
    import asyncio
    from world_legal_mcp.jurisdictions import cr
    seen = []

    async def fake(params, n):
        seen.append(dict(params))
        return []

    monkeypatch.setattr(cr, "_search_page", fake)
    j = cr.CostaRica()
    res = asyncio.run(j.search_legislation("despido", filters={"in": "text"}))
    assert seen[-1]["TipoNorma"] == 8 and "laws" in res.note
    asyncio.run(j.search_legislation("despido", filters={"in": "text", "type": "R"}))
    assert seen[-1]["TipoNorma"] == 12
    assert cr._base("Código Procesal Penal")[0] == "41297"


def test_law_number_used_as_id_is_flagged():
    from world_legal_mcp.jurisdictions.cr import _id_note
    assert "41297" in _id_note("7594", "Ley N° 991: Pensión a Particular")
    assert _id_note("41297", "x") == ""
    assert _id_note("991", "x") == ""


def test_cr_text_search_puts_base_code_first(monkeypatch):
    import asyncio
    from world_legal_mcp.jurisdictions import cr

    rows = [{"IdFichaNorma": i, "NumeroNormativa": n, "NombreTipoNorma": "Ley"}
            for i, n in ((1, 7739), (2, 7360), (8045, 2))]

    async def fake(params, n):
        return rows
    monkeypatch.setattr(cr, "_search_page", fake)
    res = asyncio.run(cr.CostaRica().search_legislation("despido sin justa causa", filters={"in": "text"}))
    assert res.items[0].id == "8045" and [i.id for i in res.items[1:]] == ["1", "2"]
