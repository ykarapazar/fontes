"""Fontes relay: receives opt-in usage counts and confirmed bug reports. Standard library only.

    POST /v1/stats   {"schema": 1, "version", "os", "counts": [{"day", "jurisdiction", "tool", "n"}]}
    POST /v1/bug     {"schema": 1, "version", "os", "jurisdiction", "tool", "error", "note"}
    GET  /healthz

Bodies are size-limited and checked field by field; unknown fields are rejected, so nothing
else can be stored. Counts are added into one row per (day, version, os, jurisdiction, tool):
single submissions are not kept. Bug reports go into a table only the owner reads
(`python3 relay.py bugs`). Client IPs are used in memory for rate limiting only and are never
written anywhere: no access log, no IP column.

Settings (env): RELAY_PORT (4020), RELAY_HOST (127.0.0.1), RELAY_DB (./data/relay.sqlite3).
Retention: bug reports 365 days, counts 730 days; pruned on each write.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import sys
import threading
import time
from collections import defaultdict, deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

MAX_BODY = {"/v1/stats": 64 * 1024, "/v1/bug": 8 * 1024}
RATE = {"/v1/stats": (60, 3600), "/v1/bug": (5, 3600)}   # requests per window (s) per IP (offices share one)
MAX_ROWS = 2000
BUG_DAYS, STATS_DAYS = 365, 730

VERSION = re.compile(r"^[0-9A-Za-z.+\-]{1,32}$")
OS = {"macos", "windows", "linux", "other"}
DAY = re.compile(r"^20\d\d-[01]\d-[0-3]\d$")
CODE = re.compile(r"^(?:[a-z]{2,10}|\*)$")
TOOL = re.compile(r"^[a-z_]{1,40}$")


class Invalid(ValueError):
    pass


def _check(cond: bool, what: str) -> None:
    if not cond:
        raise Invalid(what)


def _head(d: object, keys: set[str]) -> dict:
    _check(isinstance(d, dict), "body must be a JSON object")
    _check(set(d) == keys, f"fields must be exactly {sorted(keys)}")
    _check(type(d["schema"]) is int and d["schema"] == 1, "unknown schema")
    _check(isinstance(d["version"], str) and bool(VERSION.match(d["version"])), "bad version")
    _check(d["os"] in OS, "bad os")
    return d


def validate_stats(d: object) -> list[tuple]:
    d = _head(d, {"schema", "version", "os", "counts"})
    rows = d["counts"]
    _check(isinstance(rows, list) and 0 < len(rows) <= MAX_ROWS, "counts must be a list of 1..2000")
    out = []
    for r in rows:
        _check(isinstance(r, dict) and set(r) == {"day", "jurisdiction", "tool", "n"}, "bad count row")
        _check(isinstance(r["day"], str) and bool(DAY.match(r["day"])), "bad day")
        _check(isinstance(r["jurisdiction"], str) and bool(CODE.match(r["jurisdiction"])), "bad jurisdiction")
        _check(isinstance(r["tool"], str) and bool(TOOL.match(r["tool"])), "bad tool")
        _check(type(r["n"]) is int and 0 < r["n"] <= 100_000, "bad n")
        out.append((r["day"], d["version"], d["os"], r["jurisdiction"], r["tool"], r["n"]))
    return out


def validate_bug(d: object) -> tuple:
    d = _head(d, {"schema", "version", "os", "jurisdiction", "tool", "error", "note"})
    _check(d["jurisdiction"] == "" or (isinstance(d["jurisdiction"], str)
                                       and bool(CODE.match(d["jurisdiction"]))), "bad jurisdiction")
    _check(d["tool"] == "" or (isinstance(d["tool"], str) and bool(TOOL.match(d["tool"]))), "bad tool")
    _check(isinstance(d["error"], str) and len(d["error"]) <= 1000, "error must be text up to 1000")
    _check(isinstance(d["note"], str) and len(d["note"]) <= 4000, "note must be text up to 4000")
    _check(bool(d["error"].strip() or d["note"].strip()), "empty report")
    return d["version"], d["os"], d["jurisdiction"], d["tool"], d["error"], d["note"]


# --------------------------------------------------------------------------- #
# Storage
# --------------------------------------------------------------------------- #
class Store:
    def __init__(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.lock = threading.Lock()
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS counts (day TEXT, version TEXT, os TEXT, jurisdiction TEXT,
                tool TEXT, n INTEGER, PRIMARY KEY (day, version, os, jurisdiction, tool));
            CREATE TABLE IF NOT EXISTS bugs (id INTEGER PRIMARY KEY, received TEXT, version TEXT,
                os TEXT, jurisdiction TEXT, tool TEXT, error TEXT, note TEXT);
        """)

    def add_counts(self, rows: list[tuple]) -> None:
        cutoff = time.strftime("%Y-%m-%d", time.gmtime(time.time() - STATS_DAYS * 86400))
        with self.lock, self.db:
            self.db.executemany(
                "INSERT INTO counts VALUES (?,?,?,?,?,?) ON CONFLICT (day, version, os, jurisdiction, tool) "
                "DO UPDATE SET n = n + excluded.n", rows)
            self.db.execute("DELETE FROM counts WHERE day < ?", (cutoff,))

    def add_bug(self, bug: tuple) -> None:
        now = time.time()
        with self.lock, self.db:
            self.db.execute("INSERT INTO bugs (received, version, os, jurisdiction, tool, error, note) "
                            "VALUES (?,?,?,?,?,?,?)", (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)), *bug))
            self.db.execute("DELETE FROM bugs WHERE received < ?",
                            (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now - BUG_DAYS * 86400)),))


