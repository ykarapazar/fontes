> Ceci est une traduction assistée par machine. La version anglaise fait foi.

# Installer Fontes

Fontes permet à votre application d'IA de consulter des décisions de justice et la législation en direct sur
les sites des juridictions et des États, dans plus de 120 juridictions. Chaque résultat renvoie à l'original.
C'est un serveur MCP standard : il fonctionne donc dans toute application capable d'exécuter un serveur MCP
local : Claude Desktop, Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed,
LM Studio, Cline et d'autres.

Choisissez votre application, suivez ses étapes, puis [vérifiez que cela fonctionne](#vérifier-que-cela-fonctionne).

## Claude Desktop

1. Téléchargez le fichier `.mcpb` de Fontes depuis la
   [dernière version](https://github.com/ykarapazar/fontes/releases/latest).
2. Double-cliquez dessus. Claude Desktop l'ouvre.
3. Cliquez sur **Install**.

## Codex

Dans un terminal :

```bash
codex mcp add fontes -- uvx fontes-mcp
```

La CLI Codex et l'extension Codex pour IDE partagent ce paramètre (`~/.codex/config.toml`).
Il vous faut [uv](#il-vous-faut-uv).

## Claude Code

Dans un terminal :

```bash
claude mcp add fontes -- uvx fontes-mcp
```

Il vous faut [uv](#il-vous-faut-uv).

## Autres applications

Chacune de ces applications nécessite [uv](#il-vous-faut-uv). Ajoutez l'entrée, enregistrez, puis quittez et
rouvrez l'application.

**Cursor :** dans `~/.cursor/mcp.json` (tous les projets) ou `.cursor/mcp.json` (un seul projet) :

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**VS Code (GitHub Copilot) :** exécutez **MCP: Add Server** depuis la palette de commandes, choisissez
**Command (stdio)**, saisissez `uvx fontes-mcp` et nommez le serveur `fontes`. Ou ajoutez ceci à
`~/.copilot/mcp-config.json` :

```json
{
  "mcpServers": {
    "fontes": { "type": "stdio", "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

Les configurations plus anciennes de VS Code utilisent `.vscode/mcp.json`, où la clé de premier niveau est
`servers` au lieu de `mcpServers`.

**Gemini CLI :** dans un terminal, `gemini mcp add -s user fontes uvx fontes-mcp`. Ou ajoutez ceci à
`~/.gemini/settings.json` :

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Zed :** ouvrez votre fichier de paramètres (**zed: open settings file**) et ajoutez :

```json
{
  "context_servers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**LM Studio :** dans la barre latérale de droite, ouvrez l'onglet **Program**, cliquez sur **Install → Edit
mcp.json**, puis ajoutez :

```json
{
  "mcpServers": {
    "fontes": { "command": "uvx", "args": ["fontes-mcp"] }
  }
}
```

**Cline :** cliquez sur l'icône **MCP Servers**, ouvrez l'onglet **Configure**, cliquez sur **Configure MCP
Servers**, puis ajoutez la même entrée `mcpServers` que pour LM Studio.

**Claude Desktop, à la main** (au lieu du fichier `.mcpb`) : ajoutez la même entrée `mcpServers` à
`claude_desktop_config.json` (macOS : `~/Library/Application Support/Claude/`, Windows :
`%APPDATA%\Claude\`).

**Toute autre application MCP** (Windsurf et d'autres) : sa propre documentation indique où elle conserve ses
serveurs MCP. La plupart acceptent la même entrée : commande `uvx`, argument `fontes`.

Si l'application ne trouve pas `uvx`, utilisez son chemin complet (sous macOS et Linux, `which uvx` l'affiche).

## Il vous faut uv

Codex, Claude Code et les autres applications lancent Fontes avec `uvx`, qui est fourni avec **uv**, un petit
outil gratuit d'Astral. Pour l'installer, consultez le
[guide d'Astral](https://docs.astral.sh/uv/getting-started/installation/), ou exécutez :

- macOS ou Linux : `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell) : `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Clés

Certaines sources nécessitent une clé gratuite : voir [KEYS.md](KEYS.md).

## Vérifier que cela fonctionne

Dans une nouvelle conversation, demandez : *« Dans quelles juridictions Fontes peut-il chercher ? »*
L'application devrait répondre par une liste de pays. Si ce n'est pas le cas, quittez et rouvrez
l'application une fois de plus.

## Programme d'installation en un clic (Mac et Windows)

Le programme d'installation configure Fontes dans toutes vos applications à la fois : Claude Desktop,
Codex, Claude Code, Cursor, VS Code (GitHub Copilot), Windsurf, Gemini CLI, Zed, LM Studio et Cline.

**Avant de commencer :** quittez complètement chacune de ces applications. C'est surtout important pour
Claude Code : tant qu'il est ouvert, il réécrit `~/.claude.json` et peut annuler la modification faite par le
programme d'installation. Si vous ne pouvez pas quitter Claude Code, ajoutez-y plutôt Fontes avec
`claude mcp add` (voir [Claude Code](#claude-code)).

**Mac**

1. Téléchargez le programme d'installation pour Mac (`Fontes-Installer-…-mac.zip`) depuis la
   [dernière version](https://github.com/ykarapazar/fontes/releases/latest) et double-cliquez dessus pour le décompresser.
2. Double-cliquez sur **Fontes Installer**. Si votre Mac vous demande s'il faut ouvrir une application
   téléchargée sur Internet, cliquez sur **Ouvrir**.
3. Choisissez **Installer** et cliquez sur **OK**. La configuration prend environ une minute.
4. Un message affiche la liste des applications configurées. Cliquez sur **Terminé**, puis rouvrez ces
   applications. Pour ajouter d'abord les clés gratuites facultatives, cliquez plutôt sur **Ajouter des clés** ;
   voir [L'étape des clés](#létape-des-clés).

**Windows**

1. Téléchargez le programme d'installation pour Windows (`Fontes-Setup-….exe`) depuis la
   [dernière version](https://github.com/ykarapazar/fontes/releases/latest) et double-cliquez dessus.
   - Si Windows affiche « Windows a protégé votre ordinateur » : cliquez sur **Informations
     complémentaires**, puis sur **Exécuter quand même**.
2. Cliquez sur **Installer**. Une fenêtre s'ouvre et configure Fontes.
3. Lorsqu'on vous demande s'il faut envoyer des comptages d'utilisation anonymes, appuyez sur Entrée pour non.
4. Il vous demande s'il faut ajouter des clés maintenant. Appuyez sur Entrée pour passer ; voir
   [L'étape des clés](#létape-des-clés).
5. Lorsqu'il affiche **Terminé**, rouvrez vos applications d'IA. Si l'une d'elles était encore ouverte,
   fermez-la complètement (y compris depuis la zone de notification, près de l'horloge) et rouvrez-la.

À la fin, le programme d'installation affiche la liste des applications qu'il a configurées.

### Quelles applications il configure

Il ne configure une application que si le dossier de paramètres de cette application existe déjà sur votre
ordinateur. Claude Code n'est configuré que si `~/.claude.json` existe. Claude Desktop est toujours configuré.
Chaque application reçoit une seule entrée, `fontes`, dans ce fichier :

| Application | Fichier (Mac et Linux) | Fichier (Windows) |
|---|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` (Linux : `~/.config/Claude/`) | `%APPDATA%\Claude\claude_desktop_config.json`, ainsi que la copie propre à la version Microsoft Store |
| Codex | `~/.codex/config.toml` | `%USERPROFILE%\.codex\config.toml` |
| Claude Code | `~/.claude.json` | `%USERPROFILE%\.claude.json` |
| Cursor | `~/.cursor/mcp.json` | `%USERPROFILE%\.cursor\mcp.json` |
| VS Code (Copilot) | `~/.copilot/mcp-config.json` | `%USERPROFILE%\.copilot\mcp-config.json` |
| Windsurf | `~/.config/devin/mcp_config.json`, ou `~/.codeium/windsurf/mcp_config.json` sur les versions plus anciennes | `%APPDATA%\devin\mcp_config.json`, ou `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |
| Gemini CLI | `~/.gemini/settings.json` | `%USERPROFILE%\.gemini\settings.json` |
| Zed | `~/.config/zed/settings.json` | `%APPDATA%\Zed\settings.json` |
| LM Studio | `~/.lmstudio/mcp.json` | `%USERPROFILE%\.lmstudio\mcp.json` |
| Cline | `~/.cline/data/settings/cline_mcp_settings.json` | `%USERPROFILE%\.cline\data\settings\cline_mcp_settings.json` |

VS Code est configuré si `~/.copilot` ou le dossier de paramètres propre à VS Code existe.

Deux applications demandent une étape de plus :

- **Windsurf :** après l'avoir rouverte, cliquez sur actualiser dans Cascade.
- **Cline dans l'ancienne extension VS Code :** ajoutez Fontes à la main (voir [Cline](#autres-applications)).

### L'étape des clés

Juste après l'installation, le programme d'installation propose d'ajouter les clés gratuites pour la France et
les États-Unis. Pour les ajouter ou les modifier plus tard :

- **Mac :** rouvrez **Fontes Installer** et choisissez **Ajouter ou modifier des clés**.
- **Windows :** ouvrez le menu Démarrer, puis **Fontes** → **Add or change keys**.

La saisie est masquée. Les clés sont ajoutées à toutes les applications où Fontes est déjà installé. Quittez
et rouvrez ensuite les applications. Où obtenir les clés et ce qu'elles débloquent : [KEYS.md](KEYS.md).

### Copies de sauvegarde, réexécutions et désinstallation

Le programme d'installation ne modifie que l'entrée `fontes`. Tous les autres paramètres et commentaires
restent tels quels. Avant de modifier un fichier, il en enregistre une copie à côté, nommée
`<file>.fontes-backup-<date>`. Les copies faites après l'ajout de vos clés contiennent ces clés : supprimez
celles dont vous n'avez plus besoin. Il installe aussi uv. Le relancer est sans danger : il répare la
configuration et ne modifie rien d'autre.

Pour retirer Fontes, ouvrez **Fontes Installer** et choisissez **Retirer** (Mac), ou désinstallez **Fontes**
dans Paramètres → Applications (Windows). Il retire l'entrée `fontes`, clés comprises, de toutes les applications. Vos autres paramètres et les
copies de sauvegarde restent en place.

## Mises à jour

- **Programme d'installation et fichier `.mcpb` :** vous n'avez rien à faire. Une fois par jour, au démarrage
  de l'application, Fontes vérifie en arrière-plan s'il existe une version plus récente et la prépare ; au
  prochain démarrage de l'application, c'est elle qui est utilisée. Si une mise à jour ne peut pas être
  téléchargée ou ne fonctionne pas, Fontes continue d'utiliser la version qui fonctionnait.
- **`uvx` :** Fontes vous indique, en tête de sa liste de juridictions, qu'une version plus récente est
  disponible. Pour toujours exécuter la dernière version, utilisez `fontes-mcp@latest` à la place de `fontes-mcp`.

Aucune information vous concernant ou concernant vos recherches n'est envoyée nulle part pour cela.

## Confidentialité

Par défaut, Fontes n'envoie rien vous concernant ni concernant vos recherches. Les comptages d'utilisation sont
soumis à votre accord préalable (opt-in), et un rapport de bogue n'est envoyé qu'après que vous l'avez vu et
confirmé. Détails : [PRIVACY.md](PRIVACY.md).

## Désinstaller

Supprimez l'entrée `fontes` des paramètres MCP de votre application (dans Claude Code :
`claude mcp remove fontes`), puis quittez et rouvrez l'application.

## Bon à savoir

Fontes lit des sources publiques, principalement des sites de juridictions et d'États. Il signale les sources
non officielles dans ses réponses. Ouvrez toujours le lien vers la source avant de vous fier à une décision ou
à une disposition.

En cas de problème, envoyez par e-mail ce que vous avez fait et l'erreur que vous avez vue à
fontesmcp@proton.me.

## Avant de vous y fier

- Fontes est un outil de recherche, et non un conseil juridique. Son utilisation ne fait de personne votre avocat.
- Il est fourni « en l'état », sans garantie, et ses auteurs ne sont pas responsables de l'usage qui en est
  fait, dans la mesure permise par la loi. Les conditions complètes figurent dans la
  [licence](../../../LICENSE) (Apache 2.0).
