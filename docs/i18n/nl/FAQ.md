> Dit is een machinaal ondersteunde vertaling. De Engelse versie is leidend.

# Fontes: vragen en antwoorden

## Wat is Fontes?

Een gratis opensource-MCP-server (Apache 2.0). Hiermee kan elke app die het Model Context Protocol
spreekt (Claude, Codex, Cursor, VS Code, Gemini CLI en andere) rechterlijke uitspraken en
wetgeving live doorzoeken op websites van gerechten en overheden in meer dan 120 rechtsstelsels en
bij internationale gerechten (124 adapters). Elk resultaat noemt zijn bron en linkt naar het
origineel.

## Zijn de teksten officieel?

Meestal, maar niet altijd.

- De meeste bronnen worden beheerd door een gerecht, een ministerie of een officieel publicatieblad.
- Sommige geconsolideerde teksten worden door een overheid gepubliceerd, maar zijn uitdrukkelijk
  niet-officieel: alleen het officiële publicatieblad is authentiek.
- Enkele bronnen zijn helemaal geen overheidswebsites (bijvoorbeeld LexiVox, LawPhil, Maqam,
  Wikisource).

Fontes voegt een melding "Niet-officiële bron" toe aan elk antwoord dat uit een van deze bronnen
komt. Controleer de officiële publicatie voordat u iets citeert. De dekkingstabel in de
[README](README.md#dekking) en `list_jurisdictions` noemen de bron voor elk rechtsstelsel.

## Welke rechtsstelsels bestrijkt het, en hoe goed?

124 adapters: 108 VN-lidstaten, Hongkong, Kosovo, Palestina, Taiwan, de DIFC Courts en 11
internationale gerechten en organen (zoals het Europees Hof voor de Rechten van de Mens, de EU, het
ICJ en de WTO).

De dekking verschilt sterk. Volgens een strikte regel (de precedenten van het hoogste algemene
gerecht, of de grondwet en de primaire wetten, volledig bereikt) gelden 72 van de 124 als gedekt.
[COVERAGE.md](COVERAGE.md) vermeldt voor elk rechtsstelsel wat Fontes bereikt, wat niet, en waarom.

## Heb ik een API-sleutel nodig?

Voor bijna elk rechtsstelsel niet. Sommige bronnen hebben een gratis sleutel nodig: zie
[KEYS.md](KEYS.md).

- **Frankrijk:** ja. Frankrijk staat uit totdat u `WLM_FR_PISTE_CLIENT_ID` en
  `WLM_FR_PISTE_CLIENT_SECRET` instelt. Die krijgt u met een gratis PISTE-account (piste.gouv.fr)
  met een app die is geabonneerd op Judilibre en Légifrance.
- **Verenigde Staten:** optioneel. Zoeken in rechtspraak werkt zonder sleutel, maar de gedeelde
  demosleutel staat slechts ongeveer 10 zoekopdrachten per dag per IP-adres toe. Een gratis
  api.data.gov-sleutel in `WLM_US_GOVINFO_KEY` verhoogt dat.

Stel deze in als omgevingsvariabelen voor de Fontes-server in de MCP-instellingen van uw app. Zodra
het installatieprogramma uit is, vraagt het er na de installatie om, en met zijn starter
**Add or change keys** wijzigt u ze later.

Daarnaast vermelden enkele bronnen in hun voorwaarden dat geautomatiseerde toegang toestemming van
de uitgever vereist. Die zijn gemarkeerd als UIT en blijven uit. Een sleutel verandert dat niet;
alleen de toestemming van de uitgever doet dat (stel dan `WLM_PERMITTED=<codes>` in).

## Wat verlaat mijn computer?

Uw zoekopdrachten gaan alleen naar de bron die wordt doorzocht. Fontes houdt geen database bij en
heeft geen account nodig.

Naast de bronnen vraagt Fontes eenmaal per dag aan PyPI of er een nieuwere versie is (uit te
zetten met `FONTES_NO_UPDATE_CHECK=1`). Gebruiksaantallen staan uit tenzij u ze aanzet, en een
foutrapport wordt pas verzonden nadat u het hebt gezien en bevestigd. Uw AI-app ziet uw gesprek
onder zijn eigen voorwaarden.

Alle details: [PRIVACY.md](PRIVACY.md).

## Is dit juridisch advies?

Nee. Fontes is een onderzoekstool. Het vindt teksten; het zegt u niet wat ze betekenen voor uw
zaak, en door het te gebruiken ontstaat met niemand een relatie tussen advocaat en cliënt. De
AI-app kan een tekst verkeerd lezen, dus lees de volledige uitspraak of bepaling voordat u erop
vertrouwt. Vraag voor advies een advocaat die bevoegd is waar uw vraag speelt.

## Wie onderhoudt het? Blijft het werken?

Eén persoon: Yüce Karapazar. Er staat geen bedrijf achter Fontes, er is geen supportcontract en
geen belofte over het serviceniveau. Er worden geen juridische diensten aangeboden.

De bronnen worden eenmaal per dag gecontroleerd en de resultaten worden gepubliceerd op de
[statuspagina](https://ykarapazar.github.io/fontes/status/?lang=nl). Websites van gerechten en
overheden veranderen zonder aankondiging, dus een bron kan op elk moment stukgaan. Er is geen
garantie dat een bron, of Fontes zelf, blijft werken. Fontes wordt geleverd "zoals het is", zonder
garantie (artikelen 7 en 8 van de [LICENSE](../../../LICENSE)).

## Een tekst is fout of verouderd, of een bron werkt niet. Hoe meld ik dat?

- Open een issue met het formulier "Broken or wrong source":
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Vermeld welk rechtsstelsel, wat u
  vroeg, wat u kreeg, en de officiële pagina die de juiste tekst toont.
- Of vraag uw AI-app om "een fout in Fontes te melden" (of voer `fontes report-bug` uit). U ziet het
  rapport voordat er iets wordt verzonden.
- Of mail naar fontesmcp@proton.me.

Zet geen cliëntgegevens of vertrouwelijke feiten in een melding.

**Als u een van de bronnen beheert** en er iets niet klopt (uw voorwaarden, uw robots.txt, uw
limieten voor het aantal verzoeken), mail dan naar fontesmcp@proton.me. De bron wordt gerepareerd
of uitgezet.

## Waarin verschilt Fontes van gehoste tools voor juridisch onderzoek?

- **Het draait op uw computer.** Er is geen Fontes-server en geen account. Dat betekent ook dat het
  alleen werkt in apps die een lokale MCP-server kunnen starten (Claude Desktop, Codex, Cursor,
  VS Code en vergelijkbare), niet in apps die alleen op het web werken en alleen gehoste connectors
  accepteren.
- **Het heeft geen database.** Elke zoekopdracht gaat live naar de eigen website of API van de
  uitgever, dus de resultaten zijn even actueel als de bron, en de zoekkwaliteit is die van de bron
  zelf. Er is geen semantisch zoeken in een samengestelde index.
- **Het stelt geen gebruikslimiet.** Fontes heeft geen maandelijks maximum aan aanroepen. Het
  spreidt zijn verzoeken aan elke website, en sommige bronnen beperken hoe snel of hoe vaak ze
  kunnen worden bevraagd.
- **Het is opensource.** U kunt elke adapter lezen en precies zien waar elke tekst vandaan komt.
- **Er staat geen leverancier achter.** Geen contract, helpdesk of belofte over beschikbaarheid
  (zie "Wie onderhoudt het?").

## Met welke apps en systemen werkt het?

Elke MCP-app die een lokale (stdio-)server kan draaien, bijvoorbeeld Claude Desktop, Claude Code,
Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio en Cline. Fontes
draait op macOS, Windows en Linux, overal waar uv draait (Python 3.13+). Het staat nog niet op
PyPI; zodra dat zo is, hebben de meeste apps één opdracht of één configuratievermelding nodig, en
Claude Desktop neemt een `.mcpb`-bestand waarop u dubbelklikt. Een installatieprogramma met één
klik voor Mac en Windows is in voorbereiding. Het stelt Claude Desktop, Codex, Claude Code, Cursor,
VS Code, Windsurf, Gemini CLI, Zed, LM Studio en Cline in één keer in. Stappen voor elke app:
[INSTALL.md](INSTALL.md).

## Kan ik code bijdragen?

Op dit moment niet. Issues, meldingen over bronnen en verzoeken om rechtsstelsels zijn welkom. Zie
[CONTRIBUTING.md](../../../CONTRIBUTING.md).
