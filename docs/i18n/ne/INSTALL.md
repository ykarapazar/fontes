> यो मेसिनको सहायताले गरिएको अनुवाद हो। अंग्रेजी संस्करण नै प्रामाणिक हो।

# Fontes इन्स्टल गर्ने

Fontes ले तपाईंको AI एपलाई १२० भन्दा बढी क्षेत्राधिकारमा अदालत र सरकारका वेबसाइटहरूमा अदालतका फैसला र
कानुन लाइभ खोज्न दिन्छ। हरेक नतिजाले मूल स्रोतको लिंक दिन्छ। यो एउटा मानक MCP सर्भर हो, त्यसैले स्थानीय MCP
सर्भर चलाउन सक्ने कुनै पनि एपमा काम गर्छ: Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot),
Gemini CLI, Windsurf, Zed, LM Studio, Cline र अन्य।

आफ्नो एप छान्नुहोस्, त्यसका चरणहरू पालना गर्नुहोस्, त्यसपछि [काम गर्छ कि गर्दैन जाँच्नुहोस्](#काम-गर्छ-कि-गर्दैन-जाँच्ने)।

## Claude Desktop

1. [पछिल्लो रिलिज](https://github.com/ykarapazar/fontes/releases/latest) बाट Fontes को `.mcpb` फाइल
   डाउनलोड गर्नुहोस्।
2. त्यसमा डबल-क्लिक गर्नुहोस्। Claude Desktop ले त्यसलाई खोल्छ।
3. **Install** मा क्लिक गर्नुहोस्।

## Codex

टर्मिनलमा:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI र Codex IDE extension ले यो सेटिङ (`~/.codex/config.toml`) साझा गर्छन्।
तपाईंलाई [uv](#तपाईंलाई-uv-चाहिन्छ) चाहिन्छ।

## Claude Code

टर्मिनलमा:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

तपाईंलाई [uv](#तपाईंलाई-uv-चाहिन्छ) चाहिन्छ।

## अन्य एपहरू

यी प्रत्येकलाई [uv](#तपाईंलाई-uv-चाहिन्छ) चाहिन्छ। प्रविष्टि (entry) थप्नुहोस्, सुरक्षित (save) गर्नुहोस्, त्यसपछि
एप बन्द गरी फेरि खोल्नुहोस्।

**Cursor:** `~/.cursor/mcp.json` (सबै परियोजना) वा `.cursor/mcp.json` (एउटा परियोजना) मा:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** Command Palette बाट **MCP: Add Server** चलाउनुहोस्, **Command (stdio)** छान्नुहोस्,
`uvx fontes-mcp` प्रविष्ट गर्नुहोस् र सर्भरको नाम `fontes` राख्नुहोस्। वा यो `~/.copilot/mcp-config.json` मा
थप्नुहोस्:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

पुराना VS Code सेटअपहरूले `.vscode/mcp.json` प्रयोग गर्छन्, जहाँ सबैभन्दा माथिल्लो तहको key `mcpServers` को
सट्टा `servers` हुन्छ।

**Gemini CLI:** टर्मिनलमा, `gemini mcp add -s user fontes uvx fontes-mcp`। वा यो `~/.gemini/settings.json` मा
थप्नुहोस्:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** आफ्नो settings फाइल खोल्नुहोस् (**zed: open settings file**) र थप्नुहोस्:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** दायाँपट्टिको sidebar मा **Program** ट्याब खोल्नुहोस्, **Install → Edit mcp.json** मा क्लिक
गर्नुहोस्, र थप्नुहोस्:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** **MCP Servers** आइकनमा क्लिक गर्नुहोस्, **Configure** ट्याब खोल्नुहोस्, **Configure MCP Servers** मा
क्लिक गर्नुहोस्, र LM Studio मा जस्तै `mcpServers` प्रविष्टि थप्नुहोस्।

**Claude Desktop, हातले** (`.mcpb` फाइलको सट्टा): उही `mcpServers` प्रविष्टि `claude_desktop_config.json` मा
थप्नुहोस् (macOS: `~/Library/Application Support/Claude/`, Windows: `%APPDATA%\Claude\`)।

**कुनै पनि अन्य MCP एप** (Windsurf र अन्य): त्यसले आफ्ना MCP सर्भरहरू कहाँ राख्छ भन्ने कुरा त्यसकै
documentation मा हुन्छ। धेरैजसोले उही प्रविष्टि लिन्छन्: command `uvx`, argument `fontes`।

एपले `uvx` भेट्न सकेन भने त्यसको पूरा path प्रयोग गर्नुहोस् (macOS र Linux मा `which uvx` ले देखाउँछ)।

## तपाईंलाई uv चाहिन्छ

Codex, Claude Code र अन्य एपहरूले Fontes लाई `uvx` बाट सुरु गर्छन्, जुन **uv** सँगै आउँछ। uv, Astral को एउटा
सानो निःशुल्क टुल हो। यसलाई इन्स्टल गर्न [Astral को गाइड](https://docs.astral.sh/uv/getting-started/installation/)
हेर्नुहोस्, वा चलाउनुहोस्:

- macOS वा Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## कुञ्जीहरू

केही स्रोतहरूलाई निःशुल्क कुञ्जी (key) चाहिन्छ: [KEYS.md](KEYS.md) हेर्नुहोस्।

## काम गर्छ कि गर्दैन जाँच्ने

नयाँ च्याटमा सोध्नुहोस्: *"Fontes ले कुन-कुन क्षेत्राधिकारमा खोज्न सक्छ?"* एपले देशहरूको सूचीसहित जवाफ
दिनुपर्छ। दिएन भने एप एक पटक फेरि बन्द गरी खोल्नुहोस्।

## एक-क्लिक इन्स्टलर (आउँदै छ)

तपाईंका सबै एपहरूमा एकै पटक Fontes सेट अप गर्ने Mac र Windows इन्स्टलर आउँदै छ। यसले Claude Desktop, Codex,
Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio र Cline सेट अप गर्छ। यो
रिलिज भएपछि:

**सुरु गर्नुअघि:** यी प्रत्येक एप पूर्ण रूपमा बन्द गर्नुहोस्। यो Claude Code का लागि सबैभन्दा महत्त्वपूर्ण छ:
चलिरहँदा यसले `~/.claude.json` फेरि लेख्छ र इन्स्टलरले गरेको परिवर्तन उल्टाउन सक्छ। Claude Code बन्द गर्न
सक्नुहुन्न भने त्यसको सट्टा `claude mcp add` बाट Fontes थप्नुहोस् ([Claude Code](#claude-code) हेर्नुहोस्)।

**Mac**

1. डाउनलोड गरिएको **Fontes Installer** फोल्डर खोल्नुहोस्।
2. **Install Fontes.command** मा डबल-क्लिक गर्नुहोस्।
   - तपाईंको Mac ले "cannot be opened because it is from an unidentified developer" भन्यो भने: फाइलमा
     right-click (वा Control-click) गर्नुहोस्, **Open** छान्नुहोस्, अनि फेरि **Open**। यो एक पटक मात्र गर्नुपर्छ।
3. एउटा विन्डो खुल्छ र बेनामी प्रयोग-गणना पठाउने कि नपठाउने सोध्छ; नपठाउन Enter थिच्नुहोस्।
4. यसले अहिले कुञ्जीहरू थप्ने कि नथप्ने सोध्छ। छोड्न Enter थिच्नुहोस्; [कुञ्जीहरूको चरण](#कुञ्जीहरूको-चरण)
   हेर्नुहोस्।
5. यसले **Done** भनेपछि आफ्ना AI एपहरू फेरि खोल्नुहोस्।

**Windows**

1. डाउनलोड गरिएको **Fontes Installer** unzip गर्नुहोस् (right-click → Extract All)।
2. **Install Fontes.cmd** मा डबल-क्लिक गर्नुहोस्।
   - Windows ले "Windows protected your PC" देखायो भने: **More info** मा, अनि **Run anyway** मा क्लिक गर्नुहोस्।
3. बेनामी प्रयोग-गणना पठाउने कि नपठाउने भनी सोधिँदा, नपठाउन Enter थिच्नुहोस्।
4. यसले अहिले कुञ्जीहरू थप्ने कि नथप्ने सोध्छ। छोड्न Enter थिच्नुहोस्; [कुञ्जीहरूको चरण](#कुञ्जीहरूको-चरण)
   हेर्नुहोस्।
5. यसले **Done** भनेपछि आफ्ना AI एपहरू फेरि खोल्नुहोस्। कुनै एप अझै चलिरहेको थियो भने त्यसलाई पूर्ण रूपमा
   बन्द गर्नुहोस् (घडीनजिकको system tray बाट पनि) र फेरि खोल्नुहोस्।

अन्तमा इन्स्टलरले आफूले सेट अप गरेका एपहरूको सूची दिन्छ।

### यसले कुन एपहरू सेट अप गर्छ

कुनै एपको settings फोल्डर तपाईंको कम्प्युटरमा पहिले नै छ भने मात्र यसले त्यो एप सेट अप गर्छ। Claude Code
`~/.claude.json` अवस्थित भएमा मात्र सेट अप हुन्छ। Claude Desktop सधैँ सेट अप हुन्छ। प्रत्येक एपलाई यो फाइलमा
एउटा प्रविष्टि, `fontes`, दिइन्छ:

| एप | फाइल (Mac र Linux) | फाइल (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, र Microsoft Store संस्करणको आफ्नै प्रति |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, वा पुराना संस्करणमा `~/.codeium/windsurf/mcp_config.json` | `%APPDATA%\devin\mcp_config.json`, वा `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

`~/.copilot` वा VS Code को आफ्नै settings फोल्डर अवस्थित भएमा VS Code सेट अप हुन्छ।

दुई एपलाई अर्को एउटा चरण चाहिन्छ:

- **Windsurf:** यसलाई फेरि खोलेपछि Cascade मा refresh थिच्नुहोस्।
- **पुरानो VS Code extension भित्रको Cline:** Fontes हातले थप्नुहोस् ([Cline](#अन्य-एपहरू) हेर्नुहोस्)।

### कुञ्जीहरूको चरण

इन्स्टल गरेलगत्तै, इन्स्टलरले फ्रान्स र US का निःशुल्क कुञ्जीहरू थप्न प्रस्ताव गर्छ। तिनलाई पछि थप्न वा बदल्न:

- **Mac:** इन्स्टलर फोल्डरमा **Add or change keys.command** मा डबल-क्लिक गर्नुहोस्, वा Fontes Installer एप
  फेरि खोलेर **Add or change keys** छान्नुहोस्।
- **Windows:** इन्स्टलर फोल्डरमा **Add or change keys.cmd** मा डबल-क्लिक गर्नुहोस्।

टाइप गरेको देखिँदैन। कुञ्जीहरू Fontes पहिले नै भएका हरेक एपमा जान्छन्। त्यसपछि एपहरू बन्द गरी फेरि
खोल्नुहोस्। कुञ्जीहरू कहाँबाट पाउने र तिनले के खोल्छन्: [KEYS.md](KEYS.md)।

### ब्याकअप, फेरि चलाउने र हटाउने

इन्स्टलरले `fontes` प्रविष्टि मात्र परिवर्तन गर्छ। अरू हरेक सेटिङ र comment जस्ताको तस्तै रहन्छन्। कुनै फाइल
परिवर्तन गर्नुअघि, यसले त्यसको छेउमा `<file>.fontes-backup-<date>` नामको एउटा प्रति सुरक्षित गर्छ। तपाईंले
कुञ्जीहरू थपेपछि बनेका प्रतिहरूमा ती कुञ्जीहरू हुन्छन्: अब नचाहिने प्रतिहरू मेटाउनुहोस्। यसले uv पनि इन्स्टल
गर्छ। यसलाई फेरि चलाउनु सुरक्षित छ: यसले सेटअप मर्मत गर्छ र अरू केही परिवर्तन गर्दैन।

Fontes हटाउन, **Uninstall Fontes.command** (Mac) वा **Uninstall Fontes.cmd** (Windows) मा डबल-क्लिक
गर्नुहोस्। यसले हरेक एपबाट कुञ्जीसहित `fontes` प्रविष्टि हटाउँछ। तपाईंका अरू सेटिङ र ब्याकअप प्रतिहरू रहन्छन्।

## अद्यावधिक

- **इन्स्टलर र `.mcpb` फाइल:** तपाईंले केही गर्नुपर्दैन। दिनको एक पटक, एप सुरु हुँदा, Fontes ले पृष्ठभूमिमा
  नयाँ संस्करण छ कि छैन जाँच्छ र त्यसलाई तयार राख्छ; अर्को पटक एप सुरु हुँदा त्यही प्रयोग हुन्छ। अद्यावधिक
  डाउनलोड हुन सकेन वा काम गरेन भने, Fontes ले काम गरेको संस्करण नै प्रयोग गरिरहन्छ।
- **`uvx`:** नयाँ संस्करण उपलब्ध भएमा Fontes ले आफ्नो क्षेत्राधिकार सूचीको सबैभन्दा माथि तपाईंलाई बताउँछ। सधैँ
  सबैभन्दा नयाँ संस्करण चलाउन, `fontes-mcp` को सट्टा `fontes-mcp@latest` प्रयोग गर्नुहोस्।

यसका लागि तपाईं वा तपाईंका खोजहरूबारे कुनै जानकारी कतै पठाइँदैन।

## गोपनीयता

Fontes ले पूर्वनिर्धारित रूपमा तपाईं वा तपाईंका खोजहरूबारे केही पनि पठाउँदैन। प्रयोग-गणना opt-in हो, र त्रुटि
रिपोर्ट तपाईंले हेरेर पुष्टि गरेपछि मात्र पठाइन्छ। विवरण: [PRIVACY.md](PRIVACY.md)।

## हटाउने

आफ्नो एपको MCP सेटिङबाट `fontes` प्रविष्टि हटाउनुहोस् (Claude Code मा: `claude mcp remove fontes`), त्यसपछि
एप बन्द गरी फेरि खोल्नुहोस्।

## थाहा पाउनुपर्ने कुरा

Fontes ले सार्वजनिक स्रोतहरू पढ्छ, प्रायः अदालत र सरकारका वेबसाइटहरू। यसले आफ्ना उत्तरहरूमा अनाधिकारिक
स्रोतहरूलाई चिन्ह लगाउँछ। कुनै फैसला वा दफामा भर पर्नुअघि सधैँ स्रोतको लिंक खोल्नुहोस्।

केही गडबड भयो भने, तपाईंले के गर्नुभयो र कुन त्रुटि देख्नुभयो fontesmcp@proton.me मा इमेल गर्नुहोस्।

## भर पर्नुअघि

- Fontes अनुसन्धान टुल हो, कानुनी सल्लाह होइन। यसको प्रयोगले कसैलाई पनि तपाईंको कानुन व्यवसायी बनाउँदैन।
- यो "जस्तो छ त्यस्तै" ("as is") उपलब्ध गराइएको हो, कुनै वारेन्टीबिना, र कानुनले अनुमति दिएसम्म यसका लेखकहरू
  यसको प्रयोगका लागि उत्तरदायी हुँदैनन्। पूरा सर्तहरू [इजाजतपत्र](../../../LICENSE) (Apache 2.0) मा छन्।
