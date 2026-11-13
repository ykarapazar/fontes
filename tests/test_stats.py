"""Opt-in usage counts, offline: off by default, only code + tool + count ever leave."""
import json
import time

import pytest

from world_legal_mcp import server, stats

SECRET_QUERY = "huurprijs Ayşe Yılmaz SECRETQ"
SECRET_ID = "ECLI:NL:HR:2099:SECRETID"


class Resp:
    def __init__(self, status):
        self.status_code = status


@pytest.fixture
def cache(tmp_path, monkeypatch):
    monkeypatch.setenv("FONTES_CACHE_DIR", str(tmp_path))
    monkeypatch.delenv("FONTES_STATS", raising=False)
    sends = []
    monkeypatch.setattr(stats, "_start_send", lambda: sends.append(1))

    async def fake_fetch(j, method, *args, **kw):
        return f"Error ({j.code}): source down"
    monkeypatch.setattr(server, "_fetch", fake_fetch)
    return tmp_path, sends


async def use_tools():
    await server.search_caselaw("nl", SECRET_QUERY, filters=None)
    await server.get_decision("nl", SECRET_ID)
    await server.search_caselaw("client Ayşe SECRETJ", "x")   # unknown jurisdiction: not counted


async def test_off_by_default_nothing_written_or_sent(cache):
    tmp, sends = cache
    assert not stats.enabled()
    await use_tools()
    stats.record("nl", "search_caselaw")
    assert not stats.stats_file().exists() and sends == []


async def test_payload_holds_only_version_os_and_counts(cache, monkeypatch):
    monkeypatch.setenv("FONTES_STATS", "1")
    await use_tools()
    await use_tools()
    raw = stats.stats_file().read_text(encoding="utf-8")
    body = stats.payload(json.loads(raw)["days"], version="0.1.0")
    sent = json.dumps(body, ensure_ascii=False)
    for leak in ("SECRET", "Ayşe", "huurprijs", "ECLI", "client"):
        assert leak not in raw and leak not in sent
    assert set(body) == {"schema", "version", "os", "counts"}
    assert body["os"] in {"macos", "windows", "linux", "other"}
    today = time.strftime("%Y-%m-%d", time.gmtime())
    assert body["counts"] == [
        {"day": today, "jurisdiction": "nl", "tool": "get_decision", "n": 2},
        {"day": today, "jurisdiction": "nl", "tool": "search_caselaw", "n": 2},
    ]


def test_record_drops_anything_not_shaped_like_a_code_or_tool(cache, monkeypatch):
    monkeypatch.setenv("FONTES_STATS", "1")
    for code, tool in [("Ayşe", "search_caselaw"), ("nl x", "get_decision"),
                       ("nl", "rm -rf"), ("ECLI:NL", "get_decision")]:
        stats.record(code, tool)
    assert not stats.stats_file().exists()


def test_send_once_a_day_clears_on_success_keeps_on_failure(cache, monkeypatch):
    tmp, sends = cache
    monkeypatch.setenv("FONTES_STATS", "1")
    stats.record("gb", "search_legislation")
    assert sends == [1]                                    # never sent before: due now
    posted = []
    assert not stats.send(post=lambda url, json, timeout: posted.append(json) or Resp(503))
    assert json.loads(stats.stats_file().read_text())["days"]   # kept for the next try
    def boom(url, json, timeout):
        raise OSError("no network")
    assert not stats.send(post=boom)                        # silent
    assert stats.send(post=lambda url, json, timeout: posted.append((url, timeout)) or Resp(200))
    assert posted[-1] == ("http://127.0.0.1:9/v1/stats", stats.TIMEOUT)
    assert json.loads(stats.stats_file().read_text())["days"] == {}
    stats.record("gb", "search_legislation")
    assert sends == [1]                                    # sent just now: not again today


def test_record_never_raises(tmp_path, monkeypatch):
    f = tmp_path / "file"
    f.write_text("x")
    monkeypatch.setenv("FONTES_CACHE_DIR", str(f / "sub"))   # cannot be created
    monkeypatch.setenv("FONTES_STATS", "1")
    stats.record("nl", "search_caselaw")
