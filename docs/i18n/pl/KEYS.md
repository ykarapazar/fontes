> To jest tłumaczenie wspomagane maszynowo. Wiążąca jest wersja angielska.

# Klucze API

Niemal każde źródło w Fontes działa bez klucza. Trzy wymagają bezpłatnego klucza:

| Klucz | Udostępnia | Bez niego |
|---|---|---|
| `WLM_FR_PISTE_CLIENT_ID` + `WLM_FR_PISTE_CLIENT_SECRET` | Francja: Judilibre (orzeczenia sądów) i Légifrance (akty prawne) | Francja jest wyłączona. `list_jurisdictions` pokazuje ją jako nieaktywną. |
| `WLM_US_GOVINFO_KEY` | Stany Zjednoczone: wyszukiwanie govinfo (orzeczenia sądów federalnych, Statutes at Large, public laws) | Fontes używa wspólnego `DEMO_KEY`: około 10 wyszukiwań dziennie na adres IP. Otwarcie znanego orzeczenia i US Code nie wymagają klucza. |
| `WLM_US_COURTLISTENER_KEY` | Sądy stanowe USA (`us-states`): orzeczenia sądów najwyższych i apelacyjnych wszystkich 50 stanów oraz DC, z CourtListener | Orzecznictwo sądów stanowych USA jest wyłączone. `list_jurisdictions` pokazuje je jako nieaktywne. |

Klucze są opcjonalne. Możesz je dodać później.

## Dodawanie klucza

**Za pomocą instalatora.** Po skonfigurowaniu Fontes instalator proponuje dodanie kluczy. Na komputerze
Mac kliknij **Dodaj klucze** lub **Gotowe**, aby pominąć; w systemie Windows odpowiedz na pytanie
(naciśnij Enter, aby pominąć). Aby dodać lub zmienić klucze później, uruchom **Add or change keys**:

- Mac: ponownie otwórz aplikację Fontes Installer i wybierz **Dodaj lub zmień klucze**.
- Windows: otwórz menu Start, a następnie wybierz **Fontes** → **Dodaj lub zmień klucze**.

Wpisywane znaki są ukryte. Przy każdym kluczu: wklej go, naciśnij Enter, aby zachować
istniejący, lub wpisz `-`, aby go usunąć. Klucze trafiają do każdej aplikacji, która ma już
Fontes.

**Za pomocą rozszerzenia Claude Desktop (.mcpb).** Otwórz Claude > Settings > Extensions > Fontes
i wypełnij pola. Wszystkie są opcjonalne.

**Ręcznie.** Dodaj zmienne do bloku `env` wpisu `fontes` w konfiguracji MCP swojej aplikacji:

```json
"fontes": {
  "command": "...",
  "args": ["..."],
  "env": { "WLM_US_GOVINFO_KEY": "your-key" }
}
```

Po każdej zmianie uruchom aplikację ponownie.

## Francja: PISTE (bezpłatnie)

