"""Live smoke tests against the Gaceta Oficial de Cuba (www.gacetaoficial.gob.cu, 10 s crawl delay)
and MINJUS's reposted issues (www.minjus.gob.cu). Needs network; both hosts are slow and sometimes
time out on connect."""
from world_legal_mcp import server


async def test_cu_search_type_number_gives_norm_code():
    # "Ley 189" -> the Gazette norm database's type+number filters; the hit id is the norm code.
    out = await server.search_legislation("cu", "Ley 189", limit=5)
    assert "GOC-2026-540-O78" in out and "Código de Trabajo" in out, out


async def test_cu_norm_code_narrows_to_norm_and_constitution_alias():
    # A norm code from an issue the Gazette site serves (not MINJUS) opens just that norm.
    toc = await server.get_legislation_toc("cu", "GOC-2026-540-O78")
    assert "Código de Trabajo" in toc and "gacetaoficial.gob.cu" in toc, toc[:500]
    c = await server.get_legislation_provision("cu", "Constitución", "Artículo 1")
    assert "Estado socialista de derecho" in c and "GOC-2025-487-ES9" in c, c


async def test_cu_norm_code_opens_issue_and_label_variants():
    # A norm code inside an issue opens that issue; "art. 5" and "5" resolve like "Artículo 5".
    a = await server.get_legislation_provision("cu", "GOC-2026-227-O26", "art. 5")
    b = await server.get_legislation_provision("cu", "GOC-2026-O26", "5")
    assert "estado civil" in a.lower() and "estado civil" in b.lower(), a


async def test_cu_later_norm_article_is_qualified():
    # The Reglamento (Resolución 61/2026) in the same issue restarts at Artículo 1.
    out = await server.get_legislation_provision("cu", "GOC-2026-O26", "1 GOC-2026-228-O26")
    assert "GOC-2026-228-O26" in out, out


async def test_cu_bad_id():
    assert "Bad request" in await server.get_legislation_text("cu", "ley 180")
