"""installer/: the auto-updating launcher and the config merging, without network or real configs."""
import json
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "installer"))
import fontes_launcher as L
import fontes_setup as S


@pytest.fixture(autouse=True)
def state(tmp_path, monkeypatch):
    monkeypatch.setenv("FONTES_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("UV", "/x/uv")
    monkeypatch.delenv("FONTES_FROM", raising=False)


def ok_run(code=0):
    calls = []
    def run(cmd, **kw):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, code)
    return run, calls


# ---- launcher ------------------------------------------------------------- #
def test_update_installs_checks_and_pins_new_version():
    run, calls = ok_run()
    assert L.update("fontes", fetch=lambda p: "0.2.0", run=run) == "updated"
    assert calls[0][:3] == ["/x/uv", "tool", "run"] and "fontes-mcp==0.2.0" in calls[0]
    assert L.load_state("fontes")["good"] == "0.2.0"
    assert L.run_command("fontes", ["--only", "nl"], L.load_state("fontes"))[-4:] == \
        ["fontes-mcp==0.2.0", "fontes", "--only", "nl"]


def test_failed_update_keeps_last_good_version():
    L.save_state("fontes", {"good": "0.1.0"})
    run, _ = ok_run(code=1)
    assert L.update("fontes", fetch=lambda p: "0.2.0", run=run) == "failed"
    st = L.load_state("fontes")
    assert st["good"] == "0.1.0" and st["failed"] == "0.2.0"


def test_offline_and_current_do_nothing():
    L.save_state("fontes", {"good": "0.2.0"})
    run, calls = ok_run()
    assert L.update("fontes", fetch=lambda p: None, run=run) == "offline"
    assert L.update("fontes", fetch=lambda p: "0.2.0", run=run) == "current"
    assert calls == [] and L.load_state("fontes")["good"] == "0.2.0"
    assert not L.due(L.load_state("fontes"))   # checked: no new check for a day


def test_versions_compare_numerically():
    assert L.parse_version("1.10.0") > L.parse_version("1.9.9")


def test_dev_source_overrides_pypi(monkeypatch):
    monkeypatch.setenv("FONTES_FROM", "/src/fontes")
    assert "/src/fontes" in L.run_command("fontes", [], {"good": "0.1.0"})


# ---- config merging ------------------------------------------------------- #
ENTRY = {"command": "/x/uv", "args": ["run", "/s/fontes_launcher.py", "fontes"]}
SERVERS = {"fontes": ENTRY}
REMOVE = {"fontes": None}


def test_json_merge_keeps_other_entries_and_is_idempotent():
    old = json.dumps({"mcpServers": {"other": {"command": "x"}}, "theme": "dark"})
    new = S.merge_json(old, SERVERS)
    data = json.loads(new)
    assert data["theme"] == "dark" and data["mcpServers"]["other"] == {"command": "x"}
    assert data["mcpServers"]["fontes"] == ENTRY
    assert S.merge_json(new, SERVERS) == new
    assert json.loads(S.merge_json(new, REMOVE)) == json.loads(old)


def test_json_uninstall_leaves_entries_it_did_not_write():
    old = json.dumps({"mcpServers": {"fontes": {"command": "uvx", "args": ["fontes-mcp"]}}})
    assert json.loads(S.merge_json(old, REMOVE)) == json.loads(old)


def test_json_uninstall_of_our_only_entry_leaves_valid_json():
    assert json.loads(S.merge_json(S.merge_json(None, SERVERS), REMOVE)) == {}


def test_json_refuses_broken_file():
    with pytest.raises(ValueError):
        S.merge_json("{not json", SERVERS)


CODEX = '''# my settings
model = "o4"

[mcp_servers.other]   # keep me
command = "x"

[mcp_servers.fontes]
command = "old"

[mcp_servers.fontes.env]
A = "1"

[profiles.work]
model = "o3"
'''


