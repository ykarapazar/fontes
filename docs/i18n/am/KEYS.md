> ይህ በማሽን የታገዘ ትርጉም ነው። የእንግሊዝኛው ቅጂ ገዢ ነው።

# የ API ቁልፎች

በ Fontes ውስጥ ያሉ ሁሉም ምንጮች ማለት ይቻላል ያለ ቁልፍ ይሠራሉ። ሁለቱ ነፃ ቁልፍ ያስፈልጋቸዋል:

| ቁልፍ | የሚከፍተው | ያለ እሱ |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | ፈረንሳይ፦ Judilibre (የፍርድ ቤት ውሳኔዎች) እና Légifrance (ሕጎች) | ፈረንሳይ ጠፍቷል። `list_jurisdictions` እንደ ንቁ ያልሆነ (inactive) ያሳየዋል። |
| `WLM_US_GOVINFO_KEY` | አሜሪካ፦ የ govinfo ፍለጋ (የፌዴራል ፍርድ ቤት ውሳኔዎች (opinions)፣ Statutes at Large፣ public laws) | Fontes የጋራውን `DEMO_KEY` ይጠቀማል፦ በአንድ የ IP አድራሻ በቀን ወደ 10 ፍለጋዎች። የታወቀ ውሳኔን መክፈትና US Code ቁልፍ አያስፈልጋቸውም። |

ቁልፎች አማራጭ ናቸው። በኋላ ሊያክሏቸው ይችላሉ።

## ቁልፍ መጨመር

**በመጫኛው (installer)።** Fontes ከተዘጋጀ በኋላ፣ መጫኛው ቁልፎችን ለመጨመር ያቀርባል። በ Mac ላይ **ቁልፎችን አክል** ን፣
ወይም ለመዝለል **ተጠናቋል** ን ጠቅ ያድርጉ፤ በ Windows ላይ ጥያቄውን ይመልሱ (ለመዝለል Enter ን ይጫኑ)። በኋላ ቁልፎችን ለመጨመር ወይም ለመቀየር፣ **ቁልፎችን አክል ወይም ቀይር** ን ያስኪዱ:

- Mac: የ Fontes Installer መተግበሪያን እንደገና ከፍተው **ቁልፎችን አክል ወይም ቀይር** ን ይምረጡ።
- Windows: የ Start menu ን ይክፈቱ፣ ከዚያም **Fontes** → **ቁልፎችን አክል ወይም ቀይር**።

የሚተይቡት አይታይም። ለእያንዳንዱ ቁልፍ፦ ይለጥፉት፣ ያለውን ለማቆየት Enter ን ይጫኑ፣ ወይም ለማስወገድ `-` ብለው ይተይቡ። ቁልፎቹ
Fontes ቀድሞውኑ ወዳለባቸው መተግበሪያዎች ሁሉ ይገባሉ።

**በ Claude Desktop ቅጥያ (extension) (.mcpb)።** Claude > Settings > Extensions > Fontes ን ከፍተው መስኮቹን ይሙሉ።
ሁሉም አማራጭ ናቸው።

**በእጅ።** ተለዋዋጮቹን በመተግበሪያዎ የ MCP ቅንብር ውስጥ ባለው የ `fontes` ግቤት `env` ክፍል ውስጥ ያክሉ:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

ከማንኛውም ለውጥ በኋላ መተግበሪያውን እንደገና ያስጀምሩ።

## ፈረንሳይ፦ PISTE (ነፃ)

