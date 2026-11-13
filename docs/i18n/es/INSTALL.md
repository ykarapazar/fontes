> Esta es una traducción asistida por máquina. La versión en inglés es la que prevalece.

# Instalar Fontes

Fontes permite que su aplicación de IA consulte resoluciones judiciales y legislación en directo en
sitios web judiciales y gubernamentales de más de 120 jurisdicciones. Cada resultado enlaza al
original. Es un servidor MCP estándar, por lo que funciona en cualquier aplicación que pueda ejecutar
un servidor MCP local: Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Gemini
CLI, Windsurf, Zed, LM Studio, Cline y otras.

Elija su aplicación, siga sus pasos y luego [compruebe que funciona](#comprobar-que-funciona).

## Claude Desktop

1. Descargue el archivo `.mcpb` de Fontes de la
   [última versión](https://github.com/ykarapazar/fontes/releases/latest).
2. Haga doble clic en él. Claude Desktop lo abre.
3. Haga clic en **Install**.

## Codex

En un terminal:

```bash
codex mcp add fontes -- uvx fontes-mcp
```

La CLI de Codex y la extensión de Codex para IDE comparten esta configuración (`~/.codex/config.toml`).
Necesita [uv](#necesita-uv).

## Claude Code

En un terminal:

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Necesita [uv](#necesita-uv).

## Otras aplicaciones

Cada una de ellas necesita [uv](#necesita-uv). Añada la entrada, guarde y luego cierre y vuelva a
abrir la aplicación.

**Cursor:** en `~/.cursor/mcp.json` (todos los proyectos) o `.cursor/mcp.json` (un proyecto):

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot):** ejecute **MCP: Add Server** desde la paleta de comandos (Command
Palette), elija **Command (stdio)**, introduzca `uvx fontes-mcp` y llame al servidor `fontes`. O añada
esto a `~/.copilot/mcp-config.json`:

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Las configuraciones más antiguas de VS Code usan `.vscode/mcp.json`, donde la clave de nivel superior
es `servers` en lugar de `mcpServers`.

**Gemini CLI:** en un terminal, `gemini mcp add -s user fontes uvx fontes-mcp`. O añada esto a
`~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed:** abra su archivo de configuración (**zed: open settings file**) y añada:

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio:** en la barra lateral derecha, abra la pestaña **Program**, haga clic en **Install → Edit
mcp.json** y añada:

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline:** haga clic en el icono **MCP Servers**, abra la pestaña **Configure**, haga clic en
**Configure MCP Servers** y añada la misma entrada `mcpServers` que para LM Studio.

**Claude Desktop, a mano** (en lugar del archivo `.mcpb`): añada la misma entrada `mcpServers` a
`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows:
`%APPDATA%\Claude\`).

**Cualquier otra aplicación MCP** (Windsurf y otras): su propia documentación indica dónde guarda sus
servidores MCP. La mayoría aceptan la misma entrada: comando `uvx`, argumento `fontes`.

Si la aplicación no encuentra `uvx`, use su ruta completa (en macOS y Linux, `which uvx` la muestra).

## Necesita uv

Codex, Claude Code y las demás aplicaciones inician Fontes con `uvx`, que viene con **uv**, una
pequeña herramienta gratuita de Astral. Para instalarla, consulte la
[guía de Astral](https://docs.astral.sh/uv/getting-started/installation/) o ejecute:

- macOS o Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Claves

Algunas fuentes necesitan una clave gratuita: consulte [KEYS.md](KEYS.md).

## Comprobar que funciona

En un chat nuevo, pregunte: *«¿En qué jurisdicciones puede buscar Fontes?»* La aplicación debería
responder con una lista de países. Si no lo hace, cierre y vuelva a abrir la aplicación una vez más.

## Instalador en un clic (en camino)

Está en camino un instalador para Mac y Windows que configura Fontes en todas sus aplicaciones a la
vez. Configura Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf,
Gemini CLI, Zed, LM Studio y Cline. Cuando se publique:

**Antes de empezar:** cierre por completo cada una de estas aplicaciones. Esto es especialmente
importante para Claude Code: mientras se ejecuta, reescribe `~/.claude.json` y puede deshacer el
cambio del instalador. Si no puede cerrar Claude Code, añada Fontes con `claude mcp add` en su lugar
(consulte [Claude Code](#claude-code)).

**Mac**

1. Abra la carpeta descargada **Fontes Installer**.
2. Haga doble clic en **Install Fontes.command**.
   - Si su Mac dice que "cannot be opened because it is from an unidentified developer" (no se puede
     abrir porque procede de un desarrollador no identificado): haga clic con el botón derecho (o
     Control-clic) en el archivo, elija **Open** y luego **Open** otra vez. Solo tiene que hacerlo
     una vez.
3. Se abre una ventana que le pregunta si desea enviar recuentos de uso anónimos; pulse Intro para
   responder que no.
4. Le pregunta si desea añadir claves ahora. Pulse Intro para omitirlo; consulte
   [El paso de las claves](#el-paso-de-las-claves).
5. Cuando diga **Listo**, vuelva a abrir sus aplicaciones de IA.

**Windows**

1. Descomprima el archivo descargado **Fontes Installer** (botón derecho → Extract All).
2. Haga doble clic en **Install Fontes.cmd**.
   - Si Windows muestra "Windows protected your PC": haga clic en **More info** y luego en
     **Run anyway**.
3. Cuando le pregunte si desea enviar recuentos de uso anónimos, pulse Intro para responder que no.
4. Le pregunta si desea añadir claves ahora. Pulse Intro para omitirlo; consulte
   [El paso de las claves](#el-paso-de-las-claves).
5. Cuando diga **Listo**, vuelva a abrir sus aplicaciones de IA. Si alguna seguía en ejecución,
   ciérrela por completo (también desde la bandeja del sistema, junto al reloj) y vuelva a abrirla.

Al final, el instalador enumera las aplicaciones que ha configurado.

### Qué aplicaciones configura

Configura una aplicación solo si la carpeta de configuración de esa aplicación ya existe en su
ordenador. Claude Code solo se configura si existe `~/.claude.json`. Claude Desktop se configura
siempre. Cada aplicación recibe una entrada, `fontes`, en este archivo:

| Aplicación | Archivo (Mac y Linux) | Archivo (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux: `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, y la copia propia de la versión de Microsoft Store |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, o `~/.codeium/windsurf/mcp_config.json` en versiones anteriores | `%APPDATA%\devin\mcp_config.json`, o `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code se configura si existe `~/.copilot` o la propia carpeta de configuración de VS Code.

Dos aplicaciones necesitan un paso más:

- **Windsurf:** después de volver a abrirlo, pulse actualizar (refresh) en Cascade.
- **Cline dentro de la extensión antigua de VS Code:** añada Fontes a mano (consulte
  [Cline](#otras-aplicaciones)).

### El paso de las claves

Justo después de instalar, el instalador le ofrece añadir las claves gratuitas de Francia y de
EE. UU. Para añadirlas o cambiarlas más tarde:

- **Mac:** haga doble clic en **Add or change keys.command** en la carpeta del instalador, o vuelva a
  abrir la aplicación Fontes Installer y elija **Añadir o cambiar claves**.
- **Windows:** haga doble clic en **Add or change keys.cmd** en la carpeta del instalador.

Lo que escriba no se muestra. Las claves se añaden a todas las aplicaciones que ya tienen Fontes.
Después, cierre y vuelva a abrir las aplicaciones. Dónde obtener las claves y qué desbloquean:
[KEYS.md](KEYS.md).

### Copias de seguridad, nuevas ejecuciones y desinstalación

El instalador solo modifica la entrada `fontes`. Todos los demás ajustes y comentarios quedan como
estaban. Antes de modificar un archivo, guarda una copia junto a él, llamada
`<file>.fontes-backup-<date>`. Las copias hechas después de añadir claves contienen esas claves:
elimine las que ya no necesite. También instala uv. Volver a ejecutarlo es seguro: repara la
configuración y no cambia nada más.

Para quitar Fontes, haga doble clic en **Uninstall Fontes.command** (Mac) o **Uninstall Fontes.cmd**
(Windows). Elimina la entrada `fontes`, claves incluidas, de todas las aplicaciones. Sus demás ajustes
y las copias de seguridad se conservan.

## Actualizaciones

- **Instalador y archivo `.mcpb`:** no tiene que hacer nada. Una vez al día, cuando se inicia la
  aplicación, Fontes busca una versión más reciente en segundo plano y la deja preparada; la próxima
  vez que se inicie la aplicación, la usará. Si una actualización no se puede descargar o no funciona,
  Fontes sigue usando la versión que funcionaba.
- **`uvx`:** Fontes le avisa cuando hay una versión más reciente, al principio de su lista de
  jurisdicciones. Para ejecutar siempre la versión más reciente, use `fontes-mcp@latest` en lugar de
  `fontes`.

Para esto no se envía a ningún sitio ninguna información sobre usted ni sobre sus búsquedas.

## Privacidad

Por defecto, Fontes no envía nada sobre usted ni sobre sus búsquedas. Los recuentos de uso son
opcionales (solo si usted los activa), y un informe de error solo se envía después de que usted lo vea
y lo confirme. Detalles: [PRIVACY.md](PRIVACY.md).

## Quitarlo

Elimine la entrada `fontes` de la configuración MCP de su aplicación (en Claude Code:
`claude mcp remove fontes`) y luego cierre y vuelva a abrir la aplicación.

## Conviene saber

Fontes lee fuentes públicas, en su mayoría sitios web judiciales y gubernamentales. Marca las no
oficiales en sus respuestas. Abra siempre el enlace a la fuente antes de confiar en una resolución o
una disposición.

Si algo falla, escriba a fontesmcp@proton.me contando lo que hizo y el error que vio.

## Antes de confiar en él

- Fontes es una herramienta de investigación, no asesoramiento jurídico. Usarlo no convierte a nadie
  en su abogado.
- Se proporciona «tal cual», sin garantía, y sus autores no son responsables del uso que se haga de
  él, en la medida en que la ley lo permita. Las condiciones completas están en la
  [licencia](../../../LICENSE) (Apache 2.0).
