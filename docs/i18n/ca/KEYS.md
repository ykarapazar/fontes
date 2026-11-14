> Aquesta és una traducció assistida per màquina. La versió anglesa és la que preval.

# Claus d'API

Gairebé totes les fonts de Fontes funcionen sense clau. Dues necessiten una clau gratuïta:

| Clau | Desbloqueja | Sense la clau |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | França: Judilibre (resolucions judicials) i Légifrance (legislació) | França queda desactivada. `list_jurisdictions` la mostra com a inactiva. |
| `WLM_US_GOVINFO_KEY` | Estats Units: cerca a govinfo (resolucions de tribunals federals, Statutes at Large, public laws) | Fontes fa servir la `DEMO_KEY` compartida: unes 10 cerques al dia per adreça IP. Obrir una resolució coneguda i el US Code no necessiten clau. |

Les claus són opcionals. Les podeu afegir més tard.

## Afegir una clau

**Amb l'instal·lador.** Un cop configurat Fontes, l'instal·lador us ofereix afegir claus.
En un Mac, feu clic a **Afegeix claus**, o a **Fet** per ometre-ho; a Windows, responeu la pregunta
(premeu Retorn per ometre-ho). Per afegir o canviar claus més tard, executeu
**Add or change keys**:

- Mac: torneu a obrir l'aplicació Fontes Installer i trieu **Afegeix o canvia claus**.
- Windows: feu doble clic a `Add or change keys.cmd` a la carpeta de l'instal·lador. El programa
  d'instal·lació per a Windows, quan estigui disponible, també el posa a Start menu > Fontes.

El que escriviu no es mostra. Per a cada clau: enganxeu-la, premeu Retorn per conservar l'actual o
escriviu `-` per eliminar-la. Les claus van a totes les aplicacions que ja tenen Fontes.

**Amb l'extensió de Claude Desktop (.mcpb).** Obriu Claude > Settings > Extensions > Fontes i ompliu
els camps. Tots són opcionals.

**Manualment.** Afegiu les variables al bloc `env` de l'entrada `fontes` a la configuració MCP de la
vostra aplicació:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Reinicieu l'aplicació després de qualsevol canvi.

## França: PISTE (gratuït)

