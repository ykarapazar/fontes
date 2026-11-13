> Bu çeviri makine desteğiyle hazırlanmıştır. Esas olan İngilizce sürümdür.

# API anahtarları

Fontes'teki neredeyse her kaynak anahtarsız çalışır. İkisi ücretsiz bir anahtar gerektirir:

| Anahtar | Neyi açar | Anahtar olmadan |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Fransa: Judilibre (mahkeme kararları) ve Légifrance (mevzuat) | Fransa kapalıdır. `list_jurisdictions` onu etkin değil olarak gösterir. |
| `WLM_US_GOVINFO_KEY` | Amerika Birleşik Devletleri: govinfo araması (federal mahkeme kararları, Statutes at Large, public laws) | Fontes ortak `DEMO_KEY`'i kullanır: IP adresi başına günde yaklaşık 10 arama. Bilinen bir kararı açmak ve US Code anahtar gerektirmez. |

Anahtarlar isteğe bağlıdır. Bunları daha sonra ekleyebilirsiniz.

## Anahtar eklemek

**Kurulum programıyla.** Kurulum sırasında kurulum programı anahtar eklemek isteyip istemediğinizi
sorar. Atlamak için **Şimdi değil**'i seçin (veya Enter'a basın). Anahtarları daha sonra eklemek veya
değiştirmek için **Anahtar ekle veya değiştir**'i çalıştırın:

- Mac: Fontes Installer uygulamasını yeniden açıp **Anahtar ekle veya değiştir**'i seçin ya da kurulum
  programı klasöründeki `Add or change keys.command` dosyasına çift tıklayın.
- Windows: kurulum programı klasöründeki `Add or change keys.cmd` dosyasına çift tıklayın. Windows
  kurulum programı, kullanıma sunulduğunda, bunu Start menu > Fontes altına da koyar.

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
