> دا ژباړه د ماشین په مرسته شوې ده. انګلیسي نسخه معتبره ده.

# API کیلي

په Fontes کې نږدې هره سرچینه پرته له کیلي کار کوي. درې یې یوې وړیا کیلي ته اړتیا لري:

| کیلي | څه پرانیزي | له هغې پرته |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | فرانسه: Judilibre (د محکمو فیصلې) او Légifrance (قوانین او مقررې) | فرانسه بنده ده. `list_jurisdictions` یې غیر فعاله ښيي. |
| `WLM_US_GOVINFO_KEY` | متحده ایالات: د govinfo لټون (د فدرالي محکمو نظرونه، Statutes at Large، عامه قوانین) | Fontes ګډه `DEMO_KEY` کاروي: د هرې IP پتې لپاره په ورځ کې شاوخوا 10 لټونونه. د یوې معلومې فیصلې پرانیستل او US Code کیلي ته اړتیا نه لري. |
| `WLM_US_COURTLISTENER_KEY` | د متحده ایالاتو ایالتي محکمې (`us-states`): د ټولو 50 ایالتونو او DC د عالي او استیناف محکمو نظرونه، له CourtListener څخه | د متحده ایالاتو د ایالتي محکمو قضايي رویه بنده ده. `list_jurisdictions` یې غیرفعاله ښيي. |

کیلي اختیاري دي. تاسو یې وروسته هم ور زیاتولای شئ.

## د کیلي ور زیاتول

**له نصبوونکي سره.** کله چې Fontes جوړ شي، نصبوونکی وړاندیز کوي چې کیلي ور زیاتې کړي. په Mac کې، پر
**کیلي ور زیاتې کړئ** کلیک وکړئ، یا د تېرېدو لپاره پر **ترسره شو**؛ په Windows کې، پوښتنې ته ځواب ورکړئ (د
تېرېدو لپاره Enter کېکاږئ). د دې لپاره چې وروسته کیلي ور زیاتې یا بدلې کړئ، **کیلي ور زیاتې یا بدلې کړئ** وچلوئ:

- Mac: Fontes Installer اپ بیا پرانیزئ او **کیلي ور زیاتې یا بدلې کړئ** وټاکئ.
- Windows: د Start menu خلاص کړئ، بیا **Fontes** → **کیلي ور زیاتې یا بدلې کړئ** وټاکئ.

لیکل پټ وي. د هرې کیلي لپاره: هغه ونښلوئ، د هغه څه د ساتلو لپاره چې شته Enter کېکاږئ، یا د لرې کولو لپاره
`-` ولیکئ. کیلي هر هغه اپ ته ځي چې لا دمخه Fontes لري.

**د Claude Desktop له غځونې (.mcpb) سره.** Claude > Settings > Extensions > Fontes پرانیزئ او
ساحې ډکې کړئ. ټولې یې اختیاري دي.

**په لاس.** متغیرونه د خپل اپ د MCP تنظیماتو د `fontes` ننوتنې `env` بلاک ته ور زیات کړئ:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

له هر بدلون وروسته اپ بیا پیل کړئ.

## فرانسه: PISTE (وړیا)

