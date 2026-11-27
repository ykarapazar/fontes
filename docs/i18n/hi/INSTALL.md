> यह मशीन की सहायता से किया गया अनुवाद है। अंग्रेज़ी संस्करण ही प्रामाणिक है।

# Fontes इंस्टॉल करना

Fontes आपके AI ऐप को 125 क्षेत्राधिकारों में न्यायालयों और सरकार की वेबसाइटों पर न्यायालयों के निर्णय और
विधान लाइव खोजने देता है। हर परिणाम मूल का लिंक देता है। यह एक मानक MCP सर्वर है, इसलिए यह किसी भी ऐसे ऐप में
काम करता है जो स्थानीय MCP सर्वर चला सकता है: Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub
Copilot), Gemini CLI, Windsurf, Zed, LM Studio, Cline और अन्य।

अपना ऐप चुनें, उसके चरणों का पालन करें, फिर [जाँचें कि यह काम करता है](#जाँचना-कि-यह-काम-करता-है)।

## Claude Desktop

1. [नवीनतम रिलीज़](https://github.com/ykarapazar/fontes/releases/latest) से Fontes की `.mcpb` फ़ाइल
   डाउनलोड करें।
2. उस पर डबल-क्लिक करें। Claude Desktop उसे खोलता है।
3. **Install** पर क्लिक करें।

## Codex

टर्मिनल में:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI और Codex IDE एक्सटेंशन यह सेटिंग साझा करते हैं (`~/.codex/config.toml`)।
आपको [uv](#आपको-uv-चाहिए) चाहिए।

## Claude Code

टर्मिनल में:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

आपको [uv](#आपको-uv-चाहिए) चाहिए।

## अन्य ऐप

इनमें से हर एक को [uv](#आपको-uv-चाहिए) चाहिए। प्रविष्टि जोड़ें, सहेजें, फिर ऐप को बंद करके फिर से खोलें।

**Cursor:** `~/.cursor/mcp.json` (सभी प्रोजेक्ट) या `.cursor/mcp.json` (एक प्रोजेक्ट) में:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** Command Palette से **MCP: Add Server** चलाएँ, **Command (stdio)** चुनें,
`uvx fontes-mcp` दर्ज करें और सर्वर का नाम `fontes` रखें। या इसे `~/.copilot/mcp-config.json` में जोड़ें:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

पुराने VS Code सेटअप `.vscode/mcp.json` का उपयोग करते हैं, जहाँ शीर्ष-स्तर की कुंजी `mcpServers` के बजाय
`servers` होती है।

**Gemini CLI:** टर्मिनल में, `gemini mcp add -s user fontes uvx fontes-mcp`। या इसे `~/.gemini/settings.json`
में जोड़ें:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** अपनी सेटिंग्स फ़ाइल खोलें (**zed: open settings file**) और जोड़ें:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** दाईं ओर के साइडबार में **Program** टैब खोलें, **Install → Edit mcp.json** पर क्लिक करें, और
जोड़ें:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** **MCP Servers** आइकन पर क्लिक करें, **Configure** टैब खोलें, **Configure MCP Servers** पर क्लिक
करें, और वही `mcpServers` प्रविष्टि जोड़ें जो LM Studio के लिए है।

**Claude Desktop, हाथ से** (`.mcpb` फ़ाइल के बजाय): वही `mcpServers` प्रविष्टि
`claude_desktop_config.json` में जोड़ें (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`)।

**कोई भी अन्य MCP ऐप** (Windsurf और अन्य): उसका अपना दस्तावेज़ बताता है कि वह अपने MCP सर्वर कहाँ रखता है।
अधिकांश वही प्रविष्टि लेते हैं: कमांड `uvx`, आर्ग्युमेंट `fontes-mcp`।

यदि ऐप को `uvx` नहीं मिलता, तो उसके पूरे पाथ का उपयोग करें (macOS और Linux पर `which uvx` उसे दिखाता है)।

## आपको uv चाहिए

Codex, Claude Code और अन्य ऐप Fontes को `uvx` से शुरू करते हैं, जो **uv** के साथ आता है, Astral का एक छोटा
मुफ़्त टूल। इसे इंस्टॉल करने के लिए [Astral की गाइड](https://docs.astral.sh/uv/getting-started/installation/)
देखें, या चलाएँ:

- macOS या Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## कुंजियाँ

कुछ स्रोतों के लिए मुफ़्त कुंजी चाहिए: देखें [KEYS.md](KEYS.md)।

## जाँचना कि यह काम करता है

एक नई चैट में पूछें: *"Fontes किन क्षेत्राधिकारों में खोज सकता है?"* ऐप को देशों की सूची के साथ उत्तर देना
चाहिए। यदि ऐसा नहीं होता, तो ऐप को एक बार और बंद करके फिर से खोलें।

## एक-क्लिक इंस्टॉलर (Mac और Windows)

इंस्टॉलर आपके सभी ऐप में एक साथ Fontes सेट अप करता है: Claude Desktop, Codex, Claude Code, Cursor,
VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio और Cline।

**शुरू करने से पहले:** इनमें से हर ऐप को पूरी तरह बंद करें। यह सबसे अधिक Claude Code के लिए मायने रखता है:
चलते समय वह `~/.claude.json` को फिर से लिखता है और इंस्टॉलर का बदलाव पलट सकता है। यदि आप Claude Code बंद नहीं
कर सकते, तो इसके बजाय उसमें `claude mcp add` से Fontes जोड़ें (देखें [Claude Code](#claude-code))।

**Mac**

1. [नवीनतम रिलीज़](https://github.com/ykarapazar/fontes/releases/latest) से Mac इंस्टॉलर
   (`Fontes-Installer-…-mac.zip`) डाउनलोड करें और उसे अनज़िप करने के लिए उस पर डबल-क्लिक करें।
2. **Fontes Installer** पर डबल-क्लिक करें। यदि आपका Mac पूछे कि क्या इंटरनेट से डाउनलोड किया गया ऐप खोलना है,
   तो **Open** पर क्लिक करें।
3. **इंस्टॉल करें** चुनें और **ठीक है** पर क्लिक करें। सेट अप में लगभग एक मिनट लगता है।
4. एक संदेश उन ऐप की सूची दिखाता है जिन्हें उसने सेट अप किया। **हो गया** पर क्लिक करें, फिर उन ऐप को फिर से
   खोलें। पहले वैकल्पिक मुफ़्त कुंजियाँ जोड़ने के लिए, इसके बजाय **कुंजियाँ जोड़ें** पर क्लिक करें; देखें
   [कुंजियों वाला चरण](#कुंजियों-वाला-चरण)।

**Windows**

1. [नवीनतम रिलीज़](https://github.com/ykarapazar/fontes/releases/latest) से Windows इंस्टॉलर (`Fontes-Setup-….exe`) डाउनलोड करें और उस पर डबल-क्लिक करें।
   - यदि Windows "Windows protected your PC" दिखाता है: **More info** पर क्लिक करें, फिर **Run anyway**।
2. **इंस्टॉल करें** पर क्लिक करें। एक विंडो खुलती है और Fontes सेट अप करती है।
3. जब पूछा जाए कि क्या अनाम उपयोग-गणना भेजनी है, तो "नहीं" के लिए Enter दबाएँ।
4. वह पूछता है कि क्या अभी कुंजियाँ जोड़नी हैं। छोड़ने के लिए Enter दबाएँ; देखें
   [कुंजियों वाला चरण](#कुंजियों-वाला-चरण)।
5. जब वह **Done** कहे, तो अपने AI ऐप फिर से खोलें। यदि कोई अभी भी चल रहा था, तो उसे पूरी तरह बंद करें
   (सिस्टम ट्रे से भी, घड़ी के पास) और फिर से खोलें।

अंत में इंस्टॉलर उन ऐप की सूची देता है जिन्हें उसने सेट अप किया।

### यह किन ऐप को सेट अप करता है

यह किसी ऐप को केवल तभी सेट अप करता है जब उस ऐप का सेटिंग्स फ़ोल्डर पहले से आपके कंप्यूटर पर हो। Claude Code
केवल तभी सेट अप होता है जब `~/.claude.json` मौजूद हो। Claude Desktop हमेशा सेट अप होता है। हर ऐप को इस फ़ाइल
में एक प्रविष्टि, `fontes`, मिलती है:

| ऐप | फ़ाइल (Mac और Linux) | फ़ाइल (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, और Microsoft Store संस्करण की अपनी प्रति |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, या पुराने संस्करणों पर `~/.codeium/windsurf/mcp_config.json` | `%APPDATA%\devin\mcp_config.json`, या `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code तब सेट अप होता है जब `~/.copilot` या VS Code का अपना सेटिंग्स फ़ोल्डर मौजूद हो।

दो ऐप को एक और चरण चाहिए:

- **Windsurf:** उसे फिर से खोलने के बाद, Cascade में refresh दबाएँ।
- **पुराने VS Code एक्सटेंशन के भीतर Cline:** Fontes को हाथ से जोड़ें (देखें [Cline](#अन्य-ऐप))।

### कुंजियों वाला चरण

इंस्टॉल करने के ठीक बाद, इंस्टॉलर फ़्रांस और US की मुफ़्त कुंजियाँ जोड़ने की पेशकश करता है। उन्हें बाद में जोड़ने
या बदलने के लिए:

- **Mac:** **Fontes Installer** फिर से खोलें और **कुंजियाँ जोड़ें या बदलें** चुनें।
- **Windows:** स्टार्ट मेनू खोलें, फिर **Fontes** → **Add or change keys** चुनें।

टाइपिंग छिपी रहती है। कुंजियाँ हर उस ऐप में जाती हैं जिसमें पहले से Fontes है। इसके बाद ऐप बंद करके फिर से
खोलें। कुंजियाँ कहाँ से मिलेंगी और वे क्या खोलती हैं: [KEYS.md](KEYS.md)।

### बैकअप, दोबारा चलाना और हटाना

इंस्टॉलर केवल `fontes` प्रविष्टि बदलता है। बाकी हर सेटिंग और टिप्पणी जैसी थी वैसी ही रहती है। किसी फ़ाइल को
बदलने से पहले, वह उसके बगल में `<file>.fontes-backup-<date>` नाम से एक प्रति सहेजता है। आपके कुंजियाँ जोड़ने के
बाद बनी प्रतियों में वे कुंजियाँ होती हैं: जिनकी अब आपको ज़रूरत नहीं, उन्हें हटा दें। यह uv भी इंस्टॉल करता है।
इसे दोबारा चलाना सुरक्षित है: यह सेटअप की मरम्मत करता है और और कुछ नहीं बदलता।

Fontes हटाने के लिए, **Fontes Installer** खोलें और **हटाएँ** चुनें (Mac), या **Fontes** को सेटिंग्स → Apps में अनइंस्टॉल करें
(Windows)। यह हर ऐप से `fontes` प्रविष्टि, कुंजियों सहित, हटा देता है। आपकी अन्य सेटिंग्स
और बैकअप प्रतियाँ बनी रहती हैं।

## अपडेट

- **इंस्टॉलर और `.mcpb` फ़ाइल:** आपको कुछ करने की आवश्यकता नहीं है। दिन में एक बार, जब ऐप शुरू होता है, Fontes
  बैकग्राउंड में नए संस्करण की जाँच करता है और उसे तैयार रखता है; अगली बार ऐप शुरू होने पर वह उसका उपयोग
  करता है। यदि कोई अपडेट डाउनलोड नहीं हो सकता या काम नहीं करता, तो Fontes उसी संस्करण का उपयोग करता रहता है
  जो काम करता था।
- **`uvx`:** नया संस्करण उपलब्ध होने पर Fontes आपको अपनी क्षेत्राधिकार-सूची के ऊपर बताता है। हमेशा नवीनतम
  संस्करण चलाने के लिए, `fontes-mcp` के स्थान पर `fontes-mcp@latest` का उपयोग करें।

इसके लिए आपके या आपकी खोजों के बारे में कोई जानकारी कहीं नहीं भेजी जाती।

## गोपनीयता

Fontes डिफ़ॉल्ट रूप से आपके या आपकी खोजों के बारे में कुछ नहीं भेजता। उपयोग-गणना ऑप्ट-इन है, और बग रिपोर्ट केवल
तब भेजी जाती है जब आप उसे देख लें और पुष्टि करें। विवरण: [PRIVACY.md](PRIVACY.md)।

## इसे हटाना

अपने ऐप की MCP सेटिंग्स से `fontes` प्रविष्टि हटाएँ (Claude Code में: `claude mcp remove fontes`), फिर ऐप
बंद करके फिर से खोलें।

## जानने योग्य बातें

Fontes सार्वजनिक स्रोत पढ़ता है, अधिकतर न्यायालयों और सरकार की वेबसाइटें। वह अपने उत्तरों में गैर-आधिकारिक
स्रोतों को चिह्नित करता है। किसी निर्णय या उपबंध पर भरोसा करने से पहले हमेशा स्रोत का लिंक खोलें।

यदि कुछ गलत हो जाए, तो आपने क्या किया और कौन-सी त्रुटि देखी, यह fontesmcp@proton.me पर ईमेल करें।

## इस पर भरोसा करने से पहले

- Fontes एक शोध टूल है, विधिक सलाह नहीं। इसका उपयोग किसी को आपका वकील नहीं बनाता।
- यह "जैसा है" के आधार पर, बिना किसी वारंटी के प्रदान किया जाता है, और जहाँ तक कानून अनुमति देता है, इसके लेखक
  इसके उपयोग के तरीके के लिए उत्तरदायी नहीं हैं। पूरी शर्तें [लाइसेंस](../../../LICENSE) (Apache 2.0) में हैं।
