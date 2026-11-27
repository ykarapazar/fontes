import json

import httpx
import pytest

from world_legal_mcp import _http, lexifina, registry, server, stats
from world_legal_mcp.base import BadRequest, NotFound, SourceError


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.delenv("WLM_LEXIFINA", raising=False)
    monkeypatch.setattr(stats, "record", lambda *a, **k: None)


def _resp(status=200, payload=None, headers=None):
    return httpx.Response(status, json=payload, headers=headers or {},
                          request=httpx.Request("POST", lexifina.URL))


def _ok(text="hello", structured=None):
    res = {"content": [{"type": "text", "text": text}]}
    if structured is not None:
        res["structuredContent"] = structured
    return {"jsonrpc": "2.0", "id": 1, "result": res}


def _fake_post(monkeypatch, response=None, exc=None):
    sent = []

    async def post(url, **kw):
        sent.append((url, kw))
        if exc:
            raise exc
        return response

    monkeypatch.setattr(_http, "post", post)
    return sent


# ---- call() ----

async def test_call_passes_result_and_drops_none(monkeypatch):
    sent = _fake_post(monkeypatch, _resp(payload=_ok("body")))
    res = await lexifina.call("read_law", path="a/b.md", date=None, offset=0)
    assert lexifina.text(res) == "body"
    url, kw = sent[0]
    assert url == lexifina.URL
    assert kw["json"]["params"] == {"name": "read_law", "arguments": {"path": "a/b.md", "offset": 0}}


async def test_call_not_in_corpus_is_notfound(monkeypatch):
    p = {"result": {"isError": True, "content": [{"type": "text", "text": "Path is not inside a corpus"}]}}
    _fake_post(monkeypatch, _resp(payload=p))
    with pytest.raises(NotFound):
        await lexifina.call("read_law", path="x")


async def test_call_other_iserror_is_badrequest(monkeypatch):
    p = {"result": {"isError": True, "content": [{"type": "text", "text": "date is malformed"}]}}
    _fake_post(monkeypatch, _resp(payload=p))
    with pytest.raises(BadRequest):
        await lexifina.call("read_law", path="x")


async def test_call_429_mentions_retry_after(monkeypatch):
    _fake_post(monkeypatch, _resp(429, {}, {"Retry-After": "30"}))
    with pytest.raises(SourceError) as ei:
        await lexifina.call("read_law")
    assert "30" in str(ei.value) and ei.value.status == 429


@pytest.mark.parametrize("status", [503, 500])
async def test_call_http_errors(monkeypatch, status):
    _fake_post(monkeypatch, _resp(status, {}))
    with pytest.raises(SourceError) as ei:
        await lexifina.call("read_law")
    assert ei.value.status == status


async def test_call_network_error(monkeypatch):
    _fake_post(monkeypatch, exc=httpx.ConnectTimeout("slow"))
    with pytest.raises(SourceError) as ei:
        await lexifina.call("read_law")
    assert ei.value.status == "network"


async def test_call_jsonrpc_error(monkeypatch):
    _fake_post(monkeypatch, _resp(payload={"error": {"message": "nope"}}))
    with pytest.raises(SourceError, match="nope"):
        await lexifina.call("read_law")


async def test_call_unparseable_body(monkeypatch):
    _fake_post(monkeypatch, httpx.Response(200, content=b"<html>", request=httpx.Request("POST", lexifina.URL)))
    with pytest.raises(SourceError):
        await lexifina.call("read_law")


# ---- tools ----

@pytest.fixture
def calls(monkeypatch):
    log = []
    script = {}

    async def fake(tool, **args):
        log.append((tool, args))
        r = script.get(tool, _ok("body")["result"])
        if isinstance(r, Exception):
            raise r
        return r

    monkeypatch.setattr(lexifina, "call", fake)
    return log, script


PATH = "germany/bund/acts/grundgesetz/artikel/001.md"


