> این ترجمه با کمک ماشین انجام شده است. نسخه انگلیسی معتبر است.

# کلیدهای API

تقریباً همه منابع Fontes بدون کلید کار می‌کنند. دو منبع به یک کلید رایگان نیاز دارند:

| کلید | چه چیزی را فعال می‌کند | بدون آن |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | فرانسه: Judilibre (آرای دادگاه‌ها) و Légifrance (قوانین و مقررات) | فرانسه خاموش است. `list_jurisdictions` آن را غیرفعال نشان می‌دهد. |
| `WLM_US_GOVINFO_KEY` | ایالات متحده: جست‌وجوی govinfo (آرای دادگاه‌های فدرال، Statutes at Large، قوانین عمومی) | Fontes از `DEMO_KEY` مشترک استفاده می‌کند: حدود ۱۰ جست‌وجو در روز برای هر نشانی IP. باز کردن یک رأی مشخص و US Code به کلید نیاز ندارند. |

کلیدها اختیاری هستند. می‌توانید آن‌ها را بعداً اضافه کنید.

## افزودن کلید

**با نصب‌کننده.** نصب‌کننده در حین نصب می‌پرسد آیا می‌خواهید کلید اضافه کنید. برای رد شدن
**Not now** را انتخاب کنید (یا Enter را بزنید). برای افزودن یا تغییر کلیدها در آینده، **Add or change keys** را اجرا کنید:

- Mac: برنامه Fontes Installer را دوباره باز کنید و **Add or change keys** را انتخاب کنید، یا روی
  `Add or change keys.command` در پوشه نصب‌کننده دوبار کلیک کنید.
- Windows: روی `Add or change keys.cmd` در پوشه نصب‌کننده دوبار کلیک کنید. برنامه راه‌اندازی Windows،
  پس از اینکه در دسترس قرار گیرد، آن را در Start menu > Fontes هم قرار می‌دهد.

آنچه تایپ می‌کنید نمایش داده نمی‌شود. برای هر کلید: آن را paste کنید، برای نگه داشتن مقدار فعلی Enter را بزنید، یا برای
حذف آن `-` را تایپ کنید. کلیدها به هر برنامه‌ای که از قبل Fontes را دارد اضافه می‌شوند.

**با افزونه Claude Desktop (.mcpb).** Claude > Settings > Extensions > Fontes را باز کنید و
فیلدها را پر کنید. همه آن‌ها اختیاری هستند.

**به‌صورت دستی.** متغیرها را به بلوک `env` در مدخل `fontes` در پیکربندی MCP برنامه خود اضافه کنید:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

پس از هر تغییر، برنامه را دوباره راه‌اندازی کنید.

## فرانسه: PISTE (رایگان)

