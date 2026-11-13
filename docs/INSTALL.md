# Installing Fontes

Fontes lets your AI app look up court decisions and legislation live on court and government
websites in over 120 jurisdictions. Every result links to the original. It is a standard MCP
server, so it works in any app that can run a local MCP server: Claude Desktop, Codex, Claude
Code, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio, Cline and others.

**Fontes is not on PyPI yet.** The steps below work once the first release is out.

Pick your app, follow its steps, then [check that it works](#checking-it-works).

## Claude Desktop

1. Download the Fontes `.mcpb` file from the
   [latest release](https://github.com/ykarapazar/fontes/releases/latest).
2. Double-click it. Claude Desktop opens it.
3. Click **Install**.

## Codex

In a terminal:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

The Codex CLI and the Codex IDE extension share this setting (`~/.codex/config.toml`).
You need [uv](#you-need-uv).

## Claude Code

In a terminal:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

You need [uv](#you-need-uv).

## Other apps

Each of these needs [uv](#you-need-uv). Add the entry, save, then quit and reopen the app.

**Cursor:** in `~/.cursor/mcp.json` (all projects) or `.cursor/mcp.json` (one project):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** run **MCP: Add Server** from the Command Palette, choose
**Command (stdio)**, enter `uvx fontes-mcp` and name the server `fontes`. Or add this to
`~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Older VS Code setups use `.vscode/mcp.json`, where the top-level key is `servers` instead of
`mcpServers`.

**Gemini CLI:** in a terminal, `gemini mcp add -s user fontes uvx fontes-mcp`. Or add this to
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** open your settings file (**zed: open settings file**) and add:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** in the right-hand sidebar, open the **Program** tab, click **Install → Edit
mcp.json**, and add:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** click the **MCP Servers** icon, open the **Configure** tab, click **Configure MCP
Servers**, and add the same `mcpServers` entry as for LM Studio.

**Claude Desktop, by hand** (instead of the `.mcpb` file): add the same `mcpServers` entry to
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Any other MCP app** (Windsurf and others): its own documentation says where it keeps its MCP
servers. Most take the same entry: command `uvx`, argument `fontes`.

If the app cannot find `uvx`, use its full path (on macOS and Linux, `which uvx` prints it).

## You need uv

Codex, Claude Code and the other apps start Fontes with `uvx`, which comes with **uv**, a small
free tool from Astral. To install it, see
[Astral's guide](https://docs.astral.sh/uv/getting-started/installation/), or run:

- macOS or Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Keys

Some sources need a free key: see [KEYS.md](KEYS.md).

## Checking it works

In a new chat, ask: *"Which jurisdictions can Fontes search?"* The app should answer with a
list of countries. If it doesn't, quit and reopen the app once more.

## One-click installer (on its way)

A Mac and Windows installer that sets up Fontes in all your apps at once is on its way. It sets
up Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI,
Zed, LM Studio and Cline. Once it is released:

**Before you start:** quit each of these apps completely. This matters most for Claude Code:
while it runs, it rewrites `~/.claude.json` and can undo the installer's change. If you cannot
quit Claude Code, add Fontes to it with `claude mcp add` instead (see [Claude Code](#claude-code)).

**Mac**

1. Open the downloaded **Fontes Installer** folder.
2. Double-click **Install Fontes.command**.
   - If your Mac says it "cannot be opened because it is from an unidentified developer":
     right-click (or Control-click) the file, choose **Open**, then **Open** again. You only
     do this once.
3. A window opens and asks whether to send anonymous usage counts; press Enter for no.
4. It asks whether to add keys now. Press Enter to skip; see [The keys step](#the-keys-step).
5. When it says **Done**, open your AI apps again.

**Windows**

1. Unzip the downloaded **Fontes Installer** (right-click → Extract All).
2. Double-click **Install Fontes.cmd**.
   - If Windows shows "Windows protected your PC": click **More info**, then **Run anyway**.
3. When asked whether to send anonymous usage counts, press Enter for no.
4. It asks whether to add keys now. Press Enter to skip; see [The keys step](#the-keys-step).
5. When it says **Done**, open your AI apps again. If one was still running, close it
   completely (also from the system tray, near the clock) and open it again.

At the end the installer lists the apps it set up.

### Which apps it sets up

It sets up an app only if that app's settings folder is already on your computer. Claude Code
is set up only if `~/.claude.json` exists. Claude Desktop is always set up. Each app gets one
entry, `fontes`, in this file:

| App | File (Mac and Linux) | File (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, and the Microsoft Store version's own copy |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, or `~/.codeium/windsurf/mcp_config.json` on older versions | `%APPDATA%\devin\mcp_config.json`, or `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code is set up if `~/.copilot` or VS Code's own settings folder exists.

Two apps need one more step:

- **Windsurf:** after reopening it, press refresh in Cascade.
- **Cline inside the older VS Code extension:** add Fontes by hand (see [Cline](#other-apps)).

### The keys step

Right after installing, the installer offers to add the free France and US keys. To add or
change them later:

- **Mac:** double-click **Add or change keys.command** in the installer folder, or open the
  Fontes Installer app again and choose **Add or change keys**.
- **Windows:** double-click **Add or change keys.cmd** in the installer folder.

Typing is hidden. The keys go into every app that already has Fontes. Quit and reopen the apps
afterwards. Where to get the keys and what they unlock: [KEYS.md](KEYS.md).

### Backups, reruns and removing

The installer only changes the `fontes` entry. Every other setting and comment stays as it was.
Before it changes a file, it saves a copy next to it, named `<file>.fontes-backup-<date>`. Copies
made after you added keys contain those keys: delete the ones you no longer need. It also
installs uv. Running it again is safe: it repairs the setup and changes nothing else.

To remove Fontes, double-click **Uninstall Fontes.command** (Mac) or **Uninstall Fontes.cmd**
(Windows). It removes the `fontes` entry, keys included, from every app. Your other settings
and the backup copies stay.

## Updates

- **Installer and `.mcpb` file:** you don't need to do anything. Once a day, when the app
  starts, Fontes checks for a newer version in the background and gets it ready; the next time
  the app starts it uses it. If an update cannot be downloaded or does not work, Fontes keeps
  using the version that worked.
- **`uvx`:** Fontes tells you when a newer version is available, at the top of its list of
  jurisdictions. To always run the newest version, use `fontes-mcp@latest` in place of `fontes-mcp`.

No information about you or your searches is sent anywhere for this.

## Privacy

Fontes sends nothing about you or your searches by default. Usage counts are opt-in, and a bug
report is sent only after you see it and confirm. Details: [PRIVACY.md](PRIVACY.md).

## Removing it

Remove the `fontes` entry from your app's MCP settings (in Claude Code:
`claude mcp remove fontes`), then quit and reopen the app.

## Good to know

Fontes reads public sources, mostly court and government websites. It marks unofficial ones in
its answers. Always open the source link before relying on a decision or a provision.

If something goes wrong, email what you did and the error you saw to fontesmcp@proton.me.

## Before you rely on it

- Fontes is a research tool, not legal advice. Using it does not make anyone your lawyer.
- It is provided "as is", with no warranty, and its authors are not liable for how it is used,
  as far as the law allows. The full terms are in the [licence](../LICENSE) (Apache 2.0).
