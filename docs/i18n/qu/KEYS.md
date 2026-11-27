> Kayqa makinap yanapasqan t'ikrasqam. Inglés simipi qillqasqam chaninchasqa kaq (autoritativo).

# API llavekuna

Fontespi yaqa llapan pukyukunam mana llaveyuq llamk'an. Kimsaymi mana qullqiyuq llaveta necesitan:

| Llave | Ima kicharin | Mana kaptin |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Francia: Judilibre (taripana wasikunap taripayninkuna), Légifrance (kamachiykuna) | Franciaqa wañusqam. `list_jurisdictions` nisqaqa mana llamk'aq hinam rikuchin. |
| `WLM_US_GOVINFO_KEY` | Estados Unidos: govinfo maskay (federal taripana wasikunap opinionninkuna, Statutes at Large, public laws) | Fontesqa rakinakusqa `DEMO_KEY` nisqatam llamk'achin: sapa IP direcciónpaq p'unchawpi yaqa 10 maskaykuna. Riqsisqa taripayta kichanapaq, US Code nisqapaqpas manam llave necesitakunchu. |
| `WLM_US_COURTLISTENER_KEY` | Estados Unidospa estado taripana wasikuna (`us-states`): llapan 50 estadokunap DC nisqapas aswan hatun taripana wasikunap apelación taripana wasikunapas opinionninkuna, CourtListener nisqamanta | Estados Unidospa estado taripana wasikunap jurisprudencian wañusqam. `list_jurisdictions` nisqaqa mana llamk'aqta rikuchin. |

Llavekunaqa akllanapaqmi. Qhipamanpas yapayta atinki.

## Huk llaveta yapay

