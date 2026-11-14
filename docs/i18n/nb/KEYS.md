> Dette er en maskinassistert oversettelse. Den engelske versjonen er den gjeldende.

# API-nøkler

Nesten alle kilder i Fontes fungerer uten nøkkel. To krever en gratis nøkkel:

| Nøkkel | Gir tilgang til | Uten den |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Frankrike: Judilibre (rettsavgjørelser) og Légifrance (lovgivning) | Frankrike er slått av. `list_jurisdictions` viser det som inaktivt. |
| `WLM_US_GOVINFO_KEY` | USA: søk i govinfo (avgjørelser fra føderale domstoler, Statutes at Large, public laws) | Fontes bruker den delte `DEMO_KEY`: rundt 10 søk om dagen per IP-adresse. Å åpne en kjent avgjørelse og US Code krever ingen nøkkel. |

Nøkler er valgfrie. Du kan legge dem til senere.

## Legge til en nøkkel

**Med installasjonsprogrammet.** Når Fontes er satt opp, tilbyr installasjonsprogrammet å legge
til nøkler. På en Mac klikker du på **Legg til nøkler**, eller **Ferdig** for å hoppe over; på
Windows svarer du på spørsmålet (trykk Enter for å hoppe over). For å legge til eller endre
nøkler senere kjører du **Add or change keys**:

- Mac: åpne appen Fontes Installer igjen og velg **Legg til eller endre nøkler**.
- Windows: dobbeltklikk på `Add or change keys.cmd` i mappen til installasjonsprogrammet.
  Windows-installasjonsprogrammet legger den også i Start menu > Fontes når det er tilgjengelig.

Det du skriver, vises ikke. For hver nøkkel: lim den inn, trykk Enter for å beholde det som står
der, eller skriv `-` for å fjerne den. Nøklene legges til i alle apper som allerede har Fontes.

**Med Claude Desktop-utvidelsen (.mcpb).** Åpne Claude > Settings > Extensions > Fontes, og fyll
ut feltene. Alle er valgfrie.

**For hånd.** Legg variablene i `env`-blokken i oppføringen `fontes` i MCP-konfigurasjonen til
appen din:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Start appen på nytt etter hver endring.

## Frankrike: PISTE (gratis)

