import asyncio

from world_legal_mcp.jurisdictions import cz


def test_esbirka_fixed_page_size_and_slice(monkeypatch):
    asked = []

    async def fake(method, url, what, json=None, **kw):
        asked.append((json["start"], json["pocet"]))     # 'start' is a page number
        k = json["start"]
        return {"seznam": [{"kodDokumentuSbirky": f"{i}/2000 Sb.", "staleUrl": f"/x/{i}"}
                           for i in range(k * 100, k * 100 + 100)], "pocetCelkem": 1000}
    monkeypatch.setattr(cz, "_json", fake)
    r = asyncio.run(cz.Czechia().search_legislation("nájem", limit=5, page=6))    # hits 26-30
    assert asked == [(0, 100)] and [h.number for h in r.items] == [f"{i}/2000" for i in range(25, 30)]
    asked.clear()
    r = asyncio.run(cz.Czechia().search_legislation("nájem", limit=25, page=4))   # hits 76-100
    assert asked == [(0, 100)] and r.total == 1000
    asked.clear()
    r = asyncio.run(cz.Czechia().search_legislation("nájem", limit=30, page=4))   # hits 91-120
    assert asked == [(0, 100), (1, 100)]
    assert [h.number for h in r.items] == [f"{i}/2000" for i in range(90, 120)]


def _nss_html(ids):
    rows = "".join(f'<tr><td>a</td><td>b</td><td>01.01.2024</td><td>1 Afs {i}/2024</td><td>NSS</td>'
                   f'<td><a href="/DokumentOriginal/Html/{i}">x</a></td><td>g</td><td>h</td></tr>'
                   for i in ids)
    return f"<table>{rows}</table>"


def test_nss_fetches_next_source_page_when_slice_crosses_it(monkeypatch):
    pages = []

    async def form():
        return {"fields": {"textDokumentu": "t", "oznacenivecivcelku": "c", "soudsenat": "s",
                           "datumvydanirozhodnuti": "d"}, "data": [], "nss": "278"}

    async def page(method, url, what, content="", **kw):
        if "MyResTRowsCont" in url:
            k = int(dict(p.split("=", 1) for p in content.split("&"))["pageNum"])
            pages.append(k)
            return _nss_html(range(k * 40, k * 40 + 40))[7:-8]
        return ("Počet nalezených záznamů: 100 var currParams = 'p'; var currSort = 's';"
                + _nss_html(range(40)))
    monkeypatch.setattr(cz, "_nss_form", form)
    monkeypatch.setattr(cz, "_page", page)
    r = asyncio.run(cz._nss_search("x", 25, 2, {}))      # hits 26-50 span source pages 0 and 1
    assert pages == [1]
    assert [h.id for h in r.items] == [f"nssoud:{i}" for i in range(25, 50)]


def test_rozhodnuti_fixed_source_page_and_slice(monkeypatch):
    asked = []

    async def fake(method, url, what, params=None, **kw):
        p = dict(params)
        asked.append((p["limit"], p["page"]))
        k = p["page"]
        return {"items": [{"uuid": str(i), "metadata": {}} for i in range(k * 100, k * 100 + 100)],
                "totalElements": 1000}
    monkeypatch.setattr(cz, "_json", fake)
    monkeypatch.setattr(cz, "_hit", lambda i: i["uuid"])
    r = asyncio.run(cz.Czechia().search_caselaw("nájem", limit=25, page=4))   # hits 76-100
    assert asked == [(100, 0)] and r.items == [str(i) for i in range(75, 100)]
    asked.clear()
    r = asyncio.run(cz.Czechia().search_caselaw("nájem", limit=30, page=4))   # hits 91-120
    assert asked == [(100, 0), (100, 1)] and r.items == [str(i) for i in range(90, 120)]
