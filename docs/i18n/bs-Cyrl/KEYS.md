> Ово је машински потпомогнут пријевод. Мјеродавна је верзија на енглеском.

# API кључеви

Готово сваки извор у алату Fontes ради без кључа. Три извора захтијевају бесплатан кључ:

| Кључ | Откључава | Без њега |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Француска: Judilibre (судске одлуке) и Légifrance (прописи) | Француска је искључена. `list_jurisdictions` је приказује као неактивну. |
| `WLM_US_GOVINFO_KEY` | Сједињене Америчке Државе: претрага говинфо (мишљења савезних судова, Statutes at Large, public laws) | Fontes користи заједнички `DEMO_KEY`: око 10 претрага дневно по IP адреси. За отварање познате одлуке и за US Code кључ није потребан. |
| `WLM_US_COURTLISTENER_KEY` | Судови држава САД-а (`us-states`): мишљења врховних и апелационих судова свих 50 држава и DC-а, из CourtListener-а | Судска пракса држава САД-а је искључена. `list_jurisdictions` је приказује као неактивну. |

Кључеви су опционални. Можете их додати и касније.

## Додавање кључа

**Помоћу инсталацијског програма.** Када је Fontes постављен, инсталацијски програм нуди да додате
кључеве. На Mac-у кликните на **Додај кључеве** или на **Готово** да прескочите; на Windows-у
одговорите на питање (притисните Enter да прескочите). Да касније додате или промијените кључеве,
покрените **Add or change keys**:

- Mac: поново отворите апликацију Fontes Installer и одаберите **Додај или промијени кључеве**.
- Windows: отворите Start menu, па **Fontes** → **Додај или промијени кључеве**.

Унос се не приказује. За сваки кључ: залијепите га, притисните Enter да задржите постојећи или
укуцајте `-` да га уклоните. Кључеви се уписују у сваку апликацију која већ има Fontes.

**Помоћу проширења за Claude Desktop (.mcpb).** Отворите Claude > Settings > Extensions > Fontes
и попуните поља. Сва су опционална.

**Ручно.** Додајте варијабле у блок `env` уноса `fontes` у MCP конфигурацији своје апликације:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Након сваке измјене поново покрените апликацију.

## Француска: PISTE (бесплатно)

