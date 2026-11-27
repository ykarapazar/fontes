> Ky është një përkthim i ndihmuar nga makina. Versioni në anglisht është ai që vlen.

# Çelësat API

Pothuajse çdo burim në Fontes funksionon pa çelës. Tre prej tyre kërkojnë një çelës falas:

| Çelësi | Çfarë hap | Pa të |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Franca: Judilibre (vendime gjyqësore) dhe Légifrance (legjislacion) | Franca është joaktive. `list_jurisdictions` e tregon si joaktive. |
| `WLM_US_GOVINFO_KEY` | Shtetet e Bashkuara: kërkimi govinfo (opinionet e gjykatave federale, Statutes at Large, ligjet publike) | Fontes përdor `DEMO_KEY` e përbashkët: rreth 10 kërkime në ditë për adresë IP. Hapja e një vendimi të njohur dhe US Code nuk kërkojnë çelës. |
| `WLM_US_COURTLISTENER_KEY` | Gjykatat shtetërore të SHBA-së (`us-states`): opinionet e gjykatave supreme dhe të apelit të të 50 shteteve dhe të DC-së, nga CourtListener | Praktika gjyqësore e shteteve të SHBA-së është joaktive. `list_jurisdictions` e shfaq si joaktive. |

Çelësat janë opsionalë. Mund t'i shtoni më vonë.

## Shtimi i një çelësi

**Me instaluesin.** Pasi Fontes të jetë konfiguruar, instaluesi ofron të shtojë çelësa. Në Mac,
klikoni **Shto çelësa**, ose **U krye** për ta anashkaluar; në Windows, përgjigjuni pyetjes (shtypni
Enter për ta anashkaluar). Për të shtuar ose ndryshuar çelësat më vonë, ekzekutoni
**Add or change keys**:

- Mac: hapni sërish aplikacionin Fontes Installer dhe zgjidhni **Shto ose ndrysho çelësat**.
- Windows: hapni menunë Start, pastaj **Fontes** → **Shto ose ndrysho çelësat**.

Shkrimi është i fshehur. Për çdo çelës: ngjiteni, shtypni Enter për të mbajtur atë që është, ose
shkruani `-` për ta hequr. Çelësat shkojnë në çdo aplikacion që e ka tashmë Fontes.

**Me zgjerimin e Claude Desktop (.mcpb).** Hapni Claude > Settings > Extensions > Fontes dhe
plotësoni fushat. Të gjitha janë opsionale.

**Me dorë.** Shtoni variablat në bllokun `env` të hyrjes `fontes` në konfigurimin MCP të
aplikacionit tuaj:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Rinisni aplikacionin pas çdo ndryshimi.

## Franca: PISTE (falas)

