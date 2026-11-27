"""Countries read through Lexifina's record: offline checks with lexifina.call faked."""
import pytest

from world_legal_mcp import lexifina, registry
from world_legal_mcp.base import BadRequest, NotFound, SourceError
from world_legal_mcp.jurisdictions import lexifina_countries as L

ACT = "south-africa/national/acts/act/2013/4"


def _res(body, /, **structured):
    return {"content": [{"type": "text", "text": body}], "structuredContent": structured}


@pytest.fixture
def za():
    registry.discover()
    return registry._all["za"]


@pytest.fixture
def fake(monkeypatch):
    """Answers shaped like the real server; `routes` maps tool -> function(args)."""
    calls = []
    routes = {}

    async def call(tool, **args):
        calls.append((tool, args))
        return routes[tool](args)
    monkeypatch.setattr(lexifina, "call", call)
    routes["calls"] = calls
    return routes


def _acts(n):
    return [{"path": f"south-africa/national/acts/act/2000/{i}", "title": f"Act {i}",
             "matching_provisions": 10 - i} for i in range(n)]


def test_registered_unofficial_and_off(monkeypatch, za):
    assert za.via_lexifina and not za.sources[0].official and za.coverage()["legislation"]
    assert not za.coverage()["caselaw"] and za.samples == {}
    assert "south africa" in za.aliases and registry.canonical("south-africa") == "za"
    monkeypatch.setenv("WLM_LEXIFINA", "0")
    assert not za.supports("search_legislation") and "WLM_LEXIFINA=0" in za.notes


async def test_search_dedupes_acts_and_pages(fake, za):
    matches = [{"path": f"{ACT}/section-00{i}.md", "act": "POPIA", "unit": str(i), "heading": "H",
                "official_url": "https://x/popia.pdf", "last_change": {"in_force": "2014-04-11"}}
               for i in range(1, 4)]
    fake["search_law"] = lambda a: _res("t", acts=_acts(5), matches=matches, matched_by="index",
                                        match="phrase", summary="s")
    r = await za.search_legislation("privacy", limit=2, page=2, filters={})
    assert [h.id for h in r.items] == [f"south-africa/national/acts/act/2000/{i}" for i in (2, 3)]
    assert r.total == 5 and not r.incomplete and "Lexifina" in r.note
    r = await za.search_legislation("privacy", limit=10, page=1, filters={})
    assert len(r.items) == 5 and r.items[0].url == lexifina.REPO
    assert fake["calls"][0][1]["jurisdiction"] == "south-africa"


async def test_search_dedupes_without_acts_list(fake, za):
    matches = [{"path": f"{ACT}/section-00{i}.md", "act": "POPIA", "unit": str(i), "heading": "H",
                "official_url": "https://x/popia.pdf", "last_change": {"in_force": "2014-04-11"}}
               for i in (1, 2)]
    fake["search_law"] = lambda a: _res("t", matches=matches, matched_by="index", match="phrase")
    r = await za.search_legislation("privacy", limit=10, page=1, filters={})
    assert [(h.id, h.title, h.date, h.url) for h in r.items] == [
        (ACT, "POPIA", "", "https://x/popia.pdf")]
    assert "that provision last changed 2014-04-11" in r.items[0].snippet


async def test_search_cap_is_incomplete(fake, za):
    fake["search_law"] = lambda a: _res("t", acts=_acts(12), matches=[], matched_by="index", match="phrase")
    r = await za.search_legislation("the", limit=20, page=1, filters={})
    assert not r.incomplete and r.total is None and len(r.items) == 12
    assert "only its 12 best-matching acts" in r.note and "below state or provincial" in r.note
    fake["search_law"] = lambda a: _res("t", acts=_acts(11), matches=[], matched_by="index", match="phrase")
    r = await za.search_legislation("the", limit=20, page=1, filters={})
    assert r.total == 11 and "best-matching" not in r.note


async def test_search_fuzzy_fallback_says_no_phrase_match(fake, za):
    fake["search_law"] = lambda a: _res("t", acts=_acts(3), matches=[], matched_by="index",
                                        match="most_words", summary="No provision holds it as a phrase")
    r = await za.search_legislation("money laundering", limit=20, page=1, filters={})
    assert r.total == 0 and len(r.items) == 3
    assert r.note.startswith("NO act or provision matched the phrase") and "unrelated" in r.note
    assert "may not be in Lexifina's record" in r.note


async def test_search_zero_keeps_explanation(fake, za):
    fake["search_law"] = lambda a: _res("0 provision(s) hold 'zzz'. Searched 4 bodies of law.", page={"total": 0})
    r = await za.search_legislation("zzz", limit=20, page=1, filters={})
    assert r.items == [] and "Searched 4 bodies" in r.note
    with pytest.raises(BadRequest):
        await za.search_legislation("  ", limit=20, page=1, filters={})


