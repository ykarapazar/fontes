> Ovo je mašinski potpomognut prevod. Merodavna je verzija na engleskom.

# API ključevi

Skoro svaki izvor u programu Fontes radi bez ključa. Dvama je potreban besplatan ključ:

| Ključ | Šta otključava | Bez njega |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Francuska: Judilibre (sudske odluke) i Légifrance (propisi) | Francuska je isključena. `list_jurisdictions` je prikazuje kao neaktivnu. |
| `WLM_US_GOVINFO_KEY` | Sjedinjene Države: govinfo pretraga (odluke saveznih sudova, Statutes at Large, javni zakoni) | Fontes koristi zajednički `DEMO_KEY`: oko 10 pretraga dnevno po IP adresi. Za otvaranje poznate odluke i US Code ključ nije potreban. |

Ključevi su opcioni. Možete ih dodati kasnije.

## Dodavanje ključa

**Pomoću instalacionog programa.** Kada je Fontes podešen, instalacioni program nudi da doda
ključeve. Na Mac-u kliknite na **Dodaj ključeve**, ili na **Gotovo** da biste preskočili; na
Windows-u odgovorite na pitanje (pritisnite Enter da biste preskočili). Da biste kasnije dodali ili
promenili ključeve, pokrenite **Add or change keys**:

- Mac: ponovo otvorite aplikaciju Fontes Installer i izaberite **Dodaj ili promeni ključeve**.
- Windows: dvaput kliknite na `Add or change keys.cmd` u fascikli instalacionog programa.
  Program za instalaciju za Windows, kada bude dostupan, staviće ga i u meni Start > Fontes.

Unos je skriven. Za svaki ključ: nalepite ga, pritisnite Enter da zadržite postojeći, ili
ukucajte `-` da ga uklonite. Ključevi se upisuju u svaku aplikaciju koja već ima Fontes.

**Pomoću Claude Desktop proširenja (.mcpb).** Otvorite Claude > Settings > Extensions > Fontes i
popunite polja. Sva su opciona.

**Ručno.** Dodajte promenljive u blok `env` unosa `fontes` u MCP konfiguraciji svoje aplikacije:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Nakon svake izmene ponovo pokrenite aplikaciju.

## Francuska: PISTE (besplatno)

