> នេះគឺជាការបកប្រែដោយមានជំនួយពីម៉ាស៊ីន។ កំណែភាសាអង់គ្លេសគឺជាកំណែដែលមានអានុភាព។

# កូនសោ API

ប្រភពស្ទើរតែទាំងអស់នៅក្នុង Fontes ដំណើរការដោយគ្មានកូនសោ។ ប្រភពពីរត្រូវការកូនសោឥតគិតថ្លៃ៖

| កូនសោ | បើកឱ្យប្រើ | បើគ្មានវា |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | ប្រទេសបារាំង៖ Judilibre (សេចក្ដីសម្រេចរបស់តុលាការ) និង Légifrance (លិខិតបទដ្ឋានគតិយុត្ត) | ប្រទេសបារាំងត្រូវបានបិទ។ `list_jurisdictions` បង្ហាញវាថាអសកម្ម។ |
| `WLM_US_GOVINFO_KEY` | សហរដ្ឋអាមេរិក៖ ការស្វែងរក govinfo (មតិរបស់តុលាការសហព័ន្ធ, Statutes at Large, public laws) | Fontes ប្រើ `DEMO_KEY` ដែលប្រើរួមគ្នា៖ ប្រហែល 10 ការស្វែងរកក្នុងមួយថ្ងៃ ក្នុងមួយអាសយដ្ឋាន IP។ ការបើកសេចក្ដីសម្រេចដែលស្គាល់រួច និង US Code មិនត្រូវការកូនសោទេ។ |

កូនសោគឺជាជម្រើស។ អ្នកអាចបន្ថែមវានៅពេលក្រោយ។

## ការបន្ថែមកូនសោ

**ជាមួយកម្មវិធីដំឡើង។** នៅពេល Fontes ត្រូវបានរៀបចំរួច កម្មវិធីដំឡើងស្នើឱ្យបន្ថែមកូនសោ។ នៅលើ Mac សូមចុច
**បន្ថែមកូនសោ** ឬ **រួចរាល់** ដើម្បីរំលង; នៅលើ Windows សូមឆ្លើយសំណួរ (ចុច Enter ដើម្បីរំលង)។
ដើម្បីបន្ថែម ឬផ្លាស់ប្ដូរកូនសោនៅពេលក្រោយ សូមដំណើរការ **Add or change keys**៖

- Mac៖ បើកកម្មវិធី Fontes Installer ម្ដងទៀត ហើយជ្រើសរើស **បន្ថែម ឬប្ដូរកូនសោ**។
- Windows៖ បើក Start menu បន្ទាប់មក **Fontes** → **បន្ថែម ឬប្ដូរកូនសោ**។

អ្វីដែលអ្នកវាយត្រូវបានលាក់។ សម្រាប់កូនសោនីមួយៗ៖ បិទភ្ជាប់វា ចុច Enter ដើម្បីរក្សាអ្វីដែលមានស្រាប់ ឬវាយ `-` ដើម្បី
លុបវា។ កូនសោត្រូវបានបញ្ចូលទៅក្នុងកម្មវិធីនីមួយៗដែលមាន Fontes រួចហើយ។

**ជាមួយផ្នែកបន្ថែម Claude Desktop (.mcpb)។** បើក Claude > Settings > Extensions > Fontes ហើយ
បំពេញវាល។ វាលទាំងអស់គឺជាជម្រើស។

**ដោយដៃ។** បន្ថែមអថេរទៅក្នុងប្លុក `env` នៃធាតុ `fontes` នៅក្នុងការកំណត់រចនាសម្ព័ន្ធ MCP នៃកម្មវិធីរបស់អ្នក៖

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

ចាប់ផ្ដើមកម្មវិធីឡើងវិញ បន្ទាប់ពីការផ្លាស់ប្ដូរណាមួយ។

## ប្រទេសបារាំង៖ PISTE (ឥតគិតថ្លៃ)

