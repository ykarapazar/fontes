> Detta är en maskinstödd översättning. Den engelska versionen gäller.

# Integritetsmeddelande för Fontes

Fontes körs på din dator. Dina sökningar och de dokument du öppnar stannar
mellan din dator, de källor du söker i (officiella, plus CourtListener och Lexifina där du använder dem, se nedan) och den AI-app du använder (enligt den
appens egna villkor). Fontes självt skickar **ingenting som standard** till Fontes
utvecklare.

## Vad som kan lämna din dator, och när

**1. Uppdateringskontroll (på som standard).** En gång om dagen frågar Fontes PyPI, det offentliga
paketregistret för Python, vilken version som är den senaste. Förfrågan innehåller ingenting om dig eller ditt arbete;
PyPI ser din IP-adress, som vid all nedladdning. För att stänga av den, ange `FONTES_NO_UPDATE_CHECK=1`
(meddelandet i appen) och `FONTES_NO_AUTO_UPDATE=1` (installationsprogrammets automatiska uppdateringar).

**2. Användningssiffror (avstängda om du inte slår på dem).** Om du väljer att delta (opt-in) skickar Fontes en gång om dagen:

- Fontes-versionen och din operativsystemfamilj (macOS, Windows, Linux);
- per dag, hur många gånger varje verktyg användes för varje jurisdiktionskod, till exempel
  ”2026-11-10, nl, search_caselaw, 12”.

Det är hela meddelandet. Det innehåller aldrig dina sökningar, dokument- eller mål-id:n, dokumenttext,
ditt namn, ett konto eller något id för dig eller din dator. Siffrorna väntar på din dator
(i Fontes cachemapp, `stats.json`) tills de skickas; om sändningen misslyckas väntar de till
nästa dag.

- **Delta (opt-in)**: svara ”j” när installationsprogrammet frågar, eller ange `FONTES_STATS=1` för Fontes-servern.
- **Avstå (opt-out)**: kör installationsprogrammet igen och tryck Enter vid den frågan, eller ta bort
  `FONTES_STATS`. Om du raderar `stats.json` förkastas allt som ännu inte har skickats.

**3. Felrapporter (endast när du skickar en).** När du begär en (`fontes report-bug`, eller ber
din AI-app rapportera ett fel i Fontes) visar Fontes dig först hela rapporten och skickar den endast om
du bekräftar. Den innehåller Fontes-versionen, din operativsystemfamilj, jurisdiktionskoden, verktygsnamnet och
felmeddelandet från det senaste misslyckade verktygsanropet (med dina sökord och id:n bortklippta), och
en anteckning om du skriver en. Skriv inte klientuppgifter i anteckningen. För att stödja detta sparar Fontes
det senaste felet på din dator (`last-error.json` i dess cachemapp, ersätts varje gång);
det skickas aldrig på egen hand.

**4. Lexifina (på som standard).** `get_law_on_date`, `get_law_history`, de 91 länderna och Indiens lagar läses via Lexifinas lagregister, så de går till Lexifina lika väl som, eller i stället för, den officiella webbplatsen. Dina sökord, citat och datum går till Lexifinas kostnadsfria server, `global-law.lexifina.com`, som drivs av Lexifina, inte av Fontes utvecklare. Lexifina dokumenterar att dess server loggar vilket verktyg som anropades och hur lång tid det tog, aldrig vad som efterfrågades; Fontes kan inte kontrollera det, och Lexifinas egna villkor gäller. Lexifina ser din IP-adress, som all webbserver gör. För att stänga av Lexifina helt, ange `WLM_LEXIFINA=0`; de två verktygen och länderna slutar då fungera och inget skickas dit.

## Vart det går och hur länge det sparas

Användningssiffror och felrapporter går till en liten server som drivs av Fontes utvecklare
(`relay.kinetra.fit`). Den lagrar inga IP-adresser: de används endast i minnet, kortvarigt, för att
stoppa överbelastning, och webbservern för ingen åtkomstlogg för den. Siffrorna läggs ihop till dagliga
summor; enskilda inskick sparas inte. Summorna sparas i upp till 2 år, felrapporter i upp till
1 år, och raderas sedan. Ingenting säljs eller delas.

Om servern inte kan nås skickas ingenting: siffrorna stannar på din dator och felrapporter
hänvisar dig i stället till ärendehanteringen (issue tracker).

## Vem som är ansvarig, och på vilken grund

Personuppgiftsansvarig för användningssiffror och felrapporter är Yüce Karapazar, utvecklaren av
Fontes. Kontakt: fontesmcp@proton.me.

Den rättsliga grunden är ditt samtycke (artikel 6.1 a i UK GDPR och EU:s dataskyddsförordning, GDPR). Användningssiffror
skickas endast om du väljer att delta (opt-in), och en felrapport endast efter att du har bekräftat den. Du kan när som helst återkalla
ditt samtycke genom att avstå enligt beskrivningen ovan; detta påverkar inte det som skickats
tidigare.

## Kontakt

Frågor eller begäranden: mejla fontesmcp@proton.me, eller öppna ett ärende (issue) på
<https://github.com/ykarapazar/fontes/issues>.