def test_toml_merge_replaces_only_our_tables_and_keeps_comments():
    new = S.merge_toml(CODEX, SERVERS)
    d = tomllib.loads(new)
    assert "# my settings" in new and "# keep me" in new
    assert d["model"] == "o4" and d["profiles"]["work"]["model"] == "o3"
    assert d["mcp_servers"]["other"] == {"command": "x"}
    assert d["mcp_servers"]["fontes"]["args"] == ENTRY["args"]
    assert "env" not in d["mcp_servers"]["fontes"]
    assert d["mcp_servers"]["fontes"]["startup_timeout_sec"] == 60
    assert S.merge_toml(new, SERVERS) == new
    back = tomllib.loads(S.merge_toml(new, REMOVE))
    assert set(back["mcp_servers"]) == {"other"} and back["profiles"] == d["profiles"]


def test_toml_windows_paths_round_trip():
    e = {"command": r"C:\Users\Ayşe\.local\bin\uv.exe", "args": [r"C:\x\fontes_launcher.py"]}
    assert tomllib.loads(S.merge_toml("", {"fontes": e}))["mcp_servers"]["fontes"]["command"] == e["command"]


def test_toml_refuses_broken_file():
    with pytest.raises(tomllib.TOMLDecodeError):
        S.merge_toml("[broken", SERVERS)


def test_backup_written_only_on_change(tmp_path):
    f = tmp_path / "c.json"
    f.write_text("{}")
    assert S.write_with_backup(f, "{}", "{}") is None
    name = S.write_with_backup(f, "{}", '{"a": 1}')
    assert (tmp_path / name).read_text() == "{}" and f.read_text() == '{"a": 1}'


def test_toml_env_table_written():
    e = {**ENTRY, "env": {"FONTES_STATS": "1"}}
    d = tomllib.loads(S.merge_toml("", {"fontes": e}))
    assert d["mcp_servers"]["fontes"]["env"] == {"FONTES_STATS": "1"}


# ---- install / uninstall: Fontes only -------------------------------------- #
LEGACY_WORD = {"command": "/x/uv", "args": ["run", "/old/fontes_launcher.py", "word-mcp-live"],
               "env": {"MCP_AUTHOR": "A. Lawyer"}}


def test_install_adds_only_fontes_and_leaves_an_old_word_entry_alone(tmp_path, monkeypatch):
    monkeypatch.setattr(S.sys, "platform", "darwin")
    monkeypatch.setattr(S.Path, "home", classmethod(lambda cls: tmp_path))
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / ".codex"))
    monkeypatch.setattr(S, "find_uv", lambda: "/x/uv")
    monkeypatch.setattr(S, "prefetch", lambda uv, app: True)
    monkeypatch.setattr(S.sys.stdin, "isatty", lambda: False, raising=False)
    assert "word-mcp-live" not in L.APPS
    claude = S.claude_configs()[0]
    claude.parent.mkdir(parents=True)
    claude.write_text(json.dumps({"mcpServers": {"word-mcp-live": LEGACY_WORD}}))
    (tmp_path / ".codex").mkdir()
    codex = S.codex_config()

    assert S.main(["install"]) == 0
    servers = json.loads(claude.read_text())["mcpServers"]
    assert set(servers) == {"fontes", "word-mcp-live"} and servers["word-mcp-live"] == LEGACY_WORD
    assert set(tomllib.loads(codex.read_text())["mcp_servers"]) == {"fontes"}
    assert "word" not in codex.read_text().lower()

    assert S.main(["uninstall"]) == 0
    assert json.loads(claude.read_text())["mcpServers"] == {"word-mcp-live": LEGACY_WORD}


def test_setup_has_no_author_option():
    with pytest.raises(SystemExit):
        S.main(["install", "--author", "A. Lawyer"])


# ---- every app: install, rerun, keys, uninstall --------------------------- #
APP_NAMES = ["Claude Desktop", "Codex", "Claude Code", "Cursor", "VS Code", "Windsurf",
             "Gemini CLI", "Zed", "LM Studio", "Cline"]
