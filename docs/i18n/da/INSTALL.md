> Dette er en maskinstøttet oversættelse. Den engelske version er den gældende.

# Installation af Fontes

Fontes lader din AI-app slå retsafgørelser og lovgivning op live på domstoles og myndigheders
websteder i over 120 jurisdiktioner. Hvert resultat linker til originalen. Det er en standard
MCP-server, så den virker i enhver app, der kan køre en lokal MCP-server: Claude Desktop, Codex,
Claude Code, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio, Cline og
andre.

Vælg din app, følg dens trin, og [tjek derefter, at det virker](#tjek-at-det-virker).

## Claude Desktop

1. Hent Fontes-filen `.mcpb` fra den
   [seneste udgivelse](https://github.com/ykarapazar/fontes/releases/latest).
2. Dobbeltklik på den. Claude Desktop åbner den.
3. Klik på **Install**.

## Codex

I en terminal:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI og Codex-udvidelsen til IDE'er deler denne indstilling (`~/.codex/config.toml`).
Du skal bruge [uv](#du-skal-bruge-uv).

## Claude Code

I en terminal:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Du skal bruge [uv](#du-skal-bruge-uv).

## Andre apps

Hver af disse skal bruge [uv](#du-skal-bruge-uv). Tilføj posten, gem, og afslut og genåbn
derefter appen.

**Cursor:** i `~/.cursor/mcp.json` (alle projekter) eller `.cursor/mcp.json` (ét projekt):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** kør **MCP: Add Server** fra Command Palette, vælg
**Command (stdio)**, skriv `uvx fontes-mcp`, og giv serveren navnet `fontes`. Eller tilføj dette til
`~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Ældre VS Code-opsætninger bruger `.vscode/mcp.json`, hvor nøglen på øverste niveau er `servers`
i stedet for `mcpServers`.

**Gemini CLI:** i en terminal, `gemini mcp add -s user fontes uvx fontes-mcp`. Eller tilføj dette til
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** åbn din indstillingsfil (**zed: open settings file**), og tilføj:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** åbn fanen **Program** i sidepanelet til højre, klik på **Install → Edit
mcp.json**, og tilføj:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** klik på ikonet **MCP Servers**, åbn fanen **Configure**, klik på **Configure MCP
Servers**, og tilføj den samme `mcpServers`-post som for LM Studio.

**Claude Desktop, manuelt** (i stedet for filen `.mcpb`): tilføj den samme `mcpServers`-post til
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Enhver anden MCP-app** (Windsurf og andre): dens egen dokumentation siger, hvor den gemmer
sine MCP-servere. De fleste tager den samme post: kommandoen `uvx`, argumentet `fontes-mcp`.

Hvis appen ikke kan finde `uvx`, så brug den fulde sti (på macOS og Linux viser `which uvx` den).

## Du skal bruge uv

Codex, Claude Code og de andre apps starter Fontes med `uvx`, som følger med **uv**, et lille
gratis værktøj fra Astral. Se
[Astrals vejledning](https://docs.astral.sh/uv/getting-started/installation/) for at installere
det, eller kør:

- macOS eller Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Nøgler

Nogle kilder kræver en gratis nøgle: se [KEYS.md](KEYS.md).

## Tjek, at det virker

Spørg i en ny chat: *"Which jurisdictions can Fontes search?"* Appen bør svare med en liste over
lande. Gør den ikke det, så afslut og genåbn appen én gang til.

## Installationsprogram med ét klik (Mac og Windows)

Installationsprogrammet sætter Fontes op i alle dine apps på én gang: Claude Desktop, Codex,
Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio og Cline.

**Før du begynder:** afslut hver af disse apps helt. Det betyder mest for Claude Code: mens den
kører, omskriver den `~/.claude.json` og kan fortryde installationsprogrammets ændring. Hvis du
ikke kan afslutte Claude Code, så tilføj Fontes til den med `claude mcp add` i stedet (se
[Claude Code](#claude-code)).

**Mac**

1. Hent Mac-installationsprogrammet (`Fontes-Installer-…-mac.zip`) fra den [seneste
   udgivelse](https://github.com/ykarapazar/fontes/releases/latest), og dobbeltklik på det for at
   pakke det ud.
2. Dobbeltklik på **Fontes Installer**. Hvis din Mac spørger, om du vil åbne en app, der er hentet
   fra internettet, så klik på **Åbn**.
3. Vælg **Installér**, og klik på **OK**. Opsætningen tager omkring et minut.
4. En meddelelse viser de apps, det har sat op. Klik på **Færdig**, og åbn derefter de apps igen.
   Hvis du vil tilføje de valgfrie gratis nøgler først, skal du i stedet klikke på **Tilføj
   nøgler**; se [Nøgletrinnet](#nøgletrinnet).

**Windows**

1. Hent Windows-installationsprogrammet (`Fontes-Setup-….exe`) fra den [seneste
   udgivelse](https://github.com/ykarapazar/fontes/releases/latest), og dobbeltklik på det.
   - Hvis Windows viser "Windows beskyttede din pc": klik på **Flere oplysninger** og derefter
     på **Kør alligevel**.
2. Klik på **Installér**. Et vindue åbner sig og opsætter Fontes.
3. Når du bliver spurgt, om der skal sendes anonyme brugstal, så tryk Enter for nej.
4. Det spørger, om du vil tilføje nøgler nu. Tryk Enter for at springe over; se
   [Nøgletrinnet](#nøgletrinnet).
5. Når der står **Færdig**, åbner du dine AI-apps igen. Hvis en af dem stadig kørte, så luk den
   helt (også fra meddelelsesområdet ved uret), og åbn den igen.

Til sidst viser installationsprogrammet de apps, det har sat op.

### Hvilke apps det sætter op

Det sætter kun en app op, hvis appens indstillingsmappe allerede findes på din computer. Claude
Code sættes kun op, hvis `~/.claude.json` findes. Claude Desktop sættes altid op. Hver app får
én post, `fontes`, i denne fil:

| App | Fil (Mac og Linux) | Fil (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json` og Microsoft Store-versionens egen kopi |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, eller `~/.codeium/windsurf/mcp_config.json` i ældre versioner | `%APPDATA%\devin\mcp_config.json`, eller `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code sættes op, hvis `~/.copilot` eller VS Codes egen indstillingsmappe findes.

To apps kræver ét trin mere:

- **Windsurf:** når du har genåbnet den, så tryk på opdatér (refresh) i Cascade.
- **Cline i den ældre VS Code-udvidelse:** tilføj Fontes manuelt (se [Cline](#andre-apps)).

### Nøgletrinnet

Lige efter installationen tilbyder installationsprogrammet at tilføje de gratis nøgler til
Frankrig og USA. Sådan tilføjer eller ændrer du dem senere:

- **Mac:** åbn **Fontes Installer** igen, og vælg **Tilføj eller skift nøgler**.
- **Windows:** åbn Start-menuen, og vælg derefter **Fontes** → **Tilføj eller skift nøgler**.

Det, du skriver, vises ikke. Nøglerne kommer ind i alle apps, der allerede har Fontes. Afslut og
genåbn apps bagefter. Hvor du får nøglerne, og hvad de giver adgang til: [KEYS.md](KEYS.md).

### Sikkerhedskopier, ny kørsel og fjernelse

Installationsprogrammet ændrer kun posten `fontes`. Alle andre indstillinger og kommentarer
forbliver, som de var. Før det ændrer en fil, gemmer det en kopi ved siden af med navnet
`<file>.fontes-backup-<date>`. Kopier, der er lavet, efter at du har tilføjet nøgler, indeholder
disse nøgler: slet dem, du ikke længere har brug for. Det installerer også uv. Det er sikkert at
køre det igen: det reparerer opsætningen og ændrer intet andet.

For at fjerne Fontes skal du åbne **Fontes Installer** og vælge **Fjern** (Mac) eller afinstallere **Fontes** under Indstillinger → Apps (Windows). Det fjerner posten `fontes`, inklusive nøgler, fra alle apps.
Dine andre indstillinger og sikkerhedskopierne bliver.

## Opdateringer

- **Installationsprogram og filen `.mcpb`:** du behøver ikke gøre noget. Én gang om dagen, når
  appen starter, tjekker Fontes i baggrunden, om der er en nyere version, og gør den klar; næste
  gang appen starter, bruger den den. Hvis en opdatering ikke kan hentes eller ikke virker,
  fortsætter Fontes med den version, der virkede.
- **`uvx`:** Fontes fortæller dig, når en nyere version er tilgængelig, øverst i sin liste over
  jurisdiktioner. Brug `fontes-mcp@latest` i stedet for `fontes-mcp` for altid at køre den nyeste version.

Der sendes ingen oplysninger om dig eller dine søgninger nogen steder hen til dette.

## Privatliv

Fontes sender som standard intet om dig eller dine søgninger. Brugstal kræver dit tilvalg, og en
fejlrapport sendes kun, når du har set den og bekræftet. Detaljer: [PRIVACY.md](PRIVACY.md).

## Fjern det

Fjern posten `fontes` fra appens MCP-indstillinger (i Claude Code: `claude mcp remove fontes`),
og afslut og genåbn derefter appen.

## Godt at vide

Fontes læser offentlige kilder, for det meste domstoles og myndigheders websteder. Den markerer
uofficielle kilder i sine svar. Åbn altid kildelinket, før du stoler på en afgørelse eller en
bestemmelse.

Hvis noget går galt, så skriv til fontesmcp@proton.me, hvad du gjorde, og hvilken fejl du så.

## Før du stoler på det

- Fontes er et researchværktøj, ikke juridisk rådgivning. Brugen af det gør ikke nogen til din
  advokat.
- Det leveres "som det er", uden garanti, og forfatterne er ikke ansvarlige for, hvordan det
  bruges, i det omfang loven tillader det. De fulde vilkår står i
  [licensen](../../../LICENSE) (Apache 2.0).
