> Toto je strojovo podporovaný preklad. Rozhodujúce je anglické znenie.

# Inštalácia Fontes

Fontes umožňuje vašej AI aplikácii vyhľadávať súdne rozhodnutia a právne predpisy naživo na
stránkach súdov a štátnych orgánov vo viac ako 120 jurisdikciách. Každý výsledok odkazuje na
originál. Je to štandardný MCP server, takže funguje v každej aplikácii, ktorá dokáže spustiť
lokálny MCP server: Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot),
Gemini CLI, Windsurf, Zed, LM Studio, Cline a ďalšie.

Vyberte si aplikáciu, postupujte podľa jej krokov a potom
[overte, že to funguje](#overenie-že-to-funguje).

## Claude Desktop

1. Stiahnite si súbor Fontes `.mcpb` z
   [najnovšieho vydania](https://github.com/ykarapazar/fontes/releases/latest).
2. Dvakrát naň kliknite. Claude Desktop ho otvorí.
3. Kliknite na **Install**.

## Codex

V termináli:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI a rozšírenie Codex pre IDE zdieľajú toto nastavenie (`~/.codex/config.toml`).
Potrebujete [uv](#potrebujete-uv).

## Claude Code

V termináli:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Potrebujete [uv](#potrebujete-uv).

## Ďalšie aplikácie

Každá z nich potrebuje [uv](#potrebujete-uv). Pridajte záznam, uložte, potom aplikáciu ukončite
a znova otvorte.

**Cursor:** v `~/.cursor/mcp.json` (všetky projekty) alebo `.cursor/mcp.json` (jeden projekt):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** v palete príkazov (Command Palette) spustite **MCP: Add Server**,
zvoľte **Command (stdio)**, zadajte `uvx fontes-mcp` a server pomenujte `fontes`. Alebo toto pridajte
do `~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Staršie nastavenia VS Code používajú `.vscode/mcp.json`, kde je kľúč najvyššej úrovne `servers`
namiesto `mcpServers`.

**Gemini CLI:** v termináli `gemini mcp add -s user fontes uvx fontes-mcp`. Alebo toto pridajte do
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** otvorte súbor nastavení (**zed: open settings file**) a pridajte:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** v pravom bočnom paneli otvorte kartu **Program**, kliknite na **Install → Edit
mcp.json** a pridajte:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** kliknite na ikonu **MCP Servers**, otvorte kartu **Configure**, kliknite na
**Configure MCP Servers** a pridajte rovnaký záznam `mcpServers` ako pri LM Studio.

**Claude Desktop, ručne** (namiesto súboru `.mcpb`): pridajte rovnaký záznam `mcpServers` do
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Akákoľvek iná MCP aplikácia** (Windsurf a ďalšie): jej vlastná dokumentácia uvádza, kde má
uložené svoje MCP servery. Väčšina prijíma rovnaký záznam: príkaz `uvx`, argument `fontes`.

Ak aplikácia nevie nájsť `uvx`, použite jeho úplnú cestu (na macOS a Linuxe ju vypíše `which uvx`).

## Potrebujete uv

Codex, Claude Code a ostatné aplikácie spúšťajú Fontes pomocou `uvx`, ktorý sa dodáva s **uv**,
malým bezplatným nástrojom od spoločnosti Astral. Ak ho chcete nainštalovať, pozrite si
[návod od Astral](https://docs.astral.sh/uv/getting-started/installation/) alebo spustite:

- macOS alebo Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Kľúče

Niektoré zdroje vyžadujú bezplatný kľúč: pozri [KEYS.md](KEYS.md).

## Overenie, že to funguje

V novom chate sa opýtajte: *„V ktorých jurisdikciách dokáže Fontes vyhľadávať?“* Aplikácia by
mala odpovedať zoznamom krajín. Ak nie, ukončite a znova otvorte aplikáciu ešte raz.

## Inštalátor na jedno kliknutie (Mac)

Inštalátor pre Mac nastaví Fontes vo všetkých vašich aplikáciách naraz: Claude Desktop, Codex,
Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio a Cline. Inštalátor
pre Windows sa pripravuje; dovtedy použite postup pre vašu aplikáciu vyššie.

**Skôr než začnete:** každú z týchto aplikácií úplne ukončite. Najviac na tom záleží pri Claude
Code: kým beží, prepisuje `~/.claude.json` a môže zmenu inštalátora vrátiť späť. Ak Claude Code
nemôžete ukončiť, pridajte doň Fontes radšej pomocou `claude mcp add` (pozri
[Claude Code](#claude-code)).

**Mac**

1. Stiahnite si inštalátor pre Mac (`Fontes-Installer-…-mac.zip`) z
   [najnovšieho vydania](https://github.com/ykarapazar/fontes/releases/latest) a dvakrát naň
   kliknite, aby sa rozbalil.
2. Dvakrát kliknite na **Fontes Installer**. Ak sa váš Mac opýta, či otvoriť aplikáciu stiahnutú
   z internetu, kliknite na **Open**.
3. Zvoľte **Inštalovať** a kliknite na **OK**. Nastavenie trvá približne minútu.
4. Správa vypíše aplikácie, ktoré nastavil. Kliknite na **Hotovo** a potom tieto aplikácie znova
   otvorte. Ak chcete najprv pridať voliteľné bezplatné kľúče, kliknite namiesto toho na
   **Pridať kľúče**; pozri [Krok s kľúčmi](#krok-s-kľúčmi).

**Windows** (po vydaní inštalátora pre Windows)

1. Rozbaľte stiahnutý **Fontes Installer** (pravé tlačidlo → Extract All).
2. Dvakrát kliknite na **Install Fontes.cmd**.
   - Ak Windows zobrazí „Windows protected your PC“: kliknite na **More info** a potom na
     **Run anyway**.
3. Keď sa opýta, či odosielať anonymné počty použití, stlačením Enter odpoviete nie.
4. Opýta sa, či pridať kľúče teraz. Stlačením Enter to preskočíte; pozri
   [Krok s kľúčmi](#krok-s-kľúčmi).
5. Keď zobrazí **Hotovo**, znova otvorte svoje AI aplikácie. Ak niektorá ešte bežala, úplne ju
   zatvorte (aj zo systémovej oblasti pri hodinách) a znova ju otvorte.

Na konci inštalátor vypíše aplikácie, ktoré nastavil.

### Ktoré aplikácie nastaví

Aplikáciu nastaví iba vtedy, ak je priečinok s jej nastaveniami už vo vašom počítači. Claude Code
sa nastaví iba vtedy, ak existuje `~/.claude.json`. Claude Desktop sa nastaví vždy. Každá
aplikácia dostane jeden záznam, `fontes`, v tomto súbore:

| Aplikácia | Súbor (Mac a Linux) | Súbor (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json` a vlastná kópia verzie z Microsoft Store |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, v starších verziách `~/.codeium/windsurf/mcp_config.json` | `%APPDATA%\devin\mcp_config.json` alebo `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code sa nastaví, ak existuje `~/.copilot` alebo vlastný priečinok nastavení VS Code.

Dve aplikácie potrebujú ešte jeden krok:

- **Windsurf:** po opätovnom otvorení stlačte v Cascade obnovenie (refresh).
- **Cline v staršom rozšírení pre VS Code:** pridajte Fontes ručne (pozri [Cline](#ďalšie-aplikácie)).

### Krok s kľúčmi

Hneď po inštalácii inštalátor ponúkne pridanie bezplatných kľúčov pre Francúzsko a USA. Ak ich
chcete pridať alebo zmeniť neskôr:

- **Mac:** znova otvorte **Fontes Installer** a zvoľte **Pridať alebo zmeniť kľúče**.
- **Windows:** v priečinku inštalátora dvakrát kliknite na **Add or change keys.cmd**.

Písanie je skryté. Kľúče sa zapíšu do každej aplikácie, ktorá už Fontes má. Potom aplikácie
ukončite a znova otvorte. Kde kľúče získať a čo sprístupnia: [KEYS.md](KEYS.md).

### Zálohy, opakované spustenie a odstránenie

Inštalátor mení iba záznam `fontes`. Všetky ostatné nastavenia a komentáre zostanú tak, ako boli.
Skôr než zmení súbor, uloží vedľa neho kópiu s názvom `<file>.fontes-backup-<date>`. Kópie
vytvorené po pridaní kľúčov tieto kľúče obsahujú: tie, ktoré už nepotrebujete, vymažte.
Inštalátor tiež nainštaluje uv. Opätovné spustenie je bezpečné: opraví nastavenie a nič iné
nezmení.

Ak chcete Fontes odstrániť, otvorte **Fontes Installer** a zvoľte **Odstrániť** (Mac), alebo dvakrát
kliknite na **Uninstall Fontes.cmd** (Windows). Odstráni záznam `fontes` vrátane kľúčov zo všetkých
aplikácií. Vaše ostatné nastavenia a záložné kópie zostanú.

## Aktualizácie

- **Inštalátor a súbor `.mcpb`:** nemusíte robiť nič. Raz denne pri spustení aplikácie Fontes na
  pozadí skontroluje, či existuje novšia verzia, a pripraví ju; pri ďalšom spustení aplikácie ju
  použije. Ak sa aktualizáciu nepodarí stiahnuť alebo nefunguje, Fontes ďalej používa verziu,
  ktorá fungovala.
- **`uvx`:** Fontes vám oznámi, keď je k dispozícii novšia verzia, na začiatku svojho zoznamu
  jurisdikcií. Ak chcete vždy spúšťať najnovšiu verziu, použite `fontes-mcp@latest` namiesto
  `fontes`.

Na tento účel sa nikam neodosielajú žiadne informácie o vás ani o vašich vyhľadávaniach.

## Ochrana súkromia

Fontes predvolene neodosiela nič o vás ani o vašich vyhľadávaniach. Počty použití sú dobrovoľné
(opt-in) a hlásenie chyby sa odošle až potom, čo ho uvidíte a potvrdíte. Podrobnosti:
[PRIVACY.md](PRIVACY.md).

## Odstránenie

Odstráňte záznam `fontes` z MCP nastavení svojej aplikácie (v Claude Code:
`claude mcp remove fontes`), potom aplikáciu ukončite a znova otvorte.

## Dobré vedieť

Fontes číta verejné zdroje, väčšinou stránky súdov a štátnych orgánov. Neoficiálne zdroje vo
svojich odpovediach označuje. Skôr než sa budete spoliehať na rozhodnutie alebo ustanovenie,
vždy otvorte odkaz na zdroj.

Ak sa niečo pokazí, pošlite e-mailom, čo ste urobili a akú chybu ste videli, na
fontesmcp@proton.me.

## Skôr než sa na to budete spoliehať

- Fontes je výskumný nástroj, nie právne poradenstvo. Jeho používaním sa nikto nestáva vaším
  advokátom.
- Poskytuje sa „tak, ako je“, bez záruky, a jeho autori v rozsahu povolenom zákonom
  nezodpovedajú za spôsob jeho použitia. Úplné podmienky sú v [licencii](../../../LICENSE)
  (Apache 2.0).
