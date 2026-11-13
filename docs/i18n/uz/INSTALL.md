> Bu mashina yordamida qilingan tarjima. Ingliz tilidagi matn asosiy hisoblanadi.

# Fontes’ni oʻrnatish

Fontes AI ilovangizga 120 dan ortiq yurisdiksiyada sud qarorlari va qonunchilikni sud va davlat
veb-saytlarida jonli qidirish imkonini beradi. Har bir natija asl nusxaga havola beradi. Bu
standart MCP server, shuning uchun u lokal MCP serverni ishga tushira oladigan har qanday ilovada
ishlaydi: Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Gemini CLI,
Windsurf, Zed, LM Studio, Cline va boshqalar.

Ilovangizni tanlang, uning qadamlarini bajaring, soʻng
[ishlayotganini tekshiring](#ishlashini-tekshirish).

## Claude Desktop

1. Fontes `.mcpb` faylini
   [soʻnggi relizdan](https://github.com/ykarapazar/fontes/releases/latest) yuklab oling.
2. Uni ikki marta bosing. Claude Desktop uni ochadi.
3. **Install** tugmasini bosing.

## Codex

Terminalda:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI va Codex IDE kengaytmasi bu sozlamani birgalikda ishlatadi (`~/.codex/config.toml`).
Sizga [uv](#sizga-uv-kerak) kerak.

## Claude Code

Terminalda:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Sizga [uv](#sizga-uv-kerak) kerak.

## Boshqa ilovalar

Ularning har biriga [uv](#sizga-uv-kerak) kerak. Yozuvni qoʻshing, saqlang, soʻng ilovani yopib,
qayta oching.

**Cursor:** `~/.cursor/mcp.json` da (barcha loyihalar uchun) yoki `.cursor/mcp.json` da (bitta
loyiha uchun):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** buyruqlar palitrasidan (Command Palette) **MCP: Add Server** ni
ishga tushiring, **Command (stdio)** ni tanlang, `uvx fontes-mcp` ni kiriting va serverga `fontes`
deb nom bering. Yoki buni `~/.copilot/mcp-config.json` ga qoʻshing:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

VS Code’ning eski sozlamalari `.vscode/mcp.json` dan foydalanadi, unda yuqori darajadagi kalit
`mcpServers` emas, `servers`.

**Gemini CLI:** terminalda: `gemini mcp add -s user fontes uvx fontes-mcp`. Yoki buni
`~/.gemini/settings.json` ga qoʻshing:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** sozlamalar faylingizni oching (**zed: open settings file**) va qoʻshing:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** oʻng yon paneldagi **Program** yorligʻini oching, **Install → Edit mcp.json** ni
bosing va qoʻshing:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** **MCP Servers** belgisini bosing, **Configure** yorligʻini oching, **Configure MCP
Servers** ni bosing va LM Studio uchun boʻlgan `mcpServers` yozuvining xuddi oʻzini qoʻshing.

**Claude Desktop, qoʻlda** (`.mcpb` fayli oʻrniga): xuddi shu `mcpServers` yozuvini
`claude_desktop_config.json` ga qoʻshing (macOS: `~/Library/Application Support/Claude/`,
Windows: `%APPDATA%\Claude\`).

**Boshqa har qanday MCP ilovasi** (Windsurf va boshqalar): uning oʻz hujjatlari MCP serverlarini
qayerda saqlashini aytadi. Aksariyati xuddi shu yozuvni qabul qiladi: buyruq `uvx`, argument
`fontes`.

Agar ilova `uvx` ni topa olmasa, uning toʻliq yoʻlidan foydalaning (macOS va Linux’da uni
`which uvx` chiqarib beradi).

## Sizga uv kerak

Codex, Claude Code va boshqa ilovalar Fontes’ni `uvx` bilan ishga tushiradi, u esa Astral’ning
kichik bepul vositasi boʻlgan **uv** bilan birga keladi. Uni oʻrnatish uchun
[Astral qoʻllanmasiga](https://docs.astral.sh/uv/getting-started/installation/) qarang yoki
ishga tushiring:

- macOS yoki Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Kalitlar

Baʼzi manbalar bepul kalit talab qiladi: [KEYS.md](KEYS.md) ga qarang.

## Ishlashini tekshirish

Yangi suhbatda soʻrang: *“Fontes qaysi yurisdiksiyalarda qidira oladi?”* Ilova mamlakatlar
roʻyxati bilan javob berishi kerak. Agar bunday boʻlmasa, ilovani yana bir bor yopib, qayta
oching.

## Bir bosishda ishlaydigan oʻrnatuvchi (tez orada)

Tez orada Fontes’ni barcha ilovalaringizda birdaniga sozlaydigan Mac va Windows oʻrnatuvchisi
chiqadi. U Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini
CLI, Zed, LM Studio va Cline’ni sozlaydi. U chiqqandan keyin:

**Boshlashdan oldin:** bu ilovalarning har birini butunlay yoping. Bu ayniqsa Claude Code uchun
muhim: u ishlayotganda `~/.claude.json` ni qayta yozadi va oʻrnatuvchi kiritgan oʻzgarishni bekor
qilishi mumkin. Agar Claude Code’ni yopa olmasangiz, Fontes’ni unga `claude mcp add` bilan
qoʻshing ([Claude Code](#claude-code) ga qarang).

**Mac**

1. Yuklab olingan **Fontes Installer** jildini oching.
2. **Install Fontes.command** ni ikki marta bosing.
   - Agar Mac’ingiz fayl “cannot be opened because it is from an unidentified developer” deb
     aytsa: faylni sichqonchaning oʻng tugmasi bilan (yoki Control tugmasini bosib turib) bosing,
     **Open** ni tanlang, soʻng yana **Open** ni bosing. Buni faqat bir marta qilasiz.
3. Oyna ochiladi va anonim foydalanish hisoblarini yuborish-yubormaslikni soʻraydi; “yoʻq” deb
   javob berish uchun Enter tugmasini bosing.
4. U kalitlarni hozir qoʻshish-qoʻshmaslikni soʻraydi. Oʻtkazib yuborish uchun Enter tugmasini
   bosing; [Kalitlar qadami](#kalitlar-qadami) ga qarang.
5. U **Tayyor** deb koʻrsatganda, AI ilovalaringizni qayta oching.

**Windows**

1. Yuklab olingan **Fontes Installer** arxivini oching (oʻng tugma → Extract All).
2. **Install Fontes.cmd** ni ikki marta bosing.
   - Agar Windows “Windows protected your PC” deb koʻrsatsa: **More info** ni, soʻng
     **Run anyway** ni bosing.
3. Anonim foydalanish hisoblarini yuborish-yubormaslikni soʻraganda, “yoʻq” deb javob berish
   uchun Enter tugmasini bosing.
4. U kalitlarni hozir qoʻshish-qoʻshmaslikni soʻraydi. Oʻtkazib yuborish uchun Enter tugmasini
   bosing; [Kalitlar qadami](#kalitlar-qadami) ga qarang.
5. U **Tayyor** deb koʻrsatganda, AI ilovalaringizni qayta oching. Agar ulardan biri hali ham
   ishlayotgan boʻlsa, uni butunlay yoping (tizim lagani, soat yonidagi joydan ham) va qayta
   oching.

Oxirida oʻrnatuvchi oʻzi sozlagan ilovalar roʻyxatini chiqaradi.

### Qaysi ilovalarni sozlaydi

U ilovani faqat shu ilovaning sozlamalar jildi kompyuteringizda allaqachon mavjud boʻlsa
sozlaydi. Claude Code faqat `~/.claude.json` mavjud boʻlsa sozlanadi. Claude Desktop har doim
sozlanadi. Har bir ilova ushbu faylda bitta `fontes` yozuvini oladi:

| Ilova | Fayl (Mac va Linux) | Fayl (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json` va Microsoft Store versiyasining oʻz nusxasi |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, yoki eski versiyalarda `~/.codeium/windsurf/mcp_config.json` | `%APPDATA%\devin\mcp_config.json` yoki `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code `~/.copilot` yoki VS Code’ning oʻz sozlamalar jildi mavjud boʻlsa sozlanadi.

Ikki ilovaga yana bitta qadam kerak:

- **Windsurf:** qayta ochgandan keyin Cascade’da yangilash (refresh) tugmasini bosing.
- **VS Code’ning eski kengaytmasidagi Cline:** Fontes’ni qoʻlda qoʻshing
  ([Cline](#boshqa-ilovalar) ga qarang).

### Kalitlar qadami

Oʻrnatishdan soʻng darhol oʻrnatuvchi Fransiya va AQSh uchun bepul kalitlarni qoʻshishni taklif
qiladi. Ularni keyinroq qoʻshish yoki oʻzgartirish uchun:

- **Mac:** oʻrnatuvchi jildidagi **Add or change keys.command** ni ikki marta bosing yoki Fontes
  Installer ilovasini qayta oching va **Kalitlarni qoʻshish yoki oʻzgartirish** ni tanlang.
- **Windows:** oʻrnatuvchi jildidagi **Add or change keys.cmd** ni ikki marta bosing.

Yozilgan matn yashirin. Kalitlar Fontes allaqachon oʻrnatilgan har bir ilovaga yoziladi. Shundan
soʻng ilovalarni yopib, qayta oching. Kalitlarni qayerdan olish va ular nimani ochishi:
[KEYS.md](KEYS.md).

### Zaxira nusxalar, qayta ishga tushirish va olib tashlash

Oʻrnatuvchi faqat `fontes` yozuvini oʻzgartiradi. Boshqa barcha sozlamalar va izohlar oʻzgarishsiz
qoladi. Faylni oʻzgartirishdan oldin u uning yoniga `<file>.fontes-backup-<date>` nomli nusxa
saqlaydi. Kalitlar qoʻshilgandan keyin yaratilgan nusxalarda shu kalitlar boʻladi; keraksiz
boʻlganlarini oʻchiring. U uv’ni ham oʻrnatadi. Uni qayta ishga tushirish xavfsiz: u sozlamani
tiklaydi va boshqa hech narsani oʻzgartirmaydi.

Fontes’ni olib tashlash uchun **Uninstall Fontes.command** (Mac) yoki **Uninstall Fontes.cmd**
(Windows) ni ikki marta bosing. U barcha ilovalardan `fontes` yozuvini, kalitlar bilan birga,
olib tashlaydi. Boshqa sozlamalaringiz va zaxira nusxalar qoladi.

## Yangilanishlar

- **Oʻrnatuvchi va `.mcpb` fayli:** hech narsa qilishingiz shart emas. Kuniga bir marta, ilova
  ishga tushganda, Fontes fon rejimida yangiroq versiya bor-yoʻqligini tekshiradi va uni
  tayyorlaydi; ilova keyingi safar ishga tushganda u ishlatiladi. Agar yangilanishni yuklab
  boʻlmasa yoki u ishlamasa, Fontes ishlagan versiyadan foydalanishda davom etadi.
- **`uvx`:** Fontes yangiroq versiya haqida yurisdiksiyalar roʻyxatining boshida xabar beradi.
  Har doim eng yangi versiyani ishga tushirish uchun `fontes-mcp` oʻrniga `fontes-mcp@latest` dan
  foydalaning.

Buning uchun siz yoki qidiruvlaringiz haqida hech qanday maʼlumot hech qayerga yuborilmaydi.

## Maxfiylik

Fontes sukut boʻyicha siz yoki qidiruvlaringiz haqida hech narsa yubormaydi. Foydalanish hisoblari
ixtiyoriy (opt-in), xatolik hisoboti esa faqat siz uni koʻrib, tasdiqlaganingizdan keyin
yuboriladi. Tafsilotlar: [PRIVACY.md](PRIVACY.md).

## Olib tashlash

`fontes` yozuvini ilovangizning MCP sozlamalaridan olib tashlang (Claude Code’da:
`claude mcp remove fontes`), soʻng ilovani yopib, qayta oching.

## Bilib qoʻyish foydali

Fontes ochiq manbalarni, asosan sud va davlat veb-saytlarini oʻqiydi. Norasmiy manbalarni u
javoblarida belgilaydi. Qaror yoki normaga tayanishdan oldin har doim manba havolasini oching.

Agar biror narsa notoʻgʻri ketsa, fontesmcp@proton.me manziliga nima qilganingiz va qanday xatoni
koʻrganingizni yozing.

## Unga tayanishdan oldin

- Fontes yuridik maslahat emas, tadqiqot vositasi. Undan foydalanish hech kimni sizning
  advokatingizga aylantirmaydi.
- U “boricha” (“as is”), kafolatsiz taqdim etiladi va uning mualliflari qonun ruxsat bergan
  darajada undan qanday foydalanishingiz uchun javobgar emas. Toʻliq shartlar
  [litsenziyada](../../../LICENSE) (Apache 2.0).
