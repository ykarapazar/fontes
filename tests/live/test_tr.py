"""Live smoke tests against Bedesten (mevzuat.adalet.gov.tr) and the AYM decision banks.
Needs network. Slow on purpose: Bedesten is throttled to one request per 3.5 s."""
import re

from world_legal_mcp import server


async def test_tr_caselaw_court_chamber_date():
    out = await server.search_caselaw("tr", "kira tespiti", limit=3, filters={
        "court": "yargitay", "chamber": "3. Hukuk Dairesi", "exact": "true",
        "date_from": "2024-01-01", "date_to": "2024-12-31"})
    assert "Yargıtay 3. Hukuk Dairesi" in out and "OR-ed" not in out
    dates = re.findall(r"- Date: (\d{4})", out)
    assert dates and set(dates) == {"2024"}


async def test_tr_law_id_variants_and_temporary_article():
    for law_id in ("6098", "TBK", "kanun 6098"):
        out = await server.get_legislation_provision("tr", law_id, "m. 1")
        assert "1.5.6098" in out and "Sözleşme" in out
    gec = await server.get_legislation_provision("tr", "4857", "Geçici Madde 1")
    assert "# İŞ KANUNU: Geçici Madde 1" in gec and "1475 sayılı" in gec


async def test_tr_aym_round_trip():
    out = await server.search_caselaw("tr", '"ifade özgürlüğü"', limit=2,
                                      filters={"court": "aym_bb", "date_from": "2025-01-01"})
    ids = re.findall(r'get_decision\("tr", "(aym:bb:[0-9a-f-]+)"', out)
    assert ids, out
    dec = await server.get_decision("tr", ids[0], max_chars=3000)
    assert "Anayasa Mahkemesi" in dec and "B. No:" in dec


async def test_tr_uyusmazlik_round_trip():
    out = await server.search_caselaw("tr", "kamulaştırmasız el atma", limit=2,
                                      filters={"court": "uyusmazlik"})
    ids = re.findall(r'get_decision\("tr", "(uyusmazlik:\d{4}-\d+)"', out)
    assert ids, out
    dec = await server.get_decision("tr", ids[0], max_chars=3000)
    assert "UYUŞMAZLIK" in dec.upper(), dec[:500]


async def test_tr_sayistay_daire_round_trip():
    out = await server.search_caselaw("tr", "ihale", limit=2, filters={"court": "sayistay_daire"})
    ids = re.findall(r'get_decision\("tr", "(sayistay:daire:\d+)"', out)
    assert ids, out
    dec = await server.get_decision("tr", ids[0], max_chars=3000)
    assert "Sayıştay" in dec, dec[:500]


async def test_tr_rekabet_and_gib_search():
    rek = await server.search_caselaw("tr", "Google", limit=2, filters={"court": "rekabet"})
    assert "Rekabet Kurulu" in rek and "rekabet:" in rek, rek[:500]
    gib = await server.search_caselaw("tr", "kira geliri", limit=2, filters={"court": "gib_ozelge"})
    ids = re.findall(r'get_decision\("tr", "(gib:[^"]+)"', gib)
    assert ids, gib[:500]
    assert "gelir" in (await server.get_decision("tr", ids[0], max_chars=2000)).lower()


async def test_tr_law_1136_date_as_of_and_current_article():
    out = await server.search_legislation("tr", "Avukatlık Kanunu", limit=3)
    assert "- Date: 1969-04-07" in out
    md12 = await server.get_legislation_provision("tr", "1.5.1136", "12")
    assert "- Text as of: 20" in md12 and "arabuluculuk" in md12 and "7249" not in md12
