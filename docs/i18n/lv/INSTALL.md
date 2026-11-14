> Šis ir tulkojums, kas sagatavots ar mašīntulkošanas palīdzību. Noteicošā ir angļu valodas versija.

# Fontes instalēšana

Fontes ļauj jūsu MI lietotnei tieši meklēt tiesu nolēmumus un tiesību aktus tiesu un valsts
iestāžu tīmekļa vietnēs vairāk nekā 120 jurisdikcijās. Katrs rezultāts sniedz saiti uz
oriģinālu. Tas ir standarta MCP serveris, tāpēc tas darbojas jebkurā lietotnē, kas var palaist
lokālu MCP serveri: Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot),
Gemini CLI, Windsurf, Zed, LM Studio, Cline un citās.

Izvēlieties savu lietotni, izpildiet tās darbības, pēc tam
[pārbaudiet, vai darbojas](#kā-pārbaudīt-vai-darbojas).

## Claude Desktop

1. Lejupielādējiet Fontes `.mcpb` failu no
   [jaunākās versijas](https://github.com/ykarapazar/fontes/releases/latest).
2. Veiciet uz tā dubultklikšķi. Claude Desktop to atver.
3. Noklikšķiniet uz **Install**.

## Codex

Terminālī:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI un Codex IDE paplašinājums izmanto šo pašu iestatījumu (`~/.codex/config.toml`).
Jums vajadzīgs [uv](#jums-vajadzīgs-uv).

## Claude Code

Terminālī:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Jums vajadzīgs [uv](#jums-vajadzīgs-uv).

## Citas lietotnes

Katrai no tām vajadzīgs [uv](#jums-vajadzīgs-uv). Pievienojiet ierakstu, saglabājiet, pēc tam
aizveriet lietotni un atveriet to vēlreiz.

**Cursor:** failā `~/.cursor/mcp.json` (visiem projektiem) vai `.cursor/mcp.json` (vienam
projektam):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** komandu paletē (Command Palette) palaidiet **MCP: Add Server**,
izvēlieties **Command (stdio)**, ievadiet `uvx fontes-mcp` un nosauciet serveri `fontes`. Vai
pievienojiet šo failam `~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Vecākās VS Code konfigurācijās tiek izmantots `.vscode/mcp.json`, kur augstākā līmeņa atslēga ir
`servers`, nevis `mcpServers`.

**Gemini CLI:** terminālī `gemini mcp add -s user fontes uvx fontes-mcp`. Vai pievienojiet šo failam
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** atveriet iestatījumu failu (**zed: open settings file**) un pievienojiet:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** labajā sānjoslā atveriet cilni **Program**, noklikšķiniet uz **Install → Edit
mcp.json** un pievienojiet:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** noklikšķiniet uz ikonas **MCP Servers**, atveriet cilni **Configure**, noklikšķiniet uz
**Configure MCP Servers** un pievienojiet to pašu `mcpServers` ierakstu kā LM Studio.

**Claude Desktop manuāli** (`.mcpb` faila vietā): pievienojiet to pašu `mcpServers` ierakstu
failam `claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Jebkura cita MCP lietotne** (Windsurf un citas): tās dokumentācijā norādīts, kur tā glabā
savus MCP serverus. Lielākā daļa pieņem to pašu ierakstu: komanda `uvx`, arguments `fontes`.

Ja lietotne nevar atrast `uvx`, izmantojiet tā pilno ceļu (macOS un Linux to parāda
`which uvx`).

## Jums vajadzīgs uv

Codex, Claude Code un citas lietotnes palaiž Fontes ar `uvx`, kas ir iekļauts **uv** – nelielā
bezmaksas Astral rīkā. Lai to instalētu, skatiet
[Astral ceļvedi](https://docs.astral.sh/uv/getting-started/installation/) vai palaidiet:

- macOS vai Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Atslēgas

Dažiem avotiem nepieciešama bezmaksas atslēga: skatiet [KEYS.md](KEYS.md).

## Kā pārbaudīt, vai darbojas

Jaunā sarunā pajautājiet: *“Kurās jurisdikcijās Fontes var meklēt?”* Lietotnei vajadzētu
atbildēt ar valstu sarakstu. Ja tā nenotiek, vēlreiz aizveriet lietotni un atveriet to no jauna.

## Instalētājs ar vienu klikšķi (Mac)

Mac instalētājs iestata Fontes visās jūsu lietotnēs uzreiz: Claude Desktop, Codex, Claude Code,
Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio un Cline. Windows
instalētājs būs pieejams drīzumā; līdz tam izmantojiet augstāk norādītās darbības savai lietotnei.

**Pirms sākat:** pilnībā aizveriet katru no šīm lietotnēm. Visvairāk tas attiecas uz Claude
Code: darbības laikā tā pārraksta `~/.claude.json` un var atsaukt instalētāja izmaiņas. Ja
nevarat aizvērt Claude Code, labāk pievienojiet tai Fontes ar `claude mcp add` (skatiet
[Claude Code](#claude-code)).

**Mac**

1. Lejupielādējiet Mac instalētāju (`Fontes-Installer-…-mac.zip`) no
   [jaunākās versijas](https://github.com/ykarapazar/fontes/releases/latest) un veiciet uz tā dubultklikšķi, lai to izpakotu.
2. Veiciet dubultklikšķi uz **Fontes Installer**. Ja jūsu Mac jautā, vai atvērt no interneta
   lejupielādētu lietotni, noklikšķiniet uz **Open**.
3. Izvēlieties **Instalēt** un noklikšķiniet uz **Labi**. Iestatīšana aizņem apmēram minūti.
4. Ziņojumā ir uzskaitītas lietotnes, kuras tas iestatīja. Noklikšķiniet uz **Gatavs** un pēc tam atkal
   atveriet šīs lietotnes. Lai vispirms pievienotu neobligātās bezmaksas atslēgas, tā vietā
   noklikšķiniet uz **Pievienot atslēgas**; skatiet [Atslēgu solis](#atslēgu-solis).

**Windows** (kad Windows instalētājs būs izlaists)

1. Izpakojiet lejupielādēto **Fontes Installer** (labā poga → Extract All).
2. Veiciet dubultklikšķi uz **Install Fontes.cmd**.
   - Ja Windows parāda “Windows protected your PC”: noklikšķiniet uz **More info**, pēc tam uz
     **Run anyway**.
3. Kad tiek jautāts, vai sūtīt anonīmus lietojuma skaitļus, lai atbildētu “nē”, nospiediet
   Enter.
4. Tas jautā, vai pievienot atslēgas tagad. Lai izlaistu, nospiediet Enter; skatiet
   [Atslēgu solis](#atslēgu-solis).
5. Kad tas parāda **Done**, atkal atveriet savas MI lietotnes. Ja kāda vēl darbojās, pilnībā to
   aizveriet (arī sistēmas teknē, pie pulksteņa) un atveriet vēlreiz.

Beigās instalētājs uzskaita lietotnes, kuras tas iestatīja.

### Kuras lietotnes tas iestata

Tas iestata lietotni tikai tad, ja tās iestatījumu mape jau ir jūsu datorā. Claude Code tiek
iestatīta tikai tad, ja eksistē `~/.claude.json`. Claude Desktop tiek iestatīta vienmēr. Katra
lietotne saņem vienu ierakstu `fontes` šajā failā:

| Lietotne | Fails (Mac un Linux) | Fails (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json` un Microsoft Store versijas atsevišķā kopija |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json` vai vecākās versijās `~/.codeium/windsurf/mcp_config.json` | `%APPDATA%\devin\mcp_config.json` vai `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code tiek iestatīts, ja eksistē `~/.copilot` vai paša VS Code iestatījumu mape.

Divām lietotnēm vajadzīgs vēl viens solis:

- **Windsurf:** pēc atkārtotas atvēršanas nospiediet atsvaidzināšanu (refresh) Cascade.
- **Cline vecākajā VS Code paplašinājumā:** pievienojiet Fontes manuāli (skatiet
  [Cline](#citas-lietotnes)).

### Atslēgu solis

Uzreiz pēc instalēšanas instalētājs piedāvā pievienot bezmaksas Francijas un ASV atslēgas. Lai
tās pievienotu vai mainītu vēlāk:

- **Mac:** vēlreiz atveriet **Fontes Installer** un izvēlieties **Pievienot vai mainīt atslēgas**.
- **Windows:** instalētāja mapē veiciet dubultklikšķi uz **Add or change keys.cmd**.

Ievadītais teksts netiek rādīts. Atslēgas tiek ierakstītas katrā lietotnē, kurā jau ir Fontes.
Pēc tam aizveriet lietotnes un atveriet tās vēlreiz. Kur iegūt atslēgas un ko tās atver:
[KEYS.md](KEYS.md).

### Rezerves kopijas, atkārtota palaišana un noņemšana

Instalētājs maina tikai ierakstu `fontes`. Visi citi iestatījumi un komentāri paliek nemainīti.
Pirms faila maiņas tas blakus saglabā kopiju ar nosaukumu `<file>.fontes-backup-<date>`.
Kopijās, kas izveidotas pēc atslēgu pievienošanas, ir šīs atslēgas: izdzēsiet tās, kas vairs nav
vajadzīgas. Tas arī instalē uv. Atkārtota palaišana ir droša: tā salabo iestatījumus un neko
citu nemaina.

Lai noņemtu Fontes, atveriet **Fontes Installer** un izvēlieties **Noņemt** (Mac) vai veiciet
dubultklikšķi uz **Uninstall Fontes.cmd** (Windows). Tas no visām lietotnēm noņem ierakstu `fontes`, ieskaitot
atslēgas. Jūsu pārējie iestatījumi un rezerves kopijas paliek.

## Atjauninājumi

- **Instalētājs un `.mcpb` fails:** jums nekas nav jādara. Reizi dienā, kad lietotne tiek
  palaista, Fontes fonā pārbauda, vai ir jaunāka versija, un sagatavo to; nākamajā lietotnes
  palaišanas reizē tā tiek izmantota. Ja atjauninājumu nevar lejupielādēt vai tas nedarbojas,
  Fontes turpina izmantot versiju, kas darbojās.
- **`uvx`:** Fontes jurisdikciju saraksta augšdaļā paziņo, kad ir pieejama jaunāka versija. Lai
  vienmēr palaistu jaunāko versiju, `fontes-mcp` vietā izmantojiet `fontes-mcp@latest`.

Šim nolūkam nekāda informācija par jums vai jūsu meklējumiem netiek nekur sūtīta.

## Privātums

Pēc noklusējuma Fontes nesūta neko par jums vai jūsu meklējumiem. Lietojuma skaitļi tiek sūtīti
tikai ar jūsu piekrišanu (opt-in), un kļūdas ziņojums tiek nosūtīts tikai pēc tam, kad esat to
redzējis un apstiprinājis. Sīkāk: [PRIVACY.md](PRIVACY.md).

## Noņemšana

Noņemiet ierakstu `fontes` no savas lietotnes MCP iestatījumiem (Claude Code:
`claude mcp remove fontes`), pēc tam aizveriet lietotni un atveriet to vēlreiz.

## Der zināt

Fontes lasa publiskus avotus, galvenokārt tiesu un valsts iestāžu tīmekļa vietnes. Savās
atbildēs tas atzīmē neoficiālos avotus. Pirms paļaujaties uz nolēmumu vai normu, vienmēr
atveriet avota saiti.

Ja kaut kas nedarbojas, uzrakstiet, ko darījāt un kādu kļūdu redzējāt, uz fontesmcp@proton.me.

## Pirms paļaujaties uz to

- Fontes ir izpētes rīks, nevis juridiska konsultācija. Tā lietošana nevienu nepadara par jūsu
  advokātu.
- Tas tiek nodrošināts “tāds, kāds ir” (“as is”), bez jebkādām garantijām, un tā autori,
  ciktāl to pieļauj likums, neatbild par to, kā tas tiek izmantots. Pilni noteikumi ir
  [licencē](../../../LICENSE) (Apache 2.0).
