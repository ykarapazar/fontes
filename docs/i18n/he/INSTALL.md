> זהו תרגום בסיוע מכונה. הנוסח האנגלי הוא הנוסח המחייב.

# התקנת Fontes

Fontes מאפשר ליישום ה-AI שלכם לאתר פסקי דין וחקיקה בזמן אמת באתרי בתי משפט וממשלות ביותר
מ-120 תחומי שיפוט. כל תוצאה מקשרת למקור. זהו שרת MCP סטנדרטי, ולכן הוא עובד בכל יישום שיכול
להפעיל שרת MCP מקומי: Claude Desktop, ‏Codex, ‏Claude Code, ‏Cursor, ‏VS Code (GitHub Copilot),
‏Gemini CLI, ‏Windsurf, ‏Zed, ‏LM Studio, ‏Cline ואחרים.

בחרו את היישום שלכם, בצעו את השלבים שלו, ואז [בדקו שזה עובד](#בדיקה-שזה-עובד).

## Claude Desktop

1. הורידו את קובץ ה-`.mcpb` של Fontes
   [מהגרסה האחרונה](https://github.com/ykarapazar/fontes/releases/latest).
2. לחצו עליו לחיצה כפולה. Claude Desktop פותח אותו.
3. לחצו על **Install**.

## Codex

בטרמינל:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

ה-Codex CLI והרחבת ה-IDE של Codex חולקים הגדרה זו (`~/.codex/config.toml`).
דרוש [uv](#דרוש-uv).

## Claude Code

בטרמינל:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

דרוש [uv](#דרוש-uv).

## יישומים אחרים

כל אחד מאלה דורש [uv](#דרוש-uv). הוסיפו את הרשומה, שמרו, ואז צאו מהיישום ופתחו אותו מחדש.

**Cursor:** בקובץ `~/.cursor/mcp.json` (כל הפרויקטים) או `.cursor/mcp.json` (פרויקט אחד):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** הריצו **MCP: Add Server** מתוך ה-Command Palette, בחרו
**Command (stdio)**, הזינו `uvx fontes-mcp` ותנו לשרת את השם `fontes`. או הוסיפו את זה
ל-`~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

הגדרות VS Code ישנות יותר משתמשות ב-`.vscode/mcp.json`, שבו המפתח העליון הוא `servers` במקום
`mcpServers`.

**Gemini CLI:** בטרמינל, `gemini mcp add -s user fontes uvx fontes-mcp`. או הוסיפו את זה
ל-`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** פתחו את קובץ ההגדרות שלכם (**zed: open settings file**) והוסיפו:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** בסרגל הצד הימני, פתחו את הלשונית **Program**, לחצו על **Install → Edit
mcp.json**, והוסיפו:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** לחצו על הסמל **MCP Servers**, פתחו את הלשונית **Configure**, לחצו על **Configure MCP
Servers**, והוסיפו את אותה רשומת `mcpServers` כמו ב-LM Studio.

**Claude Desktop, ידנית** (במקום קובץ ה-`.mcpb`): הוסיפו את אותה רשומת `mcpServers`
ל-`claude_desktop_config.json` ‏(macOS: ‏`~/Library/Application Support/Claude/`, ‏Windows:
‏`%APPDATA%\Claude\`).

**כל יישום MCP אחר** (Windsurf ואחרים): התיעוד שלו מציין היכן הוא שומר את שרתי ה-MCP שלו.
רובם מקבלים את אותה רשומה: הפקודה `uvx`, הארגומנט `fontes`.

אם היישום אינו מוצא את `uvx`, השתמשו בנתיב המלא שלו (ב-macOS וב-Linux, ‏`which uvx` מדפיס אותו).

## דרוש uv

Codex, ‏Claude Code והיישומים האחרים מפעילים את Fontes באמצעות `uvx`, שמגיע עם **uv**, כלי
קטן וחינמי של Astral. כדי להתקין אותו, ראו את
[המדריך של Astral](https://docs.astral.sh/uv/getting-started/installation/), או הריצו:

- macOS או Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows ‏(PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## מפתחות

חלק מהמקורות דורשים מפתח חינמי: ראו [KEYS.md](KEYS.md).

## בדיקה שזה עובד

בשיחה חדשה, שאלו: *"באילו תחומי שיפוט Fontes יכול לחפש?"* היישום אמור לענות ברשימת
מדינות. אם לא, צאו מהיישום ופתחו אותו מחדש פעם נוספת.

## תוכנית התקנה בלחיצה אחת (Mac ו-Windows)

תוכנית ההתקנה מגדירה את Fontes בכל היישומים שלכם בבת אחת: Claude Desktop, ‏Codex, ‏Claude Code,
‏Cursor, ‏VS Code (GitHub Copilot), ‏Windsurf, ‏Gemini CLI, ‏Zed, ‏LM Studio ו-Cline.

**לפני שמתחילים:** צאו לגמרי מכל אחד מהיישומים האלה. זה חשוב במיוחד ב-Claude Code: כל עוד הוא
פועל, הוא כותב מחדש את `~/.claude.json` ועלול לבטל את השינוי של תוכנית ההתקנה. אם אינכם יכולים
לצאת מ-Claude Code, הוסיפו אליו את Fontes באמצעות `claude mcp add` במקום זאת (ראו
[Claude Code](#claude-code)).

**Mac**

1. הורידו את תוכנית ההתקנה ל-Mac ‏(`Fontes-Installer-…-mac.zip`)
   מ[הגרסה האחרונה](https://github.com/ykarapazar/fontes/releases/latest) ולחצו עליה לחיצה כפולה כדי לחלץ אותה.
2. לחצו לחיצה כפולה על **Fontes Installer**. אם ה-Mac שלכם שואל אם לפתוח יישום שהורד
   מהאינטרנט, לחצו **פתח**.
3. בחרו **התקנה** ולחצו **אישור**. ההגדרה נמשכת כדקה.
4. הודעה מפרטת את היישומים שהיא הגדירה. לחצו **סיום**, ואז פתחו שוב את היישומים האלה. כדי להוסיף
   קודם את המפתחות החינמיים האופציונליים, לחצו במקום זאת **הוספת מפתחות**; ראו [שלב המפתחות](#שלב-המפתחות).

**Windows**

1. הורידו את תוכנית ההתקנה ל-Windows (`Fontes-Setup-….exe`) מ[הגרסה האחרונה](https://github.com/ykarapazar/fontes/releases/latest) ולחצו עליה לחיצה כפולה.
   - אם Windows מציג "Windows protected your PC": לחצו על **More info**, ואז על **Run anyway**.
2. לחצו **התקנה**. ייפתח חלון ויגדיר את Fontes.
3. כשנשאלים אם לשלוח ספירות שימוש אנונימיות, הקישו Enter עבור "לא".
4. הוא שואל אם להוסיף מפתחות עכשיו. הקישו Enter כדי לדלג; ראו [שלב המפתחות](#שלב-המפתחות).
5. כשמופיעה ההודעה **הסתיים**, פתחו שוב את יישומי ה-AI שלכם. אם אחד מהם עדיין פעל, סגרו
   אותו לגמרי (גם ממגש המערכת, ליד השעון) ופתחו אותו שוב.

בסיום, תוכנית ההתקנה מציגה את רשימת היישומים שהגדירה.

### אילו יישומים היא מגדירה

היא מגדירה יישום רק אם תיקיית ההגדרות של אותו יישום כבר קיימת במחשב שלכם. Claude Code מוגדר
רק אם `~/.claude.json` קיים. Claude Desktop מוגדר תמיד. כל יישום מקבל רשומה אחת, `fontes`,
בקובץ הזה:

| יישום | קובץ (Mac ו-Linux) | קובץ (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` ‏(Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, וגם העותק הנפרד של גרסת Microsoft Store |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, או `~/.codeium/windsurf/mcp_config.json` בגרסאות ישנות יותר | `%APPDATA%\devin\mcp_config.json`, או `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code מוגדר אם `~/.copilot` או תיקיית ההגדרות של VS Code עצמו קיימים.

שני יישומים דורשים צעד נוסף:

- **Windsurf:** לאחר שפותחים אותו מחדש, לחצו על רענון ב-Cascade.
- **Cline בתוך הרחבת VS Code הישנה יותר:** הוסיפו את Fontes ידנית (ראו [Cline](#יישומים-אחרים)).

### שלב המפתחות

מיד לאחר ההתקנה, תוכנית ההתקנה מציעה להוסיף את המפתחות החינמיים של צרפת וארצות הברית. כדי
להוסיף או לשנות אותם מאוחר יותר:

- **Mac:** פתחו שוב את **Fontes Installer** ובחרו **הוספה או שינוי של מפתחות**.
- **Windows:** פתחו את תפריט Start, ואז **Fontes** → **Add or change keys**.

ההקלדה מוסתרת. המפתחות נכנסים לכל יישום שכבר יש בו את Fontes. לאחר מכן צאו מהיישומים ופתחו
אותם מחדש. היכן משיגים את המפתחות ומה הם פותחים: [KEYS.md](KEYS.md).

### גיבויים, הרצות חוזרות והסרה

תוכנית ההתקנה משנה רק את הרשומה `fontes`. כל הגדרה והערה אחרת נשארות כפי שהיו. לפני שהיא
משנה קובץ, היא שומרת עותק לידו, בשם `<file>.fontes-backup-<date>`. עותקים שנוצרו לאחר שהוספתם
מפתחות מכילים את המפתחות האלה: מחקו את אלה שאינכם צריכים עוד. היא גם מתקינה את uv. הרצה
חוזרת שלה בטוחה: היא מתקנת את ההגדרה ואינה משנה שום דבר אחר.

כדי להסיר את Fontes, פתחו את **Fontes Installer** ובחרו **הסרה** ‏(Mac), או הסירו את
**Fontes** בהגדרות → יישומים ‏(Windows). היא מסירה את הרשומה `fontes`, כולל המפתחות, מכל היישומים. ההגדרות האחרות שלכם
ועותקי הגיבוי נשארים.

## עדכונים

- **תוכנית ההתקנה וקובץ ה-`.mcpb`:** אינכם צריכים לעשות דבר. פעם ביום, כשהיישום מופעל,
  Fontes בודק ברקע אם יש גרסה חדשה יותר ומכין אותה; בהפעלה הבאה של היישום הוא משתמש בה.
  אם לא ניתן להוריד עדכון או שהוא אינו עובד, Fontes ממשיך להשתמש בגרסה שעבדה.
- **`uvx`:** ‏Fontes מודיע לכם כשיש גרסה חדשה יותר, בראש רשימת תחומי השיפוט שלו. כדי להריץ תמיד
  את הגרסה החדשה ביותר, השתמשו ב-`fontes-mcp@latest` במקום `fontes-mcp`.

שום מידע עליכם או על החיפושים שלכם אינו נשלח לשום מקום לשם כך.

## פרטיות

Fontes אינו שולח שום דבר עליכם או על החיפושים שלכם כברירת מחדל. ספירות השימוש הן בהסכמה
מפורשת בלבד (opt-in), ודיווח על באג נשלח רק לאחר שראיתם אותו ואישרתם. פרטים: [PRIVACY.md](PRIVACY.md).

## הסרת Fontes

הסירו את הרשומה `fontes` מהגדרות ה-MCP של היישום שלכם (ב-Claude Code:
`claude mcp remove fontes`), ואז צאו מהיישום ופתחו אותו מחדש.

## כדאי לדעת

Fontes קורא מקורות ציבוריים, בעיקר אתרי בתי משפט וממשלות. הוא מסמן בתשובותיו מקורות לא
רשמיים. פתחו תמיד את הקישור למקור לפני שאתם מסתמכים על פסק דין או על הוראה.

אם משהו משתבש, שלחו בדוא"ל את מה שעשיתם ואת השגיאה שראיתם אל fontesmcp@proton.me.

## לפני שמסתמכים עליו

- Fontes הוא כלי מחקר, לא ייעוץ משפטי. השימוש בו אינו הופך אף אחד לעורך הדין שלכם.
- הוא מסופק "כמות שהוא" (as is), ללא אחריות, ומחבריו אינם אחראים לאופן השימוש בו, ככל
  שהדין מתיר. התנאים המלאים נמצאים [ברישיון](../../../LICENSE) ‏(Apache 2.0).
