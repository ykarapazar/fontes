> Dette er ei maskinassistert omsetjing. Den engelske versjonen er den gjeldande.

# Personvernerklæring for Fontes

Fontes køyrer på datamaskina di. Søka dine og dokumenta du opnar, blir verande
mellom datamaskina di, dei offisielle kjeldene du søkjer i, og KI-appen du brukar (under
vilkåra til den appen). Fontes sjølv sender Fontes-utviklarane **ingenting som
standard**.

## Kva som kan forlate datamaskina di, og når

**1. Oppdateringskontroll (på som standard).** Éin gong om dagen spør Fontes PyPI, den offentlege
pakkeindeksen for Python, kva versjon som er den nyaste. Førespurnaden inneheld ingenting om deg eller arbeidet ditt;
PyPI ser IP-adressa di, som ved alle nedlastingar. For å slå han av, set `FONTES_NO_UPDATE_CHECK=1`
(meldinga i appen) og `FONTES_NO_AUTO_UPDATE=1` (dei automatiske oppdateringane til installasjonsprogrammet).

**2. Brukstal (av med mindre du slår dei på).** Om du seier ja (opt-in), sender Fontes éin gong om dagen:

- Fontes-versjonen og OS-familien din (macOS, Windows, Linux);
- per dag, kor mange gonger kvart verktøy vart brukt for kvar jurisdiksjonskode, til dømes
  «2026-11-10, nl, search_caselaw, 12».

Det er heile meldinga. Ho inneheld aldri søka dine, dokument- eller saks-ID-ar, dokumenttekst,
namnet ditt, ein konto eller nokon ID for deg eller datamaskina di. Tala ventar på datamaskina di
(i mellomlagermappa til Fontes, `stats.json`) til dei blir sende; om sendinga mislukkast, ventar dei til
neste dag.

- **Slå på (opt in)**: svar «j» når installasjonsprogrammet spør, eller set `FONTES_STATS=1` for Fontes-serveren.
- **Slå av (opt out)**: køyr installasjonsprogrammet på nytt og trykk Enter ved det spørsmålet, eller fjern
  `FONTES_STATS`. Slettar du `stats.json`, forkastar du alt som enno ikkje er sendt.

**3. Feilrapportar (berre når du sender ein).** Når du ber om ein (`fontes report-bug`, eller ber
KI-appen din rapportere ein feil i Fontes), viser Fontes deg heile rapporten først og sender han berre om
du stadfestar. Han inneheld Fontes-versjonen, OS-familien din, jurisdiksjonskoden, verktøynamnet og
feilmeldinga frå det siste mislukka verktøykallet (med søkjeorda og ID-ane dine fjerna), og
ein merknad om du skriv ein. Ikkje skriv klientopplysningar i merknaden. For å støtte dette held Fontes
på den siste feilen på datamaskina di (`last-error.json` i mellomlagermappa, erstatta kvar gong);
han blir aldri send åleine.

## Kvar det går, og kor lenge det blir teke vare på

Brukstal og feilrapportar går til ein liten server som Fontes-utviklaren driv
(`relay.kinetra.fit`). Han lagrar ingen IP-adresser: dei blir berre brukte i minnet, kortvarig, for å
stoppe flaumar, og nettserveren fører ingen tilgangslogg for han. Tala blir lagde saman til daglege
summar; einskilde innsendingar blir ikkje tekne vare på. Summane blir tekne vare på i opptil 2 år, feilrapportar i opptil
1 år, og blir så sletta. Ingenting blir selt eller delt.

Om den serveren ikkje kan nåast, blir ingenting sendt: tala blir verande på datamaskina di, og feilrapportar
viser deg i staden til saksoversikta (issue tracker).

## Kven som er ansvarleg, og på kva grunnlag

Behandlingsansvarleg for brukstal og feilrapportar er Yüce Karapazar, utviklaren av
Fontes. Kontakt: fontesmcp@proton.me.

Det rettslege grunnlaget er samtykket ditt (artikkel 6 nr. 1 bokstav a i UK GDPR og EUs personvernforordning, GDPR). Brukstal
blir berre sende om du seier ja (opt-in), og ein feilrapport berre etter at du har stadfesta han. Du kan trekkje
samtykket tilbake når som helst ved å slå av slik det er skildra ovanfor; dette påverkar ikkje det som vart sendt
før.

## Kontakt

Spørsmål eller førespurnader: send e-post til fontesmcp@proton.me, eller opprett ei sak på
<https://github.com/ykarapazar/fontes/issues>.
