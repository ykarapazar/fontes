> Ceci est une traduction assistée par machine. La version anglaise fait foi.

# Fontes : questions et réponses

## Qu'est-ce que Fontes ?

Un serveur MCP gratuit et open source (Apache 2.0). Il permet à toute application qui parle le Model Context
Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI et d'autres) de rechercher des décisions de justice et la
législation en direct sur les sites des juridictions et des États, dans 125 juridictions et cours
internationales, ainsi que 91 autres pays via le registre de Lexifina (voir ci-dessous). Chaque résultat indique sa source et renvoie à l'original.

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

125 adaptateurs : 108 États membres de l'ONU, Hong Kong, le Kosovo, la Palestine, Taïwan, les DIFC Courts, les juridictions des États américains et
11 juridictions et organes internationaux (comme la Cour européenne des droits de l'homme, l'UE, la CIJ et
l'OMC).

La couverture varie beaucoup. Selon une règle stricte (les précédents de la juridiction suprême de droit commun,
ou la constitution et les lois de premier rang, atteints intégralement), 72 des 125 sont considérées comme
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
- **Juridictions des États américains :** oui. La jurisprudence des États (`us-states`) est désactivée tant que vous n'avez pas défini `WLM_US_COURTLISTENER_KEY` avec votre propre jeton d'API CourtListener gratuit. CourtListener est géré par l'organisation à but non lucratif Free Law Project ; ce n'est pas une source officielle, et chaque réponse le précise.

Définissez-les comme variables d'environnement du serveur Fontes dans les paramètres MCP de votre application.
Les programmes d'installation les demandent après l'installation, et leur lanceur
**Ajouter ou modifier des clés** permet de les modifier plus tard.

Par ailleurs, quelques sources indiquent dans leurs conditions que l'accès automatisé nécessite l'autorisation
de l'éditeur. Elles sont marquées OFF et restent désactivées. Une clé n'y change rien ; seule l'autorisation de
l'éditeur le peut (définissez alors `WLM_PERMITTED=<codes>`).

## D'où viennent les versions passées et les pays supplémentaires ?

De [Lexifina](https://github.com/lexifina/global-law), qui conserve le droit d'environ 200 pays sous forme d'historique git : chaque modification est un commit daté du jour de son entrée en vigueur. Fontes le lit via le serveur hébergé gratuit de Lexifina. Deux outils l'utilisent : `get_law_on_date` (une disposition telle qu'elle était en vigueur à une date, y compris dans le passé, avec la loi qui l'a modifiée en dernier) et `get_law_history` (chaque loi ayant modifié une disposition, ou la modification mot à mot entre deux dates). Fontes lit aussi de cette façon 91 autres pays et territoires, pour la législation seulement (par exemple l'Afrique du Sud, le Kenya, le Mexique, la Nouvelle-Zélande, la Russie, la Corée du Sud, la Belgique, la Lituanie, l'Ukraine, la Malaisie, la Thaïlande et l'Arabie saoudite). Ils sont distincts des 125 adaptateurs à couverture officielle en direct, et la couverture varie beaucoup selon le pays (le registre national du Kenya compte 9 textes). Les textes de loi indiens viennent aussi du registre de Lexifina, car les conditions d'India Code interdisent l'accès automatisé ; ses arrêts de la Cour suprême sont en direct.

Lexifina n'est pas l'éditeur officiel, et son registre n'est pas en direct : Lexifina vérifie chaque pays de temps à autre, et son propre rapport du 2026-11-26 comptait 338 ensembles de textes nationaux sur 383 comme non vérifiés au cours des 7 derniers jours. Chaque réponse nomme Lexifina comme source, renvoie à la page de l'éditeur officiel et indique jusqu'où va le registre.

Lexifina considère que les textes juridiques officiels ne sont pas protégés par le droit d'auteur ; dans certains pays, il copie donc des sites dont les conditions ou le robots.txt sont respectés par Fontes lui-même. Fontes continue de les respecter pour tout ce qu'il récupère lui-même ; ce qui passe par Lexifina suit le propre jugement de Lexifina, consigné pays par pays dans ses dépôts. Quelques-unes restreignent l'usage (l'éditeur du Kenya est sous licence CC BY-NC). Vos termes de recherche, citations et dates vont au serveur de Lexifina pour ces cas. Définissez `WLM_LEXIFINA=0` pour le désactiver. Le serveur gratuit accepte 60 appels par minute et 10 000 par jour et par adresse internet ; aucune clé ni compte. Fontes n'est pas affilié à Lexifina.

## Qu'est-ce qui quitte mon ordinateur ?

Vos recherches ne vont qu'à la source interrogée (pour les outils et les pays Lexifina, c'est le serveur de
Lexifina). Fontes ne tient aucune base de données et ne nécessite aucun
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
macOS, Windows et Linux, partout où uv fonctionne (Python 3.13+). Sur un Mac ou un PC Windows, un programme d'installation en un
clic configure Claude Desktop, Codex, Claude Code, Cursor, VS Code, Windsurf, Gemini CLI, Zed, LM Studio et Cline
en une seule fois. Les étapes pour chaque
application : [INSTALL.md](INSTALL.md).

## Puis-je contribuer du code ?

Pas pour le moment. Les tickets (issues), les signalements de sources et les demandes de juridictions sont les
bienvenus. Voir [CONTRIBUTING.md](../../../CONTRIBUTING.md).
