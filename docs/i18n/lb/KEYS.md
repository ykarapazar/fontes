> Dëst ass eng maschinnegestëtzt Iwwersetzung. Déi englesch Versioun ass moossgeblech.

# API-Schlësselen

Bal all Quell a Fontes funktionéiert ouni Schlëssel. Zwou brauchen e gratis Schlëssel:

| Schlëssel | Mécht zougänglech | Ouni en |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Frankräich: Judilibre (Geriichtsentscheedungen) a Légifrance (Gesetzgebung) | Frankräich ass aus. `list_jurisdictions` weist et als inaktiv. |
| `WLM_US_GOVINFO_KEY` | Vereenegt Staaten: Sich a govinfo (Uerteeler vu Bundesgeriichter, Statutes at Large, public laws) | Fontes benotzt de gedeelten `DEMO_KEY`: ongeféier 10 Sichen den Dag pro IP-Adress. Fir eng bekannt Entscheedung opzemaachen a fir den US Code brauch een kee Schlëssel. |

Schlëssele sinn fakultativ. Dir kënnt se méi spéit derbäisetzen.

## E Schlëssel derbäisetzen

**Mam Installatiounsprogramm.** Soubal Fontes ageriicht ass, proposéiert den Installatiounsprogramm,
Schlësselen derbäizesetzen. Op engem Mac klickt op **Schlësselen derbäisetzen**, oder op **Fäerdeg**,
fir ze iwwersprangen; op Windows beäntwert d'Fro (dréckt Enter, fir ze iwwersprangen). Fir méi
spéit Schlësselen derbäizesetzen oder z'änneren, lafe loosst **Add or change keys**:

- Mac: Maacht d'App Fontes Installer nees op a wielt **Schlësselen derbäisetzen oder änneren**.
- Windows: Klickt duebel op `Add or change keys.cmd` am Dossier vum Installatiounsprogramm. De
  Windows-Setup-Programm setzt et, soubal en disponibel ass, och an Start menu > Fontes.

Wat Dir tippt, bleift verstoppt. Fir all Schlëssel: fügt en an, dréckt Enter, fir dat ze halen,
wat do ass, oder tippt `-`, fir en ze läschen. D'Schlësselen ginn an all App derbäigesat, déi
Fontes schonn huet.

**Mat der Claude-Desktop-Extensioun (.mcpb).** Maacht Claude > Settings > Extensions > Fontes op a
fëllt d'Felder aus. Si sinn all fakultativ.

**Mat der Hand.** Setzt d'Variabelen an den `env`-Block vun der Entrée `fontes` an der
MCP-Konfiguratioun vun Ärer App:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Start d'App no all Ännerung nei.

## Frankräich: PISTE (gratis)

1. Maacht e Kont op [piste.gouv.fr](https://piste.gouv.fr) op. Domat akzeptéiert Dir d'Konditioune
   vu PISTE (CGU).
2. Gitt op API > **Consentement CGU API**. Akzeptéiert d'Konditioune fir **JUDILIBRE** a
   **Légifrance** (Produktioun).
3. Erstellt eng **Produktiounsapplikatioun**. D'`APP_SANDBOX`, déi fir Iech erstallt gouf, kann
   d'Produktioun net erreechen. Kräizt ënner "Modifier l'application" **JUDILIBRE (production)** an
   **Légifrance (production)** un, an iwwerhuelt d'Ännerung.
4. Maacht den Tab **Authentification** vun der Applikatioun op. Kopéiert d'`client_id` an
   d'`client_secret`.
5. Loosst **Add or change keys** lafen a fügt se an.

D'Konditiounen, kuerz gesot:

- Donnéeën: Licence Ouverte / Etalab 2.0. D'Weiderverwäertung, och kommerziell, ass mat
  Quellenugab erlaabt.
- Publizéiert oder deelt Är Zougangsdonnéeë net. Sot PISTE Bescheed, wa se un d'Ëffentlechkeet
  komm sinn.
- D'Légifrance-API ass e Beta-Service. E ka suspendéiert ginn an huet Quoten (pro Sekonn, Minutt
  an Dag).
- D'Texter op Légifrance sinn net déi authentesch Versioun. Just den ënnerschriwwene PDF vum
  Journal officiel ass et.
