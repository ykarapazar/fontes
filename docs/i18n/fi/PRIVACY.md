> Tämä on konekäännöksen avulla tehty käännös. Englanninkielinen versio on määräävä.

# Fontesin tietosuojaseloste

Fontes toimii tietokoneellasi. Hakusi ja avaamasi asiakirjat pysyvät
tietokoneesi, hakemiesi virallisten lähteiden ja käyttämäsi tekoälysovelluksen välillä (kyseisen
sovelluksen omien ehtojen mukaisesti). Fontes itse ei lähetä Fontesin kehittäjille **oletuksena
mitään**.

## Mitä tietokoneeltasi voi lähteä, ja milloin

**1. Päivitystarkistus (oletuksena päällä).** Kerran päivässä Fontes kysyy PyPI:ltä, julkiselta Python-pakettien
hakemistolta, mikä versio on uusin. Pyyntö ei sisällä mitään sinusta tai työstäsi; PyPI
näkee IP-osoitteesi, kuten minkä tahansa latauksen yhteydessä. Ota se pois päältä asettamalla `FONTES_NO_UPDATE_CHECK=1`
(sovelluksen sisäinen ilmoitus) ja `FONTES_NO_AUTO_UPDATE=1` (asennusohjelman automaattiset päivitykset).

**2. Käyttömäärät (pois päältä, ellet ota niitä käyttöön).** Jos annat suostumuksesi (opt-in), Fontes lähettää kerran päivässä:

- Fontesin version ja käyttöjärjestelmäperheesi (macOS, Windows, Linux);
- päivittäin, kuinka monta kertaa kutakin työkalua käytettiin kullekin lainkäyttöaluekoodille, esimerkiksi
  "2026-11-10, nl, search_caselaw, 12".

Siinä on koko viesti. Se ei koskaan sisällä hakujasi, asiakirjojen tai asioiden tunnisteita, asiakirjojen
tekstiä, nimeäsi, käyttäjätiliä eikä mitään sinun tai tietokoneesi tunnistetta. Määrät odottavat tietokoneellasi
(Fontesin välimuistikansiossa, `stats.json`), kunnes ne lähetetään; jos lähetys epäonnistuu, ne odottavat
seuraavaan päivään.

- **Ota käyttöön**: vastaa "y", kun asennusohjelma kysyy, tai aseta `FONTES_STATS=1` Fontes-palvelimelle.
- **Poista käytöstä**: aja asennusohjelma uudelleen ja paina Enter kyseisen kysymyksen kohdalla, tai poista
  `FONTES_STATS`. Tiedoston `stats.json` poistaminen hävittää kaiken, mitä ei ole vielä lähetetty.

**3. Virheraportit (vain kun lähetät sellaisen).** Kun pyydät raporttia (`fontes report-bug`, tai pyydät
tekoälysovellustasi raportoimaan Fontesin virheen), Fontes näyttää sinulle ensin koko raportin ja lähettää sen vain, jos
vahvistat. Se sisältää Fontesin version, käyttöjärjestelmäperheesi, viimeisimmän epäonnistuneen työkalukutsun
lainkäyttöaluekoodin, työkalun nimen ja virheilmoituksen (hakusanasi ja tunnisteet poistettuina) sekä
huomautuksen, jos kirjoitat sellaisen. Älä kirjoita huomautukseen asiakastietoja. Tätä varten Fontes säilyttää
viimeisimmän virheen tietokoneellasi (`last-error.json` sen välimuistikansiossa, korvataan joka kerta);
sitä ei koskaan lähetetä erikseen.

## Minne tiedot menevät ja kuinka kauan niitä säilytetään

Käyttömäärät ja virheraportit menevät Fontesin kehittäjän ylläpitämälle pienelle
palvelimelle (`relay.kinetra.fit`). Se ei tallenna IP-osoitteita: niitä käytetään vain muistissa, hetken, pyyntötulvien
estämiseen, eikä verkkopalvelin pidä siitä käyttölokia. Määrät lasketaan yhteen päivittäisiksi
kokonaismääriksi; yksittäisiä lähetyksiä ei säilytetä. Kokonaismäärät säilytetään enintään 2 vuotta, virheraportit enintään
1 vuoden, minkä jälkeen ne poistetaan. Mitään ei myydä eikä jaeta.

Jos palvelimeen ei saada yhteyttä, mitään ei lähetetä: määrät jäävät tietokoneellesi, ja virheraporttien kohdalla
sinut ohjataan sen sijaan issue-seurantaan.

## Kuka on vastuussa, ja millä perusteella

Käyttömäärien ja virheraporttien rekisterinpitäjä on Yüce Karapazar, Fontesin
kehittäjä. Yhteystiedot: fontesmcp@proton.me.

Käsittelyn oikeusperuste on suostumuksesi (Yhdistyneen kuningaskunnan UK GDPR:n ja EU:n yleisen tietosuoja-asetuksen 6 artiklan 1 kohdan a alakohta). Käyttömäärät
lähetetään vain, jos annat suostumuksesi, ja virheraportti vasta, kun olet vahvistanut sen. Voit peruuttaa
suostumuksesi milloin tahansa poistamalla käytön edellä kuvatulla tavalla; tämä ei vaikuta siihen, mitä on lähetetty
aiemmin.

## Yhteystiedot

Kysymykset tai pyynnöt: lähetä sähköpostia osoitteeseen fontesmcp@proton.me tai avaa issue osoitteessa
<https://github.com/ykarapazar/fontes/issues>.
