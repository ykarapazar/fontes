> Dette er ei maskinassistert omsetjing. Den engelske versjonen er den gjeldande.

# API-nøklar

Nesten alle kjelder i Fontes verkar utan nøkkel. To krev ein gratis nøkkel:

| Nøkkel | Gjev tilgang til | Utan han |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Frankrike: Judilibre (rettsavgjerder) og Légifrance (lovgjeving) | Frankrike er av. `list_jurisdictions` viser det som inaktivt. |
| `WLM_US_GOVINFO_KEY` | USA: søk i govinfo (avgjerder frå føderale domstolar, Statutes at Large, public laws) | Fontes brukar den delte `DEMO_KEY`: om lag 10 søk om dagen per IP-adresse. Å opne ei kjend avgjerd og US Code krev ingen nøkkel. |

Nøklane er valfrie. Du kan leggje dei til seinare.

## Leggje til ein nøkkel

**Med installasjonsprogrammet.** Når Fontes er sett opp, tilbyr installasjonsprogrammet å leggje til
nøklar. På Mac klikkar du på **Legg til nøklar**, eller **Ferdig** for å hoppe over; på Windows
svarar du på spørsmålet (trykk Enter for å hoppe over). For å leggje til eller endre nøklar seinare,
køyr **Add or change keys**:

- Mac: opne Fontes Installer-appen igjen og vel **Legg til eller endre nøklar**.
- Windows: dobbeltklikk på `Add or change keys.cmd` i installasjonsmappa. Installasjonsprogrammet for Windows
  legg han òg, når det blir tilgjengeleg, i Start-menyen > Fontes.

Det du skriv, blir ikkje vist. For kvar nøkkel: lim han inn, trykk Enter for å behalde det som står der, eller skriv `-` for å
fjerne han. Nøklane går inn i alle appar som allereie har Fontes.

**Med Claude Desktop-utvidinga (.mcpb).** Opne Claude > Settings > Extensions > Fontes og
fyll ut felta. Alle er valfrie.

**For hand.** Legg variablane til i `env`-blokka i `fontes`-oppføringa i MCP-konfigurasjonen til appen din:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Start appen på nytt etter kvar endring.

## Frankrike: PISTE (gratis)

