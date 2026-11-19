> Bu terjime maşynyň kömegi bilen taýýarlandy. Iňlis dilindäki görnüşi esasy hasaplanýar.

# API açarlary

Fontes-daky çeşmeleriň hemmesi diýen ýaly açarsyz işleýär. Ikisine mugt açar gerek:

| Açar | Näme açýar | Açarsyz |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Fransiýa: Judilibre (kazyýet çözgütleri) we Légifrance (kanunçylyk) | Fransiýa öçük. `list_jurisdictions` ony işjeň däl diýip görkezýär. |
| `WLM_US_GOVINFO_KEY` | Amerikanyň Birleşen Ştatlary: govinfo gözlegi (federal kazyýet çözgütleri, Statutes at Large, public laws) | Fontes umumy `DEMO_KEY` ulanýar: bir IP salgy üçin günde takmynan 10 gözleg. Belli bir çözgüdi açmak we US Code üçin açar gerek däl. |

Açarlar islege bagly. Olary soňra goşup bilersiňiz.

## Açar goşmak

**Gurnaýjy arkaly.** Fontes sazlanandan soň, gurnaýjy açar goşmagy teklip edýär. Mac-da
**Açarlary goş** basyň ýa-da geçmek üçin **Taýýar** basyň; Windows-da soraga jogap beriň (geçmek
üçin Enter basyň). Açarlary soňra goşmak ýa-da üýtgetmek üçin **Add or change keys** işlediň:

- Mac: Fontes Installer programmasyny täzeden açyň we **Açarlary goş ýa-da üýtget** saýlaň.
- Windows: Start menu-ni açyň, soňra **Fontes** → **Açarlary goş ýa-da üýtget**.

Ýazylýan tekst gizlin bolýar. Her açar üçin: ony goýuň, bar bolany saklamak üçin Enter
düwmesine basyň ýa-da aýyrmak üçin `-` ýazyň. Açarlar Fontes eýýäm bar bolan her programma
girizilýär.

**Claude Desktop giňeltmesi (.mcpb) arkaly.** Claude > Settings > Extensions > Fontes açyň we
meýdanlary dolduryň. Olaryň hemmesi islege bagly.

**El bilen.** Üýtgeýänleri programmaňyzyň MCP sazlamasyndaky `fontes` ýazgysynyň `env`
blokuna goşuň:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Islendik üýtgetmeden soň programmany täzeden açyň.

## Fransiýa: PISTE (mugt)

