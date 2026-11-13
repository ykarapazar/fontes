from world_legal_mcp.jurisdictions.hr import Croatia


def _h(t, d, n):
    return {"title": t, "date": d, "number": n, "snippet": ""}


def test_rerank_whole_word_and_newest_first():
    hits = [_h("Zakon o prestanku rada", "1990-12-14", "A"), _h("Zakon o radu", "2009-12-15", "B"),
            _h("Zakon o radu", "2014-07-30", "C")]
    out = Croatia._rerank(hits, "radu")
    assert [x["number"] for x in out] == ["C", "B", "A"]
    assert "newer act" in out[1]["snippet"]


def test_constitution_status_not_latest():
    d = {"title": "Ustav Republike Hrvatske", "number": "NN 56/1990", "date": "1990-12-22"}
    assert "latest" not in Croatia._status(d)
    assert "after 2014" in Croatia._status(d)


def test_rerank_original_vs_prociscen_and_newer_amendment():
    hits = [_h("Zakon o trgovačkim društvima", "1993-12-15", "O"),
            _h("Zakon o trgovačkim društvima (pročišćeni tekst)", "2011-12-27", "P"),
            _h("Zakon o izmjenama i dopuni Zakona o trgovačkim društvima", "2013-06-07", "A")]
    out = Croatia._rerank(hits, "Zakon o trgovačkim društvima")
    assert [x["number"] for x in out] == ["P", "O", "A"]
    assert "Older act" in out[1]["snippet"] and "Newer amending" in out[0]["snippet"]
