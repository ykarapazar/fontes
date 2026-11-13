> یہ مشین کی مدد سے کیا گیا ترجمہ ہے۔ انگریزی ورژن ہی مستند ہے۔

# API کیز

Fontes کا تقریباً ہر ماخذ کی (key) کے بغیر کام کرتا ہے۔ دو کو ایک مفت کی درکار ہے:

| کی | کیا کھولتی ہے | اس کے بغیر |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | فرانس: Judilibre (عدالتی فیصلے) اور Légifrance (قانون سازی) | فرانس بند ہے۔ `list_jurisdictions` اسے غیر فعال دکھاتا ہے۔ |
| `WLM_US_GOVINFO_KEY` | امریکہ: govinfo تلاش (وفاقی عدالتوں کی آراء، Statutes at Large، عوامی قوانین) | Fontes مشترکہ `DEMO_KEY` استعمال کرتا ہے: ہر IP ایڈریس کے لیے دن میں تقریباً 10 تلاشیں۔ کسی معلوم فیصلے کو کھولنے اور US Code کے لیے کی درکار نہیں۔ |

کیز اختیاری ہیں۔ آپ انہیں بعد میں شامل کر سکتے ہیں۔

## کی شامل کرنا

**انسٹالر کے ساتھ۔** انسٹال کرتے وقت، انسٹالر پوچھتا ہے کہ کیا آپ کیز شامل کرنا چاہتے ہیں۔ چھوڑنے کے لیے
**Not now** منتخب کریں (یا Enter دبائیں)۔ بعد میں کیز شامل یا تبدیل کرنے کے لیے، **Add or change keys** چلائیں:

- Mac: Fontes Installer ایپ دوبارہ کھولیں اور **Add or change keys** منتخب کریں، یا انسٹالر فولڈر میں
  `Add or change keys.command` پر ڈبل کلک کریں۔
- Windows: انسٹالر فولڈر میں `Add or change keys.cmd` پر ڈبل کلک کریں۔ Windows سیٹ اپ
  پروگرام، جب دستیاب ہوگا، اسے Start menu > Fontes میں بھی رکھ دے گا۔

ٹائپنگ چھپی رہتی ہے۔ ہر کی کے لیے: اسے پیسٹ کریں، جو موجود ہے اسے رکھنے کے لیے Enter دبائیں، یا اسے
ہٹانے کے لیے `-` ٹائپ کریں۔ کیز ہر اس ایپ میں جاتی ہیں جس میں پہلے سے Fontes موجود ہو۔

**Claude Desktop ایکسٹینشن (.mcpb) کے ساتھ۔** Claude > Settings > Extensions > Fontes کھولیں اور
فیلڈز پُر کریں۔ یہ سب اختیاری ہیں۔

**ہاتھ سے۔** اپنی ایپ کی MCP config میں `fontes` اندراج کے `env` بلاک میں variables شامل کریں:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

کسی بھی تبدیلی کے بعد ایپ دوبارہ شروع کریں۔

## فرانس: PISTE (مفت)