1. په [piste.gouv.fr](https://piste.gouv.fr) کې یو حساب جوړ کړئ. دا د PISTE د شرطونو (CGU) منل دي.
2. API > **Consentement CGU API** ته لاړ شئ. د **JUDILIBRE** او **Légifrance** (production) شرطونه ومنئ.
3. یو **production application** جوړ کړئ. هغه `APP_SANDBOX` چې ستاسو لپاره جوړ شوی production ته نشي رسېدای.
   د "Modifier l'application" لاندې، **JUDILIBRE (production)** او **Légifrance (production)** په نښه کړئ، بیا یې پلي کړئ.
4. د اپ **Authentification** ټب پرانیزئ. `client_id` او `client_secret` کاپي کړئ.
5. **Add or change keys** وچلوئ او هغه ونښلوئ.

شرطونه، په لنډه توګه:

- معلومات: Licence Ouverte / Etalab 2.0. بیا کارونه، په شمول د سوداګریزې بیا کارونې، د سرچینې له یادولو سره اجازه لري.
- خپل اعتبارنامې (credentials) مه خپروئ او مه یې شریکوئ. که ښکاره شي، PISTE ته خبر ورکړئ.
- د Légifrance API یو beta خدمت دی. کېدای شي وځنډول شي، او سهمیې (quotas) لري (په ثانیه، دقیقه او ورځ).
- د Légifrance متنونه معتبره نسخه نه ده. یوازې د Journal officiel لاسلیک شوی PDF معتبر دی.
- Judilibre: د قاضیانو یا منشیانو نومونه د هغوی د کار د ارزونې، پرتلنې یا وړاندوینې لپاره مه کاروئ
  (Code de l'organisation judiciaire art. L111-13؛ جزايي جرم).
- Judilibre: GDPR تعقیب کړئ. هڅه مه کوئ چې اړخونه بیا وپېژنئ.

ستاسو سهمیې په PISTE کې د API Sélectionnées > Actions > Consulter les quotas لاندې دي.

## متحده ایالات: api.data.gov (وړیا)

1. [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) ته لاړ شئ (کیلي په پرده ښودل کېږي)
   یا [api.data.gov/signup](https://api.data.gov/signup/) ته (کیلي تاسو ته برېښنالیک کېږي).
2. خپل نوم او برېښنالیک ولیکئ. د "how will you use it" ساحه اختیاري ده.
3. 40-توري کیلي کاپي کړئ.
4. **Add or change keys** وچلوئ او هغه د امریکا د کیلي په توګه ونښلوئ.

شرطونه، په لنډه توګه:

- له خپلې کیلي سره، govinfo په یوه ساعت کې تر 36,000 غوښتنو پورې اجازه ورکوي.
- موږ د API لپاره ځانګړي د خدمت شرطونه ونه موندل (api.data.gov/terms/ شتون نه لري). تایید شوي نه دي.
  [د govinfo پالیسۍ](https://www.govinfo.gov/about/policies) او
  [د data.gov د محرمیت پالیسي](https://data.gov/privacy-policy/) وګورئ.
- کیلي له ځان سره وساتئ.

## د متحده ایالاتو ایالتي محکمې: CourtListener (وړیا)

CourtListener د [Free Law Project](https://free.law) لخوا پرمخ وړل کېږي، چې یو غیرانتفاعي سازمان دی او له 2010 کال راهیسې یې د متحده ایالاتو د محکمو نظرونه راټول کړي او د ټولو لپاره یې وړیا کړي. د هغه د خپل شمېرنې له مخې، دا له نهو میلیونو څخه زیاتې فیصلې لري. دا رسمي سرچینه نه ده: محکمې خپل نظرونه پخپله خپروي، او CourtListener هغه د محکمو له وېبپاڼو او سکین شویو حقوقي راپورونو څخه راټولوي. د Fontes هره ځواب چې له هغه څخه وي دا ویلی. Fontes د Free Law Project سره تړاو نه لري.

1. په [courtlistener.com](https://www.courtlistener.com/sign-in/) کې وړیا حساب جوړ کړئ.
2. خپل پروفایل پرانیزئ او خپل API token کاپي کړئ.
3. **Add or change keys** وچلوئ او هغه د CourtListener د کیلي په توګه ونښلوئ.

شرطونه، په لنډه توګه ([بشپړ شرطونه](https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies)):

- token یوازې ستاسو دی: مه یې شریکوئ، مه یې له نورو سره یو ځای کوئ یا بیا پلورئ، او څو حسابونه مه کاروئ.
- تاسو مسوول یاست چې د AI اپ ستاسو له token سره څه کوي.
- د دوی د معلوماتو په اړه د AI تحلیل داسې مه وړاندې کوئ چې ګواکې Free Law Project یې جوړ کړی، تایید کړی یا ازمویلی وي.
- وړیا حساب په دقیقه کې 5، په ساعت کې 50 او په ورځ کې 125 غوښتنې اجازه ورکوي. یو لټون یوه غوښتنه ده؛ د یوې فیصلې پرانیستل دوې دي. د Free Law Project غړيتوب دا حدود لوړوي.
- CourtListener د دقت تضمین نه کوي. مخکې له دې چې پر یوه نظر تکیه وکړئ، د محکمې له نقل سره یې وګورئ.

## کیلي چېرته ساتل کېږي

- **نصبوونکی یا په لاس:** د ساده متن په توګه د هر اپ د MCP تنظیماتو په فایل کې، د
  `fontes` ننوتنې په `env` بلاک کې. هر څوک چې ستاسو د کارن فایلونه لوستلای شي، کیلي هم لوستلای شي.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac)،
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` یا `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **د Claude Desktop غځونه (.mcpb):** Claude دا ساحې په خپلو تنظیماتو کې ساتي او د ستاسو د سیسټم
  په خوندي زېرمه (Keychain په Mac کې، Credential Manager په Windows کې) یې ساتنه کوي.

د هر بدلون مخکې، نصبوونکی د تنظیماتو د فایل یوه کاپي د هغه تر څنګ خوندي کوي
(`<file>.fontes-backup-<time>`). هغه کاپي چې له کیلي ور زیاتولو وروسته جوړې شوې، کیلي هم لري. زړې
کاپي چې ورته اړتیا نه لرئ ړنګې کړئ.

## د کیلي بدلول یا لرې کول

- **Add or change keys** وچلوئ. د بدلولو لپاره نوې کیلي ونښلوئ، یا د لرې کولو لپاره `-` ولیکئ.
- یا `env` بلاک په لاس سم کړئ او اپ بیا پیل کړئ.
- د Fontes لرې کول د هغه ټوله ننوتنه، له کیلي سره، لرې کوي. بیک اپ کاپي نه ړنګوي.
- که یوه کیلي ښکاره شوې وي، په سرچینه کې یې هم بدله کړئ: په PISTE کې، د خپل اپ لپاره نوې اعتبارنامې جوړې کړئ؛
  د api.data.gov لپاره، د نوې کیلي لپاره نوم لیکنه وکړئ.

## هغه پیغامونه چې کېدای شي یې ووینئ

| پیغام | معنا |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | د فرانسې کیلي نشته. یوه ور زیاته کړئ. |
| `Inactive: needs a free PISTE account. ...` (په `list_jurisdictions` کې) | همدا. |
| `PISTE refused the client credentials ...` | ID یا secret غلط دی یا نور اعتبار نه لري. دواړه بیا د Authentification له ټب څخه کاپي کړئ. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | ستاسو اپ په هغه API کې ګډون نه لري، یا تاسو د هغه شرطونه نه دي منلي. 2 او 3 ګامونه وګورئ. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | د امریکا کیلي نشته. لټون په ورځ کې د یو څو غوښتنو لپاره کار کوي. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | demo کیلي مصرف شوې. خپله کیلي ور زیاته کړئ. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | کیلي غلطه ده، یا لا له برېښنالیک څخه نه ده تایید شوې. |

یو خالي ارزښت د کیلي نشتوالی ګڼل کېږي.

## اجازې (WLM_PERMITTED)

دا API کیلي نه ده، او نصبوونکی یې نه ټاکي. **یوازې هغه وخت یې وټاکئ چې هغه
اجازه پخپله ولرئ.**

ځینې سرچینې په ډیفالټ ډول بندې دي ځکه چې د هغوی شرطونه یا robots.txt پرته له اجازې اتومات کارونه
منع کوي. که تاسو د خپرونکي اجازه لرئ، یوه سرچینه د هغې د کوډ په ور زیاتولو سره روښانه کړئ
`WLM_PERMITTED` ته، د کامې په جلا کولو، په `env` بلاک کې: `"WLM_PERMITTED": "in,de"`.

| کوډ | سرچینه |
|---|---|
| `az` | آذربایجان: e-qanun.az (د عدلیې وزارت) |
| `bh` | بحرین: د قانون جوړونې او حقوقي نظر کمیسیون (lloc.gov.bh) |
| `co` | کولمبیا: Función Pública، Gestor Normativo (تلفیقي قوانین او مقررې) |
| `de` | آلمان: NeuRIS (د فدرالي حقوقي معلوماتو پورټل، آزمایښتي خدمت) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | یونان: د چاپ ملي دفتر، د Government Gazette لټون (search.et.gr) |
| `in` | هند: India Code (indiacode.gov.in) |
| `mu` | موریشس: ستره محکمه (supremecourt.govmu.org) |
| `sg` | سنګاپور: د محکمو فیصلې (elitigation.sg) |

پرته له اجازې، Fontes وايي: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
