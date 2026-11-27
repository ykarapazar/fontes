> Ko ñembohasa ojejapo máquina pytyvõ reheve. Pe inglés ñe'ẽme oĩva ha'e pe autoritativo.

# Clave API

Haimete opaite ypykue Fontes-pe oiko clave'ỹre. Mbohapy oikotevẽ peteĩ reigua:

| Clave | Mba'épa oipe'a | Ndaipóriramo |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Francia: Judilibre (tribunalkuéra sentencia) ha Légifrance (léikuéra) | Francia oĩ mbogue. `list_jurisdictions` ohechauka ndoikóiháicha. |
| `WLM_US_GOVINFO_KEY` | Estados Unidos: govinfo jeheka (tribunal federal opinión, Statutes at Large, public laws) | Fontes oipuru `DEMO_KEY` ojepurúva oñondive: 10 jeheka rupi ára ha ára peteĩteĩ IP dirección-pe g̃uarã. Peteĩ sentencia ojekuaáva jeipe'a ha US Code noikotevẽi clave. |
| `WLM_US_COURTLISTENER_KEY` | Estados Unidos estado-kuéra tribunal (`us-states`): opinión tribunal supremo ha de apelación 50 estado ha DC-pegua, CourtListener-gui | Estados Unidos estado-kuéra jurisprudencia oĩ mbogue. `list_jurisdictions` ohechauka ndoikóiháicha. |

Clave-kuéra ojeiporavo hag̃ua. Ikatu rembojoapy upéi.

## Clave ñembojoapy

**Instalador reheve.** Fontes oñemohenda rire, instalador oikuave'ẽ rembojoapy hag̃ua clave. Mac-pe,
ejopy **Embojoapy clave**, térã **Opáma** rehasa hag̃ua; Windows-pe, embohovái porandu (ejopy Enter
rehasa hag̃ua). Rembojoapy térã remoambue hag̃ua upéi, emboguata **Add or change keys**:

- Mac: eipe'a jey aplicación Fontes Installer ha eiporavo **Embojoapy térã emoambue clave**.
- Windows: eipe'a Start menu, upe rire **Fontes** → **Embojoapy térã emoambue clave**.

Rehaíva oñeñomi. Peteĩteĩ clave-pe g̃uarã: emboja, ejopy Enter reñongatu hag̃ua oĩva, térã
ehai `-` renohẽ hag̃ua. Clave-kuéra oike opaite aplicación oguerekómava Fontes-pe.

**Claude Desktop extensión (.mcpb) reheve.** Eipe'a Claude > Settings > Extensions > Fontes ha
emyenyhẽ umi campo. Opavave ojeiporavo hag̃ua.

**Nde pópe.** Embojoapy variable-kuéra entrada `fontes` bloque `env`-pe nde aplicación
configuración MCP-pe:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Eipe'a jey aplicación oimeraẽ ñemoambue rire.

## Francia: PISTE (reigua)

1. Ejapo peteĩ cuenta [piste.gouv.fr](https://piste.gouv.fr)-pe. Upéva he'ise reguerohory
   PISTE condicionkuéra (CGU).
2. Eho API > **Consentement CGU API**-pe. Eguerohory condicionkuéra **JUDILIBRE** ha
   **Légifrance** (production)-pe g̃uarã.
3. Ejapo peteĩ **aplicación de producción**. `APP_SANDBOX` ojejapóva ndéve g̃uarã ndaikatúi
   og̃uahẽ producción-pe. "Modifier l'application" guýpe, emarka **JUDILIBRE (production)** ha
   **Légifrance (production)**, upéi emoĩ.
4. Eipe'a aplicación pestaña **Authentification**. Ekopia `client_id` ha `client_secret`.
5. Emboguata **Add or change keys** ha emboja umíva.

Condicionkuéra, mbykyhápe:

- Dato: Licence Ouverte / Etalab 2.0. Jeporu jey, comercial avei, oñemoneĩ atribución reheve.
- Ani remosarambi térã reme'ẽ nde credencial-kuéra. Emomarandu PISTE-pe osẽramo.
- Légifrance API ha'e peteĩ servicio beta. Ikatu ojejoko, ha oguereko cuota (segundo,
  minuto ha ára rupi).
- Légifrance jehaipy ndaha'éi versión auténtica. Journal officiel PDF oñefirmáva añoite
  ha'e.
