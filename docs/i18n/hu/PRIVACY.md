> Ez gépi segítséggel készült fordítás. Az angol változat az irányadó.

# A Fontes adatvédelmi tájékoztatója

A Fontes az Ön számítógépén fut. A keresései és a megnyitott dokumentumok az Ön számítógépe, a
keresett hivatalos források és az Ön által használt MI-alkalmazás között maradnak (az adott
alkalmazás saját feltételei szerint). Maga a Fontes alapértelmezés szerint **semmit sem küld** a
Fontes fejlesztőinek.

## Mi hagyhatja el a számítógépét, és mikor

**1. Frissítés-ellenőrzés (alapértelmezés szerint bekapcsolva).** A Fontes naponta egyszer
megkérdezi a PyPI-t, a nyilvános Python-csomagtárat, hogy melyik a legújabb verzió. A kérés
semmit sem tartalmaz Önről vagy a munkájáról; a PyPI látja az IP-címét, mint bármely letöltésnél.
Kikapcsoláshoz állítsa be a `FONTES_NO_UPDATE_CHECK=1` (az alkalmazáson belüli értesítés) és a
`FONTES_NO_AUTO_UPDATE=1` (a telepítő automatikus frissítései) értéket.

**2. Használati számadatok (kikapcsolva, hacsak be nem kapcsolja).** Ha hozzájárul (opt-in), a
Fontes naponta egyszer elküldi:

- a Fontes verzióját és az operációs rendszer családját (macOS, Windows, Linux);
- naponként, hogy az egyes eszközöket hányszor használták az egyes joghatósági kódokhoz,
  például „2026-11-10, nl, search_caselaw, 12”.

Ez a teljes üzenet. Soha nem tartalmazza a kereséseit, dokumentum- vagy ügyazonosítókat,
dokumentumszöveget, az Ön nevét, fiókot, sem az Önt vagy a számítógépét azonosító bármilyen
azonosítót. A számadatok az Ön számítógépén várakoznak (a Fontes gyorsítótármappájában,
`stats.json`), amíg el nem küldik őket; ha a küldés nem sikerül, a következő napig várnak.

- **Hozzájárulás (opt-in)**: válaszoljon „y”-nal, amikor a telepítő megkérdezi, vagy állítsa be a
  `FONTES_STATS=1` értéket a Fontes-szerver számára.
- **Visszavonás (opt-out)**: futtassa újra a telepítőt, és ennél a kérdésnél nyomja meg az
  Entert, vagy távolítsa el a `FONTES_STATS` változót. A `stats.json` törlése elveti mindazt,
  amit még nem küldtek el.

**3. Hibajelentések (csak ha Ön küld egyet).** Ha kér egyet (`fontes report-bug`, vagy megkéri az
MI-alkalmazását, hogy jelentsen egy Fontes-hibát), a Fontes először megmutatja Önnek a teljes
jelentést, és csak akkor küldi el, ha megerősíti. Tartalmazza a Fontes verzióját, az operációs
rendszer családját, az utolsó sikertelen eszközhívás joghatósági kódját, az eszköz nevét és a
hibaüzenetet (a keresőszavai és az azonosítók eltávolításával), valamint egy megjegyzést, ha
ír ilyet. Ne írjon a megjegyzésbe ügyféladatokat. Ennek támogatására a Fontes az utolsó hibát a
számítógépén tárolja (`last-error.json` a gyorsítótármappájában, minden alkalommal felülírva);
ezt önmagában soha nem küldi el.

## Hová kerül, és meddig őrzik

A használati számadatok és a hibajelentések egy kis szerverre kerülnek, amelyet a Fontes
fejlesztője üzemeltet (`relay.kinetra.fit`). Ez nem tárol IP-címeket: ezeket csak a memóriában,
rövid ideig használja az elárasztás megakadályozására, és a webszerver nem vezet hozzáférési
naplót hozzá. A számadatok napi összesítésekbe kerülnek; az egyes beküldéseket nem őrzi meg. Az
összesítéseket legfeljebb 2 évig, a hibajelentéseket legfeljebb 1 évig őrzi, majd törli. Semmit
nem ad el, és nem oszt meg.

Ha ez a szerver nem érhető el, semmi sem kerül elküldésre: a számadatok a számítógépén maradnak,
a hibajelentések pedig ehelyett a hibakövetőhöz (issue tracker) irányítják.

## Ki a felelős, és milyen jogalapon

A használati számadatok és a hibajelentések adatkezelője Yüce Karapazar, a Fontes fejlesztője.
Kapcsolat: fontesmcp@proton.me.

A jogalap az Ön hozzájárulása (az Egyesült Királyság GDPR-ja és az uniós GDPR 6. cikk (1)
bekezdésének a) pontja). A használati számadatok csak akkor kerülnek elküldésre, ha hozzájárul,
a hibajelentés pedig csak azután, hogy megerősítette. Hozzájárulását bármikor visszavonhatja a
fent leírt módon; ez nem érinti a korábban elküldött adatokat.

## Kapcsolat

Kérdések vagy kérések: írjon a fontesmcp@proton.me címre, vagy nyisson egy issue-t itt:
<https://github.com/ykarapazar/fontes/issues>.