async def test_path_skips_find(calls):
    log, _ = calls
    out = await server.get_law_on_date(PATH, date="2020-01-01")
    assert out.startswith(lexifina.CREDIT)
    assert [t for t, _ in log] == ["read_law"]
    assert log[0][1]["path"] == PATH and log[0][1]["date"] == "2020-01-01"


async def test_future_date_is_flagged(calls):
    out = await server.get_law_on_date(PATH, date="2999-01-01")
    assert out.startswith("Fontes: 2999-01-01 is in the future") and lexifina.CREDIT in out
    assert not (await server.get_law_on_date(PATH, date="2020-01-01")).startswith("Fontes:")
    assert (await server.get_law_on_date(PATH)).startswith("Fontes: this text was not compared")


async def test_citation_single_result(calls):
    log, script = calls
    script["find_provision"] = {"content": [], "structuredContent": {"results": [{"path": PATH}]}}
    out = await server.get_law_on_date("Art. 1 GG", date="2020-01-01")
    assert [t for t, _ in log] == ["find_provision", "read_law"]
    assert log[1][1]["path"] == PATH
    assert out.startswith(lexifina.CREDIT)


async def test_citation_read_as(calls):
    log, script = calls
    script["find_provision"] = {"content": [], "structuredContent": {
        "results": [{"path": PATH}, {"path": "x/y.md"}], "read_as": "x"}}
    await server.get_law_on_date("Art. 1 GG")
    assert log[1][1]["path"] == PATH


async def test_citation_many_results_lists_candidates(calls):
    log, script = calls
    script["find_provision"] = {"content": [{"type": "text", "text": "cand a\ncand b"}],
                                "structuredContent": {"results": [{"path": "a.md"}, {"path": "b.md"}]}}
    out = await server.get_law_on_date("Art. 1")
    assert [t for t, _ in log] == ["find_provision"]
    assert out.startswith("Fontes: that citation did not match one provision") and lexifina.CREDIT in out
    assert "cand a" in out and "Pass one of these paths" in out


async def test_citation_no_results_is_not_a_read(calls):
    log, script = calls
    script["find_provision"] = {"content": [{"type": "text", "text": "nothing"}], "structuredContent": {"results": []}}
    out = await server.get_law_on_date("Art. 1 ZZ")
    assert [t for t, _ in log] == ["find_provision"]
    assert "Pass one of these paths" not in out


async def test_source_error_message(calls):
    _, script = calls
    script["read_law"] = SourceError("busy", 429)
    out = await server.get_law_on_date(PATH)
    assert out.startswith("Error (Lexifina): busy (HTTP 429)")
    assert "not a 'no results' answer" in out


async def test_notfound_and_badrequest(calls):
    _, script = calls
    script["read_law"] = NotFound("gone")
    assert (await server.get_law_on_date(PATH)).startswith("Not found (Lexifina)")
    script["read_law"] = BadRequest("bad")
    assert (await server.get_law_on_date(PATH)).startswith("Bad request (Lexifina)")


async def test_find_error_is_reported_once(calls):
    log, script = calls
    script["find_provision"] = SourceError("down", 503)
    out = await server.get_law_on_date("Art. 1 GG")
    assert out.startswith("Error (Lexifina)")
    assert [t for t, _ in log].count("find_provision") == 1  # fails if the lookup is repeated


@pytest.mark.parametrize("bad", ["2020", "01-02-2020", "yesterday"])
async def test_bad_date(calls, bad):
    log, _ = calls
    assert (await server.get_law_on_date(PATH, date=bad)).startswith("Bad request")
    assert not log


async def test_history_requires_both_dates(calls):
    log, _ = calls
    assert (await server.get_law_history(PATH, date_a="2020-01-01")).startswith("Bad request")
    assert (await server.get_law_history(PATH, date_b="2020-01-01")).startswith("Bad request")
    assert not log


async def test_history_bad_date(calls):
    log, _ = calls
    assert (await server.get_law_history(PATH, date_a="2020", date_b="today")).startswith("Bad request")
    assert not log


