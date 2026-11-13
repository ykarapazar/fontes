import asyncio

from world_legal_mcp import _http
from world_legal_mcp.jurisdictions import hr

PAGE = ('<div class="resultTitle"><a href="/clanci/sluzbeni/2026_10_128_1525.html">{t}<span>x</span>'
        '</a><div class="official-number-and-date">NN 128/2026, (1525), odluka, 30.9.2026.</div>')


def test_search_drops_non_decisions_and_sends_dates(monkeypatch):
    seen = []

    class R:
        status_code = 200
        text = ("Ukupno je pronađeno <span>5</span>"
                + PAGE.format(t="Odluka Ustavnog suda Republike Hrvatske broj: U-III-1/2020 od 30. rujna 2026.")
                + PAGE.format(t="Strategija upravljanja nekretninama"))

    async def fake(url, **kw):
        seen.append(url)
        return R()
    monkeypatch.setattr(_http, "get", fake)
    res = asyncio.run(hr.Croatia().search_caselaw(
        "zastara", filters={"date_from": "2022-01-01", "date_to": "2022-12-31"}))
    assert len(res.items) == 1 and "Ustavnog" in res.items[0].title
    assert "od=01.01.2022" in seen[0] and "do=31.12.2022" in seen[0]
    assert "Vrhovni sud" in res.note


def test_status_marks_original_vs_consolidated():
    orig = {"title": "Ustav Republike Hrvatske", "number": "NN 56/1990 (1092)", "date": "1990-12-22"}
    msg = hr.Croatia._status(orig)
    assert "ORIGINAL" in msg and "NOT the current" in msg and "2010/85/2422" in msg
    cons = {"title": "Ustav Republike Hrvatske (pročišćeni tekst)", "number": "NN 85/2010 (2422)",
            "date": "2010-07-09"}
    assert "consolidated" in hr.Croatia._status(cons) and "ORIGINAL" not in hr.Croatia._status(cons)


def test_amending_status_reports_repeal_wording():
    d = {"title": "Zakon o izmjenama i dopunama Zakona o x", "number": "NN 1/2026 (1)", "date": "2026-01-01",
         "paras": ["Članak 1.", "Danas prestaje važiti članak 5."]}
    assert "prestaje važiti članak 5" in hr.Croatia._status(d)
    d["paras"] = ["Članak 1."]
    assert "No repeal wording" in hr.Croatia._status(d)


def test_search_requests_wide_pool_then_slices(monkeypatch):
    seen = {}

    async def fake(self, q, *, limit, **kw):
        seen["limit"] = limit
        return [{"id": str(i), "title": t, "number": "", "type": "", "date": "2000-01-01",
                 "snippet": "", "url": ""} for i, t in enumerate(["Zakon o prestanku rada", "Zakon o radu"])], 2
    monkeypatch.setattr(hr.Croatia, "_search", fake)
    res = asyncio.run(hr.Croatia().search_legislation("radu", limit=1))
    assert seen["limit"] >= 60 and [h.title for h in res.items] == ["Zakon o radu"]
