> Dette er en maskinstøttet oversættelse. Den engelske version er den gældende.

# API-nøgler

Næsten alle kilder i Fontes virker uden nøgle. To kræver en gratis nøgle:

| Nøgle | Giver adgang til | Uden den |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Frankrig: Judilibre (retsafgørelser) og Légifrance (lovgivning) | Frankrig er slået fra. `list_jurisdictions` viser det som inaktivt. |
| `WLM_US_GOVINFO_KEY` | USA: søgning i govinfo (domme fra føderale domstole, Statutes at Large, public laws) | Fontes bruger den delte `DEMO_KEY`: omkring 10 søgninger om dagen pr. IP-adresse. At åbne en kendt afgørelse og US Code kræver ingen nøgle. |

Nøgler er valgfrie. Du kan tilføje dem senere.

## Tilføj en nøgle

**Med installationsprogrammet.** Under installationen spørger installationsprogrammet, om du vil
tilføje nøgler. Vælg **Ikke nu** (eller tryk Enter) for at springe over. For at tilføje eller
ændre nøgler senere skal du køre **Add or change keys**:

- Mac: åbn appen Fontes Installer igen, og vælg **Tilføj eller skift nøgler**, eller dobbeltklik på
  `Add or change keys.command` i installationsprogrammets mappe.
- Windows: dobbeltklik på `Add or change keys.cmd` i installationsprogrammets mappe. Windows-
  installationsprogrammet lægger den også i Start menu > Fontes, når det er tilgængeligt.

Det, du skriver, vises ikke. For hver nøgle: indsæt den, tryk Enter for at beholde det, der er
der, eller skriv `-` for at fjerne den. Nøglerne tilføjes i alle apps, der allerede har Fontes.

**Med Claude Desktop-udvidelsen (.mcpb).** Åbn Claude > Settings > Extensions > Fontes, og udfyld
felterne. De er alle valgfrie.

**Manuelt.** Læg variablerne i `env`-blokken i posten `fontes` i din apps MCP-konfiguration:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Genstart appen efter hver ændring.

## Frankrig: PISTE (gratis)

1. Opret en konto på [piste.gouv.fr](https://piste.gouv.fr). Dermed accepterer du PISTE's vilkår
   (CGU).
2. Gå til API > **Consentement CGU API**. Acceptér vilkårene for **JUDILIBRE** og
   **Légifrance** (produktion).
3. Opret en **produktionsapplikation**. Den `APP_SANDBOX`, der blev oprettet til dig, kan ikke nå
   produktionsmiljøet. Under "Modifier l'application" skal du markere **JUDILIBRE (production)** og
   **Légifrance (production)** og anvende ændringen.
4. Åbn applikationens fane **Authentification**. Kopiér `client_id` og `client_secret`.
5. Kør **Add or change keys**, og indsæt dem.

Vilkårene kort fortalt:

- Data: Licence Ouverte / Etalab 2.0. Genbrug, også kommercielt, er tilladt med kildeangivelse.
- Offentliggør eller del ikke dine adgangsoplysninger. Giv PISTE besked, hvis de er blevet
  offentlige.
- Légifrance-API'et er en betatjeneste. Den kan blive suspenderet og har kvoter (pr. sekund,
  minut og dag).
- Teksterne på Légifrance er ikke den autentiske version. Det er kun den underskrevne PDF af
  Journal officiel.
- Judilibre: brug ikke navne på dommere eller justitssekretærer (greffiers) til at vurdere,
  sammenligne eller forudsige deres arbejde (Code de l'organisation judiciaire art. L111-13; en
  strafbar handling).
- Judilibre: overhold GDPR. Forsøg ikke at genidentificere parterne.

Din kvote finder du på PISTE under API Sélectionnées > Actions > Consulter les quotas.

## USA: api.data.gov (gratis)