- Judilibre: ani reipuru juez térã secretario réra rehecha, rembojoja térã remomarandu
  hag̃ua hembiapo (Code de l'organisation judiciaire art. L111-13; peteĩ delito penal).
- Judilibre: emoañete GDPR. Ani reñeha'ã reikuaa jey parte-kuéra.

Nde cuota-kuéra oĩ PISTE-pe, API Sélectionnées > Actions > Consulter les quotas-pe.

## Estados Unidos: api.data.gov (reigua)

1. Eho [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup)-pe (clave ojehechauka
   pantalla-pe) térã [api.data.gov/signup](https://api.data.gov/signup/)-pe (clave oñemondo
   ndéve correo rupive).
2. Ehai nde réra ha nde correo. Campo "how will you use it" ojeiporavo hag̃ua.
3. Ekopia clave 40 carácter orekóva.
4. Emboguata **Add or change keys** ha emboja Estados Unidos clave ramo.

Condicionkuéra, mbykyhápe:

- Nde clave tee reheve, govinfo oheja 36,000 jerure peve peteĩ aravópe.
- Ndajajuhúi condicionkuéra API-pe g̃uarã añoite (api.data.gov/terms/ ndaipóri). Ndojehechajeýi.
  Ehecha [govinfo's policies](https://www.govinfo.gov/about/policies) ha
  [data.gov privacy policy](https://data.gov/privacy-policy/).
- Eñongatu clave nde añoite g̃uarã.

## Estados Unidos estado-kuéra tribunal: CourtListener (reigua)

CourtListener omotenondéva [Free Law Project](https://free.law), peteĩ organización ojehepyme'ẽ'ỹva ombyatýva 2010 guive Estados Unidos tribunal opinión ha omoĩva opavavépe reigua. Hembiapo ñemoĩ he'iháicha, oguereko nueve millón sentencia ári. Ndaha'éi fuente oficial: tribunalkuéra voi omoherakuã hembiapokue, ha CourtListener ombyaty chupekuéra tribunal sitio web ha léi kuatiañe'ẽ escaneada-gui. Opaite Fontes mbohovái upégui he'i upéva. Fontes ndojoajúi Free Law Project ndive.

1. Embosako'i peteĩ cuenta reigua [courtlistener.com](https://www.courtlistener.com/sign-in/)-pe.
2. Eipe'a nde perfil ha ekopia nde API token.
3. Emboguata **Add or change keys** ha emboja CourtListener clave ramo.

Condicionkuéra, mbykyhápe ([condición pukukue](https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies)):

- Token ndeve añoite g̃uarã: ani reñomoirũ, reñembyaty térã rereñoi jey, ha ani reipuru heta cuenta.
- Nde reresarai'ỹ mba'épa peteĩ aplicación IA ojapo nde token reheve.
- Ani remoĩ peteĩ IA análisis hembiapokue rehegua ojejapo, ojehechakuaa térã ojehecha Free Law Project-pe.
- Peteĩ cuenta reigua oheja 5 jerure minuto rupi, 50 aravo rupi ha 125 ára rupi. Peteĩ jeheka ha'e peteĩ jerure; peteĩ sentencia jeipe'a ha'e mokõi. Free Law Project miembro ramo omoguahẽ ambue límite.
- CourtListener ndoikuaaukái hekoete. Ehecha peteĩ opinión tribunal kopia ndive ndoguerovia mboyve.

## Moõpa oñeñongatu clave-kuéra

- **Instalador térã nde pópe:** jehaipy hesakãháicha peteĩteĩ aplicación archivo configuración
  MCP-pe, entrada `fontes` bloque `env`-pe. Oimeraẽva ikatúva omoñe'ẽ nde archivo usuario
  ikatu omoñe'ẽ clave-kuéra.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` térã `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Claude Desktop extensión (.mcpb):** Claude oñongatu ko'ã campo iconfiguración-pe ha
  oñangareko hesekuéra nde sistema ñeñongatu segura reheve (Keychain Mac-pe, Credential
  Manager Windows-pe).

Peteĩteĩ ñemoambue mboyve, instalador oñongatu archivo configuración kópia ykére
(`<file>.fontes-backup-<time>`). Kópia ojejapóva rembojoapy rire clave oguereko avei umi clave.
Embogue kópia tuja ndereikotevẽiva.

## Clave ñemoambue térã ñenohẽ

- Emboguata **Add or change keys**. Emboja peteĩ clave pyahu remyengovia hag̃ua, térã ehai `-`
  renohẽ hag̃ua.
- Térã emoambue bloque `env` nde pópe ha eipe'a jey aplicación.
- Renohẽramo Fontes, onohẽ entrada opaite, clave-kuéra reheve. Nombogueí umi kópia.
- Peteĩ clave osẽramo, emyengovia avei ypykuépe: PISTE-pe, ejapo credencial pyahu nde
  aplicación-pe g̃uarã; api.data.gov-pe, eñemboheraguapy peteĩ clave pyahúpe g̃uarã.

## Marandu ikatúva rehecha

| Marandu | He'ise |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Ndaipóri Francia clave. Embojoapy peteĩ. |
| `Inactive: needs a free PISTE account. ...` (`list_jurisdictions`-pe) | Peteĩcha. |
| `PISTE refused the client credentials ...` | ID térã secret oĩ vai térã ndoikovéi. Ekopia jey mokõivéva pestaña Authentification-gui. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Nde aplicación noñesuscribíri upe API-pe, térã ndereguerohorýi gueteri hembiapoukapy. Ehecha tembiapo 2 ha 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Ndaipóri Estados Unidos clave. Jeheka oiko mbovymi ñehenóipe ára ha ára. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Demo clave opáma. Embojoapy nde clave tee. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Clave oĩ vai, térã noñemoañetéi gueteri correo-gui. |

Peteĩ valor nandi ojepapa clave'ỹ ramo.

## Permiso (WLM_PERMITTED)

Kóva ndaha'éi peteĩ clave API, ha instalador nomoĩri. **Emoĩ reguerekóramo upe permiso
nde ae añoite.**

Oĩ ypykue oĩva mbogue ijypýpe ihembiapoukapy térã robots.txt ombotove rupi jeporu automático
permiso'ỹre. Reguerekóramo ijára permiso, emyandy peteĩ ypykue rembojoapývo hi'código
`WLM_PERMITTED`-pe, coma reheve oñembojojáva, bloque `env`-pe: `"WLM_PERMITTED": "in,de"`.

| Código | Ypykue |
|---|---|
| `az` | Azerbaiyán: e-qanun.az (Ministerio de Justicia) |
| `bh` | Baréin: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Colombia: Función Pública, Gestor Normativo (léikuéra consolidado) |
| `de` | Alemania: NeuRIS (portal federal de información jurídica, servicio de prueba) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Grecia: National Printing Office, Government Gazette search (search.et.gr) |
| `in` | India: India Code (indiacode.gov.in) |
| `mu` | Mauricio: Supreme Court (supremecourt.govmu.org) |
| `sg` | Singapur: tribunal sentencia (elitigation.sg) |

Permiso'ỹre, Fontes he'i: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
