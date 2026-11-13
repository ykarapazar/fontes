> Bu çeviri makine desteğiyle hazırlanmıştır. Esas olan İngilizce sürümdür.

# Fontes: sorular ve yanıtlar

## Fontes nedir?

Ücretsiz, açık kaynaklı bir MCP sunucusudur (Apache 2.0). Model Context Protocol'ü konuşan her
uygulamanın (Claude, Codex, Cursor, VS Code, Gemini CLI ve diğerleri) 120'den fazla yargı alanında ve
uluslararası mahkemede (124 adaptör) mahkeme kararlarını ve mevzuatı mahkeme ve devlet internet
sitelerinde canlı olarak aramasını sağlar. Her sonuç kaynağını belirtir ve asıl metne bağlantı verir.

## Metinler resmî mi?

Çoğunlukla evet, ama her zaman değil.

- Kaynakların çoğu bir mahkeme, bir bakanlık veya bir resmî gazete tarafından işletilir.
- Bazı konsolide metinler bir devlet tarafından yayımlanır, ancak açıkça resmî değildir: yalnızca
  resmî gazete asıl metindir.
- Birkaç kaynak hiç devlet sitesi değildir (örneğin LexiVox, LawPhil, Maqam, Wikisource).

Fontes, bunlardan birinden gelen her yanıta "Resmî olmayan kaynak" uyarısı ekler. Herhangi bir şeye
atıf yapmadan önce resmî yayını kontrol edin. [README](README.md#kapsam) içindeki kapsam tablosu ve
`list_jurisdictions` her yargı alanının kaynağını belirtir.

## Hangi yargı alanlarını kapsıyor ve ne ölçüde?

124 adaptör: 108 BM üyesi devlet, Hong Kong, Kosova, Filistin, Tayvan, DIFC Mahkemeleri ve
11 uluslararası mahkeme ve kuruluş (Avrupa İnsan Hakları Mahkemesi, AB, UAD ve DTÖ gibi).

Kapsam çok farklıdır. Katı bir kurala göre (en yüksek genel mahkemenin emsal kararlarına ya da
anayasa ve temel kanunlara eksiksiz ulaşılması), 124'ün 72'si kapsanmış sayılır.
[COVERAGE.md](../../COVERAGE.md) (İngilizce), her yargı alanı için Fontes'in neye ulaştığını, neye
ulaşmadığını ve nedenini listeler.

## API anahtarına ihtiyacım var mı?

Neredeyse her yargı alanı için hayır. Bazı kaynaklar ücretsiz bir anahtar gerektirir: bkz.
[KEYS.md](KEYS.md).

- **Fransa:** evet. `WLM_FR_PISTE_CLIENT_ID` ve `WLM_FR_PISTE_CLIENT_SECRET` ayarlanana kadar Fransa
  kapalıdır. Bunlar, Judilibre ve Légifrance'a abone edilmiş bir uygulamaya sahip ücretsiz bir PISTE
  hesabından (piste.gouv.fr) alınır.
- **Amerika Birleşik Devletleri:** isteğe bağlı. İçtihat araması anahtar olmadan çalışır, ancak
  ortak demo anahtarı IP adresi başına günde yalnızca yaklaşık 10 aramaya izin verir.
  `WLM_US_GOVINFO_KEY` içine konan ücretsiz bir api.data.gov anahtarı bu sınırı yükseltir.

Bunları uygulamanızın MCP ayarlarında Fontes sunucusu için ortam değişkenleri olarak ayarlayın.
Kurulum programı yayımlandığında, kurulumdan sonra bunları soracak ve **Anahtar ekle veya değiştir**
başlatıcısı daha sonra bunları değiştirecek.

Bundan ayrı olarak, birkaç kaynak kullanım koşullarında otomatik erişimin yayıncının iznini
gerektirdiğini belirtir. Bunlar OFF olarak işaretlidir ve kapalı kalır. Bir anahtar bunu
değiştirmez; yalnızca yayıncının izni değiştirir (o durumda `WLM_PERMITTED=<codes>` ayarlayın).

## Bilgisayarımdan ne çıkıyor?

Aramalarınız yalnızca aranan kaynağa gider. Fontes veritabanı tutmaz ve hesap gerektirmez.

Kaynakların dışında Fontes, günde bir kez PyPI'a daha yeni bir sürüm olup olmadığını sorar
(`FONTES_NO_UPDATE_CHECK=1` ile kapatın). Kullanım sayıları siz açmadıkça kapalıdır ve bir hata
bildirimi yalnızca siz onu görüp onayladıktan sonra gönderilir. Yapay zekâ uygulamanız, sohbetinizi
kendi koşulları çerçevesinde görür.

Tüm ayrıntılar: [PRIVACY.md](PRIVACY.md).

## Bu hukuki danışmanlık mı?

Hayır. Fontes bir araştırma aracıdır. Metinleri bulur; bunların sizin davanız için ne anlama
geldiğini söylemez ve kullanılması kimseyle avukat–müvekkil ilişkisi kurmaz. Yapay zekâ uygulaması
bir metni yanlış okuyabilir; bu yüzden bir karara veya hükme güvenmeden önce tamamını okuyun.
Danışmanlık için sorunuzun ortaya çıktığı yerde yetkili bir avukata başvurun.

## Kim sürdürüyor? Çalışmaya devam edecek mi?

Tek bir kişi: Yüce Karapazar. Fontes'in arkasında bir şirket, destek sözleşmesi veya hizmet düzeyi
taahhüdü yoktur. Hiçbir hukuki hizmet sunulmaz.

Kaynaklar günde bir kez kontrol edilir ve sonuçlar
[durum sayfasında](https://ykarapazar.github.io/fontes/status/?lang=tr) yayımlanır. Mahkeme ve devlet
internet siteleri haber vermeden değişir, bu yüzden bir kaynak her an bozulabilir. Herhangi bir
kaynağın ya da Fontes'in kendisinin çalışmaya devam edeceğinin garantisi yoktur. Fontes "olduğu gibi",
garanti olmaksızın sunulur ([LICENSE](../../../LICENSE) dosyasının 7. ve 8. bölümleri).

## Bir metin yanlış, güncel değil ya da bir kaynak bozuk. Nasıl bildiririm?

- "Broken or wrong source" formuyla bir issue açın:
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Hangi yargı alanı olduğunu, ne
  sorduğunuzu, ne aldığınızı ve doğru metni gösteren resmî sayfayı belirtin.
- Ya da yapay zekâ uygulamanızdan "bir Fontes hatası bildirmesini" isteyin (veya `fontes report-bug`
  komutunu çalıştırın). Herhangi bir şey gönderilmeden önce bildirimi görürsünüz.
- Ya da fontesmcp@proton.me adresine e-posta gönderin.

Bir bildirime müvekkil bilgilerini veya gizli olguları yazmayın.

**Kaynaklardan birini işletiyorsanız** ve bir şey yanlışsa (kullanım koşullarınız, robots.txt'niz,
istek sınırlarınız), fontesmcp@proton.me adresine e-posta gönderin. Kaynak düzeltilecek veya
kapatılacaktır.

## Fontes, barındırılan (hosted) hukuki araştırma araçlarından nasıl farklı?

- **Bilgisayarınızda çalışır.** Fontes sunucusu ve hesap yoktur. Bu aynı zamanda yalnızca yerel bir
  MCP sunucusu başlatabilen uygulamalarda (Claude Desktop, Codex, Cursor, VS Code ve benzerleri)
  çalıştığı, yalnızca barındırılan bağlayıcıları (connector) kabul eden salt web uygulamalarında
  çalışmadığı anlamına gelir.
- **Veritabanı yoktur.** Her arama canlı olarak yayıncının kendi internet sitesine veya API'sine
  gider; bu yüzden sonuçlar kaynak kadar günceldir ve arama kalitesi kaynağın kendisininkidir.
  Seçilmiş bir dizin üzerinde anlamsal (semantik) arama yoktur.
- **Kullanım sınırı koymaz.** Fontes'in aylık çağrı sınırı yoktur. Her internet sitesine yaptığı
  istekleri aralıklandırır ve bazı kaynaklar ne kadar hızlı veya ne sıklıkta sorgulanabileceklerini
  sınırlar.
- **Açık kaynaklıdır.** Her adaptörü okuyabilir ve her metnin tam olarak nereden geldiğini
  görebilirsiniz.
- **Arkasında bir satıcı yoktur.** Sözleşme, destek masası veya kesintisiz çalışma taahhüdü yoktur
  (bkz. "Kim sürdürüyor?").

## Hangi uygulama ve sistemlerle çalışır?

Yerel (stdio) bir sunucu çalıştırabilen her MCP uygulamasıyla, örneğin Claude Desktop, Claude Code,
Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio ve Cline. Fontes macOS,
Windows ve Linux'ta, uv'nin çalıştığı her yerde (Python 3.13+) çalışır. Mac ve Windows için tek tıkla kurulum programı
yolda. Claude Desktop, Codex, Claude Code, Cursor, VS Code, Windsurf, Gemini CLI, Zed, LM Studio ve
Cline'ı tek seferde kurar. Her uygulama için adımlar: [INSTALL.md](INSTALL.md).

## Kod katkısında bulunabilir miyim?

Şu anda hayır. Issue'lar, kaynak bildirimleri ve yargı alanı talepleri memnuniyetle karşılanır. Bkz.
[CONTRIBUTING.md](../../../CONTRIBUTING.md).
