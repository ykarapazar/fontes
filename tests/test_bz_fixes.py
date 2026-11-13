from world_legal_mcp.jurisdictions import bz

RULES = """TABLE OF CONTENTS
PART 10
DEFENCE
TABLE OF CONTENTS
Scope of this Part..........................................Rule 10.1
The period for filing a defence...........................Rule 10.2
Service of copy of defence................................Rule 10.3
Defendant's duty to set out case..........................Rule 10.4
Defence of tender.........................................Rule 10.5
10.1 The Rules in this Part set out the procedure.
10.2 (1) A defendant must file a defence.
10.3 Period is 28 days.
10.4 (1) The defence must set out all the facts.
(2) Such statement must be as short as practicable.
10.5 Tender is not available unless paid in.
PART 11
OTHER
"""


def test_rules_split():
    toc, texts = bz._split_rules(RULES)
    assert set(texts) == {"10.1", "10.2", "10.3", "10.4", "10.5"}
    assert "as short as practicable" in texts["10.4"] and "PART 11" not in texts["10.5"]
    assert any(e.provision == "10.4" and "duty to set out" in e.title for e in toc)
    assert bz._norm_prov("Rule 10.4(2)") == "10.4"
    assert bz._norm_prov("238") == "238"


def test_hit_posted_date():
    post = {"id": 1, "title": {"rendered": "A v B"}, "date": "2025-03-01T10:00:00", "excerpt": {"rendered": "x"}}
    assert bz._hit(post, with_date=True).snippet.startswith("[Posted on site: 2025-03-01]")
    assert bz._hit(post).snippet == "x"


def test_bz_date_filter_message_warns_posting_date_is_not_decision_date():
    import asyncio
    import pytest
    from world_legal_mcp.base import BadRequest
    from world_legal_mcp.jurisdictions.bz import Belize
    with pytest.raises(BadRequest, match="decision date"):
        asyncio.run(Belize().search_caselaw("negligence", filters={"date_from": "2022-01-01"}))


def test_later_amendments_found(monkeypatch):
    import asyncio

    async def fake_search(q):
        return [("a.pdf", "Act No. 08 of 2024 Criminal Code Amendment No. 2 Act 2024"),
                ("b.pdf", "Cap 101 Criminal Code Act")]

    async def fake_law(name):
        return {"sections": {"3": "3. The principal Act is amended in section 238 by deleting x.",
                             "4": "4. The principal Act is amended in section 2380 by y."}}

    monkeypatch.setattr(bz, "_agm_search", fake_search)
    monkeypatch.setattr(bz, "_law", fake_law)
    out = asyncio.run(bz._later_amendments({"title": "Cap 101 Criminal Code Act"}, "238"))
    assert len(out) == 1 and "Act No. 8 of 2024" in out[0] and "deleting x" in out[0]


def test_decision_posted_date_is_labelled_not_decision_date(monkeypatch):
    import asyncio

    class R:
        status_code = 200
        def json(self):
            return {"id": 5, "date": "2026-02-04T00:00:00", "title": {"rendered": "Civil Appeal No. 9 of 2004 A v B"},
                    "content": {"rendered": "<p>IN THE COURT OF APPEAL OF BELIZE 9 March 2005</p>"}, "categories": []}

    async def fake(url, params, who):
        return R()

    monkeypatch.setattr(bz, "_json", fake)
    d = asyncio.run(bz.Belize().get_decision("5"))
    assert d.date == "" and "NOT the decision date" in " ".join(d.metadata)
    assert "read it from the judgment text" in d.metadata["Decision date"]
