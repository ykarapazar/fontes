"""Fontes setup: add (or remove) Fontes in the MCP apps it finds: Claude Desktop, Codex,
Claude Code, Cursor, VS Code, Windsurf, Gemini CLI, Zed, LM Studio and Cline.

Run by the double-click wrappers once uv is present:

    uv run --managed-python --python 3.13 --no-project fontes_setup.py install|keys|uninstall

`keys` asks for the optional free API keys (France, United States) and saves them in the `env`
of our entry in every app that has it; `install` asks the same right after setting up.

It only ever touches its own entry ("fontes"); every other entry,
setting and comment in the config files stays as it was. Before changing a file it saves a
copy next to it (`<file>.fontes-backup-<time>`). Running it again changes nothing.

Paths follow HOME / APPDATA / LOCALAPPDATA / XDG_CONFIG_HOME / CODEX_HOME / CLAUDE_CONFIG_DIR,
so tests can point them at a throwaway folder.
"""
from __future__ import annotations

import argparse
import getpass
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time
import tomllib
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fontes_i18n as i18n
import fontes_launcher as launcher

LAUNCHER_NAME = "fontes_launcher.py"

# All user-facing text is in locales/<lang>.json (see fontes_i18n.py for how the language is chosen).
t = i18n.t


# --------------------------------------------------------------------------- #
# Where things live
# --------------------------------------------------------------------------- #
def claude_configs() -> list[Path]:
    if sys.platform == "win32":
        appdata = Path(os.environ.get("APPDATA") or Path.home() / "AppData/Roaming")
        paths = [appdata / "Claude/claude_desktop_config.json"]
        # Claude from the Microsoft Store keeps its settings in a per-package folder.
        local = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData/Local")
        for d in glob.glob(os.path.join(local, "Packages", "Claude_*", "LocalCache", "Roaming", "Claude")):
            paths.append(Path(d) / "claude_desktop_config.json")
        return paths
    if sys.platform == "darwin":
        return [Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"]
    return [Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config") / "Claude/claude_desktop_config.json"]


def claude_desktop_present() -> bool:
    """Claude Desktop itself, or a settings folder it made. Call before configure(), which
    writes its settings file whether or not the app is there (so a later install finds Fontes)."""
    if sys.platform == "win32":
        local = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData/Local")
        if Path(local, "AnthropicClaude").exists() or glob.glob(os.path.join(local, "Packages", "Claude_*")):
            return True
    elif sys.platform == "darwin":
        if any(p.exists() for p in (Path("/Applications/Claude.app"), Path.home() / "Applications/Claude.app")):
            return True
    else:
        return True  # no official Linux app to look for
    return any(p.parent.exists() for p in claude_configs())


def codex_config() -> Path:
    return Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex") / "config.toml"


def user_config_dir() -> Path:
    """Where desktop apps keep per-user settings: Application Support, %APPDATA%, ~/.config."""
    if sys.platform == "win32":
        return Path(os.environ.get("APPDATA") or Path.home() / "AppData/Roaming")
    if sys.platform == "darwin":
        return Path.home() / "Library/Application Support"
    return Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")


class Client(NamedTuple):
    name: str
    path: Path                 # the config file we edit
    kind: str = "JSON"         # "JSON" (comments allowed) or "TOML"
    key: str = "mcpServers"    # the object that holds the servers
    detect: tuple = ()         # any of these present = app installed; () = always (Claude Desktop)
    extra: dict = {}           # fields the app wants in each entry besides command/args/env


def clients() -> list[Client]:
    """Every app we set up, with its user-level config file (paths checked against each app's
    docs on 2026-11-11). Windows paths for the apps without Windows docs follow the macOS ones
    and are untested."""
    home, cfg = Path.home(), user_config_dir()
    xdg = Path(os.environ.get("XDG_CONFIG_HOME") or home / ".config")
    claude_code = Path(os.environ.get("CLAUDE_CONFIG_DIR") or home) / ".claude.json"
    copilot = Path(os.environ.get("COPILOT_HOME") or home / ".copilot")
    # Windsurf: current builds read devin/mcp_config.json; older ones ~/.codeium/windsurf.
    devin = (cfg if sys.platform == "win32" else xdg) / "devin"
    windsurf = devin if devin.exists() else home / ".codeium/windsurf"
    zed = cfg / "Zed" if sys.platform == "win32" else xdg / "zed"
    return [
        *(Client("Claude Desktop", p) for p in claude_configs()),
        Client("Codex", codex_config(), "TOML", "mcp_servers", (codex_config().parent,)),
        Client("Claude Code", claude_code, detect=(claude_code,)),
        Client("Cursor", home / ".cursor/mcp.json", detect=(home / ".cursor",)),
        # VS Code: the documented user file for Copilot (not the profile mcp.json, whose path is
        # undocumented and whose reader is deprecated).
        Client("VS Code", copilot / "mcp-config.json", detect=(copilot, cfg / "Code/User"),
               extra={"type": "stdio"}),
        Client("Windsurf", windsurf / "mcp_config.json", detect=(windsurf,)),
        Client("Gemini CLI", home / ".gemini/settings.json", detect=(home / ".gemini",)),
        Client("Zed", zed / "settings.json", key="context_servers", detect=(zed,)),
        Client("LM Studio", home / ".lmstudio/mcp.json", detect=(home / ".lmstudio",)),
        # Cline's documented global file, shared by its IDE, CLI and SDK builds.
        Client("Cline", home / ".cline/data/settings/cline_mcp_settings.json", detect=(home / ".cline",)),
    ]


def find_uv() -> str | None:
    exe = "uv.exe" if sys.platform == "win32" else "uv"
    for c in (os.environ.get("UV"), shutil.which("uv"),
              str(Path.home() / ".local/bin" / exe), str(Path.home() / ".cargo/bin" / exe)):
        if c and Path(c).is_file():
            return str(Path(c).resolve())
    return None


def entry(uv: str, app: str, env: dict[str, str]) -> dict:
    """The command an MCP client runs for one of our servers."""
    e = {"command": uv,
         "args": ["run", "--managed-python", "--python", "3.13", "--no-project", "--quiet",
                  str(launcher.state_dir() / LAUNCHER_NAME), app]}
    if env:
        e["env"] = env
    return e


def is_ours(e: object) -> bool:
    return isinstance(e, dict) and any(LAUNCHER_NAME in str(a) for a in e.get("args", []))


# --------------------------------------------------------------------------- #
# Safe file editing
# --------------------------------------------------------------------------- #
def write_with_backup(path: Path, old: str | None, new: str) -> str | None:
    """Write `new` if it differs. Returns the backup file name, if one was made."""
    if old == new:
        return None
    path.parent.mkdir(parents=True, exist_ok=True)
    backup = None
    if old is not None:
        backup = path.with_name(f"{path.name}.fontes-backup-{time.strftime('%Y%m%d-%H%M%S')}")
        shutil.copy2(path, backup)
    tmp = path.with_name(path.name + ".fontes-tmp")
    tmp.write_text(new, encoding="utf-8")
    os.replace(tmp, path)
    return backup.name if backup else ""


class Node(NamedTuple):
    start: int
    end: int
    value: object
    members: dict | None  # objects: name -> (key start, value Node, end of a following comma or None)


class _JSONC:
    """A small JSON reader that also accepts comments and trailing commas (VS Code, Zed and
    Gemini CLI settings have them) and remembers where every object member is, so one member
    can be replaced or removed while every other byte, comments included, stays as it was."""
    STRING = re.compile(r'"(?:[^"\\\x00-\x1f]|\\.)*"')
    LITERAL = re.compile(r"-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?|true|false|null")

    def __init__(self, text: str):
        self.s, self.i = text, 0

    def parse(self) -> Node:
        node = self.value()
        self.skip()
        if self.i != len(self.s):
            raise ValueError(f"unexpected text at {self.i}")
        return node

    def skip(self) -> None:
        s = self.s
        while self.i < len(s):
            if s[self.i] in " \t\r\n﻿":
                self.i += 1
            elif s.startswith("//", self.i):
                j = s.find("\n", self.i)
                self.i = len(s) if j < 0 else j
            elif s.startswith("/*", self.i):
                j = s.find("*/", self.i + 2)
                if j < 0:
                    raise ValueError("unterminated comment")
                self.i = j + 2
            else:
                return

    def token(self, pattern: re.Pattern) -> object:
        m = pattern.match(self.s, self.i)
        if not m:
            raise ValueError(f"invalid JSON at {self.i}")
        self.i = m.end()
        return json.loads(m.group())

    def value(self) -> Node:
        self.skip()
        start, s = self.i, self.s
        if not (s.startswith("{", start) or s.startswith("[", start)):
            v = self.token(self.STRING if s.startswith('"', start) else self.LITERAL)
            return Node(start, self.i, v, None)
        close, obj = ("}", True) if s[start] == "{" else ("]", False)
        self.i += 1
        members: dict = {}
        items: list = []
        self.skip()
        while not s.startswith(close, self.i):
            if self.i >= len(s):
                raise ValueError("unexpected end of file")
            key_start = self.i
            if obj:
                key = self.token(self.STRING)
                self.skip()
                if not s.startswith(":", self.i):
                    raise ValueError(f"expected ':' at {self.i}")
                self.i += 1
            node = self.value()
            self.skip()
            comma = None
            if s.startswith(",", self.i):
                self.i += 1
                comma = self.i
                self.skip()
            elif not s.startswith(close, self.i):
                raise ValueError(f"expected ',' or '{close}' at {self.i}")
            if obj:
                members.pop(key, None)  # a repeated key: the last one counts, as in JSON.parse
                members[key] = (key_start, node, comma)
            else:
                items.append(node.value)
        self.i += 1
        if obj:
            return Node(start, self.i, {k: m[1].value for k, m in members.items()}, members)
        return Node(start, self.i, items, None)


def _line_indent(text: str, pos: int) -> str:
    line = text[text.rfind("\n", 0, pos) + 1:pos]
    return line[:len(line) - len(line.lstrip(" \t"))]


def _dump(value: object, indent: str) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False).replace("\n", "\n" + indent)


def _insert(text: str, obj: Node, name: str, value: object) -> str:
    """Add a member right after the object's opening brace."""
    member = lambda ind: f"{json.dumps(name, ensure_ascii=False)}: {_dump(value, ind)}"
    if obj.members:
        first = next(iter(obj.members.values()))[0]
        own_line = not text[text.rfind("\n", 0, first) + 1:first].strip()
        ind = _line_indent(text, first) if own_line else _line_indent(text, obj.start) + "  "
        return text[:obj.start + 1] + f"\n{ind}{member(ind)}," + text[obj.start + 1:]
    base = _line_indent(text, obj.start)
    inside = text[obj.start + 1:obj.end - 1]
    if inside.strip():  # only comments inside: keep them after our member
        return text[:obj.start + 1] + f"\n{base}  {member(base + '  ')}" + text[obj.start + 1:]
    return text[:obj.start + 1] + f"\n{base}  {member(base + '  ')}\n{base}" + text[obj.end - 1:]


def _remove(text: str, obj: Node, name: str) -> str:
    """Delete one member (and the comma that went with it), and its line if it had one alone."""
    names = list(obj.members)
    key_start, node, comma = obj.members[name]
    a, b = key_start, comma or node.end
    prev_comma = None
    if comma is None and names.index(name) > 0:  # the last member: drop the comma before it
        prev_comma = obj.members[names[names.index(name) - 1]][2]
    while a > 0 and text[a - 1] in " \t":
        a -= 1
    rest = len(text[b:]) - len(text[b:].lstrip(" \t"))
    if (a == 0 or text[a - 1] == "\n") and text[b + rest:b + rest + 1] in ("\n", "\r"):
        b += rest + (2 if text.startswith("\r\n", b + rest) else 1)
    text = text[:a] + text[b:]
    if prev_comma is not None:
        text = text[:prev_comma - 1] + text[prev_comma:]
    return text


def merge_json(old: str | None, servers: dict[str, dict | None], key: str = "mcpServers") -> str:
    """Set (dict) or remove (None) entries under `key`; every other byte stays as it was."""
    text = old if old and old.strip() else "{}"
    if not isinstance(_JSONC(text).parse().value, dict):
        raise ValueError("top level is not an object")
    expected = _JSONC(text).parse().value
    if not isinstance(expected.get(key, {}), dict):
        raise ValueError(f"{key} is not an object")
    for name, e in servers.items():
        root = _JSONC(text).parse()
        box = root.members[key][1] if key in root.members else None
        if e is None:
            if box is None or not is_ours(box.value.get(name)):
                continue
            del expected[key][name]
            text = _remove(text, box, name)
            root = _JSONC(text).parse()
            box = root.members[key][1]
            if not box.members and not text[box.start + 1:box.end - 1].strip():
                del expected[key]
                text = _remove(text, root, key)
        elif box is None:
            expected[key] = {name: e}
            text = _insert(text, root, key, {name: e})
        elif name in box.members:
            expected[key][name] = e
            node = box.members[name][1]
            if node.value != e:
                ind = _line_indent(text, box.members[name][0])
                text = text[:node.start] + _dump(e, ind) + text[node.end:]
        else:
            expected[key][name] = e
            text = _insert(text, box, name, e)
    # Safety net: the file must read back as exactly the intended settings.
    if _JSONC(text).parse().value != expected:
        raise ValueError("edit would change other settings")
    return text if text.endswith("\n") else text + "\n"


def _toml_table_path(line: str) -> tuple[str, ...] | None:
    """('mcp_servers', 'fontes', 'env') for '[mcp_servers.fontes.env]', else None."""
    s = line.strip()
    if not s.startswith("[") or s.startswith("[["):
        return None
    try:
        d = tomllib.loads(s)
    except tomllib.TOMLDecodeError:
        return None
    path: list[str] = []
    while isinstance(d, dict) and len(d) == 1:
        k = next(iter(d))
        path.append(k)
        d = d[k]
    return tuple(path)


def _toml_value(v) -> str:
    if isinstance(v, list):
        return "[" + ", ".join(_toml_value(x) for x in v) + "]"
    if isinstance(v, (int, float)):
        return str(v)
    return json.dumps(v, ensure_ascii=False)  # JSON string escapes are valid TOML


def merge_toml(old: str | None, servers: dict[str, dict | None]) -> str:
    """Text-level edit of Codex's config.toml: drop our [mcp_servers.<name>] tables and
    append fresh ones. Everything else, comments included, is kept byte for byte."""
    old = old or ""
    before = tomllib.loads(old)  # refuse to touch a file we cannot read
    current = before.get("mcp_servers", {})
    names = {n for n, e in servers.items() if e is not None or is_ours(current.get(n))}
    kept, skipping = [], False
    for line in old.splitlines(keepends=True):
        p = _toml_table_path(line)
        if p is not None:
            skipping = len(p) >= 2 and p[0] == "mcp_servers" and p[1] in names
        if not skipping:
            kept.append(line)
    text = "".join(kept).rstrip("\n")
    for name, e in servers.items():
        if e is None:
            continue
        block = [f"[mcp_servers.{name}]"]  # our names are plain TOML keys
        block += [f"{k} = {_toml_value(v)}" for k, v in e.items() if k != "env"]
        block.append("startup_timeout_sec = 60")
        if e.get("env"):
            block.append(f"\n[mcp_servers.{name}.env]")
            block += [f"{json.dumps(k)} = {_toml_value(v)}" for k, v in e["env"].items()]
        text += ("\n\n" if text else "") + "\n".join(block)
    new = text + "\n" if text else ""
    # Safety net: everything except our own tables must parse back exactly as before.
    after = tomllib.loads(new)
    strip = lambda d: {**d, "mcp_servers": {k: v for k, v in d.get("mcp_servers", {}).items()
                                            if k not in names and k not in servers}}
    if strip(before) != strip(after):
        raise ValueError("edit would change other settings")
    return new


def read_servers(c: Client) -> dict:
    """The servers object in one app's config ({} if the file is missing or unreadable)."""
    try:
        text = c.path.read_text(encoding="utf-8")
        data = tomllib.loads(text) if c.kind == "TOML" else _JSONC(text).parse().value
        servers = data.get(c.key, {})
    except (OSError, ValueError, AttributeError):
        return {}
    return servers if isinstance(servers, dict) else {}


def apply(c: Client, servers: dict[str, dict | None]) -> bool:
    """Write our entries into one app's file. False if the file could not be read."""
    old = c.path.read_text(encoding="utf-8") if c.path.exists() else None
    shaped = {n: None if e is None else {**c.extra, **e} for n, e in servers.items()}
    try:
        new = merge_toml(old, shaped) if c.kind == "TOML" else merge_json(old, shaped, c.key)
        if old is not None:  # same values, perhaps in another order: leave the file alone
            load = tomllib.loads if c.kind == "TOML" else (lambda x: _JSONC(x).parse().value)
            was, now = load(old).get(c.key, {}), load(new).get(c.key, {})
            if all(was.get(n) == now.get(n) for n in shaped):
                new = old
    except ValueError:  # tomllib.TOMLDecodeError is a ValueError too
        print(t("bad_file", path=c.path, kind=c.kind))
        return False
    removing = all(e is None for e in servers.values())
    backup = write_with_backup(c.path, old, new)
    if os.environ.get("FONTES_BRIEF"):  # the Mac app's closing dialog shows outcomes, not paths
        return True
    if backup is None:
        print(t("not_there" if removing else "unchanged", client=c.name, path=c.path))
        return True
    print(t("removed" if removing else "configured", client=c.name, path=c.path))
    if backup:
        print(t("backup", name=backup))
    return True


def configure(servers: dict[str, dict], only_ours: bool = False) -> list[str]:
    """Set our entries in every installed app (only_ours: only where Fontes already is).
    Returns the names of the apps that now have them."""
    done: list[str] = []
    for c in clients():
        if only_ours:
            if not any(is_ours(read_servers(c).get(n)) for n in servers):
                continue
        elif c.detect and not any(d.exists() for d in c.detect):
            if not os.environ.get("FONTES_BRIEF"):
                print(t("not_found", client=c.name))
            continue
        if apply(c, servers) and c.name not in done:
            done.append(c.name)
    return done


def existing_env(name: str) -> dict[str, str]:
    """Keep env values (e.g. FONTES_STATS, API keys) the user already set for our entry."""
    env: dict[str, str] = {}
    for c in clients():
        e = read_servers(c).get(name)
        if isinstance(e, dict) and isinstance(e.get("env"), dict):
            env.update({k: str(v) for k, v in e["env"].items()})
    return env


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #
def ask_stats(ask=input) -> bool:
    """The opt-in question for usage counts. Anything but an explicit yes is no."""
    try:
        answer = ask(t("stats_privacy", privacy=i18n.privacy_url()) + "\n" + t("stats"))
    except EOFError:
        return False
    return i18n.yes(answer)


def prefetch(uv: str, app: str) -> bool:
    """Download the newest version now (so the first start is fast) and record it as good."""
    if not gui():  # the Mac app shows its own "working" notice; its closing dialog stays short
        print(t("fetch", app=app))
    env = {**os.environ, "UV": uv}
    if app == "fontes" and env.get("FONTES_FROM"):  # development source, not PyPI
        cmd = [uv, "tool", "run", "--quiet", "--managed-python", "--python", "3.13",
               "--from", env["FONTES_FROM"], "python", "-c", launcher.verify_code(launcher.APPS[app])]
        ok = subprocess.run(cmd, env=env, stdin=subprocess.DEVNULL).returncode == 0
    else:
        cmd = [uv, "run", "--managed-python", "--python", "3.13", "--no-project", "--quiet",
               str(launcher.state_dir() / LAUNCHER_NAME), "--update", app]
        out = subprocess.run(cmd, env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL)
        ok = out.stdout.strip() in ("updated", "current")
    if not (ok and gui()):
        print(t("fetch_ok" if ok else "fetch_fail", app=app))
    return ok


# Optional free API keys, saved in the env of our entry. Never printed.
KEYS = {"WLM_FR_PISTE_CLIENT_ID": "key_fr_id", "WLM_FR_PISTE_CLIENT_SECRET": "key_fr_secret",
        "WLM_US_GOVINFO_KEY": "key_us"}
KEYS_URL = f"{i18n.REPO}docs/KEYS.md"
INSTALL_URL = f"{i18n.REPO}docs/INSTALL.md"


def gui() -> bool:
    """Run from the Mac app (no terminal): ask with dialogs instead."""
    return sys.platform == "darwin" and os.environ.get("FONTES_GUI") == "1"


def _dialog(script: str, *args: str) -> str | None:
    """One AppleScript dialog; its answer, or None if the person cancelled it."""
    r = subprocess.run(["osascript", "-e", "on run argv", "-e", script, "-e", "end run", *args],
                       capture_output=True, text=True, stdin=subprocess.DEVNULL)
    return r.stdout.rstrip("\n") if r.returncode == 0 else None


def want_keys(ask=input) -> bool:
    """Offer the keys step (optional, default no)."""
    intro = t("keys_intro", url=KEYS_URL)
    if gui():
        while True:
            b = _dialog('button returned of (display dialog (item 1 of argv) with title "Fontes" '
                        'buttons {item 2 of argv, item 3 of argv, item 4 of argv} '
                        'default button (item 4 of argv) cancel button (item 2 of argv))',
                        intro, t("app_button_cancel"), t("app_button_guide"), t("app_button_continue"))
            if b != t("app_button_guide"):
                return b == t("app_button_continue")
            subprocess.run(["open", KEYS_URL])
    try:
        return i18n.yes(ask(intro + "\n" + t("keys_ask")))
    except EOFError:
        return False


def ask_secret(prompt: str) -> str | None:
    """Hidden input; None if cancelled."""
    if gui():
        return _dialog('text returned of (display dialog (item 1 of argv) with title "Fontes" '
                       'default answer "" with hidden answer buttons {item 2 of argv, item 3 of argv} '
                       'default button (item 3 of argv) cancel button (item 2 of argv))',
                       prompt.strip(), t("app_button_cancel"), t("app_button_ok"))
    try:
        return getpass.getpass(prompt)
    except (EOFError, KeyboardInterrupt):
        return None


def ask_keys(env: dict[str, str], ask=ask_secret) -> bool:
    """Ask for each key: Enter keeps (or skips) it, '-' removes it. Updates env in place.
    True if anything changed; a cancel leaves env as it was."""
    new = dict(env)
    for var, label in KEYS.items():
        key = ("app_key_set" if new.get(var) else "app_key_unset") if gui() else \
            ("keys_set" if new.get(var) else "keys_unset")
        answer = ask(t(key, name=t(label)))
        if answer is None:
            return False
        answer = answer.strip()
        if answer == "-":
            new.pop(var, None)
        elif answer:
            new[var] = answer
    changed = new != env
    env.clear()
    env.update(new)
    return changed


def install() -> int:
    if not gui():
        print(t("start"))
    uv = find_uv()
    if not uv:
        print(t("no_uv"))
        return 1
    home = launcher.state_dir()
    home.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__).resolve().parent / LAUNCHER_NAME, home / LAUNCHER_NAME)

    fontes_env = {k: v for k, v in existing_env("fontes").items() if k != "FONTES_FROM"}
    if sys.stdin.isatty():  # usage counts: opt-in, default no; without a terminal, keep as is
        fontes_env.pop("FONTES_STATS", None)
        if ask_stats():
            fontes_env["FONTES_STATS"] = "1"
    if os.environ.get("FONTES_FROM"):
        fontes_env["FONTES_FROM"] = os.environ["FONTES_FROM"]

    for app in launcher.APPS:
        prefetch(uv, app)
    claude_seen = claude_desktop_present()
    done = configure({"fontes": entry(uv, "fontes", fontes_env)})
    done = [c for c in done if c != "Claude Desktop" or claude_seen]
    if done:
        print(t("apps_list", clients=", ".join(done)))
    # Keys are optional, so they are offered only once Fontes is set up. The Mac app offers
    # them in its closing dialog instead.
    if not gui() and sys.stdin.isatty() and want_keys() and ask_keys(fontes_env):
        configure({"fontes": entry(uv, "fontes", fontes_env)}, only_ours=True)
        print(t("keys_saved"))
    print(t("done") if done else t("no_apps", url=INSTALL_URL))
    return 0


def keys() -> int:
    """Add, change or remove the API keys in every app that already has Fontes."""
    uv = find_uv()
    if not uv:
        print(t("no_uv"))
        return 1
    env = existing_env("fontes")
    if not any(is_ours(read_servers(c).get("fontes")) for c in clients()):
        print(t("keys_no_apps"))
        return 1
    if gui():
        if not want_keys():
            return 0
    elif sys.stdin.isatty():
        print(t("keys_intro", url=KEYS_URL))
    else:
        print(t("keys_unchanged"))
        return 1
    if not ask_keys(env):
        print(t("keys_unchanged"))
        return 0
    configure({"fontes": entry(uv, "fontes", env)}, only_ours=True)
    print(t("keys_saved"))
    return 0


def uninstall() -> int:
    servers = {name: None for name in launcher.APPS}
    for c in clients():
        if c.path.exists():
            apply(c, servers)
    shutil.rmtree(launcher.state_dir(), ignore_errors=True)
    print(t("done_uninstall"))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="fontes_setup")
    p.add_argument("action", choices=["install", "keys", "uninstall"])
    a = p.parse_args(argv)
    return {"install": install, "keys": keys, "uninstall": uninstall}[a.action]()


if __name__ == "__main__":
    sys.exit(main())
