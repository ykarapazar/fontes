> See on masinabil tehtud tõlge. Autoriteetne on ingliskeelne versioon.

# API-võtmed

Peaaegu iga Fontese allikas töötab ilma võtmeta. Kaks vajavad tasuta võtit:

| Võti | Avab | Ilma selleta |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Prantsusmaa: Judilibre (kohtulahendid) ja Légifrance (õigusaktid) | Prantsusmaa on välja lülitatud. `list_jurisdictions` näitab seda mitteaktiivsena. |
| `WLM_US_GOVINFO_KEY` | Ameerika Ühendriigid: govinfo otsing (föderaalkohtute lahendid, Statutes at Large, public laws) | Fontes kasutab jagatud `DEMO_KEY`-d: umbes 10 otsingut päevas IP-aadressi kohta. Teadaoleva lahendi avamine ja US Code ei vaja võtit. |

Võtmed on valikulised. Saate need lisada hiljem.

## Võtme lisamine

**Paigaldajaga.** Paigaldamise ajal küsib paigaldaja, kas soovite võtmeid lisada. Valige
**Not now** (või vajutage Enter), et vahele jätta. Võtmete lisamiseks või muutmiseks hiljem käivitage **Add or change keys**:

- Mac: avage rakendus Fontes Installer uuesti ja valige **Add or change keys** või tehke paigaldaja kaustas
  topeltklõps failil `Add or change keys.command`.
- Windows: tehke paigaldaja kaustas topeltklõps failil `Add or change keys.cmd`. Windowsi
  paigaldusprogramm paneb selle, kui see on saadaval, ka menüüsse Start > Fontes.

Sisestatav tekst on peidetud. Iga võtme puhul: kleepige see, vajutage Enter, et olemasolev alles jätta, või sisestage `-`,
et see eemaldada. Võtmed lisatakse igasse rakendusse, kus Fontes juba on.

**Claude Desktopi laiendusega (.mcpb).** Avage Claude > Settings > Extensions > Fontes ja
täitke väljad. Kõik need on valikulised.

**Käsitsi.** Lisage muutujad oma rakenduse MCP-seadetes `fontes`-kirje plokki `env`:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Taaskäivitage rakendus pärast iga muudatust.

## Prantsusmaa: PISTE (tasuta)

