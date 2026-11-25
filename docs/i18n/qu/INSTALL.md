> Kayqa makinap yanapasqan t'ikrasqam. Inglés simipi qillqasqam chaninchasqa kaq (autoritativo).

# Fontes instalay

Fontesqa IA aplicacionniykita taripana wasikunap taripayninkunata, kamachiykunatapas taripana
wasikunap, gobiernop web sitionkunapi kawsaqta maskachin, 120 aswan jurisdicciónkunapi. Sapa
kutichiymi originalman t'inkin. Huk estándar MCP servidormi, chayrayku local MCP servidorta
purichiyta atiq mayqin aplicacionpipas llamk'an: Claude Desktop, Codex, Claude Code, Cursor,
VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio, Cline, hukkunapipas.

Aplicacionniykita akllay, ruraykunanta qatiy, chaymanta [llamk'asqanta qhaway](#llamkasqanta-qhaway).

## Claude Desktop

1. Fontes `.mcpb` archivota
   [qhipa kaq lluqsiymanta](https://github.com/ykarapazar/fontes/releases/latest) uraykuchiy.
2. Iskay kuti click ruway. Claude Desktop kichanqa.
3. **Install** nisqapi click ruway.

## Codex

Huk terminalpi:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

Codex CLI, Codex IDE extensión nisqapas kay configuraciónta rakinakunku (`~/.codex/config.toml`).
[uv](#uv-nisqatam-necesitanki) nisqatam necesitanki.

## Claude Code

Huk terminalpi:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

[uv](#uv-nisqatam-necesitanki) nisqatam necesitanki.

## Huk aplicacionkuna

Kaykunap sapakamanmi [uv](#uv-nisqatam-necesitanki) nisqata necesitan. Qillqata yapay,
waqaychay, chaymanta aplicacionta wichqay hinaspa wakmanta kichay.

**Cursor:** `~/.cursor/mcp.json` (llapan proyectokunapaq) utaq `.cursor/mcp.json` (huk proyectopaq) nisqapi:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** Command Palette nisqamanta **MCP: Add Server** nisqata purichiy,
**Command (stdio)** nisqata akllay, `uvx fontes-mcp` nisqata qillqay, servidortataq `fontes` nispa
sutichay. Utaq kayta `~/.copilot/mcp-config.json` nisqaman yapay:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Ñawpaq VS Code configuracionkunaqa `.vscode/mcp.json` nisqatam llamk'achinku, chaypim hawa kaq
llaveqa `mcpServers` rantinpi `servers`.

**Gemini CLI:** huk terminalpi, `gemini mcp add -s user fontes uvx fontes-mcp`. Utaq kayta
`~/.gemini/settings.json` nisqaman yapay:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** configuración archivoykita kichay (**zed: open settings file**) hinaspa yapay:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** paña lado barrapi **Program** pestañata kichay, **Install → Edit mcp.json**
nisqapi click ruway, hinaspa yapay:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** **MCP Servers** iconopi click ruway, **Configure** pestañata kichay, **Configure MCP
Servers** nisqapi click ruway, hinaspa LM Studiopaq hina kaq `mcpServers` qillqata yapay.

**Claude Desktop, makiwan** (`.mcpb` archivop rantinpi): kaq `mcpServers` qillqata
`claude_desktop_config.json` nisqaman yapay (macOS: `~/Library/Application Support/Claude/`,
Windows: `%APPDATA%\Claude\`).

**Huk MCP aplicacionkuna** (Windsurf, hukkunapas): kikin documentacionninmi MCP
servidorninkunata maypi waqaychasqanta nin. Achkaqa kaq qillqatam chaskinku: kamachiy `uvx`,
argumento `fontes-mcp`.

Aplicación `uvx` nisqata mana tarinchu chayqa, llapan ñanninta llamk'achiy (macOS, Linux
nisqapi `which uvx` nisqam qillqan).

## uv nisqatam necesitanki

Codex, Claude Code, huk aplicacionkunapas Fontestaqa `uvx` nisqawanmi qallarichinku, chaytaq
**uv** nisqawan hamun, Astralpa huk huch'uy mana qullqiyuq llamk'anan. Instalanaykipaq,
[Astralpa yachachiyninta](https://docs.astral.sh/uv/getting-started/installation/) qhaway,
utaq purichiy:

- macOS utaq Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Llavekuna

Wakin pukyukunaqa mana qullqiyuq llavetam necesitan: [KEYS.md](KEYS.md) qhaway.

## Llamk'asqanta qhaway

Musuq rimanakuypi tapuy: *"Mayqin jurisdicciónkunapi Fontes maskanman?"* Aplicacionqa
suyukunap listanwanmi kutichinan. Mana chhayna kaptinqa, aplicacionta huk kutitawan wichqay
hinaspa wakmanta kichay.

## Huk clickllawan instalador (Mac utaq Windows)

Instaladorqa Fontesta llapan aplicacionniykikunapi huk kutillapi churan: Claude Desktop, Codex,
Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio, Cline.

**Manaraq qallarichkaspa:** kay aplicacionkunap sapakamanta tukuy-tukuyta wichqay. Kayqa
Claude Codepaqmi aswan ancha: purichkaptinqa `~/.claude.json` nisqata wakmanta qillqan,
instaladorpa tikrasqantataq paskanmanmi. Claude Codeta mana wichqayta atinkichu chayqa,
Fontestaqa `claude mcp add` nisqawan yapay ([Claude Code](#claude-code) qhaway).

**Mac**

1. Mac instaladorta (`Fontes-Installer-…-mac.zip`) [qhipa kaq
   lluqsiymanta](https://github.com/ykarapazar/fontes/releases/latest) uraykuchiy, hinaspa
   paskanaykipaq iskay kuti click ruway.
2. **Fontes Installer** nisqapi iskay kuti click ruway. Macniyki internetmanta uraykuchisqa
   aplicacionta kichanaykimanta tapusuptinki, **Open** nisqapi click ruway.
3. **Instalay** akllay, hinaspa **Allinmi** nisqapi click ruway. Churayqa yaqa huk minutotam unan.
4. Huk willakuymi churasqan aplicacionkunata rikuchin. **Tukusqa** nisqapi click ruway, chaymanta
   chay aplicacionkunata wakmanta kichay. Ñawpaqta mana kamachisqa, mana qullqiyuq llavekunata
   yapanaykipaqqa, **Llavekunata yapay** nisqapi click ruway; [Llavekuna yapay](#llavekuna-yapay)
   qhaway.

**Windows**

1. Windows instaladorta (`Fontes-Setup-….exe`) [qhipa kaq lluqsiymanta](https://github.com/ykarapazar/fontes/releases/latest) uraykuchiy, hinaspa iskay kuti click ruway.
   - Windows "Windows protected your PC" nispa rikuchiptinqa: **More info** nisqapi click
     ruway, chaymanta **Run anyway**.
2. **Instalay** nisqapi click ruway. Huk ventana kichakun, Fontesta churanqa.
3. Sutinnaq llamk'achiy yupaykunata kachananmanta tapusuptinki, mana nispaqa Enter ñit'iy.
4. Kunanpacha llavekunata yapananmanta tapusunki. Saltanaykipaq Enter ñit'iy;
   [Llavekuna yapay](#llavekuna-yapay) qhaway.
5. **Done** nisqanpi, IA aplicacionniykikunata wakmanta kichay. Huknin purichkarqaraq chayqa,
   tukuy-tukuyta wichqay (sistemap bandejanmantapas, relojpa qayllanpi) hinaspa wakmanta kichay.

Tukukuypi instaladorqa churasqan aplicacionkunap listantam rikuchin.

### Mayqin aplicacionkunapi churan

Huk aplicacionpiqa churan configuración carpetan computadoraykipi kaqtiñam. Claude Codeqa
`~/.claude.json` kaptinllam churakun. Claude Desktopqa sapa kutim churakun. Sapa aplicacionmi
huk qillqata, `fontes`, kay archivopi chaskin:

| Aplicación | Archivo (Mac, Linux) | Archivo (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, Microsoft Store versiónpa kikin copianpas |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, utaq ñawpaq versionkunapi `~/.codeium/windsurf/mcp_config.json` | `%APPDATA%\devin\mcp_config.json`, utaq `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Codeqa `~/.copilot` utaq VS Codep kikin configuración carpetan kaptinmi churakun.

Iskay aplicacionkunam huk rurayta aswan necesitanku:

- **Windsurf:** wakmanta kichaspa, Cascade nisqapi refresh ñit'iy.
- **Ñawpaq VS Code extensión ukhupi Cline:** Fontesta makiwan yapay ([Cline](#huk-aplicacionkuna) qhaway).

### Llavekuna yapay

Instalasqa qhipallamanmi, instaladorqa Francia, Estados Unidos nisqakunapaq mana qullqiyuq
llavekunata yapayta munanki chayqa tapusunki. Qhipaman yapanaykipaq utaq tikranaykipaq:

- **Mac:** **Fontes Installer** nisqata wakmanta kichay hinaspa **Llavekunata yapay utaq tikray** akllay.
- **Windows:** Start menu nisqata kichay, hinaspa **Fontes** → **Llavekunata yapay utaq tikray** akllay.

Qillqasqaykiqa pakasqam. Llavekunaqa Fontesniyuqña llapan aplicacionkunamanmi yaykunku.
Chaymanta aplicacionkunata wichqay hinaspa wakmanta kichay. Llavekunata maypi tarinaykipaq,
imatataq kicharinku: [KEYS.md](KEYS.md).

### Backupkuna, wakmanta purichiy, qichuypas

Instaladorqa `fontes` qillqallatam tikran. Huk llapan configuracionkuna, comentariokunapas
kasqanman hinam qhipakun. Huk archivota manaraq tikrachkaspa, qayllanpi huk copiata waqaychan,
`<file>.fontes-backup-<date>` sutiyuqta. Llavekunata yapasqayki qhipa copiakunaqa chay
llavekunatam apanku: mana necesitasqaykikunata qichuy. uv nisqatapas instalanmi. Wakmanta
purichiyqa mana sasachakuyniyuqmi: churasqata allichan, manataq huk imatapas tikranchu.

Fontesta qichunaykipaq, **Fontes Installer** nisqata kichay hinaspa **Qichuy** akllay (Mac), utaq
**Fontes** Settings → Apps nisqapi qichuy (Windows). `fontes` qillqata, llavekunantinta, llapan
aplicacionkunamanta qichun. Huk configuracionniykikuna, backup copiakunapas qhipakunmi.

## Musuqchaykuna

- **Instalador, `.mcpb` archivopas:** manam imatapas ruwanaykichu. P'unchawpi huk kutita,
  aplicación qallariptin, Fontesqa ch'inllamanta qhipanpi aswan musuq versiónta maskan,
  wakichintaq; aplicación hamuq kuti qallariptinmi chayta llamk'achin. Huk musuqchay mana
  uraykuchiyta atikunchu utaq mana llamk'anchu chayqa, Fontesqa llamk'aq versiónllatam
  llamk'achichkan.
- **`uvx`:** Fontesqa aswan musuq versión kaptinmi willasunki, jurisdicciónkuna listanpa
  hawanpi. Sapa kuti aswan musuq versiónta purichinaykipaq, `fontes-mcp` rantinpi `fontes-mcp@latest`
  nisqata llamk'achiy.

Kaypaqqa manam qammanta nitaq maskasqaykikunamanta imapas mayman kachakunchu.

## Privacidad

Fontesqa ñawpaqmantapachaqa manam qammanta nitaq maskasqaykikunamanta imatapas kachanchu.
Llamk'achiy yupaykunaqa qampa ari nisqaykiwanllam, pantay willakuytaq rikusqayki, ari
nisqayki qhipallam kachakun. Sut'inchaykuna: [PRIVACY.md](PRIVACY.md).

## Qichuy

Aplicacionniykip MCP configuracionninmanta `fontes` qillqata qichuy (Claude Codepi:
`claude mcp remove fontes`), chaymanta aplicacionta wichqay hinaspa wakmanta kichay.

## Yachanapaq allin

Fontesqa público pukyukunatam ñawinchan, astawanqa taripana wasikunap, gobiernop web
sitionkunata. Mana oficial kaqkunataqa kutichiyninkunapim qillqan. Manaraq huk taripayman
utaq disposiciónman confiakuchkaspa, hayk'appas pukyup t'inkinta kichay.

Imapas mana allin rinqa, ima ruwasqaykita, rikusqayki pantaytapas fontesmcp@proton.me
nisqaman qillqamuy.

## Manaraq confiakuchkaspa

- Fontesqa maskana llamk'anam, manam asesoramiento jurídicochu. Llamk'achiyqa manam pitapas
  abogadoyki kananpaq ruwanchu.
- "Kasqanman hina" (as is) qusqam, mana ima garantíayuq, ruraqninkunataq manam imayna
  llamk'achisqanmanta cuentata qunkuchu, derecho saqisqanman hina. Llapan condicionkunaqa
  [licenciapim](../../../LICENSE) (Apache 2.0).