async def test_history_both_dates_compare(calls):
    log, _ = calls
    out = await server.get_law_history(PATH, date_a="2000-01-01", date_b="today")
    assert log == [("compare_dates", {"path": PATH, "date_a": "2000-01-01", "date_b": "today"})]
    assert out.startswith(lexifina.CREDIT)
    assert out.startswith(lexifina.CREDIT + "\n\n" + server._RECORD_START)


async def test_history_neither_is_provision_history(calls):
    log, _ = calls
    out = await server.get_law_history(PATH)
    assert log == [("provision_history", {"path": PATH})]
    assert "started following that country's law" in out and out.index("Lexifina started") > len(lexifina.CREDIT)


async def test_disabled(calls, monkeypatch):
    log, _ = calls
    monkeypatch.setenv("WLM_LEXIFINA", "0")
    assert await server.get_law_on_date(PATH) == lexifina.OFF
    assert await server.get_law_history(PATH) == lexifina.OFF
    assert not log


@pytest.mark.parametrize("given,expected", [(5, 1000), (60000, 60000), (10**9, 100000)])
async def test_max_chars_clamped(calls, given, expected):
    log, _ = calls
    await server.get_law_on_date(PATH, max_chars=given)
    assert log[0][1]["max_chars"] == expected


async def test_offset_not_negative(calls):
    log, _ = calls
    await server.get_law_on_date(PATH, offset=-5)
    assert log[0][1]["offset"] == 0


@pytest.mark.parametrize("name", ["get_law_on_date", "get_law_history"])
def test_unknown_arguments_rejected(name):
    model = server.mcp._tool_manager.get_tool(name).fn_metadata.arg_model
    with pytest.raises(Exception, match="Unknown argument"):
        model.model_validate({"provision": "x", "year_from": "2020"})
    model.model_validate({"provision": "x"})


# ---- test-agent fixes ----

def _text(t, **s):
    return {"content": [{"type": "text", "text": t}], "structuredContent": s}


async def test_ambiguous_citation_leads_with_fontes_line(calls):
    _, script = calls
    script["find_provision"] = _text("cand a\nuse read_law", results=[{"path": "a.md"}, {"path": "b.md"}])
    out = await server.get_law_on_date("Kodeks pracy art. 154")
    assert out.startswith("Fontes: that citation did not match one provision")
    assert "also pass `jurisdiction`" in out and "pick one of the paths below" in out
    assert "cand a" in out and "use get_law_on_date" in out and "read_law" not in out
    out = await server.get_law_on_date("Kodeks pracy art. 154", jurisdiction="poland")
    assert "also pass" not in out


async def test_no_act_called_error_leads_with_fontes_line(calls):
    _, script = calls
    script["find_provision"] = BadRequest("No act called 'x' is among the act names; try search_law")
    out = await server.get_law_history("x art. 1", jurisdiction="nl")
    assert out.startswith("Fontes: that citation did not match one provision")
    assert "Bad request (Lexifina): No act called" in out and "try search_legislation" in out


async def test_before_record_start(calls):
    _, script = calls
    script["read_law"] = _text("p: the record's first version of it is the consolidated text in force on "
                               "2026-10-28 (X), where this record starts. The record does not say what it said "
                               "on 2020-01-01; it may well have been in force then.")
    out = await server.get_law_on_date(PATH, date="2020-01-01")
    assert out.startswith("Fontes: no text for 2020-01-01: Lexifina's record for this provision starts on 2026-10-28")
    script["read_law"] = _text("not yet in force on 2020-01-01")
    assert "starts later," in await server.get_law_on_date(PATH, date="2020-01-01")


