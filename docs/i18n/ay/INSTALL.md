> Aka jaqukipäwix mäkina yanapt'ampiw luratawa. Inglés arun qillqatawa chiqapax (autoritativo).

# Fontes instalaña

Fontes ukax IA aplicacionamaruw taripañ utanakan taripäwinakap, kamachinaksa taripañ uta,
gobierno web sitionakan jichhpach thaqañapatak yanapt'i, 125 jurisdiccionat. Sapa
jaysäwix originalaruw mayachata. Mä estándar MCP servidorawa, ukatwa mä local MCP servidor
irnaqayañ puedki uka kuna aplicacionansa irnaqi: Claude Desktop, Codex, Claude Code, Cursor,
VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio, Cline, yaqhanakansa.

Aplicacionam ajllim, lurawinakap lurtam, ukat [irnaqatap uñakipam](#irnaqatap-uñakipaña).

## Claude Desktop

1. Fontes `.mcpb` archivo
   [qhipa apsuwita](https://github.com/ykarapazar/fontes/releases/latest) apaqam.
2. Ukar pä kuti click lurtam. Claude Desktop jist'arasini.
3. **Install** ukar click lurtam.

## Codex

Mä terminal ukana:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI, Codex IDE extensión ukanakax aka configuración (`~/.codex/config.toml`)
chikachasipxi. [uv](#uv-wakisiwa) wakisiwa.

## Claude Code

Mä terminal ukana:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

[uv](#uv-wakisiwa) wakisiwa.

## Yaqha aplicacionanaka

Sapa maynix [uv](#uv-wakisiwa) munaraki. Qillqat yapxatam, imam, ukat aplicación
jist'antam, wasitat jist'aram.

**Cursor:** `~/.cursor/mcp.json` ukana (taqi proyectonaka) jan ukax `.cursor/mcp.json` ukana (mä proyecto):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** Command Palette ukat **MCP: Add Server** irnaqayam,
**Command (stdio)** ajllim, `uvx fontes-mcp` qillqam, servidorarus `fontes` sutimp uchañam. Jan
ukax akx `~/.copilot/mcp-config.json` ukar yapxatam:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Nayra VS Code configuracionax `.vscode/mcp.json` apnaqi, ukansti nayrïr llavex `servers`
ukawa, `mcpServers` lanti.

**Gemini CLI:** mä terminal ukana, `gemini mcp add -s user fontes uvx fontes-mcp`. Jan ukax akx
`~/.gemini/settings.json` ukar yapxatam:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** configuración archivom jist'aram (**zed: open settings file**) ukat yapxatam:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** kupi tuqin barra ukana, **Program** pestaña jist'aram, **Install → Edit
mcp.json** ukar click lurtam, ukat yapxatam:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** **MCP Servers** ícono ukar click lurtam, **Configure** pestaña jist'aram,
**Configure MCP Servers** ukar click lurtam, ukat LM Studio ukan pachpa `mcpServers` qillqat
yapxatam.

**Claude Desktop, amparampi** (`.mcpb` archivo lanti): pachpa `mcpServers` qillqat
`claude_desktop_config.json` ukar yapxatam (macOS: `~/Library/Application Support/Claude/`,
Windows: `%APPDATA%\Claude\`).

**Kuna yaqha MCP aplicacionasa** (Windsurf, yaqhanakasa): pachpa documentacionapaw kawkins
MCP servidoranakap imaski uk siwa. Jilpachax pachpa qillqat katuqi: comando `uvx`,
argumento `fontes-mcp`.

Aplicacionax `uvx` jan jikxatkchixa, taqpach thakip apnaqam (macOS, Linux ukana, `which uvx`
ukax uñacht'ayi).

## uv wakisiwa

Codex, Claude Code, yaqha aplicacionanakas Fontes `uvx` ukampiw qalltayapxi, ukax **uv**
ukampiw juti, Astral ukan mä jisk'a inaki irnaqañapa. Instalañatakix
[Astral ukan yatichäwip](https://docs.astral.sh/uv/getting-started/installation/) uñjam, jan
ukax irnaqayam:

- macOS jan ukax Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Llavenaka

Yaqhip jalsunakax inaki llaveniw wakisi: [KEYS.md](KEYS.md) uñjam.

## Irnaqatap uñakipaña

Mä machaq chat ukana jiskt'am: *"Kawkïr jurisdiccionanakansa Fontes thaqaspa?"*
Aplicacionax mä markanak siqimpiw jaysañapa. Jan ukham lurkchixa, aplicación mä kuti
jist'antam, wasitat jist'aram.

## Mä click instalador (Mac ukat Windows)

Instaladorax Fontes taqi aplicacionanakaman mä kutik wakicht'i: Claude Desktop, Codex,
Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio, Cline.

**Janïr qalltkasa:** aka aplicacionanakat kawkïrinakas jist'arataki ukanak jist'antam. Akax
Claude Code ukatakix juk'amp wakiskiriwa: irnaqkasax `~/.claude.json` wasitat qillqi, ukat
instaladorax lurki uka chhaqtayaspawa. Claude Code jist'antañ jan puedkasma ukhaxa, Fontes
ukar `claude mcp add` ukamp yapxatam ([Claude Code](#claude-code) uñjam).

**Mac**

1. Mac instalador (`Fontes-Installer-…-mac.zip`)
   [qhipa apsuwita](https://github.com/ykarapazar/fontes/releases/latest) ukat apaqam, ukat
   jist'arañatakix pä kuti click lurtam.
2. **Fontes Installer** ukar pä kuti click lurtam. Macamax internet ukat apaqat aplicación
   jist'arañ munasmati sasin jiskt'ani ukhaxa, **Open** ukar click lurtam.
3. **Instalaña** ajllim ukat **Walikiwa** ukar click lurtam. Wakicht'añax niya mä minutow alt'i.
4. Mä yatiyäwiw wakicht'at aplicacionanak uñacht'ayi. **Tukuyatawa** ukar click lurtam, ukat uka
   aplicacionanak wasitat jist'aram. Nayraqat munasaw inaki llavenak yapxatañatakix, **Llavenak yapxataña**
   ukar click lurtam; [Llave yapxataña](#llave-yapxataña) uñjam.

**Windows**

1. Windows instalador (`Fontes-Setup-….exe`) [qhipa apsuwita](https://github.com/ykarapazar/fontes/releases/latest) ukat apaqam, ukat pä kuti click lurtam.
   - Windows "Windows protected your PC" uñacht'ayi ukhaxa: **More info** ukar click lurtam,
     ukat **Run anyway**.
2. **Instalaña** ajllim. Mä wintana uñacht'ayi, ukat Fontes wakicht'i.
3. Jan sutin apnaqat jakhunak apayañ munasmati sasin jiskt'kätam ukhaxa, jan sañatakix
   Enter limt'am.
4. Jichhax llave yapxatañ munasmati sasaw jiskt'i. Pasañatakix Enter limt'am;
   [Llave yapxataña](#llave-yapxataña) uñjam.
5. **Done** siski ukhaxa, IA aplicacionanakam wasitat jist'aram. Maynix irnaqaskakchixa,
   taqpach jist'antam (bandeja del sistema ukatsa, pacha uñacht'ayir jak'ana) ukat wasitat
   jist'aram.

Tukuyañanx instaladorax wakicht'ki uka aplicacionanak siqi uñacht'ayi.

### Kawkïr aplicacionanaksa wakicht'i

Mä aplicacionax configuración carpetapax computadoraman utjki ukhakiw wakicht'ata.
Claude Code ukax `~/.claude.json` utjki ukhakiw wakicht'ata. Claude Desktop ukax sapakutiw
wakicht'ata. Sapa aplicacionax mä qillqat katuqi, `fontes`, aka archivo ukana:

| Aplicación | Archivo (Mac, Linux) | Archivo (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, ukat Microsoft Store versión ukan pachpa copiapa |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, jan ukax nayra versionanakan `~/.codeium/windsurf/mcp_config.json` | `%APPDATA%\devin\mcp_config.json`, jan ukax `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code ukax `~/.copilot` jan ukax VS Code ukan pachpa configuración carpetapax utjki ukhaw
wakicht'ata.

Pä aplicacionax yaqha lurawi munapxi:

- **Windsurf:** wasitat jist'arasax Cascade ukan refresh ukar click lurtam.
- **Nayra Cline VS Code extensión manqhana:** Fontes amparamamp yapxatam ([Cline](#yaqha-aplicacionanaka) uñjam).

### Llave yapxataña

Instalasax mäkiw, instaladorax Francia, Estados Unidos ukatak inaki llavenak yapxatañ
munasmati sasaw jiskt'i. Qhipat yapxatañataki jan ukax mayjt'ayañataki:

- **Mac:** **Fontes Installer** wasitat jist'aram ukat **Llavenak yapxataña jan ukax mayjt'ayaña** ajllim.
- **Windows:** Start menu ukar jist'aram, ukat **Fontes** → **Llavenak yapxataña jan ukax mayjt'ayaña** ajllim.

Qillqkta ukax imantatawa. Llavenakax Fontes utjki uka taqi aplicacionanakaruw mantapxi.
Ukat aplicacionanak jist'antam, wasitat jist'aram. Kawkits llave jikxatasi, kunsa jist'ari:
[KEYS.md](KEYS.md).

### Copianaka, wasitat irnaqayaña, apsuña

Instaladorax `fontes` qillqatakiw mayjt'ayi. Yaqha configuración, comentarionakas
kunjamäkänsa ukhamaw qhiparapxi. Mä archivo mayjt'ayañat nayraqatax jak'apan mä copia imi,
`<file>.fontes-backup-<date>` sutini. Llavenak yapxatkasin lurat copianakax uka llavenakaniwa:
jan wakiskir copianak chhaqtayam. uv ukas wakicht'arakiwa. Wasitat irnaqayañax janiw
jan walt'äwïkiti: instalación askichi, janirakiw yaqha kunas mayjt'aykiti.

Fontes apsuñatakix **Fontes Installer** jist'aram ukat **Apaqaña** ajllim (Mac), jan ukax
Settings → Apps (Windows) ukan **Fontes** apsuña. `fontes` qillqat taqi aplicacionanakat
apsu, llavenakapampi. Yaqha configuracionamax, copianakas qhiparapxiwa.

## Machaqtayäwinaka

- **Instalador, `.mcpb` archivo:** janiw kuns luraña wakiskiti. Sapa uru mä kuti, aplicacionax
  qalltki ukhaxa, Fontes ukax imantat machaq versión uñakipi ukat wakicht'i; aplicacionax
  wasitat qalltki ukhaw apnaqasini. Mä machaqtayäwix apaqañ jan puedkchi jan ukax jan
  irnaqkchixa, Fontes ukax qhipa irnaqkän uka versionampiw sarantaskaki.
- **`uvx`:** Fontes ukax machaq versión utjki ukhaxa, jurisdiccionanak siqi patxan
  yatiyätam. Sapakut qhipa versión irnaqayañatakix `fontes-mcp` lanti `fontes-mcp@latest` apnaqam.

Akatakix janiw kunas jumat jan ukax thaqäwinakamat kawkirus apayaskiti.

## Privacidad

Fontes ukax nayratpach janiw kuns jumat jan ukax thaqäwinakamat apaykiti. Apnaqat jakhunakax
jïsa sasma ukhakiw apayasi, pantjat yatiyäwinakasti uñjasin chiqapar sasma ukhakiw apayasi.
Juk'ampi: [PRIVACY.md](PRIVACY.md).

## Kunjams apsuña

Aplicacionaman MCP configuracionapat `fontes` qillqat apsum (Claude Code ukana:
`claude mcp remove fontes`), ukat aplicación jist'antam, wasitat jist'aram.

## Yatiñatak wakiski

Fontes ukax público jalsunak liyi, jilpachax taripañ uta, gobierno web sitionakawa. Jan
oficial jalsunakax jaysäwinakapan uñacht'ayatawa. Mä taripäwir jan ukax disposición ukar
confiañat nayraqatax sapakut jalsun mayachäwip jist'aram.

Kunas jan irnaqkchixa, kuns lurkta, kuna pantjasïwis uñstawayi uk fontesmcp@proton.me ukar
apayam.

## Janïr confiaskasa

- Fontes ukax thaqañ irnaqañawa, janiw asesoramiento jurídicokiti. Apnaqañax janiw abogadoma
  lantikiti.
- "Kunjamäki ukhamaw" (as is) churata, jan garantíani, luririnakapasti janiw kunjams apnaqasi
  uka tuqit responsablekiti, kamachix jaytki ukhakama. Taqpach condicionanakax
  [licencia](../../../LICENSE) ukankiwa (Apache 2.0).
