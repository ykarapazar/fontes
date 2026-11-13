"""Offline tests for the Bedesten legislation side of the Turkey adapter. Fixtures in
tests/fixtures/tr were recorded live (2026-11-11); fulltext_1136_header.json is the real
getDocumentContent reply for Law 1136 cut after the header (and its <style> block)."""
import json
from pathlib import Path

import httpx
import pytest

from world_legal_mcp import _http
from world_legal_mcp.jurisdictions import tr

FIX = Path(__file__).parent / "fixtures" / "tr"


def _fix(name):
    return json.loads((FIX / name).read_text(encoding="utf-8"))


class Bedesten:
    def __init__(self):
        self.bodies: list[tuple[str, dict]] = []

    def __call__(self, req: httpx.Request) -> httpx.Response:
        path, data = req.url.path, json.loads(req.content)["data"]
        self.bodies.append((path, data))
        if path == "/mevzuat/searchDocuments":
            if data.get("mevzuatAdi") == "Avukatlık Kanunu" or data.get("mevzuatNo") == "1136":
                return httpx.Response(200, json=_fix("search_avukatlik_kanunu.json"))
            if data.get("mevzuatAdi") == "Meslek Kuralları":
                return httpx.Response(200, json=_fix("search_title_meslek_kurallari.json"))
            if data.get("phrase") == '"Meslek Kuralları"':
                return httpx.Response(200, json=_fix("search_phrase_meslek_kurallari.json"))
            return httpx.Response(500)   # an unquoted OR-ed phrase search would land here
        if path == "/mevzuat/mevzuatMaddeTree" and data["mevzuatId"] == "103689":
            return httpx.Response(200, json=_fix("tree_1136.json"))
        if path == "/mevzuat/getDocumentContent":
            if data["documentType"] == "MEVZUAT" and data["id"] == "103689":
                return httpx.Response(200, json=_fix("fulltext_1136_header.json"))
            if data["documentType"] == "MADDE" and data["id"] in ("1665927", "1701074"):
                return httpx.Response(200, json=_fix(f"madde_{data['id']}.json"))
        return httpx.Response(404)


@pytest.fixture
def bed(monkeypatch):
    mock = Bedesten()
    monkeypatch.setattr(_http, "_client", httpx.AsyncClient(transport=httpx.MockTransport(mock)))
    monkeypatch.setattr(_http, "_intervals", {})
    for cache in (tr._laws, tr._trees, tr._fulltexts):
        cache.clear()
    return mock


async def test_search_fills_missing_gazette_date(bed):
    res = await tr.Turkey().search_legislation("Avukatlık Kanunu", limit=3, page=1, filters={})
    law, kky = res.items
    # Bedesten's index has resmiGazeteTarihi null for 1136; the date is in the text header
    assert law.id == "1.5.1136" and law.date == "1969-04-07"
    assert law.snippet == "Resmî Gazete 1969-04-07, sayı 13168"
    assert kky.date == "2002-06-19"


async def test_provision_uses_current_article_not_stale_copy(bed):
    p = await tr.Turkey().get_legislation_provision("1.5.1136", "12")
    # the tree also holds a 2024 copy of md.12 whose page footnotes are about Law 7249 (staj)
    assert ("MADDE", "1701074") in [(d.get("documentType"), d.get("id")) for _, d in bed.bodies]
    assert "arabuluculuk" in p.text and "7249" not in p.text
    assert p.as_of == "2026-07-21"


async def test_toc_has_no_stale_duplicates(bed):
    toc = await tr.Turkey().get_legislation_toc("1.5.1136")
    labels = [e.provision for e in toc.entries if e.provision]
    assert labels.count("Madde 12") == 1 and len(labels) == len(set(labels))
    assert labels.index("Madde 11") < labels.index("Madde 12") < labels.index("Madde 15")
    assert labels[-1] == tr.DIGER


