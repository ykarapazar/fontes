> Бу машина ёрдамида қилинган таржима. Инглиз тилидаги матн асосий ҳисобланади.

# API калитлари

Fontes'даги деярли барча манбалар калитсиз ишлайди. Иккитасига бепул калит керак:

| Калит | Нимани очади | Калитсиз |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Франция: Judilibre (суд қарорлари) ва Légifrance (қонунчилик) | Франция ўчиқ. `list_jurisdictions` уни нофаол деб кўрсатади. |
| `WLM_US_GOVINFO_KEY` | Америка Қўшма Штатлари: govinfo қидируви (федерал суд қарорлари, Statutes at Large, public laws) | Fontes умумий `DEMO_KEY` дан фойдаланади: ҳар бир IP манзил учун кунига тахминан 10 та қидирув. Маълум қарорни очиш ва US Code учун калит керак эмас. |

Калитлар ихтиёрий. Уларни кейинроқ қўшишингиз мумкин.

## Калит қўшиш

**Ўрнатувчи орқали.** Fontes созлангандан сўнг ўрнатувчи калит қўшишни таклиф қилади. Mac'да
**Калитларни қўшиш** ни босинг ёки ўтказиб юбориш учун **Тайёр** ни босинг; Windows'да саволга жавоб
беринг (ўтказиб юбориш учун Enter тугмасини босинг). Калитларни кейинроқ қўшиш ёки ўзгартириш учун
**Add or change keys** ни ишга туширинг:

- Mac: Fontes Installer иловасини қайта очинг ва **Калитларни қўшиш ёки ўзгартириш** ни танланг.
- Windows: ўрнатувчи жилдидаги `Add or change keys.cmd` ни икки марта босинг. Windows ўрнатиш
  дастури чиққанда уни Start menu > Fontes га ҳам жойлаштиради.

Ёзилаётган матн яширин бўлади. Ҳар бир калит учун: уни жойлаштиринг, мавжудини сақлаб қолиш
учун Enter тугмасини босинг ёки олиб ташлаш учун `-` ёзинг. Калитлар Fontes аллақачон мавжуд
бўлган ҳар бир иловага киритилади.

**Claude Desktop кенгайтмаси (.mcpb) орқали.** Claude > Settings > Extensions > Fontes ни очинг
ва майдонларни тўлдиринг. Уларнинг барчаси ихтиёрий.

**Қўлда.** Ўзгарувчиларни иловангиз MCP созламасидаги `fontes` ёзувининг `env` блокига қўшинг:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Ҳар қандай ўзгаришдан кейин иловани қайта ишга туширинг.

## Франция: PISTE (бепул)

