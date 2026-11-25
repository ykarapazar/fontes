"""Live smoke tests against vbpl.vn (sitemap-slug search + Next.js detail pages),
vanban.chinhphu.vn (ASP.NET postback search + datafiles PDFs)
and anle.toaan.gov.vn (precedents; needs the OS trust store, so macOS/Windows only).
Needs network; 1 s spacing per request."""
from world_legal_mcp import server


async def test_vn_provision_label_variants():
    a = await server.get_legislation_provision("vn", "211189", "Điều 3")
    b = await server.get_legislation_provision("vn", "211189", "3")
    assert a == b and "Điều 3" in a and "Giải thích từ ngữ" in a


async def test_vn_year_filter():
    out = await server.search_legislation("vn", "Luật Đất đai", limit=10,
                                       filters={"year": "2024", "source": "chinhphu"})
    assert "31/2024/QH15" in out and "(page 1, 10 per page)" in out


async def test_vn_postback_paging():
    p2 = await server.search_legislation("vn", "Luật Đất đai", limit=50, page=2,
                                      filters={"source": "chinhphu"})
    assert "### 51." in p2 and "### 1." not in p2


async def test_vn_number_is_not_an_id():
    out = await server.get_legislation_text("vn", "91/2015/QH13")
    assert out.startswith("Bad request") and "91/2015/QH13" in out


async def test_vn_vbpl_constitution():
    hits = await server.search_legislation("vn", "hiến pháp", filters={"type": "hien-phap"})
    assert "### 1. Hien phap nam 2013" in hits and "hien-phap-nam-1946--535" in hits
    a = await server.get_legislation_provision("vn", "hien-phap-nam-2013--32801", "Điều 120")
    b = await server.get_legislation_provision("vn", "https://vbpl.vn/van-ban/chi-tiet/32801", "120")
    body = lambda out: out.split("\n\n", 1)[1]  # noqa: E731  (after the header lines)
    assert body(a) == body(b) and "sửa đổi Hiến pháp" in a


async def test_vn_vbpl_civil_code_text():
    # the Government Portal copy is a scan; vbpl.vn has the text
    hits = await server.search_legislation("vn", "91/2015/QH13")
    assert "bo-luat-dan-su-so-91-2015-qh13--95942" in hits
    p = await server.get_legislation_provision("vn", "bo-luat-dan-su-so-91-2015-qh13--95942", "689")
    assert "Điều 689. Hiệu lực thi hành" in p and "01 tháng 01 năm 2017" in p


async def test_vn_precedent_number_ids():
    a = await server.get_decision("vn", "01/2016/AL")
    b = await server.get_decision("vn", "TAND014297")
    assert a == b and "Án lệ số 01/2016/AL" in a and "Giết người" in a
    hit = await server.search_caselaw("vn", "án lệ số 47")
    assert "47/2021/AL" in hit


async def test_vn_precedent_search_diacritics():
    exact = await server.search_caselaw("vn", "hình sự", limit=50)
    plain = await server.search_caselaw("vn", "hinh su", limit=50)
    assert "Hình sự" in exact and "90/2026/AL" not in exact  # 90 is about 'sử dụng đất'
    count = lambda out: out.split("case law: ")[1].split(" decisions")[0]  # noqa: E731
    assert count(exact) == count(plain)


async def test_vn_precedent_pdf_text():
    out = await server.get_decision("vn", "TAND332760")
    assert "72/2024/AL" in out and "Giải pháp pháp lý" in out and "NỘI DUNG VỤ ÁN" in out


async def test_vn_precedent_scan_is_reported():
    out = await server.get_decision("vn", "90/2026/AL")
    assert out.startswith("Error") and "scanned PDF" in out and "TAND377340" in out