1. Opprett ein konto på [piste.gouv.fr](https://piste.gouv.fr). Det inneber å godta vilkåra til PISTE (CGU).
2. Gå til API > **Consentement CGU API**. Godta vilkåra for **JUDILIBRE** og **Légifrance** (produksjon).
3. Opprett ein **produksjonsapplikasjon**. `APP_SANDBOX` som er laga for deg, kan ikkje nå produksjon.
   Under «Modifier l'application», kryss av for **JUDILIBRE (production)** og **Légifrance (production)**, og bruk endringa.
4. Opne fana **Authentification** for appen. Kopier `client_id` og `client_secret`.
5. Køyr **Add or change keys** og lim dei inn.

Vilkåra, kort sagt:

- Data: Licence Ouverte / Etalab 2.0. Vidarebruk, òg kommersiell vidarebruk, er tillaten med kjeldetilvising.
- Ikkje publiser eller del påloggingsopplysningane dine. Sei frå til PISTE om dei lek ut.
- Légifrance-API-et er ei betateneste. Det kan bli stansa, og det har kvotar (per sekund, minutt og dag).
- Légifrance-tekstane er ikkje den autentiske versjonen. Berre den signerte PDF-en av Journal officiel er det.
- Judilibre: ikkje bruk namna på dommarar eller rettsskrivarar til å vurdere, samanlikne eller føreseie arbeidet deira
  (Code de l'organisation judiciaire art. L111-13; ei straffbar handling).
- Judilibre: følg GDPR. Ikkje prøv å identifisere partane på nytt.

Kvotane dine finn du på PISTE under API Sélectionnées > Actions > Consulter les quotas.

## USA: api.data.gov (gratis)

1. Gå til [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (nøkkelen blir vist på skjermen)
   eller [api.data.gov/signup](https://api.data.gov/signup/) (nøkkelen blir send til deg på e-post).
2. Skriv inn namn og e-postadresse. Feltet «how will you use it» er valfritt.
3. Kopier nøkkelen på 40 teikn.
4. Køyr **Add or change keys** og lim han inn som USA-nøkkelen.

Vilkåra, kort sagt:

- Med din eigen nøkkel tillèt govinfo opptil 36 000 førespurnader i timen.
- Vi fann ingen API-spesifikke tenestevilkår (api.data.gov/terms/ finst ikkje). Ikkje verifisert.
  Sjå [retningslinjene til govinfo](https://www.govinfo.gov/about/policies) og
  [personvernerklæringa til data.gov](https://data.gov/privacy-policy/).
- Hald nøkkelen for deg sjølv.

## Kvar nøklane blir lagra

- **Installasjonsprogram eller for hand:** som rein tekst i MCP-konfigurasjonsfila til kvar app, i `env`-blokka i
  `fontes`-oppføringa. Alle som kan lese brukarfilene dine, kan lese nøklane.
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
- **Claude Desktop-utvidinga (.mcpb):** Claude held desse felta i innstillingane sine og vernar dei
  med den sikre lagringa i systemet ditt (Keychain på Mac, Credential Manager på Windows).

Før kvar endring lagrar installasjonsprogrammet ein kopi av konfigurasjonsfila ved sida av
(`<file>.fontes-backup-<time>`). Kopiar laga etter at du la til nøklar, inneheld òg nøklane. Slett gamle
kopiar du ikkje treng.

## Endre eller fjerne ein nøkkel

- Køyr **Add or change keys**. Lim inn ein ny nøkkel for å erstatte han, eller skriv `-` for å fjerne han.
- Eller rediger `env`-blokka for hand og start appen på nytt.
- Avinstallerer du Fontes, blir heile oppføringa fjerna, nøklane medrekna. Tryggingskopiane blir ikkje sletta.
- Om ein nøkkel har lekt ut, byt han òg ut ved kjelda: på PISTE, lag nye påloggingsopplysningar for appen din;
  for api.data.gov, registrer deg for ein ny nøkkel.

## Meldingar du kan sjå

| Melding | Tyding |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Ingen nøkkel for Frankrike. Legg til ein. |
| `Inactive: needs a free PISTE account. ...` (i `list_jurisdictions`) | Det same. |
| `PISTE refused the client credentials ...` | ID-en eller løyndomen er feil eller ikkje lenger gyldig. Kopier begge på nytt frå fana Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Appen din abonnerer ikkje på det API-et, eller du har ikkje godteke vilkåra for det. Sjå steg 2 og 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Ingen USA-nøkkel. Søk verkar for nokre få kall om dagen. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Demonøkkelen er brukt opp. Legg til din eigen nøkkel. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Nøkkelen er feil, eller ikkje stadfesta frå e-posten enno. |

Ein tom verdi tel som ingen nøkkel.

## Løyve (WLM_PERMITTED)

Dette er ikkje ein API-nøkkel, og installasjonsprogrammet set han ikkje. **Set han berre om du sjølv har
det løyvet.**

Somme kjelder er av som standard fordi vilkåra eller robots.txt deira forbyr automatisert bruk utan
løyve. Om du har løyve frå utgjevaren, slå på ei kjelde ved å leggje koden hennar til i
`WLM_PERMITTED`, skilde med komma, i `env`-blokka: `"WLM_PERMITTED": "in,de"`.

| Kode | Kjelde |
|---|---|
| `az` | Aserbajdsjan: e-qanun.az (justisdepartementet) |
| `bh` | Bahrain: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Colombia: Función Pública, Gestor Normativo (konsolidert lovgjeving) |
| `de` | Tyskland: NeuRIS (føderal rettsinformasjonsportal, prøveteneste) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Hellas: National Printing Office, søk i Government Gazette (search.et.gr) |
| `in` | India: India Code (indiacode.gov.in) |
| `mu` | Mauritius: Supreme Court (supremecourt.govmu.org) |
| `sg` | Singapore: domstolsavgjerder (elitigation.sg) |

Utan løyve seier Fontes: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
