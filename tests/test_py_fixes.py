import asyncio

from world_legal_mcp.jurisdictions import py


def _law(lid, title, arts):
    return {"id": lid, "title": title, "arts": arts, "paras": [], "entries": [], "url": "u", "meta": {}, "pdfs": []}


def test_civil_article_found_in_sibling_record(monkeypatch):
    laws = {"5293": _law("5293", "CODIGO CIVIL", {"1": ["Art.1"]}),
            "522": _law("522", "CODIGO CIVIL III", {"1856": ["Art.1856.- daño"]})}

    async def fake(lid):
        return laws.get(lid) or _law(lid, "x", {})
    monkeypatch.setattr(py, "_law", fake)
    p = asyncio.run(py.Paraguay().get_legislation_provision("5293", "1856"))
    assert p.law_id == "522" and "1856" in p.text


def test_search_notes_and_ranking(monkeypatch):
    data = [{"id_documento": 1, "titulo_documento": "Ley Nº 2242 / PROMULGACIÓN DE LA NUEVA CONSTITUCIÓN NACIONAL",
             "nombre_categoria": "Leyes Paraguayas"},
            {"id_documento": 9580, "titulo_documento": "CONSTITUCION DE LA REPUBLICA DEL PARAGUAY",
             "nombre_categoria": "Leyes Paraguayas"},
            {"id_documento": 2515, "titulo_documento": "Ley Nº 729 / SANCIONA EL CODIGO DEL TRABAJO",
             "nombre_categoria": "Leyes Paraguayas"},
            {"id_documento": 2608, "titulo_documento": "Ley Nº 213 / ESTABLECE EL CODIGO DEL TRABAJO.",
             "nombre_categoria": "Leyes Paraguayas"}]

    class R:
        content = __import__("json").dumps(data).encode()
        status_code = 200

    only = [d for d in data if d["id_documento"] != 9580]

    class R2(R):
        content = __import__("json").dumps(only).encode()

    async def fake(url):
        return R() if "Rep" in url else R2()
    monkeypatch.setattr(py, "_bacn_get", fake)
    py._search_cache.clear()
    res = asyncio.run(py.Paraguay().search_legislation("Constitución Nacional"))
    assert res.items[0].id == "9580"
    py._search_cache.clear()
    res = asyncio.run(py.Paraguay().search_legislation("Código del Trabajo"))
    assert res.items[0].id == "2608" and "repealed by art. 412" in res.note
