> Бул машинанын жардамы менен жасалган котормо. Негизги нуска — англисче нуска.

# API ачкычтары

Fontes'теги булактардын дээрлик баары ачкычсыз иштейт. Экөөнө акысыз ачкыч керек:

| Ачкыч | Эмнени ачат | Ачкычсыз |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Франция: Judilibre (сот чечимдери) жана Légifrance (мыйзамдар) | Франция өчүк. `list_jurisdictions` аны активдүү эмес деп көрсөтөт. |
| `WLM_US_GOVINFO_KEY` | Америка Кошмо Штаттары: govinfo издөөсү (федералдык соттордун чечимдери, Statutes at Large, public laws) | Fontes жалпы `DEMO_KEY` колдонот: бир IP дарек үчүн күнүнө болжол менен 10 издөө. Белгилүү чечимди ачууга жана US Code үчүн ачкыч керек эмес. |

Ачкычтар милдеттүү эмес. Аларды кийин кошо аласыз.

## Ачкыч кошуу

**Орнотуучу аркылуу.** Орнотуу учурунда орнотуучу ачкычтарды кошкуңуз келеби деп сурайт.
Өткөрүп жиберүү үчүн **Азыр эмес** тандаңыз (же Enter басыңыз). Ачкычтарды кийин кошуу же
өзгөртүү үчүн **Add or change keys** иштетиңиз:

- Mac: Fontes Installer тиркемесин кайра ачып, **Ачкычтарды кошуу же өзгөртүү** тандаңыз же
  орнотуучу папкасындагы `Add or change keys.command` файлын эки жолу басыңыз.
- Windows: орнотуучу папкасындагы `Add or change keys.cmd` файлын эки жолу басыңыз. Windows
  орнотуу программасы чыккандан кийин, ал аны Start menu > Fontes ичине да коёт.

Терилген текст көрүнбөйт. Ар бир ачкыч үчүн: аны чаптаңыз, бар нерсени сактоо үчүн Enter
басыңыз же аны алып салуу үчүн `-` териңиз. Ачкычтар Fontes мурунтан эле бар болгон ар бир
тиркемеге кошулат.

**Claude Desktop кеңейтүүсү (.mcpb) аркылуу.** Claude > Settings > Extensions > Fontes ачып,
талааларды толтуруңуз. Алардын баары милдеттүү эмес.

**Кол менен.** Өзгөрмөлөрдү тиркемеңиздин MCP конфигурациясындагы `fontes` жазуусунун `env`
блогуна кошуңуз:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Ар кандай өзгөртүүдөн кийин тиркемени кайра иштетиңиз.

## Франция: PISTE (акысыз)