OTHER = {"command": "npx", "args": ["other-server"]}


@pytest.fixture
def home(tmp_path, monkeypatch):
    """A throwaway Mac home with every app's config folder present."""
    monkeypatch.setattr(S.sys, "platform", "darwin")
    monkeypatch.setattr(S.Path, "home", classmethod(lambda cls: tmp_path))
    for v in ("XDG_CONFIG_HOME", "CLAUDE_CONFIG_DIR", "COPILOT_HOME"):
        monkeypatch.delenv(v, raising=False)
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / ".codex"))
    monkeypatch.setattr(S, "find_uv", lambda: "/x/uv")
    monkeypatch.setattr(S, "prefetch", lambda uv, app: True)
    monkeypatch.setattr(S.sys.stdin, "isatty", lambda: False, raising=False)
    for c in S.clients():
        for d in c.detect:
            if d.suffix == ".json":   # Claude Code is detected by its file
                d.parent.mkdir(parents=True, exist_ok=True)
                d.write_text('{"numStartups": 3}')
            else:
                d.mkdir(parents=True, exist_ok=True)
    return tmp_path


def by_name(name):
    return next(c for c in S.clients() if c.name == name)


def test_clients_cover_every_app(home):
    assert [c.name for c in S.clients()] == APP_NAMES
    assert by_name("Claude Code").path == home / ".claude.json"
    assert by_name("Cursor").path == home / ".cursor/mcp.json"
    assert by_name("VS Code").path == home / ".copilot/mcp-config.json"
    assert by_name("Windsurf").path == home / ".codeium/windsurf/mcp_config.json"
    assert by_name("Gemini CLI").path == home / ".gemini/settings.json"
    assert by_name("Zed").path == home / ".config/zed/settings.json"
    assert by_name("LM Studio").path == home / ".lmstudio/mcp.json"
    assert by_name("Cline").path == home / ".cline/data/settings/cline_mcp_settings.json"


def test_windsurf_prefers_the_current_devin_file(home):
    (home / ".config/devin").mkdir(parents=True)
    assert by_name("Windsurf").path == home / ".config/devin/mcp_config.json"


def test_windows_paths_follow_appdata_and_home(tmp_path, monkeypatch):
    monkeypatch.setattr(S.sys, "platform", "win32")
    monkeypatch.setattr(S.Path, "home", classmethod(lambda cls: tmp_path))
    monkeypatch.setenv("APPDATA", str(tmp_path / "Roaming"))
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "Local"))
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / ".codex"))
    for v in ("CLAUDE_CONFIG_DIR", "COPILOT_HOME"):
        monkeypatch.delenv(v, raising=False)
    (tmp_path / "Roaming/devin").mkdir(parents=True)
    paths = {c.name: c.path for c in S.clients()}
    assert paths["Claude Desktop"] == tmp_path / "Roaming/Claude/claude_desktop_config.json"
    assert paths["Zed"] == tmp_path / "Roaming/Zed/settings.json"
    assert paths["Windsurf"] == tmp_path / "Roaming/devin/mcp_config.json"
    assert paths["Cursor"] == tmp_path / ".cursor/mcp.json"
    assert paths["Claude Code"] == tmp_path / ".claude.json"


