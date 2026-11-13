> Սա մեքենայի օգնությամբ կատարված թարգմանություն է։ Վավերական է անգլերեն տարբերակը։

# API բանալիներ

Fontes-ի գրեթե յուրաքանչյուր աղբյուր աշխատում է առանց բանալու։ Երկուսին անհրաժեշտ է անվճար
բանալի՝

| Բանալի | Ինչ է բացում | Առանց դրա |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Ֆրանսիա՝ Judilibre (դատական ակտեր) և Légifrance (օրենսդրություն) | Ֆրանսիան անջատված է։ `list_jurisdictions`-ը այն ցույց է տալիս որպես ոչ ակտիվ։ |
| `WLM_US_GOVINFO_KEY` | Միացյալ Նահանգներ՝ govinfo որոնում (դաշնային դատարանների որոշումներ, Statutes at Large, public laws) | Fontes-ն օգտագործում է ընդհանուր `DEMO_KEY`-ը՝ IP հասցեից օրական մոտ 10 որոնում։ Հայտնի որոշում բացելու և US Code-ի համար բանալի պետք չէ։ |

Բանալիներն ընտրովի են։ Կարող եք դրանք ավելացնել ավելի ուշ։

## Բանալու ավելացում

**Տեղադրիչով։** Տեղադրման ընթացքում տեղադրիչը հարցնում է՝ արդյոք ցանկանում եք ավելացնել
բանալիներ։ Բաց թողնելու համար ընտրեք **Ոչ հիմա** (կամ սեղմեք Enter)։ Բանալիներն ավելի ուշ
ավելացնելու կամ փոխելու համար գործարկեք **Add or change keys**՝

- Mac. նորից բացեք Fontes Installer հավելվածը և ընտրեք **Ավելացնել կամ փոխել բանալիները**, կամ
  տեղադրիչի թղթապանակում կրկնակի սեղմեք `Add or change keys.command`-ի վրա։
- Windows. տեղադրիչի թղթապանակում կրկնակի սեղմեք `Add or change keys.cmd`-ի վրա։ Windows-ի
  տեղադրման ծրագիրը, երբ հասանելի լինի, այն կտեղադրի նաև Start մենյու > Fontes-ում։

Մուտքագրվածը թաքցված է։ Յուրաքանչյուր բանալու համար՝ տեղադրեք այն, սեղմեք Enter՝ եղածը պահելու
համար, կամ մուտքագրեք `-`՝ այն հեռացնելու համար։ Բանալիները գրանցվում են յուրաքանչյուր
հավելվածում, որն արդեն ունի Fontes։

**Claude Desktop ընդլայնմամբ (.mcpb)։** Բացեք Claude > Settings > Extensions > Fontes և լրացրեք
դաշտերը։ Դրանք բոլորն ընտրովի են։

**Ձեռքով։** Ավելացրեք փոփոխականները ձեր հավելվածի MCP կարգավորման `fontes` գրառման `env`
բլոկին՝

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Ցանկացած փոփոխությունից հետո վերագործարկեք հավելվածը։

## Ֆրանսիա՝ PISTE (անվճար)

