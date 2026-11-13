"""Offline tests for Mauritius: repealed ranges and 4-digit articles in law text, `since` filter."""
import pytest

from world_legal_mcp.base import BadRequest, NotFound
from world_legal_mcp.jurisdictions import mu
from world_legal_mcp.models import DecisionHit

TEXT = """ARRANGEMENT OF SECTIONS
1. Short title
An Act
1. Short title
Text one.
2. Next
Text two.
3. – 36. —
37. Accomplices
Text 37.
38. Other
Text 38.
"""


def test_repealed_range_does_not_stop_numbering():
    labels = [b["label"] for b in mu._parse_law(TEXT) if b["kind"] == "section"]
    assert labels == ["1", "2", "3", "37", "38"]


def test_four_digit_articles():
    text = "ARRANGEMENT OF\nAn Act\n1. A\nx\n2. B\ny\n3. – 1381. —\n1382. Liability\nz\n"
    assert "1382" in [b["label"] for b in mu._parse_law(text) if b["kind"] == "section"]
    assert mu._norm_provision("s. 1382") == "1382"


async def test_provision_inside_range(monkeypatch):
    j = mu.Mauritius()

    async def law(_id):
        return {"id": "X", "title": "T", "url": "u", "blocks": mu._parse_law(TEXT)}
    monkeypatch.setattr(j, "_law", law)
    with pytest.raises(NotFound, match="falls inside 3-36"):
        await j.get_legislation_provision("X", "20")
    assert (await j.get_legislation_provision("X", "3")).provision == "3"


def test_despace_repairs_split_words_only():
    t = ("recognised the publi c interest. recognised public public. a ssembly assembly assembly. "
         "into into " + "in to " * 20 + "rec ognised. B\u2019s election selection selection. "
         "with-\nout without without. non-\ndiscrimination. member s members members")
    u = mu._despace(t)
    assert "rec ognised" not in u and "publi c" not in u and "a ssembly" not in u
    assert "without without" in u and "non-discrimination" in u and "in to" in u
    assert "B\u2019s election" in u and "member s" not in u


async def test_since_filter(monkeypatch):
    j = mu.Mauritius()
    hits = [DecisionHit(id=f"[{y}] UKPC 1", title="t", date=f"{y}-01-01") for y in (2021, 2022, 2025)]

    async def fake(*a):
        return list(hits)
    monkeypatch.setattr(mu, "jcpc_hits", fake)
    r = await j.search_caselaw("dismissal", filters={"court": "jcpc", "since": "2022"})
    assert [h.id for h in r.items] == ["[2022] UKPC 1", "[2025] UKPC 1"]
    with pytest.raises(BadRequest):
        await j.search_caselaw("x", filters={"court": "jcpc", "since": "2022", "year": "2023"})


async def test_provision_in_dash_entry_says_so(monkeypatch):
    text = "ARRANGEMENT OF\nAn Act\n1. A\nx\n2. B\ny\n3. – 36. —\n37. C\nz\n"
    j = mu.Mauritius()

    async def law(_id):
        return {"id": "X", "title": "T", "url": "u", "blocks": mu._parse_law(text)}
    monkeypatch.setattr(j, "_law", law)
    with pytest.raises(NotFound, match="one dash entry"):
        await j.get_legislation_provision("X", "20")


async def test_local_search_note_warns_no_status(monkeypatch):
    items = [{"id": "a", "title": "DATA PROTECTION ACT, No 13 of 2004", "type": "Revised law",
              "number": "", "year": "", "url": "u", "key": "dataprotectionact"}]

    async def idx():
        return items
    monkeypatch.setattr(mu, "_index", idx)
    r = await mu.Mauritius().search_legislation("data protection act", filters={"type": "revised"})
    assert "No in-force status" in r.note and "repealed" in r.note
