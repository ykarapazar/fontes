> Aquesta és una traducció assistida per màquina. La versió anglesa és la que preval.

# Fontes: preguntes i respostes

## Què és Fontes?

Un servidor MCP gratuït i de codi obert (Apache 2.0). Permet que qualsevol aplicació que parli el
Model Context Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI i altres) cerqui resolucions
judicials i legislació en directe des de llocs web judicials i governamentals de més de 120
jurisdiccions i tribunals internacionals (124 adaptadors). Cada resultat indica la seva font i enllaça
amb l'original.

## Els textos són oficials?

Majoritàriament, però no sempre.

- La majoria de fonts les gestiona un tribunal, un ministeri o un butlletí oficial.
- Alguns textos consolidats els publica un govern, però són expressament no oficials: només el
  butlletí oficial és autèntic.
- Unes quantes fonts ni tan sols són llocs governamentals (per exemple LexiVox, LawPhil, Maqam,
  Wikisource).

Fontes afegeix un avís "Unofficial source" (font no oficial) a cada resposta que prové d'una
d'aquestes. Abans de citar res, comproveu la publicació oficial. La taula de cobertura del
[README](README.md#cobertura) i `list_jurisdictions` indiquen la font de cada jurisdicció.

## Quines jurisdiccions cobreix, i fins a quin punt?

124 adaptadors: 108 estats membres de l'ONU, Hong Kong, Kosovo, Palestina, Taiwan, els DIFC Courts i
11 tribunals i organismes internacionals (com ara el Tribunal Europeu de Drets Humans, la UE, la CIJ i
l'OMC).

La cobertura varia molt. Segons un criteri estricte (la jurisprudència del tribunal suprem de la
jurisdicció ordinària, o la constitució i les lleis, abastades íntegrament), 72 de les 124 compten com
a cobertes. [COVERAGE.md](../../COVERAGE.md) indica, per a cada jurisdicció, què abasta Fontes, què no
abasta i per què.

## Necessito una clau d'API?

Per a gairebé totes les jurisdiccions, no. Algunes fonts necessiten una clau gratuïta: vegeu
[KEYS.md](KEYS.md).

- **França:** sí. França queda desactivada fins que definiu `WLM_FR_PISTE_CLIENT_ID` i
  `WLM_FR_PISTE_CLIENT_SECRET`. S'obtenen d'un compte gratuït de PISTE (piste.gouv.fr) amb una
  aplicació subscrita a Judilibre i Légifrance.
- **Estats Units:** opcional. La cerca de jurisprudència funciona sense clau, però la clau de
  demostració compartida només permet unes 10 cerques al dia per adreça IP. Una clau gratuïta
  d'api.data.gov a `WLM_US_GOVINFO_KEY` augmenta aquest límit.

Definiu-les com a variables d'entorn per al servidor Fontes a la configuració MCP de la vostra
aplicació. Quan surti l'instal·lador, us les demanarà després de la instal·lació, i la seva drecera
**Add or change keys** permet canviar-les més tard.

A banda d'això, algunes fonts diuen a les seves condicions que l'accés automatitzat requereix el
permís de l'editor. Estan marcades com a OFF i es queden desactivades. Una clau no ho canvia; només el
permís de l'editor ho canvia (llavors definiu `WLM_PERMITTED=<codes>`).

## Què surt del meu ordinador?

Les vostres cerques només van a la font on es cerca. Fontes no manté cap base de dades i no requereix
cap compte.

A banda de les fonts, Fontes pregunta a PyPI un cop al dia si hi ha una versió més nova (desactiveu-ho
amb `FONTES_NO_UPDATE_CHECK=1`). Els recomptes d'ús estan desactivats tret que els activeu, i un
informe d'error només s'envia després que l'hàgiu vist i confirmat. La vostra aplicació d'IA veu la
vostra conversa segons les seves pròpies condicions.

Tots els detalls: [PRIVACY.md](PRIVACY.md).

## Això és assessorament jurídic?

No. Fontes és una eina de recerca. Troba textos; no us diu què signifiquen per al vostre cas, i
utilitzar-lo no crea cap relació advocat-client amb ningú. L'aplicació d'IA pot llegir malament un
text, així que llegiu la resolució o la disposició completa abans de confiar-hi. Per obtenir
assessorament, consulteu un advocat habilitat al lloc on sorgeix la vostra qüestió.

## Qui el manté? Continuarà funcionant?

Una persona: Yüce Karapazar. No hi ha cap empresa al darrere de Fontes, ni contracte de suport, ni
compromís de nivell de servei. No s'ofereixen serveis jurídics.

Les fonts es comproven un cop al dia i els resultats es publiquen a la
[pàgina d'estat](https://ykarapazar.github.io/fontes/status/?lang=ca). Els llocs web judicials i
governamentals canvien sense avís, de manera que una font pot deixar de funcionar en qualsevol
moment. No hi ha cap garantia que cap font, ni el mateix Fontes, continuï funcionant. Fontes es
proporciona "tal com és", sense garantia (seccions 7 i 8 de la [LICENSE](../../../LICENSE)).

## Un text és erroni, està desactualitzat o una font no funciona. Com ho comunico?

- Obriu una incidència (issue) amb el formulari "Broken or wrong source":
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Digueu quina jurisdicció, què heu
  preguntat, què heu obtingut i la pàgina oficial que mostra el text correcte.
- O demaneu a la vostra aplicació d'IA que "informi d'un error de Fontes" (o executeu
  `fontes report-bug`). Veieu l'informe abans que s'enviï res.
- O escriviu a fontesmcp@proton.me.

No incloeu dades de clients ni fets confidencials en un informe.

**Si gestioneu una de les fonts** i alguna cosa no és correcta (les vostres condicions, el robots.txt,
els límits de peticions), escriviu a fontesmcp@proton.me. La font es corregirà o es desactivarà.

## En què es diferencia Fontes de les eines de recerca jurídica allotjades?

- **S'executa al vostre ordinador.** No hi ha cap servidor de Fontes ni cap compte. Això també vol dir
  que només funciona en aplicacions que poden iniciar un servidor MCP local (Claude Desktop, Codex,
  Cursor, VS Code i similars), no en aplicacions només web que només accepten connectors allotjats.
- **No té base de dades.** Cada cerca va en directe al lloc web o l'API del mateix editor, de manera
  que els resultats són tan actuals com la font, i la qualitat de la cerca és la de la mateixa font. No
  hi ha cerca semàntica sobre un índex seleccionat.
- **No imposa cap límit d'ús.** Fontes no té cap topall mensual de crides. Espaia les peticions a cada
  lloc, i algunes fonts limiten la rapidesa o la freqüència amb què se les pot consultar.
- **És de codi obert.** Podeu llegir cada adaptador i veure exactament d'on prové cada text.
- **No hi ha cap proveïdor al darrere.** Cap contracte, servei d'assistència ni compromís de
  disponibilitat (vegeu "Qui el manté?").

## Amb quines aplicacions i sistemes funciona?

Amb qualsevol aplicació MCP que pugui executar un servidor local (stdio), per exemple Claude Desktop,
Claude Code, Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio i Cline.
Fontes funciona a macOS, Windows i Linux, a qualsevol lloc on funcioni uv (Python 3.13+). Encara no és
a PyPI; quan hi sigui, la majoria d'aplicacions necessitaran una ordre o una entrada de configuració, i
Claude Desktop accepta un fitxer `.mcpb` que s'obre amb doble clic. Hi ha en camí un instal·lador d'un
clic per a Mac i Windows. Configura Claude Desktop, Codex, Claude Code, Cursor, VS Code, Windsurf,
Gemini CLI, Zed, LM Studio i Cline alhora. Passos per a cada aplicació: [INSTALL.md](INSTALL.md).

## Puc contribuir-hi amb codi?

De moment, no. Les incidències (issues), els informes sobre fonts i les sol·licituds de jurisdiccions
són benvinguts. Vegeu [CONTRIBUTING.md](../../../CONTRIBUTING.md).
