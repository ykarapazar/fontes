> هذه ترجمة أُعدّت بمساعدة الآلة. النسخة الإنجليزية هي النسخة المعتمدة.

# مفاتيح API

يعمل كل مصدر تقريبًا في Fontes بلا مفتاح. ثلاثة منها تحتاج إلى مفتاح مجاني:

| المفتاح | ما يتيحه | بدونه |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | فرنسا: Judilibre (الأحكام القضائية) وLégifrance (التشريعات) | فرنسا معطّلة. يعرضها `list_jurisdictions` على أنها غير نشطة. |
| `WLM_US_GOVINFO_KEY` | الولايات المتحدة: بحث govinfo (آراء المحاكم الفيدرالية، Statutes at Large، القوانين العامة) | يستخدم Fontes المفتاح المشترك `DEMO_KEY`: نحو 10 عمليات بحث يوميًا لكل عنوان IP. فتح حكم معروف وUS Code لا يحتاجان إلى مفتاح. |
| `WLM_US_COURTLISTENER_KEY` | محاكم الولايات الأمريكية (`us-states`): آراء المحاكم العليا ومحاكم الاستئناف في الولايات الخمسين كلها ومقاطعة كولومبيا (DC)، من CourtListener | الأحكام القضائية للولايات الأمريكية معطّلة. يعرضها `list_jurisdictions` على أنها غير نشطة. |

المفاتيح اختيارية. يمكنك إضافتها لاحقًا.

## إضافة مفتاح

**باستخدام أداة التثبيت.** بعد إعداد Fontes، تعرض أداة التثبيت إضافة المفاتيح. على جهاز Mac، انقر
**إضافة المفاتيح**، أو **تم** للتخطي؛ وعلى Windows، أجب عن السؤال (اضغط Enter للتخطي). لإضافة المفاتيح أو تغييرها لاحقًا، شغّل **Add or change keys**:

- Mac: افتح تطبيق Fontes Installer مرة أخرى واختر **إضافة المفاتيح أو تغييرها**.
- Windows: افتح قائمة Start، واختر **Fontes**، ثم **إضافة المفاتيح أو تغييرها**.

لا تظهر الكتابة. لكل مفتاح: الصقه، أو اضغط Enter للإبقاء على القيمة الموجودة، أو اكتب `-`
لإزالته. تُضاف المفاتيح إلى كل تطبيق يحتوي على Fontes مسبقًا.

**باستخدام إضافة Claude Desktop ‏(.mcpb).** افتح Claude > Settings > Extensions > Fontes و
املأ الحقول. جميعها اختيارية.

**يدويًا.** أضِف المتغيرات إلى كتلة `env` في إدخال `fontes` ضمن إعدادات MCP لتطبيقك:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

أعِد تشغيل التطبيق بعد أي تغيير.

## فرنسا: PISTE (مجاني)