1. [piste.gouv.fr](https://piste.gouv.fr) да ҳисоб қайдномаси яратинг. Бу PISTE шартларини (CGU)
   қабул қилишни англатади.
2. API > **Consentement CGU API** бўлимига ўтинг. **JUDILIBRE** ва **Légifrance** (production)
   шартларини қабул қилинг.
3. **Production application** яратинг. Сиз учун яратилган `APP_SANDBOX` production'га кира
   олмайди. “Modifier l'application” остида **JUDILIBRE (production)** ва **Légifrance
   (production)** ни белгиланг, сўнг қўлланг.
4. Илованинг **Authentification** ёрлиғини очинг. `client_id` ва `client_secret` ни нусхаланг.
5. **Add or change keys** ни ишга туширинг ва уларни жойлаштиринг.

Шартлар, қисқача:

- Маълумотлар: Licence Ouverte / Etalab 2.0. Қайта фойдаланиш, жумладан тижорий қайта
  фойдаланиш, муаллифликни кўрсатган ҳолда рухсат этилади.
- Ҳисоб маълумотларингизни эълон қилманг ва бошқаларга берманг. Улар сизиб чиқса, PISTE'га
  хабар беринг.
- Légifrance API — бета хизмат. У тўхтатилиши мумкин ва унда квоталар бор (секунд, дақиқа ва
  кун бўйича).
- Légifrance матнлари ҳақиқий таҳрир эмас. Фақат имзоланган Journal officiel PDF'и ҳақиқий.
- Judilibre: судьялар ёки суд котибларининг исмларидан уларнинг ишини баҳолаш, солиштириш ёки
  башорат қилиш учун фойдаланманг (Code de l'organisation judiciaire, L111-13-модда; жиноят).
- Judilibre: GDPR талабларига риоя қилинг. Тарафларни қайта идентификация қилишга уринманг.

Квоталарингиз PISTE'да API Sélectionnées > Actions > Consulter les quotas остида.

## Америка Қўшма Штатлари: api.data.gov (бепул)

1. [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) га (калит экранда кўрсатилади)
   ёки [api.data.gov/signup](https://api.data.gov/signup/) га (калит электрон почтангизга
   юборилади) ўтинг.
2. Исмингиз ва электрон почтангизни киритинг. “How will you use it” майдони ихтиёрий.
3. 40 белгили калитни нусхаланг.
4. **Add or change keys** ни ишга туширинг ва уни АҚШ калити сифатида жойлаштиринг.

Шартлар, қисқача:

- Ўз калитингиз билан govinfo соатига 36 000 тагача сўровга рухсат беради.
- Биз API'га хос фойдаланиш шартларини топмадик (api.data.gov/terms/ мавжуд эмас).
  Текширилмаган. Қаранг: [govinfo сиёсатлари](https://www.govinfo.gov/about/policies) ва
  [data.gov махфийлик сиёсати](https://data.gov/privacy-policy/).
- Калитни ўзингизда сақланг.

## Калитлар қаерда сақланади

- **Ўрнатувчи орқали ёки қўлда:** ҳар бир илованинг MCP созлама файлида, `fontes` ёзувининг
  `env` блокида оддий матн сифатида. Фойдаланувчи файлларингизни ўқий оладиган ҳар ким
  калитларни ўқий олади.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` ёки `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Claude Desktop кенгайтмаси (.mcpb):** Claude бу майдонларни ўз созламаларида сақлайди ва
  уларни тизимингизнинг хавфсиз хотираси (Mac'да Keychain, Windows'да Credential Manager)
  билан ҳимоя қилади.

Ҳар бир ўзгаришдан олдин ўрнатувчи созлама файлининг нусхасини унинг ёнида сақлайди
(`<file>.fontes-backup-<time>`). Калитларни қўшганингиздан кейин яратилган нусхаларда калитлар
ҳам бўлади. Кераги бўлмаган эски нусхаларни ўчиринг.

## Калитни ўзгартириш ёки олиб ташлаш

- **Add or change keys** ни ишга туширинг. Алмаштириш учун янги калитни жойлаштиринг ёки олиб
  ташлаш учун `-` ёзинг.
- Ёки `env` блокини қўлда таҳрирланг ва иловани қайта ишга туширинг.
- Fontes'ни олиб ташлаш унинг бутун ёзувини, калитлар билан бирга, олиб ташлайди. У заҳира
  нусхаларни ўчирмайди.
- Агар калит сизиб чиққан бўлса, уни манбада ҳам алмаштиринг: PISTE'да иловангиз учун янги
  ҳисоб маълумотларини яратинг; api.data.gov учун янги калитга рўйхатдан ўтинг.

## Сиз кўриши мумкин бўлган хабарлар

| Хабар | Маъноси |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Франция калити йўқ. Уни қўшинг. |
| `Inactive: needs a free PISTE account. ...` (`list_jurisdictions` да) | Худди шундай. |
| `PISTE refused the client credentials ...` | ID ёки secret нотўғри ёки энди амал қилмайди. Иккаласини Authentification ёрлиғидан қайта нусхаланг. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Иловангиз шу API'га обуна қилинмаган ёки унинг шартларини қабул қилмагансиз. 2- ва 3-қадамларга қаранг. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | АҚШ калити йўқ. Қидирув кунига бир неча марта ишлайди. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Демо калит лимити тугади. Ўз калитингизни қўшинг. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Калит нотўғри ёки электрон почтадаги хат орқали ҳали тасдиқланмаган. |

Бўш қиймат калит йўқ деб ҳисобланади.

## Рухсатлар (WLM_PERMITTED)

Бу API калити эмас ва ўрнатувчи уни созламайди. **Уни фақат ўзингиз шу рухсатга эга бўлсангиз
созланг.**

Баъзи манбалар стандарт ҳолатда ўчиқ, чунки уларнинг шартлари ёки robots.txt рухсатсиз
автоматлаштирилган фойдаланишни тақиқлайди. Агар нашр этувчидан рухсатингиз бўлса, манбанинг
кодини `env` блокидаги `WLM_PERMITTED` га вергул билан ажратиб қўшиб, уни ёқинг:
`"WLM_PERMITTED": "in,de"`.

| Код | Манба |
|---|---|
| `az` | Озарбайжон: e-qanun.az (Адлия вазирлиги) |
| `bh` | Баҳрайн: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Колумбия: Función Pública, Gestor Normativo (барча ўзгартишлар киритилган қонунчилик) |
| `de` | Германия: NeuRIS (федерал ҳуқуқий ахборот портали, синов хизмати) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Греция: Миллий босмахона, Ҳукумат ахборотномаси қидируви (search.et.gr) |
| `in` | Ҳиндистон: India Code (indiacode.gov.in) |
| `mu` | Маврикий: Олий суд (supremecourt.govmu.org) |
| `sg` | Сингапур: суд қарорлари (elitigation.sg) |

Рухсатсиз Fontes шундай дейди: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
