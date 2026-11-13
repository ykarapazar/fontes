"""Fontes launcher: start an MCP server from PyPI and keep it up to date, quietly.

MCP clients (Claude Desktop, Codex) run this instead of the server itself:

    uv run --managed-python --python 3.13 --no-project --quiet fontes_launcher.py fontes [args]

(--managed-python: only uv's own Python, never a system one; on a Mac without developer
tools, probing /usr/bin/python3 would pop up an "install developer tools" dialog.)

What it does on every start:
  1. Runs the last version known to work, pinned (`uv tool run --from PKG==VER CMD`).
     A pinned, already-cached version starts without touching the network.
  2. At most once a day, starts a separate background process that asks PyPI for the
     latest version, installs it into uv's cache and checks that it imports. Only if
     that succeeds does it become the "good" version used from the next start on.
     A failed or slow update never touches the version that works.

Standard library only (it must run before anything is installed). Settings:
  FONTES_NO_AUTO_UPDATE=1  never look for or install updates
  FONTES_FROM=<path|url>   run from that source instead of PyPI (development; no updates)
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

# The PyPI package behind the server. Renaming Fontes on PyPI = change "package" here.
APPS = {
    "fontes": {"package": "fontes-mcp", "command": "fontes",
               "check": "import world_legal_mcp.server"},
}
CHECK_EVERY = 24 * 3600   # seconds between update checks
PYPI_TIMEOUT = 5          # seconds; runs in the background, never delays the server
INSTALL_TIMEOUT = 600     # seconds for downloading + checking a new version


def state_dir() -> Path:
    if d := os.environ.get("FONTES_STATE_DIR"):
        return Path(d)
    if sys.platform == "win32":
        return Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData/Local") / "Fontes"
    if sys.platform == "darwin":
        return Path.home() / "Library/Application Support/Fontes"
    return Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local/state") / "fontes"


def _state_file(app: str) -> Path:
    return state_dir() / f"{app}.json"


def load_state(app: str) -> dict:
    try:
        return json.loads(_state_file(app).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_state(app: str, state: dict) -> None:
    f = _state_file(app)
    f.parent.mkdir(parents=True, exist_ok=True)
    tmp = f.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=1), encoding="utf-8")
    os.replace(tmp, f)


def uv_path() -> str:
    # `uv run` exports UV = its own path to the processes it starts.
    return os.environ.get("UV") or shutil.which("uv") or "uv"


def parse_version(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in re.findall(r"\d+", v.split("+")[0])[:4])


def latest_on_pypi(package: str, timeout: float = PYPI_TIMEOUT) -> str | None:
    url = f"https://pypi.org/pypi/{package}/json"
    req = urllib.request.Request(url, headers={"User-Agent": "Fontes-launcher"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)["info"]["version"]
    except Exception:
        return None


def due(state: dict, now: float | None = None) -> bool:
    return (now or time.time()) - state.get("checked", 0) >= CHECK_EVERY


def run_command(app: str, args: list[str], state: dict) -> list[str]:
    spec = APPS[app]
    source = os.environ.get("FONTES_FROM")
    if source:
        frm = source
    elif state.get("good"):
        frm = f"{spec['package']}=={state['good']}"
    else:
        frm = spec["package"]
    return [uv_path(), "tool", "run", "--managed-python", "--from", frm, spec["command"], *args]


def cached(app: str, state: dict, run=subprocess.run) -> bool:
    """True if the pinned good version starts from uv's cache alone. Without --offline, uv
    re-checks the index once its cached copy is older than PyPI's max-age (10 minutes) and
    fails outright when there is no network."""
    spec = APPS[app]
    cmd = [uv_path(), "tool", "run", "--offline", "--quiet", "--managed-python",
           "--from", f"{spec['package']}=={state['good']}", "python", "-c", ""]
    try:
        return run(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, timeout=60).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def verify_code(spec: dict) -> str:
    """Python run inside a candidate version: it must import and provide the command."""
    return (f"import shutil, sys; {spec['check']}; "
            f"sys.exit(shutil.which({spec['command']!r}) is None)")


def update(app: str, fetch=latest_on_pypi, run=subprocess.run) -> str:
    """Install and verify the latest version; record it as good only if it works.

    Returns a short status word (used by tests and the installer)."""
    spec = APPS[app]
    state = load_state(app)
    state["checked"] = time.time()
    save_state(app, state)
    latest = fetch(spec["package"])
    if not latest:
        return "offline"
    good = state.get("good")
    if good and parse_version(latest) <= parse_version(good):
        return "current"
    cmd = [uv_path(), "tool", "run", "--quiet", "--managed-python",
           "--from", f"{spec['package']}=={latest}",
           "python", "-c", verify_code(spec)]
    try:
        ok = run(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                 stderr=subprocess.DEVNULL, timeout=INSTALL_TIMEOUT).returncode == 0
    except (OSError, subprocess.SubprocessError):
        ok = False
    state = load_state(app)
    if not ok:
        state["failed"] = latest
        save_state(app, state)
        return "failed"
    state.update(good=latest, updated=time.time())
    state.pop("failed", None)
    save_state(app, state)
    return "updated"


def start_background_update(app: str) -> None:
    """Run `update` in a detached process so the server starts right away."""
    cmd = [sys.executable, os.path.abspath(__file__), "--update", app]
    kw: dict = {"stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL,
                "stderr": subprocess.DEVNULL, "close_fds": True}
    if sys.platform == "win32":
        kw["creationflags"] = 0x00000008 | 0x00000200 | 0x08000000  # detached, new group, no window
    else:
        kw["start_new_session"] = True
    try:
        subprocess.Popen(cmd, **kw)
    except OSError:
        pass


def main(argv: list[str]) -> int:
    if argv[:1] == ["--update"]:
        print(update(argv[1]))
        return 0
    app = argv[0] if argv and argv[0] in APPS else "fontes"
    args = argv[1:] if argv and argv[0] in APPS else argv
    state = load_state(app)
    if (not os.environ.get("FONTES_NO_AUTO_UPDATE") and not os.environ.get("FONTES_FROM")
            and due(state)):
        start_background_update(app)
    cmd = run_command(app, args, state)
    if state.get("good") and not os.environ.get("FONTES_FROM") and cached(app, state):
        cmd.insert(3, "--offline")
    if sys.platform == "win32":  # exec on Windows breaks the client's stdio pipes
        return subprocess.call(cmd)
    os.execvp(cmd[0], cmd)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