1. Napravite nalog na [piste.gouv.fr](https://piste.gouv.fr). To podrazumeva prihvatanje
   uslova PISTE (CGU).
2. Idite na API > **Consentement CGU API**. Prihvatite uslove za **JUDILIBRE** i
   **Légifrance** (production).
3. Napravite **production aplikaciju** (production application). `APP_SANDBOX` napravljen za
   vas ne može da pristupi production okruženju. Pod "Modifier l'application" označite
   **JUDILIBRE (production)** i **Légifrance (production)**, pa primenite.
4. Otvorite karticu **Authentification** aplikacije. Kopirajte `client_id` i `client_secret`.
5. Pokrenite **Add or change keys** i nalepite ih.

Uslovi, ukratko:

- Podaci: Licence Ouverte / Etalab 2.0. Ponovna upotreba, uključujući komercijalnu, dozvoljena je
  uz navođenje izvora.
- Ne objavljujte niti delite svoje akreditive. Obavestite PISTE ako procure.
- Légifrance API je beta usluga. Može biti obustavljena i ima kvote (po sekundi, minutu i danu).
- Tekstovi na Légifrance nisu autentična verzija. Autentičan je samo potpisani PDF Journal
  officiel.
- Judilibre: ne koristite imena sudija ili sudskih službenika da biste ocenjivali, upoređivali
  ili predviđali njihov rad (Code de l'organisation judiciaire, čl. L111-13; krivično delo).
- Judilibre: poštujte GDPR. Ne pokušavajte da ponovo identifikujete stranke.

Vaše kvote se nalaze na PISTE pod API Sélectionnées > Actions > Consulter les quotas.

## Sjedinjene Države: api.data.gov (besplatno)

1. Idite na [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (ključ se prikazuje na
   ekranu) ili [api.data.gov/signup](https://api.data.gov/signup/) (ključ vam se šalje imejlom).
2. Unesite svoje ime i imejl. Polje "how will you use it" je opciono.
3. Kopirajte ključ od 40 znakova.
4. Pokrenite **Add or change keys** i nalepite ga kao ključ za SAD.

Uslovi, ukratko:

- Sa sopstvenim ključem, govinfo dozvoljava do 36,000 zahteva na sat.
- Nismo pronašli uslove korišćenja specifične za API (api.data.gov/terms/ ne postoji).
  Neprovereno. Pogledajte [govinfo pravila](https://www.govinfo.gov/about/policies) i
  [data.gov politiku privatnosti](https://data.gov/privacy-policy/).
- Ključ zadržite za sebe.

## Gde se ključevi čuvaju

- **Instalacioni program ili ručno:** kao običan tekst u MCP konfiguracionoj datoteci svake
  aplikacije, u bloku `env` unosa `fontes`. Svako ko može da čita vaše korisničke datoteke može
  da pročita ključeve.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` ili `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Claude Desktop proširenje (.mcpb):** Claude čuva ova polja u svojim podešavanjima i štiti ih
  bezbednim skladištem vašeg sistema (Keychain na Mac-u, Credential Manager na Windows-u).

Pre svake izmene, instalacioni program čuva kopiju konfiguracione datoteke pored nje
(`<file>.fontes-backup-<time>`). Kopije napravljene nakon što ste dodali ključeve takođe sadrže
ključeve. Obrišite stare kopije koje vam nisu potrebne.

## Promena ili uklanjanje ključa

- Pokrenite **Add or change keys**. Nalepite novi ključ da biste zamenili stari, ili ukucajte
  `-` da biste ga uklonili.
- Ili ručno izmenite blok `env` i ponovo pokrenite aplikaciju.
- Deinstalacija programa Fontes uklanja ceo njegov unos, uključujući ključeve. Ne briše rezervne
  kopije.
- Ako je ključ procureo, zamenite ga i kod izvora: na PISTE napravite nove akreditive za svoju
  aplikaciju; za api.data.gov registrujte novi ključ.

## Poruke koje možete videti

| Poruka | Značenje |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Nema ključa za Francusku. Dodajte ga. |
| `Inactive: needs a free PISTE account. ...` (u `list_jurisdictions`) | Isto. |
| `PISTE refused the client credentials ...` | ID ili secret je pogrešan ili više ne važi. Ponovo kopirajte oba sa kartice Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Vaša aplikacija nije pretplaćena na taj API ili niste prihvatili njegove uslove. Pogledajte korake 2 i 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Nema ključa za SAD. Pretraga radi za nekoliko poziva dnevno. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Demo ključ je potrošen. Dodajte sopstveni ključ. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Ključ je pogrešan ili još nije potvrđen preko imejla. |

Prazna vrednost se smatra kao da ključa nema.

## Dozvole (WLM_PERMITTED)

Ovo nije API ključ i instalacioni program ga ne podešava. **Podesite ga samo ako tu dozvolu
lično imate.**

Neki izvori su podrazumevano isključeni jer njihovi uslovi ili robots.txt zabranjuju
automatizovanu upotrebu bez dozvole. Ako imate dozvolu izdavača, uključite izvor tako što ćete
njegov kod dodati u `WLM_PERMITTED`, razdvojeno zarezima, u bloku `env`:
`"WLM_PERMITTED": "in,de"`.

| Kod | Izvor |
|---|---|
| `az` | Azerbejdžan: e-qanun.az (Ministarstvo pravde) |
| `bh` | Bahrein: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Kolumbija: Función Pública, Gestor Normativo (prečišćeni propisi) |
| `de` | Nemačka: NeuRIS (savezni portal pravnih informacija, probna usluga) |
| `difc` | Sudovi Međunarodnog finansijskog centra u Dubaiju (difccourts.ae) |
| `gr` | Grčka: Nacionalna štamparija, pretraga Službenog glasnika (search.et.gr) |
| `in` | Indija: India Code (indiacode.gov.in) |
| `mu` | Mauricijus: Vrhovni sud (supremecourt.govmu.org) |
| `sg` | Singapur: sudske presude (elitigation.sg) |

Bez dozvole, Fontes kaže: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
