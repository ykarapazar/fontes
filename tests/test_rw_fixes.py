import asyncio

import pytest

from world_legal_mcp.base import BadRequest
from world_legal_mcp.jurisdictions import rw


def _hit(i, num, date, name="A v B", court="Supreme Court"):
    return {"_source": {"document_id": i, "file_id": i + 1, "document_name": name, "document_case_no": num,
                        "document_collection_name": court, "document_date": date}}


def _patch(monkeypatch, rows, seen=None):
    async def fake(query, limit, page, params):
        if seen is not None:
            seen.append((query, limit, dict(params)))
        return rows, len(rows)
    monkeypatch.setattr(rw, "_search", fake)


def _run(coro):
    return asyncio.run(coro)


def test_year_range_params():
    q = {}
    rw._year({"year": "2022-"}, q)
    assert q == {"startDate": "2022-01-01"}
    q = {}
    rw._year({"year": "2022-2024"}, q)
    assert q == {"startDate": "2022-01-01", "endDate": "2024-12-31"}
    q = {}
    rw._year({"year": "2022"}, q)
    assert q == {"year": "2022"}
    with pytest.raises(BadRequest):
        rw._year({"year": "2024-2022"}, {})
    with pytest.raises(BadRequest):
        rw._year({"year": "abc"}, {})


def test_duplicates_collapsed_and_bad_date_blanked(monkeypatch):
    _patch(monkeypatch, [_hit(1, "RS/X 1/2019/SC", "2022-07-22"), _hit(2, "RS/X 1/2019/SC", "2022-07-22"),
                         _hit(3, "RAD 00002/2020/CA", "1921-03-31", "C v D")])
    res = _run(rw.RW().search_caselaw("contract"))
    assert [h.id for h in res.items] == ["1", "3"]
    assert "also uploaded as id 2" in res.items[0].snippet
    assert res.items[1].date == ""
    assert "portal error" in res.note


def test_case_number_query_keeps_exact_match(monkeypatch):
    seen = []
    _patch(monkeypatch, [_hit(1, "RS/INJUST/RSOC 00002/2022/SC", "2022-10-21"),
                         _hit(9990, "RS/INJUST/RSOC 00001/2019/SC", "2020-01-31")], seen)
    res = _run(rw.RW().search_caselaw("RS/INJUST/RSOC 00001/2019/SC"))
    assert [h.id for h in res.items] == ["9990"]
    assert seen[0][2]["startDate"] == "2019-01-01" and seen[0][1] == 50


def test_decision_date_taken_from_header(monkeypatch):
    f = {"id": 5, "languages": "en", "document": {"section": "2.1", "name": "U v H", "case_no": "RS/INJUST/RAD 00002/2020/CA",
                                                   "date": "1921-03-31", "collection": {"name_en": "Court of Appeal"}}}

    async def fake_file(did):
        return f

    async def fake_pdf(fid, url):
        return b""
    monkeypatch.setattr(rw, "_file", fake_file)
    monkeypatch.setattr(rw, "_pdf", fake_pdf)
    monkeypatch.setattr(rw._http, "pdf_text", lambda b: "[Rwanda COURT OF APPEAL - X - March 31, 2021]\nbody")
    rw._decisions.clear()
    d = _run(rw.RW().get_decision("8303"))
    assert d.date == "2021-03-31" and "wrong" in d.metadata["Date note"]


def test_penal_code_hint(monkeypatch):
    seen = []
    _patch(monkeypatch, [], seen)
    res = _run(rw.RW().search_legislation("Penal Code"))
    assert seen[0][0] == "offences and penalties in general" and "68/2018" in res.note
    res = _run(rw.RW().search_legislation("Civil Code"))
    assert seen[1][0] == "Civil Code" and "4551" in res.note


def test_provision_has_amendment_note(monkeypatch):
    async def fake_law(self, id):
        return {"id": "1", "title": "T", "url": "u", "arts": {"43": "Article 43"}, "meta": {"Gazette date": "2018-09-06"}}
    monkeypatch.setattr(rw.RW, "_law", fake_law)
    p = _run(rw.RW().get_legislation_provision("1", "43"))
    assert "Amending laws are separate" in p.text