1. أنشئ حسابًا على [piste.gouv.fr](https://piste.gouv.fr). وهذا يعني قبول شروط PISTE ‏(CGU).
2. انتقل إلى API > **Consentement CGU API**. اقبل الشروط الخاصة بـ **JUDILIBRE** و**Légifrance** (production).
3. أنشئ **production application** (تطبيق إنتاج). لا يستطيع `APP_SANDBOX` الذي أُنشئ لك الوصول إلى بيئة الإنتاج.
   تحت "Modifier l'application"، حدّد **JUDILIBRE (production)** و**Légifrance (production)**، ثم طبّق.
4. افتح علامة التبويب **Authentification** الخاصة بالتطبيق. انسخ `client_id` و`client_secret`.
5. شغّل **Add or change keys** والصقهما.

الشروط، باختصار:

- البيانات: Licence Ouverte / Etalab 2.0. إعادة الاستخدام، بما فيها إعادة الاستخدام التجاري، مسموحة مع نسبة العمل إلى مصدره.
- لا تنشر بيانات اعتمادك ولا تشاركها. أبلغ PISTE إذا تسرّبت.
- واجهة Légifrance البرمجية خدمة تجريبية (beta). قد تُعلَّق، ولها حصص (في الثانية والدقيقة واليوم).
- نصوص Légifrance ليست النسخة الأصلية. وحده ملف PDF الموقَّع من Journal officiel هو الأصلي.
- Judilibre: لا تستخدم أسماء القضاة أو كتّاب الضبط لتقييم عملهم أو مقارنته أو التنبؤ به
  (Code de l'organisation judiciaire المادة L111-13؛ وهي جريمة جنائية).
- Judilibre: اتّبع اللائحة العامة لحماية البيانات (GDPR). لا تحاول إعادة تحديد هوية الأطراف.

حصصك موجودة على PISTE تحت API Sélectionnées > Actions > Consulter les quotas.

## الولايات المتحدة: api.data.gov (مجاني)

1. انتقل إلى [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (يُعرض المفتاح على الشاشة)
   أو [api.data.gov/signup](https://api.data.gov/signup/) (يُرسَل المفتاح إليك بالبريد الإلكتروني).
2. أدخل اسمك وبريدك الإلكتروني. حقل "how will you use it" اختياري.
3. انسخ المفتاح المكوّن من 40 حرفًا.
4. شغّل **Add or change keys** والصقه بوصفه مفتاح الولايات المتحدة.

الشروط، باختصار:

- بمفتاحك الخاص، يسمح govinfo بما يصل إلى 36,000 طلب في الساعة.
- لم نجد شروط خدمة خاصة بالواجهة البرمجية (api.data.gov/terms/ غير موجودة). غير مُتحقَّق منه.
  راجع [سياسات govinfo](https://www.govinfo.gov/about/policies) و
  [سياسة الخصوصية في data.gov](https://data.gov/privacy-policy/).
- احتفظ بالمفتاح لنفسك.

## محاكم الولايات الأمريكية: CourtListener (مجاني)

يدير CourtListener منظمة [Free Law Project](https://free.law)، وهي منظمة غير ربحية تجمع آراء المحاكم الأمريكية منذ عام 2010 وتتيحها مجانًا للجميع. وبحسب إحصائها الخاص، يضم أكثر من تسعة ملايين حكم. وهو ليس مصدرًا رسميًا: فالمحاكم تنشر آراءها بنفسها، وCourtListener يجمعها من مواقع المحاكم ومن مجموعات الأحكام الممسوحة ضوئيًا. وكل إجابة من Fontes مصدرها هذا الموقع تذكر ذلك. Fontes غير تابع لـ Free Law Project.

1. أنشئ حسابًا مجانيًا على [courtlistener.com](https://www.courtlistener.com/sign-in/).
2. افتح ملفك الشخصي وانسخ رمز API (token) الخاص بك.
3. شغّل **Add or change keys** والصقه بوصفه مفتاح CourtListener.

الشروط، باختصار ([الشروط الكاملة](https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies)):

- الرمز لك وحدك: لا تشاركه ولا تجمعه مع رموز غيرك ولا تبعه، ولا تستخدم عدة حسابات.
- أنت مسؤول عما يفعله تطبيق ذكاء اصطناعي برمزك.
- لا تقدّم تحليل الذكاء الاصطناعي لبياناتهم على أنه من إنتاج Free Law Project أو بتأييدها أو بعد تدقيقها.
- يسمح الحساب المجاني بـ 5 طلبات في الدقيقة و50 في الساعة و125 في اليوم. البحث طلب واحد؛ وفتح حكم طلبان. وتؤدي عضوية Free Law Project إلى رفع الحدود.
- لا يضمن CourtListener الدقة. قارن الحكم بنسخة المحكمة قبل أن تعتمد عليه.

## أين تُخزَّن المفاتيح

- **أداة التثبيت أو يدويًا:** كنص عادي في ملف إعدادات MCP لكل تطبيق، في كتلة `env` من
  إدخال `fontes`. يستطيع أي شخص يمكنه قراءة ملفات المستخدم الخاصة بك قراءة المفاتيح.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac)،
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` أو `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **إضافة Claude Desktop ‏(.mcpb):** يحتفظ Claude بهذه الحقول في إعداداته ويحميها
  بالتخزين الآمن في نظامك (Keychain على Mac، وCredential Manager على Windows).

قبل كل تغيير، تحفظ أداة التثبيت نسخة من ملف الإعدادات بجانبه
(`<file>.fontes-backup-<time>`). النسخ التي تُنشأ بعد إضافتك المفاتيح تحتوي على المفاتيح أيضًا. احذف النسخ
القديمة التي لا تحتاج إليها.

## تغيير مفتاح أو إزالته

- شغّل **Add or change keys**. الصق مفتاحًا جديدًا لاستبداله، أو اكتب `-` لإزالته.
- أو عدّل كتلة `env` يدويًا وأعِد تشغيل التطبيق.
- إلغاء تثبيت Fontes يُزيل إدخاله بالكامل، بما في ذلك المفاتيح. ولا يحذف النسخ الاحتياطية.
- إذا تسرّب مفتاح، فاستبدله أيضًا لدى المصدر: على PISTE، أنشئ بيانات اعتماد جديدة لتطبيقك؛
  ولدى api.data.gov، سجّل للحصول على مفتاح جديد.

## رسائل قد تراها

| الرسالة | المعنى |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | لا يوجد مفتاح لفرنسا. أضِف واحدًا. |
| `Inactive: needs a free PISTE account. ...` (في `list_jurisdictions`) | الشيء نفسه. |
| `PISTE refused the client credentials ...` | المعرّف أو السرّ خاطئ أو لم يعد صالحًا. انسخ كليهما مرة أخرى من علامة التبويب Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | تطبيقك غير مشترك في تلك الواجهة البرمجية، أو لم تقبل شروطها. راجع الخطوتين 2 و3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | لا يوجد مفتاح للولايات المتحدة. يعمل البحث لعدد قليل من الاستدعاءات يوميًا. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | استُنفد المفتاح التجريبي. أضِف مفتاحك الخاص. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | المفتاح خاطئ، أو لم يُؤكَّد بعد من البريد الإلكتروني. |

القيمة الفارغة تُعدّ بمثابة عدم وجود مفتاح.

## الأذونات (WLM_PERMITTED)

هذا ليس مفتاح API، ولا تضبطه أداة التثبيت. **اضبطه فقط إذا كنت تملك ذلك
الإذن بنفسك.**

بعض المصادر معطّلة افتراضيًا لأن شروطها أو ملف robots.txt لديها يحظر الاستخدام الآلي دون
إذن. إذا كان لديك إذن من الناشر، ففعّل المصدر بإضافة رمزه إلى
`WLM_PERMITTED`، مفصولًا بفواصل، في كتلة `env`: `"WLM_PERMITTED": "in,de"`.

| الرمز | المصدر |
|---|---|
| `az` | أذربيجان: e-qanun.az (وزارة العدل) |
| `bh` | البحرين: هيئة التشريع والرأي القانوني (lloc.gov.bh) |
| `co` | كولومبيا: Función Pública، Gestor Normativo (التشريعات الموحَّدة) |
| `de` | ألمانيا: NeuRIS (بوابة المعلومات القانونية الاتحادية، خدمة تجريبية) |
| `difc` | محاكم مركز دبي المالي العالمي (difccourts.ae) |
| `gr` | اليونان: المطبعة الوطنية، البحث في الجريدة الرسمية (search.et.gr) |
| `mu` | موريشيوس: المحكمة العليا (supremecourt.govmu.org) |
| `sg` | سنغافورة: أحكام المحاكم (elitigation.sg) |

بدون إذن، يقول Fontes: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
