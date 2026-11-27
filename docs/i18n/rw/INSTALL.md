> Iyi ni inyandiko yahinduwe hifashishijwe imashini. Inyandiko y'Icyongereza ni yo ifite agaciro.

# Gushyiraho Fontes

Fontes ituma porogaramu yawe ya AI ishakisha ibyemezo by'inkiko n'amategeko ako kanya ku mbuga z'inkiko
n'iza Leta mu mafasi y'ubutabera 125. Buri gisubizo gifite ihuza rijya ku nyandiko y'umwimerere.
Ni seriveri MCP isanzwe, bityo ikora muri porogaramu iyo ari yo yose ishobora gukoresha seriveri MCP iri
kuri mudasobwa: Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Gemini CLI,
Windsurf, Zed, LM Studio, Cline n'izindi.

Hitamo porogaramu yawe, ukurikize intambwe zayo, hanyuma [ugenzure ko ikora](#genzura-ko-ikora).

## Claude Desktop

1. Kuramo dosiye `.mcpb` ya Fontes muri
   [verisiyo iheruka](https://github.com/ykarapazar/fontes/releases/latest).
2. Uyikandeho kabiri. Claude Desktop irayifungura.
3. Kanda **Install**.

## Codex

Muri terminal:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI na extension ya Codex ya IDE bisangira iri genamiterere (`~/.codex/config.toml`).
Ukeneye [uv](#ukeneye-uv).

## Claude Code

Muri terminal:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Ukeneye [uv](#ukeneye-uv).

## Izindi porogaramu

Buri imwe muri izi ikenera [uv](#ukeneye-uv). Ongeraho icyanditswe, ubike, hanyuma ufunge porogaramu
burundu wongere uyifungure.

**Cursor:** muri `~/.cursor/mcp.json` (imishinga yose) cyangwa `.cursor/mcp.json` (umushinga umwe):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** koresha **MCP: Add Server** muri Command Palette, uhitemo
**Command (stdio)**, wandike `uvx fontes-mcp` hanyuma wite seriveri `fontes`. Cyangwa wongere ibi muri
`~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Imiterere ya kera ya VS Code ikoresha `.vscode/mcp.json`, aho urufunguzo rwo hejuru ari `servers` aho
kuba `mcpServers`.

**Gemini CLI:** muri terminal, `gemini mcp add -s user fontes uvx fontes-mcp`. Cyangwa wongere ibi muri
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** fungura dosiye y'igenamiterere ryawe (**zed: open settings file**) wongeremo:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** mu ruhande rw'iburyo, fungura tab **Program**, ukande **Install → Edit
mcp.json**, wongeremo:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** kanda ikimenyetso **MCP Servers**, fungura tab **Configure**, ukande **Configure MCP
Servers**, wongeremo icyanditswe cya `mcpServers` kimwe n'icya LM Studio.

**Claude Desktop, n'intoki** (aho gukoresha dosiye `.mcpb`): ongeraho icyanditswe cya `mcpServers`
kimwe muri `claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Indi porogaramu ya MCP iyo ari yo yose** (Windsurf n'izindi): inyandiko zayo bwite zivuga aho ibika
seriveri zayo za MCP. Nyinshi zemera icyanditswe kimwe: command `uvx`, argument `fontes-mcp`.

Niba porogaramu itabona `uvx`, koresha inzira yayo yuzuye (kuri macOS na Linux, `which uvx` irayigaragaza).

## Ukeneye uv

Codex, Claude Code n'izindi porogaramu zitangiza Fontes ukoresheje `uvx`, iza hamwe na **uv**, igikoresho
gito cy'ubuntu cya Astral. Kugira ngo uyishyireho, reba
[ubuyobozi bwa Astral](https://docs.astral.sh/uv/getting-started/installation/), cyangwa ukore:

- macOS cyangwa Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Imfunguzo

Inkomoko zimwe zikenera urufunguzo rw'ubuntu: reba [KEYS.md](KEYS.md).

## Genzura ko ikora

Mu kiganiro gishya, baza: *"Ni ayahe mafasi y'ubutabera Fontes ishobora gushakishamo?"* Porogaramu
igomba gusubiza itanga urutonde rw'ibihugu. Niba itabikoze, yifunge burundu wongere uyifungure indi
nshuro imwe.

## Porogaramu yo gushyiraho ukanze rimwe (Mac na Windows)

Porogaramu yo gushyiraho ishyira Fontes muri porogaramu zawe zose icyarimwe: Claude Desktop,
Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio na Cline.

**Mbere yo gutangira:** funga burundu buri porogaramu muri izi. Ibi ni ingenzi cyane kuri Claude Code:
iyo ikora, yongera kwandika `~/.claude.json` kandi ishobora gusiba impinduka porogaramu yo gushyiraho
yakoze. Niba udashobora gufunga Claude Code, yongereho Fontes ukoresheje `claude mcp add` aho kubikora
utyo (reba [Claude Code](#claude-code)).

**Mac**

1. Kuramo porogaramu yo gushyiraho ya Mac (`Fontes-Installer-…-mac.zip`) muri [verisiyo iheruka
   gusohoka](https://github.com/ykarapazar/fontes/releases/latest) hanyuma uyikandeho kabiri kugira
   ngo uyifungure.
2. Kanda kabiri kuri **Fontes Installer**. Niba Mac yawe ikubajije niba ushaka gufungura porogaramu
   yakuwe kuri internet, kanda **Open**.
3. Hitamo **Shyiraho** hanyuma ukande **OK**. Gushyiraho bifata nk'umunota umwe.
4. Ubutumwa bugaragaza porogaramu yashyizemo Fontes. Kanda **Byarangiye**, hanyuma wongere ufungure
   izo porogaramu. Niba ushaka kubanza kongeraho imfunguzo z'ubuntu zitari itegeko, ahubwo kanda
   **Ongeraho imfunguzo**; reba [Intambwe y'imfunguzo](#intambwe-yimfunguzo).

**Windows**

1. Kuramo porogaramu yo gushyiraho ya Windows (`Fontes-Setup-….exe`) muri [verisiyo iheruka gusohoka](https://github.com/ykarapazar/fontes/releases/latest) hanyuma uyikandeho kabiri.
   - Niba Windows yerekanye "Windows protected your PC": kanda **More info**, hanyuma **Run anyway**.
2. Kanda **Shyiraho**. Hazagaragara idirishya rishyiraho Fontes.
3. Nibakubaza niba yakohereza imibare y'ikoreshwa itagaragaza nyirayo, kanda Enter kugira ngo uvuge oya.
4. Irabaza niba yakongeraho imfunguzo ubu. Kanda Enter kugira ngo usimbuke; reba
   [Intambwe y'imfunguzo](#intambwe-yimfunguzo).
5. Nivuga **Byarangiye.**, ongera ufungure porogaramu zawe za AI. Niba imwe yari igikora, yifunge burundu
   (no muri system tray, hafi y'isaha) wongere uyifungure.

Ku iherezo, porogaramu yo gushyiraho itanga urutonde rwa porogaramu yashyizemo Fontes.

### Porogaramu ishyiramo

Ishyira Fontes muri porogaramu gusa iyo ububiko bw'igenamiterere bw'iyo porogaramu busanzwe buri kuri
mudasobwa yawe. Claude Code ishyirwamo gusa iyo `~/.claude.json` ihari. Claude Desktop ihora ishyirwamo.
Buri porogaramu ibona icyanditswe kimwe, `fontes`, muri iyi dosiye:

| Porogaramu | Dosiye (Mac na Linux) | Dosiye (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, na kopi yihariye ya verisiyo ya Microsoft Store |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, cyangwa `~/.codeium/windsurf/mcp_config.json` kuri verisiyo za kera | `%APPDATA%\devin\mcp_config.json`, cyangwa `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code ishyirwamo iyo `~/.copilot` cyangwa ububiko bw'igenamiterere bwa VS Code ubwayo buhari.

Porogaramu ebyiri zikenera indi ntambwe imwe:

- **Windsurf:** nyuma yo kuyongera gufungura, kanda refresh muri Cascade.
- **Cline iri muri extension ya kera ya VS Code:** ongeramo Fontes n'intoki (reba [Cline](#izindi-porogaramu)).

### Intambwe y'imfunguzo

Ako kanya nyuma yo gushyiraho, porogaramu yo gushyiraho igusaba niba yakongeraho imfunguzo z'ubuntu z'u
Bufaransa n'iza Leta Zunze Ubumwe za Amerika. Kugira ngo uzongereho cyangwa uzihindure nyuma:

- **Mac:** ongera ufungure **Fontes Installer** uhitemo **Ongeraho cyangwa uhindure imfunguzo**.
- **Windows:** fungura menu ya Start, hanyuma uhitemo **Fontes** → **Ongeraho cyangwa uhindure imfunguzo**.

Ibyo wandika ntibigaragara. Imfunguzo zijya muri buri porogaramu isanzwe ifite Fontes. Nyuma yaho, funga
porogaramu burundu wongere uzifungure. Aho wabona imfunguzo n'icyo zifungura: [KEYS.md](KEYS.md).

### Kopi z'ububiko, kongera kuyikoresha no kuyikuraho

Porogaramu yo gushyiraho ihindura gusa icyanditswe cya `fontes`. Irindi genamiterere ryose n'ibisobanuro
(comments) byose bigumaho uko byari biri. Mbere yo guhindura dosiye, ibika kopi yayo iruhande rwayo,
yitwa `<file>.fontes-backup-<date>`. Kopi zakozwe nyuma y'uko wongeyeho imfunguzo zirimo izo mfunguzo:
siba izo utagikeneye. Inashyiraho uv. Kongera kuyikoresha nta kibazo biteza: ikosora ibyashyizweho kandi
ntigire ikindi ihindura.

Kugira ngo ukureho Fontes, fungura **Fontes Installer** uhitemo **Kuraho** (Mac), cyangwa ukureho **Fontes** muri Settings → Apps (Windows). Ikuraho icyanditswe cya `fontes`, imfunguzo zirimo, muri buri
porogaramu. Irindi genamiterere ryawe na kopi z'ububiko bigumaho.

## Ivugurura

- **Porogaramu yo gushyiraho na dosiye `.mcpb`:** nta cyo ukeneye gukora. Rimwe ku munsi, iyo porogaramu
  itangiye, Fontes igenzura mu buryo butagaragara niba hari verisiyo nshya ikayitegura; ubutaha porogaramu
  itangiye irayikoresha. Niba ivugurura ridashobora gukurwamo cyangwa ritakora, Fontes ikomeza gukoresha
  verisiyo yakoraga.
- **`uvx`:** Fontes ikubwira iyo hari verisiyo nshya, hejuru y'urutonde rwayo rw'amafasi y'ubutabera.
  Kugira ngo uhore ukoresha verisiyo nshya kurusha izindi, koresha `fontes-mcp@latest` mu mwanya wa `fontes-mcp`.

Nta makuru akwerekeyeho cyangwa yerekeye ibyo ushakisha yoherezwa ahantu na hamwe kubera ibi.

## Ubuzima bwite

Fontes ntiyohereza ikintu na kimwe kikwerekeyeho cyangwa cyerekeye ibyo ushakisha mu buryo busanzwe.
Imibare y'ikoreshwa ni ku bushake bwawe (opt-in), kandi raporo y'ikosa yoherezwa gusa umaze kuyibona no
kuyemeza. Ibisobanuro: [PRIVACY.md](PRIVACY.md).

## Kuyikuraho

Kuraho icyanditswe cya `fontes` mu igenamiterere rya MCP rya porogaramu yawe (muri Claude Code:
`claude mcp remove fontes`), hanyuma ufunge porogaramu burundu wongere uyifungure.

## Ibyiza kumenya

Fontes isoma inkomoko rusange, inyinshi zikaba imbuga z'inkiko n'iza Leta. Mu bisubizo byayo igaragaza
izitari iza Leta. Buri gihe fungura ihuza ry'inkomoko mbere yo gushingira ku cyemezo cyangwa ku ngingo.

Niba hari ikitagenze neza, andikira fontesmcp@proton.me uvuge icyo wakoze n'ikosa wabonye.

## Mbere yo kuyizera

- Fontes ni igikoresho cy'ubushakashatsi, si inama mu by'amategeko. Kuyikoresha ntibigira umuntu uwo ari
  we wese umunyamategeko wawe.
- Itangwa "uko iri" ("as is"), nta garanti, kandi abayikoze ntibaryozwa uko ikoreshwa, mu rugero amategeko
  yemera. Amabwiriza yose ari mu [ruhushya](../../../LICENSE) (Apache 2.0).
