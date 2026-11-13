> Dette er en maskinstøttet oversættelse. Den engelske version er den gældende.

# Fontes: spørgsmål og svar

## Hvad er Fontes?

En gratis open source-MCP-server (Apache 2.0). Den lader enhver app, der taler Model Context
Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI og andre), søge i retsafgørelser og
lovgivning live på domstoles og myndigheders websteder i over 120 jurisdiktioner og
internationale domstole (124 adaptere). Hvert resultat nævner sin kilde og linker til originalen.

## Er teksterne officielle?

For det meste, men ikke altid.

- De fleste kilder drives af en domstol, et ministerium eller en officiel lovtidende.
- Nogle konsoliderede tekster offentliggøres af en regering, men er udtrykkeligt uofficielle: kun
  den officielle lovtidende er autentisk.
- Nogle få kilder er slet ikke offentlige websteder (for eksempel LexiVox, LawPhil, Maqam,
  Wikisource).

Fontes tilføjer en meddelelse om "uofficiel kilde" til hvert svar, der kommer fra en af disse
kilder. Tjek den officielle offentliggørelse, før du citerer. Dækningstabellen i
[README](README.md#dækning) og `list_jurisdictions` nævner kilden for hver jurisdiktion.

## Hvilke jurisdiktioner dækker den, og hvor godt?

124 adaptere: 108 FN-medlemsstater, Hongkong, Kosovo, Palæstina, Taiwan, DIFC Courts og 11
internationale domstole og organer (såsom Den Europæiske Menneskerettighedsdomstol, EU, ICJ og
WTO).

Dækningen varierer meget. Efter en streng regel (den øverste almindelige domstols præjudikater,
eller forfatningen og de vigtigste love, nået fuldt ud) regnes 72 af de 124 som dækket.
[COVERAGE.md](COVERAGE.md) angiver for hver jurisdiktion, hvad Fontes når, hvad den ikke når, og
hvorfor.

## Skal jeg bruge en API-nøgle?

Ikke for næsten alle jurisdiktioner. Nogle få kilder kræver en gratis nøgle: se
[KEYS.md](KEYS.md).

- **Frankrig:** ja. Frankrig er slået fra, indtil du sætter `WLM_FR_PISTE_CLIENT_ID` og
  `WLM_FR_PISTE_CLIENT_SECRET`. Dem får du med en gratis PISTE-konto (piste.gouv.fr) med en app,
  der abonnerer på Judilibre og Légifrance.
- **USA:** valgfrit. Søgning i retspraksis virker uden nøgle, men den delte demonøgle tillader kun
  omkring 10 søgninger om dagen pr. IP-adresse. En gratis api.data.gov-nøgle i
  `WLM_US_GOVINFO_KEY` hæver det.

Sæt dem som miljøvariabler for Fontes-serveren i din apps MCP-indstillinger. Når
installationsprogrammet er ude, spørger det efter dem efter installationen, og med dets
startfil **Add or change keys** kan du ændre dem senere.

Derudover siger nogle kilder i deres vilkår, at automatiseret adgang kræver udgiverens
tilladelse. De er markeret OFF og forbliver slået fra. En nøgle ændrer ikke ved det; det gør kun
udgiverens tilladelse (sæt så `WLM_PERMITTED=<codes>`).

## Hvad forlader min computer?

Dine søgninger sendes kun til den kilde, der søges i. Fontes fører ingen database og kræver ingen
konto.

Ud over kilderne spørger Fontes én gang om dagen PyPI, om der er en nyere version (slås fra med
`FONTES_NO_UPDATE_CHECK=1`). Brugstal er slået fra, medmindre du slår dem til, og en fejlrapport
sendes kun, når du har set og bekræftet den. Din AI-app ser din samtale under sine egne vilkår.

Alle detaljer: [PRIVACY.md](PRIVACY.md).

## Er dette juridisk rådgivning?

Nej. Fontes er et researchværktøj. Det finder tekster; det fortæller dig ikke, hvad de betyder for
din sag, og brugen af det skaber ikke et advokat-klient-forhold med nogen. AI-appen kan læse en
tekst forkert, så læs hele afgørelsen eller bestemmelsen, før du stoler på den. For rådgivning,
spørg en advokat med kvalifikation dér, hvor dit spørgsmål opstår.

## Hvem vedligeholder den? Vil den blive ved med at virke?

Én person: Yüce Karapazar. Der er ingen virksomhed bag Fontes, ingen supportkontrakt og intet løfte
om serviceniveau. Der tilbydes ingen juridiske tjenester.

Kilderne tjekkes én gang om dagen, og resultaterne offentliggøres på
[statussiden](https://ykarapazar.github.io/fontes/status/?lang=da). Domstoles og myndigheders
websteder ændrer sig uden varsel, så en kilde kan holde op med at virke når som helst. Der er
ingen garanti for, at en kilde, eller Fontes selv, bliver ved med at virke. Fontes leveres "som
det er", uden garanti (afsnit 7 og 8 i [LICENSE](../../../LICENSE)).

## En tekst er forkert eller forældet, eller en kilde virker ikke. Hvordan rapporterer jeg det?

- Opret et issue med formularen "Broken or wrong source":
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Angiv jurisdiktionen, hvad du spurgte
  om, hvad du fik, og den officielle side, der viser den rigtige tekst.
- Eller bed din AI-app om at "rapportere en fejl i Fontes" (eller kør `fontes report-bug`). Du ser
  rapporten, før noget sendes.
- Eller skriv til fontesmcp@proton.me.

Skriv ikke klientdata eller fortrolige oplysninger i en rapport.

**Hvis du driver en af kilderne**, og noget er forkert (dine vilkår, din robots.txt, dine rate
limits), så skriv til fontesmcp@proton.me. Kilden bliver rettet eller slået fra.

## Hvordan adskiller Fontes sig fra hostede værktøjer til juridisk research?

- **Den kører på din computer.** Der er ingen Fontes-server og ingen konto. Det betyder også, at
  den kun virker i apps, der kan starte en lokal MCP-server (Claude Desktop, Codex, Cursor,
  VS Code og lignende), ikke i apps, der kun kører på nettet og kun accepterer hostede connectors.
- **Den har ingen database.** Hver søgning går live til udgiverens eget websted eller API, så
  resultaterne er lige så aktuelle som kilden, og søgekvaliteten er kildens egen. Der er ingen
  semantisk søgning i et kurateret indeks.
- **Den sætter ingen forbrugsgrænse.** Fontes har ikke noget månedligt maksimum for antal kald.
  Den fordeler sine forespørgsler på hvert websted, og nogle kilder begrænser, hvor hurtigt eller
  hvor ofte de kan forespørges.
- **Den er open source.** Du kan læse hver adapter og se præcis, hvor hver tekst kommer fra.
- **Der er ingen leverandør bag den.** Ingen kontrakt, ingen supportafdeling og intet løfte om
  oppetid (se "Hvem vedligeholder den?").

## Hvilke apps og systemer virker den med?

Enhver MCP-app, der kan køre en lokal (stdio-)server, for eksempel Claude Desktop, Claude Code,
Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio og Cline. Fontes
kører på macOS, Windows og Linux, overalt hvor uv kører (Python 3.13+). Den er ikke på PyPI endnu;
når den er det, kræver de fleste apps én kommando eller én konfigurationspost, og Claude Desktop
tager en `.mcpb`-fil, som du dobbeltklikker på. Et installationsprogram med ét klik til Mac og
Windows er på vej. Det sætter Claude Desktop, Codex, Claude Code, Cursor, VS Code, Windsurf,
Gemini CLI, Zed, LM Studio og Cline op på én gang. Trin for hver app: [INSTALL.md](INSTALL.md).

## Kan jeg bidrage med kode?

Ikke for øjeblikket. Issues, rapporter om kilder og ønsker om jurisdiktioner er velkomne. Se
[CONTRIBUTING.md](../../../CONTRIBUTING.md).
