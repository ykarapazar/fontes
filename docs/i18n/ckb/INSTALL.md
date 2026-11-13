> ئەمە وەرگێڕانێکە بە یارمەتیی ئامێر کراوە. وەشانی ئینگلیزی وەشانی باوەڕپێکراوە.

# دامەزراندنی Fontes

Fontes ڕێگە بە بەرنامەی AIەکەتان دەدات بڕیارەکانی دادگا و یاسا و ڕێساکان بە زیندوویی لە ماڵپەڕەکانی دادگا و
حکومەتدا، لە زیاتر لە 120 ناوچەی دادوەریدا بدۆزێتەوە. هەر ئەنجامێک بەستەری بۆ دەقە ڕەسەنەکە هەیە. ڕاژەکارێکی ستانداردی MCPە،
بۆیە لە هەر بەرنامەیەکدا کار دەکات کە بتوانێت ڕاژەکارێکی MCPی ناوخۆیی کار پێ بکات: Claude Desktop، Codex، Claude
Code، Cursor، VS Code (GitHub Copilot)، Gemini CLI، Windsurf، Zed، LM Studio، Cline و ئەوانی تر.

**Fontes هێشتا لە PyPI نییە.** ئەم هەنگاوانەی خوارەوە کاتێک کار دەکەن کە یەکەم وەشان دەربچێت.

