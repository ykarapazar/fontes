> Bu, maşın dəstəyi ilə hazırlanmış tərcümədir. Əsas olan ingiliscə versiyadır.

# API açarları

Fontes-dəki demək olar ki, hər mənbə açarsız işləyir. Üçü pulsuz açar tələb edir:

| Açar | Nəyi açır | Açarsız |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Fransa: Judilibre (məhkəmə qərarları) və Légifrance (qanunvericilik) | Fransa söndürülüb. `list_jurisdictions` onu qeyri-aktiv kimi göstərir. |
| `WLM_US_GOVINFO_KEY` | Amerika Birləşmiş Ştatları: govinfo axtarışı (federal məhkəmə qərarları, Statutes at Large, public laws) | Fontes ümumi `DEMO_KEY`-dən istifadə edir: IP ünvanı başına gündə təxminən 10 axtarış. Məlum qərarı açmaq və US Code açar tələb etmir. |
| `WLM_US_COURTLISTENER_KEY` | ABŞ ştatlarının məhkəmələri (`us-states`): bütün 50 ştatın və DC-nin ali və apellyasiya məhkəmələrinin qərarları, CourtListener-dən | ABŞ ştatlarının məhkəmə təcrübəsi söndürülüb. `list_jurisdictions` onu qeyri-aktiv kimi göstərir. |

Açarlar istəyə bağlıdır. Onları sonra əlavə edə bilərsiniz.

## Açar əlavə etmək

**Quraşdırıcı ilə.** Fontes quraşdırıldıqdan sonra quraşdırıcı açar əlavə etməyi təklif edir. Mac-da
**Açarları əlavə et** və ya ötürmək üçün **Hazır** klikləyin; Windows-da suala cavab verin (ötürmək
üçün Enter basın). Açarları sonra əlavə etmək və ya dəyişmək üçün **Açarları əlavə et və ya dəyiş**
işə salın:

- Mac: Fontes Installer proqramını yenidən açıb **Açarları əlavə et və ya dəyiş** seçin.
- Windows: Start menu-nu açın, sonra **Fontes** → **Açarları əlavə et və ya dəyiş**.

Yazdığınız görünmür. Hər açar üçün: onu yapışdırın, mövcud olanı saxlamaq üçün Enter basın və ya
silmək üçün `-` yazın. Açarlar Fontes-in artıq olduğu hər proqrama əlavə olunur.

**Claude Desktop genişləndirməsi (.mcpb) ilə.** Claude > Settings > Extensions > Fontes açın və
sahələri doldurun. Onların hamısı istəyə bağlıdır.

**Əl ilə.** Dəyişənləri proqramınızın MCP konfiqurasiyasındakı `fontes` qeydinin `env` blokuna
əlavə edin:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Hər dəyişiklikdən sonra proqramı yenidən başladın.

## Fransa: PISTE (pulsuz)

