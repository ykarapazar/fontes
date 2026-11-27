> Ин тарҷума бо ёрии мошин омода шудааст. Нусхаи англисӣ асосӣ ба ҳисоб меравад.

# Калидҳои API

Қариб ҳамаи манбаъҳо дар Fontes бе калид кор мекунанд. Ба сетоаш калиди ройгон лозим аст:

| Калид | Чиро мекушояд | Бе он |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Фаронса: Judilibre (қарорҳои судӣ) ва Légifrance (қонунгузорӣ) | Фаронса хомӯш аст. `list_jurisdictions` онро ғайрифаъол нишон медиҳад. |
| `WLM_US_GOVINFO_KEY` | Иёлоти Муттаҳидаи Амрико: ҷустуҷӯи govinfo (қарорҳои судҳои федералӣ, Statutes at Large, public laws) | Fontes `DEMO_KEY`-и умумиро истифода мебарад: тақрибан 10 ҷустуҷӯ дар як рӯз барои як суроғаи IP. Барои кушодани қарори маълум ва US Code калид лозим нест. |
| `WLM_US_COURTLISTENER_KEY` | Судҳои иёлотии ИМА (`us-states`): қарорҳои судҳои олӣ ва аппелятсионии ҳамаи 50 иёлот ва DC аз CourtListener | Таҷрибаи судии иёлотҳои ИМА хомӯш аст. `list_jurisdictions` онро ҳамчун ғайрифаъол нишон медиҳад. |

Калидҳо ихтиёрӣ мебошанд. Шумо метавонед онҳоро баъдтар илова кунед.

## Илова кардани калид

**Бо насбкунанда.** Пас аз танзим шудани Fontes насбкунанда илова кардани калидҳоро пешниҳод
мекунад. Дар Mac **Илова кардани калидҳо**-ро пахш кунед ё барои гузаштан **Тайёр**-ро; дар Windows
ба савол ҷавоб диҳед (барои гузаштан Enter-ро пахш кунед). Барои баъдтар илова ё тағйир додани
калидҳо **Add or change keys**-ро иҷро кунед:

- Mac: барномаи Fontes Installer-ро аз нав кушоед ва **Илова ё тағйир додани калидҳо**-ро интихоб
  кунед.
- Windows: менюи Start-ро кушоед, сипас **Fontes** → **Илова ё тағйир додани калидҳо**.

Матни чопшаванда пинҳон аст. Барои ҳар калид: онро гузоред, барои нигоҳ доштани он чи ҳаст
Enter-ро пахш кунед ё барои хориҷ кардан `-` нависед. Калидҳо ба ҳар барномае, ки аллакай
Fontes дорад, ворид мешаванд.

**Бо васеъкунандаи Claude Desktop (.mcpb).** Claude > Settings > Extensions > Fontes-ро
кушоед ва майдонҳоро пур кунед. Ҳамаи онҳо ихтиёрӣ мебошанд.

**Дастӣ.** Тағйирёбандаҳоро ба блоки `env`-и сабти `fontes` дар танзимоти MCP-и барномаи худ
илова кунед:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Пас аз ҳар тағйир барномаро аз нав оғоз кунед.

## Фаронса: PISTE (ройгон)