بەرنامەکەتان هەڵبژێرن، هەنگاوەکانی جێبەجێ بکەن، پاشان [بپشکنن کە کار دەکات](#بپشکنن-کە-کار-دەکات).

## Claude Desktop

1. فایلی `.mcpb`ی Fontes لە
   [دوایین وەشان](https://github.com/ykarapazar/fontes/releases/latest) دابگرن.
2. دوو جار کلیکی لەسەر بکەن. Claude Desktop دەیکاتەوە.
3. کلیک لەسەر **Install** بکەن.

## Codex

لە تێرمیناڵێکدا:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI و پێوەکراوی (extension) Codex IDE ئەم ڕێکخستنە هاوبەش دەکەن (`~/.codex/config.toml`).
پێویستتان بە [uv](#پێویستتان-بە-uv-هەیە) هەیە.

## Claude Code

لە تێرمیناڵێکدا:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

پێویستتان بە [uv](#پێویستتان-بە-uv-هەیە) هەیە.

## بەرنامەکانی تر

هەر یەکێک لەمانە پێویستی بە [uv](#پێویستتان-بە-uv-هەیە) هەیە. تۆمارەکە (entry) زیاد بکەن، پاشەکەوتی بکەن، پاشان بەرنامەکە دابخەن و دووبارە بیکەنەوە.

**Cursor:** لە `~/.cursor/mcp.json` (هەموو پڕۆژەکان) یان `.cursor/mcp.json` (یەک پڕۆژە):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** لە Command Paletteەوە **MCP: Add Server** کار پێ بکەن، **Command (stdio)**
هەڵبژێرن، `uvx fontes-mcp` بنووسن و ناوی ڕاژەکارەکە بکەن بە `fontes`. یان ئەمە زیاد بکەن بۆ
`~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

ڕێکخستنە کۆنەکانی VS Code `.vscode/mcp.json` بەکار دەهێنن، کە تێیدا کلیلی ئاستی سەرەوە لە جیاتی `mcpServers`، `servers`ە.

**Gemini CLI:** لە تێرمیناڵێکدا، `gemini mcp add -s user fontes uvx fontes-mcp`. یان ئەمە زیاد بکەن بۆ
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** فایلی ڕێکخستنەکانتان بکەنەوە (**zed: open settings file**) و ئەمە زیاد بکەن:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** لە شریتی لای ڕاست (sidebar)، تابی **Program** بکەنەوە، کلیک لەسەر **Install → Edit
mcp.json** بکەن، و ئەمە زیاد بکەن:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** کلیک لەسەر ئایکۆنی **MCP Servers** بکەن، تابی **Configure** بکەنەوە، کلیک لەسەر **Configure MCP
Servers** بکەن، و هەمان تۆماری `mcpServers` زیاد بکەن کە بۆ LM Studio بوو.

**Claude Desktop، بە دەست** (لە جیاتی فایلی `.mcpb`): هەمان تۆماری `mcpServers` زیاد بکەن بۆ
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`، Windows:
`%APPDATA%\Claude\`).

**هەر بەرنامەیەکی تری MCP** (Windsurf و ئەوانی تر): بەڵگەنامەکانی خودی بەرنامەکە دەڵێن ڕاژەکارە MCPیەکانی
لە کوێ هەڵدەگرێت. زۆربەیان هەمان تۆمار وەردەگرن: فەرمان `uvx`، ئارگیومێنت `fontes`.

ئەگەر بەرنامەکە نەتوانێت `uvx` بدۆزێتەوە، ڕێڕەوی (path) تەواوی بەکار بهێنن (لە macOS و Linux، `which uvx` چاپی دەکات).

## پێویستتان بە uv هەیە

Codex، Claude Code و بەرنامەکانی تر Fontes بە `uvx` دەست پێ دەکەن، کە لەگەڵ **uv** دێت، ئامرازێکی بچووک و
خۆڕایی لە Astralەوە. بۆ دامەزراندنی، سەیری
[ڕێنماییی Astral](https://docs.astral.sh/uv/getting-started/installation/) بکەن، یان ئەمە کار پێ بکەن:

- macOS یان Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## کلیلەکان

هەندێک سەرچاوە پێویستیان بە کلیلێکی خۆڕایی هەیە: سەیری [KEYS.md](KEYS.md) بکەن.

## بپشکنن کە کار دەکات

لە گفتوگۆیەکی نوێدا بپرسن: *«Fontes لە کام ناوچە دادوەرییەکاندا دەتوانێت بگەڕێت؟»* بەرنامەکە دەبێت بە
لیستێکی وڵاتان وەڵام بداتەوە. ئەگەر وا نەبوو، بەرنامەکە جارێکی تر دابخەن و دووبارە بیکەنەوە.

## دامەزرێنەری یەک-کلیک (بەم زووانە)

دامەزرێنەرێک بۆ Mac و Windows کە Fontes لە هەموو بەرنامەکانتاندا بە یەکجار ڕێکدەخات لە ڕێگەدایە.
Claude Desktop، Codex، Claude Code، Cursor، VS Code (GitHub Copilot)، Windsurf، Gemini CLI،
Zed، LM Studio و Cline ڕێکدەخات. کاتێک دەرچوو:

**پێش ئەوەی دەست پێ بکەن:** هەر یەکێک لەم بەرنامانە بە تەواوی دابخەن. ئەمە بۆ Claude Code گرنگترینە:
لە کاتی کارکردنیدا، `~/.claude.json` دووبارە دەنووسێتەوە و دەتوانێت گۆڕانکارییەکەی دامەزرێنەر هەڵبوەشێنێتەوە. ئەگەر
ناتوانن Claude Code دابخەن، لە جیاتی ئەوە Fontes بە `claude mcp add` بۆی زیاد بکەن (سەیری [Claude Code](#claude-code) بکەن).

**Mac**

1. بوخچەی دابەزێنراوی **Fontes Installer** بکەنەوە.
2. دوو جار کلیک لەسەر **Install Fontes.command** بکەن.
   - ئەگەر Macەکەتان گوتی "cannot be opened because it is from an unidentified developer":
     کلیکی ڕاست (یان Control-click) لەسەر فایلەکە بکەن، **Open** هەڵبژێرن، پاشان دووبارە **Open**. تەنها
     یەک جار ئەمە دەکەن.
3. پەنجەرەیەک دەکرێتەوە و دەپرسێت ئایا ژمارەی بێناوی (anonymous) بەکارهێنان بنێرێت؛ بۆ نەخێر Enter دابگرن.
4. دەپرسێت ئایا ئێستا کلیلەکان زیاد بکات. بۆ تێپەڕاندن Enter دابگرن؛ سەیری [هەنگاوی کلیلەکان](#هەنگاوی-کلیلەکان) بکەن.
5. کاتێک گوتی **Done**، بەرنامەکانی AIتان دووبارە بکەنەوە.

**Windows**

1. **Fontes Installer**ی دابەزێنراو لە zip دەربهێنن (کلیکی ڕاست → Extract All).
2. دوو جار کلیک لەسەر **Install Fontes.cmd** بکەن.
   - ئەگەر Windows "Windows protected your PC"ی پیشان دا: کلیک لەسەر **More info** بکەن، پاشان **Run anyway**.
3. کاتێک پرسیاری لێ کرا ئایا ژمارەی بێناوی بەکارهێنان بنێرێت، بۆ نەخێر Enter دابگرن.
4. دەپرسێت ئایا ئێستا کلیلەکان زیاد بکات. بۆ تێپەڕاندن Enter دابگرن؛ سەیری [هەنگاوی کلیلەکان](#هەنگاوی-کلیلەکان) بکەن.
5. کاتێک گوتی **Done**، بەرنامەکانی AIتان دووبارە بکەنەوە. ئەگەر یەکێکیان هێشتا کاری دەکرد، بە تەواوی دایبخەن
   (لە system trayیش، لە نزیک کاتژمێرەکە) و دووبارە بیکەنەوە.

لە کۆتاییدا دامەزرێنەرەکە ئەو بەرنامانە لیست دەکات کە ڕێکی خستوون.

### کام بەرنامانە ڕێکدەخات

بەرنامەیەک تەنها کاتێک ڕێکدەخات کە بوخچەی ڕێکخستنەکانی ئەو بەرنامەیە پێشتر لەسەر کۆمپیوتەرەکەتان هەبێت. Claude Code
تەنها ئەگەر `~/.claude.json` هەبێت ڕێکدەخرێت. Claude Desktop هەمیشە ڕێکدەخرێت. هەر بەرنامەیەک یەک
تۆمار، `fontes`، لەم فایلەدا وەردەگرێت:

| بەرنامە | فایل (Mac و Linux) | فایل (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`، و کۆپیی خودی وەشانی Microsoft Store |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`، یان لە وەشانە کۆنەکاندا `~/.codeium/windsurf/mcp_config.json` | `%APPDATA%\devin\mcp_config.json`، یان `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code ڕێکدەخرێت ئەگەر `~/.copilot` یان بوخچەی ڕێکخستنەکانی خودی VS Code هەبێت.

دوو بەرنامە پێویستیان بە هەنگاوێکی تر هەیە:

- **Windsurf:** دوای دووبارە کردنەوەی، لە Cascade دا refresh دابگرن.
- **Cline لە ناو پێوەکراوە کۆنەکەی VS Code:** Fontes بە دەست زیاد بکەن (سەیری [Cline](#بەرنامەکانی-تر) بکەن).

### هەنگاوی کلیلەکان

ڕاستەوخۆ دوای دامەزراندن، دامەزرێنەرەکە پێشنیاری زیادکردنی کلیلە خۆڕاییەکانی فەرەنسا و ئەمریکا دەکات. بۆ
زیادکردن یان گۆڕینیان دواتر:

- **Mac:** لە بوخچەی دامەزرێنەرەکەدا دوو جار کلیک لەسەر **Add or change keys.command** بکەن، یان
  بەرنامەی Fontes Installer دووبارە بکەنەوە و **Add or change keys** هەڵبژێرن.
- **Windows:** لە بوخچەی دامەزرێنەرەکەدا دوو جار کلیک لەسەر **Add or change keys.cmd** بکەن.

نووسین نیشان نادرێت. کلیلەکان دەچنە ناو هەموو ئەو بەرنامانەی کە پێشتر Fontesیان تێدایە. دواتر بەرنامەکان دابخەن و
دووبارە بیانکەنەوە. کلیلەکان لە کوێ وەربگرن و چی دەکەنەوە: [KEYS.md](KEYS.md).

### پاشەکەوت، دووبارە کارپێکردن و لابردن

دامەزرێنەرەکە تەنها تۆماری `fontes` دەگۆڕێت. هەموو ڕێکخستن و لێدوانێکی (comment) تر وەک خۆی دەمێنێتەوە.
پێش ئەوەی فایلێک بگۆڕێت، کۆپییەک لە تەنیشتیدا پاشەکەوت دەکات، بە ناوی `<file>.fontes-backup-<date>`. ئەو کۆپییانەی
دوای زیادکردنی کلیلەکان دروستکراون ئەو کلیلانەیان تێدایە: ئەوانەی چیتر پێویستتان پێیان نییە بیانسڕنەوە. هەروەها
uv دادەمەزرێنێت. دووبارە کارپێکردنی هیچ کێشەیەکی نییە: ڕێکخستنەکە چاک دەکاتەوە و هیچی تر ناگۆڕێت.

بۆ لابردنی Fontes، دوو جار کلیک لەسەر **Uninstall Fontes.command** (Mac) یان **Uninstall Fontes.cmd**
(Windows) بکەن. تۆماری `fontes`، لەگەڵ کلیلەکان، لە هەموو بەرنامەکان لادەبات. ڕێکخستنەکانی ترتان
و کۆپییە پاشەکەوتەکان دەمێننەوە.

## نوێکردنەوەکان

- **دامەزرێنەر و فایلی `.mcpb`:** پێویست ناکات هیچ بکەن. ڕۆژی جارێک، کاتێک بەرنامەکە
  دەست پێ دەکات، Fontes لە پاشبنەمادا بۆ وەشانێکی نوێتر دەپشکنێت و ئامادەی دەکات؛ جاری داهاتوو کە
  بەرنامەکە دەست پێ بکات بەکاری دەهێنێت. ئەگەر نوێکردنەوەیەک دانەبەزێنرێت یان کار نەکات، Fontes
  بەردەوام دەبێت لە بەکارهێنانی ئەو وەشانەی کە کاری کردووە.
- **`uvx`:** Fontes پێتان دەڵێت کاتێک وەشانێکی نوێتر بەردەستە، لە سەرەوەی لیستی ناوچە دادوەرییەکانی.
  بۆ ئەوەی هەمیشە نوێترین وەشان کار پێ بکەن، لە جیاتی `fontes-mcp`، `fontes-mcp@latest` بەکار بهێنن.

بۆ ئەمە هیچ زانیارییەک دەربارەی ئێوە یان گەڕانەکانتان بۆ هیچ شوێنێک نانێردرێت.

## تایبەتمەندی

Fontes بە شێوەی بنەڕەتی هیچ شتێک دەربارەی ئێوە یان گەڕانەکانتان نانێرێت. ژمارەکانی بەکارهێنان ئارەزوومەندانەن (opt-in)، و ڕاپۆرتی
هەڵە تەنها دوای ئەوەی بیبینن و پشتڕاستی بکەنەوە دەنێردرێت. وردەکاری: [PRIVACY.md](PRIVACY.md).

## لابردنی

تۆماری `fontes` لە ڕێکخستنەکانی MCPی بەرنامەکەتان لابەرن (لە Claude Code:
`claude mcp remove fontes`)، پاشان بەرنامەکە دابخەن و دووبارە بیکەنەوە.

## باشە بزانن

Fontes سەرچاوە گشتییەکان دەخوێنێتەوە، زۆربەیان ماڵپەڕەکانی دادگا و حکومەت. سەرچاوە نافەرمییەکان لە
وەڵامەکانیدا نیشان دەکات. پێش ئەوەی پشت بە بڕیارێک یان ماددەیەک ببەستن، هەمیشە بەستەری سەرچاوەکە بکەنەوە.

ئەگەر شتێک بە هەڵەدا چوو، ئەوەی کردتان و ئەو هەڵەیەی بینیتان بە ئیمەیڵ بنێرن بۆ fontesmcp@proton.me.

## پێش ئەوەی پشتی پێ ببەستن

- Fontes ئامرازێکی توێژینەوەیە، نەک ئامۆژگاریی یاسایی. بەکارهێنانی هیچ کەسێک ناکات بە پارێزەری ئێوە.
- «وەک خۆی» (as is)، بەبێ هیچ گەرەنتییەک پێشکەش دەکرێت، و نووسەرەکانی بەرپرسیار نین لە چۆنیەتیی بەکارهێنانی،
  تا ئەو ئاستەی یاسا ڕێگە دەدات. مەرجە تەواوەکان لە [مۆڵەت](../../../LICENSE)دان (Apache 2.0).
