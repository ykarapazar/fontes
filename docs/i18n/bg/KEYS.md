> Това е машинно подпомогнат превод. Меродавна е версията на английски език.

# API ключове

Почти всички източници във Fontes работят без ключ. Два изискват безплатен ключ:

| Ключ | Какво отключва | Без него |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Франция: Judilibre (съдебни решения) и Légifrance (законодателство) | Франция е изключена. `list_jurisdictions` я показва като неактивна. |
| `WLM_US_GOVINFO_KEY` | САЩ: търсене в govinfo (решения на федералните съдилища, Statutes at Large, публични закони) | Fontes използва общия `DEMO_KEY`: около 10 търсения на ден от един IP адрес. За отваряне на известно решение и за US Code не е нужен ключ. |

Ключовете не са задължителни. Можете да ги добавите по-късно.

## Добавяне на ключ

**С инсталатора.** По време на инсталирането инсталаторът пита дали искате да добавите
ключове. Изберете **Не сега** (или натиснете Enter), за да пропуснете. За да добавите или
промените ключове по-късно, стартирайте **Add or change keys**:

- Mac: отворете отново приложението Fontes Installer и изберете **Добавяне или промяна на
  ключове** или щракнете двукратно върху `Add or change keys.command` в папката на инсталатора.
- Windows: щракнете двукратно върху `Add or change keys.cmd` в папката на инсталатора.
  Инсталационната програма за Windows, когато бъде налична, ще го постави и в менюто „Старт“ >
  Fontes.

Въвежданото не се показва. За всеки ключ: поставете го, натиснете Enter, за да запазите
текущата стойност, или въведете `-`, за да го премахнете. Ключовете се записват във всяко
приложение, в което вече има Fontes.

**С разширението за Claude Desktop (.mcpb).** Отворете Claude > Settings > Extensions > Fontes и
попълнете полетата. Всички те са незадължителни.

**Ръчно.** Добавете променливите в блока `env` на записа `fontes` в MCP конфигурацията на
приложението си:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

След всяка промяна рестартирайте приложението.

## Франция: PISTE (безплатно)

1. Създайте профил в [piste.gouv.fr](https://piste.gouv.fr). Това означава да приемете
   условията на PISTE (CGU).
2. Отидете в API > **Consentement CGU API**. Приемете условията за **JUDILIBRE** и
   **Légifrance** (production).
3. Създайте **production приложение** (production application). Създаденото за вас
   `APP_SANDBOX` няма достъп до production. В "Modifier l'application" отметнете
   **JUDILIBRE (production)** и **Légifrance (production)**, след това приложете.
4. Отворете раздела **Authentification** на приложението. Копирайте `client_id` и
   `client_secret`.
5. Стартирайте **Add or change keys** и ги поставете.

Условията накратко:

- Данни: Licence Ouverte / Etalab 2.0. Повторната употреба, включително търговската, е
  разрешена с посочване на източника.
- Не публикувайте и не споделяйте идентификационните си данни. Уведомете PISTE, ако изтекат.
- API на Légifrance е бета услуга. Тя може да бъде спряна и има квоти (на секунда, минута и
  ден).
- Текстовете в Légifrance не са автентичната версия. Автентичен е само подписаният PDF на
  Journal officiel.
- Judilibre: не използвайте имената на съдии или съдебни служители, за да оценявате,
  сравнявате или прогнозирате тяхната работа (Code de l'organisation judiciaire, чл. L111-13;
  престъпление).
- Judilibre: спазвайте GDPR. Не се опитвайте да идентифицирате повторно страните.

Квотите ви са в PISTE в API Sélectionnées > Actions > Consulter les quotas.

## САЩ: api.data.gov (безплатно)

1. Отидете на [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (ключът се показва на
   екрана) или на [api.data.gov/signup](https://api.data.gov/signup/) (ключът ви се изпраща по
   имейл).
2. Въведете името и имейла си. Полето "how will you use it" не е задължително.
3. Копирайте ключа от 40 знака.
4. Стартирайте **Add or change keys** и го поставете като ключ за САЩ.

Условията накратко:

- Със собствен ключ govinfo позволява до 36,000 заявки на час.
- Не открихме условия за ползване, специфични за API (api.data.gov/terms/ не съществува).
  Непроверено. Вижте [политиките на govinfo](https://www.govinfo.gov/about/policies) и
  [политиката за поверителност на data.gov](https://data.gov/privacy-policy/).
- Не споделяйте ключа с никого.

## Къде се съхраняват ключовете

- **С инсталатора или ръчно:** като обикновен текст във файла с MCP конфигурацията на всяко
  приложение, в блока `env` на записа `fontes`. Всеки, който може да чете потребителските ви
  файлове, може да прочете ключовете.
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
- **Разширението за Claude Desktop (.mcpb):** Claude пази тези полета в настройките си и ги
  защитава със защитеното хранилище на системата ви (Keychain на Mac, Credential Manager на
  Windows).

Преди всяка промяна инсталаторът запазва до файла с конфигурацията негово копие
(`<file>.fontes-backup-<time>`). Копията, направени след добавянето на ключове, също съдържат
ключовете. Изтрийте старите копия, които не ви трябват.

## Промяна или премахване на ключ

- Стартирайте **Add or change keys**. Поставете нов ключ, за да замените стария, или въведете
  `-`, за да го премахнете.
- Или редактирайте блока `env` ръчно и рестартирайте приложението.
- Деинсталирането на Fontes премахва целия му запис, включително ключовете. То не изтрива
  резервните копия.
- Ако ключ е изтекъл, сменете го и при източника: в PISTE създайте нови идентификационни данни
  за приложението си; за api.data.gov се регистрирайте за нов ключ.

## Съобщения, които може да видите

| Съобщение | Значение |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Няма ключ за Франция. Добавете такъв. |
| `Inactive: needs a free PISTE account. ...` (в `list_jurisdictions`) | Същото. |
| `PISTE refused the client credentials ...` | ID или secret е грешен или вече не е валиден. Копирайте отново и двете от раздела Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Приложението ви не е абонирано за този API или не сте приели условията му. Вижте стъпки 2 и 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Няма ключ за САЩ. Търсенето работи за няколко извиквания на ден. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Демо ключът е изчерпан. Добавете собствен ключ. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Ключът е грешен или още не е потвърден от имейла. |

Празна стойност се счита за липса на ключ.

## Разрешения (WLM_PERMITTED)

Това не е API ключ и инсталаторът не го задава. **Задавайте го само ако вие лично притежавате
това разрешение.**

Някои източници са изключени по подразбиране, защото условията им или robots.txt забраняват
автоматизираната употреба без разрешение. Ако имате разрешение от издателя, включете източника,
като добавите кода му в `WLM_PERMITTED`, разделен със запетаи, в блока `env`:
`"WLM_PERMITTED": "in,de"`.

| Код | Източник |
|---|---|
| `az` | Азербайджан: e-qanun.az (Министерство на правосъдието) |
| `bh` | Бахрейн: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Колумбия: Función Pública, Gestor Normativo (консолидирано законодателство) |
| `de` | Германия: NeuRIS (федерален портал за правна информация, пробна услуга) |
| `difc` | Съдилищата на Дубайския международен финансов център (difccourts.ae) |
| `gr` | Гърция: Национална печатница, търсене в Правителствения вестник (search.et.gr) |
| `in` | Индия: India Code (indiacode.gov.in) |
| `mu` | Мавриций: Върховен съд (supremecourt.govmu.org) |
| `sg` | Сингапур: съдебни решения (elitigation.sg) |

Без разрешение Fontes казва: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
