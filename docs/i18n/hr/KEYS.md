> Ovo je strojno potpomognut prijevod. Mjerodavna je engleska verzija.

# API ključevi

Gotovo svaki izvor u programu Fontes radi bez ključa. Dva izvora zahtijevaju besplatan ključ:

| Ključ | Otključava | Bez njega |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Francuska: Judilibre (sudske odluke) i Légifrance (propisi) | Francuska je isključena. `list_jurisdictions` je prikazuje kao neaktivnu. |
| `WLM_US_GOVINFO_KEY` | Sjedinjene Američke Države: pretraživanje govinfo (mišljenja saveznih sudova, Statutes at Large, public laws) | Fontes upotrebljava zajednički `DEMO_KEY`: oko 10 pretraživanja dnevno po IP adresi. Za otvaranje poznate odluke i za US Code ključ nije potreban. |

Ključevi nisu obvezni. Možete ih dodati i kasnije.

## Dodavanje ključa

**Pomoću instalacijskog programa.** Tijekom instalacije instalacijski program pita želite li
dodati ključeve. Odaberite **Ne sada** (ili pritisnite Enter) da biste preskočili. Da biste
ključeve dodali ili promijenili kasnije, pokrenite **Add or change keys**:

- Mac: ponovno otvorite aplikaciju Fontes Installer i odaberite **Dodaj ili promijeni ključeve**
  ili dvaput kliknite na `Add or change keys.command` u mapi instalacijskog programa.
- Windows: dvaput kliknite na `Add or change keys.cmd` u mapi instalacijskog programa.
  Instalacijski program za Windows, kada bude dostupan, stavit će ga i u Start menu > Fontes.

Unos se ne prikazuje. Za svaki ključ: zalijepite ga, pritisnite Enter da biste zadržali
postojeći ili upišite `-` da biste ga uklonili. Ključevi se upisuju u svaku aplikaciju koja već
ima Fontes.

**Pomoću proširenja za Claude Desktop (.mcpb).** Otvorite Claude > Settings > Extensions > Fontes
i ispunite polja. Nijedno nije obvezno.

**Ručno.** Dodajte varijable u blok `env` unosa `fontes` u MCP konfiguraciji svoje aplikacije:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Nakon svake promjene ponovno pokrenite aplikaciju.

## Francuska: PISTE (besplatno)

