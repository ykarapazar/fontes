from world_legal_mcp.jurisdictions.itlos import _pick_order, _dmy


def _d(title):
    return {"title": title, "date": _dmy(title)}


def test_pick_order_delivered_date():
    docs = [_d("Order 2019/1 of 23 April 2019"), _d("Order 2019/2 of 2 May 2019"),
            _d("Order of 25 May 2019")]
    ov = [("Overview", "The Tribunal delivered its Order on 25 May 2019.")]
    assert _pick_order(docs, ov)[0]["date"] == "2019-05-25"


def test_pick_order_on_date_form_and_fallback():
    docs = [_d("Order 1999/2 of 3 August 1999"), _d("Order of 27 August 1999")]
    ov = [("Overview", "On 27 August 1999, the Tribunal delivered its Order in the case.")]
    assert _pick_order(docs, ov)[0]["date"] == "1999-08-27"
    assert _pick_order(docs, [])[0]["title"] == "Order of 27 August 1999"


def test_basic_texts_pointer_in_notes_and_gaps():
    from world_legal_mcp.jurisdictions.itlos import ITLOS
    url = "/en/main/basic-texts-and-other-documents/"
    assert url in ITLOS.notes
    assert any(url in g and "Rules" in g for g in ITLOS.gaps)