- Judilibre: Benotzt d'Nimm vu Riichter oder Greffieren net, fir hir Aarbecht ze bewäerten, ze
  vergläichen oder virauszesoen (Code de l'organisation judiciaire Art. L111-13; eng Strofdot).
- Judilibre: Respektéiert d'DSGVO. Probéiert net, d'Parteien erëm z'identifizéieren.

Är Quote fannt Dir op PISTE ënner API Sélectionnées > Actions > Consulter les quotas.

## Vereenegt Staaten: api.data.gov (gratis)

1. Gitt op [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (de Schlëssel gëtt um
   Bildschierm gewisen) oder op [api.data.gov/signup](https://api.data.gov/signup/) (de Schlëssel
   gëtt Iech gemailt).
2. Gitt Ären Numm an Är E-Mail-Adress an. D'Feld "how will you use it" ass fakultativ.
3. Kopéiert de Schlëssel vu 40 Zeechen.
4. Loosst **Add or change keys** lafen a fügt en als US-Schlëssel an.

D'Konditiounen, kuerz gesot:

- Mat Ärem eegene Schlëssel erlaabt govinfo bis zu 36.000 Ufroen an der Stonn.
- Mir hu keng Notzungskonditioune fonnt, déi speziell fir d'API gëllen (api.data.gov/terms/
  existéiert net). Net verifizéiert. Kuckt d'[Richtlinne vu govinfo](https://www.govinfo.gov/about/policies)
  an d'[Dateschutzrichtlinn vun data.gov](https://data.gov/privacy-policy/).
- Haalt de Schlëssel fir Iech.

## Wou d'Schlësselen gespäichert ginn

- **Installatiounsprogramm oder mat der Hand:** als Kloertext am MCP-Konfiguratiounsfichier vun all
  App, am `env`-Block vun der Entrée `fontes`. Jiddereen, deen Är Benotzerfichieren liese kann, kann
  d'Schlësselen liesen.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` oder `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Claude-Desktop-Extensioun (.mcpb):** Claude hält dës Felder a sengen Astellungen a schützt se
  mat dem sécheren Späicher vun Ärem System (Keychain um Mac, Credential Manager ënner Windows).

Virun all Ännerung späichert den Installatiounsprogramm eng Kopie vum Konfiguratiounsfichier
dernieft (`<file>.fontes-backup-<time>`). Kopien, déi gemaach goufen, nodeems Dir Schlësselen
derbäigesat hutt, enthalen och d'Schlësselen. Läscht al Kopien, déi Dir net braucht.

## E Schlëssel änneren oder läschen

- Loosst **Add or change keys** lafen. Fügt en neie Schlëssel an, fir en z'ersetzen, oder tippt
  `-`, fir en ze läschen.
- Oder ännert den `env`-Block mat der Hand a start d'App nei.
- Wann Dir Fontes desinstalléiert, gëtt seng ganz Entrée ewechgeholl, mat de Schlësselen.
  D'Sécherheetskopie ginn net geläscht.
- Wann e Schlëssel un d'Ëffentlechkeet komm ass, ersetzt en och bei der Quell: maacht op PISTE nei
  Zougangsdonnéeë fir Är App; bei api.data.gov frot en neie Schlëssel un.

## Meldungen, déi Dir gesi kënnt

| Meldung | Bedeitung |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Kee Schlëssel fir Frankräich. Setzt een derbäi. |
| `Inactive: needs a free PISTE account. ...` (an `list_jurisdictions`) | Datselwecht. |
| `PISTE refused the client credentials ...` | D'ID oder de Secret ass falsch oder net méi gülteg. Kopéiert allebéid nach eng Kéier aus dem Tab Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Är App ass net op dës API abonnéiert, oder Dir hutt hir Konditiounen net akzeptéiert. Kuckt d'Schrëtt 2 an 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Kee US-Schlëssel. D'Sich funktionéiert fir e puer Opriff den Dag. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Den Demo-Schlëssel ass opgebraucht. Setzt Ären eegene Schlëssel derbäi. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | De Schlëssel ass falsch, oder nach net iwwer d'E-Mail bestätegt. |

En eidele Wäert gëllt als kee Schlëssel.

## Erlaabnesser (WLM_PERMITTED)

Dat ass keen API-Schlëssel, an den Installatiounsprogramm setzt en net. **Setzt en just, wann Dir
dës Erlaabnes selwer hutt.**

E puer Quelle sinn standardméisseg aus, well hir Konditiounen oder hir robots.txt eng automatiséiert
Notzung ouni Erlaabnes verbidden. Wann Dir d'Erlaabnes vum Editeur hutt, schalt eng Quell an,
andeems Dir hire Code, mat Kommaen getrennt, an `WLM_PERMITTED` am `env`-Block derbäisetzt:
`"WLM_PERMITTED": "in,de"`.

| Code | Quell |
|---|---|
| `az` | Aserbaidschan: e-qanun.az (Justizministère) |
| `bh` | Bahrain: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Kolumbien: Función Pública, Gestor Normativo (konsolidéiert Gesetzgebung) |
| `de` | Däitschland: NeuRIS (Bundesportal fir juristesch Informatioun, Testservice) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Griicheland: Nationaldréckerei, Sich am Amtsblat (search.et.gr) |
| `in` | Indien: India Code (indiacode.gov.in) |
| `mu` | Mauritius: Supreme Court (supremecourt.govmu.org) |
| `sg` | Singapur: Geriichtsuerteeler (elitigation.sg) |

Ouni Erlaabnes seet Fontes: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
