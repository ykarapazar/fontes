> To jest tłumaczenie wspomagane maszynowo. Wiążąca jest wersja angielska.

# Instalacja Fontes

Fontes pozwala Twojej aplikacji AI wyszukiwać orzeczenia sądów i akty prawne na żywo na stronach
sądów i instytucji państwowych w ponad 120 jurysdykcjach. Każdy wynik zawiera link do oryginału.
Jest to standardowy serwer MCP, więc działa w każdej aplikacji, która potrafi uruchomić lokalny
serwer MCP: Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Gemini CLI,
Windsurf, Zed, LM Studio, Cline i innych.

Wybierz swoją aplikację, wykonaj jej kroki, a następnie
[sprawdź, czy działa](#sprawdzenie-czy-działa).

## Claude Desktop

1. Pobierz plik Fontes `.mcpb` z
   [najnowszego wydania](https://github.com/ykarapazar/fontes/releases/latest).
2. Kliknij go dwukrotnie. Claude Desktop go otworzy.
3. Kliknij **Install**.

## Codex

W terminalu:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI i rozszerzenie Codex dla IDE współdzielą to ustawienie (`~/.codex/config.toml`).
Potrzebujesz [uv](#potrzebujesz-uv).

## Claude Code

W terminalu:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Potrzebujesz [uv](#potrzebujesz-uv).

## Inne aplikacje

Każda z nich potrzebuje [uv](#potrzebujesz-uv). Dodaj wpis, zapisz, a następnie zamknij i otwórz
ponownie aplikację.

**Cursor:** w `~/.cursor/mcp.json` (wszystkie projekty) lub `.cursor/mcp.json` (jeden projekt):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** uruchom **MCP: Add Server** z palety poleceń (Command Palette),
wybierz **Command (stdio)**, wpisz `uvx fontes-mcp` i nazwij serwer `fontes`. Albo dodaj to do
`~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Starsze konfiguracje VS Code używają `.vscode/mcp.json`, gdzie kluczem najwyższego poziomu jest
`servers` zamiast `mcpServers`.

**Gemini CLI:** w terminalu `gemini mcp add -s user fontes uvx fontes-mcp`. Albo dodaj to do
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** otwórz plik ustawień (**zed: open settings file**) i dodaj:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** na prawym pasku bocznym otwórz kartę **Program**, kliknij **Install → Edit
mcp.json** i dodaj:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** kliknij ikonę **MCP Servers**, otwórz kartę **Configure**, kliknij **Configure MCP
Servers** i dodaj ten sam wpis `mcpServers` co w przypadku LM Studio.

**Claude Desktop, ręcznie** (zamiast pliku `.mcpb`): dodaj ten sam wpis `mcpServers` do
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Każda inna aplikacja MCP** (Windsurf i inne): jej własna dokumentacja podaje, gdzie
przechowuje swoje serwery MCP. Większość przyjmuje ten sam wpis: polecenie `uvx`, argument
`fontes-mcp`.

Jeśli aplikacja nie może znaleźć `uvx`, użyj jego pełnej ścieżki (w systemach macOS i Linux
wyświetla ją `which uvx`).

## Potrzebujesz uv

Codex, Claude Code i inne aplikacje uruchamiają Fontes za pomocą `uvx`, który jest dostarczany z
**uv**, małym bezpłatnym narzędziem firmy Astral. Aby je zainstalować, zobacz
[przewodnik Astral](https://docs.astral.sh/uv/getting-started/installation/) albo uruchom:

- macOS lub Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Klucze

Niektóre źródła wymagają bezpłatnego klucza: zobacz [KEYS.md](KEYS.md).

## Sprawdzenie, czy działa

W nowym czacie zapytaj: *„W jakich jurysdykcjach może wyszukiwać Fontes?”* Aplikacja powinna
odpowiedzieć listą krajów. Jeśli tak się nie stanie, zamknij i otwórz aplikację jeszcze raz.

## Instalator jednym kliknięciem (Mac i Windows)

Instalator konfiguruje Fontes we wszystkich Twoich aplikacjach naraz: Claude Desktop,
Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio i Cline.

**Zanim zaczniesz:** całkowicie zamknij każdą z tych aplikacji. Najważniejsze jest to w przypadku
Claude Code: gdy działa, nadpisuje `~/.claude.json` i może cofnąć zmianę wprowadzoną przez
instalator. Jeśli nie możesz zamknąć Claude Code, dodaj do niego Fontes za pomocą
`claude mcp add` (zobacz [Claude Code](#claude-code)).

**Mac**

1. Pobierz instalator dla komputerów Mac (`Fontes-Installer-…-mac.zip`) z
   [najnowszego wydania](https://github.com/ykarapazar/fontes/releases/latest) i kliknij go
   dwukrotnie, aby go rozpakować.
2. Kliknij dwukrotnie **Fontes Installer**. Jeśli Twój Mac zapyta, czy otworzyć aplikację pobraną
   z internetu, kliknij **Open**.
3. Wybierz **Zainstaluj** i kliknij **OK**. Konfiguracja trwa około minuty.
4. Komunikat wyświetli listę skonfigurowanych aplikacji. Kliknij **Gotowe**, a następnie ponownie
   otwórz te aplikacje. Aby najpierw dodać opcjonalne bezpłatne klucze, kliknij zamiast tego
   **Dodaj klucze**; zobacz [Krok z kluczami](#krok-z-kluczami).

**Windows**

1. Pobierz instalator dla systemu Windows (`Fontes-Setup-….exe`) z
   [najnowszego wydania](https://github.com/ykarapazar/fontes/releases/latest) i kliknij go dwukrotnie.
   - Jeśli Windows wyświetli „Windows protected your PC”: kliknij **More info**, a następnie
     **Run anyway**.
2. Kliknij **Zainstaluj**. Otworzy się okno i skonfiguruje Fontes.
3. Gdy pojawi się pytanie, czy wysyłać anonimowe liczniki użycia, naciśnij Enter, aby
   odpowiedzieć „nie”.
4. Zapyta, czy dodać klucze teraz. Naciśnij Enter, aby pominąć; zobacz
   [Krok z kluczami](#krok-z-kluczami).
5. Gdy wyświetli **Gotowe**, ponownie otwórz swoje aplikacje AI. Jeśli któraś nadal działała,
   zamknij ją całkowicie (także z zasobnika systemowego obok zegara) i otwórz ponownie.

Na końcu instalator wyświetla listę skonfigurowanych aplikacji.

### Które aplikacje konfiguruje

Konfiguruje aplikację tylko wtedy, gdy folder jej ustawień już istnieje na Twoim komputerze.
Claude Code jest konfigurowany tylko wtedy, gdy istnieje `~/.claude.json`. Claude Desktop jest
konfigurowany zawsze. Każda aplikacja otrzymuje jeden wpis, `fontes`, w tym pliku:

| Aplikacja | Plik (Mac i Linux) | Plik (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json` oraz własna kopia wersji z Microsoft Store |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, w starszych wersjach `~/.codeium/windsurf/mcp_config.json` | `%APPDATA%\devin\mcp_config.json` lub `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code jest konfigurowany, jeśli istnieje `~/.copilot` lub własny folder ustawień VS Code.

Dwie aplikacje wymagają jeszcze jednego kroku:

- **Windsurf:** po ponownym otwarciu naciśnij odświeżanie (refresh) w Cascade.
- **Cline w starszym rozszerzeniu VS Code:** dodaj Fontes ręcznie (zobacz [Cline](#inne-aplikacje)).

### Krok z kluczami

Zaraz po instalacji instalator proponuje dodanie bezpłatnych kluczy dla Francji i USA. Aby dodać
je lub zmienić później:

- **Mac:** ponownie otwórz **Fontes Installer** i wybierz **Dodaj lub zmień klucze**.
- **Windows:** otwórz menu Start, a następnie wybierz **Fontes** → **Dodaj lub zmień klucze**.

Wpisywane znaki są ukryte. Klucze trafiają do każdej aplikacji, która ma już Fontes. Następnie
zamknij i otwórz ponownie aplikacje. Skąd wziąć klucze i co udostępniają: [KEYS.md](KEYS.md).

### Kopie zapasowe, ponowne uruchomienie i usuwanie

Instalator zmienia tylko wpis `fontes`. Wszystkie inne ustawienia i komentarze pozostają bez
zmian. Zanim zmieni plik, zapisuje obok niego kopię o nazwie `<file>.fontes-backup-<date>`.
Kopie utworzone po dodaniu kluczy zawierają te klucze: usuń te, których już nie potrzebujesz.
Instaluje też uv. Ponowne uruchomienie jest bezpieczne: naprawia konfigurację i niczego innego
nie zmienia.

Aby usunąć Fontes, otwórz **Fontes Installer** i wybierz **Usuń** (Mac) lub odinstaluj
**Fontes** w Ustawienia → Aplikacje (Windows). Usuwa on wpis `fontes`, łącznie z kluczami, ze wszystkich
aplikacji. Twoje pozostałe ustawienia i kopie zapasowe pozostają.

## Aktualizacje

- **Instalator i plik `.mcpb`:** nie musisz nic robić. Raz dziennie, przy uruchomieniu aplikacji,
  Fontes sprawdza w tle, czy jest nowsza wersja, i ją przygotowuje; przy następnym uruchomieniu
  aplikacja z niej korzysta. Jeśli aktualizacji nie da się pobrać lub nie działa, Fontes nadal
  używa wersji, która działała.
- **`uvx`:** Fontes informuje Cię o dostępności nowszej wersji na początku swojej listy
  jurysdykcji. Aby zawsze uruchamiać najnowszą wersję, użyj `fontes-mcp@latest` zamiast `fontes-mcp`.

W tym celu nigdzie nie są wysyłane żadne informacje o Tobie ani o Twoich wyszukiwaniach.

## Prywatność

Fontes domyślnie nie wysyła niczego o Tobie ani o Twoich wyszukiwaniach. Liczniki użycia są
dobrowolne (opt-in), a zgłoszenie błędu zostaje wysłane dopiero wtedy, gdy je zobaczysz i
potwierdzisz. Szczegóły: [PRIVACY.md](PRIVACY.md).

## Usuwanie

Usuń wpis `fontes` z ustawień MCP swojej aplikacji (w Claude Code: `claude mcp remove fontes`),
a następnie zamknij i otwórz ponownie aplikację.

## Warto wiedzieć

Fontes czyta źródła publiczne, głównie strony sądów i instytucji państwowych. Źródła nieoficjalne
oznacza w swoich odpowiedziach. Zanim zaufasz orzeczeniu lub przepisowi, zawsze otwórz link do
źródła.

Jeśli coś pójdzie nie tak, napisz na fontesmcp@proton.me, co zrobiłeś i jaki błąd się pojawił.

## Zanim na nim polegasz

- Fontes jest narzędziem badawczym, a nie poradą prawną. Korzystanie z niego nie czyni nikogo
  Twoim prawnikiem.
- Jest udostępniany „w stanie, w jakim jest” („as is”), bez gwarancji, a jego autorzy, w
  granicach dozwolonych przez prawo, nie ponoszą odpowiedzialności za sposób jego wykorzystania.
  Pełne warunki znajdują się w [licencji](../../../LICENSE) (Apache 2.0).
