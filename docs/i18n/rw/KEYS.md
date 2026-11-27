> Iyi ni inyandiko yahinduwe hifashishijwe imashini. Inyandiko y'Icyongereza ni yo ifite agaciro.

# Imfunguzo za API

Inkomoko hafi ya zose ziri muri Fontes zikora nta rufunguzo. Eshatu zikenera urufunguzo rw'ubuntu:

| Urufunguzo | Icyo rufungura | Utarufite |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | U Bufaransa: Judilibre (ibyemezo by'inkiko) na Légifrance (amategeko) | U Bufaransa burafunze. `list_jurisdictions` ibugaragaza nk'ubudakora. |
| `WLM_US_GOVINFO_KEY` | Leta Zunze Ubumwe za Amerika: ishakisha rya govinfo (ibyemezo by'inkiko za leta yunze ubumwe, Statutes at Large, public laws) | Fontes ikoresha urufunguzo rusangiwe `DEMO_KEY`: ishakisha rigera ku 10 ku munsi kuri buri aderesi IP. Gufungura icyemezo usanzwe uzi na US Code ntibikenera urufunguzo. |
| `WLM_US_COURTLISTENER_KEY` | Inkiko za Leta zigize Leta Zunze Ubumwe za Amerika (`us-states`): ibyemezo by'inkiko nkuru n'iz'ubujurire z'ama Leta yose 50 na DC, biturutse kuri CourtListener | Imanza z'inkiko za Leta zigize Leta Zunze Ubumwe za Amerika zirafunze. `list_jurisdictions` irazigaragaza nk'izidakora. |

Imfunguzo si itegeko. Ushobora kuzongeraho nyuma.

## Kongeraho urufunguzo

**Ukoresheje porogaramu yo gushyiraho.** Fontes imaze gushyirwaho, porogaramu yo gushyiraho igusaba
kongeraho imfunguzo. Kuri Mac, kanda **Ongeraho imfunguzo**, cyangwa **Byarangiye** kugira ngo
usimbuke; kuri Windows, subiza ikibazo (kanda Enter kugira ngo usimbuke). Kugira ngo wongereho
cyangwa uhindure imfunguzo nyuma, koresha **Ongeraho cyangwa uhindure imfunguzo**:

- Mac: ongera ufungure porogaramu Fontes Installer uhitemo **Ongeraho cyangwa uhindure imfunguzo**.
- Windows: fungura menu ya Start, hanyuma uhitemo **Fontes** → **Ongeraho cyangwa uhindure imfunguzo**.

Ibyo wandika ntibigaragara. Kuri buri rufunguzo: rwomeke, kanda Enter kugira ngo ugumane urusanzwe,
cyangwa wandike `-` kugira ngo urukureho. Imfunguzo zijya muri buri porogaramu isanzwe ifite Fontes.

**Ukoresheje extension ya Claude Desktop (.mcpb).** Fungura Claude > Settings > Extensions > Fontes
wuzuze imyanya. Yose si itegeko.

**N'intoki.** Ongeraho variables mu gice `env` cy'icyanditswe cya `fontes` mu igenamiterere rya MCP rya
porogaramu yawe:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Ongera utangize porogaramu nyuma y'impinduka iyo ari yo yose.

## U Bufaransa: PISTE (ubuntu)

1. Fungura konti kuri [piste.gouv.fr](https://piste.gouv.fr). Ibyo bisobanura ko wemera amabwiriza ya
   PISTE (CGU).
2. Jya kuri API > **Consentement CGU API**. Emera amabwiriza ya **JUDILIBRE** na **Légifrance** (production).
3. Kora **porogaramu ya production**. `APP_SANDBOX` wakorewe ntishobora kugera kuri production.
   Muri "Modifier l'application", hitamo **JUDILIBRE (production)** na **Légifrance (production)**, hanyuma
   ubishyire mu bikorwa.
4. Fungura tab **Authentification** ya porogaramu. Kopa `client_id` na `client_secret`.
5. Koresha **Ongeraho cyangwa uhindure imfunguzo** uzomeke.

Amabwiriza, mu ncamake:

- Amakuru: Licence Ouverte / Etalab 2.0. Ushobora kuyakoresha kongera, harimo no mu bucuruzi, niba
  uvuga inkomoko.
- Ntugatangaze cyangwa ngo usangize ibikuranga (credentials). Menyesha PISTE niba byamenyekanye.
- API ya Légifrance ni serivisi ya beta. Ishobora guhagarara, kandi ifite imibare ntarengwa (ku isegonda,
  ku munota no ku munsi).
- Inyandiko za Légifrance si verisiyo yemewe (authentic). PDF isinye ya Journal officiel ni yo yonyine
  yemewe.
- Judilibre: ntukoreshe amazina y'abacamanza cyangwa abanditsi b'inkiko kugira ngo usuzume, ugereranye
  cyangwa uhanure akazi kabo (Code de l'organisation judiciaire art. L111-13; ni icyaha gihanwa
  n'amategeko).
- Judilibre: kurikiza GDPR. Ntugerageze kongera kumenya ababurana.

Imibare ntarengwa yawe kuri PISTE iri muri API Sélectionnées > Actions > Consulter les quotas.

## Leta Zunze Ubumwe za Amerika: api.data.gov (ubuntu)

1. Jya kuri [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (urufunguzo rugaragara ku
   kirahure) cyangwa kuri [api.data.gov/signup](https://api.data.gov/signup/) (urufunguzo
   rwoherezwa kuri imeyili).
2. Andika izina ryawe na imeyili yawe. Umwanya "how will you use it" si itegeko.
3. Kopa urufunguzo rw'inyuguti 40.
4. Koresha **Ongeraho cyangwa uhindure imfunguzo** urwomeke nk'urufunguzo rwa Leta Zunze Ubumwe za Amerika.

Amabwiriza, mu ncamake:

- Ukoresheje urufunguzo rwawe bwite, govinfo yemera ubusabe bugera ku 36,000 ku isaha.
- Ntitwabonye amabwiriza yihariye y'ikoreshwa ya API ubwayo (api.data.gov/terms/ ntibaho). Ntibyagenzuwe.
  Reba [politiki za govinfo](https://www.govinfo.gov/about/policies) na
  [politiki y'ubuzima bwite ya data.gov](https://data.gov/privacy-policy/).
- Urufunguzo rugumane wenyine.

## Inkiko za Leta zigize Leta Zunze Ubumwe za Amerika: CourtListener (ubuntu)

CourtListener iyoborwa na [Free Law Project](https://free.law), umuryango udaharanira indonke umaze kuva mu 2010 ukusanya ibyemezo by'inkiko zo muri Leta Zunze Ubumwe za Amerika ukabigeza kuri bose ku buntu. Ukurikije imibare yawo bwite, ufite ibyemezo birenga miliyoni icyenda. Si inkomoko y'ubuyobozi: inkiko zitangaza ibyemezo byazo ubwazo, naho CourtListener ikabikusanya ku mbuga z'inkiko no mu nyandiko z'amategeko zasikanwe. Buri gisubizo cya Fontes gituruka kuri yo kibivuga. Fontes nta sano ifitanye na Free Law Project.

1. Fungura konti y'ubuntu kuri [courtlistener.com](https://www.courtlistener.com/sign-in/).
2. Fungura umwirondoro wawe ukope API token yawe.
3. Koresha **Ongeraho cyangwa uhindure imfunguzo** urwomeke nk'urufunguzo rwa CourtListener.

Amabwiriza, mu ncamake ([amabwiriza yuzuye](https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies)):

- Token ni iyawe wenyine: ntuyisangire n'abandi, ntuyihuze n'iz'abandi cyangwa ngo uyigurishe, kandi ntukoreshe konti nyinshi.
- Ni wowe ubazwa ibyo porogaramu ya AI ikora na token yawe.
- Ntugaragaze isesengura rya AI ryakozwe ku makuru yabo nk'iryakozwe, ryemejwe cyangwa ryagenzuwe na Free Law Project.
- Konti y'ubuntu yemera ubusabe 5 ku munota, 50 ku isaha na 125 ku munsi. Ishakisha rimwe ni busabe bumwe; gufungura icyemezo ni ubusabe bubiri. Kuba umunyamuryango wa Free Law Project byongera iyo mipaka.
- CourtListener ntiyemeza ko ibyayo ari ukuri. Genzura icyemezo ugereranyije n'inyandiko y'urukiko mbere yo kucyiringira.

## Aho imfunguzo zibikwa

- **Ukoresheje porogaramu yo gushyiraho cyangwa n'intoki:** mu nyandiko isomeka (plain text) muri dosiye
  y'igenamiterere rya MCP rya buri porogaramu, mu gice `env` cy'icyanditswe cya `fontes`. Umuntu wese
  ushobora gusoma dosiye zawe ashobora gusoma imfunguzo.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` cyangwa `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Extension ya Claude Desktop (.mcpb):** Claude ibika iyo myanya mu igenamiterere ryayo kandi
  ikayirinda ikoresheje ububiko bwizewe bwa sisitemu yawe (Keychain kuri Mac, Credential Manager kuri
  Windows).

Mbere ya buri mpinduka, porogaramu yo gushyiraho ibika kopi ya dosiye y'igenamiterere iruhande rwayo
(`<file>.fontes-backup-<time>`). Kopi zakozwe nyuma y'uko wongeyeho imfunguzo nazo zirimo izo mfunguzo.
Siba kopi za kera utagikeneye.

## Guhindura cyangwa gukuraho urufunguzo

- Koresha **Ongeraho cyangwa uhindure imfunguzo**. Omeka urufunguzo rushya kugira ngo urusimbuze, cyangwa
  wandike `-` kugira ngo urukureho.
- Cyangwa uhindure igice `env` n'intoki hanyuma wongere utangize porogaramu.
- Gukuraho Fontes bikuraho icyanditswe cyayo cyose, imfunguzo zirimo. Ntibisiba kopi z'ububiko.
- Niba urufunguzo rwamenyekanye, rusimbuze no ku nkomoko: kuri PISTE, kora ibikuranga bishya bya
  porogaramu yawe; kuri api.data.gov, iyandikishe ubone urufunguzo rushya.

## Ubutumwa ushobora kubona

| Ubutumwa | Icyo busobanura |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Nta rufunguzo rw'u Bufaransa. Ongeraho rumwe. |
| `Inactive: needs a free PISTE account. ...` (muri `list_jurisdictions`) | Ni kimwe. |
| `PISTE refused the client credentials ...` | ID cyangwa secret si byo cyangwa byararangiye. Ongera ukope byombi muri tab Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Porogaramu yawe ntiyiyandikishije kuri iyo API, cyangwa ntiwemeye amabwiriza yayo. Reba intambwe ya 2 n'iya 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Nta rufunguzo rwa Leta Zunze Ubumwe za Amerika. Ishakisha rikora ku mahamagara make ku munsi. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Urufunguzo rwa demo rwarashize. Ongeraho urufunguzo rwawe bwite. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Urufunguzo si rwo, cyangwa ntiwaruremeje muri imeyili. |

Agaciro gasa (karimo ubusa) kabarwa nk'aho nta rufunguzo.

## Uruhushya (WLM_PERMITTED)

Iki si urufunguzo rwa API, kandi porogaramu yo gushyiraho ntiyigishyiraho. **Gishyireho gusa niba wowe
ubwawe ufite urwo ruhushya.**

Inkomoko zimwe zirafunze mu buryo busanzwe kubera ko amabwiriza yazo cyangwa robots.txt yazo bibuza
gukoresha mu buryo bwikora nta ruhushya. Niba ufite uruhushya rw'uyitangaza, fungura inkomoko wongera
kode yayo muri `WLM_PERMITTED`, zitandukanyijwe n'akitso, mu gice `env`: `"WLM_PERMITTED": "in,de"`.

| Kode | Inkomoko |
|---|---|
| `az` | Azerubayijani: e-qanun.az (Minisiteri y'Ubutabera) |
| `bh` | Bahareyini: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Kolombiya: Función Pública, Gestor Normativo (amategeko avuguruye) |
| `de` | U Budage: NeuRIS (urubuga rwa leta yunze ubumwe rw'amakuru y'amategeko, serivisi y'igerageza) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | U Bugereki: Icapiro rya Leta, ishakisha muri Igazeti ya Leta (search.et.gr) |
| `in` | U Buhinde: India Code (indiacode.gov.in) |
| `mu` | Morise: Urukiko rw'Ikirenga (supremecourt.govmu.org) |
| `sg` | Singapuru: imanza z'inkiko (elitigation.sg) |

Nta ruhushya, Fontes ivuga: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
