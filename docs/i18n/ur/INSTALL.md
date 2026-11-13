> یہ مشین کی مدد سے کیا گیا ترجمہ ہے۔ انگریزی ورژن ہی مستند ہے۔

# Fontes انسٹال کریں

Fontes آپ کی AI ایپ کو 120 سے زیادہ جورسڈکشنز میں عدالتی اور حکومتی ویب سائٹس پر عدالتی فیصلے اور
قانون سازی براہِ راست تلاش کرنے دیتا ہے۔ ہر نتیجہ اصل سے لنک ہوتا ہے۔ یہ ایک معیاری MCP سرور ہے،
اس لیے یہ ہر اس ایپ میں کام کرتا ہے جو مقامی MCP سرور چلا سکتی ہو: Claude Desktop، Codex، Claude
Code، Cursor، VS Code (GitHub Copilot)، Gemini CLI، Windsurf، Zed، LM Studio، Cline اور دیگر۔

اپنی ایپ منتخب کریں، اس کے مراحل پر عمل کریں، پھر [چیک کریں کہ یہ کام کرتا ہے](#چیک-کریں-کہ-یہ-کام-کرتا-ہے)۔

## Claude Desktop

1. Fontes کی `.mcpb` فائل
   [تازہ ترین ریلیز](https://github.com/ykarapazar/fontes/releases/latest) سے ڈاؤن لوڈ کریں۔
2. اس پر ڈبل کلک کریں۔ Claude Desktop اسے کھول دیتا ہے۔
3. **Install** پر کلک کریں۔

## Codex

ٹرمینل میں:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI اور Codex IDE ایکسٹینشن یہ سیٹنگ مشترک استعمال کرتے ہیں (`~/.codex/config.toml`)۔
[uv](#آپ-کو-uv-کی-ضرورت-ہے) درکار ہے۔

## Claude Code

ٹرمینل میں:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

[uv](#آپ-کو-uv-کی-ضرورت-ہے) درکار ہے۔

## دیگر ایپس

ان سب کو [uv](#آپ-کو-uv-کی-ضرورت-ہے) درکار ہے۔ اندراج شامل کریں، محفوظ کریں، پھر ایپ کو بند کر کے دوبارہ کھولیں۔

**Cursor:** `~/.cursor/mcp.json` (تمام پروجیکٹس) یا `.cursor/mcp.json` (ایک پروجیکٹ) میں:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** Command Palette سے **MCP: Add Server** چلائیں،
**Command (stdio)** منتخب کریں، `uvx fontes-mcp` درج کریں اور سرور کا نام `fontes` رکھیں۔ یا یہ
`~/.copilot/mcp-config.json` میں شامل کریں:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

VS Code کے پرانے سیٹ اپ `.vscode/mcp.json` استعمال کرتے ہیں، جس میں سب سے اوپر کی key
`mcpServers` کے بجائے `servers` ہوتی ہے۔

**Gemini CLI:** ٹرمینل میں، `gemini mcp add -s user fontes uvx fontes-mcp`۔ یا یہ
`~/.gemini/settings.json` میں شامل کریں:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** اپنی سیٹنگز فائل کھولیں (**zed: open settings file**) اور یہ شامل کریں:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** دائیں سائیڈبار میں **Program** ٹیب کھولیں، **Install → Edit
mcp.json** پر کلک کریں اور یہ شامل کریں:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** **MCP Servers** آئیکن پر کلک کریں، **Configure** ٹیب کھولیں، **Configure MCP
Servers** پر کلک کریں اور LM Studio والا وہی `mcpServers` اندراج شامل کریں۔

**Claude Desktop، ہاتھ سے** (`.mcpb` فائل کے بجائے): وہی `mcpServers` اندراج
`claude_desktop_config.json` میں شامل کریں (macOS: `~/Library/Application Support/Claude/`، Windows:
`%APPDATA%\Claude\`)۔

**کوئی بھی دوسری MCP ایپ** (Windsurf اور دیگر): اس ایپ کی اپنی دستاویزات بتاتی ہیں کہ وہ MCP سرورز
کہاں رکھتی ہے۔ زیادہ تر یہی اندراج قبول کرتی ہیں: کمانڈ `uvx`، آرگیومنٹ `fontes`۔

اگر ایپ کو `uvx` نہ ملے، تو اس کا مکمل پاتھ استعمال کریں (macOS اور Linux پر، `which uvx` اسے پرنٹ کرتا ہے)۔

## آپ کو uv کی ضرورت ہے

Codex، Claude Code اور دیگر ایپس Fontes کو `uvx` کے ذریعے چلاتی ہیں، جو **uv** کے ساتھ آتا ہے، Astral کا
ایک چھوٹا مفت ٹول۔ اسے انسٹال کرنے کے لیے،
[Astral کی گائیڈ](https://docs.astral.sh/uv/getting-started/installation/) دیکھیں، یا یہ چلائیں:

- macOS یا Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## کیز

کچھ ذرائع کو ایک مفت کی (key) درکار ہے: [KEYS.md](KEYS.md) دیکھیں۔

## چیک کریں کہ یہ کام کرتا ہے

ایک نئی گفتگو میں پوچھیں: *"Fontes کن جورسڈکشنز میں تلاش کر سکتا ہے؟"* ایپ کو
ممالک کی فہرست کے ساتھ جواب دینا چاہیے۔ اگر ایسا نہ ہو، تو ایپ کو ایک بار پھر بند کر کے دوبارہ کھولیں۔

## ون کلک انسٹالر (جلد آ رہا ہے)

Mac اور Windows کے لیے ایک انسٹالر آنے والا ہے جو Fontes کو آپ کی تمام ایپس میں ایک ہی بار میں سیٹ اپ کرتا ہے۔
یہ Claude Desktop، Codex، Claude Code، Cursor، VS Code (GitHub Copilot)، Windsurf، Gemini CLI،
Zed، LM Studio اور Cline کو سیٹ اپ کرتا ہے۔ جب یہ آ جائے:

**شروع کرنے سے پہلے:** ان میں سے ہر ایپ کو مکمل طور پر بند کر دیں۔ یہ Claude Code کے لیے سب سے زیادہ اہم ہے:
چلتے ہوئے یہ `~/.claude.json` کو دوبارہ لکھتا ہے اور انسٹالر کی تبدیلی کو ختم کر سکتا ہے۔ اگر آپ
Claude Code کو بند نہیں کر سکتے، تو اس کے بجائے Fontes کو اس میں `claude mcp add` کے ذریعے شامل کریں ([Claude Code](#claude-code) دیکھیں)۔

**Mac**

1. ڈاؤن لوڈ کیا ہوا **Fontes Installer** فولڈر کھولیں۔
2. **Install Fontes.command** پر ڈبل کلک کریں۔
   - اگر آپ کا Mac کہے "cannot be opened because it is from an unidentified developer"
     (نہیں کھل سکتی کیونکہ یہ ایک نامعلوم ڈویلپر کی ہے): فائل پر رائٹ کلک (یا Control-کلک) کریں، **Open** منتخب کریں، پھر دوبارہ **Open**۔ آپ یہ صرف
     ایک بار کرتے ہیں۔
3. ایک ونڈو کھلتی ہے اور پوچھتی ہے کہ آیا گمنام استعمال کے اعداد و شمار بھیجے جائیں؛ "نہیں" کے لیے Enter دبائیں۔
4. یہ پوچھتا ہے کہ آیا ابھی کیز شامل کی جائیں۔ چھوڑنے کے لیے Enter دبائیں؛ [کیز کا مرحلہ](#کیز-کا-مرحلہ) دیکھیں۔
5. جب یہ **Done** دکھائے، تو اپنی AI ایپس دوبارہ کھولیں۔

**Windows**

1. ڈاؤن لوڈ کیے ہوئے **Fontes Installer** کو unzip کریں (رائٹ کلک ← Extract All)۔
2. **Install Fontes.cmd** پر ڈبل کلک کریں۔
   - اگر Windows دکھائے "Windows protected your PC": **More info** پر، پھر **Run anyway** پر کلک کریں۔
3. جب پوچھا جائے کہ آیا گمنام استعمال کے اعداد و شمار بھیجے جائیں، تو "نہیں" کے لیے Enter دبائیں۔
4. یہ پوچھتا ہے کہ آیا ابھی کیز شامل کی جائیں۔ چھوڑنے کے لیے Enter دبائیں؛ [کیز کا مرحلہ](#کیز-کا-مرحلہ) دیکھیں۔
5. جب یہ **Done** دکھائے، تو اپنی AI ایپس دوبارہ کھولیں۔ اگر کوئی ابھی بھی چل رہی تھی، تو اسے
   مکمل طور پر بند کریں (system tray سے بھی، گھڑی کے پاس) اور دوبارہ کھولیں۔

آخر میں، انسٹالر ان ایپس کی فہرست دکھاتا ہے جنہیں اس نے سیٹ اپ کیا۔

### یہ کن ایپس کو سیٹ اپ کرتا ہے

انسٹالر کسی ایپ کو صرف اس صورت میں سیٹ اپ کرتا ہے جب اس ایپ کا سیٹنگز فولڈر پہلے سے آپ کے کمپیوٹر پر موجود ہو۔ Claude Code
صرف اس صورت میں سیٹ اپ ہوتا ہے جب `~/.claude.json` موجود ہو۔ Claude Desktop ہمیشہ سیٹ اپ ہوتا ہے۔ ہر ایپ
کو اس فائل میں ایک اندراج، `fontes`، ملتا ہے:

| ایپ | فائل (Mac اور Linux) | فائل (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`، اور Microsoft Store ورژن کی الگ کاپی |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`، یا پرانے ورژنز پر `~/.codeium/windsurf/mcp_config.json` | `%APPDATA%\devin\mcp_config.json`، یا `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code اس صورت میں سیٹ اپ ہوتا ہے جب `~/.copilot` یا VS Code کا اپنا سیٹنگز فولڈر موجود ہو۔

دو ایپس کو ایک اور قدم درکار ہے:

- **Windsurf:** دوبارہ کھولنے کے بعد، Cascade میں refresh بٹن دبائیں۔
- **پرانی VS Code ایکسٹینشن کے اندر Cline:** Fontes کو ہاتھ سے شامل کریں ([Cline](#دیگر-ایپس) دیکھیں)۔

### کیز کا مرحلہ

انسٹال کرنے کے فوراً بعد، انسٹالر فرانس اور امریکہ کی مفت کیز شامل کرنے کی پیشکش کرتا ہے۔ انہیں بعد میں
شامل کرنے یا تبدیل کرنے کے لیے:

- **Mac:** انسٹالر فولڈر میں **Add or change keys.command** پر ڈبل کلک کریں، یا
  Fontes Installer ایپ دوبارہ کھولیں اور **Add or change keys** منتخب کریں۔
- **Windows:** انسٹالر فولڈر میں **Add or change keys.cmd** پر ڈبل کلک کریں۔

ٹائپنگ چھپی رہتی ہے۔ کیز ہر اس ایپ میں جاتی ہیں جس میں پہلے سے Fontes موجود ہو۔ اس کے بعد ایپس کو بند کر کے دوبارہ
کھولیں۔ کیز کہاں سے حاصل کریں اور وہ کیا کھولتی ہیں: [KEYS.md](KEYS.md)۔

### بیک اپ، دوبارہ چلانا اور ان انسٹال

انسٹالر صرف `fontes` اندراج کو تبدیل کرتا ہے۔ باقی ہر سیٹنگ اور تبصرہ (comment) جوں کا توں رہتا ہے۔
کسی فائل کو تبدیل کرنے سے پہلے، یہ اس کی ایک کاپی اس کے ساتھ `<file>.fontes-backup-<date>` کے نام سے محفوظ کرتا ہے۔ جو کاپیاں
کیز شامل کرنے کے بعد بنی ہوں ان میں وہ کیز موجود ہوتی ہیں: جن کی آپ کو مزید ضرورت نہیں انہیں حذف کر دیں۔ یہ
uv بھی انسٹال کرتا ہے۔ اسے دوبارہ چلانا محفوظ ہے: یہ سیٹ اپ کی مرمت کرتا ہے اور کچھ اور تبدیل نہیں کرتا۔

Fontes کو ہٹانے کے لیے، **Uninstall Fontes.command** (Mac) یا **Uninstall Fontes.cmd**
(Windows) پر ڈبل کلک کریں۔ یہ تمام ایپس سے `fontes` اندراج، کیز سمیت، ہٹا دیتا ہے۔ آپ کی باقی سیٹنگز
اور بیک اپ کاپیاں برقرار رہتی ہیں۔

## اپ ڈیٹس

- **انسٹالر اور `.mcpb` فائل:** آپ کو کچھ کرنے کی ضرورت نہیں۔ دن میں ایک بار، جب ایپ شروع ہوتی ہے،
  Fontes پس منظر میں نئے ورژن کی جانچ کرتا ہے اور اسے تیار کر لیتا ہے؛ اگلی بار جب
  ایپ شروع ہو تو وہ اسے استعمال کرتی ہے۔ اگر کوئی اپ ڈیٹ ڈاؤن لوڈ نہ ہو یا کام نہ کرے، تو Fontes وہی
  ورژن استعمال کرتا رہتا ہے جو کام کر رہا تھا۔
- **`uvx`:** جب نیا ورژن دستیاب ہو تو Fontes آپ کو جورسڈکشنز کی فہرست کے
  اوپر بتاتا ہے۔ ہمیشہ تازہ ترین ورژن چلانے کے لیے، `fontes-mcp` کے بجائے `fontes-mcp@latest` استعمال کریں۔

اس کے لیے آپ یا آپ کی تلاشوں کے بارے میں کوئی معلومات کہیں نہیں بھیجی جاتیں۔

## پرائیویسی

Fontes بطورِ ڈیفالٹ آپ یا آپ کی تلاشوں کے بارے میں کچھ نہیں بھیجتا۔ استعمال کے اعداد و شمار opt-in ہیں، اور بگ
رپورٹ صرف اس وقت بھیجی جاتی ہے جب آپ اسے دیکھ کر تصدیق کر دیں۔ تفصیلات: [PRIVACY.md](PRIVACY.md)۔

## ہٹانا

اپنی ایپ کی MCP سیٹنگز سے `fontes` اندراج حذف کریں (Claude Code میں:
`claude mcp remove fontes`)، پھر ایپ کو بند کر کے دوبارہ کھولیں۔

## جاننا مفید ہے

Fontes عوامی ذرائع پڑھتا ہے، جن میں سے زیادہ تر عدالتی اور حکومتی ویب سائٹس ہیں۔ یہ اپنے جوابات میں غیر سرکاری ذرائع
کی نشاندہی کرتا ہے۔ کسی فیصلے یا شق پر انحصار کرنے سے پہلے ہمیشہ ماخذ کا لنک کھولیں۔

اگر کچھ غلط ہو جائے، تو آپ نے جو کیا اور جو ایرر دیکھا، وہ fontesmcp@proton.me پر ای میل کریں۔

## انحصار کرنے سے پہلے

- Fontes ایک تحقیقی ٹول ہے، قانونی مشورہ نہیں۔ اس کا استعمال کسی کو آپ کا وکیل نہیں بناتا۔
- یہ "جیسا ہے" کی بنیاد پر، کسی وارنٹی کے بغیر فراہم کیا جاتا ہے، اور اس کے مصنفین اس کے استعمال کے طریقے کے ذمہ دار نہیں،
  جہاں تک قانون اجازت دے۔ مکمل شرائط [LICENSE](../../../LICENSE) (Apache 2.0) میں ہیں۔
