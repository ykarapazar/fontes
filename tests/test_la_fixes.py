"""Laos: English name mapping, null.pdf, incomplete records; offline."""
import asyncio

from world_legal_mcp.jurisdictions import la

ROW = ('<div id="legals-grid"><div class="summary">1-1 ຂອງ 1</div><table class="items"><tbody>'
       '<tr><td>T</td><td>A</td><td>{d}</td><td></td><td>{t}</td><td>ປັດຈຸບັນ</td>'
       '<td><a href="/index.php?r=site/display&id=9">x</a></td><td></td>'
       '<td><a href="/kcfinder/upload/files/{f}">p</a></td></tr></tbody></table></div>')


def _run(monkeypatch, row, q):
    seen = []

    class R:
        status_code = 200
        text = row

    async def get(url, **kw):
        seen.append(url)
        return R()
    monkeypatch.setattr(la._http, "get", get)
    res = asyncio.run(la.Laos().search_legislation(q, limit=10, page=1, filters={}))
    return res, seen


def test_english_name_searches_lao_title(monkeypatch):
    _, seen = _run(monkeypatch, ROW.format(d="", t="", f="a.pdf"), "Civil Code")
    assert "%E0%BA%9B%E0%BA%B0%E0%BA%A1" in seen[0] and "civil" not in seen[0].lower()


def test_null_pdf_and_incomplete_record(monkeypatch):
    res, _ = _run(monkeypatch, ROW.format(d="", t="", f="null.pdf"), "x")
    snip = res.items[0].snippet
    assert "null.pdf" not in snip.replace("(null.pdf)", "") and "Lao PDF (scan)" not in snip
    assert "no date or type" in snip
    assert res.items[0].status == "" and "Date line" in snip
    assert "no date filter" in res.note


def test_row_with_null_and_real_pdf_shows_real_pdf(monkeypatch):
    row = ROW.replace("</tbody>", "").replace("</a></td></tr>",
          '</a><a href="/kcfinder/upload/files/null.pdf">n</a></td></tr></tbody>')
    res, _ = _run(monkeypatch, row.format(d="2018-12-06", t="x", f="ilovepdf_merged (4).pdf"), "x")
    snip = res.items[0].snippet
    assert "ilovepdf_merged%20(4).pdf" in snip and "broken" not in snip


def test_english_generic_law_queries_use_lao_topic(monkeypatch):
    _, seen = _run(monkeypatch, ROW.format(d="", t="", f="a.pdf"), "land law")
    assert "law" not in seen[0]


def test_labour_law_searches_lao_labour_word(monkeypatch):
    _, seen = _run(monkeypatch, ROW.format(d="", t="", f="a.pdf"), "labour law")
    assert "%E0%BB%81%E0%BA%AE%E0%BA%87%E0%BA%87%E0%BA%B2%E0%BA%99" in seen[0] and "law" not in seen[0]