1. [piste.gouv.fr](https://piste.gouv.fr) saytında hesab yaradın. Bu, PISTE şərtlərini (CGU) qəbul
   etmək deməkdir.
2. API > **Consentement CGU API** bölməsinə keçin. **JUDILIBRE** və **Légifrance** (production)
   üçün şərtləri qəbul edin.
3. **Production application** yaradın. Sizin üçün yaradılmış `APP_SANDBOX` production-a çata
   bilmir. "Modifier l'application" altında **JUDILIBRE (production)** və **Légifrance
   (production)** işarələyin, sonra tətbiq edin.
4. Tətbiqin **Authentification** tabını açın. `client_id` və `client_secret` dəyərlərini
   kopyalayın.
5. **Açarları əlavə et və ya dəyiş** işə salın və onları yapışdırın.

Qısaca şərtlər:

- Məlumatlar: Licence Ouverte / Etalab 2.0. Kommersiya məqsədli təkrar istifadə daxil olmaqla
  təkrar istifadəyə mənbə göstərilməsi şərti ilə icazə verilir.
- Giriş məlumatlarınızı dərc etməyin və ya paylaşmayın. Onlar sızarsa, PISTE-ə bildirin.
- Légifrance API-si beta xidmətdir. O, dayandırıla bilər və onun kvotaları var (saniyə, dəqiqə və
  gün üzrə).
- Légifrance mətnləri autentik versiya deyil. Yalnız imzalanmış Journal officiel PDF-i autentikdir.
- Judilibre: hakimlərin və ya məhkəmə katiblərinin adlarından onların işini qiymətləndirmək,
  müqayisə etmək və ya proqnozlaşdırmaq üçün istifadə etməyin (Code de l'organisation judiciaire
  maddə L111-13; cinayət əməlidir).
- Judilibre: GDPR-a əməl edin. Tərəflərin şəxsiyyətini yenidən müəyyən etməyə çalışmayın.

Kvotalarınız PISTE-də API Sélectionnées > Actions > Consulter les quotas altındadır.

## Amerika Birləşmiş Ştatları: api.data.gov (pulsuz)

1. [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (açar ekranda göstərilir) və ya
   [api.data.gov/signup](https://api.data.gov/signup/) (açar sizə e-poçtla göndərilir) ünvanına
   keçin.
2. Adınızı və e-poçtunuzu daxil edin. "Ondan necə istifadə edəcəksiniz" sahəsi istəyə bağlıdır.
3. 40 simvollu açarı kopyalayın.
4. **Açarları əlavə et və ya dəyiş** işə salın və onu ABŞ açarı kimi yapışdırın.

Qısaca şərtlər:

- Öz açarınızla govinfo saatda 36.000-ə qədər sorğuya icazə verir.
- API-yə xas istifadə şərtləri tapmadıq (api.data.gov/terms/ mövcud deyil). Yoxlanılmayıb.
  Bax [govinfo-nun siyasətləri](https://www.govinfo.gov/about/policies) və
  [data.gov məxfilik siyasəti](https://data.gov/privacy-policy/).
- Açarı özünüzdə saxlayın.

## ABŞ ştatlarının məhkəmələri: CourtListener (pulsuz)

CourtListener 2010-cu ildən ABŞ məhkəmə qərarlarını toplayan və onları hamı üçün pulsuz edən qeyri-kommersiya təşkilatı [Free Law Project](https://free.law) tərəfindən idarə olunur. Öz hesablamasına görə, doqquz milyondan çox qərar saxlayır. Bu, rəsmi mənbə deyil: məhkəmələr qərarlarını özləri dərc edir, CourtListener isə onları məhkəmə saytlarından və skan edilmiş hüquqi hesabatlardan toplayır. Ondan gələn hər Fontes cavabı bunu bildirir. Fontes Free Law Project ilə əlaqəli deyil.

1. [courtlistener.com](https://www.courtlistener.com/sign-in/) saytında pulsuz hesab yaradın.
2. Profilinizi açın və API tokeninizi kopyalayın.
3. **Açarları əlavə et və ya dəyiş** işə salın və onu CourtListener açarı kimi yapışdırın.

Qısaca şərtlər ([tam şərtlər](https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies)):

- Token yalnız sizindir: onu paylaşmayın, birləşdirməyin və ya yenidən satmayın və bir neçə hesabdan istifadə etməyin.
- Süni intellekt tətbiqinin tokeninizlə etdiklərinə görə siz məsuliyyət daşıyırsınız.
- Süni intellektin onların məlumatları üzərindəki təhlilini Free Law Project tərəfindən hazırlanmış, təsdiq edilmiş və ya yoxlanılmış kimi təqdim etməyin.
- Pulsuz hesab dəqiqədə 5, saatda 50 və gündə 125 sorğuya icazə verir. Axtarış bir sorğudur; qərarı açmaq iki sorğudur. Free Law Project üzvlüyü limitləri artırır.
- CourtListener dəqiqliyə zəmanət vermir. Qərara etibar etməzdən əvvəl onu məhkəmənin nüsxəsi ilə yoxlayın.

## Açarlar harada saxlanılır

- **Quraşdırıcı və ya əl ilə:** hər proqramın MCP konfiqurasiya faylında, `fontes` qeydinin `env`
  blokunda adi mətn kimi. İstifadəçi fayllarınızı oxuya bilən hər kəs açarları oxuya bilər.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` və ya `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Claude Desktop genişləndirməsi (.mcpb):** Claude bu sahələri öz parametrlərində saxlayır və
  onları sisteminizin təhlükəsiz yaddaşı ilə qoruyur (Mac-də Keychain, Windows-da Credential
  Manager).

Hər dəyişiklikdən əvvəl quraşdırıcı konfiqurasiya faylının nüsxəsini onun yanında saxlayır
(`<file>.fontes-backup-<time>`). Açarları əlavə etdikdən sonra yaradılan nüsxələr də açarları
ehtiva edir. Lazım olmayan köhnə nüsxələri silin.

## Açarı dəyişmək və ya silmək

- **Açarları əlavə et və ya dəyiş** işə salın. Onu əvəz etmək üçün yeni açar yapışdırın və ya silmək
  üçün `-` yazın.
- Və ya `env` blokunu əl ilə redaktə edin və proqramı yenidən başladın.
- Fontes-i silmək onun bütün qeydini, açarlar daxil olmaqla, silir. Ehtiyat nüsxələri silmir.
- Açar sızıbsa, onu mənbədə də əvəz edin: PISTE-də tətbiqiniz üçün yeni giriş məlumatları yaradın;
  api.data.gov üçün yeni açar alın.

## Görə biləcəyiniz mesajlar

| Mesaj | Mənası |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Fransa açarı yoxdur. Əlavə edin. |
| `Inactive: needs a free PISTE account. ...` (`list_jurisdictions`-da) | Eynisi. |
| `PISTE refused the client credentials ...` | ID və ya secret səhvdir və ya artıq etibarlı deyil. Hər ikisini Authentification tabından yenidən kopyalayın. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Tətbiqiniz həmin API-yə abunə deyil və ya onun şərtlərini qəbul etməmisiniz. Bax 2-ci və 3-cü addımlar. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | ABŞ açarı yoxdur. Axtarış gündə bir neçə çağırış üçün işləyir. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Demo açarın limiti bitib. Öz açarınızı əlavə edin. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Açar səhvdir və ya hələ e-poçtdan təsdiqlənməyib. |

Boş dəyər açarın olmaması kimi qəbul edilir.

## İcazələr (WLM_PERMITTED)

Bu, API açarı deyil və quraşdırıcı onu təyin etmir. **Onu yalnız həmin icazə özünüzdə varsa təyin
edin.**

Bəzi mənbələr defolt olaraq söndürülüb, çünki onların şərtləri və ya robots.txt-i icazəsiz
avtomatlaşdırılmış istifadəni qadağan edir. Naşirdən icazəniz varsa, mənbəni onun kodunu `env`
blokunda `WLM_PERMITTED`-ə vergüllə ayıraraq əlavə etməklə yandırın: `"WLM_PERMITTED": "in,de"`.

| Kod | Mənbə |
|---|---|
| `az` | Azərbaycan: e-qanun.az (Ədliyyə Nazirliyi) |
| `bh` | Bəhreyn: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Kolumbiya: Función Pública, Gestor Normativo (konsolidə edilmiş qanunvericilik) |
| `de` | Almaniya: NeuRIS (federal hüquqi informasiya portalı, sınaq xidməti) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Yunanıstan: Milli Mətbəə, Hökumət Qəzetində axtarış (search.et.gr) |
| `mu` | Mavriki: Ali Məhkəmə (supremecourt.govmu.org) |
| `sg` | Sinqapur: məhkəmə qərarları (elitigation.sg) |

İcazə olmadan Fontes bunu deyir: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
