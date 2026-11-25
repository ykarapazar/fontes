> ይህ በማሽን የታገዘ ትርጉም ነው። የእንግሊዝኛው ቅጂ ገዢ ነው።

# Fontesን መጫን

Fontes የ AI መተግበሪያዎ ከ120 በላይ በሆኑ የሕግ ክልሎች (jurisdictions) የፍርድ ቤት ውሳኔዎችንና ሕጎችን በፍርድ ቤትና
በመንግሥት ድረ ገጾች ላይ በቀጥታ እንዲፈልግ ያስችለዋል። እያንዳንዱ ውጤት ከዋናው ጋር ያገናኛል። መደበኛ የ MCP አገልጋይ
ስለሆነ፣ አካባቢያዊ (local) የ MCP አገልጋይ ማስኬድ በሚችል በማንኛውም መተግበሪያ ውስጥ ይሠራል፦ Claude Desktop፣ Codex፣
Claude Code፣ Cursor፣ VS Code (GitHub Copilot)፣ Gemini CLI፣ Windsurf፣ Zed፣ LM Studio፣ Cline እና ሌሎችም።

መተግበሪያዎን ይምረጡ፣ ደረጃዎቹን ይከተሉ፣ ከዚያም [መሥራቱን ያረጋግጡ](#መሥራቱን-ማረጋገጥ)።

## Claude Desktop

1. የ Fontes `.mcpb` ፋይልን ከ
   [የቅርብ ጊዜው ልቀት](https://github.com/ykarapazar/fontes/releases/latest) ያውርዱ።
2. ሁለት ጊዜ ጠቅ ያድርጉበት። Claude Desktop ይከፍተዋል።
3. **Install** ን ጠቅ ያድርጉ።

## Codex

በተርሚናል ውስጥ:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

የ Codex CLI እና የ Codex IDE ቅጥያ (extension) ይህን ቅንብር ይጋራሉ (`~/.codex/config.toml`)።
[uv](#uv-ያስፈልግዎታል) ያስፈልግዎታል።

## Claude Code

በተርሚናል ውስጥ:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

[uv](#uv-ያስፈልግዎታል) ያስፈልግዎታል።

## ሌሎች መተግበሪያዎች

እያንዳንዳቸው [uv](#uv-ያስፈልግዎታል) ያስፈልጋቸዋል። ግቤቱን (entry) ያክሉ፣ ያስቀምጡ፣ ከዚያም መተግበሪያውን ዘግተው እንደገና
ይክፈቱ።

**Cursor:** በ `~/.cursor/mcp.json` (ለሁሉም ፕሮጀክቶች) ወይም በ `.cursor/mcp.json` (ለአንድ ፕሮጀክት) ውስጥ:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** ከ Command Palette **MCP: Add Server** ን ያስኪዱ፣ **Command (stdio)** ን ይምረጡ፣
`uvx fontes-mcp` ን ያስገቡ፣ አገልጋዩንም `fontes` ብለው ይሰይሙት። ወይም ይህን በ `~/.copilot/mcp-config.json` ውስጥ ያክሉ:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

የቆዩ የ VS Code ቅንብሮች `.vscode/mcp.json` ን ይጠቀማሉ፤ እዚያ የላይኛው ደረጃ ቁልፍ (top-level key) ከ `mcpServers` ይልቅ
`servers` ነው።

**Gemini CLI:** በተርሚናል ውስጥ፣ `gemini mcp add -s user fontes uvx fontes-mcp`። ወይም ይህን በ `~/.gemini/settings.json`
ውስጥ ያክሉ:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** የቅንብሮች ፋይልዎን ይክፈቱ (**zed: open settings file**) እና ያክሉ:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** በቀኝ በኩል ባለው የጎን አሞሌ (sidebar) ውስጥ **Program** ትርን ይክፈቱ፣ **Install → Edit mcp.json** ን ጠቅ
ያድርጉ፣ እና ያክሉ:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** የ **MCP Servers** አዶን ጠቅ ያድርጉ፣ **Configure** ትርን ይክፈቱ፣ **Configure MCP Servers** ን ጠቅ ያድርጉ፣
እና ለ LM Studio የተጠቀሙበትን ተመሳሳይ የ `mcpServers` ግቤት ያክሉ።

**Claude Desktop፣ በእጅ** (ከ `.mcpb` ፋይሉ ይልቅ): ተመሳሳዩን የ `mcpServers` ግቤት በ `claude_desktop_config.json`
ውስጥ ያክሉ (macOS: `~/Library/Application Support/Claude/`፣ Windows: `%APPDATA%\Claude\`)።

**ሌላ ማንኛውም የ MCP መተግበሪያ** (Windsurf እና ሌሎች): የ MCP አገልጋዮቹን የት እንደሚያስቀምጥ የራሱ ሰነድ (documentation)
ይገልጻል። አብዛኞቹ ተመሳሳዩን ግቤት ይቀበላሉ፦ ትእዛዝ (command) `uvx`፣ ነጋሪ እሴት (argument) `fontes-mcp`።

መተግበሪያው `uvx` ን ማግኘት ካልቻለ፣ ሙሉ ዱካውን (path) ይጠቀሙ (በ macOS እና በ Linux ላይ `which uvx` ያሳየዋል)።

## uv ያስፈልግዎታል

Codex፣ Claude Code እና ሌሎቹ መተግበሪያዎች Fontesን የሚያስጀምሩት በ `uvx` ነው፤ እሱም ከ **uv** ጋር ይመጣል፣ ይህም ከ
Astral የተገኘ ትንሽ ነፃ መሣሪያ ነው። ለመጫን [የ Astral መመሪያን](https://docs.astral.sh/uv/getting-started/installation/)
ይመልከቱ፣ ወይም ያስኪዱ:

- macOS ወይም Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## ቁልፎች

አንዳንድ ምንጮች ነፃ ቁልፍ ያስፈልጋቸዋል: [KEYS.md](KEYS.md) ን ይመልከቱ።

## መሥራቱን ማረጋገጥ

በአዲስ ውይይት (chat) ውስጥ ይጠይቁ: *"Fontes በየትኞቹ የሕግ ክልሎች መፈለግ ይችላል?"* መተግበሪያው በአገሮች ዝርዝር
መመለስ አለበት። ካልመለሰ፣ መተግበሪያውን አንድ ጊዜ እንደገና ዘግተው ይክፈቱ።

## በአንድ ጠቅታ የሚጭን መጫኛ (Mac እና Windows)

መጫኛው Fontesን በሁሉም መተግበሪያዎችዎ ውስጥ በአንድ ጊዜ ያዘጋጃል፦ Claude Desktop፣ Codex፣ Claude Code፣ Cursor፣ VS
Code (GitHub Copilot)፣ Windsurf፣ Gemini CLI፣ Zed፣ LM Studio እና Cline።

**ከመጀመርዎ በፊት:** ከእነዚህ መተግበሪያዎች እያንዳንዱን ሙሉ በሙሉ ይዝጉ። ይህ ይበልጥ የሚያስፈልገው ለ Claude Code ነው፦
በሚሠራበት ጊዜ `~/.claude.json` ን እንደገና ይጽፋል፣ የመጫኛውን ለውጥም ሊቀለብሰው ይችላል። Claude Code ን መዝጋት ካልቻሉ፣
በምትኩ Fontesን በ `claude mcp add` ያክሉለት ([Claude Code](#claude-code) ን ይመልከቱ)።

**Mac**

1. የ Mac መጫኛውን (`Fontes-Installer-…-mac.zip`) ከ[የቅርብ ጊዜው
   ልቀት](https://github.com/ykarapazar/fontes/releases/latest) ያውርዱ፣ ለመፍታት (unzip) ሁለት ጊዜ ጠቅ ያድርጉት።
2. **Fontes Installer** ን ሁለት ጊዜ ጠቅ ያድርጉ። Macዎ ከበይነመረብ የወረደ መተግበሪያ መክፈት ይፈልጉ እንደሆነ ከጠየቀ፣ **Open** ን
   ጠቅ ያድርጉ።
3. **ጫን** ን ይምረጡ፣ **እሺ** ን ጠቅ ያድርጉ። ማዘጋጀቱ አንድ ደቂቃ ያህል ይወስዳል።
4. አንድ መልእክት ያዘጋጃቸውን መተግበሪያዎች ይዘረዝራል። **ተጠናቋል** ን ጠቅ ያድርጉ፣ ከዚያም እነዚያን መተግበሪያዎች እንደገና ይክፈቱ። አማራጭ ነፃ
   ቁልፎቹን መጀመሪያ ለመጨመር፣ በምትኩ **ቁልፎችን አክል** ን ጠቅ ያድርጉ፤ [የቁልፎች ደረጃ](#የቁልፎች-ደረጃ) ን ይመልከቱ።

**Windows**

1. የ Windows መጫኛውን (`Fontes-Setup-….exe`) ከ[የቅርብ ጊዜው ልቀት](https://github.com/ykarapazar/fontes/releases/latest) ያውርዱ፣ ሁለት ጊዜ ጠቅ ያድርጉት።
   - Windows "Windows protected your PC" ካሳየ፦ **More info** ን፣ ከዚያም **Run anyway** ን ጠቅ ያድርጉ።
2. **ጫን** ን ይምረጡ። መስኮት ይከፈታል እና Fontesን ያዘጋጃል።
3. ማንነትን የማይገልጹ የአጠቃቀም ቆጠራዎችን ለመላክ ሲጠየቁ፣ ለ"አይ" Enter ን ይጫኑ።
4. ቁልፎችን አሁን ለመጨመር ይጠይቃል። ለመዝለል Enter ን ይጫኑ፤ [የቁልፎች ደረጃ](#የቁልፎች-ደረጃ) ን ይመልከቱ።
5. **ተጠናቋል** ሲል፣ የ AI መተግበሪያዎችዎን እንደገና ይክፈቱ። አንዱ አሁንም እየሠራ ከነበረ፣ ሙሉ በሙሉ ይዝጉት (ከሰዓቱ አጠገብ
   ካለው system tray ውስጥም) እና እንደገና ይክፈቱት።

በመጨረሻ መጫኛው ያዘጋጃቸውን መተግበሪያዎች ይዘረዝራል።

### የሚያዘጋጃቸው መተግበሪያዎች

አንድን መተግበሪያ የሚያዘጋጀው የዚያ መተግበሪያ የቅንብሮች አቃፊ አስቀድሞ በኮምፒውተርዎ ላይ ካለ ብቻ ነው። Claude Code
የሚዘጋጀው `~/.claude.json` ካለ ብቻ ነው። Claude Desktop ሁልጊዜ ይዘጋጃል። እያንዳንዱ መተግበሪያ በዚህ ፋይል ውስጥ አንድ
ግቤት፣ `fontes`፣ ያገኛል:

| መተግበሪያ | ፋይል (Mac እና Linux) | ፋይል (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`፣ እና የ Microsoft Store ሥሪቱ የራሱ ቅጂ |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`፣ ወይም በቆዩ ሥሪቶች ላይ `~/.codeium/windsurf/mcp_config.json` | `%APPDATA%\devin\mcp_config.json`፣ ወይም `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code የሚዘጋጀው `~/.copilot` ወይም የ VS Code የራሱ የቅንብሮች አቃፊ ካለ ነው።

ሁለት መተግበሪያዎች አንድ ተጨማሪ ደረጃ ያስፈልጋቸዋል:

- **Windsurf:** እንደገና ከከፈቱት በኋላ፣ በ Cascade ውስጥ refresh ን ይጫኑ።
- **በቆየው የ VS Code ቅጥያ ውስጥ ያለ Cline:** Fontesን በእጅ ያክሉ ([Cline](#ሌሎች-መተግበሪያዎች) ን ይመልከቱ)።

### የቁልፎች ደረጃ

ከተጫነ በኋላ ወዲያውኑ፣ መጫኛው ነፃዎቹን የፈረንሳይና የአሜሪካ ቁልፎች ለመጨመር ያቀርባል። በኋላ ለመጨመር ወይም ለመቀየር:

- **Mac:** **Fontes Installer** ን እንደገና ከፍተው **ቁልፎችን አክል ወይም ቀይር** ን ይምረጡ።
- **Windows:** የ Start ምናሌውን ይክፈቱ፣ ከዚያም **Fontes** → **ቁልፎችን አክል ወይም ቀይር** ን ይምረጡ።

የሚተይቡት አይታይም። ቁልፎቹ Fontes ቀድሞውኑ ወዳለባቸው መተግበሪያዎች ሁሉ ይገባሉ። ከዚያ በኋላ መተግበሪያዎቹን ዘግተው እንደገና
ይክፈቱ። ቁልፎቹን የት እንደሚያገኙና ምን እንደሚከፍቱ: [KEYS.md](KEYS.md)።

### ምትኬዎች፣ ዳግም ማስኬድና ማስወገድ

መጫኛው የሚቀይረው የ `fontes` ግቤቱን ብቻ ነው። ሌላው እያንዳንዱ ቅንብርና አስተያየት (comment) እንደነበረ ይቆያል። አንድን
ፋይል ከመቀየሩ በፊት፣ `<file>.fontes-backup-<date>` የሚል ስም ያለው ቅጂ ከጎኑ ያስቀምጣል። ቁልፎችን ካከሉ በኋላ የተሠሩ
ቅጂዎች እነዚያን ቁልፎች ይይዛሉ፦ ከእንግዲህ የማያስፈልጉዎትን ይሰርዙ። uvንም ይጭናል። እንደገና ማስኬዱ ችግር የለውም፦ ቅንብሩን
ይጠግናል፣ ሌላ ምንም አይቀይርም።

Fontesን ለማስወገድ **Fontes Installer** ን ከፍተው **አስወግድ** ን ይምረጡ (Mac)፣ ወይም በ Settings → Apps (Windows)
ውስጥ **Fontes** ን ያራግፉ። የ `fontes` ግቤቱን፣ ቁልፎቹን ጨምሮ፣ ከእያንዳንዱ መተግበሪያ ያስወግዳል። ሌሎቹ ቅንብሮችዎና የምትኬ ቅጂዎቹ ይቆያሉ።

## ዝማኔዎች

- **መጫኛውና የ `.mcpb` ፋይሉ:** ምንም ማድረግ አያስፈልግዎትም። በቀን አንድ ጊዜ፣ መተግበሪያው ሲጀምር፣ Fontes ከበስተጀርባ
  አዲስ ሥሪት እንዳለ ይፈትሻል፣ ያዘጋጀዋልም፤ መተግበሪያው በሚቀጥለው ጊዜ ሲጀምር ይጠቀምበታል። አንድ ዝማኔ መውረድ ካልቻለ ወይም
  ካልሠራ፣ Fontes የሠራውን ሥሪት መጠቀሙን ይቀጥላል።
- **`uvx`:** አዲስ ሥሪት ሲኖር Fontes በሕግ ክልሎቹ ዝርዝር አናት ላይ ይነግርዎታል። ሁልጊዜ አዲሱን ሥሪት ለማስኬድ፣ በ
  `fontes-mcp` ምትክ `fontes-mcp@latest` ን ይጠቀሙ።

ለዚህ ሲባል ስለ እርስዎም ሆነ ስለ ፍለጋዎችዎ ምንም መረጃ ወደ የትም አይላክም።

## ግላዊነት

Fontes በነባሪ (default) ስለ እርስዎም ሆነ ስለ ፍለጋዎችዎ ምንም አይልክም። የአጠቃቀም ቆጠራዎች እርስዎ ሲፈቅዱ ብቻ (opt-in)
ናቸው፣ የስህተት ሪፖርትም የሚላከው እርስዎ አይተው ካረጋገጡ በኋላ ብቻ ነው። ዝርዝሩ: [PRIVACY.md](PRIVACY.md)።

## ማስወገድ

የ `fontes` ግቤቱን ከመተግበሪያዎ የ MCP ቅንብሮች ውስጥ ያስወግዱ (በ Claude Code ውስጥ: `claude mcp remove fontes`)፣
ከዚያም መተግበሪያውን ዘግተው እንደገና ይክፈቱ።

## ማወቅ የሚገባዎ

Fontes የሕዝብ ምንጮችን ያነባል፣ በአብዛኛው የፍርድ ቤትና የመንግሥት ድረ ገጾችን። ይፋዊ ያልሆኑትን በመልሶቹ ውስጥ ምልክት
ያደርጋቸዋል። በአንድ ውሳኔ ወይም ድንጋጌ ላይ ከመመሥረትዎ በፊት ሁልጊዜ የምንጩን ሊንክ ይክፈቱ።

የሆነ ነገር ከተበላሸ፣ ያደረጉትን እና ያዩትን የስህተት መልእክት ወደ fontesmcp@proton.me ኢሜይል ያድርጉ።

## ከመመሥረትዎ በፊት

- Fontes የጥናት መሣሪያ እንጂ የሕግ ምክር አይደለም። እሱን መጠቀም ማንንም ጠበቃዎ አያደርገውም።
- የሚቀርበው "እንዳለ" (as is) ነው፣ ያለ ምንም ዋስትና፣ ደራሲዎቹም ሕጉ በሚፈቅደው መጠን ለአጠቃቀሙ ተጠያቂ አይደሉም። ሙሉ
  ውሎቹ በ [ፈቃዱ](../../../LICENSE) (Apache 2.0) ውስጥ ይገኛሉ።