1. Дар [piste.gouv.fr](https://piste.gouv.fr) ҳисоб эҷод кунед. Ин маънои қабул кардани
   шартҳои PISTE (CGU)-ро дорад.
2. Ба API > **Consentement CGU API** гузаред. Шартҳоро барои **JUDILIBRE** ва **Légifrance**
   (production) қабул кунед.
3. **Production application** эҷод кунед. `APP_SANDBOX`, ки барои шумо сохта шудааст, ба
   production дастрасӣ надорад. Дар зери "Modifier l'application" **JUDILIBRE (production)** ва
   **Légifrance (production)**-ро қайд кунед, сипас татбиқ кунед.
4. Ҷадвалаки **Authentification**-и барномаро кушоед. `client_id` ва `client_secret`-ро нусха
   бардоред.
5. **Add or change keys**-ро иҷро кунед ва онҳоро гузоред.

Шартҳо, мухтасар:

- Маълумот: Licence Ouverte / Etalab 2.0. Истифодаи такрорӣ, аз ҷумла истифодаи такрории
  тиҷоратӣ, бо зикри муаллиф иҷозат дода мешавад.
- Маълумоти ҳисоби худро нашр накунед ва ба дигарон надиҳед. Агар онҳо фош шаванд, ба PISTE
  хабар диҳед.
- API-и Légifrance хизматрасонии бета аст. Он метавонад боздошта шавад ва квотаҳо дорад (дар
  як сония, дақиқа ва рӯз).
- Матнҳои Légifrance версияи аслӣ нестанд. Танҳо PDF-и имзошудаи Journal officiel аслӣ аст.
- Judilibre: номҳои судяҳо ё котибони судро барои арзёбӣ, муқоиса ё пешгӯии кори онҳо
  истифода набаред (Code de l'organisation judiciaire, моддаи L111-13; ҷиноят).
- Judilibre: GDPR-ро риоя кунед. Кӯшиш накунед, ки тарафҳоро аз нав муайян кунед.

Квотаҳои шумо дар PISTE дар зери API Sélectionnées > Actions > Consulter les quotas мебошанд.

## Иёлоти Муттаҳидаи Амрико: api.data.gov (ройгон)

1. Ба [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (калид дар экран нишон
   дода мешавад) ё [api.data.gov/signup](https://api.data.gov/signup/) (калид ба почтаи
   электронии шумо фиристода мешавад) гузаред.
2. Ном ва почтаи электронии худро ворид кунед. Майдони "How will you use it" ихтиёрӣ аст.
3. Калиди 40-аломатиро нусха бардоред.
4. **Add or change keys**-ро иҷро кунед ва онро ҳамчун калиди ИМА гузоред.

Шартҳо, мухтасар:

- Бо калиди худатон govinfo то 36 000 дархост дар як соат иҷозат медиҳад.
- Мо шартҳои истифодаи махсуси API-ро наёфтем (api.data.gov/terms/ вуҷуд надорад). Санҷида
  нашудааст. Нигаред: [сиёсатҳои govinfo](https://www.govinfo.gov/about/policies) ва
  [сиёсати махфияти data.gov](https://data.gov/privacy-policy/).
- Калидро барои худ нигоҳ доред.

## Судҳои иёлотии ИМА: CourtListener (ройгон)

CourtListener-ро [Free Law Project](https://free.law), созмони ғайритиҷоратӣ идора мекунад, ки аз соли 2010 қарорҳои судҳои амрикоиро ҷамъ мекунад ва онҳоро ройгон ба ҳама дастрас менамояд. Тибқи ҳисоби худаш, он зиёда аз нӯҳ миллион қарорро дар бар мегирад. Он манбаи расмӣ нест: судҳо қарорҳои худро худашон нашр мекунанд ва CourtListener онҳоро аз сомонаҳои судҳо ва маҷмӯаҳои скандашудаи қарорҳо ҷамъ мекунад. Ҳар посухи Fontes аз он инро мегӯяд. Fontes ба Free Law Project алоқаманд нест.

1. Дар [courtlistener.com](https://www.courtlistener.com/sign-in/) ҳисоби ройгон эҷод кунед.
2. Профили худро кушоед ва токени API-и худро нусха бардоред.
3. **Add or change keys**-ро иҷро кунед ва онро ҳамчун калиди CourtListener гузоред.

Шартҳо, мухтасар ([шартҳои пурра](https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies)):

- Токен танҳо аз они шумост: онро ба дигарон надиҳед, бо дигарон муттаҳид накунед ва аз нав нафурӯшед ва якчанд ҳисобро истифода набаред.
- Шумо барои он ки барномаи AI бо токени шумо чӣ кор мекунад, масъул ҳастед.
- Таҳлили AI аз рӯи маълумоти онҳоро ҳамчун таҳияшуда, тасдиқшуда ё санҷидашудаи Free Law Project пешниҳод накунед.
- Ҳисоби ройгон 5 дархост дар як дақиқа, 50 дар як соат ва 125 дар як рӯзро иҷозат медиҳад. Як ҷустуҷӯ як дархост аст; кушодани як қарор ду дархост. Узвият дар Free Law Project маҳдудиятҳоро зиёд мекунад.
- CourtListener дурустиро кафолат намедиҳад. Пеш аз такя ба як қарор, онро бо нусхаи суд санҷед.

## Калидҳо дар куҷо нигоҳ дошта мешаванд

- **Бо насбкунанда ё дастӣ:** ҳамчун матни оддӣ дар файли танзимоти MCP-и ҳар барнома, дар
  блоки `env`-и сабти `fontes`. Ҳар касе, ки файлҳои корбарии шуморо хонда метавонад, калидҳоро
  хонда метавонад.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` ё `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Васеъкунандаи Claude Desktop (.mcpb):** Claude ин майдонҳоро дар танзимоти худ нигоҳ
  медорад ва онҳоро бо анбори бехатари системаи шумо (Keychain дар Mac, Credential Manager дар
  Windows) муҳофизат мекунад.

Пеш аз ҳар тағйир насбкунанда нусхаи файли танзимотро дар паҳлӯи он захира мекунад
(`<file>.fontes-backup-<time>`). Нусхаҳое, ки пас аз илова кардани калидҳо сохта шудаанд,
калидҳоро низ доранд. Нусхаҳои кӯҳнаеро, ки ба шумо лозим нестанд, нест кунед.

## Тағйир додан ё хориҷ кардани калид

- **Add or change keys**-ро иҷро кунед. Барои иваз кардан калиди навро гузоред ё барои хориҷ
  кардан `-` нависед.
- Ё блоки `env`-ро дастӣ таҳрир кунед ва барномаро аз нав оғоз кунед.
- Хориҷ кардани Fontes тамоми сабти онро, бо калидҳо, хориҷ мекунад. Он нусхаҳои эҳтиётиро
  нест намекунад.
- Агар калид фош шуда бошад, онро дар манбаъ низ иваз кунед: дар PISTE барои барномаи худ
  маълумоти ҳисоби нав эҷод кунед; барои api.data.gov барои калиди нав сабти ном кунед.

## Паёмҳое, ки шумо метавонед бинед

| Паём | Маъно |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Калиди Фаронса нест. Онро илова кунед. |
| `Inactive: needs a free PISTE account. ...` (дар `list_jurisdictions`) | Ҳамин. |
| `PISTE refused the client credentials ...` | ID ё secret нодуруст аст ё дигар эътибор надорад. Ҳардуро аз ҷадвалаки Authentification аз нав нусха бардоред. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Барномаи шумо ба он API обуна нашудааст ё шумо шартҳои онро қабул накардаед. Қадамҳои 2 ва 3-ро бинед. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Калиди ИМА нест. Ҷустуҷӯ барои чанд даъват дар як рӯз кор мекунад. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Калиди намоишӣ тамом шуд. Калиди худро илова кунед. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Калид нодуруст аст ё ҳанӯз аз почтаи электронӣ тасдиқ нашудааст. |

Қимати холӣ ҳамчун набудани калид ҳисоб мешавад.

## Иҷозатҳо (WLM_PERMITTED)

Ин калиди API нест ва насбкунанда онро муқаррар намекунад. **Онро танҳо агар худатон он иҷозатро
дошта бошед, муқаррар кунед.**

Баъзе манбаъҳо бо нобаёнӣ хомӯш мебошанд, зеро шартҳо ё robots.txt-и онҳо истифодаи худкорро
бе иҷозат манъ мекунанд. Агар шумо аз нашркунанда иҷозат дошта бошед, манбаъро бо илова кардани
рамзи он ба `WLM_PERMITTED`, бо вергул ҷудо карда, дар блоки `env` фаъол кунед:
`"WLM_PERMITTED": "in,de"`.

| Рамз | Манбаъ |
|---|---|
| `az` | Озарбойҷон: e-qanun.az (Вазорати адлия) |
| `bh` | Баҳрайн: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Колумбия: Función Pública, Gestor Normativo (қонунгузории ҷамъбастшуда) |
| `de` | Олмон: NeuRIS (портали федералии иттилооти ҳуқуқӣ, хизматрасонии озмоишӣ) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Юнон: Матбааи миллӣ, ҷустуҷӯи Бюллетени ҳукумат (search.et.gr) |
| `in` | Ҳиндустон: India Code (indiacode.gov.in) |
| `mu` | Маврикий: Суди олӣ (supremecourt.govmu.org) |
| `sg` | Сингапур: қарорҳои судӣ (elitigation.sg) |

Бе иҷозат Fontes мегӯяд: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