1. [piste.gouv.fr](https://piste.gouv.fr) پر اکاؤنٹ بنائیں۔ اس کا مطلب PISTE کی شرائط (CGU) قبول کرنا ہے۔
2. API > **Consentement CGU API** پر جائیں۔ **JUDILIBRE** اور **Légifrance** (production) کی شرائط قبول کریں۔
3. ایک **production application** بنائیں۔ آپ کے لیے بنایا گیا `APP_SANDBOX` production تک نہیں پہنچ سکتا۔
   "Modifier l'application" کے تحت، **JUDILIBRE (production)** اور **Légifrance (production)** پر ٹک کریں، پھر لاگو کریں۔
4. ایپ کا **Authentification** ٹیب کھولیں۔ `client_id` اور `client_secret` کاپی کریں۔
5. **Add or change keys** چلائیں اور انہیں پیسٹ کریں۔

شرائط، مختصراً:

- ڈیٹا: Licence Ouverte / Etalab 2.0۔ دوبارہ استعمال، بشمول تجارتی دوبارہ استعمال، انتساب کے ساتھ جائز ہے۔
- اپنی اسناد (credentials) شائع یا شیئر نہ کریں۔ اگر وہ لیک ہو جائیں تو PISTE کو بتائیں۔
- Légifrance API ایک بیٹا سروس ہے۔ اسے معطل کیا جا سکتا ہے، اور اس کے کوٹے ہیں (فی سیکنڈ، منٹ اور دن)۔
- Légifrance کے متن مستند ورژن نہیں ہیں۔ صرف دستخط شدہ Journal officiel PDF مستند ہے۔
- Judilibre: ججوں یا کلرکوں کے نام ان کے کام کی جانچ، موازنہ یا پیش گوئی کے لیے استعمال نہ کریں
  (Code de l'organisation judiciaire art. L111-13؛ ایک فوجداری جرم)۔
- Judilibre: GDPR کی پابندی کریں۔ فریقین کی دوبارہ شناخت کی کوشش نہ کریں۔

آپ کے کوٹے PISTE پر API Sélectionnées > Actions > Consulter les quotas کے تحت ہیں۔

## امریکہ: api.data.gov (مفت)

1. [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) پر جائیں (کی اسکرین پر دکھائی جاتی ہے)
   یا [api.data.gov/signup](https://api.data.gov/signup/) پر (کی آپ کو ای میل کی جاتی ہے)۔
2. اپنا نام اور ای میل درج کریں۔ "how will you use it" والا فیلڈ اختیاری ہے۔
3. 40 حروف والی کی کاپی کریں۔
4. **Add or change keys** چلائیں اور اسے امریکی کی کے طور پر پیسٹ کریں۔

شرائط، مختصراً:

- اپنی کی کے ساتھ، govinfo ایک گھنٹے میں 36,000 تک درخواستوں کی اجازت دیتا ہے۔
- ہمیں API کے لیے مخصوص سروس کی کوئی شرائط نہیں ملیں (api.data.gov/terms/ موجود نہیں)۔ غیر تصدیق شدہ۔
  [govinfo کی پالیسیاں](https://www.govinfo.gov/about/policies) اور
  [data.gov کی پرائیویسی پالیسی](https://data.gov/privacy-policy/) دیکھیں۔
- کی اپنے پاس رکھیں۔

## کیز کہاں محفوظ ہوتی ہیں

- **انسٹالر یا ہاتھ سے:** ہر ایپ کی MCP config فائل میں سادہ متن کے طور پر، `fontes` اندراج کے
  `env` بلاک میں۔ جو کوئی بھی آپ کی یوزر فائلیں پڑھ سکتا ہے وہ کیز پڑھ سکتا ہے۔
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
- **Claude Desktop ایکسٹینشن (.mcpb):** Claude یہ فیلڈز اپنی سیٹنگز میں رکھتا ہے اور انہیں
  آپ کے سسٹم کی محفوظ اسٹوریج (Mac پر Keychain، Windows پر Credential Manager) سے محفوظ کرتا ہے۔

ہر تبدیلی سے پہلے، انسٹالر config فائل کی ایک کاپی اس کے ساتھ محفوظ کرتا ہے
(`<file>.fontes-backup-<time>`)۔ کیز شامل کرنے کے بعد بنی کاپیوں میں کیز بھی ہوتی ہیں۔ جن پرانی
کاپیوں کی آپ کو ضرورت نہیں انہیں حذف کر دیں۔

## کی تبدیل کرنا یا ہٹانا

- **Add or change keys** چلائیں۔ کی بدلنے کے لیے نئی کی پیسٹ کریں، یا اسے ہٹانے کے لیے `-` ٹائپ کریں۔
- یا `env` بلاک میں ہاتھ سے ترمیم کریں اور ایپ دوبارہ شروع کریں۔
- Fontes ان انسٹال کرنے سے اس کا پورا اندراج، کیز سمیت، ہٹ جاتا ہے۔ یہ بیک اپ کاپیاں حذف نہیں کرتا۔
- اگر کوئی کی لیک ہو گئی ہو، تو اسے ماخذ پر بھی بدلیں: PISTE پر، اپنی ایپ کے لیے نئی اسناد بنائیں؛
  api.data.gov کے لیے، نئی کی کے لیے سائن اپ کریں۔

## پیغامات جو آپ کو نظر آ سکتے ہیں

| پیغام | مطلب |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | فرانس کی کوئی کی نہیں۔ ایک شامل کریں۔ |
| `Inactive: needs a free PISTE account. ...` (`list_jurisdictions` میں) | وہی۔ |
| `PISTE refused the client credentials ...` | ID یا secret غلط ہے یا اب درست نہیں۔ دونوں کو Authentification ٹیب سے دوبارہ کاپی کریں۔ |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | آپ کی ایپ اس API کی سبسکرائبڈ نہیں، یا آپ نے اس کی شرائط قبول نہیں کیں۔ مراحل 2 اور 3 دیکھیں۔ |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | امریکہ کی کوئی کی نہیں۔ تلاش دن میں چند کالز کے لیے کام کرتی ہے۔ |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | demo key استعمال ہو چکی ہے۔ اپنی کی شامل کریں۔ |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | کی غلط ہے، یا ای میل سے ابھی تصدیق نہیں ہوئی۔ |

خالی قدر کو کی نہ ہونا شمار کیا جاتا ہے۔

## اجازتیں (WLM_PERMITTED)

یہ API کی نہیں ہے، اور انسٹالر اسے سیٹ نہیں کرتا۔ **اسے صرف اس صورت میں سیٹ کریں جب وہ
اجازت خود آپ کے پاس ہو۔**

کچھ ذرائع بطورِ ڈیفالٹ بند ہیں کیونکہ ان کی شرائط یا robots.txt اجازت کے بغیر خودکار استعمال کی ممانعت
کرتی ہیں۔ اگر آپ کے پاس ناشر کی اجازت ہے، تو کسی ماخذ کو آن کرنے کے لیے اس کا کوڈ
`WLM_PERMITTED` میں، کوما سے الگ کر کے، `env` بلاک میں شامل کریں: `"WLM_PERMITTED": "in,de"`۔

| کوڈ | ماخذ |
|---|---|
| `az` | آذربائیجان: e-qanun.az (وزارتِ انصاف) |
| `bh` | بحرین: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | کولمبیا: Función Pública، Gestor Normativo (یکجا شدہ قانون سازی) |
| `de` | جرمنی: NeuRIS (وفاقی قانونی معلومات کا پورٹل، آزمائشی سروس) |
| `difc` | دبئی انٹرنیشنل فنانشل سینٹر کورٹس (difccourts.ae) |
| `gr` | یونان: قومی چھاپہ خانہ، سرکاری گزٹ کی تلاش (search.et.gr) |
| `in` | بھارت: India Code (indiacode.gov.in) |
| `mu` | ماریشس: سپریم کورٹ (supremecourt.govmu.org) |
| `sg` | سنگاپور: عدالتی فیصلے (elitigation.sg) |

اجازت کے بغیر، Fontes کہتا ہے: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
