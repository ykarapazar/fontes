> Dit is een machinaal ondersteunde vertaling. De Engelse versie is leidend.

# Fontes installeren

Met Fontes kan uw AI-app rechterlijke uitspraken en wetgeving live opzoeken op websites van
gerechten en overheden in meer dan 120 rechtsstelsels. Elk resultaat linkt naar het origineel. Het
is een standaard MCP-server en werkt dus in elke app die een lokale MCP-server kan draaien: Claude
Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio,
Cline en andere.

Kies uw app, volg de stappen en [controleer daarna of het werkt](#controleren-of-het-werkt).

## Claude Desktop

1. Download het Fontes-bestand `.mcpb` uit de
   [nieuwste release](https://github.com/ykarapazar/fontes/releases/latest).
2. Dubbelklik erop. Claude Desktop opent het.
3. Klik op **Install**.

## Codex

In een terminal:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

De Codex CLI en de Codex IDE-extensie delen deze instelling (`~/.codex/config.toml`).
U hebt [uv](#u-hebt-uv-nodig) nodig.

## Claude Code

In een terminal:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

U hebt [uv](#u-hebt-uv-nodig) nodig.

## Andere apps

Elk van deze apps heeft [uv](#u-hebt-uv-nodig) nodig. Voeg de vermelding toe, sla op, sluit de app
af en open hem opnieuw.

**Cursor:** in `~/.cursor/mcp.json` (alle projecten) of `.cursor/mcp.json` (één project):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** voer **MCP: Add Server** uit vanuit het opdrachtenpalet, kies
**Command (stdio)**, voer `uvx fontes-mcp` in en noem de server `fontes`. Of voeg dit toe aan
`~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Oudere VS Code-opstellingen gebruiken `.vscode/mcp.json`, waar de sleutel op het hoogste niveau
`servers` is in plaats van `mcpServers`.

**Gemini CLI:** in een terminal `gemini mcp add -s user fontes uvx fontes-mcp`. Of voeg dit toe aan
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** open uw instellingenbestand (**zed: open settings file**) en voeg toe:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** open in de rechterzijbalk het tabblad **Program**, klik op **Install → Edit
mcp.json** en voeg toe:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** klik op het pictogram **MCP Servers**, open het tabblad **Configure**, klik op
**Configure MCP Servers** en voeg dezelfde `mcpServers`-vermelding toe als bij LM Studio.

**Claude Desktop, met de hand** (in plaats van het `.mcpb`-bestand): voeg dezelfde
`mcpServers`-vermelding toe aan `claude_desktop_config.json` (macOS:
`~/Library/Application Support/Claude/`, Windows: `%APPDATA%\Claude\`).

**Elke andere MCP-app** (Windsurf en andere): de eigen documentatie van de app vermeldt waar die
zijn MCP-servers bewaart. De meeste gebruiken dezelfde vermelding: opdracht `uvx`, argument `fontes`.

Als de app `uvx` niet kan vinden, gebruik dan het volledige pad (op macOS en Linux toont `which uvx`
het).

## U hebt uv nodig

Codex, Claude Code en de andere apps starten Fontes met `uvx`, dat wordt meegeleverd met **uv**, een
kleine gratis tool van Astral. Zie voor de installatie de
[handleiding van Astral](https://docs.astral.sh/uv/getting-started/installation/), of voer uit:

- macOS of Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Sleutels

Sommige bronnen hebben een gratis sleutel nodig: zie [KEYS.md](KEYS.md).

## Controleren of het werkt

Vraag in een nieuwe chat: *"Welke rechtsstelsels kan Fontes doorzoeken?"* De app hoort te antwoorden
met een lijst van landen. Gebeurt dat niet, sluit de app dan nog een keer af en open hem opnieuw.

## Installatieprogramma met één klik (Mac)

Het Mac-installatieprogramma stelt Fontes in één keer in al uw apps in: Claude Desktop, Codex,
Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio en Cline. Een
installatieprogramma voor Windows is in voorbereiding; gebruik tot die tijd de stappen voor uw app
hierboven.

**Voordat u begint:** sluit elk van deze apps volledig af. Dat is vooral belangrijk voor Claude Code:
terwijl het draait, herschrijft het `~/.claude.json` en kan het de wijziging van het
installatieprogramma ongedaan maken. Als u Claude Code niet kunt afsluiten, voeg Fontes er dan in
plaats daarvan aan toe met `claude mcp add` (zie [Claude Code](#claude-code)).

**Mac**

1. Download het Mac-installatieprogramma (`Fontes-Installer-…-mac.zip`) uit de
   [nieuwste release](https://github.com/ykarapazar/fontes/releases/latest) en dubbelklik erop om
   het uit te pakken.
2. Dubbelklik op **Fontes Installer**. Als uw Mac vraagt of u een van internet gedownloade app wilt
   openen, klik dan op **Open**.
3. Kies **Installeren** en klik op **OK**. Het instellen duurt ongeveer een minuut.
4. Een melding toont de apps die zijn ingesteld. Klik op **Klaar** en open die apps daarna opnieuw.
   Wilt u eerst de optionele gratis sleutels toevoegen, klik dan in plaats daarvan op
   **Sleutels toevoegen**; zie [Sleutels in het installatieprogramma](#sleutels-in-het-installatieprogramma).

**Windows** (zodra het installatieprogramma voor Windows is uitgebracht)

1. Pak de gedownloade **Fontes Installer** uit (rechtsklik → **Alles uitpakken**).
2. Dubbelklik op **Install Fontes.cmd**.
   - Als Windows "Windows heeft uw pc beschermd" toont: klik op **Meer informatie** en daarna op
     **Toch uitvoeren**.
3. Wanneer gevraagd wordt of u anonieme gebruiksaantallen wilt verzenden, druk op Enter voor nee.
4. Het vraagt of u nu sleutels wilt toevoegen. Druk op Enter om over te slaan; zie
   [Sleutels in het installatieprogramma](#sleutels-in-het-installatieprogramma).
5. Wanneer **Klaar** verschijnt, opent u uw AI-apps weer. Als er een nog draaide, sluit die dan
   volledig af (ook vanuit het systeemvak, naast de klok) en open hem opnieuw.

Aan het einde toont het installatieprogramma de apps die het heeft ingesteld.

### Welke apps het instelt

Het stelt een app alleen in als de instellingenmap van die app al op uw computer staat. Claude Code
wordt alleen ingesteld als `~/.claude.json` bestaat. Claude Desktop wordt altijd ingesteld. Elke app
krijgt één vermelding, `fontes`, in dit bestand:

| App | Bestand (Mac en Linux) | Bestand (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, en de eigen kopie van de Microsoft Store-versie |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, of `~/.codeium/windsurf/mcp_config.json` bij oudere versies | `%APPDATA%\devin\mcp_config.json`, of `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code wordt ingesteld als `~/.copilot` of de eigen instellingenmap van VS Code bestaat.

Twee apps hebben nog één stap nodig:

- **Windsurf:** druk na het heropenen op refresh in Cascade.
- **Cline in de oudere VS Code-extensie:** voeg Fontes met de hand toe (zie [Cline](#andere-apps)).

### Sleutels in het installatieprogramma

Direct na de installatie biedt het installatieprogramma aan de gratis sleutels voor Frankrijk en de
VS toe te voegen. Om ze later toe te voegen of te wijzigen:

- **Mac:** open **Fontes Installer** opnieuw en kies **Sleutels toevoegen of wijzigen**.
- **Windows:** dubbelklik op **Add or change keys.cmd** in de map van het installatieprogramma.

Wat u typt blijft verborgen. De sleutels worden toegevoegd aan elke app die Fontes al heeft. Sluit de
apps daarna af en open ze opnieuw. Waar u de sleutels krijgt en wat ze ontsluiten: [KEYS.md](KEYS.md).

### Reservekopieën, opnieuw uitvoeren en verwijderen

Het installatieprogramma wijzigt alleen de vermelding `fontes`. Alle andere instellingen en
opmerkingen blijven zoals ze waren. Voordat het een bestand wijzigt, slaat het er een kopie naast
op, met de naam `<file>.fontes-backup-<date>`. Kopieën die zijn gemaakt nadat u sleutels hebt
toegevoegd, bevatten die sleutels: verwijder de kopieën die u niet meer nodig hebt. Het installeert
ook uv. Opnieuw uitvoeren is veilig: het herstelt de installatie en wijzigt verder niets.

Om Fontes te verwijderen, opent u **Fontes Installer** en kiest u **Verwijderen** (Mac), of
dubbelklikt u op **Uninstall Fontes.cmd** (Windows). Dit verwijdert de vermelding `fontes`, inclusief
sleutels, uit elke app. Uw andere instellingen en de reservekopieën blijven staan.

## Updates

- **Installatieprogramma en `.mcpb`-bestand:** u hoeft niets te doen. Eenmaal per dag, wanneer de
  app start, controleert Fontes op de achtergrond of er een nieuwere versie is en zet die klaar; de
  volgende keer dat de app start, wordt die gebruikt. Als een update niet kan worden gedownload of
  niet werkt, blijft Fontes de versie gebruiken die werkte.
- **`uvx`:** Fontes meldt bovenaan zijn lijst van rechtsstelsels wanneer er een nieuwere versie
  beschikbaar is. Om altijd de nieuwste versie te draaien, gebruikt u `fontes-mcp@latest` in plaats van
  `fontes`.

Hiervoor wordt geen informatie over u of uw zoekopdrachten verzonden.

## Privacy

Fontes verzendt standaard niets over u of uw zoekopdrachten. Gebruiksaantallen zijn opt-in, en een
foutrapport wordt pas verzonden nadat u het hebt gezien en bevestigd. Details: [PRIVACY.md](PRIVACY.md).

## Verwijderen

Verwijder de vermelding `fontes` uit de MCP-instellingen van uw app (in Claude Code:
`claude mcp remove fontes`), sluit de app daarna af en open hem opnieuw.

## Goed om te weten

Fontes leest openbare bronnen, vooral websites van gerechten en overheden. Niet-officiële bronnen
markeert het in zijn antwoorden. Open altijd de link naar de bron voordat u op een uitspraak of een
bepaling vertrouwt.

Als er iets misgaat, mail dan wat u deed en welke foutmelding u zag naar fontesmcp@proton.me.

## Voordat u erop vertrouwt

- Fontes is een onderzoekstool, geen juridisch advies. Door het te gebruiken wordt niemand uw
  advocaat.
- Het wordt geleverd "zoals het is", zonder garantie, en de auteurs zijn, voor zover de wet dat
  toestaat, niet aansprakelijk voor hoe het wordt gebruikt. De volledige voorwaarden staan in de
  [licentie](../../../LICENSE) (Apache 2.0).
