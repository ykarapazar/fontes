import pytest

from world_legal_mcp.jurisdictions import icj
from world_legal_mcp.base import BadRequest


def _adapter():
    return icj.Adapter() if hasattr(icj, "Adapter") else next(
        v for v in vars(icj).values() if isinstance(v, type) and hasattr(v, "search_caselaw") and v.__module__ == icj.__name__)()


async def _run(monkeypatch, filters):
    seen = []

    async def fake_page(self, params):
        seen.append(params)
        return [], 0

    async def fake_opt(n):
        return "5177"

    cls = type(_adapter())
    monkeypatch.setattr(cls, "_search_page", fake_page)
    monkeypatch.setattr(icj, "_case_option", fake_opt)
    await _adapter().search_caselaw("x", filters=filters)
    return seen[0]


async def test_default_type_includes_orders(monkeypatch):
    p = await _run(monkeypatch, {})
    assert p["field_document_group_type"] == "493"


async def test_provisional_measures_keeps_orders(monkeypatch):
    p = await _run(monkeypatch, {"proceedings": "provisional_measures"})
    assert (p["field_document_group_type"], p["field_doc_incidental_proceedings"]) == ("493", "409")


async def test_case_filter(monkeypatch):
    p = await _run(monkeypatch, {"case": "178"})
    assert p["case_selection"] == "2" and p["field_doc_case_code_1[]"] == ["5177"]


async def test_case_filter_must_be_number(monkeypatch):
    with pytest.raises(BadRequest):
        await _run(monkeypatch, {"case": "gambia"})


async def test_query_naming_a_case_restricts_to_it(monkeypatch):
    icj._case_ids.clear(); icj._case_names.clear()
    icj._case_ids.update({"178": "5177", "70": "5051", "182": "9"})
    icj._case_names.update({"178": "Application of the Convention on the Prevention and Punishment of the Crime of Genocide  (The Gambia v. Myanmar)",
                            "70": "Military and Paramilitary Activities in and against Nicaragua (Nicaragua v. United States of America)",
                            "182": "Allegations of Genocide under the Convention on Genocide (Ukraine v. Russian Federation)"})
    icj._case_ids.update({"91": "1", "118": "2"})
    icj._case_names.update({"91": "Genocide Convention (Bosnia v. Serbia)", "118": "Genocide Convention (Croatia v. Serbia)"})
    try:
        assert await icj._match_cases("Gambia Myanmar Rohingya") == ["178"]
        assert await icj._match_cases("Nicaragua United States military and paramilitary activities judgment") == ["70"]
        assert await icj._match_cases("genocide convention judgment") == []   # too many cases / too loose
        p = await _run(monkeypatch, {})
        assert "field_doc_case_code_1[]" not in p      # query "x" names nothing
    finally:
        icj._case_ids.clear(); icj._case_names.clear()


async def test_judgment_before_orders_in_one_case(monkeypatch):
    from world_legal_mcp.models import DecisionHit
    def h(i):
        return DecisionHit(id=i, title="t", court="c", date="2020-01-01", case_number="178", snippet="", url="u")
    rows = [h("178-20250725-ord-01-00"), h("178-20220722-jud-01-00"), h("178-20210101-ord-01-00")]

    async def fake_page(self, params):
        return rows, 3

    async def fake_opt(n):
        return "5177"
    monkeypatch.setattr(type(_adapter()), "_search_page", fake_page)
    monkeypatch.setattr(icj, "_case_option", fake_opt)
    r = await _adapter().search_caselaw("x", filters={"case": "178"})
    assert r.items[0].id == "178-20220722-jud-01-00"


async def test_four_same_title_cases_still_match(monkeypatch):
    icj._case_ids.clear(); icj._case_names.clear()
    for n in ("115", "116", "117", "126"):
        icj._case_ids[n] = n
        icj._case_names[n] = "Armed Activities on the Territory of the Congo (X v. Y)"
    icj._case_ids["9"] = "9"; icj._case_names["9"] = "Other"
    try:
        assert sorted(await icj._match_cases("Armed Activities on the Territory of the Congo reparations")) == ["115", "116", "117", "126"]
    finally:
        icj._case_ids.clear(); icj._case_names.clear()


_STATUTE = """<html><body><main><div class="manila"><h1>STATUTE</h1>
<h5>Article 1</h5><p>Established.</p><h5>Article 38</h5><p>1. The Court shall apply: custom.</p>
<ol><li>conventions</li></ol><h5>CHAPTER III</h5><h5>Article 39</h5><p>Languages.</p></div></main></body></html>"""


@pytest.mark.asyncio
async def test_statute_provision_and_search(monkeypatch):
    class R:
        status_code = 200
        headers = {}
        text = _STATUTE

    async def fake_get(url, **kw):
        return R()
    icj._law_cache.clear()
    monkeypatch.setattr(icj._http, "get", fake_get)
    a = icj.ICJ()
    p = await a.get_legislation_provision("Statute of the International Court of Justice", "38")
    assert p.provision == "Article 38" and "custom" in p.text and "conventions" in p.text
    res = await a.search_legislation("Statute of the International Court of Justice", limit=10, page=1, filters={})
    assert [h.id for h in res.items] == ["statute"]
    res = await a.search_legislation("languages", limit=10, page=1, filters={})
    assert res.items and "Article 39" in res.items[0].snippet
    icj._law_cache.clear()
