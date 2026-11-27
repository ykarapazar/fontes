"""Offline tests: discovery, aliases, filter validation, unsupported-method message."""
import pytest

from world_legal_mcp import registry, server
from world_legal_mcp.base import BadRequest, Jurisdiction, NotFound, Source
from world_legal_mcp.models import Decision, DecisionHit, Results

CALLS = []


class _OnlyCaselaw(Jurisdiction):
    code = "zz"
    name = "Testland"
    sources = (Source("Testland Courts", "https://courts.example", covers=("caselaw",),
                      commercial_use=False),)
    caselaw_filters = {"court": "court code"}

    async def search_caselaw(self, query, *, limit, page, filters):
        if filters.get("court") == "bad":
            raise BadRequest("court must be a code")
        CALLS.append((query, limit, page, filters))
        return Results([DecisionHit(id="ZZ-1", title="A v B", court="Top Court", date="2026-01-02",
                                    url="https://courts.example/1", snippet="held")], total=1)

    async def get_decision(self, id):
        if id != "ZZ-1":
            raise NotFound(f"no decision {id}")
        CALLS.append(("get", id))
        return Decision(id=id, title="A v B", text="x" * 5000, url="https://courts.example/1",
                        court="Top Court", date="2026-01-02")


@pytest.fixture(autouse=True)
def _testland():
    registry.discover()
    registry.register(_OnlyCaselaw())
    yield
    registry._all.pop("zz", None)
    registry._enabled = None


def test_discovery_finds_ported_adapters():
    codes = {j.code for j in registry.available()}
    assert {"nl", "gb"} <= codes
    for code in ("nl", "gb"):
        assert registry.get(code).supported() == [
            "search_caselaw", "get_decision", "search_legislation",
            "get_legislation_toc", "get_legislation_provision", "get_legislation_text",
        ]


def test_aliases_and_case():
    assert registry.get("uk").code == "gb"
    assert registry.get(" GB ").code == "gb"
    assert registry.get("xx") is None


def test_no_alias_shadows_a_code():
    registry.discover()
    clash = {a: c for a, c in registry._aliases.items() if a in registry._all and a != c}
    assert not clash, f"aliases that hide another adapter's code: {clash}"
    assert registry.get("ccj").code == "ccj"


async def test_unknown_jurisdiction_message():
    out = await server.search_caselaw("xx", "anything")
    assert "Unknown or disabled jurisdiction 'xx'" in out and "list_jurisdictions()" in out
    assert len(out) < 300   # no dump of every code


async def test_unknown_jurisdiction_suggests_close_matches():
    out = await server.search_legislation("Germay", "x")
    assert "Did you mean: de (" in out and out.count("(") <= 4
    assert "Did you mean: ke (Kenya)" in await server.search_legislation("Kenia", "x")
    assert "Did you mean: za (South Africa)" in await server.list_jurisdictions("Sout Africa")
    assert "Did you mean" not in await server.list_jurisdictions("qqqqqqq")


async def test_unsupported_method_names_official_site():
    out = await server.get_legislation_text("zz", "some-law")
    assert "not supported for Testland (zz)" in out
    assert "no legislation source" in out and "search_caselaw" in out


async def test_unknown_filter_lists_valid_ones():
    out = await server.search_caselaw("zz", "q", filters={"judge": "x"})
    assert "Unknown caselaw filter(s) for zz: judge" in out
    assert "`court`" in out
    out = await server.search_legislation("uk", "q", filters={"court": "uksc"})
    assert "Unknown legislation filter(s) for gb: court" in out and "`doc_type`" in out


async def test_valid_filters_and_paging_pass_through():
    out = await server.search_caselaw("zz", "q", limit=5, page=2, filters={"court": "a"})
    assert CALLS[-1] == ("q", 5, 2, {"court": "a"})
    assert "# Testland (zz) case law: 1 decisions found for 'q' (page 2, 5 per page)" in out
    assert "### 6. A v B" in out and 'get_decision("zz", "ZZ-1")' in out and "> held" in out