1. Looge konto aadressil [piste.gouv.fr](https://piste.gouv.fr). See tähendab PISTE tingimuste (CGU) aktsepteerimist.
2. Minge API > **Consentement CGU API**. Aktsepteerige **JUDILIBRE** ja **Légifrance'i** (production) tingimused.
3. Looge **tootmisrakendus** (production application). Teie jaoks loodud `APP_SANDBOX` ei pääse tootmiskeskkonda.
   Märkige jaotises „Modifier l'application“ **JUDILIBRE (production)** ja **Légifrance (production)** ning rakendage.
4. Avage rakenduse vahekaart **Authentification**. Kopeerige `client_id` ja `client_secret`.
5. Käivitage **Add or change keys** ja kleepige need.

Tingimused lühidalt:

- Andmed: Licence Ouverte / Etalab 2.0. Taaskasutus, sh äriline taaskasutus, on lubatud allikale viidates.
- Ärge avaldage ega jagage oma pääsuandmeid. Teatage PISTE-le, kui need lekivad.
- Légifrance'i API on beetateenus. Selle võidakse peatada ja sellel on kvoodid (sekundis, minutis ja päevas).
- Légifrance'i tekstid ei ole autentne versioon. Autentne on ainult allkirjastatud Journal officiel'i PDF.
- Judilibre: ärge kasutage kohtunike ega kohtuametnike nimesid nende töö hindamiseks, võrdlemiseks ega ennustamiseks
  (Code de l'organisation judiciaire art. L111-13; kuritegu).
- Judilibre: järgige GDPR-i. Ärge püüdke pooli uuesti tuvastada.

Teie kvoodid on PISTE-s jaotises API Sélectionnées > Actions > Consulter les quotas.

## Ameerika Ühendriigid: api.data.gov (tasuta)

1. Minge aadressile [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (võti kuvatakse ekraanil)
   või [api.data.gov/signup](https://api.data.gov/signup/) (võti saadetakse teile e-postiga).
2. Sisestage oma nimi ja e-posti aadress. Väli „how will you use it“ on valikuline.
3. Kopeerige 40-märgiline võti.
4. Käivitage **Add or change keys** ja kleepige see USA võtmena.

Tingimused lühidalt:

- Oma võtmega lubab govinfo kuni 36 000 päringut tunnis.
- Me ei leidnud API-spetsiifilisi kasutustingimusi (api.data.gov/terms/ ei ole olemas). Kontrollimata.
  Vt [govinfo põhimõtteid](https://www.govinfo.gov/about/policies) ja
  [data.gov privaatsuspoliitikat](https://data.gov/privacy-policy/).
- Hoidke võti endale.

## Kus võtmeid hoitakse

- **Paigaldaja või käsitsi:** lihttekstina iga rakenduse MCP-seadete failis, `fontes`-kirje
  plokis `env`. Igaüks, kes saab teie kasutajafaile lugeda, saab lugeda ka võtmeid.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` või `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Claude Desktopi laiendus (.mcpb):** Claude hoiab neid välju oma seadetes ja kaitseb neid
  teie süsteemi turvalise salvestusega (Macis Keychain, Windowsis Credential Manager).

Enne iga muudatust salvestab paigaldaja seadete failist koopia selle kõrvale
(`<file>.fontes-backup-<time>`). Pärast võtmete lisamist tehtud koopiad sisaldavad samuti võtmeid. Kustutage vanad
koopiad, mida te ei vaja.

## Võtme muutmine või eemaldamine

- Käivitage **Add or change keys**. Kleepige uus võti, et see asendada, või sisestage `-`, et see eemaldada.
- Või muutke plokki `env` käsitsi ja taaskäivitage rakendus.
- Fontese eemaldamine eemaldab kogu selle kirje koos võtmetega. Varukoopiaid see ei kustuta.
- Kui võti on lekkinud, asendage see ka allikas: PISTE-s looge oma rakendusele uued pääsuandmed;
  api.data.gov-is registreeruge uue võtme saamiseks.

## Teated, mida võite näha

| Teade | Tähendus |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Prantsusmaa võtit pole. Lisage see. |
| `Inactive: needs a free PISTE account. ...` (`list_jurisdictions`-is) | Sama. |
| `PISTE refused the client credentials ...` | ID või saladus on vale või enam ei kehti. Kopeerige mõlemad uuesti vahekaardilt Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Teie rakendus ei ole seda API-t tellinud või te pole selle tingimusi aktsepteerinud. Vt samme 2 ja 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | USA võtit pole. Otsing töötab mõne päringu jaoks päevas. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Demovõti on ära kasutatud. Lisage oma võti. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Võti on vale või pole seda e-kirjast veel kinnitatud. |

Tühi väärtus tähendab, et võtit pole.

## Load (WLM_PERMITTED)

See ei ole API-võti ja paigaldaja seda ei määra. **Määrake see ainult siis, kui teil endal on
see luba.**

Mõned allikad on vaikimisi välja lülitatud, sest nende tingimused või robots.txt keelavad automatiseeritud kasutamise ilma
loata. Kui teil on avaldaja luba, lülitage allikas sisse, lisades selle koodi muutujasse
`WLM_PERMITTED`, komadega eraldatult, plokis `env`: `"WLM_PERMITTED": "in,de"`.

| Kood | Allikas |
|---|---|
| `az` | Aserbaidžaan: e-qanun.az (justiitsministeerium) |
| `bh` | Bahrein: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Colombia: Función Pública, Gestor Normativo (konsolideeritud õigusaktid) |
| `de` | Saksamaa: NeuRIS (föderaalne õigusteabe portaal, katseteenus) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Kreeka: National Printing Office, Government Gazette otsing (search.et.gr) |
| `in` | India: India Code (indiacode.gov.in) |
| `mu` | Mauritius: Supreme Court (supremecourt.govmu.org) |
| `sg` | Singapur: kohtuotsused (elitigation.sg) |

Ilma loata ütleb Fontes: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
