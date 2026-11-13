import asyncio
from types import SimpleNamespace

from world_legal_mcp.jurisdictions import iq


def _row(i, title):
    return f'<a href="/law-detail/?id={i}"><div class="ms-4"><h4>{title}</h4></div></a>'


def test_common_word_with_year_falls_back(monkeypatch):
    async def post(url, data=None, **kw):
        k = data["keyword"]
        if k == "قانون":
            return SimpleNamespace(status_code=500, text="")
        if k == "لسنة 2024":
            return SimpleNamespace(status_code=200, text=_row(1, "قانون رقم (3) لسنة 2024 قانون س") +
                                   _row(2, "نظام رقم (20) لسنة 2024 نظام ص"))
        return SimpleNamespace(status_code=200, text="")
    monkeypatch.setattr(iq._http, "post", post)
    r = asyncio.run(iq.Iraq().search_legislation("قانون", filters={"year": 2024}))
    assert [h.id for h in r.items] == ["1"]


def test_status_translated():
    assert "repealed" in iq._STATUS["هەڵوەشاوەتەوە"]


def _fake_post(monkeypatch):
    async def post(url, data=None, **kw):
        k = data["keyword"]
        if k == "قانون":
            return SimpleNamespace(status_code=500, text="")
        if k == "لسنة 2024":
            return SimpleNamespace(status_code=200, text=_row(2, "نظام رقم (20) لسنة 2024 نظام ص"))
        if k == "لسنة 2023":
            return SimpleNamespace(status_code=200, text=_row(1, "قانون رقم (3) لسنة 2023 قانون س"))
        return SimpleNamespace(status_code=200, text="")
    monkeypatch.setattr(iq._http, "post", post)


def test_empty_year_says_plainly(monkeypatch):
    _fake_post(monkeypatch)
    r = asyncio.run(iq.Iraq().search_legislation("قانون", filters={"year": 2024}))
    assert not r.items and "holds no such record" in r.note


def test_year_range(monkeypatch):
    _fake_post(monkeypatch)
    r = asyncio.run(iq.Iraq().search_legislation("قانون", filters={"year_from": 2023, "year_to": 2024}))
    assert [h.id for h in r.items] == ["1"]


def test_zero_hit_phrase_note(monkeypatch):
    _fake_post(monkeypatch)
    r = asyncio.run(iq.Iraq().search_legislation("قانون العمل رقم 71"))
    assert not r.items and "exact phrase" in r.note


def test_zero_hit_says_not_found_and_year_note_counts_languages(monkeypatch):
    _fake_post(monkeypatch)
    r = asyncio.run(iq.Iraq().search_legislation("قانون العمل رقم 71"))
    assert "Not found" in r.note and "treat it as not held" in r.note
    r = asyncio.run(iq.Iraq().search_legislation("قانون", filters={"year": 2024}))
    assert "Arabic" in r.note and "Kurdish" in r.note and "یاسا" in r.note


def test_hits_note_says_title_only(monkeypatch):
    import asyncio
    from types import SimpleNamespace
    from world_legal_mcp.jurisdictions import iq

    html = ('<a href="/law-detail/?id=1"><div class="ms-4"><h4>قانون رقم (10) لسنة 1997 '
            'قانون إيقاف العمل</h4></div></a>')

    async def fake_post(url, **kw):
        return SimpleNamespace(status_code=200, text=html)

    monkeypatch.setattr(iq._http, "post", fake_post)
    res = asyncio.run(iq.Iraq().search_legislation("العمل"))
    assert "read the titles" in res.note and "does not hold it" in res.note
