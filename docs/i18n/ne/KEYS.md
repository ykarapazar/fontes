> यो मेसिनको सहायताले गरिएको अनुवाद हो। अंग्रेजी संस्करण नै प्रामाणिक हो।

# API कुञ्जीहरू

Fontes का लगभग हरेक स्रोत कुञ्जी (key) बिना काम गर्छन्। तीनलाई निःशुल्क कुञ्जी चाहिन्छ:

| कुञ्जी | के खोल्छ | यो बिना |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | फ्रान्स: Judilibre (अदालतका फैसला) र Légifrance (कानुन) | फ्रान्स बन्द रहन्छ। `list_jurisdictions` ले यसलाई निष्क्रिय देखाउँछ। |
| `WLM_US_GOVINFO_KEY` | संयुक्त राज्य अमेरिका: govinfo खोज (संघीय अदालतका रायहरू (opinions), Statutes at Large, public laws) | Fontes ले साझा `DEMO_KEY` प्रयोग गर्छ: प्रति IP ठेगाना दिनमा करिब १० खोज। थाहा भएको फैसला खोल्न र US Code का लागि कुञ्जी चाहिँदैन। |
| `WLM_US_COURTLISTENER_KEY` | अमेरिकी राज्य अदालतहरू (`us-states`): सबै ५० राज्य र DC का सर्वोच्च र पुनरावेदन अदालतका रायहरू (opinions), CourtListener बाट | अमेरिकी राज्य अदालतका नजिर बन्द रहन्छन्। `list_jurisdictions` ले यसलाई निष्क्रिय देखाउँछ। |

कुञ्जीहरू ऐच्छिक हुन्। तपाईं तिनलाई पछि थप्न सक्नुहुन्छ।

## कुञ्जी थप्ने

**इन्स्टलरबाट।** Fontes सेट अप भएपछि, इन्स्टलरले कुञ्जीहरू थप्न प्रस्ताव गर्छ। Mac मा, **कुञ्जीहरू थप्नुहोस्** मा
क्लिक गर्नुहोस्, वा छोड्न **सकियो** मा; Windows मा, प्रश्नको जवाफ दिनुहोस् (छोड्न Enter थिच्नुहोस्)। पछि कुञ्जीहरू थप्न वा बदल्न, **Add or change keys** चलाउनुहोस्:

- Mac: Fontes Installer एप फेरि खोलेर **कुञ्जीहरू थप्नुहोस् वा बदल्नुहोस्** छान्नुहोस्।
- Windows: Start menu खोल्नुहोस्, त्यसपछि **Fontes** → **कुञ्जीहरू थप्नुहोस् वा बदल्नुहोस्** छान्नुहोस्।

टाइप गरेको देखिँदैन। प्रत्येक कुञ्जीका लागि: त्यसलाई टाँस्नुहोस्, भइरहेकै राख्न Enter थिच्नुहोस्, वा हटाउन `-`
टाइप गर्नुहोस्। कुञ्जीहरू Fontes पहिले नै भएका हरेक एपमा जान्छन्।

**Claude Desktop extension (.mcpb) बाट।** Claude > Settings > Extensions > Fontes खोल्नुहोस् र फिल्डहरू भर्नुहोस्।
ती सबै ऐच्छिक हुन्।

**हातले।** आफ्नो एपको MCP config मा `fontes` प्रविष्टिको `env` block मा variables थप्नुहोस्:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

कुनै पनि परिवर्तनपछि एप फेरि सुरु गर्नुहोस्।

## फ्रान्स: PISTE (निःशुल्क)

