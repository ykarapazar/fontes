> Bu, maşın dəstəyi ilə hazırlanmış tərcümədir. Əsas olan ingiliscə versiyadır.

# Fontes: suallar və cavablar

## Fontes nədir?

Pulsuz, açıq mənbəli MCP serveri (Apache 2.0). O, Model Context Protocol ilə işləyən istənilən
proqrama (Claude, Codex, Cursor, VS Code, Gemini CLI və digərləri) 120-dən çox yurisdiksiyada və
beynəlxalq məhkəmədə (124 adapter) məhkəmə qərarlarını və qanunvericiliyi məhkəmə və dövlət
saytlarında canlı olaraq axtarmağa imkan verir. Hər nəticə öz mənbəyini göstərir və orijinala
keçid verir.

## Mətnlər rəsmidirmi?

Əksərən bəli, amma həmişə yox.

- Mənbələrin əksəriyyətini məhkəmə, nazirlik və ya rəsmi qəzet idarə edir.
- Bəzi konsolidə edilmiş mətnləri dövlət dərc edir, lakin onlar açıq şəkildə qeyri-rəsmidir:
  yalnız rəsmi qəzet autentikdir.
- Bir neçə mənbə ümumiyyətlə dövlət saytı deyil (məsələn, LexiVox, LawPhil, Maqam, Wikisource).

