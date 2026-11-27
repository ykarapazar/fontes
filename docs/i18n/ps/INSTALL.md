> دا ژباړه د ماشین په مرسته شوې ده. انګلیسي نسخه معتبره ده.

# د Fontes نصبول

Fontes ستاسو AI اپ ته اجازه ورکوي چې د محکمو فیصلې او قوانین او مقررې په ژوندۍ بڼه د محکمو او حکومتونو
په وېبپاڼو کې، په 125 قضايي حوزو کې ولټوي. هره پایله له اصلي متن سره لینک لري. دا یو معیاري MCP
سرور دی، نو په هر هغه اپ کې کار کوي چې محلي MCP سرور چلولای شي: Claude Desktop، Codex، Claude
Code، Cursor، VS Code (GitHub Copilot)، Gemini CLI، Windsurf، Zed، LM Studio، Cline او نور.

خپل اپ وټاکئ، د هغه ګامونه تعقیب کړئ، بیا [وګورئ چې کار کوي](#وګورئ-چې-کار-کوي).

## Claude Desktop

1. د Fontes `.mcpb` فایل له
   [وروستۍ خپرونې](https://github.com/ykarapazar/fontes/releases/latest) څخه ښکته کړئ.
2. پرې دوه ځله کلیک وکړئ. Claude Desktop یې پرانیزي.
3. پر **Install** کلیک وکړئ.

## Codex

په یوه ترمینل کې:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI او د Codex IDE غځونه (extension) دا تنظیم شریکوي (`~/.codex/config.toml`).
تاسو [uv](#uv-ته-اړتیا-لرئ) ته اړتیا لرئ.

## Claude Code

په یوه ترمینل کې:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

تاسو [uv](#uv-ته-اړتیا-لرئ) ته اړتیا لرئ.

## نور اپونه

هر یو له دې اپونو [uv](#uv-ته-اړتیا-لرئ) ته اړتیا لري. ننوتنه (entry) ور زیاته کړئ، خوندي یې کړئ، بیا اپ وتړئ او بیا یې پرانیزئ.

**Cursor:** په `~/.cursor/mcp.json` (ټولې پروژې) یا `.cursor/mcp.json` (یوه پروژه) کې:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** له Command Palette څخه **MCP: Add Server** وچلوئ، **Command (stdio)**
وټاکئ، `uvx fontes-mcp` ولیکئ او سرور ته د `fontes` نوم ورکړئ. یا دا
`~/.copilot/mcp-config.json` ته ور زیات کړئ:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

د VS Code زاړه تنظیمات `.vscode/mcp.json` کاروي، چېرې چې د پورتنۍ کچې کیلي د `mcpServers` پر ځای `servers` ده.

**Gemini CLI:** په یوه ترمینل کې، `gemini mcp add -s user fontes uvx fontes-mcp`. یا دا
`~/.gemini/settings.json` ته ور زیات کړئ:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** د تنظیماتو فایل پرانیزئ (**zed: open settings file**) او دا ور زیات کړئ:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** په ښي اړخ (sidebar) کې **Program** ټب پرانیزئ، پر **Install → Edit
mcp.json** کلیک وکړئ، او دا ور زیات کړئ:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** پر **MCP Servers** آیکون کلیک وکړئ، **Configure** ټب پرانیزئ، پر **Configure MCP
Servers** کلیک وکړئ، او همغه `mcpServers` ننوتنه ور زیاته کړئ چې د LM Studio لپاره ده.

**Claude Desktop، په لاس** (د `.mcpb` فایل پر ځای): همغه `mcpServers` ننوتنه
`claude_desktop_config.json` ته ور زیاته کړئ (macOS: `~/Library/Application Support/Claude/`، Windows:
`%APPDATA%\Claude\`).

**هر بل MCP اپ** (Windsurf او نور): د هغه خپل اسناد وايي چې خپل MCP
سرورونه چېرته ساتي. ډېری یې همغه ننوتنه مني: کمانډ `uvx`، دلیل (argument) `fontes-mcp`.

که اپ `uvx` ونه موندلای شي، د هغه بشپړه لاره (path) وکاروئ (په macOS او Linux کې، `which uvx` یې چاپوي).

## uv ته اړتیا لرئ

Codex، Claude Code او نور اپونه Fontes د `uvx` په واسطه پیلوي، چې له **uv** سره راځي، چې د Astral یوه کوچنۍ
وړیا وسیله ده. د نصبولو لپاره یې،
[د Astral لارښود](https://docs.astral.sh/uv/getting-started/installation/) وګورئ، یا دا وچلوئ:

- macOS یا Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## کیلي

ځینې سرچینې یوې وړیا کیلي ته اړتیا لري: [KEYS.md](KEYS.md) وګورئ.

## وګورئ چې کار کوي

په یوه نوې چټ کې وپوښتئ: *«Fontes په کومو قضايي حوزو کې لټون کولای شي؟»* اپ باید د
هېوادونو له لېست سره ځواب ورکړي. که داسې ونه شي، اپ یو ځل بیا وتړئ او بیا یې پرانیزئ.

## یو کلیک نصبوونکی (Mac او Windows)

نصبوونکی Fontes ستاسو په ټولو اپونو کې په یو ځل جوړوي: Claude Desktop، Codex، Claude Code، Cursor،
VS Code (GitHub Copilot)، Windsurf، Gemini CLI، Zed، LM Studio او Cline.

**مخکې له دې چې پیل وکړئ:** هر یو له دې اپونو په بشپړه توګه وتړئ. دا د Claude Code لپاره تر ټولو مهم دی:
کله چې چلېږي، `~/.claude.json` بیا لیکي او کولای شي د نصبوونکي بدلون بېرته وګرځوي. که تاسو
Claude Code نشئ تړلای، نو پر ځای یې Fontes د `claude mcp add` په واسطه ور زیات کړئ ([Claude Code](#claude-code) وګورئ).

**Mac**

1. د Mac نصبوونکی (`Fontes-Installer-…-mac.zip`) له [وروستۍ خپرونې](https://github.com/ykarapazar/fontes/releases/latest)
   څخه ښکته کړئ او د zip څخه د ایستلو لپاره پرې دوه ځله کلیک وکړئ.
2. پر **Fontes Installer** دوه ځله کلیک وکړئ. که ستاسو Mac وپوښتي چې ایا له انټرنېټ څخه ښکته شوی اپ
   پرانیزي، پر **Open** کلیک وکړئ.
3. **نصب** وټاکئ او پر **سمه ده** کلیک وکړئ. جوړول شاوخوا یوه دقیقه وخت نیسي.
4. یو پیغام هغه اپونه لېست کوي چې جوړ یې کړي. پر **ترسره شو** کلیک وکړئ، بیا هغه اپونه بیا پرانیزئ. که
   غواړئ لومړی اختیاري وړیا کیلي ور زیاتې کړئ، پر ځای یې پر **کیلي ور زیاتې کړئ** کلیک وکړئ؛
   [د کیلي ګام](#د-کیلي-ګام) وګورئ.

**Windows**

1. د Windows نصبوونکی (`Fontes-Setup-….exe`) له [وروستۍ خپرونې](https://github.com/ykarapazar/fontes/releases/latest) څخه ښکته کړئ او پرې دوه ځله کلیک وکړئ.
   - که Windows "Windows protected your PC" وښيي: پر **More info** کلیک وکړئ، بیا پر **Run anyway**.
2. پر **نصب** کلیک وکړئ. یوه کړکۍ پرانیزي او Fontes جوړوي.
3. کله چې وپوښتل شي چې ایا بې نومه د کارونې شمېرې ولېږي، د نه لپاره Enter کېکاږئ.
4. پوښتي چې ایا اوس کیلي ور زیاتې کړي. د تېرېدو لپاره Enter کېکاږئ؛ [د کیلي ګام](#د-کیلي-ګام) وګورئ.
5. کله چې **Done** ووايي، خپل AI اپونه بیا پرانیزئ. که یو یې لا چلېده، هغه په بشپړه توګه وتړئ
   (د system tray څخه هم، د ساعت تر څنګ) او بیا یې پرانیزئ.

په پای کې نصبوونکی هغه اپونه لېست کوي چې جوړ یې کړي.

### کوم اپونه جوړوي

دا یو اپ یوازې هغه وخت جوړوي چې د هغه اپ د تنظیماتو فولډر لا دمخه ستاسو په کمپیوټر کې وي. Claude Code
یوازې هغه وخت جوړېږي چې `~/.claude.json` شتون ولري. Claude Desktop تل جوړېږي. هر اپ په دې فایل کې یوه
ننوتنه، `fontes`، ترلاسه کوي:

| اپ | فایل (Mac او Linux) | فایل (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`، او د Microsoft Store د نسخې خپله کاپي |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`، یا په زړو نسخو کې `~/.codeium/windsurf/mcp_config.json` | `%APPDATA%\devin\mcp_config.json`، یا `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code هغه وخت جوړېږي چې `~/.copilot` یا د VS Code د خپلو تنظیماتو فولډر شتون ولري.

دوه اپونه یو بل ګام ته اړتیا لري:

- **Windsurf:** له بیا پرانیستلو وروسته، په Cascade کې refresh کېکاږئ.
- **Cline د VS Code په زاړه غځونه (extension) کې:** Fontes په لاس ور زیات کړئ ([Cline](#نور-اپونه) وګورئ).

### د کیلي ګام

سمدستي له نصبولو وروسته، نصبوونکی وړاندیز کوي چې د فرانسې او امریکا وړیا کیلي ور زیاتې کړي. د دې لپاره چې
وروسته یې ور زیاتې یا بدلې کړئ:

- **Mac:** **Fontes Installer** بیا پرانیزئ او **کیلي ور زیاتې یا بدلې کړئ** وټاکئ.
- **Windows:** د Start menu خلاص کړئ، بیا **Fontes** → **کیلي ور زیاتې یا بدلې کړئ** وټاکئ.

لیکل پټ وي. کیلي هر هغه اپ ته ځي چې لا دمخه Fontes لري. وروسته اپونه وتړئ او
بیا یې پرانیزئ. کیلي له کومه ترلاسه کړئ او څه پرانیزي: [KEYS.md](KEYS.md).

### بیک اپ، بیا چلول او لرې کول

نصبوونکی یوازې د `fontes` ننوتنه بدلوي. هر بل تنظیم او تبصره (comment) لکه څنګه چې وه پاتې کېږي.
مخکې له دې چې یو فایل بدل کړي، د هغه تر څنګ یوه کاپي خوندي کوي، چې نوم یې `<file>.fontes-backup-<date>` دی. هغه کاپي
چې تاسو له کیلي ور زیاتولو وروسته جوړې شوې، هغه کیلي لري: هغه یې ړنګې کړئ چې نور ورته اړتیا نه لرئ. دا
uv هم نصبوي. د بیا چلولو کې هېڅ ستونزه نشته: تنظیم سموي او بل هېڅ شی نه بدلوي.

د Fontes د لرې کولو لپاره، **Fontes Installer** پرانیزئ او **لرې کول** وټاکئ (Mac)، یا **Fontes** په Settings → Apps کې ولرې کړئ (Windows). دا د `fontes` ننوتنه، له کیلي سره، له هر اپ څخه لرې کوي. ستاسو نور تنظیمات
او بیک اپ کاپي پاتې کېږي.

## تازه کېدنې

- **نصبوونکی او `.mcpb` فایل:** تاسو هېڅ کار ته اړتیا نه لرئ. په ورځ کې یو ځل، کله چې اپ
  پیلېږي، Fontes په شاليد (background) کې د نوې نسخې لپاره ګوري او چمتو کوي یې؛ بل ځل چې
  اپ پیل شي، هغه کاروي. که تازه کېدنه ښکته نشي یا کار ونه کړي، Fontes
  همغه نسخه کاروي چې کار یې کاوه.
- **`uvx`:** Fontes تاسو ته وايي کله چې نوې نسخه شتون ولري، د خپل د قضايي حوزو د لېست په سر کې.
  د دې لپاره چې تل تر ټولو نوې نسخه وچلوئ، د `fontes-mcp` پر ځای `fontes-mcp@latest` وکاروئ.

د دې لپاره ستاسو یا ستاسو د لټونونو په اړه هېڅ معلومات چېرته نه لېږل کېږي.

## محرمیت

Fontes په ډیفالټ ډول ستاسو یا ستاسو د لټونونو په اړه هېڅ شی نه لېږي. د کارونې شمېرې اختیاري (opt-in) دي، او د تېروتنې
راپور یوازې هغه وخت لېږل کېږي چې تاسو یې وګورئ او تایید یې کړئ. جزئیات: [PRIVACY.md](PRIVACY.md).

## لرې کول

د خپل اپ له MCP تنظیماتو څخه د `fontes` ننوتنه لرې کړئ (په Claude Code کې:
`claude mcp remove fontes`)، بیا اپ وتړئ او بیا یې پرانیزئ.

## د پوهېدو وړ

Fontes عامه سرچینې لولي، ډېری یې د محکمو او حکومتونو وېبپاڼې. غیر رسمي سرچینې په خپلو
ځوابونو کې په نښه کوي. مخکې له دې چې پر یوې فیصلې یا مادې تکیه وکړئ، تل د سرچینې لینک پرانیزئ.

که څه غلط شول، هغه څه چې تاسو کړي او هغه تېروتنه چې مو لیدلې fontesmcp@proton.me ته برېښنالیک کړئ.

## مخکې له دې چې تکیه پرې وکړئ

- Fontes یوه څېړنیزه وسیله ده، نه حقوقي مشوره. کارول یې هېڅوک ستاسو وکیل نه جوړوي.
- دا «لکه څنګه چې دی» (as is)، پرته له هر ډول تضمینه وړاندې کېږي، او جوړوونکي یې د هغه د کارونې د څرنګوالي مسؤل نه دي،
  تر هغه ځایه چې قانون اجازه ورکوي. بشپړ شرطونه په [جواز](../../../LICENSE) (Apache 2.0) کې دي.
