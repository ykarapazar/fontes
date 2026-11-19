> Ovo je strojno potpomognut prijevod. Mjerodavna je engleska verzija.

# Instalacija programa Fontes

Fontes omogućuje vašoj AI aplikaciji da pretražuje sudske odluke i propise uživo na mrežnim
stranicama sudova i državnih tijela u više od 120 jurisdikcija. Svaki rezultat sadrži poveznicu
na izvornik. To je standardni MCP poslužitelj, pa radi u svakoj aplikaciji koja može pokrenuti
lokalni MCP poslužitelj: Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot),
Gemini CLI, Windsurf, Zed, LM Studio, Cline i drugima.

Odaberite svoju aplikaciju, slijedite njezine korake, a zatim [provjerite radi li](#provjera-radi-li).

## Claude Desktop

1. Preuzmite Fontes datoteku `.mcpb` iz
   [najnovijeg izdanja](https://github.com/ykarapazar/fontes/releases/latest).
2. Dvaput kliknite na nju. Claude Desktop će je otvoriti.
3. Kliknite **Install**.

## Codex

U terminalu:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI i Codex proširenje za IDE dijele ovu postavku (`~/.codex/config.toml`).
Potreban vam je [uv](#potreban-vam-je-uv).

## Claude Code

U terminalu:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Potreban vam je [uv](#potreban-vam-je-uv).

## Ostale aplikacije

Za svaku od ovih aplikacija potreban je [uv](#potreban-vam-je-uv). Dodajte unos, spremite, a
zatim zatvorite i ponovno otvorite aplikaciju.

**Cursor:** u `~/.cursor/mcp.json` (svi projekti) ili `.cursor/mcp.json` (jedan projekt):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** iz Command Palette pokrenite **MCP: Add Server**, odaberite
**Command (stdio)**, unesite `uvx fontes-mcp` i nazovite poslužitelj `fontes`. Ili dodajte ovo u
`~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Starije postavke programa VS Code upotrebljavaju `.vscode/mcp.json`, gdje je ključ najviše
razine `servers` umjesto `mcpServers`.

**Gemini CLI:** u terminalu, `gemini mcp add -s user fontes uvx fontes-mcp`. Ili dodajte ovo u
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** otvorite datoteku postavki (**zed: open settings file**) i dodajte:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** na desnoj bočnoj traci otvorite karticu **Program**, kliknite **Install → Edit
mcp.json** i dodajte:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** kliknite ikonu **MCP Servers**, otvorite karticu **Configure**, kliknite **Configure MCP
Servers** i dodajte isti unos `mcpServers` kao za LM Studio.

**Claude Desktop, ručno** (umjesto datoteke `.mcpb`): dodajte isti unos `mcpServers` u
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Bilo koja druga MCP aplikacija** (Windsurf i druge): njezina vlastita dokumentacija navodi gdje
čuva svoje MCP poslužitelje. Većina prihvaća isti unos: naredba `uvx`, argument `fontes`.

Ako aplikacija ne može pronaći `uvx`, upotrijebite punu putanju (na macOS-u i Linuxu ispisuje je
`which uvx`).

## Potreban vam je uv

Codex, Claude Code i ostale aplikacije pokreću Fontes pomoću naredbe `uvx`, koja dolazi uz
**uv**, mali besplatni alat tvrtke Astral. Da biste ga instalirali, pogledajte
[upute tvrtke Astral](https://docs.astral.sh/uv/getting-started/installation/) ili pokrenite:

- macOS ili Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Ključevi

Nekim izvorima potreban je besplatan ključ: pogledajte [KEYS.md](KEYS.md).

## Provjera radi li

U novom razgovoru pitajte: *„Koje jurisdikcije Fontes može pretraživati?”* Aplikacija bi trebala
odgovoriti popisom država. Ako to ne učini, još jednom zatvorite i ponovno otvorite aplikaciju.

## Instalacijski program jednim klikom (Mac i Windows)

Instalacijski program postavlja Fontes u sve vaše aplikacije odjednom: Claude Desktop, Codex,
Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio i Cline.

**Prije nego što počnete:** potpuno zatvorite svaku od tih aplikacija. To je najvažnije za Claude
Code: dok radi, on ponovno zapisuje `~/.claude.json` i može poništiti promjenu instalacijskog
programa. Ako ne možete zatvoriti Claude Code, dodajte Fontes u njega naredbom `claude mcp add`
(pogledajte [Claude Code](#claude-code)).

**Mac**

1. Preuzmite instalacijski program za Mac (`Fontes-Installer-…-mac.zip`) iz [najnovijeg
   izdanja](https://github.com/ykarapazar/fontes/releases/latest) i dvaput kliknite na njega da
   biste ga raspakirali.
2. Dvaput kliknite na **Fontes Installer**. Ako vas Mac pita želite li otvoriti aplikaciju preuzetu
   s interneta, kliknite **Open**.
3. Odaberite **Instaliraj** i kliknite **U redu**. Postavljanje traje otprilike minutu.
4. Poruka navodi aplikacije koje je postavio. Kliknite **Gotovo**, a zatim ponovno otvorite te
   aplikacije. Da biste najprije dodali neobavezne besplatne ključeve, umjesto toga kliknite **Dodaj
   ključeve**; pogledajte [Korak s ključevima](#korak-s-ključevima).

**Windows**

1. Preuzmite instalacijski program za Windows (`Fontes-Setup-….exe`) iz [najnovijeg
   izdanja](https://github.com/ykarapazar/fontes/releases/latest) i dvaput kliknite na njega.
   - Ako Windows prikaže "Windows protected your PC": kliknite **More info**, zatim **Run anyway**.
2. Kliknite **Instaliraj**. Otvorit će se prozor i postaviti Fontes.
3. Kada vas pita želite li slati anonimne brojeve korištenja, pritisnite Enter za ne.
4. Pita želite li sada dodati ključeve. Pritisnite Enter da biste preskočili; pogledajte
   [Korak s ključevima](#korak-s-ključevima).
5. Kada se pojavi **Gotovo**, ponovno otvorite svoje AI aplikacije. Ako je neka još bila
   pokrenuta, potpuno je zatvorite (i iz područja obavijesti, pokraj sata) i ponovno je otvorite.

Na kraju instalacijski program navodi aplikacije koje je postavio.

### Koje aplikacije postavlja

Aplikaciju postavlja samo ako je mapa s njezinim postavkama već na vašem računalu. Claude Code
postavlja samo ako postoji `~/.claude.json`. Claude Desktop postavlja uvijek. Svaka aplikacija
dobiva jedan unos, `fontes`, u ovoj datoteci:

| Aplikacija | Datoteka (Mac i Linux) | Datoteka (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, i vlastita kopija inačice iz trgovine Microsoft Store |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, ili `~/.codeium/windsurf/mcp_config.json` u starijim inačicama | `%APPDATA%\devin\mcp_config.json`, ili `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code se postavlja ako postoji `~/.copilot` ili vlastita mapa postavki programa VS Code.

Dvije aplikacije zahtijevaju još jedan korak:

- **Windsurf:** nakon što ga ponovno otvorite, pritisnite osvježavanje u Cascadeu.
- **Cline unutar starijeg proširenja za VS Code:** dodajte Fontes ručno (pogledajte
  [Cline](#ostale-aplikacije)).

### Korak s ključevima

Odmah nakon instalacije instalacijski program nudi da dodate besplatne ključeve za Francusku i
SAD. Da biste ih dodali ili promijenili kasnije:

- **Mac:** ponovno otvorite **Fontes Installer** i odaberite **Dodaj ili promijeni ključeve**.
- **Windows:** otvorite Start izbornik, zatim **Fontes** → **Add or change keys**.

Unos se ne prikazuje. Ključevi se upisuju u svaku aplikaciju koja već ima Fontes. Nakon toga
zatvorite i ponovno otvorite aplikacije. Gdje nabaviti ključeve i što otključavaju: [KEYS.md](KEYS.md).

### Sigurnosne kopije, ponovno pokretanje i uklanjanje

Instalacijski program mijenja samo unos `fontes`. Sve ostale postavke i komentari ostaju kakvi
su bili. Prije nego što promijeni datoteku, pokraj nje spremi kopiju pod nazivom
`<file>.fontes-backup-<date>`. Kopije izrađene nakon što ste dodali ključeve sadrže te ključeve:
izbrišite one koje vam više ne trebaju. Instalira i uv. Ponovno pokretanje je sigurno: popravlja
postavku i ne mijenja ništa drugo.

Da biste uklonili Fontes, otvorite **Fontes Installer** i odaberite **Ukloni** (Mac) ili uklonite **Fontes** u Postavke → Aplikacije (Windows). Uklanja unos `fontes`, zajedno s ključevima, iz svake
aplikacije. Vaše ostale postavke i sigurnosne kopije ostaju.

## Ažuriranja

- **Instalacijski program i datoteka `.mcpb`:** ne morate ništa činiti. Jednom dnevno, kada se
  aplikacija pokrene, Fontes u pozadini provjerava postoji li novija inačica i priprema je;
  sljedeći put kada se aplikacija pokrene, upotrebljava nju. Ako se ažuriranje ne može preuzeti
  ili ne radi, Fontes nastavlja upotrebljavati inačicu koja je radila.
- **`uvx`:** Fontes vas obavještava kada je dostupna novija inačica, na vrhu svojeg popisa
  jurisdikcija. Da biste uvijek pokretali najnoviju inačicu, upotrijebite `fontes-mcp@latest` umjesto
  `fontes`.

Za to se nikamo ne šalju nikakve informacije o vama ili vašim pretraživanjima.

## Privatnost

Fontes prema zadanim postavkama ne šalje ništa o vama ni o vašim pretraživanjima. Brojevi
korištenja šalju se samo uz vaš pristanak (opt-in), a prijava pogreške šalje se tek nakon što je
vidite i potvrdite. Pojedinosti: [PRIVACY.md](PRIVACY.md).

## Uklanjanje

Uklonite unos `fontes` iz MCP postavki svoje aplikacije (u programu Claude Code:
`claude mcp remove fontes`), a zatim zatvorite i ponovno otvorite aplikaciju.

## Dobro je znati

Fontes čita javne izvore, uglavnom mrežne stranice sudova i državnih tijela. Neslužbene izvore
označava u svojim odgovorima. Uvijek otvorite poveznicu na izvor prije nego što se oslonite na
odluku ili odredbu.

Ako nešto pođe po zlu, pošaljite opis onoga što ste učinili i pogreške koju ste vidjeli na
fontesmcp@proton.me.

## Prije nego što se oslonite na Fontes

- Fontes je alat za istraživanje, a ne pravni savjet. Njegovo korištenje nikoga ne čini vašim
  odvjetnikom.
- Pruža se „takav kakav jest”, bez jamstva, a njegovi autori nisu odgovorni za način na koji se
  upotrebljava, u mjeri u kojoj to zakon dopušta. Potpuni uvjeti nalaze se u
  [licenciji](../../../LICENSE) (Apache 2.0).