async def test_adapter_errors_become_one_line():
    assert (await server.search_caselaw("zz", "q", filters={"court": "bad"})
            == "Bad request (zz): court must be a code")
    assert await server.get_decision("zz", "nope") == "Not found (zz): no decision nope"


async def test_decision_paging_uses_cache():
    server._cache.clear()
    n = len(CALLS)
    p1 = await server.get_decision("zz", "ZZ-1", max_chars=2000)
    p2 = await server.get_decision("zz", "ZZ-1", max_chars=2000, offset=2000)
    assert p1.startswith("# A v B") and "Call again with offset=2000" in p1
    assert p2.startswith("… [continuing from char 2000]")
    assert len(CALLS) == n + 1          # second page served from cache


async def test_unofficial_source_tells_model_to_flag_it():
    from world_legal_mcp import render
    j = _OnlyCaselaw()
    j.sources = (Source("Mirror Site", "https://mirror.example", covers=("caselaw",),
                        official=False),)
    hit = DecisionHit(id="ZZ-1", title="A v B", court="C", date="", url="u", snippet="")
    out = render.caselaw_results(j, "q", Results([hit], total=1), limit=10, page_no=1)
    assert "Unofficial source: Mirror Site (https://mirror.example)" in out
    assert "tell the user" in out and "official text" in out
    assert "Unofficial" not in render.caselaw_results(_OnlyCaselaw(), "q", Results([hit], total=1), limit=10, page_no=1)


async def test_list_shows_source_terms_and_coverage():
    _OnlyCaselaw.gaps = ("Lower courts: not published online",)
    out = await server.list_jurisdictions("testland")
    del _OnlyCaselaw.gaps
    assert "Not covered" in out and "Lower courts: not published online" in out
    assert "no commercial use" in out and "Covers: caselaw" in out


async def test_list_jurisdictions_shows_tools_and_filters():
    out = await server.list_jurisdictions("gb")
    assert "## gb — United Kingdom" in out and "aliases: uk" in out
    assert "`doc_type`" in out
    assert "Tools: search_caselaw" in out
    assert "`period`" in await server.list_jurisdictions("nl")
    assert "Netherlands" in await server.list_jurisdictions("netherlands")
    assert "Netherlands" not in await server.list_jurisdictions("uk")


async def test_only_filter():
    registry.enable_only(["uk"])
    assert [j.code for j in registry.available()] == ["gb"]
    assert "Unknown or disabled" in await server.get_decision("nl", "ECLI:NL:HR:2024:1")
    with pytest.raises(SystemExit):
        registry.enable_only(["mars"])


def test_citation_to_slug():
    from world_legal_mcp.jurisdictions.gb import citation_to_slug
    assert citation_to_slug("[2024] UKSC 1") == "uksc/2024/1"
    assert citation_to_slug("[2026] EWCA Civ 1161") == "ewca/civ/2026/1161"
    assert citation_to_slug("[2026] EWHC 2093 (Ch)") == "ewhc/ch/2026/2093"
    assert citation_to_slug("https://caselaw.nationalarchives.gov.uk/ewca/civ/2026/1161/data.xml") == "ewca/civ/2026/1161"


def test_toc_keyword_includes_entries_under_matching_heading():
    from world_legal_mcp import render
    from world_legal_mcp.base import Jurisdiction
    from world_legal_mcp.models import Toc, TocEntry

    t = Toc(id="x", title="Code", url="u", entries=[
        TocEntry("Chapter 1 Huur", 0, ""),
        TocEntry("Article 1", 1, "1"),
        TocEntry("Article 2", 1, "2"),
        TocEntry("Chapter 2 Koop", 0, ""),
        TocEntry("Article 3", 1, "3"),
    ])
    out = render.toc(Jurisdiction(), t, keyword="huur")
    assert "Article 1" in out and "Article 2" in out
    assert "Article 3" not in out and "Koop" not in out
    assert "3 of 5 entries" in out


