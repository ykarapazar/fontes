> Aquesta és una traducció assistida per màquina. La versió anglesa és la que preval.

# Avís de privadesa de Fontes

Fontes s'executa al vostre ordinador. Les vostres cerques i els documents que obriu queden entre el
vostre ordinador, les fonts que cerqueu (les oficials, i CourtListener i Lexifina quan les useu,
vegeu més avall) i l'aplicació d'IA que feu servir (segons les condicions d'aquesta aplicació). El mateix Fontes no envia **res, per defecte**, als desenvolupadors
de Fontes.

## Què pot sortir del vostre ordinador, i quan

**1. Comprovació d'actualitzacions (activada per defecte).** Un cop al dia, Fontes pregunta a PyPI,
l'índex públic de paquets de Python, quina és la versió més nova. La petició no conté res sobre
vosaltres ni sobre la vostra feina; PyPI veu la vostra adreça IP, com en qualsevol baixada. Per
desactivar-la, definiu `FONTES_NO_UPDATE_CHECK=1` (l'avís dins de l'aplicació) i
`FONTES_NO_AUTO_UPDATE=1` (les actualitzacions automàtiques de l'instal·lador).

**2. Recomptes d'ús (desactivats tret que els activeu).** Si hi doneu el consentiment (opt-in), un cop
al dia Fontes envia:

- la versió de Fontes i la família del vostre sistema operatiu (macOS, Windows, Linux);
- per dia, quantes vegades s'ha utilitzat cada eina per a cada codi de jurisdicció, per exemple
  "2026-11-10, nl, search_caselaw, 12".

Aquest és el missatge complet. No inclou mai les vostres cerques, identificadors de documents o
d'assumptes, el text de documents, el vostre nom, un compte ni cap identificador de vosaltres o del
vostre ordinador. Els recomptes esperen al vostre ordinador (a la carpeta de memòria cau de Fontes,
`stats.json`) fins que s'envien; si l'enviament falla, esperen fins a l'endemà.

- **Activar-los**: responeu "y" quan l'instal·lador ho pregunti, o definiu `FONTES_STATS=1` per al
  servidor Fontes.
- **Desactivar-los**: torneu a executar l'instal·lador i premeu Retorn en aquesta pregunta, o elimineu
  `FONTES_STATS`. Suprimir `stats.json` descarta tot el que encara no s'ha enviat.

**3. Informes d'error (només quan n'envieu un).** Quan en demaneu un (`fontes report-bug`, o demanant a
la vostra aplicació d'IA que informi d'un error de Fontes), Fontes us mostra primer l'informe complet i
només l'envia si ho confirmeu. Conté la versió de Fontes, la família del vostre sistema operatiu, el
codi de jurisdicció, el nom de l'eina i el missatge d'error de la darrera crida fallida (amb les
vostres paraules de cerca i els identificadors eliminats), i una nota si n'escriviu una. No poseu
dades de clients a la nota. Per a això, Fontes conserva el darrer error al vostre ordinador
(`last-error.json` a la carpeta de memòria cau, substituït cada vegada); mai no s'envia per si sol.

**4. Lexifina (activat per defecte).** `get_law_on_date`, `get_law_history`, els 91 països i les lleis de l'Índia es llegeixen a través
del registre de legislació de Lexifina, de manera que van a Lexifina a més del lloc oficial o en lloc seu. Les vostres paraules de cerca, citacions i
dates van al servidor gratuït de Lexifina, `global-law.lexifina.com`, que gestiona Lexifina i no els
desenvolupadors de Fontes. Lexifina documenta que el seu servidor registra quina eina s'ha cridat i quant
ha durat, mai què s'ha demanat; Fontes no ho pot comprovar, i s'apliquen les condicions pròpies de
Lexifina. Lexifina veu la vostra adreça IP, com qualsevol servidor web. Per desactivar-ho completament,
definiu `WLM_LEXIFINA=0`; aquestes dues eines i aquests països deixen de funcionar i no s'hi envia res.

## On va i quant de temps es conserva

Els recomptes d'ús i els informes d'error van a un petit servidor gestionat pel desenvolupador de
Fontes (`relay.kinetra.fit`). No emmagatzema adreces IP: només s'utilitzen en memòria, breument, per
frenar els abusos de peticions, i el servidor web no conserva cap registre d'accés per a aquest
servidor. Els recomptes se sumen en totals diaris; els enviaments individuals no es conserven. Els
totals es conserven fins a 2 anys i els informes d'error fins a 1 any; després se suprimeixen. No es
ven ni es comparteix res.

Si no es pot accedir a aquest servidor, no s'envia res: els recomptes es queden al vostre ordinador i
els informes d'error remeten al gestor d'incidències (issue tracker).

## Qui n'és el responsable, i amb quina base

El responsable del tractament de les dades dels recomptes d'ús i dels informes d'error és Yüce
Karapazar, el desenvolupador de Fontes. Contacte: fontesmcp@proton.me.

La base jurídica és el vostre consentiment (article 6(1)(a) de l'UK GDPR i del RGPD de la UE). Els
recomptes d'ús només s'envien si hi doneu el consentiment, i un informe d'error només després que el
confirmeu. Podeu retirar el consentiment en qualsevol moment desactivant-los tal com s'ha descrit més
amunt; això no afecta el que s'hagi enviat abans.

## Contacte

Preguntes o sol·licituds: escriviu a fontesmcp@proton.me o obriu una incidència (issue) a
<https://github.com/ykarapazar/fontes/issues>.