async def test_history_no_difference_before_record(calls):
    _, script = calls
    script["compare_dates"] = _text("p: 0 change(s) took effect after a and on or before b. No difference in the text.")
    script["provision_history"] = _text("h", changes=[{"in_force": "2026-10-28", "kind": "baseline"}])
    out = await server.get_law_history(PATH, date_a="2024-01-01", date_b="2025-01-01")
    assert out.startswith("Fontes: Lexifina's record for this provision starts on 2026-10-28")
    out = await server.get_law_history(PATH, date_a="2024-01-01", date_b="today")
    assert "cannot show the text on 2024-01-01" in out and "when the record begins, not necessarily a change" in out
    out = await server.get_law_history(PATH, date_a="2027-01-01", date_b="today")
    assert not out.startswith("Fontes:")


async def test_history_without_dates_single_entry_is_record_start(calls):
    _, script = calls
    script["provision_history"] = _text("p: 1 change(s), oldest first.", changes=[{"in_force": "2026-10-01"}])
    assert "2026-10-01, is where Lexifina's record" in await server.get_law_history(PATH)
    script["provision_history"] = _text("p: 2 change(s), oldest first.", changes=[{"in_force": "2026-10-01"}] * 2)
    assert not (await server.get_law_history(PATH)).startswith("Fontes:")


async def test_history_dates_out_of_order(calls):
    log, _ = calls
    out = await server.get_law_history(PATH, date_a="today", date_b="2020-01-01")
    assert out == "Bad request: date_a must be on or before date_b." and not log


async def test_clamps_say_so(calls):
    log, _ = calls
    out = await server.get_law_on_date(PATH, max_chars=10**7)
    assert out.startswith("Fontes: max_chars capped at 100000.")
    assert log[0][1]["max_chars"] == 100000


def test_bounds():
    assert server._bounds(10000, 1) == (100, 1, "Fontes: limit capped at 100.\n\n")
    assert server._bounds(0, -1) == (1, 1, "Fontes: limit raised to 1; page raised to 1.\n\n")
    assert server._bounds(20, 1)[2] == ""


async def test_long_query_rejected():
    out = await server.search_legislation("gb", "x" * 501)
    assert out.startswith("Bad request: `query` is 501 characters")
    assert (await server.search_caselaw("gb", "x" * 501)).startswith("Bad request")


async def test_empty_live_search_points_to_lexifina(monkeypatch):
    from world_legal_mcp.models import Results
    registry.discover()
    j = registry.get("nl")

    async def empty(*a, **k):
        return Results(items=[], total=0)
    monkeypatch.setattr(j, "search_legislation", empty)
    assert "get_law_on_date may find it in Lexifina" in await server.search_legislation("nl", "zzz")
    monkeypatch.setenv("WLM_LEXIFINA", "0")
    assert "get_law_on_date may find" not in await server.search_legislation("nl", "zzz")


# ---- Haiku-testing fixes ----

async def test_before_record_lead_explains_not_yet_in_force(calls):
    _, script = calls
    script["read_law"] = _text("not yet in force on 2001-01-01")
    assert 'Any "not yet in force" below only means the record starts later.' in await server.get_law_on_date(
        PATH, date="2001-01-01")


async def test_echoed_input_is_escaped(monkeypatch):
    p = {"result": {"isError": True, "content": [{"type": "text", "text": "No act called 'x <script>' here"}]}}
    _fake_post(monkeypatch, _resp(payload=p))
    with pytest.raises(BadRequest) as e:
        await lexifina.call("find_provision", query="x <script>")
    assert "<" not in str(e.value) and "&lt;script&gt;" in str(e.value)


async def test_out_of_range_date(calls):
    out = await server.get_law_on_date(PATH, date="0000-01-01")
    assert "out of range" in out and "Not a date" not in out


async def test_record_end_before_requested_date(calls):
    _, script = calls
    script["read_law"] = _text("p as in force on 2026-11-27.\nNote: x: the record runs to 2026-11-06; stale.\n\nbody")
    out = await server.get_law_on_date(PATH, date="2026-11-27")
    assert "as in force on 2026-11-06, the end of Lexifina's record" in out and "as in force on 2026-11-27" not in out


