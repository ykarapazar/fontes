> Lii ab tekki la bu masin dimbali. Mbind mu Àngale mi moo am sañ-sañ.

# Samp Fontes

Fontes dafay may sa aplikasioŋ AI wut ci saa si àtte yi àttekaay yi def ak yoon yi ci sit internet yu
àttekaay yi ak yu Nguur gi, ci lu ëpp 120 juridiction. Bépp njeexital am na lëkkalekaay bu jëm ci mbind
mu njëkk mi. Serwëer MCP bu ñépp mën a jëfandikoo la, kon dafay dox ci bépp aplikasioŋ bu mën a doxal
ab serwëer MCP ci ordinatëer bi: Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot),
Gemini CLI, Windsurf, Zed, LM Studio, Cline ak yeneen.

Tànnal sa aplikasioŋ, toppal tànk yi, te ginnaaw loolu [saytul ndax mu ngi dox](#saytu-ndax-mu-ngi-dox).

## Claude Desktop

1. Yebal fichier `.mcpb` bu Fontes ci
   [sumb bu mujj bi](https://github.com/ykarapazar/fontes/releases/latest).
2. Cuqal ko ñaari yoon. Claude Desktop dafay ko ubbi.
3. Cuqal **Install**.

## Codex

Ci ab terminal:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI ak extension Codex bu IDE dañuy bokk réglage bii (`~/.codex/config.toml`).
Soxla nga [uv](#soxla-nga-uv).

## Claude Code

Ci ab terminal:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Soxla nga [uv](#soxla-nga-uv).

## Yeneen aplikasioŋ

Bu nekk ci yii soxla na [uv](#soxla-nga-uv). Yokkal xaaju kood bi, denc ko, te nga tëj aplikasioŋ bi
ba mu jeex te ubbiwaat ko.

**Cursor:** ci `~/.cursor/mcp.json` (porose yépp) walla `.cursor/mcp.json` (benn porose):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** doxal **MCP: Add Server** ci Command Palette, tànn
**Command (stdio)**, bind `uvx fontes-mcp` te tudde serwëer bi `fontes`. Walla yokkal lii ci
`~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Réglage yu yàgg yu VS Code dañuy jëfandikoo `.vscode/mcp.json`, fu caabi bu kawe bi di `servers` te du
`mcpServers`.

**Gemini CLI:** ci ab terminal, `gemini mcp add -s user fontes uvx fontes-mcp`. Walla yokkal lii ci
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** ubbil sa fichier réglage (**zed: open settings file**) te yokk:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** ci bànqaas bi ci ndeyjoor, ubbil onglet **Program**, cuq **Install → Edit
mcp.json**, te yokk:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** cuqal ikoŋ **MCP Servers**, ubbi onglet **Configure**, cuq **Configure MCP
Servers**, te yokk xaaju `mcpServers` bi ni ci LM Studio.

**Claude Desktop, ak loxo** (te du ak fichier `.mcpb` bi): yokkal xaaju `mcpServers` bi ci
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Bépp yeneen aplikasioŋ MCP** (Windsurf ak yeneen): dokimaŋ bu aplikasioŋ bi ci boppam moo wax fu mu
denc ay serwëer MCP. Li ëpp ci ñoom dañuy nangu benn xaaj bi: commande `uvx`, argument `fontes`.

Su aplikasioŋ bi gisul `uvx`, jëfandikool yoonam bu mat (ci macOS ak Linux, `which uvx` dafay ko won).

## Soxla nga uv

Codex, Claude Code ak yeneen aplikasioŋ yi dañuy tàmbali Fontes ak `uvx`, bu ànd ak **uv**, ab jumtukaay
bu tuuti bu Astral joxe ci neen. Ngir samp ko, xoolal
[gid bu Astral](https://docs.astral.sh/uv/getting-started/installation/), walla doxal:

- macOS walla Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Caabi yi

Am na ay cosaan yu soxla caabi bu ñu joxe ci neen: xoolal [KEYS.md](KEYS.md).

## Saytu ndax mu ngi dox

Ci benn waxtaan bu bees, laajal: *"Ci ban juridiction la Fontes mën a wut?"* Aplikasioŋ bi dafa war a
tontu ak limu réew yi. Su deful loolu, tëjal aplikasioŋ bi ba mu jeex te ubbiwaat ko benn yoon.

## Programu samp ci benn klig (Mac ak Windows)

Programu samp bi dafay samp Fontes ci say aplikasioŋ yépp ci benn yoon: Claude Desktop, Codex,
Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio ak Cline.
**Balaa ngay tàmbali:** tëjal aplikasioŋ yooyu yépp ba ñu jeex. Lii moo gën a am solo ci Claude Code: su
dee dox, dafay bindaat `~/.claude.json` te mën na far coppite bu programu samp bi def. Su doo mën a tëj
Claude Code, yokkal ci Fontes ak `claude mcp add` (xoolal [Claude Code](#claude-code)).

**Mac**

1. Yebal programu samp bu Mac bi (`Fontes-Installer-…-mac.zip`) ci
   [sumb bu mujj bi](https://github.com/ykarapazar/fontes/releases/latest) te cuq ko ñaari yoon ngir ubbi ko.
2. Cuqal ñaari yoon **Fontes Installer**. Su sa Mac laajee ndax mu ubbi aplikasioŋ bu ñu yeb ci internet,
   cuqal **Open**.
3. Tànnal **Samp** te cuq **OK**. Samp bi dafay yàgg lu tollu ci benn simili.
4. Benn bataaxal dafay wone aplikasioŋ yi mu samp. Cuqal **Jeex na**, te nga ubbiwaat aplikasioŋ yooyu.
   Ngir jëkk a yokk caabi yu ñu joxe ci neen yi (bu la neexee), cuqal **Yokk caabi yi** ci barab bi;
   xoolal [Tànk bu caabi yi](#tànk-bu-caabi-yi).

**Windows**

1. Yebal programu samp bu Windows bi (`Fontes-Setup-….exe`) ci [sumb bu mujj bi](https://github.com/ykarapazar/fontes/releases/latest) te cuqal ñaari yoon.
   - Su Windows wonee "Windows protected your PC": cuqal **More info**, te **Run anyway**.
2. Cuqal **Samp**. Ab fenêtre dina ubbiwaat, te Fontes dina samp.
3. Bu ñu la laajee ndax mu yónne limu jëfandikoo yu amul tur, bësal Enter ngir wax déedéet.
4. Dafay laaj ndax mu yokk caabi yi léegi. Bësal Enter ngir bàyyi ko; xoolal [Tànk bu caabi yi](#tànk-bu-caabi-yi).
5. Bu waxee **Jeex na.**, ubbiwaatal say aplikasioŋ AI. Su benn ci ñoom a ngi doxagum, tëjal ko ba mu
   jeex (ci barra bu sistem bi itam, ci wetu montar bi) te ubbiwaat ko.

Ci mujj gi, programu samp bi dafay lim aplikasioŋ yi mu samp.

### Ban aplikasioŋ lay samp

Dafay samp ab aplikasioŋ rekk su kàggu réglage bu aplikasioŋ boobu nekk ba noppi ci sa ordinatëer. Claude
Code, su `~/.claude.json` nekkee rekk lañu koy samp. Claude Desktop, saa su ne lañu koy samp. Bépp
aplikasioŋ dafay am benn xaaj, `fontes`, ci fichier bii:

| Aplikasioŋ | Fichier (Mac ak Linux) | Fichier (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, ak kopi bu sumb bu Microsoft Store ci boppam |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, walla `~/.codeium/windsurf/mcp_config.json` ci sumb yu yàgg | `%APPDATA%\devin\mcp_config.json`, walla `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code, su `~/.copilot` walla kàggu réglage bu VS Code ci boppam nekkee lañu koy samp.

Ñaari aplikasioŋ soxla nañu beneen tànk:

- **Windsurf:** ginnaaw bi nga ko ubbiwaatee, bësal refresh ci Cascade.
- **Cline ci biir extension VS Code bu yàgg bi:** yokkal Fontes ak loxo (xoolal [Cline](#yeneen-aplikasioŋ)).

### Tànk bu caabi yi

Ci saa si ginnaaw samp bi, programu samp bi dafay la laaj ndax mu yokk caabi yu Faraas ak yu Etaa-Sini yu
ñu joxe ci neen. Ngir yokk walla soppi leen ginnaaw:

- **Mac:** ubbiwaatal **Fontes Installer** te tànn **Yokk walla soppi caabi yi**.
- **Windows:** ubbil **Start** menu, te cuqal **Fontes** → **Yokk walla soppi caabi yi**.

Li ngay bind dafa nëbbu. Caabi yi dañuy dugg ci bépp aplikasioŋ bu am Fontes ba noppi. Tëjal aplikasioŋ yi
ba ñu jeex te ubbiwaat leen ginnaaw loolu. Fu ñuy jële caabi yi ak lan lañuy ubbi: [KEYS.md](KEYS.md).

### Kopi yu ñu denc, doxalaat ak dindi

Programu samp bi xaaju `fontes` bi rekk lay soppi. Yeneen réglage yépp ak commentaire yépp dañuy des ni
ñu meloon. Balaa muy soppi ab fichier, dafay denc ab kopi ci wetam, bu tudd `<file>.fontes-backup-<date>`.
Kopi yi ñu def ginnaaw bi nga yokkee caabi yi am nañu caabi yooyu: faral yi nga soxlaatul. Dafay samp uv
itam. Doxalaat ko amul benn loraange: dafay defar samp bi te du soppi leneen.

Ngir dindi Fontes, ubbil **Fontes Installer** te tànn **Dindi** (Mac), walla dindi **Fontes** ci Settings → Apps (Windows). Dafay dindi xaaju `fontes` bi, ak caabi yi, ci bépp aplikasioŋ. Say
yeneen réglage ak kopi yi ñu denc dañuy des.

## Yeesal yi

- **Programu samp bi ak fichier `.mcpb` bi:** soxlaa nga def dara. Benn yoon ci bés bi, bu aplikasioŋ bi
  tàmbalee, Fontes dafay saytu ci ginnaaw ndax am na sumb bu gën a bees te waajal ko; bu aplikasioŋ bi
  tàmbaliwaatee dafay ko jëfandikoo. Su ñu mënul a yeb ab yeesal walla mu doxul, Fontes dafay wéy di
  jëfandikoo sumb bi doxoon.
- **`uvx`:** Fontes dafay la wax bu sumb bu gën a bees amee, ci kaw limu juridiction yi. Ngir saa su
  ne doxal sumb bu gën a bees bi, jëfandikool `fontes-mcp@latest` ci barabu `fontes-mcp`.

Benn xibaar ci yaw walla ci say gëstu du dem fenn ngir lii.

## Sutura

Fontes du yónne dara ci yaw walla ci say gëstu ci njëlbéen. Limu jëfandikoo yi, su nga nangoo rekk (opt-in),
te yégle njuumte du dem lu dul ginnaaw bi nga ko gisee te dëggal ko. Leeral yi: [PRIVACY.md](PRIVACY.md).

## Dindi ko

Dindil xaaju `fontes` bi ci réglage MCP yu sa aplikasioŋ (ci Claude Code:
`claude mcp remove fontes`), te nga tëj aplikasioŋ bi ba mu jeex te ubbiwaat ko.

## Li baax nga xam

Fontes dafay jàng ay cosaan yu ñépp mën a gis, li ëpp ci ñoom ay sit internet yu àttekaay ak yu Nguur gi.
Dafay rëdd ci ay tontoom cosaan yi dul yu Nguur gi. Saa su ne ubbil lëkkalekaayu cosaan bi balaa ngay
wóolu ab àtte walla ab xaaju yoon.

Su dara baaxul, bindal li nga def ak njuumte li nga gis ci fontesmcp@proton.me.

## Balaa ngay wóolu ko

- Fontes ab jumtukaayu gëstu la, du ndigal ci yoon. Jëfandikoo ko du def kenn sa layookat.
- Ni mu mel lañu koy joxe ("as is"), te amul benn garanti, te ñi ko bind tegguñu dara ci ni ñu koy
  jëfandikoo, ci li yoon may. Sàrt yi yépp ñu ngi ci [licence](../../../LICENSE) bi (Apache 2.0).
