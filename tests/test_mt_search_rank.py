"""Malta search ranking, offline: Acts before subsidiary legislation, repealed last."""
import asyncio
from types import SimpleNamespace

from world_legal_mcp import _http
from world_legal_mcp.jurisdictions import mt

ROWS = [
    ("S.L. 35.39", "Fees payable for Residence Permits and Employment Licences Regulations", "sl/35.39"),
    ("Cap. 135(R)", "Conditions of Employment (Regulation) Act <BR><I> Repealed by Act II of 2015", "cap/135"),
    ("Cap. 210", "Persons with Disability (Employment) Act", "cap/210"),
    ("Cap. 452", "Employment and Industrial Relations Act", "cap/452"),
]


def test_acts_first_and_repealed_last(monkeypatch):
    async def post(url, **kw):
        data = [{"ChapterText": r, "ChapterTitle": t, "URL": f"eli/{e}/eng/portalpdf"} for r, t, e in ROWS]
        return SimpleNamespace(status_code=200, headers={"content-type": "application/json"},
                               json=lambda: {"data": data, "recordsFiltered": len(data)})
    monkeypatch.setattr(_http, "post", post)
    res = asyncio.run(mt.Malta().search_legislation("Employment", limit=10))
    assert [h.number for h in res.items] == ["Cap. 452", "Cap. 210", "S.L. 35.39", "Cap. 135(R)"]
    assert "<" not in res.items[-1].title
    assert "dates" in res.note
