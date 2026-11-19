> Din hija traduzzjoni magħmula bl-għajnuna tal-magna. Il-verżjoni Ingliża hija dik awtorevoli.

# Ċwievet tal-API

Kważi kull sors f'Fontes jaħdem mingħajr ċavetta. Tnejn jeħtieġu waħda b'xejn:

| Ċavetta | X'tiftaħ | Mingħajrha |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Franza: Judilibre (deċiżjonijiet tal-qorti) u Légifrance (leġiżlazzjoni) | Franza hija mitfija. `list_jurisdictions` jurih bħala inattiv. |
| `WLM_US_GOVINFO_KEY` | Stati Uniti: tfittxija ta' govinfo (opinjonijiet tal-qrati federali, Statutes at Large, public laws) | Fontes juża ċ-ċavetta komuni `DEMO_KEY`: madwar 10 tfittxijiet kuljum għal kull indirizz IP. Il-ftuħ ta' deċiżjoni magħrufa u l-US Code ma jeħtiġux ċavetta. |

Iċ-ċwievet mhumiex obbligatorji. Tista' żżidhom aktar tard.

## Kif iżżid ċavetta

**Bl-installer.** Ladarba Fontes ikun issettjat, l-installer joffri li jżid iċ-ċwievet. Fuq Mac, agħfas
**Żid iċ-ċwievet**, jew **Lest** biex taqbeż; fuq Windows, wieġeb il-mistoqsija (agħfas Enter biex
taqbeż). Biex iżżid jew tibdel iċ-ċwievet aktar tard, ħaddem **Żid jew ibdel iċ-ċwievet**:

- Mac: erġa' iftaħ l-app Fontes Installer u agħżel **Żid jew ibdel iċ-ċwievet**.
- Windows: iftaħ il-menu Start, imbagħad **Fontes** → **Żid jew ibdel iċ-ċwievet**.

It-tajpjar huwa moħbi. Għal kull ċavetta: waħħalha, agħfas Enter biex iżżomm dik li hemm, jew
ikteb `-` biex tneħħiha. Iċ-ċwievet imorru f'kull app li diġà għandha Fontes.

**Bl-estensjoni ta' Claude Desktop (.mcpb).** Iftaħ Claude > Settings > Extensions > Fontes u
imla l-oqsma. Kollha mhumiex obbligatorji.

**Bl-idejn.** Żid il-varjabbli mal-blokk `env` tal-entrata `fontes` fil-konfigurazzjoni MCP
tal-app tiegħek:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Erġa' ibda l-app wara kull bidla.

## Franza: PISTE (b'xejn)

