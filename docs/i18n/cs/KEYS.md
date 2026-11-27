> Toto je strojově asistovaný překlad. Závazná je anglická verze.

# Klíče API

Téměř každý zdroj ve Fontes funguje bez klíče. Tři zdroje vyžadují bezplatný klíč:

| Klíč | Zpřístupní | Bez něj |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Francie: Judilibre (soudní rozhodnutí) a Légifrance (právní předpisy) | Francie je vypnutá. `list_jurisdictions` ji zobrazí jako neaktivní. |
| `WLM_US_GOVINFO_KEY` | Spojené státy: vyhledávání govinfo (stanoviska federálních soudů, Statutes at Large, public laws) | Fontes používá sdílený `DEMO_KEY`: přibližně 10 hledání denně na IP adresu. Otevření známého rozhodnutí a US Code klíč nevyžadují. |
| `WLM_US_COURTLISTENER_KEY` | Soudy států USA (`us-states`): rozhodnutí nejvyšších a odvolacích soudů všech 50 států a DC, z CourtListeneru | Judikatura států USA je vypnutá. `list_jurisdictions` ji zobrazí jako neaktivní. |

Klíče jsou volitelné. Můžete je přidat i později.

## Přidání klíče

**Pomocí instalátoru.** Jakmile je Fontes nastaven, instalátor nabídne přidání klíčů. Na Macu
klikněte na **Přidat klíče**, nebo na **Hotovo**, pokud krok chcete přeskočit; ve Windows odpovězte
na otázku (stisknutím Enter krok přeskočíte). Chcete-li klíče přidat nebo změnit později, spusťte
**Add or change keys**:

- Mac: znovu otevřete aplikaci Fontes Installer a zvolte **Přidat nebo změnit klíče**.
- Windows: otevřete nabídku Start, poté **Fontes** → **Přidat nebo změnit klíče**.

Psaný text není vidět. U každého klíče: vložte ho, stisknutím Enter ponechte stávající, nebo
napište `-` pro jeho odebrání. Klíče se zapíšou do každé aplikace, která už Fontes má.

**Pomocí rozšíření pro Claude Desktop (.mcpb).** Otevřete Claude > Settings > Extensions > Fontes
a vyplňte pole. Žádné není povinné.

**Ručně.** Přidejte proměnné do bloku `env` záznamu `fontes` v konfiguraci MCP své aplikace:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Po každé změně aplikaci restartujte.

## Francie: PISTE (zdarma)