1. Załóż konto na [piste.gouv.fr](https://piste.gouv.fr). Oznacza to akceptację warunków PISTE (CGU).
2. Przejdź do API > **Consentement CGU API**. Zaakceptuj warunki dla **JUDILIBRE** i **Légifrance** (production).
3. Utwórz **aplikację produkcyjną** (production application). `APP_SANDBOX`, która została
   utworzona dla Ciebie, nie ma dostępu do produkcji. W „Modifier l'application” zaznacz
   **JUDILIBRE (production)** i **Légifrance (production)**, a następnie zastosuj zmiany.
4. Otwórz kartę **Authentification** aplikacji. Skopiuj `client_id` i `client_secret`.
5. Uruchom **Add or change keys** i wklej je.

Warunki w skrócie:

- Dane: Licence Ouverte / Etalab 2.0. Ponowne wykorzystanie, także komercyjne, jest dozwolone z podaniem źródła.
- Nie publikuj ani nie udostępniaj swoich danych uwierzytelniających. Jeśli wyciekną, zgłoś to PISTE.
- API Légifrance jest usługą w wersji beta. Może zostać zawieszone i ma limity (na sekundę, minutę i dzień).
- Teksty Légifrance nie są wersją autentyczną. Autentyczny jest tylko podpisany PDF Journal officiel.
- Judilibre: nie używaj nazwisk sędziów ani urzędników sądowych do oceniania, porównywania lub
  przewidywania ich pracy (Code de l'organisation judiciaire, art. L111-13; przestępstwo).
- Judilibre: przestrzegaj RODO. Nie próbuj ponownie identyfikować stron postępowania.

Swoje limity znajdziesz w PISTE w API Sélectionnées > Actions > Consulter les quotas.

## Stany Zjednoczone: api.data.gov (bezpłatnie)

1. Przejdź na [govinfo.gov/api-signup](https://www.govinfo.gov/api-signup) (klucz pojawi się na
   ekranie) lub [api.data.gov/signup](https://api.data.gov/signup/) (klucz przyjdzie e-mailem).
2. Podaj imię i nazwisko oraz adres e-mail. Pole „how will you use it” jest opcjonalne.
3. Skopiuj 40-znakowy klucz.
4. Uruchom **Add or change keys** i wklej go jako klucz dla USA.

Warunki w skrócie:

- Z własnym kluczem govinfo pozwala na maksymalnie 36 000 zapytań na godzinę.
- Nie znaleźliśmy warunków korzystania dotyczących konkretnie API (api.data.gov/terms/ nie
  istnieje). Niezweryfikowane. Zobacz [zasady govinfo](https://www.govinfo.gov/about/policies) i
  [politykę prywatności data.gov](https://data.gov/privacy-policy/).
- Zachowaj klucz dla siebie.

## Sądy stanowe USA: CourtListener (bezpłatnie)

CourtListener prowadzi [Free Law Project](https://free.law), organizacja non-profit, która od 2010 roku zbiera orzeczenia sądów USA i udostępnia je wszystkim za darmo. Według jej własnych danych zawiera ponad dziewięć milionów orzeczeń. Nie jest to źródło urzędowe: sądy publikują własne orzeczenia, a CourtListener zbiera je ze stron internetowych sądów i ze zeskanowanych zbiorów orzeczeń. Każda odpowiedź Fontes pochodząca z niego to zaznacza. Fontes nie jest powiązany z Free Law Project.

1. Załóż bezpłatne konto na [courtlistener.com](https://www.courtlistener.com/sign-in/).
2. Otwórz swój profil i skopiuj swój token API.
3. Uruchom **Add or change keys** i wklej go jako klucz CourtListener.

Warunki w skrócie ([pełne warunki](https://wiki.free.law/c/terms/courtlistener/courtlistenercom-terms-of-service-and-policies)):

- Token jest wyłącznie twój: nie udostępniaj go, nie łącz z cudzymi ani nie odsprzedawaj, i nie używaj kilku kont.
- Odpowiadasz za to, co aplikacja AI robi z twoim tokenem.
- Nie przedstawiaj analizy ich danych wykonanej przez AI jako przygotowanej, zatwierdzonej lub sprawdzonej przez Free Law Project.
- Bezpłatne konto pozwala na 5 zapytań na minutę, 50 na godzinę i 125 na dzień. Wyszukiwanie to jedno zapytanie; otwarcie orzeczenia to dwa. Członkostwo w Free Law Project podnosi limity.
- CourtListener nie gwarantuje dokładności. Sprawdź orzeczenie z egzemplarzem sądu, zanim na nim oprzesz.

## Gdzie są przechowywane klucze

- **Instalator lub ręcznie:** jako zwykły tekst w pliku konfiguracji MCP każdej aplikacji, w
  bloku `env` wpisu `fontes`. Każdy, kto może czytać Twoje pliki użytkownika, może przeczytać
  także klucze.
  - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac),
    `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
  - Claude Code: `~/.claude.json`
  - Codex: `~/.codex/config.toml`
  - Cursor: `~/.cursor/mcp.json`
  - VS Code (Copilot): `~/.copilot/mcp-config.json`
  - Windsurf: `~/.config/devin/mcp_config.json` lub `~/.codeium/windsurf/mcp_config.json`
    (Windows: `%APPDATA%\devin\mcp_config.json`)
  - Gemini CLI: `~/.gemini/settings.json`
  - Zed: `~/.config/zed/settings.json` (Windows: `%APPDATA%\Zed\settings.json`)
  - LM Studio: `~/.lmstudio/mcp.json`
  - Cline: `~/.cline/data/settings/cline_mcp_settings.json`
- **Rozszerzenie Claude Desktop (.mcpb):** Claude przechowuje te pola w swoich ustawieniach i
  chroni je bezpiecznym magazynem Twojego systemu (Keychain na komputerze Mac, Credential Manager
  w systemie Windows).

Przed każdą zmianą instalator zapisuje kopię pliku konfiguracji obok niego
(`<file>.fontes-backup-<time>`). Kopie utworzone po dodaniu kluczy także zawierają klucze. Usuń
stare kopie, których nie potrzebujesz.

## Zmiana lub usuwanie klucza

- Uruchom **Add or change keys**. Wklej nowy klucz, aby go zastąpić, lub wpisz `-`, aby go usunąć.
- Albo zmień blok `env` ręcznie i uruchom aplikację ponownie.
- Odinstalowanie Fontes usuwa cały jego wpis, łącznie z kluczami. Nie usuwa kopii zapasowych.
- Jeśli klucz wyciekł, zastąp go także u źródła: w PISTE wygeneruj nowe dane uwierzytelniające
  dla swojej aplikacji; w api.data.gov zarejestruj się po nowy klucz.

## Komunikaty, które możesz zobaczyć

| Komunikat | Znaczenie |
|---|---|
| `France needs a free PISTE key: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET.` | Brak klucza dla Francji. Dodaj go. |
| `Inactive: needs a free PISTE account. ...` (w `list_jurisdictions`) | To samo. |
| `PISTE refused the client credentials ...` | ID lub secret jest nieprawidłowy albo już nieważny. Skopiuj ponownie oba z karty Authentification. |
| `PISTE denied access to the ... API: subscribe the application to ... and accept its CGU on piste.gouv.fr.` | Twoja aplikacja nie subskrybuje tego API lub nie zaakceptowano jego warunków. Zobacz kroki 2 i 3. |
| `Using govinfo DEMO_KEY (about 10 searches/day per IP) ...` | Brak klucza dla USA. Wyszukiwanie działa dla kilku wywołań dziennie. |
| `govinfo rate limit reached (Retry-After ...). DEMO_KEY allows only about 10 searches a day per IP ...` | Klucz demonstracyjny został wyczerpany. Dodaj własny klucz. |
| `govinfo refused the API key (WLM_US_GOVINFO_KEY).` | Klucz jest nieprawidłowy lub nie został jeszcze potwierdzony z e-maila. |

Pusta wartość jest traktowana jak brak klucza.

## Zgody (WLM_PERMITTED)

To nie jest klucz API i instalator go nie ustawia. **Ustaw go tylko wtedy, gdy sam masz tę
zgodę.**

Niektóre źródła są domyślnie wyłączone, ponieważ ich warunki lub robots.txt zabraniają
zautomatyzowanego użycia bez zgody. Jeśli masz zgodę wydawcy, włącz źródło, dodając jego kod do
`WLM_PERMITTED`, rozdzielając kody przecinkami, w bloku `env`: `"WLM_PERMITTED": "in,de"`.

| Kod | Źródło |
|---|---|
| `az` | Azerbejdżan: e-qanun.az (Ministerstwo Sprawiedliwości) |
| `bh` | Bahrajn: Legislation and Legal Opinion Commission (lloc.gov.bh) |
| `co` | Kolumbia: Función Pública, Gestor Normativo (teksty jednolite aktów prawnych) |
| `de` | Niemcy: NeuRIS (federalny portal informacji prawnej, wersja próbna) |
| `difc` | Dubai International Financial Centre Courts (difccourts.ae) |
| `gr` | Grecja: Drukarnia Narodowa, wyszukiwarka Dziennika Rządowego (search.et.gr) |
| `mu` | Mauritius: Sąd Najwyższy (supremecourt.govmu.org) |
| `sg` | Singapur: wyroki sądów (elitigation.sg) |

Bez zgody Fontes informuje: `Off by default (<code>): the terms or robots.txt of ... forbid
automated use without the operator's permission.`
