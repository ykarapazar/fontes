> Dette er en maskinstøttet oversættelse. Den engelske version er den gældende.

# Fontes: spørgsmål og svar

## Hvad er Fontes?

En gratis open source-MCP-server (Apache 2.0). Den lader enhver app, der taler Model Context
Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI og andre), søge i retsafgørelser og
lovgivning live på domstoles og myndigheders websteder i 125 jurisdiktioner og
internationale domstole (125 adaptere), plus 91 flere lande gennem Lexifinas register (se nedenfor). Hvert resultat nævner sin kilde og linker til originalen.

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

125 adaptere: 108 FN-medlemsstater, Hongkong, Kosovo, Palæstina, Taiwan, DIFC Courts, de amerikanske delstaters domstole og 11
internationale domstole og organer (såsom Den Europæiske Menneskerettighedsdomstol, EU, ICJ og
WTO).

Dækningen varierer meget. Efter en streng regel (den øverste almindelige domstols præjudikater,
eller forfatningen og de vigtigste love, nået fuldt ud) regnes 72 af de 125 som dækket.
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
- **De amerikanske delstaters domstole:** ja. Delstaternes retspraksis (`us-states`) er slået fra, indtil du sætter `WLM_US_COURTLISTENER_KEY` til dit eget gratis CourtListener API-token. CourtListener drives af non-profitorganisationen Free Law Project; det er ikke en officiel kilde, og hvert svar siger det.

Sæt dem som miljøvariabler for Fontes-serveren i din apps MCP-indstillinger. Installationsprogrammerne
spørger efter dem efter installationen, og med deres startfil **Add or change keys** kan du
ændre dem senere.

Derudover siger nogle kilder i deres vilkår, at automatiseret adgang kræver udgiverens
tilladelse. De er markeret OFF og forbliver slået fra. En nøgle ændrer ikke ved det; det gør kun
udgiverens tilladelse (sæt så `WLM_PERMITTED=<codes>`).

## Hvor kommer de tidligere versioner og de ekstra lande fra?

Fra [Lexifina](https://github.com/lexifina/global-law), som holder lovgivningen for omkring 200
lande som git-historik: hver ændring er en commit, dateret den dag, den trådte i kraft. Fontes
læser den gennem Lexifinas gratis hostede server. To værktøjer bruger den: `get_law_on_date` (en
bestemmelse, sådan den var gældende på en dato, også i fortiden, med den lov, der sidst ændrede
den) og `get_law_history` (hver lov, der ændrede en bestemmelse, eller den ordrette ændring mellem
to datoer). Fontes læser også 91 flere lande og territorier på denne måde, kun for lovgivning (for
eksempel Sydafrika, Kenya, Mexico, New Zealand, Rusland, Sydkorea, Belgien, Litauen, Ukraine,
Malaysia, Thailand og Saudi-Arabien). De er adskilt fra de 125 adaptere med løbende officiel
dækning, og dækningen pr. land varierer meget (Kenyas nationale register indeholder 9 love).
Indiens love kommer også fra Lexifinas register, fordi India Codes vilkår forbyder automatiseret
adgang; dets højesteretsdomme er løbende.

Lexifina er ikke den officielle udgiver, og dets register er ikke løbende: Lexifina kontrollerer
hvert land fra tid til anden, og dets egen rapport fra 2026-11-26 talte 338 af 383 nationale
lovsamlinger som ikke kontrolleret inden for de seneste 7 dage. Hvert svar nævner Lexifina som
kilde, linker til den officielle udgivers side og siger, hvor langt registret rækker.

Lexifina har den holdning, at officielle lovtekster ikke er beskyttet af ophavsret, så i nogle lande
kopierer den sider, hvis vilkår eller robots.txt Fontes selv respekterer. Fontes respekterer dem
stadig for alt, hvad Fontes selv henter; det, der kommer gennem Lexifina, følger Lexifinas egen
vurdering, registreret pr. land i dets arkiver. Nogle få begrænser brugen (Kenyas udgiver: CC
BY-NC). Dine søgeord, citater og datoer går til Lexifinas server for disse. Sæt `WLM_LEXIFINA=0`
for at slå det fra. Den gratis server tillader 60 kald i minuttet og 10.000 om dagen pr.
internetadresse; ingen nøgle eller konto. Fontes er ikke tilknyttet Lexifina.

## Hvad forlader min computer?

Dine søgninger sendes kun til den kilde, der søges i (for Lexifina-værktøjerne og -landene er det Lexifinas server). Fontes fører ingen database og kræver ingen
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
kører på macOS, Windows og Linux, overalt hvor uv kører (Python 3.13+). På en Mac eller pc med Windows sætter et installationsprogram med ét klik Claude Desktop, Codex, Claude Code, Cursor, VS Code, Windsurf, Gemini CLI, Zed, LM Studio og Cline op på én gang. Trin for hver app: [INSTALL.md](INSTALL.md).

## Kan jeg bidrage med kode?

Ikke for øjeblikket. Issues, rapporter om kilder og ønsker om jurisdiktioner er velkomne. Se
[CONTRIBUTING.md](../../../CONTRIBUTING.md).
