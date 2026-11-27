> זהו תרגום בסיוע מכונה. הנוסח האנגלי הוא הנוסח המחייב.

# מפתחות API

כמעט כל מקור ב-Fontes עובד בלי מפתח. שלושה דורשים מפתח חינמי:

| מפתח | מה הוא פותח | בלעדיו |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | צרפת: Judilibre (פסקי דין) ו-Légifrance (חקיקה) | צרפת כבויה. `list_jurisdictions` מציג אותה כלא פעילה. |
| `WLM_US_GOVINFO_KEY` | ארצות הברית: חיפוש govinfo (פסקי דין של בתי משפט פדרליים, Statutes at Large, חוקים ציבוריים) | Fontes משתמש ב-`DEMO_KEY` המשותף: כ-10 חיפושים ביום לכל כתובת IP. פתיחת פסק דין ידוע וה-US Code אינם דורשים מפתח. |
| `WLM_US_COURTLISTENER_KEY` | בתי המשפט של מדינות ארצות הברית (`us-states`): פסקי דין של בתי המשפט העליונים ושל ערכאות הערעור בכל 50 המדינות וב-DC, מתוך CourtListener | פסיקת המדינות בארצות הברית כבויה. `list_jurisdictions` מציג אותה כלא פעילה. |

המפתחות אופציונליים. אפשר להוסיף אותם מאוחר יותר.

## הוספת מפתח

**באמצעות תוכנית ההתקנה.** לאחר ש-Fontes מוגדר, תוכנית ההתקנה מציעה להוסיף מפתחות. ב-Mac, לחצו
**הוספת מפתחות**, או **סיום** כדי לדלג; ב-Windows, ענו על השאלה (הקישו Enter כדי לדלג). כדי להוסיף או לשנות מפתחות מאוחר יותר, הפעילו את
**הוספה או שינוי של מפתחות**:

- Mac: פתחו שוב את היישום Fontes Installer ובחרו **הוספה או שינוי של מפתחות**.
- Windows: פתחו את תפריט Start, ואז **Fontes** → **הוספה או שינוי של מפתחות**.

ההקלדה מוסתרת. לכל מפתח: הדביקו אותו, הקישו Enter כדי לשמור את מה שקיים, או הקלידו `-` כדי
להסיר אותו. המפתחות נכנסים לכל יישום שכבר יש בו את Fontes.

**באמצעות הרחבת Claude Desktop ‏(.mcpb).** פתחו Claude > Settings > Extensions > Fontes ומלאו
את השדות. כולם אופציונליים.

**ידנית.** הוסיפו את המשתנים לבלוק `env` של הרשומה `fontes` בהגדרות ה-MCP של היישום שלכם:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

הפעילו מחדש את היישום לאחר כל שינוי.

## צרפת: PISTE (חינם)

