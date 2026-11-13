> এটি যন্ত্রের সহায়তায় করা অনুবাদ। ইংরেজি সংস্করণই প্রামাণ্য।

# Fontes ইনস্টল করা

Fontes আপনার AI অ্যাপকে ১২০টিরও বেশি এখতিয়ারে আদালত ও সরকারের ওয়েবসাইটে সরাসরি আদালতের রায় ও আইন খুঁজে
দেখতে দেয়। প্রতিটি ফলাফল মূল উৎসের লিংক দেয়। এটি একটি আদর্শ MCP সার্ভার, তাই যে অ্যাপ স্থানীয় MCP সার্ভার
চালাতে পারে তার যেকোনোটিতে এটি কাজ করে: Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot),
Gemini CLI, Windsurf, Zed, LM Studio, Cline এবং অন্যান্য।

আপনার অ্যাপ বেছে নিন, তার ধাপগুলো অনুসরণ করুন, তারপর [এটি কাজ করছে কি না যাচাই করুন](#এটি-কাজ-করছে-কি-না-যাচাই-করা)।

## Claude Desktop

1. [সর্বশেষ রিলিজ](https://github.com/ykarapazar/fontes/releases/latest) থেকে Fontes-এর `.mcpb` ফাইলটি
   ডাউনলোড করুন।
2. এতে ডাবল-ক্লিক করুন। Claude Desktop এটি খুলবে।
3. **Install**-এ ক্লিক করুন।

## Codex

একটি টার্মিনালে:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI ও Codex IDE এক্সটেনশন এই সেটিং (`~/.codex/config.toml`) ভাগ করে ব্যবহার করে।
আপনার [uv](#আপনার-uv-প্রয়োজন) প্রয়োজন।

## Claude Code

একটি টার্মিনালে:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

আপনার [uv](#আপনার-uv-প্রয়োজন) প্রয়োজন।

## অন্যান্য অ্যাপ

এগুলোর প্রতিটির জন্য [uv](#আপনার-uv-প্রয়োজন) প্রয়োজন। এন্ট্রিটি যোগ করুন, সংরক্ষণ করুন, তারপর অ্যাপটি বন্ধ করে
আবার খুলুন।

**Cursor:** `~/.cursor/mcp.json`-এ (সব প্রকল্পের জন্য) অথবা `.cursor/mcp.json`-এ (একটি প্রকল্পের জন্য):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** Command Palette থেকে **MCP: Add Server** চালান, **Command (stdio)** বেছে নিন,
`uvx fontes-mcp` লিখুন এবং সার্ভারের নাম দিন `fontes`। অথবা এটি `~/.copilot/mcp-config.json`-এ যোগ করুন:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

পুরোনো VS Code সেটআপে `.vscode/mcp.json` ব্যবহৃত হয়, যেখানে সর্বোচ্চ স্তরের কী (top-level key) `mcpServers`-এর
পরিবর্তে `servers`।

**Gemini CLI:** একটি টার্মিনালে, `gemini mcp add -s user fontes uvx fontes-mcp`। অথবা এটি
`~/.gemini/settings.json`-এ যোগ করুন:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** আপনার সেটিংস ফাইল খুলুন (**zed: open settings file**) এবং যোগ করুন:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** ডান দিকের সাইডবারে **Program** ট্যাব খুলুন, **Install → Edit mcp.json**-এ ক্লিক করুন, এবং
যোগ করুন:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** **MCP Servers** আইকনে ক্লিক করুন, **Configure** ট্যাব খুলুন, **Configure MCP Servers**-এ ক্লিক
করুন, এবং LM Studio-র মতো একই `mcpServers` এন্ট্রি যোগ করুন।

**Claude Desktop, হাতে** (`.mcpb` ফাইলের পরিবর্তে): একই `mcpServers` এন্ট্রি
`claude_desktop_config.json`-এ যোগ করুন (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`)।

**অন্য যেকোনো MCP অ্যাপ** (Windsurf ও অন্যান্য): অ্যাপটি তার MCP সার্ভারগুলো কোথায় রাখে, তা তার নিজস্ব
ডকুমেন্টেশনে বলা আছে। বেশিরভাগই একই এন্ট্রি নেয়: কমান্ড `uvx`, আর্গুমেন্ট `fontes`।

অ্যাপটি `uvx` খুঁজে না পেলে এর পূর্ণ পাথ ব্যবহার করুন (macOS ও Linux-এ `which uvx` এটি দেখায়)।

## আপনার uv প্রয়োজন

Codex, Claude Code ও অন্যান্য অ্যাপ Fontes চালু করে `uvx` দিয়ে, যা আসে **uv**-এর সঙ্গে: Astral-এর একটি ছোট
বিনামূল্যের টুল। এটি ইনস্টল করতে [Astral-এর নির্দেশিকা](https://docs.astral.sh/uv/getting-started/installation/)
দেখুন, অথবা চালান:

- macOS বা Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## API কী

কিছু উৎসের জন্য বিনামূল্যের একটি কী (key) প্রয়োজন: দেখুন [KEYS.md](KEYS.md)।

## এটি কাজ করছে কি না যাচাই করা

একটি নতুন চ্যাটে জিজ্ঞাসা করুন: *"Fontes কোন কোন এখতিয়ারে অনুসন্ধান করতে পারে?"* অ্যাপটি দেশগুলোর একটি তালিকা
দিয়ে উত্তর দেবে। না দিলে অ্যাপটি আরেকবার বন্ধ করে আবার খুলুন।

## এক-ক্লিকের ইনস্টলার (আসছে)

Mac ও Windows-এর জন্য একটি ইনস্টলার আসছে, যা একবারে আপনার সব অ্যাপে Fontes সেট আপ করে। এটি Claude Desktop,
Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio ও Cline সেট আপ করে।
এটি প্রকাশিত হলে:

**শুরু করার আগে:** এই অ্যাপগুলোর প্রতিটি পুরোপুরি বন্ধ করুন। এটি সবচেয়ে গুরুত্বপূর্ণ Claude Code-এর জন্য: এটি
চলার সময় `~/.claude.json` নতুন করে লেখে এবং ইনস্টলারের পরিবর্তন বাতিল করে দিতে পারে। Claude Code বন্ধ করতে না
পারলে, তার পরিবর্তে `claude mcp add` দিয়ে এতে Fontes যোগ করুন (দেখুন [Claude Code](#claude-code))।

**Mac**

1. ডাউনলোড করা **Fontes Installer** ফোল্ডারটি খুলুন।
2. **Install Fontes.command**-এ ডাবল-ক্লিক করুন।
   - আপনার Mac যদি বলে এটি "খোলা যাবে না কারণ এটি অজ্ঞাত ডেভেলপারের" (cannot be opened because it is from
     an unidentified developer): ফাইলটিতে রাইট-ক্লিক (বা Control-ক্লিক) করুন, **Open** বেছে নিন, তারপর আবার
     **Open**। এটি আপনাকে কেবল একবারই করতে হবে।
3. একটি উইন্ডো খুলবে এবং জিজ্ঞাসা করবে বেনামি ব্যবহার-গণনা পাঠানো হবে কি না; "না"-র জন্য Enter চাপুন।
4. এটি জিজ্ঞাসা করবে এখনই কী যোগ করবেন কি না। বাদ দিতে Enter চাপুন; দেখুন [কী যোগ করার ধাপ](#কী-যোগ-করার-ধাপ)।
5. যখন এটি **Done** দেখাবে, আপনার AI অ্যাপগুলো আবার খুলুন।

**Windows**

1. ডাউনলোড করা **Fontes Installer** আনজিপ করুন (রাইট-ক্লিক → Extract All)।
2. **Install Fontes.cmd**-এ ডাবল-ক্লিক করুন।
   - Windows যদি "Windows protected your PC" দেখায়: **More info**-তে ক্লিক করুন, তারপর **Run anyway**-তে।
3. বেনামি ব্যবহার-গণনা পাঠানো হবে কি না জিজ্ঞাসা করা হলে "না"-র জন্য Enter চাপুন।
4. এটি জিজ্ঞাসা করবে এখনই কী যোগ করবেন কি না। বাদ দিতে Enter চাপুন; দেখুন [কী যোগ করার ধাপ](#কী-যোগ-করার-ধাপ)।
5. যখন এটি **Done** দেখাবে, আপনার AI অ্যাপগুলো আবার খুলুন। কোনোটি তখনো চালু থাকলে, সেটি পুরোপুরি বন্ধ করুন
   (ঘড়ির কাছে সিস্টেম ট্রে থেকেও) এবং আবার খুলুন।

শেষে ইনস্টলার যেসব অ্যাপ সেট আপ করেছে সেগুলোর তালিকা দেখায়।

### এটি কোন কোন অ্যাপ সেট আপ করে

কোনো অ্যাপের সেটিংস ফোল্ডার আপনার কম্পিউটারে আগে থেকেই থাকলে তবেই এটি সেই অ্যাপ সেট আপ করে। Claude Code সেট আপ
করা হয় কেবল `~/.claude.json` থাকলে। Claude Desktop সবসময় সেট আপ করা হয়। প্রতিটি অ্যাপ এই ফাইলে একটি এন্ট্রি
পায়, `fontes`:

| অ্যাপ | ফাইল (Mac ও Linux) | ফাইল (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, এবং Microsoft Store সংস্করণের নিজস্ব অনুলিপি |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, অথবা পুরোনো সংস্করণে `~/.codeium/windsurf/mcp_config.json` | `%APPDATA%\devin\mcp_config.json`, অথবা `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

`~/.copilot` অথবা VS Code-এর নিজস্ব সেটিংস ফোল্ডার থাকলে VS Code সেট আপ করা হয়।

দুটি অ্যাপের জন্য আরও একটি ধাপ লাগে:

- **Windsurf:** আবার খোলার পর Cascade-এ refresh চাপুন।
- **পুরোনো VS Code এক্সটেনশনের ভেতরের Cline:** হাতে Fontes যোগ করুন (দেখুন [Cline](#অন্যান্য-অ্যাপ))।

### কী যোগ করার ধাপ

ইনস্টল শেষ হওয়ার ঠিক পরেই ইনস্টলার ফ্রান্স ও যুক্তরাষ্ট্রের বিনামূল্যের কী যোগ করার প্রস্তাব দেয়। পরে এগুলো যোগ
বা পরিবর্তন করতে:

- **Mac:** ইনস্টলার ফোল্ডারে **Add or change keys.command**-এ ডাবল-ক্লিক করুন, অথবা Fontes Installer অ্যাপটি
  আবার খুলে **Add or change keys** বেছে নিন।
- **Windows:** ইনস্টলার ফোল্ডারে **Add or change keys.cmd**-এ ডাবল-ক্লিক করুন।

টাইপ করা লেখা দেখা যায় না। কীগুলো এমন প্রতিটি অ্যাপে যায় যেটিতে আগে থেকেই Fontes আছে। এরপর অ্যাপগুলো বন্ধ করে আবার
খুলুন। কী কোথায় পাবেন এবং সেগুলো কী খুলে দেয়: [KEYS.md](KEYS.md)।

### ব্যাকআপ, পুনরায় চালানো ও সরানো

ইনস্টলার কেবল `fontes` এন্ট্রিটি পরিবর্তন করে। অন্য প্রতিটি সেটিং ও মন্তব্য যেমন ছিল তেমনই থাকে। কোনো ফাইল
পরিবর্তনের আগে এটি তার পাশে একটি অনুলিপি সংরক্ষণ করে, যার নাম `<file>.fontes-backup-<date>`। আপনি কী যোগ করার
পরে তৈরি অনুলিপিগুলোতে সেই কীগুলো থাকে: যেগুলো আর প্রয়োজন নেই সেগুলো মুছে ফেলুন। এটি uv-ও ইনস্টল করে। এটি আবার
চালানো নিরাপদ: এটি সেটআপ মেরামত করে এবং আর কিছুই পরিবর্তন করে না।

Fontes সরাতে **Uninstall Fontes.command** (Mac) বা **Uninstall Fontes.cmd** (Windows)-এ ডাবল-ক্লিক করুন। এটি
প্রতিটি অ্যাপ থেকে `fontes` এন্ট্রিটি, কীসহ, সরিয়ে দেয়। আপনার অন্যান্য সেটিংস ও ব্যাকআপ অনুলিপিগুলো থেকে যায়।

## হালনাগাদ

- **ইনস্টলার ও `.mcpb` ফাইল:** আপনাকে কিছুই করতে হবে না। দিনে একবার, অ্যাপ চালু হলে, Fontes ব্যাকগ্রাউন্ডে নতুন
  সংস্করণ আছে কি না পরীক্ষা করে এবং সেটি প্রস্তুত রাখে; পরের বার অ্যাপ চালু হলে সেটি ব্যবহার করে। কোনো হালনাগাদ
  ডাউনলোড না হলে বা কাজ না করলে, Fontes যে সংস্করণটি কাজ করেছিল সেটিই ব্যবহার করতে থাকে।
- **`uvx`:** নতুন সংস্করণ পাওয়া গেলে Fontes তা আপনাকে জানায়, তার এখতিয়ারের তালিকার একেবারে ওপরে। সবসময় সর্বশেষ
  সংস্করণ চালাতে `fontes-mcp`-এর জায়গায় `fontes-mcp@latest` ব্যবহার করুন।

এর জন্য আপনার বা আপনার অনুসন্ধান সম্পর্কে কোনো তথ্য কোথাও পাঠানো হয় না।

## গোপনীয়তা

ডিফল্টভাবে Fontes আপনার বা আপনার অনুসন্ধান সম্পর্কে কিছুই পাঠায় না। ব্যবহার-গণনা অপ্ট-ইন, এবং বাগ রিপোর্ট কেবল
আপনি দেখে নিশ্চিত করার পরেই পাঠানো হয়। বিস্তারিত: [PRIVACY.md](PRIVACY.md)।

## এটি সরানো

আপনার অ্যাপের MCP সেটিংস থেকে `fontes` এন্ট্রিটি সরিয়ে দিন (Claude Code-এ: `claude mcp remove fontes`), তারপর
অ্যাপটি বন্ধ করে আবার খুলুন।

## জেনে রাখা ভালো

Fontes প্রকাশ্য উৎস পড়ে, বেশিরভাগই আদালত ও সরকারের ওয়েবসাইট। অদাপ্তরিক উৎসগুলো এটি তার উত্তরে চিহ্নিত করে।
কোনো রায় বা বিধানের ওপর নির্ভর করার আগে সবসময় উৎসের লিংকটি খুলুন।

কিছু ভুল হলে, আপনি কী করেছিলেন এবং কোন ত্রুটি দেখেছেন তা fontesmcp@proton.me-এ ইমেইল করুন।

## নির্ভর করার আগে

- Fontes একটি গবেষণার টুল, আইনি পরামর্শ নয়। এটি ব্যবহার করলে কেউ আপনার আইনজীবী হয়ে যান না।
- এটি "যেমন আছে" (as is) ভিত্তিতে, কোনো ওয়ারেন্টি ছাড়াই দেওয়া হয়, এবং আইন যতদূর অনুমতি দেয়, এটি কীভাবে ব্যবহৃত
  হয় তার জন্য এর রচয়িতারা দায়ী নন। পূর্ণ শর্তাবলি [লাইসেন্সে](../../../LICENSE) (Apache 2.0) আছে।
