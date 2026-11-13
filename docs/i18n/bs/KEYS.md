> Ovo je mašinski potpomognut prijevod. Mjerodavna je verzija na engleskom.

# API ključevi

Gotovo svaki izvor u alatu Fontes radi bez ključa. Dva izvora zahtijevaju besplatan ključ:

| Ključ | Otključava | Bez njega |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Francuska: Judilibre (sudske odluke) i Légifrance (propisi) | Francuska je isključena. `list_jurisdictions` je prikazuje kao neaktivnu. |
| `WLM_US_GOVINFO_KEY` | Sjedinjene Američke Države: pretraga govinfo (mišljenja saveznih sudova, Statutes at Large, public laws) | Fontes koristi zajednički `DEMO_KEY`: oko 10 pretraga dnevno po IP adresi. Za otvaranje poznate odluke i za US Code ključ nije potreban. |

Ključevi su opcionalni. Možete ih dodati i kasnije.

## Dodavanje ključa

**Pomoću instalacijskog programa.** Tokom instalacije, instalacijski program pita želite li dodati
ključeve. Odaberite **Ne sada** (ili pritisnite Enter) da preskočite. Da kasnije dodate ili
promijenite ključeve, pokrenite **Add or change keys**:

- Mac: ponovo otvorite aplikaciju Fontes Installer i odaberite **Dodaj ili promijeni ključeve**
  ili dvaput kliknite na `Add or change keys.command` u mapi instalacijskog programa.
- Windows: dvaput kliknite na `Add or change keys.cmd` u mapi instalacijskog programa. Program za
  instalaciju na Windowsu, kada bude dostupan, stavit će ga i u Start menu > Fontes.

Unos se ne prikazuje. Za svaki ključ: zalijepite ga, pritisnite Enter da zadržite postojeći ili
ukucajte `-` da ga uklonite. Ključevi se upisuju u svaku aplikaciju koja već ima Fontes.

**Pomoću proširenja za Claude Desktop (.mcpb).** Otvorite Claude > Settings > Extensions > Fontes
i popunite polja. Sva su opcionalna.

**Ručno.** Dodajte varijable u blok `env` unosa `fontes` u MCP konfiguraciji svoje aplikacije:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Nakon svake izmjene ponovo pokrenite aplikaciju.

## Francuska: PISTE (besplatno)

