> এটি যন্ত্রের সহায়তায় করা অনুবাদ। ইংরেজি সংস্করণই প্রামাণ্য।

# API কী

Fontes-এর প্রায় প্রতিটি উৎস কোনো কী (key) ছাড়াই কাজ করে। দুটির জন্য বিনামূল্যের একটি কী প্রয়োজন:

| কী | যা খুলে দেয় | কী ছাড়া |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | ফ্রান্স: Judilibre (আদালতের রায়) ও Légifrance (আইন ও বিধিমালা) | ফ্রান্স বন্ধ থাকে। `list_jurisdictions` এটিকে নিষ্ক্রিয় দেখায়। |
| `WLM_US_GOVINFO_KEY` | যুক্তরাষ্ট্র: govinfo অনুসন্ধান (ফেডারেল আদালতের মতামত, Statutes at Large, public laws) | Fontes শেয়ার করা `DEMO_KEY` ব্যবহার করে: প্রতি IP ঠিকানায় দিনে প্রায় ১০টি অনুসন্ধান। জানা কোনো রায় খোলা এবং US Code-এর জন্য কোনো কী লাগে না। |

কী ঐচ্ছিক। আপনি পরে এগুলো যোগ করতে পারেন।

## কী যোগ করা

**ইনস্টলার দিয়ে।** Fontes সেট আপ হয়ে গেলে ইনস্টলার কী যোগ করার প্রস্তাব দেয়। Mac-এ **কী যোগ করুন**-এ ক্লিক
করুন, অথবা বাদ দিতে **সম্পন্ন**-এ; Windows-এ প্রশ্নের উত্তর দিন (বাদ দিতে Enter চাপুন)। পরে কী যোগ বা পরিবর্তন
করতে **কী যোগ বা পরিবর্তন করুন** চালান:

- Mac: Fontes Installer অ্যাপটি আবার খুলে **কী যোগ বা পরিবর্তন করুন** বেছে নিন।
- Windows: Start menu খুলুন, তারপর **Fontes** → **কী যোগ বা পরিবর্তন করুন**।

টাইপ করা লেখা দেখা যায় না। প্রতিটি কী-র জন্য: সেটি পেস্ট করুন, যা আছে তা রাখতে Enter চাপুন, অথবা সরাতে `-` টাইপ
করুন। কীগুলো এমন প্রতিটি অ্যাপে যায় যেটিতে আগে থেকেই Fontes আছে।

**Claude Desktop এক্সটেনশন (.mcpb) দিয়ে।** Claude > Settings > Extensions > Fontes খুলুন এবং ঘরগুলো পূরণ
করুন। সবগুলোই ঐচ্ছিক।

**হাতে।** আপনার অ্যাপের MCP কনফিগে `fontes` এন্ট্রির `env` ব্লকে ভেরিয়েবলগুলো যোগ করুন:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

যেকোনো পরিবর্তনের পর অ্যাপটি রিস্টার্ট করুন।

## ফ্রান্স: PISTE (বিনামূল্যে)

