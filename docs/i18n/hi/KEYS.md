> यह मशीन की सहायता से किया गया अनुवाद है। अंग्रेज़ी संस्करण ही प्रामाणिक है।

# API कुंजियाँ

Fontes के लगभग सभी स्रोत बिना कुंजी के काम करते हैं। तीन को एक मुफ़्त कुंजी चाहिए:

| कुंजी | क्या खोलती है | इसके बिना |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | फ़्रांस: Judilibre (न्यायालयों के निर्णय) और Légifrance (विधान) | फ़्रांस बंद रहता है। `list_jurisdictions` उसे निष्क्रिय दिखाता है। |
| `WLM_US_GOVINFO_KEY` | संयुक्त राज्य अमेरिका: govinfo खोज (संघीय न्यायालयों की opinions, Statutes at Large, public laws) | Fontes साझा `DEMO_KEY` का उपयोग करता है: प्रति IP पता दिन में लगभग 10 खोजें। किसी ज्ञात निर्णय को खोलने और US Code के लिए कुंजी की आवश्यकता नहीं। |
| `WLM_US_COURTLISTENER_KEY` | अमेरिकी राज्यों के न्यायालय (`us-states`): सभी 50 राज्यों और DC के सर्वोच्च और अपीलीय न्यायालयों की opinions, CourtListener से | अमेरिकी राज्यों का केस लॉ बंद रहता है। `list_jurisdictions` उसे निष्क्रिय दिखाता है। |

कुंजियाँ वैकल्पिक हैं। आप इन्हें बाद में जोड़ सकते हैं।

## कुंजी जोड़ना

**इंस्टॉलर से।** Fontes सेट अप हो जाने के बाद, इंस्टॉलर कुंजियाँ जोड़ने की पेशकश करता है। Mac पर,
**कुंजियाँ जोड़ें** पर क्लिक करें, या छोड़ने के लिए **हो गया** पर; Windows पर, प्रश्न का उत्तर दें (छोड़ने के लिए
Enter दबाएँ)। बाद में कुंजियाँ जोड़ने या बदलने के लिए, **Add or change keys** चलाएँ:

- Mac: Fontes Installer ऐप फिर से खोलें और **कुंजियाँ जोड़ें या बदलें** चुनें।
- Windows: Start menu खोलें, फिर **Fontes** → **कुंजियाँ जोड़ें या बदलें**।

टाइपिंग छिपी रहती है। हर कुंजी के लिए: उसे चिपकाएँ, जो मौजूद है उसे रखने के लिए Enter दबाएँ, या उसे हटाने के
लिए `-` टाइप करें। कुंजियाँ हर उस ऐप में जाती हैं जिसमें पहले से Fontes है।

**Claude Desktop एक्सटेंशन (.mcpb) से।** Claude > Settings > Extensions > Fontes खोलें और फ़ील्ड भरें। वे सभी
वैकल्पिक हैं।

**हाथ से।** वेरिएबल को अपने ऐप के MCP कॉन्फ़िग में `fontes` प्रविष्टि के `env` ब्लॉक में जोड़ें:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

किसी भी बदलाव के बाद ऐप को पुनः आरंभ करें।

## फ़्रांस: PISTE (मुफ़्त)

