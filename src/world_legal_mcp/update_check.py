"""Once-a-day "a newer Fontes exists" notice, shown in list_jurisdictions.

Never blocks: `notice()` only reads a small cache file. When that file is older than a day
it starts a background thread that asks PyPI for the latest version and rewrites it, so the
notice shows from the next call on. Off with FONTES_NO_UPDATE_CHECK=1. No data is sent
except the request itself (same as `pip install`).
"""
from __future__ import annotations

import json
import os
import re
import sys
import threading
import time
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import httpx

PACKAGE = "fontes-mcp"  # PyPI distribution name
CHECK_EVERY = 24 * 3600
TIMEOUT = 5.0
_started = False


def cache_file() -> Path:
    if d := os.environ.get("FONTES_CACHE_DIR"):
        base = Path(d)
    elif sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData/Local") / "Fontes/Cache"
    elif sys.platform == "darwin":
        base = Path.home() / "Library/Caches/Fontes"
    else:
        base = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "fontes"
    return base / "update-check.json"


def _vtuple(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in re.findall(r"\d+", v.split("+")[0])[:4])


def installed_version() -> str | None:
    try:
        return version(PACKAGE)
    except PackageNotFoundError:
        return None


def refresh(get=httpx.get) -> None:
    """Fetch the latest version from PyPI and cache it. Errors are cached as 'unknown'."""
    latest = None
    try:
        r = get(f"https://pypi.org/pypi/{PACKAGE}/json", timeout=TIMEOUT)
        if r.status_code == 200:
            latest = r.json()["info"]["version"]
    except Exception:
        pass
    f = cache_file()
    try:
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps({"checked": time.time(), "latest": latest}), encoding="utf-8")
    except OSError:
        pass


def notice(current: str | None = None) -> str:
    """One line if a newer release is known, else "". Schedules a refresh when stale."""
    global _started
    if os.environ.get("FONTES_NO_UPDATE_CHECK"):
        return ""
    current = current or installed_version()
    if not current:
        return ""
    try:
        cached = json.loads(cache_file().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        cached = {}
    if time.time() - cached.get("checked", 0) >= CHECK_EVERY and not _started:
        _started = True
        threading.Thread(target=refresh, daemon=True).start()
    latest = cached.get("latest")
    if latest and _vtuple(latest) > _vtuple(current):
        return (f"ℹ Fontes {latest} is available (this is {current}). If you used the Fontes "
                "installer it updates itself: restart Claude or Codex. Otherwise run "
                f"`uv tool upgrade {PACKAGE}` (or use `uvx {PACKAGE}@latest`).")
    return ""
