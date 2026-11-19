> Þetta er vélstudd þýðing. Enska útgáfan gildir.

# API-lyklar

Nánast allar heimildir í Fontes virka án lykils. Tvær þurfa ókeypis lykil:

| Lykill | Opnar | Án hans |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Frakkland: Judilibre (dómar) og Légifrance (löggjöf) | Frakkland er óvirkt. `list_jurisdictions` sýnir það sem óvirkt. |
| `WLM_US_GOVINFO_KEY` | Bandaríkin: govinfo-leit (dómar alríkisdómstóla, Statutes at Large, public laws) | Fontes notar sameiginlega `DEMO_KEY`: um 10 leitir á dag á hverja IP-tölu. Ekki þarf lykil til að opna þekktan dóm eða US Code. |

Lyklar eru valkvæðir. Þú getur bætt þeim við síðar.

## Að bæta við lykli

**Með uppsetningarforritinu.** Þegar Fontes hefur verið sett upp býðst uppsetningarforritið til að bæta
við lyklum. Á Mac skaltu smella á **Bæta við lyklum**, eða **Lokið** til að sleppa því; á Windows
skaltu svara spurningunni (ýttu á Enter til að sleppa því). Til að bæta við eða breyta lyklum síðar, keyrðu **Add or change keys**:

- Mac: opnaðu forritið Fontes Installer aftur og veldu **Bæta við eða breyta lyklum**.
- Windows: opnaðu Start-valmyndina, síðan **Fontes** → **Bæta við eða breyta lyklum**.

Það sem þú slærð inn er falið. Fyrir hvern lykil: límdu hann inn, ýttu á Enter til að halda því sem fyrir er, eða sláðu inn `-` til að
fjarlægja hann. Lyklarnir fara í öll forrit sem þegar hafa Fontes.

**Með Claude Desktop-viðbótinni (.mcpb).** Opnaðu Claude > Settings > Extensions > Fontes og
fylltu út reitina. Þeir eru allir valkvæðir.

**Handvirkt.** Bættu breytunum við `env`-blokkina í færslunni `fontes` í MCP-stillingum forritsins:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Endurræstu forritið eftir hverja breytingu.

## Frakkland: PISTE (ókeypis)

