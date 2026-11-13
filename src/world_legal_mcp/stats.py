"""Opt-in usage counts. Off unless FONTES_STATS=1 (the installer asks; default no).

All that is ever sent: the Fontes version, the OS family, and per UTC day how many calls each
tool got per jurisdiction code. No search text, no ids, no document text, no user or install
id. Counters live in <cache dir>/stats.json. At most once a day a background thread posts
them to <relay>/v1/stats (3 s timeout) and forgets what was accepted; a failure is silent and
keeps the counts for the next try. Nothing here can delay or break a tool call.
See docs/PRIVACY.md. The relay base URL is RELAY_URL, or FONTES_RELAY to override.
"""
from __future__ import annotations

import json
import os
import re
import sys
import threading
import time
from pathlib import Path

import httpx

from . import update_check

RELAY_URL = "https://relay.kinetra.fit"
SEND_EVERY = 24 * 3600
TIMEOUT = 3.0
KEEP_DAYS = 31           # unsent days older than this are dropped
_CODE = re.compile(r"^(?:[a-z]{2,10}|\*)$")   # a registry code, or * for list_jurisdictions
_TOOL = re.compile(r"^[a-z_]{1,40}$")
_lock = threading.Lock()
_sending = False


def relay_url() -> str:
    return (os.environ.get("FONTES_RELAY") or RELAY_URL).rstrip("/")


def enabled() -> bool:
    return os.environ.get("FONTES_STATS", "").strip().lower() in ("1", "true", "yes", "on")


def os_family() -> str:
    if sys.platform == "darwin":
        return "macos"
    if sys.platform == "win32":
        return "windows"
    return "linux" if sys.platform.startswith("linux") else "other"


def stats_file() -> Path:
    return update_check.cache_file().parent / "stats.json"


def _load() -> dict:
    try:
        d = json.loads(stats_file().read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def _save(d: dict) -> None:
    f = stats_file()
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(d), encoding="utf-8")


def _today() -> str:
    return time.strftime("%Y-%m-%d", time.gmtime())


def record(jurisdiction: str, tool: str) -> None:
    """Count one call. Only a known-shape code and tool name are kept; anything else is dropped."""
    if not enabled() or not _CODE.match(jurisdiction) or not _TOOL.match(tool):
        return
    try:
        with _lock:
            d = _load()
            day = d.setdefault("days", {}).setdefault(_today(), {})
            key = f"{jurisdiction} {tool}"
            day[key] = day.get(key, 0) + 1
            _save(d)
            due = time.time() - d.get("sent", 0) >= SEND_EVERY
        if due:
            _start_send()
    except Exception:
        pass


def payload(days: dict[str, dict[str, int]], version: str | None = None) -> dict:
    """The exact JSON body sent to the relay."""
    rows = []
    for day, counts in sorted(days.items()):
        for key, n in sorted(counts.items()):
            code, _, tool = key.partition(" ")
            rows.append({"day": day, "jurisdiction": code, "tool": tool, "n": int(n)})
    return {"schema": 1, "version": version or update_check.installed_version() or "dev",
            "os": os_family(), "counts": rows}


def _merge_back(days: dict) -> None:
    with _lock:
        d = _load()
        cur = d.setdefault("days", {})
        for day, counts in days.items():
            for k, n in counts.items():
                cur.setdefault(day, {})[k] = cur.get(day, {}).get(k, 0) + n
        oldest = time.strftime("%Y-%m-%d", time.gmtime(time.time() - KEEP_DAYS * 86400))
        d["days"] = {k: v for k, v in cur.items() if k >= oldest}
        _save(d)


def send(post=httpx.post) -> bool:
    """Post the stored counts once. True if the relay accepted them (or there was nothing)."""
    with _lock:
        d = _load()
        days = d.get("days") or {}
        d.update(sent=time.time(), days={})
        _save(d)
    if not days:
        return True
    try:
        r = post(f"{relay_url()}/v1/stats", json=payload(days), timeout=TIMEOUT)
        ok = 200 <= r.status_code < 300
    except Exception:
        ok = False
    if not ok:
        try:
            _merge_back(days)
        except Exception:
            pass
    return ok


def _start_send() -> None:
    global _sending
    if _sending:
        return
    _sending = True

    def run():
        global _sending
        try:
            send()
        except Exception:
            pass
        finally:
            _sending = False
    threading.Thread(target=run, daemon=True).start()
