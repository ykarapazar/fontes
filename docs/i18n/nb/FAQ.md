> Dette er en maskinassistert oversettelse. Den engelske versjonen er den gjeldende.

# Fontes: spørsmål og svar

## Hva er Fontes?

En gratis MCP-server med åpen kildekode (Apache 2.0). Den lar enhver app som snakker Model Context
Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI og andre), søke i rettsavgjørelser og
lovgivning direkte på domstolers og myndigheters nettsteder i over 120 jurisdiksjoner og
internasjonale domstoler (124 adaptere). Hvert resultat oppgir kilden sin og lenker til
originalen.

## Er tekstene offisielle?

Stort sett, men ikke alltid.

- De fleste kildene drives av en domstol, et departement eller en offisiell lovtidende.
- Noen konsoliderte tekster publiseres av en myndighet, men er uttrykkelig uoffisielle: bare den
  offisielle lovtidenden er autentisk.
- Noen få kilder er ikke offentlige nettsteder i det hele tatt (for eksempel LexiVox, LawPhil,
  Maqam, Wikisource).

Fontes legger til en melding om "uoffisiell kilde" i hvert svar som kommer fra en av disse
kildene. Sjekk den offisielle kunngjøringen før du siterer. Dekningstabellen i
[README](README.md#dekning) og `list_jurisdictions` oppgir kilden for hver jurisdiksjon.

## Hvilke jurisdiksjoner dekker den, og hvor godt?

124 adaptere: 108 FN-medlemsstater, Hongkong, Kosovo, Palestina, Taiwan, DIFC Courts og 11
internasjonale domstoler og organer (som Den europeiske menneskerettighetsdomstol, EU, ICJ og
WTO).

Dekningen varierer mye. Etter en streng regel (prejudikatene fra den øverste alminnelige
domstolen, eller grunnloven og de viktigste lovene, nådd fullt ut) regnes 72 av de 124 som dekket.
[COVERAGE.md](COVERAGE.md) oppgir for hver jurisdiksjon hva Fontes når, hva den ikke når, og
hvorfor.

## Trenger jeg en API-nøkkel?

Ikke for nesten alle jurisdiksjoner. Noen få kilder krever en gratis nøkkel: se
[KEYS.md](KEYS.md).

- **Frankrike:** ja. Frankrike er slått av til du setter `WLM_FR_PISTE_CLIENT_ID` og
  `WLM_FR_PISTE_CLIENT_SECRET`. Disse får du med en gratis PISTE-konto (piste.gouv.fr) med en app
  som abonnerer på Judilibre og Légifrance.
- **USA:** valgfritt. Søk i rettspraksis fungerer uten nøkkel, men den delte demonøkkelen tillater
  bare rundt 10 søk om dagen per IP-adresse. En gratis api.data.gov-nøkkel i
  `WLM_US_GOVINFO_KEY` hever det.

Sett dem som miljøvariabler for Fontes-serveren i MCP-innstillingene i appen din. Når
installasjonsprogrammet er ute, spør det etter dem etter installasjonen, og med startfilen
**Add or change keys** kan du endre dem senere.

I tillegg sier noen kilder i vilkårene sine at automatisert tilgang krever utgiverens tillatelse.
De er merket OFF og forblir slått av. En nøkkel endrer ikke det; det gjør bare utgiverens
tillatelse (sett da `WLM_PERMITTED=<codes>`).

## Hva forlater datamaskinen min?

Søkene dine sendes bare til kilden det søkes i. Fontes fører ingen database og krever ingen
konto.

I tillegg til kildene spør Fontes én gang om dagen PyPI om det finnes en nyere versjon (slås av
med `FONTES_NO_UPDATE_CHECK=1`). Brukstall er av med mindre du slår dem på, og en feilrapport
sendes bare etter at du har sett og bekreftet den. AI-appen din ser samtalen din under sine egne
vilkår.

Alle detaljer: [PRIVACY.md](PRIVACY.md).

## Er dette juridisk rådgivning?

Nei. Fontes er et researchverktøy. Det finner tekster; det forteller deg ikke hva de betyr for
saken din, og bruken av det skaper ikke et advokat-klient-forhold med noen. AI-appen kan lese en
tekst feil, så les hele avgjørelsen eller bestemmelsen før du stoler på den. For rådgivning, spør
en advokat med kvalifikasjon der spørsmålet ditt oppstår.

## Hvem vedlikeholder den? Kommer den til å fortsette å fungere?

Én person: Yüce Karapazar. Det står ikke noe selskap bak Fontes, det finnes ingen supportavtale og
ikke noe løfte om tjenestenivå. Ingen juridiske tjenester tilbys.

Kildene sjekkes én gang om dagen, og resultatene publiseres på
[statussiden](https://ykarapazar.github.io/fontes/status/?lang=nb). Domstolers og myndigheters
nettsteder endres uten varsel, så en kilde kan slutte å fungere når som helst. Det er ingen garanti
for at en kilde, eller Fontes selv, fortsetter å fungere. Fontes leveres "som det er", uten
garanti (avsnitt 7 og 8 i [LICENSE](../../../LICENSE)).

## En tekst er feil eller utdatert, eller en kilde fungerer ikke. Hvordan rapporterer jeg det?

- Opprett et issue med skjemaet "Broken or wrong source":
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Oppgi jurisdiksjonen, hva du spurte
  om, hva du fikk, og den offisielle siden som viser riktig tekst.
- Eller be AI-appen din om å "rapportere en feil i Fontes" (eller kjør `fontes report-bug`). Du ser
  rapporten før noe sendes.
- Eller send e-post til fontesmcp@proton.me.

Ikke skriv klientdata eller fortrolige opplysninger i en rapport.

**Hvis du driver en av kildene** og noe er feil (vilkårene dine, robots.txt-en din, rate limits),
send e-post til fontesmcp@proton.me. Kilden blir rettet eller slått av.

## Hvordan skiller Fontes seg fra hostede verktøy for juridisk research?

- **Den kjører på datamaskinen din.** Det finnes ingen Fontes-server og ingen konto. Det betyr
  også at den bare fungerer i apper som kan starte en lokal MCP-server (Claude Desktop, Codex,
  Cursor, VS Code og lignende), ikke i apper som bare kjører på nettet og bare godtar hostede
  connectors.
- **Den har ingen database.** Hvert søk går direkte til utgiverens eget nettsted eller API, så
  resultatene er like oppdaterte som kilden, og søkekvaliteten er kildens egen. Det finnes ikke noe
  semantisk søk i en kuratert indeks.
- **Den setter ingen bruksgrense.** Fontes har ikke noe månedlig maksimum for antall kall. Den
  sprer forespørslene sine på hvert nettsted, og noen kilder begrenser hvor raskt eller hvor ofte
  de kan spørres.
- **Den har åpen kildekode.** Du kan lese hver adapter og se nøyaktig hvor hver tekst kommer fra.
- **Det står ingen leverandør bak den.** Ingen avtale, ingen kundestøtte og ikke noe løfte om
  oppetid (se "Hvem vedlikeholder den?").

## Hvilke apper og systemer fungerer den med?

Enhver MCP-app som kan kjøre en lokal (stdio-)server, for eksempel Claude Desktop, Claude Code,
Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio og Cline. Fontes
kjører på macOS, Windows og Linux, overalt der uv kjører (Python 3.13+). På en Mac setter et installasjonsprogram med ett klikk
opp Claude Desktop, Codex, Claude Code, Cursor, VS Code, Windsurf, Gemini CLI, Zed, LM Studio og
Cline på én gang; et installasjonsprogram for Windows er på vei. Trinn for hver app:
[INSTALL.md](INSTALL.md).

## Kan jeg bidra med kode?

Ikke for øyeblikket. Issues, rapporter om kilder og ønsker om jurisdiksjoner er velkomne. Se
[CONTRIBUTING.md](../../../CONTRIBUTING.md).
