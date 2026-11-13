> Toto je strojově asistovaný překlad. Závazná je anglická verze.

# Instalace Fontes

Fontes umožňuje vaší aplikaci s AI vyhledávat soudní rozhodnutí a právní předpisy živě na webech
soudů a státních orgánů ve více než 120 jurisdikcích. Každý výsledek odkazuje na originál. Jde o
standardní server MCP, takže funguje v každé aplikaci, která umí spustit lokální server MCP:
Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed,
LM Studio, Cline a dalších.

Vyberte svou aplikaci, postupujte podle jejích kroků a pak [ověřte, že funguje](#ověření-funkčnosti).

## Claude Desktop

1. Stáhněte soubor Fontes `.mcpb` z
   [nejnovějšího vydání](https://github.com/ykarapazar/fontes/releases/latest).
2. Dvakrát na něj klikněte. Claude Desktop ho otevře.
3. Klikněte na **Install**.

## Codex

V terminálu:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI a rozšíření Codex pro IDE sdílejí toto nastavení (`~/.codex/config.toml`).
Potřebujete [uv](#potřebujete-uv).

## Claude Code

V terminálu:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Potřebujete [uv](#potřebujete-uv).

## Další aplikace

Každá z těchto aplikací potřebuje [uv](#potřebujete-uv). Přidejte záznam, uložte a pak aplikaci
ukončete a znovu otevřete.

**Cursor:** do `~/.cursor/mcp.json` (všechny projekty) nebo `.cursor/mcp.json` (jeden projekt):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** z Command Palette spusťte **MCP: Add Server**, zvolte
**Command (stdio)**, zadejte `uvx fontes-mcp` a server pojmenujte `fontes`. Nebo přidejte toto do
`~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Starší nastavení VS Code používají `.vscode/mcp.json`, kde je klíčem nejvyšší úrovně `servers`
místo `mcpServers`.

**Gemini CLI:** v terminálu `gemini mcp add -s user fontes uvx fontes-mcp`. Nebo přidejte toto do
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** otevřete soubor nastavení (**zed: open settings file**) a přidejte:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** v pravém postranním panelu otevřete kartu **Program**, klikněte na **Install → Edit
mcp.json** a přidejte:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** klikněte na ikonu **MCP Servers**, otevřete kartu **Configure**, klikněte na **Configure MCP
Servers** a přidejte stejný záznam `mcpServers` jako pro LM Studio.

**Claude Desktop, ručně** (místo souboru `.mcpb`): přidejte stejný záznam `mcpServers` do
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Jakákoli jiná aplikace MCP** (Windsurf a další): její vlastní dokumentace uvádí, kde ukládá své
servery MCP. Většina přijímá stejný záznam: příkaz `uvx`, argument `fontes`.

Pokud aplikace nemůže najít `uvx`, použijte úplnou cestu (v macOS a Linuxu ji vypíše `which uvx`).

## Potřebujete uv

Codex, Claude Code a další aplikace spouštějí Fontes příkazem `uvx`, který je součástí **uv**,
malého bezplatného nástroje od společnosti Astral. Pro instalaci viz
[návod společnosti Astral](https://docs.astral.sh/uv/getting-started/installation/) nebo spusťte:

- macOS nebo Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Klíče

Některé zdroje vyžadují bezplatný klíč: viz [KEYS.md](KEYS.md).

## Ověření funkčnosti

V nové konverzaci se zeptejte: *„Které jurisdikce umí Fontes prohledávat?“* Aplikace by měla
odpovědět seznamem zemí. Pokud ne, ukončete ji a znovu otevřete ještě jednou.

## Instalátor na jedno kliknutí (připravujeme)

Připravujeme instalátor pro Mac a Windows, který nastaví Fontes ve všech vašich aplikacích
najednou. Nastavuje Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot),
Windsurf, Gemini CLI, Zed, LM Studio a Cline. Až bude vydán:

**Než začnete:** každou z těchto aplikací úplně ukončete. Nejvíc na tom záleží u Claude Code:
zatímco běží, přepisuje `~/.claude.json` a může vrátit změnu provedenou instalátorem. Pokud
Claude Code ukončit nemůžete, přidejte do něj Fontes příkazem `claude mcp add` (viz
[Claude Code](#claude-code)).

**Mac**

1. Otevřete staženou složku **Fontes Installer**.
2. Dvakrát klikněte na **Install Fontes.command**.
   - Pokud váš Mac hlásí, že soubor "cannot be opened because it is from an unidentified developer":
     klikněte na soubor pravým tlačítkem (nebo se stisknutou klávesou Control), zvolte **Open** a pak znovu **Open**.
     Stačí to udělat jednou.
3. Otevře se okno s dotazem, zda chcete posílat anonymní počty použití; pro ne stiskněte Enter.
4. Zeptá se, zda chcete teď přidat klíče. Stisknutím Enter krok přeskočíte; viz
   [Krok s klíči](#krok-s-klíči).
5. Když se zobrazí **Hotovo**, znovu otevřete své aplikace s AI.

**Windows**

1. Rozbalte stažený **Fontes Installer** (pravé tlačítko → Extract All).
2. Dvakrát klikněte na **Install Fontes.cmd**.
   - Pokud Windows zobrazí "Windows protected your PC": klikněte na **More info** a pak na **Run anyway**.
3. Když se zeptá, zda chcete posílat anonymní počty použití, pro ne stiskněte Enter.
4. Zeptá se, zda chcete teď přidat klíče. Stisknutím Enter krok přeskočíte; viz
   [Krok s klíči](#krok-s-klíči).
5. Když se zobrazí **Hotovo**, znovu otevřete své aplikace s AI. Pokud některá ještě běžela,
   úplně ji ukončete (i z oznamovací oblasti u hodin) a znovu otevřete.

Na konci instalátor vypíše aplikace, které nastavil.

### Které aplikace nastavuje

Aplikaci nastaví pouze tehdy, když je složka s jejím nastavením už ve vašem počítači. Claude Code
nastaví pouze tehdy, když existuje `~/.claude.json`. Claude Desktop nastaví vždy. Každá aplikace
dostane jeden záznam, `fontes`, v tomto souboru:

| Aplikace | Soubor (Mac a Linux) | Soubor (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json` a vlastní kopie verze z Microsoft Store |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, ve starších verzích `~/.codeium/windsurf/mcp_config.json` | `%APPDATA%\devin\mcp_config.json` nebo `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code se nastaví, pokud existuje `~/.copilot` nebo vlastní složka nastavení VS Code.

Dvě aplikace vyžadují ještě jeden krok:

- **Windsurf:** po opětovném otevření stiskněte v Cascade obnovení.
- **Cline ve starším rozšíření pro VS Code:** přidejte Fontes ručně (viz
  [Cline](#další-aplikace)).

### Krok s klíči

Hned po instalaci instalátor nabídne přidání bezplatných klíčů pro Francii a USA. Chcete-li je
přidat nebo změnit později:

- **Mac:** dvakrát klikněte na **Add or change keys.command** ve složce instalátoru nebo znovu
  otevřete aplikaci Fontes Installer a zvolte **Přidat nebo změnit klíče**.
- **Windows:** dvakrát klikněte na **Add or change keys.cmd** ve složce instalátoru.

Psaný text není vidět. Klíče se zapíšou do každé aplikace, která už Fontes má. Poté aplikace
ukončete a znovu otevřete. Kde klíče získat a co zpřístupní: [KEYS.md](KEYS.md).

### Zálohy, opakované spuštění a odebrání

Instalátor mění pouze záznam `fontes`. Všechna ostatní nastavení a komentáře zůstávají, jak byly.
Před změnou souboru uloží vedle něj kopii s názvem `<file>.fontes-backup-<date>`. Kopie vytvořené
po přidání klíčů tyto klíče obsahují: smažte ty, které už nepotřebujete. Nainstaluje také uv.
Opakované spuštění je bezpečné: opraví nastavení a nic jiného nezmění.

Chcete-li Fontes odebrat, dvakrát klikněte na **Uninstall Fontes.command** (Mac) nebo
**Uninstall Fontes.cmd** (Windows). Odebere záznam `fontes` včetně klíčů z každé aplikace. Vaše
ostatní nastavení a zálohy zůstanou.

## Aktualizace

- **Instalátor a soubor `.mcpb`:** nemusíte nic dělat. Jednou denně, když se aplikace spustí,
  Fontes na pozadí zkontroluje, zda existuje novější verze, a připraví ji; při příštím spuštění
  aplikace použije ji. Pokud aktualizaci nelze stáhnout nebo nefunguje, Fontes dál používá verzi,
  která fungovala.
- **`uvx`:** Fontes vás na začátku svého seznamu jurisdikcí upozorní, když je k dispozici novější
  verze. Chcete-li vždy spouštět nejnovější verzi, použijte `fontes-mcp@latest` místo `fontes-mcp`.

Nikam se přitom neposílají žádné informace o vás ani o vašich vyhledáváních.

## Ochrana soukromí

Fontes ve výchozím stavu neposílá nic o vás ani o vašich vyhledáváních. Počty použití se posílají
pouze s vaším souhlasem (opt-in) a hlášení chyby se odešle teprve poté, co ho uvidíte a potvrdíte.
Podrobnosti: [PRIVACY.md](PRIVACY.md).

## Odebrání

Odeberte záznam `fontes` z nastavení MCP své aplikace (v Claude Code:
`claude mcp remove fontes`) a pak aplikaci ukončete a znovu otevřete.

## Dobré vědět

Fontes čte veřejné zdroje, převážně weby soudů a státních orgánů. Neoficiální zdroje ve svých
odpovědích označuje. Než se spolehnete na rozhodnutí nebo ustanovení, vždy otevřete odkaz na
zdroj.

Pokud se něco pokazí, pošlete popis toho, co jste udělali, a chyby, kterou jste viděli, na
fontesmcp@proton.me.

## Než se na Fontes spolehnete

- Fontes je rešeršní nástroj, ne právní poradenství. Jeho používáním se nikdo nestává vaším
  advokátem.
- Poskytuje se „tak, jak je“, bez záruky, a jeho autoři v rozsahu, který zákon dovoluje,
  neodpovídají za to, jak je používán. Úplné podmínky jsou v [licenci](../../../LICENSE)
  (Apache 2.0).
