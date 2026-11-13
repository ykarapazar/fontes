> Dit is een machinaal ondersteunde vertaling. De Engelse versie is leidend.

# API-sleutels

Bijna elke bron in Fontes werkt zonder sleutel. Twee hebben een gratis sleutel nodig:

| Sleutel | Ontsluit | Zonder sleutel |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Frankrijk: Judilibre (rechterlijke uitspraken) en Légifrance (wetgeving) | Frankrijk staat uit. `list_jurisdictions` toont het als inactief. |
| `WLM_US_GOVINFO_KEY` | Verenigde Staten: zoeken in govinfo (uitspraken van federale gerechten, Statutes at Large, public laws) | Fontes gebruikt de gedeelde `DEMO_KEY`: ongeveer 10 zoekopdrachten per dag per IP-adres. Voor het openen van een bekende uitspraak en voor de US Code is geen sleutel nodig. |

Sleutels zijn optioneel. U kunt ze later toevoegen.

## Een sleutel toevoegen

**Met het installatieprogramma.** Tijdens de installatie vraagt het installatieprogramma of u
sleutels wilt toevoegen. Kies **Niet nu** (of druk op Enter) om over te slaan. Om later sleutels toe
te voegen of te wijzigen, voert u **Add or change keys** uit:

- Mac: open de app Fontes Installer opnieuw en kies **Sleutels toevoegen of wijzigen**, of
  dubbelklik op `Add or change keys.command` in de map van het installatieprogramma.
- Windows: dubbelklik op `Add or change keys.cmd` in de map van het installatieprogramma. Het
  Windows-installatieprogramma zet het, zodra het beschikbaar is, ook in Startmenu > Fontes.

Wat u typt blijft verborgen. Voor elke sleutel: plak hem, druk op Enter om te houden wat er staat,
of typ `-` om hem te verwijderen. De sleutels worden toegevoegd aan elke app die Fontes al heeft.

**Met de Claude Desktop-extensie (.mcpb).** Open Claude > Settings > Extensions > Fontes en vul de
velden in. Alle velden zijn optioneel.

**Met de hand.** Voeg de variabelen toe aan het `env`-blok van de vermelding `fontes` in de
MCP-configuratie van uw app:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Start de app na elke wijziging opnieuw.

## Frankrijk: PISTE (gratis)

