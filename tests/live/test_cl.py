"""Live smoke tests against BCN Ley Chile. Needs network."""
from world_legal_mcp import server


async def test_cl_provision_labels():
    for law, label in (("172986", "Artículo 2314"), ("172986", "art. 2314"), ("172986", "2314"),
                       ("https://www.bcn.cl/leychile/navegar?idNorma=172986", "2314 (DEL ART. 2)")):
        out = await server.get_legislation_provision("cl", law, label)
        assert "Artículo 2314" in out and "delito o cuasidelito" in out, (law, label)


async def test_cl_civil_code_wins_plain_labels():
    """In DFL 1 the Código Civil keeps 'Artículo 1'; the decree's own article is qualified."""
    code = await server.get_legislation_provision("cl", "172986", "Artículo 1")
    assert "La ley es una declaración de la voluntad soberana" in code
    dfl = await server.get_legislation_provision("cl", "172986", "Artículo 1 (de la norma)")
    assert "Déjase sin efecto" in dfl


async def test_cl_transitory_and_errors():
    out = await server.get_legislation_provision("cl", "141599", "1 transitorio")
    assert "Artículo 1 transitorio" in out and "sesenta días" in out
    bad = await server.get_legislation_provision("cl", "codigo civil", "1")
    assert bad.startswith("Bad request (cl)")