async def test_whole_act_row_is_not_a_provision(calls):
    log, script = calls
    script["find_provision"] = _text("act x (the act: no file of it is 5)", read_as="act",
                                     results=[{"path": "x/act", "whole_act": True}])
    out = await server.get_law_on_date("x 5", jurisdiction="x")
    assert [t for t, _ in log] == ["find_provision"] and out.startswith("Fontes: that citation did not match")


async def test_path_without_md_is_retried_and_tool_names_mapped(calls):
    log, script = calls
    err = BadRequest("a/b/sec-1 is not a provision file (they end in .md); list_provisions shows what a folder holds.")
    script["read_law"] = err
    out = await server.get_law_on_date("a/b/sec-1", date="2020-01-01")
    assert [a["path"] for t, a in log if t == "read_law"] == ["a/b/sec-1", "a/b/sec-1.md"]
    assert "get_legislation_toc shows" in out and "search_legislation first" in out and "list_provisions" not in out


# ---- comparison with the live source ----

class _Live:
    code, name, via_lexifina = "nl", "Netherlands", False
    sources = ()
    supports = staticmethod(lambda m: True)


NL_PATH = "netherlands/national/acts/wet/1991/600-BWBR0005290/art-670.md"
NL_BODY = ("p as in force on 2026-11-27.\nNote: x: the record runs to 2026-11-05.\n\n# Artikel 670\n"
           "1°. De werkgever kan niet opzeggen gedurende de tijd dat de werknemer ongeschikt is tot het "
           "verrichten van zijn arbeid wegens ziekte en wat daar verder bij hoort in de wet")


def _live(monkeypatch, text, calls_seen=None):
    from world_legal_mcp.models import Provision

    async def fetch(j, method, *args, **kw):
        if calls_seen is not None:
            calls_seen.append(args)
        return text if isinstance(text, str) and text.startswith("Not found") else Provision(
            law_id="BWBR0005290", law_title="BW7", provision="7:670", text=text, url="https://wetten/x",
            as_of="2026-01-01")
    monkeypatch.setattr(server, "_fetch", fetch)
    monkeypatch.setattr(registry, "get", lambda c: _Live() if c == "nl" else None)


async def test_live_agrees(calls, monkeypatch):
    _, script = calls
    seen = []
    script["read_law"] = _text(NL_BODY)
    _live(monkeypatch, "**Artikel 7:670**\n\n1. De werkgever kan niet opzeggen gedurende de tijd dat de werknemer "
          "ongeschikt is tot het verrichten van zijn arbeid wegens ziekte en wat daar verder bij hoort in de wet", seen)
    out = await server.get_law_on_date(NL_PATH)
    assert seen == [("BWBR0005290", "670")]
    assert out.startswith("Fontes: the wording of the live official text (https://wetten/x; current official version, "
                          "in force since 2026-01-01) agrees")


async def test_live_differs_leads_with_official_text(calls, monkeypatch):
    _, script = calls
    script["read_law"] = _text(NL_BODY)
    _live(monkeypatch, "Artikel 7:670\n\n1. De werkgever kan niet opzeggen gedurende de tijd dat de werknemer "
          "ongeschikt is tot het verrichten van zijn werk wegens ziekte en wat daar verder bij hoort in de wet")
    out = await server.get_law_on_date(NL_PATH)
    assert out.startswith("Official source (wetten, current official version, in force since 2026-01-01): https://wetten/x")
    assert "differs from that official text" in out and "arbeid" in out and "check the official page yourself" in out
    assert out.index("differs") < out.index(lexifina.CREDIT)


async def test_live_failure_and_past_date(calls, monkeypatch):
    _, script = calls
    script["read_law"] = _text(NL_BODY)
    _live(monkeypatch, "Not found (nl): x")
    out = await server.get_law_on_date(NL_PATH)
    assert out.startswith("Fontes: this text was not compared") and "get_legislation_provision with jurisdiction nl" in out
    assert not (await server.get_law_on_date(NL_PATH, date="2020-01-01")).startswith("Fontes: this text")