1. Napravite račun na [piste.gouv.fr](https://piste.gouv.fr). To znači prihvatanje uslova PISTE (CGU).
2. Idite na API > **Consentement CGU API**. Prihvatite uslove za **JUDILIBRE** i **Légifrance** (production).
3. Napravite **production application**. `APP_SANDBOX` koji je napravljen za vas ne može pristupiti produkciji.
   Pod "Modifier l'application" označite **JUDILIBRE (production)** i **Légifrance (production)**, zatim primijenite.
4. Otvorite karticu **Authentification** aplikacije. Kopirajte `client_id` i `client_secret`.
5. Pokrenite **Add or change keys** i zalijepite ih.

Uslovi, ukratko:

- Podaci: Licence Ouverte / Etalab 2.0. Ponovna upotreba, uključujući komercijalnu, dozvoljena je uz navođenje izvora.
- Ne objavljujte i ne dijelite svoje pristupne podatke. Obavijestite PISTE ako procure.
- API Légifrance je beta usluga. Može biti obustavljen i ima kvote (po sekundi, minuti i danu).
- Tekstovi na Légifrance nisu autentična verzija. Autentičan je samo potpisani PDF Journal officiel.
- Judilibre: ne koristite imena sudija ili službenika suda za ocjenjivanje, poređenje ili
  predviđanje njihovog rada (Code de l'organisation judiciaire čl. L111-13; krivično djelo).
- Judilibre: poštujte GDPR. Ne pokušavajte ponovo identifikovati stranke.

Svoje kvote vidite na PISTE pod API Sélectionnées > Actions > Consulter les quotas.

## Sjedinjene Američke Države: api.data.gov (besplatno)

1. Idite na [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (ključ se prikazuje na ekranu)
   ili [api.data.gov/signup](https://api.data.gov/signup/) (ključ vam se šalje e-poštom).
2. Unesite svoje ime i e-mail adresu. Polje "how will you use it" je opcionalno.
3. Kopirajte ključ od 40 znakova.
4. Pokrenite **Add or change keys** i zalijepite ga kao ključ za SAD.

Uslovi, ukratko:

- S vlastitim ključem govinfo dopušta do 36.000 zahtjeva na sat.
- Nismo pronašli uslove korištenja specifične za API (api.data.gov/terms/ ne postoji). Neprovjereno.
  Pogledajte [pravila za govinfo](https://www.govinfo.gov/about/policies) i
  [politiku privatnosti data.gov](https://data.gov/privacy-policy/).
- Ključ zadržite za sebe.

## Gdje se ključevi čuvaju

- **Instalacijski program ili ručno:** kao običan tekst u MCP konfiguracijskoj datoteci svake
  aplikacije, u bloku `env` unosa `fontes`. Svako ko može čitati vaše korisničke datoteke može
  pročitati i ključeve.
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
- **Proširenje za Claude Desktop (.mcpb):** Claude čuva ova polja u svojim postavkama i štiti ih
  sigurnom pohranom vašeg sistema (Keychain na Macu, Credential Manager na Windowsu).

Prije svake izmjene, instalacijski program sačuva kopiju konfiguracijske datoteke pored nje
(`<file>.fontes-backup-<time>`). Kopije napravljene nakon što ste dodali ključeve također sadrže
ključeve. Obrišite stare kopije koje vam ne trebaju.

## Promjena ili uklanjanje ključa

- Pokrenite **Add or change keys**. Zalijepite novi ključ da zamijenite postojeći ili ukucajte `-`
  da ga uklonite.
- Ili ručno uredite blok `env` i ponovo pokrenite aplikaciju.
- Deinstalacija programa Fontes uklanja cijeli njegov unos, zajedno s ključevima. Ne briše
  rezervne kopije.
- Ako je ključ procurio, zamijenite ga i kod izvora: na PISTE napravite nove pristupne podatke za
  svoju aplikaciju; za api.data.gov se prijavite za novi ključ.

## Poruke koje možete vidjeti

| Poruka | Značenje |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Nema ključa za Francusku. Dodajte ga. |
| `Inactive: needs a free PISTE account. ...` (u `list_jurisdictions`) | Isto. |
| `PISTE refused the client credentials ...` | ID ili secret je pogrešan ili više ne važi. Ponovo kopirajte oba s kartice Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Vaša aplikacija nije pretplaćena na taj API ili niste prihvatili njegove uslove. Pogledajte korake 2 i 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Nema ključa za SAD. Pretraga radi za nekoliko poziva dnevno. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Demo ključ je potrošen. Dodajte vlastiti ključ. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Ključ je pogrešan ili još nije potvrđen putem e-pošte. |

Prazna vrijednost se računa kao da ključa nema.

## Dozvole (WLM_PERMITTED)

Ovo nije API ključ i instalacijski program ga ne postavlja. **Postavite ga samo ako tu dozvolu
imate vi lično.**

Neki izvori su zadano isključeni jer njihovi uslovi ili robots.txt zabranjuju automatizovanu
upotrebu bez dozvole. Ako imate dozvolu izdavača, uključite izvor tako što ćete njegov kod dodati
u `WLM_PERMITTED`, odvojeno zarezima, u bloku `env`: `"WLM_PERMITTED": "in,de"`.

| Kod | Izvor |
|---|---|
| `az` | Azerbejdžan: e-qanun.az (Ministarstvo pravde) |
| `bh` | Bahrein: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Kolumbija: Función Pública, Gestor Normativo (prečišćeni propisi) |
| `de` | Njemačka: NeuRIS (savezni portal pravnih informacija, probna usluga) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Grčka: National Printing Office, pretraga Government Gazette (search.et.gr) |
| `in` | Indija: India Code (indiacode.gov.in) |
| `mu` | Mauricijus: Supreme Court (supremecourt.govmu.org) |
| `sg` | Singapur: sudske presude (elitigation.sg) |

Bez dozvole Fontes kaže: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