@pytest.mark.parametrize("name", APP_NAMES)
def test_each_app_install_rerun_keys_uninstall(home, name, monkeypatch):
    c = by_name(name)
    c.path.parent.mkdir(parents=True, exist_ok=True)
    if c.kind == "TOML":
        c.path.write_text('# mine\n[mcp_servers.other]\ncommand = "npx"\nargs = ["other-server"]\n')
    else:
        old = json.loads(c.path.read_text()) if c.path.exists() else {}
        c.path.write_text("// my settings\n" + json.dumps({**old, "theme": "dark", c.key: {"other": OTHER}}, indent=2))

    assert S.main(["install"]) == 0
    ours = S.read_servers(c)["fontes"]
    assert S.is_ours(ours) and ours["command"] == "/x/uv" and "env" not in ours
    assert S.read_servers(c)["other"] == OTHER
    for k, v in c.extra.items():
        assert ours[k] == v
    first = c.path.read_text()
    assert ("# mine" if c.kind == "TOML" else "// my settings") in first
    backups = sorted(c.path.parent.glob(c.path.name + ".fontes-backup-*"))
    assert backups, "a backup is made before the first change"

    assert S.main(["install"]) == 0          # rerun: nothing changes, no new backup
    assert c.path.read_text() == first
    assert sorted(c.path.parent.glob(c.path.name + ".fontes-backup-*")) == backups

    # keys: typed once, written to the env of our entry, never printed
    answers = iter(["fr-id", "fr-secret", "us-key"])
    monkeypatch.setattr(S.sys.stdin, "isatty", lambda: True, raising=False)
    monkeypatch.setattr(S, "ask_secret", lambda prompt: next(answers))
    monkeypatch.setattr(S.getpass, "getpass", lambda prompt: next(answers))
    assert S.main(["keys"]) == 0
    assert S.read_servers(c)["fontes"]["env"] == {"WLM_FR_PISTE_CLIENT_ID": "fr-id",
        "WLM_FR_PISTE_CLIENT_SECRET": "fr-secret", "WLM_US_GOVINFO_KEY": "us-key"}
    assert S.read_servers(c)["other"] == OTHER

    assert S.main(["uninstall"]) == 0
    assert "fontes" not in S.read_servers(c) and S.read_servers(c)["other"] == OTHER
    assert ("# mine" if c.kind == "TOML" else "// my settings") in c.path.read_text()
    if c.kind == "JSON":
        assert S._JSONC(c.path.read_text()).parse().value["theme"] == "dark"


def test_same_values_in_another_order_are_left_alone(home):
    c = by_name("Codex")
    assert S.apply(c, {"fontes": {"command": "u", "args": [], "env": {"A": "1", "B": "2"}}})
    text = c.path.read_text()
    assert S.apply(c, {"fontes": {"command": "u", "args": [], "env": {"B": "2", "A": "1"}}})
    assert c.path.read_text() == text


def test_install_skips_apps_that_are_not_installed(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(S.sys, "platform", "darwin")
    monkeypatch.setattr(S.Path, "home", classmethod(lambda cls: tmp_path))
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / ".codex"))
    monkeypatch.setattr(S, "find_uv", lambda: "/x/uv")
    monkeypatch.setattr(S, "prefetch", lambda uv, app: True)
    monkeypatch.setattr(S.sys.stdin, "isatty", lambda: False, raising=False)
    (tmp_path / ".cursor").mkdir()
    assert S.main(["install"]) == 0
    written = {c.name for c in S.clients() if c.path.exists()}
    assert written == {"Claude Desktop", "Cursor"}
    assert not (tmp_path / ".claude.json").exists()   # never create Claude Code's own file


def test_install_asks_keys_once_and_keeps_them_on_rerun(home, monkeypatch, capsys):
    monkeypatch.setattr(S.sys.stdin, "isatty", lambda: True, raising=False)
    monkeypatch.setattr(S, "ask_stats", lambda: False)
    monkeypatch.setattr(S, "want_keys", lambda: True)
    answers = iter(["", "", "  secret-us-key  "])
    monkeypatch.setattr(S.getpass, "getpass", lambda prompt: next(answers))
    assert S.main(["install"]) == 0
    assert "secret-us-key" not in capsys.readouterr().out
    for c in S.clients():
        assert S.read_servers(c)["fontes"]["env"] == {"WLM_US_GOVINFO_KEY": "secret-us-key"}
    monkeypatch.setattr(S, "want_keys", lambda: False)   # skipped: keys stay
    assert S.main(["install"]) == 0
    assert S.read_servers(by_name("Zed"))["fontes"]["env"] == {"WLM_US_GOVINFO_KEY": "secret-us-key"}


