> Ceci est une traduction assistée par machine. La version anglaise fait foi.

# Clés d'API

Presque toutes les sources de Fontes fonctionnent sans clé. Deux en nécessitent une, gratuite :

| Clé | Débloque | Sans elle |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | France : Judilibre (décisions de justice) et Légifrance (législation) | La France est désactivée. `list_jurisdictions` l'affiche comme inactive. |
| `WLM_US_GOVINFO_KEY` | États-Unis : recherche govinfo (décisions des juridictions fédérales, Statutes at Large, public laws) | Fontes utilise la `DEMO_KEY` partagée : environ 10 recherches par jour et par adresse IP. L'ouverture d'une décision connue et le US Code ne nécessitent pas de clé. |

Les clés sont facultatives. Vous pouvez les ajouter plus tard.

## Ajouter une clé

**Avec le programme d'installation.** Une fois Fontes configuré, le programme d'installation propose d'ajouter
des clés. Sur un Mac, cliquez sur **Ajouter des clés**, ou sur **Terminé** pour passer ; sous Windows, répondez à
la question (appuyez sur Entrée pour passer). Pour ajouter ou modifier des clés plus tard, lancez **Ajouter ou
modifier des clés** :

- Mac : rouvrez l'application Fontes Installer et choisissez **Ajouter ou modifier des clés**.
- Windows : ouvrez le menu Démarrer, puis **Fontes** → **Ajouter ou modifier des clés**.

La saisie est masquée. Pour chaque clé : collez-la, appuyez sur Entrée pour conserver la valeur existante, ou
tapez `-` pour la supprimer. Les clés sont ajoutées à toutes les applications où Fontes est déjà installé.

**Avec l'extension Claude Desktop (.mcpb).** Ouvrez Claude > Settings > Extensions > Fontes et remplissez les
champs. Ils sont tous facultatifs.

**À la main.** Ajoutez les variables au bloc `env` de l'entrée `fontes` dans la configuration MCP de votre
application :

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Redémarrez l'application après toute modification.

## France : PISTE (gratuit)

1. Créez un compte sur [piste.gouv.fr](https://piste.gouv.fr). Cela implique d'accepter les conditions
   générales d'utilisation (CGU) de PISTE.
2. Allez dans API > **Consentement CGU API**. Acceptez les CGU pour **JUDILIBRE** et **Légifrance** (production).
3. Créez une **application de production**. L'`APP_SANDBOX` créée pour vous ne peut pas accéder à la production.
   Sous « Modifier l'application », cochez **JUDILIBRE (production)** et **Légifrance (production)**, puis
   appliquez.
4. Ouvrez l'onglet **Authentification** de l'application. Copiez le `client_id` et le `client_secret`.
5. Lancez **Ajouter ou modifier des clés** et collez-les.

Les conditions, en bref :

- Données : Licence Ouverte / Etalab 2.0. La réutilisation, y compris commerciale, est autorisée avec mention
  de la source.
- Ne publiez ni ne partagez vos identifiants. Prévenez PISTE en cas de fuite.
- L'API Légifrance est un service en version bêta. Elle peut être suspendue, et elle a des quotas (par seconde,
  par minute et par jour).
- Les textes de Légifrance ne sont pas la version authentique. Seul le PDF signé du Journal officiel l'est.
- Judilibre : n'utilisez pas les noms des magistrats ou des greffiers pour évaluer, comparer ou prédire leurs
  pratiques (Code de l'organisation judiciaire, art. L111-13 ; c'est une infraction pénale).
- Judilibre : respectez le RGPD. N'essayez pas de réidentifier les parties.

Vos quotas sont visibles sur PISTE sous API Sélectionnées > Actions > Consulter les quotas.

## États-Unis : api.data.gov (gratuit)