1. Otvorite račun na [piste.gouv.fr](https://piste.gouv.fr). To znači prihvaćanje uvjeta PISTE (CGU).
2. Idite na API > **Consentement CGU API**. Prihvatite uvjete za **JUDILIBRE** i **Légifrance** (production).
3. Izradite **production application**. `APP_SANDBOX` koji je izrađen za vas ne može pristupiti produkciji.
   Pod "Modifier l'application" označite **JUDILIBRE (production)** i **Légifrance (production)**, zatim primijenite.
4. Otvorite karticu **Authentification** aplikacije. Kopirajte `client_id` i `client_secret`.
5. Pokrenite **Add or change keys** i zalijepite ih.

Uvjeti, ukratko:

- Podaci: Licence Ouverte / Etalab 2.0. Ponovna uporaba, uključujući komercijalnu, dopuštena je uz navođenje izvora.
- Ne objavljujte i ne dijelite svoje pristupne podatke. Obavijestite PISTE ako procure.
- API Légifrance je beta usluga. Može biti obustavljen i ima kvote (po sekundi, minuti i danu).
- Tekstovi na Légifranceu nisu vjerodostojna inačica. Vjerodostojan je samo potpisani PDF Journal officiel.
- Judilibre: ne upotrebljavajte imena sudaca ili sudskih službenika za ocjenjivanje, uspoređivanje
  ili predviđanje njihova rada (Code de l'organisation judiciaire čl. L111-13; kazneno djelo).
- Judilibre: poštujte GDPR. Ne pokušavajte ponovno identificirati stranke.

Svoje kvote vidite na PISTE-u pod API Sélectionnées > Actions > Consulter les quotas.

## Sjedinjene Američke Države: api.data.gov (besplatno)

1. Idite na [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (ključ se prikazuje na zaslonu)
   ili [api.data.gov/signup](https://api.data.gov/signup/) (ključ vam se šalje e-poštom).
2. Unesite svoje ime i adresu e-pošte. Polje "how will you use it" nije obvezno.
3. Kopirajte ključ od 40 znakova.
4. Pokrenite **Add or change keys** i zalijepite ga kao ključ za SAD.

Uvjeti, ukratko:

- S vlastitim ključem govinfo dopušta do 36.000 zahtjeva na sat.
- Nismo pronašli uvjete korištenja specifične za API (api.data.gov/terms/ ne postoji). Neprovjereno.
  Pogledajte [pravila za govinfo](https://www.govinfo.gov/about/policies) i
  [politiku privatnosti data.gov](https://data.gov/privacy-policy/).
- Ključ zadržite za sebe.

## Gdje se ključevi čuvaju

- **Instalacijski program ili ručno:** kao običan tekst u MCP konfiguracijskoj datoteci svake
  aplikacije, u bloku `env` unosa `fontes`. Svatko tko može čitati vaše korisničke datoteke može
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
- **Proširenje za Claude Desktop (.mcpb):** Claude čuva ta polja u svojim postavkama i štiti ih
  sigurnom pohranom vašeg sustava (Keychain na Macu, Credential Manager u Windowsima).

Prije svake promjene instalacijski program sprema kopiju konfiguracijske datoteke pokraj nje
(`<file>.fontes-backup-<time>`). Kopije izrađene nakon što ste dodali ključeve također sadrže
ključeve. Izbrišite stare kopije koje vam ne trebaju.

## Promjena ili uklanjanje ključa

- Pokrenite **Add or change keys**. Zalijepite novi ključ da biste zamijenili postojeći ili
  upišite `-` da biste ga uklonili.
- Ili ručno uredite blok `env` i ponovno pokrenite aplikaciju.
- Deinstalacija programa Fontes uklanja cijeli njegov unos, zajedno s ključevima. Ne briše
  sigurnosne kopije.
- Ako je ključ procurio, zamijenite ga i kod izvora: na PISTE-u izradite nove pristupne podatke
  za svoju aplikaciju; za api.data.gov prijavite se za novi ključ.

## Poruke koje možete vidjeti

| Poruka | Značenje |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Nema ključa za Francusku. Dodajte ga. |
| `Inactive: needs a free PISTE account. ...` (u `list_jurisdictions`) | Isto. |
| `PISTE refused the client credentials ...` | ID ili secret je pogrešan ili više ne vrijedi. Ponovno kopirajte oba s kartice Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Vaša aplikacija nije pretplaćena na taj API ili niste prihvatili njegove uvjete. Pogledajte korake 2. i 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Nema ključa za SAD. Pretraživanje radi za nekoliko poziva dnevno. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Demo ključ je potrošen. Dodajte vlastiti ključ. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Ključ je pogrešan ili još nije potvrđen e-poštom. |

Prazna vrijednost smatra se kao da ključa nema.

## Dopuštenja (WLM_PERMITTED)

Ovo nije API ključ i instalacijski ga program ne postavlja. **Postavite ga samo ako to
dopuštenje imate vi osobno.**

Neki su izvori prema zadanim postavkama isključeni jer njihovi uvjeti ili robots.txt zabranjuju
automatiziranu uporabu bez dopuštenja. Ako imate dopuštenje izdavača, uključite izvor tako da
njegov kôd dodate u `WLM_PERMITTED`, odvojen zarezima, u bloku `env`: `"WLM_PERMITTED": "in,de"`.

| Kôd | Izvor |
|---|---|
| `az` | Azerbajdžan: e-qanun.az (Ministarstvo pravosuđa) |
| `bh` | Bahrein: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Kolumbija: Función Pública, Gestor Normativo (pročišćeni propisi) |
| `de` | Njemačka: NeuRIS (savezni portal pravnih informacija, probna usluga) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Grčka: National Printing Office, pretraživanje Government Gazette (search.et.gr) |
| `in` | Indija: India Code (indiacode.gov.in) |
| `mu` | Mauricijus: Supreme Court (supremecourt.govmu.org) |
| `sg` | Singapur: sudske presude (elitigation.sg) |

Bez dopuštenja Fontes javlja: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
