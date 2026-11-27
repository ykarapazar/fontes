> این ترجمه با کمک ماشین انجام شده است. نسخه انگلیسی معتبر است.

# نصب Fontes

Fontes به برنامه هوش مصنوعی شما امکان می‌دهد آرای دادگاه‌ها و قوانین و مقررات را به‌صورت زنده در وب‌سایت‌های
دادگاه‌ها و دولت‌ها در ۱۲۵ حوزه قضایی جست‌وجو کند. هر نتیجه به نسخه اصلی پیوند دارد. این یک سرور MCP
استاندارد است، پس در هر برنامه‌ای که بتواند یک سرور MCP محلی اجرا کند کار می‌کند: Claude Desktop، Codex، Claude
Code، Cursor، VS Code (GitHub Copilot)، Gemini CLI، Windsurf، Zed، LM Studio، Cline و دیگران.

برنامه خود را انتخاب کنید، مراحل آن را دنبال کنید، سپس [بررسی کنید که کار می‌کند](#بررسی-اینکه-کار-میکند).

## Claude Desktop

1. فایل `.mcpb` مربوط به Fontes را از
   [آخرین نسخه](https://github.com/ykarapazar/fontes/releases/latest) دریافت کنید.
2. روی آن دوبار کلیک کنید. Claude Desktop آن را باز می‌کند.
3. روی **Install** کلیک کنید.

## Codex

در ترمینال:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI و افزونه Codex برای IDE این تنظیم را به اشتراک می‌گذارند (`~/.codex/config.toml`).
به [uv](#به-uv-نیاز-دارید) نیاز دارید.

## Claude Code

در ترمینال:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

به [uv](#به-uv-نیاز-دارید) نیاز دارید.

## برنامه‌های دیگر

هر یک از این‌ها به [uv](#به-uv-نیاز-دارید) نیاز دارد. مدخل را اضافه کنید، ذخیره کنید، سپس برنامه را ببندید و دوباره باز کنید.

**Cursor:** در `~/.cursor/mcp.json` (همه پروژه‌ها) یا `.cursor/mcp.json` (یک پروژه):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** فرمان **MCP: Add Server** را از Command Palette اجرا کنید،
**Command (stdio)** را انتخاب کنید، `uvx fontes-mcp` را وارد کنید و نام سرور را `fontes` بگذارید. یا این را به
`~/.copilot/mcp-config.json` اضافه کنید:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

پیکربندی‌های قدیمی‌تر VS Code از `.vscode/mcp.json` استفاده می‌کنند که در آن کلید سطح بالا به جای
`mcpServers`، `servers` است.

**Gemini CLI:** در ترمینال، `gemini mcp add -s user fontes uvx fontes-mcp`. یا این را به
`~/.gemini/settings.json` اضافه کنید:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** فایل تنظیمات خود را باز کنید (**zed: open settings file**) و این را اضافه کنید:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** در نوار کناری سمت راست، زبانه **Program** را باز کنید، روی **Install → Edit
mcp.json** کلیک کنید و این را اضافه کنید:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** روی نماد **MCP Servers** کلیک کنید، زبانه **Configure** را باز کنید، روی **Configure MCP
Servers** کلیک کنید و همان مدخل `mcpServers` مربوط به LM Studio را اضافه کنید.

**Claude Desktop، به‌صورت دستی** (به جای فایل `.mcpb`): همان مدخل `mcpServers` را به
`claude_desktop_config.json` اضافه کنید (macOS: `~/Library/Application Support/Claude/`، Windows:
`%APPDATA%\Claude\`).

**هر برنامه MCP دیگر** (Windsurf و دیگران): مستندات خود آن برنامه می‌گوید سرورهای MCP را
کجا نگه می‌دارد. بیشتر آن‌ها همین مدخل را می‌پذیرند: فرمان `uvx`، آرگومان `fontes-mcp`.

اگر برنامه نتواند `uvx` را پیدا کند، از مسیر کامل آن استفاده کنید (در macOS و Linux، `which uvx` آن را چاپ می‌کند).

## به uv نیاز دارید

Codex، Claude Code و برنامه‌های دیگر Fontes را با `uvx` اجرا می‌کنند که همراه با **uv** می‌آید، ابزاری کوچک
و رایگان از Astral. برای نصب آن،
[راهنمای Astral](https://docs.astral.sh/uv/getting-started/installation/) را ببینید یا این را اجرا کنید:

- macOS یا Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## کلیدها

برخی منابع به یک کلید رایگان نیاز دارند: [KEYS.md](KEYS.md) را ببینید.

## بررسی اینکه کار می‌کند

در یک گفت‌وگوی جدید بپرسید: *«Fontes در کدام حوزه‌های قضایی می‌تواند جست‌وجو کند؟»* برنامه باید با
فهرستی از کشورها پاسخ دهد. اگر چنین نکرد، برنامه را یک بار دیگر ببندید و دوباره باز کنید.

## نصب‌کننده تک‌کلیکی (Mac و Windows)

نصب‌کننده Fontes را یک‌جا در همه برنامه‌های شما راه‌اندازی می‌کند: Claude Desktop، Codex، Claude Code،
Cursor، VS Code (GitHub Copilot)، Windsurf، Gemini CLI، Zed، LM Studio و Cline.

**پیش از شروع:** هر یک از این برنامه‌ها را به‌طور کامل ببندید. این برای Claude Code از همه مهم‌تر است:
در حین اجرا، `~/.claude.json` را بازنویسی می‌کند و ممکن است تغییر نصب‌کننده را خنثی کند. اگر نمی‌توانید
Claude Code را ببندید، به جای آن Fontes را با `claude mcp add` به آن اضافه کنید ([Claude Code](#claude-code) را ببینید).

**Mac**

1. نصب‌کننده Mac (`Fontes-Installer-…-mac.zip`) را از
   [آخرین نسخه](https://github.com/ykarapazar/fontes/releases/latest) دریافت کنید و برای از حالت فشرده درآوردن، روی آن دوبار کلیک کنید.
2. روی **Fontes Installer** دوبار کلیک کنید. اگر Mac شما پرسید که آیا برنامه‌ای را که از اینترنت
   دریافت شده باز کند، روی **Open** کلیک کنید.
3. **نصب** را انتخاب کنید و روی **تأیید** کلیک کنید. راه‌اندازی حدود یک دقیقه طول می‌کشد.
4. پیامی برنامه‌هایی را که راه‌اندازی کرده فهرست می‌کند. روی **انجام شد** کلیک کنید، سپس آن برنامه‌ها را
   دوباره باز کنید. برای افزودن کلیدهای رایگان اختیاری پیش از آن، به جای آن روی **افزودن کلیدها** کلیک کنید؛
   [مرحله کلیدها](#مرحله-کلیدها) را ببینید.

**Windows**

1. نصب‌کننده Windows (`Fontes-Setup-….exe`) را از [آخرین نسخه](https://github.com/ykarapazar/fontes/releases/latest) دریافت کنید و روی آن دوبار کلیک کنید.
   - اگر Windows پیام "Windows protected your PC" را نشان داد: روی **More info** و سپس **Run anyway** کلیک کنید.
2. روی **نصب** کلیک کنید. پنجره‌ای باز می‌شود و Fontes را راه‌اندازی می‌کند.
3. وقتی پرسیده شد آیا آمار ناشناس استفاده ارسال شود، برای «نه» Enter را بزنید.
4. می‌پرسد آیا اکنون کلیدها را اضافه کند. برای رد شدن Enter را بزنید؛ [مرحله کلیدها](#مرحله-کلیدها) را ببینید.
5. وقتی **Done** را نشان داد، برنامه‌های هوش مصنوعی خود را دوباره باز کنید. اگر یکی هنوز در حال اجرا بود، آن را
   به‌طور کامل ببندید (از system tray، کنار ساعت، هم) و دوباره باز کنید.

در پایان، نصب‌کننده برنامه‌هایی را که راه‌اندازی کرده فهرست می‌کند.

### برنامه‌هایی که راه‌اندازی می‌کند

نصب‌کننده یک برنامه را فقط در صورتی راه‌اندازی می‌کند که پوشه تنظیمات آن برنامه از قبل روی رایانه شما باشد. Claude Code
فقط در صورتی راه‌اندازی می‌شود که `~/.claude.json` وجود داشته باشد. Claude Desktop همیشه راه‌اندازی می‌شود. هر برنامه
یک مدخل، `fontes`، در این فایل می‌گیرد:

| برنامه | فایل (Mac و Linux) | فایل (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`، و نسخه جداگانه نسخه Microsoft Store |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`، یا در نسخه‌های قدیمی‌تر `~/.codeium/windsurf/mcp_config.json` | `%APPDATA%\devin\mcp_config.json`، یا `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code در صورتی راه‌اندازی می‌شود که `~/.copilot` یا پوشه تنظیمات خود VS Code وجود داشته باشد.

دو برنامه به یک مرحله دیگر نیاز دارند:

- **Windsurf:** پس از باز کردن دوباره، در Cascade دکمه refresh را بزنید.
- **Cline درون افزونه قدیمی‌تر VS Code:** Fontes را به‌صورت دستی اضافه کنید ([Cline](#برنامههای-دیگر) را ببینید).

### مرحله کلیدها

بلافاصله پس از نصب، نصب‌کننده پیشنهاد می‌دهد کلیدهای رایگان فرانسه و ایالات متحده را اضافه کند. برای افزودن یا
تغییر آن‌ها در آینده:

- **Mac:** **Fontes Installer** را دوباره باز کنید و **افزودن یا تغییر کلیدها** را انتخاب کنید.
- **Windows:** منوی Start را باز کنید و سپس **Fontes** ← **افزودن یا تغییر کلیدها** را انتخاب کنید.

آنچه تایپ می‌کنید نمایش داده نمی‌شود. کلیدها به هر برنامه‌ای که از قبل Fontes را دارد اضافه می‌شوند. پس از آن برنامه‌ها را ببندید و دوباره
باز کنید. کلیدها را از کجا بگیرید و چه چیزی را فعال می‌کنند: [KEYS.md](KEYS.md).

### نسخه‌های پشتیبان، اجرای دوباره و حذف

نصب‌کننده فقط مدخل `fontes` را تغییر می‌دهد. هر تنظیم و توضیح (comment) دیگری همان‌طور که بود باقی می‌ماند.
پیش از تغییر یک فایل، یک نسخه از آن را در کنارش با نام `<file>.fontes-backup-<date>` ذخیره می‌کند. نسخه‌هایی
که پس از افزودن کلیدها ساخته شده‌اند آن کلیدها را در خود دارند: آن‌هایی را که دیگر لازم ندارید حذف کنید. همچنین
uv را نصب می‌کند. اجرای دوباره آن بی‌خطر است: راه‌اندازی را ترمیم می‌کند و چیز دیگری را تغییر نمی‌دهد.

برای حذف Fontes، **Fontes Installer** را باز کنید و **حذف** را انتخاب کنید (Mac)، یا
**Fontes** را در Settings ← Apps (Windows) حذف کنید. مدخل `fontes` را، همراه با کلیدها، از همه برنامه‌ها حذف
می‌کند. تنظیمات دیگر شما و نسخه‌های پشتیبان باقی می‌مانند.

## به‌روزرسانی‌ها

- **نصب‌کننده و فایل `.mcpb`:** لازم نیست کاری انجام دهید. روزی یک بار، هنگام شروع برنامه،
  Fontes در پس‌زمینه وجود نسخه جدیدتر را بررسی می‌کند و آن را آماده می‌کند؛ دفعه بعد که
  برنامه شروع شود از آن استفاده می‌کند. اگر یک به‌روزرسانی دریافت نشود یا کار نکند، Fontes همچنان
  از نسخه‌ای که کار می‌کرد استفاده می‌کند.
- **`uvx`:** Fontes وقتی نسخه جدیدتری موجود باشد، در بالای فهرست
  حوزه‌های قضایی به شما اطلاع می‌دهد. برای اینکه همیشه جدیدترین نسخه اجرا شود، به جای `fontes-mcp` از `fontes-mcp@latest` استفاده کنید.

برای این کار هیچ اطلاعاتی درباره شما یا جست‌وجوهایتان به جایی ارسال نمی‌شود.

## حریم خصوصی

Fontes به‌طور پیش‌فرض هیچ چیزی درباره شما یا جست‌وجوهایتان ارسال نمی‌کند. آمار استفاده اختیاری (opt-in) است و یک گزارش
خطا فقط پس از اینکه آن را ببینید و تأیید کنید ارسال می‌شود. جزئیات: [PRIVACY.md](PRIVACY.md).

## حذف

مدخل `fontes` را از تنظیمات MCP برنامه خود حذف کنید (در Claude Code:
`claude mcp remove fontes`)، سپس برنامه را ببندید و دوباره باز کنید.

## خوب است بدانید

Fontes منابع عمومی را می‌خواند که بیشترشان وب‌سایت‌های دادگاه‌ها و دولت‌ها هستند. منابع غیررسمی را در
پاسخ‌هایش مشخص می‌کند. همیشه پیش از تکیه بر یک رأی یا یک ماده، پیوند منبع را باز کنید.

اگر مشکلی پیش آمد، آنچه انجام دادید و خطایی را که دیدید به fontesmcp@proton.me ایمیل کنید.

## پیش از تکیه بر آن

- Fontes یک ابزار پژوهشی است، نه مشاوره حقوقی. استفاده از آن هیچ‌کس را وکیل شما نمی‌کند.
- «همان‌گونه که هست» و بدون هیچ ضمانتی ارائه می‌شود و پدیدآورندگان آن مسئول نحوه استفاده از آن نیستند،
  تا جایی که قانون اجازه می‌دهد. شرایط کامل در [مجوز](../../../LICENSE) (Apache 2.0) آمده است.
