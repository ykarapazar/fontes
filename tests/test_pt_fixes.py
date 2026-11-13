import asyncio

from world_legal_mcp.jurisdictions import pt


def _rows(dates):
    return "".join(
        f'<tr valign="top"><td>x</td><td>{d}</td><td>y</td><td>R</td><td>S{i}</td>'
        f'<a href="/jstj.nsf/abc/{i:032x}?OpenDocument">{i}/22.0T8XXX.S1</a></tr>'
        for i, d in enumerate(dates))


def test_date_sort_sorts_relevant_window_not_whole_index(monkeypatch):
    calls = []

    async def fake(court, query, *, start, count, order):
        calls.append((start, count, order))
        return "<h4>3 documents returned; 443 found</h4>" + _rows(["01/05/2023", "06/09/2025", "02/01/2024"])

    monkeypatch.setattr(pt, "_dgsi_search", fake)
    res = asyncio.run(pt.Portugal().search_caselaw("arrendamento", filters={"sort": "date"}))
    assert calls == [(1, pt._DATE_WINDOW, 1)]  # relevance window, never SearchOrder=3
    assert [h.date for h in res.items] == sorted([h.date for h in res.items], reverse=True)
    assert "most relevant" in res.note


def test_codigo_penal_maps_to_pgdl_consolidated_entry(monkeypatch):
    pt._CODE_NAMES["names"] = {"código penal de 1982 versão consolidada posterior a 1995":
                               "Código Penal de 1982 Versão consolidada posterior a 1995"}
    seen = {}

    async def fake_get(url):
        seen["url"] = url
        return "no nidlei here"

    monkeypatch.setattr(pt, "_pgdl_get", fake_get)
    asyncio.run(pt.Portugal()._code_name_hit("Código Penal"))
    assert "buscacodigo=C%F3digo%20Penal%20de%201982" in seen["url"]


def test_code_name_with_citation_and_alias_and_penal_number(monkeypatch):
    pt._CODE_NAMES["names"] = {
        "código penal de 1982 versão consolidada posterior a 1995":
            "Código Penal de 1982 Versão consolidada posterior a 1995",
        "novo regime do arrendamento urbano (nrau)": "Novo Regime do Arrendamento Urbano (NRAU)",
        "novo regime do arrendamento urbano": "Novo Regime do Arrendamento Urbano (NRAU)",
    }
    seen = []

    async def fake_get(url):
        seen.append(url)
        return 'var nidlei = "109"; <title>x</title>'

    monkeypatch.setattr(pt, "_pgdl_get", fake_get)
    hit = asyncio.run(pt.Portugal()._code_name_hit("Código Penal Decreto-Lei 400/82"))
    assert hit and hit.number == "400/82" and hit.date == "1982-09-23" and "48/95" in hit.snippet
    assert asyncio.run(pt.Portugal()._code_name_hit("arrendamento urbano"))
    assert "Arrendamento%20Urbano%20%28NRAU%29" in seen[-1]


def test_date_sort_note_warns_when_window_truncates(monkeypatch):
    async def fake(court, q, *, start, count, order):
        return "<html></html>"

    monkeypatch.setattr(pt, "_dgsi_search", fake)
    monkeypatch.setattr(pt, "_dgsi_total", lambda h: 443)
    monkeypatch.setattr(pt, "_dgsi_rows", lambda h, c: [])
    res = asyncio.run(pt.Portugal().search_caselaw("arrendamento", filters={"sort": "date"}))
    assert "NOT a complete" in res.note


def test_date_window_is_tight_enough_to_stay_on_topic():
    # 50 pulled in off-topic hits (admissibility, value of action) into the top 5 by date
    assert pt._DATE_WINDOW <= 20


def test_domino_query_leading_phrase_uses_symbols():
    assert pt._domino_query('"contrato de arrendamento" AND resolução AND [DATAAC] >= 01/01/2022') == \
        '"contrato de arrendamento" & resolução & [DATAAC] >= 01/01/2022'
    assert pt._domino_query('"a b" OR c') == '"a b" | c'
    assert pt._domino_query('"a AND b" AND c') == '"a AND b" & c'
    assert pt._domino_query('arrendamento AND "a b"') == 'arrendamento AND "a b"'


def test_strip_inline_tags_do_not_split_words():
    from world_legal_mcp.jurisdictions import pt
    assert pt._strip("Assegura a execução do<b>s</b> Regulamentos, aprova<font>do</font> em anexo") == \
        "Assegura a execução dos Regulamentos, aprovado em anexo"
    assert pt._strip("a<br>b") == "a; b"
