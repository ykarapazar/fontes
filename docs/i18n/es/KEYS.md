> Esta es una traducción asistida por máquina. La versión en inglés es la que prevalece.

# Claves de API

Casi todas las fuentes de Fontes funcionan sin clave. Dos necesitan una gratuita:

| Clave | Desbloquea | Sin ella |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Francia: Judilibre (resoluciones judiciales) y Légifrance (legislación) | Francia está desactivada. `list_jurisdictions` la muestra como inactiva. |
| `WLM_US_GOVINFO_KEY` | Estados Unidos: búsqueda en govinfo (resoluciones de tribunales federales, Statutes at Large, public laws) | Fontes usa la `DEMO_KEY` compartida: unas 10 búsquedas al día por dirección IP. Abrir una resolución conocida y el US Code no requieren clave. |

Las claves son opcionales. Puede añadirlas más tarde.

## Añadir una clave

**Con el instalador.** Una vez configurado Fontes, el instalador le ofrece añadir claves.
En un Mac, haga clic en **Añadir claves**, o en **Listo** para omitirlo; en Windows, responda a la
pregunta (pulse Intro para omitirlo). Para añadir o cambiar claves más tarde, ejecute
**Add or change keys**:

- Mac: vuelva a abrir la aplicación Fontes Installer y elija **Añadir o cambiar claves**.
- Windows: haga doble clic en `Add or change keys.cmd` en la carpeta del instalador. El programa de
  instalación de Windows, cuando esté disponible, también lo colocará en Start menu > Fontes.

Lo que escriba no se muestra. Para cada clave: péguela, pulse Intro para conservar la actual o
escriba `-` para eliminarla. Las claves se añaden a todas las aplicaciones que ya tienen Fontes.

**Con la extensión de Claude Desktop (.mcpb).** Abra Claude > Settings > Extensions > Fontes y rellene
los campos. Todos son opcionales.

**A mano.** Añada las variables al bloque `env` de la entrada `fontes` en la configuración MCP de su
aplicación:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Reinicie la aplicación después de cualquier cambio.

## Francia: PISTE (gratuito)

1. Cree una cuenta en [piste.gouv.fr](https://piste.gouv.fr). Esto supone aceptar las condiciones de
   PISTE (CGU).
2. Vaya a API > **Consentement CGU API**. Acepte las condiciones de **JUDILIBRE** y **Légifrance**
   (producción).
3. Cree una **aplicación de producción**. La `APP_SANDBOX` creada para usted no puede acceder a
   producción. En "Modifier l'application", marque **JUDILIBRE (production)** y
   **Légifrance (production)** y aplique los cambios.
4. Abra la pestaña **Authentification** de la aplicación. Copie el `client_id` y el `client_secret`.
5. Ejecute **Add or change keys** y péguelos.

Condiciones, en resumen:

- Datos: Licence Ouverte / Etalab 2.0. Se permite la reutilización, incluida la comercial, con
  atribución.
- No publique ni comparta sus credenciales. Avise a PISTE si se filtran.
- La API de Légifrance es un servicio beta. Puede suspenderse y tiene cuotas (por segundo, minuto y
  día).
- Los textos de Légifrance no son la versión auténtica. Solo lo es el PDF firmado del Journal officiel.
- Judilibre: no use los nombres de jueces ni de secretarios judiciales para evaluar, comparar o
  predecir su labor (Code de l'organisation judiciaire, art. L111-13; constituye un delito).
- Judilibre: cumpla el RGPD. No intente volver a identificar a las partes.

Sus cuotas están en PISTE, en API Sélectionnées > Actions > Consulter les quotas.

## Estados Unidos: api.data.gov (gratuito)

1. Vaya a [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (la clave se muestra en
   pantalla) o a [api.data.gov/signup](https://api.data.gov/signup/) (la clave se le envía por correo
   electrónico).
2. Introduzca su nombre y su correo electrónico. El campo "how will you use it" es opcional.
3. Copie la clave de 40 caracteres.
4. Ejecute **Add or change keys** y péguela como clave de EE. UU.

Condiciones, en resumen:

- Con su propia clave, govinfo permite hasta 36.000 solicitudes por hora.
- No encontramos condiciones de servicio específicas de la API (api.data.gov/terms/ no existe). No
  verificado. Consulte las [políticas de govinfo](https://www.govinfo.gov/about/policies) y la
  [política de privacidad de data.gov](https://data.gov/privacy-policy/).
- No comparta la clave.

## Dónde se guardan las claves

- **Instalador o a mano:** como texto sin cifrar en el archivo de configuración MCP de cada
  aplicación, en el bloque `env` de la entrada `fontes`. Cualquiera que pueda leer sus archivos de
  usuario puede leer las claves.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` o `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Extensión de Claude Desktop (.mcpb):** Claude guarda estos campos en su configuración y los
  protege con el almacenamiento seguro de su sistema (Keychain en Mac, Credential Manager en Windows).

Antes de cada cambio, el instalador guarda una copia del archivo de configuración junto a él
(`<file>.fontes-backup-<time>`). Las copias hechas después de añadir claves también contienen las
claves. Elimine las copias antiguas que no necesite.

## Cambiar o eliminar una clave

- Ejecute **Add or change keys**. Pegue una clave nueva para sustituirla o escriba `-` para
  eliminarla.
- O edite el bloque `env` a mano y reinicie la aplicación.
- Desinstalar Fontes elimina toda su entrada, claves incluidas. No borra las copias de seguridad.
- Si una clave se ha filtrado, sustitúyala también en el origen: en PISTE, cree credenciales nuevas
  para su aplicación; en api.data.gov, solicite una clave nueva.

## Mensajes que puede ver

| Mensaje | Significado |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | No hay clave de Francia. Añada una. |
| `Inactive: needs a free PISTE account. ...` (en `list_jurisdictions`) | Lo mismo. |
| `PISTE refused the client credentials ...` | El ID o el secret son incorrectos o ya no son válidos. Vuelva a copiar ambos desde la pestaña Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Su aplicación no está suscrita a esa API o no ha aceptado sus condiciones. Consulte los pasos 2 y 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | No hay clave de EE. UU. La búsqueda funciona para unas pocas llamadas al día. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | La clave de demostración se ha agotado. Añada su propia clave. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | La clave es incorrecta o aún no se ha confirmado desde el correo electrónico. |

Un valor vacío cuenta como ausencia de clave.

## Permisos (WLM_PERMITTED)

Esto no es una clave de API, y el instalador no lo define. **Defínalo solo si usted mismo tiene ese
permiso.**

Algunas fuentes están desactivadas por defecto porque sus condiciones o su robots.txt prohíben el uso
automatizado sin permiso. Si tiene el permiso del editor, active una fuente añadiendo su código a
`WLM_PERMITTED`, separado por comas, en el bloque `env`: `"WLM_PERMITTED": "in,de"`.

| Código | Fuente |
|---|---|
| `az` | Azerbaiyán: e-qanun.az (Ministerio de Justicia) |
| `bh` | Baréin: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Colombia: Función Pública, Gestor Normativo (legislación consolidada) |
| `de` | Alemania: NeuRIS (portal federal de información jurídica, servicio de prueba) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Grecia: Imprenta Nacional, búsqueda en el Diario Oficial del Gobierno (search.et.gr) |
| `in` | India: India Code (indiacode.gov.in) |
| `mu` | Mauricio: Supreme Court (supremecourt.govmu.org) |
| `sg` | Singapur: sentencias judiciales (elitigation.sg) |

Sin permiso, Fontes indica: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