def test_live_path_shapes():
    shapes = {c: (r, f) for c, r, f in server._LIVE_PATHS}
    r, f = shapes["gb"]
    assert f(r.match("united-kingdom/uk/legislation/ukpga/2006/46/section/172.md")) == ("ukpga/2006/46", "section/172")
    r, f = shapes["us"]
    assert f(r.match("united-states/federal/usc/title-11/1182.md")) == ("11 USC", "1182")


# ---- strict comparison, notes, tool names, escaping, dates ----

US_LEX = ('# 11 U.S.C. § 1182. Definitions\n\n(1) Debtor.—The term "debtor" means a small business debtor.\n\n'
          '(B) does not include--\n(iii) any member of a group of affiliated debtors that has aggregate debts of more '
          'than the limit, or an affiliate of an issuer, as defined in section 3 of the Securities Exchange Act of 1934 '
          '(15 U.S.C. 78c).')
US_LIVE = ('### §1182. Definitions\n\n(1) Debtor.—The term "debtor" means a person engaged in commercial or business '
           'activities, subject to subparagraph (B), with aggregate debts of not more than $7,500,000.\n\n'
           '(B) does not include--\n(iii) any member of a group of affiliated debtors that has aggregate debts of more '
           'than the limit, or an affiliate of a corporation described in clause (ii).\n\n'
           '(Pub. L. 116-54, § 2(a), Aug. 23, 2019, 133 Stat. 1079.)')


def test_differences_are_strict():
    assert server._differences(US_LEX, US_LIVE)          # the 1182 case: must differ
    d = server._differences(US_LEX, US_LIVE)
    # passages as written (case, punctuation, a few words of context), not lower-cased word runs
    assert 'official: "or an affiliate of a corporation described in clause (ii)."' in d
    assert "not more than $7,500,000. (B) does not include--" in d
    assert 'Lexifina: "term "debtor" means a small business debtor.' in d
    assert d.count("\n") == 3 and d.endswith("(1 more differing passages)")
    a = "**Artikel 7:670**\n\n1. De werkgever kan niet opzeggen.\n2. Dat geldt ook voor de wet."
    b = "---\nstatus: x\n---\n# Artikel 670\n\n(1) de werkgever kan niet  opzeggen\n(2) dat geldt ook voor de wet\n\n" \
        "- **C1** S. 3 excluded by act\n_2 more annotations_"
    assert server._differences(a, b) == ""                # formatting, front matter, notes only
    assert server._differences(a, a.replace("opzeggen", "ontslaan"))


async def test_live_notes_are_disclosed(calls, monkeypatch):
    _, script = calls
    script["read_law"] = _text(NL_BODY)
    _live(monkeypatch, "**Artikel 7:670**\n\n1. De werkgever kan niet opzeggen gedurende de tijd dat de werknemer "
          "ongeschikt is tot het verrichten van zijn arbeid wegens ziekte en wat daar verder bij hoort in de wet\n\n"
          "- **C1** S. 3 excluded (25.4.2024) by Some Act 2024\n- **C2** S. 3 applied by Other Act")
    out = await server.get_law_on_date(NL_PATH)
    assert "wording of the live official text" in out and "also lists notes on how this provision applies" in out
    assert "'C1 S. 3 excluded (25.4.2024) by Some Act 2024'" in out and "'C2" in out


async def test_not_compared_names_tool_only_when_live_source_works(calls, monkeypatch):
    _, script = calls
    script["read_law"] = _text(NL_BODY)
    _live(monkeypatch, "Not found (nl): x")
    monkeypatch.setattr(_Live, "supports", staticmethod(lambda m: False))
    out = await server.get_law_on_date(NL_PATH)
    assert "no active live official source for Netherlands" in out and "get_legislation_provision" not in out


