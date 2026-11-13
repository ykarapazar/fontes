> Dëst ass eng maschinnegestëtzt Iwwersetzung. Déi englesch Versioun ass moossgeblech.

# Fontes: Froen an Äntwerten

## Wat ass Fontes?

E gratis Open-Source-MCP-Server (Apache 2.0). Mat him kann all App, déi d'Model Context Protocol
schwätzt (Claude, Codex, Cursor, VS Code, Gemini CLI an anerer), Geriichtsentscheedungen a
Gesetzgebung live op de Websäite vu Geriichter a Regierungen duerchsichen, a méi wéi 120
Rechtsuerdnungen an internationale Geriichter (124 Adapteren). All Resultat nennt seng Quell a
verlinkt op d'Original.

## Sinn d'Texter offiziell?

Meeschtens, mä net ëmmer.

- Déi meescht Quelle ginn vun engem Geriicht, engem Ministère oder engem offiziellen Amtsblat
  bedriwwen.
- E puer konsolidéiert Texter ginn vun enger Regierung publizéiert, sinn awer ausdrécklech
  inoffiziell: just den offiziellen Amtsblat ass authentesch.
- E puer Quelle sinn guer keng Websäite vun enger Regierung (zum Beispill LexiVox, LawPhil, Maqam,
  Wikisource).

