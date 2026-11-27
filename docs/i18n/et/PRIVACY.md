> See on masinabil tehtud tõlge. Autoriteetne on ingliskeelne versioon.

# Fontese privaatsusteade

Fontes töötab teie arvutis. Teie otsingud ja avatavad dokumendid jäävad
teie arvuti, otsitavate allikate (ametlike, pluss CourtListener ja Lexifina, kui te neid kasutate, vt allpool)
ja teie kasutatava tehisintellekti rakenduse vahele (selle rakenduse enda tingimuste alusel). Fontes ise ei saada Fontese arendajatele **vaikimisi
midagi**.

## Mis võib teie arvutist lahkuda ja millal

**1. Uuenduste kontroll (vaikimisi sees).** Kord päevas küsib Fontes PyPI-lt, avalikult Pythoni pakettide
registrilt, milline versioon on uusim. Päring ei sisalda midagi teie ega teie töö kohta; PyPI
näeb teie IP-aadressi, nagu iga allalaadimise puhul. Selle väljalülitamiseks määrake `FONTES_NO_UPDATE_CHECK=1`
(rakendusesisene teade) ja `FONTES_NO_AUTO_UPDATE=1` (paigaldaja automaatsed uuendused).

**2. Kasutuskordade arvud (väljas, kui te neid sisse ei lülita).** Kui annate nõusoleku (opt-in), saadab Fontes kord päevas:

- Fontese versiooni ja teie operatsioonisüsteemi perekonna (macOS, Windows, Linux);
- päeva kaupa, mitu korda iga tööriista iga jurisdiktsioonikoodi jaoks kasutati, näiteks
  "2026-11-10, nl, search_caselaw, 12".

See on kogu sõnum. See ei sisalda kunagi teie otsinguid, dokumentide ega kohtuasjade tunnuseid, dokumentide
teksti, teie nime, kontot ega mingit teie või teie arvuti tunnust. Arvud ootavad teie arvutis
(Fontese vahemälukaustas, `stats.json`), kuni need saadetakse; kui saatmine ebaõnnestub, ootavad need
järgmise päevani.

- **Nõusoleku andmine**: vastake "y", kui paigaldaja küsib, või määrake Fontese serverile `FONTES_STATS=1`.
- **Loobumine**: käivitage paigaldaja uuesti ja vajutage selle küsimuse juures Enter või eemaldage
  `FONTES_STATS`. Faili `stats.json` kustutamine kõrvaldab kõik, mida pole veel saadetud.

**3. Veateated (ainult siis, kui te ühe saadate).** Kui te seda palute (`fontes report-bug` või palute
oma tehisintellekti rakendusel Fontese veast teatada), näitab Fontes teile kõigepealt kogu teadet ja saadab selle ainult siis, kui
kinnitate. See sisaldab Fontese versiooni, teie operatsioonisüsteemi perekonda, viimase ebaõnnestunud tööriistakutse
jurisdiktsioonikoodi, tööriista nime ja veateadet (teie otsingusõnad ja tunnused välja lõigatud) ning
märkust, kui selle kirjutate. Ärge lisage märkusesse kliendi andmeid. Selle toetamiseks hoiab Fontes
viimast viga teie arvutis (`last-error.json` selle vahemälukaustas, asendatakse iga kord);
seda ei saadeta kunagi eraldi.

**4. Lexifina (vaikimisi sees).** `get_law_on_date`, `get_law_history` 91 riiki ja India seadused loetakse Lexifina õigusregistrist, seega lähevad need Lexifinasse, kas ametliku saidi kõrval või selle asemel. Teie otsingusõnad, viited ja kuupäevad lähevad Lexifina tasuta serverisse `global-law.lexifina.com`, mida haldab Lexifina, mitte Fontese arendajad. Lexifina dokumenteerib, et tema server logib, millist tööriista kutsuti ja kui kaua see kestis, mitte kunagi, mida küsiti; Fontes ei saa seda kontrollida ning kehtivad Lexifina enda tingimused. Lexifina näeb teie IP-aadressi, nagu iga veebiserver. Selle täielikuks väljalülitamiseks seadke `WLM_LEXIFINA=0`; need kaks tööriista ja riigid lakkavad siis töötamast ja sinna ei saadeta midagi.

## Kuhu andmed lähevad ja kui kaua neid säilitatakse

Kasutuskordade arvud ja veateated lähevad väikesesse serverisse, mida haldab Fontese arendaja
(`relay.kinetra.fit`). See ei salvesta IP-aadresse: neid kasutatakse ainult mälus, lühiajaliselt, päringutulvade
peatamiseks, ja veebiserver ei pea selle kohta pöördumislogi. Arvud liidetakse päevasteks
kogusummadeks; üksikuid saadetisi ei säilitata. Kogusummasid säilitatakse kuni 2 aastat, veateateid kuni
1 aasta, seejärel need kustutatakse. Midagi ei müüda ega jagata.

Kui serverit ei õnnestu kätte saada, ei saadeta midagi: arvud jäävad teie arvutisse ja veateadete puhul
suunatakse teid hoopis probleemide jälgimissüsteemi (issue tracker).

## Kes vastutab ja mis alusel

Kasutuskordade arvude ja veateadete vastutav töötleja on Yüce Karapazar, Fontese
arendaja. Kontakt: fontesmcp@proton.me.

Õiguslik alus on teie nõusolek (Ühendkuningriigi UK GDPR-i ja ELi isikuandmete kaitse üldmääruse artikli 6 lõike 1 punkt a). Kasutuskordade arvud
saadetakse ainult siis, kui annate nõusoleku, ja veateade alles pärast seda, kui olete selle kinnitanud. Võite
nõusoleku igal ajal tagasi võtta, loobudes ülalkirjeldatud viisil; see ei mõjuta seda, mis saadeti
varem.

## Kontakt

Küsimused või taotlused: kirjutage aadressile fontesmcp@proton.me või avage issue aadressil
<https://github.com/ykarapazar/fontes/issues>.