async def test_no_title_match_falls_back_to_exact_phrase_with_hint(bed):
    res = await tr.Turkey().search_legislation("Meslek Kuralları", limit=5, page=1, filters={})
    phrases = [d.get("phrase") for p, d in bed.bodies if "phrase" in d]
    assert phrases == ['"Meslek Kuralları"']
    assert res.total == 64
    assert "exact phrase" in res.note and "TBB Meslek Kuralları" in res.note
    assert any("TBB Meslek Kuralları" in g for g in tr.Turkey.gaps)


def _law(no, name, tur="KANUN"):
    return {"mevzuatId": f"m{no}", "mevzuatNo": no, "mevzuatAdi": name, "mevzuatTertip": 5,
            "mevzuatTur": {"id": 1, "name": tur}, "resmiGazeteTarihi": "1982-11-09T00:00:00"}


def _mock(monkeypatch, handler):
    monkeypatch.setattr(_http, "_client", httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    monkeypatch.setattr(_http, "_intervals", {})
    for cache in (tr._laws, tr._trees, tr._fulltexts):
        cache.clear()


async def test_anayasa_puts_constitution_first(monkeypatch):
    def handler(req):
        d = json.loads(req.content)["data"]
        if d.get("mevzuatAdi") == "Anayasası":
            return httpx.Response(200, json={"data": {"mevzuatList": [_law("2709", "TÜRKİYE CUMHURİYETİ ANAYASASI")], "total": 1}})
        return httpx.Response(200, json={"data": {"mevzuatList": [_law("6216", "ANAYASA MAHKEMESİNİN KURULUŞU")], "total": 1}})
    _mock(monkeypatch, handler)
    res = await tr.Turkey().search_legislation("Anayasa", limit=5, page=1, filters={})
    assert [h.number for h in res.items] == ["2709", "6216"] and res.total == 2


async def test_no_fulltext_note_when_nothing_found(monkeypatch):
    _mock(monkeypatch, lambda req: httpx.Response(200, json={"data": {"mevzuatList": [], "total": 0}}))
    res = await tr.Turkey().search_legislation("Kanun", limit=5, page=1, filters={"number": "7555"})
    assert res.total == 0 and "full-text" not in res.note


async def test_caselaw_date_order_note(monkeypatch):
    _mock(monkeypatch, lambda req: httpx.Response(200, json={"data": {"emsalKararList": [], "total": 0}}))
    r = await tr.Turkey().search_caselaw("tahliye", limit=5, page=1, filters={"court": "istinaf_hukuk"})
    assert "no relevance" in r.note
    r = await tr.Turkey().search_caselaw("tahliye", limit=5, page=1, filters={"sort": "source"})
    assert "no relevance" not in r.note


def test_decision_date_label_is_the_karar_tarihi_not_the_lower_court_date():
    pars = ["T.C.", "TARİHİ : 04/11/2025", "DAVA : Şirketin Feshi", "KARAR TARİHİ : 05/11/2026"]
    assert tr._decision_date_label(pars) == "2026-11-05"
    assert tr._decision_date_label(["TARİHİ : 04/11/2025"]) == ""


@pytest.mark.parametrize("q,want", [('"tahliye" "kira"', '+"tahliye" +"kira"'),
                                    ('"kira tespiti" dava', '"kira tespiti"'),  # 'dava' is in nearly every decision: dropped
                                    ("kira tespiti", "+kira +tespiti"),
                                    ('"kira tespiti"', '"kira tespiti"'),
                                    ('"tahliye" OR "kira"', '"tahliye" OR "kira"')])
async def test_caselaw_requires_every_term_and_phrase(monkeypatch, q, want):
    sent = []

    def handler(req):
        sent.append(json.loads(req.content)["data"]["phrase"])
        return httpx.Response(200, json={"data": {"emsalKararList": [], "total": 0}})
    _mock(monkeypatch, handler)
    await tr.Turkey().search_caselaw(q, limit=5, page=1, filters={})
    assert sent == [want]


async def test_caselaw_note_is_honest_about_ranking(monkeypatch):
    _mock(monkeypatch, lambda req: httpx.Response(200, json={"data": {"emsalKararList": [], "total": 0}}))
    res = await tr.Turkey().search_caselaw('"kira tespiti"', limit=5, page=1, filters={"court": "istinaf_hukuk"})
    assert "no subject search" in res.note and "do not narrow" in res.note
    assert "tahliyesine karar" not in res.note


def test_subject_is_read_from_dava_line_or_yargitay_first_sentence():
    assert tr._subject("ESAS NO : 1\nDAVA\t: Kira Bedelinin Tespiti\nKARAR") == "Kira Bedelinin Tespiti"
    assert tr._subject("<p>DAVANIN KONUSU : Alacak</p>") == "Alacak"
    y = "Taraflar arasındaki kiralananın tahliyesi davasından dolayı yapılan yargılama sonunda"
    assert tr._subject(y) == "kiralananın tahliyesi davası"
    assert tr._subject("no subject here") == ""


def test_subject_match_uses_stems_and_skips_generic_words():
    st = tr._stems("tahliye davası")
    assert st == ["tahli"]
    assert tr._subject_match("Kiralananın Tahliyesi", st)
    assert not tr._subject_match("Şirketin Feshi", st)
    assert tr._subject_match("Kira Bedelinin Tespiti", tr._stems('"kira tespiti"'))


def test_subject_from_yargitay_relief_clause():
    t = ("3. Hukuk Dairesi 2024/3413 E. I. DAVA Davacı vekili; davalının kiracı olduğunu, kira bedeli ödemediğini "
         "ileri sürerek; itirazın iptaline ve davalının kiralanandan tahliyesine karar verilmesini talep etmiştir. "
         "II. CEVAP Davalı vekili; davanın reddini istemiştir.")
    sub = tr._subject(t)
    assert sub == "Claim: itirazın iptaline ve davalının kiralanandan tahliyesine"
    assert tr._subject_match(sub, tr._stems("tahliye"))


def test_bedesten_pages_by_ten(monkeypatch):
    import asyncio
    calls = []

    async def fake(path, data, paging=False):
        calls.append(data["pageNumber"])
        assert data["pageSize"] == 10
        n = data["pageNumber"]
        return {"total": 95, "emsalKararList": [
            {"documentId": f"{n}-{i}", "itemType": {"name": "YARGITAYKARARI"}, "birimAdi": "3. Hukuk Dairesi"}
            for i in range(10 if n < 10 else 5)]}
    monkeypatch.setattr(tr, "_bpost", fake)
    r = asyncio.run(tr.Turkey()._search_bedesten("kira", [], None, 25, 2, "newest", None, None))
    # page 2 of 25 = hits 26-50 = source pages 3 (from its 6th hit), 4, 5
    assert calls == [3, 4, 5] and len(r.items) == 25 and r.items[0].id == "3-5" and r.items[-1].id == "5-9"


def test_bedesten_sort_breaks_ties_and_sends_capital_direction(monkeypatch):
    # live 2026-11-12: Bedesten ignores sortDirection "asc" (returns newest first); "ASC" works
    import asyncio
    sent = []

    async def fake(path, data, paging=False):
        sent.append(data)
        return {"total": 0, "emsalKararList": [], "mevzuatList": []}
    monkeypatch.setattr(tr, "_bpost", fake)
    asyncio.run(tr.Turkey()._search_bedesten("kira", [], None, 10, 1, "oldest", None, None))
    asyncio.run(tr.Turkey().search_legislation("borçlar", limit=5, page=1, filters={"sort": "oldest"}))
    assert sent[0]["sortFields"] == ["KARAR_TARIHI", "DOCUMENT_ID"] and sent[0]["sortDirection"] == "ASC"
    assert sent[1]["sortDirection"] == "ASC"