def test_install_offers_keys_only_after_apps_are_set_up(home, monkeypatch, capsys):
    monkeypatch.setattr(S.sys.stdin, "isatty", lambda: True, raising=False)
    monkeypatch.setattr(S, "ask_stats", lambda: False)
    seen = []
    def want():
        seen.append(all(S.is_ours(S.read_servers(c).get("fontes")) for c in S.clients()))
        return False
    monkeypatch.setattr(S, "want_keys", want)
    assert S.main(["install"]) == 0
    assert seen == [True]   # asked once, with every app already set up


def test_mac_app_install_never_asks_for_keys(home, monkeypatch, capsys):
    monkeypatch.setattr(S.sys, "platform", "darwin")
    monkeypatch.setenv("FONTES_GUI", "1")
    monkeypatch.setattr(S, "want_keys", lambda: pytest.fail("keys asked during install"))
    monkeypatch.setattr(S, "_dialog", lambda *a: pytest.fail("dialog during install"))
    assert S.main(["install"]) == 0
    out = capsys.readouterr().out
    assert S.t("done") in out and S.t("start") not in out


def test_mac_app_key_prompts_use_dialog_wording(monkeypatch):
    monkeypatch.setattr(S.sys, "platform", "darwin")
    monkeypatch.setenv("FONTES_GUI", "1")
    prompts = []
    S.ask_keys({"WLM_US_GOVINFO_KEY": "x"}, ask=lambda p: prompts.append(p) or "")
    assert all("Enter" not in p for p in prompts)
    assert prompts[-1] == S.t("app_key_set", name=S.t("key_us"))


def test_ask_keys_keep_change_remove_cancel(monkeypatch):
    env = {"WLM_US_GOVINFO_KEY": "old", "FONTES_STATS": "1"}
    prompts = []
    answers = iter(["new-id", "", "-"])
    assert S.ask_keys(env, ask=lambda p: prompts.append(p) or next(answers)) is True
    assert env == {"WLM_FR_PISTE_CLIENT_ID": "new-id", "FONTES_STATS": "1"}
    assert "old" not in "".join(prompts)
    assert S.ask_keys(env, ask=lambda p: "") is False and env["WLM_FR_PISTE_CLIENT_ID"] == "new-id"
    assert S.ask_keys(env, ask=lambda p: None) is False
    assert env == {"WLM_FR_PISTE_CLIENT_ID": "new-id", "FONTES_STATS": "1"}


def test_keys_without_fontes_installed_says_so(home, capsys):
    assert S.main(["keys"]) == 1
    assert S.t("keys_no_apps") in capsys.readouterr().out


def test_keys_step_links_the_guide(monkeypatch):
    seen = []
    S.want_keys(ask=lambda p: seen.append(p) or "")
    assert "github.com/ykarapazar/fontes/blob/main/docs/KEYS.md" in seen[0]
    assert "WLM_PERMITTED" not in json.dumps(S.i18n._load("en"))


# ---- JSON with comments ---------------------------------------------------- #
ZED = """// Zed settings
//
// For information on how to configure Zed, see the Zed documentation.
{
  "theme": "One Dark", // my theme
  /* block comment */
  "context_servers": {
    "other": {"command": "npx", "args": ["x"]}, // keep
  },
  "vim_mode": true,
}
"""


def test_jsonc_edit_keeps_comments_and_trailing_commas():
    new = S.merge_json(ZED, SERVERS, "context_servers")
    for keep in ("// Zed settings", "// my theme", "/* block comment */", "// keep", '"vim_mode": true,'):
        assert keep in new
    assert S._JSONC(new).parse().value["context_servers"]["fontes"] == ENTRY
    assert S.merge_json(new, SERVERS, "context_servers") == new
    assert S.merge_json(new, REMOVE, "context_servers") == ZED


