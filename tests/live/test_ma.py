"""Live smoke tests for Morocco: Constitutional Court site (cour-constitutionnelle.ma) and the
Ministry of Justice portal Adala (adala.justice.gov.ma). Needs network."""
import re

from world_legal_mcp import server
from world_legal_mcp.jurisdictions.ma import Morocco

DOC = Morocco.samples["law_id"]


async def test_ma_caselaw_search_institutions_and_ids():
    out = await server.search_caselaw("ma", "النظام الأساسي للقضاة", limit=12)
    assert 'get_decision("ma", "2074")' in out and "210/23" in out, out
    assert "المجلس الدستوري" in out    # pre-2017 Constitutional Council decisions are found too
    out = await server.get_decision("ma", "https://www.cour-constitutionnelle.ma/Decision?id=1199&Page=Decision",
                                    max_chars=3000)
    assert "- Identifier: 1199" in out and "21/1963" in out and "1963-06-11" in out, out
    assert "الغرفة الدستورية" in out
    assert "no decision with id" in await server.get_decision("ma", "999999")
    assert "numeric id" in await server.get_decision("ma", "قرار 210/23")


async def test_ma_legislation_filters():
    out = await server.search_legislation("ma", "الشغل", limit=5, filters={"type": "13"})
    assert "مدونة الشغل" in out and "1.03.194" in out, out
    out = await server.search_legislation("ma", "الشغل", limit=20,
                                          filters={"year_from": "2003", "year_to": "2004"})
    dates = re.findall(r"- Date: (\d{4})", out)
    assert dates and set(dates) <= {"2003", "2004"}, out
    assert "YYYY" in await server.search_legislation("ma", "الشغل", filters={"year_from": "03"})


async def test_ma_provision_label_variants():
    for label in ("الفصل 230", "230", "art. 230", "فصل 230"):
        out = await server.get_legislation_provision("ma", DOC, label)
        assert "الفصل 230" in out and "تقوم مقام القانون" in out, (label, out[:500])
    for label in ("618-3", "3-618"):      # sub-articles: either order
        out = await server.get_legislation_provision("ma", DOC, label)
        assert "الفصل 618-3" in out and "محرر رسمي" in out, out[:500]
    toc = await server.get_legislation_toc("ma", DOC, keyword="الكتاب الأول")
    assert 'provision "الفصل 1"' in toc, toc[:1000]
