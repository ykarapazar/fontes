> Ovo je mašinski potpomognut prijevod. Mjerodavna je verzija na engleskom.

# Instalacija alata Fontes

Fontes omogućava vašoj AI aplikaciji da pretražuje sudske odluke i propise uživo na stranicama
sudova i državnih organa u više od 120 jurisdikcija. Svaki rezultat sadrži link na original. To
je standardni MCP server, pa radi u svakoj aplikaciji koja može pokrenuti lokalni MCP server:
Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed,
LM Studio, Cline i drugim.

Odaberite svoju aplikaciju, slijedite njene korake, a zatim [provjerite da li radi](#provjera-da-li-radi).

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

Za svaku od ovih aplikacija potreban je [uv](#potreban-vam-je-uv). Dodajte unos, sačuvajte, a
zatim zatvorite i ponovo otvorite aplikaciju.

**Cursor:** u `~/.cursor/mcp.json` (svi projekti) ili `.cursor/mcp.json` (jedan projekat):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** iz Command Palette pokrenite **MCP: Add Server**, odaberite
**Command (stdio)**, unesite `uvx fontes-mcp` i nazovite server `fontes`. Ili dodajte ovo u
`~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Starije postavke VS Code koriste `.vscode/mcp.json`, gdje je ključ najvišeg nivoa `servers`
umjesto `mcpServers`.

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

**LM Studio:** u desnoj bočnoj traci otvorite karticu **Program**, kliknite **Install → Edit
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

**Bilo koja druga MCP aplikacija** (Windsurf i druge): njena vlastita dokumentacija navodi gdje
čuva svoje MCP servere. Većina prihvata isti unos: naredba `uvx`, argument `fontes-mcp`.

Ako aplikacija ne može pronaći `uvx`, koristite punu putanju (na macOS i Linuxu ispisuje je
`which uvx`).

## Potreban vam je uv

Codex, Claude Code i ostale aplikacije pokreću Fontes pomoću `uvx`, koji dolazi uz **uv**, mali
besplatni alat kompanije Astral. Da ga instalirate, pogledajte
[uputstvo kompanije Astral](https://docs.astral.sh/uv/getting-started/installation/) ili pokrenite:

- macOS ili Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Ključevi

Nekim izvorima je potreban besplatan ključ: pogledajte [KEYS.md](KEYS.md).

## Provjera da li radi

U novom razgovoru pitajte: *„Koje jurisdikcije Fontes može pretraživati?“* Aplikacija bi trebala
odgovoriti spiskom država. Ako to ne uradi, zatvorite i ponovo otvorite aplikaciju još jednom.

## Instalacijski program jednim klikom (Mac i Windows)

Instalacijski program postavlja Fontes u sve vaše aplikacije odjednom: Claude Desktop,
Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio i Cline.

**Prije nego što počnete:** potpuno zatvorite svaku od ovih aplikacija. To je najvažnije za Claude
Code: dok radi, on ponovo zapisuje `~/.claude.json` i može poništiti izmjenu instalacijskog
programa. Ako ne možete zatvoriti Claude Code, dodajte Fontes u njega pomoću `claude mcp add`
(pogledajte [Claude Code](#claude-code)).

**Mac**

1. Preuzmite instalacijski program za Mac (`Fontes-Installer-…-mac.zip`) iz
   [najnovijeg izdanja](https://github.com/ykarapazar/fontes/releases/latest) i dvaput kliknite na njega da ga raspakujete.
2. Dvaput kliknite na **Fontes Installer**. Ako vas Mac pita želite li otvoriti aplikaciju
   preuzetu s interneta, kliknite **Open**.
3. Odaberite **Instaliraj** i kliknite **U redu**. Postavljanje traje oko minutu.
4. Poruka navodi aplikacije koje je postavio. Kliknite **Gotovo**, a zatim ponovo otvorite te
   aplikacije. Da prvo dodate opcionalne besplatne ključeve, umjesto toga kliknite
   **Dodaj ključeve**; pogledajte [Korak s ključevima](#korak-s-ključevima).

**Windows**

1. Preuzmite instalacijski program za Windows (`Fontes-Setup-….exe`) iz [najnovijeg izdanja](https://github.com/ykarapazar/fontes/releases/latest) i dvaput kliknite na njega.
   - Ako Windows prikaže "Windows protected your PC": kliknite **More info**, zatim **Run anyway**.
2. Kliknite **Instaliraj**. Otvara se prozor i postavlja Fontes.
3. Kada vas pita da li da šalje anonimne brojeve korištenja, pritisnite Enter za ne.
4. Pita da li da sada dodate ključeve. Pritisnite Enter da preskočite; pogledajte
   [Korak s ključevima](#korak-s-ključevima).
5. Kada se pojavi **Gotovo**, ponovo otvorite svoje AI aplikacije. Ako je neka još bila pokrenuta,
   potpuno je zatvorite (i iz sistemske trake, pored sata) i ponovo je otvorite.

Na kraju instalacijski program navodi aplikacije koje je postavio.

### Koje aplikacije postavlja

Aplikaciju postavlja samo ako je mapa s njenim postavkama već na vašem računaru. Claude Code se
postavlja samo ako postoji `~/.claude.json`. Claude Desktop se uvijek postavlja. Svaka aplikacija
dobija jedan unos, `fontes`, u ovoj datoteci:

| Aplikacija | Datoteka (Mac i Linux) | Datoteka (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, i vlastita kopija verzije iz Microsoft Storea |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, ili `~/.codeium/windsurf/mcp_config.json` u starijim verzijama | `%APPDATA%\devin\mcp_config.json`, ili `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code se postavlja ako postoji `~/.copilot` ili vlastita mapa postavki programa VS Code.

Dvije aplikacije zahtijevaju još jedan korak:

- **Windsurf:** nakon što ga ponovo otvorite, pritisnite osvježavanje u Cascadeu.
- **Cline unutar starijeg proširenja za VS Code:** dodajte Fontes ručno (pogledajte
  [Cline](#ostale-aplikacije)).

### Korak s ključevima

Odmah nakon instalacije, instalacijski program nudi da dodate besplatne ključeve za Francusku i
SAD. Da ih dodate ili promijenite kasnije:

- **Mac:** ponovo otvorite **Fontes Installer** i odaberite **Dodaj ili promijeni ključeve**.
- **Windows:** otvorite meni Start, zatim **Fontes** → **Dodaj ili promijeni ključeve**.

Unos se ne prikazuje. Ključevi se upisuju u svaku aplikaciju koja već ima Fontes. Nakon toga
zatvorite i ponovo otvorite aplikacije. Gdje nabaviti ključeve i šta otključavaju: [KEYS.md](KEYS.md).

### Rezervne kopije, ponovno pokretanje i uklanjanje

Instalacijski program mijenja samo unos `fontes`. Sve ostale postavke i komentari ostaju kakvi
su bili. Prije nego što izmijeni datoteku, pored nje sačuva kopiju pod nazivom
`<file>.fontes-backup-<date>`. Kopije napravljene nakon što ste dodali ključeve sadrže te
ključeve: obrišite one koje vam više ne trebaju. Instalira i uv. Ponovno pokretanje je sigurno:
popravlja postavku i ne mijenja ništa drugo.

Da uklonite Fontes, otvorite **Fontes Installer** i odaberite **Ukloni** (Mac) ili u Settings → Apps (Windows) uklonite **Fontes**. Uklanja unos `fontes`, zajedno s ključevima, iz svake
aplikacije. Vaše ostale postavke i rezervne kopije ostaju.

## Ažuriranja

- **Instalacijski program i datoteka `.mcpb`:** ne morate ništa raditi. Jednom dnevno, kada se
  aplikacija pokrene, Fontes u pozadini provjerava postoji li novija verzija i priprema je;
  sljedeći put kada se aplikacija pokrene, koristi nju. Ako se ažuriranje ne može preuzeti ili
  ne radi, Fontes nastavlja koristiti verziju koja je radila.
- **`uvx`:** Fontes vam javlja kada je dostupna novija verzija, na vrhu svog spiska jurisdikcija.
  Da uvijek pokrećete najnoviju verziju, koristite `fontes-mcp@latest` umjesto `fontes-mcp`.

Za ovo se nikamo ne šalju nikakve informacije o vama ili vašim pretragama.

## Privatnost

Fontes zadano ne šalje ništa o vama ili vašim pretragama. Brojevi korištenja šalju se samo uz
vaš pristanak (opt-in), a prijava greške šalje se tek nakon što je vidite i potvrdite.
Detalji: [PRIVACY.md](PRIVACY.md).

## Uklanjanje

Uklonite unos `fontes` iz MCP postavki svoje aplikacije (u Claude Code:
`claude mcp remove fontes`), a zatim zatvorite i ponovo otvorite aplikaciju.

## Dobro je znati

Fontes čita javne izvore, uglavnom stranice sudova i državnih organa. Nezvanične izvore označava
u svojim odgovorima. Uvijek otvorite link na izvor prije nego što se oslonite na odluku ili
odredbu.

Ako nešto pođe po zlu, pošaljite opis onoga što ste uradili i greške koju ste vidjeli na
fontesmcp@proton.me.

## Prije nego što se oslonite na Fontes

- Fontes je alat za istraživanje, a ne pravni savjet. Njegovo korištenje nikoga ne čini vašim
  advokatom.
- Pruža se „takav kakav jeste“, bez garancije, a njegovi autori nisu odgovorni za način na koji
  se koristi, u mjeri u kojoj to zakon dopušta. Potpuni uslovi su u [licenci](../../../LICENSE)
  (Apache 2.0).
