> Ovo je mašinski potpomognut prevod. Merodavna je verzija na engleskom.

# Instalacija programa Fontes

Fontes omogućava vašoj AI aplikaciji da pretražuje sudske odluke i propise uživo na sajtovima
sudova i državnih organa u više od 120 jurisdikcija. Svaki rezultat sadrži vezu ka originalu.
To je standardni MCP server, pa radi u svakoj aplikaciji koja može da pokrene lokalni MCP
server: Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Gemini CLI,
Windsurf, Zed, LM Studio, Cline i drugima.

Izaberite svoju aplikaciju, pratite njene korake, a zatim
[proverite da li radi](#proverite-da-li-radi).

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

Codex CLI i Codex proširenje za IDE dele ovo podešavanje (`~/.codex/config.toml`).
Potreban vam je [uv](#potreban-vam-je-uv).

## Claude Code

U terminalu:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Potreban vam je [uv](#potreban-vam-je-uv).

## Druge aplikacije

Svakoj od njih je potreban [uv](#potreban-vam-je-uv). Dodajte unos, sačuvajte, a zatim
zatvorite i ponovo otvorite aplikaciju.

**Cursor:** u `~/.cursor/mcp.json` (svi projekti) ili `.cursor/mcp.json` (jedan projekat):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** pokrenite **MCP: Add Server** iz Command Palette, izaberite
**Command (stdio)**, unesite `uvx fontes-mcp` i nazovite server `fontes`. Ili ovo dodajte u
`~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Starija podešavanja za VS Code koriste `.vscode/mcp.json`, gde je ključ najvišeg nivoa `servers`
umesto `mcpServers`.

**Gemini CLI:** u terminalu `gemini mcp add -s user fontes uvx fontes-mcp`. Ili ovo dodajte u
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** otvorite datoteku podešavanja (**zed: open settings file**) i dodajte:

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

**Cline:** kliknite ikonu **MCP Servers**, otvorite karticu **Configure**, kliknite **Configure
MCP Servers** i dodajte isti unos `mcpServers` kao za LM Studio.

**Claude Desktop ručno** (umesto datoteke `.mcpb`): dodajte isti unos `mcpServers` u
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Svaka druga MCP aplikacija** (Windsurf i druge): njena dokumentacija navodi gde čuva svoje MCP
servere. Većina prihvata isti unos: komanda `uvx`, argument `fontes`.

Ako aplikacija ne može da pronađe `uvx`, navedite punu putanju do njega (na macOS-u i Linux-u
prikazuje je `which uvx`).

## Potreban vam je uv

Codex, Claude Code i druge aplikacije pokreću Fontes preko `uvx`, koji dolazi uz **uv**, mali
besplatan alat kompanije Astral. Da biste ga instalirali, pogledajte
[uputstvo kompanije Astral](https://docs.astral.sh/uv/getting-started/installation/) ili pokrenite:

- macOS ili Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Ključevi

Nekim izvorima je potreban besplatan ključ: pogledajte [KEYS.md](KEYS.md).

## Proverite da li radi

U novom razgovoru pitajte: *„U kojim jurisdikcijama Fontes može da pretražuje?“* Aplikacija
treba da odgovori spiskom država. Ako ne odgovori, još jednom zatvorite i ponovo otvorite
aplikaciju.

## Instalacioni program na jedan klik (Mac)

Instalacioni program za Mac podešava Fontes u svim vašim aplikacijama odjednom: Claude Desktop,
Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio i Cline.
Instalacioni program za Windows je u pripremi; do tada koristite korake za svoju aplikaciju iznad.

**Pre nego što počnete:** potpuno zatvorite svaku od ovih aplikacija. To je posebno važno za
Claude Code: dok radi, on prepisuje `~/.claude.json` i može poništiti izmenu koju je napravio
instalacioni program. Ako ne možete da zatvorite Claude Code, dodajte Fontes u njega pomoću
`claude mcp add` (pogledajte [Claude Code](#claude-code)).

**Mac**

1. Preuzmite instalacioni program za Mac (`Fontes-Installer-…-mac.zip`) iz
   [najnovijeg izdanja](https://github.com/ykarapazar/fontes/releases/latest) i dvaput kliknite na njega da biste ga raspakovali.
2. Dvaput kliknite na **Fontes Installer**. Ako vas Mac pita da li želite da otvorite aplikaciju
   preuzetu sa interneta, kliknite na **Open**.
3. Izaberite **Instaliraj** i kliknite na **U redu**. Podešavanje traje oko minut.
4. Poruka navodi aplikacije koje je podesio. Kliknite na **Gotovo**, a zatim ponovo otvorite te
   aplikacije. Da biste prvo dodali opcione besplatne ključeve, umesto toga kliknite na
   **Dodaj ključeve**; pogledajte [Korak sa ključevima](#korak-sa-ključevima).

**Windows** (kada instalacioni program za Windows bude objavljen)

1. Raspakujte preuzeti **Fontes Installer** (desni klik → Extract All).
2. Dvaput kliknite na **Install Fontes.cmd**.
   - Ako Windows prikaže „Windows protected your PC“: kliknite **More info**, pa
     **Run anyway**.
3. Kada pita da li da se šalju anonimni brojevi korišćenja, pritisnite Enter da biste odbili.
4. Pita da li želite da sada dodate ključeve. Pritisnite Enter da biste preskočili; pogledajte
   [Korak sa ključevima](#korak-sa-ključevima).
5. Kada se pojavi **Done**, ponovo otvorite svoje AI aplikacije. Ako je neka od njih još
   radila, potpuno je zatvorite (uključujući i iz sistemske trake, pored sata) i ponovo je
   otvorite.

Na kraju instalacioni program navodi aplikacije koje je podesio.

### Koje aplikacije podešava

Podešava aplikaciju samo ako fascikla sa podešavanjima te aplikacije već postoji na vašem
računaru. Claude Code se podešava samo ako postoji `~/.claude.json`. Claude Desktop se uvek
podešava. Svaka aplikacija dobija jedan unos, `fontes`, u ovoj datoteci:

| Aplikacija | Datoteka (Mac i Linux) | Datoteka (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, kao i sopstvena kopija verzije iz Microsoft Store-a |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json` ili `~/.codeium/windsurf/mcp_config.json` u starijim verzijama | `%APPDATA%\devin\mcp_config.json` ili `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code se podešava ako postoji `~/.copilot` ili sopstvena fascikla podešavanja za VS Code.

Dvema aplikacijama je potreban još jedan korak:

- **Windsurf:** nakon ponovnog otvaranja kliknite dugme za osvežavanje u Cascade-u.
- **Cline u starom VS Code proširenju:** dodajte Fontes ručno (pogledajte [Cline](#druge-aplikacije)).

### Korak sa ključevima

Odmah nakon instalacije, instalacioni program nudi da doda besplatne ključeve za Francusku i
SAD. Da biste ih kasnije dodali ili promenili:

- **Mac:** ponovo otvorite **Fontes Installer** i izaberite **Dodaj ili promeni ključeve**.
- **Windows:** dvaput kliknite na **Add or change keys.cmd** u fascikli instalacionog programa.

Unos je skriven. Ključevi se upisuju u svaku aplikaciju koja već ima Fontes. Nakon toga zatvorite
i ponovo otvorite aplikacije. Gde se dobijaju ključevi i šta otključavaju: [KEYS.md](KEYS.md).

### Rezervne kopije, ponovna pokretanja i uklanjanje

Instalacioni program menja samo unos `fontes`. Sva ostala podešavanja i komentari ostaju
nepromenjeni. Pre nego što izmeni datoteku, pored nje čuva kopiju pod imenom
`<file>.fontes-backup-<date>`. Kopije napravljene nakon što ste dodali ključeve sadrže te
ključeve: obrišite one koje vam više nisu potrebne. On instalira i uv. Ponovno pokretanje je
bezbedno: ispravlja podešavanje i ne menja ništa drugo.

Da biste uklonili Fontes, otvorite **Fontes Installer** i izaberite **Ukloni** (Mac) ili dvaput kliknite na
**Uninstall Fontes.cmd** (Windows). On uklanja unos `fontes`, zajedno sa ključevima, iz svake
aplikacije. Vaša ostala podešavanja i rezervne kopije ostaju.

## Ažuriranja

- **Instalacioni program i datoteka `.mcpb`:** ne morate ništa da radite. Jednom dnevno, kada
  vaša aplikacija pokrene Fontes, on u pozadini proverava da li postoji novija verzija i
  priprema je; sledeće pokretanje je koristi. Ako ažuriranje ne može da se preuzme ili ne radi,
  Fontes nastavlja da koristi verziju koja je radila.
- **`uvx`:** Fontes vam na početku svog spiska jurisdikcija javlja kada izađe novija verzija. Da
  biste uvek pokretali najnoviju, koristite `fontes-mcp@latest` umesto `fontes-mcp`.

Ništa o vama ili vašim pretragama se radi ovoga nikuda ne šalje.

## Privatnost

Podrazumevano, Fontes ne šalje ništa o vama ili vašim pretragama. Brojevi korišćenja šalju se
samo uz vaš pristanak (opt-in), a prijava greške tek kada je vidite i potvrdite. Detalji:
[PRIVACY.md](PRIVACY.md).

## Deinstalacija

Obrišite unos `fontes` iz MCP podešavanja svoje aplikacije (u Claude Code-u:
`claude mcp remove fontes`), a zatim zatvorite i ponovo otvorite aplikaciju.

## Dobro je znati

Fontes čita javno dostupne izvore, uglavnom sajtove sudova i državnih organa. Nezvanične
izvore označava u svojim odgovorima. Uvek otvorite vezu ka izvoru pre nego što se oslonite na
odluku ili odredbu.

Ako nešto pođe naopako, pošaljite na fontesmcp@proton.me šta ste uradili i koju ste grešku
videli.

## Pre nego što se oslonite na njega

- Fontes je alat za istraživanje, a ne pravni savet. Njegovo korišćenje nikoga ne čini vašim
  pravnikom.
- Pruža se „takav kakav jeste“, bez garancije, i njegovi autori nisu odgovorni za način na koji
  se koristi, u meri u kojoj zakon to dopušta. Potpuni uslovi nalaze se u
  [licenci](../../../LICENSE) (Apache 2.0).