1. Creeu un compte a [piste.gouv.fr](https://piste.gouv.fr). Això implica acceptar les condicions de
   PISTE (CGU).
2. Aneu a API > **Consentement CGU API**. Accepteu les condicions de **JUDILIBRE** i **Légifrance**
   (producció).
3. Creeu una **aplicació de producció**. L'`APP_SANDBOX` que es crea per a vosaltres no pot accedir a
   producció. A "Modifier l'application", marqueu **JUDILIBRE (production)** i
   **Légifrance (production)** i apliqueu-ho.
4. Obriu la pestanya **Authentification** de l'aplicació. Copieu el `client_id` i el `client_secret`.
5. Executeu **Add or change keys** i enganxeu-los.

Condicions, en resum:

- Dades: Licence Ouverte / Etalab 2.0. Se'n permet la reutilització, també comercial, amb atribució.
- No publiqueu ni compartiu les vostres credencials. Aviseu PISTE si es filtren.
- L'API de Légifrance és un servei beta. Es pot suspendre i té quotes (per segon, minut i dia).
- Els textos de Légifrance no són la versió autèntica. Només ho és el PDF signat del Journal officiel.
- Judilibre: no feu servir noms de jutges o de lletrats de l'Administració de justícia per avaluar,
  comparar o predir la seva feina (Code de l'organisation judiciaire, art. L111-13; és un delicte).
- Judilibre: compliu el RGPD. No intenteu reidentificar les parts.

Les vostres quotes són a PISTE, a API Sélectionnées > Actions > Consulter les quotas.

## Estats Units: api.data.gov (gratuït)

1. Aneu a [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (la clau es mostra a la
   pantalla) o a [api.data.gov/signup](https://api.data.gov/signup/) (la clau s'envia per correu
   electrònic).
2. Introduïu el vostre nom i correu electrònic. El camp "how will you use it" és opcional.
3. Copieu la clau de 40 caràcters.
4. Executeu **Add or change keys** i enganxeu-la com a clau dels EUA.

Condicions, en resum:

- Amb la vostra pròpia clau, govinfo permet fins a 36.000 peticions per hora.
- No hem trobat condicions de servei específiques de l'API (api.data.gov/terms/ no existeix). No
  verificat. Vegeu les [polítiques de govinfo](https://www.govinfo.gov/about/policies) i la
  [política de privadesa de data.gov](https://data.gov/privacy-policy/).
- No compartiu la clau.

## On es desen les claus

- **Instal·lador o manualment:** en text pla al fitxer de configuració MCP de cada aplicació, al bloc
  `env` de l'entrada `fontes`. Qualsevol persona que pugui llegir els vostres fitxers d'usuari pot
  llegir les claus.
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
- **Extensió de Claude Desktop (.mcpb):** Claude desa aquests camps a la seva configuració i els
  protegeix amb l'emmagatzematge segur del vostre sistema (Keychain al Mac, Credential Manager a
  Windows).

Abans de cada canvi, l'instal·lador desa una còpia del fitxer de configuració al seu costat
(`<file>.fontes-backup-<time>`). Les còpies fetes després d'haver afegit claus també contenen les
claus. Suprimiu les còpies antigues que no necessiteu.

## Canviar o eliminar una clau

- Executeu **Add or change keys**. Enganxeu una clau nova per substituir-la o escriviu `-` per
  eliminar-la.
- O editeu el bloc `env` manualment i reinicieu l'aplicació.
- Desinstal·lar Fontes elimina tota la seva entrada, incloses les claus. Les còpies de seguretat no se
  suprimeixen.
- Si una clau s'ha filtrat, substituïu-la també a l'origen: a PISTE, genereu credencials noves per a
  la vostra aplicació; a api.data.gov, registreu-vos per obtenir una clau nova.

## Missatges que podeu veure

| Missatge | Significat |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | No hi ha clau de França. Afegiu-ne una. |
| `Inactive: needs a free PISTE account. ...` (a `list_jurisdictions`) | El mateix. |
| `PISTE refused the client credentials ...` | L'ID o el secret és erroni o ja no és vàlid. Torneu a copiar tots dos de la pestanya Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | La vostra aplicació no està subscrita a aquesta API, o no n'heu acceptat les condicions. Vegeu els passos 2 i 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | No hi ha clau dels EUA. La cerca funciona per a unes quantes crides al dia. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | La clau de demostració s'ha esgotat. Afegiu-hi la vostra pròpia clau. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | La clau és errònia o encara no s'ha confirmat per correu electrònic. |

Un valor buit compta com a absència de clau.

## Permisos (WLM_PERMITTED)

Això no és una clau d'API, i l'instal·lador no el defineix. **Definiu-lo només si teniu vosaltres
mateixos aquest permís.**

Algunes fonts estan desactivades per defecte perquè les seves condicions o el seu robots.txt
prohibeixen l'ús automatitzat sense permís. Si teniu el permís de l'editor, activeu una font afegint
el seu codi a `WLM_PERMITTED`, separat per comes, al bloc `env`: `"WLM_PERMITTED": "in,de"`.

| Codi | Font |
|---|---|
| `az` | Azerbaidjan: e-qanun.az (Ministeri de Justícia) |
| `bh` | Bahrain: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Colòmbia: Función Pública, Gestor Normativo (legislació consolidada) |
| `de` | Alemanya: NeuRIS (portal federal d'informació jurídica, servei de prova) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Grècia: Impremta Nacional, cerca al Diari Oficial del Govern (search.et.gr) |
| `in` | Índia: India Code (indiacode.gov.in) |
| `mu` | Maurici: Supreme Court (supremecourt.govmu.org) |
| `sg` | Singapur: resolucions judicials (elitigation.sg) |

Sense permís, Fontes diu: `Off by default (<code>): the terms or robots.txt of ... forbid automated
use without the operator's permission.`