1. [piste.gouv.fr](https://piste.gouv.fr) saýtynda hasap dörediň. Bu PISTE şertlerini (CGU)
   kabul etmegi aňladýar.
2. API > **Consentement CGU API** bölümine geçiň. **JUDILIBRE** we **Légifrance** (production)
   şertlerini kabul ediň.
3. **Production application** dörediň. Siziň üçin döredilen `APP_SANDBOX` production-a
   girip bilmeýär. “Modifier l'application” astynda **JUDILIBRE (production)** we
   **Légifrance (production)** belläň, soňra ulanyň.
4. Programmanyň **Authentification** goýmasyny açyň. `client_id` we `client_secret` göçüriň.
5. **Add or change keys** işlediň we olary goýuň.

Şertler, gysgaça:

- Maglumatlar: Licence Ouverte / Etalab 2.0. Gaýtadan ulanmak, şol sanda täjirçilik maksatly
  gaýtadan ulanmak, awtorlygy görkezmek şerti bilen rugsat berilýär.
- Hasap maglumatlaryňyzy çap etmäň we başgalara bermäň. Olar daşyna çyksa, PISTE-ä habar beriň.
- Légifrance API beta hyzmaty. Ol togtadylyp bilner we onuň kwotalary bar (sekunt, minut we
  gün boýunça).
- Légifrance tekstleri hakyky görnüş däl. Diňe gol çekilen Journal officiel PDF-i hakyky.
- Judilibre: kazylaryň ýa-da kazyýet kätipleriniň atlaryny olaryň işine baha bermek, olary
  deňeşdirmek ýa-da çaklamak üçin ulanmaň (Code de l'organisation judiciaire, L111-13 madda;
  jenaýat).
- Judilibre: GDPR talaplaryny berjaý ediň. Taraplary gaýtadan kesgitlemäge synanyşmaň.

Kwotalaryňyz PISTE-de API Sélectionnées > Actions > Consulter les quotas astynda.

## Amerikanyň Birleşen Ştatlary: api.data.gov (mugt)

1. [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (açar ekranda görkezilýär)
   ýa-da [api.data.gov/signup](https://api.data.gov/signup/) (açar e-poçtaňyza iberilýär)
   salgysyna geçiň.
2. Adyňyzy we e-poçtaňyzy giriziň. “How will you use it” meýdany islege bagly.
3. 40 nyşanly açary göçüriň.
4. **Add or change keys** işlediň we ony ABŞ açary hökmünde goýuň.

Şertler, gysgaça:

- Öz açaryňyz bilen govinfo sagatda 36 000 haýyşa çenli rugsat berýär.
- Biz API-e mahsus ulanyş şertlerini tapmadyk (api.data.gov/terms/ ýok). Barlanmadyk.
  Serediň: [govinfo syýasatlary](https://www.govinfo.gov/about/policies) we
  [data.gov gizlinlik syýasaty](https://data.gov/privacy-policy/).
- Açary özüňizde saklaň.

## Açarlar nirede saklanýar

- **Gurnaýjy arkaly ýa-da el bilen:** her programmanyň MCP sazlama faýlynda, `fontes`
  ýazgysynyň `env` blokunda ýönekeý tekst hökmünde. Ulanyjy faýllaryňyzy okap bilýän her bir
  adam açarlary okap bilýär.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` ýa-da `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Claude Desktop giňeltmesi (.mcpb):** Claude bu meýdanlary öz sazlamalarynda saklaýar we
  olary ulgamyňyzyň howpsuz ammary (Mac-da Keychain, Windows-da Credential Manager) bilen
  goraýar.

Her üýtgetmeden öň gurnaýjy sazlama faýlynyň nusgasyny onuň ýanynda saklaýar
(`<file>.fontes-backup-<time>`). Açarlary goşanyňyzdan soň döredilen nusgalarda açarlar hem
bolýar. Gerek bolmadyk köne nusgalary pozuň.

## Açary üýtgetmek ýa-da aýyrmak

- **Add or change keys** işlediň. Çalyşmak üçin täze açary goýuň ýa-da aýyrmak üçin `-`
  ýazyň.
- Ýa-da `env` bloguny el bilen redaktirläň we programmany täzeden açyň.
- Fontes-i aýyrmak onuň tutuş ýazgysyny, açarlar bilen bilelikde, aýyrýar. Ol ätiýaçlyk
  nusgalary pozmaýar.
- Eger açar daşyna çykan bolsa, ony çeşmede hem çalşyň: PISTE-de programmaňyz üçin täze hasap
  maglumatlaryny dörediň; api.data.gov üçin täze açara ýazylyň.

## Görüp biljek habarlaryňyz

| Habar | Manysy |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Fransiýa açary ýok. Ony goşuň. |
| `Inactive: needs a free PISTE account. ...` (`list_jurisdictions` içinde) | Şol bir zat. |
| `PISTE refused the client credentials ...` | ID ýa-da secret nädogry ýa-da indi hereket etmeýär. Ikisini hem Authentification goýmasyndan täzeden göçüriň. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Programmaňyz şol API-e ýazylmadyk ýa-da siz onuň şertlerini kabul etmediňiz. 2-nji we 3-nji ädimlere serediň. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | ABŞ açary ýok. Gözleg günde birnäçe gezek işleýär. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Demo açaryň çägi gutardy. Öz açaryňyzy goşuň. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Açar nädogry ýa-da e-poçtadaky hat arkaly entek tassyklanmadyk. |

Boş baha açar ýok hasaplanýar.

## Rugsatlar (WLM_PERMITTED)

Bu API açary däl we gurnaýjy ony sazlamaýar. **Ony diňe özüňizde şol rugsat bar bolsa goýuň.**

Käbir çeşmeler adaty ýagdaýda öçük, sebäbi olaryň şertleri ýa-da robots.txt faýly rugsatsyz
awtomatik ulanylyşy gadagan edýär. Eger neşir edijiden rugsadyňyz bar bolsa, çeşmäniň kodyny
`env` blokundaky `WLM_PERMITTED` içine otur bilen bölüp goşup, ony açyň:
`"WLM_PERMITTED": "in,de"`.

| Kod | Çeşme |
|---|---|
| `az` | Azerbaýjan: e-qanun.az (Adalat ministrligi) |
| `bh` | Bahreýn: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Kolumbiýa: Función Pública, Gestor Normativo (ähli üýtgetmeler girizilen kanunçylyk) |
| `de` | Germaniýa: NeuRIS (federal hukuk maglumat portaly, synag hyzmaty) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Gresiýa: Milli metbugat, Hökümet býulleteni gözlegi (search.et.gr) |
| `in` | Hindistan: India Code (indiacode.gov.in) |
| `mu` | Mawrikiý: Ýokary kazyýet (supremecourt.govmu.org) |
| `sg` | Singapur: kazyýet çözgütleri (elitigation.sg) |

Rugsatsyz Fontes şeýle diýýär: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