1. Opprett en konto på [piste.gouv.fr](https://piste.gouv.fr). Dermed godtar du vilkårene til
   PISTE (CGU).
2. Gå til API > **Consentement CGU API**. Godta vilkårene for **JUDILIBRE** og **Légifrance**
   (produksjon).
3. Opprett en **produksjonsapplikasjon**. `APP_SANDBOX`, som ble opprettet for deg, når ikke
   produksjonsmiljøet. Under "Modifier l'application" krysser du av for **JUDILIBRE (production)**
   og **Légifrance (production)** og tar i bruk endringen.
4. Åpne fanen **Authentification** for applikasjonen. Kopier `client_id` og `client_secret`.
5. Kjør **Add or change keys**, og lim dem inn.

Vilkårene kort fortalt:

- Data: Licence Ouverte / Etalab 2.0. Gjenbruk, også kommersielt, er tillatt med kildehenvisning.
- Ikke publiser eller del tilgangsopplysningene dine. Si fra til PISTE hvis de har blitt kjent
  for offentligheten.
- Légifrance-API-et er en betatjeneste. Den kan bli suspendert og har kvoter (per sekund, minutt
  og dag).
- Tekstene på Légifrance er ikke den autentiske versjonen. Det er bare den signerte PDF-en av
  Journal officiel.
- Judilibre: ikke bruk navn på dommere eller domstolsekretærer (greffiers) til å vurdere,
  sammenligne eller forutsi arbeidet deres (Code de l'organisation judiciaire art. L111-13; en
  straffbar handling).
- Judilibre: følg GDPR. Ikke prøv å identifisere partene på nytt.

Kvoten din finner du på PISTE under API Sélectionnées > Actions > Consulter les quotas.

## USA: api.data.gov (gratis)

1. Gå til [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (nøkkelen vises på
   skjermen) eller [api.data.gov/signup](https://api.data.gov/signup/) (nøkkelen sendes til deg
   på e-post).
2. Skriv inn navnet ditt og e-postadressen din. Feltet "how will you use it" er valgfritt.
3. Kopier nøkkelen på 40 tegn.
4. Kjør **Add or change keys**, og lim den inn som US-nøkkelen.

Vilkårene kort fortalt:

- Med din egen nøkkel tillater govinfo opptil 36 000 forespørsler i timen.
- Vi har ikke funnet bruksvilkår spesifikt for API-et (api.data.gov/terms/ finnes ikke). Ikke
  verifisert. Se [retningslinjene til govinfo](https://www.govinfo.gov/about/policies) og
  [personvernerklæringen til data.gov](https://data.gov/privacy-policy/).
- Hold nøkkelen for deg selv.

## Hvor nøklene lagres

- **Installasjonsprogram eller for hånd:** i klartekst i MCP-konfigurasjonsfilen til hver app, i
  `env`-blokken i oppføringen `fontes`. Alle som kan lese brukerfilene dine, kan lese nøklene.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` eller `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Claude Desktop-utvidelsen (.mcpb):** Claude oppbevarer disse feltene i innstillingene sine og
  beskytter dem med systemets sikre lager (Keychain på Mac, Credential Manager på Windows).

Før hver endring lagrer installasjonsprogrammet en kopi av konfigurasjonsfilen ved siden av den
(`<file>.fontes-backup-<time>`). Kopier som er laget etter at du la til nøkler, inneholder også
nøklene. Slett gamle kopier du ikke trenger.

## Endre eller fjerne en nøkkel

- Kjør **Add or change keys**. Lim inn en ny nøkkel for å erstatte den, eller skriv `-` for å
  fjerne den.
- Eller rediger `env`-blokken for hånd, og start appen på nytt.
- Når du avinstallerer Fontes, fjernes hele oppføringen, inkludert nøklene. Sikkerhetskopiene
  slettes ikke.
- Hvis en nøkkel har blitt kjent for offentligheten, erstatt den også hos kilden: opprett nye
  tilgangsopplysninger for appen din på PISTE; be om en ny nøkkel hos api.data.gov.

## Meldinger du kan se

| Melding | Betydning |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Ingen nøkkel for Frankrike. Legg til en. |
| `Inactive: needs a free PISTE account. ...` (i `list_jurisdictions`) | Det samme. |
| `PISTE refused the client credentials ...` | ID-en eller secret er feil eller ikke lenger gyldig. Kopier begge på nytt fra fanen Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Appen din abonnerer ikke på dette API-et, eller du har ikke godtatt vilkårene for det. Se trinn 2 og 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Ingen US-nøkkel. Søk fungerer for noen få kall om dagen. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Demonøkkelen er brukt opp. Legg til din egen nøkkel. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Nøkkelen er feil eller ennå ikke bekreftet via e-posten. |

En tom verdi regnes som ingen nøkkel.

## Tillatelser (WLM_PERMITTED)

Dette er ikke en API-nøkkel, og installasjonsprogrammet setter den ikke. **Sett den bare hvis du
selv har denne tillatelsen.**

Noen kilder er slått av som standard fordi vilkårene eller robots.txt-en deres forbyr automatisert
bruk uten tillatelse. Hvis du har utgiverens tillatelse, slår du på en kilde ved å legge koden
dens, atskilt med komma, til `WLM_PERMITTED` i `env`-blokken: `"WLM_PERMITTED": "in,de"`.

| Kode | Kilde |
|---|---|
| `az` | Aserbajdsjan: e-qanun.az (justisdepartementet) |
| `bh` | Bahrain: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Colombia: Función Pública, Gestor Normativo (konsolidert lovgivning) |
| `de` | Tyskland: NeuRIS (føderal portal for juridisk informasjon, testtjeneste) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Hellas: Statstrykkeriet, søk i lovtidenden (search.et.gr) |
| `in` | India: India Code (indiacode.gov.in) |
| `mu` | Mauritius: Supreme Court (supremecourt.govmu.org) |
| `sg` | Singapore: domstolenes avgjørelser (elitigation.sg) |

Uten tillatelse sier Fontes: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