class Limiter:
    """Sliding-window request counts per (IP, path), in memory only."""

    def __init__(self):
        self.hits: dict[tuple, deque] = defaultdict(deque)
        self.lock = threading.Lock()

    def allow(self, ip: str, path: str, now: float | None = None) -> bool:
        limit, window = RATE[path]
        now = time.monotonic() if now is None else now
        with self.lock:
            q = self.hits[(ip, path)]
            while q and q[0] <= now - window:
                q.popleft()
            if len(q) >= limit:
                return False
            q.append(now)
            if len(self.hits) > 50_000:   # bound memory: forget idle entries
                for k in [k for k, v in self.hits.items() if not v or v[-1] <= now - window]:
                    del self.hits[k]
            return True


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #
class Handler(BaseHTTPRequestHandler):
    store: Store
    limiter: Limiter
    server_version = "fontes-relay"
    sys_version = ""

    def log_message(self, *args) -> None:   # the default writes client IPs to stderr
        pass

    def _reply(self, code: int, body: dict) -> None:
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _ip(self) -> str:
        peer = self.client_address[0]
        # Behind nginx on the same host: trust its X-Real-IP, nobody else's.
        if peer in ("127.0.0.1", "::1"):
            return self.headers.get("X-Real-IP", peer)
        return peer

    def do_GET(self) -> None:
        if self.path == "/healthz":
            self._reply(200, {"ok": True})
        else:
            self._reply(404, {"error": "not found"})

    def do_POST(self) -> None:
        path = self.path
        if path not in MAX_BODY:
            return self._reply(404, {"error": "not found"})
        try:
            size = int(self.headers.get("Content-Length", ""))
        except ValueError:
            return self._reply(411, {"error": "length required"})
        if size <= 0 or size > MAX_BODY[path]:
            return self._reply(413, {"error": "too large"})
        if not self.limiter.allow(self._ip(), path):
            return self._reply(429, {"error": "too many requests"})
        try:
            body = json.loads(self.rfile.read(size))
            if path == "/v1/stats":
                self.store.add_counts(validate_stats(body))
            else:
                self.store.add_bug(validate_bug(body))
        except (ValueError, KeyError, TypeError) as e:   # Invalid and JSON errors are ValueErrors
            return self._reply(400, {"error": str(e) if isinstance(e, Invalid) else "invalid body"})
        self._reply(200, {"ok": True})


def make_server(host: str, port: int, db: str) -> ThreadingHTTPServer:
    handler = type("H", (Handler,), {"store": Store(db), "limiter": Limiter()})
    return ThreadingHTTPServer((host, port), handler)


def print_bugs(db: str) -> None:
    con = sqlite3.connect(db)
    for row in con.execute("SELECT id, received, version, os, jurisdiction, tool, error, note "
                           "FROM bugs ORDER BY id DESC LIMIT 50"):
        print("#{} {} v{} {} {}/{}\n  error: {}\n  note: {}\n".format(*row))


def main(argv: list[str]) -> int:
    here = Path(__file__).resolve().parent
    db = os.environ.get("RELAY_DB") or str(here / "data/relay.sqlite3")
    if argv[:1] == ["bugs"]:
        print_bugs(db)
        return 0
    host = os.environ.get("RELAY_HOST", "127.0.0.1")
    port = int(os.environ.get("RELAY_PORT", "4020"))
    srv = make_server(host, port, db)
    print(f"fontes-relay listening on {host}:{port}", flush=True)
    srv.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