1. Allez sur [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (la clé s'affiche à l'écran)
   ou sur [api.data.gov/signup](https://api.data.gov/signup/) (la clé vous est envoyée par e-mail).
2. Saisissez votre nom et votre adresse e-mail. Le champ « how will you use it » est facultatif.
3. Copiez la clé de 40 caractères.
4. Lancez **Ajouter ou modifier des clés** et collez-la comme clé pour les États-Unis.

Les conditions, en bref :

- Avec votre propre clé, govinfo autorise jusqu'à 36 000 requêtes par heure.
- Nous n'avons trouvé aucune condition d'utilisation propre à l'API (api.data.gov/terms/ n'existe pas).
  Non vérifié. Voir les [politiques de govinfo](https://www.govinfo.gov/about/policies) et la
  [politique de confidentialité de data.gov](https://data.gov/privacy-policy/).
- Gardez la clé pour vous.

## Où les clés sont stockées

- **Programme d'installation ou à la main :** en texte brut dans le fichier de configuration MCP de chaque
  application, dans le bloc `env` de l'entrée `fontes`. Toute personne pouvant lire vos fichiers utilisateur
  peut lire les clés.
  - Claude Desktop : `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code : `~/.claude.json`
  - Codex : `~/.codex/config.toml`
  - Cursor : `~/.cursor/mcp.json`
  - VS Code (Copilot) : `~/.copilot/mcp-config.json`
  - Windsurf : `~/.config/devin/mcp_config.json` ou `~/.codeium/windsurf/mcp_config.json`
    (Windows : `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI : `~/.gemini/settings.json`
  - Zed : `~/.config/zed/settings.json` (Windows : `%APPDATA%\Zed\settings.json`)
  - LM Studio : `~/.lmstudio/mcp.json`
  - Cline : `~/.cline/data/settings/cline_mcp_settings.json`
- **Extension Claude Desktop (.mcpb) :** Claude conserve ces champs dans ses paramètres et les protège avec le
  stockage sécurisé de votre système (Trousseau sur Mac, Gestionnaire d'identification sur Windows).

Avant chaque modification, le programme d'installation enregistre une copie du fichier de configuration à côté
de celui-ci (`<file>.fontes-backup-<time>`). Les copies faites après l'ajout de vos clés contiennent elles aussi
les clés. Supprimez les anciennes copies dont vous n'avez pas besoin.

## Modifier ou supprimer une clé

- Lancez **Ajouter ou modifier des clés**. Collez une nouvelle clé pour la remplacer, ou tapez `-` pour la
  supprimer.
- Ou modifiez le bloc `env` à la main et redémarrez l'application.
- La désinstallation de Fontes supprime toute son entrée, clés comprises. Elle ne supprime pas les copies de
  sauvegarde.
- Si une clé a fuité, remplacez-la aussi à la source : sur PISTE, créez de nouveaux identifiants pour votre
  application ; pour api.data.gov, demandez une nouvelle clé.

## Messages que vous pouvez voir

| Message | Signification |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Aucune clé pour la France. Ajoutez-en une. |
| `Inactive: needs a free PISTE account. ...` (dans `list_jurisdictions`) | Idem. |
| `PISTE refused the client credentials ...` | L'identifiant ou le secret est erroné ou n'est plus valide. Copiez-les à nouveau tous les deux depuis l'onglet Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Votre application n'est pas abonnée à cette API, ou vous n'avez pas accepté ses conditions. Voir les étapes 2 et 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Aucune clé pour les États-Unis. La recherche fonctionne pour quelques appels par jour. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | La clé de démonstration est épuisée. Ajoutez votre propre clé. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | La clé est erronée, ou pas encore confirmée depuis l'e-mail. |

Une valeur vide équivaut à l'absence de clé.

## Autorisations (WLM_PERMITTED)

Ce n'est pas une clé d'API, et le programme d'installation ne la définit pas. **Ne la définissez que si vous
détenez vous-même cette autorisation.**

Certaines sources sont désactivées par défaut parce que leurs conditions ou leur robots.txt interdisent l'usage
automatisé sans autorisation. Si vous avez l'autorisation de l'éditeur, activez une source en ajoutant son code
à `WLM_PERMITTED`, séparé par des virgules, dans le bloc `env` : `"WLM_PERMITTED": "in,de"`.

| Code | Source |
|---|---|
| `az` | Azerbaïdjan : e-qanun.az (ministère de la Justice) |
| `bh` | Bahreïn : Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Colombie : Función Pública, Gestor Normativo (législation consolidée) |
| `de` | Allemagne : NeuRIS (portail fédéral d'information juridique, service en phase d'essai) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Grèce : Imprimerie nationale, recherche dans le Journal officiel (search.et.gr) |
| `in` | Inde : India Code (indiacode.gov.in) |
| `mu` | Maurice : Cour suprême (supremecourt.govmu.org) |
| `sg` | Singapour : décisions de justice (elitigation.sg) |

Sans autorisation, Fontes affiche : `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
