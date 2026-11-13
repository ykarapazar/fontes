> Bu çeviri makine desteğiyle hazırlanmıştır. Esas olan İngilizce sürümdür.

# Fontes gizlilik bildirimi

Fontes bilgisayarınızda çalışır. Aramalarınız ve açtığınız belgeler bilgisayarınız, aradığınız
resmî kaynaklar ve kullandığınız yapay zekâ uygulaması (o uygulamanın kendi koşulları çerçevesinde)
arasında kalır. Fontes'in kendisi Fontes geliştiricilerine **varsayılan olarak hiçbir şey
göndermez**.

## Bilgisayarınızdan ne çıkabilir ve ne zaman

**1. Güncelleme kontrolü (varsayılan olarak açık).** Fontes günde bir kez, kamuya açık Python paket
dizini olan PyPI'a en yeni sürümün hangisi olduğunu sorar. İstek sizinle veya çalışmanızla ilgili
hiçbir şey taşımaz; her indirmede olduğu gibi PyPI IP adresinizi görür. Kapatmak için
`FONTES_NO_UPDATE_CHECK=1` (uygulama içi bildirim) ve `FONTES_NO_AUTO_UPDATE=1` (kurulum programının
otomatik güncellemeleri) ayarlayın.

**2. Kullanım sayıları (siz açmadıkça kapalı).** Katılmayı seçerseniz (opt-in), Fontes günde bir kez
şunları gönderir:

- Fontes sürümü ve işletim sistemi aileniz (macOS, Windows, Linux);
- gün başına, her aracın her yargı alanı kodu için kaç kez kullanıldığı, örneğin
  "2026-11-10, nl, search_caselaw, 12".

Mesajın tamamı budur. Aramalarınızı, belge veya dava kimliklerini (id), belge metnini, adınızı, bir
hesabı ya da sizin veya bilgisayarınız için herhangi bir kimliği asla içermez. Sayılar gönderilene
kadar bilgisayarınızda bekler (Fontes'in önbellek klasöründe, `stats.json`); gönderim başarısız
olursa bir sonraki günü beklerler.

- **Katılmak (opt in)**: kurulum programı sorduğunda "e" yanıtını verin ya da Fontes sunucusu için
  `FONTES_STATS=1` ayarlayın.
- **Çıkmak (opt out)**: kurulum programını yeniden çalıştırıp o soruda Enter'a basın ya da
  `FONTES_STATS`'ı kaldırın. `stats.json` dosyasını silmek henüz gönderilmemiş her şeyi atar.

**3. Hata bildirimleri (yalnızca siz gönderdiğinizde).** Bir bildirim istediğinizde
(`fontes report-bug` veya yapay zekâ uygulamanızdan bir Fontes hatasını bildirmesini istediğinizde),
Fontes size önce bildirimin tamamını gösterir ve yalnızca siz onaylarsanız gönderir. Bildirim Fontes
sürümünü, işletim sistemi ailenizi, son başarısız araç çağrısının yargı alanı kodunu, araç adını ve
hata mesajını (arama sözcükleriniz ve kimlikler çıkarılmış olarak) ve bir not yazarsanız o notu
içerir. Nota müvekkil bilgilerini yazmayın. Bunu desteklemek için Fontes son hatayı bilgisayarınızda
tutar (önbellek klasöründe `last-error.json`, her seferinde değiştirilir); bu dosya asla tek başına
gönderilmez.

## Nereye gider ve ne kadar süre saklanır

Kullanım sayıları ve hata bildirimleri, Fontes geliştiricisinin işlettiği küçük bir sunucuya gider
(`relay.kinetra.fit`). Bu sunucu hiçbir IP adresi saklamaz: IP adresleri yalnızca bellekte, kısa
süreliğine, istek yağmurlarını durdurmak için kullanılır ve web sunucusu bunun için hiçbir erişim
kaydı tutmaz. Sayılar günlük toplamlara eklenir; tek tek gönderimler saklanmaz. Toplamlar en fazla
2 yıl, hata bildirimleri en fazla 1 yıl saklanır, ardından silinir. Hiçbir şey satılmaz veya
paylaşılmaz.

O sunucuya ulaşılamazsa hiçbir şey gönderilmez: sayılar bilgisayarınızda kalır ve hata bildirimleri
sizi bunun yerine sorun takip sistemine (issue tracker) yönlendirir.

## Kim sorumludur ve hangi hukuki sebebe dayanarak

Kullanım sayıları ve hata bildirimleri için veri sorumlusu, Fontes'in geliştiricisi Yüce
Karapazar'dır. İletişim: fontesmcp@proton.me.

Hukuki sebep açık rızanızdır (UK GDPR ve EU GDPR madde 6(1)(a)). Kullanım sayıları yalnızca
katılmayı seçerseniz, bir hata bildirimi ise yalnızca siz onayladıktan sonra gönderilir. Yukarıda
açıklandığı şekilde çıkarak rızanızı istediğiniz zaman geri çekebilirsiniz; bu, daha önce
gönderilmiş olanı etkilemez.

## İletişim

Sorular veya talepler: fontesmcp@proton.me adresine e-posta gönderin ya da
<https://github.com/ykarapazar/fontes/issues> adresinde bir issue açın.