1. [piste.gouv.fr](https://piste.gouv.fr) मा खाता बनाउनुहोस्। यसको अर्थ PISTE का सर्तहरू (CGU) स्वीकार गर्नु हो।
2. API > **Consentement CGU API** मा जानुहोस्। **JUDILIBRE** र **Légifrance** (production) का सर्तहरू स्वीकार
   गर्नुहोस्।
3. एउटा **production application** बनाउनुहोस्। तपाईंका लागि बनाइएको `APP_SANDBOX` production मा पुग्न सक्दैन।
   "Modifier l'application" अन्तर्गत **JUDILIBRE (production)** र **Légifrance (production)** मा चिन्ह लगाउनुहोस्,
   अनि लागू (apply) गर्नुहोस्।
4. app को **Authentification** ट्याब खोल्नुहोस्। `client_id` र `client_secret` कपी गर्नुहोस्।
5. **Add or change keys** चलाउनुहोस् र तिनलाई टाँस्नुहोस्।

सर्तहरू, छोटकरीमा:

- डेटा: Licence Ouverte / Etalab 2.0। श्रेय (attribution) सहित, व्यावसायिक पुनः प्रयोगसमेत, पुनः प्रयोग गर्न
  अनुमति छ।
- आफ्ना credentials प्रकाशित वा साझा नगर्नुहोस्। ती चुहिए भने PISTE लाई जानकारी दिनुहोस्।
- Légifrance API एउटा beta सेवा हो। यो निलम्बन हुन सक्छ, र यसमा कोटा (प्रति सेकेन्ड, मिनेट र दिन) छन्।
- Légifrance का पाठहरू प्रामाणिक संस्करण होइनन्। हस्ताक्षरित Journal officiel PDF मात्र प्रामाणिक हो।
- Judilibre: न्यायाधीश वा अदालतका कर्मचारी (clerks) का नाम तिनको कामको मूल्याङ्कन, तुलना वा पूर्वानुमान गर्न
  प्रयोग नगर्नुहोस् (Code de l'organisation judiciaire art. L111-13; फौजदारी कसुर)।
- Judilibre: GDPR पालना गर्नुहोस्। पक्षहरूलाई पुनः पहिचान गर्ने प्रयास नगर्नुहोस्।

तपाईंका कोटाहरू PISTE मा API Sélectionnées > Actions > Consulter les quotas अन्तर्गत छन्।

## संयुक्त राज्य अमेरिका: api.data.gov (निःशुल्क)

1. [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (कुञ्जी स्क्रिनमै देखाइन्छ) वा
   [api.data.gov/signup](https://api.data.gov/signup/) (कुञ्जी तपाईंलाई इमेल गरिन्छ) मा जानुहोस्।
2. आफ्नो नाम र इमेल प्रविष्ट गर्नुहोस्। "how will you use it" फिल्ड ऐच्छिक हो।
3. ४० अक्षरको कुञ्जी कपी गर्नुहोस्।
4. **Add or change keys** चलाउनुहोस् र त्यसलाई US कुञ्जीका रूपमा टाँस्नुहोस्।

सर्तहरू, छोटकरीमा:

- आफ्नै कुञ्जीसहित, govinfo ले घण्टामा ३६,००० अनुरोधसम्म अनुमति दिन्छ।
- हामीले API-विशेष सेवा-सर्तहरू भेटेनौँ (api.data.gov/terms/ अवस्थित छैन)। प्रमाणित गरिएको छैन।
  [govinfo का नीतिहरू](https://www.govinfo.gov/about/policies) र
  [data.gov गोपनीयता नीति](https://data.gov/privacy-policy/) हेर्नुहोस्।
- कुञ्जी आफूसँग मात्र राख्नुहोस्।

## अमेरिकी राज्य अदालतहरू: CourtListener (निःशुल्क)

CourtListener [Free Law Project](https://free.law) ले चलाउँछ, जुन एक गैरनाफामुखी संस्था हो र २०१० देखि अमेरिकी अदालतका रायहरू (opinions) संकलन गर्दै आएको छ र तिनलाई सबैका लागि निःशुल्क उपलब्ध गराउँछ। यसको आफ्नै गणनाअनुसार यसमा नौ मिलियनभन्दा बढी फैसला छन्। यो आधिकारिक स्रोत होइन: अदालतहरूले आफ्ना रायहरू आफैँ प्रकाशित गर्छन्, र CourtListener ले तिनलाई अदालतका वेबसाइट र स्क्यान गरिएका कानुनी प्रतिवेदनहरूबाट सङ्कलन गर्छ। यसबाट आएको Fontes को हरेक उत्तरले यो भन्छ। Fontes को Free Law Project सँग कुनै सम्बन्ध छैन।

1. [courtlistener.com](https://www.courtlistener.com/sign-in/) मा निःशुल्क खाता बनाउनुहोस्।
2. आफ्नो प्रोफाइल खोल्नुहोस् र आफ्नो API token कपी गर्नुहोस्।
3. **Add or change keys** चलाउनुहोस् र त्यसलाई CourtListener कुञ्जीका रूपमा टाँस्नुहोस्।

सर्तहरू, छोटकरीमा ([पूर्ण सर्तहरू](https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies)):

- token तपाईंको मात्र हो: यसलाई साझा नगर्नुहोस्, अरूसँग मिलाएर नराख्नुहोस् वा फेरि नबेच्नुहोस्, र धेरै खाता नचलाउनुहोस्।
- AI एपले तपाईंको token लाई के गर्छ भन्नेमा तपाईं जिम्मेवार हुनुहुन्छ।
- तिनीहरूको डाटामाथि AI ले गरेको विश्लेषणलाई Free Law Project ले तयार गरेको, समर्थन गरेको वा जाँचेको भनी नदेखाउनुहोस्।
- निःशुल्क खाताले प्रति मिनेट ५, प्रति घण्टा ५० र प्रति दिन १२५ अनुरोध अनुमति दिन्छ। एउटा खोज एउटा अनुरोध हो; एउटा फैसला खोल्नु दुई अनुरोध हो। Free Law Project को सदस्यताले सीमा बढाउँछ।
- CourtListener ले शुद्धताको ग्यारेन्टी दिँदैन। कुनै राय (opinion) मा भर पर्नुअघि अदालतको प्रतिसँग जाँच गर्नुहोस्।

## कुञ्जीहरू कहाँ भण्डारण हुन्छन्

- **इन्स्टलर वा हातले:** प्रत्येक एपको MCP config फाइलमा, `fontes` प्रविष्टिको `env` block मा सादा पाठ (plain
  text) का रूपमा। तपाईंका user फाइलहरू पढ्न सक्ने जो कोहीले कुञ्जीहरू पढ्न सक्छ।
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` वा `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Claude Desktop extension (.mcpb):** Claude ले यी फिल्डहरू आफ्नो सेटिङमा राख्छ र तपाईंको प्रणालीको सुरक्षित
  भण्डारण (Mac मा Keychain, Windows मा Credential Manager) ले तिनलाई सुरक्षित गर्छ।

हरेक परिवर्तनअघि, इन्स्टलरले config फाइलको एउटा प्रति त्यसको छेउमा सुरक्षित गर्छ
(`<file>.fontes-backup-<time>`)। तपाईंले कुञ्जीहरू थपेपछि बनेका प्रतिहरूमा कुञ्जीहरू पनि हुन्छन्। नचाहिने पुराना
प्रतिहरू मेटाउनुहोस्।

## कुञ्जी बदल्ने वा हटाउने

- **Add or change keys** चलाउनुहोस्। बदल्न नयाँ कुञ्जी टाँस्नुहोस्, वा हटाउन `-` टाइप गर्नुहोस्।
- वा `env` block हातले सम्पादन गरी एप फेरि सुरु गर्नुहोस्।
- Fontes अनइन्स्टल गर्दा कुञ्जीसहित त्यसको पूरै प्रविष्टि हट्छ। यसले ब्याकअप प्रतिहरू मेटाउँदैन।
- कुनै कुञ्जी चुहियो भने, स्रोतमा पनि त्यसलाई बदल्नुहोस्: PISTE मा, आफ्नो app का लागि नयाँ credentials बनाउनुहोस्;
  api.data.gov का लागि, नयाँ कुञ्जीका लागि sign up गर्नुहोस्।

## तपाईंले देख्न सक्ने सन्देशहरू

| सन्देश | अर्थ |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | फ्रान्सको कुञ्जी छैन। एउटा थप्नुहोस्। |
| `Inactive: needs a free PISTE account. ...` (`list_jurisdictions` मा) | उही। |
| `PISTE refused the client credentials ...` | ID वा secret गलत छ वा अब मान्य छैन। Authentification ट्याबबाट दुवै फेरि कपी गर्नुहोस्। |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | तपाईंको app त्यो API मा सदस्य छैन, वा तपाईंले त्यसका सर्तहरू स्वीकार गर्नुभएको छैन। चरण २ र ३ हेर्नुहोस्। |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | US कुञ्जी छैन। खोज दिनमा केही कलका लागि काम गर्छ। |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | demo key सकियो। आफ्नै कुञ्जी थप्नुहोस्। |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | कुञ्जी गलत छ, वा इमेलबाट अझै पुष्टि गरिएको छैन। |

खाली मानलाई कुञ्जी नभएको मानिन्छ।

## अनुमतिहरू (WLM_PERMITTED)

यो API कुञ्जी होइन, र इन्स्टलरले यसलाई सेट गर्दैन। **त्यो अनुमति तपाईं आफैँसँग छ भने मात्र यसलाई सेट
गर्नुहोस्।**

केही स्रोतहरू पूर्वनिर्धारित रूपमा बन्द छन्, किनकि तिनका सर्तहरू वा robots.txt ले अनुमतिबिना स्वचालित प्रयोग
निषेध गर्छन्। तपाईंसँग प्रकाशकको अनुमति छ भने, `env` block मा `WLM_PERMITTED` मा त्यसको कोड, अल्पविरामले छुट्याएर,
थपेर स्रोत चालु गर्नुहोस्: `"WLM_PERMITTED": "in,de"`।

| कोड | स्रोत |
|---|---|
| `az` | अजरबैजान: e-qanun.az (न्याय मन्त्रालय) |
| `bh` | बहराइन: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | कोलम्बिया: Función Pública, Gestor Normativo (एकीकृत कानुन) |
| `de` | जर्मनी: NeuRIS (संघीय कानुनी सूचना पोर्टल, परीक्षण सेवा) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | ग्रीस: National Printing Office, Government Gazette खोज (search.et.gr) |
| `mu` | मरिसस: Supreme Court (supremecourt.govmu.org) |
| `sg` | सिंगापुर: अदालतका फैसलाहरू (elitigation.sg) |

अनुमतिबिना, Fontes ले भन्छ: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