def test_jsonc_remove_last_member_and_empty_box():
    one = S.merge_json('{\n  "a": 1\n}\n', SERVERS)
    assert S.merge_json(one, REMOVE) == '{\n  "a": 1\n}\n'
    assert S._JSONC(S.merge_json(S.merge_json("{}", SERVERS), REMOVE)).parse().value == {}


def test_jsonc_strings_with_comment_markers_are_not_comments():
    old = '{"url": "http://x//y", "s": "/* no */", "mcpServers": {}}'
    new = S.merge_json(old, SERVERS)
    v = S._JSONC(new).parse().value
    assert v["url"] == "http://x//y" and v["s"] == "/* no */"


@pytest.mark.parametrize("bad", ["{not json", "[1, 2]", '{"mcpServers": []}', '{"a": 1} x', "/* open"])
def test_jsonc_refuses_what_it_cannot_read(bad):
    with pytest.raises(ValueError):
        S.merge_json(bad, SERVERS)


def test_mcpb_keys_are_optional_sensitive_and_mapped_to_env():
    root = Path(__file__).resolve().parents[1] / "installer" / "mcpb"
    m = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    env = m["server"]["mcp_config"]["env"]
    assert set(env) == set(S.KEYS)
    for var, ref in env.items():
        name = ref.removeprefix("${user_config.").removesuffix("}")
        item = m["user_config"][name]
        assert item["type"] == "string" and item["sensitive"] is True
        assert item["required"] is False and item["default"] == ""   # unset -> "" not the literal


# ---- usage-count question and Turkish text -------------------------------- #
@pytest.mark.parametrize("lang,answer,expected", [
    ("en", "", False), ("en", "n", False), ("en", "maybe", False), ("en", "y", True),
    ("en", "YES", True), ("tr", "", False), ("tr", "h", False), ("tr", "evet", True), ("tr", "e", True),
])
def test_stats_question_defaults_to_no(monkeypatch, lang, answer, expected):
    monkeypatch.setenv("FONTES_LANG", lang)
    assert S.ask_stats(ask=lambda prompt: answer) is expected


def test_stats_question_without_input_is_no():
    def eof(prompt):
        raise EOFError
    assert S.ask_stats(ask=eof) is False


def test_turkish_messages_complete_and_formattable(monkeypatch):
    en, tr = S.i18n._load("en"), S.i18n._load("tr")
    assert set(tr) == set(en)
    monkeypatch.setenv("FONTES_LANG", "tr")
    kw = dict(default="A", app="fontes", client="Codex", clients="Codex", path="/p", name="n", kind="JSON", version="1",
              os="mac", call="c", error="e", note="n", why="w", url="u", status=500, privacy="p")
    for key in en:
        assert S.t(key, **kw)
    assert "[e/H]" in S.t("stats")
    monkeypatch.delenv("FONTES_LANG")
    monkeypatch.setattr(S.i18n, "os_languages", lambda: ["tr_TR.UTF-8"])
    assert S.t("fetch_ok", app="x") == "  x hazır."


@pytest.mark.parametrize("prefs,expected", [
    (["pt-BR"], "en"), (["tr-TR"], "tr"), (["tr_TR.UTF-8"], "tr"), (["C", "en_GB"], "en"),
    (["xx", "tr"], "tr"), ([], "en"), ([""], "en"),
])
def test_language_fallback_chain(monkeypatch, prefs, expected):
    monkeypatch.setattr(S.i18n, "available", lambda: ["en", "tr"])  # independent of new locales
    assert S.i18n.language(prefs) == expected


def test_portuguese_fallbacks():
    """pt is Brazilian, pt-PT European; other Portuguese regions fall back to pt-PT, then pt."""
    assert S.i18n.chain("pt-BR") == ["pt-BR", "pt"]
    assert S.i18n.chain("pt_PT.UTF-8") == ["pt-PT", "pt"]
    assert S.i18n.chain("pt-AO") == ["pt-AO", "pt-PT", "pt"]
    assert S.i18n.chain("pt_MZ") == ["pt-MZ", "pt-PT", "pt"]


