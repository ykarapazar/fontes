> Toto je strojovo podporovaný preklad. Rozhodujúce je anglické znenie.

# Kľúče API

Takmer každý zdroj vo Fontes funguje bez kľúča. Tri potrebujú bezplatný kľúč:

| Kľúč | Sprístupní | Bez neho |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Francúzsko: Judilibre (súdne rozhodnutia) a Légifrance (právne predpisy) | Francúzsko je vypnuté. `list_jurisdictions` ho zobrazuje ako neaktívne. |
| `WLM_US_GOVINFO_KEY` | Spojené štáty: vyhľadávanie govinfo (rozhodnutia federálnych súdov, Statutes at Large, public laws) | Fontes použije spoločný `DEMO_KEY`: približne 10 vyhľadávaní denne na IP adresu. Otvorenie známeho rozhodnutia a US Code kľúč nepotrebujú. |
| `WLM_US_COURTLISTENER_KEY` | Súdy amerických štátov (`us-states`): rozhodnutia najvyšších a odvolacích súdov všetkých 50 štátov a DC z CourtListener | Judikatúra amerických štátov je vypnutá. `list_jurisdictions` ju zobrazuje ako neaktívnu. |

Kľúče sú voliteľné. Môžete ich pridať neskôr.

## Pridanie kľúča

**Pomocou inštalátora.** Keď je Fontes nastavený, inštalátor ponúkne pridanie kľúčov. Na Macu
kliknite na **Pridať kľúče** alebo na **Hotovo**, ak to chcete preskočiť; vo Windows odpovedzte na
otázku (stlačením Enter ju preskočíte). Ak chcete kľúče pridať alebo zmeniť neskôr, spustite
**Add or change keys**:

- Mac: znova otvorte aplikáciu Fontes Installer a zvoľte **Pridať alebo zmeniť kľúče**.
- Windows: otvorte ponuku Štart, potom **Fontes** → **Pridať alebo zmeniť kľúče**.

Písanie je skryté. Pri každom kľúči: vložte ho, stlačením Enter ponechajte existujúci, alebo
zadaním `-` ho odstráňte. Kľúče sa zapíšu do každej aplikácie, ktorá už Fontes má.

**Pomocou rozšírenia Claude Desktop (.mcpb).** Otvorte Claude > Settings > Extensions > Fontes a
vyplňte polia. Všetky sú voliteľné.

**Ručne.** Pridajte premenné do bloku `env` záznamu `fontes` v MCP konfigurácii svojej aplikácie:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Po každej zmene aplikáciu reštartujte.

## Francúzsko: PISTE (bezplatne)

