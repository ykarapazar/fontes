import asyncio

from world_legal_mcp.jurisdictions import uy


def test_title_search_finds_data_protection_law():
    r = asyncio.run(uy.Uruguay().search_legislation("Protección de Datos Personales"))
    assert r.total == 1 and r.items[0].id == "leyes/18331-2008"


def test_bare_number_finds_law():
    r = asyncio.run(uy.Uruguay().search_legislation("ley 18331"))
    assert r.items[0].id == "leyes/18331-2008"
    r = asyncio.run(uy.Uruguay().search_legislation("18.331"))
    assert r.items[0].id == "leyes/18331-2008"


def test_bjn_no_results_is_empty_not_error():
    import world_legal_mcp.jurisdictions.uy as m

    async def post(form, data):
        return '<span class="rich-messages-label">No se encontraron sentencias que cumplan este criterio</span>'
    orig, m._bjn_post = m._bjn_post, post
    try:
        form = {"query": "q", "number": "n", "search": "s", "size": "", "sort": "", "from": "", "to": "",
                "types": "", "importance": "", "viewstate": "", "action": ""}
        assert asyncio.run(m._bjn_search(form, "", "1/2000", {}, 10)) == ""
    finally:
        m._bjn_post = orig


def test_bare_numero_query_goes_to_number_field():
    import world_legal_mcp.jurisdictions.uy as m
    seen = {}

    async def fake(form, q, number, filters, size):
        seen.update(q=q, number=number)
        return ""
    async def opn():
        return {}
    o = (m._bjn_search, m._bjn_open)
    m._bjn_search, m._bjn_open = fake, opn
    try:
        asyncio.run(m.Uruguay().search_caselaw("410/2023", filters={"number": "410/2023"}))
    finally:
        m._bjn_search, m._bjn_open = o
    assert seen == {"q": "", "number": "410/2023"}


def test_decision_warns_source_is_search_page():
    import world_legal_mcp.jurisdictions.uy as m
    h = ('<span id="textoSentenciaBox">texto</span></span></div>')
    d = m._parse_hoja(h, {"sede": "SCJ", "numero": "1/2000", "date": "2000-01-01"})
    assert "No direct link" in d.note and "search page" in d.note
