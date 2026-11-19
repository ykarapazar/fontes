> Dies ist eine maschinengestützte Übersetzung. Maßgeblich ist die englische Fassung.

# Fontes installieren

Mit Fontes kann Ihre KI-App Gerichtsentscheidungen und Rechtsvorschriften live auf Websites von
Gerichten und Behörden in über 120 Rechtsordnungen nachschlagen. Jedes Ergebnis verlinkt auf das
Original. Fontes ist ein standardkonformer MCP-Server und funktioniert daher in jeder App, die einen
lokalen MCP-Server ausführen kann: Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub
Copilot), Gemini CLI, Windsurf, Zed, LM Studio, Cline und weiteren.

Wählen Sie Ihre App, folgen Sie ihren Schritten und [prüfen Sie dann, ob es funktioniert](#prüfen-ob-es-funktioniert).

## Claude Desktop

1. Laden Sie die Fontes-Datei `.mcpb` aus dem
   [neuesten Release](https://github.com/ykarapazar/fontes/releases/latest) herunter.
2. Doppelklicken Sie darauf. Claude Desktop öffnet sie.
3. Klicken Sie auf **Install**.

## Codex

In einem Terminal:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Die Codex CLI und die Codex-IDE-Erweiterung teilen sich diese Einstellung (`~/.codex/config.toml`).
Sie benötigen [uv](#sie-benötigen-uv).

## Claude Code

In einem Terminal:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Sie benötigen [uv](#sie-benötigen-uv).

## Andere Apps

Jede dieser Apps benötigt [uv](#sie-benötigen-uv). Fügen Sie den Eintrag hinzu, speichern Sie,
beenden Sie die App und öffnen Sie sie erneut.

**Cursor:** in `~/.cursor/mcp.json` (alle Projekte) oder `.cursor/mcp.json` (ein Projekt):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** Führen Sie in der Befehlspalette **MCP: Add Server** aus, wählen Sie
**Command (stdio)**, geben Sie `uvx fontes-mcp` ein und nennen Sie den Server `fontes`. Oder fügen Sie dies
zu `~/.copilot/mcp-config.json` hinzu:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Ältere VS-Code-Einrichtungen verwenden `.vscode/mcp.json`, wo der oberste Schlüssel `servers` statt
`mcpServers` heißt.

**Gemini CLI:** in einem Terminal `gemini mcp add -s user fontes uvx fontes-mcp`. Oder fügen Sie dies zu
`~/.gemini/settings.json` hinzu:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** Öffnen Sie Ihre Einstellungsdatei (**zed: open settings file**) und fügen Sie hinzu:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** Öffnen Sie in der rechten Seitenleiste den Reiter **Program**, klicken Sie auf
**Install → Edit mcp.json** und fügen Sie hinzu:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** Klicken Sie auf das Symbol **MCP Servers**, öffnen Sie den Reiter **Configure**, klicken Sie
auf **Configure MCP Servers** und fügen Sie denselben `mcpServers`-Eintrag wie bei LM Studio hinzu.

**Claude Desktop, von Hand** (statt mit der `.mcpb`-Datei): Fügen Sie denselben `mcpServers`-Eintrag
zu `claude_desktop_config.json` hinzu (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Jede andere MCP-App** (Windsurf und andere): Ihre eigene Dokumentation sagt, wo sie ihre MCP-Server
speichert. Die meisten nehmen denselben Eintrag: Befehl `uvx`, Argument `fontes`.

Wenn die App `uvx` nicht findet, verwenden Sie den vollständigen Pfad (unter macOS und Linux gibt
`which uvx` ihn aus).

## Sie benötigen uv

Codex, Claude Code und die anderen Apps starten Fontes mit `uvx`, das zu **uv** gehört, einem
kleinen kostenlosen Tool von Astral. Zur Installation siehe die
[Anleitung von Astral](https://docs.astral.sh/uv/getting-started/installation/) oder führen Sie aus:

- macOS oder Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Schlüssel

Einige Quellen benötigen einen kostenlosen Schlüssel: siehe [KEYS.md](KEYS.md).

## Prüfen, ob es funktioniert

Fragen Sie in einem neuen Chat: *„Welche Rechtsordnungen kann Fontes durchsuchen?“* Die App sollte
mit einer Liste von Ländern antworten. Falls nicht, beenden Sie die App und öffnen Sie sie noch
einmal.

## Ein-Klick-Installationsprogramm (Mac und Windows)

Das Installationsprogramm richtet Fontes in allen Ihren Apps auf einmal ein: Claude Desktop,
Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio und Cline.

**Bevor Sie beginnen:** Beenden Sie jede dieser Apps vollständig. Das ist vor allem bei Claude Code
wichtig: Solange es läuft, schreibt es `~/.claude.json` neu und kann die Änderung des
Installationsprogramms rückgängig machen. Wenn Sie Claude Code nicht beenden können, fügen Sie Fontes
stattdessen mit `claude mcp add` hinzu (siehe [Claude Code](#claude-code)).

**Mac**

1. Laden Sie das Mac-Installationsprogramm (`Fontes-Installer-…-mac.zip`) aus dem
   [neuesten Release](https://github.com/ykarapazar/fontes/releases/latest) herunter und
   doppelklicken Sie darauf, um es zu entpacken.
2. Doppelklicken Sie auf **Fontes Installer**. Wenn Ihr Mac fragt, ob eine aus dem Internet
   geladene App geöffnet werden soll, klicken Sie auf **Öffnen**.
3. Wählen Sie **Installieren** und klicken Sie auf **OK**. Die Einrichtung dauert etwa eine Minute.
4. Eine Meldung listet die eingerichteten Apps auf. Klicken Sie auf **Fertig** und öffnen Sie diese
   Apps dann wieder. Um zuerst die optionalen kostenlosen Schlüssel hinzuzufügen, klicken Sie
   stattdessen auf **Schlüssel hinzufügen**; siehe
   [Schlüssel im Installationsprogramm](#schlüssel-im-installationsprogramm).

**Windows**

1. Laden Sie das Windows-Installationsprogramm (`Fontes-Setup-….exe`) aus dem
   [neuesten Release](https://github.com/ykarapazar/fontes/releases/latest) herunter und doppelklicken Sie darauf.
   - Wenn Windows „Der Computer wurde durch Windows geschützt“ anzeigt: Klicken Sie auf **Weitere
     Informationen** und dann auf **Trotzdem ausführen**.
2. Klicken Sie auf **Installieren**. Ein Fenster öffnet sich und richtet Fontes ein.
3. Wenn Sie gefragt werden, ob anonyme Nutzungszahlen gesendet werden sollen, drücken Sie Enter für
   Nein.
4. Es fragt, ob Sie jetzt Schlüssel hinzufügen möchten. Drücken Sie Enter, um das zu überspringen;
   siehe [Schlüssel im Installationsprogramm](#schlüssel-im-installationsprogramm).
5. Wenn **Fertig** erscheint, öffnen Sie Ihre KI-Apps wieder. Falls eine noch lief, schließen Sie sie
   vollständig (auch im Infobereich der Taskleiste, neben der Uhr) und öffnen Sie sie erneut.

Am Ende listet das Installationsprogramm die Apps auf, die es eingerichtet hat.

### Welche Apps es einrichtet

Es richtet eine App nur ein, wenn deren Einstellungsordner bereits auf Ihrem Computer vorhanden ist.
Claude Code wird nur eingerichtet, wenn `~/.claude.json` existiert. Claude Desktop wird immer
eingerichtet. Jede App erhält einen Eintrag, `fontes`, in dieser Datei:

| App | Datei (Mac und Linux) | Datei (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json` sowie die eigene Kopie der Microsoft-Store-Version |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, bei älteren Versionen `~/.codeium/windsurf/mcp_config.json` | `%APPDATA%\devin\mcp_config.json` oder `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code wird eingerichtet, wenn `~/.copilot` oder der eigene Einstellungsordner von VS Code existiert.

Zwei Apps benötigen einen weiteren Schritt:

- **Windsurf:** Drücken Sie nach dem erneuten Öffnen in Cascade auf „Aktualisieren“ (refresh).
- **Cline in der älteren VS-Code-Erweiterung:** Fügen Sie Fontes von Hand hinzu (siehe [Cline](#andere-apps)).

### Schlüssel im Installationsprogramm

Direkt nach der Installation bietet das Installationsprogramm an, die kostenlosen Schlüssel für
Frankreich und die USA hinzuzufügen. So fügen Sie sie später hinzu oder ändern sie:

- **Mac:** Öffnen Sie **Fontes Installer** erneut und wählen Sie **Schlüssel hinzufügen oder ändern**.
- **Windows:** Öffnen Sie das Startmenü und wählen Sie dann **Fontes** → **Schlüssel hinzufügen oder ändern**.

Die Eingabe wird nicht angezeigt. Die Schlüssel werden in jede App eingetragen, die Fontes bereits
hat. Beenden Sie die Apps anschließend und öffnen Sie sie erneut. Wo Sie die Schlüssel erhalten und
was sie freischalten: [KEYS.md](KEYS.md).

### Sicherungskopien, erneutes Ausführen und Entfernen

Das Installationsprogramm ändert nur den Eintrag `fontes`. Alle anderen Einstellungen und Kommentare
bleiben unverändert. Bevor es eine Datei ändert, speichert es daneben eine Kopie mit dem Namen
`<file>.fontes-backup-<date>`. Kopien, die erstellt wurden, nachdem Sie Schlüssel hinzugefügt haben,
enthalten diese Schlüssel: Löschen Sie die, die Sie nicht mehr brauchen. Es installiert außerdem uv.
Ein erneutes Ausführen ist unbedenklich: Es repariert die Einrichtung und ändert sonst nichts.

Um Fontes zu entfernen, öffnen Sie **Fontes Installer** und wählen Sie **Entfernen** (Mac), oder
deinstallieren Sie **Fontes** unter Einstellungen → Apps (Windows). Das entfernt den Eintrag `fontes`,
einschließlich der Schlüssel, aus jeder App. Ihre übrigen Einstellungen und die Sicherungskopien
bleiben erhalten.

## Aktualisierungen

- **Installationsprogramm und `.mcpb`-Datei:** Sie müssen nichts tun. Einmal täglich, wenn die App
  startet, sucht Fontes im Hintergrund nach einer neueren Version und bereitet sie vor; beim nächsten
  Start der App wird sie verwendet. Wenn ein Update nicht heruntergeladen werden kann oder nicht
  funktioniert, verwendet Fontes weiter die Version, die funktioniert hat.
- **`uvx`:** Fontes zeigt oben in seiner Liste der Rechtsordnungen an, wenn eine neuere Version
  verfügbar ist. Um immer die neueste Version auszuführen, verwenden Sie `fontes-mcp@latest` statt
  `fontes`.

Dafür werden keine Informationen über Sie oder Ihre Suchen irgendwohin gesendet.

## Datenschutz

Fontes sendet standardmäßig nichts über Sie oder Ihre Suchen. Nutzungszahlen sind Opt-in, und ein
Fehlerbericht wird erst gesendet, nachdem Sie ihn gesehen und bestätigt haben. Einzelheiten:
[PRIVACY.md](PRIVACY.md).

## Entfernen

Entfernen Sie den Eintrag `fontes` aus den MCP-Einstellungen Ihrer App (in Claude Code:
`claude mcp remove fontes`), beenden Sie die App und öffnen Sie sie erneut.

## Gut zu wissen

Fontes liest öffentliche Quellen, überwiegend Websites von Gerichten und Behörden. Nichtamtliche
Quellen kennzeichnet es in seinen Antworten. Öffnen Sie immer den Link zur Quelle, bevor Sie sich auf
eine Entscheidung oder eine Vorschrift verlassen.

Wenn etwas schiefgeht, schreiben Sie an fontesmcp@proton.me, was Sie getan haben und welchen Fehler
Sie gesehen haben.

## Bevor Sie sich darauf verlassen

- Fontes ist ein Recherchewerkzeug, keine Rechtsberatung. Durch seine Nutzung wird niemand Ihr
  Rechtsanwalt.
- Es wird „wie besehen“ bereitgestellt, ohne Gewährleistung, und seine Autoren haften, soweit
  gesetzlich zulässig, nicht für seine Verwendung. Die vollständigen Bedingungen stehen in der
  [Lizenz](../../../LICENSE) (Apache 2.0).