1. Maak een account aan op [piste.gouv.fr](https://piste.gouv.fr). Daarmee aanvaardt u de
   gebruiksvoorwaarden van PISTE (CGU).
2. Ga naar API > **Consentement CGU API**. Aanvaard de voorwaarden voor **JUDILIBRE** en
   **Légifrance** (productie).
3. Maak een **productieapplicatie** aan. De `APP_SANDBOX` die voor u is aangemaakt, kan de productie
   niet bereiken. Vink onder "Modifier l'application" **JUDILIBRE (production)** en
   **Légifrance (production)** aan en pas de wijziging toe.
4. Open het tabblad **Authentification** van de applicatie. Kopieer de `client_id` en het
   `client_secret`.
5. Voer **Add or change keys** uit en plak ze.

De voorwaarden in het kort:

- Gegevens: Licence Ouverte / Etalab 2.0. Hergebruik, ook commercieel hergebruik, is toegestaan met
  bronvermelding.
- Publiceer of deel uw inloggegevens niet. Laat het PISTE weten als ze uitlekken.
- De Légifrance-API is een bètadienst. Die kan worden opgeschort en heeft quota (per seconde, minuut
  en dag).
- De teksten op Légifrance zijn niet de authentieke versie. Alleen de ondertekende pdf van het
  Journal officiel is dat.
- Judilibre: gebruik de namen van rechters of griffiers niet om hun werk te beoordelen, te vergelijken
  of te voorspellen (Code de l'organisation judiciaire art. L111-13; een strafbaar feit).
- Judilibre: leef de AVG na. Probeer de partijen niet opnieuw te identificeren.

Uw quota staan op PISTE onder API Sélectionnées > Actions > Consulter les quotas.

## Verenigde Staten: api.data.gov (gratis)

1. Ga naar [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (de sleutel wordt op het
   scherm getoond) of [api.data.gov/signup](https://api.data.gov/signup/) (de sleutel wordt u gemaild).
2. Vul uw naam en e-mailadres in. Het veld "how will you use it" is optioneel.
3. Kopieer de sleutel van 40 tekens.
4. Voer **Add or change keys** uit en plak hem als de sleutel voor de VS.

De voorwaarden in het kort:

- Met uw eigen sleutel staat govinfo tot 36.000 verzoeken per uur toe.
- We hebben geen gebruiksvoorwaarden gevonden die specifiek voor de API gelden (api.data.gov/terms/
  bestaat niet). Niet geverifieerd. Zie het [beleid van govinfo](https://www.govinfo.gov/about/policies)
  en het [privacybeleid van data.gov](https://data.gov/privacy-policy/).
- Houd de sleutel voor uzelf.

## Waar sleutels worden opgeslagen

- **Installatieprogramma of met de hand:** als platte tekst in het MCP-configuratiebestand van elke
  app, in het `env`-blok van de vermelding `fontes`. Iedereen die uw gebruikersbestanden kan lezen,
  kan de sleutels lezen.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` of `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Claude Desktop-extensie (.mcpb):** Claude bewaart deze velden in zijn instellingen en beschermt
  ze met de beveiligde opslag van uw systeem (Sleutelhanger op Mac, Referentiebeheer op Windows).

Voor elke wijziging slaat het installatieprogramma een kopie van het configuratiebestand ernaast op
(`<file>.fontes-backup-<time>`). Kopieën die zijn gemaakt nadat u sleutels hebt toegevoegd, bevatten
ook de sleutels. Verwijder oude kopieën die u niet nodig hebt.

## Een sleutel wijzigen of verwijderen

- Voer **Add or change keys** uit. Plak een nieuwe sleutel om hem te vervangen, of typ `-` om hem te
  verwijderen.
- Of bewerk het `env`-blok met de hand en start de app opnieuw.
- Bij het verwijderen van Fontes wordt de hele vermelding verwijderd, inclusief de sleutels. De
  reservekopieën worden niet verwijderd.
- Als een sleutel is uitgelekt, vervang hem dan ook bij de bron: maak op PISTE nieuwe inloggegevens
  voor uw app; vraag bij api.data.gov een nieuwe sleutel aan.

## Meldingen die u kunt zien

| Melding | Betekenis |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Geen sleutel voor Frankrijk. Voeg er een toe. |
| `Inactive: needs a free PISTE account. ...` (in `list_jurisdictions`) | Hetzelfde. |
| `PISTE refused the client credentials ...` | De ID of het secret is fout of niet meer geldig. Kopieer beide opnieuw van het tabblad Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Uw app is niet geabonneerd op die API, of u hebt de voorwaarden ervan niet aanvaard. Zie stap 2 en 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Geen sleutel voor de VS. Zoeken werkt voor een paar aanroepen per dag. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | De demosleutel is opgebruikt. Voeg uw eigen sleutel toe. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | De sleutel is fout, of nog niet bevestigd via de e-mail. |

Een lege waarde geldt als geen sleutel.

## Toestemmingen (WLM_PERMITTED)

Dit is geen API-sleutel, en het installatieprogramma stelt het niet in. **Stel het alleen in als u
die toestemming zelf hebt.**

Sommige bronnen staan standaard uit omdat hun voorwaarden of robots.txt geautomatiseerd gebruik
zonder toestemming verbieden. Als u toestemming van de uitgever hebt, zet u een bron aan door de
code ervan, gescheiden door komma's, aan `WLM_PERMITTED` in het `env`-blok toe te voegen:
`"WLM_PERMITTED": "in,de"`.

| Code | Bron |
|---|---|
| `az` | Azerbeidzjan: e-qanun.az (ministerie van Justitie) |
| `bh` | Bahrein: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Colombia: Función Pública, Gestor Normativo (geconsolideerde wetgeving) |
| `de` | Duitsland: NeuRIS (federaal portaal voor juridische informatie, proefdienst) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Griekenland: Nationale Drukkerij, zoeken in het Staatsblad (search.et.gr) |
| `in` | India: India Code (indiacode.gov.in) |
| `mu` | Mauritius: Supreme Court (supremecourt.govmu.org) |
| `sg` | Singapore: rechterlijke uitspraken (elitigation.sg) |

Zonder toestemming meldt Fontes: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
