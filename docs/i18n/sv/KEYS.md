> Detta är en maskinstödd översättning. Den engelska versionen gäller.

# API-nycklar

Nästan alla källor i Fontes fungerar utan nyckel. Tre kräver en kostnadsfri nyckel:

| Nyckel | Ger tillgång till | Utan den |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Frankrike: Judilibre (domstolsavgöranden) och Légifrance (lagstiftning) | Frankrike är avstängt. `list_jurisdictions` visar det som inaktivt. |
| `WLM_US_GOVINFO_KEY` | USA: govinfo-sökning (federala domstolsavgöranden, Statutes at Large, public laws) | Fontes använder den delade `DEMO_KEY`: omkring 10 sökningar om dagen per IP-adress. Att öppna ett känt avgörande och US Code kräver ingen nyckel. |
| `WLM_US_COURTLISTENER_KEY` | USA:s delstatsdomstolar (`us-states`): avgöranden från högsta och appellationsdomstolarna i alla 50 delstater och DC, från CourtListener | Delstaternas rättspraxis i USA är avstängd. `list_jurisdictions` visar den som inaktiv. |

Nycklar är valfria. Du kan lägga till dem senare.

## Lägga till en nyckel

**Med installationsprogrammet.** När Fontes har konfigurerats erbjuder installationsprogrammet att lägga till nycklar. På en Mac
klickar du på **Lägg till nycklar**, eller på **Klar** för att hoppa över; på Windows svarar du på frågan (tryck Enter för att hoppa över). För att lägga till eller ändra nycklar senare, kör **Add or change keys**:

- Mac: öppna appen Fontes Installer igen och välj **Lägg till eller ändra nycklar**.
- Windows: öppna Start-menyn, välj sedan **Fontes** → **Lägg till eller ändra nycklar**.

Det du skriver döljs. För varje nyckel: klistra in den, tryck Enter för att behålla det som finns, eller skriv `-` för att
ta bort den. Nycklarna läggs in i alla appar som redan har Fontes.

**Med tillägget för Claude Desktop (.mcpb).** Öppna Claude > Settings > Extensions > Fontes och
fyll i fälten. Alla är valfria.

**För hand.** Lägg till variablerna i `env`-blocket i posten `fontes` i appens MCP-konfiguration:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Starta om appen efter varje ändring.

## Frankrike: PISTE (kostnadsfritt)

