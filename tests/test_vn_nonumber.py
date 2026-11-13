from world_legal_mcp.jurisdictions import vn


def test_unnumbered_slug_title():
    h = vn._vb_hit("bo-luat-dan-su-so-khong-so--9683")
    assert h.title.startswith("Bo luat dan su (") and "Không số" in h.title
    assert h.id == "bo-luat-dan-su-so-khong-so--9683" and h.number == "Không số"


def test_numbered_slug_title():
    h = vn._vb_hit("bo-luat-dan-su-so-91-2015-qh13--95942")
    assert h.number == "91/2015/QH13" and "số 91/2015/QH13" in h.title


def test_unnumbered_hit_gets_date_from_page(monkeypatch):
    import asyncio

    async def slugs():
        return ["bo-luat-dan-su-so-khong-so--9683"]

    async def doc(id):
        return {"meta": {"Ngày ban hành": "1995-10-28", "Tình trạng hiệu lực": "Hết hiệu lực toàn bộ"}}

    monkeypatch.setattr(vn, "_vb_slugs", slugs)
    monkeypatch.setattr(vn, "_vb_doc", doc)
    r = asyncio.run(vn.Vietnam()._vb_search("bo luat dan su", "", "", 5, 1))
    assert r.items[0].date == "1995-10-28" and "Hết hiệu lực" in r.items[0].title
