import asyncio

from world_legal_mcp.jurisdictions import bb


def test_clean_law_drops_ocr_authority_footer():
    t = "x" * 5 + "\nby the uthorily of the Government i.f Barbados\nreal text"
    assert "uthorily" not in bb._clean_law(t)
    assert "real text" in bb._clean_law(t)


def test_legislation_note_says_recent_acts_missing(monkeypatch):
    async def fake(kind):
        return []
    monkeypatch.setattr(bb, "_list", fake)
    r = asyncio.run(bb.Barbados().search_legislation("Sexual Harassment"))
    assert r.total == 0 and "after the last printed revision" in r.note


def test_drop_margin_block():
    from world_legal_mcp.jurisdictions.bb import _drop_margin
    t = "3. Subject to this section, a claim\nshall not be defeated.\n\ncourt to\nfmd total\ndamages.\nCap. 194A.\n(2) This subsection applies."
    out = _drop_margin(t)
    assert "fmd total" not in out and "Cap. 194A" not in out
    assert "(2) This subsection applies." in out and "shall not be defeated." in out


def test_criminal_appeal_relabelled():
    from lxml import html as lhtml
    from world_legal_mcp.jurisdictions.bb import _rows
    doc = lhtml.fromstring('<table class="case-search-results"><tbody><tr><td>1</td><td><a href="judgments/x-v-the-queen">X v The Queen</a></td>'
                           '<td>Court Of Appeal, Civil Division</td><td></td><td>2015-12-16</td></tr></tbody></table>')
    assert "Criminal Division" in _rows(doc)[0].court


def test_drop_margin_removes_formerly_entitled_footnote():
    t = "3. Subject to this section, a claim\nshall be reduced.\n‘This Act was formerly entitled the Law Reform (Contributory Negligence) Act, 1953,\n1953-16.\n\n(2) This subsection applies."
    out = bb._drop_margin(t)
    assert "formerly" not in out and "1953-16" not in out
    assert "shall be reduced." in out and "(2) This subsection applies." in out


def test_sections_survive_lost_number_after_margin_note():
    arr = "1. Short title.\n" + "\n".join(f"{n}. Heading {n}." for n in range(2, 11)) + "\n"
    body = ("1. This Act may be cited.\n2. (1) Defs.\n3. (1) A contract.\n4. (1) Cap.\n5. X\n6. Goods\n"
            "perishing 8. Where x\n9. (1) Price.\n10. (1) Y.\n")
    secs = dict(bb._sections(arr + body))
    assert secs["3"].startswith("3. (1) A contract.")
    assert "8. Where x" in secs["6"]


def test_provision_warns_not_quotable_before_text(monkeypatch):
    import asyncio
    from world_legal_mcp.jurisdictions import bb

    law = "1. Short title.\n2. Interp.\n3. Body text here\nmore text\n4. Next section.\n" + "x" * 200

    async def fake_find(ident):
        return {"id": "statutes/X", "title": "X", "url": "u"}

    async def fake_law(row):
        return law

    monkeypatch.setattr(bb, "_find", fake_find)
    monkeypatch.setattr(bb, "_law", fake_law)
    cls = next(v for v in vars(bb).values() if isinstance(v, type) and hasattr(v, "get_legislation_provision"))
    p = asyncio.run(cls().get_legislation_provision("statutes/X", "3"))
    assert p.text.index("NOT QUOTABLE") < p.text.index("Body text")
