> ဤသည်မှာ စက်အကူအညီဖြင့် ဘာသာပြန်ထားခြင်း ဖြစ်သည်။ အင်္ဂလိပ်ဗားရှင်းသာ အတည်ဖြစ်သည်။

# API ကီးများ

Fontes ရှိ ရင်းမြစ်အားလုံးနီးပါးသည် ကီးမပါဘဲ အလုပ်လုပ်သည်။ သုံးခုသည် အခမဲ့ကီး လိုအပ်သည်:

| ကီး | ဖွင့်ပေးသည့်အရာ | ကီးမပါလျှင် |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | ပြင်သစ်: Judilibre (တရားရုံးစီရင်ချက်များ) နှင့် Légifrance (ဥပဒေများ) | ပြင်သစ်ကို ပိတ်ထားသည်။ `list_jurisdictions` က ၎င်းကို အသုံးမပြုနိုင်သည့်အဖြစ် ပြသည်။ |
| `WLM_US_GOVINFO_KEY` | အမေရိကန်ပြည်ထောင်စု: govinfo ရှာဖွေမှု (ဖက်ဒရယ်တရားရုံး ဆုံးဖြတ်ချက်များ၊ Statutes at Large၊ public laws) | Fontes သည် မျှဝေသုံး `DEMO_KEY` ကို အသုံးပြုသည်: IP လိပ်စာတစ်ခုလျှင် တစ်နေ့ ရှာဖွေမှု 10 ခုခန့်။ သိပြီးသား စီရင်ချက်တစ်ခုကို ဖွင့်ခြင်းနှင့် US Code သည် ကီး မလိုပါ။ |
| `WLM_US_COURTLISTENER_KEY` | အမေရိကန် ပြည်နယ်တရားရုံးများ (`us-states`): ပြည်နယ် ၅၀ နှင့် DC အားလုံး၏ တရားလွှတ်တော်ချုပ်နှင့် အယူခံတရားရုံးများ၏ စီရင်ချက်များ၊ CourtListener မှ | အမေရိကန် ပြည်နယ်တရားရုံးစီရင်ထုံးကို ပိတ်ထားသည်။ `list_jurisdictions` က ၎င်းကို မလှုပ်ရှားသည်ဟု ပြသည်။ |

ကီးများသည် မဖြစ်မနေ မဟုတ်ပါ။ ၎င်းတို့ကို နောက်မှ ထည့်နိုင်သည်။

## ကီးထည့်ခြင်း

**တပ်ဆင်ရေးပရိုဂရမ်ဖြင့်။** Fontes ကို စနစ်ထည့်သွင်းပြီးနောက် တပ်ဆင်ရေးပရိုဂရမ်က ကီးများ ထည့်ရန် ကမ်းလှမ်းသည်။ Mac တွင်
**ကီးများ ထည့်ရန်** ကို နှိပ်ပါ၊ သို့မဟုတ် ကျော်ရန် **ပြီးပါပြီ** ကို နှိပ်ပါ။ Windows တွင် မေးခွန်းကို ဖြေပါ (ကျော်ရန် Enter ကို နှိပ်ပါ)။
ကီးများကို နောက်မှ ထည့်ရန် သို့မဟုတ် ပြောင်းရန် **Add or change keys** ကို run ပါ:

- Mac: Fontes Installer အက်ပ်ကို ပြန်ဖွင့်ပြီး **ကီးများ ထည့်ရန် သို့မဟုတ် ပြောင်းရန်** ကို ရွေးပါ။
- Windows: Start menu ကိုဖွင့်ပြီး **Fontes** → **ကီးများ ထည့်ရန် သို့မဟုတ် ပြောင်းရန်** ကို ရွေးပါ။

ရိုက်ထည့်သည့်စာသားကို ဖုံးကွယ်ထားသည်။ ကီးတစ်ခုချင်းစီအတွက်: ၎င်းကို paste လုပ်ပါ၊ ရှိပြီးသားအရာကို ထားရန် Enter ကို နှိပ်ပါ၊ သို့မဟုတ်
ဖယ်ရှားရန် `-` ကို ရိုက်ပါ။ ကီးများသည် Fontes ရှိပြီးသား အက်ပ်တိုင်းထဲသို့ ရောက်သွားသည်။