1. បង្កើតគណនីមួយនៅ [piste.gouv.fr](https://piste.gouv.fr)។ នេះមានន័យថាទទួលយកលក្ខខណ្ឌរបស់ PISTE (CGU)។
2. ចូលទៅកាន់ API > **Consentement CGU API**។ ទទួលយកលក្ខខណ្ឌសម្រាប់ **JUDILIBRE** និង **Légifrance** (production)។
3. បង្កើត **កម្មវិធី production** មួយ។ `APP_SANDBOX` ដែលត្រូវបានបង្កើតសម្រាប់អ្នក មិនអាចចូលប្រើ production បានទេ។
   នៅក្រោម "Modifier l'application" សូមធីក **JUDILIBRE (production)** និង **Légifrance (production)** បន្ទាប់មកអនុវត្ត។
4. បើកផ្ទាំង **Authentification** របស់កម្មវិធី។ ចម្លង `client_id` និង `client_secret`។
5. ដំណើរការ **Add or change keys** ហើយបិទភ្ជាប់ពួកវា។

លក្ខខណ្ឌ ជាសង្ខេប៖

- ទិន្នន័យ៖ Licence Ouverte / Etalab 2.0។ ការប្រើឡើងវិញ រួមទាំងការប្រើឡើងវិញសម្រាប់ពាណិជ្ជកម្ម ត្រូវបានអនុញ្ញាត ដោយមានការបញ្ជាក់ប្រភព។
- កុំបោះពុម្ពផ្សាយ ឬចែករំលែកព័ត៌មានសម្គាល់ខ្លួនរបស់អ្នក។ ប្រាប់ PISTE ប្រសិនបើវាលេចធ្លាយ។
- API របស់ Légifrance គឺជាសេវាកម្មបេតា។ វាអាចត្រូវបានផ្អាក ហើយវាមានកូតា (ក្នុងមួយវិនាទី នាទី និងថ្ងៃ)។
- អត្ថបទ Légifrance មិនមែនជាកំណែត្រឹមត្រូវដើមទេ។ មានតែ PDF របស់ Journal officiel ដែលបានចុះហត្ថលេខាប៉ុណ្ណោះដែលជាកំណែត្រឹមត្រូវដើម។
- Judilibre៖ កុំប្រើឈ្មោះរបស់ចៅក្រម ឬក្រឡាបញ្ជី ដើម្បីវាយតម្លៃ ប្រៀបធៀប ឬទស្សន៍ទាយការងាររបស់ពួកគេ
  (Code de l'organisation judiciaire មាត្រា L111-13; ជាបទល្មើសព្រហ្មទណ្ឌ)។
- Judilibre៖ អនុវត្តតាម GDPR។ កុំព្យាយាមកំណត់អត្តសញ្ញាណភាគីឡើងវិញ។

កូតារបស់អ្នកមាននៅលើ PISTE ក្រោម API Sélectionnées > Actions > Consulter les quotas។

## សហរដ្ឋអាមេរិក៖ api.data.gov (ឥតគិតថ្លៃ)

1. ចូលទៅកាន់ [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (កូនសោត្រូវបានបង្ហាញនៅលើអេក្រង់)
   ឬ [api.data.gov/signup](https://api.data.gov/signup/) (កូនសោត្រូវបានផ្ញើទៅអ្នកតាមអ៊ីមែល)។
2. បញ្ចូលឈ្មោះ និងអ៊ីមែលរបស់អ្នក។ វាល "how will you use it" គឺជាជម្រើស។
3. ចម្លងកូនសោដែលមាន 40 តួអក្សរ។
4. ដំណើរការ **Add or change keys** ហើយបិទភ្ជាប់វាជាកូនសោសហរដ្ឋអាមេរិក។

លក្ខខណ្ឌ ជាសង្ខេប៖

- ជាមួយកូនសោផ្ទាល់ខ្លួនរបស់អ្នក govinfo អនុញ្ញាតរហូតដល់ 36,000 សំណើក្នុងមួយម៉ោង។
- យើងមិនបានរកឃើញលក្ខខណ្ឌសេវាកម្មជាក់លាក់សម្រាប់ API ទេ (api.data.gov/terms/ មិនមាន)។ មិនទាន់បានផ្ទៀងផ្ទាត់។
  សូមមើល [គោលការណ៍របស់ govinfo](https://www.govinfo.gov/about/policies) និង
  [គោលការណ៍ឯកជនភាពរបស់ data.gov](https://data.gov/privacy-policy/)។
- រក្សាកូនសោសម្រាប់តែខ្លួនអ្នក។

## កន្លែងដែលកូនសោត្រូវបានរក្សាទុក

- **កម្មវិធីដំឡើង ឬដោយដៃ៖** ជាអត្ថបទធម្មតានៅក្នុងឯកសារកំណត់រចនាសម្ព័ន្ធ MCP នៃកម្មវិធីនីមួយៗ នៅក្នុងប្លុក `env` នៃ
  ធាតុ `fontes`។ អ្នកណាដែលអាចអានឯកសារអ្នកប្រើប្រាស់របស់អ្នកបាន អាចអានកូនសោបាន។
  - Claude Desktop៖ `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code៖ `~/.claude.json`
  - Codex៖ `~/.codex/config.toml`
  - Cursor៖ `~/.cursor/mcp.json`
  - VS Code (Copilot)៖ `~/.copilot/mcp-config.json`
  - Windsurf៖ `~/.config/devin/mcp_config.json` ឬ `~/.codeium/windsurf/mcp_config.json`
    (Windows៖ `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI៖ `~/.gemini/settings.json`
  - Zed៖ `~/.config/zed/settings.json` (Windows៖ `%APPDATA%\Zed\settings.json`)
  - LM Studio៖ `~/.lmstudio/mcp.json`
  - Cline៖ `~/.cline/data/settings/cline_mcp_settings.json`
- **ផ្នែកបន្ថែម Claude Desktop (.mcpb)៖** Claude រក្សាទុកវាលទាំងនេះនៅក្នុងការកំណត់របស់វា ហើយការពារពួកវា
  ដោយកន្លែងផ្ទុកសុវត្ថិភាពនៃប្រព័ន្ធរបស់អ្នក (Keychain នៅលើ Mac, Credential Manager នៅលើ Windows)។

មុនការផ្លាស់ប្ដូរនីមួយៗ កម្មវិធីដំឡើងរក្សាទុកច្បាប់ចម្លងនៃឯកសារកំណត់រចនាសម្ព័ន្ធនៅក្បែរវា
(`<file>.fontes-backup-<time>`)។ ច្បាប់ចម្លងដែលបានបង្កើតបន្ទាប់ពីអ្នកបានបន្ថែមកូនសោ ក៏មានកូនសោដែរ។ សូមលុបច្បាប់ចម្លង
ចាស់ៗដែលអ្នកមិនត្រូវការ។

## ការផ្លាស់ប្ដូរ ឬការលុបកូនសោ

- ដំណើរការ **Add or change keys**។ បិទភ្ជាប់កូនសោថ្មីដើម្បីជំនួសវា ឬវាយ `-` ដើម្បីលុបវា។
- ឬកែប្លុក `env` ដោយដៃ ហើយចាប់ផ្ដើមកម្មវិធីឡើងវិញ។
- ការលុបការដំឡើង Fontes លុបធាតុទាំងមូលរបស់វា រួមទាំងកូនសោ។ វាមិនលុបច្បាប់ចម្លងបម្រុងទុកទេ។
- ប្រសិនបើកូនសោមួយបានលេចធ្លាយ សូមជំនួសវានៅប្រភពផងដែរ៖ នៅលើ PISTE បង្កើតព័ត៌មានសម្គាល់ខ្លួនថ្មីសម្រាប់កម្មវិធីរបស់អ្នក;
  សម្រាប់ api.data.gov ចុះឈ្មោះយកកូនសោថ្មីមួយ។

## សារដែលអ្នកអាចនឹងឃើញ

| សារ | អត្ថន័យ |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | គ្មានកូនសោសម្រាប់ប្រទេសបារាំង។ សូមបន្ថែមមួយ។ |
| `Inactive: needs a free PISTE account. ...` (នៅក្នុង `list_jurisdictions`) | ដូចគ្នា។ |
| `PISTE refused the client credentials ...` | ID ឬ secret ខុស ឬលែងមានសុពលភាព។ ចម្លងទាំងពីរម្ដងទៀតពីផ្ទាំង Authentification។ |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | កម្មវិធីរបស់អ្នកមិនបានជាវ API នោះ ឬអ្នកមិនទាន់បានទទួលយកលក្ខខណ្ឌរបស់វា។ សូមមើលជំហានទី 2 និងទី 3។ |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | គ្មានកូនសោសម្រាប់សហរដ្ឋអាមេរិក។ ការស្វែងរកដំណើរការបានពីរបីដងក្នុងមួយថ្ងៃ។ |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | កូនសោសាកល្បងត្រូវបានប្រើអស់។ សូមបន្ថែមកូនសោផ្ទាល់ខ្លួនរបស់អ្នក។ |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | កូនសោខុស ឬមិនទាន់ត្រូវបានបញ្ជាក់ពីអ៊ីមែល។ |

តម្លៃទទេត្រូវបានរាប់ថាគ្មានកូនសោ។

## ការអនុញ្ញាត (WLM_PERMITTED)

នេះមិនមែនជាកូនសោ API ទេ ហើយកម្មវិធីដំឡើងមិនកំណត់វាទេ។ **កំណត់វាលុះត្រាតែអ្នកផ្ទាល់មាន
ការអនុញ្ញាតនោះ។**

ប្រភពមួយចំនួនត្រូវបានបិទតាមលំនាំដើម ដោយសារលក្ខខណ្ឌ ឬ robots.txt របស់ពួកវាហាមឃាត់ការប្រើប្រាស់ស្វ័យប្រវត្តិដោយគ្មាន
ការអនុញ្ញាត។ ប្រសិនបើអ្នកមានការអនុញ្ញាតពីអ្នកបោះពុម្ពផ្សាយ សូមបើកប្រភពមួយ ដោយបន្ថែមកូដរបស់វាទៅក្នុង
`WLM_PERMITTED` ដោយបំបែកដោយសញ្ញាក្បៀស នៅក្នុងប្លុក `env`៖ `"WLM_PERMITTED": "in,de"`។

| កូដ | ប្រភព |
|---|---|
| `az` | អាស៊ែបៃហ្សង់៖ e-qanun.az (ក្រសួងយុត្តិធម៌) |
| `bh` | បារ៉ែន៖ Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | កូឡុំប៊ី៖ Función Pública, Gestor Normativo (លិខិតបទដ្ឋានគតិយុត្តបង្រួបបង្រួម) |
| `de` | អាល្លឺម៉ង់៖ NeuRIS (វិបផតថលព័ត៌មានច្បាប់សហព័ន្ធ សេវាកម្មសាកល្បង) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | ក្រិក៖ National Printing Office ការស្វែងរក Government Gazette (search.et.gr) |
| `in` | ឥណ្ឌា៖ India Code (indiacode.gov.in) |
| `mu` | ម៉ូរីស៖ Supreme Court (supremecourt.govmu.org) |
| `sg` | សិង្ហបុរី៖ សាលក្រមរបស់តុលាការ (elitigation.sg) |

បើគ្មានការអនុញ្ញាត Fontes និយាយថា៖ `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