1. צרו חשבון ב-[piste.gouv.fr](https://piste.gouv.fr). פירוש הדבר קבלת תנאי PISTE ‏(CGU).
2. עברו אל API > **Consentement CGU API**. קבלו את התנאים עבור **JUDILIBRE** ו-**Légifrance** ‏(production).
3. צרו **production application**. ה-`APP_SANDBOX` שנוצר עבורכם אינו יכול להגיע לסביבת production.
   תחת "Modifier l'application", סמנו **JUDILIBRE (production)** ו-**Légifrance (production)**, ואז החילו.
4. פתחו את הלשונית **Authentification** של האפליקציה. העתיקו את ה-`client_id` ואת ה-`client_secret`.
5. הפעילו את **הוספה או שינוי של מפתחות** והדביקו אותם.

התנאים, בקצרה:

- נתונים: Licence Ouverte / Etalab 2.0. שימוש חוזר, כולל שימוש חוזר מסחרי, מותר בכפוף לייחוס.
- אל תפרסמו ואל תשתפו את פרטי הגישה שלכם. הודיעו ל-PISTE אם הם דלפו.
- ה-API של Légifrance הוא שירות בטא. הוא עשוי להיות מושעה, ויש לו מכסות (לשנייה, לדקה וליום).
- הטקסטים של Légifrance אינם הנוסח המוסמך. רק ה-PDF החתום של ה-Journal officiel הוא המוסמך.
- Judilibre: אין להשתמש בשמות שופטים או רשמים כדי להעריך, להשוות או לחזות את עבודתם
  (Code de l'organisation judiciaire art. L111-13; עבירה פלילית).
- Judilibre: פעלו לפי ה-GDPR. אל תנסו לזהות מחדש את הצדדים.

המכסות שלכם מופיעות ב-PISTE תחת API Sélectionnées > Actions > Consulter les quotas.

## ארצות הברית: api.data.gov (חינם)

1. עברו אל [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (המפתח מוצג על המסך)
   או [api.data.gov/signup](https://api.data.gov/signup/) (המפתח נשלח אליכם בדוא"ל).
2. הזינו את שמכם ואת כתובת הדוא"ל שלכם. השדה "how will you use it" אופציונלי.
3. העתיקו את המפתח בן 40 התווים.
4. הפעילו את **הוספה או שינוי של מפתחות** והדביקו אותו כמפתח של ארצות הברית.

התנאים, בקצרה:

- עם מפתח משלכם, govinfo מאפשר עד 36,000 בקשות בשעה.
- לא מצאנו תנאי שימוש ייעודיים ל-API ‏(api.data.gov/terms/ אינו קיים). לא אומת.
  ראו את [המדיניות של govinfo](https://www.govinfo.gov/about/policies) ואת
  [מדיניות הפרטיות של data.gov](https://data.gov/privacy-policy/).
- שמרו את המפתח לעצמכם.

## בתי המשפט של מדינות ארצות הברית: CourtListener (חינם)

CourtListener מופעל בידי [Free Law Project](https://free.law), ארגון ללא כוונת רווח שאוסף פסקי דין של בתי משפט בארצות הברית מאז 2010 ומעמיד אותם חינם לכולם. לפי הספירה שלו עצמו, הוא מחזיק ביותר מתשעה מיליון פסקי דין. הוא אינו מקור רשמי: בתי המשפט מפרסמים בעצמם את פסקי הדין שלהם, ו-CourtListener אוסף אותם מאתרי בתי המשפט ומדוחות משפט סרוקים. כל תשובה של Fontes שמגיעה ממנו אומרת זאת. Fontes אינו קשור ל-Free Law Project.

1. צרו חשבון חינמי ב-[courtlistener.com](https://www.courtlistener.com/sign-in/).
2. פתחו את הפרופיל שלכם והעתיקו את אסימון ה-API שלכם.
3. הפעילו את **הוספה או שינוי של מפתחות** והדביקו אותו כמפתח CourtListener.

התנאים, בקצרה ([התנאים המלאים](https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies)):

- האסימון הוא שלכם בלבד: אין לשתף אותו, לאגד אותו עם אחרים או למכור אותו מחדש, ואין להשתמש בכמה חשבונות.
- אתם אחראים למה שאפליקציית בינה מלאכותית עושה באסימון שלכם.
- אין להציג ניתוח של בינה מלאכותית את הנתונים שלהם כמי שהופק, אושר או נבדק בידי Free Law Project.
- חשבון חינמי מאפשר 5 בקשות בדקה, 50 בשעה ו-125 ביום. חיפוש הוא בקשה אחת; פתיחת פסק דין היא שתיים. חברות ב-Free Law Project מעלה את המגבלות.
- CourtListener אינו מבטיח דיוק. בדקו פסק דין מול העותק של בית המשפט לפני שאתם מסתמכים עליו.

## היכן נשמרים המפתחות

- **תוכנית ההתקנה או ידנית:** כטקסט רגיל בקובץ הגדרות ה-MCP של כל יישום, בבלוק `env` של
  הרשומה `fontes`. כל מי שיכול לקרוא את קובצי המשתמש שלכם יכול לקרוא את המפתחות.
  - Claude Desktop: ‏`~/Library/Application Support/Claude/claude_desktop_config.json` ‏(Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` ‏(Windows)
  - Claude Code: ‏`~/.claude.json`
  - Codex: ‏`~/.codex/config.toml`
  - Cursor: ‏`~/.cursor/mcp.json`
  - VS Code (Copilot): ‏`~/.copilot/mcp-config.json`
  - Windsurf: ‏`~/.config/devin/mcp_config.json` או `~/.codeium/windsurf/mcp_config.json`
    ‏(Windows: ‏`%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: ‏`~/.gemini/settings.json`
  - Zed: ‏`~/.config/zed/settings.json` ‏(Windows: ‏`%APPDATA%\Zed\settings.json`)
  - LM Studio: ‏`~/.lmstudio/mcp.json`
  - Cline: ‏`~/.cline/data/settings/cline_mcp_settings.json`
- **הרחבת Claude Desktop ‏(.mcpb):** ‏Claude שומר שדות אלה בהגדרות שלו ומגן עליהם באמצעות
  האחסון המאובטח של המערכת שלכם (Keychain ב-Mac, ‏Credential Manager ב-Windows).

לפני כל שינוי, תוכנית ההתקנה שומרת עותק של קובץ ההגדרות לידו
(`<file>.fontes-backup-<time>`). עותקים שנוצרו לאחר שהוספתם מפתחות מכילים גם הם את המפתחות.
מחקו עותקים ישנים שאינכם צריכים.

## שינוי או הסרה של מפתח

- הפעילו את **הוספה או שינוי של מפתחות**. הדביקו מפתח חדש כדי להחליף אותו, או הקלידו `-` כדי להסיר אותו.
- או ערכו את בלוק ה-`env` ידנית והפעילו מחדש את היישום.
- הסרת Fontes מסירה את כל הרשומה שלו, כולל המפתחות. היא אינה מוחקת את עותקי הגיבוי.
- אם מפתח דלף, החליפו אותו גם במקור: ב-PISTE, צרו פרטי גישה חדשים לאפליקציה שלכם;
  ב-api.data.gov, הירשמו לקבלת מפתח חדש.

## הודעות שעשויות להופיע

| הודעה | משמעות |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | אין מפתח לצרפת. הוסיפו אחד. |
| `Inactive: needs a free PISTE account. ...` (ב-`list_jurisdictions`) | כנ"ל. |
| `PISTE refused the client credentials ...` | ה-ID או ה-secret שגויים או שאינם תקפים עוד. העתיקו את שניהם שוב מהלשונית Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | האפליקציה שלכם אינה רשומה ל-API הזה, או שלא קיבלתם את התנאים שלו. ראו שלבים 2 ו-3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | אין מפתח לארצות הברית. החיפוש עובד למספר קריאות ביום. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | מפתח ההדגמה מוצה. הוסיפו מפתח משלכם. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | המפתח שגוי, או שעדיין לא אושר מהדוא"ל. |

ערך ריק נחשב כהיעדר מפתח.

## הרשאות (WLM_PERMITTED)

זה אינו מפתח API, ותוכנית ההתקנה אינה מגדירה אותו. **הגדירו אותו רק אם אתם עצמכם מחזיקים
ברשות זו.**

חלק מהמקורות כבויים כברירת מחדל משום שהתנאים או ה-robots.txt שלהם אוסרים שימוש אוטומטי ללא
רשות. אם יש לכם רשות מהמפרסם, הפעילו מקור על ידי הוספת הקוד שלו ל-`WLM_PERMITTED`, מופרד
בפסיקים, בבלוק `env`: `"WLM_PERMITTED": "in,de"`.

| קוד | מקור |
|---|---|
| `az` | אזרבייג'ן: e-qanun.az (משרד המשפטים) |
| `bh` | בחריין: Legislation and Legal Opinion Commission ‏(lloc.gov.bh) |
| `co` | קולומביה: Función Pública, Gestor Normativo (חקיקה בנוסח משולב) |
| `de` | גרמניה: NeuRIS (פורטל המידע המשפטי הפדרלי, שירות ניסיוני) |
| `difc` | בתי המשפט של Dubai International Financial Centre ‏(difccourts.ae) |
| `gr` | יוון: National Printing Office, חיפוש ב-Government Gazette ‏(search.et.gr) |
| `mu` | מאוריציוס: Supreme Court ‏(supremecourt.govmu.org) |
| `sg` | סינגפור: פסקי דין של בתי המשפט (elitigation.sg) |

ללא רשות, Fontes אומר: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
