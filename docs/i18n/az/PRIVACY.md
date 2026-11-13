> Bu, maşın dəstəyi ilə hazırlanmış tərcümədir. Əsas olan ingiliscə versiyadır.

# Fontes məxfilik bildirişi

Fontes sizin kompüterinizdə işləyir. Axtarışlarınız və açdığınız sənədlər kompüteriniz, axtarış
apardığınız rəsmi mənbələr və istifadə etdiyiniz süni intellekt proqramı (həmin proqramın öz
şərtləri çərçivəsində) arasında qalır. Fontes-in özü Fontes tərtibatçılarına **defolt olaraq heç
nə göndərmir**.

## Kompüterinizdən nə və nə vaxt çıxa bilər

**1. Yeniləmə yoxlaması (defolt olaraq yanılı).** Fontes gündə bir dəfə ictimai Python paket
indeksi olan PyPI-dan ən yeni versiyanın hansı olduğunu soruşur. Sorğu siz və ya işiniz barədə heç
nə daşımır; istənilən yükləmədə olduğu kimi PyPI IP ünvanınızı görür. Onu söndürmək üçün
`FONTES_NO_UPDATE_CHECK=1` (proqramdaxili bildiriş) və `FONTES_NO_AUTO_UPDATE=1` (quraşdırıcının
avtomatik yeniləmələri) təyin edin.

**2. İstifadə sayları (siz yandırmadıqca söndürülüb).** Razılıq versəniz (opt in), Fontes gündə bir
dəfə bunları göndərir:

- Fontes versiyası və əməliyyat sisteminizin ailəsi (macOS, Windows, Linux);
- gün üzrə, hər alətin hər yurisdiksiya kodu üçün neçə dəfə istifadə edildiyi, məsələn
  "2026-11-10, nl, search_caselaw, 12".

Mesajın hamısı budur. O, heç vaxt axtarışlarınızı, sənəd və ya iş identifikatorlarını (id), sənəd
mətnini, adınızı, hesabı və ya sizin, yaxud kompüteriniz üçün hər hansı identifikatoru ehtiva
etmir. Saylar göndərilənə qədər kompüterinizdə gözləyir (Fontes-in keş qovluğunda, `stats.json`);
göndərmə uğursuz olarsa, növbəti günü gözləyirlər.

- **Razılıq vermək (opt in)**: quraşdırıcı soruşduqda "h" cavabını verin və ya Fontes serveri üçün
  `FONTES_STATS=1` təyin edin.
- **İmtina etmək (opt out)**: quraşdırıcını yenidən işə salın və həmin sualda Enter basın və ya
  `FONTES_STATS`-ı silin. `stats.json` faylını silmək hələ göndərilməmiş hər şeyi ləğv edir.

**3. Xəta hesabatları (yalnız siz göndərdikdə).** Siz hesabat istədikdə (`fontes report-bug` və ya
süni intellekt proqramınızdan Fontes xətasını bildirməyi xahiş etdikdə), Fontes əvvəlcə sizə tam
hesabatı göstərir və onu yalnız siz təsdiq etdikdə göndərir. Hesabat Fontes versiyasını,
əməliyyat sisteminizin ailəsini, son uğursuz alət çağırışının yurisdiksiya kodunu, alətin adını və
xəta mesajını (axtarış sözləriniz və identifikatorlar çıxarılmaqla), həmçinin qeyd yazsanız, həmin
qeydi ehtiva edir. Qeydə müştəri məlumatlarını yazmayın. Bunu dəstəkləmək üçün Fontes son xətanı
kompüterinizdə saxlayır (keş qovluğunda `last-error.json`, hər dəfə əvəz olunur); o, heç vaxt
ayrılıqda göndərilmir.

## Hara gedir və nə qədər saxlanılır

İstifadə sayları və xəta hesabatları Fontes tərtibatçısının idarə etdiyi kiçik serverə gedir
(`relay.kinetra.fit`). O, heç bir IP ünvanı saxlamır: IP ünvanları yalnız yaddaşda, qısa müddətə,
sorğu axınlarını dayandırmaq üçün istifadə olunur və veb server onun üçün heç bir giriş jurnalı
(access log) saxlamır. Saylar gündəlik cəmlərə əlavə olunur; ayrı-ayrı göndərişlər saxlanılmır.
Cəmlər 2 ilə qədər, xəta hesabatları 1 ilə qədər saxlanılır, sonra silinir. Heç nə satılmır və ya
paylaşılmır.

Həmin serverə çatmaq mümkün olmasa, heç nə göndərilmir: saylar kompüterinizdə qalır, xəta
hesabatları isə sizi bunun əvəzinə issue tracker-ə yönləndirir.

## Kim məsuldur və hansı əsasla

İstifadə sayları və xəta hesabatları üçün məlumat nəzarətçisi (data controller) Fontes-in
tərtibatçısı Yüce Karapazar-dır. Əlaqə: fontesmcp@proton.me.

Hüquqi əsas sizin razılığınızdır (UK GDPR və EU GDPR-ın 6(1)(a) maddəsi). İstifadə sayları yalnız
siz razılıq versəniz, xəta hesabatı isə yalnız siz onu təsdiq etdikdən sonra göndərilir. Yuxarıda
təsvir edildiyi kimi imtina etməklə razılığınızı istənilən vaxt geri götürə bilərsiniz; bu, əvvəl
göndərilənlərə təsir etmir.

## Əlaqə

Suallar və ya müraciətlər: fontesmcp@proton.me ünvanına e-poçt göndərin və ya
<https://github.com/ykarapazar/fontes/issues> ünvanında issue açın.