def test_lexifina_tool_names_are_renamed():
    t = lexifina.tidy("try find_provision; read_law, list_provisions, compare_dates, search_law, provision_history; "
                      "list_jurisdictions; xread_law")
    assert t == ("try get_law_on_date; get_law_on_date, get_legislation_toc, get_law_history (with date_a/date_b), "
                 "search_legislation, get_law_history; list_jurisdictions; xread_law")


async def test_dates_invalid_vs_out_of_range(calls):
    assert "not a valid calendar date" in await server.get_law_on_date(PATH, date="2026-02-30")
    assert "not a valid calendar date" in await server.get_law_on_date(PATH, date="2026-13-01")
    assert "out of range" in await server.get_law_on_date(PATH, date="0000-01-01")


async def test_candidate_text_is_escaped(calls):
    _, script = calls
    script["find_provision"] = _text("No act called 'x <script>alert(1)</script>' is among the act names", results=[])
    out = await server.get_law_on_date("x <script>alert(1)</script>", jurisdiction="za")
    assert "<script>" not in out


# ---- round 5 ----

def test_leading_section_number_is_ignored():
    for lead in ("4 ", "**4** ", "4. ", "s. 4 ", "Section 4 ", "Art. 4 ", "§ 4 "):
        assert server._differences("the following characteristics are protected", lead + "the following "
                                   "characteristics are protected") == ""


async def test_live_differs_notes_official_date_after_record_end(calls, monkeypatch):
    _, script = calls
    script["read_law"] = _text(NL_BODY)
    _live(monkeypatch, "**Artikel 7:670**\n\n1. De werkgever kan niet opzeggen gedurende de tijd dat de werknemer "
          "ongeschikt is tot het verrichten van zijn werk wegens ziekte en wat daar verder bij hoort in de wet")
    out = await server.get_law_on_date(NL_PATH)
    assert ("The official text is dated 2026-01-01, after Lexifina's record ends (2026-11-05)" not in out)
    monkeypatch.setattr(server, "_fetch", lambda *a, **k: _later())
    out = await server.get_law_on_date(NL_PATH)
    assert "The official text is dated 2026-11-10, after Lexifina's record ends (2026-11-05), which may explain" in out


async def _later():
    from world_legal_mcp.models import Provision
    return Provision(law_id="x", law_title="x", provision="1", text="Artikel 7:670\n\nheel iets anders hier",
                     url="https://wetten/x", as_of="2026-11-10")


async def test_record_start_sentence_is_tagged(calls):
    _, script = calls
    script["read_law"] = _text("p was not yet in force on 2020-01-01. It first appears on 2026-10-01 (Act 1998).\nNote: n")
    out = await server.get_law_on_date(PATH, date="2020-01-01")
    assert "(Act 1998). (Fontes: this only means Lexifina's record starts on 2026-10-01.)" in out


def test_internal_tooling_lines_dropped():
    t = ("keep this\nrun scripts/world-law/bypass_placeholder.sh now\nprovisional upload, history not yet related\n"
         "pending-change: newer commit\ncommit kind(s) not recognised, read as laws: draft\n"
         "Note: x: the record runs to 2026-11-03; pending-change\nlaw note")
    assert lexifina.tidy(t) == "keep this\nNote: x: the record runs to 2026-11-03; pending-change\nlaw note"


def test_git_jargon_dropped():
    fr = ("Note: France: the record runs to 2026-11-03; the corpus has a newer commit than the one pinned here. "
          "Last checked 2026-11-20.")
    assert lexifina.tidy(fr) == "Note: France: the record runs to 2026-11-03. Last checked 2026-11-20."
    h = "- 2024-05-01: Act 4 of 2024 amended it (commit 363bccfe66)\n- 2023-01-01: first version commit 363bccfe66d1"
    assert lexifina.tidy(h) == "- 2024-05-01: Act 4 of 2024 amended it\n- 2023-01-01: first version"
    keep = "In-force trailer present. Confirmed by replay."
    assert lexifina.tidy(keep) == keep