1. [piste.gouv.fr](https://piste.gouv.fr) сайтында аккаунт түзүңүз. Бул PISTE шарттарын (CGU)
   кабыл алууну билдирет.
2. API > **Consentement CGU API** бөлүмүнө өтүңүз. **JUDILIBRE** жана **Légifrance**
   (production) шарттарын кабыл алыңыз.
3. **Production application** түзүңүз. Сиз үчүн түзүлгөн `APP_SANDBOX` production'го кире
   албайт. “Modifier l'application” астында **JUDILIBRE (production)** жана **Légifrance
   (production)** белгилеп, андан кийин колдонуңуз.
4. Тиркеменин **Authentification** өтмөгүн ачыңыз. `client_id` жана `client_secret` көчүрүңүз.
5. **Add or change keys** иштетип, аларды чаптаңыз.

Шарттар, кыскача:

- Маалыматтар: Licence Ouverte / Etalab 2.0. Кайра колдонууга, анын ичинде коммерциялык кайра
  колдонууга, авторлукту көрсөтүү шарты менен уруксат берилет.
- Эсептик маалыматтарыңызды жарыялабаңыз жана башкалар менен бөлүшпөңүз. Эгер алар сыртка
  чыгып кетсе, PISTE'ге кабарлаңыз.
- Légifrance API — бета кызмат. Ал токтотулушу мүмкүн жана анын квоталары бар (секунд, мүнөт
  жана күн боюнча).
- Légifrance тексттери аныктыгы ырасталган версия эмес. Кол коюлган Journal officiel PDF гана
  аныктыгы ырасталган.
- Judilibre: судьялардын же сот катчыларынын аттарын алардын ишин баалоо, салыштыруу же
  болжолдоо үчүн колдонбоңуз (Code de l'organisation judiciaire, L111-13-берене; кылмыш).
- Judilibre: GDPR'ди сактаңыз. Тараптарды кайра аныктоого аракет кылбаңыз.

Квоталарыңыз PISTE'де API Sélectionnées > Actions > Consulter les quotas астында.

## Америка Кошмо Штаттары: api.data.gov (акысыз)

1. [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (ачкыч экранда көрсөтүлөт)
   же [api.data.gov/signup](https://api.data.gov/signup/) (ачкыч электрондук почтаңызга
   жөнөтүлөт) дарегине өтүңүз.
2. Атыңызды жана электрондук почтаңызды киргизиңиз. “How will you use it” талаасы милдеттүү
   эмес.
3. 40 белгиден турган ачкычты көчүрүңүз.
4. **Add or change keys** иштетип, аны АКШ ачкычы катары чаптаңыз.

Шарттар, кыскача:

- Өз ачкычыңыз менен govinfo саатына 36 000 сурамга чейин уруксат берет.
- Биз API'ге тиешелүү колдонуу шарттарын тапкан жокпуз (api.data.gov/terms/ жок). Текшерилген
  эмес. Караңыз: [govinfo саясаттары](https://www.govinfo.gov/about/policies) жана
  [data.gov купуялуулук саясаты](https://data.gov/privacy-policy/).
- Ачкычты өзүңүздө сактаңыз.

## Ачкычтар кайда сакталат

- **Орнотуучу аркылуу же кол менен:** ар бир тиркеменин MCP конфигурация файлында, `fontes`
  жазуусунун `env` блогунда жөнөкөй текст катары. Колдонуучу файлдарыңызды окуй алган ар
  ким ачкычтарды окуй алат.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` же `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Claude Desktop кеңейтүүсү (.mcpb):** Claude бул талааларды өз жөндөөлөрүндө сактайт жана
  аларды тутумуңуздун коопсуз сактагычы (Mac'те Keychain, Windows'то Credential Manager)
  менен коргойт.

Ар бир өзгөртүүдөн мурун орнотуучу конфигурация файлынын көчүрмөсүн анын жанына сактайт
(`<file>.fontes-backup-<time>`). Ачкычтарды кошкондон кийин жасалган көчүрмөлөрдө ачкычтар да
болот. Керек эмес эски көчүрмөлөрдү өчүрүңүз.

## Ачкычты өзгөртүү же алып салуу

- **Add or change keys** иштетиңиз. Алмаштыруу үчүн жаңы ачкычты чаптаңыз же аны алып салуу
  үчүн `-` териңиз.
- Же `env` блогун кол менен түзөтүп, тиркемени кайра иштетиңиз.
- Fontes'ти өчүрүү анын бүт жазуусун, ачкычтары менен кошо, алып салат. Ал камдык
  көчүрмөлөрдү өчүрбөйт.
- Эгер ачкыч сыртка чыгып кетсе, аны булакта да алмаштырыңыз: PISTE'де тиркемеңиз үчүн жаңы
  эсептик маалыматтарды түзүңүз; api.data.gov үчүн жаңы ачкычка катталыңыз.

## Сиз көрүшүңүз мүмкүн болгон билдирүүлөр

| Билдирүү | Мааниси |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Франция ачкычы жок. Аны кошуңуз. |
| `Inactive: needs a free PISTE account. ...` (`list_jurisdictions` ичинде) | Ошол эле. |
| `PISTE refused the client credentials ...` | ID же secret туура эмес же мындан ары жарактуу эмес. Экөөнү тең Authentification өтмөгүнөн кайра көчүрүңүз. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Тиркемеңиз ошол API'ге жазылган эмес же сиз анын шарттарын кабыл алган жоксуз. 2- жана 3-кадамдарды караңыз. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | АКШ ачкычы жок. Издөө күнүнө бир нече чакыруу үчүн иштейт. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Демо ачкычтын чеги бүттү. Өз ачкычыңызды кошуңуз. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Ачкыч туура эмес же электрондук каттан азырынча ырасталган эмес. |

Бош маани ачкыч жок деп эсептелет.

## Уруксаттар (WLM_PERMITTED)

Бул API ачкычы эмес жана орнотуучу аны койбойт. **Аны ошол уруксат өзүңүздө болгондо гана
коюңуз.**

Айрым булактар демейки боюнча өчүк, анткени алардын шарттары же robots.txt файлы уруксатсыз
автоматтык колдонууга тыюу салат. Эгер жарыялоочудан уруксатыңыз болсо, булактын кодун `env`
блогундагы `WLM_PERMITTED` ичине үтүр менен бөлүп кошуп, аны күйгүзүңүз:
`"WLM_PERMITTED": "in,de"`.

| Код | Булак |
|---|---|
| `az` | Азербайжан: e-qanun.az (Юстиция министрлиги) |
| `bh` | Бахрейн: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Колумбия: Función Pública, Gestor Normativo (бардык өзгөртүүлөр киргизилген мыйзамдар) |
| `de` | Германия: NeuRIS (федералдык укуктук маалымат порталы, сыноо кызматы) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Греция: Улуттук басмакана, Өкмөттүк бюллетень боюнча издөө (search.et.gr) |
| `in` | Индия: India Code (indiacode.gov.in) |
| `mu` | Маврикий: Жогорку сот (supremecourt.govmu.org) |
| `sg` | Сингапур: сот чечимдери (elitigation.sg) |

Уруксатсыз Fontes мындай дейт: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
