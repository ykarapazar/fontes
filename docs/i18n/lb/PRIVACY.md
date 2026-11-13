> Dëst ass eng maschinnegestëtzt Iwwersetzung. Déi englesch Versioun ass moossgeblech.

# Dateschutzerklärung vu Fontes

Fontes leeft op Ärem Computer. Är Sichen an d'Dokumenter, déi Dir opmaacht, bleiwen tëscht Ärem
Computer, den offizielle Quellen, an deenen Dir sicht, an der KI-App, déi Dir benotzt (ënnert den
eegene Konditioune vun där App). Fontes selwer schéckt den Entwéckler vu Fontes **standardméisseg
näischt**.

## Wat Äre Computer verloosse kann, a wéini

**1. Update-Kontroll (standardméisseg un).** Eemol am Dag freet Fontes bei PyPI, dem ëffentlechen
Index vu Python-Packagen, wéi eng Versioun déi neiste ass. D'Ufro enthält näischt iwwer Iech oder
Är Aarbecht; PyPI gesäit Är IP-Adress, wéi bei all Download. Fir dat auszeschalten, setzt
`FONTES_NO_UPDATE_CHECK=1` (den Hiwäis an der App) an `FONTES_NO_AUTO_UPDATE=1` (déi automatesch
Updates vum Installatiounsprogramm).

**2. Notzungszuelen (aus, ausser Dir schalt se an).** Wann Dir zoustëmmt, schéckt Fontes eemol am
Dag:

- d'Versioun vu Fontes an d'Famill vun Ärem Betribssystem (macOS, Windows, Linux);
- pro Dag, wéi dacks all Tool fir all Code vun enger Rechtsuerdnung benotzt gouf, zum Beispill
  "2026-11-10, nl, search_caselaw, 12".

Dat ass de ganze Message. E enthält ni Är Sichen, Dokument- oder Dossiers-IDen, Dokumententext, Ären
Numm, e Kont, oder iergendeng ID fir Iech oder Äre Computer. D'Zuele waarden op Ärem Computer (am
Cache-Dossier vu Fontes, `stats.json`), bis se geschéckt ginn; wann d'Schécken net geet, waarde se
bis den nächsten Dag.

- **Aschalten**: Äntwert "y", wann den Installatiounsprogramm freet, oder setzt `FONTES_STATS=1`
  fir de Fontes-Server.
- **Ausschalten**: Loosst den Installatiounsprogramm nach eng Kéier lafen an dréckt bei där Fro
  Enter, oder läscht `FONTES_STATS`. Wann Dir `stats.json` läscht, ass alles fort, wat nach net
  geschéckt gouf.

**3. Feelerberichter (just wann Dir een schéckt).** Wann Dir ee frot (`fontes report-bug`, oder
Dir frot Är KI-App, e Feeler vu Fontes ze mellen), weist Fontes Iech fir d'éischt de komplette
Bericht a schéckt en just, wann Dir bestätegt. E enthält d'Versioun vu Fontes, d'Famill vun Ärem
Betribssystem, de Code vun der Rechtsuerdnung, den Numm vum Tool an d'Feelermeldung vum leschten
Tool-Opruff, deen net geklappt huet (mat Äre Sichwierder an IDen erausgeholl), an eng Notiz, wann
Dir eng schreift. Schreift keng Donnéeë vu Clienten an d'Notiz. Dofir hält Fontes de leschte
Feeler op Ärem Computer (`last-error.json` a sengem Cache-Dossier, gëtt all Kéier ersat); e gëtt ni
eleng geschéckt.

## Wouhin et geet a wéi laang et gehale gëtt

Notzungszuelen a Feelerberichter ginn op e klengen Server, deen den Entwéckler vu Fontes bedreift
(`relay.kinetra.fit`). E späichert keng IP-Adressen: si ginn just kuerz am Späicher benotzt, fir
Iwwerflutunge ze stoppen, an de Webserver féiert keen Accès-Log dofir. D'Zuele ginn zu
Dagestotaler addéiert; eenzel Iwwermëttlunge ginn net gehal. Totaler ginn bis zu 2 Joer gehal,
Feelerberichter bis zu 1 Joer, a dann geläscht. Näischt gëtt verkaaft oder weiderginn.

Wann deen Server net z'erreechen ass, gëtt näischt geschéckt: d'Zuele bleiwen op Ärem Computer,
an d'Feelerberichter weisen Iech amplaz dovunner op den Issue-Tracker.

## Wien verantwortlech ass, a mat wéi enger Grondlag

De Verantwortleche fir d'Veraarbechtung vun Notzungszuelen a Feelerberichter ass Yüce Karapazar,
den Entwéckler vu Fontes. Kontakt: fontesmcp@proton.me.

D'Rechtsgrondlag ass Är Awëllegung (Artikel 6(1)(a) vun der UK GDPR an der EU-DSGVO).
Notzungszuele ginn just geschéckt, wann Dir zoustëmmt, an e Feelerbericht just, nodeems Dir en
bestätegt hutt. Dir kënnt Är Awëllegung zu all Moment zréckzéien, andeems Dir se ausschalt, wéi
uewen beschriwwen; dat huet keen Effekt op dat, wat virdru geschéckt gouf.

## Kontakt

Froen oder Ufroen: schreift un fontesmcp@proton.me, oder maacht en Issue op
<https://github.com/ykarapazar/fontes/issues> op.
