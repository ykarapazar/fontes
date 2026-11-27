> Dit is een machinaal ondersteunde vertaling. De Engelse versie is leidend.

# Privacyverklaring van Fontes

Fontes draait op uw computer. Uw zoekopdrachten en de documenten die u opent, blijven tussen uw
computer, de bronnen die u doorzoekt (officiële bronnen, plus CourtListener en Lexifina waar u die
gebruikt, zie hieronder) en de AI-app die u gebruikt (onder de eigen voorwaarden van die app). Fontes zelf stuurt de ontwikkelaars van Fontes **standaard niets**.

## Wat uw computer kan verlaten, en wanneer

**1. Updatecontrole (standaard aan).** Eenmaal per dag vraagt Fontes aan PyPI, de openbare index
van Python-pakketten, welke versie de nieuwste is. Het verzoek bevat niets over u of uw werk; PyPI
ziet uw IP-adres, zoals bij elke download. Om dit uit te zetten, stelt u `FONTES_NO_UPDATE_CHECK=1`
in (de melding in de app) en `FONTES_NO_AUTO_UPDATE=1` (de automatische updates van het
installatieprogramma).

**2. Gebruiksaantallen (uit, tenzij u ze aanzet).** Als u ervoor kiest, verstuurt Fontes eenmaal
per dag:

- de versie van Fontes en de familie van uw besturingssysteem (macOS, Windows, Linux);
- per dag, hoe vaak elke tool is gebruikt voor elke code van een rechtsstelsel, bijvoorbeeld
  "2026-11-10, nl, search_caselaw, 12".

Dat is het hele bericht. Het bevat nooit uw zoekopdrachten, document- of zaak-id's, documenttekst,
uw naam, een account, of enig id voor u of uw computer. De aantallen wachten op uw computer (in de
cachemap van Fontes, `stats.json`) tot ze worden verzonden; als verzenden mislukt, wachten ze tot
de volgende dag.

- **Aanzetten**: antwoord "y" wanneer het installatieprogramma het vraagt, of stel
  `FONTES_STATS=1` in voor de Fontes-server.
- **Uitzetten**: voer het installatieprogramma opnieuw uit en druk bij die vraag op Enter, of
  verwijder `FONTES_STATS`. Door `stats.json` te verwijderen, vervalt alles wat nog niet is
  verzonden.

**3. Foutrapporten (alleen wanneer u er een verstuurt).** Wanneer u om een foutrapport vraagt
(`fontes report-bug`, of door uw AI-app te vragen een fout in Fontes te melden), toont Fontes u eerst
het volledige rapport en verstuurt het alleen als u bevestigt. Het bevat de versie van Fontes, de
familie van uw besturingssysteem, de code van het rechtsstelsel, de naam van de tool en de
foutmelding van de laatste mislukte tool-aanroep (met uw zoekwoorden en id's eruit gehaald), en een
notitie als u die schrijft. Zet geen cliëntgegevens in de notitie. Hiervoor bewaart Fontes de
laatste fout op uw computer (`last-error.json` in de cachemap, die telkens wordt vervangen); die
wordt nooit los verzonden.

**4. Lexifina (standaard aan).** `get_law_on_date`, `get_law_history`, de 91 landen en de Indiase wetten worden gelezen via de verzameling van Lexifina, dus ze gaan naar Lexifina, naast of in plaats van de officiële site. Uw
zoekwoorden, citaten en data gaan naar de gratis server van Lexifina, `global-law.lexifina.com`, die
wordt beheerd door Lexifina en niet door de ontwikkelaars van Fontes. Lexifina documenteert dat de
server bijhoudt welke tool is aangeroepen en hoe lang die duurde, nooit wat er gevraagd werd; Fontes
kan dat niet controleren, en de eigen voorwaarden van Lexifina gelden. Lexifina ziet uw IP-adres,
zoals elke webserver dat ziet. Om Lexifina volledig uit te zetten, stelt u `WLM_LEXIFINA=0` in; die
twee tools en landen werken dan niet meer, en er wordt daarheen niets verzonden.

## Waar het naartoe gaat en hoe lang het wordt bewaard

Gebruiksaantallen en foutrapporten gaan naar een kleine server die wordt beheerd door de
ontwikkelaar van Fontes (`relay.kinetra.fit`). Die slaat geen IP-adressen op: ze worden alleen kort
in het geheugen gebruikt om overbelasting te voorkomen, en de webserver houdt er geen toegangslog
voor bij. Aantallen worden opgeteld tot dagtotalen; afzonderlijke inzendingen worden niet bewaard.
Totalen worden maximaal 2 jaar bewaard, foutrapporten maximaal 1 jaar, en daarna verwijderd. Niets
wordt verkocht of gedeeld.

Als die server niet bereikbaar is, wordt niets verzonden: aantallen blijven op uw computer en
foutrapporten verwijzen u in plaats daarvan naar de issuetracker.

## Wie verantwoordelijk is, en op welke grondslag

De verwerkingsverantwoordelijke voor gebruiksaantallen en foutrapporten is Yüce Karapazar, de
ontwikkelaar van Fontes. Contact: fontesmcp@proton.me.

De rechtsgrondslag is uw toestemming (artikel 6, lid 1, onder a, van de UK GDPR en de AVG van de EU).
Gebruiksaantallen worden alleen verzonden als u ervoor kiest, en een foutrapport alleen nadat u het
hebt bevestigd. U kunt uw toestemming op elk moment intrekken door uit te zetten zoals hierboven
beschreven; dit heeft geen gevolgen voor wat eerder is verzonden.

## Contact

Vragen of verzoeken: mail naar fontesmcp@proton.me, of open een issue op
<https://github.com/ykarapazar/fontes/issues>.
