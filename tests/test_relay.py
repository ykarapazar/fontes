"""relay/relay.py, offline: validation, limits, rate limiting, storage without IPs.

The end-to-end test runs the relay on 127.0.0.1 (random port) and points the client at it."""
import json
import sqlite3
import sys
import threading
from pathlib import Path

import httpx
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "relay"))
import relay as R

from world_legal_mcp import bugreport, stats

STATS = {"schema": 1, "version": "0.1.0", "os": "macos",
         "counts": [{"day": "2026-11-10", "jurisdiction": "nl", "tool": "search_caselaw", "n": 3}]}
BUG = {"schema": 1, "version": "0.1.0", "os": "windows", "jurisdiction": "gb",
       "tool": "get_decision", "error": "Error (gb): HTTP 500", "note": ""}


def with_(base, path, value):
    d = json.loads(json.dumps(base))
    target = d["counts"][0] if path[0] == "counts" else d
    target[path[-1]] = value
    return d


def test_valid_bodies_pass():
    assert R.validate_stats(STATS) == [("2026-11-10", "0.1.0", "macos", "nl", "search_caselaw", 3)]
    assert R.validate_bug(BUG)[2:4] == ("gb", "get_decision")


@pytest.mark.parametrize("body", [
    {**STATS, "query": "huurprijs"},                       # unknown field
    {**STATS, "install_id": "abc"},
    with_(STATS, ["counts", "q"], "x"),                     # unknown field in a row
    with_(STATS, ["counts", "jurisdiction"], "client Ayşe"),
    with_(STATS, ["counts", "tool"], "DROP TABLE"),
    with_(STATS, ["counts", "n"], 0),
    with_(STATS, ["counts", "n"], True),
    with_(STATS, ["counts", "day"], "yesterday"),
    {**STATS, "os": "TempleOS"},
    {**STATS, "version": "x" * 40},
    {**STATS, "schema": True},
    {**STATS, "counts": []},
    {**STATS, "counts": STATS["counts"] * (R.MAX_ROWS + 1)},
    [STATS],
])
def test_bad_stats_rejected(body):
    with pytest.raises(R.Invalid):
        R.validate_stats(body)


@pytest.mark.parametrize("body", [
    {**BUG, "ip": "1.2.3.4"},
    {**BUG, "error": "e" * 1001},
    {**BUG, "note": "n" * 4001},
    {**BUG, "error": "", "note": "  "},
    {**BUG, "jurisdiction": "nl; rm"},
    {**BUG, "note": 5},
])
def test_bad_bugs_rejected(body):
    with pytest.raises(R.Invalid):
        R.validate_bug(body)


def test_rate_limit_per_ip_and_path():
    lim = R.Limiter()
    n, window = R.RATE["/v1/bug"]
    assert all(lim.allow("a", "/v1/bug", now=100.0) for _ in range(n))
    assert not lim.allow("a", "/v1/bug", now=100.0)
    assert lim.allow("b", "/v1/bug", now=100.0) and lim.allow("a", "/v1/stats", now=100.0)
    assert lim.allow("a", "/v1/bug", now=100.0 + window + 1)


@pytest.fixture
def relay(tmp_path, monkeypatch):
    db = tmp_path / "r.sqlite3"
    srv = R.make_server("127.0.0.1", 0, str(db))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}"
    monkeypatch.setenv("FONTES_RELAY", url)
    monkeypatch.setenv("FONTES_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("FONTES_STATS", "1")
    monkeypatch.setattr(stats, "_start_send", lambda: None)
    yield url, db
    srv.shutdown()


def test_end_to_end_client_to_relay_stores_no_ip(relay, capsys):
    url, db = relay
    for _ in range(2):
        stats.record("nl", "search_caselaw")
    assert stats.send()
    stats.record("nl", "search_caselaw")
    assert stats.send()                                    # summed, not one row per post
    bugreport.remember("gb", "get_decision", "Error (gb): HTTP 500")
    assert bugreport.cli(["--note", "decision page empty"], ask=lambda p: "y") == 0
    assert httpx.post(f"{url}/v1/bug", content=b"{", headers={"Content-Type": "application/json"}).status_code == 400
    assert httpx.post(f"{url}/v1/bug", content=b"x" * (R.MAX_BODY["/v1/bug"] + 1)).status_code == 413
    assert httpx.post(f"{url}/v1/nope", json={}).status_code == 404
    con = sqlite3.connect(db)
    assert con.execute("SELECT jurisdiction, tool, n FROM counts").fetchall() == [("nl", "search_caselaw", 3)]
    assert con.execute("SELECT tool, note FROM bugs").fetchall() == [("get_decision", "decision page empty")]
    dump = "\n".join(con.iterdump())
    assert "127.0.0.1" not in dump and "ip" not in {c[1] for t in ("counts", "bugs")
                                                    for c in con.execute(f"PRAGMA table_info({t})")}