Fontes bunlardan birindən gələn hər cavaba "Qeyri-rəsmi mənbə" qeydi əlavə edir. Hər hansı şeyə
istinad etməzdən əvvəl rəsmi nəşri yoxlayın. [README](README.md#əhatə) faylındakı əhatə cədvəli və
`list_jurisdictions` hər yurisdiksiyanın mənbəyini göstərir.

## Hansı yurisdiksiyaları və nə dərəcədə əhatə edir?

124 adapter: 108 BMT üzvü dövlət, Honq-Konq, Kosovo, Fələstin, Tayvan, DIFC Məhkəmələri və
11 beynəlxalq məhkəmə və qurum (məsələn, Avropa İnsan Hüquqları Məhkəməsi, AB, BMƏ və ÜTT).

Əhatə çox fərqlənir. Ciddi qaydaya görə (ən yüksək ümumi məhkəmənin presedentlərinə və ya
konstitusiyaya və əsas qanunlara tam çatılması), 124-dən 72-si əhatə olunmuş sayılır.
[COVERAGE.md](../../COVERAGE.md) (ingiliscə) hər yurisdiksiya üçün Fontes-in nəyə çatdığını, nəyə
çatmadığını və səbəbini sadalayır.

## API açarı lazımdırmı?

Demək olar ki, hər yurisdiksiya üçün yox. Bəzi mənbələr pulsuz açar tələb edir: bax
[KEYS.md](KEYS.md).

- **Fransa:** bəli. `WLM_FR_PISTE_CLIENT_ID` və `WLM_FR_PISTE_CLIENT_SECRET` təyin edilənə qədər
  Fransa söndürülüb. Bunlar Judilibre və Légifrance-a abunə olunmuş tətbiqi olan pulsuz PISTE
  hesabından (piste.gouv.fr) alınır.
- **Amerika Birləşmiş Ştatları:** istəyə bağlı. Məhkəmə təcrübəsində axtarış açarsız işləyir, lakin
  ümumi demo açarı IP ünvanı başına gündə yalnız təxminən 10 axtarışa icazə verir.
  `WLM_US_GOVINFO_KEY`-də pulsuz api.data.gov açarı bu limiti artırır.

Bunları proqramınızın MCP parametrlərində Fontes serveri üçün mühit dəyişənləri kimi təyin edin.
Quraşdırıcı çıxdıqdan sonra o, quraşdırmadan sonra bunları soruşacaq, onun **Açarları əlavə et və
ya dəyiş** başladıcısı isə sonradan onları dəyişəcək.

Bundan ayrı olaraq, bir neçə mənbə öz şərtlərində avtomatlaşdırılmış girişin naşirin icazəsini
tələb etdiyini bildirir. Onlar OFF kimi işarələnib və söndürülmüş qalır. Açar bunu dəyişmir; yalnız
naşirin icazəsi dəyişir (o halda `WLM_PERMITTED=<codes>` təyin edin).

## Kompüterimdən nə çıxır?

Axtarışlarınız yalnız axtarış aparılan mənbəyə gedir. Fontes verilənlər bazası saxlamır və hesab
tələb etmir.

Mənbələrdən əlavə, Fontes gündə bir dəfə PyPI-dan daha yeni versiyanın olub-olmadığını soruşur
(onu `FONTES_NO_UPDATE_CHECK=1` ilə söndürün). İstifadə sayları siz yandırmadıqca söndürülüb, xəta
hesabatı isə yalnız siz onu görüb təsdiq etdikdən sonra göndərilir. Süni intellekt proqramınız
söhbətinizi öz şərtləri çərçivəsində görür.

Tam təfərrüatlar: [PRIVACY.md](PRIVACY.md).

## Bu, hüquqi məsləhətdirmi?

Xeyr. Fontes tədqiqat alətidir. O, mətnləri tapır; onların sizin işiniz üçün nə demək olduğunu
söyləmir və ondan istifadə heç kimlə vəkil–müştəri münasibəti yaratmır. Süni intellekt proqramı
mətni səhv oxuya bilər, buna görə qərara və ya müddəaya etibar etməzdən əvvəl onun tam mətnini
oxuyun. Məsləhət üçün sualınızın yarandığı yerdə səlahiyyətli vəkilə müraciət edin.

## Onu kim saxlayır? İşləməyə davam edəcəkmi?

Bir nəfər: Yüce Karapazar. Fontes-in arxasında şirkət, dəstək müqaviləsi və ya xidmət səviyyəsi
öhdəliyi yoxdur. Heç bir hüquqi xidmət göstərilmir.

Mənbələr gündə bir dəfə yoxlanılır və nəticələr
[vəziyyət səhifəsində](https://ykarapazar.github.io/fontes/status/?lang=az) dərc olunur. Məhkəmə və
dövlət saytları xəbərdarlıqsız dəyişir, buna görə mənbə istənilən vaxt sıradan çıxa bilər. Hər
hansı mənbənin və ya Fontes-in özünün işləməyə davam edəcəyinə zəmanət yoxdur. Fontes zəmanətsiz,
"olduğu kimi" təqdim olunur ([LICENSE](../../../LICENSE) faylının 7-ci və 8-ci bölmələri).

## Mətn səhvdir, köhnəlib və ya mənbə işləmir. Bunu necə bildirim?

- "Broken or wrong source" forması ilə issue açın:
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Hansı yurisdiksiya olduğunu, nə
  soruşduğunuzu, nə aldığınızı və düzgün mətni göstərən rəsmi səhifəni qeyd edin.
- Və ya süni intellekt proqramınızdan "Fontes xətasını bildirməyi" xahiş edin (və ya
  `fontes report-bug` işə salın). Hər hansı şey göndərilməzdən əvvəl hesabatı görürsünüz.
- Və ya fontesmcp@proton.me ünvanına e-poçt göndərin.

Hesabata müştəri məlumatlarını və ya məxfi faktları daxil etməyin.

**Mənbələrdən birini idarə edirsinizsə** və nəsə səhvdirsə (şərtləriniz, robots.txt-iniz, sorğu
limitləriniz), fontesmcp@proton.me ünvanına e-poçt göndərin. Mənbə düzəldiləcək və ya
söndürüləcək.

## Fontes host edilən (hosted) hüquqi tədqiqat alətlərindən nə ilə fərqlənir?

- **O, sizin kompüterinizdə işləyir.** Fontes serveri və hesab yoxdur. Bu, həm də o deməkdir ki, o
  yalnız yerli MCP serverini işə sala bilən proqramlarda (Claude Desktop, Codex, Cursor, VS Code və
  oxşarları) işləyir, yalnız host edilən konnektorları qəbul edən yalnız-veb proqramlarda işləmir.
- **Onun verilənlər bazası yoxdur.** Hər axtarış canlı olaraq naşirin öz saytına və ya API-sinə
  gedir, buna görə nəticələr mənbə qədər aktualdır, axtarış keyfiyyəti isə mənbənin özününkündür.
  Seçilmiş indeks üzərində semantik axtarış yoxdur.
- **İstifadə limiti qoymur.** Fontes-in aylıq çağırış limiti yoxdur. O, hər sayta sorğularını
  aralıqlarla göndərir və bəzi mənbələr onlara nə qədər tez və ya nə qədər tez-tez sorğu
  göndərilə biləcəyini məhdudlaşdırır.
- **O, açıq mənbəlidir.** Hər adapteri oxuya və hər mətnin dəqiq haradan gəldiyini görə
  bilərsiniz.
- **Onun arxasında təchizatçı yoxdur.** Müqavilə, dəstək xidməti və ya fasiləsiz işləmə öhdəliyi
  yoxdur (bax "Onu kim saxlayır?").

## Hansı proqramlar və sistemlərlə işləyir?

Yerli (stdio) serveri işə sala bilən istənilən MCP proqramı ilə, məsələn Claude Desktop, Claude
Code, Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio və Cline. Fontes
macOS, Windows və Linux-da, uv işləyən hər yerdə (Python 3.13+) işləyir. Mac və Windows üçün bir
kliklə quraşdırıcı yoldadır. O, Claude Desktop, Codex, Claude Code, Cursor, VS Code, Windsurf,
Gemini CLI, Zed, LM Studio və Cline-ı bir dəfəyə quraşdırır. Hər proqram üçün addımlar:
[INSTALL.md](INSTALL.md).

## Kodla töhfə verə bilərəmmi?

Hazırda yox. Issue-lar, mənbə hesabatları və yurisdiksiya sorğuları məmnuniyyətlə qəbul edilir. Bax
[CONTRIBUTING.md](../../../CONTRIBUTING.md).
