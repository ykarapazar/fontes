> Энэ бол машины тусламжтай хийсэн орчуулга. Англи хэл дээрх хувилбар нь давамгайлна.

# API түлхүүрүүд

Fontes дахь бараг бүх эх сурвалж түлхүүргүй ажилладаг. Гурвад нь үнэгүй түлхүүр хэрэгтэй:

| Түлхүүр | Юуг нээдэг | Түүнгүйгээр |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Франц: Judilibre (шүүхийн шийдвэр) болон Légifrance (хууль тогтоомж) | Франц унтраалттай. `list_jurisdictions` үүнийг идэвхгүй гэж харуулна. |
| `WLM_US_GOVINFO_KEY` | Америкийн Нэгдсэн Улс: govinfo хайлт (холбооны шүүхийн шийдвэрүүд, Statutes at Large, public laws) | Fontes хуваалцсан `DEMO_KEY`-г ашиглана: IP хаяг тус бүрд өдөрт ойролцоогоор 10 хайлт. Мэдэгдэж буй шийдвэрийг нээх болон US Code-д түлхүүр хэрэггүй. |
| `WLM_US_COURTLISTENER_KEY` | АНУ-ын мужийн шүүхүүд (`us-states`): 50 муж болон DC-ийн дээд болон давж заалдах шатны шүүхүүдийн шийдвэрүүд, CourtListener-ээс | АНУ-ын мужийн шүүхийн практик унтраалттай. `list_jurisdictions` үүнийг идэвхгүй гэж харуулна. |

Түлхүүрүүд заавал биш. Тэдгээрийг дараа нь нэмж болно.

## Түлхүүр нэмэх

**Суулгагчаар.** Fontes тохируулагдсаны дараа суулгагч түлхүүр нэмэхийг санал болгоно. Mac дээр
**Түлхүүр нэмэх**-ийг, эсвэл алгасахын тулд **Дууссан**-ыг товшино уу; Windows дээр асуултад
хариулна уу (алгасахын тулд Enter дарна уу). Түлхүүрүүдийг дараа нь нэмэх эсвэл өөрчлөхийн тулд
**Add or change keys**-ийг ажиллуулна уу:

- Mac: Fontes Installer аппыг дахин нээгээд **Түлхүүр нэмэх эсвэл өөрчлөх**-ийг сонгоно уу.
- Windows: Start цэсийг нээгээд, дараа нь **Fontes** → **Түлхүүр нэмэх эсвэл өөрчлөх**.

Бичсэн зүйл харагдахгүй. Түлхүүр бүрт: түүнийг буулгах, байгааг нь хэвээр үлдээхийн тулд Enter дарах, эсвэл
устгахын тулд `-` гэж бичнэ үү. Түлхүүрүүд Fontes аль хэдийн байгаа апп бүрт орно.

**Claude Desktop өргөтгөлөөр (.mcpb).** Claude > Settings > Extensions > Fontes-ийг нээгээд
талбаруудыг бөглөнө үү. Бүгд заавал биш.

**Гараар.** Хувьсагчдыг аппынхаа MCP тохиргоон дахь `fontes` бичлэгийн `env` блокт нэмнэ үү:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Аливаа өөрчлөлтийн дараа аппыг дахин эхлүүлнэ үү.

## Франц: PISTE (үнэгүй)

