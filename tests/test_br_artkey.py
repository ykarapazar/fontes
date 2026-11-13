from world_legal_mcp.jurisdictions.br import _art_key


def test_art_key():
    assert _art_key("Art. 1.358-A.") == "1358-a"
    assert _art_key("1.358 A") == "1358-a"
    assert _art_key("5º") == "5"
    assert _art_key("art 5o") == "5"
    assert _art_key("186") == "186"
    assert _art_key("186 bis") == "186-bis"
    assert _art_key("1.723 § 1º") == ""


def test_exact_match_ranks_first():
    from world_legal_mcp.jurisdictions.br import _exact
    assert _exact("14.133", {"numero": 14133, "nome": "Lei nº 14.133 de 01/04/2021"})
    assert not _exact("14.133", {"numero": 15471, "nome": "Lei nº 15.471 de 20/07/2026"})
    assert _exact("Lei de Licitações e Contratos Administrativos",
                  {"numero": 14133, "ementa": "Lei de Licitações e Contratos Administrativos."})
    assert _exact("Constituição da República Federativa do Brasil",
                  {"nome": "Constituição da República Federativa do Brasil"})
    assert not _exact("Constituição da República Federativa do Brasil", {"nome": "Lei nº 7.844"})


def test_exact_match_on_popular_name():
    from world_legal_mcp.jurisdictions.br import _exact
    c = {"numero": 8078, "nome": "Lei nº 8.078 de 11/09/1990",
         "apelido": "LEI-8078-1990-09-11 , Código de Proteção e Defesa do Consumidor (CPDC) , Código de Defesa do Consumidor (1990) (CDC)"}
    assert _exact("Código de Defesa do Consumidor", c)
    assert _exact("código de proteção e defesa do consumidor", c)
    assert not _exact("Defesa do Consumidor", c)


def test_metadata_only_norm_message():
    import pytest
    from world_legal_mcp.base import NotFound
    from world_legal_mcp.jurisdictions.br import _parse
    urn = "urn:lex:br:federal:decreto.lei:1940-12-07;2848"
    d = {"sameAs": ["http://legis.senado.leg.br/legislacao/DetalhaSigen.action?id=527942"]}
    with pytest.raises(NotFound) as e:
        _parse(urn, d)
    assert "only metadata" in str(e.value) and "legis.senado.leg.br/norma/527942" in str(e.value)


def test_flat_compilation_parse():
    """Metadata-only norms (CP, CDC...) are parsed from the Câmara 'Compilação Monovigente' HTML."""
    from world_legal_mcp.jurisdictions.br import _parse_flat
    page = ("<p>Decreto enacting</p><p>Art. 1º Aprovado.</p><p>Rio de Janeiro, 7 de dezembro de 1940</p>"
            "<p>TÍTULO I</p><p>DA VIDA</p><p>Homicídio simples</p><p>Art. 121. Matar alguém:</p>"
            "<p>Pena - reclusão, de seis a vinte anos.</p><p>Caso de diminuição</p>"
            "<p>§ 1 º Se o agente comete o crime:</p><p>Art. 121-A. Novo.</p>")
    law = _parse_flat("urn:x", {"headline": "DL 1"}, page, "https://legis.senado.leg.br/norma/1")
    assert list(law["flat"]) == ["Art. 121", "Art. 121-A"]
    assert law["flat"]["Art. 121"] == ("**Art. 121** Matar alguém:\n\nPena - reclusão, de seis a vinte anos.\n\n"
                                       "§ 1º Se o agente comete o crime:")
    assert law["keys"]["121"] == "Art. 121"
    assert [e.title for e in law["toc"]][0] == "TÍTULO I – DA VIDA"


def test_caselaw_note_says_stj_unavailable(monkeypatch):
    import asyncio
    from world_legal_mcp.jurisdictions import br

    async def fake(body):
        return {"hits": [], "total": {"value": 0}}
    monkeypatch.setattr(br, "_stf", fake)
    res = asyncio.run(br.Brazil().search_caselaw("dano moral consumidor"))
    assert "STJ" in res.note and "NOT available" in res.note
