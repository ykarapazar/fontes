> Tämä on konekäännöksen avulla tehty käännös. Englanninkielinen versio on määräävä.

# Fontes: kysymyksiä ja vastauksia

## Mikä Fontes on?

Maksuton avoimen lähdekoodin MCP-palvelin (Apache 2.0). Sen avulla mikä tahansa Model Context
Protocolia käyttävä sovellus (Claude, Codex, Cursor, VS Code, Gemini CLI ja muut) voi hakea tuomioistuinten ratkaisuja ja
lainsäädäntöä reaaliajassa tuomioistuinten ja viranomaisten verkkosivustoilta 125 lainkäyttöalueelta ja kansainvälisistä
tuomioistuimista sekä 91 muusta maasta Lexifinan tietueen kautta (katso alla). Jokainen tulos nimeää lähteensä ja linkittää alkuperäiseen.

## Ovatko tekstit virallisia?

Enimmäkseen, mutta eivät aina.

- Useimpia lähteitä ylläpitää tuomioistuin, ministeriö tai virallinen julkaisusarja.
- Jotkin ajantasaiset tekstit ovat viranomaisen julkaisemia mutta nimenomaisesti epävirallisia: vain
  virallinen säädöskokoelma on todistusvoimainen.
- Muutama lähde ei ole lainkaan viranomaisen sivusto (esimerkiksi LexiVox, LawPhil, Maqam,
  Wikisource).