1. در [piste.gouv.fr](https://piste.gouv.fr) یک حساب بسازید. این یعنی پذیرفتن شرایط PISTE (CGU).
2. به API > **Consentement CGU API** بروید. شرایط **JUDILIBRE** و **Légifrance** (production) را بپذیرید.
3. یک **production application** بسازید. `APP_SANDBOX` که برای شما ساخته شده نمی‌تواند به production دسترسی پیدا کند.
   زیر "Modifier l'application"، گزینه‌های **JUDILIBRE (production)** و **Légifrance (production)** را تیک بزنید، سپس اعمال کنید.
4. زبانه **Authentification** برنامه را باز کنید. `client_id` و `client_secret` را کپی کنید.
5. **Add or change keys** را اجرا کنید و آن‌ها را paste کنید.

شرایط، به‌طور خلاصه:

- داده‌ها: Licence Ouverte / Etalab 2.0. استفاده مجدد، از جمله استفاده مجدد تجاری، با ذکر منبع مجاز است.
- اطلاعات ورود (credentials) خود را منتشر نکنید یا با دیگران به اشتراک نگذارید. اگر فاش شدند به PISTE اطلاع دهید.
- API مربوط به Légifrance یک سرویس بتا است. ممکن است تعلیق شود، و سهمیه (در ثانیه، دقیقه و روز) دارد.
- متن‌های Légifrance نسخه معتبر نیستند. فقط PDF امضاشده Journal officiel معتبر است.
- Judilibre: از نام قضات یا منشیان دادگاه برای ارزیابی، مقایسه یا پیش‌بینی کار آن‌ها استفاده نکنید
  (Code de l'organisation judiciaire ماده L111-13؛ یک جرم کیفری).
- Judilibre: از GDPR پیروی کنید. برای شناسایی دوباره طرفین تلاش نکنید.

سهمیه‌های شما در PISTE زیر API Sélectionnées > Actions > Consulter les quotas هستند.

## ایالات متحده: api.data.gov (رایگان)

1. به [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) بروید (کلید روی صفحه نمایش داده می‌شود)
   یا به [api.data.gov/signup](https://api.data.gov/signup/) (کلید برای شما ایمیل می‌شود).
2. نام و ایمیل خود را وارد کنید. فیلد "how will you use it" اختیاری است.
3. کلید ۴۰ نویسه‌ای را کپی کنید.
4. **Add or change keys** را اجرا کنید و آن را به‌عنوان کلید ایالات متحده paste کنید.

شرایط، به‌طور خلاصه:

- با کلید خودتان، govinfo تا ۳۶٬۰۰۰ درخواست در ساعت اجازه می‌دهد.
- هیچ شرایط خدمات مختص API پیدا نکردیم (api.data.gov/terms/ وجود ندارد). تأییدنشده.
  [سیاست‌های govinfo](https://www.govinfo.gov/about/policies) و
  [سیاست حریم خصوصی data.gov](https://data.gov/privacy-policy/) را ببینید.
- کلید را برای خودتان نگه دارید.

## کلیدها کجا ذخیره می‌شوند

- **نصب‌کننده یا به‌صورت دستی:** به‌صورت متن ساده در فایل پیکربندی MCP هر برنامه، در بلوک `env` مدخل
  `fontes`. هر کسی که بتواند فایل‌های کاربری شما را بخواند می‌تواند کلیدها را بخواند.
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
- **افزونه Claude Desktop (.mcpb):** Claude این فیلدها را در تنظیمات خود نگه می‌دارد و با
  فضای ذخیره‌سازی امن سیستم شما (Keychain در Mac، Credential Manager در Windows) از آن‌ها محافظت می‌کند.

پیش از هر تغییر، نصب‌کننده یک نسخه از فایل پیکربندی را در کنار آن ذخیره می‌کند
(`<file>.fontes-backup-<time>`). نسخه‌هایی که پس از افزودن کلیدها ساخته شده‌اند کلیدها را هم دارند. نسخه‌های
قدیمی را که لازم ندارید حذف کنید.

## تغییر یا حذف کلید

- **Add or change keys** را اجرا کنید. برای جایگزینی یک کلید جدید paste کنید، یا برای حذف آن `-` را تایپ کنید.
- یا بلوک `env` را به‌صورت دستی ویرایش کنید و برنامه را دوباره راه‌اندازی کنید.
- حذف Fontes کل مدخل آن را، همراه با کلیدها، حذف می‌کند. نسخه‌های پشتیبان را حذف نمی‌کند.
- اگر کلیدی فاش شد، آن را در منبع هم جایگزین کنید: در PISTE، برای برنامه خود اطلاعات ورود جدید بسازید؛
  برای api.data.gov، برای یک کلید جدید ثبت‌نام کنید.

## پیام‌هایی که ممکن است ببینید

| پیام | معنا |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | کلید فرانسه وجود ندارد. یکی اضافه کنید. |
| `Inactive: needs a free PISTE account. ...` (در `list_jurisdictions`) | همان. |
| `PISTE refused the client credentials ...` | شناسه یا secret اشتباه است یا دیگر معتبر نیست. هر دو را دوباره از زبانه Authentification کپی کنید. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | برنامه شما در آن API مشترک نیست، یا شرایط آن را نپذیرفته‌اید. مراحل ۲ و ۳ را ببینید. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | کلید ایالات متحده وجود ندارد. جست‌وجو برای چند فراخوانی در روز کار می‌کند. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | کلید نمایشی تمام شده است. کلید خودتان را اضافه کنید. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | کلید اشتباه است، یا هنوز از طریق ایمیل تأیید نشده است. |

مقدار خالی به معنای نداشتن کلید است.

## مجوزها (WLM_PERMITTED)

این یک کلید API نیست و نصب‌کننده آن را تنظیم نمی‌کند. **فقط در صورتی آن را تنظیم کنید که خودتان آن
اجازه را داشته باشید.**

برخی منابع به‌طور پیش‌فرض خاموش هستند، زیرا شرایط یا robots.txt آن‌ها استفاده خودکار بدون
اجازه را ممنوع می‌کند. اگر از ناشر اجازه دارید، یک منبع را با افزودن کد آن به
`WLM_PERMITTED`، جداشده با ویرگول، در بلوک `env` روشن کنید: `"WLM_PERMITTED": "in,de"`.

| کد | منبع |
|---|---|
| `az` | آذربایجان: e-qanun.az (وزارت دادگستری) |
| `bh` | بحرین: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | کلمبیا: Función Pública، Gestor Normativo (قوانین و مقررات تنقیح‌شده) |
| `de` | آلمان: NeuRIS (درگاه اطلاعات حقوقی فدرال، سرویس آزمایشی) |
| `difc` | دادگاه‌های مرکز مالی بین‌المللی دبی (difccourts.ae) |
| `gr` | یونان: چاپخانه ملی، جست‌وجوی روزنامه رسمی (search.et.gr) |
| `in` | هند: India Code (indiacode.gov.in) |
| `mu` | موریس: دیوان عالی (supremecourt.govmu.org) |
| `sg` | سنگاپور: احکام دادگاه‌ها (elitigation.sg) |

بدون اجازه، Fontes می‌گوید: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