1. [piste.gouv.fr](https://piste.gouv.fr) पर खाता बनाएँ। इसका अर्थ है PISTE की शर्तें (CGU) स्वीकार करना।
2. API > **Consentement CGU API** पर जाएँ। **JUDILIBRE** और **Légifrance** (production) की शर्तें स्वीकार करें।
3. एक **production application** बनाएँ। आपके लिए बनाया गया `APP_SANDBOX` production तक नहीं पहुँच सकता।
   "Modifier l'application" के अंतर्गत **JUDILIBRE (production)** और **Légifrance (production)** पर टिक करें,
   फिर लागू करें।
4. ऐप का **Authentification** टैब खोलें। `client_id` और `client_secret` कॉपी करें।
5. **Add or change keys** चलाएँ और उन्हें चिपकाएँ।

शर्तें, संक्षेप में:

- डेटा: Licence Ouverte / Etalab 2.0। श्रेय के साथ पुनः उपयोग, वाणिज्यिक पुनः उपयोग सहित, अनुमत है।
- अपने क्रेडेंशियल प्रकाशित या साझा न करें। यदि वे लीक हो जाएँ तो PISTE को बताएँ।
- Légifrance API एक बीटा सेवा है। इसे निलंबित किया जा सकता है, और इसके कोटा हैं (प्रति सेकंड, मिनट और दिन)।
- Légifrance के पाठ प्रामाणिक संस्करण नहीं हैं। केवल हस्ताक्षरित Journal officiel PDF प्रामाणिक है।
- Judilibre: न्यायाधीशों या लिपिकों के नामों का उपयोग उनके काम का मूल्यांकन, तुलना या पूर्वानुमान करने के लिए न
  करें (Code de l'organisation judiciaire art. L111-13; एक आपराधिक अपराध)।
- Judilibre: GDPR का पालन करें। पक्षकारों की फिर से पहचान करने का प्रयास न करें।

आपके कोटा PISTE पर API Sélectionnées > Actions > Consulter les quotas के अंतर्गत हैं।

## संयुक्त राज्य अमेरिका: api.data.gov (मुफ़्त)

1. [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) पर जाएँ (कुंजी स्क्रीन पर दिखाई जाती है)
   या [api.data.gov/signup](https://api.data.gov/signup/) पर (कुंजी आपको ईमेल की जाती है)।
2. अपना नाम और ईमेल दर्ज करें। "how will you use it" फ़ील्ड वैकल्पिक है।
3. 40 अक्षरों वाली कुंजी कॉपी करें।
4. **Add or change keys** चलाएँ और उसे US कुंजी के रूप में चिपकाएँ।

शर्तें, संक्षेप में:

- आपकी अपनी कुंजी के साथ, govinfo प्रति घंटे 36,000 अनुरोधों तक की अनुमति देता है।
- हमें API-विशिष्ट सेवा की कोई शर्तें नहीं मिलीं (api.data.gov/terms/ मौजूद नहीं है)। असत्यापित।
  देखें [govinfo की नीतियाँ](https://www.govinfo.gov/about/policies) और
  [data.gov की गोपनीयता नीति](https://data.gov/privacy-policy/)।
- कुंजी अपने तक ही रखें।

## अमेरिकी राज्यों के न्यायालय: CourtListener (मुफ़्त)

CourtListener को [Free Law Project](https://free.law) चलाता है, जो एक गैर-लाभकारी संस्था है और 2010 से अमेरिकी न्यायालयों की opinions एकत्र कर रही है और उन्हें सबके लिए मुफ़्त उपलब्ध कराती है। उसकी अपनी गिनती के अनुसार उसके पास नब्बे लाख से अधिक निर्णय हैं। यह कोई आधिकारिक स्रोत नहीं है: न्यायालय अपनी opinions स्वयं प्रकाशित करते हैं, और CourtListener उन्हें न्यायालयों की वेबसाइटों और स्कैन की गई विधि रिपोर्टों से एकत्र करता है। उससे आने वाला Fontes का हर उत्तर यह बताता है। Fontes का Free Law Project से कोई संबंध नहीं है।

1. [courtlistener.com](https://www.courtlistener.com/sign-in/) पर एक मुफ़्त खाता बनाएँ।
2. अपनी प्रोफ़ाइल खोलें और अपना API टोकन कॉपी करें।
3. **Add or change keys** चलाएँ और उसे CourtListener कुंजी के रूप में चिपकाएँ।

शर्तें, संक्षेप में ([पूरी शर्तें](https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies)):

- टोकन केवल आपका है: उसे साझा न करें, दूसरों के साथ मिलाकर इस्तेमाल न करें और न बेचें, और कई खातों का उपयोग न करें।
- आपके टोकन से कोई AI ऐप जो कुछ करता है, उसके लिए आप ज़िम्मेदार हैं।
- उनके डेटा का किसी AI द्वारा किया गया विश्लेषण ऐसे प्रस्तुत न करें मानो वह Free Law Project द्वारा तैयार, समर्थित या जाँचा गया हो।
- एक मुफ़्त खाते में प्रति मिनट 5, प्रति घंटे 50 और प्रति दिन 125 अनुरोधों की अनुमति है। एक खोज एक अनुरोध है; किसी निर्णय को खोलना दो। Free Law Project की सदस्यता सीमाएँ बढ़ा देती है।
- CourtListener सटीकता की गारंटी नहीं देता। किसी opinion पर भरोसा करने से पहले उसे न्यायालय की प्रति से मिला लें।

## कुंजियाँ कहाँ संग्रहीत होती हैं

- **इंस्टॉलर से या हाथ से:** हर ऐप की MCP कॉन्फ़िग फ़ाइल में, `fontes` प्रविष्टि के `env` ब्लॉक में, सादे पाठ
  के रूप में। जो कोई भी आपकी उपयोगकर्ता फ़ाइलें पढ़ सकता है, वह कुंजियाँ पढ़ सकता है।
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` या `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Claude Desktop एक्सटेंशन (.mcpb):** Claude इन फ़ील्ड को अपनी सेटिंग्स में रखता है और उन्हें आपके सिस्टम के
  सुरक्षित भंडारण (Mac पर Keychain, Windows पर Credential Manager) से सुरक्षित करता है।

हर बदलाव से पहले, इंस्टॉलर कॉन्फ़िग फ़ाइल की एक प्रति उसके बगल में सहेजता है
(`<file>.fontes-backup-<time>`)। आपके कुंजियाँ जोड़ने के बाद बनी प्रतियों में भी कुंजियाँ होती हैं। जिन पुरानी
प्रतियों की आपको आवश्यकता नहीं, उन्हें हटा दें।

## कुंजी बदलना या हटाना

- **Add or change keys** चलाएँ। कुंजी बदलने के लिए नई कुंजी चिपकाएँ, या उसे हटाने के लिए `-` टाइप करें।
- या `env` ब्लॉक को हाथ से संपादित करें और ऐप को पुनः आरंभ करें।
- Fontes को अनइंस्टॉल करने से उसकी पूरी प्रविष्टि, कुंजियों सहित, हट जाती है। यह बैकअप प्रतियाँ नहीं हटाता।
- यदि कोई कुंजी लीक हो गई हो, तो उसे स्रोत पर भी बदलें: PISTE पर, अपने ऐप के लिए नए क्रेडेंशियल बनाएँ;
  api.data.gov के लिए, नई कुंजी हेतु साइन अप करें।

## संदेश जो आपको दिख सकते हैं

| संदेश | अर्थ |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | फ़्रांस की कोई कुंजी नहीं। एक जोड़ें। |
| `Inactive: needs a free PISTE account. ...` (`list_jurisdictions` में) | वही। |
| `PISTE refused the client credentials ...` | ID या secret गलत है या अब मान्य नहीं है। Authentification टैब से दोनों फिर से कॉपी करें। |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | आपके ऐप की उस API की सदस्यता नहीं है, या आपने उसकी शर्तें स्वीकार नहीं की हैं। चरण 2 और 3 देखें। |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | US की कोई कुंजी नहीं। खोज दिन में कुछ कॉल के लिए काम करती है। |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | डेमो कुंजी समाप्त हो गई है। अपनी कुंजी जोड़ें। |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | कुंजी गलत है, या ईमेल से अभी पुष्टि नहीं हुई है। |

खाली मान को कोई कुंजी नहीं माना जाता।

## अनुमतियाँ (WLM_PERMITTED)

यह API कुंजी नहीं है, और इंस्टॉलर इसे सेट नहीं करता। **इसे केवल तभी सेट करें जब वह अनुमति स्वयं आपके पास हो।**

कुछ स्रोत डिफ़ॉल्ट रूप से बंद हैं क्योंकि उनकी शर्तें या robots.txt बिना अनुमति स्वचालित उपयोग वर्जित करते हैं।
यदि आपके पास प्रकाशक की अनुमति है, तो किसी स्रोत का कोड `env` ब्लॉक में `WLM_PERMITTED` में, अल्पविराम से अलग
करके, जोड़कर उसे चालू करें: `"WLM_PERMITTED": "in,de"`।

| कोड | स्रोत |
|---|---|
| `az` | अज़रबैजान: e-qanun.az (Ministry of Justice) |
| `bh` | बहरीन: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | कोलंबिया: Función Pública, Gestor Normativo (समेकित विधान) |
| `de` | जर्मनी: NeuRIS (संघीय विधिक सूचना पोर्टल, परीक्षण सेवा) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | यूनान: National Printing Office, Government Gazette search (search.et.gr) |
| `in` | भारत: India Code (indiacode.gov.in) |
| `mu` | मॉरीशस: Supreme Court (supremecourt.govmu.org) |
| `sg` | सिंगापुर: न्यायालयों के निर्णय (elitigation.sg) |

अनुमति के बिना, Fontes कहता है: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
