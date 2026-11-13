> Этот перевод выполнен с помощью машинного перевода. Определяющей является английская версия.

# API-ключи

Почти все источники в Fontes работают без ключа. Двум нужен бесплатный ключ:

| Ключ | Что открывает | Без него |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Франция: Judilibre (судебные решения) и Légifrance (законодательство) | Франция выключена. `list_jurisdictions` показывает её как неактивную. |
| `WLM_US_GOVINFO_KEY` | США: поиск govinfo (решения федеральных судов, Statutes at Large, публичные законы) | Fontes использует общий `DEMO_KEY`: около 10 поисков в день с одного IP-адреса. Для открытия известного решения и US Code ключ не нужен. |

Ключи необязательны. Вы можете добавить их позже.

## Добавление ключа

**С помощью установщика.** Во время установки установщик спрашивает, хотите ли вы добавить
ключи. Выберите **Не сейчас** (или нажмите Enter), чтобы пропустить. Чтобы добавить или изменить
ключи позже, запустите **Add or change keys**:

- Mac: снова откройте приложение Fontes Installer и выберите **Добавить или изменить ключи** или
  дважды щёлкните `Add or change keys.command` в папке установщика.
- Windows: дважды щёлкните `Add or change keys.cmd` в папке установщика. Программа установки для
  Windows, когда она появится, также поместит его в меню «Пуск» > Fontes.

Вводимые символы скрыты. Для каждого ключа: вставьте его, нажмите Enter, чтобы оставить текущее
значение, или введите `-`, чтобы удалить его. Ключи попадают в каждое приложение, в котором уже
есть Fontes.

**С помощью расширения Claude Desktop (.mcpb).** Откройте Claude > Settings > Extensions >
Fontes и заполните поля. Все они необязательны.

**Вручную.** Добавьте переменные в блок `env` записи `fontes` в MCP-конфигурации вашего
приложения:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

После любого изменения перезапустите приложение.

## Франция: PISTE (бесплатно)

1. Создайте учётную запись на [piste.gouv.fr](https://piste.gouv.fr). Для этого нужно принять
   условия PISTE (CGU).
2. Перейдите в API > **Consentement CGU API**. Примите условия для **JUDILIBRE** и
   **Légifrance** (production).
3. Создайте **production-приложение** (production application). Созданное для вас
   `APP_SANDBOX` не имеет доступа к production. В разделе "Modifier l'application" отметьте
   **JUDILIBRE (production)** и **Légifrance (production)**, затем примените.
4. Откройте вкладку **Authentification** приложения. Скопируйте `client_id` и `client_secret`.
5. Запустите **Add or change keys** и вставьте их.

Условия вкратце:

- Данные: Licence Ouverte / Etalab 2.0. Повторное использование, в том числе коммерческое,
  разрешено с указанием источника.
- Не публикуйте и никому не передавайте свои учётные данные. Если они утекли, сообщите PISTE.
- API Légifrance — бета-сервис. Его работа может быть приостановлена, и у него есть квоты (в
  секунду, минуту и день).
- Тексты Légifrance не являются аутентичной версией. Аутентичен только подписанный PDF Journal
  officiel.
- Judilibre: не используйте имена судей или секретарей суда, чтобы оценивать, сравнивать или
  прогнозировать их работу (Code de l'organisation judiciaire, ст. L111-13; уголовное
  преступление).
- Judilibre: соблюдайте GDPR. Не пытайтесь повторно идентифицировать стороны.

Ваши квоты находятся на PISTE в разделе API Sélectionnées > Actions > Consulter les quotas.

## США: api.data.gov (бесплатно)

1. Перейдите на [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (ключ показывается
   на экране) или [api.data.gov/signup](https://api.data.gov/signup/) (ключ приходит вам по
   электронной почте).
2. Введите своё имя и адрес электронной почты. Поле "how will you use it" необязательно.
3. Скопируйте 40-символьный ключ.
4. Запустите **Add or change keys** и вставьте его как ключ для США.

Условия вкратце:

- Со своим ключом govinfo допускает до 36,000 запросов в час.
- Мы не нашли условий использования, относящихся именно к API (api.data.gov/terms/ не
  существует). Не проверено. См. [правила govinfo](https://www.govinfo.gov/about/policies) и
  [политику конфиденциальности data.gov](https://data.gov/privacy-policy/).
- Никому не передавайте ключ.

## Где хранятся ключи

- **Установщик или вручную:** открытым текстом в файле MCP-конфигурации каждого приложения, в
  блоке `env` записи `fontes`. Любой, кто может читать ваши пользовательские файлы, может
  прочитать ключи.
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
- **Расширение Claude Desktop (.mcpb):** Claude хранит эти поля в своих настройках и защищает
  их защищённым хранилищем вашей системы (Keychain на Mac, Credential Manager в Windows).

Перед каждым изменением установщик сохраняет рядом копию файла конфигурации
(`<file>.fontes-backup-<time>`). Копии, сделанные после добавления ключей, тоже содержат ключи.
Удалите старые копии, которые вам не нужны.

## Изменение или удаление ключа

- Запустите **Add or change keys**. Вставьте новый ключ, чтобы заменить старый, или введите `-`,
  чтобы удалить его.
- Или отредактируйте блок `env` вручную и перезапустите приложение.
- Удаление Fontes удаляет всю его запись вместе с ключами. Резервные копии при этом не
  удаляются.
- Если ключ утёк, замените его и у источника: на PISTE создайте новые учётные данные для своего
  приложения; для api.data.gov зарегистрируйте новый ключ.

## Сообщения, которые вы можете увидеть

| Сообщение | Значение |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Нет ключа для Франции. Добавьте его. |
| `Inactive: needs a free PISTE account. ...` (в `list_jurisdictions`) | То же самое. |
| `PISTE refused the client credentials ...` | ID или secret неверны или больше не действительны. Снова скопируйте оба со вкладки Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Ваше приложение не подписано на этот API, или вы не приняли его условия. См. шаги 2 и 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Нет ключа для США. Поиск работает для нескольких вызовов в день. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Демонстрационный ключ исчерпан. Добавьте собственный ключ. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Ключ неверен или ещё не подтверждён по электронной почте. |

Пустое значение считается отсутствием ключа.

## Разрешения (WLM_PERMITTED)

Это не API-ключ, и установщик его не задаёт. **Задавайте его, только если это разрешение есть
лично у вас.**

Некоторые источники по умолчанию выключены, потому что их условия или robots.txt запрещают
автоматизированное использование без разрешения. Если у вас есть разрешение издателя, включите
источник, добавив его код в `WLM_PERMITTED` через запятую в блоке `env`:
`"WLM_PERMITTED": "in,de"`.

| Код | Источник |
|---|---|
| `az` | Азербайджан: e-qanun.az (Министерство юстиции) |
| `bh` | Бахрейн: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Колумбия: Función Pública, Gestor Normativo (консолидированное законодательство) |
| `de` | Германия: NeuRIS (федеральный портал правовой информации, пробный сервис) |
| `difc` | Суды Дубайского международного финансового центра (difccourts.ae) |
| `gr` | Греция: Национальная типография, поиск по Правительственному вестнику (search.et.gr) |
| `in` | Индия: India Code (indiacode.gov.in) |
| `mu` | Маврикий: Верховный суд (supremecourt.govmu.org) |
| `sg` | Сингапур: судебные решения (elitigation.sg) |

Без разрешения Fontes сообщает: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