**Claude Desktop extension (.mcpb) ဖြင့်။** Claude > Settings > Extensions > Fontes ကို ဖွင့်ပြီး
အကွက်များကို ဖြည့်ပါ။ ၎င်းတို့အားလုံးသည် မဖြစ်မနေ မဟုတ်ပါ။

**လက်ဖြင့်။** variable များကို သင့်အက်ပ်၏ MCP config ရှိ `fontes` entry ၏ `env` block တွင် ထည့်ပါ:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

မည်သည့်ပြောင်းလဲမှုမဆို ပြုလုပ်ပြီးနောက် အက်ပ်ကို ပြန်စတင်ပါ။

## ပြင်သစ်: PISTE (အခမဲ့)

1. [piste.gouv.fr](https://piste.gouv.fr) တွင် အကောင့်တစ်ခု ဖန်တီးပါ။ ဆိုလိုသည်မှာ PISTE စည်းကမ်းချက်များ (CGU) ကို လက်ခံခြင်း ဖြစ်သည်။
2. API > **Consentement CGU API** သို့ သွားပါ။ **JUDILIBRE** နှင့် **Légifrance** (production) အတွက် စည်းကမ်းချက်များကို လက်ခံပါ။
3. **production application** တစ်ခု ဖန်တီးပါ။ သင့်အတွက် ပြုလုပ်ထားသော `APP_SANDBOX` သည် production သို့ မရောက်နိုင်ပါ။
   "Modifier l'application" အောက်တွင် **JUDILIBRE (production)** နှင့် **Légifrance (production)** ကို အမှန်ခြစ်ပြီး apply လုပ်ပါ။
4. အက်ပ်၏ **Authentification** tab ကို ဖွင့်ပါ။ `client_id` နှင့် `client_secret` ကို ကူးယူပါ။
5. **Add or change keys** ကို run ပြီး ၎င်းတို့ကို paste လုပ်ပါ။

စည်းကမ်းချက်များ အတိုချုပ်:

- ဒေတာ: Licence Ouverte / Etalab 2.0။ စီးပွားဖြစ် ပြန်လည်အသုံးပြုမှု အပါအဝင် ပြန်လည်အသုံးပြုမှုကို ရင်းမြစ်ဖော်ပြချက်ဖြင့် ခွင့်ပြုသည်။
- သင်၏ credential များကို မထုတ်ဝေပါနှင့်၊ မမျှဝေပါနှင့်။ ၎င်းတို့ ပေါက်ကြားပါက PISTE ကို အသိပေးပါ။
- Légifrance API သည် beta ဝန်ဆောင်မှု ဖြစ်သည်။ ၎င်းကို ဆိုင်းငံ့နိုင်ပြီး quota များ ရှိသည် (တစ်စက္ကန့်၊ တစ်မိနစ်နှင့် တစ်နေ့လျှင်)။
- Légifrance စာသားများသည် စစ်မှန်သော ဗားရှင်း မဟုတ်ပါ။ လက်မှတ်ထိုးထားသော Journal officiel PDF သာ စစ်မှန်သည်။
- Judilibre: တရားသူကြီးများ သို့မဟုတ် စာရေးများ၏ အမည်များကို ၎င်းတို့၏အလုပ်ကို အကဲဖြတ်ရန်၊ နှိုင်းယှဉ်ရန် သို့မဟုတ် ခန့်မှန်းရန် မသုံးပါနှင့်
  (Code de l'organisation judiciaire art. L111-13၊ ရာဇဝတ်ပြစ်မှု ဖြစ်သည်)။
- Judilibre: GDPR ကို လိုက်နာပါ။ အမှုသည်များကို ပြန်လည်ဖော်ထုတ်ရန် မကြိုးစားပါနှင့်။

သင်၏ quota များသည် PISTE ရှိ API Sélectionnées > Actions > Consulter les quotas အောက်တွင် ရှိသည်။

## အမေရိကန်ပြည်ထောင်စု: api.data.gov (အခမဲ့)

1. [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (ကီးကို မျက်နှာပြင်ပေါ်တွင် ပြသည်)
   သို့မဟုတ် [api.data.gov/signup](https://api.data.gov/signup/) (ကီးကို သင့်ထံ အီးမေးလ်ပို့သည်) သို့ သွားပါ။
2. သင်၏အမည်နှင့် အီးမေးလ်ကို ထည့်ပါ။ "how will you use it" အကွက်သည် မဖြစ်မနေ မဟုတ်ပါ။
3. စာလုံး 40 လုံးပါ ကီးကို ကူးယူပါ။
4. **Add or change keys** ကို run ပြီး ၎င်းကို US ကီးအဖြစ် paste လုပ်ပါ။

စည်းကမ်းချက်များ အတိုချုပ်:

- သင်၏ကိုယ်ပိုင်ကီးဖြင့် govinfo သည် တစ်နာရီလျှင် တောင်းဆိုမှု 36,000 အထိ ခွင့်ပြုသည်။
- API အတွက် သီးသန့် ဝန်ဆောင်မှုစည်းကမ်းချက်များကို ကျွန်ုပ်တို့ ရှာမတွေ့ပါ (api.data.gov/terms/ မရှိပါ)။ အတည်မပြုရသေးပါ။
  [govinfo ၏ မူဝါဒများ](https://www.govinfo.gov/about/policies) နှင့်
  [data.gov ကိုယ်ရေးအချက်အလက် မူဝါဒ](https://data.gov/privacy-policy/) ကို ကြည့်ပါ။
- ကီးကို သင်ကိုယ်တိုင်သာ သိမ်းထားပါ။

## အမေရိကန် ပြည်နယ်တရားရုံးများ: CourtListener (အခမဲ့)

CourtListener ကို [Free Law Project](https://free.law) က လုပ်ကိုင်သည်။ ၎င်းသည် အမြတ်အစွန်းမယူသော အဖွဲ့အစည်းဖြစ်ပြီး ၂၀၁၀ ခုနှစ်မှစ၍ အမေရိကန်တရားရုံးစီရင်ချက်များကို စုဆောင်းကာ လူတိုင်းအတွက် အခမဲ့ ရရှိနိုင်စေသည်။ ၎င်း၏ ကိုယ်ပိုင်ရေတွက်ချက်အရ စီရင်ချက် ကိုးသန်းကျော် ရှိသည်။ ၎င်းသည် တရားဝင်ရင်းမြစ် မဟုတ်ပါ။ တရားရုံးများက ၎င်းတို့၏ စီရင်ချက်များကို ကိုယ်တိုင် ထုတ်ပြန်ပြီး CourtListener က ၎င်းတို့ကို တရားရုံးဝက်ဘ်ဆိုက်များနှင့် စကန်ဖတ်ထားသော ဥပဒေရီပို့များမှ စုဆောင်းသည်။ ၎င်းမှ Fontes ၏ အဖြေတိုင်းတွင် ထိုသို့ ဖော်ပြထားသည်။ Fontes သည် Free Law Project နှင့် ဆက်စပ်မှု မရှိပါ။

1. [courtlistener.com](https://www.courtlistener.com/sign-in/) တွင် အခမဲ့အကောင့် ဖန်တီးပါ။
2. သင်၏ပရိုဖိုင်ကို ဖွင့်ပြီး သင်၏ API token ကို ကူးယူပါ။
3. **Add or change keys** ကို run ပြီး ၎င်းကို CourtListener ကီးအဖြစ် paste လုပ်ပါ။

စည်းကမ်းချက်များ အတိုချုပ် ([စည်းကမ်းချက်အပြည့်အစုံ](https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies)):

- token သည် သင့်ကိုယ်ပိုင်သာ ဖြစ်သည်။ မျှဝေခြင်း၊ ပေါင်းစည်းခြင်း၊ ပြန်ရောင်းခြင်း မပြုရ၊ အကောင့်များစွာလည်း မသုံးရ။
- AI အက်ပ်တစ်ခုက သင်၏ token ဖြင့် ပြုလုပ်သည့်အရာအတွက် သင်တာဝန်ရှိသည်။
- ၎င်းတို့၏ဒေတာကို AI က ပြုလုပ်သော ခွဲခြမ်းစိတ်ဖြာမှုကို Free Law Project က ထုတ်လုပ်သည်၊ ထောက်ခံသည်၊ စစ်ဆေးသည်ဟု မဖော်ပြရ။
- အခမဲ့အကောင့်သည် တစ်မိနစ်လျှင် တောင်းဆိုမှု ၅ ခု၊ တစ်နာရီလျှင် ၅၀၊ တစ်ရက်လျှင် ၁၂၅ ကို ခွင့်ပြုသည်။ ရှာဖွေမှုတစ်ခုသည် တောင်းဆိုမှုတစ်ခုဖြစ်ပြီး စီရင်ချက်တစ်ခုကို ဖွင့်ခြင်းသည် နှစ်ခုဖြစ်သည်။ Free Law Project အဖွဲ့ဝင်ခွင့်က ကန့်သတ်ချက်များကို မြှင့်တင်ပေးသည်။
- CourtListener သည် တိကျမှုကို အာမမခံပါ။ စီရင်ချက်တစ်ခုကို အားထားမီ တရားရုံး၏ မိတ္တူနှင့် တိုက်ဆိုင်စစ်ဆေးပါ။

## ကီးများကို မည်သည့်နေရာတွင် သိမ်းသနည်း

- **တပ်ဆင်ရေးပရိုဂရမ် သို့မဟုတ် လက်ဖြင့်:** အက်ပ်တစ်ခုချင်းစီ၏ MCP config ဖိုင်တွင်၊ `fontes` entry ၏ `env` block အတွင်း
  ရိုးရိုးစာသားအဖြစ်။ သင်၏ user ဖိုင်များကို ဖတ်နိုင်သူ မည်သူမဆို ကီးများကို ဖတ်နိုင်သည်။
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` သို့မဟုတ် `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Claude Desktop extension (.mcpb):** Claude သည် ဤအကွက်များကို ၎င်း၏ဆက်တင်များတွင် သိမ်းထားပြီး
  သင့်စနစ်၏ လုံခြုံသော သိုလှောင်မှု (Mac တွင် Keychain၊ Windows တွင် Credential Manager) ဖြင့် ကာကွယ်သည်။

ပြောင်းလဲမှုတိုင်းမတိုင်မီ တပ်ဆင်ရေးပရိုဂရမ်သည် config ဖိုင်၏ မိတ္တူတစ်ခုကို ၎င်းဘေးတွင် သိမ်းသည်
(`<file>.fontes-backup-<time>`)။ သင်ကီးများ ထည့်ပြီးနောက် ပြုလုပ်ထားသော မိတ္တူများတွင်လည်း ကီးများ ပါဝင်သည်။ မလိုအပ်သော
မိတ္တူဟောင်းများကို ဖျက်ပါ။

## ကီးကို ပြောင်းခြင်း သို့မဟုတ် ဖယ်ရှားခြင်း

- **Add or change keys** ကို run ပါ။ အစားထိုးရန် ကီးအသစ်ကို paste လုပ်ပါ၊ သို့မဟုတ် ဖယ်ရှားရန် `-` ကို ရိုက်ပါ။
- သို့မဟုတ် `env` block ကို လက်ဖြင့် ပြင်ပြီး အက်ပ်ကို ပြန်စတင်ပါ။
- Fontes ကို uninstall လုပ်ခြင်းသည် ၎င်း၏ entry တစ်ခုလုံးကို ကီးများအပါအဝင် ဖယ်ရှားသည်။ ၎င်းသည် backup မိတ္တူများကို မဖျက်ပါ။
- ကီးတစ်ခု ပေါက်ကြားပါက ၎င်းကို ရင်းမြစ်တွင်လည်း အစားထိုးပါ: PISTE တွင် သင့်အက်ပ်အတွက် credential အသစ်များ ပြုလုပ်ပါ၊
  api.data.gov အတွက် ကီးအသစ်တစ်ခုအတွက် စာရင်းသွင်းပါ။

## သင်မြင်ရနိုင်သော မက်ဆေ့ချ်များ

| မက်ဆေ့ချ် | အဓိပ္ပာယ် |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | ပြင်သစ်ကီး မရှိပါ။ တစ်ခု ထည့်ပါ။ |
| `Inactive: needs a free PISTE account. ...` (`list_jurisdictions` တွင်) | အထက်ပါအတိုင်း။ |
| `PISTE refused the client credentials ...` | ID သို့မဟုတ် secret မှားနေသည် သို့မဟုတ် အကျုံးမဝင်တော့ပါ။ Authentification tab မှ နှစ်ခုလုံးကို ထပ်ကူးပါ။ |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | သင့်အက်ပ်သည် ထို API သို့ subscribe မလုပ်ထားပါ၊ သို့မဟုတ် ၎င်း၏စည်းကမ်းချက်များကို သင်မလက်ခံရသေးပါ။ အဆင့် 2 နှင့် 3 ကို ကြည့်ပါ။ |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | US ကီး မရှိပါ။ ရှာဖွေမှုသည် တစ်နေ့ ခေါ်ဆိုမှု အနည်းငယ်အတွက် အလုပ်လုပ်သည်။ |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | demo ကီးကို အသုံးပြုပြီး ကုန်သွားပြီ။ သင်၏ကိုယ်ပိုင်ကီးကို ထည့်ပါ။ |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | ကီးမှားနေသည်၊ သို့မဟုတ် အီးမေးလ်မှ အတည်မပြုရသေးပါ။ |

တန်ဖိုးအလွတ်ကို ကီးမရှိဟု သတ်မှတ်သည်။

## ခွင့်ပြုချက်များ (WLM_PERMITTED)

ဤအရာသည် API ကီး မဟုတ်ပါ၊ တပ်ဆင်ရေးပရိုဂရမ်ကလည်း ၎င်းကို မသတ်မှတ်ပါ။ **ထိုခွင့်ပြုချက်ကို သင်ကိုယ်တိုင် ရရှိထားမှသာ
၎င်းကို သတ်မှတ်ပါ။**

ရင်းမြစ်အချို့ကို ၎င်းတို့၏ စည်းကမ်းချက်များ သို့မဟုတ် robots.txt က ခွင့်ပြုချက်မရှိဘဲ အလိုအလျောက်အသုံးပြုမှုကို တားမြစ်သောကြောင့်
မူလအားဖြင့် ပိတ်ထားသည်။ ထုတ်ဝေသူထံမှ ခွင့်ပြုချက် ရရှိထားပါက ရင်းမြစ်တစ်ခု၏ ကုဒ်ကို `env` block ရှိ
`WLM_PERMITTED` တွင် ကော်မာခြား၍ ထည့်ခြင်းဖြင့် ၎င်းကို ဖွင့်ပါ: `"WLM_PERMITTED": "in,de"`။

| ကုဒ် | ရင်းမြစ် |
|---|---|
| `az` | အဇာဘိုင်ဂျန်: e-qanun.az (တရားရေးဝန်ကြီးဌာန) |
| `bh` | ဘာရိန်း: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | ကိုလံဘီယာ: Función Pública, Gestor Normativo (ပြင်ဆင်ချက်များ ပေါင်းစည်းထားသော ဥပဒေများ) |
| `de` | ဂျာမနီ: NeuRIS (ဖက်ဒရယ် ဥပဒေဆိုင်ရာ သတင်းအချက်အလက် portal၊ စမ်းသပ်ဝန်ဆောင်မှု) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | ဂရိ: National Printing Office, Government Gazette search (search.et.gr) |
| `mu` | မော်ရီရှပ်: Supreme Court (supremecourt.govmu.org) |
| `sg` | စင်္ကာပူ: တရားရုံး စီရင်ချက်များ (elitigation.sg) |

ခွင့်ပြုချက်မရှိလျှင် Fontes က ဤသို့ ပြောသည်: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