1. Skapa ett konto på [piste.gouv.fr](https://piste.gouv.fr). Det innebär att du godkänner PISTE:s villkor (CGU).
2. Gå till API > **Consentement CGU API**. Godkänn villkoren för **JUDILIBRE** och **Légifrance** (produktion).
3. Skapa en **produktionsapplikation**. Den `APP_SANDBOX` som skapats åt dig når inte produktionsmiljön.
   Under ”Modifier l'application”, kryssa i **JUDILIBRE (production)** och **Légifrance (production)** och tillämpa sedan.
4. Öppna appens flik **Authentification**. Kopiera `client_id` och `client_secret`.
5. Kör **Add or change keys** och klistra in dem.

Villkoren i korthet:

- Data: Licence Ouverte / Etalab 2.0. Vidareutnyttjande, även kommersiellt, är tillåtet med angivande av källa.
- Publicera eller dela inte dina inloggningsuppgifter. Meddela PISTE om de läcker ut.
- Légifrance-API:t är en betatjänst. Det kan stängas av tillfälligt, och det har kvoter (per sekund, minut och dag).
- Légifrance-texterna är inte den autentiska versionen. Det är endast den signerade PDF-filen av Journal officiel.
- Judilibre: använd inte domares eller domstolshandläggares namn för att utvärdera, jämföra eller förutsäga deras arbete
  (Code de l'organisation judiciaire art. L111-13; ett brott).
- Judilibre: följ GDPR. Försök inte återidentifiera parterna.

Dina kvoter finns på PISTE under API Sélectionnées > Actions > Consulter les quotas.

## USA: api.data.gov (kostnadsfritt)

1. Gå till [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (nyckeln visas på skärmen)
   eller [api.data.gov/signup](https://api.data.gov/signup/) (nyckeln skickas till dig via e-post).
2. Ange ditt namn och din e-postadress. Fältet ”how will you use it” är valfritt.
3. Kopiera nyckeln på 40 tecken.
4. Kör **Add or change keys** och klistra in den som nyckel för USA.

Villkoren i korthet:

- Med en egen nyckel tillåter govinfo upp till 36 000 förfrågningar i timmen.
- Vi hittade inga API-specifika användarvillkor (api.data.gov/terms/ finns inte). Inte verifierat.
  Se [govinfos policyer](https://www.govinfo.gov/about/policies) och
  [data.govs integritetspolicy](https://data.gov/privacy-policy/).
- Håll nyckeln för dig själv.

## USA:s delstatsdomstolar: CourtListener (kostnadsfritt)

CourtListener drivs av [Free Law Project](https://free.law), en ideell organisation som sedan 2010 har samlat amerikanska domstolsavgöranden och gör dem kostnadsfria för alla. Enligt egna uppgifter innehåller den över nio miljoner avgöranden. Den är inte en officiell källa: domstolarna publicerar sina egna avgöranden, och CourtListener samlar in dem från domstolarnas webbplatser och inskannade rättsfallssamlingar. Varje svar från Fontes som kommer därifrån anger detta. Fontes är inte knutet till Free Law Project.

1. Skapa ett kostnadsfritt konto på [courtlistener.com](https://www.courtlistener.com/sign-in/).
2. Öppna din profil och kopiera din API-token.
3. Kör **Add or change keys** och klistra in den som nyckel för CourtListener.

Villkoren i korthet ([fullständiga villkor](https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies)):

- Token är enbart din: dela den inte, slå inte ihop den med andras och sälj inte vidare den, och använd inte flera konton.
- Du ansvarar för vad en AI-app gör med din token.
- Presentera inte en AI:s analys av deras data som framtagen, godkänd eller kontrollerad av Free Law Project.
- Ett kostnadsfritt konto tillåter 5 förfrågningar i minuten, 50 i timmen och 125 om dagen. En sökning är en förfrågan; att öppna ett avgörande är två. Ett medlemskap i Free Law Project höjer gränserna.
- CourtListener garanterar inte riktigheten. Kontrollera ett avgörande mot domstolens kopia innan du förlitar dig på det.

## Var nycklarna lagras

- **Med installationsprogrammet eller för hand:** som klartext i varje apps MCP-konfigurationsfil, i `env`-blocket i
  posten `fontes`. Alla som kan läsa dina användarfiler kan läsa nycklarna.
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
- **Tillägget för Claude Desktop (.mcpb):** Claude sparar dessa fält i sina inställningar och skyddar dem
  med systemets säkra lagring (Keychain på Mac, Credential Manager på Windows).

Före varje ändring sparar installationsprogrammet en kopia av konfigurationsfilen bredvid den
(`<file>.fontes-backup-<time>`). Kopior som gjorts efter att du lagt till nycklar innehåller också nycklarna. Radera gamla
kopior som du inte behöver.

## Ändra eller ta bort en nyckel

- Kör **Add or change keys**. Klistra in en ny nyckel för att ersätta den, eller skriv `-` för att ta bort den.
- Eller redigera `env`-blocket för hand och starta om appen.
- Avinstallation av Fontes tar bort hela dess post, nycklarna inräknade. Den raderar inte säkerhetskopiorna.
- Om en nyckel har läckt ut, ersätt den också hos källan: på PISTE, skapa nya inloggningsuppgifter för din app;
  för api.data.gov, registrera dig för en ny nyckel.

## Meddelanden du kan se

| Meddelande | Betydelse |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Ingen nyckel för Frankrike. Lägg till en. |
| `Inactive: needs a free PISTE account. ...` (i `list_jurisdictions`) | Samma sak. |
| `PISTE refused the client credentials ...` | ID:t eller hemligheten är fel eller inte längre giltig. Kopiera båda igen från fliken Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Din app abonnerar inte på det API:t, eller så har du inte godkänt dess villkor. Se steg 2 och 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Ingen nyckel för USA. Sökning fungerar för några anrop om dagen. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Demonyckeln är förbrukad. Lägg till en egen nyckel. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Nyckeln är fel, eller ännu inte bekräftad via e-postmeddelandet. |

Ett tomt värde räknas som ingen nyckel.

## Tillstånd (WLM_PERMITTED)

Detta är inte en API-nyckel, och installationsprogrammet anger den inte. **Ange den endast om du själv har
det tillståndet.**

Vissa källor är avstängda som standard eftersom deras villkor eller robots.txt förbjuder automatiserad användning utan
tillstånd. Om du har tillstånd från utgivaren, slå på en källa genom att lägga till dess kod i
`WLM_PERMITTED`, kommaseparerat, i `env`-blocket: `"WLM_PERMITTED": "in,de"`.

| Kod | Källa |
|---|---|
| `az` | Azerbajdzjan: e-qanun.az (justitieministeriet) |
| `bh` | Bahrain: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Colombia: Función Pública, Gestor Normativo (konsoliderad lagstiftning) |
| `de` | Tyskland: NeuRIS (federal portal för rättslig information, testtjänst) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Grekland: National Printing Office, sökning i Government Gazette (search.et.gr) |
| `in` | Indien: India Code (indiacode.gov.in) |
| `mu` | Mauritius: Supreme Court (supremecourt.govmu.org) |
| `sg` | Singapore: domstolsavgöranden (elitigation.sg) |

Utan tillstånd säger Fontes: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