1. Krijoni një llogari në [piste.gouv.fr](https://piste.gouv.fr). Kjo do të thotë të pranoni
   kushtet e PISTE (CGU).
2. Shkoni te API > **Consentement CGU API**. Pranoni kushtet për **JUDILIBRE** dhe
   **Légifrance** (production).
3. Krijoni një **aplikacion production**. `APP_SANDBOX` që krijohet për ju nuk mund ta arrijë
   production. Te "Modifier l'application", shënoni **JUDILIBRE (production)** dhe
   **Légifrance (production)**, pastaj zbatojeni.
4. Hapni skedën **Authentification** të aplikacionit. Kopjoni `client_id` dhe `client_secret`.
5. Ekzekutoni **Add or change keys** dhe ngjitini.

Kushtet, shkurtimisht:

- Të dhënat: Licence Ouverte / Etalab 2.0. Ripërdorimi, përfshirë ripërdorimin tregtar, lejohet me
  përmendjen e burimit.
- Mos i publikoni dhe mos i ndani kredencialet tuaja. Njoftoni PISTE nëse rrjedhin.
- API-ja e Légifrance është një shërbim beta. Mund të pezullohet, dhe ka kuota (për sekondë, minutë
  dhe ditë).
- Tekstet e Légifrance nuk janë versioni autentik. Autentik është vetëm PDF-ja e nënshkruar e
  Journal officiel.
- Judilibre: mos përdorni emrat e gjyqtarëve ose të sekretarëve gjyqësorë për të vlerësuar,
  krahasuar ose parashikuar punën e tyre (Code de l'organisation judiciaire neni L111-13; vepër
  penale).
- Judilibre: zbatoni GDPR-në. Mos u përpiqni t'i riidentifikoni palët.

Kuotat tuaja janë në PISTE te API Sélectionnées > Actions > Consulter les quotas.

## Shtetet e Bashkuara: api.data.gov (falas)

1. Shkoni te [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (çelësi shfaqet në
   ekran) ose te [api.data.gov/signup](https://api.data.gov/signup/) (çelësi ju dërgohet me
   email).
2. Shkruani emrin dhe email-in tuaj. Fusha "how will you use it" është opsionale.
3. Kopjoni çelësin me 40 karaktere.
4. Ekzekutoni **Add or change keys** dhe ngjiteni si çelësin e SHBA-së.

Kushtet, shkurtimisht:

- Me çelësin tuaj, govinfo lejon deri në 36,000 kërkesa në orë.
- Nuk gjetëm kushte shërbimi të posaçme për API-në (api.data.gov/terms/ nuk ekziston). E
  paverifikuar. Shihni [politikat e govinfo](https://www.govinfo.gov/about/policies) dhe
  [politikën e privatësisë së data.gov](https://data.gov/privacy-policy/).
- Mbajeni çelësin për vete.

## Gjykatat shtetërore të SHBA-së: CourtListener (falas)

CourtListener drejtohet nga [Free Law Project](https://free.law), një organizatë jofitimprurëse që mbledh opinionet e gjykatave amerikane që nga viti 2010 dhe i vë falas në dispozicion të të gjithëve. Sipas të dhënave të veta, ajo përmban mbi nëntë milionë vendime. Nuk është burim zyrtar: gjykatat publikojnë vetë opinionet e tyre, dhe CourtListener i mbledh nga faqet e internetit të gjykatave dhe nga përmbledhjet e skanuara të vendimeve. Çdo përgjigje e Fontes nga ky burim e thotë këtë. Fontes nuk është i lidhur me Free Law Project.

1. Krijoni një llogari falas në [courtlistener.com](https://www.courtlistener.com/sign-in/).
2. Hapni profilin tuaj dhe kopjoni token-in tuaj API.
3. Ekzekutoni **Add or change keys** dhe ngjiteni si çelësin e CourtListener.

Kushtet, shkurtimisht ([kushtet e plota](https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies)):

- Token-i është vetëm i juaji: mos e ndani, mos e bashkoni dhe mos e rishitni, dhe mos përdorni disa llogari.
- Ju mbani përgjegjësi për atë që një aplikacion IA bën me token-in tuaj.
- Mos e paraqitni analizën e të dhënave të tyre nga një IA si të prodhuar, miratuar ose kontrolluar nga Free Law Project.
- Një llogari falas lejon 5 kërkesa në minutë, 50 në orë dhe 125 në ditë. Një kërkim është një kërkesë; hapja e një vendimi janë dy. Anëtarësimi në Free Law Project i rrit kufijtë.
- CourtListener nuk garanton saktësinë. Kontrolloni një opinion me kopjen e gjykatës përpara se të mbështeteni te ai.

## Ku ruhen çelësat

- **Instaluesi ose me dorë:** si tekst i thjeshtë në skedarin e konfigurimit MCP të çdo
  aplikacioni, në bllokun `env` të hyrjes `fontes`. Kushdo që mund të lexojë skedarët tuaj të
  përdoruesit mund t'i lexojë çelësat.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` ose `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Zgjerimi i Claude Desktop (.mcpb):** Claude i mban këto fusha në cilësimet e veta dhe i mbron
  me ruajtjen e sigurt të sistemit tuaj (Keychain në Mac, Credential Manager në Windows).

Para çdo ndryshimi, instaluesi ruan një kopje të skedarit të konfigurimit pranë tij
(`<file>.fontes-backup-<time>`). Kopjet e bëra pasi keni shtuar çelësa i përmbajnë edhe çelësat.
Fshini kopjet e vjetra që nuk ju duhen.

## Ndryshimi ose heqja e një çelësi

- Ekzekutoni **Add or change keys**. Ngjitni një çelës të ri për ta zëvendësuar, ose shkruani `-`
  për ta hequr.
- Ose redaktoni bllokun `env` me dorë dhe rinisni aplikacionin.
- Çinstalimi i Fontes heq të gjithë hyrjen e tij, bashkë me çelësat. Nuk i fshin kopjet rezervë.
- Nëse një çelës ka rrjedhur, zëvendësojeni edhe te burimi: në PISTE, krijoni kredenciale të reja
  për aplikacionin tuaj; për api.data.gov, regjistrohuni për një çelës të ri.

## Mesazhet që mund të shihni

| Mesazhi | Kuptimi |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Nuk ka çelës për Francën. Shtoni një. |
| `Inactive: needs a free PISTE account. ...` (në `list_jurisdictions`) | E njëjta gjë. |
| `PISTE refused the client credentials ...` | ID-ja ose secret-i është i gabuar ose nuk është më i vlefshëm. Kopjojini sërish të dyja nga skeda Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Aplikacioni juaj nuk është i abonuar në atë API, ose nuk i keni pranuar kushtet e saj. Shihni hapat 2 dhe 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Nuk ka çelës për SHBA-në. Kërkimi funksionon për disa thirrje në ditë. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Çelësi demo është shteruar. Shtoni çelësin tuaj. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Çelësi është i gabuar, ose ende nuk është konfirmuar nga email-i. |

Një vlerë bosh llogaritet si mungesë çelësi.

## Lejet (WLM_PERMITTED)

Ky nuk është çelës API, dhe instaluesi nuk e vendos. **Vendoseni vetëm nëse e keni vetë atë
leje.**

Disa burime janë joaktive si parazgjedhje, sepse kushtet ose robots.txt e tyre ndalojnë përdorimin
e automatizuar pa leje. Nëse keni leje nga botuesi, aktivizoni një burim duke shtuar kodin e tij në
`WLM_PERMITTED`, të ndarë me presje, në bllokun `env`: `"WLM_PERMITTED": "in,de"`.

| Kodi | Burimi |
|---|---|
| `az` | Azerbajxhani: e-qanun.az (Ministria e Drejtësisë) |
| `bh` | Bahreini: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Kolumbia: Función Pública, Gestor Normativo (legjislacion i konsoliduar) |
| `de` | Gjermania: NeuRIS (portali federal i informacionit juridik, shërbim provë) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Greqia: Shtypshkronja Kombëtare, kërkimi në Fletoren Zyrtare (search.et.gr) |
| `mu` | Mauritiusi: Supreme Court (supremecourt.govmu.org) |
| `sg` | Singapori: vendimet gjyqësore (elitigation.sg) |

Pa leje, Fontes thotë: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
