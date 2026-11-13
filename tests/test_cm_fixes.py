import asyncio

from world_legal_mcp.jurisdictions import cm
from world_legal_mcp.models import DecisionHit


def _hit(i):
    return DecisionHit(id=i, title=i, court="", date="", case_number="", snippet="", url="")


def test_paged_drops_repeats_and_reports_total():
    pages = {0: [_hit("a"), _hit("a"), _hit("b")], 1: [_hit("b"), _hit("c")]}

    async def fetch(n):
        return pages.get(n, []), len(pages.get(n, []))

    items, total = asyncio.run(cm._paged(fetch, 1, 10, 3))
    assert [h.id for h in items] == ["a", "b", "c"]
    assert total == 3


def test_search_note_and_zero_total(monkeypatch):
    async def fake(fetch, page, limit, size):
        return [], 0
    monkeypatch.setattr(cm, "_paged", fake)
    r = asyncio.run(cm.Cameroon().search_caselaw("zzz", filters={"language": "en"}))
    assert r.total == 0 and "no date filter" in r.note
    r = asyncio.run(cm.Cameroon().search_legislation("travail"))
    assert "Labour Code" in r.note and "1828" in r.note


def test_scan_hit_flagged_and_note_warns(monkeypatch):
    async def fake(fetch, page, limit, size):
        return [cm.LawHit(id="1828", title="Loi 2016/007 portant Code Pénal", type="Loi", number="",
                          date="2016-07-12", snippet="", url=""),
                cm.LawHit(id="353", title="Décret 2013/288", type="Décret", number="",
                          date="2013-09-04", snippet="", url="")], 2
    monkeypatch.setattr(cm, "_paged", fake)
    r = asyncio.run(cm.Cameroon().search_legislation("Code pénal"))
    assert "scan" in r.items[0].snippet and r.items[1].snippet == ""
    assert "unrelated" in r.note


def test_provision_warns_text_is_as_signed(monkeypatch):
    async def fake(id):
        return {"id": "170", "title": "Loi 2013/004", "source": "html", "url": "u", "pdf": "", "date": "2013-04-18",
                "text": "**Article 1er :** Texte.\n\n**Article 2 :** Autre."}
    monkeypatch.setattr(cm, "_act", fake)
    p = asyncio.run(cm.Cameroon().get_legislation_provision("170", "1"))
    assert "not consolidated" in p.text and "amending" in p.text and "Texte" in p.text


def test_provision_names_amending_act(monkeypatch):
    from world_legal_mcp.models import LawHit

    async def fake(id):
        return {"id": "170", "title": "Loi N° 2013 / 004 du 18 avril 2013 fixant les incitations", "source": "html",
                "url": "u", "pdf": "", "date": "2013-04-18", "text": "**Article 1er :** Texte."}

    async def page(q, cat, n):
        mk = lambda i, t: LawHit(id=i, title=t, type="Loi", number="", date="", snippet="", url="")
        return [mk("170", "Loi N° 2013 / 004 du 18 avril 2013 fixant les incitations"),
                mk("2349", "Loi N° 2017/015 du 12 juillet 2017 modifiant et complétant certaines dispositions de la "
                           "loi N° 2013/004 du 18 avril 2013 fixant les incitations"),
                mk("365", "DECRET N°2013/297 modifiant le décret n°2013/092")], 3
    monkeypatch.setattr(cm, "_act", fake)
    monkeypatch.setattr(cm, "_prc_page", page)
    p = asyncio.run(cm.Cameroon().get_legislation_provision("170", "1"))
    assert "2017/015" in p.text and "id 2349" in p.text and "365" not in p.text
