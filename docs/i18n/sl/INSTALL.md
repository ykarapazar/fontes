> To je strojno podprt prevod. Merodajna je angleška različica.

# Namestitev orodja Fontes

Fontes vaši aplikaciji AI omogoča, da v živo išče sodne odločbe in predpise na spletnih straneh
sodišč in državnih organov v 125 jurisdikcijah. Vsak rezultat vsebuje povezavo do
izvirnika. Gre za standardni strežnik MCP, zato deluje v vsaki aplikaciji, ki lahko zažene
lokalni strežnik MCP: Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot),
Gemini CLI, Windsurf, Zed, LM Studio, Cline in drugih.

Izberite svojo aplikacijo, sledite njenim korakom in nato [preverite, ali deluje](#preverjanje-delovanja).

## Claude Desktop

1. Prenesite datoteko Fontes `.mcpb` iz
   [najnovejše izdaje](https://github.com/ykarapazar/fontes/releases/latest).
2. Dvakrat jo kliknite. Claude Desktop jo odpre.
3. Kliknite **Install**.

## Codex

V terminalu:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI in razširitev Codex za IDE si to nastavitev delita (`~/.codex/config.toml`).
Potrebujete [uv](#potrebujete-uv).

## Claude Code

V terminalu:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Potrebujete [uv](#potrebujete-uv).

## Druge aplikacije

Vsaka od teh aplikacij potrebuje [uv](#potrebujete-uv). Dodajte vnos, shranite ter nato
aplikacijo zaprite in znova odprite.

**Cursor:** v `~/.cursor/mcp.json` (vsi projekti) ali `.cursor/mcp.json` (en projekt):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** v Command Palette zaženite **MCP: Add Server**, izberite
**Command (stdio)**, vnesite `uvx fontes-mcp` in strežnik poimenujte `fontes`. Ali pa to dodajte v
`~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Starejše nastavitve VS Code uporabljajo `.vscode/mcp.json`, kjer je ključ najvišje ravni
`servers` namesto `mcpServers`.

**Gemini CLI:** v terminalu `gemini mcp add -s user fontes uvx fontes-mcp`. Ali pa to dodajte v
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** odprite datoteko z nastavitvami (**zed: open settings file**) in dodajte:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** v desni stranski vrstici odprite zavihek **Program**, kliknite **Install → Edit
mcp.json** in dodajte:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** kliknite ikono **MCP Servers**, odprite zavihek **Configure**, kliknite **Configure MCP
Servers** in dodajte isti vnos `mcpServers` kot za LM Studio.

**Claude Desktop, ročno** (namesto datoteke `.mcpb`): isti vnos `mcpServers` dodajte v
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Katera koli druga aplikacija MCP** (Windsurf in druge): njena lastna dokumentacija navaja, kje
hrani svoje strežnike MCP. Večina sprejme isti vnos: ukaz `uvx`, argument `fontes-mcp`.

Če aplikacija ne najde `uvx`, uporabite celotno pot (v sistemih macOS in Linux jo izpiše
`which uvx`).

## Potrebujete uv

Codex, Claude Code in druge aplikacije zaženejo Fontes z ukazom `uvx`, ki je del orodja **uv**,
majhnega brezplačnega orodja podjetja Astral. Za namestitev glejte
[navodila podjetja Astral](https://docs.astral.sh/uv/getting-started/installation/) ali zaženite:

- macOS ali Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Ključi

Nekateri viri potrebujejo brezplačen ključ: glejte [KEYS.md](KEYS.md).

## Preverjanje delovanja

V novem pogovoru vprašajte: *»Katere jurisdikcije lahko preišče Fontes?«* Aplikacija bi morala
odgovoriti s seznamom držav. Če ne, aplikacijo še enkrat zaprite in znova odprite.

## Namestitveni program z enim klikom (Mac in Windows)

Namestitveni program nastavi Fontes v vseh vaših aplikacijah naenkrat: Claude Desktop, Codex,
Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio in Cline.

**Preden začnete:** vsako od teh aplikacij popolnoma zaprite. To je najpomembneje pri Claude
Code: medtem ko teče, znova zapisuje `~/.claude.json` in lahko razveljavi spremembo
namestitvenega programa. Če Claude Code ne morete zapreti, vanj dodajte Fontes z ukazom
`claude mcp add` (glejte [Claude Code](#claude-code)).

**Mac**

1. Namestitveni program za Mac (`Fontes-Installer-…-mac.zip`) prenesite iz
   [najnovejše izdaje](https://github.com/ykarapazar/fontes/releases/latest) in ga dvakrat kliknite, da ga razširite.
2. Dvakrat kliknite **Fontes Installer**. Če vas Mac vpraša, ali želite odpreti aplikacijo, preneseno
   z interneta, kliknite **Odpri**.
3. Izberite **Namesti** in kliknite **V redu**. Nastavitev traja približno minuto.
4. Sporočilo navede aplikacije, ki jih je nastavil. Kliknite **Končano** in nato znova odprite te
   aplikacije. Če želite najprej dodati neobvezne brezplačne ključe, namesto tega kliknite
   **Dodaj ključe**; glejte [Korak s ključi](#korak-s-ključi).

**Windows**

1. Prenesite namestitveni program za Windows (`Fontes-Setup-….exe`) z
   [najnovejše izdaje](https://github.com/ykarapazar/fontes/releases/latest) in dvakrat kliknite nanj.
   - Če Windows prikaže "Windows protected your PC": kliknite **More info** in nato **Run anyway**.
2. Kliknite **Namesti**. Odpre se okno in nastavi Fontes.
3. Ko vas vpraša, ali želite pošiljati anonimne števce uporabe, za ne pritisnite Enter.
4. Vpraša, ali želite zdaj dodati ključe. Pritisnite Enter, da to preskočite; glejte
   [Korak s ključi](#korak-s-ključi).
5. Ko se prikaže **Končano**, znova odprite svoje aplikacije AI. Če je katera še tekla, jo
   popolnoma zaprite (tudi iz območja za obvestila ob uri) in znova odprite.

Na koncu namestitveni program navede aplikacije, ki jih je nastavil.

### Katere aplikacije nastavi

Aplikacijo nastavi le, če je mapa z njenimi nastavitvami že v vašem računalniku. Claude Code
nastavi le, če obstaja `~/.claude.json`. Claude Desktop nastavi vedno. Vsaka aplikacija dobi en
vnos, `fontes`, v tej datoteki:

| Aplikacija | Datoteka (Mac in Linux) | Datoteka (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json` in lastna kopija različice iz trgovine Microsoft Store |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json` ali `~/.codeium/windsurf/mcp_config.json` v starejših različicah | `%APPDATA%\devin\mcp_config.json` ali `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code se nastavi, če obstaja `~/.copilot` ali lastna mapa z nastavitvami VS Code.

Dve aplikaciji potrebujeta še en korak:

- **Windsurf:** ko ga znova odprete, v Cascade pritisnite osvežitev.
- **Cline v starejši razširitvi za VS Code:** Fontes dodajte ročno (glejte
  [Cline](#druge-aplikacije)).

### Korak s ključi

Takoj po namestitvi namestitveni program ponudi, da dodate brezplačna ključa za Francijo in ZDA.
Če ju želite dodati ali spremeniti pozneje:

- **Mac:** znova odprite **Fontes Installer** in izberite **Dodaj ali spremeni ključe**.
- **Windows:** odprite meni Start, nato **Fontes** → **Dodaj ali spremeni ključe**.

Vnos se ne prikazuje. Ključi se zapišejo v vsako aplikacijo, ki že ima Fontes. Nato aplikacije
zaprite in znova odprite. Kje dobiti ključe in kaj odklenejo: [KEYS.md](KEYS.md).

### Varnostne kopije, ponovni zagon in odstranitev

Namestitveni program spremeni le vnos `fontes`. Vse druge nastavitve in komentarji ostanejo
nespremenjeni. Preden spremeni datoteko, poleg nje shrani kopijo z imenom
`<file>.fontes-backup-<date>`. Kopije, ustvarjene potem, ko ste dodali ključe, te ključe
vsebujejo: izbrišite tiste, ki jih ne potrebujete več. Namesti tudi uv. Ponovni zagon je varen:
popravi nastavitev in ne spremeni ničesar drugega.

Če želite Fontes odstraniti, odprite **Fontes Installer** in izberite **Odstrani** (Mac) ali odstranite
**Fontes** v Nastavitvah → Aplikacije (Windows). Iz vsake aplikacije odstrani vnos `fontes`, skupaj s ključi.
Vaše druge nastavitve in varnostne kopije ostanejo.

## Posodobitve

- **Namestitveni program in datoteka `.mcpb`:** ničesar vam ni treba narediti. Enkrat na dan, ko
  se aplikacija zažene, Fontes v ozadju preveri, ali obstaja novejša različica, in jo pripravi;
  ob naslednjem zagonu aplikacije uporabi njo. Če posodobitve ni mogoče prenesti ali ne deluje,
  Fontes še naprej uporablja različico, ki je delovala.
- **`uvx`:** Fontes vas na vrhu svojega seznama jurisdikcij obvesti, ko je na voljo novejša
  različica. Če želite vedno zagnati najnovejšo različico, uporabite `fontes-mcp@latest` namesto
  `fontes`.

Za to se nikamor ne pošiljajo nobeni podatki o vas ali vaših iskanjih.

## Zasebnost

Fontes privzeto ne pošilja ničesar o vas ali vaših iskanjih. Števci uporabe se pošiljajo le, če
privolite (opt-in), prijava napake pa se pošlje šele, ko jo vidite in potrdite. Podrobnosti:
[PRIVACY.md](PRIVACY.md).

## Odstranitev

Odstranite vnos `fontes` iz nastavitev MCP svoje aplikacije (v Claude Code:
`claude mcp remove fontes`), nato aplikacijo zaprite in znova odprite.

## Dobro je vedeti

Fontes bere javne vire, večinoma spletne strani sodišč in državnih organov. Neuradne vire v
svojih odgovorih označi. Preden se zanesete na odločbo ali določbo, vedno odprite povezavo do
vira.

Če gre kaj narobe, pošljite opis tega, kar ste naredili, in napake, ki ste jo videli, na
fontesmcp@proton.me.

## Preden se zanesete na Fontes

- Fontes je raziskovalno orodje, ne pravni nasvet. Njegova uporaba nikogar ne naredi za vašega
  odvetnika.
- Zagotavlja se »tak, kot je«, brez jamstva, njegovi avtorji pa v obsegu, ki ga dopušča zakon, ne
  odgovarjajo za način uporabe. Celotni pogoji so v [licenci](../../../LICENSE) (Apache 2.0).
