> Bu mashina yordamida qilingan tarjima. Ingliz tilidagi matn asosiy hisoblanadi.

# API kalitlari

Fontes’ning deyarli har bir manbasi kalitsiz ishlaydi. Ikkitasiga bepul kalit kerak:

| Kalit | Nimani ochadi | Usiz |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Fransiya: Judilibre (sud qarorlari) va Légifrance (qonunchilik) | Fransiya oʻchiq. `list_jurisdictions` uni nofaol deb koʻrsatadi. |
| `WLM_US_GOVINFO_KEY` | Amerika Qoʻshma Shtatlari: govinfo qidiruvi (federal sud qarorlari, Statutes at Large, public laws) | Fontes umumiy `DEMO_KEY` dan foydalanadi: har bir IP manzil uchun kuniga taxminan 10 ta qidiruv. Maʼlum qarorni ochish va US Code uchun kalit kerak emas. |

Kalitlar ixtiyoriy. Ularni keyinroq qoʻshishingiz mumkin.

## Kalit qoʻshish

**Oʻrnatuvchi bilan.** Fontes sozlangach, oʻrnatuvchi kalitlar qoʻshishni taklif qiladi. Mac’da
**Kalitlarni qoʻshish** ni yoki oʻtkazib yuborish uchun **Tayyor** ni bosing; Windows’da savolga
javob bering (oʻtkazib yuborish uchun Enter tugmasini bosing). Kalitlarni
keyinroq qoʻshish yoki oʻzgartirish uchun **Add or change keys** ni ishga tushiring:

- Mac: Fontes Installer ilovasini qayta oching va **Kalitlarni qoʻshish yoki oʻzgartirish** ni
  tanlang.
- Windows: oʻrnatuvchi jildidagi `Add or change keys.cmd` ni ikki marta bosing. Windows oʻrnatish
  dasturi, mavjud boʻlganda, uni Start menyusi > Fontes’ga ham joylashtiradi.

Yozilgan matn yashirin. Har bir kalit uchun: uni joylashtiring, mavjudini saqlab qolish uchun
Enter tugmasini bosing yoki olib tashlash uchun `-` yozing. Kalitlar Fontes allaqachon oʻrnatilgan
har bir ilovaga yoziladi.

**Claude Desktop kengaytmasi (.mcpb) bilan.** Claude > Settings > Extensions > Fontes ni oching va
maydonlarni toʻldiring. Ularning hammasi ixtiyoriy.

**Qoʻlda.** Oʻzgaruvchilarni ilovangiz MCP sozlamasidagi `fontes` yozuvining `env` blokiga
qoʻshing:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Har qanday oʻzgarishdan keyin ilovani qayta ishga tushiring.

## Fransiya: PISTE (bepul)

