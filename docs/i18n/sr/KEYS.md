> Ово је машински потпомогнут превод. Меродавна је верзија на енглеском.

# API кључеви

Скоро сваки извор у програму Fontes ради без кључа. Трима је потребан бесплатан кључ:

| Кључ | Шта откључава | Без њега |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Француска: Judilibre (судске одлуке) и Légifrance (прописи) | Француска је искључена. `list_jurisdictions` је приказује као неактивну. |
| `WLM_US_GOVINFO_KEY` | Сједињене Државе: govinfo претрага (одлуке савезних судова, Statutes at Large, јавни закони) | Fontes користи заједнички `DEMO_KEY`: око 10 претрага дневно по IP адреси. За отварање познате одлуке и US Code кључ није потребан. |
| `WLM_US_COURTLISTENER_KEY` | Судови америчких савезних држава (`us-states`): одлуке највиших и апелационих судова свих 50 држава и DC, из CourtListener | Судска пракса америчких савезних држава је искључена. `list_jurisdictions` је приказује као неактивну. |

Кључеви су опциони. Можете их додати касније.

## Додавање кључа

**Помоћу инсталационог програма.** Када се Fontes подеси, инсталациони програм нуди да дода кључеве. На
Mac-у кликните на **Додај кључеве** или на **Готово** да бисте прескочили; на Windows-у одговорите
на питање (притисните Enter да бисте прескочили). Да бисте
касније додали или променили кључеве, покрените **Add or change keys**:

- Mac: поново отворите апликацију Fontes Installer и изаберите **Додај или промени кључеве**.
- Windows: отворите мени Start, па **Fontes** → **Додај или промени кључеве**.

Унос је скривен. За сваки кључ: налепите га, притисните Enter да задржите постојећи, или
укуцајте `-` да га уклоните. Кључеви се уписују у сваку апликацију која већ има Fontes.

**Помоћу Claude Desktop проширења (.mcpb).** Отворите Claude > Settings > Extensions > Fontes и
попуните поља. Сва су опциона.

**Ручно.** Додајте променљиве у блок `env` уноса `fontes` у MCP конфигурацији своје апликације:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Након сваке измене поново покрените апликацију.

## Француска: PISTE (бесплатно)

