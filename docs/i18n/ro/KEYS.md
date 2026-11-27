> Aceasta este o traducere asistată automat. Versiunea în limba engleză este cea care prevalează.

# Chei API

Aproape toate sursele din Fontes funcționează fără cheie. Trei necesită o cheie gratuită:

| Cheie | Ce deblochează | Fără ea |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Franța: Judilibre (hotărâri judecătorești) și Légifrance (legislație) | Franța este dezactivată. `list_jurisdictions` o afișează ca inactivă. |
| `WLM_US_GOVINFO_KEY` | Statele Unite: căutarea govinfo (opinii ale instanțelor federale, Statutes at Large, legi publice) | Fontes folosește cheia comună `DEMO_KEY`: aproximativ 10 căutări pe zi pentru fiecare adresă IP. Deschiderea unei hotărâri cunoscute și US Code nu necesită cheie. |
| `WLM_US_COURTLISTENER_KEY` | Instanțele statale din SUA (`us-states`): hotărâri ale curților supreme și de apel din toate cele 50 de state și din DC, de la CourtListener | Jurisprudența instanțelor statale din SUA este dezactivată. `list_jurisdictions` o afișează ca inactivă. |

Cheile sunt opționale. Le puteți adăuga mai târziu.

## Adăugarea unei chei

**Cu programul de instalare.** După ce Fontes este configurat, programul de instalare se oferă să adauge
chei. Pe Mac, faceți clic pe **Adăugare chei** sau pe **Gata** pentru a sări peste acest pas; pe Windows,
răspundeți la întrebare (apăsați Enter pentru a sări peste ea). Pentru a adăuga sau
modifica cheile mai târziu, rulați **Adăugați sau modificați cheile**:

- Mac: deschideți din nou aplicația Fontes Installer și alegeți **Adăugați sau modificați cheile**.
- Windows: deschideți meniul Start, apoi alegeți **Fontes** → **Adăugați sau modificați cheile**.

Textul tastat este ascuns. Pentru fiecare cheie: lipiți-o, apăsați Enter pentru a păstra ce există deja sau
tastați `-` pentru a o elimina. Cheile ajung în fiecare aplicație care are deja Fontes.

**Cu extensia Claude Desktop (.mcpb).** Deschideți Claude > Settings > Extensions > Fontes și completați
câmpurile. Toate sunt opționale.

**Manual.** Adăugați variabilele în blocul `env` al intrării `fontes` din configurația MCP a aplicației:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Reporniți aplicația după orice modificare.

## Franța: PISTE (gratuit)

