> Bu mashina yordamida qilingan tarjima. Ingliz tilidagi matn asosiy hisoblanadi.

# Fontes maxfiylik bildirishnomasi

Fontes sizning kompyuteringizda ishlaydi. Qidiruvlaringiz va siz ochgan hujjatlar kompyuteringiz,
siz qidirgan manbalar (rasmiy manbalar, shuningdek ulardan foydalansangiz CourtListener va Lexifina, quyida qarang) va siz foydalanadigan AI ilovasi oʻrtasida qoladi (shu ilovaning oʻz
shartlari asosida). Fontes’ning oʻzi sukut boʻyicha Fontes ishlab chiquvchilariga **hech narsa
yubormaydi**.

## Kompyuteringizdan nima va qachon chiqishi mumkin

**1. Yangilanishni tekshirish (sukut boʻyicha yoqilgan).** Kuniga bir marta Fontes Python
paketlarining ochiq indeksi boʻlgan PyPI’dan eng yangi versiya qaysi ekanini soʻraydi. Soʻrovda
siz yoki ishingiz haqida hech narsa yoʻq; PyPI har qanday yuklab olishdagi kabi IP manzilingizni
koʻradi. Uni oʻchirish uchun `FONTES_NO_UPDATE_CHECK=1` (ilova ichidagi xabar) va
`FONTES_NO_AUTO_UPDATE=1` (oʻrnatuvchining avtomatik yangilanishlari) ni oʻrnating.

**2. Foydalanish hisoblari (oʻzingiz yoqmaguningizcha oʻchiq).** Agar rozilik bersangiz (opt-in),
Fontes kuniga bir marta quyidagilarni yuboradi:

- Fontes versiyasi va operatsion tizimingiz oilasi (macOS, Windows, Linux);
- har bir kun uchun: har bir vosita har bir yurisdiksiya kodi uchun necha marta ishlatilgani,
  masalan “2026-11-10, nl, search_caselaw, 12”.

Butun xabar shu. U hech qachon qidiruvlaringizni, hujjat yoki ish identifikatorlarini, hujjat
matnini, ismingizni, hisobni yoki sizni yoki kompyuteringizni aniqlaydigan biror identifikatorni
oʻz ichiga olmaydi. Hisoblar yuborilguncha kompyuteringizda kutadi (Fontes kesh jildida,
`stats.json`); agar yuborish muvaffaqiyatsiz boʻlsa, ular ertasi kungacha kutadi.

- **Yoqish uchun:** oʻrnatuvchi soʻraganda “ha” deb javob bering yoki Fontes serveri uchun
  `FONTES_STATS=1` ni oʻrnating.
- **Oʻchirish uchun:** oʻrnatuvchini qayta ishga tushiring va shu savolda Enter tugmasini bosing
  yoki `FONTES_STATS` ni olib tashlang. `stats.json` ni oʻchirish hali yuborilmagan hamma narsani
  bekor qiladi.

**3. Xatolik hisobotlari (faqat siz yuborganingizda).** Siz soʻraganingizda (`fontes report-bug`
yoki AI ilovangizdan Fontes xatoligi haqida xabar berishni soʻrasangiz), Fontes avval toʻliq
hisobotni koʻrsatadi va uni faqat siz tasdiqlasangiz yuboradi. Unda Fontes versiyasi, operatsion
tizimingiz oilasi, oxirgi muvaffaqiyatsiz vosita chaqiruvining yurisdiksiya kodi, vosita nomi va
xato xabari (qidiruv soʻzlaringiz va identifikatorlar olib tashlangan) hamda, agar yozsangiz,
izoh boʻladi. Izohga mijoz maʼlumotlarini kiritmang. Buning uchun Fontes oxirgi xatoni
kompyuteringizda saqlaydi (`last-error.json` oʻz kesh jildida, har safar almashtiriladi); u
hech qachon oʻz-oʻzidan yuborilmaydi.

**4. Lexifina (sukut boʻyicha yoqilgan).** `get_law_on_date`, `get_law_history`, 91 ta mamlakat va Hindiston Acts’lari Lexifina yozuvi orqali oʻqiladi, shuning uchun ular rasmiy sayt bilan birga yoki uning oʻrniga Lexifina’ga ham boradi. Qidiruv soʻzlaringiz, iqtiboslaringiz va sanalaringiz Lexifina’ning bepul serveriga, `global-law.lexifina.com` ga boradi; u Fontes ishlab chiquvchilari emas, Lexifina tomonidan boshqariladi. Lexifina oʻz serveri faqat qaysi vosita chaqirilgani va u qancha vaqt olgani haqida jurnal yuritishini, hech qachon nima soʻralgani haqida emasligini hujjatlashtirgan; Fontes buni tekshira olmaydi va Lexifina’ning oʻz shartlari qoʻllanadi. Lexifina har qanday veb-server kabi sizning IP manzilingizni koʻradi. Lexifina’ni butunlay oʻchirish uchun `WLM_LEXIFINA=0` ni oʻrnating; u holda bu ikki vosita va mamlakatlar ishlamaydi va u yerga hech narsa yuborilmaydi.

## Maʼlumotlar qayerga boradi va qancha saqlanadi

Foydalanish hisoblari va xatolik hisobotlari Fontes ishlab chiquvchisi boshqaradigan kichik
serverga (`relay.kinetra.fit`) boradi. U IP manzillarni saqlamaydi: ular faqat xotirada, qisqa
vaqt davomida, soʻrovlar oqimining oldini olish uchun ishlatiladi va veb-server buning uchun
kirish jurnalini yuritmaydi. Hisoblar kunlik jami raqamlarga qoʻshiladi; alohida yuborishlar
saqlanmaydi. Jami raqamlar 2 yilgacha, xatolik hisobotlari 1 yilgacha saqlanadi, soʻng
oʻchiriladi. Hech narsa sotilmaydi yoki boshqalarga berilmaydi.

Agar bu server mavjud boʻlmasa, hech narsa yuborilmaydi: hisoblar kompyuteringizda qoladi,
xatolik hisobotlari esa sizni buning oʻrniga muammolar trekeriga (issue tracker) yoʻnaltiradi.

## Kim javobgar va qanday asosda

Foydalanish hisoblari va xatolik hisobotlari boʻyicha maʼlumotlar nazoratchisi (controller)
Fontes ishlab chiquvchisi Yüce Karapazar. Aloqa: fontesmcp@proton.me.

Huquqiy asos sizning roziligingiz (UK GDPR va EU GDPR 6-moddasi 1-qismining “a” bandi).
Foydalanish hisoblari faqat roziligingiz bilan, xatolik hisoboti esa faqat siz uni
tasdiqlaganingizdan keyin yuboriladi. Roziligingizni istalgan vaqtda yuqorida tasvirlanganidek
oʻchirib qaytarib olishingiz mumkin; bu avval yuborilgan narsaga taʼsir qilmaydi.

## Aloqa

Savollar yoki soʻrovlar: fontesmcp@proton.me manziliga yozing yoki
<https://github.com/ykarapazar/fontes/issues> manzilida issue oching.