1. በ [piste.gouv.fr](https://piste.gouv.fr) ላይ መለያ (account) ይፍጠሩ። ይህ የ PISTE ውሎችን (CGU) መቀበልን ይጠይቃል።
2. ወደ API > **Consentement CGU API** ይሂዱ። ለ **JUDILIBRE** እና ለ **Légifrance** (production) ውሎቹን ይቀበሉ።
3. **production application** ይፍጠሩ። ለእርስዎ የተፈጠረው `APP_SANDBOX` production ላይ መድረስ አይችልም።
   በ "Modifier l'application" ሥር **JUDILIBRE (production)** እና **Légifrance (production)** ን ምልክት ያድርጉ፣ ከዚያም ይተግብሩ።
4. የመተግበሪያውን **Authentification** ትር ይክፈቱ። `client_id` እና `client_secret` ን ይቅዱ።
5. **ቁልፎችን አክል ወይም ቀይር** ን አስኪደው ይለጥፏቸው።

ውሎቹ፣ በአጭሩ:

- መረጃው፦ Licence Ouverte / Etalab 2.0። የንግድ ዳግም አጠቃቀምን ጨምሮ ዳግም መጠቀም ምንጩን በመጥቀስ (attribution) ይፈቀዳል።
- የመግቢያ ማስረጃዎችዎን (credentials) አያትሙ ወይም ለሌላ አያጋሩ። ከወጡ (leak ካደረጉ) ለ PISTE ያሳውቁ።
- የ Légifrance API የሙከራ (beta) አገልግሎት ነው። ሊታገድ ይችላል፣ ኮታዎችም አሉት (በሰከንድ፣ በደቂቃና በቀን)።
- የ Légifrance ጽሑፎች ትክክለኛው (authentic) ቅጂ አይደሉም። ትክክለኛው የተፈረመው የ Journal officiel PDF ብቻ ነው።
- Judilibre፦ የዳኞችን ወይም የጸሐፊዎችን (clerks) ስም ሥራቸውን ለመገምገም፣ ለማወዳደር ወይም ለመተንበይ አይጠቀሙ
  (Code de l'organisation judiciaire art. L111-13፤ የወንጀል ጥፋት ነው)።
- Judilibre፦ GDPRን ይከተሉ። ተከራካሪ ወገኖችን እንደገና ለመለየት (re-identify) አይሞክሩ።

ኮታዎችዎ በ PISTE ላይ በ API Sélectionnées > Actions > Consulter les quotas ሥር ይገኛሉ።

## አሜሪካ፦ api.data.gov (ነፃ)

1. ወደ [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (ቁልፉ በማያ ገጹ ላይ ይታያል)
   ወይም ወደ [api.data.gov/signup](https://api.data.gov/signup/) (ቁልፉ በኢሜይል ይላክልዎታል) ይሂዱ።
2. ስምዎንና ኢሜይልዎን ያስገቡ። "how will you use it" የሚለው መስክ አማራጭ ነው።
3. ባለ 40 ቁምፊ (character) ቁልፉን ይቅዱ።
4. **ቁልፎችን አክል ወይም ቀይር** ን አስኪደው እንደ የአሜሪካ ቁልፍ ይለጥፉት።

ውሎቹ፣ በአጭሩ:

- በራስዎ ቁልፍ፣ govinfo በሰዓት እስከ 36,000 ጥያቄዎች (requests) ይፈቅዳል።
- ለ API የተለየ የአገልግሎት ውል አላገኘንም (api.data.gov/terms/ የለም)። ያልተረጋገጠ።
  [የ govinfo ፖሊሲዎችን](https://www.govinfo.gov/about/policies) እና
  [የ data.gov የግላዊነት ፖሊሲን](https://data.gov/privacy-policy/) ይመልከቱ።
- ቁልፉን ለራስዎ ብቻ ያቆዩ።

## ቁልፎች የት ይቀመጣሉ

- **በመጫኛው ወይም በእጅ:** በእያንዳንዱ መተግበሪያ የ MCP ቅንብር ፋይል ውስጥ፣ በ `fontes` ግቤቱ `env` ክፍል ውስጥ፣ እንደ ተራ
  ጽሑፍ (plain text)። የተጠቃሚ ፋይሎችዎን ማንበብ የሚችል ማንኛውም ሰው ቁልፎቹን ማንበብ ይችላል።
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac)፣
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` ወይም `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **የ Claude Desktop ቅጥያ (.mcpb):** Claude እነዚህን መስኮች በቅንብሮቹ ውስጥ ያስቀምጣቸዋል፣ በስርዓትዎ ደኅንነቱ የተጠበቀ
  ማከማቻ (በ Mac ላይ Keychain፣ በ Windows ላይ Credential Manager) ይጠብቃቸዋል።

ከእያንዳንዱ ለውጥ በፊት፣ መጫኛው የቅንብር ፋይሉን ቅጂ ከጎኑ ያስቀምጣል (`<file>.fontes-backup-<time>`)። ቁልፎችን ካከሉ በኋላ
የተሠሩ ቅጂዎች ቁልፎቹንም ይይዛሉ። የማያስፈልጉዎትን የቆዩ ቅጂዎች ይሰርዙ።

## ቁልፍ መቀየር ወይም ማስወገድ

- **ቁልፎችን አክል ወይም ቀይር** ን ያስኪዱ። ለመተካት አዲስ ቁልፍ ይለጥፉ፣ ወይም ለማስወገድ `-` ብለው ይተይቡ።
- ወይም የ `env` ክፍሉን በእጅ አርትዕ አድርገው መተግበሪያውን እንደገና ያስጀምሩ።
- Fontesን ማራገፍ (uninstall) ቁልፎቹን ጨምሮ ሙሉውን ግቤቱን ያስወግዳል። የምትኬ ቅጂዎቹን አይሰርዝም።
- አንድ ቁልፍ ከወጣ (leak ካደረገ)፣ ከምንጩም ይተኩት፦ በ PISTE ላይ ለመተግበሪያዎ አዲስ የመግቢያ ማስረጃዎችን ይፍጠሩ፤ ለ
  api.data.gov አዲስ ቁልፍ ለማግኘት ይመዝገቡ።

## ሊያዩዋቸው የሚችሉ መልእክቶች

| መልእክት | ትርጉሙ |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | የፈረንሳይ ቁልፍ የለም። አንድ ያክሉ። |
| `Inactive: needs a free PISTE account. ...` (በ `list_jurisdictions` ውስጥ) | ተመሳሳይ። |
| `PISTE refused the client credentials ...` | መለያው (ID) ወይም ሚስጥሩ (secret) የተሳሳተ ነው ወይም ከእንግዲህ የሚሠራ አይደለም። ሁለቱንም ከ Authentification ትር እንደገና ይቅዱ። |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | መተግበሪያዎ ለዚያ API አልተመዘገበም፣ ወይም ውሎቹን አልተቀበሉም። ደረጃ 2 እና 3 ን ይመልከቱ። |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | የአሜሪካ ቁልፍ የለም። ፍለጋ በቀን ለጥቂት ጥሪዎች ይሠራል። |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | የማሳያ ቁልፉ (demo key) አልቋል። የራስዎን ቁልፍ ያክሉ። |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | ቁልፉ የተሳሳተ ነው፣ ወይም ገና ከኢሜይሉ አልተረጋገጠም። |

ባዶ እሴት (value) እንደ ቁልፍ አለመኖር ይቆጠራል።

## ፈቃዶች (WLM_PERMITTED)

ይህ የ API ቁልፍ አይደለም፣ መጫኛውም አያዘጋጀውም። **ያዘጋጁት ያ ፈቃድ ራስዎ ካለዎት ብቻ ነው።**

አንዳንድ ምንጮች ውሎቻቸው ወይም robots.txt ያለፈቃድ በራስ-ሰር (automated) መጠቀምን ስለሚከለክሉ በነባሪ (default) ጠፍተዋል።
ከአሳታሚው ፈቃድ ካለዎት፣ የምንጩን ኮድ በ `env` ክፍል ውስጥ ወደ `WLM_PERMITTED`፣ በኮማ ተለያይቶ፣ በመጨመር ያብሩት፦
`"WLM_PERMITTED": "in,de"`።

| ኮድ | ምንጭ |
|---|---|
| `az` | አዘርባጃን፦ e-qanun.az (የፍትሕ ሚኒስቴር) |
| `bh` | ባሕሬን፦ Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | ኮሎምቢያ፦ Función Pública፣ Gestor Normativo (ማሻሻያዎች የተካተቱበት ሕግ) |
| `de` | ጀርመን፦ NeuRIS (የፌዴራል የሕግ መረጃ ፖርታል፣ የሙከራ አገልግሎት) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | ግሪክ፦ National Printing Office፣ Government Gazette ፍለጋ (search.et.gr) |
| `in` | ሕንድ፦ India Code (indiacode.gov.in) |
| `mu` | ሞሪሸስ፦ Supreme Court (supremecourt.govmu.org) |
| `sg` | ሲንጋፖር፦ የፍርድ ቤት ፍርዶች (elitigation.sg) |

ያለ ፈቃድ፣ Fontes እንዲህ ይላል፦ `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
