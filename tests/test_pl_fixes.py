import asyncio

import pytest
from world_legal_mcp.base import NotFound

from world_legal_mcp.jurisdictions import pl


class _R:
    def __init__(self, content):
        self.content = content


def test_decision_with_extra_result_class(monkeypatch):
    page = ('<html><body><div id="content"><h2>I C 19/26 - uzasadnienie Sąd Rejonowy w Świnoujściu '
            'z 2026-09-07</h2><div class="single_result invalid"><p>Sygn. akt I C 19/26</p>'
            '<p>Treść wyroku</p></div></div></body></html>').encode()

    async def fake(url, what, **kw):
        return _R(page)
    monkeypatch.setattr(pl, "_fetch", fake)
    d = asyncio.run(pl.Poland().get_decision("155515400000503_I_C_000019_2026_Uz_2026-09-07_001"))
    assert "Treść wyroku" in d.text and d.date == "2026-09-07"


def test_base_act_listed_first(monkeypatch):
    items = [{"ELI": "DU/2026/795", "address": "a", "type": "Obwieszczenie",
              "title": "Obwieszczenie ... jednolitego tekstu ustawy - Kodeks cywilny"},
             {"ELI": "DU/2025/1508", "address": "b", "type": "Ustawa",
              "title": "Ustawa z dnia 9 października 2025 r. o zmianie ustawy - Kodeks cywilny"},
             {"ELI": "DU/1964/93", "address": "c", "type": "Ustawa",
              "title": "Ustawa z dnia 23 kwietnia 1964 r. - Kodeks cywilny."}]

    async def fake(url, what, **kw):
        return {"items": items, "totalCount": 3}
    monkeypatch.setattr(pl, "_json", fake)
    r = asyncio.run(pl.Poland().search_legislation("Kodeks cywilny", limit=2))
    assert [h.id for h in r.items][0] == "DU/1964/93" and len(r.items) == 2


def test_pdf_only_act_is_read_from_pdf_text(monkeypatch):
    raw = ("Dziennik Ustaw Nr 78 - 2415 -\nRozdział I\nRZECZPOSPOLITA\nArt. 1.\nRzeczpospolita jest dobrem.\n"
           "Poz. 483\nRozdział II\nWOLNOŚCI\nZasady ogólne\nArt. 32.\n1. Wszyscy są wobec prawa rów\xad\nni.\n"
           "2. Nikt nie może być dyskryminowany.")

    async def fake_fetch(url, what, **kw):
        return _R(b"%PDF")

    async def fake_json(url, what, **kw):
        return {"title": "Konstytucja.", "address": "WDU19970780483", "textHTML": False,
                "announcementDate": "1997-04-02"}
    monkeypatch.setattr(pl, "_fetch", fake_fetch)
    monkeypatch.setattr(pl, "_json", fake_json)
    monkeypatch.setattr(pl._http, "pdf_text", lambda data: raw)
    pl._laws.clear()
    p = pl.Poland()
    prov = asyncio.run(p.get_legislation_provision("DU/1997/483", "art. 32"))
    assert "Wszyscy są wobec prawa równi." in prov.text and "Dziennik" not in prov.text
    assert "amendments are NOT applied" in prov.text
    toc = asyncio.run(p.get_legislation_toc("DU/1997/483"))
    assert [e.provision for e in toc.entries if e.provision] == ["art. 1", "art. 32"]
    assert "Rozdział II - WOLNOŚCI" in [e.title for e in toc.entries]
    assert "Rzeczpospolita jest dobrem." in asyncio.run(p.get_legislation_text("DU/1997/483")).text
    pl._laws.clear()


def test_no_article_pdf_says_id_is_not_an_act(monkeypatch):
    async def fake_fetch(url, what, **kw):
        return _R(b"%PDF")

    async def fake_json(url, what, **kw):
        return {"title": "Obwieszczenie.", "textHTML": False}
    monkeypatch.setattr(pl, "_fetch", fake_fetch)
    monkeypatch.setattr(pl, "_json", fake_json)
    monkeypatch.setattr(pl._http, "pdf_text", lambda data: "Some notice without articles")
    pl._laws.clear()
    with pytest.raises(NotFound) as e:
        asyncio.run(pl.Poland().get_legislation_provision("DU/1974/24", "18"))
    assert "search_legislation" in str(e.value) and ".pdf" not in str(e.value)
    pl._laws.clear()


def test_outdated_consolidated_text_is_flagged_up_front():
    law = pl._Law("DU/1974/141", {}, {"ELI": "DU/2023/1465", "legalStatusDate": "2023-06-13",
                                      "references": {"Tekst jednolity dla aktu": [1]}},
                  [{"ELI": "DU/2026/1245", "displayAddress": "Dz.U. 2026 poz. 1245",
                    "legalStatusDate": "2026-08-27"}], None)
    assert law.warning().startswith("**NOT THE CURRENT TEXT:**") and "2026 poz. 1245" in law.warning()


def test_pdf_act_without_articles_says_so(monkeypatch):
    async def fake(url, what, **kw):
        return _R(b"x")
    monkeypatch.setattr(pl, "_fetch", fake)
    monkeypatch.setattr(pl._http, "pdf_text", lambda c: "Some decree text\nwithout articles")
    with pytest.raises(NotFound) as e:
        asyncio.run(pl._pdf_law("DU/1974/24", {"title": "Rozporządzenie X."}))
    msg = str(e.value)
    assert "real act (Rozporządzenie X)" in msg and "journal-issue" not in msg


def test_caselaw_pages_slice_and_tie_note(monkeypatch):
    asked = []

    async def fake(self, query, filters, page):
        asked.append(page)
        return [f"h{i}" for i in range((page - 1) * 10, page * 10)], 95
    monkeypatch.setattr(pl.Poland, "_search_page", fake)
    r = asyncio.run(pl.Poland().search_caselaw("umowa najmu", limit=15, page=2, filters={}))
    assert asked == [2, 3] and r.items == [f"h{i}" for i in range(15, 30)] and r.total == 95
    assert "tied hits" in r.note