async def test_toc_and_provision(fake, za):
    provs = [{"path": f"{ACT}/section-001.md", "heading": "1. Definitions"},
             {"path": f"{ACT}/section-005.md", "heading": "5. Rights of data subjects"}]
    fake["list_provisions"] = lambda a: _res("t", provisions=provs, page={"next_offset": None})
    fake["read_law"] = lambda a: _res("NOTES\n\n# 5. Rights", act="POPIA", text="# 5. Rights",
                                      cite={"official_url": "https://x/popia.pdf"},
                                      last_change={"in_force": "2020-07-01"})
    toc = await za.get_legislation_toc(ACT)
    assert toc.title == "POPIA" and [(e.title, e.provision) for e in toc.entries][1] == (
        "5. Rights of data subjects", "section-005")
    for label in ("5", "Section 5", "section-005"):
        p = await za.get_legislation_provision(ACT, label)
        assert (p.provision, p.text, p.url, p.as_of, p.law_title) == (
            "section-005", "NOTES\n\n# 5. Rights", "https://x/popia.pdf", "2020-07-01", "POPIA")
    assert fake["calls"][-1][1]["path"] == f"{ACT}/section-005.md"


async def test_provision_falls_back_to_find_and_raises(fake, za):
    fake["list_provisions"] = lambda a: _res("t", provisions=[{"path": f"{ACT}/s-1.md", "heading": "x"}],
                                             page={"next_offset": None})
    fake["find_provision"] = lambda a: _res("t", results=[])
    with pytest.raises(NotFound):
        await za.get_legislation_provision(ACT, "99")
    fake["find_provision"] = lambda a: _res("t", results=[{"path": f"{ACT}/s-9.md", "heading": "9"}])
    fake["read_law"] = lambda a: _res("T", act="A")
    assert (await za.get_legislation_provision(ACT, "nine")).provision == "s-9"


def _parts(n):
    def read(a):
        off = a.get("offset") or 0
        i = off // 10
        nxt = None if i == n - 1 else off + 10
        s = dict(text=f"part{i}", text_part={"chars": 10 * n, "offset": off, "next_offset": nxt},
                 act="POPIA", provisions=[{"path": f"{ACT}/section-001.md"}],
                 cite={}, last_change={})
        return _res("NOTES part0" if i == 0 else "ignored", **s)
    return read


async def test_text_loops_until_done(fake, za):
    fake["read_law"] = _parts(3)
    t = await za.get_legislation_text(ACT)
    assert t.text == "NOTES part0\npart1\npart2" and t.note == "" and t.title == "POPIA"
    assert len(fake["calls"]) == 3 and t.url == lexifina.REPO


async def test_text_stops_at_cap(fake, za):
    fake["read_law"] = _parts(30)
    t = await za.get_legislation_text(ACT)
    assert len(fake["calls"]) == 10 and "get_legislation_provision" in t.note
    assert "100 of 300" in t.note or "of 300" in t.note


async def test_text_of_single_provision_file(fake, za):
    fake["read_law"] = lambda a: _res("N", text="x", act="POPIA", text_part={"chars": 1, "next_offset": None})
    t = await za.get_legislation_text(f"{ACT}/section-001.md")
    assert t.title == "POPIA" and len(fake["calls"]) == 1


async def test_source_error_propagates(monkeypatch, za):
    async def boom(tool, **a):
        raise SourceError("Lexifina is busy", 429)
    monkeypatch.setattr(lexifina, "call", boom)
    for coro in (za.search_legislation("x", limit=5, page=1, filters={}), za.get_legislation_toc(ACT),
                 za.get_legislation_text(ACT)):
        with pytest.raises(SourceError):
            await coro


async def test_provision_and_text_show_record_end_not_today(fake, za):
    pre = "p.md as in force on 2026-11-27.\nCite as: x, as in force on 2026-11-27.\nbody"
    s = dict(act="POPIA", date="2026-11-27", text="b", cite={}, text_part={"chars": 1, "next_offset": None},
             last_change={"in_force": "2014-04-11"},
             latest={"state": "same", "record_end": "2026-11-04"}, provisions=[{"path": f"{ACT}/section-001.md"}])
    fake["list_provisions"] = lambda a: _res("t", provisions=[{"path": f"{ACT}/section-001.md", "heading": "1"}],
                                             page={"next_offset": None})
    fake["read_law"] = lambda a: _res(pre, **s)
    p = await za.get_legislation_provision(ACT, "1")
    assert p.as_of.startswith("2026-11-04") and "2014-04-11" in p.as_of
    assert "2026-11-27" not in p.text and p.text.count("as in force on 2026-11-04") == 2
    t = await za.get_legislation_text(ACT)
    assert t.as_of.startswith("2026-11-04") and "2026-11-27" not in t.text
    s["latest"] = {"state": "changed", "record_end": "2026-11-04"}
    assert (await za.get_legislation_provision(ACT, "1")).as_of == "2014-04-11"


async def test_off_answers_turned_off_and_list_says_so(monkeypatch):
    from world_legal_mcp import server
    monkeypatch.setenv("WLM_LEXIFINA", "0")
    assert await server.search_legislation("za", "privacy") == lexifina.OFF
    assert await server.get_legislation_toc("za", ACT) == lexifina.OFF
    assert "turned off" in await server.list_jurisdictions("")


