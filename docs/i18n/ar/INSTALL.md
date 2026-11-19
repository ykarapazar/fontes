> هذه ترجمة أُعدّت بمساعدة الآلة. النسخة الإنجليزية هي النسخة المعتمدة.

# تثبيت Fontes

يتيح Fontes لتطبيق الذكاء الاصطناعي الذي تستخدمه البحث في الأحكام القضائية والتشريعات مباشرةً على
المواقع الإلكترونية للمحاكم والحكومات في أكثر من 120 ولاية قضائية. كل نتيجة تتضمن رابطًا إلى الأصل.
وهو خادم MCP قياسي، لذا يعمل في أي تطبيق يستطيع تشغيل خادم MCP محلي: Claude Desktop وCodex
وClaude Code وCursor وVS Code (GitHub Copilot) وGemini CLI وWindsurf وZed وLM Studio وCline وغيرها.

اختر تطبيقك، واتبع خطواته، ثم [تحقّق من أنه يعمل](#التحقق-من-أنه-يعمل).

## Claude Desktop

1. نزّل ملف Fontes بصيغة `.mcpb` من
   [أحدث إصدار](https://github.com/ykarapazar/fontes/releases/latest).
2. انقر عليه نقرًا مزدوجًا. يفتحه Claude Desktop.
3. انقر **Install**.

## Codex

في نافذة الطرفية:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

تتشارك Codex CLI وإضافة Codex لبيئة التطوير (IDE) هذا الإعداد (`~/.codex/config.toml`).
تحتاج إلى [uv](#تحتاج-إلى-uv).

## Claude Code

في نافذة الطرفية:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

تحتاج إلى [uv](#تحتاج-إلى-uv).

## تطبيقات أخرى

يحتاج كلٌّ من هذه التطبيقات إلى [uv](#تحتاج-إلى-uv). أضِف الإدخال، واحفظ، ثم أغلق التطبيق وأعِد فتحه.

**Cursor:** في `~/.cursor/mcp.json` (جميع المشاريع) أو `.cursor/mcp.json` (مشروع واحد):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** شغّل **MCP: Add Server** من لوحة الأوامر (Command Palette)، واختر
**Command (stdio)**، وأدخل `uvx fontes-mcp` وسمِّ الخادم `fontes`. أو أضِف هذا إلى
`~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

تستخدم إعدادات VS Code الأقدم `.vscode/mcp.json`، حيث يكون المفتاح الأعلى مستوى `servers` بدلًا من
`mcpServers`.

**Gemini CLI:** في نافذة الطرفية، `gemini mcp add -s user fontes uvx fontes-mcp`. أو أضِف هذا إلى
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** افتح ملف الإعدادات (**zed: open settings file**) وأضِف:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** في الشريط الجانبي الأيمن، افتح علامة التبويب **Program**، وانقر **Install → Edit
mcp.json**، وأضِف:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** انقر أيقونة **MCP Servers**، وافتح علامة التبويب **Configure**، وانقر **Configure MCP
Servers**، وأضِف إدخال `mcpServers` نفسه كما في LM Studio.

**Claude Desktop، يدويًا** (بدلًا من ملف `.mcpb`): أضِف إدخال `mcpServers` نفسه إلى
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`، Windows:
`%APPDATA%\Claude\`).

**أي تطبيق MCP آخر** (Windsurf وغيره): توثيقه الخاص يبيّن أين يحفظ خوادم MCP
الخاصة به. يقبل معظمها الإدخال نفسه: الأمر `uvx`، والوسيط `fontes`.

إذا لم يعثر التطبيق على `uvx`، فاستخدم مساره الكامل (على macOS وLinux، يطبعه `which uvx`).

## تحتاج إلى uv

يشغّل Codex وClaude Code والتطبيقات الأخرى Fontes باستخدام `uvx`، الذي يأتي مع **uv**، وهي أداة صغيرة
مجانية من Astral. لتثبيتها، راجع
[دليل Astral](https://docs.astral.sh/uv/getting-started/installation/)، أو شغّل:

- macOS أو Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## المفاتيح

بعض المصادر تحتاج إلى مفتاح مجاني: راجع [KEYS.md](KEYS.md).

## التحقق من أنه يعمل

في محادثة جديدة، اسأل: *"ما الولايات القضائية التي يستطيع Fontes البحث فيها؟"* ينبغي أن يجيب التطبيق
بقائمة من الدول. إذا لم يفعل، فأغلق التطبيق وأعِد فتحه مرة أخرى.

## أداة التثبيت بنقرة واحدة (Mac وWindows)

تُعدّ أداة التثبيت برنامج Fontes في جميع تطبيقاتك دفعة واحدة: Claude Desktop وCodex وClaude Code
وCursor وVS Code (GitHub Copilot) وWindsurf وGemini CLI وZed وLM Studio وCline.

**قبل أن تبدأ:** أغلق كل تطبيق من هذه التطبيقات تمامًا. هذا مهم أكثر ما يكون مع Claude Code:
فأثناء تشغيله، يعيد كتابة `~/.claude.json` وقد يُلغي التغيير الذي أجرته أداة التثبيت. إذا لم تستطع
إغلاق Claude Code، فأضِف Fontes إليه بـ `claude mcp add` بدلًا من ذلك (راجع [Claude Code](#claude-code)).

**Mac**

1. نزّل أداة التثبيت لنظام Mac (`Fontes-Installer-…-mac.zip`) من
   [أحدث إصدار](https://github.com/ykarapazar/fontes/releases/latest) وانقر عليها نقرًا مزدوجًا لفك ضغطها.
2. انقر نقرًا مزدوجًا على **Fontes Installer**. إذا سألك جهاز Mac هل تريد فتح تطبيق نُزّل من
   الإنترنت، فانقر **فتح**.
3. اختر **تثبيت** وانقر **موافق**. يستغرق الإعداد نحو دقيقة.
4. تظهر رسالة تسرد التطبيقات التي أعدّتها. انقر **تم**، ثم افتح تلك التطبيقات من جديد. لإضافة
   المفاتيح المجانية الاختيارية أولًا، انقر **إضافة المفاتيح** بدلًا من ذلك؛ راجع [خطوة المفاتيح](#خطوة-المفاتيح).

**Windows**

1. نزّل أداة التثبيت لنظام Windows (`Fontes-Setup-….exe`) من [أحدث إصدار](https://github.com/ykarapazar/fontes/releases/latest) وانقر عليها نقرًا مزدوجًا.
   - إذا عرض Windows "Windows protected your PC": انقر **More info**، ثم **Run anyway**.
2. انقر **تثبيت**. تفتح نافذة وتُعدّ Fontes.
3. عندما تُسأل هل تريد إرسال أعداد استخدام مجهولة الهوية، اضغط Enter للرفض.
4. تسألك هل تريد إضافة المفاتيح الآن. اضغط Enter للتخطي؛ راجع [خطوة المفاتيح](#خطوة-المفاتيح).
5. عندما تظهر **Done**، افتح تطبيقات الذكاء الاصطناعي من جديد. إذا كان أحدها لا يزال يعمل، فأغلقه
   تمامًا (من علبة النظام أيضًا، قرب الساعة) ثم افتحه من جديد.

في النهاية تسرد أداة التثبيت التطبيقات التي أعدّتها.

### التطبيقات التي تعدها

لا تُعدّ أداة التثبيت تطبيقًا إلا إذا كان مجلد إعداداته موجودًا مسبقًا على حاسوبك. لا يُعدّ Claude Code
إلا إذا كان `~/.claude.json` موجودًا. أما Claude Desktop فيُعدّ دائمًا. يحصل كل تطبيق على إدخال
واحد، `fontes`، في هذا الملف:

| التطبيق | الملف (Mac وLinux) | الملف (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`، والنسخة الخاصة بإصدار Microsoft Store |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`، أو `~/.codeium/windsurf/mcp_config.json` في الإصدارات الأقدم | `%APPDATA%\devin\mcp_config.json`، أو `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

يُعدّ VS Code إذا كان `~/.copilot` أو مجلد إعدادات VS Code نفسه موجودًا.

يحتاج تطبيقان إلى خطوة إضافية:

- **Windsurf:** بعد إعادة فتحه، اضغط زر التحديث (refresh) في Cascade.
- **Cline داخل إضافة VS Code الأقدم:** أضِف Fontes يدويًا (راجع [Cline](#تطبيقات-أخرى)).

### خطوة المفاتيح

بعد التثبيت مباشرةً، تعرض أداة التثبيت إضافة مفتاحَي فرنسا والولايات المتحدة المجانيين. لإضافتهما أو
تغييرهما لاحقًا:

- **Mac:** افتح **Fontes Installer** مرة أخرى واختر **إضافة المفاتيح أو تغييرها**.
- **Windows:** افتح قائمة ابدأ، ثم **Fontes** ← **إضافة المفاتيح أو تغييرها**.

لا تظهر الكتابة. تُضاف المفاتيح إلى كل تطبيق يحتوي على Fontes مسبقًا. أغلق التطبيقات وأعِد فتحها
بعد ذلك. من أين تحصل على المفاتيح وما الذي تتيحه: [KEYS.md](KEYS.md).

### النسخ الاحتياطية وإعادة التشغيل والإزالة

لا تغيّر أداة التثبيت إلا إدخال `fontes`. يبقى كل إعداد آخر وكل تعليق كما هو.
قبل أن تغيّر ملفًا، تحفظ نسخة منه بجانبه، باسم `<file>.fontes-backup-<date>`. النسخ
التي تُنشأ بعد إضافتك المفاتيح تحتوي على تلك المفاتيح: احذف ما لم تعد تحتاج إليه منها. كما أنها
تثبّت uv. إعادة تشغيلها آمنة: فهي تُصلح الإعداد ولا تغيّر شيئًا آخر.

لإزالة Fontes، افتح **Fontes Installer** واختر **إزالة** (Mac)، أو ألغِ تثبيت **Fontes** من الإعدادات ← التطبيقات (Windows). تُزيل إدخال `fontes`، بما في ذلك المفاتيح، من كل تطبيق. تبقى إعداداتك الأخرى
والنسخ الاحتياطية.

## التحديثات

- **أداة التثبيت وملف `.mcpb`:** لا تحتاج إلى فعل أي شيء. مرة واحدة يوميًا، عند بدء
  التطبيق، يتحقق Fontes في الخلفية من وجود إصدار أحدث ويجهّزه؛ وفي المرة التالية التي يبدأ فيها
  التطبيق يستخدمه. إذا تعذّر تنزيل التحديث أو لم يعمل، يواصل Fontes
  استخدام الإصدار الذي كان يعمل.
- **`uvx`:** يُعلمك Fontes عند توفر إصدار أحدث، في أعلى قائمة
  الولايات القضائية. لتشغيل أحدث إصدار دائمًا، استخدم `fontes-mcp@latest` بدلًا من `fontes-mcp`.

لا تُرسَل لهذا الغرض أي معلومات عنك أو عن عمليات بحثك إلى أي جهة.

## الخصوصية

لا يرسل Fontes افتراضيًا أي شيء عنك أو عن عمليات بحثك. أعداد الاستخدام اختيارية، ولا يُرسَل بلاغ
الخطأ إلا بعد أن تراه وتؤكّده. التفاصيل: [PRIVACY.md](PRIVACY.md).

## الإزالة

احذف إدخال `fontes` من إعدادات MCP في تطبيقك (في Claude Code:
`claude mcp remove fontes`)، ثم أغلق التطبيق وأعِد فتحه.

## من المفيد معرفته

يقرأ Fontes مصادر عامة، معظمها مواقع إلكترونية للمحاكم والحكومات. ويُعلِّم المصادر غير الرسمية في
إجاباته. افتح دائمًا رابط المصدر قبل الاعتماد على حكم أو نص.

إذا حدث خطأ ما، فأرسل ما فعلته ورسالة الخطأ التي رأيتها إلى fontesmcp@proton.me.

## قبل أن تعتمد عليه

- Fontes أداة بحث، وليس استشارة قانونية. استخدامه لا يجعل أي أحد محاميًا لك.
- يُقدَّم "كما هو"، دون أي ضمان، ولا يتحمل مؤلفوه المسؤولية عن كيفية استخدامه،
  في الحدود التي يسمح بها القانون. الشروط الكاملة في [الترخيص](../../../LICENSE) (Apache 2.0).
