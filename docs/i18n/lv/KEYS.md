> Šis ir tulkojums, kas sagatavots ar mašīntulkošanas palīdzību. Noteicošā ir angļu valodas versija.

# API atslēgas

Gandrīz visi Fontes avoti darbojas bez atslēgas. Trim vajadzīga bezmaksas atslēga:

| Atslēga | Atver | Bez tās |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Francija: Judilibre (tiesu nolēmumi) un Légifrance (tiesību akti) | Francija ir izslēgta. `list_jurisdictions` to rāda kā neaktīvu. |
| `WLM_US_GOVINFO_KEY` | Amerikas Savienotās Valstis: govinfo meklēšana (federālo tiesu nolēmumi, Statutes at Large, public laws) | Fontes izmanto koplietoto `DEMO_KEY`: aptuveni 10 meklējumi dienā no vienas IP adreses. Zināma nolēmuma atvēršanai un US Code atslēga nav vajadzīga. |
| `WLM_US_COURTLISTENER_KEY` | ASV štatu tiesas (`us-states`): visu 50 štatu un Kolumbijas apgabala augstāko un apelāciju tiesu spriedumi no CourtListener | ASV štatu tiesu prakse ir izslēgta. `list_jurisdictions` to rāda kā neaktīvu. |

Atslēgas nav obligātas. Tās var pievienot vēlāk.

## Atslēgas pievienošana

**Ar instalētāju.** Kad Fontes ir iestatīts, instalētājs piedāvā pievienot atslēgas. Mac datorā
noklikšķiniet uz **Pievienot atslēgas** vai, lai izlaistu, uz **Gatavs**; Windows datorā atbildiet uz
jautājumu (lai izlaistu, nospiediet Enter). Lai pievienotu vai mainītu atslēgas
vēlāk, palaidiet **Add or change keys**:

- Mac: vēlreiz atveriet lietotni Fontes Installer un izvēlieties **Pievienot vai mainīt atslēgas**.
- Windows: atveriet izvēlni Start, pēc tam **Fontes** → **Pievienot vai mainīt atslēgas**.

Ievadītais teksts netiek rādīts. Katrai atslēgai: ielīmējiet to, nospiediet Enter, lai saglabātu
esošo, vai ierakstiet `-`, lai to noņemtu. Atslēgas tiek ierakstītas katrā lietotnē, kurā jau ir
Fontes.

**Ar Claude Desktop paplašinājumu (.mcpb).** Atveriet Claude > Settings > Extensions > Fontes un
aizpildiet laukus. Neviens no tiem nav obligāts.

**Manuāli.** Pievienojiet mainīgos `fontes` ieraksta blokam `env` savas lietotnes MCP
konfigurācijā:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Pēc katras izmaiņas restartējiet lietotni.

## Francija: PISTE (bezmaksas)

