

def test_later_amenders_flags_laws_only(monkeypatch):
    import asyncio
    from world_legal_mcp.models import LawHit, Results
    from world_legal_mcp.jurisdictions import cl

    async def fake(self, q, *, limit=10, page=1, filters=None):
        assert q == "ley 19628" and filters == {"year_from": "2022"}
        mk = lambda i, t, d, s: LawHit(id=i, title=t, type="", number="", date=d, status="", snippet=s, url="")
        return Results(items=[
            mk("1209272", "Ley 21719 – REGULA LA PROTECCIÓN", "2024-12-13", "introduce modificaciones a la Ley Nº 19.628"),
            mk("1225450", "Resolución 1400 EXENTA – X", "2026-06-24", "modifica ... Ley 19.628"),
            mk("999", "Ley 21000 – OTRA", "2023-01-01", "modifica la Ley 19.629")])
    monkeypatch.setattr(cl.Chile, "search_legislation", fake)
    cl._later.clear()
    law = {"id": "141599", "title": "Ley 19628 – SOBRE PROTECCION DE LA VIDA PRIVADA", "as_of": "2022-11-10"}
    out = asyncio.run(cl.Chile()._later_amenders(law))
    assert "Ley 21719 (2024-12-13, id 1209272)" in out and "Resolución" not in out and "21000" not in out
