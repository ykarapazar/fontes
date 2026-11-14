> ეს თარგმანი შესრულებულია მანქანური თარგმანის დახმარებით. განმსაზღვრელია ინგლისური ვერსია.

# API გასაღებები

Fontes-ის თითქმის ყველა წყარო გასაღების გარეშე მუშაობს. ორს უფასო გასაღები სჭირდება:

| გასაღები | რას ხსნის | მის გარეშე |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | საფრანგეთი: Judilibre (სასამართლო გადაწყვეტილებები) და Légifrance (კანონმდებლობა) | საფრანგეთი გამორთულია. `list_jurisdictions` მას არააქტიურად აჩვენებს. |
| `WLM_US_GOVINFO_KEY` | ამერიკის შეერთებული შტატები: govinfo ძიება (ფედერალური სასამართლოების გადაწყვეტილებები, Statutes at Large, public laws) | Fontes იყენებს საერთო `DEMO_KEY`-ს: IP მისამართზე დღეში დაახლოებით 10 ძიება. ცნობილი გადაწყვეტილების გასახსნელად და US Code-ისთვის გასაღები არ არის საჭირო. |

გასაღებები არასავალდებულოა. მათი დამატება მოგვიანებითაც შეგიძლიათ.

## გასაღების დამატება

**ინსტალერით.** Fontes-ის დაყენების შემდეგ ინსტალერი გთავაზობთ გასაღებების დამატებას. Mac-ზე
დააწკაპუნეთ **გასაღებების დამატება**-ზე, ან გამოსატოვებლად **მზადაა**-ზე; Windows-ზე უპასუხეთ
შეკითხვას (გამოსატოვებლად დააჭირეთ Enter-ს). გასაღებების მოგვიანებით დამატების ან შეცვლისთვის
გაუშვით **Add or change keys**:

- Mac: ხელახლა გახსენით Fontes Installer აპი და აირჩიეთ **გასაღებების დამატება ან შეცვლა**.
- Windows: ინსტალერის საქაღალდეში ორჯერ დააწკაპუნეთ `Add or change keys.cmd`-ზე. Windows-ის
  ინსტალაციის პროგრამა, როცა ხელმისაწვდომი იქნება, მას ასევე განათავსებს Start მენიუში > Fontes.

აკრეფილი დამალულია. თითოეული გასაღებისთვის: ჩასვით ის, დააჭირეთ Enter-ს არსებულის
შესანარჩუნებლად, ან აკრიფეთ `-` მის წასაშლელად. გასაღებები იწერება ყველა აპში, რომელსაც უკვე
აქვს Fontes.

**Claude Desktop-ის გაფართოებით (.mcpb).** გახსენით Claude > Settings > Extensions > Fontes და
შეავსეთ ველები. ყველა მათგანი არასავალდებულოა.

**ხელით.** დაამატეთ ცვლადები თქვენი აპის MCP კონფიგურაციაში `fontes` ჩანაწერის `env` ბლოკში:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

ნებისმიერი ცვლილების შემდეგ გადატვირთეთ აპი.

## საფრანგეთი: PISTE (უფასო)