1. Gå til [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (nøglen vises på
   skærmen) eller [api.data.gov/signup](https://api.data.gov/signup/) (nøglen sendes til dig på
   e-mail).
2. Angiv dit navn og din e-mailadresse. Feltet "how will you use it" er valgfrit.
3. Kopiér nøglen på 40 tegn.
4. Kør **Add or change keys**, og indsæt den som US-nøglen.

Vilkårene kort fortalt:

- Med din egen nøgle tillader govinfo op til 36.000 forespørgsler i timen.
- Vi har ikke fundet brugsvilkår specifikt for API'et (api.data.gov/terms/ findes ikke).
  Ikke verificeret. Se [govinfos politikker](https://www.govinfo.gov/about/policies) og
  [data.govs privatlivspolitik](https://data.gov/privacy-policy/).
- Hold nøglen for dig selv.

## Hvor nøglerne gemmes

- **Installationsprogram eller manuelt:** i klartekst i hver apps MCP-konfigurationsfil, i
  `env`-blokken i posten `fontes`. Enhver, der kan læse dine brugerfiler, kan læse nøglerne.
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
- **Claude Desktop-udvidelsen (.mcpb):** Claude opbevarer disse felter i sine indstillinger og
  beskytter dem med dit systems sikre lager (Keychain på Mac, Credential Manager på Windows).

Før hver ændring gemmer installationsprogrammet en kopi af konfigurationsfilen ved siden af den
(`<file>.fontes-backup-<time>`). Kopier, der er lavet, efter at du har tilføjet nøgler, indeholder
også nøglerne. Slet gamle kopier, du ikke har brug for.

## Ændr eller fjern en nøgle

- Kør **Add or change keys**. Indsæt en ny nøgle for at erstatte den, eller skriv `-` for at
  fjerne den.
- Eller redigér `env`-blokken manuelt, og genstart appen.
- Når du afinstallerer Fontes, fjernes hele posten, inklusive nøglerne. Sikkerhedskopierne
  slettes ikke.
- Hvis en nøgle er blevet offentlig, så erstat den også hos kilden: opret nye
  adgangsoplysninger til din app på PISTE; anmod om en ny nøgle hos api.data.gov.

## Meddelelser, du kan se

| Meddelelse | Betydning |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Ingen nøgle til Frankrig. Tilføj en. |
| `Inactive: needs a free PISTE account. ...` (i `list_jurisdictions`) | Det samme. |
| `PISTE refused the client credentials ...` | ID'et eller secret er forkert eller ikke længere gyldigt. Kopiér begge igen fra fanen Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Din app abonnerer ikke på dette API, eller du har ikke accepteret dets vilkår. Se trin 2 og 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Ingen US-nøgle. Søgning virker for nogle få kald om dagen. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Demonøglen er brugt op. Tilføj din egen nøgle. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Nøglen er forkert eller endnu ikke bekræftet via e-mailen. |

En tom værdi tæller som ingen nøgle.

## Tilladelser (WLM_PERMITTED)

Dette er ikke en API-nøgle, og installationsprogrammet sætter den ikke. **Sæt den kun, hvis du
selv har denne tilladelse.**

Nogle kilder er slået fra som standard, fordi deres vilkår eller deres robots.txt forbyder
automatiseret brug uden tilladelse. Hvis du har udgiverens tilladelse, slår du en kilde til ved
at tilføje dens kode, adskilt med kommaer, til `WLM_PERMITTED` i `env`-blokken:
`"WLM_PERMITTED": "in,de"`.

| Kode | Kilde |
|---|---|
| `az` | Aserbajdsjan: e-qanun.az (justitsministeriet) |
| `bh` | Bahrain: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Colombia: Función Pública, Gestor Normativo (konsolideret lovgivning) |
| `de` | Tyskland: NeuRIS (føderal portal for juridisk information, testtjeneste) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Grækenland: Statstrykkeriet, søgning i lovtidenden (search.et.gr) |
| `in` | Indien: India Code (indiacode.gov.in) |
| `mu` | Mauritius: Supreme Court (supremecourt.govmu.org) |
| `sg` | Singapore: domstolenes domme (elitigation.sg) |

Uden tilladelse siger Fontes: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