1. [piste.gouv.fr](https://piste.gouv.fr) da hisob yarating. Bu PISTE shartlarini (CGU) qabul qilishni anglatadi.
2. API > **Consentement CGU API** ga oʻting. **JUDILIBRE** va **Légifrance** (production) shartlarini qabul qiling.
3. **Ishlab chiqarish ilovasini** (production application) yarating. Siz uchun yaratilgan
   `APP_SANDBOX` ishlab chiqarish muhitiga kira olmaydi. “Modifier l'application” da
   **JUDILIBRE (production)** va **Légifrance (production)** ni belgilang, soʻng qoʻllang.
4. Ilovaning **Authentification** yorligʻini oching. `client_id` va `client_secret` ni nusxalang.
5. **Add or change keys** ni ishga tushiring va ularni joylashtiring.

Shartlar qisqacha:

- Maʼlumotlar: Licence Ouverte / Etalab 2.0. Qayta foydalanish, shu jumladan tijoriy, manba koʻrsatilgan holda ruxsat etiladi.
- Kirish maʼlumotlaringizni eʼlon qilmang va boshqalarga bermang. Agar ular oshkor boʻlsa, PISTE’ga xabar bering.
- Légifrance API beta xizmat. U toʻxtatilishi mumkin va kvotalari bor (soniyada, daqiqada va kunda).
- Légifrance matnlari haqiqiy (autentik) versiya emas. Faqat imzolangan Journal officiel PDF haqiqiy hisoblanadi.
- Judilibre: sudyalar yoki sud xodimlarining ismlaridan ularning faoliyatini baholash, solishtirish
  yoki bashorat qilish uchun foydalanmang (Code de l'organisation judiciaire, L111-13-modda;
  jinoyat).
- Judilibre: GDPR’ga rioya qiling. Taraflarni qayta identifikatsiya qilishga urinmang.

Kvotalaringiz PISTE’da: API Sélectionnées > Actions > Consulter les quotas.

## Amerika Qoʻshma Shtatlari: api.data.gov (bepul)

1. [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) ga (kalit ekranda koʻrsatiladi)
   yoki [api.data.gov/signup](https://api.data.gov/signup/) ga (kalit sizga elektron pochta orqali
   yuboriladi) oʻting.
2. Ismingiz va elektron pochtangizni kiriting. “how will you use it” maydoni ixtiyoriy.
3. 40 belgili kalitni nusxalang.
4. **Add or change keys** ni ishga tushiring va uni AQSh kaliti sifatida joylashtiring.

Shartlar qisqacha:

- Oʻz kalitingiz bilan govinfo soatiga 36 000 tagacha soʻrovga ruxsat beradi.
- API’ga xos foydalanish shartlarini topa olmadik (api.data.gov/terms/ mavjud emas).
  Tasdiqlanmagan. [govinfo siyosatlari](https://www.govinfo.gov/about/policies) va
  [data.gov maxfiylik siyosati](https://data.gov/privacy-policy/) ga qarang.
- Kalitni oʻzingizda saqlang.

## Kalitlar qayerda saqlanadi

- **Oʻrnatuvchi bilan yoki qoʻlda:** oddiy matn sifatida har bir ilovaning MCP sozlamalar faylida,
  `fontes` yozuvining `env` blokida. Foydalanuvchi fayllaringizni oʻqiy oladigan har kim
  kalitlarni ham oʻqiy oladi.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` yoki `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Claude Desktop kengaytmasi (.mcpb):** Claude bu maydonlarni oʻz sozlamalarida saqlaydi va
  ularni tizimingizning xavfsiz saqlash joyi bilan himoya qiladi (Mac’da Keychain, Windows’da
  Credential Manager).

Har bir oʻzgarishdan oldin oʻrnatuvchi sozlamalar faylining nusxasini uning yonida saqlaydi
(`<file>.fontes-backup-<time>`). Kalitlar qoʻshilgandan keyin yaratilgan nusxalarda ham kalitlar
boʻladi. Kerak boʻlmagan eski nusxalarni oʻchiring.

## Kalitni oʻzgartirish yoki olib tashlash

- **Add or change keys** ni ishga tushiring. Almashtirish uchun yangi kalitni joylashtiring yoki olib tashlash uchun `-` yozing.
- Yoki `env` blokini qoʻlda tahrirlang va ilovani qayta ishga tushiring.
- Fontes’ni oʻchirish uning butun yozuvini, kalitlar bilan birga, olib tashlaydi. Zaxira nusxalarni oʻchirmaydi.
- Agar kalit oshkor boʻlgan boʻlsa, uni manbada ham almashtiring: PISTE’da ilovangiz uchun yangi
  kirish maʼlumotlarini yarating, api.data.gov uchun esa yangi kalitga roʻyxatdan oʻting.

## Koʻrishingiz mumkin boʻlgan xabarlar

| Xabar | Maʼnosi |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Fransiya kaliti yoʻq. Uni qoʻshing. |
| `Inactive: needs a free PISTE account. ...` (`list_jurisdictions` da) | Xuddi shu. |
| `PISTE refused the client credentials ...` | ID yoki secret notoʻgʻri yoki endi amal qilmaydi. Ikkalasini Authentification yorligʻidan qayta nusxalang. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Ilovangiz bu API’ga obuna boʻlmagan yoki uning shartlarini qabul qilmagansiz. 2- va 3-qadamlarga qarang. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | AQSh kaliti yoʻq. Qidiruv kuniga bir necha chaqiruv uchun ishlaydi. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Namoyish kaliti tugadi. Oʻz kalitingizni qoʻshing. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Kalit notoʻgʻri yoki hali elektron xatdan faollashtirilmagan. |

Boʻsh qiymat kalit yoʻqligi bilan bir xil.

## Ruxsatlar (WLM_PERMITTED)

Bu API kaliti emas va oʻrnatuvchi uni oʻrnatmaydi. **Uni faqat oʻzingizda shu ruxsat boʻlsa
oʻrnating.**

Baʼzi manbalar sukut boʻyicha oʻchiq, chunki ularning shartlari yoki robots.txt fayli ruxsatsiz
avtomatlashtirilgan foydalanishni taqiqlaydi. Agar nashriyotchining ruxsati boʻlsa, manbani uning
kodini `env` blokidagi `WLM_PERMITTED` ga vergul bilan ajratib qoʻshish orqali yoqing:
`"WLM_PERMITTED": "in,de"`.

| Kod | Manba |
|---|---|
| `az` | Ozarbayjon: e-qanun.az (Adliya vazirligi) |
| `bh` | Bahrayn: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Kolumbiya: Función Pública, Gestor Normativo (konsolidatsiyalangan qonunchilik) |
| `de` | Germaniya: NeuRIS (federal huquqiy axborot portali, sinov xizmati) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Gretsiya: Milliy bosmaxona, Hukumat axborotnomasi qidiruvi (search.et.gr) |
| `in` | Hindiston: India Code (indiacode.gov.in) |
| `mu` | Mavrikiy: Oliy sud (supremecourt.govmu.org) |
| `sg` | Singapur: sud qarorlari (elitigation.sg) |

Ruxsatsiz Fontes shunday xabar beradi: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
