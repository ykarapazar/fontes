> Bu çeviri makine desteğiyle hazırlanmıştır. Esas olan İngilizce sürümdür.

# API anahtarları

Fontes'teki neredeyse her kaynak anahtarsız çalışır. Üçü ücretsiz bir anahtar gerektirir:

| Anahtar | Neyi açar | Anahtar olmadan |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Fransa: Judilibre (mahkeme kararları) ve Légifrance (mevzuat) | Fransa kapalıdır. `list_jurisdictions` onu etkin değil olarak gösterir. |
| `WLM_US_GOVINFO_KEY` | Amerika Birleşik Devletleri: govinfo araması (federal mahkeme kararları, Statutes at Large, public laws) | Fontes ortak `DEMO_KEY`'i kullanır: IP adresi başına günde yaklaşık 10 arama. Bilinen bir kararı açmak ve US Code anahtar gerektirmez. |
| `WLM_US_COURTLISTENER_KEY` | ABD eyalet mahkemeleri (`us-states`): CourtListener'dan, 50 eyaletin ve DC'nin yüksek ve istinaf mahkemelerinin kararları | ABD eyalet içtihadı kapalıdır. `list_jurisdictions` onu etkin değil olarak gösterir. |

Anahtarlar isteğe bağlıdır. Bunları daha sonra ekleyebilirsiniz.

## Anahtar eklemek

**Kurulum programıyla.** Fontes kurulduktan sonra kurulum programı anahtar eklemeyi önerir. Mac'te
**Anahtar ekle**'ye ya da atlamak için **Bitti**'ye tıklayın; Windows'ta soruyu yanıtlayın (atlamak için
Enter'a basın). Anahtarları daha sonra eklemek veya değiştirmek için **Anahtar ekle veya değiştir**'i
çalıştırın:

- Mac: Fontes Installer uygulamasını yeniden açıp **Anahtar ekle veya değiştir**'i seçin.
- Windows: Başlat menüsünü açın, ardından **Fontes** → **Anahtar ekle veya değiştir**.

Yazdıklarınız gizlenir. Her anahtar için: yapıştırın, mevcut olanı korumak için Enter'a basın ya da
kaldırmak için `-` yazın. Anahtarlar, Fontes'in zaten kurulu olduğu her uygulamaya eklenir.

**Claude Desktop eklentisiyle (.mcpb).** Claude > Settings > Extensions > Fontes'i açın ve alanları
doldurun. Hepsi isteğe bağlıdır.

**Elle.** Değişkenleri, uygulamanızın MCP yapılandırmasındaki `fontes` girdisinin `env` bloğuna
ekleyin:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Her değişiklikten sonra uygulamayı yeniden başlatın.

## Fransa: PISTE (ücretsiz)

1. [piste.gouv.fr](https://piste.gouv.fr) adresinde bir hesap oluşturun. Bu, PISTE kullanım
   koşullarını (CGU) kabul etmek anlamına gelir.
2. API > **Consentement CGU API** bölümüne gidin. **JUDILIBRE** ve **Légifrance** (production) için
   koşulları kabul edin.
3. Bir **production application** oluşturun. Sizin için oluşturulan `APP_SANDBOX` production'a
   erişemez. "Modifier l'application" altında **JUDILIBRE (production)** ve **Légifrance
   (production)** kutularını işaretleyin, ardından uygulayın.
4. Uygulamanın **Authentification** sekmesini açın. `client_id` ve `client_secret` değerlerini
   kopyalayın.
5. **Anahtar ekle veya değiştir**'i çalıştırın ve bunları yapıştırın.

Kısaca koşullar:

- Veriler: Licence Ouverte / Etalab 2.0. Ticari yeniden kullanım dahil yeniden kullanıma, kaynak
  gösterilmesi şartıyla izin verilir.
- Kimlik bilgilerinizi yayımlamayın veya paylaşmayın. Sızarlarsa PISTE'ye bildirin.
- Légifrance API'si beta bir hizmettir. Askıya alınabilir ve kotaları vardır (saniye, dakika ve gün
  başına).
- Légifrance metinleri asıl (authentic) sürüm değildir. Yalnızca imzalı Journal officiel PDF'i
  asıldır.
- Judilibre: hâkimlerin veya zabıt kâtiplerinin adlarını, onların çalışmalarını değerlendirmek,
  karşılaştırmak veya öngörmek için kullanmayın (Code de l'organisation judiciaire md. L111-13;
  bir suçtur).
- Judilibre: GDPR'a uyun. Tarafların kimliğini yeniden belirlemeye çalışmayın.

Kotalarınız PISTE'de API Sélectionnées > Actions > Consulter les quotas altındadır.

## Amerika Birleşik Devletleri: api.data.gov (ücretsiz)