1. Založte si účet na [piste.gouv.fr](https://piste.gouv.fr). Znamená to přijetí podmínek PISTE (CGU).
2. Přejděte na API > **Consentement CGU API**. Přijměte podmínky pro **JUDILIBRE** a **Légifrance** (production).
3. Vytvořte **production application**. `APP_SANDBOX`, který byl vytvořen pro vás, nemá přístup k produkci.
   V části "Modifier l'application" zaškrtněte **JUDILIBRE (production)** a **Légifrance (production)** a změny použijte.
4. Otevřete kartu **Authentification** aplikace. Zkopírujte `client_id` a `client_secret`.
5. Spusťte **Add or change keys** a vložte je.

Podmínky stručně:

- Data: Licence Ouverte / Etalab 2.0. Opakované použití, včetně komerčního, je povoleno s uvedením zdroje.
- Své přihlašovací údaje nezveřejňujte ani nesdílejte. Pokud uniknou, informujte PISTE.
- API Légifrance je služba ve verzi beta. Může být přerušeno a má kvóty (za sekundu, minutu a den).
- Texty na Légifrance nejsou autentickou verzí. Autentické je pouze podepsané PDF Journal officiel.
- Judilibre: nepoužívejte jména soudců nebo soudních zaměstnanců k hodnocení, srovnávání nebo
  předvídání jejich práce (Code de l'organisation judiciaire, čl. L111-13; trestný čin).
- Judilibre: dodržujte GDPR. Nepokoušejte se znovu identifikovat účastníky.

Své kvóty uvidíte na PISTE v části API Sélectionnées > Actions > Consulter les quotas.

## Spojené státy: api.data.gov (zdarma)

1. Přejděte na [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (klíč se zobrazí na obrazovce)
   nebo [api.data.gov/signup](https://api.data.gov/signup/) (klíč vám přijde e-mailem).
2. Zadejte své jméno a e-mailovou adresu. Pole "how will you use it" je volitelné.
3. Zkopírujte 40znakový klíč.
4. Spusťte **Add or change keys** a vložte ho jako klíč pro USA.

Podmínky stručně:

- S vlastním klíčem govinfo povoluje až 36 000 požadavků za hodinu.
- Podmínky použití specifické pro API jsme nenašli (api.data.gov/terms/ neexistuje). Neověřeno.
  Viz [zásady govinfo](https://www.govinfo.gov/about/policies) a
  [zásady ochrany soukromí data.gov](https://data.gov/privacy-policy/).
- Klíč si nechte pro sebe.

## Soudy států USA: CourtListener (zdarma)

CourtListener provozuje [Free Law Project](https://free.law), nezisková organizace, která od roku 2010 shromažďuje rozhodnutí amerických soudů a zpřístupňuje je všem zdarma. Podle vlastního sčítání obsahuje přes devět milionů rozhodnutí. Není to oficiální zdroj: soudy zveřejňují svá rozhodnutí samy a CourtListener je sbírá z webů soudů a ze skenovaných sbírek rozhodnutí. Každá odpověď Fontes, která z něj pochází, to uvádí. Fontes není s Free Law Project nijak spojen.

1. Vytvořte si bezplatný účet na [courtlistener.com](https://www.courtlistener.com/sign-in/).
2. Otevřete svůj profil a zkopírujte si svůj API token.
3. Spusťte **Add or change keys** a vložte jej jako klíč CourtListeneru.

Podmínky ve stručnosti ([úplné podmínky](https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies)):

- Token je jen váš: nesdílejte jej, nespojujte jej s cizími ani jej neprodávejte dál a nepoužívejte více účtů.
- Odpovídáte za to, co aplikace s umělou inteligencí s vaším tokenem dělá.
- Neprezentujte analýzu jejich dat provedenou umělou inteligencí jako vytvořenou, schválenou nebo ověřenou Free Law Project.
- Bezplatný účet umožňuje 5 požadavků za minutu, 50 za hodinu a 125 za den. Vyhledávání je jeden požadavek; otevření rozhodnutí jsou dva. Členství ve Free Law Project limity zvyšuje.
- CourtListener nezaručuje přesnost. Než se na rozhodnutí spolehnete, ověřte je podle kopie soudu.

## Kde jsou klíče uloženy

- **Instalátor nebo ručně:** jako prostý text v konfiguračním souboru MCP každé aplikace, v bloku
  `env` záznamu `fontes`. Kdokoli, kdo může číst vaše uživatelské soubory, může přečíst i klíče.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` nebo `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Rozšíření pro Claude Desktop (.mcpb):** Claude tato pole ukládá ve svém nastavení a chrání je
  zabezpečeným úložištěm vašeho systému (Keychain na Macu, Credential Manager ve Windows).

Před každou změnou instalátor uloží kopii konfiguračního souboru vedle něj
(`<file>.fontes-backup-<time>`). Kopie vytvořené po přidání klíčů klíče také obsahují. Smažte
staré kopie, které nepotřebujete.

## Změna nebo odebrání klíče

- Spusťte **Add or change keys**. Vložením nového klíče nahradíte stávající, napsáním `-` ho
  odeberete.
- Nebo ručně upravte blok `env` a restartujte aplikaci.
- Odinstalace Fontes odebere celý jeho záznam včetně klíčů. Zálohy nesmaže.
- Pokud klíč unikl, vyměňte ho také u zdroje: na PISTE vygenerujte pro svou aplikaci nové
  přihlašovací údaje; u api.data.gov si zaregistrujte nový klíč.

## Zprávy, které můžete vidět

| Zpráva | Význam |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Chybí klíč pro Francii. Přidejte ho. |
| `Inactive: needs a free PISTE account. ...` (v `list_jurisdictions`) | Totéž. |
| `PISTE refused the client credentials ...` | ID nebo secret je chybný nebo už neplatí. Znovu zkopírujte obojí z karty Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Vaše aplikace není přihlášena k odběru tohoto API nebo jste nepřijali jeho podmínky. Viz kroky 2 a 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Chybí klíč pro USA. Vyhledávání funguje pro několik volání denně. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Demo klíč je vyčerpán. Přidejte vlastní klíč. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Klíč je chybný nebo ještě nebyl potvrzen e-mailem. |

Prázdná hodnota se považuje za chybějící klíč.

## Povolení (WLM_PERMITTED)

Nejde o klíč API a instalátor ho nenastavuje. **Nastavte ho pouze tehdy, když toto povolení máte
vy osobně.**

Některé zdroje jsou ve výchozím stavu vypnuté, protože jejich podmínky nebo robots.txt zakazují
automatizované použití bez povolení. Pokud máte povolení vydavatele, zapněte zdroj přidáním jeho
kódu do `WLM_PERMITTED`, odděleného čárkami, v bloku `env`: `"WLM_PERMITTED": "in,de"`.

| Kód | Zdroj |
|---|---|
| `az` | Ázerbájdžán: e-qanun.az (Ministerstvo spravedlnosti) |
| `bh` | Bahrajn: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Kolumbie: Función Pública, Gestor Normativo (úplná znění předpisů) |
| `de` | Německo: NeuRIS (spolkový portál právních informací, zkušební provoz) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Řecko: National Printing Office, vyhledávání v Government Gazette (search.et.gr) |
| `mu` | Mauricius: Supreme Court (supremecourt.govmu.org) |
| `sg` | Singapur: soudní rozsudky (elitigation.sg) |

Bez povolení Fontes hlásí: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