1. Направите рачун на [piste.gouv.fr](https://piste.gouv.fr). То значи прихватање услова PISTE (CGU).
2. Идите на API > **Consentement CGU API**. Прихватите услове за **JUDILIBRE** и **Légifrance** (production).
3. Направите **production application**. `APP_SANDBOX` који је направљен за вас не може приступити продукцији.
   Под "Modifier l'application" означите **JUDILIBRE (production)** и **Légifrance (production)**, затим примијените.
4. Отворите картицу **Authentification** апликације. Копирајте `client_id` и `client_secret`.
5. Покрените **Add or change keys** и залијепите их.

Услови, укратко:

- Подаци: Licence Ouverte / Etalab 2.0. Поновна употреба, укључујући комерцијалну, дозвољена је уз навођење извора.
- Не објављујте и не дијелите своје приступне податке. Обавијестите PISTE ако процуре.
- API Légifrance је бета услуга. Може бити обустављен и има квоте (по секунди, минути и дану).
- Текстови на Légifrance нису аутентична верзија. Аутентичан је само потписани PDF Journal officiel.
- Judilibre: не користите имена судија или службеника суда за оцјењивање, поређење или
  предвиђање њиховог рада (Code de l'organisation judiciaire чл. L111-13; кривично дјело).
- Judilibre: поштујте GDPR. Не покушавајте поново идентификовати странке.

Своје квоте видите на PISTE под API Sélectionnées > Actions > Consulter les quotas.

## Сједињене Америчке Државе: api.data.gov (бесплатно)

1. Идите на [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (кључ се приказује на екрану)
   или [api.data.gov/signup](https://api.data.gov/signup/) (кључ вам се шаље е-поштом).
2. Унесите своје име и е-маил адресу. Поље "how will you use it" је опционално.
3. Копирајте кључ од 40 знакова.
4. Покрените **Add or change keys** и залијепите га као кључ за САД.

Услови, укратко:

- С властитим кључем говинфо допушта до 36.000 захтјева на сат.
- Нисмо пронашли услове кориштења специфичне за API (api.data.gov/terms/ не постоји). Непровјерено.
  Погледајте [правила за говинфо](https://www.govinfo.gov/about/policies) и
  [политику приватности data.gov](https://data.gov/privacy-policy/).
- Кључ задржите за себе.

## Судови држава САД-а: CourtListener (бесплатно)

CourtListener води [Free Law Project](https://free.law), непрофитна организација која од 2010. прикупља мишљења судова САД-а и чини их бесплатним за све. Према властитом бројању, садржи више од девет милиона одлука. Није званичан извор: судови сами објављују своја мишљења, а CourtListener их прикупља с веб страница судова и из скенираних збирки судских одлука. Сваки одговор алата Fontes који потиче из њега то наводи. Fontes није повезан с Free Law Project-ом.

1. Направите бесплатан рачун на [courtlistener.com](https://www.courtlistener.com/sign-in/).
2. Отворите свој профил и копирајте свој API токен.
3. Покрените **Add or change keys** и залијепите га као CourtListener кључ.

Услови, укратко ([потпуни услови](https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies)):

- Токен је само ваш: не дијелите га, не обједињујте га с другима и не препродајте га, и не користите више рачуна.
- Ви одговарате за оно што апликација с вјештачком интелигенцијом ради с вашим токеном.
- Не представљајте анализу вјештачке интелигенције њихових података као да ју је израдио, одобрио или провјерио Free Law Project.
- Бесплатан рачун допушта 5 захтјева у минуту, 50 на сат и 125 на дан. Једна претрага је један захтјев; отварање одлуке су два. Чланство у Free Law Project-у повећава ограничења.
- CourtListener не јамчи тачност. Провјерите мишљење у примјерку суда прије него што се на њега ослоните.

## Гдје се кључеви чувају

- **Инсталацијски програм или ручно:** као обичан текст у MCP конфигурацијској датотеци сваке
  апликације, у блоку `env` уноса `fontes`. Свако ко може читати ваше корисничке датотеке може
  прочитати и кључеве.
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
- **Проширење за Claude Desktop (.mcpb):** Claude чува ова поља у својим поставкама и штити их
  сигурном похраном вашег система (Keychain на Macu, Credential Manager на Windows-у).

Прије сваке измјене, инсталацијски програм сачува копију конфигурацијске датотеке поред ње
(`<file>.fontes-backup-<time>`). Копије направљене након што сте додали кључеве такођер садрже
кључеве. Обришите старе копије које вам не требају.

## Промјена или уклањање кључа

- Покрените **Add or change keys**. Залијепите нови кључ да замијените постојећи или укуцајте `-`
  да га уклоните.
- Или ручно уредите блок `env` и поново покрените апликацију.
- Деинсталација програма Fontes уклања цијели његов унос, заједно с кључевима. Не брише
  резервне копије.
- Ако је кључ процурио, замијените га и код извора: на PISTE направите нове приступне податке за
  своју апликацију; за api.data.gov се пријавите за нови кључ.

## Поруке које можете видјети

| Порука | Значење |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Нема кључа за Француску. Додајте га. |
| `Inactive: needs a free PISTE account. ...` (у `list_jurisdictions`) | Исто. |
| `PISTE refused the client credentials ...` | ID или сецрет је погрешан или више не важи. Поново копирајте оба с картице Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Ваша апликација није претплаћена на тај API или нисте прихватили његове услове. Погледајте кораке 2 и 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Нема кључа за САД. Претрага ради за неколико позива дневно. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Демо кључ је потрошен. Додајте властити кључ. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Кључ је погрешан или још није потврђен путем е-поште. |

Празна вриједност се рачуна као да кључа нема.

## Дозволе (WLM_PERMITTED)

Ово није API кључ и инсталацијски програм га не поставља. **Поставите га само ако ту дозволу
имате ви лично.**

Неки извори су задано искључени јер њихови услови или robots.txt забрањују аутоматизовану
употребу без дозволе. Ако имате дозволу издавача, укључите извор тако што ћете његов код додати
у `WLM_PERMITTED`, одвојено зарезима, у блоку `env`: `"WLM_PERMITTED": "in,de"`.

| Код | Извор |
|---|---|
| `az` | Азербејџан: e-qanun.az (Министарство правде) |
| `bh` | Бахреин: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Колумбија: Función Pública, Gestor Normativo (пречишћени прописи) |
| `de` | Њемачка: NeuRIS (савезни портал правних информација, пробна услуга) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Грчка: National Printing Office, претрага Government Gazette (search.et.gr) |
| `mu` | Маурицијус: Supreme Court (supremecourt.govmu.org) |
| `sg` | Сингапур: судске пресуде (elitigation.sg) |

Без дозволе Fontes каже: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