1. Ստեղծեք հաշիվ [piste.gouv.fr](https://piste.gouv.fr)-ում։ Դա նշանակում է ընդունել PISTE-ի պայմանները (CGU)։
2. Անցեք API > **Consentement CGU API**։ Ընդունեք **JUDILIBRE**-ի և **Légifrance**-ի (production) պայմանները։
3. Ստեղծեք **արտադրական հավելված** (production application)։ Ձեզ համար ստեղծված `APP_SANDBOX`-ը
   չի կարող մուտք գործել արտադրական միջավայր։ «Modifier l'application» բաժնում նշեք
   **JUDILIBRE (production)** և **Légifrance (production)**, ապա կիրառեք։
4. Բացեք հավելվածի **Authentification** ներդիրը։ Պատճենեք `client_id`-ը և `client_secret`-ը։
5. Գործարկեք **Add or change keys** և տեղադրեք դրանք։

Պայմանները՝ համառոտ՝

- Տվյալներ՝ Licence Ouverte / Etalab 2.0։ Վերօգտագործումը, ներառյալ առևտրային, թույլատրված է՝ աղբյուրի նշումով։
- Մի՛ հրապարակեք և մի՛ փոխանցեք ձեր մուտքի տվյալները։ Եթե դրանք արտահոսեն, տեղեկացրեք PISTE-ին։
- Légifrance API-ն բետա ծառայություն է։ Այն կարող է կասեցվել և ունի քվոտաներ (վայրկյանում, րոպեում և օրում)։
- Légifrance-ի տեքստերը վավերական տարբերակը չեն։ Վավերական է միայն ստորագրված Journal officiel PDF-ը։
- Judilibre. մի՛ օգտագործեք դատավորների կամ դատարանի աշխատակազմի անունները նրանց աշխատանքը
  գնահատելու, համեմատելու կամ կանխատեսելու համար (Code de l'organisation judiciaire, հոդված
  L111-13. քրեական հանցագործություն)։
- Judilibre. պահպանեք GDPR-ը։ Մի՛ փորձեք վերանույնականացնել կողմերին։

Ձեր քվոտաները PISTE-ում են՝ API Sélectionnées > Actions > Consulter les quotas բաժնում։

## Միացյալ Նահանգներ՝ api.data.gov (անվճար)

1. Անցեք [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (բանալին ցուցադրվում է
   էկրանին) կամ [api.data.gov/signup](https://api.data.gov/signup/) (բանալին ուղարկվում է ձեզ
   էլ. փոստով)։
2. Մուտքագրեք ձեր անունը և էլ. փոստը։ «how will you use it» դաշտն ընտրովի է։
3. Պատճենեք 40 նիշանոց բանալին։
4. Գործարկեք **Add or change keys** և տեղադրեք այն որպես ԱՄՆ-ի բանալի։

Պայմանները՝ համառոտ՝

- Սեփական բանալիով govinfo-ն թույլ է տալիս ժամում մինչև 36 000 հարցում։
- API-ին հատուկ օգտագործման պայմաններ չենք գտել (api.data.gov/terms/ գոյություն չունի)։
  Չստուգված։ Տե՛ս [govinfo-ի քաղաքականությունները](https://www.govinfo.gov/about/policies) և
  [data.gov-ի գաղտնիության քաղաքականությունը](https://data.gov/privacy-policy/)։
- Բանալին պահեք ձեզ մոտ։

## Որտեղ են պահվում բանալիները

- **Տեղադրիչով կամ ձեռքով.** որպես պարզ տեքստ յուրաքանչյուր հավելվածի MCP կարգավորման ֆայլում՝
  `fontes` գրառման `env` բլոկում։ Յուրաքանչյուր ոք, ով կարող է կարդալ ձեր օգտատիրոջ ֆայլերը,
  կարող է կարդալ նաև բանալիները։
  - Claude Desktop՝ `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code՝ `~/.claude.json`
  - Codex՝ `~/.codex/config.toml`
  - Cursor՝ `~/.cursor/mcp.json`
  - VS Code (Copilot)՝ `~/.copilot/mcp-config.json`
  - Windsurf՝ `~/.config/devin/mcp_config.json` կամ `~/.codeium/windsurf/mcp_config.json`
    (Windows՝ `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI՝ `~/.gemini/settings.json`
  - Zed՝ `~/.config/zed/settings.json` (Windows՝ `%APPDATA%\Zed\settings.json`)
  - LM Studio՝ `~/.lmstudio/mcp.json`
  - Cline՝ `~/.cline/data/settings/cline_mcp_settings.json`
- **Claude Desktop ընդլայնում (.mcpb).** Claude-ը պահում է այս դաշտերն իր կարգավորումներում և
  պաշտպանում դրանք ձեր համակարգի անվտանգ պահոցով (Keychain՝ Mac-ում, Credential Manager՝
  Windows-ում)։

Յուրաքանչյուր փոփոխությունից առաջ տեղադրիչը կարգավորման ֆայլի պատճենը պահպանում է դրա կողքին
(`<file>.fontes-backup-<time>`)։ Բանալիներ ավելացնելուց հետո ստեղծված պատճենները նույնպես
պարունակում են բանալիները։ Ջնջեք այն հին պատճենները, որոնք ձեզ պետք չեն։

## Բանալու փոփոխում կամ հեռացում

- Գործարկեք **Add or change keys**։ Տեղադրեք նոր բանալի՝ այն փոխարինելու համար, կամ մուտքագրեք `-`՝ այն հեռացնելու համար։
- Կամ խմբագրեք `env` բլոկը ձեռքով և վերագործարկեք հավելվածը։
- Fontes-ի ապատեղադրումը հեռացնում է դրա ամբողջ գրառումը՝ ներառյալ բանալիները։ Այն չի ջնջում պահուստային պատճենները։
- Եթե բանալին արտահոսել է, փոխարինեք այն նաև աղբյուրում. PISTE-ում ստեղծեք նոր մուտքի տվյալներ
  ձեր հավելվածի համար, api.data.gov-ի համար գրանցվեք նոր բանալու համար։

## Հաղորդագրություններ, որոնք կարող եք տեսնել

| Հաղորդագրություն | Նշանակություն |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Ֆրանսիայի բանալի չկա։ Ավելացրեք այն։ |
| `Inactive: needs a free PISTE account. ...` (`list_jurisdictions`-ում) | Նույնը։ |
| `PISTE refused the client credentials ...` | ID-ն կամ secret-ը սխալ է կամ այլևս վավեր չէ։ Կրկին պատճենեք երկուսն էլ Authentification ներդիրից։ |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Ձեր հավելվածը բաժանորդագրված չէ այդ API-ին, կամ դուք չեք ընդունել դրա պայմանները։ Տե՛ս 2-րդ և 3-րդ քայլերը։ |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | ԱՄՆ-ի բանալի չկա։ Որոնումն աշխատում է օրական մի քանի կանչի համար։ |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Ցուցադրական բանալին սպառված է։ Ավելացրեք ձեր սեփական բանալին։ |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Բանալին սխալ է կամ դեռ հաստատված չէ էլ. նամակից։ |

Դատարկ արժեքը հավասարազոր է բանալու բացակայությանը։

## Թույլտվություններ (WLM_PERMITTED)

Սա API բանալի չէ, և տեղադրիչն այն չի սահմանում։ **Սահմանեք այն միայն այն դեպքում, եթե դուք
ինքներդ ունեք այդ թույլտվությունը։**

Որոշ աղբյուրներ լռելյայն անջատված են, քանի որ դրանց պայմանները կամ robots.txt-ն արգելում են
ավտոմատացված օգտագործումն առանց թույլտվության։ Եթե ունեք հրապարակողի թույլտվությունը, միացրեք
աղբյուրը՝ դրա կոդն ավելացնելով `WLM_PERMITTED`-ին, ստորակետերով բաժանված, `env` բլոկում՝
`"WLM_PERMITTED": "in,de"`։

| Կոդ | Աղբյուր |
|---|---|
| `az` | Ադրբեջան՝ e-qanun.az (Արդարադատության նախարարություն) |
| `bh` | Բահրեյն՝ Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Կոլումբիա՝ Función Pública, Gestor Normativo (համախմբված օրենսդրություն) |
| `de` | Գերմանիա՝ NeuRIS (դաշնային իրավական տեղեկատվական պորտալ, փորձնական ծառայություն) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Հունաստան՝ Ազգային տպարան, Կառավարության տեղեկագրի որոնում (search.et.gr) |
| `in` | Հնդկաստան՝ India Code (indiacode.gov.in) |
| `mu` | Մավրիկիոս՝ Գերագույն դատարան (supremecourt.govmu.org) |
| `sg` | Սինգապուր՝ դատական վճիռներ (elitigation.sg) |

Առանց թույլտվության Fontes-ը հայտնում է՝ `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
