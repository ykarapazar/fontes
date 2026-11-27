> Bu mashina yordamida qilingan tarjima. Ingliz tilidagi matn asosiy hisoblanadi.

# Fontes: savol va javoblar

## Fontes nima

Bepul, ochiq kodli MCP server (Apache 2.0). U Model Context Protocol’ni qoʻllab-quvvatlaydigan
har qanday ilovaga (Claude, Codex, Cursor, VS Code, Gemini CLI va boshqalar) sud qarorlari va
qonunchilikni sud va davlat veb-saytlarida jonli qidirish imkonini beradi: 125 ta yurisdiksiya va
xalqaro sudlarda, shuningdek Lexifina yozuvi orqali yana 91 ta mamlakatda (quyida qarang). Har bir
natija oʻz manbasini koʻrsatadi va asl nusxaga havola beradi.

## Matnlar rasmiymi

Asosan ha, lekin har doim emas.

- Manbalarning aksariyatini sud, vazirlik yoki rasmiy nashr boshqaradi.
- Baʼzi konsolidatsiyalangan matnlarni davlat organi eʼlon qiladi, lekin ular ochiqdan-ochiq
  norasmiy: faqat rasmiy nashr haqiqiy hisoblanadi.
- Bir nechta manba umuman davlat veb-sayti emas (masalan, LexiVox, LawPhil, Maqam, Wikisource).

