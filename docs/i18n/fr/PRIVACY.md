> Ceci est une traduction assistée par machine. La version anglaise fait foi.

# Politique de confidentialité de Fontes

Fontes s'exécute sur votre ordinateur. Vos recherches et les documents que vous ouvrez restent
entre votre ordinateur, les sources officielles que vous interrogez et l'application d'IA que vous utilisez
(selon les propres conditions de cette application). Fontes lui-même n'envoie aux développeurs de Fontes
**rien par défaut**.

## Ce qui peut quitter votre ordinateur, et quand

**1. Vérification des mises à jour (activée par défaut).** Une fois par jour, Fontes demande à PyPI, l'index
public des paquets Python, quelle est la version la plus récente. La requête ne contient rien sur vous ni sur
votre travail ; PyPI voit votre adresse IP, comme pour tout téléchargement. Pour la désactiver, définissez
`FONTES_NO_UPDATE_CHECK=1` (l'avis dans l'application) et `FONTES_NO_AUTO_UPDATE=1` (les mises à jour
automatiques du programme d'installation).

**2. Comptages d'utilisation (désactivés sauf si vous les activez).** Si vous y consentez, une fois par jour
Fontes envoie :

- la version de Fontes et la famille de votre système d'exploitation (macOS, Windows, Linux) ;
- par jour, combien de fois chaque outil a été utilisé pour chaque code de juridiction, par exemple
  "2026-11-10, nl, search_caselaw, 12".

C'est l'intégralité du message. Il n'inclut jamais vos recherches, les identifiants de documents ou
d'affaires, le texte des documents, votre nom, un compte, ni aucun identifiant vous concernant ou concernant
votre ordinateur. Les comptages attendent sur votre ordinateur (dans le dossier cache de Fontes, `stats.json`)
jusqu'à leur envoi ; si l'envoi échoue, ils attendent le jour suivant.

- **Activer** : répondez « o » lorsque le programme d'installation le demande, ou définissez `FONTES_STATS=1`
  pour le serveur Fontes.
- **Désactiver** : relancez le programme d'installation et appuyez sur Entrée à cette question, ou supprimez
  `FONTES_STATS`. Supprimer `stats.json` efface tout ce qui n'a pas encore été envoyé.

**3. Rapports de bogue (uniquement lorsque vous en envoyez un).** Lorsque vous en demandez un
(`fontes report-bug`, ou en demandant à votre application d'IA de signaler un bogue de Fontes), Fontes vous
montre d'abord le rapport complet et ne l'envoie que si vous confirmez. Il contient la version de Fontes, la
famille de votre système d'exploitation, le code de juridiction, le nom de l'outil et le message d'erreur du
dernier appel d'outil en échec (vos termes de recherche et identifiants en étant retirés), et une note si vous
en rédigez une. Ne mettez pas d'informations sur vos clients dans la note. Pour permettre cela, Fontes conserve
la dernière erreur sur votre ordinateur (`last-error.json` dans son dossier cache, remplacé à chaque fois) ;
elle n'est jamais envoyée seule.

## Où cela va et combien de temps c'est conservé

Les comptages d'utilisation et les rapports de bogue sont envoyés à un petit serveur géré par le développeur de
Fontes (`relay.kinetra.fit`). Il ne stocke aucune adresse IP : elles ne sont utilisées qu'en mémoire,
brièvement, pour empêcher les envois massifs, et le serveur web ne tient aucun journal d'accès pour ce service.
Les comptages sont agrégés en totaux journaliers ; les envois individuels ne sont pas conservés. Les totaux sont
conservés jusqu'à 2 ans, les rapports de bogue jusqu'à 1 an, puis supprimés. Rien n'est vendu ni partagé.

Si ce serveur est injoignable, rien n'est envoyé : les comptages restent sur votre ordinateur et les rapports de
bogue vous renvoient plutôt vers le gestionnaire de tickets (issue tracker).

## Qui est responsable, et sur quelle base

Le responsable du traitement des comptages d'utilisation et des rapports de bogue est Yüce Karapazar, le
développeur de Fontes. Contact : fontesmcp@proton.me.

La base légale est votre consentement (article 6, paragraphe 1, point a), du RGPD britannique (UK GDPR) et du
RGPD de l'UE). Les comptages d'utilisation ne sont envoyés que si vous y consentez, et un rapport de bogue
seulement après que vous l'avez confirmé. Vous pouvez retirer votre consentement à tout moment en vous
désinscrivant comme décrit ci-dessus ; cela n'affecte pas ce qui a été envoyé auparavant.

## Contact

Questions ou demandes : écrivez à fontesmcp@proton.me, ou ouvrez un ticket (issue) sur
<https://github.com/ykarapazar/fontes/issues>.