Fontes lisää ilmoituksen ”Epävirallinen lähde” jokaiseen vastaukseen, joka tulee jostakin näistä. Ennen kuin
viittaat mihinkään, tarkista virallinen julkaisu. [README](README.md#kattavuus)-tiedoston kattavuustaulukko
ja `list_jurisdictions` nimeävät kunkin lainkäyttöalueen lähteen.

## Mitä lainkäyttöalueita se kattaa, ja kuinka hyvin?

125 sovitinta: 108 YK:n jäsenvaltiota, Hongkong, Kosovo, Palestiina, Taiwan, DIFC Courts, Yhdysvaltojen osavaltioiden tuomioistuimet ja 11 kansainvälistä tuomioistuinta ja toimielintä (kuten Euroopan ihmisoikeustuomioistuin, EU,
Kansainvälinen tuomioistuin (ICJ) ja WTO).

Kattavuus vaihtelee paljon. Tiukan säännön mukaan (ylimmän yleisen tuomioistuimen ennakkopäätökset tai
perustuslaki ja keskeiset lait, saatavilla kokonaan) 72 lainkäyttöaluetta 125:stä lasketaan katetuiksi.
[COVERAGE.md](../../COVERAGE.md) kertoo kunkin lainkäyttöalueen osalta, mitä Fontes tavoittaa, mitä ei,
ja miksi.

## Tarvitsenko API-avaimen?

Lähes kaikilla lainkäyttöalueilla et. Jotkin lähteet tarvitsevat maksuttoman avaimen: katso [KEYS.md](KEYS.md).

- **Ranska:** kyllä. Ranska on pois päältä, kunnes asetat `WLM_FR_PISTE_CLIENT_ID` ja
  `WLM_FR_PISTE_CLIENT_SECRET`. Ne saat maksuttomalta PISTE-tililtä (piste.gouv.fr), jolla on
  Judilibren ja Légifrancen tilannut sovellus.
- **Yhdysvallat:** valinnainen. Oikeuskäytännön haku toimii ilman avainta, mutta jaettu demoavain
  sallii vain noin 10 hakua päivässä IP-osoitetta kohden. Maksuton api.data.gov-avain muuttujassa
  `WLM_US_GOVINFO_KEY` nostaa rajaa.
- **Yhdysvaltojen osavaltioiden tuomioistuimet:** kyllä. Osavaltioiden oikeuskäytäntö (`us-states`) on pois päältä, kunnes asetat `WLM_US_COURTLISTENER_KEY`:n omaksi ilmaiseksi CourtListenerin API-tunnukseksesi. CourtListenerin ylläpitäjä on voittoa tavoittelematon Free Law Project; se ei ole virallinen lähde, ja jokainen vastaus kertoo tämän.

Aseta nämä Fontes-palvelimen ympäristömuuttujiksi sovelluksesi MCP-asetuksissa. Asennusohjelmat
kysyvät niitä asennuksen jälkeen, ja niiden **Add or change keys** -käynnistin muuttaa niitä
myöhemmin.

Lisäksi muutama lähde ilmoittaa käyttöehdoissaan, että automaattinen käyttö edellyttää julkaisijan
lupaa. Ne on merkitty OFF ja pysyvät pois päältä. Avain ei muuta tätä; vain
julkaisijan lupa muuttaa (aseta silloin `WLM_PERMITTED=<codes>`).

## Mistä lakien aiemmat versiot ja lisämaat tulevat?

Ne tulevat [Lexifinasta](https://github.com/lexifina/global-law), joka ylläpitää noin 200 maan lakia git-historiana: jokainen muutos on commit,
joka on päivätty sinä päivänä, jona muutos astui voimaan. Fontes lukee sitä Lexifinan maksuttoman isännöidyn palvelimen kautta.
Kaksi työkalua käyttää sitä: `get_law_on_date` (säännös voimassa olevana päivänä, myös menneenä, ja laki, joka sitä viimeksi muutti)
ja `get_law_history` (jokainen laki, joka muutti säännöstä, tai sanatason muutos kahden päivämäärän välillä). Fontes lukee tätä
kautta myös 91 muuta maata ja aluetta, pelkkää lainsäädäntöä (esimerkiksi Etelä-Afrikka, Kenia, Meksiko, Uusi-Seelanti, Venäjä,
Etelä-Korea, Belgia, Liettua, Ukraina, Malesia, Thaimaa ja Saudi-Arabia). Ne ovat erillään 125 sovittimesta, joilla on elävä
virallinen kattavuus, ja kattavuus vaihtelee maittain paljon (Kenian kansallisessa tietueessa on 9 lakia). Intian lait tulevat
myös Lexifinan tietueesta, koska India Coden käyttöehdot kieltävät automaattisen käytön; sen korkeimman oikeuden tuomiot ovat elävinä.

Lexifina ei ole virallinen julkaisija, eikä sen tietue ole elävä: Lexifina tarkistaa maat aika ajoin, ja sen oma raportti
(2026-11-26) laski 383 kansallisesta lakikokonaisuudesta 338 sellaiseksi, joita ei ollut tarkistettu viimeisen seitsemän päivän
aikana. Jokainen vastaus nimeää Lexifinan lähteeksi, linkittää virallisen julkaisijan sivun ja kertoo, kuinka pitkälle tietue ulottuu.

Lexifina katsoo, että viralliset oikeudelliset tekstit eivät ole tekijänoikeuden suojaamia, joten joissakin maissa se kopioi
sivustoja, joiden käyttöehtoja tai robots.txt-tiedostoa Fontes itse kunnioittaa. Fontes kunnioittaa niitä edelleen kaikessa,
minkä se itse hakee; Lexifinan kautta tuleva noudattaa Lexifinan omaa harkintaa, joka on kirjattu maittain sen repositorioihin.
Muutamat rajoittavat käyttöä (Kenian julkaisijan aineisto: CC BY-NC). Hakusanasi, viittauksesi ja päivämäärät menevät näihin
kohdistuviin hakuihin Lexifinan palvelimelle. Voit kytkeä sen pois asettamalla `WLM_LEXIFINA=0`. Avainta tai tiliä ei tarvita;
maksuton palvelin sallii 60 kutsua minuutissa ja 10 000 päivässä internet-osoitetta kohden. Fontes ei ole yhteydessä Lexifinaan.

## Mitä tietokoneeltani lähtee?

Hakusi menevät vain haettavaan lähteeseen (Lexifinan työkalujen ja maiden osalta se on Lexifinan palvelin). Fontes ei ylläpidä
tietokantaa eikä tarvitse käyttäjätiliä.

Lähteiden lisäksi Fontes kysyy PyPI:ltä kerran päivässä, onko uudempaa versiota (pois päältä
asetuksella `FONTES_NO_UPDATE_CHECK=1`). Käyttömäärät ovat pois päältä, ellet ota niitä käyttöön, ja virheraportti
lähetetään vasta, kun olet nähnyt sen ja vahvistanut. Tekoälysovelluksesi näkee keskustelusi omien
ehtojensa mukaisesti.

Kaikki yksityiskohdat: [PRIVACY.md](PRIVACY.md).

## Onko tämä oikeudellista neuvontaa?

Ei. Fontes on tiedonhakutyökalu. Se löytää tekstejä; se ei kerro, mitä ne merkitsevät sinun
asiassasi, eikä sen käyttäminen luo asianajaja–asiakassuhdetta kenenkään kanssa. Tekoälysovellus voi
lukea tekstin väärin, joten lue koko ratkaisu tai säännös ennen kuin luotat siihen. Neuvoa varten kysy
lakimieheltä, jolla on pätevyys siellä, missä kysymyksesi syntyy.

## Kuka sitä ylläpitää? Toimiiko se jatkossakin?

Yksi henkilö: Yüce Karapazar. Fontesin takana ei ole yritystä, tukisopimusta eikä
palvelutasolupausta. Oikeudellisia palveluja ei tarjota.

Lähteet tarkistetaan kerran päivässä, ja tulokset julkaistaan
[tilasivulla](https://ykarapazar.github.io/fontes/status/?lang=fi). Tuomioistuinten ja viranomaisten verkkosivustot
muuttuvat ilman ennakkoilmoitusta, joten lähde voi lakata toimimasta milloin tahansa. Ei ole takuuta siitä, että mikään lähde
tai Fontes itse toimii jatkossakin. Fontes tarjotaan ”sellaisenaan”, ilman takuuta ([LICENSE](../../../LICENSE)-tiedoston kohdat 7
ja 8).

## Teksti on väärä tai vanhentunut, tai lähde ei toimi. Miten ilmoitan siitä?

- Avaa issue lomakkeella ”Broken or wrong source”:
  <https://github.com/ykarapazar/fontes/issues/new/choose>. Kerro, mikä lainkäyttöalue, mitä
  kysyit, mitä sait ja mikä virallinen sivu näyttää oikean tekstin.
- Tai pyydä tekoälysovellustasi ”raportoimaan Fontesin virhe” (tai aja `fontes report-bug`). Näet raportin ennen kuin
  mitään lähetetään.
- Tai lähetä sähköpostia osoitteeseen fontesmcp@proton.me.

Älä sisällytä raporttiin asiakastietoja tai luottamuksellisia tietoja.

**Jos ylläpidät jotakin lähteistä** ja jokin on pielessä (käyttöehtosi, robots.txt-tiedostosi, pyyntörajoituksesi),
lähetä sähköpostia osoitteeseen fontesmcp@proton.me. Lähde korjataan tai poistetaan käytöstä.

## Miten Fontes eroaa verkossa toimivista oikeudellisen tiedonhaun palveluista?

- **Se toimii tietokoneellasi.** Fontes-palvelinta tai käyttäjätiliä ei ole. Se tarkoittaa myös, että se
  toimii vain sovelluksissa, jotka voivat käynnistää paikallisen MCP-palvelimen (Claude Desktop, Codex, Cursor, VS Code
  ja vastaavat), ei pelkissä verkkosovelluksissa, jotka hyväksyvät vain palvelinpohjaisia liittimiä (hosted connectors).
- **Sillä ei ole tietokantaa.** Jokainen haku tehdään reaaliajassa julkaisijan omalle verkkosivustolle tai rajapintaan (API), joten
  tulokset ovat yhtä ajantasaisia kuin lähde, ja hakujen laatu on lähteen omaa. Valikoidussa hakemistossa ei ole
  semanttista hakua.
- **Se ei aseta käyttörajaa.** Fontesilla ei ole kuukausittaista kutsukattoa. Se harventaa pyyntöjään kullekin
  verkkosivustolle, ja jotkin lähteet rajoittavat, kuinka nopeasti tai kuinka usein niistä voi hakea.
- **Se on avointa lähdekoodia.** Voit lukea jokaisen sovittimen ja nähdä tarkalleen, mistä kukin teksti tulee.
- **Sen takana ei ole toimittajaa.** Ei sopimusta, tukipalvelua eikä käytettävyyslupausta (katso ”Kuka
  sitä ylläpitää?”).

## Minkä sovellusten ja järjestelmien kanssa se toimii?

Minkä tahansa MCP-sovelluksen kanssa, joka voi ajaa paikallista (stdio) palvelinta, esimerkiksi Claude Desktop, Claude Code,
Codex, Cursor, VS Code (GitHub Copilot), Gemini CLI, Windsurf, Zed, LM Studio ja Cline. Fontes
toimii macOS:ssä, Windowsissa ja Linuxissa, kaikkialla missä uv toimii (Python 3.13+). Macilla tai Windows-tietokoneella yhden napsautuksen asennusohjelma ottaa käyttöön Claude Desktopin, Codexin, Claude Coden, Cursorin, VS Coden, Windsurfin, Gemini CLI:n, Zedin, LM Studion ja Clinen kerralla. Vaiheet kullekin sovellukselle: [INSTALL.md](INSTALL.md).

## Voinko osallistua koodiin?

Ei tällä hetkellä. Issuet, lähdeilmoitukset ja lainkäyttöaluetoiveet ovat tervetulleita. Katso
[CONTRIBUTING.md](../../../CONTRIBUTING.md).
