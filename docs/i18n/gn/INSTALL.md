> Ko ñembohasa ojejapo máquina pytyvõ reheve. Pe inglés ñe'ẽme oĩva ha'e pe autoritativo.

# Fontes ñemohenda

Fontes oheja nde aplicación IA-pe oheka tribunalkuéra sentencia ha léikuéra ko'ag̃aite
tribunal ha gobierno sitio web-pe, 120 jurisdicción ári. Opaite mbohovái ojoaju pe original
rehe. Ha'e peteĩ servidor MCP estándar, upévare oiko oimeraẽ aplicación ikatúvape omboguata
peteĩ servidor MCP local: Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub
Copilot), Gemini CLI, Windsurf, Zed, LM Studio, Cline ha ambue.

Eiporavo nde aplicación, ejapo hembiapo, upéi [ehecha oikópa](#ehecha-oikópa).

## Claude Desktop

1. Emboguejy Fontes archivo `.mcpb`
   [ñemosẽ ipyahuvévagui](https://github.com/ykarapazar/fontes/releases/latest).
2. Ejopy mokõi jey hese. Claude Desktop oipe'áta.
3. Ejopy **Install**.

## Codex

Peteĩ terminal-pe:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI ha Codex IDE extensión oipuru oñondive ko configuración (`~/.codex/config.toml`).
Reikotevẽ [uv](#reikotevẽ-uv).

## Claude Code

Peteĩ terminal-pe:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Reikotevẽ [uv](#reikotevẽ-uv).

## Ambue aplicación

Peteĩteĩ ko'ãva oikotevẽ [uv](#reikotevẽ-uv). Embojoapy entrada, eñongatu, upéi emboty ha
eipe'a jey aplicación.

**Cursor:** `~/.cursor/mcp.json`-pe (opaite proyecto) térã `.cursor/mcp.json`-pe (peteĩ proyecto):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** emboguata **MCP: Add Server** Command Palette-gui, eiporavo
**Command (stdio)**, ehai `uvx fontes-mcp` ha embohéra servidor `fontes`. Térã embojoapy kóva
`~/.copilot/mcp-config.json`-pe:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

VS Code configuración tujavéva oipuru `.vscode/mcp.json`, upépe clave yvategua ha'e `servers`
`mcpServers` rendaguépe.

**Gemini CLI:** peteĩ terminal-pe, `gemini mcp add -s user fontes uvx fontes-mcp`. Térã embojoapy
kóva `~/.gemini/settings.json`-pe:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** eipe'a nde archivo configuración (**zed: open settings file**) ha embojoapy:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** barra akatúa gotyogua-pe, eipe'a pestaña **Program**, ejopy **Install → Edit
mcp.json**, ha embojoapy:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** ejopy ícono **MCP Servers**, eipe'a pestaña **Configure**, ejopy **Configure MCP
Servers**, ha embojoapy pe entrada `mcpServers` peteĩchagua LM Studio-pe g̃uaráicha.

**Claude Desktop, nde pópe** (archivo `.mcpb` rendaguépe): embojoapy pe entrada `mcpServers`
peteĩchagua `claude_desktop_config.json`-pe (macOS: `~/Library/Application Support/Claude/`,
Windows: `%APPDATA%\Claude\`).

**Oimeraẽ ambue aplicación MCP** (Windsurf ha ambue): idocumentación ijeheguáva he'i moõpa
oñongatu iservidor MCP-kuéra. Hetavéva ohupyty pe entrada peteĩchagua: comando `uvx`,
argumento `fontes`.

Aplicación ndojuhúiramo `uvx`, eipuru hape opaite (macOS ha Linux-pe, `which uvx` ohai).

## Reikotevẽ uv

Codex, Claude Code ha ambue aplicación omoñepyrũ Fontes `uvx` reheve, ou **uv** ndive,
peteĩ tembiporu michĩ ha reigua Astral mba'éva. Remohenda hag̃ua, ehecha
[Astral ñehesa'ỹijo](https://docs.astral.sh/uv/getting-started/installation/), térã emboguata:

- macOS térã Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Clave-kuéra

Oĩ ypykue oikotevẽva peteĩ clave reigua: ehecha [KEYS.md](KEYS.md).

## Ehecha oikópa

Peteĩ chat pyahúpe, eporandu: *"Mba'e jurisdicción-pepa ikatu oheka Fontes?"* Aplicación
ombohovaiva'erã peteĩ tetã lista reheve. Ndojapóiramo, emboty ha eipe'a jey aplicación
peteĩ jey.

## Instalador peteĩ click-pe (oúma)

Peteĩ instalador Mac ha Windows-pe g̃uarã omohendáva Fontes opaite nde aplicación-pe
peteĩ jeýpe oúma. Omohenda Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub
Copilot), Windsurf, Gemini CLI, Zed, LM Studio ha Cline. Osẽ rire:

**Reñepyrũ mboyve:** emboty opaite peteĩteĩ ko'ã aplicación. Kóva tuichavéva Claude Code-pe
g̃uarã: oiko aja, ohai jey `~/.claude.json` ha ikatu oipe'a instalador omoambuéva.
Ndaikatúiramo remboty Claude Code, embojoapy Fontes hese `claude mcp add` reheve (ehecha
[Claude Code](#claude-code)).

**Mac**

1. Eipe'a carpeta **Fontes Installer** remboguejy va'ekue.
2. Ejopy mokõi jey **Install Fontes.command** ári.
   - Nde Mac he'íramo "cannot be opened because it is from an unidentified developer":
     ejopy akatúa (térã Control-click) pe archivo ári, eiporavo **Open**, upéi **Open**
     jey. Rejapo kóva peteĩ jey añoite.
3. Ojepe'a peteĩ ovetã ha ndeporandu omondótapa papapy jeporu rehegua réra'ỹre; ejopy
   Enter nahániri hag̃ua.
4. Ndeporandu rembojoapysépa clave ko'ág̃a. Ejopy Enter rehasa hag̃ua; ehecha
   [Clave ñembojoapy](#clave-ñembojoapy).
5. He'ívo **Done**, eipe'a jey nde aplicación IA-kuéra.

**Windows**

1. Emosẽ ZIP-gui **Fontes Installer** remboguejy va'ekue (akatúa click → Extract All).
2. Ejopy mokõi jey **Install Fontes.cmd** ári.
   - Windows ohechaukáramo "Windows protected your PC": ejopy **More info**, upéi **Run anyway**.
3. Ndeporandúvo omondótapa papapy jeporu rehegua réra'ỹre, ejopy Enter nahániri hag̃ua.
4. Ndeporandu rembojoapysépa clave ko'ág̃a. Ejopy Enter rehasa hag̃ua; ehecha
   [Clave ñembojoapy](#clave-ñembojoapy).
5. He'ívo **Done**, eipe'a jey nde aplicación IA-kuéra. Peteĩ oikóramo gueteri, emboty
   opaite (sistema bandeja-gui avei, aravopapaha ykére) ha eipe'a jey.

Opahápe instalador ohechauka aplicación omohenda va'ekue lista.

### Mba'e aplicación-pepa omohenda

Omohenda peteĩ aplicación upe aplicación carpeta configuración oĩmaramo nde computadora-pe
añoite. Claude Code oñemohenda `~/.claude.json` oĩramo añoite. Claude Desktop oñemohenda
akóinte. Peteĩteĩ aplicación ohupyty peteĩ entrada, `fontes`, ko archivo-pe:

| Aplicación | Archivo (Mac ha Linux) | Archivo (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, ha Microsoft Store versión kópia ijeheguáva |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, térã `~/.codeium/windsurf/mcp_config.json` versión tujavévape | `%APPDATA%\devin\mcp_config.json`, térã `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code oñemohenda `~/.copilot` térã VS Code carpeta configuración ijeheguáva oĩramo.

Mokõi aplicación oikotevẽ peteĩ tembiapo ambue:

- **Windsurf:** reipe'a jey rire, ejopy refresh Cascade-pe.
- **Cline VS Code extensión tujavéva ryepýpe:** embojoapy Fontes nde pópe (ehecha [Cline](#ambue-aplicación)).

### Clave ñembojoapy

Ñemohenda rire pya'e, instalador ndeporandu rembojoapysépa Francia ha Estados Unidos clave
reigua. Rembojoapy térã remoambue hag̃ua upéi:

- **Mac:** ejopy mokõi jey **Add or change keys.command** instalador carpeta-pe, térã eipe'a
  jey aplicación Fontes Installer ha eiporavo **Add or change keys**.
- **Windows:** ejopy mokõi jey **Add or change keys.cmd** instalador carpeta-pe.

Rehaíva oñeñomi. Clave-kuéra oike opaite aplicación oguerekómava Fontes-pe. Upéi emboty ha
eipe'a jey aplicación-kuéra. Moõpa rehupyty clave ha mba'épa oipe'a: [KEYS.md](KEYS.md).

### Kópia, ñemboguata jey ha ñenohẽ

Instalador omoambue entrada `fontes` añoite. Ambue configuración ha comentario opyta oĩ
haguéicha. Omoambue mboyve peteĩ archivo, oñongatu peteĩ kópia ykére, hérava
`<file>.fontes-backup-<date>`. Kópia ojejapóva rembojoapy rire clave oguereko umi clave:
embogue umi ndereikotevẽvéima. Omohenda avei uv. Remboguata jeýramo ndaipóri peligro:
omyatyrõ ñemohenda ha nomoambuéi ambue mba'eve.

Renohẽ hag̃ua Fontes, ejopy mokõi jey **Uninstall Fontes.command** (Mac) térã **Uninstall
Fontes.cmd** (Windows) ári. Onohẽ entrada `fontes`, clave-kuéra reheve, opaite aplicación-gui.
Nde ambue configuración ha umi kópia opyta.

## Ñembopyahu

- **Instalador ha archivo `.mcpb`:** ndereikotevẽi rejapo mba'eve. Ára ha ára peteĩ jey,
  aplicación oñepyrũvo, Fontes ohecha kañyhápe oĩpa versión ipyahuvéva ha ombosako'i;
  aplicación oñepyrũ jey jave oipurúta. Peteĩ ñembopyahu ndaikatúiramo ojemboguejy térã
  ndoikóiramo, Fontes oipuru akóinte pe versión oiko porã va'ekue.
- **`uvx`:** Fontes he'i ndéve oĩramo versión ipyahuvéva, jurisdicción lista yvatégui.
  Remboguata hag̃ua akóinte versión ipyahuvéva, eipuru `fontes-mcp@latest` `fontes-mcp` rendaguépe.

Kóvape g̃uarã nomondói mamove mba'eve nde térã nde jeheka rehegua.

## Privacidad

Fontes nomondói mba'eve nde térã nde jeheka rehegua ijypýpe. Papapy jeporu rehegua
oñemondo ere héẽ ramo añoite, ha jejavy marandu oñemondo rehecha ha remoneĩ rire añoite.
Mba'emimi: [PRIVACY.md](PRIVACY.md).

## Mba'éichapa ojenohẽ

Enohẽ entrada `fontes` nde aplicación configuración MCP-gui (Claude Code-pe:
`claude mcp remove fontes`), upéi emboty ha eipe'a jey aplicación.

## Iporã reikuaa

Fontes omoñe'ẽ ypykue público, hetavéva tribunal ha gobierno sitio web. Omarka umi
ndaha'éiva oficial imbohováipe. Akóinte eipe'a ypykue joaju rejerovia mboyve peteĩ
sentencia térã disposición rehe.

Oĩramo mba'e ndoikóiva, emondo mba'épa rejapo ha jejavy rehecháva fontesmcp@proton.me-pe.

## Rejerovia mboyve hese

- Fontes ha'e peteĩ tembiporu jeheka rehegua, ndaha'éi asesoramiento jurídico. Ojepurúramo
  ndojapói avavégui nde abogado.
- Oñeme'ẽ "oĩháicha" (as is), garantía'ỹre, ha ijapoharakuéra ndaha'éi responsable
  mba'éichapa ojepuru rehe, léi oheja peve. Condición opaite oĩ [licencia](../../../LICENSE)-pe
  (Apache 2.0).