1. Vytvorte si účet na [piste.gouv.fr](https://piste.gouv.fr). To znamená prijať podmienky PISTE (CGU).
2. Prejdite do API > **Consentement CGU API**. Prijmite podmienky pre **JUDILIBRE** a **Légifrance** (production).
3. Vytvorte **produkčnú aplikáciu** (production application). `APP_SANDBOX`, ktorá bola vytvorená
   pre vás, nemá prístup k produkcii. V časti „Modifier l'application“ zaškrtnite
   **JUDILIBRE (production)** a **Légifrance (production)** a potom zmeny použite.
4. Otvorte kartu aplikácie **Authentification**. Skopírujte `client_id` a `client_secret`.
5. Spustite **Add or change keys** a vložte ich.

Podmienky v skratke:

- Údaje: Licence Ouverte / Etalab 2.0. Opätovné použitie vrátane komerčného je povolené s uvedením zdroja.
- Svoje prístupové údaje nezverejňujte ani nezdieľajte. Ak uniknú, oznámte to PISTE.
- API Légifrance je beta služba. Môže byť pozastavená a má kvóty (za sekundu, minútu a deň).
- Texty Légifrance nie sú autentickým znením. Autentické je iba podpísané PDF Journal officiel.
- Judilibre: nepoužívajte mená sudcov ani súdnych úradníkov na hodnotenie, porovnávanie alebo
  predpovedanie ich práce (Code de l'organisation judiciaire, čl. L111-13; trestný čin).
- Judilibre: dodržiavajte GDPR. Nepokúšajte sa o opätovnú identifikáciu účastníkov konania.

Svoje kvóty nájdete na PISTE v časti API Sélectionnées > Actions > Consulter les quotas.

## Spojené štáty: api.data.gov (bezplatne)

1. Prejdite na [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (kľúč sa zobrazí na
   obrazovke) alebo [api.data.gov/signup](https://api.data.gov/signup/) (kľúč vám príde e-mailom).
2. Zadajte svoje meno a e-mail. Pole „how will you use it“ je voliteľné.
3. Skopírujte 40-znakový kľúč.
4. Spustite **Add or change keys** a vložte ho ako kľúč pre USA.

Podmienky v skratke:

- S vlastným kľúčom govinfo umožňuje až 36 000 požiadaviek za hodinu.
- Nenašli sme žiadne podmienky používania špecifické pre API (api.data.gov/terms/ neexistuje).
  Neoverené. Pozri [zásady govinfo](https://www.govinfo.gov/about/policies) a
  [zásady ochrany súkromia data.gov](https://data.gov/privacy-policy/).
- Kľúč si nechajte pre seba.

## Súdy amerických štátov: CourtListener (bezplatne)

CourtListener prevádzkuje [Free Law Project](https://free.law), nezisková organizácia, ktorá od roku 2010 zhromažďuje rozhodnutia amerických súdov a sprístupňuje ich všetkým bezplatne. Podľa vlastných údajov obsahuje viac ako deväť miliónov rozhodnutí. Nie je oficiálnym zdrojom: súdy zverejňujú vlastné rozhodnutia a CourtListener ich zhromažďuje z webových stránok súdov a zo skenovaných zbierok rozhodnutí. Každá odpoveď Fontes z neho to uvádza. Fontes nie je nijako spojený s Free Law Project.

1. Vytvorte si bezplatný účet na [courtlistener.com](https://www.courtlistener.com/sign-in/).
2. Otvorte svoj profil a skopírujte svoj API token.
3. Spustite **Add or change keys** a vložte ho ako kľúč CourtListener.

Podmienky v skratke ([úplné podmienky](https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies)):

- Token je len váš: nezdieľajte ho, nezlučujte ani nepredávajte a nepoužívajte viac účtov.
- Zodpovedáte za to, čo aplikácia s AI robí s vaším tokenom.
- Neprezentujte analýzu ich údajov vytvorenú AI ako vytvorenú, schválenú alebo overenú Free Law Project.
- Bezplatný účet umožňuje 5 požiadaviek za minútu, 50 za hodinu a 125 za deň. Vyhľadávanie je jedna požiadavka; otvorenie rozhodnutia sú dve. Členstvo vo Free Law Project limity zvyšuje.
- CourtListener nezaručuje presnosť. Pred použitím skontrolujte rozhodnutie podľa kópie súdu.

## Kde sú kľúče uložené

- **Inštalátor alebo ručne:** ako obyčajný text v MCP konfiguračnom súbore každej aplikácie, v
  bloku `env` záznamu `fontes`. Ktokoľvek, kto môže čítať vaše používateľské súbory, môže čítať aj
  kľúče.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` alebo `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Rozšírenie Claude Desktop (.mcpb):** Claude uchováva tieto polia vo svojich nastaveniach a
  chráni ich zabezpečeným úložiskom vášho systému (Keychain na Macu, Credential Manager vo
  Windows).

Pred každou zmenou inštalátor uloží kópiu konfiguračného súboru vedľa neho
(`<file>.fontes-backup-<time>`). Kópie vytvorené po pridaní kľúčov obsahujú aj kľúče. Staré
kópie, ktoré nepotrebujete, vymažte.

## Zmena alebo odstránenie kľúča

- Spustite **Add or change keys**. Vložením nového kľúča ho nahradíte, zadaním `-` ho odstránite.
- Alebo upravte blok `env` ručne a reštartujte aplikáciu.
- Odinštalovanie Fontes odstráni celý jeho záznam vrátane kľúčov. Záložné kópie nevymaže.
- Ak kľúč unikol, nahraďte ho aj pri zdroji: na PISTE si pre svoju aplikáciu vytvorte nové
  prístupové údaje; pri api.data.gov sa zaregistrujte na nový kľúč.

## Správy, ktoré môžete vidieť

| Správa | Význam |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Chýba kľúč pre Francúzsko. Pridajte ho. |
| `Inactive: needs a free PISTE account. ...` (v `list_jurisdictions`) | To isté. |
| `PISTE refused the client credentials ...` | ID alebo secret je nesprávne alebo už nie je platné. Skopírujte znova obe z karty Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Vaša aplikácia nie je prihlásená k odberu tohto API alebo ste neprijali jeho podmienky. Pozri kroky 2 a 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Chýba kľúč pre USA. Vyhľadávanie funguje pre niekoľko volaní denne. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Demonštračný kľúč je vyčerpaný. Pridajte vlastný kľúč. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Kľúč je nesprávny alebo ešte nie je potvrdený z e-mailu. |

Prázdna hodnota sa počíta ako žiadny kľúč.

## Povolenia (WLM_PERMITTED)

Toto nie je kľúč API a inštalátor ho nenastavuje. **Nastavte ho iba vtedy, ak toto povolenie
máte sami.**

Niektoré zdroje sú predvolene vypnuté, pretože ich podmienky alebo robots.txt zakazujú
automatizované použitie bez povolenia. Ak máte povolenie od vydavateľa, zdroj zapnete tak, že
jeho kód pridáte do `WLM_PERMITTED`, oddelený čiarkami, v bloku `env`: `"WLM_PERMITTED": "in,de"`.

| Kód | Zdroj |
|---|---|
| `az` | Azerbajdžan: e-qanun.az (Ministerstvo spravodlivosti) |
| `bh` | Bahrajn: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Kolumbia: Función Pública, Gestor Normativo (konsolidované právne predpisy) |
| `de` | Nemecko: NeuRIS (federálny portál právnych informácií, skúšobná prevádzka) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Grécko: Národná tlačiareň, vyhľadávanie vo Vládnom vestníku (search.et.gr) |
| `mu` | Maurícius: Najvyšší súd (supremecourt.govmu.org) |
| `sg` | Singapur: súdne rozsudky (elitigation.sg) |

Bez povolenia Fontes hlási: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
