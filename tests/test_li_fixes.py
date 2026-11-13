import asyncio

from world_legal_mcp.jurisdictions import li

HTML = """<html><body>
<div class="tit1">Inhaltsverzeichnis</div>
<div class="tits"><a name="tits:1"></a>Allgemeiner Teil</div>
<div class="art"><a name="par:1"></a>&sect; 1<div class="sacht">Keine Strafe</div><div class="abs">Text eins.</div></div>
<div class="tits"><a name="tits:1"></a>Besonderer Teil</div>
<div class="art"><a name="par:107"></a>&sect; 107<div class="sacht">Gefaehrliche Drohung</div><div class="abs">Text.</div></div>
<div class="tits">Uebergangsbestimmungen</div>
<div class="art"><a name="par:999"></a>&sect; 999<div class="abs">nein</div></div>
</body></html>"""


def test_parts_do_not_cut_off_provisions():
    law = li._parse_text(HTML)
    assert "§ 107" in law["provisions"] and "§ 1" in law["provisions"]
    assert "§ 999" not in law["provisions"]
    assert any("§ 107" in e.title for e in law["toc"])


ITEMS = [{"id": str(y), "az": f"01 CG.{y}.1", "label": "", "type": "", "date": f"{y}-05-01",
          "tags": ["Schadenersatz"], "url": "u"} for y in (2020, 2022, 2023, 2025)]


def _search(query, year, monkeypatch):
    async def fake():
        return ITEMS
    monkeypatch.setattr(li, "_ogh_load", fake)
    return asyncio.run(li.Liechtenstein().search_caselaw(query, limit=10, page=1, filters={"year": year}))


def test_year_range_filter(monkeypatch):
    res = _search("Schadenersatz", "2022-2025", monkeypatch)
    assert [h.date[:4] for h in res.items] == ["2022", "2023", "2025"]


def test_range_in_query_explained(monkeypatch):
    res = _search("2022-2025 Schadenersatz", "", monkeypatch)
    assert not res.items and "year filter" in res.note