1. [piste.gouv.fr](https://piste.gouv.fr)-д бүртгэл үүсгэнэ үү. Энэ нь PISTE-ийн нөхцөлийг (CGU) хүлээн зөвшөөрнө гэсэн үг.
2. API > **Consentement CGU API** руу орно уу. **JUDILIBRE** болон **Légifrance** (production)-ийн нөхцөлийг хүлээн зөвшөөрнө үү.
3. **Production application** үүсгэнэ үү. Танд зориулж үүсгэсэн `APP_SANDBOX` production-д хүрч чадахгүй.
   "Modifier l'application" хэсэгт **JUDILIBRE (production)** болон **Légifrance (production)**-ийг чагтлаад, apply хийнэ үү.
4. Аппын **Authentification** табыг нээнэ үү. `client_id` болон `client_secret`-ийг хуулна уу.
5. **Add or change keys**-ийг ажиллуулаад тэдгээрийг буулгана уу.

Нөхцөл, товчхондоо:

- Өгөгдөл: Licence Ouverte / Etalab 2.0. Арилжааны зорилгоор оролцуулан дахин ашиглахыг эх сурвалжийг заасан нөхцөлтэйгээр зөвшөөрнө.
- Нэвтрэх мэдээллээ бүү нийтэл, бүү хуваалц. Алдагдсан бол PISTE-д мэдэгдэнэ үү.
- Légifrance API бол бета үйлчилгээ. Үүнийг түр зогсоож болох бөгөөд квоттой (секунд, минут, өдөр тутмын).
- Légifrance-ийн текстүүд баталгаат хувилбар биш. Зөвхөн гарын үсэгтэй Journal officiel PDF нь баталгаат.
- Judilibre: шүүгч эсвэл шүүхийн ажилтны нэрийг тэдний ажлыг үнэлэх, харьцуулах эсвэл таамаглахад бүү ашигла
  (Code de l'organisation judiciaire art. L111-13; эрүүгийн гэмт хэрэг).
- Judilibre: GDPR-ийг дагана уу. Талуудыг дахин таних гэж бүү оролд.

Таны квотууд PISTE дээр API Sélectionnées > Actions > Consulter les quotas хэсэгт байна.

## Америкийн Нэгдсэн Улс: api.data.gov (үнэгүй)

1. [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (түлхүүрийг дэлгэц дээр харуулна)
   эсвэл [api.data.gov/signup](https://api.data.gov/signup/) (түлхүүрийг танд имэйлээр илгээнэ) руу орно уу.
2. Нэр, имэйлээ оруулна уу. "how will you use it" талбар заавал биш.
3. 40 тэмдэгттэй түлхүүрийг хуулна уу.
4. **Add or change keys**-ийг ажиллуулаад үүнийг АНУ-ын түлхүүр болгон буулгана уу.

Нөхцөл, товчхондоо:

- Өөрийн түлхүүрээр govinfo цагт 36,000 хүртэл хүсэлт зөвшөөрдөг.
- Бид API-д зориулсан тусгай үйлчилгээний нөхцөл олоогүй (api.data.gov/terms/ байхгүй). Баталгаажаагүй.
  [govinfo-ийн бодлого](https://www.govinfo.gov/about/policies) болон
  [data.gov-ийн нууцлалын бодлогыг](https://data.gov/privacy-policy/) үзнэ үү.
- Түлхүүрээ өөртөө хадгална уу.

## АНУ-ын мужийн шүүхүүд: CourtListener (үнэгүй)

CourtListener-ийг ашгийн бус байгууллага [Free Law Project](https://free.law) ажиллуулдаг бөгөөд 2010 оноос хойш АНУ-ын шүүхийн шийдвэрүүдийг цуглуулж, хүн бүрт үнэгүй нээлттэй болгосоор ирсэн. Тэдний өөрсдийн тооцоогоор есөн саяас дээш шийдвэр агуулдаг. Энэ нь албан ёсны эх сурвалж биш: шүүхүүд өөрсдийн шийдвэрийг нийтэлдэг бөгөөд CourtListener тэдгээрийг шүүхийн вэбсайт болон сканнердсан хуулийн тайлангаас цуглуулдаг. Fontes-ийн түүнээс авсан хариулт бүр үүнийг дурддаг. Fontes нь Free Law Project-той холбоогүй.

1. [courtlistener.com](https://www.courtlistener.com/sign-in/) дээр үнэгүй бүртгэл үүсгэнэ үү.
2. Профайлаа нээж API токеноо хуулна уу.
3. **Add or change keys**-ийг ажиллуулаад үүнийг CourtListener-ийн түлхүүр болгон буулгана уу.

Нөхцөл, товчхондоо ([бүрэн нөхцөл](https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies)):

- Токен зөвхөн таных: бусдад бүү өг, бусадтай бүү нэгтгэ, дахин бүү заа, мөн хэд хэдэн бүртгэл бүү ашигла.
- AI апп таны токеноор юу хийхийн хариуцлагыг та хүлээнэ.
- AI-ийн тэдний өгөгдөлд хийсэн дүн шинжилгээг Free Law Project гаргасан, дэмжсэн эсвэл шалгасан мэтээр бүү танилцуул.
- Үнэгүй бүртгэл минутад 5, цагт 50, өдөрт 125 хүсэлт зөвшөөрдөг. Нэг хайлт нэг хүсэлт; нэг шийдвэр нээх нь хоёр хүсэлт. Free Law Project-ийн гишүүнчлэл эдгээр хязгаарыг нэмэгдүүлдэг.
- CourtListener нь үнэн зөв байхыг баталгаажуулдаггүй. Шийдвэрт найдахаасаа өмнө шүүхийн хуулбартай тулгаж шалгана уу.

## Түлхүүрүүд хаана хадгалагддаг вэ

- **Суулгагч эсвэл гараар:** апп бүрийн MCP тохиргооны файлд, `fontes` бичлэгийн `env` блокт энгийн
  текстээр. Таны хэрэглэгчийн файлуудыг уншиж чаддаг хэн ч түлхүүрүүдийг уншиж чадна.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` эсвэл `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Claude Desktop өргөтгөл (.mcpb):** Claude эдгээр талбарыг тохиргоондоо хадгалж, таны системийн
  аюулгүй хадгалалтаар (Mac дээр Keychain, Windows дээр Credential Manager) хамгаалдаг.

Өөрчлөлт бүрийн өмнө суулгагч тохиргооны файлын хуулбарыг хажууд нь хадгалдаг
(`<file>.fontes-backup-<time>`). Та түлхүүр нэмсний дараа хийгдсэн хуулбаруудад түлхүүрүүд мөн бий. Хэрэггүй
хуучин хуулбаруудыг устгана уу.

## Түлхүүр өөрчлөх эсвэл устгах

- **Add or change keys**-ийг ажиллуулна уу. Солихын тулд шинэ түлхүүр буулгах, эсвэл устгахын тулд `-` гэж бичнэ үү.
- Эсвэл `env` блокийг гараар засаад аппыг дахин эхлүүлнэ үү.
- Fontes-ийг устгахад түүний бичлэг бүхэлдээ, түлхүүрүүдийн хамт хасагдана. Нөөц хуулбаруудыг устгахгүй.
- Түлхүүр алдагдсан бол эх сурвалж дээр нь ч солино уу: PISTE дээр аппдаа шинэ нэвтрэх мэдээлэл үүсгэх;
  api.data.gov-ийн хувьд шинэ түлхүүрт бүртгүүлнэ үү.

## Таны харж болох мессежүүд

| Мессеж | Утга |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Францын түлхүүр алга. Нэмнэ үү. |
| `Inactive: needs a free PISTE account. ...` (`list_jurisdictions`-д) | Дээрхтэй адил. |
| `PISTE refused the client credentials ...` | ID эсвэл secret буруу эсвэл хүчингүй болсон. Хоёуланг нь Authentification табаас дахин хуулна уу. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Таны апп тэр API-д бүртгүүлээгүй, эсвэл та түүний нөхцөлийг хүлээн зөвшөөрөөгүй. 2 ба 3-р алхмыг үзнэ үү. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | АНУ-ын түлхүүр алга. Хайлт өдөрт цөөн дуудлагад ажиллана. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Демо түлхүүр дууссан. Өөрийн түлхүүрээ нэмнэ үү. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Түлхүүр буруу, эсвэл имэйлээс хараахан баталгаажаагүй. |

Хоосон утгыг түлхүүргүй гэж тооцно.

## Зөвшөөрөл (WLM_PERMITTED)

Энэ бол API түлхүүр биш бөгөөд суулгагч үүнийг тохируулдаггүй. **Тэр зөвшөөрлийг та өөрөө авсан тохиолдолд л
үүнийг тохируулна уу.**

Зарим эх сурвалж нөхцөл эсвэл robots.txt нь зөвшөөрөлгүй автомат ашиглалтыг хориглодог тул анхдагчаар
унтраалттай. Хэрэв та нийтлэгчээс зөвшөөрөл авсан бол эх сурвалжийн кодыг `env` блок дахь
`WLM_PERMITTED`-д таслалаар тусгаарлан нэмж идэвхжүүлнэ үү: `"WLM_PERMITTED": "in,de"`.

| Код | Эх сурвалж |
|---|---|
| `az` | Азербайжан: e-qanun.az (Хууль зүйн яам) |
| `bh` | Бахрейн: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Колумб: Función Pública, Gestor Normativo (нэмэлт өөрчлөлтийг нэгтгэсэн хууль тогтоомж) |
| `de` | Герман: NeuRIS (холбооны эрх зүйн мэдээллийн портал, туршилтын үйлчилгээ) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Грек: National Printing Office, Government Gazette search (search.et.gr) |
| `mu` | Маврики: Supreme Court (supremecourt.govmu.org) |
| `sg` | Сингапур: шүүхийн шийдвэрүүд (elitigation.sg) |

Зөвшөөрөлгүй бол Fontes ингэж хэлнэ: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
