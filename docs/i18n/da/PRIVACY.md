> Dette er en maskinstøttet oversættelse. Den engelske version er den gældende.

# Fontes' privatlivspolitik

Fontes kører på din computer. Dine søgninger og de dokumenter, du åbner, forbliver mellem din
computer, de officielle kilder, du søger i, og den AI-app, du bruger (under den apps egne
vilkår). Fontes selv sender **som standard intet** til Fontes' udvikler.

## Hvad der kan forlade din computer, og hvornår

**1. Opdateringstjek (slået til som standard).** Én gang om dagen spørger Fontes PyPI, det
offentlige indeks over Python-pakker, hvilken version der er den nyeste. Forespørgslen indeholder
intet om dig eller dit arbejde; PyPI ser din IP-adresse, som ved enhver download. For at slå det
fra skal du sætte `FONTES_NO_UPDATE_CHECK=1` (meddelelsen i appen) og `FONTES_NO_AUTO_UPDATE=1`
(installationsprogrammets automatiske opdateringer).

**2. Brugstal (slået fra, medmindre du slår dem til).** Hvis du siger ja, sender Fontes én gang
om dagen:

- Fontes' version og dit styresystems familie (macOS, Windows, Linux);
- pr. dag, hvor mange gange hvert værktøj blev brugt for hver jurisdiktionskode, for eksempel
  "2026-11-10, nl, search_caselaw, 12".

Det er hele meddelelsen. Den indeholder aldrig dine søgninger, dokument- eller sags-id'er,
dokumenttekst, dit navn, en konto eller noget id for dig eller din computer. Tallene venter på
din computer (i Fontes' cachemappe, `stats.json`), indtil de sendes; hvis afsendelsen mislykkes,
venter de til næste dag.

- **Slå til**: svar "y", når installationsprogrammet spørger, eller sæt `FONTES_STATS=1` for
  Fontes-serveren.
- **Slå fra**: kør installationsprogrammet igen, og tryk Enter ved det spørgsmål, eller fjern
  `FONTES_STATS`. Hvis du sletter `stats.json`, forsvinder alt, der endnu ikke er sendt.

**3. Fejlrapporter (kun når du sender en).** Når du beder om en (`fontes report-bug`, eller du
beder din AI-app om at rapportere en fejl i Fontes), viser Fontes dig først hele rapporten og
sender den kun, hvis du bekræfter. Den indeholder Fontes' version, dit styresystems familie,
jurisdiktionskoden, værktøjets navn og fejlmeddelelsen fra det seneste værktøjskald, der
mislykkedes (med dine søgeord og id'er fjernet), og en note, hvis du skriver en. Skriv ikke
klientdata i noten. Til dette formål gemmer Fontes den seneste fejl på din computer
(`last-error.json` i dens cachemappe, erstattes hver gang); den sendes aldrig af sig selv.

## Hvor det sendes hen, og hvor længe det opbevares

Brugstal og fejlrapporter sendes til en lille server, som Fontes' udvikler driver
(`relay.kinetra.fit`). Den gemmer ikke IP-adresser: de bruges kun kortvarigt i hukommelsen til at
stoppe oversvømmelser, og webserveren fører ingen adgangslog for den. Tallene lægges sammen til
daglige totaler; enkelte afsendelser opbevares ikke. Totaler opbevares i op til 2 år,
fejlrapporter i op til 1 år, og slettes derefter. Intet sælges eller deles.

Hvis den server ikke kan nås, sendes intet: tallene bliver på din computer, og fejlrapporter
henviser dig i stedet til issue-trackeren.

## Hvem der er ansvarlig, og på hvilket grundlag

Dataansvarlig for brugstal og fejlrapporter er Yüce Karapazar, Fontes' udvikler. Kontakt:
fontesmcp@proton.me.

Retsgrundlaget er dit samtykke (artikel 6, stk. 1, litra a, i UK GDPR og EU's
databeskyttelsesforordning). Brugstal sendes kun, hvis du siger ja, og en fejlrapport kun, når du
har bekræftet den. Du kan til enhver tid trække dit samtykke tilbage ved at slå dem fra som
beskrevet ovenfor; det påvirker ikke det, der allerede er sendt.

## Kontakt

Spørgsmål eller anmodninger: skriv til fontesmcp@proton.me, eller opret et issue på
<https://github.com/ykarapazar/fontes/issues>.