1. Izveidojiet kontu vietnē [piste.gouv.fr](https://piste.gouv.fr). Tas nozīmē PISTE noteikumu (CGU) pieņemšanu.
2. Atveriet API > **Consentement CGU API**. Pieņemiet noteikumus **JUDILIBRE** un **Légifrance** (production).
3. Izveidojiet **production application**. Jums izveidotā `APP_SANDBOX` nevar piekļūt production vidē.
   Sadaļā “Modifier l'application” atzīmējiet **JUDILIBRE (production)** un **Légifrance (production)**, pēc tam apstipriniet.
4. Atveriet lietotnes cilni **Authentification**. Nokopējiet `client_id` un `client_secret`.
5. Palaidiet **Add or change keys** un ielīmējiet tos.

Noteikumi īsumā:

- Dati: Licence Ouverte / Etalab 2.0. Atkalizmantošana, arī komerciāla, ir atļauta, norādot avotu.
- Nepublicējiet un nekopīgojiet savus piekļuves datus. Ja tie noplūst, informējiet PISTE.
- Légifrance API ir beta pakalpojums. Tā darbību var apturēt, un tam ir kvotas (sekundē, minūtē un dienā).
- Légifrance teksti nav autentiskā versija. Autentisks ir tikai parakstītais Journal officiel PDF.
- Judilibre: neizmantojiet tiesnešu vai tiesas darbinieku vārdus, lai vērtētu, salīdzinātu vai
  prognozētu viņu darbu (Code de l'organisation judiciaire L111-13. pants; noziedzīgs nodarījums).
- Judilibre: ievērojiet VDAR. Nemēģiniet atkārtoti identificēt puses.

Jūsu kvotas ir redzamas PISTE sadaļā API Sélectionnées > Actions > Consulter les quotas.

## Amerikas Savienotās Valstis: api.data.gov (bezmaksas)

1. Atveriet [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (atslēga tiek parādīta ekrānā)
   vai [api.data.gov/signup](https://api.data.gov/signup/) (atslēga tiek nosūtīta e-pastā).
2. Ievadiet savu vārdu un e-pasta adresi. Lauks “how will you use it” nav obligāts.
3. Nokopējiet 40 rakstzīmju atslēgu.
4. Palaidiet **Add or change keys** un ielīmējiet to kā ASV atslēgu.

Noteikumi īsumā:

- Ar savu atslēgu govinfo atļauj līdz 36,000 pieprasījumiem stundā.
- Mēs neatradām API specifiskus pakalpojumu noteikumus (api.data.gov/terms/ neeksistē). Nav
  pārbaudīts. Skatiet [govinfo politikas](https://www.govinfo.gov/about/policies) un
  [data.gov privātuma politiku](https://data.gov/privacy-policy/).
- Paturiet atslēgu pie sevis.

## ASV štatu tiesas: CourtListener (bezmaksas)

CourtListener uztur [Free Law Project](https://free.law) – bezpeļņas organizācija, kas kopš 2010. gada vāc ASV tiesu spriedumus un dara tos brīvi pieejamus visiem. Pēc tās pašas datiem tajā ir vairāk nekā deviņi miljoni nolēmumu. Tas nav oficiāls avots: tiesas savus spriedumus publicē pašas, un CourtListener tos savāc no tiesu vietnēm un skenētiem likumu pārskatiem. Katra Fontes atbilde no tā to norāda. Fontes nav saistīts ar Free Law Project.

1. Izveidojiet bezmaksas kontu vietnē [courtlistener.com](https://www.courtlistener.com/sign-in/).
2. Atveriet savu profilu un nokopējiet savu API token.
3. Palaidiet **Add or change keys** un ielīmējiet to kā CourtListener atslēgu.

Noteikumi īsumā ([pilnie noteikumi](https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies)):

- Token ir tikai jūsu: nedaliet to ar citiem, neapvienojiet un nepārdodiet tālāk, un neizmantojiet vairākus kontus.
- Jūs atbildat par to, ko mākslīgā intelekta lietotne dara ar jūsu token.
- Nepasniedziet mākslīgā intelekta veiktu viņu datu analīzi kā tādu, ko radījis, atbalstījis vai pārbaudījis Free Law Project.
- Bezmaksas konts ļauj 5 pieprasījumus minūtē, 50 stundā un 125 dienā. Meklēšana ir viens pieprasījums; nolēmuma atvēršana ir divi. Free Law Project dalība šos ierobežojumus palielina.
- CourtListener negarantē precizitāti. Pirms uzticaties spriedumam, salīdziniet to ar tiesas eksemplāru.

## Kur tiek glabātas atslēgas

- **Instalētājs vai manuāli:** kā vienkāršs teksts katras lietotnes MCP konfigurācijas failā,
  `fontes` ieraksta blokā `env`. Ikviens, kas var lasīt jūsu lietotāja failus, var izlasīt
  atslēgas.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` vai `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Claude Desktop paplašinājums (.mcpb):** Claude glabā šos laukus savos iestatījumos un
  aizsargā tos ar jūsu sistēmas drošo krātuvi (Keychain Mac datorā, Credential Manager
  Windows).

Pirms katras izmaiņas instalētājs blakus saglabā konfigurācijas faila kopiju
(`<file>.fontes-backup-<time>`). Kopijās, kas izveidotas pēc atslēgu pievienošanas, ir arī
atslēgas. Izdzēsiet vecās kopijas, kas jums nav vajadzīgas.

## Atslēgas maiņa vai noņemšana

- Palaidiet **Add or change keys**. Ielīmējiet jaunu atslēgu, lai to aizstātu, vai ierakstiet
  `-`, lai to noņemtu.
- Vai rediģējiet bloku `env` manuāli un restartējiet lietotni.
- Fontes atinstalēšana noņem visu tā ierakstu, ieskaitot atslēgas. Rezerves kopijas netiek
  dzēstas.
- Ja atslēga ir noplūdusi, aizstājiet to arī avotā: PISTE izveidojiet jaunus piekļuves datus
  savai lietotnei; api.data.gov reģistrējieties jaunai atslēgai.

## Ziņojumi, kurus varat redzēt

| Ziņojums | Nozīme |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Nav Francijas atslēgas. Pievienojiet to. |
| `Inactive: needs a free PISTE account. ...` (sadaļā `list_jurisdictions`) | Tas pats. |
| `PISTE refused the client credentials ...` | ID vai noslēpums ir nepareizs vai vairs nav derīgs. Vēlreiz nokopējiet abus no cilnes Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Jūsu lietotne nav abonējusi šo API vai neesat pieņēmis tā noteikumus. Skatiet 2. un 3. darbību. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Nav ASV atslēgas. Meklēšana darbojas dažiem izsaukumiem dienā. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Demonstrācijas atslēga ir izlietota. Pievienojiet savu atslēgu. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Atslēga ir nepareiza vai vēl nav apstiprināta no e-pasta. |

Tukša vērtība tiek uzskatīta par atslēgas neesamību.

## Atļaujas (WLM_PERMITTED)

Šī nav API atslēga, un instalētājs to neiestata. **Iestatiet to tikai tad, ja šī atļauja ir
jums pašam.**

Daži avoti pēc noklusējuma ir izslēgti, jo to noteikumi vai robots.txt aizliedz automatizētu
izmantošanu bez atļaujas. Ja jums ir izdevēja atļauja, ieslēdziet avotu, pievienojot tā kodu
mainīgajam `WLM_PERMITTED`, atdalot ar komatiem, blokā `env`: `"WLM_PERMITTED": "in,de"`.

| Kods | Avots |
|---|---|
| `az` | Azerbaidžāna: e-qanun.az (Tieslietu ministrija) |
| `bh` | Bahreina: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Kolumbija: Función Pública, Gestor Normativo (konsolidētie tiesību akti) |
| `de` | Vācija: NeuRIS (federālais tiesiskās informācijas portāls, izmēģinājuma pakalpojums) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Grieķija: National Printing Office, Government Gazette meklēšana (search.et.gr) |
| `in` | Indija: India Code (indiacode.gov.in) |
| `mu` | Maurīcija: Supreme Court (supremecourt.govmu.org) |
| `sg` | Singapūra: tiesu spriedumi (elitigation.sg) |

Bez atļaujas Fontes saka: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
