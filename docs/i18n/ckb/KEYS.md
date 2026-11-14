> ئەمە وەرگێڕانێکە بە یارمەتیی ئامێر کراوە. وەشانی ئینگلیزی وەشانی باوەڕپێکراوە.

# کلیلەکانی API

نزیکەی هەموو سەرچاوەیەک لە Fontes بەبێ کلیل کار دەکات. دوانیان پێویستیان بە کلیلێکی خۆڕایی هەیە:

| کلیل | چی دەکاتەوە | بەبێ ئەو |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | فەرەنسا: Judilibre (بڕیارەکانی دادگا) و Légifrance (یاسا و ڕێساکان) | فەرەنسا کوژاوەیە. `list_jurisdictions` وەک ناچالاک پیشانی دەدات. |
| `WLM_US_GOVINFO_KEY` | ویلایەتە یەکگرتووەکان: گەڕانی govinfo (بۆچوونەکانی دادگا فیدراڵییەکان، Statutes at Large، یاسا گشتییەکان) | Fontes `DEMO_KEY`ی هاوبەش بەکار دەهێنێت: نزیکەی 10 گەڕان لە ڕۆژێکدا بۆ هەر ناونیشانێکی IP. کردنەوەی بڕیارێکی ناسراو و US Code پێویستیان بە کلیل نییە. |

کلیلەکان ئارەزوومەندانەن. دەتوانن دواتر زیادیان بکەن.

## زیادکردنی کلیلێک

**لەگەڵ دامەزرێنەر.** کاتێک Fontes ڕێکخرا، دامەزرێنەرەکە پێشنیاری زیادکردنی کلیلەکان دەکات. لەسەر Mac، کلیک لەسەر
**زیادکردنی کلیلەکان** بکەن، یان بۆ تێپەڕاندن **تەواو**؛ لەسەر Windows، وەڵامی پرسیارەکە بدەنەوە (بۆ تێپەڕاندن Enter دابگرن). بۆ زیادکردن یان گۆڕینی کلیلەکان دواتر، **Add or change keys** کار پێ بکەن:

- Mac: بەرنامەی Fontes Installer دووبارە بکەنەوە و **زیادکردن یان گۆڕینی کلیلەکان** هەڵبژێرن.
- Windows: لە بوخچەی دامەزرێنەرەکەدا دوو جار کلیک لەسەر `Add or change keys.cmd` بکەن. پڕۆگرامی دامەزراندنی
  Windows، کاتێک بەردەست بوو، لە Start menu > Fontes یشدا دایدەنێت.

نووسین نیشان نادرێت. بۆ هەر کلیلێک: بیلکێنن، بۆ هێشتنەوەی ئەوەی هەیە Enter دابگرن، یان بۆ لابردنی
`-` بنووسن. کلیلەکان دەچنە ناو هەموو ئەو بەرنامانەی کە پێشتر Fontesیان تێدایە.

**لەگەڵ پێوەکراوی Claude Desktop (.mcpb).** Claude > Settings > Extensions > Fontes بکەنەوە و
خانەکان پڕ بکەنەوە. هەموویان ئارەزوومەندانەن.

**بە دەست.** گۆڕاوەکان زیاد بکەن بۆ بلۆکی `env`ی تۆماری `fontes` لە ڕێکخستنەکانی MCPی بەرنامەکەتان:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

دوای هەر گۆڕانکارییەک بەرنامەکە دووبارە دەست پێ بکەنەوە.

## فەرەنسا: PISTE (خۆڕایی)