def test_shared_text_helpers():
    from world_legal_mcp import _http
    assert _http.iso_date("27.01.2010") == "2010-01-27"
    assert _http.iso_date("5/3/2024") == "2024-03-05"
    assert _http.iso_date("2010-01-27T22:00:00Z") == "2010-01-27"
    assert _http.iso_date("Jan 2010") == ""
    md = _http.html_to_md("<html><head><style>x</style></head><body><p>A&nbsp; b</p>"
                          "<table><tr><td>Layout cell</td></tr></table><p>-</p></body></html>")
    assert md == "A b\n\nLayout cell"
    c = {}
    for i in range(5):
        _http.lru_put(c, i, i, 3)
    assert list(c) == [2, 3, 4]


async def test_size_cap_and_user_agent(monkeypatch):
    import httpx
    from world_legal_mcp import _http
    from world_legal_mcp.base import SourceError
    seen = {}

    def handler(req):
        seen["ua"] = req.headers["user-agent"]
        return httpx.Response(200, content=b"x" * 3000)

    monkeypatch.setattr(_http, "_client", httpx.AsyncClient(
        transport=httpx.MockTransport(handler), headers={"User-Agent": _http.UA}))
    assert (await _http.get("https://cap.example/a")).text == "x" * 3000
    assert seen["ua"].startswith("Fontes/")
    with pytest.raises(SourceError) as e:
        await _http.get("https://cap.example/b", max_bytes=1000)
    assert e.value.status == 413


async def test_head_keeps_content_length(monkeypatch):
    import httpx
    from world_legal_mcp import _http
    monkeypatch.setattr(_http, "_client", httpx.AsyncClient(transport=httpx.MockTransport(
        lambda req: httpx.Response(200, headers={"Content-Length": "123456"}))))
    h = await _http.request("HEAD", "https://head.example/f.pdf")
    assert h.headers["content-length"] == "123456"


def test_gating_blocks_only_when_every_source_of_a_kind_is_gated(monkeypatch):
    from world_legal_mcp.base import Source, blocked_sources

    class J:
        code = "zz"
        sources = [Source(name="gated", url="u", covers=("caselaw",), needs_permission=True)]

    monkeypatch.delenv("WLM_PERMITTED", raising=False)
    assert [s.name for s in blocked_sources(J, "search_caselaw")] == ["gated"]
    J.sources = J.sources + [Source(name="open", url="u2", covers=("caselaw",))]
    assert blocked_sources(J, "search_caselaw") == []
    monkeypatch.setenv("WLM_PERMITTED", "zz")
    assert blocked_sources(J, "get_decision") == []


def test_warnings_skip_gated_sources_unless_permitted(monkeypatch):
    from world_legal_mcp.render import _warnings

    class J:
        code = "zz"
        sources = [Source(name="gated", url="u", covers=("caselaw",), needs_permission=True, warning="ask first"),
                   Source(name="open", url="u2", covers=("caselaw",))]

    monkeypatch.delenv("WLM_PERMITTED", raising=False)
    assert _warnings(J, "caselaw") == []
    monkeypatch.setenv("WLM_PERMITTED", "zz")
    assert _warnings(J, "caselaw") == ["> ⚠ gated: ask first"]


async def test_list_jurisdictions_carries_beta_notice():
    assert (await server.list_jurisdictions("gb")).startswith("Fontes is in beta")
    assert "Fontes is in beta" in await server.list_jurisdictions()


def test_one_broken_adapter_does_not_hide_the_rest(monkeypatch):
    """Windows without tzdata broke lv's import and every adapter after it (nl, us, ...)."""
    real = registry.importlib.import_module

    def fake(name):
        if name.endswith(".lv"):
            raise ModuleNotFoundError("No time zone found with key Europe/Riga")
        return real(name)

    monkeypatch.setattr(registry, "_all", {})
    monkeypatch.setattr(registry, "_aliases", {})
    monkeypatch.setattr(registry, "_broken", {})
    monkeypatch.setattr(registry.importlib, "import_module", fake)
    codes = {j.code for j in registry.available()}
    assert "lv" not in codes and {"lu", "nl", "us", "wto"} <= codes
    assert "Europe/Riga" in server._resolve("lv", "search_caselaw")


def test_zoneinfo_works_without_system_tz():
    """tzdata must be installed so zoneinfo works where the OS has no tz database (Windows)."""
    import importlib.util
    assert importlib.util.find_spec("tzdata"), "tzdata is a declared dependency"