1. [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (anahtar ekranda gösterilir) veya
   [api.data.gov/signup](https://api.data.gov/signup/) (anahtar size e-postayla gönderilir)
   adresine gidin.
2. Adınızı ve e-posta adresinizi girin. "Nasıl kullanacaksınız" alanı isteğe bağlıdır.
3. 40 karakterlik anahtarı kopyalayın.
4. **Anahtar ekle veya değiştir**'i çalıştırın ve onu ABD anahtarı olarak yapıştırın.

Kısaca koşullar:

- Kendi anahtarınızla govinfo saatte en fazla 36.000 isteğe izin verir.
- API'ye özgü bir kullanım koşulları metni bulamadık (api.data.gov/terms/ mevcut değil).
  Doğrulanmadı. Bkz. [govinfo'nun politikaları](https://www.govinfo.gov/about/policies) ve
  [data.gov gizlilik politikası](https://data.gov/privacy-policy/).
- Anahtarı kendinize saklayın.

## ABD eyalet mahkemeleri: CourtListener (ücretsiz)

CourtListener, 2010'dan beri ABD mahkeme kararlarını toplayan ve bunları herkese ücretsiz sunan kâr amacı gütmeyen bir kuruluş olan [Free Law Project](https://free.law) tarafından işletilir. Kendi sayımına göre dokuz milyonun üzerinde karar içerir. Resmî bir kaynak değildir: mahkemeler kendi kararlarını kendileri yayımlar, CourtListener ise bunları mahkeme internet sitelerinden ve taranmış karar derlemelerinden toplar. Fontes'in bu kaynaktan verdiği her yanıt bunu belirtir. Fontes, Free Law Project ile bağlantılı değildir.

1. [courtlistener.com](https://www.courtlistener.com/sign-in/) adresinde ücretsiz bir hesap oluşturun.
2. Profilinizi açın ve API token'ınızı kopyalayın.
3. **Anahtar ekle veya değiştir**'i çalıştırın ve onu CourtListener anahtarı olarak yapıştırın.

Kısaca koşullar ([tam koşullar](https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies)):

- Token yalnızca size aittir: paylaşmayın, başkalarınınkiyle birleştirmeyin, yeniden satmayın ve birden fazla hesap kullanmayın.
- Bir yapay zekâ uygulamasının token'ınızla yaptıklarından siz sorumlusunuz.
- Bir yapay zekânın onların verileri üzerinde yaptığı analizi, Free Law Project tarafından üretilmiş, onaylanmış veya denetlenmiş gibi sunmayın.
- Ücretsiz bir hesap dakikada 5, saatte 50 ve günde 125 isteğe izin verir. Bir arama bir istektir; bir kararı açmak iki istektir. Free Law Project üyeliği sınırları yükseltir.
- CourtListener doğruluğu garanti etmez. Bir karara güvenmeden önce onu mahkemenin kendi kopyasıyla karşılaştırın.

## Anahtarlar nerede saklanır

- **Kurulum programı veya elle:** her uygulamanın MCP yapılandırma dosyasında, `fontes` girdisinin
  `env` bloğunda düz metin olarak. Kullanıcı dosyalarınızı okuyabilen herkes anahtarları okuyabilir.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` veya `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Claude Desktop eklentisi (.mcpb):** Claude bu alanları kendi ayarlarında tutar ve sisteminizin
  güvenli depolamasıyla korur (Mac'te Keychain, Windows'ta Credential Manager).

Kurulum programı her değişiklikten önce yapılandırma dosyasının bir kopyasını yanına kaydeder
(`<file>.fontes-backup-<time>`). Anahtarları ekledikten sonra alınan kopyalar da anahtarları içerir.
İhtiyacınız olmayan eski kopyaları silin.

## Bir anahtarı değiştirmek veya kaldırmak

- **Anahtar ekle veya değiştir**'i çalıştırın. Değiştirmek için yeni bir anahtar yapıştırın ya da
  kaldırmak için `-` yazın.
- Ya da `env` bloğunu elle düzenleyin ve uygulamayı yeniden başlatın.
- Fontes'i kaldırmak, anahtarlar dahil tüm girdisini kaldırır. Yedek kopyaları silmez.
- Bir anahtar sızdıysa, onu kaynağında da değiştirin: PISTE'de uygulamanız için yeni kimlik
  bilgileri oluşturun; api.data.gov için yeni bir anahtar alın.

## Görebileceğiniz mesajlar

| Mesaj | Anlamı |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Fransa anahtarı yok. Bir tane ekleyin. |
| `Inactive: needs a free PISTE account. ...` (`list_jurisdictions` içinde) | Aynısı. |
| `PISTE refused the client credentials ...` | ID veya secret yanlış ya da artık geçerli değil. İkisini de Authentification sekmesinden yeniden kopyalayın. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Uygulamanız o API'ye abone değil ya da onun koşullarını kabul etmediniz. Bkz. 2. ve 3. adımlar. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | ABD anahtarı yok. Arama günde birkaç çağrı için çalışır. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Demo anahtarının hakkı doldu. Kendi anahtarınızı ekleyin. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Anahtar yanlış ya da e-postadan henüz onaylanmamış. |

Boş bir değer, anahtar yok sayılır.

## İzinler (WLM_PERMITTED)

Bu bir API anahtarı değildir ve kurulum programı bunu ayarlamaz. **Bunu yalnızca o izne kendiniz
sahipseniz ayarlayın.**

Bazı kaynaklar, kullanım koşulları veya robots.txt'leri izinsiz otomatik kullanımı yasakladığı için
varsayılan olarak kapalıdır. Yayıncıdan izniniz varsa, bir kaynağı kodunu `env` bloğundaki
`WLM_PERMITTED` içine virgülle ayırarak ekleyerek açın: `"WLM_PERMITTED": "in,de"`.

| Kod | Kaynak |
|---|---|
| `az` | Azerbaycan: e-qanun.az (Adalet Bakanlığı) |
| `bh` | Bahreyn: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Kolombiya: Función Pública, Gestor Normativo (konsolide mevzuat) |
| `de` | Almanya: NeuRIS (federal hukuki bilgi portalı, deneme hizmeti) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Yunanistan: Ulusal Basımevi, Resmî Gazete araması (search.et.gr) |
| `in` | Hindistan: India Code (indiacode.gov.in) |
| `mu` | Mauritius: Yüksek Mahkeme (supremecourt.govmu.org) |
| `sg` | Singapur: mahkeme kararları (elitigation.sg) |

İzin olmadan Fontes şunu söyler: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
