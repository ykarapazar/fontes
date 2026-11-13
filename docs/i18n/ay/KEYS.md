> Aka jaqukipäwix mäkina yanapt'ampiw luratawa. Inglés arun qillqatawa chiqapax (autoritativo).

# API llavenaka

Fontes ukan niya taqi jalsunakax jan llavempiw irnaqi. Payax mä inaki llaveniw wakisi:

| Llave | Kuns jist'ari | Jan utjkchixa |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Francia: Judilibre (taripäwinaka), Légifrance (kamachinaka) | Francia jiwt'atawa. `list_jurisdictions` ukax jan irnaqir ukham uñacht'ayi. |
| `WLM_US_GOVINFO_KEY` | Estados Unidos: govinfo thaqaña (federal taripañ utanakan opinionanakapa, Statutes at Large, public laws) | Fontes ukax chikat apnaqat `DEMO_KEY` apnaqi: sapa uru sapa IP direccionatak niya 10 thaqäwi. Uñt'at taripäw jist'araña, US Code ukanakax janiw llave munkiti. |

Llavenakax ajlliñatakiwa. Qhipat yapxatasmawa.

## Mä llave yapxataña

**Instaladorampi.** Instalaskasa, instaladorax llavenak yapxatañ munasmati sasaw jiskt'i.
Pasañatakix **Not now** ajllim (jan ukax Enter limt'am). Qhipat llavenak yapxatañataki jan
ukax mayjt'ayañataki, **Add or change keys** irnaqayam:

- Mac: Fontes Installer aplicación wasitat jist'aram ukat **Add or change keys** ajllim, jan
  ukax instalador carpetan `Add or change keys.command` ukar pä kuti click lurtam.
- Windows: instalador carpetan `Add or change keys.cmd` ukar pä kuti click lurtam. Windows
  instalañ programax, utjxani ukhaxa, Start menu > Fontes ukarus uchaniwa.

Qillqkta ukax imantatawa. Sapa llavetaki: ch'ikt'am, utjki uk imañatakix Enter limt'am, jan
ukax apsuñatakix `-` qillqam. Llavenakax Fontes utjki uka taqi aplicacionanakaruw mantapxi.

**Claude Desktop extensión (.mcpb) ukampi.** Claude > Settings > Extensions > Fontes jist'aram
ukat camponak phuqhantam. Taqpachaw ajlliñataki.

**Amparampi.** Variables ukanak aplicacionaman MCP configuracionapan `fontes` qillqatan
`env` bloque ukar yapxatam:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Kuna mayjt'äwit qhipatsa aplicación wasitat qalltayam.

## Francia: PISTE (inaki)

1. [piste.gouv.fr](https://piste.gouv.fr) ukan mä cuenta luram. Ukax PISTE condicionanakap
   (CGU) katuqaña sañ muni.
2. API > **Consentement CGU API** ukar saram. **JUDILIBRE**, **Légifrance** (production)
   condicionanak katuqam.
3. Mä **producción aplicación** luram. Jumatak lurat `APP_SANDBOX` ukax janiw producción
   ukar puriykiti. "Modifier l'application" ukan **JUDILIBRE (production)**, **Légifrance
   (production)** chimpuntam, ukat apnaqam.
4. Aplicacionan **Authentification** pestaña jist'aram. `client_id`, `client_secret`
   copiam.
5. **Add or change keys** irnaqayam ukat ukanak ch'ikt'am.

Condicionanaka, jisk'achata:

- Yatiyäwinaka: Licence Ouverte / Etalab 2.0. Wasitat apnaqaña, aljañatakisa, atribución
  ukamp jaytatawa.
- Credencialanakam jan uñt'ayamti ni churamti. Mistsuchi ukhaxa PISTE ukar yatiyam.
- Légifrance API ukax mä beta serviciowa. Sayt'ayasispawa, cuotanakaniraki (sapa segundo,
  minuto, uru).
- Légifrance qillqatanakax janiw auténtico versionäkiti. Firmat Journal officiel PDF
  ukakiw auténtico.
- Judilibre: juezanakan jan ukax secretarionakan sutinakap jan apnaqamti lurawinakap
  chaninchañataki, chikachañataki jan ukax nayrat yatiñataki (Code de l'organisation
  judiciaire art. L111-13; mä delito penal).
- Judilibre: GDPR arkam. Partenakar wasitat uñt'añ jan yant'amti.

Cuotanakamax PISTE ukankiwa, API Sélectionnées > Actions > Consulter les quotas ukana.

## Estados Unidos: api.data.gov (inaki)

1. [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) ukar saram (llavex
   pantallan uñacht'ayasi) jan ukax [api.data.gov/signup](https://api.data.gov/signup/) ukar
   (llavex correo tuqiw apayätam).
2. Sutima, correoma qillqam. "How will you use it" campox ajlliñatakiwa.
3. 40 caracteranïr llave copiam.
4. **Add or change keys** irnaqayam ukat Estados Unidos llave ukham ch'ikt'am.

Condicionanaka, jisk'achata:

- Pachpa llavemampi, govinfo ukax mä horan 36,000 mayiwinakakamaw jaytayi.
- Janiw API ukatak sapa condicionanak jikxatapkti (api.data.gov/terms/ janiw utjkiti). Jan
  uñakipata. [govinfo's policies](https://www.govinfo.gov/about/policies),
  [data.gov privacy policy](https://data.gov/privacy-policy/) uñjam.
- Llave jumatakikiw imam.

## Kawkins llavenakax imasi

- **Instalador jan ukax amparampi:** qhana qillqat ukham sapa aplicacionan MCP configuración
  archivopana, `fontes` qillqatan `env` bloque ukana. Usuario archivonakam liyiñ puedki uka
  khitis llavenak liyiñ puedi.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` jan ukax `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Claude Desktop extensión (.mcpb):** Claude ukax aka camponak configuracionapan imi, ukat
  sistemaman jark'at imañapampiw jark'aqi (Mac ukan Keychain, Windows ukan Credential
  Manager).

Sapa mayjt'äwit nayraqata, instaladorax configuración archivon mä copiap jak'apan imi
(`<file>.fontes-backup-<time>`). Llavenak yapxatkasin lurat copianakax llavenakaniraki.
Jan wakiskir nayra copianak chhaqtayam.

## Mä llave mayjt'ayaña jan ukax apsuña

- **Add or change keys** irnaqayam. Lantiñatakix mä machaq llave ch'ikt'am, jan ukax
  apsuñatakix `-` qillqam.
- Jan ukax `env` bloque amparamamp mayjt'ayam ukat aplicación wasitat qalltayam.
- Fontes apsusax taqpach qillqatap apsu, llavenakapampi. Janiw copianak chhaqtaykiti.
- Mä llavex mistsuchixa, jalsunsa lantirakim: PISTE ukana, aplicacionamatak machaq
  credencialanak luram; api.data.gov ukana, mä machaq llavetak qillqantasim.

## Uñjaspa uka yatiyäwinaka

| Yatiyäwi | Kuns sañ muni |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Janiw Francia llave utjkiti. Maya yapxatam. |
| `Inactive: needs a free PISTE account. ...` (`list_jurisdictions` ukana) | Pachpakiwa. |
| `PISTE refused the client credentials ...` | ID jan ukax secret pantjatawa jan ukax janiw irnaqxiti. Payanak wasitat Authentification pestañat copiam. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Aplicacionamax janiw uka API ukar suscribitäkiti, jan ukax janiw condicionanakap katuqktati. 2, 3 lurawinak uñjam. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Janiw Estados Unidos llave utjkiti. Thaqañax sapa uru mä qhawqha jawsäwinakatakiw irnaqi. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Demo llavex tukusxiwa. Pachpa llavem yapxatam. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Llavex pantjatawa, jan ukax janïr correot chiqanchatäkiti. |

Mä ch'usa valorax jan llave ukham jakhutawa.

## Permisonaka (WLM_PERMITTED)

Akax janiw mä API llavekiti, instaladorasti janiw uchkiti. **Uka permiso pachpa utjkätam
ukhakiw uchañama.**

Yaqhip jalsunakax nayratpach jiwt'atawa, condicionanakapas jan ukax robots.txt ukas jan
permisompi automatizado apnaqañ jark'i. Uñt'ayirin permisop utjkätam ukhaxa, mä jalsu
naktayam códigop `WLM_PERMITTED` ukar yapxatasa, comampi jaljata, `env` bloque ukana:
`"WLM_PERMITTED": "in,de"`.

| Código | Jalsu |
|---|---|
| `az` | Azerbaiyán: e-qanun.az (Ministerio de Justicia) |
| `bh` | Baréin: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Colombia: Función Pública, Gestor Normativo (consolidado kamachinaka) |
| `de` | Alemania: NeuRIS (federal derecho yatiyäw portal, yant'äw servicio) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Grecia: National Printing Office, Government Gazette search (search.et.gr) |
| `in` | India: India Code (indiacode.gov.in) |
| `mu` | Mauricio: Supreme Court (supremecourt.govmu.org) |
| `sg` | Singapur: taripañ utanakan taripäwinakapa (elitigation.sg) |

Jan permisompixa, Fontes ukax siwa: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
