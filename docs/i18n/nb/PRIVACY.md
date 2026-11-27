> Dette er en maskinassistert oversettelse. Den engelske versjonen er den gjeldende.

# Personvernerklæring for Fontes

Fontes kjører på datamaskinen din. Søkene dine og dokumentene du åpner, forblir mellom
datamaskinen din, kildene du søker i (de offisielle, pluss CourtListener og Lexifina der du bruker
dem, se nedenfor), og AI-appen du bruker (under den appens egne vilkår). Fontes selv sender **som standard ingenting** til utvikleren av Fontes.

## Hva som kan forlate datamaskinen din, og når

**1. Oppdateringssjekk (på som standard).** Én gang om dagen spør Fontes PyPI, den offentlige
indeksen over Python-pakker, hvilken versjon som er den nyeste. Forespørselen inneholder ingenting
om deg eller arbeidet ditt; PyPI ser IP-adressen din, som ved enhver nedlasting. For å slå det av
setter du `FONTES_NO_UPDATE_CHECK=1` (meldingen i appen) og `FONTES_NO_AUTO_UPDATE=1`
(installasjonsprogrammets automatiske oppdateringer).

**2. Brukstall (av med mindre du slår dem på).** Hvis du sier ja, sender Fontes én gang om
dagen:

- versjonen av Fontes og familien til operativsystemet ditt (macOS, Windows, Linux);
- per dag, hvor mange ganger hvert verktøy ble brukt for hver jurisdiksjonskode, for eksempel
  "2026-11-10, nl, search_caselaw, 12".

Det er hele meldingen. Den inneholder aldri søkene dine, dokument- eller saks-ID-er,
dokumenttekst, navnet ditt, en konto eller noen ID for deg eller datamaskinen din. Tallene venter
på datamaskinen din (i hurtigbuffermappen til Fontes, `stats.json`) til de sendes; hvis sendingen
mislykkes, venter de til neste dag.

- **Slå på**: svar "y" når installasjonsprogrammet spør, eller sett `FONTES_STATS=1` for
  Fontes-serveren.
- **Slå av**: kjør installasjonsprogrammet på nytt og trykk Enter ved det spørsmålet, eller fjern
  `FONTES_STATS`. Hvis du sletter `stats.json`, forsvinner alt som ennå ikke er sendt.

**3. Feilrapporter (bare når du sender en).** Når du ber om en (`fontes report-bug`, eller du ber
AI-appen din om å rapportere en feil i Fontes), viser Fontes deg først hele rapporten og sender den
bare hvis du bekrefter. Den inneholder versjonen av Fontes, familien til operativsystemet ditt,
jurisdiksjonskoden, verktøyets navn og feilmeldingen fra det siste verktøykallet som mislyktes
(med søkeordene og ID-ene dine fjernet), og en merknad hvis du skriver en. Ikke skriv klientdata i
merknaden. For dette formålet beholder Fontes den siste feilen på datamaskinen din
(`last-error.json` i hurtigbuffermappen, erstattes hver gang); den sendes aldri av seg selv.

**4. Lexifina (på som standard).** `get_law_on_date`, `get_law_history`, de 91 landene og indiske lover leses gjennom Lexifinas register over loven, så de går til Lexifina i tillegg til eller i stedet for det offisielle nettstedet. Søkeordene, siteringene og
datoene dine sendes til Lexifinas gratis server, `global-law.lexifina.com`, som drives av Lexifina,
ikke av utviklerne av Fontes. Lexifina dokumenterer at serveren logger hvilket verktøy som ble kalt og
hvor lang tid det tok, aldri hva som ble spurt; Fontes kan ikke kontrollere det, og Lexifinas egne
vilkår gjelder. Lexifina ser IP-adressen din, som enhver webserver gjør. For å slå Lexifina helt av
setter du `WLM_LEXIFINA=0`; de to verktøyene og landene slutter da å virke, og ingenting sendes dit.

## Hvor det sendes, og hvor lenge det oppbevares

Brukstall og feilrapporter sendes til en liten server som utvikleren av Fontes driver
(`relay.kinetra.fit`). Den lagrer ikke IP-adresser: de brukes bare kort i minnet for å stoppe
oversvømmelser, og nettserveren fører ingen tilgangslogg for den. Tallene legges sammen til
daglige totaler; enkeltsendinger oppbevares ikke. Totaler oppbevares i opptil 2 år, feilrapporter
i opptil 1 år, og slettes deretter. Ingenting selges eller deles.

Hvis den serveren ikke kan nås, sendes ingenting: tallene blir på datamaskinen din, og
feilrapporter viser deg i stedet til issue-trackeren.

## Hvem som er ansvarlig, og på hvilket grunnlag

Behandlingsansvarlig for brukstall og feilrapporter er Yüce Karapazar, utvikleren av Fontes.
Kontakt: fontesmcp@proton.me.

Rettsgrunnlaget er samtykket ditt (artikkel 6 nr. 1 bokstav a i UK GDPR og EUs
personvernforordning). Brukstall sendes bare hvis du sier ja, og en feilrapport bare etter at du
har bekreftet den. Du kan når som helst trekke tilbake samtykket ved å slå dem av som beskrevet
ovenfor; det påvirker ikke det som allerede er sendt.

## Kontakt

Spørsmål eller forespørsler: send e-post til fontesmcp@proton.me, eller opprett et issue på
<https://github.com/ykarapazar/fontes/issues>.