1. Stofnaðu aðgang á [piste.gouv.fr](https://piste.gouv.fr). Það felur í sér að samþykkja skilmála PISTE (CGU).
2. Farðu í API > **Consentement CGU API**. Samþykktu skilmálana fyrir **JUDILIBRE** og **Légifrance** (framleiðsluumhverfi).
3. Búðu til **framleiðsluforrit** (production application). `APP_SANDBOX` sem búið var til fyrir þig nær ekki í framleiðsluumhverfið.
   Undir „Modifier l'application“, hakaðu við **JUDILIBRE (production)** og **Légifrance (production)** og vistaðu svo.
4. Opnaðu flipann **Authentification** í forritinu. Afritaðu `client_id` og `client_secret`.
5. Keyrðu **Add or change keys** og límdu þá inn.

Skilmálarnir í stuttu máli:

- Gögn: Licence Ouverte / Etalab 2.0. Endurnotkun, þar á meðal í atvinnuskyni, er leyfð með tilvísun til heimildar.
- Ekki birta eða deila aðgangsupplýsingum þínum. Láttu PISTE vita ef þær leka.
- Légifrance-API-ið er þjónusta í beta-útgáfu. Henni getur verið lokað tímabundið, og hún hefur kvóta (á sekúndu, mínútu og dag).
- Textar Légifrance eru ekki gilda útgáfan. Aðeins undirritaða PDF-skjalið af Journal officiel er það.
- Judilibre: ekki nota nöfn dómara eða dómritara til að meta, bera saman eða spá fyrir um störf þeirra
  (Code de l'organisation judiciaire art. L111-13; refsivert brot).
- Judilibre: fylgdu GDPR. Ekki reyna að endurgreina aðila málsins.

Kvótarnir þínir eru á PISTE undir API Sélectionnées > Actions > Consulter les quotas.

## Bandaríkin: api.data.gov (ókeypis)

1. Farðu á [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (lykillinn birtist á skjánum)
   eða [api.data.gov/signup](https://api.data.gov/signup/) (lykillinn er sendur þér í tölvupósti).
2. Sláðu inn nafn þitt og netfang. Reiturinn „how will you use it“ er valkvæður.
3. Afritaðu 40 stafa lykilinn.
4. Keyrðu **Add or change keys** og límdu hann inn sem lykil fyrir Bandaríkin.

Skilmálarnir í stuttu máli:

- Með eigin lykli leyfir govinfo allt að 36.000 beiðnir á klukkustund.
- Við fundum enga sérstaka notkunarskilmála fyrir API-ið (api.data.gov/terms/ er ekki til). Óstaðfest.
  Sjá [stefnur govinfo](https://www.govinfo.gov/about/policies) og
  [persónuverndarstefnu data.gov](https://data.gov/privacy-policy/).
- Haltu lyklinum fyrir þig.

## Hvar lyklarnir eru geymdir

- **Uppsetningarforrit eða handvirkt:** sem venjulegur texti í MCP-stillingaskrá hvers forrits, í `env`-blokkinni í
  færslunni `fontes`. Hver sem getur lesið notandaskrárnar þínar getur lesið lyklana.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` eða `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Claude Desktop-viðbótin (.mcpb):** Claude geymir þessa reiti í stillingum sínum og verndar þá
  með öruggri geymslu kerfisins (Keychain á Mac, Credential Manager á Windows).

Fyrir hverja breytingu vistar uppsetningarforritið afrit af stillingaskránni við hlið hennar
(`<file>.fontes-backup-<time>`). Afrit sem gerð eru eftir að þú bættir við lyklum innihalda lyklana líka. Eyddu gömlum
afritum sem þú þarft ekki.

## Að breyta eða fjarlægja lykil

- Keyrðu **Add or change keys**. Límdu inn nýjan lykil til að skipta honum út, eða sláðu inn `-` til að fjarlægja hann.
- Eða breyttu `env`-blokkinni handvirkt og endurræstu forritið.
- Ef Fontes er fjarlægt fer öll færsla þess, lyklar meðtaldir. Afritunum er ekki eytt.
- Ef lykill hefur lekið, skiptu honum einnig út hjá heimildinni: á PISTE, búðu til nýjar aðgangsupplýsingar fyrir forritið þitt;
  hjá api.data.gov, skráðu þig fyrir nýjum lykli.

## Skilaboð sem þú gætir séð

| Skilaboð | Merking |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Enginn lykill fyrir Frakkland. Bættu einum við. |
| `Inactive: needs a free PISTE account. ...` (í `list_jurisdictions`) | Sama. |
| `PISTE refused the client credentials ...` | Auðkennið eða leyndarorðið er rangt eða ekki lengur gilt. Afritaðu hvort tveggja aftur úr flipanum Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Forritið þitt er ekki áskrifandi að því API, eða þú hefur ekki samþykkt skilmála þess. Sjá skref 2 og 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Enginn lykill fyrir Bandaríkin. Leit virkar fyrir nokkur köll á dag. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Kynningarlykillinn er uppurinn. Bættu við eigin lykli. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Lykillinn er rangur, eða ekki enn staðfestur úr tölvupóstinum. |

Tómt gildi telst sem enginn lykill.

## Leyfi (WLM_PERMITTED)

Þetta er ekki API-lykill, og uppsetningarforritið stillir það ekki. **Stilltu það aðeins ef þú hefur sjálfur
það leyfi.**

Sumar heimildir eru sjálfgefið óvirkar vegna þess að skilmálar þeirra eða robots.txt banna sjálfvirka notkun án
leyfis. Ef þú hefur leyfi frá útgefandanum, virkjaðu heimild með því að bæta kóða hennar við
`WLM_PERMITTED`, aðskildum með kommu, í `env`-blokkinni: `"WLM_PERMITTED": "in,de"`.

| Kóði | Heimild |
|---|---|
| `az` | Aserbaídsjan: e-qanun.az (dómsmálaráðuneytið) |
| `bh` | Barein: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Kólumbía: Función Pública, Gestor Normativo (uppfærð löggjöf) |
| `de` | Þýskaland: NeuRIS (alríkisgátt lagaupplýsinga, prufuþjónusta) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Grikkland: National Printing Office, leit í Government Gazette (search.et.gr) |
| `in` | Indland: India Code (indiacode.gov.in) |
| `mu` | Máritíus: Supreme Court (supremecourt.govmu.org) |
| `sg` | Singapúr: dómar (elitigation.sg) |

Án leyfis segir Fontes: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
