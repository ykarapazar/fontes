"""Bug reports, offline: inputs are cut out, and nothing is sent without the user's yes."""
import json
from types import SimpleNamespace

import pytest

from world_legal_mcp import bugreport, registry, server
from world_legal_mcp.base import SourceError

QUERY = "kira artışı Ayşe Yılmaz"


@pytest.fixture(autouse=True)
def cache(tmp_path, monkeypatch):
    monkeypatch.setenv("FONTES_CACHE_DIR", str(tmp_path))
    monkeypatch.setattr(bugreport, "_last", None)


def poster():
    calls = []
    def post(url, json, timeout):
        calls.append((url, json))
        return SimpleNamespace(status_code=200)
    return post, calls


def test_redact_removes_inputs_plain_and_url_encoded_and_query_strings():
    msg = (f"Bad answer for {QUERY} at https://x.gov/search?q=kira+art%C4%B1%C5%9F%C4%B1 "
           "and https://x.gov/doc/ECLI%3ANL%3AHR%3A2024%3A1")
    out = bugreport.redact(msg, (QUERY, "ECLI:NL:HR:2024:1"))
    assert "Ayşe" not in out and "kira" not in out and "ECLI" not in out
    assert "https://x.gov/search?[removed]" in out


async def test_failed_call_is_remembered_without_its_inputs(monkeypatch):
    j = registry.get("nl")
    async def fail(query, **kw):
        raise SourceError(f"no results page for '{query}'", 502)
    monkeypatch.setattr(j, "search_caselaw", fail)
    out = await server._fetch(j, "search_caselaw", QUERY, limit=1, page=1, filters={"court": "Hof Ayşe"})
    assert QUERY in out                                   # the user still sees their own error
    last = json.loads(bugreport.last_error_file().read_text(encoding="utf-8"))
    assert last["jurisdiction"] == "nl" and last["tool"] == "search_caselaw"
    assert "Ayşe" not in last["error"] and "[removed]" in last["error"]
    r = bugreport.build()
    assert set(r) == {"schema", "version", "os", "jurisdiction", "tool", "error", "note"}
    assert r["note"] == "" and "Ayşe" not in json.dumps(r, ensure_ascii=False)


def elicit_answer(action, send=None):
    async def elicit(message, schema):
        assert "Send this report" in message
        return SimpleNamespace(action=action, data=None if send is None else schema(send=send))
    return elicit


@pytest.mark.parametrize("elicit", [
    elicit_answer("decline"), elicit_answer("cancel"), elicit_answer("accept", send=False), None,
])
async def test_mcp_tool_sends_nothing_without_confirmation(elicit):
    post, calls = poster()
    out = await bugreport.confirm_and_send(bugreport.build("it broke"), elicit, post=post)
    assert calls == [] and "Not sent" in out


async def test_mcp_tool_without_dialog_support_explains_how_to_send():
    async def unsupported(message, schema):
        raise RuntimeError("client does not support elicitation")
    post, calls = poster()
    out = await bugreport.confirm_and_send(bugreport.build("x"), unsupported, post=post)
    assert calls == [] and "fontes-mcp report-bug" in out and bugreport.ISSUES_URL in out


async def test_mcp_tool_sends_exactly_the_shown_report_after_yes():
    post, calls = poster()
    report = bugreport.build("toc empty for nl")
    out = await bugreport.confirm_and_send(report, elicit_answer("accept", send=True), post=post)
    assert out.endswith("Sent. Thank you.")
    assert calls == [("http://127.0.0.1:9/v1/bug", report)]


@pytest.mark.parametrize("answer", ["", "n", "no", "evet?", EOFError])
def test_cli_needs_explicit_yes(answer, capsys):
    post, calls = poster()
    def ask(prompt):
        if answer is EOFError:
            raise EOFError
        return answer
    assert bugreport.cli(["--note", "x"], ask=ask, post=post) == 0
    assert calls == [] and "Not sent." in capsys.readouterr().out


def test_cli_sends_after_yes_and_shows_report_first(capsys):
    post, calls = poster()
    assert bugreport.cli(["--note", "slow"], ask=lambda p: "y", post=post) == 0
    out = capsys.readouterr().out
    assert out.index("Fontes bug report") < out.index("Sent.")
    assert len(calls) == 1 and calls[0][1]["note"] == "slow"


def test_cli_failure_is_reported_not_raised(capsys):
    def post(url, json, timeout):
        raise OSError("dns")
    assert bugreport.cli(["--note", "x"], ask=lambda p: "yes", post=post) == 1
    assert bugreport.ISSUES_URL in capsys.readouterr().out


async def test_empty_report_is_not_offered():
    post, calls = poster()
    assert bugreport.cli([], ask=lambda p: pytest.fail("asked"), post=post) == 1
    assert await bugreport.confirm_and_send(bugreport.build(), elicit_answer("accept", True), post=post) == bugreport.t("bug_empty")
    assert calls == []
