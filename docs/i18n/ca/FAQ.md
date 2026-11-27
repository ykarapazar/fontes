> Aquesta és una traducció assistida per màquina. La versió anglesa és la que preval.

# Fontes: preguntes i respostes

## Què és Fontes?

Un servidor MCP gratuït i de codi obert (Apache 2.0). Permet que qualsevol aplicació que parli el
Model Context Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI i altres) cerqui resolucions
judicials i legislació en directe des de llocs web judicials i governamentals en 125
jurisdiccions i tribunals internacionals, i 91 països més a través del registre de Lexifina (vegeu més avall).
Cada resultat indica la seva font i enllaça amb l'original.

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

125 adaptadors: 108 estats membres de l'ONU, Hong Kong, Kosovo, Palestina, Taiwan, els DIFC Courts, els tribunals estatals dels EUA i 11 tribunals i organismes internacionals (com ara el Tribunal Europeu de Drets Humans, la UE, la CIJ i
l'OMC).

La cobertura varia molt. Segons un criteri estricte (la jurisprudència del tribunal suprem de la
jurisdicció ordinària, o la constitució i les lleis, abastades íntegrament), 72 de les 125 compten com
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
- **Tribunals estatals dels EUA:** sí. La jurisprudència estatal (`us-states`) està desactivada fins que definiu `WLM_US_COURTLISTENER_KEY` amb el vostre propi token d'API gratuït de CourtListener. CourtListener el gestiona Free Law Project, una organització sense ànim de lucre; no és una font oficial, i cada resposta ho indica.

Definiu-les com a variables d'entorn per al servidor Fontes a la configuració MCP de la vostra
aplicació. Els instal·ladors us les demanen després de la instal·lació, i la drecera
**Add or change keys** permet canviar-les més tard.

A banda d'això, algunes fonts diuen a les seves condicions que l'accés automatitzat requereix el
permís de l'editor. Estan marcades com a OFF i es queden desactivades. Una clau no ho canvia; només el
permís de l'editor ho canvia (llavors definiu `WLM_PERMITTED=<codes>`).

## D'on vénen les versions passades i els països addicionals?

Del [registre de Lexifina](https://github.com/lexifina/global-law), que conserva la llei de vora 200
països com a historial de git: cada canvi és una confirmació datada el dia en què va entrar en vigor.
Fontes la llegeix a través del servidor allotjat gratuït de Lexifina. Dues eines en fan ús:
`get_law_on_date` (una disposició tal com estava en vigor en una data, també en el passat, amb la llei
que la va canviar per darrera vegada) i `get_law_history` (cada llei que ha canviat una disposició, o el
canvi paraula per paraula entre dues dates). Fontes també llegeix així 91 països i territoris més, només
per a legislació (per exemple Sud-àfrica, Kenya, Mèxic, Nova Zelanda, Rússia, Corea del Sud, Bèlgica,
Lituània, Ucraïna, Malàisia, Tailàndia i Aràbia Saudita). Són independents dels 125 adaptadors amb
cobertura oficial en directe, i la cobertura per país varia molt (el registre nacional de Kenya conté 9
lleis). Les lleis de l'Índia també provenen del registre de Lexifina, perquè les condicions d'India Code
prohibeixen l'accés automatitzat; les seves sentències del Tribunal Suprem són en directe.

Lexifina no és l'editor oficial, i el seu registre no és en directe: Lexifina el revisa de tant en tant,
i el seu propi informe del 2026-11-26 va comptar 338 de 383 cossos normatius nacionals com a no revisats
en els darrers 7 dies. Cada resposta indica Lexifina com a font, enllaça la pàgina de l'editor oficial i
diu fins on arriba el registre.

Lexifina considera que els textos jurídics oficials no estan protegits per drets d'autor, de manera que
en alguns països copia llocs web les condicions o el robots.txt dels quals Fontes sí que respecta. Fontes
continua respectant-los per a tot el que obté directament; el que arriba a través de Lexifina segueix el
criteri propi de Lexifina, registrat per país als seus repositoris. Alguns en restringeixen l'ús (l'editor
de Kenya: CC BY-NC). Per a aquests casos, les vostres paraules de cerca, citacions i dates van al servidor
de Lexifina. Definiu `WLM_LEXIFINA=0` per desactivar-ho. El servidor gratuït permet 60 crides per minut i
10.000 al dia per adreça d'internet; sense clau ni compte. Fontes no està afiliada a Lexifina.

## Què surt del meu ordinador?

Les vostres cerques només van a la font on es cerca (per a les eines i els països de Lexifina, al
servidor de Lexifina). Fontes no manté cap base de dades i no requereix cap compte.

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
Fontes funciona a macOS, Windows i Linux, a qualsevol lloc on funcioni uv (Python 3.13+). En un Mac o un PC amb Windows, un instal·lador d'un clic
configura Claude Desktop, Codex, Claude Code, Cursor, VS Code, Windsurf, Gemini CLI, Zed, LM Studio i
Cline alhora. Passos per a cada aplicació: [INSTALL.md](INSTALL.md).

## Puc contribuir-hi amb codi?

De moment, no. Les incidències (issues), els informes sobre fonts i les sol·licituds de jurisdiccions
són benvinguts. Vegeu [CONTRIBUTING.md](../../../CONTRIBUTING.md).
