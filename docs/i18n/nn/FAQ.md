> Dette er ei maskinassistert omsetjing. Den engelske versjonen er den gjeldande.

# Fontes: spørsmål og svar

## Kva er Fontes?

Ein gratis MCP-server med open kjeldekode (Apache 2.0). Han lèt alle appar som snakkar Model Context
Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI og andre) søkje i rettsavgjerder og
lovgjeving direkte på nettstadene til domstolar og styresmakter i over 120 jurisdiksjonar og internasjonale
domstolar (124 adapterar). Kvart resultat namngjev kjelda si og lenkjer til originalen.

## Er tekstane offisielle?

For det meste, men ikkje alltid.

- Dei fleste kjeldene blir drivne av ein domstol, eit departement eller eit offisielt kunngjeringsblad.
- Somme konsoliderte tekstar blir publiserte av styresmaktene, men er uttrykkeleg uoffisielle: berre
  det offisielle kunngjeringsbladet er autentisk.
- Nokre få kjelder er ikkje offentlege nettstader i det heile (til dømes LexiVox, LawPhil, Maqam,
  Wikisource).

Fontes legg til ei melding om «uoffisiell kjelde» i kvart svar som kjem frå ei av desse. Før
du siterer noko, sjekk den offisielle kunngjeringa. Dekningstabellen i
[README](README.md#dekning) og `list_jurisdictions` namngjev kjelda for kvar jurisdiksjon.

## Kva jurisdiksjonar dekkjer det, og kor godt?

124 adapterar: 108 medlemsstatar i FN, Hongkong, Kosovo, Palestina, Taiwan, DIFC Courts og
11 internasjonale domstolar og organ (som Den europeiske menneskerettsdomstolen, EU,
ICJ og WTO).

Dekninga varierer mykje. Etter ein streng regel (prejudikata til den øvste allmenne domstolen, eller
grunnlova og dei primære lovene, nådde fullt ut) tel 72 av dei 124 som dekte.
[COVERAGE.md](../../COVERAGE.md) listar opp, for kvar jurisdiksjon, kva Fontes når, kva det ikkje når,
og kvifor.

## Treng eg ein API-nøkkel?

For nesten alle jurisdiksjonar, nei. Somme kjelder krev ein gratis nøkkel: sjå [KEYS.md](KEYS.md).

- **Frankrike:** ja. Frankrike er av til du set `WLM_FR_PISTE_CLIENT_ID` og
  `WLM_FR_PISTE_CLIENT_SECRET`. Desse kjem frå ein gratis PISTE-konto (piste.gouv.fr) med ein
  app som abonnerer på Judilibre og Légifrance.
- **USA:** valfritt. Søk i rettspraksis verkar utan nøkkel, men den delte demonøkkelen
  tillèt berre om lag 10 søk om dagen per IP-adresse. Ein gratis api.data.gov-nøkkel i
  `WLM_US_GOVINFO_KEY` aukar grensa.

Set desse som miljøvariablar for Fontes-serveren i MCP-innstillingane i appen din. Når
installasjonsprogrammet er ute, vil det spørje etter dei etter installeringa, og startaren **Add or change keys**
endrar dei seinare.

I tillegg seier nokre få kjelder i vilkåra sine at automatisert tilgang krev løyve frå
utgjevaren. Dei er merkte OFF og blir verande av. Ein nøkkel endrar ikkje det; berre løyve frå
utgjevaren gjer det (set då `WLM_PERMITTED=<codes>`).

## Kva forlèt datamaskina mi?

Søka dine går berre til kjelda det blir søkt i. Fontes har ingen database og krev ingen
konto.

I tillegg til kjeldene spør Fontes PyPI éin gong om dagen om det finst ein nyare versjon (slå det av
med `FONTES_NO_UPDATE_CHECK=1`). Brukstal er av med mindre du slår dei på, og ein feilrapport
blir berre send etter at du har sett han og stadfesta. KI-appen din ser samtalen din under sine
eigne vilkår.

Alle detaljar: [PRIVACY.md](PRIVACY.md).

## Er dette juridisk rådgjeving?

Nei. Fontes er eit researchverktøy. Det finn tekstar; det seier deg ikkje kva dei tyder for saka
di, og bruken skaper ikkje eit klientforhold til ein advokat for nokon. KI-appen kan
lese ein tekst feil, så les heile avgjerda eller føresegna før du stolar på henne. For råd, spør
ein advokat med kompetanse der spørsmålet ditt oppstår.

## Kven vedlikeheld det? Vil det halde fram med å verke?

Éin person: Yüce Karapazar. Det står ikkje noko selskap bak Fontes, det finst ingen supportavtale og ingen
lovnad om tenestenivå. Ingen juridiske tenester blir tilbodne.

Kjeldene blir kontrollerte éin gong om dagen, og resultata blir publiserte på
[statussida](https://ykarapazar.github.io/fontes/status/?lang=nn). Nettstadene til domstolar og styresmakter
endrar seg utan varsel, så ei kjelde kan slutte å verke når som helst. Det er ingen garanti for at nokon kjelde,
eller Fontes sjølv, vil halde fram med å verke. Fontes blir levert «som han er», utan garanti (punkt 7
og 8 i [LICENSE](../../../LICENSE)).

## Ein tekst er feil eller utdatert, eller ei kjelde er øydelagd. Korleis rapporterer eg det?

- Opprett ei sak med skjemaet «Broken or wrong source»:
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Sei kva jurisdiksjon, kva du
  spurde om, kva du fekk, og den offisielle sida som viser den rette teksten.
- Eller be KI-appen din om å «rapportere ein feil i Fontes» (eller køyr `fontes report-bug`). Du ser rapporten før
  noko blir sendt.
- Eller send e-post til fontesmcp@proton.me.

Ikkje ta med klientopplysningar eller konfidensielle fakta i ein rapport.

**Om du driv ei av kjeldene** og noko er feil (vilkåra dine, robots.txt-en din, grensene dine
for førespurnader), send e-post til fontesmcp@proton.me. Kjelda blir retta eller slått av.

## Korleis skil Fontes seg frå hosta verktøy for juridisk research?

- **Han køyrer på datamaskina di.** Det finst ingen Fontes-server og ingen konto. Det tyder òg at han
  berre verkar i appar som kan starte ein lokal MCP-server (Claude Desktop, Codex, Cursor, VS Code
  og liknande), ikkje i reine nettappar som berre tek imot hosta koplingar (connectors).
- **Han har ingen database.** Kvart søk går direkte til nettstaden eller API-et til utgjevaren sjølv, så
  resultata er like oppdaterte som kjelda, og søkjekvaliteten er kjelda sin eigen. Det finst ikkje noko
  semantisk søk over ein kuratert indeks.
- **Han set ingen bruksgrense.** Fontes har inga månadleg grense for kall. Han spreier førespurnadene sine til kvar
  nettstad, og somme kjelder avgrensar kor raskt eller kor ofte dei kan spørjast.
- **Han har open kjeldekode.** Du kan lese kvar adapter og sjå nøyaktig kvar kvar tekst kjem frå.
- **Det står ingen leverandør bak.** Ingen kontrakt, ingen kundestøtte og ingen lovnad om oppetid (sjå «Kven
  vedlikeheld det?»).

## Kva appar og system verkar det med?

Alle MCP-appar som kan køyre ein lokal server (stdio), til dømes Claude Desktop, Claude Code,
Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio og Cline. Fontes
køyrer på macOS, Windows og Linux, overalt der uv køyrer (Python 3.13+). Eit installasjonsprogram med eitt klikk for Mac og Windows er på veg. Det set
opp Claude Desktop, Codex, Claude Code, Cursor, VS Code, Windsurf, Gemini CLI, Zed, LM Studio og
Cline i éin omgang. Steg for kvar app: [INSTALL.md](INSTALL.md).

## Kan eg bidra med kode?

Ikkje for tida. Saker, kjelderapportar og ønske om jurisdiksjonar er velkomne. Sjå
[CONTRIBUTING.md](../../../CONTRIBUTING.md).
