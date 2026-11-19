> Ez gépi segítséggel készült fordítás. Az angol változat az irányadó.

# Fontes: kérdések és válaszok

## Mi a Fontes?

Ingyenes, nyílt forráskódú MCP-szerver (Apache 2.0). Lehetővé teszi, hogy bármely alkalmazás,
amely ismeri a Model Context Protocolt (Claude, Codex, Cursor, VS Code, Gemini CLI és mások),
közvetlenül bírósági és állami webhelyeken keressen bírósági határozatokat és jogszabályokat,
120+ joghatóságban és nemzetközi bíróságon (124 adapter). Minden találat megnevezi a forrását,
és az eredetire hivatkozik.

## Hivatalosak a szövegek?

Többnyire igen, de nem mindig.

- A legtöbb forrást bíróság, minisztérium vagy hivatalos lap üzemelteti.
- Egyes egységes szerkezetbe foglalt szövegeket állami szerv tesz közzé, de kifejezetten nem
  hivatalosak: csak a hivatalos lap hiteles.
- Néhány forrás egyáltalán nem állami webhely (például LexiVox, LawPhil, Maqam, Wikisource).

A Fontes „Unofficial source” megjegyzést fűz minden olyan válaszhoz, amely ezek valamelyikéből
származik. Mielőtt bármire hivatkozna, ellenőrizze a hivatalos kiadványt. A
[README](README.md#lefedettség) lefedettségi táblázata és a `list_jurisdictions` megnevezi az
egyes joghatóságok forrását.

## Mely joghatóságokat fedi le, és milyen mértékben?

124 adapter: 108 ENSZ-tagállam, Hongkong, Koszovó, Palesztina, Tajvan, a DIFC Courts, valamint
11 nemzetközi bíróság és szerv (például az Emberi Jogok Európai Bírósága, az EU, a Nemzetközi
Bíróság és a WTO).

A lefedettség nagyon eltérő. Szigorú szabály szerint (a legfelső általános bíróság precedensei,
illetve az alkotmány és az elsődleges törvények, teljes körűen elérve) a 124-ből 72 számít
lefedettnek. A [COVERAGE.md](../../COVERAGE.md) joghatóságonként felsorolja, mit ér el a Fontes,
mit nem, és miért.

## Szükségem van API-kulcsra?

Szinte minden joghatóság esetében nem. Egyes forrásokhoz ingyenes kulcs kell: lásd
[KEYS.md](KEYS.md).

- **Franciaország:** igen. Franciaország ki van kapcsolva, amíg be nem állítja a
  `WLM_FR_PISTE_CLIENT_ID` és a `WLM_FR_PISTE_CLIENT_SECRET` értéket. Ezeket egy ingyenes PISTE-
  fiókból (piste.gouv.fr) kapja, egy olyan alkalmazással, amely előfizetett a Judilibre és a
  Légifrance szolgáltatásra.
- **Egyesült Államok:** opcionális. Az ítélkezési gyakorlat keresése kulcs nélkül is működik, de a
  közös demókulcs IP-címenként csak naponta körülbelül 10 keresést enged. Egy ingyenes
  api.data.gov kulcs a `WLM_US_GOVINFO_KEY` változóban megemeli ezt a korlátot.

Ezeket környezeti változóként állítsa be a Fontes-szerver számára az alkalmazása
MCP-beállításaiban. Amint a telepítő megjelenik, a telepítés után rákérdez ezekre, később pedig
az **Add or change keys** indítójával módosíthatók.

Ettől függetlenül néhány forrás feltételei szerint az automatizált hozzáféréshez a kiadó
engedélye szükséges. Ezek OFF jelölést kapnak, és kikapcsolva maradnak. Egy kulcs ezen nem
változtat; csak a kiadó engedélye (ekkor állítsa be a `WLM_PERMITTED=<codes>` értéket).

## Mi hagyja el a számítógépemet?

A keresései csak a keresett forráshoz jutnak el. A Fontes nem tart fenn adatbázist, és nem kell
hozzá fiók.

A forrásokon kívül a Fontes naponta egyszer megkérdezi a PyPI-t, van-e újabb verzió
(kikapcsolható: `FONTES_NO_UPDATE_CHECK=1`). A használati számadatok ki vannak kapcsolva, hacsak
be nem kapcsolja őket, a hibajelentés pedig csak azután kerül elküldésre, hogy látta és
megerősítette. Az MI-alkalmazása a saját feltételei szerint látja a beszélgetését.

Minden részlet: [PRIVACY.md](PRIVACY.md).

## Ez jogi tanács?

Nem. A Fontes kutatási eszköz. Megtalálja a szövegeket; nem mondja meg, mit jelentenek az Ön
ügyére nézve, és használata senkivel sem hoz létre ügyvéd–ügyfél viszonyt. Az MI-alkalmazás
félreolvashat egy szöveget, ezért olvassa el a teljes határozatot vagy rendelkezést, mielőtt
hagyatkozna rá. Tanácsért forduljon olyan ügyvédhez, aki annak a helynek a jogában jártas, ahol
a kérdése felmerül.

## Ki tartja karban? Működni fog továbbra is?

Egyetlen személy: Yüce Karapazar. A Fontes mögött nincs cég, nincs támogatási szerződés, és
nincs szolgáltatási szintre vonatkozó ígéret. Jogi szolgáltatást nem kínál.

A forrásokat naponta egyszer ellenőrzik, az eredmények pedig az
[állapotoldalon](https://ykarapazar.github.io/fontes/status/?lang=hu) jelennek meg. A bírósági
és állami webhelyek előzetes értesítés nélkül változnak, így egy forrás bármikor
elromolhat. Nincs garancia arra, hogy bármely forrás vagy maga a Fontes továbbra is működni fog.
A Fontes „ahogy van” („as is”) alapon, szavatosság nélkül áll rendelkezésre (a
[LICENSE](../../../LICENSE) 7. és 8. szakasza).

## Egy szöveg hibás, elavult, vagy egy forrás nem működik. Hogyan jelenthetem?

- Nyisson egy issue-t a „Broken or wrong source” űrlappal:
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Adja meg, melyik joghatóságról van
  szó, mit kérdezett, mit kapott, és azt a hivatalos oldalt, amely a helyes szöveget mutatja.
- Vagy kérje meg az MI-alkalmazását, hogy „jelentsen egy Fontes-hibát” (vagy futtassa a
  `fontes report-bug` parancsot). A jelentést azelőtt látja, hogy bármi elküldésre kerülne.
- Vagy írjon a fontesmcp@proton.me címre.

Ne tegyen a jelentésbe ügyféladatokat vagy bizalmas tényeket.

**Ha Ön üzemelteti valamelyik forrást**, és valami nem stimmel (a feltételei, a robots.txt-je, a
lekérési korlátai), írjon a fontesmcp@proton.me címre. A forrást kijavítják vagy kikapcsolják.

## Miben különbözik a Fontes a hosztolt jogi kutatóeszközöktől?

- **Az Ön számítógépén fut.** Nincs Fontes-szerver, és nincs fiók. Ez azt is jelenti, hogy csak
  olyan alkalmazásokban működik, amelyek helyi MCP-szervert tudnak indítani (Claude Desktop,
  Codex, Cursor, VS Code és hasonlók), a csak hosztolt csatlakozókat elfogadó, kizárólag
  webes alkalmazásokban nem.
- **Nincs adatbázisa.** Minden keresés élőben jut el a kiadó saját webhelyére vagy API-jához, így
  a találatok annyira naprakészek, mint a forrás, és a keresés minősége a forrásé. Nincs
  szemantikus keresés egy összeválogatott index felett.
- **Nem szab használati korlátot.** A Fontesnek nincs havi híváskorlátja. Az egyes webhelyekhez
  intézett kéréseit időben elosztja, és egyes források korlátozzák, milyen gyorsan vagy milyen
  gyakran lehet lekérdezni őket.
- **Nyílt forráskódú.** Minden adaptert elolvashat, és pontosan láthatja, honnan származnak az
  egyes szövegek.
- **Nincs mögötte szolgáltató.** Nincs szerződés, ügyfélszolgálat vagy rendelkezésre állási
  ígéret (lásd „Ki tartja karban?”).

## Mely alkalmazásokkal és rendszerekkel működik?

Bármely MCP-alkalmazással, amely helyi (stdio) szervert tud futtatni, például a Claude
Desktoppal, a Claude Code-dal, a Codexszel, a Cursorral, a VS Code-dal (GitHub Copilot), a
Gemini CLI-vel, a Windsurffel, a Zeddel, az LM Studióval és a Cline-nal. A Fontes macOS-en,
Windowson és Linuxon fut, mindenhol, ahol az uv fut (Python 3.13+). Macen vagy Windows PC-n egy egykattintásos telepítő
egy lépésben beállítja a Claude Desktopot, a Codexet, a Claude Code-ot, a Cursort, a VS Code-ot, a
Windsurfot, a Gemini CLI-t, a Zedet, az LM Studiót és a Cline-t.
Lépések az egyes alkalmazásokhoz: [INSTALL.md](INSTALL.md).

## Hozzájárulhatok kóddal?

Jelenleg nem. Az issue-kat, a forrásokkal kapcsolatos jelzéseket és a joghatóságokra vonatkozó
kéréseket szívesen fogadjuk. Lásd [CONTRIBUTING.md](../../../CONTRIBUTING.md).
