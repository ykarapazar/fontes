> Toto je strojovo podporovaný preklad. Rozhodujúce je anglické znenie.

# Fontes: otázky a odpovede

## Čo je Fontes?

Bezplatný MCP server s otvoreným zdrojovým kódom (Apache 2.0). Umožňuje každej aplikácii, ktorá
podporuje Model Context Protocol (Claude, Codex, Cursor, VS Code, Gemini CLI a ďalšie), vyhľadávať
súdne rozhodnutia a právne predpisy naživo na stránkach súdov a štátnych orgánov vo viac ako 120
jurisdikciách a medzinárodných súdoch (124 adaptérov). Každý výsledok uvádza svoj zdroj a
odkazuje na originál.

## Sú texty oficiálne?

Väčšinou áno, ale nie vždy.

- Väčšinu zdrojov prevádzkuje súd, ministerstvo alebo úradný vestník.
- Niektoré konsolidované texty zverejňuje štátny orgán, ale sú výslovne neoficiálne: autentický
  je iba úradný vestník.
- Niekoľko zdrojov vôbec nie sú štátne stránky (napríklad LexiVox, LawPhil, Maqam, Wikisource).

Fontes pridáva upozornenie „Unofficial source“ ku každej odpovedi, ktorá pochádza z niektorého z
nich. Skôr než čokoľvek budete citovať, overte si oficiálnu publikáciu. Tabuľka pokrytia v
[README](README.md#pokrytie) a `list_jurisdictions` uvádzajú zdroj pre každú jurisdikciu.

## Ktoré jurisdikcie pokrýva a ako dobre?

124 adaptérov: 108 členských štátov OSN, Hongkong, Kosovo, Palestína, Taiwan, súdy DIFC a 11
medzinárodných súdov a orgánov (napríklad Európsky súd pre ľudské práva, EÚ, Medzinárodný súdny
dvor a WTO).

Pokrytie sa výrazne líši. Podľa prísneho pravidla (precedensy najvyššieho všeobecného súdu alebo
ústava a primárne zákony, dosiahnuté úplne) sa za pokryté považuje 72 zo 124.
[COVERAGE.md](../../COVERAGE.md) pre každú jurisdikciu uvádza, čo Fontes dosahuje, čo nie a prečo.

## Potrebujem kľúč API?

Takmer pre každú jurisdikciu nie. Niektoré zdroje vyžadujú bezplatný kľúč: pozri [KEYS.md](KEYS.md).

- **Francúzsko:** áno. Francúzsko je vypnuté, kým nenastavíte `WLM_FR_PISTE_CLIENT_ID` a
  `WLM_FR_PISTE_CLIENT_SECRET`. Získate ich z bezplatného účtu PISTE (piste.gouv.fr) s
  aplikáciou prihlásenou k odberu Judilibre a Légifrance.
- **Spojené štáty:** voliteľné. Vyhľadávanie v judikatúre funguje bez kľúča, ale spoločný
  demonštračný kľúč umožňuje iba približne 10 vyhľadávaní denne na IP adresu. Bezplatný kľúč
  api.data.gov vo `WLM_US_GOVINFO_KEY` tento limit zvyšuje.

Nastavte ich ako premenné prostredia pre server Fontes v MCP nastaveniach svojej aplikácie. Inštalátory sa na ne po inštalácii pýtajú a spúšťač **Add or change keys** ich
neskôr zmení.

Samostatne: niekoľko zdrojov vo svojich podmienkach uvádza, že automatizovaný prístup vyžaduje
povolenie vydavateľa. Sú označené OFF a zostávajú vypnuté. Kľúč na tom nič nemení; zmení to iba
povolenie vydavateľa (potom nastavte `WLM_PERMITTED=<codes>`).

## Čo opúšťa môj počítač?

Vaše vyhľadávania smerujú iba do prehľadávaného zdroja. Fontes nevedie žiadnu databázu a
nepotrebuje žiadny účet.

Okrem zdrojov sa Fontes raz denne pýta PyPI, či existuje novšia verzia (vypnete pomocou
`FONTES_NO_UPDATE_CHECK=1`). Počty použití sú vypnuté, pokiaľ ich nezapnete, a hlásenie chyby sa
odošle až potom, čo ste ho videli a potvrdili. Vaša AI aplikácia vidí vašu konverzáciu podľa
svojich vlastných podmienok.

Všetky podrobnosti: [PRIVACY.md](PRIVACY.md).

## Je to právne poradenstvo?

Nie. Fontes je výskumný nástroj. Vyhľadáva texty; nehovorí vám, čo znamenajú pre váš prípad, a
jeho používaním nevzniká s nikým vzťah advokát – klient. AI aplikácia môže text prečítať
nesprávne, preto si rozhodnutie alebo ustanovenie prečítajte celé skôr, než sa naň budete
spoliehať. Ak potrebujete poradenstvo, obráťte sa na advokáta oprávneného pôsobiť tam, kde vaša
otázka vzniká.

## Kto ho spravuje? Bude naďalej fungovať?

Jedna osoba: Yüce Karapazar. Za Fontes nestojí žiadna spoločnosť, neexistuje zmluva o podpore
ani prísľub úrovne služieb. Neposkytujú sa žiadne právne služby.

Zdroje sa kontrolujú raz denne a výsledky sa zverejňujú na
[stránke stavu](https://ykarapazar.github.io/fontes/status/?lang=sk). Stránky súdov a štátnych
orgánov sa menia bez upozornenia, takže zdroj sa môže kedykoľvek pokaziť. Neexistuje žiadna
záruka, že niektorý zdroj alebo samotný Fontes bude naďalej fungovať. Fontes sa poskytuje „tak,
ako je“, bez záruky (oddiely 7 a 8 [LICENSE](../../../LICENSE)).

## Text je nesprávny, zastaraný alebo zdroj nefunguje. Ako to nahlásim?

- Otvorte issue pomocou formulára „Broken or wrong source“:
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Uveďte jurisdikciu, čo ste sa pýtali,
  čo ste dostali a oficiálnu stránku, ktorá ukazuje správny text.
- Alebo požiadajte svoju AI aplikáciu, aby „nahlásila chybu vo Fontes“ (alebo spustite
  `fontes report-bug`). Hlásenie uvidíte skôr, než sa čokoľvek odošle.
- Alebo napíšte na fontesmcp@proton.me.

Do hlásenia neuvádzajte údaje o klientoch ani dôverné skutočnosti.

**Ak prevádzkujete niektorý zo zdrojov** a niečo nie je v poriadku (vaše podmienky, váš
robots.txt, vaše limity počtu požiadaviek), napíšte na fontesmcp@proton.me. Zdroj sa opraví
alebo vypne.

## Čím sa Fontes líši od hostovaných nástrojov na právny výskum?

- **Beží vo vašom počítači.** Neexistuje žiadny server Fontes ani účet. To tiež znamená, že
  funguje iba v aplikáciách, ktoré dokážu spustiť lokálny MCP server (Claude Desktop, Codex,
  Cursor, VS Code a podobné), nie vo výlučne webových aplikáciách, ktoré prijímajú iba hostované
  konektory.
- **Nemá databázu.** Každé vyhľadávanie ide naživo na vlastnú webovú stránku alebo API
  vydavateľa, takže výsledky sú také aktuálne ako zdroj a kvalita vyhľadávania je kvalitou
  samotného zdroja. Neexistuje sémantické vyhľadávanie nad kurátorsky zostaveným indexom.
- **Nestanovuje žiadny limit používania.** Fontes nemá mesačný strop volaní. Rozkladá svoje
  požiadavky na každú webovú stránku v čase a niektoré zdroje obmedzujú, ako rýchlo alebo ako
  často sa na ne možno dopytovať.
- **Má otvorený zdrojový kód.** Môžete si prečítať každý adaptér a presne vidieť, odkiaľ každý
  text pochádza.
- **Nestojí za ním žiadny dodávateľ.** Žiadna zmluva, oddelenie podpory ani prísľub dostupnosti
  (pozri „Kto ho spravuje?“).

## S ktorými aplikáciami a systémami funguje?

S každou MCP aplikáciou, ktorá dokáže spustiť lokálny (stdio) server, napríklad Claude Desktop,
Claude Code, Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio a
Cline. Fontes beží na macOS, Windows a Linuxe, všade, kde beží uv (Python 3.13+). Na Macu alebo na Windows PC
inštalátor na jedno kliknutie naraz nastaví Claude Desktop, Codex, Claude Code, Cursor, VS Code,
Windsurf, Gemini CLI, Zed, LM Studio a Cline. Postup pre každú aplikáciu:
[INSTALL.md](INSTALL.md).

## Môžem prispieť kódom?

Momentálne nie. Issues, hlásenia o zdrojoch a žiadosti o jurisdikcie sú vítané. Pozri
[CONTRIBUTING.md](../../../CONTRIBUTING.md).