1. Направите налог на [piste.gouv.fr](https://piste.gouv.fr). То подразумева прихватање
   услова PISTE (CGU).
2. Идите на API > **Consentement CGU API**. Прихватите услове за **JUDILIBRE** и
   **Légifrance** (production).
3. Направите **production апликацију** (production application). `APP_SANDBOX` направљен за
   вас не може да приступи production окружењу. Под "Modifier l'application" означите
   **JUDILIBRE (production)** и **Légifrance (production)**, па примените.
4. Отворите картицу **Authentification** апликације. Копирајте `client_id` и `client_secret`.
5. Покрените **Add or change keys** и налепите их.

Услови, укратко:

- Подаци: Licence Ouverte / Etalab 2.0. Поновна употреба, укључујући комерцијалну, дозвољена је
  уз навођење извора.
- Не објављујте нити делите своје акредитиве. Обавестите PISTE ако процуре.
- Légifrance API је бета услуга. Може бити обустављена и има квоте (по секунди, минуту и дану).
- Текстови на Légifrance нису аутентична верзија. Аутентичан је само потписани PDF Journal
  officiel.
- Judilibre: не користите имена судија или судских службеника да бисте оцењивали, упоређивали
  или предвиђали њихов рад (Code de l'organisation judiciaire, чл. L111-13; кривично дело).
- Judilibre: поштујте GDPR. Не покушавајте да поново идентификујете странке.

Ваше квоте се налазе на PISTE под API Sélectionnées > Actions > Consulter les quotas.

## Сједињене Државе: api.data.gov (бесплатно)

1. Идите на [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (кључ се приказује на
   екрану) или [api.data.gov/signup](https://api.data.gov/signup/) (кључ вам се шаље имејлом).
2. Унесите своје име и имејл. Поље "how will you use it" је опционо.
3. Копирајте кључ од 40 знакова.
4. Покрените **Add or change keys** и налепите га као кључ за САД.

Услови, укратко:

- Са сопственим кључем, govinfo дозвољава до 36,000 захтева на сат.
- Нисмо пронашли услове коришћења специфичне за API (api.data.gov/terms/ не постоји).
  Непроверено. Погледајте [govinfo правила](https://www.govinfo.gov/about/policies) и
  [data.gov политику приватности](https://data.gov/privacy-policy/).
- Кључ задржите за себе.

## Судови америчких савезних држава: CourtListener (бесплатно)

CourtListener води [Free Law Project](https://free.law), непрофитна организација која од 2010. прикупља одлуке америчких судова и чини их бесплатно доступним свима. Према сопственим подацима, садржи преко девет милиона одлука. Није званичан извор: судови сами објављују своје одлуке, а CourtListener их прикупља са веб-сајтова судова и из скенираних зборника судске праксе. Сваки одговор програма Fontes из овог извора то наводи. Fontes није повезан са Free Law Project.

1. Направите бесплатан налог на [courtlistener.com](https://www.courtlistener.com/sign-in/).
2. Отворите свој профил и копирајте свој API токен.
3. Покрените **Add or change keys** и налепите га као CourtListener кључ.

Услови, укратко ([цели услови](https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies)):

- Токен је само ваш: не делите га, не здружујте и не препродајте, и не користите више налога.
- Одговорни сте за то шта апликација са вештачком интелигенцијом ради са вашим токеном.
- Не представљајте анализу њихових података коју је направила вештачка интелигенција као да су је направили, одобрили или проверили Free Law Project.
- Бесплатан налог дозвољава 5 захтева у минути, 50 на сат и 125 дневно. Претрага је један захтев; отварање одлуке су два. Чланство у Free Law Project повећава ограничења.
- CourtListener не гарантује тачност. Проверите одлуку у примерку суда пре него што се на њу ослоните.

## Где се кључеви чувају

- **Инсталациони програм или ручно:** као обичан текст у MCP конфигурационој датотеци сваке
  апликације, у блоку `env` уноса `fontes`. Свако ко може да чита ваше корисничке датотеке може
  да прочита кључеве.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` или `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Claude Desktop проширење (.mcpb):** Claude чува ова поља у својим подешавањима и штити их
  безбедним складиштем вашег система (Keychain на Mac-у, Credential Manager на Windows-у).

Пре сваке измене, инсталациони програм чува копију конфигурационе датотеке поред ње
(`<file>.fontes-backup-<time>`). Копије направљене након што сте додали кључеве такође садрже
кључеве. Обришите старе копије које вам нису потребне.

## Промена или уклањање кључа

- Покрените **Add or change keys**. Налепите нови кључ да бисте заменили стари, или укуцајте
  `-` да бисте га уклонили.
- Или ручно измените блок `env` и поново покрените апликацију.
- Деинсталација програма Fontes уклања цео његов унос, укључујући кључеве. Не брише резервне
  копије.
- Ако је кључ процурео, замените га и код извора: на PISTE направите нове акредитиве за своју
  апликацију; за api.data.gov региструјте нови кључ.

## Поруке које можете видети

| Порука | Значење |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Нема кључа за Француску. Додајте га. |
| `Inactive: needs a free PISTE account. ...` (у `list_jurisdictions`) | Исто. |
| `PISTE refused the client credentials ...` | ID или secret је погрешан или више не важи. Поново копирајте оба са картице Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Ваша апликација није претплаћена на тај API или нисте прихватили његове услове. Погледајте кораке 2 и 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Нема кључа за САД. Претрага ради за неколико позива дневно. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Демо кључ је потрошен. Додајте сопствени кључ. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Кључ је погрешан или још није потврђен преко имејла. |

Празна вредност се сматра као да кључа нема.

## Дозволе (WLM_PERMITTED)

Ово није API кључ и инсталациони програм га не подешава. **Подесите га само ако ту дозволу
лично имате.**

Неки извори су подразумевано искључени јер њихови услови или robots.txt забрањују
аутоматизовану употребу без дозволе. Ако имате дозволу издавача, укључите извор тако што ћете
његов код додати у `WLM_PERMITTED`, раздвојено зарезима, у блоку `env`:
`"WLM_PERMITTED": "in,de"`.

| Код | Извор |
|---|---|
| `az` | Азербејџан: e-qanun.az (Министарство правде) |
| `bh` | Бахреин: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Колумбија: Función Pública, Gestor Normativo (пречишћени прописи) |
| `de` | Немачка: NeuRIS (савезни портал правних информација, пробна услуга) |
| `difc` | Судови Међународног финансијског центра у Дубаију (difccourts.ae) |
| `gr` | Грчка: Национална штампарија, претрага Службеног гласника (search.et.gr) |
| `mu` | Маурицијус: Врховни суд (supremecourt.govmu.org) |
| `sg` | Сингапур: судске пресуде (elitigation.sg) |

Без дозволе, Fontes каже: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
