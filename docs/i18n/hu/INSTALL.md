> Ez gépi segítséggel készült fordítás. Az angol változat az irányadó.

# A Fontes telepítése

A Fontes lehetővé teszi, hogy az MI-alkalmazása közvetlenül bírósági és állami webhelyeken
keressen bírósági határozatokat és jogszabályokat, több mint 120 joghatóságban. Minden találat
az eredetire hivatkozik. Szabványos MCP-szerver, így minden olyan alkalmazásban működik, amely
helyi MCP-szervert tud futtatni: Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub
Copilot), Gemini CLI, Windsurf, Zed, LM Studio, Cline és mások.

**A Fontes még nincs fent a PyPI-n.** Az alábbi lépések az első kiadás megjelenése után működnek.

Válassza ki az alkalmazását, kövesse a lépéseit, majd
[ellenőrizze, hogy működik](#a-működés-ellenőrzése).

## Claude Desktop

1. Töltse le a Fontes `.mcpb` fájlját a
   [legújabb kiadásból](https://github.com/ykarapazar/fontes/releases/latest).
2. Kattintson rá duplán. A Claude Desktop megnyitja.
3. Kattintson az **Install** gombra.

## Codex

Egy terminálban:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

A Codex CLI és a Codex IDE-bővítmény ugyanezt a beállítást használja (`~/.codex/config.toml`).
Szüksége lesz az [uv](#szüksége-lesz-az-uv-re)-re.

## Claude Code

Egy terminálban:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Szüksége lesz az [uv](#szüksége-lesz-az-uv-re)-re.

## Egyéb alkalmazások

Mindegyikhez szükség van az [uv](#szüksége-lesz-az-uv-re)-re. Adja hozzá a bejegyzést, mentsen,
majd lépjen ki az alkalmazásból, és nyissa meg újra.

**Cursor:** a `~/.cursor/mcp.json` fájlban (minden projekt) vagy a `.cursor/mcp.json` fájlban
(egy projekt):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** futtassa az **MCP: Add Server** parancsot a Command Palette-ből,
válassza a **Command (stdio)** lehetőséget, írja be: `uvx fontes-mcp`, és nevezze el a szervert így:
`fontes`. Vagy adja hozzá ezt a `~/.copilot/mcp-config.json` fájlhoz:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

A régebbi VS Code-beállítások a `.vscode/mcp.json` fájlt használják, ahol a legfelső szintű kulcs
`servers`, nem pedig `mcpServers`.

**Gemini CLI:** egy terminálban: `gemini mcp add -s user fontes uvx fontes-mcp`. Vagy adja hozzá ezt a
`~/.gemini/settings.json` fájlhoz:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** nyissa meg a beállításfájlt (**zed: open settings file**), és adja hozzá:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** a jobb oldali sávban nyissa meg a **Program** fület, kattintson az **Install → Edit
mcp.json** elemre, és adja hozzá:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** kattintson az **MCP Servers** ikonra, nyissa meg a **Configure** fület, kattintson a
**Configure MCP Servers** elemre, és adja hozzá ugyanazt az `mcpServers` bejegyzést, mint az LM
Studio esetében.

**Claude Desktop, kézzel** (a `.mcpb` fájl helyett): adja hozzá ugyanazt az `mcpServers`
bejegyzést a `claude_desktop_config.json` fájlhoz (macOS: `~/Library/Application Support/Claude/`,
Windows: `%APPDATA%\Claude\`).

**Bármely más MCP-alkalmazás** (Windsurf és mások): a saját dokumentációja megadja, hol tárolja
az MCP-szervereit. A legtöbb ugyanazt a bejegyzést fogadja el: parancs `uvx`, argumentum `fontes`.

Ha az alkalmazás nem találja az `uvx`-et, használja a teljes elérési útját (macOS-en és Linuxon a
`which uvx` kiírja).

## Szüksége lesz az uv-re

A Codex, a Claude Code és a többi alkalmazás az `uvx` segítségével indítja a Fontest, amely az
**uv** része: ez az Astral kicsi, ingyenes eszköze. A telepítéshez lásd
[az Astral útmutatóját](https://docs.astral.sh/uv/getting-started/installation/), vagy futtassa:

- macOS vagy Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Kulcsok

Egyes forrásokhoz ingyenes kulcs kell: lásd [KEYS.md](KEYS.md).

## A működés ellenőrzése

Egy új csevegésben kérdezze meg: *„Mely joghatóságokban tud keresni a Fontes?”* Az
alkalmazásnak az országok listájával kell válaszolnia. Ha nem így történik, lépjen ki az
alkalmazásból, és nyissa meg még egyszer.

## Egykattintásos telepítő (készülőben)

Készülőben van egy Mac- és Windows-telepítő, amely egyszerre az összes alkalmazásában beállítja
a Fontest. Beállítja a Claude Desktopot, a Codexet, a Claude Code-ot, a Cursort, a VS Code-ot
(GitHub Copilot), a Windsurfot, a Gemini CLI-t, a Zedet, az LM Studiót és a Cline-t. Amint
megjelenik:

**Mielőtt elkezdené:** lépjen ki teljesen ezekből az alkalmazásokból. Ez a Claude Code esetében
a legfontosabb: futás közben újraírja a `~/.claude.json` fájlt, és visszavonhatja a telepítő
módosítását. Ha nem tud kilépni a Claude Code-ból, inkább a `claude mcp add` paranccsal adja
hozzá a Fontest (lásd [Claude Code](#claude-code)).

**Mac**

1. Nyissa meg a letöltött **Fontes Installer** mappát.
2. Kattintson duplán az **Install Fontes.command** fájlra.
   - Ha a Mac azt írja, hogy „nem nyitható meg, mert azonosítatlan fejlesztőtől származik”:
     kattintson a jobb gombbal (vagy Control-kattintással) a fájlra, válassza az **Open**
     lehetőséget, majd ismét az **Open** gombot. Ezt csak egyszer kell megtennie.
3. Megnyílik egy ablak, és megkérdezi, küldjön-e névtelen használati számadatokat; a „nem”
   válaszhoz nyomja meg az Entert.
4. Megkérdezi, hogy most adja-e hozzá a kulcsokat. Kihagyáshoz nyomja meg az Entert; lásd
   [A kulcsok megadása](#a-kulcsok-megadása).
5. Amikor kiírja, hogy **Done**, nyissa meg újra az MI-alkalmazásait.

**Windows**

1. Csomagolja ki a letöltött **Fontes Installer** fájlt (jobb gomb → Extract All).
2. Kattintson duplán az **Install Fontes.cmd** fájlra.
   - Ha a Windows azt írja ki, hogy „Windows protected your PC”: kattintson a **More info**,
     majd a **Run anyway** gombra.
3. Amikor megkérdezi, küldjön-e névtelen használati számadatokat, a „nem” válaszhoz nyomja meg
   az Entert.
4. Megkérdezi, hogy most adja-e hozzá a kulcsokat. Kihagyáshoz nyomja meg az Entert; lásd
   [A kulcsok megadása](#a-kulcsok-megadása).
5. Amikor kiírja, hogy **Done**, nyissa meg újra az MI-alkalmazásait. Ha valamelyik még futott,
   zárja be teljesen (a tálcán, az óra mellett is), majd nyissa meg újra.

A végén a telepítő felsorolja, mely alkalmazásokat állította be.

### Mely alkalmazásokat állítja be

Egy alkalmazást csak akkor állít be, ha annak beállításmappája már megtalálható a
számítógépén. A Claude Code-ot csak akkor állítja be, ha létezik a `~/.claude.json` fájl. A
Claude Desktopot mindig beállítja. Minden alkalmazás egyetlen bejegyzést kap, `fontes` néven, a
következő fájlban:

| Alkalmazás | Fájl (Mac és Linux) | Fájl (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, valamint a Microsoft Store-verzió saját példánya |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, régebbi verziókon `~/.codeium/windsurf/mcp_config.json` | `%APPDATA%\devin\mcp_config.json` vagy `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

A VS Code-ot akkor állítja be, ha létezik a `~/.copilot` mappa vagy a VS Code saját
beállításmappája.

Két alkalmazás egy további lépést igényel:

- **Windsurf:** újranyitás után nyomja meg a frissítést a Cascade-ben.
- **Cline a régebbi VS Code-bővítményben:** adja hozzá kézzel a Fontest (lásd
  [Cline](#egyéb-alkalmazások)).

### A kulcsok megadása

Közvetlenül a telepítés után a telepítő felajánlja az ingyenes francia és egyesült államokbeli
kulcsok hozzáadását. Későbbi hozzáadásukhoz vagy módosításukhoz:

- **Mac:** kattintson duplán az **Add or change keys.command** fájlra a telepítő mappájában, vagy
  nyissa meg újra a Fontes Installer alkalmazást, és válassza az **Add or change keys**
  lehetőséget.
- **Windows:** kattintson duplán az **Add or change keys.cmd** fájlra a telepítő mappájában.

A begépelt szöveg rejtve marad. A kulcsok minden olyan alkalmazásba bekerülnek, amelyben már
megvan a Fontes. Utána lépjen ki az alkalmazásokból, és nyissa meg őket újra. Honnan szerezheti
be a kulcsokat, és mit tesznek elérhetővé: [KEYS.md](KEYS.md).

### Biztonsági másolatok, újrafuttatás és eltávolítás

A telepítő csak a `fontes` bejegyzést módosítja. Minden más beállítás és megjegyzés változatlan
marad. Mielőtt módosít egy fájlt, másolatot ment mellé `<file>.fontes-backup-<date>` néven. A
kulcsok hozzáadása után készült másolatok tartalmazzák ezeket a kulcsokat: törölje azokat,
amelyekre már nincs szüksége. Az uv-t is telepíti. Az újrafuttatás biztonságos: helyreállítja a
beállítást, és semmi mást nem módosít.

A Fontes eltávolításához kattintson duplán az **Uninstall Fontes.command** (Mac) vagy az
**Uninstall Fontes.cmd** (Windows) fájlra. Ez minden alkalmazásból eltávolítja a `fontes`
bejegyzést, a kulcsokkal együtt. A többi beállítása és a biztonsági másolatok megmaradnak.

## Frissítések

- **Telepítő és `.mcpb` fájl:** nincs teendője. Naponta egyszer, amikor az alkalmazás elindul, a
  Fontes a háttérben ellenőrzi, van-e újabb verzió, és előkészíti; az alkalmazás következő
  indításakor már azt használja. Ha egy frissítés nem tölthető le, vagy nem működik, a Fontes
  tovább használja a működő verziót.
- **`uvx`:** a Fontes a joghatóságok listájának tetején jelzi, ha újabb verzió érhető el. Ha
  mindig a legújabb verziót szeretné futtatni, a `fontes-mcp` helyett használja a `fontes-mcp@latest`
  formát.

Ehhez semmilyen információ nem kerül elküldésre Önről vagy a kereséseiről.

## Adatvédelem

A Fontes alapértelmezés szerint semmit sem küld Önről vagy a kereséseiről. A használati
számadatok csak kifejezett hozzájárulással (opt-in) kerülnek elküldésre, a hibajelentés pedig
csak azután, hogy Ön látta és megerősítette. Részletek: [PRIVACY.md](PRIVACY.md).

## Eltávolítás

Távolítsa el a `fontes` bejegyzést az alkalmazás MCP-beállításaiból (a Claude Code-ban:
`claude mcp remove fontes`), majd lépjen ki az alkalmazásból, és nyissa meg újra.

## Jó tudni

A Fontes nyilvános forrásokat olvas, többnyire bírósági és állami webhelyeket. A nem hivatalos
forrásokat a válaszaiban megjelöli. Mielőtt egy határozatra vagy rendelkezésre hagyatkozna,
mindig nyissa meg a forrás hivatkozását.

Ha valami nem működik, írja meg, mit csinált, és milyen hibát látott, a fontesmcp@proton.me
címre.

## Mielőtt hagyatkozna rá

- A Fontes kutatási eszköz, nem jogi tanács. Használata révén senki sem lesz az Ön ügyvédje.
- „Ahogy van” („as is”) alapon, mindenféle szavatosság nélkül áll rendelkezésre, és szerzői a
  jogszabályok által megengedett mértékben nem felelnek a felhasználás módjáért. A teljes
  feltételeket a [licenc](../../../LICENSE) (Apache 2.0) tartalmazza.
