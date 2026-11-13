import asyncio

from world_legal_mcp.jurisdictions import cu

ROW = """<html><body><div class="node node-norma-juridica"><h2 class="title"><a href="/es/decreto-ley-316-de-2013-x-0">Decreto Ley 316 de 2013 X</a></h2>
<div class="field field-name-field-estado-norma-juridica"><div class="field-label">Estado:&nbsp;</div><div class="field-items">
<div class="field-item even"><a>Copia corregida</a></div><div class="field-item odd"><a>Derogada</a></div></div></div>
<div class="field-name-body"><div class="field-label">Resumen:&nbsp;</div><p>Algo.</p></div></div></body></html>"""


class R:
    status_code = 200
    content = ROW.encode()


def test_status_not_run_together_and_constitution_hit(monkeypatch):
    async def fake(url, **kw):
        return R()
    monkeypatch.setattr(cu, "_gget", fake)
    res = asyncio.run(cu.Cuba().search_legislation("Constitución de la República"))
    assert res.items[0].id == "Constitución"
    assert res.items[1].status == "Copia corregida, Derogada"


def test_edition_id_from_search_opens(monkeypatch):
    seen = {}

    async def fake_issue(id_, slug="", item=None):
        seen["id"] = id_
        return item, {"date": ""}
    monkeypatch.setattr(cu, "_issue", fake_issue)
    item, p = asyncio.run(cu._doc("CODIGO-CIVIL"))
    assert seen["id"] == "CODIGO-CIVIL" and p["date"] == "2022-11-08"


def _row(slug, title, summ, status=""):
    st = (f'<div class="field-name-field-estado-norma-juridica"><div class="field-items">'
          f'<div class="field-item even"><a>{status}</a></div></div></div>') if status else ""
    return (f'<div class="node node-norma-juridica"><h2><a href="/es/{slug}">{title}</a></h2>{st}'
            f'<div class="field-name-body"><p>{summ}</p></div></div>')


def test_exact_summary_first_total_from_last_page_and_twin_status(monkeypatch):
    pager = ('<ul><li class="pager-next"><a href="/es/n?page=1">s</a></li>'
             '<li class="pager-last"><a href="/es/n?page=1">u</a></li></ul>')
    p0 = ("<html><head><meta charset='utf-8'></head><body>" + _row("dict", "Dictamen 1", "Sobre el Código Penal y más")
          + _row("ley-151", "Ley 151 de 2022 X", "Código Penal.")
          + _row("dl-316-0", "Decreto Ley 316 de 2013 X", "Algo", "Derogada")
          + _row("dl-316", "Decreto Ley 316 de 2013 X", "Algo") + pager + "</body></html>")
    p1 = "<html><body>" + _row("a", "Ley 1", "x") + _row("b", "Ley 2", "y") + "</body></html>"

    class P:
        status_code = 200

        def __init__(self, c):
            self.content = c.encode()

    async def fake(url, params=None, **kw):
        return P(p1 if (params or {}).get("page") == 1 else p0)
    monkeypatch.setattr(cu, "_gget", fake)
    res = asyncio.run(cu.Cuba()._gsearch({"body_value": "Código Penal"}, 10, 1, "Código Penal"))
    assert res.items[0].id == "ley-151"
    assert res.total == cu.PER_PAGE + 2
    st = res.items[-1].status
    assert st.startswith("Derogada") and "versión original" in st and "dl-316-0" in st
    assert "Copia corregida," not in st and "same title" in res.note


def test_codigo_civil_note_warns_about_later_amendments(monkeypatch):
    async def fake(url, **kw):
        return R()
    monkeypatch.setattr(cu, "_gget", fake)
    res = asyncio.run(cu.Cuba().search_legislation("Código Civil"))
    assert res.items[0].id == "CODIGO-CIVIL" and "NOT applied" in res.note