def test_copies_folded_across_pages_and_trailing_punct(monkeypatch):
    rows = [_hit(1, "RS/INJUST/RC 00001/2022/SC", "2022-03-18", "A v B"),
            _hit(3, "RS/INJUST/RC 00001/2022/SC,", "2022-03-18", "A v B"),
            _hit(5, "RS/INJUST/RC 00002/2022/SC", "2022-04-18", "C v D"),
            _hit(7, "RS/INJUST/RC 00003/2022/SC–", "2022-05-18", "E v F"),
            _hit(9, "RS/INJUST/RC 00003/2022/SC", "2022-05-18", "E v F")]
    _patch(monkeypatch, rows)
    r = _run(rw.RW().search_caselaw("contract", limit=2, page=1))
    assert r.total == 3 and [h.id for h in r.items] == ["1", "5"]
    r = _run(rw.RW().search_caselaw("contract", limit=2, page=2))
    assert [h.id for h in r.items] == ["7"]


def test_case_number_page2_empty_and_window_noted(monkeypatch):
    rows = [_hit(1, "RS/INJUST/RSOC 00001/2019/SC", "2020-01-31"),
            _hit(3, "RS/INJUST/RSOC 00001/2019/SC", "2020-01-31", "A v B en")]
    seen = []
    _patch(monkeypatch, rows, seen)
    r = _run(rw.RW().search_caselaw("RS/INJUST/RSOC 00001/2019/SC", limit=30, page=2))
    assert r.items == [] and r.total == 1
    assert seen[0][2]["endDate"] == "2022-12-31"
    r = _run(rw.RW().search_caselaw("RS/INJUST/RSOC 00001/2019/SC", limit=30))
    assert len(r.items) == 1 and "2019 to 2022" in r.note


def test_provision_names_amending_law(monkeypatch):
    async def fake(query, limit, page, params):
        return [{"_source": {"document_id": 4377, "document_date": "2023-05-30",
                             "document_name": "LAW N° 027/2023 OF 18/05/2023 AMENDING THE LAW N° 66/2018 OF 30/08/2018 REGULATING LABOUR IN RWANDA"}},
                {"_source": {"document_id": 4554, "document_date": "2018-09-06",
                             "document_name": "LAW N° 66/2018 OF 30/08/2018 REGULATING LABOUR IN RWANDA"}}], 2
    monkeypatch.setattr(rw, "_search", fake)
    am = _run(rw._amenders("LAW N° 66/2018 OF 30/08/2018 REGULATING LABOUR IN RWANDA", "4554"))
    assert [a[0] for a in am] == ["4377"]


def test_provision_quotes_amending_article(monkeypatch):
    laws = {"1": {"id": "1", "title": "LAW N° 66/2018 OF 30/08/2018 X", "url": "u", "arts": {"43": "Article 43"},
                  "meta": {"Gazette date": "2018-09-06"}},
            "9": {"id": "9", "title": "AMENDING", "url": "u", "meta": {},
                  "arts": {"2": "Article 43 of the Law n° 66/2018 is\\namended as follows: Order", "3": "other"}}}

    async def fake_law(self, id):
        return laws[str(id)]

    async def fake_am(title, own):
        return [("9", "LAW 27 AMENDING", "2023-05-30")]
    monkeypatch.setattr(rw.RW, "_law", fake_law)
    monkeypatch.setattr(rw, "_amenders", fake_am)
    p = _run(rw.RW().get_legislation_provision("1", "43"))
    assert "its article 2" in p.text and "amended as follows" in p.text and "its article 3" not in p.text


def test_amending_law_not_found_points_to_its_article(monkeypatch):
    law = {"id": "4377", "title": "LAW 027/2023 AMENDING THE LAW 66/2018", "meta": {}, "url": "u",
           "arts": {"2": "Article 2: Working hours\nArticle 43 of the Law n° 66/2018 is amended as follows:"}}

    async def fake(self, id):
        return law
    monkeypatch.setattr(rw.RW, "_law", fake)
    with pytest.raises(rw.NotFound) as e:
        _run(rw.RW().get_legislation_provision("4377", "43"))
    assert "amends article 43" in str(e.value) and "provision '2'" in str(e.value)