**Instaladorwan.** Fontes churasqaña kaptin, instaladorqa llavekunata yapayta munasqaykita
tapusunki. Macpiqa **Llavekunata yapay** nisqapi click ruway, utaq saltanaykipaq **Tukusqa**
nisqapi; Windowspiqa tapuyta kutichiy (saltanaykipaq Enter ñit'iy). Qhipaman llavekunata yapanaykipaq utaq
tikranaykipaq, **Add or change keys** nisqata purichiy:

- Mac: Fontes Installer aplicacionta wakmanta kichay hinaspa **Llavekunata yapay utaq tikray**
  akllay.
- Windows: Start menu kichay, hinaspa **Fontes** → **Llavekunata yapay utaq tikray** akllay.

Qillqasqaykiqa pakasqam. Sapa llavepaq: k'askachiy, kachkaqta waqaychanaykipaq Enter ñit'iy,
utaq qichunaykipaq `-` qillqay. Llavekunaqa Fontesniyuqña llapan aplicacionkunamanmi yaykunku.

**Claude Desktop extensionwan (.mcpb).** Claude > Settings > Extensions > Fontes nisqata kichay
hinaspa camponkunata hunt'ay. Llapanmi akllanapaq.

**Makiwan.** Variablekunata aplicacionniykip MCP configuracionninpi `fontes` qillqap `env`
bloquenman yapay:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Ima tikraymanta qhipapas aplicacionta wakmanta qallarichiy.

## Francia: PISTE (mana qullqiyuq)

1. [piste.gouv.fr](https://piste.gouv.fr) nisqapi huk cuentata ruway. Kayqa PISTEp condicionninkunata (CGU) chaskiymi.
2. API > **Consentement CGU API** nisqaman riy. **JUDILIBRE**, **Légifrance** (production) nisqakunap condicionninkunata chaskiy.
3. Huk **production application** ruway. Qampaq ruwasqa `APP_SANDBOX` nisqaqa manam productionman chayanchu.
   "Modifier l'application" nisqapi, **JUDILIBRE (production)**, **Légifrance (production)** nisqakunata akllay, chaymanta aplicay.
4. Aplicacionpa **Authentification** pestañanta kichay. `client_id`, `client_secret` nisqakunata copiay.
5. **Add or change keys** nisqata purichiy hinaspa k'askachiy.

Condicionkuna, pisillapi:

- Datokuna: Licence Ouverte / Etalab 2.0. Wakmanta llamk'achiyqa, comercial llamk'achiypas, sutinchaywanmi permitisqa.
- Ama credencialniykikunata uyarichiychu nitaq rakinakuychu. Lluqsinkuman chayqa PISTEman willay.
- Légifrance APIqa beta serviciom. Sayachisqa kanmanmi, cuotakunayuqtaq (sapa segundo, minuto, p'unchawpaq).
- Légifrancep qillqankunaqa manam chiqap (auténtica) versiónchu. Firmasqa Journal officiel PDFllam chiqap.
- Judilibre: ama juezkunap utaq secretariokunap sutinkunata llamk'achiychu llamk'ayninkuta
  chaninchanapaq, tupachinapaq utaq ñawpaqmanta willanapaq (Code de l'organisation judiciaire art. L111-13; huk delito).
- Judilibre: GDPR nisqata kasukuy. Ama partekunata wakmanta riqsichiyta munaychu.

Cuotaykikunaqa PISTEpim kachkan, API Sélectionnées > Actions > Consulter les quotas nisqapi.

## Estados Unidos: api.data.gov (mana qullqiyuq)

1. [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) nisqaman riy (llaveqa pantallapim rikukun)
   utaq [api.data.gov/signup](https://api.data.gov/signup/) nisqaman (llaveqa correoykimanmi kachakun).
2. Sutiykita, correoykitapas qillqay. "How will you use it" campoqa akllanapaqmi.
3. 40 qillqayuq llaveta copiay.
4. **Add or change keys** nisqata purichiy hinaspa Estados Unidos llave hina k'askachiy.

Condicionkuna, pisillapi:

- Kikiyki llaveykiwan, govinfoqa horapi 36,000 mañakuykunakamam saqin.
- Manam APIpaq sapaq servicio condicionkunata tarirqaykuchu (api.data.gov/terms/ manam kanchu). Mana chiqaqchasqa.
  [govinfop políticankunata](https://www.govinfo.gov/about/policies),
  [data.govpa privacidad políticantapas](https://data.gov/privacy-policy/) qhaway.
- Llaveta qamllapaq waqaychay.

## Estados Unidospa estado taripana wasikuna: CourtListener (mana qullqiyuq)

CourtListenerqa [Free Law Project](https://free.law) nisqap kamachisqanmi, mana qhapaq kayta maskaq huñunakuymi. 2010 watamantapacha Estados Unidospa taripana wasinkunap opinionninkunata huñun, llapa runapaq mana qullqiyuqta quran. Paypa huk yupasqanman hinaqa isqun milloneshina taripayniyuqmi. Manam oficial pukyuchu: taripana wasikunam kikinku opinionninkuta pawachinku, CourtListenertaq chaykunata taripana wasikunap web sitionkunamanta, scanisqa leykunap willakuyninkunamantawan huñun. Fontesmanta sapa kutichiypas chayta willan. Fontesqa manam Free Law Project nisqawan tinkisqachu.

1. [courtlistener.com](https://www.courtlistener.com/sign-in/) nisqapi mana qullqiyuq cuentata kamariy.
2. Perfilniykita kichay, API token nisqaykitataq copiay.
3. **Add or change keys** nisqata purichiy hinaspa CourtListener llave hina k'askachiy.

Condicionkuna, pisillapi ([hunt'asqa condicionkuna](https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies)):

- Tokenqa qamllapaqmi: ama rakinkichu, ama huñunkichu nitaq huk kutita ruwankichu, amataq achka cuentakunata llamk'achinkichu.
- Huk IA aplicacion tokenniykiwan imatapas ruwaptinqa qamraqmi responsablekanki.
- Ama IAp paykunap datankuta t'aqwisqanta Free Law Project ruwasqa, aprobasqa utaq chaqnisqa hina rikuchiychu.
- Mana qullqiyuq cuentaqa sapa minutupi 5 mañakuykunata, sapa horapi 50, sapa p'unchawpi 125 mañakuykunatam saqin. Huk maskayqa huk mañakuymi; huk taripayta kichayqa iskaymi. Free Law Project nisqapi socio kayqa chay saywakunata wichachin.
- CourtListenerqa manam chiqaq kayninta garantizanchu. Huk opinionpi hap'ipakuspayki, taripana wasip copianwan chaqnipay.

## Maypitaq llavekuna waqaychakun

- **Instalador utaq makiwan:** ch'uya qillqa hina sapa aplicacionpa MCP configuración archivonpi,
  `fontes` qillqap `env` bloquenpi. Usuario archivoykikunata ñawinchayta atiq mayqin runapas
  llavekunata ñawinchanmanmi.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` utaq `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Claude Desktop extensión (.mcpb):** Claudeqa kay camponkunata configuracionninpim waqaychan,
  sistemaykip seguro waqaychananwantaq amachan (Macpi Keychain, Windowspi Credential Manager).

Sapa tikraymanta ñawpaqta, instaladorqa configuración archivop huk copiantam qayllanpi
waqaychan (`<file>.fontes-backup-<time>`). Llavekunata yapasqayki qhipa copiakunaqa
llavekunatapas apanmi. Mana necesitasqayki ñawpaq copiakunata qichuy.

## Huk llaveta tikray utaq qichuy

- **Add or change keys** nisqata purichiy. Rantinanpaq musuq llaveta k'askachiy, utaq qichunaykipaq `-` qillqay.
- Utaq `env` bloqueta makiwan tikray hinaspa aplicacionta wakmanta qallarichiy.
- Fontesta qichuspaqa llapan qillqantam qichun, llavekunantinta. Backup copiakunataqa manam qichunchu.
- Huk llave lluqsirqan chayqa, pukyupipas rantiy: PISTEpi, aplicacionniykipaq musuq
  credencialkunata ruway; api.data.govpaq, musuq llavepaq qillqakuy.

## Rikunayki willakuykuna

| Willakuy | Ima niyta munan |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Manam Francia llave kanchu. Hukta yapay. |
| `Inactive: needs a free PISTE account. ...` (`list_jurisdictions` nisqapi) | Kikillanmi. |
| `PISTE refused the client credentials ...` | ID utaq secret pantasqam utaq manaña allinchu. Iskayninta Authentification pestañamanta wakmanta copiay. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Aplicacionniykiqa manam chay APIman suscribisqachu, utaq manaraq condicionninkunata chaskirqankichu. 2, 3 kaq ruraykunata qhaway. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Manam Estados Unidos llave kanchu. Maskayqa p'unchawpi pisi waqyaykunapaqmi llamk'an. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Demo llaveqa tukusqañam. Kikiyki llaveykita yapay. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Llaveqa pantasqam, utaq manaraq correomanta chiqaqchasqachu. |

Ch'usaq valorqa mana llave hinam yupakun.

## Permisokuna (WLM_PERMITTED)

Kayqa manam API llavechu, instaladortaq manam churanchu. **Kikiyki chay permisoyuq kaspallaña
churay.**

Wakin pukyukunaqa ñawpaqmantapacha wañusqam, condicionninkuna utaq robots.txt nisqanku mana
permisoyuq automatizado llamk'achiyta hark'asqanrayku. Uyarichiqpa permisonta hap'inki chayqa,
huk pukyuta hap'ichiy códigonta `WLM_PERMITTED` nisqaman yapaspa, comakunawan t'aqasqa,
`env` bloquepi: `"WLM_PERMITTED": "in,de"`.

| Código | Pukyu |
|---|---|
| `az` | Azerbaiyán: e-qanun.az (Justicia Ministerio) |
| `bh` | Baréin: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Colombia: Función Pública, Gestor Normativo (consolidado kamachiykuna) |
| `de` | Alemania: NeuRIS (federal derecho willakuy portal, prueba servicio) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Grecia: Imprenta Nacional, Gobierno Gacetapi maskay (search.et.gr) |
| `in` | India: India Code (indiacode.gov.in) |
| `mu` | Mauricio: Corte Suprema (supremecourt.govmu.org) |
| `sg` | Singapur: taripana wasikunap taripayninkuna (elitigation.sg) |

Mana permisoyuq, Fontesqa nin: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