Fontes ulardan biridan kelgan har bir javobga “Unofficial source” izohini qoʻshadi. Biror narsani
keltirishdan oldin rasmiy nashrni tekshiring. [README](README.md#qamrov) dagi qamrov jadvali va
`list_jurisdictions` har bir yurisdiksiyaning manbasini koʻrsatadi.

## Qaysi yurisdiksiyalarni qamrab oladi va qanchalik yaxshi

125 ta adapter: BMTning 108 aʼzo davlati, Gonkong, Kosovo, Falastin, Tayvan, DIFC sudlari, AQSh shtatlari sudlari va 11 ta
xalqaro sud va organ (masalan, Inson huquqlari boʻyicha Yevropa sudi, Yevropa Ittifoqi, Xalqaro
sud va Jahon savdo tashkiloti).

Qamrov keskin farq qiladi. Qatʼiy qoidaga koʻra (umumiy yurisdiksiyadagi eng yuqori sudning
pretsedent qarorlari yoki konstitutsiya va asosiy hujjatlar toʻliq qamrab olingan) 125 tadan 72
tasi qamrab olingan hisoblanadi. [COVERAGE.md](../../COVERAGE.md) har bir yurisdiksiya uchun
Fontes nimani qamrab olishi, nimani qamrab olmasligi va nima uchunligini koʻrsatadi.

## API kaliti kerakmi

Deyarli har bir yurisdiksiya uchun yoʻq. Baʼzi manbalar bepul kalit talab qiladi:
[KEYS.md](KEYS.md) ga qarang.

- **Fransiya:** ha. `WLM_FR_PISTE_CLIENT_ID` va `WLM_FR_PISTE_CLIENT_SECRET` ni oʻrnatmaguningizcha
  Fransiya oʻchiq. Ular Judilibre va Légifrance’ga obuna boʻlgan ilovaga ega bepul PISTE hisobidan
  (piste.gouv.fr) olinadi.
- **Amerika Qoʻshma Shtatlari:** ixtiyoriy. Sud amaliyoti qidiruvi kalitsiz ham ishlaydi, lekin
  umumiy namoyish kaliti har bir IP manzil uchun kuniga taxminan 10 ta qidiruvga ruxsat beradi.
  `WLM_US_GOVINFO_KEY` dagi bepul api.data.gov kaliti bu cheklovni oshiradi.
- **AQSh shtatlari sudlari:** ha. Shtatlar sud amaliyoti (`us-states`) `WLM_US_COURTLISTENER_KEY` ni oʻzingizning bepul CourtListener API tokeningizga oʻrnatmaguningizcha oʻchiq. CourtListener’ni notijorat tashkilot Free Law Project yuritadi; u rasmiy manba emas va har bir javob buni bildiradi.

Ularni ilovangizning MCP sozlamalarida Fontes serverining muhit oʻzgaruvchilari sifatida
oʻrnating. Oʻrnatuvchilar oʻrnatishdan keyin ular haqida soʻraydi, ularning
**Add or change keys** ishga tushirgichi esa keyinroq ularni oʻzgartiradi.

Alohida: bir nechta manba oʻz shartlarida avtomatlashtirilgan kirish uchun nashriyotchining
ruxsati kerakligini aytadi. Ular OFF deb belgilangan va oʻchiq qoladi. Kalit buni oʻzgartirmaydi;
buni faqat nashriyotchining ruxsati oʻzgartiradi (unda `WLM_PERMITTED=<codes>` ni oʻrnating).

## Oʻtgan versiyalar va qoʻshimcha mamlakatlar qayerdan keladi?

[Lexifina](https://github.com/lexifina/global-law) taxminan 200 mamlakat qonunchiligini git tarixi
sifatida saqlaydi: har bir oʻzgarish kuchga kirgan kunga qoʻyilgan commit sifatida yoziladi. Fontes
uni Lexifina’ning bepul xostlangan serveri orqali oʻqiydi. Ikkita vosita undan foydalanadi:
`get_law_on_date` (qoidaning sana boʻyicha, oʻtmishdagi sanada ham kuchda boʻlgan matni va uni oxirgi
marta oʻzgartirgan qonun) va `get_law_history` (normani oʻzgartirgan har bir qonun yoki ikki sana
orasidagi soʻzma-soʻz oʻzgarish). Fontes yana 91 ta mamlakat va hududni shu usulda oʻqiydi, faqat
qonunchilik uchun (masalan, Janubiy Afrika, Keniya, Meksika, Yangi Zelandiya, Rossiya, Janubiy Koreya,
Belgiya, Litva, Ukraina, Malayziya, Tailand va Saudiya Arabistoni). Ular jonli rasmiy qamrovga ega
125 ta adapterdan alohida, va mamlakatlar boʻyicha qamrov keskin farq qiladi (Keniyaning milliy
yozuvida 9 ta akt bor). Hindistonning qonunlari ham Lexifina yozuvidan olinadi, chunki India Code
shartlari avtomatlashtirilgan kirishni taqiqlaydi; uning Oliy sud hukmlari esa jonli.

Lexifina rasmiy nashriyotchi emas va uning yozuvi jonli emas: Lexifina har bir mamlakatni vaqti-vaqti
bilan qayta tekshiradi, uning 2026-yil 26-noyabrdagi hisobotida 383 ta milliy qonun organidan 338 tasi
oxirgi 7 kun ichida tekshirilmagan deb sanalgan. Har bir javobda manba sifatida Lexifina nomi
koʻrsatiladi, rasmiy nashriyotchi sahifasiga havola beriladi va yozuv qay darajada toʻliqligi aytiladi.

Lexifina rasmiy huquqiy matnlar mualliflik huquqi bilan himoyalanmagan deb hisoblaydi, shuning uchun
baʼzi mamlakatlarda Fontes oʻzi hurmat qiladigan shartlari yoki robots.txt boʻlgan saytlardan nusxa
koʻchiradi. Fontes oʻzi oladigan hamma narsa uchun ularni hurmat qilishda davom etadi; Lexifina orqali
kelganlar esa Lexifina’ning oʻz huquqiy xulosasiga amal qiladi, u har bir mamlakat uchun uning
omborlarida qayd etilgan. Baʼzilari foydalanishni cheklaydi (Keniya nashriyotchisi: CC BY-NC). Bu
hollarda qidiruv soʻzlaringiz, iqtiboslaringiz va sanalaringiz Lexifina serveriga yuboriladi.
`WLM_LEXIFINA=0` bilan oʻchiring. Bepul server bir internet manzil uchun daqiqada 60 ta va kuniga
10 000 ta chaqiruvga ruxsat beradi; kalit yoki hisob kerak emas. Fontes Lexifina bilan aloqador emas.

## Kompyuterimdan nima chiqadi

Qidiruvlaringiz faqat qidirilayotgan manbaga boradi (Lexifina vositalari va mamlakatlari uchun bu Lexifina serveri). Fontes maʼlumotlar bazasini saqlamaydi va
hisob talab qilmaydi.

Manbalardan tashqari Fontes kuniga bir marta PyPI’dan yangiroq versiya bor-yoʻqligini soʻraydi
(`FONTES_NO_UPDATE_CHECK=1` bilan oʻchiring). Foydalanish hisoblari oʻzingiz yoqmaguningizcha
oʻchiq, xatolik hisoboti esa faqat siz uni koʻrib, tasdiqlaganingizdan keyin yuboriladi. AI
ilovangiz suhbatingizni oʻz shartlari asosida koʻradi.

Toʻliq tafsilotlar: [PRIVACY.md](PRIVACY.md).

## Bu yuridik maslahatmi

Yoʻq. Fontes tadqiqot vositasi. U matnlarni topadi; ular sizning ishingiz uchun nimani
anglatishini aytmaydi va undan foydalanish hech kim bilan advokat va mijoz munosabatini yuzaga
keltirmaydi. AI ilovasi matnni notoʻgʻri oʻqishi mumkin, shuning uchun unga tayanishdan oldin
toʻliq qaror yoki normani oʻqing. Maslahat uchun masalangiz yuzaga kelgan joydagi malakali
yuristga murojaat qiling.

## Uni kim yuritadi va u ishlashda davom etadimi

Bir kishi, Yüce Karapazar. Fontes ortida kompaniya yoʻq, qoʻllab-quvvatlash shartnomasi yoki
xizmat darajasi vaʼdasi yoʻq. Yuridik xizmatlar koʻrsatilmaydi.

Manbalar kuniga bir marta tekshiriladi va natijalar
[holat sahifasida](https://ykarapazar.github.io/fontes/status/?lang=uz) eʼlon qilinadi. Sud va
davlat veb-saytlari ogohlantirishsiz oʻzgaradi, shuning uchun manba istalgan vaqtda ishlamay
qolishi mumkin. Biror manba yoki Fontes’ning oʻzi ishlashda davom etishiga kafolat yoʻq. Fontes
“boricha”, kafolatsiz taqdim etiladi ([LICENSE](../../../LICENSE) ning 7- va 8-boʻlimlari).

## Matn notoʻgʻri yoki eskirgan, yoxud manba ishlamayapti. Qanday xabar beraman

- “Broken or wrong source” shakli bilan issue oching:
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Yurisdiksiyani, nima soʻraganingizni,
  nima olganingizni va toʻgʻri matnni koʻrsatadigan rasmiy sahifani koʻrsating.
- Yoki AI ilovangizdan “Fontes xatoligi haqida xabar berish”ni soʻrang (yoki `fontes report-bug`
  ni ishga tushiring). Biror narsa yuborilishidan oldin hisobotni koʻrasiz.
- Yoki fontesmcp@proton.me manziliga yozing.

Hisobotga mijoz maʼlumotlari yoki maxfiy faktlarni kiritmang.

**Agar siz manbalardan birini boshqarsangiz** va biror narsa notoʻgʻri boʻlsa (shartlaringiz,
robots.txt faylingiz, soʻrovlar cheklovlaringiz), fontesmcp@proton.me manziliga yozing. Manba
tuzatiladi yoki oʻchiriladi.

## Fontes xostingdagi huquqiy tadqiqot vositalaridan nimasi bilan farq qiladi

- **U sizning kompyuteringizda ishlaydi.** Fontes serveri ham, hisobi ham yoʻq. Bu shuningdek u
  faqat lokal MCP serverni ishga tushira oladigan ilovalarda (Claude Desktop, Codex, Cursor,
  VS Code va shu kabilar) ishlashini anglatadi, faqat xostingdagi konnektorlarni qabul qiladigan
  veb-ilovalarda emas.
- **Uning maʼlumotlar bazasi yoʻq.** Har bir qidiruv toʻgʻridan-toʻgʻri nashriyotchining oʻz
  veb-sayti yoki API’siga boradi, shuning uchun natijalar manbaning oʻzi kabi yangi, qidiruv
  sifati esa manbaning oʻz sifati. Saralangan (curated) indeks boʻyicha semantik qidiruv yoʻq.
- **U foydalanish cheklovini qoʻymaydi.** Fontes’da oylik chaqiruvlar cheklovi yoʻq. U har bir
  saytga soʻrovlarini vaqt boʻyicha taqsimlaydi va baʼzi manbalar ularga qanchalik tez yoki
  qanchalik tez-tez murojaat qilish mumkinligini cheklaydi.
- **U ochiq kodli.** Har bir adapterni oʻqib, har bir matn qayerdan kelishini aniq koʻrishingiz
  mumkin.
- **Uning ortida yetkazib beruvchi yoʻq.** Shartnoma ham, qoʻllab-quvvatlash xizmati ham, ishlash
  vaʼdasi ham yoʻq (“Uni kim yuritadi” ga qarang).

## Qaysi ilovalar va tizimlar bilan ishlaydi

Lokal (stdio) serverni ishga tushira oladigan har qanday MCP ilovasi bilan, masalan Claude
Desktop, Claude Code, Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed,
LM Studio va Cline. Fontes macOS, Windows va Linux’da, uv ishlaydigan har qanday joyda ishlaydi
(Python 3.13+). Mac’da yoki Windows PC’da bir bosishda ishlaydigan oʻrnatuvchi
Claude Desktop, Codex, Claude Code, Cursor, VS Code, Windsurf, Gemini CLI, Zed, LM Studio va
Cline’ni birdaniga sozlaydi. Har bir ilova uchun qadamlar: [INSTALL.md](INSTALL.md).

## Kod kiritishim mumkinmi

Hozircha yoʻq. Issue’lar, manbalar haqidagi xabarlar va yurisdiksiya soʻrovlari mamnuniyat bilan
qabul qilinadi. [CONTRIBUTING.md](../../../CONTRIBUTING.md) ga qarang.
