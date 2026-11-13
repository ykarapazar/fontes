> Ky është një përkthim i ndihmuar nga makina. Versioni në anglisht është ai që vlen.

# Instalimi i Fontes

Fontes i lejon aplikacionit tuaj të AI-së të kërkojë vendime gjyqësore dhe legjislacion
drejtpërdrejt në faqet e internetit të gjykatave dhe të institucioneve shtetërore në më shumë se 120
juridiksione. Çdo rezultat lidhet me origjinalin. Është një server standard MCP, prandaj funksionon
në çdo aplikacion që mund të nisë një server MCP lokal: Claude Desktop, Codex, Claude Code, Cursor,
VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio, Cline dhe të tjerë.

**Fontes nuk është ende në PyPI.** Hapat më poshtë funksionojnë sapo të dalë versioni i parë.

Zgjidhni aplikacionin tuaj, ndiqni hapat e tij, pastaj
[kontrolloni që funksionon](#kontrolli-që-funksionon).

## Claude Desktop

1. Shkarkoni skedarin `.mcpb` të Fontes nga
   [versioni më i fundit](https://github.com/ykarapazar/fontes/releases/latest).
2. Klikojeni dy herë. Claude Desktop e hap.
3. Klikoni **Install**.

## Codex

Në një terminal:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI dhe zgjerimi Codex për IDE e ndajnë këtë cilësim (`~/.codex/config.toml`).
Ju duhet [uv](#ju-duhet-uv).

## Claude Code

Në një terminal:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Ju duhet [uv](#ju-duhet-uv).

## Aplikacione të tjera

Secili prej tyre kërkon [uv](#ju-duhet-uv). Shtoni hyrjen, ruajeni, pastaj mbyllni dhe rihapni
aplikacionin.

**Cursor:** në `~/.cursor/mcp.json` (të gjitha projektet) ose `.cursor/mcp.json` (një projekt):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** ekzekutoni **MCP: Add Server** nga Command Palette, zgjidhni
**Command (stdio)**, shkruani `uvx fontes-mcp` dhe emërtojeni serverin `fontes`. Ose shtoni këtë në
`~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Konfigurimet më të vjetra të VS Code përdorin `.vscode/mcp.json`, ku çelësi i nivelit të parë është
`servers` në vend të `mcpServers`.

**Gemini CLI:** në një terminal, `gemini mcp add -s user fontes uvx fontes-mcp`. Ose shtoni këtë në
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** hapni skedarin e cilësimeve (**zed: open settings file**) dhe shtoni:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** në shiritin anësor në të djathtë, hapni skedën **Program**, klikoni **Install → Edit
mcp.json** dhe shtoni:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** klikoni ikonën **MCP Servers**, hapni skedën **Configure**, klikoni **Configure MCP
Servers** dhe shtoni të njëjtën hyrje `mcpServers` si për LM Studio.

**Claude Desktop, me dorë** (në vend të skedarit `.mcpb`): shtoni të njëjtën hyrje `mcpServers` në
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Çdo aplikacion tjetër MCP** (Windsurf dhe të tjerë): dokumentacioni i tij tregon ku i mban
serverat MCP. Shumica marrin të njëjtën hyrje: komanda `uvx`, argumenti `fontes`.

Nëse aplikacioni nuk e gjen `uvx`, përdorni shtegun e tij të plotë (në macOS dhe Linux e shfaq
`which uvx`).

## Ju duhet uv

Codex, Claude Code dhe aplikacionet e tjera e nisin Fontes me `uvx`, që vjen me **uv**, një mjet i
vogël falas nga Astral. Për ta instaluar, shihni
[udhëzuesin e Astral](https://docs.astral.sh/uv/getting-started/installation/), ose ekzekutoni:

- macOS ose Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Çelësat

Disa burime kërkojnë një çelës falas: shihni [KEYS.md](KEYS.md).

## Kontrolli që funksionon

Në një bisedë të re, pyesni: *"Në cilat juridiksione mund të kërkojë Fontes?"* Aplikacioni duhet
të përgjigjet me një listë vendesh. Nëse jo, mbylleni dhe rihapeni aplikacionin edhe një herë.

## Instaluesi me një klik (së shpejti)

Një instalues për Mac dhe Windows që e konfiguron Fontes në të gjitha aplikacionet tuaja njëherësh
është në rrugë. Ai konfiguron Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot),
Windsurf, Gemini CLI, Zed, LM Studio dhe Cline. Sapo të publikohet:

**Para se të filloni:** mbyllni plotësisht secilin nga këto aplikacione. Kjo ka më shumë rëndësi
për Claude Code: ndërsa punon, ai rishkruan `~/.claude.json` dhe mund ta zhbëjë ndryshimin e
instaluesit. Nëse nuk mund ta mbyllni Claude Code, shtojeni Fontes në të me `claude mcp add` (shihni
[Claude Code](#claude-code)).

**Mac**

1. Hapni dosjen e shkarkuar **Fontes Installer**.
2. Klikoni dy herë **Install Fontes.command**.
   - Nëse Mac-u juaj thotë se "nuk mund të hapet sepse është nga një zhvillues i paidentifikuar":
     klikoni me të djathtën (ose Control-klik) mbi skedarin, zgjidhni **Open**, pastaj sërish
     **Open**. Këtë e bëni vetëm një herë.
3. Hapet një dritare që pyet nëse të dërgohen numërime anonime të përdorimit; shtypni Enter për
   jo.
4. Pyet nëse të shtohen çelësat tani. Shtypni Enter për ta anashkaluar; shihni
   [Hapi i çelësave](#hapi-i-çelësave).
5. Kur të shfaqet **Done**, hapni sërish aplikacionet tuaja të AI-së.

**Windows**

1. Shpaketoni **Fontes Installer** të shkarkuar (klik i djathtë → Extract All).
2. Klikoni dy herë **Install Fontes.cmd**.
   - Nëse Windows shfaq "Windows protected your PC": klikoni **More info**, pastaj **Run anyway**.
3. Kur pyetet nëse të dërgohen numërime anonime të përdorimit, shtypni Enter për jo.
4. Pyet nëse të shtohen çelësat tani. Shtypni Enter për ta anashkaluar; shihni
   [Hapi i çelësave](#hapi-i-çelësave).
5. Kur të shfaqet **Done**, hapni sërish aplikacionet tuaja të AI-së. Nëse ndonjëri ishte ende në
   punë, mbylleni plotësisht (edhe nga zona e njoftimeve, pranë orës) dhe hapeni sërish.

Në fund, instaluesi liston aplikacionet që konfiguroi.

### Cilat aplikacione konfiguron

Ai konfiguron një aplikacion vetëm nëse dosja e cilësimeve të atij aplikacioni ndodhet tashmë në
kompjuterin tuaj. Claude Code konfigurohet vetëm nëse ekziston `~/.claude.json`. Claude Desktop
konfigurohet gjithmonë. Çdo aplikacion merr një hyrje, `fontes`, në këtë skedar:

| Aplikacioni | Skedari (Mac dhe Linux) | Skedari (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, dhe kopja e veçantë e versionit nga Microsoft Store |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, ose `~/.codeium/windsurf/mcp_config.json` në versionet më të vjetra | `%APPDATA%\devin\mcp_config.json`, ose `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code konfigurohet nëse ekziston `~/.copilot` ose dosja e cilësimeve të vetë VS Code.

Dy aplikacione kërkojnë edhe një hap:

- **Windsurf:** pasi ta rihapni, shtypni rifreskimin në Cascade.
- **Cline brenda zgjerimit më të vjetër të VS Code:** shtojeni Fontes me dorë (shihni
  [Cline](#aplikacione-të-tjera)).

### Hapi i çelësave

Menjëherë pas instalimit, instaluesi ofron të shtojë çelësat falas për Francën dhe SHBA-në. Për t'i
shtuar ose ndryshuar më vonë:

- **Mac:** klikoni dy herë **Add or change keys.command** në dosjen e instaluesit, ose hapni sërish
  aplikacionin Fontes Installer dhe zgjidhni **Shto ose ndrysho çelësat**.
- **Windows:** klikoni dy herë **Add or change keys.cmd** në dosjen e instaluesit.

Shkrimi është i fshehur. Çelësat shkojnë në çdo aplikacion që e ka tashmë Fontes. Pas kësaj,
mbyllni dhe rihapni aplikacionet. Ku merren çelësat dhe çfarë hapin: [KEYS.md](KEYS.md).

### Kopjet rezervë, riekzekutimet dhe heqja

Instaluesi ndryshon vetëm hyrjen `fontes`. Çdo cilësim dhe koment tjetër mbetet siç ishte. Para se
të ndryshojë një skedar, ruan një kopje pranë tij, me emrin `<file>.fontes-backup-<date>`. Kopjet e
bëra pasi keni shtuar çelësa i përmbajnë ata çelësa: fshini ato që nuk ju duhen më. Ai instalon
gjithashtu uv. Riekzekutimi i tij është i sigurt: e riparon konfigurimin dhe nuk ndryshon asgjë
tjetër.

Për ta hequr Fontes, klikoni dy herë **Uninstall Fontes.command** (Mac) ose **Uninstall Fontes.cmd**
(Windows). Ai heq hyrjen `fontes`, bashkë me çelësat, nga çdo aplikacion. Cilësimet tuaja të tjera
dhe kopjet rezervë mbeten.

## Përditësimet

- **Instaluesi dhe skedari `.mcpb`:** nuk keni nevojë të bëni asgjë. Një herë në ditë, kur niset
  aplikacioni, Fontes kontrollon në sfond për një version më të ri dhe e përgatit; herën tjetër që
  niset aplikacioni, përdor atë. Nëse një përditësim nuk mund të shkarkohet ose nuk funksionon,
  Fontes vazhdon të përdorë versionin që funksionoi.
- **`uvx`:** Fontes ju njofton kur ka një version më të ri, në krye të listës së juridiksioneve. Për
  të ekzekutuar gjithmonë versionin më të ri, përdorni `fontes-mcp@latest` në vend të `fontes-mcp`.

Për këtë nuk dërgohet askund asnjë informacion për ju ose kërkimet tuaja.

## Privatësia

Si parazgjedhje Fontes nuk dërgon asgjë për ju ose kërkimet tuaja. Numërimet e përdorimit bëhen
vetëm me pëlqimin tuaj (opt-in), dhe një raport gabimi dërgohet vetëm pasi ta keni parë dhe
konfirmuar. Hollësi: [PRIVACY.md](PRIVACY.md).

## Heqja

Hiqni hyrjen `fontes` nga cilësimet MCP të aplikacionit tuaj (në Claude Code:
`claude mcp remove fontes`), pastaj mbyllni dhe rihapni aplikacionin.

## Mirë të dihet

Fontes lexon burime publike, kryesisht faqe të gjykatave dhe të institucioneve shtetërore. Në
përgjigjet e veta i shënon ato jozyrtare. Hapni gjithmonë lidhjen e burimit para se të mbështeteni
te një vendim ose një dispozitë.

Nëse diçka nuk shkon, shkruani te fontesmcp@proton.me çfarë bëtë dhe gabimin që patë.

## Para se të mbështeteni tek ai

- Fontes është një mjet kërkimi, jo këshillë juridike. Përdorimi i tij nuk e bën askënd avokatin
  tuaj.
- Ofrohet "siç është", pa garanci, dhe autorët e tij nuk mbajnë përgjegjësi për mënyrën si
  përdoret, për aq sa e lejon ligji. Kushtet e plota janë në [licencë](../../../LICENSE)
  (Apache 2.0).
