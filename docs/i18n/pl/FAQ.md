> To jest tłumaczenie wspomagane maszynowo. Wiążąca jest wersja angielska.

# Fontes: pytania i odpowiedzi

## Czym jest Fontes?

Bezpłatnym serwerem MCP o otwartym kodzie źródłowym (Apache 2.0). Pozwala każdej aplikacji
obsługującej Model Context Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI i inne)
wyszukiwać orzeczenia sądów i akty prawne na żywo na stronach sądów i instytucji państwowych w
125 jurysdykcjach i sądach międzynarodowych, a także w 91 innych krajach ze zbioru Lexifina
(zobacz niżej). Każdy wynik podaje swoje źródło i zawiera link do oryginału.

## Czy teksty są oficjalne?

Przeważnie tak, ale nie zawsze.

- Większość źródeł prowadzi sąd, ministerstwo lub dziennik urzędowy.
- Niektóre teksty jednolite publikuje instytucja państwowa, ale są one wyraźnie nieoficjalne:
  autentyczny jest tylko dziennik urzędowy.
- Kilka źródeł w ogóle nie jest stronami państwowymi (na przykład LexiVox, LawPhil, Maqam,
  Wikisource).

Fontes dodaje informację „Unofficial source” do każdej odpowiedzi pochodzącej z jednego z nich.
Zanim cokolwiek zacytujesz, sprawdź oficjalną publikację. Tabela zakresu w
[README](README.md#zakres) i `list_jurisdictions` podają źródło dla każdej jurysdykcji.

## Jakie jurysdykcje obejmuje i jak dobrze?

125 adaptery: 108 państw członkowskich ONZ, Hongkong, Kosowo, Palestyna, Tajwan, sądy DIFC, sądy stanowe USA oraz 11 sądów i organów międzynarodowych (na przykład Europejski Trybunał Praw Człowieka, UE,
Międzynarodowy Trybunał Sprawiedliwości i WTO).

Zakres bardzo się różni. Według ścisłej zasady (precedensy najwyższego sądu powszechnego albo
konstytucja i ustawy podstawowe, osiągnięte w pełni) za objęte uznaje się 72 ze 125.
[COVERAGE.md](../../COVERAGE.md) podaje dla każdej jurysdykcji, do czego Fontes dociera, do
czego nie i dlaczego.

## Czy potrzebuję klucza API?

Dla niemal każdej jurysdykcji nie. Niektóre źródła wymagają bezpłatnego klucza: zobacz
[KEYS.md](KEYS.md).

- **Francja:** tak. Francja jest wyłączona, dopóki nie ustawisz `WLM_FR_PISTE_CLIENT_ID` i
  `WLM_FR_PISTE_CLIENT_SECRET`. Uzyskasz je z bezpłatnego konta PISTE (piste.gouv.fr) z
  aplikacją subskrybującą Judilibre i Légifrance.
- **Stany Zjednoczone:** opcjonalnie. Wyszukiwanie orzecznictwa działa bez klucza, ale wspólny
  klucz demonstracyjny pozwala tylko na około 10 wyszukiwań dziennie na adres IP. Bezpłatny klucz
  api.data.gov w `WLM_US_GOVINFO_KEY` podnosi ten limit.
- **Sądy stanowe USA:** tak. Orzecznictwo stanowe (`us-states`) jest wyłączone, dopóki nie ustawisz `WLM_US_COURTLISTENER_KEY` na własny bezpłatny token API CourtListener. CourtListener prowadzi organizacja non-profit Free Law Project; nie jest to źródło urzędowe i każda odpowiedź to zaznacza.

Ustaw je jako zmienne środowiskowe serwera Fontes w ustawieniach MCP swojej aplikacji. Instalatory pytają o nie po instalacji, a ich program uruchamiający
**Add or change keys** pozwala je później zmienić.

Osobna sprawa: kilka źródeł stwierdza w swoich warunkach, że zautomatyzowany dostęp wymaga zgody
wydawcy. Są oznaczone jako OFF i pozostają wyłączone. Klucz tego nie zmienia; zmienia to tylko
zgoda wydawcy (wtedy ustaw `WLM_PERMITTED=<codes>`).

## Skąd biorą się dawne wersje i dodatkowe kraje?

Ze zbioru [Lexifina](https://github.com/lexifina/global-law), który prowadzi prawo około 200
krajów jako historię w git: każda zmiana to commit z datą dnia, od którego obowiązuje. Fontes
odczytuje go przez bezpłatny hostowany serwer Lexifiny. Dwa narzędzia z niego korzystają:
`get_law_on_date` (przepis w brzmieniu obowiązującym w dawnej dacie, wraz z prawem, które go
ostatnio zmieniło) oraz `get_law_history` (każde prawo, które zmieniło przepis, albo zmiana
słowo po słowie między dwiema datami). Fontes odczytuje w ten sposób także 91 innych krajów i
terytoriów, wyłącznie akty prawne (na przykład RPA, Kenia, Meksyk, Nowa Zelandia, Rosja, Korea
Południowa, Belgia, Litwa, Ukraina, Malezja, Tajlandia i Arabia Saudyjska). Są one oddzielone od
125 adapterów z bieżącym oficjalnym zakresem, a zakres dla poszczególnych krajów bardzo się różni
(krajowy zbiór Kenii obejmuje 9 ustaw). Ustawy Indii również pochodzą ze zbioru Lexifiny, ponieważ
warunki India Code zakazują zautomatyzowanego dostępu; wyroki Sądu Najwyższego są na żywo.

Lexifina nie jest oficjalnym wydawcą, a jej zbiór nie jest aktualny na żywo: Lexifina sprawdza każdy
kraj od czasu do czasu, a w jej własnym raporcie z 2026-11-26 338 z 383 krajowych zbiorów prawa
nie było sprawdzanych w ciągu ostatnich 7 dni. Każda odpowiedź podaje Lexifinę jako źródło,
linkuje stronę oficjalnego wydawcy i mówi, jak daleko sięga zbiór.

Lexifina uważa, że oficjalne teksty prawne nie podlegają ochronie praw autorskich, więc w niektórych
krajach kopiuje strony, których warunki lub robots.txt Fontes sam respektuje. Fontes nadal
respektuje je dla wszystkiego, co sam pobiera; to, co przychodzi przez Lexifinę, podlega ocenie
prawnej Lexifiny, zapisanej dla każdego kraju w jej repozytoriach. Kilka z nich ogranicza użycie
(wydawca Kenii: CC BY-NC). Wyrazy wyszukiwania, cytowania i daty trafiają w tych przypadkach do
serwera Lexifiny. Aby to wyłączyć, ustaw `WLM_LEXIFINA=0`. Bezpłatny serwer pozwala na 60 wywołań
na minutę i 10 000 dziennie na adres internetowy; bez klucza i konta. Fontes nie jest powiązany z
Lexifiną.

## Co opuszcza mój komputer?

Twoje wyszukiwania trafiają tylko do przeszukiwanego źródła (w przypadku narzędzi i krajów Lexifiny:
do serwera Lexifiny). Fontes nie prowadzi bazy danych i nie wymaga konta.

Poza źródłami Fontes raz dziennie pyta PyPI, czy istnieje nowsza wersja (wyłączysz to przez
`FONTES_NO_UPDATE_CHECK=1`). Liczniki użycia są wyłączone, dopóki ich nie włączysz, a
zgłoszenie błędu zostaje wysłane dopiero wtedy, gdy je zobaczysz i potwierdzisz. Twoja aplikacja
AI widzi Twoją rozmowę na swoich własnych warunkach.

Wszystkie szczegóły: [PRIVACY.md](PRIVACY.md).

## Czy to porada prawna?

Nie. Fontes jest narzędziem badawczym. Wyszukuje teksty; nie mówi, co oznaczają one w Twojej
sprawie, a korzystanie z niego nie tworzy z nikim relacji prawnik–klient. Aplikacja AI może źle
odczytać tekst, więc przeczytaj całe orzeczenie lub cały przepis, zanim na nim polegasz. Jeśli
potrzebujesz porady, zwróć się do prawnika uprawnionego do wykonywania zawodu tam, gdzie powstaje
Twoje pytanie.

## Kto go utrzymuje? Czy będzie nadal działał?

Jedna osoba: Yüce Karapazar. Za Fontes nie stoi żadna firma, nie ma umowy wsparcia ani
zobowiązania dotyczącego poziomu usług. Nie świadczy się żadnych usług prawnych.

Źródła są sprawdzane raz dziennie, a wyniki publikowane na
[stronie stanu](https://ykarapazar.github.io/fontes/status/?lang=pl). Strony sądów i instytucji
państwowych zmieniają się bez uprzedzenia, więc źródło może w każdej chwili przestać działać. Nie
ma gwarancji, że którekolwiek źródło lub sam Fontes będzie nadal działać. Fontes jest
udostępniany „w stanie, w jakim jest”, bez gwarancji (sekcje 7 i 8 [LICENSE](../../../LICENSE)).

## Tekst jest błędny, nieaktualny lub źródło nie działa. Jak to zgłosić?

- Otwórz zgłoszenie (issue) za pomocą formularza „Broken or wrong source”:
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Podaj jurysdykcję, o co pytałeś, co
  otrzymałeś oraz oficjalną stronę z prawidłowym tekstem.
- Albo poproś swoją aplikację AI, aby „zgłosiła błąd w Fontes” (lub uruchom
  `fontes report-bug`). Zobaczysz zgłoszenie, zanim cokolwiek zostanie wysłane.
- Albo napisz na fontesmcp@proton.me.

Nie umieszczaj w zgłoszeniu danych klientów ani informacji poufnych.

**Jeśli prowadzisz jedno ze źródeł** i coś jest nie tak (Twoje warunki, Twój robots.txt, Twoje
limity zapytań), napisz na fontesmcp@proton.me. Źródło zostanie poprawione albo wyłączone.

## Czym Fontes różni się od hostowanych narzędzi do badań prawniczych?

- **Działa na Twoim komputerze.** Nie ma serwera Fontes ani konta. Oznacza to też, że działa
  tylko w aplikacjach, które potrafią uruchomić lokalny serwer MCP (Claude Desktop, Codex,
  Cursor, VS Code i podobne), a nie w aplikacjach wyłącznie webowych, które przyjmują tylko
  hostowane konektory.
- **Nie ma bazy danych.** Każde wyszukiwanie trafia na żywo na własną stronę internetową lub API
  wydawcy, więc wyniki są tak aktualne jak źródło, a jakość wyszukiwania jest jakością samego
  źródła. Nie ma wyszukiwania semantycznego w kuratorowanym indeksie.
- **Nie nakłada limitu użycia.** Fontes nie ma miesięcznego limitu wywołań. Rozkłada w czasie
  swoje zapytania do każdej strony, a niektóre źródła ograniczają, jak szybko lub jak często można
  do nich kierować zapytania.
- **Ma otwarty kod źródłowy.** Możesz przeczytać każdy adapter i zobaczyć dokładnie, skąd
  pochodzi każdy tekst.
- **Nie stoi za nim żaden dostawca.** Brak umowy, działu wsparcia czy zobowiązania co do
  dostępności (zobacz „Kto go utrzymuje?”).

## Z jakimi aplikacjami i systemami działa?

Z każdą aplikacją MCP, która potrafi uruchomić lokalny serwer (stdio), na przykład Claude
Desktop, Claude Code, Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed,
LM Studio i Cline. Fontes działa w systemach macOS, Windows i Linux, wszędzie tam, gdzie działa
uv (Python 3.13+). Na komputerze Mac lub PC z Windows instalator jednym kliknięciem
konfiguruje naraz Claude Desktop, Codex, Claude Code, Cursor, VS Code, Windsurf, Gemini CLI, Zed,
LM Studio i Cline. Instrukcje dla każdej aplikacji:
[INSTALL.md](INSTALL.md).

## Czy mogę współtworzyć kod?

Obecnie nie. Zgłoszenia (issues), raporty o źródłach i prośby o jurysdykcje są mile widziane.
Zobacz [CONTRIBUTING.md](../../../CONTRIBUTING.md).
