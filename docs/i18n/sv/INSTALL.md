> Detta är en maskinstödd översättning. Den engelska versionen gäller.

# Installera Fontes

Fontes låter din AI-app slå upp domstolsavgöranden och lagstiftning direkt på domstolars och myndigheters
webbplatser i fler än 120 jurisdiktioner. Varje resultat länkar till originalet. Det är en standard-MCP-server,
så den fungerar i alla appar som kan köra en lokal MCP-server: Claude Desktop, Codex, Claude
Code, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio, Cline med flera.

Välj din app, följ stegen för den och [kontrollera sedan att det fungerar](#kontrollera-att-det-fungerar).

## Claude Desktop

1. Ladda ned Fontes `.mcpb`-fil från
   [den senaste versionen](https://github.com/ykarapazar/fontes/releases/latest).
2. Dubbelklicka på den. Claude Desktop öppnar den.
3. Klicka på **Install**.

## Codex

I en terminal:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI och Codex-tillägget för IDE delar den här inställningen (`~/.codex/config.toml`).
Du behöver [uv](#du-behöver-uv).

## Claude Code

I en terminal:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Du behöver [uv](#du-behöver-uv).

## Andra appar

Var och en av dessa behöver [uv](#du-behöver-uv). Lägg till posten, spara, och avsluta och öppna sedan appen igen.

**Cursor:** i `~/.cursor/mcp.json` (alla projekt) eller `.cursor/mcp.json` (ett projekt):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** kör **MCP: Add Server** från Command Palette, välj
**Command (stdio)**, ange `uvx fontes-mcp` och ge servern namnet `fontes`. Eller lägg till detta i
`~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Äldre VS Code-konfigurationer använder `.vscode/mcp.json`, där nyckeln på översta nivån är `servers` i stället för
`mcpServers`.

**Gemini CLI:** i en terminal, `gemini mcp add -s user fontes uvx fontes-mcp`. Eller lägg till detta i
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** öppna din inställningsfil (**zed: open settings file**) och lägg till:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** i sidofältet till höger, öppna fliken **Program**, klicka på **Install → Edit
mcp.json** och lägg till:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** klicka på ikonen **MCP Servers**, öppna fliken **Configure**, klicka på **Configure MCP
Servers** och lägg till samma `mcpServers`-post som för LM Studio.

**Claude Desktop, för hand** (i stället för `.mcpb`-filen): lägg till samma `mcpServers`-post i
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Alla andra MCP-appar** (Windsurf med flera): appens egen dokumentation anger var den lagrar sina MCP-servrar.
De flesta använder samma post: kommando `uvx`, argument `fontes`.

Om appen inte hittar `uvx`, använd dess fullständiga sökväg (på macOS och Linux skriver `which uvx` ut den).

## Du behöver uv

Codex, Claude Code och de andra apparna startar Fontes med `uvx`, som följer med **uv**, ett litet
kostnadsfritt verktyg från Astral. För att installera det, se
[Astrals guide](https://docs.astral.sh/uv/getting-started/installation/), eller kör:

- macOS eller Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Nycklar

Vissa källor kräver en kostnadsfri nyckel: se [KEYS.md](KEYS.md).

## Kontrollera att det fungerar

Fråga i en ny chatt: *”Vilka jurisdiktioner kan Fontes söka i?”* Appen bör svara med en
lista över länder. Om den inte gör det, avsluta och öppna appen en gång till.

## Installationsprogram med ett klick (på väg)

Ett installationsprogram för Mac och Windows som konfigurerar Fontes i alla dina appar på en gång är på väg. Det
konfigurerar Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI,
Zed, LM Studio och Cline. När det har släppts:

**Innan du börjar:** avsluta var och en av dessa appar helt. Det är viktigast för Claude Code:
medan den körs skriver den om `~/.claude.json` och kan ångra installationsprogrammets ändring. Om du inte kan
avsluta Claude Code, lägg i stället till Fontes i den med `claude mcp add` (se [Claude Code](#claude-code)).

**Mac**

1. Öppna den nedladdade mappen **Fontes Installer**.
2. Dubbelklicka på **Install Fontes.command**.
   - Om din Mac säger att filen ”cannot be opened because it is from an unidentified developer”:
     högerklicka (eller Ctrl-klicka) på filen, välj **Open** och sedan **Open** igen. Det behöver du
     bara göra en gång.
3. Ett fönster öppnas och frågar om anonyma användningssiffror ska skickas; tryck Enter för nej.
4. Det frågar om nycklar ska läggas till nu. Tryck Enter för att hoppa över; se [Nyckelsteget](#nyckelsteget).
5. När det står **Done**, öppna dina AI-appar igen.

**Windows**

1. Packa upp den nedladdade **Fontes Installer** (högerklicka → Extract All).
2. Dubbelklicka på **Install Fontes.cmd**.
   - Om Windows visar ”Windows protected your PC”: klicka på **More info** och sedan **Run anyway**.
3. När du får frågan om anonyma användningssiffror ska skickas, tryck Enter för nej.
4. Det frågar om nycklar ska läggas till nu. Tryck Enter för att hoppa över; se [Nyckelsteget](#nyckelsteget).
5. När det står **Done**, öppna dina AI-appar igen. Om någon fortfarande var igång, stäng den
   helt (även från systemfältet, vid klockan) och öppna den igen.

Till sist listar installationsprogrammet de appar det har konfigurerat.

### Vilka appar det konfigurerar

Det konfigurerar en app endast om appens inställningsmapp redan finns på din dator. Claude Code
konfigureras endast om `~/.claude.json` finns. Claude Desktop konfigureras alltid. Varje app får en
post, `fontes`, i den här filen:

| App | Fil (Mac och Linux) | Fil (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, samt Microsoft Store-versionens egen kopia |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, eller `~/.codeium/windsurf/mcp_config.json` i äldre versioner | `%APPDATA%\devin\mcp_config.json`, eller `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code konfigureras om `~/.copilot` eller VS Codes egen inställningsmapp finns.

Två appar behöver ett steg till:

- **Windsurf:** när du har öppnat den igen, tryck på uppdatera i Cascade.
- **Cline i det äldre VS Code-tillägget:** lägg till Fontes för hand (se [Cline](#andra-appar)).

### Nyckelsteget

Direkt efter installationen erbjuder installationsprogrammet att lägga till de kostnadsfria nycklarna för Frankrike och USA. För att lägga till eller
ändra dem senare:

- **Mac:** dubbelklicka på **Add or change keys.command** i installationsmappen, eller öppna
  appen Fontes Installer igen och välj **Add or change keys**.
- **Windows:** dubbelklicka på **Add or change keys.cmd** i installationsmappen.

Det du skriver döljs. Nycklarna läggs in i alla appar som redan har Fontes. Avsluta och öppna apparna
igen efteråt. Var du får nycklarna och vad de ger tillgång till: [KEYS.md](KEYS.md).

### Säkerhetskopior, omkörningar och borttagning

Installationsprogrammet ändrar endast posten `fontes`. Alla andra inställningar och kommentarer förblir som de var.
Innan det ändrar en fil sparar det en kopia bredvid den, med namnet `<file>.fontes-backup-<date>`. Kopior
som gjorts efter att du lagt till nycklar innehåller de nycklarna: radera dem du inte längre behöver. Det
installerar också uv. Det är säkert att köra det igen: det reparerar konfigurationen och ändrar inget annat.

För att ta bort Fontes, dubbelklicka på **Uninstall Fontes.command** (Mac) eller **Uninstall Fontes.cmd**
(Windows). Det tar bort posten `fontes`, nycklarna inräknade, från alla appar. Dina övriga inställningar
och säkerhetskopiorna finns kvar.

## Uppdateringar

- **Installationsprogrammet och `.mcpb`-filen:** du behöver inte göra något. En gång om dagen, när appen
  startar, söker Fontes efter en nyare version i bakgrunden och gör den klar; nästa gång
  appen startar använder den den. Om en uppdatering inte kan laddas ned eller inte fungerar fortsätter Fontes
  att använda den version som fungerade.
- **`uvx`:** Fontes meddelar dig när en nyare version finns, överst i sin lista över
  jurisdiktioner. För att alltid köra den senaste versionen, använd `fontes-mcp@latest` i stället för `fontes-mcp`.

Ingen information om dig eller dina sökningar skickas någonstans för detta.

## Integritet

Fontes skickar som standard ingenting om dig eller dina sökningar. Användningssiffror är opt-in, och en felrapport
skickas endast efter att du har sett den och bekräftat. Detaljer: [PRIVACY.md](PRIVACY.md).

## Ta bort det

Ta bort posten `fontes` från appens MCP-inställningar (i Claude Code:
`claude mcp remove fontes`), och avsluta och öppna sedan appen igen.

## Bra att veta

Fontes läser offentliga källor, mestadels domstolars och myndigheters webbplatser. Det markerar inofficiella källor i
sina svar. Öppna alltid källänken innan du förlitar dig på ett avgörande eller en bestämmelse.

Om något går fel, mejla vad du gjorde och vilket fel du fick till fontesmcp@proton.me.

## Innan du förlitar dig på det

- Fontes är ett researchverktyg, inte juridisk rådgivning. Att använda det gör inte någon till din advokat.
- Det tillhandahålls ”i befintligt skick”, utan garanti, och dess upphovspersoner ansvarar inte för hur det används,
  i den utsträckning lagen tillåter. De fullständiga villkoren finns i [licensen](../../../LICENSE) (Apache 2.0).