Fontes setzt bei all Äntwert, déi aus enger vun dëse Quelle kënnt, en Hiwäis „Inoffiziell Quell“
derbäi. Ier Dir eppes zitéiert, kontrolléiert déi offiziell Publikatioun. D'Ofdeckungstabell an der
[README](README.md#ofdeckung) an `list_jurisdictions` nennen d'Quell fir all Rechtsuerdnung.

## Wéi eng Rechtsuerdnungen deckt et of, a wéi gutt?

124 Adapteren: 108 UNO-Memberstaaten, Hong Kong, de Kosovo, Palestina, Taiwan, d'DIFC Courts an 11
international Geriichter an Organer (wéi den Europäesche Geriichtshaff fir Mënscherechter, d'EU,
den ICJ an d'WTO).

D'Ofdeckung ass ganz ënnerschiddlech. No enger strenger Reegel (d'Präjudizer vum iewechsten
allgemenge Geriicht, oder d'Verfassung an d'Haaptgesetzer, komplett erreecht) gëllen 72 vun de 124
als ofgedeckt. [COVERAGE.md](COVERAGE.md) gëtt fir all Rechtsuerdnung un, wat Fontes erreecht, wat
net, a firwat.

## Brauch ech en API-Schlëssel?

Fir bal all Rechtsuerdnung net. E puer Quelle brauchen e gratis Schlëssel: kuckt
[KEYS.md](KEYS.md).

- **Frankräich:** jo. Frankräich ass aus, bis Dir `WLM_FR_PISTE_CLIENT_ID` an
  `WLM_FR_PISTE_CLIENT_SECRET` setzt. Dës kritt Dir mat engem gratis PISTE-Kont (piste.gouv.fr) mat
  enger App, déi op Judilibre a Légifrance abonnéiert ass.
- **Vereenegt Staaten:** fakultativ. D'Sich an der Rechtsprechung funktionéiert ouni Schlëssel, mä
  de gedeelten Demo-Schlëssel erlaabt just ongeféier 10 Sichen den Dag pro IP-Adress. E gratis
  api.data.gov-Schlëssel an `WLM_US_GOVINFO_KEY` hieft dat un.

Setzt dës als Ëmfeldvariabele fir de Fontes-Server an den MCP-Astellunge vun Ärer App. Soubal den
Installatiounsprogramm eraus ass, freet en no der Installatioun dono, a mat sengem Starter
**Add or change keys** ännert Dir se méi spéit.

Doriwwer eraus soen e puer Quellen an hire Konditiounen, datt den automatiséierten Zougang
d'Erlaabnes vum Editeur brauch. Si sinn als OFF markéiert a bleiwen aus. E Schlëssel ännert dorun
näischt; just d'Erlaabnes vum Editeur mécht dat (setzt dann `WLM_PERMITTED=<codes>`).

## Wat verléisst mäi Computer?

Är Sichen ginn just un d'Quell, an där gesicht gëtt. Fontes féiert keng Datebank a brauch kee Kont.

Nieft de Quelle freet Fontes eemol am Dag bei PyPI, ob et eng méi nei Versioun gëtt (auszeschalte
mat `FONTES_NO_UPDATE_CHECK=1`). Notzungszuele sinn aus, ausser Dir schalt se an, an e
Feelerbericht gëtt just geschéckt, nodeems Dir en gesinn a bestätegt hutt. Är KI-App gesäit Äre
Gespréich ënnert hiren eegene Konditiounen.

All Detailer: [PRIVACY.md](PRIVACY.md).

## Ass dat Rechtsberodung?

Nee. Fontes ass e Recherche-Tool. Et fënnt Texter; et seet Iech net, wat se fir Äre Fall bedeiten,
a seng Notzung schaaft mat kengem eng Bezéiung tëscht Affekot a Client. D'KI-App kann en Text
falsch liesen, also liest déi ganz Entscheedung oder Bestëmmung, ier Dir Iech drop verloosst. Fir
eng Berodung frot en Affekot, deen do zougelooss ass, wou Är Fro sech stellt.

## Wien entwéckelt et weider? Funktionéiert et och weiderhin?

Eng Persoun: Yüce Karapazar. Hannert Fontes steet keng Firma, et gëtt kee Support-Kontrakt a kee
Verspriechen iwwer de Serviceniveau. Et ginn keng juristesch Déngschtleeschtungen ugebueden.

D'Quelle ginn eemol am Dag kontrolléiert, an d'Resultater ginn op der
[Statussäit](https://ykarapazar.github.io/fontes/status/?lang=lb) publizéiert. Websäite vu
Geriichter a Regierungen änneren sech ouni Ukënnegung, also kann eng Quell zu all Moment
ausfalen. Et gëtt keng Garantie, datt eng Quell, oder Fontes selwer, weider funktionéiert. Fontes
gëtt „sou wéi et ass“ zur Verfügung gestallt, ouni Garantie (Sektiounen 7 an 8 vun der
[LICENSE](../../../LICENSE)).

## En Text ass falsch oder veralt, oder eng Quell funktionéiert net. Wéi mellen ech dat?

- Maacht en Issue mam Formulaire "Broken or wrong source" op:
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Sot, wéi eng Rechtsuerdnung, wat Dir
  gefrot hutt, wat Dir kritt hutt, an déi offiziell Säit, op där de richtegen Text steet.
- Oder frot Är KI-App, „e Feeler vu Fontes ze mellen“ (oder lafe loosst `fontes report-bug`). Dir
  gesitt de Bericht, ier eppes geschéckt gëtt.
- Oder schreift un fontesmcp@proton.me.

Schreift keng Donnéeë vu Clienten a keng vertraulech Fakten an e Bericht.

**Wann Dir eng vun de Quelle bedreift** an eppes ass net richteg (Är Konditiounen, Är robots.txt,
Är Rate-Limiten), schreift un fontesmcp@proton.me. D'Quell gëtt verbessert oder ausgeschalt.

## Wat ënnerscheet Fontes vu gehoste Tools fir juristesch Recherche?

- **Et leeft op Ärem Computer.** Et gëtt kee Fontes-Server a kee Kont. Dat heescht och, datt et
  just an Apps funktionéiert, déi e lokale MCP-Server starte kënnen (Claude Desktop, Codex, Cursor,
  VS Code an ähnlech), net an Apps, déi just am Web lafen an just gehost Connectoren akzeptéieren.
- **Et huet keng Datebank.** All Sich geet live op déi eege Websäit oder API vum Editeur, also sinn
  d'Resultater esou aktuell wéi d'Quell, an d'Qualitéit vun der Sich ass déi vun der Quell selwer.
  Et gëtt keng semantesch Sich an engem kuratéierten Index.
- **Et setzt keng Notzungslimitt.** Fontes huet keng monatlech Maximalzuel vun Opriff. Et verdeelt
  seng Ufroen un all Websäit, an e puer Quelle limitéieren, wéi séier oder wéi dacks se ofgefrot
  kënne ginn.
- **Et ass Open Source.** Dir kënnt all Adapter liesen a genee gesinn, wouhier all Text kënnt.
- **Et steet kee Fournisseur dohannert.** Kee Kontrakt, kee Support-Desk a kee Verspriechen iwwer
  d'Disponibilitéit (kuckt „Wien entwéckelt et weider?“).

## Mat wéi engen Apps a Systemer funktionéiert et?

Mat all MCP-App, déi e lokale (stdio-)Server lafe loosse kann, zum Beispill Claude Desktop, Claude
Code, Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio a Cline. Fontes
leeft op macOS, Windows a Linux, iwwerall do, wou uv leeft (Python 3.13+). En Installatiounsprogramm mat engem
Klick fir Mac a Windows ass ënnerwee. En riicht Claude Desktop, Codex, Claude Code, Cursor, VS Code,
Windsurf, Gemini CLI, Zed, LM Studio a Cline an engem Gang an. Schrëtt fir all App:
[INSTALL.md](INSTALL.md).

## Kann ech Code bäidroen?

Am Moment net. Issues, Mellungen iwwer Quellen an Ufroe fir Rechtsuerdnunge sinn wëllkomm. Kuckt
[CONTRIBUTING.md](../../../CONTRIBUTING.md).
