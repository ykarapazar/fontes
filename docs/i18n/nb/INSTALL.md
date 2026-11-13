> Dette er en maskinassistert oversettelse. Den engelske versjonen er den gjeldende.

# Installere Fontes

Fontes lar AI-appen din slå opp rettsavgjørelser og lovgivning direkte på domstolers og
myndigheters nettsteder i over 120 jurisdiksjoner. Hvert resultat lenker til originalen. Det er en
standard MCP-server, så den fungerer i enhver app som kan kjøre en lokal MCP-server: Claude
Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed,
LM Studio, Cline og andre.

**Fontes er ikke på PyPI ennå.** Trinnene nedenfor fungerer når den første utgivelsen er ute.

Velg appen din, følg trinnene for den, og [sjekk deretter at det fungerer](#sjekk-at-det-fungerer).

## Claude Desktop

1. Last ned Fontes-filen `.mcpb` fra den
   [nyeste utgivelsen](https://github.com/ykarapazar/fontes/releases/latest).
2. Dobbeltklikk på den. Claude Desktop åpner den.
3. Klikk på **Install**.

## Codex

I en terminal:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI og Codex-utvidelsen for IDE-er deler denne innstillingen (`~/.codex/config.toml`).
Du trenger [uv](#du-trenger-uv).

## Claude Code

I en terminal:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Du trenger [uv](#du-trenger-uv).

## Andre apper

Hver av disse trenger [uv](#du-trenger-uv). Legg til oppføringen, lagre, og avslutt og åpne
deretter appen på nytt.

**Cursor:** i `~/.cursor/mcp.json` (alle prosjekter) eller `.cursor/mcp.json` (ett prosjekt):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** kjør **MCP: Add Server** fra Command Palette, velg
**Command (stdio)**, skriv inn `uvx fontes-mcp`, og gi serveren navnet `fontes`. Eller legg dette til i
`~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Eldre VS Code-oppsett bruker `.vscode/mcp.json`, der nøkkelen på øverste nivå er `servers` i
stedet for `mcpServers`.

**Gemini CLI:** i en terminal, `gemini mcp add -s user fontes uvx fontes-mcp`. Eller legg dette til i
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** åpne innstillingsfilen din (**zed: open settings file**), og legg til:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** åpne fanen **Program** i sidepanelet til høyre, klikk på **Install → Edit
mcp.json**, og legg til:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** klikk på ikonet **MCP Servers**, åpne fanen **Configure**, klikk på **Configure MCP
Servers**, og legg til den samme `mcpServers`-oppføringen som for LM Studio.

**Claude Desktop, for hånd** (i stedet for filen `.mcpb`): legg til den samme
`mcpServers`-oppføringen i `claude_desktop_config.json` (macOS:
`~/Library/Application Support/Claude/`, Windows: `%APPDATA%\Claude\`).

**Enhver annen MCP-app** (Windsurf og andre): dokumentasjonen for appen sier hvor den lagrer
MCP-serverne sine. De fleste tar den samme oppføringen: kommandoen `uvx`, argumentet `fontes`.

Hvis appen ikke finner `uvx`, bruk den fullstendige banen (på macOS og Linux viser `which uvx`
den).

## Du trenger uv

Codex, Claude Code og de andre appene starter Fontes med `uvx`, som følger med **uv**, et lite
gratis verktøy fra Astral. For å installere det, se
[Astrals veiledning](https://docs.astral.sh/uv/getting-started/installation/), eller kjør:

- macOS eller Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Nøkler

Noen kilder krever en gratis nøkkel: se [KEYS.md](KEYS.md).

## Sjekk at det fungerer

Spør i en ny chat: *"Which jurisdictions can Fontes search?"* Appen skal svare med en liste over
land. Hvis ikke, avslutt og åpne appen på nytt én gang til.

## Installasjonsprogram med ett klikk (på vei)

Et installasjonsprogram for Mac og Windows som setter opp Fontes i alle appene dine på én gang, er
på vei. Det setter opp Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot),
Windsurf, Gemini CLI, Zed, LM Studio og Cline. Når det er utgitt:

**Før du begynner:** avslutt hver av disse appene helt. Dette betyr mest for Claude Code: mens den
kjører, skriver den om `~/.claude.json` og kan angre endringen fra installasjonsprogrammet. Hvis du
ikke kan avslutte Claude Code, legg heller til Fontes i den med `claude mcp add` (se
[Claude Code](#claude-code)).

**Mac**

1. Åpne den nedlastede mappen **Fontes Installer**.
2. Dobbeltklikk på **Install Fontes.command**.
   - Hvis Macen sier at filen "kan ikke åpnes fordi den er fra en ukjent utvikler": høyreklikk
     (eller Ctrl-klikk) på filen, velg **Åpne**, og deretter **Åpne** igjen. Dette gjør du bare
     én gang.
3. Et vindu åpnes og spør om anonyme brukstall skal sendes; trykk Enter for nei.
4. Det spør om du vil legge til nøkler nå. Trykk Enter for å hoppe over; se
   [Nøkkeltrinnet](#nøkkeltrinnet).
5. Når det står **Ferdig**, åpner du AI-appene dine igjen.

**Windows**

1. Pakk ut den nedlastede **Fontes Installer** (høyreklikk → Pakk ut alle).
2. Dobbeltklikk på **Install Fontes.cmd**.
   - Hvis Windows viser "Windows beskyttet PC-en": klikk på **Mer informasjon** og deretter på
     **Kjør likevel**.
3. Når du blir spurt om anonyme brukstall skal sendes, trykk Enter for nei.
4. Det spør om du vil legge til nøkler nå. Trykk Enter for å hoppe over; se
   [Nøkkeltrinnet](#nøkkeltrinnet).
5. Når det står **Ferdig**, åpner du AI-appene dine igjen. Hvis en av dem fortsatt kjørte, lukk den
   helt (også fra varslingsområdet ved klokken), og åpne den igjen.

Til slutt viser installasjonsprogrammet appene det har satt opp.

### Hvilke apper det setter opp

Det setter bare opp en app hvis appens innstillingsmappe allerede finnes på datamaskinen din.
Claude Code settes bare opp hvis `~/.claude.json` finnes. Claude Desktop settes alltid opp. Hver
app får én oppføring, `fontes`, i denne filen:

| App | Fil (Mac og Linux) | Fil (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, og Microsoft Store-versjonens egen kopi |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, eller `~/.codeium/windsurf/mcp_config.json` i eldre versjoner | `%APPDATA%\devin\mcp_config.json`, eller `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code settes opp hvis `~/.copilot` eller VS Codes egen innstillingsmappe finnes.

To apper trenger ett trinn til:

- **Windsurf:** når du har åpnet den igjen, trykk på oppdater (refresh) i Cascade.
- **Cline i den eldre VS Code-utvidelsen:** legg til Fontes for hånd (se [Cline](#andre-apper)).

### Nøkkeltrinnet

Rett etter installasjonen tilbyr installasjonsprogrammet å legge til de gratis nøklene for
Frankrike og USA. Slik legger du dem til eller endrer dem senere:

- **Mac:** dobbeltklikk på **Add or change keys.command** i mappen til installasjonsprogrammet,
  eller åpne appen Fontes Installer igjen og velg **Legg til eller endre nøkler**.
- **Windows:** dobbeltklikk på **Add or change keys.cmd** i mappen til installasjonsprogrammet.

Det du skriver, vises ikke. Nøklene legges inn i alle apper som allerede har Fontes. Avslutt og
åpne appene på nytt etterpå. Hvor du får nøklene, og hva de gir tilgang til: [KEYS.md](KEYS.md).

### Sikkerhetskopier, ny kjøring og fjerning

Installasjonsprogrammet endrer bare oppføringen `fontes`. Alle andre innstillinger og kommentarer
blir som de var. Før det endrer en fil, lagrer det en kopi ved siden av med navnet
`<file>.fontes-backup-<date>`. Kopier som er laget etter at du la til nøkler, inneholder disse
nøklene: slett dem du ikke lenger trenger. Det installerer også uv. Det er trygt å kjøre det på
nytt: det reparerer oppsettet og endrer ingenting annet.

For å fjerne Fontes dobbeltklikker du på **Uninstall Fontes.command** (Mac) eller
**Uninstall Fontes.cmd** (Windows). Det fjerner oppføringen `fontes`, inkludert nøkler, fra alle
apper. De andre innstillingene dine og sikkerhetskopiene blir værende.

## Oppdateringer

- **Installasjonsprogram og filen `.mcpb`:** du trenger ikke gjøre noe. Én gang om dagen, når
  appen starter, sjekker Fontes i bakgrunnen om det finnes en nyere versjon, og gjør den klar;
  neste gang appen starter, bruker den den. Hvis en oppdatering ikke kan lastes ned eller ikke
  fungerer, fortsetter Fontes med versjonen som fungerte.
- **`uvx`:** Fontes sier fra når en nyere versjon er tilgjengelig, øverst i listen over
  jurisdiksjoner. Bruk `fontes-mcp@latest` i stedet for `fontes-mcp` for alltid å kjøre den nyeste
  versjonen.

Ingen informasjon om deg eller søkene dine sendes noe sted for dette.

## Personvern

Fontes sender som standard ingenting om deg eller søkene dine. Brukstall krever at du velger det,
og en feilrapport sendes bare etter at du har sett den og bekreftet. Detaljer:
[PRIVACY.md](PRIVACY.md).

## Fjerne det

Fjern oppføringen `fontes` fra MCP-innstillingene i appen din (i Claude Code:
`claude mcp remove fontes`), og avslutt og åpne deretter appen på nytt.

## Greit å vite

Fontes leser offentlige kilder, for det meste domstolers og myndigheters nettsteder. Den merker
uoffisielle kilder i svarene sine. Åpne alltid kildelenken før du stoler på en avgjørelse eller en
bestemmelse.

Hvis noe går galt, send e-post til fontesmcp@proton.me med hva du gjorde og feilen du så.

## Før du stoler på det

- Fontes er et researchverktøy, ikke juridisk rådgivning. Bruken av det gjør ingen til advokaten
  din.
- Det leveres "som det er", uten garanti, og forfatterne er ikke ansvarlige for hvordan det
  brukes, så langt loven tillater det. De fullstendige vilkårene står i
  [lisensen](../../../LICENSE) (Apache 2.0).
