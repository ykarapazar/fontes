> To jest tłumaczenie wspomagane maszynowo. Wiążąca jest wersja angielska.

# Informacja o prywatności Fontes

Fontes działa na Twoim komputerze. Twoje wyszukiwania i otwierane dokumenty pozostają między
Twoim komputerem, źródłami, które przeszukujesz (oficjalnymi, a także CourtListener i Lexifiną, jeśli
z nich korzystasz; zobacz niżej), i używaną przez Ciebie aplikacją AI (na warunkach tej aplikacji). Sam Fontes **domyślnie nie wysyła niczego** twórcom Fontes.

## Co może opuścić Twój komputer i kiedy

**1. Sprawdzanie aktualizacji (domyślnie włączone).** Raz dziennie Fontes pyta PyPI, publiczny
indeks pakietów Pythona, która wersja jest najnowsza. Zapytanie nie zawiera niczego o Tobie ani
o Twojej pracy; PyPI widzi Twój adres IP, jak przy każdym pobieraniu. Aby to wyłączyć, ustaw
`FONTES_NO_UPDATE_CHECK=1` (powiadomienie w aplikacji) i `FONTES_NO_AUTO_UPDATE=1`
(automatyczne aktualizacje instalatora).

**2. Liczniki użycia (wyłączone, dopóki ich nie włączysz).** Jeśli wyrazisz zgodę (opt-in), raz
dziennie Fontes wysyła:

- wersję Fontes i rodzinę Twojego systemu operacyjnego (macOS, Windows, Linux);
- dla każdego dnia, ile razy każde narzędzie zostało użyte dla każdego kodu jurysdykcji, na
  przykład „2026-11-10, nl, search_caselaw, 12”.

To cała wiadomość. Nigdy nie zawiera Twoich wyszukiwań, identyfikatorów dokumentów ani spraw,
treści dokumentów, Twojego imienia i nazwiska, konta ani żadnego identyfikatora Ciebie lub
Twojego komputera. Liczniki czekają na Twoim komputerze (w folderze pamięci podręcznej Fontes,
`stats.json`), dopóki nie zostaną wysłane; jeśli wysłanie się nie powiedzie, czekają do
następnego dnia.

- **Wyrażenie zgody**: odpowiedz „t”, gdy zapyta instalator, albo ustaw `FONTES_STATS=1` dla
  serwera Fontes.
- **Wycofanie zgody**: uruchom ponownie instalator i naciśnij Enter przy tym pytaniu albo usuń
  `FONTES_STATS`. Usunięcie `stats.json` odrzuca wszystko, co nie zostało jeszcze wysłane.

**3. Zgłoszenia błędów (tylko gdy je wyślesz).** Gdy o nie poprosisz (`fontes report-bug` albo
prośba do aplikacji AI o zgłoszenie błędu w Fontes), Fontes najpierw pokazuje Ci pełne
zgłoszenie i wysyła je tylko wtedy, gdy je potwierdzisz. Zawiera ono wersję Fontes, rodzinę
Twojego systemu operacyjnego, kod jurysdykcji, nazwę narzędzia i komunikat błędu ostatniego
nieudanego wywołania narzędzia (z usuniętymi wyszukiwanymi słowami i identyfikatorami) oraz
notatkę, jeśli ją napiszesz. Nie umieszczaj w notatce danych klientów. W tym celu Fontes
przechowuje ostatni błąd na Twoim komputerze (`last-error.json` w folderze pamięci podręcznej,
zastępowany za każdym razem); nigdy nie jest on wysyłany samodzielnie.

**4. Lexifina (domyślnie włączona).** `get_law_on_date`, `get_law_history`, 91 krajów i indyjskie akty prawne odczytywane
ze zbioru prawa Lexifiny trafiają do Lexifiny, obok oficjalnej strony albo zamiast niej. Wyrazy wyszukiwania, cytowania i daty
trafiają na bezpłatny serwer Lexifiny, `global-law.lexifina.com`, który prowadzi Lexifina, a nie
twórcy Fontes. Lexifina podaje, że jej serwer zapisuje, które narzędzie zostało wywołane i jak długo
trwało, nigdy natomiast, o co zapytano; Fontes nie może tego sprawdzić, a obowiązują warunki
samej Lexifiny. Lexifina widzi Twój adres IP, tak jak każdy serwer internetowy. Aby całkowicie
wyłączyć Lexifinę, ustaw `WLM_LEXIFINA=0`; wtedy te dwa narzędzia i kraje przestają działać, a nic
nie jest tam wysyłane.

## Dokąd trafiają dane i jak długo są przechowywane

Liczniki użycia i zgłoszenia błędów trafiają na mały serwer prowadzony przez twórcę Fontes
(`relay.kinetra.fit`). Nie przechowuje on adresów IP: są używane wyłącznie w pamięci, krótko,
aby powstrzymać zalewanie serwera zapytaniami, a serwer WWW nie prowadzi dla niego dziennika
dostępu. Liczniki są sumowane w dzienne wartości łączne; pojedyncze przesyłki nie są
przechowywane. Wartości łączne są przechowywane do 2 lat, zgłoszenia błędów do 1 roku, a
następnie usuwane. Nic nie jest sprzedawane ani udostępniane.

Jeśli ten serwer jest nieosiągalny, nic nie zostaje wysłane: liczniki pozostają na Twoim
komputerze, a zgłoszenia błędów kierują Cię zamiast tego do systemu zgłoszeń (issue tracker).

## Kto odpowiada i na jakiej podstawie

Administratorem danych w zakresie liczników użycia i zgłoszeń błędów jest Yüce Karapazar, twórca
Fontes. Kontakt: fontesmcp@proton.me.

Podstawą prawną jest Twoja zgoda (art. 6 ust. 1 lit. a UK GDPR i RODO UE). Liczniki użycia są
wysyłane tylko wtedy, gdy wyrazisz zgodę, a zgłoszenie błędu dopiero po jego potwierdzeniu.
Zgodę możesz w każdej chwili wycofać w sposób opisany powyżej; nie wpływa to na to, co zostało
wysłane wcześniej.

## Kontakt

Pytania lub wnioski: napisz na fontesmcp@proton.me albo otwórz zgłoszenie (issue) na
<https://github.com/ykarapazar/fontes/issues>.
