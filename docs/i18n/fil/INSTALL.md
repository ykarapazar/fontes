> Ito ay salin na ginawa sa tulong ng makina. Ang bersyong Ingles ang may bisa.

# Pag-install ng Fontes

Binibigyang-daan ng Fontes ang iyong AI app na maghanap ng mga desisyon ng korte at lehislasyon nang live sa
mga website ng mga korte at ng pamahalaan sa mahigit 120 hurisdiksyon. Bawat resulta ay may link sa orihinal
na dokumento. Ito ay isang karaniwang MCP server, kaya gumagana ito sa anumang app na kayang magpatakbo ng
lokal na MCP server: Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Gemini CLI,
Windsurf, Zed, LM Studio, Cline at iba pa.

Piliin ang iyong app, sundin ang mga hakbang nito, at saka [tingnan kung gumagana ito](#pagtingin-kung-gumagana-ito).

## Claude Desktop

1. I-download ang `.mcpb` file ng Fontes mula sa
   [pinakabagong release](https://github.com/ykarapazar/fontes/releases/latest).
2. I-double click ito. Bubuksan ito ng Claude Desktop.
3. I-click ang **Install**.

## Codex

Sa isang terminal:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Pinagsasaluhan ng Codex CLI at ng Codex IDE extension ang setting na ito (`~/.codex/config.toml`).
Kailangan mo ng [uv](#kailangan-mo-ng-uv).

## Claude Code

Sa isang terminal:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Kailangan mo ng [uv](#kailangan-mo-ng-uv).

## Iba pang mga app

Kailangan ng bawat isa sa mga ito ang [uv](#kailangan-mo-ng-uv). Idagdag ang entry, i-save, at saka isara at
buksang muli ang app.

**Cursor:** sa `~/.cursor/mcp.json` (lahat ng proyekto) o `.cursor/mcp.json` (isang proyekto):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** patakbuhin ang **MCP: Add Server** mula sa Command Palette, piliin ang
**Command (stdio)**, ilagay ang `uvx fontes-mcp` at pangalanan ang server na `fontes`. O idagdag ito sa
`~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Gumagamit ang mga mas lumang setup ng VS Code ng `.vscode/mcp.json`, na may top-level na key na `servers`
sa halip na `mcpServers`.

**Gemini CLI:** sa isang terminal, `gemini mcp add -s user fontes uvx fontes-mcp`. O idagdag ito sa
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** buksan ang iyong settings file (**zed: open settings file**) at idagdag:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** sa sidebar sa kanan, buksan ang tab na **Program**, i-click ang **Install → Edit
mcp.json**, at idagdag:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** i-click ang icon na **MCP Servers**, buksan ang tab na **Configure**, i-click ang **Configure MCP
Servers**, at idagdag ang parehong `mcpServers` entry tulad ng sa LM Studio.

**Claude Desktop, nang mano-mano** (sa halip na ang `.mcpb` file): idagdag ang parehong `mcpServers` entry sa
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Anumang ibang MCP app** (Windsurf at iba pa): sinasabi ng sarili nitong dokumentasyon kung saan nito
iniimbak ang mga MCP server nito. Tinatanggap ng karamihan ang parehong entry: command na `uvx`, argument na
`fontes`.

Kung hindi mahanap ng app ang `uvx`, gamitin ang buong path nito (sa macOS at Linux, ipinapakita ito ng
`which uvx`).

## Kailangan mo ng uv

Sinisimulan ng Codex, Claude Code at ng iba pang mga app ang Fontes gamit ang `uvx`, na kasama sa **uv**, isang
maliit at libreng tool mula sa Astral. Para i-install ito, tingnan ang
[gabay ng Astral](https://docs.astral.sh/uv/getting-started/installation/), o patakbuhin ang:

- macOS o Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Mga key

Kailangan ng ilang sanggunian ng libreng key: tingnan ang [KEYS.md](KEYS.md).

## Pagtingin kung gumagana ito

Sa isang bagong chat, itanong: *"Aling mga hurisdiksyon ang kayang hanapan ng Fontes?"* Dapat sumagot ang app
ng listahan ng mga bansa. Kung hindi, isara at buksang muli ang app nang isa pang beses.

## One-click installer (Mac at Windows)

Sine-set up ng installer ang Fontes sa lahat ng iyong app nang sabay-sabay: Claude Desktop,
Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio at Cline.

**Bago ka magsimula:** isara nang tuluyan ang bawat isa sa mga app na ito. Pinakamahalaga ito para sa Claude
Code: habang tumatakbo ito, isinusulat nitong muli ang `~/.claude.json` at maaaring mabura ang binago ng
installer. Kung hindi mo maisara ang Claude Code, idagdag ang Fontes dito gamit ang `claude mcp add`
(tingnan ang [Claude Code](#claude-code)).

**Mac**

1. I-download ang installer para sa Mac (`Fontes-Installer-…-mac.zip`) mula sa
   [pinakabagong release](https://github.com/ykarapazar/fontes/releases/latest) at i-double click ito
   para i-unzip.
2. I-double click ang **Fontes Installer**. Kung itanong ng iyong Mac kung bubuksan ang isang app na
   na-download mula sa internet, i-click ang **Open**.
3. Piliin ang **I-install** at i-click ang **OK**. Mga isang minuto ang pag-set up.
4. May mensaheng maglilista ng mga app na na-set up nito. I-click ang **Tapos na**, at saka buksang muli
   ang mga app na iyon. Para idagdag muna ang mga opsyonal na libreng key, i-click sa halip ang
   **Magdagdag ng mga key**; tingnan ang [Hakbang ng mga key](#hakbang-ng-mga-key).

**Windows**

1. I-download ang Windows installer (`Fontes-Setup-….exe`) mula sa
   [pinakabagong release](https://github.com/ykarapazar/fontes/releases/latest) at i-double click ito.
   - Kung ipinapakita ng Windows ang "Windows protected your PC": i-click ang **More info**, at saka
     **Run anyway**.
2. I-click ang **I-install**. Magbubukas ang isang window at ise-set up nito ang Fontes.
3. Kapag tinanong kung magpapadala ng anonymous na bilang ng paggamit, pindutin ang Enter para sa hindi.
4. Magtatanong ito kung idaragdag na ang mga key ngayon. Pindutin ang Enter para laktawan; tingnan ang
   [Hakbang ng mga key](#hakbang-ng-mga-key).
5. Kapag ipinakita nito ang **Tapos na**, buksang muli ang iyong mga AI app. Kung tumatakbo pa ang isa,
   isara ito nang tuluyan (pati sa system tray, malapit sa orasan) at buksan itong muli.

Sa dulo, inililista ng installer ang mga app na na-set up nito.

### Mga app na sine-set up nito

Sine-set up lamang nito ang isang app kung nasa computer mo na ang settings folder ng app na iyon. Sine-set
up lamang ang Claude Code kung umiiral ang `~/.claude.json`. Palaging sine-set up ang Claude Desktop.
Nakakakuha ang bawat app ng isang entry, `fontes`, sa file na ito:

| App | File (Mac at Linux) | File (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, at ang hiwalay na kopya ng bersyon sa Microsoft Store |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, o `~/.codeium/windsurf/mcp_config.json` sa mga mas lumang bersyon | `%APPDATA%\devin\mcp_config.json`, o `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

Sine-set up ang VS Code kung umiiral ang `~/.copilot` o ang sariling settings folder ng VS Code.

Dalawang app ang nangangailangan ng isa pang hakbang:

- **Windsurf:** pagkatapos itong buksang muli, pindutin ang refresh sa Cascade.
- **Cline sa loob ng mas lumang VS Code extension:** idagdag nang mano-mano ang Fontes (tingnan ang
  [Cline](#iba-pang-mga-app)).

### Hakbang ng mga key

Pagkatapos mismo ng pag-install, nag-aalok ang installer na idagdag ang mga libreng key para sa France at US.
Para idagdag o palitan ang mga ito sa ibang pagkakataon:

- **Mac:** buksang muli ang **Fontes Installer** at piliin ang **Magdagdag o magpalit ng mga key**.
- **Windows:** buksan ang Start menu, pagkatapos **Fontes** → **Add or change keys**.

Nakatago ang tina-type. Napupunta ang mga key sa bawat app na mayroon nang Fontes. Isara at buksang muli ang
mga app pagkatapos. Kung saan kukuha ng mga key at kung ano ang binubuksan ng mga ito: [KEYS.md](KEYS.md).

### Mga backup na kopya, muling pagpapatakbo at pag-alis

Ang `fontes` entry lamang ang binabago ng installer. Nananatili ang bawat iba pang setting at komento. Bago
nito baguhin ang isang file, nagse-save ito ng kopya sa tabi nito, na pinangalanang
`<file>.fontes-backup-<date>`. Naglalaman ng mga key ang mga kopyang ginawa pagkatapos mong magdagdag ng mga
key: burahin ang mga hindi mo na kailangan. Ini-install din nito ang uv. Ligtas itong patakbuhin muli:
inaayos nito ang setup at wala nang ibang binabago.

Para alisin ang Fontes, buksan ang **Fontes Installer** at piliin ang **Alisin** (Mac), o i-uninstall ang
**Fontes** sa Settings → Apps (Windows). Inaalis nito ang `fontes` entry, kasama ang mga key, mula sa bawat
app. Nananatili ang iba mo pang setting at ang mga backup na kopya.

## Mga update

- **Installer at `.mcpb` file:** wala kang kailangang gawin. Minsan sa isang araw, kapag nagsimula ang isang
  app, tumitingin ang Fontes sa background kung may mas bagong bersyon at inihahanda ito; sa susunod na
  pagsisimula ng app, ginagamit na nito iyon. Kung hindi ma-download o hindi gumana ang isang update,
  patuloy na ginagamit ng Fontes ang bersyong gumagana.
- **`uvx`:** sinasabi sa iyo ng Fontes kapag may mas bagong bersyon, sa itaas ng listahan nito ng mga
  hurisdiksyon. Para palaging patakbuhin ang pinakabago, gamitin ang `fontes-mcp@latest` sa halip na `fontes-mcp`.

Walang anumang impormasyon tungkol sa iyo o sa iyong mga paghahanap ang ipinapadala saanman para dito.

## Privacy

Walang ipinapadala ang Fontes tungkol sa iyo o sa iyong mga paghahanap bilang default. Opt-in ang bilang ng
paggamit, at ipinapadala lamang ang isang bug report pagkatapos mo itong makita at kumpirmahin. Mga detalye:
[PRIVACY.md](PRIVACY.md).

## Pag-alis nito

Alisin ang `fontes` entry mula sa mga MCP setting ng iyong app (sa Claude Code:
`claude mcp remove fontes`), at saka isara at buksang muli ang app.

## Dapat malaman

Nagbabasa ang Fontes ng mga pampublikong sanggunian, karamihan ay mga website ng korte at ng pamahalaan.
Minamarkahan nito sa mga sagot nito ang mga sanggunian na hindi opisyal. Palaging buksan ang link ng
sanggunian bago ka umasa sa isang desisyon o probisyon.

Kung may nagkaproblema, i-email sa fontesmcp@proton.me ang ginawa mo at ang error na nakita mo.

## Bago ka umasa rito

- Ang Fontes ay isang tool sa pananaliksik, hindi legal na payo. Ang paggamit nito ay hindi ginagawang
  abogado mo ang sinuman.
- Ibinibigay ito "as is", nang walang warranty, at hindi mananagot ang mga may-akda nito sa kung paano ito
  ginagamit, hanggang sa pinahihintulutan ng batas. Ang buong mga tuntunin ay nasa
  [lisensya](../../../LICENSE) (Apache 2.0).