def test_privacy_link_is_translated_only_when_the_notice_is(monkeypatch, tmp_path):
    monkeypatch.setattr(S.i18n, "_privacy_languages", lambda: {"tr"})
    assert S.i18n.privacy_url("tr").endswith("/docs/i18n/tr/PRIVACY.md")
    assert S.i18n.privacy_url("es").endswith("/docs/PRIVACY.md")
    assert S.i18n.privacy_url("en").endswith("/docs/PRIVACY.md")
    seen = []
    S.ask_stats(ask=lambda prompt: seen.append(prompt) or "")
    assert "PRIVACY.md" in seen[0]


def test_chain_maps_chinese_regions_to_scripts():
    assert S.i18n.chain("zh-TW") == ["zh-TW", "zh-Hant", "zh", "zh-Hans"]
    assert S.i18n.chain("zh_CN") == ["zh-CN", "zh-Hans", "zh"]
    assert S.i18n.chain("sr-Latn-RS") == ["sr-Latn-RS", "sr-Latn", "sr"]
    assert S.i18n.chain("iw") == ["he"] and S.i18n.chain("no-NO") == ["nb-NO", "nb"]


# ---- Claude Desktop extension (.mcpb) ------------------------------------- #
def test_mcpb_manifest_has_mcp_config_and_managed_python_only():
    """MCPB 0.4 requires server.mcp_config for every server type (uv included); the bundle's uv
    must never probe a system Python (macOS developer-tools dialog)."""
    root = Path(__file__).resolve().parents[1] / "installer" / "mcpb"
    server = json.loads((root / "manifest.json").read_text(encoding="utf-8"))["server"]
    cfg = server["mcp_config"]
    assert server["type"] == "uv" and cfg["command"] == "uv"
    assert cfg["args"] == ["run", "--directory", "${__dirname}", server["entry_point"]]
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    assert project["tool"]["uv"]["python-preference"] == "only-managed"


def test_cached_good_version_starts_offline(monkeypatch):
    """A pinned version already in uv's cache must start with no network (uv --offline);
    if the cache lost it, start normally so uv can fetch it again."""
    L.save_state("fontes", {"good": "0.1.0", "checked": 9e99})
    for code, expected in ((0, True), (1, False)):
        run, probes = ok_run(code)
        assert L.cached("fontes", L.load_state("fontes"), run=run) is expected
        assert "--offline" in probes[0] and "fontes-mcp==0.1.0" in probes[0]
    execs = []
    monkeypatch.setattr(L.os, "execvp", lambda f, cmd: execs.append(cmd))
    monkeypatch.setattr(L.sys, "platform", "darwin")
    for in_cache in (True, False):
        monkeypatch.setattr(L, "cached", lambda app, state: in_cache)
        L.main(["fontes"])
    assert execs[0][:4] == ["/x/uv", "tool", "run", "--offline"] and "fontes-mcp==0.1.0" in execs[0]
    assert "--offline" not in execs[1]


def test_install_says_so_when_no_ai_app_is_found(tmp_path, monkeypatch, capsys):
    """A PC with no AI app: settings are prepared for Claude Desktop, but the user is told."""
    monkeypatch.setattr(S.sys, "platform", "darwin")
    monkeypatch.setattr(S.Path, "home", classmethod(lambda cls: tmp_path))
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / ".codex"))
    monkeypatch.setattr(S, "find_uv", lambda: "/x/uv")
    monkeypatch.setattr(S, "prefetch", lambda uv, app: True)
    monkeypatch.setattr(S.sys.stdin, "isatty", lambda: False, raising=False)
    monkeypatch.setattr(S, "claude_desktop_present", lambda: False)
    assert S.main(["install"]) == 0
    out = capsys.readouterr().out
    assert "No AI app was found" in out and "set up in" not in out
    assert by_name("Claude Desktop").path.exists()   # ready for when Claude Desktop is installed