1. هەژمارێک لە [piste.gouv.fr](https://piste.gouv.fr) دروست بکەن. ئەمە واتە قبووڵکردنی مەرجەکانی PISTE (CGU).
2. بڕۆن بۆ API > **Consentement CGU API**. مەرجەکانی **JUDILIBRE** و **Légifrance** (production) قبووڵ بکەن.
3. **production application**ێک دروست بکەن. ئەو `APP_SANDBOX`ەی بۆتان دروستکراوە ناتوانێت بگاتە production.
   لە ژێر "Modifier l'application"، **JUDILIBRE (production)** و **Légifrance (production)** نیشان بکەن، پاشان جێبەجێی بکەن.
4. تابی **Authentification**ی بەرنامەکە بکەنەوە. `client_id` و `client_secret` کۆپی بکەن.
5. **Add or change keys** کار پێ بکەن و بیانلکێنن.

مەرجەکان، بە کورتی:

- داتا: Licence Ouverte / Etalab 2.0. دووبارە بەکارهێنانەوە، لەوانەش دووبارە بەکارهێنانەوەی بازرگانی، لەگەڵ ناوهێنانی سەرچاوە ڕێگەپێدراوە.
- زانیارییەکانی چوونەژوورەوەتان (credentials) بڵاو مەکەنەوە و هاوبەشیان مەکەن. ئەگەر دزەیان کرد PISTE ئاگادار بکەنەوە.
- APIی Légifrance خزمەتگوزارییەکی betaیە. لەوانەیە ڕابگیرێت، و سنووری بەکارهێنانی (quotas) هەیە (بۆ هەر چرکە، خولەک و ڕۆژێک).
- دەقەکانی Légifrance وەشانی باوەڕپێکراو نین. تەنها PDFی واژۆکراوی Journal officiel باوەڕپێکراوە.
- Judilibre: ناوی دادوەران یان فەرمانبەرانی دادگا بۆ هەڵسەنگاندن، بەراوردکردن یان پێشبینیکردنی کارەکەیان بەکار مەهێنن
  (Code de l'organisation judiciaire art. L111-13؛ تاوانێکی سزایی).
- Judilibre: پەیڕەوی GDPR بکەن. هەوڵ مەدەن لایەنەکان دووبارە بناسێننەوە.

سنوورەکانی بەکارهێنانتان لە PISTE لە ژێر API Sélectionnées > Actions > Consulter les quotasدان.

## ویلایەتە یەکگرتووەکان: api.data.gov (خۆڕایی)

1. بڕۆن بۆ [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (کلیلەکە لەسەر شاشە پیشان دەدرێت)
   یان [api.data.gov/signup](https://api.data.gov/signup/) (کلیلەکە بە ئیمەیڵ بۆتان دەنێردرێت).
2. ناو و ئیمەیڵەکەتان بنووسن. خانەی "how will you use it" ئارەزوومەندانەیە.
3. کلیلە 40-پیتییەکە کۆپی بکەن.
4. **Add or change keys** کار پێ بکەن و وەک کلیلی ئەمریکا بیلکێنن.

مەرجەکان، بە کورتی:

- لەگەڵ کلیلی خۆتان، govinfo ڕێگە بە تا 36,000 داواکاری لە کاتژمێرێکدا دەدات.
- هیچ مەرجێکی خزمەتگوزاریی تایبەت بە APIمان نەدۆزییەوە (api.data.gov/terms/ بوونی نییە). پشتڕاست نەکراوەتەوە.
  سەیری [سیاسەتەکانی govinfo](https://www.govinfo.gov/about/policies) و
  [سیاسەتی تایبەتمەندیی data.gov](https://data.gov/privacy-policy/) بکەن.
- کلیلەکە لای خۆتان بهێڵنەوە.

## کلیلەکان لە کوێ هەڵدەگیرێن

- **دامەزرێنەر یان بە دەست:** وەک دەقی سادە لە فایلی ڕێکخستنەکانی MCPی هەر بەرنامەیەکدا، لە بلۆکی `env`ی
  تۆماری `fontes`. هەر کەسێک بتوانێت فایلەکانی بەکارهێنەرەکەتان بخوێنێتەوە، دەتوانێت کلیلەکانیش بخوێنێتەوە.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac)،
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` یان `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **پێوەکراوی Claude Desktop (.mcpb):** Claude ئەم خانانە لە ڕێکخستنەکانیدا هەڵدەگرێت و بە
  هەڵگرتنی پارێزراوی سیستەمەکەتان (Keychain لە Mac، Credential Manager لە Windows) دەیانپارێزێت.

پێش هەر گۆڕانکارییەک، دامەزرێنەرەکە کۆپییەکی فایلی ڕێکخستنەکە لە تەنیشتیدا پاشەکەوت دەکات
(`<file>.fontes-backup-<time>`). ئەو کۆپییانەی دوای زیادکردنی کلیلەکان دروستکراون کلیلەکانیشیان تێدایە. کۆپییە
کۆنەکان کە پێویستتان پێیان نییە بسڕنەوە.

## گۆڕین یان لابردنی کلیلێک

- **Add or change keys** کار پێ بکەن. بۆ جێگۆڕکێ کلیلێکی نوێ بلکێنن، یان بۆ لابردنی `-` بنووسن.
- یان بلۆکی `env` بە دەست دەستکاری بکەن و بەرنامەکە دووبارە دەست پێ بکەنەوە.
- لابردنی Fontes هەموو تۆمارەکەی، لەگەڵ کلیلەکان، لادەبات. کۆپییە پاشەکەوتەکان ناسڕێتەوە.
- ئەگەر کلیلێک دزەی کردبێت، لە سەرچاوەکەشدا بیگۆڕن: لە PISTE، زانیاریی چوونەژوورەوەی نوێ بۆ بەرنامەکەتان دروست بکەن؛
  بۆ api.data.gov، بۆ کلیلێکی نوێ تۆمار بکەن.

## ئەو پەیامانەی لەوانەیە ببینن

| پەیام | مانا |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | کلیلی فەرەنسا نییە. یەکێک زیاد بکەن. |
| `Inactive: needs a free PISTE account. ...` (لە `list_jurisdictions`) | هەمان شت. |
| `PISTE refused the client credentials ...` | ID یان secret هەڵەیە یان چیتر کارا نییە. هەردووکیان دووبارە لە تابی Authentification کۆپی بکەن. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | بەرنامەکەتان بەشداری ئەو APIیە نەکراوە، یان مەرجەکانیتان قبووڵ نەکردووە. سەیری هەنگاوەکانی 2 و 3 بکەن. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | کلیلی ئەمریکا نییە. گەڕان بۆ چەند بانگکردنێک لە ڕۆژێکدا کار دەکات. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | کلیلە demoکە تەواو بووە. کلیلی خۆتان زیاد بکەن. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | کلیلەکە هەڵەیە، یان هێشتا لە ئیمەیڵەکەوە پشتڕاست نەکراوەتەوە. |

بەهایەکی بەتاڵ وەک نەبوونی کلیل دەژمێردرێت.

## ڕێگەپێدانەکان (WLM_PERMITTED)

ئەمە کلیلی API نییە، و دامەزرێنەرەکە داینانێت. **تەنها کاتێک دایبنێن کە ئەو
ڕێگەپێدانەتان خۆتان هەبێت.**

هەندێک سەرچاوە بە شێوەی بنەڕەتی کوژاوەن چونکە مەرجەکانیان یان robots.txt بەکارهێنانی خۆکار بەبێ
ڕێگەپێدان قەدەغە دەکەن. ئەگەر ڕێگەپێدانی بڵاوکەرەوەتان هەیە، سەرچاوەیەک هەڵبکەن بە زیادکردنی کۆدەکەی بۆ
`WLM_PERMITTED`، بە کۆما جیاکراوە، لە بلۆکی `env`دا: `"WLM_PERMITTED": "in,de"`.

| کۆد | سەرچاوە |
|---|---|
| `az` | ئازەربایجان: e-qanun.az (وەزارەتی داد) |
| `bh` | بەحرەین: دەستەی یاسادانان و بیروڕای یاسایی (lloc.gov.bh) |
| `co` | کۆلۆمبیا: Función Pública، Gestor Normativo (یاسا و ڕێسا یەکخراوەکان) |
| `de` | ئەڵمانیا: NeuRIS (دەروازەی زانیاریی یاسایی فیدراڵی، خزمەتگوزاریی تاقیکاری) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | یۆنان: نووسینگەی نیشتمانیی چاپ، گەڕانی Government Gazette (search.et.gr) |
| `in` | هیندستان: India Code (indiacode.gov.in) |
| `mu` | مۆریشیۆس: دادگای باڵا (supremecourt.govmu.org) |
| `sg` | سەنگافوورە: بڕیارەکانی دادگا (elitigation.sg) |

بەبێ ڕێگەپێدان، Fontes دەڵێت: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