1. Creați un cont pe [piste.gouv.fr](https://piste.gouv.fr). Aceasta presupune acceptarea condițiilor PISTE (CGU).
2. Mergeți la API > **Consentement CGU API**. Acceptați condițiile pentru **JUDILIBRE** și **Légifrance** (producție).
3. Creați o **aplicație de producție**. `APP_SANDBOX`, creată pentru dumneavoastră, nu poate accesa mediul de producție.
   La „Modifier l'application”, bifați **JUDILIBRE (production)** și **Légifrance (production)**, apoi aplicați.
4. Deschideți fila **Authentification** a aplicației. Copiați `client_id` și `client_secret`.
5. Rulați **Adăugați sau modificați cheile** și lipiți-le.

Condițiile, pe scurt:

- Date: Licence Ouverte / Etalab 2.0. Reutilizarea, inclusiv cea comercială, este permisă cu menționarea sursei.
- Nu publicați și nu partajați datele de autentificare. Anunțați PISTE dacă acestea sunt divulgate.
- API-ul Légifrance este un serviciu beta. Poate fi suspendat și are cote (pe secundă, pe minut și pe zi).
- Textele Légifrance nu sunt versiunea autentică. Doar PDF-ul semnat al Journal officiel este.
- Judilibre: nu folosiți numele judecătorilor sau ale grefierilor pentru a le evalua, compara sau prezice
  activitatea (Code de l'organisation judiciaire art. L111-13; infracțiune).
- Judilibre: respectați GDPR. Nu încercați să reidentificați părțile.

Cotele dumneavoastră se află pe PISTE la API Sélectionnées > Actions > Consulter les quotas.

## Statele Unite: api.data.gov (gratuit)

1. Mergeți la [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (cheia este afișată pe ecran)
   sau la [api.data.gov/signup](https://api.data.gov/signup/) (cheia vă este trimisă prin e-mail).
2. Introduceți numele și adresa de e-mail. Câmpul „how will you use it” este opțional.
3. Copiați cheia de 40 de caractere.
4. Rulați **Adăugați sau modificați cheile** și lipiți-o drept cheie pentru SUA.

Condițiile, pe scurt:

- Cu propria cheie, govinfo permite până la 36.000 de cereri pe oră.
- Nu am găsit condiții de utilizare specifice API-ului (api.data.gov/terms/ nu există). Neverificat.
  Vedeți [politicile govinfo](https://www.govinfo.gov/about/policies) și
  [politica de confidențialitate data.gov](https://data.gov/privacy-policy/).
- Păstrați cheia doar pentru dumneavoastră.

## Instanțele statale din SUA: CourtListener (gratuit)

CourtListener este administrat de [Free Law Project](https://free.law), o organizație non-profit care adună hotărâri ale instanțelor din SUA din 2010 și le pune gratuit la dispoziția tuturor. Potrivit propriei evidențe, conține peste nouă milioane de hotărâri. Nu este o sursă oficială: instanțele își publică propriile hotărâri, iar CourtListener le adună de pe site-urile instanțelor și din culegeri de jurisprudență scanate. Fiecare răspuns Fontes provenit de acolo spune acest lucru. Fontes nu este afiliat cu Free Law Project.

1. Creați un cont gratuit pe [courtlistener.com](https://www.courtlistener.com/sign-in/).
2. Deschideți-vă profilul și copiați tokenul API.
3. Rulați **Adăugați sau modificați cheile** și lipiți-l drept cheie CourtListener.

Condițiile, pe scurt ([condițiile complete](https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies)):

- Tokenul este numai al dumneavoastră: nu îl partajați, nu îl grupați cu altele și nu îl revindeți, și nu folosiți mai multe conturi.
- Sunteți responsabil pentru ce face o aplicație AI cu tokenul dumneavoastră.
- Nu prezentați analiza făcută de o AI asupra datelor lor ca fiind produsă, aprobată sau verificată de Free Law Project.
- Un cont gratuit permite 5 cereri pe minut, 50 pe oră și 125 pe zi. O căutare este o cerere; deschiderea unei hotărâri înseamnă două. Un abonament de membru Free Law Project ridică limitele.
- CourtListener nu garantează acuratețea. Verificați o hotărâre față de exemplarul instanței înainte de a vă baza pe ea.

## Unde sunt stocate cheile

- **Prin programul de instalare sau manual:** ca text simplu în fișierul de configurare MCP al fiecărei
  aplicații, în blocul `env` al intrării `fontes`. Oricine vă poate citi fișierele de utilizator poate citi
  cheile.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` sau `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Extensia Claude Desktop (.mcpb):** Claude păstrează aceste câmpuri în setările sale și le protejează cu
  stocarea securizată a sistemului (Keychain pe Mac, Credential Manager pe Windows).

Înainte de fiecare modificare, programul de instalare salvează o copie a fișierului de configurare lângă el
(`<file>.fontes-backup-<time>`). Copiile făcute după ce ați adăugat chei conțin și cheile. Ștergeți copiile
vechi de care nu aveți nevoie.

## Modificarea sau eliminarea unei chei

- Rulați **Adăugați sau modificați cheile**. Lipiți o cheie nouă pentru a o înlocui sau tastați `-` pentru
  a o elimina.
- Sau editați manual blocul `env` și reporniți aplicația.
- Dezinstalarea Fontes elimină întreaga sa intrare, inclusiv cheile. Nu șterge copiile de rezervă.
- Dacă o cheie a fost divulgată, înlocuiți-o și la sursă: pe PISTE, creați date de autentificare noi pentru
  aplicație; pentru api.data.gov, înregistrați-vă pentru o cheie nouă.

## Mesaje pe care le puteți vedea

| Mesaj | Semnificație |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Nu există cheie pentru Franța. Adăugați una. |
| `Inactive: needs a free PISTE account. ...` (în `list_jurisdictions`) | La fel. |
| `PISTE refused the client credentials ...` | ID-ul sau secretul este greșit ori nu mai este valabil. Copiați-le din nou pe amândouă din fila Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Aplicația nu este abonată la acel API sau nu ați acceptat condițiile acestuia. Vedeți pașii 2 și 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Nu există cheie pentru SUA. Căutarea funcționează pentru câteva apeluri pe zi. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Cheia demo a fost epuizată. Adăugați propria cheie. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Cheia este greșită sau nu a fost încă confirmată din e-mail. |

O valoare goală este considerată lipsă de cheie.

## Permisiuni (WLM_PERMITTED)

Aceasta nu este o cheie API, iar programul de instalare nu o setează. **Setați-o doar dacă dețineți
dumneavoastră înșivă acea permisiune.**

Unele surse sunt dezactivate implicit deoarece condițiile lor sau robots.txt interzic utilizarea automatizată
fără permisiune. Dacă aveți permisiunea editorului, activați o sursă adăugând codul ei în `WLM_PERMITTED`,
separat prin virgule, în blocul `env`: `"WLM_PERMITTED": "in,de"`.

| Cod | Sursă |
|---|---|
| `az` | Azerbaidjan: e-qanun.az (Ministerul Justiției) |
| `bh` | Bahrain: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Columbia: Función Pública, Gestor Normativo (legislație consolidată) |
| `de` | Germania: NeuRIS (portalul federal de informare juridică, serviciu de probă) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Grecia: Imprimeria Națională, căutare în Monitorul Oficial (search.et.gr) |
| `in` | India: India Code (indiacode.gov.in) |
| `mu` | Mauritius: Curtea Supremă (supremecourt.govmu.org) |
| `sg` | Singapore: hotărâri judecătorești (elitigation.sg) |

Fără permisiune, Fontes afișează: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
