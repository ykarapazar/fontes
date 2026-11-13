> Ceci est une traduction assistée par machine. La version anglaise fait foi.

# Fontes : questions et réponses

## Qu'est-ce que Fontes ?

Un serveur MCP gratuit et open source (Apache 2.0). Il permet à toute application qui parle le Model Context
Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI et d'autres) de rechercher des décisions de justice et la
législation en direct sur les sites des juridictions et des États, dans plus de 120 juridictions et cours
internationales (124 adaptateurs). Chaque résultat indique sa source et renvoie à l'original.

## Les textes sont-ils officiels ?

Le plus souvent, mais pas toujours.

- La plupart des sources sont gérées par une juridiction, un ministère ou un journal officiel.
- Certains textes consolidés sont publiés par un gouvernement mais sont expressément non officiels : seul le
  journal officiel fait foi.
- Quelques sources ne sont pas du tout des sites gouvernementaux (par exemple LexiVox, LawPhil, Maqam,
  Wikisource).

Fontes ajoute un avertissement « Source non officielle » à chaque réponse qui provient de l'une d'elles. Avant
de citer quoi que ce soit, vérifiez la publication officielle. Le tableau de couverture du
[README](README.md#couverture) et `list_jurisdictions` indiquent la source de chaque juridiction.

## Quelles juridictions couvre-t-il, et dans quelle mesure ?

124 adaptateurs : 108 États membres de l'ONU, Hong Kong, le Kosovo, la Palestine, Taïwan, les DIFC Courts et
11 juridictions et organes internationaux (comme la Cour européenne des droits de l'homme, l'UE, la CIJ et
l'OMC).

La couverture varie beaucoup. Selon une règle stricte (les précédents de la juridiction suprême de droit commun,
ou la constitution et les lois de premier rang, atteints intégralement), 72 des 124 sont considérées comme
couvertes. [COVERAGE.md](../../COVERAGE.md) indique, pour chaque juridiction, ce que Fontes atteint, ce qu'il
n'atteint pas, et pourquoi.

## Ai-je besoin d'une clé d'API ?

Pour presque toutes les juridictions, non. Certaines sources nécessitent une clé gratuite : voir
[KEYS.md](KEYS.md).

- **France :** oui. La France est désactivée tant que vous n'avez pas défini `WLM_FR_PISTE_CLIENT_ID` et
  `WLM_FR_PISTE_CLIENT_SECRET`. Ils proviennent d'un compte PISTE gratuit (piste.gouv.fr) avec une application
  abonnée à Judilibre et à Légifrance.
- **États-Unis :** facultatif. La recherche de jurisprudence fonctionne sans clé, mais la clé de démonstration
  partagée ne permet qu'environ 10 recherches par jour et par adresse IP. Une clé api.data.gov gratuite dans
  `WLM_US_GOVINFO_KEY` relève cette limite.

Définissez-les comme variables d'environnement du serveur Fontes dans les paramètres MCP de votre application.
Une fois le programme d'installation disponible, il les demandera après l'installation, et son lanceur
**Ajouter ou modifier des clés** permettra de les modifier plus tard.

Par ailleurs, quelques sources indiquent dans leurs conditions que l'accès automatisé nécessite l'autorisation
de l'éditeur. Elles sont marquées OFF et restent désactivées. Une clé n'y change rien ; seule l'autorisation de
l'éditeur le peut (définissez alors `WLM_PERMITTED=<codes>`).

## Qu'est-ce qui quitte mon ordinateur ?

Vos recherches ne vont qu'à la source interrogée. Fontes ne tient aucune base de données et ne nécessite aucun
compte.

En dehors des sources, Fontes demande à PyPI une fois par jour s'il existe une version plus récente
(désactivable avec `FONTES_NO_UPDATE_CHECK=1`). Les comptages d'utilisation sont désactivés sauf si vous les
activez, et un rapport de bogue n'est envoyé qu'après que vous l'avez vu et confirmé. Votre application d'IA
voit votre conversation selon ses propres conditions.

Tous les détails : [PRIVACY.md](PRIVACY.md).

## Est-ce un conseil juridique ?

Non. Fontes est un outil de recherche. Il trouve des textes ; il ne vous dit pas ce qu'ils signifient pour votre
affaire, et son utilisation ne crée de relation avocat-client avec personne. L'application d'IA peut mal lire un
texte : lisez donc la décision ou la disposition complète avant de vous y fier. Pour un conseil, adressez-vous à
un avocat habilité là où votre question se pose.

## Qui le maintient ? Continuera-t-il de fonctionner ?

Une seule personne : Yüce Karapazar. Il n'y a aucune entreprise derrière Fontes, aucun contrat d'assistance et
aucun engagement de niveau de service. Aucun service juridique n'est proposé.

Les sources sont vérifiées une fois par jour et les résultats sont publiés sur la
[page d'état](https://ykarapazar.github.io/fontes/status/?lang=fr). Les sites des juridictions et des États
changent sans préavis : une source peut donc cesser de fonctionner à tout moment. Rien ne garantit qu'une source,
ou Fontes lui-même, continuera de fonctionner. Fontes est fourni « en l'état », sans garantie (sections 7 et 8
de la [LICENSE](../../../LICENSE)).

## Un texte est erroné ou périmé, ou une source ne fonctionne plus. Comment le signaler ?

- Ouvrez un ticket (issue) avec le formulaire « Broken or wrong source » :
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Indiquez la juridiction, ce que vous avez demandé,
  ce que vous avez obtenu, et la page officielle qui montre le bon texte.
- Ou demandez à votre application d'IA de « signaler un bogue de Fontes » (ou exécutez `fontes report-bug`).
  Vous voyez le rapport avant que quoi que ce soit ne soit envoyé.
- Ou écrivez à fontesmcp@proton.me.

N'incluez pas d'informations sur vos clients ni de faits confidentiels dans un rapport.

**Si vous gérez l'une des sources** et que quelque chose est erroné (vos conditions, votre robots.txt, vos
limites de requêtes), écrivez à fontesmcp@proton.me. La source sera corrigée ou désactivée.

## En quoi Fontes diffère-t-il des outils de recherche juridique hébergés ?

- **Il s'exécute sur votre ordinateur.** Il n'y a ni serveur Fontes ni compte. Cela signifie aussi qu'il ne
  fonctionne que dans les applications capables de lancer un serveur MCP local (Claude Desktop, Codex, Cursor,
  VS Code et similaires), et non dans les applications uniquement web qui n'acceptent que des connecteurs
  hébergés.
- **Il n'a pas de base de données.** Chaque recherche est envoyée en direct au site web ou à l'API de l'éditeur
  lui-même : les résultats sont donc aussi à jour que la source, et la qualité de la recherche est celle de la
  source. Il n'y a pas de recherche sémantique sur un index constitué.
- **Il n'impose aucune limite d'utilisation.** Fontes n'a pas de plafond mensuel d'appels. Il espace ses
  requêtes vers chaque site, et certaines sources limitent la vitesse ou la fréquence à laquelle elles peuvent
  être interrogées.
- **Il est open source.** Vous pouvez lire chaque adaptateur et voir exactement d'où provient chaque texte.
- **Aucun fournisseur ne se tient derrière lui.** Pas de contrat, pas de service d'assistance, pas d'engagement
  de disponibilité (voir « Qui le maintient ? »).

## Avec quelles applications et quels systèmes fonctionne-t-il ?

Toute application MCP capable d'exécuter un serveur local (stdio), par exemple Claude Desktop, Claude Code,
Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio et Cline. Fontes fonctionne sous
macOS, Windows et Linux, partout où uv fonctionne (Python 3.13+). Il n'est pas encore sur PyPI ; une fois qu'il
le sera, la plupart des applications n'auront besoin que d'une commande ou d'une entrée de configuration, et
Claude Desktop accepte un fichier `.mcpb` à ouvrir d'un double-clic. Un programme d'installation en un clic pour
Mac et Windows est en préparation. Il configure Claude Desktop, Codex, Claude Code, Cursor, VS Code, Windsurf,
Gemini CLI, Zed, LM Studio et Cline en une seule fois. Les étapes pour chaque application :
[INSTALL.md](INSTALL.md).

## Puis-je contribuer du code ?

Pas pour le moment. Les tickets (issues), les signalements de sources et les demandes de juridictions sont les
bienvenus. Voir [CONTRIBUTING.md](../../../CONTRIBUTING.md).
