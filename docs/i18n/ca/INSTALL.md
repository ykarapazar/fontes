> Aquesta és una traducció assistida per màquina. La versió anglesa és la que preval.

# Com instal·lar Fontes

Fontes permet que la vostra aplicació d'IA consulti resolucions judicials i legislació en directe des
de llocs web judicials i governamentals de 125 jurisdiccions. Cada resultat enllaça amb
l'original. És un servidor MCP estàndard, de manera que funciona en qualsevol aplicació que pugui
executar un servidor MCP local: Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot),
Gemini CLI, Windsurf, Zed, LM Studio, Cline i altres.

Trieu la vostra aplicació, seguiu-ne els passos i després
[comproveu que funciona](#comprovar-que-funciona).

## Claude Desktop

1. Baixeu el fitxer `.mcpb` de Fontes de la
   [darrera versió](https://github.com/ykarapazar/fontes/releases/latest).
2. Feu-hi doble clic. Claude Desktop l'obre.
3. Feu clic a **Install**.

## Codex

En un terminal:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

La CLI de Codex i l'extensió de Codex per a IDE comparteixen aquesta configuració
(`~/.codex/config.toml`). Necessiteu [uv](#necessiteu-uv).

## Claude Code

En un terminal:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Necessiteu [uv](#necessiteu-uv).

## Altres aplicacions

Cadascuna d'aquestes necessita [uv](#necessiteu-uv). Afegiu l'entrada, deseu i després tanqueu i
torneu a obrir l'aplicació.

**Cursor:** a `~/.cursor/mcp.json` (tots els projectes) o `.cursor/mcp.json` (un projecte):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** executeu **MCP: Add Server** des de la paleta d'ordres (Command
Palette), trieu **Command (stdio)**, introduïu `uvx fontes-mcp` i anomeneu el servidor `fontes`. O afegiu
això a `~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Les configuracions més antigues de VS Code fan servir `.vscode/mcp.json`, on la clau de primer nivell
és `servers` en lloc de `mcpServers`.

**Gemini CLI:** en un terminal, `gemini mcp add -s user fontes uvx fontes-mcp`. O afegiu això a
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** obriu el fitxer de configuració (**zed: open settings file**) i afegiu:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** a la barra lateral dreta, obriu la pestanya **Program**, feu clic a **Install → Edit
mcp.json** i afegiu:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** feu clic a la icona **MCP Servers**, obriu la pestanya **Configure**, feu clic a
**Configure MCP Servers** i afegiu la mateixa entrada `mcpServers` que a LM Studio.

**Claude Desktop, manualment** (en lloc del fitxer `.mcpb`): afegiu la mateixa entrada `mcpServers` a
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Qualsevol altra aplicació MCP** (Windsurf i altres): la documentació de l'aplicació indica on desa
els seus servidors MCP. La majoria accepten la mateixa entrada: ordre `uvx`, argument `fontes-mcp`.

Si l'aplicació no troba `uvx`, feu servir el seu camí complet (a macOS i Linux, `which uvx` el
mostra).

## Necessiteu uv

Codex, Claude Code i les altres aplicacions inicien Fontes amb `uvx`, que ve amb **uv**, una petita
eina gratuïta d'Astral. Per instal·lar-la, vegeu la
[guia d'Astral](https://docs.astral.sh/uv/getting-started/installation/) o executeu:

- macOS o Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Claus

Algunes fonts necessiten una clau gratuïta: vegeu [KEYS.md](KEYS.md).

## Comprovar que funciona

En un xat nou, pregunteu: *«En quines jurisdiccions pot cercar Fontes?»* L'aplicació hauria de
respondre amb una llista de països. Si no ho fa, tanqueu i torneu a obrir l'aplicació un cop més.

## Instal·lador d'un clic (Mac i Windows)

L'instal·lador configura Fontes a totes les vostres aplicacions alhora: Claude Desktop,
Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio i Cline.

**Abans de començar:** tanqueu completament cadascuna d'aquestes aplicacions. És més important per a
Claude Code: mentre s'executa, reescriu `~/.claude.json` i pot desfer el canvi de l'instal·lador. Si
no podeu tancar Claude Code, afegiu-hi Fontes amb `claude mcp add` (vegeu
[Claude Code](#claude-code)).

**Mac**

1. Baixeu l'instal·lador per a Mac (`Fontes-Installer-…-mac.zip`) de la [darrera
   versió](https://github.com/ykarapazar/fontes/releases/latest) i feu-hi doble clic per
   descomprimir-lo.
2. Feu doble clic a **Fontes Installer**. Si el Mac us pregunta si voleu obrir una aplicació baixada
   d'internet, feu clic a **Obre**.
3. Trieu **Instal·la** i feu clic a **D'acord**. La configuració triga aproximadament un minut.
4. Un missatge llista les aplicacions que ha configurat. Feu clic a **Fet** i torneu a obrir
   aquestes aplicacions. Per afegir primer les claus gratuïtes opcionals, feu clic a **Afegeix
   claus**; vegeu [El pas de les claus](#el-pas-de-les-claus).

**Windows**

1. Baixeu l'instal·lador per a Windows (`Fontes-Setup-….exe`) de la [darrera versió](https://github.com/ykarapazar/fontes/releases/latest) i feu-hi doble clic.
   - Si Windows mostra "Windows protected your PC": feu clic a **More info** i després a
     **Run anyway**.
2. Feu clic a **Instal·la**. S'obre una finestra i configura Fontes.
3. Quan us pregunti si s'han d'enviar recomptes d'ús anònims, premeu Retorn per dir que no.
4. Pregunta si voleu afegir claus ara. Premeu Retorn per ometre-ho; vegeu
   [El pas de les claus](#el-pas-de-les-claus).
5. Quan aparegui **Fet**, torneu a obrir les vostres aplicacions d'IA. Si alguna encara s'executava,
   tanqueu-la completament (també a la safata del sistema, prop del rellotge) i torneu-la a obrir.

Al final, l'instal·lador llista les aplicacions que ha configurat.

### Quines aplicacions configura

Configura una aplicació només si la carpeta de configuració d'aquesta aplicació ja existeix a
l'ordinador. Claude Code només es configura si existeix `~/.claude.json`. Claude Desktop es configura
sempre. Cada aplicació rep una entrada, `fontes`, en aquest fitxer:

| Aplicació | Fitxer (Mac i Linux) | Fitxer (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, i la còpia pròpia de la versió de Microsoft Store |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, o `~/.codeium/windsurf/mcp_config.json` en versions més antigues | `%APPDATA%\devin\mcp_config.json`, o `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code es configura si existeix `~/.copilot` o la carpeta de configuració del mateix VS Code.

Dues aplicacions necessiten un pas més:

- **Windsurf:** després de tornar-lo a obrir, feu clic a actualitzar (refresh) a Cascade.
- **Cline dins de l'antiga extensió de VS Code:** afegiu-hi Fontes manualment (vegeu
  [Cline](#altres-aplicacions)).

### El pas de les claus

Just després de la instal·lació, l'instal·lador us ofereix afegir les claus gratuïtes de França i dels
EUA. Per afegir-les o canviar-les més tard:

- **Mac:** torneu a obrir **Fontes Installer** i trieu **Afegeix o canvia claus**.
- **Windows:** obriu el menú Inici, després **Fontes** → **Afegeix o canvia claus**.

El que escriviu no es mostra. Les claus van a totes les aplicacions que ja tenen Fontes. Després,
tanqueu i torneu a obrir les aplicacions. On obtenir les claus i què desbloquegen: [KEYS.md](KEYS.md).

### Còpies de seguretat, noves execucions i eliminació

L'instal·lador només modifica l'entrada `fontes`. Tota la resta de configuració i els comentaris es
queden com estaven. Abans de modificar un fitxer, en desa una còpia al costat, anomenada
`<file>.fontes-backup-<date>`. Les còpies fetes després d'haver afegit claus contenen aquestes claus:
suprimiu les que ja no necessiteu. També instal·la uv. Tornar-lo a executar és segur: repara la
configuració i no modifica res més.

Per eliminar Fontes, obriu **Fontes Installer** i trieu **Elimina** (Mac), o elimineu **Fontes** des de Configuració → Aplicacions (Windows). Elimina l'entrada `fontes`, incloses les claus, de totes les aplicacions. La resta de la
vostra configuració i les còpies de seguretat es mantenen.

## Actualitzacions

- **Instal·lador i fitxer `.mcpb`:** no cal que feu res. Un cop al dia, quan s'inicia l'aplicació,
  Fontes comprova en segon pla si hi ha una versió més nova i la deixa preparada; la propera vegada
  que s'iniciï l'aplicació, la fa servir. Si una actualització no es pot baixar o no funciona, Fontes
  continua fent servir la versió que funcionava.
- **`uvx`:** Fontes us avisa quan hi ha una versió més nova, a la part superior de la llista de
  jurisdiccions. Per executar sempre la versió més nova, feu servir `fontes-mcp@latest` en lloc de
  `fontes`.

Per a això no s'envia enlloc cap informació sobre vosaltres ni sobre les vostres cerques.

## Privadesa

Per defecte, Fontes no envia res sobre vosaltres ni sobre les vostres cerques. Els recomptes d'ús són
opcionals (opt-in), i un informe d'error només s'envia després que l'hàgiu vist i confirmat. Detalls:
[PRIVACY.md](PRIVACY.md).

## Com eliminar-lo

Elimineu l'entrada `fontes` de la configuració MCP de l'aplicació (a Claude Code:
`claude mcp remove fontes`) i després tanqueu i torneu a obrir l'aplicació.

## Bo de saber

Fontes llegeix fonts públiques, sobretot llocs web judicials i governamentals. Marca les no oficials a
les respostes. Obriu sempre l'enllaç a la font abans de confiar en una resolució o una disposició.

Si alguna cosa falla, envieu a fontesmcp@proton.me el que heu fet i l'error que heu obtingut.

## Abans de confiar-hi

- Fontes és una eina de recerca, no assessorament jurídic. Utilitzar-lo no converteix ningú en el
  vostre advocat.
- Es proporciona "tal com és", sense garantia, i els seus autors no són responsables de com
  s'utilitza, en la mesura que ho permeti la llei. Els termes complets són a la
  [llicència](../../../LICENSE) (Apache 2.0).