1. Oħloq kont fuq [piste.gouv.fr](https://piste.gouv.fr). Dan ifisser li taċċetta t-termini ta'
   PISTE (CGU).
2. Mur API > **Consentement CGU API**. Aċċetta t-termini għal **JUDILIBRE** u **Légifrance**
   (production).
3. Oħloq **production application**. L-`APP_SANDBOX` maħluqa għalik ma tistax tilħaq
   il-production. Taħt "Modifier l'application", immarka **JUDILIBRE (production)** u
   **Légifrance (production)**, imbagħad applika.
4. Iftaħ it-tab **Authentification** tal-app. Ikkopja l-`client_id` u l-`client_secret`.
5. Ħaddem **Add or change keys** u waħħalhom.

It-termini, fil-qosor:

- Data: Licence Ouverte / Etalab 2.0. L-użu mill-ġdid, inkluż l-użu mill-ġdid kummerċjali, huwa
  permess b'attribuzzjoni.
- Tippubblikax u taqsamx il-kredenzjali tiegħek. Għid lil PISTE jekk joħorġu.
- L-API ta' Légifrance hija servizz beta. Tista' tiġi sospiża, u għandha kwoti (kull sekonda,
  minuta u jum).
- It-testi ta' Légifrance mhumiex il-verżjoni awtentika. Huwa biss il-PDF iffirmat tal-Journal
  officiel.
- Judilibre: tużax l-ismijiet tal-imħallfin jew tar-reġistraturi biex tevalwa, tqabbel jew tbassar
  ix-xogħol tagħhom (Code de l'organisation judiciaire art. L111-13; reat kriminali).
- Judilibre: segwi l-GDPR. Tippruvax terġa' tidentifika l-partijiet.

Il-kwoti tiegħek jinsabu fuq PISTE taħt API Sélectionnées > Actions > Consulter les quotas.

## Stati Uniti: api.data.gov (b'xejn)

1. Mur fuq [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (iċ-ċavetta tidher
   fuq l-iskrin) jew [api.data.gov/signup](https://api.data.gov/signup/) (iċ-ċavetta tintbagħatlek
   b'email).
2. Daħħal ismek u l-email tiegħek. Il-qasam "how will you use it" mhuwiex obbligatorju.
3. Ikkopja ċ-ċavetta ta' 40 karattru.
4. Ħaddem **Add or change keys** u waħħalha bħala ċ-ċavetta tal-Istati Uniti.

It-termini, fil-qosor:

- Biċ-ċavetta tiegħek stess, govinfo jippermetti sa 36,000 talba fis-siegħa.
- Ma sibna l-ebda termini tas-servizz speċifiċi għall-API (api.data.gov/terms/ ma teżistix).
  Mhux ivverifikat. Ara [il-politiki ta' govinfo](https://www.govinfo.gov/about/policies) u
  [il-politika tal-privatezza ta' data.gov](https://data.gov/privacy-policy/).
- Żomm iċ-ċavetta għalik.

## Fejn jinħażnu ċ-ċwievet

- **Installer jew bl-idejn:** bħala test sempliċi fil-fajl tal-konfigurazzjoni MCP ta' kull app,
  fil-blokk `env` tal-entrata `fontes`. Kull min jista' jaqra l-fajls tal-utent tiegħek jista'
  jaqra ċ-ċwievet.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` jew `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Estensjoni ta' Claude Desktop (.mcpb):** Claude iżomm dawn l-oqsma fis-settings tiegħu u
  jipproteġihom bil-ħażna sigura tas-sistema tiegħek (Keychain fuq Mac, Credential Manager fuq
  Windows).

Qabel kull bidla, l-installer jissejvja kopja tal-fajl tal-konfigurazzjoni ħdejh
(`<file>.fontes-backup-<time>`). Il-kopji magħmula wara li żidt iċ-ċwievet fihom iċ-ċwievet
ukoll. Ħassar il-kopji qodma li m'għandekx bżonn.

## Kif tibdel jew tneħħi ċavetta

- Ħaddem **Add or change keys**. Waħħal ċavetta ġdida biex tissostitwiha, jew ikteb `-` biex
  tneħħiha.
- Jew editja l-blokk `env` bl-idejn u erġa' ibda l-app.
- Id-diżinstallazzjoni ta' Fontes tneħħi l-entrata kollha tiegħu, iċ-ċwievet inklużi. Ma tħassarx
  il-kopji ta' riżerva.
- Jekk ċavetta ħarġet, issostitwiha wkoll fis-sors: fuq PISTE, oħloq kredenzjali ġodda għall-app
  tiegħek; għal api.data.gov, irreġistra għal ċavetta ġdida.

## Messaġġi li tista' tara

| Messaġġ | Tifsira |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | M'hemmx ċavetta għal Franza. Żid waħda. |
| `Inactive: needs a free PISTE account. ...` (f'`list_jurisdictions`) | L-istess. |
| `PISTE refused the client credentials ...` | L-ID jew is-secret huma ħżiena jew m'għadhomx validi. Erġa' kkopja t-tnejn mit-tab Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | L-app tiegħek mhijiex abbonata għal dik l-API, jew ma aċċettajtx it-termini tagħha. Ara l-passi 2 u 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | M'hemmx ċavetta għall-Istati Uniti. It-tfittxija taħdem għal ftit sejħiet kuljum. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Iċ-ċavetta demo spiċċat. Żid iċ-ċavetta tiegħek stess. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Iċ-ċavetta hija ħażina, jew għadha mhix ikkonfermata mill-email. |

Valur vojt jitqies bħala l-ebda ċavetta.

## Permessi (WLM_PERMITTED)

Din mhijiex ċavetta tal-API, u l-installer ma jissettjahiex. **Issettjaha biss jekk int stess
għandek dak il-permess.**

Xi sorsi huma mitfija b'mod awtomatiku għax it-termini jew ir-robots.txt tagħhom jipprojbixxu
l-użu awtomatizzat mingħajr permess. Jekk għandek il-permess mill-pubblikatur, ixgħel sors billi
żżid il-kodiċi tiegħu ma' `WLM_PERMITTED`, separati b'virgola, fil-blokk `env`:
`"WLM_PERMITTED": "in,de"`.

| Kodiċi | Sors |
|---|---|
| `az` | Ażerbajġan: e-qanun.az (Ministeru tal-Ġustizzja) |
| `bh` | Baħrejn: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Kolombja: Función Pública, Gestor Normativo (leġiżlazzjoni konsolidata) |
| `de` | Ġermanja: NeuRIS (portal federali tal-informazzjoni legali, servizz ta' prova) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Greċja: National Printing Office, tfittxija fil-Gazzetta tal-Gvern (search.et.gr) |
| `in` | Indja: India Code (indiacode.gov.in) |
| `mu` | Mawrizju: Qorti Suprema (supremecourt.govmu.org) |
| `sg` | Singapor: sentenzi tal-qrati (elitigation.sg) |

Mingħajr permess, Fontes jgħid: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