1. შექმენით ანგარიში [piste.gouv.fr](https://piste.gouv.fr)-ზე. ეს ნიშნავს PISTE-ის პირობების (CGU) მიღებას.
2. გადადით API > **Consentement CGU API**-ზე. მიიღეთ **JUDILIBRE**-ისა და **Légifrance**-ის (production) პირობები.
3. შექმენით **საწარმოო აპი** (production application). თქვენთვის შექმნილ `APP_SANDBOX`-ს
   საწარმოო გარემოზე წვდომა არ აქვს. „Modifier l'application“-ში მონიშნეთ
   **JUDILIBRE (production)** და **Légifrance (production)**, შემდეგ გამოიყენეთ.
4. გახსენით აპის **Authentification** ჩანართი. დააკოპირეთ `client_id` და `client_secret`.
5. გაუშვით **Add or change keys** და ჩასვით ისინი.

პირობები მოკლედ:

- მონაცემები: Licence Ouverte / Etalab 2.0. ხელახალი გამოყენება, მათ შორის კომერციული, დაშვებულია წყაროს მითითებით.
- არ გამოაქვეყნოთ და არ გადასცეთ თქვენი წვდომის მონაცემები. თუ ისინი გაჟონავს, აცნობეთ PISTE-ს.
- Légifrance API ბეტა სერვისია. ის შეიძლება შეჩერდეს და აქვს კვოტები (წამში, წუთში და დღეში).
- Légifrance-ის ტექსტები არ არის ავთენტური ვერსია. ავთენტურია მხოლოდ ხელმოწერილი Journal officiel PDF.
- Judilibre: არ გამოიყენოთ მოსამართლეების ან სასამართლოს პერსონალის სახელები მათი საქმიანობის
  შესაფასებლად, შესადარებლად ან პროგნოზირებისთვის (Code de l'organisation judiciaire, მუხლი
  L111-13; სისხლის სამართლის დანაშაული).
- Judilibre: დაიცავით GDPR. არ სცადოთ მხარეების ხელახალი იდენტიფიცირება.

თქვენი კვოტები PISTE-შია: API Sélectionnées > Actions > Consulter les quotas.

## ამერიკის შეერთებული შტატები: api.data.gov (უფასო)

1. გადადით [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup)-ზე (გასაღები ეკრანზე
   გამოჩნდება) ან [api.data.gov/signup](https://api.data.gov/signup/)-ზე (გასაღები ელფოსტით
   გამოგეგზავნებათ).
2. შეიყვანეთ თქვენი სახელი და ელფოსტა. ველი „how will you use it“ არასავალდებულოა.
3. დააკოპირეთ 40-ნიშნა გასაღები.
4. გაუშვით **Add or change keys** და ჩასვით ის, როგორც აშშ-ის გასაღები.

პირობები მოკლედ:

- საკუთარი გასაღებით govinfo საათში 36 000-მდე მოთხოვნას უშვებს.
- API-ს სპეციფიკური გამოყენების პირობები ვერ ვიპოვეთ (api.data.gov/terms/ არ არსებობს).
  გადაუმოწმებელია. იხილეთ [govinfo-ის პოლიტიკები](https://www.govinfo.gov/about/policies) და
  [data.gov-ის კონფიდენციალურობის პოლიტიკა](https://data.gov/privacy-policy/).
- გასაღები საკუთარ თავთან შეინახეთ.

## სად ინახება გასაღებები

- **ინსტალერით ან ხელით:** როგორც ჩვეულებრივი ტექსტი თითოეული აპის MCP კონფიგურაციის ფაილში,
  `fontes` ჩანაწერის `env` ბლოკში. ნებისმიერს, ვისაც თქვენი მომხმარებლის ფაილების წაკითხვა
  შეუძლია, გასაღებების წაკითხვაც შეუძლია.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` ან `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Claude Desktop-ის გაფართოება (.mcpb):** Claude ამ ველებს თავის პარამეტრებში ინახავს და
  იცავს თქვენი სისტემის უსაფრთხო საცავით (Keychain Mac-ზე, Credential Manager Windows-ზე).

ყოველი ცვლილების წინ ინსტალერი კონფიგურაციის ფაილის ასლს მის გვერდით ინახავს
(`<file>.fontes-backup-<time>`). გასაღებების დამატების შემდეგ შექმნილი ასლებიც შეიცავს
გასაღებებს. წაშალეთ ძველი ასლები, რომლებიც არ გჭირდებათ.

## გასაღების შეცვლა ან წაშლა

- გაუშვით **Add or change keys**. ჩასვით ახალი გასაღები მის ჩასანაცვლებლად, ან აკრიფეთ `-` მის წასაშლელად.
- ან ხელით შეცვალეთ `env` ბლოკი და გადატვირთეთ აპი.
- Fontes-ის დეინსტალაცია შლის მის მთელ ჩანაწერს, გასაღებების ჩათვლით. ის არ შლის სარეზერვო ასლებს.
- თუ გასაღები გაჟონა, შეცვალეთ ის წყაროშიც: PISTE-ზე შექმენით ახალი წვდომის მონაცემები თქვენი
  აპისთვის, api.data.gov-ზე კი დარეგისტრირდით ახალი გასაღებისთვის.

## შეტყობინებები, რომლებიც შეიძლება ნახოთ

| შეტყობინება | მნიშვნელობა |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | საფრანგეთის გასაღები არ არის. დაამატეთ. |
| `Inactive: needs a free PISTE account. ...` (`list_jurisdictions`-ში) | იგივე. |
| `PISTE refused the client credentials ...` | ID ან secret არასწორია ან აღარ მოქმედებს. ორივე ხელახლა დააკოპირეთ Authentification ჩანართიდან. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | თქვენი აპი არ არის გამოწერილი ამ API-ზე, ან მისი პირობები არ მიგიღიათ. იხილეთ მე-2 და მე-3 ნაბიჯები. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | აშშ-ის გასაღები არ არის. ძიება მუშაობს დღეში რამდენიმე გამოძახებისთვის. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | სადემონსტრაციო გასაღები ამოიწურა. დაამატეთ საკუთარი გასაღები. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | გასაღები არასწორია ან ჯერ არ არის გააქტიურებული ელფოსტიდან. |

ცარიელი მნიშვნელობა გასაღების არარსებობას უდრის.

## ნებართვები (WLM_PERMITTED)

ეს არ არის API გასაღები და ინსტალერი მას არ აყენებს. **დააყენეთ ის მხოლოდ მაშინ, თუ ეს
ნებართვა თავად გაქვთ.**

ზოგიერთი წყარო ნაგულისხმევად გამორთულია, რადგან მისი პირობები ან robots.txt კრძალავს
ავტომატიზებულ გამოყენებას ნებართვის გარეშე. თუ გამომცემლის ნებართვა გაქვთ, ჩართეთ წყარო მისი
კოდის დამატებით `WLM_PERMITTED`-ში, მძიმით გამოყოფილი, `env` ბლოკში:
`"WLM_PERMITTED": "in,de"`.

| კოდი | წყარო |
|---|---|
| `az` | აზერბაიჯანი: e-qanun.az (იუსტიციის სამინისტრო) |
| `bh` | ბაჰრეინი: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | კოლუმბია: Función Pública, Gestor Normativo (კონსოლიდირებული კანონმდებლობა) |
| `de` | გერმანია: NeuRIS (ფედერალური სამართლებრივი ინფორმაციის პორტალი, საპილოტე სერვისი) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | საბერძნეთი: ეროვნული სტამბა, მთავრობის ბიულეტენის ძიება (search.et.gr) |
| `in` | ინდოეთი: India Code (indiacode.gov.in) |
| `mu` | მავრიკი: უზენაესი სასამართლო (supremecourt.govmu.org) |
| `sg` | სინგაპური: სასამართლო გადაწყვეტილებები (elitigation.sg) |

ნებართვის გარეშე Fontes გატყობინებთ: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
