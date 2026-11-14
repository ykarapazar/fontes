> Dette er ei maskinassistert omsetjing. Den engelske versjonen er den gjeldande.

# Installere Fontes

Fontes lèt KI-appen din slå opp rettsavgjerder og lovgjeving direkte på nettstadene til domstolar og
styresmakter i over 120 jurisdiksjonar. Kvart resultat lenkjer til originalen. Det er ein standard
MCP-server, så han verkar i alle appar som kan køyre ein lokal MCP-server: Claude Desktop, Codex, Claude
Code, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio, Cline og andre.

Vel appen din, følg stega for han, og [sjekk så at det verkar](#sjekk-at-det-verkar).

## Claude Desktop

1. Last ned `.mcpb`-fila til Fontes frå
   [den siste utgåva](https://github.com/ykarapazar/fontes/releases/latest).
2. Dobbeltklikk på henne. Claude Desktop opnar henne.
3. Klikk **Install**.

## Codex

I ein terminal:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI og Codex-utvidinga for IDE deler denne innstillinga (`~/.codex/config.toml`).
Du treng [uv](#du-treng-uv).

## Claude Code

I ein terminal:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Du treng [uv](#du-treng-uv).

## Andre appar

Kvar av desse treng [uv](#du-treng-uv). Legg til oppføringa, lagre, og avslutt og opne appen på nytt.

**Cursor:** i `~/.cursor/mcp.json` (alle prosjekt) eller `.cursor/mcp.json` (eitt prosjekt):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** køyr **MCP: Add Server** frå Command Palette, vel
**Command (stdio)**, skriv inn `uvx fontes-mcp` og kall serveren `fontes`. Eller legg dette til i
`~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Eldre VS Code-oppsett brukar `.vscode/mcp.json`, der nøkkelen på øvste nivå er `servers` i staden for
`mcpServers`.

**Gemini CLI:** i ein terminal, `gemini mcp add -s user fontes uvx fontes-mcp`. Eller legg dette til i
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** opne innstillingsfila (**zed: open settings file**) og legg til:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** i sidefeltet til høgre, opne fana **Program**, klikk **Install → Edit
mcp.json**, og legg til:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** klikk på ikonet **MCP Servers**, opne fana **Configure**, klikk **Configure MCP
Servers**, og legg til den same `mcpServers`-oppføringa som for LM Studio.

**Claude Desktop, for hand** (i staden for `.mcpb`-fila): legg den same `mcpServers`-oppføringa til i
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Alle andre MCP-appar** (Windsurf og andre): dokumentasjonen til appen seier kvar han held MCP-serverane
sine. Dei fleste tek den same oppføringa: kommando `uvx`, argument `fontes`.

Om appen ikkje finn `uvx`, bruk den fullstendige stigen (på macOS og Linux skriv `which uvx` han ut).

## Du treng uv

Codex, Claude Code og dei andre appane startar Fontes med `uvx`, som følgjer med **uv**, eit lite
gratis verktøy frå Astral. For å installere det, sjå
[rettleiinga frå Astral](https://docs.astral.sh/uv/getting-started/installation/), eller køyr:

- macOS eller Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Nøklar

Somme kjelder krev ein gratis nøkkel: sjå [KEYS.md](KEYS.md).

## Sjekk at det verkar

I ein ny samtale, spør: *«Kva jurisdiksjonar kan Fontes søkje i?»* Appen skal svare med ei
liste over land. Om han ikkje gjer det, avslutt og opne appen éin gong til.

## Installasjonsprogram med eitt klikk (Mac)

Mac-installasjonsprogrammet set opp Fontes i alle appane dine samstundes: Claude Desktop, Codex,
Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio og Cline. Eit
installasjonsprogram for Windows er på veg; fram til då kan du bruke stega for appen din ovanfor.

**Før du byrjar:** avslutt kvar av desse appane heilt. Dette er viktigast for Claude Code:
medan han køyrer, skriv han om `~/.claude.json` og kan gjere om endringa frå installasjonsprogrammet. Om du ikkje kan
avslutte Claude Code, legg heller Fontes til i han med `claude mcp add` (sjå [Claude Code](#claude-code)).

**Mac**

1. Last ned Mac-installasjonsprogrammet (`Fontes-Installer-…-mac.zip`) frå den [nyaste
   utgjevinga](https://github.com/ykarapazar/fontes/releases/latest), og dobbeltklikk på det for å
   pakke det ut.
2. Dobbeltklikk på **Fontes Installer**. Om Mac-en spør om du vil opne ein app som er lasta ned frå
   internett, klikk på **Open**.
3. Vel **Installer** og klikk på **OK**. Oppsettet tek om lag eitt minutt.
4. Ei melding listar opp appane det sette opp. Klikk på **Ferdig**, og opne så desse appane igjen.
   Vil du leggje til dei valfrie gratisnøklane først, klikkar du heller på **Legg til nøklar**; sjå
   [Nøkkelsteget](#nøkkelsteget).

**Windows** (når installasjonsprogrammet for Windows er gjeve ut)

1. Pakk ut den nedlasta **Fontes Installer** (høgreklikk → Extract All).
2. Dobbeltklikk på **Install Fontes.cmd**.
   - Om Windows viser «Windows protected your PC»: klikk **More info**, og så **Run anyway**.
3. Når du blir spurd om du vil sende anonyme brukstal, trykk Enter for nei.
4. Det spør om du vil leggje til nøklar no. Trykk Enter for å hoppe over; sjå [Nøkkelsteget](#nøkkelsteget).
5. Når det står **Done**, opne KI-appane dine igjen. Om ein av dei framleis køyrde, lukk han
   heilt (òg frå systemstatusfeltet, ved klokka) og opne han igjen.

Til slutt listar installasjonsprogrammet opp appane det sette opp.

### Kva appar det set opp

Det set berre opp ein app om innstillingsmappa til appen allereie finst på datamaskina di. Claude Code
blir berre sett opp om `~/.claude.json` finst. Claude Desktop blir alltid sett opp. Kvar app får éi
oppføring, `fontes`, i denne fila:

| App | Fil (Mac og Linux) | Fil (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, og den eigne kopien til Microsoft Store-versjonen |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, eller `~/.codeium/windsurf/mcp_config.json` i eldre versjonar | `%APPDATA%\devin\mcp_config.json`, eller `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code blir sett opp om `~/.copilot` eller den eigne innstillingsmappa til VS Code finst.

To appar treng eitt steg til:

- **Windsurf:** etter at du har opna han igjen, trykk på oppdater i Cascade.
- **Cline i den eldre VS Code-utvidinga:** legg til Fontes for hand (sjå [Cline](#andre-appar)).

### Nøkkelsteget

Rett etter installeringa tilbyr installasjonsprogrammet å leggje til dei gratis nøklane for Frankrike og USA. For å leggje dei til eller
endre dei seinare:

- **Mac:** opne **Fontes Installer** igjen og vel **Legg til eller endre nøklar**.
- **Windows:** dobbeltklikk på **Add or change keys.cmd** i installasjonsmappa.

Det du skriv, blir ikkje vist. Nøklane går inn i alle appar som allereie har Fontes. Avslutt og opne appane
igjen etterpå. Kvar du får nøklane, og kva dei gjev tilgang til: [KEYS.md](KEYS.md).

### Tryggingskopiar, nye køyringar og fjerning

Installasjonsprogrammet endrar berre `fontes`-oppføringa. Alle andre innstillingar og kommentarar blir verande som dei var.
Før det endrar ei fil, lagrar det ein kopi ved sida av, kalla `<file>.fontes-backup-<date>`. Kopiar
laga etter at du la til nøklar, inneheld desse nøklane: slett dei du ikkje lenger treng. Det
installerer òg uv. Det er trygt å køyre det på nytt: det reparerer oppsettet og endrar ikkje noko anna.

For å fjerne Fontes, opne **Fontes Installer** og vel **Fjern** (Mac), eller dobbeltklikk på **Uninstall Fontes.cmd** (Windows). Det fjernar `fontes`-oppføringa, nøklane medrekna, frå alle appar. Dei andre innstillingane dine
og tryggingskopiane blir verande.

## Oppdateringar

- **Installasjonsprogram og `.mcpb`-fil:** du treng ikkje gjere noko. Éin gong om dagen, når appen
  startar, ser Fontes etter ein nyare versjon i bakgrunnen og gjer han klar; neste gong
  appen startar, brukar han han. Om ei oppdatering ikkje kan lastast ned eller ikkje verkar, held Fontes fram
  med å bruke versjonen som verka.
- **`uvx`:** Fontes seier frå når ein nyare versjon er tilgjengeleg, øvst i lista over
  jurisdiksjonar. For alltid å køyre den nyaste versjonen, bruk `fontes-mcp@latest` i staden for `fontes-mcp`.

Ingen informasjon om deg eller søka dine blir send nokon stad for dette.

## Personvern

Fontes sender ingenting om deg eller søka dine som standard. Brukstal er opt-in, og ein feilrapport
blir berre send etter at du har sett han og stadfesta. Detaljar: [PRIVACY.md](PRIVACY.md).

## Fjerne det

Fjern `fontes`-oppføringa frå MCP-innstillingane i appen din (i Claude Code:
`claude mcp remove fontes`), og avslutt og opne appen på nytt.

## Greitt å vite

Fontes les offentlege kjelder, for det meste nettstadene til domstolar og styresmakter. Han merkjer uoffisielle kjelder i
svara sine. Opne alltid kjeldelenkja før du stolar på ei avgjerd eller ei føresegn.

Om noko går gale, send ein e-post om kva du gjorde og feilen du såg, til fontesmcp@proton.me.

## Før du stolar på det

- Fontes er eit researchverktøy, ikkje juridisk rådgjeving. Bruken gjer ikkje nokon til advokaten din.
- Han blir levert «som han er», utan garanti, og opphavspersonane er ikkje ansvarlege for korleis han blir brukt,
  så langt lova tillèt. Dei fullstendige vilkåra står i [lisensen](../../../LICENSE) (Apache 2.0).