async def test_search_words_only_inside_other_acts(fake, za):
    fake["search_law"] = lambda a: _res("t", acts=_acts(3), matches=[], matched_by="index", match="phrase",
                                        summary="s")
    r = await za.search_legislation("Data Protection Act", limit=20, page=1, filters={})
    assert r.note.startswith("None of these acts has those words in its title")
    fake["search_law"] = lambda a: _res("t", acts=[{"path": ACT, "title": "Data Protection Act, 2019"}],
                                        matches=[], matched_by="index", match="phrase", summary="s")
    r = await za.search_legislation("Data Protection Act", limit=20, page=1, filters={})
    assert not r.note.startswith("None of these")


async def test_provision_number_label_suggestions_and_single_record(fake, za):
    provs = [{"path": f"{ACT}/cl-001.md", "heading": "Clause 1. Freedom"},
             {"path": f"{ACT}/cl-050b.md", "heading": "Clause 50B. Votes"},
             {"path": f"{ACT}/s-024.md", "heading": "Clause 24"}]
    fake["list_provisions"] = lambda a: _res("t", provisions=provs, page={"next_offset": None})
    fake["read_law"] = lambda a: _res("T", act="A")
    assert (await za.get_legislation_provision(ACT, "1")).provision == "cl-001"
    assert (await za.get_legislation_provision(ACT, "50b")).provision == "cl-050b"
    fake["find_provision"] = lambda a: _res("t", results=[])
    with pytest.raises(NotFound, match="Closest labels: s-024"):
        await za.get_legislation_provision(ACT, "sec-024")
    fake["list_provisions"] = lambda a: _res("t", provisions=[{"path": f"{ACT}/text.md", "heading": "x"}],
                                             page={"next_offset": None})
    p = await za.get_legislation_provision(ACT, "6.5")
    assert p.provision == "text" and "held as one record" in p.note
    fake["find_provision"] = lambda a: _res("t", results=[{"path": f"{ACT}/s-9.md", "heading": "9"}])
    fake["list_provisions"] = lambda a: _res("t", provisions=provs, page={"next_offset": None})
    assert "closest match" in (await za.get_legislation_provision(ACT, "nine")).note


async def test_hit_without_title_uses_path_and_labels_date(fake, za):
    path = "russia/national/acts/fz/2011/261"
    fake["search_law"] = lambda a: _res("t", acts=[{"path": path, "title": ""}], matched_by="index", match="phrase",
                                        matches=[{"path": path + "/text.md",
                                                  "last_change": {"in_force": "2011-07-27"}}])
    h = (await za.search_legislation("x", limit=10, page=1, filters={})).items[0]
    assert h.title == "fz/2011/261" and h.date == "" and "last changed 2011-07-27" in h.snippet


async def test_as_of_label_is_neutral(fake, za):
    s = {"last_change": {"in_force": "2014-04-11"}, "latest": {"state": "same", "record_end": "2026-11-04"}}
    assert L._as_of(s, "b")[0].startswith("2026-11-04 (the latest state in Lexifina's record")
    s["latest"]["state"] = "changed"
    assert L._as_of(s, "b")[0] == "2014-04-11"


def test_as_of_shows_check_date_when_far_after_change():
    s = {"last_change": {"in_force": "2025-07-21"}, "latest": {"state": "changed"}}
    body = "Note: x: the record runs to 2026-11-03; stale, last checked against Y (laws.y.gov) on 2026-11-03 (1 day ago)."
    assert L._as_of(s, body)[0] == "2025-07-21 (latest change in Lexifina's record; record last checked 2026-11-03)"
    s["last_change"]["in_force"] = "2026-10-20"
    assert L._as_of(s, body)[0] == "2026-10-20"


async def test_fallback_with_same_number_has_no_warning(fake, za):
    fake["list_provisions"] = lambda a: _res("t", provisions=[{"path": f"{ACT}/s-1.md", "heading": "x"}],
                                             page={"next_offset": None})
    fake["find_provision"] = lambda a: _res("t", results=[{"path": f"{ACT}/art-057.md", "heading": "57"}])
    fake["read_law"] = lambda a: _res("T", act="A")
    p = await za.get_legislation_provision(ACT, "57")
    assert p.provision == "art-057" and not p.note
    fake["find_provision"] = lambda a: _res("t", results=[{"path": f"{ACT}/art-058.md", "heading": "58"}])
    assert "closest match" in (await za.get_legislation_provision(ACT, "57")).note


def test_as_of_same_state_shows_check_date_when_far_after_end():
    s = {"last_change": {"in_force": "2023-01-18"}, "latest": {"state": "same", "record_end": "2025-07-21"}}
    body = "Note: x: the record runs to 2025-07-21; stale, last checked against Y (laws.y.gov) on 2026-11-03 (1 day ago)."
    assert L._as_of(s, body)[0] == ("2025-07-21 (the latest state in Lexifina's record, last checked 2026-11-03; "
                                    "this wording in force since 2023-01-18)")
    assert "last checked" not in L._as_of(s, body.replace("2026-11-03", "2025-07-30"))[0]
