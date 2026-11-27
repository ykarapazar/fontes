> Bu terjime maşynyň kömegi bilen taýýarlandy. Iňlis dilindäki görnüşi esasy hasaplanýar.

# Fontes programmasyny gurnamak

Fontes AI programmaňyza 125 ýurisdiksiýada kazyýet çözgütlerini we kanunçylygy
kazyýet we döwlet saýtlarynda göni gözlemäge mümkinçilik berýär. Her netije asyl nusga
salgylanýar. Ol adaty MCP serweri, şonuň üçin ýerli MCP serweri işledip bilýän islendik
programmada işleýär: Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot),
Gemini CLI, Windsurf, Zed, LM Studio, Cline we beýlekiler.

Programmaňyzy saýlaň, onuň ädimlerini ýerine ýetiriň, soňra
[işleýändigini barlaň](#işleýändigini-barlamak).

## Claude Desktop

1. Fontes `.mcpb` faýlyny [iň soňky çykarylyşdan](https://github.com/ykarapazar/fontes/releases/latest)
   ýükläň.
2. Oňa iki gezek basyň. Claude Desktop ony açar.
3. **Install** basyň.

## Codex

Terminalda:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI we Codex IDE giňeltmesi bu sazlamany bilelikde ulanýar (`~/.codex/config.toml`).
Size [uv](#uv-gerek) gerek.

## Claude Code

Terminalda:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Size [uv](#uv-gerek) gerek.

## Beýleki programmalar

Bularyň her birine [uv](#uv-gerek) gerek. Ýazgyny goşuň, ýatda saklaň, soňra programmany
ýapyň we täzeden açyň.

**Cursor:** `~/.cursor/mcp.json` (ähli taslamalar) ýa-da `.cursor/mcp.json` (bir taslama)
faýlynda:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** Command Palette-den **MCP: Add Server** işlediň,
**Command (stdio)** saýlaň, `uvx fontes-mcp` giriziň we serwere `fontes` adyny beriň. Ýa-da muny
`~/.copilot/mcp-config.json` faýlyna goşuň:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Köne VS Code sazlamalary `.vscode/mcp.json` faýlyny ulanýar, onda ýokarky derejedäki açar
`mcpServers` däl-de, `servers` bolýar.

**Gemini CLI:** terminalda `gemini mcp add -s user fontes uvx fontes-mcp`. Ýa-da muny
`~/.gemini/settings.json` faýlyna goşuň:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** sazlamalar faýlyňyzy açyň (**zed: open settings file**) we goşuň:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** sag gapdal panelde **Program** goýmasyny açyň, **Install → Edit mcp.json**
basyň we goşuň:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** **MCP Servers** nyşanyna basyň, **Configure** goýmasyny açyň, **Configure MCP
Servers** basyň we LM Studio üçin bolşy ýaly şol bir `mcpServers` ýazgysyny goşuň.

**Claude Desktop, el bilen** (`.mcpb` faýlynyň ýerine): şol bir `mcpServers` ýazgysyny
`claude_desktop_config.json` faýlyna goşuň (macOS: `~/Library/Application Support/Claude/`,
Windows: `%APPDATA%\Claude\`).

**Islendik beýleki MCP programmasy** (Windsurf we beýlekiler): onuň öz resminamalarynda MCP
serwerleriniň nirede saklanýandygy aýdylýar. Köpüsi şol bir ýazgyny kabul edýär: buýruk `uvx`,
argument `fontes-mcp`.

Eger programma `uvx` tapyp bilmese, onuň doly ýoluny ulanyň (macOS we Linux-da `which uvx` ony
görkezýär).

## uv gerek

Codex, Claude Code we beýleki programmalar Fontes-i `uvx` bilen işe girizýär, ol bolsa Astral
kompaniýasynyň kiçi mugt guraly bolan **uv** bilen bile gelýär. Ony gurnamak üçin
[Astral-yň gollanmasyna](https://docs.astral.sh/uv/getting-started/installation/) serediň
ýa-da işlediň:

- macOS ýa-da Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Açarlar

Käbir çeşmelere mugt açar gerek: [KEYS.md](KEYS.md) serediň.

## Işleýändigini barlamak

Täze söhbetdeşlikde soraň: *“Fontes haýsy ýurisdiksiýalarda gözläp bilýär?”* Programma ýurtlaryň
sanawy bilen jogap bermeli. Eger bermese, programmany ýene bir gezek ýapyň we täzeden açyň.

## Bir basyşda gurnaýjy (Mac we Windows)

Gurnaýjy Fontes-i ähli programmalaryňyzda birbada sazlaýar: Claude Desktop, Codex,
Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio we Cline.

**Başlamazdan öň:** bu programmalaryň her birini doly ýapyň. Bu iň köp Claude Code üçin möhüm:
ol işläp durka `~/.claude.json` faýlyny täzeden ýazýar we gurnaýjynyň üýtgetmesini yzyna
gaýtaryp biler. Eger Claude Code-y ýapyp bilmeseňiz, onuň ýerine Fontes-i oňa `claude mcp add`
bilen goşuň ([Claude Code](#claude-code) serediň).

**Mac**

1. Mac üçin gurnaýjyny (`Fontes-Installer-…-mac.zip`)
   [iň soňky neşirden](https://github.com/ykarapazar/fontes/releases/latest) ýükläň we arhiwi
   açmak üçin oňa iki gezek basyň.
2. **Fontes Installer** programmasyna iki gezek basyň. Eger Mac kompýuteriňiz internetden ýüklenen
   programmany açmalydygyny sorasa, **Open** basyň.
3. **Gurnamak** saýlaň we **OK** basyň. Sazlamak takmynan bir minut alýar.
4. Habar sazlanan programmalaryň sanawyny görkezýär. **Taýýar** basyň, soňra şol programmalary
   täzeden açyň. Ilki islege bagly mugt açarlary goşmak üçin, onuň ýerine **Açarlary goş**
   basyň; [Açarlar ädimi](#açarlar-ädimi) serediň.

**Windows**

1. Windows gurnaýjysyny (`Fontes-Setup-….exe`) [iň soňky neşirden](https://github.com/ykarapazar/fontes/releases/latest) ýükläp, iki gezek basyň.
   - Eger Windows “Windows protected your PC” diýip görkezse: **More info**, soňra
     **Run anyway** basyň.
2. **Gurnamak** basyň. Penjire açylyp, Fontes-i sazlaýar.
3. Anonim ulanyş sanlaryny ibermelidigi soralanda, “ýok” üçin Enter düwmesine basyň.
4. Ol açarlary häzir goşmalydygyny soraýar. Geçmek üçin Enter düwmesine basyň;
   [Açarlar ädimi](#açarlar-ädimi) serediň.
5. **Taýýar** diýende, AI programmalaryňyzy täzeden açyň. Eger olaryň biri entek işleýän
   bolsa, ony doly ýapyň (ulgam tagtasyndan, sagadyň ýanyndan hem) we täzeden açyň.

Ahyrynda gurnaýjy sazlan programmalarynyň sanawyny görkezýär.

### Haýsy programmalary sazlaýar

Ol programmany diňe şol programmanyň sazlamalar bukjasy kompýuteriňizde eýýäm bar bolsa
sazlaýar. Claude Code diňe `~/.claude.json` bar bolsa sazlanýar. Claude Desktop hemişe
sazlanýar. Her programma şu faýlda bir ýazgy, `fontes`, alýar:

| Programma | Faýl (Mac we Linux) | Faýl (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json` we Microsoft Store wersiýasynyň öz nusgasy |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json` ýa-da köne wersiýalarda `~/.codeium/windsurf/mcp_config.json` | `%APPDATA%\devin\mcp_config.json` ýa-da `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code `~/.copilot` ýa-da VS Code-yň öz sazlamalar bukjasy bar bolsa sazlanýar.

Iki programma üçin ýene bir ädim gerek:

- **Windsurf:** ony täzeden açandan soň, Cascade-de täzelemek düwmesine basyň.
- **Köne VS Code giňeltmesiniň içindäki Cline:** Fontes-i el bilen goşuň
  ([Cline](#beýleki-programmalar) serediň).

### Açarlar ädimi

Gurnalandan dessine soň gurnaýjy Fransiýa we ABŞ üçin mugt açarlary goşmagy teklip edýär.
Olary soňra goşmak ýa-da üýtgetmek üçin:

- **Mac:** **Fontes Installer** programmasyny täzeden açyň we **Açarlary goş ýa-da üýtget** saýlaň.
- **Windows:** Start menýusyny açyň, soňra **Fontes** → **Açarlary goş ýa-da üýtget**-i saýlaň.

Ýazylýan tekst gizlin bolýar. Açarlar Fontes eýýäm bar bolan her programma girizilýär. Soňra
programmalary ýapyň we täzeden açyň. Açarlary nireden almaly we olaryň näme açýandygy:
[KEYS.md](KEYS.md).

### Ätiýaçlyk nusgalar, gaýtadan işletmek we aýyrmak

Gurnaýjy diňe `fontes` ýazgysyny üýtgedýär. Beýleki ähli sazlamalar we teswirler öňküligine
galýar. Faýly üýtgetmezden öň, ol onuň ýanynda `<file>.fontes-backup-<date>` atly nusgasyny
saklaýar. Açarlary goşanyňyzdan soň döredilen nusgalarda şol açarlar bolýar: indi gerek
bolmadyklaryny pozuň. Ol uv-ni hem gurnaýar. Ony gaýtadan işletmek howpsuz: ol sazlamany
düzedýär we başga hiç zady üýtgetmeýär.

Fontes-i aýyrmak üçin **Fontes Installer** programmasyny açyň we **Aýyrmak** saýlaň (Mac) ýa-da **Fontes**-i Sazlamalar → Programmalar (Windows) bölümünden aýyryň. Ol `fontes` ýazgysyny, açarlar bilen
bilelikde, ähli programmalardan aýyrýar. Beýleki sazlamalaryňyz we ätiýaçlyk nusgalar galýar.

## Täzelenmeler

- **Gurnaýjy we `.mcpb` faýly:** hiç zat etmegiňiz gerek däl. Günde bir gezek, programma
  açylanda, Fontes fonda täze wersiýany barlaýar we ony taýýarlaýar; programma indiki gezek
  açylanda şony ulanýar. Eger täzelenmäni ýükläp bolmasa ýa-da ol işlemese, Fontes işlän
  wersiýany ulanmagyny dowam etdirýär.
- **`uvx`:** täze wersiýa bar bolanda, Fontes muny ýurisdiksiýalar sanawynyň ýokarsynda
  aýdýar. Hemişe iň täze wersiýany işletmek üçin `fontes-mcp` ýerine `fontes-mcp@latest` ulanyň.

Munuň üçin siz ýa-da gözlegleriňiz barada hiç hili maglumat hiç ýere iberilmeýär.

## Gizlinlik

Fontes adaty ýagdaýda siz ýa-da gözlegleriňiz barada hiç zat ibermeýär. Ulanyş sanlary diňe
siziň razylygyňyz bilen iberilýär, ýalňyşlyk hasabaty bolsa diňe siz ony görüp tassyklanyňyzdan
soň iberilýär. Jikme-jiklikler: [PRIVACY.md](PRIVACY.md).

## Aýyrmak

`fontes` ýazgysyny programmaňyzyň MCP sazlamalaryndan aýyryň (Claude Code-da:
`claude mcp remove fontes`), soňra programmany ýapyň we täzeden açyň.

## Bilmek peýdaly

Fontes açyk çeşmeleri, esasan kazyýet we döwlet saýtlaryny okaýar. Ol resmi däl çeşmeleri öz
jogaplarynda belleýär. Kazyýet çözgüdine ýa-da madda daýanmazdan öň, hemişe çeşme salgylanmasyny
açyň.

Eger bir zat nädogry bolsa, näme edendigiňizi we gören ýalňyşlygyňyzy fontesmcp@proton.me
salgysyna iberiň.

## Daýanmazdan öň

- Fontes barlag guraly, hukuk maslahaty däl. Ony ulanmak hiç kimi siziň aklawçyňyz
  etmeýär.
- Ol “bolşy ýaly” (“as is”), hiç hili kepilliksiz berilýär we kanunyň rugsat berýän derejesinde
  onuň awtorlary onuň nähili ulanylýandygy üçin jogapkär däl. Doly şertler
  [lisenziýada](../../../LICENSE) (Apache 2.0).
