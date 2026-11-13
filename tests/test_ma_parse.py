from world_legal_mcp.jurisdictions import ma


def _toc(text):
    entries, blocks, _ = ma._parse(text)
    return [e.provision for e in entries if e.provision], blocks


def test_crossref_line_is_not_heading():
    toc, blocks = _toc("المادة 57\nنص\nالمادة 58\nنص أول\nالمادة 53 أعلاه.\nالمادة 59\nنص")
    assert toc == ["المادة 57", "المادة 58", "المادة 59"]
    assert blocks["المادة 58"].endswith("المادة 53 أعلاه.")


def test_restart_still_headings():
    toc, _ = _toc("المادة 1\nأ\nالمادة 2\nب\nالمادة 1\nج\nالمادة 2\nد")
    assert toc == ["المادة 1", "المادة 2", "المادة 1 (2)", "المادة 2 (2)"]


def test_norm_prov_trailing_punct():
    for p in ("المادة 586.", "المادة 586 .", "المادة 586 ـ", "المادة 586؛"):
        assert ma._norm_prov(p) == ("المادة", "586", "")
    assert ma._norm_prov("المادة 586 مكرر")[2] == "مكرر"


def test_title_date():
    assert ma._title_date("صادر في 14 من رجب 1424 (11 سبتمبر 2003)") == "2003-09-11"
    assert ma._title_date("بتاريخ 24 شوال 1397 (8 أكتوبر 1977)") == "1977-10-08"
    assert ma._title_date("صادر في 7 شوال 1436 (24 يوليو ‎ (2015‏بتحديد") == "2015-07-24"
    assert ma._title_date("الصادر في 7 شوال 1436 (24 يوليو 2015)") == ""


def test_forward_crossref_and_from():
    toc, blocks = _toc("الفصل 4\nنص\nالفصل 5 أدناه.\nالفصل 5\nنص\nالفصل 6 من هذا القانون")
    assert toc == ["الفصل 4", "الفصل 5"]
    assert "الفصل 5 أدناه." in blocks["الفصل 4"]


def test_toc_then_body_keeps_all():
    toc, _ = _toc("المادة 1\nالمادة 2\nالمادة 3\nالمادة 1\nأ\nالمادة 2\nب\nالمادة 3\nج")
    assert len(toc) == 6


def test_norm_prov_dup_suffix():
    for p in ("2 (2)", "art. 2 (2)", "المادة 2(2)", "المادة 2 (2)"):
        assert ma._norm_prov(p)[1:] == ("2", "(2)")
    assert ma._norm_prov("المادة 5 مكرر (2)")[1:] == ("5", "مكرر (2)")


def test_wrapped_crossrefs_not_headings():
    for tail in ("المادة 9 المشار إليها أعلاه.", "المادة 4 المذكورة.", "المادة 4 الأعلاه", "المادة 53 السالفة الذكر"):
        toc, blocks = _toc(f"المادة 3\nنص\n{tail}\nالمادة 4\nنص")
        assert toc == ["المادة 3", "المادة 4"] and tail in blocks["المادة 3"]


def test_mukarrara_suffix_whole():
    from world_legal_mcp.jurisdictions.ma import _ART, _norm_prov
    assert _ART.match("المادة 5 مكررة").groups()[2:] == ("مكررة", "")
    assert _norm_prov("المادة 5 مكررة (2).") == ("المادة", "5", "مكررة (2)")


def test_minhu_alladhi_crossrefs():
    from world_legal_mcp.jurisdictions.ma import _XREF
    assert _XREF.match("منه.") and _XREF.match("التي تنص") and not _XREF.match("منهجية")


# ---- caselaw year filter and error naming (no network)
import asyncio

import httpx
import pytest

from world_legal_mcp import _http
from world_legal_mcp.base import AdapterError


class _R:
    status_code = 200

    def __init__(self, rows):
        self._rows = rows

    def json(self):
        return {"recordsFiltered": 99, "data": self._rows}


def _row(i, date):
    return {"iddecision": i, "numerodecision": f"{i}/26", "datedecision": date + "T00:00:00"}


def test_caselaw_year_filter(monkeypatch):
    rows = [_row(5, "2024-03-01"), _row(4, "2023-01-01"), _row(3, "2022-06-01"), _row(2, "2021-12-31")]

    async def post(url, data=None, **kw):
        s, n = int(data["start"]), int(data["length"])
        return _R(rows[s:s + n])

    monkeypatch.setattr(_http, "post", post)
    res = asyncio.run(ma.Morocco().search_caselaw("x", filters={"year_from": "2022", "year_to": "2023"}))
    assert [i.id for i in res.items] == ["4", "3"] and res.total == 2
    res = asyncio.run(ma.Morocco().search_caselaw("x", limit=2))
    assert len(res.items) == 2 and res.total == 99
    with pytest.raises(Exception):
        asyncio.run(ma.Morocco().search_caselaw("x", filters={"year_from": "2024", "year_to": "2020"}))


def test_unreachable_names_only_failing_source(monkeypatch):
    async def get(*a, **kw):
        raise httpx.ConnectTimeout("")

    monkeypatch.setattr(_http, "get", get)
    ma._search_cache.clear()
    with pytest.raises(AdapterError) as e:
        asyncio.run(ma.Morocco().search_legislation("x"))
    assert "adala.justice.gov.ma" in str(e.value) and "cour-constitutionnelle" not in str(e.value)