1. [piste.gouv.fr](https://piste.gouv.fr)-এ একটি অ্যাকাউন্ট তৈরি করুন। এর অর্থ PISTE-এর শর্তাবলি (CGU) গ্রহণ করা।
2. API > **Consentement CGU API**-তে যান। **JUDILIBRE** ও **Légifrance** (production)-এর শর্তাবলি গ্রহণ করুন।
3. একটি **production application** তৈরি করুন। আপনার জন্য তৈরি করা `APP_SANDBOX` production-এ পৌঁছাতে পারে না।
   "Modifier l'application"-এর অধীনে **JUDILIBRE (production)** ও **Légifrance (production)**-এ টিক দিন, তারপর
   প্রয়োগ (apply) করুন।
4. অ্যাপটির **Authentification** ট্যাব খুলুন। `client_id` ও `client_secret` কপি করুন।
5. **Add or change keys** চালান এবং সেগুলো পেস্ট করুন।

শর্তাবলি, সংক্ষেপে:

- ডেটা: Licence Ouverte / Etalab 2.0। স্বীকৃতি (attribution) দিলে পুনর্ব্যবহার, বাণিজ্যিক পুনর্ব্যবহারসহ, অনুমোদিত।
- আপনার ক্রেডেনশিয়াল প্রকাশ বা শেয়ার করবেন না। সেগুলো ফাঁস হলে PISTE-কে জানান।
- Légifrance API একটি বেটা সেবা। এটি স্থগিত হতে পারে, এবং এর কোটা আছে (প্রতি সেকেন্ড, মিনিট ও দিনে)।
- Légifrance-এর পাঠ প্রামাণ্য সংস্করণ নয়। কেবল স্বাক্ষরিত Journal officiel PDF-ই প্রামাণ্য।
- Judilibre: বিচারক বা ক্লার্কদের কাজ মূল্যায়ন, তুলনা বা পূর্বাভাস করতে তাদের নাম ব্যবহার করবেন না
  (Code de l'organisation judiciaire art. L111-13; একটি ফৌজদারি অপরাধ)।
- Judilibre: GDPR মেনে চলুন। পক্ষগুলোকে পুনরায় শনাক্ত করার চেষ্টা করবেন না।

আপনার কোটা PISTE-এ API Sélectionnées > Actions > Consulter les quotas-এর অধীনে দেখা যায়।

## যুক্তরাষ্ট্র: api.data.gov (বিনামূল্যে)

1. [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup)-এ যান (কী স্ক্রিনে দেখানো হয়)
   অথবা [api.data.gov/signup](https://api.data.gov/signup/)-এ (কী আপনাকে ইমেইলে পাঠানো হয়)।
2. আপনার নাম ও ইমেইল দিন। "how will you use it" ঘরটি ঐচ্ছিক।
3. ৪০ অক্ষরের কী-টি কপি করুন।
4. **Add or change keys** চালান এবং এটিকে US কী হিসেবে পেস্ট করুন।

শর্তাবলি, সংক্ষেপে:

- আপনার নিজের কী দিয়ে govinfo ঘণ্টায় সর্বোচ্চ ৩৬,০০০টি অনুরোধের অনুমতি দেয়।
- আমরা API-নির্দিষ্ট কোনো সেবার শর্তাবলি খুঁজে পাইনি (api.data.gov/terms/ বিদ্যমান নেই)। যাচাই করা হয়নি।
  দেখুন [govinfo-র নীতিমালা](https://www.govinfo.gov/about/policies) এবং
  [data.gov-এর গোপনীয়তা নীতি](https://data.gov/privacy-policy/)।
- কী-টি নিজের কাছে রাখুন।

## কী কোথায় সংরক্ষিত থাকে

- **ইনস্টলার বা হাতে:** প্রতিটি অ্যাপের MCP কনফিগ ফাইলে, `fontes` এন্ট্রির `env` ব্লকে, সাধারণ লেখা (plain
  text) হিসেবে। যে কেউ আপনার ব্যবহারকারী ফাইলগুলো পড়তে পারেন, তিনি কীগুলোও পড়তে পারেন।
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` অথবা `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Claude Desktop এক্সটেনশন (.mcpb):** Claude এই ঘরগুলো তার সেটিংসে রাখে এবং আপনার সিস্টেমের নিরাপদ সংরক্ষণাগার
  দিয়ে সুরক্ষিত রাখে (Mac-এ Keychain, Windows-এ Credential Manager)।

প্রতিটি পরিবর্তনের আগে ইনস্টলার কনফিগ ফাইলের একটি অনুলিপি তার পাশে সংরক্ষণ করে
(`<file>.fontes-backup-<time>`)। আপনি কী যোগ করার পরে তৈরি অনুলিপিগুলোতেও কীগুলো থাকে। যেসব পুরোনো অনুলিপি আপনার
প্রয়োজন নেই সেগুলো মুছে ফেলুন।

## কী পরিবর্তন বা সরানো

- **Add or change keys** চালান। প্রতিস্থাপন করতে নতুন একটি কী পেস্ট করুন, অথবা সরাতে `-` টাইপ করুন।
- অথবা হাতে `env` ব্লক সম্পাদনা করুন এবং অ্যাপটি রিস্টার্ট করুন।
- Fontes আনইনস্টল করলে এর পুরো এন্ট্রি, কীসহ, সরে যায়। এটি ব্যাকআপ অনুলিপিগুলো মুছে দেয় না।
- কোনো কী ফাঁস হলে, উৎসেও সেটি প্রতিস্থাপন করুন: PISTE-এ আপনার অ্যাপের জন্য নতুন ক্রেডেনশিয়াল তৈরি করুন;
  api.data.gov-এর জন্য নতুন একটি কী-র জন্য সাইন আপ করুন।

## যেসব বার্তা আপনি দেখতে পারেন

| বার্তা | অর্থ |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | ফ্রান্সের কোনো কী নেই। একটি যোগ করুন। |
| `Inactive: needs a free PISTE account. ...` (`list_jurisdictions`-এ) | একই। |
| `PISTE refused the client credentials ...` | ID বা secret ভুল অথবা আর বৈধ নয়। Authentification ট্যাব থেকে দুটোই আবার কপি করুন। |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | আপনার অ্যাপ সেই API-তে সাবস্ক্রাইব করা নেই, অথবা আপনি তার শর্তাবলি গ্রহণ করেননি। ধাপ ২ ও ৩ দেখুন। |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | যুক্তরাষ্ট্রের কোনো কী নেই। দিনে কয়েকটি কলের জন্য অনুসন্ধান কাজ করে। |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | ডেমো কী-র সীমা শেষ। আপনার নিজের কী যোগ করুন। |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | কী-টি ভুল, অথবা ইমেইল থেকে এখনো নিশ্চিত করা হয়নি। |

খালি মান কোনো কী না থাকার সমান গণ্য হয়।

## অনুমতি (WLM_PERMITTED)

এটি কোনো API কী নয়, এবং ইনস্টলার এটি সেট করে না। **কেবল তখনই এটি সেট করুন যদি সেই অনুমতি আপনার নিজের থাকে।**

কিছু উৎস ডিফল্টভাবে বন্ধ, কারণ তাদের শর্তাবলি বা robots.txt অনুমতি ছাড়া স্বয়ংক্রিয় ব্যবহার নিষিদ্ধ করে। প্রকাশকের
কাছ থেকে আপনার অনুমতি থাকলে, `env` ব্লকে `WLM_PERMITTED`-এ কমা দিয়ে আলাদা করে তার কোড যোগ করে একটি উৎস চালু
করুন: `"WLM_PERMITTED": "in,de"`।

| কোড | উৎস |
|---|---|
| `az` | আজারবাইজান: e-qanun.az (বিচার মন্ত্রণালয়) |
| `bh` | বাহরাইন: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | কলম্বিয়া: Función Pública, Gestor Normativo (সংকলিত হালনাগাদ আইন) |
| `de` | জার্মানি: NeuRIS (ফেডারেল আইনি তথ্য পোর্টাল, পরীক্ষামূলক সেবা) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | গ্রিস: National Printing Office, Government Gazette অনুসন্ধান (search.et.gr) |
| `in` | ভারত: India Code (indiacode.gov.in) |
| `mu` | মরিশাস: Supreme Court (supremecourt.govmu.org) |
| `sg` | সিঙ্গাপুর: আদালতের রায় (elitigation.sg) |

অনুমতি ছাড়া Fontes বলে: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
