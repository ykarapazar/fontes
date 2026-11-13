import asyncio

import httpx

from world_legal_mcp.jurisdictions import bo


def test_case_notes():
    n = bo._case_notes("Corte Suprema de Justicia sentencia", False)
    assert "Supreme Court" in n and "not in this source" in n
    assert "cannot find a resolution by its number" in bo._case_notes("SAP-S2-0086-2025", False)
    assert "no date filter" in bo._case_notes("servidumbre 2022", False)
    assert bo._case_notes("servidumbre", False) == ""


def test_search_retries_dropped_connection(monkeypatch):
    bo._csrf.clear(); bo._searches.clear()
    calls = []

    async def token(refresh=False):
        return "t"

    async def post(url, **kw):
        calls.append(1)
        if len(calls) == 1:
            raise httpx.RemoteProtocolError("Server disconnected")
        return httpx.Response(200, text='<table class="table-striped"></table>')

    monkeypatch.setattr(bo, "_token", token)
    monkeypatch.setattr(bo._http, "post", post)
    assert asyncio.run(bo._search("desalojo", "5")) == []
    assert len(calls) == 2


def test_year_like_law_number_notes():
    assert "no date filter" in bo._dip_note("2023", "ley 2023")
    assert "scans" in bo._dip_note("1512", "ley 1512")
    assert "no date filter" not in bo._dip_note("1512", "ley 1512")


def test_body_date_warning():
    md = "# LEY DE 31 DE MAYO DE 2023\n\ntexto"
    assert "2023-05-31" in bo._body_date_warning("Ley Nº 1512, 2 de junio de 2023", md)
    assert bo._body_date_warning("Ley Nº 1512, 31 de mayo de 2023", md) == ""


def test_scan_falls_back_to_lexivox(monkeypatch):
    async def scan(n):
        raise bo._Scan("scan")

    async def norm(lid):
        return "Ley Nº 1512, 2 de junio de 2023", "**Artículo Único.-**\n\ntexto"

    monkeypatch.setattr(bo, "_law_text", scan)
    monkeypatch.setattr(bo, "_lx_norm", norm)
    t = asyncio.run(bo.Bolivia().get_legislation_text("1512"))
    assert t.id == "BO-L-N1512" and "texto" in t.text
    assert "open a law to see its date" in bo._dip_note("2023", "ley 2023")


def test_constitutional_court_note_and_abrogation_date():
    assert "Constitutional Court" in bo._case_notes("acción de inconstitucionalidad", False)
    assert "Constitutional Court" not in bo._case_notes("servidumbre", False)
    assert bo._abro_before("2/jun/2014", "2015-08-07")
    assert not bo._abro_before("2/jun/2016", "2015-08-07")


def test_slug_note_flags_mismatched_register_link():
    bad = {"link": "https://diputados.gob.bo/leyes/plp-ley-s-n-1513/", "acf": {"ley_nro": "PLP LEY S N° 1510"}}
    ok = {"link": "https://diputados.gob.bo/leyes/plp-ley-d-n-1513/", "acf": {"ley_nro": "PLP LEY D N° 1513"}}
    assert "Ley N° 1510 (link ends in 1513)" in bo._slug_note([bad, ok])
    assert bo._slug_note([ok]) == ""
